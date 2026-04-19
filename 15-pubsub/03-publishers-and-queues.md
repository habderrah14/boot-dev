# Chapter 03 — Publishers and Queues

> *"A publisher sends a message; a queue holds it until a consumer takes it. In between sits an exchange with a routing rule."*

## Learning objectives

By the end of this chapter you will be able to:

- Connect to RabbitMQ from TypeScript using `amqplib` and manage connection lifecycle.
- Declare durable exchanges and queues with idempotent `assert*` calls.
- Publish messages with `persistent: true`, `messageId`, and proper metadata.
- Use publisher confirms to know when the broker has accepted responsibility for a message.
- Configure dead-letter exchanges (DLX) for failed or expired messages.

## Prerequisites & recap

- [Message brokers](02-message-brokers.md) — you can run RabbitMQ and navigate the management UI.

## The simple version

Publishing a message is a two-step handshake. First, you tell the broker "here's a message for this exchange with this routing key." Second, the broker routes it through bindings into the appropriate queue(s), where it waits until a consumer picks it up. If you want guarantees — that the broker actually received and stored the message — you enable *publisher confirms*, which make the broker acknowledge each message after it's safely on disk. Without confirms, publishing is fire-and-forget: the `publish()` call returns instantly, but you have no idea whether the broker accepted the message, dropped it, or crashed before writing it.

The other half of this chapter is queue configuration. Queues aren't just dumb buffers — they carry policies about durability (survive restarts), dead-lettering (where rejected messages go), TTL (how long messages live), and max length (what happens when the buffer overflows). Getting these right at declaration time saves you from silent data loss in production.

## Visual flow

```
  ┌───────────┐    publish()    ┌──────────────┐
  │ Publisher  │───────────────▶│   Exchange    │
  │ (your app)│                │ events.topic  │
  └───────────┘                └──────┬───────┘
       ▲                              │ binding: "user.*"
       │ confirm                      ▼
       │ (broker ack)          ┌──────────────┐
       └───────────────────────│    Queue     │──▶ Consumer
                               │ user.events  │
                               └──────┬───────┘
                                      │ nack / TTL expired
                                      ▼
                               ┌──────────────┐
                               │  DLX Queue   │──▶ Inspection
                               │ events.dead  │
                               └──────────────┘
```
*Figure 3-1. Publisher sends to exchange; broker confirms; rejected messages route to DLX.*

## System diagram (Mermaid)

```mermaid
flowchart LR
  Pub[Publisher] --> Broker[Message_broker]
  Broker --> Q1[Queue_or_topic]
  Q1 --> SubA[Subscriber_A]
  Q1 --> SubB[Subscriber_B]
```

*Decoupled delivery: publishers never address subscribers by name.*

## Concept deep-dive

### Connecting to RabbitMQ

The `amqplib` package is the standard Node.js AMQP client. Install it:

```bash
npm install amqplib @types/amqplib
```

A connection is a TCP socket to the broker. A channel is a lightweight multiplexed session on that connection. The rule of thumb: **one connection per process, many channels on it**. Connections are expensive (TCP handshake, AMQP handshake, TLS if enabled). Channels are nearly free.

```ts
import amqp from "amqplib";

const conn = await amqp.connect(process.env.AMQP_URL ?? "amqp://localhost");
const ch = await conn.createChannel();
```

### Declaring topology with `assert*`

Before you publish, you need to ensure the exchange and queue exist. `assertExchange` and `assertQueue` are idempotent: they create the resource if it doesn't exist, or verify it matches if it does.

```ts
await ch.assertExchange("events.topic", "topic", { durable: true });
await ch.assertQueue("user.events", { durable: true });
await ch.bindQueue("user.events", "events.topic", "user.*");
```

Why declare topology in both the publisher *and* the consumer? Because either side might start first. The assert calls are safe to run from multiple processes simultaneously. In production, many teams run topology declarations in a separate migration script at deploy time — but including them in your application startup is a reasonable default.

### Publishing a message

```ts
ch.publish(
  "events.topic",          // exchange name
  "user.registered",       // routing key
  Buffer.from(JSON.stringify({ id: "abc", email: "a@b.c" })),
  {
    contentType: "application/json",
    persistent: true,
    messageId: crypto.randomUUID(),
    timestamp: Date.now(),
    headers: { source: "api" },
  }
);
```

The options matter:
- `persistent: true` — the broker writes this message to disk before confirming. Combined with a durable queue, this survives broker restarts.
- `messageId` — a unique identifier for this message. Consumers use it for idempotency (deduplication). Always set it.
- `contentType` — tells consumers how to decode the body without guessing.
- `timestamp` — when the event occurred, for ordering and debugging.

