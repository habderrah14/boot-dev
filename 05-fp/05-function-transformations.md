# Chapter 05 — Function Transformations

> "A function transformation takes a function and returns a new function that does something related but different."

## Learning objectives

By the end of this chapter you will be able to:

- Explain what a function transformation is and why it's a core FP pattern.
- Use `functools.partial` to pre-fill arguments and create specialized functions.
- Write function wrappers that add behavior (timing, retrying, logging) transparently.
- Compose small functions into pipelines using `pipe` and `compose`.

## Prerequisites & recap

- [First-class functions](02-first-class-functions.md) — functions are values; higher-order functions.
- [Pure functions](03-pure-functions.md) — side-effect-free logic.

## The simple version

A function transformation is a function that takes a function as input and returns a *new* function as output. The new function does something related — maybe it times how long the original takes, retries it on failure, or pre-fills some of its arguments.

You use this pattern constantly in backend code: wrapping HTTP handlers with authentication checks, adding retry logic to flaky API calls, or specializing a generic function for a specific use case. The idea is simple — don't modify the original function, wrap it.

## Visual flow

```
  partial: pre-fill arguments
  +---------+                    +------------+
  | greet   | -- partial("hi") -> | hello      |
  | (a, b)  |                    | (b)        |
  +---------+                    +------------+
  greet("hi", "Ada")              hello("Ada")
       same result: "hi, Ada!"

  Wrapping: add behavior around a function
  +-------------------+
  | wrapper           |
  |  +- before -----+ |
  |  | start timer   | |
  |  +---------------+ |
  |  +- fn() -------+ |     +------+
  |  | original call | | --> | fn   |
  |  +---------------+ |     +------+
  |  +- after ------+ |
  |  | log elapsed   | |
  |  +---------------+ |
  +-------------------+

  Composition: chain functions
  input --> f1 --> f2 --> f3 --> output
           strip   lower  slug

  Caption: Transformations create new functions from existing ones
  by pre-filling, wrapping, or composing.
```

## Concept deep-dive

### `functools.partial` — specializing functions

`partial` creates a new function with some arguments pre-filled:

```python
from functools import partial

def greet(greeting, name):
    return f"{greeting}, {name}!"

hello = partial(greet, "hello")
hello("Ada")         # "hello, Ada!"
hello("Alan")        # "hello, Alan!"
```

Why is this useful? Because it lets you create specialized versions of generic functions without rewriting them. You configure once and call many times. This shows up in backend code everywhere:

```python
def handler(request, *, storage):
    ...

app.route("/users", partial(handler, storage=MY_STORAGE))
```

That's dependency injection without a framework — one line.

### Wrapping a function

A wrapper takes a function, returns a new function that adds behavior around it. The shape is always the same:

```python
import time
import functools

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = time.perf_counter() - t0
            print(f"{fn.__name__} took {dt*1000:.1f} ms")
    return wrapper
```

Key details:

- `*args, **kwargs` makes the wrapper accept any signature — it's transparent.
- `@functools.wraps(fn)` copies `__name__`, `__doc__`, and `__module__` from the original function to the wrapper. Without it, introspection tools see "wrapper" instead of the real function name.
- `try/finally` ensures timing is reported even if the function raises.

This is the decorator pattern. The `@decorator` syntax you'll see in chapter 08 is just shorthand for `fn = decorator(fn)`.

### Composition

Composition chains small functions into a pipeline:

```python
def compose(*fns):
    """Right-to-left composition: compose(f, g)(x) = f(g(x))."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed

def pipe(*fns):
    """Left-to-right composition: pipe(f, g)(x) = g(f(x))."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped
```

`pipe` reads in the same order the data flows — most people find it more natural:

```python
sanitize = pipe(str.strip, str.lower, lambda s: s.replace(" ", "-"))
sanitize("  Hello World  ")   # "hello-world"
```

### Currying (preview)

Currying is a specific transformation that turns `f(a, b)` into `f(a)(b)` — each call fills exactly one argument. It's covered in depth in [chapter 07](07-currying.md). For most Python code, `partial` is the practical choice.

## Why these design choices

**Why `partial` instead of lambdas?** `partial(greet, "hello")` preserves the original function's metadata — its name, module, and docstring are accessible through `partial.func`, `partial.args`, and `partial.keywords`. A lambda `lambda name: greet("hello", name)` discards all that. Tools that inspect callables (debuggers, API docs, frameworks) work better with `partial`.

**Why always use `@functools.wraps`?** Without it, your wrapper replaces the original function's identity. `help(fn)` shows `wrapper(*args, **kwargs)` instead of the real signature. Framework routing tables show "wrapper" instead of "handle_users". It's one line and always correct.

