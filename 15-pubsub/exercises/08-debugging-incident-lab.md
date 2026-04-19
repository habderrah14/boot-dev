# Module 15 · Extended Assessment — Debugging Incident Lab

## 1) Warm-up — message failure triage

Classify symptoms: consumer lag growth, duplicate deliveries, DLQ spikes. Name first check for each.

## 2) Standard — postmortem

Write `practice/08-debugging-incident-lab/postmortem.md` for one pub/sub incident with root cause and prevention.

## 3) Bug hunt — fix three broker risks

Diagnose/fix:

1. unacked message buildup,
2. non-idempotent consumer duplicates,
3. retry storm with no backoff.

## 4) Stretch — incident runbook (≤300 words)

Draft runbook for `queue backlog > threshold` with paging and rollback criteria.

## 5) Stretch++ — simulation

Simulate one failure with a peer and improve runbook based on findings.

**Takeaway:** Messaging failures are often delivery-contract failures.
