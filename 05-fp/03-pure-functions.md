# Chapter 03 — Pure Functions

> "A pure function is a mathematical function: given the same inputs, it produces the same output and has no observable side effects."

## Learning objectives

By the end of this chapter you will be able to:

- Define purity precisely and classify functions as pure or impure.
- Identify hidden side effects (mutation, I/O, randomness, time) in existing code.
- Refactor impure code using the "functional core, imperative shell" pattern.
- Explain why pure functions are easier to test, cache, and parallelize.

## Prerequisites & recap

- [First-class functions](02-first-class-functions.md) — higher-order functions, lambdas, generators.

## The simple version

A pure function is like a formula in a spreadsheet: you put values in, you get a result out, and nothing else happens. It doesn't read the clock, it doesn't print to the screen, it doesn't change any variable outside itself. Call it a million times with the same input and you'll always get the same output.

Why does this matter? Because pure functions are dead simple to test (no mocks, no setup), safe to cache (same input = same output, always), and safe to run in parallel (no shared mutable state). The trick is structuring your program so the *interesting logic* is pure and the *messy I/O* is pushed to the edges.

## Visual flow

```
  +------------------------------------------------------+
  |                   Your program                        |
  |                                                       |
  |   Impure shell              Pure core                 |
  |  +-------------+    +-------------------------+       |
  |  | read file   | -> | validate, transform,    | ---+  |
  |  | read stdin  |    | compute, filter, map    |    |  |
  |  | HTTP request|    | (no I/O, no mutation)   |    |  |
  |  +-------------+    +-------------------------+    |  |
  |                                                    v  |
  |                      +-------------+                  |
  |                      | write file  |                  |
  |                      | HTTP resp   |                  |
  |                      | print       |                  |
  |                      +-------------+                  |
  |                        Impure shell                   |
  +------------------------------------------------------+

  Caption: "Functional core, imperative shell." I/O lives at
  the edges; pure logic lives in the center.
```

## Concept deep-dive

### The two rules of purity

A function is pure if and only if:

1. **Deterministic:** same inputs → same output, every time.
2. **No side effects:** it doesn't mutate anything outside itself — no globals, no arguments, no disk, no network, no RNG, no clock, no stdout.

That's it. If a function satisfies both rules, it's pure.

### Spotting impurity

Impurity hides in common patterns. Here are the usual suspects:

```python
counter = 0
def tick():              # impure: mutates a global
    global counter
    counter += 1

def greet(name):         # impure: side effect (print)
    print(f"hi {name}")

import random
def shuffle(xs):         # impure: RNG + mutation
    random.shuffle(xs)

import time
def now():               # impure: depends on the clock
    return time.time()
```

Each of these breaks at least one of the two rules. `tick` mutates shared state. `greet` performs I/O. `shuffle` is non-deterministic *and* mutates its input. `now` depends on external state (the system clock).

### How to purify

You don't eliminate impurity — you *contain* it. Three techniques:

**Return new values instead of mutating:**

```python
def with_appended(xs, x):
    return [*xs, x]       # new list, original untouched
```

**Move randomness to arguments:**

```python
def shuffled(xs, rng):
    out = list(xs)
    rng.shuffle(out)
    return out
```

Now the function is deterministic *given the same `rng` state*. In tests, you pass a seeded `random.Random(42)` and get reproducible results.

**Move I/O to the edges — functional core, imperative shell:**

```python
def process(lines: list[str]) -> list[str]:
    """Pure: no I/O, no mutation."""
    return [s.strip().lower() for s in lines if s.strip()]

def main():
    lines = open("in.txt").read().splitlines()   # impure edge
    result = process(lines)                       # pure center
    open("out.txt", "w").write("\n".join(result))  # impure edge
```

The `process` function is trivially testable. `main` is three lines of glue code that does the dirty work. This separation is the single most practical FP pattern for backend code.

### Why purity pays off

- **Trivial tests:** `assert total([(10, 2), (5, 1)]) == 22.47` — no database, no mocks, no fixtures.
- **Safe concurrency:** No shared mutable state means no locks, no races.
- **Memoization:** A pure function can be cached safely with `@functools.cache`. You'd never cache `time.time()`.
- **Local reasoning:** The bug is in the function's inputs, not in some global that changed three modules away.

## Why these design choices

**Why not make everything pure?** Because programs need to *do things*: read files, serve HTTP, write to databases. These are inherently impure. The goal isn't to eliminate impurity — it's to *minimize and isolate* it.

