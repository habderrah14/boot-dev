# Chapter 11 — Classes

> "TypeScript classes are JavaScript classes with types, access modifiers, parameter properties, and abstract members. Nothing more, nothing less."

## Learning objectives

By the end of this chapter you will be able to:

- Declare classes with typed fields, methods, and access modifiers.
- Use parameter properties to eliminate constructor boilerplate.
- Declare abstract classes with required subclass methods.
- Implement interfaces and understand how `implements` differs from `extends`.
- Choose between `private` (compile-time) and `#name` (runtime) privacy.

## Prerequisites & recap

- [Module 08 — JS Classes](../08-js/05-classes.md) — `class`, `constructor`, `extends`, `super`.
- [Chapter 08 — Interfaces](08-interfaces.md) — interface declaration, `implements`.

## The simple version

TypeScript classes are regular JavaScript classes with extra compile-time features bolted on. You get typed fields, access modifiers (`public`, `private`, `protected`), parameter properties (a shorthand for "declare and assign in the constructor"), and `abstract` classes that force subclasses to implement specific methods.

The key insight: most of these features are erased at compile time. `private` doesn't exist at runtime (anyone can access it via `as any`). `abstract` doesn't exist at runtime. If you need *real* runtime privacy, use JavaScript's `#` private fields. TypeScript supports both — choose based on whether you need compile-time convenience or runtime guarantees.

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
  ┌──────────────────────┐
  │   abstract Shape     │  ← cannot instantiate directly
  │   + abstract area()  │
  │   + describe()       │  ← concrete method
  └──────────┬───────────┘
             │ extends
  ┌──────────┴───────────┐
  │      Square          │
  │   - side: number     │  ← private field
  │   + area(): number   │  ← implements abstract
  │   + describe(): str  │  ← inherited
  └──────────────────────┘
```
*Figure 11-1. Abstract classes provide shared behavior; subclasses fill in the abstract methods.*

## Concept deep-dive

### Typed fields

```ts
class User {
  id: number;
  name: string;
  email?: string;
  readonly createdAt: Date = new Date();

  constructor(id: number, name: string) {
    this.id = id;
    this.name = name;
  }
}
```

Fields must be initialized in the constructor or have a default value (with `strict`). `readonly` fields can only be set in the constructor or at declaration.

### Access modifiers

| Modifier | Accessible from | Runtime enforcement |
|----------|----------------|-------------------|
| `public` (default) | Anywhere | N/A |
| `private` | This class only | Compile-time only |
| `protected` | This class + subclasses | Compile-time only |
| `readonly` | Set in constructor only | Compile-time only |

```ts
class Vault {
  private secret: string;
  constructor(s: string) { this.secret = s; }
}

new Vault("x").secret;  // compile error
(new Vault("x") as any).secret;  // works at runtime — `private` is just a hint
```

For *runtime* privacy, use ECMAScript `#` private fields:

```ts
class Vault {
  #secret: string;
  constructor(s: string) { this.#secret = s; }
}

(new Vault("x") as any).#secret;  // SyntaxError at runtime — truly private
```

### Parameter properties — less boilerplate

Instead of declaring fields and assigning them in the constructor:

```ts
class User {
  constructor(
    public readonly id: number,
    public name: string,
    private password: string,
  ) {}
}
```

Each parameter with a modifier (`public`, `private`, `protected`, `readonly`) becomes a field automatically. This eliminates the repetitive `this.id = id` pattern.

### Abstract classes

```ts
abstract class Shape {
  abstract area(): number;

  describe(): string {
    return `Shape with area = ${this.area().toFixed(2)}`;
  }
}

class Square extends Shape {
  constructor(private side: number) { super(); }

  area(): number {
    return this.side ** 2;
  }
}
```

You can't instantiate `Shape` directly — you must subclass it and implement all `abstract` members. Abstract classes are useful when subclasses share behavior (like `describe()`) but differ in specifics (like `area()`).

