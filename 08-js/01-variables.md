# Chapter 01 — Variables

> "JavaScript has three ways to declare a variable. Only two of them are worth using."

## Learning objectives

By the end of this chapter you will be able to:

- Declare variables with `let` and `const` and explain why `var` is obsolete.
- Distinguish block scope from function scope and identify when scope matters.
- Describe all seven JavaScript primitive types and the object umbrella.
- Differentiate `null` from `undefined` and apply each correctly.
- Explain hoisting and the temporal dead zone.

## Prerequisites & recap

- Any prior programming language — the [Python path](../01-python/README.md) helps.
- Node.js 20+ installed: `node --version`.

## The simple version

Every variable in JavaScript is a named box that holds a value. You create the box with a keyword — `const` makes a box whose label is permanent (you can never point it at a different value), while `let` makes a box you can re-label later. A third keyword, `var`, exists from JavaScript's early days but has confusing scoping rules, so you should pretend it doesn't exist in new code.

Values themselves come in two flavours: **primitives** (numbers, strings, booleans, and a few special singletons) and **objects** (everything else — arrays, functions, dates, your own data). The language uses two keywords to represent "nothing": `undefined` means "nobody assigned this yet" and `null` means "I deliberately set this to nothing."

## In plain terms (newbie lane)

This chapter is really about **Variables**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Declaration     Scope          Reassign?
  ──────────────────────────────────────────
  const x = 1     block { }       NO
  let   y = 2     block { }       YES
  var   z = 3     function()      YES  ← avoid
  ──────────────────────────────────────────

  Hoisting timeline (top → bottom = execution order):

  ┌─────────────────────────────────────────┐
  │  var z     → hoisted, init to undefined │
  │  let y     → hoisted, but in TDZ ░░░░░ │
  │  const x   → hoisted, but in TDZ ░░░░░ │
  │  ...                                    │
  │  const x = 1  ← TDZ ends here          │
  │  let   y = 2  ← TDZ ends here          │
  │  var   z = 3  ← assigns (was undefined)│
  └─────────────────────────────────────────┘

  ░░░ = temporal dead zone: accessing throws ReferenceError
