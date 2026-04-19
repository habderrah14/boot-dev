# Mini-project — 09-https

_Companion chapter:_ [`09-https.md`](../09-https.md)

**Goal.** Build `cert-check.ts` — a CLI that takes a list of hostnames and prints the days-until-expiry for each certificate. Suitable for running in CI to alert when certs are close to expiring.

**Acceptance criteria:**

- Accepts one or more hostnames as command-line arguments.
- For each hostname, prints: hostname, issuer, days until expiry, and a warning if < 14 days.
- Exits with code 1 if any certificate expires within 14 days.
- Handles connection errors gracefully (e.g., hostname doesn't resolve, port not open).
- Resolves all certificates in parallel with `Promise.allSettled`.

**Hints:**

- Use Node's `tls.connect()` to establish a TLS connection and `socket.getPeerCertificate()` to read cert info.
- Parse `valid_to` as a `Date` and compute days remaining.
- Use `Promise.allSettled` so one failing host doesn't prevent checking others.

**Stretch:** Add a `--json` flag that outputs results as JSON for programmatic consumption. Add a `--threshold <days>` flag to customize the warning threshold.
