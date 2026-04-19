# Mini-project — 08-authorization

_Companion chapter:_ [`08-authorization.md`](../08-authorization.md)

**Goal.** Build an `authz.ts` module with a pure `can(user, action, resource)` function and Express middleware wrappers.

**Acceptance criteria:**

- `can()` is a pure function with no side effects — takes user, action, resource, returns boolean.
- Supports roles: `admin`, `editor`, `viewer`.
- Admin can do everything. Editor can create and edit/delete own posts. Viewer can only read.
- `authorize(action)` middleware fetches the resource, checks `can()`, throws Forbidden or NotFound.
- Unit tests for `can()` cover every role × action combination (at least 15 assertions).
- Integration tests verify that protected endpoints return 403/404 for unauthorized users.

**Hints:**

- Write the `can()` function first. Make it pass all unit tests before touching middleware.
- Use a lookup table or switch statement — keep it readable.
- Test edge cases: what happens when `resource` is undefined? When `authorId` is missing?

**Stretch:** Add tenant isolation to `can()`. If `resource.tenantId !== user.tenantId`, always deny. Write tests that verify cross-tenant access is blocked.
