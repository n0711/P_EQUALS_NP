"""Finite independent oracle tests for affine recognition and graph infrastructure."""
import itertools
import random
import unittest

from graph_research_instances import (clique_three_coloring,
    cubic_tseitin_3cnf, graph_profile, pigeonhole_3cnf)
from sat import verify
from structural_hybrid_sat import structural_hybrid_sat, try_affine_sat


def exhaustive(n, clauses):
    for assignment in itertools.product((False, True), repeat=n):
        if all(any(assignment[abs(lit) - 1] == (lit > 0)
                   for lit in clause) for clause in clauses):
            return assignment
    return None


def xor_clause_block(variables, parity):
    """All forbidden assignments produce the 2^(k-1) CNF clauses for XOR=parity."""
    result = []
    for values in itertools.product((0, 1), repeat=len(variables)):
        if sum(values) % 2 != parity:
            result.append(tuple(-v if bit else v
                                for v, bit in zip(variables, values)))
    return result


class StructuralHybridTests(unittest.TestCase):
    def check(self, n, clauses, expect=None):
        reference = exhaustive(n, clauses)
        model, stats = structural_hybrid_sat(n, clauses)
        self.assertEqual(stats["status"], "completed", stats)
        self.assertEqual(model is not None, reference is not None, (n, clauses, stats))
        if expect is not None:
            self.assertEqual(model is not None, expect)
        if model is not None:
            self.assertTrue(verify(n, clauses, model))
        return stats

    def test_one_two_three_variable_xor(self):
        for variables in ((1,), (1, 2), (1, 2, 3)):
            for parity in (0, 1):
                formula = xor_clause_block(variables, parity)
                recognized, model, _ = try_affine_sat(4, formula)
                self.assertTrue(recognized)
                self.assertIsNotNone(model)
                self.assertTrue(verify(4, formula, model))
                self.assertEqual(self.check(4, formula)["method"], "affine_gf2")

    def test_affine_linear_systems_with_conflicts(self):
        for n in (3, 5, 7):
            rng = random.Random(410 + n)
            for _ in range(40):
                clauses = []
                for _ in range(6):
                    variables = tuple(sorted(rng.sample(range(1, n + 1),
                                                        rng.randrange(1, min(n, 3) + 1))))
                    clauses.extend(xor_clause_block(variables, rng.randrange(2)))
                self.check(n, clauses)

    def test_non_affine_fallback(self):
        formula = [(1, 2, 3), (-1, -2, 3)]
        recognized, model, _ = try_affine_sat(3, formula)
        self.assertFalse(recognized)
        self.assertIsNone(model)
        self.assertEqual(self.check(3, formula)["method"], "graph_separator")
        for formula in ([()], [(1,), (-1,)], [], [(1,-1), (2,)]):
            self.check(3, formula)

    def test_random_cnf_independent_truth_tables(self):
        rng = random.Random(20261107)
        for n in range(8):
            literals = [lit for lit in range(-n, n + 1) if lit]
            for _ in range(80):
                formula = [tuple(rng.choice(literals) for _ in range(rng.randrange(4)))
                           for _ in range(rng.randrange(13))] if n else [()] * rng.randrange(2)
                self.check(n, formula)

    def test_cubic_tseitin_parity_and_connections(self):
        for vertices in (6, 8, 10, 12, 16):
            for parity in ("even", "odd"):
                n, formula = cubic_tseitin_3cnf(vertices, seed=123, charge=parity)
                self.assertEqual(n, 3 * vertices // 2)
                self.assertEqual(len(formula), 4 * vertices)
                profile = graph_profile(n, formula)
                self.assertEqual(profile["components"], 1)
                self.assertGreaterEqual(profile["min_fill_width_upper_bound"],
                                        profile["degeneracy_lower_bound"])
                recognized, model, stats = try_affine_sat(n, formula)
                self.assertTrue(recognized)
                self.assertEqual(stats["equations"], vertices)
                self.assertEqual(model is not None, parity == "even")
                if model is not None:
                    self.assertTrue(verify(n, formula, model))
                hybrid_model, hybrid_metrics = structural_hybrid_sat(n, formula)
                self.assertEqual(hybrid_metrics["method"], "affine_gf2")
                self.assertEqual(hybrid_model is not None, parity == "even")
                if vertices <= 8:
                    self.check(n, formula, expect=parity == "even")

    def test_pigeonhole_3cnf_unsat(self):
        for pigeons in (2, 3, 4, 5):
            n, clauses = pigeonhole_3cnf(pigeons)
            self.assertTrue(all(len(c) <= 3 for c in clauses))
            self.assertEqual(graph_profile(n, clauses)["components"], 1)
            if pigeons <= 4:
                self.check(n, clauses, expect=False)
            self.assertFalse(try_affine_sat(n, clauses)[0])

    def test_graph_coloring_sat_unsat(self):
        for vertices, expected in ((1, True), (2, True), (3, True), (4, False)):
            n, clauses = clique_three_coloring(vertices)
            self.check(n, clauses, expect=expected)

    def test_primal_graph_width_bound_on_clique(self):
        complete = graph_profile(4, [(1,2,3,4)])
        self.assertEqual(complete["degeneracy_lower_bound"], 3)
        self.assertEqual(complete["min_fill_width_upper_bound"], 3)
        self.assertEqual(complete["articulation_vertices"], 0)
        disjoint = graph_profile(6, [(1,2), (4,5)])
        self.assertEqual(disjoint["components"], 2)
        self.assertEqual(disjoint["min_fill_width_upper_bound"], 1)

    def test_metameric_clause_permutation_and_variable_renaming(self):
        rng = random.Random(7007)
        for n in (4, 5, 6, 7):
            for _ in range(30):
                original = [tuple(rng.choice((-1, 1)) * rng.randrange(1,n + 1)
                                  for _ in range(rng.randrange(4))) for _ in range(10)]
                permutation = list(range(1, n + 1))
                rng.shuffle(permutation)
                remapped = [tuple((1 if lit > 0 else -1) * permutation[abs(lit)-1]
                                  for lit in clause) for clause in original]
                rng.shuffle(remapped)
                a = structural_hybrid_sat(n, original)[0]
                b = structural_hybrid_sat(n, remapped)[0]
                self.assertEqual(a is not None, b is not None)
                if b is not None:
                    self.assertTrue(verify(n, remapped, b))

    def test_limited_graph_fallback_is_undecided(self):
        n, formula = clique_three_coloring(4)
        model, metrics = structural_hybrid_sat(n, formula, max_calls=1)
        self.assertEqual(metrics["method"], "graph_separator")
        self.assertEqual(metrics["status"], "limit_calls")
        self.assertIsNone(model)

    def test_bad_inputs_and_generator_parameters(self):
        with self.assertRaises(ValueError):
            try_affine_sat(2, [(3,)])
        with self.assertRaises(ValueError):
            cubic_tseitin_3cnf(7)
        with self.assertRaises(ValueError):
            cubic_tseitin_3cnf(8, charge="unknown")
        with self.assertRaises(ValueError):
            pigeonhole_3cnf(1)


if __name__ == "__main__":
    unittest.main()
