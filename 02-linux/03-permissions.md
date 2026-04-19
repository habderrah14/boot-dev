# Chapter 03 — Permissions

> Every file has an owner, a group, and three permission bits each for "user", "group", and "other". Memorize those ten characters and Linux stops being mysterious.

## Learning objectives

By the end of this chapter you will be able to:

- Read `ls -l` output and translate symbolic ↔ octal permission modes.
- Change ownership and permissions with `chown` and `chmod`.
- Apply the principle of least privilege.
- Recognize when `sudo` is right — and when it's a workaround for a broken setup.
- Avoid the catastrophic `chmod 777` and `chmod -R` on the wrong directory.

## Prerequisites & recap

- [Filesystems](02-filesystems.md) — you can navigate to a file you want to inspect.

Recap: `ls -l` shows the long-form listing including the ten permission characters, owner, group, size, and mtime. This chapter teaches you to *read* that line.

## The simple version

Linux permissions are a 3×3 grid:

```
            read   write  execute
user        ?      ?      ?
group       ?      ?      ?
other       ?      ?      ?
```

Each cell is one bit. That's nine bits, displayed as `rwxrwxrwx` and addressed by three octal digits (`r=4`, `w=2`, `x=1`). For files, `x` means "runnable"; for directories, `x` means "you can `cd` into it".

Almost every permission problem reduces to: "the user the process runs as can't do *X* to this file because of *Y*." Read the ten characters, the owner, and the group; the answer follows.

## In plain terms (newbie lane)

This chapter is really about **Permissions**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

The ten characters of `ls -l` decoded.

```
   -rw-r--r--   1 dzgeek staff  1024 Apr 16 10:00 notes.md
   │└─┬─┘└┬┘└┬┘
   │  │   │  │
   │  │   │  └── other:   r--
   │  │   └───── group:   r--
   │  └───────── user:    rw-
   └──────────── type: '-' = file, 'd' = dir, 'l' = symlink

   octal:  6      4      4
           rw-    r--    r--
           4+2+0  4+0+0  4+0+0   →   chmod 644
```

## Concept deep-dive

### Reading `ls -l`

```
-rw-r--r-- 1 dzgeek staff 1024 Apr 16 10:00 notes.md
```

| Field          | Value                | Meaning                                                |
|----------------|----------------------|--------------------------------------------------------|
| type           | `-`                  | regular file (`d`=dir, `l`=symlink, `c`/`b`=device)    |
| perms          | `rw-r--r--`          | user=rw, group=r, other=r                              |
| link count     | `1`                  | hardlink count (always 1 for files; ≥ 2 for dirs)      |
| owner          | `dzgeek`             | user                                                   |
| group          | `staff`              | group                                                  |
| size           | `1024`               | bytes                                                  |
| mtime          | `Apr 16 10:00`       | last modification                                      |
| name           | `notes.md`           |                                                        |

### Permission bits, file vs. directory

The same nine bits mean different things on files vs. directories:

| Bit | On a file              | On a directory                                  |
|-----|------------------------|-------------------------------------------------|
| `r` | read contents          | list entries (`ls`)                             |
| `w` | modify contents        | create/rename/delete entries inside             |
| `x` | execute as program     | traverse into (`cd`, access files within)       |

A directory you have `r` but not `x` on lets you `ls` but not open any file inside. A directory you have `x` but not `r` on lets you access files by exact name but not list. Both are uncommon — you usually want all three together (`755` or `750`).

### Octal form

Each class is three bits → one octal digit:

```
rwx = 7    rw- = 6    r-x = 5    r-- = 4    --x = 1    --- = 0
```

So `rw-r--r--` = `644`, `rwxr-xr-x` = `755`, `rwx------` = `700`.

Common modes:

| Mode | Use                                                      |
|------|----------------------------------------------------------|
| 600  | private file (SSH keys, mail spool, secrets)             |
| 644  | normal file (readable by all, writable by owner)         |
| 700  | private directory (`~/.ssh`)                             |
| 750  | shared with group, hidden from others                    |
| 755  | normal directory or executable script                    |
| 775  | shared with group, world-readable                        |
| 777  | world-writable — almost always wrong                     |

### Changing permissions

```bash
chmod 600 id_rsa            # octal: explicit
chmod u+x run.sh            # symbolic: add execute for user
chmod go-w notes.md         # remove write from group and other
chmod -R 755 public/        # recursive — be careful
chmod a=r notes.md          # all classes equal r--
```

Symbolic form: `[ugoa][+-=][rwx]` — e.g. `g+w` (give group write), `a=rx` (everyone read+execute, nothing else).

### Changing ownership

```bash
sudo chown alice file              # change user only
sudo chown alice:devs file         # user and group
sudo chown -R you:you ~/dir        # recursive
sudo chgrp devs file               # group only
```

