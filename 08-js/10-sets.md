# Chapter 10 — Sets

> "`Set` is JavaScript's answer to 'unique collection of things.' Cheaper lookups than arrays, safer semantics than objects-as-bags."

## Learning objectives

By the end of this chapter you will be able to:

- Create, add, check, delete, and iterate a `Set`.
- Convert between arrays and sets for deduplication.
- Perform set operations: union, intersection, difference, and subset checks.
- Explain why `Set` uses reference equality for objects and work around it.
- Use `WeakSet` for "have I seen this?" tracking without memory leaks.

## Prerequisites & recap

- [Arrays](08-arrays.md) — `includes`, `filter`, spread.

## The simple version

A `Set` is a collection where every value appears at most once. You add values, check membership, and iterate — that's it. There are no duplicates, no indices, and no key-value pairs. The big win over arrays is speed: `Set.has(x)` is O(1) on average, while `Array.includes(x)` is O(n). Sets preserve insertion order, so iterating a Set gives you elements in the order you added them.

The most common pattern is deduplicating an array: `[...new Set(arr)]`. For more advanced needs — finding common elements between two collections, or elements unique to one — you use set operations, which modern runtimes now provide as built-in methods.

## In plain terms (newbie lane)

This chapter is really about **Sets**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Set basics:

  const s = new Set([1, 2, 3, 2, 1]);
  ┌─────────────────────────┐
  │  Set { 1, 2, 3 }        │  ← duplicates removed automatically
  │  s.size = 3              │
  │  s.has(2) = true    O(1) │
  └─────────────────────────┘

  Set operations:

  A = {1, 2, 3}         B = {2, 3, 4}

  A ∪ B (union)         = {1, 2, 3, 4}
  A ∩ B (intersection)  = {2, 3}
  A − B (difference)    = {1}
  A △ B (symmetric diff)= {1, 4}

  ┌─────┬───────┬─────┐
  │  1  │ 2   3 │  4  │
  │  A  │ A ∩ B │  B  │
  └─────┴───────┴─────┘
```

*Figure 10-1. Set deduplication and the four fundamental set operations.*

## Concept deep-dive

### Basics

```js
const s = new Set([1, 2, 3, 2]);
s.size;               // 3
s.has(2);             // true — O(1) lookup
s.add(4);             // Set {1, 2, 3, 4}
s.delete(1);          // true (was present)
s.clear();            // empty the set
for (const x of s) console.log(x);  // insertion order
```

**Why use Set over an array?** Two reasons: uniqueness is automatic (no need to check before adding), and membership checks are fast. If you're building a collection where you'll frequently ask "is X in here?", `Set` is the right choice.

### Array ↔ Set conversion

```js
const unique = [...new Set([1, 1, 2, 3, 3])];     // [1, 2, 3]
const backToSet = new Set(unique);                  // Set {1, 2, 3}
```

This is the most common `Set` pattern — deduplicating an array in one line. Insertion order is preserved.

### Reference equality for objects

`Set` compares values using the same algorithm as `===`. For objects, that means reference equality, not structural equality:

```js
const s = new Set();
s.add({ x: 1 });
s.add({ x: 1 });
s.size;    // 2 — two different objects, even though they look the same
```

**Why?** The same reason `===` doesn't do deep comparison — it would require recursive comparison on every `add` and `has`, which is expensive. If you need structural uniqueness, serialize to a canonical string key, or use a `Map` with a computed key.

### Built-in set operations (ES2025 / Node 22+)

Modern runtimes ship instance methods for all standard set operations:

```js
const a = new Set([1, 2, 3]);
const b = new Set([2, 3, 4]);

a.union(b);               // Set {1, 2, 3, 4}
a.intersection(b);        // Set {2, 3}
a.difference(b);          // Set {1}
a.symmetricDifference(b); // Set {1, 4}
a.isSubsetOf(b);          // false
a.isSupersetOf(b);        // false
a.isDisjointFrom(b);      // false
```

### Polyfills for older runtimes

If you're targeting runtimes without the built-in methods:

```js
function union(a, b) {
  return new Set([...a, ...b]);
}

function intersection(a, b) {
  return new Set([...a].filter(x => b.has(x)));
}

function difference(a, b) {
  return new Set([...a].filter(x => !b.has(x)));
}

function symmetricDifference(a, b) {
  const result = new Set(a);
  for (const x of b) {
    if (result.has(x)) result.delete(x);
    else result.add(x);
  }
  return result;
}
```

### WeakSet

`WeakSet` holds objects only, and doesn't prevent garbage collection. If the only reference to an object is inside a `WeakSet`, the GC can reclaim it.

```js
const seen = new WeakSet();

function processOnce(obj) {
  if (seen.has(obj)) return;
  seen.add(obj);
  // ... process obj
}
```

**Restrictions:** No iteration, no `.size`, no `.clear()`. The spec deliberately forbids observing weak references because the GC's timing is non-deterministic.

**Why use WeakSet?** The classic use case is "have I already processed this object?" without leaking memory. DOM node tracking, circular-reference detection in serializers, and one-time initialization guards all benefit from `WeakSet`.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| `===` equality | Objects with identical content are treated as different | Use a `Map` with serialized keys for structural equality |
| Insertion-order iteration | Slightly more memory than an unordered set | Unordered sets (like C++ `unordered_set`) can be faster for pure membership |
| `WeakSet` — no iteration | Can't inspect contents | Use a regular `Set` if you need to enumerate elements |
| Built-in set operations (ES2025) | Not available on older runtimes | Polyfill with the spread+filter pattern |
| No `map`/`filter` methods on Set | Must convert to array first | Sets are for membership, not transformation — convert to array for pipelines |

## Production-quality code

```js
function dedup(arr) {
  return [...new Set(arr)];
}

