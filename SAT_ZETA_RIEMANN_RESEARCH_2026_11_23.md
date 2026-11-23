# M11 (23 November 2026) - SAT, arithmetic zeta functions, and an explicit proof barrier

**Researcher:** Charalampos Nadiotis (PELAOS Tech)  
**Status:** Exact mathematical identities derived from standard Boolean algebra, point-counting and arithmetic-zeta definitions. The results are **not new P-versus-NP theorems**. No proof of P=NP, P!=NP, RH or GRH is claimed.  
**Dependencies:** M10's quadratic encoding in \`rh_grh_bridge.py\` and \`RIEMANN_HYPOTHESIS_RESEARCH_2026_11_23.md\`.

## Question and hypotheses

Given any CNF formula F with n Boolean variables, let S(F) be the **number of satisfying assignments to those n named variables, including free variables**. Let X_F be the common-zero scheme over the integers of the **entire** quadratic M10 polynomial system, including its auxiliary prefix equations. Is its arithmetic zeta function informative enough to yield a deterministic polynomial-time SAT algorithm or lower bound?

Theorem M10.1 is stronger than mere existential equivalence: every satisfying assignment has **exactly one** extension to the auxiliary variables, over every field. This preserves *counts*, not just SAT/UNSAT.

## Theorem M11.1 (constant field-extension point counts)

For **every prime p and integer r >= 1**,

\[
\#X_F(\mathbb{F}_{p^r}) = S(F).
\]

