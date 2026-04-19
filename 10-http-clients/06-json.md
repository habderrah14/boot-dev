# Chapter 06 — JSON

> "JSON is the default wire format for web APIs. It's simple, but it's not a schema; every JSON you receive needs validation."

## Learning objectives

By the end of this chapter you will be able to:

- Serialize and parse JSON in TypeScript, knowing exactly what `JSON.stringify` and `JSON.parse` do and don't handle.
- Handle edge types — dates, BigInts, `undefined`, and cycles — that JSON doesn't natively support.
- Detect and recover from malformed JSON safely.
- Integrate JSON parsing with `fetch` and explain why `JSON.parse` returns `any`.

## Prerequisites & recap

- [Headers](05-headers.md) — you know `Content-Type: application/json` signals a JSON body.
- [Types](../09-ts/01-types.md) — you understand TypeScript's type system.

## The simple version

JSON (JavaScript Object Notation) is a text format for structured data. It's the default language that APIs use to send data back and forth. You turn a JavaScript object into a JSON string with `JSON.stringify`, and you turn a JSON string back into a JavaScript value with `JSON.parse`.

The catch: JSON only supports six types — strings, numbers, booleans, null, arrays, and objects. It has no concept of `Date`, `BigInt`, `undefined`, `Map`, `Set`, or functions. Anything outside those six types either gets silently dropped or throws. And `JSON.parse` returns `any` — TypeScript can't know what shape the data has at compile time, so you must validate at runtime.

## In plain terms (newbie lane)

This chapter is really about **JSON**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  TypeScript world                    Wire (JSON text)
  ┌──────────────┐   stringify   ┌──────────────────┐
  │ { id: 1,     │─────────────▶│ {"id":1,         │
  │   name: "Ada"│              │  "name":"Ada"}    │
  │   active: un-│  (undefined  │                   │
  │   defined }  │   is dropped)│                   │
  └──────────────┘              └────────┬─────────┘
                                         │
                                         │ parse
                                         ▼
                                ┌──────────────────┐
                                │ unknown           │
                                │ (actually `any`   │
                                │  — validate it!)  │
                                └────────┬─────────┘
                                         │
                                         │ validate (Zod, etc.)
                                         ▼
                                ┌──────────────────┐
                                │ User              │
                                │ (typed, safe)     │
                                └──────────────────┘
