# Module 01 · Extended Assessment — Code Review Task

These tasks practice **reviewing code like a teammate**, not just making code pass.

## 1) Warm-up — review checklist

Create a 6-point review checklist for Module 01 code (naming, function boundaries, returns vs prints, defaults, error handling, testability).

**Success check:** Each checklist item is concrete and testable.

**What you should have learned:** Good review starts with clear standards.

## 2) Standard — review a small module

Review one solution file from `01-python/solutions/`.
Write 5 actionable comments in `practice/16-code-review-task/review-notes.md`.
Use this shape: `Observation → Why it matters → Suggested change`.

**Success check:** Comments are specific enough that the author can act without guessing.

**What you should have learned:** Useful feedback is precise and respectful.

## 3) Bug hunt — review for hidden risks

Find 3 non-style issues in sample code:

- shared mutable state,
- missing validation,
- ambiguous function contracts.

For each, provide the smallest safe refactor.

**Success check:** At least one finding references a production risk (not just readability).

**What you should have learned:** Review should catch future incidents, not just present syntax.

## 4) Stretch — standards memo (≤250 words)

Answer: _What makes a Python function “production-ready” at this level?_
Include 4 rules and one counterexample for each.

**Success check:** At least one rule explicitly covers testing/debuggability.

**What you should have learned:** Team standards reduce review churn.

## 5) Stretch++ — peer exchange

Exchange code with a peer and leave 5 substantive comments each.
Log:

- one comment you accepted,
- one comment you challenged,
- one improvement you made.

**Success check:** You can explain why each accepted change improved code quality.

**What you should have learned:** Review is collaborative engineering, not nitpicking.
