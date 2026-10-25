"""Scenario sheet for WP-V-03: one card per known scenario, showing what it sets up and when it passes.

scenarios.py calls `sheet()` with the scenarios already worked out and writes Figure 2-1 next to the scenario files.
Each card has a top-down sketch of the logical scenario in the style of the HARA scenes (../../02-concept/hara/
scenes.py): the vehicle in blue, the road user or condition the scenario is about in amber, the others grey, and the
behaviour the pass criterion asks for as a dashed green path with its moment ringed. Under it: what the scenario
exercises, the safety goals at stake, the ODD attributes it varies (outlined red where it sweeps across the ODD
boundary) and the behaviour bounds not yet fixed, its methods, its pass criterion and the verification cases that run
it.

The sketch is one concrete instance of a logical scenario, chosen to explain it; the ranges are in WP-V-03 §2.2.
No scenario has been run, and nothing here is a result. Each card loops (SMIL, no script, 6 s); a viewer that does
not animate shows the last frame.
"""

from __future__ import annotations

import math

import figkit as fk
import scenes as kit

CW = 330
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
SW, SH, UP, DN, MID, KERB_B = kit.SW, kit.SH, kit.UP, kit.DN, kit.MID, kit.KERB_B
JUNCTION = (204, 252)
CHIP_H = 16

# Turns in scene units: right into the side street, left across the oncoming lane.
RIGHT = [(22, DN), (183, DN)] + [
    (183 + 34 * math.sin(math.pi / 2 * k / 8), DN + 34 * (1 - math.cos(math.pi / 2 * k / 8)))
    for k in range(1, 9)
]
LEFT = [(22, DN), (196, DN), (214, 75), (230, 64), (238, 48), (240, 30), (240, 4)]
CIRCLE = [
    (228 + 27 * math.cos(math.radians(a)), MID + 27 * math.sin(math.radians(a)))
    for a in range(-90, -271, -15)
]
CONES = [(176, 87), (192, 83), (208, 79), (224, 75), (240, 71), (256, 69), (272, 69), (288, 69)]

