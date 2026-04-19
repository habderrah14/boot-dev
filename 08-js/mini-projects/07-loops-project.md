# Mini-project — 07-loops

_Companion chapter:_ [`07-loops.md`](../07-loops.md)

**Goal.** Build a CLI tool that reads a JSON array from a file, groups items by a user-specified key, and prints a summary table.

**Acceptance criteria:**

- Takes two CLI arguments: a JSON file path and a group-by key name.
- Reads and parses the JSON file.
- Groups items by the specified key using `reduce` or a `for...of` loop.
- Prints each group with its count and the first 3 items as a preview.
- Handles errors gracefully (file not found, invalid JSON, missing key).

**Hints:**

- Use `node:fs/promises` for reading the file.
- `process.argv[2]` and `process.argv[3]` for CLI arguments.
- A `Map` is ideal for grouping.

**Stretch:** Add a `--sort` flag that sorts groups by count (descending) before printing.
