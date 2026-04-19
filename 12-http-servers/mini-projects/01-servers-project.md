# Mini-project — 01-servers

_Companion chapter:_ [`01-servers.md`](../01-servers.md)

**Goal.** Build `server.ts` — a production-ready Express (or Fastify) server.

**Acceptance criteria:**

- `GET /health` returns `{ ok: true, uptime: <seconds> }`.
- Environment config validated with Zod at boot (`PORT`, `NODE_ENV`, `LOG_LEVEL`).
- Graceful shutdown on `SIGTERM` and `SIGINT` with a 10-second timeout.
- Structured logging via `pino-http` with per-request IDs.
- 404 catch-all handler returning `{ error: "not_found" }`.
- `x-powered-by` header disabled.

**Hints:**

- Start with the production-quality code example above and strip it to the essentials.
- Use `curl -X POST http://localhost:3000/nonexistent` to test your 404 handler.
- Test graceful shutdown: start the server, send a slow request (e.g., with a `setTimeout` in a test route), then `kill -TERM <pid>` and verify the slow request finishes.

**Stretch:** Add a Fastify version of the same server. Compare the code side-by-side. Which has less boilerplate?
