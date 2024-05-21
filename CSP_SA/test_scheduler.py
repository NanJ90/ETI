import unittest
from scheduler import run_schedule, no_teacher_overlap, no_room_overlap

class TestScheduler(unittest.TestCase):
    def test_run_schedule(self):
        execution_time, success, conflicts, method_used = run_schedule()
        self.assertTrue(success, "The schedule generation did not succeed.")
        self.assertEqual(conflicts, 0, "There are conflicts in the generated schedule.")
        self.assertIn(method_used, ["Backtracking with Heuristics", "Backtracking with Relaxed Constraints", "Simulated Annealing"], "Unexpected method used for scheduling.")

    def test_no_teacher_overlap(self):
        assignment = {('t1', 'c1'): ('t1', 'c1', 'room1', 'Monday', 1)}
        self.assertTrue(no_teacher_overlap(('t1', 'c1', 'room1', 'Monday', 2), assignment), "Teacher overlap detected incorrectly.")

    def test_no_room_overlap(self):
        assignment = {('t1', 'c1'): ('t1', 'c1', 'room1', 'Monday', 1)}
        self.assertTrue(no_room_overlap(('t1', 'c1', 'room2', 'Monday', 1), assignment), "Room overlap detected incorrectly.")

if __name__ == '__main__':
    unittest.main()
