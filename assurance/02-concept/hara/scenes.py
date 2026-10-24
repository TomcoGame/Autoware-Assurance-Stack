"""Guide-word scene sheets for WP-C-03 §6.1: one card per safety-related guide word of a function.

hara.py calls `sheets()` and writes one sheet per function with safety-related guide words, next to the HARA files
(`fig-c03-6-4-<function>-scenes.svg`). Each card shows what the function must deliver over time (required, dashed green)
against what the malfunction delivers (performed, red), and under it a top-down scene of the hazard it leads to: the
intended path and stop, the path the vehicle takes, where the deviation starts and the moment it matters. A card for a
pair folded into another names the pair it is rated as.

The chart is the guide word's pattern and is the same for every function; the scene is the hazard's and starts to
deviate when the chart does. Both are schematic: they explain each hazardous event and are not simulation results.
Each card loops (SMIL, no script, 6 s); a viewer that does not animate shows the last frame.
"""

from __future__ import annotations

import math

import figkit as fk

CW, CH = 330, 372  # card
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 84
LOOP, DRIVE = 6, 0.75  # loop length in s, and the share of it the vehicles move

STEP, LINE = "step", "line"
REQ = (STEP, [(0, 0), (20, 0), (20, 70), (100, 70)])

# Guide word: (required, performed). Time and output run 0 to 100; output can be negative (M12).
PATTERNS = {
    "M01": (REQ, (STEP, [(0, 0), (100, 0)])),
    "M02": (REQ, (STEP, [(0, 0), (20, 0), (20, 70), (55, 70), (55, 0), (100, 0)])),
    "M03": (
        (STEP, [(0, 0), (100, 0)]),
        (STEP, [(0, 0), (30, 0), (30, 70), (65, 70), (65, 0), (100, 0)]),
    ),
    "M04": (
        (STEP, [(0, 0), (15, 0), (15, 70), (45, 70), (45, 20), (100, 20)]),
        (STEP, [(0, 0), (15, 0), (15, 70), (100, 70)]),
    ),
    "M05": (REQ, (STEP, [(0, 0), (20, 0), (20, 96), (100, 96)])),
    "M06": (REQ, (STEP, [(0, 0), (20, 0), (20, 35), (100, 35)])),
    "M07": (
        (STEP, [(0, 0), (45, 0), (45, 70), (100, 70)]),
        (STEP, [(0, 0), (20, 0), (20, 70), (100, 70)]),
    ),
    "M08": (REQ, (STEP, [(0, 0), (50, 0), (50, 70), (100, 70)])),
    "M09": (
        (STEP, [(0, 0), (20, 0), (20, 70), (80, 70), (80, 0), (100, 0)]),
        (STEP, [(0, 0), (20, 0), (20, 70), (45, 70), (45, 0), (100, 0)]),
    ),
    "M10": (
        (STEP, [(0, 0), (20, 0), (20, 70), (55, 70), (55, 0), (100, 0)]),
        (STEP, [(0, 0), (20, 0), (20, 70), (90, 70), (90, 0), (100, 0)]),
    ),
    "M11": (
        REQ,
        (LINE, [(0, 0), (40, 0), (48, 26), (56, 44), (64, 56), (72, 63), (82, 68), (100, 70)]),
    ),
    "M12": (
        (STEP, [(0, 0), (20, 0), (20, 60), (100, 60)]),
        (STEP, [(0, 0), (20, 0), (20, -60), (100, -60)]),
    ),
    "M13": (
        REQ,
        (
            STEP,
            [(0, 0), (20, 0), (20, 70), (28, 92), (35, 30), (43, 86), (51, 18), (59, 80)]
            + [(67, 40), (75, 95), (83, 25), (91, 78), (100, 78)],
        ),
    ),
    "M14": (
        REQ,
        (
            STEP,
            [(0, 0), (20, 0), (20, 50), (38, 50), (38, 88), (56, 88), (56, 40), (74, 40), (74, 92)]
            + [(100, 92)],
        ),
    ),
}


