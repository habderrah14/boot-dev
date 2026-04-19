# Chapter 09 — Normalization

> Normalization is the art of storing each fact in exactly one place. It's the difference between a schema that stays honest and a schema that rots.

## Learning objectives

By the end of this chapter you will be able to:

- State the first three normal forms (1NF, 2NF, 3NF) and apply them to a messy table.
- Identify update, insertion, and deletion anomalies caused by denormalization.
- Design junction tables for many-to-many relationships.
- Know when (and why) to deliberately denormalize.
- Explain higher normal forms (BCNF, 4NF) at a conceptual level.

## Prerequisites & recap

- [Tables](02-tables.md) — creating tables with typed columns.
- [Constraints](03-constraints.md) — foreign keys and referential integrity.

## The simple version

Imagine a spreadsheet where every row contains the customer's name, address, and order details all in one row. If the customer changes their address, you have to update every order row — miss one and you have conflicting data. **Normalization** is the process of breaking that flat spreadsheet into separate tables (customers, addresses, orders) so that each fact is stored exactly once. When you need to combine them, you use joins. The result: fewer bugs, smaller storage, and a schema that doesn't fight you when requirements change.

## In plain terms (newbie lane)

This chapter is really about **Normalization**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Unnormalized (flat)
  ┌──────────────────────────────────────────────────┐
  │ order_id │ customer │ city    │ product │ qty    │
  ├──────────┼──────────┼─────────┼─────────┼────────┤
  │ 1        │ Alice    │ London  │ Widget  │ 3      │
  │ 2        │ Alice    │ London  │ Gadget  │ 1      │  "London"
  │ 3        │ Bob      │ Paris   │ Widget  │ 2      │  stored 2×
  └──────────────────────────────────────────────────┘  for Alice

                          ▼  normalize

  customers               orders              products
  ┌────┬────────┬───────┐  ┌────┬─────┬─────┬─────┐  ┌────┬────────┐
  │ id │ name   │ city  │  │ id │c_id │p_id │ qty │  │ id │ name   │
  ├────┼────────┼───────┤  ├────┼─────┼─────┼─────┤  ├────┼────────┤
  │ 1  │ Alice  │London │  │ 1  │  1  │  1  │  3  │  │ 1  │ Widget │
  │ 2  │ Bob    │Paris  │  │ 2  │  1  │  2  │  1  │  │ 2  │ Gadget │
  └────┴────────┴───────┘  │ 3  │  2  │  1  │  2  │  └────┴────────┘
                           └────┴─────┴─────┴─────┘
  Each fact stored once.   FKs link tables.

  Figure 9-1: Normalization eliminates redundancy by
  splitting one flat table into related tables.
