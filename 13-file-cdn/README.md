# Module 13 — Learn File Servers and CDNs

> Not every payload is JSON. Photos, videos, PDFs, backups — the heavy stuff — have their own storage model (objects, not rows) and their own delivery model (edges, not origins). This module is how you serve those at scale.

## Map to Boot.dev

Parallels Boot.dev's **"Learn File Servers and CDNs"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Explain the difference between block, file, and object storage.
- Use AWS S3 from TypeScript: upload, download, presigned URLs, lifecycle rules.
- Design basic HTTP caching using `Cache-Control`, `ETag`, and `Last-Modified`.
- Serve video with adaptive bitrate streaming at a conceptual level.
- Place a CDN (CloudFront) in front of an origin and reason about cache invalidation.
- Design for resiliency: availability zones, retries, idempotency.

## Prerequisites

- [Module 12: HTTP Servers](../12-http-servers/README.md).

## Chapter index

1. [File Storage](01-file-storage.md)
2. [Caching](02-caching.md)
3. [AWS S3](03-aws-s3.md)
4. [Object Storage](04-object-storage.md)
5. [Video Streaming](05-video-streaming.md)
6. [Security](06-security.md)
7. [CDNs](07-cdns.md)
8. [Resiliency](08-resiliency.md)

## How this module connects

- S3 + CloudFront is the reference deployment for static content in every TS/JS webapp.
- Caching concepts reappear in SQL query plans (Module 11) and DNS (Module 10).

## Companion artifacts

- Exercises:
  - [01 — File Storage](exercises/01-file-storage-exercises.md)
  - [02 — Caching](exercises/02-caching-exercises.md)
  - [03 — AWS S3](exercises/03-aws-s3-exercises.md)
  - [04 — Object Storage](exercises/04-object-storage-exercises.md)
  - [05 — Video Streaming](exercises/05-video-streaming-exercises.md)
  - [06 — Security](exercises/06-security-exercises.md)
  - [07 — CDNs](exercises/07-cdns-exercises.md)
  - [08 — Resiliency](exercises/08-resiliency-exercises.md)
- Extended assessment artifacts:
  - [09 — Debugging Incident Lab](exercises/09-debugging-incident-lab.md)
  - [10 — Code Review Task](exercises/10-code-review-task.md)
  - [11 — System Design Prompt](exercises/11-system-design-prompt.md)
  - [12 — Interview Challenges](exercises/12-interview-challenges.md)
- Solutions:
  - [01 — File Storage](solutions/01-file-storage-solutions.md)
  - [02 — Caching](solutions/02-caching-solutions.md)
  - [03 — AWS S3](solutions/03-aws-s3-solutions.md)
  - [04 — Object Storage](solutions/04-object-storage-solutions.md)
  - [05 — Video Streaming](solutions/05-video-streaming-solutions.md)
  - [06 — Security](solutions/06-security-solutions.md)
  - [07 — CDNs](solutions/07-cdns-solutions.md)
  - [08 — Resiliency](solutions/08-resiliency-solutions.md)
- Mini-project briefs:
  - [01 — File Storage (Core chapter project)](mini-projects/01-file-storage-project.md)
  - [01 — Photo Upload API (Bonus project)](mini-projects/01-photo-upload-api.md)
  - [02 — Caching](mini-projects/02-caching-project.md)
  - [03 — AWS S3](mini-projects/03-aws-s3-project.md)
  - [04 — Object Storage](mini-projects/04-object-storage-project.md)
  - [05 — Video Streaming](mini-projects/05-video-streaming-project.md)
  - [06 — Security](mini-projects/06-security-project.md)
  - [07 — CDNs](mini-projects/07-cdns-project.md)
  - [08 — Resiliency](mini-projects/08-resiliency-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — File Storage.** 1) c, 2) b, 3) b, 4) b, 5) b.
  - 6.  Metadata belongs in SQL because relational queries, constraints, and indexing work well on structured fields while the bytes themselves scale better in object storage.
  - 7.  Presigned URLs let clients upload directly to object storage without exposing credentials or forcing your app server to proxy the bytes.
- **Ch. 02 — Caching.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6. Use versioned URLs or explicit purge APIs to invalidate stale edge content.
  - 7. Stale-while-revalidate favors fast responses while cache refresh happens in background.
- **Ch. 03 — AWS S3.** 1) b, 2) b, 3) b, 4) b, 5) c.
  - 6. Presigning must stay server-side because clients must never hold signing secrets.
  - 7. Versioning enables recovery from accidental overwrite/deletion.
- **Ch. 04 — Object Storage.** 1) b, 2) c, 3) c, 4) b, 5) b.
  - 6. Egress-cost-friendly providers can dominate economics for large media workloads.
  - 7. Prefixes improve listing patterns and lifecycle policy targeting.
- **Ch. 05 — Video Streaming.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Adaptive streaming changes bitrate per segment based on observed bandwidth.
  - 7. Immutable segments can be long-cached; manifests need shorter freshness windows.
- **Ch. 06 — Security.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Signed URLs offer scoped, expiring access unlike permanently public buckets.
  - 7. Least privilege grants only required permissions for each service identity.
- **Ch. 07 — CDNs.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Versioned paths avoid purge complexity by changing URLs on content change.
  - 7. Even short TTL edge caching reduces origin pressure for semi-dynamic content.
- **Ch. 08 — Resiliency.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6. Untested backups are operationally untrusted until restore drills pass.
  - 7. Graceful degradation preserves core product utility during partial failures.
