"""Reproducible numerical integral/phase experiment on Sudoku coloring.

Compares exact graph-conflict checks and two Fourier quadrature windows;
all numeric results are diagnostics, never proof of SAT or UNSAT.
"""
import json
from sudoku_graph_np import patterned_solution, solve_sudoku_graph
from sudoku_phase_integrals import sudoku_phase_energy, candidate_phase_scores


def main():
    full = patterned_solution(3)
    blank = [list(row) for row in full]
    blank[0][0] = 0
    invalid = [list(row) for row in full]
    invalid[0][0] = full[0][1]
    puzzle4 = [
        [1, 0, 0, 4],
        [0, 4, 1, 0],
        [0, 1, 4, 0],
        [4, 0, 0, 1],
    ]
    answer4, metrics4 = solve_sudoku_graph(2, puzzle4)
    rows = [
        {"name": "solved_9x9", "rectangular": sudoku_phase_energy(3, full),
         "blackman_harris": sudoku_phase_energy(3, full, window="blackman_harris")},
        {"name": "one-conflict_9x9", "rectangular": sudoku_phase_energy(3, invalid),
         "blackman_harris": sudoku_phase_energy(3, invalid, window="blackman_harris")},
        {"name": "one-blank_9x9", "rectangular": sudoku_phase_energy(3, blank),
         "blackman_harris": sudoku_phase_energy(3, blank, window="blackman_harris")},
        {"name": "four_by_four_graph_search",
         "solver_status": metrics4["status"], "solver_nodes": metrics4["nodes"],
         "has_solution": answer4 is not None,
         "rectangular": sudoku_phase_energy(2, answer4) if answer4 else None},
    ]
    if any(item["rectangular"] and abs(
           item["rectangular"]["phase_energy_real"]
           - item["rectangular"]["exact_conflicts"]) > 1e-8 for item in rows):
        raise AssertionError("Fourier projection disagreed with exact conflicts")
    print(json.dumps({
        "method": "RioTuner-inspired Fourier phase projection (not pitch extraction)",
        "interpretation": "uniform Fourier projection equals edge clashes; windowed leakage is diagnostic",
        "claim": "no asymptotic SAT/Sudoku speedup or P=NP proof",
        "complexity": "phase projection O(q|E|) vs direct checking O(|E|)",
        "candidate_scores_0_0": candidate_phase_scores(3, blank, 0, 0),
        "examples": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
