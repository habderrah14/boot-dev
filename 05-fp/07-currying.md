# Chapter 07 — Currying

> "Currying turns a function of many arguments into a chain of one-argument functions. Used tastefully, it makes composition cleaner."

## Learning objectives

By the end of this chapter you will be able to:

- Define currying and distinguish it clearly from partial application.
- Implement a `curry` decorator in Python.
- Recognize when currying genuinely improves composition — and when it's a cargo-cult import from other languages.
- Use `functools.partial` as the pragmatic Python alternative.

## Prerequisites & recap

- [Closures](06-closures.md) — captured variables, inner functions returning functions.
- [Function transformations](05-function-transformations.md) — `partial`, wrappers, composition.

## The simple version

Currying transforms a function that takes multiple arguments into a series of functions that each take one argument. If you have `add(a, b)`, currying turns it into `add(a)(b)` — calling `add(1)` returns a new function that waits for `b`.

This matters because single-argument functions compose beautifully. Instead of `lambda x: between(0, 120, x)`, you just write `between(0)(120)` and get a ready-made predicate. But here's the honest truth: Python isn't Haskell. Most of the time, `functools.partial` is clearer and more idiomatic. Currying is a tool worth understanding, but reach for it only when it genuinely simplifies your code.

## Visual flow

```
  Currying:
  f(a, b, c)  -->  f(a)(b)(c)

  add(1, 2, 3) = 6

  After currying:
  add(1)       --> returns fn waiting for (b, c)
  add(1)(2)    --> returns fn waiting for (c)
  add(1)(2)(3) --> returns 6

  Partial application (compare):
  f(a, b, c)  -->  f_a(b, c)

  partial(add, 1)    --> returns fn(b, c)
  partial(add, 1)(2, 3) --> 6

  +------+     +------+     +------+     +------+
  | f    | --> | f(a) | --> |f(a)(b)| --> | value|
  | a,b,c|     | b,c  |     | c    |     |  6   |
  +------+     +------+     +------+     +------+
   curry fills one argument at a time

  +------+     +------+     +------+
  | f    | --> | f_a  | --> | value|
  | a,b,c|     | b,c  |     |  6   |
  +------+     +------+     +------+
   partial fills any number of arguments at once

  Caption: Currying enforces one-at-a-time application.
  Partial application is more flexible — fill any prefix.
```

## Concept deep-dive

### Currying vs. partial application

These two concepts are often confused. Here's the precise difference:

- **Currying** transforms `f(a, b, c)` into `f(a)(b)(c)`. Each call accepts exactly one argument and returns a new function until all arguments are supplied.
- **Partial application** fixes some arguments and returns a function expecting the rest. `partial(f, 1)` gives you `f_1(b, c)` — you fill the remaining args in one call.

In Haskell, every function is automatically curried. `add 1 2` is actually `(add 1) 2` — `add 1` returns a function. Python does *not* curry by default. You have to opt in.

### Implementing `curry` in Python

```python
def curry(fn, arity=None):
    if arity is None:
        arity = fn.__code__.co_argcount

    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*args, *more)

    return curried
```

How this works:

1. It inspects `fn` to determine how many arguments it needs (the *arity*).
2. Each call checks if enough arguments have accumulated.
3. If yes, it calls the original function. If no, it returns a new function that waits for more.

```python
@curry
def add3(a, b, c):
    return a + b + c

add3(1)(2)(3)    # 6
add3(1, 2)(3)    # 6 — also works with multiple args at once
add3(1, 2, 3)    # 6 — pass all at once
```

### Why bother with currying?

Curried functions compose naturally. You can "partially configure" them by passing one argument at a time:

```python
@curry
def between(lo, hi, x):
    return lo <= x <= hi

is_valid_age = between(0, 120)
valid_ages = list(filter(is_valid_age, ages))
```

Compare with `partial`:

```python
from functools import partial

is_valid_age = partial(between, 0, 120)
```

For this two-step usage, `partial` is arguably clearer — it's explicit about what it does and doesn't require a special decorator. Currying shines when you genuinely want to pre-apply one argument at a time across different call sites, or when building point-free pipelines.

### When currying is the wrong choice

Python isn't designed around currying. Several things work against it:

- **`*args` and `**kwargs`:** Variadic functions have no fixed arity. `curry(print)` fails because `print.__code__.co_argcount` is 0.
- **Tracebacks:** Curried functions create intermediate closures. Errors show a stack of anonymous functions instead of clear names.
- **Readability:** `between(0)(120)(age)` isn't more readable than `between(0, 120, age)` to most Python developers.

Don't curry for its own sake. If `partial` or a simple `lambda` is clearer, use that.

