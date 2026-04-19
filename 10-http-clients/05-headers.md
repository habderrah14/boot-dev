# Chapter 05 — Headers

> "Headers are metadata. They tell the server who's asking, what the client accepts, and carry auth, caching, and tracing info — all before a single byte of body is read."

## Learning objectives

By the end of this chapter you will be able to:

- Set and read headers in `fetch` using both object literals and the `Headers` class.
- List the most important request and response headers and explain when to use each.
- Handle case-insensitive header names correctly.
- Use authentication headers (Bearer, Basic, API key) safely.
- Implement conditional requests with `ETag` and `If-None-Match`.

## Prerequisites & recap

- [Why HTTP](01-why-http.md) — you know a request has headers, a body, and a method.

## The simple version

Headers are key-value pairs attached to every request and response. They carry metadata — *about* the message, not the message itself. Think of them like the label on a package: the label says who it's from, who it's for, what's inside, and how to handle it, while the actual contents are in the box (the body).

On the request side, you use headers to tell the server who you are (`User-Agent`), what format you want back (`Accept`), and to prove your identity (`Authorization`). On the response side, the server uses headers to tell you what it's sending (`Content-Type`), how long to cache it (`Cache-Control`), and where to find a newly created resource (`Location`).

## In plain terms (newbie lane)

This chapter is really about **Headers**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  REQUEST
  ┌────────────────────────────────────────────────────┐
  │ GET /v1/users HTTP/1.1                             │
  │                                                    │
  │ Accept: application/json        ◄─ what I want     │
  │ Authorization: Bearer eyJ...    ◄─ who I am        │
  │ User-Agent: myapp/1.0          ◄─ what I am        │
  │ X-Request-Id: 550e8400-...     ◄─ tracing          │
  │ If-None-Match: "abc123"        ◄─ cache check      │
  └────────────────────────────────────────────────────┘

  RESPONSE
  ┌────────────────────────────────────────────────────┐
  │ HTTP/1.1 200 OK                                    │
  │                                                    │
  │ Content-Type: application/json  ◄─ what's inside   │
  │ ETag: "def456"                  ◄─ version tag      │
  │ Cache-Control: max-age=300      ◄─ cache policy    │
  │ X-Request-Id: 550e8400-...     ◄─ echo for tracing │
  │                                                    │
  │ {"users": [...]}                ◄─ body             │
  └────────────────────────────────────────────────────┘
```

*Headers frame the conversation. The body is the content; headers are the context.*

## Concept deep-dive

### Setting headers in `fetch`

You can pass headers as a plain object:

```ts
const r = await fetch(url, {
  headers: {
    "Accept": "application/json",
    "Authorization": `Bearer ${token}`,
    "X-Request-Id": crypto.randomUUID(),
  },
});
```

Or use the `Headers` class for programmatic manipulation:

```ts
const h = new Headers();
h.set("Accept", "application/json");
h.append("X-Tag", "a");
h.append("X-Tag", "b");   // multi-value: "a, b"
```

Why does the `Headers` class exist? Because headers have special rules — they're case-insensitive, some can have multiple values, and you often need to merge sets of headers from different sources (base headers + per-request headers). The class handles all of this.

### Header names are case-insensitive

This is part of the HTTP specification. `Content-Type`, `content-type`, and `CONTENT-TYPE` are all the same header. The `Headers` class normalizes to lowercase internally. This matters when you're reading documentation that uses one casing but your code uses another — they'll still match.

### Reading response headers

```ts
r.headers.get("content-type");     // "application/json"
r.headers.has("etag");             // true or false
for (const [key, value] of r.headers) {
  console.log(`${key}: ${value}`);
}
```

### Common request headers

| Header | Purpose | Example |
|--------|---------|---------|
| `Accept` | What response format you want | `application/json` |
| `Content-Type` | Format of the body you're sending | `application/json` |
| `Authorization` | Your identity/credentials | `Bearer eyJ...` or `Basic dXNlcjpwYXNz` |
| `User-Agent` | Identifies your client | `myapp/1.0` |
| `Accept-Encoding` | Compressed responses you can handle | `gzip, deflate, br` |
| `If-None-Match` | Conditional GET — send data only if changed | ETag value from a previous response |
| `X-Request-Id` | Distributed tracing ID | A UUID |

### Common response headers

| Header | Purpose | Example |
|--------|---------|---------|
| `Content-Type` | Format of the response body | `application/json; charset=utf-8` |
| `Content-Length` | Body size in bytes | `1234` |
| `ETag` | Version fingerprint of the resource | `"abc123"` |
| `Last-Modified` | When the resource last changed | `Wed, 16 Apr 2026 10:00:00 GMT` |
| `Cache-Control` | Caching policy | `max-age=300, public` |
| `Location` | Where to find a new or moved resource | `/v1/users/42` |
| `Set-Cookie` | Starts a cookie | `session=abc; HttpOnly; Secure` |
| `Retry-After` | How long to wait before retrying | `60` (seconds) |

### Authentication headers

**Bearer tokens** — the most common pattern for APIs:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

The token is opaque to the transport layer. It might be a JWT, an API key, or a session token.

**Basic auth** — username:password, base64-encoded:

```
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

