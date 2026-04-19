# Chapter 03 — Functions

> "Functions are first-class values in JavaScript. They're also where `this` lives — and `this` is mostly why people argue about JavaScript."

## Learning objectives

By the end of this chapter you will be able to:

- Declare functions four ways and choose the right form for each situation.
- Explain how arrow functions inherit `this` and why that matters for callbacks.
- Use default parameters, rest parameters, and spread syntax.
- Write higher-order functions that accept and return functions.
- Use `bind`, `call`, and `apply` to control `this` explicitly.

## Prerequisites & recap

- [Variables](01-variables.md) — `const`, `let`, hoisting, TDZ.

## The simple version

A function in JavaScript is a value — you can store it in a variable, pass it as an argument, return it from another function. There are four ways to write one, but the two you'll use daily are **function declarations** (the classic `function name() {}` form) and **arrow functions** (`() => {}`). The critical difference is how they handle the keyword `this`: a regular function gets its own `this` determined by *how it's called*, while an arrow function inherits `this` from wherever it was *defined*. This one distinction eliminates an entire class of bugs in callbacks and event handlers.

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
  Four declaration forms:
  ─────────────────────────────────────────────────────────
  function add(a, b) { return a + b; }   ← declaration
  const add = function(a, b) { ... };    ← expression
  const add = (a, b) => a + b;          ← arrow
  const f = function fact(n) { ... };    ← named expression
  ─────────────────────────────────────────────────────────

  How `this` binds:
  ┌──────────────────────┐    ┌──────────────────────┐
  │  function() { this } │    │  () => { this }      │
  │                      │    │                      │
  │  this = determined   │    │  this = captured     │
  │  at CALL site        │    │  from DEFINITION     │
  │  (dynamic)           │    │  scope (lexical)     │
  └──────────────────────┘    └──────────────────────┘
       obj.method()               setTimeout(() => ...)
       this === obj               this === outer this
```

*Figure 3-1. Declaration forms and the two `this`-binding models.*

## Concept deep-dive

### Four declaration forms

```js
function declared(a, b) { return a + b; }          // function declaration

const expr = function (a, b) { return a + b; };    // function expression

const arrow = (a, b) => a + b;                     // arrow function

const named = function fact(n) {                    // named function expression
  return n < 2 ? 1 : n * fact(n - 1);
};
```

**Function declarations** are hoisted fully — you can call them before the line they appear on. This is the only form where hoisting actually helps readability (putting the main logic at the top and helpers below).

**Expressions and arrows** obey `const`/`let` TDZ rules — they exist only after the assignment line. This is usually what you want because it prevents accidental forward references.

**Why four forms?** Historical layering. Declarations came first (1995). Expressions enabled functions-as-values. Named expressions added self-reference for recursion. Arrows (ES2015) fixed the `this` problem. Each solved a real pain point.

### Arrow functions and `this`

Regular functions bind `this` at the **call site** — whoever calls the function determines what `this` is. Arrow functions capture `this` from the **surrounding lexical scope** at definition time.

```js
class Clock {
  constructor() {
    this.seconds = 0;

    // BUG: regular function creates its own `this`
    setInterval(function () { this.seconds++; }, 1000);

    // FIX: arrow inherits `this` from the constructor
    setInterval(() => this.seconds++, 1000);
  }
}
```

**Why does this matter?** Before arrows, you had to write `const self = this;` or `.bind(this)` on every callback. Arrows eliminated that entire pattern. The rule is simple: use arrows for callbacks, use regular functions for methods and constructors.

**Arrow functions cannot:**
- Be used as constructors (`new` throws `TypeError`).
- Access `arguments` (use rest parameters `...args` instead).
- Be used as generator functions.

### Default, rest, and spread

```js
function greet(name = "world") {
  return `hello, ${name}`;
}

function sum(...nums) {
  return nums.reduce((a, b) => a + b, 0);
}

