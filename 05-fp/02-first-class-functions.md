# Chapter 02 — First-Class Functions

> "In Python, a function is a value. Everything interesting in FP follows from that single fact."

## Learning objectives

By the end of this chapter you will be able to:

- Explain what "first-class" means and demonstrate passing functions as arguments, returning them, and storing them in data structures.
- Use `map`, `filter`, and `reduce` — and know when comprehensions are better.
- Write `lambda` expressions for short callbacks; articulate when `def` is the right choice.
- Build lazy pipelines with generators for constant-memory data processing.

## Prerequisites & recap

- [Functions](../01-python/03-functions.md) — defining, calling, `*args`/`**kwargs`.
- [What is FP](01-what-is-fp.md) — the four habits.

## The simple version

In most languages, numbers, strings, and lists are values — you can store them in variables, pass them to functions, and return them. In Python, functions are values too. You can assign a function to a variable, put functions in a list, pass a function as an argument to another function, and return a function from a function. That's what "first-class" means: functions aren't special — they're just another kind of object.

This one idea unlocks everything else in functional programming. Higher-order functions, decorators, callbacks, lazy pipelines — they all rely on the fact that a function is a value you can hand around like any other.

## Visual flow

```
  Functions are values — you can do anything with them:

  +-----------+     +-----------+     +-----------+
  | greet     |     | str.upper |     | len       |
  | (function)|     | (function)|     | (function)|
  +-----+-----+     +-----+-----+     +-----+-----+
        |                 |                 |
        v                 v                 v
  fns = [greet,      str.upper,         len]
                          |
                    for fn in fns:
                        fn("Ada")

  map / filter / reduce:

  source --> [ map(f) ] --> [ filter(p) ] --> [ reduce(g) ] --> result
     lazy        lazy           lazy             eager

  Caption: Data flows through higher-order functions.
  map and filter are lazy (iterators); reduce eagerly computes a final value.
```

## Concept deep-dive

### Functions are objects

When you write `def greet(name): ...`, Python creates a function *object* and binds it to the name `greet`. That object has attributes, a type, and can be referenced just like any other value:

```python
def greet(name):
    return f"hi {name}"

g = greet                     # bind to a new name — no parentheses
fns = [greet, str.upper, len] # store in a list
for fn in fns:
    print(fn("Ada"))          # hi Ada, ADA, 3
```

Why does this matter? Because it means you can write functions that *accept* functions as arguments or *return* new functions. These are called **higher-order functions**, and they're the backbone of FP.

You can inspect function objects too: `greet.__name__` gives `"greet"`, `greet.__doc__` gives the docstring, and `callable(greet)` returns `True`.

### `map`, `filter`, `reduce` — the classic trio

These three higher-order functions show up in almost every FP language:

```python
nums = [1, 2, 3, 4, 5]

squares = list(map(lambda n: n * n, nums))       # [1, 4, 9, 16, 25]
evens   = list(filter(lambda n: n % 2 == 0, nums)) # [2, 4]

from functools import reduce
total = reduce(lambda a, b: a + b, nums, 0)       # 15
```

`map` applies a function to every element. `filter` keeps elements where the predicate returns `True`. `reduce` folds the sequence down to a single value.

**But in Python, comprehensions are usually clearer:**

```python
squares = [n * n for n in nums]
evens   = [n for n in nums if n % 2 == 0]
total   = sum(nums)
```

Why do Pythonistas prefer comprehensions? Because they're more readable, they don't need `lambda`, and Guido van Rossum nearly removed `map`/`filter` from the language in Python 3 for that reason. Use the classic trio when you already have a named function to pass — `map(str.strip, lines)` reads nicely. Use comprehensions when you'd need a `lambda`.

`reduce` stays useful for genuine folds where no built-in exists — for example, flattening nested structures or accumulating complex results.

### `lambda` — anonymous functions

A `lambda` is a one-expression function with no name:

```python
add = lambda a, b: a + b    # works, but prefer def for named things
```

**When `lambda` is appropriate:**

- As a trivial `key=` argument: `sorted(users, key=lambda u: u["age"])`.
- As a quick callback in `map`/`filter`: `map(lambda x: x.strip(), lines)`.

**When to use `def` instead:**

- You need type annotations, default arguments, or a docstring.
- The logic needs more than one expression.
- You want a meaningful name in tracebacks.

The rule of thumb: if you're tempted to assign a `lambda` to a variable (`square = lambda x: x*x`), write a `def` instead. That's what `def` is for.

### Higher-order functions

A higher-order function takes a function as an argument, returns a function, or both:

```python
def repeat(fn, n):
    """Apply fn to a value n times in sequence."""
    def go(x):
        for _ in range(n):
            x = fn(x)
        return x
    return go

double3 = repeat(lambda x: x * 2, 3)
double3(1)   # 8  (1 → 2 → 4 → 8)
```

Why write `repeat` this way? Because it separates *configuration* (which function, how many times) from *execution* (what value). You create `double3` once and call it many times with different inputs. This is the same principle behind decorators, which you'll meet in chapter 08.

### Generators — lazy pipelines

Generators let you build pipelines that process one value at a time, using constant memory regardless of input size:

```python
def squares(xs):
    for x in xs:
        yield x * x

def evens(xs):
    return (x for x in xs if x % 2 == 0)

list(evens(squares(range(10))))   # [0, 4, 16, 36, 64]
```

Each generator yields one item, then suspends. No intermediate lists are built. This is why you can process a billion-row file with a generator pipeline that uses a few kilobytes of memory.

Generator expressions — `(expr for x in iterable)` — are the lazy equivalent of list comprehensions. Use them whenever you don't need the full list in memory.

## Why these design choices

**Why does Python make functions first-class?** Because it simplifies the language. If functions are objects, you don't need separate syntax for callbacks, strategies, or event handlers. One mechanism handles them all.

**Why prefer comprehensions over `map`/`filter`?** Readability and consistency. Comprehensions don't require importing `functools`, they're taught early, and they avoid the `lambda` noise. But `map(str.strip, lines)` is cleaner than `[s.strip() for s in lines]` when you already have a named function — so it's not a hard rule.

