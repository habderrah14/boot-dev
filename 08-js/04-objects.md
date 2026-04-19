# Chapter 04 — Objects

> "Almost everything in JavaScript is an object. Knowing how they're structured, copied, and mutated is the difference between confidence and hair-pulling."

## Learning objectives

By the end of this chapter you will be able to:

- Create, read, update, and delete object properties using dot and bracket notation.
- Use shorthand properties, computed keys, and destructuring fluently.
- Spread, merge, and clone objects — and know when spread isn't enough.
- Explain reference semantics and choose the right cloning strategy.
- Iterate objects with `Object.keys`, `Object.values`, and `Object.entries`.

## Prerequisites & recap

- [Variables](01-variables.md) — `const`, primitives vs. objects.
- [Functions](03-functions.md) — arrow functions, destructuring in parameters.

## The simple version

An object in JavaScript is a bag of named properties — think of it as a dictionary or hash map with string (or symbol) keys. When you assign an object to a variable, you're storing a *reference* (a pointer), not a copy. That means two variables can point to the same object, and changing it through one name changes it for both. If you need an independent copy, you have to explicitly clone it — either shallowly (one level deep) or deeply (all the way down).

You'll spend most of your JavaScript career creating objects, pulling values out of them (destructuring), and merging them together (spread). Mastering these three operations makes everything else — APIs, configuration, state management — feel natural.

## In plain terms (newbie lane)

This chapter is really about **Objects**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Object in memory:
  ┌─────────────────────────────┐
  │  { id: 1, name: "Ada" }    │  ← one object in heap
  └──────────┬──────────────────┘
             │
     ┌───────┴───────┐
     │               │
   ┌─┴─┐           ┌─┴─┐
   │ a  │           │ b  │     ← two variables, same reference
   └────┘           └────┘
   b.name = "Bob"  →  a.name is now "Bob" too!

  Cloning:
  const c = { ...a };           ← shallow clone (new top-level object)
  const d = structuredClone(a); ← deep clone (all nested objects too)
```

*Figure 4-1. Reference semantics — two names, one object — and cloning strategies.*

## Concept deep-dive

### Object literals

```js
const user = {
  id: 1,
  name: "Ada",
  greet() { return `hi, ${this.name}`; },
};
```

Method shorthand (`greet() {}`) replaces the older `greet: function() {}` form. Both create a regular function with dynamic `this`.

### Access patterns

```js
user.name;             // dot — when you know the key at write time
user["name"];          // bracket — when the key is dynamic
user.email ?? "none";  // safe default with nullish coalescing
delete user.email;     // remove a property (rarely needed)
```

**Why bracket notation?** It lets you use variables, expressions, or keys that aren't valid identifiers (`user["first-name"]`). Dot notation is preferred for readability when the key is static.

### Shorthand properties

When a variable name matches the desired key, you can skip the colon:

```js
const name = "Ada", id = 1;
const u = { name, id };          // same as { name: name, id: id }
```

### Computed keys

```js
const key = "age";
const u = { [key]: 36 };         // { age: 36 }
```

The expression inside `[]` is evaluated at runtime. This is essential for building objects dynamically from user input or API responses.

### Destructuring

Pull properties out of objects into standalone variables:

```js
const { name, id } = user;
const { name: userName } = user;          // rename
const { email = "none" } = user;          // default if missing
```

Destructuring in function parameters is one of JavaScript's most powerful patterns:

```js
function createServer({ port = 3000, host = "localhost" } = {}) {
  // port and host are ready to use
}
```

The `= {}` default at the end means calling `createServer()` with no argument doesn't throw.

### Spread and merge

```js
const a = { x: 1, y: 2 };
const b = { ...a, z: 3 };                 // { x: 1, y: 2, z: 3 }
const c = { ...a, x: 99 };                // { x: 99, y: 2 } — later keys win
```

**Why "later keys win"?** The spec processes spread left-to-right. This gives you a clean pattern for "defaults plus overrides": `{ ...defaults, ...userConfig }`.

### Reference semantics

Variables hold references, not values:

```js
const a = { n: 1 };
const b = a;
b.n = 2;
console.log(a.n);   // 2 — same underlying object
```

**Why references?** Copying entire objects on every assignment would be expensive. References are cheap (just a pointer). The trade-off: you must be explicit about cloning when you need independence.

### Cloning strategies

| Strategy | Syntax | Depth | Handles |
|---|---|---|---|
| Spread | `{ ...a }` | Shallow | Simple cases |
| `Object.assign` | `Object.assign({}, a)` | Shallow | Same as spread |
| `structuredClone` | `structuredClone(a)` | Deep | Dates, RegExp, Maps, Sets, ArrayBuffers, circular refs |
| `JSON.parse(JSON.stringify(a))` | — | Deep | Plain data only (drops functions, `undefined`, Dates become strings) |

Use `structuredClone` for deep cloning in modern runtimes (Node 17+, all modern browsers). Fall back to `JSON.parse(JSON.stringify())` only for plain JSON-compatible data.

### Iteration

```js
Object.keys(user);      // ["id", "name", "greet"]
Object.values(user);    // [1, "Ada", [Function: greet]]
Object.entries(user);   // [["id", 1], ["name", "Ada"], ...]

