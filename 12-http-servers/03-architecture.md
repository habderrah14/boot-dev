# Chapter 03 — Architecture

> How you split a server's code determines how easy it is to change. Layer it so each piece has one job and one reason to change.

## Learning objectives

By the end of this chapter you will be able to:

- Separate routing, business logic, and storage into distinct layers.
- Apply the "hexagonal" / "ports-and-adapters" pattern pragmatically.
- Keep HTTP handlers thin so they parse, delegate, and respond — nothing more.
- Organize files so a new engineer can find things within minutes.
- Wire dependencies at startup for clean testability.

## Prerequisites & recap

- [Routing](02-routing.md) — you can declare and group routes.
- [Servers](01-servers.md) — you can start and shut down a server.

## The simple version

Imagine a restaurant. The waiter (HTTP handler) takes your order and brings your food, but never cooks. The chef (service/domain layer) cooks according to recipes and business rules, but never talks to guests. The pantry (storage layer) provides ingredients, but doesn't know what dish is being made. Each role has one job. If you want to swap the pantry for a different supplier, the chef doesn't change. If you want to serve via a food truck instead of a dining room, the chef still doesn't change.

In server code, this translates to three layers: transport (handlers), service (business logic), and storage (database/external APIs). The service defines *interfaces* for what it needs from storage, and the actual database implementation plugs in at startup. This is the core of "ports and adapters."

## In plain terms (newbie lane)

This chapter is really about **Architecture**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  HTTP request
       │
       ▼
  ┌──────────┐    ┌───────────┐    ┌─────────────────┐
  │ Handler   │───▶│  Service   │───▶│  Storage Port    │
  │ (parse,   │    │ (business  │    │  (interface)      │
  │  respond) │    │  rules)    │    └────────┬──────────┘
  └──────────┘    └───────────┘             │
                                    ┌───────┴────────┐
                                    │                │
                               ┌────▼─────┐   ┌─────▼──────┐
                               │ Postgres │   │ In-memory   │
                               │ adapter  │   │ (for tests) │
                               └──────────┘   └────────────┘
```
*Caption: The handler knows HTTP. The service knows business rules. Storage is hidden behind an interface that can be swapped.*

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

### The three layers

1. **Transport (HTTP handler)** — parses the request (params, body), validates input with Zod, calls a service method, and writes the HTTP response. No business logic here.
2. **Service / domain** — pure-ish business logic. "Create a user", "mark order paid", "check inventory." It knows nothing about HTTP, Express, or status codes.
3. **Storage / adapter** — talks to PostgreSQL, Redis, an external API, a queue. It satisfies an *interface* defined by the service layer.

### Why this split?

- **Handlers become boring.** They follow the same pattern every time: parse → call service → respond. Boring is good — boring means no surprises.
- **Services are testable without HTTP or a database.** You pass in a fake storage implementation and assert on the service's output. No supertest, no Docker, no network calls.
- **Adapters are swappable.** Run Postgres in production and an in-memory Map in unit tests. Swap to MySQL without touching business logic.

### Ports and adapters in practice

The service defines what it *needs* — a "port":

```ts
export interface UserStorage {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  create(u: Omit<User, "id">): Promise<User>;
}
```

The adapter *implements* the port:

```ts
export function makePostgresUserStorage(pool: pg.Pool): UserStorage {
  return {
    async findById(id) {
      const r = await pool.query(
        "SELECT id, email, name FROM users WHERE id = $1", [id],
      );
      return r.rows[0] ?? null;
    },
    // ...
  };
}
```

The service receives its dependencies via constructor injection:

```ts
export function makeUserService(deps: { storage: UserStorage; log: Logger }) {
  return {
    async register(input: CreateUserInput) {
      const existing = await deps.storage.findByEmail(input.email);
      if (existing) throw new Conflict("email already registered");
      return deps.storage.create(input);
    },
  };
}
```

### Wiring at startup

Everything connects in one place — your composition root:

```ts
const pool = new pg.Pool({ connectionString: env.DATABASE_URL });
const storage = makePostgresUserStorage(pool);
const userService = makeUserService({ storage, log: logger });