**When would you pick differently?** In languages where `map`/`filter` are the primary syntax (Haskell, Elixir, JavaScript's `.map()`), you'd lean into them. In Python, reach for comprehensions first. Reach for generators when data is large or unbounded. Reach for `reduce` only when no built-in (like `sum`, `max`, `any`, `all`) fits.

## Production-quality code

```python
from functools import reduce
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def pipeline(*stages: Callable[[Iterable[T]], Iterable[U]]) -> Callable[[Iterable], list]:
    """Compose generator stages into a lazy pipeline, materialize at the end.

    Each stage takes an iterable and yields items.
    """
    if not stages:
        raise TypeError("pipeline requires at least one stage")
    for i, s in enumerate(stages):
        if not callable(s):
            raise TypeError(f"Stage {i} is not callable: {s!r}")

    def run(source: Iterable) -> list:
        current: Iterable = source
        for stage in stages:
            current = stage(current)
        return list(current)

    return run


def strip_all(lines: Iterable[str]) -> Iterable[str]:
    return (line.strip() for line in lines)

def nonempty(lines: Iterable[str]) -> Iterable[str]:
    return (line for line in lines if line)

def lowercase(lines: Iterable[str]) -> Iterable[str]:
    return (line.lower() for line in lines)


clean = pipeline(strip_all, nonempty, lowercase)

raw = ["  Hello  ", "", "  WORLD ", "  ", " Python "]
assert clean(raw) == ["hello", "world", "python"]
```

## Security notes

N/A — first-class functions are a language feature, not a security surface. However, be careful when accepting *user-supplied callables* (e.g., deserializing functions with `pickle` or `eval`). Never execute untrusted code. This concern is covered in the security module.

## Performance notes

- **`map` vs. comprehension:** In CPython, list comprehensions are marginally faster than `list(map(lambda ...))` because they avoid the per-call overhead of `lambda`. With a named C-level function (like `str.strip`), `map` can be faster since it skips Python call dispatch.
- **Generators are O(1) memory:** A generator expression `(x*x for x in range(10**9))` uses constant memory. The equivalent list comprehension allocates ~8 GB.
- **Iterator exhaustion:** `map()` and generator expressions return one-shot iterators. Iterating twice yields nothing the second time. If you need multiple passes, materialize to a `list` first.
- **`reduce` overhead:** Each step calls a Python-level function. For summation, `sum()` is 10–50x faster because it's implemented in C.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Second iteration of `map(...)` returns nothing | `map` returns a one-shot iterator; it's exhausted after the first pass | Wrap in `list()` if you need the result more than once, or use a comprehension |
| 2 | `lambda` with multiple statements causes `SyntaxError` | `lambda` only supports a single expression, not statements | Use `def` for anything beyond a trivial expression |
| 3 | `reduce(lambda a,b: a+b, xs)` instead of `sum(xs)` | Over-using `reduce` when a built-in is clearer and faster | Prefer `sum`, `max`, `min`, `any`, `all` when they fit |
| 4 | `sorted(xs, key=lambda x: x)` — lambda does nothing | Sorting with a key function that returns the element unchanged | Remove the `key` argument; the default sort already compares elements directly |
| 5 | Generator pipeline silently produces `[]` | One stage in the pipeline consumes its input but yields nothing (e.g., a stage that calls `list()` internally) | Ensure every stage is a generator that yields items, not one that materializes and forgets to yield |

## Practice

**Warm-up.** Sort a list of strings by length using `sorted(..., key=...)`.

<details><summary>Solution</summary>

```python
strings = ["banana", "fig", "apple", "kiwi"]
result = sorted(strings, key=len)
# ['fig', 'kiwi', 'apple', 'banana']
```

</details>

**Standard.** Given `records = [{"x": 1}, {"x": 2}, {"x": 3}]`, use `map` to extract the `"x"` values into a list.

<details><summary>Solution</summary>

```python
records = [{"x": 1}, {"x": 2}, {"x": 3}]
values = list(map(lambda r: r["x"], records))
assert values == [1, 2, 3]

# Or with operator.itemgetter:
from operator import itemgetter
values = list(map(itemgetter("x"), records))
```

</details>

**Bug hunt.** Why does this code print an empty list on the second call?

```python
m = map(str.upper, ["hello", "world"])
print(list(m))   # ['HELLO', 'WORLD']
print(list(m))   # [] — why?
```

<details><summary>Solution</summary>

`map` returns a one-shot iterator. After the first `list(m)` call, the iterator is exhausted. The second `list(m)` finds nothing left to yield. Fix: store the result in a list first — `result = list(map(str.upper, [...]))` — then use `result` as many times as you want.

</details>

**Stretch.** Implement `compose(*fns)` that applies functions right-to-left: `compose(f, g, h)(x)` computes `f(g(h(x)))`.

<details><summary>Solution</summary>

```python
def compose(*fns):
    if not fns:
        raise TypeError("compose requires at least one function")

    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed

shout_clean = compose(str.upper, str.strip)
assert shout_clean("  hello  ") == "HELLO"
```

</details>

**Stretch++.** Build a lazy pipeline that reads a large file, strips whitespace, filters out blank lines and comment lines (starting with `#`), extracts the first comma-separated column, and returns the count — processing one line at a time in constant memory.

<details><summary>Solution</summary>

```python
def read_lines(path):
    with open(path) as f:
        yield from f

def stripped(lines):
    return (line.strip() for line in lines)

def no_blanks(lines):
    return (line for line in lines if line)

def no_comments(lines):
    return (line for line in lines if not line.startswith("#"))

def first_column(lines):
    return (line.split(",")[0] for line in lines)

def count(items):
    return sum(1 for _ in items)

total = count(first_column(no_comments(no_blanks(stripped(read_lines("data.csv"))))))
```

</details>

## In plain terms (newbie lane)
If `First Class Functions` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `lambda` can contain:
    (a) Multiple statements
    (b) Only a single expression
    (c) Async/await
    (d) A default return of `None`

2. `map` returns:
    (a) A list
    (b) A tuple
    (c) A lazy iterator
    (d) A set

3. Functions in Python are:
    (a) Not passable as arguments
    (b) First-class values — objects like any other
    (c) Immutable strings
    (d) Only callable, not storable

4. A generator expression uses:
    (a) Square brackets `[...]`
    (b) Parentheses `(...)`
    (c) Curly braces `{...}`
    (d) Angle brackets `<...>`

5. Prefer `sum(xs)` over `reduce(lambda a,b: a+b, xs)` because:
    (a) It's faster
    (b) It's clearer
    (c) Both — it's faster and clearer
    (d) Neither — they're equivalent

**Short answer:**

6. When is `lambda` appropriate versus `def`?
7. Why do generators use constant memory?

*Answers: 1-b, 2-c, 3-b, 4-b, 5-c, 6. Use lambda for trivial one-expression callbacks (key functions, quick map/filter predicates). Use def when you need a name, docstring, type annotations, defaults, or more than one expression. 7. Generators yield one item at a time and suspend execution between yields, so they never build the full sequence in memory — only one element exists at a time.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-first-class-functions — mini-project](mini-projects/02-first-class-functions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Functions are values in Python: you can pass, return, and store them like any other object.
- Prefer comprehensions and generators over `map`/`filter` for readability; save `reduce` for real folds where no built-in exists.
- `lambda` is for trivial one-expression callbacks; anything more complex deserves a `def`.
- Generators enable constant-memory lazy pipelines — essential for processing large or unbounded data.

## Further reading

- Python docs: [`functools`](https://docs.python.org/3/library/functools.html), [`itertools`](https://docs.python.org/3/library/itertools.html).
- David Beazley, *Generator Tricks for Systems Programmers* — the definitive guide to generator pipelines.
- Next: [Pure functions](03-pure-functions.md).
