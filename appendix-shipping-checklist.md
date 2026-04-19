# Appendix — Shipping checklist (demo-ready backend)

> Use this before you call a project “done” on your resume or in an interview. It turns the modules in this book into **evidence**, not vibes.

## Repository

- [ ] **README** with: what it does, how to run locally, required env vars, link to live deploy (if any).
- [ ] **LICENSE** or explicit “personal/educational” note if you are not open-sourcing.
- [ ] **`.gitignore`** excludes `.env`, build artifacts, `node_modules/`, `.venv/`, OS junk.

## Local run

- [ ] **One command** brings up dependencies (e.g. `docker compose up` or documented `createdb` + migrate steps).
- [ ] **Seed or fixture data** so a reviewer sees a non-empty UI/API in under 2 minutes.
- [ ] **Port and URL** documented (`http://localhost:3000`, etc.).

## Tests

- [ ] **Automated tests** exist for the happy path of your core feature (even if count is small).
- [ ] **CI** (e.g. GitHub Actions) runs those tests on every PR — see [Module 03 ch. 10](03-git/10-github.md).
- [ ] Failing test reproduces the bug **before** you fix it (proves the test is real).

## Security basics

- [ ] **No secrets in git** — use env vars or secret manager; see [Module 13 ch. 06](13-file-cdn/06-security.md) for cloud patterns.
- [ ] **SQL parameterized** — never string-concat user input into queries ([Module 11](11-sql/README.md), [Module 12](12-http-servers/06-storage.md)).
- [ ] **Auth boundary clear** — who can call which route ([Module 12 ch. 07–08](12-http-servers/README.md)).

## Observability

- [ ] **Logs go to stdout/stderr** in JSON or single-line text (not only to a mystery file in the container).
- [ ] **Request or correlation ID** on API routes you care about (even a cheap random UUID per request is enough at small scale).

## Deploy (optional but high signal)

- [ ] **Public URL** or container image name + run instructions.
- [ ] **Health check** endpoint returns 200 when dependencies are up.
- [ ] **Rollback story** one sentence (“revert to previous image tag X”).

## Interview narrative

- [ ] **30-second pitch**: problem → your approach → one metric (latency, test count, users if real).
- [ ] **Trade-off you can defend** from [System design appendix](appendix-system-design.md).

Cross-link: [Integration projects](appendix-projects/README.md) for larger builds that hit multiple modules.
