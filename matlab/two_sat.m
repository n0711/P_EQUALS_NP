function [sat, assignment] = two_sat(n, clauses)
%TWO_SAT Polynomial-time 2-CNF solver using implication reachability.
% clauses is a cell array, e.g. {[1 -2], [-1 2], [1]}.
% Result sat is logical; assignment is n-by-1 logical (empty if UNSAT).
% Time O(n^3 + m) using dense transitive closure; O(n^2) memory.
% This proves no claim about unrestricted CNF-SAT or P versus NP.
if ~isscalar(n) || n < 0 || n ~= floor(n)
    error('n must be a nonnegative integer');
end
if ~iscell(clauses)
    error('clauses must be a cell array');
end
N = 2*n;
reach = false(N,N);
for j = 1:N
    reach(j,j) = true;
end
for j = 1:numel(clauses)
    c = clauses{j};
    if ~isnumeric(c) || numel(c) > 2 || any(c == 0) || ...
            any(abs(c) > n) || any(c ~= fix(c))
        error('Each clause needs 0, 1, or 2 signed literals in 1..n');
    end
    if isempty(c)
        sat = false; assignment = false(0,1); return;
    end
    a = c(1);
    b = c(end);
    reach(node(-a),node(b)) = true;
    reach(node(-b),node(a)) = true;
end
for k = 1:N
    reach = reach | (reach(:,k) & reach(k,:));
end
for v = 1:n
    if reach(2*v-1,2*v) && reach(2*v,2*v-1)
        sat = false; assignment = false(0,1); return;
    end
end
% SCC condensation topological priority from number of reachable components.
% If literal p reaches not-p, p cannot be true. Reachability determines
% ordering of distinct SCCs; reverse topological assignment is sufficient.
% Compute SCCs and topologically order them using DFS on implication graph.
adj = reach; % Reachability closure retains the same SCC DAG direction.
seen = false(1,N); order = zeros(1,N); count = 0;
for v = 1:N
    if ~seen(v)
        visit(v);
    end
end
component = zeros(1,N); cid = 0;
for j = N:-1:1
    v = order(j);
    if component(v) == 0
        cid = cid + 1;
        stack = v;
        component(v) = cid;
        while ~isempty(stack)
            w = stack(end); stack(end) = [];
            neighbors = find(adj(:,w))';
            for z = neighbors
                if component(z) == 0
                    component(z) = cid;
                    stack(end+1) = z; %#ok<AGROW>
                end
            end
        end
    end
end
assignment = false(n,1);
for v = 1:n
    assignment(v) = component(2*v-1) > component(2*v);
end
sat = true;
for j = 1:numel(clauses)
    c = clauses{j};
    if ~any(arrayfun(@(lit) assignment(abs(lit)) == (lit > 0),c))
        error('Internal model verification failed');
    end
end
    function ix = node(lit)
        ix = 2*(abs(lit)-1) + 1 + (lit < 0);
    end
    function visit(v)
        seen(v) = true;
        for w = find(adj(v,:))
            if ~seen(w)
                visit(w);
            end
        end
        count = count + 1;
        order(count) = v;
    end
end
