# Chapter 07 — Advanced Pointers

> "Pointers to pointers, arrays of pointers, and pointers to functions: the building blocks of every serious C abstraction."

## Learning objectives

By the end of this chapter you will be able to:

- Use pointer-to-pointer (`T **`) for out-parameters that allocate and for 2-D data.
- Allocate and free 2-D arrays using both row-wise and flat-buffer strategies.
- Work confidently with `char **` (argv-style string arrays).
- Use `void *` for generic containers and understand its limitations.
- Read and write `qsort`-compatible comparator functions.

## Prerequisites & recap

- [Pointers](03-pointers.md) — single-level pointers, `&`, `*`, pointer arithmetic.
- [Stack and Heap](06-stack-and-heap.md) — `malloc`, `realloc`, `free`.

## The simple version

A pointer-to-pointer is exactly what it sounds like: a variable that stores the address of another pointer. You need this in two situations. First, when a function needs to allocate memory and hand the result back to the caller — the function needs to modify the caller's pointer, so it needs the *address of that pointer*. Second, when you want a 2-D array on the heap — an array of pointers, each pointing to a row.

`void *` is C's escape hatch for generic programming. It says "this is a pointer to *something*, but I'm not telling you the type." Functions like `qsort` and `bsearch` use `void *` so they can sort any type — you provide a comparator function pointer that knows the actual type.

## Visual flow

```
  Pointer-to-pointer (T**):           argv (char **):

  pp ──▶ p ──▶ x = 7                  argv ──┬──▶ "./app\0"
                                              ├──▶ "-v\0"
  int x = 7;                                 ├──▶ "file.txt\0"
  int *p = &x;                               └──▶ NULL
  int **pp = &p;
  **pp == 7

  2-D array (row-wise):               2-D array (flat buffer):

  grid ──┬──▶ [0][1][2]               grid ──▶ [0,0][0,1][0,2]
         ├──▶ [3][4][5]                         [1,0][1,1][1,2]
         └──▶ [6][7][8]                         [2,0][2,1][2,2]
                                       access: grid[r * cols + c]
  rows can be non-contiguous           contiguous; one malloc, one free
```

*Caption: `T **` adds a level of indirection. 2-D arrays can be row-wise (flexible) or flat (cache-friendly).*

## Concept deep-dive

### Pointer to pointer

```c
int x = 7;
int *p = &x;
int **pp = &p;
printf("%d\n", **pp);  /* 7 */
```

Three levels: `pp` holds the address of `p`; `p` holds the address of `x`; `**pp` dereferences twice to reach `x`.

### Use case 1: callee-allocates out-parameter

When a function needs to allocate memory and return it to the caller, the caller's pointer must be modified. Since C passes everything by value, you pass a pointer *to* the pointer:

```c
int make_buffer(size_t n, int **out) {
    *out = malloc(n * sizeof **out);
    return *out ? 0 : -1;
}

int *buf;
if (make_buffer(10, &buf) == 0) {
    buf[0] = 42;
    free(buf);
}
```

Why not just return the pointer? You can — and often should. But when a function needs to return *two* things (e.g., an error code *and* a pointer), out-parameters are the C idiom.

### Use case 2: `char **argv`

```c
int main(int argc, char **argv) {
    for (int i = 0; i < argc; i++)
        printf("arg[%d] = %s\n", i, argv[i]);
}
```

`argv` is a pointer to an array of `char *` strings. `argv[i]` is the i-th string. `argv[argc]` is guaranteed to be `NULL`.

### 2-D arrays on the heap

**Row-wise allocation** (array of pointers to rows):

```c
int **grid = malloc(rows * sizeof *grid);
if (!grid) abort();
for (size_t r = 0; r < rows; r++) {
    grid[r] = calloc(cols, sizeof **grid);
    if (!grid[r]) abort();
}

grid[1][2] = 42;  /* natural 2-D indexing */

for (size_t r = 0; r < rows; r++) free(grid[r]);
free(grid);
```

Flexible (rows can be different lengths — "jagged array"), but rows are scattered in memory. Cache-unfriendly for sequential access.

**Flat buffer** (contiguous):

```c
int *grid = malloc(rows * cols * sizeof *grid);
if (!grid) abort();

grid[r * cols + c] = 42;

free(grid);
```

One allocation, one free, contiguous memory. Cache-friendly. Preferred when the shape is rectangular and known.

Why does contiguous memory matter? Modern CPUs load data in cache lines (64 bytes). When you access `grid[0][0]`, the hardware prefetches `grid[0][1]` through `grid[0][7]`. With row-wise allocation, each row starts at a random heap address, defeating the prefetcher.

### Function pointers and `qsort`

