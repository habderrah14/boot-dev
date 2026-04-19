# Chapter 09 — Linked Lists

> "Arrays own the cache line; linked lists own the splice."

## Learning objectives

By the end of this chapter you will be able to:

- Implement singly and doubly linked lists from scratch in Python.
- Perform insertion, deletion, traversal, and in-place reversal.
- Detect cycles with Floyd's tortoise-and-hare algorithm and find the cycle entry point.
- Articulate exactly when a linked list beats a dynamic array — and when it doesn't.

## Prerequisites & recap

- [Data-structures intro](06-data-structures-intro.md) — memory models, pointers, references.
- Familiarity with Python classes, `__iter__`, and generators.

## The simple version

Picture a scavenger hunt. Each clue tells you where to find the next one, but
you never get a map of all the locations at once. That's a linked list: each
element (a "node") stores its own data *and* the address of the next node.
There is no index you can jump to — you walk the chain from the beginning.

The trade-off is the opposite of an array. An array gives you instant access to
any position but makes inserting in the middle expensive because everything
after the insertion point must shift. A linked list lets you splice a new node
into the middle in constant time — if you already have a pointer to the right
spot — but getting to that spot costs you a walk through the chain.

## Visual flow

```
  head
   |
   v
 +---+---+    +---+---+    +---+---+    +------+
 | 1 | *-+--->| 2 | *-+--->| 3 | *-+--->| None |
 +---+---+    +---+---+    +---+---+    +------+

 Singly linked list: each node holds a value and
 a pointer to the next node.  None terminates.

 Prepend "0":
 +---+---+
 | 0 | *-+--> (old head, node 1)
 +---+---+
   ^
   |
  head  ← just rewire one pointer: O(1)
```

## Concept deep-dive

### Why linked lists exist

Arrays are laid out contiguously in memory, which makes the CPU cache happy —
sequential reads are blazing fast. But insertion or deletion at position *i*
requires shifting O(n − i) elements. When your workload is "insert and delete
at arbitrary known positions constantly", that shift cost dominates. Linked
lists eliminate it: you rewire a couple of pointers, and you're done.

### The node — the atomic unit

A linked list is not a single object; it's a *graph* of node objects connected
by references. The simplest node stores a value and a `next` pointer:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class SNode:
    value: object
    next: Optional[SNode] = None
```

A linked list is then just a reference to the first node — the "head". When
`head is None`, the list is empty.

### Singly linked list operations

**Prepend** — O(1). Create a new node whose `next` points at the old head, then
update `head`.

**Append** — O(n) unless you keep a `tail` pointer, in which case O(1).

**Search** — O(n). Walk from head until you find the value or hit `None`.

**Delete by reference** — O(1) if you have the *previous* node. O(n) otherwise
because you have to find the predecessor.

**Indexing** — O(n). There is no random access.

### Doubly linked list

Each node gains a `prev` pointer. This buys you:

- O(1) deletion when you have a reference to the node itself (you can reach
  its predecessor directly).
- Backward traversal.

The price: an extra pointer per node (more memory, more bookkeeping on every
insert/delete). Python's `collections.deque` is built on a doubly linked
block list — each block holds a small array of elements, and the blocks are
doubly linked together.

### Reversing a singly linked list

Reversal is the classic linked-list exercise. You walk the list once, flipping
each `next` pointer to point backward:

```
Before:  1 -> 2 -> 3 -> None
After:   None <- 1 <- 2 <- 3
         head is now 3
