# Chapter 11 — Performance

> A slow query is usually not "the database being slow" — it's a query missing an index, reading too much, or doing the wrong thing.

## Learning objectives

By the end of this chapter you will be able to:

- Read a query plan with `EXPLAIN` and `EXPLAIN ANALYZE`.
- Choose the right index type (B-tree, GIN, GiST, BRIN) for a workload.
- Identify and fix common anti-patterns: missing indexes, N+1 queries, large offsets.
- Understand PostgreSQL's cost model, vacuum, and autovacuum.
- Set up connection pooling for production.

## Prerequisites & recap

- [Joins](10-joins.md) — you can write multi-table queries.
- [Aggregations](07-aggregations.md) — you understand `GROUP BY` and window functions.

## The simple version

PostgreSQL doesn't run your query the way you wrote it. It **plans** the fastest strategy — choosing between sequential scans, index scans, hash joins, merge joins — based on table statistics. `EXPLAIN` shows you the plan; `EXPLAIN ANALYZE` runs the query and shows the *actual* timings. When a query is slow, the plan tells you why: a missing index forces a full table scan, stale statistics make the planner choose the wrong join strategy, or a large `OFFSET` forces the engine to read and discard thousands of rows. Fix the plan, fix the performance.

## In plain terms (newbie lane)

This chapter is really about **Performance**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Your SQL query
       │
       ▼
  ┌──────────┐    table stats     ┌─────────────┐
  │  Parser  │ ──────────────────>│   Planner   │
  └──────────┘                    │             │
                                  │ cost model  │
                                  │ index info  │
                                  │ row counts  │
                                  └──────┬──────┘
                                         │
                               chooses cheapest plan
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │   Executor   │
                                  │              │
                                  │ Seq Scan     │
                                  │ Index Scan   │
                                  │ Hash Join    │
                                  │ Merge Join   │
                                  │ Nested Loop  │
                                  └──────┬───────┘
                                         │
                                         ▼
                                   Result rows

  Figure 11-1: The planner uses statistics and cost
  estimates to choose the cheapest execution strategy.
```

## Concept deep-dive

### `EXPLAIN` and `EXPLAIN ANALYZE`

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

Shows the **estimated** plan: which scan type, estimated rows, estimated cost. No query execution.

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 42;
```

**Runs** the query and reports actuals: actual rows, actual time, buffer hits vs. reads. Use this to compare estimates to reality.

What to look for:

| Plan element | What it tells you |
|---|---|
| `Seq Scan` | Full table scan — no index used |
| `Index Scan` | Uses a B-tree (or other) index — fast |
| `Bitmap Heap Scan` | Multiple index conditions combined |
| `Hash Join` | Builds a hash table from one side, probes with the other |
| `Nested Loop` | For each outer row, scan inner side — fast with index, slow without |
| `Merge Join` | Both sides pre-sorted, merged — efficient for large sorted datasets |
| `rows=1000` vs `actual rows=1` | Stale statistics — run `ANALYZE` |
| `Buffers: shared hit=100 read=5000` | High `read` = data not in cache, lots of disk I/O |

### Indexes

**B-tree** (default) — supports equality, range, sorting, prefix `LIKE`:

```sql
CREATE INDEX ON users (email);
CREATE INDEX ON orders (user_id, created_at DESC);  -- composite
```

A composite index `(user_id, created_at DESC)` serves both `WHERE user_id = $1` and `WHERE user_id = $1 ORDER BY created_at DESC`. Column order matters: the index is usable for queries that filter on a **leftmost prefix** of the index columns.

**GIN** — inverted index for JSONB, arrays, full-text search:

```sql
CREATE INDEX ON events USING GIN (payload);
CREATE INDEX ON posts USING GIN (to_tsvector('english', body));
```

**GiST** — for geometric, range, and nearest-neighbor queries:

```sql
CREATE INDEX ON locations USING GIST (coordinates);
```

**BRIN** — Block Range Index for huge, physically ordered tables (time-series):

```sql
CREATE INDEX ON events USING BRIN (created_at);
```

Very small index size, but only useful when the physical order on disk correlates with the indexed column.

**Hash** — equality-only, rarely better than B-tree in modern PostgreSQL.

### When indexes help

- Equality filter: `WHERE email = $1` → B-tree on `email`.
- Range filter: `WHERE created_at > $1` → B-tree on `created_at`.
- Sort: `ORDER BY created_at DESC` → B-tree on `created_at DESC`.
- Join key: `JOIN orders o ON o.user_id = u.id` → B-tree on `orders(user_id)`.
- JSONB containment: `WHERE payload @> '{"type":"click"}'` → GIN on `payload`.