### Implementing interfaces

```ts
interface Serializable {
  toJSON(): object;
}

class User implements Serializable {
  constructor(public id: number, public name: string) {}

  toJSON(): object {
    return { id: this.id, name: this.name };
  }
}
```

`implements` is a compile-time check — it verifies that the class has all required members. It doesn't inherit anything and generates no runtime code. If you forget `toJSON`, the compiler tells you.

### Generic classes

```ts
class Box<T> {
  constructor(public value: T) {}

  map<U>(f: (x: T) => U): Box<U> {
    return new Box(f(this.value));
  }
}

const numBox = new Box(42);            // Box<number>
const strBox = numBox.map(String);     // Box<string>
```

Preview of [Chapter 13 — Generics](13-generics.md).

### When to use classes vs. functions + objects

Classes are appropriate when you have:
- **Shared mutable state** that methods operate on.
- **Inheritance hierarchies** with abstract behavior.
- **Identity matters** — you need `instanceof` checks.

For everything else — pure transformations, stateless utilities, configuration objects — a function or a plain typed object is simpler. Don't reach for a class just because you can.

## Why these design choices

**Why `private` at compile-time only?** TypeScript predates ECMAScript `#` private fields. When `private` was designed, there was no runtime privacy mechanism in JavaScript. TypeScript chose not to emit different code — it only adds type annotations — so `private` couldn't be enforced at runtime. Now that `#` exists, you have a choice.

