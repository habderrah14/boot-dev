# Chapter 09 — Lists

> Lists are Python's first-class sequence: ordered, mutable, and indexed. Nearly every program you write will use one.

## Learning objectives

By the end of this chapter you will be able to:

- Create, index, slice, and mutate a `list`.
- Use the key methods (`append`, `extend`, `insert`, `pop`, `sort`, `reverse`) and recall their cost.
- Distinguish list from tuple and pick correctly.
- Avoid the shared-reference traps that come with mutability and `*` replication.
- Reach for `collections.deque` when a list is the wrong tool.

## Prerequisites & recap

- [Variables](02-variables.md) — names point at values; mutation reaches through.
- [Loops](08-loops.md).

Recap from chapter 02: `b = a` does not copy; both names point at the same list. This becomes a daily concern in this chapter.

## The simple version

A list is an **ordered, mutable, indexed** collection. You can put anything into it (mixed types are legal but rarely a good idea), grow it with `append`, shrink it with `pop`, and read elements in O(1) by index. The price of mutability is sharing — two names can point at the same list and changes are visible through both.

## In plain terms (newbie lane)

This chapter is really about **Lists**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How a list lives in memory and what each method costs.

```
                   ┌────┬────┬────┬────┬────┐
   xs ────────▶    │ 10 │ 20 │ 30 │ 40 │ 50 │  ←── contiguous array of references
                   └────┴────┴────┴────┴────┘
                   idx 0   1    2    3    4

   xs.append(60)        →  add at the end                 amortized O(1)
   xs.pop()             →  remove from the end                       O(1)
   xs.insert(0, 99)     →  shift every element right                 O(n)
   xs.pop(0)            →  shift every element left                  O(n)
   xs.remove(30)        →  find then shift                           O(n)
   xs.sort()            →  Timsort, in place                  O(n log n)
   x in xs              →  linear scan                               O(n)
```

For frequent push/pop at *both* ends, use `collections.deque` (double-ended queue, O(1) at both ends).

## Concept deep-dive

### Creating

```python
nums = [1, 2, 3]
empty = []
same = list(range(5))         # [0, 1, 2, 3, 4]
chars = list("abc")           # ['a', 'b', 'c']
zeros = [0] * 10              # [0, 0, ..., 0] — fine for immutable scalars
```

### Indexing & slicing

```python
xs = [10, 20, 30, 40, 50]
xs[0]       # 10
xs[-1]      # 50  (negative indexes from the end)
xs[1:4]     # [20, 30, 40]
xs[:2]      # [10, 20]
xs[::-1]    # [50, 40, 30, 20, 10] — reversed copy
xs[::2]     # [10, 30, 50] — every other element
```

Slicing always returns a **new list**. Slice assignment replaces a range:

```python
xs[1:3] = [99]
# xs is now [10, 99, 40, 50]
```

### Mutation vs. rebinding

```python
xs.append(60)       # mutates in place; the list object is the same
xs = xs + [70]      # REBINDS xs to a new list (O(n) copy)
```

The first is O(1) amortized and visible to other names pointing at the list. The second is O(n) and creates a fresh list — other names still point at the old one.

### Key methods (cheat sheet)

| Method                | Returns       | Cost              | Notes                              |
|-----------------------|---------------|-------------------|------------------------------------|
| `xs.append(x)`        | `None`        | amortized O(1)    | grows in place                     |
| `xs.extend(ys)`       | `None`        | O(len(ys))        | concatenates in place              |
| `xs.insert(i, x)`     | `None`        | O(n)              | shifts all subsequent elements     |
| `xs.pop()`            | last item     | O(1)              | from the end                       |
| `xs.pop(0)`           | first item    | O(n)              | shifts everything left             |
| `xs.remove(x)`        | `None`        | O(n)              | first match by `==`                |
| `xs.sort()`           | `None`        | O(n log n)        | in place; stable                   |
| `sorted(xs)`          | new list      | O(n log n)        | does not mutate `xs`               |
| `xs.reverse()`        | `None`        | O(n)              | in place                           |
| `x in xs`             | `bool`        | O(n)              | linear scan                        |
| `len(xs)`             | `int`         | O(1)              |                                    |

