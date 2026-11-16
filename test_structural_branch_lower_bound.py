"""Regression witness for the structural hybrid's deterministic fallback."""
import random
import unittest
from itertools import combinations

from graph_separator_sat import _canonical, _graph, _restrict, _separator, graph_separator_sat
from sat import verify
from polarity_sat import preprocess_polarity
from structural_hybrid_sat import structural_hybrid_sat, try_affine_sat


def branch_family(k, *, odd_cycle=False):
    """Build an unsatisfiable 3-CNF with k pivot variables and 8k ring variables."""
    if k < 1:
        raise ValueError("k must be positive")
    ring = list(range(k + 1, 9 * k + 1))
    clauses = set()

    def add_opposites(variables):
        clauses.add(tuple(sorted(variables)))
        clauses.add(tuple(-v for v in sorted(variables)))

    for i, a in enumerate(ring):
        add_opposites((a, ring[(i + 1) % len(ring)], ring[(i + 2) % len(ring)]))
    if odd_cycle:
        for pair in combinations(ring[:3], 2):
            add_opposites(pair)
    else:
        for triple in combinations(ring[:5], 3):
            add_opposites(triple)
    for i in range(k):
        for a, b in combinations(ring[8*i:8*i + 8], 2):
            add_opposites((i + 1, a, b))
    return 9 * k, sorted(clauses)


class StructuralBranchLowerBound(unittest.TestCase):
    def test_prefix_states(self):
        for k in range(1, 5):
            n, clauses = branch_family(k)
            self.assertFalse(try_affine_sat(n, clauses)[0])
            self.assertEqual(preprocess_polarity(n, clauses)[0], "RESIDUAL")
            states = {_canonical(clauses)}
            for pivot in range(1, k + 1):
                children = set()
                for state in states:
                    self.assertTrue(all(len(c) >= 2 for c in state))
                    self.assertFalse(_separator(_graph(state), 2, n))
                    children.update(_restrict(state, {pivot: v}) for v in (False, True))
                states = children
                self.assertEqual(len(states), 2 ** pivot)

    def test_original_fallback_visits(self):
        for k in range(1, 5):
            n, clauses = branch_family(k)
            model, metrics = graph_separator_sat(n, clauses)
            self.assertIsNone(model)
            self.assertEqual(metrics["status"], "completed")
            self.assertGreaterEqual(metrics["fallback_branches"], 2 ** k - 1)
            self.assertGreaterEqual(metrics["calls"], 2 ** (k + 1) - 1)

    def test_signed_renamings_detected_before_search(self):
        rng = random.Random(1611)
        for k in (1, 2, 5, 20):
            n, clauses = branch_family(k)
            for _ in range(8):
                names = [i * rng.choice((-1, 1)) for i in range(1, n + 1)]
                rng.shuffle(names)
                renamed = [tuple(names[abs(v)-1] * (1 if v > 0 else -1)
                                 for v in reversed(c)) for c in clauses]
                rng.shuffle(renamed)
                model, stats = structural_hybrid_sat(n, iter(renamed), max_calls=1)
                self.assertIsNone(model)
                self.assertEqual(stats["method"], "five_literal_core")
                witness = stats["core"]
                self.assertEqual(len({abs(v) for v in witness}), 5)
                actual = set(map(frozenset, renamed))
                for triple in combinations(witness, 3):
                    self.assertIn(frozenset(triple), actual)
                    self.assertIn(frozenset(-v for v in triple), actual)

    def test_every_single_clause_deletion_is_sat(self):
        clauses = [tuple(sign * v for v in t)
                   for t in combinations(range(1, 6), 3) for sign in (-1, 1)]
        for i in range(len(clauses)):
            reduced = clauses[:i] + clauses[i+1:]
            model, stats = structural_hybrid_sat(5, (iter(c) for c in reduced))
            self.assertEqual(stats["method"], "graph_separator")
            self.assertIsNotNone(model)
            self.assertTrue(verify(5, reduced, model))

    def test_mixed_odd_cycle_detected_before_search(self):
        for k in range(1, 6):
            n, clauses = branch_family(k, odd_cycle=True)
            model, stats = structural_hybrid_sat(n, clauses, max_calls=1)
            self.assertIsNone(model)
            self.assertEqual(stats["status"], "completed")
            self.assertEqual(stats["method"], "binary_parity_conflict")

    def test_guarded_odd_cycle_still_branches(self):
        for k in range(1, 6):
            n, clauses = branch_family(k, odd_cycle=True)
            guarded = [c + (g,) for c in clauses if len(c) == 2
                       for g in (n + 1, -n - 1)]
            guarded.extend(c for c in clauses if len(c) == 3)
            model, stats = structural_hybrid_sat(n + 1, guarded)
            self.assertIsNone(model)
            self.assertEqual(stats["status"], "completed")
            self.assertEqual(stats["method"], "graph_separator")
            self.assertGreaterEqual(stats["graph"]["calls"], 2 ** (k + 1) - 1)
