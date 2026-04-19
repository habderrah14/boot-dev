# Chapter 01 — Why HTTP?

> "HTTP is the lingua franca of the web. Almost every backend is an HTTP server *and* an HTTP client. Knowing the protocol well is a competitive advantage, not a specialty."

## Learning objectives

By the end of this chapter you will be able to:

- Explain HTTP's request/response model and why it exists.
- Identify the major HTTP versions (1.1, 2, 3) and what each improves.
- List every part of a request and a response.
- Describe statelessness and why it matters for scaling.

## Prerequisites & recap

- A working TypeScript project ([Module 09 ch. 15](../09-ts/15-local-development.md)).

## The simple version

HTTP is a conversation between two computers. One computer (the *client*) sends a request — "give me this resource" or "store this data" — and the other computer (the *server*) sends back a response. Every request gets exactly one response. That's the whole pattern: ask → answer.

The protocol is *stateless*, meaning the server forgets about you the instant it finishes responding. If the server needs to "remember" you, something else — a cookie, a token, a database row — must carry that context. This forgetfulness is a feature: it lets you spread traffic across many servers because no single server holds your session in memory.

## In plain terms (newbie lane)

This chapter is really about **Why HTTP?**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌────────┐         request          ┌────────┐
  │        │ ──────────────────────▶  │        │
  │ Client │   method, path, headers, │ Server │
  │        │   optional body          │        │
  │        │                          │        │
  │        │  ◀──────────────────────  │        │
  └────────┘         response         └────────┘
                 status, headers,
                   optional body
```

*Every HTTP interaction is one request → one response. The client always initiates.*

## Concept deep-dive

### What is HTTP?

**H**yper**T**ext **T**ransfer **P**rotocol — an application-layer protocol (OSI layer 7) that runs over TCP (or QUIC for HTTP/3). In version 1.x it is text-based; in versions 2 and 3 it uses binary framing.

Why does this matter to you? Because almost every external service you integrate with — databases proxied through REST, third-party APIs, your own microservices — speaks HTTP. Understanding the protocol means you can debug problems at the wire level instead of guessing at abstractions.

### The request

A request is structured text with four parts:

```
POST /api/users HTTP/1.1          ← request line: METHOD PATH VERSION
Host: api.example.com             ← headers: Key: Value
User-Agent: curl/8.0
Content-Type: application/json
Content-Length: 24
                                  ← blank line separates headers from body
{"name":"Ada","id":1}             ← body (optional)
```

- **Request line** — tells the server *what you want to do* (method), *where* (path), and *which dialect* (version).
- **Headers** — metadata: who you are, what format you accept, authentication tokens, tracing IDs.
- **Body** — the payload. Only some methods (POST, PUT, PATCH) typically carry one.

### The response

```
HTTP/1.1 201 Created              ← status line: VERSION CODE REASON
Content-Type: application/json
Location: /api/users/1
Content-Length: 24
                                  ← blank line
{"id":1,"name":"Ada"}             ← body (optional; often JSON)
```

- **Status line** — the version, a numeric code, and a human-readable reason phrase.
- **Headers** — metadata about the response (content type, caching, location of a new resource).
- **Body** — the actual data the server is returning (or empty for 204 No Content).

### Statelessness

Each request is self-contained. The server doesn't remember previous requests unless something external — cookies, auth headers, or the server's own database — carries state across them.

Why is this a deliberate choice? Because statelessness is what allows horizontal scaling. If no server holds session state in memory, you can put a load balancer in front of ten servers and route any request to any of them. That's far simpler than synchronizing in-memory sessions across machines.

### Versions

- **HTTP/1.1** — text-based, one request per TCP connection at a time (with keep-alive for connection reuse). Works everywhere. You'll still encounter it daily.
- **HTTP/2** — binary framing, multiplexing (many concurrent streams over a single connection), header compression (HPACK). Solves head-of-line blocking at the application layer.
- **HTTP/3** — runs over QUIC (UDP instead of TCP), which gives faster handshakes, better loss recovery, and mandatory TLS. Solves head-of-line blocking at the transport layer too.

Your client libraries negotiate the version automatically based on what the server advertises. You rarely pick a version by hand, but you need to know what each one buys you when debugging latency or connection issues.

### TLS

HTTPS = HTTP over TLS. It adds encryption and server authentication via certificates. In production, always use HTTPS — there is no legitimate reason to serve an API over plain HTTP. See [ch. 09](09-https.md) for the full story.

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Text-based (HTTP/1.1) | Human-readable; easy to debug with `curl -v` | Binary (HTTP/2+) | When you need multiplexing or header compression |
| Stateless | Horizontal scaling, simplicity | Stateful (WebSockets, gRPC streams) | Long-lived bidirectional connections (chat, gaming) |
| Request/response | Simple mental model; maps to function calls | Streaming, pub/sub | Real-time data feeds, event-driven architectures |
| Single response per request | Predictable; easy to cache | Server push (HTTP/2), SSE | When the server needs to send updates unprompted |

## Production-quality code

```ts
async function httpInspect(targetUrl: string, timeoutMs = 5_000): Promise<void> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);

  try {
    const response = await fetch(targetUrl, { signal: ctrl.signal });

    console.log(`Status:  ${response.status} ${response.statusText}`);
    console.log("Headers:");
    for (const [key, value] of response.headers) {
      console.log(`  ${key}: ${value}`);
    }

    const body = await response.text();
    console.log(`Body:    ${body.length} bytes`);
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      console.error(`Request timed out after ${timeoutMs}ms`);
    } else {
      console.error("Network error:", (err as Error).message);
    }
    process.exitCode = 1;
  } finally {
    clearTimeout(timer);
  }
}

