# Chapter 08 — Paths

> "A path is the resource's name within the API. Clean paths are self-documenting; messy paths are a warning sign."

## Learning objectives

By the end of this chapter you will be able to:

- Design RESTful paths for resources using nouns, not verbs.
- Distinguish path parameters from query parameters and know when to use each.
- Handle nested resources without creating deeply coupled URL hierarchies.
- Version your API via path or header, with an informed opinion on the trade-offs.
- Choose between offset, cursor, and page-based pagination.

## Prerequisites & recap

- [URIs](03-uris.md) — you know how to parse and build URLs safely.
- [Methods](07-methods.md) — you know methods carry the verb; paths carry the noun.

## The simple version

An API path is how you name your resources. A well-designed path reads like a sentence: `GET /v1/users/42/orders` means "get the orders for user 42, version 1 of the API." The path identifies *what*; the method says *what to do*.

The main rules: use plural nouns for collections (`/users`, not `/user`), use IDs for specific resources (`/users/42`), and never put verbs in the path (`/getUsers` is wrong — `GET /users` is right). Query parameters handle everything else: filtering, sorting, pagination.

## In plain terms (newbie lane)

This chapter is really about **Paths**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  /v1/users/42/orders?status=paid&sort=-created_at&limit=10
   │    │    │    │        │           │              │
   │    │    │    │        │           │              └─ pagination
   │    │    │    │        │           └─ sort (- = desc)
   │    │    │    │        └─ filter
   │    │    │    └─ nested resource (collection)
   │    │    └─ specific resource (identity)
   │    └─ resource collection (plural noun)
   └─ API version

  Path = identity (who/what)
  Query = refinement (how many, which ones, what order)
```

*Path identifies the resource. Query refines the view. Methods verb the action. Together, they form a self-documenting API.*

## Concept deep-dive

### REST path conventions

REST (Representational State Transfer) isn't a protocol — it's a set of conventions built on HTTP's semantics. For paths, the conventions are:

1. **Resources are nouns**: `/users`, `/orders`, `/books`.
2. **Collections are plural**: `/users`, not `/user`.
3. **Items are identified by ID**: `/users/42`.
4. **Methods provide the verb** — paths don't. Never `/getUser/42` or `/deleteOrder/5`.
5. **Nested resources** belong to a parent: `/users/42/orders`.

Why nouns, not verbs? Because the HTTP method already carries the verb. `GET /users` is "get users." `DELETE /users/42` is "delete user 42." Adding a verb to the path makes the URL redundant and harder to discover — you'd have `/getUsers`, `/listUsers`, `/fetchUsers` all doing the same thing.

### Path parameters vs. query parameters

| Type | Purpose | Example | Cached separately? |
|------|---------|---------|-------------------|
| **Path** | Identity — *which* resource | `/users/42` | Yes — different resource |
| **Query** | Refinement — *which view* of a resource or collection | `/users?role=admin&limit=10` | Yes — different cache entry |

The rule of thumb: if removing the parameter would give you a *different* resource, it belongs in the path. If it would give you a *different view* of the same resource, it belongs in the query.

```
/users/42          ← identity: user 42 (path param)
/users?role=admin  ← filter: admin users (query param)
/users?limit=10    ← pagination: first 10 (query param)
```

### Versioning

How do you evolve your API without breaking existing clients? Three strategies:

**1. Path versioning** — `/v1/users`, `/v2/users`

Pros: Obvious, easy to test side by side, cacheable, visible in logs.
Cons: URLs change when the version changes; clients must update.

**2. Header versioning** — `Accept: application/vnd.myapp.v2+json`

Pros: Clean URLs that never change.
Cons: Harder to debug (not visible in URLs), harder to test (need custom headers), harder to cache.

**3. Query versioning** — `?v=1`

Pros: Simple.
Cons: Looks messy, can collide with other query params, generally considered the weakest option.

**Recommendation**: use path versioning unless you have a strong reason not to. It's the most debuggable and the most widely adopted.

### Pagination patterns

| Pattern | Mechanism | Pros | Cons |
|---------|-----------|------|------|
| **Offset/limit** | `?offset=20&limit=10` | Simple, familiar | Fragile on moving data (inserts/deletes shift the window) |
| **Cursor** | `?cursor=eyJpZCI6NDJ9` | Stable on moving data, efficient with indexes | Opaque — clients can't jump to a specific page |
| **Page/size** | `?page=3&size=10` | Human-friendly | Same instability as offset; semantically it's just offset math |

Cursor-based pagination is preferred at scale. It's stable (an insert doesn't shift all subsequent pages), it's efficient (the database can seek directly to the cursor), and it doesn't degrade with large offsets (while `OFFSET 100000` can be expensive).

### Filtering and sorting

Filtering via query parameters:

```
GET /users?status=active&role=admin&created_after=2026-01-01
```

Sorting:

```
GET /users?sort=created_at,-price
```

Convention: comma-separated field names, prefix with `-` for descending. This is a widely adopted pattern (used by JSON:API, Stripe, and others).

### Trailing slashes

`/users` and `/users/` — are they the same resource? It depends on the server. Some treat them identically, some redirect one to the other, and some serve different content.

Pick one policy and enforce it. Most modern APIs drop trailing slashes. Servers should canonicalize with a 301 redirect.

### Case conventions

URL paths should be lowercased. Use `kebab-case` or `snake_case`, not `camelCase`:

```
/v1/user-profiles     ← kebab-case (most common)
/v1/user_profiles     ← snake_case (also fine)
/v1/userProfiles      ← avoid: case-sensitive in some servers
```

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| Plural nouns | Consistent: `/users` is the collection, `/users/42` is one item | Singular (`/user/42`) | Some APIs use singular — consistency within your API matters more than which convention |
| Max 2 levels of nesting | Deeply nested URLs are hard to read and maintain | Flat with query filters | When the nesting is genuinely hierarchical (orgs → teams → members) |
| Path versioning | Most debuggable and widely understood | Header versioning | When URL stability is paramount (e.g., public links that must never change) |
| Cursor pagination | Stable under concurrent writes; scales to large datasets | Offset pagination | When clients need to jump to arbitrary pages (offset is simpler for UI) |

## Production-quality code

```ts
interface PaginationParams {
  cursor?: string;
  limit?: number;
  sort?: string;
}

