# Chapter 10 — Joins

> Joins combine rows from multiple tables. Getting joins right is half of writing SQL.

## Learning objectives

By the end of this chapter you will be able to:

- Use `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, and `FULL OUTER JOIN`.
- Recognise when a `CROSS JOIN` or self-join is the right tool.
- Predict the row count of a join and avoid accidental row multiplication.
- Filter correctly on `LEFT JOIN` results without accidentally converting to `INNER`.
- Explain why `NATURAL JOIN` is dangerous and `USING` is acceptable.

## Prerequisites & recap

- [Normalization](09-normalization.md) — you understand why data is split across tables.
- [Subqueries](08-subqueries.md) — `EXISTS` and `LATERAL` as alternatives to joins.

## The simple version

A join stitches two tables together by matching rows on a condition (usually a foreign key). **INNER JOIN** keeps only rows that match in *both* tables. **LEFT JOIN** keeps every row from the left table, filling in `NULL` where the right table has no match. That's 90 % of real-world joins. The remaining 10 % — `RIGHT JOIN`, `FULL OUTER JOIN`, `CROSS JOIN`, and self-joins — exist for specific scenarios. The most common mistake is filtering on a `LEFT JOIN`-ed table's column in `WHERE`, which silently converts it to an `INNER JOIN`.

## In plain terms (newbie lane)

This chapter is really about **Joins**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  users                    orders
  ┌────┬───────┐           ┌────┬─────────┬────────┐
  │ id │ name  │           │ id │ user_id │ amount │
  ├────┼───────┤           ├────┼─────────┼────────┤
  │  1 │ Alice │           │ 10 │    1    │  100   │
  │  2 │ Bob   │           │ 11 │    1    │  200   │
  │  3 │ Carol │           │ 12 │    2    │  150   │
  └────┴───────┘           └────┴─────────┴────────┘

  INNER JOIN (matches only)     LEFT JOIN (all from left)
  ┌───────┬────────┐            ┌───────┬────────┐
  │ name  │ amount │            │ name  │ amount │
  ├───────┼────────┤            ├───────┼────────┤
  │ Alice │  100   │            │ Alice │  100   │
  │ Alice │  200   │            │ Alice │  200   │
  │ Bob   │  150   │            │ Bob   │  150   │
  └───────┴────────┘            │ Carol │  NULL  │  ← kept!
  Carol dropped (no orders)     └───────┴────────┘

  Figure 10-1: INNER keeps matches; LEFT keeps everything
  from the left table, with NULLs for non-matches.
```

## Concept deep-dive

### INNER JOIN

Returns only rows that match in both tables:

```sql
SELECT u.name, o.amount
FROM users u
JOIN orders o ON o.user_id = u.id;
```

`JOIN` without a qualifier is `INNER JOIN`. Users without orders are dropped; orders without users are dropped.

### LEFT JOIN (LEFT OUTER JOIN)

All rows from the left table; right-side columns are `NULL` when there's no match:

```sql
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;
```

Users with zero orders still appear (with `order_count = 0`). This is the most common join variant for "show everything, including empty."

### RIGHT JOIN

Left and right are swapped. In practice, you almost never need `RIGHT JOIN` — just swap the table order and use `LEFT JOIN`. It exists for completeness.

### FULL OUTER JOIN

Every row from both sides; NULLs where there's no match on either side:

```sql
SELECT
  COALESCE(a.id, b.id) AS id,
  a.status AS source_a,
  b.status AS source_b
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.id
WHERE a.status IS DISTINCT FROM b.status;
```

Useful for reconciliation: "show me everything in A that isn't in B, everything in B that isn't in A, and everything that differs."

### CROSS JOIN

Cartesian product — every row from the left combined with every row from the right:

```sql
SELECT s.name, c.name
FROM sizes s
CROSS JOIN colors c;
```

10 sizes × 8 colors = 80 rows. Intentional for generating combinations. Accidental when you forget the `ON` clause — a 10,000 × 10,000 cross join produces 100 million rows and probably crashes your session.

### Self-join

A table joined to itself. Classic use: employee-manager hierarchies:

```sql
SELECT
  e.name AS employee,
  m.name AS manager
FROM employees e
JOIN employees m ON m.id = e.manager_id;
```

The same table appears twice with different aliases. Conceptually, you're matching rows in one copy against rows in another copy.

### Multi-way joins

```sql
SELECT u.name, o.id AS order_id, p.name AS product
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id;
```

Each additional join multiplies the number of rows if the relationship is one-to-many. A 4-way join can easily produce millions of rows from tables with thousands each. Always check row counts with `EXPLAIN` before running multi-way joins on large tables.

### Row count multiplication

This catches people:

| Users | Orders per user | INNER JOIN rows |
|---|---|---|
| 100 | 10 each | 1,000 |
| 100 | 0-100 each | 0-10,000 |

If you expected "100 users with orders" and got 1,000 rows, you forgot that each user × each order = one row. Fix with `DISTINCT`, `GROUP BY`, or rephrase with `EXISTS`:

