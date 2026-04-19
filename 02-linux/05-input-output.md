# Chapter 05 — Input / Output

> Every Unix program speaks the same three-stream language: `stdin`, `stdout`, `stderr`. Learn those, learn pipes, and small tools start feeling like a programming language.

## Learning objectives

By the end of this chapter you will be able to:

- Use stdin, stdout, and stderr deliberately.
- Redirect and merge streams; understand `2>&1` ordering.
- Compose short toolchains with `grep`, `cut`, `sort`, `uniq`, `wc`, `head`, `tail`, `awk`, `sed`, `tee`, `xargs`.
- Write a bash one-liner that solves a real problem (log analysis, top-N).

## Prerequisites & recap

- [Programs](04-programs.md) — every process has stdin/stdout/stderr.

Recap: a process is a program in motion with file descriptors 0/1/2 wired to streams. The shell sets those up *between* `fork` and `exec` — that's why `cmd > out` works.

## The simple version

A Unix program reads from **stdin** (fd 0), writes data to **stdout** (fd 1), and writes diagnostics to **stderr** (fd 2). The shell lets you redirect each of these to a file (`>`, `<`, `2>`), or wire one program's stdout to another program's stdin (`|`).

This is the one trick that makes the shell composable. Once you internalize it, "twenty short tools that each do one thing" become "twenty thousand combinations".

## In plain terms (newbie lane)

This chapter is really about **Input / Output**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The three streams of a process and how `|` and `>` reroute them.

```
                   ┌─────────────────────┐
                   │     A process       │
                   │                     │
   keyboard ──▶ 0  │   stdin             │
                   │                     │
                   │   stdout      1 ──▶ terminal
                   │                     │
                   │   stderr      2 ──▶ terminal
                   └─────────────────────┘

   Pipeline:    A | B  →   A's stdout becomes B's stdin
                              ┌──────┐    ┌──────┐
                              │  A   │ ──▶│  B   │ ──▶ terminal
                              └──────┘    └──────┘
                                  │ (stderr to terminal)

   Redirect:    A > out 2>&1  →  stdout to file, stderr merged into stdout
```

## Concept deep-dive

### The three streams

Each process is born with three file descriptors open:

| FD | Name   | Default destination | Convention |
|----|--------|---------------------|------------|
| 0  | stdin  | keyboard            | input      |
| 1  | stdout | terminal            | data       |
| 2  | stderr | terminal            | diagnostics|

A well-behaved program prints **data** to stdout and **diagnostics/errors/progress** to stderr. That separation lets you pipe data without having log lines polluting it.

### Redirection

```bash
cmd > out.txt          # stdout to file (truncate)
cmd >> out.txt         # stdout to file (append)
cmd 2> err.txt         # stderr to file
cmd > out.txt 2>&1     # stdout AND stderr to out.txt
cmd &> all.txt         # bash shortcut for above
cmd < in.txt           # stdin from file
cmd > /dev/null 2>&1   # silence everything
```

`2>&1` reads as "redirect fd 2 to whatever fd 1 currently points to". **Order matters**:

- `cmd > out 2>&1` — fd 1 now points to `out`; *then* fd 2 follows fd 1 to `out`. ✓
- `cmd 2>&1 > out` — fd 2 points to original terminal; *then* fd 1 moves to `out`. Errors still go to terminal. ✗

### Pipes

```bash
cmd1 | cmd2            # cmd1's stdout becomes cmd2's stdin
cmd1 |& cmd2           # bash: pipe stderr too
```

Pipes are the Unix superpower. The two processes run **concurrently**, with the kernel buffering bytes between them. A pipe of N stages runs N processes simultaneously.

### Process substitution

```bash
diff <(cmd1) <(cmd2)         # bash/zsh — treat command output as a file
```

`<(cmd)` runs `cmd` and presents its stdout as a path that other tools can read. Useful when a tool wants files but you have streams.

### The classic toolkit

| Tool                    | Job                                                  |
|-------------------------|------------------------------------------------------|
| `cat`                   | concat / dump                                        |
| `head -n N`, `tail -n N`| first/last N lines                                   |
| `wc -l/-w/-c`           | count lines/words/bytes                              |
| `grep PATTERN`          | filter lines (`-i`, `-v`, `-E`, `-r`)                |
| `cut -d: -f1,3`         | split by delimiter, keep fields                      |
| `awk '{print $2}'`      | mini-language for fields, math, conditions           |
| `sed 's/a/b/g'`         | stream edit                                          |
| `sort`, `sort -n`, `-k`,`-u` | sort lines (numeric, by key, unique)            |
| `uniq -c`, `uniq -d`    | collapse adjacent duplicates                         |
| `tr 'A-Z' 'a-z'`        | translate / squeeze characters                       |
| `tee file`              | duplicate stream to file *and* stdout                |
| `xargs cmd`             | turn stdin into command arguments                    |
| `column -t`             | align columns                                        |
| `jq`                    | filter / transform JSON (third-party)                |