# One sketch per scenario. `ego` is the path the pass criterion asks of the vehicle (one point: it stays put);
# `shown` the path drawn when it goes on past where the vehicle is shown; `plan` a path it must not simply follow;
# `movers` and `still` the other road users, (kind, path or point, key); `decor` the rest of the scene; `call` the
# moment the pass criterion is judged and what must hold there, its label in the top verge unless `at_y` moves it.
SCENES: dict[str, dict] = {
    "SC-01": {
        "zebra": (206, 230),
        "stop": 199,
        "movers": [("ped", [(218, 20), (218, 70)], True)],
        "ego": [(22, DN), (186, DN)],
        "call": ((186, DN), "yields before the crosswalk"),
    },
    "SC-02": {
        "still": [("car", (196, 104), False)],
        "movers": [("ped", [(216, 114), (216, 74)], True)],
        "ego": [(22, DN), (166, DN)],
        "call": ((166, DN), "slow enough to stop for anyone emerging"),
    },
    "SC-03": {
        "still": [("car", (278, DN), False), ("car", (80, UP), False), ("car", (160, UP), False)],
        "movers": [("car", [(190, DN), (246, DN)], True)],
        "ego": [(22, DN), (214, DN)],
        "call": ((214, DN), "keeps a safe gap as it brakes"),
    },
    "SC-04": {
        "decor": [("phantom", 228, DN)],
        "movers": [("car", [(10, DN), (98, DN)], True)],
        "ego": [(60, DN), (152, DN)],
        "call": ((228, DN), "no hard brake for an unconfirmed object"),
    },
    "SC-05": {
        "junction": JUNCTION,
        "stop": 196,
        "decor": [("signal", 190, 108, "go")],
        "movers": [("car_v", [(240, 2), (240, 118)], True)],
        "ego": [(22, DN), (184, DN)],
        "call": ((184, DN), "waits while its path is crossed"),
    },
    "SC-06": {
        "junction": JUNCTION,
        "plan": LEFT,
        "movers": [("car", [(300, UP), (130, UP)], True)],
        "ego": [(22, DN), (192, DN)],
        "call": ((228, UP), "turns only with a safe gap"),
        "at_y": 98,
    },
    "SC-07": {
        "junction": JUNCTION,
        "decor": [("island", 228, MID, 15)],
        "movers": [("car", CIRCLE, True)],
        "ego": [(22, DN), (176, DN)],
        "call": ((176, DN), "yields to circulating traffic"),
    },
    "SC-08": {
        "side": True,
        "plan": RIGHT,
        "movers": [("bike", [(104, 89), (196, 89)], True)],
        "ego": [(22, DN), (158, DN)],
        "call": ((196, 89), "waits for the cyclist"),
    },
    "SC-09": {
        "decor": [("nogps", 20, 15)],
        "still": [("car", (120, UP), False)],
        "ego": [(22, DN), (236, DN)],
        "call": ((236, DN), "keeps its lane, or stops in it"),
    },
    "SC-10": {
        "decor": [("cones",), ("label", 186, 112, "the map: lane open")],
        "plan": [(160, DN), (292, DN)],
        "ego": [(22, DN), (158, DN)],
        "call": ((158, DN), "does not follow the map into the cones"),
    },
    "SC-11": {
        "junction": JUNCTION,
        "stop": 196,
        "still": [("ped", (228, MID), True)],
        "decor": [("arm", 228, MID), ("mast", "asks for remote assistance")],
        "ego": [(22, DN), (184, DN)],
        "call": ((228, MID), "stops, does not move on the signal"),
        "at_y": 98,
    },
    "SC-12": {
        "movers": [("ev", [(10, UP), (272, UP)], True)],
        "ego": [(22, DN), (118, DN), (148, 87), (172, 87)],
        "call": ((172, 87), "pulls aside and lets it pass"),
    },
    "SC-13": {
        "decor": [("debris", 214, DN)],
        "ego": [(22, DN), (188, DN)],
        "call": ((214, DN), "stops before it, or passes in lane"),
    },
    "SC-14": {
        "decor": [("rain", 140)],
        "still": [("car", (90, UP), False)],
        "ego": [(22, DN), (222, DN)],
        "call": ((222, DN), "sees the ODD exit and stops safely"),
    },
    "SC-15": {
        "decor": [("door", 170, 87)],
        "still": [("ped", (200, 106), False)],
        "movers": [("ped", [(140, 114), (164, 102)], True)],
        "ego": [(170, 87)],
        "call": ((170, 87), "holds while a door is open"),
    },
    "SC-16": {
        "zebra": (196, 220),
        "stop": 189,
        "decor": [("signal", 182, 108, "stop")],
        "still": [("ped", (214, 52), False)],
        "movers": [("ped", [(206, 114), (206, 40)], True)],
        "ego": [(172, DN)],
        "call": ((172, DN), "stays held until it may go"),
    },
    "SC-17": {
        "decor": [("label", 8, 112, "Autoware lost while driving")],
        "still": [("car", (120, UP), False)],
        "ego": [(22, DN), (206, DN)],
        "hazard": True,
        "call": ((206, DN), "the monitor stops it in lane"),
    },
    "SC-18": {
        "decor": [("bay", 146, 96, 48, 20)],
        "still": [("bus", (258, 106), False)],
        "movers": [("bike", [(30, 89), (110, 89)], True)],
        "ego": [(22, DN), (126, DN), (156, 105), (170, 105)],
        "call": ((170, 105), "pulls over only into a mapped stop"),
    },
    "SC-19": {
        "still": [("ped", (176, 104), False)],
        "movers": [("bike", [(40, 89), (286, 89)], True)],
        "ego": [(170, DN)],
        "hazard": True,
        "call": ((170, DN), "warns before they step out"),
    },
    "SC-20": {
        "decor": [("mast", "remote driver: link delayed")],
        "movers": [("ped", [(214, 8), (214, 74)], True)],
        "ego": [(22, DN), (134, DN)],
        "call": ((134, DN), "rejects stale commands, stops"),
        "at_y": 98,
    },
    "SC-21": {
        "decor": [("mast", "release for vehicle 2")],
        "still": [("car", (210, 87), True)],
        "ego": [(140, 87)],
        "call": ((140, 87), "moves only on a release bound to it"),
        "at_y": 98,
    },
    "SC-22": {
        "side": True,
        "ego": [(22, DN), (176, DN)],
        "shown": RIGHT,
        "blink": True,
        "still": [("bike", (110, 89), False)],
        "call": ((176, DN), "its indicator matches the turn"),
    },
    "SC-23": {
        "junction": JUNCTION,
        "stop": 196,
        "movers": [("car_v", [(216, 2), (216, 20)], True)],
        "ego": [(22, DN), (184, DN)],
        "call": ((184, DN), "takes its turn and shows it"),
        "at_y": 98,
    },
    "SC-24": {
        "road": False,
        "decor": [("cabin",), ("mast", "remote operator")],
        "ego": [],
        "call": ((181, 48), "every seat reaches an operator"),
        "at_y": 98,
    },
    "SC-25": {
        "still": [("car", (178, DN), False), ("ped", (236, 14), True), ("ped", (252, 17), True)],
        "decor": [("star", 165, DN), ("mast", "remote operations")],
        "ego": [(150, DN)],
        "call": ((150, DN), "holds; doors open from inside"),
        "at_y": 98,
    },
    "SC-26": {
        "road": False,
        "decor": [("depot",), ("checks", 200, 34)],
        "ego": [(110, 62)],
        "call": ((110, 62), "no dispatch until checks are recorded"),
    },
}


