# File path: simulated_annealing.py

import random
import math
import csv
from Configuration import load_config

# Load configuration
config = load_config('data.cfg')

# Extract parameters from config
initial_temperature = float(config['SimulatedAnnealing']['initial_temperature'])
cooling_rate = float(config['SimulatedAnnealing']['cooling_rate'])
stopping_temperature = 0.1  # Assuming default stopping temperature
iteration_limit = int(config['SimulatedAnnealing']['iteration_limit'])

# Extract descriptive mappings
professors = {k.split('_')[1]: v for k, v in config.items('Professors')}
courses = {k.split('_')[1]: v for k, v in config.items('Courses')}
rooms = {k.split('_')[0]: k.lower() for k, v in config.items('Rooms')}  # Use room ids as-is

def parse_class_info(info):
    parts = info.split(',')
    duration = int(parts[0].split(': ')[1])
    group = int(parts[1].split(': ')[1])
    lab = len(parts) > 2 and parts[2].split(': ')[1] == 'true'
    return duration, group, lab

def initialize_schedule():
    schedule = {}
    for class_id, info in config.items('Classes'):
        professor_id, course_id = class_id.split('_')[1], class_id.split('_')[3]
        room_id = random.choice(list(rooms.keys()))
        time_slot = random.randint(1, 50)  # Assume 50 time slots for simplicity
        schedule[(professor_id, course_id)] = (room_id, time_slot)
    return schedule

def objective_function(schedule):
    conflicts = 0
    room_usage = {}
    for (professor_id, course_id), (room_id, time_slot) in schedule.items():
        if (room_id, time_slot) in room_usage:
            conflicts += 1
        else:
            room_usage[(room_id, time_slot)] = 1
    return conflicts

def neighbor_solution(current_schedule):
    new_schedule = current_schedule.copy()
    class_to_change = random.choice(list(new_schedule.keys()))
    new_schedule[class_to_change] = (
        random.choice(list(rooms.keys())),
        random.randint(1, 50)
    )
    return new_schedule

def acceptance_probability(current_value, new_value, temperature):
    if new_value < current_value:
        return 1.0
    return math.exp((current_value - new_value) / temperature)

def simulated_annealing(objective_function, initial_solution, temperature, cooling_rate, stopping_temperature, iteration_limit):
    current_solution = initial_solution
    current_value = objective_function(current_solution)
    best_solution = current_solution
    best_value = current_value

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

        print(f"Iteration {iteration}, Temp {temperature:.4f}, Current Conflicts {current_value}, Best Conflicts {best_value}")

    return best_solution, best_value

def translate_schedule(best_schedule):
    translated = []
    for (professor_id, course_id), (room_id, time_slot) in best_schedule.items():
        translated.append({
            'Professor': professors[professor_id],
            'Course': courses[course_id],
            'Room': room_id,
            'Time Slot': time_slot
        })
    return translated

def save_schedule_to_csv(schedule, file_path='best_schedule.csv'):
    keys = schedule[0].keys()
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(schedule)

# Initialize schedule and run simulated annealing
initial_schedule = initialize_schedule()
best_schedule, best_value = simulated_annealing(objective_function, initial_schedule, initial_temperature, cooling_rate, stopping_temperature, iteration_limit)

# Translate best schedule to descriptive data and save to CSV
translated_schedule = translate_schedule(best_schedule)
save_schedule_to_csv(translated_schedule)

print(f'Best schedule saved to CSV with Conflicts: {best_value}')