### Here-docs and here-strings

```bash
cat <<EOF
Line one
Line two — variables expand: $USER
EOF

cat <<'EOF'                # quoted EOF: NO expansion
Line literally with $USER
EOF

grep <<< "hello world"     # here-string
```

Here-docs are how you embed multi-line content (config templates, SQL) inside a script.

## Why these design choices

- **Three streams over two.** Without separate stderr, every pipe would have to choose between losing diagnostics or polluting data. Two-fd systems (DOS) historically conflated the two and shell pipelines were uglier for it.
- **Redirection happens in the shell, not in the program.** The program just `read`s/`write`s file descriptor 0/1/2; the shell rewires them with `dup2()` between fork and exec. That uniformity is *why* every program is pipeable without doing anything special.
- **`<(cmd)` process substitution.** Lets file-oriented tools (`diff`, `comm`) operate on live command output without temp files. The shell creates an FIFO under the hood.
- **Many small tools over one big one.** The Unix philosophy. A 20-tool pipeline is harder to discover but easier to recombine than a giant monolith.
- **When you'd choose differently.** For complex transformations (multi-line records, structured data), a real programming language wins. `jq` for JSON; Python or PowerShell when the pipeline grows past 5 stages.

## Production-quality code

### Example 1 — Top-5 words in a file

```bash
tr -s '[:space:]' '\n' < book.txt \
  | tr 'A-Z' 'a-z' \
  | grep -E '^[a-z]+$' \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -n 5
```

Pipeline reasoning:

1. `tr -s '[:space:]' '\n'` — collapse runs of whitespace into newlines (one word per line).
2. `tr 'A-Z' 'a-z'` — lowercase.
3. `grep -E '^[a-z]+$'` — keep only pure-letter words (drop punctuation-stripped junk).
4. `sort` — group identical words.
5. `uniq -c` — collapse adjacent duplicates and prepend the count.
6. `sort -rn` — sort by count descending.
7. `head -n 5` — take top five.

Each stage does one thing. Memorize this shape; you'll write it once a week.

### Example 2 — Top-10 IPs in an Nginx access log

```bash
awk '{print $1}' /var/log/nginx/access.log \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -10
```

`$1` is the client IP in the default Combined Log Format. Same shape as Example 1.

### Example 3 — Safe `xargs` over filenames with spaces

```bash
find . -type f -name '*.log' -print0 \
  | xargs -0 -I{} gzip --keep {}
```

`-print0` (find) and `-0` (xargs) use NUL as the separator instead of newline — survives spaces, quotes, and tabs in filenames. `-I{}` lets you place the filename anywhere in the command, not just at the end.

### Example 4 — Tee + log rotation pattern

```bash
long_running_command 2>&1 | tee >(gzip > run.log.gz) | head -n 100
```

`tee` duplicates the stream: 100 lines to the screen, the full thing compressed to disk. `>(gzip ...)` is process substitution writing into a subprocess.

## Security notes

- **Don't pipe untrusted input into `bash`.** `curl https://example.com/install.sh | bash` is the canonical anti-pattern. Download, read, then run.
- **Filenames as arguments.** `xargs` and shell loops choke on filenames with spaces, newlines, or hyphens (`-rf`). Use `-print0`/`-0` and `--` to end option parsing: `rm -- "$file"`.
- **Sensitive data in `tee`.** `tee` writes to the named file with current umask; default `644` may be world-readable. Use `tee >(install -m 600 /dev/stdin file)` or write the file first and chmod.
- **`>` truncates immediately.** `cmd > important.txt` clobbers `important.txt` even if `cmd` fails. Use `set -o noclobber` (`set -C`) to make `>` refuse to overwrite, then opt-in with `>|`.
- **Log injection.** A user-controlled string echoed into a log can include `\033[2J` (clear screen) or fake other log lines. Sanitize untrusted strings before logging.

## Performance notes

