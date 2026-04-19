# Chapter 13 — Tries

> "A trie doesn't just find your word — it finds every word that *starts like* your word."

## Learning objectives

By the end of this chapter you will be able to:

- Implement a trie with `insert`, `search`, `starts_with`, and `words_with_prefix`.
- Explain why tries beat hash maps for prefix operations and why hash maps beat tries for exact lookup.
- Analyze trie memory consumption and describe compressed (radix) tries.
- Recognize real-world use cases: autocomplete, spell checking, IP routing tables.

## Prerequisites & recap

- [Binary trees](10-binary-trees.md) — tries are trees; the same recursive thinking applies.
- [Hashmaps](12-hashmaps.md) — tries compete with hash maps for string lookups; you need to know the alternative.

## The simple version

Imagine you're building an autocomplete box. The user types "ap" and you want
to instantly show "app", "apple", "apt", "april". A hash map can check
whether "apple" exists, but it can't efficiently find *everything that starts
with "ap"* — you'd have to scan every key.

A trie stores strings character by character along tree edges. Every path
from the root spells out a prefix. To find all words starting with "ap", you
walk two edges (a → p) and then collect everything below. No scanning, no
hashing — just follow the tree.

The trade-off: each character takes a node (with a dict of children), so
tries use more memory than a flat hash map. For prefix-heavy workloads, the
speed advantage is worth it. For exact-match-only workloads, a hash map wins.

## Visual flow

```
  Trie holding ["app", "apple", "apt", "banana"]:

            (root)
           /      \
          a        b
          |        |
          p        a
         / \       |
        p   t*     n
        |          |
        l          a
        |          |
        e*         n
                   |
                   a*

  * = end-of-word marker

  starts_with("ap"):
    root → a → p  ← found! everything below is a match

  search("ap"):
    root → a → p  ← node exists but no end-of-word marker → False
```

## Concept deep-dive

### Why tries exist

Hash maps give you O(1) exact lookup, but they treat each key as an opaque
blob. They can't answer "what keys share this prefix?" without scanning
every entry. Tries exploit the *structure* of string keys — shared prefixes
share nodes, and prefix queries are just tree walks.

### The trie node

Each node holds:

- A **map** from character → child node. This can be a `dict` (flexible, any
  alphabet), an array of 26 (for lowercase English), or an array of 256 (for
  bytes).
- An **end-of-word flag** indicating that the path from root to this node
  spells a complete inserted word — not just a prefix of some longer word.

### Core operations

**Insert** — walk the tree character by character, creating nodes as needed.
Mark the final node as end-of-word. Cost: O(m) where m is the word length.

**Search** — walk the tree. If you reach the end of the word and the node has
the end-of-word flag, return `True`. If you can't follow an edge or the flag
is missing, return `False`. Cost: O(m).

**starts_with** — same as search, but you don't check the end-of-word flag.
If you can walk all prefix characters, the prefix exists. Cost: O(m).

**words_with_prefix** — walk to the prefix node, then DFS below it collecting
all end-of-word nodes. Cost: O(m + k) where k is the number of matching
words (plus the total characters in those words).

### Trie vs. hash map

| Operation | Trie | Hash map |
|---|---|---|
| Exact lookup | O(m) | O(1) average (O(m) for hashing) |
| Prefix query | **O(m + k)** | O(n) — scan all keys |
| Sorted iteration | **O(total chars)** — DFS is alphabetical | O(n log n) — sort keys |
| Space | O(total chars × node overhead) | O(n × key overhead) |

**Bottom line:** if you need prefix operations, use a trie. If you only need
exact match, use a hash map.

### Memory and compressed tries

A naive trie can use a lot of memory — every character gets its own node with
a dict. Two compression techniques help:

- **Radix tree (Patricia trie):** merge single-child chains into one node
  holding a string instead of a character. "apple" and "app" share a node
  for "app", and the "le" is a single edge.
- **Array-based children:** for small alphabets (e.g., lowercase English),
  use a 26-slot array instead of a dict. Faster lookups, fixed memory per
  node.

