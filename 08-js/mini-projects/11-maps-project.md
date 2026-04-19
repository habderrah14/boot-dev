# Mini-project — 11-maps

_Companion chapter:_ [`11-maps.md`](../11-maps.md)

**Goal.** Build `lru-cache.js` — an LRU (Least Recently Used) cache backed by `Map`.

**Acceptance criteria:**

- Constructor takes `maxSize`.
- `get(key)` returns the value and moves the entry to "most recently used."
- `set(key, value)` adds or updates an entry; evicts the oldest if at capacity.
- `delete(key)` removes an entry.
- `get size` returns the current number of entries.
- Backed by a `Map` — leverages insertion-order semantics (delete + re-set moves to end).
- Tests with `node:test` cover: basic get/set, eviction, LRU ordering, edge cases.

**Hints:**

- `Map` preserves insertion order. To "refresh" an entry: `delete(key)`, then `set(key, value)` — it moves to the end.
- The oldest entry is `map.keys().next().value`.

**Stretch:** Add a `ttl` option so entries expire after a given number of milliseconds. `get` returns `undefined` for expired entries and deletes them lazily.
