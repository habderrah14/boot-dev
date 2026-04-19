# Chapter 03 — Constraints

> A constraint is a truth about your data that the database *enforces*. Add them early, add them generously: they prevent bad data that no amount of application code can.

## Learning objectives

By the end of this chapter you will be able to:

- Add primary key, unique, not null, check, and foreign key constraints.
- Name constraints explicitly so error messages and migrations stay readable.
- Choose the right `ON DELETE` / `ON UPDATE` action for each relationship.
- Use deferred constraints when inserting both sides of a cycle.
- Explain why database-level constraints beat application-only validation.

## Prerequisites & recap

- [Tables](02-tables.md) — you can create tables with typed columns and basic constraints.

## The simple version

Constraints are rules you attach to columns or tables that the database enforces on every insert, update, and delete. Think of them as guards at the door: `NOT NULL` says "you must provide a value", `UNIQUE` says "no duplicates allowed", `CHECK` says "this value must pass a test", and a foreign key says "this ID must exist in that other table." The database checks these rules before writing the data, so even if your application has a bug, bad data can't sneak through.

## In plain terms (newbie lane)

This chapter is really about **Constraints**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  INSERT INTO orders (user_id, amount, status)
  VALUES (99, -5, 'banana');

         │
         ▼
  ┌──────────────────────────────┐
  │       Constraint checks      │
  │                              │
  │  FK: user_id=99 exists?  ──> ✗  REJECT (no such user)
  │  CHECK: amount > 0?     ──> ✗  REJECT (negative)
  │  CHECK: status IN (…)?  ──> ✗  REJECT (invalid)
  │  NOT NULL: all present?  ──> ✓  ok
  └──────────────────────────────┘

  Figure 3-1: Every constraint must pass before a
  row is written. One failure rejects the entire row.
```

## Concept deep-dive

### Primary key

A primary key uniquely identifies every row. It implies `UNIQUE` + `NOT NULL` automatically:

```sql
PRIMARY KEY (id)
PRIMARY KEY (user_id, product_id)   -- composite
```

You get exactly one primary key per table. Composite primary keys are common in junction tables (many-to-many relationships).

### Unique

Prevents duplicates in a column or combination of columns:

```sql
email TEXT NOT NULL UNIQUE
CONSTRAINT users_email_unique UNIQUE (email)
```

Unlike a primary key, you can have multiple unique constraints on a table. A `UNIQUE` column still allows `NULL` unless you also add `NOT NULL` — and multiple `NULL` values are permitted by the SQL standard (each `NULL` is considered distinct).

### Not null

```sql
name TEXT NOT NULL
```

This is almost always the right default. Decide explicitly which columns *actually* need to allow `NULL` — don't leave it to chance. A `NULL` in a column that "should" have a value creates ambiguity: does it mean "unknown", "not applicable", or "bug"?

### Check

Arbitrary boolean conditions on column values:

```sql
price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
CONSTRAINT valid_email CHECK (email LIKE '%@%.%')
CONSTRAINT valid_status CHECK (status IN ('pending', 'paid', 'shipped', 'delivered'))
```

`CHECK` can't easily reference other rows or tables — it's not a replacement for application validation on complex rules. But it stops obviously bad data (negative prices, nonsense statuses) at the lowest possible layer.

### Foreign key

```sql
CREATE TABLE posts (
  id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  author_id INTEGER NOT NULL
              REFERENCES users(id)
              ON DELETE CASCADE
              ON UPDATE RESTRICT
);
```

Foreign keys enforce **referential integrity**: you can't create a post referencing a user who doesn't exist, and you can't delete a user who still has posts (unless you've configured what happens).

### `ON DELETE` / `ON UPDATE` actions

| Action | Behaviour |
|---|---|
| `NO ACTION` / `RESTRICT` | Default. Refuses the operation if children exist. |
| `CASCADE` | Deletes (or updates) children when the parent is deleted (or updated). |
| `SET NULL` | Sets the child's FK column to `NULL`. |
| `SET DEFAULT` | Sets the child's FK column to its `DEFAULT` value. |

**`CASCADE` is powerful and irreversible.** Deleting one user silently deletes all their posts, comments, and activity. That might be exactly what you want (cleaning up test data) or exactly what you don't (a support agent accidentally deletes a high-value customer). Choose deliberately.

### Named constraints

```sql
CONSTRAINT pk_users PRIMARY KEY (id)
CONSTRAINT users_email_unique UNIQUE (email)
CONSTRAINT fk_posts_author FOREIGN KEY (author_id) REFERENCES users(id)
CONSTRAINT positive_price CHECK (price_cents >= 0)
```

Without explicit names, PostgreSQL generates names like `orders_user_id_fkey`. Named constraints produce clearer error messages (`violates constraint "positive_price"` vs `violates check constraint "orders_check"`) and make migration scripts self-documenting.

### Deferred constraints

PostgreSQL can delay FK checks until `COMMIT`:

```sql
ALTER TABLE employees
  ADD CONSTRAINT fk_manager
    FOREIGN KEY (manager_id) REFERENCES employees(id)
    DEFERRABLE INITIALLY IMMEDIATE;

