# Mini-project — 05-exponential-time

_Companion chapter:_ [`05-exponential-time.md`](../05-exponential-time.md)

**Goal.** Create `exponential_showdown.py` — implement brute-force and DP subset-sum, then demonstrate the performance cliff.

**Acceptance criteria:**

- Implement `subset_sum_brute(xs, target)` that checks all 2ⁿ subsets.
- Implement `subset_sum_dp(xs, target)` using a 1-D DP table.
- Benchmark both for n ∈ {5, 10, 15, 20, 25} with random positive integers and a target that's ~half the total sum.
- Print a table showing n, brute-force time, DP time, and the ratio.
- Show that DP "wins" dramatically as n grows.

**Hints:**

- Generate test data: `xs = [random.randint(1, 100) for _ in range(n)]`, `target = sum(xs) // 2`.
- For brute force at n = 25, expect it to take several seconds. At n = 30, you'll be waiting minutes.
- The DP approach's time depends on `target`, not 2ⁿ — that's the key difference.

**Stretch:** Visualize the DP table for a small example (n = 5). Print a grid showing which (item, sum) cells are reachable.
