# Chapter NN — Title

> One-sentence hook that tells the reader why this chapter matters.

## Learning objectives

By the end of this chapter you will be able to:

- Objective 1 (action verb + observable outcome).
- Objective 2.
- Objective 3.
- Objective 4.

## Prerequisites & recap

You should already be comfortable with:

- Prereq 1 (link to earlier chapter).
- Prereq 2.

A 2–3 sentence recap of the one idea from the previous chapter that this one builds on.

## The simple version

The plain-language mental model — 1–2 paragraphs. After reading just this section, the reader should be able to explain the concept to a friend in 60 seconds. No code yet, no edge cases, no jargon you haven't introduced. Just the right *picture*.

## In plain terms (newbie lane)

Optional but recommended for every **course-mapped** chapter:

- **One paragraph** restating the chapter in workload language: what problem disappears after you understand this?
- Link first-use jargon to [`GLOSSARY.md`](../GLOSSARY.md) where helpful.

> **Newbies often think:** *one concrete wrong mental model tied to this chapter.*  
> **Actually:** *the truthful replacement model in one sentence.*

Details for environment and tooling: [Onboarding](../appendix-onboarding.md) · cadence: [Study habits](../appendix-study-habits.md).

<details><summary>Pause and predict</summary>

Ask one question the reader can answer **before** reading the deep-dive (hide the answer later in the chapter or in exercises).

</details>

## Visual flow

A one-line caption above the diagram explaining what it shows.

```
 Input ──▶ Step 1 ──▶ Step 2 ──▶ Output
            │
            └─ side effect
```

ASCII / Unicode box-drawing only. Keep under 80 columns. Add a second diagram inline later if useful — this one anchors the chapter.

**Diagram caption rule:** one italic line under every figure saying **what to trace with your finger** (data, time, or money flow)—not a restatement of the title alone.

## Concept deep-dive

The full story. Build the mental model from the ground up. Weave the *why* through every subheading: what problem is this solving, what would the alternative cost, what does the runtime/spec actually do.

### A named sub-idea

Details. Bulleted lists are encouraged for enumerable rules; prose for cause-and-effect.

**Why this matters:** the one sentence that ties this sub-idea back to the chapter's headline.

### Another sub-idea

Details.

## Why these design choices

Explicit trade-off discussion. Name at least one alternative, what it would cost, and when you'd actually pick it instead. This section is where the chapter graduates from "what" to "engineering judgment".

- **Decision 1.** What we picked, what we rejected, the reason.
- **Decision 2.** Same shape.
- **When you'd choose differently.** Concrete scenarios.

## Production-quality code

Runnable, defensive, and idiomatic. No narrating-the-obvious comments (`# increment x`); only comments that explain non-obvious intent or constraint. Show the imports, the error handling, and a way to run it.

### Example 1 — Canonical usage

```python
# Code you can paste and run.
```

Walkthrough: only the lines that aren't self-explanatory.

### Example 2 — A real-world-ish scenario

```python
# Slightly bigger; closer to what shipping code looks like.
```

Walkthrough and discussion of trade-offs.

## Security notes

The realistic threats this chapter touches and how to mitigate them. Examples: input validation, secrets handling, injection, authn/authz boundaries, supply-chain.

If the chapter genuinely doesn't touch security, write:

> **N/A** — *one-sentence reason*. *(See [chapter X](path) for the related security topic.)*

Don't pad. Honest N/A is better than security theater.

## Performance notes

The cost model: time complexity, memory shape, network round-trips, syscalls, I/O patterns. Hot-path do's and don'ts. Where the cliff is.

Same N/A rule applies — write it explicitly with a one-sentence reason if the chapter is, e.g., about resume formatting.

## Common mistakes

At least four entries. Each is **symptom → cause → fix**.

- **Mistake 1.** Symptom; cause; fix.
- **Mistake 2.** …
- **Mistake 3.** …
- **Mistake 4.** …

## Practice

Progress from easy to hard. Include at least one that *must* fail before it succeeds — building debugging muscle is part of the job.

1. **Warm-up.** …
2. **Standard.** …
3. **Bug hunt.** …
4. **Stretch.** …
5. **Stretch++.** …

<details><summary>Show solutions</summary>

### Solution 1

```python
# ...
```

</details>

## Quiz

Five multiple-choice + two short-answer. Answers inline at the end of the chapter (italicized).

1. Question with four options (a) … (b) … (c) … (d) …
2. …
3. …
4. …
5. …

**Short answer:**

6. In your own words, …
7. Explain the trade-off between …

*Answers: 1-?, 2-?, 3-?, 4-?, 5-?.*

## Learn-by-doing mini-project

Keep the full brief in `mini-projects/NN-topic-project.md` (goal, acceptance criteria, hints, stretch). In the chapter body, link to that file so readers can print or share one artifact per chapter.

## Where this idea reappears

Add **≥2 outbound links** to other modules (Python ↔ OOP ↔ FP ↔ DSA ↔ HTTP ↔ SQL ↔ ops). Name the *idea* (state, failure, latency, trust boundary) not just the filename.

Always add **one line** to the curated threads when it fits:

- [Concept threads (hub)](../appendix-threads/README.md) — pick **state**, **errors/retries**, or **performance** trails.

## Chapter summary

- Bullet 1 (the one idea you want the reader to keep).
- Bullet 2.
- Bullet 3.

## Further reading

- Primary source / spec.
- One deeper treatment (book, article).
- One "next step" that extends beyond this chapter.
