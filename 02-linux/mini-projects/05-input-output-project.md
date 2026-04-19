# Mini-project — 05-input-output

_Companion chapter:_ [`05-input-output.md`](../05-input-output.md)

**Goal.** Build `logstats.sh` — given an Nginx access log path, print the top 10 IPs, top 10 URLs, and a count of HTTP 5xx responses. Pipes only — no programming languages.

**Acceptance criteria.**

- One arg: log file path; refuses if missing.
- Three sections in output, each with a clear header (`# Top 10 IPs`, etc.).
- Top 10 IPs: count + IP, sorted descending.
- Top 10 URLs: count + URL.
- 5xx count: a single integer.
- Runs against a 1-million-line log in under 5 seconds on commodity hardware.

**Hints.** Use `awk` to project specific fields. The Combined Log Format puts IP in `$1`, request line in `$5`-`$7`, status in `$9`. URL is `$7`. `grep -c '" 5..'` counts 5xx responses. Use `printf '%s\n' "# Top 10 IPs"` for headers.

**Stretch.** Add a `--since '2 hours ago'` flag using `awk` and `mktime` to filter by timestamp.