```

## Concept deep-dive

### Why normalise? Anomalies.

A denormalized schema suffers from three anomalies:

- **Update anomaly:** Alice moves from London to Berlin. You update one order row but forget the other — now Alice lives in two cities.
- **Insertion anomaly:** You can't add a new customer until they place an order (the customer data is embedded in the orders table).
- **Deletion anomaly:** Deleting Bob's only order also deletes the fact that Bob exists.

Normalization eliminates all three by ensuring each fact has exactly one home.

### 1NF — Atomic values

Every cell holds a single, atomic value. No arrays, no comma-separated lists, no nested structures:

| Violates 1NF | Why |
|---|---|
| `tags: "red,blue,green"` | Multiple values in one cell |
| `phones: ["+1-555…", "+44-20…"]` | Array crammed into a text column |

Fix: create a separate table (`post_tags`, `user_phones`) with one row per value.

### 2NF — No partial dependency

Every non-key column depends on the **entire** primary key, not just part of it. Only relevant when you have a composite PK:

Bad: `order_items(order_id, product_id, product_name)` — `product_name` depends only on `product_id`, not on the full composite key `(order_id, product_id)`.

Fix: `product_name` belongs in the `products` table. `order_items` references `product_id` via a foreign key.

### 3NF — No transitive dependency

Non-key columns don't depend on other non-key columns:

Bad:

```
users(id, zip_code, city)
```

`city` is determined by `zip_code`, not by `id`. If `zip_code` determines `city`, then `city` transitively depends on `id` through `zip_code`.

Fix: move `(zip_code, city)` to a `zip_codes` table. `users` stores only `zip_code` as a FK.

### Relationships and junction tables

| Relationship | Implementation |
|---|---|
| **One-to-one** | FK with `UNIQUE` constraint, or merge into one table |
| **One-to-many** | FK on the "many" side (`orders.user_id → users.id`) |
| **Many-to-many** | Junction table with composite PK (`post_tags(post_id, tag_id)`) |

```sql
CREATE TABLE tags (
  id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE post_tags (
  post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);
```

### Benefits of normalization

- **One place to update** — change a customer's city in one row, not hundreds.
- **Compact storage** — no repeated strings.
- **Clear vocabulary** — every entity (customer, product, order) has its own table with its own constraints.
- **Easier evolution** — adding a "phone number" field is a new table, not a schema migration on a 100-column flat table.

### Deliberate denormalization

Sometimes you *intentionally* duplicate data:

- **Performance.** A dashboard query joins 5 tables and runs 50 times per second. A materialized view or a denormalized summary table caches the result.
- **Historical snapshots.** The price on an order line item is the price *at the time of purchase*, not today's price. Copying `price_cents` into `order_items` preserves history.
- **Search indexes.** A full-text search column that concatenates `title || body` for `tsvector` indexing.

**The rule:** normalize by default; denormalize with a documented reason and a strategy to keep the copy in sync (trigger, application code, or scheduled refresh).

### BCNF and beyond

**BCNF (Boyce-Codd Normal Form):** every determinant is a candidate key. Relevant when you have multiple overlapping candidate keys — rare in practice.

**4NF:** no multi-valued dependencies (e.g., a single table storing both a person's hobbies and their phone numbers creates spurious combinations).

**5NF:** no join dependencies.

In practice, if your schema passes 3NF, you're fine for 99% of business applications. The higher forms solve exotic edge cases.

## Why these design choices

**Why normalize by default?** Because anomalies compound. A small inconsistency in week one becomes 10,000 conflicting rows by month six. Fixing a denormalized schema retroactively requires data migration, downtime, and prayer. Starting normalized and denormalizing selectively is cheap; the reverse is expensive.

**Why junction tables for many-to-many?** The alternative — comma-separated IDs in a text column — breaks `JOIN`, prevents foreign key enforcement, makes indexing impossible, and requires string parsing in every query. A junction table is first-class relational: it has its own constraints, indexes, and query semantics.

**Why snapshot prices?** Products change price. Without a snapshot, last year's invoice shows today's price — which might be higher or lower. Financial records, tax reporting, and dispute resolution all require the historical value.

**When you'd pick differently.** In analytics databases (OLAP / data warehouses), wide denormalized tables are standard because the workload is read-heavy and joins are expensive at petabyte scale. In OLTP systems (your application database), normalize.

## Production-quality code

```sql
-- Normalized tagging schema
CREATE TABLE posts (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title TEXT NOT NULL,
  body  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE tags (
  id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE post_tags (
  post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

-- Query: all posts with a specific tag
SELECT p.id, p.title
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name = 'postgresql';

-- Deliberate denormalization: snapshot price at order time
CREATE TABLE order_items (
  id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id        INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id      INTEGER NOT NULL REFERENCES products(id),
  quantity        INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0)
);

-- The JOIN to products gives you the current name;
-- unit_price_cents is the historical price at order time.
SELECT
  oi.order_id,
  p.name AS product_name,
  oi.quantity,
  oi.unit_price_cents,
  oi.quantity * oi.unit_price_cents AS line_total_cents
FROM order_items oi
JOIN products p ON p.id = oi.product_id
WHERE oi.order_id = $1;
```

## Security notes

- **Normalization limits blast radius.** If an attacker gains read access to the `orders` table, a normalized schema leaks order data but not customer emails or addresses — those are in separate tables with separate permissions. A flat table leaks everything.
- **Junction tables need their own permissions.** `post_tags` might seem harmless, but an attacker who can `INSERT` into it can tag any post with any tag — potentially adding a "featured" or "admin" tag. Grant `INSERT` only through application roles.
- **Denormalized copies are data duplication.** If you copy PII (names, emails) into a summary table for performance, you now have two places to scrub when a user requests deletion (GDPR "right to be forgotten"). Document every denormalized copy of PII.

## Performance notes

- **Joins are cheap with indexes.** A 3-table join with indexed foreign keys is typically sub-millisecond. Don't denormalize "for performance" until you've measured with `EXPLAIN ANALYZE` and confirmed the join is actually the bottleneck.
- **Junction tables need indexes on both FK columns.** `PRIMARY KEY (post_id, tag_id)` gives you an index on `(post_id, tag_id)`. But if you query by `tag_id` (all posts with tag X), you need a separate index: `CREATE INDEX ON post_tags(tag_id)`.
- **Over-normalization hurts.** If every lookup requires 8 joins, your queries become complex and slow. A `zip_codes` table is justified if you have millions of users; for a 50-user internal app, just put `city` on the user row. Normalize proportionally to your data scale.
- **Denormalized summary tables are read-optimized.** A `daily_revenue` table eliminates the `GROUP BY` on every dashboard load. The trade-off is write complexity (trigger or cron to maintain it).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Comma-separated values in a column (`"red,blue,green"`) | Violated 1NF — multiple values in one cell | Create a separate table with one row per value |
| 2 | Customer address updated in some order rows but not others | Update anomaly from denormalized data | Normalize: store address in one place |
| 3 | 8-table join for a simple lookup | Over-normalized schema | Denormalize deliberately for frequently-queried paths |
| 4 | Denormalized copy drifts out of sync | No sync strategy (trigger, cron, event) | Add a trigger or scheduled refresh; document the sync mechanism |
| 5 | Invoice shows today's price instead of purchase price | No snapshot: `order_items` joins `products.price` instead of storing its own `unit_price_cents` | Copy the price into `order_items` at order creation time |

## Practice

**Warm-up.** Given this table, list all 1NF violations:

```
students(id, name, courses_csv, phone_numbers)
```

**Standard.** Normalize `users(id, name, zip_code, city)` to 3NF. Show the resulting tables and foreign keys.

**Bug hunt.** Your `posts` table has a `tags` column of type `TEXT` storing comma-separated tag names. A colleague writes `SELECT * FROM posts WHERE tags LIKE '%sql%'`. Why does this also match a post tagged `"nosql"`? What's the proper fix?

**Stretch.** Design a many-to-many `authors ↔ books` relationship with a junction table. Include a `role` column on the junction table (e.g., "author", "editor", "translator").

**Stretch++.** Pick one denormalization in your schema (e.g., caching `order_count` on the `users` table). Implement it with a PostgreSQL trigger that updates the cached value on every `INSERT` and `DELETE` on `orders`.

<details><summary>Show solutions</summary>

**Warm-up.** Two violations: `courses_csv` stores multiple course values in one cell; `phone_numbers` stores multiple phone numbers. Both should be separate tables.

**Standard.**

```sql
CREATE TABLE zip_codes (
  zip_code TEXT PRIMARY KEY,
  city     TEXT NOT NULL
);

CREATE TABLE users (
  id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name     TEXT NOT NULL,
  zip_code TEXT REFERENCES zip_codes(zip_code)
);
```

`city` now depends on `zip_code` (its PK), not transitively on `users.id`.

**Bug hunt.** `LIKE '%sql%'` matches any substring, including "nosql", "mysql", "sql-injection". Fix: normalize tags into a `tags` table + `post_tags` junction table, then query with a join: `JOIN post_tags pt ON … JOIN tags t ON t.id = pt.tag_id WHERE t.name = 'sql'`.

**Stretch.**

```sql
CREATE TABLE authors (
  id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE books (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title TEXT NOT NULL
);

CREATE TABLE book_authors (
  book_id   INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
  author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
  role      TEXT NOT NULL DEFAULT 'author'
              CHECK (role IN ('author', 'editor', 'translator')),
  PRIMARY KEY (book_id, author_id, role)
);
```

**Stretch++.**

```sql
ALTER TABLE users ADD COLUMN order_count INTEGER NOT NULL DEFAULT 0;

CREATE OR REPLACE FUNCTION update_user_order_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE users SET order_count = order_count + 1 WHERE id = NEW.user_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE users SET order_count = order_count - 1 WHERE id = OLD.user_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_count
AFTER INSERT OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION update_user_order_count();
```

</details>

## Quiz

1. 1NF requires:
   (a) one atomic value per cell  (b) two foreign keys minimum  (c) an index on every column  (d) no primary key

2. 2NF addresses:
   (a) single-column PKs  (b) partial dependency on a composite PK  (c) transitive dependencies  (d) many-to-many relationships

3. 3NF eliminates:
   (a) all NULLs  (b) transitive dependencies among non-key columns  (c) composite keys  (d) foreign keys

4. When is denormalization justified?
   (a) always — it's faster  (b) when there's a specific performance or snapshot requirement with a sync strategy  (c) never — it violates relational theory  (d) only in NoSQL databases

5. Many-to-many relationships are implemented with:
   (a) two FKs on one table  (b) a junction table with a composite PK  (c) an array column  (d) a nested table

**Short answer:**

6. Why is 3NF usually sufficient for application databases?
7. Describe one strategy for keeping a denormalized copy in sync.

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b, 6-Higher normal forms (BCNF, 4NF, 5NF) address rare edge cases with overlapping candidate keys or multi-valued dependencies. Most business schemas don't exhibit these patterns, so 3NF eliminates the anomalies you'll actually encounter, 7-A PostgreSQL trigger on the source table that updates the denormalized copy on every INSERT/UPDATE/DELETE. Alternatives: application-level event handler, a scheduled REFRESH MATERIALIZED VIEW, or a CDC pipeline.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-normalization — mini-project](mini-projects/09-normalization-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Normalize to 3NF by default: each fact stored once, related by foreign keys.
- 1NF = atomic values; 2NF = no partial dependencies; 3NF = no transitive dependencies.
- Denormalize deliberately — for performance snapshots, search indexes, or cached aggregates — with a documented sync strategy.
- Junction tables are the relational way to model many-to-many; comma-separated columns are not.

## Further reading

- C. J. Date, *An Introduction to Database Systems* — the definitive reference on normal forms.
- [PostgreSQL 16 — Triggers](https://www.postgresql.org/docs/16/trigger-definition.html) — for implementing denormalized sync.
- Next: [Joins](10-joins.md)
