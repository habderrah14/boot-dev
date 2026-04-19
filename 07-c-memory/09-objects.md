# Chapter 09 — Objects

> "C has no classes, but you can still build objects: a struct for state, a set of functions that operate on it, and a discipline for who owns what."

## Learning objectives

By the end of this chapter you will be able to:

- Build an "object" in C using the opaque struct + constructor/destructor + methods pattern.
- Encapsulate implementation details behind forward-declared types.
- Implement runtime polymorphism using a vtable (struct of function pointers).
- Design clear ownership conventions and document them in your API.
- Explain how C's object patterns map to OOP concepts you know from Python or Java.

## Prerequisites & recap

- [Structs](02-structs.md) — data grouping and `typedef`.
- [Stack Data Structure](08-stack-data-structure.md) — you've already built an opaque struct with `new`/`free` — that's an object.

## The simple version

An "object" in C is just a struct (the data), a set of functions that take a pointer to that struct as their first argument (the methods), and a convention about who creates and destroys instances (the ownership). You hide the struct's fields by putting its definition in the `.c` file, not the `.h` header. Callers can hold a pointer but can't peek inside — they must use your API.

For polymorphism — multiple implementations of the same interface — you embed a pointer to a *vtable*: a struct full of function pointers. Each concrete type provides its own vtable. Calling a method goes through the vtable, dispatching to the right implementation at runtime. This is exactly how C++ virtual methods work under the hood; you're just doing it by hand.

## Visual flow

```
  Opaque pointer pattern:

  shape.h (public)               shape.c (private)
  ┌─────────────────────┐        ┌──────────────────────────┐
  │ typedef struct Shape │        │ struct Shape {           │
  │   Shape;             │        │   enum { CIRCLE, RECT } │
  │                      │        │     kind;               │
  │ Shape *shape_new_*() │        │   union { ... } as;     │
  │ double shape_area()  │        │ };                      │
  │ void   shape_free()  │        └──────────────────────────┘
  └─────────────────────┘         callers can't see fields

  Vtable-based polymorphism:

  ┌──────────────┐     ┌────────────────┐     ┌────────────────┐
  │   Stream     │     │  FileStream    │     │  MemStream     │
  │  ┌────────┐  │     │  vt ──▶ file_vt│     │  vt ──▶ mem_vt │
  │  │ vt ────┼──┤     │  FILE *f       │     │  char *buf     │
  │  │ impl   │  │     └────────────────┘     │  size_t len    │
  │  └────────┘  │                            └────────────────┘
  └──────────────┘     file_vt = { file_read, file_close }
                       mem_vt  = { mem_read,  mem_close  }

  Dispatch: stream_read(s, ...) → s->vt->read(s, ...)
```

*Caption: The opaque pointer hides internals. The vtable dispatches method calls to the correct implementation.*

## Concept deep-dive

### The opaque pointer pattern

Expose only the type name in the header; keep the struct body in the source:

```c
/* shape.h */
#pragma once

typedef struct Shape Shape;

Shape *shape_new_circle(double r);
Shape *shape_new_rect(double w, double h);
double shape_area(const Shape *s);
void   shape_free(Shape *s);
```

```c
/* shape.c */
#include <stdlib.h>
#include <math.h>
#include "shape.h"

struct Shape {
    enum { CIRCLE, RECT } kind;
    union {
        struct { double r; } circle;
        struct { double w, h; } rect;
    } as;
};
```

Why bother with this ceremony? Because it gives you *encapsulation*. If callers could access `s->kind` directly, they'd write code that depends on the internal layout. When you later add a `TRIANGLE` variant or change `r` to `radius`, their code breaks. With the opaque pointer, you can refactor the internals freely — only the source file changes.

### Constructors and destructors

```c
Shape *shape_new_circle(double r) {
    Shape *s = malloc(sizeof *s);
    if (!s) return NULL;
    *s = (Shape){ .kind = CIRCLE, .as.circle.r = r };
    return s;
}

Shape *shape_new_rect(double w, double h) {
    Shape *s = malloc(sizeof *s);
    if (!s) return NULL;
    *s = (Shape){ .kind = RECT, .as.rect = { w, h } };
    return s;
}

void shape_free(Shape *s) { free(s); }
```

