# Mini-project — 03-permissions

_Companion chapter:_ [`03-permissions.md`](../03-permissions.md)

**Goal.** Ship `secure-home.sh` — recursively tighten `~/.ssh` and any user-config directory you choose. Report exactly which paths it changed.

**Acceptance criteria.**

- Targets a configurable list of directories (default `~/.ssh`).
- Sets directories to `700` and regular files to `600` *unless* the file ends in `.pub` (which becomes `644`).
- Prints, for each path it changed, the old and new mode.
- Idempotent: a second run reports no changes.
- Has a `--dry-run` flag that prints what *would* happen and exits 0.

**Hints.** `stat -c '%a' file` prints the octal mode. Use `find -perm /u+w` (or similar) to find changes. Build a list of (path, old, new) and print at the end.

**Stretch.** Add a `--report` flag that emits JSON suitable for piping into a monitoring system (`jq`).