```

The trick is maintaining three pointers — `prev`, `cur`, `nxt` — so you don't
lose the rest of the chain when you flip a pointer.

### Cycle detection — Floyd's algorithm

If a list has a cycle (some node's `next` points back to an earlier node), a
naive traversal never terminates. Floyd's algorithm uses two pointers: "slow"
moves one step at a time, "fast" moves two. If they ever meet, there's a
cycle. If `fast` reaches `None`, the list is acyclic.

**Why it works.** Inside the cycle, the gap between slow and fast shrinks by
one on every step — they're guaranteed to collide within one loop of the
cycle.

**Finding the entry point** (phase 2). Once slow and fast meet, reset one
pointer to `head` and advance both one step at a time. The node where they
meet again is the cycle's entry point. This falls out of the modular
arithmetic of their positions — see *CLRS* ch. 10 for the proof.

### Why linked lists rarely win in Python

CPython's `list` is a dynamic array with excellent cache locality. On modern
hardware, walking a linked list causes a cache miss on almost every hop — each
node lives at a random heap address. Benchmarks consistently show Python
`list` beating a hand-rolled linked list for all but the most
splice-intensive workloads.

Use linked lists when:

- You splice at known positions frequently (e.g., an LRU cache: dict +
  doubly linked list).
- You compose immutable prefixes (functional / persistent data structures).
- You're implementing a deque, a free list, or an intrusive list inside a
  systems-level allocator.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| Singly linked | Less memory per node | When you never need backward traversal or O(1) delete-by-reference |
| Doubly linked | Extra pointer per node | When O(1) delete-by-reference or bidirectional traversal matters (LRU cache) |
| Sentinel / dummy head | Eliminates edge cases for empty list | Almost always worth it in production code |
| Tail pointer | O(1) append at the cost of maintaining one more pointer | When append is frequent |
| Dynamic array (`list`) | Cache-friendly, O(1) amortized append | The default — switch away only with evidence |

## Production-quality code

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class _Node:
    value: object
    next: Optional[_Node] = None


class SinglyLinkedList:
    """Singly linked list with tail pointer for O(1) append."""

    def __init__(self) -> None:
        self._head: Optional[_Node] = None
        self._tail: Optional[_Node] = None
        self._length: int = 0

    def __len__(self) -> int:
        return self._length

    def __bool__(self) -> bool:
        return self._length > 0

    def __iter__(self) -> Iterator[object]:
        cur = self._head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return f"SinglyLinkedList([{', '.join(repr(v) for v in self)}])"

    def prepend(self, value: object) -> None:
        node = _Node(value, self._head)
        self._head = node
        if self._tail is None:
            self._tail = node
        self._length += 1

    def append(self, value: object) -> None:
        node = _Node(value)
        if self._tail is not None:
            self._tail.next = node
        else:
            self._head = node
        self._tail = node
        self._length += 1

    def pop_front(self) -> object:
        if self._head is None:
            raise IndexError("pop from empty list")
        value = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._length -= 1
        return value

    def find(self, value: object) -> Optional[_Node]:
        cur = self._head
        while cur is not None:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def delete(self, value: object) -> bool:
        prev, cur = None, self._head
        while cur is not None:
            if cur.value == value:
                if prev is None:
                    self._head = cur.next
                else:
                    prev.next = cur.next
                if cur is self._tail:
                    self._tail = prev
                self._length -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def reverse(self) -> None:
        self._tail = self._head
        prev, cur = None, self._head
        while cur is not None:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        self._head = prev


def has_cycle(head: Optional[_Node]) -> bool:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next              # type: ignore[union-attr]
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def cycle_entry(head: Optional[_Node]) -> Optional[_Node]:
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next              # type: ignore[union-attr]
        fast = fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow = slow.next      # type: ignore[union-attr]
                fast = fast.next      # type: ignore[union-attr]
            return slow               # type: ignore[return-value]
    return None


def merge_sorted(
    a: Optional[_Node], b: Optional[_Node]
) -> Optional[_Node]:
    """Merge two sorted singly-linked lists into one sorted list."""
    dummy = _Node(None)
    tail = dummy
    while a is not None and b is not None:
        if a.value <= b.value:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next              # type: ignore[assignment]
    tail.next = a if a is not None else b
    return dummy.next
```

## Security notes

N/A — linked lists are an in-process data structure with no network surface.
The only security-adjacent concern is **untrusted cycle creation**: if an
attacker can modify `next` pointers (e.g., through a deserialization bug),
they can create cycles that cause infinite loops. Validate or limit traversal
length when processing untrusted input.

## Performance notes

| Operation | Singly linked | Doubly linked | `list` (dynamic array) |
|---|---|---|---|
| Access by index | O(n) | O(n) | **O(1)** |
| Prepend | **O(1)** | **O(1)** | O(n) (`insert(0, x)`) |
| Append (with tail ptr) | **O(1)** | **O(1)** | **O(1)** amortized |
| Delete by reference | O(n)* | **O(1)** | O(n) |
| Search | O(n) | O(n) | O(n) |
| Cache performance | Poor | Poor | **Excellent** |

*O(n) because you must find the predecessor; O(1) if you already have it.

**Key insight:** on modern CPUs, cache misses dominate. A linked-list
traversal generates roughly one L1 cache miss per node (each node is at a
random address), while an array traversal triggers a miss only every
~16 elements (64-byte cache line / 4-byte int). For sequential scans, arrays
are 10–50× faster in practice.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Data silently disappears | Lost the `head` reference during an operation | Always update `head` explicitly; use a sentinel if needed |
| 2 | `AttributeError: 'NoneType' has no attribute 'next'` | Dereferencing `None` at end of list | Guard with `while cur is not None` |
| 3 | Reversal produces a one-element list | Only updated `cur.next` but forgot to advance `prev` and `cur` | Use the three-pointer pattern: `prev, cur, nxt` |
| 4 | Traversal hangs forever | Cycle in the list (e.g., tail.next accidentally set to head) | Use Floyd's algorithm or cap iteration count |
| 5 | `tail` pointer is stale after deletion | Deleted the tail node but didn't update `self._tail` | Always check `if cur is self._tail: self._tail = prev` |

