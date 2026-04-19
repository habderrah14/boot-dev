# Chapter 01 — Terminals and Shells

> The terminal is not a lesser UI. It is the UI that other UIs are built on.

## Learning objectives

By the end of this chapter you will be able to:

- Distinguish a *terminal*, a *shell*, and a *console*.
- Identify your current shell and switch between bash and zsh.
- Use the keyboard shortcuts that pay back across every command-line tool.
- Read and customize the shell prompt.

## Prerequisites & recap

- Access to a Linux environment (Linux laptop, WSL2, macOS, or a container).
- That's it.

## The simple version

The **terminal** is the *window*; the **shell** is the *program inside the window*. You type into the terminal, the terminal forwards your keystrokes to the shell, the shell parses them into commands and runs other programs. The shell's output flows back through the terminal to your screen.

If you understand that single chain — keyboard → terminal → shell → program → terminal → screen — every other CLI mystery dissolves.

## In plain terms (newbie lane)

This chapter is really about **Terminals and Shells**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

How a single keypress becomes pixels on your screen.

```
   ┌──────┐  keypress   ┌──────────┐  bytes   ┌─────────┐
   │ You  │ ──────────▶ │ Terminal │ ───────▶ │  Shell  │
   └──────┘             │ emulator │          └────┬────┘
                        └──────────┘               │ fork+exec
                              ▲                    ▼
                              │              ┌──────────┐
                              │              │ Program  │
                              │              │ (ls,...) │
                              │              └────┬─────┘
                              │                   │ stdout
                              └──── pixels ◀──────┘
```

The terminal does I/O. The shell does parsing and dispatch. The programs do the actual work.

## Concept deep-dive

### Terms, precisely

- **Terminal (emulator).** GUI program that renders text and handles keyboard input. Examples: GNOME Terminal, iTerm2, Alacritty, kitty, Windows Terminal.
- **Shell.** Program *inside* the terminal that reads commands and runs them. Examples: `bash`, `zsh`, `fish`, `dash`, `sh`.
- **Console.** Historically a physical device; today, a synonym for "terminal". Linux's TTY consoles (Ctrl-Alt-F2) are the literal terminals before any X/Wayland.

### Identifying your shell

```bash
echo $SHELL              # login shell
ps -p $$ -o comm=        # shell of this session ($$ = current pid)
```

`$SHELL` is what your login session was started with. The `ps` form tells you what's *actually* running right now (in case you launched a different shell).

### Shell choice

| Shell | Default on                  | Notes                                       |
|-------|----------------------------|----------------------------------------------|
| bash  | most Linux distros          | universal; assume scripts target it          |
| zsh   | macOS, modern distros       | better completion; mostly bash-compatible    |
| fish  | nowhere by default          | friendlier; not POSIX (scripts may not run)  |
| dash  | Debian's `/bin/sh`          | minimal, fast; what shebang `#!/bin/sh` runs |

Pick **bash** or **zsh**. Switch persistently with `chsh -s /bin/bash`. The path must appear in `/etc/shells`.

### Reading the prompt

```
dzgeek@workstation:~/projects/mycourses$
```

| Part                        | Meaning                                |
|-----------------------------|----------------------------------------|
| `dzgeek`                    | current user                           |
| `workstation`               | hostname                               |
| `~/projects/mycourses`      | current working directory; `~` = home  |
| `$`                         | ready for input (`#` if root)          |

Customize via `PS1` (bash) or `PROMPT` (zsh). A minimal example:

```bash
export PS1='\u@\h:\w\$ '
```

### Anatomy of a command

```
command  [options]  [arguments]
ls       -la         ~/projects
```

- **command** — usually a filename in `$PATH` or a shell built-in (like `cd`).
- **options / flags** — short (`-l`) or long (`--long`); shorts can bundle: `-la` = `-l -a`.
- **arguments** — file paths, strings, etc.

`--` ends option parsing: `rm -- -i` removes a file literally named `-i`.

### Essential shortcuts

| Key                | Action                       |
|--------------------|------------------------------|
| `Tab`              | autocomplete file/command    |
| `↑` / `↓`          | history                      |
| `Ctrl-R`           | reverse history search       |
| `Ctrl-C`           | interrupt current command    |
| `Ctrl-D`           | EOF / exit shell             |
| `Ctrl-L`           | clear screen                 |
| `Ctrl-A` / `Ctrl-E`| start / end of line          |
| `Ctrl-W`           | delete previous word         |
| `Ctrl-U`           | delete to start of line      |
| `Alt-.`            | last argument of last cmd    |
| `!!`               | run previous command         |
| `!$`               | last argument of last cmd    |

Memorize the top six. They compound.

## Why these design choices

- **Terminal vs. shell separation.** A terminal that's "just a window" can render any shell's output, and a shell that's "just text in/out" runs over SSH, in CI, in containers. Coupling them would lose all that.
- **Bash as the lingua franca.** It's not the *best* shell — it's the one every script in the universe targets. POSIX scripting in `bash` runs everywhere; `fish`-only scripts don't.
- **Shortcuts as muscle memory.** A 20% speedup per command, across 50 commands a day, across years, is a career multiplier. Editor-bound shells (`set -o emacs` / `set -o vi`) bake shortcuts into your hands.
- **Hidden config files (`~/.bashrc`).** Versioned, copyable, repeatable. The opposite of a GUI's "click here, then there".
- **When you'd choose differently.** Local-only ergonomics on macOS lean toward `zsh`; explicitly POSIX-only scripts lean toward `dash` for portability and speed.

