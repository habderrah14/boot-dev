# Mini-project — 02-routing

_Companion chapter:_ [`02-routing.md`](../02-routing.md)

**Goal.** Build a routing-only server: full CRUD for `Book` under `/v1/books`, with 404 and 405 handlers, using a sub-router for `/v1`. No persistent storage (use an in-memory `Map`).

**Acceptance criteria:**

- `GET /v1/books` returns a list (with `limit` query param, capped at 100).
- `GET /v1/books/:id` returns a single book or 404.
- `POST /v1/books` creates a book and returns 201.
- `PATCH /v1/books/:id` updates a book or returns 404.
- `DELETE /v1/books/:id` deletes a book (204) or returns 404.
- `PUT /v1/books/:id` returns 405 with an `Allow` header.
- Any unmatched path returns `{ error: "not_found" }` with 404.
- Path parameter `id` is validated as a positive integer.

**Hints:**

- Use `app.route("/:id")` to chain `.get()`, `.patch()`, `.delete()`, `.all()` on the same path.
- Test with `curl -X PUT http://localhost:3000/v1/books/1` to verify 405.

**Stretch:** Add a `/v2/books` endpoint that wraps responses in `{ data: ..., meta: { total: n } }` while `/v1/books` keeps the flat array shape.
