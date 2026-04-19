# Mini-project — 06-stack-and-heap

_Companion chapter:_ [`06-stack-and-heap.md`](../06-stack-and-heap.md)

**Goal.** Build `IntVec` — a dynamic integer array — with a full test suite. Run under AddressSanitizer and confirm zero leaks or errors.

**Acceptance criteria:**

- API: `vec_init`, `vec_push`, `vec_pop`, `vec_get`, `vec_len`, `vec_free`.
- `vec_push` returns 0 on success, -1 on OOM.
- Tests: push 10,000 ints, pop them all, assert LIFO order and final size == 0.
- `make test` builds with `-fsanitize=address,undefined -g` and runs the test binary.

**Hints:**

- Start capacity at 0 with `data = NULL`. `realloc(NULL, n)` behaves like `malloc(n)`.
- The doubling strategy (cap = cap ? cap * 2 : 8) is standard.

**Stretch:** Add `vec_insert(v, index, value)` and `vec_remove(v, index)` with `memmove` for shifting elements.
