# Chapter 06 — Structuring Queries

> Bigger queries become unreadable. CTEs, subqueries, views, and formatting are your tools for keeping SQL maintainable as complexity grows.

## Learning objectives

By the end of this chapter you will be able to:

- Use Common Table Expressions (CTEs) to break complex queries into named steps.
- Write recursive CTEs for tree/graph traversal.
- Create views and materialized views.
- Decide when a CTE, subquery, or view is the right abstraction.
- Format SQL for readability and team consistency.

## Prerequisites & recap

- [Basic Queries](05-basic-queries.md) — you can write `SELECT` with `WHERE`, `ORDER BY`, `LIMIT`.

## The simple version

When a query gets long, you break code into functions. SQL's equivalent is the **CTE** (Common Table Expression): a `WITH` clause that names an intermediate result set so the next step can reference it by name. **Views** are saved queries — you define them once and query them like tables. **Materialized views** go further: they cache the result on disk and only re-run when you explicitly refresh them. All three exist for the same reason: humans can't hold a 50-line nested subquery in their heads.

## In plain terms (newbie lane)

This chapter is really about **Structuring Queries**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  WITH
    step_1 AS (…),      ┌─────────┐
    step_2 AS (…)        │ step_1  │──┐
  SELECT …               └─────────┘  │   ┌─────────┐
  FROM step_2;           ┌─────────┐  ├──>│  final  │
                         │ step_2  │──┘   │ SELECT  │
                         └─────────┘      └─────────┘

  View (always re-runs):       Materialized view (cached):
  ┌───────────────────┐        ┌───────────────────┐
  │ CREATE VIEW v AS  │        │ CREATE MATERIALIZED│
  │   SELECT …        │        │   VIEW mv AS …    │
  │                   │        │                   │
  │ SELECT * FROM v;  │        │ REFRESH …         │
  │ (runs query now)  │        │ SELECT * FROM mv; │
  └───────────────────┘        │ (reads cache)     │
                               └───────────────────┘

  Figure 6-1: CTEs chain named steps; views save queries;
  materialized views cache results.
```

## Concept deep-dive

### CTEs (`WITH`)

A CTE names an intermediate result so the final query reads like a sequence of steps:

```sql
WITH recent_orders AS (
  SELECT *
  FROM orders
  WHERE created_at >= now() - INTERVAL '7 days'
),
big_spenders AS (
  SELECT user_id, SUM(amount) AS total
  FROM recent_orders
  GROUP BY user_id
  HAVING SUM(amount) > 1000
)
SELECT u.id, u.name, bs.total
FROM users u
JOIN big_spenders bs ON bs.user_id = u.id
ORDER BY bs.total DESC;
```

Without the CTE, this would be a 3-level nested subquery. With the CTE, each step has a name and can be read independently.

### Are CTEs optimised?

In PostgreSQL 12+, non-recursive CTEs are **inlined** by default — the optimizer treats them the same as subqueries. If you need a CTE to act as an optimization fence (force it to materialise), use `AS MATERIALIZED`:

```sql
WITH expensive AS MATERIALIZED (
  SELECT … FROM big_table WHERE …
)
SELECT … FROM expensive WHERE …;
```

This is rarely needed, but worth knowing when debugging query plans.

### Recursive CTEs

Walk a tree or graph by combining a **base case** with a **recursive step**:

```sql
WITH RECURSIVE ancestors AS (
  -- Base case: start from a specific category
  SELECT id, name, parent_id, 0 AS depth
  FROM categories
  WHERE id = $1

  UNION ALL

  -- Recursive step: walk up the tree
  SELECT c.id, c.name, c.parent_id, a.depth + 1
  FROM categories c
  JOIN ancestors a ON c.id = a.parent_id
)
SELECT * FROM ancestors ORDER BY depth;
```

The recursion continues until the recursive step produces zero new rows. **Danger**: if your data has cycles, this runs forever. Add a depth limit:

```sql
WHERE a.depth < 100   -- safety valve
```

### Views

A view is a named, reusable query. It doesn't store data — it re-runs every time you query it:

```sql
CREATE VIEW active_users AS
  SELECT id, name, email, last_seen
  FROM users
  WHERE active AND NOT archived;

SELECT * FROM active_users
WHERE last_seen > now() - INTERVAL '30 days';
```

Views simplify application code (query a view instead of repeating complex joins) and can serve as a security layer (expose only certain columns or rows to a role).

### Materialized views

Like a view, but the result is cached on disk:

```sql
CREATE MATERIALIZED VIEW daily_revenue AS
  SELECT
    date_trunc('day', created_at) AS day,
    SUM(amount) AS total,
    COUNT(*) AS order_count
  FROM orders
  GROUP BY 1;

SELECT * FROM daily_revenue ORDER BY day DESC LIMIT 7;

