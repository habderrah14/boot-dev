# Chapter 02 — Functions

> "Typing functions well is the highest-leverage thing you can do in TypeScript — signatures are contracts the rest of the codebase depends on."

## Learning objectives

By the end of this chapter you will be able to:

- Annotate function parameters and return types.
- Use optional, default, and rest parameters correctly.
- Write function type aliases and higher-order function signatures.
- Distinguish `void`, `never`, and `undefined` as return types.
- Use overloads when a single signature can't express the contract.

## Prerequisites & recap

- [Chapter 01 — Types](01-types.md) — primitive types, inference, `tsconfig.json`.
- [Module 08 — JS Functions](../08-js/03-functions.md) — arrow functions, closures, rest parameters.

## The simple version

A function signature is a contract. It tells callers "give me *these* types, and I promise to give you back *that* type." TypeScript enforces that contract at every call site, so if someone passes a string where you expected a number, the compiler catches it before the code ever runs.

You should always annotate parameters (the compiler can't guess what callers will pass) and annotate the return type on any function that's exported or non-trivial. Inside the body, let inference do its job — TypeScript can figure out what `a + b` produces without your help.

## In plain terms (newbie lane)

This chapter is really about **Functions**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  caller code          signature              function body
  ───────────       ───────────────         ─────────────────
                   ┌───────────────┐
  add(2, 3)  ────▶ │ (a: number,   │ ────▶  return a + b;
                   │  b: number)   │              │
                   │    : number   │ ◀────────────┘
                   └───────────────┘        inferred: number
                         │
                    type-checked at
                     every call site
```
*Figure 2-1. The signature sits between caller and body, enforcing the contract both ways.*

## Concept deep-dive

### Parameters and return types

```ts
function add(a: number, b: number): number {
  return a + b;
}

const mul = (a: number, b: number): number => a * b;
```

Why annotate the return type? When the body is non-trivial, the annotation documents your intent *and* guards against accidental drift. Without it, a refactor that changes the return statement might silently change the inferred type, and callers won't notice until something breaks far downstream.

### Optional parameters

```ts
function greet(name: string, title?: string): string {
  return title ? `${title} ${name}` : name;
}
```

Optional parameters have type `T | undefined`. They must come after all required parameters — TypeScript enforces this because JavaScript's positional argument semantics make leading optionals ambiguous.

### Default parameters

```ts
function greetOrWorld(name: string = "world"): string {
  return `hi, ${name}`;
}
```

A default parameter is implicitly optional — callers can omit it. The type is inferred from the default value, so you don't need to annotate it.

### Rest parameters

```ts
function sum(...nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0);
}
```

Rest parameters collect remaining arguments into a typed array. They must be the last parameter.

### Function type aliases

```ts
type BinOp = (a: number, b: number) => number;
const add: BinOp = (a, b) => a + b;
```

Function types are *structural* — any function with matching parameter and return types satisfies the alias. This is why you can pass an inline arrow to any callback typed as `BinOp` without declaring that it "implements" anything.

### `void` vs. `undefined`

```ts
function log(msg: string): void {
  console.log(msg);
}
```

`void` means "don't look at the return value." It's subtly different from `undefined`:

- A *function declaration* with return type `void` must not explicitly return a value.
- A *callback typed* as `() => void` is lenient — it accepts functions that return anything, because callers promise to ignore the result. This is why `[1,2,3].forEach(n => n * 2)` works even though the callback returns a number.

### `never` — functions that don't return

A function that always throws or loops forever has return type `never`:

```ts
function fail(msg: string): never {
  throw new Error(msg);
}
```

`never` is the bottom type — it's assignable to everything, and nothing is assignable to it (except `never` itself). This makes it the perfect type for exhaustiveness checks (see [Chapter 03](03-unions.md)).

### Overloads

Sometimes a function has different return types depending on its input:

```ts
function len(x: string): number;
function len(x: unknown[]): number;
function len(x: string | unknown[]): number {
  return x.length;
}
```

The first two lines are *overload signatures* — what callers see. The last is the *implementation signature* — what the body uses. Reach for overloads only when a union in the signature can't express different return types per input; otherwise, a single union signature is simpler.

### Contextual typing — inference at call sites

```ts
[1, 2, 3].map(n => n * 2);      // n is inferred as number
```

TypeScript uses the *target signature* (in this case, `Array<number>.map`) to infer callback parameter types. You don't need to annotate `n: number` — the context provides it. This is why well-typed libraries make your code shorter, not longer.

## Why these design choices

**Why annotate parameters but not locals?** Parameters are the public API of a function — TypeScript can't infer what callers *will* pass, only what they *did* pass. Locals, on the other hand, are always inferred from their initialization.

**Why is `void` lenient for callbacks?** Because JavaScript APIs like `forEach` and `addEventListener` ignore callback return values. If `void` were strict for callbacks, you'd need to wrap every callback with an explicit `return undefined`, which would be noisy and pointless.

**When would you choose differently?** If your function has more than two overloads, consider whether a generic signature or a discriminated-union parameter would be clearer. Overloads are powerful but add cognitive overhead for readers and maintainers.

## Production-quality code

```ts
type Comparator<T> = (a: T, b: T) => number;

function sortBy<T>(
  items: readonly T[],
  compare: Comparator<T>,
): T[] {
  return [...items].sort(compare);
}

