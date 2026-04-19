# Chapter 01 — Types

> "TypeScript is JavaScript plus a type checker. The code you write and ship is JS; the types exist to catch bugs and document intent *before* runtime."

## Learning objectives

By the end of this chapter you will be able to:

- Annotate variables and function signatures with TypeScript types.
- Use the primitive, literal, array, object, and `unknown`/`any` types correctly.
- Explain why type inference means you annotate less than you think.
- Run the TypeScript compiler with a sensible `tsconfig.json`.

## Prerequisites & recap

- [Module 08 — JavaScript](../08-js/README.md) — you should be comfortable with JS variables, functions, and basic control flow.

## The simple version

Think of types as labels you stick on your values. When you write `let age: number = 36`, you're telling TypeScript "this variable will always hold a number — yell at me if I ever try to put something else in here." The compiler reads those labels, checks that everything lines up, and then *strips them out* before your code runs. You ship plain JavaScript; the types only exist during development to catch mistakes early.

The best part? TypeScript is smart enough to figure out most labels on its own. When you write `const name = "Ada"`, it already knows that's a string. You only need to be explicit at the edges — function parameters, return types, and public APIs — and let inference handle the rest.

## In plain terms (newbie lane)

This chapter is really about **Types**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  ┌──────────┐     ┌───────────┐     ┌──────────┐
  │  .ts file │────▶│    tsc    │────▶│  .js file │──▶ node / browser
  │  (typed)  │     │  (check)  │     │ (no types)│
  └──────────┘     └─────┬─────┘     └──────────┘
                         │
                    type errors
                   (compile-time)
```
*Figure 1-1. TypeScript checks at compile time, then erases types to produce plain JS.*

## Concept deep-dive

### Primitive types — the building blocks

TypeScript has seven primitive types that mirror JavaScript's runtime values:

```ts
let n: number = 3.14;
let i: bigint = 10n;
let s: string = "hi";
let b: boolean = true;
let u: undefined = undefined;
let x: null = null;
let y: symbol = Symbol();
```

Why does this matter? Every value you'll ever work with traces back to one of these primitives or to an object built from them. Knowing which primitive you're dealing with lets the compiler check that you're calling the right methods — you can't call `.toUpperCase()` on a number, and TypeScript will catch that before your users do.

### Type inference — let the compiler work for you

TypeScript infers types from assignments. You rarely need to annotate local variables:

```ts
const age = 36;         // TypeScript knows this is number
const name = "Ada";     // TypeScript knows this is string
```

Why trust inference? Because explicit annotations on every local variable add visual noise without adding safety. The compiler already knows `36` is a number. Your job is to annotate at *boundaries* — function parameters, return types, and exported declarations — where inference can't reach or where you want documentation for other developers.

```ts
function greet(name: string): string {
  return `hi, ${name}`;
}
```

### Literal types — when a type is a specific value

Sometimes a variable shouldn't hold *any* string — it should hold one of a few specific strings:

```ts
let mode: "dev" | "prod" = "dev";
mode = "staging";   // error: "staging" is not "dev" | "prod"
```

Literal types make illegal states unrepresentable. Instead of checking at runtime whether someone passed a valid mode, the compiler rejects bad values at write time.

### Array and tuple types

```ts
const nums: number[] = [1, 2, 3];
const ids: Array<number> = [1];          // generic form — same thing
const pair: [string, number] = ["ada", 36];  // tuple: fixed length, typed per position
```

### Object types

```ts
const user: { id: number; name: string } = { id: 1, name: "Ada" };
```

For reusable shapes, give them a name with an interface or type alias:

```ts
interface User { id: number; name: string; }
type Id = number;
```

### `any` vs. `unknown` — the safety spectrum

- **`any`** disables type checking entirely. It's a trapdoor: anything goes, nothing is checked. Treat it as technical debt.
- **`unknown`** is "I don't know what this is *yet*." You must narrow it before using it, which forces you to prove safety.

```ts
let x: unknown = JSON.parse(s);
if (typeof x === "string") x.toUpperCase();  // safe — narrowed to string
```

Why prefer `unknown`? Because `any` lets bugs through silently. `unknown` says "I'll figure this out, but I'll do it safely."

### Running TypeScript — your first project

```bash
npm init -y
npm install --save-dev typescript @types/node
npx tsc --init           # generates tsconfig.json
```

A sensible `tsconfig.json`:

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "dist"
  },
  "include": ["src/**/*.ts"]
}
```