REFRESH MATERIALIZED VIEW daily_revenue;
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;  -- no lock, needs unique index
```

The trade-off: reads are instant (it's a cached table), but data is stale until you refresh. Great for dashboards and reports that tolerate minutes-old data.

### Subqueries vs CTEs vs views

| Need | Use |
|---|---|
| One-off intermediate step within a query | CTE |
| Reusable "virtual table" across many queries | View |
| Cached result for expensive aggregations | Materialized view |
| Simple inline filter or scalar value | Subquery |

### Formatting conventions

- One clause per line (`SELECT`, `FROM`, `WHERE`, `ORDER BY`).
- Indent CTE bodies and subqueries by 2-4 spaces.
- Align `JOIN` predicates under the `ON`.
- Use short, consistent aliases: `u` for `users`, `o` for `orders`.
- Uppercase SQL keywords.

Bad:

```sql
select u.name, count(o.id) from users u join orders o on o.user_id=u.id where u.active group by u.name order by count(o.id) desc;
```

Good:

```sql
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.active
GROUP BY u.name
ORDER BY order_count DESC;
```

Readable SQL is a kindness to your future self and everyone on your team.

## Why these design choices

**Why CTEs over nested subqueries?** A 3-level nested subquery forces you to read inside-out. A CTE chain reads top-to-bottom, like prose. The optimizer usually produces the same plan for both, so the choice is about human readability — and readability wins in a team codebase.

**Why views for reuse?** If four different API endpoints filter users the same way, duplicating the `WHERE` clause in each query is a maintenance burden and a bug magnet. A view centralises the logic. Change the view definition, and all four endpoints pick up the change.

**Why materialized views for reports?** Aggregating millions of rows on every dashboard load is wasteful. A materialized view runs the aggregation once and serves cached results until you refresh. The trade-off is staleness — you decide how stale is acceptable (every minute? every hour? nightly?).

**When you'd pick differently.** If your CTE is used exactly once and is small, an inline subquery is fine — the CTE overhead (extra typing, extra naming) isn't worth it. If your materialized view must be real-time, you're better off with an index or a pre-computed column maintained by a trigger.

## Production-quality code

```sql
-- CTE chain: top 10 users by spend in the last 30 days, with rank
WITH per_user AS (
  SELECT
    user_id,
    SUM(amount) AS total_spend,
    COUNT(*) AS order_count
  FROM orders
  WHERE created_at >= now() - INTERVAL '30 days'
  GROUP BY user_id
),
ranked AS (
  SELECT
    user_id,
    total_spend,
    order_count,
    RANK() OVER (ORDER BY total_spend DESC) AS spend_rank
  FROM per_user
)
SELECT
  r.spend_rank,
  u.name,
  u.email,
  r.total_spend,
  r.order_count
FROM ranked r
JOIN users u ON u.id = r.user_id
WHERE r.spend_rank <= 10
ORDER BY r.spend_rank;

-- Materialized view for a dashboard with concurrent refresh
CREATE MATERIALIZED VIEW monthly_revenue AS
  SELECT
    date_trunc('month', created_at) AS month,
    SUM(amount) AS revenue,
    COUNT(DISTINCT user_id) AS unique_buyers
  FROM orders
  WHERE status = 'paid'
  GROUP BY 1;

CREATE UNIQUE INDEX ON monthly_revenue (month);

REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

## Security notes

- **Views as access control.** Grant a role `SELECT` on a view but not on the underlying table. The view can filter rows (row-level security lite) or hide columns (e.g., `salary`) without modifying the base table.
- **`SECURITY DEFINER` views.** By default, a view runs with the *querier's* permissions. With `CREATE VIEW … WITH (security_barrier) AS …`, PostgreSQL prevents the optimizer from pushing user-supplied predicates into the view in ways that might leak hidden rows.
- **Materialized views and stale data.** A materialized view that caches sensitive data (PII, financial) persists that data on disk even if the source rows are deleted. Factor this into your data retention and compliance strategy.

## Performance notes

- **CTEs in PG 12+ are inlined.** The optimizer can push predicates through a CTE the same way it would a subquery. If you see a CTE materialising unexpectedly in `EXPLAIN`, check for side-effects (like `INSERT … RETURNING`) — those force materialisation.
- **Materialized views are just tables.** You can index them, `ANALYZE` them, and `EXPLAIN` queries against them exactly like regular tables. A `REFRESH MATERIALIZED VIEW` without `CONCURRENTLY` takes an exclusive lock — schedule it during low-traffic windows.
- **`REFRESH … CONCURRENTLY` needs a unique index.** Without one, PostgreSQL can't determine which rows changed and must lock the view. The unique index lets it do a diff and swap.
- **Recursive CTEs can be expensive.** Each recursion level runs a query. A 1,000-level tree produces 1,000 iterations. If you query tree structures frequently, consider the `ltree` extension or a closure table.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Query with 4+ levels of nested subqueries is unreadable | Growing complexity without refactoring | Rewrite as a CTE chain: one step per `WITH` clause |
| 2 | Dashboard shows yesterday's data | Materialized view hasn't been refreshed | Schedule `REFRESH MATERIALIZED VIEW` via `pg_cron` or app cron |
| 3 | Correlated subquery in `SELECT` is much slower than expected | Runs once per outer row | Replace with a `LEFT JOIN … GROUP BY` or a CTE |
| 4 | Recursive CTE runs forever | Data has a cycle (e.g., A → B → A) | Add `WHERE depth < 100` or use `CYCLE` detection (PG 14+) |
| 5 | `REFRESH MATERIALIZED VIEW` blocks all reads for seconds | Using non-concurrent refresh on a production view | Add a unique index and use `REFRESH … CONCURRENTLY` |

