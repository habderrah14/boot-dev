# Module 05 — Learn Functional Programming in Python

> Functional programming is a discipline: prefer values over variables, expressions over statements, and functions over methods. Adopted even partially, it produces code that is dramatically easier to test, parallelize, and reason about.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Functional Programming"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Identify pure vs. impure code and move impurity to the edges of your program.
- Use `map`, `filter`, `reduce`, and list/dict comprehensions idiomatically.
- Write and reason about recursive functions, including when recursion is the wrong tool.
- Build higher-order functions, closures, and decorators.
- Model data with sum types (tagged unions / ADTs) in Python.

## Prerequisites

- [Module 01: Python](../01-python/README.md) and [Module 04: OOP](../04-oop/README.md).

## Chapter index

1. [What is Functional Programming?](01-what-is-fp.md)
2. [First Class Functions](02-first-class-functions.md)
3. [Pure Functions](03-pure-functions.md)
4. [Recursion](04-recursion.md)
5. [Function Transformations](05-function-transformations.md)
6. [Closures](06-closures.md)
7. [Currying](07-currying.md)
8. [Decorators](08-decorators.md)
9. [Sum Types](09-sum-types.md)

## How this module connects

- Pure functions underpin testability (Module 01) and parallelism (Modules 12, 15).
- Closures & decorators are the mechanics behind web framework middleware, retries, and caching (Module 13).
- Sum types re-appear in TypeScript's discriminated unions (Module 09).

## Companion artifacts

- Exercises:
  - [01 — What is Functional Programming?](exercises/01-what-is-fp-exercises.md)
  - [02 — First Class Functions](exercises/02-first-class-functions-exercises.md)
  - [03 — Pure Functions](exercises/03-pure-functions-exercises.md)
  - [04 — Recursion](exercises/04-recursion-exercises.md)
  - [05 — Function Transformations](exercises/05-function-transformations-exercises.md)
  - [06 — Closures](exercises/06-closures-exercises.md)
  - [07 — Currying](exercises/07-currying-exercises.md)
  - [08 — Decorators](exercises/08-decorators-exercises.md)
  - [09 — Sum Types](exercises/09-sum-types-exercises.md)
- Extended assessment artifacts:
  - [10 — Debugging Incident Lab](exercises/10-debugging-incident-lab.md)
  - [11 — Code Review Task](exercises/11-code-review-task.md)
  - [12 — System Design Prompt](exercises/12-system-design-prompt.md)
  - [13 — Interview Challenges](exercises/13-interview-challenges.md)
- Solutions:
  - [01 — What is Functional Programming?](solutions/01-what-is-fp-solutions.md)
  - [02 — First Class Functions](solutions/02-first-class-functions-solutions.md)
  - [03 — Pure Functions](solutions/03-pure-functions-solutions.md)
  - [04 — Recursion](solutions/04-recursion-solutions.md)
  - [05 — Function Transformations](solutions/05-function-transformations-solutions.md)
  - [06 — Closures](solutions/06-closures-solutions.md)
  - [07 — Currying](solutions/07-currying-solutions.md)
  - [08 — Decorators](solutions/08-decorators-solutions.md)
  - [09 — Sum Types](solutions/09-sum-types-solutions.md)
- Mini-project briefs:
  - [01 — Functional Core ETL (Bonus project)](mini-projects/01-functional-core-etl.md)
  - [01 — What Is FP (Core chapter project)](mini-projects/01-what-is-fp-project.md)
  - [02 — First Class Functions](mini-projects/02-first-class-functions-project.md)
  - [03 — Pure Functions](mini-projects/03-pure-functions-project.md)
  - [04 — Recursion](mini-projects/04-recursion-project.md)
  - [05 — Function Transformations](mini-projects/05-function-transformations-project.md)
  - [06 — Closures](mini-projects/06-closures-project.md)
  - [07 — Currying](mini-projects/07-currying-project.md)
  - [08 — Decorators](mini-projects/08-decorators-project.md)
  - [09 — Sum Types](mini-projects/09-sum-types-project.md)
- Milestone capstone:
  - [Capstone 01 — Immutable CLI](capstone/capstone-01-immutable-cli.md)

## Quiz answer key

- **Ch. 01 — What is Functional Programming?.** 1) b, 2) d, 3) b, 4) b, 5) c.
  - 6.  One concrete backend benefit is that pure functions are trivial to test because they need no mocks, databases, or teardown.
  - 7.  Python is not pure-FP because it allows mutation and side effects freely, and it does not enforce referential transparency in the type system.
- **Ch. 02 — First Class Functions.** 1) b, 2) c, 3) b, 4) b, 5) c.
  - 6.  Use `lambda` for tiny one-expression callbacks; prefer `def` for named, documented, annotated, or multi-step logic.
  - 7.  Generators stream one value at a time, so they avoid building full intermediate sequences in memory.
- **Ch. 03 — Pure Functions.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  Pure functions are simple to test because they depend only on inputs and have no side effects.
  - 7.  Inject RNG/state explicitly (for example, seeded `random.Random`) to keep behavior deterministic.
- **Ch. 04 — Recursion.** 1) a, 2) b, 3) a, 4) c, 5) c.
  - 6.  Recursion fits naturally recursive data such as trees, nested JSON, filesystems, and ASTs.
  - 7.  Python avoids tail-call optimization to preserve readable stack traces and debuggability.
- **Ch. 05 — Function Transformations.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6.  `partial` supports dependency injection by pre-binding dependencies and simplifying call signatures.
  - 7.  `pipe` reads left-to-right and usually matches human data-flow reasoning better than right-to-left `compose`.
- **Ch. 06 — Closures.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  A closure is a function that retains access to variables from its defining lexical scope.
  - 7.  Loop-lambda bugs come from late binding: lambdas capture the variable reference, not per-iteration values.
- **Ch. 07 — Currying.** 1) a, 2) b, 3) b, 4) b, 5) b.
  - 6.  `partial` is clearer when pre-filling multiple arguments or working with non-curried callables.
  - 7.  Python conventions and call semantics make partials/closures/plain functions more ergonomic than strict currying.
- **Ch. 08 — Decorators.** 1) b, 2) c, 3) b, 4) b, 5) a.
  - 6.  Decorator factories have layered scopes: config capture, function capture, then per-call wrapper execution.
  - 7.  `functools.wraps` preserves metadata (`__name__`, `__doc__`, etc.) needed by tooling and introspection.
- **Ch. 09 — Sum Types.** 1) b, 2) a, 3) c, 4) b, 5) b.
  - 6.  Sum types are safer than sentinel values because success/failure are distinct structural variants, preventing accidental misuse.
  - 7.  Use enum when variants have no payload; use tagged dataclasses when each variant carries its own fields.
