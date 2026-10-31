"""Small finite checks for mathematical proof obligations (not a P=NP proof)."""
import itertools
import unittest

from sat import dpll, two_sat, verify


def brute_force(n, formula):
    """Independent exhaustive truth-table oracle."""
    for values in itertools.product((False, True), repeat=n):
        if all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in formula):
            return values
    return None


class ProofObligationTests(unittest.TestCase):
    def test_all_cnf_with_two_clauses_on_three_variables(self):
        # All nonempty clauses with 1..3 distinct signed literals;
        # also include the empty clause and contradictory literals.
        literals = [-3, -2, -1, 1, 2, 3]
        clauses = [()] + [
            c for length in (1, 2, 3)
            for c in itertools.combinations(literals, length)
        ]
        for a in clauses:
            for b in clauses:
                formula = (a, b)
                expected = brute_force(3, formula)
                actual = dpll(3, formula)
                self.assertEqual(actual is not None, expected is not None,
                                 msg=f"counterexample: {formula!r}")
                if actual is not None:
                    self.assertTrue(verify(3, formula, actual))

    def test_two_sat_crosscheck_on_all_small_two_clause_instances(self):
        literals = [-3, -2, -1, 1, 2, 3]
        clauses = [()] + [
            c for length in (1, 2)
            for c in itertools.combinations(literals, length)
        ]
        for a in clauses:
            for b in clauses:
                formula = (a, b)
                expected = brute_force(3, formula)
                actual = two_sat(3, formula)
                self.assertEqual(actual is not None, expected is not None,
                                 msg=f"counterexample: {formula!r}")
                if actual is not None:
                    self.assertTrue(verify(3, formula, actual))

    def test_residual_function_count_fixed_variable_order(self):
        # F_k = AND_i(x_i OR y_i). Assign x variables first.
        # Residual Boolean functions over y are indexed by S.
        for k in range(0, 9):
            fingerprints = set()
            y_assignments = list(itertools.product((False, True), repeat=k))
            for mask in range(1 << k):
                fingerprints.add(tuple(
                    all(ys[i] for i in range(k) if (mask >> i) & 1)
                    for ys in y_assignments
                ))
            self.assertEqual(len(fingerprints), 1 << k)

if __name__ == "__main__":
    unittest.main()
