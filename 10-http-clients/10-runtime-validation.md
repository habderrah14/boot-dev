# Chapter 10 — Runtime Validation

> "TypeScript's types vanish at build time. Anything crossing your process boundary — HTTP body, env var, file — is just bytes. Validate at the boundary or pay the price later."

## Learning objectives

By the end of this chapter you will be able to:

- Explain why TypeScript types cannot validate runtime data and identify the exact boundary where the gap exists.
- Define schemas with Zod that produce both a runtime parser and a TypeScript type from a single source.
- Integrate validation into `fetch` wrappers so every API response is validated before your code touches it.
- Validate environment variables at startup to crash fast on bad configuration.
- Share schemas between client and server in a monorepo.

## Prerequisites & recap

- [JSON](06-json.md) — you know `JSON.parse` returns `any` and that JSON has no schema.
- [Types](../09-ts/01-types.md) — you understand TypeScript's structural type system.

## The simple version

TypeScript types are a compile-time illusion. They help you write correct code, but the moment your program runs, those types are gone — erased by the compiler. When data arrives from outside your process (an HTTP response, a file, an environment variable, a message queue), TypeScript has no idea what shape it has. If you cast `JSON.parse(raw)` to `User`, you're lying to the compiler. It will believe you, and your code will crash later when it tries to access `user.email` on a response that doesn't have an email field.

The fix: use a schema validator like Zod. You define the expected shape once, and Zod gives you two things — a runtime parser that rejects bad data at the boundary, and a TypeScript type you can use throughout your code. One source of truth, two guarantees.

## In plain terms (newbie lane)

This chapter is really about **Runtime Validation**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Outside world              Your process boundary            Your code
  (untrusted)                                                (trusted)
  ┌──────────┐    ┌─────────────────────────────────┐    ┌──────────┐
  │ HTTP body │    │                                 │    │          │
  │ Env vars  │───▶│  JSON.parse ──▶ unknown         │    │  User    │
  │ Files     │    │                   │             │    │  (typed, │
  │ IPC msgs  │    │                   ▼             │    │   safe)  │
  │ CLI args  │    │         schema.parse(unknown)   │───▶│          │
  └──────────┘    │              │           │       │    └──────────┘
                   │           ✓ T        ✗ ZodError │
                   │                                 │
                   └─────────────────────────────────┘
                          THE TRUST BOUNDARY
                   (validate here, trust everywhere else)
```

*Data enters as `unknown`. A schema validator either promotes it to a typed value or rejects it with a structured error. You validate once at the boundary, then trust the type downstream.*

## Concept deep-dive

### The problem

```ts
type User = { id: number; name: string };
const r = await fetch("/api/user/42");
const u: User = await r.json();      // compiles — but it's a lie
```

At runtime, `r.json()` calls `JSON.parse`, which returns `any`. The type annotation `User` makes TypeScript *believe* the data has `id` and `name`, but there's no enforcement. If the server returns `{ "error": "not found" }`, your code won't crash at the fetch — it'll crash later when something tries to use `u.id` as a number.

Why is this so dangerous? Because the crash happens far from where the bad data entered. Debugging becomes a detective game of tracing back to the boundary where validation should have happened.

### The fix: schema validators

A schema validator builds a runtime parser *and* a TypeScript type from the same definition. No duplication, no drift between what you think you're getting and what you actually validate.

| Library | Approach | Bundle size | DX |
|---------|----------|-------------|-----|
| **Zod** | Fluent builder API | ~12KB | Excellent — the de facto standard |
| **Valibot** | Functional, tree-shakeable | ~1KB | Good — Zod-like, smaller output |
| **ArkType** | Type-level inference | ~10KB | Cutting-edge — uses TS type syntax |
| **io-ts** | Functional (fp-ts) | ~6KB | Steeper learning curve |
| **Yup/Joi** | Older, less TS-integrated | ~20KB+ | Mature, but weaker TypeScript inference |

This chapter uses Zod because it's the most widely adopted and has the best TypeScript integration.

### Zod basics

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1),
  email: z.string().email().optional(),
  createdAt: z.string().datetime().transform((s) => new Date(s)),
});

type User = z.infer<typeof UserSchema>;
```

`z.infer<typeof UserSchema>` extracts the TypeScript type:

```ts
type User = {
  id: number;
  name: string;
  email?: string | undefined;
  createdAt: Date;   // transformed from string
};
```

One definition, two outputs. The schema *is* the type.

### Parsing vs. safe parsing

```ts
const user = UserSchema.parse(raw);
// Throws ZodError if invalid

const result = UserSchema.safeParse(raw);
// Returns { success: true, data: User } | { success: false, error: ZodError }
```

