# Chapter 16 — P vs NP

> "Some problems you can solve quickly. Some you can only check quickly. Whether those are the same thing is the million-dollar question — literally."

## Learning objectives

By the end of this chapter you will be able to:

- State what P and NP mean, both informally and in terms of Turing machines.
- Recognize NP-complete problems in the wild and understand what "NP-complete" implies for algorithm design.
- Distinguish "NP-hard" from "impossible" and know what practical options you have.
- Explain why a resolution of P vs. NP would reshape cryptography, optimization, and science.
- Perform a polynomial-time reduction on paper.

## Prerequisites & recap

- [Big-O](03-big-o.md) — you need to be comfortable with polynomial vs.
  exponential growth rates.
- [Exponential time](05-exponential-time.md) — the algorithms that P vs. NP
  is about.

## The simple version

Think of a jigsaw puzzle. Putting it together might take hours — you try
piece after piece, and there's no obvious shortcut. But *checking* whether a
completed puzzle is correct takes seconds: you look at the picture and see
if everything fits. P vs. NP asks: if you can check a solution quickly, does
that mean you can also *find* one quickly?

**P** is the class of problems you can *solve* in polynomial time (fast).
**NP** is the class of problems where you can *verify* a proposed solution
in polynomial time. Every problem in P is automatically in NP (if you can
solve it fast, you can verify by solving it again). The open question is
whether the reverse is true — can every problem whose solution is easy to
check also be solved fast?

Most computer scientists believe P ≠ NP: some problems are fundamentally
harder to solve than to check. But nobody has proved it yet. It's the
biggest open question in computer science, and the Clay Mathematics
Institute offers \$1,000,000 for a proof either way.

## Visual flow

```
  ┌───────────────────────────────────────┐
  │                NP-hard                │
  │  ┌─────────────────────────────────┐  │
  │  │          NP                     │  │
  │  │  ┌───────────────────────────┐  │  │
  │  │  │        NP-complete        │  │  │
  │  │  │  SAT, TSP, Knapsack,     │  │  │
  │  │  │  Graph Coloring, ...     │  │  │
  │  │  └───────────────────────────┘  │  │
  │  │                                 │  │
  │  │  ┌───────────────────┐          │  │
  │  │  │       P           │          │  │
  │  │  │  Sorting, search, │          │  │
  │  │  │  shortest path,   │          │  │
  │  │  │  primality, ...   │          │  │
  │  │  └───────────────────┘          │  │
  │  └─────────────────────────────────┘  │
  │                                       │
  │  Halting problem (undecidable)        │
  └───────────────────────────────────────┘

  If P = NP, the P and NP-complete regions merge.
  If P ≠ NP (widely believed), they stay separate.
```

## Concept deep-dive

### P — the "easy" problems

**P** (Polynomial time) is the class of decision problems solvable by a
deterministic Turing machine in O(n^k) time for some constant k. In
practical terms: problems with algorithms that run in polynomial time.

Examples in P:

