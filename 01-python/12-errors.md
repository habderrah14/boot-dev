# Chapter 12 — Errors

> Errors are not the enemy. Silent bugs are. This chapter is about how to *welcome* errors while refusing to let them crash the world.

## Learning objectives

By the end of this chapter you will be able to:

- Raise and catch exceptions with `try / except / else / finally`.
- Choose between EAFP and LBYL idioms appropriately.
- Define and raise a custom exception that preserves cause.
- Use `with` for guaranteed resource cleanup.
- Recognize when "errors as values" beats exceptions.

## Prerequisites & recap

- [Functions](03-functions.md) — exceptions cross function boundaries.
- [Testing & debugging](05-testing-and-debugging.md).

Recap from chapter 03: validate at the boundary, raise early. From chapter 05: `assert` is *not* for input validation; `raise` is.

## The simple version

When something goes wrong, **raise** an exception with a clear message. Where you can do something useful about it, **catch** it narrowly. Where you can't, let it propagate — your caller might know what to do, or your top-level error handler will turn it into a 500 response.

The biggest single rule: **catch the narrowest exception type that makes sense, and never `except:` bare.**

## In plain terms (newbie lane)

This chapter is really about **Errors**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How a `try / except / else / finally` block dispatches.

```
   ┌────────────┐
   │    try     │
   │  do work   │
   └──────┬─────┘
          │
       success ?
        │      │
        │ yes  │ no
        ▼      ▼
   ┌────────┐  ┌──────────────────┐
   │  else  │  │ except <Match>?  │
   │ ran ok │  │  yes → handler   │
   └────┬───┘  │  no  → propagate │
        │      └────────┬─────────┘
        ▼               ▼
   ┌────────────────────────┐
   │       finally          │  ← always runs (success, caught, or propagating)
   │   close, release, log  │
   └────────────────────────┘
```

`else` runs *iff* the `try` succeeded. `finally` runs *always* — including when an exception is propagating out.

## Concept deep-dive

### Raising

```python
def sqrt(x: float) -> float:
    if x < 0:
        raise ValueError(f"sqrt of negative: {x}")
    return x ** 0.5
```

`raise` with a built-in exception class (or a subclass) and an informative message. The message ends up in logs and tracebacks; future-you will read it under pressure — make it useful.

Common built-ins to raise:

- `ValueError` — right type, wrong value (`-1` for a count).
- `TypeError` — wrong type (`"5"` where a number was expected).
- `KeyError` / `IndexError` — missing key / bad index.
- `FileNotFoundError`, `PermissionError`, `TimeoutError` — OS conditions.
- `RuntimeError` — generic; rarely the best choice.
- `NotImplementedError` — abstract method that subclasses must override.

### Catching

```python
try:
    result = risky()
except ValueError as e:
    log.warning("bad value: %s", e)
    result = None
except (KeyError, IndexError):
    result = None
else:
    log.info("happy path")
finally:
    cleanup()
```

- `except T as e` binds the exception to `e`.
- `except (A, B)` matches either type.
- `else` runs only when no exception was raised in `try`.
- `finally` always runs.

**Never** `except:` bare or `except BaseException:` — both swallow `KeyboardInterrupt` and `SystemExit`, which means Ctrl-C stops working. **Avoid** `except Exception:` unless you re-raise after logging or are at the top of an event loop.

### EAFP vs. LBYL

Two philosophies:

- **LBYL** (Look Before You Leap): `if k in d: x = d[k]`.
- **EAFP** (Easier to Ask Forgiveness than Permission): `try: x = d[k] except KeyError: ...`.

Python idiomatically prefers EAFP when:

- The happy path dominates (rare exceptions are cheap).
- The check would race with the action (multi-threaded, filesystem, network).

LBYL is fine when checking is cheap and the failure is expected often (e.g., `if user.is_admin: ...`).

### Custom exceptions

```python
class ValidationError(Exception):
    """Raised when user input fails validation."""


def parse_age(s: str) -> int:
    try:
        n = int(s)
    except ValueError as e:
        raise ValidationError(f"age not numeric: {s!r}") from e
    if not 0 <= n <= 120:
        raise ValidationError(f"age out of range: {n}")
    return n
```

`raise X from e` chains the original exception so the traceback shows both — invaluable for debugging.

Define your own exception types for *your* error categories so callers can `except ValidationError` instead of trying to disambiguate from a built-in. Group related errors under a base class:

