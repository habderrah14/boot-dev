# Mini-project — 12-hashmaps

_Companion chapter:_ [`12-hashmaps.md`](../12-hashmaps.md)

**Goal.** Implement a full `HashMap` class with chaining, automatic resizing,
iteration, and deletion. Benchmark it against Python's built-in `dict`.

**Acceptance criteria:**

- `set(key, value)`, `get(key)`, `delete(key)`, `__len__`, `__iter__` all
  work correctly.
- The table resizes when load factor exceeds 0.7.
- Include at least 8 unit tests covering: insert, lookup, update, delete,
  missing key, resize trigger, iteration, and collision handling.
- Benchmark: insert and lookup 100,000 random keys; print wall-clock times
  for both your `HashMap` and Python's `dict`. Expect your version to be
  5–10× slower — that's fine.

**Hints:**

- Use `hash(key) % len(self._buckets)` for bucket indexing.
- Test collisions by inserting keys whose hashes collide modulo a small
  bucket count (e.g., capacity=4).

**Stretch:** Implement a second version using open addressing with linear
probing. Compare performance against the chaining version.
