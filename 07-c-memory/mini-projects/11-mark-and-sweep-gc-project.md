# Mini-project — 11-mark-and-sweep-gc

_Companion chapter:_ [`11-mark-and-sweep-gc.md`](../11-mark-and-sweep-gc.md)

**Goal.** Implement the toy GC from this chapter. Build a small object graph with at least one cycle and unreachable garbage. Run `gc_collect` and verify that unreachable objects (including cycles) are freed while rooted objects survive.

**Acceptance criteria:**

- `gc_alloc`, `gc_add_root`, `gc_collect`, `gc_shutdown` all implemented.
- Test creates: 3 rooted objects, 2 unreachable garbage objects, and 1 unreachable cycle (A→B→A).
- After `gc_collect`, verify (via print statements or counters) that exactly the garbage + cycle were freed.
- `gc_shutdown` cleans up everything.
- Clean under `-fsanitize=address`.

**Hints:**

- Use `calloc` so that `refs` entries default to `NULL` (safe for the mark function).
- `gc_alloc` stores `refs` right after the struct using flexible allocation: `calloc(1, sizeof *o + nrefs * sizeof(GCObj *))`.

**Stretch:** Replace the recursive `mark` with an iterative version. Benchmark with a chain of 100,000 objects — recursive should crash; iterative should complete.
