# Chapter 03 — Functions

> A function is the smallest reusable unit of logic you can name. Once you can write good functions, you can teach yourself any idea in this book.

## Learning objectives

By the end of this chapter you will be able to:

- Define a function with `def`, with zero or more parameters, and call it correctly.
- Distinguish *parameters* from *arguments*; positional from keyword; *returning* from *printing*.
- Use default values without falling into the mutable-default trap.
- Write a useful docstring and basic type hints.
- Compose small functions into larger ones without re-stating logic.

## Prerequisites & recap

You should already be comfortable with:

- [Variables](02-variables.md) — names, values, and assignment.
- Running a Python file from the terminal ([chapter 01](01-introduction.md)).

Recap from chapter 02: assignment binds a *name* to a *value*. A function is just another value, so `def greet(...)` creates a value (the function object) and binds it to the name `greet`.

## The simple version

A function is a **labelled box** that takes inputs, runs some steps, and gives back a result. You write the box once, then *call* it as many times as you want — each call gets fresh inputs and produces a fresh result.

Two crucial habits from day one: a function should usually **return** a value (not print it), and it should **do one thing**. If you can describe the function in a single sentence without saying "and", you've probably split it well.

## In plain terms (newbie lane)

This chapter is really about **Functions**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How a call moves through a function and back to the caller.

```
   Caller                       Function: full_name
   ──────                       ───────────────────
   x = full_name("Ada","Lovelace")
        │
        │  arguments  ──────▶   first = "Ada"
        │                       last  = "Lovelace"
        │                              │
        │                              ▼
        │                       return first + " " + last
        │                              │
        ◀───── return value ───────────┘
   x == "Ada Lovelace"
```

The arguments slide into the parameter slots; the body runs; the `return` value slides back out. Anything not returned is invisible to the caller.

## Must know now

- The chapter's core mental model and one working example.
- The most common beginner bug for this topic.
- Enough to finish the matching exercise L1 and L2 tasks.

## Can skip for now

- Advanced performance caveats.
- Rare edge cases and deep language internals.
- Optional tooling depth that is not needed for this chapter's checkpoint.

## Concept deep-dive

### Anatomy of a function

```python
def full_name(first: str, last: str) -> str:
    """Return 'First Last' with a single space separator."""
    return f"{first} {last}"
```

- `def` introduces a function.
- `full_name` is the function's name — a regular variable bound to the function object.
- `first`, `last` are **parameters** — placeholder names visible only inside the body.
- `: str` and `-> str` are **type hints**. Python ignores them at runtime, but your editor, linter, and future TypeScript brain will not.
- The triple-quoted string is the **docstring** — `help(full_name)` and IDE tooltips read it.
- `return` produces the function's output and ends the call.

When you call it:

```python
greeting = full_name("Ada", "Lovelace")
#                    └────arguments────┘
```

Parameters live in the *signature*; arguments live at the *call site*.

### Returning vs. printing

A **returning** function gives a value back. A **printing** function produces a side effect on the screen. They are not interchangeable.

```python
def square(n):
    return n * n

def shout(s):
    print(s.upper())

x = square(5) + 1   # x == 26 — return value is reusable
y = shout("hi")     # screen prints HI; y == None
```

Omitting `return` is the same as `return None`. You can still combine them — print *and* return — but defaulting to "return the result, let the caller decide what to print" keeps your functions reusable and testable.

