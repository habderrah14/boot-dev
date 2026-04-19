# Chapter 03 — Unions

> "A union type says 'this value is one of these.' It's TypeScript's answer to JavaScript's polymorphic values."

## Learning objectives

By the end of this chapter you will be able to:

- Declare union types and explain why they exist.
- Narrow unions with `typeof`, `in`, and discriminated unions.
- Use `never` for exhaustiveness checks that turn missed cases into compile errors.
- Filter unions with `Exclude` and `Extract`.

## Prerequisites & recap

- [Chapter 01 — Types](01-types.md) — primitives, inference, `unknown`.
- [Chapter 02 — Functions](02-functions.md) — function signatures, `never`.

## The simple version

A union type is a choice: "this value is *one of* these types." If you have a variable typed `number | string`, it could be either — and TypeScript won't let you call number-only methods or string-only methods until you check which one you actually have. That check is called *narrowing*, and it's how you go from "could be anything in this set" to "definitely this specific type."

The most powerful form of unions is the *discriminated union*: each variant has a shared literal field (like `kind` or `type`) that TypeScript can read in a `switch` statement. This pattern is the TypeScript equivalent of algebraic data types (sum types) from functional programming.

## In plain terms (newbie lane)

This chapter is really about **Unions**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
         ┌───────────────────┐
         │   A  |  B  |  C   │   union type
         └────────┬──────────┘
                  │
          typeof / in / .kind
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     ┌─────┐  ┌─────┐  ┌─────┐
     │  A  │  │  B  │  │  C  │   narrowed types
     └─────┘  └─────┘  └─────┘
```
*Figure 3-1. Narrowing decomposes a union into its individual variants.*

## Concept deep-dive

### Declaring unions

```ts
type Id = number | string;

function find(id: Id) {
  // id is number | string here — can only use methods common to both
}
```

A value of type `number | string` only exposes what's *common* to both types until you narrow. That means you can't call `.toFixed()` (number-only) or `.padStart()` (string-only) directly.

### Narrowing with `typeof`

For primitive unions, `typeof` is the standard narrowing tool:

```ts
function pad(id: number | string): string {
  if (typeof id === "number") return id.toFixed(2);
  return id.padStart(8, "0");
}
```

Why does this work? TypeScript reads your control flow. After the `typeof` check, it *knows* that inside the `if` block, `id` must be a `number`. In the `else` branch, it's narrowed to `string`.

### Narrowing with `in`

For object unions where variants have different properties:

```ts
type Dog = { bark(): void };
type Cat = { meow(): void };

function speak(a: Dog | Cat) {
  if ("bark" in a) a.bark();
  else a.meow();
}
```

### Discriminated unions — the most powerful pattern

When each variant of a union has a shared literal field, TypeScript can narrow exactly:

```ts
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side * s.side;
  }
}
```

Why is this so powerful? The `kind` field acts as a *tag* that uniquely identifies which variant you're dealing with. TypeScript narrows the entire object — inside the `"circle"` case, `s.radius` exists and `s.side` doesn't. This is compile-time pattern matching.

### Exhaustiveness with `never`

If you add a new shape variant but forget to handle it, TypeScript can catch that:

```ts
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.radius ** 2;
    case "square": return s.side * s.side;
    default: {
      const _exhaustive: never = s;
      return _exhaustive;
    }
  }
}
```

If every variant is handled, `s` in the default branch has type `never` — the assignment succeeds. If you add a `"triangle"` variant without a case, `s` would be `{ kind: "triangle"; ... }` in the default — which isn't assignable to `never`, so the compiler errors. You've turned a runtime bug into a compile-time error.

### `Exclude` and `Extract` — filtering unions

These utility types work on union members:

```ts
type Primitive = string | number | boolean | null;
type NotNull   = Exclude<Primitive, null>;             // string | number | boolean
type StrOrNum  = Extract<Primitive, string | number>;  // string | number
```

`Exclude<T, U>` removes members assignable to `U`. `Extract<T, U>` keeps only members assignable to `U`.

### The Result pattern

A discriminated union for safe error handling without exceptions:

```ts
type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

function divide(a: number, b: number): Result<number> {
  return b === 0
    ? { ok: false, error: "division by zero" }
    : { ok: true, value: a / b };
}

const r = divide(10, 2);
if (r.ok) {
  console.log(r.value);   // TypeScript knows value exists here
} else {
  console.error(r.error);  // TypeScript knows error exists here
}
```

## Why these design choices

**Why unions over class hierarchies?** JavaScript values are often "one of several shapes" without sharing a common class. Unions model this directly, without forcing an inheritance tree. They compose better (you can add variants without modifying existing code) and align with functional programming's sum types.

**Why discriminated unions specifically?** The `kind`/`type` tag pattern is explicit, exhaustive, and JSON-serializable. Unlike `instanceof` checks, it works across serialization boundaries (e.g., API responses), because the tag survives JSON round-trips while prototype chains don't.

**When would you pick differently?** If your variants share significant behavior (methods, state), a class hierarchy with `abstract` might be clearer. But for data-oriented types — API responses, events, parsed tokens — discriminated unions are almost always the better choice.

## Production-quality code

```ts
type HttpOutcome =
  | { status: "ok"; code: 200 | 201; body: unknown }
  | { status: "redirect"; code: 301 | 302; location: string }
  | { status: "client_error"; code: 400 | 401 | 403 | 404; message: string }
  | { status: "server_error"; code: 500 | 502 | 503; message: string };

