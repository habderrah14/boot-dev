# Mini-project — 06-data-structures-intro

_Companion chapter:_ [`06-data-structures-intro.md`](../06-data-structures-intro.md)

**Goal.** Create `structure_benchmark.py` — benchmark membership tests on 100,000 items using `list`, `set`, and sorted-list + binary search.

**Acceptance criteria:**

- Generate 100,000 random integers as the collection.
- Generate 10,000 random test queries (mix of present and absent values).
- Time membership testing for each approach: `x in list`, `x in set`, and `bisect.bisect_left()` on a sorted list.
- Output a table showing: approach, total time, average time per query, and speedup relative to list.
- Include brief printed analysis of results.

**Hints:**

- Use `bisect.bisect_left()` for binary search: `found = bisect.bisect_left(sorted_xs, x) < len(sorted_xs) and sorted_xs[bisect.bisect_left(sorted_xs, x)] == x`.
- Don't include the sort time in the benchmark — sort once before timing.
- Expect `set` to be ~1000× faster than `list` for this size.

**Stretch:** Add `dict` lookup (key → value) and `sortedcontainers.SortedList` to the comparison.