This is trivially decodable — it's base64, not encryption. Only use Basic auth over HTTPS.

**API keys** — usually a custom header or query parameter:

```
X-API-Key: sk_live_abc123
```

Why so many patterns? Because different APIs were designed at different times with different security models. Bearer tokens are the modern standard; Basic auth is legacy but still used for simplicity; API keys are common for service-to-service calls.

**Never hard-code secrets.** Read them from `process.env` and never log them.

### Content negotiation

The client tells the server what formats it prefers:

```
Accept: application/json, text/html;q=0.8
```

The quality factor `q` (0.0–1.0) ranks preferences. The server picks the best match. If no `Accept` header is sent, many APIs default to HTML or XML — which is why your `fetch` call might return HTML when you expected JSON.

### Conditional requests (caching)

ETags let you avoid re-downloading unchanged data:

1. First request: server responds with `ETag: "abc123"`.
2. Subsequent request: client sends `If-None-Match: "abc123"`.
3. If the resource hasn't changed, server responds `304 Not Modified` with no body.
4. If it has changed, server responds `200` with the new data and a new ETag.

This saves bandwidth and reduces server load. In high-traffic APIs, conditional requests can cut data transfer dramatically.

### Distributed tracing (W3C)

`Traceparent` and `Tracestate` headers carry trace context across services. OpenTelemetry generates and propagates them. When you send an `X-Request-Id` on a request, it ties all downstream service calls to a single trace, making debugging across microservices possible.

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Case-insensitive names | Prevents bugs from casing mismatches across implementations | Case-sensitive (like in some protocols) | You wouldn't — case sensitivity causes needless bugs |
| Bearer over Basic | Tokens can be scoped, rotated, and revoked without changing passwords | Session cookies | When you're building a browser-first app where cookies are simpler |
| ETags for caching | Content-addressed — works even when the modification timestamp is unreliable | `Last-Modified` + `If-Modified-Since` | When you have reliable timestamps and don't want to compute hashes |
| `X-Request-Id` for tracing | Correlates logs across services without coupling them | Logging correlation only within a single service | You'd almost always want cross-service tracing in production |

## Production-quality code

