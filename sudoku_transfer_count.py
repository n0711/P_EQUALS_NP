"""Exact generalized Sudoku counting by a row-transfer state graph.

A row is a permutation of digits. The transfer frontier stores q column
digit masks and b currently active box masks, where q = b*b. States with
identical future constraints are memoized. This implements sparse transfer
matrix multiplication over nonnegative integers, without enumerating all
complete q^(q*q) colorings.

This is a finite exact counting algorithm, NOT polynomial-time for
arbitrary generalized Sudoku. Exceeded limits return UNDECIDED (None).
"""
from __future__ import annotations

from itertools import permutations
from math import factorial
from time import perf_counter

from sudoku_graph_np import _validate, verify_sudoku_certificate


class _StateLimit(Exception):
    pass


def count_sudoku_transfer(
    box,
    givens,
    *,
    max_states=100000,
    max_row_permutations=100000,
    symmetry_break_blank=True,
):
    """Return (exact_count_or_None, witness_or_None, metrics).

    status='completed' means the count is exact (including zero).
    status='limit_states' or 'limit_row_permutations' is UNDECIDED.
    Counts include every completion, not merely equivalence classes.
    The optional first-row symmetry applies ONLY to a clue-free board.
    """
    q, flat = _validate(box, givens)
    for name, bound in (("max_states", max_states),
                        ("max_row_permutations", max_row_permutations)):
        if bound is not None and (
            not isinstance(bound, int) or isinstance(bound, bool) or bound < 1
        ):
            raise ValueError(name + " must be a positive integer or None")
    if not isinstance(symmetry_break_blank, bool):
        raise ValueError("symmetry_break_blank must be boolean")

    started = perf_counter()
    blank = not any(flat)
    symmetry = blank and symmetry_break_blank
    multiplier = factorial(q) if symmetry else 1
    stats = {
        "status": "completed",
        "method": "row_transfer_exact_integer_counting",
        "states": 0,
        "transitions": 0,
        "row_trials": 0,
        "memo_hits": 0,
        "memo_entries": 0,
        "row_candidate_counts": [],
        "symmetry_first_row_fixed": symmetry,
        "symmetry_multiplier": multiplier,
        "elapsed_seconds": 0.0,
    }

    def finish(status, count, witness=None):
        stats["status"] = status
        stats["elapsed_seconds"] = perf_counter() - started
        return count, witness, stats

    rows = [tuple(flat[r*q:(r+1)*q]) for r in range(q)]
    candidates = []
    digits = set(range(1, q + 1))
    for r, row in enumerate(rows):
        nonzero = [v for v in row if v]
        # A duplicate within a row contradicts its all-different constraint.
        if len(nonzero) != len(set(nonzero)):
            return finish("completed", 0)
        if symmetry and r == 0:
            options = [tuple(range(1, q + 1))]
        else:
            remaining = sorted(digits.difference(nonzero))
            total = factorial(len(remaining))
            if max_row_permutations is not None and total > max_row_permutations:
                stats["row_candidate_counts"].append(total)
                return finish("limit_row_permutations", None)
            missing_places = [i for i, x in enumerate(row) if not x]
            options = []
            for perm in permutations(remaining):
                filled = list(row)
                for pos, digit in zip(missing_places, perm):
                    filled[pos] = digit
                options.append(tuple(filled))
        candidates.append(tuple(options))
        stats["row_candidate_counts"].append(len(options))

    zeros = (0,) * q
    empty_boxes = (0,) * box
    memo = {}
    witness_choices = {}

    def count_suffix(row_number, column_masks, active_boxes):
        if row_number == q:
            return 1
        key = (row_number, column_masks, active_boxes)
        previous = memo.get(key)
        if previous is not None:
            stats["memo_hits"] += 1
            return previous
        if max_states is not None and stats["states"] >= max_states:
            raise _StateLimit
        stats["states"] += 1

        total = 0
        for row in candidates[row_number]:
            stats["row_trials"] += 1
            columns = list(column_masks)
            boxes = list(active_boxes)
            compatible = True
            for column, digit in enumerate(row):
                bit = 1 << (digit - 1)
                block_column = column // box
                if columns[column] & bit or boxes[block_column] & bit:
                    compatible = False
                    break
                columns[column] |= bit
                boxes[block_column] |= bit
            if not compatible:
                continue

            stats["transitions"] += 1
            next_cols = tuple(columns)
            next_boxes = empty_boxes if (row_number + 1) % box == 0 else tuple(boxes)
            suffix_count = count_suffix(row_number + 1, next_cols, next_boxes)
            if suffix_count and key not in witness_choices:
                witness_choices[key] = (row, next_cols, next_boxes)
            total += suffix_count
        memo[key] = total
        return total

    try:
        normalized_count = count_suffix(0, zeros, empty_boxes)
    except _StateLimit:
        stats["memo_entries"] = len(memo)
        return finish("limit_states", None)
    stats["memo_entries"] = len(memo)
    exact_count = normalized_count * multiplier

    witness = None
    if normalized_count:
        witness = []
        columns, boxes = zeros, empty_boxes
        for r in range(q):
            key = (r, columns, boxes)
            digit_row, columns, boxes = witness_choices[key]
            witness.append(list(digit_row))
        assert verify_sudoku_certificate(box, givens, witness)
    return finish("completed", exact_count, witness)