The naming convention `type_new_*` / `type_free` maps directly to constructors and destructors. The `_new` function allocates and initializes. The `_free` function cleans up and deallocates.

### Method dispatch

```c
double shape_area(const Shape *s) {
    switch (s->kind) {
        case CIRCLE: return M_PI * s->as.circle.r * s->as.circle.r;
        case RECT:   return s->as.rect.w * s->as.rect.h;
    }
    return 0.0;
}
```

This is *closed polymorphism*: the set of variants is fixed at compile time (CIRCLE and RECT). Adding a new shape requires modifying the source file. For *open polymorphism* — where new types can be added without changing existing code — you need a vtable.

### Polymorphism with vtables

A vtable is a struct of function pointers. Each concrete type provides its own vtable instance. The base type holds a pointer to the vtable:

```c
/* stream.h */
#pragma once
#include <stddef.h>

typedef struct Stream Stream;

typedef struct {
    int  (*read)(Stream *self, void *buf, size_t n);
    int  (*close)(Stream *self);
} StreamVT;

struct Stream {
    const StreamVT *vt;
    void *impl;
};

int stream_read(Stream *s, void *buf, size_t n);
int stream_close(Stream *s);
```

```c
/* stream.c */
#include "stream.h"

int stream_read(Stream *s, void *buf, size_t n) {
    return s->vt->read(s, buf, n);
}

int stream_close(Stream *s) {
    return s->vt->close(s);
}
```

Each concrete stream provides its own vtable and constructor:

```c
/* file_stream.c */
#include <stdio.h>
#include <stdlib.h>
#include "stream.h"

typedef struct { FILE *f; } FileData;

static int file_read(Stream *self, void *buf, size_t n) {
    FileData *fd = self->impl;
    return (int)fread(buf, 1, n, fd->f);
}

static int file_close(Stream *self) {
    FileData *fd = self->impl;
    fclose(fd->f);
    free(fd);
    free(self);
    return 0;
}

static const StreamVT FILE_VT = { file_read, file_close };

Stream *file_stream_new(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return NULL;

    FileData *fd = malloc(sizeof *fd);
    if (!fd) { fclose(f); return NULL; }
    fd->f = f;

    Stream *s = malloc(sizeof *s);
    if (!s) { fclose(f); free(fd); return NULL; }
    s->vt   = &FILE_VT;
    s->impl = fd;
    return s;
}
```

Callers never see `FileData`. They call `stream_read(s, buf, n)` and the vtable dispatches to the right implementation. This is exactly how C++ vtables work — one extra pointer dereference per method call.

### Ownership conventions

When objects reference other objects, you need clear rules:

| Convention | Meaning | Example |
|---|---|---|
| **Creator frees** | Whoever calls `xxx_new` must call `xxx_free` | Most objects |
| **Transfer** | Function hands ownership to caller; caller must free | `strdup` returns owned memory |
| **Borrow** | Function reads but doesn't own; caller keeps owning | `const T *` parameters |

Get ownership wrong and you have leaks (nobody frees), use-after-free (freed too early), or double-free (freed by both parties). Document ownership in your header comments.

### Ownership cycles

If object A owns object B and B owns A, neither's refcount reaches zero — both leak. Solutions: weak references (ch. 10), cycle collector (ch. 11), or avoid the cycle by design (make one side a borrow, not an owned reference).

## Why these design choices

**Why manual vtables instead of language-level inheritance?** Because C doesn't have classes. The vtable pattern gives you the same runtime dispatch with full control over memory layout and initialization. Many C++ implementations use the exact same technique — a hidden pointer to a table of function pointers.

**Why opaque pointers instead of just "don't touch the fields"?** Because conventions break under pressure. If a developer can see the fields, they'll access them — especially in a rush. The opaque pointer makes it a compile error, not a code-review finding.

**When would you pick differently?** If you're using C++, use virtual methods and RAII — the compiler generates the vtable and destructor calls for you. In Go, interfaces give you vtable-style dispatch without inheritance. In Rust, traits + `dyn Trait` serve the same role. C's manual approach is the right choice when you need total control or are writing in a C-only environment (kernels, embedded).

