# Module 08 — Learn JavaScript

> Every backend — every one — touches JavaScript somewhere: a frontend, a config file, a build script, or the server itself running on Node.js. You don't have to love the language; you do have to read it fluently.

## Map to Boot.dev

Parallels Boot.dev's **"Learn JavaScript"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Distinguish `var` / `let` / `const` and use `const` by default.
- Write functions, including arrow functions and higher-order functions, and use `this` without mystery.
- Work with objects, classes, and prototypes; explain how JS's object model differs from Python's.
- Use arrays, sets, and maps fluently with their iteration protocols.
- Read, write, and compose Promises; reason about the single-threaded event loop.
- Know the difference between Node.js, Deno, Bun, and the browser — and when it matters.
- Import and export ES modules.

## Prerequisites

- [Module 01: Python](../01-python/README.md) and [Module 04: OOP](../04-oop/README.md).

## Chapter index

1. [Variables](01-variables.md)
2. [Comparisons](02-comparisons.md)
3. [Functions](03-functions.md)
4. [Objects](04-objects.md)
5. [Classes](05-classes.md)
6. [Prototypes](06-prototypes.md)
7. [Loops](07-loops.md)
8. [Arrays](08-arrays.md)
9. [Errors](09-errors.md)
10. [Sets](10-sets.md)
11. [Maps](11-maps.md)
12. [Promises](12-promises.md)
13. [The Event Loop](13-event-loop.md)
14. [Runtimes](14-runtimes.md)
15. [Modules](15-modules.md)

## How this module connects

- Prerequisite for everything TypeScript-flavored: Modules 09, 10, 12, 13, 15.
- The event loop is the mental model you reuse for async in any language.

## Companion artifacts

- Exercises:
  - [01 — Variables](exercises/01-variables-exercises.md)
  - [02 — Comparisons](exercises/02-comparisons-exercises.md)
  - [03 — Functions](exercises/03-functions-exercises.md)
  - [04 — Objects](exercises/04-objects-exercises.md)
  - [05 — Classes](exercises/05-classes-exercises.md)
  - [06 — Prototypes](exercises/06-prototypes-exercises.md)
  - [07 — Loops](exercises/07-loops-exercises.md)
  - [08 — Arrays](exercises/08-arrays-exercises.md)
  - [09 — Errors](exercises/09-errors-exercises.md)
  - [10 — Sets](exercises/10-sets-exercises.md)
  - [11 — Maps](exercises/11-maps-exercises.md)
  - [12 — Promises](exercises/12-promises-exercises.md)
  - [13 — The Event Loop](exercises/13-event-loop-exercises.md)
  - [14 — Runtimes](exercises/14-runtimes-exercises.md)
  - [15 — Modules](exercises/15-modules-exercises.md)
- Extended assessment artifacts:
  - [16 — Debugging Incident Lab](exercises/16-debugging-incident-lab.md)
  - [17 — Code Review Task](exercises/17-code-review-task.md)
  - [18 — System Design Prompt](exercises/18-system-design-prompt.md)
  - [19 — Interview Challenges](exercises/19-interview-challenges.md)
- Solutions:
  - [01 — Variables](solutions/01-variables-solutions.md)
  - [02 — Comparisons](solutions/02-comparisons-solutions.md)
  - [03 — Functions](solutions/03-functions-solutions.md)
  - [04 — Objects](solutions/04-objects-solutions.md)
  - [05 — Classes](solutions/05-classes-solutions.md)
  - [06 — Prototypes](solutions/06-prototypes-solutions.md)
  - [07 — Loops](solutions/07-loops-solutions.md)
  - [08 — Arrays](solutions/08-arrays-solutions.md)
  - [09 — Errors](solutions/09-errors-solutions.md)
  - [10 — Sets](solutions/10-sets-solutions.md)
  - [11 — Maps](solutions/11-maps-solutions.md)
  - [12 — Promises](solutions/12-promises-solutions.md)
  - [13 — The Event Loop](solutions/13-event-loop-solutions.md)
  - [14 — Runtimes](solutions/14-runtimes-solutions.md)
  - [15 — Modules](solutions/15-modules-solutions.md)