When should you use which? Use `.parse()` at trust boundaries where invalid data is unexpected and should crash hard (e.g., env vars at startup). Use `.safeParse()` when you need to handle the failure gracefully (e.g., validating user input and returning error messages).

### Plugging validation into `fetch`

This is where runtime validation pays off most. Every HTTP response crosses a trust boundary:

```ts
async function getValidated<T>(
  url: string,
  schema: z.ZodSchema<T>,
): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new HttpError(r.status, await r.text());
  const raw: unknown = await r.json();
  return schema.parse(raw);
}

const user = await getValidated("/api/users/42", UserSchema);
// user is fully typed AND runtime-validated
```

Now your code is honest. If the server returns unexpected data, you get a `ZodError` at the boundary — not a cryptic `TypeError: Cannot read property 'name' of undefined` three function calls later.

### Sharing schemas between client and server

In a monorepo, put your schemas in a shared package:

```
packages/
  schemas/
    src/user.ts     ← UserSchema + type User
  api-server/
    src/routes.ts   ← imports UserSchema for response validation
  web-client/
    src/api.ts      ← imports UserSchema for response parsing
```

Both sides import the same schema. If the server adds a field, the client's schema is updated in the same PR. If the server removes a field, the client fails to compile — you catch the breaking change before it ships.

### Validating environment variables

Environment variables are another trust boundary. They come from outside your process, and they're always strings:

```ts
const EnvSchema = z.object({
  PORT: z.coerce.number().int().positive(),
  NODE_ENV: z.enum(["development", "production", "test"]),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

export const env = EnvSchema.parse(process.env);
```

Why crash at startup? Because a missing or malformed env var will cause a mysterious failure later — maybe minutes later, maybe on the first request, maybe on the 1000th request. Crashing at boot with `ZodError: PORT: Expected number, received NaN` is infinitely easier to debug.

### Common Zod patterns

**Discriminated unions** — validate and narrow a union at runtime:

```ts
const EventSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("click"), x: z.number(), y: z.number() }),
  z.object({ type: z.literal("keypress"), key: z.string() }),
]);

const event = EventSchema.parse(raw);
switch (event.type) {
  case "click": console.log(event.x, event.y); break;   // narrowed
  case "keypress": console.log(event.key); break;        // narrowed
}
```

**Transforms** — convert data during validation:

```ts
const PostSchema = z.object({
  id: z.number(),
  title: z.string(),
  createdAt: z.string().datetime().transform((s) => new Date(s)),
  tags: z.string().transform((s) => s.split(",").map((t) => t.trim())),
});
```

**Defaults and coercion**:

```ts
z.coerce.number()           // "42" → 42
z.string().default("anon")  // undefined → "anon"
z.boolean().default(false)
```

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Validate at the boundary | One validation point; trusted types everywhere downstream | Validate at every use site | Never — scattered validation is redundant and easy to miss |
| Schema = type (single source) | No drift between what you validate and what you type | Separate type + validator | When you need a type that's different from the wire format (use `.transform()`) |
| Crash on invalid env vars | Fast, obvious failure beats mysterious runtime errors | Log a warning and continue | Never for required vars — a warning gets lost in log noise |
| Zod over manual type guards | Zod handles nested objects, arrays, unions, transforms automatically | Manual `if (typeof x === 'object' && ...)` checks | When you need zero dependencies and the schema is trivially simple |

## Production-quality code

```ts
import { z } from "zod";

class HttpError extends Error {
  constructor(public readonly status: number, public readonly body: string) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
  }
}

class ValidationError extends Error {
  constructor(
    public readonly url: string,
    public readonly issues: z.ZodIssue[],
  ) {
    const summary = issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    super(`Validation failed for ${url}: ${summary}`);
    this.name = "ValidationError";
  }
}

async function getValidated<T>(url: string, schema: z.ZodSchema<T>): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new HttpError(r.status, await r.text());

  const raw: unknown = await r.json();
  const result = schema.safeParse(raw);

  if (!result.success) {
    throw new ValidationError(url, result.error.issues);
  }

  return result.data;
}

async function postValidated<TReq, TRes>(
  url: string,
  body: TReq,
  requestSchema: z.ZodSchema<TReq>,
  responseSchema: z.ZodSchema<TRes>,
): Promise<TRes> {
  const validBody = requestSchema.parse(body);

  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validBody),
  });

  if (!r.ok) throw new HttpError(r.status, await r.text());

  const raw: unknown = await r.json();
  const result = responseSchema.safeParse(raw);

  if (!result.success) {
    throw new ValidationError(url, result.error.issues);
  }

  return result.data;
}

// --- Schemas ---

const UserSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1),
  email: z.string().email(),
  createdAt: z.string().datetime().transform((s) => new Date(s)),
});

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

type User = z.infer<typeof UserSchema>;
type CreateUser = z.infer<typeof CreateUserSchema>;

// --- Usage ---

async function demo() {
  const user = await getValidated("/api/users/42", UserSchema);
  console.log(user.name, user.createdAt instanceof Date);  // true

  const newUser = await postValidated(
    "/api/users",
    { name: "Ada", email: "ada@example.com" },
    CreateUserSchema,
    UserSchema,
  );
  console.log(newUser.id);
}

// --- Environment validation ---

const EnvSchema = z.object({
  PORT: z.coerce.number().int().positive().default(3000),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

export const env = EnvSchema.parse(process.env);
```