BEGIN;
SET CONSTRAINTS fk_manager DEFERRED;
INSERT INTO employees (id, name, manager_id) VALUES (1, 'Alice', 2);
INSERT INTO employees (id, name, manager_id) VALUES (2, 'Bob', 1);
COMMIT;  -- both FKs valid at commit time
```

Useful when inserting both sides of a cycle in one transaction. Without deferral, the first insert would fail because the referenced row doesn't exist yet.

## Why these design choices

**Why enforce at the database level?** Your application has bugs. Your next developer's application has different bugs. A third-party script bypasses your application entirely. The database is the only layer that *every* write passes through. If the constraint lives only in JavaScript, a direct `psql` session, a migration script, or a microservice in another language can all insert bad data.

**Why `NOT NULL` by default?** Every nullable column doubles the mental overhead: you must handle the "what if it's null?" case everywhere. In SQL, `NULL` is infectious — `NULL = NULL` is `NULL`, not `TRUE`. The fewer nullable columns, the fewer surprise query results.

**Why name constraints?** In six months you'll see `ERROR: violates constraint "orders_check"` in your logs at 3 AM. If you'd named it `positive_amount`, you'd know instantly what went wrong without digging into the schema.

**When you'd pick differently.** `CASCADE` is right for cleanup tables (sessions, logs, drafts). `RESTRICT` is right for business-critical relationships (orders referencing users — you don't want to accidentally delete a customer and lose their order history). `SET NULL` is right for optional relationships ("this post's author account was deleted, but the post stays").

## Production-quality code

```sql
CREATE TABLE users (
  id         INTEGER GENERATED ALWAYS AS IDENTITY,
  email      TEXT NOT NULL,
  name       TEXT NOT NULL,
  active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT pk_users PRIMARY KEY (id),
  CONSTRAINT users_email_unique UNIQUE (email),
  CONSTRAINT valid_email CHECK (email LIKE '%@%.%')
);

CREATE TABLE orders (
  id         INTEGER GENERATED ALWAYS AS IDENTITY,
  user_id    INTEGER NOT NULL,
  amount     INTEGER NOT NULL,
  status     TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT pk_orders PRIMARY KEY (id),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT positive_amount CHECK (amount > 0),
  CONSTRAINT valid_status CHECK (
    status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')
  )
);

CREATE TABLE team_memberships (
  team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role    TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'admin')),
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT pk_team_memberships PRIMARY KEY (team_id, user_id)
);
```

## Security notes

- **Foreign keys prevent orphaned references.** Without them, you can delete a user and leave orders pointing at a non-existent `user_id`. At best this causes confusing reports; at worst it creates a data integrity hole that could be exploited (e.g., a new user gets the recycled ID and "inherits" someone else's orders).
- **`CHECK` constraints block obvious injection payloads.** `CHECK (status IN ('pending', 'paid'))` rejects any value that isn't in the whitelist, including SQL fragments an attacker might try to inject through a vulnerable application layer.
- **Composite primary keys in junction tables prevent duplication attacks.** Without `PRIMARY KEY (team_id, user_id)`, an attacker could add themselves to a team multiple times, potentially gaining elevated privileges if the application counts memberships.

## Performance notes

- **Primary keys automatically create a B-tree index.** You never need to add an index on a PK column — it's already there.
- **`UNIQUE` constraints also create an index.** So `UNIQUE (email)` gives you fast lookups on `email` for free.
- **Foreign key columns should be indexed on the child side.** PostgreSQL does *not* automatically index FK columns. Without an index on `orders(user_id)`, deleting a user triggers a sequential scan of the entire `orders` table to check for children. On a large table, this blocks writes for seconds.
- **`CHECK` constraints are evaluated per-row and very fast.** They don't scan other tables; they only look at the current row's values. The cost is negligible.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Deleting a user wipes all their orders, comments, and history | `ON DELETE CASCADE` used for business-critical relationships | Use `RESTRICT` for important data; reserve `CASCADE` for cleanup tables |
| 2 | `NULL` values appear in columns that "should always have a value" | Forgot `NOT NULL` | Add `NOT NULL` during table creation; retrofitting requires backfill |
| 3 | `ERROR: insert or update on table "posts" violates FK constraint` when seeding | Inserting child rows before parent rows | Insert parents first, then children — or use deferred constraints |
| 4 | Deleting a parent row takes 30+ seconds on a large table | No index on the FK column in the child table | `CREATE INDEX ON orders(user_id)` |
| 5 | Error message says `violates constraint "orders_check"` — unclear what failed | Unnamed `CHECK` constraint | Name constraints explicitly: `CONSTRAINT positive_amount CHECK (…)` |

## Practice

**Warm-up.** Add `CHECK (price_cents > 0)` to an existing `products` table. Insert a row with price 0 and confirm it's rejected. Insert a row with price 100 and confirm it succeeds.

**Standard.** Create a `posts` table with a foreign key `author_id` referencing `users(id)` with `ON DELETE CASCADE`. Insert a user, insert two posts, delete the user, and verify the posts are gone.

**Bug hunt.** You run `ALTER TABLE posts ADD CONSTRAINT fk_posts_author FOREIGN KEY (author_id) REFERENCES users(id)` on a table where some `author_id` values don't exist in `users`. What happens? How do you fix it?

**Stretch.** Model a many-to-many relationship between `students` and `courses` with a `enrollments` junction table. Include a composite primary key and appropriate `ON DELETE` actions.

**Stretch++.** Use deferred foreign keys to insert two employees who reference each other as managers in a single transaction.

<details><summary>Show solutions</summary>

**Warm-up.**

```sql
ALTER TABLE products ADD CONSTRAINT positive_price CHECK (price_cents > 0);

