# M10 (23 November 2026): Riemann hypotheses, algebraic SAT, and a falsifiable proof boundary

**Researcher:** Charalampos Nadiotis, PELAOS Tech  
**Status:** The reduction proved below is unconditional and standard. The supplied Python implementation and finite tests require CI verification. **No proof of P = NP, P != NP, RH, or GRH is claimed.**  
**Related repository:** `PROOF_STATUS.md`, `RESEARCH_MILESTONES.md`, `structural_hybrid_sat.py` and `paper/structural-sat-milestones.tex`.

## M10 research question

Can a rigorous connection between the Riemann Hypothesis and computational complexity advance the existing exact SAT work? The mathematically relevant pathway is **the Generalized Riemann Hypothesis (GRH) -> arithmetic algebraic feasibility (Hilbert's Nullstellensatz, HN) -> complexity classes**. The classical RH is only a special case of GRH; a result that requires GRH must not be claimed under RH alone.

The educational video [But what is the Riemann hypothesis? Visualizing analytic continuation](https://youtu.be/sD0NjbwqlYw) (3Blue1Brown) motivates the zeta function and analytic continuation; it does **not** establish a SAT algorithm, GRH, or a P-vs-NP proof. The additional video at https://youtu.be/x36UmiSiEzc was supplied as context but its specific assertions were not independently verified for this note.

## Theorem M10.1 (unconditional quadratic-field encoding)

Let `F` be a CNF with `n` explicitly represented Boolean variables, `m` clauses and `L` literal occurrences. A deterministic procedure constructs integer-coefficient polynomial equations `E(F)` such that:

1. Every polynomial has total degree at most 2 and at most 5 distinct monomials.
2. The number of variables, equations and written monomial terms is `O(n + m + L)`; representation of variable indices adds logarithmic factors.
3. **For every field K** (including `C`, `F_2`, `F_3`, `F_5`), `F` is satisfiable if and only if `E(F)` has a common zero over K.

The reduction is polynomial in the conventional *explicit* CNF encoding. If an unused variable count `n` is encoded only as an arbitrarily large binary integer, then writing `n` Boolean equations is not polynomial in that compressed input. The implementation's bound is explicitly parameterized by `n + m + L`; a compressed-input complexity claim is excluded.

**Construction.** For each original Boolean variable `x_i`, add the equation

`x_i (x_i - 1) = 0`.

For a signed literal `l`, define the *falsity factor* `q(l)` as `1 - x_i` for a positive occurrence of `x_i` and as `x_i` for a negated occurrence. A nonempty clause with factors `q_1,...,q_k` is satisfied precisely when `q_1 * ... * q_k = 0`. An empty clause contributes `1 = 0`.

Clauses of width 1 or 2 give degree-at-most-two equations directly. For width `k >= 3`, introduce `k-2` auxiliary variables `z_1,...,z_(k-2)` and equations

```text
z_1 - q_1 q_2 = 0
z_j - z_(j-1) q_(j+1) = 0        (2 <= j <= k-2)
z_(k-2) q_k = 0
```

Add `z_j(z_j - 1) = 0` for every auxiliary variable. Each polynomial has degree at most two and at most five monomials after expansion. The construction handles repeated literals and tautological clauses without special-case simplification.

**Proof.** Let K be a field. From `x(x-1)=0` and the absence of zero divisors, any root has each original `x_i` in `{0,1}`. The auxiliary prefix equations uniquely force `z_j` to equal the product of the first `j+1` falsity factors; hence the last equation forces each clause to have at least one true literal. An empty clause forces `1=0`, which is impossible in any field. Thus every common zero restricts to a satisfying Boolean assignment. Conversely, assign each original variable its satisfying bit and each auxiliary variable its indicated prefix product. Every equation vanishes, including the auxiliary Boolean constraints. Hence the equivalence holds in either direction for every field. QED.

### Corollary M10.2 (why GRH is unnecessary for Boolean polynomial instances)

For this **special family** of algebraic systems, `E(F)` has a complex zero if and only if it has an `F_p` zero for **each** prime `p`, if and only if the original CNF is satisfiable. This follows already from Theorem M10.1; no prime-distribution estimate, analytic continuation, RH or GRH is needed.

Crucially, this universal modular equivalence does **not** make it computationally easy to find a root. Exploring all `p^(n+A)` field tuples is still exponential for fixed `p >= 2`. The result is a *reduction* and validation invariant, not a worst-case speedup.

### Literature boundary: Koiran's conditional theorem

Pascal Koiran, *Hilbert's Nullstellensatz Is in the Polynomial Hierarchy*, Journal of Complexity 12(4), 273-286 (1996), established under GRH that general integer-polynomial complex feasibility (HN) is in `RP^NP` (and hence the second level of the polynomial hierarchy). Its argument exploits modular solvability for a sufficiently large collection of primes, a nontrivial number-theoretic step **for general algebraic systems**. This does not imply `HN in P`, and therefore does not imply `SAT in P` or `P=NP`.

- Original article: https://www.sciencedirect.com/science/article/pii/S0885064X96900199
- Accessible article PDF: https://cs.uwaterloo.ca/~r5olivei/courses/2025-spring-cs860/K96-HN-PH.pdf
- Related geometric-complexity route: Ketan Mulmuley's *On P vs NP, Geometric Complexity Theory, and the Riemann Hypothesis*, https://arxiv.org/abs/0908.1936 . This invokes mathematics beyond the classical zeta RH, and provides no solved P-vs-NP conclusion.

## Implementation and falsification checks

- `rh_grh_bridge.py`: integer sparse quadratic equations, the deterministic lift of a Boolean assignment to all auxiliary variables, and optional modular evaluation. The generator does **not** enumerate roots.
- `test_rh_grh_bridge.py`: independent truth-table SAT oracle, field-grid exhaustive checks for small cases over primes 2, 3 and 5, seeded arbitrary formulas, long-clause degree/output-size guard, and validation cases.
- `.github/workflows/rh-grh-bridge.yml`: isolated CI suite to avoid altering the existing SAT benchmark workflow.

```sh
python -m unittest -v test_rh_grh_bridge.py
```

**Evidence classification:** The proof above is a mathematical derivation of an established construction. Defined tests must not be reported as passed until the GitHub workflow (or a reproducible local run) is observed to complete successfully. Finite tests cannot establish a general computational complexity classification.

## Next proof obligations and decision

**Affirmative route:** Exhibit one deterministic algorithm `A` for **all** CNF inputs (or for all polynomial systems `E(F)` arising from arbitrary CNF) and prove its total bit-operation cost is `O(N^c)` for some fixed `c`, including conversion, auxiliary variables, certificates and arithmetic. Then Cook-Levin implies `P=NP`. No such bound is supplied here.

**Negative route:** Show a superpolynomial lower bound for *every* deterministic polynomial-time candidate deciding SAT, not merely for DPLL, graph separators, arithmetic-circuit representations or bounded-depth models. No such bound is supplied here.

**Falsification gate for this milestone:** a non-Boolean modular root for a prime field, a disagreement between CNF SAT and algebraic feasibility, or superlinear-size growth beyond the stated `O(n + m + L)` construction (up to index encoding) would invalidate M10.1 or its implementation. Conversely, a passing test suite supports finite correctness only.

**Outcome:** A valid, nontrivial cross-domain research bridge and a clearer boundary for the current proof program. The algebraic encoding is unconditional, so assuming GRH adds no leverage to this specific encoding without a further *new algorithmic or lower-bound theorem*.
