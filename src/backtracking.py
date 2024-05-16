import random
import csv
import time
import math
from Configuration import load_config
from sa_utils import initialize_schedule, objective_function, neighbor_solution, acceptance_probability, simulated_annealing

# Load configuration
config = load_config('data.cfg')

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
        # Check if an assignment is a solution
        for variable, value in assignment.items():
            if not self.constraints.get(variable, lambda x, y: True)(value, assignment):
                return False
        return True

    def most_constrained_variable(self, assignment):
        # Choose the variable with the fewest legal values
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def least_constraining_value(self, variable, assignment):
        # Choose the value that rules out the fewest choices for the neighboring variables
        return sorted(self.domains[variable], key=lambda val: self.count_conflicts(variable, val, assignment))

    def count_conflicts(self, variable, value, assignment):
        # Count the number of conflicts the value causes
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

    def iterative_backtracking_search_relaxed(self):
        stack = [{}]  # Stack to store partial assignments
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
    # Ensure no teacher has overlapping classes
    teacher, subject, room, day, time = assignment_value
    for key, value in assignment.items():
        t, s, r, d, ti = value
        if teacher == t and day == d and time == ti:
            return False
    return True

def no_room_overlap(assignment_value, assignment):
    # Ensure no room has overlapping classes
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

# Attempt 1: Use iterative backtracking with heuristics
print("Attempting with backtracking and heuristics...")
optimal_schedule = csp.iterative_backtracking_search()
method_used = "Backtracking with Heuristics"

# Attempt 2: If no solution, use iterative backtracking with relaxed constraints
if not optimal_schedule:
    print("No solution found with backtracking and heuristics. Trying with relaxed constraints...")
    optimal_schedule = csp.iterative_backtracking_search_relaxed()
    method_used = "Backtracking with Relaxed Constraints"

# Attempt 3: If still no solution, use simulated annealing
if not optimal_schedule:
    print("No solution found with relaxed constraints. Trying simulated annealing...")
    method_used = "Simulated Annealing"
    initial_schedule = initialize_schedule()
    initial_temperature = 1000
    cooling_rate = 0.95
    stopping_temperature = 0.1
    iteration_limit = 1000

    optimal_schedule, _ = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)

# Translate the schedule to descriptive data and save to CSV
if optimal_schedule:
    translated_schedule = translate_schedule(optimal_schedule)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_path = f'best_schedule_{timestamp}.csv'
    save_schedule_to_csv(translated_schedule, file_path)
    print(f'Best schedule saved to CSV: {file_path}')
    print(f'Solution found using: {method_used}')
else:
    print("No solution found.")
