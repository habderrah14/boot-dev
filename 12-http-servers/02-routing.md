# Chapter 02 — Routing

> Routing matches an incoming request to the code that should handle it. Keep it boring, predictable, and close to the URL design from [Module 10 ch. 08](../10-http-clients/08-paths.md).

## Learning objectives

By the end of this chapter you will be able to:

- Declare routes with path parameters, query parameters, and HTTP methods.
- Compose routers and mount them under a versioned prefix.
- Serve static files in development.
- Return proper 404 and 405 responses.
- Explain why route order matters and how overlapping patterns cause silent bugs.

## Prerequisites & recap

- [Servers](01-servers.md) — you can start a server and handle a single request.
- [Paths & URLs](../10-http-clients/08-paths.md) — you understand the anatomy of a URL.

## The simple version

Routing is the switchboard operator of your server. A request arrives with a method (`GET`, `POST`, etc.) and a path (`/v1/users/42`). The router scans its list of registered patterns top-to-bottom, finds the first match, and hands the request to that handler. If nothing matches, you return 404. If the path matches but the method doesn't, you return 405.

That's it. Routing is pattern matching. The complexity comes from organizing hundreds of routes so they stay readable, versioned, and conflict-free.

## In plain terms (newbie lane)

This chapter is really about **Routing**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  GET /v1/users/42
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │  Router table (scanned top → bottom)        │
  │                                             │
  │  GET  /v1/users      → listUsers            │
  │  GET  /v1/users/:id  → getUser      ← MATCH│
  │  POST /v1/users      → createUser           │
  │  *    *               → 404 handler         │
  └─────────────────────────────────────────────┘
       │
       ▼
  getUser(req, res)  ──▶  { id: 42, name: "Ada" }
```
*Caption: The router scans registered patterns in order and dispatches to the first match.*

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

### Basic routes in Express

Express routes combine an HTTP method and a path pattern:

```ts
app.get("/users", listUsers);
app.get("/users/:id", getUser);
app.post("/users", createUser);
app.patch("/users/:id", updateUser);
app.delete("/users/:id", deleteUser);
```

This is the classic CRUD pattern. Each line maps one method+path combination to one handler function. **Why one handler per route?** Because it keeps each function small, testable, and replaceable. A single mega-handler with a `switch` on method is harder to read and impossible to compose with middleware.

### Path parameters

Path parameters capture dynamic segments of the URL:

```ts
app.get("/users/:id", (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id < 1) {
    return res.status(400).json({ error: "invalid id" });
  }
  // ...
});
```

**Why validate path params?** Because `req.params.id` is always a string — and it comes from the client. A path like `/users/DROP TABLE` is perfectly valid HTTP. You must parse and validate before using it in any query or logic.

### Query parameters

Query parameters are key-value pairs after the `?` in the URL:

```ts
app.get("/posts", (req, res) => {
  const limit = Math.min(Number(req.query.limit ?? 20), 100);
  const offset = Number(req.query.offset ?? 0);
  // ...
});
```

Always validate and clamp. A client sending `?limit=999999` could trigger a massive database query. Cap to a sensible maximum.

### Sub-routers — grouping related routes

As your API grows, mounting everything on `app` directly becomes unwieldy. Sub-routers let you group and namespace:

```ts
const userRouter = express.Router();
userRouter.get("/", listUsers);
userRouter.get("/:id", getUser);
userRouter.post("/", createUser);
userRouter.patch("/:id", updateUser);
userRouter.delete("/:id", deleteUser);

app.use("/v1/users", userRouter);
```

**Why sub-routers?** Three reasons: (1) you can apply middleware to a group (e.g., authentication on all `/v1/users` routes), (2) each router lives in its own file, and (3) versioning becomes a single mount-point change.

### API versioning via path

Prefix routes with `/v1`, `/v2`, etc. When the shape of an endpoint changes in a breaking way, add a new version. Keep the old one running until clients migrate:

```ts
app.use("/v1", v1Router);
app.use("/v2", v2Router);
```

**Why not version via header?** Header versioning (e.g., `Accept: application/vnd.myapp.v2+json`) is harder to test with a browser, harder to cache, and harder for clients to discover. Path versioning is visible, cacheable, and debuggable.

### Static files

In development, serve static assets directly:

```ts
app.use("/static", express.static("public"));
```

In production, use a CDN (see [Module 13 ch. 07](../13-file-cdn/07-cdns.md)). Serving static files through Node wastes event-loop time on I/O that nginx or a CDN handles far more efficiently.

### 404 — nothing matched

Express evaluates middleware in registration order. A catch-all at the end handles unmatched requests:

```ts
app.use((_req, res) => {
  res.status(404).json({ error: "not_found" });
});
```

**Why not let Express's default 404 through?** Because Express's default returns an HTML page, and your JSON API clients will choke on it.

### 405 — wrong method on a known path

If `GET /users/42` exists but `PUT /users/42` doesn't, returning 404 is misleading. The resource exists; the method is unsupported. Use 405:

```ts
app.route("/users/:id")
  .get(getUser)
  .patch(updateUser)
  .delete(deleteUser)
  .all((_req, res) => res.status(405).json({ error: "method_not_allowed" }));