for (const [key, value] of Object.entries(user)) {
  console.log(key, value);
}
```

### `in` vs. `Object.hasOwn`

```js
"name" in user;                    // true — checks own AND inherited
Object.hasOwn(user, "name");       // true — own properties only
```

**Why `Object.hasOwn` over `obj.hasOwnProperty`?** The latter can be shadowed if someone sets `obj.hasOwnProperty = () => false`. `Object.hasOwn` is a static method that can't be overridden on the instance.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Reference semantics | Must clone explicitly | Languages with value types (Rust, Go structs) copy by default |
| Shallow spread by default | Nested objects still share references | Use `structuredClone` when nested independence matters |
| String-only keys (plus symbols) | Can't use objects as keys directly | Use `Map` when you need object keys |
| `delete` operator | Slow (deoptimizes V8 hidden classes) | Set to `undefined` if performance matters; or use `Map` |
| `Object.hasOwn` (2022) | Not available in very old runtimes | Polyfill or use `Object.prototype.hasOwnProperty.call(obj, key)` |

## Production-quality code

```js
function pick(obj, keys) {
  return Object.fromEntries(
    keys.filter(k => Object.hasOwn(obj, k)).map(k => [k, obj[k]])
  );
}

function omit(obj, keys) {
  const excluded = new Set(keys);
  return Object.fromEntries(
    Object.entries(obj).filter(([k]) => !excluded.has(k))
  );
}

function deepMerge(target, source) {
  const result = { ...target };
  for (const [key, value] of Object.entries(source)) {
    if (
      value !== null &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      Object.hasOwn(result, key) &&
      typeof result[key] === "object" &&
      result[key] !== null
    ) {
      result[key] = deepMerge(result[key], value);
    } else {
      result[key] = value;
    }
  }
  return result;
}

