# Chapter 02 — Tables

> A table is the unit of relational design. Every decision you make here — columns, types, keys — echoes through every query you'll ever write against it.

## Learning objectives

By the end of this chapter you will be able to:

- Create, alter, and drop tables with confidence.
- Pick the right PostgreSQL column type for each real-world concept.
- Choose between surrogate and natural primary keys.
- Follow naming conventions that prevent future headaches.
- Use `GENERATED AS IDENTITY` as the modern alternative to `SERIAL`.

## Prerequisites & recap

- [Introduction](01-introduction.md) — you can connect to PostgreSQL via `psql` and run basic SQL.

## The simple version

A table is like a spreadsheet with strict rules: every column has a fixed data type, every row must obey those types, and you define the rules up front with `CREATE TABLE`. Picking the right types — `TEXT` for strings, `TIMESTAMPTZ` for dates, `NUMERIC` for money — saves you from an entire category of bugs that are almost impossible to fix after your table has millions of rows.

## In plain terms (newbie lane)

This chapter is really about **Tables**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  CREATE TABLE users (                        Table on disk
    id    SERIAL PRIMARY KEY,       ┌────┬──────────┬────────────┐
    email TEXT NOT NULL UNIQUE, ──>  │ id │  email   │ created_at │
    created_at TIMESTAMPTZ          ├────┼──────────┼────────────┤
               DEFAULT now()        │  1 │ a@b.c    │ 2025-03-…  │
  );                                │  2 │ x@y.z    │ 2025-03-…  │
                                    └────┴──────────┴────────────┘
  Figure 2-1: CREATE TABLE defines the column blueprint;
  rows are inserted into that shape.
