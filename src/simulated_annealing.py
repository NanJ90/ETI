import json
import math
import random

with open('../data/small_data.json') as f:
    schedule = json.load(f)

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
    def initial(self):
        return [0, 0, 0, 0]
    def value(self, state):
        return sum(state)
    def neighbours(self, state):
        return [[state[0] + random.choice([-1, 1]), state[1], state[2], state[3]],
                [state[0], state[1] + random.choice([-1, 1]), state[2], state[3]],
                [state[0], state[1], state[2] + random.choice([-1, 1]), state[3]],
                [state[0], state[1], state[2], state[3] + random.choice([-1, 1])]]

problem = Problem()
T0 = 1
tau = 0.01
tmax = 1000
print(simulated_annealing(problem, T0, tau, tmax))

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

# Define your CSP problem
csp = CSP(variables, domains, constraints)

# Use simulated annealing to find an initial solution
initial_solution = simulated_annealing(problem, T0, tau, tmax)

# If the solution from simulated annealing satisfies all constraints, return it
if csp.is_solution(initial_solution):
    print(initial_solution)
else:
    # If not, use backtracking to find a solution that satisfies all constraints
    solution = csp.backtracking_search(initial_solution)
    print(solution)