```

*Figure 1-1. Scope, reassignment, and hoisting for each declaration keyword.*

## Concept deep-dive

### Three declarations — and why you only need two

```js
var   a = 1;   // legacy — function-scoped, hoisted to undefined
let   b = 2;   // modern — block-scoped
const c = 3;   // modern — block-scoped, cannot be reassigned
```

Always prefer `const`. Use `let` only when you genuinely need to reassign. Never use `var` in new code.

**Why?** `const` communicates intent: "this binding won't change." Readers can stop tracking reassignment and focus on what the value *does*. `let` signals "watch out — this will change." `var` signals nothing useful because its scope leaks out of blocks, creating bugs that `let` and `const` were specifically designed to prevent.

### `const` doesn't mean "immutable"

`const` freezes the *binding* — the name-to-value arrow — not the value itself:

```js
const xs = [1, 2, 3];
xs.push(4);         // fine — you mutated the array, not the binding
xs = [];            // TypeError — you tried to rebind const
```

If you truly want to freeze the value, call `Object.freeze(xs)`. But beware: `Object.freeze` is shallow — nested objects inside a frozen object can still be mutated.

**Why does `const` work this way?** Because the alternative — deep immutability by default — would require the engine to recursively freeze every nested structure on every assignment, which is expensive and often unnecessary. The binding-level guarantee is cheap and catches the most common class of bugs (accidental reassignment).

### Block scope vs. function scope

```js
function demo() {
  if (true) {
    let   x = 1;
    var   y = 2;
  }
  // x is NOT accessible here — block-scoped, stays inside { }
  // y IS accessible here — function-scoped, leaked out of the if
}
```

Block scope matches the mental model you already have from Python, C, Java, or Rust: a variable lives inside the braces where you declared it. `var`'s function scope is a historical accident from JavaScript's hurried ten-day creation in 1995 — Brendan Eich modeled it on a mix of Java and Scheme, and function scope was the compromise.

### Hoisting and the temporal dead zone

All three keywords hoist their declarations to the top of their scope — but they differ in what happens between the hoist and the actual line:

- **`var`**: hoisted *and initialized to `undefined`*. You can read it before the line and get `undefined` silently — a recipe for subtle bugs.
- **`let` / `const`**: hoisted but placed in a **temporal dead zone (TDZ)**. Any access before the declaration line throws a `ReferenceError`. This is a feature, not a bug — it forces you to declare before you use, catching mistakes at the point of error rather than silently propagating `undefined`.

```js
console.log(x); // undefined — var is already initialized
console.log(y); // ReferenceError — let is in the TDZ
var x = 1;
let y = 2;
```

### The seven primitives

JavaScript has exactly seven primitive types:

| Type        | Example          | Notes                                         |
|-------------|------------------|-----------------------------------------------|
| `number`    | `42`, `3.14`     | 64-bit IEEE-754 float — one type for ints and floats |
| `bigint`    | `9007199254740993n` | Arbitrary-precision integers                |
| `string`    | `"hello"`        | Unicode text, immutable                       |
| `boolean`   | `true`, `false`  |                                               |
| `undefined` | `undefined`      | "never assigned"                              |
| `null`      | `null`           | "intentionally empty"                         |
| `symbol`    | `Symbol("id")`   | Unique identifiers, used as object keys       |

Everything else — arrays, functions, dates, regex, your custom objects — is an **object**.

**Why only one number type?** Early JavaScript targeted non-programmers building web forms. Having separate int and float types (like Java) was deemed unnecessary complexity. The trade-off: you can't safely represent integers above `2^53 - 1` with `number`, which is why `bigint` was added later.

### `null` vs. `undefined`

- `undefined` is the language's default: an uninitialized variable, a missing function argument, a function that doesn't `return`, or a property that doesn't exist.
- `null` is *your* explicit signal meaning "I checked, and there's nothing here."

Prefer `null` for intentional absences in your own APIs. Don't mix both — pick a convention and stick to it. Most codebases treat `undefined` as "the system's nothing" and `null` as "the developer's nothing."

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| `const` by default | Verbosity when you *do* reassign | If your language has pattern-matching/destructuring that obviates reassignment entirely (e.g., Rust `let` is immutable by default) |
| Block scope via `let`/`const` | Breaks ancient `var`-dependent code | Never — block scope is strictly better for new code |
| Single `number` type | Precision loss above 2^53 | Languages with separate int types (Go, Rust) avoid this entirely |
| `null` *and* `undefined` | Two ways to say "nothing" creates confusion | Most languages pick one (Python's `None`, Rust's `Option`) |
| Shallow `Object.freeze` | Deep freeze is expensive | Immutable data structures (Immer, Immutable.js) when you need guarantees |

## Production-quality code

```js
"use strict";

const MAX_RETRIES = 3;
const DEFAULT_TIMEOUT_MS = 5_000;

function fetchWithRetry(url, { retries = MAX_RETRIES, timeout = DEFAULT_TIMEOUT_MS } = {}) {
  let attempt = 0;

  while (attempt < retries) {
    attempt += 1;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = fetch(url, { signal: controller.signal });
      clearTimeout(id);
      return response;
    } catch {
      clearTimeout(id);
      if (attempt >= retries) throw new Error(`Failed after ${retries} attempts: ${url}`);
    }
  }
}

const DAYS = Object.freeze(["mon", "tue", "wed", "thu", "fri", "sat", "sun"]);

