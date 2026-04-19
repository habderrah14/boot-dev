# Chapter 10 — Dictionaries

> A dict maps keys to values with average O(1) lookup. It is the workhorse of modern programming — JSON, configuration, caches, indexes, function call frames.

## Learning objectives

By the end of this chapter you will be able to:

- Create, access, and mutate a `dict`.
- Iterate keys, values, and items.
- Use `get`, `setdefault`, `pop`, `update`, and dict comprehensions idiomatically.
- Explain what *hashable* means and why mutable types can't be keys.
- Reach for `defaultdict`, `Counter`, and `OrderedDict` when they fit better.

## Prerequisites & recap

- [Lists](09-lists.md) — for-comprehensions and the cost of `x in xs`.
- [Comparisons](07-comparisons.md) — `==` is what `in dict` ultimately uses.

Recap: linear `x in list` is O(n). For repeated membership tests, hash-based structures are dramatically faster — that's the dict's superpower.

## The simple version

A dict is a **hash table** — a mapping from a *hashable* key to a value, with average O(1) get/set/in. Keys must be hashable (immutable, with a stable `__hash__`); values can be anything. Iteration walks keys in **insertion order** (guaranteed since Python 3.7).

If you reach for a list and find yourself doing `if name not in seen:`, you almost always wanted a dict (or set).

## In plain terms (newbie lane)

This chapter is really about **Dictionaries**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How a dict resolves `prices["apple"]`.

```
   key "apple"
        │
        │ hash("apple")  →  6248915983298319234
        │
        ▼
   ┌─────────────────────────────────────────────┐
   │  hash table (open addressing in CPython)    │
   │  ┌──────┬──────┬──────┬──────┬──────┐       │
   │  │  …   │bread │apple │  …   │  …   │       │
   │  └──────┴──────┴──────┴──────┴──────┘       │
   │            (slot index)                     │
   └─────────────────────────────────────────────┘
                  │
                  ▼  collision? probe next slot
              return value
```

Average O(1) for get/set/contains. Worst case O(n) under pathological collisions (rare with built-in hashes; possible if you write a bad `__hash__`).

## Concept deep-dive

### Basics

```python
prices = {"apple": 0.50, "bread": 2.40}
prices["apple"]            # 0.50
prices["butter"]           # KeyError: 'butter'
prices.get("butter")       # None  — no exception
prices.get("butter", 3.99) # 3.99  — explicit default
"apple" in prices          # True
len(prices)                # 2
```

`get` is the safer default-bearing read. `prices[k]` is right when the key *should* exist and a missing key indicates a bug worth crashing on.

### Mutation

```python
prices["eggs"] = 3.00          # set or overwrite
prices["apple"] = 0.60         # update
del prices["bread"]            # delete; KeyError if missing
prices.pop("eggs", None)       # delete; default if missing
prices.update({"milk": 1.10})  # merge (right wins on conflict)
prices |= {"oj": 4.00}         # ditto, Python 3.9+ syntax
```

### Iteration

```python
for key in prices:                      # iterates keys
    ...

for key, value in prices.items():       # idiomatic when both needed
    ...

for value in prices.values():
    ...
```

Insertion order is preserved since Python 3.7. Don't rely on iteration order matching a *sort* order; sort explicitly when you need it: `sorted(prices.items())`.

### Hashable keys

A key must be **hashable**: it must implement `__hash__` and not change while in the dict. Built-in immutables qualify (`int`, `float`, `str`, `bool`, `tuple` of hashables, `frozenset`). Mutable types (`list`, `dict`, `set`) do not.

```python
d = {(1, 2): "point"}      # ✓
d = {[1, 2]: "point"}      # TypeError: unhashable type: 'list'
```

User-defined classes are hashable by default (using `id`); override `__hash__` and `__eq__` together if you want value-based hashing.

### Idioms

**Counting:**

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```

cleaner with `defaultdict`:

```python
from collections import defaultdict
counts = defaultdict(int)
for w in words:
    counts[w] += 1
```

cleanest with `Counter`:

```python
from collections import Counter
counts = Counter(words)
counts.most_common(3)     # top three (word, count) pairs
```

**Grouping:**

```python
from collections import defaultdict
by_team = defaultdict(list)
for name, team in people:
    by_team[team].append(name)
```

**Inverting (one-to-one):**

```python
inverse = {v: k for k, v in d.items()}     # collisions silently overwrite
```

**Inverting (one-to-many):**

```python
inverse = defaultdict(list)
for k, v in d.items():
    inverse[v].append(k)
