# Chapter 04 — Abstraction

> "Abstraction is hiding a complicated truth behind a simple story, and getting the story right."

## Learning objectives

By the end of this chapter you will be able to:

- Design classes whose public surface tells the *story* of what they do, not *how* they do it.
- Write abstract base classes (ABCs) with `abc.ABC` and `@abstractmethod` to declare contracts.
- Use `typing.Protocol` for structural (duck-type) interfaces when inheritance would be overkill.
- Recognize leaky abstractions and fix them by translating errors and simplifying signatures.
- Decide between ABCs and Protocols for a given design situation.

## Prerequisites & recap

- [Encapsulation](03-encapsulation.md) — you should understand how classes control access to their data.

## The simple version

Abstraction is the art of giving callers a simple, honest story about what an object does while hiding the messy details of *how* it does it. When you call `list.append(x)`, you don't think about dynamic arrays, amortized doubling, or C-level memory allocation — you think "add an item to the end." That's a good abstraction: the story is simple, accurate, and stable even if the implementation changes.

In Python, you formalize abstractions in two ways: *abstract base classes* (ABCs) declare "any subclass must implement these methods," while *Protocols* declare "any object with these methods is acceptable" — no inheritance required. Both are tools for saying "here's the contract" without locking callers into a specific implementation.

## Visual flow

```
  ┌──────────────────────────────────────────┐
  │             Caller code                   │
  │                                           │
  │  storage.put("key", data)                 │
  │  value = storage.get("key")               │
  └──────────────┬───────────────────────────┘
                 │
                 │  calls the abstract interface
                 │
  ┌──────────────▼───────────────────────────┐
  │        Storage  (ABC or Protocol)         │
  │                                           │
  │  + put(key: str, value: bytes) -> None    │
  │  + get(key: str) -> bytes                 │
  └──────┬──────────────────┬────────────────┘
         │                  │
  ┌──────▼──────┐    ┌──────▼──────┐
  │ MemoryStore  │    │  FileStore   │
  │              │    │              │
  │ dict-backed  │    │ disk-backed  │
  └─────────────┘    └─────────────┘

  Callers depend on the story (put/get), not the shelf (dict/disk).
```
*Figure 1 — The abstract interface decouples callers from concrete implementations.*

## Concept deep-dive

### The idea: stories, not machinery

An *abstraction* hides implementation details behind a stable interface. The key insight is that the interface isn't just "what methods exist" — it's a *promise* about behavior:

- `list.append(x)` — you don't know about dynamic arrays, amortized doubling, or C arrays. You know: "the item is now at the end."
- `dict[k]` — you don't know about hashing, open addressing, or resizing. You know: "give me the value for this key."

A good abstraction lets callers *rely on the story*, not on the implementation. When you change the implementation (say, swapping a dict-backed cache for Redis), callers should not need to change.

### Abstract base classes (ABCs)

When several concrete classes share a contract, declare it explicitly with `abc.ABC`:

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    """Store and retrieve binary values by string key."""

    @abstractmethod
    def put(self, key: str, value: bytes) -> None: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...
```

Any class that inherits from `Storage` but doesn't implement `put` and `get` will raise `TypeError` at instantiation — not at call time. This is the ABC's value: you get an immediate, clear error instead of a runtime `AttributeError` buried in production logs.

```python
class MemoryStorage(Storage):
    def __init__(self):
        self._data: dict[str, bytes] = {}

    def put(self, key: str, value: bytes) -> None:
        self._data[key] = value

    def get(self, key: str) -> bytes:
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]
```

Why ABCs? They make the contract *explicit and enforceable*. When a new developer writes a third storage backend, the ABC tells them exactly which methods to implement, and Python refuses to let them forget one.

### Protocols — structural typing

If you don't want an inheritance link, Python supports *duck-type interfaces* via `typing.Protocol`:

```python
from typing import Protocol


class Readable(Protocol):
    def read(self, n: int) -> bytes: ...


def drain(src: Readable) -> bytes:
    """Read all content from any source that has a .read() method."""
    chunks: list[bytes] = []
    while chunk := src.read(4096):
        chunks.append(chunk)
    return b"".join(chunks)
