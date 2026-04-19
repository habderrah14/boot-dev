# Chapter 05 — Exponential Time

> "Some problems get exponentially harder as inputs grow. Recognizing them is how you avoid burning a week on an algorithm that would take a century to run."

## Learning objectives

By the end of this chapter you will be able to:

- Recognize O(2ⁿ) and O(n!) patterns in recursive code.
- Explain *why* naive Fibonacci is exponential and how memoization collapses it to O(n).
- Identify overlapping subproblems — the key condition for dynamic programming.
- Know the classic exponential problems: Fibonacci, subset sum, Towers of Hanoi, TSP.
- Choose the right strategy when exact solutions are infeasible: heuristics, approximation, branch-and-bound.

## Prerequisites & recap

- [Chapter 03 — Big-O Analysis](03-big-o.md) — you need to reason about recurrence relations.
- [Recursion](../05-fp/04-recursion.md) — all examples here are recursive.

## The simple version

Some problems have a search space that doubles (or worse) with every additional element in the input. If you're checking all subsets of n items, there are 2ⁿ subsets. If you're checking all orderings, there are n! permutations. For n = 20, 2²⁰ is about a million — manageable. For n = 60, 2⁶⁰ is about a quintillion — more operations than any computer can finish in a human lifetime.

The good news: many exponential problems have structure you can exploit. If the same sub-calculation appears repeatedly (overlapping subproblems), you can cache the result and skip the re-work. This is memoization — and it's the simplest form of dynamic programming. It can collapse an O(2ⁿ) algorithm into O(n) or O(n²). The bad news: some problems are genuinely hard (NP-hard), and no known technique avoids exponential time in the worst case. For those, you need heuristics or approximation algorithms.

## Visual flow

```
  Naive fib(5) call tree — exponential explosion:

                        fib(5)
                       /      \
                  fib(4)      fib(3)
                 /     \      /     \
            fib(3)  fib(2)  fib(2)  fib(1)
            /   \     |       |
       fib(2) fib(1) ...     ...
         |
        ...

  Total calls: 15 (for n=5).  For n=40: ~1.6 billion.

  Memoized fib(5) — each value computed once:

  fib(0) -> fib(1) -> fib(2) -> fib(3) -> fib(4) -> fib(5)
    0         1         1         2         3         5

  Total calls: 6 (for n=5).  For n=40: 41.  That's the cure.
```
*Figure 5-1: Without memoization, fib(5) recomputes fib(2) three times and fib(3) twice. With memoization, each value is computed exactly once.*

## Concept deep-dive

### Examples that explode

Here are the classic exponential-time problems. You'll encounter variants of these throughout your career:

**Naive Fibonacci — O(2ⁿ):**

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

Each call spawns *two* more calls. The call tree is a binary tree of depth n, giving roughly 2ⁿ nodes. `fib(40)` takes seconds. `fib(60)` would take centuries.

Why is it exponential? Because the same subproblems are solved over and over. `fib(5)` computes `fib(3)` twice and `fib(2)` three times. The redundancy grows explosively with n.

**All subsets of n items — 2ⁿ subsets:**

Every item is either included or excluded — that's 2 choices per item, giving 2ⁿ total subsets. For n = 20, that's about a million. For n = 30, it's about a billion.

**All permutations — n!:**

For n = 10, that's 3.6 million. For n = 15, it's 1.3 trillion. For n = 20, it's 2.4 × 10¹⁸. Permutation enumeration is even worse than exponential.

**Traveling Salesman (brute force) — O(n!):**

Check every possible ordering of n cities. At n = 15, you're already past what brute force can handle in a reasonable time.

### The cure: memoization

The key insight is **overlapping subproblems**. If the same sub-calculation appears multiple times in the recursion tree, you can cache each result the first time you compute it and return the cached value on subsequent calls.

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

Now each value of `fib(k)` is computed exactly once, for k = 0 to n. Total work: O(n). Total space: O(n) for the cache.

This is **dynamic programming** in its simplest form. The `@cache` decorator (Python 3.9+) handles all the bookkeeping. For earlier versions, use `@lru_cache(maxsize=None)`.

### When memoization doesn't help

Memoization works when the problem has overlapping subproblems — the same inputs produce the same outputs, and those inputs recur. It does *not* help when:

- **Subproblems don't overlap.** `is_prime(n)` has no overlapping subproblems — each n is checked only once regardless of caching.
- **The state space is too large.** If each subproblem has a unique key (e.g., a full board state in chess), the cache grows as large as the search space — you've gained nothing.
- **The problem is inherently hard.** NP-hard problems like general TSP can't be reduced to polynomial time with memoization (unless P = NP, which... probably not).

