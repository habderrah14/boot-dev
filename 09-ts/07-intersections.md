# Chapter 07 — Intersections

> "An intersection type `A & B` is a value that satisfies *both* A and B. It's how you compose small types into bigger ones without inheritance."

## Learning objectives

By the end of this chapter you will be able to:

- Combine types with `&` to build composite shapes.
- Explain when intersections differ from `extends` on interfaces.
- Recognize and debug conflicting properties that collapse to `never`.
- Use intersections with generics for mixin-style composition.

## Prerequisites & recap

- [Chapter 05 — Objects](05-objects.md) — object types, structural typing, type aliases.

## The simple version

A union (`A | B`) means "one of these." An intersection (`A & B`) means "all of these at once." When you intersect two object types, the result is a single type that has *every* property from both. It's like gluing two shapes together — the resulting value must satisfy both.

This is TypeScript's main tool for composition. Instead of building deep inheritance hierarchies, you define small, focused types and combine them with `&`. Need timestamps on your user? `User & Timestamped`. Need audit fields on your order? `Order & Audited`. Each piece stays independent and reusable.

## In plain terms (newbie lane)

This chapter is really about **Intersections**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌──────────────┐   ┌──────────────┐
  │  { id: num } │   │ { name: str }│
  │  Identified  │   │    Named     │
  └──────┬───────┘   └──────┬───────┘
         │                  │
         └────────┬─────────┘
                  │  &
         ┌────────┴────────┐
         │  { id: number;  │
         │    name: string }│
         │     User        │
         └─────────────────┘
```
*Figure 7-1. Intersection merges all properties from both types.*

## Concept deep-dive

### Merging shapes

The most common use of intersections: composing small types into bigger ones.

```ts
type Identified = { id: number };
type Named = { name: string };

type User = Identified & Named;   // { id: number; name: string }

const u: User = { id: 1, name: "Ada" };
```

Why use this instead of writing one big type? Because `Identified` and `Named` are reusable. You can combine them with other types — `Post & Identified & Timestamped` — without repeating fields.

### Adding fields to third-party types

Intersections are especially handy when you can't modify an existing type:

```ts
type WithTimestamps = {
  createdAt: Date;
  updatedAt: Date;
};

type Post = {
  title: string;
  body: string;
} & WithTimestamps;
```

You've added timestamps without touching the original type definition. This is a "mixin" pattern — you compose behavior by combining types.

### Conflicts collapse to `never`

If two intersected types have the same property with incompatible types, the property becomes `never`:

```ts
type A = { x: number };
type B = { x: string };
type C = A & B;   // x: number & string → never
```

`number & string` has no possible value — nothing is simultaneously a number and a string. The property `x` becomes `never`, making the entire type effectively unusable. This is TypeScript telling you the composition doesn't make sense.

### Intersections with generics

A powerful pattern for enriching values:

```ts
function withId<T>(x: T): T & { id: string } {
  return { ...x, id: crypto.randomUUID() };
}

const user = withId({ name: "Ada" });
// type: { name: string } & { id: string }
```

The generic preserves the input type while adding new fields.

### Intersection vs. `extends`

Interfaces can achieve similar composition via `extends`:

```ts
interface Identified { id: number }
interface Named { name: string }
interface User extends Identified, Named {}
```

Key differences:

| | Intersection (`&`) | `extends` |
|---|---|---|
| Works with type aliases | Yes | No (interfaces only) |
| Declaration merging | No | Yes (interfaces merge) |
| Conflicting properties | Silently collapses to `never` | Compile error |
| Unions, mapped types | Yes | No |

Rule of thumb: prefer `interface` + `extends` for object shapes you might augment (especially in libraries). Use `type` + `&` for everything else — unions, conditional types, mapped types, and one-off compositions.

## Why these design choices

**Why composition over inheritance?** Intersections let you mix and match small types without committing to an inheritance tree. You can combine `Timestamped`, `SoftDeletable`, and `Audited` in any combination without a diamond inheritance problem.

**Why does `never` result from conflicts instead of an error?** TypeScript follows type theory: `number & string` is the type of values that are both — which is empty, hence `never`. This is consistent and composable, but it can be surprising. Some teams prefer `interface extends` here because it gives an explicit error.

**When would you pick differently?** If you want an error on conflicting properties (not a silent `never`), use `interface extends`. If your types involve unions or computed properties, you need `type` + `&` because interfaces can't express those.

## Production-quality code

```ts
type Timestamped = {
  readonly createdAt: Date;
  readonly updatedAt: Date;
};

type SoftDeletable = {
  readonly deletedAt: Date | null;
};

type Audited = {
  readonly lastModifiedBy: string;
};

type BaseEntity = Timestamped & SoftDeletable & Audited;

type User = BaseEntity & {
  readonly id: number;
  readonly name: string;
  readonly email: string;
};

type Post = BaseEntity & {
  readonly id: number;
  readonly title: string;
  readonly body: string;
  readonly authorId: number;
};

