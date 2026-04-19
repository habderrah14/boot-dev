# Module 12 · Extended Assessment — System Design Primer

These tasks introduce **backend system design reasoning** using the module’s server concepts.

## 1) Warm-up — design vocabulary

Define and contrast:

- stateless vs stateful,
- latency vs throughput,
- horizontal vs vertical scaling,
- consistency vs availability,
- sync vs async boundaries,
- graceful degradation.

**Success check:** Each definition includes one practical backend example.

**What you should have learned:** Design conversations use shared terms for tradeoffs.

## 2) Standard — design a small API service

Design one service (URL shortener, voting API, or notes API) with:

- 4 endpoints,
- data model,
- auth approach,
- failure strategy,
- observability baseline.

Write in `practice/11-system-design-primer/service-design.md`.

**Success check:** Design is implementable and names at least three explicit tradeoffs.

**What you should have learned:** Good systems start simple and constraint-aware.

## 3) Bug hunt — identify scaling risks

Given your design, list 3 likely break points at 10x traffic:

- routing/load distribution,
- storage/query hot spots,
- retry/error amplification.

For each, propose a mitigation.

**Success check:** Mitigations are specific (e.g., index change, queue, cache policy), not vague.

**What you should have learned:** Anticipating failure modes is core system design work.

## 4) Stretch — capacity memo (≤300 words)

Estimate rough capacity for one endpoint:

- requests/sec,
- p95 latency target,
- DB query cost,
- expected bottleneck.

**Success check:** Includes explicit assumptions and one sensitivity check.

**What you should have learned:** Back-of-the-envelope math sharpens architecture choices.

## 5) Stretch++ — peer review design critique

Review a peer design with 5 questions on reliability, security, cost, rollout, and observability.
Capture one change you’d require before production.

**Success check:** Feedback ties directly to risk reduction.

**What you should have learned:** Design quality improves through structured critique.