### When you can't avoid exponential time

For genuinely hard problems, you have four main strategies:

1. **Heuristics** — find a good-enough answer quickly. Example: nearest-neighbor for TSP gives a tour that's typically within 20–25% of optimal, in O(n²) time.
2. **Approximation algorithms** — guaranteed to be within a factor of optimal. Example: the Christofides algorithm for metric TSP guarantees a tour within 1.5× optimal.
3. **Branch and bound** — explore the search tree, but prune branches that provably can't lead to a better solution than the current best. Can be fast on practical instances despite exponential worst case.
4. **Constraint solvers** — SAT, SMT, and ILP solvers use sophisticated heuristics internally and can solve many "exponential" instances in seconds. Before writing your own search, consider formulating the problem for a solver.

### The numbers that matter

| n | 2ⁿ | n! | Time at 10⁹ ops/sec |
|---|---|---|---|
| 10 | 1,024 | 3.6M | instant |
| 20 | ~10⁶ | ~2.4 × 10¹⁸ | 2ⁿ: 1 ms; n!: 77 years |
| 30 | ~10⁹ | ~2.7 × 10³² | 2ⁿ: 1 sec; n!: heat death |
| 40 | ~10¹² | — | 2ⁿ: 18 min |
| 60 | ~10¹⁸ | — | 2ⁿ: 37 years |

**Rule of thumb:** Never run brute-force exponential on n > ~25 without a plan.

## Why these design choices

**Why memoize instead of building a table bottom-up?** Memoization (top-down) is usually simpler to code — you write the natural recursive solution and add `@cache`. Bottom-up DP (filling a table iteratively) avoids recursion depth limits and can be more cache-friendly, but requires you to figure out the correct fill order. Start with memoization; switch to bottom-up if you hit recursion limits or need to optimize further.

**Why not always use DP?** Because DP requires two conditions: (1) overlapping subproblems and (2) optimal substructure (the optimal solution is composed of optimal sub-solutions). Many problems have neither. And even when DP applies, the time complexity might still be O(n · target) — which is "pseudo-polynomial" and can blow up for large target values.

**When would you pick heuristics over exact solutions?** When the input is large enough that exact solutions are infeasible, *and* a "pretty good" answer is acceptable. Logistics (routing, scheduling) is full of NP-hard problems where heuristics are the only practical option — and businesses run on them every day.

## Production-quality code

```python
from functools import cache
from typing import Sequence


@cache
def fib(n: int) -> int:
    """Fibonacci with memoization: O(n) time, O(n) space."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib_iterative(n: int) -> int:
    """Fibonacci iteratively: O(n) time, O(1) space."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def all_subsets(xs: Sequence) -> list[list]:
    """Generate all 2^n subsets. O(2^n) — inherently exponential."""
    if not xs:
        return [[]]
    rest = all_subsets(xs[1:])
    return rest + [[xs[0]] + s for s in rest]


def subset_sum_bruteforce(xs: Sequence[int], target: int) -> bool:
    """Does any subset sum to target? O(2^n) brute force."""
    for subset in all_subsets(xs):
        if sum(subset) == target:
            return True
    return False


def subset_sum_dp(xs: Sequence[int], target: int) -> bool:
    """Does any subset of non-negative ints sum to target?

    O(n * target) time, O(target) space — pseudo-polynomial.
    """
    if target < 0:
        return False
    reachable = [False] * (target + 1)
    reachable[0] = True
    for x in xs:
        for s in range(target, x - 1, -1):
            if reachable[s - x]:
                reachable[s] = True
    return reachable[target]


def hanoi(n: int, src: str = "A", dst: str = "C", via: str = "B") -> list[str]:
    """Towers of Hanoi: 2^n - 1 moves (optimal). Returns list of moves."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    moves: list[str] = []

    def _solve(n: int, src: str, dst: str, via: str) -> None:
        if n == 0:
            return
        _solve(n - 1, src, via, dst)
        moves.append(f"{src} -> {dst}")
        _solve(n - 1, via, dst, src)

    _solve(n, src, dst, via)
    return moves
```

## Security notes

N/A — exponential algorithms are a *self-inflicted* denial-of-service risk (your own code running too long) rather than an external attack vector. However, if user input controls the size parameter `n` of an exponential algorithm, an attacker can cause resource exhaustion. Always validate and cap input sizes for endpoints that trigger combinatorial computation.

