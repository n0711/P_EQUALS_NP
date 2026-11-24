"""M13 independent #SAT oracle and explicit rejection regressions.

This verifies a restricted cutset algorithm; it cannot prove P=NP.
"""
import itertools
import random
import unittest

from cutset_zeta_sat import cutset_zeta_profile


def brute_force_count(n, clauses):
    """Independent SAT oracle over all original variables."""
    result = 0
    for bits in itertools.product((False, True), repeat=n):
        if all(any(
            (bits[abs(lit)-1] if lit > 0 else not bits[-lit-1])
            for lit in clause
        ) for clause in clauses):
            result += 1
    return result


def guarded_petals(k):
    """Each guarded 3-OR clause is a non-affine residual component."""
    return 1 + 3*k, [
        (1, 2+3*i, 3+3*i, 4+3*i)
        for i in range(k)
    ]


def guarded_xor_chain(k, *, base=2):
    """k Boolean variables, k-1 XOR=1 edges guarded by separator 1."""
    clauses = []
    for i in range(base, base + k-1):
        clauses.extend(((1, i, i+1), (1, -i, -(i+1))))
    return clauses


class CutsetZetaTests(unittest.TestCase):
    def check(self, n, clauses, cutset):
        result = cutset_zeta_profile(n, clauses, cutset, local_degree=3)
        if result["status"] == "counted":
            expected = brute_force_count(n, clauses)
            self.assertEqual(result["model_count"], expected,
                             (n, clauses, cutset, result))
            count = result["model_count"]
            self.assertEqual(result["local_coefficients"],
                             (1, count, count*(count+1)//2,
                              count*(count+1)*(count+2)//6))
        else:
            self.assertEqual(result["status"], "unrecognized")
            self.assertIsNone(result["model_count"])
            self.assertIsNone(result["local_coefficients"])
        return result

    def test_empty_and_false_and_isolated_variables(self):
        self.assertEqual(self.check(0, [], [])["model_count"], 1)
        self.assertEqual(self.check(0, [()], [])["model_count"], 0)
        self.assertEqual(self.check(5, [], [])["model_count"], 32)
        self.assertEqual(self.check(4, [(1,)], [])["model_count"], 8)
        self.assertEqual(self.check(4, [(1,-1),(2,)], [])["model_count"], 8)

    def test_mixed_disconnected_non_affine_components(self):
        # (x1 or x2) gives 3 models, (x3 or x4 or x5) gives 7.
        result = self.check(5, [(1,2), (3,4,5)], [])
        self.assertEqual(result["model_count"], 21)
        self.assertGreaterEqual(result["metrics"]["enumerated_components"], 1)
        self.assertEqual(result["metrics"]["separator_variables"], 0)

    def test_guarded_petals_closed_form(self):
        for k in range(1, 5):
            n, clauses = guarded_petals(k)
            result = self.check(n, clauses, [1])
            self.assertEqual(result["model_count"], 2**(3*k)+7**k)
            self.assertEqual(result["metrics"]["branches_examined"], 2)
        n, clauses = guarded_petals(100)
        result = cutset_zeta_profile(n, clauses, [1], local_degree=2)
        self.assertEqual(result["status"], "counted")
        self.assertEqual(result["model_count"], 2**300 + 7**100)
        self.assertEqual(result["metrics"]["enumerated_components"], 100)
        self.assertEqual(result["local_coefficients"][1],
                         result["model_count"])

    def test_guarded_affine_large_component(self):
        for k in range(2, 6):
            clauses = guarded_xor_chain(k)
            result = self.check(k+1, clauses, [1])
            self.assertEqual(result["model_count"], 2**k+2)
            self.assertGreaterEqual(result["metrics"]["affine_components"], 1)
        k = 120
        result = cutset_zeta_profile(k+1, guarded_xor_chain(k), [1],
                                     local_degree=2)
        self.assertEqual(result["status"], "counted")
        self.assertEqual(result["model_count"], 2**k+2)
        self.assertEqual(result["metrics"]["affine_components"], 1)

    def test_affine_and_non_affine_mixed(self):
        petal_count = 4
        chain_count = 30
        n = 1 + 3*petal_count + chain_count
        _, petal_clauses = guarded_petals(petal_count)
        chain_clauses = guarded_xor_chain(chain_count,
                                          base=2+3*petal_count)
        result = cutset_zeta_profile(n, petal_clauses + chain_clauses, [1],
                                     local_degree=2)
        self.assertEqual(result["status"], "counted")
        self.assertEqual(result["model_count"],
                         2**(3*petal_count+chain_count) +
                         7**petal_count * 2)
        self.assertEqual(result["metrics"]["enumerated_components"],
                         petal_count)
        self.assertEqual(result["metrics"]["affine_components"], 1)

    def test_conditioned_branch_conflict_and_free_variables(self):
        # If s=false, the two clauses force both x and not x.
        result = self.check(4, [(1,2),(1,-2)], [1])
        self.assertEqual(result["model_count"], 8)
        self.assertEqual(result["metrics"]["contradictory_branches"], 0)
        self.assertEqual(self.check(3, [(1,), (-1,)], [1])["model_count"], 0)
        self.assertEqual(self.check(3, [(1,), (1,2)], [1])["model_count"], 4)

    def test_seeded_random_against_independent_truth_tables(self):
        rng = random.Random(20261123)
        counted, unrecognized = 0, 0
        for n in range(8):
            literals = [lit for lit in range(-n, n+1) if lit]
            for _ in range(90):
                clauses = ([tuple(rng.choice(literals)
                                  for __ in range(rng.randrange(5)))
                            for ___ in range(rng.randrange(9))]
                           if n else [()] * rng.randrange(3))
                proxy = max(2, n+len(clauses)+sum(len(c) for c in clauses))
                bound = proxy.bit_length()-1
                order = list(range(1,n+1))
                rng.shuffle(order)
                separator = order[:rng.randrange(min(n,bound)+1)]
                result = self.check(n, clauses, separator)
                if result["status"] == "counted":
                    counted += 1
                else:
                    unrecognized += 1
        self.assertGreater(counted, 250)
        self.assertGreaterEqual(unrecognized, 0)

    def test_non_affine_large_component_rejected(self):
        n = 25
        result = cutset_zeta_profile(n, [tuple(range(1,n+1))], [])
        self.assertEqual(result["status"], "unrecognized")
        self.assertIn("component", result["reason"])
        self.assertIsNone(result["model_count"])
        # A SAT branch is easy, but the other branch is too large;
        # no partial or guessed total count can be reported.
        result = cutset_zeta_profile(26,
                                     [(1,*tuple(range(2,27)))], [1])
        self.assertEqual(result["status"], "unrecognized")
        self.assertIsNone(result["local_coefficients"])

    def test_oversized_separator_rejected_before_enumeration(self):
        result = cutset_zeta_profile(12, [], range(1,10))
        self.assertEqual(result["status"], "unrecognized")
        self.assertIn("separator", result["reason"])
        self.assertEqual(result["metrics"]["branches_examined"], 0)

    def test_invalid_inputs(self):
        for n, clauses, cutset in (
            (-1, [], []),
            (True, [], []),
            (3, [(0,)], []),
            (3, [(4,)], []),
            (3, [], [0]),
            (3, [], [4]),
            (3, [], [True]),
            (3, [], [1,1]),
            (3, [], None),
        ):
            with self.subTest(n=n, clauses=clauses, cutset=cutset):
                with self.assertRaises(ValueError):
                    cutset_zeta_profile(n, clauses, cutset)
        for degree in (-1, True, 0.5):
            with self.assertRaises(ValueError):
                cutset_zeta_profile(3, [], [], local_degree=degree)


if __name__ == "__main__":
    unittest.main()
