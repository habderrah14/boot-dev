# Mini-project — 10-sets

_Companion chapter:_ [`10-sets.md`](../10-sets.md)

**Goal.** Build `tag-analyzer.js` — a CLI that reads a JSON file of items (each with a `tags` array) and reports tag analytics.

**Acceptance criteria:**

- Reads a JSON file path from CLI arguments.
- Collects all unique tags across all items using a `Set`.
- Prints the total number of unique tags.
- Prints tags sorted alphabetically.
- Finds tags that appear in every item (intersection of all tag sets).
- Finds tags that appear in only one item.

**Hints:**

- Start with a Set of all tags from the first item, then `intersection` with each subsequent item's tags for the "shared by all" query.
- For "appears in only one item," count occurrences with a `Map`, then filter for count === 1.

**Stretch:** Add a `--overlap <file2>` flag that compares tags between two JSON files and prints union, intersection, and difference.
