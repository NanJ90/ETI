import random
import csv
import time
import math
from ConfigForSA import load_config
from sa_utils import initialize_schedule, objective_function, neighbor_solution, acceptance_probability, simulated_annealing
from timeit import default_timer as timer

# Load configuration
config = load_config('../configuration files/data.cfg')

# Extract parameters from config
professors = {k.split('_')[1]: v for k, v in config.items('Professors')}
courses = {k.split('_')[1]: v for k, v in config.items('Courses')}
rooms = {k: room_details.split(',')[0].strip().lower() for k, room_details in config.items('Rooms')}
classroom_availability = [
    {
        'room': room,
        'day': random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        'time': [i for i in range(1, 51)]  # Assume 50 time slots for simplicity
    }
    for room, details in config.items('Rooms')
]

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
        stack = [{}]  # Stack to store partial assignments
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
    if len(assignment_value) == 5:
        teacher, subject, room, day, time = assignment_value
    else:
        teacher, subject, room = assignment_value
        day, time = None, None

    for key, value in assignment.items():
        t, s, r, d, ti = value if len(value) == 5 else (*value, None, None)
        if teacher == t and day == d and time == ti:
            return False
    return True

def no_room_overlap(assignment_value, assignment):
    if len(assignment_value) == 5:
        teacher, subject, room, day, time = assignment_value
    else:
        teacher, subject, room = assignment_value
        day, time = None, None

    for key, value in assignment.items():
        t, s, r, d, ti = value if len(value) == 5 else (*value, None, None)
        if room == r and day == d and time == ti:
            return False
    return True

def translate_schedule(best_schedule):
    translated = []
    for key, value in best_schedule.items():
        teacher_id, course_id = key
        if len(value) == 5:
            room_id, day, time_slot = value[2], value[3], value[4]
        else:
            room_id, day, time_slot = value
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

def count_total_conflicts(schedule, csp):
    conflicts = 0
    for variable, value in schedule.items():
        teacher, subject = variable
        if len(value) == 5:
            room, day, time_slot = value[2], value[3], value[4]
        else:
            room, day, time_slot = value
        assignment_value = (teacher, subject, room, day, time_slot)
        conflicts += csp.count_conflicts(variable, assignment_value, schedule)
    return conflicts

def run_scheduler():
    # Define your CSP problem
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

    start_time = timer()
    optimal_schedule = csp.iterative_backtracking_search()

    method_used = "Backtracking"

    feasible_solution = False
    if not optimal_schedule:
        method_used = "Simulated Annealing"
        initial_schedule = initialize_schedule()
        initial_temperature = 1000
        cooling_rate = 0.95
        stopping_temperature = 0.1
        iteration_limit = 1000

        optimal_schedule, _ = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)
        feasible_solution = optimal_schedule is not None

    execution_time = timer() - start_time

    conflicts = 0
    if optimal_schedule:
        translated_schedule = translate_schedule(optimal_schedule)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_path = f'../output/best_schedule_{timestamp}.csv'
        # save_schedule_to_csv(translated_schedule, file_path)
        conflicts = count_total_conflicts(optimal_schedule, csp)
        success = conflicts == 0  # Only consider it a success if there are no conflicts
    else:
        print("No solution found.")
        success = False

    return execution_time, success, conflicts, feasible_solution, method_used

# Performance analysis
num_runs = 5
total_execution_time = 0
total_conflicts = 0
optimal_success_count = 0
feasible_success_count = 0

for _ in range(num_runs):
    execution_time, success, conflicts, feasible_solution, method_used = run_scheduler()
    total_execution_time += execution_time
    total_conflicts += conflicts
    if success:
        optimal_success_count += 1
    if feasible_solution:
        feasible_success_count += 1

average_execution_time = total_execution_time / num_runs
average_conflicts = total_conflicts / num_runs
optimal_success_rate = optimal_success_count / num_runs
feasible_success_rate = feasible_success_count / num_runs

print(f'Average Execution Time: {average_execution_time:.6f} seconds')
print(f'Average Conflicts: {average_conflicts:.2f}')
print(f'Optimal Success Rate: {optimal_success_rate * 100:.2f}%')
print(f'Feasible Success Rate: {feasible_success_rate * 100:.2f}%')

# Save the evaluation report
evaluation_report = {
    'Average Execution Time (s)': average_execution_time,
    'Optimal Success Rate': optimal_success_rate,
    'Feasible Success Rate': feasible_success_rate,
    'Average Conflicts': average_conflicts,
}

with open('evaluation_report.csv', 'w', newline='') as csvfile:
    fieldnames = evaluation_report.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(evaluation_report)