for (const day of DAYS) {
  console.log(day);
}
```

## Security notes

- **Accidental globals.** In sloppy mode (no `"use strict"`), assigning to an undeclared variable creates a global. A typo like `usrname = input` silently creates `globalThis.usrname`. Always use strict mode (automatic inside ES modules) and always declare with `const` or `let`.
- **Prototype pollution via `var`.** In old code, `var` in the global scope creates a property on `globalThis`, which can collide with built-in names or be overwritten by malicious input. `let`/`const` at the top level do not attach to `globalThis`.

## Performance notes

- `const` vs. `let` vs. `var` have no measurable runtime performance difference in modern engines (V8, SpiderMonkey, JSC). The choice is entirely about correctness and readability.
- `Object.freeze` has a one-time cost at freeze time and a negligible cost per property access (the engine checks the frozen flag). For hot paths with large objects, profile before freezing.
- Temporal dead zone checks are optimized away by JIT compilers once the engine proves the access is safe.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Variable is `undefined` when you expected a value | Reading a `var` before its assignment line — hoisting initialized it to `undefined` silently | Switch to `let`/`const`; the TDZ `ReferenceError` makes the bug obvious |
| `const obj = {}; obj.x = 1` "works" but you expected an error | `const` freezes the binding, not the value | Use `Object.freeze(obj)` if you need value immutability |
| Loop closure captures the wrong value: `[3, 3, 3]` instead of `[0, 1, 2]` | Using `var` in a `for` loop — all closures share the same function-scoped variable | Use `let` — each iteration gets its own block-scoped copy |
| `ReferenceError: Cannot access 'x' before initialization` | Accessing a `let`/`const` variable before its declaration line (TDZ) | Move the declaration above the first access |
| Implicit global created by a typo | Sloppy mode + missing declaration keyword | Add `"use strict"` or use ES modules (strict by default) |

## Practice

**Warm-up.** Declare a `const` holding your name, a `let` holding your age, and print both. Try reassigning the `const` and observe the error.

**Standard.** Take a file full of `var` declarations and convert each to `let` or `const`. For each, decide which is appropriate and note what breaks.

**Bug hunt.** Predict the output of this code, then run it to verify:

```js
const fns = [];
for (var i = 0; i < 3; i++) fns.push(() => i);
console.log(fns.map(f => f()));
```

Now change `var` to `let` and predict again.

**Stretch.** Call `Object.freeze` on a nested object `{ a: 1, inner: { b: 2 } }`. Verify that `inner.b` can still be mutated. Write a `deepFreeze` function that recursively freezes all nested objects.

**Stretch++.** Write a short code sample that demonstrates the temporal dead zone. Include a comment explaining why the TDZ is useful rather than harmful.

<details><summary>Show solutions</summary>

**Bug hunt.**

```js
// With var: [3, 3, 3] — all closures share the same function-scoped i,
// which is 3 after the loop finishes.
// With let: [0, 1, 2] — each iteration gets its own block-scoped i.
```

**Stretch.**

```js
function deepFreeze(obj) {
  Object.freeze(obj);
  for (const val of Object.values(obj)) {
    if (val !== null && typeof val === "object" && !Object.isFrozen(val)) {
      deepFreeze(val);
    }
  }
  return obj;
}

const data = deepFreeze({ a: 1, inner: { b: 2 } });
data.inner.b = 99;
console.log(data.inner.b); // still 2
```

**Stretch++.**

```js
function demo() {
  // console.log(x); // ReferenceError — x is in the TDZ
  const x = 42;
  console.log(x);    // 42
}
// The TDZ catches "use before declare" bugs at the exact point of error,
// rather than silently returning undefined (which var does).
```

</details>

## Quiz

1. Which declaration strategy should you follow?
    (a) Always `var`
    (b) Always `let`
    (c) Always `const`
    (d) `const` by default, `let` when you must reassign

2. What happens with `const x = []; x.push(1);`?
    (a) `TypeError` — `x` is constant
    (b) Works fine — the array is mutated, not the binding
    (c) Returns `undefined`
    (d) Replaces `x` with a new array

3. What is `var`'s scope?
    (a) Block
    (b) Function
    (c) Global always
    (d) File / module

4. What happens when you access a `let` variable before its declaration?
    (a) You get `undefined`
    (b) `ReferenceError` via the temporal dead zone
    (c) You get `null`
    (d) You get `NaN`

5. Which of these is a primitive type?
    (a) Array
    (b) Object
    (c) `bigint`
    (d) `Promise`

**Short answer:**

6. Why is `var` avoided in modern JavaScript?
7. Explain the difference between `null` and `undefined` with one sentence each.

*Answers: 1-d, 2-b, 3-b, 4-b, 5-c. 6 — `var` is function-scoped and hoists to `undefined`, causing silent bugs that block-scoped `let`/`const` prevent. 7 — `undefined` is the system default for "never assigned"; `null` is the developer's explicit signal for "intentionally empty."*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-variables — mini-project](mini-projects/01-variables-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Use `const` by default, `let` when you must reassign, and never `var`.
- `const` freezes the binding, not the value — use `Object.freeze` for value immutability.
- JavaScript has seven primitives; everything else is an object.
- The temporal dead zone turns silent `undefined` bugs into loud `ReferenceError`s — embrace it.

## Further reading

- MDN, *JavaScript Reference — Statements: `let`, `const`, `var`*.
- Axel Rauschmayer, *JavaScript for Impatient Programmers* — Ch. 11 Variables and assignment.
- Next: [Comparisons](02-comparisons.md).
