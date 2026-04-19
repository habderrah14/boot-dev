# Chapter 08 — Arrays

> "Arrays in JavaScript are objects with numeric keys and a `length`. Most of your data manipulation will happen through their method surface."

## Learning objectives

By the end of this chapter you will be able to:

- Create, access, and mutate arrays with confidence.
- Distinguish mutating methods from non-mutating methods and prefer the latter.
- Use the declarative pipeline — `map`, `filter`, `reduce`, `find`, `some`, `every`.
- Use spread, rest, destructuring, and `Array.from` for array construction.
- Sort correctly (always with a comparator for numbers).

## Prerequisites & recap

- [Loops](07-loops.md) — `for...of`, array methods.
- [Objects](04-objects.md) — reference semantics apply to arrays too.

## The simple version

An array is JavaScript's ordered collection — a list of values indexed by position. Under the hood, it's a special object where the keys are numeric indices and there's a magic `length` property. The power of arrays comes from their method surface: over 30 built-in methods for searching, transforming, sorting, and accumulating. The most important distinction to learn is which methods **mutate** the array in place (like `sort`, `push`, `splice`) and which return a **new array** (like `map`, `filter`, `slice`). In modern code, you'll almost always prefer the non-mutating versions — they're safer, easier to debug, and play well with any framework that tracks state changes.

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
  Mutating vs. Non-mutating:

  MUTATING (modify in place)        NON-MUTATING (return new)
  ─────────────────────────         ─────────────────────────
  push / pop                        slice
  unshift / shift                   concat
  splice                            map / filter / reduce
  sort / reverse                    find / findIndex
  fill                              some / every / includes
                                    flat / flatMap
                                    toSorted / toReversed (ES2023)

  Pipeline pattern:
  ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
  │  data  │────>│ filter │────>│  map   │────>│ reduce │──> result
  └────────┘     └────────┘     └────────┘     └────────┘
   (original      (subset)      (transformed)   (single
    unchanged)                                    value)
```

*Figure 8-1. Mutating vs. non-mutating methods and the declarative pipeline.*

## Concept deep-dive

### Creating and accessing

```js
const a = [1, 2, 3];
a[0];             // 1
a.length;         // 3
a[-1];            // undefined — JavaScript doesn't support negative indexing
a.at(-1);         // 3 — use .at() for negative indices (ES2022)
```

**Why doesn't `a[-1]` work?** Array indices are property keys. `-1` is a valid key but not a valid index — it creates a property named `"-1"`, not an access to the last element. The `at()` method was added specifically to fix this gap.

### Mutating methods

| Method | Effect | Returns |
|---|---|---|
| `push(x)` | Append to end | New length |
| `pop()` | Remove from end | Removed element |
| `unshift(x)` | Prepend to start | New length |
| `shift()` | Remove from start | Removed element |
| `splice(i, n, ...items)` | Remove `n` at `i`, insert `items` | Removed elements |
| `sort(cmp)` | Sort in place | The same array |
| `reverse()` | Reverse in place | The same array |
| `fill(v, start, end)` | Overwrite range with `v` | The same array |

**Why know about mutation?** If you pass an array to a function and that function calls `.sort()`, your original array is now sorted too (reference semantics). This creates bugs at a distance. Prefer non-mutating alternatives.

### Non-mutating methods

| Method | Returns | Purpose |
|---|---|---|
| `slice(i, j)` | Shallow copy of `[i, j)` | Extract a sub-array |
| `concat(other)` | Combined new array | Merge arrays |
| `map(fn)` | New array | Transform each element |
| `filter(fn)` | New array | Keep elements matching predicate |
| `reduce(fn, init)` | Single value | Accumulate |
| `find(fn)` / `findIndex(fn)` | Element or `-1` | First match |
| `some(fn)` / `every(fn)` | Boolean | Test existence / universality |
| `includes(x)` | Boolean | Contains check |
| `flat(depth)` / `flatMap(fn)` | Flattened array | Flatten nested arrays |
| `toSorted(cmp)` | New sorted array | Non-mutating sort (ES2023) |
| `toReversed()` | New reversed array | Non-mutating reverse (ES2023) |
| `toSpliced(i, n, ...items)` | New array | Non-mutating splice (ES2023) |

### Spread and destructuring

```js
const xs = [1, 2, 3];
const ys = [0, ...xs, 4];               // [0, 1, 2, 3, 4]
const [first, ...rest] = xs;            // first = 1, rest = [2, 3]
const [, second] = xs;                  // skip first, second = 2
```

### `sort` is lexicographic by default

This is the single most surprising behaviour in JavaScript arrays:

```js
[10, 2, 1].sort();                      // [1, 10, 2] ← WRONG for numbers!
[10, 2, 1].sort((a, b) => a - b);       // [1, 2, 10] ← correct
```

**Why?** `sort()` converts elements to strings and compares them lexicographically. The string `"10"` comes before `"2"` because `"1" < "2"`. Always pass a comparator for non-string arrays.

`sort` has been stable since ES2019 (equal elements maintain their relative order).

### `Array.from`

Build arrays from iterables or with a mapper:

```js
Array.from({ length: 5 }, (_, i) => i * i);  // [0, 1, 4, 9, 16]
Array.from(new Set([1, 2, 2, 3]));           // [1, 2, 3]
Array.from("hello");                          // ["h", "e", "l", "l", "o"]
```

### `flat` and `flatMap`

```js
[[1, 2], [3, [4]]].flat();          // [1, 2, 3, [4]] — one level
[[1, 2], [3, [4]]].flat(Infinity);  // [1, 2, 3, 4]   — all levels

