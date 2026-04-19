# Chapter 08 — Decorators

> "A decorator is just a function transformation with special syntax. `@dec` before a `def` is shorthand for `fn = dec(fn)`."

## Learning objectives

By the end of this chapter you will be able to:

- Write decorators with and without arguments.
- Use `@functools.wraps` to preserve function metadata — and explain why it's non-negotiable.
- Apply decorators to methods and classes.
- Read decorator stacking order and predict the execution sequence.
- Recognize built-in decorators: `@property`, `@staticmethod`, `@classmethod`, `@cache`.

## Prerequisites & recap

- [Function transformations](05-function-transformations.md) — wrappers, `partial`, composition.
- [Closures](06-closures.md) — captured variables, inner functions.

## The simple version

A decorator is a function that takes a function, adds some behavior, and returns a new function. Python's `@decorator` syntax is just shorthand — writing `@timed` above a function definition is exactly the same as writing `fn = timed(fn)` after it.

That's all a decorator is. It's not magic, it's not a special language feature — it's a function transformation with convenient syntax. Decorators are how Python handles cross-cutting concerns: logging, timing, retrying, authentication, caching. Instead of copy-pasting the same `try/except` into every handler, you write it once as a decorator and apply it with a single line.

## Visual flow

```
  Without decorator syntax:          With decorator syntax:

  def fn(...): ...                   @dec
  fn = dec(fn)                       def fn(...): ...
                                        (identical result)

  Decorator without arguments:
  +-------+     +-------+     +----------+
  | @timed| --> | timed | --> | wrapper  |
  | def f |     | (f)   |     | (calls f)|
  +-------+     +-------+     +----------+

  Decorator WITH arguments:
  +---------------+     +---------+     +---------+     +----------+
  | @retry(n=3)   | --> | retry(3)| --> |decorate | --> | wrapper  |
  | def f         |     |         |     | (f)     |     | (calls f)|
  +---------------+     +---------+     +---------+     +----------+
                         returns         returns         calls f
                         decorate        wrapper         with retry

  Stacking order:
  @a                  means: f = a(b(c(f)))
  @b
  @c                  execution: c wraps first, b wraps c's result,
  def f(): ...                   a wraps b's result

  Caption: Decorators wrap functions. With-argument decorators
  have three nesting levels. Stacking applies bottom-up.
```

## Concept deep-dive

### The syntax

```python
@decorator
def fn(...): ...

# is exactly equivalent to:
def fn(...): ...
fn = decorator(fn)
```

That's the entire mechanism. The `@` line calls `decorator(fn)` and rebinds the name `fn` to whatever it returns. This means:

- A decorator must be callable.
- It receives the original function as its argument.
- It should return a callable (usually a wrapper function).

### Decorator without arguments

The most common pattern:

```python
import functools
import time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - t0
            print(f"{fn.__name__}: {elapsed*1000:.1f}ms")
    return wrapper

@timed
def work(n):
    return sum(range(n))
```

Key elements:
- `*args, **kwargs` makes the wrapper accept any signature transparently.
- `@functools.wraps(fn)` copies `__name__`, `__doc__`, `__module__`, `__qualname__`, and `__annotations__` from `fn` to `wrapper`.
- `try/finally` ensures timing is logged even if the function raises.

### Decorator with arguments

When you write `@retry(attempts=5)`, Python evaluates `retry(attempts=5)` first, which must *return* a decorator. So you need three levels of nesting:

```python
def retry(attempts=3, delay=0.1):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if i == attempts - 1:
                        raise
                    time.sleep(delay * 2 ** i)
        return wrapper
    return decorate

@retry(attempts=5)
def fetch(url): ...
```

Level 1: `retry(attempts=5)` — captures configuration, returns `decorate`.
Level 2: `decorate(fn)` — captures the function, returns `wrapper`.
Level 3: `wrapper(*args, **kwargs)` — runs on every call.

### Method decorators

Decorators work identically on methods. The first parameter is `self` (or `cls`):

```python
class API:
    @retry(attempts=3)
    def fetch(self, url):
        ...
```

The wrapper receives `self` as part of `*args` — it doesn't need special handling.

Built-in method decorators you should know:
- `@property` — turns a method into a computed attribute.
- `@staticmethod` — no `self` or `cls`, just a function in a class namespace.
- `@classmethod` — receives `cls` instead of `self`.

### Class decorators

`@dec` on a class receives the class and returns a (possibly modified) class:

```python
registry = {}

def register(cls):
    registry[cls.__name__] = cls
    return cls

@register
class Handler: ...

# registry == {"Handler": <class Handler>}
```

Common uses: plugin registries, ORM model registration, adding methods or attributes automatically.

### `@functools.wraps` — always use it

Without `@functools.wraps(fn)`:
- `wrapper.__name__` is `"wrapper"` instead of the original name.
- `wrapper.__doc__` is `None` instead of the original docstring.
- Framework routing tables, API docs, and debuggers all show wrong information.

