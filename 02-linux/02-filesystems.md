# Chapter 02 — Filesystems

> On Linux, *everything is a file* — devices, sockets, even processes. Understanding the filesystem is understanding the system.

## Learning objectives

By the end of this chapter you will be able to:

- Navigate the Unix directory tree using absolute and relative paths.
- Create, copy, move, and delete files and directories safely.
- Use `ls`, `stat`, `file`, `find`, and `grep`/`rg` confidently.
- Read and follow logs as they grow.
- Avoid the disasters that `rm -rf`, missing quotes, and case-mismatches cause.

## Prerequisites & recap

- [Terminals and Shells](01-terminals-and-shells.md) — you can type into a shell and read its output.

Recap: the shell forwards your commands to programs. Most of those programs operate on files in the filesystem.

## The simple version

Linux has **one tree** rooted at `/`. There are no drive letters; other devices and filesystems are *mounted* onto directories. Paths are either **absolute** (starting with `/`) or **relative** (starting from the current directory). Hidden files start with `.` and are filtered from `ls` unless you ask.

Five commands cover 90% of daily filesystem work: `cd`, `ls`, `cat`/`less`, `find`, `grep` (or `rg`).

## In plain terms (newbie lane)

This chapter is really about **Filesystems**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The standard Linux directory hierarchy.

```
   /
   ├── bin/      → /usr/bin    system commands
   ├── boot/                   kernel + bootloader
   ├── dev/                    device files (sda, tty, null, …)
   ├── etc/                    system configuration
   ├── home/                   user home directories
   │   └── dzgeek/             ← your $HOME (~)
   │       ├── .bashrc         hidden config
   │       └── projects/
   ├── proc/                   kernel/process pseudo-FS
   ├── root/                   root user's home
   ├── tmp/                    transient files (cleared on reboot)
   ├── usr/                    user programs and libraries
   │   ├── bin/   ← most CLI tools live here
   │   └── lib/
   └── var/                    variable state (logs, caches)
       └── log/
```

Mounted filesystems (USB drives, network shares) appear as subdirectories — typically under `/mnt`, `/media`, or `/run`.

## Concept deep-dive

### Paths

- **Absolute** — starts with `/`. Same meaning anywhere: `/home/dzgeek/hello.py`.
- **Relative** — anything else. Resolved against the current working directory.
- `.` — current directory.
- `..` — parent.
- `~` — your home (shell expansion; not understood by every program).
- `~alice` — Alice's home.

### Core commands

| Command                 | Use                                                |
|-------------------------|----------------------------------------------------|
| `pwd`                   | print working directory                            |
| `cd PATH`               | change directory; `cd -` toggles to previous       |
| `ls`                    | list (`-l` long, `-a` all, `-h` human sizes)       |
| `tree`                  | recursive view                                     |
| `mkdir -p a/b/c`        | make directories, parents as needed                |
| `rmdir DIR`             | remove an *empty* directory                        |
| `rm FILE`               | remove a file                                      |
| `rm -rf DIR`            | remove a directory recursively (DANGER)            |
| `cp src dst`            | copy (`-r` recursively, `-i` prompt)               |
| `mv src dst`            | move/rename (`-i` prompt)                          |
| `ln -s target link`     | symbolic link                                      |
| `stat FILE`             | full metadata (size, perms, atime/mtime/ctime)     |
| `file FILE`             | guess the file type by content                     |
| `du -sh DIR`            | total size of DIR (human readable)                 |
| `df -h`                 | free disk space per mount                          |

### Reading files

```bash
cat short.txt          # dump everything
less long.txt          # pager: q to quit, /pattern to search
head -n 20 file        # first 20 lines
tail -n 20 file        # last 20 lines
tail -f app.log        # follow as it grows (tail -F survives rotation)
```

`less` is the right default for files of unknown length — it doesn't load everything into memory and supports search.

### Finding files

```bash
find . -name "*.py"               # by name
find . -type d -name tests        # only directories named 'tests'
find . -type f -mtime -7          # modified in the last 7 days
find . -size +1M                  # larger than 1 MB
find . -name node_modules -prune -o -print   # exclude a directory
locate readme                     # fast, uses prebuilt DB (sudo updatedb)
```

### Finding *inside* files

