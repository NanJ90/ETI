import csv

def load_schedule(file_path):
    schedule = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            schedule.append(row)
    return schedule

def print_schedule(schedule):
    for row in schedule:
        print(row)

# Path to the uploaded CSV file
file_path = 'output/best_schedule_20240516-211254.csv'

# Load and print the schedule
schedule = load_schedule(file_path)
print_schedule(schedule)
