# Mini-project — 02-functions

_Companion chapter:_ [`02-functions.md`](../02-functions.md)

**Goal.** Build a typed `filter-users.ts` script that loads a JSON file of users, filters to active admins, and writes the result to a smaller JSON file. Every function must have explicit parameter and return type annotations.

**Acceptance criteria:**

- No use of `any` anywhere.
- At least three functions: `loadUsers`, `filterActiveAdmins`, `writeResults`.
- Each function has explicit parameter types and return type.
- The script runs via `npx tsx filter-users.ts input.json output.json`.

**Hints:**

- Use `unknown` for the parsed JSON and narrow with a type predicate.
- Return `Promise<void>` for async functions with no meaningful return.

**Stretch:** Add a `--role` CLI flag that accepts any role string, and make the filter function generic over the role field.
