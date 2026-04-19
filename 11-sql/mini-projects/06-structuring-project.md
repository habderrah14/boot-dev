# Mini-project — 06-structuring

_Companion chapter:_ [`06-structuring.md`](../06-structuring.md)

**Goal.** Build a `monthly_revenue` materialized view and a query that compares the current month's revenue to last month's using CTEs.

**Acceptance criteria:**

- `orders` table with at least 1,000 rows spanning 3+ months.
- `monthly_revenue` materialized view with columns: `month`, `revenue`, `order_count`.
- A unique index on `month` for concurrent refresh.
- A CTE-based query that outputs: `current_month_revenue`, `last_month_revenue`, `growth_pct`.

**Hints:**

- Use `date_trunc('month', now())` for the current month boundary.
- Growth percentage: `(current - previous) / previous * 100`.
- Handle division by zero with `NULLIF`.

**Stretch:** Add a recursive CTE that generates a series of the last 12 months, then `LEFT JOIN` to `monthly_revenue` so months with zero orders still appear (with `revenue = 0`).
