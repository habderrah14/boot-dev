# Mini-project — 05-function-transformations

_Companion chapter:_ [`05-function-transformations.md`](../05-function-transformations.md)

**Goal.** Implement a decorator library (`transforms.py`) with `@timed`, `@retry(attempts, delay)`, and `@throttle(per_seconds)`. Stack all three on an HTTP-fetching function and demonstrate correct behavior.

**Acceptance criteria:**

- [ ] Each wrapper uses `@functools.wraps` and passes `*args, **kwargs` transparently.
- [ ] `@retry` uses exponential backoff: `delay * 2^attempt`.
- [ ] `@throttle` enforces minimum interval between calls.
- [ ] `@timed` reports execution time to stderr (not stdout).
- [ ] Stacking `@timed @retry(3) @throttle(0.5)` on a function works correctly.
- [ ] At least one test per wrapper, plus a test for the stacked combination.

**Hints:**

- Use `time.monotonic()` for throttle (not `time.time()`, which can jump).
- Remember: `@a @b @c def f` means `a(b(c(f)))`. The outermost decorator sees the final wrapper.

**Stretch:** Add a `@cache_with_ttl(seconds)` wrapper that caches results for a limited time, then re-calls the function.
