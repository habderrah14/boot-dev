# Chapter 02 — Structs

> "A struct is how C says 'these fields belong together.' It's the closest thing C has to an object, and it's enough."

## Learning objectives

By the end of this chapter you will be able to:

- Declare, initialize, and nest structs.
- Pass structs by value and by pointer, and know when to choose each.
- Use `typedef` to create cleaner type names.
- Predict struct size by reasoning about alignment and padding.

## Prerequisites & recap

- [C Basics](01-c-basics.md) — types, functions, compilation.

## The simple version

A struct bundles related data into a single variable. Instead of juggling separate `x` and `y` variables, you group them into a `Point` struct and pass it around as one thing. When you hand a struct to a function, C copies every byte of it — like photocopying a form. If the struct is large or you want the function to modify the original, you pass a pointer to it instead (like handing someone the address of the filing cabinet rather than a photocopy).

The compiler may insert invisible padding bytes between fields to keep each one aligned to its natural boundary (doubles on 8-byte boundaries, ints on 4-byte, etc.). This means field order affects how much memory your struct actually uses.

## Visual flow

```
  struct Point (no padding)          struct Bad (wasteful ordering)
  ┌────────────────────────────┐     ┌───┬───────┬────────┬────┬────┐
  │  double x      (8 bytes)  │     │ c │ pad×7 │ double │ int│pad4│
  ├────────────────────────────┤     │ 1 │  (7)  │  (8)   │(4) │(4) │
  │  double y      (8 bytes)  │     └───┴───────┴────────┴────┴────┘
  └────────────────────────────┘     total: 24 bytes
  total: 16 bytes
                                     struct Good (optimal ordering)
                                     ┌────────┬────┬───┬─────┐
                                     │ double │ int│ c │pad×3│
                                     │  (8)   │(4) │(1)│ (3) │
                                     └────────┴────┴───┴─────┘
                                     total: 16 bytes
```

*Caption: Field ordering determines padding. Largest-first minimizes wasted bytes.*

## Concept deep-dive

### Declaration and initialization

```c
struct Point {
    double x;
    double y;
};

struct Point p = { .x = 3.0, .y = 4.0 };
printf("(%.1f, %.1f)\n", p.x, p.y);
```

Designated initializers (`.x = ...`) are clearer than positional ones and protect you when fields are reordered.

### `typedef` — dropping the `struct` keyword

Every time you write `struct Point p`, the `struct` keyword is noise. `typedef` lets you name the type directly:

```c
typedef struct Point {
    double x, y;
} Point;

Point p = {3.0, 4.0};
```

Why keep the tag name (`struct Point`) and the typedef name (`Point`) the same? Convention. Some codebases use different names, but same-name avoids confusion. The tag name also lets you create self-referential structs (a node pointing to another node) since the typedef isn't available inside the struct body.

### By value vs. by pointer

```c
double distance(Point a, Point b) {
    double dx = a.x - b.x, dy = a.y - b.y;
    return sqrt(dx * dx + dy * dy);
}

void translate(Point *p, double dx, double dy) {
    p->x += dx;
    p->y += dy;
}
```

By value copies every byte. For a 16-byte `Point`, that's cheap. For a 256-byte `User` record, it's a silent `memcpy` on every call. Pass by pointer when:

- The struct is large (rule of thumb: bigger than two machine words / 16 bytes).
- The function needs to modify the original.
- You want to signal read-only intent with `const Point *`.

The `->` operator is shorthand for `(*p).x` — it dereferences the pointer and accesses the field in one step.

### Alignment and padding

CPUs read memory most efficiently when data falls on its natural alignment boundary. A `double` (8 bytes) wants to start at an address divisible by 8. The compiler inserts invisible padding bytes to enforce this:

```c
struct Bad {
    char  c;   /* 1 byte, then 7 bytes padding */
    double d;  /* 8 bytes */
    int   i;   /* 4 bytes, then 4 padding */
};              /* total: 24 bytes */

struct Good {
    double d;  /* 8 bytes */
    int   i;   /* 4 bytes */
    char  c;   /* 1 byte, then 3 padding */
};              /* total: 16 bytes */
```

