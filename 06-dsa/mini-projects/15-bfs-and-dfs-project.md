# Mini-project — 15-bfs-and-dfs

_Companion chapter:_ [`15-bfs-and-dfs.md`](../15-bfs-and-dfs.md)

**Goal.** Build a maze solver: given a 2D grid with walls (`#`), open spaces
(`.`), a start (`S`), and an end (`E`), find and display the shortest path
using BFS.

**Acceptance criteria:**

- Read a maze from a text file (one row per line).
- Find the shortest path from S to E using BFS.
- Print the maze with the path marked (e.g., `*` for path cells).
- Print the path length.
- Handle edge cases: no path exists, start = end, multiple S or E (error).

**Hints:**

- Neighbors of cell (r, c) are (r±1, c) and (r, c±1) — skip walls and
  out-of-bounds.
- Store predecessor pointers to reconstruct the path.

**Stretch:** Add weighted edges (some cells cost more to traverse, indicated
by digits 1–9) and switch to Dijkstra for the shortest weighted path.