def check(ids: list[str]) -> list[str]:
    errs = [f"{i}: no sketch in scards.py" for i in ids if i not in SCENES]
    errs += [
        f"{i}: sketch in scards.py for a scenario that does not exist"
        for i in SCENES
        if i not in ids
    ]
    return errs


# ---------------------------------------------------------------- scene, 300 x 120 at (ox, oy)


def user(kind: str, x: float, y: float, key: bool, anim: str = "") -> str:
    cls = "key" if key else "oth"
    if kind == "car":
        return kit.car(x, y, cls, anim=anim)
    if kind == "car_v":
        return kit.car(x, y, cls, vertical=True, anim=anim)
    if kind == "ev":
        lights = "".join(
            fk.el("circle", None, cx=fk.num(x + dx), cy=fk.num(y), r=2.6, class_=c)
            for dx, c in ((-4, "bcn"), (4, "bcr"))
        )
        return f"<g>{kit.car(x, y, cls)}<g>{lights}{kit.blink()}</g>{anim}</g>"
    if kind == "bus":
        body = fk.el(
            "rect", None, x=fk.num(x - 22), y=fk.num(y - 7), width=44, height=14, rx=3, class_=cls
        )
        return f"<g>{body}{anim}</g>"
    if kind == "bike":
        body = fk.el(
            "rect", None, x=fk.num(x - 8), y=fk.num(y - 2.5), width=16, height=5, rx=2.5, class_=cls
        )
        return f"<g>{body}{anim}</g>"
    body = fk.el("circle", None, cx=fk.num(x), cy=fk.num(y), r=4.2, class_="key" if key else "ped")
    return f"<g>{body}{anim}</g>"


