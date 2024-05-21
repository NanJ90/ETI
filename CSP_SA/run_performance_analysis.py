import csv
from scheduler import run_schedule

def analyze_performance(runs=5):
    total_execution_time = 0
    total_conflicts = 0
    success_count = 0

    for _ in range(runs):
        execution_time, success, conflicts, method_used = run_schedule()
        total_execution_time += execution_time
        total_conflicts += conflicts
        if success:
            success_count += 1

        with open('evaluation_report.csv', 'a', newline='') as csvfile:
            fieldnames = ['Execution Time (s)', 'Success', 'Conflicts', 'Method Used']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'Execution Time (s)': execution_time,
                'Success': success,
                'Conflicts': conflicts,
                'Method Used': method_used
            })

    average_execution_time = total_execution_time / runs
    average_conflicts = total_conflicts / runs
    success_rate = success_count / runs

    print(f'Average Execution Time: {average_execution_time:.2f} seconds')
    print(f'Average Conflicts: {average_conflicts:.2f}')
    print(f'Success Rate: {success_rate * 100:.2f}%')

if __name__ == "__main__":
    analyze_performance()
