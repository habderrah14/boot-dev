# Mini-project — 04-json

_Companion chapter:_ [`04-json.md`](../04-json.md)

**Goal.** Add Zod validation and uniform response/error envelopes to every endpoint in your server.

**Acceptance criteria:**

- Every `POST` and `PATCH` endpoint validates the request body with Zod.
- Successful responses use `{ data: ... }` (single items) or `{ data: [...], meta: { ... } }` (lists).
- Validation errors return `{ error: "validation_failed", details: [...] }` with status 400.
- Domain errors return `{ error: "<code>", message: "<description>" }` with the appropriate status.
- Unknown errors return `{ error: "server_error" }` with status 500.
- Tests assert the response shape (not just the status code).
- Body size is capped at 1 MB.

**Hints:**

- Start with the error middleware. Test it by deliberately sending invalid bodies.
- Use Zod's `.partial()` for PATCH schemas.
- Use `supertest` to assert on the full response body shape in tests.

**Stretch:** Add an `/export` endpoint that streams all items as NDJSON. Write a test that reads the stream and verifies each line is valid JSON.