```c
int cmp_int(const void *a, const void *b) {
    const int *ia = a, *ib = b;
    return (*ia > *ib) - (*ia < *ib);
}

int arr[] = {3, 1, 4, 1, 5};
qsort(arr, 5, sizeof *arr, cmp_int);
```

`qsort` is generic because it takes `void *` for the array, `size_t` for element size, and a comparator function pointer. It never knows the type — it just shuffles bytes and asks the comparator for ordering.

Why the `(a > b) - (a < b)` pattern? The naive `return *ia - *ib` overflows if the values are large (e.g., `INT_MAX - (-1)`). The comparison-based pattern is always safe.

### `void *` — the generic pointer

`void *` means "pointer to something, type unknown." Rules:

- No arithmetic: the compiler doesn't know the element size.
- Implicit conversion to/from any object pointer type in C (no cast needed).
- In C++, you need an explicit cast — this is one reason C and C++ are different languages.

```c
void *mem = malloc(100);
int *arr = mem;  /* implicit conversion in C */
```

### Sorting strings

```c
int cmp_str(const void *a, const void *b) {
    const char *const *sa = a;
    const char *const *sb = b;
    return strcmp(*sa, *sb);
}

char *names[] = {"Charlie", "Ada", "Bob"};
qsort(names, 3, sizeof *names, cmp_str);
```

The type is `const char *const *` because `qsort` passes *pointers to elements* — each element is a `char *`, so you receive a `char **` (cast from `void *`), and the double `const` protects both the pointer and the string.

## Why these design choices

**Why `void *` instead of generics?** C was designed before parametric polymorphism was well understood. `void *` gives you runtime generics with no compiler support — at the cost of type safety. C++ added templates. Rust added generics with monomorphization. C's approach is simpler but error-prone.

**Why two 2-D styles?** Row-wise allocation predates the flat-buffer pattern and maps naturally to `grid[r][c]` syntax. Flat buffers are newer idiom wisdom driven by cache-performance research. Both have valid use cases.

**When would you pick differently?** In C++, use `std::vector<std::vector<int>>` or a flat `std::vector<int>` with index arithmetic. In Rust, `Vec<Vec<i32>>` or `ndarray`. In NumPy, contiguous flat buffers are the default — C's flat style is exactly what NumPy does under the hood.

## Production-quality code

### Safe grid allocation with cleanup on failure

```c
#include <stdlib.h>

int **grid_new(size_t rows, size_t cols) {
    int **g = malloc(rows * sizeof *g);
    if (!g) return NULL;

    for (size_t r = 0; r < rows; r++) {
        g[r] = calloc(cols, sizeof **g);
        if (!g[r]) {
            for (size_t i = 0; i < r; i++) free(g[i]);
            free(g);
            return NULL;
        }
    }
    return g;
}

void grid_free(int **g, size_t rows) {
    if (!g) return;
    for (size_t r = 0; r < rows; r++) free(g[r]);
    free(g);
}
```

The failure path frees all previously allocated rows before returning `NULL`. This is a common pattern — allocate in a loop, on failure unwind what you've done so far.

### Sorting an array of structs

```c
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct { char name[64]; int age; } Person;

int cmp_by_age(const void *a, const void *b) {
    const Person *pa = a, *pb = b;
    return (pa->age > pb->age) - (pa->age < pb->age);
}

int cmp_by_name(const void *a, const void *b) {
    const Person *pa = a, *pb = b;
    return strcmp(pa->name, pb->name);
}

int main(void) {
    Person people[] = {
        {"Charlie", 30}, {"Ada", 25}, {"Bob", 35}
    };
    size_t n = sizeof people / sizeof people[0];

    qsort(people, n, sizeof *people, cmp_by_name);
    for (size_t i = 0; i < n; i++)
        printf("%s (%d)\n", people[i].name, people[i].age);

    return 0;
}
```

## Security notes

- **Missing inner frees**: if you free the outer `grid` pointer but not the inner rows, you leak memory proportional to `rows * cols`. In a long-running server, this eventually causes OOM.
- **`void *` cast errors**: casting a `void *` to the wrong type is UB. The compiler can't help you — `void *` erases all type information.
- **`qsort` comparator returning wrong sign**: a buggy comparator can cause `qsort` to loop forever or access out-of-bounds memory. Always test comparators on edge cases (equal elements, min/max values).

## Performance notes

