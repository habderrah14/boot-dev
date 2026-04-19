# Chapter 02 — Comparisons

> "JavaScript has two equality operators. Use the strict one — or spend your weekends debugging coercion tables."

## Learning objectives

By the end of this chapter you will be able to:

- Use `===` and `!==` everywhere and explain why `==` is dangerous.
- List all falsy values and predict truthy/falsy checks.
- Choose between `??` and `||` for default values.
- Safely traverse nested objects with optional chaining (`?.`).
- Test for `NaN` correctly.

## Prerequisites & recap

- [Variables](01-variables.md) — primitives, `null` vs. `undefined`.

## The simple version

When you compare two values in JavaScript, you have a choice: ask "are these the same type *and* the same value?" (`===`) or ask "if I squint and convert types, could these be equal?" (`==`). The second one is almost always wrong. `0 == "0"` is `true`. `"" == false` is `true`. `null == undefined` is `true`. These surprises have caused enough production bugs that the universal advice is simple: always use `===`.

JavaScript also has a notion of "truthy" and "falsy" — every value, when used in a boolean context like an `if`, is treated as either true or false. Only seven values are falsy; everything else (including empty arrays and objects) is truthy. Once you memorize the falsy list, you can read any conditional in any codebase.

## In plain terms (newbie lane)

This chapter is really about **Comparisons**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  a == b                          a === b
  ──────                          ───────
  ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
  │ operands │───>│ coerce   │───>│ compare  │    │ operands │───>│ compare  │
  │  a , b   │    │ types to │    │ values   │    │  a , b   │    │ type AND │
  └─────────┘    │ match    │    └──────────┘    └─────────┘    │ value    │
                  └──────────┘                                   └──────────┘
                  ↑ surprise!                                   ↑ predictable

  Falsy values (memorize these 7):
  ┌───────────────────────────────────────────────────┐
  │  false   0   -0   0n   ""   null   undefined  NaN │
  └───────────────────────────────────────────────────┘
  Everything else is truthy — including "0", "false", [], {}
```

*Figure 2-1. Loose vs. strict equality and the complete falsy list.*

## Concept deep-dive

### `===` vs. `==` — why coercion is the enemy

```js
0 == "0";            // true  — string coerced to number
0 == false;          // true  — boolean coerced to number
null == undefined;   // true  — special case in the spec
"" == 0;             // true  — both coerced to number 0
0 === "0";           // false — different types, done
```

`==` applies the *Abstract Equality Comparison Algorithm* — a set of type-coercion rules so complex that even experienced developers can't predict all outcomes. `===` applies *Strict Equality* — no coercion, same type required. Use `===` everywhere.

**Why does `==` exist at all?** JavaScript was designed in ten days for non-programmers writing form validation. Loose equality was meant to be "forgiving." In practice, it forgives bugs into your codebase.

### Truthy and falsy

Every value in JavaScript has a boolean identity. The **falsy** values are exactly seven:

`false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`

Everything else is **truthy**, including values that surprise people:

```js
Boolean("0");      // true — non-empty string
Boolean("false");  // true — non-empty string
Boolean([]);       // true — object
Boolean({});       // true — object
```

**Why does this matter?** You'll see `if (user)` and `if (response.data)` everywhere. Understanding truthy/falsy tells you exactly which values slip through.

### `??` (nullish coalescing) vs. `||` (logical OR)

Both provide default values, but they disagree on what counts as "missing":

```js
"" || "default";     // "default" — empty string is falsy
"" ?? "default";     // ""        — empty string is not null/undefined

