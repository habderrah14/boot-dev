#!/usr/bin/env python3
"""Insert ## Where this idea reappears before ## Chapter summary when missing."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name))

SECTION = """## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
"""


def links_for_module(mod: str) -> str:
    m = {
        "01-python": """  - [Variables and types in JavaScript](../08-js/01-variables.md) — the same binding model with different syntax.
  - [Built-in collections → abstract DSA](../06-dsa/06-data-structures-intro.md) — from Python lists to asymptotic cost.""",
        "02-linux": """  - [Python fundamentals](../01-python/README.md) — most tooling you run lives in userspace you configure here.
  - [Containers under the hood](../14-docker/02-containers.md) — namespaces build on the kernel concepts from this module.""",
        "03-git": """  - [GitHub collaboration](../03-git/10-github.md) — social layer on top of commits you learned locally.
  - [CI/CD and Docker](../14-docker/README.md) — where clean Git history meets reproducible builds.""",
        "04-oop": """  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.""",
        "05-fp": """  - [JavaScript functions as values](../08-js/03-functions.md) — first-class functions everywhere on the web.
  - [Runtime validation with schemas](../10-http-clients/10-runtime-validation.md) — sum types meet JSON boundaries.""",
        "06-dsa": """  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.""",
        "07-c-memory": """  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.""",
        "08-js": """  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.""",
        "09-ts": """  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.""",
        "10-http-clients": """  - [HTTP servers](../12-http-servers/01-servers.md) — the other side of the same protocol.
  - [Webhooks and callbacks](../12-http-servers/09-webhooks.md) — HTTP used as an event bus.""",
        "11-sql": """  - [Server-side persistence patterns](../12-http-servers/06-storage.md) — how applications wrap SQL safely.
  - [Normalization vs delivery](../13-file-cdn/01-file-storage.md) — metadata in SQL, bytes in object storage.""",
        "12-http-servers": """  - [HTTP clients](../10-http-clients/01-why-http.md) — symmetric skills for debugging full stacks.
  - [Safe SQL from application code](../11-sql/04-crud.md) — parameters, transactions, and errors behind your routes.""",
        "13-file-cdn": """  - [SQL metadata patterns](../11-sql/README.md) — storing pointers, not blobs.
  - [HTTP cache semantics](../10-http-clients/05-headers.md) — `Cache-Control` and friends behind CDN behavior.""",
        "14-docker": """  - [Linux processes and packages](../02-linux/04-programs.md) — what PID 1 and namespaces build on.
  - [Pub/Sub services](../15-pubsub/README.md) — how containers host brokers and workers.""",
        "15-pubsub": """  - [HTTP webhooks](../12-http-servers/09-webhooks.md) — synchronous cousin to async messaging.
  - [JSON and serialization](../10-http-clients/06-json.md) — message payloads cross language boundaries.""",
        "16-job-hunt": """  - [Integration projects (cross-module builds)](../appendix-projects/README.md) — ship evidence that stitches HTTP, SQL, Docker, and messaging.
  - [System design primer](../appendix-system-design.md) — vocabulary for scaling conversations post-modules.""",
    }
    return m.get(mod, """  - [Backend path overview](../README.md) — how modules connect.
  - [Glossary](../../GLOSSARY.md) — shared vocabulary across languages.""")


def main() -> None:
    for mod_path in MODULES:
        mod = mod_path.name
        block = SECTION + links_for_module(mod) + "\n\n"
        for chap in sorted(mod_path.glob("[0-9][0-9]-*.md")):
            raw = chap.read_text(encoding="utf-8")
            if "## Where this idea reappears" in raw:
                continue
            idx = raw.find("\n## Chapter summary")
            if idx == -1:
                print(f"No Chapter summary: {chap}")
                continue
            new = raw[:idx] + "\n\n" + block + raw[idx:]
            chap.write_text(new, encoding="utf-8")
            print(f"Injected cross-links -> {chap.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
