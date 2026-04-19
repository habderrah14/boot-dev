# Mini-project — 09-normalization

_Companion chapter:_ [`09-normalization.md`](../09-normalization.md)

**Goal.** Take a flat "spreadsheet" table that mixes users, orders, and products into a single row, and normalize it to 3NF.

**Acceptance criteria:**

- Start with this flat table:

```sql
CREATE TABLE flat_orders (
  order_id      INTEGER,
  customer_name TEXT,
  customer_email TEXT,
  customer_city TEXT,
  product_name  TEXT,
  product_price INTEGER,
  quantity      INTEGER,
  order_date    DATE
);
```

- Produce: `customers`, `products`, `orders`, `order_items` tables — all in 3NF.
- Migrate the data from `flat_orders` into the normalized tables using `INSERT … SELECT`.
- Verify with a join query that reconstructs the original flat view.
- Document each normalization step (which anomaly it fixes).

**Hints:**

- Extract customers first (deduplicate by email).
- Extract products next (deduplicate by name).
- Then build orders and order_items with FKs.

**Stretch:** Add a `customer_city → region` lookup table (3NF on the city/region transitive dependency) and a trigger that keeps a `total_amount` cache on the `orders` table.
