# Mini-project — 07-cdns

_Companion chapter:_ [`07-cdns.md`](../07-cdns.md)

**Goal.** Deploy a static site (HTML + CSS + JS assets) to S3 + CloudFront with versioned asset URLs, short TTL on HTML, and long TTL on assets.

**Acceptance criteria:**

- S3 bucket is private; CloudFront uses OAC.
- Asset filenames include a content hash (e.g., `app.abc123.js`).
- Assets served with `Cache-Control: public, max-age=31536000, immutable`.
- `index.html` served with `Cache-Control: public, max-age=60`.
- A deploy script uploads to S3 and invalidates `/index.html`.
- HTTPS enabled with a custom domain (or the CloudFront default domain).

**Hints:**

- Use a build tool (Vite, webpack) that fingerprints output files.
- Upload assets first, then `index.html`, to avoid a window where HTML references missing assets.
- `aws cloudfront create-invalidation --paths "/index.html"` invalidates only the HTML.

**Stretch:** Add a CloudFront Function that adds security headers (`Content-Security-Policy`, `X-Frame-Options`) to every response.
