import csv

def validate_schedule(schedule):
    teacher_schedule = {}
    room_schedule = {}

    for entry in schedule:
        professor = entry['Professor']
        course = entry['Course']
        room = entry['Room']
        day = entry['Day']
        time_slot = entry['Time Slot']

        # Check teacher schedule
        if professor not in teacher_schedule:
            teacher_schedule[professor] = []
        teacher_schedule[professor].append((day, time_slot))

        # Check room schedule
        if room not in room_schedule:
            room_schedule[room] = []
        room_schedule[room].append((day, time_slot))

    # Validate teacher schedule
    for professor, times in teacher_schedule.items():
        times.sort()
        for i in range(1, len(times)):
            if times[i] == times[i - 1]:
                print(f"Conflict detected for Professor {professor} at {times[i]}")
                return False

    # Validate room schedule
    for room, times in room_schedule.items():
        times.sort()
        for i in range(1, len(times)):
            if times[i] == times[i - 1]:
                print(f"Conflict detected in Room {room} at {times[i]}")
                return False

    print("No conflicts detected. Schedule is valid.")
    return True

def load_schedule_from_csv(file_path):
    with open(file_path, 'r', newline='') as input_file:
        dict_reader = csv.DictReader(input_file)
        schedule = [row for row in dict_reader]
    return schedule

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate.py <path_to_schedule_csv>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    schedule = load_schedule_from_csv(file_path)
    if validate_schedule(schedule):
        print("The schedule is valid.")
    else:
        print("The schedule has conflicts.")