## Practice

**Warm-up.** Build a 5-node singly linked list. Print all values with a `for`
loop.

**Standard.** Implement `delete_at(index)` that removes the node at a given
position (0-based). Handle out-of-range gracefully.

**Bug hunt.** A colleague wrote this reversal:

```python
def bad_reverse(head):
    cur = head
    while cur and cur.next:
        cur.next, cur = cur, cur.next
    return cur
```

Explain why it produces an infinite loop and fix it.

**Stretch.** Implement a doubly linked list with O(1) `delete_node(node)`.
Verify by building a list, deleting the middle node, and iterating both
forward and backward.

**Stretch++.** Detect the cycle entry point using Floyd's two-phase algorithm.
Write a test that manually creates a cycle and asserts the correct entry node.

<details><summary>Show solutions</summary>

**Warm-up:**

```python
ll = SinglyLinkedList()
for v in [5, 4, 3, 2, 1]:
    ll.prepend(v)
for v in ll:
    print(v)  # 1, 2, 3, 4, 5
```

**Standard:**

```python
def delete_at(self, index: int) -> object:
    if index < 0 or index >= self._length:
        raise IndexError("index out of range")
    if index == 0:
        return self.pop_front()
    prev, cur = None, self._head
    for _ in range(index):
        prev, cur = cur, cur.next
    prev.next = cur.next
    if cur is self._tail:
        self._tail = prev
    self._length -= 1
    return cur.value
```

**Bug hunt:** Python's tuple-packing evaluates the right side first.
`cur.next, cur = cur, cur.next` sets `cur.next = cur` (a self-loop!)
before advancing `cur`. Fix: use an explicit temporary variable (`nxt =
cur.next`) and the three-pointer pattern shown in the production code.

**Stretch++:**

```python
a, b, c, d = _Node(1), _Node(2), _Node(3), _Node(4)
a.next, b.next, c.next, d.next = b, c, d, b   # cycle at b
assert cycle_entry(a) is b
```

</details>

## In plain terms (newbie lane)
If `Linked Lists` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Accessing index *i* in a singly linked list is:
    (a) O(1)  (b) O(log n)  (c) O(n)  (d) O(n log n)

2. Prepending to a singly linked list (with head pointer) is:
    (a) O(1)  (b) O(n)  (c) O(log n)  (d) O(n²)

3. Floyd's cycle-detection algorithm uses:
    (a) a hash set of visited nodes  (b) two pointers moving at different speeds
    (c) a stack  (d) BFS on the list graph

4. Python's `list` (dynamic array) typically beats linked lists because of:
    (a) CPU cache locality and O(1) indexing  (b) better asymptotic insert
    (c) lower pointer overhead  (d) built-in cycle detection

5. `collections.deque` is internally:
    (a) a dynamic array  (b) a doubly linked block list  (c) a binary heap
    (d) a hash table

**Short answer:**

6. Give one real-world scenario where a linked list is the right choice over a
   dynamic array.

7. Why does Floyd's algorithm use only O(1) extra space?

*Answers: 1-c, 2-a, 3-b, 4-a, 5-b. 6) LRU cache (dict + doubly linked list) where you need O(1) move-to-front on every access. 7) It uses only two pointer variables regardless of list size — no auxiliary data structure.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-linked-lists — mini-project](mini-projects/09-linked-lists-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A linked list is a chain of heap-allocated nodes connected by pointers —
  O(1) splice at a known position, O(n) random access.
- Doubly linked lists add a `prev` pointer for O(1) delete-by-reference at
  the cost of extra memory.
- On modern hardware, dynamic arrays (`list`) almost always outperform linked
  lists due to cache effects. Reach for a linked list only when you have a
  concrete reason (LRU cache, intrusive lists, persistent data structures).
- Floyd's tortoise-and-hare algorithm detects cycles in O(n) time and O(1)
  space.

## Further reading

- *CLRS* ch. 10 — Elementary Data Structures.
- Raymond Hettinger, "Modern Python Dictionaries" (PyCon talk) — contrasts
  array-based and pointer-based layouts.
- Next: [Binary trees](10-binary-trees.md).
