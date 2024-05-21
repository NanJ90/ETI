# ETI: Intelligent Timetable Intelligence

Welcome to the ETI project repository! This project focuses on developing an intelligent system for automatic timetable generation using advanced heuristic algorithms, specifically Genetic Algorithms (GA) and Constraint Satisfaction Problem (CSP) techniques with Simulated Annealing (SA).

## Demo Video
Watch the [demo video](https://www.youtube.com/watch?v=bMu7USLMZ0E) to see ETI in action.

## Problem Description
The goal of this project is to create a system, named ETI, that generates optimal timetables by balancing various constraints and preferences.

### Key Features
- **Simulated Annealing (SA):** Used for initial solution estimates due to its ability to avoid local minima and explore a wide range of possible solutions. SA will be benchmarked against other methods such as backtracking, iterative refinement, and random start strategies.
- **Genetic Algorithms (GA):** Leveraged for their evolutionary approach, utilizing processes like crossover and mutation to achieve highly optimal outcomes.

### Timetable Constraints and Preferences
Creating an effective class schedule requires consideration of numerous requirements, including:

- **Professors:** Availability and schedule.
- **Students:** Class enrollment and schedule.
- **Classes:** Type and duration.
- **Classrooms:** Availability, capacity, and equipment.

These requirements can be categorized by their importance:

#### Hard Requirements (must be satisfied for a feasible schedule):
1. **Classroom Availability:** A class can only be scheduled in an available classroom.
2. **Conflict-Free Scheduling:** No professor or student group can have more than one class scheduled at the same time.
3. **Seating Capacity:** Classrooms must have sufficient seating to accommodate all students in the class.
4. **Equipment Availability:** Classrooms must be equipped with necessary laboratory equipment (e.g., computers) if required by the class.

By addressing these constraints and preferences, ETI aims to intelligently and efficiently generate timetables that meet all critical requirements while optimizing for various other factors.

## Getting Started
To get started with the ETI project, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/eti.git
   cd eti
