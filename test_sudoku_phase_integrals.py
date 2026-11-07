"""Independent checks of RioTuner-inspired Sudoku Fourier integrals.

The phase method is a numerical diagnostic, not an exact solver.
"""
import itertools
import math
import random
import unittest

from sat import dpll, verify as verify_cnf
from sudoku_graph_np import (
    patterned_solution, solve_sudoku_graph, sudoku_graph,
    verify_sudoku_certificate,
)
from sudoku_graph_to_sat import (
    sudoku_to_cnf, coloring_to_cnf_witness, cnf_witness_to_coloring,
)
from sudoku_phase_integrals import (
    character_projection, blackman_harris_weights,
    sudoku_phase_energy, candidate_phase_scores,
)


class SudokuFourierTests(unittest.TestCase):
    def test_discrete_fourier_delta_identity(self):
        for colors in (1, 2, 4, 9, 16):
            for a in range(1, colors + 1):
                for b in range(1, colors + 1):
                    z = character_projection(colors, a, b)
                    self.assertLess(abs(z - float(a == b)), 2e-12)

    def test_exact_graph_color_energy_solved_and_conflict(self):
        for box in (1, 2, 3, 4):
            solved = patterned_solution(box)
            info = sudoku_phase_energy(box, solved)
            self.assertTrue(info["valid_complete_coloring"])
            self.assertEqual(info["exact_conflicts"], 0)
            self.assertLess(abs(info["phase_energy_real"]), 3e-10)
            if box == 1:
                continue
            broken = [list(row) for row in solved]
            broken[0][0] = broken[0][1]
            direct = sum(
                broken[u // (box*box)][u % (box*box)]
                == broken[v // (box*box)][v % (box*box)]
                for u, v in sudoku_graph(box)[0]
            )
            check = sudoku_phase_energy(box, broken)
            self.assertEqual(check["exact_conflicts"], direct)
            self.assertGreater(direct, 0)
            self.assertLess(abs(check["phase_energy_real"] - direct), 5e-9)

    def test_partial_grid_is_not_declared_sat(self):
        puzzle = [[0]*9 for _ in range(9)]
        info = sudoku_phase_energy(3, puzzle)
        self.assertEqual(info["exact_conflicts"], 0)
        self.assertFalse(info["valid_complete_coloring"])
        self.assertEqual(info["scored_edges"], 0)

    def test_random_complete_assignments_four_by_four(self):
        rng = random.Random(20261107)
        for _ in range(240):
            grid = [[rng.randrange(1,5) for _ in range(4)] for _ in range(4)]
            check = sudoku_phase_energy(2, grid)
            self.assertLess(abs(check["phase_energy_real"] -
                                check["exact_conflicts"]), 2e-10)

    def test_blackman_harris_not_exact_orthogonality(self):
        weights = blackman_harris_weights(9)
        self.assertEqual(len(weights), 9)
        self.assertAlmostEqual(weights[0], weights[-1], places=12)
        self.assertAlmostEqual(sum(weights), 0.35875*8, delta=0.01)
        self.assertLess(abs(character_projection(9, 1, 2)), 1e-12)
        leaked = character_projection(9, 1, 2, window="blackman_harris")
        self.assertGreater(abs(leaked), 0.01)
        solved = patterned_solution(3)
        stats = sudoku_phase_energy(3, solved, window="blackman_harris")
        self.assertEqual(stats["exact_conflicts"], 0)
        self.assertGreater(stats["phase_abs_energy"], 0.01)
        self.assertFalse(stats["phase_abs_energy"] == 0.0)

    def test_candidate_phase_scores_equal_exact_peer_counts(self):
        solved = patterned_solution(3)
        blank = [list(row) for row in solved]
        blank[0][0] = 0
        scores = candidate_phase_scores(3, blank, 0, 0)
        for digit, data in scores.items():
            self.assertLess(abs(data["fourier_clashes"] -
                                data["exact_clashes"]), 2e-11)
        self.assertEqual(scores[solved[0][0]]["exact_clashes"], 0)
        self.assertGreater(min(scores[d]["exact_clashes"]
                               for d in scores if d != solved[0][0]), 0)

    def test_four_by_four_exact_cnf_reduction(self):
        complete = patterned_solution(2)
        puzzle = [list(row) for row in complete]
        for r in (0, 3):
            for c in (1, 2):
                puzzle[r][c] = 0
        count, cnf = sudoku_to_cnf(2, puzzle)
        self.assertEqual(count, 4**3)
        witness = coloring_to_cnf_witness(2, puzzle, complete)
        self.assertIsNotNone(witness)
        self.assertTrue(verify_cnf(count, cnf, witness))
        recovered = cnf_witness_to_coloring(2, puzzle, witness)
        self.assertEqual(recovered, complete)
        model = dpll(count, cnf)
        self.assertIsNotNone(model)
        result = cnf_witness_to_coloring(2, puzzle, model)
        self.assertTrue(verify_sudoku_certificate(2, puzzle, result))

    def test_wrong_witness_and_conflicting_puzzle_reduction(self):
        known = patterned_solution(2)
        puzzle = [list(row) for row in known]
        puzzle[0][0] = puzzle[0][1]
        self.assertIsNone(coloring_to_cnf_witness(2, puzzle, known))
        count, cnf = sudoku_to_cnf(2, puzzle)
        self.assertIsNone(dpll(count, cnf))
        self.assertIsNone(cnf_witness_to_coloring(2, puzzle, [False]*count))

    def test_phase_projection_input_validation(self):
        for colors, a, b in ((0, 1, 1), (4, 0, 2), (4, 3, 5)):
            with self.assertRaises(ValueError):
                character_projection(colors, a, b)
        with self.assertRaises(ValueError):
            character_projection(4, 1, 2, window="unknown")
        with self.assertRaises(ValueError):
            candidate_phase_scores(2, patterned_solution(2), 0, 0)


if __name__ == "__main__":
    unittest.main()
