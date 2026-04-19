# Chapter 01 — Introduction

> SQL is the language of relational data. You'll use it more than any single programming language across a career — learn it like you mean it.

## Learning objectives

By the end of this chapter you will be able to:

- Explain what a relational database is and why the model endures.
- Connect to PostgreSQL via `psql` and navigate its meta-commands.
- Write your first `SELECT` statement.
- Distinguish between PostgreSQL, MySQL, and SQLite — and know when each shines.
- Run PostgreSQL locally (native or Docker).

## Prerequisites & recap

- A terminal and basic command-line skills ([Module 02](../02-linux/README.md)).

## The simple version

A relational database is a collection of spreadsheets that know about each other. Each "spreadsheet" is a **table** with named columns and typed rows. You talk to these tables using **SQL** — a language that lets you ask questions ("give me every user who signed up this month") and make changes ("update their plan to premium"). The database engine figures out the fastest way to answer you; you just describe *what* you want, not *how* to get it.

PostgreSQL, MySQL, and SQLite all speak SQL with minor dialect differences. This book uses PostgreSQL because it's the strictest and most feature-rich — what you learn transfers easily to the others.

## In plain terms (newbie lane)

This chapter is really about **Introduction**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌──────────┐    SQL statement    ┌────────────────────┐
  │  Client   │ ─────────────────> │    PostgreSQL       │
  │ (psql,    │                    │  ┌──────────────┐   │
  │  app,     │                    │  │   Parser     │   │
  │  GUI)     │ <───────────────── │  │   Planner    │   │
  └──────────┘    result rows      │  │   Executor   │   │
                                   │  └──────┬───────┘   │
                                   │         │           │
                                   │  ┌──────▼───────┐   │
                                   │  │  Tables on   │   │
                                   │  │    disk      │   │
                                   │  └──────────────┘   │
                                   └────────────────────┘

  Figure 1-1: You send SQL; the engine parses, plans,
  executes, and returns rows.
```

## Concept deep-dive

### What is a relational database?

A set of **tables**, each a grid of **rows** (records) and **columns** (attributes), connected to each other through **keys**. SQL is the declarative language you use to query and mutate them — you describe the result you want, and the engine decides the execution strategy.

Edgar Codd invented the relational model in 1970. Over fifty years later it's still dominant because the core idea — tables plus set math plus declarative queries — is simple enough to reason about yet powerful enough to model almost any business domain.

### Why SQL and not just an ORM?

ORMs generate SQL for you. That's fine for simple CRUD, but the moment you need a report, a migration, a performance diagnosis, or a query the ORM can't express, you're back to raw SQL. If you don't know it, you're stuck. Think of SQL as the assembly language of data: you don't write it for everything, but you'd better be able to read and write it when you need to.

### The big three engines

| Engine | Licence | Sweet spot | Strictness |
|---|---|---|---|
| **PostgreSQL** | Open source (permissive) | Feature-rich apps, analytics, strict typing | High |
| **MySQL / MariaDB** | Open source (GPL) | Web apps, read-heavy workloads, wide hosting support | Medium |
| **SQLite** | Public domain | Embedded apps, local dev, mobile, CLI tools | Low |

All three speak SQL with small dialect differences. Learning PostgreSQL first transfers easily because its stricter behaviour catches mistakes earlier.

### Install PostgreSQL

```bash
# Ubuntu / Debian
sudo apt install postgresql
sudo systemctl status postgresql

# macOS
brew install postgresql@16
brew services start postgresql@16
```

Or run it in Docker — the fastest way to get a disposable instance (see [Module 14](../14-docker/README.md)):

```bash
docker run --name pg16 \
  -e POSTGRES_PASSWORD=pw \
  -p 5432:5432 \
  -d postgres:16
```

### Connect via `psql`

`psql` is the official PostgreSQL CLI — your SQL REPL:

```bash
psql -h localhost -U postgres
```

Essential meta-commands inside `psql`:

| Command | What it does |
|---|---|
| `\l` | List all databases |
| `\c mydb` | Connect to a database |
| `\dt` | List tables in current schema |
| `\d users` | Describe a table's columns and constraints |
| `\x` | Toggle expanded (vertical) output |
| `\timing` | Show query execution time |
| `\q` | Quit |

### Your first query

```sql
SELECT 'hello, world';
```

Now something more useful — create a table, insert rows, read them back:

```sql
CREATE TABLE users (
  id    SERIAL PRIMARY KEY,
  name  TEXT NOT NULL
);

INSERT INTO users (name) VALUES ('Ada'), ('Alan');

