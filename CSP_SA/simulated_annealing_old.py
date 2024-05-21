import json
import math
import random


# with open('../data/small_data.json') as f:
#     schedule = json.load(f)

def read_config(file_name):
    config =
def format_output(output):
    formatted_output = []
    for teacher, classroom in output:
        formatted_output.append(f"{teacher['name']} is teaching {teacher['subject']} in {classroom['room']} on {classroom['day']} at {classroom['time'][0]} to {classroom['time'][1]}")
    return "\n".join(formatted_output)

def simulated_annealing(problem, T0, tau, tmax):
    current = problem.initial()
    for t in range(tmax):
        T = T0 * math.exp(-t/tau)
        if T == 0:
            return current
        next = random.choice(problem.neighbours(current))
        delta = problem.value(next) - problem.value(current)
        if delta > 0 or random.random() < math.exp(delta / T):
            current = next
    return current

class Problem:
    def __init__(self, teachers, subjects, classroom_availability):
        self.teachers = teachers
        self.subjects = subjects
        self.classroom_availability = classroom_availability
    def initial(self):
        assignment = []
        for teacher in self.teachers:
          for teacher in self.teachers:
            subject = random.choice(self.subjects)
            classroom = random.choice(self.classroom_availability)
            time = random.choice(classroom["time"])
            assignment.append((teacher, subject, classroom["room"], classroom["day"], time))
        return assignment
    def value(self, assignment):
        penalties = 0
        for i, (teacher1, subject1, room1, day1, time1) in enumerate(assignment):
            for j, (teacher2, subject2, room2, day2, time2) in enumerate(assignment):
                if i != j:
                    if teacher1 == teacher2 and day1 == day2 and time1 == time2:
                        penalties += 1  # Same teacher teaching two subjects at the same time
                    if room1 == room2 and day1 == day2 and time1 == time2:
                        penalties += 1  # Same room occupied at the same time
        return -penalties  # The goal is to minimize penalties, hence return the negative value
    def neighbours(self, assignment):
        # Generate neighbors by randomly modifying the schedule
        neighbors = []
        for i in range(len(assignment)):
            new_assignment = list(assignment)
            teacher, subject, room, day, time = new_assignment[i]

            # Randomly change classroom or time slot for the current teacher-subject pair
            if random.choice([True, False]):
                while True:
                    new_classroom = random.choice(self.classroom_availability)
                    new_room = new_classroom["room"]
                    new_day = new_classroom["day"]
                    new_time = random.choice(new_classroom["time"])
                    if not any(t == teacher and r == new_room and d == new_day and t == new_time for t, s, r, d, t in new_assignment):
                        break
                new_assignment[i] = (teacher, subject, new_room, new_day, new_time)
            else:
                while True:
                    new_teacher = random.choice(self.teachers)
                    if not any(t == new_teacher and d == day and t == time for t, s, r, d, t in new_assignment):
                        break
                new_assignment[i] = (new_teacher, subject, room, day, time)
            neighbors.append(new_assignment)
        return neighbors

# Define your CSP problem
teachers = schedule['teachers']
subjects = schedule['subjects']
classroom_availability = schedule['classroom_availability']

variables = [(teacher, subject,classroom) for teacher in teachers for subject in subjects for classroom in classroom_availability]


problem = Problem(teachers, subjects, classroom_availability)

T0 = 1
tau = 0.01
tmax = 1000
# print(simulated_annealing(problem, T0, tau, tmax))
optimal_schedule = simulated_annealing(problem, T0, tau, tmax)
print("Optimal Schedule:")
for teacher, subject, room, day, time in optimal_schedule:
    print(f"{teacher['name']} teaching {subject['name']} in {room} on {day} at {time}")
class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

    def is_solution(self, assignment):
        # Check if an assignment is a solution
        for variable, value in assignment.items():
            if not self.constraints[variable](value, assignment):
                return False
        return True

    def backtracking_search(self, assignment={}):
        # If all variables have been assigned, return the assignment
        if len(assignment) == len(self.variables):
            return assignment

        # Select an unassigned variable
        unassigned = [v for v in self.variables if v not in assignment]
        first = unassigned[0]

        # Try every option for the first unassigned variable
        for value in self.domains[first]:
            assignment[first] = value
            if self.is_solution(assignment):
                result = self.backtracking_search(assignment)
                if result is not None:
                    return result
            assignment.pop(first)

        return None


# domains = {}

# for variable in variables:
    # domains[variable] = [classroom for classroom, availability in classroom_availability.items() if availability[subjects] == 1]
# print(variables)        
# print(domains)
# csp = CSP(variables, domains, constraints,'../data/small_data.json')

# # Use simulated annealing to find an initial solution
# initial_solution = simulated_annealing(problem, T0, tau, tmax)

# # If the solution from simulated annealing satisfies all constraints, return it
# if csp.is_solution(initial_solution):
#     print(initial_solution)
# else:
#     # If not, use backtracking to find a solution that satisfies all constraints
#     solution = csp.backtracking_search(initial_solution)
#     print(solution)