Why does the compiler pad instead of just reading unaligned? On some architectures (ARM, older SPARC), unaligned reads cause a hardware fault. On x86, they work but are slower. The compiler plays it safe and portable.

**Rule of thumb:** order fields from largest alignment to smallest. Use `sizeof(struct X)` to verify.

### Nested structs

Structs compose naturally:

```c
typedef struct Line {
    Point start, end;
} Line;

Line l = { .start = {0, 0}, .end = {3, 4} };
```

### Anonymous structs (C11)

C11 lets you embed structs without naming the field — the inner fields "float up":

```c
typedef struct {
    int id;
    struct { double lat, lon; };  /* anonymous */
} Location;

Location loc = { .id = 1, .lat = 51.5, .lon = -0.1 };
```

This is most useful inside unions (ch. 05).

## Why these design choices

**Why does C copy structs by value?** Because C treats structs the same as integers — they're values. This is simple and predictable: when you pass a struct, the function gets its own copy and can't accidentally corrupt the caller's data. The cost is memcpy overhead for large structs, which is why the pointer convention exists.

**Why not auto-pack fields?** The compiler could reorder fields to eliminate padding, but then `memcmp` on a struct, serialization code, and FFI bindings would all break. C guarantees fields appear in memory in declaration order. If you want optimal packing, you order them yourself.

**When would you pick differently?** In Rust, structs are also values but the compiler *can* reorder fields (unless you use `#[repr(C)]`). In Go, structs are values with the same manual-ordering expectation as C. If struct layout doesn't matter to you, a language with automatic packing is easier.

## Production-quality code

### A user record module

`user.h`:

```c
#pragma once
#include <stddef.h>

typedef struct User {
    long   id;
    char   name[64];
    int    age;
} User;

User  user_create(long id, const char *name, int age);
void  user_print(const User *u);
int   user_cmp(const User *a, const User *b);
```

`user.c`:

```c
#include <stdio.h>
#include <string.h>
#include "user.h"

User user_create(long id, const char *name, int age) {
    User u = {0};
    u.id  = id;
    u.age = age;
    strncpy(u.name, name, sizeof u.name - 1);
    return u;
}

void user_print(const User *u) {
    printf("User{id=%ld, name=\"%s\", age=%d}\n", u->id, u->name, u->age);
}

int user_cmp(const User *a, const User *b) {
    if (a->id != b->id) return (a->id > b->id) - (a->id < b->id);
    return strcmp(a->name, b->name);
}
```

`main.c`:

```c
#include <stdio.h>
#include "user.h"

int main(void) {
    User u1 = user_create(1, "Ada", 36);
    User u2 = user_create(2, "Grace", 85);

    user_print(&u1);
    user_print(&u2);

    printf("cmp = %d\n", user_cmp(&u1, &u2));
    return 0;
}
```

Note `strncpy` with `sizeof u.name - 1` — this prevents buffer overflow when `name` is longer than 63 characters. The `{0}` initializer zeroes the struct, ensuring the name is null-terminated even after `strncpy`.

## Security notes

- **Buffer overflow in fixed-size char arrays**: if you use `strcpy` instead of `strncpy`, a long name silently overflows into adjacent fields. Always bound your copies.
- **Information leakage through padding**: padding bytes are uninitialized. If you send a struct over the network or write it to disk, the padding may contain leftover stack data. Zero the struct before filling it (`memset` or `= {0}`).
- **Struct comparison with `memcmp`**: padding bytes may differ even when all fields are equal, causing false negatives. Compare field by field.

## Performance notes

