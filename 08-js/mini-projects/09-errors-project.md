# Mini-project — 09-errors

_Companion chapter:_ [`09-errors.md`](../09-errors.md)

**Goal.** Build an `errors.js` module exporting a hierarchy of application errors and a demonstration script.

**Acceptance criteria:**

- Export `AppError` (base), `ValidationError`, `NotFoundError`, and `AuthError`.
- Each has a `code` string property (e.g., `"VALIDATION_ERROR"`, `"NOT_FOUND"`).
- Each supports `cause` chaining.
- A `demo.js` script imports the errors, simulates operations that throw each type, and catches them with appropriate handlers.
- The demo logs the full cause chain for any chained error.
- Tests with `node:test` verify error names, codes, `instanceof` checks, and cause chains.

**Hints:**

- A base `AppError` class with `code` and `statusCode` reduces duplication.
- Test `instanceof` both directly (`err instanceof NotFoundError`) and up the chain (`err instanceof AppError`).

**Stretch:** Add a `toJSON()` method on `AppError` that serializes the error (including cause chain) to a JSON-safe object suitable for API responses.
