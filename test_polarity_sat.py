"""Finite oracle and metamorphic tests of M6 polarity/signature SAT portfolio."""
import itertools
import random
import unittest

from dense_cnf_families import (all_positive_triples,
                                all_signs_on_each_triple,
                                opposite_monotone_triples)
from graph_research_instances import graph_profile, cubic_tseitin_3cnf
from polarity_sat import polarity_hybrid_sat, preprocess_polarity
from sat import verify


def exhaustive(n, clauses):
    for values in itertools.product((False, True), repeat=n):
        if all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return values
    return None


class PolaritySATTests(unittest.TestCase):
    def check(self, n, clauses, **options):
        expected = exhaustive(n, clauses)
        model, stats = polarity_hybrid_sat(n, clauses, **options)
        self.assertEqual(stats["status"], "completed", (n, clauses, stats))
        self.assertEqual(model is not None, expected is not None,
                         (n, clauses, stats))
        if model is not None:
            self.assertTrue(verify(n, clauses, model))
        return stats

    def test_empty_tautological_and_conflict(self):
        for n, clauses in ((0, []), (0, [()]), (3, []),
                           (3, [(1, -1), (2,)]),
                           (2, [(1,), (-1,)]),
                           (3, [(1,2), (1,-2), (-1,2), (-1,-2)])):
            with self.subTest(n=n, clauses=clauses):
                self.check(n, clauses)

    def test_complete_primal_graph_easy_sat(self):
        for n in (3, 4, 6, 8, 10):
            N, clauses = all_positive_triples(n)
            model, stats = polarity_hybrid_sat(N, clauses)
            self.assertIsNotNone(model)
            self.assertEqual(stats["method"], "polarity_preprocess")
            self.assertEqual(stats["preprocessing"]["pure_assignments"], n)
            self.assertEqual(graph_profile(n, clauses)["min_fill_width_upper_bound"],
                             n - 1)
            self.assertTrue(verify(n, clauses, model))

    def test_complete_signatures_detect_unsat(self):
        for n in (3, 4, 6, 8):
            N, clauses = all_signs_on_each_triple(n)
            model, stats = polarity_hybrid_sat(N, clauses)
            self.assertIsNone(model)
            self.assertEqual(stats["status"], "completed")
            self.assertEqual(stats["preprocessing"]["complete_support_contradictions"], 1)
            self.assertEqual(stats["preprocessing"]["pure_assignments"], 0)
            self.assertEqual(graph_profile(n, clauses)["degeneracy_lower_bound"],
                             n - 1)

    def test_equal_graph_different_sat_behavior(self):
        for n in (3, 4, 5, 6, 7):
            formulas = [all_positive_triples(n)[1],
                        all_signs_on_each_triple(n)[1],
                        opposite_monotone_triples(n)[1]]
            profiles = [graph_profile(n, f) for f in formulas]
            self.assertEqual([p["edges"] for p in profiles],
                             [n*(n-1)//2]*3)
            self.assertEqual([p["min_fill_width_upper_bound"] for p in profiles],
                             [n-1]*3)
            self.assertTrue(self.check(n, formulas[0])["method"] == "polarity_preprocess")
            self.check(n, formulas[1])
            self.check(n, formulas[2])

    def test_opposite_monotone_threshold(self):
        for n in range(3, 10):
            N, clauses = opposite_monotone_triples(n)
            model, stats = polarity_hybrid_sat(N, clauses)
            self.assertEqual(stats["status"], "completed")
            self.assertEqual(model is not None, n <= 4)
            if model is not None:
                self.assertTrue(verify(n, clauses, model))
            self.assertEqual(stats["preprocessing"]["pure_assignments"], 0)
            self.assertEqual(stats["preprocessing"]["complete_support_contradictions"], 0)

    def test_affine_path_remains_available(self):
        for charge in ("even", "odd"):
            n, clauses = cubic_tseitin_3cnf(8, seed=41, charge=charge)
            model, stats = polarity_hybrid_sat(n, clauses)
            self.assertEqual(stats["method"], "polarity_then_affine_gf2")
            self.assertEqual(model is not None, charge == "even")

    def test_preprocess_preserves_residual_extensions(self):
        # x1 is pure positive; x2 is forced true, x3 is unconstrained.
        n, formula = 4, [(1, 2), (1, -2), (2,), (4, -4)]
        state, residual, partial, metrics = preprocess_polarity(n, formula)
        self.assertEqual(state, "SAT")
        self.assertTrue(partial[2])
        for unused in (False, True):
            full = [partial.get(v, unused) for v in range(1, n + 1)]
            self.assertTrue(verify(n, formula, full))

    def test_random_truth_table_oracle(self):
        rng = random.Random(20261107)
        for n in range(9):
            lits = [i for i in range(-n, n+1) if i]
            for _ in range(90):
                formula = ([tuple(rng.choice(lits) for _ in range(rng.randrange(5)))
                            for __ in range(rng.randrange(14))]
                           if n else [()] * rng.randrange(3))
                self.check(n, formula)

    def test_signed_variable_renaming(self):
        rng = random.Random(6007)
        for n in range(1, 8):
            lits = [i for i in range(-n, n+1) if i]
            for _ in range(30):
                formula = [tuple(rng.choice(lits) for __ in range(rng.randrange(1,4)))
                           for __ in range(rng.randrange(9))]
                mapping = list(range(1,n+1))
                rng.shuffle(mapping)
                flips = [rng.choice((-1,1)) for _ in range(n)]
                renamed = [
                    tuple((1 if lit > 0 else -1)*mapping[abs(lit)-1]*flips[abs(lit)-1]
                          for lit in clause) for clause in formula
                ]
                left = polarity_hybrid_sat(n, formula)[0]
                right = polarity_hybrid_sat(n, renamed)[0]
                self.assertEqual(left is not None, right is not None)
                if right is not None:
                    self.assertTrue(verify(n, renamed, right))

    def test_limit_not_unsat(self):
        n, clauses = opposite_monotone_triples(6)
        model, stats = polarity_hybrid_sat(n, clauses, max_calls=1)
        self.assertIsNone(model)
        self.assertEqual(stats["status"], "limit_calls")

    def test_bad_literals_and_parameters(self):
        for n, clauses in ((-1, []), (3, [(0,)]), (3, [(4,)])):
            with self.assertRaises(ValueError):
                polarity_hybrid_sat(n, clauses)
        with self.assertRaises(ValueError):
            preprocess_polarity(3, [], max_signature_width=-1)
        with self.assertRaises(ValueError):
            all_positive_triples(2)


if __name__ == "__main__":
    unittest.main()
