#!/usr/bin/env python3
"""Replace the Mini-project briefs subsection in each module README with links to all mini-projects/."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name))

SECTION_START = re.compile(r"^- Mini-project briefs:\s*\n", re.MULTILINE)


def human_title(stem: str) -> str:
    """01-introduction-project -> 01 — Introduction."""
    base = stem.removesuffix("-project")
    parts = base.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        rest = parts[1].replace("-", " ").title()
        return f"{parts[0]} — {rest}"
    return stem.replace("-", " ").title()


def build_list(mod: Path) -> str:
    files = sorted((mod / "mini-projects").glob("*.md"))
    lines = ["- Mini-project briefs:\n"]
    for f in files:
        label = human_title(f.stem)
        lines.append(f"  - [{label}](mini-projects/{f.name})\n")
    return "".join(lines)


def patch_readme(path: Path, new_section: str) -> None:
    text = path.read_text(encoding="utf-8")
    m = SECTION_START.search(text)
    if not m:
        print(f"WARN: no Mini-project briefs in {path}")
        return
    start = m.start()
    # find end: next line that starts with ## (at beginning)
    rest = text[m.end() :]
    end_rel = re.search(r"^## ", rest, re.MULTILINE)
    if not end_rel:
        end = len(text)
    else:
        end = m.end() + end_rel.start()
    new_text = text[:start] + new_section + text[end:]
    path.write_text(new_text, encoding="utf-8")
    print(f"Patched {path.relative_to(ROOT)}")


def main() -> None:
    for mod in MODULES:
        readme = mod / "README.md"
        if not readme.exists():
            continue
        patch_readme(readme, build_list(mod))


if __name__ == "__main__":
    main()
