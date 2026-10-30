import test from 'node:test';
import assert from 'node:assert/strict';
import { Graph, astar, bfs, dfs, dijkstra, bidirectionalBfs } from './search.mjs';

// Independent reference: repeated edge relaxation, no priority queue.
function bellmanFord(graph, start) {
  const distance = new Array(graph.size).fill(Infinity);
  distance[start] = 0;
  for (let pass = 1; pass < graph.size; pass++) {
    let changed = false;
    for (let from = 0; from < graph.size; from++) {
      for (const { to, cost } of graph.adj[from]) {
        if (distance[from] + cost < distance[to]) {
          distance[to] = distance[from] + cost;
          changed = true;
        }
      }
    }
    if (!changed) break;
  }
  return distance;
}

function validatePath(graph, start, goal, answer) {
  if (!answer.found) {
    assert.equal(answer.path, null);
    assert.equal(answer.cost, Infinity);
    return;
  }
  assert.equal(answer.path[0], start);
  assert.equal(answer.path.at(-1), goal);
  assert.equal(new Set(answer.path).size, answer.path.length);
  let cost = 0;
  for (let i = 1; i < answer.path.length; i++) {
    const edges = graph.adj[answer.path[i - 1]].filter(edge => edge.to === answer.path[i]);
    assert.ok(edges.length > 0, 'Every path step must be an edge');
    // Random reference tests use at most one edge per ordered vertex pair.
    cost += Math.min(...edges.map(edge => edge.cost));
  }
  assert.equal(answer.cost, cost);
}

test('empty paths, unreachable goals, cycles, and directed reverse traversal', () => {
  const graph = new Graph(5, [[0, 1], [1, 2], [2, 0], [2, 3]]);
  for (const search of [bfs, dfs, astar, dijkstra, bidirectionalBfs]) {
    assert.deepEqual(search(graph, 2, 2).path, [2]);
    assert.equal(search(graph, 0, 4).found, false);
    assert.equal(search(graph, 3, 0).found, false);
    const answer = search(graph, 0, 3);
    assert.equal(answer.cost, 3);
    validatePath(graph, 0, 3, answer);
  }
});

test('weighted optimum differs from minimum hop count', () => {
  const graph = new Graph(3, [[0, 2, 10], [0, 1, 2], [1, 2, 3]]);
  assert.equal(astar(graph, 0, 2).cost, 5);
  assert.throws(() => bfs(graph, 0, 2), /unit/);
  assert.throws(() => bidirectionalBfs(graph, 0, 2), /unit/);
});

test('A* reopens a vertex for an admissible but inconsistent heuristic', () => {
  // S=0, A=1, B=2, G=3. A is first reached at cost 3, then at cost 2.
  const graph = new Graph(4, [[0, 1, 3], [0, 2, 1], [2, 1, 1], [1, 3, 3]]);
  const h = [0, 0, 4, 0];
  const answer = astar(graph, 0, 3, node => h[node]);
  assert.deepEqual(answer.path, [0, 2, 1, 3]);
  assert.equal(answer.cost, 5);
  assert.equal(answer.stats.reopened, 1);
});

test('stale heap entries and zero-cost cycles do not cause extra expansion', () => {
  const graph = new Graph(5, [[0, 1, 9], [0, 2, 1], [2, 1, 1], [1, 2, 0], [1, 1, 0]]);
  const answer = astar(graph, 0, 4);
  assert.equal(answer.found, false);
  assert.equal(answer.stats.stalePops, 1);
  assert.equal(answer.stats.expanded, 3);
});

test('DFS is iterative and can return a longer path than BFS', () => {
  const graph = new Graph(5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]]);
  assert.equal(dfs(graph, 0, 4).cost, 4);
  assert.equal(bfs(graph, 0, 4).cost, 1);
  const n = 30000;
  const chain = new Graph(n, Array.from({ length: n - 1 }, (_, i) => [i, i + 1]));
  assert.equal(dfs(chain, 0, n - 1).path.length, n);
});

