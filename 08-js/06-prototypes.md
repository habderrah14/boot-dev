# Chapter 06 — Prototypes

> "Under every class, there's a prototype. Under every object, there's a chain. Understanding them takes most of JavaScript's mystery away."

## Learning objectives

By the end of this chapter you will be able to:

- Explain how JavaScript's prototype chain resolves property lookups.
- Distinguish `Constructor.prototype` from `instance.__proto__`.
- Use `Object.create`, `Object.getPrototypeOf`, and `Object.setPrototypeOf`.
- Describe how `instanceof` works and when it fails.
- Explain why classes are sugar over this mechanism.

## Prerequisites & recap

- [Objects](04-objects.md) — property access, `Object.hasOwn`.
- [Classes](05-classes.md) — `class`, `extends`, `super`.

## The simple version

Every object in JavaScript has a hidden link to another object called its **prototype**. When you access a property that doesn't exist on the object itself, JavaScript follows this link to the prototype, then to the prototype's prototype, and so on until it either finds the property or reaches the end of the chain (`null`). This is how methods defined on a class are shared across all instances without being copied — every instance links to the same `Class.prototype` object. The entire class system is built on top of this simple lookup mechanism.

## In plain terms (newbie lane)

This chapter is really about **Prototypes**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Property lookup for admin.greet():

  admin (instance)
  ┌─────────────────────┐
  │  id: 1              │  greet not here...
  │  perms: ["delete"]  │        │
  └─────────┬───────────┘        │
            │ [[Prototype]]      ▼
  Admin.prototype                │
  ┌─────────────────────┐        │
  │  can()              │  greet not here either...
  └─────────┬───────────┘        │
            │ [[Prototype]]      ▼
  User.prototype                 │
  ┌─────────────────────┐        │
  │  greet() ◄──────────│────────┘  FOUND! Use this one.
  │  get email()        │
  └─────────┬───────────┘
            │ [[Prototype]]
  Object.prototype
  ┌─────────────────────┐
  │  toString()         │
  │  hasOwnProperty()   │
  └─────────┬───────────┘
            │ [[Prototype]]
           null  ← end of chain
```

*Figure 6-1. Prototype chain walkthrough for method resolution.*

## Concept deep-dive

### Every object has a prototype

When you read `obj.x`, JavaScript runs this algorithm:

1. Look for `x` directly on `obj` (an "own" property).
2. If not found, look on `Object.getPrototypeOf(obj)`.
3. Continue up the chain until found, or until the prototype is `null`.

Writes always go directly on the object — they **shadow** the prototype's property rather than modifying it.

```js
const a = {};
Object.getPrototypeOf(a) === Object.prototype;  // true
Object.getPrototypeOf(Object.prototype);         // null — end of the line
```

**Why this design?** Prototype-based inheritance (invented by Self, adopted by JavaScript) is simpler than class-based inheritance at the engine level — you just link objects together. There's no separate "class" construct needed. JavaScript's `class` keyword is a later addition that generates the same prototype linkages under the hood.

### `Constructor.prototype` vs. `__proto__`

These two related but different concepts cause endless confusion:

- **`Constructor.prototype`** is a property on a function. It's the object that will become the prototype of instances created with `new Constructor()`.
- **`obj.__proto__`** (or `Object.getPrototypeOf(obj)`) is the actual prototype link of an existing object — the object it delegates to for property lookups.

```js
function User(name) { this.name = name; }
User.prototype.greet = function () { return `hi, ${this.name}`; };

const u = new User("Ada");
Object.getPrototypeOf(u) === User.prototype;    // true
u.greet();  // "hi, Ada" — found on User.prototype
```

**Why the confusing naming?** `prototype` was named before the mental model was clear. `__proto__` was a non-standard browser hack that became standardized. The modern API is `Object.getPrototypeOf` / `Object.setPrototypeOf`.

### How classes map to prototypes

```js
class User {
  greet() { return "hi"; }
}

