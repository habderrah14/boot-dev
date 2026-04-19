#!/usr/bin/env python3
"""
Generate full exercise + solution files for all companion chapters.
Uses module-specific templates keyed by chapter title (from H1).

For **humanized**, chapter-tied prompts in modules 01–03 and 08–12, prefer
`scripts/humanize_exercises_slice.py` and re-run this script only for other
modules or as a fallback when regenerating the whole tree.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name))

DOMAIN = {
    "01-python": "Python 3.12",
    "02-linux": "Linux shell and userspace",
    "03-git": "Git version control",
    "04-oop": "Python object-oriented design",
    "05-fp": "Python functional programming",
    "06-dsa": "Python data structures and algorithms",
    "07-c-memory": "C17 and memory management",
    "08-js": "JavaScript (ES2022+)",
    "09-ts": "TypeScript 5.x",
    "10-http-clients": "TypeScript HTTP clients (fetch, Node 20)",
    "11-sql": "PostgreSQL 16 and SQL",
    "12-http-servers": "TypeScript HTTP servers (e.g. Express-style patterns)",
    "13-file-cdn": "object storage, CDNs, and media delivery",
    "14-docker": "Docker and OCI containers",
    "15-pubsub": "RabbitMQ-style pub/sub in TypeScript",
    "16-job-hunt": "job search, resume, and interviewing",
}


def chapter_meta(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^#\s+Chapter\s+(\d+)\s+—\s+(.+)$", text.split("\n", 1)[0])
    if m:
        return m.group(1), m.group(2).strip()
    m2 = re.match(r"^#\s+(.+)$", text.split("\n", 1)[0])
    return ("?", m2.group(1).strip() if m2 else path.stem)


def exercises_md(mod: str, num: str, title: str, slug: str) -> str:
    dom = DOMAIN.get(mod, "software engineering")
    return f"""# Module {mod[:2]} · Chapter {num} Exercises — {title}

Domain: **{dom}**. Every task should produce something you can paste into notes or a repo.

## 1) Warm-up — vocabulary and mental model

In **≤8 bullets**, define the core terms from this chapter and state *why each matters on a backend team*. Tie at least two bullets to production risks (downtime, data loss, security, cost).

**Setup:** Re-read the chapter section *The simple version* and *Learning objectives*.

**Success check:** A teammate could skim your bullets and explain the idea in one sentence.

**What you should have learned:** Precision beats buzzwords — names for things you already half-knew.

## 2) Standard — apply the happy path

Pick **one concrete scenario** from the chapter (or the chapter mini-project brief) and implement / diagram / script the *happy path* end-to-end at a small scale (single file or single SQL file / single container / single route).

**Setup:** Create a folder `practice/{slug}/` with your artifact and a 5-line `README.md` saying how to run it.

**Success check:** A fresh clone + your README runs without guessing missing steps.

**What you should have learned:** The chapter’s default workflow is muscle memory.

## 3) Bug hunt — break it on purpose

Introduce **three separate bugs** related to this chapter’s topic (wrong flag, wrong assumption about state, missing validation, bad query plan, leaky resource, etc.). Document *symptom → root cause → fix* for each.

**Setup:** Keep diffs or comments showing before/after.

**Success check:** Each bug is reproducible with numbered steps.

**What you should have learned:** Debugging is pattern matching on failure signatures.

## 4) Stretch — trade-offs and failure modes

Write a **≤300-word memo** answering: “When would I *not* choose the default approach from this chapter?” Name two alternatives, their costs, and one scenario each where they win.

**Success check:** Memo mentions latency, operability, or security explicitly.

**What you should have learned:** Mature engineers defend choices with constraints, not slogans.

## 5) Stretch++ — teach someone else

Record **a 3-minute spoken outline** (bullet script is fine) or write **10 flashcards** that would prepare a peer for a whiteboard/live-coding question on `{title}`.

**Success check:** Includes at least one “common wrong answer” card or slide.

**What you should have learned:** Teaching forces gaps in understanding to the surface.
"""


def solutions_md(mod: str, num: str, title: str, slug: str) -> str:
    dom = DOMAIN.get(mod, "software engineering")
    return f"""# Module {mod[:2]} · Chapter {num} Solutions — {title}

These are **reference solutions / reasoning guides**. Your artifacts may differ; grade yourself with the success checks.

## 1) Warm-up — vocabulary and mental model

**Approach:** Start from definitions in the chapter deep-dive, then map each term to a failure mode.

**Example reasoning:** If you cannot explain *statelessness* (HTTP), *mutation* (Python), *pointer aliasing* (C), *pure function* (FP), or *normal form* (SQL) in one clause each, revisit the chapter diagrams.

**Common wrong answers:** Confusing similar terms (authn vs authz, stack vs heap, interface vs type, cluster index vs nonclustered, image vs container).

**Takeaway:** Bullet fidelity beats paragraph length.

## 2) Standard — apply the happy path

**Worked path:** (1) smallest runnable slice → (2) one automated check (`pytest`, `node --test`, `curl`, `psql -f`, `docker compose config`) → (3) freeze versions in a comment or lockfile.

**Edge cases:** Paths with spaces, ports already in use, missing env vars, TLS name mismatch, SQL `NULL` tri-state logic.

**If blocked:** Reduce scope until *one* observable output proves the happy path (status 200, row count, container `healthy`, etc.).

**Takeaway:** Shipping a thin vertical slice beats a wide stub.

## 3) Bug hunt — break it on purpose

**How to grade yourself:** Each bug should take a reviewer **>2 minutes** to spot without your hint — otherwise deepen the bug.

**Typical patterns for {dom}:**
- Off-by-one / wrong comparison operator.
- Async serial vs parallel confusion.
- SQL string concatenation instead of parameters.
- Trusting client input for authz.
- Forgetting `Content-Type` / charset.
- C resource without paired `free` / `close` / `ROLLBACK`.

**Takeaway:** Bugs you manufacture intentionally become future incident intuition.

## 4) Stretch — trade-offs and failure modes

**Skeleton answer:** Default wins when team skill, ecosystem defaults, and operational tooling align. Alternatives win when **latency SLO**, **compliance**, **team size**, or **hosting constraints** dominate.

**Concrete angles for `{title}`:** cost of round-trips, blast radius of misconfiguration, observability coverage, migration pain, vendor lock-in.

**Takeaway:** Write decisions as “given X constraint, pick Y.”

## 5) Stretch++ — teach someone else

**Peer-review trick:** Swap artifacts with another learner; each asks one hostile “what if?” question.

**Common wrong answers to flag in flashcards:** Myths (“always normalize to 5NF”, “always microservices”, “Docker == VMs”, “JWT == authz”).

**Takeaway:** Flashcards that include *wrong* patterns inoculate you against interview traps.
"""


def main() -> None:
    for mod_path in MODULES:
        mod = mod_path.name
        for chap in sorted(mod_path.glob("[0-9][0-9]-*.md")):
            slug = chap.stem
            num, title = chapter_meta(chap)
            ex = mod_path / "exercises" / f"{slug}-exercises.md"
            so = mod_path / "solutions" / f"{slug}-solutions.md"
            ex.parent.mkdir(exist_ok=True)
            so.parent.mkdir(exist_ok=True)
            ex.write_text(exercises_md(mod, num, title, slug), encoding="utf-8")
            so.write_text(solutions_md(mod, num, title, slug), encoding="utf-8")
        print(f"Wrote exercises+solutions for {mod}")


if __name__ == "__main__":
    main()
