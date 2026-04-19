# Mini-project — 07-advanced-pointers

_Companion chapter:_ [`07-advanced-pointers.md`](../07-advanced-pointers.md)

**Goal.** Build a CSV loader: read a CSV file into an array of `Person` structs, sort by a user-chosen column using `qsort` with function pointers, and print the sorted result.

**Acceptance criteria:**

- Reads from a file path given as a command-line argument.
- Supports sorting by at least two fields (e.g., name and age).
- Sort direction (ascending/descending) via a flag.
- Clean under `-fsanitize=address` with no leaks.

**Hints:**

- Use `fgets` + `strtok` for parsing CSV lines.
- Store an array of `Person` structs (fixed-size array or dynamic with `realloc`).
- Write two comparator functions and select between them based on argv.

**Stretch:** Support reverse sorting by wrapping the comparator: `int rev_cmp(const void *a, const void *b) { return -cmp(a, b); }`.
