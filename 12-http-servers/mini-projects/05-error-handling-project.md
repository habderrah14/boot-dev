# Mini-project — 05-error-handling

_Companion chapter:_ [`05-error-handling.md`](../05-error-handling.md)

**Goal.** Build a consistent error-handling layer for your server.

**Acceptance criteria:**

- Error class hierarchy: `HttpError`, `NotFound`, `BadRequest`, `Unauthorized`, `Forbidden`, `Conflict`.
- Central error middleware handles `ZodError`, `HttpError`, and unknown errors.
- Request-ID middleware: reads `X-Request-Id` or generates UUID; echoes in response.
- Structured logging via `pino` with request ID in every log line.
- `asyncHandler` wrapper on all async routes.
- Process-level handlers for `unhandledRejection` and `uncaughtException`.
- Tests assert: 400 on bad input, 404 on missing resource, 500 on unknown error (with no stack trace in response body).

**Hints:**

- Define error classes in a shared `errors.ts` file.
- Test the error middleware by throwing each error type from a test route.
- Use `supertest` and assert that the 500 response body does *not* contain the word "stack" or a file path.

**Stretch:** Add request duration logging (how long each request took) and a `Retry-After` header on 429 responses.