app.post("/v1/users", asyncHandler(async (req, res) => {
  const input = CreateUser.parse(req.body);
  const user = await userService.register(input);
  res.status(201).json({ data: user });
}));
```

**Why wire in one place?** Because you can see every dependency at a glance. In tests, you swap `makePostgresUserStorage` for `makeMemoryUserStorage` and everything else stays identical.

### The handler template

Every handler follows the same shape:

```ts
export const create = asyncHandler(async (req, res) => {
  const input = CreateThing.parse(req.body);     // 1. Parse + validate
  const result = await svc.create(input);         // 2. Call service
  res.status(201).json({ data: result });          // 3. Respond
});
```

If your handler does more than parse → delegate → respond, you're leaking business logic into the transport layer.

### The asyncHandler helper

Express doesn't forward errors from async handlers to error middleware unless you `.catch(next)`:

```ts
const asyncHandler = (fn: Function) => (req: any, res: any, next: any) =>
  Promise.resolve(fn(req, res, next)).catch(next);
```

Without this, thrown errors in async handlers silently hang the request. Fastify doesn't need this — it handles async natively.

### Folder layout

Two common approaches:

**By layer** (recommended for most projects):

```
src/
  config/         # env, logger
  routes/         # HTTP endpoints — no business logic
    users.ts
    orders.ts
  services/       # business rules
    users.ts
    orders.ts
  storage/        # interfaces + implementations
    users.ts
    orders.ts
  schemas/        # Zod schemas (shared by routes and services)
  types.ts
  server.ts       # Express app setup
  main.ts         # composition root + listen
```

**By feature** (good for large teams with domain ownership):

```
src/
  users/
    route.ts
    service.ts
    storage.ts
    schema.ts
  orders/
    route.ts
    service.ts
    storage.ts
    schema.ts
  server.ts
  main.ts
```

Pick one and be consistent. Mixing both is worse than either.

## Why these design choices

| Decision | Trade-off | When you'd pick differently |
|---|---|---|
| Three layers (handler → service → storage) | More files, more ceremony for tiny apps | Prototype or script with 2 endpoints → put everything in one file |
| Service owns the storage interface (ports-and-adapters) | Indirection cost; more types to maintain | You'll never swap the database → skip the interface, depend on the implementation directly |
| Constructor/factory injection | Slightly more boilerplate than importing singletons | You're OK with singletons and don't test in isolation → import directly |
| By-layer folder layout | Spreads one feature across multiple directories | Large team with domain ownership → by-feature layout keeps related code together |
| `asyncHandler` wrapper | Extra wrapping on every route | Using Fastify → not needed; using Express 5+ → also not needed (native async support) |

## Production-quality code

```ts
import express, { Request, Response, NextFunction, Router } from "express";
import { z } from "zod";

// --- Schemas ---

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});
type CreateUserInput = z.infer<typeof CreateUserSchema>;

// --- Types ---

interface User {
  id: string;
  email: string;
  name: string;
}

// --- Storage port ---

interface UserStorage {
  findById(id: string): Promise<User | null>;
  create(input: CreateUserInput): Promise<User>;
  list(): Promise<User[]>;
}

// --- In-memory adapter (for tests / demo) ---

function makeMemoryUserStorage(): UserStorage {
  const store = new Map<string, User>();
  let seq = 0;
  return {
    async findById(id) { return store.get(id) ?? null; },
    async create(input) {
      const user: User = { id: String(++seq), ...input };
      store.set(user.id, user);
      return user;
    },
    async list() { return [...store.values()]; },
  };
}

// --- Service ---

function makeUserService(deps: { storage: UserStorage }) {
  return {
    async register(input: CreateUserInput): Promise<User> {
      return deps.storage.create(input);
    },
    async getById(id: string): Promise<User> {
      const user = await deps.storage.findById(id);
      if (!user) throw new NotFoundError(`user ${id}`);
      return user;
    },
    async list(): Promise<User[]> {
      return deps.storage.list();
    },
  };
}

// --- Error types ---

class NotFoundError extends Error {
  readonly status = 404;
  readonly code = "not_found";
}

// --- Async handler ---

function asyncHandler(fn: (req: Request, res: Response) => Promise<void>) {
  return (req: Request, res: Response, next: NextFunction) =>
    Promise.resolve(fn(req, res)).catch(next);
}

// --- Routes ---

