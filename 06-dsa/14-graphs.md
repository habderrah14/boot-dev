# Chapter 14 — Graphs

> "Arrays model sequences, trees model hierarchies, graphs model everything else — and everything else is most of the world."

## Learning objectives

By the end of this chapter you will be able to:

- Represent a graph as an adjacency list and an adjacency matrix, and choose between them.
- Distinguish directed vs. undirected, weighted vs. unweighted, and cyclic vs. acyclic graphs.
- Build, query, and traverse a graph in Python using plain dicts.
- Recognize which classic algorithm (BFS, DFS, Dijkstra, topological sort, etc.) applies to a given problem.

## Prerequisites & recap

- [Queues](08-queues.md) — BFS uses a queue.
- [Hashmaps](12-hashmaps.md) — adjacency lists are dicts.

## The simple version

A graph is just a collection of *things* (called nodes or vertices) and
*connections* between them (called edges). Think of a social network: people
are nodes, friendships are edges. Think of a road map: cities are nodes, roads
are edges. Think of a build system: tasks are nodes, "A must finish before B"
is a directed edge from A to B.

Unlike trees, graphs have no root, no enforced hierarchy, and can have cycles
(you can follow edges and end up back where you started). That generality
makes graphs the right model for an enormous range of real-world problems —
but it also means you need careful algorithms to avoid infinite loops and
manage complexity.

## Visual flow

```
  Directed graph:

    A ──→ B ──→ D
    |           ↑
    v           |
    C ──────────┘

  Undirected graph:

    A ─── B
    |     |
    C ─── D

  Adjacency list for the directed graph:

    { "A": ["B", "C"],
      "B": ["D"],
      "C": ["D"],
      "D": []          }

  Adjacency matrix for the directed graph:

         A  B  C  D
    A [  0  1  1  0 ]
    B [  0  0  0  1 ]
    C [  0  0  0  1 ]
    D [  0  0  0  0 ]
```

## Concept deep-dive

### Why graphs matter for backend developers

Graphs aren't just an academic exercise. Every time you encounter one of
these, you're working with a graph:

- **Microservice dependencies** — which service calls which? Is there a
  circular dependency?
- **Database foreign keys** — tables and relationships form a graph; migration
  ordering is topological sort.
- **Task scheduling** — build systems (Make, Bazel), CI pipelines, cron
  dependencies.
- **Network routing** — IP packets finding shortest paths.
- **Git commits** — a DAG (directed acyclic graph) of commits.
- **Social features** — friend-of-friend, recommendation engines.

### Terminology

| Term | Meaning |
|---|---|
| **Vertex / node** | An entity in the graph |
| **Edge** | A connection between two vertices |
| **Directed edge** | One-way connection (A → B ≠ B → A) |
| **Undirected edge** | Two-way connection (A — B = B — A) |
| **Weighted edge** | Edge with a numeric cost (distance, latency, bandwidth) |
| **Path** | A sequence of edges connecting two vertices |
| **Cycle** | A path that starts and ends at the same vertex |
| **DAG** | Directed Acyclic Graph — directed, no cycles |
| **Connected** | Every pair of nodes has a path between them |
| **Degree** | Number of edges touching a node (in-degree + out-degree for directed) |

### Representation 1: adjacency list

A dict mapping each node to a list of its neighbors:

```python
graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}
```

For weighted graphs, store `(neighbor, weight)` tuples:

```python
weighted: dict[str, list[tuple[str, float]]] = {
    "A": [("B", 3.0), ("C", 1.0)],
    "B": [("D", 2.0)],
    "C": [("D", 5.0)],
    "D": [],
}
```

**Space:** O(V + E). **Iterate neighbors:** O(degree). **Edge lookup:** O(degree).

### Representation 2: adjacency matrix

A V × V matrix where `matrix[i][j]` is 1 (or the weight) if there's an edge
from i to j:

```python
#         A  B  C  D
matrix = [[0, 1, 1, 0],   # A
          [0, 0, 0, 1],   # B
          [0, 0, 0, 1],   # C
          [0, 0, 0, 0]]   # D
```

**Space:** O(V²). **Edge lookup:** O(1). **Iterate neighbors:** O(V).

### When to choose which

| Scenario | Best representation |
|---|---|
| Sparse graph (most real-world graphs) | **Adjacency list** — O(V + E) space, fast neighbor iteration |
| Dense graph (E ≈ V²) | **Adjacency matrix** — O(1) edge lookup, no worse on space |
| Frequent "is there an edge from A to B?" queries | Adjacency matrix or adjacency list with `set` neighbors |
| Dynamic graph (nodes/edges added/removed) | Adjacency list with `dict[str, set[str]]` |

### Core algorithms — preview

These are detailed in the next chapters, but you should know the landscape:

