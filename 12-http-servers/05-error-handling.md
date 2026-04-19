# Chapter 05 — Error Handling

> Every server fails sometimes. Great servers fail **predictably, loudly, and safely** — the caller knows what happened, the operator knows why, and no secrets leak.

## Learning objectives

By the end of this chapter you will be able to:

- Define a domain error hierarchy that maps cleanly to HTTP status codes.
- Build a central error middleware that handles every error path in one place.
- Log errors with enough context to debug — without leaking secrets to clients.
- Handle uncaught exceptions and unhandled rejections at the process level.
- Attach a request ID to every request for end-to-end traceability.

## Prerequisites & recap

- [JSON](04-json.md) — you can parse and validate request bodies.
- [Errors in JS](../08-js/09-errors.md) — you understand `try/catch`, `Error` classes, and promise rejections.

## The simple version

When something goes wrong in your server, two audiences need to hear about it. The *client* needs to know what happened in terms they can act on: "your email is invalid" (400), "you're not logged in" (401), "that item doesn't exist" (404). The *operator* (you, at 2 AM) needs to know everything: the stack trace, the request ID, the user ID, the SQL query that failed.

The trick is routing the right information to the right audience. Clients get a safe, structured JSON envelope. Logs get the full story. A single error middleware at the bottom of your middleware stack handles this split for every route, so you never duplicate the logic.

## In plain terms (newbie lane)

This chapter is really about **Error Handling**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Handler throws (or next(err))
       │
       ▼
  ┌──────────────────────────────────────┐
  │  Central Error Middleware            │
  │                                      │
  │  ZodError?  ──▶  400 + field details │
  │  HttpError? ──▶  err.status + code   │
  │  Unknown?   ──▶  500 "server_error"  │
  │                                      │
  │  ALWAYS: log full error server-side  │
  │  NEVER:  send stack trace to client  │
  └──────────────────────────────────────┘
       │                    │
       ▼                    ▼
  Client sees:        Operator sees:
  { error, message }  { err, stack, reqId, userId }
```
*Caption: The error middleware splits information between the client (safe) and the operator (detailed).*

## System diagram (Mermaid)

```mermaid
flowchart LR
  Client[HTTP_client] --> Listener[Server_listen]
  Listener --> Router[Router]
  Router --> Handler[Handler]
  Handler --> Response[Response]
```

*High-level HTTP server data flow for this chapter’s topic.*

## Concept deep-dive

### A domain error hierarchy

Define your error classes once and throw them from services. The central middleware maps them to HTTP responses:

```ts
class HttpError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message?: string,
    public readonly details?: unknown,
  ) {
    super(message ?? code);
  }
}

class NotFound extends HttpError {
  constructor(resource = "resource") {
    super(404, "not_found", `${resource} not found`);
  }
}

class BadRequest extends HttpError {
  constructor(message = "bad request", details?: unknown) {
    super(400, "bad_request", message, details);
  }
}

class Unauthorized extends HttpError {
  constructor() {
    super(401, "unauthorized", "authentication required");
  }
}

class Forbidden extends HttpError {
  constructor() {
    super(403, "forbidden", "insufficient permissions");
  }
}

class Conflict extends HttpError {
  constructor(message = "conflict") {
    super(409, "conflict", message);
  }
}
```

**Why a class hierarchy?** Because `instanceof` checks are cheap, readable, and let TypeScript narrow the type. The alternative — checking `err.status` on plain objects — loses type safety and is error-prone.

### Central error middleware

This is the single most important piece of error infrastructure in your server. Register it *after* all routes:

```ts
app.use((err: unknown, req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof z.ZodError) {
    return res.status(400).json({
      error: "validation_failed",
      details: err.issues.map((i) => ({
        path: i.path.join("."),
        message: i.message,
      })),
    });
  }

  if (err instanceof HttpError) {
    return res.status(err.status).json({
      error: err.code,
      message: err.message,
      ...(err.details ? { details: err.details } : {}),
    });
  }

  req.log?.error({ err }, "unhandled error");
  res.status(500).json({ error: "server_error" });
});
```

**Why centralize?** Because scattering `try/catch` blocks in every handler leads to inconsistent error shapes, forgotten logging, and leaked stack traces. One middleware, one shape, one logging strategy.

### What to log

Your structured logs should include:

- **Request ID** — set on the first middleware, echoed in `X-Request-Id` response header. This is the thread that connects client report → load balancer → server log → database slow query.
- **Method, path, status, duration** — the basics for any request.
- **Error class, message, stack** — for debugging.
- **User ID** (if authenticated) — never the password, token, or session.

**What NOT to log:** passwords, tokens, full request bodies (PII risk), credit card numbers, SSNs.

### Request-ID middleware

```ts
app.use((req: Request, res: Response, next: NextFunction) => {
  const id = (req.headers["x-request-id"] as string) ?? randomUUID();
  (req as any).id = id;
  res.setHeader("x-request-id", id);
  next();
});
```

If the client or load balancer sends an `X-Request-Id`, you propagate it. Otherwise, you generate one. Include it in every log line and error response so you can trace a single request through your entire system.

### The asyncHandler pattern

Express doesn't forward rejections from async handlers to error middleware. You need a wrapper:

```ts
const asyncHandler = (fn: Function) => (req: any, res: any, next: any) =>
  Promise.resolve(fn(req, res, next)).catch(next);
