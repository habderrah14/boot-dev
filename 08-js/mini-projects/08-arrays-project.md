# Mini-project — 08-arrays

_Companion chapter:_ [`08-arrays.md`](../08-arrays.md)

**Goal.** Build `pipeline.js` — a data-processing CLI that loads a JSON array of orders and computes summary statistics.

**Acceptance criteria:**

- Reads a JSON file of orders (each with `customer`, `amount`, `date`, `items`).
- Computes: total revenue, average order value, top 5 customers by total spend.
- Groups orders by date and prints items-per-day counts.
- Uses only non-mutating array methods (no `sort()` — use `toSorted()` or `[...arr].sort()`).
- Output is formatted as a readable table in the terminal.

**Hints:**

- `reduce` for aggregation, `map` for transformation.
- `Object.entries(groupBy(...))` for the per-day breakdown.
- `toSorted((a, b) => b.total - a.total).slice(0, 5)` for top 5.

**Stretch:** Accept an optional `--filter` flag to include only orders above a minimum amount.