def decor(ox: float, oy: float, d: tuple) -> list[str]:
    kind = d[0]
    if kind == "signal":
        _, x, y, state = d
        out = [
            fk.el("rect", None, x=ox + x - 4, y=oy + y - 9, width=8, height=18, rx=2, class_="sig")
        ]
        for dy, s in ((-4.5, "stop"), (4.5, "go")):
            cls = ("sr" if s == "stop" else "sg") if s == state else "soff"
            out.append(fk.el("circle", None, cx=ox + x, cy=fk.num(oy + y + dy), r=2.6, class_=cls))
        return out
    if kind == "island":
        _, x, y, r = d
        return [fk.el("circle", None, cx=ox + x, cy=oy + y, r=r, class_="isle")]
    if kind == "cones":
        return [
            fk.el(
                "path",
                None,
                d=f"M{fk.num(ox + x)} {fk.num(oy + y - 5)} L{fk.num(ox + x + 4)} {fk.num(oy + y + 3)} "
                f"L{fk.num(ox + x - 4)} {fk.num(oy + y + 3)} Z",
                class_="cone",
            )
            for x, y in CONES
        ]
    if kind == "label":
        _, x, y, s = d
        return [fk.text(ox + x, oy + y, s, "ax")]
    if kind == "mast":
        mx = ox + 18
        return [
            fk.el(
                "path",
                None,
                d=f"M{mx} {oy + 22} L{mx + 6} {oy + 6} L{mx + 12} {oy + 22}",
                class_="mast",
            ),
            fk.text(mx + 18, oy + 19, d[1], "ax"),
        ]
    if kind == "nogps":
        _, x, y = d
        return [
            fk.el("circle", None, cx=ox + x, cy=oy + y, r=6, class_="sat"),
            fk.el(
                "line",
                None,
                x1=ox + x - 7,
                y1=oy + y - 7,
                x2=ox + x + 7,
                y2=oy + y + 7,
                class_="xo",
            ),
            fk.text(ox + x + 12, oy + y + 4, "GNSS lost", "ax"),
        ]
    if kind == "phantom":
        _, x, y = d
        return [
            fk.el(
                "rect", None, x=ox + x - 11, y=oy + y - 7, width=22, height=14, rx=3, class_="phan"
            ),
            fk.text(ox + x, oy + y + 4, "?", "kt", "middle"),
        ]
    if kind == "debris":
        _, x, y = d
        pts = [(-7, -3), (-2, -7), (6, -5), (8, 2), (2, 7), (-6, 5)]
        return [
            fk.el(
                "path",
                None,
                d="M"
                + " L".join(f"{fk.num(ox + x + a)} {fk.num(oy + y + b)}" for a, b in pts)
                + " Z",
                class_="key",
            )
        ]
    if kind == "arm":
        _, x, y = d
        return [
            fk.el("line", None, x1=ox + x, y1=oy + y, x2=ox + x - 12, y2=oy + y + 6, class_="armk")
        ]
    if kind == "rain":
        x0 = d[1]
        out = [fk.el("rect", None, x=ox + x0, y=oy, width=SW - x0, height=SH, class_="fog")]
        for i in range(int((SW - x0 - 6) / 12)):
            for j in range(5):
                x, y = ox + x0 + 6 + i * 12 + (j % 2) * 6, oy + 8 + j * 24
                out.append(fk.el("line", None, x1=x, y1=y, x2=x - 3, y2=y + 7, class_="drop"))
        return out
    if kind == "door":
        _, x, y = d
        return [
            fk.el(
                "rect", None, x=ox + x - 6, y=oy + y + 6.5, width=10, height=7, rx=1, class_="doorp"
            )
        ]
    if kind == "bay":
        _, x, y, w, h = d
        return [fk.el("rect", None, x=ox + x, y=oy + y, width=w, height=h, rx=3, class_="bay")]
    if kind == "star":
        _, x, y = d
        pts = [
            (
                x + (9 if k % 2 == 0 else 4) * math.cos(math.pi * k / 5),
                y + (9 if k % 2 == 0 else 4) * math.sin(math.pi * k / 5),
            )
            for k in range(10)
        ]
        return [
            fk.el(
                "path",
                None,
                d="M" + " L".join(f"{fk.num(ox + a)} {fk.num(oy + b)}" for a, b in pts) + " Z",
                class_="hit",
            )
        ]
    if kind == "cabin":
        out = [fk.el("rect", None, x=ox + 96, y=oy + 30, width=108, height=64, rx=14, class_="cab")]
        for sx in (126, 174):
            for sy in (48, 76):
                out.append(
                    fk.el(
                        "rect",
                        None,
                        x=ox + sx - 12,
                        y=oy + sy - 8,
                        width=24,
                        height=16,
                        rx=4,
                        class_="seat",
                    )
                )
                out.append(fk.el("circle", None, cx=ox + sx - 3, cy=oy + sy, r=4.2, class_="ped"))
                out.append(fk.el("circle", None, cx=ox + sx + 7, cy=oy + sy, r=2.4, class_="sos"))
        return out
    if kind == "depot":
        return [
            fk.el("rect", None, x=ox + 70, y=oy + 30, width=80, height=64, rx=4, class_="bay"),
            fk.text(ox + 110, oy + 108, "depot bay", "ax", "middle"),
        ]
    if kind == "checks":
        _, x, y = d
        out = [fk.el("rect", None, x=ox + x, y=oy + y, width=82, height=56, rx=4, class_="sheet")]
        for i, s in enumerate(("calibration", "cleanliness", "versions")):
            out.append(
                fk.el(
                    "rect",
                    None,
                    x=ox + x + 6,
                    y=oy + y + 8 + 16 * i,
                    width=8,
                    height=8,
                    rx=1,
                    class_="box",
                )
            )
            out.append(fk.text(ox + x + 18, oy + y + 15.5 + 16 * i, s, "ax"))
        return out
    raise fk.FigureError(f"scards.py: no decor {kind}")


