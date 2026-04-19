# Mini-project — 08-queues

_Companion chapter:_ [`08-queues.md`](../08-queues.md)

**Goal.** Simulate a single-server queue: customers arrive at random intervals, each requires a random service time, and you track wait times and queue length.

**Acceptance criteria:**

- Simulate 1000 customer arrivals.
- Inter-arrival time: random exponential with mean 1.0 second.
- Service time: random exponential with mean 0.8 seconds.
- Track and report: average wait time, maximum wait time, average queue length, maximum queue length.
- Use a `deque` for the customer queue.
- Output a summary with the statistics.

**Hints:**

- Use `random.expovariate(1.0)` for exponential random variables.
- Process events chronologically: maintain a `current_time` and a `server_free_at` timestamp.
- A customer's wait time = max(0, server_free_at - arrival_time).
- This is a basic M/M/1 queue — a foundational model in queueing theory.

**Stretch:** Add a priority queue variant where VIP customers (10% of arrivals) jump to the front. Compare average wait times for VIP vs. regular customers. Use `heapq` to implement priority-based dequeuing.