```python
class AppError(Exception): pass
class ValidationError(AppError): pass
class AuthError(AppError): pass
```

A single `except AppError` then catches all your application errors.

### `with` and context managers

```python
with open("data.txt") as f:
    text = f.read()
# file is closed here, even if read() raised
```

`with` guarantees cleanup. Use it for *every* resource that has a release: files, locks, sockets, database connections, transactions. The `__enter__` / `__exit__` protocol underneath is covered in [Module 04](../04-oop/README.md).

Stack `with` statements when you have multiple resources:

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())
```

### Errors as values

Sometimes exceptions are the wrong tool. For deeply hot loops or APIs where every call might fail in known ways, returning an explicit `(value, error)` tuple or an `Either`-style result type avoids exception-handling overhead. Modules 09 (TypeScript) and 12 (HTTP servers) explore this trade-off in detail.

## Why these design choices

- **Narrow excepts.** Catching `Exception` hides every unrelated bug — typos, attribute errors, subtle logic mistakes. The whole point of exceptions is to separate the unusual from the routine; broad catches collapse that distinction.
- **`raise X from e` instead of `raise X`.** The original cause carries the line numbers and types you'll need to debug. Losing it costs hours.
- **Custom exception classes.** Built-ins are coarse: `ValueError` could mean "bad email" or "negative discount". Your own class lets the catcher act on the *kind* of error, not just the bad-news fact.
- **`with` over try/finally.** Easier to read, harder to get wrong, no chance of forgetting `close`. Files opened without `with` are a warning sign in code review.
- **EAFP over LBYL in concurrent code.** "Check then act" is a TOCTOU bug factory across threads, processes, and the filesystem. The action is the only atomic operation that matters.
- **When you'd choose differently.** Library authors crossing FFI or performance-critical numerical code often prefer return codes or sentinel `None` to avoid exception-frame allocation. Same applies to fast iteration loops where a missing key is expected on most iterations.

## Production-quality code

### Example 1 — Retry with bounded backoff

```python
"""Retry a flaky callable up to `attempts` times with exponential backoff."""

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    attempts: int = 3,
    base_delay: float = 1.0,
    catch: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError),
) -> T:
    """Call fn(); on `catch` exceptions retry with backoff `base_delay * 2**i`."""
    last_exc: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except catch as e:
            last_exc = e
            if i == attempts - 1:
                break
            time.sleep(base_delay * (2 ** i))
    assert last_exc is not None
    raise last_exc
```

Bounded attempts; explicit catch list; preserves the last exception for debugging.

### Example 2 — Validation that surfaces all the bad fields

```python
"""Aggregate validation errors instead of failing on the first one."""


class ValidationError(Exception):
    def __init__(self, errors: dict[str, str]):
        super().__init__(f"validation failed: {errors}")
        self.errors = errors


def validate_user(body: dict) -> dict:
    errors: dict[str, str] = {}

    email = body.get("email")
    if not isinstance(email, str) or "@" not in email:
        errors["email"] = "must be a string containing '@'"

    age_raw = body.get("age")
    try:
        age = int(age_raw)
        if not 0 <= age <= 120:
            errors["age"] = f"out of range: {age}"
    except (TypeError, ValueError):
        errors["age"] = f"must be an integer; got {age_raw!r}"

    if errors:
        raise ValidationError(errors)
    return {"email": email, "age": age}
