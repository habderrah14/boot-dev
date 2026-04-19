# Mini-project — 03-pointers

_Companion chapter:_ [`03-pointers.md`](../03-pointers.md)

**Goal.** Build a small array utility library with `fill`, `sum`, `map`, and `for_each` — all operating on `int *` arrays with `size_t` lengths. Use function pointers for `map` and `for_each`.

**Acceptance criteria:**

- `map` takes a function `int (*fn)(int)` and returns a new heap-allocated array (caller must free).
- `for_each` takes a function `void (*fn)(int)` and calls it per element.
- All functions use `const int *` when they don't modify the array.
- Tests use `assert()` to verify correctness.
- Clean under `-fsanitize=address`.

**Hints:**

- `map` needs `malloc` (ch. 06 preview) — allocate `n * sizeof(int)` bytes and remember to check for NULL.
- `assert(sum(arr, 5) == 15)` is your test harness.

**Stretch:** Add `filter(const int *arr, size_t n, bool (*pred)(int), size_t *out_len)` that returns a new array of elements satisfying the predicate.
