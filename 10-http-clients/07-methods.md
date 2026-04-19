# Chapter 07 — Methods

> "HTTP methods carry intent. Using the right one signals to clients, servers, caches, and humans what the request means — and whether it's safe to retry."

## Learning objectives

By the end of this chapter you will be able to:

- Pick the right HTTP method for each operation and explain why it matters.
- Define *safe* and *idempotent* and classify every common method.
- Use methods correctly in `fetch`, including body-carrying methods.
- Explain when POST is appropriate for non-create operations (RPC-style).
- Handle method overrides for legacy proxies.

## Prerequisites & recap

- [Why HTTP](01-why-http.md) — you know requests carry a method, path, headers, and optional body.

## The simple version

HTTP methods are verbs. They tell the server what you want to *do* to a resource. `GET` means "give me this resource." `POST` means "process this data" (usually create something). `PUT` means "replace this resource entirely." `PATCH` means "update part of it." `DELETE` means "remove it."

The reason methods matter goes beyond naming conventions. They carry *guarantees*. A `GET` is *safe* — the server promises it won't change anything. A `PUT` is *idempotent* — calling it ten times has the same effect as calling it once. These guarantees tell caches, proxies, and retry logic how to behave. If you use `POST` when you mean `PUT`, your retry logic can't safely retry, and caches can't cache.

## In plain terms (newbie lane)

This chapter is really about **Methods**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Method      CRUD        Safe?   Idempotent?   Body?
  ─────────   ─────────   ─────   ───────────   ─────
  GET         Read        yes     yes           no
  POST        Create/RPC  no      no            yes
  PUT         Replace     no      yes           yes
  PATCH       Update      no      maybe         yes
  DELETE      Remove      no      yes           optional
  HEAD        Metadata    yes     yes           no
  OPTIONS     Caps/CORS   yes     yes           no

  Safe        = no side effects (read-only)
  Idempotent  = N calls = same effect as 1 call
```

*Safety and idempotency are contracts. They determine what caches cache, what proxies retry, and what your code can safely repeat.*

## Concept deep-dive

### The common methods

| Method | CRUD mapping | Safe? | Idempotent? | Typical body |
|--------|-------------|-------|-------------|-------------|
| `GET` | Read | Yes | Yes | No body (some servers accept one, but don't rely on it) |
| `POST` | Create / RPC | No | No | Yes — the data to create or the action to perform |
| `PUT` | Full replace | No | Yes | Yes — the complete new representation |
| `PATCH` | Partial update | No | Depends on implementation | Yes — only the fields to change |
| `DELETE` | Remove | No | Yes | Optional (most servers ignore it) |
| `HEAD` | Metadata only | Yes | Yes | No body returned (same headers as GET) |
| `OPTIONS` | Capabilities / CORS preflight | Yes | Yes | No body |

### Safe methods

A method is *safe* when it has no observable side effects on the server. `GET`, `HEAD`, and `OPTIONS` are safe. The server can log the request and update analytics, but it must not create, modify, or delete resources.

Why does safety matter? Because it tells caches they can serve responses without worrying about stale data, tells prefetchers they can prefetch links without side effects, and tells search engines they can crawl without modifying your data.

### Idempotent methods

A method is *idempotent* when making the same request N times produces the same result as making it once. `GET`, `PUT`, `DELETE`, `HEAD`, and `OPTIONS` are all idempotent.

`PUT /users/42 { "name": "Ada" }` is idempotent: no matter how many times you send it, user 42's name is "Ada." `POST /users { "name": "Ada" }` is *not* idempotent: each call might create a new user.

Why does idempotency matter? Because it determines whether you can *safely retry* a failed request. If a PUT times out and you're not sure if the server processed it, you can retry without fear of duplicate effects. If a POST times out, retrying might create a duplicate resource.

### Mapping methods to resources

```
GET    /users           → list all users
GET    /users/42        → get user 42
POST   /users           → create a new user
PUT    /users/42        → replace user 42 entirely
PATCH  /users/42        → update specific fields of user 42
DELETE /users/42        → remove user 42
```

The path names the resource (a noun). The method provides the verb. This is why `/getUser/42` or `/deleteUser/42` are anti-patterns — the verb is redundant with the method.

### Using methods in `fetch`

```ts
// GET (default)
const users = await fetch("/api/users");

// POST with JSON body
await fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Ada", email: "ada@example.com" }),
});

// PUT — full replacement
await fetch("/api/users/42", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Ada", email: "ada@new.com", role: "admin" }),
});

// PATCH — partial update
await fetch("/api/users/42", {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "ada@new.com" }),
});