```

*JSON is a lossy serialization. What goes in isn't always what comes out. Validate after parsing.*

## Concept deep-dive

### The basics

```ts
const obj = { id: 1, name: "Ada" };
const jsonString = JSON.stringify(obj);     // '{"id":1,"name":"Ada"}'
const parsed = JSON.parse(jsonString);       // type is `any`
```

JSON supports exactly these types:

| JSON type | JavaScript equivalent |
|-----------|----------------------|
| string | `string` |
| number | `number` (finite IEEE-754 only) |
| boolean | `boolean` |
| null | `null` |
| array | `Array` |
| object | plain `Object` (no class methods) |

What JSON does **not** support: `undefined`, `BigInt`, `Date`, `Map`, `Set`, `RegExp`, `Infinity`, `NaN`, functions, symbols, or circular references. You need to handle each of these yourself.

### `JSON.stringify` behavior and options

**Replacer** — filter or transform values during serialization:

```ts
JSON.stringify(obj, null, 2);               // pretty-print with 2-space indent
JSON.stringify(obj, ["id", "name"]);        // only include these keys
JSON.stringify(obj, (key, value) =>         // custom transform
  typeof value === "bigint" ? value.toString() : value
);
```

**What gets silently dropped:**

- Properties with `undefined` values → removed entirely.
- Properties with `function` values → removed entirely.
- `Symbol` keys → removed entirely.

This is a deliberate choice: JSON is a data interchange format, and these JavaScript-specific constructs have no representation in other languages.

### `JSON.parse` and the reviver

`JSON.parse` returns `any`. TypeScript's type system cannot enforce the shape of data that arrives at runtime. You can cast it, but that's a lie — see [ch. 10](10-runtime-validation.md) for the real fix.

A **reviver** function lets you transform values during parsing:

```ts
const data = JSON.parse(jsonString, (key, value) =>
  key === "createdAt" ? new Date(value) : value
);
```

Why use a reviver? Because the server sends dates as ISO strings (`"2026-04-16T10:00:00Z"`), but your code wants `Date` objects. The reviver converts them during parsing so the rest of your code works with rich types.

### Dates

JSON has no date type. The convention is ISO 8601 strings:

```ts
const user = { name: "Ada", createdAt: new Date().toISOString() };
JSON.stringify(user);
// '{"name":"Ada","createdAt":"2026-04-16T10:00:00.000Z"}'
```

When you parse this back, `createdAt` is a *string*, not a `Date`. You must convert it yourself — either with a reviver or in your validation layer.

Why ISO 8601? Because it's unambiguous, sortable, timezone-aware, and universally understood. Unix timestamps (seconds since epoch) are also common but lose timezone information and are harder for humans to read.

### BigInt

`JSON.stringify(1n)` throws a `TypeError`. BigInt is not representable in JSON because JSON numbers are IEEE-754 doubles, and BigInt can exceed their range.

Your options:

1. **Serialize as string** — `"12345678901234567890"` — and parse back with `BigInt()`.
2. **Use a replacer/reviver pair** — automate the conversion.
3. **Use a library** like `json-bigint` — handles it transparently but adds a dependency.

### Error handling

Both `JSON.stringify` and `JSON.parse` can throw:

- `JSON.parse` throws `SyntaxError` on malformed input.
- `JSON.stringify` throws `TypeError` on BigInt or circular references.

```ts
function safeParse(raw: string): unknown {
  try {
    return JSON.parse(raw);
  } catch {
    return undefined;
  }
}
```

When logging parse failures, log the input *length* and the first ~100 bytes, not the full string. Full payloads in logs are a security and storage risk.

### `fetch` + JSON

Reading JSON from a response:

```ts
const r = await fetch(url);
const data = await r.json();     // internally calls JSON.parse; throws on malformed JSON
```

Sending JSON in a request:

```ts
await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});
```

Why the explicit `Content-Type`? Because `fetch` doesn't set it automatically when you pass a string body. Without it, the server might reject your request or misinterpret the body format.

### JSON + TypeScript's type system

`JSON.parse` returns `any`. The moment you assign it to a typed variable, you're lying to the compiler:

```ts
type User = { id: number; name: string };
const user: User = JSON.parse(raw);   // compiles — but no runtime guarantee
```

The fix: treat parse output as `unknown` and validate. See [ch. 10](10-runtime-validation.md).

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Text format | Human-readable; debuggable with `curl` | Binary (Protobuf, MessagePack, CBOR) | When payload size or parse speed matters at scale |
| No date type | Keeps the format simple and language-agnostic | Include a date type (like BSON does) | When you're in a MongoDB ecosystem (BSON) |
| Drop `undefined` silently | `undefined` is JavaScript-specific; other languages don't have it | Serialize as `null` | You can do this with a replacer, but it changes semantics |
| `any` return type | JavaScript's `JSON.parse` predates TypeScript | Return `unknown` (TypeScript 5.x has an option for this) | Enable `--resolveJsonModule` and validation libraries |

## Production-quality code

```ts
type Replacer = (key: string, value: unknown) => unknown;
type Reviver = (key: string, value: unknown) => unknown;

const bigintReplacer: Replacer = (_key, value) =>
  typeof value === "bigint" ? `${value}` : value;

const dateReviver: Reviver = (key, value) => {
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(value)) {
    const date = new Date(value);
    if (!isNaN(date.getTime())) return date;
  }
  return value;
};

function safeStringify(value: unknown, pretty = false): string {
  return JSON.stringify(value, bigintReplacer, pretty ? 2 : undefined);
}

