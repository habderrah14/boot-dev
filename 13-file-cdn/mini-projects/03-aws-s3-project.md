# Mini-project — 03-aws-s3

_Companion chapter:_ [`03-aws-s3.md`](../03-aws-s3.md)

**Goal.** Build a complete upload/download API using presigned URLs. The browser uploads directly to S3; the server confirms and records metadata.

**Acceptance criteria:**

- `POST /api/upload-url` returns a presigned PUT URL and the generated key.
- `POST /api/confirm-upload` verifies the object exists in S3 (HeadObject), checks size, and inserts metadata.
- `GET /api/files/:id` returns a presigned GET URL (60-second expiry).
- Bucket has Block Public Access enabled and a CORS rule for your origin.
- No AWS credentials are exposed to the client or committed to git.

**Hints:**

- Use `randomUUID()` for collision-free keys.
- `HeadObjectCommand` returns metadata (size, content-type) without downloading the object.
- Test with `curl` or the browser's network inspector.

**Stretch:** Add lifecycle rules that move uploads older than 90 days to Standard-IA, and configure bucket versioning.