function partition<T>(
  items: readonly T[],
  predicate: (item: T) => boolean,
): [pass: T[], fail: T[]] {
  const pass: T[] = [];
  const fail: T[] = [];
  for (const item of items) {
    (predicate(item) ? pass : fail).push(item);
  }
  return [pass, fail];
}

function pipe<A, B, C>(f: (a: A) => B, g: (b: B) => C): (a: A) => C {
  return (a) => g(f(a));
}
```

Notice: `readonly T[]` on input parameters communicates that the function won't mutate your array. The spread in `sortBy` creates a copy because `Array.sort` mutates in place.

## Security notes

- **`any` in parameters is an injection vector.** If an HTTP handler types its request body as `any`, you skip all validation. Type external input as `unknown` and validate with a schema library.
- **Overloads can hide unsafe branches.** If the implementation signature is broader than the overload signatures, you might accept inputs that no overload covers. Always make the implementation signature a proper superset.

## Performance notes

N/A — Function signatures are erased at compile time. The emitted JavaScript is identical to what you'd write by hand. The only performance consideration is the same as plain JavaScript: avoid unnecessary allocations in hot paths (e.g., creating closures inside tight loops).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Exported function's return type silently changes after refactor | Missing explicit return type annotation | Annotate return types on all exported functions |
| 2 | `any` leaks into call sites, disabling checks downstream | Parameter typed as `any` | Type as `unknown` or the specific expected type |
| 3 | `function f(): void { return 42; }` errors, but `cb: () => void` accepts `() => 42` | `void` is strict on declarations, lenient on callback types | Understand the distinction; use `void` deliberately |
| 4 | Overload implementation doesn't match public signatures | Implementation signature incompatible with one or more overload signatures | The implementation must be a superset of all overloads |
| 5 | `Parameter 'x' implicitly has an 'any' type` | Missing annotation on parameter with `strict: true` | Add the type annotation |

## Practice

**1. Warm-up.** Write a typed `square(n: number): number` function that returns `n * n`. Verify the compiler rejects `square("hi")`.

**2. Standard.** Write a function `getEmails(users: { name: string; email: string }[]): string[]` that returns just the email addresses. Add a return type annotation.

**3. Bug hunt.** Why does `function f(): void { return 42; }` fail, but assigning `() => 42` to a variable typed `() => void` works?

**4. Stretch.** Write overloaded `len` signatures for `string`, `Array<T>`, `Set<T>`, and `Map<any, any>`, each returning `number`.

**5. Stretch++.** Implement `compose<A, B, C>(f: (b: B) => C, g: (a: A) => B): (a: A) => C` and verify that `compose(String, Math.abs)(-5)` returns `"5"`.

<details><summary>Solutions</summary>

**1.**
```ts
function square(n: number): number {
  return n * n;
}
```

**2.**
```ts
function getEmails(users: { name: string; email: string }[]): string[] {
  return users.map(u => u.email);
}
```

**3.** A `void` return type on a *function declaration* is strict — it forbids returning a value. But `() => void` as a *callback type* is lenient by design: callers promise to ignore the return, so any function shape fits. This prevents forcing wrappers around callbacks like `forEach`.

**4.**
```ts
function len(x: string): number;
function len<T>(x: T[]): number;
function len<T>(x: Set<T>): number;
function len<K, V>(x: Map<K, V>): number;
function len(x: string | unknown[] | Set<unknown> | Map<unknown, unknown>): number {
  if (typeof x === "string" || Array.isArray(x)) return x.length;
  return x.size;
}
```

**5.**
```ts
function compose<A, B, C>(f: (b: B) => C, g: (a: A) => B): (a: A) => C {
  return (a) => f(g(a));
}
```

</details>

## Quiz

1. Optional parameter syntax:
   (a) `param!`  (b) `param?`  (c) `param: T | null`  (d) `param = null`

2. A function with return type `never`:
   (a) Returns `null`  (b) Never returns (throws or loops forever)  (c) Implicit `any`  (d) Alias for `void`

3. Rest parameter syntax:
   (a) `args[]: T`  (b) `...args: T[]`  (c) `...args: T`  (d) `*args: T`

4. Overloads require:
   (a) Multiple signatures + one implementation  (b) Multiple implementations  (c) An abstract class  (d) `any` return type

5. Contextual typing means:
   (a) The compiler uses the call-site target to infer callback params  (b) Everything is `any`  (c) Parameters are always `unknown`  (d) Types are checked at runtime

**Short answer:**

6. Why annotate return types on exported functions?
7. What's the difference between a `void` return type and returning `undefined`?

*Answers: 1-b, 2-b, 3-b, 4-a, 5-a. 6 — Exported functions are public contracts; an explicit return type documents intent, prevents silent drift, and gives better error messages at the declaration site rather than at distant call sites. 7 — `void` means "ignore the return value"; `undefined` means the function explicitly returns the value `undefined`. A `void`-typed callback can accept any return, while an `undefined`-typed one must return exactly `undefined`.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-functions — mini-project](mini-projects/02-functions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Annotate function parameters and return types at boundaries; let inference cover the body.
- Use `void` for methods whose return value should be ignored; `never` for functions that don't return.
- Overloads express different return types per input, but prefer a union or generic when possible.
- Contextual typing means well-typed libraries make your code shorter, not longer.

## Further reading

- [TypeScript Handbook — More on Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html)
- [TypeScript Handbook — Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
- Next: [Unions](03-unions.md)
