# The Backend Developer's Companion

A guided, textbook-depth companion to the [Boot.dev Backend Developer Path (Python / TypeScript)](https://www.boot.dev/paths/backend?tech=python-typescript).

This book is not a replacement for the interactive Boot.dev lessons. It is a _parallel reference_ you read alongside the course, giving you:

- Extended explanations of every concept, with the "why" behind the "what".
- Diagrams (Mermaid) you can redraw yourself to cement the mental model.
- Fully-worked code examples that run on your own machine.
- Exercises, solutions, quizzes, and mini-projects that go **beyond** the Boot.dev interactive exercises so your skills generalize.
- Cross-module links so you can trace a single idea (e.g. _state_) through Python, OOP, FP, DSA, and HTTP.

## Who this book is for

- **You are following the Boot.dev path** and want deeper explanations, more practice, or offline reference.
- **You are a self-taught developer** consolidating half-remembered fundamentals.
- **You teach programming** and want a ready-made curriculum to remix.

## How to use this book

Each module folder (`01-python/`, `02-linux/`, …) maps 1:1 to a Boot.dev course. Inside a module you'll find:

- `README.md` — module overview, learning outcomes, and how chapters map to the Boot.dev curriculum.
- `NN-topic.md` — one chapter per Boot.dev lesson chapter, in order.
- `exercises/`, `solutions/`, `mini-projects/` — when exercise or project material is too large to embed inline.

A suggested workflow:

0. If day one feels fuzzy: read [Onboarding](appendix-onboarding.md) and skim [Study habits](appendix-study-habits.md); use [Concept threads](appendix-threads/README.md) when an idea spans modules.
1. Watch / read the Boot.dev lesson.
2. Read the companion chapter here for a deeper take (many chapters include an **In plain terms (newbie lane)** subsection).
3. Do the **exercises** in this book (not just the Boot.dev ones).
4. Build the **mini-project** at the end of the chapter.
5. Take the quiz to confirm retention.

## Table of contents

See [`SUMMARY.md`](SUMMARY.md) for the full chapter-by-chapter index (including [onboarding](appendix-onboarding.md), [system design](appendix-system-design.md), [integration projects](appendix-projects/01-tiny-pastebin.md), and [concept threads](appendix-threads/README.md)).

The backend loop is intentional: **Module 11 (SQL) → Module 12 (HTTP Servers) → Module 13 (File/CDN) → Module 14 (Docker) → Module 15 (Pub/Sub)**. Treat these as production essentials, not optional extras.

## Prerequisites

You need:

- A computer you can install software on (Linux, macOS, or Windows with WSL2).
- A text editor (VS Code, Neovim, etc.).
- A terminal.
- ~12 months of calendar time if you're starting from zero.

Everything else — languages, tools, libraries — is installed as you need it. Each chapter lists its own prerequisites.

## Conventions

- **Voice.** Second-person ("you"). Conversational but technical.
- **Code.** Every snippet uses a language tag and runs as shown on:
  - Python 3.12+
  - Node.js 20+ with TypeScript 5.x
  - C17 (any reasonable GCC/Clang)
  - PostgreSQL 16+ for SQL examples
- **Diagrams.** Mermaid, embedded in Markdown.
- **Exercises** are numbered. Solutions live in `solutions/` or in a collapsible `<details>` block.
- **Quizzes** end each chapter: five multiple-choice + two short-answer.
- **Mini-projects** give you a small buildable thing to ship at chapter's end.

## Scope

This book covers the **16 courses** of the Boot.dev Python/TypeScript backend path. It intentionally **does not** re-implement the 8 guided / portfolio projects (Bookbot, Asteroids, AI Agent, Static Site Generator, Personal Project 1, Pokedex, Blog Aggregator, Capstone) — those are best done directly on Boot.dev where the autograder and lore context live.

If you're studying for junior backend roles, prioritize completing Modules **11–15** as one systems sequence; this is where persistence, API boundaries, deployment, and async workflows connect.

## Status

Work in progress. Core chapter content is drafted across all modules; companion artifacts are being completed module-by-module.

- Progress dashboard: [`PROGRESS.md`](PROGRESS.md)
- Full chapter index: [`SUMMARY.md`](SUMMARY.md)
- Artifact conventions: see "Artifact naming & quality" in [`PROGRESS.md`](PROGRESS.md)

## License

Study-only, personal use. Not affiliated with Boot.dev.
