// Standard graph algorithms; this project does not claim their invention.
function nonnegativeInteger(value, label) {
  if (!Number.isSafeInteger(value) || value < 0) {
    throw new RangeError(`${label} must be a nonnegative safe integer`);
  }
}

function add(a, b) {
  const sum = a + b;
  if (!Number.isSafeInteger(sum)) throw new RangeError('Path cost or priority exceeds exact integer range');
  return sum;
}

export class Graph {
  constructor(vertexCount, edges = [], { directed = true } = {}) {
    nonnegativeInteger(vertexCount, 'vertexCount');
    this.size = vertexCount;
    this.adj = Array.from({ length: vertexCount }, () => []);
    this.reverse = Array.from({ length: vertexCount }, () => []);
    this.unitWeight = true;
    const insert = (from, to, cost) => {
      this.adj[from].push(Object.freeze({ to, cost }));
      this.reverse[to].push(Object.freeze({ to: from, cost }));
    };
    for (const [from, to, cost = 1] of edges) {
      this.checkVertex(from);
      this.checkVertex(to);
      nonnegativeInteger(cost, 'edge cost');
      if (cost !== 1) this.unitWeight = false;
      insert(from, to, cost);
      if (!directed && from !== to) insert(to, from, cost);
    }
    for (const list of [...this.adj, ...this.reverse]) Object.freeze(list);
    Object.freeze(this.adj);
    Object.freeze(this.reverse);
    Object.freeze(this);
  }

  checkVertex(vertex) {
    if (!Number.isSafeInteger(vertex) || vertex < 0 || vertex >= this.size) {
      throw new RangeError(`Invalid vertex: ${vertex}`);
    }
  }
}

function initialize(graph, start, goal, unitOnly = false) {
  graph.checkVertex(start);
  graph.checkVertex(goal);
  if (unitOnly && !graph.unitWeight) throw new RangeError('BFS requires unit edge costs; use A* or Dijkstra for weighted paths');
  return { expanded: 0, examinedEdges: 0, discovered: 1, peakFrontier: 1, reopened: 0, stalePops: 0 };
}

function reconstruct(parent, start, goal) {
  const path = [goal];
  while (path.at(-1) !== start) path.push(parent[path.at(-1)]);
  return path.reverse();
}

function result(path, cost, stats) {
  return { found: path !== null, path, cost, stats };
}

export function bfs(graph, start, goal) {
  const stats = initialize(graph, start, goal, true);
  const parent = new Array(graph.size).fill(-1);
  const distance = new Array(graph.size).fill(Infinity);
  distance[start] = 0;
  const queue = [start];
  let head = 0;
  while (head < queue.length) {
    const node = queue[head++];
    stats.expanded++;
    if (node === goal) return result(reconstruct(parent, start, goal), distance[node], stats);
    for (const { to } of graph.adj[node]) {
      stats.examinedEdges++;
      if (distance[to] !== Infinity) continue;
      distance[to] = distance[node] + 1;
      parent[to] = node;
      queue.push(to);
      stats.discovered++;
    }
    stats.peakFrontier = Math.max(stats.peakFrontier, queue.length - head);
  }
  return result(null, Infinity, stats);
}

export function dfs(graph, start, goal) {
  const stats = initialize(graph, start, goal);
  const parent = new Array(graph.size).fill(-1);
  const distance = new Array(graph.size).fill(Infinity);
  distance[start] = 0;
  // Frames preserve recursive DFS adjacency order without the JS call stack.
  const stack = [{ node: start, next: 0 }];
  while (stack.length) {
    const frame = stack.at(-1);
    if (frame.next === 0) {
      stats.expanded++;
      if (frame.node === goal) return result(reconstruct(parent, start, goal), distance[goal], stats);
    }
    if (frame.next === graph.adj[frame.node].length) {
      stack.pop();
      continue;
    }
    const { to, cost } = graph.adj[frame.node][frame.next++];
    stats.examinedEdges++;
    if (distance[to] !== Infinity) continue;
    parent[to] = frame.node;
    distance[to] = add(distance[frame.node], cost);
    stack.push({ node: to, next: 0 });
    stats.discovered++;
    stats.peakFrontier = Math.max(stats.peakFrontier, stack.length);
  }
  return result(null, Infinity, stats);
}

