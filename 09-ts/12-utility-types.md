# Chapter 12 — Utility Types

> "TypeScript ships a small library of *utility types* — type-level functions — that let you transform existing types without rewriting them."

## Learning objectives

By the end of this chapter you will be able to:

- Use `Partial`, `Required`, `Readonly`, `Pick`, `Omit`, and `Record` to reshape object types.
- Use `Extract`, `Exclude`, and `NonNullable` to filter union types.
- Use `Parameters`, `ReturnType`, and `Awaited` to extract types from functions and promises.
- Compose utility types for real-world patterns like PATCH endpoints and event maps.

## Prerequisites & recap

- [Chapter 05 — Objects](05-objects.md) — object types, `readonly`, optional properties.
- [Chapter 03 — Unions](03-unions.md) — union types, literal types.

## The simple version

Utility types are TypeScript's built-in type transformers. Instead of rewriting a type with different modifiers, you wrap an existing type: `Partial<User>` makes every field optional, `Readonly<User>` makes every field readonly, `Pick<User, "name" | "email">` extracts just those fields. Think of them as functions that take a type and return a new type.

The key insight: these transformations are *type-level only*. They don't generate any runtime code. `Partial<User>` doesn't create a new object — it creates a new *type* that describes what a partial user object looks like.

## In plain terms (newbie lane)

This chapter is really about **Utility Types**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
         ┌──────────────┐
         │   User       │
         │  id: number  │
         │  name: string│
         │  email: string│
         └──────┬───────┘
                │
  ┌─────────────┼──────────────┬──────────────┐
  │             │              │              │
  ▼             ▼              ▼              ▼
Partial<>    Readonly<>    Pick<,"name">   Omit<,"id">
  │             │              │              │
  ▼             ▼              ▼              ▼
all fields   all fields     { name:       { name: str,
optional     readonly        string }      email: str }
```
*Figure 12-1. Utility types transform an existing type into a new shape.*

## Concept deep-dive

### `Partial<T>` — make everything optional

```ts
type User = { id: number; name: string; email: string };
type UserPatch = Partial<User>;
// { id?: number; name?: string; email?: string }
```

Why is this useful? PATCH endpoints: callers send only the fields they want to update.

### `Required<T>` — make everything required

The inverse of `Partial`:

```ts
type WithAllFields = Required<{ id?: number; name?: string }>;
// { id: number; name: string }
```

### `Readonly<T>` — make everything readonly

```ts
const u: Readonly<User> = { id: 1, name: "Ada", email: "a@b.c" };
u.name = "x";   // error: cannot assign to 'name'
```

Important: `Readonly<T>` is *shallow*. If `User` has a nested object field like `address: { city: string }`, the nested `city` is still mutable. For deep readonly, you need a custom recursive type (see Practice section).

### `Pick<T, Keys>` — keep only specific fields

```ts
type NameAndEmail = Pick<User, "name" | "email">;
// { name: string; email: string }
```

Use `Pick` when you want a subset of an existing type — like a public view that hides internal fields.

### `Omit<T, Keys>` — remove specific fields

```ts
type PublicUser = Omit<User, "passwordHash">;
```

The complement of `Pick`. Useful for stripping sensitive or internal fields.

### `Record<K, V>` — typed dictionary

```ts
type ScoreBoard = Record<string, number>;
const s: ScoreBoard = { ada: 36, alan: 41 };

