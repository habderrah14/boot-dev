# Mini-project — 04-sorting

_Companion chapter:_ [`04-sorting.md`](../04-sorting.md)

**Goal.** Create `sort_showdown.py` — implement bubble, insertion, merge, and quick sort, then benchmark them against Python's `sorted()` on various input sizes and distributions.

**Acceptance criteria:**

- All four sorts are implemented from scratch.
- Benchmark on input sizes n ∈ {100, 1_000, 10_000} with three distributions: random, sorted, reverse-sorted.
- Output a formatted table showing algorithm, input type, input size, and time.
- Verify correctness: each sort's output matches `sorted()` for every test case.
- Include a brief analysis (printed) explaining which algorithm "wins" for each scenario and why.

**Hints:**

- For O(n²) sorts, don't go above n = 10,000 — they'll take minutes.
- Use `random.seed(42)` for reproducible results.
- Remember that quick sort with a bad pivot degrades on sorted input — include that in your analysis.

**Stretch:** Add counting sort for integer inputs in a known range and show it achieving O(n + k) time.
