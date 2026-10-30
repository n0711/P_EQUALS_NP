# Local graph matrix collection

Created for the graph-search work on 30 October 2026. These are generated illustrative examples, not downloaded data or an external benchmark collection. Regenerate with `node collect-matrices.mjs`. Files stay in this project's `matrices/` directory.

## Graphs and files

| Directory | Vertices | Input edges | Purpose |
| --- | ---: | ---: | --- |
| `directed_diamond` | 4 | 4 | Equal-length routes, directed traversal |
| `astar_reopening` | 4 | 4 | Weighted paths, admissible inconsistent heuristic |
| `weighted_disconnected` | 6 | 5 | Weighted undirected graph, isolated vertex |
| `cycle_five` | 5 | 5 | Unit-cost cycle |
| `grid_four_by_four` | 16 | 24 | Four-neighbor grid, Manhattan heuristic |

Each graph directory contains its source `graph.json`, all nine matrices together in `matrices.json`, and nine CSV files. `matrices/index.json` records graph sizes and every matrix's dimensions. Undirected edges appear once in `graph.json`; adjacency representations contain both directions. Input-edge order determines incidence-column order.

Rows are source vertex IDs and columns are destination IDs except for the incidence matrix, whose columns are edge IDs `e0`, `e1`, etc. CSVs have a header and a first column named `vertex`. JSON uses `null` for an absent minimum-cost edge or unreachable distance; CSV uses `INF`. A diagonal shortest-path distance is always zero because an empty path is allowed. A missing diagonal edge remains `null` in `min_edge_cost`.

## Definitions

| Matrix/file name | Meaning |
| --- | --- |
| `adjacency` | Binary A: A[u,v] = 1 exactly when an edge u -> v exists |
| `edge_multiplicity` | Number of input edges connecting each ordered pair, mirrored for undirected graphs |
| `weight_sum` | W[u,v]: sum of edge weights between u and v; zero if absent |
| `min_edge_cost` | Cheapest individual edge cost between u and v; absent edges are null/INF |
| `incidence` | B[u,e] = -1 at an edge's source, +1 at its destination; self-loop columns are zero |
| `weighted_degree` | Diagonal D with D[u,u] = sum_v W[u,v] |
| `laplacian` | L = D - W; directed examples use the out-degree convention |
| `reachability` | R[u,v] = 1 when a path exists, including length-zero paths |
| `shortest_paths` | Minimum total edge cost for every ordered vertex pair |

`weight_sum` is useful for graph algebra, but is not a shortest-path cost matrix when parallel edges exist. Shortest paths use `min_edge_cost`. Binary adjacency and multiplicity distinguish zero-cost edges from missing edges, which W alone cannot do.

For undirected graphs the orientation used in B is arbitrary. With C the diagonal matrix of input-edge weights, L = B C B^T. Consequently L is symmetric and x^T L x = sum_e w_e (x_v - x_u)^2 >= 0. For directed graphs D - W need not be symmetric; B C B^T instead represents the corresponding undirected edge collection and is not generally the directed L. Self-loop weights cancel from D - W under the stated row-sum convention.

## Reading a matrix

The weighted A* reopening example has minimum-edge matrix:

```text
      0    1    2    3
0   INF    3    1  INF
1   INF  INF  INF    3
2   INF    1  INF  INF
3   INF  INF  INF  INF
```

The shortest route from 0 to 3 is 0 -> 2 -> 1 -> 3, cost 5. The heuristic [0, 0, 4, 0] is admissible but inconsistent on 2 -> 1: 4 > 1 + 0. A* initially expands vertex 1 at cost 3, then must reopen it at cost 2.

In PowerShell, CSVs can be loaded with `Import-Csv`, and JSON with `Get-Content -Raw ... | ConvertFrom-Json`. Spreadsheet software can open the CSV files directly; `INF` remains a text marker.

## Validation and cost

`matrix.test.mjs` checks all collected shortest-path distances against A*, and against BFS and bidirectional BFS when edge costs are one. Distances are generated independently with Floyd-Warshall. It also checks Laplacian row sums, symmetry and B C B^T for undirected examples, grid Manhattan distances, and the distinction between absent and zero-cost edges.

Dense square matrices require O(V^2) storage. The dense incidence matrix requires O(V E) storage. Floyd-Warshall uses O(V^3) time. These formats suit these small examples; larger graph collections should use sparse edge lists or sparse matrices and compute only the distances needed. Generating a dense all-pairs matrix is not an optimization for a single A* query.