```

Aggregating errors gives users one round-trip to fix all issues, instead of a fix-one-then-discover-another loop. Pydantic and similar libraries do this for you in production.

## Security notes

- **Never include secrets in exception messages.** A `ValueError("invalid token: sk-live-abc...")` leaks the token to logs forever. Strip or redact before raising.
- **Distinguish "bad input" from "internal error" at the API boundary.** Return `400 Bad Request` for `ValidationError`, `500` for everything else — but don't leak stack traces. The user gets `{"error": "bad request"}`; your logs get the full traceback.
- **Avoid `eval()` in error handlers.** Tempting for "convert this string back to a value", but a malicious traceback string becomes code execution. Use safe parsers.
- **Don't catch `Exception` and continue silently** — the next operation runs in an unknown state. Either handle specifically or fail loud.

## Performance notes

- **Raising and catching is fast** when uncommon (~10 µs in CPython). It is **slow** in tight loops where every iteration raises (~1000× slower than normal flow). Don't use exceptions as control flow inside numeric loops.
- **`try` block with no exception is essentially free** — entering the block costs ~1 ns. Only the *raise* path costs.
- **`with open` adds one frame** to the call stack and an `__enter__`/`__exit__` pair. Negligible compared to the I/O you're about to do.
- **Custom exception classes are cheap** — define as many as makes the code clear.

## Common mistakes

- **Bare `except:`.** Symptom: Ctrl-C does nothing; bugs vanish. Cause: catching `KeyboardInterrupt`/`SystemExit`. Fix: catch a specific type, or `except Exception` only at top-level with logging.
- **`except Exception:` then continue.** Symptom: program runs in undefined state. Cause: blanket catch. Fix: catch narrowly, log + re-raise, or fail.
- **Lost cause.** Symptom: `ValidationError` traceback shows nothing about the original `ValueError`. Cause: `raise X` instead of `raise X from e`. Fix: `from e`.
- **Forgetting `with`.** Symptom: file descriptor leak; eventually `Too many open files`. Cause: `f = open(...)` with no close. Fix: always `with open(...) as f:`.
- **`else` order.** Symptom: `SyntaxError`. Cause: putting `else` after `finally`. Fix: order is `try` → `except` → `else` → `finally`.
- **`assert` for input validation.** Symptom: production bypasses checks. Cause: `assert` is stripped under `-O`. Fix: `if not ok: raise ValueError(...)`.

## Practice

1. **Warm-up.** Wrap `1/0` in a `try/except` that prints a friendly message.
2. **Standard.** Implement `safe_get(d, path)` taking a dot-path string `"a.b.c"` and a nested dict; return the value at that path or `None` if any key is missing.
3. **Bug hunt.** Why does this raise `SyntaxError`?

    ```python
    try:
        do_work()
    finally:
        print("done")
    else:
        print("ok")
    ```

4. **Stretch.** Write a `suppress(exc_type)` context manager (without `contextlib`) that swallows the given exception type.
5. **Stretch++.** Write a `@retry(attempts=3, on=(IOError,))` decorator (function that returns a function — see [Module 05](../05-fp/08-decorators.md) for the deep dive).

<details><summary>Show solutions</summary>

```python
try:
    1 / 0
except ZeroDivisionError as e:
    print(f"oops: {e}")
```

```python
def safe_get(d, path):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur
```

3. `else` must come *before* `finally` and immediately after the `except` clause(s):

```python
try:
    do_work()
except SomethingError:
    handle()
else:
    print("ok")
finally:
    print("done")
```

```python
class suppress:
    def __init__(self, exc): self.exc = exc
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, self.exc)
```

```python
import time, functools

def retry(attempts=3, on=(Exception,), base_delay=1.0):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except on as e:
                    last = e
                    if i == attempts - 1: break
                    time.sleep(base_delay * 2 ** i)
            raise last
        return wrapper
    return deco
```

</details>

## Quiz

1. Which block always runs?
    (a) `try` (b) `except` (c) `else` (d) `finally`
2. `except:` with no class catches:
    (a) only `Exception` (b) all exceptions including `KeyboardInterrupt` (c) only user errors (d) nothing
3. EAFP stands for:
    (a) Extract, Apply, Filter, Print (b) Easier to Ask Forgiveness than Permission (c) Every Attempt Fails Politely (d) Exceptions Are For People
4. `with open(...)` guarantees:
    (a) the file exists (b) the file is closed after the block (c) data is flushed to disk immediately (d) atomicity
5. `raise X from e` primarily:
    (a) converts exception types (b) chains causes in the traceback (c) silences the original (d) is invalid

**Short answer:**

6. Why is bare `except:` almost always a bug?
7. Give one case where exceptions are better than return-value error handling.

*Answers: 1-d, 2-b, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [12-errors — mini-project](mini-projects/12-errors-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Raise narrow exceptions with clear messages and `raise X from e` to chain causes.
- Catch narrowly; let unknown errors propagate.
- `with` is for resources; `try/except/else/finally` is for control flow.
- Don't use exceptions as control flow inside hot loops.

## Further reading

- Python docs — [*Errors and Exceptions*](https://docs.python.org/3/tutorial/errors.html).
- [PEP 3134 — Exception Chaining](https://peps.python.org/pep-3134/).
- Next: [practice](13-practice.md).
