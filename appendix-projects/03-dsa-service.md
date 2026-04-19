# Integration project 03 — DSA microservice

**Modules touched:** [01 Python](01-python/README.md), [06 DSA](06-dsa/README.md), [10 HTTP clients](10-http-clients/README.md), [12 HTTP servers](12-http-servers/README.md) (optional facade), [14 Docker](14-docker/README.md).

## Goal

Expose **one heavy algorithm** (e.g. single-source shortest paths on a weighted graph, or A* on a grid) as a **Python microservice** behind HTTP. A thin **TypeScript** client CLI measures latency and correctness vs a golden-file test suite. Containerize Python with a pinned slim image.

## Acceptance criteria

1. `POST /solve` accepts JSON graph representation + source node; returns distances or path.
2. Python service validates input size limits (`n` nodes, `m` edges) and returns `413` or `400` with helpful errors.
3. **Benchmark mode:** `GET /health` plus a CLI (`pnpm ts-node bench.ts`) fires ≥100 requests at known graphs; prints p50/p95 latency table.
4. Golden tests in Python (`pytest`) cover at least 5 graph shapes including edge cases (disconnected component, negative cycle rejection if applicable).
5. `Dockerfile` for Python service uses multi-stage build; final image non-root.
6. README explains Big-O of your implementation and when you would **not** use this service (too much overhead for tiny graphs).

## Hints

- Use `uvicorn` + FastAPI or stdlib `http.server` for minimal surface — your call, document it.
- For benchmarking, warm up JVM is N/A; do warm-up iterations in TS client before measuring.

## Stretch extensions

- Add caching with TTL for identical graph hashes.
- Compare Python implementation to a second language (optional) behind the same API contract.
