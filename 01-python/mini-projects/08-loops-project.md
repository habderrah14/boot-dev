# Mini-project — 08-loops

_Companion chapter:_ [`08-loops.md`](../08-loops.md)

**Goal.** Build `primes.py` — print all primes up to `n` using the Sieve of Eratosthenes, plus a `Counter`-style line that reports density.

**Acceptance criteria.**

- `primes_up_to(n: int) -> list[int]` returns primes ≤ n; raises for `n < 2`.
- Implementation uses a list of booleans and *no* external imports for the sieve itself.
- A `main()` prints the count and the first 10 primes when called as `python3 primes.py 100`.
- Tests verify: primes up to 30 == `[2,3,5,7,11,13,17,19,23,29]`; primes up to 1 raises.
- Sieve is O(n log log n) — note the complexity in the docstring.

**Hints.** Mark indices, then `return [i for i, is_prime in enumerate(sieve) if is_prime]`. Start the inner loop at `i*i` (composites smaller than that have a smaller prime factor).

**Stretch.** Add a `--time` flag that prints how many primes/second your sieve produces for `n = 10^6`.
