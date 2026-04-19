# Appendix — Junior backend spine (beyond the core 16)

> These topics appear **between the lines** of Modules 10–15. This page ties them together so you know what to study next after the Boot.dev-shaped path—without inventing fake chapters.

## Structured logging and request IDs

- Emit **one JSON object per line** to stdout from your API; include `request_id`, `route`, `duration_ms`, `user_id` (if any).
- Propagate the same ID to downstream HTTP calls and DB logs when debugging.
- See [HTTP servers — error handling](12-http-servers/05-error-handling.md) and [Docker debug](14-docker/07-debug.md) for where logs show up in containers.

## Testing pyramid (backend)

| Layer           | Examples                     | Where you learned pieces                                                             |
| --------------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| **Unit**        | pure functions, validators   | [Python testing](01-python/05-testing-and-debugging.md), [TS types](09-ts/README.md) |
| **Integration** | API + real DB in CI          | [SQL](11-sql/README.md), [Server storage](12-http-servers/06-storage.md)             |
| **Contract**    | consumer-driven HTTP schemas | [Runtime validation](10-http-clients/10-runtime-validation.md)                       |

Aim for **fast unit, few integration, rare e2e** — slow suites die from neglect.

For a guided reading order and concrete rollout checklist, see [Concept thread — Testing strategy](appendix-threads/testing-strategy.md).

## Schema migrations

- Treat schema changes like **API versions**: backward-compatible steps, expand → migrate data → contract.
- Link: [SQL structuring](11-sql/06-structuring.md), [Normalization](11-sql/09-normalization.md), server chapters that own the schema.

## Twelve-factor style config

- **Config in environment**, not hard-coded secrets.
- **Dev/prod parity** via Docker Compose — [Module 14](14-docker/README.md).
- **Disposability** — processes start fast; see [Servers](12-http-servers/01-servers.md) graceful shutdown.

## REST ergonomics (practical)

- Resources, plural nouns, consistent error envelope, pagination cursors vs offsets, `409` vs `422` honesty.
- Link: [HTTP methods](10-http-clients/07-methods.md), [Server routing](12-http-servers/02-routing.md), [OpenAPI / docs](12-http-servers/10-documentation.md).

## Real-time primer (optional)

- **SSE** — one-way server push over HTTP; simpler than WebSockets for dashboards.
- **WebSockets** — duplex, stateful connections; harder to scale horizontally.
- Not a first-course requirement; interviewers sometimes mention them—read MDN after HTTP is solid.

## Tie-in

- [System design starter](appendix-system-design.md) for vocabulary after this page.
- [Shipping checklist](appendix-shipping-checklist.md) before you call a project interview-ready.
