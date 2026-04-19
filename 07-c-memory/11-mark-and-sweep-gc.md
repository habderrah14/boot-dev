# Chapter 11 — Mark and Sweep GC

> "Refcount frees as soon as it can. Mark-and-sweep waits, scans, and frees everything unreachable. Pay less on every operation; occasionally pay for a full scan."

## Learning objectives

By the end of this chapter you will be able to:

- Describe the mark and sweep phases and explain why each is necessary.
- Identify "roots" in a program and explain their role in reachability.
- Implement a toy mark-and-sweep collector in C.
- Compare mark-and-sweep with reference counting on cycle handling, latency, and throughput.
- Explain how generational GC builds on mark-and-sweep to reduce pause times.

## Prerequisites & recap

- [Reference Counting GC](10-refcounting-gc.md) — deterministic but can't handle cycles.
- [Objects](09-objects.md) — opaque structs, ownership.

## The simple version

Mark-and-sweep asks a simple question: "can the running program still reach this object?" Instead of counting references, the collector pauses the program, starts from every pointer the program is actively using (the *roots*), and follows all references outward, *marking* every object it reaches. Then it *sweeps* through every allocated object: anything without a mark is unreachable — garbage — and gets freed. Marks are cleared for the next cycle.

The beauty of this approach: it handles cycles for free. If A→B→A and neither is reachable from a root, neither gets marked, and both are swept. The cost: the program stops during collection (a "pause"), and the collector must know about every allocation and every root.

## Visual flow

```
  Before collection:

  ROOTS                           HEAP
  ┌──────┐                       ┌───┐   ┌───┐   ┌───┐   ┌───┐
  │ main │──refs──▶               │ A │──▶│ B │──▶│ C │   │ D │
  │ vars │         ▲              └───┘   └───┘   └───┘   └───┘
  └──────┘         │                                ▲       ▲
                   │                                │       │
                   └────────────────────────────────┘       │
                                                    (D is not
                                                     reachable)

  Mark phase:                                 Sweep phase:
  Start from roots, follow refs.              Walk all allocations.
  Mark A ✓  B ✓  C ✓                          A ✓ → keep (clear mark)
  D is never reached → unmarked               B ✓ → keep (clear mark)
                                              C ✓ → keep (clear mark)
                                              D ✗ → FREE

  Result: D is freed. A, B, C survive. Cycle A→B→A would also
  be freed if neither A nor B were root-reachable.
```

*Caption: Mark traces reachability from roots. Sweep frees everything the mark phase didn't visit.*

## Concept deep-dive

### The two phases

**Mark:** Start from roots. For each root, recursively follow all outgoing references, setting a `marked` flag on every object visited. If you've already marked an object, stop (this handles cycles — you don't loop forever).

**Sweep:** Walk the global list of all allocations. If an object isn't marked, it's unreachable — free it and remove it from the list. If it is marked, clear the mark for the next collection cycle.

### What are roots?

A root is any pointer the program is currently using:

- **Global and static variables** — always reachable for the program's lifetime.
- **Local variables on the call stack** — reachable until the function returns.
- **CPU registers** — may hold pointers during computation.
- **Pinned handles** — explicitly registered references for FFI or thread safety.

In a real collector, finding stack roots automatically requires a *conservative scan* (treating every stack word that looks like a pointer as one) or compiler cooperation (generating a *stack map* that says where pointers live in each frame). For a toy collector, you register roots explicitly.

### The allocation list

The collector must know about every object it might need to free. The simplest approach: maintain a linked list of all allocations. Every `gc_alloc` adds to the list. Sweep walks the list and removes freed nodes.

### Why this works for cycles

Consider A→B→A with no root reference to either:

1. Mark phase: no root reaches A, so A isn't marked. B isn't marked either.
2. Sweep phase: both A and B are unmarked → freed.

Refcounting would keep both at count 1 forever. Mark-and-sweep doesn't care about counts — it only cares about reachability.

### Pros and cons

| | Mark-and-sweep | Reference counting |
|---|---|---|
| **Cycles** | Handled naturally | Leaks without extra machinery |
| **Per-operation cost** | None (no work on assign) | Retain/release on every reference change |
| **Cleanup timing** | Deferred to collection pause | Immediate when count hits zero |
| **Pause time** | Stop-the-world during collection | None (work spread across operations) |
| **Implementation** | More complex (needs roots, alloc list) | Simple (counter in each object) |
| **Memory usage** | Spikes between collections | Stays tight |

