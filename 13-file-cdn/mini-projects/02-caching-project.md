# Mini-project — 02-caching

_Companion chapter:_ [`02-caching.md`](../02-caching.md)

**Goal.** Add full HTTP caching to a read-heavy API: ETag-based conditional requests, `Cache-Control` headers, and Redis memoization for the expensive endpoint. Verify 304 responses with `curl`.

**Acceptance criteria:**

- `GET /api/products/:id` returns an `ETag` and `Cache-Control: public, max-age=60`.
- Conditional requests with `If-None-Match` return `304 Not Modified` when unchanged.
- A slow endpoint (`GET /api/dashboard/:userId`) is memoized in Redis with a 60-second TTL.
- The dashboard endpoint works (slower) when Redis is down.
- Static assets are served with `Cache-Control: public, max-age=31536000, immutable`.

**Hints:**

- Use `crypto.createHash("md5")` on the response body for a content-based ETag.
- Wrap Redis calls in try/catch to degrade gracefully.
- Test with `curl -i -H 'If-None-Match: "<etag>"'`.

**Stretch:** Add `stale-while-revalidate=300` to the product endpoint and implement a cache-stampede lock in Redis.
