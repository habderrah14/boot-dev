# Chapter 11 — Maps

> "`Map` is a key-value store where keys can be anything, iteration order is deterministic, and `.size` is O(1). Use it when you'd otherwise reach for a plain `{}`."

## Learning objectives

By the end of this chapter you will be able to:

- Create, get, set, delete, and iterate a `Map`.
- Explain why `Map` beats plain `{}` for dynamic key-value collections.
- Convert between `Map` and plain objects for JSON interop.
- Use `WeakMap` for GC-friendly metadata attached to objects.
- Choose `Map` vs. `Object` for each use case.

## Prerequisites & recap

- [Objects](04-objects.md) — property access, `Object.entries`.
- [Sets](10-sets.md) — the `Set` counterpart.

## The simple version

A `Map` is JavaScript's dedicated key-value data structure. Unlike a plain object (`{}`), a Map accepts **any value** as a key — objects, functions, numbers, even `NaN`. It preserves insertion order, gives you `.size` in O(1), and doesn't suffer from prototype pollution or key-coercion bugs. Use a plain object for static, string-keyed data (like JSON payloads and config). Use a `Map` for dynamic collections where keys are added and removed at runtime, especially when the keys aren't strings.

## In plain terms (newbie lane)

This chapter is really about **Maps**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Map vs. Object — when to pick which:

  ┌──────────────────────────────┬──────────────────────────────┐
  │          Map                 │          Object              │
  ├──────────────────────────────┼──────────────────────────────┤
  │  Keys: any value             │  Keys: strings / symbols     │
  │  .size: O(1)                 │  Object.keys(o).length: O(n) │
  │  Iteration: insertion order  │  Iteration: insertion order* │
  │  No prototype keys           │  Inherits from Object.proto  │
  │  Frequent add/delete: fast   │  delete: slow (deoptimizes)  │
  │  Not JSON-serializable       │  JSON-native                 │
  └──────────────────────────────┴──────────────────────────────┘
  * Object key order has edge cases with numeric keys

  Map structure:
  ┌──────────┬──────────┐
  │   Key    │  Value   │
  ├──────────┼──────────┤
  │  "a"     │    1     │
  │  {obj}   │  "admin" │
  │  42      │  true    │
  │  NaN     │  "weird" │  ← NaN works as a key!
  └──────────┴──────────┘
```

*Figure 11-1. Map vs. Object comparison and Map's any-key capability.*

## Concept deep-dive

### Basics

```js
const m = new Map();
m.set("a", 1).set("b", 2);      // chainable
m.get("a");                       // 1
m.has("b");                       // true
m.size;                           // 2
m.delete("a");                    // true
m.clear();                        // empty
```

### Any key type

Unlike `{}` where keys are coerced to strings, `Map` preserves key identity:

```js
const user = { id: 1 };
const cache = new Map();
cache.set(user, { role: "admin" });
cache.get(user);      // { role: "admin" }

cache.set(42, "number key");
cache.set("42", "string key");
cache.get(42);        // "number key" — 42 and "42" are different keys
```

With a plain object, `obj[42]` and `obj["42"]` are the same key because all object keys are strings.

**Why does this matter?** In a plain object, all keys become strings. If you're building a cache keyed by objects, a frequency counter keyed by numbers, or a lookup table with mixed-type keys, `Map` is the only correct choice.

### Deterministic iteration order

Maps iterate in insertion order — guaranteed by the spec:

```js
const m = new Map([["c", 3], ["a", 1], ["b", 2]]);
for (const [key, value] of m) {
  console.log(key, value);  // c:3, a:1, b:2
}

m.keys();      // MapIterator {"c", "a", "b"}
m.values();    // MapIterator {3, 1, 2}
m.entries();   // MapIterator {["c",3], ["a",1], ["b",2]}
```

### O(1) `.size`

```js
m.size;                          // O(1) — tracked internally
Object.keys(obj).length;        // O(n) — allocates an array and counts
```

If you frequently check collection size, `Map` avoids the overhead of `Object.keys`.

### Initializers

```js
const m = new Map([["a", 1], ["b", 2]]);
const fromObj = new Map(Object.entries({ a: 1, b: 2 }));
```

### Map ↔ Object conversion

```js
const obj = Object.fromEntries(m);              // Map → Object (loses non-string keys)
const map = new Map(Object.entries(obj));        // Object → Map

