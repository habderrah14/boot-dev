# Module 10 — Learn HTTP Clients in TypeScript

> Before you build servers, you must know what a server _sees_. The client-side view of HTTP — request, response, status, headers, body — is the contract every backend will ever have to honor.

## Map to Boot.dev

Parallels Boot.dev's **"Learn HTTP Clients"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Make HTTP requests from TypeScript using `fetch` and handle success, failure, and timeouts.
- Construct correct URIs, set headers, and parse JSON safely.
- Map HTTP methods (GET/POST/PUT/PATCH/DELETE) to CRUD semantics.
- Explain HTTPS, TLS, and certificates at the level of "what breaks when it breaks".
- Validate untrusted data at runtime using Zod or similar.

## Prerequisites

- [Module 09: TypeScript](../09-ts/README.md).
- A working Node 20+ + TypeScript project.

## Chapter index

1. [Why HTTP?](01-why-http.md)
2. [DNS](02-dns.md)
3. [URIs](03-uris.md)
4. [Errors](04-errors.md)
5. [Headers](05-headers.md)
6. [JSON](06-json.md)
7. [Methods](07-methods.md)
8. [Paths](08-paths.md)
9. [HTTPS](09-https.md)
10. [Runtime Validation](10-runtime-validation.md)

## How this module connects

- Flip-side of Module 12 (HTTP Servers). Everything learned here about requests is what your server must parse, validate, and respond to.
- Runtime validation becomes critical in Pub/Sub (Module 15) where messages cross process boundaries.

## Companion artifacts

- Exercises:
  - [01 — Why HTTP?](exercises/01-why-http-exercises.md)
  - [02 — DNS](exercises/02-dns-exercises.md)
  - [03 — URIs](exercises/03-uris-exercises.md)
  - [04 — Errors](exercises/04-errors-exercises.md)
  - [05 — Headers](exercises/05-headers-exercises.md)
  - [06 — JSON](exercises/06-json-exercises.md)
  - [07 — Methods](exercises/07-methods-exercises.md)
  - [08 — Paths](exercises/08-paths-exercises.md)
  - [09 — HTTPS](exercises/09-https-exercises.md)
  - [10 — Runtime Validation](exercises/10-runtime-validation-exercises.md)
- Extended assessment artifacts:
  - [11 — Debugging Incident Lab](exercises/11-debugging-incident-lab.md)
  - [12 — Code Review Task](exercises/12-code-review-task.md)
  - [13 — System Design Prompt](exercises/13-system-design-prompt.md)
  - [14 — Interview Challenges](exercises/14-interview-challenges.md)
- Solutions:
  - [01 — Why HTTP?](solutions/01-why-http-solutions.md)
  - [02 — DNS](solutions/02-dns-solutions.md)
  - [03 — URIs](solutions/03-uris-solutions.md)
  - [04 — Errors](solutions/04-errors-solutions.md)
  - [05 — Headers](solutions/05-headers-solutions.md)
  - [06 — JSON](solutions/06-json-solutions.md)
  - [07 — Methods](solutions/07-methods-solutions.md)
  - [08 — Paths](solutions/08-paths-solutions.md)
  - [09 — HTTPS](solutions/09-https-solutions.md)
  - [10 — Runtime Validation](solutions/10-runtime-validation-solutions.md)
- Mini-project briefs:
  - [01 — HTTP Inspector (Bonus project)](mini-projects/01-http-inspector.md)
  - [01 — Why HTTP? (Core chapter project)](mini-projects/01-why-http-project.md)
  - [02 — DNS](mini-projects/02-dns-project.md)
  - [03 — URIs](mini-projects/03-uris-project.md)
  - [04 — Errors](mini-projects/04-errors-project.md)
  - [05 — Headers](mini-projects/05-headers-project.md)
  - [06 — JSON](mini-projects/06-json-project.md)
  - [07 — Methods](mini-projects/07-methods-project.md)
  - [08 — Paths](mini-projects/08-paths-project.md)
  - [09 — HTTPS](mini-projects/09-https-project.md)
  - [10 — Runtime Validation](mini-projects/10-runtime-validation-project.md)
- Milestone capstone:
  - [Capstone 02 — API Client CLI](capstone/capstone-02-api-client-cli.md)

## Quiz answer key

- **Ch. 01 — Why HTTP?.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6.  Statelessness lets any server handle any request because no server must remember session state in memory.
  - 7.  Multiplexing solves application-layer head-of-line blocking by allowing many streams to share one connection concurrently.
- **Ch. 02 — DNS.** 1) a, 2) b, 3) a, 4) b, 5) b.
  - 6. Resolver and OS caches retain old records until TTL expiry, delaying visible updates.
  - 7. Typical DNS tools include `dig`, `nslookup`, and `host`.
- **Ch. 03 — URIs.** 1) a, 2) b, 3) a, 4) a, 5) b.
  - 6. `URL` APIs avoid encoding bugs, slash issues, and concatenation injection mistakes.
  - 7. `/users` and `/users/` can map to different behavior depending on server routing rules.
- **Ch. 04 — Errors.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. `fetch` resolves for 4xx/5xx; clients must still check `response.ok`.
  - 7. Jitter prevents synchronized retry storms during service recovery.
- **Ch. 05 — Headers.** 1) b, 2) b, 3) a, 4) a, 5) b.
  - 6. Basic auth is only encoded; without HTTPS credentials are trivially exposed.
  - 7. Consistent `User-Agent` improves provider-side support, tracing, and rate-limit policy.
- **Ch. 06 — JSON.** 1) c, 2) b, 3) b, 4) b, 5) b.
  - 6. Parse output is runtime data; treat as `unknown` until validated.
  - 7. ISO timestamps are unambiguous, sortable, and timezone-safe.
- **Ch. 07 — Methods.** 1) b, 2) d, 3) b, 4) b, 5) a.
  - 6. PUT replaces full representation; PATCH modifies only provided fields.
  - 7. Idempotency keys prevent duplicate side effects when requests are retried.
- **Ch. 08 — Paths.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Cursor pagination is stable and efficient under writes; offset is not.
  - 7. Path-based versioning is visible in URLs/logs and easier to test.
- **Ch. 09 — HTTPS.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6. Disabling certificate checks enables MITM interception despite encryption.
  - 7. TLS requirements preserve HTTP/2 safety and protocol integrity in transit.
- **Ch. 10 — Runtime Validation.** 1) b, 2) b, 3) a, 4) b, 5) b.
  - 6. TS types are erased at runtime; external data must be validated explicitly.
  - 7. Shared schemas catch contract drift earlier across client-server boundaries.