| Algorithm | Problem it solves | Time |
|---|---|---|
| **BFS** (ch. 15) | Shortest path in unweighted graph; level-by-level traversal | O(V + E) |
| **DFS** (ch. 15) | Cycle detection, topological sort, connected components | O(V + E) |
| **Dijkstra** | Shortest path with non-negative weights | O((V + E) log V) |
| **Bellman-Ford** | Shortest path with negative weights | O(V · E) |
| **Topological sort** | Linear ordering of DAG nodes | O(V + E) |
| **Kruskal / Prim** | Minimum spanning tree | O(E log V) |
| **Floyd-Warshall** | All-pairs shortest paths | O(V³) |

### Graphs in Python

Python has no built-in graph class. For simple problems, `dict[str, list[str]]`
works perfectly. For production graph analysis, use `networkx` — it provides
hundreds of algorithms, visualization, and I/O for standard graph formats.

## Why these design choices

| Choice | Trade-off | When you'd pick differently |
|---|---|---|
| Adjacency list with `dict` | Simple, flexible, O(V+E) space | Adjacency matrix when graph is dense or you need O(1) edge queries |
| `list` neighbors | Preserves insertion order, allows duplicates | `set` neighbors for O(1) edge existence checks and no duplicates |
| `defaultdict(list)` | Auto-creates entries for new nodes | Plain `dict` when you want explicit node registration |
| `networkx` | Feature-complete, well-tested | Overhead too high for performance-critical inner loops — drop to raw dicts |
| Directed over undirected | Models one-way relationships (dependencies, links) | Undirected when the relationship is symmetric (friendships, roads) |

## Production-quality code

```python
from __future__ import annotations
from collections import defaultdict, deque
from typing import Iterator


class DirectedGraph:
    """Directed graph using adjacency list with set-based neighbors."""

    def __init__(self) -> None:
        self._adj: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node: str) -> None:
        self._adj.setdefault(node, set())

    def add_edge(self, src: str, dst: str) -> None:
        self._adj[src].add(dst)
        self._adj.setdefault(dst, set())

    def remove_edge(self, src: str, dst: str) -> None:
        self._adj[src].discard(dst)

    def has_edge(self, src: str, dst: str) -> bool:
        return dst in self._adj.get(src, set())

    def neighbors(self, node: str) -> set[str]:
        return self._adj.get(node, set())

    @property
    def nodes(self) -> set[str]:
        return set(self._adj)

    @property
    def num_edges(self) -> int:
        return sum(len(nbrs) for nbrs in self._adj.values())

    def in_degree(self, node: str) -> int:
        return sum(1 for nbrs in self._adj.values() if node in nbrs)

    def out_degree(self, node: str) -> int:
        return len(self._adj.get(node, set()))

    # -- Traversals (detailed in ch. 15) --------------------------------

    def bfs(self, start: str) -> Iterator[str]:
        visited = {start}
        q: deque[str] = deque([start])
        while q:
            node = q.popleft()
            yield node
            for nbr in sorted(self._adj.get(node, set())):
                if nbr not in visited:
                    visited.add(nbr)
                    q.append(nbr)

    def dfs(self, start: str) -> Iterator[str]:
        visited: set[str] = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            yield node
            for nbr in sorted(self._adj.get(node, set()), reverse=True):
                if nbr not in visited:
                    stack.append(nbr)

    # -- Cycle detection -------------------------------------------------

    def has_cycle(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in self._adj}

        def visit(node: str) -> bool:
            color[node] = GRAY
            for nbr in self._adj.get(node, set()):
                if color.get(nbr, WHITE) == GRAY:
                    return True
                if color.get(nbr, WHITE) == WHITE and visit(nbr):
                    return True
            color[node] = BLACK
            return False

        return any(color[n] == WHITE and visit(n) for n in self._adj)

    # -- Topological sort (Kahn's algorithm) -----------------------------

    def topological_sort(self) -> list[str] | None:
        """Returns topological order, or None if the graph has a cycle."""
        in_deg = {n: 0 for n in self._adj}
        for nbrs in self._adj.values():
            for nbr in nbrs:
                in_deg[nbr] = in_deg.get(nbr, 0) + 1

        q = deque(sorted(n for n, d in in_deg.items() if d == 0))
        order: list[str] = []

        while q:
            node = q.popleft()
            order.append(node)
            for nbr in sorted(self._adj.get(node, set())):
                in_deg[nbr] -= 1
                if in_deg[nbr] == 0:
                    q.append(nbr)

        return order if len(order) == len(in_deg) else None
```

## Security notes

N/A — in-process data structure. The operational concern is **algorithmic
complexity**: a graph with adversarially-crafted edges can make naive
algorithms (e.g., all-pairs shortest path on a dense graph) consume O(V³)
time. When processing user-supplied graph data, cap the number of nodes and
edges, and enforce timeouts on expensive algorithms.

## Performance notes

| Operation | Adjacency list | Adjacency matrix |
|---|---|---|
| Add node | O(1) | O(V) — resize matrix |
| Add edge | O(1) | O(1) |
| Remove edge | O(1) with set neighbors | O(1) |
| Has edge? | O(1) with set; O(deg) with list | O(1) |
| Iterate neighbors | O(deg) | O(V) |
| Space | O(V + E) | O(V²) |
| BFS / DFS | O(V + E) | O(V²) |

