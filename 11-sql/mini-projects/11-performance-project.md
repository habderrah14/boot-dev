# Mini-project — 11-performance

_Companion chapter:_ [`11-performance.md`](../11-performance.md)

**Goal.** Seed a 1,000,000-row `events` table and benchmark queries before and after adding indexes.

**Acceptance criteria:**

- `events` table with `id`, `user_id`, `event_type`, `payload JSONB`, `created_at`.
- 1M rows with varied `user_id` (1-10,000), `event_type` (5-10 distinct values), and `created_at` (spanning 1 year).
- Benchmark query: `SELECT * FROM events WHERE user_id = 42 AND created_at > now() - INTERVAL '30 days' ORDER BY created_at DESC LIMIT 20`.
- Run `EXPLAIN ANALYZE` before and after adding `CREATE INDEX ON events (user_id, created_at DESC)`.
- Report timing difference.

**Hints:**

- Use `generate_series(1, 1000000)` with `(random() * 10000)::int` for `user_id`.
- Use `now() - (random() * INTERVAL '365 days')` for `created_at`.
- Array of event types: `(ARRAY['click','view','purchase','signup','logout'])[1 + (random()*4)::int]`.

**Stretch:** Add a GIN index on `payload` and benchmark a JSONB containment query: `WHERE payload @> '{"source": "mobile"}'`. Compare GIN scan time to sequential scan.
