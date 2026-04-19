# Chapter 10 — Reference Counting GC

> "Reference counting tracks how many names point to an object. When the count hits zero, the object frees itself. CPython itself uses exactly this."

## Learning objectives

By the end of this chapter you will be able to:

- Implement `retain` / `release` on a C object and explain why the initial count is 1.
- Trace reference counts through a sequence of assignments and explain when frees occur.
- Explain why cycles leak under pure reference counting and describe solutions.
- Design a destructor that recursively releases child objects.
- Discuss the thread-safety trade-offs of reference counting.

## Prerequisites & recap

- [Objects](09-objects.md) — opaque structs, constructors/destructors, ownership conventions.

## The simple version

Imagine every object has a counter that says "this many pieces of code are currently using me." When you create an object, the counter starts at 1 (you, the creator). When you share the object with someone else, you bump the counter up (*retain*). When you're done with it, you bump it down (*release*). When the counter hits zero, nobody is using the object, so it frees itself.

This is *reference counting*, and it's the simplest form of automatic memory management. CPython uses it for every Python object you create. The advantage: objects are freed the instant they become unused — deterministic, immediate cleanup. The disadvantage: if two objects point to each other (a cycle), both counters stay at 1 forever, and neither is ever freed.

## Visual flow

```
  Lifecycle of a ref-counted object:

  ┌──────────┐   retain   ┌──────────┐   retain   ┌──────────┐
  │ obj_new  │──────────▶ │ refcount │──────────▶ │ refcount │
  │ rc = 1   │            │ rc = 2   │            │ rc = 3   │
  └──────────┘            └──────────┘            └──────────┘
                                                       │
                          release    release    release │
                          ┌──────────┐         ┌───────▼──┐
                          │ refcount │◀────────│ refcount  │
                          │ rc = 1   │         │ rc = 2    │
                          └────┬─────┘         └───────────┘
                               │ release
                               ▼
                          ┌──────────┐
                          │ rc = 0   │──▶ FREE
                          └──────────┘

  The cycle problem:

  A (rc=1) ──refs──▶ B (rc=1)
      ▲                  │
      └──────refs────────┘

  After releasing external refs:
  A (rc=1) ──refs──▶ B (rc=1)    ← both stuck at 1
      ▲                  │         neither freed
      └──────refs────────┘
```

*Caption: Reference counting frees objects when the count reaches zero. Cycles prevent counts from reaching zero.*

## Concept deep-dive

### The core mechanism

Every object embeds a reference count. `new` sets it to 1. `retain` increments. `release` decrements. At zero, the destructor runs and the memory is freed.

```c
#include <stdlib.h>

typedef struct Obj {
    int refcount;
    /* ... other fields ... */
} Obj;

Obj *obj_new(void) {
    Obj *o = calloc(1, sizeof *o);
    if (o) o->refcount = 1;
    return o;
}

Obj *obj_retain(Obj *o) {
    if (o) o->refcount++;
    return o;
}

void obj_release(Obj *o) {
    if (!o) return;
    if (--o->refcount == 0) {
        /* release any children here */
        free(o);
    }
}
```

Why start at 1, not 0? Because the creator holds the first reference. If you started at 0, you'd need an immediate `retain` after every `new` — an easy step to forget.

Why return `Obj *` from `retain`? So you can write `node->child = obj_retain(other)` in a single expression.

### Rules for users

1. **`new` gives you one reference.** You must eventually `release` it.
2. **Storing a pointer into a field:** `retain` before storing.
3. **Overwriting a field:** `release` the old value, `retain` the new.
4. **Functions that borrow** don't retain. Functions that **keep** a reference do retain.
5. **Don't use an object after your last `release`** — it may be freed.

### Destructors must release children

When an object's count reaches zero, its destructor must release any objects it owns. Otherwise, those children are leaked:

```c
typedef struct Node {
    int refcount;
    Obj *payload;
    struct Node *next;
} Node;

Node *node_new(Obj *payload) {
    Node *n = calloc(1, sizeof *n);
    if (!n) return NULL;
    n->refcount = 1;
    n->payload  = obj_retain(payload);
    n->next     = NULL;
    return n;
}

void node_release(Node *n) {
    if (!n) return;
    if (--n->refcount == 0) {
        obj_release(n->payload);
        node_release(n->next);
        free(n);
    }
}
```

The chain reaction: releasing the head of a list causes each node to release the next, freeing the entire list when all external references are gone.

### The cycle problem

```c
Node *a = node_new(some_obj);
Node *b = node_new(some_obj);
a->next = node_retain(b);   /* b's refcount = 2 */
b->next = node_retain(a);   /* a's refcount = 2 */

node_release(a);  /* a's count drops to 1 (b still refs it) */
node_release(b);  /* b's count drops to 1 (a still refs it) */
/* Both stuck at 1 forever — leaked */
```

Why does this happen? Each object holds a reference to the other, keeping both counts above zero. No amount of external `release` calls can break the cycle.

### Solutions to cycles

**1. Weak references.** A weak reference doesn't increment the refcount. One side of the cycle uses a weak ref, so the other side can reach zero:

