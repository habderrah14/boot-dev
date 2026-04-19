# Mini-project — 06-json

_Companion chapter:_ [`06-json.md`](../06-json.md)

**Goal.** Build `json-io.ts` exporting `safeParse<T>(raw: string, validator: (x: unknown) => x is T)` and a `stringify` that handles BigInt and Date.

**Acceptance criteria:**

- `safeParse` returns `{ ok: true, data: T }` or `{ ok: false, error: string }`.
- `safeParse` catches `SyntaxError` and returns a descriptive error (not the full input).
- `safeParse` runs the validator function and returns an error if validation fails.
- `stringify` converts BigInt to string representation and Date to ISO string.
- `stringify` handles circular references by throwing a clear error (not the default cryptic message).

**Hints:**

- Use a replacer function for BigInt and Date.
- For cycle detection, track visited objects in a `WeakSet`.
- The validator is a type predicate: `(x: unknown) => x is T`.

**Stretch:** Add a `toNDJSON(items: unknown[])` function that serializes an array as newline-delimited JSON (one object per line), suitable for streaming.