```

### Route order matters

Express matches top-to-bottom and stops at the first match. If you register a catch-all before a specific route, the specific route never fires:

```ts
app.get("/users/:id", getUser);
app.get("/users/me", getMe);   // NEVER REACHED — :id matches "me"
```

Fix: put literal paths before parameterized ones, or validate the param inside the handler.

### OpenAPI-first routing

Many teams define routes in an OpenAPI spec first, then generate types and routers. This is powerful when the API is the public contract, because clients can generate SDKs from the same spec. The trade-off is that you now maintain a YAML file alongside your code.

## Why these design choices

| Decision | Trade-off | When you'd pick differently |
|---|---|---|
| Path-based versioning (`/v1/`) | Clutters URLs slightly | Strongly typed internal API with header negotiation → version via `Accept` header |
| Sub-routers per resource | More files, more wiring | Tiny API with 3–4 routes → mount directly on `app` |
| 405 for wrong method | Extra code per route group | You don't care about HTTP correctness → skip (but clients will be confused) |
| Static files via Express | Easy in dev | Production → always use a CDN or nginx |
| Top-to-bottom matching | Simple, predictable | Framework with ranked/weighted matching (Fastify, Hono) → less order-sensitive |

## Production-quality code

```ts
import express, { Request, Response, Router } from "express";

function asyncHandler(
  fn: (req: Request, res: Response) => Promise<void>,
) {
  return (req: Request, res: Response, next: express.NextFunction) =>
    Promise.resolve(fn(req, res)).catch(next);
}

interface Book {
  id: number;
  title: string;
  author: string;
}

let nextId = 1;
const books = new Map<number, Book>();

const bookRouter = Router();

bookRouter.get("/", (_req: Request, res: Response) => {
  const limit = Math.min(Number(_req.query.limit ?? 20), 100);
  const all = [...books.values()].slice(0, limit);
  res.json({ data: all });
});

bookRouter.get("/:id", asyncHandler(async (req: Request, res: Response) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id < 1) {
    res.status(400).json({ error: "invalid_id" });
    return;
  }
  const book = books.get(id);
  if (!book) {
    res.status(404).json({ error: "not_found" });
    return;
  }
  res.json({ data: book });
}));

bookRouter.post("/", asyncHandler(async (req: Request, res: Response) => {
  const { title, author } = req.body;
  if (!title || !author) {
    res.status(400).json({ error: "title and author required" });
    return;
  }
  const book: Book = { id: nextId++, title, author };
  books.set(book.id, book);
  res.status(201).json({ data: book });
}));

bookRouter.route("/:id")
  .patch(asyncHandler(async (req: Request, res: Response) => {
    const id = Number(req.params.id);
    const book = books.get(id);
    if (!book) { res.status(404).json({ error: "not_found" }); return; }
    Object.assign(book, req.body);
    res.json({ data: book });
  }))
  .delete(asyncHandler(async (req: Request, res: Response) => {
    const id = Number(req.params.id);
    if (!books.delete(id)) { res.status(404).json({ error: "not_found" }); return; }
    res.status(204).end();
  }))
  .all((_req: Request, res: Response) => {
    res.status(405).json({ error: "method_not_allowed" });
  });

const app = express();
app.use(express.json());
app.use("/v1/books", bookRouter);

app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: "not_found" });
});

