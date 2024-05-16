import random
from sa_utils import initialize_schedule, objective_function, simulated_annealing

if __name__ == "__main__":
    initial_schedule = initialize_schedule()
    initial_temperature = 1000
    cooling_rate = 0.95
    stopping_temperature = 0.1
    iteration_limit = 1000

    best_schedule, best_value = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)

    print(f"Best schedule: {best_schedule}, Conflicts: {best_value}")
