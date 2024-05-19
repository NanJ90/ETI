import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog, QMenu
from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QRect
from threading import Thread
import time
import random
import math
import csv 
from datetime import datetime

from Configuration import Configuration
from CourseClass import CourseClass
from functools import partial
from random import randint

import csv
from datetime import datetime
import time

def save_schedule_to_csv(schedule, algorithm_name):
    numberOfRooms = instance.GetNumberOfRooms()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"../output/schedule_{algorithm_name}_{timestamp}.csv"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Group", "Day", "Hour", "Room", "Course", "Professor"])

        classes = schedule.GetClasses()
        for course_class, position in classes.items():
            day = position // (numberOfRooms * DAY_HOURS) + 1
            time = position % (numberOfRooms * DAY_HOURS)
            room = time // DAY_HOURS
            time = time % DAY_HOURS + 1

            group_names = [group.GetName() for group in course_class.GetGroups()]
            writer.writerow([
                ", ".join(group_names),
                day,
                time,
                instance.GetRoomById(room).GetName(),
                course_class.GetCourse().GetName(),
                course_class.GetProfessor().GetName()
            ])


# Genetic algorithm
class Algorithm:
    def __init__(self, numberOfChromosomes, replaceByGeneration, trackBest, prototype):
        self.replaceByGeneration = replaceByGeneration
        self.prototype = prototype
        self.currentBestSize = 0
        self.currentGeneration = 0

        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        if trackBest < 1:
            trackBest = 1

        if self.replaceByGeneration < 1:
            self.replaceByGeneration = 1
        elif self.replaceByGeneration > numberOfChromosomes - trackBest:
            self.replaceByGeneration = numberOfChromosomes - trackBest

        self.chromosomes = numberOfChromosomes * [None]
        self.bestFlags = numberOfChromosomes * [False]
        self.bestChromosomes = trackBest * [None]

    def GetInstance():
        prototype = Schedule(2, 2, 80, 3)
        instance = Algorithm(100, 8, 5, prototype)
        return instance

    def Start(self):
        for it in range(len(self.chromosomes)):
            if self.chromosomes[it]:
                del self.chromosomes[it]

            self.chromosomes[it] = self.prototype.MakeNewFromPrototype()
            self.AddToBest(it)

        self.currentGeneration = 0
        random.seed()
        lengthOfChromosomes = len(self.chromosomes)

        while 1:
            best = self.GetBestChromosome()
            if best.GetFitness() >= 1:
                return best

            offspring = self.replaceByGeneration * [None]
            for j in range(0, self.replaceByGeneration):
                a = randint(0, 327670) % lengthOfChromosomes
                b = randint(0, 327670) % lengthOfChromosomes
                p1 = self.chromosomes[a]
                p2 = self.chromosomes[b]
                offspring[j] = p1.Crossover(p2)
                offspring[j].Mutation()

            for j in range(0, self.replaceByGeneration):
                ci = randint(0, 32767) % len(self.chromosomes)
                while self.IsInBest(ci):
                    ci = randint(0, 32767) % len(self.chromosomes)

                self.chromosomes[ci] = offspring[j]
                self.AddToBest(ci)

            self.currentGeneration = self.currentGeneration + 1

    def GetBestChromosome(self):
        return self.chromosomes[self.bestChromosomes[0]]

    def AddToBest(self, chromosomeIndex):
        if (self.currentBestSize == len(self.bestChromosomes) and self.chromosomes[self.bestChromosomes[self.currentBestSize - 1]].GetFitness() >=
                self.chromosomes[chromosomeIndex].GetFitness()) or self.bestFlags[chromosomeIndex]:
            return

        i = self.currentBestSize
        j = 0
        for i in range(self.currentBestSize, 0, -1):
            if i < len(self.bestChromosomes):
                if self.chromosomes[self.bestChromosomes[i - 1]].GetFitness() > \
                        self.chromosomes[chromosomeIndex].GetFitness():
                    j = i
                    break
                self.bestChromosomes[i] = self.bestChromosomes[i - 1]
            else:
                self.bestFlags[self.bestChromosomes[i - 1]] = False
            j = i - 1

        self.bestChromosomes[j] = chromosomeIndex
        self.bestFlags[chromosomeIndex] = True

        if self.currentBestSize < len(self.bestChromosomes):
            self.currentBestSize = self.currentBestSize + 1

    def IsInBest(self, chromosomeIndex):
        return self.bestFlags[chromosomeIndex]

    def ClearBest(self):
        for i in range(len(self.bestFlags), -1, -1):
            self.bestFlags[i] = False

        self.currentBestSize = 0


