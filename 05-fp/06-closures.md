# Chapter 06 — Closures

> "A closure is a function that remembers the variables from the scope where it was created, even after that scope has ended."

## Learning objectives

By the end of this chapter you will be able to:

- Explain what closures capture and how `__closure__` works under the hood.
- Use closures to create private state without classes.
- Apply `nonlocal` to mutate captured variables — and know when not to.
- Avoid the late-binding loop-variable trap that surprises every Python developer once.

## Prerequisites & recap

- [Scope](../01-python/04-scope.md) — LEGB rule, local vs. enclosing vs. global.
- [First-class functions](02-first-class-functions.md) — functions as values, higher-order functions.

## The simple version

When you define a function inside another function, the inner function can use variables from the outer function — even after the outer function has returned. That inner function, together with the variables it "remembers," is called a *closure*.

Think of it like this: the outer function is a factory, and the inner function is a product that ships with some of the factory's settings baked in. The factory is gone, but the settings live on inside the product. Closures are how decorators, memoizers, and event systems work. They give you lightweight encapsulation — private state without needing a class.

## Visual flow

```
  make_adder(5) is called:
  +------------------------+
  | make_adder scope       |
  |   x = 5               |
  |                        |
  |   def add(y):          |
  |       return x + y  <--+-- captures x
  |                        |
  |   return add           |
  +------------------------+
        |
        v
  add5 = <closure>    # make_adder's scope is gone,
  add5(3) -> 8        # but x=5 lives on in add5.__closure__

  Late-binding trap:
  +------------------------------------+
  | fns = [lambda: i for i in range(3)]|
  |                                    |
  | All three lambdas share the SAME i |
  | After the loop, i = 2             |
  |                                    |
  | [f() for f in fns] -> [2, 2, 2]   |
  +------------------------------------+

  Fix: lambda i=i: i  (capture the VALUE, not the reference)

  Caption: Closures capture references to enclosing variables.
  The late-binding trap happens because all lambdas share one
  variable, which ends up with the loop's final value.
```

## Concept deep-dive

### What closures capture

When you define a function inside another function, the inner function can reference variables from the enclosing scope:

```python
def make_adder(x):
    def add(y):
        return x + y
    return add

add5 = make_adder(5)
add5(3)     # 8
```

`add` *closes over* `x`. After `make_adder` returns, its local scope is gone — but the reference to `x` survives inside `add.__closure__`:

```python
add5.__closure__          # (<cell at 0x...: int object at 0x...>,)
add5.__closure__[0].cell_contents   # 5
```

Python stores captured variables in *cell objects*. The closure holds references to these cells, not copies of the values. This distinction matters, as you'll see next.

### Closures capture references, not values

Because closures hold references to variables (not snapshots of their values), mutations to the variable are visible to the closure:

```python
def make_counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

c = make_counter()
c()   # 1
c()   # 2
c()   # 3
```

The `nonlocal` keyword tells Python: "when I assign to `n`, I mean the `n` from the enclosing scope — don't create a new local." Without `nonlocal`, `n += 1` would create a new local `n`, and you'd get an `UnboundLocalError` because Python sees the assignment and treats `n` as local before it's defined.

### The late-binding trap

This is the single most common closure gotcha in Python:

```python
fns = [lambda: i for i in range(3)]
[f() for f in fns]        # [2, 2, 2]   — NOT [0, 1, 2]
```

Why? All three lambdas capture the *same variable* `i`. They don't capture the *value* of `i` at the time the lambda was created. By the time you call them, the loop is done and `i == 2`.

**Fix: capture the value with a default argument:**

```python
fns = [lambda i=i: i for i in range(3)]
[f() for f in fns]        # [0, 1, 2]
```

The `i=i` creates a default parameter that snapshots the current value of `i` at definition time. It's ugly, but it's the standard Python idiom.

### Closures vs. classes

For encapsulated state, closures and classes are often interchangeable:

```python
# Closure version
def make_counter(start=0):
    n = start
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

# Class version
class Counter:
    def __init__(self, start=0):
        self.n = start
    def inc(self):
        self.n += 1
        return self.n
```

When should you use which?

- **Closures:** when you need one or two behaviors on private state. Lighter, less boilerplate.
- **Classes:** when you need multiple methods sharing state, inheritance, or a richer interface. Classes also make it easier to inspect and test state.

Use whichever reads clearer for the situation. Don't force one paradigm where the other is a better fit.

### What closures enable

Closures are the mechanism behind several important patterns:

