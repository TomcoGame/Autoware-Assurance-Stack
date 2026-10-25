"""Envelope parameter sheet for WP-S-02: one card per parameter, showing what it bounds.

tsr.py calls `sheet()` and writes Figure 2-1 next to the TSR files. Each card shows a schematic of what the parameter
bounds, on the road or over time, then the parameter's value or source exactly as WP-S-02 §2.1 states it, where that
comes from (the timing model, a decision of the lead, or the vehicle still to be chosen), and the requirements that
use it. The drawings carry no numbers: every value is the text below them, so a value changed in tsr.yaml or the
timing model changes the card and cannot disagree with the drawing.

tsr.py refuses a parameter without a drawing here, or a drawing for a parameter that does not exist.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "02-concept" / "hara"))
import figkit as fk  # noqa: E402
import scenes as sk  # noqa: E402

CW, CH = 330, 316
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
DN, UP = sk.DN, sk.UP
SW, SH = sk.SW, sk.SH


def dim(
    ox: float, oy: float, x1: float, x2: float, y: float, label: str, cls: str = "dm"
) -> list[str]:
    """A horizontal dimension line from x1 to x2 at y, with ticks and a label above."""
    a, b = ox + min(x1, x2), ox + max(x1, x2)
    return [
        fk.el(
            "line",
            None,
            x1=fk.num(a),
            y1=fk.num(oy + y),
            x2=fk.num(b),
            y2=fk.num(oy + y),
            class_=cls,
        ),
        fk.el(
            "line",
            None,
            x1=fk.num(a),
            y1=fk.num(oy + y - 5),
            x2=fk.num(a),
            y2=fk.num(oy + y + 5),
            class_=cls,
        ),
        fk.el(
            "line",
            None,
            x1=fk.num(b),
            y1=fk.num(oy + y - 5),
            x2=fk.num(b),
            y2=fk.num(oy + y + 5),
            class_=cls,
        ),
        fk.text((a + b) / 2, oy + y - 7, label, "dmt", "middle"),
    ]


def vdim(ox: float, oy: float, x: float, y1: float, y2: float, label: str) -> list[str]:
    a, b = oy + min(y1, y2), oy + max(y1, y2)
    return [
        fk.el(
            "line",
            None,
            x1=fk.num(ox + x),
            y1=fk.num(a),
            x2=fk.num(ox + x),
            y2=fk.num(b),
            class_="dm",
        ),
        fk.el(
            "line",
            None,
            x1=fk.num(ox + x - 5),
            y1=fk.num(a),
            x2=fk.num(ox + x + 5),
            y2=fk.num(a),
            class_="dm",
        ),
        fk.el(
            "line",
            None,
            x1=fk.num(ox + x - 5),
            y1=fk.num(b),
            x2=fk.num(ox + x + 5),
            y2=fk.num(b),
            class_="dm",
        ),
        fk.text(ox + x + 8, (a + b) / 2 + 4, label, "dmt"),
    ]


def arrow(
    ox: float, oy: float, x1: float, y1: float, x2: float, y2: float, cls: str = "mv"
) -> list[str]:
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 7 * math.cos(a), y2 - 7 * math.sin(a)
    px, py = 4 * math.sin(a), -4 * math.cos(a)
    return [
        fk.el(
            "line",
            None,
            x1=fk.num(ox + x1),
            y1=fk.num(oy + y1),
            x2=fk.num(ox + x2),
            y2=fk.num(oy + y2),
            class_=cls,
        ),
        fk.el(
            "path",
            None,
            d=f"M{fk.num(ox + x2)} {fk.num(oy + y2)} L{fk.num(ox + hx + px)} {fk.num(oy + hy + py)} "
            f"L{fk.num(ox + hx - px)} {fk.num(oy + hy - py)} Z",
            class_=cls + "h",
        ),
    ]


def plot(ox: float, oy: float, ylabel: str, xlabel: str) -> list[str]:
    """An empty plot area filling the drawing space, with axis labels."""
    return [
        fk.el("rect", None, x=ox, y=oy, width=SW, height=SH, rx=6, class_="plot"),
        fk.el(
            "line",
            None,
            x1=ox + 30,
            y1=oy + SH - 22,
            x2=ox + SW - 10,
            y2=oy + SH - 22,
            class_="axis",
        ),
        fk.el("line", None, x1=ox + 30, y1=oy + 10, x2=ox + 30, y2=oy + SH - 22, class_="axis"),
        fk.text(ox + 34, oy + 18, "↑ " + ylabel, "ax"),
        fk.text(ox + SW - 10, oy + SH - 8, xlabel + " →", "ax", "end"),
    ]


def ego(ox: float, oy: float, x: float, y: float = DN) -> str:
    return sk.car(ox + x, oy + y, "ego2")


def draw(pid: str, ox: float, oy: float) -> list[str]:
    road = sk.road
    if pid == "P-01":
        return (
            road(ox, oy)
            + [ego(ox, oy, 50), sk.car(ox + 250, oy + DN, "oth")]
            + dim(ox, oy, 62, 205, DN - 16, "safe distance (P-06)")
            + dim(ox, oy, 205, 238, DN + 20, "P-01", "dmr")
        )
    if pid == "P-02":
        return (
            road(ox, oy)
            + [
                fk.el(
                    "rect",
                    None,
                    x=ox + 20,
                    y=oy + DN - 9,
                    width=200,
                    height=18,
                    rx=3,
                    class_="swept",
                ),
                ego(ox, oy, 40),
                fk.el(
                    "rect",
                    None,
                    x=fk.num(ox + 170),
                    y=fk.num(oy + DN + 13),
                    width=16,
                    height=5,
                    rx=2.5,
                    class_="bike",
                ),
            ]
            + vdim(ox, oy, 230, DN + 9, DN + 15.5, "P-02")
            + [fk.text(ox + 120, oy + DN - 13, "swept path", "dmt", "middle")]
        )
    if pid == "P-03":
        return (
            road(ox, oy)
            + sk.crosswalk(ox, oy, 196, 220)
            + [
                sk.stopline(ox, oy, 189),
                sk.person(ox + 208, oy + 74),
                sk.car(ox + 190, oy + DN, "ghostr"),
                ego(ox, oy, 172),
            ]
            + dim(ox, oy, 184, 202, DN - 16, "P-03", "dmr")
            + [fk.text(ox + 100, oy + DN + 4, "held at standstill", "dmt", "middle")]
        )
    if pid == "P-04":
        path = [(22 + 10 * i, DN + 9 * math.sin(i / 3)) for i in range(25)]
        return (
            road(ox, oy)
            + [
                fk.el(
                    "path",
                    None,
                    d=f"M{ox + 18} {oy + 22} L{ox + 24} {oy + 6} L{ox + 30} {oy + 22}",
                    class_="mast",
                ),
                fk.text(ox + 36, oy + 19, "remote operator", "ax"),
                fk.el("path", None, d=sk.poly(ox, oy, path), class_="mvp"),
                ego(ox, oy, 262, path[-1][1]),
            ]
            + vdim(ox, oy, 282, DN - 9, DN + 9, "P-04")
        )
    if pid == "P-05":
        out = plot(ox, oy, "deceleration", "time")
        x0, x1, base = ox + 30, ox + SW - 10, oy + SH - 22
        out += [
            fk.el("line", None, x1=x0, y1=base - 66, x2=x1, y2=base - 66, class_="cap2"),
            fk.text(x1 - 4, base - 70, "emergency", "ax", "end"),
            fk.el("line", None, x1=x0, y1=base - 30, x2=x1, y2=base - 30, class_="cap"),
            fk.text(x1 - 4, base - 34, "P-05", "dmt", "end"),
            fk.el(
                "path",
                None,
                d=f"M{x0} {base} L{x0 + 60} {base} L{x0 + 60} {base - 30} L{x1 - 40} {base - 30} L{x1 - 40} {base}",
                class_="mvp",
            ),
            fk.el("path", None, d=f"M{x0 + 60} {base - 30} L{x0 + 60} {base - 66}", class_="cut"),
            fk.text(x0 + 66, base - 50, "unconfirmed braking held here", "ax"),
        ]
        return out
    if pid == "P-06":
        return (
            road(ox, oy)
            + [ego(ox, oy, 40), sk.car(ox + 262, oy + DN, "oth")]
            + dim(ox, oy, 52, 92, DN - 18, "response")
            + dim(ox, oy, 92, 200, DN - 18, "own braking")
            + dim(ox, oy, 200, 250, DN - 18, "")
            + [fk.text(ox + 225, oy + DN - 25, "less lead's", "dmt", "middle")]
            + dim(ox, oy, 52, 250, DN + 20, "safe distance")
        )
    if pid == "P-07":
        return (
            road(ox, oy)
            + [
                fk.el(
                    "rect", None, x=ox + 150, y=oy + DN + 3, width=44, height=14, rx=3, class_="oth"
                ),
                ego(ox, oy, 60),
                sk.person(ox + 172, oy + SH - 12),
                fk.el(
                    "rect",
                    None,
                    x=ox + 236,
                    y=oy + UP - 2.5,
                    width=16,
                    height=5,
                    rx=2.5,
                    class_="bike",
                ),
            ]
            + arrow(ox, oy, 172, SH - 18, 172, DN + 22)
            + arrow(ox, oy, 236, UP + 6, 210, DN - 4)
            + [
                fk.text(ox + 164, oy + SH - 10, "pedestrian, from the occlusion", "ax", "end"),
                fk.text(ox + 256, oy + UP + 4, "cyclist", "ax"),
            ]
        )
    if pid in ("P-08", "P-09"):
        out = plot(ox, oy, "messages" if pid == "P-08" else "remote commands", "time")
        base = oy + SH - 22
        ticks = [40, 60, 80, 100, 120] if pid == "P-08" else [40, 70, 100]
        for x in ticks:
            out.append(
                fk.el("line", None, x1=ox + x, y1=base, x2=ox + x, y2=base - 30, class_="tick")
            )
        if pid == "P-08":
            out += dim(ox, oy, 120, 230, SH - 64, "P-08", "dmr")
            out += [
                fk.text(ox + 175, oy + SH - 28, "monitor silent", "ax", "middle"),
                fk.el("path", None, d=f"M{ox + 230} {base - 44} L{ox + 230} {base}", class_="cut"),
                fk.text(ox + SW - 8, oy + 36, "vehicle stops itself", "dmt", "end"),
            ]
        else:
            out += [
                fk.el(
                    "line", None, x1=ox + 160, y1=base, x2=ox + 160, y2=base - 30, class_="tickr"
                ),
                fk.text(ox + 166, base - 20, "old command", "ax"),
            ]
            out += dim(ox, oy, 100, 160, SH - 64, "P-09", "dmr")
            out += [fk.text(ox + SW - 8, oy + 36, "older than P-09: rejected, stop", "dmt", "end")]
        return out
    if pid == "P-10":
        out = plot(ox, oy, "steering angle", "speed")
        x0, x1, base, top = ox + 30, ox + SW - 10, oy + SH - 22, oy + 26
        pts = [
            (x0 + (x1 - x0) * i / 20, top + (base - top) * (1 - 1 / (1 + (i / 6) ** 2)))
            for i in range(21)
        ]
        d = (
            f"M{x0} {base} "
            + " ".join(f"L{fk.num(x)} {fk.num(y)}" for x, y in pts)
            + f" L{x1} {base} Z"
        )
        out += [
            fk.el("path", None, d=d, class_="allow"),
            fk.el(
                "path",
                None,
                d="M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in pts),
                class_="cap",
            ),
            fk.text(x0 + 140, top + 40, "allowed below P-10", "dmt"),
        ]
        return out
    if pid == "P-11":
        out = plot(ox, oy, "acceleration", "time")
        x0, x1, base = ox + 30, ox + SW - 10, oy + SH - 22
        cmd = [(x0, base - 20), (x0 + 60, base - 20), (x0 + 60, base - 55), (x1, base - 55)]
        band_hi = [(x, y - 10) for x, y in cmd]
        band_lo = [(x, y + 10) for x, y in cmd][::-1]
        out += [
            fk.el(
                "path",
                None,
                d="M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in band_hi + band_lo) + " Z",
                class_="allow",
            ),
            fk.el(
                "path",
                None,
                d="M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in cmd),
                class_="cap",
            ),
            fk.el(
                "path",
                None,
                d=f"M{x0} {base - 22} L{x0 + 70} {base - 24} L{x0 + 100} {base - 52} L{x0 + 170} {base - 57} "
                f"L{x0 + 190} {base - 78}",
                class_="mvp",
            ),
            fk.el("circle", None, cx=x0 + 190, cy=base - 78, r=8, class_="ring2"),
            fk.text(x0 + 178, base - 76, "outside ±P-11: fault", "dmt", "end"),
        ]
        return out
    if pid == "P-12":
        return (
            road(ox, oy)
            + [
                ego(ox, oy, 30),
                fk.el("rect", None, x=ox + 248, y=oy + DN - 3, width=6, height=6, class_="obj"),
            ]
            + dim(ox, oy, 42, 251, DN - 18, "range: stopping distance at top ODD speed")
            + [fk.text(ox + 258, oy + DN + 28, "smallest object", "ax", "end")]
        )
    if pid == "P-13":
        return (
            road(ox, oy)
            + [
                ego(ox, oy, 60),
                fk.el(
                    "rect",
                    None,
                    x=ox + 190,
                    y=oy + DN - 7,
                    width=18,
                    height=14,
                    rx=3,
                    class_="phantom",
                ),
                sk.car(ox + 30, oy + DN, "oth"),
            ]
            + [
                fk.text(ox + 199, oy + DN - 13, "nothing there", "dmt", "middle"),
                fk.text(
                    ox + 150,
                    oy + SH - 10,
                    "each false detection can brake: rate ≤ P-13, per sensor",
                    "ax",
                    "middle",
                ),
            ]
        )
    raise fk.FigureError(f"{pid}: no drawing in pcards.py")


DRAWN = {f"P-{i:02d}" for i in range(1, 14)}


def origin(p: dict) -> tuple[str, str]:
    """Where a parameter's value comes from, as a short pill label and its class."""
    if p.get("margin") or p.get("budget"):
        return "WP-S-04", "po"
    if p.get("value"):
        return p["decision"], "pd"
    if p.get("pending"):
        return f"waits {p['pending']}", "pw"
    return "to be set", "pw"