```

Any class with a matching `read(self, n: int) -> bytes` method satisfies `Readable` — no `class Foo(Readable)` declaration needed. Type checkers (mypy, pyright) verify compatibility at check time; Python doesn't enforce at runtime unless you decorate the Protocol with `@runtime_checkable`.

Why Protocols? Because sometimes there's no natural inheritance relationship. A file, a socket, and an HTTP response body all have `.read()`, but they don't share a common ancestor. A Protocol says "I care about the shape, not the lineage."

### Leaky abstractions

Joel Spolsky's Law of Leaky Abstractions: "All non-trivial abstractions, to some degree, are leaky." A leaky abstraction is one where callers must know about the implementation to use it correctly:

- `list.remove(x)` *reads* like O(1) — "remove this item." It's actually O(n). Code that calls `remove()` in a loop gets O(n²) and the abstraction is to blame for hiding the cost.
- An `HttpClient.get(url)` that sometimes raises `socket.timeout` has leaked the transport layer into the domain.

How to fix leaks:
1. Pick the simplest story the implementation can honestly support.
2. Translate low-level errors into domain-level errors at the boundary.
3. Document performance characteristics when they're non-obvious.

### Naming the public surface

Write the *usage* first, in plain English:

> `Storage` stores bytes by key and retrieves them later. It never loses keys that were successfully written.

If your usage description mentions "Redis," "SQL," "retry," or "table," you're leaking implementation into the story. The public surface should describe *what*, not *how*.

## Why these design choices

**Why ABCs instead of just documentation?** Documentation says "you should implement `put` and `get`." An ABC says "you *must*, and Python will refuse to run if you don't." For shared contracts across a team, enforcement beats hope.

**Why Protocols instead of ABCs?** ABCs require inheritance, which creates coupling. If you're writing a library and want to accept "anything that has a `.read()` method," forcing users to inherit from your base class is invasive. Protocols are opt-in for the consumer.

**When to use which:**

| Criterion | ABC | Protocol |
|---|---|---|
| Natural "is-a" hierarchy | Yes | No |
| Shared default implementations | Yes (via concrete methods on the ABC) | No |
| Third-party classes must conform | No (they'd have to inherit) | Yes (structural match) |
| Runtime `isinstance` checks | Yes | Only with `@runtime_checkable` |

**When you'd pick differently:** If you have only one implementation and no foreseeable second one, an ABC is premature abstraction. Start with the concrete class; extract an interface when you actually need to swap implementations.

## Production-quality code

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class StorageError(Exception):
    """Domain-level error — callers never see sqlite3 or redis exceptions."""


class Storage(ABC):
    """Abstract contract for key-value byte storage."""

    @abstractmethod
    def put(self, key: str, value: bytes) -> None:
        """Store value under key. Raises StorageError on failure."""

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Retrieve value by key. Raises KeyError if missing, StorageError on failure."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove key. No-op if key doesn't exist. Raises StorageError on failure."""

    def exists(self, key: str) -> bool:
        """Default implementation — subclasses may override for efficiency."""
        try:
            self.get(key)
            return True
        except KeyError:
            return False


class MemoryStorage(Storage):
    """In-memory implementation — fast, ephemeral, good for tests."""

    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def put(self, key: str, value: bytes) -> None:
        self._data[key] = value

    def get(self, key: str) -> bytes:
        try:
            return self._data[key]
        except KeyError:
            raise

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def __repr__(self) -> str:
        return f"MemoryStorage(keys={len(self._data)})"


class FileStorage(Storage):
    """Disk-backed implementation — persistent, slower."""

    def __init__(self, directory: str) -> None:
        import pathlib
        self._dir = pathlib.Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, value: bytes) -> None:
        self._validate_key(key)
        try:
            (self._dir / key).write_bytes(value)
        except OSError as exc:
            raise StorageError(f"failed to write {key!r}") from exc

    def get(self, key: str) -> bytes:
        self._validate_key(key)
        path = self._dir / key
        if not path.exists():
            raise KeyError(key)
        try:
            return path.read_bytes()
        except OSError as exc:
            raise StorageError(f"failed to read {key!r}") from exc

    def delete(self, key: str) -> None:
        self._validate_key(key)
        (self._dir / key).unlink(missing_ok=True)

    @staticmethod
    def _validate_key(key: str) -> None:
        if "/" in key or "\\" in key or ".." in key:
            raise ValueError(f"unsafe key: {key!r}")

    def __repr__(self) -> str:
        return f"FileStorage(directory={str(self._dir)!r})"


# ── Protocol example ────────────────────────────────────

class Logger(Protocol):
    def info(self, msg: str) -> None: ...
    def error(self, msg: str) -> None: ...


class StdoutLogger:
    """Satisfies Logger without inheriting from it."""
    def info(self, msg: str) -> None:
        print(f"[INFO] {msg}")
    def error(self, msg: str) -> None:
        print(f"[ERROR] {msg}")


def ingest(storage: Storage, key: str, data: bytes, logger: Logger) -> None:
    """Store data and log the result — depends on abstractions, not concretions."""
    try:
        storage.put(key, data)
        logger.info(f"stored {len(data)} bytes under {key!r}")
    except StorageError as exc:
        logger.error(f"storage failure: {exc}")
        raise
```

## Security notes

The `FileStorage` example above demonstrates a real security concern: **path traversal**. If a caller can pass `key="../../etc/passwd"`, the storage might read or write outside its intended directory. The `_validate_key` method is a minimal defense — production code should use `pathlib.Path.resolve()` and verify the resolved path is still inside the base directory.

More broadly, abstractions can *hide* security-relevant behavior. If your `Storage` ABC silently switches from encrypted to plaintext storage depending on the backend, callers who assume encryption are vulnerable. Document security-relevant properties explicitly in the ABC's docstring.

## Performance notes

