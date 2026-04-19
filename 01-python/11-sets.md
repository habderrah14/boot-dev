# Chapter 11 — Sets

> A set is a bag of unique hashable values. Reach for one the moment you catch yourself writing `if x not in some_list:`.

## Learning objectives

By the end of this chapter you will be able to:

- Create a `set` and `frozenset` and pick correctly between them.
- Use set operations: union, intersection, difference, symmetric difference, subset.
- Choose a set when membership or deduplication is the dominant operation.
- Avoid the `{}` empty-set trap.

## Prerequisites & recap

- [Dictionaries](10-dictionaries.md) — sets reuse the same hashing mechanism.

Recap: dict lookup is O(1) on average because of hashing. A set is essentially a dict with no values — the same fast-membership trick.

## The simple version

A set holds **unique, hashable** elements with **O(1) average** membership tests, additions, and removals. Order is not guaranteed (insertion-order is *not* preserved like in dicts). For algorithms involving "is this here?", "are these the same?", or "what's in both?", a set is almost always the right answer.

## In plain terms (newbie lane)

This chapter is really about **Sets**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

Set operations as Venn diagrams.

```
        ┌─────────────────┐         ┌─────────────────┐
        │       A         │         │       B         │
        │   ┌─────────────┼─────────┼──────────┐      │
        │   │     A ∩ B (intersection)        │      │
        │   └─────────────┼─────────┼──────────┘      │
        └─────────────────┘         └─────────────────┘
              A - B            A ∩ B          B - A
              ─────            ─────          ─────
        only in A              in both        only in B

        A ∪ B = everything in either
        A ^ B = (A - B) ∪ (B - A)  — symmetric difference
        A <= B → every element of A is in B  (subset)
```

## Concept deep-dive

### Creating

```python
s = {1, 2, 3}                  # set literal
empty = set()                  # ⚠ NOT {} — that's a dict
from_list = set([1, 2, 2, 3])  # {1, 2, 3} — duplicates collapse
chars = set("hello")           # {'h', 'e', 'l', 'o'} — unordered
```

`{}` is the empty *dict*, not the empty set. This is the one syntax wart of Python sets.

### Set operations

```python
a = {1, 2, 3}
b = {3, 4, 5}

a | b      # union          {1, 2, 3, 4, 5}
a & b      # intersection   {3}
a - b      # difference     {1, 2}
a ^ b      # sym diff       {1, 2, 4, 5}

a <= b     # subset?
a < b      # strict subset?
a >= b     # superset?
a.isdisjoint(b)   # True iff no overlap

3 in a     # True, O(1)
```

The methods (`a.union(b)`, `a.intersection(b)`, …) accept any iterable; the operators require both sides to be sets.

### Mutation

```python
a.add(4)
a.update([5, 6, 7])    # add many
a.remove(4)            # KeyError if missing
a.discard(99)          # silent if missing
a.pop()                # remove an arbitrary element
a.clear()              # empty in place
```

In-place equivalents of the binary operators: `a |= b`, `a &= b`, `a -= b`, `a ^= b`.

### `frozenset`

