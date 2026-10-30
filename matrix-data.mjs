import { Graph } from './search.mjs';

const square = n => Array.from({ length: n }, () => new Array(n).fill(0));
function exactSum(a, b) {
  const value = a + b;
  if (!Number.isSafeInteger(value)) throw new RangeError('Matrix arithmetic exceeds exact integer range');
  return value;
}

export function buildMatrices(spec) {
  const { vertexCount: n, edges, directed = true } = spec;
  // Reuse graph input validation; matrices are constructed independently below.
  new Graph(n, edges, { directed });
  const adjacency = square(n);
  const multiplicity = square(n);
  const weights = square(n);
  const minimum = Array.from({ length: n }, () => new Array(n).fill(Infinity));
  const incidence = Array.from({ length: n }, () => new Array(edges.length).fill(0));
  function insert(u, v, w) {
    adjacency[u][v] = 1;
    multiplicity[u][v]++;
    weights[u][v] = exactSum(weights[u][v], w);
    minimum[u][v] = Math.min(minimum[u][v], w);
  }
  edges.forEach(([u, v, w = 1], column) => {
    insert(u, v, w);
    if (!directed && u !== v) insert(v, u, w);
    incidence[u][column] -= 1;
    incidence[v][column] += 1;
  });
  const degree = square(n);
  for (let u = 0; u < n; u++) degree[u][u] = weights[u].reduce(exactSum, 0);
  const laplacian = weights.map((row, u) => row.map((w, v) => degree[u][v] - w));
  const distance = minimum.map((row, u) => row.map((w, v) => u === v ? 0 : w));
  // Floyd-Warshall is independent of the graph-search implementation.
  for (let k = 0; k < n; k++) for (let u = 0; u < n; u++) for (let v = 0; v < n; v++) {
    if (distance[u][k] !== Infinity && distance[k][v] !== Infinity) {
      distance[u][v] = Math.min(distance[u][v], exactSum(distance[u][k], distance[k][v]));
    }
  }
  const reachability = distance.map(row => row.map(value => Number.isFinite(value) ? 1 : 0));
  const nullable = matrix => matrix.map(row => row.map(value => value === Infinity ? null : value));
  return {
    adjacency,
    edge_multiplicity: multiplicity,
    weight_sum: weights,
    min_edge_cost: nullable(minimum),
    incidence,
    weighted_degree: degree,
    laplacian,
    reachability,
    shortest_paths: nullable(distance),
  };
}

const gridEdges = [];
for (let row = 0; row < 4; row++) for (let col = 0; col < 4; col++) {
  const u = row * 4 + col;
  if (col < 3) gridEdges.push([u, u + 1, 1]);
  if (row < 3) gridEdges.push([u, u + 4, 1]);
}

export const examples = [
  {
    id: 'directed_diamond', vertexCount: 4, directed: true,
    description: 'Two equal-length routes; deterministic path selection and reverse traversal.',
    edges: [[0, 1, 1], [0, 2, 1], [1, 3, 1], [2, 3, 1]],
  },
  {
    id: 'astar_reopening', vertexCount: 4, directed: true,
    description: 'Admissible inconsistent heuristic h=[0,0,4,0] for goal 3 requires reopening vertex 1.',
    heuristic: [0, 0, 4, 0], goal: 3,
    edges: [[0, 1, 3], [0, 2, 1], [2, 1, 1], [1, 3, 3]],
  },
  {
    id: 'weighted_disconnected', vertexCount: 6, directed: false,
    description: 'Weighted undirected graph with isolated vertex 5; unreachable paths and a symmetric Laplacian.',
    edges: [[0, 1, 2], [1, 2, 3], [2, 0, 4], [2, 3, 1], [3, 4, 2]],
  },
  {
    id: 'cycle_five', vertexCount: 5, directed: false,
    description: 'Five-vertex unit-cost cycle for traversal and graph algebra.',
    edges: [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 4, 1], [4, 0, 1]],
  },
  {
    id: 'grid_four_by_four', vertexCount: 16, directed: false,
    description: 'Four-neighbor 4x4 grid, row-major numbering; Manhattan distance equals shortest-path distance.',
    edges: gridEdges,
  },
];
