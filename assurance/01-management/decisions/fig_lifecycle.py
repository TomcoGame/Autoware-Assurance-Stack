#!/usr/bin/env python3
"""Decision register Figure 1: the lifecycle of a question, drawn from the status table of README.md.

Each state is a box with its name and the first clause of its Meaning cell; the transitions are
fixed here and checked against the states of the table and of check_decisions.STATUSES, so adding a
state anywhere without drawing it fails.

    python3 fig_lifecycle.py            # write figures/fig-dr-1-lifecycle.svg
    python3 fig_lifecycle.py --check    # fail if it is stale or the states disagree
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figures"))
sys.path.insert(0, str(HERE))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402

OUT = HERE / "figures" / "fig-dr-1-lifecycle.svg"
README = HERE / "README.md"
W = 640
BW, BH = 196, 58
DY = 98  # row pitch
# Top-left corner of each box (x, row), and the transitions drawn between them, with their labels.
POS = {
    "queued": (190, 0),
    "open": (190, 1),
    "answered": (60, 2),
    "assumed": (320, 2),
    "applied": (190, 3),
    "withdrawn": (420, 0.5),
}
EDGES = [
    ("queued", "open", "asked in a batch"),
    ("open", "answered", "lead picks"),
    ("open", "assumed", "easy, no answer"),
    ("answered", "applied", "change made"),
    ("assumed", "applied", "change made"),
]
EXTRA = """svg .box { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; }
svg .box-lead { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.6; }
svg .box-done { fill:var(--card); stroke:var(--ok); stroke-width:1.8; }
svg .edge { stroke:var(--ink3); stroke-width:1.4; fill:none; }
svg .edge-any { stroke:var(--ink3); stroke-width:1.2; fill:none; stroke-dasharray:4 4; }
svg .head { fill:var(--ink3); }
svg .rule { fill:var(--badsoft); }
svg .rule-t { font:600 13px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bad); }
"""


def states() -> list[tuple[str, str]]:
    head, rows = fk.table(fk.section(README.read_text(encoding="utf-8"), "## Lifecycle"), "Status")
    out = []
    for r in rows:
        name = fk.plain(r[fk.col(head, "Status")])
        meaning = fk.plain(r[fk.col(head, "Meaning")])
        out.append((name, re.split(r"[.;:]", meaning)[0]))
    return out


Y0 = 76


def corner(name: str) -> tuple[float, float]:
    x, r = POS[name]
    return x, Y0 + r * DY


def centre(name: str) -> tuple[float, float]:
    x, y = corner(name)
    return x + BW / 2, y + BH / 2


def arrow(x1: float, y1: float, x2: float, y2: float, cls: str = "edge") -> list[str]:
    """A line from (x1, y1) to (x2, y2) with a head at the end."""
    import math

    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 7 * math.cos(a), y2 - 7 * math.sin(a)
    px, py = 4 * math.sin(a), -4 * math.cos(a)
    return [
        fk.el("line", None, x1=fk.num(x1), y1=fk.num(y1), x2=fk.num(hx), y2=fk.num(hy), class_=cls),
        fk.el(
            "path",
            None,
            d=f"M{fk.num(x2)} {fk.num(y2)} L{fk.num(hx + px)} {fk.num(hy + py)} L{fk.num(hx - px)} {fk.num(hy - py)} Z",
            class_="head",
        ),
    ]


def edge_point(name: str, toward: tuple[float, float]) -> tuple[float, float]:
    """Where the line from the centre of `name` toward a point leaves its box."""
    cx, cy = centre(name)
    tx, ty = toward
    vx, vy = tx - cx, ty - cy
    sx = (BW / 2) / abs(vx) if vx else float("inf")
    sy = (BH / 2) / abs(vy) if vy else float("inf")
    s = min(sx, sy)
    return cx + vx * s, cy + vy * s


def short(meaning: str) -> list[str]:
    """The meaning in at most two lines of the box, cut back to a comma if it is longer."""
    text = meaning
    while len(fk.wrap(text, BW - 20, "s")) > 2 and ", " in text:
        text = text.rsplit(", ", 1)[0]
    return fk.wrap(text, BW - 20, "s")[:2]


def build_svg(st: list[tuple[str, str]]) -> str:
    x0 = 24
    body = [
        fk.text(24, 32, "Lifecycle of a question", "h"),
        fk.text(24, 54, "States of the register (README table); dashed: from any state", "t"),
    ]
    for a, b, label in EDGES:
        ca, cb = centre(a), centre(b)
        p1, p2 = edge_point(a, cb), edge_point(b, ca)
        body += arrow(*p1, *p2)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        if abs(p1[0] - p2[0]) < 1:
            body.append(fk.text(mx + 10, my + 4, label, "s"))
        elif p2[0] < p1[0] or (p2[0] > p1[0] and p2[1] > p1[1] and b == "applied"):
            body.append(fk.text(mx - 10, my + 4, label, "s", "end"))
        else:
            body.append(fk.text(mx + 10, my + 4, label, "s"))
    wc = centre("withdrawn")
    for n in ("queued", "open", "assumed"):
        p1, p2 = edge_point(n, wc), edge_point("withdrawn", centre(n))
        body += arrow(*p1, *p2, cls="edge-any")
    meaning = dict(st)
    for name in POS:
        x, y = corner(name)
        cls = "box-lead" if name == "answered" else "box-done" if name == "applied" else "box"
        body.append(
            fk.el("rect", None, x=fk.num(x), y=fk.num(y), width=BW, height=BH, rx=8, class_=cls)
        )
        body.append(fk.text(x + 10, y + 20, name, "m"))
        for j, ln in enumerate(short(meaning[name])):
            body.append(fk.text(x + 10, y + 37 + 13 * j, ln, "s"))
    y = corner("applied")[1] + BH + 26
    rule = "A hard question is never assumed, and never applied without the lead's answer."
    lines = fk.wrap(rule, W - 2 * x0 - 24, "tb")
    body.append(
        fk.el(
            "rect",
            None,
            x=x0,
            y=fk.num(y),
            width=W - 2 * x0,
            height=16 + 18 * len(lines),
            rx=6,
            class_="rule",
        )
    )
    for j, ln in enumerate(lines):
        body.append(fk.text(x0 + 12, y + 21 + 18 * j, ln, "rule-t"))
    h = y + 16 + 18 * len(lines) + 16
    desc = (
        "States: "
        + "; ".join(f"{n}: {m}" for n, m in st)
        + ". Transitions: "
        + "; ".join(f"{a} to {b} ({lab})" for a, b, lab in EDGES)
        + "; any state to withdrawn. "
        + rule
    )
    return fk.svg(W, int(h), "Lifecycle of a decision register question", desc, body, EXTRA)


def build() -> dict[Path, str]:
    st = states()
    names = [n for n, _ in st]
    if names != list(check_decisions.STATUSES):
        raise fk.FigureError(
            f"README states {names} differ from check_decisions.STATUSES {list(check_decisions.STATUSES)}"
        )
    if set(names) != set(POS):
        raise fk.FigureError(f"README states {names} differ from the states drawn {sorted(POS)}")
    return {OUT: build_svg(st)}


if __name__ == "__main__":
    fk.run(build, __doc__)
