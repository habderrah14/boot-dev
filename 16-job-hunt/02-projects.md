# Chapter 02 — Projects

> *"A junior resume is 80% projects. Hiring managers can't yet take your word for 'I can build things' — your projects have to say it for you."*

## Learning objectives

By the end of this chapter you will be able to:

- Choose projects that demonstrate the exact skills a target role requires.
- Shape a project to be explainable in 60 seconds to a recruiter and in 15 minutes to a staff engineer.
- Ship projects — reviewers trust ones they can run, read, and criticize.
- Write a project README that does 90% of the resume-screening work for you.
- Distinguish practice projects from portfolio projects.

## Prerequisites & recap

- [Chapter 01: Strategy](01-strategy.md) — you have a target role. Projects need to match it.
- Before you call a repo “portfolio-ready,” run the companion [Shipping checklist](../appendix-shipping-checklist.md) (tests, README, secrets, deploy).

## The simple version

From your perspective, a project is how you practice. From a reviewer's perspective, it's evidence for three questions: Can you write code that works? Can you maintain code over time? Can you make appropriate technical decisions? Most junior portfolios answer only the first question. Projects that also demonstrate maintainability (tests, CI, clean git history) and judgment (documented trade-offs, deliberate technology choices) are what earn interviews.

You need three projects: a substantial deployed app (your headline), a system-y depth piece (signals you understand internals), and a collaboration (OSS contribution or team project — signals you work with humans). Three is enough. More dilutes attention; fewer under-signals.

## Visual flow

```
  ┌────────────┐    ┌────────────┐    ┌────────────┐
  │ Target     │───▶│ Pick 3     │───▶│ Build &    │
  │ Role       │    │ Projects   │    │ Ship       │
  └────────────┘    └────────────┘    └─────┬──────┘
                                            │
                                            ▼
                                     ┌────────────┐
                                     │ Write      │
                                     │ README     │───▶ Resume
                                     │ (decisions,│───▶ Interview
                                     │  demo URL) │
                                     └────────────┘
```
*Figure 2-1. Projects flow from your target role through building and shipping to your resume.*

## Concept deep-dive

### What a project is actually for

From the reviewer's perspective, a project answers three questions:

1. **Can you write code that works?** (Correctness.)
2. **Can you work on code that didn't exist yesterday and still has to exist tomorrow?** (Maintainability.)
3. **Can you choose problems and solutions appropriately?** (Judgment.)

Most junior projects answer #1 only. Projects that also answer #2 and #3 are what get you interviewed.

### The portfolio spine

Not a laundry list — a small, intentional set:

1. **A substantial app** — 1–3 months of work, multiple features, deployed. Your headline.
2. **A system-y piece** — demonstrates a concept from the path (a toy DB, an HTTP client from scratch, a parser, a job queue). Signals depth.
3. **A collaboration** — pull requests to an OSS project, or a project with at least one other contributor. Signals you can work with humans.

### Picking a project that matches the target

Re-read your target statement from chapter 01 and pattern-match:

- **Backend roles** → APIs, auth, databases, a real use case, deployed.
- **Fintech** → correctness, money arithmetic (decimals, not floats), auditability.
- **Dev tools** → CLIs, libraries, good docs, tests.
- **Data-adjacent** → pipelines, batch jobs, schema design.

Bad match example: a Chrome extension portfolio applied to "backend engineer at a payments company." The reviewer has no on-ramp to believe you.

### Ship > finish

A deployed 80%-complete app trumps an undeployed "perfect" one. Shipping forces you to confront config, secrets, build pipelines, hosting cost, and observability — exactly the skills backend roles care about. A live URL on your resume is worth roughly one round of interviews.

### The README that does the work

Reviewers skim. A good README opens every door before they've clicked into the code:

1. **One-line description** — what this is, in plain language.
2. **Screenshot / demo link** — evidence it runs.
3. **Why** — the problem it solves. Keep it real.
4. **Architecture** — a diagram and 3–5 bullets on how the pieces interact.
5. **Key decisions** — 3–5 trade-offs you made and why. This is where reviewers form opinions.
6. **Local setup** — commands a stranger can paste and see it run.
7. **Tests** — how to run them, coverage philosophy.
8. **What's next** — roadmap, known limitations. Shows judgment.

