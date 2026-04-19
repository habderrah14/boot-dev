# Chapter 04 — Programs

> A program is a file that can be executed. A process is a running instance of one. Your shell is just another program that runs programs.

## Learning objectives

By the end of this chapter you will be able to:

- Distinguish program, process, and daemon.
- Start, inspect, suspend, and kill processes.
- Read and modify `$PATH`; understand shebang lines.
- Run commands in foreground and background; manage jobs.
- Trap signals to clean up reliably.

## Prerequisites & recap

- [Permissions](03-permissions.md) — the execute bit gates "can this run?".

Recap from chapter 03: `chmod +x file` makes a file runnable. The shell still has to find it, which is what this chapter explains.

## The simple version

A **program** is bytes on disk. A **process** is a program in motion — it has a PID, memory, open file descriptors, and a parent. The shell runs a program by `fork()`-ing a child and `exec()`-ing the program inside the child; when the program exits, the shell wakes up and prompts you again.

`$PATH` decides which file gets executed when you type a name. Signals (`SIGTERM`, `SIGKILL`, `SIGHUP`) are how you ask a process to do something — usually "stop".

## In plain terms (newbie lane)

This chapter is really about **Programs**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How `python3 hello.py` becomes a running process and back.

```
   You type "python3 hello.py" + Enter
            │
            ▼
   ┌──────────────┐         fork()           ┌────────────────┐
   │ Bash (PID 1) │ ──────────────────────▶  │ Child (new PID)│
   └──────────────┘                          └─────────┬──────┘
            │                                          │ exec /usr/bin/python3
            │                                          ▼
            │                                  ┌─────────────┐
            │   wait()                         │  python3    │
            │ ◀─────────────────── exit code ──┤  hello.py   │
            ▼                                  └─────────────┘
   prompt returns
```

`fork` makes a copy of the shell. `exec` replaces the copy's program with the new one. The shell `wait`s until the child exits, captures the exit code (`$?`), and prompts again.

## Concept deep-dive

### Programs vs. processes vs. daemons

- **Program.** Bytes in a file. `/usr/bin/python3`.
- **Process.** A running program. Has a PID, parent (PPID), memory image, environment, working directory, open files.
- **Daemon.** A process that runs in the background, usually started by the system, with no controlling terminal. Convention: name ends in `d` (`sshd`, `cron`, `systemd`).

One program can be many processes (`python3` runs as 50 different services on a server). One process is always exactly one program (after `exec`).

### `$PATH` and how the shell finds executables

When you type `python3`, the shell:

1. Checks if it's a shell built-in (e.g., `cd`, `echo`, `export`).
2. Checks if it's an alias.
3. Checks if it's a function defined in the shell.
4. Searches each directory in `$PATH`, **left to right**, taking the first match.

```bash
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/home/dzgeek/.local/bin

which python3        # /usr/bin/python3 — first PATH match
type python3         # 'python3 is /usr/bin/python3'
type cd              # 'cd is a shell builtin'
command -v python3   # POSIX-portable equivalent of `which`
```

To prepend a directory:

```bash
export PATH="$HOME/bin:$PATH"
```

Add the line to `~/.bashrc` (or `~/.zshrc`) for persistence. Order matters — earlier directories win.

### Shebang

The first line of a script tells the kernel what to run it with:

```bash
#!/usr/bin/env python3
print("hi")
```

Make it executable: `chmod +x hi.py`. Now `./hi.py` invokes `python3 hi.py`.

