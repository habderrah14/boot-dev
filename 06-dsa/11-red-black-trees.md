# Chapter 11 — Red-Black Trees

> "Paint it red, paint it black — what matters is that every path sees the same number of dark nodes."

## Learning objectives

By the end of this chapter you will be able to:

- State the five red-black tree invariants and explain why they guarantee O(log n) height.
- Perform left and right rotations on paper and in code.
- Trace, at a high level, how insertion and deletion restore the invariants.
- Identify where red-black trees live in real systems and know when to reach for one in Python.

## Prerequisites & recap

- [Binary trees & BSTs](10-binary-trees.md) — you should be comfortable with
  BST insert, delete, and the concept of tree height.

## The simple version

A plain BST can degenerate into a linked list if you feed it sorted data.
A red-black tree prevents that by assigning every node a color — red or
black — and enforcing a handful of rules about those colors. Whenever an
insert or delete breaks a rule, the tree fixes itself with *rotations*
(local rewiring of a few pointers) and *recoloring*. The rules guarantee
that the longest path from root to leaf is never more than twice the shortest,
which keeps the height at O(log n) and every operation fast.

You almost never implement a red-black tree from scratch. But understanding
how they work tells you *why* `std::map`, Java's `TreeMap`, and the Linux
kernel's scheduler all reach for this specific structure: it's the sweet spot
between strictness (AVL) and simplicity (plain BST).

## Visual flow

```
  A valid red-black tree (B = black, R = red):

              10(B)
            /       \
         5(R)       15(R)
        /   \       /   \
      3(B)  7(B) 12(B) 20(B)

  Every root-to-NIL path has exactly 2 black nodes
  (the "black-height" is 2, not counting the root
  or NIL sentinels, depending on convention).

  Left-rotate at X:          Right-rotate at Y:

       X              Y           Y            X
      / \            / \         / \          / \
     A   Y    →     X   C      X   C   →    A   Y
        / \        / \        / \              / \
       B   C      A   B     A   B            B   C

  Key property: BST ordering is preserved.
```

## Concept deep-dive

### The five invariants

1. **Every node is red or black.**
2. **The root is black.**
3. **Every leaf (NIL sentinel) is black.** (NIL nodes are implicit "empty"
   children — they simplify the logic.)
4. **A red node's children are both black.** (No two reds in a row on any
   path.)
5. **For every node, all paths from that node to descendant NILs contain the
   same number of black nodes** — the "black-height."

**Why these five rules guarantee O(log n) height.** Rule 4 says you can never
have two consecutive reds, so on any root-to-leaf path, at least half the
nodes are black. Rule 5 says every path has the same number of black nodes.
Together, the longest possible path (alternating red-black) is at most 2×
the shortest (all-black). If the shortest path has length *b* (the
black-height), the longest is ≤ 2b, and since there are n nodes total, you
can show b ≤ log₂(n + 1). Therefore h ≤ 2·log₂(n + 1) = O(log n).

### Rotations — the atomic repair operation

A rotation rewires three nodes and their subtrees without violating BST
ordering. It takes O(1) — just a few pointer swaps. Left-rotation makes a
node's right child the new parent; right-rotation does the symmetric thing.

Rotations alone don't fix color violations — they're always paired with
recoloring.

### Insertion