```

**Memoization:**

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

`lru_cache` is a built-in dict-backed memoizer with a size cap. Almost always preferable to hand-rolling one.

### Dict comprehension

```python
squared = {n: n * n for n in range(5)}
filtered = {k: v for k, v in items.items() if v > 0}
```

Same shape as a list comprehension but produces key-value pairs.

## Why these design choices

- **Hash tables for dicts.** O(1) average is dramatically better than the O(n) of a list of pairs. The trade-off is memory (a hash table is sparser than an array) and the hashable-key requirement. CPython's dict is one of the fastest hash tables in any popular language.
- **Insertion-order iteration.** Pre-3.7 dicts had unspecified order; relying on it caused real bugs. The 3.7+ guarantee preserves backward-compatible behavior while enabling natural patterns like JSON serialization that round-trips its key order.
- **`get` with default vs. exceptions.** Two valid styles: "ask forgiveness, not permission" (`try: d[k] except KeyError`) vs. "look before you leap" (`d.get(k, default)`). Both are Pythonic; pick by intent — `get` for "absent is normal", `[]` for "absent is a bug".
- **`Counter`/`defaultdict` over hand-rolled.** They're optimized in C and signal intent at the call site.
- **When you'd choose differently.** If you need ordered *and* range queries, a sorted container (`sortedcontainers.SortedDict`) is better. If keys can collide pathologically (untrusted hash inputs from the network), use Python's built-in randomized hash seeding (on by default) or Bloom filters / cryptographic hashes for the keys.

## Production-quality code

### Example 1 — Group people by team, defensively

```python
"""Group (name, team) pairs by team. Empty input → empty result."""

from collections import defaultdict
from typing import Iterable


def group_by_team(people: Iterable[tuple[str, str]]) -> dict[str, list[str]]:
    """Return {team: [names]}, preserving first-seen team order."""
    out: defaultdict[str, list[str]] = defaultdict(list)
    for name, team in people:
        if not team:
            raise ValueError(f"empty team for {name!r}")
        out[team].append(name)
    return dict(out)   # convert back to a plain dict for callers


if __name__ == "__main__":
    print(group_by_team([("Ada", "eng"), ("Bob", "ops"), ("Cy", "eng")]))
    # {'eng': ['Ada', 'Cy'], 'ops': ['Bob']}
```

We return a plain `dict` rather than `defaultdict` so callers don't get surprise auto-vivification later.

### Example 2 — A bounded LRU cache from `OrderedDict`

```python
"""A tiny LRU cache for when you don't want functools.lru_cache's call-frame magic."""

from collections import OrderedDict
from typing import Hashable, TypeVar, Generic

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> V | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)        # mark as most recently used
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._capacity:
            self._data.popitem(last=False) # evict least recently used

    def __len__(self) -> int:
        return len(self._data)


if __name__ == "__main__":
    c: LRUCache[str, int] = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("c", 3)
    print(c.get("a"))   # None — evicted
    print(c.get("b"))   # 2
