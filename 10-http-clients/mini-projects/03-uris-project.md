# Mini-project — 03-uris

_Companion chapter:_ [`03-uris.md`](../03-uris.md)

**Goal.** Build `url-builder.ts` — a module exporting `build({ base, path, query })` that always produces a valid URL, encoding untrusted values correctly.

**Acceptance criteria:**

- `build({ base: "https://api.com", path: "/v1/users", query: { name: "Ada Lovelace" } })` returns a valid `URL` with the name properly encoded.
- Path segments containing special characters (`/`, `?`, `#`) are encoded.
- Query values containing `&` or `=` are encoded.
- Throws a descriptive error if `base` is not a valid absolute URL.
- Exported as an ES module with TypeScript types.

**Hints:**

- Use `new URL(path, base)` for the foundation.
- Loop over `query` entries with `searchParams.set()`.
- Test edge cases: empty query, empty path, unicode in values.

**Stretch:** Add a `pathSegments: string[]` option that builds the path from an array of segments, encoding each one independently.
