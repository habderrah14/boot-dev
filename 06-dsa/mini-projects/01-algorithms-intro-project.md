# Mini-project — 01-algorithms-intro

_Companion chapter:_ [`01-algorithms-intro.md`](../01-algorithms-intro.md)

**Goal.** Create `benchmark.py` that implements both linear and binary search, benchmarks them across input sizes n ∈ {100, 1_000, 10_000, 100_000, 1_000_000}, and reports results.

**Acceptance criteria:**

- Both search functions are implemented from scratch (no `bisect`).
- For each input size, search for 100 random targets and report average time per search.
- Output is a clear table showing n, linear time, binary time, and the ratio.
- The binary search input is pre-sorted (don't include sort time in the benchmark).

**Hints:**

- Use `time.perf_counter()` for precise timing.
- Generate sorted data with `list(range(n))`.
- Pick some targets that *miss* to exercise the worst case.

**Stretch:** If `matplotlib` is available, plot the results on a log-log scale. If not, print an ASCII bar chart.
