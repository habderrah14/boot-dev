# Mini-project — 01-types

_Companion chapter:_ [`01-types.md`](../01-types.md)

**Goal.** Set up a TypeScript project from scratch with `src/`, `tsconfig.json`, and `package.json`. Implement typed `sum(...nums: number[]): number` and `median(nums: number[]): number` functions, plus tests using `node:test`.

**Acceptance criteria:**

- `npx tsc` compiles with zero errors under `strict: true`.
- `npm test` runs and passes.
- No use of `any` anywhere.
- `noUncheckedIndexedAccess` is enabled.

**Hints:**

- `median` needs to handle even-length arrays (average the two middle elements).
- With `noUncheckedIndexedAccess`, you'll need to handle the `T | undefined` return from array indexing.

**Stretch:** Add a `mode(nums: number[]): number | undefined` function that returns the most frequent value. Handle ties by returning the first one encountered.