def value(pattern: tuple, t: float) -> float:
    kind, pts = pattern
    if kind == STEP:
        return [f for tp, f in pts if tp <= t][-1]
    for (t0, f0), (t1, f1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return f0 + (f1 - f0) * (t - t0) / ((t1 - t0) or 1)
    return pts[-1][1]


def onset(gw: str) -> float:
    """First time the performed output leaves the required one."""
    req, perf = PATTERNS[gw]
    return next(t / 2 for t in range(201) if abs(value(req, t / 2) - value(perf, t / 2)) > 1)


# ---------------------------------------------------------------- chart, 300 x 104 at (ox, oy)

PX0, PX1, PY0, PY1 = 34, 292, 10, 84


def chart(ox: float, oy: float, gw: str, output: str) -> list[str]:
    req, perf = PATTERNS[gw]
    signed = any(f < 0 for _, pts in (req, perf) for _, f in pts)
    zero = (PY0 + PY1) / 2 if signed else PY1 - 2

    def xy(t: float, f: float) -> tuple[float, float]:
        span = (PY1 - PY0) / (2 if signed else 1)
        return ox + PX0 + t / 100 * (PX1 - PX0), oy + zero - f / 100 * span

    def d(pattern: tuple) -> str:
        kind, pts = pattern
        out = [xy(*pts[0])]
        for (_, fp), (t, f) in zip(pts, pts[1:]):
            if kind == STEP and f != fp:
                out.append(xy(t, fp))
            out.append(xy(t, f))
        return "M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in out)

    x0, x1 = ox + PX0, ox + PX1
    body = [
        fk.el(
            "rect", None, x=x0, y=oy + PY0 - 4, width=PX1 - PX0, height=PY1 - PY0 + 6, class_="plot"
        ),
        fk.el("line", None, x1=x0, y1=oy + zero, x2=x1, y2=oy + zero, class_="axis"),
        fk.text(x0, oy + PY1 + 14, "↑ " + fk.fit(output, 170, "s"), "ax"),
        fk.text(x1, oy + PY1 + 14, "time →", "ax", "end"),
        fk.el("path", None, d=d(req), class_="req"),
        fk.el("path", None, d=d(perf), class_="perf", pathLength=1),
    ]
    t0 = onset(gw)
    cx, _ = xy(t0, 0)
    body.append(
        fk.el(
            "line",
            None,
            x1=fk.num(cx),
            y1=oy + PY0 - 4,
            x2=fk.num(cx),
            y2=oy + PY1 + 2,
            class_="on",
        )
    )
    body.append(cursor(x0, x1, oy + PY0 - 4, oy + PY1 + 2))
    return body


def cursor(x0: float, x1: float, y0: float, y1: float) -> str:
    move = fk.el(
        "animateTransform",
        None,
        attributeName="transform",
        type="translate",
        values=f"{fk.num(x0 - x1)} 0;0 0;0 0",
        keyTimes=f"0;{DRIVE};1",
        dur=f"{LOOP}s",
        repeatCount="indefinite",
    )
    return (
        f'<g><line x1="{fk.num(x1)}" y1="{fk.num(y0)}" x2="{fk.num(x1)}" y2="{fk.num(y1)}" '
        f'class="cur"/>{move}</g>'
    )


# ---------------------------------------------------------------- scene, 300 x 120 at (ox, oy)

SW, SH = 300, 120
UP, DN, MID, KERB_T, KERB_B = 46, 78, 62, 30, 94  # lane centres (oncoming, ego), centre line, kerbs


def road(
    ox: float, oy: float, junction: tuple[float, float] | None = None, side: bool = False
) -> list[str]:
    out = [
        fk.el("rect", None, x=ox, y=oy, width=SW, height=SH, rx=6, class_="verge"),
        fk.el("rect", None, x=ox, y=oy + KERB_T, width=SW, height=KERB_B - KERB_T, class_="road"),
    ]
    if junction:
        a, b = junction
        out.append(fk.el("rect", None, x=ox + a, y=oy, width=b - a, height=SH, class_="road"))
    if side:
        out.append(
            fk.el(
                "rect",
                None,
                x=ox + 200,
                y=oy + KERB_B - 1,
                width=34,
                height=SH - KERB_B + 1,
                class_="road",
            )
        )
    out.append(fk.el("line", None, x1=ox, y1=oy + MID, x2=ox + SW, y2=oy + MID, class_="lane"))
    for y in (KERB_T, KERB_B):
        out.append(fk.el("line", None, x1=ox, y1=oy + y, x2=ox + SW, y2=oy + y, class_="kerb"))
    return out


def car(x: float, y: float, cls: str, vertical: bool = False, anim: str = "") -> str:
    w, h = (13, 24) if vertical else (24, 13)
    body = fk.el(
        "rect", None, x=fk.num(x - w / 2), y=fk.num(y - h / 2), width=w, height=h, rx=3, class_=cls
    )
    if cls in ("ego", "ghost") and not vertical:
        body += fk.el(
            "rect",
            None,
            x=fk.num(x + 4),
            y=fk.num(y - 4.5),
            width=4,
            height=9,
            rx=1,
            class_=cls + "w",
        )
    return f"<g>{body}{anim}</g>"


def person(x: float, y: float) -> str:
    return fk.el("circle", None, cx=fk.num(x), cy=fk.num(y), r=4.2, class_="ped")


def crosswalk(ox: float, oy: float, a: float, b: float) -> list[str]:
    return [
        fk.el(
            "rect", None, x=fk.num(ox + a), y=fk.num(oy + y), width=b - a, height=4, class_="zebra"
        )
        for y in range(KERB_T + 3, KERB_B - 3, 8)
    ]


def stopline(ox: float, oy: float, x: float) -> str:
    return fk.el(
        "line", None, x1=ox + x, y1=oy + MID + 1, x2=ox + x, y2=oy + KERB_B - 1, class_="stop"
    )


def along(pts: list[tuple[float, float]], u: float) -> tuple[float, float]:
    """The point a share `u` of the way along a polyline."""
    segs = [math.dist(p, q) for p, q in zip(pts, pts[1:])]
    total = sum(segs) or 1
    left = u * total
    for (p, q), s in zip(zip(pts, pts[1:]), segs):
        if left <= s and s:
            return p[0] + (q[0] - p[0]) * left / s, p[1] + (q[1] - p[1]) * left / s
        left -= s
    return pts[-1]


def drift(x0: float, y0: float, x_on: float, y1: float, x_end: float, weave: bool = False) -> list:
    pts = []
    for i in range(41):
        x = x0 + (x_end - x0) * i / 40
        if x <= x_on:
            y = y0
        elif weave:
            y = y0 + 13 * math.sin((x - x_on) / 12) * min(1, (x - x_on) / 30)
        else:
            k = min(1, (x - x_on) / 90)
            y = y0 + (y1 - y0) * (1 - math.cos(math.pi * k)) / 2
        pts.append((x, y))
    return pts


EXTRA_SIGNAL = {"M03", "M04", "M05", "M10", "M13", "M14"}  # a signal is shown that should not be


def scene(hz: str, gw: str) -> dict:
    """Decor, intended and actual paths in scene units, the callout and the vehicle's look."""
    u = onset(gw) / 100
    s: dict = {"decor": [], "ghost_vertical": False, "blink": None}
    if hz == "H-01":
        s["others"] = [(240, DN)]
        s["intended"], s["actual"] = [(22, DN), (196, DN)], [(22, DN), (216, DN)]
        s["call"] = ((228, DN), "closes on the car ahead")
    elif hz == "H-02":
        s["zebra"], s["stop"], s["people"] = (206, 230), 199, [(218, 72)]
        s["intended"], s["actual"] = [(22, DN), (184, DN)], [(22, DN), (204, DN)]
        s["call"] = ((218, 72), "into the crosswalk")
    elif hz == "H-03":
        stop = 120 + 80 * u
        s["intended"], s["actual"] = [(80, DN), (282, DN)], [(80, DN), (stop, DN)]
        s["follow"] = [(30, DN), (stop - 27, DN)]
        s["call"] = ((stop - 14, DN), "the car behind runs in")
    elif hz == "H-04":
        x_on = 22 + 200 * u
        if gw == "M12":
            act, label = drift(22, DN, x_on, KERB_B + 12, 268), "off the road"
        elif gw == "M13":
            act, label = drift(22, DN, x_on, DN, 268, weave=True), "weaves out of its lane"
        else:
            act, label = drift(22, DN, x_on, UP, 268), "into the oncoming lane"
        s["intended"], s["actual"] = [(22, DN), (268, DN)], act
        hit = next(((x, y) for x, y in act if abs(y - DN) > 14), act[-1])
        s["others"] = [(min(hit[0] + 26, 282), UP)] if gw not in ("M12",) else []
        s["call"] = (hit, label)
    elif hz == "H-05":
        s["zebra"], s["stop"], s["people"] = (196, 220), 189, [(208, 74)]
        s["intended"], s["actual"] = [(172, DN)], [(172, DN), (194, DN)]
        s["call"] = ((208, 74), "moves off into the crosswalk")
    elif hz == "H-06":
        s["junction"], s["stop"] = (204, 252), 196
        s["others_v"] = [(228, UP + 2)]
        s["intended"], s["actual"] = [(22, DN), (180, DN)], [(22, DN), (276, DN)]
        s["call"] = ((228, DN), "enters against the right of way")
    elif hz == "H-07":
        x_on = 40 + 120 * u
        s["intended"] = [(22, DN), (x_on, DN)] + [
            (x_on + 90 * k / 10, DN + 9 * (1 - math.cos(math.pi * k / 10)) / 2)
            for k in range(1, 11)
        ]
        s["actual"] = [(22, DN), (282, DN)]
        s["call"] = ((min(x_on + 130, 270), DN), "drives on with no safe stop")
    elif hz == "H-08":
        s["others"], s["remote"] = [(250, DN)], True
        s["intended"], s["actual"] = [(22, DN), (208, DN)], [(22, DN), (233, DN)]
        s["call"] = ((238, DN), "keeps to the stale command")
    elif hz == "H-09":
        s["side"] = True
        turn = [(22, DN), (183, DN)] + [
            (
                183 + 34 * math.sin(math.pi / 2 * k / 8),
                DN + 34 * (1 - math.cos(math.pi / 2 * k / 8)),
            )
            for k in range(1, 9)
        ]
        straight = [(22, DN), (282, DN)]
        s["intended"], s["bikes"] = turn, [(176, 89)]
        if gw == "M12":
            s["actual"], s["blink"] = turn, ("left", "turns right, signals left")
            s["call"] = ((176, 89), "the cyclist reads the wrong side")
        elif gw in EXTRA_SIGNAL:
            s["intended"] = straight
            s["actual"], s["blink"] = straight, ("right", "signals right, goes straight on")
            s["call"] = ((176, 89), "others yield for no turn")
        else:
            s["actual"], s["blink"] = turn, ("", "turns right with no signal")
            s["call"] = ((176, 89), "the cyclist is not warned")
    elif hz == "H-10":
        s["people"] = [(118, DN)]
        s["intended"], s["actual"] = [(172, DN)], [(172, DN), (138, DN)]
        s["call"] = ((122, DN), "rolls back toward the person behind")
    else:
        raise fk.FigureError(f"no scene for {hz}")
    return s


def poly(ox: float, oy: float, pts: list) -> str:
    return "M" + " L".join(f"{fk.num(ox + x)} {fk.num(oy + y)}" for x, y in pts)


def motion(ox: float, oy: float, pts: list) -> str:
    """Translate from the start of `pts` to its end over the drive, then hold; the static frame is the end."""
    ex, ey = pts[-1]
    vals = [along(pts, k / 12) for k in range(13)] if len(pts) > 1 else [pts[0]]
    keys = [DRIVE * k / 12 for k in range(13)] if len(pts) > 1 else [0]
    vals.append(pts[-1])
    keys.append(1)
    return fk.el(
        "animateTransform",
        None,
        attributeName="transform",
        type="translate",
        values=";".join(f"{fk.num(x - ex)} {fk.num(y - ey)}" for x, y in vals),
        keyTimes=";".join(fk.num(k) if k not in (0, 1) else str(k) for k in keys),
        dur=f"{LOOP}s",
        repeatCount="indefinite",
    )


def appear(at: float) -> str:
    return fk.el(
        "animate",
        None,
        attributeName="opacity",
        values="0;0;1;1",
        keyTimes=f"0;{fk.num(at)};{fk.num(min(at + 0.02, 1))};1",
        dur=f"{LOOP}s",
        repeatCount="indefinite",
    )


def draw_on() -> str:
    return fk.el(
        "animate",
        None,
        attributeName="stroke-dashoffset",
        values="1;0;0",
        keyTimes=f"0;{DRIVE};1",
        dur=f"{LOOP}s",
        repeatCount="indefinite",
    )


def blink() -> str:
    return fk.el(
        "animate",
        None,
        attributeName="opacity",
        values="1;0.15;1",
        dur="0.8s",
        repeatCount="indefinite",
    )


def blinkers(x: float, y: float, side: str, cls: str) -> str:
    dy = 7 if side == "right" else -7
    return "".join(
        fk.el("circle", None, cx=fk.num(x + dx), cy=fk.num(y + dy), r=3, class_=cls)
        for dx in (-10, 10)
    )


def draw_scene(ox: float, oy: float, hz: str, gw: str) -> list[str]:
    s = scene(hz, gw)
    u = onset(gw) / 100
    out = road(ox, oy, s.get("junction"), s.get("side", False))
    if "zebra" in s:
        out += crosswalk(ox, oy, *s["zebra"])
    if "stop" in s:
        out.append(stopline(ox, oy, s["stop"]))
    for x, y in s.get("others", []):
        out.append(car(ox + x, oy + y, "oth"))
    for x, y in s.get("others_v", []):
        out.append(car(ox + x, oy + y, "oth", vertical=True))
    for x, y in s.get("people", []):
        out.append(person(ox + x, oy + y))
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
            fk.text(ox + 36, oy + 19, "remote operator: stop", "ax"),
        ]
    if "follow" in s:
        f = s["follow"]
        out.append(car(ox + f[-1][0], oy + f[-1][1], "oth", anim=motion(ox, oy, f)))
    it, ac = s["intended"], s["actual"]
    if len(it) > 1:
        out.append(fk.el("path", None, d=poly(ox, oy, it), class_="ipath"))
    if len(ac) > 1:
        out.append(f'<path d="{poly(ox, oy, ac)}" class="apath" pathLength="1">{draw_on()}</path>')
    if s["blink"]:
        side, what = s["blink"]
        out.append(car(ox + 130, oy + DN, "ego"))
        if side:
            out.append(f"<g>{blinkers(ox + 130, oy + DN, side, 'bl-bad')}{blink()}</g>")
        out.append(fk.text(ox + 8, oy + 18, what, "ax"))
    else:
        gx, gy = it[-1]
        out.append(car(ox + gx, oy + gy, "ghost", anim=motion(ox, oy, it)))
        ex, ey = ac[-1]
        out.append(car(ox + ex, oy + ey, "ego", anim=motion(ox, oy, ac)))
    t_on = DRIVE * u if len(ac) > 1 and hz not in ("H-05", "H-10") else 0.05
    fx, fy = {"H-05": ac[0], "H-10": ac[0], "H-09": (130, DN)}.get(hz) or along(ac, u)
    out.append(
        f'<g opacity="1">{fk.el("circle", None, cx=fk.num(ox + fx), cy=fk.num(oy + fy - 14), r=6.5, class_="fault")}'
        f'{fk.text(ox + fx, oy + fy - 10.5, "!", "fx", "middle")}{appear(t_on)}</g>'
    )
    (cx, cy), label = s["call"]
    lw = fk.width(label, "s") + 14
    lx = min(max(ox + cx - lw / 2, ox + 4), ox + SW - lw - 4)
    ly = oy + (cy + 22 if cy < 70 else cy - 40)
    ly = min(ly, oy + SH - 20)
    out.append(
        f"<g>{fk.el('circle', None, cx=fk.num(ox + cx), cy=fk.num(oy + cy), r=12, class_='ring')}"
        f"{fk.el('rect', None, x=fk.num(lx), y=fk.num(ly), width=fk.num(lw), height=18, rx=9, class_='callout')}"
        f"{fk.text(lx + lw / 2, ly + 13, label, 'ct', 'middle')}{appear(DRIVE * 0.98)}</g>"
    )
    return out