```

**Why is this necessary?** In Express 4, if an async handler throws (or its promise rejects), the error disappears — the client gets a hanging request. `asyncHandler` catches the rejection and calls `next(err)`, routing it to your error middleware. Express 5 and Fastify handle this natively.

### What clients see

| Status | Meaning | Client action |
|---|---|---|
| 4xx | Client's fault | Fix the request and retry |
| 5xx | Server's fault | Report the error; retry with backoff |

For 4xx errors, the `message` tells the client what to fix. For 5xx errors, the message is generic — details are logged server-side. Never expose internal error details to clients. A stack trace is a gift to attackers: it reveals framework versions, file paths, and sometimes database structure.

### Uncaught exceptions and unhandled rejections

If an error escapes all your `try/catch` and middleware, the process is in an unknown state. Log and crash:

```ts
process.on("unhandledRejection", (reason) => {
  logger.error({ reason }, "unhandledRejection");
  process.exit(1);
});

process.on("uncaughtException", (err) => {
  logger.error({ err }, "uncaughtException");
  process.exit(1);
});
```

**Why crash?** Because after an uncaught exception, you can't guarantee that your application state (in-memory caches, database connections, half-written transactions) is consistent. Let your orchestrator (Docker, Kubernetes, systemd) restart you into a clean state.

### Timeouts

A handler that waits forever on a stuck upstream will hold a connection, a request slot, and potentially a database connection open indefinitely. Set timeouts:

```ts
app.use((req: Request, res: Response, next: NextFunction) => {
  res.setTimeout(30_000, () => {
    res.status(504).json({ error: "gateway_timeout" });
  });
  next();
});
```

Combine with `AbortController` for in-flight HTTP requests to upstream services.

### Observability basics

Start simple and expand:

1. **Structured logs** (JSON via pino) — query by request ID, status, error code.
2. **Metrics** (RED: Rate, Errors, Duration) — expose via `/metrics` for Prometheus.
3. **Traces** (OpenTelemetry) — follow a request across multiple services.

Structured logs with request IDs will solve 90% of your debugging needs. Add metrics and traces when you have multiple services.

## Why these design choices

| Decision | Trade-off | When you'd pick differently |
|---|---|---|
| Class hierarchy for errors | Requires defining classes upfront | Very small API with 2 error types → use plain objects with `status` and `code` fields |
| Central error middleware | All errors go through one path | GraphQL → errors are part of the response body, not HTTP status codes |
| Crash on uncaught exception | Process restarts; brief downtime | Serverless (Lambda) → the runtime handles process lifecycle; just log |
| Request IDs | One more header to manage | Internal tool with no observability requirements → skip (but you'll regret it) |
| Log JSON, not strings | Harder to read in dev terminal | Use `pino-pretty` in development for human-readable output |

## Production-quality code

```ts
import express, { Request, Response, NextFunction } from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import pino from "pino";
import pinoHttp from "pino-http";

// --- Error hierarchy ---

class HttpError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message?: string,
    public readonly details?: unknown,
  ) {
    super(message ?? code);
    this.name = this.constructor.name;
  }
}

class NotFound extends HttpError {
  constructor(resource = "resource") {
    super(404, "not_found", `${resource} not found`);
  }
}
class BadRequest extends HttpError {
  constructor(msg = "bad request", details?: unknown) {
    super(400, "bad_request", msg, details);
  }
}
class Unauthorized extends HttpError {
  constructor() { super(401, "unauthorized", "authentication required"); }
}
class Forbidden extends HttpError {
  constructor() { super(403, "forbidden", "insufficient permissions"); }
}
class Conflict extends HttpError {
  constructor(msg = "conflict") { super(409, "conflict", msg); }
}

// --- Helpers ---

function asyncHandler(fn: (req: Request, res: Response) => Promise<void>) {
  return (req: Request, res: Response, next: NextFunction) =>
    Promise.resolve(fn(req, res)).catch(next);
}

// --- App ---

const logger = pino({ level: "info" });
const app = express();

app.use(pinoHttp({
  logger,
  genReqId: (req) => (req.headers["x-request-id"] as string) ?? randomUUID(),
}));

app.use(express.json({ limit: "1mb" }));