### Library support

- **`toolz.curry`** — a robust, battle-tested curry decorator from the `toolz` library. Handles edge cases better than a hand-rolled version.
- **`functools.partial`** — for most practical needs in idiomatic Python.

## Why these design choices

**Why isn't Python curried by default?** Because Python's design philosophy favors explicit function calls. `f(a, b, c)` is clear. `f(a)(b)(c)` requires the reader to know that `f` is curried. Python also supports `*args`, `**kwargs`, and default arguments, which all complicate automatic currying.

**When is currying genuinely useful in Python?** When you're building a library of composable predicates or transformations that are meant to be partially applied one argument at a time. Think DSLs for validation, query building, or data pipeline configuration.

**When should you use `partial` instead?** Almost always. `partial` is built-in, explicit, and doesn't require modifying the original function. It works with any callable, including C-level functions. Use currying only when the one-at-a-time pattern is central to your API design.

## Production-quality code

```python
import functools
import inspect
from typing import Any, Callable


def curry(fn: Callable, arity: int | None = None) -> Callable:
    """Curry a function so it can be called one argument at a time.

    Pass arity explicitly for variadic functions (*args/**kwargs).
    """
    if arity is None:
        try:
            sig = inspect.signature(fn)
            arity = sum(
                1 for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            )
        except (ValueError, TypeError):
            raise TypeError(
                f"Cannot determine arity of {fn!r}. Pass arity explicitly."
            )
    if arity < 1:
        raise ValueError(f"arity must be >= 1, got {arity}")

    @functools.wraps(fn)
    def curried(*args: Any) -> Any:
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*args, *more)

    return curried


def uncurry(fn: Callable, arity: int) -> Callable:
    """Reverse currying: turn f(a)(b)(c) back into f(a, b, c)."""
    def uncurried(*args: Any) -> Any:
        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, got {len(args)}")
        result = fn
        for arg in args:
            result = result(arg)
        return result
    return uncurried


# --- Usage ---
@curry
def by_key(key: str, value: Any, row: dict) -> bool:
    return row.get(key) == value

is_admin = by_key("role", "admin")
is_active = by_key("status", "active")

rows = [
    {"name": "Ada", "role": "admin", "status": "active"},
    {"name": "Bob", "role": "user", "status": "active"},
    {"name": "Eve", "role": "admin", "status": "inactive"},
]

admins = list(filter(is_admin, rows))
assert len(admins) == 2
assert all(r["role"] == "admin" for r in admins)

active_admins = list(filter(lambda r: is_admin(r) and is_active(r), rows))
assert len(active_admins) == 1


@curry
def multiply(a: int, b: int) -> int:
    return a * b

def pipe(x, *fns):
    for f in fns:
        x = f(x)
    return x

result = pipe(5, multiply(2), multiply(3))
assert result == 30   # 5 * 2 = 10, 10 * 3 = 30
```

## Security notes

N/A — currying is a function-composition technique with no direct security implications. The usual caveats about not executing untrusted callables apply.

## Performance notes

- **Curried call overhead:** Each curried invocation step creates a new closure. `f(a)(b)(c)` involves three function calls and two closure creations, versus one call for `f(a, b, c)`. Overhead is ~100–200 ns per step.
- **Arity detection:** `inspect.signature()` is relatively expensive (~1 µs). The `curry` decorator pays this cost once at decoration time, not on every call.
- **Deep curry chains:** A 10-argument curried function creates 9 intermediate closures. For hot paths, this is measurable. For configuration-time or request-level use, it's negligible.
- **`toolz.curry` vs. hand-rolled:** `toolz.curry` is optimized in C (via `cytoolz`) and handles edge cases. Prefer it for production use over a hand-rolled version.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `curry(print)` raises `TypeError` or behaves strangely | `print` is variadic (`*args`); automatic arity detection gives 0 | Pass `arity` explicitly: `curry(print, arity=1)`. |
| 2 | Curried function returns a function instead of a value | Not enough arguments supplied — the curried function is still waiting | Check that you've supplied all required arguments. Use `arity` to verify. |
| 3 | Currying makes code less readable, not more | Forcing currying where `partial` or a direct call is clearer | Use currying only when one-at-a-time application genuinely simplifies composition. Default to `partial`. |
| 4 | Confusing currying with partial application | Using the terms interchangeably | Currying: `f(a)(b)(c)` — one at a time. Partial: `f_a(b, c)` — fill any prefix. |

## Practice

**Warm-up.** Curry `add(a, b)` manually (without the `curry` decorator). Verify `add(1)(2) == 3`.

<details><summary>Solution</summary>