def draw_scene(ox: float, oy: float, s: dict) -> list[str]:
    if s.get("road", True):
        out = kit.road(ox, oy, s.get("junction"), s.get("side", False))
    else:
        out = [fk.el("rect", None, x=ox, y=oy, width=SW, height=SH, rx=6, class_="verge")]
    if "zebra" in s:
        out += kit.crosswalk(ox, oy, *s["zebra"])
    if "stop" in s:
        out.append(kit.stopline(ox, oy, s["stop"]))
    for d in s.get("decor", []):
        out += decor(ox, oy, d)
    for kind, (x, y), key in s.get("still", []):
        out.append(user(kind, ox + x, oy + y, key))
    for kind, path, key in s.get("movers", []):
        x, y = path[-1]
        out.append(user(kind, ox + x, oy + y, key, kit.motion(ox, oy, path)))
    if len(s.get("plan", [])) > 1:
        out.append(fk.el("path", None, d=kit.poly(ox, oy, s["plan"]), class_="plan"))
    ego = s["ego"]
    shown = s.get("shown", ego)
    if len(shown) > 1:
        out.append(fk.el("path", None, d=kit.poly(ox, oy, shown), class_="ipath"))
    if ego:
        ex, ey = ego[-1]
        lights = ""
        if s.get("hazard"):
            lights = f"<g>{kit.blinkers(ox + ex, oy + ey, 'right', 'amb')}{kit.blinkers(ox + ex, oy + ey, 'left', 'amb')}{kit.blink()}</g>"
        elif s.get("blink"):
            lights = f"<g>{kit.blinkers(ox + ex, oy + ey, 'right', 'amb')}{kit.blink()}</g>"
        out.append(kit.car(ox + ex, oy + ey, "sego", anim=lights + kit.motion(ox, oy, ego)))
    (cx, cy), label = s["call"]
    lw = fk.width(label, "s") + 14
    lx = min(max(ox + cx - lw / 2, ox + 4), ox + SW - lw - 4)
    ly = oy + s.get("at_y", 6)
    out.append(
        f"<g>{fk.el('circle', None, cx=fk.num(ox + cx), cy=fk.num(oy + cy), r=12, class_='pring')}"
        f"{fk.el('rect', None, x=fk.num(lx), y=fk.num(ly), width=fk.num(lw), height=18, rx=9, class_='pcall')}"
        f"{fk.text(lx + lw / 2, ly + 13, label, 'ct', 'middle')}{kit.appear(kit.DRIVE * 0.98)}</g>"
    )
    return out


# ---------------------------------------------------------------- card


