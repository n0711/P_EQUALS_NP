"""Regression witness for the structural hybrid's deterministic fallback."""
import unittest
from itertools import combinations

from graph_separator_sat import _canonical, _graph, _restrict, _separator
from polarity_sat import preprocess_polarity
from structural_hybrid_sat import structural_hybrid_sat, try_affine_sat


def branch_family(k):
    """Build an unsatisfiable 3-CNF with k pivot variables and 8k ring variables."""
    if k < 1:
        raise ValueError("k must be positive")
    ring = list(range(k + 1, 9 * k + 1))
    clauses = set()

    def add_opposites(triple):
        clauses.add(tuple(sorted(triple)))
        clauses.add(tuple(-v for v in sorted(triple)))

    for i, a in enumerate(ring):
        add_opposites((a, ring[(i + 1) % len(ring)], ring[(i + 2) % len(ring)]))
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

    def test_solver_visits(self):
        for k in range(1, 5):
            n, clauses = branch_family(k)
            model, metrics = structural_hybrid_sat(n, clauses)
            self.assertIsNone(model)
            self.assertEqual(metrics["status"], "completed")
            self.assertGreaterEqual(metrics["graph"]["fallback_branches"], 2 ** k - 1)
            self.assertGreaterEqual(metrics["graph"]["calls"], 2 ** (k + 1) - 1)