**When would you pick differently?** If you're in a language with native composition operators (Haskell's `.`, Elixir's `|>`), you'd use those instead of building `pipe`/`compose` manually. In Python, the manual version is fine — it's simple, readable, and works.

**`pipe` vs. `compose`:** `pipe` reads left-to-right (data flow order). `compose` reads right-to-left (mathematical order, like f ∘ g). Python code reviews tend to prefer `pipe` because it matches the reading direction. Either is fine — pick one and be consistent.

## Production-quality code

```python
import functools
import time
from typing import Callable, TypeVar

T = TypeVar("T")


def timed(fn: Callable[..., T]) -> Callable[..., T]:
    """Measure and print execution time."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - t0
            print(f"{fn.__name__}: {elapsed*1000:.1f}ms")
    return wrapper


def retry(attempts: int = 3, delay: float = 0.1, backoff: float = 2.0):
    """Retry on exception with exponential backoff."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorate(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if i < attempts - 1:
                        time.sleep(delay * backoff ** i)
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorate


def throttle(fn: Callable[..., T], min_interval: float = 1.0) -> Callable[..., T]:
    """Limit call rate to at most once per min_interval seconds."""
    last_called = 0.0

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        nonlocal last_called
        now = time.monotonic()
        wait = min_interval - (now - last_called)
        if wait > 0:
            time.sleep(wait)
        last_called = time.monotonic()
        return fn(*args, **kwargs)
    return wrapper


def pipe(*fns: Callable) -> Callable:
    """Left-to-right function composition."""
    if not fns:
        raise TypeError("pipe requires at least one function")

    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# --- Usage ---
@timed
@retry(attempts=3, delay=0.05)
def fetch_data(url: str) -> str:
    import urllib.request
    return urllib.request.urlopen(url).read().decode()

slugify = pipe(str.strip, str.lower, lambda s: s.replace(" ", "-"))
assert slugify("  Hello World  ") == "hello-world"
```

## Security notes

- **Retry wrappers and authentication:** If a retry wrapper re-sends requests with credentials, be aware that each retry is a new opportunity for interception. Use HTTPS and ensure tokens haven't expired between retries.
- **Throttle as rate-limit bypass:** A `throttle` wrapper limits *your own* call rate, but it doesn't protect your server from external abuse. Don't confuse client-side throttling with server-side rate limiting.
- **Wrapping security-sensitive functions:** If you wrap an authentication check, make sure the wrapper doesn't accidentally swallow the exception that signals "unauthorized." Be explicit about what you catch.

## Performance notes

- **`partial` overhead:** `functools.partial` adds ~30 ns per call in CPython — negligible for nearly all use cases.
- **Wrapper overhead:** Each wrapper adds one Python function call (~50–100 ns). Stacking three wrappers adds ~200 ns. For request-level handlers (millisecond scale), this is invisible. For inner loops called millions of times, it matters.
- **`pipe` overhead:** Each function in the pipe adds one call. A 5-stage pipe adds ~500 ns per invocation. If performance is critical, inline the pipeline.
- **`retry` with exponential backoff:** The delay grows as `delay * backoff^i`. With defaults (0.1s, backoff=2.0), three attempts take 0 + 0.1 + 0.2 = 0.3s worst case. Five attempts take 0 + 0.1 + 0.2 + 0.4 + 0.8 = 1.5s. Plan accordingly.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `help(fn)` shows `wrapper(*args, **kwargs)` after wrapping | Missing `@functools.wraps(fn)` on the wrapper function | Always add `@functools.wraps(fn)` as the first line of your wrapper. |
| 2 | `partial` raises `TypeError: got multiple values for argument` | Pre-filling a keyword argument that the caller also passes | Use `partial` for positional args or keyword-only args. Check the original signature before pre-filling. |
| 3 | Retry wrapper silently swallows errors | Catching `Exception` in a retry without re-raising after final attempt | Always re-raise on the last attempt: `if i == attempts - 1: raise`. |
| 4 | Stacked wrappers produce confusing tracebacks | Too many layers of `wrapper` functions with no distinguishing names | Use `@functools.wraps` on every layer, and keep wrapper stacks shallow (2–3 max). |
| 5 | `compose(f, g)(x)` produces unexpected results | Confusion about direction — `compose` applies right-to-left, `pipe` applies left-to-right | Pick one convention, document it, and stick to it. Use `pipe` if you find it more readable. |

## Practice

**Warm-up.** Create a partial function from `str.startswith` that checks for the prefix `"http"`. Test it on a few strings.

