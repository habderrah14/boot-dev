# Capstone 03 — Event-Driven System (after Module 15)

Extend a backend service with event-driven processing and resilient consumers.

## Goal

Demonstrate production-grade pub/sub flows with idempotency, retries, and observability.

## Requirements

- Publish domain events from service actions.
- Consume with at-least-once semantics and idempotent handler.
- Implement DLQ handling and replay strategy.
- Emit structured logs with correlation/request IDs.
- Include integration tests for duplicate and failure scenarios.

## Success criteria

- Duplicate deliveries do not create duplicate side effects.
- Failed messages route predictably to DLQ.
- Runbook explains operator actions for backlog spikes.

## Stretch

Add transactional outbox for producer reliability.
