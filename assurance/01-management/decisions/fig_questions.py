#!/usr/bin/env python3
"""Figures for decision register questions that need a picture to show how the options differ.

    figures/dq-001.svg   ODD reach of each option: top speed against who shares the road
    figures/dq-002.svg   where the command is bounded in each option, along the command path
    figures/dq-034.svg   following distance the monitor keeps against speed, for each option

The option keys and titles drawn are checked against register.yaml, so a figure cannot fall out of
step with its question.

    python3 fig_questions.py            # write the figures
    python3 fig_questions.py --check    # fail if one is stale or disagrees with the register
"""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figures"))
sys.path.insert(0, str(HERE))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402

W = 640
EXTRA = """svg .qm { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; }
svg .safe { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.8; }
svg .plat { fill:none; stroke:var(--ink3); stroke-width:1.2; stroke-dasharray:5 4; }
svg .arrow { stroke:var(--ink3); stroke-width:1.4; fill:none; }
svg .head { fill:var(--ink3); }
svg .reach-a { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.8; }
svg .reach-b { fill:var(--ambsoft); stroke:var(--amb); stroke-width:1.6; }
svg .reach-c { fill:var(--card); stroke:var(--ink3); stroke-width:1.4; }
svg .fa { stroke:var(--acc); stroke-width:2.4; fill:none; }
svg .fb { stroke:var(--amb); stroke-width:2.4; fill:none; stroke-dasharray:7 4; }
svg .fc { stroke:var(--ink3); stroke-width:2.4; fill:none; stroke-dasharray:2 3; }
svg .ka { font:700 13px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); }
"""

# ---------------------------------------------------------------- DQ-001

# (key, top speed km/h, road-user level 1..3)
ODD = [("A", 20, 2), ("B", 50, 3), ("C", 15, 1)]
LEVELS = [
    "Staff only, private site",
    "Pedestrians, cyclists, slow traffic",
    "All public road users",
]
VMAX = 60


def dq001(titles: dict[str, str]) -> str:
    x0, x1, ytop, ybot = 196, W - 28, 74, 314
    lh = (ybot - ytop) / len(LEVELS)
    body = [
        fk.text(24, 32, "How far each ODD option reaches", "h"),
        fk.text(24, 54, "Further right and higher means more hazards and more to validate", "t"),
    ]
    for i, lab in enumerate(LEVELS):
        yc = ybot - lh * i - lh / 2
        for j, ln in enumerate(fk.wrap(lab, x0 - 36, "t")):
            body.append(fk.text(24, yc - 2 + 15 * j, ln, "t"))
        body.append(
            fk.el(
                "line",
                None,
                x1=x0,
                y1=fk.num(ybot - lh * (i + 1)),
                x2=x1,
                y2=fk.num(ybot - lh * (i + 1)),
                class_="hair",
            )
        )
    for v in range(0, VMAX + 1, 10):
        x = x0 + (x1 - x0) * v / VMAX
        body.append(
            fk.el("line", None, x1=fk.num(x), y1=ytop, x2=fk.num(x), y2=ybot, class_="hair")
        )
        body.append(fk.text(x, ybot + 18, str(v), "s", "middle"))
    body.append(fk.text((x0 + x1) / 2, ybot + 38, "Top speed, km/h", "t", "middle"))
    for key, v, lvl in sorted(ODD, key=lambda o: -o[1]):
        w = (x1 - x0) * v / VMAX
        h = lh * lvl - 10
        y = ybot - h
        body.append(
            fk.el(
                "rect",
                None,
                x=x0,
                y=fk.num(y),
                width=fk.num(w),
                height=fk.num(h),
                rx=6,
                class_=f"reach-{key.lower()}",
            )
        )
        body.append(fk.text(x0 + w - 8, y + 18, f"{key}", "ka" if key == "A" else "tb", "end"))
    y = ybot + 64
    for key, v, lvl in ODD:
        line = f"{key}  {titles[key]}: up to {v} km/h; {LEVELS[lvl - 1].lower()}"
        for j, ln in enumerate(fk.wrap(line, W - 48, "t")):
            body.append(fk.text(24, y, ln, "tb" if j == 0 else "t"))
            y += 17
        y += 4
    desc = (
        "Each ODD option of DQ-001 as a region from zero to its top speed and up to the road users it shares the road with. "
        + " ".join(
            f"{k} ({titles[k]}): up to {v} km/h, {LEVELS[lvl - 1].lower()}." for k, v, lvl in ODD
        )
    )
    return fk.svg(W, int(y + 6), "DQ-001: reach of each ODD option", desc, body, EXTRA)