app.use((req: Request, res: Response, next: NextFunction) => {
  res.setTimeout(30_000, () => {
    res.status(504).json({ error: "gateway_timeout" });
  });
  next();
});

// --- Example route using typed errors ---

app.get("/users/:id", asyncHandler(async (req, res) => {
  const user = await findUserById(req.params.id);
  res.json({ data: user });
}));

async function findUserById(id: string) {
  const user = null; // simulate lookup
  if (!user) throw new NotFound(`user ${id}`);
  return user;
}

// --- 404 catch-all ---

app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: "not_found" });
});

// --- Central error middleware ---

app.use((err: unknown, req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof z.ZodError) {
    res.status(400).json({
      error: "validation_failed",
      details: err.issues.map((i) => ({
        path: i.path.join("."),
        message: i.message,
      })),
    });
    return;
  }

  if (err instanceof HttpError) {
    res.status(err.status).json({
      error: err.code,
      message: err.message,
      ...(err.details ? { details: err.details } : {}),
    });
    return;
  }

  req.log.error({ err }, "unhandled error");
  res.status(500).json({ error: "server_error" });
});

// --- Process-level safety net ---

process.on("unhandledRejection", (reason) => {
  logger.error({ reason }, "unhandledRejection");
  process.exit(1);
});

process.on("uncaughtException", (err) => {
  logger.error({ err }, "uncaughtException");
  process.exit(1);
});

export { app, HttpError, NotFound, BadRequest, Unauthorized, Forbidden, Conflict };
```

## Security notes

- **Never expose stack traces** — they reveal framework versions, file paths, database types, and sometimes query structures. Log them; don't send them.
- **Generic 5xx messages** — if the server breaks, the client sees `{ "error": "server_error" }`. No hints about what went wrong internally.
- **Uniform error shape** — attackers probe different endpoints looking for inconsistent error handling that leaks information. A central middleware ensures every endpoint behaves identically.
- **Don't reveal existence via error codes** — returning "user not found" vs. "wrong password" tells an attacker which emails are registered. Return "invalid credentials" for both (see Chapter 07).
- **Rate limit error-triggering endpoints** — if an endpoint returns detailed validation errors, attackers can use it to enumerate valid field values. Rate limit accordingly.

## Performance notes

- **Error middleware is free when no error occurs** — Express only calls the 4-argument middleware when `next(err)` is called. There's no per-request overhead for happy paths.
- **`instanceof` checks are fast** — a chain of 5 `instanceof` checks in the error middleware takes nanoseconds. Don't optimize this.
- **Logging is the bottleneck** — `pino` is the fastest Node.js logger, but writing to stdout still has I/O cost. In very high-throughput services, consider sampling error logs or using async transport.
- **Request timeouts** prevent resource leaks — a stuck upstream shouldn't hold a connection open indefinitely. Set `res.setTimeout()` or use a reverse proxy timeout.
- **Crash-restart is fast** — a Node process restarts in < 1 second. The brief downtime from crashing on uncaught exceptions is far less costly than running in a corrupted state.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Thrown error in an async handler silently hangs the request (no response, no log) | Express 4 doesn't catch async rejections | Wrap all async handlers with `asyncHandler` that calls `.catch(next)` |
| Client receives a full Node.js stack trace in the response body | Error middleware doesn't strip internal details, or the default Express error handler kicks in | Ensure your error middleware handles *all* error types and never passes stack traces to `res.json()` |
| Every handler has its own `try/catch` returning slightly different error shapes | No central error middleware; error handling duplicated per route | Add a single error middleware at the end; remove per-handler `try/catch` blocks |
| Logs say "Error: undefined" with no useful context | Error was thrown without a message, or logging `err.message` instead of the full error object | Throw errors with descriptive messages; log `{ err }` (pino serializes the full error including stack) |
| An intermittent bug is impossible to trace across services | No request IDs | Add request-ID middleware; propagate the ID to upstream HTTP calls and database queries |
| Server runs in a corrupted state after an unhandled rejection | No `unhandledRejection` handler — the process continues despite unknown state | Add process-level handlers that log and exit; let the orchestrator restart |

## Practice

**Warm-up.** Define a `NotFound` error class and throw it from a service function. Verify the client receives a 404 JSON response.

<details><summary>Solution</summary>

```ts
class NotFound extends Error {
  readonly status = 404;
  readonly code = "not_found";
  constructor(resource: string) {
    super(`${resource} not found`);
  }
}

