# Chapter 04 — Enums

> "An enum is a named set of integer constants. It's how C says 'here is a closed list of choices.'"

## Learning objectives

By the end of this chapter you will be able to:

- Declare and use enums with explicit and auto-incremented values.
- Understand the underlying integer representation and its implications.
- Design bitmask (flag) enums using powers of two.
- Convert enums to strings and iterate over enum values.
- Use enums to build type-safer APIs.

## Prerequisites & recap

- [C Basics](01-c-basics.md) — types, `printf`, `switch`.

## The simple version

An enum gives names to a list of integer constants. Instead of scattering magic numbers like `0`, `1`, `2` through your code, you write `RED`, `GREEN`, `BLUE` — and the compiler maps them to integers for you. This makes your code readable, your `switch` statements exhaustive, and your intent clear.

The catch: C enums are just integers wearing a costume. The compiler won't stop you from assigning `42` to a `Color` variable or mixing enum types. They're a naming tool, not a type-safety tool — at least not until C23's `enum class`.

## Visual flow

```
  Auto-increment                Bitmask (powers of 2)

  enum Color {                  enum Perm {
    RED   = 0,                    READ  = 0b001  (1),
    GREEN = 1,                    WRITE = 0b010  (2),
    BLUE  = 2                     EXEC  = 0b100  (4)
  };                            };

  0   1   2                     Combine: READ | WRITE = 0b011 (3)
  ▼   ▼   ▼                    Test:    perms & READ  → true?
  R   G   B

  Sentinel pattern:             Switch dispatch:
  enum Day {                    switch (c) {
    MON, TUE, ..., SUN,           case RED:   ...
    DAY_COUNT  ← not a day        case GREEN: ...
  };                               case BLUE:  ...
  for (d = MON; d < DAY_COUNT)  }
```

*Caption: Enums map names to ints. Use auto-increment for sequential values, powers of two for combinable flags.*

## Concept deep-dive

### Basic declaration

```c
enum Color { RED, GREEN, BLUE };
enum Color c = GREEN;
```

Values auto-increment from 0: `RED = 0`, `GREEN = 1`, `BLUE = 2`. You can override:

```c
enum Status { OK = 200, NOT_FOUND = 404, SERVER_ERROR = 500 };
```

Why start from 0? Convention from C's origins. Zero is the "default" value for uninitialized static storage, so `RED` being 0 means a zero-initialized `Color` is a valid value.

### `typedef` to drop the tag

```c
typedef enum { RED, GREEN, BLUE } Color;
Color c = BLUE;
```

Without `typedef`, every declaration would say `enum Color c`. The typedef creates a shorter alias. This is purely syntactic convenience.

### Enums are integers — and that's a problem

```c
Color c = 42;  /* compiler may not even warn */
```

C enums implicitly convert to and from `int`. There's no compile-time enforcement that a `Color` variable holds a valid color. This is why `switch` statements need a `default` case or `-Wswitch-enum` — future enum values added by a colleague won't be caught otherwise.

C23 introduces `enum class` for stricter typing (no implicit conversions). Until your toolchain supports it, discipline and compiler warnings are your safety net.

### Flags (bitmask enums)

When you need to combine options, use powers of two so each value occupies a single bit:

```c
typedef enum {
    PERM_READ  = 1 << 0,   /* 1 */
    PERM_WRITE = 1 << 1,   /* 2 */
    PERM_EXEC  = 1 << 2,   /* 4 */
} Perm;

Perm p = PERM_READ | PERM_WRITE;
if (p & PERM_READ)  { /* readable */ }
if (p & PERM_EXEC)  { /* executable */ }
```

Why powers of two? Because each flag occupies exactly one bit position. OR-ing them together sets multiple bits. AND-ing with a flag tests if that bit is set. Consecutive integers (0, 1, 2, 3) don't work because bit patterns overlap.

### Iteration via sentinel

```c
typedef enum { MON, TUE, WED, THU, FRI, SAT, SUN, DAY_COUNT } Day;

for (Day d = MON; d < DAY_COUNT; d++) {
    printf("day %d\n", d);
}
```

`DAY_COUNT` isn't a real day — it's a *sentinel* that always equals the number of values. This trick works only when values are sequential starting from 0.

### Enum-to-string mapping

C has no reflection, so you write the mapping yourself:

```c
const char *color_name(Color c) {
    switch (c) {
        case RED:   return "red";
        case GREEN: return "green";
        case BLUE:  return "blue";
    }
    return "unknown";
}
```

For DRY codebases with many enums, X-macros generate both the enum and the string table from a single list:

```c
#define COLORS(X) \
    X(RED)        \
    X(GREEN)      \
    X(BLUE)

#define ENUM_ENTRY(name) name,
#define STR_ENTRY(name) [name] = #name,

typedef enum { COLORS(ENUM_ENTRY) COLOR_COUNT } Color;
static const char *color_names[] = { COLORS(STR_ENTRY) };
```

This is advanced — understand the manual approach first.

## Why these design choices

**Why are C enums just integers?** Because C was designed for systems programming where you often need to store enum values in bitfields, network packets, or file formats. Implicit integer conversion makes this frictionless. The cost is type safety.

**Why not use `#define` constants instead?** You can: `#define RED 0`. But `#define` values have no type, no scope, and no debugger integration. An `enum` creates a named type that debuggers can display symbolically and compilers can warn about in `switch` statements.

**When would you pick differently?** In Rust, enums are algebraic data types — each variant can carry data, and the compiler forces you to handle every case. In Java, `enum` instances are full objects with methods. C's lightweight approach trades safety for simplicity and zero overhead.

## Production-quality code

### Result type for error handling

```c
typedef enum {
    RES_OK,
    RES_ERR_NOT_FOUND,
    RES_ERR_PERMISSION,
    RES_ERR_IO,
    RES_ERR_COUNT
} Result;

static const char *result_names[] = {
    [RES_OK]             = "ok",
    [RES_ERR_NOT_FOUND]  = "not found",
    [RES_ERR_PERMISSION] = "permission denied",
    [RES_ERR_IO]         = "I/O error",
};

const char *result_str(Result r) {
    if (r < 0 || r >= RES_ERR_COUNT) return "unknown";
    return result_names[r];
}

Result read_file(const char *path, char **out) {
    FILE *f = fopen(path, "r");
    if (!f) return RES_ERR_NOT_FOUND;
    /* ... read contents into *out ... */
    fclose(f);
    return RES_OK;
}
```

### Permission flags system

```c
#include <stdio.h>

typedef unsigned int Perm;
#define PERM_NONE  0u
#define PERM_READ  (1u << 0)
#define PERM_WRITE (1u << 1)
#define PERM_EXEC  (1u << 2)

Perm perm_grant(Perm current, Perm flag)  { return current | flag; }
Perm perm_revoke(Perm current, Perm flag) { return current & ~flag; }
int  perm_has(Perm current, Perm flag)    { return (current & flag) == flag; }

void perm_print(Perm p) {
    printf("%c%c%c\n",
        perm_has(p, PERM_READ)  ? 'r' : '-',
        perm_has(p, PERM_WRITE) ? 'w' : '-',
        perm_has(p, PERM_EXEC)  ? 'x' : '-');
}
```

Note: the flags use `#define` with `unsigned int` rather than `enum` because OR-ing enum values produces an `int`, not the enum type. This is a common pattern in production C.

## Security notes

- **Unchecked enum values from external input**: if you read an integer from a network packet and cast it to an enum, validate the range first. An out-of-range value in a `switch` without `default` leads to undefined behavior or skipping all cases silently.
- **Flag manipulation bugs**: using `&` instead of `|` to combine flags, or `|` instead of `& ~` to revoke, can silently grant permissions that should be denied.

## Performance notes

- Enums are integers — they have zero runtime overhead compared to raw `int` constants. The type name exists only at compile time.
- `switch` on enums is typically compiled to a jump table for dense values (0, 1, 2, ...) or a binary search for sparse values (200, 404, 500). Jump tables are O(1); binary search is O(log n).
- Flag operations (`|`, `&`, `~`) compile to single CPU instructions.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `switch` doesn't handle a new enum value | Added a value but forgot to update all switches | Compile with `-Wswitch-enum`; avoid `default` unless you genuinely need a catch-all |
| Flags combine incorrectly (`READ | WRITE` gives 3 but test fails) | Flag values aren't powers of two (e.g., `READ=1, WRITE=2, EXEC=3`) | Use `1 << N` for each flag; verify with binary representation |
| `Color c = 42;` compiles silently | C enums have no range enforcement | Validate external input; consider wrapper functions |
| Enum-to-string returns stale names | String table not updated when enum values change | Use X-macros or a build-time check that `sizeof names / sizeof names[0] == COUNT` |
| Sentinel `DAY_COUNT` processed as a real value | Used `<=` instead of `<` in loop, or forgot to exclude sentinel in switch | Loop with `< DAY_COUNT`; don't add a case for the sentinel |