The "Key decisions" section is where you win or lose the interview. "I chose Postgres over MongoDB because the data is relational and I need ACID across the orders table" beats "I used Postgres."

### Anti-patterns

- **Todo apps / CRUD clones** with no differentiator.
- **"AI wrapper" with no real product** — every reviewer has seen 200.
- **Copy of a tutorial** with the same file structure as the tutorial.
- **Gigantic monorepo** of half-started ideas.
- **Never deployed**, with `TODO` peppered through the README.
- **14 technologies for a 200-line app** — signals lack of judgment.

### Depth signals that interviewers love

- Tests run in CI and you *removed* a flaky test (not just added tests).
- A real database, not SQLite-in-memory (for a backend role).
- A README explaining why you *didn't* use feature X.
- Release tags or a changelog.
- An issue you filed on yourself ("v2 idea: pagination cursors").
- At least one refactor visible in git history.

### Open-source contribution

One merged PR to a real project is worth a project of its own. Track these criteria: did you fix a real issue (not docs-only)? Was the PR non-trivial (>20 lines, non-cosmetic)? Did you interact with maintainers (review cycles)?

If all three: it goes on the resume. If not: it's practice, not signal. A realistic target: one merged non-trivial PR in 6 weeks.

## Why these design choices

**Why only three projects?** Because attention is scarce. A reviewer with 30 seconds will skip past a list of 15 repos and click on nothing. Three curated, well-documented projects with live demos concentrate the signal.

**Why "ship" over "finish"?** Because the gap between 80% and 100% is where most projects die. Shipping teaches you deployment, monitoring, and the messy reality of production — the exact skills employers value. An undeployed perfect app teaches you nothing about ops.

**Why the README matters more than the code?** Because the README is read first. A reviewer who reads a strong README will *look for reasons to like your code*. A reviewer who sees a weak README (or none) will *look for reasons to skip you*. First impressions are asymmetric.

**When you'd pick differently:** If you're applying for a role that values deep algorithmic work (ML, systems programming), a single deep project with benchmarks and a paper-quality writeup may outweigh three breadth projects.

## Production-quality code

### README template

```markdown
# [Project Name]

[One-line description of what this is and who it's for.]

**Live demo:** [URL]
**Video walkthrough:** [URL, if applicable]

## Why

[2–3 sentences: the real problem this solves. Not "to learn X"
but "because existing tools don't handle Y well."]

## Architecture

[ASCII diagram or link to diagram]

- **HTTP layer:** [framework] + [validation library]
- **Auth:** [approach and why]
- **Storage:** [database] + [driver/ORM]
- **Deployment:** [platform], containerized with [Docker/etc.]

## Key decisions

- **[Decision 1]** — [what you chose], because [why].
  Alternative considered: [what you didn't choose and why not].
- **[Decision 2]** — ...
- **[Decision 3]** — ...

## Local setup

[Exact commands to clone, install, configure, and run.]

## Tests

[How to run tests. Coverage philosophy: "I test business logic
and API boundaries; I don't test framework glue."]

## What's next

- [ ] [Feature or improvement you'd add with more time]
- [ ] [Known limitation you'd address]
```

### Portfolio audit checklist

```
For each project, verify:
[ ] One-line description is clear to a non-engineer
[ ] Live demo URL works (or recording exists)
[ ] README has all 8 sections
[ ] "Key decisions" section has 3+ entries with trade-offs
[ ] Tests exist and run in CI
[ ] Git history shows 20+ commits with at least one refactor
[ ] No secrets in the repository (run a secrets scanner)
[ ] Dependencies are not wildly outdated
```

## Security notes

N/A — this chapter covers portfolio strategy, not software security.

## Performance notes

N/A — project "performance" is measured by interview conversion, covered in the metrics discussion.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Scope creep: 3-month project never ships | Perfectionism or feature addiction | Set a 3-week deadline for v1; deploy at 80% complete; iterate after |
| Tutorial lookalike: identical file names and structure to the course material | Followed the tutorial without diverging | Rename, restructure, add features the tutorial didn't cover, deploy |
| Private repo: reviewer can't see your code | Forgot to make it public, or left it private "until it's ready" | Make it public now; "ready" is the enemy of "visible" |
| README is an afterthought: 3 lines, no decisions, no demo link | Treating documentation as optional | Write the README *before* you consider the project done |
| No tests anywhere | "I know it works" mentality | Add tests for business logic and API boundaries; run them in CI |

