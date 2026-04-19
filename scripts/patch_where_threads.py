#!/usr/bin/env python3
"""Append concept-threads hub bullet under ## Where this idea reappears if missing."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name))

INSERT = "  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.\n"
HUB = "Concept threads (hub)"

PAT = re.compile(
    r"(  - [^\n]+\n"
    r"  - [^\n]+\n)"
    r"(\n+)$",
    re.MULTILINE,
)


def patch(text: str) -> str:
    w0 = text.find("## Where this idea reappears")
    if w0 == -1:
        return text
    w1 = text.find("\n## Chapter summary", w0)
    if w1 == -1:
        return text
    chunk = text[w0:w1]
    if HUB in chunk:
        return text
    if "**Cross-module links (read next when you feel stuck):**" not in chunk:
        return text
    m = PAT.search(chunk)
    if not m:
        return text
    replacement = m.group(1) + "\n" + INSERT + m.group(2)
    new_chunk = chunk[: m.start()] + replacement + chunk[m.end() :]
    return text[:w0] + new_chunk + text[w1:]


def main() -> None:
    for mod in MODULES:
        for chap in sorted(mod.glob("[0-9][0-9]-*.md")):
            raw = chap.read_text(encoding="utf-8")
            new = patch(raw)
            if new != raw:
                chap.write_text(new, encoding="utf-8")
                print(f"Patched {chap.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