typeof User;                    // "function"
typeof User.prototype.greet;    // "function"
```

When you write `greet()` in a class body, JavaScript puts it on `User.prototype`. When you `new User()`, the new object's `[[Prototype]]` is set to `User.prototype`. That's it — there's no magic beyond this linkage.

### The chain in action

```
instance → Class.prototype → Parent.prototype → Object.prototype → null
```

For an array:

```
[1,2,3] → Array.prototype → Object.prototype → null
```

This is why arrays have `.map()` (from `Array.prototype`) and `.toString()` (from `Object.prototype`).

### `Object.create` — explicit prototype setup

```js
const base = {
  hello() { return "hi"; },
};

const child = Object.create(base);
child.hello();                   // "hi" — found via prototype
Object.getPrototypeOf(child) === base;  // true
```

`Object.create(null)` creates a "bare" object with no prototype — useful for dictionaries where you don't want inherited properties like `toString` or `constructor` interfering.

### Shadowing (overriding)

Setting a property on an instance **shadows** (hides) the prototype's property without modifying it:

```js
child.hello = () => "custom";
child.hello();    // "custom" — own property wins
delete child.hello;
child.hello();    // "hi" — prototype version is still there
```

### `instanceof` under the hood

`a instanceof B` walks the prototype chain of `a` and checks if any prototype is `B.prototype`:

```js
const u = new User("Ada");
u instanceof User;   // true — User.prototype is in u's chain
u instanceof Object; // true — Object.prototype is in everyone's chain
```

**When does `instanceof` fail?** Across different realms (iframes, `vm.runInNewContext`), each realm has its own `Array`, `Object`, etc. An array from one realm fails `instanceof Array` in another. Use `Array.isArray()` instead.

### Performance of the chain

Method lookup walks the chain linearly. In practice:

- V8 caches lookups using *inline caches* and *hidden classes*, so the cost is near-zero for stable shapes.
- Deep chains (more than 3-4 levels) can slow down lookups and make code harder to reason about.
- Setting a prototype at runtime (`Object.setPrototypeOf`) deoptimizes the engine's hidden class system. Avoid it in production code.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Prototype-based inheritance | Flexible but unfamiliar to class-trained devs | Class-based languages (Java, C#) have a more rigid but predictable model |
| Shared methods on prototype | Memory efficient (one copy) | Per-instance arrow methods auto-bind `this` but use more memory |
| Delegation (not copying) | Method calls walk the chain at runtime | Copying ("stamping") all methods onto each instance avoids the walk but duplicates memory |
| `Object.create(null)` for dictionaries | Loses all inherited methods | Use `Map` instead for the cleanest key-value semantics |
| `instanceof` checks prototype chain | Breaks across realms | Use duck-typing or `Symbol.hasInstance` for cross-realm checks |

## Production-quality code

```js
function walkPrototypeChain(obj) {
  const chain = [];
  let current = obj;
  while (current !== null) {
    chain.push(current);
    current = Object.getPrototypeOf(current);
  }
  return chain;
}

function inheritsFrom(instance, Constructor) {
  let proto = Object.getPrototypeOf(instance);
  while (proto !== null) {
    if (proto === Constructor.prototype) return true;
    proto = Object.getPrototypeOf(proto);
  }
  return false;
}

function createDict() {
  return Object.create(null);
}