0 || 10;             // 10  — zero is falsy, probably a bug
0 ?? 10;             // 0   — zero is not null/undefined
```

- Use `??` when you want a default only for `null` or `undefined` (the "nullish" values).
- Use `||` when empty strings, `0`, and `false` should also trigger the default.

**Why two operators?** `||` predates `??` by decades. When JavaScript added `??` in ES2020, it was specifically to fix the bug where `0 || fallback` throws away a perfectly valid zero.

### `?.` — optional chaining

```js
user?.address?.street           // undefined if any hop is null/undef
users?.[0]?.name                // bracket access
callback?.()                    // call only if callback exists
```

Optional chaining short-circuits to `undefined` instead of throwing a `TypeError`. It replaced pages of `user && user.address && user.address.street` boilerplate.

**Why not use it everywhere?** Overuse hides bugs. If `user` should *always* exist, using `user?.name` silently returns `undefined` instead of crashing where the real problem is. Use `?.` only where `null`/`undefined` is a legitimate possibility.

### Deep equality

`===` on objects checks **reference equality** — "are these the exact same object in memory?" — not structural equality:

```js
{ a: 1 } === { a: 1 }   // false — different objects
const x = { a: 1 };
x === x;                 // true — same reference
```

For structural comparison:

- `JSON.stringify(a) === JSON.stringify(b)` — works for plain data (no functions, dates, regex, or circular refs).
- `node:util.isDeepStrictEqual(a, b)` — handles more types.
- Third-party: Lodash's `isEqual`.

### `NaN` — the value that isn't equal to itself

```js
NaN === NaN;         // false — by IEEE-754 spec
Number.isNaN(NaN);   // true  — correct test
isNaN("hello");      // true  — coerces string to NaN first, misleading
Number.isNaN("hello"); // false — no coercion, correct
```

Always use `Number.isNaN()`, never the global `isNaN()`.

### `typeof null === "object"` — the eternal bug

```js
typeof null;         // "object" — a bug from JavaScript's first implementation
```

This was a mistake in the original C implementation (null's type tag was 0, the same as object). It was never fixed because too much code depended on it. Check for null explicitly: `x === null`.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| `===` over `==` | Slightly more typing | Never — `===` is strictly better |
| `??` over `\|\|` | Two operators to learn | Use `\|\|` when you deliberately want to treat `0`/`""` as missing |
| Optional chaining `?.` | Can mask bugs if overused | Omit `?.` when the value *must* exist — let the TypeError crash loudly |
| Seven falsy values | Memorization required | Languages like Python have a simpler model (empty containers are falsy) |
| `NaN !== NaN` | Surprising | IEEE-754 mandates this; use `Number.isNaN` |

## Production-quality code

```js
function resolveConfig(userConfig) {
  const defaults = {
    port: 3000,
    host: "localhost",
    retries: 3,
    verbose: false,
  };

  return {
    port:    userConfig?.port    ?? defaults.port,
    host:    userConfig?.host    ?? defaults.host,
    retries: userConfig?.retries ?? defaults.retries,
    verbose: userConfig?.verbose ?? defaults.verbose,
  };
}

function shallowEqual(a, b) {
  if (a === b) return true;
  if (a === null || b === null) return false;
  if (typeof a !== "object" || typeof b !== "object") return false;

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.hasOwn(b, key) || a[key] !== b[key]) return false;
  }
  return true;
}

