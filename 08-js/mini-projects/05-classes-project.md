# Mini-project — 05-classes

_Companion chapter:_ [`05-classes.md`](../05-classes.md)

**Goal.** Implement three data-structure classes — `Stack`, `Queue`, and `RingBuffer` — each using `#` private fields.

**Acceptance criteria:**

- `Stack`: `push(x)`, `pop()`, `peek()`, `get size`, `isEmpty()`.
- `Queue`: `enqueue(x)`, `dequeue()`, `peek()`, `get size`, `isEmpty()`.
- `RingBuffer(capacity)`: `write(x)` (overwrites oldest if full), `read()`, `get size`, `isFull()`.
- All internal storage uses `#` private fields.
- A test file with `node:test` covers edge cases (empty pop, full ring buffer, etc.).

**Hints:**

- `Stack` is backed by an array with `push`/`pop`.
- `Queue` can use an array, but `shift()` is O(n) — consider a linked-list or head-pointer approach for the stretch.
- `RingBuffer` uses a fixed-size array with read/write pointers.

**Stretch:** Make `Queue` O(1) for both `enqueue` and `dequeue` using a circular buffer internally.
