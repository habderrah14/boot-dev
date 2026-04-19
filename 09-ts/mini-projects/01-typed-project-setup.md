# Mini-project — Typed Project Setup

## Goal

Bootstrap a small TypeScript project with strict compiler settings and a couple of typed utility functions.

## Deliverable

A working TS project with `tsconfig.json`, `package.json`, source files, and tests.

## Required behavior

1. `strict: true` enabled.
2. `noUncheckedIndexedAccess` enabled.
3. Implement typed `sum` and `median` functions.
4. Add tests using `node:test` or equivalent.
5. `npx tsc` passes with zero errors.

## Acceptance criteria

- No `any` in the codebase.
- The project compiles and runs from a clean checkout.
- README documents setup, test, and build commands.
- Types are annotated at public boundaries, not every local variable.

## Hints

- Keep the project tiny and focused.
- Use inference for locals.
- Handle even-length medians by averaging the two middle values.

## Stretch goals

1. Add a `mode` function.
2. Add runtime validation for one function boundary.
3. Configure ESLint with TypeScript support.
