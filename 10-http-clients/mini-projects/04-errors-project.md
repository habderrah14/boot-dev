# Mini-project — 04-errors

_Companion chapter:_ [`04-errors.md`](../04-errors.md)

**Goal.** Build `http-client.ts` exporting a `request<T>(method, url, options?)` function with typed errors, timeouts, and smart retries.

**Acceptance criteria:**

- Throws `HttpError` (with `status` and `body`) on non-2xx responses.
- Supports configurable timeout via `AbortSignal.timeout`.
- Retries idempotent methods (GET, PUT, DELETE) on transient failures (network errors, 502/503/504) with jittered exponential backoff.
- Never retries POST unless an `idempotencyKey` option is provided.
- Honors `Retry-After` header on 429 responses.
- Defaults: timeout 10s, max 3 retries, base delay 200ms.

**Hints:**

- Use a `Set` for retryable status codes and idempotent methods.
- Parse `Retry-After` as seconds (integer) and convert to ms.
- The retry loop should be a `for` loop with `attempt <= maxRetries`.

**Stretch:** Add a `signal` option so the caller can provide their own `AbortSignal` that composes with the timeout signal (use `AbortSignal.any([...])` in Node 20+).
