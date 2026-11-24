# M12 (23 November 2026) — Polynomial-time zeta exponents on recognized affine CNF

**Author:** Charalampos Nadiotis, PELAOS Tech  
**Category:** Established affine constraint theory, reproducible implementation and a bounded interpretation of the number-theoretic SAT program.  
**Status at creation:** Mathematical result proved under an explicit recognizer contract; implementation/CI still subject to observed verification. **This does not prove P=NP, P!=NP, RH or GRH.**

## Research question

M11 showed that the integer polynomial scheme X_F produced by M10 has arithmetic zeta function

\[
\zeta_{X_F}(s)=\zeta(s)^{S(F)}, \quad \Re(s)>1,
\]

where \(S(F)=\#\mathrm{SAT}(F)\) counts assignments to *all* \(n\) named variables. In general computing this exponent is #SAT-hard. Can the exponent be obtained in polynomial time for a **precisely stated subclass** without traversing all \(2^n\) assignments?

**Answer:** Yes, for CNFs consisting only of conservative, individually recognized complete XOR clause blocks with 1–3 variables. The technique is Gaussian elimination over GF(2), not a result of RH.

## Encoding recognized complete XOR blocks

For an unsigned variable support \(U=\{i_1,\ldots,i_k\}\), with \(1\le k\le3\), each signed clause over U excludes exactly one Boolean assignment to those k variables. A full parity block contains **all** \(2^{k-1}\) signed clauses that forbid exactly those local assignments of a common parity p. Its conjunction therefore enforces

\[
\bigoplus_{i\in U}x_i=1\oplus p.
\]

Remove tautological clauses and duplicate clauses, including repeated copies of literals, *before* checking complete support patterns. Every surviving support must comprise one such complete XOR block. Each group then corresponds exactly to one GF(2) linear equation. If any support is incomplete, has mixed parity, has width above three, or cannot otherwise be recognized, the routine returns **unrecognized**, never falsely reporting UNSAT or a #SAT count. An explicit empty CNF clause is a recognized contradiction with exactly zero models.

## Theorem M12.1 — exact polynomial-time exponent on affine CNF

Let \(F\) be an explicitly represented CNF over \(n\) named variables whose non-tautological clauses all satisfy the complete-XOR-block grammar above. Let \(A\in\mathbb F_2^{m\times n}\) and \(b\in\mathbb F_2^m\) be the resulting matrix and right-hand side. Let \(r=\mathrm{rank}_{\mathbb F_2}(A)\). Then

\[
S(F)=
\begin{cases}
0,&\text{if } Ax=b\text{ is inconsistent},\\
2^{n-r},&\text{otherwise}.
\end{cases}
\]

Furthermore, the M10-M11 arithmetic zeta function satisfies

\[
\zeta_{X_F}(s)=
\begin{cases}
1,&S(F)=0,\\
\zeta(s)^{2^{n-r}},&S(F)>0,
\end{cases}
\qquad \Re(s)>1.
\]

**Proof.** Every complete XOR block is logically equivalent to precisely one linear parity equation, so their conjunction has exactly the solutions of \(Ax=b\). Standard Gaussian elimination decides whether this system is inconsistent. If consistent, it has \(n-r\) free variables. Every choice of these free variables extends uniquely to a solution, producing \(2^{n-r}\) total assignments. The count includes unused variables. M10's auxiliary variables are also uniquely determined and therefore do not multiply the count. Applying M11's established identity yields the arithmetic zeta formula. QED.

**Complexity.** Recognition groups clauses with width at most three and checks up to four patterns per support. Constructing the matrix and performing bitwise GF(2) elimination use polynomially many bit operations in the explicitly encoded input length \(N\). In particular, ordinary dense elimination has an \(O(n^3)\) arithmetic-operation upper bound; bit encoding and construction remain polynomial as well. The count \(2^{n-r}\) requires only \(n-r+1\) bits, despite its numerical magnitude. Generating local zeta coefficients through degree \(d\) takes polynomial time in \(N+d\) *including the output size*, not automatically polynomial in \(N+\log d\) if \(d\) arrives in binary. No exhaustive enumeration is needed on recognized inputs.

The same counting result can be stated for arbitrary *explicitly given linear equations* over GF(2); the implemented recognizer is a strict and conservative subset of all possible affine CNF encodings. This is an established algorithmic tractability fact, not a novel general P-versus-NP claim.

## Example

Three named variables \(x_1,x_2,x_3\) with XOR equation \(x_1\oplus x_2=1\) have rank 1, so S=\(2^{3-1}=4\). Their M10 scheme has exactly four points over every finite field extension, with

\[
Z(X_F/\mathbb F_p,t)=(1-t)^{-4}
=1+4t+10t^2+20t^3+\cdots.
\]

Changing to the inconsistent system \(x_1=0,\ x_2=0,\ x_1\oplus x_2=1\) yields zero models and zeta equal to 1. Neither result uses RH.

## Implementation and evidence protocol

- `affine_zeta_sat.py`: conservative complete-XOR recognition using the pre-existing M5 affine solver, rank extraction, exact model counts, and local coefficients. Unrecognized inputs return null counts and must be handled separately.
- `test_affine_zeta_sat.py`: independent Boolean truth-table counts, full parity-block generator, seeded rank checks, signed relabelling invariance, zero-variable/empty-clause boundaries, connected even/odd cubic Tseitin instances, a 200-variable equality chain, and a 1,000-variable free case.
- `.github/workflows/m12-affine-zeta.yml`: executes M12 together with the M10/M11 oracles and compiles Python modules. Final verification must use the workflow run ID and the exact head commit.

**Expected counterexample/falsification gate:** A formula outside the grammar with reported model count 0 or positive rather than explicit "unrecognized"; a disagreement with independent truth-table counting; inconsistent parity constraints reported with a nonzero count; or any unnoticed enumeration in the recognized path invalidates the implementation's claims.

## Distinguishing conditional from unconditional claims

1. **Unconditional:** Complete parity block recognition and GF(2) elimination count all solutions in polynomial time *for the recognized class*. The zeta identity then holds.
2. **Conditional on GRH:** Koiran's published result for general Hilbert's Nullstellensatz in RP^NP; this is unrelated to the polynomial rank computation here.
3. **Still missing:** A deterministic polynomial-time algorithm for **every** CNF, or a general lower bound excluding all polynomial-time SAT algorithms. Thus neither P=NP nor P!=NP has been proved.

## Prior literature

- T. J. Schaefer (1978), *The Complexity of Satisfiability Problems*, STOC, https://doi.org/10.1145/800133.804350 — classification of tractable Boolean constraint languages including affine relations.
- P. Koiran (1996), *Hilbert's Nullstellensatz Is in the Polynomial Hierarchy*, Journal of Complexity, https://www.sciencedirect.com/science/article/pii/S0885064X96900199 — GRH-conditional result for general algebraic feasibility.
- Earlier M10 and M11 records: [quadratic integer encoding](RIEMANN_HYPOTHESIS_RESEARCH_2026_11_23.md), [exact arithmetic zeta count identity](SAT_ZETA_RIEMANN_RESEARCH_2026_11_23.md).

**Outcome:** A constructive positive result for a well-defined restricted SAT family, paired with an explicit rejection contract that prevents generalization to arbitrary CNF.
