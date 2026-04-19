# Chapter 04 — Sorting Algorithms

> "Sorting is solved in every standard library — which is exactly why understanding the classics pays off. You'll appreciate why `sorted()` beats your implementation, and you'll recognize sort-shaped problems in disguise."

## Learning objectives

By the end of this chapter you will be able to:

- Implement bubble sort, insertion sort, merge sort, and quick sort from scratch.
- Compare their time complexity, space complexity, and stability.
- Explain why Python uses Timsort and when `sorted()` is the right answer (almost always).
- Recognize problems that are "sorting in disguise" (inversions, median finding, scheduling).

## Prerequisites & recap

- [Chapter 03 — Big-O Analysis](03-big-o.md) — you need to analyze loop complexity.
- [Recursion](../05-fp/04-recursion.md) — merge sort and quick sort are recursive.

## The simple version

Sorting means rearranging a collection so elements are in order. That sounds trivial — and in production, it is: you call `sorted()` and move on. But *why* sorting matters goes deeper than putting numbers in order.

Sorting is a *force multiplier* for other algorithms. Once data is sorted, binary search works (O(log n) instead of O(n)), duplicates cluster together, medians become O(1) lookups, and merge-based algorithms become possible. Understanding the classic sorts gives you the vocabulary to recognize when a problem is "really just sorting" — which happens more often than you'd think.

## Visual flow

```
  Merge Sort: divide, conquer, merge
  ====================================

  [38, 27, 43, 3, 9, 82, 10]           Level 0: full array
          /                \
  [38, 27, 43]        [3, 9, 82, 10]    Level 1: split
    /      \            /        \
  [38]  [27, 43]    [3, 9]   [82, 10]   Level 2: split
         /   \       /   \     /    \
       [27] [43]   [3]  [9] [82]  [10]  Level 3: base cases
         \   /       \   /     \    /
       [27, 43]    [3, 9]   [10, 82]    Merge up
          \   /        \        /
  [27, 38, 43]     [3, 9, 10, 82]       Merge up
          \              /
  [3, 9, 10, 27, 38, 43, 82]            Merge: done!

  Each level does O(n) work. There are log(n) levels.
  Total: O(n log n).
```
*Figure 4-1: Merge sort recursion tree. The key insight: each level does O(n) total work across all sub-arrays.*

## Concept deep-dive

### Why study sorts you'll never use in production?

Three reasons:

1. **Pattern recognition.** Merge sort teaches you divide-and-conquer. Quick sort teaches you partitioning. Insertion sort teaches you maintaining a sorted invariant. These patterns appear everywhere — in database query plans, in distributed systems, in compiler optimization passes.
2. **Trade-off thinking.** Each sort makes different trade-offs (time vs. space, worst-case vs. average-case, stability vs. speed). Learning to evaluate trade-offs on sorting — where the problem is simple — prepares you to evaluate them on harder problems.
3. **Interviews.** Like it or not, sorting algorithms are common interview fodder. But the *real* skill being tested is "can you reason about algorithms?"

### Stability

A **stable** sort preserves the relative order of elements that compare equal. Why does this matter?

Imagine you have employee records sorted by first name, and you want to sort them by last name. With a stable sort, employees sharing a last name remain in first-name order — you get a natural "sort by last name, then first name" for free. With an unstable sort, the first-name ordering is destroyed.

### Bubble sort — O(n²), stable

Repeatedly walk through the list, swapping adjacent elements that are out of order. Each pass "bubbles" the largest unsorted element to its correct position.

Why is it O(n²)? In the worst case (reverse-sorted input), every element must bubble all the way across the list. That's roughly n passes of n comparisons.

Why study it? Because it's the simplest sort to understand and trace on paper. It's also a cautionary tale — simplicity doesn't imply efficiency.

### Insertion sort — O(n²) worst, O(n) best, stable

Walk through the list left to right. For each element, slide it backward into its correct position among the already-sorted prefix.

Why is it O(n) on nearly-sorted input? Because each element is already close to its correct position, so the "slide backward" step barely moves anything.

Why does this matter? Because Timsort — Python's built-in sort — uses insertion sort on small sub-arrays. It turns out that for arrays under ~64 elements, insertion sort's low overhead beats merge sort's optimal asymptotics.

### Merge sort — O(n log n), stable, O(n) space

Split the array in half, recursively sort each half, then merge the two sorted halves. The merge step is the key: it walks through both halves simultaneously, always picking the smaller element.