function mixin(target, ...sources) {
  for (const source of sources) {
    for (const key of Object.getOwnPropertyNames(source)) {
      const desc = Object.getOwnPropertyDescriptor(source, key);
      Object.defineProperty(target, key, desc);
    }
  }
  return target;
}
```

## Security notes

- **Prototype pollution.** If an attacker can set arbitrary keys on an object (e.g., via unchecked `JSON.parse` followed by recursive merge), they can set `__proto__` to inject properties that every object in the process inherits. This has led to real CVEs in libraries like `lodash.merge`. Always validate or whitelist keys from untrusted input.
- **Mutating `Object.prototype`.** Adding properties to `Object.prototype` affects every object globally. This is a vector for supply-chain attacks — a malicious npm package could modify `Object.prototype` to intercept all property lookups.

## Performance notes

- **Inline caches.** V8 (and other engines) cache prototype chain lookups. After the first access, repeated accesses to the same property on objects with the same shape are essentially O(1).
- **`Object.setPrototypeOf` is slow.** Changing an object's prototype after creation forces the engine to abandon its optimized hidden class and rebuild. Avoid it outside of initialization code.
- **Deep chains.** Each additional level in the chain is a cache miss on first access. Keep inheritance hierarchies shallow (2-3 levels max) for both performance and readability.
- **`Object.create(null)` dictionaries.** Slightly faster for key lookups than regular objects because there's no prototype chain to consult. Useful for large lookup tables.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `delete obj.method` doesn't remove the method | The method lives on the prototype, not the instance | You're deleting a shadow (or there's nothing to delete); if you must, modify the prototype directly (but don't) |
| Mutating `Object.prototype` breaks everything | Adding properties to the root prototype affects all objects | Never modify built-in prototypes in production code |
| `hasOwnProperty` returns wrong results | Someone set `obj.hasOwnProperty = false` | Use `Object.hasOwn(obj, key)` (static method, can't be shadowed) |
| `instanceof` fails across iframes/realms | Each realm has its own prototype objects | Use `Array.isArray()` for arrays; duck-type for custom classes |
| Setting `__proto__` on a user-controlled object | Prototype pollution vulnerability | Use `Map` for user-controlled keys, or `Object.create(null)` |

## Practice

**Warm-up.** Print the prototype chain of an empty array by calling `Object.getPrototypeOf` in a loop until you reach `null`.

**Standard.** Implement a function `inherits(Child, Parent)` the old-school ES5 way (before `class extends`). Verify with `instanceof`.

**Bug hunt.** Why does `delete user.greet` not remove `greet` when the user was created from `new User()`?

**Stretch.** Add a `shuffle` method to `Array.prototype`. Make it work, then explain why extending built-in prototypes is dangerous in a library.

**Stretch++.** Walk and print the complete prototype chain of a `Map` instance. How many levels deep does it go?

<details><summary>Show solutions</summary>

**Warm-up.**

```js
let obj = [];
while (obj !== null) {
  console.log(obj);
  obj = Object.getPrototypeOf(obj);
}
// [] → Array.prototype → Object.prototype → null
```

**Bug hunt.**

```js
// greet lives on User.prototype, not on the instance.
// delete only removes own properties. The prototype's greet is unaffected.
// To verify: Object.hasOwn(user, "greet") is false.
```

**Standard.**

```js
function inherits(Child, Parent) {
  Child.prototype = Object.create(Parent.prototype);
  Child.prototype.constructor = Child;
}
```

</details>

## Quiz

1. `Class.prototype` is:
    (a) The class itself
    (b) The object that instances inherit from
    (c) `undefined` in classes
    (d) Same as `__proto__`

2. Method lookup works by:
    (a) Checking the instance only
    (b) Walking the prototype chain
    (c) Hash table lookup
    (d) Calling `call()` internally

3. `Object.create(base)` returns:
    (a) A copy of `base`
    (b) A new object whose prototype is `base`
    (c) An error
    (d) A frozen object

4. Mutating `Object.prototype`:
    (a) Is safe and recommended
    (b) Affects every object in the program
    (c) Is prevented by the engine
    (d) Only affects new objects

5. Classes under the hood are:
    (a) A unique internal type
    (b) Functions with a `prototype` property
    (c) Maps
    (d) Records

**Short answer:**

6. What is the difference between `Constructor.prototype` and `instance.__proto__`?
7. Why should you avoid deep prototype chains?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — `Constructor.prototype` is a property on the constructor function that defines what instances will inherit; `instance.__proto__` (or `Object.getPrototypeOf(instance)`) is the actual prototype link on a specific instance, pointing to the constructor's prototype. 7 — Each level adds a lookup step (though cached), increases cognitive complexity, and makes debugging harder; prefer composition over deep inheritance.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-prototypes — mini-project](mini-projects/06-prototypes-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Every object has a prototype; property lookup walks the chain until it finds the property or hits `null`.
- Classes are syntactic sugar — methods live on `Class.prototype`, instances link to it.
- Never mutate built-in prototypes (`Object.prototype`, `Array.prototype`) in production code.
- Prefer `Object.getPrototypeOf` over `__proto__` and keep inheritance hierarchies shallow.

## Further reading

- MDN, *Inheritance and the prototype chain*.
- Kyle Simpson, *You Don't Know JS: this & Object Prototypes*.
- Next: [Loops](07-loops.md).