const url = process.argv[2];
if (!url) {
  console.error("Usage: npx tsx 01-why-http.ts <url>");
  process.exit(1);
}
httpInspect(url);
```

## Security notes

- **Always use HTTPS in production.** Plain HTTP exposes every header — including `Authorization` — to anyone on the network path.
- **Never trust the server's response body blindly.** Even HTTPS guarantees only that the bytes came from the right server; the server itself may return bad data. Validate at the boundary ([ch. 10](10-runtime-validation.md)).
- **Sensitive headers (tokens, cookies) can leak via logs.** Redact before logging.

## Performance notes

- **DNS + TCP + TLS handshake** — the first request to a new host pays ~3 round trips before a single byte of HTTP flows. Connection reuse (keep-alive, HTTP/2 multiplexing) amortizes this cost.
- **HTTP/2 multiplexing** avoids head-of-line blocking at the application layer, so many requests in flight share one connection without waiting for each other.
- **Body size** — larger payloads cost bandwidth and parse time. Use `Accept-Encoding: gzip` to compress, and only request the fields you need (if the API supports sparse fieldsets).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "fetch didn't throw on 404 — my code kept running with bad data" | `fetch` resolves on *all* HTTP statuses, including errors; it only rejects on network failures | Check `response.ok` or `response.status` before reading the body |
| 2 | "My parallel requests on HTTP/1.1 are slower than expected" | HTTP/1.1 sends one request at a time per connection (pipelining is unreliable) | Use HTTP/2 for true multiplexing, or open multiple connections |
| 3 | "I keep confusing TLS versions with HTTP versions" | They're independent layers — HTTP/1.1 can run over TLS 1.3, and HTTP/2 can run over TLS 1.2 | Remember: HTTP version = application protocol, TLS version = encryption layer |
| 4 | "I thought HTTP keeps a session between requests" | HTTP is stateless by design; the server forgets you after each response | Use cookies, tokens, or server-side sessions to carry state explicitly |

## Practice

### Warm-up

Run `curl -v https://example.com`. Identify the request line, at least three request headers, the status line, and two response headers.

<details><summary>Show solution</summary>

