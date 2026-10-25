"""Safety goal scene sheet for WP-C-04: one card per safety goal, showing how the concept holds it.

fsc.py calls `sheet()` and writes Figure 4-2 next to the FSC files. Each card shows, over time, what Autoware (or a
remote operator) commands when it goes wrong (red, dashed), the bound the safety envelope sets (amber), and what
reaches the vehicle through the safety monitor (blue). Under it, a top-down scene of the hazard the goal prevents:
where the faulty command would take the vehicle (red ghost), where the monitor steps in, and the safe state the item
reaches instead (blue). The card lists the rated FSRs by the element that carries them, from fsc.yaml.

The charts and scenes are schematic: they explain the concept and are not simulation results. Each card loops (SMIL,
6 s); a viewer that does not animate shows the last frame. The road, vehicles and animation come from the HARA scene
kit (../hara/scenes.py), so both sheets read the same way.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hara"))
import figkit as fk  # noqa: E402
import scenes as sk  # noqa: E402

CW, CH = 330, 478
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 84
DN, UP = sk.DN, sk.UP

# Safety goal: chart (quantity, command, bound, passed) and scene. Series are step lists over time 0..100 with values
# -100..100; `None` for a series that does not apply. Scene units are those of the HARA scene kit (300 x 120).
GOALS = {
    "SG-01": {
        "chart": (
            "Acceleration",
            [(0, 20), (35, 20), (35, 95), (100, 95)],
            [(0, 50), (60, 50), (60, -50), (100, -50)],
            [(0, 20), (35, 20), (35, 50), (60, 50), (60, -50), (100, -50)],
        ),
        "others": [(240, DN)],
        "fault": [(22, DN), (222, DN)],
        "item": [(22, DN), (176, DN)],
        "at": 0.35,
        "act": "EL-02 bounds, then brakes",
        "end": "held at standstill",
    },
    "SG-02": {
        "chart": (
            "Deceleration",
            [(0, 15), (100, 15)],
            [(0, 15), (40, 15), (40, 75), (100, 75)],
            [(0, 15), (45, 15), (45, 75), (100, 75)],
        ),
        "zebra": (206, 230),
        "stop": 199,
        "people": [(218, 72)],
        "fault": [(22, DN), (226, DN)],
        "item": [(22, DN), (184, DN)],
        "at": 0.45,
        "act": "EL-02 brakes",
        "end": "stops before the crosswalk",
    },
    "SG-03": {
        "chart": (
            "Deceleration",
            [(0, 10), (40, 10), (40, 95), (70, 95), (70, 10), (100, 10)],
            [(0, 45), (100, 45)],
            [(0, 10), (40, 10), (40, 45), (70, 45), (70, 10), (100, 10)],
        ),
        "follow": [(30, DN), (200, DN)],
        "fault": [(80, DN), (150, DN)],
        "item": [(80, DN), (238, DN)],
        "at": 0.4,
        "act": "EL-02 limits unconfirmed braking",
        "end": "the car behind keeps its gap",
    },
    "SG-04": {
        "chart": (
            "Steering",
            [(0, 10), (35, 10), (35, 90), (100, 90)],
            [(0, 40), (100, 40)],
            [(0, 10), (100, 10)],
        ),
        "others": [(258, UP)],
        "fault": "drift",
        "item": [(22, DN), (204, DN)],
        "at": 0.35,
        "act": "EL-02 rejects the steering",
        "end": "stopped in its lane",
    },
    "SG-05": {
        "chart": (
            "Motion at standstill",
            [(0, 0), (30, 0), (30, 60), (100, 60)],
            [(0, 0), (100, 0)],
            [(0, 0), (100, 0)],
        ),
        "zebra": (196, 220),
        "stop": 189,
        "people": [(208, 74)],
        "fault": [(172, DN), (194, DN)],
        "item": [(172, DN)],
        "at": 0.3,
        "act": "EL-02 holds, EL-05 park brake",
        "end": "held, park brake on",
    },
    "SG-06": {
        "chart": (
            "Speed into the conflict area",
            [(0, 60), (100, 60)],
            [(0, 60), (40, 60), (40, 0), (100, 0)],
            [(0, 60), (40, 60), (45, 40), (50, 25), (55, 12), (60, 0), (100, 0)],
        ),
        "junction": (204, 252),
        "stop": 196,
        "others_v": [(228, UP + 2)],
        "fault": [(22, DN), (276, DN)],
        "item": [(22, DN), (180, DN)],
        "at": 0.4,
        "act": "EL-02 refuses entry",
        "end": "stops at the line",
    },
    "SG-07": {
        "chart": (
            "Speed",
            [(0, 60), (40, 60)],
            [(0, 100), (45, 100), (45, 0), (100, 0)],
            [(0, 60), (45, 60), (52, 40), (59, 22), (66, 8), (72, 0), (100, 0)],
        ),
        "fault": [(22, DN), (282, DN)],
        "item": [(22, DN), (204, DN)],
        "at": 0.4,
        "act": "EL-02 detects the loss",
        "end": "stopped in lane, hazards on",
        "hazards": True,
    },
    "SG-08": {
        "chart": (
            "Speed (remote)",
            [(0, 50), (100, 50)],
            [(0, 100), (45, 100), (45, 0), (100, 0)],
            [(0, 50), (45, 50), (52, 30), (59, 14), (66, 0), (100, 0)],
        ),
        "others": [(250, DN)],
        "remote": True,
        "fault": [(22, DN), (233, DN)],
        "item": [(22, DN), (204, DN)],
        "at": 0.45,
        "act": "EL-02 rejects the old command",
        "end": "stopped and held",
    },
    "SG-09": {
        "chart": (
            "Indicator side",
            [(0, 0), (30, 0), (30, -60), (100, -60)],
            [(0, 0), (30, 0), (30, 60), (100, 60)],
            [(0, 0), (30, 0), (30, -60), (38, -60), (38, 0), (100, 0)],
        ),
        "side": True,
        "bikes": [(176, 89)],
        "fault": "turn",
        "item": "turn",
        "at": 0.38,
        "act": "EL-02: signals left, turns right",
        "end": "hazard lights warn the cyclist",
        "hazards": True,
    },
}

CHART_X0, CHART_X1, CHART_Y0, CHART_Y1 = 34, 292, 10, 84


def chart(ox: float, oy: float, spec: tuple) -> list[str]:
    quantity, cmd, bound, passed = spec
    signed = any(v < 0 for s in (cmd, bound, passed) if s for _, v in s)
    zero = (CHART_Y0 + CHART_Y1) / 2 if signed else CHART_Y1 - 2
    span = (CHART_Y1 - CHART_Y0) / (2 if signed else 1)

    def d(pts: list) -> str:
        xy = []
        for k, (t, v) in enumerate(pts):
            x, y = ox + CHART_X0 + t / 100 * (CHART_X1 - CHART_X0), oy + zero - v / 100 * span
            if k and pts[k - 1][0] == t:
                xy.append((x, y))
            elif k:
                xy.append((x, xy[-1][1]))
                xy.append((x, y))
            else:
                xy.append((x, y))
        return "M" + " L".join(f"{fk.num(a)} {fk.num(b)}" for a, b in xy)

    x0, x1 = ox + CHART_X0, ox + CHART_X1
    out = [
        fk.el(
            "rect",
            None,
            x=x0,
            y=oy + CHART_Y0 - 4,
            width=CHART_X1 - CHART_X0,
            height=CHART_Y1 - CHART_Y0 + 6,
            class_="plot",
        ),
        fk.el("line", None, x1=x0, y1=oy + zero, x2=x1, y2=oy + zero, class_="axis"),
        fk.text(x0, oy + CHART_Y1 + 14, "↑ " + fk.fit(quantity, 170, "s"), "ax"),
        fk.text(x1, oy + CHART_Y1 + 14, "time →", "ax", "end"),
    ]
    if bound:
        out.append(fk.el("path", None, d=d(bound), class_="bnd"))
    out.append(fk.el("path", None, d=d(cmd), class_="cmd"))
    out.append(fk.el("path", None, d=d(passed), class_="mon"))
    out.append(sk.cursor(x0, x1, oy + CHART_Y0 - 4, oy + CHART_Y1 + 2))
    return out


def paths(g: str, s: dict) -> tuple[list, list]:
    if s["fault"] == "drift":
        x_on = 22 + 200 * s["at"]
        return sk.drift(22, DN, x_on, UP, 268), s["item"]
    if s["fault"] == "turn":
        turn = [(22, DN), (183, DN)] + [
            (
                183 + 34 * math.sin(math.pi / 2 * k / 8),
                DN + 34 * (1 - math.cos(math.pi / 2 * k / 8)),
            )
            for k in range(1, 9)
        ]
        return turn, turn
    return s["fault"], s["item"]


def scene(ox: float, oy: float, g: str) -> list[str]:
    s = GOALS[g]
    out = sk.road(ox, oy, s.get("junction"), s.get("side", False))
    if "zebra" in s:
        out += sk.crosswalk(ox, oy, *s["zebra"])
    if "stop" in s:
        out.append(sk.stopline(ox, oy, s["stop"]))
    for x, y in s.get("others", []):
        out.append(sk.car(ox + x, oy + y, "oth"))
    for x, y in s.get("others_v", []):
        out.append(sk.car(ox + x, oy + y, "oth", vertical=True))
    for x, y in s.get("people", []):
        out.append(sk.person(ox + x, oy + y))
    for x, y in s.get("bikes", []):
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(ox + x - 8),
                y=fk.num(oy + y - 2.5),
                width=16,
                height=5,
                rx=2.5,
                class_="bike",
            )
        )
    if s.get("remote"):
        out += [
            fk.el(
                "path",
                None,
                d=f"M{ox + 18} {oy + 22} L{ox + 24} {oy + 6} L{ox + 30} {oy + 22}",
                class_="mast",
            ),
            fk.text(ox + 36, oy + 19, "remote command, too old", "ax"),
        ]
    fault, item = paths(g, s)
    if "follow" in s:
        f = s["follow"]
        out.append(sk.car(ox + f[-1][0], oy + f[-1][1], "oth", anim=sk.motion(ox, oy, f)))
    if g == "SG-09":
        out.append(fk.el("path", None, d=sk.poly(ox, oy, item), class_="ipath2"))
        out.append(sk.car(ox + 130, oy + DN, "ego2"))
        out.append(
            f"<g>{sk.blinkers(ox + 130, oy + DN, 'left', 'bl')}"
            f"{sk.blinkers(ox + 130, oy + DN, 'right', 'bl')}{sk.blink()}</g>"
        )
        mx, my = 130, DN
    else:
        out.append(fk.el("path", None, d=sk.poly(ox, oy, fault), class_="fpath"))
        fx, fy = fault[-1]
        out.append(sk.car(ox + fx, oy + fy, "fghost", anim=sk.motion(ox, oy, fault)))
        if len(item) > 1:
            out.append(
                f'<path d="{sk.poly(ox, oy, item)}" class="ipath2" pathLength="1">{sk.draw_on()}</path>'
            )
        ex, ey = item[-1]
        anim = sk.motion(ox, oy, item)
        body = sk.car(ox + ex, oy + ey, "ego2")
        if s.get("hazards"):
            body += (
                f"<g>{sk.blinkers(ox + ex, oy + ey, 'left', 'bl')}"
                f"{sk.blinkers(ox + ex, oy + ey, 'right', 'bl')}{sk.blink()}</g>"
            )
        out.append(f"<g>{body}{anim}</g>")
        mx, my = sk.along(item, s["at"]) if len(item) > 1 else item[0]
    t_on = sk.DRIVE * s["at"]
    out.append(
        f"<g>{fk.el('circle', None, cx=fk.num(ox + mx), cy=fk.num(oy + my - 15), r=7, class_='mk')}"
        f"{fk.text(ox + mx, oy + my - 11.5, 'M', 'mkt', 'middle')}{sk.appear(t_on)}</g>"
    )
    lw = fk.width(s["act"], "s") + 12
    lx = min(max(ox + mx - lw / 2, ox + 4), ox + sk.SW - lw - 4)
    out.append(
        f"<g>{fk.el('rect', None, x=fk.num(lx), y=fk.num(oy + 4), width=fk.num(lw), height=17, rx=8.5, class_='actb')}"
        f"{fk.text(lx + lw / 2, oy + 16, s['act'], 'actt', 'middle')}"
        f"{fk.el('line', None, x1=fk.num(ox + mx), y1=oy + 21, x2=fk.num(ox + mx), y2=fk.num(oy + my - 22), class_='lead')}"
        f"{sk.appear(t_on)}</g>"
    )
    end = item[-1] if g != "SG-09" else s["bikes"][0]
    lw = fk.width(s["end"], "s") + 14
    lx = min(max(ox + end[0] - lw / 2, ox + 4), ox + sk.SW - lw - 4)
    out.append(
        f"<g>{fk.el('circle', None, cx=fk.num(ox + end[0]), cy=fk.num(oy + end[1]), r=12, class_='okring')}"
        f"{fk.el('rect', None, x=fk.num(lx), y=oy + sk.SH - 22, width=fk.num(lw), height=18, rx=9, class_='okb')}"
        f"{fk.text(lx + lw / 2, oy + sk.SH - 9, s['end'], 'ct', 'middle')}{sk.appear(sk.DRIVE * 0.98)}</g>"
    )
    return out


EXTRA = sk.EXTRA + """svg { --mon:#2d55c8; --bnd:#b97800; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --bnd:#e7a52a; } }
svg .cmd { fill:none; stroke:var(--perf); stroke-width:2; stroke-dasharray:5 4; }
svg .bnd { fill:none; stroke:var(--bnd); stroke-width:2; stroke-dasharray:2 3; }
svg .mon { fill:none; stroke:var(--mon); stroke-width:2.6; stroke-linejoin:round; }
svg .fpath { fill:none; stroke:var(--perf); stroke-width:2; stroke-dasharray:5 4; }
svg .ipath2 { fill:none; stroke:var(--mon); stroke-width:2.6; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:1 1; }
svg .fghost { fill:none; stroke:var(--perf); stroke-width:1.4; stroke-dasharray:3 2; } svg .fghostw { fill:none; }
svg .ego2 { fill:var(--mon); } svg .ego2w { fill:var(--bg); opacity:.75; }
svg .bl { fill:var(--amber); }
svg .mk { fill:var(--mon); } svg .mkt { font:700 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .actb { fill:var(--bg); stroke:var(--mon); stroke-width:1.2; }
svg .actt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--mon); }
svg .lead { stroke:var(--mon); stroke-width:1; stroke-dasharray:2 2; }
svg .okring { fill:none; stroke:var(--mon); stroke-width:1.6; }
svg .okb { fill:var(--mon); }
svg .lc { stroke:var(--perf); stroke-width:2; stroke-dasharray:5 4; } svg .lb { stroke:var(--bnd); stroke-width:2; stroke-dasharray:2 3; }
svg .lm { stroke:var(--mon); stroke-width:2.6; }
"""


def card(x: float, y: float, g: str, d: dict, m: dict, els: dict) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, g, "gid"))
    pill = f"ASIL {d['asil']}"
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
            class_="pr",
        )
    )
    out.append(fk.text(x + CW - 14 - pw / 2, y + 24.5, pill, "prt", "middle"))
    for k, ln in enumerate(fk.wrap(d["statement"], CW - 28, "tb")[:3]):
        out.append(fk.text(x + 14, y + 44 + 16 * k, ln, "tb"))
    out += chart(x + 2, y + 92, GOALS[g]["chart"])
    out += scene(x + 15, y + 214, g)
    yy = y + 354
    by: dict[str, list[str]] = {}
    for f in m["fsrs"]:
        if f["goal"] == g and f["asil"] != "QM":
            by.setdefault(f["element"], []).append(f["id"][4:])
    lines = []
    for e, ids in by.items():
        lines += fk.wrap(f"{e} {els[e]['name']}: FSR-{', '.join(ids)}", CW - 28, "s")
    for k, ln in enumerate(lines[:4]):
        out.append(fk.text(x + 14, yy + 15 * k, ln, "s"))
    yy += 15 * min(len(lines), 4) + 6
    for k, ln in enumerate(fk.wrap("Safe state: " + d["safe_state"], CW - 28, "s")[:4]):
        out.append(fk.text(x + 14, yy + 15 * k, ln, "ax"))
    return out


def sheet(m: dict, sg: dict[str, dict], els: dict) -> str:
    rows = math.ceil(len(sg) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "How the concept holds each safety goal", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-C-04 §4, Figure 4-2: a fault in Autoware or the remote link, the envelope's bound, and what "
            "the safety monitor lets through. Schematic, not simulation results.",
            "t",
        ),
    ]
    for i, (g, d) in enumerate(sg.items()):
        body += card(
            MARGIN + (i % COLS) * (CW + GAP), HEAD + (i // COLS) * (CH + GAP), g, d, m, els
        )
    ly = h - 26
    body += [
        fk.el("line", None, x1=MARGIN, y1=ly - 4, x2=MARGIN + 26, y2=ly - 4, class_="lc"),
        fk.text(MARGIN + 34, ly, "faulty command, where it would lead", "t"),
        fk.el("line", None, x1=MARGIN + 290, y1=ly - 4, x2=MARGIN + 316, y2=ly - 4, class_="lb"),
        fk.text(MARGIN + 324, ly, "envelope bound", "t"),
        fk.el("line", None, x1=MARGIN + 450, y1=ly - 4, x2=MARGIN + 476, y2=ly - 4, class_="lm"),
        fk.text(MARGIN + 484, ly, "what reaches the vehicle, path taken", "t"),
        fk.el("circle", None, cx=MARGIN + 760, cy=ly - 4, r=7, class_="mk"),
        fk.text(MARGIN + 760, ly - 0.5, "M", "mkt", "middle"),
        fk.text(MARGIN + 774, ly, "the monitor steps in", "t"),
    ]
    desc = "How the concept holds each safety goal. " + " ".join(
        f"{g} (ASIL {d['asil']}): {GOALS[g]['act']}; the vehicle is {GOALS[g]['end']}."
        for g, d in sg.items()
    )
    return fk.svg(
        w, h, "WP-C-04 Figure 4-2: how the concept holds each safety goal", desc, body, EXTRA
    )


def check(sg: dict[str, dict]) -> list[str]:
    errs = [f"{g}: no scene in envelope.py" for g in sg if g not in GOALS]
    errs += [f"{g}: scene for a safety goal that does not exist" for g in GOALS if g not in sg]
    return errs
