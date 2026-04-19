# Mini-project — 07-methods

_Companion chapter:_ [`07-methods.md`](../07-methods.md)

**Goal.** Build a tiny HTTP client library with typed helpers `get`, `post`, `put`, `patch`, and `del`.

**Acceptance criteria:**

- Each method sets appropriate headers and returns typed JSON.
- `post` accepts an optional `idempotencyKey` parameter and sends it as an `Idempotency-Key` header.
- `del` treats 404 as success (the resource is already gone — idempotent intent).
- All methods throw `HttpError` with status and body on failure.
- Each method accepts an optional `AbortSignal` for cancellation.

**Hints:**

- Extract common logic into a `handleResponse<T>` function.
- Use a `jsonHeaders()` helper that sets `Content-Type` and `Accept`.
- `del` returns `void`, not parsed JSON.

**Stretch:** Add a `head(url)` method that returns just the headers as a `Record<string, string>`.