```bash
grep -rn "TODO" .       # recursive, with line numbers
rg "TODO"               # ripgrep — faster, respects .gitignore
rg -t py "def main"     # only Python files
```

`rg` (ripgrep) is dramatically faster than `grep -r` and is the default for working programmers in 2024+.

### Hidden files

Files starting with `.` are hidden from `ls` unless you pass `-a`. The convention covers config (`~/.bashrc`, `~/.ssh/`), tool state (`~/.cache/`, `~/.local/share/`), and per-project overrides (`.env`, `.gitignore`).

### Symbolic vs. hard links

```bash
ln file hardlink         # second name for the same inode; both must be on same FS
ln -s file softlink      # pointer to a path; can dangle if target is removed
```

Hard links share the file's inode (metadata + content). Soft links store a path. Most of the time you want a soft link.

## Why these design choices

- **One tree, no drive letters.** Lets `cd /any/path` work uniformly whether the data is local SSD, NFS, or a USB stick. Mount points hide the distinction.
- **`/etc` for config, `/var` for state, `/usr` for programs.** Lets `/usr` be read-only (immutable images, container layers) while writable state stays elsewhere. The Filesystem Hierarchy Standard (FHS) codifies this.
- **Hidden = leading dot.** A pure convention with no kernel meaning, which means it's universal across tools without coordination.
- **Symlinks vs. hardlinks.** Hardlinks are atomic but constrained (same FS, no directories). Symlinks are flexible but can dangle. The trade-off lets you pick per use case.
- **Case-sensitive paths.** A surprise to macOS/Windows users; a feature to script writers — `Makefile` and `makefile` are different files. Don't depend on case-insensitive lookup.
- **When you'd choose differently.** Container-friendly distros (NixOS, Bazel) replace `/usr` with content-addressed stores. They get reproducibility at the cost of FHS expectations.

## Production-quality code

### Example 1 — Scaffold a project safely

```bash
#!/usr/bin/env bash
set -euo pipefail

name=${1:?usage: $0 <project-name>}

if [[ -e "$name" ]]; then
    echo "error: '$name' already exists" >&2
    exit 1
fi

mkdir -p "$name"/{src,tests,docs}
touch "$name"/{README.md,.gitignore}
cat > "$name/.gitignore" <<'EOF'
__pycache__/
.venv/
*.pyc
EOF

tree "$name"
```

`set -euo pipefail` is the right default for any non-trivial bash script — it fails on errors, undefined variables, and broken pipelines.

### Example 2 — Bulk rename safely

```bash
#!/usr/bin/env bash
set -euo pipefail

# Rename every .md to .markdown in the current directory
shopt -s nullglob   # if no matches, the loop runs zero times instead of once on the literal '*.md'

for f in *.md; do
    target="${f%.md}.markdown"
    [[ -e "$target" ]] && { echo "skip: $target exists" >&2; continue; }
    mv -- "$f" "$target"
    echo "renamed: $f -> $target"
done
```

`${f%.md}` strips the trailing extension. `--` ends option parsing so a filename starting with `-` doesn't get interpreted as a flag.

### Example 3 — Find the ten largest files

```bash
du -ah . 2>/dev/null | sort -hr | head -n 10
```

`du -a` lists files too (not just directories); `sort -hr` sorts human-readable sizes in reverse; `head -n 10` keeps the top.

## Security notes

- **`rm -rf` is irreversible.** No "trash" by default. Triple-check the path; consider `trash-cli` (`trash` command) for an undo-able alternative.
- **`rm -rf $VAR/*` when `$VAR` is empty.** Becomes `rm -rf /*`. Always quote (`"$VAR"`) and use `set -u` to fail on undefined vars.
- **Symlink races.** A privileged process traversing into a directory it doesn't own can be tricked by a hostile symlink. Use `realpath -e` and check ownership before opening.
- **World-writable directories.** `/tmp` exists for them, with the **sticky bit** ensuring users can only delete their own files. Don't replicate `/tmp`-like permissions elsewhere.
- **`.gitignore` is not security.** A `.env` file in your repo isn't safe just because it's gitignored locally — once committed, history keeps it forever.

## Performance notes