## Practice

**Warm-up.** Pick your three portfolio projects. Write one-liner descriptions for each, aligned with your target statement.

<details><summary>Show solution</summary>

Example for a backend-focused junior targeting fintech:
1. **Ledger API** — A double-entry bookkeeping REST API with Postgres and decimal arithmetic.
2. **Tiny Queue** — A Redis-backed job queue with retries and DLQ, inspired by RabbitMQ.
3. **OSS PR** — Fixed a race condition in an open-source retry library (merged).

Each one-liner connects to the target: fintech (ledger), systems depth (queue), collaboration (OSS).

</details>

**Standard.** Rewrite the README of your best existing project using the 8-section structure above. Ask a non-engineer if they understand sections 1–3.

<details><summary>Show solution</summary>

The test: your non-engineer friend reads the first three sections and can tell you (1) what the project does, (2) that it's live, and (3) why you built it. If they can't, rewrite those sections in plainer language.

</details>

**Bug hunt.** A friend's project has "solid code, no callbacks." Audit their GitHub: what's missing that would make it interview-ready?

<details><summary>Show solution</summary>

Common gaps: no README or a 3-line README; no live demo; no tests; no CI; no "Why" or "Decisions" sections; README lists features but the code doesn't build on a fresh clone. Fixing those is usually a weekend's work.

</details>

**Stretch.** Find one realistic "good first issue" on a medium-sized OSS project (500+ stars, active maintainers). Leave a comment asking to claim it.

<details><summary>Show solution</summary>

Search GitHub for `label:"good first issue" language:TypeScript stars:>500` (or your target language). Read 5 issues. Pick one where you understand the codebase enough to contribute. Comment: "I'd like to work on this. I've read the contributing guide and reviewed the relevant code. My approach would be [brief plan]. Let me know if that works."

</details>

**Stretch++.** Ship a tiny v1 (≤ 2 weeks). Deploy it. Add a live URL to your README. Share it somewhere public.

<details><summary>Show solution</summary>

Timebox aggressively: week 1 build core features, week 2 deploy and polish README. Deploy on Fly.io, Railway, or Render (all have free tiers). Share the link on your LinkedIn, a relevant Discord, or Hacker News "Show HN."

</details>

## In plain terms (newbie lane)
If `Projects` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. A project's primary job on your resume is to:
    (a) prove you can write code (b) prove you have judgment, can ship, and can maintain (c) list technologies (d) impress your friends

2. Recommended portfolio size:
    (a) 1 massive project (b) 3 intentional projects (c) 15 small ones (d) 7 tutorial clones

3. A deployed 80% project vs an undeployed "perfect" one:
    (a) deployed wins (b) perfect wins (c) tie (d) undeployed is always better

4. The README section that most influences interview invites:
    (a) features list (b) key decisions + why (c) license file (d) contributor list

5. A useful OSS contribution is:
    (a) a typo fix in the README (b) a non-trivial PR with maintainer interaction (c) a fork you never pushed (d) starring the repo

**Short answer:**

6. Describe how to match project choice to target role with one concrete example.

7. Why does a "14 technologies for 200 LOC" project read as a *negative* signal?

*Answers: 1-b, 2-b, 3-a, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [02-projects — mini-project](mini-projects/02-projects-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Integration projects (cross-module builds)](../appendix-projects/README.md) — tie every earlier module into interview stories.
  - [System design primer](../appendix-system-design.md) — vocabulary for scaling conversations post-modules.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Three intentional projects, aligned to a target role, deployed, and well-documented.
- "Key decisions" + a live demo URL = most of the signal a reviewer needs.
- OSS contributions count when they're non-trivial, reviewed, and merged.
- Ship at 80% — the gap between 80% and 100% is where portfolios go to die.

## Further reading

- [How to write a README](https://www.makeareadme.com/).
- [First Contributions](https://firstcontributions.github.io/) — OSS starter pointers.
- Dan Abramov, ["Things I Don't Know as of 2018"](https://overreacted.io/things-i-dont-know-as-of-2018/) — a model for speaking honestly about your skills.
- Next: [GitHub profile](03-github-profile.md).
