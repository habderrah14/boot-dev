# Chapter 07 — Loops

> "JavaScript gives you five loop constructs and a handful of array methods. Three of the loops and most of the methods are all you need."

## Learning objectives

By the end of this chapter you will be able to:

- Choose between `for...of`, classic `for`, and `while` for different iteration needs.
- Explain why `for...in` is wrong for arrays and what to use instead.
- Use `forEach`, `map`, `filter`, and `reduce` for declarative iteration.
- Use `break`, `continue`, and labels correctly.
- Avoid the `forEach` + `async` trap.

## Prerequisites & recap

- [Variables](01-variables.md) — `const` in loop declarations.
- [Functions](03-functions.md) — callbacks, arrow functions.

## The simple version

When you need to do something for every item in a collection, you have two styles: **imperative** (a loop that says "go through each item and do X") and **declarative** (a method that says "transform/filter/reduce this collection"). For arrays and other iterables, `for...of` is the imperative workhorse — it handles values directly, supports `break` and `continue`, and works with `async/await`. For transformation pipelines, array methods like `map`, `filter`, and `reduce` express intent more clearly. The one loop you should almost never use on arrays is `for...in` — it iterates keys (as strings!), including inherited ones, which is rarely what you want.

## In plain terms (newbie lane)

This chapter is really about **Loops**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Choosing the right iteration tool:

  Need values from an iterable?
  ├── YES ─── for...of       ← preferred for arrays, sets, maps
  │           (supports break, continue, await)
  │
  Need the index too?
  ├── YES ─── for (let i = 0; ...) or arr.entries()
  │
  Need to transform each element?
  ├── YES ─── .map(fn)       ← returns new array
  │
  Need a subset?
  ├── YES ─── .filter(fn)    ← returns new array
  │
  Need a single accumulated value?
  ├── YES ─── .reduce(fn, init)
  │
  Need object keys?
  ├── YES ─── Object.entries(obj) + for...of
  │           (NOT for...in on arrays!)
  │
  Condition-based repetition?
  └── YES ─── while / do...while
```

*Figure 7-1. Decision tree for choosing an iteration construct.*

## Concept deep-dive

### `for...of` — your default loop

```js
for (const x of [1, 2, 3]) console.log(x);         // values
for (const char of "hello") console.log(char);      // string chars
for (const x of new Set([1, 2, 3])) console.log(x); // set values
for (const [k, v] of new Map([["a", 1]])) console.log(k, v);
```

`for...of` works with anything that implements the [iterable protocol](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Iteration_protocols) (`Symbol.iterator`). Arrays, strings, Sets, Maps, generators, and `NodeList` are all iterable. Plain objects are **not** — use `Object.entries(obj)` to make them iterable.

**Why `for...of` over `forEach`?** It supports `break`, `continue`, and `await`. `forEach` supports none of these — `return` inside a `forEach` callback only exits the current callback, not the loop.

### `for...in` — avoid for arrays

```js
for (const key in { a: 1, b: 2 }) console.log(key);  // "a", "b" — keys
```

`for...in` iterates **enumerable string keys**, including inherited ones. On arrays, that means:

```js
for (const key in [10, 20]) console.log(key);  // "0", "1" — string indices!
```

It also picks up any properties added to `Array.prototype`. For objects, prefer `Object.entries()` + `for...of`. For arrays, always use `for...of`.

### Classic `for` loop

```js
for (let i = 0; i < items.length; i++) {
  console.log(i, items[i]);
}
```

Use the classic `for` when you need the index, need to skip elements (`i += 2`), or need to iterate backwards. Otherwise, `for...of` or array methods are clearer.

### Array methods — declarative iteration

```js
const nums = [1, 2, 3, 4, 5];
nums.forEach(x => console.log(x));          // side effects only, returns undefined
nums.map(x => x * x);                       // [1, 4, 9, 16, 25]
nums.filter(x => x > 2);                    // [3, 4, 5]
nums.reduce((sum, x) => sum + x, 0);        // 15
nums.find(x => x > 3);                      // 4 (first match)
nums.some(x => x > 4);                      // true
nums.every(x => x > 0);                     // true
```

**Why prefer these over loops?** They declare *what* you want (transform, filter, accumulate) rather than *how* to walk the collection. The intent is immediately clear from the method name. Chain them for powerful pipelines:

```js
const topActive = users
  .filter(u => u.active)
  .map(u => u.name)
  .sort();
```

### `while` and `do...while`

```js
let n = 1;
while (n < 100) n *= 2;        // condition checked before body

let input;
do {
  input = getInput();
} while (!input);               // body runs at least once
```

Use `while` for condition-based repetition where you don't know the iteration count in advance. `do...while` guarantees at least one execution.

### `break`, `continue`, and labels

```js
for (const user of users) {
  if (user.isBot) continue;     // skip this iteration
  if (user.isAdmin) break;      // exit the loop entirely
  process(user);
}
```

**Labels** let you break or continue an outer loop from inside a nested one:

```js
outer: for (const row of matrix) {
  for (const cell of row) {
    if (cell === target) break outer;
  }
}
```

Labels are legal but rare. If you reach for one, consider extracting the inner loop into a function that returns early instead.

### The `forEach` + `async` trap

```js
// BUG: forEach does NOT await the callbacks — they fire in parallel,
// and the function continues immediately
urls.forEach(async (url) => {
  const data = await fetch(url);
  // ...
});

// FIX 1: Sequential — use for...of
for (const url of urls) {
  const data = await fetch(url);
}