# ---------------------------------------------------------------- DQ-002

# Each option: the chain from planning to actuators, top to bottom. (label, sub, rated, on Autoware computer)
CHAIN = {
    "A": [
        ("Planning, control", "Autoware", False, True),
        ("vehicle_cmd_gate", "limits, mode select", False, True),
        ("Safety monitor", "own hardware, can stop alone", True, False),
        ("Drive-by-wire", "", False, False),
    ],
    "B": [
        ("Planning, control", "Autoware", False, True),
        ("vehicle_cmd_gate", "+ mrm_handler, rated", True, True),
        ("Drive-by-wire", "", False, False),
    ],
    "C": [
        ("Planning, control", "Autoware", False, True),
        ("vehicle_cmd_gate", "limits, mode select", False, True),
        ("Drive-by-wire", "own limits, watchdog stop", True, False),
    ],
}


def dq002(titles: dict[str, str]) -> str:
    cw, gap, top = 184, 10, 112
    bh, step = 50, 72
    body = [
        fk.text(24, 32, "Where the command is bounded", "h"),
        fk.text(24, 54, "Blue: rated for safety. Dashed: runs on the Autoware computer", "t"),
        fk.text(24, 72, "(Linux, ROS 2), where one platform fault hits everything inside.", "t"),
    ]
    bottom = 0
    for i, key in enumerate("ABC"):
        x = 24 + i * (cw + gap)
        body.append(fk.text(x + cw / 2, top - 12, f"{key}", "ka" if key == "A" else "tb", "middle"))
        chain = CHAIN[key]
        on = [n for n, c in enumerate(chain) if c[3]]
        if on:
            y0 = top + on[0] * step - 8
            y1 = top + on[-1] * step + bh + 8
            body.append(
                fk.el(
                    "rect", None, x=x - 2, y=y0, width=cw + 4, height=y1 - y0, rx=10, class_="plat"
                )
            )
        for n, (label, sub, rated, _) in enumerate(chain):
            y = top + n * step
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=x + 8,
                    y=y,
                    width=cw - 16,
                    height=bh,
                    rx=7,
                    class_="safe" if rated else "qm",
                )
            )
            body.append(fk.text(x + cw / 2, y + (20 if sub else 30), label, "tb", "middle"))
            if sub:
                body.append(fk.text(x + cw / 2, y + 37, fk.fit(sub, cw - 24, "s"), "s", "middle"))
            if n + 1 < len(chain):
                ya, yb = y + bh, y + step
                body.append(
                    fk.el(
                        "line",
                        None,
                        x1=fk.num(x + cw / 2),
                        y1=ya + 2,
                        x2=fk.num(x + cw / 2),
                        y2=yb - 7,
                        class_="arrow",
                    )
                )
                cx = x + cw / 2
                body.append(
                    fk.el(
                        "path",
                        None,
                        d=f"M{fk.num(cx - 4)} {yb - 8} L{fk.num(cx + 4)} {yb - 8} L{fk.num(cx)} {yb - 2} Z",
                        class_="head",
                    )
                )
            bottom = max(bottom, y + bh)
        lines = fk.wrap(titles[key], cw - 8, "t")
        for j, ln in enumerate(lines):
            body.append(fk.text(x + cw / 2, top + 4 * step + 2 + 16 * j, ln, "t", "middle"))
    h = top + 4 * step + 2 + 16 * 3 + 8
    desc = (
        "The command path of each option of DQ-002, from planning and control down to the drive-by-wire system. "
        + " ".join(
            f"{k} ({titles[k]}): "
            + " then ".join(
                f"{c[0]}{' (rated for safety)' if c[2] else ''}{' on the Autoware computer' if c[3] else ''}"
                for c in CHAIN[k]
            )
            + "."
            for k in "ABC"
        )
    )
    return fk.svg(W, int(h), "DQ-002: where the command is bounded", desc, body, EXTRA)


# ---------------------------------------------------------------- DQ-034

# Safe following distance behind a vehicle at the same speed v: d = v t + v² / (2 b) - v² / (2 B) + m,
# with our response time t, our guaranteed braking b, the vehicle ahead's braking B and the margin m
# of SG-01 (WP-S-04). The values are the question's assumptions, not measurements.
RESPONSE, OWN, MARGIN = 0.5, 4.0, 0.5
AHEAD = {"A": 8.0, "B": 6.0, "C": 4.0}
FMAX = 50


