# Mini-project — 08-stack-data-structure

_Companion chapter:_ [`08-stack-data-structure.md`](../08-stack-data-structure.md)

**Goal.** Ship `stack.h` / `stack.c` as a reusable library with a comprehensive test suite. Run under AddressSanitizer.

**Acceptance criteria:**

- API: `stack_new`, `stack_free`, `stack_push`, `stack_pop`, `stack_peek`, `stack_len`.
- Tests: push 10,000 ints, pop all, assert LIFO order.
- Test the empty-stack edge case (pop and peek return -1).
- `Makefile` with a `test` target that builds with `-fsanitize=address,undefined -g`.
- Zero ASan errors or leaks.

**Hints:**

- Start with `data = NULL`, `cap = 0`. The first `ensure_cap` call triggers `realloc(NULL, ...)` which acts like `malloc`.
- Use `assert()` for test assertions — it's simple and prints the failing expression.

**Stretch:** Add `stack_to_array(const Stack *s, int **out, size_t *len)` that copies the stack contents into a new heap-allocated array.
