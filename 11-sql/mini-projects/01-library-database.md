# Mini-project — Library Database

## Goal

Set up a small library schema, seed data, and query it from an application.

## Deliverable

A PostgreSQL database with `authors` and `books` tables plus a script that queries the join.

## Required behavior

1. Create a `library` database.
2. Define `authors` and `books` tables.
3. Seed at least five rows in each table.
4. Query a join between books and authors from Node.js.
5. Document setup and teardown in README.

## Acceptance criteria

- Tables use sensible types and constraints.
- Foreign keys connect books to authors.
- Query output is readable and correct.
- README explains how to recreate the database from scratch.

## Hints

- Insert authors first and capture IDs with `RETURNING`.
- Keep price values in integer cents.
- Use `pg.Pool` instead of opening individual connections.

## Stretch goals

1. Add a `genres` table and a many-to-many join table.
2. Add a query that returns the top five most expensive books.
3. Include `EXPLAIN` output for one query.
