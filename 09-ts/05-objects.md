# Chapter 05 — Objects

> "Object types describe shape. TypeScript's type system is primarily *structural* — a value fits a type if its shape matches."

## Learning objectives

By the end of this chapter you will be able to:

- Declare object types via inline annotations and type aliases.
- Use optional (`?`) and `readonly` properties.
- Use index signatures for dictionary-like objects.
- Explain structural typing and excess property checks.
- Apply branded types when structural typing is too permissive.

## Prerequisites & recap

- [Chapter 01 — Types](01-types.md) — primitives, inference.
- [Module 08 — JS Objects](../08-js/04-objects.md) — object literals, destructuring, computed properties.

## The simple version

In TypeScript, an object type is a description of *shape*: what properties exist, what types they have, and which ones are optional. If a value has the right shape, it fits the type — regardless of where it came from or what it's called. This is *structural typing*: TypeScript cares about what a value looks like, not what it's named.

This is fundamentally different from Java or C# where you need to explicitly declare that a class "implements" an interface. In TypeScript, if it has the right fields, it fits. No ceremony required.

## In plain terms (newbie lane)

This chapter is really about **Objects**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  type Point = { x: number; y: number }

  ┌────────────────────────┐
  │  { x: 1, y: 2, z: 3 } │   value (has extra field)
  └───────────┬────────────┘
              │
              │  structural check:
              │  has x: number? ✓
              │  has y: number? ✓
              ▼
  ┌────────────────────────┐
  │       Point            │   type (satisfied)
  └────────────────────────┘
```
*Figure 5-1. Structural typing checks shape, not identity. Extra fields are tolerated (with caveats).*

## Concept deep-dive

### Inline types vs. aliases

```ts
function greet(u: { name: string }): string {
  return `hi, ${u.name}`;
}
```

For one-off types, inline is fine. For reusable shapes, always give them a name:

```ts
type User = { id: number; name: string; email?: string };
```

Why alias? Because you'll reference this shape in multiple places — function parameters, return types, API response handlers. A name makes it greppable, refactorable, and self-documenting.

### Optional properties

```ts
type User = { id: number; name: string; email?: string };
```

`email` has type `string | undefined`. You must check for `undefined` before using it. Optional properties are different from properties that are explicitly `string | undefined` — with `exactOptionalPropertyTypes` enabled, you can't assign `undefined` to an optional field (it must be absent or a `string`).

### Readonly properties

```ts
type Config = { readonly port: number; readonly host: string };

const config: Config = { port: 8080, host: "localhost" };
config.port = 3000;  // error: Cannot assign to 'port' because it is a read-only property
```

`readonly` is compile-time only — it doesn't call `Object.freeze()`. But it prevents accidental mutation through the type system, which catches most bugs.

### Index signatures — open-ended shapes

When you need a dictionary-like object with dynamic keys:

```ts
type Headers = { [key: string]: string };
const h: Headers = { "content-type": "application/json" };
```

With `noUncheckedIndexedAccess` enabled, `h["x-custom"]` returns `string | undefined` — because the key might not exist. Without the flag, TypeScript pretends every key is present, which is unsafe.

### Structural typing — duck typing with teeth

```ts
type Point = { x: number; y: number };

const p3d = { x: 1, y: 2, z: 3 };
const p: Point = p3d;   // OK — p3d has x and y, that's enough
```

TypeScript is structural: if a value has at least the required properties, it satisfies the type. Extra properties are tolerated when assigning from a variable.

But there's a catch — **excess property checks**:

```ts
const p2: Point = { x: 1, y: 2, z: 3 };  // ERROR: 'z' does not exist in type 'Point'
```

When you assign an *object literal* directly to a typed variable, TypeScript adds an extra check: no properties beyond what the type declares. Why? Because extra properties on a literal are almost always typos. If you meant to pass `z`, you probably mistyped a field name. This check only applies to literals — assigning from a variable (as in the `p3d` example above) doesn't trigger it.

### Intersections for merging

You can combine object types with `&`:

```ts
type Timestamped = { createdAt: Date; updatedAt: Date };
type UserWithTimes = User & Timestamped;
```

See [Chapter 07 — Intersections](07-intersections.md) for the full story.

### Branded types — when structural is too loose

Sometimes two types have the same shape but represent different things:

```ts
type UserId = number & { readonly __brand: unique symbol };
type PostId = number & { readonly __brand: unique symbol };

function createUserId(n: number): UserId {
  return n as UserId;
}

function getUser(id: UserId): void { /* ... */ }

const postId = 42 as PostId;
getUser(postId);  // error: PostId is not assignable to UserId
```

Branding adds a phantom property that doesn't exist at runtime but prevents mixing up structurally identical types. Use it when confusing two IDs or two measurements would cause a real bug.

## Why these design choices

**Why structural typing?** It matches how JavaScript actually works. Objects in JS don't declare which "interface" they implement — they just have properties. Structural typing aligns the type system with the runtime semantics, avoiding the friction of nominal typing where you'd need explicit `implements` declarations everywhere.

**Why excess property checks only on literals?** It's a pragmatic compromise. Object literals are "fresh" — you're creating them right there, so extra properties are likely mistakes. Variables might come from a library, a function call, or a spread — extra properties are expected and harmless.

**When would you pick differently?** If you need nominal typing (preventing structurally identical but semantically different types from being mixed), use branded types. If you need deep immutability, use `Readonly<T>` recursively or reach for a library like Immer.

## Production-quality code

```ts
type User = {
  readonly id: number;
  readonly name: string;
  readonly email: string;
  readonly role: "admin" | "user" | "viewer";
  readonly createdAt: Date;
};

