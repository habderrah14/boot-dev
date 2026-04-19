# Mini-project — 08-decorators

_Companion chapter:_ [`08-decorators.md`](../08-decorators.md)

**Goal.** Write a decorator library (`decos.py`) with `@timed`, `@retry(attempts, delay)`, `@requires_auth`, and `@log_calls`. Stack all four on a single handler function and test the stacked behavior.

**Acceptance criteria:**

- [ ] Each decorator uses `@functools.wraps`.
- [ ] `@retry` uses exponential backoff and logs each retry attempt.
- [ ] `@requires_auth` checks for a `user` attribute on the first argument.
- [ ] `@timed` logs to `stderr` or a logger (not `print` to stdout).
- [ ] Stacking all four on one function works correctly and in the expected order.
- [ ] At least one test per decorator, plus a test for stacked behavior.
- [ ] `help(decorated_fn)` shows the original function's name and docstring.

**Hints:**

- Stack order matters: `@timed @retry @requires_auth @log_calls def handle(req)` means `timed(retry(requires_auth(log_calls(handle))))`. Think about which concern should be outermost.
- Use `unittest.mock.patch` or a fake request object in tests.

**Stretch:** Write a `@validate_args(**schemas)` decorator that checks argument types/ranges before calling the function.
