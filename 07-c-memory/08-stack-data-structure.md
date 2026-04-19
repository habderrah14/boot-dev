# Chapter 08 — Stack Data Structure

> "You've met the stack twice already — as a memory region and as a LIFO data structure in Python. Here you build the DS in C, which is a masterclass in heap allocation and pointer discipline."

## Learning objectives

By the end of this chapter you will be able to:

- Implement a dynamic-array-backed stack in C with a clean public API.
- Handle capacity growth with `realloc` and amortized O(1) push.
- Design error handling via return codes and out-parameters.
- Hide implementation details behind an opaque pointer.
- Reason about how to make a data structure generic using macros or `void *`.

## Prerequisites & recap

- [Stack and Heap](06-stack-and-heap.md) — `malloc`, `realloc`, `free`.
- [Advanced Pointers](07-advanced-pointers.md) — `T **` out-parameters.
- Familiarity with the stack as a LIFO concept (from your DSA module).

## The simple version

A stack is a container where you push items onto the top and pop them off in reverse order — last in, first out (LIFO). In Python, you'd use a list and call `append`/`pop`. In C, you build it yourself: a struct holding a heap-allocated array, a size counter, and a capacity counter. When the array fills up, you double it with `realloc`. When you're done, you free everything.

Building this from scratch teaches you the core skills of C library design: memory ownership, error signaling, encapsulation, and resource cleanup. Every C data structure — hash maps, queues, trees — follows the same patterns.

## Visual flow

```
  Stack internals (after push 10, 20, 30):

  Stack struct (on heap)
  ┌─────────────────────────────────────┐
  │  data ──▶ ┌────┬────┬────┬────┐    │
  │           │ 10 │ 20 │ 30 │ ?? │    │
  │           └────┴────┴────┴────┘    │
  │  size = 3                          │
  │  cap  = 4  (next push fits)        │
  └─────────────────────────────────────┘

  push(40):   data[3] = 40, size = 4   (fits in cap)
  push(50):   realloc to cap=8, then data[4] = 50, size = 5

  pop():      size--, return data[size] → 50
  pop():      size--, return data[size] → 40

  API flow:
  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
  │ new  │──▶│ push │──▶│ push │──▶│ pop  │──▶│ free │
  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘
  alloc       grow if     grow if   shrink      free data
  struct      needed      needed    size        + struct
```

*Caption: A stack backed by a dynamic array. Doubling on overflow gives amortized O(1) push.*

## Concept deep-dive

### The API — your public contract

```c
/* stack.h */
#pragma once
#include <stddef.h>

typedef struct Stack Stack;

Stack *stack_new(void);
void   stack_free(Stack *s);
int    stack_push(Stack *s, int value);
int    stack_pop(Stack *s, int *out);
int    stack_peek(const Stack *s, int *out);
size_t stack_len(const Stack *s);
```

Why `typedef struct Stack Stack;` with no body? This is the *opaque pointer* pattern. Callers can hold a `Stack *` but can't access its fields — they must go through the API. You can change the internal representation (linked list, ring buffer) without breaking callers.

Why return `int` from `push` and `pop`? Because C has no exceptions. Return 0 for success, -1 for failure (OOM on push, empty on pop). The actual value comes through an out-parameter (`int *out`). This is the standard C error-handling convention.

### The implementation

```c
/* stack.c */
#include <stdlib.h>
#include "stack.h"

struct Stack {
    int   *data;
    size_t size;
    size_t cap;
};

Stack *stack_new(void) {
    Stack *s = calloc(1, sizeof *s);
    return s;
}

void stack_free(Stack *s) {
    if (!s) return;
    free(s->data);
    free(s);
}

static int ensure_cap(Stack *s) {
    if (s->size < s->cap) return 0;
    size_t new_cap = s->cap ? s->cap * 2 : 8;
    int *tmp = realloc(s->data, new_cap * sizeof *tmp);
    if (!tmp) return -1;
    s->data = tmp;
    s->cap  = new_cap;
    return 0;
}

int stack_push(Stack *s, int value) {
    if (ensure_cap(s) != 0) return -1;
    s->data[s->size++] = value;
    return 0;
}

int stack_pop(Stack *s, int *out) {
    if (s->size == 0) return -1;
    *out = s->data[--s->size];
    return 0;
}

int stack_peek(const Stack *s, int *out) {
    if (s->size == 0) return -1;
    *out = s->data[s->size - 1];
    return 0;
}

size_t stack_len(const Stack *s) {
    return s->size;
}
```

### The doubling strategy

Why double instead of adding a fixed amount (say, +10)?

