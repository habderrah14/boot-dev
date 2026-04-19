# Mini-project — 07-scalability

_Companion chapter:_ [`07-scalability.md`](../07-scalability.md)

**Goal.** Scale a pipeline from 100 msg/s to 5,000 msg/s without changing the handler logic.

**Acceptance criteria.**

- Baseline: 1 queue, 1 consumer, prefetch 1. Measure sustained throughput.
- Tune prefetch until a single consumer peaks. Record the number.
- Add consumers until the queue drains at 5,000 msg/s (simulate a 10ms handler via `setTimeout`).
- Partition the queue into 4 with a consistent-hash exchange. Re-run and compare.
- Produce a short write-up explaining what bottleneck you hit at each step and how you relieved it.

**Hints.** Enable the `rabbitmq_consistent_hash_exchange` plugin: `rabbitmq-plugins enable rabbitmq_consistent_hash_exchange`. Use the management UI to watch queue depth in real time. Your handler is probably fine; look at DB and network first.

**Stretch.** Add monitoring: export queue depth and consumer count to a Prometheus endpoint. Create a Grafana dashboard showing the four key metrics.
