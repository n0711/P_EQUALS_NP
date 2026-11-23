"""Finite independent tests for the M11 SAT zeta identity.

No test here establishes P=NP, P!=NP, RH, GRH, or a zeta evaluator.
"""
import itertools
import random
import unittest

from rh_grh_bridge import cnf_to_quadratic_system
from zeta_sat import (
    count_sat_bounded,
    local_zeta_coefficients,
    pole_order_at_one,
    symbolic_euler_exponent,
)


def gf4_mul(a, b):
    """Multiply in F_4 = F_2[u]/(u^2+u+1), elements encoded 0..3."""
    product_poly = 0
    for shift in range(2):
        if (b >> shift) & 1:
            product_poly ^= a << shift
    for degree in (3, 2):
        if (product_poly >> degree) & 1:
            product_poly ^= 0b111 << (degree - 2)
    return product_poly


def gf4_evaluate(poly, values):
    result = 0
    for monomial, coeff in poly.items():
        term = coeff & 1
        for variable in monomial:
            term = gf4_mul(term, values[variable - 1])
        result ^= term
    return result


def field_point_count(n, clauses, field):
    total, equations = cnf_to_quadratic_system(n, clauses)
    if field == 2:
        mul, add, scalar = lambda a, b: a * b % 2, lambda a, b: (a + b) % 2, lambda x: x % 2
    elif field == 4:
        mul, add, scalar = gf4_mul, lambda a, b: a ^ b, lambda x: x & 1
    else:
        raise ValueError("only 2 or 4 supported in independent oracle")
    def eval_poly(poly, values):
        result = 0
        for monomial, coeff in poly.items():
            term = scalar(coeff)
            for index in monomial:
                term = mul(term, values[index - 1])
            result = add(result, term)
        return result
    return sum(
        all(eval_poly(eq, values) == 0 for eq in equations)
        for values in itertools.product(range(field), repeat=total)
    )


def independent_count(n, clauses):
    result = 0
    for bits in itertools.product((False, True), repeat=n):
        if all(any(bits[abs(lit)-1] if lit > 0 else not bits[-lit-1]
                   for lit in clause) for clause in clauses):
            result += 1
    return result


class M11ZetaSATTests(unittest.TestCase):
    def test_known_counts_and_local_series(self):
        examples = [
            (0, [], 1),
            (0, [()], 0),
            (1, [(1,), (-1,)], 0),
            (1, [(1,)], 1),
            (2, [(1, 2)], 3),
            (2, [], 4),
            (2, [(1,), (-2,)], 1),
            (3, [(1, 2, 3)], 7),
        ]
        for n, clauses, expected in examples:
            with self.subTest(n=n, clauses=clauses):
                self.assertEqual(count_sat_bounded(n, clauses), expected)
                self.assertEqual(pole_order_at_one(expected), expected)
                self.assertEqual(symbolic_euler_exponent(expected), expected)
                a = local_zeta_coefficients(expected, 4)
                self.assertEqual(a[0], 1)
                self.assertEqual(a[1], expected)
                self.assertEqual(a[2], expected*(expected+1)//2)

    def test_point_counts_over_prime_and_extension_fields(self):
        # F4 genuinely contains elements beyond {0,1}; enumerate all of them.
        # Equality of both counts to #SAT supports the theorem on small cases.
        cases = [
            (0, []), (0, [()]), (1, []),
            (1, [(1,)]), (1, [(1,), (-1,)]),
            (1, [(1, -1)]), (2, [(1, 2)]),
            (2, [(1, -2), (-1, 2)]),
            (3, [(1, 2, 3)]),
            (3, [(1, 1, -1)]),
        ]
        for n, clauses in cases:
            with self.subTest(n=n, clauses=clauses):
                expected = independent_count(n, clauses)
                self.assertEqual(field_point_count(n, clauses, 2), expected)
                self.assertEqual(field_point_count(n, clauses, 4), expected)

    def test_independent_seeded_count_oracle(self):
        rng = random.Random(20261123)
        for n in range(7):
            literals = [lit for lit in range(-n, n + 1) if lit]
            for _ in range(60):
                formula = (
                    [tuple(rng.choice(literals) for _ in range(rng.randrange(5)))
                     for __ in range(rng.randrange(8))]
                    if n else [()] * rng.randrange(2)
                )
                count = independent_count(n, formula)
                self.assertEqual(count_sat_bounded(n, formula), count)
                self.assertEqual(local_zeta_coefficients(count, 1)[1], count)

    def test_series_coefficients_closed_forms(self):
        self.assertEqual(local_zeta_coefficients(0, 5), (1, 0, 0, 0, 0, 0))
        self.assertEqual(local_zeta_coefficients(1, 5), (1, 1, 1, 1, 1, 1))
        self.assertEqual(local_zeta_coefficients(2, 5), (1, 2, 3, 4, 5, 6))
        self.assertEqual(local_zeta_coefficients(3, 4), (1, 3, 6, 10, 15))
        self.assertEqual(local_zeta_coefficients(5, 0), (1,))

    def test_explicit_exponential_bound_and_type_rejection(self):
        with self.assertRaises(ValueError):
            count_sat_bounded(17, [])
        with self.assertRaises(ValueError):
            count_sat_bounded(2, [], max_variables=1)
        for count in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                local_zeta_coefficients(count, 3)
        for degree in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                local_zeta_coefficients(1, degree)
        with self.assertRaises(ValueError):
            count_sat_bounded(0, [], max_variables=-1)
        with self.assertRaises(ValueError):
            pole_order_at_one(-1)
        with self.assertRaises(ValueError):
            symbolic_euler_exponent(True)


if __name__ == "__main__":
    unittest.main()