type Role = "admin" | "user" | "viewer";
type Permissions = Record<Role, string[]>;
```

When `K` is a literal union, `Record` guarantees that *every* key is present — it's an exhaustive map.

### `Extract<T, U>` and `Exclude<T, U>` — filter unions

```ts
type Primitive = string | number | boolean | null;
type NonNull   = Exclude<Primitive, null>;            // string | number | boolean
type StrOrNum  = Extract<Primitive, string | number>; // string | number
```

`Exclude` removes members assignable to `U`. `Extract` keeps only members assignable to `U`.

### `NonNullable<T>`

```ts
type Defined = NonNullable<string | undefined | null>;   // string
```

Shorthand for `Exclude<T, null | undefined>`.

### `Parameters<F>` and `ReturnType<F>`

Extract parameter types and return type from a function type:

```ts
type F = (a: number, b: string) => boolean;
type Args = Parameters<F>;    // [number, string]
type Ret  = ReturnType<F>;     // boolean
```

### `Awaited<T>`

Recursively unwraps promises:

```ts
type T = Awaited<Promise<Promise<string>>>;   // string
```

### Composing utility types

The real power comes from combining them:

```ts
type UserUpdate = Partial<Omit<User, "id" | "createdAt">>;
```

This says: "all User fields except `id` and `createdAt`, and all of them optional." One line replaces a duplicate type declaration that would drift out of sync.

## Why these design choices

**Why are utility types shallow?** Because deep transformations require recursion, which adds complexity and can interact badly with circular types. Shallow is the safe, predictable default. When you need deep versions, you write them explicitly (or use a library).

**Why do `Pick` and `Omit` accept string keys instead of inferring?** Because you might want to compute keys dynamically with `keyof`, conditional types, or template literals. Accepting a union of string literal types is the most flexible design.

**When would you pick differently?** For nested objects, `Partial<T>` disappoints — nested fields stay required. You'll need a custom `DeepPartial<T>` (see [Chapter 14 — Conditional Types](14-conditional-types.md)). Also, `Omit<T, K>` doesn't error when `K` contains keys that don't exist in `T` — this can hide typos. Some teams use a stricter `StrictOmit` custom type.

## Production-quality code

```ts
interface User {
  readonly id: number;
  readonly name: string;
  readonly email: string;
  readonly role: "admin" | "user" | "viewer";
  readonly passwordHash: string;
  readonly createdAt: Date;
}

type PublicUser = Omit<User, "passwordHash">;

type UserCreateInput = Omit<User, "id" | "createdAt" | "passwordHash"> & {
  password: string;
};

type UserUpdateInput = Partial<Omit<User, "id" | "createdAt" | "passwordHash">>;

type EventMap = {
  "user:created": { user: PublicUser };
  "user:updated": { userId: number; changes: UserUpdateInput };
  "user:deleted": { userId: number };
};

function emit<K extends keyof EventMap>(event: K, payload: EventMap[K]): void {
  console.log(`[${String(event)}]`, payload);
}

function patchUser(id: number, patch: UserUpdateInput): PublicUser {
  const existing = loadUser(id);
  const updated = { ...existing, ...patch };
  saveUser(updated);

  const { passwordHash, ...publicUser } = updated;
  return publicUser;
}