INSERT INTO products (name, price_cents) VALUES ('Free', 0);
-- ERROR: new row violates check constraint "positive_price"

INSERT INTO products (name, price_cents) VALUES ('Widget', 100);
-- INSERT 0 1
```

**Standard.**

```sql
CREATE TABLE posts (
  id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title     TEXT NOT NULL,
  body      TEXT NOT NULL DEFAULT ''
);

INSERT INTO users (email, name) VALUES ('test@example.com', 'Test') RETURNING id;
-- id = 1
INSERT INTO posts (author_id, title) VALUES (1, 'Post A'), (1, 'Post B');
DELETE FROM users WHERE id = 1;
SELECT * FROM posts;
-- (0 rows) — CASCADE deleted them
```

**Bug hunt.** The `ADD CONSTRAINT` fails with `ERROR: insert or update on table "posts" violates foreign key constraint`. Fix: delete or update orphaned rows first (`DELETE FROM posts WHERE author_id NOT IN (SELECT id FROM users)`), then add the constraint.

**Stretch.**

```sql
CREATE TABLE students (
  id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE courses (
  id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title TEXT NOT NULL
);

CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (student_id, course_id)
);
```

**Stretch++.**

```sql
CREATE TABLE employees (
  id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name       TEXT NOT NULL,
  manager_id INTEGER,
  CONSTRAINT fk_manager FOREIGN KEY (manager_id)
    REFERENCES employees(id) DEFERRABLE INITIALLY IMMEDIATE
);

BEGIN;
SET CONSTRAINTS fk_manager DEFERRED;
INSERT INTO employees (id, name, manager_id)
  OVERRIDING SYSTEM VALUE VALUES (1, 'Alice', 2);
INSERT INTO employees (id, name, manager_id)
  OVERRIDING SYSTEM VALUE VALUES (2, 'Bob', 1);
COMMIT;
```

</details>

## Quiz

1. `PRIMARY KEY` implies:
   (a) `UNIQUE` + `NOT NULL`  (b) `NOT NULL` only  (c) `UNIQUE` only  (d) `NULL` allowed

2. `ON DELETE CASCADE`:
   (a) refuses the delete  (b) deletes child rows when the parent is deleted  (c) sets child to `NULL`  (d) does nothing

3. A `CHECK` constraint can reference:
   (a) other tables freely  (b) columns within the same row  (c) stored procedures  (d) external APIs

4. Adding `NOT NULL` to a populated column without a default:
   (a) always works  (b) fails if any existing row has `NULL` in that column  (c) silently drops NULLs  (d) promotes NULLs to empty strings

5. A composite primary key:
   (a) is illegal  (b) uses multiple columns to form the key  (c) is the same as a composite unique  (d) can only be defined via `CHECK`

**Short answer:**

6. Give one risk of using `CASCADE` deletes on a business-critical table.
7. Why should you name constraints explicitly?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b, 6-A single accidental parent delete silently removes all children (orders, invoices, etc.) with no undo — you lose business data that may be unrecoverable without a backup, 7-Named constraints produce clear error messages and make migration scripts self-documenting; unnamed ones generate opaque names like "orders_check" that reveal nothing about what went wrong.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-constraints — mini-project](mini-projects/03-constraints-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Constraints are the database's promises — they reject bad data regardless of which client writes it.
- Use `NOT NULL` by default, name every constraint, and index foreign key columns on the child side.
- Choose `ON DELETE` actions deliberately: `RESTRICT` for critical data, `CASCADE` for cleanup tables, `SET NULL` for optional relationships.
- Deferred constraints handle circular references within a transaction.

## Further reading

- [PostgreSQL 16 — Constraints](https://www.postgresql.org/docs/16/ddl-constraints.html)
- [PostgreSQL 16 — Foreign Keys](https://www.postgresql.org/docs/16/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- Next: [CRUD](04-crud.md)