- **ABC overhead** is negligible — the `abstractmethod` check happens once at class creation, not on every call.
- **Protocol overhead** is zero at runtime unless `@runtime_checkable` is used. Type checking happens statically via mypy/pyright.
- **Abstraction boundaries add indirection**, which prevents some optimizations (inlining, specialization). In Python, this cost is trivial compared to interpreter overhead and I/O. In hot C/Rust code, it matters — but you're writing Python.
- **Leaky performance abstractions** are the real danger: an interface that hides O(n) behind O(1)-looking syntax can cause production outages.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Designing an ABC with six implementations you don't have yet | Premature abstraction — speculating about future needs | Start with one concrete class. Extract an ABC when you actually have two implementations. |
| 2 | Abstract method signatures leak implementation: `def save(self, postgres_conn)` | The ABC is coupled to a specific backend | Use domain-level parameters: `def save(self, key: str, value: bytes)`. The backend is an implementation detail. |
| 3 | Callers catch `sqlite3.OperationalError` from a "generic" storage class | Transport-layer errors leaking through the abstraction | Translate to domain errors (`StorageError`) at the boundary. Chain the original with `raise ... from exc`. |
| 4 | Using inheritance (ABC) when the conforming types have no natural hierarchy | Forcing an "is-a" relationship where none exists | Use a Protocol instead. Structural typing is less invasive. |
| 5 | A Protocol with 15 methods | The interface is too wide — hard to implement, hard to mock | Split into smaller, focused Protocols (Interface Segregation Principle). |

## Practice

**Warm-up.** Write `Animal(ABC)` with an abstract `speak() -> str` method. Implement `Dog` and `Cat`.

**Standard.** Define a `Cache` Protocol with `get(key)` and `set(key, value)` methods. Write two implementations: `DictCache` (in-memory) and `NullCache` (always misses). Write a function that accepts `Cache` and works with both.

**Bug hunt.** Your `Storage.put()` implementation occasionally raises `sqlite3.OperationalError`. Why is this a leaky abstraction, and how do you fix it?

**Stretch.** Refactor a hand-rolled duck-type interface (where you just happened to give two classes the same method names) into an explicit `Protocol`. Verify with mypy.

**Stretch++.** Write a `@runtime_checkable` Protocol and use `isinstance(x, MyProtocol)`. Then read the documentation and list two caveats of `@runtime_checkable`.

<details><summary>Show solutions</summary>

**Bug hunt.** The caller must know you're using SQLite to handle the error — that's a leak. Fix: catch `sqlite3.OperationalError` inside `put()` and raise a domain-level `StorageError` with `raise StorageError("write failed") from exc`.

**Stretch++.** Caveats: (1) `@runtime_checkable` only checks that the methods *exist*, not that their signatures match. (2) It's slower than a plain `isinstance` check against a concrete class, since it uses `__subclasshook__` with attribute inspection.

</details>

## In plain terms (newbie lane)
If `Abstraction` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. An ABC:
    (a) can be instantiated directly  (b) raises `TypeError` if abstract methods are unimplemented at instantiation  (c) prevents all subclassing  (d) requires `@abstractmethod` on every method

2. Protocols use:
    (a) nominal typing  (b) structural typing — shape matters, not lineage  (c) runtime reflection only  (d) metaclasses exclusively

3. A "leaky abstraction" means:
    (a) it causes memory leaks  (b) callers must know implementation details to use it correctly  (c) it hides complexity well  (d) it uses inheritance

4. Which is a good public method name for a queue abstraction?
    (a) `put_redis`  (b) `enqueue`  (c) `insert_to_sql`  (d) `send_to_rabbit`

5. Prefer a Protocol over an ABC when:
    (a) you need runtime enforcement  (b) there's no natural inheritance link between conforming types  (c) you're using dataclasses  (d) always, ABCs are obsolete

**Short answer:**

6. Define "leaky abstraction" in one sentence.
7. When does inheritance (ABC) earn its keep over a Protocol?

*Answers: 1-b, 2-b, 3-b, 4-b, 5-b. 6 — A leaky abstraction is an interface that forces callers to understand the underlying implementation to use it correctly or avoid errors. 7 — When you have a natural "is-a" hierarchy, when you want shared default implementations (concrete methods on the ABC), or when you need reliable `isinstance` checks without `@runtime_checkable` caveats.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [04-abstraction — mini-project](mini-projects/04-abstraction-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Abstraction is a story about *what* an object does, not *how* it does it — and getting the story right is the hard part.
- ABCs enforce contracts via nominal typing: subclasses *must* implement abstract methods or Python refuses to instantiate them.
- Protocols enforce contracts via structural typing: any object with matching methods qualifies, no inheritance required.
- Translate low-level errors at the abstraction boundary so callers never see implementation details leaking through.

## Further reading

- Joel Spolsky, [The Law of Leaky Abstractions](https://www.joelonsoftware.com/2002/11/11/the-law-of-leaky-abstractions/).
- Python docs: [`abc`](https://docs.python.org/3/library/abc.html) module.
- Python docs: [`typing.Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol).
- Next: [Inheritance](05-inheritance.md).