- **Decorators** (chapter 08) — the wrapper function closes over the original function.
- **Memoization** — the cache dict lives in the closure.
- **Callbacks and event handlers** — the handler closes over the context it needs.
- **Factory functions** — `make_adder`, `make_logger`, `make_validator`.

Understanding closures is understanding how half of FP Python works under the hood.

## Why these design choices

**Why does Python capture by reference instead of by value?** Because Python variables are name bindings, not storage locations. A closure captures the *name*, and the name always refers to the current value. This is consistent with how all Python scoping works — it just surprises people in the loop-lambda case.

**Why require `nonlocal` for mutation?** To keep the scoping rules unambiguous. Without `nonlocal`, any assignment creates a local variable. This is the same reason you need `global` to assign to module-level variables. Explicit is better than implicit.

**When would you skip closures?** When the state is complex enough to warrant named attributes and methods. A closure with five `nonlocal` variables and three inner functions is harder to understand than a class with the same behavior. Closures are for lightweight encapsulation; classes are for heavyweight.

## Production-quality code

```python
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def make_counter(start: int = 0) -> Callable[[], int]:
    """Create a counter closure. Each call increments and returns the count."""
    n = start
    def inc() -> int:
        nonlocal n
        n += 1
        return n
    return inc


def once(fn: Callable[..., T]) -> Callable[..., T]:
    """Return a closure that calls fn only the first time, then returns cached result."""
    called = False
    result: T = None  # type: ignore[assignment]

    def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal called, result
        if not called:
            result = fn(*args, **kwargs)
            called = True
        return result
    return wrapper


def make_event_bus():
    """Event bus using closures for encapsulation. No classes needed."""
    subscribers: list[Callable] = []

    def subscribe(fn: Callable) -> None:
        subscribers.append(fn)

    def unsubscribe(fn: Callable) -> None:
        subscribers.remove(fn)

    def publish(event: Any) -> None:
        for fn in subscribers:
            fn(event)

    return subscribe, unsubscribe, publish


def memoize(fn: Callable[..., T]) -> Callable[..., T]:
    """Simple memoizer using a closure over a private cache dict."""
    cache: dict[tuple, T] = {}

    def wrapper(*args: Any) -> T:
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper


# --- Usage ---
counter = make_counter()
assert counter() == 1
assert counter() == 2

@once
def load_config():
    print("Loading...")  # only prints once
    return {"debug": True}

load_config()   # "Loading..."
load_config()   # (silent, returns cached {"debug": True})

subscribe, unsubscribe, publish = make_event_bus()
log = []
subscribe(log.append)
publish("hello")
assert log == ["hello"]
```

## Security notes

- **Closures can leak references to sensitive data:** If a closure captures a variable holding a password, API key, or token, that reference persists as long as the closure exists. Ensure closures don't outlive the intended lifecycle of sensitive data.
- **Unintended state sharing:** If two closures close over the same mutable variable, one can affect the other. In concurrent code, this creates race conditions.

## Performance notes

- **Closure creation:** Creating a closure is slightly more expensive than a plain function call because Python must create cell objects for captured variables. The overhead is ~50–100 ns — negligible unless you're creating millions of closures in a tight loop.
- **Variable lookup:** Accessing a closure variable is marginally slower than a local variable (cell dereference vs. direct stack access). In practice, this is unmeasurable for most code.
- **Memory:** Closures keep references to captured variables alive. If a closure captures a large object (e.g., a DataFrame), that object stays in memory for the closure's lifetime. Use `del` or `weakref` if this matters.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `[lambda: i for i in range(3)]` returns `[2, 2, 2]` | Late binding — all lambdas share the same `i`, which equals 2 after the loop | Use default argument to snapshot: `lambda i=i: i`. |
| 2 | `UnboundLocalError: local variable 'n' referenced before assignment` | Assigning to a captured variable without `nonlocal` — Python treats it as a new local | Add `nonlocal n` before the assignment inside the inner function. |
| 3 | Closure holds a large object in memory long after it's needed | The closure captures a reference to the object, preventing garbage collection | Capture only what you need (extract the field, not the whole object). Or set the variable to `None` when done. |
| 4 | Two closures interfere with each other's state | Both close over the same mutable variable (e.g., a shared list) from a common enclosing scope | Give each closure its own scope — create closures inside separate function calls. |

## Practice

**Warm-up.** Write `make_adder(x)` and verify `make_adder(5)(10) == 15`.

<details><summary>Solution</summary>

```python
def make_adder(x):
    def add(y):
        return x + y
    return add

add5 = make_adder(5)
assert add5(10) == 15
assert add5(0) == 5
```