## Performance notes

| Algorithm | Time | Space | Practical limit |
|---|---|---|---|
| Naive fib(n) | O(2ⁿ) | O(n) stack | n ≈ 35 |
| Memoized fib(n) | O(n) | O(n) cache | n ≈ 900 (Python recursion limit) |
| Iterative fib(n) | O(n) | O(1) | n ≈ 10⁶ (arbitrary precision slows) |
| All subsets | O(2ⁿ) | O(2ⁿ) output | n ≈ 20–25 |
| Subset sum (brute) | O(2ⁿ) | O(2ⁿ) | n ≈ 20–25 |
| Subset sum (DP) | O(n · target) | O(target) | depends on target magnitude |
| Towers of Hanoi | O(2ⁿ) | O(n) stack | n ≈ 25 for printing; mathematically optimal |

The jump from n = 20 (milliseconds) to n = 40 (minutes) to n = 60 (years) is the defining characteristic of exponential growth. Always estimate the runtime *before* running an exponential algorithm.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `fib(40)` takes 30+ seconds | Forgot to memoize — naive recursion recomputes the same values billions of times | Add `@cache` decorator, or convert to iterative |
| 2 | `RecursionError` on memoized `fib(1500)` | Python's default recursion limit (~1000) exceeded even with caching, because the first call still recurses to depth n | Use `sys.setrecursionlimit()` or switch to iterative |
| 3 | "Memoizing my function didn't speed it up at all" | The function has no overlapping subproblems (e.g., `is_prime`) | Memoization only helps when the same arguments are passed multiple times — verify with a counter |
| 4 | DP subset-sum works for small targets but OOM on target = 10⁹ | The DP table size is O(target), which is 10⁹ entries at ~8 bytes each = 8 GB | Use meet-in-the-middle (split items in half, O(2^(n/2))) or a different algorithm for large targets |
| 5 | Believing production inputs will stay small | "n is only 15 in our test data" → customer uploads 50 items | Validate input size at the API boundary; reject or fall back to heuristic for large n |

## Practice

**Warm-up.** Time naive `fib` vs. `@cache`-decorated `fib` for n ∈ {10, 20, 30, 35}. Print the results and the time taken.

<details><summary>Show solution</summary>

```python
import time
from functools import cache

def fib_naive(n):
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)

@cache
def fib_memo(n):
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

for n in [10, 20, 30, 35]:
    start = time.perf_counter()
    r1 = fib_naive(n)
    t1 = time.perf_counter() - start

    fib_memo.cache_clear()
    start = time.perf_counter()
    r2 = fib_memo(n)
    t2 = time.perf_counter() - start

    print(f"n={n:3d}  naive={t1:.4f}s  memo={t2:.6f}s  ratio={t1/max(t2, 1e-9):.0f}x")
```

</details>

**Standard.** Implement subset-sum two ways: brute-force (check all 2ⁿ subsets) and DP (O(n · target) table). Verify they agree on `xs=[3, 7, 1, 8, -2], target=6`.

<details><summary>Show solution</summary>

```python
def subset_sum_brute(xs, target):
    def subsets(xs):
        if not xs:
            return [[]]
        rest = subsets(xs[1:])
        return rest + [[xs[0]] + s for s in rest]
    return any(sum(s) == target for s in subsets(xs))

def subset_sum_dp(xs, target):
    reachable = {0}
    for x in xs:
        reachable = reachable | {s + x for s in reachable}
    return target in reachable

xs = [3, 7, 1, 8, -2]
target = 6
assert subset_sum_brute(xs, target) == True    # 3 + 1 + (-2) + ... many combos
assert subset_sum_dp(xs, target) == True
assert subset_sum_brute(xs, target) == subset_sum_dp(xs, target)
```

Note: the set-based DP approach handles negative numbers naturally; the array-based approach requires offset indexing.

</details>

**Bug hunt.** A developer adds `@cache` to `is_prime(n)` and says "now it's dynamic programming." Why doesn't this qualify as DP?

<details><summary>Show solution</summary>

Dynamic programming requires **overlapping subproblems** — the same sub-calculation must appear multiple times in the recursion tree. `is_prime(n)` checks divisibility by 2, 3, 5, … up to √n. Each divisor is checked exactly once, and checking `is_prime(100)` doesn't help with `is_prime(101)`. There's no overlap to exploit.

Caching `is_prime` helps if you call it multiple times with the *same* n (simple memoization), but that's not DP — it's just avoiding redundant top-level calls.

</details>

