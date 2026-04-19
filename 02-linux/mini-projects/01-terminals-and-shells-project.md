# Mini-project — 01-terminals-and-shells

_Companion chapter:_ [`01-terminals-and-shells.md`](../01-terminals-and-shells.md)

**Goal.** Ship `whereami.sh` — a 5–10 line bash script that prints user, host, pwd, shell, and git branch (or "no-repo").

**Acceptance criteria.**

- File starts with `#!/usr/bin/env bash` and `set -euo pipefail`.
- Output is exactly five lines, in fixed order.
- Detects "no-repo" without throwing if not in a git tree.
- Has the executable bit set; runs as `./whereami.sh`.
- Idempotent: running it twice produces identical output.

**Hints.** `git rev-parse --abbrev-ref HEAD 2>/dev/null` returns the branch or empty. Use `||` for the fallback: `branch=$(... || echo no-repo)`.

**Stretch.** Add `--json` flag that emits the same info as a one-line JSON object suitable for piping into `jq`.