**Rule of thumb:** if E << V², use an adjacency list. Most real-world graphs
are sparse — social networks, road maps, dependency graphs all have
E = O(V) to O(V log V). The adjacency list wins on both space and
traversal time.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Infinite loop during traversal | Cycle in the graph and no "visited" set | Always maintain a visited set in BFS/DFS |
| 2 | Missing nodes in traversal output | Graph is disconnected; BFS/DFS from one node doesn't reach all components | Run BFS/DFS from *every* unvisited node |
| 3 | Undirected graph has only one-way edges | Added edge A→B but forgot B→A | For undirected graphs, always add both directions |
| 4 | Topological sort returns `None` unexpectedly | Graph has a cycle — topological sort only works on DAGs | Detect and report the cycle; redesign the dependency structure |
| 5 | Using adjacency matrix for a sparse graph | O(V²) space and O(V²) traversal waste time on empty entries | Switch to adjacency list — O(V + E) is much smaller when E << V² |

## Practice

**Warm-up.** Represent a 4-node undirected graph (A—B, B—C, C—D, A—D) as an
adjacency list. Verify that each edge appears in both directions.

**Standard.** Write a function `degree(graph, node)` that returns the total
degree of a node in an undirected graph (number of edges touching it).

**Bug hunt.** A colleague runs recursive DFS on a graph with a cycle A → B →
C → A. The function never returns. Explain why and propose two fixes.

**Stretch.** Implement cycle detection in a directed graph using DFS with
three-color marking (white/gray/black). Return `True` if a cycle exists.

**Stretch++.** Implement topological sort using Kahn's algorithm (BFS with
in-degree tracking). Verify on a DAG of 6 nodes; return `None` if a cycle
is detected.

<details><summary>Show solutions</summary>

**Warm-up:**

```python
g = {
    "A": ["B", "D"],
    "B": ["A", "C"],
    "C": ["B", "D"],
    "D": ["C", "A"],
}
```

**Bug hunt:** Recursive DFS without a visited set will revisit A after
reaching C → A, then visit B again, then C again — infinite loop. Fix 1:
add a `visited` set and skip already-visited nodes. Fix 2: use iterative
DFS with an explicit stack and visited set (also avoids `RecursionError`).

**Stretch++:**

```python
from collections import deque

def topological_sort(g: dict[str, list[str]]) -> list[str] | None:
    in_deg = {u: 0 for u in g}
    for u in g:
        for v in g[u]:
            in_deg[v] = in_deg.get(v, 0) + 1
    q = deque(u for u, d in in_deg.items() if d == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                q.append(v)
    return order if len(order) == len(in_deg) else None
```

</details>

## In plain terms (newbie lane)
If `Graphs` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. DAG stands for:
    (a) Distributed Adjacency Graph
    (b) Directed Acyclic Graph
    (c) Double-Adjacency Graph
    (d) Directed Associative Graph

2. Adjacency matrix space complexity:
    (a) O(V + E)  (b) O(V²)  (c) O(E)  (d) O(V)

3. Adjacency list is better for:
    (a) dense graphs  (b) sparse graphs  (c) always  (d) never

4. Topological sort works on:
    (a) any graph  (b) any directed graph  (c) only DAGs  (d) only undirected graphs

5. Dijkstra's algorithm requires:
    (a) a DAG  (b) non-negative edge weights  (c) unweighted edges
    (d) a connected graph

**Short answer:**

6. When is an adjacency matrix the right choice over an adjacency list?

7. Give a concrete backend-engineering use case for a directed graph.

*Answers: 1-b, 2-b, 3-b, 4-c, 5-b. 6) When the graph is dense (E ≈ V²) and you need O(1) edge-existence queries. The matrix wastes space on sparse graphs but excels at constant-time lookups on dense ones. 7) Microservice dependency tracking — each service is a node, each call is a directed edge. Topological sort tells you safe deployment order; cycle detection warns you about circular dependencies.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [14-graphs — mini-project](mini-projects/14-graphs-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Big-O and production trade-offs](../06-dsa/03-big-o.md) — performance reasoning for APIs and batch jobs.
  - [Stack memory vs heap objects](../07-c-memory/06-stack-and-heap.md) — why recursion depth and allocation patterns matter.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A graph is the most general data structure: nodes + edges, modeling
  arbitrary relationships — from social networks to build dependencies.
- Adjacency lists (dict of neighbors) are the default for sparse graphs;
  adjacency matrices suit dense graphs with frequent edge queries.
- Directed vs. undirected and weighted vs. unweighted are independent
  dimensions — choose based on the problem.
- Most graph problems reduce to a known algorithm (BFS, DFS, Dijkstra,
  topological sort, etc.) — learn to recognize which one applies.

## Further reading

- `networkx` documentation — the go-to Python library for serious graph work.
- *CLRS* ch. 22–26 — graph algorithms from BFS to max-flow.
- Next: [BFS and DFS](15-bfs-and-dfs.md).
