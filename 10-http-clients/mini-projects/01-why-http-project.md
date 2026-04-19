# Mini-project — 01-why-http

_Companion chapter:_ [`01-why-http.md`](../01-why-http.md)

**Goal.** Build `http-inspect.ts` — a CLI tool that takes a URL as a command-line argument, fetches it, and prints the response status, all response headers, and the body size in bytes.

**Acceptance criteria:**

- Accepts a URL via `process.argv[2]`.
- Prints status code and reason phrase.
- Prints every response header as `name: value`.
- Prints the body length in bytes (not characters — use `Buffer.byteLength` on the text or read as an `ArrayBuffer`).
- Times out after 5 seconds with a clear error message.
- Exits with code 1 on any error.

**Hints:**

- Use `AbortSignal.timeout(5000)` or an `AbortController` with `setTimeout`.
- `response.arrayBuffer()` gives you exact byte length via `.byteLength`.

**Stretch:** Add a `--headers-only` flag that behaves like an HTTP HEAD request (uses `method: "HEAD"`).
