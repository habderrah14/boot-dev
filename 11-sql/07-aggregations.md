# Chapter 07 — Aggregations

> Aggregations collapse many rows into summaries. They are how you answer "how many?", "how much?", "per what?".

## Learning objectives

By the end of this chapter you will be able to:

- Use `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ARRAY_AGG`, and `STRING_AGG`.
- Group rows with `GROUP BY` and filter groups with `HAVING`.
- Use `FILTER` for conditional aggregation without self-joins.
- Write window functions (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, running totals) to aggregate without collapsing rows.
- Distinguish when to use `GROUP BY` vs a window function.

## Prerequisites & recap

- [Basic Queries](05-basic-queries.md) — `SELECT`, `WHERE`, `ORDER BY`.
- [Structuring](06-structuring.md) — CTEs for multi-step queries.

## The simple version

Aggregation takes a pile of rows and crunches them into a single summary value: the total, the count, the average. `GROUP BY` splits the pile into smaller piles first — one per group — and then aggregates each group separately. **Window functions** do something subtler: they compute an aggregate over a group but *keep every row visible*. Think of `GROUP BY` as collapsing rows into a summary table; think of windows as adding a "running commentary" column to every row.

## In plain terms (newbie lane)

This chapter is really about **Aggregations**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Raw rows                 GROUP BY user_id + SUM(amount)
  ┌────────┬────────┐      ┌──────────┬───────┐
  │user_id │ amount │      │ user_id  │ total │
  ├────────┼────────┤      ├──────────┼───────┤
  │   1    │  100   │      │    1     │  300  │
  │   1    │  200   │ ──>  │    2     │  400  │
  │   2    │  150   │      └──────────┴───────┘
  │   2    │  250   │       Rows collapsed into groups
  └────────┴────────┘

  Window function: SUM(amount) OVER (PARTITION BY user_id)
  ┌────────┬────────┬────────────┐
  │user_id │ amount │ user_total │
  ├────────┼────────┼────────────┤
  │   1    │  100   │    300     │   Every row kept,
  │   1    │  200   │    300     │   aggregate added
  │   2    │  150   │    400     │   alongside
  │   2    │  250   │    400     │
  └────────┴────────┴────────────┘

  Figure 7-1: GROUP BY collapses rows; window functions don't.
```

## Concept deep-dive

### Basic aggregate functions

```sql
SELECT
  COUNT(*)        AS total_rows,
  COUNT(email)    AS non_null_emails,
  SUM(amount)     AS total_revenue,
  AVG(amount)     AS mean_amount,
  MIN(amount)     AS smallest,
  MAX(amount)     AS largest
FROM orders;
```

`COUNT(*)` counts rows regardless of NULLs. `COUNT(col)` counts only non-NULL values in that column — a subtle but important distinction.

### `GROUP BY`

Split rows into groups and aggregate each:

```sql
SELECT user_id, COUNT(*) AS orders, SUM(amount) AS total
FROM orders
GROUP BY user_id
ORDER BY total DESC;
```

**Rule:** every non-aggregated column in `SELECT` must appear in `GROUP BY`. PostgreSQL enforces this strictly (MySQL historically didn't, which led to non-deterministic results).

### `HAVING`

`WHERE` filters rows *before* grouping. `HAVING` filters groups *after* aggregation:

```sql
SELECT user_id, SUM(amount) AS total
FROM orders
GROUP BY user_id
HAVING SUM(amount) > 1000;
```

If you can filter with `WHERE` (on raw columns), do — it reduces the number of rows the engine must group. `HAVING` is only needed when the filter depends on the aggregate result.

### `DISTINCT` inside aggregates

```sql
SELECT COUNT(DISTINCT user_id) AS unique_buyers FROM orders;
```

Counts distinct values, not distinct rows. Useful for "how many *different* users placed orders."

### `FILTER`

Conditional aggregation without `CASE`:

```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'paid')      AS paid,
  COUNT(*) FILTER (WHERE status = 'cancelled')  AS cancelled,
  SUM(amount) FILTER (WHERE status = 'paid')    AS paid_revenue
FROM orders;
```

This replaces the old `SUM(CASE WHEN … THEN … ELSE 0 END)` pattern. `FILTER` is cleaner, PostgreSQL-specific, and the optimizer handles it well.

### Array and string aggregates

```sql
SELECT user_id, ARRAY_AGG(id ORDER BY created_at) AS order_ids
FROM orders
GROUP BY user_id;