## Production-quality code

### Example 1 — Where am I?

```bash
pwd                # /home/dzgeek
whoami             # dzgeek
hostname           # workstation
uname -a           # kernel info
which python3      # /usr/bin/python3 — first match in $PATH
type cd            # 'cd is a shell builtin'
echo $SHELL        # login shell
```

`which` finds executables; `type` is a shell built-in that also reports aliases and built-ins. Together they tell you exactly which thing will run.

### Example 2 — Help, in three doses

```bash
man ls             # full manual; q to quit, /word to search
ls --help          # short usage
tldr ls            # community examples (install: brew/apt install tldr)
```

`man` is canonical, `--help` is fast, `tldr` shows real-world examples. Use them in that order when you're confused.

### Example 3 — A tiny `.bashrc` snippet

```bash
# ~/.bashrc — pick aliases that earn their keystrokes
alias ll='ls -alh'
alias gs='git status -sb'
alias gd='git diff'

# Safer rm/cp/mv (prompt before overwrite)
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

# Show git branch in prompt
parse_git_branch() { git branch 2>/dev/null | sed -n 's/^\* \(.*\)/(\1)/p'; }
export PS1='\u@\h:\w$(parse_git_branch)\$ '
```

Source it (`source ~/.bashrc`) or open a new shell.

## Security notes

- **`sudo` runs as root.** Read the command twice before running. Never blindly run a `sudo` command from a stranger.
- **Untrusted scripts.** `curl | bash` is the worst pattern in modern devops. Always download, read, then run.
- **`$PATH` ordering matters.** A `~/.local/bin/ls` shadowing `/usr/bin/ls` is a privilege-escalation vector. Don't put writable directories early in `$PATH`.
- **Shell history can leak secrets.** `mysql -p<password>` ends up in `~/.bash_history`. Use `read -s` for prompts or a credentials file with `600` permissions.
- **Beware of `eval`.** `eval $UNTRUSTED` is arbitrary code execution. Don't.

## Performance notes

- A shell prompt should render in **<10 ms**. If it lags, you put something heavy in `PS1` (probably a network or git call). Cache or async it.
- `bash` startup: ~5 ms cold; `zsh` with full Oh-My-Zsh: ~300 ms — noticeable in CI loops.
- Tab completion across `$PATH` runs every time; a 50k-file home directory makes it crawl. `compgen` indexes help.
- For one-shot tools called from a Makefile or hot loop, `dash` (~1 ms) beats `bash` (~5 ms).

## Common mistakes

- **Spaces in paths.** Symptom: `cp My File foo` says "no such file 'My'". Cause: shell splits on whitespace. Fix: quote — `cp "My File" foo`.
- **`rm -rf $VAR/*` when `$VAR` is empty.** Symptom: filesystem destroyed. Cause: expands to `rm -rf /*`. Fix: `[ -n "$VAR" ] || exit 1` before the rm; better, use `set -u`.
- **Wrong shell.** Symptom: a script with `[[ ]]` fails on a system where `/bin/sh` is `dash`. Cause: shebang says `#!/bin/sh`. Fix: shebang `#!/usr/bin/env bash`.
- **`./` not in `$PATH`.** Symptom: `myscript.sh` says "command not found" when the file is right there. Cause: current directory is intentionally not in `$PATH`. Fix: `./myscript.sh`.
- **Trusting cwd.** Symptom: a deploy script blows up files because it ran from the wrong directory. Fix: `cd "$(dirname "$0")"` at the top of every script.

## Practice

1. **Warm-up.** Print your username, home directory, and current working directory.
2. **Standard.** Find the full path of `python3` and print its version on the same line.
3. **Bug hunt.** `ls My Documents` lists two things — why?
4. **Stretch.** Use `history | grep cd` to find the last five `cd` commands you ran.
5. **Stretch++.** Customize `PS1` to show the current git branch (research `__git_ps1`).

<details><summary>Show solutions</summary>

```bash
echo "$USER $HOME $(pwd)"
```

```bash
echo "$(which python3) $(python3 --version)"
```

3. The shell splits arguments on whitespace; `My` and `Documents` become two separate arguments. Quote: `ls "My Documents"`.

```bash
history | grep -w cd | tail -5
```

</details>

## Quiz

1. The difference between terminal and shell:
    (a) same thing (b) window vs. program (c) hardware vs. software (d) GUI vs. TTY
2. `Ctrl-R` does:
    (a) redo (b) reverse history search (c) refresh (d) restart
3. Which is a shell built-in, not a separate executable?
    (a) `ls` (b) `cd` (c) `grep` (d) `python3`
4. `~` in a path means:
    (a) root (b) home (c) current (d) previous
5. `$PATH` is:
    (a) the current directory (b) an env var listing where to search for executables (c) a shell alias (d) the home path

**Short answer:**

6. Why must you quote `"My Documents"`?
7. Under what circumstance would `which python3` and `type python3` disagree?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-terminals-and-shells — mini-project](mini-projects/01-terminals-and-shells-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Terminal = window; shell = program; programs do the work.
- Pick bash or zsh; learn the top six shortcuts; customize `PS1` once.
- `$PATH` ordering controls which binary runs when there are duplicates.
- Be paranoid about `sudo`, `curl | bash`, and unquoted variables.

## Further reading

- William Shotts, *The Linux Command Line* (free online).
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) — read every entry.
- Next: [filesystems](02-filesystems.md).
