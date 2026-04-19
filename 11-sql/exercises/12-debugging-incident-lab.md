# Module 11 · Extended Assessment — Debugging Incident Lab

## 1) Warm-up — triage SQL failures

Classify three symptoms (slow query, lock wait, missing index) and list first diagnostic query/command for each.

**Success check:** Includes at least one `EXPLAIN (ANALYZE, BUFFERS)` and one lock-inspection query.

## 2) Standard — postmortem

Write `practice/12-debugging-incident-lab/postmortem.md` for one SQL incident: timeline, impact, root cause, fix, prevention.

## 3) Bug hunt — fix three SQL failure modes

Diagnose and fix:

1. table scan due to non-sargable predicate,
2. N+1 query loop,
3. transaction deadlock risk.

Document `symptom → evidence → fix`.

## 4) Stretch — runbook (≤250 words)

Draft an on-call runbook for `DB latency spike` including rollback and communication criteria.

## 5) Stretch++ — simulation

Run a peer simulation on one failure and capture one runbook improvement.

**Takeaway:** SQL incidents are usually visibility problems before they are syntax problems.
