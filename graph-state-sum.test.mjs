import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sudokuGraph,projectColoring,stateSum,countColorings} from './graph-state-sum.mjs';

function sudokuRowOracle4(clues={}) {
  const rows=[];
  function perm(a){if(a.length===4){rows.push(a);return;}for(let c=0;c<4;c++)if(!a.includes(c))perm([...a,c]);}
  perm([]);let total=0n;
  for(const r0 of rows)for(const r1 of rows)for(const r2 of rows)for(const r3 of rows){
    const a=[r0,r1,r2,r3].flat();
    if(Object.entries(clues).some(([k,v])=>a[Number(k)]!==v))continue;
    if([0,1,2,3].some(c=>new Set([a[c],a[4+c],a[8+c],a[12+c]]).size!==4))continue;
    if([0,2,8,10].some(i=>new Set([a[i],a[i+1],a[i+4],a[i+5]]).size!==4))continue;
    total++;
  }
  return total;
}

function audit(eq,throws) {
  const g=sudokuGraph(2);eq(g.n,16);eq(g.edges.length,56);
  const g9=sudokuGraph(3);eq(g9.edges.length,810);
  const net=projectColoring(g.n,g.edges);eq(net.vertices.length,168);eq(net.links.length,208);eq(Math.max(...net.vertices.map(v=>v.ports.length)),3);
  const net9=projectColoring(g9.n,g9.edges);eq(Math.max(...net9.vertices.map(v=>v.ports.length)),3);
  let cases=0;
  // Every simple graph on three labelled vertices, two palette sizes, three clue cases.
  const all=[[0,1],[0,2],[1,2]];
  for(let mask=0;mask<8;mask++)for(const q of [2,3])for(const clues of [{},{0:0},{0:0,1:0}]){
    const edges=all.filter((_,i)=>mask&(1<<i));
    eq(stateSum(projectColoring(3,edges,clues),q).total,countColorings(3,edges,q,clues));cases++;
  }
  eq(stateSum(projectColoring(2,[[0,1]]),2,[[2,3],[5,7]]).total,29n);
  eq(stateSum(projectColoring(1,[]),3).total,3n);
  eq(stateSum(projectColoring(0,[]),3).total,1n);
  throws(()=>stateSum(net,4));throws(()=>projectColoring(2,[[0,1],[1,0]]));throws(()=>stateSum(projectColoring(1,[],{0:2}),2));
  const observations=[];
  for(const clues of [{},{0:0},{0:0,1:0},{0:0,5:3}]){
    const count=countColorings(g.n,g.edges,g.q,clues);eq(count,sudokuRowOracle4(clues));observations.push(String(count));
  }
  eq(observations.join(","),"288,72,0,24");
  return {smallGraphCases:cases,sudokuCounts:observations,weightedEdge:"29",sudoku4:{vertices:net.vertices.length,edges:net.links.length},sudoku9:{vertices:net9.vertices.length,edges:net9.links.length}};
}

test('graph state-sum projection and Sudoku oracle',()=>{audit(assert.equal,assert.throws);});
