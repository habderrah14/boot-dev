# Chapter 01 — Servers

> A server is a program that listens on a port, accepts requests, and responds. In 20 lines of TypeScript you can stand one up; the other 20 years are about _not_ breaking it.

## Learning objectives

By the end of this chapter you will be able to:

- Start an HTTP server in Node with the raw `node:http` module, Express, and Fastify.
- Trace the full request/response lifecycle from TCP accept to body flush.
- Set status codes, headers, and response bodies correctly.
- Validate configuration at boot time with Zod.
- Shut a server down gracefully so in-flight requests complete.
- Attach structured logging with per-request context.

## Prerequisites & recap

- [HTTP clients](../10-http-clients/README.md) — you already know what a request and response look like from the caller's side. Now you're building the other end.

## The simple version

Think of an HTTP server as a receptionist sitting at a desk (a port). Clients walk in (TCP connections), hand over a slip of paper (the request), and wait. The receptionist reads the slip, decides who should handle it, gets the answer, and hands back a reply (the response). If nobody is at the desk, the client gets a "connection refused." If the receptionist is overwhelmed, clients queue up or time out.

Your job in this chapter is to build that receptionist. You'll start with the raw Node API to see every moving part, then switch to frameworks that handle the boring plumbing for you. Along the way you'll learn why "just calling `process.exit()`" is the server equivalent of slamming the phone down mid-sentence.

## In plain terms (newbie lane)

This chapter is really about **Servers**. Skim _Learning objectives_ above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.
> **Actually:** you only need the _next_ honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>

## Visual flow

```
  ┌────────┐        ┌─────────────────────────────────┐
  │ Client │──TCP──▶│  Server (listening on port 3000) │
  └────────┘        │                                  │
                    │  1. Accept connection             │
      HTTP req ───▶ │  2. Parse method, path, headers   │
                    │  3. Route to handler               │
                    │  4. Handler runs logic              │
      HTTP res ◀─── │  5. Write status + headers + body  │
                    │  6. Close / keep-alive              │
                    └─────────────────────────────────┘
```

_Caption: The request/response lifecycle inside a Node HTTP server._

## System diagram (Mermaid)

```mermaid
flowchart LR
  Client[HTTP_client] --> Listener[Server_listen]
  Listener --> Router[Router]
  Router --> Handler[Handler]
  Handler --> Response[Response]
```

*Caption: Trace the flow (data/time/money) through this figure before reading further.*

_High-level HTTP server data flow for this chapter’s topic._

## Concept deep-dive

### Raw Node HTTP — the foundation

Before you reach for a framework, see what the platform gives you for free:

```ts
import http from "node:http";

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true }));
    return;
  }
  res.writeHead(404);
  res.end();
});

server.listen(3000, () => console.log("http://localhost:3000"));
```

This works, but there's no routing, no body parsing, no error handling. For anything beyond a health check you'll want a framework — but knowing what `createServer` does under the hood helps you debug every framework built on top of it.

### Why use a framework?

Raw `node:http` makes you reinvent routing, body parsing, CORS, content negotiation, and error handling on every project. Frameworks solve these problems once so you can focus on your domain logic. The two you'll encounter most often:

- **Express** — 20 years old, battle-tested, largest middleware ecosystem.
- **Fastify** — modern, async-first, schema validation built in, roughly 2–3× faster than Express in benchmarks.

### Express — the workhorse

```ts
import express from "express";
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => res.json({ ok: true }));
app.post("/users", (req, res) => res.status(201).json({ id: 1, ...req.body }));

app.listen(3000);
```

Express's callback-based API predates `async/await`. You need an `asyncHandler` wrapper (covered in Chapter 05) to forward thrown errors to middleware. Despite that, its ecosystem is enormous and hiring is easy.

### Fastify — the modern choice

```ts
import Fastify from "fastify";
const app = Fastify({ logger: true });
app.get("/health", async () => ({ ok: true }));
await app.listen({ port: 3000 });
```

Fastify is async from the start, has built-in JSON Schema validation, and includes a logger (pino) out of the box. If you're starting a new project with no legacy constraints, Fastify is the stronger default.

### Configuration — fail fast at boot