def chips(
    x0: float, y: float, items: list[tuple[str, str]], right: float
) -> tuple[list[str], float]:
    """Chips (label, class) from x0, wrapping before `right`; the y of the last row."""
    out, x = [], x0
    for label, cls in items:
        w = fk.width(label, "s") + 12
        if x + w > right and x > x0:
            x, y = x0, y + CHIP_H + 4
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x),
                y=fk.num(y - 12),
                width=fk.num(w),
                height=CHIP_H,
                rx=8,
                class_=cls,
            )
        )
        out.append(fk.text(x + w / 2, y, label, cls + "t", "middle"))
        x += w + 5
    return out, y


def body(x: float, y: float, c: dict) -> tuple[list[str], float]:
    """The card's content and its height."""
    out = [fk.text(x + 14, y + 24, c["id"], "gid")]
    if c["crosses"]:
        label = "crosses the ODD boundary"
        w = fk.width(label, "s") + 14
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x + CW - 14 - w),
                y=y + 11,
                width=fk.num(w),
                height=18,
                rx=4,
                class_="xp",
            )
        )
        out.append(fk.text(x + CW - 14 - w / 2, y + 24, label, "xpt", "middle"))
    lines = fk.wrap(c["name"], CW - 28, "tb")[:2]
    for i, ln in enumerate(lines):
        out.append(fk.text(x + 14, y + 44 + 16 * i, ln, "tb"))
    oy = y + 34 + 16 * len(lines)
    out += draw_scene(x + 15, oy, SCENES[c["id"]])
    yy = oy + SH + 20
    for label, xs in c["exercises"]:
        for i, ln in enumerate(fk.wrap(f"{label}: {', '.join(xs)}", CW - 34, "s")):
            out.append(fk.text(x + 14, yy, ln, "ax"))
            yy += 14
    yy += 8
    out.append(fk.text(x + 14, yy, "Varies", "hd"))
    items = [(a, "ox" if crosses else "oc") for a, crosses in c["odd"]]
    items += [(f"bound {b}", "ob") for b in c["bounds"]]
    got, yy = chips(x + 64, yy, items, x + CW - 14)
    out += got
    yy += 22
    out.append(fk.text(x + 14, yy, "Methods", "hd"))
    got, yy = chips(x + 64, yy, [(m, "mp") for m in c["methods"]], x + CW - 14)
    out += got
    yy += 22
    out.append(fk.text(x + 14, yy, "Passes when", "hd"))
    yy += 15
    for ln in fk.wrap(c["criterion"], CW - 34, "s"):
        out.append(fk.text(x + 14, yy, ln, "s"))
        yy += 14
    yy += 2
    for ln in fk.wrap(f"Judged against {', '.join(c['refs'])}", CW - 34, "s"):
        out.append(fk.text(x + 14, yy, ln, "ax"))
        yy += 14
    run = ", ".join(c["run_by"]) if c["run_by"] else "no verification case (validation, WP-V-07)"
    for ln in fk.wrap(f"Run by {run}", CW - 34, "s"):
        out.append(fk.text(x + 14, yy, ln, "ax"))
        yy += 14
    return out, yy - y + 4