export { app };
```

## Security notes

- **Path traversal** — if you serve static files, `express.static` handles `..` traversal for you. If you build your own file-serving logic, sanitize paths rigorously or you'll serve `/etc/passwd`.
- **Open redirect** — never redirect to a user-supplied URL without validating against an allowlist of domains.
- **Parameter pollution** — Express parses `?sort=asc&sort=desc` into an array. If your code expects a string, it breaks. Validate types.
- **Regex DoS (ReDoS)** — if you use custom regex for route matching, a crafted path can hang the event loop. Stick to framework-provided pattern matching.

## Performance notes

- **Router lookup is O(n)** in Express — it linearly scans registered routes. For most apps (< 200 routes) this is negligible. Fastify uses a radix tree (O(log n)) which matters if you have thousands of routes.
- **Sub-router overhead** — each `app.use(prefix, router)` adds a layer. The cost is tiny but measurable at extreme scale. Don't over-nest.
- **Static files** — every static file request ties up the Node event loop. In production, offload to nginx or a CDN.
- **Query parsing** — Express parses the query string on every request via `qs`. If you don't use nested query objects, switch to the faster built-in `querystring` via `app.set("query parser", "simple")`.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| A route handler never runs even though the URL looks correct | A more general route registered above it matches first (e.g., `/:id` catches `"me"`) | Put literal paths before parameterized paths, or add validation inside the parameterized handler |
| `GET /users` works but `GET /users/` returns 404 | Trailing slash inconsistency — Express treats them as different paths by default | Use `app.enable("strict routing")` intentionally, or normalize trailing slashes with middleware |
| Two identical route registrations — only the first runs | Express stops at the first match; the second is silently ignored | Search for duplicate registrations; use a linter or OpenAPI spec to catch collisions |
| 404 handler fires for every request | The catch-all middleware was registered before the routes | Always register your 404 handler *after* all routes |
| `req.params.id` is `"undefined"` (the string) | Route pattern has `:id` but the handler reads `req.query.id` instead | Use `req.params` for path segments, `req.query` for `?key=value` pairs |

## Practice

**Warm-up.** Add `GET /` returning plain text `"hello"` to an Express app.

<details><summary>Solution</summary>

```ts
app.get("/", (_req, res) => {
  res.type("text/plain").send("hello");
});
```

</details>

**Standard.** Implement full CRUD routes for a `Book` resource (`GET /`, `GET /:id`, `POST /`, `PATCH /:id`, `DELETE /:id`) with basic validation.

<details><summary>Solution</summary>

See the production-quality code section above for a complete example. Key points: validate `id` is a positive integer, return 404 when the book doesn't exist, return 201 on create, 204 on delete.

</details>

**Bug hunt.** You register `app.get("/users", handlerA); app.get("/users", handlerB);`. Only `handlerA` ever runs. Why?

<details><summary>Solution</summary>

Express matches top-to-bottom. The first matching route wins and sends a response. `handlerB` is never reached because `handlerA` already matched the same method+path. If you need both to run, call `next()` in `handlerA` — but usually this means you should merge the logic or use middleware.

</details>

**Stretch.** Group all v1 routes under `/v1` using a sub-router. Add a second version (`/v2`) of one endpoint that returns a different response shape.

<details><summary>Solution</summary>

```ts
const v1 = express.Router();
v1.get("/books", listBooksV1);
v1.get("/books/:id", getBookV1);

const v2 = express.Router();
v2.get("/books", listBooksV2);

app.use("/v1", v1);
app.use("/v2", v2);
```

</details>

**Stretch++.** Return 405 `Method Not Allowed` (with an `Allow` header listing valid methods) when a known path is hit with an unsupported method.

<details><summary>Solution</summary>

```ts
bookRouter.route("/:id")
  .get(getBook)
  .patch(updateBook)
  .delete(deleteBook)
  .all((_req, res) => {
    res.set("Allow", "GET, PATCH, DELETE");
    res.status(405).json({ error: "method_not_allowed" });
  });
```

The `Allow` header tells the client which methods *are* supported, per RFC 7231.

</details>

## Quiz

1. How are path parameters defined in Express?
   (a) `/users?id=X`  (b) `/users/:id`  (c) Via the fragment `#id`  (d) Via a header

2. How do you group related routes in Express?
   (a) `Router.use()`  (b) Mount a sub-router under a prefix with `app.use(prefix, router)`  (c) Nested classes  (d) Separate `app` instances

3. Where should the 404 catch-all handler be registered?
   (a) Before all routes  (b) After all routes, at the end of the middleware chain  (c) Inside each route  (d) It's not needed

4. What's the correct status code for "this path exists but this method isn't supported"?
   (a) 400  (b) 401  (c) 404  (d) 405

5. How does Express serve static files in development?
   (a) `express.static(dir)`  (b) Manual `app.get()` per file  (c) Stream-only mode  (d) nginx is required

**Short answer:**

6. Why should you always validate path parameters before using them?

7. Why is path-based API versioning (`/v1/`, `/v2/`) preferred over header-based versioning for most public APIs?

*Answers: 1-b, 2-b, 3-b, 4-d, 5-a. 6 — Path parameters come from untrusted client input. Without validation, values like non-numeric IDs, SQL fragments, or special characters can cause crashes, injection, or data corruption downstream. 7 — Path-based versions are visible in URLs, easy to test in a browser, cacheable by CDNs, and discoverable without special tooling. Header-based versioning requires clients to set custom headers, which many tools (browsers, cURL one-liners) don't do by default.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-routing — mini-project](mini-projects/02-routing-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP clients](../10-http-clients/01-why-http.md) — symmetric skills for debugging full stacks.
  - [Safe SQL from application code](../11-sql/04-crud.md) — parameters, transactions, and errors behind your routes.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Routes map a method + path to a handler function — Express scans top-to-bottom, first match wins.
- Sub-routers group related routes under a prefix, enabling clean versioning and per-group middleware.
- Always handle 404 (no match) and 405 (wrong method) explicitly — default HTML responses confuse API clients.
- Validate every path and query parameter — they're untrusted input, just like request bodies.

## Further reading

- [Express — Routing guide](https://expressjs.com/en/guide/routing.html)
- [Fastify — Routes documentation](https://fastify.dev/docs/latest/Reference/Routes/)
- Next: [Architecture](03-architecture.md).