## Practice

**Warm-up.** Take the query `SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000)` and rewrite it as a `JOIN`.

**Standard.** Build a recursive CTE on a `categories(id, name, parent_id)` table that returns the full ancestor path from a given category up to the root.

**Bug hunt.** `SELECT *, COUNT(*) FROM orders;` fails without `GROUP BY`. Why? What is the intent, and how do you fix it?

**Stretch.** Create a view `top_customers` that shows each user's total spend and order count. Query it to find users who spent over $1,000.

**Stretch++.** Create a materialized view `daily_revenue`, add a unique index on the `day` column, and set up a concurrent refresh. Verify the refresh doesn't block a concurrent `SELECT`.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
SELECT DISTINCT u.*
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.amount > 1000;
```

**Standard.**

```sql
CREATE TABLE categories (
  id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name      TEXT NOT NULL,
  parent_id INTEGER REFERENCES categories(id)
);

WITH RECURSIVE ancestors AS (
  SELECT id, name, parent_id, 0 AS depth
  FROM categories
  WHERE id = 5

  UNION ALL

  SELECT c.id, c.name, c.parent_id, a.depth + 1
  FROM categories c
  JOIN ancestors a ON c.id = a.parent_id
)
SELECT * FROM ancestors ORDER BY depth;
```

**Bug hunt.** `SELECT *` asks for per-row data; `COUNT(*)` is an aggregate that collapses all rows into one. You can't mix them without `GROUP BY`. If the intent is the total row count, remove `*`: `SELECT COUNT(*) FROM orders;`. If the intent is per-row data plus a total, use a window function: `SELECT *, COUNT(*) OVER () AS total FROM orders;`.

**Stretch.**

```sql
CREATE VIEW top_customers AS
  SELECT
    u.id,
    u.name,
    u.email,
    COALESCE(SUM(o.amount), 0) AS total_spend,
    COUNT(o.id) AS order_count
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.id
  GROUP BY u.id;

SELECT * FROM top_customers WHERE total_spend > 100000;
```

**Stretch++.**

```sql
CREATE MATERIALIZED VIEW daily_revenue AS
  SELECT
    date_trunc('day', created_at)::date AS day,
    SUM(amount) AS revenue,
    COUNT(*) AS order_count
  FROM orders
  WHERE status = 'paid'
  GROUP BY 1;

CREATE UNIQUE INDEX ON daily_revenue (day);

-- In one session:
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;

-- In another session (concurrently):
SELECT * FROM daily_revenue ORDER BY day DESC LIMIT 5;
-- This SELECT is not blocked.
```

</details>

## Quiz

1. The CTE keyword is:
   (a) `LET`  (b) `WITH`  (c) `SUBQUERY`  (d) `INLINE`

2. A recursive CTE uses:
   (a) `WITH RECURSIVE … UNION ALL …`  (b) `FOR … IN` loops  (c) cursors only  (d) impossible in SQL

3. A view is:
   (a) a cached result  (b) a saved query that re-runs on each access  (c) a table clone  (d) a trigger

4. A materialized view:
   (a) is identical to a regular view  (b) caches results on disk; must be refreshed explicitly  (c) is always up to date  (d) exists only in memory

5. A correlated subquery:
   (a) references columns from the outer query  (b) is always faster than a JOIN  (c) is deprecated  (d) only works in PostgreSQL

**Short answer:**

6. When would you choose a CTE over a subquery?
7. Name one advantage and one disadvantage of materialized views.

*Answers: 1-b, 2-a, 3-b, 4-b, 5-a, 6-When the intermediate result is referenced multiple times or when the query has multiple logical steps that are easier to read as a named sequence rather than nested inside-out, 7-Advantage: instant reads for expensive aggregations. Disadvantage: data is stale until refreshed — you must schedule refreshes and accept some latency.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-structuring — mini-project](mini-projects/06-structuring-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- CTEs (`WITH`) name intermediate steps and make complex queries readable top-to-bottom.
- Views are saved queries; materialized views cache results on disk and need explicit refresh.
- Recursive CTEs handle tree and graph traversal — add depth limits to prevent runaway recursion.
- Formatting matters: one clause per line, consistent aliases, uppercase keywords.

## Further reading

- [PostgreSQL 16 — WITH Queries (CTEs)](https://www.postgresql.org/docs/16/queries-with.html)
- [PostgreSQL 16 — CREATE VIEW](https://www.postgresql.org/docs/16/sql-createview.html)
- [PostgreSQL 16 — CREATE MATERIALIZED VIEW](https://www.postgresql.org/docs/16/sql-creatematerializedview.html)
- Next: [Aggregations](07-aggregations.md)
