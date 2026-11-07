"""Independent oracle and practical finite regression tests for M7 Sudoku-as-NP."""
import itertools
import random
import unittest

from sudoku_graph_np import (
    patterned_solution, solve_sudoku_graph,
    sudoku_graph, sudoku_units, verify_sudoku_certificate,
)


def four_by_four_solutions():
    """Independent row-permutation oracle; no call to the M7 solver."""
    symbols = (1, 2, 3, 4)
    rows = list(itertools.permutations(symbols))
    results = []

    def dfs(chosen):
        if len(chosen) == 4:
            results.append(tuple(chosen))
            return
        r = len(chosen)
        for row in rows:
            if any(row[c] == earlier[c] for earlier in chosen for c in range(4)):
                continue
            if any(row[c] == earlier[d]
                   for earlier_idx, earlier in enumerate(chosen)
                   if earlier_idx // 2 == r // 2
                   for c in range(4)
                   for d in range(4)
                   if c != d and c // 2 == d // 2):
                continue
            dfs(chosen + (row,))

    dfs(())
    return tuple(results)


def compatible(grid, solution):
    return all(clue == 0 or clue == solution[r][c]
               for r, row in enumerate(grid) for c, clue in enumerate(row))


NINE = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]
NINE_SOLUTION = [
    [5,3,4,6,7,8,9,1,2],
    [6,7,2,1,9,5,3,4,8],
    [1,9,8,3,4,2,5,6,7],
    [8,5,9,7,6,1,4,2,3],
    [4,2,6,8,5,3,7,9,1],
    [7,1,3,9,2,4,8,5,6],
    [9,6,1,5,3,7,2,8,4],
    [2,8,7,4,1,9,6,3,5],
    [3,4,5,2,8,6,1,7,9],
]


class SudokuNPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = four_by_four_solutions()
        assert len(cls.oracle) == 288, len(cls.oracle)

    def test_graph_exact_edge_counts_and_cliques(self):
        for b, cells, edge_count in ((1,1,0), (2,16,56), (3,81,810)):
            edges, peers = sudoku_graph(b)
            self.assertEqual(len(peers), cells)
            self.assertEqual(len(edges), edge_count)
            self.assertEqual(len(edges), len(set(edges)))
            self.assertTrue(all(u < v for u, v in edges))
            for unit in sudoku_units(b):
                for u, v in itertools.combinations(unit, 2):
                    self.assertIn((min(u,v), max(u,v)), edges)

    def test_certificate_verifier_rejects_bad_colorings(self):
        solved = patterned_solution(3)
        givens = [[0]*9 for _ in range(9)]
        self.assertTrue(verify_sudoku_certificate(3, givens, solved))
        conflict = [list(row) for row in solved]
        conflict[0][0] = conflict[0][1]
        self.assertFalse(verify_sudoku_certificate(3, givens, conflict))
        forbidden = [[0]*9 for _ in range(9)]
        forbidden[0][0] = (solved[0][0] % 9) + 1
        self.assertFalse(verify_sudoku_certificate(3, forbidden, solved))
        incomplete = [list(row) for row in solved]
        incomplete[0][0] = 0
        self.assertFalse(verify_sudoku_certificate(3, givens, incomplete))

    def test_exact_four_by_four_against_independent_oracle(self):
        rng = random.Random(20261107)
        sample = self.oracle
        for _ in range(240):
            source = sample[rng.randrange(len(sample))]
            probability = rng.randrange(0, 17)
            puzzle = [[source[r][c] if rng.randrange(16) < probability else 0
                       for c in range(4)] for r in range(4)]
            expected = any(compatible(puzzle, candidate) for candidate in sample)
            answer, metrics = solve_sudoku_graph(2, puzzle)
            self.assertEqual(metrics["status"], "completed")
            self.assertEqual(answer is not None, expected, (puzzle, metrics))
            if answer is not None:
                self.assertTrue(verify_sudoku_certificate(2, puzzle, answer))

    def test_four_by_four_random_clues_against_oracle(self):
        rng = random.Random(20261108)
        for _ in range(300):
            puzzle = [[rng.randrange(5) if rng.random() < .32 else 0
                       for c in range(4)] for r in range(4)]
            expected = any(compatible(puzzle, candidate) for candidate in self.oracle)
            answer, stats = solve_sudoku_graph(2, puzzle)
            self.assertEqual(stats["status"], "completed")
            self.assertEqual(answer is not None, expected, (puzzle, stats))
            if answer is not None:
                self.assertTrue(verify_sudoku_certificate(2, puzzle, answer))

    def test_practical_nine_by_nine(self):
        self.assertTrue(verify_sudoku_certificate(3, NINE, NINE_SOLUTION))
        answer, stats = solve_sudoku_graph(3, NINE)
        self.assertEqual(stats["status"], "completed")
        self.assertIsNotNone(answer)
        self.assertTrue(verify_sudoku_certificate(3, NINE, answer))

    def test_empty_and_complete_four_by_four(self):
        self.assertTrue(verify_sudoku_certificate(2, [[0]*4 for _ in range(4)],
                                                  patterned_solution(2)))
        for puzzle in (patterned_solution(2), [[0]*4 for _ in range(4)]):
            answer, stats = solve_sudoku_graph(2, puzzle)
            self.assertEqual(stats["status"], "completed")
            self.assertTrue(verify_sudoku_certificate(2, puzzle, answer))

    def test_conflicting_clues_are_unsat(self):
        puzzle = [[0]*9 for _ in range(9)]
        puzzle[0][0] = puzzle[0][1] = 3
        self.assertIsNone(solve_sudoku_graph(3, puzzle)[0])
        model, info = solve_sudoku_graph(3, puzzle)
        self.assertIsNone(model)
        self.assertEqual(info["status"], "completed")

    def test_one_by_one_sudoku(self):
        for puzzle in ([[0]], [[1]]):
            model, info = solve_sudoku_graph(1, puzzle)
            self.assertEqual(model, [[1]])
            self.assertEqual(info["status"], "completed")

    def test_large_witness_16_by_16_and_sparse_row(self):
        known = patterned_solution(4)
        puzzle = [list(row) for row in known]
        for r in range(16):
            puzzle[r][(r * 7) % 16] = 0
        self.assertTrue(verify_sudoku_certificate(4, puzzle, known))
        model, status = solve_sudoku_graph(4, puzzle)
        self.assertEqual(status["status"], "completed")
        self.assertIsNotNone(model)
        self.assertTrue(verify_sudoku_certificate(4, puzzle, model))

    def test_node_limit_never_means_unsat(self):
        puzzle = [[0]*4 for _ in range(4)]
        answer, info = solve_sudoku_graph(2, puzzle, max_nodes=1)
        self.assertIsNone(answer)
        self.assertEqual(info["status"], "limit_nodes")

    def test_malformed_input_validation(self):
        for b, puzzle in ((0, []), (2, [[0]*4]*3),
                          (2, [[0]*4]*3+[[0]*3]),
                          (2, [[0]*4]*3+[[0,0,0,5]])):
            with self.assertRaises(ValueError):
                solve_sudoku_graph(b, puzzle)
        with self.assertRaises(ValueError):
            solve_sudoku_graph(2, [[0]*4 for _ in range(4)], max_nodes=0)
        with self.assertRaises(ValueError):
            sudoku_graph(0)


if __name__ == "__main__":
    unittest.main()
