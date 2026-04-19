# Chapter 03 — Big-O Analysis

> "Big-O is how engineers talk about 'how fast' without counting nanoseconds."

## Learning objectives

By the end of this chapter you will be able to:

- Compute the Big-O of simple loops, nested loops, and divide-and-conquer recurrences.
- Distinguish Big-O (upper bound), Big-Ω (lower bound), and Big-Θ (tight bound).
- Analyze both time and space complexity of a function.
- Recognize the common complexity classes: O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ), O(n!).
- Explain amortized analysis with a concrete example.

## Prerequisites & recap

- [Chapter 02 — Math](02-math.md) — logarithms, series sums.

## The simple version

Big-O notation answers a simple question: "as my input gets bigger, how much more work does my code do?" It deliberately ignores constants and small terms because those don't change the *shape* of the growth curve. An algorithm that does 3n + 7 operations and one that does n + 1000 are both O(n) — they both grow linearly. But an algorithm that does n² operations is a fundamentally different beast, because doubling the input *quadruples* the work.

Think of Big-O as a speed limit sign for your code. It doesn't tell you the exact speed you're driving — it tells you the maximum speed the road allows. An O(n²) algorithm *might* be fast on small inputs, but the sign warns you: "this road gets very slow as traffic increases."

## Visual flow

```
  Growth rates (n = input size, operations on y-axis)

  ops
   |
   |                                                  * O(n!)
   |                                            *
   |                                      *           * O(2^n)
   |                                *
   |                          *
   |                    * . . . . . . . . . . . .     * O(n^2)
   |              *  . .
   |          * .  .                                  * O(n log n)
   |        *.  .
   |      *. .                                        * O(n)
   |    *..
   |  *:                                              * O(log n)
   | *
   |*.............................................. .. * O(1)
   +---------------------------------------------------> n

  The gap between classes widens fast. By n=1000, O(n^2) does
  1,000,000 ops while O(n log n) does ~10,000.
```
*Figure 3-1: Common complexity classes. Vertical axis is work; horizontal is input size.*

## Concept deep-dive

### The formal-ish definition

`f(n) = O(g(n))` if and only if there exist constants `c > 0` and `n₀ ≥ 0` such that `f(n) ≤ c · g(n)` for all `n ≥ n₀`.

Translation: past some point, `f` grows no faster than a constant times `g`. You're saying "I don't care about startup costs or constant factors — just tell me the *shape* of the growth."

**Three siblings you should know:**

| Notation | Meaning | Analogy |
|---|---|---|
| **O(g)** | Upper bound — f grows *at most* as fast as g | "at most this fast" |
| **Ω(g)** | Lower bound — f grows *at least* as fast as g | "at least this fast" |
| **Θ(g)** | Tight bound — f grows *exactly* as fast as g (up to constants) | "exactly this fast" |

In practice, engineers say "O" when they mean "Θ." When you say "merge sort is O(n log n)," you really mean it's Θ(n log n) — it's *always* n log n, not just "at most." This is sloppy but universal, so be aware.

### Rules of thumb

These four rules handle 90% of complexity analysis:

1. **Drop constants:** `3n + 2 = O(n)`. The 3 and 2 don't affect the growth *shape*.
2. **Drop non-dominant terms:** `n² + n = O(n²)`. As n grows, the n² term dominates.
3. **Nested loops multiply:** A loop over n inside a loop over n → O(n²). A loop over n inside a loop over m → O(n·m).
4. **Halving the problem → log:** If each step cuts the input in half, you get a log n factor.

### Why drop constants?

Because Big-O is about *scaling behavior*, not absolute speed. An algorithm that does 100n operations is faster than one doing n² once n > 100. On modern systems where n can easily be millions, the growth rate matters far more than the constant factor. That said, constants *do* matter in practice — an O(n) algorithm with a constant of 10⁹ is slower than O(n²) for all practical inputs. Big-O is a tool, not a religion.

### Common complexity classes

| Class | Name | Example | What it feels like |
|---|---|---|---|
| O(1) | Constant | dict lookup, stack push | Instant regardless of size |
| O(log n) | Logarithmic | Binary search | Barely notices input growth |
| O(n) | Linear | Scan a list, sum elements | Proportional to input |
| O(n log n) | Linearithmic | Merge sort, Python `sorted` | Slightly worse than linear |
| O(n²) | Quadratic | Bubble sort, pairwise comparison | Starts hurting at n > 10⁴ |
| O(2ⁿ) | Exponential | Subset enumeration | Intractable past n ≈ 25 |
| O(n!) | Factorial | Permutation enumeration | Intractable past n ≈ 12 |

### Time vs. space

**Time complexity** counts operations. **Space complexity** counts extra memory beyond the input.

- Merge sort: O(n log n) time, O(n) auxiliary space (for the merge buffer).
- In-place sorts (like heapsort): O(n log n) time, O(1) auxiliary space.
- Recursive algorithms use O(depth) stack space, which is easy to forget.

