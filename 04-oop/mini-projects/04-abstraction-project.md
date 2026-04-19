# Mini-project — 04-abstraction

_Companion chapter:_ [`04-abstraction.md`](../04-abstraction.md)

**Goal.** Design a `Notifier` abstraction with an ABC and two concrete implementations.

**Acceptance criteria:**

- `Notifier(ABC)` with `send(recipient: str, subject: str, body: str) -> None`.
- `EmailNotifier` — prints a formatted email to stdout (simulating SMTP).
- `LogNotifier` — writes to a logger.
- All implementation-specific errors are translated to a `NotificationError` domain exception.
- A `send_welcome(user, notifier: Notifier)` function that works with any implementation.
- Tests that verify both implementations and error translation.

**Hints:** Use `raise NotificationError("...") from exc` to chain the original exception. Write tests that mock a failure and assert `NotificationError` is raised.

**Stretch:** Add a `SlackNotifier` that uses a Protocol instead of the ABC, and show that `send_welcome` still works with it (you may need to adjust the type hint).
