"""Reproducible oracle checks for benchmark variants."""
import itertools
import random
import unittest
from sat import verify
from sat_benchmark import solve_counted

class BenchmarkTests(unittest.TestCase):
    def test_oracle(self):
        rng = random.Random(20261031)
        for n in range(0, 7):
            literals = [x for x in range(-n, n + 1) if x]
            for _ in range(150):
                clauses = [tuple(rng.choice(literals)
                                 for _ in range(rng.randrange(4)))
                           for _ in range(rng.randrange(12))] if n else [()] if rng.randrange(2) else []
                expected = any(verify(n, clauses, a)
                               for a in itertools.product((False, True), repeat=n))
                for strategy in ("first", "occurrence"):
                    result, stats = solve_counted(n, clauses, strategy)
                    self.assertEqual(result is not None, expected, (n, clauses, strategy))
                    if result is not None:
                        self.assertTrue(verify(n, clauses, result))
                    self.assertGreaterEqual(stats["calls"], 1)

    def test_deterministic(self):
        formula = [(1, 2, -3), (-1, 3), (2, -3)]
        for strategy in ("first", "occurrence"):
            self.assertEqual(solve_counted(3, formula, strategy),
                             solve_counted(3, formula, strategy))

    def test_unknown_strategy(self):
        with self.assertRaises(ValueError):
            solve_counted(2, [], "neural")

if __name__ == "__main__":
    unittest.main()
