# Chapter 09 — Errors

> "JavaScript's error model is minimal — one `Error` class, a few subclasses — which means most of the discipline is yours."

## Learning objectives

By the end of this chapter you will be able to:

- Throw and catch errors using `try/catch/finally`.
- Use built-in Error subclasses and create custom ones.
- Chain errors with `cause` for debuggable error trails.
- Handle errors in async code with `async/await` and promise chains.
- Decide when to throw vs. return a sentinel value.

## Prerequisites & recap

- [Functions](03-functions.md) — `try/catch` scope, arrow functions.
- [Classes](05-classes.md) — `extends` for custom error classes.

## The simple version

When something goes wrong at runtime — a network request fails, a file is missing, an argument is invalid — you signal the problem by **throwing** an error. The runtime unwinds the call stack until it finds a `try/catch` block willing to handle it. If nothing catches the error, the program crashes. That's actually a good thing — a crash with a stack trace is vastly better than silent corruption.

The key discipline is this: throw `Error` objects (never strings or numbers), catch only what you can meaningfully handle, and re-throw everything else. Don't swallow errors with empty `catch` blocks — they hide bugs that will bite you later in production.

## In plain terms (newbie lane)

This chapter is really about **Errors**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>


## Visual flow

```
  Error flow through the call stack:

  main()
    └── handler(req)
          └── fetchUser(id)
                └── throw new NotFoundError("user 42")
                          │
  Stack unwinds ◄─────────┘
                          │
  handler(req)            │
    try {                 │
      fetchUser(id) ◄─────┘  caught here!
    } catch (err) {
      if (err instanceof NotFoundError)
        return { status: 404 };
      throw err;    ────────────►  re-thrown to main()
    } finally {
      cleanup();    ← always runs
    }

  Error chaining with cause:
  ┌───────────────────────────────────────┐
  │ ApiError: "payment failed"            │
  │   cause: TypeError: "x is not a fn"  │
  │     cause: ...                        │
  └───────────────────────────────────────┘
```

*Figure 9-1. Stack unwinding, catch-and-rethrow, and error chaining.*

## Concept deep-dive

### Throwing errors

```js
throw new Error("something went wrong");
```

You *can* throw anything (`throw "oops"`, `throw 42`), but **always throw `Error` instances**. Only `Error` objects carry a stack trace and support `instanceof` checks — both essential for debugging.

**Why does JavaScript let you throw anything?** Historical permissiveness. The language doesn't enforce types anywhere, errors included. But every linter, style guide, and experienced developer agrees: throw `Error` descendants only.

### Built-in error subclasses

| Error type | When the engine throws it |
|---|---|
| `TypeError` | Wrong type — calling a non-function, reading property of `undefined`/`null` |
| `RangeError` | Value out of valid range — invalid array length, stack overflow |
| `SyntaxError` | Parser-level — malformed code (caught at parse time, not runtime) |
| `ReferenceError` | Undeclared variable or TDZ violation |
| `URIError` | Malformed URI in `decodeURI`, etc. |

### Custom errors

```js
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

class NotFoundError extends Error {
  constructor(resource, id) {
    super(`${resource} ${id} not found`);
    this.name = "NotFoundError";
    this.resource = resource;
    this.id = id;
  }
}
```

**Why set `this.name`?** By default, subclasses inherit `name: "Error"`. Setting it explicitly makes stack traces readable — you'll see `ValidationError: age must be positive` instead of `Error: age must be positive`.

### Catching errors

```js
try {
  riskyOperation();
} catch (err) {
  if (err instanceof ValidationError) {
    console.warn(`Validation failed on ${err.field}: ${err.message}`);
  } else {
    throw err;   // DON'T swallow errors you didn't expect
  }
} finally {
  cleanup();     // always runs — success, error, or re-throw
}
```

ES2019+ allows catch without a binding when you don't need the error object:

```js
try { JSON.parse(input); } catch { return null; }
```

**Why re-throw?** If your catch block handles `ValidationError` but a `TypeError` sneaks in, swallowing it hides a real bug. The pattern is: catch specific errors, re-throw everything else.

### Error chaining with `cause`

```js
try {
  rawDatabaseQuery(sql);
} catch (err) {
  throw new Error("query failed", { cause: err });
}
```