- Passing a small struct (≤ 16 bytes) by value is often *faster* than by pointer on modern x86-64, because the struct fits in two registers and avoids a memory indirection.
- `sizeof` is a compile-time constant — it costs nothing at runtime.
- Cache performance favors arrays of structs (AoS) for sequential access of all fields, but structs of arrays (SoA) for accessing one field across many records. This matters at scale.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Function doesn't modify the caller's struct | Passed by value (copy) instead of by pointer | Change parameter to `T *` and pass `&s` |
| Compiler says "incompatible type" at call site | Forgot `&` when function expects a pointer | Add `&` before the variable name |
| `sizeof(struct X)` is larger than expected | Padding from suboptimal field ordering | Reorder largest-alignment-first; verify with `sizeof` |
| `strncpy` doesn't null-terminate | Source string is exactly `n` bytes long | Always set `dest[sizeof dest - 1] = '\0'` or use `= {0}` first |
| `memcmp` says two equal structs differ | Padding bytes contain different garbage | Compare field by field, or zero the struct at initialization |

## Practice

**Warm-up.** Define `typedef struct { double w, h; } Rectangle;` and write `double area(const Rectangle *r)`. Print the result.

**Standard.** Reorder `struct Bad` from the deep-dive to minimize `sizeof`. Print `sizeof` before and after to confirm the improvement.

**Bug hunt.** This code compiles. What's wrong?

```c
Point p;
printf("x = %f\n", p.x);
```

**Stretch.** Implement `typedef struct { double re, im; } Complex;` with functions `complex_add`, `complex_mul`, and `complex_print`. Use `const Complex *` for inputs.

**Stretch++.** Add `Complex complex_conj(const Complex *c)` that returns the conjugate. Write a small test harness that verifies `c * conj(c)` has zero imaginary part for several inputs.

<details><summary>Solutions</summary>

**Bug hunt.** `p` is uninitialized. Reading `p.x` is undefined behavior — it may print 0.0, garbage, or cause a crash depending on compiler and optimization level.

**Warm-up.**

```c
#include <stdio.h>

typedef struct { double w, h; } Rectangle;

double area(const Rectangle *r) {
    return r->w * r->h;
}

int main(void) {
    Rectangle r = { .w = 3.0, .h = 4.0 };
    printf("area = %.1f\n", area(&r));
    return 0;
}
```

**Stretch.**

```c
typedef struct { double re, im; } Complex;

Complex complex_add(const Complex *a, const Complex *b) {
    return (Complex){ a->re + b->re, a->im + b->im };
}

Complex complex_mul(const Complex *a, const Complex *b) {
    return (Complex){
        a->re * b->re - a->im * b->im,
        a->re * b->im + a->im * b->re
    };
}

void complex_print(const Complex *c) {
    printf("%.2f + %.2fi\n", c->re, c->im);
}
```

</details>

## In plain terms (newbie lane)
If `Structs` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `p->x` is shorthand for:
    (a) `p.x`  (b) `(*p).x`  (c) `p[x]`  (d) `&p.x`

2. Passing a struct by value:
    (a) shares memory  (b) copies every byte  (c) is illegal in C  (d) requires a pointer

3. `typedef struct X { ... } X;` lets you:
    (a) define two different types  (b) use `X` without the `struct` keyword  (c) avoid struct padding  (d) export fields automatically

4. Struct field order can:
    (a) change program semantics  (b) affect `sizeof` due to padding  (c) be rearranged by the compiler  (d) have no effect on anything

5. `const Point *p` means:
    (a) the pointer can't be redirected  (b) the pointee fields can't be modified through `p`  (c) the pointer is null  (d) same as `Point *p`

**Short answer:**

6. Why should you pass large structs by pointer rather than by value?
7. Explain why reordering struct fields from largest to smallest alignment reduces `sizeof`.

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-structs — mini-project](mini-projects/02-structs-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A struct groups related fields into a single type — C's version of a plain data object.
- Pass small structs by value; pass large ones by `const T *` for efficiency and mutation safety.
- Field order determines padding and `sizeof` — order from largest alignment to smallest.
- Always zero-initialize structs and use bounded string copies to avoid leaking data or overflowing buffers.

## Further reading

- Eric Raymond, *The Lost Art of C Structure Packing* — deep dive into alignment and ABI.
- Next: [Pointers](03-pointers.md).
