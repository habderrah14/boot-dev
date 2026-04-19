# Chapter 02 — Containers

> "A container is a normal Linux process that has been given its own view of the system. It's not a VM. It's not magic."

## Learning objectives

By the end of this chapter you will be able to:

- Define image, container, and layer and explain how they relate.
- Run, stop, remove, and inspect containers with confidence.
- Map ports, pass environment variables, and mount volumes.
- Use interactive shells and `docker exec` to explore running containers.

## Prerequisites & recap

- [Install](01-install.md) — Docker is installed and `hello-world` runs.

## The simple version

An **image** is a read-only blueprint — a snapshot of a filesystem with everything an application needs to run (code, runtime, libraries, config). A **container** is a running instance of that image with a thin writable layer on top. You can run many containers from one image, just like you can create many objects from one class.

When you type `docker run nginx`, Docker pulls the `nginx` image (if it doesn't have it locally), creates a container from it, and starts the process. The container has its own filesystem, network, and process tree — isolated from the host — but it shares the host's kernel. That's the key difference from a VM: no guest OS, no hypervisor, just kernel-level isolation.

## Visual flow

```
  Image (read-only layers)          Container(s)
  +---------------------------+
  | Layer 4: COPY app files   |
  | Layer 3: RUN npm install  |     +-- Container A --------+
  | Layer 2: RUN apt-get ...  | --> | thin writable layer    |
  | Layer 1: FROM ubuntu      |     | (container-specific)   |
  +---------------------------+     +------------------------+
         |
         |                           +-- Container B --------+
         +-------------------------> | thin writable layer    |
                                     | (different writes)     |
                                     +------------------------+

  Caption: Multiple containers share the same read-only image
  layers. Each gets its own writable layer on top.
```

## System diagram (Mermaid)

```mermaid
flowchart TB
  Host[Linux_host] --> Engine[Container_engine]
  Engine --> Image[Image_layers]
  Image --> Ctr[Running_container]
  Ctr --> Net[Network_namespace]
```

*How the host, image, and container namespaces relate.*

## Concept deep-dive

### Image vs. container

- **Image** — the read-only blueprint: a filesystem snapshot + metadata (default command, exposed ports, env vars). Built from a Dockerfile.
- **Container** — a running (or stopped) instance of an image with a thin writable layer on top. Ephemeral by default — when you remove it, the writable layer is gone.

An image is to a container what a class is to an instance.

### Layers

Images are stacks of read-only layers. Each Dockerfile instruction creates one layer. Docker shares layers between images — if two images both start `FROM ubuntu:22.04`, they share that base layer on disk. This saves storage and speeds up pulls.

```bash
docker image history node:20
```

### Running containers

```bash
docker run [OPTIONS] IMAGE [COMMAND...]
```

Essential flags:

| Flag | What it does |
|---|---|
| `-d` | Detach (run in background) |
| `--rm` | Auto-remove container on exit |
| `-it` | Interactive mode + allocate a TTY |
| `-p host:container` | Publish a port |
| `-e NAME=VALUE` | Set an environment variable |
| `-v host:container` | Bind mount or named volume |
| `--name myapp` | Give the container a human-friendly name |

### First containers

```bash
docker run --rm hello-world              # run and auto-clean
docker run --rm -it ubuntu bash          # interactive shell
docker run -d -p 8080:80 --name web nginx  # background nginx
docker logs web                          # see output
docker stop web && docker rm web         # clean up
```

### Listing and inspecting

```bash
docker ps                  # running containers
docker ps -a               # all (including stopped)
docker images              # local images
docker inspect web         # full JSON: state, env, mounts, network
docker inspect -f '{{.State.Status}}' web  # query specific fields
```

### Cleanup

```bash
docker rm $(docker ps -aq)                  # remove all stopped
docker rmi $(docker images -q -f dangling=true)  # remove dangling images
docker system prune                         # safe cleanup of unused
docker system prune -a --volumes            # aggressive cleanup
```

### Environment variables and ports

```bash
docker run -d \
  --name api \
  -e NODE_ENV=production \
  -e PORT=3000 \
  -p 3000:3000 \
  myapp:1.0
```

Port mapping is **host:container**. Inside the container, the app must bind to `0.0.0.0:3000` (not `127.0.0.1`) — the container's loopback is private.

### Interactive access

```bash
docker run --rm -it --entrypoint bash myapp:1.0   # override entrypoint
docker exec -it api sh                             # shell into running container
docker exec api cat /etc/os-release                # run a one-off command
```

`docker exec` is your go-to for "what's going on inside that container?"

## Why these design choices

**Why layers instead of a single filesystem?** Layers enable sharing and caching. If 10 images all use `node:20-alpine` as their base, that base is stored once on disk, not 10 times. When you rebuild an image, only changed layers are rebuilt — unchanged layers are cached. The trade-off: more complexity in the storage driver, and write-heavy workloads in the writable layer are slower than native filesystem writes.

**Why `--rm` by default for development?** Without `--rm`, every `docker run` leaves a stopped container behind. After a day of development, you have hundreds of stopped containers consuming disk. `--rm` cleans up automatically. The trade-off: you can't inspect a crashed container's filesystem after it exits (useful for debugging). Use `--rm` for throwaway runs; omit it when you need post-mortem inspection.

**Why bind `0.0.0.0` inside the container?** A container has its own network namespace with its own loopback. If your app binds `127.0.0.1:3000`, it's only reachable from inside the container — the host can't reach it even with `-p 3000:3000`. Binding `0.0.0.0` makes it reachable from any network interface, including the Docker bridge that connects to the host.

## Production-quality code

### Ephemeral Postgres for development

```bash
docker run -d \
  --name pg-dev \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=dev-only \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  --rm \
  postgres:16

# Connect from host
psql "postgresql://app:dev-only@localhost:5432/myapp"

# Stop (--rm removes it; pgdata volume persists)
docker stop pg-dev
```

### Run a build tool without installing it locally

```bash
docker run --rm \
  -v "$PWD":/app \
  -w /app \
  node:20 npm install
```

`-v "$PWD":/app` mounts your current directory. `-w /app` sets the working directory. No local Node installation needed.

### Inspect a container's environment

```bash
docker inspect api --format '{{range .Config.Env}}{{println .}}{{end}}'
```

## Security notes

- **Containers run as root by default.** This means a container escape vulnerability gives the attacker root on the host. Always use `USER` in your Dockerfile to drop privileges (covered in [Chapter 06](06-dockerfiles.md)).
- **Don't store secrets in environment variables visible via `docker inspect`.** Use Docker secrets, a mounted file, or a secret manager.
- **The writable layer is not isolated from the host's disk I/O.** A container writing heavily to its writable layer can degrade host performance.

## Performance notes

- **Container startup is fast** — typically <1 second for a pre-pulled image. It's just creating a process with namespaces, not booting an OS.
- **Port mapping has overhead.** Docker uses iptables (or `docker-proxy`) for port forwarding. For high-throughput, consider `--network host` on Linux (covered in [Chapter 05](05-networks.md)).
- **The writable layer uses a copy-on-write filesystem** (overlay2). First writes to a file copy it from the image layer — subsequent writes are native speed. For write-heavy workloads, use a volume instead.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Hundreds of stopped containers piling up | Forgetting `--rm` on throwaway runs | Use `--rm` for dev/test; periodically run `docker system prune` |
| 2 | Host can't reach the app despite `-p 3000:3000` | App binds `127.0.0.1:3000` inside the container | Bind to `0.0.0.0:3000` in the application config |
| 3 | Port mapping seems backwards | Confused by `host:container` order in `-p` | `-p 8080:80` maps host port 8080 to container port 80 |
| 4 | Data disappears when container restarts | State stored in the writable layer, not a volume | Mount a named volume for persistent data (see [Chapter 03](03-storage.md)) |
| 5 | `docker run node:20 npm test` fails with "file not found" | No code mounted into the container | Use `-v "$PWD":/app -w /app` to mount your project directory |

## Practice

### Warm-up

Run an interactive Ubuntu container. List the running processes inside it with `ps aux`. Exit.

<details><summary>Show solution</summary>

```bash
docker run --rm -it ubuntu bash
# Inside the container:
apt update && apt install -y procps
ps aux
# You'll see bash as PID 1 and ps itself
exit
```

</details>

### Standard

Start nginx on port 8080. Verify it works with `curl localhost:8080`. Stop and remove it.

<details><summary>Show solution</summary>

```bash
docker run -d -p 8080:80 --name web nginx
curl -s localhost:8080 | head -5
# Should show nginx welcome page HTML
docker stop web && docker rm web
```

</details>

### Bug hunt

You run `docker run -d -p 3000:3000 myapp` and try `curl localhost:3000` — but it says "connection refused." The app logs show it's running. What's wrong?

<details><summary>Show solution</summary>

The app is likely bound to `127.0.0.1:3000` inside the container. The container's loopback is private — the Docker bridge can't reach it. Fix: configure the app to bind `0.0.0.0:3000`. In Express: `app.listen(3000, "0.0.0.0")`. In many frameworks, setting `HOST=0.0.0.0` as an environment variable works.

</details>

### Stretch

Run Postgres in a container with a named volume. Connect from your host with `psql`. Create a table, stop the container, restart it, and verify the table still exists.

<details><summary>Show solution</summary>

```bash
docker run -d --name pg \
  -e POSTGRES_PASSWORD=test \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

psql -h localhost -U postgres -c "CREATE TABLE test (id INT);"
docker stop pg && docker start pg
psql -h localhost -U postgres -c "SELECT * FROM test;"
# Table exists — data persisted in the volume

docker stop pg && docker rm pg
```

</details>

### Stretch++

Use `docker exec` to install `curl` in a running nginx container, fetch `localhost` from inside the container, then remove the package. Observe that the changes exist only in this container's writable layer.

<details><summary>Show solution</summary>

```bash
docker run -d --name web nginx
docker exec web apt update
docker exec web apt install -y curl
docker exec web curl -s http://localhost
# Shows nginx welcome page
docker exec web apt remove -y curl
docker stop web && docker rm web
```

The package installation only affected this container's writable layer. A new container from the same image would not have curl installed.

</details>

## In plain terms (newbie lane)
If `Containers` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. How many containers can you run from one image?
   (a) 1:1 only  (b) Many — images are reusable blueprints  (c) N images : 1 container  (d) Unrelated concepts

2. What happens to the writable layer when you `docker rm` a container?
   (a) It persists  (b) It's deleted  (c) It merges into the image  (d) It's cached forever

3. What does `-p 8080:80` mean?
   (a) Host 80 → container 8080  (b) Host 8080 → container 80  (c) Same port on both  (d) Random mapping

4. What's the difference between `docker exec` and `docker run`?
   (a) Identical  (b) `exec` runs in an existing container; `run` creates a new one  (c) Reversed  (d) `exec` is deprecated

5. What does the `--rm` flag do?
   (a) Removes the image  (b) Removes the container on exit  (c) Removes volumes  (d) Dry run mode

**Short answer:**

6. Why are container images called "layered"?
7. Why should you never store important state in a container's writable layer?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — Each Dockerfile instruction creates a read-only filesystem layer. Layers stack on top of each other and are shared between images, saving disk space and speeding up pulls. 7 — The writable layer is ephemeral — it's deleted when the container is removed. Any data you need to keep must go in a volume or an external storage service.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-containers — mini-project](mini-projects/02-containers-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Linux processes and packages](../02-linux/04-programs.md) — what PID 1 and namespaces build on.
  - [Pub/Sub services](../15-pubsub/README.md) — how containers host brokers and workers.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- **Image = read-only blueprint; container = running instance** with its own writable layer, network, and process tree.
- **Layers are cached and shared** between images — this is why Docker is fast and disk-efficient.
- **Master `-p`, `-e`, `-v`, `--rm`, and `-it`** — these five flags cover 90% of daily Docker usage.

## Further reading

- Docker docs, *Docker overview* — images, containers, and the runtime.
- Docker docs, *docker run reference* — every flag explained.
- Julia Evans, *How containers work* — excellent visual explainer.
- Next: [Storage](03-storage.md).
