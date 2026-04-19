# Chapter 04 — Recursion

> "Recursion is a function calling itself. It's the natural expression for anything self-similar: trees, nested data, parsing, and divide-and-conquer algorithms."

## Learning objectives

By the end of this chapter you will be able to:

- Write a recursive function with a correct base case and recursive step.
- Convert a simple recursion to iteration (and know when to bother).
- Explain Python's recursion limit, why tail-call optimization doesn't exist in CPython, and what to do about it.
- Apply memoization to recursive functions with overlapping subproblems.
- Recognize when recursion is the wrong tool and iteration is clearer.

## Prerequisites & recap

- [Functions](../01-python/03-functions.md) — defining and calling functions, the call stack.
- [Pure functions](03-pure-functions.md) — why side-effect-free functions compose well.

## The simple version

A recursive function is a function that calls itself to solve a smaller version of the same problem. Every recursive function needs two things: a *base case* that stops the recursion, and a *recursive step* that makes the problem smaller and calls itself again. Without the base case, you recurse forever and crash.

Recursion maps naturally to data that is itself recursive: trees, nested lists, file systems, JSON, ASTs. For flat sequences, a loop is usually simpler and faster in Python. The key is matching the tool to the shape of the data.

## Visual flow

```
  factorial(4)
  |
  +---> 4 * factorial(3)
              |
              +---> 3 * factorial(2)
                          |
                          +---> 2 * factorial(1)
                                      |
                                      +---> return 1  (base case)
                                 return 2 * 1 = 2
                          return 3 * 2 = 6
              return 4 * 6 = 24

  Each call adds a frame to the stack.
  The base case triggers unwinding.

  Tree walk (natural recursion):

       A
      / \
     B   C
    /
   D

  walk(A) -> visit A, walk(B), walk(C)
  walk(B) -> visit B, walk(D)
  walk(D) -> visit D (no children = base case)
  walk(C) -> visit C (no children = base case)

  Caption: Recursion mirrors the structure of the data.
  Trees are *the* canonical recursion use case.
```

## Concept deep-dive

### Anatomy of a recursive function

Every recursive function has exactly two parts:

1. **Base case** — returns a result without recursing. This is your exit condition.
2. **Recursive step** — calls itself on a *smaller* problem and combines the result.

```python
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

Without a base case, you get infinite recursion and a `RecursionError`. Without the problem getting *smaller*, you get the same thing. Both conditions must hold.

### Tree walks — recursion's natural home

Trees are inherently recursive: a tree is a node with zero or more subtrees. The recursive structure of the data maps directly to a recursive function:

```python
def walk(node, visit):
    visit(node.value)
    for child in node.children:
        walk(child, visit)
```

This is why parsers, file-system traversals, and DOM manipulations are almost always recursive. The code mirrors the data shape.

### Recursion vs. iteration

Every recursion can be rewritten iteratively, often with an explicit stack. In CPython, iteration is:

- **Faster** — no call-frame overhead per step.
- **Unbounded** — not limited by the recursion limit.

Recursion is often **clearer** for naturally recursive data (trees, ASTs, nested structures). For flat sequences (summing a list, finding a max), a loop or built-in is almost always better.

The decision rule: does the data have recursive structure? Use recursion. Is it a flat sequence? Use iteration.

### Python has no tail-call optimization

In languages like Scheme or Haskell, a *tail-recursive* function (where the recursive call is the last operation) can be optimized to run in O(1) stack space. Python deliberately does not do this. Guido van Rossum has explained why: it breaks tracebacks, which are essential for debugging.

The default recursion limit is ~1000 frames:

```python
import sys
sys.getrecursionlimit()   # 1000
```

You can raise it with `sys.setrecursionlimit()`, but that's a band-aid. For deep structures, convert to an explicit stack:

```python
def walk_iterative(root):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node.value
        stack.extend(reversed(node.children))
```

This handles trees of any depth, uses O(depth) memory on the explicit stack, and never hits the recursion limit.

### Memoization for overlapping subproblems

Naive recursive Fibonacci recalculates the same values exponentially:

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`fib(5)` calls `fib(3)` twice, `fib(2)` three times, and so on. The time complexity is O(2^n).

Adding `@functools.cache` stores each result and turns O(2^n) into O(n):

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

This works because `fib` is pure — same input always gives the same output. You'd never memo a function that reads the clock or a database.

### Mutual recursion

Two functions can call each other:

```python
def is_even(n):
    return True if n == 0 else is_odd(n - 1)

def is_odd(n):
    return False if n == 0 else is_even(n - 1)