function loadUser(_id: number): User {
  throw new Error("Not implemented");
}
function saveUser(_user: User): void {
  throw new Error("Not implemented");
}
```

## Security notes

- **`Omit` for sensitive fields is a compile-time guard only.** At runtime, the object still has the omitted fields unless you explicitly delete or destructure them away. When sending data to clients, destructure to create a new object without sensitive fields.
- **`Partial` inputs need runtime validation.** A PATCH endpoint typed as `Partial<User>` accepts `{}` — which is technically valid but might not be meaningful. Validate that at least one field is present.

## Performance notes

N/A — Utility types are erased at compile time. They produce zero runtime code. The only cost is compile-time type computation, which is negligible for standard utility types.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Nested objects still mutable after `Readonly<T>` | `Readonly` is shallow | Write a `DeepReadonly<T>` or use a library |
| 2 | `Omit<T, "typo">` doesn't error | `Omit` accepts any string, not just valid keys | Use a custom `StrictOmit<T, K extends keyof T>` |
| 3 | `Partial<T>` lets through `{}` as valid | Every field is optional, so an empty object satisfies the type | Validate at runtime that at least one field is present |
| 4 | Utility types expected at runtime | Assuming `Partial<User>` creates some runtime object | Remember: utility types are erased. They're compile-time only |
| 5 | Composing too many utility types in one line | `Partial<Omit<Pick<Required<T>, K>, J>>` becomes unreadable | Extract intermediate types with descriptive names |

## Practice

**1. Warm-up.** Write out the expanded type of `Partial<{ a: number; b: string }>` — what does each field look like?

**2. Standard.** Define `type PublicUser = Omit<User, "passwordHash">` and verify that accessing `passwordHash` on a `PublicUser` is a compile error.

**3. Bug hunt.** Why does `Partial<User>` not affect nested objects? What would you need for deep partial?

**4. Stretch.** Use `Record<HttpMethod, Handler>` to type a route map where every HTTP method must have a handler.

**5. Stretch++.** Use `Parameters` and `ReturnType` to write a generic `typedCall<F extends (...args: any[]) => any>(fn: F, ...args: Parameters<F>): ReturnType<F>` wrapper.

<details><summary>Solutions</summary>

**1.**
```ts
// Partial<{ a: number; b: string }> expands to:
// { a?: number; b?: string }
// Each field becomes optional (T | undefined).
```

**2.**
```ts
type User = { id: number; name: string; passwordHash: string };
type PublicUser = Omit<User, "passwordHash">;

const u: PublicUser = { id: 1, name: "Ada" };
// u.passwordHash;  // error: Property 'passwordHash' does not exist
```

**3.** `Partial<T>` only makes top-level properties optional. If `User` has `address: { city: string; zip: string }`, the nested `city` and `zip` remain required. For deep partial:
```ts
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};
```

**4.**
```ts
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type Handler = (req: Request) => Response;
type RouteMap = Record<HttpMethod, Handler>;
```

**5.**
```ts
function typedCall<F extends (...args: any[]) => any>(
  fn: F,
  ...args: Parameters<F>
): ReturnType<F> {
  return fn(...args);
}
```

</details>

## Quiz

1. `Partial<T>`:
   (a) Makes every field optional  (b) Removes `readonly`  (c) Deletes properties at runtime  (d) Works at runtime

2. `Pick<T, K>` vs. `Omit<T, K>`:
   (a) Same thing  (b) Reversed  (c) `Pick` keeps `K`; `Omit` removes `K`  (d) Unrelated

3. `Record<K, V>`:
   (a) Creates an object type mapping each key in `K` to value type `V`  (b) A tuple  (c) An array  (d) A union

4. `ReturnType<F>`:
   (a) Always `never`  (b) Extracts `F`'s return type  (c) Returns `F` itself  (d) Always `unknown`

5. Utility types at runtime:
   (a) Present as objects  (b) Fully erased  (c) Generate JavaScript  (d) Partially present

**Short answer:**

6. When does `Partial<T>` disappoint?
7. Name one practical use for `Parameters<F>`.

*Answers: 1-a, 2-c, 3-a, 4-b, 5-b. 6 — When `T` has nested object fields: `Partial` only makes top-level fields optional, leaving nested fields required. You need `DeepPartial<T>` for full recursion. 7 — Building a generic wrapper or decorator that preserves a function's parameter types, like a logging wrapper or retry function.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [12-utility-types — mini-project](mini-projects/12-utility-types-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Utility types are type-level functions that transform existing types without rewriting them.
- `Partial`, `Pick`, `Omit`, `Record` reshape objects; `Extract`, `Exclude` filter unions.
- Compose them (`Partial<Omit<User, "id">>`) to derive input/output types from a single source of truth.
- They're all shallow and compile-time only — no runtime impact, no deep nesting.

## Further reading

- [TypeScript Handbook — Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript Playground](https://www.typescriptlang.org/play) — experiment with utility type compositions interactively.
- Next: [Generics](13-generics.md)