### Real-world use cases

- **Autocomplete** — type a prefix, get completions.
- **Spell checking** — is this word in the dictionary?
- **IP routing tables** — longest-prefix match on bit strings.
- **Longest common prefix** — walk the trie until a node has more than one
  child.
- **T9 predictive text** — map digit sequences to words.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| `dict` for children | Flexible alphabet, sparse nodes | Array of 26 when alphabet is fixed (faster, more compact) |
| End-of-word flag | Distinguishes prefixes from inserted words | Always needed — without it, `search("ap")` would return True if "apple" was inserted |
| DFS for `words_with_prefix` | Simple, alphabetical order | BFS if you want shortest words first |
| Trie over hash map | Prefix queries | Hash map when you only need exact match (simpler, faster, less memory) |
| Compressed (radix) trie | Fewer nodes, less memory | When memory is constrained and words share long prefixes |

## Production-quality code

```python
from __future__ import annotations
from typing import Iterator


class TrieNode:
    __slots__ = ("children", "end", "count")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.end: bool = False
        self.count: int = 0  # words passing through this node


class Trie:
    """Prefix tree with insert, search, prefix query, deletion, and counting."""

    def __init__(self) -> None:
        self._root = TrieNode()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, word: str) -> bool:
        return self.search(word)

    def insert(self, word: str) -> None:
        if not word:
            raise ValueError("cannot insert empty string")
        node = self._root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            node.count += 1
        if not node.end:
            node.end = True
            self._size += 1

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def count_with_prefix(self, prefix: str) -> int:
        node = self._find(prefix)
        return node.count if node is not None else 0

    def words_with_prefix(self, prefix: str) -> list[str]:
        node = self._find(prefix)
        if node is None:
            return []
        results: list[str] = []
        self._collect(node, list(prefix), results)
        return results

    def delete(self, word: str) -> bool:
        """Remove a word. Returns True if the word was present."""
        if not self.search(word):
            return False
        node = self._root
        for ch in word:
            child = node.children[ch]
            child.count -= 1
            if child.count == 0:
                del node.children[ch]
                self._size -= 1
                return True
            node = child
        node.end = False
        self._size -= 1
        return True

    def _find(self, prefix: str) -> TrieNode | None:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect(
        self, node: TrieNode, path: list[str], results: list[str]
    ) -> None:
        if node.end:
            results.append("".join(path))
        for ch in sorted(node.children):
            path.append(ch)
            self._collect(node.children[ch], path, results)
            path.pop()

    def all_words(self) -> list[str]:
        """Return all inserted words in sorted order."""
        results: list[str] = []
        self._collect(self._root, [], results)
        return results
```

## Security notes

N/A — tries are in-process data structures. The main operational risk is
**memory exhaustion**: inserting very long strings or a huge number of
distinct prefixes can consume significant memory because each character
creates a node. When accepting user input, cap the maximum word length and
the total number of entries.

## Performance notes

| Operation | Time | Space |
|---|---|---|
| Insert | O(m) per word | O(m) new nodes in the worst case |
| Search | O(m) | O(1) extra |
| starts_with | O(m) | O(1) extra |
| words_with_prefix | O(m + total chars of results) | O(results) |
| Total trie space | O(Σ unique prefixes) | — |

**m** = length of the word/prefix. **n** = number of stored words.

**Memory reality check:** a trie of 100,000 English words with a `dict`-per-
node can use 50–100 MB — far more than a `set` holding the same words.
Compressed tries (radix trees) and array-based children significantly reduce
this.

**When the trie loses:** for exact-match-only workloads, a `set` (hash table)
is O(1) amortized, uses less memory, and is simpler. Reach for a trie only
when prefix operations are required.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | `search("ap")` returns `True` but "ap" was never inserted | Missing end-of-word flag; the node exists because "apple" passes through it | Always check `node.end`, not just node existence |
| 2 | `words_with_prefix` returns millions of results | Prefix is too short (e.g., "a") and matches most of the dictionary | Paginate results or require a minimum prefix length |
| 3 | Memory usage explodes | Long strings or large alphabet with `dict` children | Use a compressed trie or array-based children; cap input length |
| 4 | Unicode characters break the trie | Assuming single-byte characters; some Unicode code points span multiple chars in UTF-16 | Iterate over Python strings (which are Unicode code points) — this works correctly by default |
| 5 | Deletion leaves orphan nodes | Removed the end flag but didn't prune empty branches | Walk back up and remove nodes with no children and no end flag |