**Why does Python make this hard?** Python doesn't enforce purity at the language level. There's no `IO` monad, no type-level tracking of effects. You rely on discipline and convention. This is fine for most codebases — you document which functions are pure, you test them easily, and you keep I/O at the edges.

**When would you skip purity?** For quick scripts, prototypes, or deeply I/O-bound code where every function is a database call. Don't thread pure wrappers around code that's *entirely* about side effects. Apply the pattern where it gives you leverage — the transformation layer between input and output.

## Production-quality code

```python
from functools import cache
from typing import Iterable, NamedTuple


class LineItem(NamedTuple):
    price: float
    quantity: int


def subtotal(items: Iterable[LineItem]) -> float:
    """Pure: sum of price * quantity for each item."""
    return sum(item.price * item.quantity for item in items)


def total(items: Iterable[LineItem], tax_rate: float = 0.07) -> float:
    """Pure: subtotal + tax, rounded to cents."""
    items = list(items)  # materialize once for reuse
    return round(subtotal(items) * (1 + tax_rate), 2)


@cache
def fib(n: int) -> int:
    """Pure + memoized: safe to cache because fib is deterministic."""
    if n < 0:
        raise ValueError(f"fib undefined for negative n: {n}")
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def process_lines(lines: Iterable[str]) -> list[str]:
    """Pure: strip, lowercase, remove blanks. No I/O."""
    return [s.strip().lower() for s in lines if s.strip()]


# --- Impure shell ---
def main():
    items = [LineItem(10.00, 2), LineItem(5.50, 1)]
    print(f"Total: ${total(items):.2f}")       # $27.29

    print(f"fib(30) = {fib(30)}")               # 832040

    with open("input.txt") as f:
        result = process_lines(f)
    with open("output.txt", "w") as f:
        f.write("\n".join(result))
```

## Security notes

- **Memoization and user input:** If you cache a pure function that operates on user-supplied data, ensure the cache doesn't grow unboundedly. Use `@functools.lru_cache(maxsize=...)` instead of `@cache` for functions exposed to external input. An attacker could send unique inputs to exhaust memory.
- **Injection through "pure" functions:** A function that builds SQL from its arguments may be technically pure (same input → same output, no side effects), but it can still produce SQL injection payloads. Purity doesn't imply safety — you still need parameterized queries.

## Performance notes

- **Pure functions enable memoization:** `@cache` turns O(2^n) naive Fibonacci into O(n) with zero algorithmic changes. This only works because the function is pure — caching an impure function produces stale or wrong results.
- **Immutable copies cost memory:** `[*xs, x]` allocates a new list every time. For tight loops with large lists, this matters. Use mutable accumulators internally when performance requires it — just don't expose mutation to callers.
- **`functools.cache` memory:** Unbounded cache grows forever. For production use, prefer `lru_cache(maxsize=1024)` or an external cache with TTL.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Function passes tests in isolation but fails in production | Hidden dependency on a global variable or environment variable | Make all dependencies explicit parameters. Grep for `global`, `os.environ`, and module-level mutable state. |
| 2 | `@cache` on `def now(): return time.time()` freezes the clock | Caching an impure function — it returns the same value forever | Only cache pure functions. If a function depends on time, RNG, or I/O, don't cache it. |
| 3 | `def add(item, bag): bag.append(item); return bag` mutates caller's list | Modifying a mutable argument is a side effect even if you return it | Return a new collection: `return [*bag, item]`. |
| 4 | Logging inside a "pure" function makes tests noisy | `print()` and `logging.info()` are side effects | Accept a logger as an optional parameter, or move logging to the caller. Keep the core function silent. |
| 5 | Pure function works but is 100x slower than the imperative version | Creating new lists/dicts at every step instead of mutating in place | Use internal mutation when needed (e.g., accumulator pattern), but keep the function's *interface* pure — accept immutable input, return new output. |

## Practice

**Warm-up.** Rewrite `sort_in_place(xs)` (which calls `xs.sort()`) as a pure `sorted_copy(xs)` that returns a new sorted list without modifying the original.

<details><summary>Solution</summary>

```python
def sorted_copy(xs):
    return sorted(xs)

original = [3, 1, 2]
result = sorted_copy(original)
assert result == [1, 2, 3]
assert original == [3, 1, 2]  # unchanged
```

</details>

**Standard.** You're given this impure script. Identify the impurities and extract a pure core:

