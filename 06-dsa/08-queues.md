# Chapter 08 — Queues

> "A queue is a FIFO line. Everyone you've ever served in the order they arrived lives in a queue."

## Learning objectives

By the end of this chapter you will be able to:

- Implement a queue with `collections.deque` and explain why `list` is a bad choice.
- Distinguish between a queue, a deque, and a priority queue — and know when to use each.
- Recognize queue-shaped problems: BFS, task processing, rate limiting, request buffering.
- Use `heapq` for priority-queue operations in Python.

## Prerequisites & recap

- [Chapter 07 — Stacks](07-stacks.md) — you understand LIFO; now you'll learn FIFO.

## The simple version

A queue is a line. Items join at the back and leave from the front — just like a queue at a coffee shop. The first person in line gets served first. That's FIFO: First In, First Out.

Where stacks model *nesting* (most recent first), queues model *fairness* (first come, first served). BFS explores a graph level by level because it processes nodes in the order they were discovered — that's a queue. Web servers handle requests in arrival order — that's a queue. Background job systems like Celery or RabbitMQ are queues. Any time you need to process items in the order they arrived, you need a FIFO queue.

## Visual flow

```
  Queue operations (FIFO):

  enqueue(A)   enqueue(B)   enqueue(C)   dequeue()    peek()

  +----------+  +----------+  +----------+  +----------+  +----------+
  |          |  |          |  |          |  |          |  |          |
  | A -----> |  | A  B --> |  | A  B  C >|  | B  C -->|  | B  C -->|
  |          |  |          |  |          |  |          |  |          |
  +----------+  +----------+  +----------+  +----------+  +----------+
   front=A       front=A       front=A       front=B       front=B
   back=A        back=B        back=C        back=C        back=C

  dequeue() returns A (the first one in).
  peek() returns B (the current front) without removing it.

  Priority Queue (items dequeue by priority, not arrival):

  push(C,3)  push(A,1)  push(B,2)   pop()     pop()
  +-------+  +-------+  +-------+  +-------+  +-------+
  |  C:3  |  |  A:1  |  |  A:1  |  |  B:2  |  |  C:3  |
  |       |  |  C:3  |  |  B:2  |  |  C:3  |  |       |
  |       |  |       |  |  C:3  |  |       |  |       |
  +-------+  +-------+  +-------+  +-------+  +-------+

  pop() returns A (priority 1 = smallest = highest priority).
```
*Figure 8-1: FIFO queue (top) vs. priority queue (bottom). In a FIFO queue, order of arrival determines order of service. In a priority queue, priority does.*

## Concept deep-dive

### The queue API

A basic queue supports four operations, all O(1):

| Operation | Description |
|---|---|
| `enqueue(x)` | Add x to the back |
| `dequeue()` | Remove and return the front element |
| `peek()` | Return the front element without removing it |
| `is_empty()` / `len()` | Check if the queue has elements |

### Why not use a list?

This is the single most important thing in this chapter: **never use `list.pop(0)` for a queue**.

`list.pop(0)` removes the first element, which requires shifting *every remaining element* one position to the left. That's O(n) per dequeue. Over m dequeue operations on a list of n elements, you pay O(n·m) — which is catastrophic.

```python
# DON'T do this
queue = [1, 2, 3, 4, 5]
queue.pop(0)  # O(n) — shifts [2,3,4,5] left

# DO this
from collections import deque
queue = deque([1, 2, 3, 4, 5])
queue.popleft()  # O(1) — no shifting
```

### Python idiom: `collections.deque`

`collections.deque` (double-ended queue, pronounced "deck") is implemented as a doubly-linked list of fixed-size blocks. It provides O(1) operations on *both* ends:

```python
from collections import deque

q = deque()
q.append(1)       # enqueue to back
q.append(2)
q.append(3)
q.popleft()       # dequeue from front → 1
q[0]              # peek at front → 2
len(q)            # 2
```

Why is `deque` O(1) at both ends while `list` isn't? Because `deque` doesn't store elements in a single contiguous array. It uses a chain of small arrays (blocks), so removing from the front doesn't require shifting — it just advances a pointer within the first block.

### The deque: double-ended queue

A deque extends the queue concept by allowing efficient insertion and removal at *both* ends:

| Operation | Complexity |
|---|---|
| `append(x)` | O(1) — add to right |
| `appendleft(x)` | O(1) — add to left |
| `pop()` | O(1) — remove from right |
| `popleft()` | O(1) — remove from left |
| `q[i]` | O(n) — random access (not O(1)!) |

Note the trade-off: `deque` gives you O(1) on both ends but O(n) random access. `list` gives you O(1) random access but O(n) at the left end. Pick based on your access pattern.