Why O(n log n)? There are log₂(n) levels of splitting, and each level does O(n) total work merging.

Why O(n) space? Because the merge step needs a temporary buffer to hold the merged result. This is merge sort's main downside — it's not in-place.

Why stable? Because the merge step uses `<=` (not `<`) when comparing elements from the left half, so equal elements from the left half come before those from the right, preserving their original order.

### Quick sort — O(n log n) average, O(n²) worst, unstable

Pick a "pivot" element, partition the array into elements less than, equal to, and greater than the pivot, then recursively sort the less-than and greater-than partitions.

Why O(n²) worst case? If you consistently pick the smallest or largest element as pivot (e.g., always picking `xs[0]` on already-sorted input), one partition is empty and the other has n−1 elements. That gives you n levels instead of log n.

Why use it anyway? Because in practice (with random or median-of-three pivot selection), it's *very* fast — often faster than merge sort due to better cache locality and lower constant factors.

### Timsort — Python's `sorted()`

Timsort is a hybrid of merge sort and insertion sort, designed by Tim Peters in 2002 specifically for real-world data. It:

1. Identifies natural "runs" — consecutive elements that are already sorted (or reverse-sorted).
2. Extends short runs to a minimum length using insertion sort.
3. Merges runs using an optimized merge that exploits existing order.

Result: O(n) on already-sorted data, O(n log n) worst case, stable, and consistently fast on real-world inputs. It's the right answer in production. Implement sorts only to *learn*.

## Why these design choices

| Decision | Why | When to pick differently |
|---|---|---|
| Merge sort for guaranteed O(n log n) | No pathological inputs can degrade it | When O(n) extra space is unacceptable (use heapsort instead — O(n log n), O(1) space, but unstable and slower in practice) |
| Quick sort for speed in practice | Better cache locality, smaller constants | When worst-case matters (use merge sort or intro-sort, which falls back to heapsort after log n recursion depth) |
| Insertion sort for small arrays | Low overhead dominates at small n | When n is always large — but even then, hybrid sorts use insertion for small sub-arrays |
| Timsort for production | Exploits real-world patterns, stable, adaptive | When you need an unstable in-place sort with O(1) space (use heapsort or intro-sort) |

**The theoretical floor:** No comparison-based sort can do better than O(n log n) in the worst case. This is provable — there are Ω(n log n) leaves in the decision tree of comparisons. Non-comparison sorts (counting sort, radix sort) can beat this, but they require constraints on the data (integers in a known range).

## Production-quality code

```python
from typing import TypeVar
from collections.abc import MutableSequence

T = TypeVar("T")


def bubble_sort(xs: MutableSequence) -> MutableSequence:
    """O(n^2) stable sort. Educational only."""
    n = len(xs)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if xs[j] > xs[j + 1]:
                xs[j], xs[j + 1] = xs[j + 1], xs[j]
                swapped = True
        if not swapped:
            break
    return xs


def insertion_sort(xs: MutableSequence) -> MutableSequence:
    """O(n^2) worst, O(n) best (nearly sorted). Stable."""
    for i in range(1, len(xs)):
        key = xs[i]
        j = i - 1
        while j >= 0 and xs[j] > key:
            xs[j + 1] = xs[j]
            j -= 1
        xs[j + 1] = key
    return xs


def merge_sort(xs: list) -> list:
    """O(n log n) stable sort, O(n) auxiliary space."""
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left = merge_sort(xs[:mid])
    right = merge_sort(xs[mid:])
    return _merge(left, right)


def _merge(a: list, b: list) -> list:
    """Merge two sorted lists into one sorted list."""
    result: list = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def quick_sort(xs: list) -> list:
    """O(n log n) average, O(n^2) worst. Not stable.

    Uses median-of-three pivot selection to reduce worst-case likelihood.
    """
    if len(xs) <= 1:
        return xs

    # median-of-three pivot selection
    first, mid_val, last = xs[0], xs[len(xs) // 2], xs[-1]
    pivot = sorted([first, mid_val, last])[1]

    lo = [x for x in xs if x < pivot]
    eq = [x for x in xs if x == pivot]
    hi = [x for x in xs if x > pivot]
    return quick_sort(lo) + eq + quick_sort(hi)
```

## Security notes

