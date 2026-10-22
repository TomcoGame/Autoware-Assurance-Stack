#!/usr/bin/env python3
"""Read the WP-M-00 work product register: the gates of §2 and every row of the §3 tables.

Used by the generators that draw or list work products (fig_m00_register.py, folder_index.py,
case/tools/dashboard.py). Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figkit import ASSURANCE  # noqa: E402
from figkit import FigureError  # noqa: E402
from figkit import STATUS_NAME  # noqa: E402
from figkit import col  # noqa: E402
from figkit import plain  # noqa: E402
from figkit import section  # noqa: E402
from figkit import table  # noqa: E402

WP_M_00 = ASSURANCE / "01-management" / "WP-M-00-work-product-register.md"


@dataclass
class Product:
    wid: str
    name: str
    href: str  # relative to 01-management/
    section: str  # "3.2"
    folder: str  # "02-concept"
    gate_text: str
    gates: list[int]
    status: str

    @property
    def path(self) -> Path:
        return (WP_M_00.parent / self.href).resolve()


@dataclass
class Register:
    gates: list[tuple[str, str]]  # (G0, Governance)
    sections: list[tuple[str, str, str]]  # (3.1, Management, 01-management)
    products: list[Product] = field(default_factory=list)


def parse_gates(text: str, known: int) -> list[int]:
    """Gate numbers named in a Gate cell. 'G1→G5' is a range; 'G2 (x), G6 (y)' names two."""
    out: set[int] = set()
    for a, b in re.findall(r"G(\d)\s*→\s*G(\d)", text):
        out.update(range(int(a), int(b) + 1))
    out.update(int(g) for g in re.findall(r"G(\d)", text))
    bad = [g for g in out if g >= known]
    if not out or bad:
        raise FigureError(f"gate cell {text!r} names no known gate")
    return sorted(out)


def load(md: str | None = None) -> Register:
    md = md if md is not None else WP_M_00.read_text(encoding="utf-8")
    head, rows = table(section(md, "## 2. Gates"), "Gate")
    gates = [(plain(r[col(head, "Gate")]), plain(r[col(head, "Name")])) for r in rows]
    if [g for g, _ in gates] != [f"G{i}" for i in range(len(gates))]:
        raise FigureError("WP-M-00 §2 gates must be G0, G1, … in order")
    s3 = section(md, "## 3. Register")
    reg = Register(gates=gates, sections=[])
    seen: set[str] = set()
    for num, title, folder in re.findall(r"^### (3\.\d+) (.+?) \(`([^`]*)/`\)\s*$", s3, re.M):
        reg.sections.append((num, title, folder))
        head, rows = table(section(s3, f"### {num} "), "ID")
        for r in rows:
            if len(r) != len(head):
                raise FigureError(
                    f"WP-M-00 §{num}: row {r[0]!r} has {len(r)} cells, header {len(head)}"
                )
            cell = r[col(head, "ID")]
            m = re.fullmatch(r"\[(WP-[A-Z]-\d\d)\]\(([^)]+)\)", cell)
            if not m:
                raise FigureError(
                    f"WP-M-00 §{num}: ID cell {cell!r} is not a link to the work product"
                )
            wid, href = m.groups()
            if wid in seen:
                raise FigureError(f"WP-M-00: {wid} appears twice")
            seen.add(wid)
            status = plain(r[col(head, "Status")])
            if status not in STATUS_NAME:
                raise FigureError(
                    f"WP-M-00 {wid}: status {status!r} is not one of {', '.join(STATUS_NAME)}"
                )
            gate_text = plain(r[col(head, "Gate")])
            reg.products.append(
                Product(
                    wid=wid,
                    name=plain(r[col(head, "Work product")]),
                    href=href,
                    section=num,
                    folder=folder,
                    gate_text=gate_text,
                    gates=parse_gates(gate_text, len(gates)),
                    status=status,
                )
            )
    if not reg.products:
        raise FigureError("WP-M-00 §3 has no register rows")
    return reg