function immutableUpdate(obj, path, value) {
  const keys = path.split(".");
  if (keys.length === 1) return { ...obj, [keys[0]]: value };
  return {
    ...obj,
    [keys[0]]: immutableUpdate(obj[keys[0]] ?? {}, keys.slice(1).join("."), value),
  };
}
```

## Security notes

- **Prototype pollution.** If you blindly merge user-controlled keys into an object (e.g., `Object.assign(target, userInput)`), an attacker can set `__proto__` to inject properties onto every object in your process. Validate or whitelist keys, or use `Map` for user-controlled data.
- **`__proto__` as a key.** Setting `obj["__proto__"]` on a plain object changes its prototype chain. Use `Object.create(null)` for dictionary-like objects that should have no prototype, or use `Map`.

## Performance notes

- Property access (`obj.key`) is O(1) in modern engines — V8 uses hidden classes (shapes) to optimize lookups.
- `delete obj.key` deoptimizes V8's hidden class transitions. If you're removing properties frequently, use `Map` instead.
- `Object.keys()` / `Object.entries()` allocate a new array each call. In hot paths, cache the result or iterate differently.
- Spread (`{ ...obj }`) performs a shallow copy — proportional to the number of top-level keys. For large objects on hot paths, consider mutable updates.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Mutating an object "at a distance" — function changes caller's data | Reference semantics — the function received a reference, not a copy | Clone before mutating: `const local = { ...original }` |
| `{ ...a }` doesn't isolate nested objects | Spread is shallow — nested objects still share references | Use `structuredClone(a)` for deep independence |
| `for...in` iterates unexpected inherited keys | `for...in` walks the prototype chain | Use `Object.keys(obj)` or `for...of Object.entries(obj)` |
| `JSON.stringify` clone drops `undefined`, functions, and Dates | `JSON.stringify` only handles JSON-compatible types | Use `structuredClone` |
| `obj[someObject]` uses `"[object Object]"` as the key | Objects are coerced to strings when used as keys | Use `Map` for non-string keys |

## Practice

**Warm-up.** Create an object using shorthand for three local variables. Access one property with dot notation and another with bracket notation.

**Standard.** Implement `omit(obj, keys)` — the opposite of `pick`. Given `omit({ a: 1, b: 2, c: 3 }, ["b"])`, return `{ a: 1, c: 3 }`.

**Bug hunt.** Explain why `const b = { ...a }; b.inner.x = 1;` also changes `a.inner.x`. How do you fix it?

**Stretch.** Write a function that takes an options object with destructuring and provides defaults for three levels of nesting.

**Stretch++.** Implement `deepMerge(target, source)` that recursively merges nested objects (not arrays — those get replaced).

<details><summary>Show solutions</summary>

**Bug hunt.**

```js
// Spread is shallow — `b.inner` is the SAME object as `a.inner`.
// Fix: use structuredClone for a deep copy.
const b = structuredClone(a);
b.inner.x = 1;
console.log(a.inner.x); // unchanged
```

**Standard.**

```js
function omit(obj, keys) {
  const excluded = new Set(keys);
  return Object.fromEntries(
    Object.entries(obj).filter(([k]) => !excluded.has(k))
  );
}
```

**Stretch++.**

```js
function deepMerge(target, source) {
  const result = { ...target };
  for (const [key, val] of Object.entries(source)) {
    if (val && typeof val === "object" && !Array.isArray(val) &&
        result[key] && typeof result[key] === "object") {
      result[key] = deepMerge(result[key], val);
    } else {
      result[key] = val;
    }
  }
  return result;
}
```

</details>

## Quiz

1. What does `{ x }` shorthand mean?
    (a) Same as `{ x: x }`
    (b) Syntax error
    (c) Makes `x` private
    (d) Deep copies `x`

2. What does `{ ...a }` produce?
    (a) Deep clone of `a`
    (b) Shallow clone of `a`
    (c) A move — `a` is now empty
    (d) A reference copy

3. When you assign `const b = a` where `a` is an object:
    (a) `b` is a copy of `a`
    (b) `b` and `a` share the same underlying object
    (c) `a` becomes immutable
    (d) `b` is `undefined`

4. Which is the safer own-property check?
    (a) `key in obj`
    (b) `Object.hasOwn(obj, key)`
    (c) `obj[key]` is truthy
    (d) `typeof obj[key] !== "undefined"`

5. `Object.entries(user)` returns:
    (a) An array of keys
    (b) An array of values
    (c) An array of `[key, value]` pairs
    (d) A `Map`

**Short answer:**

6. Why prefer `structuredClone` over `JSON.parse(JSON.stringify(x))`?
7. When is spread insufficient for making a copy?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-c. 6 — `structuredClone` handles Dates, RegExps, Maps, Sets, circular references, and `undefined`; JSON round-tripping drops or corrupts all of those. 7 — When the object has nested objects/arrays — spread only copies the top level, leaving nested references shared.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-objects — mini-project](mini-projects/04-objects-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Object literals with shorthand, computed keys, and destructuring are your daily bread.
- Variables hold references — clone explicitly when you need independence.
- Use `structuredClone` for deep copies; spread for shallow.
- `Object.hasOwn` is the safe way to check for own properties.

## Further reading

- MDN, *Working with objects*.
- MDN, *structuredClone()*.
- Next: [Classes](05-classes.md).