- **Algorithmic complexity attacks on quick sort:** If an attacker controls the input and knows your pivot selection strategy, they can craft inputs that trigger O(n²) worst-case behavior. This is a real denial-of-service vector. Mitigation: use randomized pivot selection or intro-sort (which switches to heapsort after too much recursion).
- **Timing side channels:** If you sort sensitive data (like password hashes) and the sort time is observable, an attacker might infer information about the data. This is rare in practice but worth noting for security-critical systems.

## Performance notes

| Algorithm | Time (best) | Time (avg) | Time (worst) | Space | Stable |
|---|---|---|---|---|---|
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick sort | O(n log n) | O(n log n) | O(n²) | O(log n) avg stack | No |
| Timsort | O(n) | O(n log n) | O(n log n) | O(n) | Yes |
| Heapsort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |

**Practical benchmarks (rough, CPython, 10⁵ random ints):**

- Bubble sort: ~30 seconds
- Insertion sort: ~10 seconds
- Merge sort (Python): ~0.5 seconds
- Quick sort (Python): ~0.3 seconds
- `sorted()` (Timsort, C): ~0.01 seconds

That 30× gap between your Python merge sort and the built-in `sorted()` is why you should always use the built-in in production. It's implemented in C with optimizations you don't want to re-implement.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Quick sort is extremely slow on already-sorted input | Pivot is always `xs[0]` or `xs[-1]`, producing maximally unbalanced partitions | Use median-of-three or random pivot selection |
| 2 | `RecursionError` on large inputs with merge sort or quick sort | Python's default recursion limit is ~1000; deeply recursive sorts exceed it | Use `sys.setrecursionlimit()` cautiously, or convert to iterative (bottom-up merge sort) |
| 3 | Multi-key sort gives wrong order | Sorting by each key separately with an unstable sort | Use a stable sort with a tuple key: `sorted(xs, key=lambda x: (x.last, x.first))` |
| 4 | Mutating a list you don't own with `xs.sort()` | `sort()` is in-place; the caller's list is changed | Use `sorted(xs)` to create a new sorted list, leaving the original untouched |
| 5 | Merge sort uses `<` instead of `<=` in the merge step | Breaks stability — equal elements from the right half can leapfrog left-half elements | Always use `<=` when comparing left vs. right in a stable merge |

## Practice

**Warm-up.** Sort `[3, 1, 4, 1, 5]` using bubble sort by hand. Write down the state of the array after each pass, and count the total swaps.

<details><summary>Show solution</summary>

```
Pass 1: [1, 3, 1, 4, 5]  →  [1, 1, 3, 4, 5]  (3 swaps: 3↔1, 4↔1, no more)
  Detail: [3,1,4,1,5] → [1,3,4,1,5] → [1,3,1,4,5] → [1,1,3,4,5]  3 swaps
Pass 2: [1, 1, 3, 4, 5]  (0 swaps — swapped=False → early exit)
Total swaps: 3
```

</details>

**Standard.** Implement merge sort from scratch. Test it on a random list of 10,000 elements and verify the result matches `sorted()`.

<details><summary>Show solution</summary>

```python
import random

def merge_sort(xs):
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    left = merge_sort(xs[:mid])
    right = merge_sort(xs[mid:])
    return merge(left, right)

def merge(a, b):
    result, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result

data = [random.randint(0, 100_000) for _ in range(10_000)]
assert merge_sort(data) == sorted(data)
```

</details>

**Bug hunt.** A developer implements quick sort using `xs[0]` as the pivot. Their code works on random inputs but is extremely slow on already-sorted inputs. Why? What's the fix?

<details><summary>Show solution</summary>

When the input is already sorted and the pivot is `xs[0]` (the minimum), the partition produces:
- `lo = []` (nothing less than the minimum)
- `hi = xs[1:]` (everything else)

This means each recursive call only removes one element, giving n levels of recursion instead of log n. Total: O(n²).

Fix: use a random pivot (`pivot = xs[random.randint(0, len(xs)-1)]`) or median-of-three (`pivot = sorted([xs[0], xs[len(xs)//2], xs[-1]])[1]`).

</details>

**Stretch.** Implement a counting-inversions algorithm using merge sort. An inversion is a pair (i, j) where i < j but xs[i] > xs[j]. For `[2, 4, 1, 3, 5]`, the inversions are (2,1), (4,1), (4,3) — count = 3.

<details><summary>Show solution</summary>

