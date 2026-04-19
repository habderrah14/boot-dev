# Mini-project — 10-type-narrowing

_Companion chapter:_ [`10-type-narrowing.md`](../10-type-narrowing.md)

**Goal.** Build a type-safe JSON validator module with composable guards: `isString`, `isNumber`, `isRecord`, `hasField`, `isArrayOf`, `isUser`, and `assertIsUser`. Test by passing valid and invalid JSON to `assertIsUser` and catching errors.

**Acceptance criteria:**

- All guards use `x is T` predicates.
- `assertIsUser` uses `asserts x is T`.
- Tests cover: valid user, missing fields, wrong field types, null, arrays, primitives.
- `isArrayOf` is generic: `isArrayOf<T>(arr: unknown, guard: (x: unknown) => x is T): arr is T[]`.
- No use of `any` (except inside predicate bodies for property access on `unknown`).

**Hints:**

- Build guards compositionally: `isUser` uses `isRecord`, `hasField`, and `isString`.
- `hasField(x, "name", isString)` checks both presence and type.

**Stretch:** Add `isOneOf<T extends string>(value: unknown, allowed: readonly T[]): value is T` for validating literal unions at runtime.
