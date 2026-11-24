"""M15 independently validate Bellman-Ford Boolean difference constraints.

These tests compare SAT/UNSAT with a separate exhaustive Boolean oracle
and with the pre-existing 2-SAT implication/SCC implementation. Every
UNSAT outcome must supply an explicit negative-weight cycle certificate.
"""
import itertools
import random
import unittest

from bellman_ford_boolean_sat import bellman_ford_boolean_sat
from sat import two_sat, verify
from structural_hybrid_sat import structural_hybrid_sat


def exhaustive_model(n, clauses):
    for bits in itertools.product((False, True), repeat=n):
        if all(any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return list(bits)
    return None


def assert_negative_cycle(test_case, cycle, node_count):
    test_case.assertTrue(cycle, "UNSAT needs an actual negative cycle")
    test_case.assertTrue(all(isinstance(edge, tuple) and len(edge) == 3
                             for edge in cycle))
    test_case.assertTrue(all(0 <= u < node_count and 0 <= v < node_count
                             for u, v, _ in cycle))
    test_case.assertTrue(all(left[1] == right[0] for left, right in
                             zip(cycle, cycle[1:] + cycle[:1])))
    test_case.assertLess(sum(edge[2] for edge in cycle), 0)


class BellmanFordBooleanSATTests(unittest.TestCase):
    def check(self, n, clauses):
        result = bellman_ford_boolean_sat(n, clauses)
        self.assertIn(result["status"], ("sat", "unsat"))
        reference = exhaustive_model(n, clauses)
        self.assertEqual(result["status"] == "sat", reference is not None,
                         (n, clauses, result))
        # The SCC solver accepts only syntactic 2-CNF; the Bellman
        # parser correctly discards tautologies even if they are wide.
        if all(len(clause) <= 2 for clause in clauses):
            scc_witness = two_sat(n, clauses)
            self.assertEqual(scc_witness is not None, reference is not None)
        if result["status"] == "sat":
            self.assertIsNone(result["negative_cycle"])
            self.assertTrue(verify(n, clauses, result["model"]))
        else:
            self.assertIsNone(result["model"])
            assert_negative_cycle(self, result["negative_cycle"], n + 1)
        self.assertLessEqual(result["metrics"]["passes"], n + 1)
        return result

    def test_empty_formula_and_empty_clause(self):
        self.assertEqual(self.check(0, [])["model"], [])
        self.assertEqual(self.check(0, [()])["status"], "unsat")
        self.assertEqual(self.check(5, [])["model"], [False] * 5)
        self.assertEqual(self.check(4, [(), (1, -1)])["status"], "unsat")

    def test_forced_values_and_duplicates(self):
        self.assertEqual(self.check(4, [(1,), (-2,), (3, 3), (-4, -4)])
                         ["model"], [True, False, True, False])
        self.assertEqual(self.check(3, [(1,), (1, 1), (-2,), (3, -3)])
                         ["status"], "sat")
        self.assertEqual(self.check(3, [(1,), (-1,)])["status"], "unsat")
        self.assertEqual(self.check(3, [(-2,), (2,), (-3,)])["status"], "unsat")

    def test_implication_chains_and_cycle_certificates(self):
        clauses = [(1,), (-1, 2), (-2, 3), (-3, 4), (-4,)]
        self.assertEqual(self.check(4, clauses)["status"], "unsat")
        self.assertEqual(self.check(4, clauses[:-1])["status"], "sat")
        self.assertEqual(self.check(5, [(-1, 2), (-2, 3), (-3, 4)])
                         ["status"], "sat")

    def test_tautological_wide_clause_discarded(self):
        self.check(4, [(1, -1, 2, 3, 4), (-2, 3), (-3, 4), (2,)])
        self.check(2, [(1, -1, 2), (1,), (-1,)])
        self.check(2, [(2, -2, 2), (1, -1)])

    def test_unsupported_clauses_never_decided(self):
        for n, clauses in (
            (2, [(1, 2)]),
            (2, [(-1, -2)]),
            (3, [(1, 2, 3)]),
            (3, [(1,), (-1,), (2, 3)]),
            (4, [(-1, 2), (3, 4)]),
        ):
            result = bellman_ford_boolean_sat(n, clauses)
            self.assertEqual(result["status"], "unrecognized")
            self.assertIsNone(result["model"])
            self.assertIsNone(result["negative_cycle"])

    def test_seeded_random_implications_against_independent_oracles(self):
        rng = random.Random(20261124)
        for n in range(0, 9):
            for _ in range(70):
                clauses = []
                for _ in range(rng.randrange(12)):
                    if n == 0:
                        clauses.append(())
                    elif rng.randrange(4) == 0:
                        variable = rng.randrange(1, n + 1)
                        clauses.append((variable if rng.randrange(2) else -variable,))
                    elif n > 1:
                        a, b = rng.sample(range(1, n + 1), 2)
                        clause = (-a, b)
                        if rng.randrange(2):
                            clause = (b, -a)
                        clauses.append(clause)
                    else:
                        clauses.append((1, -1))
                self.check(n, clauses)

    def test_random_variable_permutations_preserve_sat(self):
        rng = random.Random(14411)
        for n in range(2, 8):
            for _ in range(35):
                clauses = []
                for _ in range(10):
                    a, b = rng.sample(range(1, n + 1), 2)
                    clauses.append((-a, b))
                clauses.append((rng.randrange(1, n + 1),))
                perm = list(range(1, n + 1))
                rng.shuffle(perm)
                reordered = [tuple((1 if v > 0 else -1) * perm[abs(v)-1]
                                   for v in clause) for clause in clauses]
                rng.shuffle(reordered)
                self.assertEqual(self.check(n, clauses)["status"],
                                 self.check(n, reordered)["status"])

    def test_large_implication_chain_with_forced_contradiction(self):
        n = 350
        chain = [(-i, i + 1) for i in range(1, n)]
        sat = bellman_ford_boolean_sat(n, chain + [(1,)])
        self.assertEqual(sat["status"], "sat")
        self.assertTrue(all(sat["model"]))
        unsat = bellman_ford_boolean_sat(n, chain + [(1,), (-n,)])
        self.assertEqual(unsat["status"], "unsat")
        assert_negative_cycle(self, unsat["negative_cycle"], n + 1)

    def test_multiple_disconnected_implication_components(self):
        clauses = [(1,), (-1, 2), (-3, 4), (-4, 3), (-5,), (-5, 6)]
        result = self.check(7, clauses)
        self.assertTrue(result["model"][0])
        self.assertTrue(result["model"][1])
        self.assertFalse(result["model"][4])

    def test_portfolio_uses_bellman_ford_after_affine_rejection(self):
        sat_formula = [(1,), (-1, 2), (-2, 3)]
        model, metrics = structural_hybrid_sat(3, sat_formula)
        self.assertEqual(metrics["status"], "completed")
        self.assertEqual(metrics["method"], "bellman_ford_difference")
        self.assertTrue(verify(3, sat_formula, model))
        self.assertIsNone(metrics["negative_cycle"])

        unsat_formula = sat_formula + [(-3,)]
        model, metrics = structural_hybrid_sat(3, unsat_formula)
        self.assertEqual(metrics["status"], "completed")
        self.assertEqual(metrics["method"], "bellman_ford_difference")
        self.assertIsNone(model)
        assert_negative_cycle(self, metrics["negative_cycle"], 4)

        # Unsupported positive disjunction remains with the exact fallback.
        model, metrics = structural_hybrid_sat(3, [(1, 2, 3)])
        self.assertEqual(metrics["status"], "completed")
        self.assertNotEqual(metrics["method"], "bellman_ford_difference")
        self.assertTrue(verify(3, [(1, 2, 3)], model))

    def test_exact_input_validation(self):
        for n, clauses in ((-1, []), (True, []), (1.5, []),
                           (2, [(0,)]), (2, [(3,)]), (2, [(True,)]),
                           (2, [(-3,)]), (2, [(1.0,)])):
            with self.subTest(n=n, clauses=clauses):
                with self.assertRaises(ValueError):
                    bellman_ford_boolean_sat(n, clauses)

    def test_failure_to_count_models_is_explicit(self):
        # Both formulas are SAT, yet their model counts differ.
        a = bellman_ford_boolean_sat(2, [])
        b = bellman_ford_boolean_sat(2, [(-1, 2)])
        self.assertEqual(a["status"], "sat")
        self.assertEqual(b["status"], "sat")
        self.assertEqual(sum(1 for bits in itertools.product((False, True),
                             repeat=2) if True), 4)
        self.assertEqual(sum(1 for bits in itertools.product((False, True),
                             repeat=2) if not bits[0] or bits[1]), 3)
        self.assertNotIn("model_count", a)
        self.assertNotIn("model_count", b)


if __name__ == "__main__":
    unittest.main()
