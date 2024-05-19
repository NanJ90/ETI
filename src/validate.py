import csv
import collections
import time
def load_schedule(file_path):
    schedule = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            schedule.append(row)
    return schedule

def find_conflicts(schedule):
    conflicts = {
        'professor_conflicts': collections.defaultdict(list),
        'room_conflicts': collections.defaultdict(list)
    }

    time_slot_format = collections.defaultdict(list)
    for entry in schedule:
        professor = entry['Professor']
        room = entry['Room']
        day = entry['Day']
        time_slot = entry['Time Slot']
        
        # Check for professor conflicts
        key = (professor, day, time_slot)
        if key in time_slot_format:
            conflicts['professor_conflicts'][key].append(entry)
        else:
            time_slot_format[key].append(entry)
        
        # Check for room conflicts
        key = (room, day, time_slot)
        if key in time_slot_format:
            conflicts['room_conflicts'][key].append(entry)
        else:
            time_slot_format[key].append(entry)

    return conflicts

def generate_report(conflicts, report_file):
    with open(report_file, 'w') as file:
        file.write("Schedule Conflict Report\n")
        file.write("========================\n\n")
        
        file.write("Professor Conflicts:\n")
        file.write("--------------------\n")
        for key, entries in conflicts['professor_conflicts'].items():
            file.write(f"Conflict for Professor {entries[0]['Professor']} at {key[1]} {key[2]}\n")
            for entry in entries:
                file.write(f"  Course: {entry['Course']}, Room: {entry['Room']}\n")
            file.write("\n")
        
        file.write("Room Conflicts:\n")
        file.write("----------------\n")
        for key, entries in conflicts['room_conflicts'].items():
            file.write(f"Conflict for Room {entries[0]['Room']} at {key[1]} {key[2]}\n")
            for entry in entries:
                file.write(f"  Professor: {entry['Professor']}, Course: {entry['Course']}\n")
            file.write("\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate.py <schedule_file>")
        sys.exit(1)

    schedule_file = sys.argv[1]
    report_file = f'conflicts_report_{time.strftime("%Y%m%d-%H%M%S")}.txt'

    schedule = load_schedule(schedule_file)
    conflicts = find_conflicts(schedule)
    generate_report(conflicts, report_file)

    print(f"Conflict report generated: {report_file}")
