# Mini-project — 13-tries

_Companion chapter:_ [`13-tries.md`](../13-tries.md)

**Goal.** Build an autocomplete CLI tool: `python autocomplete.py words.txt`.
It loads a dictionary file into a trie, prompts the user for prefixes, and
prints matching words sorted by length (shortest first).

**Acceptance criteria:**

- Loads the dictionary file and reports the number of words and load time.
- Accepts interactive prefix input (loop until the user types "quit").
- Prints up to 20 matches per prefix, sorted by length then alphabetically.
- Handles edge cases: empty prefix, no matches, very short prefix.
- Include timing for each prefix query.

**Hints:**

- `/usr/share/dict/words` is available on most Unix systems and has ~100,000
  words.
- Use `sorted(results, key=lambda w: (len(w), w))` for the sort order.

**Stretch:** Add fuzzy matching — allow one character to be wrong (edit
distance 1). This turns the problem into a BFS/DFS that explores neighboring
branches at each level.
