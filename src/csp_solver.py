import random
import csv
import time
import math
from Configuration import load_config
from sa_utils import initialize_schedule, objective_function, neighbor_solution, acceptance_probability, simulated_annealing

# Load configuration
config = load_config('../configuration files/data.cfg')

# Extract parameters from config
professors = {k.split('_')[1]: v for k, v in config.items('Professors')}
courses = {k.split('_')[1]: v for k, v in config.items('Courses')}
rooms = {k: room_details.split(',')[0].strip().lower() for k, room_details in config.items('Rooms')}  # Use room ids as-is
classroom_availability = []
for room, details in config.items('Rooms'):
    lab, capacity = details.split(',')
    classroom_availability.append({
        'room': room,
        'day': random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        'time': [i for i in range(1, 51)]  # Assume 50 time slots for simplicity
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

    def iterative_backtracking_search_relaxed(self):
        stack = [{}]
        while stack:
            assignment = stack.pop()
            if len(assignment) == len(self.variables):
                return assignment

            var = self.most_constrained_variable(assignment)
            for value in self.least_constraining_value(var, assignment):
                new_assignment = assignment.copy()
                new_assignment[var] = value
                stack.append(new_assignment)
        return None

def no_teacher_overlap(assignment_value, assignment):
    teacher, subject, room, day, time = assignment_value
    for key, value in assignment.items():
        t, s, r, d, ti = value
        if teacher == t and day == d and time == ti:
            print(f"Teacher overlap detected: {teacher} has overlapping classes at {day} {time}")
            return False
    return True

def no_room_overlap(assignment_value, assignment):
    teacher, subject, room, day, time = assignment_value
    for key, value in assignment.items():
        t, s, r, d, ti = value
        if room == r and day == d and time == ti:
            print(f"Room overlap detected: {room} has overlapping classes at {day} {time}")
            return False
    return True

def translate_schedule(best_schedule):
    translated = []
    print("Translating schedule. Best schedule format:", best_schedule)
    for key, value in best_schedule.items():
        try:
            teacher_id, course_id = key
            room_id, day, time_slot = value[2], value[3], value[4]
        except ValueError:
            print(f"Unexpected format: {key}, {value}")
            continue
        translated.append({
            'Professor': professors.get(teacher_id, f"Unknown ({teacher_id})"),
            'Course': courses.get(course_id, f"Unknown ({course_id})"),
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

# Define CSP problem
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

# Step 1: Use DRL-guided heuristic
try:
    from drl import drl_guided_heuristic
    print("Attempting with DRL-guided heuristic...")
    optimal_schedule = drl_guided_heuristic(variables, domains, constraints)
    method_used = "DRL-guided Heuristic"
except ImportError:
    print("DRL-guided heuristic module not found. Skipping this step.")
    optimal_schedule = None

# Step 2: Use iterative backtracking with relaxed constraints if DRL-guided heuristic fails
if not optimal_schedule:
    print("No solution found with DRL-guided heuristic. Trying with backtracking and relaxed constraints...")
    optimal_schedule = csp.iterative_backtracking_search_relaxed()
    method_used = "Backtracking with Relaxed Constraints"

# Step 3: Use standard iterative backtracking if previous methods fail
if not optimal_schedule:
    print("No solution found with relaxed constraints. Trying with standard backtracking...")
    optimal_schedule = csp.iterative_backtracking_search()
    method_used = "Standard Backtracking"

# Step 4: If all methods fail, use simulated annealing
if not optimal_schedule:
    print("No solution found with standard backtracking. Trying simulated annealing...")
    method_used = "Simulated Annealing"
    initial_schedule = initialize_schedule()
    initial_temperature = 1000
    cooling_rate = 0.95
    stopping_temperature = 0.1
    iteration_limit = 1000

    optimal_schedule, _ = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)

# Translate and save schedule
if optimal_schedule:
    translated_schedule = translate_schedule(optimal_schedule)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_path = f'../output/best_schedule_{timestamp}.csv'
    save_schedule_to_csv(translated_schedule, file_path)
    print(f'Best schedule saved to CSV: {file_path}')
    print(f'Solution found using: {method_used}')
else:
    print("No solution found.")