Immutable, hashable. Can be a dict key, a set element, or returned from a function safely (callers can't mutate it).

```python
groups = {frozenset({"ada", "bob"}), frozenset({"cy"})}    # set of teams
SAFE_HEADERS = frozenset({"User-Agent", "Accept"})         # constant lookup
```

If a function returns "the immutable result of a computation", use `frozenset` to communicate that semantically and prevent accidental mutation.

### When to use which

| Task                                | Best structure                                  |
|-------------------------------------|-------------------------------------------------|
| many membership checks              | `set`                                           |
| remove duplicates (order matters)   | `list(dict.fromkeys(xs))` (preserves order)     |
| remove duplicates (order doesn't)   | `set(xs)`                                       |
| count occurrences                   | `Counter`                                       |
| sorted unique                       | `sorted(set(xs))`                               |
| keep sorted, unique, fast inserts   | `sortedcontainers.SortedSet` (third-party)      |
| return immutable result             | `frozenset(...)`                                |

## Why these design choices

- **Sets are dicts without values.** The same hash-table machinery powers both. CPython could have skipped sets and asked you to use `dict.fromkeys`, but a dedicated type signals intent and exposes the algebraic operations cleanly.
- **No order guarantee.** Sets are about membership, not sequence. Maintaining insertion order would slow inserts and isn't useful for set algebra. If order matters, use a list-with-set-for-seen pattern.
- **`{}` is the empty dict.** A historical accident; dicts existed first and grabbed the curly-brace literal. Live with `set()`.
- **`frozenset` for immutability.** Mirrors the `list`/`tuple` pair. Lets sets-of-sets and dict keys work.
- **When you'd choose differently.** For *streaming* uniqueness over millions of items, a Bloom filter trades exactness (false positives) for orders-of-magnitude less memory. For *cryptographic* set membership (private set intersection), specialized libraries — but those are advanced.

## Production-quality code

### Example 1 — Friends-in-common

```python
"""Set algebra over real-world membership data."""

from collections.abc import Iterable


def common_friends(a: Iterable[str], b: Iterable[str]) -> set[str]:
    """Return everyone who is a friend of both."""
    return set(a) & set(b)


def either_friend(a: Iterable[str], b: Iterable[str]) -> set[str]:
    return set(a) | set(b)


def exclusive(a: Iterable[str], b: Iterable[str]) -> set[str]:
    """Friends of exactly one — symmetric difference."""
    return set(a) ^ set(b)


if __name__ == "__main__":
    alice = ["bob", "cy", "dan"]
    bob = ["cy", "dan", "eve"]
    print(common_friends(alice, bob))   # {'cy', 'dan'}
    print(exclusive(alice, bob))        # {'bob', 'eve'}
```

Each function reads as English and is one operator wide. That's the standard library doing its job.

### Example 2 — Order-preserving deduplication

```python
"""Two ways to dedupe a list, both O(n)."""

from typing import Iterable, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


def unique_seen(xs: Iterable[T]) -> list[T]:
    """Order-preserving uniqueness via a 'seen' set."""
    seen: set[T] = set()
    out: list[T] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def unique_dictkeys(xs: Iterable[T]) -> list[T]:
    """Order-preserving uniqueness via dict.fromkeys (Python 3.7+)."""
    return list(dict.fromkeys(xs))
```

`dict.fromkeys` is shorter and equally fast. Use it when readability matters; use the explicit `seen` set when you need to do extra work per item.

## Security notes

- **Hash flooding.** Sets share dict's hash-table implementation. Per-process hash randomization (on by default) mitigates adversarial inputs; don't disable `PYTHONHASHSEED`.
- **Sensitive data in sets.** Just like dicts, a `print(secrets_set)` will dump everything. If you must inspect, redact or hash before logging.
- **Set difference for ACL checks.** A common pattern: `forbidden = required - present` then `if forbidden: deny()`. It's correct and clear; the bug is when you compare strings case-sensitively (`"GET"` vs `"get"`) — normalize before set construction.

## Performance notes

- `add`, `remove`, `in`: average O(1).
- `len`, iteration: O(n).
- Set algebra (`a & b`, `a | b`, `a - b`): O(min(|a|, |b|)) for intersection, O(|a| + |b|) for union/difference.
- For very small `n` (under ~10 items), a list scan can outperform a set due to hashing overhead. Don't reflexively reach for a set on a 5-item collection.
- Memory: a set takes ~3× the bytes of a list of the same elements due to the hash table.

## Common mistakes

- **`{}` is a dict, not a set.** Symptom: `{} | {1}` works but `{}.add(1)` raises `AttributeError`. Cause: `{}` parses as an empty dict. Fix: `set()`.
- **Iteration order assumed.** Symptom: tests pass locally, fail in CI. Cause: relying on set order. Fix: `sorted(s)` when order matters in output.
- **Putting unhashables in a set.** Symptom: `TypeError: unhashable type: 'list'`. Cause: list is mutable. Fix: convert to `tuple` or `frozenset` first.
- **Using a set for "ordered unique".** Symptom: output order is randomized. Fix: `dict.fromkeys` or the seen-set pattern above.
- **Set algebra on non-sets without conversion.** Symptom: `[1, 2] & [2, 3]` raises `TypeError`. Cause: list has no `&`. Fix: `set([1,2]) & set([2,3])`.

## Practice

1. **Warm-up.** Dedupe `[1, 1, 2, 3, 3, 4]` into a sorted list.
2. **Standard.** Given two lists, return a sorted list of items in **both**.
3. **Bug hunt.** Why does this raise?

    ```python
    set([[1, 2], [3, 4]])
    ```

4. **Stretch.** Given a list of strings, return only those that are anagrams of the first string (case-insensitive).
5. **Stretch++.** Implement `power_set(xs: list)` returning a `list[frozenset]` of every subset (including the empty set).

<details><summary>Show solutions</summary>

```python
sorted(set([1, 1, 2, 3, 3, 4]))
```

```python
sorted(set(a) & set(b))
```

3. Lists are mutable and therefore unhashable. Wrap in tuples: `set([(1, 2), (3, 4)])`.

```python
def anagrams(words):
    target = sorted(words[0].lower())
    return [w for w in words if sorted(w.lower()) == target]
```

```python
from itertools import combinations

def power_set(xs):
    return [frozenset(c) for n in range(len(xs) + 1) for c in combinations(xs, n)]
```

</details>

## Quiz

1. Empty set literal:
    (a) `{}` (b) `set()` (c) `[]` (d) `()`
2. `{1, 2, 3} & {2, 3, 4}`:
    (a) `{1, 2, 3, 4}` (b) `{2, 3}` (c) `{1, 4}` (d) `{}`
3. `len({1, 1, 1})`:
    (a) 1 (b) 3 (c) undefined (d) error
4. A set can contain:
    (a) lists (b) dicts (c) tuples of ints (d) sets
5. Best structure for "is x in this 1M-item collection, repeatedly":
    (a) list (b) tuple (c) set (d) deque

**Short answer:**

6. Name two differences between set and list.
7. Why are sets ideal for deduplication?

*Answers: 1-b, 2-b, 3-a, 4-c, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-sets — mini-project](mini-projects/11-sets-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Sets store unique hashable elements with O(1) average membership.
- Use them for dedup and set algebra; use `frozenset` when immutability matters.
- `{}` is a dict; the empty set is `set()`.
- For ordered-unique, use `dict.fromkeys` or the seen-set pattern.

## Further reading

- Python docs — [*Set Types*](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset).
- Bloom filters — when set-membership at scale outgrows RAM.
- Next: [errors](12-errors.md).
