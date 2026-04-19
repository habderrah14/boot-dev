# Module 04 — Learn Object Oriented Programming in Python

> OOP is not about syntax — it's about drawing boundaries. A good class hides a decision so thoroughly that the rest of your program can change without caring. A bad class leaks its decisions into every caller.

## Map to Boot.dev

Parallels Boot.dev's **"Learn Object Oriented Programming"** course, chapter-for-chapter.

## Learning outcomes

By the end of this module you will be able to:

- Design small classes that own one clear responsibility.
- Apply the four OOP pillars — encapsulation, abstraction, inheritance, polymorphism — and know when each helps or hurts.
- Refactor messy procedural code into classes without just renaming the mess.
- Recognize when _not_ to use inheritance (spoiler: most of the time — prefer composition).

## Prerequisites

- [Module 01: Python](../01-python/README.md). You should be comfortable with functions and dicts.

## Chapter index

1. [Clean Code](01-clean-code.md)
2. [Classes](02-classes.md)
3. [Encapsulation](03-encapsulation.md)
4. [Abstraction](04-abstraction.md)
5. [Inheritance](05-inheritance.md)
6. [Polymorphism](06-polymorphism.md)

## How this module connects

- OOP's pillars reappear in TypeScript (Module 09, especially `classes` and `interfaces`).
- _Polymorphism_ is the foundation for plugin systems, ORMs (Module 11), and web framework middleware (Module 12).

## Companion artifacts

- Exercises:
  - [01 — Clean Code](exercises/01-clean-code-exercises.md)
  - [02 — Classes](exercises/02-classes-exercises.md)
  - [03 — Encapsulation](exercises/03-encapsulation-exercises.md)
  - [04 — Abstraction](exercises/04-abstraction-exercises.md)
  - [05 — Inheritance](exercises/05-inheritance-exercises.md)
  - [06 — Polymorphism](exercises/06-polymorphism-exercises.md)
- Extended assessment artifacts:
  - [07 — Debugging Incident Lab](exercises/07-debugging-incident-lab.md)
  - [08 — Code Review Task](exercises/08-code-review-task.md)
  - [09 — System Design Prompt](exercises/09-system-design-prompt.md)
  - [10 — Interview Challenges](exercises/10-interview-challenges.md)
- Solutions:
  - [01 — Clean Code](solutions/01-clean-code-solutions.md)
  - [02 — Classes](solutions/02-classes-solutions.md)
  - [03 — Encapsulation](solutions/03-encapsulation-solutions.md)
  - [04 — Abstraction](solutions/04-abstraction-solutions.md)
  - [05 — Inheritance](solutions/05-inheritance-solutions.md)
  - [06 — Polymorphism](solutions/06-polymorphism-solutions.md)
- Mini-project briefs:
  - [01 — Clean Code Audit (Bonus project)](mini-projects/01-clean-code-audit.md)
  - [01 — Clean Code (Core chapter project)](mini-projects/01-clean-code-project.md)
  - [02 — Classes](mini-projects/02-classes-project.md)
  - [03 — Encapsulation](mini-projects/03-encapsulation-project.md)
  - [04 — Abstraction](mini-projects/04-abstraction-project.md)
  - [05 — Inheritance](mini-projects/05-inheritance-project.md)
  - [06 — Polymorphism](mini-projects/06-polymorphism-project.md)
- Milestone capstone:
  - [Capstone Milestone](capstone/capstone-milestone.md)

## Quiz answer key

- **Ch. 01 — Clean Code.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  A comment is worth writing when it explains non-obvious intent, constraints, or a workaround the code itself cannot express.
  - 7.  Over-extracting creates tiny helper functions that increase navigation and cognitive overhead without adding clarity or reuse.
- **Ch. 02 — Classes.** 1) b, 2) a, 3) b, 4) b, 5) b.
  - 6.  Use a classmethod when you need an alternative constructor that accepts different input formats while keeping `__init__` focused.
  - 7.  Defining `__eq__` without `__hash__` makes instances unhashable, so they cannot be used as set members or dict keys.
- **Ch. 03 — Encapsulation.** 1) b, 2) b, 3) a, 4) b, 5) b.
  - 6.  Python uses a convention-based privacy model because strict enforcement can be bypassed and code review/linting catches boundary violations in practice.
  - 7.  Use a property setter when assignments must always enforce an invariant, such as lower/upper bounds.
- **Ch. 04 — Abstraction.** 1) b, 2) b, 3) b, 4) b, 5) b.
  - 6.  A leaky abstraction forces callers to understand implementation details to use an interface safely.
  - 7.  Choose an ABC when you want explicit inheritance contracts, shared defaults, or reliable runtime `isinstance` checks.
- **Ch. 05 — Inheritance.** 1) b, 2) c, 3) b, 4) b, 5) b.
  - 6.  Deep inheritance increases coupling because parent changes can break distant descendants and complicate reasoning.
  - 7.  Inheritance is appropriate for framework extension points where subclassing is the intended integration mechanism.
- **Ch. 06 — Polymorphism.** 1) a, 2) b, 3) b, 4) b, 5) a.
  - 6.  Move from `isinstance` chains to polymorphism when cases multiply, logic repeats, or new types are added often.
  - 7.  Duck typing is flexible because behavior is shape-based, but risky without static checks because missing methods surface only at runtime.
