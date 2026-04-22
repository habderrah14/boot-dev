# Chapter 08 — Loops

> Repetition is where beginners feel power and experts feel caution. Both are right.

## Learning objectives

By the end of this chapter you will be able to:

- Write `for` and `while` loops idiomatically.
- Use `range`, container iteration, `enumerate`, and `zip`.
- Use `break` and `continue` deliberately, not as escape hatches.
- Recognize when a comprehension is clearer than a loop.
- Avoid the classic mutate-while-iterating bug.

## Prerequisites & recap

- [Comparisons](07-comparisons.md) — loop conditions are comparisons.
- [Functions](03-functions.md) — most loops are extracted into named functions in real code.

Recap: you can already test a condition (`if`) and execute a block once. Loops execute it repeatedly.

## The simple version

Two loop shapes cover 99% of cases. **`for`** runs once per item in something iterable (list, range, file). **`while`** runs as long as a condition is true. Reach for `for` first; pick `while` when you don't know the iteration count in advance.

A **comprehension** (`[expr for x in xs if cond]`) is a `for` loop that builds a new collection in one expression — clearer when the body is a single transformation.

## In plain terms (newbie lane)

This chapter is really about **Loops**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How `for x in xs:` advances and exits.

```
   ┌─────────────┐
   │  iter(xs)   │  ←─ Python builds an iterator
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐         StopIteration
   │  next(it)   │  ───────────────────────▶  loop ends
   └──────┬──────┘
          │ value
          ▼
   ┌─────────────┐
   │  body uses  │  ──── break ────▶  exits immediately (skips else)
   │  x, runs    │  ──── continue ─▶  back to next(it)
   └──────┬──────┘
          │
          └──────────▶  back to next(it)
```

## Must know now

- The chapter's core mental model and one working example.
- The most common beginner bug for this topic.
- Enough to finish the matching exercise L1 and L2 tasks.

## Can skip for now

- Advanced performance caveats.
- Rare edge cases and deep language internals.
- Optional tooling depth that is not needed for this chapter's checkpoint.

## Concept deep-dive

### `for` loops the iterable

```python
for i in range(5):
    print(i)             # 0 1 2 3 4

for name in ["ada", "bob"]:
    print(name)

for i, name in enumerate(["ada", "bob"], start=1):
    print(i, name)       # 1 ada / 2 bob

for a, b in zip([1, 2, 3], ["x", "y", "z"]):
    print(a, b)

for a, b in zip([1, 2, 3], ["x", "y"], strict=True):
    ...                  # raises ValueError on length mismatch (Py 3.10+)
```

`range(start, stop, step)` is exclusive of `stop`. `enumerate(xs, start=0)` pairs index with item. `zip` pairs items from two or more iterables, stopping at the shortest unless `strict=True`.

### `while` for condition-driven loops

```python
n = 1
while n < 1000:
    n *= 2
print(n)    # 1024

# Retry with bounded attempts
attempts = 0
while attempts < 5:
    if try_call():
        break
    attempts += 1
else:
    raise RuntimeError("gave up after 5 attempts")
```

Use `while` when the iteration count depends on results computed during the loop (retries, parsing until EOF, simulation until stable).

### `break` and `continue`

- `break` exits the **nearest** enclosing loop immediately.
- `continue` jumps to the next iteration.

```python
for line in lines:
    if not line.strip():
        continue              # skip blank lines
    if line.startswith("#"):
        break                 # stop at first comment
    process(line)
```

Over-using these hurts readability. A single `if process(line):` around the call often reads better than two `continue`s and a `break`.

### Loop `else`

```python
for x in haystack:
    if x == needle:
        break
else:
    print("not found")
```

`else` runs **iff** the loop completed *without* `break`. Useful for "search; on miss, do X" patterns. Most teams find it confusing — use sparingly and leave a comment.

### Comprehensions

