# Chapter 05 — Classes

> "Classes are syntactic sugar over JavaScript's prototype model. They read like classes in other languages, but underneath they're functions and objects you already know."

## Learning objectives

By the end of this chapter you will be able to:

- Declare a class with fields, methods, getters/setters, and static members.
- Use private fields (`#name`) for true encapsulation.
- Extend a class with `extends` and call `super` correctly.
- Decide when a class is the right abstraction (and when a plain object or factory function is better).

## Prerequisites & recap

- [Objects](04-objects.md) — literals, methods, reference semantics.
- [Functions](03-functions.md) — `this`, arrow vs. regular.

## The simple version

A class is a blueprint for creating objects that share the same shape and behaviour. You define the initial state in a `constructor`, attach behaviour as methods, and create instances with `new`. JavaScript classes are genuinely just a cleaner syntax for the prototype-based pattern that existed before — `typeof MyClass` is literally `"function"`. The real additions are **private fields** (prefixed with `#`, truly inaccessible from outside) and a readable inheritance syntax (`extends` / `super`).

Use a class when you have a clear concept with internal state and multiple related methods. For everything else — configuration objects, one-off helpers, stateless utilities — a plain object or a module-level function is simpler and lighter.

## In plain terms (newbie lane)

This chapter is really about **Classes**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  class User                         class Admin extends User
  ┌──────────────────────────┐       ┌──────────────────────────┐
  │  #password  (private)    │       │  perms     (public)      │
  │  id         (public)     │       │  can(action)             │
  │  name       (public)     │       └────────────┬─────────────┘
  │  greet()                 │                    │ extends
  │  get email()             │                    │
  │  static fromJSON()       │       User.prototype
  └──────────────────────────┘       ┌──────────────────────────┐
         │                           │  greet()                 │
         │ new User(...)             │  get email()             │
         ▼                           └──────────────────────────┘
  ┌──────────────────────────┐                    │
  │  instance                │                    ▼
  │  { id: 1, name: "Ada",  │       Object.prototype → null
  │    #password: "***" }    │
  └──────────────────────────┘
```

*Figure 5-1. Class structure, inheritance chain, and instance layout.*

## Concept deep-dive

### Class syntax

```js
class User {
  #password;
  static domain = "example.com";

  constructor(id, name, password) {
    this.id = id;
    this.name = name;
    this.#password = password;
  }

  greet() {
    return `hi, ${this.name}`;
  }

  get email() {
    return `${this.name}@${User.domain}`;
  }

  set password(p) {
    if (p.length < 8) throw new Error("too short");
    this.#password = p;
  }

  checkPassword(p) {
    return p === this.#password;
  }

  static fromJSON(json) {
    return new User(json.id, json.name, json.pw);
  }
}
```

**Why this syntax?** Before ES2015, you'd write `function User(id) { this.id = id; }` and manually attach methods to `User.prototype`. The `class` keyword bundles all of that into a readable block, enforces `new` (calling `User()` without `new` throws), and adds features like `static` and `#private` that the old syntax couldn't express.

### Private fields (`#`)

```js
const u = new User(1, "Ada", "s3cret!");
u.#password;   // SyntaxError — truly inaccessible outside the class
```

This isn't a convention like Python's `_name`. The `#` prefix is enforced at the language level — the engine won't let you access it. Private fields are the only way to guarantee encapsulation in JavaScript.

**Why `#` and not `private`?** The TC39 committee considered the `private` keyword but chose `#` because it makes private access syntactically distinct — you can never accidentally confuse `this.name` (public) with `this.#name` (private). It also makes parsing easier for engines and tooling.

### Inheritance with `extends` and `super`

```js
class Admin extends User {
  constructor(id, name, password, perms) {
    super(id, name, password);
    this.perms = perms;
  }

  can(action) {
    return this.perms.includes(action);
  }
}
```

Rules:
- You **must** call `super()` before using `this` in a derived constructor.
- `super.method()` calls the parent's version.
- A class can only extend one parent (no multiple inheritance).

**Why call `super` first?** The parent constructor initializes the object. Until `super()` runs, `this` doesn't exist — there's no object to set properties on. This ordering is enforced to prevent half-initialized objects.

### `instanceof` and constructor

```js
const admin = new Admin(1, "Ada", "pass", ["delete"]);
admin instanceof Admin;   // true
admin instanceof User;    // true — walks the prototype chain
admin.constructor === Admin;  // true
```

### Static members

Static fields and methods belong to the class itself, not to instances:

```js
class Timer {
  static #count = 0;
  static next() { return ++Timer.#count; }
}

Timer.next(); // 1
Timer.next(); // 2
```

**Why use statics?** Factory methods (`fromJSON`, `create`), constants, and counters that are conceptually tied to the class but not to any instance.

### Getters and setters

Getters and setters let you expose computed properties or add validation without changing how consumers access the data:

```js
class Circle {
  #radius;
  constructor(r) { this.#radius = r; }

  get area() { return Math.PI * this.#radius ** 2; }

  get radius() { return this.#radius; }
  set radius(r) {
    if (r < 0) throw new RangeError("radius must be non-negative");
    this.#radius = r;
  }
}

const c = new Circle(5);
c.area;       // 78.54... — accessed like a property, computed on the fly
c.radius = 10; // validation runs in the setter
```

### Classes are prototypes under the hood

```js
typeof User;               // "function"
User.prototype.greet;      // [Function: greet]
```

`class` is syntactic sugar. Methods live on `Class.prototype`. Instances delegate to that prototype. Understanding this connection is key to debugging — and it's the subject of [Chapter 06](06-prototypes.md).

### When to use a class vs. alternatives

| Use a class when... | Use a factory function when... | Use a plain object when... |
|---|---|---|
| Multiple instances share behaviour | You want true private state without `#` (closure-based) | The data is static configuration |
| Lifecycle matters (constructor, cleanup) | You don't need `instanceof` | There are no methods beyond simple accessors |
| You need inheritance | You want to avoid `new` and `this` | JSON serialization is the primary concern |

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| `class` as sugar over prototypes | Two mental models (class syntax + prototype reality) | Languages with true classes (Java, C#) don't have this duality |
| `#` for private fields | Unusual syntax; can't access in tests without workarounds | TypeScript's `private` offers compile-time-only privacy with test access |
| Single inheritance only | No mixins built-in | Use composition or mixin patterns when you need multiple behaviour sources |
| `new` required | Easy to forget (fixed by `class` throwing without it) | Factory functions don't need `new` |

## Production-quality code

```js
class EventEmitter {
  #listeners = new Map();

  on(event, handler) {
    if (typeof handler !== "function") {
      throw new TypeError(`handler must be a function, got ${typeof handler}`);
    }
    if (!this.#listeners.has(event)) {
      this.#listeners.set(event, []);
    }
    this.#listeners.get(event).push(handler);
    return this;
  }

  off(event, handler) {
    const handlers = this.#listeners.get(event);
    if (!handlers) return this;
    const idx = handlers.indexOf(handler);
    if (idx !== -1) handlers.splice(idx, 1);
    return this;
  }

  emit(event, ...args) {
    const handlers = this.#listeners.get(event);
    if (!handlers) return false;
    for (const handler of handlers) {
      handler(...args);
    }
    return true;
  }

  listenerCount(event) {
    return this.#listeners.get(event)?.length ?? 0;
  }
}

class Counter {
  #n = 0;
  increment() { this.#n++; return this; }
  decrement() { this.#n--; return this; }
  get value() { return this.#n; }
  reset() { this.#n = 0; return this; }
}
```

## Security notes

- **Private fields prevent external tampering.** Unlike the `_convention` pattern, `#fields` can't be accessed via `obj["#field"]` or reflection. They're truly private — important for security-sensitive state like tokens or passwords.
- **`instanceof` can be spoofed.** An attacker can override `Symbol.hasInstance` to make `instanceof` return whatever they want. Don't use `instanceof` as a security gate — validate data shapes instead.

## Performance notes

- Class instantiation (`new`) allocates an object and sets up the prototype chain. This is highly optimized in V8 — comparable to calling a factory function.
- Methods on the prototype are shared across all instances (one copy in memory). Arrow methods defined in the constructor (`this.greet = () => ...`) create a new function per instance — heavier but binds `this` automatically.
- Private fields have zero runtime overhead beyond a simple property access — the privacy check happens at parse/compile time.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ReferenceError: Must call super constructor before accessing 'this'` | Using `this` before `super()` in a derived constructor | Move `super()` to the first line of the constructor |
| Arrow method doesn't appear on `prototype` | `this.greet = () => ...` in constructor creates an instance property | Use method shorthand in the class body if you need prototype sharing |
| `TypeError: Class constructor X cannot be invoked without 'new'` | Calling `MyClass()` instead of `new MyClass()` | Always use `new` with classes |
| Everything is a class — even stateless utilities | Over-applying OOP patterns | Export plain functions for stateless operations |
| Can't test private fields | `#fields` are truly inaccessible | Test through the public API; private state is an implementation detail |

## Practice

**Warm-up.** Write a `Point` class with `x`, `y` properties and a `distanceTo(other)` method using the distance formula.

**Standard.** Refactor a module that uses module-level `let` variables and exported functions into a class. Add tests to verify behaviour is identical.

**Bug hunt.** Why does this code throw?

```js
class B extends A {
  constructor() {
    this.x = 1;
    super();
  }
}
```

**Stretch.** Use a private field `#attempts` to implement a read-only counter that tracks how many times a method has been called.

**Stretch++.** Write a tiny event emitter class with `on(event, handler)`, `emit(event, ...args)`, and `off(event, handler)`. Test it with `node:test`.

<details><summary>Show solutions</summary>

**Warm-up.**

```js
class Point {
  constructor(x, y) { this.x = x; this.y = y; }
  distanceTo(other) {
    return Math.hypot(this.x - other.x, this.y - other.y);
  }
}
```

**Bug hunt.**

```js
// Must call super() BEFORE using this in a derived constructor.
// Fix: swap the lines.
class B extends A {
  constructor() {
    super();
    this.x = 1;
  }
}
```

**Stretch++.**

```js
class EventEmitter {
  #listeners = new Map();
  on(event, fn) {
    if (!this.#listeners.has(event)) this.#listeners.set(event, []);
    this.#listeners.get(event).push(fn);
    return this;
  }
  emit(event, ...args) {
    for (const fn of this.#listeners.get(event) ?? []) fn(...args);
  }
  off(event, fn) {
    const fns = this.#listeners.get(event);
    if (fns) this.#listeners.set(event, fns.filter(f => f !== fn));
  }
}
```

</details>

## Quiz

1. A class in JavaScript is:
    (a) A new type primitive
    (b) Syntactic sugar over prototypes
    (c) An alias for `Object`
    (d) Compile-time only

2. Private field syntax is:
    (a) `_name`
    (b) `#name`
    (c) `private name`
    (d) `__name__`

3. In a subclass constructor, you must call `super()`:
    (a) Optionally
    (b) Before using `this`
    (c) After using `this`
    (d) Only if the parent has fields

4. Static members belong to:
    (a) Each instance
    (b) The class itself
    (c) The prototype
    (d) The global scope

5. Classes vs. factory functions:
    (a) Classes always win
    (b) Factories always win
    (c) Pick based on the use case
    (d) Identical performance and semantics

**Short answer:**

6. What does `instanceof` actually check?
7. When should you prefer a plain object or factory function over a class?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-c. 6 — `instanceof` walks the prototype chain of the left operand and checks if any prototype matches the `prototype` property of the right operand. 7 — When you have no shared behaviour, no lifecycle, or when the data is simple configuration / JSON — plain objects are lighter and easier to serialize.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-classes — mini-project](mini-projects/05-classes-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Classes are syntactic sugar over prototypes — `typeof MyClass === "function"`.
- Private fields (`#name`) provide true encapsulation enforced by the engine.
- `extends` / `super` give you clean single inheritance; call `super()` before `this`.
- Use classes when state + behaviour cohere; prefer plain objects or functions for simpler cases.

## Further reading

- MDN, *Classes*.
- MDN, *Private class features*.
- Next: [Prototypes](06-prototypes.md).