It's one line. It's always correct. There is no reason to skip it.

### Stacking decorators

```python
@a
@b
@c
def f(): ...

# equals: f = a(b(c(f)))
```

The bottom decorator wraps first, the top one wraps last. When `f()` is called, `a`'s wrapper runs first (outermost), then `b`'s, then `c`'s, then the original function.

This means order matters. `@requires_auth` should be outside `@timed` if you want to time only authenticated calls.

## Why these design choices

**Why does Python use `@` syntax instead of just `fn = dec(fn)`?** Because the decorator is part of the function's definition — logically, it belongs right next to it. The `@` syntax makes the decoration visible at the point of definition, not buried after the function body.

**Why three levels for with-argument decorators?** Because the `@` line is evaluated first: `@retry(n=3)` calls `retry(n=3)`, which must return a decorator (a function that takes `fn`). That decorator returns the wrapper. There's no shortcut — this is a consequence of how Python evaluates the `@` line.

**When would you skip decorators?** When the wrapping is a one-off. If you only need to time one function once, just call `timed(my_function)()` directly. Decorators shine when the same cross-cutting concern applies to many functions.

## Production-quality code

```python
import functools
import logging
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def timed(fn: Callable[..., T]) -> Callable[..., T]:
    """Log execution time to the module logger."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - t0
            logger.debug("%s: %.1fms", fn.__name__, elapsed * 1000)
    return wrapper


def retry(
    attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Retry on specified exceptions with exponential backoff."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorate(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: Exception | None = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if i < attempts - 1:
                        wait = delay * backoff ** i
                        logger.warning(
                            "%s attempt %d/%d failed: %s. Retrying in %.2fs",
                            fn.__name__, i + 1, attempts, exc, wait,
                        )
                        time.sleep(wait)
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorate


def requires_auth(fn: Callable[..., T]) -> Callable[..., T]:
    """Reject requests without authenticated user."""
    @functools.wraps(fn)
    def wrapper(request: Any, *args: Any, **kwargs: Any) -> T:
        if not getattr(request, "user", None):
            raise PermissionError("Authentication required")
        return fn(request, *args, **kwargs)
    return wrapper


def log_calls(fn: Callable[..., T]) -> Callable[..., T]:
    """Log function name and arguments on each call."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        logger.info("Calling %s(args=%r, kwargs=%r)", fn.__name__, args, kwargs)
        return fn(*args, **kwargs)
    return wrapper


# --- Usage: stacking decorators ---
@timed
@retry(attempts=3, delay=0.05, exceptions=(ConnectionError, TimeoutError))
@log_calls
def fetch_user(user_id: int) -> dict:
    """Fetch user from external API."""
    import urllib.request
    resp = urllib.request.urlopen(f"https://api.example.com/users/{user_id}")
    import json
    return json.loads(resp.read())


# Class decorator example
_registry: dict[str, type] = {}

def register(cls: type) -> type:
    """Register a class in the global handler registry."""
    _registry[cls.__name__] = cls
    return cls

@register
class UserHandler:
    pass

assert "UserHandler" in _registry
```

## Security notes

- **Auth decorator bypass:** If `@requires_auth` raises a generic exception instead of returning an HTTP 401/403, the error might leak through a catch-all handler and expose stack traces. Return proper HTTP error responses.
- **Decorator order for security:** Place `@requires_auth` as the outermost decorator so it runs first. If `@timed` wraps outside `@requires_auth`, unauthenticated requests still consume timing resources.
- **Mutable state in decorators:** Shared caches or counters across requests can leak data between users. Use request-scoped storage, not decorator-level dicts, for user-specific data.

## Performance notes

- **Per-call overhead:** Each decorator adds one function call (~50–100 ns). Three stacked decorators add ~200 ns — invisible for HTTP handlers (ms scale), measurable for tight inner loops.
- **`@functools.wraps` cost:** The `wraps` decorator copies attributes at decoration time (once), not at call time. Zero runtime cost.
- **`@cache` unbounded growth:** `@functools.cache` uses an unbounded dict. For functions exposed to diverse inputs, use `@lru_cache(maxsize=N)`.
- **Decorator creation is one-time:** The nesting and closure creation happen once when the module loads. Only the innermost `wrapper` runs per call.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `help(fn)` shows `wrapper(*args, **kwargs)` | Missing `@functools.wraps(fn)` | Always add `@functools.wraps(fn)` to the wrapper function. |
| 2 | Decorator order produces unexpected behavior | Forgetting that `@a @b @c def f` means `a(b(c(f)))` — outermost runs first | Draw the nesting. Put the concern you want to run first on the outside (top). |
| 3 | Test failures because decorator shares state | Mutable variables (cache, counter) in the decorator persist across tests | Clear shared state in test teardown, or use request-scoped state instead of decorator-level state. |
| 4 | Decorated generator yields nothing | Wrapper calls `fn()` and returns the result, but doesn't iterate the generator | If the wrapped function is a generator, the wrapper should `yield from fn(*args, **kwargs)` or return the generator object. |
| 5 | `@retry` silently swallows the final exception | Missing re-raise on the last attempt | Ensure the loop re-raises on `i == attempts - 1`. |

