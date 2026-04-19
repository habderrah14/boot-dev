#!/usr/bin/env python3
"""Insert ## In plain terms (newbie lane) after ## The simple version for priority modules."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOW = {
    "01-python",
    "02-linux",
    "03-git",
    "08-js",
    "09-ts",
    "10-http-clients",
    "11-sql",
    "12-http-servers",
}

NEWBIE = """## In plain terms (newbie lane)

This chapter is really about **{title}**. Skim *Learning objectives* above first—they are your exit ticket.

> **Newbies often think:** they must memorize the whole chapter before writing any code.  
> **Actually:** you only need the *next* honest mental model, then you prove it with the exercises and mini-project.

Companion links: [Onboarding](../appendix-onboarding.md) · [Study habits](../appendix-study-habits.md) · [Concept threads](../appendix-threads/README.md)

<details><summary>Pause and predict</summary>

Without scrolling: what is one real bug or outage class this chapter helps you prevent?

</details>

"""


def chapter_title(path: Path) -> str:
    line = path.read_text(encoding="utf-8").split("\n", 1)[0]
    m = re.match(r"^#\s+Chapter\s+\d+\s+—\s+(.+)$", line)
    if m:
        return m.group(1).strip()
    m2 = re.match(r"^#\s+(.+)$", line)
    return m2.group(1).strip() if m2 else path.stem


def insert_block(text: str, title: str) -> str:
    if "## In plain terms (newbie lane)" in text:
        return text
    block = NEWBIE.format(title=title) + "\n"

    m = re.search(r"^## The simple version\s*\n", text, re.MULTILINE)
    if m:
        start = m.end()
        rest = text[start:]
        m2 = re.search(r"^## [^#]", rest, re.MULTILINE)
        end = start + m2.start() if m2 else len(text)
        return text[:end] + block + text[end:]

    # Chapters without "The simple version" (e.g. some late HTTP chapters): insert before Concept deep-dive
    idx = text.find("\n## Concept deep-dive\n")
    if idx != -1:
        return text[: idx + 1] + block + text[idx + 1 :]
    return text


def main() -> None:
    for name in sorted(ALLOW):
        mod = ROOT / name
        if not mod.is_dir():
            continue
        for chap in sorted(mod.glob("[0-9][0-9]-*.md")):
            raw = chap.read_text(encoding="utf-8")
            new = insert_block(raw, chapter_title(chap))
            if new != raw:
                chap.write_text(new, encoding="utf-8")
                print(f"Inserted newbie lane -> {chap.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
