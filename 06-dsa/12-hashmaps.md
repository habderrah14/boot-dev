# Chapter 12 — Hashmaps

> "Hash the key, index the array, handle the collision. That's the whole trick — and it powers half the software you use."

## Learning objectives

By the end of this chapter you will be able to:

- Implement a hash table from scratch using chaining and open addressing.
- Explain how hash functions, load factor, and resizing interact to maintain O(1) average performance.
- Articulate what makes a good hash function and why Python randomizes hash seeds.
- Know when a hash map is the wrong tool and what to reach for instead.

## Prerequisites & recap

- [Math — modular arithmetic](02-math.md) — you'll use the modulo operator constantly.
- [Python dicts](../01-python/10-dictionaries.md) — `dict` is Python's built-in hash map.

## The simple version

Think of a library with numbered shelves. When a new book arrives, instead of
scanning every shelf for an empty spot, you run the book's title through a
formula that spits out a shelf number. You go straight to that shelf and
place the book. When someone asks for the book later, you run the same
formula, get the same shelf number, and grab it directly — no searching.

The formula is the *hash function*, and the shelf is the *bucket*. The
catch: two different titles might produce the same shelf number — a
*collision*. You need a plan for that. The two main strategies are
*chaining* (each shelf holds a short list) and *open addressing* (if the
shelf is taken, check the next one). As long as you don't let the shelves
get too crowded (the *load factor*), everything stays fast: O(1) average.

## Visual flow

```
  Hash table with chaining (4 buckets, 5 entries):

  key "alice"  ──hash──> 2
  key "bob"    ──hash──> 0
  key "carol"  ──hash──> 2   (collision with "alice")
  key "dave"   ──hash──> 3
  key "eve"    ──hash──> 1

  Bucket array:
  ┌─────────────────────────────────┐
  │ 0 │ → [("bob", 42)]            │
  │ 1 │ → [("eve", 99)]            │
  │ 2 │ → [("alice", 7), ──────────┤
  │   │     ("carol", 13)]         │
  │ 3 │ → [("dave", 55)]           │
  └─────────────────────────────────┘

  Lookup "carol":
    hash("carol") % 4 = 2
    Walk bucket 2: skip "alice", match "carol" → 13
```

## Concept deep-dive

### The core idea

A hash map is three things working together:

1. **An array** of size *m* (the bucket array).
2. **A hash function** `h(key)` that maps any key to an integer.
3. **A collision strategy** — what to do when `h(key1) % m == h(key2) % m`.

The index is `hash(key) % m`. Store the `(key, value)` pair there. On
lookup, compute the index, go to that bucket, and find your key.

### Hash functions — what makes a good one

A good hash function is:

- **Deterministic:** the same key always produces the same hash.
- **Uniform:** keys spread evenly across buckets. A bad hash that maps
  everything to bucket 0 turns your O(1) table into an O(n) linked list.
- **Fast:** hashing should be cheaper than the alternative (e.g., binary
  search).
- **Avalanche effect:** a small change in the key should change the hash
  dramatically. This prevents clustering.

Python's built-in `hash()` handles all this for you on immutable types.
For strings, it uses SipHash — a cryptographically-inspired hash designed
to resist collision attacks.

### Collision resolution: chaining

Each bucket holds a list (or linked list) of `(key, value)` pairs. On
collision, you append to the list. On lookup, you walk the list comparing
keys.

**Pros:** simple, never fills up, degrades gracefully.
**Cons:** pointer overhead, cache-unfriendly (each chain is a separate
allocation).

### Collision resolution: open addressing

Store all entries directly in the bucket array. On collision, *probe* for
the next empty slot:

- **Linear probing:** check index, index+1, index+2, ... Clusters badly but
  cache-friendly.
- **Quadratic probing:** check index, index+1², index+2², ... Less
  clustering.
- **Double hashing:** use a second hash function for the step size. Best
  distribution.

Python's `dict` uses open addressing with a perturbation scheme that
combines quadratic probing with bits from the full hash to scatter entries
effectively.

**Tombstones:** when you delete from an open-addressing table, you can't
just empty the slot — that would break the probe chain. Instead, mark it
as "deleted" (a tombstone). Lookups skip tombstones; inserts can reuse
them.

### Load factor and resizing

The load factor α = n / m (number of entries / number of buckets).
Performance degrades as α grows — chains get longer (chaining) or probe
sequences get longer (open addressing).

The standard rule: **resize when α > 0.7** (Python's `dict` resizes at
~2/3). Resizing means allocating a bigger array and *rehashing* every
entry — the old indices are invalid because m changed. This is O(n), but
it happens infrequently enough that inserts are O(1) amortized.

### Why O(1) average

With a uniform hash and α bounded, each bucket holds O(α) = O(1) items on
average. Lookup = compute hash O(1) + walk bucket O(1) = O(1). Worst case
is O(n) — all keys collide into one bucket — but with a good hash and
bounded load, this is astronomically unlikely.

### What makes keys hashable in Python

