# Milestone: exact clause-frontier representation and a falsifiable width bound

Date: 2026-11-02. Status: tested research prototype; **not** a proof of P=NP.

## Formal representation

Let F be a CNF of n variables and m non-tautological distinct clauses. Fix a permutation pi of the variables. For cut t (the first t variables processed), a clause is *active* when it contains at least one processed and at least one unprocessed variable. A frontier state is the bitmask of **already satisfied** active clauses. Every clause whose final variable has been assigned must be satisfied; a failing transition is rejected. States with identical bitmasks are merged, keeping one concrete partial-assignment witness.

Transition at variable v: (i) OR the incoming active-satisfaction mask with the bitmask of clauses made true by v's chosen value, (ii) reject if any clause closing at this step is still false, and (iii) mask out every clause that is not active after the step. This evaluates **two successors per reached state**, not all 2^n full assignments. Tautologies and duplicate clauses are removed without changing satisfiability. The empty clause is immediately UNSAT.

### Exactness invariant

At each cut, a stored frontier mask exists **if and only if** there is a partial assignment to the processed variables that satisfies all closed clauses and has exactly that satisfaction pattern on the active clauses. Proof by induction: the empty prefix has the empty state. Assigning the next variable makes precisely the clauses containing its satisfied literal true. If a clause closes false, no extension can repair it. Conversely, every viable extension is represented by one of the two transitions. Dropping satisfied information about closed clauses is sound because these clauses cannot be affected by remaining variables. Two prefixes with equal active masks have the same future feasibility because all other clauses are either closed and satisfied or untouched. At the final cut, every clause is closed, so a surviving empty state corresponds exactly to a satisfying full assignment. A saved partial witness for each state yields a verified model; an empty set of states proves UNSAT.

### Upper bound, including state processing

Let N be the input's finite bit length, and let w be the maximum number of active clauses at any cut for the chosen order. At cut t there are at most 2^w masks, so the sum of generated distinct layer states is at most (n+1)2^w; attempted transitions are at most 2n2^w. Each state key uses at most m bits and each stored witness at most n bits. Precomputing masks and frontier metadata takes polynomial time and space. Dictionary/hashing, mask operations, clause normalization, validation, and reconstruction all have polynomial bit cost per transition. Consequently:

    Time = O(poly(N) * 2^w)
    Space = O(poly(N) * 2^w)

The implementation uses optional resource ceilings; a limit returns status `limit_states` or `limit_seconds` and **no SAT/UNSAT decision**. The formal exact algorithm is the same procedure without those ceilings.

If w=O(log N), time and space are polynomial, for that structural class and a supplied variable order. This is a parameterized guarantee, **not** a general polynomial bound: w can be Omega(n) and Omega(m).

### Explicit obstruction to a universal polynomial bound for this algorithm/order

For F_k=AND_{i=1}^k (x_i OR y_i), order x_1,...,x_k,y_1,...,y_k. Exactly 2^k different active-clause satisfaction masks are reachable immediately after the x-block. No clause has closed, and each x_i independently determines whether its corresponding crossing clause is already satisfied. Hence this implemented fixed-order frontier DP has at least 2^k states at that layer. Explicit CNF input length is Theta(k log(k+1)) with conventional binary variable IDs; the state count is superpolynomial in input length. Interleaving (x_1,y_1,...,x_k,y_k) instead has frontier width 1 and at most two states. This is **not** a lower bound on all variable orders or SAT algorithms.

## Local experiment (2026-11-02)

Run: `python -m unittest -v test_frontier_sat.py`; `python run_frontier_benchmark.py --max-states 100000 --max-seconds 8 > frontier-results.json`. Five test methods passed, including 560 seeded small-CNF instances checked by an exhaustive independent truth-assignment oracle (0..7 variables), explicit witnesses, tautology/empty-clause cases, resource limits, and the adversarial paired-clause family. The full production `sat.py` in the repository provides validation and witness verification.

