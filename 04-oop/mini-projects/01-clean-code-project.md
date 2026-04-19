# Mini-project — 01-clean-code

_Companion chapter:_ [`01-clean-code.md`](../01-clean-code.md)

**Goal.** Take a 50+ line script from your own work (or an open-source project) and refactor it into clean code.

**Acceptance criteria:**

- All variables and functions have intent-revealing names.
- No function exceeds ~20 lines or has more than one responsibility.
- All magic numbers are replaced with named constants.
- Nesting depth never exceeds two levels.
- Existing behavior is preserved — prove it with before/after tests.

**Hints:** Work in small commits: rename first, then extract, then flatten. Run tests after every step.

**Stretch:** Submit the refactoring as a PR with a description that explains each change and *why* readability improved.