function hasOverlap(a, b) {
  const setB = b instanceof Set ? b : new Set(b);
  for (const x of a) {
    if (setB.has(x)) return true;
  }
  return false;
}

function uniqueByKey(arr, keyFn) {
  const seen = new Set();
  return arr.filter(item => {
    const key = keyFn(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function collectTags(items) {
  const tags = new Set();
  for (const item of items) {
    for (const tag of item.tags ?? []) {
      tags.add(tag);
    }
  }
  return [...tags].sort();
}
```

## Security notes

N/A — Sets don't introduce direct security vulnerabilities. However, if you use a `Set` to track "allowed" values for authorization, remember that object identity (`===`) means two structurally identical objects won't match. Use primitive values (strings, numbers) for security-sensitive lookups.

## Performance notes

- `Set.has()`, `.add()`, and `.delete()` are O(1) on average (hash-based). `Array.includes()` is O(n).
- For lookups on collections larger than ~10-20 elements, `Set` significantly outperforms arrays.
- Converting array → Set → array (`[...new Set(arr)]`) costs O(n) time and O(n) memory. For very large arrays, this is still better than O(n²) dedup with `indexOf`.
- Sets use more memory per element than arrays (hash table overhead). For tiny collections (< 5 elements), an array is fine.
- Iterating a `Set` is O(n) — same as an array.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Two "equal" objects both added to the Set | `Set` uses `===` (reference equality) for objects | Use primitive keys, or serialize objects to strings |
| Trying to sort a Set | Sets don't have a `.sort()` method | Convert to array: `[...s].sort()` |
| Using a Set when you need values too | Set stores only keys, no associated values | Use `Map` for key-value pairs |
| Assuming `WeakSet` has `.size` | WeakSet deliberately hides its size | Track count separately if needed |
| Using built-in set methods on Node < 22 | `union`, `intersection` etc. are ES2025 | Use the polyfill pattern or upgrade your runtime |

## Practice

**Warm-up.** Deduplicate `[1, 1, 2, 3, 3, 3]` into a sorted array using a Set.

**Standard.** Given two arrays of strings, print: (1) items in both, (2) items in only the first, (3) items in only the second.

**Bug hunt.** Why does this code report `size: 2` instead of `size: 1`?

```js
const s = new Set();
s.add({ name: "Ada" });
s.add({ name: "Ada" });
console.log(s.size);
```

**Stretch.** Implement `intersection`, `union`, and `difference` functions. Write tests with `node:test`.

**Stretch++.** Profile `Set.has()` vs. `Array.includes()` on a collection of 100,000 random numbers. Measure lookup time for 10,000 queries each.

<details><summary>Show solutions</summary>

**Warm-up.**

```js
const sorted = [...new Set([1, 1, 2, 3, 3, 3])].sort((a, b) => a - b);
// [1, 2, 3]
```

**Bug hunt.**

```js
// Each { name: "Ada" } is a different object in memory.
// Set uses === (reference equality) — two different references = two entries.
// Fix: use the same reference, or use a primitive key.
const ada = { name: "Ada" };
const s = new Set();
s.add(ada);
s.add(ada);   // same reference — not added again
console.log(s.size); // 1
```

**Standard.**

```js
const a = new Set(["apple", "banana", "cherry"]);
const b = new Set(["banana", "cherry", "date"]);

const both = [...a].filter(x => b.has(x));      // intersection
const onlyA = [...a].filter(x => !b.has(x));     // difference A - B
const onlyB = [...b].filter(x => !a.has(x));     // difference B - A
```

</details>

## Quiz

1. `new Set([1, 1, 2])` has size:
    (a) 2
    (b) 3
    (c) 1
    (d) `undefined`

2. Set iteration order is:
    (a) Insertion order
    (b) Random
    (c) Sorted
    (d) Undefined by spec

3. How does Set compare `{ x: 1 }` and `{ x: 1 }` (two separate objects)?
    (a) Equal (structural comparison)
    (b) Not equal (reference comparison)
    (c) Throws an error
    (d) Depends on the runtime

4. How do you get a sorted array from a Set?
    (a) `s.sort()`
    (b) `[...s].sort()`
    (c) `s.toArray()`
    (d) `Array.sort(s)`

5. `WeakSet` supports:
    (a) `.size` and iteration
    (b) Iteration but no `.size`
    (c) Neither — only `has`, `add`, `delete` with object keys
    (d) Strong references that prevent GC

**Short answer:**

6. When does `Set.has(x)` significantly outperform `Array.includes(x)`?
7. Give one real-world use case for `WeakSet`.

*Answers: 1-a, 2-a, 3-b, 4-b, 5-c. 6 — On collections larger than ~20 elements, because `Set.has` is O(1) while `Array.includes` is O(n). The difference grows linearly with collection size. 7 — Tracking which DOM nodes have been processed (e.g., initialized with an event listener) without preventing garbage collection when the node is removed from the DOM.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-sets — mini-project](mini-projects/10-sets-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `Set` stores unique values with O(1) `has` / `add` / `delete`, preserving insertion order.
- `[...new Set(arr)]` is the canonical one-liner for array deduplication.
- Modern runtimes provide built-in `union`, `intersection`, `difference`, and subset checks; polyfill on older runtimes.
- `WeakSet` is for GC-friendly "have I seen this object?" tracking — no iteration, no size.

## Further reading

- MDN, *Set*.
- MDN, *WeakSet*.
- TC39 proposal, *Set methods*.
- Next: [Maps](11-maps.md).
