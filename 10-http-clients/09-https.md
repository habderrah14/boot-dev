# Chapter 09 — HTTPS

> "HTTPS is HTTP inside a TLS tunnel. It provides encryption (nobody can read), integrity (nobody can tamper), and authentication (you're talking to who you think)."

## Learning objectives

By the end of this chapter you will be able to:

- Describe the TLS 1.3 handshake at a high level and explain what each step achieves.
- Explain what X.509 certificates do and how the trust chain works.
- Recognize common HTTPS errors and know how to fix each one.
- Set up certificate management for production (Let's Encrypt / ACME).
- Explain certificate pinning, mTLS, and when to use each.

## Prerequisites & recap

- [Why HTTP](01-why-http.md) — you know HTTPS is HTTP + TLS, and that production traffic must be encrypted.

## The simple version

Without HTTPS, every HTTP request travels as plaintext. Any device on the network path — your Wi-Fi router, your ISP, a corporate proxy — can read your passwords, tokens, and data. HTTPS wraps the entire HTTP conversation inside a TLS (Transport Layer Security) tunnel that provides three guarantees:

1. **Encryption** — the content is scrambled; only the client and server can read it.
2. **Integrity** — if anyone modifies the data in transit, both sides detect it.
3. **Authentication** — the server proves its identity via a certificate signed by a trusted authority.

The cost? A one-time handshake that adds ~1 round trip before data flows. With TLS 1.3, this cost is minimal. There is no legitimate reason to serve an API over plain HTTP in production.

## In plain terms (newbie lane)

This chapter is really about **HTTPS**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Client                                 Server
    │                                       │
    │──── ClientHello ─────────────────────▶│
    │     (ciphers, SNI hostname,           │
    │      key share)                       │
    │                                       │
    │◀─── ServerHello + Cert Chain ────────│
    │     (chosen cipher, server's          │
    │      certificate chain, key share)    │
    │                                       │
    │     Client validates:                 │
    │     ✓ cert chain → trusted root CA    │
    │     ✓ hostname matches cert SAN       │
    │     ✓ cert not expired                │
    │     ✓ cert not revoked                │
    │                                       │
    │     Both derive session key           │
    │     from key shares                   │
    │                                       │
    │════ Encrypted HTTP traffic ══════════│
    │     (all requests and responses       │
    │      are now encrypted)               │
    │                                       │
```

*TLS 1.3 completes in ~1 round trip. After that, all HTTP traffic is encrypted. The client verifies the server's identity before sending any application data.*

## Concept deep-dive

### Why HTTPS is non-negotiable

Every argument for skipping HTTPS in production has been debunked:

- "It's slow" — TLS 1.3 adds one round trip. Session resumption (0-RTT) makes subsequent connections even faster.
- "It's only needed for sensitive data" — without HTTPS, session cookies, tokens, and every header travel in plaintext. An attacker on the same Wi-Fi can hijack sessions.
- "It's expensive" — Let's Encrypt provides free certificates. CPU cost for encryption is negligible on modern hardware.

Modern browsers flag plain HTTP pages as "Not Secure." Google ranks HTTPS sites higher. HTTP/2 and HTTP/3 require TLS. The web has moved on.

### X.509 certificates

A server's certificate is a signed document that binds a hostname to a public key. It contains:

- **Subject** — who the cert belongs to (the hostname).
- **Subject Alternative Name (SAN)** — the hostnames and IPs the cert is valid for.
- **Public key** — used during the handshake to establish encryption.
- **Validity period** — not-before and not-after dates.
- **Issuer** — the Certificate Authority (CA) that signed it.
- **Signature** — the CA's cryptographic signature proving authenticity.

### The trust chain

Trust works through a chain of signatures:

```
  Root CA cert (built into your OS/browser)
    │
    └── signs → Intermediate CA cert
                   │
                   └── signs → Server's cert (example.com)
```

Your browser/Node runtime ships with a bundle of ~100 trusted root CA certificates. When a server presents its cert, the client walks the chain:

1. Is the server cert signed by an intermediate CA?
2. Is that intermediate signed by a trusted root?
3. If yes to both, the server is who it claims to be.

Why the intermediate CA? Root CA private keys are kept offline in vaults. Intermediate CAs handle daily signing. If an intermediate is compromised, only it needs to be revoked, not the root.

### The TLS 1.3 handshake (simplified)

1. **ClientHello** — the client sends supported ciphers, the SNI hostname, and a key share.
2. **ServerHello** — the server picks a cipher, sends its certificate chain and its own key share.
3. **Client validation** — the client verifies the cert chain against trusted roots, checks the hostname against the cert's SAN, checks expiry, checks revocation.
4. **Key derivation** — both sides combine their key shares to derive a shared session key.
5. **Encrypted traffic** — all subsequent HTTP traffic is encrypted with the session key.

All of this happens in ~1 round trip with TLS 1.3. TLS 1.2 took 2 round trips. Session resumption (0-RTT) can skip the handshake entirely for repeat connections.

### Hostname verification

The cert's SAN (Subject Alternative Name) must include the hostname the client connected to. `*.example.com` covers `api.example.com` but not `example.com` itself (and not `sub.api.example.com`). If the hostname doesn't match, the client aborts with a hostname-mismatch error.

### Common HTTPS errors

| Error | Meaning | Fix |
|-------|---------|-----|
| `CERT_HAS_EXPIRED` | Certificate's validity period has passed | Renew the certificate |
| `SELF_SIGNED_CERT_IN_CHAIN` | Cert not signed by a trusted CA | Use a CA-signed cert (Let's Encrypt) or add the CA to your trust store for internal certs |
| `CERT_NOT_YET_VALID` | Certificate's not-before date is in the future | Fix system clock, or wait for the cert's validity start |
| `ERR_SSL_PROTOCOL_ERROR` | Cipher mismatch or protocol incompatibility | Update client or server to support modern ciphers |
| `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | Missing intermediate cert in the chain | Configure the server to send the full chain, not just the leaf cert |

### Let's Encrypt and ACME

Let's Encrypt provides free, automated, 90-day certificates via the ACME protocol. Setup once, and it auto-renews:

- **Certbot** — standalone CLI. `certbot certonly --nginx -d example.com`.
- **Caddy** — auto-HTTPS built in. Just specify the domain.
- **cert-manager** — Kubernetes-native. Manages certificates as custom resources.

Why 90-day certs? Short validity reduces the window of compromise if a key is stolen. Automation makes short lifetimes practical.

### Certificate pinning

Pinning means hard-coding the expected certificate (or its hash) in your client. Even if a CA is compromised and issues a fraudulent cert for your domain, the pinned client rejects it.

The trade-off is operational: if you rotate your cert and forget to update the pin, your client is bricked. This is why pinning is mainly used in mobile apps and high-security environments, not in general web clients.

### Client trust store in Node

Node bundles its own CA root store. To trust an additional CA (e.g., an internal corporate CA):

```bash
NODE_EXTRA_CA_CERTS=/path/to/internal-ca.pem node app.js
```

This is the correct way to handle internal CAs. Never disable certificate verification.

### mTLS (Mutual TLS)

In standard TLS, only the server presents a certificate. In mTLS, the client also presents one. This proves the client's identity to the server — useful for service-to-service communication where both sides need to authenticate.

mTLS is common in:

- Microservice meshes (Istio, Linkerd).
- Financial APIs with strict compliance requirements.
- Zero-trust network architectures.

## Why these design choices

| Decision | Why | Alternative | When you'd pick differently |
|---|---|---|---|
| CA-based trust | Scales to billions of domains; any browser trusts any valid cert | Self-signed certs, TOFU (trust on first use) | Internal services where you control both client and server |
| Short-lived certs (90 days) | Limits exposure window if a key is compromised | Long-lived certs (1-2 years) | When automation isn't possible (rare) |
| SNI for hostname routing | Multiple domains can share one IP address | One IP per domain | You wouldn't — IPv4 addresses are scarce |
| Certificate pinning | Defends against CA compromise | Trust the CA system entirely | When CA compromise is an accepted risk (most web apps) |

## Production-quality code

```ts
import * as tls from "node:tls";

interface CertInfo {
  hostname: string;
  issuer: string;
  validFrom: string;
  validTo: string;
  daysUntilExpiry: number;
  serialNumber: string;
}

function checkCertificate(hostname: string, port = 443): Promise<CertInfo> {
  return new Promise((resolve, reject) => {
    const socket = tls.connect({ host: hostname, port, servername: hostname }, () => {
      const cert = socket.getPeerCertificate();

      if (!cert || !cert.valid_to) {
        socket.destroy();
        return reject(new Error(`No certificate returned for ${hostname}`));
      }

      const validTo = new Date(cert.valid_to);
      const now = new Date();
      const daysUntilExpiry = Math.floor(
        (validTo.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
      );

      const info: CertInfo = {
        hostname,
        issuer: cert.issuer?.O ?? "unknown",
        validFrom: cert.valid_from,
        validTo: cert.valid_to,
        daysUntilExpiry,
        serialNumber: cert.serialNumber,
      };

      socket.destroy();
      resolve(info);
    });

    socket.on("error", (err) => reject(err));
  });
}

async function main() {
  const hosts = process.argv.slice(2);
  if (hosts.length === 0) {
    console.error("Usage: npx tsx 09-https.ts <hostname> [hostname2] ...");
    process.exit(1);
  }

  for (const host of hosts) {
    try {
      const info = await checkCertificate(host);
      const status = info.daysUntilExpiry < 14 ? "⚠ EXPIRING SOON" : "✓ OK";
      console.log(
        `${host}: ${status} (expires in ${info.daysUntilExpiry} days, ` +
        `issued by ${info.issuer})`,
      );
    } catch (err) {
      console.error(`${host}: ERROR — ${(err as Error).message}`);
    }
  }
}

main();
```

## Security notes

- **Never disable certificate verification in production.** Setting `rejectUnauthorized: false` or `NODE_TLS_REJECT_UNAUTHORIZED=0` makes your connection vulnerable to man-in-the-middle attacks. The encryption is meaningless if you don't verify who you're encrypting to.
- **Self-signed certs in tests can mask real problems.** Use `mkcert` to generate locally-trusted development certificates instead of disabling verification.
- **Certificate Transparency (CT)** — all publicly trusted CAs must log issued certificates to public CT logs. You can monitor these logs to detect unauthorized certificates for your domain.
- **Revocation checking** — if a private key is compromised, the cert should be revoked. OCSP stapling lets the server prove its cert hasn't been revoked without the client contacting the CA separately.

## Performance notes

- **TLS 1.3 handshake: ~1 RTT.** TLS 1.2 was ~2 RTT. Session resumption (0-RTT) skips the handshake entirely for repeat connections, at the cost of replay vulnerability (only safe for idempotent requests).
- **Encryption overhead** — modern CPUs have AES-NI hardware acceleration. The CPU cost of encryption/decryption is negligible compared to network latency.
- **Connection reuse** is critical. The TLS handshake is the expensive part; once established, the connection can carry many HTTP requests. HTTP/2 multiplexing over a single TLS connection amortizes the handshake cost across all requests.
- **OCSP stapling** — without it, the client makes a separate request to the CA's OCSP responder for every new connection, adding latency. With stapling, the server includes the OCSP response in the handshake.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | "Certificate expired — 3 AM production outage" | Renewal wasn't automated or the automation silently failed | Use Let's Encrypt + certbot/Caddy with monitoring. Alert when < 14 days remain |
| 2 | "`rejectUnauthorized: false` in production code" | Developer disabled verification during testing and forgot to remove it | Never commit this setting. Use `mkcert` for local dev instead |
| 3 | "Browser shows 'Not Secure' despite having a cert" | Mixed content — HTTPS page loading HTTP resources (images, scripts) | Ensure all resources are loaded over HTTPS |
| 4 | "Server clock is wrong — cert appears expired or not yet valid" | System time drifted; cert validity dates fail comparison | Sync system clock with NTP (`ntpd` or `chronyd`) |
| 5 | "`UNABLE_TO_VERIFY_LEAF_SIGNATURE`" | Server sends only the leaf cert, not the full chain | Configure the server to send the intermediate CA cert(s) in the chain |

## Practice

### Warm-up

Use OpenSSL to print the certificate expiry date for `example.com`.

<details><summary>Show solution</summary>

```bash
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -enddate
# notAfter=May 12 23:59:59 2026 GMT
```

</details>

### Standard

Use Node's `tls` module to connect to a host and print the peer certificate's subject, issuer, and validity dates.

<details><summary>Show solution</summary>

```ts
import * as tls from "node:tls";

const socket = tls.connect(
  { host: "example.com", port: 443, servername: "example.com" },
  () => {
    const cert = socket.getPeerCertificate();
    console.log("Subject:", cert.subject);
    console.log("Issuer:", cert.issuer);
    console.log("Valid from:", cert.valid_from);
    console.log("Valid to:", cert.valid_to);
    socket.destroy();
  },
);
```

</details>

### Bug hunt

A user reports: "The browser shows NET::ERR_CERT_AUTHORITY_INVALID for our site, but the cert was just issued." What's likely wrong?

<details><summary>Show solution</summary>

The most likely cause is that the server is sending only the leaf certificate, not the full chain. The browser can't verify the cert because it doesn't have the intermediate CA cert. Fix: configure the server to include the intermediate certificate(s) in the chain. This is a common misconfiguration with Nginx, Apache, and cloud load balancers.

Another possibility: the cert was issued by a CA that isn't in the browser's trust store (e.g., an internal CA or a very new CA).

</details>

### Stretch

Set up local development HTTPS with `mkcert`. Generate a certificate for `localhost` and use it with a simple Node HTTPS server.

<details><summary>Show solution</summary>

```bash
# Install mkcert and create a local CA
mkcert -install
mkcert localhost 127.0.0.1 ::1
# Creates localhost+2.pem and localhost+2-key.pem
```

```ts
import * as https from "node:https";
import * as fs from "node:fs";

const server = https.createServer(
  {
    cert: fs.readFileSync("localhost+2.pem"),
    key: fs.readFileSync("localhost+2-key.pem"),
  },
  (req, res) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("Hello over HTTPS!\n");
  },
);

server.listen(3443, () => console.log("https://localhost:3443"));
```

The browser trusts this cert because `mkcert -install` added its root CA to the system trust store.

</details>

### Stretch++

Look up Certificate Transparency logs for a domain you own (or `example.com`) using `https://crt.sh`. Explain what CT logs are and why they matter.

<details><summary>Show solution</summary>

Visit `https://crt.sh/?q=example.com` to see all certificates ever issued for `example.com`.

Certificate Transparency (CT) is a public logging system where CAs must record every certificate they issue. This serves two purposes:

1. **Detection** — domain owners can monitor CT logs to detect unauthorized certificates issued for their domains (e.g., by a compromised CA).
2. **Accountability** — browsers require certificates to be logged in CT. A cert without a CT entry (SCT) is rejected by Chrome and Safari.

CT doesn't prevent mis-issuance — it makes it detectable, which is a strong deterrent.

</details>

## Quiz

1. HTTPS provides:
   (a) Only encryption  (b) Encryption, integrity, and authentication  (c) Only authentication  (d) Only integrity

2. A certificate's trust is validated via:
   (a) The CA chain back to a trusted root  (b) DNS  (c) IP address  (d) Random verification

3. Hostname verification uses:
   (a) CN only (deprecated)  (b) Subject Alternative Name (SAN)  (c) A header  (d) A cookie

4. TLS 1.3 handshake completes in approximately:
   (a) 2 round trips  (b) 1 round trip  (c) 3 round trips  (d) 0 round trips (with resumption, for repeat connections)

5. Let's Encrypt / ACME provides:
   (a) Paid certificates  (b) Free automated certificates  (c) Browser-only certificates  (d) Key escrow

**Short answer:**

6. Why is disabling TLS certificate verification dangerous, even in staging environments?
7. Give one reason why HTTP/2 and HTTP/3 require TLS.

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b. 6 — Disabling verification means you're encrypting traffic to an unknown party. A man-in-the-middle attacker can present any certificate and intercept all traffic, including tokens and credentials. In staging, this trains developers to ignore TLS errors and risks leaking staging credentials. 7 — Requiring TLS prevents middleboxes (proxies, firewalls) from inspecting and modifying HTTP/2 binary frames, which would break the protocol. It also ensures a baseline of security for all connections.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-https — mini-project](mini-projects/09-https-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- HTTPS = HTTP over TLS. It provides encryption, integrity, and server authentication in ~1 round trip.
- X.509 certificates bind hostnames to public keys via a trust chain back to a root CA.
- Automate certificate renewal with Let's Encrypt/ACME — never let certs expire manually.
- Never disable certificate verification in production. Use `mkcert` for local development instead.

## Further reading

- *Bulletproof SSL and TLS*, Ivan Ristić — the comprehensive guide to TLS deployment.
- Let's Encrypt documentation — setup guides for every server and platform.
- Next: [Runtime Validation](10-runtime-validation.md).
