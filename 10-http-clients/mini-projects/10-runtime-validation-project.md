# Mini-project — 10-runtime-validation

_Companion chapter:_ [`10-runtime-validation.md`](../10-runtime-validation.md)

**Goal.** Build `api-client.ts` with `getValidated(url, schema)` and `postValidated(url, body, requestSchema, responseSchema)` — a fully type-safe, runtime-validated HTTP client.

**Acceptance criteria:**

- `getValidated<T>(url, schema)` fetches, checks `response.ok`, parses JSON, validates with the schema, and returns `T`.
- `postValidated<TReq, TRes>(url, body, requestSchema, responseSchema)` validates the request body *before* sending, then validates the response.
- Both throw typed errors: `HttpError` for non-2xx, `ValidationError` for schema failures.
- `ValidationError` includes the URL and a human-readable summary of the issues.
- Include at least two schemas (e.g., `UserSchema`, `CreateUserSchema`) and demonstrate the full round-trip.

**Hints:**

- Use `safeParse` and build a `ValidationError` class that wraps `ZodError.issues`.
- The request body validation catches bugs before they leave your process.
- Use `z.infer<typeof Schema>` for all type annotations — no manual type definitions.

**Stretch:** Add response schema caching — store the schema per URL pattern and automatically validate without the caller passing a schema each time. Register schemas with a `registerSchema("/api/users/:id", UserSchema)` function.
