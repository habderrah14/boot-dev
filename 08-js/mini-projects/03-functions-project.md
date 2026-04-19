# Mini-project — 03-functions

_Companion chapter:_ [`03-functions.md`](../03-functions.md)

**Goal.** Implement `debounce(fn, ms)` and `throttle(fn, ms)` with comprehensive tests.

**Acceptance criteria:**

- `debounce`: delays invocation until `ms` milliseconds after the last call; resets the timer on each call.
- `throttle`: invokes at most once per `ms` milliseconds; drops calls within the cooldown.
- Both preserve `this` and forward all arguments.
- Tests use `node:test` and `node:timers/promises` (or manual `setTimeout`) to verify timing behaviour.

**Hints:**

- `debounce` needs `clearTimeout` + `setTimeout`.
- `throttle` needs a timestamp check (`Date.now()`).
- Use `fn.apply(this, args)` inside the returned function to preserve context.

**Stretch:** Add a `leading` option to `debounce` that fires on the first call, then waits.