### Publisher confirms: knowing the broker got it

By default, `publish()` returns a boolean that only tells you whether the internal buffer accepted the message — it says nothing about the broker. To get real confirmation, you use a *confirm channel*:

```ts
const confirmCh = await conn.createConfirmChannel();

confirmCh.publish("events.topic", "user.registered", body, opts);
await confirmCh.waitForConfirms();
```

`createConfirmChannel()` puts the channel into publisher-confirms mode. After publishing, `waitForConfirms()` blocks until the broker has acknowledged every outstanding message on that channel. If the broker rejects a message (e.g., unroutable with `mandatory: true`), the promise rejects.

Use confirms for any data you can't afford to lose. For high-throughput telemetry where occasional loss is acceptable, regular channels are fine.

### The `mandatory` flag

When you publish with `mandatory: true`, the broker will return the message (via a `basic.return` event) if no queue is bound to receive it. Without `mandatory`, unroutable messages are silently dropped. Enable it when you want to know about routing gaps.

### Connection lifecycle and shutdown

Open one connection at startup and close it cleanly on shutdown:

```ts
process.once("SIGTERM", async () => {
  await ch.close();
  await conn.close();
});
```

Don't create a channel per publish — the overhead adds up and you'll exhaust broker resources under load. Don't create a connection per publish — that's dramatically worse.

### Dead-letter exchanges (DLX)

When a message is rejected by a consumer (`nack` without requeue), expires due to TTL, or is dropped because the queue hit its max length — the broker can send it to a *dead-letter exchange* instead of discarding it. Configure this at queue declaration time:

```ts
await ch.assertQueue("user.events", {
  durable: true,
  deadLetterExchange: "events.dlx",
});
```

Route the DLX to a dedicated dead-letter queue that you monitor:

```ts
await ch.assertExchange("events.dlx", "fanout", { durable: true });
await ch.assertQueue("events.dead", { durable: true });
await ch.bindQueue("events.dead", "events.dlx", "");
```

A DLX is critical for observability. Without it, rejected messages vanish silently, and you'll never know that your consumer is failing 2% of its workload.

### Message properties reference

| Property | Purpose |
|---|---|
| `contentType` | MIME type (`application/json`, `application/x-protobuf`) |
| `messageId` | Unique ID for idempotency / deduplication |
| `correlationId` | Ties related messages together (request-reply, tracing) |
| `replyTo` | Reply queue for request/response over broker |
| `timestamp` | When the event occurred (Unix ms) |
| `expiration` | Per-message TTL in milliseconds (string) |
| `priority` | Queue-level priority (0–9) |
| `headers` | Arbitrary key-value metadata |

### Transactions vs confirms

AMQP defines `tx.select` / `tx.commit` transactions. They work, but they're approximately **250x slower** than publisher confirms because they synchronize at the protocol level. The RabbitMQ docs explicitly recommend confirms over transactions. Use confirms.

## Why these design choices

**Why `persistent: true` isn't the default?** Because persistence has a cost — disk I/O. Many messages (telemetry, heartbeats, debug events) genuinely don't need to survive a broker restart, and forcing persistence on them wastes IOPS. The explicit opt-in forces you to think about which messages matter.

**Why UUIDs for `messageId`?** Because consumers need a stable, unique key for deduplication. If two instances of your publisher are running and both process the same database row, they'll produce two messages with different `messageId` values — the consumer can detect and skip the duplicate. Without `messageId`, deduplication requires fragile heuristics.

**Why DLX instead of just logging failures?** Because a DLX keeps the message *intact* in the broker, where you can inspect its full body, headers, and properties. A log entry captures only what you remembered to log. DLX queues also let you *replay* failed messages back into the work queue after fixing the consumer bug.

**When you'd pick differently:** If you're on AWS, SQS handles dead-letter queues natively with a `RedrivePolicy`. If you're using Kafka, failed messages typically go to a separate "error" topic. The DLX concept is RabbitMQ-specific but the pattern (route failures somewhere inspectable) is universal.

## Production-quality code

