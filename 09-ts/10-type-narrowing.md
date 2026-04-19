# Chapter 10 — Type Narrowing

> "Narrowing is the compiler's super-power: take a broad type, look at control flow, and give you back a tighter type without casts."

## Learning objectives

By the end of this chapter you will be able to:

- Narrow types with `typeof`, `in`, `instanceof`, equality, and truthiness checks.
- Write custom type predicates (`x is T`) for reusable narrowing logic.
- Write assertion functions (`asserts x is T`) for fail-fast validation.
- Use exhaustive `never` checks to guarantee all variants are handled.
- Recognize when narrowing is lost (async boundaries, callbacks) and how to work around it.

## Prerequisites & recap

- [Chapter 03 — Unions](03-unions.md) — union types, discriminated unions, `never`.

## The simple version

When you have a value typed as `string | number`, you can't call string methods or number methods on it directly — the compiler doesn't know which one you have. *Narrowing* is how you tell the compiler "I've checked, and it's definitely a string now." You write a regular JavaScript check (like `typeof x === "string"`), and TypeScript reads that check, narrows the type in that branch, and lets you use string methods safely.

The beauty is that these are ordinary runtime checks — the same `typeof` and `instanceof` you'd write in plain JavaScript. TypeScript just *understands* them and adjusts the types accordingly. No special syntax, no runtime overhead, no magic.

## In plain terms (newbie lane)

This chapter is really about **Type Narrowing**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌──────────────────┐
  │   x: A | B | C   │   broad type
  └────────┬─────────┘
           │
    typeof / in / instanceof / === / .kind
           │
  ┌────────┼────────────────┐
  │        │                │
  ▼        ▼                ▼
┌────┐  ┌────┐    ┌─────────────┐
│ A  │  │ B  │    │ C (or never │
│    │  │    │    │ if exhausted)│
└────┘  └────┘    └─────────────┘
```
*Figure 10-1. Each check narrows the type in the corresponding branch.*

## Concept deep-dive

### `typeof` narrowing — primitives

```ts
function pad(x: number | string): string {
  if (typeof x === "number") return x.toFixed(2);   // x: number
  return x.padStart(8, "0");                         // x: string
}
```

TypeScript understands `typeof` checks for `"string"`, `"number"`, `"boolean"`, `"bigint"`, `"symbol"`, `"undefined"`, `"object"`, and `"function"`.

### `in` narrowing — property presence

```ts
type Dog = { bark(): void };
type Cat = { meow(): void };

function speak(a: Dog | Cat): void {
  if ("bark" in a) a.bark();   // a: Dog
  else a.meow();                // a: Cat
}
```

The `in` operator checks whether a property exists on an object. TypeScript uses this to narrow to the variant that has that property.

### `instanceof` narrowing — class instances

```ts
function describe(e: Error | string): string {
  if (e instanceof Error) return e.message;   // e: Error
  return e;                                    // e: string
}
```

### Equality narrowing

```ts
function f(x: string | null): string {
  if (x === null) return "null";
  return x.toUpperCase();   // x: string
}
```

Strict equality (`===`) and inequality (`!==`) narrow types. Loose equality (`==`) also works but narrowing is less precise.

### Truthiness narrowing — use with care

```ts
function len(s: string | undefined): number {
  if (s) return s.length;   // s: string (but empty string is falsy!)
  return 0;
}
```

Truthiness narrows out `null`, `undefined`, `0`, `""`, and `false`. This is dangerous when you need to distinguish between `""` (valid empty string) and `undefined` (missing). When the distinction matters, use explicit checks: `if (s !== undefined)`.

### Discriminated unions (recap from Ch. 03)

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; s: number };

function area(sh: Shape): number {
  switch (sh.kind) {
    case "circle": return Math.PI * sh.r ** 2;
    case "square": return sh.s ** 2;
  }
}
```

The `kind` literal field lets TypeScript narrow the entire object in each `case` branch.

### User-defined type predicates

When built-in checks aren't enough, write a custom predicate:

```ts
interface User {
  id: number;
  name: string;
}

function isUser(x: unknown): x is User {
  return (
    typeof x === "object" && x !== null &&
    "id" in x && typeof (x as Record<string, unknown>).id === "number" &&
    "name" in x && typeof (x as Record<string, unknown>).name === "string"
  );
}
```

After the predicate, callers get narrowing:

```ts
const data: unknown = JSON.parse(raw);
if (isUser(data)) {
  data.name.toUpperCase();   // data: User — safe
}
```

