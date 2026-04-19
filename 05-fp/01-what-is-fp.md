# Chapter 01 — What is Functional Programming?

> "FP is a discipline of thought: prefer values to variables, expressions to statements, and functions to methods."

## Learning objectives

By the end of this chapter you will be able to:

- Contrast imperative and functional programming styles with concrete examples.
- List the four core FP habits: immutability, purity, first-class functions, composition.
- Explain where Python sits on the imperative–functional spectrum and why that matters.
- Articulate the backend-specific payoffs of adopting FP habits.

## Prerequisites & recap

- [Python basics](../01-python/README.md) — variables, loops, functions, data structures.
- [OOP fundamentals](../04-oop/README.md) — enough to compare paradigms.

## The simple version

Functional programming is a way of thinking about code where you describe *what* the result should be rather than *how* to get there step by step. Instead of mutating variables in loops, you pass data through small, predictable functions that each do one thing. Each function takes input, returns output, and touches nothing else — no globals, no hidden state, no surprise side effects.

You don't need a special language. Python gives you most of the tools — comprehensions, generators, first-class functions, `functools` — so you can write in a functional style whenever it makes your code simpler, safer, and easier to test.

## Visual flow

```
  Imperative                         Functional
  ----------                         ----------
  total = 0                          total = sum(nums)
  for n in nums:                        ^
      total += n                        |
      ^                             one expression,
      |                             no mutation
  step-by-step mutation
  of a variable

  +---------+    +---------+    +---------+
  |   f1    | -> |   f2    | -> |   f3    | -> result
  +---------+    +---------+    +---------+
     strip          lower       replace(" ","-")

  Caption: FP chains small, pure transformations into a pipeline.
  Each box is a function; data flows left to right.
```

## Concept deep-dive

### Imperative vs. functional — the core split

When you write imperative code, you tell the computer *how* to do something. You create a variable, loop through data, and mutate that variable on every pass:

```python
total = 0
for n in nums:
    total += n
```

When you write functional code, you describe *what* the result is:

```python
total = sum(nums)
```

Both are valid Python. The functional version is shorter, harder to get wrong, and communicates intent directly. That doesn't mean loops are evil — sometimes a loop is the clearest option. FP is about reaching for the declarative style *first* and falling back to imperative when it genuinely helps readability.

### The four habits

Every functional style revolves around four habits. You don't need all four at once — each one pays off independently.

1. **Immutability.** Values don't change; you create new values instead. When nothing mutates, you never chase a bug caused by "who changed this variable?" Immutable data is also safe to share across threads without locks.

2. **Purity.** A function's output depends only on its inputs, and it produces no side effects — no writing to disk, no printing, no touching globals. Pure functions are trivially testable: `assert double(3) == 6`. No mocks, no fixtures, no teardown.

3. **First-class functions.** Functions are values. You can pass them as arguments, return them from other functions, and store them in lists or dicts. This is the foundation that makes composition, callbacks, and decorators possible.

4. **Composition.** Build complex behavior by snapping small functions together like Lego bricks. Instead of one 200-line function, you get a pipeline of five 10-line functions, each independently testable.

### Where Python sits on the spectrum

Languages live on a spectrum. Haskell sits at "mostly pure" — side effects are tracked in the type system. Clojure is "data-first, pragmatic" — immutable by default but practical about I/O. Python is a multi-paradigm language with FP-friendly features:

- List/dict/set comprehensions and generator expressions.
- `map`, `filter`, `functools.reduce`.
- First-class functions and closures.
- `functools` (partial, cache, wraps) and `itertools`.
- `match/case` for pattern matching (3.10+).

You get *most* of the benefits without fighting the language. The trick is knowing which FP tool to reach for and when to stop.

### Why FP matters for backend work

Backend systems have specific pain points that FP habits directly address:

- **Testability.** Pure functions need no database connection, no mock server, no test fixtures. Input in, output out, assert.
- **Concurrency safety.** Immutable data can be shared across threads and async tasks without locks or races.
- **Data pipelines.** ETL, log processing, request validation — these are naturally expressed as composed pipelines of small transforms.
- **Debugging.** When functions don't depend on hidden state, bugs are local. The cause is in the function's inputs, not in some global that changed three modules away.

## Why these design choices

**Why not go all-in on FP in Python?** Because Python is imperative at heart. It has mutable default arguments, `for` loops that rebind variables, no tail-call optimization, and I/O baked into the standard library. Fighting the language's grain makes code harder to read for the next developer.

**When would you pick a different approach?** If your domain is heavily stateful — GUI event loops, database ORMs, game engines — OOP or imperative styles may map more naturally to the problem. FP shines in the *transformation layer*: the code between "receive input" and "produce output."

**The pragmatic middle ground:** Use FP to shrink and isolate your impure, stateful code. Keep side effects (I/O, logging, database calls) at the edges. Make the core logic pure and composable. This is the "functional core, imperative shell" pattern, and it works beautifully in Python.

## Production-quality code

```python
from functools import reduce
from typing import Callable, Sequence


def pipe(*fns: Callable) -> Callable:
    """Left-to-right function composition.

    Each function receives the output of the previous one.
    Raises TypeError early if any argument isn't callable.
    """
    if not fns:
        raise TypeError("pipe requires at least one function")
    for i, f in enumerate(fns):
        if not callable(f):
            raise TypeError(f"Argument {i} is not callable: {f!r}")

    def piped(x):
        return reduce(lambda acc, f: f(acc), fns, x)

    return piped


def uppercase_names(users: Sequence[dict]) -> list[str]:
    """Extract and uppercase user names — pure, no mutation."""
    return [u["name"].upper() for u in users]


# --- Usage ---
sanitize = pipe(str.strip, str.lower, lambda s: s.replace(" ", "-"))
assert sanitize("  Hello World  ") == "hello-world"

users = [{"name": "Ada"}, {"name": "Alan"}]
assert uppercase_names(users) == ["ADA", "ALAN"]
```

## Security notes

N/A — this chapter covers programming paradigms, not security-sensitive operations. Security implications of specific FP techniques (e.g., memoization cache poisoning) are covered in later chapters where they apply.

## Performance notes

- **Comprehensions vs. loops:** CPython optimizes list comprehensions into tighter bytecode than equivalent `for`-`append` loops. Expect a small but consistent speedup — typically 10–30% for simple transforms.
- **`sum()` vs. manual accumulation:** Built-in `sum()` runs in C and is faster than a Python-level loop.
- **`pipe`/`compose` overhead:** Each function call in the pipeline adds Python call overhead (~50–100 ns per call in CPython 3.12). For hot inner loops this matters; for request-level pipelines it's negligible.
- **Memory:** Comprehensions build the full list in memory. For large datasets, switch to generator expressions: `(x.upper() for x in names)`.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Code is unreadable despite being "functional" | Forcing FP everywhere — 5-deep nested `map`/`filter`/`lambda` chains | Use a loop or comprehension when it reads more clearly. FP is a tool, not a religion. |
| 2 | Pipeline silently produces wrong results | One function in the chain returns `None` instead of a value | Ensure every function in a pipeline explicitly returns a value. Add type hints. |
| 3 | `lst.sort()` in a "pure" pipeline mutates the input | Confusing mutating methods (`.sort()`, `.append()`) with non-mutating functions (`sorted()`, `[*xs, x]`) | Use `sorted(lst)` instead of `lst.sort()`. Prefer functions that return new values. |
| 4 | "FP code is slow" on benchmarks | Building intermediate lists at every step instead of using generators | Chain generator expressions or use `itertools` for lazy evaluation. Only materialize at the end. |

## Practice

**Warm-up.** Rewrite this for-append loop as a list comprehension:

```python
out = []
for s in strings:
    out.append(s.strip().lower())
```

<details><summary>Solution</summary>

```python
out = [s.strip().lower() for s in strings]
```

</details>

**Standard.** Write `compose2(f, g)` that returns a function computing `f(g(x))`.

