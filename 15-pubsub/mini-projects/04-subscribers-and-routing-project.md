# Mini-project — 04-subscribers-and-routing

_Companion chapter:_ [`04-subscribers-and-routing.md`](../04-subscribers-and-routing.md)

**Goal.** Build a consumer for `user.*` events with retry logic and a separate DLX monitor.

**Acceptance criteria.**

- Consumer subscribes to `user.*` on a topic exchange with prefetch 10.
- Handler logs each event, acks on success, republishes with incremented retry count on failure.
- After 3 failures, nacks without requeue (routes to DLX).
- A separate "DLX monitor" consumer prints dead-lettered messages for inspection.
- Publish 20 messages; make 5 of them fail (e.g., missing a required field). Verify: 15 acked, 5 in DLX queue.

**Hints.** Use a header `x-attempts` to track retries. The DLX monitor is a simple consumer on the `events.dead` queue that logs and acks.

**Stretch.** Replace immediate retry with a delayed retry queue (TTL 10 seconds, DLX back to the work exchange). Verify the delay by logging timestamps.