function safeParse<T = unknown>(
  raw: string,
  reviver?: Reviver,
): { ok: true; data: T } | { ok: false; error: string } {
  try {
    const data = JSON.parse(raw, reviver as Parameters<typeof JSON.parse>[1]) as T;
    return { ok: true, data };
  } catch (e) {
    const preview = raw.length > 100 ? raw.slice(0, 100) + "..." : raw;
    return { ok: false, error: `Parse failed (${raw.length} bytes): ${preview}` };
  }
}

async function fetchJson<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);

  const text = await r.text();
  const result = safeParse<T>(text, dateReviver);
  if (!result.ok) throw new Error(result.error);
  return result.data;
}
```

## Security notes

- **JSON injection** — if you embed user-provided strings into JSON without using `JSON.stringify`, you can create malformed JSON or inject extra fields. Always serialize with `JSON.stringify`.
- **Prototype pollution** — `JSON.parse('{"__proto__": {"admin": true}}')` can pollute `Object.prototype` in some environments. Use `Object.create(null)` for parsed results if you're merging into configuration objects, or validate with a schema library.
- **Sensitive data in JSON** — API responses may include fields you shouldn't expose (internal IDs, emails, secrets). Use an allow-list (serializer or schema) rather than sending raw database objects.

## Performance notes

- **`JSON.parse` is fast** — V8's JSON parser is heavily optimized. For payloads under 1MB, parse time is negligible compared to network transfer.
- **`JSON.stringify` can be slow on deep/large objects** — especially with a complex replacer. For hot paths, consider pre-computing the JSON string.
- **Large arrays** — parsing a 100MB JSON array loads the entire thing into memory. For large datasets, consider streaming parsers like `stream-json` or NDJSON (one JSON object per line).
- **Pretty-printing costs** — `JSON.stringify(x, null, 2)` produces larger output. Only use it for human-readable output, not wire format.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "My property disappeared after stringify" | The property's value is `undefined`, which JSON drops silently | Convert to `null` before stringifying if you need to preserve the key |
| 2 | "TypeError: Do not know how to serialize a BigInt" | `JSON.stringify` can't handle `BigInt` natively | Use a replacer to convert BigInt to string |
| 3 | "Dates come back as strings after a round-trip" | JSON has no date type; `Date` objects serialize to ISO strings and stay strings after parsing | Use a reviver to convert ISO strings back to `Date` objects |
| 4 | "TypeError: Converting circular structure to JSON" | Your object has circular references (e.g., parent → child → parent) | Break the cycle before stringifying, or use a replacer that tracks visited objects |
| 5 | "I assigned `JSON.parse(raw)` to a typed variable and it compiled, but it crashed at runtime" | `JSON.parse` returns `any`; the type annotation is a lie | Treat the result as `unknown` and validate with Zod or a type guard |

## Practice

### Warm-up

Parse `'{"a":1,"b":"hello"}'` and access the `a` property. Print its type at runtime.

<details><summary>Show solution</summary>

```ts
const data = JSON.parse('{"a":1,"b":"hello"}');
console.log(data.a);            // 1
console.log(typeof data.a);     // "number"
```

</details>

### Standard

Serialize an object containing a `Date` to JSON, then parse it back and restore the `Date` using a reviver.

<details><summary>Show solution</summary>

```ts
const original = { name: "Ada", createdAt: new Date("2026-04-16T10:00:00Z") };
const json = JSON.stringify(original);
console.log(json);
// '{"name":"Ada","createdAt":"2026-04-16T10:00:00.000Z"}'