Why not just use `as User`? Because `as` is a lie — it tells the compiler "trust me" without any runtime check. A type predicate actually validates the value and *earns* the narrowing.

### Assertion functions

```ts
function assertIsUser(x: unknown): asserts x is User {
  if (!isUser(x)) throw new Error("Expected a User object");
}

const data: unknown = JSON.parse(raw);
assertIsUser(data);
data.name;   // data: User — narrowed by the assertion
```

Assertion functions narrow by side effect: if they return (don't throw), the variable is narrowed. They're ideal for fail-fast validation at function entry points.

### Exhaustive `never` check

```ts
function area(sh: Shape): number {
  switch (sh.kind) {
    case "circle": return Math.PI * sh.r ** 2;
    case "square": return sh.s ** 2;
    default: {
      const _exhaustive: never = sh;
      return _exhaustive;
    }
  }
}
```

If all variants are handled, `sh` in the default is `never` — the assignment succeeds vacuously. Add a new variant without a case, and the compiler errors because the new variant isn't assignable to `never`.

### Narrowing lost in callbacks and async

```ts
function f(x: number | null) {
  if (x !== null) {
    // x is `number` here
    setTimeout(() => {
      // x is still narrowed to `number` in modern TS (5.x)
      // but in older versions or complex cases, narrowing may be lost
      console.log(x.toFixed(2));
    });
  }
}
```

Modern TypeScript (5.x) narrows through many closures, but for correctness-critical code, re-check inside the callback or capture in a `const`:

```ts
const safe = x;  // const captures the narrowed type
setTimeout(() => console.log(safe.toFixed(2)));
```

## Why these design choices

**Why control-flow analysis instead of special syntax?** TypeScript's narrowing works with the JavaScript checks you'd write anyway — `typeof`, `in`, `instanceof`. No new syntax to learn, no runtime overhead, and the same code works in both TS and JS contexts.

**Why are type predicates `x is T` instead of automatic?** Automatic inference for predicates would require the compiler to prove that your function's logic correctly identifies the type — a hard problem in general. By making you write `x is T`, TypeScript shifts the responsibility to you: you promise the predicate is correct, and the compiler trusts you.

**When would you pick differently?** For complex validation (nested objects, arrays of specific shapes), type predicates become tedious. Use a runtime validation library (Zod, ArkType, Valibot) that generates both the runtime check and the TypeScript type from a single schema definition.

## Production-quality code

```ts
interface ApiResponse {
  status: number;
  data: unknown;
}

interface User {
  id: number;
  name: string;
  email: string;
}

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

function isUser(x: unknown): x is User {
  if (!isRecord(x)) return false;
  return (
    typeof x.id === "number" &&
    typeof x.name === "string" &&
    typeof x.email === "string"
  );
}

function assertIsUser(x: unknown): asserts x is User {
  if (!isUser(x)) {
    throw new TypeError(
      `Expected User, got: ${JSON.stringify(x).slice(0, 100)}`
    );
  }
}

function isArrayOf<T>(
  arr: unknown,
  guard: (x: unknown) => x is T,
): arr is T[] {
  return Array.isArray(arr) && arr.every(guard);
}

async function fetchUsers(url: string): Promise<User[]> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const json: unknown = await res.json();
  if (!isArrayOf(json, isUser)) {
    throw new TypeError("Expected array of users");
  }
  return json;
}
```

## Security notes

- **Type predicates that lie are security holes.** If `isAdmin(x)` returns `true` without actually checking the `role` field, you've granted admin access to any object. Always validate every field in a predicate.
- **Never rely on type narrowing alone for authorization.** TypeScript narrowing is a compile-time concept. Runtime authorization checks must exist independently of the type system.
- **`as` casts bypass narrowing entirely.** Prefer predicates (`x is T`) over casts (`x as T`) for external data. Casts provide zero runtime safety.

## Performance notes

N/A — Narrowing checks are ordinary JavaScript runtime operations (`typeof`, `in`, `instanceof`). Their performance is identical to writing the same checks in plain JavaScript. Type predicates and assertion functions add a function call overhead, but it's negligible.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Narrowing lost after async/await or inside callbacks | TypeScript can't always track narrowing across closure boundaries | Re-check inside the callback or capture in a `const` before the closure |
| 2 | Truthiness check hides `""` (empty string) or `0` | `if (x)` treats empty string and zero as falsy | Use explicit checks: `if (x !== undefined)` or `if (x !== null)` |
| 3 | Type predicate lies — returns `true` without checking all fields | Incomplete validation in the predicate body | Check every required field with `typeof` and `in` |
| 4 | Using `as T` casts instead of narrowing | Quick fix that bypasses type safety | Replace with a type predicate or assertion function |
| 5 | `Property 'foo' does not exist` despite `if (x)` check | `x` has type `{ foo?: () => void } \| null`; truthiness narrows out `null` but `foo` is still optional | Check `x.foo` separately: `if (x && x.foo) x.foo()` |

## Practice

**1. Warm-up.** Narrow a `string | undefined` value using `if (s !== undefined)` and call `.toUpperCase()`.

**2. Standard.** Write an `isUser(x: unknown): x is User` predicate and use it to filter an `unknown[]` into `User[]`.

**3. Bug hunt.** Why does `if (x) x.foo()` error on `x: { foo?: () => void } | null`?

**4. Stretch.** Write `assertIsNumber(x: unknown): asserts x is number` and use it in a function that parses CLI arguments.

**5. Stretch++.** Model a state machine with a discriminated union (`"idle" | "loading" | "success" | "error"`) and an exhaustive `switch`. Add a new state and verify the compiler catches the missing case.

<details><summary>Solutions</summary>

**1.**
```ts
function shout(s: string | undefined): string {
  if (s !== undefined) return s.toUpperCase();
  return "";
}
```

**2.**
```ts
interface User { id: number; name: string }

function isUser(x: unknown): x is User {
  return (
    typeof x === "object" && x !== null &&
    "id" in x && typeof (x as any).id === "number" &&
    "name" in x && typeof (x as any).name === "string"
  );
}

const users: User[] = unknownArray.filter(isUser);
```

**3.** `if (x)` narrows out `null`, so `x` is `{ foo?: () => void }`. But `foo` is optional — it's `(() => void) | undefined`. Calling `x.foo()` fails because `foo` might be `undefined`. Fix: `if (x && x.foo) x.foo()` or `x?.foo()`.

**4.**
```ts
function assertIsNumber(x: unknown): asserts x is number {
  if (typeof x !== "number") {
    throw new TypeError(`Expected number, got ${typeof x}`);
  }
}
```

**5.**
```ts
type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: string }
  | { status: "error"; message: string };

function render(state: State): string {
  switch (state.status) {
    case "idle":    return "Ready";
    case "loading": return "Loading...";
    case "success": return state.data;
    case "error":   return `Error: ${state.message}`;
    default: { const _: never = state; return _; }
  }
}
```

</details>

## Quiz

1. `typeof x === "number"` in an `if` block:
   (a) Narrows `x` to `number` in that block  (b) Only an assertion  (c) Runtime check only, no type narrowing  (d) Deprecated

2. A type predicate `x is T`:
   (a) Is a runtime type check  (b) Is a user-defined narrowing helper  (c) Is a type alias  (d) Is a decorator

3. `asserts x is T`:
   (a) Throws or narrows — if the function returns, `x` is `T`  (b) Runtime only  (c) Compile-time only  (d) Same as `x is T`

4. Truthiness narrowing on empty strings:
   (a) Works correctly  (b) Falls into the "falsy" branch  (c) Causes a compile error  (d) Requires a cast

5. Exhaustive `never` check:
   (a) Lint-only suggestion  (b) Compile-time guarantee that all variants are handled  (c) Runtime-only check  (d) Optional and rarely useful

**Short answer:**

6. Why are type predicates preferable to `as` casts?
7. Give one case where assertion functions are better than type predicates.

*Answers: 1-a, 2-b, 3-a, 4-b, 5-b. 6 — Type predicates perform a runtime check and earn the narrowing; `as` casts skip all validation and lie to the compiler. Predicates catch invalid data at runtime; casts let it through silently. 7 — At function entry points where invalid input should crash immediately: `assertIsUser(data); // rest of function uses data as User`. Assertion functions avoid wrapping the entire function body in an `if`.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-type-narrowing — mini-project](mini-projects/10-type-narrowing-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Narrowing uses ordinary JavaScript checks (`typeof`, `in`, `instanceof`, equality) to refine types within control flow branches.
- Type predicates (`x is T`) let you build reusable narrowing logic for complex shapes.
- Assertion functions (`asserts x is T`) narrow by side effect — if they don't throw, the type is narrowed.
- Exhaustive `never` checks turn missed discriminated union variants into compile errors.

## Further reading

- [TypeScript Handbook — Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook — Type Guards](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)
- Next: [Classes](11-classes.md)
