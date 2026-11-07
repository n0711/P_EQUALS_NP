"""Independent finite oracle for exact graph-separator SAT experiments."""
import itertools
import random
import unittest

from graph_separator_sat import graph_separator_sat
from sat import dpll, verify


def oracle(n, clauses):
    for model in itertools.product((False, True), repeat=n):
        if all(any(model[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return model
    return None


def one_gate(blocks):
    clauses = []
    for i in range(blocks):
        a, b = 2 * i + 2, 2 * i + 3
        clauses.extend(((1, a, b), (-1, -a, b), (a, -b)))
    return 2 * blocks + 1, clauses


def two_gates(blocks):
    clauses = []
    for i in range(blocks):
        a, b = 2 * i + 3, 2 * i + 4
        clauses.extend(((1, 2, a, b), (-1, -2, -a, -b)))
    return 2 * blocks + 2, clauses


class GraphSeparatorSATTests(unittest.TestCase):
    def check(self, n, formula, **kwargs):
        expected = oracle(n, formula)
        model, metrics = graph_separator_sat(n, formula, **kwargs)
        self.assertEqual(metrics['status'], 'completed', metrics)
        self.assertEqual(model is not None, expected is not None, (n, formula, metrics))
        if model is not None:
            self.assertTrue(verify(n, formula, model))
        self.assertEqual(dpll(n, formula) is not None, expected is not None)
        return metrics

    def test_edge_cases(self):
        cases = ((0, []), (0, [()]), (4, []), (2, [(1,), (-1,)]),
                 (3, [(1,-1), (2,), (2,2)]), (3, [()]),
                 (2, [(1,2), (-1,2), (1,-2), (-1,-2)]))
        for n, clauses in cases:
            with self.subTest(n=n, clauses=clauses):
                self.check(n, clauses)

    def test_graph_articulation(self):
        n, formula = one_gate(7)
        info = self.check(n, formula)
        self.assertGreater(info['separator_1_splits'], 0, info)
        self.assertGreater(info['component_splits'], 0, info)

    def test_graph_two_variable_separator(self):
        n, formula = two_gates(6)
        info = self.check(n, formula)
        self.assertEqual(info['separator_1_splits'], 0, info)
        self.assertGreater(info['separator_2_splits'], 0, info)
        self.assertGreater(info['component_splits'], 0, info)

    def test_dense_unsat_fallback(self):
        for n in (3, 5):
            formula = [tuple((-v if assignment[v-1] else v) for v in range(1,n+1))
                       for assignment in itertools.product((False,True), repeat=n)]
            info = self.check(n, formula)
            self.assertGreater(info['fallback_branches'], 0)
            self.assertEqual(info['separator_1_splits'], 0)
            self.assertEqual(info['separator_2_splits'], 0)

    def test_random_independent_oracle(self):
        rng = random.Random(20261107)
        for n in range(9):
            lits = [v for v in range(-n, n+1) if v]
            for _ in range(100):
                formula = [tuple(rng.choice(lits) for _ in range(rng.randrange(5)))
                           for _ in range(rng.randrange(17))] if n else [()] * rng.randrange(3)
                self.check(n, formula)

    def test_renaming_invariance(self):
        rng = random.Random(417)
        for n in range(1, 8):
            for _ in range(30):
                formula = [tuple(rng.choice((-1,1)) * rng.randrange(1,n+1)
                                 for _ in range(rng.randrange(4))) for _ in range(12)]
                permutation = list(range(1,n+1))
                rng.shuffle(permutation)
                renamed = [tuple((1 if lit>0 else -1)*permutation[abs(lit)-1]
                                 for lit in clause) for clause in formula]
                self.assertEqual(graph_separator_sat(n,formula)[0] is not None,
                                 graph_separator_sat(n,renamed)[0] is not None)

    def test_resource_limit_is_not_unsat(self):
        n, f = two_gates(8)
        model, stats = graph_separator_sat(n, f, max_calls=1)
        self.assertIsNone(model)
        self.assertEqual(stats['status'], 'limit_calls')

    def test_pair_limit_and_disabled_separators(self):
        n, f = two_gates(5)
        for kw in ({'max_separator_size':0}, {'pair_scan_limit':3},
                   {'max_separator_size':1}):
            self.check(n, f, **kw)

    def test_invalid_input(self):
        for n, f in ((-1, []), (1, [(2,)]), (2, [(0,)])):
            with self.assertRaises(ValueError):
                graph_separator_sat(n, f)
        for kw in ({'max_separator_size':3}, {'pair_scan_limit':0},
                   {'max_calls':0}):
            with self.assertRaises(ValueError):
                graph_separator_sat(2, [], **kw)


if __name__ == '__main__':
    unittest.main()
