"""Safety mechanism sheet for WP-S-03: one card per safety mechanism, showing where it runs and how fast it must act.

tsc.py calls `sheet()` and writes Figure 3-1 next to the TSC files. Each card shows the system architecture of Figure
2-1 in small, with the component the mechanism runs on (filled) and those it uses (outlined); its time budget from
WP-S-04 (the binding fault tolerant time interval, shared between detecting the fault, reacting to it and a reserve);
the reaction it starts; what it does; and the functional safety requirements it implements. A mechanism with no
WP-S-04 budget says so.

Budgets are the ranges WP-S-04 computes from proposed margins and fault magnitudes; nothing here is a measurement.
The time bar loops (SMIL, 6 s); a viewer that does not animate shows the last frame.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

ASSURANCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ASSURANCE / "02-concept" / "hara"))
import figkit as fk  # noqa: E402
import scenes as sk  # noqa: E402

CW, CH = 330, 462
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
ASILS = ["QM", "A", "B", "C", "D"]

# Short names for the small boxes of the architecture; the "runs on" line uses the full names.
SHORT = {
    "CMP-01": "Autoware",
    "CMP-02": "Safety monitor",
    "CMP-03": "Channel",
    "CMP-04": "LiDAR",
    "CMP-05": "Radar",
    "CMP-06": "Drive-by-wire",
    "CMP-07": "State",
    "CMP-08": "Brake",
    "CMP-09": "Doors",
    "CMP-10": "Monitor power",
    "CMP-11": "Remote ops",
}

# Figure 2-1 places boxes in x 24..616 and y 96..466; a card shows them at this scale.
SX, SY, OX, OY = 0.5, 0.4, 24, 96


def timed() -> tuple[dict, dict]:
    """The timing model of WP-S-04 and its time-critical mechanisms (imported here: timing.py imports tsc)."""
    sys.path.insert(0, str(ASSURANCE / "03-system" / "timing"))
    import timing

    m = timing.load()
    return m, {s["id"]: s for s in m["mechanisms"]}


def budget(s: dict, tm: dict, tmech: dict) -> dict | None:
    """The binding FTTI of a time-critical mechanism, worst and best case in s, with its goal and shares."""
    import timing

    t = tmech.get(s["id"])
    if not t:
        return None
    worst, best, goal = timing.bound(tm, t)
    return {"worst": worst, "best": best, "goal": goal, **tm["allocation"]}


def span(lo: float, hi: float) -> str:
    a, b = f"{lo * 1000:.0f}", f"{hi * 1000:.0f}"
    return f"{a} ms" if a == b else f"{a}–{b} ms"


def arch(ox: float, oy: float, s: dict, comps: list[dict]) -> list[str]:
    def rect(c: dict) -> tuple[float, float, float, float]:
        x, y, w, h = c["box"]
        return ox + (x - OX) * SX, oy + (y - OY) * SY, w * SX, h * SY

    uses = set(s.get("uses") or [])
    out = [fk.el("rect", None, x=ox - 6, y=oy - 6, width=312, height=162, rx=6, class_="verge")]
    hx, hy, hw, hh = rect(next(c for c in comps if c["id"] == s["host"]))
    for c in comps:
        if c["id"] in uses:
            x, y, w, h = rect(c)
            out.append(
                fk.el(
                    "line",
                    None,
                    x1=fk.num(x + w / 2),
                    y1=fk.num(y + h / 2),
                    x2=fk.num(hx + hw / 2),
                    y2=fk.num(hy + hh / 2),
                    class_="lead",
                )
            )
    for c in comps:
        x, y, w, h = rect(c)
        cls, tcls = (
            ("hst", "hstt")
            if c["id"] == s["host"]
            else ("use", "uset") if c["id"] in uses else ("dim", "dimt")
        )
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x),
                y=fk.num(y),
                width=fk.num(w),
                height=fk.num(h),
                rx=3,
                class_=cls,
            )
        )
        label = fk.fit(SHORT.get(c["id"], c["name"]), (w - 4) * 11.5 / 9.5, "s")
        if h >= 16:
            out.append(fk.text(x + w / 2, y + h / 2 + 3.5, label, tcls, "middle"))
    return out


def timebar(ox: float, oy: float, b: dict | None, s: dict) -> list[str]:
    w = 300
    if not b:
        return [
            fk.el("rect", None, x=ox, y=oy, width=w, height=14, rx=3, class_="dim"),
            fk.text(ox + w / 2, oy + 11, "no time budget in WP-S-04", "dimt", "middle"),
            fk.text(ox, oy + 30, "Acts by design or as a limit, not a race against a fault", "ax"),
        ]
    d, r = b["detect"], b["react"]
    parts = [("det", "detect", d), ("rea", "react", r), ("res", "reserve", 1 - d - r)]
    out, x = [], ox
    for cls, name, share in parts:
        out.append(
            fk.el(
                "rect", None, x=fk.num(x), y=oy, width=fk.num(w * share - 1), height=14, class_=cls
            )
        )
        lbl = f"{name} {span(b['worst'] * share, b['best'] * share)}"
        out.append(fk.text(x + 3, oy + 26, fk.fit(lbl, w * share - 4, "s"), "ax"))
        x += w * share
    out.append(
        fk.text(
            ox,
            oy + 42,
            f"FTTI of {b['goal']}: {span(b['worst'], b['best'])} (largest fault first)",
            "ax",
        )
    )
    out.append(sk.cursor(ox, ox + w, oy - 3, oy + 17))
    return out


def card(x: float, y: float, s: dict, k: dict, b: dict | None, reactions: dict) -> list[str]:
    a = max((k["fsrs"][f]["asil"] for f in s["implements"]), key=ASILS.index, default="QM")
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, s["id"], "gid"))
    pill = f"ASIL {a}"
    pw = fk.width(pill, "m") * 0.9 + 14
    out.append(
        fk.el(
            "rect",
            None,
            x=fk.num(x + CW - 14 - pw),
            y=y + 11,
            width=fk.num(pw),
            height=19,
            rx=4,
            class_="pr" if a != "QM" else "pf",
        )
    )
    out.append(
        fk.text(x + CW - 14 - pw / 2, y + 24.5, pill, "prt" if a != "QM" else "pft", "middle")
    )
    out.append(fk.text(x + 60, y + 24, fk.fit(s["name"], CW - 90 - pw, "tb"), "tb"))
    comps = k["components_list"]
    name = {c["id"]: c["name"] for c in comps}
    where = f"Runs on {name[s['host']]}" + (
        f"; uses {', '.join(name[c] for c in s['uses'])}" if s.get("uses") else ""
    )
    for i, ln in enumerate(fk.wrap(where, CW - 28, "s")[:3]):
        out.append(fk.text(x + 14, y + 42 + 14 * i, ln, "ax"))
    out += arch(x + 15, y + 88, s, comps)
    out += timebar(x + 15, y + 260, b, s)
    react = (
        "; ".join(f"{r} {reactions.get(r, '')}".strip() for r in s["reaction"])
        if s["reaction"]
        else "none of its own"
    )
    yy = y + 320
    for ln in fk.wrap("Reaction: " + react, CW - 28, "s")[:2]:
        out.append(fk.text(x + 14, yy, ln, "s"))
        yy += 15
    for ln in fk.wrap(s["does"], CW - 28, "s")[:6]:
        out.append(fk.text(x + 14, yy + 3, ln, "ax"))
        yy += 14
    lines = fk.wrap("Implements " + ", ".join(s["implements"]), CW - 28, "s")
    for ln in lines[:2]:
        out.append(fk.text(x + 14, yy + 6, ln, "s"))
        yy += 15
    return out


EXTRA = sk.EXTRA + """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --amb2:#b97800; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --amb2:#e7a52a; } }
svg .hst { fill:var(--mon); } svg .hstt { font:600 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .use { fill:var(--monsoft); stroke:var(--mon); stroke-width:1.2; }
svg .uset { font:600 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--mon); }
svg .dim { fill:var(--bg); stroke:var(--grid); stroke-width:1; }
svg .dimt { font:9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .lead { stroke:var(--mon); stroke-width:1.2; stroke-dasharray:3 2; }
svg .det { fill:var(--mon); } svg .rea { fill:var(--amb2); } svg .res { fill:var(--grid); }
"""


def sheet(m: dict, k: dict) -> str:
    tm, tmech = timed()
    reactions = k["reaction_names"]
    mechs = m["mechanisms"]
    rows = math.ceil(len(mechs) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "Where each safety mechanism runs, and how fast it must act", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-03 §3, Figure 3-1: the component each mechanism runs on (filled) and uses (outlined), and "
            "its share of the fault tolerant time interval",
            "t",
        ),
        fk.text(MARGIN, 73, "from WP-S-04. Budgets are computed ranges, not measurements.", "t"),
    ]
    for i, s in enumerate(mechs):
        body += card(
            MARGIN + (i % COLS) * (CW + GAP),
            HEAD + (i // COLS) * (CH + GAP),
            s,
            k,
            budget(s, tm, tmech),
            reactions,
        )
    ly = h - 26
    body += [
        fk.el("rect", None, x=MARGIN, y=ly - 11, width=22, height=14, rx=3, class_="hst"),
        fk.text(MARGIN + 30, ly, "runs on", "t"),
        fk.el("rect", None, x=MARGIN + 100, y=ly - 11, width=22, height=14, rx=3, class_="use"),
        fk.text(MARGIN + 130, ly, "uses", "t"),
        fk.el("rect", None, x=MARGIN + 200, y=ly - 11, width=22, height=14, class_="det"),
        fk.text(MARGIN + 230, ly, "time to detect", "t"),
        fk.el("rect", None, x=MARGIN + 350, y=ly - 11, width=22, height=14, class_="rea"),
        fk.text(MARGIN + 380, ly, "time to react", "t"),
        fk.el("rect", None, x=MARGIN + 490, y=ly - 11, width=22, height=14, class_="res"),
        fk.text(MARGIN + 520, ly, "reserve, within the FTTI", "t"),
    ]
    desc = "Safety mechanisms: " + "; ".join(
        f"{s['id']} {s['name']} runs on {s['host']}"
        + (f", uses {', '.join(s['uses'])}" if s.get("uses") else "")
        + (
            f", FTTI of {b['goal']} {span(b['worst'], b['best'])}"
            if (b := budget(s, tm, tmech))
            else ", no time budget"
        )
        for s in mechs
    )
    return fk.svg(w, h, "WP-S-03 Figure 3-1: safety mechanisms", desc + ".", body, EXTRA)
