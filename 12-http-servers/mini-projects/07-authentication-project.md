# Mini-project — 07-authentication

_Companion chapter:_ [`07-authentication.md`](../07-authentication.md)

**Goal.** Build a complete auth module: `/register`, `/login`, `/me`, `/refresh`.

**Acceptance criteria:**

- `POST /register` — validates input (Zod), hashes password (bcrypt, cost 12), creates user, returns 201.
- `POST /login` — verifies credentials, returns JWT access token (15 min) + refresh token (7 days), stores refresh token in DB.
- `GET /me` — protected by `authenticate` middleware, returns user profile.
- `POST /refresh` — rotates the refresh token, returns new access + refresh tokens.
- Generic "invalid credentials" error for all login failures.
- Tests cover: successful registration, duplicate email, successful login, wrong password, expired token, refresh rotation.

**Hints:**

- The refresh token is a plain `crypto.randomUUID()` stored in a `sessions` table.
- Test token expiration by signing a token with `expiresIn: "0s"` in tests.
- Don't forget to add the `authenticate` middleware to the composition root.

**Stretch:** Add rate limiting on `/login` (max 10 attempts per IP per minute) using `express-rate-limit`.
