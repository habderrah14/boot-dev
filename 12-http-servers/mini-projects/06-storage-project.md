# Mini-project — 06-storage

_Companion chapter:_ [`06-storage.md`](../06-storage.md)

**Goal.** Implement a real `UserStorage` using Drizzle + Postgres (via Docker). Run the same service tests against both the memory and Postgres adapters.

**Acceptance criteria:**

- Drizzle schema for `users` table with `id`, `email`, `name`, `created_at`.
- Migration file checked into git.
- `makePostgresUserStorage(pool)` satisfies the `UserStorage` interface.
- `makeMemoryUserStorage()` also satisfies the same interface.
- Service tests run against both adapters and pass.
- Docker Compose file for local Postgres.
- Transaction helper used for any multi-statement operations.

**Hints:**

- Start with `docker run --rm -e POSTGRES_PASSWORD=test -p 5432:5432 postgres:16` for quick local dev.
- Use `RETURNING *` in your INSERT queries to avoid a second SELECT.
- Run integration tests with `DATABASE_URL=postgres://...` and unit tests with the memory adapter.

**Stretch:** Add a `drizzle-kit` script to your `package.json` that generates and applies migrations. Write a CI step that runs migrations against a fresh Postgres and then runs the test suite.