// FIX 2: Parallel — use Promise.all + map
const results = await Promise.all(urls.map(url => fetch(url)));
```

`forEach` ignores the return value of each callback, including promises. It cannot await them.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| `for...of` as default | Can't access index directly | Use `entries()` for index: `for (const [i, x] of arr.entries())` |
| `for...in` for objects | Iterates inherited keys too | Always pair with `Object.hasOwn` or prefer `Object.entries` |
| `forEach` returns `undefined` | Can't chain, can't break | Use `for...of` when you need `break`/`await` |
| `reduce` for accumulation | Can be hard to read for complex logic | Use a `for...of` loop when `reduce` is more than ~3 lines |
| Labels for nested loops | Unusual syntax, hard to read | Extract inner loop to a function |

## Production-quality code

```js
function chunk(arr, size) {
  if (size <= 0) throw new RangeError("size must be positive");
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}

function groupBy(arr, keyFn) {
  const groups = new Map();
  for (const item of arr) {
    const key = keyFn(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  return groups;
}

async function mapSequential(items, asyncFn) {
  const results = [];
  for (const item of items) {
    results.push(await asyncFn(item));
  }
  return results;
}

async function mapParallel(items, asyncFn, concurrency = Infinity) {
  if (concurrency === Infinity) {
    return Promise.all(items.map(asyncFn));
  }
  const results = [];
  for (const batch of chunk(items, concurrency)) {
    results.push(...await Promise.all(batch.map(asyncFn)));
  }
  return results;
}
```

## Security notes

N/A — Loops themselves don't introduce security vulnerabilities. However, be cautious with `for...in` on user-controlled objects (prototype pollution risk — see [Chapter 06](06-prototypes.md)).

## Performance notes

- `for` and `for...of` are equally fast in modern engines. V8 optimizes both to near-identical machine code.
- `forEach` has slight overhead from the function call per element, but it's negligible unless you're iterating millions of items.
- `.map().filter()` chains create intermediate arrays. For very large datasets, consider a single `reduce` or a `for...of` loop to avoid extra allocations.
- `break` in `for...of` is free — the iterator's `return()` method is called to clean up resources (important for generators).

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `for...in` on an array yields string keys `"0"`, `"1"` | `for...in` iterates enumerable keys, not values | Use `for...of` for values |
| `async` callbacks in `forEach` don't wait | `forEach` ignores returned promises | Use `for...of` with `await`, or `Promise.all` + `.map()` |
| Mutating an array during `for...of` causes skips or repeats | Structural changes invalidate the iterator | Build a new array instead, or iterate a copy |
| `reduce` callback is unreadable at 10+ lines | Overusing `reduce` for complex logic | Switch to a `for...of` loop — explicit state is clearer |
| `break` inside `forEach` doesn't work | `forEach` doesn't support `break` — it calls the callback for every element | Use `for...of` when you need early exit |

## Practice

**Warm-up.** Iterate an array two ways: `for...of` and `forEach`. Print each element with its index (hint: `arr.entries()` for `for...of`).

**Standard.** Compute the minimum and maximum of a numeric array in a single pass using `reduce`.

**Bug hunt.** Why does `for (const x in [10, 20, 30])` print `"0"`, `"1"`, `"2"` instead of `10`, `20`, `30`?

**Stretch.** Write `chunk(arr, size)` that splits an array into sub-arrays of at most `size` elements. Return the result without mutating the input.

**Stretch++.** Write `mapParallel(items, asyncFn, concurrency)` that processes at most `concurrency` items at a time using `Promise.all`, returning all results in order.

<details><summary>Show solutions</summary>

**Bug hunt.**

```js
// for...in iterates enumerable KEYS (as strings), not values.
// Array indices are keys: "0", "1", "2".
// Fix: use for...of to get values.
for (const x of [10, 20, 30]) console.log(x); // 10, 20, 30
```

**Standard.**

```js
const [min, max] = nums.reduce(
  ([lo, hi], x) => [Math.min(lo, x), Math.max(hi, x)],
  [Infinity, -Infinity]
);
```

**Stretch.**

```js
function chunk(arr, size) {
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}
```

</details>

## Quiz

1. For iterating array values, prefer:
    (a) `for...in`
    (b) `for...of`
    (c) `for (let i = 0; ...)` always
    (d) `while`

2. `for...in` iterates:
    (a) Values
    (b) Enumerable string keys, including inherited
    (c) Entries (key-value pairs)
    (d) Array length

3. Which array method returns a new array?
    (a) `forEach`
    (b) `map`
    (c) `push`
    (d) `sort`

4. Can you `break` out of a `forEach`?
    (a) Yes, with `break`
    (b) `return` exits only the current callback, not the loop
    (c) Yes, with `throw`
    (d) Not possible cleanly — use `for...of` instead

5. Labels in loops are:
    (a) Deprecated
    (b) Legal but rarely needed
    (c) Always required for nested loops
    (d) A syntax error

**Short answer:**

6. Why does `forEach` with `async` callbacks not work as expected?
7. When should you use a classic `for` loop instead of `for...of`?

*Answers: 1-b, 2-b, 3-b, 4-d, 5-b. 6 — `forEach` calls each callback but ignores the returned promise, so all async callbacks fire concurrently and the code after `forEach` runs before they complete. 7 — When you need the index for non-sequential access (e.g., stepping by 2, iterating backwards), or when performance on a tight numerical loop matters.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-loops — mini-project](mini-projects/07-loops-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `for...of` is your default loop for arrays and iterables — it handles values directly and supports `break`, `continue`, and `await`.
- Array methods (`map`, `filter`, `reduce`) express intent declaratively — use them for transformation pipelines.
- Never use `for...in` on arrays — it iterates string keys, including inherited ones.
- `forEach` + `async` is a trap — use `for...of` or `Promise.all` instead.

## Further reading

- MDN, *Loops and iteration*.
- MDN, *Iteration protocols*.
- Next: [Arrays](08-arrays.md).
