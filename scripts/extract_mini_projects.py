#!/usr/bin/env python3
"""Extract ## Learn-by-doing mini-project / ## Mini-project sections into mini-projects/NN-*-project.md."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted(
    p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)
)

HEADER_PAT = re.compile(
    r"^(## Learn-by-doing mini-project|## Mini-project.*)\s*$", re.MULTILINE
)
STOP_PAT = re.compile(r"^## (Chapter summary|Further reading)\s*$", re.MULTILINE)


def extract_block(text: str) -> tuple[str | None, int | None, int | None]:
    m = HEADER_PAT.search(text)
    if not m:
        return None, None, None
    start = m.start()
    rest = text[m.end() :]
    stop = STOP_PAT.search(rest)
    if not stop:
        end = len(text)
    else:
        end = m.end() + stop.start()
    block = text[start:end].rstrip()
    return block, start, end


def main() -> None:
    for mod in MODULES:
        mini = mod / "mini-projects"
        mini.mkdir(exist_ok=True)
        for chap in sorted(mod.glob("[0-9][0-9]-*.md")):
            raw = chap.read_text(encoding="utf-8")
            block, start, end = extract_block(raw)
            if block is None:
                print(f"SKIP (no section): {chap.relative_to(ROOT)}")
                continue
            stem = chap.stem  # e.g. 02-variables
            out = mini / f"{stem}-project.md"
            title_line = block.split("\n", 1)[0]
            body = block.split("\n", 1)[1] if "\n" in block else ""
            out.write_text(
                f"# Mini-project — {stem}\n\n"
                f"_Companion chapter:_ [`{chap.name}`](../{chap.name})\n\n"
                f"{body.strip()}\n",
                encoding="utf-8",
            )
            link = f"mini-projects/{stem}-project.md"
            replacement = (
                f"{title_line}\n\n"
                f"Full brief (goal, acceptance criteria, hints, stretch): "
                f"[{stem} — mini-project]({link}).\n"
            )
            new_raw = raw[:start] + replacement + raw[end:]
            chap.write_text(new_raw, encoding="utf-8")
            print(f"OK {chap.relative_to(ROOT)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