The `cause` property (ES2022) chains errors together. When you inspect the error, you see both the high-level message and the root cause. This is invaluable for debugging — you know *what* went wrong (your API layer) and *why* (the database driver).

### Async error handling

With `async/await`, `try/catch` works exactly as you'd expect:

```js
async function loadUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to load user:", err);
    throw err;
  }
}
```

With `.then()` chains:

```js
fetch(url)
  .then(res => res.json())
  .then(data => process(data))
  .catch(err => console.error(err));
```

**Critical:** Unhandled promise rejections crash the process in Node 15+. Every promise chain must end with `.catch()`, and every `await` should be in a `try/catch` at the boundary.

### When NOT to throw

Exceptions are for **exceptional** conditions — things that shouldn't happen in normal flow. If "not found" is a normal, expected response:

```js
// DON'T throw for expected outcomes
function findUser(id) {
  const user = db.get(id);
  if (!user) return null;     // sentinel value — caller checks
  return user;
}

// DO throw for broken invariants
function requireUser(id) {
  const user = db.get(id);
  if (!user) throw new NotFoundError("user", id);
  return user;
}
```

The caller decides whether "not found" is normal or exceptional.

## Why these design choices

| Design choice | Trade-off | When you'd pick differently |
|---|---|---|
| Throw-and-catch model | Stack unwinds implicitly — hard to reason about control flow | Rust's `Result<T, E>` makes errors explicit in the return type |
| Single `Error` base class | No typed error hierarchy out of the box | Java's checked exceptions force callers to handle specific types |
| `cause` chaining (ES2022) | Not available in older runtimes | Use a `details` property as a fallback |
| Unhandled rejection = crash | Strict but safe | Some frameworks catch globally and log instead |
| `finally` always runs | Can mask the original error if `finally` throws | Keep `finally` blocks simple — cleanup only |

## Production-quality code

```js
class AppError extends Error {
  constructor(message, { code, statusCode = 500, cause } = {}) {
    super(message, { cause });
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
  }
}

class ValidationError extends AppError {
  constructor(message, field, { cause } = {}) {
    super(message, { code: "VALIDATION_ERROR", statusCode: 400, cause });
    this.field = field;
  }
}

class NotFoundError extends AppError {
  constructor(resource, id, { cause } = {}) {
    super(`${resource} ${id} not found`, { code: "NOT_FOUND", statusCode: 404, cause });
    this.resource = resource;
    this.id = id;
  }
}

class AuthError extends AppError {
  constructor(message = "unauthorized", { cause } = {}) {
    super(message, { code: "AUTH_ERROR", statusCode: 401, cause });
  }
}

async function retry(fn, { attempts = 3, delay = 100, backoff = 2 } = {}) {
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === attempts - 1) throw err;
      await new Promise(r => setTimeout(r, delay * backoff ** i));
    }
  }
}

function parseAge(input) {
  const n = Number(input);
  if (Number.isNaN(n)) {
    throw new ValidationError("age must be numeric", "age");
  }
  if (n < 0 || n > 150) {
    throw new ValidationError("age out of range (0-150)", "age");
  }
  return n;
}
```

## Security notes

- **Don't expose internal errors to clients.** Stack traces, SQL queries, and file paths in error messages help attackers. Log the full error server-side; return a generic message to the client.
- **Don't use error messages for control flow.** Matching error messages with string comparison (`err.message === "not found"`) is fragile and bypassable. Use `instanceof`, error codes, or status codes.
- **Validate before throwing.** A `ValidationError` should describe what's wrong without echoing back user input verbatim (XSS risk if the error message is rendered in HTML).

## Performance notes

- Throwing errors is expensive — the engine captures the entire call stack. Don't use exceptions for expected control flow (like "value not found"). Return `null`, `undefined`, or a result object instead.
- `try/catch` blocks themselves have near-zero overhead in modern engines when no error is thrown. The V8 JIT optimizes the happy path.
- Deeply nested `try/catch` blocks don't add measurable cost, but they do add cognitive cost. Prefer a single boundary catch at the outermost layer.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Silent bug — error disappeared | Empty `catch (e) {}` swallows everything | Always log or re-throw; never leave catch blocks empty |
| No stack trace in error output | Threw a string instead of an `Error` object | Always throw `new Error(msg)` or a subclass |
| Unhandled promise rejection crashes Node | Forgot `await` or `.catch()` on a promise | Add `try/catch` around `await` or `.catch()` at the chain end |
| Catching too broadly — can't tell what went wrong | Single catch handles all error types | Use `instanceof` checks and re-throw unrecognized errors |
| Error has wrong `name` in stack trace | Custom error didn't set `this.name` | Add `this.name = this.constructor.name` in the constructor |

