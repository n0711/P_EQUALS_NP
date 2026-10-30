import { writeFileSync } from 'node:fs';
import { Graph, astar, bfs, dfs, bidirectionalBfs } from './search.mjs';

function grid(width, height, blocked = new Set()) {
  const edges = [];
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const node = y * width + x;
    if (blocked.has(node)) continue;
    for (const [nx, ny] of [[x + 1, y], [x, y + 1]]) {
      const to = ny * width + nx;
      if (nx < width && ny < height && !blocked.has(to)) edges.push([node, to]);
    }
  }
  return new Graph(width * height, edges, { directed: false });
}

const width = 40;
const height = 40;
const blocked = new Set();
for (let x = 5; x < width - 1; x += 6) {
  const gap = ((x - 5) / 6) % 2 === 0 ? height - 2 : 1;
  for (let y = 0; y < height; y++) if (y !== gap) blocked.add(y * width + x);
}
const scenarios = [
  ['open 40x40 grid', grid(width, height)],
  ['alternating wall gaps', grid(width, height, blocked)],
];
const rows = [];
for (const [scenario, graph] of scenarios) {
  const start = 0;
  const goal = graph.size - 1;
  const manhattan = node => width - 1 - (node % width) + height - 1 - Math.floor(node / width);
  const searches = [
    ['BFS', () => bfs(graph, start, goal)],
    ['DFS', () => dfs(graph, start, goal)],
    ['bidirectional BFS', () => bidirectionalBfs(graph, start, goal)],
    ['A* h=0 (Dijkstra)', () => astar(graph, start, goal)],
    ['A* Manhattan', () => astar(graph, start, goal, manhattan)],
  ];
  for (const [algorithm, run] of searches) {
    const answer = run();
    rows.push({ scenario, algorithm, cost: answer.found ? answer.cost : null, ...answer.stats });
  }
}
console.table(rows);
writeFileSync(new URL('./results.json', import.meta.url), JSON.stringify({
  description: 'Deterministic operation counts, not wall-clock speed claims. Graph construction excluded.',
  rows,
}, null, 2) + '\n');
