# Mini-project — 05-headers

_Companion chapter:_ [`05-headers.md`](../05-headers.md)

**Goal.** Build `apiClient.ts` — a reusable API client that automatically injects `Authorization`, `Accept`, `User-Agent`, and `X-Request-Id` headers on every request.

**Acceptance criteria:**

- Constructor takes `{ baseUrl, token, userAgent? }`.
- Every request automatically includes `Authorization: Bearer <token>`, `Accept: application/json`, `User-Agent`, and a unique `X-Request-Id`.
- Exposes `get(path)` and `post(path, body)` methods.
- Per-request headers can override defaults.
- Sensitive headers are redacted in any logged output.

**Hints:**

- Use `crypto.randomUUID()` for request IDs.
- The `Headers` class constructor accepts a plain object.
- Merge base headers with per-request headers using object spread or `Headers.set()`.

**Stretch:** Add ETag-based conditional GET caching — store ETags per URL and automatically send `If-None-Match` on subsequent requests. Return cached data on 304.