function handleOutcome(outcome: HttpOutcome): string {
  switch (outcome.status) {
    case "ok":
      return `Success (${outcome.code})`;
    case "redirect":
      return `Redirect to ${outcome.location}`;
    case "client_error":
      return `Client error ${outcome.code}: ${outcome.message}`;
    case "server_error":
      return `Server error ${outcome.code}: ${outcome.message}`;
    default: {
      const _exhaustive: never = outcome;
      return _exhaustive;
    }
  }
}
```

## Security notes

- **Stringly-typed statuses invite injection.** If you type a status as `string` instead of a literal union, any string is accepted — including ones you never intended. Use literal unions to restrict the set of valid values.
- **Validate discriminant fields from external input.** A JSON payload claiming `{ "status": "ok" }` might have `status: "admin_override"`. Always validate that the discriminant matches your union before narrowing.

## Performance notes

N/A — Union types are erased at compile time. The `switch` or `if` statements you write for narrowing are plain JavaScript control flow with no overhead beyond what you'd write without TypeScript.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Property 'foo' does not exist on type 'A \| B'` | Calling a method that only exists on one variant without narrowing first | Narrow with `typeof`, `in`, or a discriminant field before accessing |
| 2 | New variant added but no compile error | Missing exhaustiveness check in `default` | Add `const _: never = x` in the default/else branch |
| 3 | Using `status: string` instead of `status: "ok" \| "error"` | Stringly-typed discriminant | Use literal types for the tag field |
| 4 | Deeply nested `if`/`else` chains to narrow unions | Not using a discriminated union pattern | Refactor to a shared `kind`/`type` tag and use `switch` |

## Practice

**1. Warm-up.** Define `type Id = number | string` and write a function that prints each differently using `typeof`.

**2. Standard.** Create a discriminated `Event` union with variants `"click"` (payload: `{ x: number; y: number }`), `"keypress"` (payload: `{ key: string }`), and `"focus"` (no extra payload). Write a `describe(event: Event): string` function.

**3. Bug hunt.** Why does `function f(x: A | B) { x.foo(); }` error when only `A` has `foo`?

**4. Stretch.** Add an exhaustiveness guard with `never` to your `describe` function. Then add a `"blur"` variant and verify the compiler catches the missing case.

**5. Stretch++.** Use `Extract` to pull the `"click"` variant out of `Event` into its own type `ClickEvent`. Use `Exclude` to get all non-click events.

<details><summary>Solutions</summary>

**1.**
```ts
type Id = number | string;

function printId(id: Id): void {
  if (typeof id === "number") {
    console.log(`Numeric ID: ${id.toFixed(0)}`);
  } else {
    console.log(`String ID: ${id.toUpperCase()}`);
  }
}
```

**2.**
```ts
type Event =
  | { type: "click"; x: number; y: number }
  | { type: "keypress"; key: string }
  | { type: "focus" };

function describe(e: Event): string {
  switch (e.type) {
    case "click":    return `Click at (${e.x}, ${e.y})`;
    case "keypress": return `Key: ${e.key}`;
    case "focus":    return "Focused";
  }
}
```

**3.** Because `x` is `A | B`, TypeScript only allows access to members common to both. `foo` only exists on `A`, so you must narrow first: `if ("foo" in x) x.foo();`.

**4.** Add `default: { const _: never = e; return _; }` to the switch. After adding `"blur"`, the compiler reports that `{ type: "blur" }` isn't assignable to `never`.

**5.**
```ts
type ClickEvent = Extract<Event, { type: "click" }>;
type NonClickEvent = Exclude<Event, { type: "click" }>;
```

</details>

## Quiz

1. A union type `A | B` means:
   (a) Intersection of A and B  (b) The value is one of these types  (c) Both A and B simultaneously  (d) A compile error

2. Narrowing via `typeof`:
   (a) Runtime-only  (b) Both compile-time and runtime; TypeScript reads the check  (c) Only comments  (d) Deprecated

3. A discriminated union requires:
   (a) A shared literal field across all variants  (b) A class hierarchy  (c) The `in` operator  (d) Identical shapes

4. The exhaustiveness trick with `never`:
   (a) Is impossible  (b) Assigns the remaining variable to a `never`-typed const to force a compile error  (c) Works only at runtime  (d) Requires `assert`

5. `Exclude<A | B | C, B>` returns:
   (a) `B`  (b) `A | C`  (c) `A | B | C`  (d) `A & C`

**Short answer:**

6. Why are discriminated unions better than stringly-typed status fields?
7. When is `Extract` useful?

*Answers: 1-b, 2-b, 3-a, 4-b, 5-b. 6 — Discriminated unions restrict values to a known set of literals, enable exhaustive switch statements, and give you per-variant type narrowing. A plain `string` accepts any value and provides no narrowing. 7 — When you need to pull specific variants out of a large union, e.g., extracting the "click" event type from an events union for a specialized handler.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-unions — mini-project](mini-projects/03-unions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Union types represent "one of" — the value is one of several possible types.
- Narrow with `typeof`, `in`, `instanceof`, or a discriminant field to access variant-specific members.
- Discriminated unions with a shared literal tag are the most powerful pattern for modeling sum types.
- Assign unhandled cases to `never` to get compile-time exhaustiveness checks.

## Further reading

- [TypeScript Handbook — Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook — Everyday Types: Union Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#union-types)
- Next: [Arrays](04-arrays.md)
