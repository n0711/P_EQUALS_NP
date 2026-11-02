"""Exact-count regression checks; timings are intentionally not asserted."""
import unittest
from residual_state_benchmark import measure

class ResidualStateBenchmarkTests(unittest.TestCase):
    def test_exact_counts(self):
        for k in (0, 1, 4, 8, 12):
            row = measure(k)
            self.assertEqual(row["unique"], 1 << k)
            self.assertEqual(row["expected"], row["unique"])

    def test_resource_guard(self):
        with self.assertRaises(ValueError):
            measure(21)

if __name__ == "__main__":
    unittest.main()
