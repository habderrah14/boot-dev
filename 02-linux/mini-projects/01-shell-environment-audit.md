# Mini-project — Shell Environment Audit

## Goal

Build a small shell script toolkit that audits your terminal/shell environment and reports whether it is safe and productive for backend development.

## Deliverable

A repository folder (or gist) containing:

- `audit-shell.sh` (main script)
- `README.md` explaining usage
- sample output from your machine

## Required checks

Your script must report:

1. Current user, host, shell, and working directory.
2. Whether key commands resolve correctly: `bash`, `zsh`, `python3`, `git`, `docker`.
3. Whether any user-writable directory appears **before** system dirs in `PATH`.
4. Whether shell config file exists (`~/.bashrc` or `~/.zshrc`).
5. Whether at least 3 productivity aliases are defined.

## Acceptance criteria

- Script begins with `#!/usr/bin/env bash` and uses `set -euo pipefail`.
- Script exits with code `0` on success and non-zero on fatal checks.
- Output is readable and labeled by check section.
- At least one warning condition is demonstrated in `README.md`.
- No interactive prompts required to run the audit.

## Suggested output format

```text
[INFO] User: dzgeek
[INFO] Shell: /usr/bin/zsh
[PASS] command: git -> /usr/bin/git
[WARN] PATH ordering: /home/dzgeek/.local/bin appears before /usr/bin
[PASS] shell config: ~/.zshrc found
[FAIL] aliases: found 2, expected >= 3
```

## Hints

- Use `command -v` for command resolution.
- Parse `PATH` by splitting on `:`.
- Use `test -w` to check whether a directory is user-writable.
- Count alias lines from config with `grep` and `wc -l`.

## Stretch goals

1. Add a `--json` mode for machine-readable output.
2. Add a `--strict` mode that treats warnings as failures.
3. Add unit-like self-checks for helper functions.

## Evaluation rubric (self-check)

- **Correctness (40%)** — checks behave correctly across pass/fail scenarios.
- **Robustness (30%)** — handles missing commands and missing files gracefully.
- **Clarity (20%)** — output is understandable at a glance.
- **Polish (10%)** — docs and script style are clean and consistent.
