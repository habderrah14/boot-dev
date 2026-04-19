# Companion Book Progress Tracker

This file tracks implementation progress for companion artifacts promised in `README.md`.

## Definition of done (per module)

A module is considered **content-complete** when all of the following are true:

1. Core lesson chapters exist and are linked from `SUMMARY.md`.
2. Every chapter has an exercise file in `exercises/` that **meets the quality bar** (5 tasks with prompts, setup, success checks).
3. Every chapter has a matching solution file in `solutions/` with **worked reasoning**, not one-line summaries.
4. Module `README.md` contains a real quiz answer key section (no placeholder answer keys).
5. Every chapter’s inline mini-project is **extracted** to `mini-projects/NN-*-project.md` and linked from the module README.
6. Diagram-natural chapters include at least one **Mermaid or ASCII** figure where it helps; dashboard tracks `Diagrams met-bar`.
7. **Newbie lane** subsection (`## In plain terms (newbie lane)`) present in rollout chapters; dashboard tracks `Newbie prose`.
8. **Lesson visuals** caption rule followed (see [`templates/chapter-template.md`](templates/chapter-template.md)); dashboard tracks `Lesson visuals`.

## Master plan verification (2026-04)

Automated / manual audit against [`backend_companion_master.plan.md`](/home/dzgeek/.cursor/plans/backend_companion_master.plan.md):

- Mini-project files exist per chapter (counts align with chapter counts + legacy workbench where applicable).
- `SUMMARY.md` lists onboarding, study habits, shipping checklist, junior spine, concept threads, system design, integration projects.
- `## Where this idea reappears` includes link to [`appendix-threads/README.md`](appendix-threads/README.md) in course chapters.
- Exercises in modules **01–03** and **08–12** use **humanized** prompts ([`scripts/humanize_exercises_slice.py`](scripts/humanize_exercises_slice.py)); other modules still use the generator fallback until sliced.

## Artifact naming & quality

### File naming

- Exercises: `exercises/NN-topic-exercises.md`
- Solutions: `solutions/NN-topic-solutions.md`
- Mini-project briefs: `mini-projects/NN-topic-project.md` (one per chapter, extracted from the chapter)

`NN` matches chapter order.

### Quality bar

- Exercises include at least 5 tasks: warm-up, standard, bug-hunt, stretch, stretch++ — each with prompt, inputs/setup, success check, and a takeaway line.
- Solutions explain reasoning, wrong answers, and edge cases — not only final commands/code.
- Mini-project briefs include: goal, acceptance criteria, hints, stretch extensions.
- Links must resolve from module README and (when listed) from `SUMMARY.md`.

## Module dashboard

Legend: ✅ meets bar · 🟨 partial / in progress · ⬜ not started

| Module          | Lessons | Exercises bar | Solutions bar | Quiz key | Mini-projects extracted | Diagrams bar | Newbie prose | Lesson visuals | Debug labs | Code review tasks | System design prompts | Interview challenges | Capstone milestone |
| --------------- | ------- | ------------- | ------------- | -------- | ----------------------- | ------------ | ------------ | -------------- | ---------- | ----------------- | --------------------- | -------------------- | ------------------ |
| 01-python       | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 02-linux        | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 03-git          | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 04-oop          | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 05-fp           | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 06-dsa          | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 07-c-memory     | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 08-js           | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 09-ts           | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 10-http-clients | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 11-sql          | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 12-http-servers | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 13-file-cdn     | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 14-docker       | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 15-pubsub       | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |
| 16-job-hunt     | ✅      | ✅            | ✅            | ✅       | ✅                      | ✅           | ✅           | ✅             | ✅         | ✅                | ✅                    | ✅                   | ✅                 |

**Diagrams bar:** every chapter in modules 12–15 has ≥1 Mermaid (or intentional ASCII-only) diagram; targeted chapters in 06–08, 10, 07 as listed in the improvement plan.

**Newbie prose:** `## In plain terms (newbie lane)` is now present across all chapter files in modules 01–16.

**Lesson visuals:** caption rule pass is complete for all currently detected figures (Mermaid/ASCII/image) across modules 01–16.

**New rollout columns:**

- **Debug labs** = incident-style troubleshooting exercises with broken code/symptoms.
- **Code review tasks** = PR-style review prompts with actionable comments.
- **System design prompts** = chapter/module prompts that force scaling and trade-off thinking.
- **Interview challenges** = staged easy→hard interview-style tasks embedded before Module 16.
- **Capstone milestone** = module-level milestone project (tier checkpoints after 05/10/15).

## Placeholder / marker audit

A repo-wide search for authoring markers (`TODO`, `FIXME`, `TBD`, `WIP`, `coming soon`) was reviewed. Remaining hits are **intentional prose** (e.g. example Git commit subjects like `WIP:`, ripgrep tutorials that search for `TODO`, SQL _parameter_ placeholders, career advice warning against `TODO` in READMEs). No unfinished “replace this later” blocks were found that require removal.

## Current sprint focus

1. Keep the dashboard honest when adding chapters — update artifact columns (including Newbie prose / Lesson visuals).
2. Run the per-chapter checklist (see root `README.md` conventions) before merging substantive edits.
3. Appendices: [`appendix-projects/`](appendix-projects/) and [`appendix-system-design.md`](appendix-system-design.md) are part of the extended curriculum; link them from [`SUMMARY.md`](SUMMARY.md).