```

This is elegant but Python-unfriendly for large `n` — you'll blow the stack quickly. In real code, use `n % 2 == 0`. Mutual recursion shows up more practically in parsers and state machines.

## Why these design choices

**Why doesn't Python add TCO?** Because Python values debuggability over optimization. Full tracebacks showing every recursive call are immensely useful when things go wrong. TCO would collapse those frames, making bugs harder to find.

**When is recursion the right choice?** When the data is recursive (trees, graphs, nested JSON) and the depth is bounded. A filesystem tree might be 20 levels deep — well within the limit. A linked list of 100,000 nodes is not.

**When should you avoid recursion?** For flat iteration (loops over lists), deep linear structures (linked lists, long chains), and any case where you know the depth could exceed ~1000. Convert to an explicit stack or iterative solution.

**Memoization trade-off:** You trade memory for speed. `@cache` grows without bound. For production, use `@lru_cache(maxsize=...)` to cap memory.

## Production-quality code

```python
from __future__ import annotations
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, Iterator


@dataclass
class TreeNode:
    value: str
    children: list[TreeNode] = field(default_factory=list)


def walk_recursive(node: TreeNode, visit: Callable[[str], None]) -> None:
    """Recursive DFS. Clean for shallow trees."""
    visit(node.value)
    for child in node.children:
        walk_recursive(child, visit)


def walk_iterative(root: TreeNode) -> Iterator[str]:
    """Iterative DFS with explicit stack. Safe for any depth."""
    stack: list[TreeNode] = [root]
    while stack:
        node = stack.pop()
        yield node.value
        stack.extend(reversed(node.children))


def deep_sum(xs: list) -> int | float:
    """Sum a nested list of numbers, any depth."""
    total = 0
    for x in xs:
        total += deep_sum(x) if isinstance(x, list) else x
    return total


def flatten(xs: list) -> list:
    """Flatten an arbitrarily nested list."""
    result: list = []
    for x in xs:
        if isinstance(x, list):
            result.extend(flatten(x))
        else:
            result.append(x)
    return result


@lru_cache(maxsize=512)
def fib(n: int) -> int:
    """Fibonacci with bounded memoization."""
    if n < 0:
        raise ValueError(f"fib undefined for negative n: {n}")
    return n if n < 2 else fib(n - 1) + fib(n - 2)


# --- Usage ---
tree = TreeNode("A", [
    TreeNode("B", [TreeNode("D")]),
    TreeNode("C"),
])

assert list(walk_iterative(tree)) == ["A", "B", "D", "C"]
assert deep_sum([1, [2, [3, 4], 5], 6]) == 21
assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]
assert fib(10) == 55
```

## Security notes

- **Stack exhaustion as DoS:** If your server processes user-supplied recursive data (nested JSON, deeply nested XML), an attacker can send deeply nested input to trigger `RecursionError` and crash the process. Always validate nesting depth before recursing on untrusted input, or use iterative processing.
- **`sys.setrecursionlimit` dangers:** Raising the recursion limit too high can cause a segfault (C stack overflow) rather than a clean Python error. Don't use it as a production fix.

## Performance notes

- **Call overhead:** Each recursive call in CPython creates a new frame object (~100–200 ns overhead). For a million-element flat list, a loop is dramatically faster than recursion.
- **Memoized Fibonacci:** Without `@cache`, `fib(30)` makes ~2.7 million calls. With `@cache`, it makes 31.
- **Explicit stack vs. recursion:** An explicit stack avoids frame creation overhead but adds list append/pop overhead. For trees, the difference is small. For deep linear recursion (>1000 levels), the explicit stack is the only option.
- **`@cache` vs. `@lru_cache`:** `@cache` is unbounded — great for development, risky for long-running servers. `@lru_cache(maxsize=N)` evicts old entries.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | `RecursionError: maximum recursion depth exceeded` | Missing or wrong base case | Ensure the base case covers all termination conditions. Trace through with small input to verify. |
| 2 | Function recurses but the problem doesn't get smaller | Recursive step doesn't reduce toward the base case (e.g., `f(n)` calls `f(n)`) | Verify each recursive call passes a strictly smaller/simpler argument. |
| 3 | `fib(40)` takes forever | Exponential blowup from overlapping subproblems without memoization | Add `@functools.cache` or `@lru_cache`. Or convert to iterative with a loop. |
| 4 | Deep tree walk crashes with `RecursionError` | Tree depth exceeds Python's recursion limit (~1000) | Convert to iterative traversal with an explicit stack. |
| 5 | Recursive `flatten` works but is quadratic | Using `result = result + flatten(x)` (creates new list each time) instead of `.extend()` | Use `result.extend(flatten(x))` to avoid O(n^2) list concatenation. |

## Practice

**Warm-up.** Write a recursive `power(base, exp)` for positive integers. `power(2, 10)` → `1024`.

<details><summary>Solution</summary>

```python
def power(base, exp):
    if exp == 0:
        return 1
    return base * power(base, exp - 1)

