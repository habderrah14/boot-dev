# Mini-project — 05-unions

_Companion chapter:_ [`05-unions.md`](../05-unions.md)

**Goal.** Build a tiny interpreter value type supporting `int`, `float`, and `string` variants as a tagged union. Implement a pretty-printer that outputs the value with its type label.

**Acceptance criteria:**

- Constructor functions: `val_int(int)`, `val_float(double)`, `val_string(const char *)`.
- `val_print(const Value *v)` prints e.g. `int(42)`, `float(3.14)`, `string("hello")`.
- `val_free(Value *v)` releases the string variant's memory.
- Clean under `-fsanitize=address` with no leaks.

**Hints:**

- The string constructor should `malloc` + `strcpy` to own its data.
- Use `= {0}` to zero-initialize the struct so unset members are safe.

**Stretch:** Add a `val_eq(const Value *a, const Value *b)` function that returns true if both values have the same tag and equal content (use `strcmp` for strings).