### Generational GC

Observation: most objects die young. A generational collector divides objects into generations:

- **Young (gen 0):** recently allocated. Collected frequently (cheap — most are already dead).
- **Old (gen 1, 2, ...):** survived previous collections. Collected rarely (expensive — most are alive).

Objects that survive a young collection are *promoted* to the old generation. This dramatically reduces pause times because most collections only scan the small young generation.

CPython's cycle collector is generational: generation 0 is collected after every 700 allocations, generation 1 after every 10 gen-0 collections, and generation 2 after every 10 gen-1 collections.

### A toy collector

```c
#include <stdlib.h>
#include <string.h>

typedef struct GCObj GCObj;
struct GCObj {
    int     marked;
    GCObj  *next_alloc;   /* linked list of all allocations */
    size_t  nrefs;        /* number of outgoing references */
    GCObj **refs;          /* array of outgoing references */
};

static GCObj *all_allocs = NULL;
static GCObj **roots     = NULL;
static size_t  roots_len = 0;
static size_t  roots_cap = 0;

GCObj *gc_alloc(size_t nrefs) {
    GCObj *o = calloc(1, sizeof *o + nrefs * sizeof(GCObj *));
    if (!o) return NULL;
    o->nrefs = nrefs;
    o->refs  = (GCObj **)(o + 1);
    o->next_alloc = all_allocs;
    all_allocs = o;
    return o;
}

int gc_add_root(GCObj *o) {
    if (roots_len == roots_cap) {
        size_t new_cap = roots_cap ? roots_cap * 2 : 8;
        GCObj **tmp = realloc(roots, new_cap * sizeof *tmp);
        if (!tmp) return -1;
        roots = tmp;
        roots_cap = new_cap;
    }
    roots[roots_len++] = o;
    return 0;
}

static void mark(GCObj *o) {
    if (!o || o->marked) return;
    o->marked = 1;
    for (size_t i = 0; i < o->nrefs; i++)
        mark(o->refs[i]);
}

void gc_collect(void) {
    /* Mark phase: trace from all roots */
    for (size_t i = 0; i < roots_len; i++)
        mark(roots[i]);

    /* Sweep phase: free unmarked, clear marks on survivors */
    GCObj **p = &all_allocs;
    while (*p) {
        if (!(*p)->marked) {
            GCObj *dead = *p;
            *p = dead->next_alloc;
            free(dead);
        } else {
            (*p)->marked = 0;
            p = &(*p)->next_alloc;
        }
    }
}

void gc_shutdown(void) {
    GCObj *o = all_allocs;
    while (o) {
        GCObj *next = o->next_alloc;
        free(o);
        o = next;
    }
    all_allocs = NULL;
    free(roots);
    roots = NULL;
    roots_len = roots_cap = 0;
}
```

Real collectors add: incremental/concurrent collection, compaction (defragmentation), write barriers (for generational tracking), precise stack scanning, and support for finalizers. But this toy captures the essential algorithm.

## Why these design choices

**Why stop the world?** During marking, the collector must see a consistent view of the object graph. If the program keeps running, it might create new objects or change references while the collector is scanning — leading to premature frees or missed objects. Concurrent and incremental collectors exist but are far more complex, using write barriers to track mutations during collection.

**Why a linked list of all allocations?** The sweep phase must visit every allocated object to find unmarked ones. A linked list is the simplest way. More sophisticated allocators use block-based or bitmap-based tracking for better cache performance.

**When would you pick differently?** For latency-sensitive applications (games, real-time audio), stop-the-world pauses are unacceptable. Use incremental or concurrent collectors (Go's GC, Java's ZGC/Shenandoah). For deterministic cleanup (RAII, file handles), reference counting or Rust's ownership system is superior. Mark-and-sweep is best when throughput matters more than latency and cycles are common.

## Production-quality code

### Using the toy collector

