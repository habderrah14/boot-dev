# Mini-project — 03-storage

_Companion chapter:_ [`03-storage.md`](../03-storage.md)

**Goal.** Run Postgres + your Node app using volumes. Back up the database volume to a `.tgz`.

**Acceptance criteria:**

- Postgres runs with a named volume for its data directory.
- Your app connects to Postgres and creates a table with sample data.
- `docker stop pg && docker start pg` — data survives.
- A backup script creates `pgdata-backup.tgz` using a throwaway Alpine container.
- Restoring from the backup into a new volume produces identical data.

**Hints:**

- The Postgres data directory is `/var/lib/postgresql/data`.
- Use `:ro` when mounting the source volume for backup (read-only safety).
- Test the restore by creating a new volume and a new Postgres container pointing at it.

**Stretch:** Automate the backup as a cron job that runs daily and keeps the last 7 backups.