</details>

**Standard.** Implement a counter closure with three operations: `get()`, `inc()`, and `reset()`.

<details><summary>Solution</summary>

```python
def make_counter(start=0):
    n = start

    def get():
        return n

    def inc():
        nonlocal n
        n += 1
        return n

    def reset():
        nonlocal n
        n = start
        return n

    return get, inc, reset

get, inc, reset = make_counter(0)
assert inc() == 1
assert inc() == 2
assert get() == 2
assert reset() == 0
assert get() == 0
```

</details>

**Bug hunt.** Fix this code so it returns `[0, 1, 2]` instead of `[2, 2, 2]`:

```python
fns = [lambda: i for i in range(3)]
print([f() for f in fns])
```

<details><summary>Solution</summary>

```python
fns = [lambda i=i: i for i in range(3)]
print([f() for f in fns])   # [0, 1, 2]
```

The `i=i` default argument captures the current value of `i` at definition time, rather than sharing a single reference to the loop variable.

</details>

**Stretch.** Write `once(fn)` — a closure that calls `fn` the first time and returns the cached result for every subsequent call.

<details><summary>Solution</summary>

```python
def once(fn):
    called = False
    result = None

    def wrapper(*args, **kwargs):
        nonlocal called, result
        if not called:
            result = fn(*args, **kwargs)
            called = True
        return result
    return wrapper

call_count = 0
@once
def expensive():
    global call_count
    call_count += 1
    return 42

assert expensive() == 42
assert expensive() == 42
assert call_count == 1
```

</details>

**Stretch++.** Implement `make_rate_limiter(limit, per_seconds)` as a closure that raises `RateLimitError` if called more than `limit` times within `per_seconds`.

<details><summary>Solution</summary>

```python
import time

class RateLimitError(Exception):
    pass

def make_rate_limiter(limit, per_seconds):
    calls = []

    def check():
        nonlocal calls
        now = time.monotonic()
        calls = [t for t in calls if now - t < per_seconds]
        if len(calls) >= limit:
            raise RateLimitError(
                f"Rate limit exceeded: {limit} calls per {per_seconds}s"
            )
        calls.append(now)

    return check

limiter = make_rate_limiter(3, 1.0)
limiter()   # ok
limiter()   # ok
limiter()   # ok
try:
    limiter()   # raises RateLimitError
except RateLimitError:
    print("Rate limited!")
```

</details>

## In plain terms (newbie lane)
If `Closures` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A closure:
    (a) Compiles to a class behind the scenes
    (b) Remembers variables from the scope where it was created
    (c) Can only access global variables
    (d) Only works at module level

2. Without `nonlocal`, assigning to a captured variable:
    (a) Modifies the outer variable
    (b) Creates a new local variable (and likely causes `UnboundLocalError`)
    (c) Raises `SyntaxError`
    (d) Copies the variable

3. Late binding in loop lambdas captures:
    (a) Values at definition time
    (b) References to variables, evaluated at call time
    (c) Types of the variables
    (d) Function signatures

4. Closures vs. classes for state:
    (a) Classes are always better
    (b) Interchangeable — pick based on readability and complexity
    (c) Closures are always faster
    (d) Classes require the GIL, closures don't

5. `once(fn)` should:
    (a) Call `fn` every time
    (b) Call `fn` the first time and return the cached result after
    (c) Store results in a database
    (d) Only work with async functions

**Short answer:**

6. Explain closures in one sentence.
7. Why does the late-binding trap usually surprise people?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b, 6. A closure is a function that retains access to variables from the enclosing scope where it was defined, even after that scope has ended. 7. People expect each lambda to capture the value of the loop variable at the time it's created, but Python captures the reference — all lambdas share the same variable, which has the loop's final value by the time they're called.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-closures — mini-project](mini-projects/06-closures-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Closures capture references to enclosing variables, not copies of their values. The captured variables live on in `__closure__` cells.
- Use `nonlocal` to rebind (mutate) a captured variable from within the closure.
- The late-binding trap (`[lambda: i for i in range(3)]`) bites because all lambdas share one variable. Fix with `lambda i=i: i`.
- Closures provide lightweight encapsulation — private state without classes. Use classes when the state or interface grows complex.

## Further reading

- Python docs: [Execution model — Naming and binding](https://docs.python.org/3/reference/executionmodel.html).
- Python docs: [`nonlocal` statement](https://docs.python.org/3/reference/simple_stmts.html#the-nonlocal-statement).
- Next: [Currying](07-currying.md).