interface Filters {
  [key: string]: string | number | boolean | undefined;
}

function buildResourceUrl(
  base: string,
  version: string,
  resource: string,
  id?: string | number,
  nested?: string,
): URL {
  let path = `/${version}/${resource}`;
  if (id != null) path += `/${encodeURIComponent(String(id))}`;
  if (nested) path += `/${nested}`;
  return new URL(path, base);
}

function applyQueryParams(
  url: URL,
  filters: Filters = {},
  pagination: PaginationParams = {},
): URL {
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined) {
      url.searchParams.set(key, String(value));
    }
  }

  if (pagination.cursor) url.searchParams.set("cursor", pagination.cursor);
  if (pagination.limit) url.searchParams.set("limit", String(pagination.limit));
  if (pagination.sort) url.searchParams.set("sort", pagination.sort);

  return url;
}

// Usage
const url = buildResourceUrl("https://api.example.com", "v1", "users", 42, "orders");
applyQueryParams(url, { status: "paid" }, { limit: 10, sort: "-created_at" });
console.log(url.toString());
// https://api.example.com/v1/users/42/orders?status=paid&limit=10&sort=-created_at

// Cursor-based pagination loop
async function fetchAllPages<T>(
  baseUrl: string,
  parse: (json: unknown) => { data: T[]; nextCursor?: string },
): Promise<T[]> {
  const all: T[] = [];
  let cursor: string | undefined;

  do {
    const url = new URL(baseUrl);
    if (cursor) url.searchParams.set("cursor", cursor);

    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);

    const page = parse(await r.json());
    all.push(...page.data);
    cursor = page.nextCursor;
  } while (cursor);

  return all;
}
```

## Security notes

- **Path traversal** — if user input ends up in a file-serving path without validation, `../../etc/passwd` attacks become possible. Always validate and sanitize path segments; use `encodeURIComponent` for dynamic segments.
- **ID enumeration** — sequential integer IDs (`/users/1`, `/users/2`, ...) let attackers enumerate all resources. Use UUIDs or opaque IDs when resource IDs shouldn't be guessable.
- **Query parameter injection** — if query parameters are reflected in database queries without sanitization, SQL injection or NoSQL injection is possible. Always parameterize queries server-side.

## Performance notes

- **Offset pagination degrades** — `OFFSET 100000` forces the database to scan and skip 100,000 rows. Cursor pagination uses an indexed seek, which is constant-time regardless of depth.
- **Deep nesting increases URL length** — extremely long URLs (>2000 characters) can be rejected by some proxies and browsers. Keep nesting shallow.
- **Cache-friendliness** — path parameters produce different cache entries per resource (`/users/42` vs. `/users/43`). Query parameters do too (`?page=1` vs. `?page=2`). Design your paths so that frequently accessed resources are cache-friendly.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "URLs have verbs: `/getUsers`, `/deleteUser/42`" | Putting verbs in the path instead of using HTTP methods | Use `GET /users` and `DELETE /users/42` — the method is the verb |
| 2 | "Mixing plural and singular: `/user/42/orders` then `/products`" | Inconsistent naming convention | Pick plural for everything and stick with it |
| 3 | "Deeply nested resources: `/orgs/1/teams/5/members/42/roles/3`" | Over-nesting creates rigid, hard-to-evolve URLs | Flatten past 2 levels: `GET /roles/3` with a query `?member=42` |
| 4 | "Pagination breaks when new items are inserted" | Using offset pagination on a live dataset — inserts shift all offsets | Use cursor-based pagination for stable traversal |

## Practice

### Warm-up

Design RESTful paths for a `Product` resource. Include list, get, create, update, and delete.

<details><summary>Show solution</summary>

```
GET    /v1/products          ← list all products
GET    /v1/products/{id}     ← get one product
POST   /v1/products          ← create a product
PUT    /v1/products/{id}     ← replace a product
PATCH  /v1/products/{id}     ← update fields of a product
DELETE /v1/products/{id}     ← delete a product
```

</details>

### Standard

Add a nested `/stores/{id}/products` endpoint to the Product API. When would you use this nested path vs. a flat path with a query parameter?

<details><summary>Show solution</summary>

```
GET /v1/stores/{storeId}/products     ← products belonging to a specific store
GET /v1/products?store_id={storeId}   ← alternative: filter products by store
```

Use the nested path when products *belong to* a store and the relationship is central to the API's domain model. Use the flat path with a filter when products exist independently and the store is just one of many possible filters.

</details>

### Bug hunt

An API has the endpoint `GET /api/getUserById?id=1`. What's wrong with this design, and how would you fix it?

<details><summary>Show solution</summary>

Three problems:
1. **Verb in path** — `getUserById` puts the verb in the path. The method `GET` already provides the verb.
2. **ID in query** — the ID identifies the resource, so it belongs in the path.
3. **Singular** — inconsistent with REST conventions.

Fix: `GET /api/users/1`

</details>

### Stretch

Design cursor-based pagination for a `/feed` endpoint. Define the response shape including the cursor, and explain why cursor pagination is better than offset for this use case.

<details><summary>Show solution</summary>

```
GET /v1/feed?limit=20
GET /v1/feed?cursor=eyJ0IjoiMjAyNi0wNC0xNiJ9&limit=20
```

Response:

```json
{
  "data": [ ... ],
  "pagination": {
    "next_cursor": "eyJ0IjoiMjAyNi0wNC0xNSJ9",
    "has_more": true
  }
}
```

Cursor pagination is better for a feed because:
- New items are constantly being inserted at the top. With offset pagination, an insert shifts all items, causing duplicates or missed items on the next page.
- Cursor pagination uses an indexed seek (e.g., `WHERE created_at < cursor_timestamp`), which is efficient regardless of how deep into the feed you are.
- Offset pagination with `OFFSET 10000` would force the database to scan 10,000 rows just to skip them.

</details>

### Stretch++

Design API versioning via the `Accept` header. Show the request, explain how the server selects the version, and list pros and cons compared to path versioning.

<details><summary>Show solution</summary>

Request:

```
GET /users/42
Accept: application/vnd.myapp.v2+json
```

The server inspects the `Accept` header, extracts the version from the media type, and routes to the appropriate handler. If no version is specified, it defaults to the latest (or a stable default).

**Pros vs. path versioning:**
- URLs are stable — `/users/42` never changes.
- Cleaner separation of concerns — version is metadata, not identity.

**Cons vs. path versioning:**
- Harder to test (you need to set custom headers, not just change the URL).
- Not visible in server logs without extra configuration.
- Can't easily link to a specific version in documentation or a browser.
- CDNs and proxies may not vary cache by `Accept` header without explicit configuration.

</details>

## Quiz

1. RESTful paths use:
   (a) Verbs  (b) Nouns  (c) Both  (d) Numbers only

2. The path parameter for resource identity:
   (a) `/users?id=42`  (b) `/users/42`  (c) A header  (d) The body

3. The preferred versioning strategy is:
   (a) Query parameter  (b) Path or header  (c) Body  (d) Fragment

4. Deep nesting (3+ levels) is:
   (a) Encouraged  (b) Best avoided — flatten to 2 levels  (c) Required by REST  (d) Impossible

5. URL path casing should be:
   (a) `camelCase`  (b) `kebab-case` or `snake_case`, lowercase  (c) `PascalCase`  (d) `SCREAMING_CASE`

**Short answer:**

6. What is the practical difference between cursor and offset pagination?
7. Give one argument in favor of path-based API versioning.

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — Offset pagination skips N rows, which is fragile when data is inserted or deleted (causing duplicates or missed items) and slow for large offsets. Cursor pagination seeks to a specific point using an index, which is stable under concurrent writes and constant-time regardless of depth. 7 — Path versioning is immediately visible in URLs, logs, and documentation. You can test different versions by simply changing the URL, without needing custom headers or tooling.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-paths — mini-project](mini-projects/08-paths-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Paths are resource nouns; methods are the verbs. Never put verbs in URLs.
- Path parameters identify resources (`/users/42`); query parameters refine views (`?role=admin`).
- Version via path (`/v1`) for maximum debuggability.
- Cursor pagination is more stable and efficient than offset pagination, especially at scale.

## Further reading

- *REST API Design Rulebook*, Mark Masse — comprehensive conventions and rationale.
- JSON:API specification — a well-thought-out standard for JSON APIs including pagination and sorting.
- Next: [HTTPS](09-https.md).
