# Chapter 09 — Enums

> "TypeScript enums exist. They're also a little weird. Most of the time, a union of string literals is a better choice."

## Learning objectives

By the end of this chapter you will be able to:

- Declare numeric and string enums and explain their runtime behavior.
- Use `const enum` and understand why many teams disable it.
- Prefer literal unions and `as const` objects for new code.
- Choose the right enumeration pattern for your use case.

## Prerequisites & recap

- [Chapter 01 — Types](01-types.md) — primitives, literal types.
- [Chapter 03 — Unions](03-unions.md) — literal unions, narrowing.

## The simple version

An enum is a way to give friendly names to a fixed set of values. TypeScript offers `enum` as a keyword, but unlike most TypeScript features, enums generate *runtime code* — they're not just types that get erased. This makes them unusual in the TypeScript world, and many teams prefer the simpler alternative: literal unions like `"pending" | "shipped" | "delivered"`.

The modern TypeScript convention is to reach for literal unions by default and only use `enum` when you're working with legacy code or need specific features like reverse mapping.

## In plain terms (newbie lane)

This chapter is really about **Enums**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Source: enum Direction { Up, Down, Left, Right }

  Compiled JS (runtime object):
  ┌──────────────────────────────────┐
  │  Direction[0] = "Up"             │  ← reverse mapping
  │  Direction["Up"] = 0             │  ← forward mapping
  │  Direction[1] = "Down"           │
  │  Direction["Down"] = 1           │
  │  ...                             │
  └──────────────────────────────────┘

  Source: type Direction = "up" | "down" | "left" | "right"

  Compiled JS:
  ┌──────────────────────────────────┐
  │  (nothing — type is erased)      │
  └──────────────────────────────────┘
```
*Figure 9-1. Enums emit runtime objects; literal unions emit nothing.*

## Concept deep-dive

### Numeric enums

```ts
enum Direction { Up, Down, Left, Right }
// Up = 0, Down = 1, Left = 2, Right = 3

let d: Direction = Direction.Up;
```

Numeric enums have *reverse mappings*: `Direction[0] === "Up"`. They emit a runtime object with both forward and reverse lookups.

Why are numeric enums risky? Because values depend on declaration order. If someone inserts `Neutral` between `Up` and `Down`, every subsequent value shifts — and any stored `1` now means `Neutral` instead of `Down`. This is a silent data corruption bug.

### String enums

```ts
enum Status {
  Pending   = "pending",
  Shipped   = "shipped",
  Delivered = "delivered",
}
```

String enums are safer — values are explicit and self-describing. They don't have reverse mappings. The emitted runtime object maps `Status.Pending` to `"pending"`.

### `const enum`

```ts
const enum LogLevel { Info, Warn, Error }
log(LogLevel.Info);    // inlined to log(0) — no runtime object
```

`const enum` inlines values at compile time, producing no runtime object. But it has problems:

- Breaks with `isolatedModules: true` (required by most bundlers).
- Can't be used across module boundaries in some setups.
- Many codebases ban it via `@typescript-eslint/no-enum`.

### The alternative: literal unions

```ts
type Status = "pending" | "shipped" | "delivered";

function transition(current: Status, next: Status): void {
  // ...
}
```

Advantages over enums:

- **No runtime object emitted** — purely a type, erased at compile time.
- **Works seamlessly with JSON** — the values are plain strings, no mapping needed.
- **Composable** — you can use `Exclude`, `Extract`, and other utility types on unions.
- **No reordering bugs** — values are explicit strings, not positions.

Disadvantage: no `Status.Pending` IntelliSense namespace. You type the literal directly. In practice, editors autocomplete string literals from union types.

### The `as const` object pattern

If you want both a runtime object (for iteration) and a literal-union type:

```ts
const Status = {
  Pending:   "pending",
  Shipped:   "shipped",
  Delivered: "delivered",
} as const;

type Status = (typeof Status)[keyof typeof Status];
// "pending" | "shipped" | "delivered"
```

This gives you the best of both worlds: `Status.Pending` for IntelliSense, `Object.values(Status)` for iteration, and the derived union type for parameter annotations. Many teams prefer this to `enum`.

### When to use `enum`

- Interop with legacy C/Java APIs that use integer constants.
- Working in a codebase that already uses enums consistently.
- You need reverse mapping (numeric only).

Otherwise, prefer literal unions or the `as const` pattern.

## Why these design choices

**Why do enums emit runtime code?** Because TypeScript was designed to be a superset of JavaScript, and enums provide a convenient namespace object at runtime. This was a reasonable choice in 2012, but modern TypeScript has better alternatives.

**Why do many teams avoid enums?** Three reasons: (1) they're the *only* TypeScript feature that generates code you didn't write, which surprises developers who expect TypeScript to be "types that erase"; (2) numeric enums are fragile to reordering; (3) `const enum` has bundler compatibility issues.

**When would you pick differently?** If your team already uses enums and has conventions to avoid the pitfalls (always use string values, never reorder), there's no urgent reason to refactor. But for new code, literal unions and `as const` are simpler and safer.

## Production-quality code

```ts
const HttpMethod = {
  Get:    "GET",
  Post:   "POST",
  Put:    "PUT",
  Patch:  "PATCH",
  Delete: "DELETE",
} as const;

type HttpMethod = (typeof HttpMethod)[keyof typeof HttpMethod];

