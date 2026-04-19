#!/usr/bin/env python3
"""Rewrite exercises + solutions for priority modules with chapter-tied prompts."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "01-python",
    "02-linux",
    "03-git",
    "08-js",
    "09-ts",
    "10-http-clients",
    "11-sql",
    "12-http-servers",
]


def chapter_title(chap: Path) -> str:
    line = chap.read_text(encoding="utf-8").split("\n", 1)[0]
    m = re.match(r"^#\s+Chapter\s+\d+\s+—\s+(.+)$", line)
    if m:
        return m.group(1).strip()
    m2 = re.match(r"^#\s+(.+)$", line)
    return m2.group(1).strip() if m2 else chap.stem


def exercises_md(mod: str, title: str, slug: str) -> str:
    mod_label = mod[:2]
    return f"""# Module {mod_label} · Exercises — {title}

Tasks reference **this chapter only** (plus its mini-project brief). Use the chapter file `{slug}.md` while you work.

## 1) Warm-up — vocabulary

List **six terms** introduced in *{title}*. For each: one-line definition **in your own words** + one sentence on why a backend team cares.

**Success check:** No term is copied verbatim from the chapter heading without explanation.

**What you should have learned:** You can explain the headline without running code.

## 2) Standard — smallest working artifact

Implement **one** concrete artifact described in the chapter’s *Production-quality code* section, **or** the first acceptance bullet of [`mini-projects/{slug}-project.md`](../mini-projects/{slug}-project.md). Put it under `practice/{slug}/` with a 5-line `README.md` (`cd` path + run command + expected output).

**Success check:** A peer can run your README on a clean machine and see the same output.

**What you should have learned:** The happy path is reproducible, not lucky.

## 3) Bug hunt — three chapter-themed bugs

Introduce **three bugs** that a reader of *{title}* could realistically make (misread API, wrong flag, wrong assumption about defaults). Document **symptom → root cause → fix** for each with a minimal diff.

**Success check:** Each bug references a sentence or API from this chapter.

**What you should have learned:** You recognize failure signatures tied to this topic.

## 4) Stretch — trade-off memo (≤250 words)

Answer: *When would I avoid the default approach from “{title}”, and what would I use instead?* Name two alternatives and one failure mode each prevents.

**Success check:** Memo mentions at least one of: latency, security, operability, cost.

**What you should have learned:** Choices are constrained, not tribal.

## 5) Stretch++ — teach-back

Record **5 flashcards** (front/back) or a **3-minute outline** explaining *{title}* to a friend who only knows Modules 01–02. Include **one common wrong answer** on a card.

**Success check:** A listener could answer a basic interview question on this topic afterward.

**What you should have learned:** Teaching exposes holes in understanding.
"""


def solutions_md(mod: str, title: str, slug: str) -> str:
    mod_label = mod[:2]
    return f"""# Module {mod_label} · Solutions — {title}

Use this after an honest attempt. Your code may differ; grade with the **success checks**.

## 1) Warm-up — vocabulary

**Approach:** Pull terms from *Concept deep-dive* and *Common mistakes*; prefer precise verbs.

**Common wrong answers:** Confusing similar names; defining a term using the same word; skipping “why backend cares.”

**Takeaway:** If you cannot explain a term in one breath, revisit that subsection.

## 2) Standard — smallest working artifact

**Approach:** Copy the chapter’s canonical snippet, then delete until it still runs. Add `README.md` with exact commands.

**Edge cases:** Wrong working directory, missing dependency version, Windows vs POSIX paths.

**Takeaway:** Repro beats cleverness.

## 3) Bug hunt — three chapter-themed bugs

**Examples (adapt to your chapter):** off-by-one config, missing `await`, wrong SQL join, wrong HTTP header casing, Docker `localhost` confusion.

**Takeaway:** Tie each bug to a **sentence** in the chapter so you remember where the trap was.

## 4) Stretch — trade-off memo

**Skeleton:** Default wins when constraints match the chapter’s assumptions. Pick alternatives when scale, compliance, or team topology differs.

**Takeaway:** Write “Given X constraint, pick Y.”

## 5) Stretch++ — teach-back

**Peer check:** Swap flashcards; ask one hostile follow-up each.

**Takeaway:** Wrong answers on cards are as valuable as right ones.
"""


def main() -> None:
    for mod in MODULES:
        base = ROOT / mod
        exdir = base / "exercises"
        soldir = base / "solutions"
        if not exdir.is_dir():
            continue
        for ex in sorted(exdir.glob("[0-9][0-9]-*-exercises.md")):
            slug = ex.name.replace("-exercises.md", "")
            chap = base / f"{slug}.md"
            if not chap.exists():
                print(f"MISS chapter {chap}")
                continue
            title = chapter_title(chap)
            ex.write_text(exercises_md(mod, title, slug), encoding="utf-8")
            so = soldir / f"{slug}-solutions.md"
            so.write_text(solutions_md(mod, title, slug), encoding="utf-8")
        print(f"Humanized exercises+solutions -> {mod}")


if __name__ == "__main__":
    main()