```sql
SELECT u.*
FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

### `USING` and `NATURAL JOIN`

```sql
JOIN orders USING (user_id)        -- equi-join on shared column name
NATURAL JOIN orders                -- joins on ALL shared column names
```

`USING` is fine when the FK and PK share the exact same column name. `NATURAL JOIN` is dangerous: if someone adds a column named `status` to both tables, the join silently includes it in the match condition. **Never use `NATURAL JOIN` in production code.**

### The WHERE-on-LEFT-JOIN trap

```sql
-- BUG: silently converts LEFT to INNER
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.amount > 100;
```

Carol has no orders, so `o.amount` is `NULL`. `NULL > 100` is `NULL` (not `TRUE`), so Carol is filtered out. The `LEFT JOIN` is meaningless.

Fix: move the condition into the `ON` clause, or use `IS NULL`:

```sql
-- Keep users with no orders, but only show orders > 100
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 100;
```

## Why these design choices

**Why explicit `JOIN … ON`?** Older SQL used comma-separated tables in `FROM` with the join condition in `WHERE`. This syntax is ambiguous (is it a join condition or a filter?) and easy to break (forget the condition → accidental cross join). Explicit `JOIN … ON` separates join logic from filter logic.

**Why LEFT JOIN is more common than RIGHT.** Convention: the "primary" table goes on the left. `FROM users LEFT JOIN orders` reads as "all users, optionally with their orders." Flipping to `FROM orders RIGHT JOIN users` says the same thing less clearly. Stick with LEFT.

**Why avoid NATURAL JOIN.** It couples your query to the exact set of column names in both tables. A column rename, addition, or migration silently changes the join semantics. Explicit `ON` is immune to schema drift.

**When you'd pick differently.** If you only need presence/absence (not the joined data), `EXISTS` is often faster than `JOIN + DISTINCT`. If you need "top N per group," `LATERAL` (Chapter 08) is cleaner than a multi-way join with window functions.

## Production-quality code

```sql
-- Per-user order summary (including users with zero orders)
SELECT
  u.id,
  u.name,
  COUNT(o.id) AS order_count,
  COALESCE(SUM(o.amount), 0) AS total_spend,
  MAX(o.created_at) AS last_order_at
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id
ORDER BY total_spend DESC;

-- Reconcile two imported CSVs to find mismatches
SELECT
  COALESCE(a.sku, b.sku) AS sku,
  a.price AS price_source_a,
  b.price AS price_source_b,
  CASE
    WHEN a.sku IS NULL THEN 'only in B'
    WHEN b.sku IS NULL THEN 'only in A'
    ELSE 'price mismatch'
  END AS issue
FROM import_a a
FULL OUTER JOIN import_b b ON a.sku = b.sku
WHERE a.price IS DISTINCT FROM b.price;

-- Employee hierarchy with manager name
SELECT
  e.id,
  e.name AS employee,
  COALESCE(m.name, '(no manager)') AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY m.name NULLS FIRST, e.name;

-- Multi-way join: order line items with product and customer details
SELECT
  u.name AS customer,
  o.id AS order_id,
  p.name AS product,
  oi.quantity,
  oi.unit_price_cents,
  oi.quantity * oi.unit_price_cents AS line_total
