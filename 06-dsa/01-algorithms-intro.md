# Chapter 01 — Algorithms Intro

> "An algorithm is a recipe: finite, unambiguous, and correct. Everything in this module is either an algorithm or a data structure the algorithms live in."

## Learning objectives

By the end of this chapter you will be able to:

- Define *algorithm* and *data structure* in your own words.
- Walk through a simple algorithm on paper before writing a single line of code.
- Name the four qualities you judge every algorithm by: correctness, performance, simplicity, and generality.
- Implement and trace linear search and binary search.

## Prerequisites & recap

- [Module 01 — Python](../01-python/README.md) — you should be comfortable with functions, loops, and lists.

## The simple version

Think of an algorithm as a cooking recipe. It takes ingredients (inputs), follows a series of clear, unambiguous steps, and eventually produces a dish (output). The recipe must actually finish — it can't say "stir forever." And each step must be precise enough that anyone following it gets the same result.

A data structure, on the other hand, is how you organize your pantry. Put your spices in alphabetical order and you can find cumin in seconds. Dump them in a pile and you're scanning every jar. The way you *organize* data determines how fast your algorithms can work on it. That interplay — algorithm plus data structure — is the core of this entire module.

## Visual flow

```
  +----------+     +---------+     +------------+     +--------+     +----------+     +------+
  | Problem  |---->| Design  |---->| Implement  |---->|  Test  |---->| Analyze  |---->| Done |
  | (paper!) |     | (trace) |     | (code)     |     | (edge  |     | (Big-O)  |     |      |
  +----------+     +---------+     +------------+     | cases) |     +----------+     +------+
                                                      +--------+
```
*Figure 1-1: The algorithm development loop. Notice that "paper" comes before "code."*

## Concept deep-dive

### What is an algorithm?

Donald Knuth defined it: *"An algorithm is a finite, definite, effective procedure that produces an output from input(s)."*

Three properties make that definition tick:

- **Finite** — it must halt. An infinite loop isn't an algorithm; it's a bug.
- **Definite** — each step is unambiguous. "Sort of check the list" isn't a step; `if xs[i] == target` is.
- **Effective** — each step is doable with basic operations. You can't hand-wave "now factor this 500-digit number."

Why does this matter to you as a backend developer? Because when you write request handlers, data pipelines, or batch jobs, you need guarantees. Does your handler always return? Does every edge case produce a correct result? Those are the questions algorithms formalize.

### What is a data structure?

A data structure is an *organization of data* that makes some operations fast — usually at the expense of others. A Python `list` gives you O(1) access by index but O(n) search. A `dict` gives you O(1) average search but doesn't preserve insertion order the way you might expect (well, CPython 3.7+ does, but that's an implementation detail, not a language guarantee — until 3.7 made it one).

Choosing the right structure can drop an algorithm from O(n²) to O(n). You'll see this repeatedly throughout this module: the data structure *enables* the algorithm.

### Qualities to judge by

Every algorithm you write or evaluate should be judged on four axes:

1. **Correctness** — does it produce the right answer for *all* valid inputs, including edge cases? This is non-negotiable.
2. **Performance** — how much time and space does it use as the input grows? (That's what Big-O, Chapter 03, formalizes.)
3. **Simplicity** — can you prove it correct? Can a teammate reading it at 2 a.m. during an incident? Simple code has fewer bugs.
4. **Generality** — does it degrade gracefully at the edges? An empty list, a single element, duplicates, negative numbers — a good algorithm handles them all without special-casing.

### On-paper first

Before you write code, trace the algorithm by hand with a small example. If you can't do it on paper, you won't do it in code. Draw three things:

- The input values.
- The variables and how they change at each step.
- The final output.

This habit will save you hours of debugging. It's the single most underrated skill in DSA.

### The classic: linear search

Linear search is the simplest algorithm worth studying. You walk through every element until you find the target or run out of list.

Why start here? Because it establishes the baseline. Every fancier search algorithm is measured against "well, I could just scan the whole thing." If your clever algorithm doesn't beat O(n) for your workload, you don't need it.

### Binary search: when structure enables speed

Binary search exploits a *sorted* input. Instead of scanning every element, you check the middle, then throw away the half that can't contain the target. Each step halves the search space — that's why it's O(log n).

The key insight: the data structure (a sorted sequence) *enables* the algorithm (binary search). Without the sort invariant, binary search produces wrong answers. This interplay between structure and algorithm is the theme of the entire module.

### "Loop, accumulate, return"

Most DSA boils down to a pattern: set up state, iterate through data updating state, return the final state. Summing an array, finding a maximum, counting occurrences — they're all variations on this skeleton. Once you see it, you'll recognize it everywhere.

## Why these design choices

**Linear search vs. binary search** — why would you ever use linear search if binary is faster? Three reasons:

1. **Your data isn't sorted.** Binary search requires a sorted input. If you need to sort first, that's O(n log n) — which might cost more than a single O(n) scan.
2. **Your data is small.** For n < 50 or so, linear search with its minimal overhead often *outperforms* binary search in wall-clock time due to cache locality and branch prediction.
3. **Your data changes frequently.** Maintaining a sorted array means O(n) inserts. If you're inserting often and searching rarely, a linear scan on an unsorted list can win overall.

**When to pick differently:** If you search the same dataset thousands of times, sort it once (O(n log n)) and binary-search each time (O(log n)). If you need even faster lookups, consider a hash set (O(1) average) — but that's Chapter 06 territory.

## Production-quality code

```python
from typing import Sequence, TypeVar

T = TypeVar("T")


def linear_search(xs: Sequence[T], target: T) -> int:
    """Return index of first occurrence of target, or -1 if absent."""
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1


def binary_search(xs: Sequence[int], target: int) -> int:
    """Return index of target in sorted sequence xs, or -1 if absent.

    Precondition: xs must be sorted in ascending order.
    """
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2  # avoids overflow in languages with fixed-width ints
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def array_sum(xs: Sequence[int | float]) -> int | float:
    """Sum all elements. Demonstrates the 'loop, accumulate, return' pattern."""
    total = 0
    for x in xs:
        total += x
    return total
```

## Security notes

N/A — search and summation algorithms operate on in-memory data with no external I/O, no deserialization, and no privilege boundaries. Security concerns arise when you use these algorithms on *untrusted input sizes* (see Performance notes).

## Performance notes

| Algorithm | Time (worst) | Time (best) | Space |
|---|---|---|---|
| Linear search | O(n) | O(1) — target is first | O(1) |
| Binary search | O(log n) | O(1) — target is middle | O(1) |
| Array sum | O(n) | O(n) | O(1) |

- **Linear search** touches every element in the worst case. For 10⁶ items, that's 10⁶ comparisons — about 1 ms on modern hardware.
- **Binary search** on 10⁶ sorted items does ~20 comparisons. That's the power of logarithms.
- **Watch out for hidden costs:** Python's `in` operator on a `list` is linear search. If you're calling `x in some_list` inside a loop over another list, you have O(n·m) — which can silently kill performance.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Binary search returns wrong index or misses elements | Input isn't actually sorted | Always ensure the sort invariant. Add an assertion during development: `assert xs == sorted(xs)` |
| 2 | Off-by-one: binary search infinite-loops or skips elements | Using `mid = (lo + hi) // 2` and updating `lo = mid` instead of `lo = mid + 1` | After checking `xs[mid]`, always move *past* mid: `lo = mid + 1` or `hi = mid - 1` |
| 3 | "It worked on my test" but fails in production | Only tested the happy path — missed empty list, single element, all-duplicates, target-not-present | Test edge cases *first*: `[]`, `[42]`, `[1,1,1,1]`, target absent |
| 4 | Confusing best-case and worst-case when choosing an algorithm | Assuming average-case performance is guaranteed | Always reason about worst-case unless you can prove the input distribution |

## Practice

**Warm-up.** Implement `linear_search` from scratch without looking at the code above. Test it with an empty list, a single-element list, and a list where the target is last.

<details><summary>Show solution</summary>

```python
def linear_search(xs, target):
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1

assert linear_search([], 5) == -1
assert linear_search([5], 5) == 0
assert linear_search([1, 2, 3], 3) == 2
assert linear_search([1, 2, 3], 4) == -1
```

</details>

**Standard.** Implement `binary_search` from scratch. Test with an empty list, a miss, and a hit at both boundaries.

<details><summary>Show solution</summary>

```python
def binary_search(xs, target):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if xs[mid] == target:
            return mid
        elif xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

assert binary_search([], 1) == -1
assert binary_search([1, 2, 3], 0) == -1
assert binary_search([1, 2, 3], 1) == 0
assert binary_search([1, 2, 3], 3) == 2
```

</details>

**Bug hunt.** Trace `binary_search([1, 2, 3], 0)` on paper. What values do `lo`, `hi`, and `mid` take at each step? Why does it correctly return -1?

<details><summary>Show solution</summary>

```
Step 1: lo=0, hi=2, mid=1 → xs[1]=2 > 0 → hi=0
Step 2: lo=0, hi=0, mid=0 → xs[0]=1 > 0 → hi=-1
Step 3: lo=0 > hi=-1 → exit loop → return -1
```

The target 0 is less than every element, so `hi` keeps shrinking until `lo > hi`.

</details>

**Stretch.** Implement `lower_bound(xs, target)`: return the index of the *first* element ≥ target. This is a variant of binary search used heavily in real systems (database index lookups, for example).

<details><summary>Show solution</summary>

```python
def lower_bound(xs, target):
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

assert lower_bound([1, 3, 5, 7], 4) == 2   # first element >= 4 is 5 at index 2
assert lower_bound([1, 3, 5, 7], 5) == 2   # exact match
assert lower_bound([1, 3, 5, 7], 0) == 0   # everything qualifies
assert lower_bound([1, 3, 5, 7], 9) == 4   # nothing qualifies
```

Note the subtle differences from standard binary search: `hi` starts at `len(xs)` (not `len(xs) - 1`), and the loop condition is `lo < hi` (not `lo <= hi`). These prevent off-by-one errors in the "first ≥" variant.

</details>

**Stretch++.** Measure the wall-clock runtime of linear search vs. binary search on a sorted list of 10⁶ integers. Search for 1000 random targets and compare the total time for each approach.

<details><summary>Show solution</summary>

```python
import random
import time

data = list(range(1_000_000))
targets = [random.randint(0, 1_500_000) for _ in range(1000)]

start = time.perf_counter()
for t in targets:
    linear_search(data, t)
linear_time = time.perf_counter() - start

start = time.perf_counter()
for t in targets:
    binary_search(data, t)
binary_time = time.perf_counter() - start

print(f"Linear: {linear_time:.3f}s")
print(f"Binary: {binary_time:.3f}s")
print(f"Ratio:  {linear_time / binary_time:.0f}x")
```

Expect binary search to be roughly 10,000–50,000× faster for this input size.

</details>

## In plain terms (newbie lane)
If `Algorithms Intro` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. An algorithm must:
    (a) be infinite  (b) halt, be definite, and be effective  (c) be recursive  (d) use a data structure

2. Binary search requires:
    (a) sorted input  (b) unique elements  (c) integer elements  (d) an immutable sequence

3. Linear search is:
    (a) O(log n)  (b) O(n)  (c) O(1)  (d) O(n²)

4. The trade-off between binary and linear search is:
    (a) binary is faster but requires sorted input  (b) linear is always better  (c) binary mutates the input  (d) there is no difference

5. The first step when solving any DSA problem should be:
    (a) write code  (b) trace an example on paper  (c) measure performance  (d) optimize

**Short answer:**

6. When might linear search beat binary search in practice?
7. Name the four qualities we judge algorithms by.

*Answers: 1-b, 2-a, 3-b, 4-a, 5-b, 6-When data is unsorted, very small, or searched only once (sorting cost exceeds search savings), 7-Correctness, performance, simplicity, generality.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-algorithms-intro — mini-project](mini-projects/01-algorithms-intro-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- An algorithm is a finite, definite, effective procedure. A data structure is how you organize data to make specific operations fast. Together, they form solutions.
- Always trace on paper before coding — it's the fastest way to catch bugs and build intuition.
- Judge every algorithm on correctness first, then performance, simplicity, and generality.
- The right data structure enables the right algorithm: sorted data turns O(n) search into O(log n).

## Further reading

- *The Algorithm Design Manual*, Steven Skiena — the preface alone is worth your time.
- *Introduction to Algorithms* (CLRS) — the canonical reference, chapters 1–2.
- Python `bisect` module documentation — the standard library's binary search.
- Next: [Math](02-math.md).