```c
#include <stdio.h>

int main(void) {
    /* Build a small graph */
    GCObj *root = gc_alloc(2);
    gc_add_root(root);

    GCObj *child1 = gc_alloc(0);
    GCObj *child2 = gc_alloc(1);
    root->refs[0] = child1;
    root->refs[1] = child2;

    GCObj *grandchild = gc_alloc(0);
    child2->refs[0] = grandchild;

    /* Allocate garbage (no root path) */
    GCObj *garbage1 = gc_alloc(0);
    GCObj *garbage2 = gc_alloc(1);
    garbage2->refs[0] = garbage1;
    (void)garbage1; (void)garbage2;

    printf("Before collect: all objects in alloc list\n");
    gc_collect();
    printf("After collect: garbage1 and garbage2 freed\n");

    gc_shutdown();
    return 0;
}
```

### Cycles collected correctly

```c
int main(void) {
    GCObj *a = gc_alloc(1);
    GCObj *b = gc_alloc(1);
    a->refs[0] = b;
    b->refs[0] = a;
    /* No roots reference a or b */

    gc_collect();
    /* Both a and b are freed — cycle is no problem */

    gc_shutdown();
    return 0;
}
```

### Iterative mark (production-safe for deep graphs)

The recursive `mark` function can overflow the stack on deep object graphs (e.g., a linked list with a million nodes). Production collectors use an explicit worklist:

```c
#include <stdlib.h>

static void mark_iterative(GCObj *start) {
    if (!start || start->marked) return;

    size_t cap = 64, len = 0;
    GCObj **stack = malloc(cap * sizeof *stack);
    if (!stack) return;

    stack[len++] = start;
    start->marked = 1;

    while (len > 0) {
        GCObj *o = stack[--len];
        for (size_t i = 0; i < o->nrefs; i++) {
            GCObj *ref = o->refs[i];
            if (ref && !ref->marked) {
                ref->marked = 1;
                if (len == cap) {
                    cap *= 2;
                    GCObj **tmp = realloc(stack, cap * sizeof *tmp);
                    if (!tmp) { free(stack); return; }
                    stack = tmp;
                }
                stack[len++] = ref;
            }
        }
    }
    free(stack);
}
```

## Security notes

- **Missing roots lead to premature frees**: if you forget to register a root, the collector frees objects the program is still using. This is a use-after-free vulnerability. In a real GC, the root set must be precise or conservatively overapproximate (never miss a true root).
- **Finalizer ordering**: if freed objects run cleanup code (finalizers), the order matters. A finalizer that accesses another finalized object can read freed memory. Most production GCs forbid inter-object access in finalizers.
- **Conservative scanning risks**: treating every integer that looks like a pointer as a root keeps some garbage alive (false retention), but never frees live objects. This wastes memory but is safe. The alternative — precise scanning — is harder to implement but doesn't over-retain.

## Performance notes

- **Mark phase**: O(live objects). You only visit reachable objects, and each is visited once.
- **Sweep phase**: O(total allocations) — you walk every object, live or dead.
- **Total collection cost**: O(live + dead) = O(all allocations). This means collections are cheaper when most objects are dead (common in generational young gen).
- **Pause time**: proportional to heap size. A 1 GB heap with millions of objects may pause for 10–100 ms. Generational collection reduces this to sub-millisecond for young-gen collections.
- **Allocation cost**: adding to a linked list is O(1). Bump-pointer allocation (used in copying collectors) is even faster — just increment a pointer.
- **Memory overhead**: each object needs a `marked` bit and an `alloc_list` pointer. In practice, the mark bit is packed into unused pointer bits or a bitmap.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Live object freed during collection | Root not registered; collector thinks object is unreachable | Always `gc_add_root` for global/persistent references |
| Stack overflow during mark | Recursive `mark` on deep object graphs (thousands of nodes) | Use iterative marking with an explicit stack/worklist |
| Collection takes too long | Sweep scans all allocations, including long-lived objects | Use generational GC: scan young gen frequently, old gen rarely |
| Memory usage grows between collections | GC only runs when triggered; objects accumulate | Tune the allocation threshold; collect more frequently |
| Object graph corruption after collection | Mutation during collection (concurrent modification) | Stop the world during collection, or add write barriers |

## Practice

**Warm-up.** Add `gc_add_root` and `gc_remove_root` functions to the toy collector. Verify that adding a root keeps an object alive across a `gc_collect`.

**Standard.** Rewrite the `mark` function iteratively using an explicit stack (dynamic array). Test with a chain of 100 linked objects.

