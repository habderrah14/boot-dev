# Mini-project — 07-intersections

_Companion chapter:_ [`07-intersections.md`](../07-intersections.md)

**Goal.** Define mixin types `Timestamped`, `SoftDeletable`, and `Audited`. Compose them into `User` and `Post` entity types. Write utility functions `softDelete`, `restore`, and `markModified` that work generically on any entity with the appropriate mixin.

**Acceptance criteria:**

- Each mixin is an independent type.
- `User` and `Post` are composed via `&`.
- Generic functions constrained with `extends` — e.g., `softDelete<T extends SoftDeletable>(entity: T): T`.
- Tests verify that conflicting property types produce `never`.
- No use of `any`.

**Hints:**

- `softDelete` sets `deletedAt` to `new Date()`.
- `restore` sets `deletedAt` back to `null`.
- Test type errors by intentionally intersecting conflicting types and observing the `never` result.

**Stretch:** Add a `Versioned` mixin with `version: number` and a `bumpVersion<T extends Versioned>(entity: T): T` function.