**Bounded deque:** `deque(maxlen=n)` automatically drops the oldest element when a new one is added to a full deque. This is perfect for sliding windows, rolling logs, and "most recent N events" patterns.

```python
recent = deque(maxlen=5)
for i in range(10):
    recent.append(i)
print(list(recent))  # [5, 6, 7, 8, 9] — oldest values auto-evicted
```

### Priority queue

A priority queue dequeues elements not by arrival order, but by *priority*. The element with the highest priority (lowest priority value, by convention) comes out first.

Under the hood, a priority queue is typically implemented as a **binary heap** — a complete binary tree where every parent is smaller than its children. This gives:

| Operation | Complexity |
|---|---|
| Insert (push) | O(log n) |
| Remove min (pop) | O(log n) |
| Peek at min | O(1) |
| Search for arbitrary element | O(n) |

Python's `heapq` module implements a min-heap on top of a regular list:

```python
import heapq

pq = []
heapq.heappush(pq, (3, "low priority"))
heapq.heappush(pq, (1, "high priority"))
heapq.heappush(pq, (2, "medium priority"))

priority, item = heapq.heappop(pq)  # (1, "high priority")
```

For a max-heap, negate the priority: `heappush(pq, (-priority, item))`.

### Queues in the real world

Queues are everywhere in backend systems:

- **BFS traversal** (Chapter 15): explore a graph level by level by processing nodes in discovery order.
- **Request buffering:** a web server queues incoming requests when all workers are busy.
- **Rate limiting:** a token-bucket algorithm replenishes tokens at a fixed rate; requests dequeue tokens.
- **Work queues:** RabbitMQ, SQS, Celery — background task processing follows the producer-consumer pattern over FIFO queues.
- **Print spoolers, I/O buffers, packet routing** — anything that processes items in arrival order.

The FIFO guarantee is what makes queues fair. Without it, late-arriving items could starve earlier ones — a real problem in systems under load.

## Why these design choices

**Why `deque` instead of a linked list?** A `deque` offers O(1) at both ends *and* reasonable memory overhead (elements are stored in contiguous blocks, which are cache-friendly). A pure linked list would also give O(1) at both ends but with much higher per-element memory overhead (~56 bytes per node in Python) and poor cache locality.

**When would you use `queue.Queue` instead of `deque`?** Python's `queue.Queue` (from the `queue` module) adds thread-safe blocking operations: `put()` blocks if the queue is full, `get()` blocks if it's empty. Use it for producer-consumer patterns in multi-threaded code. For single-threaded use, `deque` is simpler and faster.

**When would you use a priority queue instead of a regular queue?** When not all items are equal. A hospital ER doesn't serve patients in arrival order — it serves by urgency. Dijkstra's algorithm doesn't explore nodes in discovery order — it explores the nearest unvisited node. Any time "importance" trumps "arrival time," use a priority queue.

**When is a sorted list better than a priority queue?** When the data is static (you sort once and query many times) or when you need access to *all* elements in sorted order, not just the minimum. A priority queue is optimized for dynamic insert + extract-min; a sorted list is optimized for static range queries.

## Production-quality code

