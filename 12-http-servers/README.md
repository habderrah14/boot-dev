# Module 12 — Learn HTTP Servers in TypeScript

> Servers are where backend work becomes concrete. A good server is a boring server: it accepts a request, does one thing, responds in a predictable shape, and logs enough that you'd notice if it stopped.

## Map to Boot.dev

Parallels Boot.dev's **"Learn HTTP Servers"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Start an HTTP server in Node.js/TypeScript (with and without Express).
- Design routes, handle JSON bodies, and respond with correct status codes.
- Lay out a server codebase that separates routing, business logic, and storage.
- Implement authentication (passwords, JWTs) and authorization (role checks, ownership).
- Accept and verify webhooks.
- Generate and publish API documentation.

## Prerequisites

- [Module 10: HTTP Clients](../10-http-clients/README.md).
- [Module 11: SQL](../11-sql/README.md) for storage.

## Chapter index

1. [Servers](01-servers.md)
2. [Routing](02-routing.md)
3. [Architecture](03-architecture.md)
4. [JSON](04-json.md)
5. [Error Handling](05-error-handling.md)
6. [Storage](06-storage.md)
7. [Authentication](07-authentication.md)
8. [Authorization](08-authorization.md)
9. [Webhooks](09-webhooks.md)
10. [Documentation](10-documentation.md)

## How this module connects

- File servers (Module 13) are built on the same foundation with different payload shapes.
- Webhooks are a real-world precursor to the pub/sub patterns in Module 15.

## Companion artifacts

- Exercises:
  - [01 — Servers](exercises/01-servers-exercises.md)
  - [02 — Routing](exercises/02-routing-exercises.md)
  - [03 — Architecture](exercises/03-architecture-exercises.md)
  - [04 — JSON](exercises/04-json-exercises.md)
  - [05 — Error Handling](exercises/05-error-handling-exercises.md)
  - [06 — Storage](exercises/06-storage-exercises.md)
  - [07 — Authentication](exercises/07-authentication-exercises.md)
  - [08 — Authorization](exercises/08-authorization-exercises.md)
  - [09 — Webhooks](exercises/09-webhooks-exercises.md)
  - [10 — Documentation](exercises/10-documentation-exercises.md)
- Extended assessment artifacts:
  - [11 — System Design Primer](exercises/11-system-design-primer.md)
  - [12 — Code Review Task](exercises/12-code-review-task.md)
  - [13 — Debugging Incident Lab](exercises/13-debugging-incident-lab.md)
  - [14 — Interview Challenges](exercises/14-interview-challenges.md)
- Solutions:
  - [01 — Servers](solutions/01-servers-solutions.md)
  - [02 — Routing](solutions/02-routing-solutions.md)
  - [03 — Architecture](solutions/03-architecture-solutions.md)
  - [04 — JSON](solutions/04-json-solutions.md)
  - [05 — Error Handling](solutions/05-error-handling-solutions.md)
  - [06 — Storage](solutions/06-storage-solutions.md)
  - [07 — Authentication](solutions/07-authentication-solutions.md)
  - [08 — Authorization](solutions/08-authorization-solutions.md)
  - [09 — Webhooks](solutions/09-webhooks-solutions.md)
  - [10 — Documentation](solutions/10-documentation-solutions.md)
- Mini-project briefs:
  - [01 — Production-Ready Server (Bonus project)](mini-projects/01-production-ready-server.md)
  - [01 — Servers (Core chapter project)](mini-projects/01-servers-project.md)
  - [02 — Routing](mini-projects/02-routing-project.md)
  - [03 — Architecture](mini-projects/03-architecture-project.md)
  - [04 — JSON](mini-projects/04-json-project.md)
  - [05 — Error Handling](mini-projects/05-error-handling-project.md)
  - [06 — Storage](mini-projects/06-storage-project.md)
  - [07 — Authentication](mini-projects/07-authentication-project.md)
  - [08 — Authorization](mini-projects/08-authorization-project.md)
  - [09 — Webhooks](mini-projects/09-webhooks-project.md)
  - [10 — Documentation](mini-projects/10-documentation-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Servers.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  Crashing early turns misconfiguration into an obvious deploy-time failure instead of a hidden runtime 500 that affects users later.
  - 7.  Fastify is async-native, includes built-in validation and logging, and usually requires less boilerplate than Express for new projects.
- **Ch. 02 — Routing.** 1) b, 2) b, 3) b, 4) d, 5) a.
  - 6. Unvalidated path parameters can cause crashes, injection, or downstream data corruption.
  - 7. Path-based versioning is URL-visible, cache-friendly, and easy to test.
- **Ch. 03 — Architecture.** 1) b, 2) b, 3) b, 4) b, 5) c.
  - 6. Adapter-based storage boundaries enable fast service tests with in-memory backends.
  - 7. A composition root centralizes dependency wiring and avoids hidden global coupling.
- **Ch. 04 — JSON.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Consistent error envelopes simplify client handling and machine-readable diagnostics.
  - 7. Streaming large outputs controls memory usage and improves throughput.
- **Ch. 05 — Error Handling.** 1) c, 2) b, 3) b, 4) b, 5) b.
  - 6. Service-layer throws keep domain logic transport-agnostic; middleware maps to HTTP.
  - 7. Structured logs enable indexed filtering/aggregation across request metadata.
- **Ch. 06 — Storage.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Query builders fit teams wanting SQL-like control with strong type support.
  - 7. Never edit applied migrations; create forward migrations to avoid schema drift.
- **Ch. 07 — Authentication.** 1) c, 2) b, 3) a, 4) b, 5) b.
  - 6. Bcrypt is intentionally slow and salted; SHA-256 is too fast for password storage.
  - 7. JWT scales statelessly; sessions support simpler revocation.
- **Ch. 08 — Authorization.** 1) a, 2) b, 3) b, 4) a, 5) b.
  - 6. Returning 404 can prevent resource enumeration by unauthorized clients.
  - 7. Centralized `can()` policy logic improves consistency and testability.
- **Ch. 09 — Webhooks.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 10 — Documentation.** 1) b, 2) b, 3) b, 4) b, 5) b.
