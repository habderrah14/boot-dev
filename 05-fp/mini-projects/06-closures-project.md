# Mini-project — 06-closures

_Companion chapter:_ [`06-closures.md`](../06-closures.md)

**Goal.** Build `make_bank(initial_balance)` returning four closures: `balance()`, `deposit(amount)`, `withdraw(amount)`, and `history()`. All state is private — no classes, no globals.

**Acceptance criteria:**

- [ ] `balance()` returns current balance.
- [ ] `deposit(amount)` adds to balance and returns new balance. Rejects non-positive amounts.
- [ ] `withdraw(amount)` subtracts from balance if sufficient funds. Returns new balance or raises `ValueError`.
- [ ] `history()` returns a list of `(action, amount, resulting_balance)` tuples.
- [ ] No class, no global — all state lives in closures.
- [ ] At least five unit tests covering: deposit, withdraw, overdraft rejection, history tracking, multiple accounts don't interfere.

**Hints:**

- Use a list for history — captured by reference, so `append` works without `nonlocal`.
- You *do* need `nonlocal` for the balance variable since you reassign it.

**Stretch:** Add a `transfer(from_bank, to_bank, amount)` function that atomically moves money between two closure-based accounts.
