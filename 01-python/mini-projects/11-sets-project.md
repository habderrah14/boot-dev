# Mini-project — 11-sets

_Companion chapter:_ [`11-sets.md`](../11-sets.md)

**Goal.** Build `email_clean.py` — read a file of one email per line, strip duplicates **case-insensitively**, write a sorted unique list to `clean.txt`, and print a summary.

**Acceptance criteria.**

- `clean(path_in: str, path_out: str) -> dict[str, int]` returns `{"in": n_in, "unique": n_unique, "duplicates": n_in - n_unique}`.
- Comparison is case-insensitive (`Bob@X.com` and `bob@x.com` collapse).
- Empty lines and lines containing only whitespace are skipped.
- Output is sorted ascending.
- Tests cover: an empty file, one valid email, mixed-case duplicates, whitespace lines.

**Hints.** Lower-case once when adding to the set: `seen.add(line.strip().lower())`. Use `with open(...)` for both files.

**Stretch.** Add a domain breakdown: `domains_by_count` returns `Counter` of `email.split("@")[1]`.
