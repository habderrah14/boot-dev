# Mini-project — 02-message-brokers

_Companion chapter:_ [`02-message-brokers.md`](../02-message-brokers.md)

**Goal.** Run RabbitMQ via Docker Compose, declare a complete topology with a seed script, and verify everything via the management UI.

**Acceptance criteria.**

- A `docker-compose.yml` that starts RabbitMQ with management enabled and a non-default username/password.
- A TypeScript seed script (`setup-topology.ts`) that declares: one topic exchange, three queues (user, order, audit), bindings with appropriate routing keys, and a dead-letter exchange with its queue.
- Running the seed script twice produces no errors (idempotent).
- The management UI shows all declared topology with correct bindings.
- A short `README.md` section explaining each exchange, queue, and binding.

**Hints.** Use `amqplib` for the seed script. `assertExchange` and `assertQueue` are idempotent by design. Test idempotency by running the script twice in a row.

**Stretch.** Add a health-check endpoint that connects to RabbitMQ and verifies the expected topology exists.
