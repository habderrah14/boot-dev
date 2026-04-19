# Mini-project — Functional Core ETL

## Goal

Build a single-file ETL script with a pure transformation core and an impure I/O shell.

## Deliverable

A script that reads CSV product data, normalizes it through a composed pipeline, and writes JSON output.

## Required behavior

1. All transformation logic lives in pure functions.
2. At least three transformations are composed together.
3. I/O is isolated to `main()`.
4. The script accepts an input CSV path and an output JSON path.
5. At least two unit tests cover the pure functions.

## Acceptance criteria

- No file or network I/O appears inside transformation helpers.
- The pipeline can be tested independently of the CLI.
- Output JSON contains normalized, validated rows.
- README explains how to run and test the script.

## Hints

- Use `csv.DictReader` for input and `json.dump` for output.
- Good transforms include trimming whitespace, parsing numbers, and lowercasing categories.
- Filter invalid rows before serialization.

## Stretch goals

1. Add a `--validate` mode that prints errors to stderr.
2. Add a `pipe()` helper to chain the transforms.
3. Add a small benchmark comparing imperative vs. composed transformations.