Why does space matter? Because memory is finite and shared. An algorithm that allocates O(n²) memory for n = 100,000 needs ~40 GB. Your server doesn't have that. Space complexity is just as important as time — sometimes more so, because OOM kills are harder to debug than slowness.

### Amortized analysis

Sometimes a single operation is occasionally slow, but averaged over many operations it's fast. The classic example: Python list `append`.

- Most appends are O(1) — just write to the next slot.
- Occasionally, the internal array is full and Python allocates a new array of ~1.125× the size, copies everything over — O(n).
- But that expensive resize happens rarely. Spread the cost over n appends and each one averages out to O(1).

This is **amortized O(1)**. It doesn't mean every single append is O(1) — it means the *average* over a sequence of appends is O(1). The distinction matters for latency-sensitive systems where a single slow operation can cause a timeout.

## Why these design choices

**Why use Big-O instead of benchmarking?** Because benchmarks are machine-specific and input-specific. Big-O gives you a machine-independent prediction of how an algorithm *scales*. It tells you "if I double my users, will my response time double (O(n)) or quadruple (O(n²))?" — which is exactly the question you need to answer during system design.

**When does Big-O mislead?** When the constants are enormous, when inputs are always small, or when the analysis hides important factors (like cache behavior). An O(n) algorithm with terrible cache locality can be slower than an O(n log n) algorithm that's cache-friendly. Use Big-O for architecture decisions; use benchmarks for micro-optimization.

**Alternatives:** In competitive programming, you sometimes count exact operations. In systems programming, you care about cache lines and branch prediction. In distributed systems, you care about network round-trips more than CPU ops. Big-O is the starting point, not the final word.

## Production-quality code

```python
"""Examples demonstrating different complexity classes."""

from typing import Sequence


def constant_lookup(d: dict, key: str) -> object:
    """O(1) average — hash table lookup."""
    return d.get(key)


def linear_scan(xs: Sequence[int], target: int) -> bool:
    """O(n) — must check every element in the worst case."""
    for x in xs:
        if x == target:
            return True
    return False


def has_duplicate_pair(xs: Sequence[int]) -> bool:
    """O(n) with O(n) space — using a set trades space for time.

    The naive O(n^2) approach compares all pairs. This approach
    checks membership in a set, which is O(1) average per lookup.
    """
    seen: set[int] = set()
    for x in xs:
        if x in seen:
            return True
        seen.add(x)
    return False


def all_pairs(xs: Sequence[int]) -> list[tuple[int, int]]:
    """O(n^2) — every element paired with every other."""
    pairs = []
    n = len(xs)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((xs[i], xs[j]))
    return pairs


def binary_search_count(xs: Sequence[int], target: int) -> int:
    """O(log n) — returns number of comparisons made."""
    lo, hi = 0, len(xs) - 1
    comparisons = 0
    while lo <= hi:
        comparisons += 1
        mid = lo + (hi - lo) // 2
        if xs[mid] == target:
            return comparisons
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return comparisons
```

## Security notes

N/A — Big-O analysis is a mathematical framework, not executable code with attack surface. However, understanding complexity *is* security-relevant: algorithmic complexity attacks exploit worst-case behavior (e.g., hash flooding to trigger O(n²) hash table operations). Understanding Big-O helps you recognize and defend against these attacks.

## Performance notes

| Input size (n) | O(log n) | O(n) | O(n log n) | O(n²) |
|---|---|---|---|---|
| 100 | 7 | 100 | 664 | 10,000 |
| 1,000 | 10 | 1,000 | 9,966 | 1,000,000 |
| 10,000 | 13 | 10,000 | 132,877 | 100,000,000 |
| 100,000 | 17 | 100,000 | 1,660,964 | 10,000,000,000 |
| 1,000,000 | 20 | 1,000,000 | 19,931,569 | 1,000,000,000,000 |

**Rule of thumb for Python:** A modern machine does roughly 10⁷–10⁸ simple Python operations per second. So:

- O(n) at n = 10⁶ → ~0.1 seconds. Fine.
- O(n²) at n = 10⁶ → ~10¹² ops → hours. Not fine.
- O(n log n) at n = 10⁶ → ~2×10⁷ ops → ~0.2 seconds. Fine.

This is why O(n²) algorithms that "work fine in testing" (n = 100) explode in production (n = 100,000).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Claiming `x in my_list` is O(1) | Confusing lists with sets/dicts — `x in list` is O(n) | Use `set` or `dict` for O(1) membership testing |
| 2 | "My O(n²) solution works fine" | Only tested with n ≤ 100; production has n = 50,000 | Always test with production-scale inputs during development |
| 3 | Analyzing best-case but hitting worst-case in production | E.g., assuming quick sort is always O(n log n) | Reason about worst-case complexity unless you can guarantee input distribution |
| 4 | Ignoring space complexity | Algorithm works but OOM-kills on large inputs due to O(n²) memory | Track both time and space; prefer in-place algorithms when memory is tight |
| 5 | Counting `print` statements as the dominant operation | Focusing on I/O in analysis instead of the operation that scales | Count the operation that grows with input size — usually comparisons, additions, or lookups |

