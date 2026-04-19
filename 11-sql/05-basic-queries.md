# Chapter 05 — Basic Queries

> SELECT is the workhorse of SQL. Master its ~six clauses and you can answer 80 % of the data questions you'll face.

## Learning objectives

By the end of this chapter you will be able to:

- Write `SELECT` statements with `WHERE`, `ORDER BY`, `LIMIT`, and `OFFSET`.
- Use comparison, logical, and pattern-matching operators.
- Handle `NULL` correctly with `IS NULL` / `IS NOT NULL`.
- Use `DISTINCT` and `DISTINCT ON`.
- Write `CASE` expressions for conditional logic.
- Choose cursor-based (keyset) pagination over offset-based pagination at scale.

## Prerequisites & recap

- [CRUD](04-crud.md) — you can insert, update, and delete rows.

## The simple version

A `SELECT` statement asks the database a question: "give me these columns, from this table, where these conditions are true, sorted this way, and only this many rows." You describe *what* you want; the engine figures out *how* to get it. The execution order isn't the order you write the clauses — the engine evaluates `FROM` first, then `WHERE`, then `SELECT`, then `ORDER BY`, then `LIMIT`. Understanding this order explains most "but why doesn't it work?" moments.

## In plain terms (newbie lane)

This chapter is really about **Basic Queries**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Written order          Execution order
  ──────────────         ──────────────────
  SELECT cols            1. FROM table
  FROM table       ───>  2. WHERE condition
  WHERE condition        3. SELECT cols / expressions
  ORDER BY col           4. ORDER BY col
  LIMIT n OFFSET m       5. LIMIT n OFFSET m

  Figure 5-1: You write SELECT first, but the engine
  evaluates FROM first. Aliases defined in SELECT are
  not visible in WHERE (because WHERE runs earlier).