SELECT user_id, STRING_AGG(status, ', ' ORDER BY created_at) AS status_history
FROM orders
GROUP BY user_id;
```

`ARRAY_AGG` collects values into a PostgreSQL array. `STRING_AGG` concatenates them with a delimiter. Both support `ORDER BY` inside the aggregate.

### Window functions

Window functions compute a value across a set of rows *related to the current row* without collapsing them:

```sql
SELECT
  user_id,
  amount,
  SUM(amount) OVER (PARTITION BY user_id) AS user_total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS seq,
  amount - LAG(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS delta
FROM orders;
```

Key window functions:

| Function | What it does |
|---|---|
| `ROW_NUMBER()` | Sequential number within partition |
| `RANK()` | Rank with gaps for ties |
| `DENSE_RANK()` | Rank without gaps |
| `LAG(col, n)` | Value from `n` rows before (default 1) |
| `LEAD(col, n)` | Value from `n` rows after |
| `SUM(x) OVER (ORDER BY t)` | Running total |
| `AVG(x) OVER (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` | Moving average |

### Running totals

```sql
SELECT
  id,
  amount,
  SUM(amount) OVER (ORDER BY created_at) AS running_total
FROM orders;
```

`ORDER BY` inside `OVER()` creates a **frame**: each row sees the sum of itself and all preceding rows.

### Percentiles

```sql
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY amount) AS p95
FROM orders;
```

`PERCENTILE_CONT` returns an interpolated value (always `DOUBLE PRECISION`). `PERCENTILE_DISC` returns an actual row value.

## Why these design choices

**Why `GROUP BY` is strict about columns.** If you `SELECT user_id, email, SUM(amount)` but only `GROUP BY user_id`, which `email` should the database return? A user might have changed their email between orders. MySQL picks an arbitrary one; PostgreSQL rejects the query. Strictness prevents non-deterministic results.

**Why window functions exist.** Before window functions, "add a running total" required a correlated subquery (one inner query per outer row) — O(n²). Window functions do it in a single pass — O(n log n) at worst. They also express the intent more clearly: "compute this aggregate *alongside* each row, not *instead of* each row."

**Why `FILTER` over `CASE`.** `CASE WHEN status = 'paid' THEN 1 ELSE 0 END` works but is verbose and error-prone (easy to forget the `ELSE 0`). `FILTER (WHERE status = 'paid')` is shorter, self-documenting, and harder to get wrong.

**When you'd pick differently.** Simple counts that don't need per-row context: `GROUP BY`. Per-row enrichment (rank, running total, row-over-row delta): window functions. If you need both summary and detail in the same result, a window function avoids the self-join.

## Production-quality code

```sql
-- Daily revenue report with running monthly total
WITH daily AS (
  SELECT
    date_trunc('day', created_at)::date AS day,
    SUM(amount) AS revenue,
    COUNT(*) AS order_count
  FROM orders
  WHERE status = 'paid'
    AND created_at >= date_trunc('month', now())
  GROUP BY 1
)
SELECT
  day,
  revenue,
  order_count,
  SUM(revenue) OVER (ORDER BY day) AS mtd_revenue
FROM daily
ORDER BY day;

-- Top 3 products per category by revenue
WITH ranked AS (
  SELECT
    p.category,
    p.name,
    SUM(oi.quantity * oi.unit_price_cents) AS revenue,
    ROW_NUMBER() OVER (
      PARTITION BY p.category
      ORDER BY SUM(oi.quantity * oi.unit_price_cents) DESC
    ) AS rn
  FROM order_items oi
  JOIN products p ON p.id = oi.product_id
  GROUP BY p.category, p.name
)
SELECT category, name, revenue
FROM ranked
WHERE rn <= 3
ORDER BY category, rn;

-- Conditional counts in a single pass
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'paid')      AS paid,
  COUNT(*) FILTER (WHERE status = 'cancelled')  AS cancelled,
  COUNT(*) FILTER (WHERE status = 'refunded')   AS refunded,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE status = 'cancelled') / NULLIF(COUNT(*), 0),
    1
  ) AS cancel_rate_pct
FROM orders
WHERE created_at >= now() - INTERVAL '30 days';
```

## Security notes

- **Aggregation can leak information.** Even if a user can't see individual salary rows, `SELECT AVG(salary) FROM employees WHERE department = 'exec'` might reveal something sensitive. Row-level security (RLS) policies should consider aggregate access.
- **Injecting into `GROUP BY` or `ORDER BY`.** If your application lets users choose the grouping column via URL parameter, validate against a whitelist. An attacker who controls the column name can probe for column existence or trigger expensive sorts.

## Performance notes

- **`WHERE` before `GROUP BY`, `HAVING` after.** Filtering with `WHERE` reduces the number of rows the engine must hash or sort for grouping. Using `HAVING` for conditions that *could* go in `WHERE` forces the engine to process (and then discard) extra rows.
- **`COUNT(DISTINCT col)` is expensive.** It requires sorting or hashing to deduplicate. On large tables, consider `HyperLogLog` approximations (`postgresql-hll` extension) if exact counts aren't needed.
- **Window functions add a sort.** Each `OVER (PARTITION BY … ORDER BY …)` may add a sort step. If multiple windows use the same partition and order, define a named window to help the planner reuse the sort: `WINDOW w AS (PARTITION BY user_id ORDER BY created_at)`, then `SUM(amount) OVER w`.
- **Indexes for `GROUP BY`.** If you frequently group by `user_id`, an index on `user_id` lets the engine group via an index scan instead of a hash — faster for large tables.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `ERROR: column must appear in GROUP BY or aggregate` | Non-aggregated column in `SELECT` not listed in `GROUP BY` | Add the column to `GROUP BY` or wrap it in an aggregate |
| 2 | `COUNT(col)` returns fewer rows than expected | `COUNT(col)` ignores NULLs | Use `COUNT(*)` if you want total rows |
| 3 | Window function results are wrong | Forgot `PARTITION BY` — aggregated over the whole table | Add `PARTITION BY group_column` to the `OVER` clause |
| 4 | Using `HAVING` instead of `WHERE` | Filtering on a raw column in `HAVING` instead of pre-grouping | Move the condition to `WHERE` — it's semantically clearer and faster |
| 5 | Median calculation returns wrong type | Used `PERCENTILE_DISC` expecting interpolation | Use `PERCENTILE_CONT` for interpolated values |

## Practice

**Warm-up.** Count the number of orders per `status`.

**Standard.** Find the top 5 users by total spend. Return `user_id`, `total_spend`, and `order_count`.

**Bug hunt.** `SELECT user_id, amount FROM orders GROUP BY user_id` fails. Why? What did the author probably intend?

**Stretch.** Add a running total of `amount` per user, ordered by `created_at`. Use a window function.

**Stretch++.** Compute the median order amount using `PERCENTILE_CONT(0.5)`. Then compute the median per user (hint: window-function-style percentile isn't directly supported — use a CTE with `ROW_NUMBER` and `COUNT`).

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
SELECT status, COUNT(*) AS n
FROM orders
GROUP BY status
ORDER BY n DESC;
```

