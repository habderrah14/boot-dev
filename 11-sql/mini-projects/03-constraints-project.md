# Mini-project — 03-constraints

_Companion chapter:_ [`03-constraints.md`](../03-constraints.md)

**Goal.** Extend the blog schema from Chapter 02 with full constraint coverage.

**Acceptance criteria:**

- `users.email` has a `UNIQUE` constraint and a `CHECK` that it contains `@`.
- `posts.author_id` is a FK to `users(id)` with `ON DELETE CASCADE`.
- `posts.title` has `CHECK (length(title) > 0)`.
- `comments.post_id` FK to `posts(id)` with `CASCADE`; `comments.author_id` FK to `users(id)` with `RESTRICT`.
- All constraints are explicitly named.
- Demonstrate each constraint by attempting a violating insert and showing the error message.

**Hints:**

- `RESTRICT` on `comments.author_id` means you can't delete a user who has comments — you'll need to delete their comments first.
- Use `\d+ posts` to verify constraints appear correctly.

**Stretch:** Add an `exclusion` constraint using `btree_gist` to prevent overlapping date ranges on a `room_bookings` table.
