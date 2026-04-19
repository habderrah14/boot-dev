# Module 12 · Extended Assessment — Debugging Incident Lab

Practice incident response for backend server failures under production-like constraints.

## 1) Warm-up — classify incident signals

For each symptom, classify likely category and first diagnostic step:

- intermittent 500s on one endpoint,
- latency spikes without error logs,
- works locally but fails in deploy.

**Success check:** Each classification includes one concrete command/log/query to run first.

**What you should have learned:** Fast triage starts with signal quality, not guesswork.

## 2) Standard — write a mini postmortem

Create `practice/13-debugging-incident-lab/postmortem.md` with:

- impact,
- timeline,
- root cause,
- mitigation,
- prevention.

Use a realistic server incident from this module.

**Success check:** Root cause is specific and prevention is actionable.

**What you should have learned:** Incidents are learning loops, not blame loops.

## 3) Bug hunt — diagnose three server failure patterns

Reproduce and fix:

1. request timeout due to missing abort/timeout boundary,
2. resource leak (connection/request handle not released),
3. retry storm caused by unsafe retry policy.

Document `symptom → evidence → fix` for each.

**Success check:** Each issue has a targeted verification step after fix.

**What you should have learned:** Server failures often hide in retries and cleanup paths.

## 4) Stretch — runbook draft (≤300 words)

Write a first-response runbook for `5xx spike` incidents:

- alert thresholds,
- dashboards/logs to check,
- rollback criteria,
- communication notes.

**Success check:** Runbook can be followed by another engineer without extra context.

**What you should have learned:** Operational clarity reduces MTTR.

## 5) Stretch++ — incident simulation exercise

Create one simulated incident scenario for a peer and grade their response quality.
Capture one improvement to your own runbook based on their attempt.

**Success check:** Simulation surfaces at least one missing step in your process.

**What you should have learned:** Practiced response beats theoretical response.
