# Mini-project — 04-enums

_Companion chapter:_ [`04-enums.md`](../04-enums.md)

**Goal.** Implement a tiny Unix-style permission system with a `Perm` bitmask type.

**Acceptance criteria:**

- Functions: `perm_grant`, `perm_revoke`, `perm_has`, `perm_print`.
- `perm_print` outputs `rwx`-style strings (e.g., `rw-` for read+write, no exec).
- A `main` that demonstrates granting, revoking, and testing permissions.
- Compiles cleanly with `-Wall -Wextra -Wswitch-enum -std=c17`.

**Hints:**

- Use `unsigned int` for the permission type to avoid signed-arithmetic surprises.
- `& ~flag` clears a bit; `| flag` sets a bit; `& flag` tests a bit.

**Stretch:** Add `perm_from_string` that parses `"rwx"` / `"r--"` / `"---"` strings into a `Perm` value.