# ---------------------------------------------------------------- sheet

EXTRA = """svg { --req:#23875a; --perf:#c2412b; --road:#e9ebee; --verge:#f7f8f9; --lane:#ffffff; --zeb:#ffffff;
 --ego:#c2412b; --oth:#9aa1ab; --amber:#e39b00; --a3:#d4644a; --a1:#f5dcd3; --t1:#3b140b; }
@media (prefers-color-scheme: dark) { svg { --req:#45b882; --perf:#ff7a63; --road:#2b2f36; --verge:#1b1e22;
 --lane:#7f8792; --zeb:#c9ced6; --ego:#ff7a63; --oth:#6f7782; --amber:#f2b84b; --a3:#bb4f34; --a1:#4a2820; --t1:#f6e3dd; } }
svg .plot { fill:var(--bg); stroke:var(--grid); stroke-width:1; }
svg .axis { stroke:var(--ink3); stroke-width:1; }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .req { fill:none; stroke:var(--req); stroke-width:2; stroke-dasharray:5 4; }
svg .perf { fill:none; stroke:var(--perf); stroke-width:2.4; stroke-linejoin:round; }
svg .on { stroke:var(--perf); stroke-width:1; stroke-dasharray:2 3; }
svg .cur { stroke:var(--ink2); stroke-width:1; opacity:.55; }
svg .verge { fill:var(--verge); stroke:var(--grid); stroke-width:1; }
svg .road { fill:var(--road); }
svg .lane { stroke:var(--lane); stroke-width:1.5; stroke-dasharray:8 7; }
svg .kerb { stroke:var(--ink3); stroke-width:1.2; }
svg .zebra { fill:var(--zeb); }
svg .stop { stroke:var(--zeb); stroke-width:3; }
svg .oth { fill:var(--oth); }
svg .ego { fill:var(--ego); } svg .egow { fill:var(--bg); opacity:.75; }
svg .ghost { fill:none; stroke:var(--req); stroke-width:1.4; stroke-dasharray:3 2; } svg .ghostw { fill:none; }
svg .ped { fill:var(--ink); }
svg .bike { fill:var(--ink2); }
svg .mast { fill:none; stroke:var(--ink2); stroke-width:1.6; }
svg .ipath { fill:none; stroke:var(--req); stroke-width:2; stroke-dasharray:5 4; }
svg .apath { fill:none; stroke:var(--perf); stroke-width:2.6; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:1 1; }
svg .fault { fill:var(--perf); }
svg .fx { font:700 10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .ring { fill:none; stroke:var(--perf); stroke-width:1.6; }
svg .callout { fill:var(--perf); }
svg .ct { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .bl-bad { fill:var(--amber); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .pr { fill:var(--a3); } svg .pf { fill:var(--a1); }
svg .prt { font:600 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:#ffffff; }
svg .pft { font:600 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--t1); }
svg .lr { stroke:var(--req); stroke-width:2; stroke-dasharray:5 4; } svg .lp { stroke:var(--perf); stroke-width:2.4; }
"""