```ts
// publisher.ts — production publisher with confirms, DLX, and clean shutdown
import amqp, { type ConfirmChannel, type Connection } from "amqplib";
import { randomUUID } from "crypto";

const EXCHANGE = "events.topic";
const DLX_EXCHANGE = "events.dlx";
const DLX_QUEUE = "events.dead";

let conn: Connection;
let ch: ConfirmChannel;

export async function initPublisher(url: string): Promise<void> {
  conn = await amqp.connect(url);
  ch = await conn.createConfirmChannel();

  await ch.assertExchange(EXCHANGE, "topic", { durable: true });
  await ch.assertExchange(DLX_EXCHANGE, "fanout", { durable: true });
  await ch.assertQueue(DLX_QUEUE, { durable: true });
  await ch.bindQueue(DLX_QUEUE, DLX_EXCHANGE, "");

  conn.on("error", (err) => {
    console.error("AMQP connection error", err);
    process.exit(1);
  });

  process.once("SIGTERM", shutdown);
  process.once("SIGINT", shutdown);
}

export async function publish(
  routingKey: string,
  payload: unknown,
): Promise<void> {
  const body = Buffer.from(JSON.stringify(payload));

  ch.publish(EXCHANGE, routingKey, body, {
    contentType: "application/json",
    persistent: true,
    mandatory: true,
    messageId: randomUUID(),
    timestamp: Date.now(),
  });

  await ch.waitForConfirms();
}

async function shutdown(): Promise<void> {
  try {
    await ch.close();
    await conn.close();
  } catch {
    // already closing
  }
  process.exit(0);
}
```

```ts
// usage example
import { initPublisher, publish } from "./publisher.js";

await initPublisher(process.env.AMQP_URL ?? "amqp://localhost");

await publish("user.registered", {
  id: "u-123",
  email: "alice@example.com",
  registeredAt: new Date().toISOString(),
});

console.log("Event published and confirmed");
```

## Security notes

- **Connection strings.** Store `AMQP_URL` in environment variables, never in source code. The URL often contains credentials (`amqp://user:pass@host`).
- **Least-privilege accounts.** In production, create a RabbitMQ user that can only publish to specific exchanges and declare specific queues. Don't use the admin account for application connections.
- **Message content.** Don't put secrets, tokens, or passwords in message payloads. If a consumer needs a secret to act on an event, it should fetch it from a vault or config service.

## Performance notes

- **Channel-per-publish anti-pattern.** Creating a channel costs a round-trip to the broker. At 1,000 publishes/second, that's 1,000 extra round-trips. Reuse channels; create one per publisher thread or worker.
- **Batch confirms.** `waitForConfirms()` blocks until all outstanding publishes on the channel are confirmed. Publishing 100 messages then calling `waitForConfirms()` once is much faster than calling it after each individual publish. The trade-off: a larger batch means more messages to republish if the batch fails.
- **`persistent: true` throughput.** Persistent messages halve throughput compared to transient because of fsync. For non-critical data (metrics, logs), use transient messages on non-durable queues.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Messages disappear after broker restart | `persistent: true` missing on publish, even though the queue is durable | Set `persistent: true` in publish options; durable queue alone only preserves the queue definition, not the messages |
| Creating a new channel for every publish | Misunderstanding the channel lifecycle; massive overhead under load | Create one channel at startup; reuse it for all publishes in that process |
| Publisher doesn't know messages were dropped | Publishing without confirms; `publish()` returns `true` but the broker may have discarded the message | Use `createConfirmChannel()` and `waitForConfirms()` for critical data |
| Rejected messages vanish with no trace | No DLX configured on the queue; `nack` without requeue silently discards | Configure `deadLetterExchange` at queue declaration; monitor the DLX queue |
| Topology mismatch at startup | Publisher asserts queue with different options than the consumer declared previously | Use identical `assertQueue` options everywhere; or run topology declaration in a single migration script |

## Practice

**Warm-up.** Connect to your local RabbitMQ. Publish a single "hello" message to a fanout exchange. Verify it appears in a bound queue via the management UI.

<details><summary>Show solution</summary>

```ts
import amqp from "amqplib";

const conn = await amqp.connect("amqp://localhost");
const ch = await conn.createChannel();

await ch.assertExchange("hello.fanout", "fanout", { durable: false });
await ch.assertQueue("hello.queue", { durable: false });
await ch.bindQueue("hello.queue", "hello.fanout", "");

ch.publish("hello.fanout", "", Buffer.from("hello world"));

console.log("Published. Check management UI → Queues → hello.queue");
await ch.close();
await conn.close();
```

</details>

**Standard.** Publish a JSON event with `messageId`, `timestamp`, `contentType`, and `persistent: true`. Use a confirm channel and log the confirmation.

<details><summary>Show solution</summary>

