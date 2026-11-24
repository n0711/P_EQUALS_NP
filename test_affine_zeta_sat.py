"""M12 independent counting oracles: complete affine CNF and zeta coefficients.

Do not infer a general polynomial-time #SAT algorithm from these tests.
"""
import itertools
import random
import unittest

from affine_zeta_sat import affine_zeta_profile
from graph_research_instances import cubic_tseitin_3cnf
from sat import verify


def independent_model_count(n, clauses):
    return sum(
        all(any(bits[abs(lit) - 1] == (lit > 0)
                for lit in clause) for clause in clauses)
        for bits in itertools.product((False, True), repeat=n)
    )


def block(variables, rhs):
    """Construct all forbidden parity patterns by independent truth tables."""
    clauses = []
    for bits in itertools.product((0, 1), repeat=len(variables)):
        if sum(bits) % 2 != rhs:
            clauses.append(tuple(-variable if value else variable
                                 for variable, value in zip(variables, bits)))
    return clauses


class M12AffineZetaTests(unittest.TestCase):
    def assert_counted(self, n, clauses, expected=None):
        result = affine_zeta_profile(n, clauses, local_degree=4)
        self.assertEqual(result["status"], "counted", (n, clauses, result))
        oracle = independent_model_count(n, clauses)
        self.assertEqual(result["model_count"], oracle, (n, clauses, result))
        if expected is not None:
            self.assertEqual(result["model_count"], expected)
        count = result["model_count"]
        self.assertEqual(result["local_coefficients"][0], 1)
        self.assertEqual(result["local_coefficients"][1], count)
        self.assertEqual(result["local_coefficients"][2], count*(count+1)//2)
        witness = result["witness"]
        if count:
            self.assertIsNotNone(witness)
            self.assertEqual(len(witness), n)
            self.assertTrue(verify(n, clauses, witness))
            self.assertEqual(count, 1 << result["free_variables"])
            self.assertEqual(result["free_variables"] + result["rank"], n)
        else:
            self.assertIsNone(witness)
            self.assertIsNone(result["free_variables"])
        return result

    def test_empty_unit_and_tautological(self):
        self.assert_counted(0, [], 1)
        self.assert_counted(0, [()], 0)
        self.assert_counted(4, [], 16)
        self.assert_counted(4, [(1, -1), (2, -2)], 16)
        self.assert_counted(4, [(1, 1), (2, -2)], 8)
        self.assert_counted(4, [(-2,), (-2,), (3, -3)], 8)

    def test_exact_xor_rank_and_free_variables(self):
        n = 7
        clauses = block((1, 2, 3), 1) + block((2, 3, 4), 0)
        clauses += block((1, 4), 1)  # dependent equation
        result = self.assert_counted(n, clauses, 1 << (n - 2))
        self.assertEqual(result["rank"], 2)
        self.assertEqual(result["free_variables"], 5)

    def test_unique_support_inconsistent_affine_system(self):
        # x1=0, x2=0, x1 XOR x2=1; no repeated-support mixed parity.
        clauses = block((1,), 0) + block((2,), 0) + block((1, 2), 1)
        result = self.assert_counted(5, clauses, 0)
        self.assertEqual(result["local_coefficients"], (1, 0, 0, 0, 0))

    def test_tseitin_connected_graph_counts(self):
        for vertices in (6, 8, 10):
            for parity in ("even", "odd"):
                n, clauses = cubic_tseitin_3cnf(vertices, seed=27,
                                                 charge=parity)
                expected = 1 << (n - vertices + 1) if parity == "even" else 0
                result = self.assert_counted(n, clauses, expected)
                if parity == "even":
                    self.assertEqual(result["rank"], vertices - 1)

    def test_seeded_random_unique_supports(self):
        rng = random.Random(20261123)
        for n in range(1, 9):
            possibilities = [group for width in range(1, min(n, 3) + 1)
                             for group in itertools.combinations(range(1, n + 1), width)]
            for _ in range(55):
                choices = rng.sample(possibilities,
                                     min(len(possibilities), rng.randrange(9)))
                clauses = []
                for variables in choices:
                    clauses.extend(block(variables, rng.randrange(2)))
                rng.shuffle(clauses)
                self.assert_counted(n, clauses)

    def test_signed_variable_bijection_and_duplicate_blocks(self):
        rng = random.Random(8093)
        for n in range(3, 8):
            for _ in range(25):
                variables = rng.sample(range(1, n + 1), 3)
                clauses = block(variables, rng.randrange(2))
                clauses += block((variables[0],), rng.randrange(2))
                perm = list(range(1, n + 1))
                rng.shuffle(perm)
                flip = [rng.choice((-1, 1)) for _ in range(n)]
                modified = [
                    tuple((1 if lit > 0 else -1) *
                          perm[abs(lit) - 1] * flip[abs(lit) - 1]
                          for lit in clause)
                    for clause in clauses
                ]
                modified.extend(modified[:2])  # duplications do not change SAT
                self.assertEqual(independent_model_count(n, clauses),
                                 affine_zeta_profile(n, modified)["model_count"])

    def test_unsupported_is_not_unsat(self):
        for n, clauses in (
            (3, [(1, 2, 3)]),
            (4, [(1, 2, 3, 4)]),
            (3, [(1,), (-1,)]),  # contradictory, but grammar is rejected
            (3, [(1, 2, 3), (-1, -2, 3)]),
        ):
            result = affine_zeta_profile(n, clauses)
            self.assertEqual(result["status"], "unrecognized")
            self.assertIsNone(result["model_count"])
            self.assertIsNone(result["local_coefficients"])
            self.assertIsNone(result["witness"])

    def test_large_polynomial_subclass_no_brute_force(self):
        n = 200
        clauses = []
        for variable in range(1, n):
            clauses.extend(block((variable, variable + 1), 0))
        result = affine_zeta_profile(n, clauses)
        self.assertEqual(result["status"], "counted")
        self.assertEqual(result["rank"], n - 1)
        self.assertEqual(result["model_count"], 2)
        self.assertEqual(result["local_coefficients"], (1, 2, 3, 4))
        # All free variables are included in the result (written n+1 bits).
        unrestrained = affine_zeta_profile(1000, [], local_degree=2)
        self.assertEqual(unrestrained["model_count"].bit_length(), 1001)
        self.assertEqual(unrestrained["rank"], 0)

    def test_degree_and_literal_validation(self):
        for degree in (-1, True, 0.5):
            with self.assertRaises(ValueError):
                affine_zeta_profile(3, [], local_degree=degree)
        for n, clauses in ((True, []), (-1, []), (3, [(4,)]),
                           (3, [(0,)])):
            with self.assertRaises(ValueError):
                affine_zeta_profile(n, clauses)


if __name__ == "__main__":
    unittest.main()
