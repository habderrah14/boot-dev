# Mini-project — 04-objects

_Companion chapter:_ [`04-objects.md`](../04-objects.md)

**Goal.** Build `obj-utils.js` — a utility module exporting `pick`, `omit`, `deepClone`, and `deepMerge`.

**Acceptance criteria:**

- All four functions work correctly on nested objects.
- `deepClone` handles objects, arrays, Dates, and `null` values.
- `deepMerge` recursively merges objects but replaces arrays wholesale.
- A companion test file (`obj-utils.test.js`) uses `node:test` with at least 3 tests per function.
- `node --test obj-utils.test.js` passes.

**Hints:**

- For `deepClone`, check `typeof val === "object" && val !== null`, then recurse.
- For `deepMerge`, handle the "both sides are plain objects" case specially.

**Stretch:** Add `flattenKeys(obj)` that converts `{ a: { b: 1 } }` to `{ "a.b": 1 }`.
