# Mini-project — No-Var Linter

## Goal

Build a small Node.js CLI that scans JavaScript files and flags any use of `var`.

## Deliverable

A command-line script plus README that runs on a directory and reports every `var` occurrence.

## Required behavior

1. Accept a directory path as an argument.
2. Recursively scan `.js` files.
3. Print file name, line number, and the line containing `var`.
4. Exit with code 1 if any `var` is found, otherwise 0.
5. Include a `--fix` mode that replaces `var` with `let` conservatively.

## Acceptance criteria

- Uses `const` and `let` throughout the linter itself.
- Handles nested directories.
- Produces readable output.
- README explains installation and usage.

## Hints

- Use `node:fs/promises` and `node:path`.
- A regex like `/\bvar\s+/` catches most cases.
- Think carefully before auto-fixing — `let` is safer than `var`, but still not always right.

## Stretch goals

1. Support `.mjs` files too.
2. Add a `--ignore node_modules` filter.
3. Add tests for the scanner helper functions.
