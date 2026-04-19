# Module 07 · Chapter 02 Solutions — Structs

These are **reference solutions / reasoning guides**. Your artifacts may differ; grade yourself with the success checks.

## 1) Warm-up — vocabulary and mental model

**Approach:** Start from definitions in the chapter deep-dive, then map each term to a failure mode.

**Example reasoning:** If you cannot explain *statelessness* (HTTP), *mutation* (Python), *pointer aliasing* (C), *pure function* (FP), or *normal form* (SQL) in one clause each, revisit the chapter diagrams.

**Common wrong answers:** Confusing similar terms (authn vs authz, stack vs heap, interface vs type, cluster index vs nonclustered, image vs container).

**Takeaway:** Bullet fidelity beats paragraph length.

## 2) Standard — apply the happy path

**Worked path:** (1) smallest runnable slice → (2) one automated check (`pytest`, `node --test`, `curl`, `psql -f`, `docker compose config`) → (3) freeze versions in a comment or lockfile.

**Edge cases:** Paths with spaces, ports already in use, missing env vars, TLS name mismatch, SQL `NULL` tri-state logic.

**If blocked:** Reduce scope until *one* observable output proves the happy path (status 200, row count, container `healthy`, etc.).

**Takeaway:** Shipping a thin vertical slice beats a wide stub.

## 3) Bug hunt — break it on purpose

**How to grade yourself:** Each bug should take a reviewer **>2 minutes** to spot without your hint — otherwise deepen the bug.

**Typical patterns for C17 and memory management:**
- Off-by-one / wrong comparison operator.
- Async serial vs parallel confusion.
- SQL string concatenation instead of parameters.
- Trusting client input for authz.
- Forgetting `Content-Type` / charset.
- C resource without paired `free` / `close` / `ROLLBACK`.

**Takeaway:** Bugs you manufacture intentionally become future incident intuition.

## 4) Stretch — trade-offs and failure modes

**Skeleton answer:** Default wins when team skill, ecosystem defaults, and operational tooling align. Alternatives win when **latency SLO**, **compliance**, **team size**, or **hosting constraints** dominate.

**Concrete angles for `Structs`:** cost of round-trips, blast radius of misconfiguration, observability coverage, migration pain, vendor lock-in.

**Takeaway:** Write decisions as “given X constraint, pick Y.”

## 5) Stretch++ — teach someone else

**Peer-review trick:** Swap artifacts with another learner; each asks one hostile “what if?” question.

**Common wrong answers to flag in flashcards:** Myths (“always normalize to 5NF”, “always microservices”, “Docker == VMs”, “JWT == authz”).

**Takeaway:** Flashcards that include *wrong* patterns inoculate you against interview traps.