- **Many small files** stress the filesystem (millions of inodes, slow `ls`, slow `find`). Use `find . -type f | wc -l` to know what you're working with.
- **`ls` is O(n) with sorting**; an unsorted `ls -f` is faster on huge directories.
- **`find` walks the tree**; `locate` is O(1) lookup against an index. For one-shot queries on a small tree, use `find`. For repeated queries on a large tree, `locate` (or build your own index).
- **`rg` vs. `grep -r`**: ripgrep parallelizes across cores and skips `.gitignore`d files; typically 5–50× faster on large repos.
- **`tail -f` consumes a poll loop**; `tail -F` re-opens on rotation. For high-volume logs, use `journalctl -f` or a real log shipper.
- **WSL2 quirk.** Reading files under `/mnt/c/...` is dramatically slower than the Linux-native filesystem. Keep work inside `~`.

## Common mistakes

- **Disastrous `rm`.** Symptom: lost work. Cause: typo in path, empty variable, missing `-i`. Fix: `set -u`; alias `rm='rm -i'`; review interactively or use `trash`.
- **Missing trailing slash on `cp`/`mv`.** Symptom: `cp file backup` *renames* `file` to `backup` if `backup` doesn't exist. Cause: cp infers intent from existence. Fix: `cp file backup/` (forces "into directory") and pre-create `backup`.
- **Case-sensitivity surprise.** Symptom: `import App` works on macOS, fails in CI. Cause: `app.py` vs. `App.py`. Fix: standardize case from the start.
- **Path with spaces, no quotes.** Symptom: command parses your filename as multiple arguments. Fix: quote variable expansions: `cp "$src" "$dst"`.
- **`cd` errors silently in scripts.** Symptom: subsequent commands run in the wrong dir. Cause: missing `set -e` or `cd path || exit`. Fix: `cd "$dir" || exit 1`.
- **`tail -f` on rotated logs.** Symptom: output stops mid-day. Fix: use `tail -F`.

## Practice

1. **Warm-up.** From `/tmp`, return to your home in three different ways (no shell history).
2. **Standard.** Find every file in your home directory modified in the last 24 hours (`-mtime -1`).
3. **Bug hunt.** `cp ~/file ~/backup` succeeds if `~/backup` is a directory but renames if it doesn't exist. Why?
4. **Stretch.** Print the ten largest files under `.` (recursive), in human-readable sizes.
5. **Stretch++.** Use `find -exec` (or `xargs`) to delete every `__pycache__` directory recursively, dry-running first.

<details><summary>Show solutions</summary>

```bash
cd        # implicit $HOME
cd ~      # tilde expansion
cd $HOME  # env var
```

```bash
find ~ -type f -mtime -1
```

3. `cp` decides: if the target exists and is a directory, copy *into* it; otherwise *rename* the source to the target name. To force "into directory" semantics, use a trailing slash: `cp ~/file ~/backup/`.

```bash
du -ah . 2>/dev/null | sort -hr | head -n 10
```

```bash
# dry run
find . -type d -name __pycache__ -print
# delete
find . -type d -name __pycache__ -exec rm -rf {} +
```

</details>

## Quiz

1. `.` means:
    (a) home (b) current dir (c) root (d) hidden
2. Hidden files start with:
    (a) `_` (b) `.` (c) `~` (d) `$`
3. `cd` with no args goes to:
    (a) root (b) home (c) previous (d) error
4. `rm` removes which without `-r`?
    (a) files only (b) files and empty dirs (c) recursively (d) nothing
5. To follow a log as it grows:
    (a) `cat -f` (b) `less` (c) `tail -f` (d) `head`

**Short answer:**

6. Why doesn't Linux have drive letters?
7. When would you prefer `rg` over `grep -r`?

*Answers: 1-b, 2-b, 3-b, 4-a, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-filesystems — mini-project](mini-projects/02-filesystems-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- One tree, rooted at `/`; no drive letters.
- Paths are absolute or relative; `.`, `..`, `~` are your friends.
- `find` walks; `locate` indexes; `rg` is the modern grep.
- `set -euo pipefail` and quoted variables prevent the worst of bash's footguns.

## Further reading

- `man hier` — the filesystem hierarchy standard.
- [Greg's Wiki — Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls).
- Next: [permissions](03-permissions.md).