- **Sorting** — O(n log n).
- **Shortest path** — Dijkstra in O((V + E) log V).
- **Primality testing** — AKS algorithm, O(n^6) where n = number of digits.
  (Before 2002, people weren't sure this was in P.)
- **Maximum flow** — various polynomial algorithms.
- **Linear programming** — ellipsoid method and interior-point methods.

### NP — the "checkable" problems

**NP** (Nondeterministic Polynomial time) is the class of decision problems
where a proposed solution (a "certificate") can be *verified* in polynomial
time.

The name comes from the Turing machine model: a nondeterministic machine can
"guess" the right certificate in one step, then verify it in polynomial time.
For a deterministic machine, the verification is polynomial but the
finding might not be.

**Every problem in P is also in NP.** If you can solve it in polynomial
time, you can verify by re-solving. The question is whether NP contains
problems that are *not* in P.

### NP-complete — the hardest in NP

A problem is **NP-complete** if:

1. It's in NP (solutions can be verified in polynomial time).
2. Every other NP problem can be *reduced* to it in polynomial time.

NP-complete problems are the "hardest" problems in NP. If you find a
polynomial-time algorithm for *any one* of them, then *every* NP problem
has a polynomial-time algorithm — and P = NP.

Classic NP-complete problems:

| Problem | Statement |
|---|---|
| **SAT** (Boolean satisfiability) | Given a Boolean formula, is there an assignment of variables that makes it true? (Cook-Levin theorem, 1971 — the first NP-complete problem.) |
| **3-SAT** | SAT restricted to clauses of exactly 3 literals. Still NP-complete. |
| **Traveling Salesman (decision)** | Is there a tour visiting all cities with total distance ≤ k? |
| **Hamiltonian path** | Is there a path visiting every node exactly once? |
| **Graph coloring (≥ 3 colors)** | Can you color a graph with k colors such that no adjacent nodes share a color? |
| **Knapsack** | Can you select items with total weight ≤ W and total value ≥ V? |
| **Subset sum** | Is there a subset of integers that sums to exactly T? |
| **Clique** | Does the graph contain a complete subgraph of size k? |
| **Vertex cover** | Can you cover all edges with at most k vertices? |

### NP-hard — at least as hard as NP-complete

A problem is **NP-hard** if every NP problem reduces to it — but it doesn't
have to be *in* NP itself. NP-hard problems might not even be decidable.

- The **halting problem** is NP-hard (every NP problem reduces to it) but
  it's *undecidable* — no algorithm solves it at all, let alone in
  polynomial time.
- The **optimization version of TSP** ("find the shortest tour") is NP-hard
  but technically not in NP because the question isn't a yes/no decision
  problem. (The decision version — "is there a tour ≤ k?" — is NP-complete.)

**"NP-hard" does not mean "unsolvable."** It means no known polynomial-time
algorithm exists. You might still solve it for small inputs, or approximate
it closely.

### Reductions — the key technique

A reduction from problem A to problem B means: "if I can solve B, I can
solve A." You transform an instance of A into an instance of B in polynomial
time, solve B, and map the answer back.

To prove a new problem X is NP-complete:

1. **Show X ∈ NP:** given a candidate solution, verify it in polynomial time.
2. **Reduce a known NP-complete problem to X:** show that a solver for X
   would also solve the known problem.

### Why P vs. NP matters

**If P = NP:**

- Every problem whose solution you can check quickly, you can also *find*
  quickly.
- **Cryptography collapses.** RSA, ECC, and most public-key crypto rely on
  the assumption that certain problems (factoring, discrete log) are hard to
  solve but easy to verify. If P = NP, those problems have polynomial-time
  solutions.
- **Optimization becomes easy.** Logistics, scheduling, protein folding,
  circuit design — all the NP-hard problems we approximate today would have
  exact, fast solutions.
- **Automatic theorem proving becomes tractable.** Checking a proof is in P;
  if P = NP, *finding* proofs is too.

**If P ≠ NP (widely believed):**

- Hard problems stay hard. Cryptography stays secure (modulo quantum
  computing advances).
- We continue to rely on approximation algorithms, heuristics, and
  constraint solvers for NP-hard problems.
- The world stays as it is.

### What you do in practice when you hit NP-hard

You don't give up. You:

1. **Reduce the problem size.** Many NP-hard problems are tractable for small
   n. Subset sum with n = 20? Brute-force 2²⁰ ≈ 1 million — easy.
2. **Approximate.** Many NP-hard problems have polynomial-time approximation
   algorithms with provable guarantees. Vertex cover has a 2-approximation.
   TSP has a 1.5-approximation (Christofides).
3. **Use heuristics.** Greedy algorithms, simulated annealing, genetic
   algorithms — no guarantees, but often good in practice.
4. **Use a SAT/ILP solver.** Modern SAT solvers (MiniSat, CaDiCaL) and
   Integer Linear Programming solvers (Gurobi, CPLEX) handle millions of
   variables on many real-world instances, despite the worst-case
   complexity.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| Brute force for small n | Simple, correct, exponential time | Only when n is small enough (≤ ~20–25 for 2^n, ≤ ~10 for n!) |
| Approximation algorithm | Polynomial time, provable quality bound | When you need a guarantee (e.g., "within 2× of optimal") |
| Heuristic (greedy, SA) | Fast, no guarantee on quality | When "good enough" is fine and speed matters |
| SAT / ILP solver | Surprisingly fast on structured instances | When the problem can be naturally encoded as constraints |
| Dynamic programming (pseudo-polynomial) | Polynomial in n × W for knapsack; not truly polynomial in input size | When the numbers are bounded (e.g., knapsack with small capacity) |

## Production-quality code

```python
from __future__ import annotations
from itertools import combinations
from typing import Sequence


def subset_sum_brute(
    nums: Sequence[int], target: int
) -> list[int] | None:
    """Brute-force subset sum. O(2^n) — only viable for small n."""
    for r in range(len(nums) + 1):
        for combo in combinations(nums, r):
            if sum(combo) == target:
                return list(combo)
    return None


def subset_sum_dp(
    nums: Sequence[int], target: int
) -> bool:
    """Dynamic-programming subset sum. O(n * target) — pseudo-polynomial.
    Only works for non-negative integers."""
    if target < 0:
        return False
    reachable = [False] * (target + 1)
    reachable[0] = True
    for num in nums:
        for t in range(target, num - 1, -1):
            if reachable[t - num]:
                reachable[t] = True
    return reachable[target]


def tsp_nearest_neighbor(
    dist: list[list[float]],
) -> tuple[list[int], float]:
    """Nearest-neighbor heuristic for TSP. O(n^2).
    Returns (tour, total_distance). Not optimal but fast."""
    n = len(dist)
    visited = [False] * n
    tour = [0]
    visited[0] = True
    total = 0.0

    for _ in range(n - 1):
        current = tour[-1]
        best_next = -1
        best_dist = float("inf")
        for j in range(n):
            if not visited[j] and dist[current][j] < best_dist:
                best_dist = dist[current][j]
                best_next = j
        tour.append(best_next)
        visited[best_next] = True
        total += best_dist

    total += dist[tour[-1]][tour[0]]
    return tour, total


def verify_subset_sum(
    nums: Sequence[int], target: int, certificate: Sequence[int]
) -> bool:
    """Polynomial-time verifier for subset sum.
    Demonstrates that subset sum is in NP."""
    return (
        all(x in nums for x in certificate)
        and len(set(certificate)) == len(certificate)
        and sum(certificate) == target
    )
```

## Security notes

P vs. NP has deep implications for security:

- **If P = NP, public-key cryptography breaks.** RSA relies on the
  assumption that factoring large integers is hard (not known to be in P,
  though not proven NP-complete either). If P = NP, factoring would be
  polynomial.
- **Hash function collision resistance** assumes that finding collisions is
  hard. If P = NP, finding collisions would be easy.
- **In practice:** even if P ≠ NP, quantum computers threaten RSA and ECC
  (Shor's algorithm). Post-quantum cryptography is being standardized to
  address this.

**Practical security note:** when you encounter an NP-hard problem in a
security context (e.g., password cracking by brute force), the hardness is
your friend — it's what makes the attack impractical. Don't weaken it by
reducing the problem size (short passwords) or using weak heuristics.

## Performance notes

| Problem | Brute force | Best known exact | Practical approach |
|---|---|---|---|
| Subset sum (n items) | O(2^n) | O(2^(n/2)) — meet in the middle | DP if target is small; SAT solver otherwise |
| TSP (n cities) | O(n!) | O(n² · 2^n) — Held-Karp DP | Heuristics (nearest neighbor, 2-opt, LKH) |
| SAT (n variables) | O(2^n) | Exponential worst case | CDCL SAT solvers handle millions of vars on structured instances |
| Graph coloring (k colors) | O(k^n) | Exponential | Greedy coloring (approximation), SAT encoding |
| Knapsack (n items, capacity W) | O(2^n) | O(n · W) — pseudo-polynomial DP | DP when W is bounded; FPTAS for arbitrary W |

The gap between worst-case theory and practical performance is enormous for
NP-hard problems. SAT solvers routinely solve instances with millions of
variables because real-world instances have structure that brute-force
analysis ignores.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Treating "NP-hard" as "unsolvable" | Conflating "no known polynomial algorithm" with "can't be solved at all" | Remember: small instances are tractable; approximation and heuristics work well in practice |
| 2 | Claiming a problem "is NP" to mean it's hard | Misusing "NP" as a synonym for "hard" | NP is a *class* of problems. Saying "the problem is NP" means solutions are verifiable in poly time — that includes every problem in P |
| 3 | Believing approximation is always bad | Assuming approximate ≠ useful | Many NP-hard problems have approximation algorithms within 1–2% of optimal. Vertex cover has a 2-approx; TSP has a 1.5-approx |
| 4 | Trying to prove P = NP by implementing a fast SAT solver | Confusing good average-case performance with polynomial worst-case | SAT solvers are fast on *structured* instances, not *all* instances. A polynomial worst-case algorithm is what would prove P = NP |
| 5 | Ignoring pseudo-polynomial algorithms | Dismissing DP approaches because "the problem is NP-hard" | Knapsack DP runs in O(n · W) — polynomial in the *value* of W, exponential in the *size* of W. If W is bounded, it's practical |

## Practice

**Warm-up.** Verify that checking a Sudoku solution is in P: given a filled
9×9 grid, write a function that checks validity in O(1) time (fixed-size
board).

**Standard.** Implement brute-force subset sum for n up to 20. Time it on
inputs of size 10, 15, and 20 and observe the exponential growth.

**Bug hunt.** A colleague claims they can solve TSP for 100 cities in
polynomial time using nearest-neighbor. Explain why this doesn't prove
P = NP.

**Stretch.** Research and summarize one approximation algorithm (e.g.,
the 2-approximation for vertex cover: repeatedly pick an edge, add both
endpoints, remove covered edges). Implement it.

**Stretch++.** Encode a 4×4 Sudoku as a SAT problem and solve it using the
`python-sat` library. Map variables to "cell (r,c) has value v", add
constraints for rows, columns, and boxes.

<details><summary>Show solutions</summary>

**Warm-up:**

```python
def is_valid_sudoku(grid: list[list[int]]) -> bool:
    for i in range(9):
        row = [grid[i][j] for j in range(9)]
        col = [grid[j][i] for j in range(9)]
        if len(set(row)) != 9 or len(set(col)) != 9:
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = [grid[br+r][bc+c] for r in range(3) for c in range(3)]
            if len(set(block)) != 9:
                return False
    return True
```

**Bug hunt:** Nearest-neighbor is a *heuristic*, not an exact algorithm. It
runs in O(n²) and produces a tour, but that tour is not guaranteed to be
optimal — it can be up to O(log n) times worse than the best tour. Proving
P = NP requires a polynomial-time algorithm that finds the *optimal*
solution (or correctly answers the decision problem) on *every* input,
not just gives a "good enough" answer on most inputs.

**Stretch (2-approximation for vertex cover):**

```python
def vertex_cover_2approx(
    edges: list[tuple[str, str]],
) -> set[str]:
    cover: set[str] = set()
    remaining = set(range(len(edges)))
    while remaining:
        idx = next(iter(remaining))
        u, v = edges[idx]
        cover.add(u)
        cover.add(v)
        remaining = {
            i for i in remaining
            if edges[i][0] not in cover and edges[i][1] not in cover
        }
    return cover
```

</details>

## In plain terms (newbie lane)
If `P Vs Np` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. P is:
    (a) problems solvable in polynomial time
    (b) problems only verifiable in polynomial time
    (c) undecidable problems
    (d) problems with infinite solutions

2. NP-complete means:
    (a) impossible to solve
    (b) in NP, and every NP problem reduces to it in polynomial time
    (c) solvable in polynomial time
    (d) always exponential time

3. Is there a known polynomial-time algorithm for SAT?
    (a) Yes — Cook proved one in 1971
    (b) No — Cook proved SAT is NP-complete, not that it's in P
    (c) Yes, but only for 2-SAT
    (d) SAT is undecidable

4. Brute-force TSP for n cities runs in:
    (a) O(n²)  (b) O(n!)  (c) O(log n)  (d) O(n³)

5. If P = NP were proved, it would:
    (a) break RSA and most public-key cryptography
    (b) make every NP problem solvable in polynomial time
    (c) both (a) and (b)
    (d) have no practical consequence

**Short answer:**

6. What is the difference between NP-hard and NP-complete?

7. Why are heuristics and approximation algorithms useful when the exact
   problem is NP-hard?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-c. 6) NP-complete = in NP + every NP problem reduces to it. NP-hard = every NP problem reduces to it, but the problem itself might not be in NP (might not even be decidable). NP-complete is the intersection of NP and NP-hard. 7) Because "NP-hard" is a worst-case statement. Many real-world instances have structure that heuristics exploit. Approximation algorithms provide provable bounds (e.g., "within 2× of optimal") in polynomial time, which is often good enough for practical purposes.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [16-p-vs-np — mini-project](mini-projects/16-p-vs-np-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- **P** = problems solvable in polynomial time. **NP** = problems whose
  solutions are verifiable in polynomial time. Every P problem is in NP.
- **NP-complete** problems are the hardest in NP: solve one in polynomial
  time and you've proved P = NP. Classics: SAT, TSP, knapsack, graph
  coloring.
- **NP-hard** ≠ impossible. Use approximation algorithms, heuristics,
  DP (pseudo-polynomial), or SAT/ILP solvers for practical solutions.
- The P vs. NP question is unresolved. If P = NP, cryptography collapses
  and optimization becomes easy. Most experts believe P ≠ NP.

## Further reading

- *Computers and Intractability: A Guide to the Theory of NP-Completeness*
  (Garey & Johnson) — the definitive catalog of NP-complete problems.
- Scott Aaronson, "P vs. NP" — excellent accessible overview.
- *CLRS* ch. 34 — NP-Completeness.
- Next module: [Module 07 — C Memory](../07-c-memory/README.md).
