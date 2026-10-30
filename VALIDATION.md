# Validation record

Date: 30 October 2026. Runtime: Node.js v24.22.1 on Windows.

`node --test`: **14 tests passed, 0 failed** after adding the matrix collection.

- All 4,096 directed simple graphs on four vertices, every start/goal pair: 65,536 cases per search method. BFS, bidirectional BFS and A* matched Bellman-Ford distances. DFS matched reachability. Returned paths were checked against graph edges.
- 100 weighted graphs using seed 20261030, eight vertices each, all start/goal pairs: 12,800 Dijkstra/A* results matched independently calculated distances, including randomly chosen admissible lower bounds.
- Specific tests cover inconsistent heuristics and reopening, zero costs, stale priority entries, unreachable goals, cycles, duplicate edges, invalid values, arithmetic overflow, and a 30,000-vertex DFS chain.
- Every collected distance matched the search implementation. Undirected Laplacians matched B diag(weights) B transpose and were symmetric. All Laplacian row sums were zero.
- Every 4x4 grid distance equaled Manhattan distance. Missing edges and zero-cost edges remained distinct in matrix representations.

`node demo.mjs` generated `results.json`. Its exact operation counts are summarized in `README.md`. No claim about wall-clock superiority is made.

`node collect-matrices.mjs` generated five graph descriptions, five JSON matrix bundles, 45 CSV matrices, and an index. An additional export check parsed every CSV back into values and compared them with the corresponding JSON matrix and regenerated source data; all matched. Graph descriptions and index size were also checked.

These tests are evidence about the implementation and exported examples. General algorithm guarantees depend on the assumptions and arguments in `README.md` and `RESEARCH_NOTES.md`; finite tests do not establish a complexity-class equality.
