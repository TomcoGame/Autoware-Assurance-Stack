#!/usr/bin/env python3
"""WP-C-01 Figure 5-1: the item boundary, its elements and the interfaces that cross it.

Elements come from WP-C-01 §5.1 and interfaces from §5.2. Where each element sits and how each
interface is routed is fixed here; the generator refuses to draw if the tables name an element or
an interface it has no place for, if an interface's ends differ from its route, or if an element's
"In the item" cell disagrees with the side of the boundary it is drawn on.

    python3 fig_c01_boundary.py            # write fig-c01-5-1-boundary.svg
    python3 fig_c01_boundary.py --check    # fail if it is stale or disagrees with the tables
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
import figkit as fk  # noqa: E402

DOC = ASSURANCE / "02-concept" / "WP-C-01-item-definition.md"
OUT = HERE / "fig-c01-5-1-boundary.svg"
W = 640
LX, CX, RX = 24, 216, 474  # left edges of the three columns
LW, CW, RW = 128, 208, 142
GL = (LX + LW + CX - 14) / 2  # label x in the left gap
GR = (CX + CW + 14 + RX) / 2  # label x in the right gap

# Element: (x, y, width, height, inside the item)
BOX = {
    "Sensors": (CX, 96, CW, 46, True),
    "Autoware computer": (CX, 196, CW, 196, True),
    "Safety monitor": (CX, 446, CW, 46, True),
    "HD map data": (LX, 200, LW, 40, False),
    "Update backend": (LX, 250, LW, 40, False),
    "Remote operations centre": (LX, 300, LW, 40, False),
    "Passengers": (LX, 350, LW, 40, False),
    "Other road users": (RX, 96, RW, 46, False),
    "Vehicle platform": (RX, 250, RW, 242, False),
    "Power supply": (RX, 530, RW, 40, False),
}

# Interface: (from, to, polyline points, where the label goes, label anchor)
ROUTE = {
    "I-01": ("Other road users", "Sensors", [(RX, 119), (CX + CW, 119)], (GR, 113), "middle"),
    "I-02": (
        "Sensors",
        "Autoware computer",
        [(CX + CW / 2, 142), (CX + CW / 2, 196)],
        (CX + CW / 2 + 8, 173),
        "",
    ),
    "I-03": (
        "Autoware computer",
        "Safety monitor",
        [(CX + CW / 2, 392), (CX + CW / 2, 446)],
        (CX + CW / 2 + 8, 423),
        "",
    ),
    "I-04": (
        "Safety monitor",
        "Vehicle platform",
        [(CX + CW, 458), (RX, 458)],
        (GR, 452),
        "middle",
    ),
    "I-05": (
        "Vehicle platform",
        "Safety monitor",
        [(RX, 480), (CX + CW, 480)],
        (GR, 496),
        "middle",
    ),
    "I-06": (
        "Vehicle platform",
        "Autoware computer",
        [(RX, 300), (CX + CW, 300)],
        (GR, 294),
        "middle",
    ),
    "I-07": ("HD map data", "Autoware computer", [(LX + LW, 220), (CX, 220)], (GL, 214), "middle"),
    "I-10": (
        "Update backend",
        "Autoware computer",
        [(LX + LW, 270), (CX, 270)],
        (GL, 264),
        "middle",
    ),
    "I-08": (
        "Remote operations centre",
        "Autoware computer",
        [(LX + LW, 320), (CX, 320)],
        (GL, 314),
        "middle",
    ),
    "I-09": ("Passengers", "Autoware computer", [(LX + LW, 370), (CX, 370)], (GL, 364), "middle"),
    "I-11": (
        "Vehicle platform",
        "Other road users",
        [(RX + RW / 2, 250), (RX + RW / 2, 142)],
        (RX + RW / 2 + 8, 200),
        "",
    ),
    "I-12": (
        "Power supply",
        "Safety monitor",
        [(RX, 550), (CX + CW / 2, 550), (CX + CW / 2, 492)],
        (CX + CW / 2 + 8, 540),
        "",
    ),
}
TWO_WAY = {"I-08", "I-09"}  # trips and requests in, status back

EXTRA = """svg .in { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.6; }
svg .out { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; }
svg .todo { fill:var(--bg); stroke:var(--acc); stroke-width:1.6; stroke-dasharray:5 3; }
svg .bound { fill:none; stroke:var(--acc); stroke-width:1.4; stroke-dasharray:7 5; }
svg .bl { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); letter-spacing:.06em; }
svg .wire { stroke:var(--ink2); stroke-width:1.4; fill:none; }
svg .head { fill:var(--ink2); }
svg .ts { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .iid { font:500 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""


def tables() -> tuple[dict[str, bool], dict[str, tuple[str, str]]]:
    md = DOC.read_text(encoding="utf-8")
    head, rows = fk.table(fk.section(md, "### 5.1 Elements"), "Element")
    elements = {
        fk.plain(r[fk.col(head, "Element")]): fk.plain(r[fk.col(head, "In the item")]) == "Yes"
        for r in rows
    }
    head, rows = fk.table(fk.section(md, "### 5.2 Interfaces"), "ID")
    ifaces = {
        fk.plain(r[fk.col(head, "ID")]): (
            fk.plain(r[fk.col(head, "From")]),
            fk.plain(r[fk.col(head, "To")]),
        )
        for r in rows
    }
    return elements, ifaces


def head_at(x1: float, y1: float, x2: float, y2: float) -> str:
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 7 * math.cos(a), y2 - 7 * math.sin(a)
    px, py = 4 * math.sin(a), -4 * math.cos(a)
    return fk.el(
        "path",
        None,
        d=f"M{fk.num(x2)} {fk.num(y2)} L{fk.num(hx + px)} {fk.num(hy + py)} L{fk.num(hx - px)} {fk.num(hy - py)} Z",
        class_="head",
    )


def build_svg(elements: dict[str, bool], ifaces: dict[str, tuple[str, str]], todo: set[str]) -> str:
    body = [
        fk.text(24, 32, "Item boundary and interfaces", "h"),
        fk.text(24, 54, "WP-C-01 §5: what is inside the item, and what crosses its edge", "t"),
        fk.el("rect", None, x=CX - 14, y=72, width=CW + 28, height=436, rx=12, class_="bound"),
        fk.text(CX - 6, 88, "ITEM", "bl"),
    ]
    for iid in sorted(ifaces):
        _, _, pts, (lx, ly), anchor = ROUTE[iid]
        d = "M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in pts)
        body.append(fk.el("path", None, d=d, class_="wire"))
        body.append(head_at(*pts[-2], *pts[-1]))
        if iid in TWO_WAY:
            body.append(head_at(*pts[1], *pts[0]))
        body.append(fk.text(lx, ly, iid, "iid", anchor))
    for name, (x, y, w, h, inside) in BOX.items():
        cls = "todo" if name in todo else "in" if inside else "out"
        body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=7, class_=cls))
        cls_t = "tb" if inside else "ts"  # outside boxes are narrower: a 12px label
        lines = fk.wrap(name, w - (16 if inside else 6), cls_t)
        top = y + h / 2 - (len(lines) - 1) * 7.5 + 4
        for j, ln in enumerate(lines):
            body.append(fk.text(x + w / 2, top + 15 * j, ln, cls_t, "middle"))
    y = 600
    legend = [
        ("in", "Inside the item"),
        ("todo", "Inside, not yet built"),
        ("out", "Outside the item"),
    ]
    x = 24
    for cls, label in legend:
        body += [
            fk.el("rect", None, x=x, y=y - 12, width=22, height=16, rx=4, class_=cls),
            fk.text(x + 30, y, label, "t"),
        ]
        x += 30 + fk.width(label, "t") + 22
    h = y + 22
    desc = (
        "Inside the item: "
        + ", ".join(n for n, i in elements.items() if i)
        + ". Outside: "
        + ", ".join(n for n, i in elements.items() if not i)
        + ". Interfaces: "
        + "; ".join(f"{iid} from {a} to {b}" for iid, (a, b) in sorted(ifaces.items()))
        + "."
    )
    return fk.svg(W, h, "WP-C-01 Figure 5-1: item boundary and interfaces", desc, body, EXTRA)