```ts
import amqp from "amqplib";
import { randomUUID } from "crypto";

const conn = await amqp.connect("amqp://localhost");
const ch = await conn.createConfirmChannel();

await ch.assertExchange("events.topic", "topic", { durable: true });
await ch.assertQueue("user.events", { durable: true });
await ch.bindQueue("user.events", "events.topic", "user.*");

ch.publish(
  "events.topic",
  "user.registered",
  Buffer.from(JSON.stringify({ id: randomUUID(), email: "test@test.com" })),
  {
    contentType: "application/json",
    persistent: true,
    messageId: randomUUID(),
    timestamp: Date.now(),
  },
);

await ch.waitForConfirms();
console.log("Broker confirmed the message");

await ch.close();
await conn.close();
```

</details>

**Bug hunt.** Your teammate says "we lose about 1% of messages on broker restart." The queues are durable. What's the likely cause?

<details><summary>Show solution</summary>

Messages are published without `persistent: true`. A durable queue preserves the queue *definition* on restart, but transient messages (the default) live in memory and are lost when the broker process stops. Fix: add `persistent: true` to every `publish()` call for important messages, and use publisher confirms so you'd notice if any message failed to persist.

</details>

**Stretch.** Enable publisher confirms and publish 1,000 messages. Measure the time with confirms vs without. Report the throughput difference.

<details><summary>Show solution</summary>

Two approaches: (1) `waitForConfirms()` after each individual publish, or (2) batch — publish all 1,000, then call `waitForConfirms()` once. Individual confirms are the slowest (one round-trip per message). Batched confirms are near-equal to no-confirms. Typical results on localhost: no-confirms ~50,000 msg/s, batched confirms ~40,000 msg/s, per-message confirms ~5,000 msg/s. The batch approach is the recommended production pattern.

</details>

**Stretch++.** Configure a DLX on a queue. Publish a message, then manually reject it from the management UI (or write a consumer that `nack`s it without requeue). Verify the message appears in the dead-letter queue.

<details><summary>Show solution</summary>

```ts
await ch.assertExchange("events.dlx", "fanout", { durable: true });
await ch.assertQueue("events.dead", { durable: true });
await ch.bindQueue("events.dead", "events.dlx", "");

await ch.assertQueue("work.queue", {
  durable: true,
  deadLetterExchange: "events.dlx",
});
await ch.bindQueue("work.queue", "events.topic", "work.*");

// publish a message
ch.publish("events.topic", "work.test", Buffer.from("test"), {
  persistent: true,
});

// consume and nack without requeue
await ch.consume("work.queue", (msg) => {
  if (!msg) return;
  console.log("Rejecting message to DLX");
  ch.nack(msg, false, false); // requeue = false → routes to DLX
});

// check events.dead queue in the management UI — the message should appear there
```

</details>

## In plain terms (newbie lane)
If `Publishers And Queues` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A persistent message survives a broker restart only when:
    (a) the queue is also durable (b) nothing else is needed (c) only the exchange is durable (d) confirms are disabled

2. The relationship between connections and channels is:
    (a) they're the same thing (b) one connection, many channels (c) one channel, many connections (d) unrelated concepts

3. The default behavior of `publish()` is:
    (a) confirmed by the broker (b) fire-and-forget into the buffer (c) synchronous and blocking (d) batched automatically

4. A dead-letter exchange captures:
    (a) duplicated messages (b) rejected or expired messages (c) only new messages (d) nothing — it's decorative

5. `messageId` is primarily used for:
    (a) routing decisions (b) consumer-side idempotency and deduplication (c) timing (d) authentication

**Short answer:**

6. Why should you use publisher confirms for important events, even though they reduce throughput?

7. Give one reason to declare topology in a migration script rather than in each process.

*Answers: 1-a, 2-b, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-publishers-and-queues — mini-project](mini-projects/03-publishers-and-queues-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP webhooks](../12-http-servers/09-webhooks.md) — synchronous cousin to async messaging.
  - [JSON and serialization](../10-http-clients/06-json.md) — message payloads cross language boundaries.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- One connection per process, many channels. Channels are the unit of work; connections are the unit of TCP.
- Durable queue + persistent message = survives broker restarts. You need both — one without the other still loses data.
- Publisher confirms tell you the broker accepted responsibility. Without them, `publish()` is fire-and-forget.
- Dead-letter exchanges catch rejected and expired messages. Without them, failures are invisible.

## Further reading

- [amqplib documentation](https://amqp-node.github.io/amqplib/) — the Node.js AMQP client API reference.
- [RabbitMQ — Publisher Confirms](https://www.rabbitmq.com/confirms.html) — official guide.
- Next: [subscribers and routing](04-subscribers-and-routing.md).
