# Mini-project — 07-aggregations

_Companion chapter:_ [`07-aggregations.md`](../07-aggregations.md)

**Goal.** Build a SQL report dashboard: weekly revenue, weekly active users (WAU), and top 10 products by units sold. Use CTEs and window functions.

**Acceptance criteria:**

- Three CTEs: `weekly_revenue`, `weekly_active_users`, `top_products`.
- `weekly_revenue` includes a `week_over_week_growth_pct` column using `LAG`.
- `top_products` uses `ROW_NUMBER` to rank within a single query.
- Final `SELECT` joins the three CTEs into a single result.
- Works on your seeded `orders`, `order_items`, and `products` tables.

**Hints:**

- Use `date_trunc('week', created_at)` for weekly grouping.
- WAU = `COUNT(DISTINCT user_id)` per week.
- Growth: `(current_week - last_week) / last_week * 100`.

**Stretch:** Add a 4-week moving average of revenue using a window frame: `AVG(revenue) OVER (ORDER BY week ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)`.