SELECT * FROM users;
```

You just did your first Create, Read operations. The rest of this module builds on exactly this loop.

### Case and formatting conventions

SQL keywords are case-insensitive; most codebases uppercase them for visibility. Identifiers (table and column names) are also case-insensitive *unless* you double-quote them — at which point PostgreSQL preserves their exact case:

```sql
SELECT name FROM users;    -- same as
select NAME from USERS;

-- but this is case-sensitive because of double quotes:
CREATE TABLE "MixedCase" (id INT);
SELECT * FROM "MixedCase";     -- must quote forever
SELECT * FROM mixedcase;       -- ERROR: relation "mixedcase" does not exist
```

Prefer `snake_case` names (`first_name`, not `firstName`) and avoid double-quoting. Future you will thank present you.

## Why these design choices

**Why declarative?** Imperative code says *how* — loop through rows, check each one, collect matches. SQL says *what* — "give me rows where status is 'paid'". The declarative approach lets the engine choose the fastest path (sequential scan, index scan, parallel workers) without you rewriting your code. This separation of intent from execution is why SQL survived five decades of hardware revolutions.

**Why PostgreSQL as the teaching default?** MySQL silently truncates data that's too long for a column; SQLite happily stores a string in an INTEGER column. PostgreSQL rejects both. Strictness hurts at first but prevents entire classes of bugs in production. Moving from strict to lenient is easy; the reverse is painful.

**Why not start with an ORM?** ORMs are an abstraction. Abstractions leak. If you learn the ORM first, every leaked abstraction becomes a mystery. If you learn SQL first, the ORM becomes a convenience whose generated queries you can read, diagnose, and override.

## Production-quality code

```sql
-- Create a bookstore database from scratch
CREATE DATABASE bookstore;
\c bookstore

CREATE TABLE books (
  id          SERIAL PRIMARY KEY,
  title       TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);

INSERT INTO books (title, price_cents) VALUES
  ('SICP', 5995),
  ('The C Programming Language', 3995),
  ('Designing Data-Intensive Applications', 4499)
RETURNING id, title, price_cents;
```

Connecting from a Node.js application:

```ts
import pg from "pg";

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
});

const result = await pool.query(
  "SELECT id, title, price_cents FROM books WHERE price_cents > $1",
  [4000]
);

for (const row of result.rows) {
  console.log(`${row.title}: $${(row.price_cents / 100).toFixed(2)}`);
}

await pool.end();
```

Why `pg.Pool` instead of `pg.Client`? Opening a fresh connection for every query takes ~5-20 ms of TCP + TLS handshake. A pool keeps connections warm and reuses them. In production this is non-negotiable.

## Security notes

- **SQL injection starts on day one.** The moment you concatenate user input into a SQL string, an attacker owns your database. Always use parameterized queries (`$1`, `$2`, …). Even in `psql` scripts, prefer `\set` variables over string pasting.
- **Default `postgres` superuser.** Never run application queries as the `postgres` superuser. Create a role with the minimum privileges your app needs (`GRANT SELECT, INSERT, UPDATE ON ...`). If the app is compromised, the blast radius is smaller.
- **Connection strings in environment variables.** Never hard-code `DATABASE_URL` in source files. Use environment variables or a secrets manager.

## Performance notes

At this stage, performance isn't your bottleneck — understanding is. But two habits pay off from the start:

- **Avoid `SELECT *` in application code.** It fetches every column, even ones you'll never use. Naming columns explicitly lets the engine skip unnecessary I/O and makes your intent clear.
- **Use `\timing` in `psql`.** It prints how long each statement took. You'll develop an intuition for what "fast" looks like before you learn `EXPLAIN`.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Money amounts drift by fractions of a cent | Stored as `FLOAT` / `DOUBLE PRECISION` | Use `NUMERIC` or store as integer cents |
| 2 | "relation does not exist" after `CREATE TABLE "Users"` | Double-quoted identifier preserves case; unquoted `users` doesn't match | Never double-quote identifiers — use lowercase `snake_case` |
| 3 | Changes disappear after `psql` session | Multi-statement script outside a transaction, error rolled back silently | Wrap related statements in `BEGIN; … COMMIT;` |
| 4 | Node app hangs on shutdown | `pg.Client` left open, event loop never exits | Use `pg.Pool` and call `pool.end()` on shutdown |
| 5 | "password authentication failed" in Docker | Default user is `postgres`, password must match `-e POSTGRES_PASSWORD=…` | Check your connection string matches the Docker env vars |

## Practice

**Warm-up.** Start PostgreSQL locally (native or Docker). Open `psql`, run `SELECT version();`, and confirm you're on PostgreSQL 16+.

**Standard.** Create a `books` table with `id SERIAL PRIMARY KEY`, `title TEXT NOT NULL`, and `price_cents INTEGER NOT NULL CHECK (price_cents >= 0)`. Insert five rows and select them back ordered by price descending.

**Bug hunt.** You created a table with `CREATE TABLE "Users" (…)`. Now `SELECT * FROM Users;` returns `ERROR: relation "users" does not exist`. Why?

**Stretch.** Connect to your local PostgreSQL from a Node.js script using `pg.Pool`. Run `SELECT * FROM books` and print each row.

**Stretch++.** Run PostgreSQL in Docker with a named volume so data survives `docker rm`. Stop and recreate the container, then verify your books are still there.

<details><summary>Show solutions</summary>

**Warm-up.**

```bash
# Native
psql -U postgres -c "SELECT version();"

