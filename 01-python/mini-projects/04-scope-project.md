# Mini-project — 04-scope

_Companion chapter:_ [`04-scope.md`](../04-scope.md)

**Goal.** Build `counter.py`: `make_counter()` returns `(get, inc, reset)` closures. Multiple counters created from the same factory must be independent.

**Acceptance criteria.**

- `get`, `inc`, `reset` all share state via `nonlocal`.
- Two counters from two `make_counter()` calls have independent state.
- A `unittest.TestCase` proves independence (`c1.inc()` doesn't affect `c2.get()`).
- The module exports nothing on `from counter import *` other than `make_counter`.

**Hints.** Use `__all__ = ["make_counter"]` to control what `import *` exposes. Use `assertEqual` to compare counter values.

**Stretch.** Add a `step` parameter to `make_counter(start=0, step=1)` so you can build a counter that ticks by 5.
