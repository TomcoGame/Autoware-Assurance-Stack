#!/usr/bin/env python3
"""Check that every Markdown table row in the assurance tree has as many cells as its header.

A row with too few or too many cells renders shifted on GitHub and breaks the generators that read
tables. Pipes inside backticks or escaped as \\| do not split cells.

    python3 check_tables.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ASSURANCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
from figkit import split_row  # noqa: E402

SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def check_text(text: str, name: str) -> list[str]:
    errs = []
    lines = text.splitlines()
    fence = False
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("```"):
            fence = not fence
        if (
            not fence
            and ln.lstrip().startswith("|")
            and i + 1 < len(lines)
            and SEP.match(lines[i + 1])
        ):
            n = len(split_row(ln))
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                k = len(split_row(lines[j]))
                if k != n:
                    errs.append(f"{name}:{j + 1}: {k} cells, header has {n}")
                j += 1
            i = j
            continue
        i += 1
    return errs


def main() -> int:
    errs = []
    paths = sorted(ASSURANCE.rglob("*.md"))
    for p in paths:
        errs += check_text(p.read_text(encoding="utf-8"), str(p.relative_to(ASSURANCE.parent)))
    for e in errs:
        print(e)
    if errs:
        return 1
    print(f"tables OK in {len(paths)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
