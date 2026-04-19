# Mini-project — Photo Upload API

## Goal

Build a photo-upload API that issues presigned upload URLs and signed download URLs.

## Deliverable

A TypeScript + AWS S3 flow where the browser uploads directly to object storage.

## Required behavior

1. `GET /api/upload-url?type=image/jpeg` returns a presigned PUT URL.
2. `POST /api/photos` records metadata after upload confirmation.
3. `GET /api/photos/:id` returns a signed download URL or redirect.
4. Bucket public access is disabled.
5. The app server never proxies the bytes.

## Acceptance criteria

- Presigned URLs expire quickly.
- Uploads are validated after confirmation.
- SQL stores only metadata and keys.
- README explains the request/confirmation flow.

## Hints

- Use UUID-based object keys.
- Use `@aws-sdk/s3-request-presigner`.
- Store the original filename separately from the S3 key.

## Stretch goals

1. Add MIME type validation.
2. Add a size limit check.
3. Add a CDN-backed download mode.
