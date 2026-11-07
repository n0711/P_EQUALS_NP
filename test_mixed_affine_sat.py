"""M6 independent truth-table and metamorphic tests for mixed affine/CNF SAT."""
import itertools
import random
import unittest

from graph_research_instances import cubic_tseitin_3cnf
from mixed_affine_sat import extract_affine_blocks, mixed_affine_sat
from sat import verify


def xor_block(variables, rhs):
    clauses = []
    for assignment in itertools.product((0, 1), repeat=len(variables)):
        if sum(assignment) % 2 != rhs:
            clauses.append(tuple(-v if bit else v
                                 for v, bit in zip(variables, assignment)))
    return clauses


def oracle(n, formula):
    for model in itertools.product((False, True), repeat=n):
        if all(any(model[abs(lit)-1] == (lit > 0) for lit in c)
               for c in formula):
            return model
    return None


class MixedAffineTests(unittest.TestCase):
    def check(self, n, clauses):
        expected = oracle(n, clauses)
        actual, info = mixed_affine_sat(n, clauses)
        self.assertEqual(info["status"], "completed")
        self.assertEqual(actual is not None, expected is not None,
                         (n, clauses, info))
        if actual is not None:
            self.assertTrue(verify(n, clauses, actual))
        return info

    def test_empty_clauses_and_tautologies(self):
        for n, formula in ((0, []), (0, [()]), (3, []),
                           (3, [(1,-1), (2,)]), (3, [(1,), (-1,)]),
                           (3, [(), (2,)]), (3, [(1,1), (2,-2)])):
            self.check(n, formula)

    def test_complete_xor_blocks_and_unused_variables(self):
        for width in (1, 2, 3):
            for parity in (0, 1):
                formula = xor_block(tuple(range(1,width+1)), parity)
                equations, residual, metrics = extract_affine_blocks(5, formula)
                self.assertEqual(metrics["equations"], 1)
                self.assertEqual(residual, ())
                self.assertEqual(metrics["extracted_clauses"], 1 << (width-1))
                self.check(5, formula)

    def test_mixed_system_linear_forcing_and_unsat(self):
        # XOR(x1,x2,x3)=0 and XOR(x1,x2)=0 force x3=0.
        # Variables x4,x5,x6 are also forced to 0.
        # The remaining four-literal clause then cannot be satisfied.
        formula = xor_block((1,2,3), 0) + xor_block((1,2), 0)
        formula += [(-4,), (-5,), (-6,), (3,4,5,6)]
        info = self.check(6, formula)
        self.assertEqual(info["equations"], 5)
        self.assertEqual(info["residual_clauses"], 1)
        self.assertGreater(info["linear_forced"], 0)

    def test_mixed_satisfiable_witness(self):
        formula = xor_block((1,2,3), 1)
        formula += [(1,2,3,4), (-1,-2,3,4)]
        info = self.check(5, formula)
        self.assertEqual(info["equations"], 1)
        self.assertEqual(info["residual_variables"], 4)

    def test_affine_cycle_inconsistent_without_units(self):
        formula = (xor_block((1,2), 0) + xor_block((2,3), 0)
                   + xor_block((1,3), 1))
        info = self.check(3, formula)
        self.assertEqual(info["equations"], 3)
        self.assertEqual(info["residual_clauses"], 0)
        self.assertGreater(info["linear_conflicts"], 0)

    def test_partial_blocks_do_not_get_extracted(self):
        # Not every small pair of clauses is an XOR.
        formula = [(1,2,3), (1,-2,3)]
        _, residual, stats = extract_affine_blocks(3, formula)
        self.assertEqual(len(residual), 2)
        self.assertEqual(stats["equations"], 0)
        self.check(3, formula)

    def test_seeded_arbitrary_cnf_oracle(self):
        rng = random.Random(2026110706)
        for n in range(9):
            literals = [v for v in range(-n,n+1) if v]
            for _ in range(80):
                formula = [tuple(rng.choice(literals) for _ in range(rng.randrange(5)))
                           for _ in range(rng.randrange(14))] if n else [()] * rng.randrange(2)
                self.check(n, formula)

    def test_seeded_mixed_affine_oracle(self):
        rng = random.Random(519)
        for n in (4, 5, 6, 7, 8):
            for _ in range(35):
                clauses = []
                for __ in range(3):
                    group = tuple(sorted(rng.sample(range(1,n+1), rng.randrange(1,4))))
                    clauses += xor_block(group, rng.randrange(2))
                for __ in range(4):
                    vars4 = rng.sample(range(1,n+1), 4)
                    clauses.append(tuple(rng.choice((-1,1))*v for v in vars4))
                self.check(n, clauses)

    def test_connected_cubic_parity_plus_general_clause(self):
        for vertices in (6, 8, 10, 12):
            for charge, expected in (("odd", False), ("even", True)):
                n, clauses = cubic_tseitin_3cnf(vertices, seed=17, charge=charge)
                if charge == "even":
                    base, _ = mixed_affine_sat(n, clauses)
                    self.assertIsNotNone(base)
                    extra = tuple(v if base[v - 1] else -v for v in (1,2,3,4))
                else:
                    extra = (1,2,3,4)
                formula = clauses + [extra]
                model, stats = mixed_affine_sat(n, formula)
                self.assertEqual(model is not None, expected)
                self.assertEqual(stats["equations"], vertices)
                self.assertEqual(stats["residual_variables"], 4)
                if model is not None:
                    self.assertTrue(verify(n, formula, model))

    def test_renaming_sign_and_clause_order(self):
        rng = random.Random(601)
        for n in (4, 5, 6, 7):
            for _ in range(25):
                base = xor_block((1,2,3), rng.randrange(2))
                base += [tuple(rng.choice((-1,1))*v for v in rng.sample(range(1,n+1), 4))]
                permutation = list(range(1,n+1))
                rng.shuffle(permutation)
                renamed = [tuple((1 if lit > 0 else -1)*permutation[abs(lit)-1]
                                 for lit in clause) for clause in base]
                rng.shuffle(renamed)
                a, _ = mixed_affine_sat(n, base)
                b, _ = mixed_affine_sat(n, renamed)
                self.assertEqual(a is not None, b is not None)

    def test_limit_is_not_unsat(self):
        model, info = mixed_affine_sat(5, [(1,2,3,4)], max_calls=1)
        self.assertIsNone(model)
        self.assertEqual(info["status"], "limit_calls")

    def test_input_validation(self):
        for n, formula in ((-1, []), (2, [(0,)]), (2, [(3,)])):
            with self.assertRaises(ValueError):
                mixed_affine_sat(n, formula)
        for limit in (0, -1, True):
            with self.assertRaises(ValueError):
                mixed_affine_sat(3, [], max_calls=limit)


if __name__ == "__main__":
    unittest.main()
