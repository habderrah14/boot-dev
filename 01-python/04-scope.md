# Chapter 04 — Scope

> Scope is the rulebook the interpreter uses to answer one question: when I see the name `x`, which `x` do I mean?

## Learning objectives

By the end of this chapter you will be able to:

- State Python's LEGB lookup rule and apply it to any snippet.
- Distinguish local, enclosing, global, and built-in scopes.
- Use `global` and `nonlocal` correctly — and know when *not* to.
- Spot and fix `UnboundLocalError`.
- Avoid shadowing built-ins.

## Prerequisites & recap

- [Functions](03-functions.md) — you know that a function call has its own body.
- [Variables](02-variables.md) — names point at values.

Recap: assignment binds a name in the *current scope*. Until now we treated "the file" as the only scope. Functions introduce a new one.

## The simple version

A **scope** is a region of code where a given name is looked up consistently. Python has four nested scopes — local, enclosing, global, built-in — and looks up names in that order, returning the first match.

When you write to a name *inside* a function, you create a local. When you read it, you walk outward until you find one. That single rule explains every "weird" name-lookup case in Python.

## In plain terms (newbie lane)

This chapter is really about **Scope**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The four scopes Python searches, in order, when you reference a name.

```
   ┌──────────────────────────────────────────────────────────┐
   │  Built-in scope: print, len, range, list, …              │
   │  ┌────────────────────────────────────────────────────┐  │
   │  │  Global scope: top-level of the current module     │  │
   │  │  ┌──────────────────────────────────────────────┐  │  │
   │  │  │  Enclosing scope: outer function (if any)    │  │  │
   │  │  │  ┌────────────────────────────────────────┐  │  │  │
   │  │  │  │  Local scope: current function body    │  │  │  │
   │  │  │  └────────────────────────────────────────┘  │  │  │
   │  │  └──────────────────────────────────────────────┘  │  │
   │  └────────────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────────────┘
                         L → E → G → B
                  search outward; first match wins
```

## Concept deep-dive

### LEGB

When you reference a name, Python searches four scopes in order:

1. **L**ocal — inside the current function.
2. **E**nclosing — any surrounding function(s), innermost first.
3. **G**lobal — the module (file) level.
4. **B**uilt-in — names like `print`, `len`, `range`.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)       # local
    inner()
    print(x)           # enclosing

outer()
print(x)               # global
```

### Assignment creates locals

Assigning to a name *anywhere* inside a function makes it local for the *whole* function body — even before the assignment line:

```python
x = 1

def f():
    print(x)   # ⚠ UnboundLocalError
    x = 2      # this line marked x local everywhere in f, including the print above
```

The fix depends on intent:

- *Read the global, don't write it:* remove the assignment.
- *Write the global:* declare `global x` at the top of `f`.
- *Use a fresh local:* rename to avoid confusion.

### `global` and `nonlocal`

```python
counter = 0

def tick():
    global counter         # write through to the module scope
    counter += 1
```

```python
def make_counter():
    n = 0                  # enclosing local
    def tick():
        nonlocal n         # write through to make_counter's scope
        n += 1
        return n
    return tick
```

`global` reaches all the way to module scope. `nonlocal` reaches to the *nearest enclosing function* that has the name. If neither exists, you get `SyntaxError`.

### Built-ins

The built-in scope holds names like `print`, `len`, `range`, `list`, `dict`, `id`, `type`. Inspect with `import builtins; dir(builtins)`. Reusing one of these as a variable name shadows the built-in for the rest of that scope:

```python
list = [1, 2]    # ← bug factory
list((3, 4))     # TypeError: 'list' object is not callable
```

**Why this matters:** the linter warning `redefining built-in 'list'` is one of the top sources of head-scratching bugs. Treat any squiggly under a name as a real signal.

## Why these design choices

- **LEGB instead of explicit declarations.** Python opted for "implicit local on assignment, search outward on read" to keep function definitions concise. The cost is surprises like `UnboundLocalError`; the benefit is no `var`/`let` ceremony.
- **`global` is verbose on purpose.** Writing to a global from inside a function is almost always a mistake; the explicit keyword forces you to confront it. When you're tempted to use `global`, you almost always want a return value or a class instead.
- **`nonlocal` exists to make closures useful.** Without it, you couldn't write a counter without a class. With it, you can encapsulate mutable state in a function — a poor man's object.
- **When you'd choose differently.** Languages like Rust and Java require explicit declarations and forbid implicit captures. Their compilers catch more lookup mistakes; Python catches them at runtime. Both are defensible designs; Python optimized for development speed.

## Production-quality code

### Example 1 — A counter closure

```python
"""Counters built with closures vs classes — same external behavior."""

from typing import Callable


def make_counter(start: int = 0) -> tuple[Callable[[], int], Callable[[], int]]:
    """Return (get, inc) closures sharing private mutable state."""
    n = start

    def get() -> int:
        return n

    def inc() -> int:
        nonlocal n
        n += 1
        return n

    return get, inc


if __name__ == "__main__":
    get, inc = make_counter()
    for _ in range(3):
        inc()
    print(get())   # 3
```

The state lives in `make_counter`'s scope. The two inner functions share it via closure.

### Example 2 — Why `global` is usually wrong

```python
"""Bad: hidden mutation; Good: explicit return value."""

