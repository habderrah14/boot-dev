# Mini-project — 03-big-o

_Companion chapter:_ [`03-big-o.md`](../03-big-o.md)

**Goal.** Create `complexity.py` — implement 5 toy functions of different complexity classes and empirically verify their Big-O by benchmarking.

**Acceptance criteria:**

- Implement one function for each class: O(1), O(log n), O(n), O(n log n), O(n²).
- Benchmark each function for n ∈ {10, 100, 1_000, 10_000, 100_000}.
- For each function, compute the ratio `time(2n) / time(n)`. Verify it matches the expected ratio (e.g., ~2.0 for O(n), ~4.0 for O(n²), ~1.0 for O(1)).
- Output a clear table with columns: function name, n, time, ratio.

**Hints:**

- Use `time.perf_counter()` for timing.
- Run each function multiple times and take the median to reduce noise.
- The O(1) function should be something like `dict.get(key)`, not just `return 42`.

**Stretch:** Add O(2ⁿ) for small n (up to 25) and show how the ratio approaches 2.0 (doubling n adds a constant → time doubles).
