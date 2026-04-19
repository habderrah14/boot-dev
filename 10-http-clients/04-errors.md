# Chapter 04 — Errors

> "HTTP has two kinds of errors: network errors your library raises, and status codes the server returned. Handle both or your app will silently eat failures."

## Learning objectives

By the end of this chapter you will be able to:

- List the HTTP status classes (1xx–5xx) and the most important individual codes.
- Distinguish a `fetch` rejection from a non-2xx response — and explain why this distinction trips up everyone.
- Implement timeouts and aborts with `AbortController`.
- Retry safely with exponential backoff and jitter, and explain when retrying is dangerous.

## Prerequisites & recap

- [Why HTTP](01-why-http.md) — you understand request/response and statelessness.
- [Errors in JavaScript](../08-js/09-errors.md) — you know try/catch and error propagation.

## The simple version

When an HTTP request fails, there are exactly two places the failure can happen. First, the request might never reach the server — DNS fails, the connection is refused, the network is down, or you aborted it. In this case, `fetch` throws an exception. Second, the request reaches the server, but the server says "no" — it returns a 4xx or 5xx status code. In this case, `fetch` does _not_ throw. It happily gives you a `Response` object with a `.status` of 404 or 500. If you don't check, your code will try to use the error response as if it were valid data.

This is the single most common mistake with `fetch`: assuming it throws on HTTP errors. It doesn't. You must check `response.ok` yourself.

## In plain terms (newbie lane)

This chapter is really about **Errors**. Skim _Learning objectives_ above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.
> **Actually:** you only need the _next_ honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>

## Visual flow

```
  ┌────────┐          ┌─────────┐          ┌────────┐
  │ Your   │──fetch──▶│ Network │──────── ▶│ Server │
  │  Code  │          │         │          │        │
  └────┬───┘          └────┬────┘          └───┬────┘
       │                   │                   │
       │    CASE 1: network fails              │
       │◀── exception ────┤                    │
       │   (DNS, refused, │                    │
       │    abort, timeout)│                   │
       │                   │                   │
       │    CASE 2: server responds            │
       │◀──────────────────┼─── Response ─────┤
       │   (status 200,    │   (2xx, 4xx,     │
       │    404, 500, etc) │    5xx — all      │
       │   NO exception!   │    resolve)       │
       │                   │                   │
```

_`fetch` only rejects on network-level failures. HTTP error statuses (4xx, 5xx) are normal resolutions — you must check them yourself._

## Concept deep-dive

### Status classes

| Range | Meaning                              | Your action                           |
| ----- | ------------------------------------ | ------------------------------------- |
| 1xx   | Informational (rare for APIs)        | Usually handled by the runtime        |
| 2xx   | Success                              | Process the response                  |
| 3xx   | Redirection                          | `fetch` follows redirects by default  |
| 4xx   | Client error — your request is wrong | Fix your request; don't retry blindly |
| 5xx   | Server error — the server is wrong   | May be worth retrying (with care)     |

### The codes you'll see most

- **200 OK** — generic success.
- **201 Created** — resource created; look for a `Location` header pointing to it.
- **204 No Content** — success with no body (common for DELETE).
- **301/308** — permanent redirect. 308 preserves the method; 301 may change POST to GET.
- **302/307** — temporary redirect. Same distinction as above.
- **400 Bad Request** — your payload is malformed.
- **401 Unauthorized** — you need to authenticate (confusing name — it really means "unauthenticated").
- **403 Forbidden** — you're authenticated but not allowed.
- **404 Not Found** — the resource doesn't exist.
- **409 Conflict** — state mismatch (duplicate entry, version conflict).
- **422 Unprocessable Entity** — the payload is syntactically valid but semantically wrong (validation failed).
- **429 Too Many Requests** — you're rate-limited. Honor the `Retry-After` header.
- **500 Internal Server Error** — generic server failure.
- **502 Bad Gateway** — the server's upstream is broken.
- **503 Service Unavailable** — the server is overloaded or in maintenance.
- **504 Gateway Timeout** — the server's upstream is too slow.

### When does `fetch` reject?

`fetch` resolves with a `Response` for _any_ HTTP status — including 404 and 500. It only rejects when:

- **Network failure** — DNS resolution fails, connection refused, network unreachable.
- **CORS** (browser only) — the server's CORS policy blocks the request.
- **Abort** — you called `controller.abort()` or the signal timed out.
- **Malformed response** — the server sent something that isn't valid HTTP.

This means you must **always check `response.ok`**:

```ts
const r = await fetch(url);
if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
```

Why did they design it this way? Because a 404 is a valid, successful HTTP transaction — the server processed your request and told you the resource doesn't exist. From the network's perspective, nothing went wrong.

### Most common `fetch` bug (wrong vs right)

**Wrong (assumes catch handles 4xx/5xx):**

```ts
try {
  const user = await fetch("https://api.example.com/users/123").then((r) =>
    r.json(),
  );
  console.log(user.name);
} catch (err) {
  // This will NOT run for HTTP 404/500
  console.error("Request failed", err);
}
```

If the server returns `404` with an error JSON body, this code still calls `r.json()` and then behaves as if it got a valid user object.

**Right (explicit status gate):**

```ts
const response = await fetch("https://api.example.com/users/123");
if (!response.ok) {
  const body = await response.text();
  throw new Error(`HTTP ${response.status}: ${body}`);
}
const user = await response.json();
console.log(user.name);
```

This tiny `if (!response.ok)` check prevents a huge class of silent production bugs.

### Timeouts

Native `fetch` has no built-in timeout parameter. You have two options:

**Option 1 — `AbortSignal.timeout()` (Node 18+, modern browsers):**

```ts
const r = await fetch(url, { signal: AbortSignal.timeout(5_000) });
```

**Option 2 — Manual `AbortController`:**

```ts
const ctrl = new AbortController();
const timer = setTimeout(() => ctrl.abort(), 5_000);
try {
  const r = await fetch(url, { signal: ctrl.signal });
  // ... use response
} finally {
  clearTimeout(timer);
}
```

Why no built-in timeout? Because timeout semantics are surprisingly complex — should it cover just the connection, or also the body download? Different use cases need different answers. `AbortController` gives you full control.

### Retries: when and how

Retry on **idempotent** methods (GET, PUT, DELETE) for **transient** failures:

- Network errors (DNS, connection reset).
- 502, 503, 504 (upstream problems).
- 408 Request Timeout.
- 429 Too Many Requests (after honoring `Retry-After`).

**Never retry a non-idempotent POST without an idempotency key.** A second POST might create a duplicate charge, a duplicate order, or a duplicate user. If you must retry POST, attach a unique `Idempotency-Key` header so the server can deduplicate.

**Exponential backoff with jitter** prevents retry storms (where thousands of clients retry simultaneously and overwhelm the server):

```
wait = baseMs * 2^attempt + random(0, jitterMs)
```

### Structured error handling

Don't just throw generic `Error`. Build a small error hierarchy so callers can distinguish HTTP errors from network errors from timeouts:

```ts
class HttpError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: string,
  ) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
  }
}
```

This lets callers pattern-match: "If it's a 401, redirect to login. If it's a 429, wait and retry. If it's a network error, show an offline banner."

## Why these design choices

| Decision                         | Why                                                                                             | Alternative                                                          | When you'd pick differently                                                    |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `fetch` doesn't throw on 4xx/5xx | HTTP errors are valid responses; throwing would conflate protocol success with business failure | Axios throws on non-2xx by default                                   | When you want the convenience of a single catch block (use Axios or a wrapper) |
| No built-in timeout              | Timeout scope is ambiguous (connect vs. full response)                                          | Libraries like `got` have `timeout.request`, `timeout.connect`, etc. | When you need fine-grained timeout control                                     |
| Exponential backoff              | Prevents retry storms; gives the server time to recover                                         | Fixed interval                                                       | Never — fixed intervals cause synchronized retries (thundering herd)           |
| Jitter in backoff                | Desynchronizes retries across clients                                                           | No jitter                                                            | Never in production — jitter is always beneficial                              |

## Production-quality code