```python
def count_inversions(xs):
    def sort_and_count(xs):
        if len(xs) <= 1:
            return xs, 0
        mid = len(xs) // 2
        left, left_inv = sort_and_count(xs[:mid])
        right, right_inv = sort_and_count(xs[mid:])
        merged, split_inv = merge_and_count(left, right)
        return merged, left_inv + right_inv + split_inv

    def merge_and_count(a, b):
        result, inversions = [], 0
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                result.append(a[i]); i += 1
            else:
                result.append(b[j]); j += 1
                inversions += len(a) - i
        result.extend(a[i:])
        result.extend(b[j:])
        return result, inversions

    return sort_and_count(xs)[1]

assert count_inversions([2, 4, 1, 3, 5]) == 3
assert count_inversions([5, 4, 3, 2, 1]) == 10  # reverse-sorted = max inversions
assert count_inversions([1, 2, 3, 4, 5]) == 0   # sorted = 0 inversions
```

</details>

**Stretch++.** Benchmark bubble sort, insertion sort, merge sort, quick sort, and Python's `sorted()` on 10⁵ random integers. Also test on already-sorted and reverse-sorted inputs. Present results in a table showing how each algorithm behaves on different input distributions.

<details><summary>Show solution</summary>

```python
import random
import time

def benchmark(sort_fn, data):
    copy = data[:]
    start = time.perf_counter()
    sort_fn(copy)
    return time.perf_counter() - start

n = 10_000  # use 10k for O(n^2) sorts; 100k for others
random_data = [random.randint(0, n) for _ in range(n)]
sorted_data = sorted(random_data)
reverse_data = sorted_data[::-1]

sorts = {
    "bubble": bubble_sort,
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "sorted()": sorted,
}

for name, fn in sorts.items():
    for label, data in [("random", random_data), ("sorted", sorted_data), ("reverse", reverse_data)]:
        t = benchmark(fn, data)
        print(f"{name:12s} | {label:8s} | {t:.4f}s")
```

Key observations: insertion sort shines on sorted input (O(n)). Naive quick sort degrades on sorted input. `sorted()` dominates everywhere.

</details>

## In plain terms (newbie lane)
If `Sorting` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Python's built-in sort algorithm is:
    (a) quicksort  (b) mergesort  (c) Timsort  (d) bubble sort

2. A stable sort:
    (a) preserves the relative order of equal elements  (b) crashes gracefully  (c) is always single-threaded  (d) uses O(1) space

3. Merge sort's complexity is:
    (a) O(n log n) time, O(n) auxiliary space  (b) O(n²) time  (c) O(log n) time  (d) O(n) time

4. Quick sort's worst-case complexity is:
    (a) O(n log n)  (b) O(n²)  (c) O(2ⁿ)  (d) O(n!)

5. Insertion sort is efficient when:
    (a) the input is always random  (b) the input is nearly sorted  (c) it's O(log n)  (d) it's unstable

**Short answer:**

6. When does the stability of a sort algorithm matter? Give a concrete example.
7. Why does Timsort use insertion sort for small runs instead of merge sort all the way down?

*Answers: 1-c, 2-a, 3-a, 4-b, 5-b, 6-When sorting by multiple keys sequentially — e.g., sort employees by last name, then by first name; stability ensures the first-name order is preserved within same last names, 7-Because insertion sort has lower constant overhead (no function call overhead, no auxiliary array allocation) and is faster than merge sort on small arrays due to cache locality and branch prediction.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-sorting — mini-project](mini-projects/04-sorting-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- The classic sorts (bubble, insertion, merge, quick) teach patterns you'll use beyond sorting: incremental building, divide-and-conquer, and partitioning.
- O(n log n) is the theoretical floor for comparison-based sorting. Merge sort guarantees it; quick sort achieves it on average.
- Stability matters when sorting by multiple keys. Timsort (Python's built-in) is stable, adaptive, and fast — use it in production.
- Implementing sorts teaches you to *think* about algorithms; calling `sorted()` is what you do in production code.

## Further reading

- Tim Peters' original Timsort description: [bugs.python.org/file4451/timsort.txt](https://bugs.python.org/file4451/timsort.txt).
- *Introduction to Algorithms* (CLRS), chapters 2 (insertion sort), 7 (quicksort), 8 (sorting lower bound).
- Visualizations: [visualgo.net/en/sorting](https://visualgo.net/en/sorting) — watch each algorithm step by step.
- Next: [Exponential Time](05-exponential-time.md).
