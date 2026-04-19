# Mini-project — 05-delivery

_Companion chapter:_ [`05-delivery.md`](../05-delivery.md)

**Goal.** Build a reliable pipeline: publisher (with confirms) → durable queue → idempotent consumer → PostgreSQL.

**Acceptance criteria.**

- Producer publishes 1,000 orders, each with a unique `messageId`, and reports how many the broker confirmed.
- Consumer inserts into `orders` + `processed_messages` in one transaction, then acks.
- Kill the consumer mid-batch; restart it; DB contains exactly 1,000 rows (no duplicates, no losses).
- Repeat with `persistent: false` and document what breaks when you restart the broker.

**Hints.** Use `docker run -p 5672:5672 -p 15672:15672 rabbitmq:3-management` so you can watch the queue depth from the UI. Use a simple Postgres container for the database.

**Stretch.** Add the outbox pattern on the publisher side: the API writes to orders + outbox in one transaction, and a relay worker publishes from the outbox table.
