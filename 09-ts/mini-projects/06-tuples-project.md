# Mini-project — 06-tuples

_Companion chapter:_ [`06-tuples.md`](../06-tuples.md)

**Goal.** Create a `pair.ts` module with the following typed utilities:
- `swap<A, B>(t: readonly [A, B]): [B, A]`
- `zip<A, B>(as: readonly A[], bs: readonly B[]): [A, B][]`
- `unzip<A, B>(pairs: readonly (readonly [A, B])[]): [A[], B[]]`
- `enumerate<T>(xs: readonly T[]): [number, T][]`

**Acceptance criteria:**

- All functions use `readonly` on input parameters.
- Tests cover edge cases: empty arrays, unequal-length inputs for `zip`.
- No use of `any`.

**Hints:**

- `zip` should stop at the shorter array's length.
- `unzip` is the inverse of `zip`.

**Stretch:** Add a `mapPair<A, B, C, D>(pair: readonly [A, B], f: (a: A) => C, g: (b: B) => D): [C, D]` function.
