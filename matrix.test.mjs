import test from 'node:test';
import assert from 'node:assert/strict';
import { Graph, astar, bfs, bidirectionalBfs } from './search.mjs';
import { buildMatrices, examples } from './matrix-data.mjs';

test('every collected distance agrees with search and every Laplacian row sums to zero', () => {
  for (const spec of examples) {
    const matrices = buildMatrices(spec);
    const graph = new Graph(spec.vertexCount, spec.edges, { directed: spec.directed });
    for (let u = 0; u < graph.size; u++) {
      assert.equal(matrices.laplacian[u].reduce((a, b) => a + b, 0), 0);
      for (let v = 0; v < graph.size; v++) {
        const expected = matrices.shortest_paths[u][v] ?? Infinity;
        assert.equal(astar(graph, u, v).cost, expected);
        if (graph.unitWeight) {
          assert.equal(bfs(graph, u, v).cost, expected);
          assert.equal(bidirectionalBfs(graph, u, v).cost, expected);
        }
        assert.equal(matrices.reachability[u][v], Number(expected !== Infinity));
      }
    }
  }
});

test('undirected weighted Laplacian equals B diag(weights) B transpose', () => {
  for (const spec of examples.filter(example => !example.directed)) {
    const { incidence: b, laplacian: l } = buildMatrices(spec);
    for (let u = 0; u < spec.vertexCount; u++) for (let v = 0; v < spec.vertexCount; v++) {
      const product = spec.edges.reduce((sum, edge, e) => sum + b[u][e] * (edge[2] ?? 1) * b[v][e], 0);
      assert.equal(l[u][v], product);
      assert.equal(l[u][v], l[v][u]);
    }
  }
});

test('zero-cost edges, parallel edges, self loops and missing edges remain distinct', () => {
  const m = buildMatrices({ vertexCount: 3, directed: false, edges: [[0, 1, 0], [0, 1, 5], [1, 1, 2]] });
  assert.equal(m.adjacency[0][1], 1);
  assert.equal(m.edge_multiplicity[0][1], 2);
  assert.equal(m.weight_sum[0][1], 5);
  assert.equal(m.min_edge_cost[0][1], 0);
  assert.equal(m.shortest_paths[0][1], 0);
  assert.equal(m.min_edge_cost[0][2], null);
  assert.equal(m.shortest_paths[0][2], null);
  assert.equal(m.shortest_paths[2][2], 0);
  assert.ok(m.incidence.every(row => row[2] === 0));
  assert.deepEqual(m.laplacian, [[5, -5, 0], [-5, 5, 0], [0, 0, 0]]);
});

test('4x4 grid distances equal Manhattan distances', () => {
  const spec = examples.find(example => example.id === 'grid_four_by_four');
  const m = buildMatrices(spec);
  for (let u = 0; u < 16; u++) for (let v = 0; v < 16; v++) {
    const expected = Math.abs(u % 4 - v % 4) + Math.abs(Math.floor(u / 4) - Math.floor(v / 4));
    assert.equal(m.shortest_paths[u][v], expected);
  }
});
