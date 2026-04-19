# Mini-project — 04-object-storage

_Companion chapter:_ [`04-object-storage.md`](../04-object-storage.md)

**Goal.** Write a CLI tool that syncs a local directory to an S3-compatible bucket using the SDK. Support `--dry-run` mode.

**Acceptance criteria:**

- Accepts `--source <dir>`, `--bucket <name>`, `--prefix <prefix>`, and `--dry-run` flags.
- Lists local files and remote objects; uploads new/changed files, optionally deletes remote-only files.
- `--dry-run` prints what would happen without making changes.
- Works with both AWS S3 and R2 by accepting an `--endpoint` flag.

**Hints:**

- Use `ListObjectsV2` to get remote keys; walk the local directory with `fs.readdir`.
- Compare by key and file size (or MD5/ETag) to detect changes.
- Use `PutObjectCommand` for uploads; `DeleteObjectCommand` for deletes.

**Stretch:** Add parallelism (e.g., 4 concurrent uploads) and a progress bar.
