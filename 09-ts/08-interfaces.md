# Chapter 08 — Interfaces

> "An interface is a named object shape. It overlaps heavily with `type` — but has a few superpowers, and is idiomatic in many TypeScript codebases."

## Learning objectives

By the end of this chapter you will be able to:

- Declare and extend interfaces.
- Use declaration merging deliberately (and know when it's dangerous).
- Choose between `interface` and `type` with a clear rationale.
- Implement interfaces with classes.
- Augment third-party types using global declaration merging.

## Prerequisites & recap

- [Chapter 05 — Objects](05-objects.md) — object types, structural typing.
- [Chapter 07 — Intersections](07-intersections.md) — `&`, composition.

## The simple version

An interface is just a named shape for an object — "a thing with these properties and methods." It's almost identical to a `type` alias for an object, but with two extra capabilities: it can be *extended* with `extends`, and it supports *declaration merging* (two `interface User {}` blocks in different files automatically combine into one).

Most of the time, `interface` and `type` are interchangeable for object shapes. The real question is which conventions your team follows. The pragmatic rule: use `interface` for object shapes you expect to extend or augment; use `type` for unions, intersections, conditional types, and computed types.

## In plain terms (newbie lane)

This chapter is really about **Interfaces**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌─────────────────┐   extends   ┌─────────────────┐
  │   Timestamps    │◀────────────│      User       │
  │  createdAt      │             │  id, name       │
  │  updatedAt      │             │  + createdAt    │
  └─────────────────┘             │  + updatedAt    │
                                  └────────┬────────┘
                                           │
                                     implements
                                           │
                                  ┌────────┴────────┐
                                  │  class UserImpl │
                                  │  (must satisfy  │
                                  │   all fields)   │
                                  └─────────────────┘
```
*Figure 8-1. Interfaces define shape; classes implement it; `extends` chains shapes together.*

## Concept deep-dive

### Declaring interfaces

```ts
interface User {
  id: number;
  name: string;
  email?: string;
  readonly createdAt: Date;
}
```

This is equivalent to `type User = { id: number; name: string; ... }`. The syntax differs (no `=`, uses `{ }` directly), but the resulting type is the same.

### Extending interfaces

```ts
interface Timestamps {
  createdAt: Date;
  updatedAt: Date;
}

interface User extends Timestamps {
  id: number;
  name: string;
}
```

`extends` copies all properties from the parent. You can extend multiple interfaces:

```ts
interface Permissioned {
  permissions: string[];
}

interface Admin extends User, Permissioned {}
```

Why `extends` over `&`? Two reasons: readability (it reads like natural English) and error messages (extending with a conflicting property type gives a clear error, while `&` silently produces `never`).

### Declaration merging — the unique superpower

```ts
interface User { id: number }
interface User { name: string }
// merged: User has both id and name
```

Two separate `interface User { ... }` declarations merge automatically. Type aliases can't do this.

**Legitimate use:** augmenting third-party library types. Express's `Request` object, Node's `ProcessEnv`, and similar types are designed to be extended via declaration merging:

```ts
declare global {
  namespace Express {
    interface Request {
      user?: { id: string; role: string };
    }
  }
}
export {};
```

**Dangerous use:** accidental merging within your app code. If two files both declare `interface User`, they silently combine, potentially creating a shape neither author intended.

### Augmenting `process.env`

```ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      PORT: string;
      NODE_ENV: "development" | "production" | "test";
      DATABASE_URL: string;
    }
  }
}
export {};
```

Now `process.env.PORT` is typed as `string` instead of `string | undefined`, and `process.env.NODE_ENV` is restricted to three known values.

### Classes implementing interfaces

```ts
interface Greeter {
  greet(): string;
}

class Hello implements Greeter {
  greet(): string {
    return "hi";
  }
}
```

`implements` doesn't inherit anything — it only verifies that the class satisfies the interface at compile time. If you forget a method, the compiler tells you. If you add extra methods, that's fine (structural typing).

### Function types via interfaces

```ts
interface BinOp {
  (a: number, b: number): number;
}
const add: BinOp = (a, b) => a + b;
```

Same effect as `type BinOp = (a: number, b: number) => number`. Rarely used — type aliases are more readable for function types.

### When to pick what

| Use case | Pick |
|----------|------|
| Object shapes, especially extendable | `interface` |
| Unions, intersections, mapped types | `type` |
| Library type augmentation | `interface` (declaration merging) |
| Function signatures | `type` |
| Conditional or template literal types | `type` |

In practice, many teams pick one style and use it everywhere. Consistency matters more than the micro-optimization of choosing perfectly between them.

## Why these design choices

**Why do both `interface` and `type` exist?** Historical reasons. `interface` predates many of `type`'s capabilities and is deeply embedded in TypeScript's design. They've converged so much that for object shapes, they're nearly identical. The TypeScript team has said they'd probably not have both if starting from scratch.

**Why declaration merging?** It enables "open" types that libraries can expose and consumers can extend — crucial for the DefinitelyTyped ecosystem. Without it, you couldn't add a `user` property to Express's `Request` without forking the types.

**When would you pick differently?** If you're building a library meant to be augmented by consumers, use `interface` for the shapes they'll extend. If you're writing internal application code where merging would be confusing, use `type` to avoid accidental merging.

## Production-quality code

```ts
interface Repository<T> {
  find(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(item: T): Promise<void>;
  delete(id: string): Promise<void>;
}

class InMemoryRepo<T extends { id: string }> implements Repository<T> {
  private readonly store = new Map<string, T>();