### Copying

- **Shallow copy** (one level): `ys = xs[:]`, `list(xs)`, or `xs.copy()`.
- **Deep copy** (nested mutables too): `import copy; copy.deepcopy(xs)`.

A shallow copy is enough when the elements are immutable (`int`, `str`, `tuple`-of-immutables). It's a bug when elements are themselves lists or dicts.

### Tuples — the immutable cousin

```python
point = (3, 4)
x, y = point
```

Tuples are immutable, hashable (if elements are), and slightly faster than lists. Use them for **fixed-size, heterogeneous records**: `(name, age, role)`. Use lists for variable-size, homogeneous collections.

`namedtuple` and `dataclass` give you self-documenting versions:

```python
from collections import namedtuple
Point = namedtuple("Point", "x y")
p = Point(3, 4)
p.x, p.y      # 3, 4
```

### `list * n` shares references

```python
rows = [[0] * 3] * 2
rows[0][0] = 1
print(rows)      # [[1, 0, 0], [1, 0, 0]]   ← same inner list, twice
```

`*` repeats *references*. The fix is a comprehension that runs the inner expression each time:

```python
rows = [[0] * 3 for _ in range(2)]
rows[0][0] = 1
print(rows)      # [[1, 0, 0], [0, 0, 0]]   ✓
```

## Why these design choices

- **Lists are dynamic arrays, not linked lists.** O(1) random access, O(n) insertion in the middle. The choice trades insert cost for the ~10× cache-friendly read speed an array gives over a linked list. `collections.deque` exists for the cases where you legitimately need O(1) push/pop at both ends.
- **Mutation in place returns `None`.** This is a deliberate design choice: it prevents you from chaining `xs.sort().append(x)` and discovering at runtime that `sort` returned `None`. The convention is "in place returns None; pure returns a new value".
- **Slices copy.** Sharing slice views (like NumPy does) is faster but mutation rules become a minefield. Python prioritizes simplicity over the one-percent speed win.
- **Tuples vs. lists.** Tuples signal "fixed-shape record" to the reader; lists signal "homogeneous, growable". Linters and type checkers exploit this. Same shape, different semantics.
- **When you'd choose differently.** For numeric arrays, NumPy. For deques, `collections.deque`. For ordered, deduplicated collections, `dict.fromkeys(xs)` or a `set` (if order isn't needed).

## Production-quality code

### Example 1 — Order-preserving uniqueness

```python
"""Return the unique elements of xs in their first-seen order."""

from typing import Iterable, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


def unique(xs: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    out: list[T] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


if __name__ == "__main__":
    print(unique([3, 1, 3, 2, 1]))   # [3, 1, 2]
```

The naive `if x not in out` would be O(n²) — list membership is linear. The `seen` set keeps it O(n). For Python 3.7+, `list(dict.fromkeys(xs))` is a one-liner that achieves the same thing using dict's insertion-order guarantee.

### Example 2 — A small in-memory queue, done right

```python
"""Use deque, not list, when you need a FIFO."""

from collections import deque


def process_jobs(initial: list[str]) -> list[str]:
    """Drain a queue, appending 'RETRY:<job>' once per job, returning the order processed."""
    queue: deque[str] = deque(initial)
    processed: list[str] = []
    while queue:
        job = queue.popleft()        # O(1) — list.pop(0) would be O(n)
        processed.append(job)
        if job.startswith("flaky"):
            queue.append(f"RETRY:{job}")
    return processed
```

`deque.popleft()` is O(1); `list.pop(0)` is O(n). For 10k jobs the difference is the difference between "instant" and "noticeable".

## Security notes

- **Untrusted indices.** `xs[user_index]` raises `IndexError` for out-of-range. Catch or validate (`0 <= i < len(xs)`) so a crafted request doesn't crash your handler.
- **Don't `eval` a string that "looks like a list".** Use `ast.literal_eval` for safe evaluation of literal data structures, or `json.loads` if it's actually JSON.
- **Memory exhaustion via `list * n`.** A user-supplied `n` of `10**9` will allocate gigabytes silently. Validate sizes before allocating.