type UserPatch = Partial<Omit<User, "id" | "createdAt">>;

type UserIndex = { readonly [id: number]: User | undefined };

function buildIndex(users: readonly User[]): UserIndex {
  const index: Record<number, User> = {};
  for (const user of users) {
    index[user.id] = user;
  }
  return index;
}

function findUser(index: UserIndex, id: number): User | undefined {
  return index[id];
}

function applyPatch(user: User, patch: UserPatch): User {
  return { ...user, ...patch, updatedAt: new Date() } as User & { updatedAt: Date };
}
```

## Security notes

- **Don't trust object shapes from external input.** TypeScript's structural checks are compile-time only. A JSON payload can have any shape. Always validate at trust boundaries with a runtime schema library (Zod, ArkType, etc.).
- **Excess property checks don't apply to API responses.** If a server returns extra fields, they'll be silently included in your object. Don't assume an object *only* has the declared properties — it might have more.

## Performance notes

N/A — Object types are erased at compile time. The runtime performance of object creation, access, and spread is unchanged from plain JavaScript. The only consideration: deep-spreading large objects for immutability has O(n) cost per level, same as in JS.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Mutating a shared object that callers own | Input object typed without `readonly` or `Readonly<T>` | Use `Readonly<T>` or `readonly` on input parameters |
| 2 | `Property 'z' does not exist on type 'Point'` on an inline literal | Excess property check on object literal | Assign via a variable if the extra field is intentional, or remove it |
| 3 | `undefined` access on index signature without error | `noUncheckedIndexedAccess` not enabled | Enable the flag; handle `T \| undefined` |
| 4 | Mixing up `UserId` and `PostId` because both are `number` | Structural typing treats identical shapes as the same type | Use branded types to distinguish |

## Practice

**1. Warm-up.** Define an `Address` type with `street: string`, `city: string`, `zip: string` and use it in a function parameter.

**2. Standard.** Create a dictionary of users keyed by numeric id. Write a typed lookup function that returns `User | undefined`.

**3. Bug hunt.** Why does `const p: Point = { x: 1, y: 2, z: 3 }` fail, but `const tmp = { x: 1, y: 2, z: 3 }; const p: Point = tmp;` succeeds?

**4. Stretch.** Implement a branded `UserId` type with a factory function. Verify that a plain `number` can't be used where `UserId` is expected.

**5. Stretch++.** Use `Readonly<T>` to make an entire `Config` type deeply immutable (one level). Then explore why nested objects remain mutable and what you'd need for deep readonly.

<details><summary>Solutions</summary>

**1.**
```ts
type Address = { street: string; city: string; zip: string };

function formatAddress(addr: Address): string {
  return `${addr.street}, ${addr.city} ${addr.zip}`;
}
```

**2.**
```ts
type UserIndex = { [id: number]: User | undefined };

function findUser(index: UserIndex, id: number): User | undefined {
  return index[id];
}
```

**3.** Object literals get an "excess property check" that rejects extra fields — it's designed to catch typos. Assigning from a variable bypasses this check because the variable might legitimately have extra properties from another context.

**4.**
```ts
type UserId = number & { readonly __brand: unique symbol };

function createUserId(n: number): UserId {
  return n as UserId;
}

function getUser(id: UserId): void { /* ... */ }

// getUser(42);  // error: number is not assignable to UserId
getUser(createUserId(42));  // OK
```

**5.**
```ts
type Config = Readonly<{
  host: string;
  port: number;
  db: { host: string; port: number };
}>;
// config.host = "x"     → error (readonly)
// config.db.host = "x"  → no error! Readonly is shallow.
// For deep: type DeepReadonly<T> = { readonly [K in keyof T]: DeepReadonly<T[K]> };
```

</details>

## Quiz

1. TypeScript's type system is:
   (a) Nominal  (b) Structural  (c) Dynamic  (d) Interface-only

2. `readonly` on an object property:
   (a) Calls `Object.freeze` at runtime  (b) Prevents writes at compile time  (c) Makes the property private  (d) Renames the property

3. An index signature `[k: string]: V` is for:
   (a) Open-ended dictionaries  (b) Required on every object  (c) Deprecated  (d) Arrays only

4. Excess property checks apply to:
   (a) All assignments  (b) Object literals assigned directly to typed targets  (c) Classes only  (d) Never

5. `T & U` on object types produces:
   (a) The first type only  (b) A union  (c) An intersection — must satisfy both  (d) A compile error

**Short answer:**

6. When should you use an inline object type vs. a type alias?
7. Why are branded types useful despite adding complexity?

*Answers: 1-b, 2-b, 3-a, 4-b, 5-c. 6 — Inline for one-off, single-use shapes (e.g., a local helper function parameter). Type alias for any shape referenced in two or more places. 7 — They prevent mixing up structurally identical but semantically different values (e.g., UserId vs. PostId), turning a class of logic bugs into compile errors.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-objects — mini-project](mini-projects/05-objects-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Object types describe shape; TypeScript's structural typing checks shape, not identity.
- Use `readonly` and optional (`?`) properties to communicate intent and enforce constraints.
- Excess property checks catch typos on object literals; structural typing is permissive elsewhere.
- Branded types add nominal-like safety when structural typing is too loose.

## Further reading

- [TypeScript Handbook — Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook — Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)
- Next: [Tuples](06-tuples.md)