```ts
class HttpError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: string,
  ) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
  }
}

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: string;
  timeoutMs?: number;
  retries?: number;
  retryBaseMs?: number;
}

const RETRYABLE_STATUSES = new Set([408, 429, 502, 503, 504]);
const IDEMPOTENT_METHODS = new Set(["GET", "HEAD", "PUT", "DELETE", "OPTIONS"]);

function isRetryable(method: string, status: number): boolean {
  return (
    IDEMPOTENT_METHODS.has(method.toUpperCase()) &&
    RETRYABLE_STATUSES.has(status)
  );
}

async function request<T>(url: string, opts: RequestOptions = {}): Promise<T> {
  const {
    method = "GET",
    headers,
    body,
    timeoutMs = 10_000,
    retries = 3,
    retryBaseMs = 200,
  } = opts;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {
        method,
        headers,
        body,
        signal: AbortSignal.timeout(timeoutMs),
      });

      if (response.ok) {
        return (await response.json()) as T;
      }

      const responseBody = await response.text();

      if (attempt < retries && isRetryable(method, response.status)) {
        const retryAfter = response.headers.get("Retry-After");
        const retryAfterSeconds = retryAfter
          ? Number.parseInt(retryAfter, 10)
          : NaN;
        const waitMs = Number.isFinite(retryAfterSeconds)
          ? retryAfterSeconds * 1_000
          : retryBaseMs * 2 ** attempt + Math.random() * 100;
        await new Promise((resolve) => setTimeout(resolve, waitMs));
        continue;
      }

      throw new HttpError(response.status, responseBody);
    } catch (err) {
      if (err instanceof HttpError) throw err;

      lastError = err as Error;

      if (attempt < retries && IDEMPOTENT_METHODS.has(method.toUpperCase())) {
        const waitMs = retryBaseMs * 2 ** attempt + Math.random() * 100;
        await new Promise((resolve) => setTimeout(resolve, waitMs));
        continue;
      }

      throw lastError;
    }
  }

  throw lastError ?? new Error("Unreachable");
}
```

## Security notes

- **Don't leak error bodies to end users.** A 500 response from an upstream API might contain stack traces, database queries, or internal hostnames. Log the full body server-side; return a generic message to the client.
- **Don't retry with credentials to untrusted servers.** Each retry resends your `Authorization` header. If a redirect sends you to a different origin, `fetch` strips the header by default — but your retry logic might not.
- **Rate-limit your retries.** Unlimited retries with short backoff can look like a DDoS attack to the upstream server, getting your IP blocked.

## Performance notes

- **Timeout budget** — set your timeout to less than your own server's response deadline. If your API promises a 30s response, set your outgoing fetch timeout to 25s so you have time to return a graceful error.
- **Connection reuse** — `fetch` in Node (via `undici`) pools connections. Retries to the same host reuse the pool, so the TCP+TLS handshake cost is paid only once.
- **Don't retry too aggressively.** Three retries with exponential backoff (200ms, 400ms, 800ms) add ~1.4s worst-case. More than five retries rarely helps and just delays your response.

## Common mistakes

| #   | Symptom                                                              | Cause                                                                               | Fix                                                                    |
| --- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1   | "My catch block never fires on 404"                                  | `fetch` resolves on all HTTP statuses; it only rejects on network/abort errors      | Check `response.ok` or `response.status` before using the body         |
| 2   | "Retrying POST caused duplicate charges"                             | POST is not idempotent; retrying creates a new resource each time                   | Use an `Idempotency-Key` header, or don't retry non-idempotent methods |
| 3   | "All my clients retry at exactly the same time and crash the server" | Fixed retry interval without jitter causes synchronized retries                     | Add random jitter: `baseMs * 2^attempt + random(0, jitterMs)`          |
| 4   | "I lost the error body — I don't know what the server said"          | Code throws `new Error("request failed")` without capturing `await response.text()` | Always read and attach the response body to your error for debugging   |

## Practice

### Warm-up

Fetch `https://httpbin.org/status/404`. Confirm that `fetch` doesn't throw. Print the status code.

<details><summary>Show solution</summary>

```ts
const r = await fetch("https://httpbin.org/status/404");
console.log("Status:", r.status); // 404
console.log("ok?", r.ok); // false
// No exception was thrown — fetch resolved normally.
```

</details>

### Standard

Build an `HttpError` class with `status` and `body` properties. Write a `getJson(url)` function that throws `HttpError` on non-2xx responses.

<details><summary>Show solution</summary>

```ts
class HttpError extends Error {
  constructor(
    public status: number,
    public body: string,
  ) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
  }
}

async function getJson<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new HttpError(r.status, await r.text());
  return (await r.json()) as T;
}

try {
  const data = await getJson("https://httpbin.org/status/500");
} catch (e) {
  if (e instanceof HttpError) {
    console.log(`Server returned ${e.status}: ${e.body}`);
  }
}
```

