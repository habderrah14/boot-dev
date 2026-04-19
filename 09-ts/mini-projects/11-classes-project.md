# Mini-project — 11-classes

_Companion chapter:_ [`11-classes.md`](../11-classes.md)

**Goal.** Implement an abstract `Repository<T>` class with `InMemoryRepo<T>` and `FileRepo<T>` subclasses.

**Acceptance criteria:**

- `Repository<T>` has `find`, `findAll`, `save`, `delete` methods.
- `InMemoryRepo` stores data in a `Map`.
- `FileRepo` stores data as JSON in a file (one file per entity, using `id` as filename).
- Both pass the same test suite (written against the `Repository<T>` interface).
- Uses parameter properties and `readonly` where appropriate.
- `T` is constrained to `{ id: string }`.

**Hints:**

- `FileRepo` can use `node:fs/promises` for file I/O.
- Store files in a temp directory for tests and clean up after.
- The abstract class can provide shared logic (like `findAll` delegating to `find`).

**Stretch:** Add a `validate(item: T): void` abstract method that subclasses must implement, called before every `save`.