```python
from collections import deque
import heapq
from typing import TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar("T")


class FIFOQueue(Generic[T]):
    """FIFO queue backed by collections.deque. O(1) all operations."""

    def __init__(self, maxlen: int | None = None) -> None:
        self._data: deque[T] = deque(maxlen=maxlen)

    def enqueue(self, item: T) -> None:
        self._data.append(item)

    def dequeue(self) -> T:
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def peek(self) -> T:
        if not self._data:
            raise IndexError("peek at empty queue")
        return self._data[0]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __repr__(self) -> str:
        items = list(self._data)
        return f"FIFOQueue(front={items})"


@dataclass(order=True)
class PrioritizedItem:
    """Wrapper for priority queue items that handles comparison correctly."""
    priority: float
    item: object = field(compare=False)


class PriorityQueue:
    """Priority queue backed by heapq (min-heap).

    Items with lower priority values are dequeued first.
    """

    def __init__(self) -> None:
        self._heap: list[PrioritizedItem] = []

    def push(self, item: object, priority: float) -> None:
        heapq.heappush(self._heap, PrioritizedItem(priority, item))

    def pop(self) -> object:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        return heapq.heappop(self._heap).item

    def peek(self) -> object:
        if not self._heap:
            raise IndexError("peek at empty priority queue")
        return self._heap[0].item

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)


def sliding_max(nums: list[int], k: int) -> list[int]:
    """Maximum of each sliding window of size k. O(n) time, O(k) space.

    Uses a monotonic deque: indices are stored in decreasing order of
    their values. The front of the deque is always the index of the
    current window's maximum.
    """
    if k <= 0:
        raise ValueError(f"Window size must be positive, got {k}")
    if not nums:
        return []

    dq: deque[int] = deque()  # stores indices
    result: list[int] = []

    for i, n in enumerate(nums):
        # Remove indices of elements smaller than current from back
        while dq and nums[dq[-1]] <= n:
            dq.pop()
        dq.append(i)

        # Remove front index if it's outside the window
        if dq[0] <= i - k:
            dq.popleft()

        # Window is fully formed once we've seen k elements
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

## Security notes

- **Unbounded queue growth (DoS):** If producers add items faster than consumers process them, the queue grows without limit, eventually causing OOM. Always set bounds: `deque(maxlen=N)` or `queue.Queue(maxsize=N)`. In production systems, this is why message brokers have queue size limits and back-pressure mechanisms.
- **Priority inversion:** In a priority queue, low-priority items can starve if high-priority items keep arriving. Mitigate by aging (gradually increasing the priority of waiting items) or using separate queues for each priority level.

## Performance notes

| Operation | `list` (as queue) | `deque` | `heapq` (priority queue) |
|---|---|---|---|
| Enqueue (back) | amortized O(1) | O(1) | O(log n) |
| Dequeue (front) | **O(n)** | O(1) | O(log n) |
| Peek (front) | O(1) | O(1) | O(1) |
| Memory per element | ~8 bytes | ~8 bytes | ~8 bytes |

The critical difference: `list.pop(0)` is O(n) while `deque.popleft()` is O(1). For a queue of 100,000 items, that's the difference between 100,000 operations and 10,000,000,000 total shifts.

**When does `deque` indexing matter?** `deque[i]` is O(n), not O(1). If you need both FIFO semantics *and* random access, consider keeping a `deque` for the queue and a `dict` for index-based lookup (this is essentially how an LRU cache works).

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Queue operations get slower as the queue grows | Using `list.pop(0)` — O(n) per dequeue | Switch to `collections.deque` with `popleft()` |
| 2 | `deque.pop()` returns the wrong element | `pop()` removes from the *right* (back), not the front | Use `popleft()` for FIFO dequeue |
| 3 | Sliding window loses old values unexpectedly | Forgot to set `maxlen` or set it too small | Use `deque(maxlen=k)` with the correct window size |
| 4 | Priority queue doesn't work with custom objects | `heapq` compares tuples element-by-element; if priorities are equal, it compares the items (which may not be comparable) | Use `dataclass(order=True)` with a `field(compare=False)` for the item, or include a tie-breaking counter |
| 5 | Using a priority queue where a simple `sort()` of a small list would suffice | Over-engineering — if all items are available upfront and the list is small, `sorted()` is simpler | Only use `heapq` when items arrive dynamically and you need to extract the minimum incrementally |

## Practice

**Warm-up.** Enqueue the numbers 1 through 5 into a `deque`, then dequeue and print each one. Verify they come out in order.

<details><summary>Show solution</summary>

```python
from collections import deque

q = deque()
for i in range(1, 6):
    q.append(i)

result = []
while q:
    result.append(q.popleft())

print(result)  # [1, 2, 3, 4, 5]
assert result == [1, 2, 3, 4, 5]
```

</details>

**Standard.** Implement a rolling average of size k using a `deque`. Test it on `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` with k = 3.

<details><summary>Show solution</summary>

```python
from collections import deque

def rolling_average(values, k):
    window = deque(maxlen=k)
    result = []
    total = 0.0
    for v in values:
        if len(window) == k:
            total -= window[0]
        window.append(v)
        total += v
        if len(window) == k:
            result.append(total / k)
    return result

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
avgs = rolling_average(data, 3)
print(avgs)  # [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
assert len(avgs) == len(data) - 2
assert avgs[0] == (1 + 2 + 3) / 3
assert avgs[-1] == (8 + 9 + 10) / 3
```

</details>

**Bug hunt.** A developer implements a queue using a list: `queue.append(item)` to enqueue and `queue.pop()` to dequeue. Items come out in the wrong order. What's the bug?

<details><summary>Show solution</summary>

`list.pop()` (no argument) removes from the *back*, giving LIFO behavior (a stack, not a queue). The developer wanted FIFO, which requires removing from the front.

The fix: use `collections.deque` with `popleft()`:

```python
from collections import deque
queue = deque()
queue.append(1)
queue.append(2)
queue.popleft()  # → 1 (correct FIFO)
```

Or if using a list (not recommended): `queue.pop(0)` — but this is O(n).

</details>

**Stretch.** Implement a priority queue for Dijkstra's shortest-path algorithm. Given a weighted adjacency list, find the shortest distance from a start node to all other nodes.

<details><summary>Show solution</summary>

```python
import heapq
from collections import defaultdict