DAY_HOURS = 4
DAYS_NUM = 5


class Schedule:
    def __init__(self, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability):
        self.numberOfCrossoverPoints = numberOfCrossoverPoints
        self.mutationSize = mutationSize
        self.crossoverProbability = crossoverProbability
        self.mutationProbability = mutationProbability
        self.fitness = 0
        self.slots = []
        self.criteria = []
        self.score = 0
        self.classes = {}
        self.slots = (DAYS_NUM * DAY_HOURS * instance.GetNumberOfRooms()) * [None]
        self.criteria = (instance.GetNumberOfCourseClasses() * 5) * [None]

    def GetClasses(self):
        return self.classes

    def copy(self, setupOnly):
        c = Schedule(0, 0, 0, 0)
        if not setupOnly:
            c.slots = self.slots
            c.classes = self.classes
            c.criteria = self.criteria
            c.fitness = self.fitness
        else:
            c.slots = (DAYS_NUM * DAY_HOURS * instance.GetNumberOfRooms()) * [None]
            c.criteria = (instance.GetNumberOfCourseClasses() * 5) * [None]

        c.numberOfCrossoverPoints = self.numberOfCrossoverPoints
        c.mutationSize = self.mutationSize
        c.crossoverProbability = self.crossoverProbability
        c.mutationProbability = self.mutationProbability
        c.score = self.score

        return c

    def MakeNewFromPrototype(self):
        size = len(self.slots)
        newChromosome = self.copy(True)
        c = instance.GetCourseClasses()
        nr = instance.GetNumberOfRooms()
        maxLength = nr * DAY_HOURS * DAYS_NUM
        for it in c:
            dur = it.GetDuration()
            day = randint(0, 32767) % DAYS_NUM
            room = randint(0, 32767) % nr
            time = randint(0, 32767) % (DAY_HOURS + 1 - dur)
            pos = day * nr * DAY_HOURS + room * DAY_HOURS + time
            newChromosome.classes[it] = pos

            for i in range(dur - 1, -1, -1):
                if newChromosome.slots[pos + i] is None:
                    newChromosome.slots[pos + i] = [it]
                else:
                    newChromosome.slots[pos + i].append(it)

            newChromosome.classes[it] = pos

        newChromosome.CalculateFitness()
        return newChromosome

    def Crossover(self, parent2):
        if randint(0, 32767) % 100 > self.crossoverProbability:
            return self.copy(False)

        n = self.copy(True)
        size = len(self.classes)
        cp = size * [None]

        for i in range(self.numberOfCrossoverPoints, 0, -1):
            while 1:
                p = randint(0, 32767) % size
                if not cp[p]:
                    cp[p] = True
                    break

        j = 0
        first = randint(0, 1) == 0
        for i in range(0, size):
            if first:
                if j >= len(list(self.classes.keys())):
                    break
                it1 = self.classes[list(self.classes.keys())[j]]
                n.classes[list(self.classes.keys())[j]] = it1
                for k in range(list(self.classes.keys())[j].GetDuration() - 1, -1, -1):
                    if n.slots[it1 + k] is None:
                        n.slots[it1 + k] = [list(self.classes.keys())[j]]
                    else:
                        n.slots[it1 + k].append(list(self.classes.keys())[j])
            else:
                if j >= len(list(parent2.classes.keys())):
                    break
                it2 = parent2.classes[list(parent2.classes.keys())[j]]
                n.classes[list(parent2.classes.keys())[j]] = it2
                for k in range(list(parent2.classes.keys())[j].GetDuration() - 1, -1, -1):
                    if n.slots[it2 + k] is None:
                        n.slots[it2 + k] = [list(parent2.classes.keys())[j]]
                    else:
                        n.slots[it2 + k].append(list(parent2.classes.keys())[j])

            if cp[i]:
                first = not first

            j = j + 1

        n.CalculateFitness()
        return n

    def Mutation(self):
        if randint(0, 32767) % 100 > self.mutationProbability:
            return None

        numberOfClasses = len(self.classes)
        size = len(self.slots)

        for i in range(self.mutationSize, 0, -1):
            mpos = randint(0, 32767) % numberOfClasses
            pos1 = self.classes[list(self.classes.keys())[mpos]]
            it = list(self.classes.keys())[mpos]
            cc1 = it

            nr = instance.GetNumberOfRooms()
            dur = cc1.GetDuration()
            day = randint(0, 32767) % DAYS_NUM
            room = randint(0, 32767) % nr
            time = randint(0, 32767) % (DAY_HOURS + 1 - dur)
            pos2 = day * nr * DAY_HOURS + room * DAY_HOURS + time

            for j in range(dur - 1, -1, -1):
                c1 = self.slots[pos1 + j]
                for k in range(0, len(c1)):
                    if c1[k] == cc1:
                        del c1[k]
                        break

                if self.slots[pos2 + j] is None:
                    self.slots[pos2 + j] = [cc1]
                else:
                    self.slots[pos2 + j].append(cc1)

            self.classes[cc1] = pos2
        self.CalculateFitness()

    def CalculateFitness(self):
        score = 0
        numberOfRooms = instance.GetNumberOfRooms()
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        for i in self.classes.keys():
            p = self.classes[i]
            day = p // daySize
            time = p % daySize
            room = time // DAY_HOURS
            time = time % DAY_HOURS

            dur = i.GetDuration()
            ro = False
            for j in range(dur - 1, -1, -1):
                if len(self.slots[p + j]) > 1:
                    ro = True
                    break

            if not ro:
                score = score + 1

            self.criteria[ci + 0] = not ro

            cc = i
            r = instance.GetRoomById(room)
            self.criteria[ci + 1] = r.GetNumberOfSeats() >= cc.GetNumberOfSeats()
            if self.criteria[ci + 1]:
                score = score + 1

            self.criteria[ci + 2] = (not cc.IsLabRequired()) or (cc.IsLabRequired() and r.IsLab())
            if self.criteria[ci + 2]:
                score = score + 1

            po = False
            go = False
            t = day * daySize + time
            breakPoint = False
            for k in range(numberOfRooms, 0, -1):
                if breakPoint:
                    break
                for l in range(dur - 1, -1, -1):
                    if breakPoint:
                        break
                    cl = self.slots[t + l]
                    if not cl is None:
                        for it in cl:
                            if breakPoint:
                                break
                            if cc != it:
                                if not po and cc.ProfessorOverlaps(it):
                                    po = True
                                if not go and cc.GroupsOverlap(it):
                                    go = True
                                if po and go:
                                    breakPoint = True

                t = t + DAY_HOURS

            if not po:
                score = score + 1
            self.criteria[ci + 3] = not po

            if not go:
                score = score + 1
            self.criteria[ci + 4] = not go

            ci += 5

        self.fitness = score / (instance.GetNumberOfCourseClasses() * DAYS_NUM)
        self.score = score

    def GetFitness(self):
        return self.fitness

