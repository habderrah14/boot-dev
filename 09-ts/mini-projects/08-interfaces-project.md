# Mini-project — 08-interfaces

_Companion chapter:_ [`08-interfaces.md`](../08-interfaces.md)

**Goal.** Create `Logger`, `Notifier`, and `Storage` interfaces. Implement in-memory versions of each. Wire them together in a `UserService` class that demonstrates dependency injection.

**Acceptance criteria:**

- `UserService` constructor takes `Repository<User>`, `Logger`, and `Notifier` as parameters.
- Swapping implementations (e.g., `ConsoleLogger` to `FileLogger`) requires no changes to `UserService`.
- Tests verify behavior by passing mock implementations.
- No use of `any`.

**Hints:**

- `Logger` might have `info(msg: string): void` and `error(msg: string): void`.
- `Notifier` might have `notify(userId: string, message: string): Promise<void>`.
- For testing, create a `SpyNotifier` that records calls without sending real notifications.

**Stretch:** Add an `Auditable` interface and make `UserService` log every mutation to an audit trail.
