# Chapter 03 — URIs

> "A URI is the address of a resource. Parse it wrong and everything downstream breaks."

## Learning objectives

By the end of this chapter you will be able to:

- Identify every part of a URI: scheme, userinfo, host, port, path, query, fragment.
- Build and parse URLs safely with the `URL` class — never string concatenation.
- Encode and decode percent-encoded strings correctly.
- Distinguish URL from URI from URN and know which term to use when.

## Prerequisites & recap

- [Why HTTP](01-why-http.md) — you know requests target a path on a host.

## The simple version

A URL is a structured address. Just like a postal address has a country, city, street, and apartment number, a URL has a scheme (`https`), a host (`api.example.com`), a path (`/v1/users`), and optional extras like a query string (`?limit=10`) and a fragment (`#section`).

The critical rule: never build URLs by gluing strings together. Use the `URL` class. String concatenation leads to double slashes, missing encoding, and injection vulnerabilities. The `URL` class handles all of that for you.

## In plain terms (newbie lane)

This chapter is really about **URIs**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  https://user:pass@api.example.com:443/v1/users?limit=10#section
  \___/   \_______/ \_______________/ \_/ \________/ \______/ \______/
  scheme   userinfo      host        port    path     query   fragment
    │         │            │           │       │         │        │
    │         │            │           │       │         │        └─ client-only
    │         │            │           │       │         └─ filters
    │         │            │           │       └─ resource identity
    │         │            │           └─ defaults by scheme
    │         │            └─ where (after DNS)
    │         └─ rare; avoid in APIs
    └─ how (protocol)
```

*Every part has a job. Only scheme, host, and path are used in most API calls.*

## Concept deep-dive

### URI vs. URL vs. URN

These three terms confuse everyone, but the distinction is simple:

- **URI** (Uniform Resource Identifier) — the umbrella term. It *names* something.
- **URL** (Uniform Resource Locator) — a URI that also tells you *how and where* to get it. `https://example.com/page` is a URL.
- **URN** (Uniform Resource Name) — a URI that *names* something without saying where it is. `urn:isbn:978-0-13-468599-1` is a URN.

In practice, when you're working with HTTP, you'll say "URL" and mean it. The spec pedant says "URI," but nobody will correct you at work.

### Anatomy of a URL

```
https://user:pass@api.example.com:443/v1/users?limit=10#section
```

