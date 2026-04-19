# Mini-project — 03-unions

_Companion chapter:_ [`03-unions.md`](../03-unions.md)

**Goal.** Model an HTTP outcome as a discriminated union with variants `Ok`, `Redirect`, `NotFound`, and `ServerError`. Write a `handle(outcome)` function using `switch` and a `never` exhaustiveness guard.

**Acceptance criteria:**

- Each variant has a `status` discriminant and appropriate payload fields.
- `handle` returns a human-readable string for each variant.
- Adding a new variant without handling it causes a compile error.
- No use of `any`.

**Hints:**

- Use literal types for HTTP status codes within each variant.
- The `never` check goes in the `default` branch.

**Stretch:** Add a `toResponse(outcome: HttpOutcome): { statusCode: number; body: string }` function that converts each variant to an HTTP-like response object.