## Practice

**Warm-up.** Throw a `TypeError`, catch it, and print the message and stack trace.

**Standard.** Define a `NotFoundError` subclass with `resource` and `id` properties. Throw and catch it, using `instanceof` to distinguish it from other errors.

**Bug hunt.** Explain why `catch (e) {}` (empty body) is dangerous and what bug it hides in this code:

```js
try {
  const data = JSON.parse(userInput);
  processData(dta);  // typo!
} catch (e) {}
```

**Stretch.** Wrap a `fetch` call with `try/catch`, re-throw with `cause`, and write a handler that logs the full cause chain.

**Stretch++.** Implement a global `process.on("unhandledRejection", handler)` that logs the error and exits with code 1. Test it by creating an unhandled promise rejection.

<details><summary>Show solutions</summary>

**Bug hunt.**

```js
// The typo `dta` (instead of `data`) throws a ReferenceError.
// The empty catch swallows it silently — the code appears to work
// but processData is never called and no error is logged.
// Fix: at minimum, log the error; better yet, re-throw unexpected errors.
try {
  const data = JSON.parse(userInput);
  processData(data);
} catch (e) {
  if (e instanceof SyntaxError) {
    console.warn("Invalid JSON:", e.message);
  } else {
    throw e;  // ReferenceError from the typo now surfaces
  }
}
```

**Stretch.**

```js
async function fetchWithContext(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    throw new Error(`Failed to fetch ${url}`, { cause: err });
  }
}

function logCauseChain(err, depth = 0) {
  console.error("  ".repeat(depth) + `${err.name}: ${err.message}`);
  if (err.cause) logCauseChain(err.cause, depth + 1);
}
```

</details>

## Quiz

1. You should prefer throwing:
    (a) Strings
    (b) Numbers
    (c) `Error` instances or subclasses
    (d) Plain objects

2. The built-in error for a wrong type is:
    (a) `TypeError`
    (b) `RangeError`
    (c) `ReferenceError`
    (d) `SyntaxError`

3. Async error handling with `await` uses:
    (a) `.catch()` only
    (b) `try/catch`
    (c) Both work
    (d) `throw` only

4. Custom errors are created by:
    (a) `class MyError extends Error {}`
    (b) `new Error("x", { code: 1 })`
    (c) `function MyError() {}`
    (d) Not possible in JavaScript

5. Unhandled promise rejection in Node 20+:
    (a) Is silent
    (b) Logs a warning only
    (c) Crashes the process by default
    (d) Is not supported

**Short answer:**

6. Why use `cause` when re-throwing errors?
7. Why should you avoid throwing for expected "not found" results?

*Answers: 1-c, 2-a, 3-c, 4-a, 5-c. 6 — `cause` preserves the original error's stack trace and message, creating a chain that shows both what went wrong at the high level and the root cause. 7 — Throwing is expensive (captures stack trace) and forces callers into try/catch; returning `null` or a result object is cheaper and makes the "not found" case explicit in the return type.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [09-errors — mini-project](mini-projects/09-errors-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [TypeScript narrowing](../09-ts/10-type-narrowing.md) — turning runtime knowledge into compile-time proofs.
  - [HTTP clients](../10-http-clients/README.md) — where Promises meet the network.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Always throw `Error` subclasses — they carry stack traces and support `instanceof`.
- Catch only what you can handle; re-throw everything else.
- Use `cause` (ES2022) to chain errors and preserve the debugging trail.
- `async/await` + `try/catch` is the modern error-handling pattern; every promise must be caught.

## Further reading

- MDN, *Error*.
- MDN, *Error: cause*.
- Node.js docs, *Errors*.
- Next: [Sets](10-sets.md).
