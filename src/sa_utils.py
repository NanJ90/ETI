import random
import math
from Configuration import load_config

# Load configuration
config = load_config('../configuration files/data.cfg')

# Extract parameters from config
rooms = {k.split('_')[0]: k.lower() for k, v in config.items('Rooms')}  # Use room ids as-is

def initialize_schedule():
    schedule = {}
    for class_id, info in config.items('Classes'):
        professor_id, course_id = class_id.split('_')[1], class_id.split('_')[3]
        room_id = random.choice(list(rooms.keys()))
        day = random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        time_slot = random.randint(1, 50)  # Assume 50 time slots for simplicity
        schedule[(professor_id, course_id)] = (room_id, day, time_slot)
    return schedule

def objective_function(schedule):
    conflicts = 0
    room_usage = {}
    for (professor_id, course_id), (room_id, day, time_slot) in schedule.items():
        if (room_id, day, time_slot) in room_usage:
            conflicts += 1
        else:
            room_usage[(room_id, day, time_slot)] = 1
    return conflicts

def neighbor_solution(current_schedule):
    new_schedule = current_schedule.copy()
    class_to_change = random.choice(list(new_schedule.keys()))
    new_schedule[class_to_change] = (
        random.choice(list(rooms.keys())),
        random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        random.randint(1, 50)
    )
    return new_schedule

def acceptance_probability(current_value, new_value, temperature):
    if new_value < current_value:
        return 1.0
    return math.exp((current_value - new_value) / temperature)

def simulated_annealing(objective_function, initial_solution, initial_temperature, cooling_rate, stopping_temperature, iteration_limit):
    current_solution = initial_solution
    current_value = objective_function(current_solution)
    best_solution = current_solution
    best_value = current_value

    temperature = initial_temperature
    iteration = 0

    while temperature > stopping_temperature and iteration < iteration_limit:
        new_solution = neighbor_solution(current_solution)
        new_value = objective_function(new_solution)

        if acceptance_probability(current_value, new_value, temperature) > random.random():
            current_solution = new_solution
            current_value = new_value

            if new_value < best_value:
                best_solution = new_solution
                best_value = new_value

        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_value
