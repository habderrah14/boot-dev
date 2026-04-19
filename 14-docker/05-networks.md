# Chapter 05 — Networks

> Docker networking is mostly invisible when it works, and baffling when it doesn't. Learn the three default networks and you'll troubleshoot most issues in one command.

## Learning objectives

- Distinguish bridge, host, and none networks.
- Create user-defined networks.
- Understand container DNS.
- Publish ports correctly.

## Prerequisites & recap

- [Containers](02-containers.md), [Compose](04-execute.md).

## Concept deep-dive

### Default drivers

- **bridge** — default. Each container gets a veth pair into a Linux bridge. Containers in the same user-defined bridge can reach each other by name.
- **host** — container shares the host's network stack (Linux only). No isolation, no port mapping — the container's port is the host's port.
- **none** — no networking. The container has `lo` and nothing else.

### Default bridge vs. user-defined bridge

The default `bridge` network is legacy; it doesn't give you DNS-based container discovery. Always create a user-defined bridge (or use Compose, which does this for you).

```bash
docker network create myapp
docker run -d --name db --network myapp postgres:16
docker run --rm --network myapp alpine ping -c 1 db
```

`db` resolves via Docker's internal DNS.

### Compose networks

Compose creates a dedicated network per project automatically. All services can reach each other by service name.

### Publishing ports

`-p host:container` opens the host-side port via a `docker-proxy` process or iptables DNAT rules. Not needed for intra-container traffic.

Common patterns:

```bash
-p 8080:80           # host 8080 → container 80
-p 127.0.0.1:8080:80 # only loopback (more secure dev)
-p 80                # random host port → 80 (good for tests)
```

### Service-to-service traffic

Don't route traffic from your API to your DB through `localhost:5432`. Use the container name (`db:5432`) so the DNS-based resolution works and doesn't require host port publishing.

### DNS

Docker runs an internal DNS server at `127.0.0.11` inside containers. `/etc/resolv.conf` points at it. It resolves container/service names.

### Troubleshooting

```bash
docker network ls
docker network inspect myapp          # list connected containers, IPs
docker exec -it api nslookup db       # inside the network
docker exec -it api wget -O- http://db:5432
```

### Network policies (Compose)

Separate services into networks that can't see each other:

```yaml
services:
  api:
    networks: [frontend, backend]
  web:
    networks: [frontend]
  db:
    networks: [backend]
networks:
  frontend:
  backend:
```

`web` can't reach `db` directly.

### IPv6, macvlan, overlay

Advanced. `macvlan` gives containers real LAN IPs; `overlay` (Swarm/k8s) spans multi-host. Rarely needed for small apps.

## Worked examples

### Example 1 — User-defined bridge

```bash
docker network create myapp
docker run -d --name db --network myapp -e POSTGRES_PASSWORD=pw postgres:16
docker run --rm --network myapp postgres:16 psql "postgres://postgres:pw@db:5432/postgres" -c "SELECT 1"
```

### Example 2 — Host networking

```bash
docker run --rm --network host nginx
# nginx is reachable at http://localhost:80 directly; no -p needed.
```

Linux only; Docker Desktop fakes this with limitations.

## Diagrams

```mermaid
flowchart LR
  api --(svc DNS)--> db
  host --(-p 3000:3000)--> api
```

*Caption: Trace the flow (data/time/money) through this figure before reading further.*

## Real-world incidents (postmortem sketches)

| Incident | Symptom | Root cause | Prevention |
|----------|---------|------------|------------|
| **Loopback confusion** | Healthcheck `curl http://localhost:3000` passes on host, fails in CI | Script assumed host network; inside bridge network `localhost` is the container itself | Hit `http://api:3000` or use internal DNS name |
| **Shadow network** | Two stacks, same `COMPOSE_PROJECT_NAME`, random 503s | Default bridge collisions + reused network namespace from aborted `down` | Unique project names per repo; `docker compose down` in CI teardown |
| **Over-published DB** | Security audit flags Postgres on `0.0.0.0:5432` | `- "5432:5432"` left in `docker-compose.yml` committed to prod profile | Split `compose.prod.yaml` without host ports; DB reachable only on internal network |

## Common pitfalls & gotchas

- Using `localhost` inside a container to reach another container — loopback is per-container.
- Relying on the default bridge's lack of DNS.
- Exposing 0.0.0.0 on a port meant for internal-only.
- Two Compose projects claiming the same ports.

## Exercises

1. Warm-up. `docker network ls`; note the defaults.
2. Standard. Create a user network; run two containers; ping one from the other by name.
3. Bug hunt. Why does `curl http://db:5432` from your API container fail when they're on different networks?
4. Stretch. Split API/DB into two networks via Compose; verify `web` can't hit `db`.
5. Stretch++. Use `--network host` on Linux to run an app without `-p`.

## In plain terms (newbie lane)
If `Networks` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Default network driver:
    (a) host (b) bridge (c) overlay (d) none
2. DNS between containers works on:
    (a) default bridge (b) user-defined bridge (c) none (d) host
3. `-p 3000` with no host port:
    (a) errors (b) picks a random host port (c) disables publishing (d) same as no flag
4. Host networking on Docker Desktop (Mac):
    (a) native (b) limited support (c) same as Linux (d) unsupported
5. DNS server inside container:
    (a) 127.0.0.1:53 (b) 127.0.0.11 (c) 8.8.8.8 (d) host's resolver

**Short answer:**

6. Why prefer user-defined bridges?
7. One reason to split Compose networks.

## Mini-project: Apply it

Full brief (goal, acceptance criteria, hints, stretch): [05-networks — mini-project](mini-projects/05-networks-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Linux processes and packages](../02-linux/04-programs.md) — what PID 1 and namespaces build on.
  - [Pub/Sub services](../15-pubsub/README.md) — how containers host brokers and workers.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Bridge (default), host, none.
- User-defined bridges provide DNS.
- Publish ports only when the host needs to reach them.

## Further reading

- Docker networking docs.
- Next: [Dockerfiles](06-dockerfiles.md).
