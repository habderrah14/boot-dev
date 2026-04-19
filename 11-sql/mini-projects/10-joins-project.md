# Mini-project — 10-joins

_Companion chapter:_ [`10-joins.md`](../10-joins.md)

**Goal.** Build a SQL report: per user, their order count, total spend, and last order date. Include users with no orders.

**Acceptance criteria:**

- Uses `LEFT JOIN` + `GROUP BY`.
- Returns columns: `user_id`, `user_name`, `order_count`, `total_spend`, `last_order_date`.
- Users with no orders show `order_count = 0`, `total_spend = 0`, `last_order_date = NULL`.
- Sorted by `total_spend DESC`.
- Works on your seeded data.

**Hints:**

- Use `COUNT(o.id)` not `COUNT(*)` — the latter counts 1 even for NULL-only rows.
- Use `COALESCE(SUM(o.amount), 0)` to turn NULL sums into 0.

**Stretch:** Add a `tier` column using `CASE`: "whale" (> $1,000), "regular" (> $100), "new" (0 orders), "small" (everything else). Then add a second query that shows the distribution of tiers.