function safeParseNumber(input) {
  const n = Number(input);
  if (Number.isNaN(n)) return null;
  return n;
}
```

## Security notes

- **Type confusion in input validation.** Using `==` to compare user input can bypass checks. `0 == ""` is `true` — an empty password field could pass a check comparing against `0`. Always use `===`.
- **Prototype pollution via `typeof` checks.** `typeof null === "object"` means a null check like `if (typeof x === "object")` passes for `null`. Always add an explicit `x !== null` guard.

## Performance notes

- `===` is faster than `==` because it skips the coercion algorithm. The difference is negligible in practice, but there's no reason to use the slower, buggier option.
- Optional chaining (`?.`) compiles to simple null checks in modern engines — no overhead beyond a branch prediction.
- `Object.keys()` in `shallowEqual` allocates an array. For hot-path comparisons, consider caching keys or using a dedicated library.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `0 == ""` returns `true` unexpectedly | Loose equality coerces both to `0` | Use `===` |
| Default value of `0` is replaced: `count \|\| 10` gives `10` | `\|\|` treats `0` as falsy | Use `??` — it only triggers on `null`/`undefined` |
| `[1] == true` is `true` | Array → string → number coercion chain | Use `===`; it returns `false` |
| `typeof x === "object"` passes for `null` | The `typeof null` bug | Add `&& x !== null` |
| `NaN === NaN` is `false` | IEEE-754 spec | Use `Number.isNaN(x)` |

## Practice

**Warm-up.** Predict the result of each, then verify in the console:

```js
[] == false
[] === false
null == undefined
null === undefined
```

**Standard.** Implement `shallowEqual(a, b)` for plain objects. It should return `true` when both objects have the same keys and all values pass `===`.

**Bug hunt.** A colleague wrote `const limit = userCount || 10;` and users are reporting that a count of `0` always shows `10`. Explain why and fix it.

**Stretch.** Write a `safeGet(obj, path, defaultValue)` function that uses optional chaining logic (but works with a string path like `"user.address.street"`) and returns `defaultValue` if any segment is `null`/`undefined`.

**Stretch++.** Read the [ECMAScript spec's Abstract Equality Comparison](https://tc39.es/ecma262/#sec-abstract-equality-comparison) and explain, step by step, why `0 == "0"` is `true`.

<details><summary>Show solutions</summary>

**Warm-up.**

```js
[] == false;       // true  — [] → "" → 0, false → 0, 0 == 0
[] === false;      // false — different types
null == undefined; // true  — special spec rule
null === undefined; // false — different types
```

**Bug hunt.**

```js
// 0 is falsy, so || skips it and returns 10.
// Fix: use nullish coalescing.
const limit = userCount ?? 10;
```

**Stretch.**

```js
function safeGet(obj, path, defaultValue = undefined) {
  const keys = path.split(".");
  let current = obj;
  for (const key of keys) {
    if (current == null) return defaultValue;
    current = current[key];
  }
  return current ?? defaultValue;
}
```

</details>

## Quiz

1. When should you use `==`?
    (a) Always
    (b) Never — prefer `===`
    (c) For numbers only
    (d) For strings only

2. Which of these is truthy?
    (a) `"0"`
    (b) `0`
    (c) `null`
    (d) `NaN`

3. What does `0 ?? 5` evaluate to?
    (a) `0`
    (b) `5`
    (c) `NaN`
    (d) `TypeError`

4. What does `user?.name` do when `user` is `null`?
    (a) Throws `TypeError`
    (b) Returns `undefined`
    (c) Same as `user.name`
    (d) Returns an empty string

5. How does `Number.isNaN(x)` differ from `isNaN(x)`?
    (a) They're identical
    (b) `Number.isNaN` is stricter — no type coercion
    (c) `isNaN` is stricter
    (d) Both are deprecated

**Short answer:**

6. When is `||` the right choice over `??`?
7. Why does `typeof null` return `"object"`?

*Answers: 1-b, 2-a, 3-a, 4-b, 5-b. 6 — Use `||` when you want empty strings, `0`, and `false` to also trigger the default (e.g., treating all falsy values as "missing"). 7 — A bug in JavaScript's original C implementation where null's type tag was 0 (same as object); never fixed for backward compatibility.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-comparisons — mini-project](mini-projects/02-comparisons-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Always use `===` — loose equality's coercion rules are a bug factory.
- Use `??` for defaults when `null`/`undefined` are the only "missing" signals; use `||` when all falsy values count.
- Optional chaining (`?.`) replaces verbose null-guard chains but shouldn't mask bugs where values must exist.
- `NaN !== NaN` is by spec — use `Number.isNaN()`.

## Further reading

- MDN, *Equality comparisons and sameness*.
- MDN, *Nullish coalescing operator (??)*.
- Next: [Functions](03-functions.md).
