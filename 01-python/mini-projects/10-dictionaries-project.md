# Mini-project — 10-dictionaries

_Companion chapter:_ [`10-dictionaries.md`](../10-dictionaries.md)

**Goal.** Build `word_index.py` — read a text file, return a dict from word → sorted list of (1-based) line numbers where the word appears (case-insensitive, punctuation stripped).

**Acceptance criteria.**

- `build_index(path: str) -> dict[str, list[int]]`.
- Words are lower-cased and stripped of trailing punctuation (`.`, `,`, `:`, `;`, `!`, `?`).
- Line numbers are unique and sorted ascending in each list.
- Empty file → empty dict.
- Tests cover: a single line, repeated words, mixed case, punctuation, empty file.

**Hints.** Use `with open(path) as f:` for the file. Use `enumerate(f, start=1)` for line numbers. `str.translate(str.maketrans("", "", ".,:;!?"))` is a fast way to strip punctuation.

**Stretch.** Add a CLI: `python3 word_index.py <file> <word>` prints just the line numbers for that word, or `not found`.
