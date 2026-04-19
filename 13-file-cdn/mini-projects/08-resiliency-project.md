# Mini-project — 08-resiliency

_Companion chapter:_ [`08-resiliency.md`](../08-resiliency.md)

**Goal.** Wrap a flaky external API call with a full resilience stack: timeout, retries with jittered backoff, and a circuit breaker. Add metrics and load-test to validate.

**Acceptance criteria:**

- Every outbound call has a 2-second timeout.
- Failed calls retry up to 3 times with exponential backoff + jitter (200/400/800 ms base).
- After 5 failures within 30 seconds, the circuit opens and fast-fails for 30 seconds.
- When the circuit is open, a degraded response is returned (cached data or a fallback).
- Metrics track: total calls, successes, failures, retries, circuit state.
- A load test (e.g., with `autocannon` or `k6`) validates behavior under a simulated dependency outage.

**Hints:**

- Compose the patterns: `circuitBreaker.call(() => withRetry(() => fetchWithTimeout(...)))`.
- Use a simple in-memory metrics counter for prototyping; switch to Prometheus/StatsD in production.
- Simulate a flaky dependency by running a local server that returns 500 for 10 seconds, then recovers.

**Stretch:** Add a health endpoint (`GET /health`) that reports circuit breaker states. Add a Grafana dashboard (or console log) showing retry rate and circuit state over time.