JSON.stringify(Object.fromEntries(m));           // Map → JSON (via Object)
```

**Why isn't Map JSON-serializable?** JSON only supports string keys. A Map can have any key type, so there's no lossless way to serialize it. You must explicitly convert to an object (losing non-string keys) or to an array of entries.

### When to pick Map vs. Object

| Criteria | Map | Object |
|---|---|---|
| Key types | Any | Strings and symbols only |
| Size | `.size` — O(1) | `Object.keys().length` — O(n) |
| Frequent add/delete | Fast (optimized for it) | `delete` deoptimizes V8 hidden classes |
| JSON serialization | Manual conversion | Native |
| Fixed-shape records | Overkill | Perfect |
| Prototype pollution risk | None | Yes — `__proto__`, `constructor` |
| Default choice for... | Dynamic collections, caches, counters | Config, DTOs, API payloads |

### WeakMap

`WeakMap` keys must be objects (or non-registered symbols). The key-value pair is garbage-collected when no other reference to the key exists.

```js
const metadata = new WeakMap();

function process(element) {
  if (!metadata.has(element)) {
    metadata.set(element, { processedAt: Date.now() });
  }
  return metadata.get(element);
}
```

**Why WeakMap?** It attaches data to objects without preventing them from being garbage-collected. Without `WeakMap`, storing metadata in a regular `Map` keyed by object references creates a memory leak — the Map's reference keeps the object alive forever.

**Restrictions:** No iteration, no `.size`, no `.clear()`, no `.keys()`. You can only `get`, `set`, `has`, and `delete` with a known key.

Use cases:
- Private data for class instances (pre-`#private` fields).
- DOM node metadata.
- Memoization caches where arguments are objects.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Any-key capability | Slower than string-only hash tables | Use `Object` for string-keyed, static data |
| Insertion-order iteration | Slight memory overhead | Unordered maps (like Go's `map`) don't guarantee order |
| Not JSON-serializable | Requires conversion step | Object wins for data that will be serialized frequently |
| `WeakMap` — no iteration | Can't inspect contents for debugging | Use regular `Map` when you need to enumerate entries |
| `delete` on Map is fast | Map has more overhead per element than Object | Use Object for small, static records |

## Production-quality code

```js
function countOccurrences(arr) {
  const counts = new Map();
  for (const item of arr) {
    counts.set(item, (counts.get(item) ?? 0) + 1);
  }
  return counts;
}

function memoize(fn) {
  const cache = new Map();
  return function memoized(arg) {
    if (cache.has(arg)) return cache.get(arg);
    const result = fn(arg);
    cache.set(arg, result);
    return result;
  };
}

class LRU {
  #map = new Map();
  #maxSize;

  constructor(maxSize) {
    if (maxSize <= 0) throw new RangeError("maxSize must be positive");
    this.#maxSize = maxSize;
  }

  get(key) {
    if (!this.#map.has(key)) return undefined;
    const value = this.#map.get(key);
    this.#map.delete(key);
    this.#map.set(key, value);
    return value;
  }

  set(key, value) {
    if (this.#map.has(key)) this.#map.delete(key);
    this.#map.set(key, value);
    if (this.#map.size > this.#maxSize) {
      const oldest = this.#map.keys().next().value;
      this.#map.delete(oldest);
    }
  }

  get size() { return this.#map.size; }
}
```

## Security notes

- **Prototype pollution via objects.** Using `{}` with user-controlled keys is a security risk: setting `__proto__` or `constructor.prototype` can pollute every object in the process. `Map` is immune to this because keys are stored internally, not on the object's prototype chain.
- **Use `Map` for user-controlled keys.** Whenever keys come from untrusted input (form fields, API parameters, URL query strings), use a `Map` instead of a plain object. Alternatively, use `Object.create(null)` for a prototype-free dictionary.

## Performance notes

- `Map.get`, `.set`, `.has`, `.delete` are O(1) on average — hash-table based.
- `Map` uses more memory per entry than a plain object (each entry stores the full key and value, plus hash overhead). For small, static records (< 10 keys), objects are lighter.
- `Map.delete` does not deoptimize the engine, unlike `delete obj.key` which forces V8 to abandon its hidden class optimization. For collections with frequent deletions, `Map` wins.
- Iterating a `Map` is O(n) — same as `Object.entries()`, but `Map` doesn't allocate an intermediate array.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `obj[1]` and `obj["1"]` overwrite each other | Object keys are coerced to strings | Use `Map` — it keeps `1` and `"1"` as separate keys |
| Setting `__proto__` on a user-controlled object | Prototype pollution vulnerability | Use `Map` for user-controlled key-value data |
| `JSON.stringify(map)` returns `"{}"` | `Map` is not JSON-serializable | Convert: `JSON.stringify(Object.fromEntries(map))` |
| Assuming `WeakMap` is iterable | WeakMap deliberately hides contents | Use a regular `Map` if you need to enumerate entries |
| Using `Map` for a JSON payload | Unnecessary overhead for static, string-keyed data | Use a plain object for DTOs and config |

## Practice

**Warm-up.** Build a Map of the first 10 perfect squares (key: number, value: its square).

**Standard.** Group an array of objects by a field into a `Map<string, Array>`. For example, group users by `role`.

**Bug hunt.** Why might using `{}` for a user-controlled key cause a prototype-pollution vulnerability? Show the attack and the Map-based fix.

**Stretch.** Convert a `Map` with mixed-type keys to a JSON-compatible format and back. Handle the loss of non-string keys explicitly.

**Stretch++.** Use `WeakMap` to attach private metadata (creation timestamp, access count) to objects. Verify that the metadata doesn't prevent garbage collection.

<details><summary>Show solutions</summary>

**Warm-up.**

```js
const squares = new Map();
for (let i = 1; i <= 10; i++) squares.set(i, i * i);
```

**Bug hunt.**

```js
// Attack:
const data = {};
const maliciousKey = "__proto__";
data[maliciousKey] = { isAdmin: true };
// Now {}.isAdmin === true for EVERY new object!

// Fix: use Map
const safeData = new Map();
safeData.set(maliciousKey, { isAdmin: true });
// No prototype pollution — Map stores keys internally
```

**Standard.**

```js
function groupBy(arr, keyFn) {
  const groups = new Map();
  for (const item of arr) {
    const key = keyFn(item);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  return groups;
}

const byRole = groupBy(users, u => u.role);
```

</details>

## Quiz

1. `Map` keys can be:
    (a) Strings only
    (b) Strings and numbers
    (c) Any value
    (d) Objects only

2. `m.size` is:
    (a) O(n)
    (b) O(1)
    (c) Not defined on Map
    (d) Requires iteration

3. `WeakMap` differs from `Map` in that:
    (a) It's iterable
    (b) Keys must be objects, and entries are GC-eligible
    (c) It's sorted
    (d) It's faster for string keys

4. To convert a `Map` to JSON:
    (a) `JSON.stringify(m)` directly
    (b) `Object.fromEntries(m)` then `JSON.stringify`
    (c) `m.toJSON()`
    (d) It's automatic

5. In a plain `{}`, the keys `1` and `"1"`:
    (a) Are different keys
    (b) Are the same key — coerced to string
    (c) Throw an error
    (d) Depends on strict mode

**Short answer:**

6. When would you pick Object over Map?
7. Describe one use case where `WeakMap` is necessary.

*Answers: 1-c, 2-b, 3-b, 4-b, 5-b. 6 — When the data is a fixed-shape, string-keyed record that will be serialized to JSON (config objects, API payloads, DTOs). 7 — Attaching metadata to DOM nodes (e.g., tracking which elements have been initialized with event listeners) without preventing the nodes from being garbage-collected when removed from the DOM.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-maps — mini-project](mini-projects/11-maps-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `Map` is the right choice for dynamic key-value data — any key type, O(1) `.size`, immune to prototype pollution.
- Plain objects are best for static, string-keyed records that need JSON serialization.
- `WeakMap` is for GC-friendly metadata on objects — no iteration, no size, keys must be objects.
- Never use plain `{}` for user-controlled keys — use `Map` or `Object.create(null)`.

## Further reading

- MDN, *Map*.
- MDN, *WeakMap*.
- Next: [Promises](12-promises.md).