**Why this matters:** code that prints inside business logic is hard to test (you can't `assert` a print), hard to repurpose (a web handler can't render a `print`), and hard to compose (you can't pass a `print` into another function and use the result). Return values are how functions cooperate.

### Positional and keyword arguments

```python
def discount(price, pct=10):
    return price * (1 - pct / 100)

discount(100)               # 90.0  — uses default pct=10
discount(100, 20)           # 80.0  — positional override
discount(price=100, pct=5)  # 95.0  — keyword, self-documenting
discount(pct=25, price=80)  # 60.0  — keyword order doesn't matter
```

Rule of thumb: pass by position when there are 1–2 parameters and the meaning is obvious; pass by keyword the moment a `bool` appears (`flush=True` reads better than `True`) or when the call would be ambiguous to a reader.

### Default values — and the mutable-default trap

Defaults are evaluated **once**, when the `def` line runs — not on each call. With immutable defaults (`int`, `str`, `None`) that's fine. With *mutable* defaults (`list`, `dict`, `set`) it's a bug factory:

```python
def add(item, bag=[]):       # ⚠ trap
    bag.append(item)
    return bag

add("x")   # ['x']
add("y")   # ['x', 'y']  — same list, persisted across calls
```

The fix is the **None-sentinel pattern**:

```python
def add(item, bag=None):
    if bag is None:
        bag = []
    bag.append(item)
    return bag
```

A fresh list is created on every call where the caller didn't supply one.

### Docstrings and type hints

A docstring is the function's contract; type hints are its shape.

```python
def clamp(value: float, low: float, high: float) -> float:
    """Return value bounded to [low, high].

    Raises ValueError if low > high.
    """
    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(value, high))
```

You don't need hints to *run*, but every team you'll join uses them. Habit-form early.

### Composition: small functions plug together

```python
def is_vowel(ch: str) -> bool:
    return ch.lower() in "aeiou"

def count_vowels(text: str) -> int:
    return sum(1 for ch in text if is_vowel(ch))
```

`count_vowels` is two lines because `is_vowel` exists. Splitting along nouns ("a vowel", "a count") rather than verbs ("loop and count") yields functions you'll reuse later.

## Why these design choices

- **Return over print, by default.** Returning is composable and testable; printing is a leaf operation. Pick printing only when the *purpose* of the function is the side effect (a CLI's `main`, a logger). When you need both, have the worker function return and a thin wrapper print the result.
- **Keyword arguments for booleans and >2 params.** They cost a few characters at the call site and save minutes of confusion three months from now. Most production codebases enforce this with linter rules.
- **`None` sentinel over mutable defaults.** The alternative — relying on `[]` "looking" fresh — silently shares state across calls. The `None` pattern is one extra line and removes a whole bug class.
- **Type hints, even when optional.** They double as machine-readable docs, power editor autocomplete, and let tools like `mypy` catch class mismatches before runtime. The cost is two characters per parameter; the payoff scales with the codebase.
- **Docstrings, even short ones.** A 1-line docstring sits where readers already look (the function header), unlike a comment buried 40 lines in. `help()`, Sphinx, and IDEs all surface it for free.
- **When you'd choose differently.** Hot loops where every microsecond matters sometimes inline rather than call (function calls in CPython cost ~100ns); CLI scripts where you don't need to test anything sometimes legitimately mix print into the worker. Both are exceptions, not defaults.

## Production-quality code

### Example 1 — A small, well-shaped utility module

```python
# pricing.py
"""Pricing helpers for the checkout flow."""

from typing import Iterable


def tax(amount: float, rate: float = 0.07) -> float:
    """Return the tax owed on `amount` at `rate` (e.g. 0.07 for 7%)."""
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be in [0, 1]")
    return amount * rate


def total(amount: float, rate: float = 0.07) -> float:
    """Return amount + tax(amount, rate)."""
    return amount + tax(amount, rate)


def cart_total(prices: Iterable[float], rate: float = 0.07) -> float:
    """Return the post-tax total of a sequence of line-item prices."""
    subtotal = sum(prices)
    return total(subtotal, rate)


if __name__ == "__main__":
    print(f"{cart_total([19.99, 4.50, 12.00]):.2f}")
```

Each function does one thing, validates inputs, and returns a value. The CLI runner is gated behind `if __name__ == "__main__"` so importing the module never prints.

### Example 2 — Composing instead of duplicating

```python
# text_stats.py
"""Tiny library for counting things in text."""

VOWELS = frozenset("aeiouAEIOU")


def is_vowel(ch: str) -> bool:
    """True iff ch is a single English vowel (any case)."""
    return ch in VOWELS


def count_where(text: str, predicate) -> int:
    """Count characters in text for which predicate(ch) is True."""
    return sum(1 for ch in text if predicate(ch))


def count_vowels(text: str) -> int:
    return count_where(text, is_vowel)


def count_digits(text: str) -> int:
    return count_where(text, str.isdigit)
```

Two domain-specific counters share one engine. Adding `count_uppercase` is a one-liner.

## Security notes

Functions are the boundary at which untrusted input first becomes structured data. Two habits that matter from day one:

- **Validate at the entry, not the exit.** If `tax(amount, rate)` is called with `rate=200`, the bug is in your validation. Raise early so the broken caller is the one in the stack trace.
- **Don't construct shells, SQL, or HTML by string concatenation inside helpers.** A function called `run_query(name)` that does `f"SELECT * FROM users WHERE name='{name}'"` is a SQL-injection oracle. Use the parameterized API of your library; we cover this seriously in [Module 11 — SQL](../11-sql/README.md).
- **Avoid logging secrets implicitly.** A function that "just returns a value" but also `print`s the value can leak API keys to CI logs. Returning over printing pays a security dividend too.

## Performance notes

- A Python function call costs roughly **50–200 nanoseconds** in CPython (interpreter dispatch, frame setup). For 99% of code this is invisible. For the inner loop of a numeric kernel, factoring out a one-line helper can measurably slow things down.
- **Defaults are evaluated once**, at definition time. Heavy expressions there (e.g. `def f(now=datetime.now())`) freeze a value at import — almost always a bug, occasionally a useful cache.
- **Type hints have zero runtime cost** in CPython — they're stored as metadata and never checked.
- **Recursion** is bounded by `sys.getrecursionlimit()` (default 1000). Algorithms that recurse on arbitrary user input need either an iterative form or an explicit `sys.setrecursionlimit`. We come back to this in [Module 05 — recursion](../05-fp/04-recursion.md).
- **Cost model:** writing more, smaller functions makes code slower than one huge function in micro-benchmarks; it makes systems faster in practice because you can replace, cache, or parallelize one piece at a time.

## Common mistakes

- **Forgetting `return`.** Symptom: the function "works" interactively but tests get `None`. Cause: missing `return` keyword (`a + b` computes and discards). Fix: read the body — every branch should either return or raise.
- **Mutable default argument.** Symptom: a list/dict mysteriously remembers values across calls. Cause: the default object is created once and reused. Fix: use the `None`-sentinel pattern.
- **Boolean-flag soup.** Symptom: calls like `do(data, fast=True, dry_run=False, verbose=True, retry=False)`. Cause: one function trying to be many. Fix: split into separate functions or accept a small config object.
- **Mixing return and print in one function.** Symptom: a CLI works but the same logic in a web handler renders garbage. Cause: business logic reaches for `print` instead of returning. Fix: a worker function that returns + a thin caller that prints.
- **Side effects hiding in "pure" names.** Symptom: `compute_total(cart)` also writes to a database. Cause: the name lies. Fix: rename to `compute_and_persist_total`, or split.
- **Too many parameters (>4).** Symptom: callers can never remember the order. Cause: the function does multiple things, or it should accept a dataclass. Fix: split, or pass a small object.

## Practice

1. **Warm-up.** Write `double(n)` that returns `n * 2`. Add a one-line docstring.
2. **Standard.** Write `celsius_to_fahrenheit(c: float) -> float` with a docstring and a sensible behaviour for `c < -273.15` (raise `ValueError`).
3. **Bug hunt.** Why does this print `None`? Fix it without changing the call site.

    ```python
    def add(a, b):
        a + b
    print(add(2, 3))
    ```

4. **Stretch.** Write `fmt_price(amount: float, currency: str = "USD") -> str` that returns `"USD 12.30"` with always-two decimals. Reject negative amounts.
5. **Stretch++.** Write `compose(f, g)` that returns a new function equivalent to `lambda x: f(g(x))`. Verify with `compose(square, double)(3) == 36`.

<details><summary>Show solutions</summary>

```python
def double(n):
    """Return n times two."""
    return n * 2


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit. Raises if below absolute zero."""
    if c < -273.15:
        raise ValueError("temperature below absolute zero")
    return c * 9 / 5 + 32
```

Bug: `a + b` computes a sum then discards it. Add `return`:

```python
def add(a, b):
    return a + b
```

```python
def fmt_price(amount: float, currency: str = "USD") -> str:
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return f"{currency} {amount:.2f}"


def compose(f, g):
    return lambda x: f(g(x))
```

</details>

## Quiz

1. A *parameter* is:
    (a) the value passed at a call (b) a name in the function's signature (c) a return statement (d) a keyword
2. `def f(): pass` evaluated as `f()` returns:
    (a) `None` (b) `0` (c) `""` (d) raises
3. Which calls are equivalent for `def f(a, b=1):`?
    (a) `f(2)`, `f(2, 1)`, `f(a=2, b=1)` (b) only `f(2, 1)` (c) none are equivalent (d) `f(1)` and `f(2)`
4. `def g(x=[]): x.append(1); return x`. What does `g()` return on its third call?
    (a) `[1]` (b) `[1, 1]` (c) `[1, 1, 1]` (d) error
5. `help(f)` displays:
    (a) the bytecode (b) the docstring (c) the source (d) the type

**Short answer:**

6. Define *parameter* vs. *argument* in one sentence each.
7. Why is an implicit `return None` considered risky in production code?

*Answers: 1-b, 2-a, 3-a, 4-c, 5-b.*

## Learn-by-doing mini-project

Use the single module project track and complete **Checkpoint B**:

- [Python Fundamentals Companion Track](mini-projects/00-python-fundamentals-companion-track.md)

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A function takes inputs (parameters), runs a body, and returns a value — exactly one.
- Prefer returning over printing; keyword arguments over positional flags.
- Mutable default arguments are evaluated once — use `None` and create fresh values inside.
- Small functions named after nouns compose into larger features without duplication.

## Further reading

- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/).
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/).
- Robert Martin, *Clean Code*, chapter 3 ("Functions").
- Next: [scope](04-scope.md).
