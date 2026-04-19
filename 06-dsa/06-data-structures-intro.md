# Chapter 06 — Data Structures Intro

> "A data structure is a *discipline* of organizing data so specific operations are fast. Pick wisely and the algorithm writes itself."

## Learning objectives

By the end of this chapter you will be able to:

- Classify common data structures by their fast operations (access, search, insert, delete).
- Read the complexity cheat sheet and use it to pick the right structure for a given workload.
- Match real problems to structures: "hot key lookups" → hashmap, "always get the smallest" → heap, "FIFO processing" → deque.
- Explain the fundamental trade-off: no structure is best at everything.

## Prerequisites & recap

- [Chapter 03 — Big-O Analysis](03-big-o.md) — you need to compare O(1) vs. O(n) vs. O(log n).
- [Python lists, dicts, and sets](../01-python/README.md) — you should be comfortable using them; now you'll understand *why* they perform the way they do.

## The simple version

Every data structure is a set of trade-offs. A Python `list` lets you access any element by index in O(1), but searching for a value requires scanning the whole thing — O(n). A `dict` lets you look up any key in O(1) average, but doesn't maintain a sorted order. A heap always gives you the smallest element in O(1), but can't tell you if a specific value exists without scanning everything.

Your job isn't to memorize every structure — it's to learn the *one question* that picks the right one: "What operation does my code do *most*?" If it's key lookups, use a dict. If it's "give me the smallest," use a heap. If it's "process in arrival order," use a deque. The structure follows from the workload.

## Visual flow

```
  What operation does your code do most?
  ========================================

  "Look up by key"                 ---->  dict / set       O(1) avg
       |
  "Get min or max repeatedly"      ---->  heapq            O(1) peek, O(log n) push/pop
       |
  "Process in order of arrival"    ---->  deque            O(1) both ends
       |
  "Range query on sorted data"     ---->  sorted list      O(log n) search
       |                                  or balanced BST
  "Prefix match / autocomplete"    ---->  trie             O(m) per query
       |
  "Model relationships"            ---->  graph (adj list) O(V+E) traversal
       |
  "Random access by index"         ---->  list / array     O(1) index
```
*Figure 6-1: Decision tree for choosing a data structure. Start from your dominant operation.*

## Concept deep-dive

### The cheat sheet

This is the table you'll reference throughout your career. Bookmark it.

| Structure | Access | Search | Insert | Delete | Space |
|---|---|---|---|---|---|
| **Array / list** (Python `list`) | O(1) by index | O(n) | O(n) worst (mid); amortized O(1) end | O(n) | O(n) |
| **Linked list** | O(n) | O(n) | O(1) at head/tail (with ref) | O(1) with node ref | O(n) |
| **Hash map** (Python `dict`) | — | O(1) avg | O(1) avg | O(1) avg | O(n) |
| **Hash set** (Python `set`) | — | O(1) avg | O(1) avg | O(1) avg | O(n) |
| **Balanced BST** | — | O(log n) | O(log n) | O(log n) | O(n) |
| **Heap** (Python `heapq`) | O(1) top only | O(n) | O(log n) | O(log n) | O(n) |
| **Trie** | — | O(m) key length | O(m) | O(m) | O(n·m) |
| **Graph (adjacency list)** | — | varies | O(1) per edge | O(1)–O(V) | O(V+E) |

### Why no structure is "best"

Every O(1) in one column comes at the cost of O(n) in another. A hash map gives you O(1) lookups, but it's unordered — you can't efficiently ask "give me all keys between 100 and 200." A sorted array lets you binary-search in O(log n), but inserting a new element costs O(n) because you have to shift everything.

This is the **fundamental trade-off** of data structures. Speed somewhere costs speed (or space) elsewhere. Your workload determines which costs you can afford.

### Picking by workload pattern

Here's how to think about real problems:

- **"Hot keyed lookups"** — user sessions, config values, caches. Use a **dict**. O(1) average lookup is unbeatable.
- **"Ordered range queries"** — "all events between timestamp A and B." Use a **balanced BST** (Python doesn't have one built-in; use `sortedcontainers.SortedList`). Or keep a sorted list and binary-search.
- **"Always process the highest-priority item next"** — task schedulers, Dijkstra's algorithm. Use a **heap** (`heapq`).
- **"Prefix matching, autocomplete"** — search suggestions, IP routing tables. Use a **trie**.
- **"Parent-child navigation, relationships"** — social networks, dependency graphs. Use a **graph** with adjacency lists.
- **"Process items in arrival order"** — request queues, BFS traversal. Use a **deque** (`collections.deque`).
- **"Random access by position"** — matrix operations, buffer management. Use a **list** (Python `list` or `array`).

### Python's built-ins cover 80% of needs

You don't need to implement most structures from scratch. Python gives you:

- `list`, `tuple` — dynamic arrays.
- `dict`, `set` — hash tables.
- `collections.deque` — double-ended queue (efficient at both ends).
- `heapq` — binary min-heap.
- `collections.Counter` — multiset / frequency counter.
- `collections.defaultdict` — dict with default factory.
- `collections.OrderedDict` — insertion-ordered dict (less needed since Python 3.7+ dicts maintain insertion order).

Reach for a custom structure only when built-ins don't fit — and that's rare in typical backend work.

### When to think about cache friendliness

Modern CPUs are *much* faster than memory. When the CPU reads a value from RAM, it loads an entire cache line (~64 bytes). If the next value you need is in that same cache line, it's essentially free.

Arrays are cache-friendly — elements are contiguous in memory. Linked lists are *not* — each node can be anywhere in the heap. This is why Python `list` (which is a dynamic array) often outperforms linked-list-based structures for small-to-medium sizes, even when the linked list has better Big-O.

## Why these design choices

**Why does Python use hash tables for `dict` and `set`?** Because the most common operations on mappings and sets — lookup, insert, delete — are all O(1) average with hash tables. The alternative (balanced BST) gives O(log n) for everything but adds sorted-order traversal. Python's designers bet that developers rarely need sorted-order iteration from their dicts — and they were right.

**Why doesn't Python have a built-in balanced BST?** Because `dict` + `sorted()` covers most use cases. When you *do* need ordered operations, the `sortedcontainers` third-party library provides `SortedList`, `SortedDict`, and `SortedSet` with excellent performance.

**When would you pick a linked list over an array?** Almost never in Python, due to cache locality and the overhead of Python objects. In lower-level languages (C, Rust), linked lists matter for specific patterns: O(1) insertion/deletion at arbitrary positions when you already have a pointer to the node, or when you need a stable-address collection (no reallocation).

## Production-quality code

```python
from collections import deque, Counter
import heapq
from typing import Sequence


def most_recent_events(events: list[str], max_size: int = 100) -> deque:
    """Keep the most recent `max_size` events using a bounded deque.

    O(1) per append, automatic eviction of oldest when full.
    """
    recent: deque[str] = deque(maxlen=max_size)
    for event in events:
        recent.append(event)
    return recent


def is_known_word(word: str, dictionary: set[str]) -> bool:
    """O(1) average membership test using a hash set."""
    return word in dictionary


def top_k_largest(stream: Sequence[int], k: int) -> list[int]:
    """Return the k largest elements from a stream.

    Uses a min-heap of size k: O(n log k) time, O(k) space.
    This is better than sorting when n >> k.
    """
    if k <= 0:
        return []
    heap: list[int] = []
    for value in stream:
        if len(heap) < k:
            heapq.heappush(heap, value)
        elif value > heap[0]:
            heapq.heapreplace(heap, value)
    return sorted(heap, reverse=True)


def word_frequencies(text: str) -> list[tuple[str, int]]:
    """Return words sorted by frequency (descending).

    Counter handles counting in O(n); most_common sorts by count.
    """
    words = text.lower().split()
    return Counter(words).most_common()


def sliding_window_average(values: Sequence[float], k: int) -> list[float]:
    """Compute the rolling average with window size k.

    Uses a deque to maintain the window: O(n) total, O(k) space.
    """
    if k <= 0:
        raise ValueError(f"Window size must be positive, got {k}")
    window: deque[float] = deque(maxlen=k)
    result: list[float] = []
    running_sum = 0.0
    for value in values:
        if len(window) == k:
            running_sum -= window[0]
        window.append(value)
        running_sum += value
        if len(window) == k:
            result.append(running_sum / k)
    return result
```

## Security notes

- **Hash flooding (DoS):** If an attacker controls the keys inserted into a hash-based structure (`dict`, `set`), they can craft keys that all hash to the same bucket, degrading O(1) operations to O(n). Python mitigates this with hash randomization (`PYTHONHASHSEED` is random by default since 3.3). Don't disable it in production.
- **Unbounded growth:** If you use a `dict` or `list` as a cache without bounds, an attacker can cause OOM by sending many unique keys. Always use bounded structures (`deque(maxlen=...)`, `@lru_cache(maxsize=...)`) or implement explicit eviction.

## Performance notes

| Operation | list | dict/set | deque | heapq |
|---|---|---|---|---|
| Access by index | O(1) | N/A | O(n) | N/A |
| Search (membership) | O(n) | O(1) avg | O(n) | O(n) |
| Append to end | amort O(1) | O(1) avg | O(1) | O(log n) push |
| Insert at front | O(n) | N/A | O(1) | N/A |
| Delete from middle | O(n) | O(1) avg | O(n) | O(n) |
| Get min/max | O(n) | O(n) | O(n) | O(1) min |

**The hidden cost of `in` on a list:** `x in my_list` is O(n). If you do this in a loop over another list, you get O(n·m). Switching to `x in my_set` makes it O(n) total. This is the single most common performance mistake in Python code.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Endpoint slows to a crawl as data grows | Using `x in some_list` for membership checks in a hot loop — O(n) per check | Convert to `set` for O(1) lookups: `some_set = set(some_list)` |
| 2 | "I need a sorted dict" so they sort the dict on every access | Not knowing about `sortedcontainers.SortedDict` or keeping a separate sorted index | `pip install sortedcontainers` or maintain a `heapq` alongside the dict |
| 3 | Rolling their own heap instead of using `heapq` | Not knowing the standard library | `heapq.heappush()`, `heapq.heappop()` — it's a min-heap; negate values for max-heap |
| 4 | Using a `dict` when an `Enum` or dataclass would suffice | Over-using flexible structures when the schema is fixed | If the keys are known at write time and don't change, use a typed class |
| 5 | Appending to a list, then calling `list.pop(0)` for FIFO behavior | `pop(0)` is O(n) because it shifts all remaining elements | Use `collections.deque` with `append()` and `popleft()` — both O(1) |

## Practice

**Warm-up.** For the problem "find the top 5 largest numbers in a stream of 10⁶ numbers," which data structure should you use and why?

<details><summary>Show solution</summary>

Use a **min-heap of size 5**. Push each number; if the heap exceeds size 5, pop the smallest. After processing all numbers, the heap contains the 5 largest.

Why min-heap? Because the smallest element in the heap is the threshold — anything smaller than it can't be in the top 5. This gives you O(n log k) time and O(k) space, which is much better than sorting the entire stream (O(n log n) time, O(n) space).

```python
import heapq

def top_5(stream):
    heap = []
    for x in stream:
        if len(heap) < 5:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)
```

</details>

**Standard.** Pick the right data structure for autocomplete (prefix search). Justify your choice and explain why a hash map wouldn't work.

<details><summary>Show solution</summary>

Use a **trie** (prefix tree). Each node represents a character, and paths from root to leaves represent words. To autocomplete "hel", you traverse h → e → l, then enumerate all children — giving you "hello", "help", "helmet", etc.

Why not a hash map? Because a hash map requires the *exact* key. You can't efficiently ask "give me all keys that start with 'hel'" — you'd have to scan every key (O(n)). A trie answers prefix queries in O(m + k) where m is the prefix length and k is the number of matches.

Alternative: a sorted list with binary search can find the first word starting with "hel" in O(log n), then scan forward. This is simpler and more cache-friendly, but less efficient for very large dictionaries.

</details>

**Bug hunt.** An intern used a `list` for membership checks in a loop over 10,000 items, and the code takes 45 seconds. What's the asymptotic bug, and what's the fix?

<details><summary>Show solution</summary>

The bug: `if item in big_list` inside a loop is O(n) per check × O(m) iterations = O(n·m). With n = 10,000 and m = 10,000, that's 10⁸ operations.

The fix: convert the list to a set before the loop.

```python
big_set = set(big_list)
for item in other_list:
    if item in big_set:    # O(1) instead of O(n)
        process(item)
```

This changes the total from O(n·m) to O(n + m) — a ~10,000× speedup.

</details>

**Stretch.** Implement a sliding-window average of size k using a `deque`. Process a list of 1 million floats and verify the result.

<details><summary>Show solution</summary>

```python
from collections import deque

def sliding_average(values, k):
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

import random
data = [random.random() for _ in range(1_000_000)]
avgs = sliding_average(data, 100)
assert len(avgs) == len(data) - 99
```

The deque's `maxlen` automatically drops the oldest element, and we maintain a running sum to avoid recalculating the window sum each time — O(n) total.

</details>

**Stretch++.** Design a data structure for "users who mutually follow each other" in a social network. What structure would you use? What are the operations you need to support? Sketch the interface and complexity.

<details><summary>Show solution</summary>

Use a **graph represented as an adjacency set** — a `dict[str, set[str]]` mapping each user to the set of users they follow.

```python
from collections import defaultdict

class SocialGraph:
    def __init__(self):
        self._follows: dict[str, set[str]] = defaultdict(set)

    def follow(self, user: str, target: str) -> None:
        """O(1)"""
        self._follows[user].add(target)

    def unfollow(self, user: str, target: str) -> None:
        """O(1)"""
        self._follows[user].discard(target)

    def is_mutual(self, user_a: str, user_b: str) -> bool:
        """O(1) — check both directions."""
        return user_b in self._follows[user_a] and user_a in self._follows[user_b]

    def mutual_friends(self, user_a: str, user_b: str) -> set[str]:
        """O(min(|friends_a|, |friends_b|)) — set intersection."""
        return self._follows[user_a] & self._follows[user_b]
```

Using sets for the adjacency lists gives O(1) edge existence checks and O(min(a, b)) intersection for mutual friends.

</details>

## In plain terms (newbie lane)
If `Data Structures Intro` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `list.index(x)` complexity:
    (a) O(1)  (b) O(log n)  (c) O(n)  (d) O(n log n)

2. Python's `heapq` provides:
    (a) a max-heap  (b) a min-heap  (c) a stack  (d) a queue

3. `deque.appendleft()` complexity:
    (a) O(n)  (b) O(1)  (c) O(log n)  (d) O(n log n)

4. Best structure for autocomplete prefix search:
    (a) hash map  (b) trie or sorted array with binary search  (c) linked list  (d) heap

5. Lookup in a balanced BST:
    (a) O(1)  (b) O(log n) balanced  (c) O(n) worst if unbalanced  (d) both b and c

**Short answer:**

6. Why is there no universally "best" data structure?
7. When would a linked list beat a dynamic array in practice?

*Answers: 1-c, 2-b, 3-b, 4-b, 5-d, 6-Every structure trades speed on some operations for slowness on others — no structure can be O(1) for access AND search AND insert AND delete simultaneously, 7-When you have a reference to a node and need O(1) insert/delete at that position (e.g., LRU cache implemented with a doubly-linked list + hash map), or in languages where array reallocation/copying is expensive.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-data-structures-intro — mini-project](mini-projects/06-data-structures-intro-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Every data structure is a set of trade-offs: fast access means slow search, fast search means more memory, fast insert means slow ordered traversal. Pick based on your workload's dominant operation.
- The cheat sheet (list, dict, set, heap, BST, trie, graph) covers nearly every situation. Know the complexity of each structure's key operations.
- Python's built-ins (`list`, `dict`, `set`, `deque`, `heapq`) handle 80% of needs. Reach for custom structures only when they don't fit.
- The most common performance bug in Python is using `x in list` where `x in set` would be O(1).

## Further reading

- Python docs: `collections` module — `deque`, `Counter`, `defaultdict`, `OrderedDict`.
- Python docs: `heapq` module — binary heap operations.
- `sortedcontainers` documentation — pure-Python sorted collections with excellent performance.
- Next: [Stacks](07-stacks.md).