```

## Concept deep-dive

### The shape of a SELECT

```sql
SELECT col1, col2          -- projection: which columns
FROM   table               -- source: which table
WHERE  condition           -- filter: which rows
ORDER BY col1 [ASC|DESC]   -- sort: what order
LIMIT  n OFFSET m;         -- pagination: how many
```

### Projections and aliases

```sql
SELECT * FROM users;                        -- all columns (avoid in app code)
SELECT id, name FROM users;                 -- specific columns
SELECT id AS user_id, name FROM users;      -- aliased column
SELECT price_cents / 100.0 AS price_dollars -- computed column
FROM products;
```

`SELECT *` is convenient in `psql` exploration but dangerous in application code — it returns columns you don't need (wasting I/O) and breaks when someone adds a column.

### Filtering with WHERE

```sql
WHERE status = 'paid'
WHERE amount >= 100 AND amount < 1000
WHERE email LIKE '%@example.com'
WHERE email ILIKE '%@example.com'                    -- case-insensitive (PG)
WHERE tags @> ARRAY['featured']                       -- array contains (PG)
WHERE created_at BETWEEN now() - INTERVAL '7 days' AND now()
WHERE id IN (1, 2, 3)
WHERE name IS NULL
WHERE active = TRUE AND NOT archived
```

### NULL semantics — the biggest trap in SQL

`NULL` means "unknown". It's not zero, not empty string, not false. Any comparison with `NULL` produces `NULL` (not `TRUE` or `FALSE`):

```sql
WHERE deleted_at = NULL     -- NEVER matches! NULL = NULL is NULL
WHERE deleted_at IS NULL    -- correct
WHERE deleted_at IS NOT NULL
```

SQL uses **three-valued logic**: `TRUE`, `FALSE`, `NULL`. `WHERE` only passes rows where the condition is `TRUE` — both `FALSE` and `NULL` are filtered out. This is why `WHERE x <> NULL` returns zero rows even when non-NULL values exist.

### Sorting

```sql
ORDER BY created_at DESC
ORDER BY category ASC, created_at DESC      -- multi-key
ORDER BY LOWER(name)                         -- by expression
ORDER BY created_at DESC NULLS LAST          -- NULL placement
```

Without `ORDER BY`, PostgreSQL returns rows in whatever order is cheapest — which is *not* guaranteed to be insertion order. If you need deterministic order, always specify it.

### Pagination

**Offset-based** (simple but has problems):

```sql
LIMIT 10 OFFSET 20;    -- skip 20, return 10 (page 3 of 10-per-page)
```

Problems: (1) slow at large offsets — the engine must scan and discard `OFFSET` rows; (2) unstable — rows inserted between page fetches shift everything.

**Cursor-based / keyset** (fast and stable):

```sql
SELECT id, body, created_at
FROM posts
WHERE (created_at, id) < ($cursor_ts, $cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 10;
```

Uses the last row of the previous page as a cursor. The database seeks directly to that position via an index — O(1) regardless of page number.

### DISTINCT

```sql
SELECT DISTINCT country FROM users;

-- DISTINCT ON (PG extension): first row per group
SELECT DISTINCT ON (user_id) user_id, created_at
FROM sessions
ORDER BY user_id, created_at DESC;
```

`DISTINCT ON` is PostgreSQL-specific and extremely useful — it gives you the "latest session per user" without a window function or subquery.

### CASE expressions

Inline conditional logic:

```sql
SELECT id,
  CASE
    WHEN amount > 10000 THEN 'whale'
    WHEN amount > 1000  THEN 'medium'
    ELSE 'small'
  END AS tier
FROM orders;
```

`CASE` is an expression — you can use it in `SELECT`, `WHERE`, `ORDER BY`, and even inside aggregate functions.

## Why these design choices

**Why declarative?** You write `WHERE status = 'paid'`; the engine decides whether to use a sequential scan, an index scan, or a bitmap heap scan. If you add an index later, the *same query* gets faster automatically — no code change needed.

**Why cursor-based pagination?** At page 1, offset and cursor are equally fast. At page 1,000, offset must read and throw away 10,000 rows before returning 10. Cursor-based skips directly to the right position via the index. For any API that clients can paginate deeply, keyset is the only scalable option.

**Why is NULL a separate concept from "empty"?** An empty string `''` means "the user provided a value and it was blank." `NULL` means "we don't know." Confusing them leads to queries that produce wrong results silently. SQL's three-valued logic is strict about this distinction, and you need to be too.

**When you'd pick differently.** Offset pagination is fine for admin panels where you never go past page 10. `SELECT *` is fine in ad-hoc `psql` exploration. `DISTINCT` can be a performance trap on large tables — consider `EXISTS` or `GROUP BY` as alternatives.

## Production-quality code

```sql
-- Recent active users with deterministic pagination
SELECT id, name, email, last_seen
FROM users
WHERE active = TRUE
  AND last_seen >= now() - INTERVAL '30 days'
ORDER BY last_seen DESC, id DESC
LIMIT 100;

-- Cursor-based pagination for a user's post feed
SELECT id, title, body, created_at
FROM posts
WHERE author_id = $1
  AND (created_at, id) < ($2::timestamptz, $3::integer)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Categorise orders by size with CASE
SELECT
  id,
  amount,
  CASE
    WHEN amount >= 10000 THEN 'enterprise'
    WHEN amount >= 1000  THEN 'business'
    WHEN amount >= 100   THEN 'starter'
    ELSE 'micro'
  END AS tier,
  created_at
FROM orders
WHERE status = 'paid'
ORDER BY amount DESC;
```

## Security notes

- **Never interpolate user input into `WHERE` clauses.** `WHERE email = '${userInput}'` is SQL injection. Use `WHERE email = $1` with parameterized values.
- **`LIKE` with user-supplied patterns.** If a user provides the pattern, they can use `%` and `_` as wildcards. Escape them if you want literal matching: `WHERE name LIKE $1 || '%'` — but make sure `$1` is sanitised (escape `%` and `_`).
- **Leaking data through pagination.** Cursor-based pagination exposes the cursor values (timestamps, IDs) in the API. If IDs are sequential, an attacker can estimate your total row count or enumerate records. Consider UUIDs or opaque cursors (base64-encoded compound keys).

## Performance notes

- **Indexes make `WHERE` fast.** Without an index, `WHERE user_id = 42` scans every row in the table (sequential scan). With `CREATE INDEX ON orders(user_id)`, it seeks directly (index scan). Chapter 11 covers this in depth.
- **Offset pagination degrades linearly.** `OFFSET 100000 LIMIT 10` reads 100,010 rows and discards 100,000. Cursor pagination reads exactly 10 rows at any page depth.
- **`DISTINCT` on large result sets is expensive.** It sorts or hashes all rows to deduplicate. If you can achieve the same result with `EXISTS` or a pre-filtered join, prefer those.
- **`ORDER BY` on an unindexed column requires a full sort.** If the sort column matches an index, the engine reads rows in order — no sort needed. This is why composite indexes that include both the filter column and the sort column are so powerful.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Query returns zero rows when NULLs exist | Used `WHERE col = NULL` or `WHERE col <> NULL` | Use `IS NULL` / `IS NOT NULL` |
| 2 | Results change between identical queries | No `ORDER BY` — engine returns rows in arbitrary order | Always specify `ORDER BY` when order matters |
| 3 | Page 500 is very slow but page 1 is fast | Using `OFFSET 5000 LIMIT 10` | Switch to cursor-based pagination |
| 4 | Application breaks when a new column is added | `SELECT *` in code — new column changes result shape | Name columns explicitly |
| 5 | `WHERE` filter on an aliased column fails | `WHERE tier = 'whale'` — aliases aren't available in `WHERE` | Repeat the expression, use a subquery, or filter in `HAVING` |

## Practice

**Warm-up.** Select the 5 most recently created users. Include `id`, `name`, and `created_at`.

**Standard.** Find all orders with an amount above the average amount. (Hint: subquery in `WHERE`.)

**Bug hunt.** Your query `SELECT * FROM users WHERE deleted_at <> NULL` returns zero rows, but you know some users have non-NULL `deleted_at` values. Why? Fix it.

**Stretch.** Write a cursor-based pagination query for the `posts` table, using `(created_at, id)` as the cursor. Fetch the second page (after a given cursor).

**Stretch++.** Use `CASE` inside `COUNT` to produce a single query that returns three counts: orders with amount < 100, 100-999, and 1000+.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
SELECT id, name, created_at
FROM users
ORDER BY created_at DESC
LIMIT 5;
```

**Standard.**

```sql
SELECT *
FROM orders
WHERE amount > (SELECT AVG(amount) FROM orders);
```

**Bug hunt.** `<> NULL` evaluates to `NULL` (not `TRUE`), so no rows pass the filter. Fix: `WHERE deleted_at IS NOT NULL`.

**Stretch.**

```sql
SELECT id, title, body, created_at
FROM posts
WHERE (created_at, id) < ('2025-03-15T10:00:00Z'::timestamptz, 42)
ORDER BY created_at DESC, id DESC
LIMIT 10;
```

**Stretch++.**

```sql
SELECT
  COUNT(*) FILTER (WHERE amount < 100)                   AS micro,
  COUNT(*) FILTER (WHERE amount >= 100 AND amount < 1000) AS medium,
  COUNT(*) FILTER (WHERE amount >= 1000)                  AS large
FROM orders;
```

Or with `CASE`:

```sql
SELECT
  SUM(CASE WHEN amount < 100 THEN 1 ELSE 0 END)                   AS micro,
  SUM(CASE WHEN amount >= 100 AND amount < 1000 THEN 1 ELSE 0 END) AS medium,
  SUM(CASE WHEN amount >= 1000 THEN 1 ELSE 0 END)                  AS large
FROM orders;
```

</details>

## Quiz

1. To skip 20 rows and return 10:
   (a) `LIMIT 20 OFFSET 10`  (b) `LIMIT 10 OFFSET 20`  (c) `OFFSET 10 LIMIT 20`  (d) `TAKE 10 SKIP 20`

2. The correct way to check for NULL:
   (a) `= NULL`  (b) `IS NULL`  (c) `== NULL`  (d) `<> NULL`

3. Case-insensitive prefix match in PostgreSQL:
   (a) `LIKE 'A%'`  (b) `ILIKE 'a%'`  (c) `= 'A'`  (d) `@> 'A'`

4. Multi-column sort:
   (a) `ORDER BY a AND b`  (b) `ORDER BY a, b`  (c) `ORDER BY a + b`  (d) only single column allowed

5. `DISTINCT`:
   (a) removes duplicate rows  (b) removes NULLs  (c) sorts results  (d) counts rows

**Short answer:**

6. Explain the advantage of cursor-based pagination over offset-based pagination.
7. When is `SELECT *` acceptable? When is it not?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-a, 6-Cursor pagination uses an index to seek directly to the next page regardless of depth — O(1). Offset pagination must scan and discard all preceding rows — O(n) where n is the offset. Cursor is also stable when new rows are inserted, 7-Acceptable in ad-hoc psql exploration and quick debugging. Not acceptable in application code because it fetches unnecessary columns and breaks when schema changes add or reorder columns.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-basic-queries — mini-project](mini-projects/05-basic-queries-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `SELECT` shape: `FROM` → `WHERE` → `SELECT` → `ORDER BY` → `LIMIT`. Understanding execution order explains most surprises.
- `NULL` is three-valued; always use `IS NULL` / `IS NOT NULL`, never `= NULL`.
- Cursor-based (keyset) pagination scales; offset pagination degrades linearly with page depth.
- Name your columns, alias your expressions, and always include `ORDER BY` when order matters.

## Further reading

- Markus Winand, [Use the Index, Luke — Pagination](https://use-the-index-luke.com/sql/partial-results/fetch-next-page)
- [PostgreSQL 16 — SELECT](https://www.postgresql.org/docs/16/sql-select.html)
- Next: [Structuring](06-structuring.md)
