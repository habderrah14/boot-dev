# Mini-project — 05-basic-queries

_Companion chapter:_ [`05-basic-queries.md`](../05-basic-queries.md)

**Goal.** Seed a `posts` table with 10,000 rows and benchmark offset vs. cursor pagination at page 500.

**Acceptance criteria:**

- `posts` table with `id`, `author_id`, `title`, `body`, `created_at`.
- 10,000 rows with varied `created_at` values.
- A script that times fetching page 500 (10 rows per page) using both offset (`OFFSET 4990 LIMIT 10`) and cursor.
- Report both timings and explain the difference.

**Hints:**

- Use `generate_series(1, 10000)` to seed rows quickly.
- Use `\timing` in `psql` or `EXPLAIN ANALYZE` to measure.
- For the cursor query, first fetch page 499 to get the cursor values.

**Stretch:** Increase to 1,000,000 rows and compare at page 50,000.
