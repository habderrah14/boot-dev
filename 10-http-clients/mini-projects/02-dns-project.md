# Mini-project — 02-dns

_Companion chapter:_ [`02-dns.md`](../02-dns.md)

**Goal.** Build `dns-info.ts` — a CLI that takes a domain name and prints its A, AAAA, MX, and TXT records using `dns.promises`.

**Acceptance criteria:**

- Accepts a domain via `process.argv[2]`.
- Prints each record type on its own labeled line.
- Handles missing record types gracefully (prints "(none)" instead of crashing).
- Runs all lookups in parallel with `Promise.all` for speed.
- Prints a clear error if the domain doesn't exist (NXDOMAIN).

**Hints:**

- Wrap each `dns.resolveX()` call in a try/catch — not all domains have every record type.
- MX records have `priority` and `exchange` fields.
- TXT records come back as arrays of string arrays (joined segments).

**Stretch:** Add a `--json` flag that outputs the results as formatted JSON instead of human-readable text.