A key must be **immutable** and implement `__hash__` and `__eq__`.
Strings, ints, tuples (of hashables), and frozen dataclasses work. Lists
and dicts are mutable → not hashable → can't be dict keys.

**Why immutability?** If you could mutate a key after inserting it, its
hash would change, but it's still stored at the old bucket. Lookup would
go to the new bucket and miss — the entry becomes invisible.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| Chaining | Simple, handles high load gracefully; extra pointers | Teaching, or when deletions are frequent (no tombstones needed) |
| Open addressing | Cache-friendly, no pointer overhead; complex deletion | Performance-critical production code (Python's `dict` choice) |
| Resize at α = 0.7 | Balances memory vs. speed | Lower threshold (0.5) for latency-sensitive code; higher (0.9) to save memory |
| Hash randomization | Prevents DoS; hashes differ across runs | Disable with `PYTHONHASHSEED=0` for deterministic testing only |
| BST instead of hash map | O(log n) but sorted, no hash function needed | When you need sorted iteration, range queries, or min/max |

## Production-quality code

```python
from __future__ import annotations
from typing import Iterator


class HashMap:
    """Hash table with separate chaining and automatic resizing."""

    _LOAD_THRESHOLD = 0.7

    def __init__(self, capacity: int = 16) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._buckets: list[list[tuple[object, object]]] = [
            [] for _ in range(capacity)
        ]
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: object) -> bool:
        return self._find_in_bucket(key) is not None

    def __repr__(self) -> str:
        pairs = ", ".join(f"{k!r}: {v!r}" for k, v in self)
        return f"HashMap({{{pairs}}})"

    def _bucket_for(self, key: object) -> list[tuple[object, object]]:
        return self._buckets[hash(key) % len(self._buckets)]

    def _find_in_bucket(self, key: object) -> object | None:
        for k, v in self._bucket_for(key):
            if k == key:
                return v
        return None

    def set(self, key: object, value: object) -> None:
        bucket = self._bucket_for(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size / len(self._buckets) > self._LOAD_THRESHOLD:
            self._resize(len(self._buckets) * 2)

    def get(self, key: object, default: object = None) -> object:
        result = self._find_in_bucket(key)
        return result if result is not None else default

    def delete(self, key: object) -> None:
        bucket = self._bucket_for(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return
        raise KeyError(key)

    def __iter__(self) -> Iterator[tuple[object, object]]:
        for bucket in self._buckets:
            yield from bucket

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.set(key, value)
```

## Security notes

**Hash-flooding DoS.** An attacker who controls the keys sent to your server
can craft inputs that all hash to the same bucket, turning O(1) lookups into
O(n). This has been exploited against web frameworks (2011 "hash collision"
attacks on PHP, Java, Python, Ruby).

**Python's defense:** since Python 3.3, `PYTHONHASHSEED` is randomized on
every interpreter start. The hash of a string differs across runs, so an
attacker can't predict collisions without knowing the seed. This is why
`hash("abc")` gives a different number every time you restart Python.

**Practical advice:** never expose hash-table-backed structures (dicts, sets)
to unbounded adversarial input without rate limiting or input validation.

## Performance notes

| Operation | Average | Worst case | Amortized |
|---|---|---|---|
| Insert (set) | O(1) | O(n) — all collide | O(1) — resize is rare |
| Lookup (get) | O(1) | O(n) | O(1) |
| Delete | O(1) | O(n) | O(1) |
| Resize | O(n) | O(n) | — |
| Iteration | O(m + n) | O(m + n) | — |

**m** is the number of buckets, **n** the number of entries. Iteration visits
every bucket (even empty ones), so a very sparse table wastes time on empty
slots. Python's `dict` uses a compact layout that avoids this.

**Memory:** each entry stores key, value, and hash (Python's `dict` caches
the hash to speed up resizing and comparison). Chained tables also pay for
list overhead. Expect 3–5× the raw data size.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `TypeError: unhashable type: 'list'` | Used a mutable object as a dict key | Use a tuple or frozenset instead |
| 2 | Key "disappears" after mutation | Mutated an object used as a key; its hash changed but it's stored at the old index | Never mutate dict keys; use immutable types or frozen dataclasses |
| 3 | All lookups are slow (O(n)) | Degenerate hash function (e.g., always returns 0) or all keys hash to the same bucket | Use Python's built-in `hash()` or a well-tested hash function |
| 4 | Dict grows unboundedly in a long-running service | Never deleting entries; load factor stays below threshold so no OOM, but memory creeps | Implement TTL, LRU eviction, or use `WeakValueDictionary` |
| 5 | Deterministic test fails in CI | Hash randomization makes dict iteration order unpredictable across runs | Don't depend on insertion order for correctness (or set `PYTHONHASHSEED=0` in tests) |

## Practice

**Warm-up.** Compute `hash("ada")` twice in the same Python session (same
result). Restart Python and compute it again (different result). Explain why.

**Standard.** Add an `__iter__` method to the `HashMap` class that yields
`(key, value)` pairs. Verify by iterating over a map with 10 entries.

**Bug hunt.** A colleague stores `Point` objects (with mutable `x`, `y`
attributes) as dict keys. Insertions work, but lookups return `None` after
the point's `x` is changed. Explain the root cause.

**Stretch.** Add automatic resizing to the `HashMap`: when the load factor
exceeds 0.7, double the bucket count and rehash all entries.

**Stretch++.** Implement an open-addressing hash map with linear probing and
tombstone-based deletion. Benchmark against the chaining version for 100,000
inserts.

<details><summary>Show solutions</summary>

**Warm-up:** Python randomizes `PYTHONHASHSEED` on each interpreter start to
defend against hash-flooding DoS attacks. Within a single session the seed is
fixed, so `hash("ada")` is stable. Across sessions the seed changes, so the
hash differs.

**Bug hunt:** When `point.x` is mutated, `hash(point)` changes (assuming
`__hash__` depends on `x`). But the dict stored the point at the bucket
computed from the *old* hash. Looking up the point now computes the *new*
hash, goes to a different bucket, and misses. Fix: make `Point` immutable
(`@dataclass(frozen=True)`) or don't use it as a key.

**Stretch++:**

```python
class OpenAddressMap:
    _EMPTY = object()
    _TOMBSTONE = object()

    def __init__(self, capacity: int = 16) -> None:
        self._keys: list[object] = [self._EMPTY] * capacity
        self._vals: list[object] = [self._EMPTY] * capacity
        self._size = 0

    def _probe(self, key: object):
        idx = hash(key) % len(self._keys)
        while True:
            k = self._keys[idx]
            if k is self._EMPTY or k is self._TOMBSTONE or k == key:
                return idx
            idx = (idx + 1) % len(self._keys)

    def set(self, key: object, value: object) -> None:
        if self._size / len(self._keys) > 0.6:
            self._resize(len(self._keys) * 2)
        idx = self._probe(key)
        if self._keys[idx] is self._EMPTY or self._keys[idx] is self._TOMBSTONE:
            self._size += 1
        self._keys[idx] = key
        self._vals[idx] = value

    def get(self, key: object, default: object = None) -> object:
        idx = hash(key) % len(self._keys)
        while True:
            k = self._keys[idx]
            if k is self._EMPTY:
                return default
            if k == key:
                return self._vals[idx]
            idx = (idx + 1) % len(self._keys)

    def delete(self, key: object) -> None:
        idx = hash(key) % len(self._keys)
        while True:
            k = self._keys[idx]
            if k is self._EMPTY:
                raise KeyError(key)
            if k == key:
                self._keys[idx] = self._TOMBSTONE
                self._vals[idx] = self._EMPTY
                self._size -= 1
                return
            idx = (idx + 1) % len(self._keys)

    def _resize(self, new_cap: int) -> None:
        old_k, old_v = self._keys, self._vals
        self._keys = [self._EMPTY] * new_cap
        self._vals = [self._EMPTY] * new_cap
        self._size = 0
        for k, v in zip(old_k, old_v):
            if k is not self._EMPTY and k is not self._TOMBSTONE:
                self.set(k, v)
```

</details>

## In plain terms (newbie lane)
If `Hashmaps` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Average-case `dict` lookup in Python is:
    (a) O(1)  (b) O(log n)  (c) O(n)  (d) O(n²)

2. Collisions in a hash table are resolved by:
    (a) rejecting the insert  (b) chaining or open addressing
    (c) recursion  (d) ignoring duplicates

3. Python `dict` keys must be:
    (a) strings  (b) immutable and hashable  (c) integers  (d) unique and ordered

4. The load factor α equals:
    (a) m / n  (b) n / m  (c) always 1.0  (d) the collision count

5. The main symptom of a bad hash function is:
    (a) all entries land in one bucket → O(n) lookups
    (b) Python crashes
    (c) keys are reordered
    (d) out-of-memory errors

**Short answer:**

6. Why should you never mutate an object that's being used as a dict key?

7. What does Python's hash-seed randomization protect against?

*Answers: 1-a, 2-b, 3-b, 4-b, 5-a. 6) Mutation changes the hash, so the object is stored at the old bucket but lookups compute the new hash and go to a different bucket — the entry becomes invisible. 7) Hash-flooding DoS attacks where an adversary crafts keys that all collide, degrading O(1) lookups to O(n).*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [12-hashmaps — mini-project](mini-projects/12-hashmaps-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A hash map combines an array, a hash function, and a collision strategy to
  achieve O(1) average-case insert, lookup, and delete.
- Chaining stores collisions in per-bucket lists; open addressing probes for
  empty slots in the array itself. Python's `dict` uses open addressing.
- The load factor (n/m) controls performance; resize (rehash) when it exceeds
  ~0.7.
- Python's `dict` is one of the most optimized data structures in any
  language — implement your own once to appreciate it, then use `dict` in
  production.

## Further reading

- Raymond Hettinger, "Modern Python Dictionaries: A Confluence of a Dozen
  Great Ideas" (PyCon 2017 talk — still the best explanation of Python's
  dict internals).
- *CLRS* ch. 11 — Hash Tables.
- Next: [Tries](13-tries.md).