**Proof.** M10 imposes \`x_i(x_i-1)=0\`, which has precisely the roots 0 and 1 in any field. Every original variable at a common zero is therefore Boolean. Each prefix equation \`z_j-q_j z_{j-1}=0\` fixes its auxiliary uniquely from the original Boolean values, and the final clause-product equation holds exactly when the clause is true. Thus restriction to original variables is a bijection between field-valued zeros and satisfying assignments, independent of p or r. QED.

**Stronger integral explanation.** \(\mathbb{Z}[x]/(x(x-1)) \cong \mathbb{Z}\times\mathbb{Z}\) by the Chinese remainder theorem because the ideals \((x)\) and \((x-1)\) are comaximal. Applying this to n variables identifies the Boolean coordinate algebra with \(\mathbb{Z}^{2^n}\). Each clause equation sets the nonsatisfying coordinates to zero; each auxiliary equation simply eliminates one uniquely determined auxiliary variable. Consequently the full coordinate algebra is isomorphic to \(\mathbb{Z}^{S(F)}\), with the convention that \(\mathbb{Z}^{0}\) is the zero ring. Geometrically, X_F is a disjoint union of S(F) copies of \(\operatorname{Spec}\mathbb{Z}\). Nothing number-theoretically subtle remains in this special scheme.

## Corollary M11.2 (exact local and global zeta identity)

For each prime p, define the local point-counting zeta function

\[
Z(X_F/\mathbb{F}_p,t)
=\exp\left(\sum_{r=1}^\infty
\frac{\#X_F(\mathbb{F}_{p^r})}{r}t^r\right).
\]

By Theorem M11.1 and \(-\log(1-t)=\sum_{r\ge 1}t^r/r\),

\[
\boxed{Z(X_F/\mathbb{F}_p,t)=(1-t)^{-S(F)}}.
\]

For complex s with \(\Re(s)>1\), the global arithmetic Euler product is

\[
\begin{aligned}
\zeta_{X_F}(s)
&=\prod_{\text{primes }p} Z(X_F/\mathbb{F}_p,p^{-s})\\
&=\prod_p (1-p^{-s})^{-S(F)}\\
&=\boxed{\zeta(s)^{S(F)}}.
\end{aligned}
\]

These equalities extend meromorphically using the **already known** analytic continuation of the ordinary Riemann zeta function. **No assumption of RH or GRH appears in the proof.**

The coefficient of t in each local zeta power series is S(F). More generally, the kth coefficient is 0 for k>0 when S=0, and for S>=1 is \(\binom{S+k-1}{k}\).

## Corollary M11.3 (SAT is equivalent to a pole for this encoding)

- If F is UNSAT, S(F)=0, so \(\zeta_{X_F}(s)=1\); it has **no pole at 1**.
- If F is SAT, S(F)>=1 and \(\zeta_{X_F}(s)=\zeta(s)^{S(F)}\), which has a **pole of order S(F) at s=1**.

Therefore SAT is equivalent to the existence of the pole at s=1 in this special arithmetic zeta family, while **the pole order and the first local coefficient are both exactly #SAT**.

The correspondence is an NP-complete decision reformulation, *not* a polynomial algorithm for checking the existence of the pole from its compact polynomial-system description. Computing the pole order is #P-complete under the standard counting-problem conventions because it is precisely #SAT under an explicit polynomial-time parsimonious reduction.

**Zero-set boundary:** for S>0, \(\zeta_{X_F}\) has the **same zero locations** as ordinary \(\zeta(s)\), with multiplicities multiplied by S. Assuming RH would place its nontrivial zeros on the critical line for all satisfiable F, but cannot distinguish among their assignments or give an algorithm to calculate S. For S=0, \(\zeta_{X_F}\) is identically 1 and has no zeros.

## Algorithmic interpretation: why the equality does not resolve P vs NP

The compact equation \(\zeta_{X_F}=\zeta^{S(F)}\) does not reveal S(F); it places the entire #SAT difficulty **in the exponent**. A supposed polynomial-time program that takes the M10 encoding of arbitrary F and outputs the exact pole order / first local coefficient would solve #SAT in polynomial time (and therefore SAT); proving such a program exists remains an open proof obligation.

Similarly, deciding merely whether a pole exists from this input is equivalent to SAT. RH supplies a claim about zero locations of \(\zeta(s)\), not an efficient way of finding the exponent S(F). Koiran (1996) establishes a **GRH-conditional** placement of the more general Hilbert Nullstellensatz feasibility problem in \(RP^{NP}\), **not in P**.

**Additional precision:** A numerical oracle for \(\zeta_{X_F}(s)\) or its logarithm must include a precise representation, precision, running-time and output-length model. Neither a symbolic identity nor analytic continuation licenses a polynomial-time bit-complexity claim. Returning \(\zeta(s)^{S(F)}\) as a symbolic expression with an **unknown** exponent is not calculating that function from the input.

## Reproducible finite evidence

- \`zeta_sat.py\` implements bounded exhaustive **#SAT** (maximum 16 variables by default) and the exact symbolic coefficients of \((1-t)^{-S}\). It does **not** evaluate an arithmetic zeta function from a CNF in polynomial time.
- \`test_zeta_sat.py\` independently counts all points of the M10 polynomial system over \(\mathbb F_2\) and its nontrivial extension field \(\mathbb F_4\) in small examples (including non-Boolean candidate values); it cross-checks truth tables, seeded formulas, model counts, local coefficients and input validation.
- \`.github/workflows/m11-zeta-sat.yml\` runs the tests and Python syntax checks.

Reproduce: \`python -m unittest -v test_zeta_sat.py\`.

**Status at authorship:** source and tests pushed; passing CI must be independently inspected before upgrading to CI-verified evidence. Finite cases do not prove the complexity classification or an open conjecture.

## Next falsifiable target

1. Assess whether an independently defined **restricted family** admits efficiently computable S (for example, complete recognized affine systems over GF(2), where \`S=0\` or \`2^{n-rank}\`); this is a standard tractability result and must not be generalized beyond its hypotheses.
2. Track the conversion bit cost and any hidden expansion separately from analytic notation.
3. Seek a *new* worst-case theorem for unrestricted SAT or a genuinely general lower bound. Neither is provided by the arithmetic zeta reformulation.

## Sources and prior work

1. Clay Mathematics Institute, **P vs NP** (currently unsolved): https://www.claymath.org/millennium/p-vs-np/
2. Pascal Koiran, *Hilbert's Nullstellensatz Is in the Polynomial Hierarchy*, Journal of Complexity 12(4), 1996: https://www.sciencedirect.com/science/article/pii/S0885064X96900199
3. Ivan Mustață, *The Hasse-Weil zeta function: definition* (standard finite-field point-counting zeta): https://websites.umich.edu/~mmustata/lecture2.pdf
4. Arithmetic scheme zeta via Euler product: https://www.mathi.uni-heidelberg.de/~venjakob/diplom/williams.pdf
5. Harvard/MIT online notes on #SAT and counting complexity: https://hardness.mit.edu/drafts/2023-10-15.pdf

**Outcome:** a complete exact identity and an NP/#P-hardness barrier for the *particular* zeta-function encoding. This strengthens the research program's falsification discipline; it is not an affirmative or negative solution of P vs NP.
