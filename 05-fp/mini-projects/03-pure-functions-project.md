# Mini-project — 03-pure-functions

_Companion chapter:_ [`03-pure-functions.md`](../03-pure-functions.md)

**Goal.** Refactor a CLI tool that reads stdin, counts word frequencies, and writes results to stdout. Separate it into a pure `count_words(lines: Iterable[str]) -> dict[str, int]` core and an impure `main()` shell.

**Acceptance criteria:**

- [ ] `count_words` is pure: no I/O, no globals, no mutation of arguments.
- [ ] `main()` handles all I/O: reading stdin, writing stdout.
- [ ] Running `echo "hello world hello" | python wordcount.py` prints `hello: 2\nworld: 1`.
- [ ] At least three unit tests for `count_words` — no I/O in the tests.
- [ ] An optional `--top N` flag filters to the N most frequent words (logic in a separate pure function).

**Hints:**

- `collections.Counter` is a natural fit for counting.
- Your pure function should accept `Iterable[str]` (lines), not a file object.

**Stretch:** Add a `--format json` flag. Keep the formatting logic pure — a function that takes a `dict[str, int]` and returns a `str`.
