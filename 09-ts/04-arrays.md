# Chapter 04 — Arrays

> "Arrays carry their element type through every operation. Read the type, not just the value."

## Learning objectives

By the end of this chapter you will be able to:

- Type arrays with `T[]` and `Array<T>` and explain why both exist.
- Use `readonly` arrays to communicate and enforce immutability contracts.
- Type `map`, `filter`, and `reduce` correctly, including tricky accumulator inference.
- Enable `noUncheckedIndexedAccess` and handle the resulting `T | undefined`.

## Prerequisites & recap

- [Chapter 01 — Types](01-types.md) — primitives, inference.
- [Module 08 — JS Arrays](../08-js/08-arrays.md) — `map`, `filter`, `reduce`, destructuring, spread.

## The simple version

In TypeScript, an array isn't just "a list of stuff" — it's "a list of stuff *of a specific type*." When you write `number[]`, every element must be a number, and every operation that produces elements gives you numbers back. This means `map`, `filter`, `reduce`, and indexing all carry the type through, so the compiler can catch mistakes like trying to call `.toUpperCase()` on a number you pulled out of an array.

The key insight is that array indexing is *unsafe by default* — `arr[10]` on a five-element array returns `undefined` at runtime, but TypeScript says the type is `T`, not `T | undefined`. The `noUncheckedIndexedAccess` flag fixes this, and you should always enable it.

## In plain terms (newbie lane)

This chapter is really about **Arrays**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌─────────┐    .map(f)    ┌─────────┐
  │  T[]    │──────────────▶│  U[]    │
  └─────────┘               └─────────┘

  ┌─────────┐   .filter(p)  ┌─────────┐
  │  T[]    │──────────────▶│  T[]    │
  └─────────┘               └─────────┘

  ┌─────────┐  .reduce(f,i) ┌─────────┐
  │  T[]    │──────────────▶│    U    │  (scalar)
  └─────────┘               └─────────┘
```
*Figure 4-1. Array operations preserve and transform element types.*

## Concept deep-dive

### Two syntaxes, same meaning

```ts
const nums: number[] = [1, 2, 3];
const strs: Array<string> = ["a", "b"];
```

Both are identical. `number[]` is syntactic sugar for `Array<number>`. Pick one style per codebase and stick with it.

### `readonly` arrays — communicating intent

```ts
function sum(xs: readonly number[]): number {
  return xs.reduce((a, b) => a + b, 0);
}

const data = [1, 2, 3];
sum(data);   // works — mutable is assignable to readonly
```

Why bother? When you type a parameter as `readonly number[]`, you're making two promises: to callers ("I won't mutate your array") and to future maintainers ("don't add `.push()` calls here"). The compiler enforces both — `xs.push(4)` inside `sum` would be a compile error.

`readonly` is a *compile-time contract*, not a runtime freeze. The underlying array is still mutable through other references. But the type system prevents accidental mutation through *this* reference, which is usually enough.

### `map`, `filter`, `reduce` — typed

```ts
const lengths: number[] = ["a", "bc"].map(s => s.length);
const evens = [1, 2, 3].filter(n => n % 2 === 0);      // number[]
const total = [1, 2, 3].reduce<number>((acc, n) => acc + n, 0);
```

Why does `reduce` sometimes need an explicit generic? When the accumulator's initial value has a different type than the elements, or when the initial value is `[]` (which infers as `never[]`), TypeScript can't determine the accumulator type. Passing the generic — `reduce<number>(...)` — resolves the ambiguity.

### `noUncheckedIndexedAccess` — closing the safety gap

Without this flag, `arr[i]` returns `T` even when `i` might be out of bounds. With it, `arr[i]` returns `T | undefined`:

```ts
const arr = ["a", "b", "c"];
const first = arr[0];   // string | undefined (with flag on)
if (first !== undefined) {
  console.log(first.toUpperCase());  // safe
}
```

This flag prevents the classic "silent undefined" bug where you access an out-of-bounds index and get `undefined` that propagates silently until something explodes downstream. Enable it in every project.

### Destructuring preserves types

```ts
const [a, b, ...rest] = [1, 2, 3, 4];
//    ^number ^number  ^number[]
```

### Spread creates new arrays

```ts
const extra: number[] = [0, ...nums, 4];
```

Spread infers the union of all source element types.

### Mixed arrays infer unions

```ts
const mixed = [1, "a"];   // (string | number)[]
```

TypeScript widens to the union of all element types. If you want a tuple instead, use `as const` (see [Chapter 06](06-tuples.md)).

## Why these design choices

**Why `readonly` instead of `Immutable`?** TypeScript's `readonly` is shallow and compile-time only. A deep-freeze utility would require runtime overhead and recursive type gymnastics. The shallow, compile-time approach catches 90% of accidental mutation bugs with zero runtime cost.

**Why isn't `noUncheckedIndexedAccess` the default?** Backward compatibility. Enabling it would break millions of lines of existing TypeScript code. But for new projects, it's a clear win — the `T | undefined` it produces forces you to handle the "element might not exist" case that JavaScript silently ignores.

**When would you pick differently?** If you're working with fixed-size collections where each position has a different type, use a tuple (`[string, number]`) instead of an array. If you need truly immutable data structures with structural sharing, reach for a library like Immer.

## Production-quality code

```ts
function chunk<T>(items: readonly T[], size: number): T[][] {
  if (size <= 0) throw new RangeError("chunk size must be positive");

  const result: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    result.push(items.slice(i, i + size));
  }
  return result;
}

function unique<T>(items: readonly T[]): T[] {
  return [...new Set(items)];
}

