# Capstone 02 — API Client CLI (after Module 10)

Build a typed CLI that calls one external HTTP API reliably.

## Goal

Demonstrate robust HTTP client behavior: validation, retries, timeouts, and user-facing errors.

## Requirements

- Implement at least 3 commands/endpoints.
- Validate runtime payloads before use.
- Add timeout + retry with jitter for transient failures.
- Surface useful error messages without leaking internals.
- Provide tests for success and failure paths.

## Success criteria

- Works predictably with flaky network simulation.
- Includes clear README and example invocations.
- Uses typed interfaces and runtime checks together.

## Stretch

Add local cache with TTL and cache-bypass flag.