| Part | Value | Required? | Purpose |
|------|-------|-----------|---------|
| **Scheme** | `https` | Yes | Determines the protocol |
| **Userinfo** | `user:pass` | Rare | HTTP Basic auth in the URL (avoid — it's visible) |
| **Host** | `api.example.com` | Yes | Server to connect to (after DNS) |
| **Port** | `443` | No — defaults by scheme (80/443) | TCP port |
| **Path** | `/v1/users` | Yes (at least `/`) | Identifies the resource |
| **Query** | `limit=10` | No | Key-value filters, pagination, etc. |
| **Fragment** | `section` | No | Client-side only — never sent to server |

### The `URL` class

The `URL` class is built into Node 16+ and all modern browsers. It parses, validates, and lets you mutate URLs safely:

```ts
const u = new URL("https://api.example.com/v1/users?limit=10");

u.hostname;                      // "api.example.com"
u.port;                          // "" (default for https)
u.pathname;                      // "/v1/users"
u.search;                        // "?limit=10"
u.searchParams.get("limit");     // "10"
u.origin;                        // "https://api.example.com"
```

Setters mutate in place and keep the URL valid:

```ts
u.searchParams.set("limit", "20");
u.pathname = "/v1/orders";
u.toString();  // "https://api.example.com/v1/orders?limit=20"
```

Why use this instead of string concatenation? Because the `URL` class handles encoding, slash normalization, and validation automatically. String concatenation doesn't.

### Relative URLs and base

A relative URL like `/v1/users` has no scheme or host. The `URL` constructor requires a base to resolve it:

```ts
new URL("/v1/users", "https://api.example.com");
// → https://api.example.com/v1/users

new URL("/v1/users");
// → TypeError: Invalid URL
```

This is exactly how browsers resolve relative links — against the page's origin. Your API client should do the same against a configured base URL.

### Percent encoding

Certain characters have special meaning in URLs (`/`, `?`, `#`, `&`, `=`, space). When these characters appear in *data* (a username, a search term), they must be percent-encoded:

```ts
encodeURIComponent("hello world/#");   // "hello%20world%2F%23"
decodeURIComponent("hello%20world");   // "hello world"
```

The good news: `URLSearchParams` handles encoding automatically for query values:

```ts
const u = new URL("https://api.example.com/search");
u.searchParams.set("q", "hello world/#");
u.toString();  // "https://api.example.com/search?q=hello+world%2F%23"
```

### Path vs. query — when to use which

- **Path** identifies the resource: `/users/42` — "user 42."
- **Query** refines or filters: `/users?role=admin&limit=10` — "admin users, first 10."

The rule of thumb: if two different values produce *different resources*, it belongs in the path. If two different values produce *different views of the same resource*, it belongs in the query.

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Structured format with fixed part order | Unambiguous parsing; every library agrees on what's the host vs. the path | Flat strings | You wouldn't — ambiguity breaks routing |
| Percent encoding | Allows any Unicode character in any URL part without ambiguity | Disallow special characters | You'd lose expressiveness |
| Fragment is client-only | Server never needs to know which section you scrolled to; keeps caching simple | Send fragment to server | Single-page apps use fragments for routing — a workaround, not a design win |
| `URLSearchParams` auto-encoding | Prevents injection and encoding bugs | Manual `encodeURIComponent` everywhere | Only when you need control over encoding details (rare) |

## Production-quality code

```ts
interface BuildUrlOptions {
  base: string;
  path: string;
  query?: Record<string, string | number | boolean>;
}

function buildUrl({ base, path, query }: BuildUrlOptions): URL {
  const url = new URL(path, base);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      url.searchParams.set(key, String(value));
    }
  }

  return url;
}

function appendPathSegment(url: URL, segment: string): URL {
  const encoded = encodeURIComponent(segment);
  const base = url.pathname.endsWith("/") ? url.pathname : url.pathname + "/";
  url.pathname = base + encoded;
  return url;
}

// Usage
const usersUrl = buildUrl({
  base: "https://api.example.com",
  path: "/v1/users",
  query: { role: "admin", limit: 10, active: true },
});
// https://api.example.com/v1/users?role=admin&limit=10&active=true

const userUrl = appendPathSegment(
  new URL("/v1/users", "https://api.example.com"),
  "42",
);
// https://api.example.com/v1/users/42
```

## Security notes

- **URL injection** — if user input goes into a URL without encoding, an attacker can manipulate the path or query to access unintended resources. Always use `encodeURIComponent` for path segments and `searchParams.set` for query values.
- **Userinfo in URLs** — `https://user:pass@host` puts credentials in the URL, which ends up in logs, browser history, and `Referer` headers. Never use this pattern.
- **Open redirect** — if you accept a URL from user input and redirect to it, validate the scheme and host. An attacker can redirect to `https://evil.com`.

## Performance notes

N/A — URL parsing is microsecond-scale work. The `URL` constructor is a single allocation. The cost of building URLs is negligible compared to the network round trip that follows.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `TypeError: Invalid URL` on a path like `/v1/users` | Relative URLs require a base argument in the `URL` constructor | Pass a base: `new URL("/v1/users", baseUrl)` |
| 2 | Double slashes in the path: `https://api.com//v1//users` | String concatenation of base and path without checking slashes | Use the `URL` constructor — it normalizes paths |
| 3 | Query parameter with `&` in the value breaks parsing | Value wasn't encoded: `?q=a&b` is two params, not one value | Use `searchParams.set("q", "a&b")` — it encodes automatically |
| 4 | Server treats `/users` and `/users/` as different resources | Trailing-slash inconsistency | Pick one policy and canonicalize; strip or add trailing slashes consistently |

## Practice

### Warm-up

Parse `https://ex.com/a?b=1#top` using `new URL()` and print each component: protocol, hostname, pathname, search, and hash.

<details><summary>Show solution</summary>

```ts
const u = new URL("https://ex.com/a?b=1#top");
console.log("protocol:", u.protocol);   // "https:"
console.log("hostname:", u.hostname);   // "ex.com"
console.log("pathname:", u.pathname);   // "/a"
console.log("search:", u.search);       // "?b=1"
console.log("hash:", u.hash);           // "#top"
```

</details>

### Standard

Build a URL with two query parameters using `searchParams.set`. Start from `https://api.example.com/search`.

<details><summary>Show solution</summary>

```ts
const u = new URL("https://api.example.com/search");
u.searchParams.set("q", "typescript");
u.searchParams.set("page", "2");
console.log(u.toString());
// https://api.example.com/search?q=typescript&page=2
```

</details>

### Bug hunt

A developer writes `const u = new URL(userInput)` where `userInput` is `"/users"`. The code throws. Why?

<details><summary>Show solution</summary>

`/users` is a relative URL — it has no scheme or host. The `URL` constructor requires either an absolute URL or a second argument providing the base. Fix: `new URL(userInput, "https://api.example.com")`.

</details>

### Stretch

Write a function `appendPath(url: URL, segment: string): URL` that safely appends a path segment, handling trailing slashes and encoding.

<details><summary>Show solution</summary>

```ts
function appendPath(url: URL, segment: string): URL {
  const result = new URL(url.toString());
  const base = result.pathname.endsWith("/")
    ? result.pathname
    : result.pathname + "/";
  result.pathname = base + encodeURIComponent(segment);
  return result;
}

const base = new URL("https://api.example.com/v1/users");
console.log(appendPath(base, "42").toString());
// https://api.example.com/v1/users/42

console.log(appendPath(base, "hello world").toString());
// https://api.example.com/v1/users/hello%20world
```

</details>

### Stretch++

Handle trailing-slash inconsistency: write a function that normalizes any URL to your chosen policy (e.g., always strip trailing slashes on paths, except for root `/`).

<details><summary>Show solution</summary>

```ts
function normalizeTrailingSlash(url: URL): URL {
  const result = new URL(url.toString());
  if (result.pathname !== "/" && result.pathname.endsWith("/")) {
    result.pathname = result.pathname.slice(0, -1);
  }
  return result;
}

console.log(normalizeTrailingSlash(new URL("https://api.com/users/")).pathname);
// "/users"

console.log(normalizeTrailingSlash(new URL("https://api.com/")).pathname);
// "/"
```

</details>

## Quiz

1. A URL's main parts are:
   (a) Scheme + host + path + query + fragment  (b) Scheme only  (c) Host + body  (d) Scheme + body

2. The modern way to parse a URL in Node/browser is:
   (a) `URL.parse()`  (b) `new URL(str)`  (c) Regex  (d) `url.parse()` (deprecated)

3. To safely encode a query parameter value, use:
   (a) `encodeURIComponent`  (b) `encodeURI`  (c) Nothing  (d) `JSON.stringify`

4. A relative URL needs:
   (a) A base URL  (b) A fragment  (c) A host header  (d) A port

5. The difference between a URN and a URL is:
   (a) They're identical  (b) A URN identifies without locating; a URL locates  (c) Both are unused  (d) A URN is for TLS

**Short answer:**

6. Why should you never build URLs by concatenating strings?
7. Give one case where the trailing slash makes a difference.

*Answers: 1-a, 2-b, 3-a, 4-a, 5-b. 6 — String concatenation skips encoding, can produce double slashes, and opens the door to injection attacks. The `URL` class handles all of this correctly. 7 — Some servers treat `/users` and `/users/` as different endpoints — one might 301-redirect to the other, or one might 404. Static file servers often treat `/dir/` as "list directory" and `/dir` as "look for a file named dir."*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-uris — mini-project](mini-projects/03-uris-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A URL has a fixed structure: scheme, host, path, query, fragment — each with a specific job.
- The `URL` class parses, validates, and mutates URLs safely; `searchParams` handles query encoding.
- Percent-encoding is required for special characters in data positions — `encodeURIComponent` or `searchParams` handles it.
- Never concatenate URL strings manually — use the `URL` constructor.

## Further reading

- WHATWG URL Standard — the living specification browsers implement.
- MDN, *URL API* — practical reference with examples.
- Next: [Errors](04-errors.md).