# Docker
docker exec -it pg16 psql -U postgres -c "SELECT version();"
```

**Standard.**

```sql
CREATE TABLE books (
  id          SERIAL PRIMARY KEY,
  title       TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);

INSERT INTO books (title, price_cents) VALUES
  ('SICP', 5995),
  ('TAOCP Vol 1', 7999),
  ('DDIA', 4499),
  ('K&R C', 3995),
  ('TCP/IP Illustrated', 6500);

SELECT * FROM books ORDER BY price_cents DESC;
```

**Bug hunt.** Double-quoted `"Users"` preserves the capital U. Unquoted `Users` is folded to lowercase `users`, which doesn't match `"Users"`. Fix: don't double-quote — use `CREATE TABLE users (…)`.

**Stretch.**

```ts
import pg from "pg";
const pool = new pg.Pool({ connectionString: "postgres://postgres:pw@localhost:5432/postgres" });
const { rows } = await pool.query("SELECT * FROM books");
console.table(rows);
await pool.end();
```

**Stretch++.**

```bash
docker volume create pgdata
docker run --name pg16 \
  -e POSTGRES_PASSWORD=pw \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 -d postgres:16

# Insert books…
docker rm -f pg16
# Recreate with same volume:
docker run --name pg16 \
  -e POSTGRES_PASSWORD=pw \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 -d postgres:16

# Data survives because the volume outlives the container.
docker exec -it pg16 psql -U postgres -c "SELECT * FROM books;"
```

</details>

## Quiz

1. A relational database organises data as:
   (a) documents in collections  (b) tables of rows and columns, related by keys  (c) key-value pairs  (d) graph nodes and edges

2. SQL keywords are:
   (a) always uppercase  (b) always lowercase  (c) case-insensitive unless the identifier is double-quoted  (d) case-sensitive

3. The PostgreSQL CLI tool is:
   (a) `mysql`  (b) `psql`  (c) `sqlplus`  (d) `mongo`

4. Money should be stored as:
   (a) `FLOAT`  (b) `NUMERIC` or integer cents  (c) `TEXT`  (d) `REAL`

5. Unquoted identifiers in PostgreSQL are:
   (a) preserved exactly  (b) folded to lowercase  (c) folded to uppercase  (d) random

**Short answer:**

6. Why should you prefer `NUMERIC` (or integer cents) over `FLOAT` for monetary values?
7. Name one advantage of learning PostgreSQL before MySQL or SQLite.

*Answers: 1-b, 2-c, 3-b, 4-b, 5-b, 6-FLOAT uses binary floating point which cannot represent many decimal fractions exactly, leading to rounding errors that accumulate; NUMERIC stores exact decimal values, 7-PostgreSQL is the strictest of the three — it rejects bad data that MySQL or SQLite would silently accept, so habits you form carry safely to the other engines.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-introduction — mini-project](mini-projects/01-introduction-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- SQL is a declarative language; PostgreSQL, MySQL, and SQLite are engines that execute it.
- `psql` is your REPL — learn the meta-commands (`\l`, `\dt`, `\d`, `\timing`).
- Use `NUMERIC` or integer cents for money, `snake_case` for identifiers, and parameterized queries from day one.
- Always use a connection pool (`pg.Pool`) in application code.

## Further reading

- [PostgreSQL 16 Official Tutorial](https://www.postgresql.org/docs/16/tutorial.html)
- [PostgreSQL Data Types](https://www.postgresql.org/docs/16/datatype.html)
- Next: [Tables](02-tables.md)