### When indexes don't help

- **Functional transformation:** `WHERE LOWER(email) = $1` can't use a plain index on `email`. Fix: create a **functional index**: `CREATE INDEX ON users (LOWER(email))`.
- **Leading wildcard:** `WHERE email LIKE '%gmail.com'` can't use a B-tree. Fix: `pg_trgm` GIN index for trigram matching.
- **Low-cardinality columns:** An index on `active BOOLEAN` with 99% `TRUE` values barely filters. Fix: partial index: `CREATE INDEX ON users (id) WHERE active = FALSE`.
- **Small tables:** Sequential scan on 100 rows is faster than the overhead of an index lookup.

### Partial indexes

Index only the rows you actually query:

```sql
CREATE INDEX ON orders (user_id)
WHERE status = 'pending';
```

Smaller, faster, and only useful for queries that include the same `WHERE` condition.

### Cost of indexes

Every index slows down writes (the index must be updated on every `INSERT` / `UPDATE` / `DELETE`) and consumes disk space. A 100-column table with 50 indexes is writing 51 data structures on every insert. **Index what you query; don't index "just in case."**

### The cost model

PostgreSQL assigns a numeric **cost** to each plan step:

- `seq_page_cost = 1.0` (reading a page sequentially)
- `random_page_cost = 4.0` (seeking to a random page)
- `cpu_tuple_cost = 0.01` (processing a row)
- `cpu_index_tuple_cost = 0.005` (processing an index entry)

The planner sums costs and picks the cheapest plan. On SSDs, `random_page_cost` can be lowered to ~1.1 because random reads are nearly as fast as sequential.

### Common anti-patterns

| Anti-pattern | Why it's slow | Fix |
|---|---|---|
| Missing index on FK column | Deleting a parent scans the entire child table | `CREATE INDEX ON orders(user_id)` |
| `SELECT *` | Fetches all columns, including blobs | Name only needed columns |
| `OFFSET 100000` | Scans and discards 100k rows | Keyset/cursor pagination (Chapter 05) |
| N+1 queries from app code | 1 query for users + N queries for orders | Batch: `WHERE user_id = ANY($1::int[])` or `JOIN` |
| Scalar correlated subquery | Re-runs inner query per outer row | `LEFT JOIN … GROUP BY` |
| Index on low-cardinality column | Index returns most rows → slower than seq scan | Partial index or skip the index |
| `WHERE LOWER(col) = $1` on a plain index | Functional transform defeats the index | Functional index: `CREATE INDEX ON t (LOWER(col))` |

### Connection pooling

Opening a PostgreSQL connection takes 5-20 ms (TCP + TLS + auth + fork). A busy app opening/closing connections per request wastes hundreds of ms.

- **Application-level:** `pg.Pool` in Node.js, `HikariCP` in Java, `sqlx::Pool` in Rust.
- **External pooler (production):** **PgBouncer** in transaction mode. Sits between your app and PostgreSQL. 1,000 app connections share 50 real PostgreSQL connections. Essential when you have many serverless functions or microservices.

### VACUUM and ANALYZE

PostgreSQL's MVCC creates dead tuples on every `UPDATE` and `DELETE` (the old version stays until vacuumed). `VACUUM` reclaims that space. `ANALYZE` updates the statistics the planner uses to make cost estimates.

**Autovacuum** handles both automatically. When it doesn't keep up (high-write tables, tables with millions of updates), performance degrades:

- Stale stats → planner picks bad plans.
- Dead tuples → table bloat → more pages to scan.

Monitor: `SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;`

### Bloat

When `VACUUM` can't reclaim space (a long-running transaction holds a snapshot), the table grows permanently. `VACUUM FULL` rewrites the table but takes an `ACCESS EXCLUSIVE` lock. In production, use `pg_repack` for online compaction.

## Why these design choices

**Why a cost-based optimizer?** Rule-based optimizers ("always use an index if one exists") make wrong choices when the index is less selective than a sequential scan. Cost-based optimizers use actual statistics — row counts, value distributions — to make data-driven decisions. This is why `ANALYZE` matters: without fresh stats, the optimizer is guessing.

