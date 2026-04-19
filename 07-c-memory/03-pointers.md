# Chapter 03 — Pointers

> "A pointer is a number that names a memory address. Every mystery in C comes from this one idea."

## Learning objectives

By the end of this chapter you will be able to:

- Declare, initialize, and dereference pointers of any type.
- Pass data by pointer to modify it across function boundaries.
- Handle null and dangling pointers safely.
- Apply `const` correctness to document intent and catch bugs at compile time.
- Use pointer arithmetic to traverse arrays.
- Read and write function pointer declarations.

## Prerequisites & recap

- [Structs](02-structs.md) — you've already seen `->` for accessing fields through a pointer. Now you'll understand what's really happening under the hood.

## The simple version

Every variable lives somewhere in memory, and that "somewhere" has an address — a number like `0x7ffd4a3c`. A pointer is a variable that holds one of these addresses. The `&` operator asks "where does this live?", and the `*` operator asks "what's stored at this address?" That's the entire model.

Why care? Because C doesn't let you return two values from a function, doesn't resize arrays for you, and doesn't copy large data around for free. Pointers solve all of these problems by letting you share access to data without copying it. But sharing access also means sharing *responsibility* — if you hold a pointer to memory that no longer exists, you have a dangling pointer, and your program's behavior becomes undefined.

## Visual flow

```
  Stack frame of main()              Heap (or another frame)
  ┌──────────────────────┐
  │  int x = 20          │◄─────────────── *p reads/writes here
  │  addr: 0x7ffd0040    │
  ├──────────────────────┤
  │  int *p = 0x7ffd0040 │───── p holds ──▶ the address of x
  │  addr: 0x7ffd0048    │
  └──────────────────────┘

  &x  →  0x7ffd0040    (address-of)
  *p  →  20             (dereference)
  *p = 30  →  x is now 30
```

*Caption: A pointer `p` stores the address of `x`. Dereferencing `p` reads or writes `x`.*

## Concept deep-dive

### Declaration and dereferencing

```c
int x = 10;
int *p = &x;        /* p holds the address of x */
printf("%d\n", *p); /* 10 — dereference: "what's at this address?" */
*p = 20;            /* writes to x through p */
printf("%d\n", x);  /* 20 */
```

Read `int *p` as "p is a pointer to int." The `*` in the declaration means "pointer type." The `*` in an expression means "dereference." Same symbol, two contexts.

Why does this two-step dance exist? Because functions in C receive copies of their arguments. Without pointers, a function can never modify the caller's variables. With pointers, you pass the *address*, and the function reaches back into the caller's memory.

### Null pointers

```c
int *p = NULL;
if (p != NULL) {
    printf("%d\n", *p);
}
```

`NULL` is a sentinel meaning "this pointer doesn't point anywhere valid." Dereferencing `NULL` is undefined behavior — on most OSes it triggers a segfault. Always check before dereferencing a pointer you didn't just create yourself.

C23 introduces `nullptr` as a type-safe null pointer constant. Prefer it when your compiler supports C23.

### Passing to functions

```c
void increment(int *n) {
    (*n)++;
}

int x = 5;
increment(&x);
printf("%d\n", x);  /* 6 */
```

Without the pointer, `increment` would receive a copy of `5`, increment the copy, and the caller's `x` would stay `5`. This is why `scanf` needs `&x` — it must write into *your* variable, not its own copy.

### `const` correctness

| Declaration | Meaning |
|---|---|
| `const int *p` | Pointee is read-only through `p`. Can't write `*p = 5`. |
| `int * const p` | Pointer itself is constant. Can't repoint `p = &y`. |
| `const int * const p` | Both: can't modify pointee or redirect pointer. |

Why bother? `const` is a *contract* between you and future readers (including the compiler). When a function takes `const int *p`, it promises not to modify the data. The compiler enforces this, turning accidental mutations into compile-time errors.

**Read rule:** read the declaration right-to-left. `const int *p` → "p is a pointer to int const" → pointee is const. `int * const p` → "p is a const pointer to int" → pointer is const.

### Pointer arithmetic

