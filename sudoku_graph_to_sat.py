"""An exact, explicit reduction from generalized Sudoku to CNF SAT.

This is a polynomial-size encoding of precolored Sudoku graph coloring,
not a proof of P=NP or a reduction in the opposite direction.
"""
from __future__ import annotations
from itertools import combinations
from sat import verify as verify_cnf
from sudoku_graph_np import _validate, sudoku_graph, verify_sudoku_certificate


def indicator_variable(side, cell, digit):
    """1-indexed propositional variable for a Sudoku cell and color."""
    if not 0 <= cell < side * side or not 1 <= digit <= side:
        raise ValueError("invalid cell or digit")
    return cell * side + digit


def sudoku_to_cnf(box, puzzle):
    """Each proper Sudoku coloring corresponds to a SAT model."""
    side, given = _validate(box, puzzle)
    clauses = []
    for cell in range(side * side):
        digits = [indicator_variable(side, cell, d) for d in range(1, side + 1)]
        clauses.append(tuple(digits))
        clauses.extend((-a, -b) for a, b in combinations(digits, 2))
        if given[cell]:
            clauses.append((indicator_variable(side, cell, given[cell]),))
    edges, _ = sudoku_graph(box)
    for u, v in edges:
        for digit in range(1, side + 1):
            clauses.append((-indicator_variable(side, u, digit),
                            -indicator_variable(side, v, digit)))
    return side ** 3, tuple(clauses)


def coloring_to_cnf_witness(box, puzzle, candidate):
    if not verify_sudoku_certificate(box, puzzle, candidate):
        return None
    side = box * box
    model = [False] * (side ** 3)
    for r, row in enumerate(candidate):
        for c, digit in enumerate(row):
            model[indicator_variable(side, r * side + c, digit) - 1] = True
    count, clauses = sudoku_to_cnf(box, puzzle)
    assert verify_cnf(count, clauses, model)
    return model


def cnf_witness_to_coloring(box, puzzle, model):
    side = box * box
    count, clauses = sudoku_to_cnf(box, puzzle)
    if not hasattr(model, "__len__") or len(model) != count:
        return None
    if not verify_cnf(count, clauses, model):
        return None
    coloring = []
    for r in range(side):
        row = []
        for c in range(side):
            cell = r * side + c
            values = [d for d in range(1, side + 1)
                      if model[indicator_variable(side, cell, d) - 1]]
            if len(values) != 1:
                return None
            row.append(values[0])
        coloring.append(row)
    assert verify_sudoku_certificate(box, puzzle, coloring)
    return coloring
