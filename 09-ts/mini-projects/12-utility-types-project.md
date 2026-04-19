# Mini-project — 12-utility-types

_Companion chapter:_ [`12-utility-types.md`](../12-utility-types.md)

**Goal.** Re-type an existing CRUD module using utility types to eliminate duplicate type declarations.

**Acceptance criteria:**

- A single `User` source-of-truth type.
- `UserCreateInput = Omit<User, "id" | "createdAt">`.
- `UserUpdateInput = Partial<Omit<User, "id" | "createdAt">>`.
- `PublicUser = Omit<User, "passwordHash">`.
- CRUD functions (`create`, `update`, `findById`, `delete`) use these derived types.
- No duplicate field declarations across types.

**Hints:**

- Start by defining the "full" `User` type with all fields.
- Derive everything else with `Pick`, `Omit`, `Partial`.
- Test that compile errors appear when you try to pass wrong fields.

**Stretch:** Add a `UserEvent` type using a `Record`-based event map: `Record<"created" | "updated" | "deleted", { userId: number; timestamp: Date }>`.