users.flatMap(u => u.emails);        // collects all emails into one array
```

`flatMap` is equivalent to `.map(fn).flat(1)` but in a single pass — more efficient.

### Checking "is this an array?"

```js
typeof [];                  // "object" — not helpful
Array.isArray([]);          // true — the correct check
[] instanceof Array;        // true — but fails across realms
```

Always use `Array.isArray()`.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Mutating methods exist alongside non-mutating | Confusion about which is which | Immutable-first languages (Clojure, Elixir) don't have this problem |
| Lexicographic default sort | Surprising for numbers | Most languages sort numbers numerically by default |
| `at()` for negative indices | Requires learning a new method | Python's `arr[-1]` is more intuitive |
| ES2023 `toSorted`/`toReversed` | Not available in older runtimes | Use `[...arr].sort()` as a polyfill pattern |
| `typeof [] === "object"` | Useless for detection | `Array.isArray()` fixes it but adds a function call |

## Production-quality code

```js
function unique(arr) {
  return [...new Set(arr)];
}

function groupBy(arr, keyFn) {
  return arr.reduce((groups, item) => {
    const key = keyFn(item);
    (groups[key] ??= []).push(item);
    return groups;
  }, {});
}

function zip(a, b) {
  const length = Math.min(a.length, b.length);
  return Array.from({ length }, (_, i) => [a[i], b[i]]);
}

function chunk(arr, size) {
  if (size <= 0) throw new RangeError("chunk size must be positive");
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}

function partition(arr, predicate) {
  const pass = [];
  const fail = [];
  for (const item of arr) {
    (predicate(item) ? pass : fail).push(item);
  }
  return [pass, fail];
}