## Practice

**Warm-up.** Define `enum Suit { CLUBS, DIAMONDS, HEARTS, SPADES }` and write a `suit_name` function. Print all four names in a loop using the sentinel trick.

**Standard.** Define permission flags (`READ`, `WRITE`, `EXEC`) and write `grant`, `revoke`, `has`, and `print` functions. Demonstrate combining and testing flags.

**Bug hunt.** This code compiles. Why might it miss cases?

```c
Color c = get_color();
switch (c) {
    case RED:   handle_red();   break;
    case GREEN: handle_green(); break;
}
```

**Stretch.** Build a `Result` enum with `OK`, `ERR_NOT_FOUND`, `ERR_IO`, and a `result_str` function. Use it as the return type for a `read_file` function.

**Stretch++.** Use X-macros to generate both `enum Color` and `const char *color_names[]` from a single macro definition. Verify they stay in sync with a `_Static_assert`.

<details><summary>Solutions</summary>

**Bug hunt.** If someone adds `BLUE` to the `Color` enum later, this `switch` won't handle it and silently falls through. Compiling with `-Wswitch-enum` makes the compiler warn about unhandled values. A `default` case would catch it at runtime but defeats the compile-time check.

**Warm-up.**

```c
typedef enum { CLUBS, DIAMONDS, HEARTS, SPADES, SUIT_COUNT } Suit;

const char *suit_name(Suit s) {
    switch (s) {
        case CLUBS:    return "Clubs";
        case DIAMONDS: return "Diamonds";
        case HEARTS:   return "Hearts";
        case SPADES:   return "Spades";
        default:       return "?";
    }
}

int main(void) {
    for (Suit s = CLUBS; s < SUIT_COUNT; s++)
        printf("%s\n", suit_name(s));
    return 0;
}
```

**Stretch++.**

```c
#define COLORS(X) X(RED) X(GREEN) X(BLUE)

#define ENUM_VAL(name) name,
#define STR_VAL(name)  [name] = #name,

typedef enum { COLORS(ENUM_VAL) COLOR_COUNT } Color;
static const char *color_names[] = { COLORS(STR_VAL) };

_Static_assert(sizeof color_names / sizeof color_names[0] == COLOR_COUNT,
               "color_names out of sync with Color enum");
```

</details>

## In plain terms (newbie lane)
If `Enums` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. Enum values default starting from:
    (a) 1  (b) 0  (c) -1  (d) undefined

2. Bitmask flag values should be:
    (a) consecutive integers  (b) powers of two  (c) prime numbers  (d) negative

3. C enums are:
    (a) strict types in all C versions  (b) integers; C23 adds `enum class` for strictness  (c) structs  (d) macros

4. Best way to convert an enum to a string in C:
    (a) reflection  (b) `switch` or lookup table  (c) `printf` with `%e`  (d) cast to `char *`

5. A sentinel like `DAY_COUNT` is:
    (a) a bug  (b) a useful last value enabling iteration and size checks  (c) dead code  (d) required by the standard

**Short answer:**

6. Why does C provide less enum type safety than languages like Rust or Java?
7. Why must bitmask flags use powers of two rather than consecutive integers?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-enums — mini-project](mini-projects/04-enums-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Python object model](../01-python/02-variables.md) — names, references, and mutability at a higher level.
  - [JavaScript event loop](../08-js/13-event-loop.md) — another managed-memory runtime with different scheduling trade-offs.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Enums give integer constants readable names, improving code clarity and enabling compiler warnings for unhandled cases.
- Bitmask enums use powers of two so flags can be combined with `|` and tested with `&`.
- C enums lack type safety — validate values from external input and use `-Wswitch-enum`.
- Sentinel values and X-macros are idiomatic patterns for iteration and keeping enum/string tables in sync.

## Further reading

- Linux kernel coding style — enum and flag best practices.
- C23 `enum class` proposal (N3030) — stricter enum typing coming to C.
- Next: [Unions](05-unions.md).