- Mini-project briefs:
  - [01 — No-Var Linter (Bonus project)](mini-projects/01-no-var-linter.md)
  - [01 — Variables (Core chapter project)](mini-projects/01-variables-project.md)
  - [02 — Comparisons](mini-projects/02-comparisons-project.md)
  - [03 — Functions](mini-projects/03-functions-project.md)
  - [04 — Objects](mini-projects/04-objects-project.md)
  - [05 — Classes](mini-projects/05-classes-project.md)
  - [06 — Prototypes](mini-projects/06-prototypes-project.md)
  - [07 — Loops](mini-projects/07-loops-project.md)
  - [08 — Arrays](mini-projects/08-arrays-project.md)
  - [09 — Errors](mini-projects/09-errors-project.md)
  - [10 — Sets](mini-projects/10-sets-project.md)
  - [11 — Maps](mini-projects/11-maps-project.md)
  - [12 — Promises](mini-projects/12-promises-project.md)
  - [13 — Event Loop](mini-projects/13-event-loop-project.md)
  - [14 — Runtimes](mini-projects/14-runtimes-project.md)
  - [15 — Modules](mini-projects/15-modules-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Variables.** 1) d, 2) b, 3) b, 4) b, 5) c.
  - 6. `var` is avoided because it is function-scoped and hoists to `undefined`, creating silent bugs that `let`/`const` prevent.
  - 7. `undefined` means the system's default for "never assigned"; `null` means the developer's explicit signal for "intentionally empty."
- **Ch. 02 — Comparisons.** 1) b, 2) a, 3) a, 4) b, 5) b.
  - 6. Use `||` when all falsy values should trigger defaults, not just nullish values.
  - 7. `typeof null === "object"` is a historical bug kept for backward compatibility.
- **Ch. 03 — Functions.** 1) c, 2) c, 3) b, 4) a, 5) b.
  - 6. Arrow functions inherit lexical `this`, avoiding callback context confusion.
  - 7. Named function expressions improve stack traces and debuggability.
- **Ch. 04 — Objects.** 1) a, 2) b, 3) b, 4) b, 5) c.
  - 6. `structuredClone` preserves richer data types and cycles that JSON cloning breaks.
  - 7. Shallow copies fail when nested objects/arrays remain shared references.
- **Ch. 05 — Classes.** 1) b, 2) b, 3) b, 4) b, 5) c.
  - 6. `instanceof` checks whether constructor prototype appears in an object's prototype chain.
  - 7. Prefer plain objects when behavior/lifecycle complexity does not justify class overhead.
- **Ch. 06 — Prototypes.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. `Constructor.prototype` is the template for instances; `instance.__proto__` is the actual per-instance link.
  - 7. Deep chains increase lookup complexity and cognitive/debug overhead.
- **Ch. 07 — Loops.** 1) b, 2) b, 3) b, 4) d, 5) b.
  - 6. `forEach` does not await callback promises, so async callbacks run without loop-level sequencing.
  - 7. Index loops still help when stepping patterns, reverse iteration, or tight-loop control are needed.
- **Ch. 08 — Arrays.** 1) b, 2) b, 3) d, 4) b, 5) b.
  - 6. `find` returns first match; `filter` returns all matches as an array.
  - 7. Use `toSorted`, `toReversed`, and `toSpliced` for non-mutating alternatives.
- **Ch. 09 — Errors.** 1) c, 2) a, 3) c, 4) a, 5) c.
  - 6. Error `cause` preserves root-cause context while adding domain-level meaning.
  - 7. Throwing can be costly and forces control-flow disruption; expected misses can use explicit result types.
- **Ch. 10 — Sets.** 1) a, 2) a, 3) b, 4) b, 5) c.
  - 6. For larger collections, `Set.has` scales better than repeated linear `Array.includes` scans.
  - 7. Useful for tracking processed objects/nodes by identity without duplicate work.
- **Ch. 11 — Maps.** 1) c, 2) b, 3) b, 4) b, 5) b.
  - 6. Plain objects are fine for fixed-shape string-keyed JSON-like records.
  - 7. `WeakMap` is useful for attaching metadata to objects without preventing GC.
- **Ch. 12 — Promises.** 1) a, 2) b, 3) b, 4) c, 5) c.
  - 6. Use `Promise.allSettled` when you need every outcome, including failures, instead of fail-fast behavior.
  - 7. Timeout wrappers cap latency and avoid hanging forever on stalled async operations.
- **Ch. 13 — The Event Loop.** 1) a, 2) b, 3) a, 4) b, 5) b.
  - 6. Microtasks drain first to preserve Promise/queueMicrotask consistency before moving to next macrotask.
  - 7. `setImmediate` runs in Node's check phase, while `setTimeout(0)` runs in timers phase.
- **Ch. 14 — Runtimes.** 1) c, 2) a, 3) b, 4) c, 5) b.
  - 6. Node's built-in test runner reduces dependencies and integrates cleanly with standard tooling.
  - 7. Pick Deno when secure-by-default permissions and web-standard-first runtime behavior are priorities.
- **Ch. 15 — Modules.** 1) b, 2) c, 3) b, 4) a, 5) b.
  - 6. Named exports are refactor-friendlier because symbol names stay explicit across imports.
  - 7. Barrel files can hide dependency edges and occasionally hurt tree-shaking clarity.
