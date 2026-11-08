"""Three deterministic dense 3-CNF families with identical primal graph K_n.

Graph-theoretic width/connectedness alone cannot classify SAT difficulty.
All generators are explicit, standard, mathematical test cases.
"""
from __future__ import annotations

from itertools import combinations, product


def all_positive_triples(n):
    """SAT, positive-only 3-CNF, primal graph K_n for n >= 3."""
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be at least three")
    return n, [tuple(triple) for triple in combinations(range(1, n + 1), 3)]


def all_signs_on_each_triple(n):
    """UNSAT, all eight exclusion patterns for each triple, graph K_n."""
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be at least three")
    clauses = []
    for support in combinations(range(1, n + 1), 3):
        for forbidden in product((False, True), repeat=3):
            clauses.append(tuple(-v if bit else v for v, bit in zip(support, forbidden)))
    return n, clauses


def opposite_monotone_triples(n):
    """Positive AND negative 3-clauses on all triples.

    Each positive triple requires at most two variables False.
    Each negative triple requires at most two variables True.
    Hence SAT iff n <= 4 (for n >= 3).
    Graph K_n, no unit or pure literals, no full support-signature block.
    """
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be at least three")
    triples = [tuple(c) for c in combinations(range(1, n + 1), 3)]
    return n, triples + [tuple(-v for v in c) for c in triples]


def validate_family_cases():
    return {
        "positive": {"sat": True, "reason": "set all variables True"},
        "full_support": {"sat": False,
                         "reason": "all 8 forbidden patterns on each triple"},
        "opposite_monotone": {
            "sat_if": "n <= 4",
            "reason": "both number of True and False variables at most two"},
    }