```
> GET / HTTP/2                        ← request line
> Host: example.com                   ← request header 1
> User-Agent: curl/8.x               ← request header 2
> Accept: */*                         ← request header 3

< HTTP/2 200                          ← status line
< content-type: text/html; ...        ← response header 1
< content-length: 1256                ← response header 2
```

</details>

### Standard

Use `fetch` to GET a JSON endpoint (try `https://httpbin.org/get`). Print the status code and the parsed body.

<details><summary>Show solution</summary>

```ts
const response = await fetch("https://httpbin.org/get");
console.log("Status:", response.status);
console.log("Body:", await response.json());
```

</details>

### Bug hunt

A developer writes this code and assumes it will catch a 404:

```ts
try {
  const data = await fetch("https://httpbin.org/status/404");
  console.log("Got data:", await data.text());
} catch (e) {
  console.log("Error caught!");
}
```

Why does `"Error caught!"` never print?

<details><summary>Show solution</summary>

`fetch` only rejects on *network* errors (DNS failure, connection refused, abort). An HTTP 404 is a perfectly valid response — the server successfully answered "not found." You must check `data.ok` or `data.status` yourself.

</details>

### Stretch

Use `fetch` to POST a JSON body to `https://httpbin.org/post`. Set the `Content-Type` header and print the response.

<details><summary>Show solution</summary>

```ts
const response = await fetch("https://httpbin.org/post", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Ada", role: "engineer" }),
});
console.log(response.status);
console.log(await response.json());
```

</details>

### Stretch++

Compare HTTP/1.1 vs. HTTP/2 latency by running `curl` with `--http1.1` and `--http2` against `https://httpbin.org/get`. Use `-w '\ntime_total: %{time_total}\n'` to measure total time. Run each five times and compare the median.

<details><summary>Show solution</summary>

```bash
# HTTP/1.1
for i in {1..5}; do
  curl -s -o /dev/null --http1.1 -w '%{time_total}\n' https://httpbin.org/get
done

# HTTP/2
for i in {1..5}; do
  curl -s -o /dev/null --http2 -w '%{time_total}\n' https://httpbin.org/get
done
```

For a single request, the difference is mainly the handshake. HTTP/2's multiplexing advantage shows when you issue many requests concurrently over one connection.

</details>

## Quiz

1. HTTP operates at which layer?
   (a) Transport layer  (b) Application layer over TCP/QUIC  (c) Data-link layer  (d) Physical layer

2. An HTTP request contains:
   (a) Method + path + version + headers + optional body  (b) Method only  (c) Headers only  (d) Body only

3. "Stateless" means:
   (a) No state anywhere in the system  (b) Each request is self-contained on the server side  (c) Cookies are not allowed  (d) No body is permitted

4. HTTP/2's main improvement over 1.1 is:
   (a) Text framing  (b) Binary framing + multiplexing  (c) QUIC transport  (d) Mandatory TLS

5. HTTPS uses:
   (a) Plaintext HTTP  (b) HTTP over TLS  (c) HTTP over QUIC only  (d) HTTP/3 only

**Short answer:**

6. Why does statelessness simplify horizontal scaling?
7. What problem does multiplexing solve in HTTP/2?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b. 6 — Any server can handle any request because no server holds session state in memory, so a load balancer can route freely. 7 — It eliminates head-of-line blocking at the application layer by letting multiple streams share one TCP connection concurrently instead of waiting one-at-a-time.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-why-http — mini-project](mini-projects/01-why-http-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- HTTP is a request/response protocol over TCP (or QUIC). The client always initiates.
- It is stateless by design — this is what makes horizontal scaling practical.
- Versions 1.1 (text), 2 (binary + multiplexing), and 3 (QUIC) each solve specific latency and throughput problems.
- HTTPS (HTTP + TLS) is non-negotiable in production.

## Further reading

- Julia Evans, *HTTP: Learn your browser's language* — a visual, approachable introduction.
- RFC 9110, *HTTP Semantics* — the definitive specification.
- Next: [DNS](02-dns.md).