class BacktrackingSolution:
    def __init__(self):
        self.classes = {}
        self.slots = (DAYS_NUM * DAY_HOURS * instance.GetNumberOfRooms()) * [None]

    def GetClasses(self):
        return self.classes

    def setClasses(self, classes):
        for course_class, position in classes:
            self.classes[course_class] = position
            dur = course_class.GetDuration()
            for i in range(dur):
                self.slots[position + i] = [course_class]

test = "test"
algorithm_type = "Genetic Algorithm"
instance = None

class Example(QMainWindow):
    trigger = pyqtSignal()

    def __init__(self):
        super().__init__()
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

        self.geneticAction = QAction("Genetic Algorithm", self, checkable=True)
        self.geneticAction.setChecked(True)
        self.geneticAction.triggered.connect(partial(self.setAlgorithm, "Genetic Algorithm"))

        self.backtrackingAction = QAction("Backtracking with Simulated Annealing", self, checkable=True)
        self.backtrackingAction.setChecked(False)
        self.backtrackingAction.triggered.connect(partial(self.setAlgorithm, "Backtracking with Simulated Annealing"))

        algorithmMenu = QMenu("Algorithm", self)
        algorithmMenu.addAction(self.geneticAction)
        algorithmMenu.addAction(self.backtrackingAction)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(startAction)
        fileMenu.addAction(exitAction)
        menubar.addMenu(algorithmMenu)

        self.setGeometry(300, 400, 600, 600)
        self.setWindowTitle('Schedule Solver')

        self.show()


    def setAlgorithm(self, algorithm):
        global algorithm_type
        algorithm_type = algorithm
        print(f"Selected Algorithm: {algorithm_type}")

        # Ensure only one algorithm is selected at a time
        if algorithm == "Genetic Algorithm":
            self.geneticAction.setChecked(True)
            self.backtrackingAction.setChecked(False)
        elif algorithm == "Backtracking with Simulated Annealing":
            self.geneticAction.setChecked(False)
            self.backtrackingAction.setChecked(True)


    def showDialog(self):
        global fname
        fname = QFileDialog.getOpenFileName(self, 'Open file')
        if fname[0]:
            t = Thread(target=self.dial)
            t.start()
            t.join()

    def dial(self):
        global instance
        instance = Configuration()
        instance.Parsefile(fname[0])
        global test
        test = "aaa"
        global best
        best = False

    # Ensure bestChromosome is defined before saving the schedule
    def start(self):
        tic = time.time()
        t1 = Thread(target=self.alg)
        t1.start()
        t1.join()

        toc = time.time()
        duration = toc - tic
        global bestChromosome

        if bestChromosome:
            print(f"Time taken to generate schedule: {duration:.2f} seconds")
            save_schedule_to_csv(bestChromosome, algorithm_type)
        else:
            print("Failed to generate a valid schedule.")
    def alg(self):
        global bestChromosome
        global best
        global instance

        if algorithm_type == "Genetic Algorithm":
            prototype = Schedule(2, 2, 80, 3)
            algorithm = Algorithm(100, 8, 5, prototype)
            bestChromosome = algorithm.Start()
            best = True
        elif algorithm_type == "Backtracking with Simulated Annealing":
            bestChromosome = solve_backtracking(instance)
            best = True

    def paintEvent(self, e):
        if test == "test":
            return
        qp = QPainter(self)
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

        numberOfGroups = instance.GetNumberOfStudentGroups()

        for k in range(0, numberOfGroups):
            for i in range(0, GROUP_COLUMN_NUMBER):
                for j in range(0, GROUP_ROW_NUMBER):
                    l = k % 2
                    m = k // 2

                    WidthRect = 95
                    HeightRect = 60

                    XRect = GROUP_MARGIN_WIDTH + i * GROUP_CELL_WIDTH + l * WidthRect * (GROUP_COLUMN_NUMBER + 1)
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
                        qp.drawText(r1, Qt.AlignCenter, "Group: " + instance.GetStudentsGroupById(str(k + 1)).GetName())
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

                    if i == 0 and j > 0:
                        qp.drawText(r1, Qt.AlignCenter, str(i + j))
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

                    if j == 0 and i > 0:
                        days = ["MON", "TUE", "WED", "THR", "FRI"]
                        qp.drawText(r1, Qt.AlignCenter, str(days[i - 1]))
                        qp.drawRect(XRect, YRect, WidthRect, HeightRect)

        if best:
            font = qp.font()
            font.setPointSize(10)
            font.setBold(False)
            font.setFamily("Cyrillic")
            qp.setFont(font)
            qp.setPen(Qt.black)

            classes = bestChromosome.GetClasses()
            numberOfRooms = instance.GetNumberOfRooms()
            for it in classes.keys():
                c = it
                p = int(classes[it])

                t = p % (numberOfRooms * DAY_HOURS)
                d = p // (numberOfRooms * DAY_HOURS) + 1
                r = t // DAY_HOURS
                t = t % DAY_HOURS + 1

                for k in range(0, numberOfGroups):
                    for l in c.GetGroups():
                        if l == instance.GetStudentsGroupById(str(k + 1)):
                            grNumber = k

                            l = grNumber % 2
                            m = grNumber // 2

                            XRect = l * WidthRect * (GROUP_COLUMN_NUMBER + 1) + GROUP_MARGIN_WIDTH + d * GROUP_CELL_WIDTH
                            YRect = m * HeightRect * (GROUP_ROW_NUMBER + 1) + GROUP_MARGIN_HEIGHT + t * GROUP_CELL_HEIGHT
                            WidthRect = 95
                            HeightRect = c.GetDuration() * GROUP_CELL_HEIGHT

                            info = c.GetCourse().GetName() + "\n" + c.GetProfessor().GetName() + "\n"
                            info += instance.GetRoomById(r).GetName() + " "
                            if c.IsLabRequired():
                                info += "Lab"

                            rect = QRect(XRect, YRect, WidthRect, HeightRect)
                            qp.drawText(rect, Qt.TextWordWrap | Qt.AlignVCenter | Qt.AlignHCenter, info)
                            qp.drawRect(XRect, YRect, WidthRect, HeightRect)
                            qp.setClipRect(rect)  # Ensure text is clipped to the rect
            test = "aaa"


