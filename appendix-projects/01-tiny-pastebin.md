# Integration project 01 — Tiny Pastebin

**Modules touched:** [09 TypeScript](09-ts/README.md), [10 HTTP clients](10-http-clients/README.md), [11 SQL](11-sql/README.md), [12 HTTP servers](12-http-servers/README.md), [13 File / CDN](13-file-cdn/README.md), [14 Docker](14-docker/README.md).

## Goal

Ship a **pastebin** where users `POST` multi-kilobyte text, receive a short `id`, and `GET /p/:id` returns the body. Metadata lives in Postgres; bytes live in object storage (S3-compatible or MinIO locally). Add a `docker compose` file so a reviewer runs `docker compose up` and hits the API.

## Acceptance criteria

1. `POST /pastes` with JSON `{ "content": "...", "ttl_hours": 24 }` returns `{ "id": "...", "url": "..." }`.
2. `GET /pastes/:id` streams bytes from object storage through the app (or redirects with a presigned URL — document which you chose and why).
3. Postgres stores `id`, `content_key`, `expires_at`, `created_at` — never the full blob if using object storage.
4. TTL enforced: expired pastes return `404` and object deleted or lifecycle rule documented.
5. `docker compose up` starts API + Postgres + MinIO (or mocks S3) + runs migrations automatically.
6. `README.md` lists env vars, curl examples, and one paragraph on threat model (content scanning, size limits).

## Hints

- Presigned `PUT` lets browsers upload directly; for CLI-only scope, server-side `PUT` to MinIO is fine.
- Use `Content-Length` limits and a max TTL cap to prevent abuse.
- Store only a random `id` (UUID v4) in URLs — no sequential IDs.

## Stretch extensions

- Syntax highlighting via `Content-Type` negotiation.
- Rate limit per IP (`429` with `Retry-After`).
- Virus scan hook (document-only stub is OK).