```c
typedef struct {
    Obj *target;    /* NOT retained */
    int  is_valid;  /* set to 0 when target is freed */
} WeakRef;
```

When the target is freed, it sets `is_valid = 0` on all its weak refs. Code must check `is_valid` before dereferencing.

**2. Cycle collector.** Periodically trace from known roots and identify groups of objects reachable only from each other. Free the entire group. CPython does this: primary refcount for most frees, plus a generational cycle collector for objects that might participate in cycles.

**3. Avoid cycles by design.** Tree structures don't cycle. Parent→child is an owning reference; child→parent (if needed) is a borrow. This is the simplest and most common solution.

### Thread safety

Incrementing and decrementing a plain `int` from multiple threads is a data race:

```
Thread A: reads refcount (1)
Thread B: reads refcount (1)
Thread A: writes refcount = 0 → frees!
Thread B: writes refcount = 0 → double free!
```

Solutions:

| Approach | Cost | Used by |
|---|---|---|
| Single-thread only | Zero | Many C libraries |
| `_Atomic int refcount` | ~1–5 ns per op | Rust `Arc`, Swift ARC |
| Mutex | ~20–50 ns per op | Overkill for refcount |
| Global interpreter lock | Zero per-op, blocks threads | CPython (GIL) |

For most C code, either stay single-threaded or use `_Atomic int`:

```c
#include <stdatomic.h>

typedef struct {
    _Atomic int refcount;
    /* ... */
} AtomicObj;

void atomic_release(AtomicObj *o) {
    if (!o) return;
    if (atomic_fetch_sub(&o->refcount, 1) == 1) {
        free(o);
    }
}
```

`atomic_fetch_sub` returns the *previous* value — if it was 1, the new value is 0 and we free.

## Why these design choices

**Why use refcounting over tracing GC?** Refcounting is deterministic: objects are freed the *instant* the last reference is dropped. This means file handles close immediately, network connections shut down promptly, and memory usage stays tight. Tracing GC defers cleanup to collection pauses, which is fine for memory but bad for scarce resources like sockets.

**Why does CPython use refcounting + cycle collector?** Pure refcounting can't handle cycles, but it handles 99% of objects perfectly. The cycle collector only needs to examine objects that *might* participate in cycles (containers like lists, dicts, classes). This gives CPython immediate cleanup for simple objects and periodic cycle collection for the rest.

**When would you pick differently?** If cycles are common and you don't need deterministic cleanup, a tracing GC (Go, Java, .NET) is simpler. If you need zero-overhead ownership, Rust's borrow checker eliminates the counter entirely.

## Production-quality code

### Boxed int with full refcount discipline

```c
#include <stdlib.h>
#include <stdio.h>

typedef struct BoxedInt {
    int refcount;
    int value;
} BoxedInt;

BoxedInt *bi_new(int v) {
    BoxedInt *b = malloc(sizeof *b);
    if (!b) return NULL;
    b->refcount = 1;
    b->value = v;
    return b;
}

BoxedInt *bi_retain(BoxedInt *b) {
    if (b) b->refcount++;
    return b;
}

void bi_release(BoxedInt *b) {
    if (!b) return;
    if (--b->refcount == 0) {
        free(b);
    }
}

void bi_print(const BoxedInt *b) {
    if (b) printf("BoxedInt(%d, rc=%d)\n", b->value, b->refcount);
}
```

### Refcounted linked list

```c
#include <stdlib.h>
#include <stdio.h>

typedef struct RCNode {
    int refcount;
    int value;
    struct RCNode *next;
} RCNode;

RCNode *rcnode_new(int value) {
    RCNode *n = calloc(1, sizeof *n);
    if (!n) return NULL;
    n->refcount = 1;
    n->value = value;
    return n;
}

RCNode *rcnode_retain(RCNode *n) {
    if (n) n->refcount++;
    return n;
}

void rcnode_release(RCNode *n) {
    while (n && --n->refcount == 0) {
        RCNode *next = n->next;
        free(n);
        n = next;
    }
}

void rcnode_append(RCNode *head, int value) {
    RCNode *cur = head;
    while (cur->next) cur = cur->next;
    cur->next = rcnode_new(value);
}

void rcnode_print(const RCNode *n) {
    for (; n; n = n->next)
        printf("%d -> ", n->value);
    printf("NULL\n");
}
```

Note: the `release` function uses iteration instead of recursion to avoid stack overflow on long lists.

## Security notes

- **Refcount overflow**: if the refcount overflows (goes past `INT_MAX`), decrementing wraps around and the object is freed while still in use. In practice, use `size_t` or clamp at a maximum value. CPython uses `Py_ssize_t` and treats very high refcounts as "immortal."
- **Double release**: decrementing below zero causes the same refcount to "wrap" and eventually reach zero again, triggering a double free. Defensive code can `assert(o->refcount > 0)` in the release function during development.
- **Use-after-release**: the most common refcount bug. Object A releases B, then later dereferences B. If B's count reached zero, the memory is freed and potentially reallocated. Use ASan to catch these.

## Performance notes

