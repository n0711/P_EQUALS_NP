"""Small reproducible exact-counting benchmark and explicit undecided cases.

The independent 4x4 reference is the M7 oracle. Results are exact only
when status='completed'; finite results are not P=NP evidence.
"""
from __future__ import annotations
import json

from sudoku_graph_np import patterned_solution, solve_sudoku_graph, verify_sudoku_certificate
from sudoku_transfer_count import count_sudoku_transfer
from test_sudoku_graph_np import four_by_four_solutions, compatible, NINE


def run_case(name, box, givens, **kwargs):
    count, witness, data = count_sudoku_transfer(box, givens, **kwargs)
    if witness is not None:
        assert verify_sudoku_certificate(box, givens, witness)
    if data["status"] == "completed":
        assert (count > 0) == (witness is not None)
    return {"name": name, "box": box, "side": box*box,
            "given_count": sum(v != 0 for row in givens for v in row),
            "status": data["status"], "exact_count": count,
            "witness_valid": witness is not None, "metrics": data}


def main():
    oracle = four_by_four_solutions()
    assert len(oracle) == 288
    blank4 = [[0]*4 for _ in range(4)]
    known4 = patterned_solution(2)
    partial4 = [list(row) for row in known4]
    for r in range(4):
        partial4[r][r] = 0
    expected_partial4 = sum(compatible(partial4, candidate) for candidate in oracle)
    solved9 = patterned_solution(3)
    one_blank9 = [list(row) for row in solved9]
    one_blank9[0][0] = 0
    result = [
        run_case("blank_4x4_full_row_transfer", 2, blank4,
                 symmetry_break_blank=False, max_states=30000),
        run_case("blank_4x4_symmetry_quotient", 2, blank4,
                 symmetry_break_blank=True, max_states=30000),
        run_case("four_blank_4x4_oracle", 2, partial4),
        run_case("solved_9x9", 3, solved9),
        run_case("single_blank_9x9", 3, one_blank9),
        run_case("standard_9x9_bounded_count", 3, NINE,
                 max_states=60, max_row_permutations=2000),
        run_case("blank_9x9_row_budget", 3, [[0]*9 for _ in range(9)],
                 max_row_permutations=5000),
        run_case("constructed_solved_16x16", 4, patterned_solution(4)),
    ]
    assert result[0]["exact_count"] == result[1]["exact_count"] == 288
    assert result[2]["exact_count"] == expected_partial4
    assert result[3]["exact_count"] == result[4]["exact_count"] == 1
    assert result[6]["status"] == "limit_row_permutations"
    assert result[7]["exact_count"] == 1
    graph_witness, graph_info = solve_sudoku_graph(3, NINE)
    assert graph_info["status"] == "completed" and graph_witness is not None
    print(json.dumps({
        "milestone": "M8",
        "hypothesis": "sparse row-transfer counts exact Fourier Sudoku partition function",
        "known_independent_4x4_solutions": len(oracle),
        "partial4_oracle_exact_count": expected_partial4,
        "graph_witness_on_9x9": {
            "status": graph_info["status"],
            "nodes": graph_info["nodes"],
            "has_witness": graph_witness is not None,
        },
        "complexity": "exponential worst-case transfer states; no P=NP conclusion",
        "recording": "Python 3, same runner, arbitrary-precision integer counts",
        "cases": result,
    }, indent=2))


if __name__ == "__main__":
    main()
