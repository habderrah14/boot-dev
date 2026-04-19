# Chapter 03 — Encapsulation

> "Encapsulation is the right to refuse. An object owns its data; other code cannot touch that data except through the door the object provides."

## Learning objectives

By the end of this chapter you will be able to:

- Apply Python's naming conventions for "private" attributes (`_name`, `__name`) and explain why they're conventions, not enforcement.
- Expose state through methods or `@property` decorators rather than raw attributes.
- Enforce invariants at the boundary so the class guarantees its own consistency.
- Decide when to expose data publicly, when to use properties, and when to hide state behind methods.
- Protect internal mutable state from leaking to callers.

## Prerequisites & recap

- [Classes](02-classes.md) — you should be able to write a class with `__init__`, instance methods, and `__repr__`.

## The simple version

Encapsulation means an object controls access to its own data. Instead of letting any caller reach in and set `account.balance = -1000`, the object exposes a `withdraw()` method that checks whether the operation is valid first. The class becomes the single place where the rules are enforced, so you never have to hunt through the entire codebase to find out who broke the invariant.

In Python, there's no `private` keyword — it's all convention. A single underscore (`_balance`) says "this is internal, don't touch it." A double underscore (`__balance`) triggers name mangling to avoid accidental collisions in subclasses. Neither one prevents determined access, and that's by design: Python trusts developers to respect the boundary.

## Visual flow

```
  ┌─────────────────────────────────────────────────┐
  │                  Caller code                     │
  └────────────┬────────────────────┬───────────────┘
               │                    │
           allowed              forbidden
               │                    │
  ┌────────────▼──────────┐    ┌────▼───────────────┐
  │   Public interface     │    │  _internal state    │
  │                        │    │                     │
  │  .deposit(amount)      │    │  ._balance          │
  │  .withdraw(amount)     │    │  ._transactions     │
  │  .balance  (property)  │    │  ._validate(...)    │
  │  .transactions (copy)  │    │                     │
  └────────────┬──────────┘    └─────────────────────┘
               │                         ▲
               │    validates, then       │
               └─────────────────────────┘
                    mutates safely
```
*Figure 1 — Callers go through the public interface; the object mediates all access to its internal state.*

## Concept deep-dive

### Python's privacy model: convention + name mangling

```python
class Widget:
    def __init__(self):
        self.public = 1        # truly public — anyone can read/write
        self._internal = 2     # "leave me alone" by convention
        self.__secret = 3      # name-mangled to _Widget__secret
```

- **`_leading`** — a hint to other developers: "this is internal and may change without notice." Respected by most Python programmers and by linters, but not enforced at runtime.
- **`__double_leading`** — name-mangled by the interpreter to `_ClassName__attr`. Its purpose is to avoid accidental collisions in subclass hierarchies, *not* to provide security. Any code can still access `obj._Widget__secret`.

Why no `private` keyword? Python's philosophy is "we're all consenting adults." Runtime enforcement adds complexity, slows attribute access, and can't truly prevent access anyway (reflection, `ctypes`, etc.). Convention works because code reviews and linters catch violations before they ship.

### Getters, setters, and `@property`

If you come from Java, your instinct is to write `get_x()` / `set_x(v)` for every field. In Python, that's an anti-pattern. Start with a plain public attribute. If you later need validation or computation, wrap it in a `@property` without changing the caller's code:

```python
class Celsius:
    def __init__(self, degrees: float):
        self.degrees = degrees       # goes through the setter below

    @property
    def degrees(self) -> float:
        return self._degrees

    @degrees.setter
    def degrees(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"{value} is below absolute zero")
        self._degrees = value

    @property
    def kelvin(self) -> float:
        """Computed on the fly — no stored redundancy."""
        return self._degrees + 273.15
```

```python
t = Celsius(20)
t.degrees = 100        # goes through setter, validates
print(t.kelvin)        # 373.15 — computed, not stored
t.degrees = -300       # ValueError
```

Why properties matter: they let you start simple (public attribute) and migrate to validated access *without breaking any caller*. In Java, you'd have to change every `obj.x` to `obj.getX()`. In Python, the interface stays `obj.x` either way.

### Invariants at the boundary

Encapsulation's deepest benefit isn't hiding data — it's *guaranteeing consistency*. If your class promises that items are always sorted, encapsulation makes that promise enforceable:

```python
class SortedBag:
    def __init__(self):
        self._items: list[int] = []

    def add(self, x: int) -> None:
        import bisect
        bisect.insort(self._items, x)

    @property
    def items(self) -> tuple[int, ...]:
        return tuple(self._items)    # return a copy — caller can't mutate

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)
```

The invariant ("always sorted") holds because the only way to add items is through `add()`, which uses `bisect.insort`. The `items` property returns a tuple (immutable), so callers can't sneak in an unsorted element.