function topN(arr, n, compareFn = (a, b) => b - a) {
  return [...arr].sort(compareFn).slice(0, n);
}
```

## Security notes

- **Denial of service via large arrays.** If user input controls the size of an array (e.g., `Array.from({ length: userInput })`), validate the size first. An attacker could request `Array(1e9)` and crash the process with an out-of-memory error.
- **Prototype pollution through array-like objects.** When merging user-controlled objects that have numeric keys and a `length` property, they can masquerade as arrays. Validate with `Array.isArray()` before treating input as an array.

## Performance notes

- `push` / `pop` are O(1). `unshift` / `shift` are O(n) because all elements must be moved.
- `.map().filter()` chains create intermediate arrays. For very large datasets, combine into a single `reduce` or `for...of` loop.
- `sort` is O(n log n) — TimSort in V8. Creating a sorted copy with `toSorted()` or `[...arr].sort()` adds the cost of a shallow copy.
- `includes` and `indexOf` are O(n). For frequent lookups, convert to a `Set` first (O(1) per lookup after O(n) construction).
- Sparse arrays (`Array(1000)`) have different internal representations than dense arrays. V8 optimizes dense arrays heavily — avoid sparse arrays in performance-sensitive code.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `[10, 2, 1].sort()` returns `[1, 10, 2]` | Default sort is lexicographic on strings | Always pass a comparator: `.sort((a, b) => a - b)` |
| `typeof arr === "object"` doesn't detect arrays | `typeof` returns `"object"` for arrays, objects, and `null` | Use `Array.isArray(arr)` |
| `Array(3)` creates `[empty × 3]`, not `[undefined, undefined, undefined]` | `Array(n)` creates a sparse array with no elements | Use `Array.from({ length: 3 })` or `new Array(3).fill(undefined)` |
| Sorting mutated the original array | `.sort()` is in-place | Use `.toSorted()` or `[...arr].sort()` |
| `arr.find()` returns `undefined` and you can't tell if the element was found or is actually `undefined` | `find` returns the value, which could be `undefined` | Use `findIndex` and check for `-1` |

## Practice

**Warm-up.** Sum an array of numbers using `reduce`. Then do it with a `for...of` loop. Compare readability.

**Standard.** Implement `unique(arr)` — return an array with duplicates removed, preserving insertion order. Compare `Set`-based and `indexOf`-based approaches.

**Bug hunt.** Why does `[10, 2, 1].sort()` return `[1, 10, 2]`? Fix it.

**Stretch.** Write `zip(a, b)` that returns an array of pairs: `zip([1,2,3], ["a","b","c"])` → `[[1,"a"], [2,"b"], [3,"c"]]`. Handle arrays of different lengths by stopping at the shorter one.

**Stretch++.** Implement `chunk(arr, size)` immutably. Then implement `partition(arr, predicate)` that splits an array into two: elements that pass and elements that fail.

<details><summary>Show solutions</summary>

**Warm-up.**

```js
const sum = [1, 2, 3, 4].reduce((acc, x) => acc + x, 0); // 10
```

**Bug hunt.**

```js
// sort() converts to strings: "10" < "2" lexicographically.
// Fix: always pass a numeric comparator.
[10, 2, 1].sort((a, b) => a - b); // [1, 2, 10]
```

**Standard.**

```js
// Set-based (O(n), preferred):
const unique = arr => [...new Set(arr)];

// indexOf-based (O(n²), avoid for large arrays):
const unique2 = arr => arr.filter((x, i) => arr.indexOf(x) === i);
```

**Stretch.**

```js
function zip(a, b) {
  const len = Math.min(a.length, b.length);
  return Array.from({ length: len }, (_, i) => [a[i], b[i]]);
}
```

</details>

## Quiz

1. How do you check if something is an array?
    (a) `typeof x === "array"`
    (b) `Array.isArray(x)`
    (c) `x instanceof Object`
    (d) `x.length` exists

2. What does `arr.at(-1)` return?
    (a) `undefined`
    (b) The last element
    (c) An error
    (d) The array length

3. How do you get a sorted copy without mutating?
    (a) `arr.sort()`
    (b) `arr.toSorted()`
    (c) `arr.slice().sort()`
    (d) Both (b) and (c)

4. The default `sort()` order is:
    (a) Numeric ascending
    (b) Lexicographic on string coercion
    (c) Random
    (d) Stable numeric

5. `[[1, 2], [3]].flat()` produces:
    (a) `[[1, 2], [3]]`
    (b) `[1, 2, 3]`
    (c) An error
    (d) `[1, 2]`

**Short answer:**

6. When should you use `find` vs. `filter`?
7. Name two non-mutating alternatives to mutating array methods introduced in ES2023.

*Answers: 1-b, 2-b, 3-d, 4-b, 5-b. 6 — Use `find` when you need the first element matching a condition (returns one value or `undefined`); use `filter` when you need all matching elements (returns an array). 7 — `toSorted()` (replaces `sort()`), `toReversed()` (replaces `reverse()`), and `toSpliced()` (replaces `splice()`).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-arrays — mini-project](mini-projects/08-arrays-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Arrays are objects with numeric indices — use `Array.isArray()` to detect them.
- Prefer non-mutating methods (`map`, `filter`, `toSorted`) over mutating ones (`sort`, `splice`, `push`).
- Always pass a comparator to `sort` for numbers — the default is lexicographic.
- `at(-1)` replaces the missing negative-index feature; `Array.from` builds arrays from iterables.

## Further reading

- MDN, *Array*.
- MDN, *Change Array by copy (ES2023)*.
- Next: [Errors](09-errors.md).
