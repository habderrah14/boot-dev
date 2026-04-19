# Mini-project — Clean Code Audit

## Goal

Refactor one messy Python module into something your future self can read in six months without a headache.

## Deliverable

A before/after refactor of a real script or module, plus a short write-up of what changed.

## Required checks

1. Rename cryptic identifiers.
2. Extract one responsibility per function.
3. Remove flag arguments.
4. Replace deep nesting with guard clauses.
5. Delete narration comments.

## Acceptance criteria

- Behavior is unchanged and backed by tests.
- Every function name describes a single responsibility.
- No boolean flags hide alternate code paths.
- The module has a brief README explaining the refactor decisions.

## Hints

- Start with the smallest, safest change: rename variables.
- Add tests before larger structural edits.
- Refactor one function at a time so diffs stay reviewable.

## Stretch goals

1. Add a `before.md` and `after.md` comparison.
2. Submit the refactor as a PR and summarize the readability wins.
3. Ask another person to review the code and record their feedback.
