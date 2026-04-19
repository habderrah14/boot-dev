# Chapter 08 — Subqueries

> A subquery is a query embedded in another query. Used well, they express "find X where Y is true" problems directly; used poorly, they obscure and slow things down.

## Learning objectives

By the end of this chapter you will be able to:

- Write subqueries in `SELECT`, `FROM`, and `WHERE`.
- Distinguish scalar, multi-row, and correlated subqueries.
- Use `EXISTS`, `NOT EXISTS`, `IN`, `ANY`, and `ALL`.
- Use `LATERAL` joins for "top-N per group" problems.
- Know when a JOIN or CTE is clearer or faster.

## Prerequisites & recap

- [Basic Queries](05-basic-queries.md) — `SELECT`, `WHERE`, `ORDER BY`.
- [Structuring](06-structuring.md) — CTEs for naming intermediate results.

## The simple version

A subquery is a `SELECT` inside another `SELECT`. You can put it in three places: in the `WHERE` clause to filter ("give me users who have at least one order"), in the `FROM` clause as a derived table ("treat the result of this query as a table"), or in the `SELECT` list to compute a per-row value ("for each user, count their orders"). The most important variant to learn is `EXISTS` — it answers "does at least one matching row exist?" and it's both the most readable and the most efficient way to express presence/absence checks.

## In plain terms (newbie lane)

This chapter is really about **Subqueries**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Subquery in WHERE           Subquery in FROM
  ─────────────────           ────────────────
  SELECT * FROM users         SELECT AVG(t.total)
  WHERE id IN (               FROM (
    SELECT user_id              SELECT user_id,
    FROM orders                        SUM(amount) AS total
    WHERE amount > 1000         FROM orders
  );                            GROUP BY user_id
                              ) AS t;
  Inner query runs once,
  returns a set of IDs.       Inner query produces a
  Outer filters by that set.  derived table aliased as t.


  Correlated subquery         LATERAL join
  ────────────────────        ────────────
  SELECT u.id,                SELECT u.id, r.*
    (SELECT COUNT(*)          FROM users u,
     FROM orders o              LATERAL (
     WHERE o.user_id = u.id)    SELECT id, amount
  FROM users u;                 FROM orders o
                                WHERE o.user_id = u.id
  Re-runs for each             ORDER BY created_at DESC
  outer row. O(n × m).         LIMIT 3
                              ) AS r;
                              Per-user top-3, using index.

  Figure 8-1: Four places to put a subquery, each with
  different performance characteristics.
```

## Concept deep-dive

### Scalar subquery (one row, one value)

```sql
SELECT id, name,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;
```

Returns a single value per outer row. If the inner query returns more than one row, PostgreSQL raises an error. Often clearer as a `LEFT JOIN … GROUP BY`, but convenient for quick one-offs.

### Subquery in FROM (derived table)

```sql
SELECT AVG(totals.total) AS avg_user_spend
FROM (
  SELECT user_id, SUM(amount) AS total
  FROM orders
  GROUP BY user_id
) AS totals;
```

The inner query runs first and produces a temporary result set. You **must** alias it (`AS totals`); most engines require this.

### Subquery in WHERE

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

SELECT * FROM products
WHERE price < (SELECT AVG(price) FROM products);
```

`IN` checks membership in the set returned by the subquery. The scalar comparison (`<`) works when the subquery returns exactly one value.

### `EXISTS` / `NOT EXISTS`

```sql
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.amount > 1000
);
```

`EXISTS` returns `TRUE` as soon as the inner query finds *one* matching row — it short-circuits. This makes it often faster than `IN` for large result sets. `NOT EXISTS` is the idiomatic way to find "rows without matching children":

```sql
SELECT * FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### Correlated subqueries

A correlated subquery references the outer query:

```sql
SELECT u.id, u.name,
  (SELECT MAX(created_at) FROM orders o WHERE o.user_id = u.id) AS last_order
FROM users u;
```

Conceptually, the inner query re-runs for every outer row. The optimizer may convert it to a join internally, but if it can't, performance degrades to O(n × m). Prefer `LEFT JOIN … GROUP BY` for large datasets.

### `ANY` / `ALL`

```sql
SELECT * FROM products
WHERE price > ALL (SELECT price FROM products WHERE category = 'budget');

WHERE id = ANY (ARRAY[1, 2, 3])   -- equivalent to IN (1, 2, 3)
```

`ALL` means "compared to every value in the set." `ANY` means "compared to at least one." They're occasionally more expressive than `IN` but less commonly used.

### `LATERAL` joins

`LATERAL` lets a subquery in `FROM` reference columns from preceding tables — like a correlated subquery, but in the `FROM` clause:

```sql
SELECT u.id, u.name, r.last_order_id, r.amount
FROM users u,
  LATERAL (
    SELECT id AS last_order_id, amount
    FROM orders o
    WHERE o.user_id = u.id
    ORDER BY created_at DESC
    LIMIT 1
  ) AS r;