## Production-quality code

### Logger with vtable dispatch

```c
/* logger.h */
#pragma once

typedef struct Logger Logger;
typedef struct {
    void (*info)(Logger *self, const char *msg);
    void (*error)(Logger *self, const char *msg);
    void (*close)(Logger *self);
} LoggerVT;

struct Logger {
    const LoggerVT *vt;
    void *impl;
};

void logger_info(Logger *l, const char *msg);
void logger_error(Logger *l, const char *msg);
void logger_close(Logger *l);

Logger *stdout_logger_new(void);
Logger *file_logger_new(const char *path);
```

```c
/* logger.c */
#include <stdio.h>
#include <stdlib.h>
#include "logger.h"

void logger_info(Logger *l, const char *msg)  { l->vt->info(l, msg); }
void logger_error(Logger *l, const char *msg) { l->vt->error(l, msg); }
void logger_close(Logger *l)                  { l->vt->close(l); }

static void stdout_info(Logger *self, const char *msg) {
    (void)self;
    fprintf(stdout, "[INFO] %s\n", msg);
}
static void stdout_error(Logger *self, const char *msg) {
    (void)self;
    fprintf(stderr, "[ERROR] %s\n", msg);
}
static void stdout_close(Logger *self) { free(self); }

static const LoggerVT STDOUT_VT = { stdout_info, stdout_error, stdout_close };

Logger *stdout_logger_new(void) {
    Logger *l = malloc(sizeof *l);
    if (!l) return NULL;
    l->vt   = &STDOUT_VT;
    l->impl = NULL;
    return l;
}

typedef struct { FILE *f; } FileLogData;

static void file_info(Logger *self, const char *msg) {
    FileLogData *d = self->impl;
    fprintf(d->f, "[INFO] %s\n", msg);
}
static void file_error(Logger *self, const char *msg) {
    FileLogData *d = self->impl;
    fprintf(d->f, "[ERROR] %s\n", msg);
}
static void file_close(Logger *self) {
    FileLogData *d = self->impl;
    fclose(d->f);
    free(d);
    free(self);
}

static const LoggerVT FILE_VT = { file_info, file_error, file_close };

Logger *file_logger_new(const char *path) {
    FILE *f = fopen(path, "a");
    if (!f) return NULL;

    FileLogData *d = malloc(sizeof *d);
    if (!d) { fclose(f); return NULL; }
    d->f = f;

    Logger *l = malloc(sizeof *l);
    if (!l) { fclose(f); free(d); return NULL; }
    l->vt   = &FILE_VT;
    l->impl = d;
    return l;
}
```

Callers use `logger_info(log, "server started")` regardless of whether `log` writes to stdout or a file.

## Security notes

- **Vtable corruption**: if an attacker can overwrite the vtable pointer (e.g., through a buffer overflow on a nearby field), they can redirect method calls to arbitrary code. Mark vtables as `const` and consider placing them in read-only memory.
- **Use-after-free on objects**: freed objects with vtable pointers are attractive targets for exploitation. The attacker triggers a reallocation of the same size, fills it with a fake vtable, and the next method call jumps to attacker-controlled code.
- **Exposed `void *impl`**: casting `impl` to the wrong type is UB. Validate that `vt` matches the expected vtable before accessing `impl` in code that handles multiple stream types.

## Performance notes

