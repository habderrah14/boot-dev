# Mini-project — 03-architecture

_Companion chapter:_ [`03-architecture.md`](../03-architecture.md)

**Goal.** Scaffold a `users` feature with full layered architecture.

**Acceptance criteria:**

- `schemas/user.ts` — Zod schemas for `CreateUser` and `User`.
- `storage/users.ts` — `UserStorage` interface + Postgres implementation + in-memory implementation.
- `services/users.ts` — `makeUserService(deps)` with `register`, `getById`, `list`.
- `routes/users.ts` — thin handlers using the service.
- `main.ts` — composition root that wires everything and starts the server.
- Tests run the service with the in-memory adapter and pass without any external dependencies.

**Hints:**

- Start with the interface. Write the in-memory adapter. Wire the service and write tests. Add routes last.
- Use `composeApp()` so your tests and your `main.ts` share the same wiring logic.

**Stretch:** Add an `orders` feature following the same structure. Verify that the two features are completely independent — removing one should not affect the other.