- **Flat 2-D buffer** is 2–10× faster than row-wise for sequential traversal due to cache locality. For random access, the difference is smaller.
- **`qsort`** is O(n log n) average, O(n²) worst case. Some implementations use introsort (quicksort + heapsort fallback) to guarantee O(n log n).
- **`void *` indirection**: generic containers using `void *` require one extra pointer dereference per element access. For hot paths, type-specific implementations (via macros or code generation) can be 10–30% faster.
- **`sizeof *p`** is always a compile-time constant — using it instead of `sizeof(type)` costs nothing and prevents mismatches if the type changes.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Memory leak after freeing a 2-D array | Freed the outer pointer but not the inner row pointers | Free inner allocations first, then the outer array |
| `sizeof(p)` returns 8 instead of array size | `sizeof` a pointer gives pointer size, not what it points to | Use `sizeof *p` for element size; track array length separately |
| `void *p; p + 1;` won't compile | Can't do arithmetic on `void *` — element size unknown | Cast to `char *` or a typed pointer first |
| `qsort` produces wrong order | Comparator returns wrong sign or overflows on subtraction | Use `(a > b) - (a < b)` pattern instead of `a - b` |
| Crash on `grid[r][c]` with flat buffer | Used flat buffer but indexed like row-wise | Use `grid[r * cols + c]` for flat buffers |

## Practice

**Warm-up.** Allocate, use, and free a 3×3 int grid using the flat-buffer style. Fill with the values 1–9 and print as a matrix.

**Standard.** Write `int read_line(char **out)` that reads one line from stdin into a heap-allocated buffer. Caller must free the result.

**Bug hunt.** Why doesn't this work?

```c
void *p = malloc(10);
int x = *(p + 4);  /* compiler error */
```

**Stretch.** Sort an array of `Person` structs by a chosen field (name or age) using `qsort` with a function pointer. Let the user pick the sort key via a command-line argument.

**Stretch++.** Implement a generic min-heap over `void *` elements: `heap_new(size_t elem_size, int (*cmp)(const void *, const void *))`, `heap_push`, `heap_pop`. Test with both `int` and `char *` comparators.

<details><summary>Solutions</summary>

**Bug hunt.** `void *` has no known element size, so `p + 4` is illegal — the compiler doesn't know how many bytes "4 elements" is. Fix: cast to `char *` for byte arithmetic (`*(int *)((char *)p + 4)`), or better, cast to the target type first (`int *ip = p; int x = ip[1];`).

**Warm-up.**

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *grid = malloc(3 * 3 * sizeof *grid);
    if (!grid) return 1;

    for (int i = 0; i < 9; i++) grid[i] = i + 1;

    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++)
            printf("%2d ", grid[r * 3 + c]);
        printf("\n");
    }

    free(grid);
    return 0;
}
```

**Standard.**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int read_line(char **out) {
    size_t cap = 64, len = 0;
    char *buf = malloc(cap);
    if (!buf) return -1;

    int c;
    while ((c = fgetc(stdin)) != EOF && c != '\n') {
        if (len + 1 >= cap) {
            cap *= 2;
            char *tmp = realloc(buf, cap);
            if (!tmp) { free(buf); return -1; }
            buf = tmp;
        }
        buf[len++] = (char)c;
    }
    buf[len] = '\0';

    if (len == 0 && c == EOF) { free(buf); *out = NULL; return -1; }
    *out = buf;
    return 0;
}
```

</details>

## In plain terms (newbie lane)
If `Advanced Pointers` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `int **p` is:
    (a) a 2-D array  (b) a pointer to a pointer to int  (c) illegal  (d) same as `int *`

2. A common reason for a `T **` parameter is:
    (a) coding style  (b) callee-allocates output where the callee sets the caller's pointer  (c) faster copies  (d) const correctness

3. For cache-friendly 2-D access, prefer:
    (a) array of pointers  (b) contiguous flat buffer  (c) linked list  (d) hash table

4. `qsort`'s comparator returns:
    (a) `bool`  (b) negative, zero, or positive `int` indicating order  (c) the lesser element  (d) `void`

5. `void *` arithmetic is:
    (a) legal in standard C  (b) illegal — element size unknown  (c) always 1-byte steps  (d) implementation-defined

**Short answer:**

6. When is a flat-buffer 2-D array better than row-wise allocation?
7. What makes `qsort` generic despite C having no templates or generics?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [07-advanced-pointers — mini-project](mini-projects/07-advanced-pointers-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Pointer-to-pointer (`T **`) enables callee-allocated out-parameters and 2-D heap arrays.
- Prefer contiguous flat buffers for cache performance; use row-wise when rows have different lengths.
- `void *` and function pointers give C runtime generics — `qsort` is the canonical example.
- Always free inner allocations before outer ones, and use the safe comparator pattern `(a > b) - (a < b)`.

## Further reading

- `man 3 qsort`, `man 3 bsearch` — standard library generic algorithms.
- *C Interfaces and Implementations*, David Hanson — extensive use of `void *` generics.
- Next: [Stack Data Structure](08-stack-data-structure.md).
