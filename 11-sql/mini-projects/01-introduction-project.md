# Mini-project — 01-introduction

_Companion chapter:_ [`01-introduction.md`](../01-introduction.md)

**Goal.** Set up PostgreSQL (Docker or native), create a `library` database with `books` and `authors` tables, seed them with at least five rows each, and query them from a Node.js script.

**Acceptance criteria:**

- PostgreSQL is running and accessible via `psql`.
- `authors` table has `id SERIAL PRIMARY KEY` and `name TEXT NOT NULL`.
- `books` table has `id`, `title`, `author_id` (foreign key to `authors`), and `price_cents`.
- At least 5 authors and 5 books exist.
- A Node.js script connects via `pg.Pool`, runs `SELECT b.title, a.name FROM books b JOIN authors a ON a.id = b.author_id`, and prints the results.

**Hints:**

- Insert authors first — books reference them via `author_id`.
- Use `RETURNING id` on the authors insert so you know which IDs to use for books.

**Stretch:** Add a `\timing` benchmark of your query and a `EXPLAIN` plan in a comment at the top of your script.