With fixed growth, pushing n elements triggers n/10 reallocations, each copying all previous elements. Total work: O(n²). With doubling, you trigger log₂(n) reallocations. The total copy work across all pushes is n + n/2 + n/4 + ... ≈ 2n = O(n). Per push: amortized O(1).

Shrinking (halving capacity when `size < cap/4`) is optional. Most workloads don't benefit, and it adds complexity. Only implement it if memory pressure is a real concern.

### Error handling conventions

| Return value | Meaning |
|---|---|
| `0` | Success |
| `-1` | Error (OOM, empty, invalid argument) |
| Pointer | `NULL` on failure, valid pointer on success |

The caller decides how to react. For a stack in a server, you might log and continue. For a stack in a safety-critical system, you might abort.

### Making it generic

Option 1 — **void * elements**:

```c
typedef struct GStack GStack;
GStack *gstack_new(void);
int     gstack_push(GStack *s, void *elem);
void   *gstack_pop(GStack *s);
```

Simple, but you lose type safety and pay an extra pointer per element.

Option 2 — **macros (type-safe code generation)**:

```c
#define STACK_DECL(T, prefix)                        \
    typedef struct { T *data; size_t size, cap; }    \
    prefix##_Stack;                                  \
    int prefix##_push(prefix##_Stack *s, T value);   \
    /* ... */
```

Ugly, but type-safe and zero overhead — the compiler generates specialized code for each type. This is how production C libraries like `stb` and `klib` work.

## Why these design choices

**Why opaque pointers?** Encapsulation. If you expose `struct Stack { int *data; ... }` in the header, callers can (and will) reach in and modify `size` directly. Now you can't add thread safety or change the backing store without breaking them. Opaque pointers enforce the API boundary.

**Why not return the popped value directly?** Because you need to signal "stack is empty" somehow. Returning a sentinel value (like -1 or INT_MIN) reduces the usable range of integers. Out-parameters + return codes keep the error channel separate from the data channel.

**When would you pick differently?** In C++, `std::stack<int>` gives you templates, RAII, and exceptions. In Rust, `Vec<T>` handles the backing array and drop semantics automatically. The C approach trades convenience for control.

## Production-quality code

### Complete stack module with tests

`stack.h` — as shown in the API section above.

`stack.c` — as shown in the implementation section above.

`test_stack.c`:

```c
#include <assert.h>
#include <stdio.h>
#include "stack.h"

int main(void) {
    Stack *s = stack_new();
    assert(s != NULL);
    assert(stack_len(s) == 0);

    for (int i = 0; i < 1000; i++)
        assert(stack_push(s, i) == 0);
    assert(stack_len(s) == 1000);

    int val;
    assert(stack_peek(s, &val) == 0 && val == 999);

    for (int i = 999; i >= 0; i--) {
        assert(stack_pop(s, &val) == 0);
        assert(val == i);
    }
    assert(stack_len(s) == 0);
    assert(stack_pop(s, &val) == -1);

    stack_free(s);
    printf("All tests passed.\n");
    return 0;
}
```

### Balanced parentheses checker

```c
#include <stdio.h>
#include "stack.h"

int balanced(const char *s) {
    Stack *st = stack_new();
    if (!st) return -1;

    int ok = 1;
    for (; *s && ok; s++) {
        if (*s == '(' || *s == '[' || *s == '{') {
            stack_push(st, *s);
        } else if (*s == ')' || *s == ']' || *s == '}') {
            int top;
            if (stack_pop(st, &top) != 0) { ok = 0; break; }
            if ((*s == ')' && top != '(') ||
                (*s == ']' && top != '[') ||
                (*s == '}' && top != '{')) { ok = 0; }
        }
    }
    if (ok && stack_len(st) != 0) ok = 0;

    stack_free(st);
    return ok;
}
```

## Security notes

- **Unchecked push on OOM**: if `stack_push` returns -1 and the caller ignores it, the value is silently dropped. In security-sensitive code (e.g., an expression parser), this could lead to incorrect evaluation.
- **Stack used after free**: passing a freed `Stack *` to any API function is UB. Set the pointer to `NULL` after `stack_free` to convert use-after-free into a null-deref (which is at least deterministic on most OSes).

## Performance notes

