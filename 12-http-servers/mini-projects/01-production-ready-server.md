# Mini-project — Production-Ready Server

## Goal

Build a small HTTP server that looks and behaves like something you could deploy behind a load balancer.

## Deliverable

A Node.js + TypeScript server with health checks, validation, shutdown handling, and logging.

## Required behavior

1. `GET /health` returns `{ ok: true, uptime: <seconds> }`.
2. Environment config is validated at boot.
3. `x-powered-by` is disabled.
4. Graceful shutdown handles `SIGTERM` and `SIGINT`.
5. Structured logging includes request IDs.

## Acceptance criteria

- Works with Express or Fastify.
- Fails fast on missing env config.
- 404s are handled consistently.
- README explains run and test steps.

## Hints

- Use Zod for env validation.
- Use `pino-http` or framework logging.
- Keep routing and shutdown logic readable.

## Stretch goals

1. Add a Fastify version for comparison.
2. Add an `/echo` route.
3. Add request body size limits and redaction.
