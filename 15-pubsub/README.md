# Module 15 — Learn Pub/Sub in RabbitMQ and TypeScript

> Not every request belongs in an HTTP round-trip. When work can happen later, in parallel, or on another server entirely, you reach for a message broker. RabbitMQ is the classic starting point — AMQP, battle-tested, and boringly reliable.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Pub/Sub"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Contrast request/response with publish/subscribe and explain when each fits.
- Model a system around messages, queues, exchanges, and routing keys.
- Publish and consume messages from RabbitMQ in TypeScript using `amqplib`.
- Choose appropriate delivery guarantees (at-most-once, at-least-once, exactly-once).
- Serialize messages safely and plan for schema evolution.
- Scale consumers horizontally without double-processing messages.

## Prerequisites

- [Module 12: HTTP Servers](../12-http-servers/README.md).
- [Module 14: Docker](../14-docker/README.md) (you'll run RabbitMQ via `docker run`).

## Chapter index

1. [Pub/Sub Architecture](01-pubsub-architecture.md)
2. [Message Brokers](02-message-brokers.md)
3. [Publishers and Queues](03-publishers-and-queues.md)
4. [Subscribers and Routing](04-subscribers-and-routing.md)
5. [Delivery](05-delivery.md)
6. [Serialization](06-serialization.md)
7. [Scalability](07-scalability.md)

## How this module connects

- Webhooks (Module 12) and pub/sub solve overlapping problems — you'll see the trade-off first-hand.
- Serialization ties back to JSON (Module 10) and runtime validation.

## Companion artifacts

- Exercises:
  - [01 — Pub/Sub Architecture](exercises/01-pubsub-architecture-exercises.md)
  - [02 — Message Brokers](exercises/02-message-brokers-exercises.md)
  - [03 — Publishers and Queues](exercises/03-publishers-and-queues-exercises.md)
  - [04 — Subscribers and Routing](exercises/04-subscribers-and-routing-exercises.md)
  - [05 — Delivery](exercises/05-delivery-exercises.md)
  - [06 — Serialization](exercises/06-serialization-exercises.md)
  - [07 — Scalability](exercises/07-scalability-exercises.md)
- Extended assessment artifacts:
  - [08 — Debugging Incident Lab](exercises/08-debugging-incident-lab.md)
  - [09 — Code Review Task](exercises/09-code-review-task.md)
  - [10 — System Design Prompt](exercises/10-system-design-prompt.md)
  - [11 — Interview Challenges](exercises/11-interview-challenges.md)
- Solutions:
  - [01 — Pub/Sub Architecture](solutions/01-pubsub-architecture-solutions.md)
  - [02 — Message Brokers](solutions/02-message-brokers-solutions.md)
  - [03 — Publishers and Queues](solutions/03-publishers-and-queues-solutions.md)
  - [04 — Subscribers and Routing](solutions/04-subscribers-and-routing-solutions.md)
  - [05 — Delivery](solutions/05-delivery-solutions.md)
  - [06 — Serialization](solutions/06-serialization-solutions.md)
  - [07 — Scalability](solutions/07-scalability-solutions.md)
- Mini-project briefs:
  - [01 — Event Flow Design (Bonus project)](mini-projects/01-event-flow-design.md)
  - [01 — Pub/Sub Architecture (Core chapter project)](mini-projects/01-pubsub-architecture-project.md)
  - [02 — Message Brokers](mini-projects/02-message-brokers-project.md)
  - [03 — Publishers and Queues](mini-projects/03-publishers-and-queues-project.md)
  - [04 — Subscribers and Routing](mini-projects/04-subscribers-and-routing-project.md)
  - [05 — Delivery](mini-projects/05-delivery-project.md)
  - [06 — Serialization](mini-projects/06-serialization-project.md)
  - [07 — Scalability](mini-projects/07-scalability-project.md)
- Milestone capstone:
  - [Capstone 03 — Event-Driven System](capstone/capstone-03-event-driven-system.md)

## Quiz answer key

- **Ch. 01 — Pub/Sub Architecture.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  A broker gives you buffering, retries, and fan-out without coupling the publisher to each consumer's uptime.
  - 7.  Idempotency is critical because a consumer may see the same message more than once and must avoid duplicating side effects.
- **Ch. 02 — Message Brokers.** 1) b, 2) a, 3) b, 4) a, 5) b.
- **Ch. 03 — Publishers and Queues.** 1) a, 2) b, 3) b, 4) b, 5) b.
- **Ch. 04 — Subscribers and Routing.** 1) b, 2) b, 3) a, 4) b, 5) b.
- **Ch. 05 — Delivery.** 1) b, 2) b, 3) c, 4) b, 5) c.
- **Ch. 06 — Serialization.** 1) b, 2) c, 3) b, 4) b, 5) b.
- **Ch. 07 — Scalability.** 1) b, 2) b, 3) b, 4) b, 5) c.