**Always use `#!/usr/bin/env <prog>`** instead of hard-coding `/usr/bin/python3` — `env` searches `$PATH`, so the script works on systems where Python lives in a different prefix (Homebrew's `/opt/homebrew/bin`, virtualenvs, etc.).

### Process inspection

```bash
ps aux                # all processes (BSD-style)
ps -ef                # all processes (System V)
ps -p $$              # this shell
top                   # live; q to quit
htop                  # nicer top, if installed
pgrep python          # find PIDs by command name
pidof firefox         # PID of one program
pstree                # process tree
```

Useful columns: `PID` (process id), `PPID` (parent), `USER`, `%CPU`, `%MEM`, `STAT` (state), `CMD` (command line).

### Sending signals

```bash
kill PID              # SIGTERM (15) — polite "please stop"
kill -9 PID           # SIGKILL  (9) — force, no cleanup
kill -HUP PID         # SIGHUP   (1) — reload config (convention)
kill -INT PID         # SIGINT   (2) — same as Ctrl-C in foreground
pkill -f pattern      # by command line
killall firefox       # by program name
```

A process can install handlers for most signals (`SIGTERM`, `SIGINT`, `SIGHUP`) and clean up before exiting. `SIGKILL` and `SIGSTOP` cannot be caught — the kernel does the work directly.

**Default order:** `kill PID`, wait a few seconds, then `kill -9 PID` only if it's still alive. Going straight to `-9` skips cleanup (open files, locks, child processes).

### Foreground / background / jobs

```bash
long-task &           # start in background; prompt returns
long-task             # foreground; blocks until done
^Z                    # suspend foreground job
jobs                  # list bg/suspended jobs
fg %1                 # resume job 1 in foreground
bg %1                 # resume job 1 in background
nohup cmd &           # ignore SIGHUP so it survives logout
disown %1             # detach job from this shell
```

`&` and `nohup` are fine for one-offs. For services that need to survive forever, use a real supervisor: **systemd** (Linux), **launchd** (macOS), or a container scheduler.

### Environment variables

```bash
export NAME=dzgeek           # set + export to children of this shell
NAME=dzgeek                  # set, but only this shell sees it
ONCE=true cmd                # set ONCE for *this command only*
printenv NAME                # print one
env                          # print all
unset NAME                   # remove
```

Process children **inherit** exported env vars; they do not see unexported shell variables. This is how a config flag set in your `.bashrc` reaches every program you launch.

### Exit codes

Every process returns an integer (0–255) when it exits.

- `0` — success.
- Anything else — failure. Specific tools document specific codes (`grep` returns `1` if no match, `2` on error).

```bash
cmd
echo $?      # the exit code of the last command
```

`set -e` in a script makes the shell exit on any non-zero return. `cmd1 && cmd2` runs `cmd2` only on success; `cmd1 || fallback` only on failure.

### Trapping signals

```bash
#!/usr/bin/env bash
tmp=$(mktemp)
trap 'rm -f "$tmp"; echo "cleaned up"' EXIT INT TERM

# ... do work using "$tmp" ...
```

`trap` registers a handler. `EXIT` runs on any exit (normal or signal). Use it to clean up temp files, kill child processes, release locks.

## Why these design choices

- **Fork + exec**, not "spawn". Forking the shell first lets the child inherit env vars, file descriptors, and current directory before swapping in the new program. This is the foundation of redirection (`> file` is set up *between* fork and exec).
- **Signals as the IPC primitive**. Cheap, kernel-mediated, async. The `kill` model dates to V7 Unix (1979) and remains the universal "stop / reload / hangup" channel.
- **`$PATH` over registries**. A plain text colon-separated list, editable in any shell config. No central database to corrupt; users can override system tools by prepending their own directory.
- **Shebang over file-extension dispatch**. The kernel reads the first two bytes (`#!`) and runs the named interpreter — works for any language without per-language registration.
- **`SIGTERM` then `SIGKILL`**. Polite-then-force gives well-behaved processes a chance to clean up. Programs that ignore `SIGTERM` are buggy; programs that hang on it have unflushed work to do.
- **When you'd choose differently.** Container schedulers (Kubernetes, Nomad) and process supervisors (systemd) replace ad-hoc backgrounding entirely. For long-lived services, never use `nohup &` in production.

## Production-quality code

### Example 1 — Find and stop a stuck process

```bash
$ ps aux | grep '[r]unaway.py'
dzgeek  12345 99.0 2.0  ...  python3 runaway.py

$ kill 12345
$ sleep 2 && ps -p 12345 >/dev/null && echo "still alive" || echo "gone"
gone
```

The `[r]` trick excludes the `grep` itself from matching its own command line. If `kill` doesn't work after a few seconds, escalate to `kill -9`.

### Example 2 — A bash script with proper cleanup

```bash
#!/usr/bin/env bash
set -euo pipefail

work_dir=$(mktemp -d)
log_file="$work_dir/run.log"

cleanup() {
    local rc=$?
    rm -rf "$work_dir"
    [[ $rc -eq 0 ]] && echo "ok" || echo "failed (rc=$rc); see backup at /tmp/last-failure.log"
    exit "$rc"
}
trap cleanup EXIT

# ...do work that uses "$work_dir" and writes "$log_file"...
echo "writing to $log_file"
echo "hello" > "$log_file"
```

`trap cleanup EXIT` runs on success, failure, and signal. The exit code is preserved so callers see the original failure reason.

### Example 3 — Detach a background daemon, capture its PID

```bash
nohup python3 worker.py > worker.log 2>&1 &
pid=$!
echo "worker started (pid $pid)" > worker.pid
disown
```

`$!` is the PID of the most recently backgrounded job. Writing it to `worker.pid` lets a stop script `kill "$(cat worker.pid)"` later. **For real services, use systemd, not this pattern.**

## Security notes

- **Trust `$PATH`.** A writable directory early in `$PATH` lets an attacker drop a malicious `ls` and have it run as you. Never put `.` (current directory) in `$PATH`. Use `~/.local/bin`, not `/tmp`.
- **`kill -9` skips cleanup.** A database server killed with `-9` may leave a corrupt write-ahead log. Always try `SIGTERM` first.
- **Background processes inherit credentials.** A `nohup` job survives your logout and runs with your full permissions. Don't background things you wouldn't trust unattended.
- **Process listings can leak secrets.** A command like `mysql -p<password>` puts the password in `ps aux` output for everyone on the box. Use stdin or a credentials file.
- **Shebang on a privileged path.** A setuid script with `#!/usr/bin/env python3` runs whichever Python comes first in `$PATH` — including a malicious one. Setuid scripts are unsafe; use compiled binaries.

## Performance notes

- **`fork` is cheap on Linux** (copy-on-write pages); spawning thousands of processes per second is feasible.
- **`fork+exec` is fast enough** for shell pipelines but slow vs. an in-process function call (~1 ms vs. ~100 ns). Don't `fork` inside a tight loop in a high-throughput service.
- **`ps aux` is O(n)** in number of processes plus reading from `/proc`. On a busy server, prefer `ps -o pid,comm -p $pid` for one specific process.
- **`pgrep`/`pidof`** read `/proc/*/stat`; both are fast.
- **Signal delivery is essentially free** (a kernel context switch). The expensive part is the handler your program runs — keep it short.

## Common mistakes

- **Forgot `./`.** Symptom: `script.sh: command not found` even though `ls` shows it. Cause: current directory not in `$PATH` (correctly!). Fix: `./script.sh` or move to `~/bin`.
- **Missing execute bit.** Symptom: `Permission denied` running a script. Fix: `chmod +x script.sh`.
- **`kill -9` first, ask later.** Symptom: corrupted state (DB, queues, partial files). Cause: skipped cleanup. Fix: `SIGTERM`, wait, escalate.
- **Unexported variable.** Symptom: child process can't see the value you set. Cause: shell variable, not env variable. Fix: `export NAME=value`.
- **Background process zombies.** Symptom: `ps` shows `[done]` processes that never go away. Cause: parent didn't `wait()`. Fix: use `wait`, or detach with `disown`/`setsid`.
- **`nohup` for production services.** Symptom: service vanishes on reboot. Fix: use `systemd` (or your container platform).

## Practice

1. **Warm-up.** Print the first directory in your `$PATH` (one-liner).
2. **Standard.** Start `sleep 120 &`, confirm with `jobs`, bring it to foreground, cancel with `Ctrl-C`.
3. **Bug hunt.** Your script `run.sh` prints `command not found: run.sh`. Two distinct causes — name them.
4. **Stretch.** Write a one-liner that counts processes per owner: `ps -eo user | sort | uniq -c | sort -rn | head`.
5. **Stretch++.** Use `trap` in bash to delete a temp file on `EXIT`, *and* propagate Ctrl-C with the original exit code.

<details><summary>Show solutions</summary>

```bash
echo "$PATH" | cut -d: -f1
```

3. (a) Missing `./` and the script's directory isn't in `$PATH`. (b) Missing execute bit; or wrong shebang interpreter not installed.

```bash
ps -eo user | sort | uniq -c | sort -rn | head
```

```bash
tmp=$(mktemp)
cleanup() { local rc=$?; rm -f "$tmp"; exit "$rc"; }
trap cleanup EXIT INT TERM
# ... use "$tmp" ...
```

</details>

## Quiz

1. The shell finds `python3` via:
    (a) `$PYTHONPATH` (b) `$PATH` (c) kernel magic (d) `/etc/programs`
2. A process's PID is:
    (a) user id (b) process id (c) parent id (d) program id
3. Which is "force kill"?
    (a) `SIGTERM` (b) `SIGINT` (c) `SIGKILL` (d) `SIGHUP`
4. Background a command:
    (a) `&` (b) `|` (c) `>` (d) `<<`
5. Shebang on first line:
    (a) tells the kernel which interpreter to run (b) is optional (c) must be `#!/bin/sh` (d) is a comment only

**Short answer:**

6. Why use `#!/usr/bin/env python3` instead of hard-coding `/usr/bin/python3`?
7. What's the practical difference between `SIGTERM` and `SIGKILL`?

*Answers: 1-b, 2-b, 3-c, 4-a, 5-a.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-programs — mini-project](mini-projects/04-programs-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Programs live on disk; processes run in memory.
- `$PATH` + executable bit decide what runs when you type a name.
- Polite `SIGTERM` first, escalate to `SIGKILL` only if needed.
- `trap … EXIT` is how shell scripts clean up reliably.
- Use `systemd`/containers for real services; `nohup` is for one-offs.

## Further reading

- `man 7 signal` — full signal reference.
- *The Linux Programming Interface* by Michael Kerrisk, chapters 24–27.
- Next: [input/output](05-input-output.md).