**Why parameter properties?** Constructors in TypeScript (and Java, C#) often have boilerplate: declare a field, accept a parameter, assign parameter to field. Parameter properties collapse all three into one line. The trade-off is readability — new TypeScript developers sometimes find them confusing.

**When would you pick differently?** If you're writing a library and need guaranteed encapsulation, use `#` private fields. If you're writing application code where compile-time checks are sufficient, `private` is fine and produces cleaner `console.log` output.

## Production-quality code

```ts
interface Repository<T extends { id: string }> {
  find(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(item: T): Promise<void>;
  delete(id: string): Promise<void>;
}

abstract class BaseRepository<T extends { id: string }> implements Repository<T> {
  protected readonly store = new Map<string, T>();

  async find(id: string): Promise<T | null> {
    return this.store.get(id) ?? null;
  }

  async findAll(): Promise<T[]> {
    return [...this.store.values()];
  }

  async save(item: T): Promise<void> {
    this.validate(item);
    this.store.set(item.id, item);
  }

  async delete(id: string): Promise<void> {
    if (!this.store.has(id)) {
      throw new Error(`Entity ${id} not found`);
    }
    this.store.delete(id);
  }

  protected abstract validate(item: T): void;
}

interface User {
  id: string;
  name: string;
  email: string;
}

class UserRepository extends BaseRepository<User> {
  protected validate(user: User): void {
    if (!user.name.trim()) throw new Error("Name is required");
    if (!user.email.includes("@")) throw new Error("Invalid email");
  }
}
```

## Security notes

- **`private` is not a security boundary.** Any code can access `private` fields via `as any` or through the JavaScript runtime. Don't store secrets in `private` fields expecting them to be safe from untrusted code.
- **`#` private fields are runtime-enforced** and can't be accessed externally, even via `as any`. Use them when encapsulation is a security requirement.
- **`protected` members are accessible in subclasses.** If your class is extended by untrusted code, `protected` fields are not private.

## Performance notes

N/A — TypeScript class features (`private`, `public`, `abstract`) are erased at compile time. The emitted JavaScript is a standard ES class. `#` private fields have negligible runtime overhead (they use a WeakMap internally in older transpilation targets, but are native in modern engines).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `private` field accessible via `(obj as any).field` | `private` is compile-time only | Use `#field` for runtime privacy |
| 2 | `TypeError: Must call super constructor` | Forgot `super()` in a derived class constructor | Call `super()` before accessing `this` |
| 3 | `implements` but forgot a method | Missing method in class body | Read the compile error and implement the missing member |
| 4 | Overusing classes for stateless logic | Habit from OOP-heavy languages | Use functions + typed objects for stateless operations |
| 5 | Generic class methods all use `any` | Forgot to use the type parameter `T` in method signatures | Thread `T` through all method params and returns |

## Practice

**1. Warm-up.** Create a `Rectangle` class with `width` and `height` parameters and an `area()` method.

**2. Standard.** Refactor `Rectangle` to use parameter properties, eliminating the manual field declarations and assignments.

**3. Bug hunt.** Why does `class C { private x = 0 }; (new C() as any).x = 5;` work at runtime?

**4. Stretch.** Implement a generic `Stack<T>` class with `push`, `pop`, `peek`, and `isEmpty` methods.

**5. Stretch++.** Create an abstract `Command` base class with `execute()` and `undo()` abstract methods. Implement `AddCommand` and `RemoveCommand` subclasses and execute them polymorphically.

<details><summary>Solutions</summary>

**1.**
```ts
class Rectangle {
  width: number;
  height: number;
  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
  }
  area(): number { return this.width * this.height; }
}
```

**2.**
```ts
class Rectangle {
  constructor(
    public readonly width: number,
    public readonly height: number,
  ) {}
  area(): number { return this.width * this.height; }
}
```

**3.** `private` is a TypeScript compile-time keyword — it generates no runtime enforcement. At runtime, the field is a normal public property. Use `#x` for runtime privacy.

**4.**
```ts
class Stack<T> {
  private items: T[] = [];
  push(x: T): void { this.items.push(x); }
  pop(): T | undefined { return this.items.pop(); }
  peek(): T | undefined { return this.items[this.items.length - 1]; }
  isEmpty(): boolean { return this.items.length === 0; }
}
```

**5.**
```ts
abstract class Command<T> {
  abstract execute(state: T): T;
  abstract undo(state: T): T;
}

class AddCommand extends Command<number[]> {
  constructor(private item: number) { super(); }
  execute(state: number[]) { return [...state, this.item]; }
  undo(state: number[]) { return state.slice(0, -1); }
}
```

</details>

## Quiz

1. `private` in TypeScript is enforced:
   (a) At runtime  (b) At compile time only  (c) Neither  (d) Both

2. Parameter properties:
   (a) Shorthand for field declaration + constructor assignment  (b) Static fields  (c) Abstract-only  (d) Not supported

3. An `abstract class`:
   (a) Can be instantiated directly  (b) Cannot be instantiated — must be subclassed  (c) Is the same as an interface  (d) Only exists at runtime

4. `implements` vs. `extends`:
   (a) Identical  (b) `extends` inherits behavior; `implements` only checks shape  (c) Reversed  (d) Same runtime performance

5. Truly private fields use:
   (a) `_name` convention  (b) `#name` syntax  (c) `private name`  (d) `name!` assertion

**Short answer:**

6. When should you use `#name` over `private`?
7. Why are abstract classes useful even without shared state?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b. 6 — When you need runtime enforcement of privacy (e.g., security-sensitive data, library APIs where consumers shouldn't access internals). 7 — They enforce a contract: subclasses must implement specific methods. Even without shared state, this guarantees that every subclass has a `toJSON()` or `validate()` method, enabling polymorphic code.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-classes — mini-project](mini-projects/11-classes-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- TypeScript classes add types, access modifiers, and parameter properties to JavaScript classes — all erased at compile time.
- `private` is compile-time only; `#name` is runtime-enforced. Choose based on your needs.
- Abstract classes enforce subclass contracts; `implements` verifies interface compliance without inheritance.
- Prefer functions + typed objects for stateless logic; use classes when you need shared mutable state or inheritance hierarchies.

## Further reading

- [TypeScript Handbook — Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html)
- [MDN — Private class features (`#`)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Private_properties)
- Next: [Utility Types](12-utility-types.md)
