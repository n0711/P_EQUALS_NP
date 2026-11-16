"""Independent small CNF oracle and structured-frontier regression tests."""
import itertools
import random
import unittest

from dense_cnf_families import guarded_frontier_family
from frontier_sat import frontier_sat
from polarity_sat import preprocess_polarity
from structural_hybrid_sat import try_affine_sat
from sat import verify


def pairs(k):
    return [(i, k + i) for i in range(1, k + 1)]


class FrontierTests(unittest.TestCase):
    def test_edge_cases(self):
        for n, cnf, answer in [(0, [], True), (0, [()], False),
                                (2, [(1,), (-1,)], False),
                                (3, [(1, -1), (2,)], True),
                                (3, [()], False), (3, [], True)]:
            model, info = frontier_sat(n, cnf)
            self.assertEqual(info['status'], 'completed')
            self.assertEqual(model is not None, answer)
            if model is not None:
                self.assertTrue(verify(n, cnf, model))

    def test_exact_independent_oracle(self):
        rng = random.Random(20261102)
        for n in range(0, 8):
            literals = [i for i in range(-n, n + 1) if i]
            for _ in range(80):
                cnf = [tuple(rng.choice(literals) for _ in range(rng.randrange(4)))
                       for _ in range(rng.randrange(15))] if n else [()] * rng.randrange(2)
                expected = any(verify(n, cnf, a)
                               for a in itertools.product((False, True), repeat=n))
                model, metrics = frontier_sat(n, cnf)
                self.assertEqual(metrics['status'], 'completed')
                self.assertEqual(model is not None, expected, (n, cnf))
                if model is not None:
                    self.assertTrue(verify(n, cnf, model))

    def test_order_changes_width_not_answer(self):
        k = 9
        grouped = list(range(1, 2 * k + 1))
        interleaved = [v for i in range(1, k + 1) for v in (i, k + i)]
        a, s = frontier_sat(2 * k, pairs(k), order=grouped)
        b, t = frontier_sat(2 * k, pairs(k), order=interleaved)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertEqual(s['max_frontier'], k)
        self.assertEqual(s['peak_states'], 1 << k)
        self.assertEqual(t['max_frontier'], 1)
        self.assertLessEqual(t['peak_states'], 2)

    def test_guarded_family_survives_preprocessing_and_exceeds_cap(self):
        for k in range(2, 9):
            n, clauses = guarded_frontier_family(k)
            state, residual, partial, _ = preprocess_polarity(n, clauses)
            self.assertEqual(state, "RESIDUAL")
            self.assertFalse(partial)
            self.assertEqual(set(clauses), set(residual))
            self.assertFalse(try_affine_sat(n, residual)[0])
            order = [*range(1, k + 1), n, *range(k + 1, n)]
            model, metrics = frontier_sat(n, residual, order, max_states=2**k - 1)
            self.assertIsNone(model)
            self.assertEqual(metrics["status"], "limit_states")
            model, metrics = frontier_sat(n, residual, order)
            self.assertEqual(metrics["status"], "completed")
            self.assertGreaterEqual(metrics["peak_states"], 2**k)
            self.assertTrue(verify(n, clauses, model))

    def test_guarded_prefixes_have_distinct_suffix_functions(self):
        for k in range(2, 7):
            n, clauses = guarded_frontier_family(k)
            for prefix in itertools.product((False, True), repeat=k):
                for i in range(k):
                    suffix = tuple(j == i for j in range(k))
                    self.assertEqual(verify(n, clauses, prefix + suffix + (True,)),
                                     not prefix[i])

    def test_limit_is_not_unsat(self):
        model, m = frontier_sat(24, pairs(12), max_states=32)
        self.assertIsNone(model)
        self.assertEqual(m['status'], 'limit_states')

    def test_validation(self):
        for order in ([1, 1], [2, 3], [1], [1, 3]):
            with self.assertRaises(ValueError):
                frontier_sat(2, [(1,)], order=order)
        with self.assertRaises(ValueError):
            frontier_sat(2, [(3,)])
        with self.assertRaises(ValueError):
            frontier_sat(2, [], max_states=0)


if __name__ == '__main__':
    unittest.main()