<details><summary>Solution</summary>

```python
from functools import partial

is_http = partial(str.startswith, "http")
# This doesn't work as expected because str.startswith is unbound.
# Instead:
def starts_with(prefix, s):
    return s.startswith(prefix)

is_http = partial(starts_with, "http")
assert is_http("https://example.com") is True
assert is_http("ftp://files.com") is False
```

</details>

**Standard.** Build the `timed` wrapper from this chapter and apply it to a function that sums a large range.

<details><summary>Solution</summary>

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__}: {(time.perf_counter() - t0)*1000:.1f}ms")
    return wrapper

@timed
def big_sum(n):
    return sum(range(n))

result = big_sum(10_000_000)  # prints: big_sum: ~120ms
```

</details>

**Bug hunt.** After wrapping, `help(fn)` shows `wrapper(*args, **kwargs)`. Why, and how do you fix it?

<details><summary>Solution</summary>

The wrapper function replaces the original function's identity. Without `@functools.wraps(fn)`, the wrapper's own `__name__`, `__doc__`, and `__qualname__` are used instead. Fix: add `@functools.wraps(fn)` as a decorator on the wrapper function.

</details>

**Stretch.** Implement `pipe(*fns)` (left-to-right composition) with input validation. Demonstrate it on a text-processing pipeline.

<details><summary>Solution</summary>

```python
def pipe(*fns):
    if not fns:
        raise TypeError("pipe requires at least one function")
    for i, f in enumerate(fns):
        if not callable(f):
            raise TypeError(f"Argument {i} is not callable: {f!r}")

    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped

clean = pipe(str.strip, str.lower, lambda s: s.replace(" ", "-"))
assert clean("  Hello World  ") == "hello-world"
```

</details>

**Stretch++.** Write `throttle(fn, per_seconds=1.0)` that limits a function to at most one call per `per_seconds`. Verify with timestamps.

<details><summary>Solution</summary>

```python
import functools, time

def throttle(per_seconds=1.0):
    def decorate(fn):
        last_called = [0.0]

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            elapsed = now - last_called[0]
            if elapsed < per_seconds:
                time.sleep(per_seconds - elapsed)
            last_called[0] = time.monotonic()
            return fn(*args, **kwargs)
        return wrapper
    return decorate

@throttle(per_seconds=0.5)
def ping():
    print(f"ping at {time.monotonic():.2f}")

for _ in range(3):
    ping()  # each call is ~0.5s apart
```

</details>

## In plain terms (newbie lane)
If `Function Transformations` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `functools.partial(f, 1)` returns:
    (a) A new function with the first argument pre-filled as 1
    (b) The return value of `f(1)`
    (c) A class instance
    (d) The original function unchanged

2. `@functools.wraps(fn)` preserves:
    (a) The function's source code
    (b) `__name__`, `__doc__`, `__module__`, and other metadata
    (c) The function's bytecode
    (d) Nothing — it's a no-op

3. `compose(f, g)(x)` equals:
    (a) `g(f(x))`
    (b) `f(g(x))`
    (c) `f(x) + g(x)`
    (d) Depends on implementation

4. A wrapper function should:
    (a) Always catch all exceptions
    (b) Be transparent by default — add specific behavior without altering the function's contract
    (c) Print all arguments for debugging
    (d) Return a tuple of (result, metadata)

5. `partial` vs. `lambda` for pre-filling arguments:
    (a) Identical in all ways
    (b) `partial` preserves introspection metadata better
    (c) `lambda` is always safer
    (d) `partial` is deprecated

**Short answer:**

6. Give one use of `functools.partial` in a web handler context.
7. Why do most Python developers prefer `pipe` over `compose`?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b, 6. Pre-filling a storage or database dependency into a handler function — `partial(handler, storage=db)` — so the router can call `handler(request)` without knowing about storage. This is dependency injection without a framework. 7. `pipe` reads left-to-right, which matches the data flow direction and the natural reading order in English. `compose` reads right-to-left (mathematical convention), which most people find less intuitive in code.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-function-transformations — mini-project](mini-projects/05-function-transformations-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A function transformation takes a function and returns a new function with modified behavior.
- `functools.partial` specializes functions by pre-filling arguments — lightweight dependency injection.
- Wrappers add behavior (timing, retrying, logging) around a function. Always use `@functools.wraps`.
- Compose small transforms into pipelines with `pipe` (left-to-right) or `compose` (right-to-left).

## Further reading

- Python docs: [`functools`](https://docs.python.org/3/library/functools.html) — `partial`, `wraps`, `reduce`.
- Next: [Closures](06-closures.md).