### Leaking mutable state

This is the most common encapsulation bug in Python:

```python
class BadBag:
    def __init__(self):
        self._items = []

    def get_items(self):
        return self._items    # BUG: caller gets a reference to the real list
```

Now any caller can `bag.get_items().append(999)` and corrupt the invariant. Fix: return a copy (`list(self._items)`) or an immutable view (`tuple(self._items)`).

### When to expose vs. hide

| Situation | Recommendation | Why |
|---|---|---|
| Simple data with no rules | Public attribute | Keep it simple; add a property later if rules emerge |
| Data with a constraint (age ≥ 0) | `@property` with validation in the setter | Enforce the rule at the boundary |
| Internal bookkeeping (caches, counters) | `_prefix` | Signal "don't depend on this" |
| Fields that subclasses might accidentally shadow | `__prefix` | Name mangling prevents collisions |

### Dataclasses and encapsulation

`@dataclass(frozen=True)` with `_`-prefixed fields gives you value semantics plus encapsulation-by-immutability — often a better answer than hand-rolled setters. If the object can't be mutated, there's nothing to protect.

## Why these design choices

**Why convention instead of enforcement?** Enforcement creates a false sense of security (reflection bypasses it), adds runtime cost, and makes debugging harder (you can't inspect private fields in a crash dump). Convention is cheaper, transparent, and works in practice because code review catches violations.

**Why `@property` instead of getter/setter methods?** Uniform access: callers use `obj.x` whether it's a plain attribute or computed. You can evolve the implementation without changing the interface. This is a Python-specific advantage — Java doesn't have it, which is why Java conventions don't apply here.

**Why return copies from accessors?** Because Python's assignment semantics are reference-based. Returning `self._items` gives the caller a *reference* to your internal list, not a copy. Any mutation through that reference breaks your invariants silently.

**When you'd pick differently:** For hot paths where copying a large list on every access is too expensive, return a read-only view (e.g., `types.MappingProxyType` for dicts) or document that the caller must not mutate. For simple internal scripts, the overhead of properties and defensive copies isn't worth it.

## Production-quality code

```python
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterator


@dataclass
class Transaction:
    amount_cents: int
    timestamp: datetime
    description: str


class BankAccount:
    """Account with encapsulated balance and an append-only transaction log."""

    def __init__(self, owner: str, balance_cents: int = 0):
        if not owner.strip():
            raise ValueError("owner must not be blank")
        if balance_cents < 0:
            raise ValueError("initial balance cannot be negative")
        self._owner = owner
        self._balance_cents = balance_cents
        self._transactions: list[Transaction] = []

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance_cents(self) -> int:
        return self._balance_cents

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        """Return an immutable snapshot — callers cannot mutate the log."""
        return tuple(self._transactions)

    def deposit(self, amount_cents: int, description: str = "deposit") -> None:
        if amount_cents <= 0:
            raise ValueError("deposit amount must be positive")
        self._balance_cents += amount_cents
        self._record(amount_cents, description)

    def withdraw(self, amount_cents: int, description: str = "withdrawal") -> None:
        if amount_cents <= 0:
            raise ValueError("withdrawal amount must be positive")
        if amount_cents > self._balance_cents:
            raise ValueError(
                f"insufficient funds: have {self._balance_cents}, need {amount_cents}"
            )
        self._balance_cents -= amount_cents
        self._record(-amount_cents, description)

    def _record(self, amount_cents: int, description: str) -> None:
        self._transactions.append(
            Transaction(
                amount_cents=amount_cents,
                timestamp=datetime.now(timezone.utc),
                description=description,
            )
        )

    def __repr__(self) -> str:
        return (
            f"BankAccount(owner={self._owner!r}, "
            f"balance_cents={self._balance_cents}, "
            f"transactions={len(self._transactions)})"
        )
```

## Security notes

Encapsulation is *not* a security mechanism. A determined caller can access `_private` attributes via `__dict__`, `getattr`, or name-demangling. If you need true isolation (e.g., plugin sandboxing), you need process boundaries or a restricted execution environment — not underscores.

That said, encapsulation *reduces the attack surface of accidental misuse*: if the only way to transfer money is `withdraw()`, you have one place to add logging, rate limiting, and fraud checks.

## Performance notes

- **`@property`** adds a function call on every access. For simple attributes accessed in tight loops, this is measurable but rarely significant for backend code dominated by I/O.
- **Returning copies** from properties (e.g., `tuple(self._items)`) costs O(n). If the collection is large and accessed frequently, consider returning a `types.MappingProxyType` (for dicts) or documenting the contract ("don't mutate") instead of copying.
- **`__slots__`** combined with encapsulation eliminates the per-instance `__dict__`, saving memory when you have many instances with fixed attributes.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Writing Java-style `get_x()` / `set_x()` methods | Porting habits from Java/C# | Use plain attributes or `@property`. Python callers expect `obj.x`, not `obj.get_x()`. |
| 2 | Caller mutates your internal list through a property | Property returns a reference to the mutable internal collection | Return a copy (`list(...)`) or immutable view (`tuple(...)`) from accessors. |
| 3 | Using `__double_underscore` everywhere "for safety" | Misunderstanding name mangling as a security feature | Use `_single_underscore` in almost all cases. Reserve `__` for avoiding subclass name collisions. |
| 4 | Treating `_` as real privacy and assuming no one will access it | Confusing convention with enforcement | Respect the convention, but know that determined callers can still access `_` attributes. Design APIs to make the right thing easy, not the wrong thing impossible. |
| 5 | Adding a `@property` setter but forgetting to validate | Migrating from a plain attribute to a property without adding the checks that motivated the migration | If you're adding a property, you're adding it for a reason — add the validation in the setter. |

## Practice

**Warm-up.** Convert a class that has `get_name()` / `set_name(v)` methods into one that uses a `name` property.

**Standard.** Write a `BankAccount` class where `balance` is a read-only property and `deposit()` / `withdraw()` enforce non-negative balance. Prove the invariant holds with tests.

**Bug hunt.** Why can a caller see `self.__secret` by accessing `obj._ClassName__secret`? Is this a bug in Python?

**Stretch.** Add a `transactions` property to your `BankAccount` that returns a *copy* of the internal list. Write a test that proves mutating the returned list doesn't affect the account.

**Stretch++.** Use `functools.cached_property` to cache an expensive computation (e.g., `Rectangle.diagonal`) that invalidates if a dimension changes. Discuss: what makes cache invalidation hard here?

<details><summary>Show solutions</summary>

**Bug hunt.** Name mangling prepends `_ClassName` to avoid accidental collisions in inheritance hierarchies — it's not a security feature. Any code that knows the class name can access the attribute. This is by design: Python doesn't have true private access.

**Stretch.**

```python
@property
def transactions(self):
    return list(self._transactions)  # or tuple(...)
```

Test:

```python
acct = BankAccount("Alice", 100)
acct.deposit(50)
txns = acct.transactions
txns.clear()
assert len(acct.transactions) == 1  # internal list unaffected
```

**Stretch++.** `functools.cached_property` caches on first access and never recomputes. If `width` or `height` changes, the cached diagonal is stale. You'd need to delete the cached value in the setters (`del self.__dict__["diagonal"]`) or avoid `cached_property` for mutable objects.

</details>

## In plain terms (newbie lane)
If `Encapsulation` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. `self._x` means:
    (a) private, enforced by the runtime  (b) private by convention  (c) class attribute  (d) public

2. `self.__x` is:
    (a) strictly hidden from all access  (b) name-mangled to `_ClassName__x`  (c) a type hint  (d) illegal syntax

3. `@property` allows:
    (a) attribute-style access that runs a method  (b) automatic threading  (c) deletion of the instance  (d) async access

4. The Pythonic way to add validation to a field that was previously public:
    (a) rename the field and update all callers  (b) wrap it in a `@property` — callers don't change  (c) subclass and override  (d) use a metaclass

5. Returning a mutable internal list from a property:
    (a) is safe  (b) breaks encapsulation — callers can mutate it  (c) is required  (d) is fine if documented

**Short answer:**

6. Why is there no `private` keyword in Python?
7. Give one scenario where `@property` is clearly better than a plain attribute.

*Answers: 1-b, 2-b, 3-a, 4-b, 5-b. 6 — Python's philosophy is "we're all consenting adults." Convention is sufficient because code review catches violations, and true enforcement can always be bypassed via reflection anyway. 7 — When a field has a constraint (e.g., temperature must be ≥ -273.15). A property setter validates on every assignment without changing the caller's syntax.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [03-encapsulation — mini-project](mini-projects/03-encapsulation-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Classes in TypeScript](../09-ts/11-classes.md) — the same OO ideas with a static type system.
  - [HTTP handler layering](../12-http-servers/03-architecture.md) — objects become routers, controllers, services.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Encapsulation means the object owns its data and controls mutation — the class is the single source of truth for its invariants.
- Python uses conventions (`_`, `__`) instead of runtime enforcement, and that works because code review and linters catch violations.
- `@property` lets you migrate from a plain attribute to validated access without breaking any caller.
- Always return copies or immutable views of internal mutable state to prevent callers from corrupting your invariants.

## Further reading

- PEP 8, section on [Designing for Inheritance](https://peps.python.org/pep-0008/#designing-for-inheritance) — guidance on public vs. internal naming.
- Python docs: [`property`](https://docs.python.org/3/library/functions.html#property) built-in.
- Next: [Abstraction](04-abstraction.md).
