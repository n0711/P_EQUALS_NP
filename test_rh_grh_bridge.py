"""Independent finite-oracle tests for the unconditional CNF -> HN bridge.

Finite tests support implementation correctness only, not P=NP or GRH.
"""
import itertools
import random
import unittest

from rh_grh_bridge import (
    cnf_to_quadratic_system,
    evaluate_equation,
    is_common_zero,
    lift_boolean_assignment,
)


def sat_oracle(n, clauses):
    for bits in itertools.product((0, 1), repeat=n):
        if all(any(bits[abs(lit) - 1] == int(lit > 0) for lit in clause)
               for clause in clauses):
            return bits
    return None


class RHGRHBridgeTests(unittest.TestCase):
    def check_all_boolean_points(self, n, clauses):
        count, equations = cnf_to_quadratic_system(n, clauses)
        self.assertTrue(all(max((len(term) for term in eq), default=0) <= 2
                            for eq in equations))
        for bits in itertools.product((0, 1), repeat=n):
            lifted = lift_boolean_assignment(n, clauses, bits)
            self.assertEqual(len(lifted), count)
            actual = is_common_zero(equations, lifted)
            expected = all(any(bits[abs(lit) - 1] == int(lit > 0)
                               for lit in clause) for clause in clauses)
            self.assertEqual(actual, expected, (n, clauses, bits))
        self.assertEqual(sat_oracle(n, clauses) is not None,
                         any(is_common_zero(
                             equations, lift_boolean_assignment(n, clauses, bits))
                             for bits in itertools.product((0, 1), repeat=n)))

    def test_edge_cases(self):
        cases = [
            (0, []),
            (0, [()]),
            (1, [(1,)]),
            (1, [(-1,)]),
            (1, [(1,), (-1,)]),
            (1, [(1, -1)]),
            (1, [(1, 1, 1)]),
            (2, [(1, 2), (-1, 2)]),
            (2, [(1, -2, 2)]),
            (3, [(1, 2, 3), (-1, -2), (3,)]),
        ]
        for n, clauses in cases:
            with self.subTest(n=n, clauses=clauses):
                self.check_all_boolean_points(n, clauses)

    def test_finite_field_full_grid(self):
        # Enumerate EVERY field assignment (including non-Boolean points).
        # Characteristic 2, 3 and 5; bounded small examples only.
        examples = [
            (0, []),
            (0, [()]),
            (1, [(1,)]),
            (1, [(1,), (-1,)]),
            (1, [(1, -1)]),
            (1, [(1, 1, 1)]),
            (2, [(1, 2), (-1, 2)]),
            (2, [(1, -2, 2)]),
        ]
        for p in (2, 3, 5):
            for n, clauses in examples:
                with self.subTest(p=p, n=n, clauses=clauses):
                    count, equations = cnf_to_quadratic_system(n, clauses)
                    has_root = any(
                        is_common_zero(equations, values, modulus=p)
                        for values in itertools.product(range(p), repeat=count)
                    )
                    self.assertEqual(has_root, sat_oracle(n, clauses) is not None)

    def test_seeded_random_boolean_oracle(self):
        rng = random.Random(20261123)
        for n in range(6):
            literals = [lit for lit in range(-n, n + 1) if lit]
            for _ in range(80):
                if n:
                    clauses = [
                        tuple(rng.choice(literals)
                              for __ in range(rng.randrange(6)))
                        for ___ in range(rng.randrange(8))
                    ]
                else:
                    clauses = [()] * rng.randrange(3)
                self.check_all_boolean_points(n, clauses)

    def test_long_clause_stays_quadratic_and_linear_sized(self):
        n = 60
        total, equations = cnf_to_quadratic_system(n, [tuple(range(1, n + 1))])
        self.assertEqual(total, 2*n - 2)
        self.assertEqual(len(equations), 3*n - 3)
        self.assertLessEqual(max(len(eq) for eq in equations), 4)
        self.assertLessEqual(max(len(monomial) for eq in equations
                                 for monomial in eq), 2)
        all_true = lift_boolean_assignment(n, [tuple(range(1, n + 1))],
                                           [1]*n)
        self.assertTrue(is_common_zero(equations, all_true))
        all_false = lift_boolean_assignment(n, [tuple(range(1, n + 1))],
                                            [0]*n)
        self.assertFalse(is_common_zero(equations, all_false))

    def test_input_validation(self):
        for n, clauses in ((-1, []), (True, []), (2, [(0,)]),
                           (2, [(3,)]), (2, [(1.5,)])):
            with self.assertRaises(ValueError):
                cnf_to_quadratic_system(n, clauses)
        with self.assertRaises(ValueError):
            lift_boolean_assignment(2, [(1,)], [0])
        with self.assertRaises(ValueError):
            lift_boolean_assignment(2, [(1,)], [0, 2])
        with self.assertRaises(ValueError):
            evaluate_equation({(): 1}, [], modulus=1)


if __name__ == "__main__":
    unittest.main()