def card(
    x: float, y: float, f: dict, gw: str, c: list, names: dict, worst: dict, goal_of: dict
) -> list[str]:
    _, hz, into, why = c
    rated = into or gw
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, gw, "gid"))
    out.append(fk.text(x + 48, y + 24, fk.fit(names[gw]["name"], 150, "tb"), "tb"))
    out.append(fk.text(x + 14, y + 41, fk.fit(names[gw]["means"], CW - 28, "s"), "s"))
    pill = f"{hz} · ASIL {worst.get((f['id'], rated), '—')}" if not into else f"rated as {into}"
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
            class_="pf" if into else "pr",
        )
    )
    out.append(fk.text(x + CW - 14 - pw / 2, y + 24.5, pill, "pft" if into else "prt", "middle"))
    out += chart(x + 2, y + 50, gw, f["output"])
    out += draw_scene(x + 15, y + 172, hz, gw)
    for k, ln in enumerate(fk.wrap(why, CW - 28, "s")[:3]):
        out.append(fk.text(x + 14, y + 311 + 15 * k, ln, "s"))
    goal = goal_of.get(hz, "—")
    out.append(
        fk.text(
            x + 14, y + CH - 12, fk.fit(f"{goal} · {hz} {names['_hz'][hz]}", CW - 28, "s"), "ax"
        )
    )
    return out


