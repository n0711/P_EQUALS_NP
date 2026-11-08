# PELAOS graph-search workspace

Working implementation and research notes for Charalampos Nadiotis / PELAOS Tech.
Started 30 October 2026. This repository implements established algorithms and documents their correctness and limitations. It does not claim a new algorithm or a proof that P = NP.

## Paper and licence

Read the [compiled paper](paper/graph-search.pdf) or its [XeLaTeX source](paper/graph-search.tex). The source is authoritative; rebuild the PDF after source changes. Author: Charalampos Nadiotis, PELAOS Tech. The manuscript and its source are licensed under the ROS3-derived [Civilian-Use Licence (No Military Use), Version 1.0](MANUSCRIPT_LICENCE.md), also printed in the paper's appendix. This manuscript licence does not grant a new software licence.

Repository: [n0711/P_EQUALS_NP](https://github.com/n0711/P_EQUALS_NP).

## Run locally

Node.js 20 or newer; no downloaded packages required. From this directory:

```powershell
node --test
node demo.mjs
node collect-matrices.mjs
```

`demo.mjs` writes deterministic operation counts to `results.json`.
`collect-matrices.mjs` creates the local `matrices/` collection and its index.
No files are uploaded or published by these scripts.

## Implementation

| Method | Implementation choices | Guarantee |
| --- | --- | --- |
| BFS | Array queue with a head index; mark on insertion; parent pointers | Shortest path on unit-cost graphs |
| DFS | Explicit stack of traversal frames; visited tracking; parent pointers | Reachability and a path; not necessarily shortest |
| Bidirectional BFS | Expand the smaller frontier by whole layers; reverse edges for the goal-side search | Shortest path on unit-cost directed or undirected graphs |
| A* | Binary min-heap; cache heuristic values; skip obsolete entries; reopen improved vertices | Minimum-cost path if the heuristic is admissible |
| Dijkstra | A* with h = 0 | Minimum-cost path with nonnegative costs |

These are practical improvements over naive implementations. BFS and DFS already have optimal worst-case linear traversal bounds for explicit adjacency-list graphs. We do not claim to improve their general asymptotic bounds.

```javascript
import { Graph, astar, bfs, dfs, bidirectionalBfs } from './search.mjs';

// Vertices are integers 0 through vertexCount - 1. Edges: [from, to, cost].
const weighted = new Graph(3, [[0, 1, 2], [1, 2, 3], [0, 2, 10]]);
console.log(astar(weighted, 0, 2)); // path [0, 1, 2], cost 5

const unit = new Graph(4, [[0, 1], [1, 2], [2, 3], [0, 3]], { directed: false });
console.log(bfs(unit, 0, 3).path); // [0, 3]
console.log(dfs(unit, 0, 3).path); // [0, 1, 2, 3], adjacency order matters
console.log(bidirectionalBfs(unit, 0, 3).path); // [0, 3]
```

For A*, pass `heuristic(vertex, goal)` as the fourth argument. It must be a deterministic nonnegative lower bound on remaining cost and be zero at the goal. Admissibility is a caller obligation: runtime validation checks values, not the mathematical lower-bound property. A test demonstrates how an overestimate can return a suboptimal path. Inconsistent admissible heuristics are supported by reopening vertices.

Costs and heuristic values must be nonnegative safe integers. Arithmetic that leaves JavaScript's exact integer range throws an error. This version does not support negative weights, arbitrary precision, fractional weights, infinite graphs, or dynamic changes to a graph. The graph's adjacency lists are immutable after construction. Unreachable results have `path: null`, `found: false`, `cost: Infinity` in memory; JSON data uses `null` for unreachable distances.

## Complexity and measurement

Let V and E be the vertex and adjacency-entry counts, including both directions for undirected edges. Graph construction, validation, and reverse adjacency require O(V + E) time and storage. Each search initializes arrays of length V.

- BFS, DFS, and bidirectional BFS: O(V + E) worst-case time; O(V) auxiliary storage in addition to the graph. BFS's queue retains processed entries until the search returns, still O(V).
- A* with a consistent heuristic, including Dijkstra: O(V + (E + 1) log(E + 2)) time and O(V + E) auxiliary storage with this lazy-duplicate heap, assuming O(1) heuristic evaluations. Each vertex expands at most once. If heuristic evaluation is more expensive, add the total cost of computing it.
- A* with an inconsistent admissible heuristic: reopening preserves correctness but the preceding expansion bound no longer applies. Count repeated expansions and heuristic computation in any complexity claim.

These are ordinary RAM-model operation bounds with representable integers, not a bit-complexity analysis for unbounded integers.

Metrics count processing of the goal as an expansion, even though its outgoing edges are not scanned. `examinedEdges` counts actual adjacency scans. `discovered` counts first discovery per search direction, so bidirectional BFS can count a vertex twice. `peakFrontier` measures stored work entries: pending queue entries for BFS, active frames for DFS, heap entries including stale entries for A*, and retained current/next layer entries for bidirectional BFS. It is not total memory or a directly interchangeable measure across algorithms.

## Reproducible observations

The demo uses unit-cost, four-neighbor, undirected grids. A* uses Manhattan distance, a consistent heuristic under these conditions. Equal A* priorities prefer larger g, then insertion order.

| Scenario | Method | Path cost | Expanded |
| --- | --- | ---: | ---: |
| Open 40 x 40 | BFS | 78 | 1600 |
| Open 40 x 40 | DFS | 1560 | 1561 |
| Open 40 x 40 | Bidirectional BFS | 78 | 1560 |
| Open 40 x 40 | A*, Manhattan | 78 | 79 |
| Alternating wall gaps | BFS | 300 | 1366 |
| Alternating wall gaps | DFS | 872 | 1361 |
| Alternating wall gaps | Bidirectional BFS | 300 | 1359 |
| Alternating wall gaps | A*, Manhattan | 300 | 1239 |

The open-grid result depends strongly on the heuristic and tie breaking. The wall example demonstrates a weaker gain and a larger A* frontier. Fewer expansions are not a wall-clock speedup claim; preprocessing and heuristic costs matter. Neither scenario establishes a worst-case improvement for SAT.

## Validation and research

`search.test.mjs` checks all 4,096 directed simple graphs on four vertices, each with all 16 start/goal pairs. BFS, bidirectional BFS, and A* distances are compared to independent Bellman-Ford relaxation; DFS reachability and returned paths are checked. Another 100 seeded weighted graphs exercise zero costs and admissible heuristics. Additional cases cover reopening, stale heap entries, invalid inputs, parallel edges, overflow, and a 30,000-vertex DFS chain.

Read [RESEARCH_NOTES.md](RESEARCH_NOTES.md) for correctness arguments and the SAT connection, and [MATRICES.md](MATRICES.md) for matrix definitions and formats.

Primary A* reference: Peter E. Hart, Nils J. Nilsson, Bertram Raphael (1968), [A Formal Basis for the Heuristic Determination of Minimum Cost Paths](https://www.cs.auckland.ac.nz/courses/compsci709s2c/resources/Mike.d/astarNilsson.pdf). The original paper treats positive-cost graphs; this finite-graph implementation also supports zero-cost edges with strict cost improvements.


## New research milestone - exact component SAT (7 November 2026)

[COMPONENT_FACTORIZATION_2026_11_07.md](COMPONENT_FACTORIZATION_2026_11_07.md) establishes the standard exact factorization and counting identity for disconnected CNF components, and a polynomial guarantee **only** when component size is O(log N) under the explicit-input convention. [component_sat.py](component_sat.py) implements independent-component DPLL and verified model reconstruction. The regression suite [test_component_sat.py](test_component_sat.py) passed six test methods locally, including 640 independent truth-table checks and 210 variable-renaming checks.

Run: python -m unittest -v test_component_sat.py

This result does not prove P = NP and does not claim new complexity-theoretic priority. It maintains the attribution to Charalampos Nadiotis's earlier ResearchGate work while clearly distinguishing that work from the 2026 OpenAI ETH preprint.


## Graph-theoretic SAT milestone - separator conditioning (7 November 2026)

[GRAPH_SEPARATOR_RESEARCH_2026_11_07.md](GRAPH_SEPARATOR_RESEARCH_2026_11_07.md) documents an exact, deterministic [graph_separator_sat.py](graph_separator_sat.py) prototype. It builds the CNF primal graph, searches one- and two-variable separators, conditions on those assignments, independently solves disconnected components, memoizes exact residuals, and verifies witnesses. This follows established cutset-conditioning / AND-OR search ideas and does **not** prove P = NP or claim mathematical novelty.

Reproduce:

```sh
python -m unittest -v test_graph_separator_sat.py
python run_graph_separator_benchmark.py > graph-separator-results.json
```

The local run passed nine methods, including 900 seeded independent small-CNF oracle checks and 210 variable-renaming tests. Eighteen deterministic benchmark instances agreed with the DPLL baseline. Runtime improvement is **not** claimed: graph inspection can be slower than direct DPLL on easy examples. The SAT verification GitHub Actions job includes the tests and saves benchmark data as a workflow artifact.


## Research milestone ledger and XeLaTeX paper (M5, 7 November 2026)

The cumulative [RESEARCH_MILESTONES.md](RESEARCH_MILESTONES.md) records every milestone with dated hypotheses, scoped mathematical statements, implementation commits, experiments, independent verification status, adverse results, and the next falsification gate. The separate [XeLaTeX working manuscript](paper/structural-sat-milestones.tex) integrates the results as they are validated. The original [graph-search paper](paper/graph-search.tex) remains unchanged.

Milestone M5 adds [structural_hybrid_sat.py](structural_hybrid_sat.py), which conservatively recognizes complete XOR CNF blocks of width up to three and solves recognized systems over GF(2), otherwise using the exact [graph-separator solver](graph_separator_sat.py). [graph_research_instances.py](graph_research_instances.py) generates connected cubic Tseitin, pigeonhole 3-CNF and graph-coloring instances and measures primal graph width bounds. [test_structural_hybrid_sat.py](test_structural_hybrid_sat.py) is the independent finite regression suite. [run_structural_benchmark.py](run_structural_benchmark.py) runs bounded comparisons (DPLL, graph separator, hybrid), preserving separate timeout, limit and UNSAT statuses.

Reproduce with:
- `python -m unittest -v test_structural_hybrid_sat.py`
- `python run_structural_benchmark.py --quick --timeout-seconds 3 --max-calls 1200 > structural-results.json`
- `cd paper && xelatex structural-sat-milestones.tex && xelatex structural-sat-milestones.tex`

**Verification and novelty boundary:** This is a reproducible implementation of established affine SAT / AND-OR graph methods, not an unconditional polynomial-time SAT solver. Update the ledger and manuscript only with explicitly verified outcomes.


## M6 - Literal polarity and identical primal graph counterfamilies (7 November 2026)

[RESEARCH_MILESTONES.md](RESEARCH_MILESTONES.md) records the M6 theorem, experimental evidence and falsification criteria. The [XeLaTeX research manuscript](paper/structural-sat-milestones.tex) includes the mathematical proof.

Three explicit 3-CNF families share the complete primal graph K_n but have different SAT statuses: all-positive triples are SAT, all eight sign patterns on every triple are UNSAT, and all-positive plus all-negative triples are SAT exactly for n=3,4. Therefore connectivity/treewidth alone do not determine satisfiability. [dense_cnf_families.py](dense_cnf_families.py) generates the cases, and [polarity_sat.py](polarity_sat.py) implements standard exact unit/pure-literal preprocessing and complete-support contradiction detection, falling back to the previous affine/graph solver when needed. This does not provide a general polynomial-time SAT algorithm.

Run the tests and benchmark:

```sh
python -m unittest -v test_polarity_sat.py
python run_polarity_benchmark.py --quick --timeout-seconds 3 --max-calls 1800 > m6-polarity-results.json
```

A GitHub Actions workflow runs M6 alongside the earlier SAT regression suites and archives the benchmark JSON. See the milestone ledger for the verified run ID, not merely the existence of a test file.
