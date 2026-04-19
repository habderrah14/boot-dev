# Mini-project — 05-video-streaming

_Companion chapter:_ [`05-video-streaming.md`](../05-video-streaming.md)

**Goal.** Write a script that takes an input MP4, transcodes it to HLS at 360p and 720p, uploads to S3, and outputs a playable CDN URL.

**Acceptance criteria:**

- Accepts an input file path and an output S3 prefix.
- Produces `master.m3u8`, two variant playlists, and all `.ts` segments.
- Uploads to S3 with correct `Content-Type` and `Cache-Control` headers.
- Prints the playable URL: `https://cdn.example.com/<prefix>/master.m3u8`.
- `.ts` segments get `immutable` caching; `.m3u8` files get short TTLs.

**Hints:**

- Use `child_process.execFile` to call `ffmpeg`.
- Walk the output directory recursively to find all generated files.
- Set `Content-Type: application/vnd.apple.mpegurl` for `.m3u8` and `video/mp2t` for `.ts`.

**Stretch:** Add a third rendition (1080p) and generate a thumbnail image from the first frame (`ffmpeg -i input.mp4 -vframes 1 -q:v 2 thumb.jpg`).
