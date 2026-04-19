# Mini-project — 02-containers

_Companion chapter:_ [`02-containers.md`](../02-containers.md)

**Goal.** Run a Node.js script inside a container without installing Node locally.

**Acceptance criteria:**

- Create a simple `index.js` that starts an HTTP server on port 3000.
- Use `docker run` with the `node:20` image, mount your code, and start the server.
- Verify with `curl localhost:3000` from the host.
- No local Node.js installation used.

**Hints:**

- `-v "$PWD":/app -w /app` mounts your current directory and sets the working directory.
- `-p 3000:3000` publishes the port.
- The command is `node index.js`.

**Stretch:** Add a `package.json` with a dependency. Run `npm install` inside the container first (using a separate `docker run`), then start the server.