async function getUser(id: string) {
  const user = await storage.findById(id);
  if (!user) throw new NotFound(`user ${id}`);
  return user;
}
```

The central error middleware catches this and returns `{ error: "not_found", message: "user 42 not found" }` with status 404.

</details>

**Standard.** Add a central error middleware that handles `ZodError` (400), `HttpError` (dynamic status), and unknown errors (500). Test all three paths.

<details><summary>Solution</summary>

```ts
app.use((err: unknown, req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof z.ZodError) {
    return res.status(400).json({
      error: "validation_failed",
      details: err.issues.map(i => ({ path: i.path.join("."), message: i.message })),
    });
  }
  if (err instanceof HttpError) {
    return res.status(err.status).json({ error: err.code, message: err.message });
  }
  req.log?.error({ err }, "unhandled");
  res.status(500).json({ error: "server_error" });
});
```

</details>

**Bug hunt.** A developer writes `app.get("/test", async (req, res) => { throw new Error("boom"); })` but the error never reaches the error middleware. Why?

<details><summary>Solution</summary>

Express 4 doesn't handle promise rejections from async route handlers. The thrown error becomes an unhandled rejection — it never reaches `next(err)`. Fix: wrap with `asyncHandler`:

```ts
app.get("/test", asyncHandler(async (req, res) => {
  throw new Error("boom");
}));
```

Now the `.catch(next)` inside `asyncHandler` routes the error to the middleware.

</details>

**Stretch.** Add request-ID middleware that reads `X-Request-Id` from the incoming request (or generates a UUID), attaches it to the request object, and echoes it in the response header. Verify the ID appears in error logs.

<details><summary>Solution</summary>

```ts
app.use((req: Request, res: Response, next: NextFunction) => {
  const id = (req.headers["x-request-id"] as string) ?? randomUUID();
  (req as any).id = id;
  res.setHeader("x-request-id", id);
  next();
});
```

With `pino-http`, the request ID is automatically included in logs when you use `genReqId`.

</details>

**Stretch++.** Add a `Retry-After` header to 429 (Too Many Requests) responses. Return the number of seconds until the rate limit window resets.

<details><summary>Solution</summary>

```ts
class TooManyRequests extends HttpError {
  constructor(public readonly retryAfterSeconds: number) {
    super(429, "too_many_requests", "rate limit exceeded");
  }
}

// In error middleware:
if (err instanceof TooManyRequests) {
  return res
    .set("Retry-After", String(err.retryAfterSeconds))
    .status(429)
    .json({ error: err.code, message: err.message });
}
```

</details>

## Quiz

1. HTTP 4xx status codes indicate:
   (a) Success  (b) Redirect  (c) Client error  (d) Server error

2. Where should the central error middleware be registered in Express?
   (a) Before all routes  (b) After all routes — signature is `(err, req, res, next)`  (c) Inside each route  (d) Express doesn't support error middleware

3. Should stack traces be included in API error responses?
   (a) Yes, for debugging  (b) No — they're a security risk; log them server-side only  (c) Only in production  (d) Express includes them by default and that's fine

4. What should happen on an `uncaughtException`?
   (a) Ignore it  (b) Log the error and exit; let the orchestrator restart  (c) Continue running  (d) Throw it again

5. What is a request ID used for?
   (a) Random number per log line  (b) A per-request identifier echoed in responses for end-to-end tracing  (c) A timestamp  (d) It's unnecessary overhead

**Short answer:**

6. Why is `throw new NotFound()` in a service better than `return res.status(404).json(...)` in a handler?

7. Name one benefit of structured logging (JSON) over `console.log` strings.

*Answers: 1-c, 2-b, 3-b, 4-b, 5-b. 6 — Throwing from the service keeps the service independent of HTTP. The service doesn't know about `res`, status codes, or response formats. A central middleware handles the HTTP mapping, ensuring consistency across all endpoints. You can also reuse the service from a CLI, a worker, or a different transport without changing it. 7 — Structured JSON logs let your log aggregator (Datadog, Grafana, ELK) index individual fields, so you can filter by request ID, status code, user ID, or error class. String logs require regex parsing and break on format changes.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-error-handling — mini-project](mini-projects/05-error-handling-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP clients](../10-http-clients/01-why-http.md) — symmetric skills for debugging full stacks.
  - [Safe SQL from application code](../11-sql/04-crud.md) — parameters, transactions, and errors behind your routes.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Define a typed error hierarchy (`HttpError`, `NotFound`, `BadRequest`, etc.) and throw from services — a central middleware maps them to HTTP responses consistently.
- Log the full error (stack, context, request ID) server-side; send only safe, structured JSON to clients.
- Use `asyncHandler` in Express 4 to route async rejections to the error middleware — otherwise thrown errors silently hang.
- Request IDs and structured logs are the cheapest debugging investment you'll ever make — they turn a 3-hour investigation into a 3-minute log search.

## Further reading

- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- Beyer et al., *Site Reliability Engineering* (O'Reilly) — Chapter 6: Monitoring Distributed Systems
- [Pino — Node.js logger](https://getpino.io/)
- Next: [Storage](06-storage.md).