**Why not index everything?** Each index is a separate data structure maintained on every write. A table with 20 indexes does 21 writes per insert. Write-heavy workloads (event logging, session tracking) suffer dramatically from over-indexing. The sweet spot is indexing exactly the columns that appear in your query `WHERE`, `JOIN`, and `ORDER BY` clauses.

**Why connection pooling?** PostgreSQL forks a new backend process per connection. Each process consumes ~5-10 MB of memory. 1,000 connections = 10 GB of memory just for connection overhead. A pool of 50 connections serves the same traffic with 500 MB. This is the single biggest production performance win for most applications.

**When you'd pick differently.** In read-heavy OLAP workloads, index everything you query and don't worry about write speed. In append-only log tables, BRIN indexes are tiny and effective. In serverless environments (Lambda, Cloud Functions), an external pooler like PgBouncer is mandatory because each invocation opens a new connection.

## Production-quality code

```sql
-- Diagnose a slow query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.id, o.amount, u.name
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.user_id = 42
  AND o.created_at > now() - INTERVAL '7 days'
ORDER BY o.created_at DESC;

-- If plan shows Seq Scan on orders, add a composite index:
CREATE INDEX CONCURRENTLY idx_orders_user_date
ON orders (user_id, created_at DESC);

-- Functional index for case-insensitive email lookup
CREATE INDEX idx_users_lower_email
ON users (LOWER(email));

SELECT * FROM users WHERE LOWER(email) = LOWER($1);

-- Partial index for pending orders only
CREATE INDEX idx_orders_pending
ON orders (user_id, created_at)
WHERE status = 'pending';

-- Keyset pagination (replaces OFFSET)
SELECT id, title, created_at
FROM posts
WHERE (created_at, id) < ($1::timestamptz, $2::integer)
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Batch fetch to eliminate N+1
SELECT * FROM orders
WHERE user_id = ANY($1::integer[])
ORDER BY user_id, created_at DESC;
```

Application-level pooling (Node.js):

```ts
import pg from "pg";

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});

const result = await pool.query(
  "SELECT id, title FROM posts WHERE author_id = $1 ORDER BY created_at DESC LIMIT 10",
  [userId]
);
```

## Security notes

- **`EXPLAIN` can leak information.** Showing query plans to end users reveals table names, column names, index names, and row-count estimates. Never expose `EXPLAIN` output through an API.
- **`CREATE INDEX CONCURRENTLY` prevents denial-of-service.** A regular `CREATE INDEX` acquires a write lock, blocking all inserts and updates until complete. On a large table this can last minutes. `CONCURRENTLY` avoids the lock but takes longer and can't run inside a transaction.
- **Connection pool credentials.** PgBouncer's connection string includes the database password. Protect the PgBouncer config file with filesystem permissions and never commit it to version control.
- **Monitoring queries.** `pg_stat_activity` shows all currently running queries, including query text. Restrict access to this view to admin roles — it can reveal sensitive parameter values.

## Performance notes

This entire chapter *is* about performance, but here are the highest-leverage habits:

- **Measure first.** Never optimise blindly. Run `EXPLAIN ANALYZE` on the actual query with actual data. A query that takes 2 ms doesn't need an index.
- **Composite indexes for filter + sort.** `CREATE INDEX ON orders (user_id, created_at DESC)` covers both `WHERE user_id = $1` and `ORDER BY created_at DESC` in a single index scan — no sort step.
- **Covering indexes (INCLUDE).** `CREATE INDEX ON orders (user_id) INCLUDE (amount, status)` lets the engine answer the query from the index alone (index-only scan) without touching the table heap.
- **`pg_stat_statements` for top-N slowest queries.** Enable this extension and query `SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10` to find your biggest bottlenecks.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Query uses Seq Scan on a 10M-row table | No index on the `WHERE` column | Add a B-tree index; verify with `EXPLAIN` |
| 2 | `EXPLAIN` estimated 10 rows, actual was 100,000 | Stale statistics | Run `ANALYZE table_name` to update stats |
| 3 | `CREATE INDEX` locks the table for minutes | Regular (non-concurrent) index creation | Use `CREATE INDEX CONCURRENTLY` |
| 4 | Application uses 500 database connections, PostgreSQL OOM | No connection pooling | Add `pg.Pool` (app-side) or PgBouncer (infra-side) |
| 5 | Table grows to 100 GB despite only 10 GB of live data | Dead tuples from high `UPDATE`/`DELETE` without vacuum | Tune autovacuum thresholds; use `pg_repack` for one-time compaction |
| 6 | `WHERE LOWER(email) = $1` ignores the index on `email` | Functional transformation on the column | Create `CREATE INDEX ON users (LOWER(email))` |