function makeUserRouter(svc: ReturnType<typeof makeUserService>): Router {
  const router = Router();

  router.get("/", asyncHandler(async (_req, res) => {
    const users = await svc.list();
    res.json({ data: users });
  }));

  router.get("/:id", asyncHandler(async (req, res) => {
    const user = await svc.getById(req.params.id);
    res.json({ data: user });
  }));

  router.post("/", asyncHandler(async (req, res) => {
    const input = CreateUserSchema.parse(req.body);
    const user = await svc.register(input);
    res.status(201).json({ data: user });
  }));

  return router;
}

// --- Composition root ---

function composeApp() {
  const app = express();
  app.use(express.json());

  const storage = makeMemoryUserStorage();
  const userService = makeUserService({ storage });
  const userRouter = makeUserRouter(userService);

  app.use("/v1/users", userRouter);

  app.use((_req: Request, res: Response) => {
    res.status(404).json({ error: "not_found" });
  });

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    if (err.status && err.code) {
      res.status(err.status).json({ error: err.code, message: err.message });
      return;
    }
    if (err instanceof z.ZodError) {
      res.status(400).json({ error: "validation_failed", details: err.issues });
      return;
    }
    res.status(500).json({ error: "server_error" });
  });

  return app;
}

export { composeApp, makeUserService, makeMemoryUserStorage };
```

## Security notes

- **Layer enforcement prevents injection** — when handlers never touch the database directly, there's no temptation to concatenate SQL strings. All queries go through the storage layer, which uses parameterized queries.
- **Don't expose internal errors** — the error middleware should strip stack traces before sending to clients. Log them server-side.
- **Dependency injection ≠ insecurity** — injecting dependencies doesn't weaken security, but be careful that test adapters can't accidentally be used in production. Gate on `NODE_ENV` or compile-time checks.
- **Avoid circular imports** — they can cause partially initialized modules, leading to undefined values where you expect classes or functions. This can bypass validation or auth checks.

## Performance notes

- **Thin handlers** mean each request spends minimal time in the HTTP layer. The real work (database, computation) is in the service and storage layers where you can optimize independently.
- **Factory injection has near-zero runtime cost** — you create service objects once at startup. There's no per-request overhead compared to importing singletons.
- **In-memory adapters** make tests fast — no Docker startup, no network latency. Your test suite runs in seconds, not minutes.
- **Avoid deep call stacks** — three layers is plenty. Adding "repository," "use case," "presenter," and "mapper" layers buys you nothing in most Node apps and adds stack depth + complexity.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Business logic (validation, authorization, calculations) scattered across route handlers | The service layer was skipped — handlers talk to storage directly | Extract logic into a service. Handlers should only parse, delegate, and respond |
| Tests require a running database | Route handlers import `pg` directly | Introduce a storage interface; inject an in-memory implementation in tests |
| `utils.ts` grows to 500+ lines and everything imports from it | Shared code has no clear owner | Split into focused modules: `errors.ts`, `schemas.ts`, `middleware.ts` |
| Circular import causes `TypeError: X is not a function` | Layer A imports from layer B which imports from layer A | Follow a strict dependency direction: routes → services → storage. Never go backwards |
| Changing one feature breaks a seemingly unrelated feature | Shared mutable state (global variables, singletons with state) | Use dependency injection; each service instance gets its own dependencies |

## Practice

**Warm-up.** Take an existing handler that queries the database directly. Extract the query into a service function.

<details><summary>Solution</summary>

Before:
```ts
app.get("/users/:id", async (req, res) => {
  const r = await pool.query("SELECT * FROM users WHERE id = $1", [req.params.id]);
  if (!r.rows[0]) return res.status(404).json({ error: "not found" });
  res.json(r.rows[0]);
});
```

After:
```ts
// service
async function getUserById(id: string): Promise<User> {
  const user = await storage.findById(id);
  if (!user) throw new NotFound(`user ${id}`);
  return user;
}

// handler
app.get("/users/:id", asyncHandler(async (req, res) => {
  const user = await getUserById(req.params.id);
  res.json({ data: user });
}));
```

</details>

**Standard.** Define a `UserStorage` interface with `findById`, `create`, and `list`. Implement both a Postgres adapter and an in-memory adapter. Write a test using the in-memory version.

<details><summary>Solution</summary>

```ts
interface UserStorage {
  findById(id: string): Promise<User | null>;
  create(input: CreateUserInput): Promise<User>;
  list(): Promise<User[]>;
}

