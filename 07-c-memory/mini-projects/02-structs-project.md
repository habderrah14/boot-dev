# Mini-project — 02-structs

_Companion chapter:_ [`02-structs.md`](../02-structs.md)

**Goal.** Implement a `User` CRUD module: create, print (to-string), and compare. Store users in a fixed-size array of 100; expose `add_user` and `list_users` functions from a separate `.c`/`.h` pair.

**Acceptance criteria:**

- `user_create` handles names longer than the buffer safely.
- `list_users` prints all added users to `stdout`.
- Compiles cleanly with `-Wall -Wextra -std=c17`.

**Hints:**

- `strncpy(dest, src, n)` copies at most `n` bytes. Null-terminate manually.
- A global `User users[100]` with a `size_t user_count` counter is fine for now — dynamic allocation comes in ch. 06.

**Stretch:** Add `find_user_by_id` that returns `const User *` or `NULL` if not found.
