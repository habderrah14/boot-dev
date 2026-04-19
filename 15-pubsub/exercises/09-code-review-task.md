# Module 15 · Extended Assessment — Code Review Task

## 1) Warm-up — review rubric

Create rubric for publisher/consumer code: ack strategy, idempotency, retry/backoff, ordering assumptions, schema evolution, observability, security.

## 2) Standard — review one solution

Review one `15-pubsub/solutions/` file and leave 6 actionable comments.

## 3) Bug hunt — hidden failure risks

Find and patch three risks: lost acks, poison message loop, unsafe deserialize path.

## 4) Stretch — approval memo

Document go/no-go with required fixes before production.

## 5) Stretch++ — peer review exchange

Do reciprocal review and log one disagreement resolved with a test.

**Takeaway:** Pub/sub review must focus on delivery guarantees and operability.