1. Insert the new node as in a normal BST and color it **red** (red is "less
   disruptive" — it doesn't change any path's black-height).
2. **Fix-up:** if the new node's parent is red, you have a red-red violation
   (rule 4). There are three cases (symmetric on left/right):
   - **Uncle is red:** recolor parent and uncle black, grandparent red; move
     the problem up.
   - **Uncle is black, node is an inner child:** rotate the node up to make
     it an outer child (reduces to the next case).
   - **Uncle is black, node is an outer child:** rotate the grandparent and
     recolor.
3. Recolor the root black (rule 2).

At most 2 rotations per insert; O(log n) recoloring steps.

### Deletion

Deletion is the harder operation. When you remove or move a black node, you
change a path's black-height, potentially violating rule 5. The fix-up has
six cases (symmetric), involving rotations and recoloring. Most textbooks
(and this book) don't ask you to memorize the cases — they ask you to
understand *why* the fix-up works: each case either resolves the violation
or transforms it into a simpler case, converging in O(log n) steps.

### RB vs. AVL — when to pick which

| Property | Red-black | AVL |
|---|---|---|
| Balance strictness | Loose (height ≤ 2·log n) | Strict (height ≤ 1.44·log n) |
| Rotations per insert | ≤ 2 | ≤ 2 |
| Rotations per delete | ≤ 3 | O(log n) in worst case |
| Lookup speed | Slightly slower (taller tree) | Slightly faster (shorter tree) |
| Best for | Write-heavy workloads | Read-heavy workloads |

In practice, the difference is small. Red-black trees won the popularity
contest because of slightly cheaper mutations.

### Where you see them

- **C++** `std::map`, `std::set`, `std::multimap` — the ISO standard
  requires sorted associative containers; most implementations use red-black
  trees.
- **Java** `TreeMap`, `TreeSet`.
- **Linux kernel** — the scheduler's CFS (Completely Fair Scheduler) uses a
  red-black tree to track runnable processes by virtual runtime.
- **Python** — no built-in red-black tree. For sorted containers, use the
  third-party `sortedcontainers` library (which uses a B-tree-like
  structure internally) or `bisect` for binary search on sorted lists.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| Red-black over AVL | Fewer rotations on delete, slightly taller tree | AVL when reads vastly outnumber writes (databases' index lookup path) |
| Red-black over skip list | Deterministic worst-case vs. probabilistic | Skip lists when you want simpler concurrent implementations |
| NIL sentinels | Eliminates edge cases (leaf checks) at cost of a shared sentinel node | Some implementations use `None` and add explicit checks — saves one allocation |
| Coloring new node red | Doesn't change black-height → fewer fix-ups | Always — there's no advantage to inserting black |

## Production-quality code

Implementing a full red-black tree is a 200+ line exercise that's
instructive once but error-prone for production. In Python, you should use
`sortedcontainers.SortedList` for the same O(log n) sorted operations.

Below is a rotation implementation and a demonstration of the practical
alternative:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Color(Enum):
    RED = "R"
    BLACK = "B"


@dataclass
class RBNode:
    value: int
    color: Color = Color.RED
    left: Optional[RBNode] = None
    right: Optional[RBNode] = None
    parent: Optional[RBNode] = None


def left_rotate(root: Optional[RBNode], x: RBNode) -> Optional[RBNode]:
    """Left-rotate subtree rooted at x. Returns the (possibly new) tree root."""
    y = x.right
    if y is None:
        raise ValueError("Cannot left-rotate: no right child")

    x.right = y.left
    if y.left is not None:
        y.left.parent = x

    y.parent = x.parent
    if x.parent is None:
        root = y
    elif x is x.parent.left:
        x.parent.left = y
    else:
        x.parent.right = y

    y.left = x
    x.parent = y
    return root


def right_rotate(root: Optional[RBNode], y: RBNode) -> Optional[RBNode]:
    """Right-rotate subtree rooted at y. Returns the (possibly new) tree root."""
    x = y.left
    if x is None:
        raise ValueError("Cannot right-rotate: no left child")

    y.left = x.right
    if x.right is not None:
        x.right.parent = y

    x.parent = y.parent
    if y.parent is None:
        root = x
    elif y is y.parent.left:
        y.parent.left = x
    else:
        y.parent.right = x

    x.right = y
    y.parent = x
    return root


# -----------------------------------------------------------------
# In practice, use sortedcontainers for O(log n) sorted operations:
# -----------------------------------------------------------------

def sorted_container_demo() -> None:
    from sortedcontainers import SortedList

    sl = SortedList([5, 1, 8, 3])
    sl.add(2)
    print(list(sl))              # [1, 2, 3, 5, 8]
    print(sl.bisect_left(3))     # 2  (index where 3 starts)
    sl.discard(5)
    print(list(sl))              # [1, 2, 3, 8]
```

## Security notes

N/A — red-black trees are in-process sorted containers. The indirect security
relevance is that **unbalanced BSTs are vulnerable to algorithmic complexity
attacks** (adversary feeds sorted input → O(n) operations). Red-black trees
defend against this by construction — every operation stays O(log n)
regardless of input order.

## Performance notes

All operations — insert, delete, search — are O(log n) worst-case. The
constant factors are:

- **2 rotations max per insert, 3 per delete.** Each rotation is O(1) — a
  few pointer swaps.
- **Memory overhead:** one color bit per node (often stored in a spare bit of
  the parent pointer in C/C++ implementations).
- **Cache behavior:** similar to any pointer-based tree — poor compared to
  arrays. `sortedcontainers.SortedList` in Python uses a "list of lists"
  layout that's more cache-friendly and often faster in practice despite
  similar asymptotic bounds.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Two reds in a row after insert | Forgot the fix-up phase; just inserted red and stopped | Always run the fix-up loop after inserting |
| 2 | Root is red after fix-up | The fix-up recolored the root red during propagation | Last step of every insert fix-up: force root to black |
| 3 | Black-height differs across paths after delete | Removed a black node without compensating | Run the delete fix-up cases; they restore the invariant |
| 4 | Rotation corrupts the tree | Forgot to update the parent pointer of the rotated node | Rotations must update three sets of pointers: child, parent, and grandparent |
| 5 | Implementing from scratch for production | Bugs in the ~8 fix-up cases that are hard to test exhaustively | Use a battle-tested library (`sortedcontainers`, C++ STL, Java stdlib) |

## Practice

**Warm-up.** Draw a valid red-black tree with 7 nodes. Label each node's
color. Verify all five invariants by hand.

**Standard.** Perform a left-rotation and a right-rotation on paper for a
5-node tree. Confirm that BST ordering is preserved.

**Bug hunt.** After inserting values 1 through 5 into an RB tree, you notice
two consecutive red nodes on a path. Which invariant is violated, and which
fix-up case applies?

**Stretch.** Insert values 1 through 10 into an empty red-black tree using
any online visualizer (e.g., USFCA's tool). Record the tree shape and color
assignments after each insert. How many rotations total?

**Stretch++.** Benchmark `sortedcontainers.SortedList` against `sorted()` +
`bisect.insort` for 100,000 insertions into a maintained-sorted collection.
Measure total time and per-operation average.

<details><summary>Show solutions</summary>

**Bug hunt:** Invariant 4 (a red node's children must be black). If the
uncle is red, apply case 1: recolor parent and uncle black, grandparent
red, and recurse upward. If the uncle is black, apply a rotation (case 2
or 3 depending on inner/outer child).

**Stretch++:**

```python
import time
from bisect import insort
from sortedcontainers import SortedList

n = 100_000
data = list(range(n))

# SortedList
sl = SortedList()
t0 = time.perf_counter()
for x in data:
    sl.add(x)
t1 = time.perf_counter()
print(f"SortedList: {t1 - t0:.3f}s")

# bisect.insort into a plain list
arr = []
t0 = time.perf_counter()
for x in data:
    insort(arr, x)
t1 = time.perf_counter()
print(f"bisect.insort: {t1 - t0:.3f}s")
# insort is O(n) per insert (shift), so this is O(n²) total.
```

</details>

## In plain terms (newbie lane)
If `Red Black Trees` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A red-black tree guarantees height:
    (a) exactly log₂ n
    (b) ≤ 2·log₂(n + 1), i.e., O(log n)
    (c) perfectly balanced at all times
    (d) O(n) in the worst case

2. A red node's children must be:
    (a) red or black, no constraint
    (b) both black
    (c) both red
    (d) the same color as their parent

3. Python's standard library provides a red-black tree as:
    (a) `collections.OrderedDict`
    (b) `heapq`
    (c) there is no RB tree in the stdlib — use `sortedcontainers`
    (d) `set`

4. A rotation changes:
    (a) the BST ordering of elements
    (b) the tree structure while preserving BST ordering
    (c) only node colors
    (d) nothing observable

5. `std::map` in C++ is typically implemented as:
    (a) a hash table
    (b) a red-black tree
    (c) an AVL tree
    (d) a B-tree

**Short answer:**

6. Why are rotations essential to maintaining red-black tree invariants?

7. When would you choose a hash map over a balanced BST?

*Answers: 1-b, 2-b, 3-c, 4-b, 5-b. 6) Rotations restructure the tree locally to reduce height imbalances without violating BST ordering — they're the mechanism that converts color/height violations into valid configurations. 7) When you don't need sorted order and want O(1) average lookup instead of O(log n) — the most common case in practice.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-red-black-trees — mini-project](mini-projects/11-red-black-trees-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A red-black tree is a BST augmented with node colors and five invariants
  that guarantee O(log n) height — and therefore O(log n) insert, delete,
  and search.
- Rotations and recoloring are the repair mechanisms; at most 2–3 rotations
  per operation.
- Red-black trees power `std::map`, Java's `TreeMap`, and the Linux kernel's
  CFS scheduler. In Python, `sortedcontainers` is the practical equivalent.
- Don't implement from scratch for production — understand the invariants so
  you can reason about performance guarantees.

## Further reading

- *CLRS* ch. 13 — Red-Black Trees (the definitive reference).
- Sedgewick, *Left-Leaning Red-Black Trees* — a simplified variant with
  fewer cases.
- USFCA Data Structure Visualizations — interactive RB tree applet.
- Next: [Hashmaps](12-hashmaps.md).