**Bug hunt.** Why is the recursive `mark` function dangerous for long linked lists?

```c
static void mark(GCObj *o) {
    if (!o || o->marked) return;
    o->marked = 1;
    for (size_t i = 0; i < o->nrefs; i++)
        mark(o->refs[i]);
}
```

**Stretch.** Add allocation counters: count `gc_alloc` calls, live objects after collection, and freed objects per collection. Print stats after each `gc_collect`.

**Stretch++.** Add a simple generational split: young (gen 0) and old (gen 1). Promote objects that survive two collections. Collect gen 0 frequently (every 100 allocations) and gen 1 rarely (every 10 gen-0 collections).

<details><summary>Solutions</summary>

**Bug hunt.** Each recursive `mark` call adds a stack frame (~100 bytes). A linked list of 100,000 nodes causes ~10 MB of stack usage, which exceeds the default stack size (typically 1–8 MB) and crashes with a segfault. The fix is iterative marking with a heap-allocated worklist.

**Warm-up.**

```c
int gc_add_root(GCObj *o) {
    if (roots_len == roots_cap) {
        size_t new_cap = roots_cap ? roots_cap * 2 : 8;
        GCObj **tmp = realloc(roots, new_cap * sizeof *tmp);
        if (!tmp) return -1;
        roots = tmp;
        roots_cap = new_cap;
    }
    roots[roots_len++] = o;
    return 0;
}

void gc_remove_root(GCObj *o) {
    for (size_t i = 0; i < roots_len; i++) {
        if (roots[i] == o) {
            roots[i] = roots[--roots_len];
            return;
        }
    }
}
```

**Stretch.**

```c
static size_t total_allocs = 0;
static size_t total_frees  = 0;

GCObj *gc_alloc(size_t nrefs) {
    total_allocs++;
    /* ... existing code ... */
}

void gc_collect(void) {
    size_t freed = 0;
    /* ... mark phase ... */
    GCObj **p = &all_allocs;
    while (*p) {
        if (!(*p)->marked) {
            GCObj *dead = *p;
            *p = dead->next_alloc;
            free(dead);
            freed++;
        } else {
            (*p)->marked = 0;
            p = &(*p)->next_alloc;
        }
    }
    total_frees += freed;
    fprintf(stderr, "[GC] freed=%zu total_allocs=%zu total_frees=%zu\n",
            freed, total_allocs, total_frees);
}
```

</details>

## In plain terms (newbie lane)
If `Mark And Sweep Gc` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. The mark phase:
    (a) frees memory  (b) identifies reachable objects by tracing from roots  (c) deallocates  (d) reorders memory

2. The sweep phase:
    (a) frees unmarked (unreachable) objects  (b) marks objects  (c) compacts memory  (d) resets pointers

3. Roots are:
    (a) leaf nodes  (b) known-reachable starting points (globals, stack, registers)  (c) globals only  (d) heap-only pointers

4. Cycles under mark-and-sweep:
    (a) leak  (b) are handled — unreachable cycles are freed  (c) crash the collector  (d) require weak references

5. Immediate cleanup advantage belongs to:
    (a) mark-and-sweep  (b) reference counting  (c) both equally  (d) generational GC only

**Short answer:**

6. Compare reference counting and mark-and-sweep on cycle handling and pause time.
7. Why are generational collectors so effective in practice?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [11-mark-and-sweep-gc — mini-project](mini-projects/11-mark-and-sweep-gc-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Mark-and-sweep traces from roots to find reachable objects, then frees everything else — cycles are handled naturally.
- The cost is stop-the-world pauses proportional to heap size, with no per-operation overhead.
- Generational GC exploits the "most objects die young" observation to reduce pause times dramatically.
- Real collectors (Go, Java, CPython's cycle collector) build on these fundamentals with incremental, concurrent, and compacting techniques.

## Further reading

- *The Garbage Collection Handbook*, Jones, Hosking, and Moss — the definitive reference.
- CPython `Modules/gcmodule.c` — the cycle collector paired with refcounting.
- Bob Nystrom, *Crafting Interpreters*, ch. 26 — a mark-and-sweep GC for a toy VM.
- Next module: [Module 08 — JavaScript](../08-js/README.md).
