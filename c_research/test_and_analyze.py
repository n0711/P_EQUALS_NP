"""Exhaustive independent decision checks (stdlib only)."""
import itertools,json,random,subprocess,tempfile,pathlib,sys
def verify(n, clauses, a):
    return len(a)==n and all(any(a[abs(l)-1] == (l>0) for l in c) for c in clauses)
def run(binary,n,clauses):
    with tempfile.TemporaryDirectory() as td:
        path=pathlib.Path(td)/"test.cnf"
        path.write_text(f"p cnf {n} {len(clauses)}\n"+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
        return json.loads(subprocess.check_output([binary,str(path)],text=True,timeout=15))
def main():
    binary=str(pathlib.Path(sys.argv[1]).resolve())
    rng=random.Random(20261031)
    records=[]
    for n in range(1,9):
        for k in range(30):
            clauses=[tuple(rng.choice([v for v in range(-n,n+1) if v]) for _ in range(rng.randrange(4))) for _ in range(rng.randrange(12))]
            actual=run(binary,n,clauses)
            oracle=any(verify(n,clauses,a) for a in itertools.product((False,True),repeat=n))
            if actual['sat']!=oracle: raise AssertionError((n,k,clauses,actual))
            records.append(dict(n=n,case=k,**actual))
    out={'seed':20261031,'oracle_checked':len(records),'results':records}
    pathlib.Path(__file__).with_name("c_sat_results.json").write_text(json.dumps(out,indent=2))
    print("PASS",len(records),"independent exhaustive oracle checks")
    for n in range(1,9):
        sample=[r for r in records if r['n']==n]
        print("n=",n,"mean_calls=",round(sum(x['calls'] for x in sample)/len(sample),2),"max_calls=",max(x['calls'] for x in sample))
    print("Finite tests do not establish polynomial worst-case complexity.")
if __name__=="__main__":main()
