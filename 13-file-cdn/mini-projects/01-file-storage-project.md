# Mini-project — 01-file-storage

_Companion chapter:_ [`01-file-storage.md`](../01-file-storage.md)

**Goal.** Build a photo-upload API: the server generates presigned URLs for upload and signed download URLs. The browser uploads directly to S3; the server never proxies bytes.

**Acceptance criteria:**

- `GET /api/upload-url?type=image/jpeg` returns a presigned PUT URL and the generated S3 key.
- `POST /api/photos` records metadata (key, user, size) after the client confirms upload.
- `GET /api/photos/:id` returns a short-lived signed download URL (redirect or JSON).
- The S3 bucket has Block Public Access enabled.
- No AWS credentials are exposed to the client.

**Hints:**

- Use `@aws-sdk/client-s3` and `@aws-sdk/s3-request-presigner`.
- Generate a UUID-based key to avoid collisions.
- Set `expiresIn: 300` (5 minutes) for upload URLs, `expiresIn: 60` for download URLs.

**Stretch:** Add a confirmation step that verifies the object actually exists in S3 (HeadObject) and checks its size against a limit before inserting into the database.