def dijkstra(graph: dict[str, list[tuple[str, int]]], start: str) -> dict[str, int]:
    dist = {start: 0}
    pq = [(0, start)]

    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph.get(node, []):
            new_dist = d + weight
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    return dist

graph = {
    "A": [("B", 1), ("C", 4)],
    "B": [("C", 2), ("D", 5)],
    "C": [("D", 1)],
    "D": [],
}

distances = dijkstra(graph, "A")
assert distances == {"A": 0, "B": 1, "C": 3, "D": 4}
print(distances)
```

The priority queue ensures we always process the nearest unvisited node — the key insight of Dijkstra's algorithm.

</details>

**Stretch++.** Implement a circular buffer with fixed capacity using `deque(maxlen=n)`. Support `write(data)`, `read() -> data`, `is_full()`, and `is_empty()`. Then benchmark it against a naive list-based circular buffer.

<details><summary>Show solution</summary>

```python
from collections import deque
import time

class CircularBuffer:
    """Fixed-capacity circular buffer using deque.

    When full, new writes overwrite the oldest data.
    """
    def __init__(self, capacity: int):
        self._buf = deque(maxlen=capacity)

    def write(self, data) -> None:
        self._buf.append(data)

    def read(self):
        if not self._buf:
            raise IndexError("read from empty buffer")
        return self._buf.popleft()

    def is_full(self) -> bool:
        return len(self._buf) == self._buf.maxlen

    def is_empty(self) -> bool:
        return len(self._buf) == 0

    def __len__(self) -> int:
        return len(self._buf)

buf = CircularBuffer(3)
buf.write("a"); buf.write("b"); buf.write("c")
assert buf.is_full()
buf.write("d")  # overwrites "a"
assert buf.read() == "b"  # "a" was evicted
assert buf.read() == "c"
assert buf.read() == "d"
assert buf.is_empty()

# Benchmark
n = 1_000_000
buf = CircularBuffer(1000)
start = time.perf_counter()
for i in range(n):
    buf.write(i)
    if buf.is_full():
        buf.read()
elapsed = time.perf_counter() - start
print(f"Circular buffer: {n} ops in {elapsed:.3f}s")
```

</details>

## In plain terms (newbie lane)
If `Queues` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A queue is:
    (a) LIFO  (b) FIFO  (c) random access  (d) always sorted

2. The correct Python choice for a queue is:
    (a) `list`  (b) `collections.deque`  (c) `set`  (d) `dict`

3. Python's `heapq` provides:
    (a) a max-heap  (b) a min-heap  (c) a balanced BST  (d) a sorted array

4. A priority queue differs from a regular queue because:
    (a) it has O(log n) operations  (b) it dequeues by priority, not arrival order  (c) both a and b  (d) neither

5. `deque(maxlen=100)`:
    (a) provides O(1) appends and automatically drops the oldest element when full  (b) raises an error at 100 elements  (c) returns a list  (d) is not supported

**Short answer:**

6. Why is BFS queue-shaped?
7. When does a priority queue beat a sorted list?

*Answers: 1-b, 2-b, 3-b, 4-c, 5-a, 6-BFS processes nodes in discovery order — the first node discovered at a given level is explored before any node at the next level. This FIFO behavior maps directly to a queue, 7-When items arrive dynamically (one at a time) and you need the minimum after each insertion. A sorted list would require O(n) per insert to maintain order, while a heap requires O(log n). If all data is available upfront, sorting once (O(n log n)) then indexing (O(1)) is better.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-queues — mini-project](mini-projects/08-queues-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A queue is FIFO: first in, first out. Use `collections.deque` in Python — never `list.pop(0)`, which is O(n).
- A deque supports O(1) operations on both ends, making it versatile for queues, sliding windows, and bounded buffers.
- A priority queue (via `heapq`) dequeues by priority instead of arrival order — essential for Dijkstra's algorithm, task scheduling, and any "most important first" pattern.
- Queues are foundational in backend systems: request buffering, work queues, BFS, and rate limiting all rely on FIFO semantics.

## Further reading

- Python docs: `collections.deque` — the full API including `rotate()`, `maxlen`, and thread safety notes.
- Python docs: `heapq` — heap operations, `nlargest`, `nsmallest`, merge.
- Python docs: `queue.Queue` — thread-safe blocking queue for producer-consumer patterns.
- Queueing theory: M/M/1 queue model — the mathematical foundation for capacity planning.
- Next: [Linked Lists](09-linked-lists.md).
