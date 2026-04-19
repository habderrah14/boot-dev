# Concept thread — Testing strategy (unit → integration → contract → e2e)

Use this thread when you know testing matters, but you’re unsure **which layer** should own a given check.

## The goal

Build confidence with the cheapest reliable signal first:

1. **Unit tests** for local logic and edge cases
2. **Integration tests** for boundaries (DB, filesystem, broker)
3. **Contract tests** for request/response schema compatibility
4. **End-to-end tests** for one or two golden user flows

If every bug is only caught in e2e, your suite is too slow and too expensive.

## Quick decision table

| If you need to verify…                       | Best layer  | Why                                        |
| -------------------------------------------- | ----------- | ------------------------------------------ |
| Pure function behavior, branching, edge math | Unit        | Fastest feedback, no external setup        |
| Handler + real DB migration/query behavior   | Integration | Catches schema/query/repository mismatches |
| API request/response shape compatibility     | Contract    | Protects producers/consumers from drift    |
| Login→business action→side effect happy path | E2E         | Verifies wiring of the whole system        |

## Read in this order

### 1) Fundamentals: Python testing and debugging

- [01-python/05-testing-and-debugging.md](../01-python/05-testing-and-debugging.md)
- Focus: assertions, fixtures, failure messages, red→green loop.

### 2) Type and boundary confidence

- [09-ts/README.md](../09-ts/README.md)
- [10-http-clients/10-runtime-validation.md](../10-http-clients/10-runtime-validation.md)
- Focus: compile-time vs runtime guarantees, payload validation.

### 3) Persistence and integration reality

- [11-sql/README.md](../11-sql/README.md)
- [12-http-servers/06-storage.md](../12-http-servers/06-storage.md)
- Focus: tests with real schema/storage paths, transaction behavior.

### 4) Error paths and reliability

- [12-http-servers/05-error-handling.md](../12-http-servers/05-error-handling.md)
- [15-pubsub/05-delivery.md](../15-pubsub/05-delivery.md)
- Focus: retries, idempotency, dead-letter handling.

### 5) Shipping and verification

- [appendix-junior-backend.md](../appendix-junior-backend.md)
- [appendix-shipping-checklist.md](../appendix-shipping-checklist.md)
- Focus: test strategy as part of release readiness.

## Suggested default ratio

Start here, then adapt per project:

- **Unit:** 70–85%
- **Integration:** 10–25%
- **Contract:** 5–10%
- **E2E:** 1–5%

This isn’t dogma; it’s a speed-vs-confidence heuristic.

## Common failure modes

1. **Too many e2e tests**
   - Symptom: CI takes forever; failures are flaky and hard to diagnose.
   - Fix: move business-rule checks down to unit/integration.

2. **Only unit tests, no integration**
   - Symptom: green tests, broken migrations/queries in staging.
   - Fix: add integration tests around real schema and query paths.

3. **No contract validation**
   - Symptom: frontend/backend disagree on JSON shape silently.
   - Fix: validate payloads at runtime and pin schemas in tests.

4. **No error-path tests**
   - Symptom: retries flood dependencies; duplicate side effects.
   - Fix: add tests for timeout, retry budget, idempotency keys.

## Mini-checklist for any backend feature

- [ ] Unit tests for branch logic and edge cases
- [ ] Integration test for storage or external boundary
- [ ] Contract test for input/output schema
- [ ] One golden-path e2e (max a few)
- [ ] At least one failure-path test (timeout, 4xx/5xx, duplicate delivery)

## Where this idea reappears

- [errors-and-retries.md](errors-and-retries.md)
- [performance.md](performance.md)
- [state.md](state.md)
