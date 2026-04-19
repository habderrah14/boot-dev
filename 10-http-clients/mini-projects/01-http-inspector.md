# Mini-project — HTTP Inspector

## Goal

Build a CLI tool that fetches a URL and prints the response status, headers, and body size.

## Deliverable

A TypeScript script plus README that inspects a URL from the command line.

## Required behavior

1. Accept a URL as an argument.
2. Print the status code and reason phrase.
3. Print every response header.
4. Print body length in bytes.
5. Time out after 5 seconds and exit non-zero on failure.

## Acceptance criteria

- Uses `fetch` or equivalent `http` client API.
- Handles timeout cleanly with a useful message.
- Can inspect both JSON and HTML responses.
- README explains usage and examples.

## Hints

- `response.arrayBuffer()` gives exact byte length.
- Use an `AbortController` for timeout control.
- Consider a `--headers-only` mode as a stretch.

## Stretch goals

1. Add JSON pretty-printing for `application/json`.
2. Add a `--method` flag.
3. Add retry-once behavior for transient network errors.
