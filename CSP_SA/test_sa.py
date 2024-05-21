# test_simulated_annealing.py
import unittest
from Configuration import load_config
from simulated_annealing import simulated_annealing, objective_function

class TestSimulatedAnnealing(unittest.TestCase):

    def setUp(self):
        # Load configuration
        self.config = load_config('../configuration files/data.cfg')
        self.initial_temperature = float(self.config['SimulatedAnnealing']['initial_temperature'])
        self.cooling_rate = float(self.config['SimulatedAnnealing']['cooling_rate'])
        self.stopping_temperature = 0.1  # Assuming default stopping temperature
        self.initial_solution = 50  # Assuming default initial solution
        self.iteration_limit = int(self.config['SimulatedAnnealing']['iteration_limit'])

    def test_config_loading(self):
        self.assertIn('SimulatedAnnealing', self.config)
        self.assertEqual(self.initial_temperature, 1000)
        self.assertEqual(self.cooling_rate, 0.95)
        self.assertEqual(self.iteration_limit, 1000)

    def test_simulated_annealing(self):
        best_solution, best_value = simulated_annealing(
            objective_function,
            self.initial_solution,
            self.initial_temperature,
            self.cooling_rate,
            self.iteration_limit
        )
        self.assertIsNotNone(best_solution)
        self.assertIsNotNone(best_value)

if __name__ == "__main__":
    unittest.main()
