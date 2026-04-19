# Mini-project — 12-errors

_Companion chapter:_ [`12-errors.md`](../12-errors.md)

**Goal.** Build `csv_parse.py` — read a CSV of `(name, age)` rows. Raise a custom `RowError` carrying the offending line number for any malformed row; aggregate all bad rows and report them at the end if `strict=True`.

**Acceptance criteria.**

- `parse(path: str, strict: bool = True) -> list[tuple[str, int]]`.
- `RowError(line: int, reason: str)` is a custom exception with both fields accessible as attributes.
- In strict mode, the **first** bad row raises immediately.
- In non-strict mode, bad rows are collected; at the end, raise `MultipleRowErrors([RowError, ...])` if any.
- A test file covers: a valid CSV, one bad row in strict and non-strict modes, an empty file, a missing file (`FileNotFoundError`).

**Hints.** Use the standard `csv` module: `import csv; with open(path) as f: reader = csv.reader(f)`. Track line numbers with `enumerate(reader, start=1)`. Pre-define `MultipleRowErrors` to take and store a list of `RowError`s.

**Stretch.** Add a `--report` flag that runs in non-strict mode and prints a markdown summary table of bad rows.