```

`OrderedDict.move_to_end` and `popitem(last=False)` are O(1). `functools.lru_cache` is the production answer for memoizing function calls; this version generalizes to caches you control explicitly.

## Security notes

- **Hash flooding.** Attackers who control dict keys can force pathological collisions, turning O(1) into O(n). CPython mitigates with **per-process hash randomization** (on by default since 3.3); don't disable `PYTHONHASHSEED`.
- **Mass-assignment from untrusted input.** `user.__dict__.update(request_body)` is a classic vulnerability — a request body can set fields like `is_admin`. Use an allow-list or a validation library (`pydantic`, `marshmallow`) at the boundary.
- **Sensitive data in dicts.** Logging `print(config)` may dump secrets. Use a custom `__repr__` that redacts known-sensitive keys (`password`, `token`, `api_key`).

## Performance notes

- **Get / set / contains: O(1) average.** Worst case O(n) under collisions; rare in practice.
- **Iteration: O(n) but cache-friendly** — CPython 3.6+ stores dict entries in a compact array.
- **Memory:** a dict typically takes ~3–4× the bytes of an equivalent list of pairs because of the open-addressed hash table. Worth it for the lookup speed.
- **`x in dict` vs `x in list`.** `in dict` is O(1); `in list` is O(n). Converting to a `dict` (or `set`) once for repeated lookups is almost always worth the upfront copy cost.
- **Avoid `dict.keys()` for membership tests.** `k in d` is identical and shorter.

## Common mistakes

- **`KeyError` on a key you assumed exists.** Symptom: an exception in production. Cause: the data didn't match your assumption. Fix: `d.get(k, default)` or `if k in d:`.
- **Mutating a dict while iterating.** Symptom: `RuntimeError: dictionary changed size during iteration`. Cause: `del d[k]` inside `for k in d`. Fix: iterate `list(d)` or `list(d.items())`.
- **Using a list as a key.** Symptom: `TypeError: unhashable type: 'list'`. Cause: lists are mutable. Fix: use a `tuple` (or `frozenset` for sets-of-things keys).
- **Inverting a many-to-one map naively.** Symptom: missing keys in the inverse. Cause: comprehension overwrites on duplicate values. Fix: use `defaultdict(list)` and append.
- **Counting with a list of `.append`s.** Symptom: O(n²) work to count occurrences. Cause: you wrote `if x not in seen: seen.append(x); counts.append(1)`. Fix: `Counter(xs)`.

## Practice

1. **Warm-up.** Count letters in `"mississippi"` using a dict.
2. **Standard.** Invert a dict; handle value collisions by mapping each value to a list of its keys.
3. **Bug hunt.** Why does this crash and how do you fix it?

    ```python
    d = {"a": 1, "b": 2}
    for k in d:
        if k == "a":
            del d[k]
    ```

4. **Stretch.** Merge many dicts, summing values for shared keys.
5. **Stretch++.** Implement an `LFU` (least-frequently-used) cache: when capacity is exceeded, evict the key with the smallest access count, breaking ties by least-recently-used.

<details><summary>Show solutions</summary>

```python
from collections import Counter
counts = Counter("mississippi")
```

```python
from collections import defaultdict
def invert(d):
    out = defaultdict(list)
    for k, v in d.items():
        out[v].append(k)
    return dict(out)
```

3. You can't change a dict's size during iteration. Iterate a snapshot of the keys: `for k in list(d):`.

```python
from collections import Counter
def merge_sum(dicts):
    c = Counter()
    for d in dicts:
        c.update(d)
    return dict(c)
```

LFU sketch:

```python
from collections import OrderedDict, defaultdict

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.values = {}
        self.freq = defaultdict(int)
        self.bucket = defaultdict(OrderedDict)   # freq → ordered keys
        self.min_freq = 0

    def _bump(self, key):
        f = self.freq[key]
        self.bucket[f].pop(key)
        if not self.bucket[f] and self.min_freq == f:
            self.min_freq += 1
        self.freq[key] = f + 1
        self.bucket[f + 1][key] = None

    def get(self, key):
        if key not in self.values:
            return None
        self._bump(key)
        return self.values[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.values:
            self.values[key] = value
            self._bump(key)
            return
        if len(self.values) >= self.capacity:
            evict_key, _ = self.bucket[self.min_freq].popitem(last=False)
            del self.values[evict_key]
            del self.freq[evict_key]
        self.values[key] = value
        self.freq[key] = 1
        self.bucket[1][key] = None
        self.min_freq = 1
```

</details>

## Quiz

1. Missing key via `d[k]` raises:
    (a) `IndexError` (b) `KeyError` (c) returns `None` (d) returns `0`
2. `d.get("x")` returns:
    (a) `None` if missing (b) raises (c) `0` (d) empty string
3. Which can be a dict key?
    (a) `list` (b) `dict` (c) `tuple` (d) `set`
4. `for k in d:` iterates:
    (a) items (b) values (c) keys (d) undefined order
5. Best choice for counting occurrences:
    (a) `list` (b) `dict` + `get` (c) `Counter` (d) both b and c

**Short answer:**

6. What does it mean for a value to be hashable?
7. Why are dict lookups O(1) on average but worst case O(n)?

*Answers: 1-b, 2-a, 3-c, 4-c, 5-d.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-dictionaries — mini-project](mini-projects/10-dictionaries-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Dicts are hash tables: average O(1) get/set/contains, O(n) iteration, insertion-order preserved.
- Keys must be hashable; values can be anything.
- Reach for `Counter`, `defaultdict`, and `OrderedDict` when their semantics fit.
- Don't mutate during iteration; don't expose dict-shaped untrusted input directly to your model.

## Further reading

- Python docs — [`dict`](https://docs.python.org/3/library/stdtypes.html#dict), [`collections`](https://docs.python.org/3/library/collections.html).
- Raymond Hettinger's PyCon talks on the modern dict implementation.
- Next: [sets](11-sets.md).
