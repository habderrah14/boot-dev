# Mini-project — 16-p-vs-np

_Companion chapter:_ [`16-p-vs-np.md`](../16-p-vs-np.md)

**Goal.** Implement brute-force and heuristic solvers for the subset-sum
problem. Compare their accuracy and runtime as n grows.

**Acceptance criteria:**

- `brute_force_subset_sum(nums, target)` returns the exact subset or
  `None`. Works for n ≤ 20.
- `greedy_subset_sum(nums, target)` uses a greedy heuristic (e.g., sort
  descending, take items that fit). May not find the answer even if it
  exists.
- Benchmark both on random instances for n = 10, 15, 20, 25.
- Print a table: n, brute-force time, greedy time, brute-force correct,
  greedy correct.
- The table should clearly show exponential growth for brute-force and
  constant-ish time for greedy.

**Hints:**

- Use `random.sample(range(1, 1000), n)` for random inputs.
- Set `target = sum(nums) // 3` for a reasonable challenge.

**Stretch:** Add a DP solver (`subset_sum_dp`) and include it in the
benchmark. Observe that it's fast when `target` is small but blows up when
`target` is large (pseudo-polynomial behavior).