const OrderStatus = {
  Pending:   "pending",
  Confirmed: "confirmed",
  Shipped:   "shipped",
  Delivered: "delivered",
  Canceled:  "canceled",
} as const;

type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];

function isOrderStatus(value: unknown): value is OrderStatus {
  return (
    typeof value === "string" &&
    (Object.values(OrderStatus) as string[]).includes(value)
  );
}

function transitionOrder(current: OrderStatus, next: OrderStatus): void {
  const allowed: Record<OrderStatus, readonly OrderStatus[]> = {
    [OrderStatus.Pending]:   [OrderStatus.Confirmed, OrderStatus.Canceled],
    [OrderStatus.Confirmed]: [OrderStatus.Shipped, OrderStatus.Canceled],
    [OrderStatus.Shipped]:   [OrderStatus.Delivered],
    [OrderStatus.Delivered]: [],
    [OrderStatus.Canceled]:  [],
  };

  if (!allowed[current].includes(next)) {
    throw new Error(`Cannot transition from ${current} to ${next}`);
  }
}
```

## Security notes

- **Validate enum values from external input.** An API might send `"admin_override"` as a status value. Don't assume the incoming string matches your enum. Write a runtime guard like `isOrderStatus` above.
- **Numeric enums are especially dangerous from external input** — accepting arbitrary numbers without validation means any integer is "valid."

## Performance notes

N/A — Both enums and literal unions have negligible runtime cost. The `as const` pattern creates a small frozen object, which is a one-time allocation. The runtime performance difference between patterns is unmeasurable.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Inserting a new member in a numeric enum breaks stored values | Values depend on declaration order | Use string enums or literal unions with explicit values |
| 2 | `const enum` breaks with bundler (`isolatedModules`) | `const enum` requires non-isolated compilation | Switch to `as const` object or regular string enum |
| 3 | Relying on reverse mapping with string enums | String enums don't have reverse mappings | Use `Object.entries()` on an `as const` object instead |
| 4 | Using enums for feature flags | String-to-boolean mapping is clearer with a plain object | Use `Record<string, boolean>` or a literal union |

## Practice

**1. Warm-up.** Declare a `Direction` numeric enum and print every member's name and value.

**2. Standard.** Refactor `enum Status { Pending = "pending", Shipped = "shipped", Delivered = "delivered" }` to a literal union + `as const` map.

**3. Bug hunt.** Why might shipping a numeric enum break when you insert a new member between existing ones?

**4. Stretch.** Write a type guard `isStatus(x: unknown): x is Status` that works with the `as const` pattern.

**5. Stretch++.** Compare the compiled JavaScript output of (a) a numeric enum, (b) a string enum, and (c) an `as const` object. Which emits the smallest code?

<details><summary>Solutions</summary>

**1.**
```ts
enum Direction { Up, Down, Left, Right }
for (const key of Object.keys(Direction).filter(k => isNaN(Number(k)))) {
  console.log(`${key} = ${Direction[key as keyof typeof Direction]}`);
}
```

**2.**
```ts
const Status = {
  Pending:   "pending",
  Shipped:   "shipped",
  Delivered: "delivered",
} as const;

type Status = (typeof Status)[keyof typeof Status];
```

**3.** Numeric enum values are assigned based on position (0, 1, 2, ...). Inserting a new member shifts all subsequent values. Any stored integer now maps to a different meaning — silent data corruption.

**4.**
```ts
function isStatus(x: unknown): x is Status {
  return typeof x === "string" &&
    (Object.values(Status) as string[]).includes(x);
}
```

**5.** The `as const` object emits the smallest code — just a plain object literal. String enums emit an IIFE with assignments. Numeric enums emit an IIFE with both forward and reverse mappings.

</details>

## Quiz

1. Numeric enums start at:
   (a) 0  (b) 1  (c) undefined  (d) -1

2. String enums have reverse mappings:
   (a) Yes  (b) No  (c) Only with `strict`  (d) With a helper function

3. `const enum`:
   (a) Emits a runtime object  (b) Inlines values at compile time  (c) Is deprecated  (d) Only works with classes

4. For API state values, prefer:
   (a) Numeric enum  (b) String enum or literal union  (c) Symbols  (d) Booleans

5. `as const` map + derived union gives:
   (a) Nothing useful  (b) Runtime object + literal-union type  (c) Only a type  (d) Only works for arrays

**Short answer:**

6. Why do numeric enums fail when members are reordered?
7. Give one reason to still use `enum` in a modern codebase.

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b. 6 — Values are assigned by position (0, 1, 2...). Reordering or inserting changes the value-to-name mapping, breaking any stored or serialized integer values. 7 — When working with legacy code that already uses enums consistently, or when interoperating with C/Java APIs that expect integer constants with reverse mapping.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-enums — mini-project](mini-projects/09-enums-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Numeric enums are fragile — values depend on declaration order and are prone to reordering bugs.
- String enums are safer but still emit runtime code.
- Literal unions (`"a" | "b"`) and `as const` objects are the modern alternative — simpler, JSON-friendly, and composable.
- Reserve `enum` for legacy interop or codebases already committed to the pattern.

## Further reading

- [TypeScript Handbook — Enums](https://www.typescriptlang.org/docs/handbook/enums.html)
- [Matt Pocock — Enums considered harmful](https://www.totaltypescript.com/concepts/enums)
- Next: [Type Narrowing](10-type-narrowing.md)