**Standard.**

```sql
SELECT
  user_id,
  SUM(amount) AS total_spend,
  COUNT(*) AS order_count
FROM orders
GROUP BY user_id
ORDER BY total_spend DESC
LIMIT 5;
```

**Bug hunt.** `amount` is not aggregated and not in `GROUP BY`. The author probably meant `SUM(amount)` or `GROUP BY user_id, amount`. Fix depends on intent:

```sql
-- If they wanted total per user:
SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id;

-- If they wanted each distinct (user_id, amount) pair:
SELECT user_id, amount FROM orders GROUP BY user_id, amount;
```

**Stretch.**

```sql
SELECT
  user_id,
  id,
  amount,
  created_at,
  SUM(amount) OVER (
    PARTITION BY user_id ORDER BY created_at
  ) AS running_total
FROM orders
ORDER BY user_id, created_at;
```

**Stretch++.**

Global median:

```sql
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median
FROM orders;
```

Per-user median (workaround):

```sql
WITH numbered AS (
  SELECT
    user_id,
    amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount) AS rn,
    COUNT(*) OVER (PARTITION BY user_id) AS cnt
  FROM orders
)
SELECT
  user_id,
  AVG(amount) AS median_amount
FROM numbered
WHERE rn IN (FLOOR((cnt + 1) / 2.0)::int, CEIL((cnt + 1) / 2.0)::int)
GROUP BY user_id;
```

</details>

## Quiz

1. `COUNT(*)` vs `COUNT(col)`:
   (a) identical  (b) `COUNT(col)` ignores NULLs in that column  (c) `COUNT(*)` ignores NULLs  (d) `COUNT` is not an aggregate

2. `WHERE` vs `HAVING`:
   (a) identical  (b) `WHERE` filters rows pre-group; `HAVING` filters groups post-aggregation  (c) `HAVING` is faster  (d) `WHERE` is for aggregates

3. A window function:
   (a) collapses rows into groups  (b) computes an aggregate alongside each row without collapsing  (c) only ranks rows  (d) is unsupported in PostgreSQL

4. `COUNT(*) FILTER (WHERE status = 'paid')`:
   (a) counts only rows where status is 'paid'  (b) samples randomly  (c) limits output  (d) is a subquery

5. `ARRAY_AGG(col)`:
   (a) joins strings  (b) collects values into a PostgreSQL array  (c) sums values  (d) creates a view

**Short answer:**

6. Give one scenario where a window function is better than `GROUP BY`.
7. What is the performance cost of window functions compared to plain aggregates?

*Answers: 1-b, 2-b, 3-b, 4-a, 5-b, 6-When you need both per-row detail and a group aggregate in the same result — e.g. showing each order's amount alongside the user's total spend. GROUP BY would collapse the per-row detail, 7-Window functions add a sort step per distinct OVER clause. For large datasets this sort dominates. Named windows and matching indexes can reduce the cost.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-aggregations — mini-project](mini-projects/07-aggregations-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `GROUP BY` collapses rows into groups; window functions aggregate without collapsing.
- Use `WHERE` to filter rows before grouping and `HAVING` to filter groups after aggregation.
- `FILTER (WHERE …)` is PostgreSQL's clean alternative to `CASE`-based conditional aggregation.
- `ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, and running totals via `SUM() OVER (ORDER BY …)` are essential window function patterns.

## Further reading

- [PostgreSQL 16 — Aggregate Functions](https://www.postgresql.org/docs/16/functions-aggregate.html)
- [PostgreSQL 16 — Window Functions](https://www.postgresql.org/docs/16/tutorial-window.html)
- Next: [Subqueries](08-subqueries.md)