**Stretch.** Implement the Towers of Hanoi for n disks. Print each move. Count the total moves and verify it equals 2ⁿ − 1.

<details><summary>Show solution</summary>

```python
def hanoi(n, src="A", dst="C", via="B"):
    count = 0
    def solve(n, src, dst, via):
        nonlocal count
        if n == 0:
            return
        solve(n - 1, src, via, dst)
        print(f"Move disk {n}: {src} -> {dst}")
        count += 1
        solve(n - 1, via, dst, src)
    solve(n, src, dst, via)
    return count

for n in range(1, 6):
    moves = hanoi(n)
    expected = 2**n - 1
    assert moves == expected, f"n={n}: got {moves}, expected {expected}"
    print(f"n={n}: {moves} moves (expected {expected})\n")
```

</details>

**Stretch++.** Research and implement one heuristic for the Traveling Salesman Problem — the nearest-neighbor heuristic. Test on a set of 10 random 2D points and compare the tour length to the brute-force optimal (n = 10 is small enough for brute force).

<details><summary>Show solution</summary>

```python
import math
import itertools
import random

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def tour_length(points, order):
    total = sum(distance(points[order[i]], points[order[i+1]])
                for i in range(len(order) - 1))
    total += distance(points[order[-1]], points[order[0]])
    return total

def tsp_bruteforce(points):
    n = len(points)
    best = float("inf")
    best_order = None
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        length = tour_length(points, order)
        if length < best:
            best = length
            best_order = order
    return best, best_order

def tsp_nearest_neighbor(points):
    n = len(points)
    visited = [False] * n
    order = [0]
    visited[0] = True
    for _ in range(n - 1):
        current = order[-1]
        nearest = min(
            (i for i in range(n) if not visited[i]),
            key=lambda i: distance(points[current], points[i])
        )
        order.append(nearest)
        visited[nearest] = True
    return tour_length(points, order), order

random.seed(42)
points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(10)]
opt_len, _ = tsp_bruteforce(points)
nn_len, _ = tsp_nearest_neighbor(points)
print(f"Optimal:  {opt_len:.2f}")
print(f"Nearest:  {nn_len:.2f}")
print(f"Ratio:    {nn_len/opt_len:.2f}x optimal")
```

</details>

## In plain terms (newbie lane)
If `Exponential Time` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. 2³⁰ is roughly:
    (a) 10⁶  (b) 10⁹  (c) 10¹²  (d) 10¹⁸

2. Memoization helps when subproblems:
    (a) are disjoint  (b) overlap  (c) are purely I/O-bound  (d) don't exist

3. Naive Fibonacci is:
    (a) O(n)  (b) O(log n)  (c) O(2ⁿ)  (d) O(n²)

4. TSP brute-force is:
    (a) O(n²)  (b) O(n!)  (c) polynomial  (d) O(2ⁿ)

5. "Exponential" means the runtime:
    (a) is polynomial with a large constant  (b) grows as aⁿ for some a > 1  (c) applies only to Fibonacci  (d) is slow only in theory

**Short answer:**

6. Why does `@cache` turn Fibonacci from O(2ⁿ) to O(n)?
7. Name a practical strategy for when an exact exponential-time solution is infeasible.

*Answers: 1-b, 2-b, 3-c, 4-b, 5-b, 6-Because each fib(k) for k=0..n is computed exactly once and cached — subsequent calls return immediately. The 2^n redundant recomputations are eliminated leaving n unique computations, 7-Use heuristics (nearest-neighbor for TSP), approximation algorithms (guaranteed ratio to optimal), branch-and-bound (prune the search tree), or constraint solvers (SAT/ILP).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-exponential-time — mini-project](mini-projects/05-exponential-time-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Exponential algorithms (O(2ⁿ), O(n!)) become infeasible shockingly fast — n = 30 is often the boundary between "instant" and "impossible."
- Memoization collapses exponential recursions with overlapping subproblems into polynomial time. It's the simplest form of dynamic programming.
- Not all problems can be memoized — you need overlapping subproblems and optimal substructure. Some problems are genuinely NP-hard.
- For intractable problems, use heuristics, approximation algorithms, or constraint solvers instead of giving up.

## Further reading

- *Algorithm Design* (Kleinberg & Tardos), chapter 6 — dynamic programming with beautiful examples.
- *Introduction to Algorithms* (CLRS), chapter 15 — the formal DP treatment.
- Python `functools.cache` documentation — the one-decorator path from exponential to polynomial.
- Next: [Data Structures Intro](06-data-structures-intro.md).