// DELETE
await fetch("/api/users/42", { method: "DELETE" });
```

### POST for non-create operations (RPC)

Not every action maps cleanly to CRUD. When you need to "archive a user," "send a notification," or "run a report," REST conventions get awkward. Using POST for these actions is standard:

```
POST /users/42/archive          → archive user 42
POST /users/42/send-invite      → send invite to user 42
POST /reports/generate           → generate a report
```

Keep the action under a resource whenever possible. This preserves discoverability and keeps the URL meaningful.

### Method overrides

Some legacy proxies or firewalls only allow GET and POST. The workaround: send POST with an `X-HTTP-Method-Override` header:

```ts
await fetch(url, {
  method: "POST",
  headers: { "X-HTTP-Method-Override": "DELETE" },
});
```

This is rare in modern networks. You'll likely only encounter it behind corporate proxies or with very old API gateways.

### HEAD

`HEAD` is identical to `GET` but returns only headers, no body. Use it to:

- Check `Content-Length` before downloading a large file.
- Check `Last-Modified` to see if a resource changed.
- Verify a URL exists (200 vs. 404) without transferring data.

### OPTIONS

Used by browsers for CORS preflight: "Am I allowed to make this cross-origin request?" Also useful for discovering allowed methods via the `Allow` response header.

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Separate methods instead of one verb + action param | Enables semantic behavior by caches, proxies, retry logic | RPC-style with a single POST endpoint | gRPC, GraphQL — when you want a single endpoint with flexible operations |
| PUT is idempotent | Safe to retry on timeout — you know the state after success | POST for all writes | When you can't guarantee full-replacement semantics |
| PATCH separate from PUT | PUT replaces the entire resource; PATCH updates a subset | Only PUT (client sends full object every time) | When partial updates are rare and sending the full object is simpler |
| POST is not idempotent by default | Creating a resource should produce a new resource each time | Make everything idempotent with keys | Use idempotency keys when you need safe retries on POST |

## Production-quality code

```ts
class HttpError extends Error {
  constructor(public readonly status: number, public readonly body: string) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
  }
}

interface FetchOptions {
  headers?: Record<string, string>;
  signal?: AbortSignal;
  idempotencyKey?: string;
}

async function handleResponse<T>(r: Response): Promise<T> {
  if (!r.ok) throw new HttpError(r.status, await r.text());
  if (r.status === 204) return undefined as T;
  return (await r.json()) as T;
}

function jsonHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    "Accept": "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
}

export const api = {
  async get<T>(url: string, opts: FetchOptions = {}): Promise<T> {
    const r = await fetch(url, {
      headers: { "Accept": "application/json", ...opts.headers },
      signal: opts.signal,
    });
    return handleResponse<T>(r);
  },

  async post<T>(url: string, body: unknown, opts: FetchOptions = {}): Promise<T> {
    const headers = jsonHeaders(opts.headers);
    if (opts.idempotencyKey) {
      headers["Idempotency-Key"] = opts.idempotencyKey;
    }
    const r = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
      signal: opts.signal,
    });
    return handleResponse<T>(r);
  },

  async put<T>(url: string, body: unknown, opts: FetchOptions = {}): Promise<T> {
    const r = await fetch(url, {
      method: "PUT",
      headers: jsonHeaders(opts.headers),
      body: JSON.stringify(body),
      signal: opts.signal,
    });
    return handleResponse<T>(r);
  },

  async patch<T>(url: string, body: unknown, opts: FetchOptions = {}): Promise<T> {
    const r = await fetch(url, {
      method: "PATCH",
      headers: jsonHeaders(opts.headers),
      body: JSON.stringify(body),
      signal: opts.signal,
    });
    return handleResponse<T>(r);
  },

  async del(url: string, opts: FetchOptions = {}): Promise<void> {
    const r = await fetch(url, {
      method: "DELETE",
      headers: { "Accept": "application/json", ...opts.headers },
      signal: opts.signal,
    });
    if (!r.ok && r.status !== 404) {
      throw new HttpError(r.status, await r.text());
    }
  },
};
```

## Security notes

- **GET requests should never trigger side effects.** If a GET endpoint creates or deletes data, CSRF attacks become trivial — an `<img src="/api/delete-account">` tag in an email would trigger the action.
- **CSRF on POST** — browsers automatically include cookies on cross-origin POST requests. Use CSRF tokens or `SameSite` cookies to prevent unauthorized state changes.
- **Method overrides** — if your server supports `X-HTTP-Method-Override`, validate that only authorized clients can use it. An attacker might turn a POST into a DELETE.

## Performance notes

- **GET responses are cacheable by default.** Proxies, CDNs, and browsers cache GET responses based on `Cache-Control` headers. POST, PUT, PATCH, and DELETE responses are never cached.
- **HEAD is cheap.** When you only need metadata (content length, last modified, existence check), HEAD avoids transferring the body entirely.
- **Batching vs. individual requests** — if you need to create 100 resources, 100 individual POST requests incur 100 round trips. Some APIs offer batch endpoints to reduce this overhead.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "Retrying POST caused duplicate orders" | POST is not idempotent; each retry creates a new resource | Use an `Idempotency-Key` header so the server can deduplicate |
| 2 | "Using POST for reads — cache never kicks in" | POST responses aren't cached by default | Use GET for read operations; it's cacheable and safe |
| 3 | "DELETE with body — server ignores the body" | Many servers and proxies strip the body from DELETE requests | Move the filter criteria to query parameters or the path |
| 4 | "Treating PATCH as PUT — overwriting fields with `null`" | PATCH should update *only* the provided fields; PUT replaces the entire resource | If using PATCH, send only the fields you want to change; omit the rest |

## Practice

### Warm-up

Match each HTTP method to its CRUD operation: GET → ?, POST → ?, PUT → ?, PATCH → ?, DELETE → ?

<details><summary>Show solution</summary>

- GET → Read
- POST → Create (or RPC action)
- PUT → Replace (full update)
- PATCH → Partial update
- DELETE → Remove

</details>

### Standard

Implement typed wrappers for GET, POST, PUT, PATCH, and DELETE using `fetch`. Each should set appropriate headers and throw `HttpError` on failure.

<details><summary>Show solution</summary>

```ts
class HttpError extends Error {
  constructor(public status: number, public body: string) {
    super(`HTTP ${status}`);
  }
}

