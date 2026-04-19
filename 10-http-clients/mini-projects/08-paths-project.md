# Mini-project — 08-paths

_Companion chapter:_ [`08-paths.md`](../08-paths.md)

**Goal.** Design paths for a small blog API with posts, comments, and authors.

**Acceptance criteria:**

- CRUD paths for posts, comments, and authors.
- Comments are nested under posts: `/v1/posts/{id}/comments`.
- Filtering: by author, by status (`?author=42&status=published`).
- Cursor-based pagination on all list endpoints.
- Sorting: `?sort=-published_at,title`.
- Versioned via path (`/v1`).
- Document the paths in a simple table (or OpenAPI YAML as a stretch).

**Hints:**

- List endpoints: `GET /v1/posts`, `GET /v1/authors`.
- Nested: `GET /v1/posts/{id}/comments`, `POST /v1/posts/{id}/comments`.
- Author detail: `GET /v1/authors/{id}`.
- Pagination response includes `next_cursor` and `has_more`.

**Stretch:** Write the path design as an OpenAPI 3.0 YAML file with path parameters, query parameters, and response schemas.
