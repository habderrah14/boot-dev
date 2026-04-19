# Mini-project — 04-arrays

_Companion chapter:_ [`04-arrays.md`](../04-arrays.md)

**Goal.** Implement a typed `groupBy<T, K extends string | number>(xs: readonly T[], key: (x: T) => K): Record<K, T[]>` function with comprehensive tests.

**Acceptance criteria:**

- `readonly` on the input parameter.
- `noUncheckedIndexedAccess` enabled in `tsconfig.json`.
- Tests cover: empty array, single-key grouping, multi-key grouping, numeric keys.
- No use of `any`.

**Hints:**

- `Record<K, T[]>` maps each key to an array of matching elements.
- Use `??=` to lazily initialize each group array.

**Stretch:** Add a `countBy` function that returns `Record<K, number>` and a `partitionBy` that returns `[T[], T[]]` based on a predicate.
