# Mini-project — 02-comparisons

_Companion chapter:_ [`02-comparisons.md`](../02-comparisons.md)

**Goal.** Build `lint-loose-eq.js` — a CLI tool that scans `.js` files in a directory and flags every use of `==` or `!=` (but not `===` or `!==`).

**Acceptance criteria:**

- Takes a directory path as a CLI argument.
- Recursively scans all `.js` files.
- For each match, prints file name, line number, and the offending line.
- Ignores `===` and `!==` (don't false-positive on those).
- Exits with code 1 if any loose equality found, 0 otherwise.

**Hints:**

- A regex like `/[^!=]==[^=]/` or using a simple parser (like `acorn`) works.
- Watch out for `==` inside string literals — a regex approach will false-positive on those.

**Stretch:** Use the `acorn` parser to build an AST and find `BinaryExpression` nodes with `operator: "=="` — no false positives from strings or comments.