const restored = JSON.parse(json, (key, value) =>
  key === "createdAt" ? new Date(value) : value
);
console.log(restored.createdAt instanceof Date);  // true
console.log(restored.createdAt.toISOString());     // "2026-04-16T10:00:00.000Z"
```

</details>

### Bug hunt

A developer writes `JSON.stringify({ a: undefined, b: 2 })` and expects `'{"a":undefined,"b":2}'`. The actual output is `'{"b":2}'`. Why?

<details><summary>Show solution</summary>

`undefined` is not a valid JSON value. `JSON.stringify` intentionally drops properties whose values are `undefined`. This is by design — other languages consuming the JSON wouldn't know what to do with `undefined`. If you need to preserve the key, convert `undefined` to `null` first: `JSON.stringify({ a: null, b: 2 })`.

</details>

### Stretch

Handle BigInt in a JSON round-trip. Stringify an object with a BigInt property, then parse it back and recover the BigInt.

<details><summary>Show solution</summary>

```ts
const original = { id: 1, balance: 99999999999999999n };

const json = JSON.stringify(original, (_, value) =>
  typeof value === "bigint" ? `BIGINT:${value}` : value
);
console.log(json);
// '{"id":1,"balance":"BIGINT:99999999999999999"}'

const restored = JSON.parse(json, (_, value) =>
  typeof value === "string" && value.startsWith("BIGINT:")
    ? BigInt(value.slice(7))
    : value
);
console.log(restored.balance);             // 99999999999999999n
console.log(typeof restored.balance);      // "bigint"
```

</details>

### Stretch++

Use the `stream-json` library to parse a large JSON array without loading the entire file into memory. Read from a file and count the elements.

<details><summary>Show solution</summary>

```ts
import { createReadStream } from "node:fs";
import { parser } from "stream-json";
import { streamArray } from "stream-json/streamers/StreamArray";

let count = 0;

const pipeline = createReadStream("large-data.json")
  .pipe(parser())
  .pipe(streamArray());

for await (const { value } of pipeline) {
  count++;
}

console.log(`Processed ${count} items without loading all into memory`);
```

Install with: `npm install stream-json`

</details>

## Quiz

1. JSON natively supports:
   (a) Date  (b) BigInt  (c) string, number, boolean, null, array, object  (d) RegExp

2. `JSON.parse` returns (in TypeScript):
   (a) `any`  (b) `unknown` is preferable, but `any` is the default  (c) `Object`  (d) `Record<string, unknown>`

3. Pretty-print with 2-space indent:
   (a) `JSON.stringify(x).format(2)`  (b) `JSON.stringify(x, null, 2)`  (c) `JSON.stringify(x, 2)`  (d) Not available

4. A cyclic object passed to `JSON.stringify`:
   (a) Produces an infinite loop  (b) Throws a TypeError  (c) Silently truncates  (d) Returns `{}`

5. Dates in JSON are:
   (a) A native type  (b) Encoded as ISO 8601 strings by convention  (c) Numeric timestamps required  (d) Illegal

**Short answer:**

6. Why should you treat `JSON.parse` output as `unknown` rather than trusting a type annotation?
7. Give one advantage of ISO 8601 strings over Unix epoch integers for dates.

*Answers: 1-c, 2-b, 3-b, 4-b, 5-b. 6 — `JSON.parse` runs at runtime where TypeScript types don't exist. The returned data could be anything — the type annotation is a compile-time lie. Treating it as `unknown` forces you to validate, preventing runtime crashes from unexpected shapes. 7 — ISO 8601 strings are human-readable, sortable as strings, include timezone information, and are unambiguous across locales.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [06-json — mini-project](mini-projects/06-json-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- JSON supports six types (string, number, boolean, null, array, object) and silently drops or throws on everything else.
- `JSON.parse` returns `any` — treat it as `unknown` and validate at the boundary.
- Use replacers and revivers for edge types (Date, BigInt) that JSON doesn't support natively.
- Always set `Content-Type: application/json` when sending JSON in HTTP requests.

## Further reading

- ECMA-404, *The JSON Data Interchange Syntax* — the official specification.
- MDN, *JSON.parse* and *JSON.stringify* — practical API reference.
- Next: [Methods](07-methods.md).
