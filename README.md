
Demo video: https://www.youtube.com/watch?v=bMu7USLMZ0E

Problem Description:
The goal of this project is to develop an intelligent system that automatically generates timetables using heuristic
algorithms, specifically Genetic Algorithms (GA) and Constraint Satisfaction Problem (CSP) techniques with Simulated
Annealing (SA). This system, named ETI, will create optimal timetables by balancing various constraints and preferences.

Simulated Annealing (SA) will serve as a robust baseline for initial solution estimates due to its capability to avoid local
minima and efficiently explore a wide range of possible solutions. Comparatively, this algorithm will be benchmarked
against other methods such as backtracking, iterative refinement, and random start strategies to address the timetable CSP.

Genetic Algorithms (GA) will be employed for their strength in evolving solutions over iterations, leveraging processes
like crossover and mutation to achieve highly optimal outcomes.

Creating an effective class schedule requires consideration of numerous requirements, including but not limited to the
number of professors, students, classes, and classrooms, classroom capacities, and the presence of necessary laboratory
equipment. These requirements can be categorized by their importance:

Hard Requirements (must be satisfied for a feasible schedule):
1. A class can only be scheduled in an available classroom.
2. No professor or student group can have more than one class scheduled at the same time.
3. Classrooms must have sufficient seating to accommodate all students in the class.
4. Classrooms must be equipped with the necessary laboratory equipment (e.g., computers) if required by the class.

By addressing these constraints and preferences, ETI aims to intelligently and efficiently generate timetables that meet
all critical requirements while optimizing for various other factors.
