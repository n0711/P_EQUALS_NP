# M14 — Residual linear-form rank and exact SAT counting

For an explicitly represented mixed system Ax=b over GF(2) and CNF B(x), first eliminate A. If inconsistent the count is zero. Otherwise write x=x0+Vy, where V has independent columns and d=n-r free coordinates. For each variable appearing in B, collect the corresponding row of V into a matrix W. Let q=rank(W).

Theorem: #SAT(A AND B)=2^(d-q) times the number of accepted assignments to q independent residual coordinates.

Proof: Select q independent rows U of W. The map y -> Uy is surjective onto GF(2)^q and every fiber has exactly 2^(d-q) elements by rank-nullity. Every row of W is a linear combination of U, so every literal in B is constant on each fiber (including its offset from x0 and sign). Evaluate B once per fiber and sum the common fiber sizes. This proves the identity, including q=0 and empty residual clauses.

Algorithm: Gaussian elimination on A, compute V, select independent rows of W, express all residual rows in that basis, enumerate q-bit vectors and evaluate residual clauses using parity operations. No expanded CNF conversion is necessary. Bit complexity is 2^q poly(N) for explicit variable representation and input bit length N. The exact count has at most n+1 bits. In particular q=O(log N) is sufficient for polynomial time. The M11 arithmetic zeta exponent equals this count without RH.

Example: n free variables, no affine constraints, B=(x1 OR x2 OR x3). q=3, seven accepted vectors, count=7*2^(n-3). With equality constraints x1=x2=x3, q=1 and one accepted vector, count=2^(n-r-1).

Boundary: arbitrary CNF with A empty and every variable appearing has q=n. Thus this bound alone does not establish P=NP. It also supplies no universal lower bound. The theorem uses standard linear algebra, not a new result about RH. Implementation and independent tests remain future work; this note is a mathematical derivation, not execution evidence.