Load from environment variables, validate with Zod, and crash immediately if anything is missing. You never want to discover a missing `DATABASE_URL` at 2 AM when the first user hits the endpoint that needs it.

```ts
import { z } from "zod";

const env = z
  .object({
    PORT: z.coerce.number().default(3000),
    DATABASE_URL: z.string().url(),
    NODE_ENV: z
      .enum(["development", "production", "test"])
      .default("development"),
  })
  .parse(process.env);
```

**Why Zod at boot?** Because `process.env.PORT` is always a string (or undefined). Zod coerces, validates, and gives you a typed object in one step. If validation fails, you get a clear error message and the process exits before it can serve a single bad response.

### Graceful shutdown — don't slam the door

When your orchestrator (Docker, Kubernetes, systemd) sends `SIGTERM`, your server should:

1. Stop accepting new connections.
2. Let in-flight requests finish (up to a timeout).
3. Close database pools, flush logs.
4. Exit cleanly.

If you skip this, some users get a broken response mid-stream. In a rolling deploy, that means brief 502s on every release.

```ts
function shutdown() {
  server.close((err) => {
    if (err) process.exit(1);
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 10_000).unref();
}
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

The `setTimeout` is your safety net: if in-flight requests hang forever, you force-exit after 10 seconds so the deploy doesn't stall.

### Readiness + draining (production pattern)

In real deploys behind a load balancer, pair graceful shutdown with a readiness signal:

- `/health` answers: "process is alive"
- `/ready` answers: "safe to receive new traffic"

On `SIGTERM`, mark the app as **not ready** first, then stop accepting new connections and drain in-flight requests.

```ts
let isReady = true;
let inFlight = 0;

app.use((req, res, next) => {
  inFlight += 1;
  res.on("finish", () => {
    inFlight -= 1;
  });
  next();
});

app.get("/health", (_req, res) => {
  res.status(200).json({ ok: true });
});

app.get("/ready", (_req, res) => {
  if (!isReady) {
    res.status(503).json({ ok: false, reason: "shutting_down" });
    return;
  }
  res.status(200).json({ ok: true });
});

function shutdown(signal: string) {
  isReady = false;
  logger.info({ signal }, "draining server");

  server.close((err) => {
    if (err) {
      logger.error({ err }, "shutdown error");
      process.exit(1);
    }
    logger.info({ inFlight }, "shutdown complete");
    process.exit(0);
  });

  setTimeout(() => {
    logger.error({ inFlight }, "forced shutdown after timeout");
    process.exit(1);
  }, 10_000).unref();
}
```

This sequence reduces dropped requests during rolling deploys and makes load balancer behavior predictable.

### Logging — what happened and when

Every request should produce at least one log line with: method, path, status, duration, and a request ID. Use `pino` (or the framework's built-in logger) and output structured JSON so your log aggregator can index fields.

**Why not `console.log`?** Because `console.log` gives you a string. A log aggregator needs structured fields to filter, alert, and build dashboards. `pino` outputs JSON at roughly zero overhead compared to string interpolation.

**What not to log:** request bodies (PII risk), authorization tokens, passwords.

## Why these design choices

| Decision              | Trade-off                                      | When you'd pick differently                                                                              |
| --------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Express over Fastify  | Larger ecosystem, more tutorials               | You're starting fresh and want speed + built-in validation → use Fastify                                 |
| Zod at boot           | Process crashes if config is wrong             | You need partial startup (e.g., a health check that works without a DB) → validate lazily per-dependency |
| Graceful shutdown     | Slightly more code; 10s timeout delays deploys | Stateless lambda / serverless → not needed; container orchestrator handles it                            |
| Structured JSON logs  | Harder to read in a terminal during dev        | Local dev with no aggregator → use pino-pretty or console transport                                      |
| Single-process server | Simpler mental model                           | CPU-bound workloads → use `cluster` module or separate worker processes                                  |

## Production-quality code

```ts
import express, { Request, Response, NextFunction } from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import pino from "pino";
import pinoHttp from "pino-http";

const Env = z.object({
  PORT: z.coerce.number().default(3000),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),
  LOG_LEVEL: z
    .enum(["fatal", "error", "warn", "info", "debug", "trace"])
    .default("info"),
});
const env = Env.parse(process.env);

