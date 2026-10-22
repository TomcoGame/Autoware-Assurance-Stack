#!/usr/bin/env python3
"""Check that every relative link in the assurance tree resolves, including #anchors into Markdown.

Scans assurance/**/*.md and the repository's CLAUDE.md. External links (http, mailto) are not
fetched. An anchor must match a heading of the target file, slugged the way GitHub does.

    python3 check_links.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ASSURANCE = Path(__file__).resolve().parents[2]
REPO = ASSURANCE.parent
LINK = re.compile(r"(?<!\\)!?\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def slug(heading: str) -> str:
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip()).lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    out: set[str] = set()
    seen: dict[str, int] = {}
    text = CODE.sub("", md.read_text(encoding="utf-8"))
    for m in re.finditer(r"^#{1,6} (.+?)\s*$", text, re.M):
        base = slug(m.group(1))
        n = seen.get(base, 0)
        out.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    return out


def files() -> list[Path]:
    out = sorted(ASSURANCE.rglob("*.md"))
    if (REPO / "CLAUDE.md").is_file():
        out.append(REPO / "CLAUDE.md")
    return out


def check(paths: list[Path]) -> list[str]:
    errs = []
    cache: dict[Path, set[str]] = {}
    for md in paths:
        text = CODE.sub("", md.read_text(encoding="utf-8"))
        for m in LINK.finditer(text):
            url = m.group(1)
            if re.match(r"[a-z][a-z0-9+.-]*:", url) or url.startswith("//"):
                continue
            path, _, frag = url.partition("#")
            target = (md.parent / path).resolve() if path else md.resolve()
            where = f"{md.relative_to(REPO)}: {url}"
            if not target.exists():
                errs.append(f"{where}: no such file")
                continue
            if frag and target.suffix == ".md":
                if target not in cache:
                    cache[target] = anchors(target)
                if frag not in cache[target]:
                    errs.append(f"{where}: no heading #{frag}")
    return errs


def main() -> int:
    paths = files()
    errs = check(paths)
    for e in errs:
        print(e)
    if errs:
        return 1
    print(f"links OK in {len(paths)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