- **Pipes are concurrent.** `slow1 | slow2` runs both processes in parallel; total wall time ≈ max(time(slow1), time(slow2)) + tiny overhead, not sum.
- **Pipe buffer is ~64 KiB on Linux.** A fast producer with a slow consumer blocks once the buffer fills (built-in backpressure).
- **`grep` is C-fast.** Filtering with `grep` *before* heavier tools (`awk`, `sort`) keeps the pipeline lean.
- **`sort` is the typical bottleneck.** It's O(n log n) and may spool to disk for inputs larger than memory; set `LC_ALL=C` (byte sort, no locale) for ~3× speedup when locale-correct ordering doesn't matter.
- **`xargs -P N`** parallelizes invocations across N processes — instant speedup when each command is independent.
- **`cat file | grep x` is the famous "useless use of cat"** — slower than `grep x file` (extra process, extra pipe). Cosmetic in pipelines you write once; matters in scripts run often.

## Common mistakes

- **`cmd 2>&1 > file`** — sends stderr to the *original* stdout (terminal), not the file. Fix: `cmd > file 2>&1`.
- **`xargs` choking on spaces.** Symptom: weird "no such file" errors with file names like `My Doc.txt`. Cause: default whitespace splitting. Fix: `find -print0 | xargs -0`.
- **`grep` with regex special chars.** Symptom: `grep .` matches everything; `grep 1.2` matches `1x2` too. Cause: `.` is a metacharacter. Fix: `grep -F` for fixed strings, or escape with `\.`.
- **Locale-induced slow `sort`.** Symptom: a `sort` over a 100MB log takes 30s. Cause: UTF-8 locale collation. Fix: `LC_ALL=C sort`.
- **Truncated output redirection.** Symptom: a long-running command's `> output` is empty or partial after Ctrl-C. Cause: shell `>` redirected the file but the output was buffered in the program. Fix: `stdbuf -oL cmd > out` or use `>>` for append + check at the end.
- **`>` overwriting precious files.** Symptom: typo destroys data. Fix: `set -C` (noclobber) + explicit `>|` when overwriting is intended.

## Practice

1. **Warm-up.** Pipe `echo "HELLO"` through `tr` to lowercase.
2. **Standard.** From `/etc/passwd`, print usernames whose login shell is `/bin/bash`.
3. **Bug hunt.** `cmd 2>&1 | grep error` doesn't catch some errors. Why might that be?
4. **Stretch.** Replace every tab with four spaces in `*.py` files (preview with `grep -l` first).
5. **Stretch++.** Print the unique hostnames from `/etc/hosts`, sorted, one per line.

<details><summary>Show solutions</summary>

```bash
echo "HELLO" | tr 'A-Z' 'a-z'
```

```bash
grep '/bin/bash$' /etc/passwd | cut -d: -f1
```

3. Some programs print errors to **stdout** (especially poorly-written ones, or when stderr is buffered). `2>&1` only merges fd 2 into fd 1; if the program never wrote to fd 2, there's nothing to catch. Inspect with `cmd > /tmp/out 2> /tmp/err` and look at both.

```bash
# preview which files have tabs
grep -lP '\t' *.py
# replace
grep -lP '\t' *.py | xargs sed -i 's/\t/    /g'
```

```bash
awk '{for (i=2; i<=NF; i++) print $i}' /etc/hosts | sort -u
```

</details>

## Quiz

1. Redirect stderr to a file:
    (a) `> err` (b) `2> err` (c) `|& err` (d) `>> err`
2. `cmd > out 2>&1` sends:
    (a) stdout and stderr to `out` (b) only stderr to `out` (c) only stdout (d) swaps them
3. `uniq -c`:
    (a) removes duplicates anywhere (b) collapses *adjacent* duplicates and prepends count (c) counts all words (d) sorts
4. Pipe stdin of `B` from stdout of `A`:
    (a) `A || B` (b) `A | B` (c) `A > B` (d) `A ; B`
5. `tee file`:
    (a) silences output (b) duplicates to file and stdout (c) overwrites the terminal (d) is obsolete

**Short answer:**

6. When should output be written to stderr instead of stdout?
7. Why is `xargs -0` safer than the default `xargs`?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-input-output — mini-project](mini-projects/05-input-output-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Three streams: stdin (0), stdout (1), stderr (2). Use stderr for diagnostics.
- Redirect with `>`, `<`, `2>`, `2>&1`; pipe with `|`. Order matters in `2>&1`.
- Twenty small tools compose into a programming language. Memorize the canonical pipeline shape.
- Use `-print0` / `-0` for filenames; `LC_ALL=C` to speed up `sort`; `set -C` to prevent overwrites.

## Further reading

- Brian Kernighan & Rob Pike, *The Unix Programming Environment*.
- [`man bash`](https://man7.org/linux/man-pages/man1/bash.1.html) — the redirection section is worth re-reading.
- Next: [packages](06-packages.md).