```

## Concept deep-dive

### `CREATE TABLE`

```sql
CREATE TABLE users (
  id          SERIAL PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  name        TEXT NOT NULL,
  active      BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Each column declaration says: name, type, constraints. Get this right and the database enforces your business rules at the storage layer — no amount of buggy application code can violate them.

### Common types (PostgreSQL)

| Category | Types | When to use |
|---|---|---|
| Integer | `SMALLINT`, `INTEGER`, `BIGINT` | Counts, foreign keys, small IDs |
| Auto-id | `SERIAL` / `BIGSERIAL` or `GENERATED AS IDENTITY` | Surrogate primary keys |
| Exact numeric | `NUMERIC(precision, scale)` | Money, precise decimals |
| Approximate | `REAL`, `DOUBLE PRECISION` | Scientific data where rounding is acceptable |
| Text | `TEXT`, `VARCHAR(n)` | Strings — prefer `TEXT` unless you have a real max-length |
| Boolean | `BOOLEAN` | Flags, toggles |
| Date/time | `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ` | Always prefer `TIMESTAMPTZ` |
| UUID | `UUID` | Globally unique IDs, distributed systems |
| JSON | `JSON`, `JSONB` | Semi-structured data; `JSONB` is indexable |
| Binary | `BYTEA` | Small blobs (put large ones on object storage) |

**Why `TEXT` over `VARCHAR(n)`?** PostgreSQL stores them identically. `VARCHAR(255)` is a MySQL-ism that adds a constraint you rarely need. If you genuinely need a length limit (e.g., a country code), `VARCHAR(2)` is fine — otherwise, `TEXT` is simpler.

**Why `TIMESTAMPTZ` over `TIMESTAMP`?** `TIMESTAMP` stores a "wall clock" value with no timezone context. If your server changes timezone, or you have users in multiple zones, stored times become ambiguous. `TIMESTAMPTZ` stores the instant in UTC internally and converts on display. Always use it.

### Primary keys

A column (or combination) that uniquely identifies each row:

- **Surrogate** (`SERIAL`, `BIGSERIAL`, `UUID`) — meaningless to the business, stable forever. A user can change their email; the surrogate ID never changes.
- **Natural** (`email`, `isbn`) — meaningful but rarely truly immutable. What happens when a user changes their email?

Surrogate keys are the safer default. Use natural keys only when the value is genuinely immutable (like an ISO country code).

### `SERIAL` vs `GENERATED AS IDENTITY`

`SERIAL` is the legacy PostgreSQL idiom — it creates a hidden sequence and wires it up via a default. The modern SQL-standard alternative is cleaner:

```sql
CREATE TABLE users (
  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL
);
```

`GENERATED ALWAYS` prevents manual ID insertion (unless you `OVERRIDING SYSTEM VALUE`). It makes intent explicit: the database owns this column. Prefer it for new schemas.

### Constraints preview

- `NOT NULL` — must have a value.
- `UNIQUE` — no duplicates.
- `CHECK (…)` — arbitrary condition.
- `DEFAULT value` — assumed when not provided.
- `REFERENCES other(col)` — foreign key (next chapter).

### `ALTER TABLE`

```sql
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users RENAME COLUMN name TO full_name;
ALTER TABLE users ALTER COLUMN email TYPE CITEXT;
```

**Why this matters in production:** Adding a nullable column with a default is nearly instant (PostgreSQL records the default in the catalog; existing rows aren't rewritten). Adding `NOT NULL` to a populated column requires scanning every row to verify no NULLs exist — on a 100M-row table, that's a lock you'll feel.

### `DROP TABLE`

```sql
DROP TABLE users;              -- errors if table doesn't exist
DROP TABLE IF EXISTS users;    -- safe for scripts and migrations
```

`DROP TABLE` is irreversible (outside a transaction). In production, prefer soft-deletes or renaming before dropping.

### Naming conventions

- Lowercase `snake_case` everywhere.
- Plural table names (`users`, `orders`), singular column names (`email`, `name`).
- Avoid SQL reserved words (`user`, `order`) as table names — you'll have to double-quote them forever, which violates the "never double-quote" rule from Chapter 01.
- Foreign key columns: `<referenced_table_singular>_id` — e.g., `author_id`, `order_id`.

## Why these design choices

**Why types matter.** A column typed `INTEGER` rejects the string `"banana"`. A column typed `TEXT` accepts `"-5.99"` when you meant a price. Types are your first line of validation — free, automatic, and faster than any application-layer check.

**Why surrogate keys by default.** Natural keys feel right ("email *is* the user") until the business changes the rules. A new feature lets users change their email. Now every foreign key pointing at the old email is broken. Surrogate keys decouple identity from meaning.

**Why strict defaults.** In MySQL, inserting a 300-character string into `VARCHAR(255)` silently truncates. PostgreSQL raises an error. Strict behaviour costs you a few minutes of debugging during development; silent truncation costs you hours of forensic data recovery in production.

**When you'd pick differently.** If you're building an embedded app with SQLite, `TEXT` affinity is all you get — strict typing isn't an option. If your table is append-only and will grow to billions of rows, `BIGSERIAL` or `UUID` avoids the 2-billion-row `INTEGER` ceiling. If you're in a heavily sharded distributed system, UUIDs avoid cross-shard sequence coordination.

## Production-quality code

```sql
CREATE TABLE authors (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name  TEXT NOT NULL
);

CREATE TABLE books (
  id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  author_id   INTEGER NOT NULL REFERENCES authors(id),
  title       TEXT NOT NULL,
  isbn        TEXT UNIQUE,
  published   DATE,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE events (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  kind        TEXT NOT NULL,
  payload     JSONB NOT NULL DEFAULT '{}',
  received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO authors (name) VALUES ('Kernighan'), ('Abelson')
RETURNING id, name;

INSERT INTO books (author_id, title, isbn, price_cents) VALUES
  (1, 'The C Programming Language', '978-0131103627', 3995),
  (2, 'SICP', '978-0262510875', 5995)
RETURNING id, title;

INSERT INTO events (kind, payload) VALUES
  ('page_view', '{"url": "/home", "user_id": 42}')
RETURNING id, received_at;
```

## Security notes

- **Column types are a security boundary.** An `INTEGER` column rejects string payloads that might contain injection attempts against downstream consumers. Don't use `TEXT` for everything "because it's easy".
- **`JSONB` is powerful but unconstrained.** Unlike typed columns, `JSONB` accepts any valid JSON. If you store user input in `JSONB`, validate its shape in the application layer or use `CHECK` constraints with `jsonb_typeof()`.
- **Avoid storing secrets in plain-text columns.** Passwords, API keys, tokens — use `pgcrypto` or handle encryption at the application layer. A database backup is a copy of your secrets if they're unencrypted.

## Performance notes

- **`TEXT` vs `VARCHAR(n)` is free.** PostgreSQL stores both the same way internally — `VARCHAR(n)` just adds a length check. No performance difference.
- **`JSONB` vs separate columns.** Queries against typed columns with B-tree indexes are faster than `JSONB` path queries. Use `JSONB` for truly flexible or sparse data, not as a lazy alternative to schema design.
- **`ALTER TABLE ADD COLUMN` with a volatile default** (like `random()`) rewrites the entire table. A static default (like `now()` which is stable within a transaction, or a literal) is recorded in the catalog only — instant even on a billion-row table.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `VARCHAR(255)` everywhere, but some values are longer than 255 | Carried MySQL habits to PostgreSQL | Use `TEXT`; add `CHECK (length(col) <= n)` only when a real limit exists |
| 2 | Timestamps display wrong in different timezones | Used `TIMESTAMP` instead of `TIMESTAMPTZ` | Use `TIMESTAMPTZ`; store instants, not wall-clock strings |
| 3 | `ALTER TABLE ADD COLUMN email TEXT NOT NULL` fails on a populated table | Existing rows have `NULL` for the new column | Add with a `DEFAULT`, or add nullable, backfill, then set `NOT NULL` |
| 4 | Money drifts: `0.1 + 0.2 = 0.30000000000000004` | Used `FLOAT` / `DOUBLE PRECISION` | Use `NUMERIC(12, 2)` or store as integer cents |
| 5 | Table named `user` requires quotes everywhere | `user` is a reserved word in SQL | Name it `users` (plural) or `app_users` |

## Practice

**Warm-up.** Create a `products` table with `id`, `name`, and `price_cents`. Insert two rows and select them.

**Standard.** Add `created_at TIMESTAMPTZ NOT NULL DEFAULT now()` and `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()` columns to your `products` table. Verify defaults work on a new insert.

**Bug hunt.** You run `ALTER TABLE users ADD COLUMN email TEXT NOT NULL;` on a table with 1,000 existing rows. It fails. Why? Propose two fixes.

**Stretch.** Add a `JSONB` `metadata` column to `products`. Insert a row with `'{"color": "red", "weight_kg": 1.5}'`. Write a query that filters on `metadata->>'color'`.

**Stretch++.** Rewrite the `products` table using `GENERATED ALWAYS AS IDENTITY` instead of `SERIAL`. Explain the behavioural difference when someone tries `INSERT INTO products (id, name, price_cents) VALUES (999, 'Hack', 0)`.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
CREATE TABLE products (
  id          SERIAL PRIMARY KEY,
  name        TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);

INSERT INTO products (name, price_cents) VALUES ('Widget', 999), ('Gadget', 2499);
SELECT * FROM products;
```

**Standard.**

```sql
ALTER TABLE products
  ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

INSERT INTO products (name, price_cents) VALUES ('Doohickey', 1599);
SELECT * FROM products;
```

**Bug hunt.** Existing rows have no value for `email`, so they'd be `NULL`, violating `NOT NULL`. Fix 1: `ADD COLUMN email TEXT NOT NULL DEFAULT 'unknown@example.com'` (then backfill real values). Fix 2: Add as nullable, update existing rows, then `ALTER COLUMN email SET NOT NULL`.

**Stretch.**

```sql
ALTER TABLE products ADD COLUMN metadata JSONB NOT NULL DEFAULT '{}';

INSERT INTO products (name, price_cents, metadata)
VALUES ('Gizmo', 3999, '{"color": "red", "weight_kg": 1.5}');

SELECT * FROM products WHERE metadata->>'color' = 'red';
```

**Stretch++.** With `GENERATED ALWAYS AS IDENTITY`, the explicit ID insert fails: `ERROR: cannot insert a non-DEFAULT value into column "id"`. With `SERIAL`, it succeeds (and may collide with the sequence later). `GENERATED ALWAYS` makes the database's ownership of the column explicit.

</details>

## Quiz

1. The preferred general-purpose string type in PostgreSQL is:
   (a) `VARCHAR(255)`  (b) `TEXT`  (c) `CHAR(n)`  (d) `BLOB`

2. Money values should be stored as:
   (a) `FLOAT`  (b) `NUMERIC` or integer cents  (c) `BIGINT` always  (d) `TEXT`

3. `TIMESTAMPTZ` differs from `TIMESTAMP` because:
   (a) they're identical  (b) `TIMESTAMPTZ` is timezone-aware  (c) `TIMESTAMPTZ` is slower  (d) `TIMESTAMP` is timezone-aware

4. A surrogate key is:
   (a) a natural identifier like email  (b) a synthetic identifier like `SERIAL`  (c) a foreign key  (d) a computed column

5. Adding a `NOT NULL` column to an existing table with rows:
   (a) always works instantly  (b) requires a default or backfill  (c) is impossible  (d) silently drops the constraint

**Short answer:**

6. When is `JSONB` a better choice than adding separate columns?
7. Why prefer surrogate keys by default?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b, 6-When the data is truly semi-structured or sparse — e.g. event payloads where different event types have different fields. If you'd need 50 nullable columns for rare attributes JSONB is cleaner, 7-Surrogate keys are immutable and decouple identity from business data. Natural keys can change (user renames email) breaking all foreign key references.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-tables — mini-project](mini-projects/02-tables-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Tables are defined by columns (name + type) and constraints — get both right up front.
- Prefer `TEXT`, `TIMESTAMPTZ`, `NUMERIC` for money, and surrogate keys by default.
- `GENERATED ALWAYS AS IDENTITY` is the modern replacement for `SERIAL`.
- Adding constraints to an existing table is harder than defining them at creation — design carefully.

## Further reading

- [PostgreSQL 16 — Data Types](https://www.postgresql.org/docs/16/datatype.html)
- [PostgreSQL 16 — CREATE TABLE](https://www.postgresql.org/docs/16/sql-createtable.html)
- Next: [Constraints](03-constraints.md)