## Practice

**Warm-up.** What's the time complexity of `sum([x * x for x in xs])`? Break it down step by step.

<details><summary>Show solution</summary>

- The list comprehension iterates over `xs` (n elements): O(n).
- Each iteration does one multiplication: O(1).
- `sum()` iterates over the resulting list (n elements): O(n).
- Total: O(n) + O(n) = O(n).

</details>

**Standard.** Analyze the time complexity of this code:

```python
for i in range(n):
    j = 1
    while j < n:
        j *= 2
```

<details><summary>Show solution</summary>

- Outer loop: n iterations.
- Inner loop: `j` starts at 1 and doubles each iteration until it reaches n → log₂(n) iterations.
- Total: n × log₂(n) = **O(n log n)**.

</details>

**Bug hunt.** A developer says "`x in my_dict` is O(n) because the dict has n items." Is this correct? Why or why not?

<details><summary>Show solution</summary>

Incorrect. `x in dict` is O(1) *average* because dictionaries use hash tables. The hash of `x` is computed (O(1) for common types), then a single bucket is checked. Only in pathological cases (all keys hash to the same bucket) does it degrade to O(n). In contrast, `x in list` *is* O(n) because lists require a linear scan.

</details>

**Stretch.** Analyze the *space* complexity of recursive factorial vs. iterative factorial. Which uses more memory, and why?

<details><summary>Show solution</summary>

```python
def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

- **Recursive:** O(n) space — each call adds a stack frame, and there are n calls before reaching the base case.
- **Iterative:** O(1) space — only a fixed number of variables regardless of n.

Both are O(n) time, but the recursive version risks `RecursionError` for large n (Python's default limit is ~1000).

</details>

**Stretch++.** Derive merge sort's O(n log n) complexity using the Master Theorem. State which case of the theorem applies and why.

<details><summary>Show solution</summary>

Merge sort's recurrence: `T(n) = 2·T(n/2) + O(n)`

Master Theorem: For `T(n) = a·T(n/b) + O(n^d)`:
- a = 2 (two subproblems)
- b = 2 (each half the size)
- d = 1 (linear merge step)

Compute: `log_b(a) = log₂(2) = 1 = d`

This is **Case 2** of the Master Theorem (a = b^d): T(n) = O(n^d · log n) = **O(n log n)**.

Intuitively: there are log₂(n) levels in the recursion tree, and each level does O(n) total work across all subproblems.

</details>

## In plain terms (newbie lane)
If `Big O` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. O(n) + O(n²) simplifies to:
    (a) O(n)  (b) O(n²)  (c) O(n³)  (d) O(n + n²)

2. Dropping constants is valid because:
    (a) they're always small  (b) Big-O characterizes asymptotic growth, not absolute speed  (c) Python is fast enough  (d) it's just a convention

3. Binary search complexity:
    (a) O(n)  (b) O(log n)  (c) O(1)  (d) O(n log n)

4. "Amortized O(1) for list append" means:
    (a) every append is O(1)  (b) the average cost per append is O(1), even though rare resizes are O(n)  (c) O(log n)  (d) it's impossible to achieve

5. The difference between O and Θ:
    (a) they're identical  (b) Θ is a tight bound; O is only an upper bound  (c) Θ is a lower bound  (d) they're just different Greek letters

**Short answer:**

6. Why is it valid to drop non-dominant terms in Big-O?
7. When do constant factors matter in practice, despite Big-O ignoring them?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b, 6-Because as n→∞ the dominant term grows so much faster that the others become negligible (e.g., n² dwarfs n for large n), 7-When inputs are always small (n < 1000), when comparing algorithms of the same Big-O class, or when constant factors represent expensive operations like network I/O or disk seeks.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-big-o — mini-project](mini-projects/03-big-o-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Big-O describes how an algorithm's work scales with input size — not how fast it runs in absolute terms. Drop constants and non-dominant terms to focus on growth shape.
- The common classes (O(1), O(log n), O(n), O(n log n), O(n²)) cover almost every algorithm you'll encounter. Know what each one *feels like* at scale.
- Track space complexity alongside time — OOM kills are harder to debug than slowness.
- Amortized analysis spreads occasional expensive operations across many cheap ones, giving you O(1) average for operations like list append.

## Further reading

- *Introduction to Algorithms* (CLRS), chapter 3 — the formal treatment of asymptotic notation.
- *The Algorithm Design Manual*, Skiena, chapter 2 — practical approach to algorithm analysis.
- Big-O Cheat Sheet: [bigocheatsheet.com](https://www.bigocheatsheet.com/) — quick reference for common operations.
- Next: [Sorting Algorithms](04-sorting.md).
