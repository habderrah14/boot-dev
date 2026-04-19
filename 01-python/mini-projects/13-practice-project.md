# Mini-project — 13-practice

_Companion chapter:_ [`13-practice.md`](../13-practice.md)

**Goal.** Build `cli_wordcount.py` — a CLI tool that takes a filename and an optional `--top k` (default 10), prints the k most common words. Handle missing-file and empty-file gracefully.

**Acceptance criteria.**

- `python3 cli_wordcount.py file.txt --top 5` prints 5 lines: `count word`.
- Words are lowercased and stripped of trailing punctuation.
- Missing file prints `error: file not found: <path>` and exits with code `2`.
- Empty file prints `(no words)` and exits with code `0`.
- Tests cover: 3-word file, missing file, empty file, ties (deterministic order).

**Hints.** Use `argparse` for the CLI; `pathlib.Path(path).read_text()` for the file; `Counter(words).most_common(k)` for the ranking. Use `sys.exit(2)` for the not-found error.

**Stretch.** Add `--ignore-stopwords` that filters a built-in list of common English words (`the`, `and`, `of`, `a`, `to`, `in`, …).