test('all directed simple graphs on four vertices, every start/goal pair', () => {
  const possible = [];
  for (let u = 0; u < 4; u++) for (let v = 0; v < 4; v++) if (u !== v) possible.push([u, v]);
  for (let mask = 0; mask < 2 ** possible.length; mask++) {
    const graph = new Graph(4, possible.filter((_, bit) => mask & (1 << bit)));
    for (let start = 0; start < 4; start++) {
      const truth = bellmanFord(graph, start);
      for (let goal = 0; goal < 4; goal++) {
        for (const search of [bfs, bidirectionalBfs, astar]) {
          const answer = search(graph, start, goal);
          assert.equal(answer.cost, truth[goal], `${search.name}, graph=${mask}, ${start}->${goal}`);
          validatePath(graph, start, goal, answer);
        }
        const answer = dfs(graph, start, goal);
        assert.equal(answer.found, truth[goal] !== Infinity);
        validatePath(graph, start, goal, answer);
      }
    }
  }
});

test('seeded weighted graphs agree with independent shortest-path reference', () => {
  let seed = 20261030;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 2 ** 32; };
  for (let trial = 0; trial < 100; trial++) {
    const n = 8;
    const edges = [];
    for (let u = 0; u < n; u++) for (let v = 0; v < n; v++) {
      if (random() < 0.22) edges.push([u, v, Math.floor(random() * 10)]);
    }
    const graph = new Graph(n, edges);
    const truth = Array.from({ length: n }, (_, start) => bellmanFord(graph, start));
    for (let goal = 0; goal < n; goal++) {
      // Lower bounds obtained from independent exact distances; can be inconsistent.
      const h = truth.map(row => Number.isFinite(row[goal]) ? Math.floor(row[goal] * random()) : 0);
      for (let start = 0; start < n; start++) {
        for (const answer of [dijkstra(graph, start, goal), astar(graph, start, goal, node => h[node])]) {
          assert.equal(answer.cost, truth[start][goal]);
          validatePath(graph, start, goal, answer);
        }
      }
    }
  }
});

test('invalid vertices, costs, heuristics and arithmetic overflow are rejected', () => {
  assert.throws(() => new Graph(-1), /vertexCount/);
  assert.throws(() => new Graph(2, [[0, 2]]), /vertex/);
  for (const cost of [-1, 1.5, Infinity, NaN]) assert.throws(() => new Graph(2, [[0, 1, cost]]), /cost/);
  const graph = new Graph(2, [[0, 1]]);
  assert.throws(() => bfs(graph, -1, 1), /vertex/);
  assert.throws(() => astar(graph, 0, 1, () => 1), /goal/);
  assert.throws(() => astar(graph, 0, 1, node => node === 1 ? 0 : -1), /heuristic/);
  const huge = new Graph(3, [[0, 1, Number.MAX_SAFE_INTEGER], [1, 2, 1]]);
  assert.throws(() => astar(huge, 0, 2), /exact integer/);
});

test('parallel edges, self loops, undirected construction and deterministic ties', () => {
  const graph = new Graph(3, [[0, 0, 0], [0, 1, 7], [0, 1, 2], [1, 2, 1]], { directed: false });
  assert.equal(astar(graph, 2, 0).cost, 3);
  const diamond = new Graph(4, [[0, 1], [0, 2], [1, 3], [2, 3]]);
  assert.deepEqual(astar(diamond, 0, 3).path, astar(diamond, 0, 3).path);
});

test('overestimating a heuristic can lose optimality: documented caller obligation', () => {
  const graph = new Graph(3, [[0, 2, 10], [0, 1, 1], [1, 2, 1]]);
  assert.equal(astar(graph, 0, 2, node => node === 1 ? 100 : 0).cost, 10);
  assert.equal(dijkstra(graph, 0, 2).cost, 2);
});