def sheet(f: dict, a: dict, names: dict, worst: dict, goal_of: dict) -> str:
    sc = [(g, c) for g, c in f["class"].items() if c[0] == "SC"]
    rows = math.ceil(len(sc) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    rated = sum(1 for _, c in sc if not c[2])
    body = [
        fk.text(
            MARGIN,
            34,
            fk.fit(f"{f['id']} {f['name']}: what each malfunction does", w - 2 * MARGIN, "h"),
            "h",
        ),
        fk.text(
            MARGIN,
            56,
            f"WP-C-03 §6.1, Figure 6-4 ({f['id']}): the {len(sc)} safety-related guide words, {rated} rated and "
            f"{len(sc) - rated} folded into another. Schematic, not simulation results.",
            "t",
        ),
    ]
    for i, (g, c) in enumerate(sc):
        body += card(
            MARGIN + (i % COLS) * (CW + GAP),
            HEAD + (i // COLS) * (CH + GAP),
            f,
            g,
            c,
            names,
            worst,
            goal_of,
        )
    ly = h - 26
    body += [
        fk.el("line", None, x1=MARGIN, y1=ly - 4, x2=MARGIN + 26, y2=ly - 4, class_="lr"),
        fk.text(MARGIN + 34, ly, "required output, intended path", "t"),
        fk.el("line", None, x1=MARGIN + 270, y1=ly - 4, x2=MARGIN + 296, y2=ly - 4, class_="lp"),
        fk.text(MARGIN + 304, ly, "performed output, path taken", "t"),
        fk.el("circle", None, cx=MARGIN + 530, cy=ly - 4, r=6.5, class_="fault"),
        fk.text(MARGIN + 530, ly - 0.5, "!", "fx", "middle"),
        fk.text(MARGIN + 544, ly, "where the deviation starts", "t"),
        fk.el("circle", None, cx=MARGIN + 760, cy=ly - 4, r=8, class_="ring"),
        fk.text(MARGIN + 776, ly, "the moment it matters", "t"),
    ]
    desc = f"Guide-word scenes for {f['id']} {f['name']}. " + " ".join(
        f"{g} {a['guidewords'][g]['name']}: {c[3]} ({c[1]}{', rated as ' + c[2] if c[2] else ''})."
        for g, c in sc
    )
    return fk.svg(w, h, f"{f['id']} guide-word scenes", desc, body, EXTRA)


def sheets(a: dict, hazards: dict[str, str], worst: dict, goal_of: dict) -> list[tuple[dict, str]]:
    """(function, svg) for every function with safety-related guide words, in order."""
    names = dict(a["guidewords"])
    names["_hz"] = hazards
    return [
        (f, sheet(f, a, names, worst, goal_of))
        for f in a["functions"]
        if any(c[0] == "SC" for c in f["class"].values())
    ]


def check(a: dict, hazards: set[str]) -> list[str]:
    errs = [f"{g}: no chart pattern" for g in a["guidewords"] if g not in PATTERNS]
    for f in a["functions"]:
        if not f.get("output"):
            errs.append(f"{f['id']}: needs an output, the axis of its scenes")
        for g, c in f["class"].items():
            if c[0] == "SC":
                try:
                    scene(c[1], g)
                except fk.FigureError as e:
                    errs.append(f"{f['id']}/{g}: {e}")
    return errs
