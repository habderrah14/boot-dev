# Chapter 05 — Unions

> "A union lets several types share the same memory. It's C's way to say 'this slot holds one of these things at a time.'"

## Learning objectives

By the end of this chapter you will be able to:

- Declare and use a `union` and explain how it differs from a `struct`.
- Combine a union with an enum tag to build a tagged union (C's version of a sum type).
- Explain the aliasing rules and use `memcpy` for safe bit reinterpretation.
- Design tagged union types for interpreters, ASTs, and protocol parsers.

## Prerequisites & recap

- [Enums](04-enums.md) — you'll use enums as the discriminant tag.
- [Structs](02-structs.md) — unions are structs' mirror image: structs stack fields end-to-end; unions overlay them.

## The simple version

A struct says "I have an X *and* a Y *and* a Z." A union says "I have an X *or* a Y *or* a Z — but only one at a time." All members share the same starting address, and the union is as large as its biggest member. You save memory, but you take on the responsibility of knowing which member is currently valid. If you read the `float` member after writing the `int` member, you get garbage (or worse).

The standard pattern is the *tagged union*: wrap a union in a struct alongside an enum that says which member is active. This is how C simulates Python's `Union` types, Rust's `enum` variants, or TypeScript's discriminated unions.

## Visual flow

```
  struct (fields stacked):          union (fields overlaid):
  ┌────────────────────────┐        ┌────────────────────────┐
  │  int i      (4 bytes)  │        │                        │
  ├────────────────────────┤        │   int i   ─┐           │
  │  float f    (4 bytes)  │        │   float f  ├─ same     │
  ├────────────────────────┤        │   char *s ─┘  memory   │
  │  char *s    (8 bytes)  │        │                        │
  └────────────────────────┘        └────────────────────────┘
  total: ≥16 bytes                  total: 8 bytes (max member)

  Tagged union pattern:
  ┌───────────────┬────────────────────────┐
  │ enum tag      │  union data            │
  │ (which is it?)│  (the actual value)    │
  └───────────────┴────────────────────────┘
       ▲                    ▲
       │                    │
  switch(tag)         access tag-appropriate
  to dispatch         member only
```

*Caption: A union overlays all members at the same address. The tag enum tracks which member is valid.*

## Concept deep-dive

### Declaration

```c
union Value {
    int    i;
    float  f;
    char  *s;
};

union Value v;
v.i = 42;
printf("%d\n", v.i);   /* 42 — fine */
v.f = 3.14f;            /* now v.i is meaningless */
```

`sizeof(union Value)` equals the size of its largest member (here, `char *` at 8 bytes on 64-bit), plus any padding needed for alignment.

### Why would you want this?

Memory efficiency. If a variable can be *either* an int *or* a float *or* a string — but never more than one at a time — a union avoids wasting space for the unused alternatives. This matters when you have millions of values (think: a VM's value stack, a JSON parser's node pool, or a packet buffer).

### Type-punning and aliasing

Reading `v.f` after writing `v.i` reinterprets the int's bit pattern as a float. This is called *type-punning*. Under C's strict aliasing rules, this is implementation-defined or outright undefined behavior depending on the types and compiler flags.

The safe, portable way to reinterpret bits:

```c
#include <string.h>
#include <stdint.h>

uint32_t float_bits(float f) {
    uint32_t out;
    memcpy(&out, &f, sizeof out);
    return out;
}
```

`memcpy` is defined to work on any types and modern compilers optimize it to a single register move — zero overhead.

### Tagged union — the essential pattern

Pair a union with an enum tag and wrap both in a struct:

```c
typedef struct Result {
    enum { RES_OK, RES_ERR } tag;
    union {
        int ok_value;
        const char *err_message;
    } data;
} Result;

Result success(int v) {
    return (Result){ .tag = RES_OK, .data.ok_value = v };
}

Result failure(const char *msg) {
    return (Result){ .tag = RES_ERR, .data.err_message = msg };
}

void result_print(const Result *r) {
    switch (r->tag) {
        case RES_OK:  printf("ok: %d\n", r->data.ok_value); break;
        case RES_ERR: fprintf(stderr, "err: %s\n", r->data.err_message); break;
    }
}
```

This pattern is the backbone of C interpreters, AST nodes, protocol parsers, and configuration systems. Every time you see `tag + union`, you're looking at a sum type.

### Anonymous unions (C11)

C11 lets you skip naming the union field, so the union members float up:

```c
typedef struct {
    enum { VAL_NUM, VAL_STR } tag;
    union {
        int   n;
        char *s;
    };
} Value;

Value v = { .tag = VAL_NUM, .n = 7 };
printf("%d\n", v.n);   /* access directly, no .data.n */
```

This is cleaner when the union is always used through the parent struct.

### Size and alignment

A union's size is the maximum of its members, rounded up to the strictest alignment. You always pay for the worst case:

```c
union Big {
    char   c;       /* 1 byte */
    double d;       /* 8 bytes */
};
/* sizeof(union Big) == 8 */
```

This is the cost of flexibility: even when you're only storing a `char`, you use 8 bytes.

## Why these design choices

**Why overlay memory instead of just using a struct?** When you have an array of a million values, each of which is either an int or a double or a string pointer, a struct wastes 20 bytes per element (4+8+8) when you only need at most 8. A tagged union uses 12 bytes (4 for tag + 8 for the largest member), saving nearly half the memory.

**Why doesn't C enforce the tag automatically?** Because tagged unions are a convention, not a language feature. C trusts you to keep the tag in sync. This is why Rust's `enum` is superior for safety — the compiler enforces exhaustive matching and prevents reading the wrong variant.

**When would you pick differently?** If you're writing in Rust, use `enum` — it's a tagged union with compiler enforcement. In TypeScript, discriminated unions with string literal tags serve the same purpose. In C, you accept the manual discipline or layer macros on top.

## Production-quality code

### A JSON-ish value type

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { J_NULL, J_BOOL, J_NUMBER, J_STRING, J_TYPE_COUNT } JType;

typedef struct JValue {
    JType type;
    union {
        int    boolean;
        double number;
        char  *string;
    } as;
} JValue;

JValue jval_null(void)     { return (JValue){ .type = J_NULL }; }
JValue jval_bool(int b)    { return (JValue){ .type = J_BOOL,   .as.boolean = !!b }; }
JValue jval_number(double n) { return (JValue){ .type = J_NUMBER, .as.number = n }; }

JValue jval_string(const char *s) {
    char *copy = malloc(strlen(s) + 1);
    if (!copy) return jval_null();
    strcpy(copy, s);
    return (JValue){ .type = J_STRING, .as.string = copy };
}

void jval_free(JValue *v) {
    if (v->type == J_STRING) {
        free(v->as.string);
        v->as.string = NULL;
    }
    v->type = J_NULL;
}

void jval_print(const JValue *v) {
    switch (v->type) {
        case J_NULL:   printf("null");              break;
        case J_BOOL:   printf(v->as.boolean ? "true" : "false"); break;
        case J_NUMBER: printf("%g", v->as.number);  break;
        case J_STRING: printf("\"%s\"", v->as.string); break;
        default:       printf("<?>");               break;
    }
}
```

Note: `jval_string` allocates a copy because the caller might pass a stack buffer that goes out of scope. The ownership rule is clear: `jval_string` allocates, `jval_free` releases.

### Safe bit reinterpretation

```c
#include <string.h>
#include <stdint.h>
#include <stdio.h>

void print_float_bits(float f) {
    uint32_t bits;
    memcpy(&bits, &f, sizeof bits);
    printf("float %.6f = 0x%08x\n", f, bits);
}
```

## Security notes

- **Reading the wrong union member**: in a protocol parser, reading `v.as.string` when `v.type` is `J_NUMBER` gives you a garbage pointer. Dereferencing it is a potential crash or read from an attacker-controlled address.
- **Tag desync from external data**: if you deserialize a tagged union from a file or network, always validate the tag is in range before accessing the union. An invalid tag value could skip all `switch` cases, leaving uninitialized data exposed.
- **String variant ownership**: if `J_STRING` owns a heap allocation and you forget to `jval_free` it, you leak memory. If you free it twice (e.g., after copying the struct by value), you have a double-free vulnerability.

## Performance notes

- A tagged union is typically 4 bytes (tag) + size of largest member + padding. Compare to a struct holding all members: the union saves memory at scale.
- `switch` on the tag compiles to a jump table for small, dense enum ranges — O(1) dispatch.
- `memcpy` for type-punning is optimized away by modern compilers (GCC, Clang) into a zero-cost register move when the sizes match.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Reading a union member gives garbage | Wrote a different member; reading the wrong one | Always check the tag before accessing |
| Tag says `J_STRING` but string pointer is garbage | Updated union member without updating the tag | Write tag and member together, ideally via constructor functions |
| `sizeof(union)` is "too big" | Expected sum of members; it's actually the max | Remember: `sizeof` = max member + alignment padding |
| Memory leak with string variant | Forgot to free the heap-allocated string before overwriting | Call `jval_free` before reassigning a value |
| Crash when type-punning via union | Strict aliasing violation under `-fstrict-aliasing` | Use `memcpy` instead of reading a different union member |

## Practice

**Warm-up.** Define `union { int i; double d; }` and print `sizeof`. Predict the answer before running.

**Standard.** Implement the `Result` tagged union from the deep-dive with `success`, `failure`, and `result_print` functions. Test both paths from `main`.

**Bug hunt.** What's wrong with this code?

```c
union Value v;
v.i = 7;
printf("float: %f\n", v.f);
```

**Stretch.** Extend the `JValue` type to support `J_ARRAY` — a variant holding a pointer to a dynamic array of `JValue` plus its length. Implement `jval_array`, `jval_array_push`, and `jval_free` (recursive for arrays).

**Stretch++.** Implement a `reinterpret_bits` function that takes a `double`, uses `memcpy` to extract the raw `uint64_t`, and prints the sign bit, exponent, and mantissa fields of the IEEE-754 representation.

<details><summary>Solutions</summary>

**Bug hunt.** You wrote `v.i = 7` (storing 7 as an `int`), then read `v.f` (interpreting those bits as a `float`). The bit pattern `0x00000007` interpreted as IEEE-754 float is a tiny denormalized number, not `7.0`. This is implementation-defined or undefined behavior depending on compiler settings. Always track which member is active.

**Warm-up.**

```c
#include <stdio.h>

int main(void) {
    union { int i; double d; } u;
    printf("sizeof(union) = %zu\n", sizeof u);  /* 8 on most platforms */
    return 0;
}
```

**Standard.**

```c
typedef struct {
    enum { RES_OK, RES_ERR } tag;
    union {
        int ok_value;
        const char *err_message;
    } data;
} Result;

Result success(int v) {
    return (Result){ .tag = RES_OK, .data.ok_value = v };
}

Result failure(const char *msg) {
    return (Result){ .tag = RES_ERR, .data.err_message = msg };
}

void result_print(const Result *r) {
    switch (r->tag) {
        case RES_OK:  printf("ok: %d\n", r->data.ok_value); break;
        case RES_ERR: fprintf(stderr, "err: %s\n", r->data.err_message); break;
    }
}
```

</details>

## In plain terms (newbie lane)
If `Unions` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `sizeof(union { int i; double d; })` equals:
    (a) sum of members (12)  (b) max member + padding (8)  (c) always 4  (d) varies by call

2. A tagged union is:
    (a) a union alone  (b) an enum tag + union + struct wrapper  (c) a C++ template  (d) a macro

3. Reading a union member you didn't last write is:
    (a) always fine  (b) potentially UB / implementation-defined  (c) compile error  (d) auto-converts the value

4. The portable way to reinterpret bits between types is:
    (a) union type-punning  (b) `memcpy`  (c) pointer cast  (d) `reinterpret_cast`

5. Anonymous unions (no field name) arrived in:
    (a) C89  (b) C99  (c) C11  (d) C23

**Short answer:**

6. Why are tagged unions necessary in C but not in Rust?
7. Why use `memcpy` instead of union member aliasing for bit reinterpretation?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-c*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [05-unions — mini-project](mini-projects/05-unions-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A union overlays multiple types at the same memory address — it's as large as its biggest member.
- Always pair a union with an enum tag to create a *tagged union* — C's version of a sum type.
- Never read a union member you didn't last write; for bit reinterpretation, use `memcpy`.
- Tagged unions are the foundation of AST nodes, VM values, protocol messages, and configuration variants in C.

## Further reading

- C11 standard, section 6.7.2.1 — struct and union specifiers.
- *Crafting Interpreters*, Robert Nystrom — uses tagged unions extensively for the Lox VM.
- Next: [Stack and Heap](06-stack-and-heap.md).