You usually need root to change ownership. You can change *group* of a file you own, if you're a member of the new group.

### Special bits

- **Setuid** (`s` in user-x slot): program runs with the privileges of its **owner**, not the caller. Used by `/usr/bin/passwd` to update `/etc/shadow`. A massive security responsibility — never set it on something you wrote without thinking very carefully.
- **Setgid on a directory** (`s` in group-x slot): files created inside inherit the directory's group. Useful for shared project directories.
- **Sticky bit** (`t` in other-x slot, on a directory): only the file's owner can delete it. Used on `/tmp` so users can write but not delete each other's files.

```bash
chmod u+s binary    # setuid (rarely correct outside system tools)
chmod g+s shared/   # setgid on directory
chmod +t /tmp       # sticky
```

### `sudo`

```bash
sudo apt update           # one elevated command
sudo -i                   # interactive root shell (prefer not to)
sudo -u alice ls /home/alice    # run as another user
```

`sudo` reads `/etc/sudoers` (edit with `visudo`). Best practice: **least privilege** — grant specific commands, not blanket root. Group-based access (e.g. `wheel`, `sudo` group) is the default.

## Why these design choices

- **Three classes, three actions.** Coarse but easy to reason about. Linux added richer ACLs (`getfacl`/`setfacl`) and SELinux/AppArmor for finer control; for 95% of files the basic mode bits are enough.
- **Octal as a first-class API.** Compact, scriptable, and unambiguous. Symbolic mode is for humans; octal is for scripts and Dockerfiles.
- **Setuid as a privilege escalation tool.** Lets ordinary users perform privileged operations *narrowly* (change their password) without granting them full root. The cost is a class of vulnerabilities — every setuid binary is a security audit unto itself.
- **Sticky bit on `/tmp`.** Lets all users write while preventing them from deleting each other's files. The right shape for a shared scratchpad.
- **`sudo` over `su`.** `sudo` runs *one* command and logs it; `su` gives a full root shell. Audit trails and habit-forming.
- **When you'd choose differently.** Multi-user systems with complex role-based access reach for **POSIX ACLs**. Containers often run as a single non-root user, making mode bits trivial. SELinux on RHEL/Fedora layers mandatory access control on top.

## Production-quality code

### Example 1 — Lock down an SSH directory

```bash
#!/usr/bin/env bash
set -euo pipefail

ssh_dir="$HOME/.ssh"
[[ -d "$ssh_dir" ]] || { echo "no ~/.ssh" >&2; exit 1; }

chmod 700 "$ssh_dir"
find "$ssh_dir" -maxdepth 1 -type f -name "id_*" ! -name "*.pub" \
    -exec chmod 600 {} +
find "$ssh_dir" -maxdepth 1 -type f -name "*.pub" \
    -exec chmod 644 {} +
chmod 600 "$ssh_dir/authorized_keys" 2>/dev/null || true
chmod 600 "$ssh_dir/known_hosts" 2>/dev/null || true
chmod 600 "$ssh_dir/config" 2>/dev/null || true

ls -l "$ssh_dir"
```

SSH refuses to use private keys with group/other readable. The `find -exec` pattern targets exactly the right files without globbing surprises.

### Example 2 — A shared project directory

```bash
sudo addgroup devs
sudo usermod -aG devs alice
sudo usermod -aG devs bob

sudo mkdir -p /srv/projects/acme
sudo chown :devs /srv/projects/acme
sudo chmod 2770 /srv/projects/acme    # 2 = setgid; new files inherit 'devs'

# Now: alice and bob can both read/write/cd; new files come out group=devs
```

The leading `2` in `2770` sets the setgid bit. Without it, files Alice creates would belong to her primary group, locking Bob out.

## Security notes

- **`chmod 777` is a red flag.** Almost never the right answer. The few legitimate cases (intentionally world-writable scratch directories) want the sticky bit too: `chmod 1777`.
- **`chmod -R` traversal.** A `chmod -R 644 /var/www` makes every script un-executable. Use `find -type f -exec chmod 644 {} +` and `find -type d -exec chmod 755 {} +` to set files and directories separately.
- **Editing as root leaves files root-owned.** `sudo vim /etc/foo` is fine; `sudo cp foo ~/work` leaves `~/work/foo` owned by root and your editor can't save. Use `sudo chown $USER:$USER` when you intend the file to be yours.
- **Setuid binaries are a privilege boundary.** Don't write setuid scripts (most kernels ignore the bit on scripts anyway, on purpose). For elevation, use `sudo` or a small, audited C binary.
- **Permissions don't survive `git`.** Git tracks only the executable bit on files. Tooling like `setfacl`, ownership, and full mode bits need to be re-applied at deploy time.
- **The path matters too.** A file with `644` is unreachable if any parent directory is `700` and you're not the owner. `ls -ld` each component to debug.