# Backtracking with Simulated Annealing implementation
def solve_backtracking(config):
    current_solution = initial_solution(config)
    current_cost = calculate_cost(current_solution)

    temperature = 100.0
    cooling_rate = 0.99
    min_temperature = 0.1

    best_solution = current_solution
    best_cost = current_cost

    while temperature > min_temperature:
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_cost = calculate_cost(neighbor_solution)

        if accept_solution(current_cost, neighbor_cost, temperature):
            current_solution = neighbor_solution
            current_cost = neighbor_cost

            if neighbor_cost < best_cost:
                best_solution = neighbor_solution
                best_cost = neighbor_cost

        temperature *= cooling_rate

    solution_obj = BacktrackingSolution()
    solution_obj.setClasses(best_solution)
    return solution_obj

def initial_solution(config):
    solution = []
    temp_solution = BacktrackingSolution()
    for course_class in config.GetCourseClasses():
        position = generate_initial_position(course_class, temp_solution)
        temp_solution.setClasses([(course_class, position)])
        solution.append((course_class, position))
    return solution

# Update generate_initial_position to handle conflict checks using temp_solution
def generate_initial_position(course_class, temp_solution):
    nr = instance.GetNumberOfRooms()
    dur = course_class.GetDuration()
    
    while True:
        day = randint(0, 32767) % DAYS_NUM
        room = randint(0, 32767) % nr
        time = randint(0, 32767) % (DAY_HOURS + 1 - dur)
        pos = day * nr * DAY_HOURS + room * DAY_HOURS + time

        # Check for conflicts in the generated position using temp_solution slots
        conflict = False
        for i in range(dur):
            if pos + i < len(temp_solution.slots) and temp_solution.slots[pos + i] is not None:
                conflict = True
                break

        if not conflict:
            break

    return pos

# Ensure the alg method properly defines bestChromosome
def alg(self):
    global bestChromosome
    global best
    global instance

    if algorithm_type == "Genetic Algorithm":
        prototype = Schedule(2, 2, 80, 3)
        algorithm = Algorithm(100, 8, 5, prototype)
        bestChromosome = algorithm.Start()
        best = True
    elif algorithm_type == "Backtracking with Simulated Annealing":
        bestChromosome = solve_backtracking(instance)
        if bestChromosome is not None:
            best = True


def calculate_cost(solution):
    cost = 0
    for course_class, value in solution:
        cost += value  # Dummy cost calculation
    return cost

def generate_neighbor(solution):
    neighbor = solution[:]
    if neighbor:
        neighbor[0] = (neighbor[0][0], neighbor[0][1] + 1)  # Simple neighbor generation
    return neighbor

def accept_solution(current_cost, neighbor_cost, temperature):
    if neighbor_cost < current_cost:
        return True
    else:
        acceptance_probability = math.exp((current_cost - neighbor_cost) / temperature)
        return random.random() < acceptance_probability


if __name__ == '__main__':
    time.sleep(1)
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