```python
import json

data = json.load(open("users.json"))
adults = []
for user in data:
    if user["age"] >= 18:
        user["status"] = "verified"
        adults.append(user)
json.dump(adults, open("adults.json", "w"))
```

<details><summary>Solution</summary>

Impurities: (1) file I/O, (2) mutating input dicts (`user["status"] = ...`).

```python
import json

def verify_adults(users: list[dict]) -> list[dict]:
    """Pure: filter adults and add status. No mutation, no I/O."""
    return [
        {**user, "status": "verified"}
        for user in users
        if user["age"] >= 18
    ]

def main():
    data = json.load(open("users.json"))
    result = verify_adults(data)
    json.dump(result, open("adults.json", "w"))
```

</details>

**Bug hunt.** A colleague decorated `now()` with `@cache` and wonders why the timestamp never changes:

```python
from functools import cache
import time

@cache
def now():
    return time.time()
```

Explain the bug and the fix.

<details><summary>Solution</summary>

`time.time()` is impure — it depends on the system clock. `@cache` caches the first result and returns it forever. Fix: don't cache impure functions. Remove `@cache`, or redesign so the caller passes the timestamp in.

</details>

**Stretch.** Write a pure `running_total(xs)` that takes a list of numbers and returns the prefix sums: `running_total([1, 2, 3, 4])` → `[1, 3, 6, 10]`.

<details><summary>Solution</summary>

```python
from itertools import accumulate

def running_total(xs):
    return list(accumulate(xs))

assert running_total([1, 2, 3, 4]) == [1, 3, 6, 10]
assert running_total([]) == []
```

</details>

**Stretch++.** Split a Flask-style HTTP handler into a pure `handle(request_dict) -> response_dict` and an impure shell that reads the request and sends the response. Write tests for the pure handler without running a server.

<details><summary>Solution</summary>

```python
def handle(request: dict) -> dict:
    """Pure: maps request data to response data."""
    name = request.get("name", "").strip()
    if not name:
        return {"status": 400, "body": {"error": "name required"}}
    return {"status": 200, "body": {"greeting": f"Hello, {name}!"}}

# Impure shell (Flask)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/greet", methods=["POST"])
def greet():
    response = handle(request.get_json())
    return jsonify(response["body"]), response["status"]

# Tests — no server needed
def test_handle_valid():
    assert handle({"name": "Ada"}) == {
        "status": 200,
        "body": {"greeting": "Hello, Ada!"},
    }

def test_handle_missing_name():
    assert handle({})["status"] == 400
```

</details>

## In plain terms (newbie lane)
If `Pure Functions` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A pure function:
    (a) Prints to stdout
    (b) Is deterministic and has no side effects
    (c) Uses `random.random()`
    (d) Mutates its arguments

2. Which is impure?
    (a) `abs(-3)`
    (b) `time.time()`
    (c) `(1, 2)[0]`
    (d) `len([1, 2])`

3. Memoization (`@cache`) is safe for:
    (a) Any function
    (b) Pure functions only
    (c) Async functions only
    (d) Generators only

4. "Functional core, imperative shell" means:
    (a) Tests must be written functionally
    (b) Wrap pure logic in a thin I/O layer at the edges
    (c) Use a functional programming language
    (d) Prohibit classes entirely

5. Mutating an argument:
    (a) Preserves purity
    (b) Is a side effect — breaks purity
    (c) Is fine if you also return it
    (d) Is only impure for lists, not dicts

**Short answer:**

6. Why are pure functions easy to test?
7. Give one technique to make a randomness-dependent function pure.

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b, 6. Pure functions depend only on their inputs and produce no side effects, so you test them with simple assert statements — no mocks, no fixtures, no database, no teardown. 7. Pass the RNG as an argument (e.g., `random.Random(seed)`) so the function is deterministic given the same RNG state.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-pure-functions — mini-project](mini-projects/03-pure-functions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Pure = deterministic + no side effects. If a function satisfies both rules, it's pure.
- Push impurity to the edges of your program: read input at the top, write output at the bottom, keep everything in between pure.
- Pure functions are cheap to test, safe to cache with `@cache`, and safe to run in parallel.
- You don't eliminate impurity — you contain it. That's the "functional core, imperative shell" pattern.

## Further reading

- Gary Bernhardt, *Functional Core, Imperative Shell* — the talk that named this pattern.
- Python docs: [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache), [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache).
- Next: [Recursion](04-recursion.md).
