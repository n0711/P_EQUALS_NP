"""Fourier / phase-integral diagnostics for Sudoku graph coloring.

RioTuner source inspiration (n0711/riotuner, private repository):
engine/src/partials.rs demodulates a signal by complex phase factors
inside overlapping windows; engine/src/window.rs uses Blackman-Harris.

Here we reuse the mathematical phase-projection idea, NOT audio code.
For q colors and integer a,b in [1,q]:
delta(a,b) = (1/q) sum_{k=0}^{q-1} exp(2*pi*i*k*(a-b)/q)
           = (1/2pi) integral_0^{2pi} exp(i*(a-b)*theta) dtheta
           = 1 when a==b, else 0 (exact arithmetic).

On a fully assigned Sudoku graph, sum_edges(delta) is the exact number
of same-color conflicts. Floating-point is diagnostic ONLY; exact integer
edge checking remains the verifier. Nonuniform audio windowing destroys
this exact discrete orthogonality and should not decide SAT.
"""
from __future__ import annotations

import cmath
import math

from sudoku_graph_np import _validate, sudoku_graph


def blackman_harris_weights(count):
    """Independent equation-based reproduction of the known four-term window."""
    if not isinstance(count, int) or count < 1:
        raise ValueError("count must be positive")
    if count == 1:
        return (1.0,)
    return tuple(
        0.35875
        - 0.48829 * math.cos(2.0 * math.pi * k / (count - 1))
        + 0.14128 * math.cos(4.0 * math.pi * k / (count - 1))
        - 0.01168 * math.cos(6.0 * math.pi * k / (count - 1))
        for k in range(count)
    )


def character_projection(colors, a, b, *, window="rectangular"):
    """Numeric phase projection; never an exact SAT decision oracle."""
    if not isinstance(colors, int) or colors < 1:
        raise ValueError("colors must be positive")
    if not (isinstance(a, int) and isinstance(b, int)
            and 1 <= a <= colors and 1 <= b <= colors):
        raise ValueError("colors must be integers in 1..colors")
    if window == "rectangular":
        weights = (1.0,) * colors
    elif window == "blackman_harris":
        weights = blackman_harris_weights(colors)
    else:
        raise ValueError("unknown window")
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("window has zero weight")
    diff = a - b
    return sum(
        weight * cmath.exp(2j * math.pi * k * diff / colors)
        for k, weight in enumerate(weights)
    ) / total_weight


def sudoku_phase_energy(box, coloring, *, window="rectangular"):
    """Evaluate a complete or partial assignment over Sudoku graph edges.

    Only edges with two assigned positive digits contribute. The
    'exact_conflicts' key is evaluated via integer equality, not floats.
    A zero conflict count on a *partial* coloring is NOT SAT.
    """
    side, flat = _validate(box, coloring)
    edges, _ = sudoku_graph(box)
    populated = [(u, v) for u, v in edges if flat[u] and flat[v]]
    phases = [character_projection(side, flat[u], flat[v], window=window)
              for u, v in populated]
    exact_conflicts = sum(flat[u] == flat[v] for u, v in populated)
    return {
        "side": side,
        "window": window,
        "assigned_cells": sum(x != 0 for x in flat),
        "scored_edges": len(populated),
        "total_edges": len(edges),
        "exact_conflicts": exact_conflicts,
        "phase_energy_real": sum(z.real for z in phases),
        "phase_energy_imag": sum(z.imag for z in phases),
        "phase_abs_energy": sum(abs(z) for z in phases),
        "max_projection_error": max(
            (abs(z - float(flat[u] == flat[v]))
             for (u, v), z in zip(populated, phases)),
            default=0.0,
        ),
        "valid_complete_coloring": (
            all(flat) and exact_conflicts == 0
        ),
    }


def candidate_phase_scores(box, coloring, row, col):
    """Fourier-based edge-clash diagnostics for each candidate color.

    These scores are identical to counting assigned same-color peers,
    apart from floating-point error, and cannot establish a speedup.
    """
    side, flat = _validate(box, coloring)
    if not (isinstance(row, int) and isinstance(col, int)
            and 0 <= row < side and 0 <= col < side):
        raise ValueError("cell out of range")
    vertex = row * side + col
    if flat[vertex]:
        raise ValueError("candidate cell must be blank")
    _, peers = sudoku_graph(box)
    neighbors = [flat[u] for u in peers[vertex] if flat[u]]
    return {
        digit: {
            "exact_clashes": sum(digit == other for other in neighbors),
            "fourier_clashes": sum(
                character_projection(side, digit, other).real
                for other in neighbors
            ),
        }
        for digit in range(1, side + 1)
    }