```ts
interface ClientConfig {
  baseUrl: string;
  token: string;
  userAgent?: string;
}

function createApiClient(config: ClientConfig) {
  const { baseUrl, token, userAgent = "backend-companion/1.0" } = config;

  function baseHeaders(extraHeaders?: Record<string, string>): Headers {
    const h = new Headers({
      "Authorization": `Bearer ${token}`,
      "Accept": "application/json",
      "User-Agent": userAgent,
      "X-Request-Id": crypto.randomUUID(),
    });
    if (extraHeaders) {
      for (const [k, v] of Object.entries(extraHeaders)) {
        h.set(k, v);
      }
    }
    return h;
  }

  return {
    async get<T>(path: string, headers?: Record<string, string>): Promise<T> {
      const url = new URL(path, baseUrl);
      const r = await fetch(url, { headers: baseHeaders(headers) });
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
      return (await r.json()) as T;
    },

    async post<T>(path: string, body: unknown, headers?: Record<string, string>): Promise<T> {
      const url = new URL(path, baseUrl);
      const h = baseHeaders({ "Content-Type": "application/json", ...headers });
      const r = await fetch(url, {
        method: "POST",
        headers: h,
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
      return (await r.json()) as T;
    },
  };
}

// Conditional GET with ETag caching
async function fetchWithEtag<T>(
  url: string,
  cachedEtag: string | null,
  cachedData: T | null,
): Promise<{ data: T; etag: string }> {
  const headers: Record<string, string> = {};
  if (cachedEtag) headers["If-None-Match"] = cachedEtag;

  const r = await fetch(url, { headers });

  if (r.status === 304 && cachedData !== null && cachedEtag !== null) {
    return { data: cachedData, etag: cachedEtag };
  }

  if (!r.ok) throw new Error(`HTTP ${r.status}`);

  const data = (await r.json()) as T;
  const etag = r.headers.get("etag") ?? "";
  return { data, etag };
}
```

## Security notes

- **Never log full `Authorization` headers.** Redact or mask them in logs. A leaked Bearer token is a full credential.
- **Basic auth is plaintext** — base64 is encoding, not encryption. Only use it over HTTPS, and prefer Bearer tokens.
- **`Set-Cookie` without `HttpOnly` and `Secure` flags** makes cookies accessible to JavaScript and transmittable over plain HTTP. Always set both in production.
- **Sensitive headers survive redirects.** If a 3xx redirect sends you to a different origin, `fetch` strips `Authorization` by default — but custom `X-API-Key` headers might not be stripped. Be aware of cross-origin redirect behavior.

## Performance notes

- **Header size matters at scale.** Each request carries all headers. JWTs can be large (1KB+). HTTP/2's HPACK compression helps, but keeping tokens small reduces overhead.
- **Conditional requests save bandwidth.** A `304 Not Modified` response has no body. For frequently polled resources, ETags can reduce data transfer by 90%+.
- **`Accept-Encoding: gzip`** compresses response bodies, often reducing size by 60–80%. Node's `fetch` (undici) handles this by default in recent versions.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "API returns HTML instead of JSON" | Missing `Accept: application/json` header; API defaults to HTML | Always set `Accept: application/json` explicitly |
| 2 | "Token appears in production logs" | Logging full request headers including `Authorization` | Redact sensitive headers before logging |
| 3 | "Setting `Content-Type` on a GET request" | Copy-pasted from a POST example; GET has no body, so `Content-Type` is meaningless | Only set `Content-Type` when sending a body |
| 4 | "Header name comparison fails" | Comparing `"Content-Type" === r.headers.get("content-type")` — name casing differs | Header names are case-insensitive; use `Headers.get()` which normalizes |

## Practice

### Warm-up

Fetch `https://httpbin.org/headers` with a custom `User-Agent` header. Print the response to see what the server received.

<details><summary>Show solution</summary>

```ts
const r = await fetch("https://httpbin.org/headers", {
  headers: { "User-Agent": "my-custom-agent/1.0" },
});
console.log(await r.json());
// { "headers": { "User-Agent": "my-custom-agent/1.0", ... } }
```

</details>

### Standard

Implement a conditional GET with ETag. First fetch a resource and store its ETag. Then fetch again with `If-None-Match` and handle the 304.

<details><summary>Show solution</summary>

```ts
const firstResponse = await fetch("https://httpbin.org/etag/abc123");
const etag = firstResponse.headers.get("etag");
console.log("ETag:", etag);

const secondResponse = await fetch("https://httpbin.org/etag/abc123", {
  headers: etag ? { "If-None-Match": etag } : {},
});
console.log("Status:", secondResponse.status);  // 304
```

