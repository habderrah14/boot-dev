# Mini-project — 01-pubsub-architecture

_Companion chapter:_ [`01-pubsub-architecture.md`](../01-pubsub-architecture.md)

**Goal.** Design and diagram the complete event flow for an e-commerce purchase, showing the path from payment through fulfillment, email notification, analytics tracking, and inventory update.

**Acceptance criteria.**

- ASCII diagram (no Mermaid) showing exchanges, queues, bindings, and services.
- Each flow is labeled as fan-out or work-queue with a one-sentence justification.
- At least two events are modeled (`order.placed`, `payment.confirmed`).
- A paragraph explains what happens when the email service goes down for 10 minutes.
- A paragraph identifies which consumers need idempotency and why.

**Hints.** Think about which events trigger multiple consumers (fan-out) versus which trigger parallel workers doing the same job (work queue). Fulfillment might be a work queue if you have multiple warehouse workers; email notification is fan-out alongside analytics.

**Stretch.** Add a `shipment.dispatched` event and show how the order service could update the order status by subscribing to it — demonstrating bidirectional event flow.