## Security notes

- **Validation is a security boundary.** Unvalidated input is the root cause of injection attacks, type confusion, and privilege escalation. Schema validation prevents entire classes of bugs.
- **Don't trust `Content-Type` alone.** A response might claim `Content-Type: application/json` but contain HTML or something else entirely. Always validate the parsed structure.
- **Overly permissive schemas** — `z.object({}).passthrough()` or `z.any()` defeats the purpose. Be as strict as possible; add fields only when needed.
- **Error messages can leak internal structure.** Don't expose raw `ZodError` messages to end users in API responses — they reveal your schema's field names and constraints. Log them internally; return generic errors to clients.

## Performance notes

- **Validation has a cost** — Zod compiles schemas on first use, then reuses the compiled form. For hot paths (thousands of validations per second), this is a few microseconds per validation — negligible compared to I/O.
- **Don't validate the same data twice.** Validate once at the boundary, then pass the typed result through your code. Re-validating deep in the call stack is wasted work.
- **Large schemas** — deeply nested schemas with many transforms can be slower. Profile if you suspect validation is a bottleneck (it almost never is).
- **Valibot for bundle size** — if you're in a browser context where 12KB matters, Valibot gives you Zod-like validation at ~1KB.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "Typed variable has the wrong shape at runtime" | Assigned `JSON.parse(raw)` to a typed variable without validation — the type is a lie | Use `schema.parse(raw)` instead of type assertion |
| 2 | "Validation only happens on the client, server sends bad data" | Server doesn't validate its own responses; client-side validation catches it too late | Validate on both sides. In a monorepo, share the schema |
| 3 | "`any` leaked into the codebase — now nothing is type-safe" | One unvalidated `JSON.parse` result spread through the call chain | Treat all boundary data as `unknown`; validate before using |
| 4 | "App crashes at 3 AM because `DATABASE_URL` is missing" | Environment variable not validated at startup; crash happens on first DB query | Validate all env vars at boot with `schema.parse(process.env)` |
| 5 | "Schema accepts everything — found a bug in production" | Used `z.any()` or `.passthrough()` as a shortcut | Define strict schemas. `.strict()` rejects unknown keys |

## Practice

### Warm-up

Install Zod and write a `UserSchema` with `id` (positive integer), `name` (non-empty string), and `email` (valid email). Validate a valid object and an invalid one.

<details><summary>Show solution</summary>

```bash
npm install zod
```

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1),
  email: z.string().email(),
});

console.log(UserSchema.parse({ id: 1, name: "Ada", email: "ada@example.com" }));
// { id: 1, name: 'Ada', email: 'ada@example.com' }

const result = UserSchema.safeParse({ id: -1, name: "", email: "not-an-email" });
console.log(result.success);  // false
console.log(result.error?.issues);
// [
//   { path: ['id'], message: 'Number must be greater than 0' },
//   { path: ['name'], message: 'String must contain at least 1 character(s)' },
//   { path: ['email'], message: 'Invalid email' },
// ]
```

</details>

### Standard

Wrap `fetch` in a generic `getValidated<T>(url, schema)` function that validates the response body and returns a typed result.

<details><summary>Show solution</summary>

```ts
import { z } from "zod";

async function getValidated<T>(url: string, schema: z.ZodSchema<T>): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const raw: unknown = await r.json();
  return schema.parse(raw);
}

const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
});

const user = await getValidated("https://jsonplaceholder.typicode.com/users/1", UserSchema);
console.log(user.name);  // typed and validated
```

</details>

### Bug hunt

A developer writes:

```ts
type User = { id: number; name: string };
const u: User = JSON.parse(rawBody);
console.log(u.name.toUpperCase());
```

This compiles without errors but crashes at runtime with `TypeError: Cannot read property 'toUpperCase' of undefined`. Why?

<details><summary>Show solution</summary>

`JSON.parse` returns `any`, so the type annotation `User` is a compile-time lie. At runtime, the parsed data might not have a `name` field at all — `rawBody` could be `'{"id": 42}'` or `'{"error": "not found"}'`. The fix: validate with a schema.

```ts
const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
});