| Family and order | k | max active clauses | peak frontier states | elapsed seconds |
| --- | ---: | ---: | ---: | ---: |
| disjoint pairs, grouped | 4 | 4 | 16 | 0.0003 |
| disjoint pairs, interleaved | 4 | 1 | 2 | 0.0002 |
| disjoint pairs, grouped | 8 | 8 | 256 | 0.0067 |
| disjoint pairs, interleaved | 8 | 1 | 2 | 0.0003 |
| disjoint pairs, grouped | 12 | 12 | 4,096 | 0.2181 |
| disjoint pairs, interleaved | 12 | 1 | 2 | 0.0006 |
| disjoint pairs, grouped | 16 | 16 | 65,536 | 4.0215 |
| disjoint pairs, interleaved | 16 | 1 | 2 | 0.0009 |

Also sampled 9 seeded 3-CNFs with n in {8,10,12}, 4n generated clauses, seeds 101/202/303. Their measured peak states ranged from 10 to 72, with computed max active clause width 21 to 34. This illustrates that the 2^w bound can be loose, **not** that arbitrary instances are polynomial. Numbers are a single local run; tracemalloc measures tracked Python allocations, not total resident memory. Local timing depends on hardware and test instrumentation. These are measured counts rather than fitted complexity laws.

## Relationship to prior results

This is a standard width-parameterized style of dynamic programming, not a new general SAT solution. Existing compilation research identifies both polynomially representable structured CNFs and exponential-size OBDD families (Bova & Slivovsky, *Theory of Computing Systems*, 2016, DOI: 10.1007/s00224-016-9715-z). Ordered BDD lower bounds do not automatically transfer to arbitrary decision-only SAT methods. See also `PROOF_STATUS.md` and `HYBRID_EFSA_LITERATURE_PLAN.md`.

## Next falsifiable gate

1. Check the same exact method against more UNSAT benchmark families and independent certificates when available; oracle truth tables only scale to small n.
2. Add measured variable-order construction cost, compare fixed, interleaved, and a predeclared polynomial-time order heuristic on reproducible instance families.
3. Attempt a rigorous general bound on **both** the width/number of states and the cost of finding/recognizing the representation. A valid counterfamily rejects that bound for the specified algorithm; it does not settle P versus NP.

## Connected 3-CNF surviving polarity preprocessing

For k ≥ 2, use variables x₁,…,xₖ, y₁,…,yₖ and z. For each i include
(xᵢ ∨ yᵢ ∨ z) and (¬xᵢ ∨ ¬yᵢ ∨ ¬z). For each i < j include
(xᵢ ∨ xⱼ ∨ z). This gives 2k + 1 variables and 2k + k(k−1)/2 clauses.
The x variables and z induce a clique of size k+1, giving primal treewidth
at least k. Every variable occurs in both polarities. All clauses have
width three and each support carries at most two patterns. Consequently
polarity preprocessing leaves the whole formula intact and the implemented
complete XOR-block recognizer declines it.

Process all x variables first, then z, then all y variables. At the x cut
no clause has closed. The satisfaction bit of each positive diagonal clause
equals its xᵢ, so the frontier contains exactly 2^k distinct states there.

Even merging prefixes with identical suffix truth functions cannot compress
that cut. Set z true, set yᵢ true and set every other y false. This suffix
satisfies the formula exactly when xᵢ is false. Choosing any coordinate on
which two prefixes differ therefore distinguishes them. A decision procedure
can still find a model immediately by setting z true and every y false.

The explicit encoding has O(k² log k) bits, so 2^k grows faster than any
polynomial in that length. The obstruction applies to processing this prefix
while preserving exact suffix behavior. It gives no lower bound for other
orders or for deciding unrestricted SAT.

| k | Clauses | States at x cut (exact) | Peak over full run (measured) |
| ---: | ---: | ---: | ---: |
| 4 | 14 | 16 | 20 |
| 8 | 44 | 256 | 264 |
| 12 | 90 | 4096 | 4108 |

Reproduce the measured column from the repository root:

```python
from dense_cnf_families import guarded_frontier_family
from frontier_sat import frontier_sat

for k in (4, 8, 12):
    n, clauses = guarded_frontier_family(k)
    order = [*range(1, k + 1), n, *range(k + 1, n)]
    model, stats = frontier_sat(n, clauses, order)
    assert stats["status"] == "completed" and model is not None
    print(k, len(clauses), stats["peak_states"])
```