EXTRA = sk.EXTRA + """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --dimc:#4b525c; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --dimc:#b9bfc8; } }
svg .ego2 { fill:var(--mon); } svg .ego2w { fill:var(--bg); opacity:.75; }
svg .ghostr { fill:none; stroke:var(--perf); stroke-width:1.4; stroke-dasharray:3 2; } svg .ghostrw { fill:none; }
svg .dm { stroke:var(--dimc); stroke-width:1.2; } svg .dmr { stroke:var(--perf); stroke-width:1.6; }
svg .dmt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .swept { fill:var(--monsoft); stroke:var(--mon); stroke-width:1; stroke-dasharray:3 2; }
svg .mv { stroke:var(--perf); stroke-width:1.6; } svg .mvh { fill:var(--perf); }
svg .mvp { fill:none; stroke:var(--mon); stroke-width:2.2; stroke-linejoin:round; }
svg .cap { fill:none; stroke:var(--amber); stroke-width:2; stroke-dasharray:5 3; }
svg .cap2 { stroke:var(--ink3); stroke-width:1.2; stroke-dasharray:2 3; }
svg .cut { stroke:var(--perf); stroke-width:1.6; stroke-dasharray:3 2; }
svg .allow { fill:var(--monsoft); }
svg .tick { stroke:var(--mon); stroke-width:3; } svg .tickr { stroke:var(--perf); stroke-width:3; }
svg .ring2 { fill:none; stroke:var(--perf); stroke-width:1.6; }
svg .obj { fill:var(--ink); }
svg .phantom { fill:none; stroke:var(--perf); stroke-width:1.4; stroke-dasharray:3 2; }
svg .po { fill:var(--monsoft); stroke:var(--mon); stroke-width:1; } svg .pot { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--mon); }
svg .pd { fill:var(--a3); } svg .pdt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:#ffffff; }
svg .pw { fill:var(--bg); stroke:var(--ink3); stroke-width:1; stroke-dasharray:3 2; } svg .pwt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""


def card(x: float, y: float, p: dict, val: str, users: list[str]) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, p["id"], "gid"))
    label, cls = origin(p)
    pw = fk.width(label, "m") * 0.85 + 14
    out.append(
        fk.el(
            "rect",
            None,
            x=fk.num(x + CW - 14 - pw),
            y=y + 11,
            width=fk.num(pw),
            height=18,
            rx=4,
            class_=cls,
        )
    )
    out.append(fk.text(x + CW - 14 - pw / 2, y + 24, label, cls + "t", "middle"))
    for i, ln in enumerate(fk.wrap(p["name"], CW - 28, "tb")[:3]):
        out.append(fk.text(x + 14, y + 44 + 16 * i, ln, "tb"))
    out += draw(p["id"], x + 15, y + 92)
    yy = y + 230
    for ln in fk.wrap(val, CW - 28, "s")[:4]:
        out.append(fk.text(x + 14, yy, ln, "s"))
        yy += 15
    for ln in fk.wrap("Used by " + ", ".join(users), CW - 28, "s")[:3]:
        out.append(fk.text(x + 14, yy + 4, ln, "ax"))
        yy += 14
    return out


def sheet(m: dict, values: dict[str, str]) -> str:
    ps = m["parameters"]
    rows = math.ceil(len(ps) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "What each envelope parameter bounds", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-02 §2.1, Figure 2-1: a schematic of what each parameter bounds, its value or source as WP-S-02 "
            "states it, and the requirements",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "that use it. The drawings carry no numbers; the values are the text below them.",
            "t",
        ),
    ]
    for i, p in enumerate(ps):
        users = [r["id"] for r in m["tsrs"] if p["id"] in (r.get("params") or [])]
        body += card(
            MARGIN + (i % COLS) * (CW + GAP),
            HEAD + (i // COLS) * (CH + GAP),
            p,
            values[p["id"]],
            users,
        )
    ly = h - 26
    lx = MARGIN
    for cls, label in (
        ("po", "from the timing model (WP-S-04)"),
        ("pd", "decided by the lead"),
        ("pw", "to be set (vehicle, data or targets)"),
    ):
        body += [
            fk.el("rect", None, x=lx, y=ly - 12, width=22, height=16, rx=4, class_=cls),
            fk.text(lx + 30, ly, label, "t"),
        ]
        lx += 30 + fk.width(label, "t") + 24
    desc = "Envelope parameters: " + "; ".join(
        f"{p['id']} {p['name']}: {values[p['id']]}" for p in ps
    )
    return fk.svg(w, h, "WP-S-02 Figure 2-1: envelope parameters", desc + ".", body, EXTRA)


def check(m: dict) -> list[str]:
    ids = {p["id"] for p in m.get("parameters", [])}
    errs = [f"{p}: no drawing in pcards.py" for p in sorted(ids - DRAWN)]
    errs += [
        f"{p}: drawing in pcards.py for a parameter that does not exist"
        for p in sorted(DRAWN - ids)
    ]
    return errs