EXTRA = kit.EXTRA + """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --bad2:#c2412b; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --bad2:#ff7a63; } }
svg .hd { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .sego { fill:var(--mon); }
svg .key { fill:var(--amber); } svg .kt { font:700 10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--amber); }
svg .plan { fill:none; stroke:var(--ink3); stroke-width:1.6; stroke-dasharray:2 4; }
svg .pring { fill:none; stroke:var(--req); stroke-width:1.6; }
svg .pcall { fill:var(--req); }
svg .amb { fill:var(--amber); }
svg .bcn { fill:#2d55c8; } svg .bcr { fill:#d23a2a; }
svg .sig { fill:var(--ink2); } svg .sr { fill:#e0412f; } svg .sg { fill:#2fb36c; } svg .soff { fill:var(--ink3); opacity:.5; }
svg .isle { fill:var(--verge); stroke:var(--ink3); stroke-width:1.2; }
svg .cone { fill:var(--amber); }
svg .sat { fill:none; stroke:var(--ink3); stroke-width:1.4; } svg .xo { stroke:var(--bad2); stroke-width:1.8; }
svg .phan { fill:none; stroke:var(--amber); stroke-width:1.4; stroke-dasharray:3 2; }
svg .armk { stroke:var(--amber); stroke-width:2.2; stroke-linecap:round; }
svg .fog { fill:var(--ink3); opacity:.12; } svg .drop { stroke:var(--ink3); stroke-width:1.2; }
svg .doorp { fill:var(--amber); }
svg .bay { fill:none; stroke:var(--req); stroke-width:1.3; stroke-dasharray:4 3; }
svg .hit { fill:var(--bad2); }
svg .cab { fill:var(--card); stroke:var(--ink3); stroke-width:1.4; }
svg .seat { fill:var(--road); } svg .sos { fill:var(--amber); }
svg .sheet { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; } svg .box { fill:none; stroke:var(--ink3); stroke-width:1.2; }
svg .xp { fill:var(--bg); stroke:var(--bad2); stroke-width:1.2; } svg .xpt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bad2); }
svg .oc { fill:var(--card); stroke:var(--ink3); stroke-width:1; } svg .oct { font:10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .ox { fill:var(--card); stroke:var(--bad2); stroke-width:1.6; } svg .oxt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--bad2); }
svg .ob { fill:none; stroke:var(--ink3); stroke-width:1; stroke-dasharray:3 2; } svg .obt { font:10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink3); }
svg .mp { fill:var(--monsoft); stroke:var(--mon); stroke-width:1; } svg .mpt { font:10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--mon); }
"""


def sheet(cards: list[dict]) -> str:
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    out = [
        fk.text(MARGIN, 34, "What each known scenario sets up, and when it passes", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-V-03 §2, Figure 2-1: one concrete instance of each logical scenario, what it exercises, the ODD "
            "attributes it varies, its methods and pass criterion,",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "and the verification cases of WP-S-09 that run it. Schematic: the ranges are in §2.2, and no scenario "
            "has been run.",
            "t",
        ),
    ]
    y = HEAD
    for i in range(0, len(cards), COLS):
        row = cards[i : i + COLS]
        rh = max(body(0, 0, c)[1] for c in row)
        for j, c in enumerate(row):
            x = MARGIN + j * (CW + GAP)
            out.append(
                fk.el("rect", None, x=x, y=y, width=CW, height=fk.num(rh), rx=8, class_="card")
            )
            out += body(x, y, c)[0]
        y += rh + GAP
    ly, lx = y + 22, MARGIN
    legend = [
        ("sego", "the vehicle"),
        ("key", "what the scenario is about"),
        ("oth", "other road users"),
        ("ipath", "what the pass criterion asks"),
        ("plan", "a path it must not just follow"),
        ("ox", "swept across the ODD boundary"),
        ("ob", "behaviour bound not yet fixed"),
    ]
    for mark, label in legend:
        if mark in ("ipath", "plan"):
            out.append(fk.el("line", None, x1=lx, y1=ly - 4, x2=lx + 26, y2=ly - 4, class_=mark))
        elif mark in ("ox", "ob"):
            out.append(
                fk.el("rect", None, x=lx, y=ly - 12, width=26, height=CHIP_H, rx=8, class_=mark)
            )
        else:
            out.append(kit.car(lx + 13, ly - 4, mark))
        out.append(fk.text(lx + 34, ly, label, "t"))
        lx += 34 + fk.width(label, "t") + 22
        if lx > w - 240:
            lx, ly = MARGIN, ly + 24
    desc = "Known scenarios: " + "; ".join(
        f"{c['id']} {c['name']}: passes when {c['criterion']}" for c in cards
    )
    return fk.svg(
        w, int(ly + 22), "WP-V-03 Figure 2-1: the known scenarios", desc + ".", out, EXTRA
    )