function softDelete<T extends SoftDeletable>(entity: T): T {
  return { ...entity, deletedAt: new Date() };
}

function markModified<T extends Audited>(entity: T, by: string): T {
  return { ...entity, lastModifiedBy: by, updatedAt: new Date() } as T;
}
```

## Security notes

N/A — Intersection types are a compile-time construct and don't affect runtime security. The same rules about validating external input apply regardless of how you compose your types.

## Performance notes

N/A — Intersections are erased at compile time. The runtime objects are plain JavaScript objects, and spreading (`{ ...a, ...b }`) has the same O(n) cost as in plain JS.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Property is `never` and you can't assign any value | Two intersected types have the same property with incompatible types | Use consistent types across components, or pick one with `Omit` before intersecting |
| 2 | Using `&` when `Pick` + rename would be cleaner | Over-composing with intersections when you only need a subset | Use `Pick<T, K>` or `Omit<T, K>` to select specific fields |
| 3 | Relying on declaration merging in app code | Using `interface` where repeated declarations merge unexpectedly | Use `type` aliases for app code; reserve merging for library augmentation |
| 4 | Type is correct but objects have stale fields after spread | Spread is shallow — nested objects share references | Deep-clone nested objects or use immutable update patterns |

## Practice

**1. Warm-up.** Define `Timestamped` with `createdAt` and `updatedAt`. Use `&` to add it to a `User` type.

**2. Standard.** Write `mergeWith<T, U>(a: T, b: U): T & U` using spread. Test it with two different object shapes.

**3. Bug hunt.** Why is `type X = { a: number } & { a: string }` unusable? What type does `a` become?

**4. Stretch.** Show the difference between `interface A { x: number }; interface A { y: string }` (declaration merging) and `type B = { x: number } & { y: string }` — are they equivalent?

**5. Stretch++.** Compose three mixin types (`Timestamped`, `SoftDeletable`, `Owned`) into a `BaseRecord`. Write a generic `softDelete<T extends SoftDeletable>(entity: T): T` function.

<details><summary>Solutions</summary>

**1.**
```ts
type Timestamped = { createdAt: Date; updatedAt: Date };
type User = { id: number; name: string } & Timestamped;
```

**2.**
```ts
function mergeWith<T, U>(a: T, b: U): T & U {
  return { ...a, ...b } as T & U;
}
```

**3.** `a` becomes `number & string`, which is `never`. No value can be both a number and a string simultaneously, so the property is impossible to satisfy.

**4.** They produce the same shape (`{ x: number; y: string }`), but declaration merging happens across separate `interface` declarations and can be surprising in large codebases. The `type` + `&` version is explicit and happens in one place.

**5.**
```ts
type Timestamped = { createdAt: Date; updatedAt: Date };
type SoftDeletable = { deletedAt: Date | null };
type Owned = { ownerId: string };
type BaseRecord = Timestamped & SoftDeletable & Owned;

function softDelete<T extends SoftDeletable>(entity: T): T {
  return { ...entity, deletedAt: new Date() };
}
```

</details>

## Quiz

1. `A & B` means:
   (a) Value is A or B  (b) Value satisfies both A and B  (c) A extends B  (d) Interface-only syntax

2. Conflicting field types in `&`:
   (a) First type wins  (b) Second type wins  (c) Collapses to `never`  (d) Compile error

3. Interface vs. type alias:
   (a) Identical  (b) Interfaces can declaration-merge; types can express more  (c) Types can't extend  (d) Interfaces are runtime

4. Prefer type aliases for:
   (a) Object shapes exclusively  (b) Unions, mapped types, and computed types  (c) Any time, always  (d) Nothing, always use interfaces

5. Intersection can compose:
   (a) Only classes  (b) Any object-like types  (c) Primitives only  (d) Tuples only

**Short answer:**

6. When does `interface extends` read better than `&`?
7. What's one trade-off of declaration merging?

*Answers: 1-b, 2-c, 3-b, 4-b, 5-b. 6 — When building a class hierarchy or extending a well-known shape (e.g., `interface Admin extends User`), `extends` reads as natural English and gives explicit errors on conflicts. 7 — It can silently change a type's shape when multiple files declare the same interface name, making it hard to track down where fields came from.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-intersections — mini-project](mini-projects/07-intersections-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `A & B` produces a type that must satisfy both A and B — composition without inheritance.
- Conflicting properties in intersections collapse to `never`, not an error.
- Use `interface extends` when you want explicit conflict errors; use `type` + `&` for unions, generics, and flexible composition.
- Small, focused mixin types composed with `&` keep your type hierarchy flat and reusable.

## Further reading

- [TypeScript Handbook — Object Types: Intersection Types](https://www.typescriptlang.org/docs/handbook/2/objects.html#intersection-types)
- [TypeScript Handbook — Interfaces vs. Type Aliases](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#differences-between-type-aliases-and-interfaces)
- Next: [Interfaces](08-interfaces.md)