  async find(id: string): Promise<T | null> {
    return this.store.get(id) ?? null;
  }

  async findAll(): Promise<T[]> {
    return [...this.store.values()];
  }

  async save(item: T): Promise<void> {
    this.store.set(item.id, item);
  }

  async delete(id: string): Promise<void> {
    this.store.delete(id);
  }
}

interface User {
  id: string;
  name: string;
  email: string;
}

const userRepo: Repository<User> = new InMemoryRepo<User>();
```

This pattern lets you swap `InMemoryRepo` for a `PostgresRepo` or a `MongoRepo` without changing the code that depends on `Repository<User>` — that's the power of coding against an interface.

## Security notes

N/A — Interfaces are a compile-time construct. The same runtime validation rules apply: never trust that an object from external input matches an interface. Validate with a runtime schema library at trust boundaries.

## Performance notes

N/A — Interfaces are fully erased at compile time. There is no runtime cost to declaring or implementing an interface. The `implements` keyword generates no code — it's a pure compile-time check.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Interface has unexpected properties | Accidental declaration merging from another file | Use `type` for app code; reserve `interface` for types designed to merge |
| 2 | Global augmentation doesn't work | Missing `export {}` at the bottom of the `.d.ts` file | Add `export {}` to make the file a module |
| 3 | `implements` but forgot a method | Missing method in class body | Read the compiler error; implement the missing method |
| 4 | Mixing `interface` and `type` for the same concept | Inconsistent style across files | Pick one convention and lint for it |
| 5 | `Property 'user' does not exist on type 'Request'` | Missing global augmentation for Express | Add a `declare global { namespace Express { ... } }` block |

## Practice

**1. Warm-up.** Convert `type User = { id: number; name: string }` to an `interface` and verify it works the same way.

**2. Standard.** Define a `Storage<T>` interface with `get`, `set`, `delete` methods. Implement `InMemoryStorage<T>`.

**3. Bug hunt.** Why does merging `interface User` in two separate files quietly change the type's shape?

**4. Stretch.** Augment `process.env` to include typed `PORT`, `NODE_ENV`, and `DATABASE_URL` fields.

**5. Stretch++.** Write a declaration file (`types/express.d.ts`) that adds `user?: { id: string; role: string }` to Express's `Request`.

<details><summary>Solutions</summary>

**1.**
```ts
interface User {
  id: number;
  name: string;
}
```
Same behavior as the `type` alias — structural typing doesn't care which keyword you used.

**2.**
```ts
interface Storage<T> {
  get(key: string): T | undefined;
  set(key: string, value: T): void;
  delete(key: string): boolean;
}

class InMemoryStorage<T> implements Storage<T> {
  private data = new Map<string, T>();
  get(key: string) { return this.data.get(key); }
  set(key: string, value: T) { this.data.set(key, value); }
  delete(key: string) { return this.data.delete(key); }
}
```

**3.** Declaration merging is a feature of `interface` — two declarations with the same name automatically combine. In a large codebase, this can produce unexpected shapes without any explicit connection between the files.

**4.**
```ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      PORT: string;
      NODE_ENV: "development" | "production" | "test";
      DATABASE_URL: string;
    }
  }
}
export {};
```

**5.**
```ts
// types/express.d.ts
declare global {
  namespace Express {
    interface Request {
      user?: { id: string; role: string };
    }
  }
}
export {};
```

</details>

## Quiz

1. Interface vs. type alias:
   (a) Identical in all cases  (b) Interfaces can declaration-merge; types can't  (c) Interfaces are classes  (d) Types are runtime-checked

2. `implements` on a class:
   (a) Checked at compile time only  (b) Checked at runtime  (c) Deprecated  (d) Optional and has no effect

3. Extending multiple interfaces:
   (a) Not allowed  (b) `extends A, B`  (c) Only through intersection  (d) Only one parent allowed

4. `interface BinOp { (a: number, b: number): number }` declares:
   (a) An object type  (b) A function type  (c) Illegal syntax  (d) A class

5. Augmenting a global type requires:
   (a) `declare global { ... }` in a module file  (b) `extends` keyword  (c) `import.meta`  (d) It's impossible

**Short answer:**

6. When is declaration merging genuinely useful?
7. When does `type` beat `interface`?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-a. 6 — When augmenting third-party library types (e.g., adding fields to Express Request, extending ProcessEnv). This is the primary designed use case. 7 — For unions (`type A = B | C`), mapped types, conditional types, template literal types, and any computed type. Interfaces can only describe object shapes.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-interfaces — mini-project](mini-projects/08-interfaces-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Interfaces declare named object shapes, nearly identical to type aliases for objects.
- `extends` chains interfaces; declaration merging combines same-named interfaces automatically.
- Use `interface` for shapes you expect to extend or augment; use `type` for unions and computed types.
- `implements` on classes is a compile-time shape check — it doesn't inherit anything.

## Further reading

- [TypeScript Handbook — Interfaces](https://www.typescriptlang.org/docs/handbook/2/objects.html#interfaces)
- [TypeScript Handbook — Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
- Next: [Enums](09-enums.md)
