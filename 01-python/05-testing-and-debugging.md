# Chapter 05 — Testing and Debugging

> Your code's job is to work. Your *tests'* job is to make you believe it.

## Learning objectives

By the end of this chapter you will be able to:

- Write automated tests with `unittest`.
- Use `assert` for in-code invariants without leaning on it for input validation.
- Read a traceback and pause execution with `breakpoint()`.
- Distinguish unit, integration, and end-to-end tests and know how to mix them.

## Prerequisites & recap

- [Functions](03-functions.md) and [Scope](04-scope.md) — you can write a function and reason about where its names live.

Recap from chapter 03: pure functions (input → output, no side effects) are easy to test. The fewer side effects, the smaller and faster your tests.

## The simple version

A test is a second, independent description of what the code is supposed to do. When the code and the test disagree, *at least one* of them is wrong — and that disagreement is the most valuable signal in software.

Write the smallest test you can; run it before and after every change. Debugging then becomes "find the smallest failing test" rather than "stare at the code and hope".

## In plain terms (newbie lane)

This chapter is really about **Testing and Debugging**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The red → green → refactor cycle that drives test-first development.

```
   ┌──────────────┐
   │ Write a test │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐    ┌─ red:    test fails (expected)
   │   Run tests  │ ──▶│
   └──────┬───────┘    └─ green:  test passes
          │
          ▼
   ┌──────────────┐
   │ Implement /  │
   │   refactor   │
   └──────┬───────┘
          │
          └─────────────▶ run tests again
```

## Concept deep-dive

### `assert` — for invariants you control

```python
def abs_value(n: int | float) -> int | float:
    result = n if n >= 0 else -n
    assert result >= 0, "internal bug: abs returned negative"
    return result
```

`assert` raises `AssertionError` when the condition is false. It's for **invariants you control** — facts about *your* code's logic. The Python interpreter strips assertions when run with `-O`, so don't use `assert` for input validation or security checks. For untrusted inputs, `raise ValueError("...")` explicitly.

### `unittest` — the standard test framework

```python
# test_math_utils.py
import unittest

from math_utils import abs_value


class TestAbs(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(abs_value(3), 3)

    def test_negative(self):
        self.assertEqual(abs_value(-3), 3)

    def test_zero(self):
        self.assertEqual(abs_value(0), 0)


if __name__ == "__main__":
    unittest.main()
```

Run with `python3 -m unittest test_math_utils.py`. Every method whose name starts with `test_` runs as an isolated test; setup/teardown methods (`setUp`, `tearDown`) run around each test if defined.

**Naming convention:** name tests after *behaviors*, not functions: `test_returns_zero_for_empty_list`, not `test_average_1`. The name should describe what fails when the test fails.

### Tracebacks — read bottom to top

```
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    main()
  File "app.py", line 4, in main
    print(1/0)
ZeroDivisionError: division by zero
```

The **last line** tells you *what* happened. The frames above tell you *how you got there* (call stack, innermost last). Always start at the bottom.

### `breakpoint()` — the debugger you already have

```python
def discount(price: float, pct: float) -> float:
    breakpoint()                 # Python 3.7+, drops into pdb here
    return price * (1 - pct / 100)
```

When execution reaches `breakpoint()`, you get a `(Pdb)` prompt. Useful commands:

