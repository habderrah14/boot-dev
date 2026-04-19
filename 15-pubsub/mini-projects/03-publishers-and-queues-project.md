# Mini-project — 03-publishers-and-queues

_Companion chapter:_ [`03-publishers-and-queues.md`](../03-publishers-and-queues.md)

**Goal.** Build a reusable publisher module with durable exchange, persistent messages, publisher confirms, and DLX configured.

**Acceptance criteria.**

- A `publisher.ts` module exporting `init(url)` and `publish(routingKey, payload)`.
- Uses `createConfirmChannel` and waits for confirms after each publish (or batch).
- Exchange is durable; messages are persistent with `messageId` and `timestamp`.
- DLX is configured: rejected messages route to a dead-letter queue.
- A test script publishes 100 messages, confirms all, and logs the count.
- Clean shutdown on SIGTERM closes the channel and connection.

**Hints.** Start with the production code from this chapter. Add error handling for `conn.on("error")` and `ch.on("error")`. Test by killing the consumer mid-batch to see unacked messages pile up, then restart to see redelivery.

**Stretch.** Add a batch-confirm mode: publish N messages, then call `waitForConfirms()` once. Compare throughput against per-message confirms.