- **Per-operation cost**: a refcount increment/decrement is a single memory read-modify-write. On x86-64 with atomics, it's 1–5 ns. Without atomics, it's essentially free (~0.3 ns).
- **Cache pressure**: every retain/release touches the refcount field, which means the cache line containing the object header is written on every reference change. For objects referenced from many threads, this causes *cache line bouncing*.
- **Deterministic cleanup**: the key performance advantage of refcounting. File descriptors, database connections, and locks are released immediately — not at the next GC pause.
- **Comparison to tracing GC**: refcounting has higher per-operation cost but lower latency. Tracing GC has lower throughput cost (no per-assignment work) but occasional pauses.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Memory grows without bound | Forgot to `retain` before storing; `release` happens on a non-retained copy | Always `retain` when storing a reference in a field |
| Crash on release | Refcount went negative (double release) | `assert(o->refcount > 0)` in debug builds; set pointer to NULL after release |
| Leak reported by Valgrind with no missing `release` | Cycle: two objects referencing each other | Use weak references for back-pointers or break the cycle by design |
| Data race crash in multithreaded code | Non-atomic refcount incremented/decremented from multiple threads | Use `_Atomic int` or restrict the object to one thread |
| Destructor doesn't release children | Forgot to call `release` on owned fields when count hits zero | The destructor must release every field it `retain`ed |

## Practice

**Warm-up.** Implement `BoxedInt` with `bi_new`, `bi_retain`, `bi_release`. Create one, retain it twice, release it three times, and verify it's freed.

**Standard.** Build a refcounted `Node` list. Push three nodes. Retain the head from two places. Release one, verify the list survives. Release the other, verify the list is freed (use Valgrind or ASan).

**Bug hunt.** What's wrong with this code?

```c
RCNode *a = rcnode_new(1);
RCNode *b = rcnode_new(2);
a->next = b;               /* forgot retain */
rcnode_release(a);          /* frees a, then frees b (rc was 1) */
rcnode_release(b);          /* double free! */
```

**Stretch.** Add a `WeakRef` type that stores a pointer without bumping the refcount. Include an `is_valid` flag that the destructor clears.

**Stretch++.** Make `retain` and `release` thread-safe using `_Atomic int`. Write a test that creates an object, shares it across two pthreads, and verifies correct cleanup.

<details><summary>Solutions</summary>

**Bug hunt.** `a->next = b` stores `b` without retaining it. `b`'s refcount stays at 1. When `rcnode_release(a)` frees `a` and then frees `a->next` (which is `b`), `b`'s refcount goes from 1 to 0 and it's freed. Then `rcnode_release(b)` tries to free `b` again — double free. Fix: `a->next = rcnode_retain(b);` bumps `b`'s count to 2.

**Warm-up.**

```c
int main(void) {
    BoxedInt *b = bi_new(42);    /* rc = 1 */
    bi_retain(b);                 /* rc = 2 */
    bi_retain(b);                 /* rc = 3 */
    bi_release(b);                /* rc = 2 */
    bi_release(b);                /* rc = 1 */
    bi_release(b);                /* rc = 0 → freed */
    return 0;
}
```

**Stretch.**

```c
typedef struct {
    RCNode *target;
    int is_valid;
} WeakRef;

WeakRef weak_ref(RCNode *target) {
    return (WeakRef){ .target = target, .is_valid = 1 };
}

RCNode *weak_deref(WeakRef *w) {
    return w->is_valid ? w->target : NULL;
}
```

In the destructor, iterate registered weak refs and set `is_valid = 0`.

</details>

## In plain terms (newbie lane)
If `Refcounting Gc` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. When refcount reaches zero:
    (a) the destructor runs and memory is freed  (b) nothing happens  (c) the count resets  (d) the OS reclaims it later

2. Cycles cause:
    (a) crashes  (b) leaks under pure reference counting  (c) faster frees  (d) nothing

3. The best remedy for reference cycles:
    (a) weak references or a cycle collector  (b) ignore them  (c) use `malloc` differently  (d) stack-allocate everything

4. Thread-safe refcount requires:
    (a) a plain `int`  (b) `_Atomic int` or a lock  (c) nothing special  (d) it's impossible

5. CPython's memory management combines:
    (a) mark-and-sweep only  (b) reference counting plus a cycle collector  (c) no GC at all  (d) region-based allocation

**Short answer:**

6. Why must a destructor release the object's own retained references?
7. Why prefer atomic operations over locks for refcount updates?

*Answers: 1-a, 2-b, 3-a, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [10-refcounting-gc — mini-project](mini-projects/10-refcounting-gc-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Reference counting frees objects the instant the last reference is dropped — deterministic and immediate.
- Every `new` starts at refcount 1. Retain before storing; release when done. Destructors must release children.
- Pure refcounting leaks on cycles. Fix with weak references, a cycle collector, or avoiding cycles by design.
- Thread-safe refcounting requires atomic operations; CPython uses the GIL instead.

## Further reading

- CPython `Include/object.h` — `Py_INCREF` / `Py_DECREF` in the real world.
- Swift ARC documentation — reference counting with compiler-inserted retain/release.
- Next: [Mark and Sweep GC](11-mark-and-sweep-gc.md).