```

This is the modern, efficient solution for "most recent order per user" or "top-N per group" problems. Without `LATERAL`, you'd need a window function + CTE, which is more code for the same result.

**`LEFT JOIN LATERAL`** preserves users who have zero orders:

```sql
SELECT u.id, u.name, r.last_order_id, r.amount
FROM users u
LEFT JOIN LATERAL (
  SELECT id AS last_order_id, amount
  FROM orders o
  WHERE o.user_id = u.id
  ORDER BY created_at DESC
  LIMIT 1
) AS r ON TRUE;
```

### When to use what

| Problem | Best tool |
|---|---|
| Filter by presence/absence | `EXISTS` / `NOT EXISTS` |
| Filter by membership in a set | `IN` (or `EXISTS` for large sets) |
| One-off computed value per row | Scalar subquery or `LEFT JOIN` |
| Derived intermediate table | Subquery in `FROM` or CTE |
| Top-N per group | `LATERAL` or window function + CTE |
| Multi-step logic | CTE chain |

## Why these design choices

**Why `EXISTS` over `IN`?** `EXISTS` short-circuits: it stops scanning the inner query after the first match. `IN` may build the entire set before checking. For large inner result sets, `EXISTS` is faster. Also, `NOT IN` has a dangerous interaction with NULLs (see Common mistakes), while `NOT EXISTS` handles NULLs correctly.

**Why `LATERAL`?** Before `LATERAL`, "last order per user" required either a correlated subquery (runs once per user — slow) or a `ROW_NUMBER()` window function wrapped in a CTE (more code). `LATERAL` expresses the intent directly: "for each user, run this subquery." The optimizer can use an index on `orders(user_id, created_at)` to make it fast.

**Why avoid deep nesting?** A 4-level nested subquery reads inside-out. Each level adds mental overhead. CTEs read top-to-bottom. After 2 levels of nesting, refactor to a CTE.

**When you'd pick differently.** If you need the result of the subquery for multiple purposes (join + filter + display), materialise it in a CTE. If the subquery is trivial and used once, inline it. If performance is critical and the optimizer doesn't flatten the subquery, rewrite as a join.

## Production-quality code

```sql
-- Users who placed at least one order over $100 in the last 30 days
SELECT u.id, u.name, u.email
FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id
    AND o.amount > 10000
    AND o.created_at >= now() - INTERVAL '30 days'
);

-- Users who have NEVER placed an order
SELECT u.id, u.name, u.email
FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Last 3 orders per user via LATERAL
SELECT u.id, u.name, r.order_id, r.amount, r.created_at
FROM users u
LEFT JOIN LATERAL (
  SELECT o.id AS order_id, o.amount, o.created_at
  FROM orders o
  WHERE o.user_id = u.id
  ORDER BY o.created_at DESC
  LIMIT 3
) AS r ON TRUE
ORDER BY u.id, r.created_at DESC;

-- Products priced above their category average
SELECT p.id, p.name, p.price, p.category, ca.avg_price
FROM products p
JOIN (
  SELECT category, AVG(price) AS avg_price
  FROM products
  GROUP BY category
) AS ca ON ca.category = p.category
WHERE p.price > ca.avg_price
ORDER BY p.category, p.price DESC;
```

## Security notes

- **Subqueries can bypass intended access boundaries.** A `WHERE id IN (SELECT … FROM secret_table)` works if the querying role has `SELECT` on `secret_table`. Row-level security (RLS) policies apply to each table independently — make sure the inner table's RLS covers the subquery's access pattern.
- **`NOT IN` with NULLs can leak information unexpectedly.** If the inner query returns any `NULL`, `NOT IN` returns zero rows (see Common mistakes). An attacker who can influence the inner query's result set could use this to force a specific outcome. Prefer `NOT EXISTS` to avoid this class of issue.

## Performance notes

- **`EXISTS` short-circuits; `IN` may not.** For `WHERE id IN (SELECT …)`, the engine builds the full result set of the inner query. For `EXISTS`, it stops at the first match. On a subquery that returns millions of rows, this is a significant difference.
- **Correlated subqueries in `SELECT` run once per outer row.** On 10,000 outer rows with 1,000 inner rows each, that's 10 million row evaluations. A `LEFT JOIN … GROUP BY` does the same work in one pass.
- **`LATERAL` uses indexes.** The optimizer can push the `WHERE o.user_id = u.id` predicate into an index scan on `orders(user_id, created_at)`. This makes "top-N per group" efficient even on large tables.
- **The optimizer may rewrite your subquery.** PostgreSQL's planner often converts `IN` subqueries to semi-joins and correlated subqueries to hash joins. `EXPLAIN ANALYZE` shows what actually happened — don't assume the written form dictates the plan.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `NOT IN (SELECT …)` returns zero rows unexpectedly | Inner query returns at least one `NULL`; `x NOT IN (…, NULL)` is always `NULL` | Use `NOT EXISTS` instead — it handles NULLs correctly |
| 2 | `ERROR: subquery must return only one column` | Scalar subquery in `SELECT` returns multiple columns | Select only one column in the subquery, or rewrite as a join |
| 3 | `ERROR: subquery used as an expression returned more than one row` | Scalar subquery returns multiple rows | Add `LIMIT 1`, use `EXISTS`, or rewrite as a join |
| 4 | Correlated subquery is very slow | Re-runs for each outer row without an index | Add an index on the inner table's join column, or rewrite as `LEFT JOIN … GROUP BY` |
| 5 | Subquery in `FROM` fails with syntax error | Forgot the alias (`AS t`) | Every derived table must have an alias |

## Practice

**Warm-up.** Find users whose email is *not* in a `banned_emails` table. Use `NOT EXISTS`.

**Standard.** Find products priced above their category's average. (Hint: subquery in `FROM` or `WHERE`.)

**Bug hunt.** `SELECT * FROM users WHERE id NOT IN (SELECT manager_id FROM employees)` returns zero rows. You know there are users who aren't managers. Why? Fix it.

**Stretch.** Rewrite the Chapter 07 "top 3 per category" query using `LATERAL` instead of `ROW_NUMBER`.

**Stretch++.** Compare `EXPLAIN ANALYZE` plans for `IN` vs `EXISTS` on a table with 100k+ rows. Which plan does the optimizer choose? Are they the same?

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
SELECT * FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM banned_emails b WHERE b.email = u.email
);
```

