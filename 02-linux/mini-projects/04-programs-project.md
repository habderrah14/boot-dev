# Mini-project — 04-programs

_Companion chapter:_ [`04-programs.md`](../04-programs.md)

**Goal.** Build `watchlog.sh` — tail a log file in the background, print its PID, and shut down cleanly on Ctrl-C using `trap`.

**Acceptance criteria.**

- Takes the log file path as `$1`; refuses if missing.
- Starts `tail -F` in the background; captures the PID.
- Prints `watching <path> (pid <pid>)` on start.
- On `EXIT`, `INT`, or `TERM`: kills the `tail`, prints `stopped`, exits with the original exit code.
- Re-running it doesn't leak processes (no orphan `tail`s in `ps`).

**Hints.** `tail -F "$log" &` then `pid=$!`. The `trap` handler should `kill "$pid" 2>/dev/null || true` and `wait "$pid" 2>/dev/null || true` to reap.

**Stretch.** Add a `--filter <regex>` flag that pipes through `grep --line-buffered`, preserving live output.