- **Vtable dispatch**: one extra pointer dereference per method call (load vtable address, then load function address, then call). On modern CPUs this adds ~1–2 ns — negligible for most code, but measurable in hot loops with millions of calls.
- **Opaque pointer allocation**: each object requires a heap allocation (for the struct) plus potentially another for `impl`. Consider embedding the impl data directly after the base struct (flexible array member or single allocation with pointer arithmetic) to reduce allocations.
- **Branch prediction**: `switch`-based dispatch (tagged union) is faster than vtable dispatch for a small number of types because the CPU branch predictor handles `switch` well. Vtables win when the number of types grows or when types are added without recompilation.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Compiler error: "incomplete type" when accessing fields | Struct definition is in the `.c` file (opaque pointer, working as intended) | Use the public API functions; don't access fields directly |
| Segfault on first method call | Forgot to set the vtable pointer in the constructor | Initialize `s->vt = &MY_VT;` in every constructor |
| Memory leak when two objects reference each other | Ownership cycle: A owns B, B owns A | Make one reference a borrow (non-owning); or use ref counting (ch. 10) |
| `void *impl` cast to wrong type | Multiple stream types sharing code but impl types differ | Verify the vtable pointer matches before casting, or use separate structs |
| Callers break when you change struct fields | Struct definition exposed in header | Move struct definition to `.c` file; expose only `typedef struct X X;` in header |

## Practice

**Warm-up.** Refactor your `Stack` from ch. 08 to use the opaque pointer pattern if you haven't already. Verify that callers can't access `s->data` directly.

**Standard.** Build a `Shape` object with circle and rect variants using a tagged union. Implement `shape_area`, `shape_perimeter`, and `shape_print`. Use the opaque pointer pattern.

**Bug hunt.** Someone published `shape.h` with the full struct definition. A caller wrote `s->kind = RECT;` without updating the union. Why is this a problem?

**Stretch.** Implement the `Stream` interface with `FileStream` and `MemStream` backends. Write a `read_all` function that works with any `Stream *`.

**Stretch++.** Add `shape_retain` and `shape_release` (refcount-based) to preview ch. 10. Each shape starts with `refcount = 1`. `retain` increments, `release` decrements, and `release` frees when count reaches 0.

<details><summary>Solutions</summary>

**Bug hunt.** By exposing the struct, the caller can set `kind = RECT` while the union still holds circle data (`r`). When `shape_area` reads `s->as.rect.w` and `s->as.rect.h`, it reads the circle's `r` plus garbage padding. The fix: move the struct definition to the `.c` file.

**Warm-up.** Ensure `stack.h` has only `typedef struct Stack Stack;` and function prototypes. The `struct Stack { int *data; size_t size, cap; };` definition lives only in `stack.c`.

**Stretch++.**

```c
struct Shape {
    int refcount;
    enum { CIRCLE, RECT } kind;
    union { struct { double r; } circle; struct { double w, h; } rect; } as;
};

Shape *shape_retain(Shape *s) {
    if (s) s->refcount++;
    return s;
}

void shape_release(Shape *s) {
    if (!s) return;
    if (--s->refcount == 0) free(s);
}
```

</details>

## In plain terms (newbie lane)
If `Objects` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. The opaque pointer pattern:
    (a) exposes all fields  (b) hides fields behind a forward-declared struct  (c) is C++ only  (d) makes code slower

2. A vtable is:
    (a) a hash table of strings to functions  (b) a struct of function pointers for dispatch  (c) a macro  (d) a stack

3. "Creator frees" is:
    (a) a memory leak  (b) an ownership convention  (c) a compiler flag  (d) an OS API

4. The performance cost of vtable dispatch is:
    (a) zero  (b) one extra pointer dereference per call  (c) a full garbage collection  (d) O(n)

5. Two objects each owning the other leads to:
    (a) faster cleanup  (b) a memory leak in manual memory management  (c) nothing  (d) automatic cleanup

**Short answer:**

6. Why should you keep the struct body in the `.c` file rather than the `.h` file?
7. How does a C vtable differ from C++ virtual method dispatch?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-objects — mini-project](mini-projects/09-objects-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Objects in C = opaque struct (data) + functions taking `T *self` (methods) + documented ownership (lifecycle).
- The opaque pointer pattern hides internals by keeping the struct body in the `.c` file.
- Vtables (structs of function pointers) give you runtime polymorphism — the same pattern C++ uses under the hood.
- Ownership must be an explicit, documented convention: creator-frees, transfer, or borrow.

## Further reading

- GObject (GLib) — a full OOP system built in C, used by GTK and GNOME.
- *Object-Oriented Programming with ANSI-C*, Axel-Tobias Schreiner — free online book.
- Next: [Reference Counting GC](10-refcounting-gc.md).