const pair = [1, 2];
const more = [0, ...pair, 3];      // [0, 1, 2, 3]
```

- **Default parameters** replace the old `name = name || "default"` pattern (which breaks on falsy values like `0` or `""`).
- **Rest parameters** (`...args`) collect remaining arguments into a real array — unlike the legacy `arguments` object, which is array-like but not an actual array.
- **Spread** (`...arr`) expands an iterable into individual arguments or array elements.

### Callbacks and higher-order functions

A function that takes another function as an argument (or returns one) is called **higher-order**:

```js
[1, 2, 3].map(x => x * x);           // callback pattern

const adder = n => x => x + n;        // returns a function
const add5 = adder(5);
add5(3);     // 8
```

**Why are higher-order functions important?** They're the foundation of functional-style JavaScript — `map`, `filter`, `reduce`, event handlers, middleware chains, and promise combinators all depend on passing functions around.

### Closures

When a function references a variable from an outer scope, it "closes over" that variable — the variable survives even after the outer function returns:

```js
function counter() {
  let n = 0;
  return () => ++n;
}
const c = counter();
c(); // 1
c(); // 2
```

The returned arrow function keeps `n` alive. This is a **closure**. You've been using closures implicitly in every callback — now you have the name for it.

### `bind`, `call`, `apply`

These methods set `this` explicitly:

```js
function greet(greeting) {
  return `${greeting}, ${this.name}`;
}