- **Push**: amortized O(1). Worst-case single push is O(n) during reallocation, but this happens only O(log n) times over n pushes.
- **Pop/Peek**: O(1) always — just decrement `size` or read `data[size-1]`.
- **Memory overhead**: at worst 50% unused capacity (right after a doubling). Compared to a linked-list stack (one pointer overhead per element), the array-backed stack is far more cache-friendly.
- **`calloc(1, sizeof *s)`** zeros the struct, giving `data = NULL`, `size = 0`, `cap = 0`. `realloc(NULL, n)` behaves like `malloc(n)`, so the first push just works.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Crash after `pop` on empty stack | Didn't check return code; dereferenced garbage `out` | Always check `stack_pop` return value before using `*out` |
| Memory leak | Freed the `Stack` struct but not `data`, or forgot `stack_free` entirely | `stack_free` must free `data` first, then the struct |
| Old pointers into the stack's data become invalid | `realloc` moved the buffer; old `int *` into data is dangling | Never cache pointers into the stack's internal array |
| `realloc` failure loses the old buffer | Wrote `s->data = realloc(s->data, ...)` — if it returns NULL, old data is lost | Use a temporary variable for the `realloc` result |
| Stack appears to have wrong values after resize | Forgot to copy or used wrong size in `realloc` | Use `new_cap * sizeof *tmp` — `sizeof *tmp` matches element type automatically |

## Practice

**Warm-up.** Implement `void stack_clear(Stack *s)` that resets `size` to 0 without freeing or shrinking the internal array.

**Standard.** Implement the full stack API (new, push, pop, peek, len, free). Test by pushing 20 values and popping them in reverse.

**Bug hunt.** What goes wrong if `ensure_cap` does `s->data = realloc(s->data, new_cap * sizeof *s->data)` instead of using a temporary?

**Stretch.** Add shrink logic: when `size < cap / 4`, halve the capacity (but never below 8). Test that memory usage decreases after many pops.

**Stretch++.** Port the stack to use `void *` elements and `size_t elem_size`, supporting any type. Internally, store a `char *` buffer and use `memcpy` for element access.

<details><summary>Solutions</summary>

**Bug hunt.** If `realloc` fails and returns `NULL`, writing `s->data = NULL` loses the only pointer to the existing allocation. The old data is leaked and the stack is corrupted. Always assign to a temporary: `int *tmp = realloc(s->data, ...); if (!tmp) return -1; s->data = tmp;`.

**Warm-up.**

```c
void stack_clear(Stack *s) {
    s->size = 0;
}
```

**Stretch++.**

```c
typedef struct {
    char  *data;
    size_t elem_size;
    size_t size, cap;
} GStack;

GStack *gstack_new(size_t elem_size) {
    GStack *s = calloc(1, sizeof *s);
    if (s) s->elem_size = elem_size;
    return s;
}

int gstack_push(GStack *s, const void *elem) {
    if (s->size == s->cap) {
        size_t new_cap = s->cap ? s->cap * 2 : 8;
        char *tmp = realloc(s->data, new_cap * s->elem_size);
        if (!tmp) return -1;
        s->data = tmp;
        s->cap = new_cap;
    }
    memcpy(s->data + s->size * s->elem_size, elem, s->elem_size);
    s->size++;
    return 0;
}

int gstack_pop(GStack *s, void *out) {
    if (s->size == 0) return -1;
    s->size--;
    memcpy(out, s->data + s->size * s->elem_size, s->elem_size);
    return 0;
}

void gstack_free(GStack *s) {
    if (!s) return;
    free(s->data);
    free(s);
}
```

</details>

## In plain terms (newbie lane)
If `Stack Data Structure` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Amortized push cost of a doubling-array stack:
    (a) O(1)  (b) O(n)  (c) O(log n)  (d) O(n²)

2. If `realloc` returns NULL:
    (a) the original pointer is freed  (b) the original pointer remains valid  (c) UB  (d) memory is zeroed

3. `stack_free(NULL)` should:
    (a) crash  (b) be a safe no-op  (c) leak memory  (d) assert

4. `calloc(1, sizeof *s)`:
    (a) allocates one zeroed struct  (b) allocates 1 byte  (c) crashes  (d) is identical to `malloc`

5. An opaque struct (`typedef struct Stack Stack;` in header):
    (a) hides implementation from callers  (b) makes code slower  (c) is illegal in C  (d) requires C++

**Short answer:**

6. Why is doubling better than increment-by-one for capacity growth?
7. What is the caller's contract if `stack_push` returns -1?

*Answers: 1-a, 2-b, 3-b, 4-a, 5-a*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [08-stack-data-structure — mini-project](mini-projects/08-stack-data-structure-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A stack in C is a struct wrapping a dynamic array with `push`, `pop`, `peek`, and `free` operations.
- Doubling capacity growth gives amortized O(1) push with O(log n) reallocations.
- Return int status codes for error handling; use out-parameters for values.
- The opaque pointer pattern hides internals; generic versions use `void *` or macros.

## Further reading

- Linux kernel `include/linux/list.h` — an intrusive doubly-linked list, another approach to data structure design in C.
- *Algorithms in C*, Robert Sedgewick — classic C data structure implementations.
- Next: [Objects](09-objects.md).