```python
squares = [n * n for n in range(10)]
evens   = [n for n in range(20) if n % 2 == 0]
pairs   = {w: len(w) for w in words}
uniq    = {w.lower() for w in words}
gen     = (n * n for n in range(10**6))   # generator: lazy, no list built
```

A comprehension replaces a 3-line `for + append` loop with one expression. Use them when the body is **one transformation plus optional filter**. If the body needs multiple steps or branches, write the loop.

### Mutation during iteration

```python
items = [1, 2, 3, 4]
for x in items:
    items.remove(x)        # corrupts the iteration; ends with [2, 4]
```

Iterating a list while inserting or removing items shifts the underlying indices and the iterator misses elements. Workarounds:

- Iterate a *copy*: `for x in list(items):`.
- Build a new list: `items = [x for x in items if keep(x)]`.
- For dicts: iterate `list(d.keys())` or `list(d.items())`.

### Walrus operator (`:=`)

```python
while (line := input_stream.readline()):
    process(line)
```

Assigns and tests in one expression. Useful for read-and-test loops; otherwise prefer the unambiguous two-line form.

## Why these design choices

- **`for` over `while`.** A `for` loop has a single, obvious termination condition (the iterator runs out). A `while` invites infinite-loop bugs and demands a manual counter when one is needed. Pick the shape that matches your iteration source.
- **Comprehensions are expressions, not statements.** That makes them composable: you can pass `[n*n for n in xs]` directly to `sum`, `max`, or another function. A multi-line `for` can't appear inside another expression.
- **Loop `else`.** Underused because it's confusing; not because it's bad. Save it for the canonical "for-search" pattern, where the alternative is a sentinel boolean.
- **No `do-while` in Python.** The `while True: … if cond: break` pattern is the idiomatic substitute.
- **When you'd choose differently.** Tight numeric loops over arrays should *not* be Python `for` loops — vectorize with NumPy or push to C. Iterating millions of items in pure Python is the wrong tool.

## Production-quality code

### Example 1 — Sum of digits, both ways

```python
"""Two equivalent ways to sum the digits of a non-negative int."""


def digit_sum_loop(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


def digit_sum_str(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    return sum(int(c) for c in str(n))


if __name__ == "__main__":
    for fn in (digit_sum_loop, digit_sum_str):
        assert fn(12345) == 15, fn.__name__
    print("ok")
```

The string-conversion form is shorter and slightly slower. Both are fine; pick the clearer one in context.

### Example 2 — FizzBuzz with patterns

```python
"""FizzBuzz, then refactored to extend without rewriting."""


def fizzbuzz(n: int) -> list[str]:
    """Return the FizzBuzz sequence from 1 to n inclusive."""
    out = []
    for i in range(1, n + 1):
        word = ""
        if i % 3 == 0:
            word += "Fizz"
        if i % 5 == 0:
            word += "Buzz"
        out.append(word or str(i))
    return out


if __name__ == "__main__":
    for line in fizzbuzz(15):
        print(line)
```

The `word or str(i)` trick is a clean use of `or` returning operand values (chapter 07). Adding "Bazz" for multiples of 7 is a one-line addition — the structure scales.

## Security notes

- **Bounded retries.** A `while True:` retry loop without a max-attempts counter or exponential backoff turns one slow downstream into a self-DoS. Always pair retries with an attempt cap and a sleep.
- **Don't loop over user-controlled sizes blindly.** `for _ in range(int(request.body))` will burn CPU forever if a user sends `999999999`. Validate ranges before looping.
- **Iteration over untrusted iterables.** Implementing `__iter__` on a class can run arbitrary code. Don't `for x in user_supplied_object` without knowing the type.

## Performance notes

- A pure-Python `for` loop iterates at ~10⁷ items/second on a modern laptop. NumPy does the same elementwise math at ~10⁹.
- `list.append` is amortized O(1). Pre-allocating (`out = [None] * n`) is sometimes faster but rarely worth the complexity.
- `for x in xs` is faster than `for i in range(len(xs)): x = xs[i]` — the index version does extra work per iteration.
- `enumerate` and `zip` produce iterators in C; cheaper than building intermediate lists.
- Comprehensions are typically ~30% faster than the equivalent explicit loop because the loop logic runs in C, not Python bytecode.

