# Mini-project — 09-enums

_Companion chapter:_ [`09-enums.md`](../09-enums.md)

**Goal.** Model your project's user roles two ways: (a) string `enum Role`, (b) `as const` + derived union type. Write tests that compare the behavior and examine the compiled JavaScript output.

**Acceptance criteria:**

- Both approaches define the same set of roles: `Admin`, `Editor`, `Viewer`.
- A `hasPermission(role: Role, action: string): boolean` function works with both approaches.
- Tests verify iteration over values with `Object.values(Role)`.
- Compare the emitted JS for both approaches in a comment or test file.

**Hints:**

- Compile with `npx tsc` and inspect `dist/` to see the emitted JavaScript.
- The `as const` pattern emits a plain object; the enum emits an IIFE.

**Stretch:** Add a runtime guard `isRole(x: unknown): x is Role` for both approaches. Which is easier to write?
