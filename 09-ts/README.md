# Module 09 — Learn TypeScript

> TypeScript is JavaScript with a diary. It writes down what you meant at write-time so the compiler can remind you later when you forget. For a backend team the payoff is enormous: fewer runtime errors, better refactors, self-documenting APIs.

## Map to Boot.dev

Parallels Boot.dev's **"Learn TypeScript"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Add precise static types to JavaScript code without over-engineering.
- Model data with unions, intersections, interfaces, tuples, and enums.
- Narrow types using control flow and discriminated unions.
- Use generics to write reusable functions and classes without `any`.
- Apply utility types (`Partial`, `Pick`, `Omit`, `Record`, …) in real codebases.
- Set up a local TypeScript project from scratch (`tsc`, `tsconfig.json`, ESLint).

## Prerequisites

- [Module 08: JavaScript](../08-js/README.md).
- Optional: [Module 04: OOP](../04-oop/README.md) for classes and [Module 05: FP](../05-fp/README.md) for sum types.

## Chapter index

1. [Types](01-types.md)
2. [Functions](02-functions.md)
3. [Unions](03-unions.md)
4. [Arrays](04-arrays.md)
5. [Objects](05-objects.md)
6. [Tuples](06-tuples.md)
7. [Intersections](07-intersections.md)
8. [Interfaces](08-interfaces.md)
9. [Enums](09-enums.md)
10. [Type Narrowing](10-type-narrowing.md)
11. [Classes](11-classes.md)
12. [Utility Types](12-utility-types.md)
13. [Generics](13-generics.md)
14. [Conditional Types](14-conditional-types.md)
15. [Local Development](15-local-development.md)

## How this module connects

- Every subsequent TypeScript module (10, 12, 13, 15) assumes fluency here.
- Utility types and generics are the lingua franca of library APIs (e.g., Express types, Drizzle ORM types).

## Companion artifacts

- Exercises:
  - [01 — Types](exercises/01-types-exercises.md)
  - [02 — Functions](exercises/02-functions-exercises.md)
  - [03 — Unions](exercises/03-unions-exercises.md)
  - [04 — Arrays](exercises/04-arrays-exercises.md)
  - [05 — Objects](exercises/05-objects-exercises.md)
  - [06 — Tuples](exercises/06-tuples-exercises.md)
  - [07 — Intersections](exercises/07-intersections-exercises.md)
  - [08 — Interfaces](exercises/08-interfaces-exercises.md)
  - [09 — Enums](exercises/09-enums-exercises.md)
  - [10 — Type Narrowing](exercises/10-type-narrowing-exercises.md)
  - [11 — Classes](exercises/11-classes-exercises.md)
  - [12 — Utility Types](exercises/12-utility-types-exercises.md)
  - [13 — Generics](exercises/13-generics-exercises.md)
  - [14 — Conditional Types](exercises/14-conditional-types-exercises.md)
  - [15 — Local Development](exercises/15-local-development-exercises.md)
- Extended assessment artifacts:
  - [16 — Debugging Incident Lab](exercises/16-debugging-incident-lab.md)
  - [17 — Code Review Task](exercises/17-code-review-task.md)
  - [18 — System Design Prompt](exercises/18-system-design-prompt.md)
  - [19 — Interview Challenges](exercises/19-interview-challenges.md)
- Solutions:
  - [01 — Types](solutions/01-types-solutions.md)
  - [02 — Functions](solutions/02-functions-solutions.md)
  - [03 — Unions](solutions/03-unions-solutions.md)
  - [04 — Arrays](solutions/04-arrays-solutions.md)
  - [05 — Objects](solutions/05-objects-solutions.md)
  - [06 — Tuples](solutions/06-tuples-solutions.md)
  - [07 — Intersections](solutions/07-intersections-solutions.md)
  - [08 — Interfaces](solutions/08-interfaces-solutions.md)
  - [09 — Enums](solutions/09-enums-solutions.md)
  - [10 — Type Narrowing](solutions/10-type-narrowing-solutions.md)
  - [11 — Classes](solutions/11-classes-solutions.md)
  - [12 — Utility Types](solutions/12-utility-types-solutions.md)
  - [13 — Generics](solutions/13-generics-solutions.md)
  - [14 — Conditional Types](solutions/14-conditional-types-solutions.md)
  - [15 — Local Development](solutions/15-local-development-solutions.md)