function makeMemoryUserStorage(): UserStorage {
  const store = new Map<string, User>();
  let seq = 0;
  return {
    async findById(id) { return store.get(id) ?? null; },
    async create(input) {
      const u: User = { id: String(++seq), ...input };
      store.set(u.id, u);
      return u;
    },
    async list() { return [...store.values()]; },
  };
}

// Test
const storage = makeMemoryUserStorage();
const svc = makeUserService({ storage });
const user = await svc.register({ email: "a@b.c", name: "Ada" });
assert(user.id === "1");
assert(user.email === "a@b.c");
```

</details>

**Bug hunt.** A developer imports `pg` directly in a handler file. Why is this a problem even if the queries are correct?

<details><summary>Solution</summary>

Direct `pg` imports in handlers create a tight coupling between the HTTP layer and the database. You can't test the handler without a running Postgres instance. You also can't reuse the business logic from a CLI tool, a worker, or a different transport. The fix is to depend on a storage interface and inject the implementation.

</details>

**Stretch.** Wire everything in a single `composeApp(config)` factory function that returns the Express app. Tests call this factory with in-memory adapters.

<details><summary>Solution</summary>

See the production-quality code section above. The `composeApp()` function creates the Express app, instantiates all storage and service dependencies, mounts routes, and returns the configured app. Tests call `composeApp()` directly (optionally passing test-specific config) and use `supertest(app)` to make requests.

</details>

**Stretch++.** Reorganize the project into a by-feature layout (`src/users/{route,service,storage}.ts`) and compare. Which is easier to navigate?

<details><summary>Solution</summary>

By-feature layout:
```
src/users/route.ts     → imports service
src/users/service.ts   → imports storage interface
src/users/storage.ts   → defines interface + Postgres implementation
src/users/schema.ts    → Zod schemas
```

Advantage: everything about "users" is in one directory. Disadvantage: shared utilities (error classes, middleware) still need a common location. For small teams, by-layer is simpler. For large teams with feature ownership, by-feature scales better.

</details>

## Quiz

1. What should HTTP handlers do?
   (a) Hold all business logic  (b) Be thin: parse input, call a service, write the response  (c) Talk to the database directly  (d) All of the above

2. In ports-and-adapters, what is a "port"?
   (a) A TCP port number  (b) An interface the service defines; implementations plug in  (c) A UI-only pattern  (d) Deprecated in modern frameworks

3. What does the `asyncHandler` wrapper do?
   (a) Makes async handlers synchronous  (b) Forwards thrown/rejected errors to Express error middleware  (c) Wraps database calls  (d) Adds logging

4. How should you handle circular imports between layers?
   (a) They're safe — ignore them  (b) Restructure: enforce a strict dependency direction (routes → services → storage)  (c) They're required for DI  (d) Only a TypeScript problem

5. What's the best folder layout approach?
   (a) By layer only  (b) By feature only  (c) Either is valid — pick one and be consistent  (d) Random

**Short answer:**

6. Name one concrete benefit of the ports-and-adapters approach.

7. Why is composing all app dependencies in a single factory function useful?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-c. 6 — You can run your full service test suite against an in-memory adapter in milliseconds, without Docker or a real database, while using the exact same service code that runs in production. 7 — A single composition root makes all dependencies visible in one place, simplifies test setup (swap any dependency), and prevents hidden global state.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-architecture — mini-project](mini-projects/03-architecture-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP clients](../10-http-clients/01-why-http.md) — symmetric skills for debugging full stacks.
  - [Safe SQL from application code](../11-sql/04-crud.md) — parameters, transactions, and errors behind your routes.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Three layers — transport (handlers), service (business logic), storage (database) — give each piece one job and one reason to change.
- Services depend on storage *interfaces*, not implementations. Swap Postgres for an in-memory Map in tests without touching business logic.
- Keep handlers thin: parse → delegate → respond. If a handler contains an `if` that isn't about request validation, that logic belongs in the service.
- Wire all dependencies in a single composition root so the full dependency graph is visible and testable.

## Further reading

- Alistair Cockburn, [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- Mark Seemann, *Dependency Injection: Principles, Practices, and Patterns*
- Next: [JSON](04-json.md).
