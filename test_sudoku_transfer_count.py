"""Independent finite counting oracle tests for M8 row-transfer Sudoku."""
import random
import unittest

from sudoku_graph_np import patterned_solution, verify_sudoku_certificate
from sudoku_transfer_count import count_sudoku_transfer
from test_sudoku_graph_np import compatible, four_by_four_solutions, NINE, NINE_SOLUTION


class SudokuTransferCountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = four_by_four_solutions()
        assert len(cls.oracle) == 288

    def oracle_count(self, puzzle):
        return sum(compatible(puzzle, solution) for solution in self.oracle)

    def check_count(self, box, puzzle, expected, **kwargs):
        result, witness, stats = count_sudoku_transfer(box, puzzle, **kwargs)
        self.assertEqual(stats["status"], "completed", (box, puzzle, stats))
        self.assertEqual(result, expected, (box, puzzle, stats))
        self.assertEqual(witness is not None, expected != 0)
        if witness is not None:
            self.assertTrue(verify_sudoku_certificate(box, puzzle, witness))
        return stats

    def test_empty_four_by_four_exact_288_with_symmetry(self):
        blank = [[0] * 4 for _ in range(4)]
        symmetric = self.check_count(2, blank, 288, symmetry_break_blank=True)
        exhaustive = self.check_count(2, blank, 288, symmetry_break_blank=False)
        self.assertEqual(symmetric["symmetry_multiplier"], 24)
        self.assertEqual(exhaustive["symmetry_multiplier"], 1)
        self.assertLess(symmetric["states"], exhaustive["states"])

    def test_all_288_known_solutions_count_one(self):
        for rows in self.oracle:
            puzzle = [list(row) for row in rows]
            self.check_count(2, puzzle, 1)

    def test_240_seeded_clue_subsets_against_independent_counts(self):
        rng = random.Random(20261109)
        for _ in range(240):
            truth = self.oracle[rng.randrange(len(self.oracle))]
            puzzle = [
                [truth[r][c] if rng.randrange(16) < rng.randrange(17) else 0
                 for c in range(4)]
                for r in range(4)
            ]
            self.check_count(2, puzzle, self.oracle_count(puzzle))

    def test_160_random_adversarial_clue_sets(self):
        rng = random.Random(20261110)
        for _ in range(160):
            puzzle = [
                [rng.randrange(1, 5) if rng.random() < .30 else 0
                 for _ in range(4)]
                for _ in range(4)
            ]
            self.check_count(2, puzzle, self.oracle_count(puzzle))

    def test_invalid_duplicate_row_and_column(self):
        bad_row = [[1, 1, 0, 0], [0]*4, [0]*4, [0]*4]
        bad_col = [[1, 0, 0, 0], [1, 0, 0, 0], [0]*4, [0]*4]
        bad_box = [[1, 0, 0, 0], [0, 1, 0, 0], [0]*4, [0]*4]
        for puzzle in (bad_row, bad_col, bad_box):
            self.check_count(2, puzzle, 0)

    def test_known_nine_by_nine_complete(self):
        self.check_count(3, NINE_SOLUTION, 1)
        puzzle = [list(row) for row in NINE_SOLUTION]
        puzzle[0][0] = 0
        self.check_count(3, puzzle, 1)

    def test_known_nine_by_nine_standard_puzzle_bounded(self):
        # Complete enumeration may be expensive even when finding one
        # satisfying witness is fast. Bounded counting is not UNSAT.
        count, model, info = count_sudoku_transfer(
            3, NINE, max_states=60, max_row_permutations=2000)
        self.assertIn(info["status"], ("completed", "limit_states"))
        if info["status"] == "completed":
            self.assertEqual(count, 1)
            self.assertTrue(verify_sudoku_certificate(3, NINE, model))
        else:
            self.assertIsNone(count)
            self.assertIsNone(model)

    def test_constructed_sixteen_by_sixteen(self):
        known = patterned_solution(4)
        self.check_count(4, known, 1)
        puzzle = [list(row) for row in known]
        for r in range(16):
            puzzle[r][(r*7) % 16] = 0
        self.check_count(4, puzzle, 1)

    def test_single_cell_sudoku(self):
        self.check_count(1, [[0]], 1)
        self.check_count(1, [[1]], 1)

    def test_state_limit_is_not_unsat(self):
        blank = [[0]*4 for _ in range(4)]
        result, witness, stats = count_sudoku_transfer(
            2, blank, max_states=1)
        self.assertIsNone(result)
        self.assertIsNone(witness)
        self.assertEqual(stats["status"], "limit_states")

    def test_row_permutation_limit_is_not_unsat(self):
        blank = [[0]*9 for _ in range(9)]
        result, witness, stats = count_sudoku_transfer(
            3, blank, max_row_permutations=5000)
        self.assertIsNone(result)
        self.assertIsNone(witness)
        self.assertEqual(stats["status"], "limit_row_permutations")

    def test_invalid_input_budgets(self):
        blank = [[0]*4 for _ in range(4)]
        for kwargs in ({"max_states": 0}, {"max_row_permutations": 0},
                       {"max_states": True}, {"symmetry_break_blank": 1}):
            with self.assertRaises(ValueError):
                count_sudoku_transfer(2, blank, **kwargs)

    def test_relabel_givens_preserves_count(self):
        rng = random.Random(20261111)
        for _ in range(45):
            original = self.oracle[rng.randrange(288)]
            puzzle = [[original[r][c] if rng.randrange(2) else 0
                       for c in range(4)] for r in range(4)]
            pi = [1,2,3,4]
            rng.shuffle(pi)
            remapped = [[pi[v-1] if v else 0 for v in row] for row in puzzle]
            expected = self.oracle_count(puzzle)
            self.check_count(2, puzzle, expected)
            self.check_count(2, remapped, expected)


if __name__ == "__main__":
    unittest.main()