</details>

### Bug hunt

A developer writes `fetch(url, { headers: "Authorization: Bearer abc" })`. TypeScript compiles fine but the request fails. Why?

<details><summary>Show solution</summary>

The `headers` option expects a `HeadersInit` — an object, an array of tuples, or a `Headers` instance. A plain string is not valid `HeadersInit`. It might pass type-checking loosely but won't produce the intended header. Fix: `{ headers: { "Authorization": "Bearer abc" } }`.

</details>

### Stretch

Build a `RedactedHeaders` utility function that takes a `Headers` object and returns a plain object with sensitive headers (like `Authorization`, `Cookie`, `X-API-Key`) masked as `"[REDACTED]"`.

<details><summary>Show solution</summary>

```ts
const SENSITIVE_HEADERS = new Set([
  "authorization", "cookie", "set-cookie", "x-api-key",
]);

function redactHeaders(headers: Headers): Record<string, string> {
  const result: Record<string, string> = {};
  for (const [key, value] of headers) {
    result[key] = SENSITIVE_HEADERS.has(key.toLowerCase())
      ? "[REDACTED]"
      : value;
  }
  return result;
}

const h = new Headers({
  "Authorization": "Bearer secret-token",
  "Content-Type": "application/json",
  "X-API-Key": "sk_live_abc",
});
console.log(redactHeaders(h));
// { authorization: "[REDACTED]", "content-type": "application/json", "x-api-key": "[REDACTED]" }
```

</details>

### Stretch++

Add `Accept-Encoding: gzip` to a request and verify the response is compressed by inspecting the `Content-Encoding` response header. Decompress if needed.

<details><summary>Show solution</summary>

```ts
const r = await fetch("https://httpbin.org/gzip", {
  headers: { "Accept-Encoding": "gzip" },
});

console.log("Content-Encoding:", r.headers.get("content-encoding"));
const data = await r.json();
console.log("Compressed response received:", data.gzipped);
```

Note: Node's built-in `fetch` (undici) handles decompression transparently in recent versions, so `r.json()` works regardless. In older environments you'd need to pipe the response through `zlib.createGunzip()`.

</details>

## Quiz

1. HTTP header names are:
   (a) Case-sensitive  (b) Case-insensitive  (c) Uppercase only  (d) Lowercase only

2. An API key is typically sent via:
   (a) The request body  (b) `Authorization` header or a custom header like `X-API-Key`  (c) The path  (d) The fragment

3. `Retry-After` is:
   (a) A response header suggesting how long to wait  (b) A request header  (c) Obsolete  (d) Browser-only

4. `If-None-Match` is:
   (a) A request header for ETag-based conditional requests  (b) Response-only  (c) A cookie  (d) Deprecated

5. The `Accept` header specifies:
   (a) What the server must return  (b) Content types the client prefers  (c) Authentication  (d) Encoding

**Short answer:**

6. Why should Basic auth only be used over HTTPS?
7. Why standardize on a single `User-Agent` string per client application?

*Answers: 1-b, 2-b, 3-a, 4-a, 5-b. 6 — Basic auth is base64-encoded, not encrypted. Over plain HTTP, anyone on the network path can decode the credentials trivially. HTTPS encrypts the entire request including headers. 7 — A consistent `User-Agent` lets API providers identify your client in their logs, apply rate limits per-client, and contact you if your client misbehaves.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-headers — mini-project](mini-projects/05-headers-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Headers are case-insensitive key-value pairs that carry metadata about requests and responses.
- Use the `Headers` class for safe, composable header management.
- Authentication (Bearer, Basic, API key) and tracing (`X-Request-Id`, `Traceparent`) live in headers.
- Conditional requests with ETags save bandwidth — the server returns 304 with no body when the resource hasn't changed.

## Further reading

- MDN, *HTTP headers* — comprehensive reference for every standard header.
- W3C Trace Context specification — how `Traceparent` and `Tracestate` work.
- Next: [JSON](06-json.md).