**Standard.**

```sql
SELECT p.*
FROM products p
WHERE p.price > (
  SELECT AVG(p2.price) FROM products p2 WHERE p2.category = p.category
);
```

Or with a derived table:

```sql
SELECT p.*
FROM products p
JOIN (
  SELECT category, AVG(price) AS avg_price
  FROM products GROUP BY category
) ca ON ca.category = p.category
WHERE p.price > ca.avg_price;
```

**Bug hunt.** `manager_id` is `NULL` for employees without a manager. `NOT IN (…, NULL)` evaluates to `NULL` for every row — no rows pass. Fix: `WHERE id NOT IN (SELECT manager_id FROM employees WHERE manager_id IS NOT NULL)` or preferably `WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.manager_id = u.id)`.

**Stretch.**

```sql
SELECT p.category, r.*
FROM (SELECT DISTINCT category FROM products) p,
LATERAL (
  SELECT id, name, price
  FROM products
  WHERE category = p.category
  ORDER BY price DESC
  LIMIT 3
) AS r
ORDER BY p.category, r.price DESC;
```

**Stretch++.**

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

EXPLAIN ANALYZE
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

In PostgreSQL, both typically produce a Hash Semi Join — the optimizer rewrites `IN` to a semi-join. Plans are usually identical.

</details>

## Quiz

1. `EXISTS` short-circuits:
   (a) never  (b) yes — stops at the first matching row  (c) only in PostgreSQL  (d) only for NULLs

2. A correlated subquery:
   (a) references columns from the outer query  (b) is independent of the outer query  (c) always causes an error  (d) is deprecated

3. The modern idiom for "top-N per group":
   (a) correlated subquery only  (b) `ROW_NUMBER()` window function  (c) `LATERAL` join  (d) both b and c

4. `NOT IN (subquery)` when the subquery returns a `NULL`:
   (a) works normally  (b) is always `TRUE`  (c) evaluates to `NULL` — excludes all rows  (d) raises an error

5. A subquery alias in `FROM`:
   (a) is optional  (b) is required in most SQL engines  (c) is only needed in MySQL  (d) is always illegal

**Short answer:**

6. When is `EXISTS` preferable to `IN`?
7. What problem does `LATERAL` solve that a regular subquery in `FROM` cannot?

*Answers: 1-b, 2-a, 3-d, 4-c, 5-b, 6-When the inner query returns a large result set — EXISTS short-circuits after the first match while IN may materialise the entire set. Also NOT EXISTS handles NULLs correctly while NOT IN does not, 7-A regular subquery in FROM cannot reference columns from other tables in the same FROM clause. LATERAL can — it runs once per outer row, enabling patterns like "top-N per group" where the subquery needs the outer row's key to filter.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-subqueries — mini-project](mini-projects/08-subqueries-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Subqueries fit in `SELECT` (scalar), `FROM` (derived table), and `WHERE` (`IN`, `EXISTS`).
- `EXISTS` short-circuits and handles NULLs correctly — prefer it over `IN` for presence checks.
- `LATERAL` joins solve "top-N per group" elegantly and efficiently.
- `NOT IN` with NULLs is a classic trap — always use `NOT EXISTS` instead.

## Further reading

- [PostgreSQL 16 — Subqueries](https://www.postgresql.org/docs/16/functions-subquery.html)
- [PostgreSQL 16 — LATERAL](https://www.postgresql.org/docs/16/queries-table-expressions.html#QUERIES-LATERAL)
- Next: [Normalization](09-normalization.md)
