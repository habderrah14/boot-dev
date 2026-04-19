#!/usr/bin/env python3
"""Insert a Mermaid diagram into chapters that lack one (modules 12–15 + targeted paths)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MERMAID_12 = """## System diagram (Mermaid)

```mermaid
flowchart LR
  Client[HTTP_client] --> Listener[Server_listen]
  Listener --> Router[Router]
  Router --> Handler[Handler]
  Handler --> Response[Response]
```

*High-level HTTP server data flow for this chapter’s topic.*
"""

MERMAID_13 = """## System diagram (Mermaid)

```mermaid
sequenceDiagram
  participant App as App_server
  participant API as Storage_API
  participant Store as Object_store
  App->>API: Request_or_presign
  API->>Store: Direct_or_signed_PUT
  Store-->>App: Confirm
```

*Typical control plane vs data plane when moving bytes to durable storage.*
"""

MERMAID_14 = """## System diagram (Mermaid)

```mermaid
flowchart TB
  Host[Linux_host] --> Engine[Container_engine]
  Engine --> Image[Image_layers]
  Image --> Ctr[Running_container]
  Ctr --> Net[Network_namespace]
```

*How the host, image, and container namespaces relate.*
"""

MERMAID_15 = """## System diagram (Mermaid)

```mermaid
flowchart LR
  Pub[Publisher] --> Broker[Message_broker]
  Broker --> Q1[Queue_or_topic]
  Q1 --> SubA[Subscriber_A]
  Q1 --> SubB[Subscriber_B]
```

*Decoupled delivery: publishers never address subscribers by name.*
"""

MERMAID_PROMISES = """## Promise lifecycle (Mermaid)

```mermaid
stateDiagram-v2
  [*] --> pending
  pending --> fulfilled: resolve
  pending --> rejected: reject
  fulfilled --> [*]
  rejected --> [*]
```

*A Promise settles exactly once.*
"""

MERMAID_EVENT_LOOP = """## Event loop sketch (Mermaid)

```mermaid
flowchart TB
  CallStack[Call_stack] --> WebAPI[Web_APIs_timers_IO]
  WebAPI --> TaskQueue[Microtask_then_macrotask_queues]
  TaskQueue --> CallStack
```

*Work finishes on the stack; async completions enqueue callbacks.*
"""

MERMAID_STACK_HEAP = """## Stack vs heap (Mermaid)

```mermaid
flowchart TB
  subgraph stackRegion [Call_stack_frames]
    F1[frame_main]
    F2[frame_callee]
  end
  subgraph heapRegion [Heap_objects]
    O1[malloc_block]
    O2[struct_on_heap]
  end
  F1 --> O1
  F2 --> O2
```

*Frames hold pointers; objects with dynamic lifetime live on the heap.*
"""

MERMAID_BFS_DFS = """## Graph traversal modes (Mermaid)

```mermaid
flowchart LR
  Start[Start_node] --> Q[Queue_BFS]
  Start --> S[Stack_DFS]
  Q --> Layer[Level_order_visit]
  S --> Deep[Depth_first_visit]
```

*BFS explores layers; DFS drills deep before siblings.*
"""

MERMAID_DNS = """## DNS resolution chain (Mermaid)

```mermaid
sequenceDiagram
  participant App as Application
  participant Stub as Stub_resolver
  participant Auth as Authoritative
  App->>Stub: Query_hostname
  Stub->>Auth: Optional_referral_chain
  Auth-->>Stub: RRset_A_AAAA_CNAME
  Stub-->>App: Cached_or_fresh_answer
```

*Stub resolver handles recursion; your HTTP client only sees the final address.*
"""

EXTRA = {
    ROOT / "08-js" / "12-promises.md": MERMAID_PROMISES,
    ROOT / "08-js" / "13-event-loop.md": MERMAID_EVENT_LOOP,
    ROOT / "07-c-memory" / "06-stack-and-heap.md": MERMAID_STACK_HEAP,
    ROOT / "06-dsa" / "15-bfs-and-dfs.md": MERMAID_BFS_DFS,
    ROOT / "10-http-clients" / "02-dns.md": MERMAID_DNS,
}


def inject_after_visual_flow(text: str, block: str) -> str:
    marker = "\n## Concept deep-dive"
    if "```mermaid" in text:
        return text
    idx = text.find(marker)
    if idx == -1:
        return text
    return text[:idx] + "\n" + block + text[idx:]


def main() -> None:
    for mod, block in (
        ("12-http-servers", MERMAID_12),
        ("13-file-cdn", MERMAID_13),
        ("14-docker", MERMAID_14),
        ("15-pubsub", MERMAID_15),
    ):
        base = ROOT / mod
        for chap in sorted(base.glob("[0-9][0-9]-*.md")):
            raw = chap.read_text(encoding="utf-8")
            new = inject_after_visual_flow(raw, block)
            if new != raw:
                chap.write_text(new, encoding="utf-8")
                print(f"Injected -> {chap.relative_to(ROOT)}")

    for path, block in EXTRA.items():
        if not path.exists():
            print(f"MISSING {path}")
            continue
        raw = path.read_text(encoding="utf-8")
        if "```mermaid" in raw:
            print(f"Skip (already has mermaid): {path.relative_to(ROOT)}")
            continue
        new = inject_after_visual_flow(raw, block)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            print(f"Injected -> {path.relative_to(ROOT)}")
        else:
            print(f"No anchor: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