def follow(v_kmh: float, ahead: float) -> float:
    v = v_kmh / 3.6
    return v * RESPONSE + v * v / (2 * OWN) - v * v / (2 * ahead) + MARGIN


def dq034(titles: dict[str, str]) -> str:
    x0, x1, y0, y1 = 70, 500, 84, 324
    dmax = 25
    X = lambda v: x0 + (x1 - x0) * v / FMAX  # noqa: E731
    Y = lambda d: y1 - (y1 - y0) * d / dmax  # noqa: E731
    body = [
        fk.text(24, 32, "How far back the monitor keeps the vehicle", "h"),
        fk.text(
            24, 54, "Following distance behind a vehicle at the same speed, for each option", "t"
        ),
    ]
    for d in range(0, dmax + 1, 5):
        body.append(
            fk.el("path", None, d=f"M{x0} {fk.num(Y(d))} L{x1} {fk.num(Y(d))}", class_="hair")
        )
        body.append(fk.text(x0 - 8, Y(d) + 4, f"{d} m", "s", "end"))
    for v in range(0, FMAX + 1, 10):
        body.append(fk.text(X(v), y1 + 18, str(v), "s", "middle"))
    body.append(fk.text((x0 + x1) / 2, y1 + 38, "Speed, km/h", "t", "middle"))
    for key, cls in zip(AHEAD, ("fa", "fb", "fc")):
        pts = [(X(v), Y(follow(v, AHEAD[key]))) for v in range(0, FMAX + 1, 2)]
        body.append(
            fk.el(
                "path",
                None,
                d="M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in pts),
                class_=cls,
            )
        )
        x, y = pts[-1]
        body.append(
            fk.text(
                x + 8,
                y + 4,
                f"{key}  {follow(FMAX, AHEAD[key]):.1f} m",
                "ka" if key == "A" else "tb",
            )
        )
    y = y1 + 66
    for key in AHEAD:
        line = f"{key}  {titles[key]} ({AHEAD[key]:g} m/s²)"
        for j, ln in enumerate(fk.wrap(line, W - 48, "t")):
            body.append(fk.text(24, y, ln, "tb" if j == 0 else "t"))
            y += 17
        y += 4
    body.append(
        fk.text(
            24,
            y + 4,
            f"Assumes a {RESPONSE:g} s response, {OWN:g} m/s² of our own braking and a {MARGIN:g} m margin.",
            "s",
        )
    )
    y += 20
    desc = (
        "Following distance the safety monitor keeps behind a vehicle at the same speed, from 0 to "
        f"{FMAX} km/h, for each option of DQ-034. "
        + " ".join(
            f"{k} ({titles[k]}): vehicle ahead braking at {AHEAD[k]:g} m/s², {follow(FMAX, AHEAD[k]):.1f} m at {FMAX} km/h."
            for k in AHEAD
        )
        + f" Assumes a {RESPONSE:g} s response, {OWN:g} m/s² of own braking and a {MARGIN:g} m margin."
    )
    return fk.svg(W, int(y + 6), "DQ-034: following distance for each option", desc, body, EXTRA)


FIGURES = {
    "DQ-001": ("figures/dq-001.svg", dq001, [k for k, _, _ in ODD]),
    "DQ-002": ("figures/dq-002.svg", dq002, list(CHAIN)),
    "DQ-034": ("figures/dq-034.svg", dq034, list(AHEAD)),
}


def build() -> dict[Path, str]:
    entries = {d["id"]: d for d in check_decisions.load()}
    out = {}
    for qid, (rel, draw, keys) in FIGURES.items():
        d = entries.get(qid)
        if d is None:
            raise fk.FigureError(f"{qid} is not in register.yaml")
        titles = {o["key"]: o["title"] for o in d["options"]}
        if sorted(titles) != sorted(keys):
            raise fk.FigureError(
                f"{qid}: the figure draws options {keys}, the register has {sorted(titles)}"
            )
        if d.get("figure") != rel:
            raise fk.FigureError(
                f"{qid}: register figure is {d.get('figure')!r}, this script writes {rel}"
            )
        out[HERE / rel] = draw(titles)
    return out


if __name__ == "__main__":
    fk.run(build, __doc__)