```c
int a[5] = {10, 20, 30, 40, 50};
int *p = a;             /* a decays to &a[0] */
printf("%d\n", *(p+2)); /* 30 */
p++;                    /* now points to a[1] */
printf("%d\n", *p);     /* 20 */
```

Why does `p + 2` jump by 8 bytes (on a system with 4-byte ints) and not 2 bytes? Because pointer arithmetic advances by `sizeof(*p)`. The compiler multiplies for you. This is why `a[i]` is exactly equivalent to `*(a + i)` — array indexing is syntactic sugar over pointer arithmetic.

### Array decay

When you use an array name in most expressions, it "decays" to a pointer to its first element. This is why you can pass an array to a function expecting a pointer. The exception: `sizeof(a)` gives the full array size, not a pointer size (but only in the scope where `a` was declared as an array).

### Function pointers

```c
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int (*op)(int, int) = add;
printf("%d\n", op(2, 3));   /* 5 */

op = sub;
printf("%d\n", op(2, 3));   /* -1 */
```

Why do these exist? Callbacks, dispatch tables, plugin architectures — anywhere you want to choose behavior at runtime. The C standard library's `qsort` takes a function pointer so it can sort any type.

### Dangling pointers

```c
int *make_bad(void) {
    int x = 42;
    return &x;   /* x dies when this function returns */
}

int *p = make_bad();
printf("%d\n", *p); /* UB: p points to dead memory */
```

The local `x` lived on the stack frame of `make_bad`. When the function returned, that frame was popped. `p` now points to recycled memory. This is the most common pointer bug and one of the hardest to track down, because the memory often still contains the old value — until something else overwrites it.

## Why these design choices

**Why are pointers exposed at all?** Many languages hide pointers behind references or garbage-collected handles. C exposes them because it was designed to write operating systems, where you *need* to manipulate specific hardware addresses, implement memory allocators, and control exactly where data lives.

**Why is `const` opt-in rather than default?** Historical accident. C was designed in 1972; `const` was added later (C89). If C were designed today, immutability would likely be the default. Rust took this lesson — `let` bindings are immutable unless you say `let mut`.

**When would you pick differently?** Rust references (`&T` / `&mut T`) enforce at compile time that you can't have a dangling pointer, a data race, or simultaneous mutable and immutable access. If your project doesn't need C's ecosystem or ABI compatibility, Rust is strictly safer for pointer-heavy code.

## Production-quality code

### Swap function

```c
void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}
```

### Safe parse with output parameter

```c
#include <errno.h>
#include <limits.h>
#include <stdlib.h>

int parse_int(const char *s, int *out) {
    char *end;
    errno = 0;
    long val = strtol(s, &end, 10);
    if (end == s || *end != '\0') return -1;
    if (errno == ERANGE || val < INT_MIN || val > INT_MAX) return -1;
    *out = (int)val;
    return 0;
}
```

This is how production C handles parsing: `strtol` + range check + output parameter. Compare to `atoi`, which silently returns 0 on failure.

