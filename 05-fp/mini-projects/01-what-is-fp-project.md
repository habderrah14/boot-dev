# Mini-project — 01-what-is-fp

_Companion chapter:_ [`01-what-is-fp.md`](../01-what-is-fp.md)

**Goal.** Write a single-file script `etl.py` that reads a CSV of product data, normalizes each row with a composed pipeline of pure functions, and writes the result as JSON.

**Acceptance criteria:**

- [ ] All transformation logic lives in pure functions (no I/O, no globals).
- [ ] A `pipe()` or `compose()` function chains at least three transformations.
- [ ] I/O (file read/write) happens only in `main()`.
- [ ] Running `python etl.py products.csv output.json` produces valid JSON.
- [ ] At least two unit tests for the pure functions (no file I/O in tests).

**Hints:**

- Transformations might include: strip whitespace from all fields, convert price strings to floats, normalize category names to lowercase, filter out rows with missing required fields.
- Use `csv.DictReader` for input and `json.dump` for output.

**Stretch:** Add a `--validate` flag that prints validation errors (missing fields, bad prices) to stderr without writing output.