## Performance notes

- `chmod`/`chown` are O(1) per file (a single `chmod`/`chown` syscall). On a tree, `-R` walks; for very large trees, parallelize with `xargs -P` or use `setfacl -R --set-file=`.
- Filesystem permission checks are cached in the kernel; checking permission on the same path twice is essentially free.
- POSIX ACLs (`setfacl`) add a modest overhead per check vs. plain mode bits, but enable cases plain modes can't express. Worth it where the alternative is `chmod 777`.

## Common mistakes

- **`chmod 777` to "fix" an access problem.** Symptom: the immediate problem goes away. Cause: papering over the actual permission/ownership mismatch. Fix: identify the user the process runs as and grant *minimal* required access.
- **Recursive chmod blows away executables.** Symptom: scripts under `/srv/www` stop running. Cause: `chmod -R 644` removed `x` from directories too. Fix: separate `find -type f` and `find -type d` invocations.
- **Editing root-owned files in your editor.** Symptom: editor refuses to save. Cause: not the owner. Fix: `sudoedit` (or `sudo -e`) — opens an editor as you, copies back as root.
- **SSH "permissions are too open" error.** Symptom: `ssh-add` or `ssh` refuses. Cause: `~/.ssh/id_*` is `644` instead of `600`. Fix: `chmod 600 ~/.ssh/id_*`.
- **Permission denied on a file you own.** Symptom: `cat ~/file` says no. Cause: a parent directory has `o-x`. Fix: `ls -ld` each ancestor; fix the right one.
- **Container runs as root.** Symptom: bind-mounted files end up root-owned. Cause: container's UID 0 = host's UID 0. Fix: run the container as a non-root UID matching your user.

## Practice

1. **Warm-up.** Translate `-rwxr-x---` to octal and the reverse: `750` to symbolic.
2. **Standard.** Make `~/bin/hello.sh` executable by you only; verify with `ls -l`.
3. **Bug hunt.** You `chmod 600 public.html` and the web server returns `403`. Why?
4. **Stretch.** Find every file under `./` with mode `777` and print the path.
5. **Stretch++.** Explain what happens when setuid is on a shell script vs. a compiled binary. Why do most kernels ignore setuid on scripts?

<details><summary>Show solutions</summary>

1. `750` ↔ `rwxr-x---`. The owner has full access, the group has read+execute, others have nothing.

```bash
mkdir -p ~/bin
echo '#!/usr/bin/env bash' > ~/bin/hello.sh
echo 'echo hi' >> ~/bin/hello.sh
chmod 700 ~/bin/hello.sh
ls -l ~/bin/hello.sh
```

3. The web server runs as a different user (e.g., `www-data`); with mode `600`, only your account can read the file. Set `644` (or `640` if owned by group `www-data`) to let it serve.

```bash
find . -type f -perm 777
```

5. Setuid on a compiled binary causes it to run with the owner's privileges — used by `passwd`, `ping`, etc. Setuid on a shell script *would* let any user run a privileged shell with controllable input (e.g., `IFS`, `PATH`); attackers can break the script's assumptions trivially. The kernel ignores setuid on scripts (look up the `noexec_setid` policy on Linux) — security-by-prevention.

</details>

## Quiz

1. `644` means:
    (a) `rw-r--r--` (b) `rwxr--r--` (c) `rwxrw-rw-` (d) `r--r--r--`
2. Execute bit on a directory allows:
    (a) running files in it (b) traversing into it (c) deleting it (d) listing its name
3. Which changes ownership?
    (a) `chmod` (b) `chown` (c) `chgrp` (d) both b and c
4. The `t` bit on `/tmp`:
    (a) blocks deletion unless you own the file (b) forces tab expansion (c) is a setuid (d) limits size
5. `chmod 777` on user-uploaded files is:
    (a) correct (b) safe (c) a security hole (d) required

**Short answer:**

6. What's the practical difference between `rwxrwxrwx` on a directory vs. on a file?
7. Why does SSH refuse world-readable private keys?

*Answers: 1-a, 2-b, 3-d, 4-a, 5-c.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-permissions — mini-project](mini-projects/03-permissions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Ten characters in `ls -l` carry the entire permission story.
- Octal = three bits per class: `r=4, w=2, x=1`.
- `x` on a directory means "traverse"; without it, files inside are unreachable by exact name.
- Least privilege is a habit. `chmod 777` is rarely the answer.
- Use `sudo` for narrow elevations; never write setuid shell scripts.

## Further reading

- `man chmod`, `man 5 acl` — reference and extended ACLs.
- *The Linux Programming Interface* by Michael Kerrisk, chapters 15 and 17.
- Next: [programs](04-programs.md).
