# Mini-project — 02-tables

_Companion chapter:_ [`02-tables.md`](../02-tables.md)

**Goal.** Design and create a schema for a blog platform with `users`, `posts`, and `comments` tables.

**Acceptance criteria:**

- Use `GENERATED ALWAYS AS IDENTITY` for primary keys.
- Use `TIMESTAMPTZ` for all date columns, with `DEFAULT now()`.
- `posts.author_id` references `users(id)`.
- `comments.post_id` references `posts(id)`, `comments.author_id` references `users(id)`.
- Include `CHECK` constraints: post `title` must be non-empty, comment `body` must be non-empty.
- Seed with at least 3 users, 5 posts, and 10 comments.
- Run `\d users`, `\d posts`, `\d comments` and confirm constraints appear.

**Hints:**

- Insert users first, then posts, then comments — foreign keys enforce order.
- Use `RETURNING id` to capture generated IDs for subsequent inserts.

**Stretch:** Add a `tags` table and a `post_tags` junction table to support many-to-many tagging.