```python
def add(a):
    def inner(b):
        return a + b
    return inner

assert add(1)(2) == 3
assert add(10)(20) == 30
```

</details>

**Standard.** Use the `curry` decorator from this chapter to implement `between(lo, hi, x)` and filter a list of ages.

<details><summary>Solution</summary>

```python
@curry
def between(lo, hi, x):
    return lo <= x <= hi

is_valid_age = between(0, 120)
ages = [15, -3, 45, 200, 99, 0, 121]
valid = list(filter(is_valid_age, ages))
assert valid == [15, 45, 99, 0]
```

</details>

**Bug hunt.** `curry(print)` misbehaves — it calls `print` immediately without arguments. Why?

<details><summary>Solution</summary>

`print` accepts `*args`, so `co_argcount` (or `inspect.signature` required params) is 0. The curry decorator thinks zero arguments are needed and calls `print()` immediately. Fix: pass `arity` explicitly — `curry(print, arity=1)`.

</details>

**Stretch.** Implement `uncurry(fn, n)` that takes a curried function `f(a)(b)(c)` and returns a regular `f(a, b, c)`.

<details><summary>Solution</summary>

```python
def uncurry(fn, n):
    def uncurried(*args):
        if len(args) != n:
            raise TypeError(f"Expected {n} args, got {len(args)}")
        result = fn
        for arg in args:
            result = result(arg)
        return result
    return uncurried

curried_add = curry(lambda a, b, c: a + b + c)
normal_add = uncurry(curried_add, 3)
assert normal_add(1, 2, 3) == 6
```

</details>

**Stretch++.** Install `toolz` and use `toolz.curry` to define a pipeline of curried transforms. Compare code clarity with the equivalent `partial` version.

<details><summary>Solution</summary>

```python
from toolz import curry, pipe

@curry
def multiply(factor, x):
    return x * factor

@curry
def add(offset, x):
    return x + offset

@curry
def clamp(lo, hi, x):
    return max(lo, min(hi, x))

result = pipe(5, multiply(3), add(10), clamp(0, 20))
assert result == 20   # 5*3=15, 15+10=25, clamp(0,20,25)=20

# Equivalent with partial:
from functools import partial

def multiply_p(factor, x): return factor * x
def add_p(offset, x): return offset + x
def clamp_p(lo, hi, x): return max(lo, min(hi, x))

result_p = clamp_p(0, 20, add_p(10, multiply_p(3, 5)))
assert result_p == 20
```

</details>

## In plain terms (newbie lane)
If `Currying` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Currying transforms `f(a, b, c)` into:
    (a) `f(a)(b)(c)` — a chain of single-argument functions
    (b) `f(a, b, c)` — no change
    (c) `f(c, b, a)` — reversed arguments
    (d) `f()` called repeatedly

2. Partial application vs. currying:
    (a) They're identical
    (b) Partial pre-fills some args at once; currying enforces one-by-one
    (c) Partial is always faster
    (d) Currying returns a tuple

3. `functools.partial`:
    (a) Implements full currying
    (b) Implements partial application
    (c) Requires classes
    (d) Is deprecated

4. Python curries functions by default:
    (a) Yes
    (b) No
    (c) Only for lambdas
    (d) Only with the `toolz` library

5. Currying helps most with:
    (a) Class design
    (b) Composition and "pre-apply one arg at a time" patterns
    (c) Async programming
    (d) Generator pipelines

**Short answer:**

6. When is `partial` clearer than a curried version?
7. Why is currying rare in idiomatic Python?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b, 6. When you want to pre-fill two or more arguments at once — partial(f, a, b) is more explicit than f(a)(b) and doesn't require the function to be curried. Partial also works with any callable, including C builtins. 7. Python's calling convention (explicit args, *args, **kwargs, defaults) doesn't map cleanly to currying. The ecosystem uses partial, closures, and plain function calls. Currying adds syntactic overhead without enough payoff for most Python code.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-currying — mini-project](mini-projects/07-currying-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Currying transforms `f(a, b, c)` into `f(a)(b)(c)` — each call fills one argument and returns a function.
- Partial application (`functools.partial`) fills any number of arguments at once — it's Python's practical default.
- Currying enables clean one-at-a-time composition, but Python's calling conventions make it less natural than in Haskell or ML.
- Reach for currying when it genuinely clarifies your API; default to `partial` otherwise.

## Further reading

- [`toolz` documentation](https://toolz.readthedocs.io/) — robust currying and functional utilities for Python.
- Haskell wiki: [Currying](https://wiki.haskell.org/Currying) — to see where the idea comes from and where it shines.
- Next: [Decorators](08-decorators.md).