const logger = pino({ level: env.LOG_LEVEL });

const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "1mb" }));

app.use(
  pinoHttp({
    logger,
    genReqId: (req) => (req.headers["x-request-id"] as string) ?? randomUUID(),
  }),
);

app.get("/health", (_req: Request, res: Response) => {
  res.json({ ok: true, uptime: process.uptime() });
});

app.post("/echo", (req: Request, res: Response) => {
  res.json({ you_sent: req.body });
});

app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: "not_found" });
});

app.use((err: unknown, req: Request, res: Response, _next: NextFunction) => {
  req.log.error({ err }, "unhandled error");
  res.status(500).json({ error: "server_error" });
});

const server = app.listen(env.PORT, () => {
  logger.info({ port: env.PORT }, "server listening");
});

function shutdown(signal: string) {
  logger.info({ signal }, "shutting down");
  server.close((err) => {
    if (err) {
      logger.error({ err }, "error during shutdown");
      process.exit(1);
    }
    logger.info("shutdown complete");
    process.exit(0);
  });
  setTimeout(() => {
    logger.error("forced shutdown after timeout");
    process.exit(1);
  }, 10_000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
```

## Security notes

- **Disable `x-powered-by`** — `app.disable("x-powered-by")` removes the header that tells attackers you're running Express. It's free defense-in-depth.
- **Bind address matters** — `0.0.0.0` is reachable from outside the container (needed in Docker); `127.0.0.1` is local only. In production behind a reverse proxy, bind to `0.0.0.0` and let the proxy/firewall restrict access.
- **Body size limits** — without `express.json({ limit: "1mb" })`, an attacker can POST a multi-gigabyte body and OOM your server.
- **Don't log secrets** — never log `Authorization` headers, tokens, or passwords. Configure your logger's redaction list.
- **HTTPS termination** — in production, terminate TLS at the load balancer or reverse proxy (nginx, Caddy), not in Node. Node's TLS performance is adequate but you lose the operational benefits of centralized cert management.

## Performance notes

- **Event loop** — Node is single-threaded. A synchronous 50ms computation blocks every other request for that 50ms. Offload CPU work to worker threads or a separate service.
- **Keep-alive** — Node's HTTP server supports keep-alive by default. Clients reuse TCP connections, saving the three-way handshake on every request. Don't disable it unless you have a specific reason.
- **Backpressure** — if you write large responses with `res.write()`, check the return value. If it returns `false`, pause your data source until the `drain` event fires.
- **Startup time** — Zod parsing and logger setup add a few milliseconds. In serverless (Lambda), this matters; in long-running servers, it's negligible.
- **Cluster mode** — for CPU-bound servers, run one process per core via the `cluster` module or let your orchestrator (Kubernetes) scale horizontally with multiple pods.

## Common mistakes

| Symptom                                                   | Cause                                                                     | Fix                                                                                                  |
| --------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `req.body` is `undefined`                                 | Forgot `app.use(express.json())`                                          | Add the JSON body-parsing middleware before your routes                                              |
| Server unreachable inside Docker                          | Bound to `127.0.0.1` instead of `0.0.0.0`                                 | Use `app.listen(port)` without specifying host, or explicitly bind to `0.0.0.0`                      |
| `docker stop` takes 10 seconds and then kills the process | No `SIGTERM` handler — Docker waits its stop timeout then sends `SIGKILL` | Add graceful shutdown; close the server on `SIGTERM`                                                 |
| Full request bodies appear in logs (PII breach)           | Logging middleware dumps everything by default                            | Configure log redaction; never log bodies unless you explicitly opt in per-route                     |
| `EADDRINUSE` on restart during development                | Previous process didn't release the port                                  | Use `server.close()` in your shutdown handler; or use `--watch` with `node --watch` which handles it |

## Practice

**Warm-up.** Spin up a raw `node:http` server that returns `"pong"` with status 200 on `GET /ping` and 404 on everything else.

<details><summary>Solution</summary>

```ts
import http from "node:http";

const server = http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/ping") {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("pong");
    return;
  }
  res.writeHead(404);
  res.end();
});

