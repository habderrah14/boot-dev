# Mini-project — Event Flow Design

## Goal

Design the event flow for an e-commerce purchase using pub/sub concepts.

## Deliverable

An ASCII architecture diagram plus short explanatory notes.

## Required behavior

1. Model at least two events.
2. Include at least three downstream consumers.
3. Identify where work-queue and fan-out patterns are used.
4. Explain behavior when one consumer goes down.
5. Explain which consumers must be idempotent.

## Acceptance criteria

- Diagram is readable and labeled.
- Explanations show understanding of eventual consistency.
- Work-queue vs fan-out choice is justified.

## Hints

- Think about email, analytics, fulfillment, and inventory.
- Mention the broker explicitly.
- Use routing keys or queues in the diagram.

## Stretch goals

1. Add a shipment event.
2. Show replay or dead-letter handling.
3. Add a brief note comparing RabbitMQ and Kafka.