## Practice

**Warm-up.** Run `EXPLAIN` on `SELECT * FROM orders WHERE user_id = 42`. Note whether it shows Seq Scan or Index Scan.

**Standard.** Create an index on `orders(user_id, created_at)`. Re-run `EXPLAIN ANALYZE` on the same query and compare the plan.

**Bug hunt.** A query `SELECT * FROM users WHERE email LIKE '%@gmail.com'` is slow despite a B-tree index on `email`. Why doesn't the index help? What index type would?

**Stretch.** Create a composite index that covers both filter and sort: `orders(user_id, created_at DESC)`. Write a query that uses it for `WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10` and verify with `EXPLAIN` that there's no Sort step.

**Stretch++.** Install and configure PgBouncer in transaction pooling mode locally. Connect your Node.js application through PgBouncer instead of directly to PostgreSQL. Compare connection times with and without the pooler.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

If no index exists, you'll see:

```
Seq Scan on orders  (cost=0.00..2500.00 rows=10 width=…)
  Filter: (user_id = 42)
```

**Standard.**

```sql
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at);

EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;
```

Now shows:

```
Index Scan using idx_orders_user_date on orders  (cost=0.42..8.44 rows=10 width=…)
  Index Cond: (user_id = 42)
```

**Bug hunt.** B-tree indexes support prefix matching (`LIKE 'abc%'`) but not suffix/infix matching (`LIKE '%abc'`). The leading `%` prevents the index from being used. Fix: install `pg_trgm` and create a GIN trigram index:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_users_email_trgm ON users USING GIN (email gin_trgm_ops);
```

**Stretch.**

```sql
CREATE INDEX idx_orders_user_date_desc
ON orders (user_id, created_at DESC);

EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 10;
```

Plan should show `Index Scan` with no `Sort` node — the index provides the rows in the requested order.

**Stretch++.** PgBouncer config (`pgbouncer.ini`):

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

Connect your app to `postgres://user:pass@localhost:6432/mydb`. Connection acquisition should drop from ~10ms to <1ms.

</details>

## Quiz

1. The fastest way to see a query's execution plan:
   (a) `SHOW PLAN`  (b) `EXPLAIN` (estimated)  (c) `EXPLAIN ANALYZE` (runs query, reports actuals)  (d) both b and c, depending on need

2. B-tree indexes help with:
   (a) `LIKE '%suffix'`  (b) equality, range, and ordered scans  (c) JSONB containment  (d) none of the above

3. Every index costs:
   (a) nothing  (b) write speed and disk space  (c) only disk space  (d) read speed

4. `OFFSET 100000 LIMIT 10`:
   (a) is identical to cursor pagination  (b) is slow — scans and discards 100k rows  (c) is always fast  (d) is a syntax error

5. Connection pooling:
   (a) is optional for all applications  (b) is standard for production PostgreSQL deployments  (c) is deprecated  (d) replaces indexing

**Short answer:**

6. Why does a functional transformation (like `LOWER(col)`) defeat a plain index on `col`?
7. Name one reason not to index every column in a table.

*Answers: 1-d, 2-b, 3-b, 4-b, 5-b, 6-The index stores values of `col` as-is. When the query applies LOWER() the engine compares the transformed value, which doesn't match any index entry. A functional index on LOWER(col) stores the transformed values, 7-Each index must be updated on every write (INSERT/UPDATE/DELETE). A table with many indexes has significantly slower write throughput and consumes more disk space — resources wasted if those indexes are never queried.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-performance — mini-project](mini-projects/11-performance-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- **Measure first:** `EXPLAIN ANALYZE` is your most important tool. Never guess at performance.
- **Index what you query:** composite indexes for filter + sort, functional indexes for transformations, partial indexes for filtered subsets.
- **Connection pooling is non-negotiable in production:** `pg.Pool` in the app, PgBouncer between app and database.
- **Autovacuum keeps the planner honest:** monitor dead tuples and stale statistics.

## Further reading

- Markus Winand, [Use the Index, Luke](https://use-the-index-luke.com/) — the best free resource on SQL indexing.
- [PostgreSQL 16 — EXPLAIN](https://www.postgresql.org/docs/16/sql-explain.html)
- [PostgreSQL 16 — Index Types](https://www.postgresql.org/docs/16/indexes-types.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/)
- Next module: [Module 12 — HTTP Servers](../12-http-servers/README.md)
