# M13 (23 November 2026) — Exact #SAT by logarithmic cutsets, affine components and bounded enumeration

**Author:** Charalampos Nadiotis, PELAOS Tech  
**Research status:** Standard, explicitly restricted cutset-conditioning and model-counting theorem, with a new reproducible implementation in this repository. The theorem below is a derived application of established methods, not a general P=NP or P!=NP proof.  
**Dependencies:** [M10 algebraic encoding](RIEMANN_HYPOTHESIS_RESEARCH_2026_11_23.md), [M11 exact arithmetic zeta identity](SAT_ZETA_RIEMANN_RESEARCH_2026_11_23.md), [M12 polynomial affine counting](AFFINE_ZETA_M12_2026_11_23.md).

## 1. Motivation

M11 established the exact arithmetic identity for every explicitly represented CNF formula F,

\[
\zeta_{X_F}(s)=\zeta(s)^{\#F}, \qquad \Re(s)>1,
\]

where \(\#F\) counts **all** assignments to the n named original Boolean variables satisfying F. M12 computes this exponent in polynomial time for a conservative complete-XOR-block subclass. This milestone asks whether the tractable family can also contain **genuinely non-affine** formulas.

**Answer:** Yes, when a caller supplies a logarithmically small variable cutset and every conditioned residual component is either recognized affine, or has logarithmically many variables.

This is a known form of cutset conditioning and independent component counting, specialized to the existing M12 rank machinery. Neither the Riemann Hypothesis nor GRH is necessary.

## 2. Notation and exact counting identity

Let F be a CNF with n original variables, m clauses and L literal occurrences. Let \(S\subseteq\{1,\dots,n\}\) be a **supplied** set of separator variables. For an assignment \(\alpha\in\{0,1\}^S\), simplify F by removing satisfied clauses and false literals. If an empty clause remains, the branch count is zero.

Otherwise let the nontrivial connected components of its *primal graph* on residual clause variables be \(F_{1,\alpha},\ldots,F_{k_\alpha,\alpha}\). Let \(u_\alpha\) be the number of variables outside S not occurring in any residual clause. Different components have disjoint variable sets, and their models can be chosen independently.

**Theorem M13.1 (exact conditioned count).**

\[
\boxed{
\#F=\sum_{\alpha\in\{0,1\}^{S}}
2^{u_\alpha}\prod_{j=1}^{k_\alpha}\#F_{j,\alpha}
}
\]

Here an empty product is 1. If a branch has an empty clause, its summand is 0.

**Proof.** Every complete Boolean assignment has exactly one restriction to S, so the satisfying assignments form a disjoint union indexed by \(\alpha\). Fix a noncontradictory \(\alpha\). Because distinct residual components have disjoint variable sets, choices of satisfying assignments for them are independent and the number of combinations is the product of their model counts. Each of the \(u_\alpha\) unconstrained variables can independently be set to 0 or 1, contributing \(2^{u_\alpha}\). Summing counts for disjoint separator assignments gives the formula. QED.

## 3. Polynomial-time **restricted** theorem

Define the explicit-input size proxy

\[
N_0=\max\{2,n+m+L\},\qquad b=\lfloor\log_2N_0\rfloor.
\]

This assumes n is an explicit variable count, not a gigantic integer compressed into a few bits. If n is only supplied as a binary integer and not explicitly represented, the time bound is polynomial in n+m+L, not necessarily in the compressed encoding's bit length.

The algorithm accepts a supplied separator S only if \(|S|\le b\). For each separator assignment, it builds exact residual primal components. A residual component is accepted if either:

1. Its CNF is recognized *exactly* as the complete XOR-clause grammar in M12. Its model count is computed from the GF(2) rank in polynomial bit time (even if the component has more than b variables), or
2. It contains at most b variables, in which case exhaustive \(2^b\) truth-table enumeration computes the count.

If neither condition holds, the algorithm returns **unrecognized** for the *entire formula*, with no count. It never silently assumes UNSAT for an unsupported component.

**Theorem M13.2 (bounded cutset and bounded non-affine component exact counting).** For any explicitly represented CNF and supplied S that passes the size test, if every noncontradictory separator assignment has only components satisfying the two tests above (except components skipped after a provable zero product), M13 returns the exact model count. Its bit complexity is bounded by

\[
\operatorname{poly}(N_0+d)\,2^{|S|}\,2^b,
\]

where d is the requested local-zeta series degree written in unary/output-size terms. Since \(|S|\le b\le \log_2N_0\), this is polynomial in \(N_0+d\). If the algorithm reports unrecognized, it makes no claim about satisfiability or count.

**Proof.** Soundness follows by applying M13.1 and the exact component counters: rank counting is exact on M12's recognized grammar, and exhaustive evaluation is exact on the bounded components. Contradictory branches have zero models and can be skipped. All component and free-variable factors are calculated exactly and summed. The number of separator assignments is \(2^{|S|}\le N_0\). For each assignment, building the primal components and testing the grammar are polynomial in the explicit input; a non-affine accepted component costs at most \(2^b\operatorname{poly}(N_0)\le N_0\operatorname{poly}(N_0)\). There are at most O(N_0) disjoint residual components. The total count is at most \(2^n\), so it is representable in at most n+1 bits. Local zeta coefficients through degree d have polynomial total output length in N_0+d and are derived from the count by exact integer arithmetic. Hence the total bit complexity is polynomial under the stated conditions. QED.

**Scope caveats:** The cutset is *provided*, not discovered. The algorithm does not provide a polynomial-time search for a suitable separator on arbitrary CNFs. The restriction is checked separately for every conditioned residual, and this class does not cover arbitrary 3-SAT.

## 4. Explicit non-affine, globally connected family

Let s be a separator Boolean variable and, for each i=1,...,k, introduce a private triple \(a_i,b_i,c_i\). Define

\[
F_k=\bigwedge_{i=1}^k(s\lor a_i\lor b_i\lor c_i).
\]

The global primal graph is connected through s. Condition on S={s}:

- If s=1, all k clauses are satisfied, and the remaining 3k variables are free: \(2^{3k}=8^k\) models.
- If s=0, each component is the **non-affine** triple clause \(a_i\lor b_i\lor c_i\), with exactly 7 satisfying assignments, and the k components are independent: \(7^k\) models.

Thus,

\[
\boxed{\#F_k=8^k+7^k.}
\]

For k>=1 this is not the model count of an affine solution space on the same 3k+1 variables (an affine solution space has either 0 or a power-of-two number of models). The family is therefore **genuinely outside the affine subclass**, but is exactly countable in polynomial time by the supplied separator and 3-variable component counting.

The M11 arithmetic zeta of its quadratic encoding is

\[
\boxed{\zeta_{X_{F_k}}(s)=\zeta(s)^{8^k+7^k}}.
\]

This is a result for this *restricted family*, not for general SAT. Any claim that this resolves P vs NP would be invalid.

## 5. Mixed large affine and non-affine components

A globally connected formula may contain both the guarded non-affine petals above and a large guarded XOR chain:

\[
(s\lor x_i\lor x_{i+1})\land
(s\lor\neg x_i\lor\neg x_{i+1}),
\]

for each consecutive pair in a chain of t variables. With s=0, the two clauses enforce \(x_i\oplus x_{i+1}=1\); the full consistent chain has rank t-1, hence exactly **two** models. With s=1, all t chain variables are unconstrained.

With k independent non-affine petals and a guarded XOR chain of t variables sharing s, the exact total is

\[
\#F_{k,t}=2^{3k+t}+2\cdot7^k.
\]

The method can count the large chain via rank without exponential enumeration, while counting each small non-affine petal independently.

## 6. Implementation and verification

- `cutset_zeta_sat.py`: validates inputs and the logarithmic separator bound, enumerates cutset assignments, constructs exact residual components, counts affine components via `affine_zeta_profile`, uses independent bounded counting for residuals of <=b variables, tracks metrics and declines unsupported inputs. The output includes the exact local zeta coefficients derived from #SAT.
- `test_cutset_zeta_sat.py`: independent Boolean truth tables, seeded small CNFs, zero-variable/empty-clause cases, duplicate/tautological and isolated-variable cases, explicit 100-petal count \(2^{300}+7^{100}\), a 120-variable guarded affine chain, mixed components, unsupported large residuals and oversized separators.
- `.github/workflows/m13-cutset-zeta.yml`: full M10–M13 independent regression suite and Python compilation checks.

**Reproduce:**

```sh
python -m unittest -v test_cutset_zeta_sat.py test_affine_zeta_sat.py test_zeta_sat.py test_rh_grh_bridge.py
```

**Evidence status at authorship:** Code and tests pushed to the research branch. Treat test results as unverified until an actual GitHub Actions run reports success. Finite verification does not prove the general theorem; the theorem above is a mathematical derivation with an explicit polynomial-time contract.

## 7. Falsification criteria and next gap

1. Find a counted small CNF for which the returned count differs from independent enumeration, including duplicated literals, tautologies, branches with forced contradictions, or free variables.
2. Find an accepted formula whose cutset or a non-affine residual violates the logarithmic bound, or an unrecognized affine component silently treated as UNSAT.
3. Audit actual time and memory costs on the adversarial guarded families as instance sizes increase; experimental runtimes do not prove a worst-case bound.
4. To resolve P=NP, prove that an equivalent polynomial-time procedure accepts **every** CNF input without falling back to exponentially large cutsets or non-affine components. No such theorem is established. To resolve P!=NP, a general superpolynomial lower bound against **all** polynomial-time SAT algorithms would be required. No such theorem is established.

## Established literature, not a novelty claim

- Bayardo and Pehoushek (2000), *Counting Models Using Connected Components*, AAAI: https://cdn.aaai.org/AAAI/2000/AAAI00-024.pdf
- Dechter and Mateescu et al., *AND/OR Cutset Conditioning*, IJCAI 2005: https://ijcai.org/proceedings/2005/220
- Martin Dyer et al., discussion of affine exact Boolean counting, https://eprints.whiterose.ac.uk/id/eprint/7981/1/Martin_Dyer_1.pdf
- M12: `AFFINE_ZETA_M12_2026_11_23.md` in this repository.

**M13 result:** Exact counting on a strictly larger structural subclass than the recognized affine formulas, with a constructive polynomial-time guarantee and explicit refusal of unsupported inputs. Neither RH nor GRH changes the general proof obligation.
