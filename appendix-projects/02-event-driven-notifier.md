# Integration project 02 — Event-driven notifier

**Modules touched:** [11 SQL](11-sql/README.md), [12 HTTP servers](12-http-servers/README.md), [14 Docker](14-docker/README.md), [15 Pub/Sub](15-pubsub/README.md), [10 HTTP clients](10-http-clients/README.md).

## Goal

When a row is inserted into a `notifications` table, downstream channels receive work **asynchronously** via a message broker. Implement the **outbox pattern**: HTTP handler writes business data + outbox row in one DB transaction; a publisher process reads the outbox and pushes to RabbitMQ; worker consumers call a fake email HTTP endpoint (mock server or webhook.site).

## Acceptance criteria

1. Schema: `notifications(id, user_id, template, payload jsonb, created_at)` and `outbox(id, aggregate_type, aggregate_id, payload jsonb, published_at)`.
2. `POST /notify` inserts both rows transactionally; returns `202` with `location` header pointing to notification status resource.
3. Publisher service (separate process or loop) marks outbox rows published and publishes durable messages.
4. At least two consumer types (e.g. `email` and `sms` queues) with different routing keys; one consumer simulates failure + retry with DLQ documented.
5. Everything runs under `docker compose` with Postgres + RabbitMQ + API + publisher + consumers.
6. README includes sequence diagram (Mermaid) of the happy path.

## Hints

- Use `SELECT ... FOR UPDATE SKIP LOCKED` when claiming outbox rows.
- Serialize messages with JSON; version the payload with a `schema_version` field.
- Keep idempotency keys on the consumer side to survive duplicate deliveries.

## Stretch extensions

- Metrics endpoint (`/metrics`) counting published vs failed messages.
- Chaos test: `docker kill` a consumer mid-flight; document recovery.