assert power(2, 10) == 1024
assert power(5, 0) == 1
```

</details>

**Standard.** Flatten an arbitrarily nested list of ints: `flatten([1, [2, [3, 4], 5], 6])` → `[1, 2, 3, 4, 5, 6]`.

<details><summary>Solution</summary>

```python
def flatten(xs):
    result = []
    for x in xs:
        if isinstance(x, list):
            result.extend(flatten(x))
        else:
            result.append(x)
    return result

assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]
assert flatten([]) == []
assert flatten([1, 2, 3]) == [1, 2, 3]
```

</details>

**Bug hunt.** Why does `fib(100)` take forever without `@cache`?

<details><summary>Solution</summary>

Without memoization, `fib(n)` branches into two recursive calls at each level, creating O(2^n) total calls. Most are redundant — `fib(50)` is recalculated billions of times. `@cache` stores each result on first computation and returns the cached value for subsequent calls, reducing total calls to O(n).

</details>

**Stretch.** Write `reverse_list(xs)` recursively without using slicing or built-in `reversed`.

<details><summary>Solution</summary>

```python
def reverse_list(xs):
    if len(xs) <= 1:
        return list(xs)
    return [xs[-1]] + reverse_list(xs[:-1])

# More efficient with an accumulator:
def reverse_list(xs, acc=None):
    if acc is None:
        acc = []
    if not xs:
        return acc
    return reverse_list(xs[1:], [xs[0]] + acc)

assert reverse_list([1, 2, 3, 4]) == [4, 3, 2, 1]
```

</details>

**Stretch++.** Convert the recursive tree `walk` to an iterative version using an explicit stack. Verify that both produce the same output for a test tree.

<details><summary>Solution</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Node:
    value: str
    children: list = field(default_factory=list)

def walk_recursive(node, acc=None):
    if acc is None:
        acc = []
    acc.append(node.value)
    for child in node.children:
        walk_recursive(child, acc)
    return acc

def walk_iterative(root):
    result = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.value)
        stack.extend(reversed(node.children))
    return result

tree = Node("A", [Node("B", [Node("D")]), Node("C")])
assert walk_recursive(tree) == walk_iterative(tree) == ["A", "B", "D", "C"]
```

</details>

## In plain terms (newbie lane)
If `Recursion` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A recursive function must have:
    (a) A base case
    (b) Tail-call optimization
    (c) A loop inside it
    (d) A global variable

2. Python's default recursion limit is approximately:
    (a) Unbounded
    (b) ~1000 frames
    (c) 100 frames
    (d) 10,000 frames

3. Memoizing `fib` changes its complexity from:
    (a) O(2^n) to O(n)
    (b) O(n) to O(1)
    (c) O(n^2) to O(n log n)
    (d) No change — memoization only helps readability

4. Does Python support tail-call optimization?
    (a) Always
    (b) With a special decorator
    (c) No — deliberately omitted
    (d) Only with `sys.settail()`

5. Tree traversals are best expressed as:
    (a) Flat loops only
    (b) Recursion only
    (c) Either recursion or explicit stack — recursion is often clearer
    (d) BFS only

**Short answer:**

6. Name one problem where recursion is clearer than iteration.
7. Why doesn't Python implement tail-call optimization?

*Answers: 1-a, 2-b, 3-a, 4-c, 5-c, 6. Tree traversal (parsing, filesystem walking, nested JSON processing, AST evaluation) — any problem where the data structure is inherently recursive. 7. Guido van Rossum decided against it because TCO collapses stack frames, making tracebacks less informative and debugging harder. Python prioritizes debuggability over this optimization.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-recursion — mini-project](mini-projects/04-recursion-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Every recursive function needs a base case (to stop) and a recursive step (that reduces the problem).
- Python lacks tail-call optimization — the recursion limit is ~1000 frames. For deep structures, convert to an explicit stack.
- Memoize recursive functions with overlapping subproblems using `@functools.cache` or `@lru_cache`.
- Use recursion for recursive data (trees, nested structures); use iteration for flat sequences.

## Further reading

- *Structure and Interpretation of Computer Programs*, Chapter 1 — the classic treatment of recursion and iteration.
- Python docs: [`sys.getrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.getrecursionlimit).
- Guido van Rossum, [*Tail Recursion Elimination*](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html) — why Python doesn't do TCO.
- Next: [Function transformations](05-function-transformations.md).