</details>

### Bug hunt

A developer writes a "retry everything" function that retries all failed requests, regardless of method or status code. Why is this dangerous?

<details><summary>Show solution</summary>

Retrying non-idempotent methods (like POST) can create duplicate resources — duplicate orders, duplicate charges, duplicate users. Retrying 400 (Bad Request) is pointless because the request will always fail with the same payload. Retrying 401/403 is wasteful because the credentials won't magically become valid. You should only retry idempotent methods on transient failures (network errors, 502/503/504, 429).

</details>

### Stretch

Add a 5-second timeout to a `fetch` call using `AbortController`. Catch the abort error and print a descriptive message.

<details><summary>Show solution</summary>

```ts
const ctrl = new AbortController();
const timer = setTimeout(() => ctrl.abort(), 5_000);

try {
  const r = await fetch("https://httpbin.org/delay/10", {
    signal: ctrl.signal,
  });
  console.log(r.status);
} catch (e) {
  if (e instanceof DOMException && e.name === "AbortError") {
    console.error("Request timed out after 5 seconds");
  } else {
    console.error("Network error:", (e as Error).message);
  }
} finally {
  clearTimeout(timer);
}
```

Or, more concisely with `AbortSignal.timeout`:

```ts
try {
  const r = await fetch("https://httpbin.org/delay/10", {
    signal: AbortSignal.timeout(5_000),
  });
} catch (e) {
  console.error("Timed out or network error:", (e as Error).message);
}
```

</details>

### Stretch++

Build a retry helper with jittered exponential backoff. It should accept a function, a max attempt count, and a base delay. Log each retry attempt with the wait time.

<details><summary>Show solution</summary>

```ts
async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  baseMs = 200,
): Promise<T> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (e) {
      if (attempt === maxAttempts - 1) throw e;
      const waitMs = baseMs * 2 ** attempt + Math.random() * 100;
      console.log(
        `Attempt ${attempt + 1} failed, retrying in ${waitMs.toFixed(0)}ms...`,
      );
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }
  throw new Error("Unreachable");
}

// Usage
const data = await withRetry(
  () =>
    fetch("https://httpbin.org/status/503").then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    }),
  4,
  300,
);
```

</details>

## Quiz

1. `fetch` rejects when:
   (a) Any non-2xx status (b) Only on network/abort/CORS failures (c) Never (d) Only on 500

2. Status 429 means:
   (a) Server is down (b) Rate limited — too many requests (c) Bad request (d) Forbidden

3. Retrying POST safely requires:
   (a) Always safe (b) An idempotency key to prevent duplicates (c) Just catching network errors (d) Always retrying on 5xx

4. Timeout in native `fetch` is achieved via:
   (a) `options.timeout` (b) `AbortController` or `AbortSignal.timeout` (c) No mechanism exists (d) `Promise.race` only

5. 401 vs. 403:
   (a) Identical meaning (b) 401 = authenticate (who are you?); 403 = forbidden (you can't do this) (c) Reversed (d) Both deprecated

**Short answer:**

6. Why should you check `response.ok` instead of relying on try/catch alone?
7. Give one reason for adding jitter to exponential backoff.

_Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — `fetch` resolves on all HTTP statuses including 4xx/5xx. Without checking `response.ok`, your code will treat error responses as valid data. 7 — Jitter desynchronizes retries across clients. Without it, all clients retry at the same intervals, creating a "thundering herd" that hammers the recovering server all at once._

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-errors — mini-project](mini-projects/04-errors-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.

## Chapter summary

- `fetch` only rejects on network/abort errors — HTTP error statuses (4xx, 5xx) are normal resolutions that you must check with `response.ok`.
- Use `AbortController` or `AbortSignal.timeout` for request timeouts.
- Retry only idempotent methods on transient failures, with exponential backoff and jitter.
- Build a typed error hierarchy (`HttpError`) so callers can distinguish and handle different failure modes.

## Further reading

- MDN, _Using the Fetch API_ — the definitive browser/Node reference.
- MDN, _AbortController_ — signal-based cancellation.
- Next: [Headers](05-headers.md).
