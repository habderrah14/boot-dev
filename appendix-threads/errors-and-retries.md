# Thread — Errors, HTTP failures, and retries

1. [Python errors](../01-python/12-errors.md) — exceptions and tracebacks.
2. [Testing and debugging](../01-python/05-testing-and-debugging.md) — repro mindset.
3. [Git reset & recovery](../03-git/08-reset.md) — when you “broke the repo.”
4. [HTTP client errors](../10-http-clients/04-errors.md) — status codes, parsing failures.
5. [HTTPS & trust](../10-http-clients/09-https.md) — TLS failures are errors too.
6. [Runtime validation](../10-http-clients/10-runtime-validation.md) — schema mismatch at the boundary.
7. [SQL constraints](../11-sql/03-constraints.md) — integrity errors as API design feedback.
8. [Server error handling](../12-http-servers/05-error-handling.md) — mapping failures to responses.
9. [Webhooks](../12-http-servers/09-webhooks.md) — delivery failures and retries.
10. [Pub/Sub delivery](../15-pubsub/05-delivery.md) — acks, nacks, DLQ.

**Capstone question:** *When is a retry **unsafe** without an idempotency key? Name two money-adjacent examples.*
