# Mini-project — 01-variables

_Companion chapter:_ [`01-variables.md`](../01-variables.md)

**Goal.** Build `lint-no-var.js` — a CLI script that scans all `.js` files in a directory and flags every `var` usage.

**Acceptance criteria:**

- Takes a directory path as a CLI argument.
- Recursively finds all `.js` files.
- Prints each `var` occurrence with file name, line number, and the offending line.
- Exits with code 1 if any `var` found, 0 otherwise.

**Hints:**

- Use `node:fs/promises` and `node:path` for file operations.
- A simple regex like `/\bvar\s+/` catches most cases.
- Use `const` and `let` throughout — no `var` in your own linter!

**Stretch:** Add a `--fix` flag that replaces `var` with `let` (a conservative default) and writes the file back.