const u = UserSchema.parse(JSON.parse(rawBody));
// If name is missing, ZodError is thrown HERE — not later at .toUpperCase()
console.log(u.name.toUpperCase());
```

</details>

### Stretch

Add environment variable validation at application boot. Define a schema for `PORT`, `NODE_ENV`, `DATABASE_URL`, and `API_KEY`. Crash immediately if any required variable is missing or malformed.

<details><summary>Show solution</summary>

```ts
import { z } from "zod";

const EnvSchema = z.object({
  PORT: z.coerce.number().int().positive().default(3000),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

let env: z.infer<typeof EnvSchema>;

try {
  env = EnvSchema.parse(process.env);
} catch (e) {
  if (e instanceof z.ZodError) {
    console.error("Invalid environment variables:");
    for (const issue of e.issues) {
      console.error(`  ${issue.path.join(".")}: ${issue.message}`);
    }
  }
  process.exit(1);
}

console.log(`Starting on port ${env.PORT} in ${env.NODE_ENV} mode`);
```

</details>

### Stretch++

Share a schema between a server and a client in a monorepo structure. Create a shared `schemas/` directory with a `User` schema, and show how both sides import it.

<details><summary>Show solution</summary>

```
packages/
  schemas/
    src/user.ts
    package.json
  api-server/
    src/routes.ts
  web-client/
    src/api.ts
```

`packages/schemas/src/user.ts`:

```ts
import { z } from "zod";

export const UserSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1),
  email: z.string().email(),
  createdAt: z.string().datetime().transform((s) => new Date(s)),
});

export type User = z.infer<typeof UserSchema>;

export const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

export type CreateUser = z.infer<typeof CreateUserSchema>;
```

`packages/api-server/src/routes.ts`:

```ts
import { UserSchema, CreateUserSchema } from "@myapp/schemas";

app.post("/users", (req, res) => {
  const body = CreateUserSchema.parse(req.body);
  const user = createUser(body);
  res.json(UserSchema.parse(user));  // validate outgoing data too
});
```

`packages/web-client/src/api.ts`:

```ts
import { UserSchema, type User } from "@myapp/schemas";

async function getUser(id: number): Promise<User> {
  const r = await fetch(`/api/users/${id}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return UserSchema.parse(await r.json());
}
```

Both sides validate against the same schema. If the schema changes, both sides update together.

</details>

## Quiz

1. TypeScript types at runtime:
   (a) Present and enforced  (b) Erased — they don't exist  (c) Optional  (d) Enforced only in strict mode

2. `z.infer<typeof Schema>` produces:
   (a) A runtime value  (b) A derived TypeScript type  (c) A JSON Schema  (d) A class instance

3. `parse` vs. `safeParse`:
   (a) `parse` throws ZodError on failure; `safeParse` returns a result object  (b) They're identical  (c) `safeParse` is legacy  (d) `parse` is deprecated

4. The best place to validate HTTP response data is:
   (a) In the UI component  (b) In the fetch wrapper at the boundary  (c) In unit tests only  (d) Never

5. Validating environment variables at startup:
   (a) Is overkill  (b) Lets you crash fast on bad configuration before serving traffic  (c) Is too slow  (d) Is impossible in Node

**Short answer:**

6. Why can't TypeScript types replace runtime validation?
7. What's the advantage of sharing schemas between client and server?

*Answers: 1-b, 2-b, 3-a, 4-b, 5-b. 6 — TypeScript types are erased during compilation and don't exist at runtime. Data from external sources (HTTP, files, env vars) has no type information. Without runtime validation, your type annotations are unverified assumptions. 7 — Shared schemas guarantee both sides agree on the data shape. If the server adds, removes, or changes a field, the client's schema updates in the same change, preventing drift. Breaking changes are caught at compile time, not in production.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-runtime-validation — mini-project](mini-projects/10-runtime-validation-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- TypeScript types are compile-time only — they're erased at runtime and can't validate external data.
- Zod (or a similar library) produces both a runtime parser and a TypeScript type from a single schema definition.
- Validate at every trust boundary: HTTP responses, environment variables, files, IPC messages, CLI arguments.
- Share schemas between client and server to prevent drift and catch breaking changes at compile time.

## Further reading

- Zod documentation — comprehensive API reference and guides.
- Colin McDonnell, *Designing the perfect TypeScript schema validation library* — the design philosophy behind Zod.
- Next module: [Module 11 — SQL](../11-sql/README.md).