function firstOrDefault<T>(items: readonly T[], fallback: T): T {
  const first = items[0];  // T | undefined with noUncheckedIndexedAccess
  return first ?? fallback;
}

function groupBy<T, K extends string | number>(
  items: readonly T[],
  keyFn: (item: T) => K,
): Record<K, T[]> {
  const result = {} as Record<K, T[]>;
  for (const item of items) {
    const key = keyFn(item);
    (result[key] ??= []).push(item);
  }
  return result;
}
```

## Security notes

N/A — Array typing is a compile-time concern. However, if you're accepting arrays from external input (API bodies, query params), always validate the element types at runtime. TypeScript's `string[]` annotation won't stop someone from sending `[1, true, null]`.

## Performance notes

- **`readonly` has zero runtime cost** — it's erased at compile time.
- **Spread (`[...arr]`)** creates a shallow copy: O(n) time and memory. Avoid in hot loops on large arrays.
- **`reduce` vs. `for` loop** — functionally equivalent in performance for most cases. Use whichever reads better.
- **`noUncheckedIndexedAccess`** adds no runtime overhead — it only changes the type, not the code.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Accidentally mutating a parameter array | Parameter typed as `T[]` instead of `readonly T[]` | Use `readonly T[]` for params you don't intend to mutate |
| 2 | `reduce` infers accumulator as `never[]` | Empty initial array `[]` with no generic hint | Pass the generic: `.reduce<string[]>((acc, x) => ..., [])` |
| 3 | Silent `undefined` from out-of-bounds access | `noUncheckedIndexedAccess` not enabled | Enable the flag; handle `T \| undefined` at access sites |
| 4 | `Array(3)` creates sparse array, not `[undefined, undefined, undefined]` | `Array` constructor with a single number creates holes | Use `Array.from({ length: 3 })` or `[undefined, undefined, undefined]` |
| 5 | Type mismatch after `.filter()` with type guard | `.filter(Boolean)` doesn't narrow the type | Use `.filter((x): x is NonNullable<T> => x != null)` |

## Practice

**1. Warm-up.** Write `unique<T>(xs: readonly T[]): T[]` that returns an array with duplicates removed.

**2. Standard.** Write `chunk<T>(xs: readonly T[], size: number): T[][]` that splits an array into sub-arrays of the given size.

**3. Bug hunt.** Why does `[].reduce((acc, x) => [...acc, x])` sometimes infer the accumulator as `never[]`?

**4. Stretch.** Enable `noUncheckedIndexedAccess` in a project and refactor one file to handle all the resulting `T | undefined` values.

**5. Stretch++.** Write an immutable push: `append<T>(xs: readonly T[], x: T): readonly T[]` that returns a new array. Verify that the caller can't mutate the result through the return type.

<details><summary>Solutions</summary>

**1.**
```ts
function unique<T>(xs: readonly T[]): T[] {
  return [...new Set(xs)];
}
```

**2.**
```ts
function chunk<T>(xs: readonly T[], size: number): T[][] {
  const result: T[][] = [];
  for (let i = 0; i < xs.length; i += size) {
    result.push(xs.slice(i, i + size));
  }
  return result;
}
```

**3.** No initial value and no items means TypeScript can't determine the element type, so the accumulator infers as `never[]`. Fix: provide an initial value with a type annotation or pass the generic: `.reduce<T[]>((acc, x) => [...acc, x], [])`.

**4.** After enabling, every `arr[i]` becomes `T | undefined`. Fix with `if (item !== undefined)` guards, nullish coalescing (`??`), or non-null assertion (`!`) when you're provably safe.

**5.**
```ts
function append<T>(xs: readonly T[], x: T): readonly T[] {
  return [...xs, x];
}
```

</details>

## Quiz

1. `readonly T[]` means:
   (a) Can't be mutated through this reference  (b) Immutable at runtime via `Object.freeze`  (c) Shallow freeze  (d) Same as `T[]`

2. `arr[0]` with `noUncheckedIndexedAccess` enabled returns:
   (a) `T`  (b) `T | undefined`  (c) `any`  (d) `never`

3. For function parameters you won't mutate, prefer:
   (a) `T[]`  (b) `readonly T[]`  (c) `Array<T>`  (d) `T`

4. `reduce` accumulator type often needs:
   (a) Nothing special  (b) An explicit generic when initial value differs from element type  (c) `as any`  (d) A class wrapper

5. `[1, "a"]` infers as:
   (a) `any[]`  (b) `(number | string)[]`  (c) A compile error  (d) `unknown[]`

**Short answer:**

6. Why should you enable `noUncheckedIndexedAccess`?
7. When (if ever) is it acceptable to cast `readonly T[]` to `T[]`?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b. 6 — It forces you to handle the case where an index might be out of bounds, preventing silent `undefined` propagation that causes downstream crashes. 7 — Almost never. The only legitimate case is when interfacing with a library that requires a mutable array type but promises not to mutate it. Even then, prefer spreading into a new array.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-arrays — mini-project](mini-projects/04-arrays-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Arrays are typed: `T[]` or `Array<T>`, with `readonly T[]` for immutability contracts.
- `noUncheckedIndexedAccess` closes the most dangerous gap in array typing — enable it always.
- `reduce` often needs explicit generics when the accumulator type differs from elements.
- `readonly` is compile-time only, zero cost, and communicates intent clearly.

## Further reading

- [TypeScript Handbook — Everyday Types: Arrays](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#arrays)
- [TypeScript `noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess)
- Next: [Objects](05-objects.md)
