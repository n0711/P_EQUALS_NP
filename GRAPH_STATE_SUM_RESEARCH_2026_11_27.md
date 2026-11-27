# Graph state sums and the Sudoku projection (2026-11-27)

Status: exact representation theorem and finite checks; no new general circuit lower bound, P=NP or P!=NP proof. This work is independent of open PR #13 and starts from main.

## A1: literature audit (partial)
- OpenAI, [Paths, trees and grids separate Valiant's hierarchy](https://github.com/openai/math/tree/main/preprints/Paths-trees-and-grids-separate-Valiants-hierarchy-November-24-2026), 24 Nov 2026, intro and README. The authors report a grid state-sum circuit lower bound n^Omega((log n)^(1/12)) and a full arithmetic hierarchy separation. The 24 Nov papers supersede the 23 Nov preprint.
- OpenAI, [Circuit lower bounds for Hamiltonian cycle and the permanent](https://github.com/openai/math/tree/main/preprints/Circuit-lower-bounds-for-Hamiltonian-cycle-and-the-permanent-November-24-2026), 24 Nov 2026, README: eventual exp(Omega((log N)^2/(log log N)^2)) lower bounds for Hamiltonian cycle over all fields, permanent outside characteristic two.
- Anthropic, [VP != VNP over every field](https://github.com/anthropics/formal-math/tree/main/vp-vnp), README: reported eventual m^(c(log m)^(1/3)) bounds for Hamiltonian cycle and permanent (except characteristic two for permanent); authors explicitly distinguish the statement from P vs NP and report no human mathematician has checked the proof.
- Scope: these source excerpts and theorem summaries were inspected, not complete manuscripts or Lean kernel checks. Exact, border and bit complexity must not be conflated.

## A2–A3: explicit specialization
Let G=(V,E) be a finite simple graph with n vertices and m edges, q>=1 colors, and fixed clues. Define the weighted coloring polynomial
C_G(X)=sum_{proper clue-consistent c} prod_{v in V} X[v,c(v)].
Construct a loopless network H: for each incidence (v,e), create an equality node. Chain the incidence nodes belonging to each v, and for each original edge connect its two incidence nodes via a new degree-two inequality node. At one designated incidence of each v put weight X[v,color] and a clue filter. An isolated vertex is represented by a marked unary node joined to a free unary node. Every vertex of H has degree at most three.

Give every network edge a q-valued label. Let generic Z_H be the sum, over edge labelings, of the product of one independent table entry at each network vertex. Specialize each equality table to zero for unequal incident labels, otherwise one (or the designated weight, zero if the clue fails). Specialize inequality tables to the indicator of distinct labels, and free tables to one.

**Proposition (over any field):** this substitution, which maps each independent variable to 0, 1 or a marker variable, gives exactly C_G(X).
Proof: nonzero-compatible labelings propagate one color along each equality chain; inequality nodes enforce all original edges, designated markers enforce clues and contribute exactly one factor per cell. Each valid coloring gives exactly one compatible edge labeling, and vice versa. The two term sums therefore agree as formal polynomials. This is a standard tensor-network encoding, not a novelty claim.

If i vertices are isolated, H has 3m+2i vertices and 4m-n+2i edges: 2m incidence-to-inequality edges, 2m-(n-i) chain edges, and i isolated gadget edges. Hence explicit generic tables need O((n+m)q^3) entries; graph and tables are polynomial in explicit graph size and q. For b-by-b Sudoku blocks, q=b^2, n=q^2 and each cell has degree 3q-2b-1. Thus m=q^2(3q-2b-1)/2 and the generic table count is O(q^6). Our simple pairwise Sudoku graph construction costs O(q^4) comparisons, and the network constructor O(n+m) expected dictionary operations. Polynomial-size input is not polynomial-time contraction.

## A4: circuit bounds and the obstruction
For a fixed network H and a cut of its vertices, the generic coefficient flattening has rank exactly q^k over every field, where k is the number of crossing edges. Rows and columns correspond to products of local table entries on each side. Internal inconsistent assignments give zero rows or columns; the remaining submatrix decomposes into q^k disjoint nonempty all-ones blocks indexed by crossing labels. Each block has rank one. This gives a fixed-cut tensor rank result, not an unrestricted arithmetic circuit size lower bound. Different gates can use different cuts and cancellations.

Specialization proves size(C_G) <= size(Z_H) (up to input conventions); a lower bound on Z_H therefore does NOT give a lower bound on C_G. A reverse polynomial projection from a proven hard family, or a direct lower bound, would be needed. The graph gadget is not the explicit square-grid witness of the cited paper. No such reverse projection is established here.

## A5: Boolean decision transfer
At all marker variables equal to one, the polynomial over the integers gives the number of completions; over positive characteristic counts can cancel. E.g. one isolated vertex with two colors gives 2=0 over F_2 despite being colorable. A coefficient polynomial lower bound is not a lower bound for testing existence of a witness. Even #P-hard counting is not by itself a lower bound for NP decision. Need a uniform bit-complexity-preserving reduction or simulation and a proved lower bound in the appropriate model. RH/GRH is not used here and supplies no such bridge.

## A6–A7: reproducibility and manuscript
Run node --test graph-state-sum.test.mjs (Node >=20) or npm test for all tests. The exact test body was executed in a V8 JS environment before committing. The full repo suite and Node test runner were not executed in that environment. The enumeration function refuses >1,000,000 labelings by default and does not return a false zero on refusal. The graph coloring search is an exponential reference oracle, not a new efficient Sudoku solver. Finite checks: 48 small graph/clue/palette combinations, weighted edge example, degenerate inputs and four 4x4 Sudoku cases independently enumerated by row permutations. 9x9 graph construction checked; no full enumeration of 9x9. See results/graph-state-sum-2026-11-27.json.
Lean formalization not executed or supplied; next prove the labeling/coloring bijection and cut-rank lemma with explicit graph and field definitions. Standalone XeLaTeX milestone draft supplied; not compiled here. No merge of existing PR #13 or claim of novelty.

## Next research gates
1. Reproduce the generic independent-table cut and grid construction (including the paper's variable-cut argument, not just fixed flattenings).
2. Investigate reverse projection via weighted list-coloring gadgets with polynomial blowup; prove coefficient preservation and field conditions or report a counterexample. Such a reduction would still only transfer arithmetic hardness.
3. Specify and audit a Boolean decision reduction independently; test for counting/decision and uniform/nonuniform gaps.
4. Mechanize the projection lemma in Lean and integrate the reviewed milestone into the main manuscript.