greet.call({ name: "Ada" }, "Hi");           // "Hi, Ada"
greet.apply({ name: "Ada" }, ["Hi"]);        // "Hi, Ada" — args as array
const boundGreet = greet.bind({ name: "Ada" });
boundGreet("Hi");                             // "Hi, Ada"
```

- `call` invokes immediately with individual args.
- `apply` invokes immediately with an array of args.
- `bind` returns a new function with `this` permanently set.

**Why do these exist?** Before arrow functions, `bind` was the primary way to preserve `this` in callbacks. You'll still see it in legacy code and in situations where you need to partially apply arguments.

### Immediately Invoked Function Expressions (IIFE)

```js
(function () { /* private scope */ })();
```

Historically used to create private scope before `let`/`const` existed. Less needed now, but you'll encounter them in older codebases and in situations where you need a one-time initialization block with its own scope.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Arrows for callbacks | Can't use as constructors or methods | Use regular functions for object methods needing dynamic `this` |
| Lexical `this` in arrows | Can't change `this` after definition | Use `.bind()` or regular function if you need dynamic `this` binding |
| `arguments` object (legacy) | Array-like but not an array | Always use rest params (`...args`) in new code |
| Default params in signature | Evaluated per call (can use expressions) | In Python-style languages, defaults are evaluated once — JS re-evaluates each call, which is safer for mutable defaults |
| Four function forms | Cognitive overhead for learners | A language designed today would likely have only arrows + declarations |

## Production-quality code

```js
function debounce(fn, ms) {
  let timer = null;
  return function debounced(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

function throttle(fn, ms) {
  let last = 0;
  return function throttled(...args) {
    const now = Date.now();
    if (now - last < ms) return;
    last = now;
    return fn.apply(this, args);
  };
}

function once(fn) {
  let called = false;
  let result;
  return function (...args) {
    if (called) return result;
    called = true;
    result = fn.apply(this, args);
    return result;
  };
}

function pipe(...fns) {
  return (x) => fns.reduce((v, f) => f(v), x);
}
```

## Security notes

- **`Function()` constructor and `eval`.** Never build functions from user-supplied strings — `new Function("return " + userInput)()` is code injection. If you need dynamic behaviour, use a whitelist or a sandboxed interpreter.
- **`this` in global scope.** In sloppy mode, `this` in a standalone function is `globalThis`, giving access to the entire global object. Always use strict mode (or ES modules, which are strict by default) so `this` is `undefined` instead.

## Performance notes

- Arrow functions and regular functions have identical runtime performance in modern engines. The choice is about semantics, not speed.
- `bind` creates a new function object each time it's called. In hot loops binding the same function repeatedly, cache the bound version.
- Closures keep their outer scope's variables alive. If a closure captures a large object and lives longer than expected (e.g., stored in a long-lived cache), it can cause memory leaks. Be deliberate about what closures capture.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `this` is `undefined` in a callback | Used a regular function where `this` refers to the call site, not the class | Use an arrow function, or `.bind(this)` |
| Arrow method on an object — `this` is wrong | Arrow captures `this` from the surrounding scope (module/global), not the object | Use regular function syntax for object methods |
| Stack trace says `(anonymous)` | Unnamed function expression | Use named function expressions: `const fn = function myName() {}` |
| `arguments` is not iterable | `arguments` is array-like, not an array | Use rest params `...args`, or `Array.from(arguments)` |
| `new` on an arrow throws `TypeError` | Arrow functions don't have a `[[Construct]]` internal method | Use a regular function or class for constructors |

## Practice

**Warm-up.** Write an `add(a, b)` function three ways: declaration, expression, and arrow. Verify all three work.

**Standard.** Write a comparator function and use it to sort an array of objects by two keys (primary: `lastName`, secondary: `firstName`).

**Bug hunt.** Explain why `setInterval(function(){ this.tick(); }, 1000)` inside a class constructor breaks. Provide two fixes.

**Stretch.** Implement `once(fn)` — a higher-order function that ensures `fn` runs at most once. Subsequent calls return the first result.

**Stretch++.** Reimplement `Function.prototype.bind` from scratch (handle both `this` binding and partial application).

<details><summary>Show solutions</summary>

**Bug hunt.**

```js
// `this` in the callback is globalThis (or undefined in strict mode),
// not the class instance.
// Fix 1: arrow function
setInterval(() => this.tick(), 1000);
// Fix 2: bind
setInterval(function () { this.tick(); }.bind(this), 1000);
```

**Stretch.**

```js
function once(fn) {
  let called = false;
  let result;
  return function (...args) {
    if (called) return result;
    called = true;
    result = fn.apply(this, args);
    return result;
  };
}
```

**Stretch++.**

```js
Function.prototype.myBind = function (thisArg, ...boundArgs) {
  const fn = this;
  return function (...callArgs) {
    return fn.apply(thisArg, [...boundArgs, ...callArgs]);
  };
};
```

</details>

## Quiz

1. In an arrow function, `this` comes from:
    (a) The caller
    (b) A bound value
    (c) The surrounding lexical scope
    (d) It's always `undefined`

2. Arrow functions can:
    (a) Be used with `new`
    (b) Have their own `arguments` object
    (c) Neither — no `new`, no `arguments`
    (d) Both

3. `...args` in a parameter list is:
    (a) Spread syntax
    (b) Rest — collects remaining args into an array
    (c) A default parameter
    (d) Invalid syntax

4. Which form is fully hoisted (callable before its line)?
    (a) `function x() {}`
    (b) `const x = function() {}`
    (c) `const x = () => {}`
    (d) None of the above

5. `fn.bind(obj)` does what?
    (a) Calls `fn` immediately
    (b) Returns a new function with `this` permanently bound to `obj`
    (c) Mutates `fn`
    (d) Is deprecated

**Short answer:**

6. Why prefer arrow functions for callbacks?
7. Why should you name your function expressions?

*Answers: 1-c, 2-c, 3-b, 4-a, 5-b. 6 — Arrows inherit `this` from the enclosing scope, avoiding the common bug where a callback's `this` unexpectedly refers to the caller or global. 7 — Named expressions produce readable stack traces; anonymous functions show as "(anonymous)" in errors.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-functions — mini-project](mini-projects/03-functions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Arrow functions inherit `this` lexically — use them for callbacks and closures.
- Regular functions bind `this` dynamically — use them for object methods and constructors.
- Default/rest/spread make function signatures expressive and safe.
- Higher-order functions (accepting or returning functions) are the backbone of idiomatic JavaScript.

## Further reading

- MDN, *Functions — arrow functions, closures, rest parameters*.
- Kyle Simpson, *You Don't Know JS: Scope & Closures*.
- Next: [Objects](04-objects.md).
