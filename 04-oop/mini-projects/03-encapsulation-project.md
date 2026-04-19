# Mini-project — 03-encapsulation

_Companion chapter:_ [`03-encapsulation.md`](../03-encapsulation.md)

**Goal.** Re-implement `Account` from Chapter 02 with full encapsulation: private balance, a read-only transaction log, and methods that enforce invariants.

**Acceptance criteria:**

- `balance` is a read-only property.
- `deposit(amount)` and `withdraw(amount)` enforce positive amounts and non-negative balance.
- A `transactions` property returns an immutable view of the history.
- No test can mutate the balance or transaction log except through `deposit` / `withdraw`.
- At least 8 tests: happy paths, edge cases (zero, negative amounts), invariant violations.

**Hints:** Use `tuple(self._transactions)` or `copy.copy()` in the `transactions` property. Write tests that try to "cheat" by mutating the returned list.

**Stretch:** Add an `undo_last()` method that reverses the most recent transaction. Think about what invariants this complicates.