<details><summary>Solution</summary>

```python
def compose2(f, g):
    def composed(x):
        return f(g(x))
    return composed

shout = compose2(str.upper, str.strip)
assert shout("  hello  ") == "HELLO"
```

</details>

**Bug hunt.** A colleague wrote this and claims it's functional:

```python
def add_tag(items, tag):
    for item in items:
        item["tags"].append(tag)
    return items
```

What's wrong, and how would you fix it?

<details><summary>Solution</summary>

It mutates the input dicts in place — a side effect. The caller's data is changed. A functional version creates new dicts:

```python
def add_tag(items, tag):
    return [{**item, "tags": [*item["tags"], tag]} for item in items]
```

</details>

**Stretch.** Use `pipe` from this chapter to build a URL sanitizer that: strips whitespace, lowercases, replaces spaces with hyphens, and removes non-alphanumeric characters (except hyphens).

<details><summary>Solution</summary>

```python
import re

sanitize_url = pipe(
    str.strip,
    str.lower,
    lambda s: s.replace(" ", "-"),
    lambda s: re.sub(r"[^a-z0-9\-]", "", s),
)

assert sanitize_url("  My Cool Page!  ") == "my-cool-page"
```

</details>

**Stretch++.** Take a small imperative script you've written before (or invent one that processes a list of dicts) and rewrite it in FP style: pure functions composed into a pipeline, side effects only at the edges. Compare line count, testability, and readability.

<details><summary>Hint</summary>

Structure your rewrite as:
1. A series of small pure functions (`clean`, `validate`, `transform`).
2. A `pipe(clean, validate, transform)` composition.
3. A `main()` that handles I/O and calls the pipeline.

</details>

## In plain terms (newbie lane)
If `What Is Fp` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A pure function:
    (a) Returns different outputs for the same inputs
    (b) Returns the same output for the same inputs and has no side effects
    (c) Always returns `None`
    (d) Must be a lambda

2. First-class functions can be:
    (a) Returned from other functions only
    (b) Passed as arguments only
    (c) Stored in data structures only
    (d) All of the above — passed, returned, and stored

3. `list.sort()` is:
    (a) Pure — it sorts the list
    (b) Impure — it mutates the list in place and returns `None`
    (c) Functional — it returns a sorted list
    (d) Immutable

4. `sum(xs)` is an example of:
    (a) Imperative style
    (b) Declarative/functional style
    (c) Object-oriented style
    (d) Non-deterministic computation

5. FP in Python is:
    (a) Impossible — Python is imperative
    (b) Fully supported — Python is a functional language
    (c) Partial — Python supports most FP features pragmatically
    (d) Deprecated since 3.0

**Short answer:**

6. Give one concrete backend benefit of writing pure functions.
7. Why isn't Python considered a pure-FP language?

*Answers: 1-b, 2-d, 3-b, 4-b, 5-c, 6. Pure functions are trivially testable — no mocks, no database, no fixtures needed. (Also accept: safe concurrency, easy caching, local reasoning.) 7. Python allows unrestricted mutation, has no referential transparency enforcement, doesn't track side effects in the type system, and deliberately omits tail-call optimization.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-what-is-fp — mini-project](mini-projects/01-what-is-fp-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- FP = immutability + purity + first-class functions + composition. Each habit pays off independently.
- Python supports FP pragmatically — use comprehensions, generators, `functools`, and pure functions where they simplify your code.
- Use FP to shrink and isolate side-effectful code: pure core, impure edges.
- FP habits make backend code easier to test, safer to parallelize, and simpler to debug.

## Further reading

- *Functional Python Programming* by Steven Lott — comprehensive FP-in-Python guide.
- Gary Bernhardt, *Functional Core, Imperative Shell* — the architecture pattern that makes FP practical in any language.
- Python docs: [`functools`](https://docs.python.org/3/library/functools.html), [`itertools`](https://docs.python.org/3/library/itertools.html).
- Next: [First-class functions](02-first-class-functions.md).