def build() -> dict[Path, str]:
    elements, ifaces = tables()
    if set(elements) != set(BOX):
        raise fk.FigureError(
            f"WP-C-01 §5.1 elements {sorted(elements)} differ from those placed {sorted(BOX)}"
        )
    for name, inside in elements.items():
        if inside != BOX[name][4]:
            raise fk.FigureError(f"WP-C-01 §5.1: {name} is drawn on the other side of the boundary")
    if set(ifaces) != set(ROUTE):
        raise fk.FigureError(
            f"WP-C-01 §5.2 interfaces {sorted(ifaces)} differ from those routed {sorted(ROUTE)}"
        )
    for iid, ends in ifaces.items():
        if ends != ROUTE[iid][:2]:
            raise fk.FigureError(
                f"WP-C-01 {iid}: table says {ends}, the route joins {ROUTE[iid][:2]}"
            )
    md = DOC.read_text(encoding="utf-8")
    head, rows = fk.table(fk.section(md, "## 3. The item and its functions"), "ID")
    todo = (
        {"Safety monitor"}
        if any(
            "Does not exist" in r[fk.col(head, "State")]
            and "Safety monitor" in r[fk.col(head, "Realised by (pinned packages)")]
            for r in rows
        )
        else set()
    )
    return {OUT: build_svg(elements, ifaces, todo)}


if __name__ == "__main__":
    fk.run(build, __doc__)