FROM orders o
JOIN users u ON u.id = o.user_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'paid'
ORDER BY o.id, p.name;
```

## Security notes

- **Joins can leak data across table boundaries.** If role A has `SELECT` on `orders` but not `users`, a `JOIN users ON …` will fail. But if A has access to both tables, the join may expose combinations the application didn't intend to reveal. Use views or row-level security to control what joined data is visible.
- **Cross joins as a denial-of-service vector.** A query with an accidental or malicious cross join can consume all available memory and CPU. If your application constructs joins from user input, validate the join conditions.

## Performance notes

- **Index the FK column on the child side.** `JOIN orders o ON o.user_id = u.id` uses an index on `orders(user_id)`. Without it, every join iteration scans the full `orders` table.
- **Join order matters to the optimizer.** PostgreSQL's planner considers multiple join orders and picks the cheapest. But with 8+ tables, the planner may not explore all permutations. You can hint with `SET join_collapse_limit` or restructure the query.
- **Hash joins vs. nested loops vs. merge joins.** The planner picks based on table sizes and available indexes. Hash joins are fast for large unindexed tables. Nested loops are fast when the inner side has an index. Merge joins are fast when both sides are pre-sorted. `EXPLAIN ANALYZE` tells you which was chosen.
- **LEFT JOIN with aggregate can use HashAggregate.** `LEFT JOIN + GROUP BY` is a common pattern and well-optimized. Don't rewrite it as a correlated subquery "for performance" — it's almost always slower.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `LEFT JOIN` returns same rows as `INNER JOIN` | `WHERE` clause filters on a right-side column (`WHERE o.amount > 0`), excluding NULLs | Move the condition to the `ON` clause, or handle `NULL` explicitly |
| 2 | Query returns 10x more rows than expected | One-to-many join multiplies rows (each order creates a row per user-order pair) | Use `DISTINCT`, `GROUP BY`, or rephrase with `EXISTS` |
| 3 | Accidental cross join producing millions of rows | Forgot the `ON` clause or used comma-separated `FROM` | Always use explicit `JOIN … ON` |
| 4 | `NATURAL JOIN` silently returns wrong results after a migration | New column with the same name added to both tables | Use explicit `ON` or `USING` — never `NATURAL` |
| 5 | Self-join returns no rows for top-level employees | Top-level employees have `manager_id = NULL`; `INNER JOIN` drops them | Use `LEFT JOIN employees m ON m.id = e.manager_id` |

## Practice

**Warm-up.** Join `users` to `orders`. Show `user.name` and `order.amount` for all matching rows.

**Standard.** Show all users with their order count, including users with zero orders. Use `LEFT JOIN` + `COUNT(o.id)` + `GROUP BY`.

**Bug hunt.** Your query `SELECT u.name, o.amount FROM users u LEFT JOIN orders o ON o.user_id = u.id WHERE o.amount > 0` doesn't return users without orders. Why? Fix it.

**Stretch.** Write a self-join on an `employees` table to show each employee's name alongside their manager's name. Include top-level employees (those with no manager).

**Stretch++.** Use `FULL OUTER JOIN` to reconcile two tables (`import_2024` and `import_2025`) by `sku`. Show items only in 2024, only in 2025, and those with price differences.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
SELECT u.name, o.amount
FROM users u
JOIN orders o ON o.user_id = u.id;
```

**Standard.**

```sql
SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
ORDER BY order_count DESC;
```

**Bug hunt.** `WHERE o.amount > 0` filters out rows where `o.amount IS NULL` — which is exactly the rows for users without orders. The `LEFT JOIN` produces `NULL` for those users, and `NULL > 0` is `NULL` (filtered out). Fix: move the condition to `ON`:

```sql
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 0;
```

Now users without matching orders still appear with `o.amount = NULL`.

**Stretch.**

```sql
SELECT
  e.name AS employee,
  COALESCE(m.name, '(top-level)') AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY manager, employee;
```

**Stretch++.**

```sql
SELECT
  COALESCE(a.sku, b.sku) AS sku,
  a.price AS price_2024,
  b.price AS price_2025,
  CASE
    WHEN a.sku IS NULL THEN 'new in 2025'
    WHEN b.sku IS NULL THEN 'removed in 2025'
    WHEN a.price <> b.price THEN 'price changed'
  END AS status
FROM import_2024 a
FULL OUTER JOIN import_2025 b ON a.sku = b.sku
WHERE a.price IS DISTINCT FROM b.price
ORDER BY sku;
```

</details>

## Quiz

1. `INNER JOIN` returns:
   (a) all rows from the left table  (b) only rows that match in both tables  (c) the Cartesian product  (d) all rows from the right table

2. `LEFT JOIN` with no matching right-side row:
   (a) drops the row  (b) keeps the left row with NULLs for right columns  (c) raises an error  (d) duplicates the left row

3. A self-join is useful for:
   (a) sorting  (b) hierarchies (employee → manager)  (c) CTEs  (d) constraints

4. `WHERE` on a right-side column of a `LEFT JOIN`:
   (a) is the same as filtering in `ON`  (b) converts the `LEFT JOIN` to `INNER` by excluding NULLs  (c) has no effect  (d) is a syntax error

5. `NATURAL JOIN`:
   (a) is preferred in production  (b) is fragile — joins on all shared column names  (c) is deprecated in all databases  (d) is always explicit

**Short answer:**

6. Why should you avoid `NATURAL JOIN` in production?
7. Describe a scenario where `FULL OUTER JOIN` is the right choice.

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b, 6-NATURAL JOIN implicitly joins on every column name shared by both tables. Adding or renaming a column silently changes the join condition, which can produce wrong results without any error, 7-Reconciling two data sources (e.g. two CSV imports) — FULL OUTER JOIN shows rows present in only one source, plus rows in both sources that differ.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-joins — mini-project](mini-projects/10-joins-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Always use explicit `JOIN … ON` — never comma-separated tables, never `NATURAL JOIN`.
- `INNER JOIN` keeps matches only; `LEFT JOIN` keeps everything from the left table.
- Filtering on a right-side column in `WHERE` silently converts a `LEFT JOIN` to `INNER` — move the condition to `ON`.
- One-to-many joins multiply rows; use `DISTINCT`, `GROUP BY`, or `EXISTS` when you want one row per parent.

## Further reading

- [PostgreSQL 16 — Table Expressions (Joins)](https://www.postgresql.org/docs/16/queries-table-expressions.html)
- [Markus Winand — SQL Joins Visualized](https://use-the-index-luke.com/sql/join)
- Next: [Performance](11-performance.md)