async function get<T>(url: string): Promise<T> {
  const r = await fetch(url, { headers: { Accept: "application/json" } });
  if (!r.ok) throw new HttpError(r.status, await r.text());
  return (await r.json()) as T;
}

async function post<T>(url: string, body: unknown): Promise<T> {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new HttpError(r.status, await r.text());
  return (await r.json()) as T;
}

// put, patch, del follow the same pattern with their respective methods
```

</details>

### Bug hunt

A developer retries all failed requests regardless of method. A payment POST fails with a timeout, gets retried, and the customer is charged twice. Why did this happen and how do you fix it?

<details><summary>Show solution</summary>

POST is not idempotent — the server treats each request as a new creation. When the first POST succeeded but the response was lost due to timeout, the retry created a second payment. Fix: send an `Idempotency-Key` header with a unique value (e.g., UUID) that the server uses to deduplicate. If the server sees the same key twice, it returns the original response instead of processing again.

</details>

### Stretch

Add an `Idempotency-Key` header to POST requests. Generate the key client-side and pass it through.

<details><summary>Show solution</summary>

```ts
async function safePost<T>(url: string, body: unknown): Promise<T> {
  const idempotencyKey = crypto.randomUUID();
  const r = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return (await r.json()) as T;
}
```

The key should be stored and reused for retries of the *same logical operation*, so the server can deduplicate.

</details>

### Stretch++

Write a CLI tool that tests every method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS) against `httpbin.org` and prints the status code and response for each.

<details><summary>Show solution</summary>

```ts
const base = "https://httpbin.org";
const methods = [
  { method: "GET", url: `${base}/get` },
  { method: "POST", url: `${base}/post`, body: { test: true } },
  { method: "PUT", url: `${base}/put`, body: { test: true } },
  { method: "PATCH", url: `${base}/patch`, body: { test: true } },
  { method: "DELETE", url: `${base}/delete` },
  { method: "HEAD", url: `${base}/get` },
  { method: "OPTIONS", url: `${base}/get` },
];

for (const { method, url, body } of methods) {
  const r = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const size = method === "HEAD" ? "(no body)" : `${(await r.text()).length} bytes`;
  console.log(`${method.padEnd(8)} ${r.status} ${size}`);
}
```

</details>

## Quiz

1. Safe methods include:
   (a) GET, POST  (b) GET, HEAD, OPTIONS  (c) All methods  (d) POST, PUT

2. Which methods are idempotent?
   (a) GET only  (b) PUT only  (c) DELETE only  (d) GET, PUT, DELETE, HEAD, OPTIONS

3. Partial update uses:
   (a) PUT  (b) PATCH  (c) POST  (d) HEAD

4. Retrying POST without an idempotency key is:
   (a) Always safe  (b) Risky — may create duplicates  (c) Required by spec  (d) Blocked by servers

5. OPTIONS is mainly used for:
   (a) CORS preflight and capability discovery  (b) Creating resources  (c) Deleting resources  (d) Authentication

**Short answer:**

6. What is the semantic difference between PUT and PATCH?
7. Give one practical example of an idempotency key.

*Answers: 1-b, 2-d, 3-b, 4-b, 5-a. 6 — PUT replaces the entire resource with the provided representation; PATCH modifies only the fields included in the request. If you PUT without a field, it's removed; if you PATCH without a field, it's left unchanged. 7 — A payment processing API: the client generates a UUID for each payment attempt and sends it as `Idempotency-Key`. If the request is retried due to a timeout, the server recognizes the duplicate key and returns the original response instead of charging again.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-methods — mini-project](mini-projects/07-methods-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- HTTP methods carry semantic intent: GET reads, POST creates, PUT replaces, PATCH updates, DELETE removes.
- *Safe* methods (GET, HEAD, OPTIONS) have no side effects. *Idempotent* methods (GET, PUT, DELETE, HEAD, OPTIONS) can be safely retried.
- POST is not idempotent — use idempotency keys when you need safe retries on create operations.
- Keep verbs in the method, nouns in the path. Avoid `/getUser` or `/deleteItem` patterns.

## Further reading

- RFC 9110, *HTTP Semantics* — the authoritative specification for method definitions.
- Stripe API docs, *Idempotent Requests* — a well-designed real-world example.
- Next: [Paths](08-paths.md).