## Common mistakes

- **Off-by-one with `range`.** Symptom: missing the last element or going one over. Cause: `range(n)` is `0..n-1`. Fix: write the bounds explicitly: `range(1, n+1)` for `1..n`.
- **Mutating a list while iterating.** Symptom: items skipped or `RuntimeError`. Cause: iterator position vs. list index drift. Fix: iterate a copy or build a new list.
- **Infinite `while`.** Symptom: terminal hangs, CPU at 100%. Cause: loop variable never reaches the exit condition. Fix: read every branch — does each path move toward termination?
- **Quadratic accidental cost.** Symptom: works on 100 items, hangs on 100k. Cause: nested loops over the same data, or `x in long_list` inside a loop. Fix: convert one of them to a set (`O(1)` membership) or sort-and-merge.
- **Comprehension abuse.** Symptom: a single-line comprehension nobody can read. Cause: nested ifs, multiple `for`s, side effects. Fix: it's a loop — write a loop.

## Practice

1. **Warm-up.** Print the integers 10 down to 1.
2. **Standard.** Given `words: list[str]`, print `"len  word"` for each, padded to 4.
3. **Bug hunt.** Why does this delete only half the items?

    ```python
    items = [1, 2, 3, 4]
    for x in items:
        items.remove(x)
    ```

4. **Stretch.** Without using `in`, write `contains(xs: list, target) -> bool`.
5. **Stretch++.** Rewrite FizzBuzz as a single list comprehension that returns a `list[str]`.

<details><summary>Show solutions</summary>

```python
for n in range(10, 0, -1):
    print(n)
```

```python
for w in words:
    print(f"{len(w):>4}  {w}")
```

3. The iterator advances by index. After `items.remove(1)`, `items == [2,3,4]` and the iterator's next index is 1 — pointing at `3`, skipping `2`. The off-by-one repeats.

```python
def contains(xs, target):
    for x in xs:
        if x == target:
            return True
    return False
```

```python
[("FizzBuzz" if n % 15 == 0
  else "Fizz" if n % 3 == 0
  else "Buzz" if n % 5 == 0
  else str(n)) for n in range(1, 21)]
```

</details>

## Quiz

1. `range(5)` yields:
    (a) 1..5 (b) 0..4 (c) 0..5 (d) 1..4
2. The idiomatic way to pair indexes with items:
    (a) `for i in range(len(xs))` (b) `for i, x in enumerate(xs)` (c) `while i < len(xs)` (d) `map(…)`
3. `break` does what in a nested loop?
    (a) exits all loops (b) exits the innermost loop (c) exits the function (d) raises
4. Which is typically clearer than a `for ... append` loop?
    (a) a comprehension (b) a `while` (c) `reduce` (d) recursion
5. `for ... else` runs `else`:
    (a) always (b) never (c) iff the loop finishes without `break` (d) iff the loop was empty

**Short answer:**

6. When would you pick `while` over `for`?
7. Why is mutating a list during iteration risky?

*Answers: 1-b, 2-b, 3-b, 4-a, 5-c.*

## Learn-by-doing mini-project

Use the single module project track and complete **Checkpoint D**:

- [Python Fundamentals Companion Track](mini-projects/00-python-fundamentals-companion-track.md)

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Prefer `for` for known iterables, `while` for condition-driven repetition.
- `enumerate`, `zip`, comprehensions, and the walrus cover the common idioms.
- Never mutate the thing you're iterating — copy it or build a new one.
- Watch nested loops over the same data; that's where O(n²) lives.

## Further reading

- Python docs — [*Compound statements: for, while*](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement).
- David Beazley, *Python Cookbook*, chapter 4 ("Iterators and Generators").
- Next: [lists](09-lists.md).
