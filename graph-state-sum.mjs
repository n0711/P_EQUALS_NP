// Exact reference implementation; enumeration is intentionally bounded, not a polynomial solver.
export function sudokuGraph(b) {
  if (!Number.isSafeInteger(b) || b < 1) throw new Error("invalid block size");
  const q=b*b, n=q*q, edges=[];
  for(let u=0;u<n;u++) for(let v=u+1;v<n;v++){
    const r=Math.floor(u/q), s=Math.floor(v/q), c=u%q, d=v%q;
    if(r===s || c===d || (Math.floor(r/b)===Math.floor(s/b)&&Math.floor(c/b)===Math.floor(d/b))) edges.push([u,v]);
  }
  return {n,edges,q};
}

export function projectColoring(n,edges,clues={}) {
  if(!Number.isSafeInteger(n)||n<0) throw new Error("invalid vertex count");
  const seen=new Set(), ports=Array.from({length:n},()=>[]), vertices=[], links=[];
  const node=(kind,cell=null,marker=false)=>{vertices.push({kind,cell,marker,ports:[]});return vertices.length-1;};
  const link=(a,b)=>{const i=links.length;links.push([a,b]);vertices[a].ports.push(i);vertices[b].ports.push(i);};
  for(const [u,v] of edges){
    if(!Number.isInteger(u)||!Number.isInteger(v)||u<0||v<0||u>=n||v>=n||u===v) throw new Error("invalid edge");
    const key=[Math.min(u,v),Math.max(u,v)].join(",");
    if(seen.has(key)) throw new Error("duplicate edge");seen.add(key);
    const a=node("eq",u,ports[u].length===0), b=node("eq",v,ports[v].length===0), t=node("neq");
    ports[u].push(a);ports[v].push(b);link(a,t);link(b,t);
  }
  for(let u=0;u<n;u++){
    if(!ports[u].length){const a=node("eq",u,true);link(a,node("free"));ports[u].push(a);}
    for(let j=1;j<ports[u].length;j++)link(ports[u][j-1],ports[u][j]);
  }
  for(const [k,v] of Object.entries(clues)) if(!/^(0|[1-9]\d*)$/.test(k)||Number(k)>=n||!Number.isInteger(v)||v<0) throw new Error("invalid clue");
  return {vertices,links,clues:{...clues}};
}

export function stateSum(net,q,weights=null,limit=1000000) {
  if(!Number.isSafeInteger(q)||q<1||!Number.isSafeInteger(limit)||limit<1)throw new Error("invalid parameters");
  for(const c of Object.values(net.clues))if(c>=q)throw new Error("clue out of range");
  let total=0n, visits=0;const a=Array(net.links.length).fill(0);
  if(BigInt(q)**BigInt(a.length)>BigInt(limit))throw new Error("enumeration limit");
  function visit(i){
    if(i<a.length){for(let c=0;c<q;c++){a[i]=c;visit(i+1);}return;}
    visits++;let term=1n;
    for(const v of net.vertices){
      const x=v.ports.map(p=>a[p]), c=x[0];
      if(v.kind==="neq"&&x[0]===x[1])return;
      if(v.kind==="eq"&&x.some(t=>t!==c))return;
      if(v.marker){if(Object.hasOwn(net.clues,v.cell)&&net.clues[v.cell]!==c)return;
        if(weights!==null)term*=BigInt(weights[v.cell][c]);}
    }
    total+=term;
  }
  visit(0);return {total,visits};
}

export function countColorings(n,edges,q,clues={}) {
  if(!Number.isSafeInteger(q)||q<1)throw new Error("invalid q");
  projectColoring(n,edges,clues); // validate graph and clues
  for(const c of Object.values(clues))if(c>=q)throw new Error("clue out of range");
  const adj=Array.from({length:n},()=>[]);
  for(const [u,v] of edges){adj[u].push(v);adj[v].push(u);}
  const a=Array(n).fill(-1);let total=0n;
  function visit(u){
    if(u===n){total++;return;}
    const fixed=Object.hasOwn(clues,u);
    for(let c=0;c<q;c++){
      if((fixed&&clues[u]!==c)||adj[u].some(v=>a[v]===c))continue;
      a[u]=c;visit(u+1);a[u]=-1;
    }
  }
  visit(0);return total;
}