# BAD
total = 0
def add_bad(n: int) -> None:
    global total
    total += n

# GOOD — pure function, caller decides where to store
def add_good(total: int, n: int) -> int:
    return total + n
```

The `BAD` version is impossible to test without resetting global state between cases. The `GOOD` version takes its inputs explicitly and returns its result — testable, parallelizable, and reusable.

## Security notes

- **Module-level mutable state** (a global `dict` or `list`) is shared across every request handled by the same process. In a web server, that's a data leak waiting to happen — one user's data ends up in another user's response. Always pass state explicitly through function arguments or a request-scoped container.
- **Don't bind secrets in nested closures and `return` them carelessly.** A returned closure keeps a reference to its enclosing variables; if you `return inc` and `inc` closes over a database password, that password is reachable from anyone who got `inc`.

## Performance notes

- **Local lookups are fast** — they're an array index into the function's local frame. Global and built-in lookups are dict lookups (still O(1), but with a higher constant factor). Hot loops sometimes alias built-ins as locals: `_len = len; for x in data: _len(x)` — micro-optimization, only used when profiling shows it matters.
- **Closures hold references** to their enclosing variables for the closure's lifetime. A long-lived closure over a giant list keeps that list in memory. Be intentional about what you capture.

## Common mistakes

- **`UnboundLocalError`.** Symptom: read-then-write inside a function fails on the read. Cause: Python sees a later assignment and marks the name local everywhere. Fix: declare `global`/`nonlocal`, or rename to a fresh local.
- **Accidental `global`.** Symptom: a function silently changes module state. Cause: writing through `global` instead of returning. Fix: refactor to take state as a parameter and return the new state.
- **Shadowing built-ins.** Symptom: `'X' object is not callable`. Cause: a variable named `list`, `dict`, `id`, `input`, `type`, etc. Fix: rename.
- **Closure over a loop variable.** Symptom: a list of lambdas all return the same value. Cause: each closure captures the *name* `i`, which by loop end equals the final value. Fix: bind via default argument: `lambda i=i: i`.

## Practice

1. **Warm-up.** What scope do function parameters live in? Justify in one sentence.
2. **Standard.** Predict the output without running, then verify:

    ```python
    x = 10
    def f():
        x = 20
    f()
    print(x)
    ```

3. **Bug hunt.** Fix the `UnboundLocalError`:

    ```python
    total = 0
    def add(n):
        total = total + n
    add(5)
    print(total)
    ```

4. **Stretch.** Implement `make_bank(start)` returning three closures: `balance()`, `deposit(n)`, `withdraw(n)`. Forbid negative balances by raising `ValueError`.
5. **Stretch++.** Re-implement `make_bank` without `nonlocal` by mutating a `dict`. Compare the two designs in a comment.

<details><summary>Show solutions</summary>

1. Local — parameters are pre-bound locals at function entry.
2. `10` — assignment inside `f` is local; the global `x` is untouched.
3. Either declare `global total` inside `add`, or (better) make `add` a pure function: `def add(total, n): return total + n`.
4. and 5.:

    ```python
    def make_bank(start: float):
        bal = start

        def balance(): return bal

        def deposit(n: float):
            nonlocal bal
            if n < 0:
                raise ValueError("deposit must be non-negative")
            bal += n

        def withdraw(n: float):
            nonlocal bal
            if n < 0 or n > bal:
                raise ValueError("invalid withdrawal")
            bal -= n

        return balance, deposit, withdraw
    ```

    Without `nonlocal`, hold state in a dict — mutation reaches through, no rebinding needed:

    ```python
    def make_bank(start):
        state = {"bal": start}
        def balance(): return state["bal"]
        def deposit(n):
            if n < 0: raise ValueError
            state["bal"] += n
        ...
    ```

</details>

## Quiz

1. LEGB stands for:
    (a) Long, Extended, Grouped, Broad (b) Local, Enclosing, Global, Built-in (c) Loop, Expression, Grammar, Binding (d) Lookup, Evaluate, Guard, Block
2. Inside a function, assigning to a name:
    (a) reads from enclosing scope (b) always affects the global (c) makes the name local for the whole function (d) is a syntax error
3. `global` lets you:
    (a) read a global (you already could) (b) *write* to a global from within a function (c) make a local visible to callers (d) reset the interpreter
4. Which is a bad name because it shadows a built-in?
    (a) `result` (b) `values` (c) `list` (d) `data`
5. The correct keyword to rebind an *enclosing* non-global variable is:
    (a) `global` (b) `nonlocal` (c) `outer` (d) `self`

**Short answer:**

6. In your own words, describe LEGB.
7. Why is shadowing a built-in typically a bug?

*Answers: 1-b, 2-c, 3-b, 4-c, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-scope — mini-project](mini-projects/04-scope-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Python resolves names with LEGB: Local → Enclosing → Global → Built-in.
- Assignment inside a function creates a local unless marked `global` or `nonlocal`.
- Closures + `nonlocal` give you mutable state without classes.
- Avoid `global`; pass state explicitly. Never shadow built-ins.

## Further reading

- Python docs — [*Execution model: Naming and binding*](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding).
- David Beazley, [*The Inner Workings of Python Closures*](https://dabeaz.com/) (talks).
- Next: [testing and debugging](05-testing-and-debugging.md).
