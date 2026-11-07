"""Independent finite oracle tests for exact incidence-component SAT method."""
import itertools
import random
import unittest

from component_sat import component_sat
from sat import dpll, verify


def oracle(n, clauses):
    for assignment in itertools.product((False, True), repeat=n):
        if all(any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return assignment
    return None


class ComponentSatTests(unittest.TestCase):
    def check(self, n, formula):
        expected = oracle(n, formula)
        actual, metrics = component_sat(n, formula)
        self.assertEqual(actual is not None, expected is not None, (n, formula, metrics))
        self.assertEqual((dpll(n, formula) is not None), (expected is not None))
        self.assertEqual(metrics["status"], "completed")
        if actual is not None:
            self.assertTrue(verify(n, formula, actual))
        return metrics

    def test_zero_variable_and_empty_clause(self):
        for n, formula in ((0, []), (0, [()]), (3, []), (3, [(1, -1)]),
                           (3, [(1, 1), (-1,)]), (2, [(1,), (-1,)])):
            self.check(n, formula)

    def test_disconnected_satisfiable_components(self):
        formula = [(1, 2), (-1, 2), (3,), (4, 5), (-4, 5), (6, -6)]
        m = self.check(7, formula)
        self.assertEqual(m["components"], 3)
        self.assertEqual(m["max_component_variables"], 2)
        self.assertEqual(m["dpll_calls"], 3)

    def test_disconnected_unsat_component(self):
        formula = [(1, 2), (3,), (-3,), (4, 5)]
        self.check(6, formula)
        self.assertIsNone(component_sat(6, formula)[0])

    def test_independent_random_oracle(self):
        rng = random.Random(20261107)
        for n in range(8):
            literals = [lit for lit in range(-n, n + 1) if lit]
            for _ in range(80):
                if n:
                    formula = [tuple(rng.choice(literals) for _ in range(rng.randrange(5)))
                               for _ in range(rng.randrange(13))]
                else:
                    formula = [()] * rng.randrange(3)
                self.check(n, formula)

    def test_variable_renaming_invariance(self):
        rng = random.Random(20261108)
        for n in range(1, 8):
            literals = [lit for lit in range(-n, n + 1) if lit]
            for _ in range(30):
                formula = [tuple(rng.choice(literals) for _ in range(rng.randrange(1, 5)))
                           for _ in range(10)]
                permutation = list(range(1, n + 1))
                rng.shuffle(permutation)
                renamed = [tuple((1 if lit > 0 else -1) * permutation[abs(lit) - 1]
                                 for lit in clause) for clause in formula]
                a = component_sat(n, formula)[0]
                b = component_sat(n, renamed)[0]
                self.assertEqual(a is not None, b is not None)
                if b is not None:
                    self.assertTrue(verify(n, renamed, b))

    def test_input_validation(self):
        for n, formula in ((-1, []), (2, [(0,)]), (2, [(3,)]), (0, [(1,)])):
            with self.assertRaises(ValueError):
                component_sat(n, formula)


if __name__ == "__main__":
    unittest.main()
