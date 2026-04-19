# Chapter 15 — Local Development

> The difference between "I wrote TypeScript once" and "TypeScript is part of my flow" is a sane local setup: fast feedback, linting, formatting, tests, debugger.

## Learning objectives

- Set up a TypeScript project with `tsc`, `tsx`, or `ts-node`.
- Configure ESLint + Prettier.
- Use `node:test` or Vitest.
- Debug with source maps.

## Prerequisites & recap

- [Modules](../08-js/15-modules.md), [Types](01-types.md).

## In plain terms (newbie lane)

This chapter is really about **Local Development**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Concept deep-dive

### Project skeleton

```
myapp/
  src/
    index.ts
    math.ts
  test/
    math.test.ts
  package.json
  tsconfig.json
  .eslintrc.cjs
  .prettierrc
```

### `package.json` scripts

```jsonc
{
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "node --test --import=tsx ./test/*.ts",
    "lint": "eslint .",
    "format": "prettier --write ."
  }
}
```

`tsx` is a fast TypeScript runner; great for local dev. `tsc` type-checks and emits JS for production.

### `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "sourceMap": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*.ts"]
}
```

### ESLint + Prettier

```bash
npm i -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier eslint-config-prettier
```

Typical rules: no `any`, consistent type imports, no-unused-vars. Let Prettier own formatting; ESLint owns logic-level rules.

### Tests

Two common choices:

- **Node stdlib** (`node:test` + `--import=tsx`): zero dependency, fast.
- **Vitest** / **Jest**: richer API, coverage.

For backend, `node:test` is usually enough:

```ts
import { test } from "node:test";
import assert from "node:assert";

test("adds", () => assert.strictEqual(1 + 2, 3));
```

### Debugging

With `sourceMap: true`, the debugger maps runtime to `.ts` lines. VS Code:

```json
// .vscode/launch.json
{
  "type": "node",
  "request": "launch",
  "name": "Debug index",
  "program": "${workspaceFolder}/src/index.ts",
  "runtimeArgs": ["--import", "tsx"]
}
```

### Type-check in CI

```yaml
- run: npm ci
- run: npm run lint
- run: npx tsc --noEmit
- run: npm test
```

`tsc --noEmit` is the typecheck step — no JS output, just errors.

### Watch mode

- `tsc --watch` — continuous typecheck.
- `tsx watch src/index.ts` — continuous run with type-stripping (no type checks!).
- `node --watch --import=tsx src/index.ts` — modern alternative.

Combine `tsc --watch --noEmit` in one terminal with `tsx watch` in another.

## Worked examples

### Example 1 — Minimal scripts

```jsonc
{
  "type": "module",
  "scripts": {
    "dev": "node --watch --import=tsx src/index.ts",
    "typecheck": "tsc --noEmit",
    "test": "node --test --import=tsx test/**/*.ts"
  }
}
```

### Example 2 — ESLint config

```js
// .eslintrc.cjs
module.exports = {
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier",
  ],
  rules: {
    "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    "@typescript-eslint/consistent-type-imports": "error",
  },
};
```

## Diagrams

```mermaid
flowchart LR
  edit[src/*.ts] --tsx watch--> run[running process]
  edit --tsc --noEmit--> check[type errors]
  edit --eslint--> lint[lint errors]
  edit --prettier--> format
```

*Caption: Trace the flow (data/time/money) through this figure before reading further.*

## Common pitfalls & gotchas

- `tsx`/`ts-node` skip type checking unless configured. Keep `tsc --noEmit` in CI.
- ESM + CJS mismatches — stick with ESM.
- Forgetting `sourceMap: true` → unmappable stack traces.
- Over-configured `.eslintrc` — start minimal.

## Exercises

1. Warm-up. Scaffold a TS project with `dev`, `build`, `test` scripts.
2. Standard. Add ESLint + Prettier; run on the repo.
3. Bug hunt. Why does `tsx` run code with type errors?
4. Stretch. Configure VS Code launch config to debug `src/index.ts` with breakpoints on `.ts` lines.
5. Stretch++. Add a pre-commit hook (`husky`) that runs lint + typecheck.

## Quiz

1. Typecheck in CI:
    (a) `tsx` (b) `tsc --noEmit` (c) `eslint` (d) `prettier`
2. `tsx`:
    (a) bundler (b) ESM-friendly TS runner, strips types (c) type checker (d) transpiler that enforces types
3. For runtime code in production:
    (a) ship `src/` (b) ship compiled `dist/` (c) run via `tsx` (d) it depends — any is fine
4. Source maps:
    (a) slow code (b) map compiled code back to TS lines (c) replace typechecking (d) runtime only
5. Test runner that ships with Node 20+:
    (a) Jest (b) Mocha (c) `node:test` (d) Vitest

**Short answer:**

6. Why split lint from typecheck in CI?
7. One reason to prefer `node:test` over Jest for small projects.

## Mini-project: Apply it

Full brief (goal, acceptance criteria, hints, stretch): [15-local-development — mini-project](mini-projects/15-local-development-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- `tsx` for runs, `tsc --noEmit` for checks.
- Lint + format + test + sourcemap = happy flow.
- Ship compiled `dist/`, not raw `src/`.

## Further reading

- TypeScript Handbook, *Project Configuration*.
- Next module: [Module 10 — HTTP Clients](../10-http-clients/README.md).
