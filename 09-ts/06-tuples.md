# Chapter 06 — Tuples

> "Tuples are arrays with a fixed length and a known type per position. Handy when returning a pair of values or modeling a positional record."

## Learning objectives

By the end of this chapter you will be able to:

- Declare tuples with per-position types and labeled elements.
- Use `readonly` tuples and `as const` for literal inference.
- Destructure tuples safely.
- Know when a tuple is the right choice — and when a named object is better.

## Prerequisites & recap

- [Chapter 04 — Arrays](04-arrays.md) — `T[]`, `readonly`, `noUncheckedIndexedAccess`.

## The simple version

An array says "a list of values, all the same type." A tuple says "a fixed number of values, each with its own type." Think of a tuple as a lightweight, unnamed struct where position determines meaning. When you write `[string, number]`, you're saying "exactly two elements: the first is a string, the second is a number."

Tuples are great for small returns (like React's `useState` returning `[value, setter]`) but become unclear when you have more than two or three elements. At that point, a named object with labeled fields reads better.

## In plain terms (newbie lane)

This chapter is really about **Tuples**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  tuple: [string, number]
  ┌─────────┬─────────┐
  │  [0]    │  [1]    │
  │ string  │ number  │
  │ "Ada"   │  36     │
  └─────────┴─────────┘
       ▲         ▲
       │         │
  destructured:  │
  const [name, age] = pair;
```
*Figure 6-1. Tuples fix both length and type per position.*

## Concept deep-dive

### Basic tuples

```ts
const pair: [string, number] = ["Ada", 36];
const [name, age] = pair;   // name: string, age: number
```

Length and type per position are fixed. Extra elements and out-of-bounds access are compile errors:

```ts
const p: [string, number] = ["Ada", 36, true];   // error: too many elements
pair[2];                                           // error: no element at index 2
```

### Labeled elements

Labels are purely documentation — they don't affect the type system — but they dramatically improve readability:

```ts
type HttpEntry = [method: string, path: string, status: number];
```

Without labels, a reader seeing `[string, string, number]` has to guess what each position means. With labels, the intent is clear.

### Readonly tuples

```ts
const pair: readonly [string, number] = ["Ada", 36];
pair[0] = "Bob";  // error: cannot assign to readonly tuple
```

Same concept as `readonly` arrays — prevents mutation through this reference.

### Optional and rest elements

Tuples can have optional trailing elements and rest elements:

```ts
type Named = [first: string, last?: string];
type AtLeastOne = [first: string, ...rest: string[]];
```

Rest elements let you model "one or more" patterns while keeping the first position strongly typed.

### `as const` — literal tuple inference

By default, TypeScript infers `[1, "a"]` as `(string | number)[]` — a mutable array of the union. To get a tuple:

```ts
const xs = [1, "a"] as const;   // readonly [1, "a"]
```

`as const` pins both the length and the literal values. The resulting type is `readonly [1, "a"]` — not just `[number, string]`, but specifically `[1, "a"]`. This is invaluable for configuration objects and constant lists.

### When to use tuples

Use tuples for:

- **Small positional returns** like `[value, setter]`, `[error, result]`.
- **Heterogeneous pairs** in function signatures (e.g., `[key, value]` from `Object.entries`).
- **Fixed-shape data** from wire formats where position is meaningful.

Avoid tuples when:

- **Named properties would be clearer.** `{ lat: number; lng: number }` beats `[number, number]` for readability.
- **More than 3 elements.** Positional semantics become confusing.
- **Elements might grow.** If the structure evolves, a tuple's positional contract makes refactoring harder.

## Why these design choices

**Why separate tuples from arrays?** Because they solve different problems. Arrays model *collections* of uniform elements. Tuples model *records* where position carries meaning. Without tuples, you'd use objects for everything — which is verbose for simple pairs — or arrays with union types — which loses per-position type information.

**Why is `as const` needed?** TypeScript defaults to widening: `[1, "a"]` becomes `(string | number)[]` because mutable arrays might have elements pushed or replaced. `as const` signals "this value won't change," so TypeScript can narrow to the exact shape. It's an explicit opt-in because immutability is the exception in JavaScript, not the rule.

**When would you pick differently?** For more than two or three values, always prefer a named object. For single returns, just return the value directly. Tuples sit in the sweet spot of "I need exactly two or three typed values, and creating an object for that feels heavy."

## Production-quality code

```ts
function swap<A, B>(pair: readonly [A, B]): [B, A] {
  return [pair[1], pair[0]];
}

function zip<A, B>(
  as: readonly A[],
  bs: readonly B[],
): [A, B][] {
  const len = Math.min(as.length, bs.length);
  const result: [A, B][] = [];
  for (let i = 0; i < len; i++) {
    result.push([as[i]!, bs[i]!]);
  }
  return result;
}

function unzip<A, B>(pairs: readonly (readonly [A, B])[]): [A[], B[]] {
  const as: A[] = [];
  const bs: B[] = [];
  for (const [a, b] of pairs) {
    as.push(a);
    bs.push(b);
  }
  return [as, bs];
}

function enumerate<T>(xs: readonly T[]): [index: number, value: T][] {
  return xs.map((x, i) => [i, x]);
}
```

## Security notes

N/A — Tuple types are erased at compile time and have no runtime representation. Security concerns around data validation apply to the underlying values, not to the tuple structure.

## Performance notes

N/A — Tuples are plain JavaScript arrays at runtime. There's no performance difference between `[string, number]` and `Array<string | number>` — they're both just arrays. The distinction is purely in the type system.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Using a tuple when a small object would read better | Positional semantics are unclear for 3+ elements | Refactor to a named object: `{ lat: number; lng: number }` |
| 2 | `[1, "a"]` infers as `(string \| number)[]` instead of a tuple | TypeScript widens to mutable array by default | Use `as const` or an explicit type annotation |
| 3 | Tuple length drift after refactor | Added or removed an element but didn't update all destructuring sites | TypeScript catches this — read the compile errors |
| 4 | Forgetting `readonly` on tuple parameters | Allows callers' tuples to be mutated | Use `readonly [A, B]` for function params |

## Practice

**1. Warm-up.** Write a function that returns `[width: number, height: number]` and destructure the result.

**2. Standard.** Implement `zip<A, B>(as: A[], bs: B[]): [A, B][]` that pairs elements from two arrays.

**3. Bug hunt.** Why does `const xs = [1, "a"]` infer `(string | number)[]` instead of `[number, string]`? How do you fix it?

**4. Stretch.** Define a `Point3D` tuple with labels: `[x: number, y: number, z: number]`. Write a `distance` function between two `Point3D` values.

**5. Stretch++.** Refactor a function that returns a 4-element tuple into one that returns a named object. Compare the readability at call sites.

<details><summary>Solutions</summary>

**1.**
```ts
function dimensions(): [width: number, height: number] {
  return [1920, 1080];
}
const [w, h] = dimensions();
```

**2.**
```ts
function zip<A, B>(as: A[], bs: B[]): [A, B][] {
  const len = Math.min(as.length, bs.length);
  const result: [A, B][] = [];
  for (let i = 0; i < len; i++) {
    result.push([as[i]!, bs[i]!]);
  }
  return result;
}
```

**3.** Without `as const`, TypeScript widens to a mutable array of the union. Fix: `const xs = [1, "a"] as const` gives `readonly [1, "a"]`, or annotate: `const xs: [number, string] = [1, "a"]`.

**4.**
```ts
type Point3D = [x: number, y: number, z: number];

function distance(a: Point3D, b: Point3D): number {
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}
```

**5.** Before: `function parse(): [name: string, age: number, email: string, role: string]`
After: `function parse(): { name: string; age: number; email: string; role: string }`
The object version is clearer at call sites: `result.email` vs. `result[2]`.

</details>

## Quiz

1. A tuple type is:
   (a) A fixed-length typed array  (b) An object  (c) A generic  (d) Arrays only

2. Out-of-bounds index on a tuple under `strict`:
   (a) Returns `any`  (b) Compile error  (c) Returns `undefined` silently  (d) Runtime error only

3. Labels on tuple elements are:
   (a) Enforced at runtime  (b) Documentation only  (c) Part of the type identity  (d) Banned in strict mode

4. `as const` on `[1, "a"]` produces:
   (a) `readonly [1, "a"]` (literal tuple)  (b) Runtime `Object.freeze`  (c) Same as `[number, string]`  (d) A compile error

5. Prefer a tuple over an object when:
   (a) Always  (b) The pairing is idiomatic (e.g., `[value, setter]`)  (c) You have many fields  (d) The data is nested

**Short answer:**

6. Why use labels on tuple elements if they're erased?
7. Give one case where a tuple is clearly better than an object.

*Answers: 1-a, 2-b, 3-b, 4-a, 5-b. 6 — Labels improve readability in tooltips, documentation, and code review. They help humans understand what each position means without reading the implementation. 7 — React's `useState` returns `[value, setter]` — the positional contract is universally understood, and destructuring with custom names (`const [count, setCount] = ...`) is more ergonomic than object destructuring.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-tuples — mini-project](mini-projects/06-tuples-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Tuples fix both length and per-position type, unlike arrays which are uniform.
- Labels and `as const` improve readability and literal type precision.
- Use tuples for small positional returns (2-3 elements); prefer named objects for anything larger.
- `readonly` tuples prevent mutation through the typed reference.

## Further reading

- [TypeScript Handbook — Object Types: Tuple Types](https://www.typescriptlang.org/docs/handbook/2/objects.html#tuple-types)
- [TypeScript Handbook — `const` assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#literal-inference)
- Next: [Intersections](07-intersections.md)
