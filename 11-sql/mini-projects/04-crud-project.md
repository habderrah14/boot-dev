# Mini-project — 04-crud

_Companion chapter:_ [`04-crud.md`](../04-crud.md)

**Goal.** Build a Node.js script that upserts a batch of users from a CSV file, atomically (inside a transaction), and prints how many were inserted vs. updated.

**Acceptance criteria:**

- Read a CSV with columns `email,name`.
- Use `ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name`.
- Wrap the entire batch in `BEGIN; … COMMIT;`.
- Use `RETURNING` and `xmax` to distinguish inserts from updates (`xmax = 0` means insert).
- Print a summary: "Inserted: X, Updated: Y".

**Hints:**

- `xmax` is a PostgreSQL system column. When it's `0`, the row was freshly inserted. When non-zero, it was updated (the `xmax` records the transaction that last modified it).
- Use `pg.Pool.connect()` + `client.query()` for transaction control.

**Stretch:** Add error handling that rolls back the entire batch if any single upsert fails, and reports which row caused the failure.
