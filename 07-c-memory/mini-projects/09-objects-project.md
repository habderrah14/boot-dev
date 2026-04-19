# Mini-project — 09-objects

_Companion chapter:_ [`09-objects.md`](../09-objects.md)

**Goal.** Implement a `Logger` with two backends — `stdout` and `file` — hidden behind a common vtable interface.

**Acceptance criteria:**

- `logger.h` exposes: `Logger *stdout_logger_new()`, `Logger *file_logger_new(const char *)`, `logger_info`, `logger_error`, `logger_close`.
- Callers use the same API regardless of backend.
- File logger appends; stdout logger writes to stdout/stderr.
- Clean under `-fsanitize=address` with no leaks.

**Hints:**

- The vtable can be a `static const` in the `.c` file — one instance shared by all loggers of that type.
- `(void)self;` suppresses "unused parameter" warnings for functions that don't need `self`.

**Stretch:** Add a `null_logger_new()` that silently discards all messages — useful for testing or disabling logging.
