# Mini-project — 08-subqueries

_Companion chapter:_ [`08-subqueries.md`](../08-subqueries.md)

**Goal.** Build a report using `LATERAL`: for each user, include their last 3 orders and their lifetime spend in a single query.

**Acceptance criteria:**

- Query returns: `user_id`, `user_name`, `lifetime_spend`, `order_id`, `order_amount`, `order_date`.
- Users with zero orders still appear (use `LEFT JOIN LATERAL`).
- Lifetime spend is computed via a scalar subquery or a separate CTE.
- Works on your seeded data.

**Hints:**

- Use `LEFT JOIN LATERAL (… LIMIT 3) ON TRUE` for the last 3 orders.
- Compute `lifetime_spend` in a CTE and join it in.
- Index `orders(user_id, created_at DESC)` for optimal performance.

**Stretch:** Add each order's rank within the user's history using `ROW_NUMBER()` inside the `LATERAL` subquery.
