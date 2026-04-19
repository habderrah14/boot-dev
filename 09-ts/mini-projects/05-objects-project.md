# Mini-project — 05-objects

_Companion chapter:_ [`05-objects.md`](../05-objects.md)

**Goal.** Design a `Product` type with branded `ProductId`. Implement a `ProductIndex` (dictionary by id) with typed `add`, `remove`, and `findById` operations.

**Acceptance criteria:**

- `ProductId` is a branded `number` — plain numbers can't be used as product IDs.
- `findById` returns `Product | undefined`.
- `add` rejects products with duplicate IDs (throw an error).
- `noUncheckedIndexedAccess` enabled.
- Tests cover add, remove, find (existing and missing).

**Hints:**

- A factory function `createProductId(n: number): ProductId` makes the branding ergonomic.
- Use `Record<number, Product>` or an index signature for the index.

**Stretch:** Add a `search(index: ProductIndex, query: Partial<Omit<Product, "id">>): Product[]` that matches products by partial field values.
