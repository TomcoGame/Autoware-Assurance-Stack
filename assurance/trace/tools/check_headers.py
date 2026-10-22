#!/usr/bin/env python3
"""Check the document control header of every work product against the WP-M-00 register.

Every file a WP-M-00 row links to must start with the header table of assurance/README.md
(Conventions → Document control header): all nine fields, in order, non-empty; `Work product`
starting with the register ID; `Status` agreeing with the register's status letter. Every
`WP-*.md` file in the tree must be in the register.

    python3 check_headers.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

ASSURANCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
import figkit as fk  # noqa: E402
import wpregister  # noqa: E402

FIELDS = [
    "Work product",
    "Standard reference",
    "Version",
    "Status",
    "ASIL / scope",
    "Author",
    "Reviewer(s)",
    "Approver",
    "Baseline",
]
STATUS_WORD = {
    "S": "Skeleton",
    "D": "Draft",
    "R": "In review",
    "A": "Approved",
    "B": "Baselined",
    "N/A": "N/A",
}


def header(text: str) -> dict[str, str] | None:
    """The Field/Value table that follows the title, or None."""
    try:
        head, rows = fk.table(text.split("\n## ", 1)[0], "Field")
    except fk.FigureError:
        return None
    if head != ["Field", "Value"]:
        return None
    return {r[0]: r[1] for r in rows if len(r) == 2}


def check_product(p: wpregister.Product, text: str) -> list[str]:
    errs = []
    h = header(text)
    if h is None:
        return [f"{p.wid}: no document control header (| Field | Value |) before the first section"]
    if list(h) != FIELDS:
        errs.append(f"{p.wid}: header fields are {list(h)}, expected {FIELDS}")
    for f in FIELDS:
        if not h.get(f, "").strip():
            errs.append(f"{p.wid}: header field {f!r} is empty")
    if not h.get("Work product", "").startswith(p.wid + " "):
        errs.append(f"{p.wid}: 'Work product' must start with {p.wid}")
    status = h.get("Status", "")
    if status != STATUS_WORD[p.status]:
        errs.append(f"{p.wid}: header Status {status!r}, register says {STATUS_WORD[p.status]!r}")
    if not re.match(r"\d+\.\d+ ", h.get("Version", "") + " "):
        errs.append(f"{p.wid}: Version starts with a number like 0.1")
    return errs


def main() -> int:
    reg = wpregister.load()
    errs = []
    linked = set()
    for p in reg.products:
        if not p.path.is_file():
            errs.append(f"{p.wid}: register links {p.href}, which does not exist")
            continue
        linked.add(p.path)
        if p.path.name.startswith("WP-") and not p.path.name.startswith(p.wid + "-"):
            errs.append(f"{p.wid}: file name {p.path.name} does not start with its ID")
        if p.path.name.startswith("WP-"):
            errs += check_product(p, p.path.read_text(encoding="utf-8"))
    for f in sorted(ASSURANCE.rglob("WP-*.md")):
        if f.resolve() not in linked:
            errs.append(f"{f.relative_to(ASSURANCE)}: not in the WP-M-00 register")
    for e in errs:
        print(e)
    if errs:
        return 1
    print(f"headers OK for {len(reg.products)} work products")
    return 0


if __name__ == "__main__":
    sys.exit(main())
