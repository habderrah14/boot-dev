# Module 07 — Learn Memory Management in C

> Every programming language manages memory. The question is whether _you_ do it, or someone else does it for you. Spending a few weeks in C where there is no "someone else" will change how you read every other language.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Memory Management"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Write, compile, and debug a small C17 program end-to-end (clang/gcc + `make`).
- Explain the difference between the stack and the heap, and choose correctly between them.
- Use pointers fluently: address-of, dereference, pointer arithmetic, and `const` correctness.
- Build a reference-counted object system in C.
- Implement a mark-and-sweep garbage collector.

## Prerequisites

- Comfort with a terminal and a compiler — Module 02.
- Familiarity with DSA (Module 06) helps; the GC project uses linked structures.

## Chapter index

1. [C Basics](01-c-basics.md)
2. [Structs](02-structs.md)
3. [Pointers](03-pointers.md)
4. [Enums](04-enums.md)
5. [Unions](05-unions.md)
6. [Stack and Heap](06-stack-and-heap.md)
7. [Advanced Pointers](07-advanced-pointers.md)
8. [Stack Data Structure](08-stack-data-structure.md)
9. [Objects](09-objects.md)
10. [Refcounting GC](10-refcounting-gc.md)
11. [Mark and Sweep GC](11-mark-and-sweep-gc.md)

## How this module connects

- Pointers demystify _references_ in Python, Java, JS, and TS: under the hood, everything is a pointer.
- Refcounting is how CPython itself manages memory — Module 01 runs on what you build in ch. 10.
- Stack/heap knowledge shows up in performance tuning (Module 11) and container sizing (Module 14).

## Companion artifacts

- Exercises:
  - [01 — C Basics](exercises/01-c-basics-exercises.md)
  - [02 — Structs](exercises/02-structs-exercises.md)
  - [03 — Pointers](exercises/03-pointers-exercises.md)
  - [04 — Enums](exercises/04-enums-exercises.md)
  - [05 — Unions](exercises/05-unions-exercises.md)
  - [06 — Stack and Heap](exercises/06-stack-and-heap-exercises.md)
  - [07 — Advanced Pointers](exercises/07-advanced-pointers-exercises.md)
  - [08 — Stack Data Structure](exercises/08-stack-data-structure-exercises.md)
  - [09 — Objects](exercises/09-objects-exercises.md)
  - [10 — Refcounting GC](exercises/10-refcounting-gc-exercises.md)
  - [11 — Mark and Sweep GC](exercises/11-mark-and-sweep-gc-exercises.md)
- Extended assessment artifacts:
  - [12 — Debugging Incident Lab](exercises/12-debugging-incident-lab.md)
  - [13 — Code Review Task](exercises/13-code-review-task.md)
  - [14 — System Design Prompt](exercises/14-system-design-prompt.md)
  - [15 — Interview Challenges](exercises/15-interview-challenges.md)
- Solutions:
  - [01 — C Basics](solutions/01-c-basics-solutions.md)
  - [02 — Structs](solutions/02-structs-solutions.md)
  - [03 — Pointers](solutions/03-pointers-solutions.md)
  - [04 — Enums](solutions/04-enums-solutions.md)
  - [05 — Unions](solutions/05-unions-solutions.md)
  - [06 — Stack and Heap](solutions/06-stack-and-heap-solutions.md)
  - [07 — Advanced Pointers](solutions/07-advanced-pointers-solutions.md)
  - [08 — Stack Data Structure](solutions/08-stack-data-structure-solutions.md)
  - [09 — Objects](solutions/09-objects-solutions.md)
  - [10 — Refcounting GC](solutions/10-refcounting-gc-solutions.md)
  - [11 — Mark and Sweep GC](solutions/11-mark-and-sweep-gc-solutions.md)
- Mini-project briefs:
  - [01 — C Basics (Core chapter project)](mini-projects/01-c-basics-project.md)
  - [01 — C Calculator (Bonus project)](mini-projects/01-c-calculator.md)
  - [02 — Structs](mini-projects/02-structs-project.md)
  - [03 — Pointers](mini-projects/03-pointers-project.md)
  - [04 — Enums](mini-projects/04-enums-project.md)
  - [05 — Unions](mini-projects/05-unions-project.md)
  - [06 — Stack and Heap](mini-projects/06-stack-and-heap-project.md)
  - [07 — Advanced Pointers](mini-projects/07-advanced-pointers-project.md)
  - [08 — Stack Data Structure](mini-projects/08-stack-data-structure-project.md)
  - [09 — Objects](mini-projects/09-objects-project.md)
  - [10 — Refcounting GC](mini-projects/10-refcounting-gc-project.md)
  - [11 — Mark and Sweep GC](mini-projects/11-mark-and-sweep-gc-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — C Basics.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  Undefined behavior means the standard makes no guarantees; unlike runtime exceptions, the compiler may optimize based on assumptions that make the bug appear or disappear unpredictably.
  - 7.  `.h` files declare interfaces so multiple `.c` files can compile independently; `.c` files define the actual code so the linker can combine them.
- **Ch. 02 — Structs.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 03 — Pointers.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 04 — Enums.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 05 — Unions.** 1) b, 2) b, 3) b, 4) b, 5) c.
- **Ch. 06 — Stack and Heap.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 07 — Advanced Pointers.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 08 — Stack Data Structure.** 1) a, 2) b, 3) b, 4) a, 5) a.
- **Ch. 09 — Objects.** 1) b, 2) b, 3) b, 4) b, 5) b.
- **Ch. 10 — Refcounting GC.** 1) a, 2) b, 3) a, 4) b, 5) b.
- **Ch. 11 — Mark and Sweep GC.** 1) b, 2) a, 3) b, 4) b, 5) b.