## Performance notes

- **Cache-friendly reads.** A list is a contiguous array of pointers; iterating sequentially is cache-friendly.
- **Append is amortized O(1)** because Python over-allocates: when capacity is exhausted, it grows the buffer geometrically.
- **`pop(0)` and `insert(0, x)` are O(n).** This is the #1 reason juniors' "queue" implementations are slow on real input.
- **Sorting is O(n log n) Timsort**, optimized for partially-sorted data — naturally sorted runs are detected and merged.
- **Membership (`x in xs`) is O(n).** For repeated lookups, build a `set` once and query it.
- **Comprehensions are faster than `for + append`** by ~30% — the loop machinery runs in C.

## Common mistakes

- **Shared inner lists from `*` replication.** Symptom: changing `grid[0][0]` changes every row. Cause: `[[0]*3]*2` shares the same inner list. Fix: `[[0]*3 for _ in range(2)]`.
- **Expecting `xs.sort()` to return the sorted list.** Symptom: `xs = xs.sort()` makes `xs` `None`. Cause: in-place methods return `None`. Fix: `xs.sort()` then use `xs`, or `xs = sorted(xs)`.
- **Using a list as a queue.** Symptom: throughput tanks after a few thousand items. Cause: `pop(0)` is O(n). Fix: `collections.deque`.
- **Quadratic deduplication.** Symptom: `unique` slow on large inputs. Cause: `if x not in out` on a list. Fix: track seen items in a `set`.
- **Mutating a list passed as a default argument.** See chapter 03's mutable-default trap — it's especially nasty with lists.

## Practice

1. **Warm-up.** Build `[1, 4, 9, 16, 25]` with a comprehension.
2. **Standard.** Merge two sorted lists into one sorted list without using `sorted` or `sort`.
3. **Bug hunt.** Fix the shared-row bug:

    ```python
    grid = [[0] * 3] * 3
    grid[0][0] = 1
    print(grid)  # all rows show [1, 0, 0] — wrong
    ```

4. **Stretch.** Rotate a list left by `k` in O(n) using slicing.
5. **Stretch++.** Implement `chunks(xs, size)` that yields successive chunks of length `size` (the last may be shorter).

<details><summary>Show solutions</summary>

```python
[n * n for n in range(1, 6)]
```

```python
def merge(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
```

```python
grid = [[0] * 3 for _ in range(3)]
```

```python
def rotate_left(xs, k):
    k %= len(xs) or 1
    return xs[k:] + xs[:k]
```

```python
def chunks(xs, size):
    if size <= 0:
        raise ValueError("size must be positive")
    for i in range(0, len(xs), size):
        yield xs[i:i + size]
```

</details>

## Quiz

1. `xs[-1]` gives:
    (a) the first item (b) the last item (c) error on empty (d) both b and c
2. `xs.sort()` returns:
    (a) the sorted list (b) `None` (c) the original (d) a new list
3. `len([[0]*3]*2)` equals:
    (a) 2 (b) 3 (c) 6 (d) error
4. `xs.pop(0)` is:
    (a) O(1) (b) O(n) (c) O(log n) (d) undefined
5. Tuples differ from lists in:
    (a) indexing (b) slicing (c) mutability (d) iteration

**Short answer:**

6. Why does `xs = xs + [y]` differ from `xs.append(y)` in cost and semantics?
7. When should a tuple replace a list?

*Answers: 1-d, 2-b, 3-a, 4-b, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-lists — mini-project](mini-projects/09-lists-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Lists are ordered, mutable, and indexed; slicing copies, in-place methods return `None`.
- The `*` operator on lists shares references — use a comprehension for nested structures.
- Reach for `deque` for FIFO, `set` for membership tests, and `tuple` for fixed records.
- Memorize the Big-O of each method — it's the difference between fast and slow code.

## Further reading

- Python docs — [`list`](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists), [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque).
- Tim Peters' [Timsort description](https://github.com/python/cpython/blob/main/Objects/listsort.txt).
- Next: [dictionaries](10-dictionaries.md).
