import sys
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QFont
from PyQt5.QtCore import QRect, pyqtSignal, QThread, pyqtSlot
import random
import csv
import time
import math
from Configuration import load_config
from sa_utils import initialize_schedule, objective_function, neighbor_solution, acceptance_probability, simulated_annealing

# Constants
DAY_HOURS = 4
DAYS_NUM = 5

# Load configuration
config = load_config('../configuration files/data.cfg')

# Extract parameters from config
professors = {k.split('_')[1]: v for k, v in config.items('Professors')}
courses = {k.split('_')[1]: v for k, v in config.items('Courses')}
rooms = {k: room_details.split(',')[0].strip().lower() for k, room_details in config.items('Rooms')}
classroom_availability = []
for room, details in config.items('Rooms'):
    lab, capacity = details.split(',')
    classroom_availability.append({
        'room': room,
        'day': random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        'time': [i for i in range(1, 51)]
    })

class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

    def is_solution(self, assignment):
        for variable, value in assignment.items():
            if not self.constraints.get(variable, lambda x, y: True)(value, assignment):
                return False
        return True

    def most_constrained_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def least_constraining_value(self, variable, assignment):
        return sorted(self.domains[variable], key=lambda val: self.count_conflicts(variable, val, assignment))

    def count_conflicts(self, variable, value, assignment):
        temp_assignment = assignment.copy()
        temp_assignment[variable] = value
        return sum(1 for var in self.variables if var in temp_assignment and not self.constraints[var](temp_assignment[var], temp_assignment))

    def iterative_backtracking_search(self):
        stack = [{}]
        while stack:
            assignment = stack.pop()
            if len(assignment) == len(self.variables):
                return assignment

            var = self.most_constrained_variable(assignment)
            for value in self.least_constraining_value(var, assignment):
                new_assignment = assignment.copy()
                new_assignment[var] = value
                if self.is_solution(new_assignment):
                    stack.append(new_assignment)
        return None

def no_teacher_overlap(assignment_value, assignment):
    teacher, subject, room, day, time = assignment_value
    for key, value in assignment.items():
        t, s, r, d, ti = value
        if teacher == t and day == d and time == ti:
            return False
    return True

def no_room_overlap(assignment_value, assignment):
    teacher, subject, room, day, time = assignment_value
    for key, value in assignment.items():
        t, s, r, d, ti = value
        if room == r and day == d and time == ti:
            return False
    return True

def translate_schedule(best_schedule):
    translated = []
    for (teacher_id, course_id), (room_id, day, time_slot) in best_schedule.items():
        translated.append({
            'Professor': professors[teacher_id],
            'Course': courses[course_id],
            'Room': room_id,
            'Day': day,
            'Time Slot': time_slot
        })
    return translated

def save_schedule_to_csv(schedule, file_path):
    keys = schedule[0].keys()
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(schedule)

class SolverThread(QThread):
    def __init__(self, example):
        super().__init__()
        self.example = example

    def run(self):
        self.example.solve()