- `l` — list source around the current line
- `n` — execute next line (don't step into calls)
- `s` — step into the next call
- `p expr` — print the value of `expr`
- `pp expr` — pretty-print
- `c` — continue until the next breakpoint or end
- `q` — quit
- `w` — show the call stack (where am I?)

You can also set the `PYTHONBREAKPOINT` env var to swap in a richer debugger like `ipdb` without changing source.

### Kinds of tests

| Kind | What it covers | Speed | Volume |
|---|---|---|---|
| Unit | One function, no I/O | Microseconds–ms | Most |
| Integration | A few units + real DB / HTTP | 10s–100s of ms | Some |
| End-to-end | The whole system through its outermost interface | Seconds | A few |

The right ratio is roughly the **test pyramid**: many unit tests at the base, fewer integration tests, even fewer end-to-end. Inverting it (lots of slow E2E tests, few unit tests) gives you a brittle, slow CI that nobody trusts.

## Why these design choices

- **Unittest is in the standard library.** No dependency, runs on every Python install. `pytest` is more ergonomic and what most teams reach for in practice — but `unittest`'s `assertEqual` style ports over directly.
- **`assert` ≠ runtime validation.** The `-O` strip is a footgun if you don't know about it. Keep `assert` for "this should never happen, given my own code is correct"; use `raise` for anything driven by the outside world.
- **Test the behavior, not the implementation.** Tests that mirror the function line-by-line break on every refactor. Tests that name observable behavior survive rewrites.
- **`breakpoint()` over `print`-debugging.** Once you're in `pdb` you can inspect *anything*, not just what you remembered to print. Print debugging is fine for one-second reproductions; `breakpoint()` is better for any bug you can't reproduce in your head.
- **When you'd choose differently.** For tiny scripts (≤ 50 lines), formal tests are overkill — a `doctest` block in the docstring is enough. For libraries with public APIs, lean on property-based testing (`hypothesis`) on top of unit tests.

## Production-quality code

### Example 1 — Test, then fix

You discover that `average([])` raises `ZeroDivisionError`. Decide on the right behavior (return `0.0`) and *write the test first*:

```python
# test_stats.py
import unittest

from stats import average


class TestAverage(unittest.TestCase):
    def test_empty_returns_zero(self):
        self.assertEqual(average([]), 0.0)

    def test_basic(self):
        self.assertAlmostEqual(average([1, 2, 3]), 2.0)

    def test_negative(self):
        self.assertAlmostEqual(average([-1, 1]), 0.0)
```

Run — `test_empty_returns_zero` fails (red). Fix:

```python
# stats.py
def average(xs):
    """Return the arithmetic mean of xs, or 0.0 if empty."""
    if not xs:
        return 0.0
    return sum(xs) / len(xs)
```

Run again — green. Refactor if needed; tests stay green. You just did TDD.

### Example 2 — A test that uses a fixture

```python
# test_user_service.py
import unittest
from unittest.mock import MagicMock

from user_service import UserService


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock()
        self.svc = UserService(repo=self.repo)

    def test_create_calls_repo_with_email(self):
        self.repo.save.return_value = {"id": 1}
        result = self.svc.create("a@b.com")
        self.repo.save.assert_called_once()
        saved = self.repo.save.call_args[0][0]
        self.assertEqual(saved["email"], "a@b.com")
        self.assertEqual(result["id"], 1)
```

`MagicMock` stands in for the real repository so the test runs without a database. We assert *that* the right call was made — not what the database happened to do.

## Security notes

- **Never test against production credentials or data.** Tests should use throwaway databases (Docker, SQLite in-memory) and synthetic data. A bug in a test can `DROP TABLE` real customers.
- **Avoid asserting on secrets.** A failing test prints expected vs. actual; a test that compares `actual_token == "sk-live-..."` will dump the secret into CI logs forever.
- **`assert` does not enforce security.** `assert is_admin(user)` becomes a no-op under `-O`, silently bypassing your check. For authorization, raise.

## Performance notes

- Unit tests should run in **milliseconds**. A 5-second unit test is a sign you're doing integration work — move it to its own file or category.
- A reasonable target: full unit-test suite < 2 seconds for a junior project; under 30 seconds for a real service.
- Use `python3 -m unittest discover -s tests/ -v` to run a directory tree. CI tools parallelize across test files, so favor *more, smaller* test files over a few giant ones.
- `setUp` runs once per test method, not per class. If a fixture is expensive (load a CSV, spin up Docker), use `setUpClass` or move to integration tests with an explicit lifecycle.

## Common mistakes

- **Tests that hit the network.** Symptom: CI flaky on Mondays. Cause: real HTTP calls. Fix: stub or use `responses` / `pytest-httpx` to record interactions.
- **Tests that test the mock.** Symptom: rewriting the implementation breaks unrelated tests. Cause: tests over-specify how the function is called. Fix: assert on observable outcomes instead of internal call patterns.
- **`assert` for input validation.** Symptom: production has bugs that "should be impossible". Cause: assertions stripped under `-O`. Fix: `if not condition: raise ValueError(...)`.
- **Print-debugging committed.** Symptom: production logs full of `print("here")`. Cause: forgot to remove. Fix: a pre-commit hook that rejects bare `print` in non-CLI files.
- **One giant test.** Symptom: a single test fails and you can't tell which behavior broke. Cause: testing five things in one method. Fix: split.

## Practice

1. **Warm-up.** Write a `unittest.TestCase` with three tests for `double(n)` from chapter 03.
2. **Standard.** Add a `test_rejects_negative_subtotal` to `tip.py`'s mini-project.
3. **Bug hunt.** "All tests pass but the feature is broken in production." What's the most likely cause and how do you confirm it?
4. **Stretch.** Use `breakpoint()` to find why `sum([1, 2, "3"])` fails. Propose a fix that skips non-numbers.
5. **Stretch++.** Add a `doctest` to `celsius_to_fahrenheit`. Run with `python3 -m doctest -v math_utils.py`.

<details><summary>Show solutions</summary>

```python
class TestDouble(unittest.TestCase):
    def test_positive(self):  self.assertEqual(double(3), 6)
    def test_zero(self):      self.assertEqual(double(0), 0)
    def test_negative(self):  self.assertEqual(double(-4), -8)
```

3. The broken code path isn't covered. Add a test exercising it; it'll fail; then fix.

```python
def safe_sum(xs):
    return sum(x for x in xs if isinstance(x, (int, float)))
```

```python
def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit.

    >>> celsius_to_fahrenheit(0)
    32.0
    >>> celsius_to_fahrenheit(100)
    212.0
    """
    return c * 9 / 5 + 32
```

</details>

## Quiz

1. A *unit* test:
    (a) spans multiple services (b) exercises one function/unit, usually without I/O (c) must use mocks (d) requires `pytest`
2. Tracebacks are read:
    (a) top down (b) bottom up (c) alphabetically (d) by timestamp
3. `assert x` becomes a no-op when Python runs with:
    (a) `-v` (b) `-O` (c) `-B` (d) `-I`
4. The simplest way to stop at a line in modern Python is:
    (a) `import pdb; pdb.set_trace()` (b) `breakpoint()` (c) `raise Stop` (d) `os.abort()`
5. A red-green-refactor cycle looks like:
    (a) write code, then write test (b) write test, run, fix, refactor (c) write docs first (d) there is no cycle

**Short answer:**

6. Why does a test disagreeing with code give you useful information?
7. Why is `assert` the wrong tool for input validation in production?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-testing-and-debugging — mini-project](mini-projects/05-testing-and-debugging-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Tests are an independent description of intent — they catch the disagreement between you and your code.
- Use `unittest` for behavior tests; use `assert` for self-checks, never for input validation.
- Read tracebacks bottom-up; pause execution with `breakpoint()`.
- Aim for a pyramid: many fast unit tests, few slow end-to-end ones.

## Further reading

- Python docs — [`unittest`](https://docs.python.org/3/library/unittest.html), [`pdb`](https://docs.python.org/3/library/pdb.html).
- Michael Feathers, *Working Effectively with Legacy Code*.
- Brian Okken, *Python Testing with pytest* — when you outgrow `unittest`.
- Next: [computing](06-computing.md).
