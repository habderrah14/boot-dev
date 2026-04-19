# Mini-project — 09-linked-lists

_Companion chapter:_ [`09-linked-lists.md`](../09-linked-lists.md)

**Goal.** Implement an LRU (Least Recently Used) cache backed by a hash map
and a doubly linked list. `get` and `put` must both run in O(1).

**Acceptance criteria:**

- `LRUCache(capacity)` creates a cache with a fixed maximum size.
- `get(key)` returns the value and marks the entry as most-recently used, or
  returns `-1` if missing.
- `put(key, value)` inserts or updates; evicts the least-recently used entry
  when at capacity.
- All operations are O(1).
- Include at least 5 unit tests covering: basic get/put, eviction, update
  existing key, capacity-1 edge case, and interleaved operations.

**Hints:**

- The doubly linked list tracks recency order. The hash map maps keys to
  list nodes for O(1) lookup.
- Use sentinel head and tail nodes to avoid `None` checks.

**Stretch:** Add a `ttl` (time-to-live) parameter so entries expire after a
given number of seconds.