class Example(QMainWindow):
    trigger = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.best = False
        self.bestChromosome = None
        self.instance = None
        self.initUI()

    def initUI(self):
        startAction = QAction(QIcon('start.png'), 'Start Solving', self)
        startAction.setShortcut('Ctrl+S')
        startAction.setStatusTip('Start Solving')
        startAction.triggered.connect(self.start)

        exitAction = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        openAction = QAction(QIcon('open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open new File')
        openAction.triggered.connect(self.showDialog)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(startAction)
        fileMenu.addAction(exitAction)

        self.setGeometry(300, 400, 600, 600)
        self.setWindowTitle('Schedule - Backtracking and Simulated Annealing')
        self.show()

    def showDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file')
        if fname:
            self.dial(fname)

    def dial(self, fname):
        self.instance = Configuration()
        self.instance.Parsefile(fname)
        self.best = False

    def start(self):
        self.solver_thread = SolverThread(self)
        self.solver_thread.start()
        self.solver_thread.finished.connect(self.on_solver_finished)

    @pyqtSlot()
    def on_solver_finished(self):
        self.update()

    def solve(self):
        teachers = list(professors.keys())
        subjects = list(courses.keys())

        variables = [(teacher, subject) for teacher in teachers for subject in subjects]
        domains = {
            (teacher, subject): [(teacher, subject, room['room'], room['day'], time) for room in classroom_availability for time in room['time']]
            for teacher in teachers for subject in subjects
        }
        constraints = {
            (teacher, subject): lambda value, assignment: no_teacher_overlap(value, assignment) and no_room_overlap(value, assignment)
            for teacher in teachers for subject in subjects
        }

        csp = CSP(variables, domains, constraints)
        optimal_schedule = csp.iterative_backtracking_search()
        method_used = "Backtracking"

        if not optimal_schedule:
            method_used = "Simulated Annealing"
            initial_schedule = initialize_schedule()
            initial_temperature = 1000
            cooling_rate = 0.95
            stopping_temperature = 0.1
            iteration_limit = 1000

            optimal_schedule, _ = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)

        if optimal_schedule:
            translated_schedule = translate_schedule(optimal_schedule)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            file_path = f'../output/best_schedule_{timestamp}.csv'
            save_schedule_to_csv(translated_schedule, file_path)
            print(f'Best schedule saved to CSV: {file_path}')
            print(f'Solution found using: {method_used}')
            self.best = True
            self.bestChromosome = optimal_schedule

    def paintEvent(self, e):
        if not self.best:
            return
        qp = QPainter(self)
        if qp.isActive():
            print("QPainter is already active")
            return
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
        DAYS_NUM = 5
        DAY_HOURS = 4

        GROUP_CELL_WIDTH = 95
        GROUP_CELL_HEIGHT = 60

        GROUP_MARGIN_WIDTH = 50
        GROUP_MARGIN_HEIGHT = 40

        GROUP_COLUMN_NUMBER = DAYS_NUM + 1
        GROUP_ROW_NUMBER = DAY_HOURS + 1

        GROUP_TABLE_WIDTH = GROUP_CELL_WIDTH * GROUP_COLUMN_NUMBER + GROUP_MARGIN_WIDTH
        GROUP_TABLE_HEIGHT = GROUP_CELL_HEIGHT * GROUP_ROW_NUMBER + GROUP_MARGIN_HEIGHT

        numberOfGroups = self.instance.GetNumberOfStudentGroups()

        for k in range(0, numberOfGroups):
            for i in range(0, GROUP_COLUMN_NUMBER):
                for j in range(0, GROUP_ROW_NUMBER):

                    l = k % 2
                    m = k // 2

                    WidthRect = 95
                    HeightRect = 60

                    XRect = GROUP_MARGIN_WIDTH + i * GROUP_CELL_WIDTH  + l * WidthRect * (GROUP_COLUMN_NUMBER + 1)
                    YRect = GROUP_MARGIN_HEIGHT + j * GROUP_CELL_HEIGHT + m * HeightRect * (GROUP_ROW_NUMBER + 1)

                    font = qp.font()
                    font.setWeight(QFont.Bold)
                    font.setPointSize(12)
                    font.setFamily("Cyrillic")
                    qp.setFont(font)

                    if i == 0 or j == 0:
                        r1 = QRect(XRect, YRect, WidthRect, HeightRect)

                    if i == 0 and j == 0:
                        font = qp.font()
                        font.setPointSize(10)
                        font.setBold(False)
                        font.setFamily("Cyrillic")
                        qp.setFont(font)
                        qp.drawText(r1, Qt.AlignCenter, "Group: " + self.instance.GetStudentsGroupById(str(k + 1)).GetName())
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

                    if i == 0 and j > 0:
                        qp.drawText(r1, Qt.AlignCenter, str(i + j))
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

                    if j == 0 and i > 0:
                        days = ["MON", "TUE", "WED", "THR", "FRI"]
                        qp.drawText(r1, Qt.AlignCenter, str(days[i - 1]))
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

        if self.best:
            font = qp.font()
            font.setPointSize(10)
            font.setBold(False)
            font.setFamily("Cyrillic")
            qp.setFont(font)
            qp.setPen(Qt.black)

            classes = self.bestChromosome.GetClasses()
            numberOfRooms = self.instance.GetNumberOfRooms()
            for it in classes.keys():
                c = it
                p = int(classes[it])

                t = p % (numberOfRooms * DAY_HOURS)
                d = p // (numberOfRooms * DAY_HOURS) + 1
                r = t // DAY_HOURS
                t = t % DAY_HOURS + 1

                grNumber = 0
                info = ''
                for k in range(0, numberOfGroups):
                    for l in c.GetGroups():
                        if l == self.instance.GetStudentsGroupById(str(k + 1)):
                            grNumber = k

                            l = grNumber % 2
                            m = grNumber // 2

                            XRect = l * WidthRect * (GROUP_COLUMN_NUMBER + 1) + GROUP_MARGIN_WIDTH + d * GROUP_CELL_WIDTH
                            YRect = m * HeightRect * (GROUP_ROW_NUMBER + 1) + GROUP_MARGIN_HEIGHT + t * GROUP_CELL_HEIGHT
                            WidthRect = 95
                            HeightRect = c.GetDuration() * GROUP_CELL_HEIGHT

                            info = c.GetCourse().GetName() + "\n" + c.GetProfessor().GetName() + "\n"
                            info += self.instance.GetRoomById(r).GetName() + " "
                            if c.IsLabRequired():
                                info += "Lab"

                            rect = QRect(XRect, YRect, WidthRect, HeightRect)
                            qp.drawText(rect, Qt.TextWordWrap | Qt.AlignVCenter | Qt.AlignHCenter, info)
                            qp.drawRect(XRect, YRect, WidthRect, HeightRect)

if __name__ == '__main__':
    time.sleep(10)
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

time.sleep(10)