- Mini-project briefs:
  - [01 — Typed Project Setup (Bonus project)](mini-projects/01-typed-project-setup.md)
  - [01 — Types (Core chapter project)](mini-projects/01-types-project.md)
  - [02 — Functions](mini-projects/02-functions-project.md)
  - [03 — Unions](mini-projects/03-unions-project.md)
  - [04 — Arrays](mini-projects/04-arrays-project.md)
  - [05 — Objects](mini-projects/05-objects-project.md)
  - [06 — Tuples](mini-projects/06-tuples-project.md)
  - [07 — Intersections](mini-projects/07-intersections-project.md)
  - [08 — Interfaces](mini-projects/08-interfaces-project.md)
  - [09 — Enums](mini-projects/09-enums-project.md)
  - [10 — Type Narrowing](mini-projects/10-type-narrowing-project.md)
  - [11 — Classes](mini-projects/11-classes-project.md)
  - [12 — Utility Types](mini-projects/12-utility-types-project.md)
  - [13 — Generics](mini-projects/13-generics-project.md)
  - [14 — Conditional Types](mini-projects/14-conditional-types-project.md)
  - [15 — Local Development](mini-projects/15-local-development-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Types.** 1) b, 2) b, 3) b, 4) c, 5) b.
  - 6.  Function boundaries are public contracts other code depends on; inference is usually enough for local variables inside the implementation.
  - 7.  `strict` catches null/undefined bugs, implicit `any`, and other issues early, when they are still cheap to fix.
- **Ch. 02 — Functions.** 1) b, 2) b, 3) b, 4) a, 5) a.
  - 6.  Exported functions benefit from explicit return types to lock public contracts and catch drift early.
  - 7.  `void` means return value is ignored; `undefined` means the function returns exactly `undefined`.
- **Ch. 03 — Unions.** 1) b, 2) b, 3) a, 4) b, 5) b.
  - 6.  Discriminated unions enable exhaustive handling and precise narrowing that plain `string` cannot provide.
  - 7.  `Extract` is useful for selecting specific variants from large unions.
- **Ch. 04 — Arrays.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6.  `noUncheckedIndexedAccess` forces explicit handling of potential out-of-bounds `undefined` values.
  - 7.  Converting readonly arrays to mutable should be rare and isolated to strict interop needs.
- **Ch. 05 — Objects.** 1) b, 2) b, 3) a, 4) b, 5) c.
  - 6.  Inline shapes are fine for single-use locals; aliases are better for reused contracts.
  - 7.  Branded types prevent semantic mixups among structurally identical values.
- **Ch. 06 — Tuples.** 1) a, 2) b, 3) b, 4) a, 5) b.
  - 6.  Labeled tuples improve readability for positional meanings.
  - 7.  `useState`-style APIs fit tuples because positional conventions are ergonomic and widely understood.
- **Ch. 07 — Intersections.** 1) b, 2) c, 3) b, 4) b, 5) b.
  - 6.  `extends` often reads clearer for hierarchy extension and conflict diagnostics.
  - 7.  Interface merging can hide shape changes across files and complicate traceability.
- **Ch. 08 — Interfaces.** 1) b, 2) a, 3) b, 4) b, 5) a.
  - 6.  Declaration merging is primarily useful for third-party type augmentation.
  - 7.  Use type aliases for unions/mapped/conditional/template-literal type expressions.
- **Ch. 09 — Enums.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6.  Reordering numeric enums breaks persisted mappings due to positional value assignment.
  - 7.  Enums are useful for legacy interop with numeric constants and reverse mapping needs.
- **Ch. 10 — Type Narrowing.** 1) a, 2) b, 3) a, 4) b, 5) b.
  - 6.  Type predicates validate at runtime before narrowing; `as` casts bypass checks and can lie.
  - 7.  Assertion functions are useful at boundaries to fail fast and keep downstream code strongly typed.
- **Ch. 11 — Classes.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6.  `#private` is appropriate when runtime privacy is required, not just compile-time checks.
  - 7.  Abstract classes enforce method contracts for polymorphic implementations.
- **Ch. 12 — Utility Types.** 1) a, 2) c, 3) a, 4) b, 5) b.
  - 6.  `Partial` is shallow, so nested objects need deep utilities for recursive optionality.
  - 7.  `Parameters`/`ReturnType` help wrappers preserve original function signatures.
- **Ch. 13 — Generics.** 1) b, 2) b, 3) b, 4) b, 5) a.
  - 6.  Constraints are needed when implementation relies on members not guaranteed on unconstrained `T`.
  - 7.  Explicit generic args help when inference is ambiguous or too broad.
- **Ch. 14 — Conditional Types.** 1) b, 2) b, 3) a, 4) a, 5) b.
  - 6.  Distribution matters when transforming unions and expecting union-wise behavior vs whole-union behavior.
  - 7.  `infer` is commonly used in helpers like custom return/parameter extraction types.
- **Ch. 15 — Local Development.** 1) b, 2) b, 3) b, 4) b, 5) c.
  - 6.  Lint and typecheck catch different classes of issues; both should run independently in CI.
  - 7.  `node:test` is lightweight and dependency-free for small projects.