## Practice

**Warm-up.** Write `@log_calls` — a decorator that prints the function name and arguments before each call.

<details><summary>Solution</summary>

```python
import functools

def log_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"Calling {fn.__name__}(args={args!r}, kwargs={kwargs!r})")
        return fn(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(1, 2)   # prints: Calling add(args=(1, 2), kwargs={})
```

</details>

**Standard.** Write `@retry(attempts, delay)` with exponential backoff.

<details><summary>Solution</summary>

```python
import functools, time

def retry(attempts=3, delay=0.1):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if i == attempts - 1:
                        raise
                    time.sleep(delay * 2 ** i)
        return wrapper
    return decorate

call_count = 0

@retry(attempts=3, delay=0.01)
def flaky():
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError("fail")
    return "success"

assert flaky() == "success"
assert call_count == 3
```

</details>

**Bug hunt.** Why does `help(fn)` show `wrapper` after decorating? How do you fix it?

<details><summary>Solution</summary>

Without `@functools.wraps(fn)`, the wrapper function replaces the original function's identity. `help()` shows the wrapper's `__name__` and `__doc__` instead of the original's. Fix: add `@functools.wraps(fn)` as a decorator on the `wrapper` function inside the decorator.

</details>

**Stretch.** Write a decorator that caches results by keyword arguments only, ignoring positional arguments.

<details><summary>Solution</summary>

```python
import functools

def cache_by_kwargs(fn):
    cache = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]
    return wrapper

@cache_by_kwargs
def fetch(url, *, format="json", page=1):
    print(f"Fetching {url} (format={format}, page={page})")
    return {"url": url, "format": format, "page": page}

fetch("/api", format="json", page=1)   # fetches
fetch("/api2", format="json", page=1)  # cache hit (same kwargs)
```

</details>

**Stretch++.** Write a class decorator `@auto_repr` that adds a `__repr__` method to any class, showing all `__init__` parameters.

<details><summary>Solution</summary>

```python
import inspect

def auto_repr(cls):
    params = list(inspect.signature(cls.__init__).parameters.keys())
    params = [p for p in params if p != "self"]

    def __repr__(self):
        attrs = ", ".join(f"{p}={getattr(self, p)!r}" for p in params)
        return f"{cls.__name__}({attrs})"

    cls.__repr__ = __repr__
    return cls

@auto_repr
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

u = User("Ada", 36)
assert repr(u) == "User(name='Ada', age=36)"
```

</details>

## In plain terms (newbie lane)
If `Decorators` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `@dec` before `def f` is equivalent to:
    (a) `dec = f`
    (b) `f = dec(f)`
    (c) `f = f(dec)`
    (d) `dec.f = f`

2. A decorator with arguments needs:
    (a) One level of function nesting
    (b) Two levels of function nesting
    (c) Three levels of function nesting
    (d) Metaclasses

3. `@functools.wraps(fn)` preserves:
    (a) The function's source code
    (b) `__name__`, `__doc__`, `__module__`, and other metadata
    (c) The function's bytecode
    (d) Nothing useful

4. `@a @b @c def f():` is equivalent to:
    (a) `a(f) + b(f) + c(f)`
    (b) `a(b(c(f)))`
    (c) `c(b(a(f)))`
    (d) `SyntaxError`

5. `@cache` is safe when the function is:
    (a) Pure — deterministic with no side effects
    (b) Async
    (c) A class method only
    (d) Any callable

**Short answer:**

6. Explain the three nested functions in a decorator with arguments.
7. Why should `@functools.wraps` always be used?

*Answers: 1-b, 2-c, 3-b, 4-b, 5-a, 6. Level 1 (e.g., retry(n=3)) captures configuration and returns the actual decorator. Level 2 (decorate(fn)) captures the function and returns the wrapper. Level 3 (wrapper(*args, **kwargs)) runs on every call, using both the configuration and the original function. 7. Without it, the wrapper replaces the original function's __name__, __doc__, and other metadata. Debuggers, logging, help(), and framework introspection all show "wrapper" instead of the real function name. It's one line with zero runtime cost.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-decorators — mini-project](mini-projects/08-decorators-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Decorators are syntactic sugar for function transformations: `@dec` equals `fn = dec(fn)`.
- Decorators with arguments need three nesting levels: config → decorator → wrapper.
- Always use `@functools.wraps(fn)` — it preserves metadata with zero runtime cost.
- Stacking order is bottom-up: `@a @b @c def f` means `a(b(c(f)))`. The outermost decorator's wrapper runs first.

## Further reading

- [PEP 318](https://peps.python.org/pep-0318/) — the original decorator proposal.
- Python docs: [`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps).
- Real Python: [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/).
- Next: [Sum types](09-sum-types.md).
