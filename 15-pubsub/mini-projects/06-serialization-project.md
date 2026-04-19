# Mini-project — 06-serialization

_Companion chapter:_ [`06-serialization.md`](../06-serialization.md)

**Goal.** Build an event bus that publishes and consumes three versions of `OrderCreated` side-by-side.

**Acceptance criteria.**

- One TypeScript module owns the v1/v2/v3 Zod schemas and a `parseOrderCreated(msg)` dispatcher.
- A publisher CLI takes a version flag (`--v 1|2|3`) and emits a message with the right `schema-version` header.
- A single consumer handles all three versions without code duplication.
- A test verifies that a message tagged with an unknown version routes to DLX rather than crashing the consumer.

**Hints.** Store the schema map as `Record<string, Record<number, ZodSchema>>` for extensibility. Use `z.discriminatedUnion` once you add multiple event names.

**Stretch.** Add a fourth version with a renamed field. Implement dual-writing in the publisher and a transform in the consumer that normalizes both field names.