### `strlen` via pointer arithmetic

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}
```

Pointer subtraction gives the number of *elements* (not bytes) between two pointers into the same array. The `const` on both pointers signals that this function doesn't modify the string.

## Security notes

- **Null pointer dereference**: can crash your server or, on some embedded systems without memory protection, corrupt data at address 0. Always validate pointers from untrusted sources (user input, config parsing, malloc results).
- **Dangling pointer exploitation**: use-after-free is one of the most common vulnerability classes (CWE-416). An attacker can arrange for the freed memory to be reallocated with controlled data, then trigger the dangling dereference to execute arbitrary code.
- **Function pointer overwrite**: if an attacker can write past a buffer and overwrite a function pointer on the stack or in a struct, they redirect control flow. This is the basis of many ROP (return-oriented programming) attacks.

## Performance notes

- Dereferencing a pointer costs one memory load (or zero, if the compiler can prove the value is already in a register). Pointer-heavy code can be slower than value-based code due to *cache misses* — following a pointer sends the CPU to an unpredictable memory location.
- `const` enables compiler optimizations: if the compiler knows a value can't change through a pointer, it can cache it in a register across function calls instead of reloading from memory.
- Pointer arithmetic is free at the hardware level — the multiplication by element size happens at compile time.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Segfault on function return value | Returned pointer to a local variable (dangling) | Allocate on the heap or return by value |
| Function doesn't modify caller's variable | Passed by value instead of by pointer | Change to pointer parameter, pass `&x` |
| `*p++` increments the wrong thing | `*p++` is `*(p++)` — increments the pointer, not the value | Use `(*p)++` to increment the pointed-to value |
| Compiler warns "incompatible pointer type" | Passed `int *` where `const int *` expected (or vice versa) | Match the `const` qualifier; don't cast away `const` |
| Crash in release build but not debug | Dangling pointer: debug build zeros memory, release doesn't | Run under AddressSanitizer (`-fsanitize=address`) |

## Practice

**Warm-up.** Write `void fill(int *arr, size_t n, int value)` that sets every element of `arr` to `value`. Test it from `main`.

**Standard.** Implement `my_strlen` using pointer arithmetic (no `[]` indexing). Compare your result against the standard `strlen`.

**Bug hunt.** This function is called from `main` and the result is printed. What goes wrong?

```c
int *make_answer(void) {
    int x = 42;
    return &x;
}
```

**Stretch.** Implement `void for_each(int *arr, size_t n, void (*fn)(int))` that calls `fn` on each element. Test with a function that prints and one that doubles (using `int *`-based variant).

**Stretch++.** Write a function `double average(const int *arr, size_t n)` that computes the mean. Use `const` everywhere appropriate. Add a `parse_int` function with an output parameter (`int *out`) and use it to parse command-line arguments before computing the average.

<details><summary>Solutions</summary>

**Bug hunt.** `x` is a local variable on the stack. When `make_answer` returns, its stack frame is reclaimed. The returned pointer now points to memory that may be reused by the next function call. Dereferencing it is undefined behavior — it might print 42 today, garbage tomorrow, or crash on a different compiler.

**Standard.**

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}
```

**Warm-up.**

```c
void fill(int *arr, size_t n, int value) {
    for (size_t i = 0; i < n; i++) {
        arr[i] = value;
    }
}
```

**Stretch.**

```c
void for_each(int *arr, size_t n, void (*fn)(int)) {
    for (size_t i = 0; i < n; i++) {
        fn(arr[i]);
    }
}

void print_int(int x) { printf("%d\n", x); }

int main(void) {
    int nums[] = {1, 2, 3, 4, 5};
    for_each(nums, 5, print_int);
    return 0;
}
```

</details>

## In plain terms (newbie lane)
If `Pointers` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `int *p = &x;` means:
    (a) `p` is a copy of `x`  (b) `p` holds the address of `x`  (c) compile error  (d) undefined

2. `*p = 10` does:
    (a) changes `p` itself  (b) writes 10 to the location `p` points to  (c) illegal without `const`  (d) nothing

3. Dereferencing a null pointer:
    (a) returns 0  (b) is UB, usually a segfault  (c) throws an exception  (d) prints an error

4. `const int *p` means:
    (a) `p` is const, pointee is not  (b) pointee is const, `p` is not  (c) both are const  (d) neither is const

5. In an expression, an array name `arr` decays to:
    (a) the full array  (b) `&arr[0]`  (c) a copy of the array  (d) `NULL`

**Short answer:**

6. Why can't you return a pointer to a local variable?
7. When would you use `int * const p` vs. `const int *p`?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-pointers — mini-project](mini-projects/03-pointers-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- A pointer is a variable that holds a memory address. `&` takes the address; `*` dereferences it.
- Pass by pointer when you need a function to modify the caller's data, or to avoid copying large values.
- `const` correctness documents and enforces read-only contracts at compile time.
- Dangling pointers (returning `&local`, use-after-free) are C's most dangerous class of bugs — sanitizers are your best defense.

## Further reading

- *Expert C Programming: Deep C Secrets*, Peter van der Linden — thorough treatment of pointer subtleties.
- *Understanding and Using C Pointers*, Richard Reese — dedicated pointer deep-dive.
- Next: [Enums](04-enums.md).
