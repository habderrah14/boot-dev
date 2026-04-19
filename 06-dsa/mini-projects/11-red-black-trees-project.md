# Mini-project — 11-red-black-trees

_Companion chapter:_ [`11-red-black-trees.md`](../11-red-black-trees.md)

**Goal.** Build a time-series data store using `sortedcontainers.SortedList`
that supports O(log n) insert and O(log n + k) range queries (where k is the
number of results).

**Acceptance criteria:**

- `insert(timestamp, value)` adds a data point.
- `query(start, end)` returns all data points in `[start, end]` in order.
- Benchmark against the naive approach (re-sort a list on every insert) for
  10,000 inserts + 1,000 range queries.
- Print a comparison table showing wall-clock times.

**Hints:**

- Store `(timestamp, value)` tuples; `SortedList` sorts by the first element.
- Use `irange(start, end)` for efficient range queries.

**Stretch:** Add a `delete_range(start, end)` that removes all entries in a
timestamp range in O(log n + k).
