import { mkdirSync, writeFileSync } from 'node:fs';
import { buildMatrices, examples } from './matrix-data.mjs';

const root = new URL('./matrices/', import.meta.url);
mkdirSync(root, { recursive: true });
const index = {
  provenance: 'Locally generated illustrative graphs. Not an external benchmark dataset.',
  conventions: 'See ../MATRICES.md. Rows/columns use vertex IDs; incidence columns use edge-list order. null/INF denotes no finite distance or absent edge.',
  examples: [],
};
for (const spec of examples) {
  const directory = new URL(`${spec.id}/`, root);
  mkdirSync(directory, { recursive: true });
  const matrices = buildMatrices(spec);
  writeFileSync(new URL('graph.json', directory), JSON.stringify(spec, null, 2) + '\n');
  writeFileSync(new URL('matrices.json', directory), JSON.stringify(matrices, null, 2) + '\n');
  const dimensions = {};
  for (const [name, matrix] of Object.entries(matrices)) {
    const columns = name === 'incidence' ? spec.edges.length : spec.vertexCount;
    dimensions[name] = [spec.vertexCount, columns];
    const header = ['vertex', ...Array.from({ length: columns }, (_, i) => name === 'incidence' ? `e${i}` : String(i))];
    const rows = matrix.map((row, i) => [i, ...row.map(value => value === null ? 'INF' : value)]);
    writeFileSync(new URL(`${name}.csv`, directory), [header, ...rows].map(row => row.join(',')).join('\n') + '\n');
  }
  index.examples.push({ id: spec.id, vertexCount: spec.vertexCount, edgeCount: spec.edges.length, directed: spec.directed, dimensions });
}
writeFileSync(new URL('index.json', root), JSON.stringify(index, null, 2) + '\n');
console.log(`Saved ${examples.length} graphs, ${examples.length * 9} CSV matrices, and JSON equivalents to ${root.pathname}`);
