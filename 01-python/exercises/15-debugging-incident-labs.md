# Module 01 · Extended Assessment — Debugging Incident Labs

Tasks focus on **diagnosis and repair** of realistic failures. Use concepts from `05-testing-and-debugging.md` and earlier chapters.

## 1) Warm-up — symptom matching

Given three failing snippets, identify for each:

- error type,
- failing line,
- one likely root cause.

**Success check:** You classify each failure correctly (`NameError`, `TypeError`, `IndexError`, etc.) and cite line numbers.

**What you should have learned:** Stack traces are maps, not noise.

## 2) Standard — incident report

Take one real bug from your Module 01 work and write `practice/15-debugging-incident-labs/incident-report.md` with:

- timeline,
- symptom,
- root cause,
- fix,
- prevention.

**Success check:** Report includes exact failing input and exact fix.

**What you should have learned:** Writing incidents builds repeatable debugging habits.

## 3) Bug hunt — fix three failure patterns

Reproduce and fix three common issues:

1. mutable default argument,
2. variable shadowing/scope confusion,
3. off-by-one loop bug.

For each, document: `symptom → root cause → minimal fix`.

**Success check:** Each fix is minimal and behavior is verified with one test case.

**What you should have learned:** Patterns repeat; debugging gets faster with pattern memory.

## 4) Stretch — prevention memo (≤250 words)

Write: _Which debugging guardrails should a junior backend dev add by default?_
Include at least three from: assertions, input checks, unit tests, logging, type hints, linter.

**Success check:** Memo links each guardrail to one failure type it prevents.

**What you should have learned:** Prevention is cheaper than diagnosis.

## 5) Stretch++ — teach-back simulation

Create a 4-question mini-debug quiz for a peer:

- each question gives symptom + code,
- peer provides diagnosis + fix,
- you grade and explain one common misconception.

**Success check:** At least one misconception is surfaced and corrected.

**What you should have learned:** If you can teach debugging, you actually understand it.