class MinHeap {
  items = [];
  get size() { return this.items.length; }
  less(a, b) { return a.f < b.f || (a.f === b.f && (a.g > b.g || (a.g === b.g && a.order < b.order))); }
  push(item) {
    const a = this.items;
    a.push(item);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!this.less(a[i], a[p])) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }
  pop() {
    const a = this.items;
    const first = a[0];
    const last = a.pop();
    if (a.length) {
      a[0] = last;
      let i = 0;
      while (2 * i + 1 < a.length) {
        let child = 2 * i + 1;
        if (child + 1 < a.length && this.less(a[child + 1], a[child])) child++;
        if (!this.less(a[child], a[i])) break;
        [a[i], a[child]] = [a[child], a[i]];
        i = child;
      }
    }
    return first;
  }
}

export function astar(graph, start, goal, heuristic = () => 0) {
  const stats = initialize(graph, start, goal);
  const cache = new Map();
  const h = node => {
    if (!cache.has(node)) {
      const value = heuristic(node, goal);
      nonnegativeInteger(value, 'heuristic');
      cache.set(node, value);
    }
    return cache.get(node);
  };
  if (h(goal) !== 0) throw new RangeError('Heuristic at the goal must be zero');
  const parent = new Array(graph.size).fill(-1);
  const best = new Array(graph.size).fill(Infinity);
  const expanded = new Set();
  const open = new MinHeap();
  let order = 0;
  best[start] = 0;
  open.push({ node: start, g: 0, f: h(start), order: order++ });
  while (open.size) {
    const { node, g } = open.pop();
    if (g !== best[node]) { stats.stalePops++; continue; }
    if (expanded.has(node)) stats.reopened++;
    expanded.add(node);
    stats.expanded++;
    if (node === goal) return result(reconstruct(parent, start, goal), g, stats);
    for (const { to, cost } of graph.adj[node]) {
      stats.examinedEdges++;
      const candidate = add(g, cost);
      if (candidate >= best[to]) continue;
      if (best[to] === Infinity) stats.discovered++;
      best[to] = candidate;
      parent[to] = node;
      open.push({ node: to, g: candidate, f: add(candidate, h(to)), order: order++ });
    }
    stats.peakFrontier = Math.max(stats.peakFrontier, open.size);
  }
  return result(null, Infinity, stats);
}

export const dijkstra = (graph, start, goal) => astar(graph, start, goal);

export function bidirectionalBfs(graph, start, goal) {
  const stats = initialize(graph, start, goal, true);
  if (start === goal) return result([start], 0, stats);
  const distance = [new Array(graph.size).fill(-1), new Array(graph.size).fill(-1)];
  const parent = [new Array(graph.size).fill(-1), new Array(graph.size).fill(-1)];
  const frontier = [[start], [goal]];
  const adjacency = [graph.adj, graph.reverse];
  distance[0][start] = distance[1][goal] = 0;
  stats.discovered = stats.peakFrontier = 2;
  while (frontier[0].length && frontier[1].length) {
    const side = frontier[0].length <= frontier[1].length ? 0 : 1;
    const other = 1 - side;
    const next = [];
    let meeting = -1;
    let cost = Infinity;
    // Finish the entire layer and choose its cheapest intersection.
    for (const node of frontier[side]) {
      stats.expanded++;
      for (const { to } of adjacency[side][node]) {
        stats.examinedEdges++;
        if (distance[side][to] !== -1) continue;
        distance[side][to] = distance[side][node] + 1;
        parent[side][to] = node;
        next.push(to);
        stats.discovered++;
        if (distance[other][to] !== -1) {
          const candidate = distance[side][to] + distance[other][to];
          if (candidate < cost) { cost = candidate; meeting = to; }
        }
      }
    }
    stats.peakFrontier = Math.max(stats.peakFrontier, frontier[0].length + frontier[1].length + next.length);
    frontier[side] = next;
    if (meeting !== -1) {
      const path = reconstruct(parent[0], start, meeting);
      for (let node = meeting; node !== goal;) {
        node = parent[1][node];
        path.push(node);
      }
      return result(path, cost, stats);
    }
  }
  return result(null, Infinity, stats);
}
