# Module 12 · Extended Assessment — Code Review Task

Review server-side code with a **production-readiness lens**.

## 1) Warm-up — server review rubric

Create an 8-point rubric covering:

- input validation,
- auth/authz,
- status-code correctness,
- error handling,
- logging/traceability,
- retry/idempotency safety,
- dependency boundaries,
- testability.

**Success check:** At least 3 rubric items address security/reliability directly.

**What you should have learned:** Server reviews prioritize risk, not cosmetic style.

## 2) Standard — review one endpoint slice

Pick one solution file in `12-http-servers/solutions/` and leave 6 actionable comments in `practice/12-code-review-task/review-notes.md`.
Use: `Issue → Impact → Suggested patch`.

**Success check:** At least one comment covers an error-path bug and one covers observability.

**What you should have learned:** Real quality lives in unhappy paths.

## 3) Bug hunt — find hidden production risks

Identify 3 high-risk patterns in reviewed code:

- unvalidated input path,
- silent failure/logging gap,
- non-idempotent retry danger.

Propose smallest safe fixes.

**Success check:** Each fix can be verified with one targeted test.

**What you should have learned:** Risk-oriented review prevents costly incidents.

## 4) Stretch — approval memo (≤250 words)

Write: _Would you approve this PR for production today? Why or why not?_
Include required changes and optional improvements.

**Success check:** Distinguishes blockers from non-blocking feedback.

**What you should have learned:** Strong reviewers prioritize what truly blocks shipping.

## 5) Stretch++ — reciprocal peer review

Swap endpoint code with a peer. Each reviewer leaves 7 comments and records one disagreement with rationale.
Document outcomes in `practice/12-code-review-task/peer-review-log.md`.

**Success check:** At least one design disagreement is resolved with a test or clearer requirement.

**What you should have learned:** Healthy technical disagreement improves architecture quality.