`strict: true` is non-negotiable. It enables a suite of flags (`strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and more) that make types actually useful. Disabling it because something is inconvenient is like wearing a seatbelt but leaving it unbuckled.

## Why these design choices

**Why structural typing?** TypeScript checks *shape*, not *name*. If two types have the same fields, they're compatible. This matches how JavaScript actually works — duck typing — and avoids the ceremony of nominal type hierarchies found in Java or C#.

**Why erase types?** Types are a development-time tool. By erasing them, TypeScript guarantees zero runtime overhead and full interop with existing JS libraries. The trade-off is that you can't do runtime type checks based on TS types alone (you need runtime validation libraries for that).

**When would you pick differently?** If you need runtime type information (e.g., serialization, validation), pair TypeScript with a runtime schema library like Zod or ArkType. TypeScript alone can't protect you at runtime boundaries like API inputs or JSON parsing.

## Production-quality code

```ts
import { readFile } from "node:fs/promises";

interface Config {
  readonly host: string;
  readonly port: number;
  readonly debug: boolean;
}

async function loadConfig(path: string): Promise<Config> {
  const raw: unknown = JSON.parse(await readFile(path, "utf-8"));

  if (
    typeof raw !== "object" || raw === null ||
    !("host" in raw) || typeof (raw as Record<string, unknown>).host !== "string" ||
    !("port" in raw) || typeof (raw as Record<string, unknown>).port !== "number" ||
    !("debug" in raw) || typeof (raw as Record<string, unknown>).debug !== "boolean"
  ) {
    throw new Error(`Invalid config at ${path}`);
  }

  return raw as Config;
}
```

This code receives `unknown` from `JSON.parse`, narrows it with runtime checks, and only then asserts it's a `Config`. Compare to the lazy version that uses `as Config` with no checks — that compiles fine but crashes in production when the JSON is malformed.

## Security notes

- **`any` is a security risk.** If an API handler types its input as `any`, you skip validation entirely. Attackers can send unexpected payloads that slip through unchecked. Always type external input as `unknown` and validate.
- **Type erasure means no runtime protection.** TypeScript types don't exist at runtime. Never rely on a type annotation to prevent malicious input — pair with runtime validation at trust boundaries.

## Performance notes

N/A — TypeScript types are erased at compile time and have zero runtime cost. The `tsc` compiler itself adds a build step (typically 1–10 seconds for moderate projects), but the emitted JavaScript is identical in performance to hand-written JS.

## Common mistakes

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | No type errors on obviously wrong code | Variable or parameter typed as `any` | Change to `unknown` and narrow |
| 2 | `Property 'x' does not exist on type '{}'` on parsed JSON | Used `JSON.parse()` which returns `any` (or `unknown` with strict) without narrowing | Narrow with `typeof`/`in` checks or use a validation library |
| 3 | Massive annotation noise in local variables | Over-annotating — adding types to every `const` | Remove annotations on locals; let inference carry |
| 4 | `Cannot find name 'Buffer'` or similar Node globals | Missing `@types/node` | `npm install --save-dev @types/node` |
| 5 | `strict` disabled because "it's easier" | Short-term convenience over long-term safety | Enable `strict: true` from day one; fix errors properly |

## Practice

**1. Warm-up.** Run `npx tsc --init`, create `src/add.ts` with a typed `add(a: number, b: number): number` function, compile with `npx tsc`, and run the output with `node dist/add.js`.

**2. Standard.** Write a function that accepts a `color: "red" | "green" | "blue"` parameter and returns a hex string. Use a `switch` statement and verify the compiler rejects `"purple"`.

**3. Bug hunt.** What's wrong with this code? Why does it compile but fail at runtime?

```ts
function getLength(x: any) {
  return x.length;
}
getLength(42);
```

**4. Stretch.** Write a function that takes an `unknown` value and narrows it to a `User` object (with `id: number` and `name: string` fields) using `typeof` and `in` checks.

**5. Stretch++.** Enable `noUncheckedIndexedAccess` in your `tsconfig.json` and fix every resulting error in a small codebase. Document what each fix teaches you.

<details><summary>Solutions</summary>

**1.** `src/add.ts`:
```ts
function add(a: number, b: number): number {
  return a + b;
}
console.log(add(2, 3));
```

**2.**
```ts
function toHex(color: "red" | "green" | "blue"): string {
  switch (color) {
    case "red":   return "#ff0000";
    case "green": return "#00ff00";
    case "blue":  return "#0000ff";
  }
}
```

**3.** `any` disables type checking, so `x.length` is assumed valid even when `x` is `42`. At runtime, `(42).length` is `undefined`. Fix: type `x` as `unknown` and narrow, or as `string | unknown[]`.

**4.**
```ts
function isUser(x: unknown): x is { id: number; name: string } {
  return (
    typeof x === "object" && x !== null &&
    "id" in x && typeof (x as Record<string, unknown>).id === "number" &&
    "name" in x && typeof (x as Record<string, unknown>).name === "string"
  );
}
```

**5.** After enabling the flag, every `arr[i]` becomes `T | undefined`. Fix by adding null checks (`if (item !== undefined)`) or using `??` fallbacks.

</details>

## Quiz

1. When you don't know a value's type, you should use:
   (a) `any`  (b) `unknown`  (c) `null`  (d) `void`

2. `strict: true` in `tsconfig.json`:
   (a) Slows compilation  (b) Enables stricter checks; recommended  (c) Rejects all JS files  (d) Disables JSX

3. A tuple `[string, number]` is:
   (a) An array of mixed types  (b) A fixed-length array typed per position  (c) An object  (d) A union

4. Type inference means:
   (a) The compiler is rarely correct  (b) It fails for primitives  (c) It usually works — annotate at boundaries  (d) It's disabled by `strict`

5. To use an `unknown` value as a `string`, you must:
   (a) Cast with `as string` without checks  (b) Narrow with `typeof` first  (c) Use `any` instead  (d) Call `JSON.parse`

**Short answer:**

6. Why should you annotate function boundaries but not local variables?
7. Give one reason `strict` mode is worth adopting from day one.

*Answers: 1-b, 2-b, 3-b, 4-c, 5-b. 6 — Function boundaries are public contracts other code depends on; inference handles locals safely. 7 — It catches null/undefined bugs, implicit `any`, and other issues that are harder to fix retroactively in a large codebase.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-types — mini-project](mini-projects/01-types-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [HTTP servers in TypeScript](../12-http-servers/README.md) — types meet request/response boundaries.
  - [Runtime validation](../10-http-clients/10-runtime-validation.md) — when `unknown` enters your trust boundary.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- TypeScript adds a static type checker on top of JavaScript; types are erased at compile time.
- Annotate at boundaries (function parameters, return types, exports); trust inference inside function bodies.
- Prefer `unknown` over `any` — it forces safe narrowing instead of silent failures.
- Always enable `strict: true` from the start.

## Further reading

- [TypeScript Handbook — Basic Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
- [TypeScript `strict` mode explained](https://www.typescriptlang.org/tsconfig#strict)
- Next: [Functions](02-functions.md)