server.listen(3000);
```

</details>

**Standard.** Convert the above to Express with a `/health` route returning `{ ok: true }`. Add `express.json()` middleware.

<details><summary>Solution</summary>

```ts
import express from "express";
const app = express();
app.use(express.json());
app.get("/health", (_req, res) => res.json({ ok: true }));
app.listen(3000, () => console.log("listening on 3000"));
```

</details>

**Bug hunt.** A colleague's Express server logs `req.body` as `undefined` even though the client is sending valid JSON. The client sets `Content-Type: application/json`. What's wrong?

<details><summary>Solution</summary>

The server is missing `app.use(express.json())`. Without this middleware, Express does not parse JSON bodies and `req.body` remains `undefined`. Add the middleware before any routes that need body access.

</details>

**Stretch.** Add graceful shutdown to your Express server. On `SIGTERM`, stop accepting new connections, wait up to 10 seconds for in-flight requests, then exit.

<details><summary>Solution</summary>

```ts
const server = app.listen(3000);

function shutdown() {
  server.close((err) => {
    if (err) process.exit(1);
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 10_000).unref();
}
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
```

</details>

**Stretch++.** Add structured logging with `pino-http`. Each request should get a unique ID (`X-Request-Id` header or generated UUID). Log method, path, status, and duration.

<details><summary>Solution</summary>

```ts
import pinoHttp from "pino-http";
import { randomUUID } from "node:crypto";

app.use(
  pinoHttp({
    genReqId: (req) => (req.headers["x-request-id"] as string) ?? randomUUID(),
  }),
);
```

`pino-http` automatically logs method, url, status code, and response time on every request completion.

</details>

## Quiz

1. Which Node.js API creates a raw HTTP server?
   (a) `net.createServer()` (b) `http.createServer((req, res) => {...})` (c) `express()` (d) `Fastify()`

2. What does graceful shutdown mean?
   (a) Call `process.exit(0)` immediately (b) Stop accepting new connections, finish in-flight requests, then exit (c) Send `SIGKILL` to self (d) Restart the process

3. How do you enable JSON body parsing in Express?
   (a) It's automatic (b) `app.use(express.json())` (c) `app.use(express.urlencoded())` (d) Not supported

4. When running inside a Docker container, which bind address makes the server reachable from outside?
   (a) `127.0.0.1` (b) `0.0.0.0` (c) `localhost` (d) They're all identical

5. Why validate environment configuration with Zod at boot?
   (a) Regex is too complex (b) Crash early with a clear error instead of failing on the first request that needs a missing variable (c) Zod is faster than `process.env` (d) dotenv handles validation automatically

**Short answer:**

6. Why is crashing early on a bad environment variable better than discovering it at runtime?

7. Give one concrete reason you might choose Fastify over Express for a new project.

_Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — A boot-time crash gives you an immediate, obvious error in your deploy pipeline; a runtime failure might not surface for hours or days, and when it does it's a 500 error to a real user. 7 — Fastify is async-native (no `asyncHandler` wrapper needed), has built-in request/response validation via JSON Schema or Zod, includes pino logging out of the box, and benchmarks 2-3× faster than Express._

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-servers — mini-project](mini-projects/01-servers-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP clients](../10-http-clients/01-why-http.md) — symmetric skills for debugging full stacks.
  - [Safe SQL from application code](../11-sql/04-crud.md) — parameters, transactions, and errors behind your routes.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.

## Chapter summary

- A server listens on a port, routes incoming requests to handlers, and sends responses — `node:http` is the foundation, frameworks (Express, Fastify) handle the ceremony.
- Validate configuration at boot with Zod so you crash with a clear error instead of serving broken responses.
- Graceful shutdown (stop accepting, drain in-flight, timeout, exit) prevents 502s during deploys.
- Structured logging with per-request IDs is the cheapest investment you can make in debuggability.

## Further reading

- [Fastify — Getting started](https://fastify.dev/docs/latest/Guides/Getting-Started/)
- [Express — Hello world](https://expressjs.com/en/starter/hello-world.html)
- [Pino — Node.js logger](https://getpino.io/)
- Next: [Routing](02-routing.md).