## Practice

**Warm-up.** Insert `["cat", "car", "dog"]` into a trie. Test
`starts_with("ca")` (True) and `search("ca")` (False).

**Standard.** Implement `delete(word)` that removes a word and prunes dead
branches (nodes with no children and no end flag).

**Bug hunt.** After inserting "apple" and "app", you call `search("ap")` and
get `False`. Your colleague expected `True` because "ap" is a prefix of
"apple". Explain why `False` is the correct behavior.

**Stretch.** Add a `count` field to each node tracking how many words pass
through it. Use it to implement `count_with_prefix(prefix)` in O(m) without
DFS.

**Stretch++.** Implement a compressed trie (radix tree) that merges
single-child chains into single nodes holding substrings instead of
characters. Verify it uses fewer nodes than the standard trie for the same
word set.

<details><summary>Show solutions</summary>

**Warm-up:**

```python
t = Trie()
for w in ["cat", "car", "dog"]:
    t.insert(w)
assert t.starts_with("ca") is True
assert t.search("ca") is False
```

**Bug hunt:** `search("ap")` correctly returns `False` because "ap" was never
inserted as a complete word. The node for "ap" exists (as part of the path to
"apple" and "app"), but its `end` flag is `False`. The `search` method checks
*both* that the node exists *and* that `end` is `True`. The method
`starts_with("ap")` would return `True`.

**Stretch:**

The production code above already includes `count`. Each `insert` increments
`count` on every node along the path. `count_with_prefix("ap")` walks to the
"p" node and returns `node.count` — no DFS needed.

</details>

## In plain terms (newbie lane)
If `Tries` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Trie insert complexity for a word of length m:
    (a) O(1)  (b) O(log n)  (c) O(m)  (d) O(n)

2. For exact full-word lookup, which is usually faster?
    (a) trie  (b) hash map  (c) they're equal  (d) depends on word length

3. A trie node's children are commonly stored as:
    (a) a fixed-size array  (b) a dict  (c) a linked list
    (d) any of the above — each has trade-offs

4. Trie space can grow up to:
    (a) O(n)  (b) O(n · m) where m is average word length  (c) O(log n)  (d) O(1)

5. The end-of-word flag is needed because:
    (a) a prefix node can exist without the prefix being an inserted word
    (b) the tree must be balanced
    (c) it saves memory
    (d) it's optional

**Short answer:**

6. Give a concrete use case where a trie is clearly better than a hash map.

7. What problem does a compressed (radix) trie solve?

*Answers: 1-c, 2-b, 3-d, 4-b, 5-a. 6) Autocomplete — you need all words sharing a prefix. A hash map can't do this without scanning every key. A trie walks to the prefix node and collects descendants in O(m + k). 7) A radix trie merges chains of single-child nodes into one node holding a substring, reducing the total node count and memory usage — especially beneficial when words share long prefixes.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [13-tries — mini-project](mini-projects/13-tries-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A trie stores strings character-by-character along tree edges, making
  prefix queries — autocomplete, starts-with, longest common prefix —
  efficient at O(m) per query.
- For exact-match-only workloads, a hash map is simpler and faster. Reach
  for a trie when prefix operations are the bottleneck.
- Memory is the trie's weakness — each character gets a node. Compressed
  (radix) tries and array-based children mitigate this.
- The end-of-word flag is essential: a node existing doesn't mean the word
  was inserted.

## Further reading

- *Algorithms* by Sedgewick & Wayne, ch. 5.2 — Tries.
- Suffix arrays and suffix trees — related structures for substring search.
- Next: [Graphs](14-graphs.md).
