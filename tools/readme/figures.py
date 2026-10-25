#!/usr/bin/env python3
"""The README and wiki figures: a concept illustration of the doer-and-checker architecture in an
urban scene, the architecture strip, the standards map, the item and the minimal risk condition.

    python3 tools/readme/figures.py            # write tools/readme/figures/*.svg
    python3 tools/readme/figures.py --check    # fail if any of them is stale

Every label comes from facts.py, which reads the work products and the decision register; the
vehicles are the models of models/ (see models/CREDITS.md), rendered by render3d.py. The scene is an
illustration of the concept, not output of the system: the safety monitor does not exist yet, and
each scene figure says so on its face. Output is deterministic: the same inputs give the same bytes.
"""

from __future__ import annotations

import math
from pathlib import Path
import random
import re
import sys
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facts as fx  # noqa: E402
import mesh  # noqa: E402
import render3d as r3  # noqa: E402
import wpregister  # noqa: E402  (on the path through facts)

OUT = HERE / "figures"
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
STAMP = "CONCEPT ILLUSTRATION · the safety monitor is not built yet · draft for engineering review"

BLUE, BLUE2, RED, GREEN, VIOLET, AMBER, GREY = (
    "#5b9bff",
    "#a9c8ff",
    "#ff4d40",
    "#43f08a",
    "#c38bff",
    "#ffcf6e",
    "#d5d9df",
)

# ---------------------------------------------------------------- the scene (metres; x right, y ahead)

EGO = (1.75, 0.0)
CROSSWALK = (29.0, 32.0)
CROSS_ST = (34.0, 47.0)
STOP_Y = 28.4  # the monitor's stop line, before the crosswalk
PED = (0.9, 30.6)
CYCLIST = (-6.2, 26.0)
GEOFENCE_Y = 80.0
PARKED = ("minivan", 4.9, 13.0, 0.0)
TRAFFIC = [  # model, x, y, heading (degrees to the left of +y)
    ("sedan", -1.75, 52.0, 180.0),
    ("hatchback", -1.75, 66.0, 180.0),
    ("wagon", -14.0, 38.5, -90.0),
    ("suv", -22.5, 38.5, -90.0),
    ("compact", 12.0, 42.5, 90.0),
]
EGO_PAINT = r3.Paint(body=(232, 235, 238))
TRAFFIC_PAINT = {
    "sedan": r3.Paint(body=(92, 104, 122)),
    "hatchback": r3.Paint(body=(150, 70, 62)),
    "wagon": r3.Paint(body=(120, 124, 130)),
    "suv": r3.Paint(body=(48, 52, 58)),
    "compact": r3.Paint(body=(70, 98, 132)),
    "minivan": r3.Paint(body=(168, 170, 168)),
}


def text(x, y, s, size=13, fill="#e8eaed", weight=400, anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}"{a} '
        f'font-family="{FONT}"{" " + extra if extra else ""}>{escape(s)}</text>'
    )


def tw(s: str, size: float) -> float:
    """Approximate width of a string in the UI font."""
    return len(s) * size * 0.56


def poly(cam, pts, style):
    return '<polygon points="{}" style="{}"/>'.format(
        " ".join(f"{a:.1f},{b:.1f}" for a, b in (cam(*p) for p in pts)), style
    )


def line(cam, a, b, style):
    (x1, y1), (x2, y2) = cam(*a), cam(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="{style}"/>'


class Dots:
    """Many small points, drawn as zero-length round-capped strokes, one path per look."""

    def __init__(self, cam):
        self.cam = cam
        self.groups: dict[tuple, list[str]] = {}

    def add(self, p, r, colour, opacity):
        x, y = self.cam(*p)
        key = (colour, round(r * 4) / 4, round(opacity * 10) / 10)
        self.groups.setdefault(key, []).append(f"M{x:.0f} {y:.0f}h0")

    def svg(self, cls=""):
        c = f' class="{cls}"' if cls else ""
        return [
            f'<path{c} d="{"".join(ds)}" stroke="{col}" stroke-width="{2 * r:g}" stroke-opacity="{op:g}" stroke-linecap="round" fill="none"/>'
            for (col, r, op), ds in sorted(self.groups.items())
            if op > 0 and r > 0
        ]


DEFS = f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07090c"/><stop offset="0.45" stop-color="#12151a"/><stop offset="1" stop-color="#1b1e24"/></linearGradient>
<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0d11" stop-opacity="0.95"/><stop offset="0.28" stop-color="#0b0d11" stop-opacity="0.35"/><stop offset="0.5" stop-color="#0b0d11" stop-opacity="0"/></linearGradient>
<radialGradient id="vignette" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient>
<linearGradient id="env" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.55"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0.22"/></linearGradient>
<linearGradient id="path" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{RED}" stop-opacity="0.55"/><stop offset="0.7" stop-color="{RED}" stop-opacity="0.35"/><stop offset="1" stop-color="{RED}" stop-opacity="0.05"/></linearGradient>
<linearGradient id="wall" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{BLUE2}" stop-opacity="0.75"/><stop offset="1" stop-color="{BLUE2}" stop-opacity="0.05"/></linearGradient>
<linearGradient id="curtain" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="7" height="7" fill="#9aa0a6" fill-opacity="0.10"/><line x1="0" y1="0" x2="0" y2="7" stroke="#c4c8ce" stroke-opacity="0.35" stroke-width="2"/></pattern>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.2"/></filter>
<filter id="shadow" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5"/></filter>
</defs>
<style>
.pulse {{ animation: pulse 2.8s ease-in-out infinite; }}
.scan {{ animation: scan 3.6s linear infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 0.55; }} 50% {{ opacity: 1; }} }}
@keyframes scan {{ 0% {{ opacity: 0.15; }} 30% {{ opacity: 0.9; }} 100% {{ opacity: 0.15; }} }}
@media (prefers-reduced-motion: reduce) {{ .pulse, .scan {{ animation: none; }} }}
</style>"""


def road(cam):
    w, side, asphalt = "#cfd3d9", "#2a2e34", "#202328"
    out = [
        poly(
            cam, [(-7.5, -10, 0), (7.5, -10, 0), (7.5, 120, 0), (-7.5, 120, 0)], f"fill:{asphalt}"
        ),
        poly(
            cam,
            [
                (-80, CROSS_ST[0], 0),
                (80, CROSS_ST[0], 0),
                (80, CROSS_ST[1], 0),
                (-80, CROSS_ST[1], 0),
            ],
            f"fill:{asphalt}",
        ),
    ]
    for x, d in ((-7.5, -2.2), (7.5, 2.2)):  # pavements
        for y0, y1 in ((-10, CROSS_ST[0]), (CROSS_ST[1], 120)):
            out.append(
                poly(cam, [(x, y0, 0), (x + d, y0, 0), (x + d, y1, 0), (x, y1, 0)], f"fill:{side}")
            )
            out.append(
                line(cam, (x, y0), (x, y1), f"stroke:{w};stroke-width:1.4;stroke-opacity:.7")
            )
    for y in CROSS_ST:
        for a, b in ((-80, -7.5), (7.5, 80)):
            out.append(line(cam, (a, y), (b, y), f"stroke:{w};stroke-width:1.4;stroke-opacity:.7"))
    for dx in (-0.12, 0.12):  # double yellow centre line
        out.append(
            line(cam, (dx, -10), (dx, CROSSWALK[0] - 1.5), "stroke:#e6c84a;stroke-width:1.3")
        )
        out.append(line(cam, (dx, CROSS_ST[1] + 3.5), (dx, 120), "stroke:#e6c84a;stroke-width:1.3"))
    for x in (-3.6, 3.6):  # parking lanes
        for y in range(-10, int(CROSSWALK[0]) - 2, 6):
            out.append(line(cam, (x, y), (x, y + 3), "stroke:#6d727a;stroke-width:1.2"))
    out.append(
        line(cam, (0, CROSSWALK[0] - 1.2), (7.5, CROSSWALK[0] - 1.2), f"stroke:{w};stroke-width:3")
    )
    for y0, y1, op in (
        (CROSSWALK[0], CROSSWALK[1], 0.85),
        (CROSS_ST[1] + 0.5, CROSS_ST[1] + 3.0, 0.55),
    ):
        for i in range(10):
            x = -7 + i * 1.5
            out.append(
                poly(
                    cam,
                    [(x, y0, 0), (x + 0.7, y0, 0), (x + 0.7, y1, 0), (x, y1, 0)],
                    f"fill:{w};fill-opacity:{op}",
                )
            )
    return out


def lidar(cam, rnd):
    """Points on building fronts and trees, and scan rings on the ground around the vehicle."""
    world = Dots(cam)
    for side, y0, y1 in ((-1, -6, 28), (-1, 50, 95), (1, -6, 9), (1, 22, 28), (1, 50, 95)):
        for z in [0.5 + 0.75 * i for i in range(12)]:
            y = y0
            while y < y1:
                y += rnd.uniform(0.5, 1.2)
                if rnd.random() < 0.18:
                    continue
                hue = int(260 - 140 * z / 9) // 10 * 10
                p = (side * 11.5 + rnd.uniform(-0.15, 0.15), y, z)
                world.add(p, max(0.55, 1.5 - y / 70), f"hsl({hue},85%,62%)", 0.75 - y / 200)
    for _ in range(90):
        x, y = rnd.choice((-1, 1)) * rnd.uniform(8.3, 9.5), rnd.uniform(0, 90)
        if CROSS_ST[0] - 3 < y < CROSS_ST[1] + 3:
            continue
        for _ in range(4):
            p = (x + rnd.uniform(-1, 1), y + rnd.uniform(-1, 1), rnd.uniform(2.5, 4.5))
            world.add(p, 1.0, "hsl(130,70%,55%)", 0.5)
    out = world.svg()
    for i, rad in enumerate((4.5, 6.5, 9, 12, 15.5, 19.5, 24)):
        ring = Dots(cam)
        n = int(50 + rad * 6)
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = EGO[0] + rad * math.cos(a) + rnd.uniform(-0.08, 0.08), EGO[1] + rad * math.sin(a)
            if y < -7 or (0.3 < x < 3.2 and 2.4 < y < STOP_Y):
                continue
            ring.add(
                (x, y, 0), max(0.7, 1.7 - rad / 30), f"hsl({150 + int(rad * 6)},90%,62%)", 0.75
            )
        out.append(f'<g class="scan" style="animation-delay:{i * 0.18:.2f}s">')
        out += ring.svg()
        out.append("</g>")
    return out


def overlays(cam):
    """Autoware's plan, the occluded area, the monitor's envelope and stop wall, the geofence."""
    out = [
        poly(
            cam, [(0.65, 2.4, 0), (2.85, 2.4, 0), (2.85, 110, 0), (0.65, 110, 0)], "fill:url(#path)"
        )
    ]
    points = Dots(cam)
    for y in range(4, 108, 3):  # trajectory points
        points.add((1.75, y, 0.02), max(0.8, 3.2 - y / 30), "#ffd1cc", max(0.15, 0.9 - y / 120))
    out += points.svg()
    model, vx, vy, _ = PARKED
    hw, hl = 1.05, 2.6
    out.append(
        poly(
            cam,
            [
                (vx + hw, vy - hl, 0),
                (vx + hw, vy + hl, 0),
                (11, vy + hl + 9, 0),
                (11, vy - hl + 2, 0),
            ],
            "fill:url(#hatch);stroke:#c4c8ce;stroke-opacity:.5;stroke-dasharray:4 3;stroke-width:1",
        )
    )
    env = [(0.3, 2.4, 0), (3.2, 2.4, 0), (3.2, STOP_Y, 0), (0.3, STOP_Y, 0)]
    out.append(
        f'<g class="pulse" filter="url(#glow)">{poly(cam, env, f"fill:none;stroke:{BLUE};stroke-width:6")}</g>'
    )
    out.append(poly(cam, env, f"fill:url(#env);stroke:{BLUE2};stroke-width:2"))
    for y in (8, 14, 20, 26):  # stopping-distance ticks
        out.append(line(cam, (0.3, y), (0.9, y), f"stroke:{BLUE2};stroke-width:1.4"))
        out.append(line(cam, (2.6, y), (3.2, y), f"stroke:{BLUE2};stroke-width:1.4"))
    out.append(
        poly(
            cam,
            [(0.1, STOP_Y, 0), (3.4, STOP_Y, 0), (3.4, STOP_Y, 2.2), (0.1, STOP_Y, 2.2)],
            "fill:url(#wall)",
        )
    )
    out.append(line(cam, (0.1, STOP_Y, 0), (3.4, STOP_Y, 0), "stroke:#ffffff;stroke-width:3"))
    sx, sy = cam(1.75, STOP_Y - 2.2, 0)
    out.append(text(sx, sy + 4, "STOP", 12, "#ffffff", 800, "middle", 'letter-spacing="2"'))
    gy = GEOFENCE_Y
    out.append(
        poly(cam, [(-40, gy, 0), (40, gy, 0), (40, gy, 4), (-40, gy, 4)], "fill:url(#curtain)")
    )
    out.append(
        line(cam, (-40, gy), (40, gy), f"stroke:{VIOLET};stroke-width:2;stroke-dasharray:9 6")
    )
    return out


def tag(cam, p, label, color):
    sx, sy = cam(*p)
    w = tw(label, 10.5) + 10
    return [
        f'<rect x="{sx - w / 2:.1f}" y="{sy - 15:.1f}" width="{w:.1f}" height="15" rx="3" fill="#0d0f12" '
        f'fill-opacity="0.78" stroke="{color}" stroke-opacity="0.8" stroke-width="0.8"/>',
        text(sx, sy - 4, label, 10.5, color, 600, "middle"),
    ]


def detection_box(cam, x, y, heading, size, color=GREEN):
    """The wireframe box a perception stack draws around a detected object."""
    w, ln, h = size
    c, s = math.cos(math.radians(heading)), math.sin(math.radians(heading))
    corners = {}
    for i, dx in enumerate((-w / 2, w / 2)):
        for j, dy in enumerate((-ln / 2, ln / 2)):
            for k, z in enumerate((0, h)):
                corners[(i, j, k)] = (x + dx * c - dy * s, y + dx * s + dy * c, z)
    edges = [((0, 0, 0), (1, 0, 0)), ((0, 1, 0), (1, 1, 0)), ((0, 0, 1), (1, 0, 1)), ((0, 1, 1), (1, 1, 1)),
             ((0, 0, 0), (0, 1, 0)), ((1, 0, 0), (1, 1, 0)), ((0, 0, 1), (0, 1, 1)), ((1, 0, 1), (1, 1, 1)),
             ((0, 0, 0), (0, 0, 1)), ((1, 0, 0), (1, 0, 1)), ((0, 1, 0), (0, 1, 1)), ((1, 1, 0), (1, 1, 1))]  # fmt: skip
    top = [corners[k] for k in ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))]
    out = [poly(cam, top, f"fill:{color};fill-opacity:0.08")]
    out += [
        line(cam, corners[a], corners[b], f"stroke:{color};stroke-width:1.3;stroke-opacity:0.9")
        for a, b in edges
    ]
    return out


def cylinder(cam, x, y, r, h, color, n=14):
    def ring(z):
        return [
            (x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z)
            for i in range(n)
        ]

    out = [
        poly(cam, ring(z), f"fill:{color};fill-opacity:0.25;stroke:{color};stroke-width:1.4")
        for z in (0, h)
    ]
    out += [
        line(cam, (x + d, y, 0), (x + d, y, h), f"stroke:{color};stroke-width:1.4") for d in (-r, r)
    ]
    return out


def vehicle(cam, model: mesh.Model, x, y, heading, paint, min_cell=0.03, ambient=0.42):
    """A model simplified to what its size on screen can show, then rendered."""
    ppm = cam.focal / max(cam.depth((x, y, 0.8)), 1.0)  # pixels per metre at its distance
    m = mesh.simplify(model, max(min_cell, 3.0 / ppm))
    return r3.render(m, cam, x, y, heading, paint, ambient=ambient, min_area=0.8)


def roof_sensor(cam, x, y):
    """A lidar on the roof of the ego vehicle, as robotaxis carry."""
    lx, ly = cam(x, y - 0.2, 1.62)
    return [
        f'<circle class="pulse" cx="{lx:.1f}" cy="{ly:.1f}" r="9" fill="{GREEN}" fill-opacity="0.35" filter="url(#soft)"/>',
        f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="7" ry="4.5" fill="#1d2126" stroke="{GREEN}" stroke-width="1.3"/>',
    ]


def scene(cam, W, H, models) -> list[str]:
    rnd = random.Random(4600)
    out = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    out += road(cam) + lidar(cam, rnd) + overlays(cam)
    things = []  # (depth, svg parts), drawn far to near
    for name, x, y, heading in TRAFFIC + [PARKED]:
        model = models[name]
        depth, polys = vehicle(cam, model, x, y, heading, TRAFFIC_PAINT[name], ambient=0.55)
        size = model.size()
        box = detection_box(cam, x, y, heading, (size[0] + 0.2, size[1] + 0.2, size[2] + 0.1))
        label = "parked minivan" if (name, x, y, heading) == PARKED else "car"
        lab = tag(cam, (x, y, size[2] + 0.6), label, GREEN)
        things.append((depth, polys + box + lab))
    ped = cylinder(cam, PED[0], PED[1], 0.35, 1.75, RED) + tag(
        cam, (PED[0], PED[1], 2.3), "pedestrian", "#ffb4ae"
    )
    things.append((cam.depth((PED[0], PED[1], 1)), ped))
    cx, cy = CYCLIST
    cyc = detection_box(cam, cx, cy, 0, (0.7, 1.8, 1.7)) + tag(cam, (cx, cy, 2.2), "cyclist", GREEN)
    things.append((cam.depth((cx, cy, 1)), cyc))
    for _, parts in sorted(things, key=lambda t: -t[0]):
        out += parts
    sx, sy = cam(EGO[0], EGO[1], 0)
    out.append(
        f'<ellipse cx="{sx:.1f}" cy="{sy + 4:.1f}" rx="{cam.focal * 1.3 / max(cam.depth((EGO[0], EGO[1], 0)), 1):.0f}" ry="14" fill="#000" fill-opacity="0.45" filter="url(#soft)"/>'
    )
    out += vehicle(cam, models["kiri10"], EGO[0], EGO[1], 0.0, EGO_PAINT, 0.03)[1]
    out += roof_sensor(cam, EGO[0], EGO[1])
    out.append(f'<rect width="{W}" height="{H}" fill="url(#fog)"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    return out


def card(ax, ay, x, y, w, num, title, sub, src, color):
    h = 62
    ex = x if ax < x else x + w
    return [
        f'<path d="M{ax:.1f},{ay:.1f} L{ex:.1f},{y + 22:.1f}" stroke="{color}" stroke-width="1.4" fill="none" stroke-opacity="0.9"/>',
        f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="{color}" fill-opacity="0.25"/>',
        f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3.5" fill="{color}"/>',
        f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#111418" fill-opacity="0.92" stroke="{color}" stroke-opacity="0.75" stroke-width="1.2"/></g>',
        f'<circle cx="{x + 20}" cy="{y + 21}" r="10" fill="{color}"/>',
        text(x + 20, y + 25.5, num, 12, "#0d0f12", 800, "middle"),
        text(x + 38, y + 26, title, 14, "#f3f4f6", 650),
        text(x + 14, y + 44, sub, 11.5, "#b9bfc8"),
        text(x + 14, y + 57, src, 10.5, color, 650, extra='letter-spacing="0.2"'),
    ]


def note(x, y, w, num, title, sub, src, color):
    """A card without a leader line."""
    return card(x - 1, y + 22, x, y, w, num, title, sub, src, color)[3:]


def pill(x, y, s, color, size=11.5):
    w = tw(s, size) + 18
    return [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="22" rx="11" fill="#111418" fill-opacity="0.9" stroke="{color}" stroke-opacity="0.8" stroke-width="1.1"/>',
        text(x + w / 2, y + 15.5, s, size, "#eef0f3", 600, "middle"),
    ], w


def pills(x, y, labels, color):
    out = []
    for s in labels:
        parts, w = pill(x, y, s, color)
        out += parts
        x += w + 8
    return out


def stamp(x, y, size=11.5, label=STAMP):
    w = tw(label, size) + 34
    return [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="24" rx="12" fill="#2a2108" fill-opacity="0.92" stroke="{AMBER}" stroke-width="1.1"/>',
        f'<circle cx="{x + 14}" cy="{y + 12}" r="4" fill="{AMBER}"/>',
        text(x + 24, y + 16.5, label, size, AMBER, 650),
    ]


def svg(W, H, title, desc, body, rx=14):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{escape(title)}</title>\n<desc id="d">{escape(desc)}</desc>\n{DEFS}\n'
        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="{rx}"/></clipPath>\n<g clip-path="url(#clip)">\n'
        + "\n".join(body)
        + "\n</g>\n</svg>\n"
    )


def describe(v, odd) -> str:
    return (
        "Concept illustration, not output of the system. A white robotaxi on unmodified Autoware approaches "
        "a crosswalk in a city street; other cars are shown with the boxes a perception stack draws around "
        f"them. Autoware's planned path is red (rated {v['autoware']}). The independent safety monitor's "
        f"envelope, the vehicle's swept path over its stopping distance, is blue (ASIL {v['monitor']}) and "
        "ends at a stop wall before a pedestrian on the crosswalk. A parked minivan hides the kerb; the "
        "monitor limits speed so the vehicle can stop for someone stepping out. A dashed geofence marks the "
        f"edge of the operational design domain: {', '.join(odd)}. The safety monitor is not built yet; "
        "everything is a draft for engineering review."
    )


def banner(f: fx.Facts, v: dict, models) -> str:
    W, H = 1280, 460
    cam = r3.Camera(pos=(1.5, -26.0, 14.0), pitch=25, focal=800, cx=W / 2, cy=385)
    odd = [lim.tag for lim in f.limits.values()]
    b = scene(cam, W, H, models)
    b.append(
        text(36, 52, "Autoware Assurance Stack", 30, "#ffffff", 750, extra='letter-spacing="-0.3"')
    )
    b.append(
        text(
            36,
            80,
            "A UL 4600 safety case for driverless Autoware: Autoware drives, an independent monitor checks.",
            15,
            "#c9ced6",
        )
    )
    b += stamp(36, 96)
    ax, ay = cam(1.75, STOP_Y, 1.6)
    b += card(
        ax,
        ay,
        880,
        128,
        300,
        "1",
        "Stops before the crosswalk",
        "The monitor's envelope must stay clear",
        f"SG-02 · SG-06 · ASIL {v['monitor']}",
        BLUE2,
    )
    ax, ay = cam(9.5, 21, 0)
    b += card(
        ax,
        ay,
        940,
        262,
        300,
        "2",
        "Slows where it can't see",
        "Speed set for someone stepping out",
        f"FSR-06.02 · ASIL {v['fsr0602']}",
        GREY,
    )
    ax, ay = cam(1.75, 58, 0)
    b += card(
        ax,
        ay,
        36,
        236,
        270,
        "3",
        f"Autoware drives, {v['autoware']}",
        "Unmodified upstream, pinned",
        v["dq_qm"],
        "#ff8a80",
    )
    b += pills(36, 400, ["ODD"] + odd, VIOLET)
    return svg(W, H, "Autoware Assurance Stack: concept illustration", describe(v, odd), b)


def full(f: fx.Facts, v: dict, models) -> str:
    W, H = 1280, 720
    cam = r3.Camera(pos=(1.5, -18.0, 11.0), pitch=25, focal=960, cx=W / 2, cy=490)
    odd = [lim.tag for lim in f.limits.values()]
    b = scene(cam, W, H, models)
    b.append(f'<rect width="{W}" height="78" fill="#0b0d10" fill-opacity="0.82"/>')
    b.append(
        text(
            32,
            36,
            "Autoware drives. An independent safety monitor checks every command.",
            21,
            "#ffffff",
            700,
        )
    )
    x = 32
    for sw, label in [
        (f"fill:{RED};fill-opacity:.7", f"Autoware's plan ({v['autoware']})"),
        (
            f"fill:{BLUE};fill-opacity:.75;stroke:{BLUE2}",
            f"Monitor's envelope (ASIL {v['monitor']})",
        ),
        (f"fill:{GREEN};fill-opacity:.15;stroke:{GREEN}", "Detected road users"),
        ("fill:url(#hatch);stroke:#c4c8ce", "Occluded"),
        (f"fill:none;stroke:{VIOLET};stroke-dasharray:3 2", "Geofence (ODD edge)"),
    ]:
        b.append(f'<rect x="{x}" y="52" width="16" height="11" rx="2" style="{sw}"/>')
        b.append(text(x + 22, 62, label, 12.5, "#d7dbe0"))
        x += 40 + tw(label, 12.5)
    ax, ay = cam(1.75, STOP_Y, 1.6)
    b += card(ax, ay, 880, 150, 360, "1", "Stops before the crosswalk", "Something is in the swept path: geometry, not classification",
              f"SG-02 · SG-06 · FSR-06.01 · ASIL {v['fsr0601']} · {v['dq_sg06']}", BLUE2)  # fmt: skip
    ax, ay = cam(9.5, 21, 0)
    b += card(
        ax,
        ay,
        920,
        330,
        330,
        "2",
        "Slows where it can't see",
        "Speed set so it can stop for someone stepping out",
        f"FSR-06.02 · ASIL {v['fsr0602']}",
        GREY,
    )
    ax, ay = cam(1.75, 56, 0)
    b += card(
        ax,
        ay,
        32,
        330,
        330,
        "3",
        f"Autoware drives, and stays {v['autoware']}",
        "Perceives, plans, controls; unmodified upstream",
        f"{v['dq_qm']} · WP-C-04 EL-01",
        "#ff8a80",
    )
    b += note(
        32,
        420,
        330,
        "4",
        "If it can't drive on safely",
        "Stop in lane, hazard lights on; pull over first if it can",
        f"SG-07 · ASIL {v['sg07']} · {v['dq_mrc']}",
        AMBER,
    )
    b += pills(32, 98, ["ODD · WP-C-02"] + odd, VIOLET)
    gx, gy = cam(-16, GEOFENCE_Y, 0)
    b.append(
        f'<path d="M{gx:.1f},{gy:.1f} L150,120" stroke="{VIOLET}" stroke-width="1.1" stroke-dasharray="3 3" fill="none"/>'
    )
    b += stamp((W - tw(STAMP, 11.5) - 34) / 2, H - 40)
    return svg(
        W,
        H,
        "Autoware with an independent safety monitor: concept illustration",
        describe(v, odd),
        b,
    )


# ---------------------------------------------------------------- architecture strip and standards map
# Light and dark through prefers-color-scheme, like the figures of assurance/.

THEMED = {
    "bg": ("#ffffff", "#0d1117"),
    "ink": ("#14171c", "#eceef1"),
    "ink2": ("#4b525c", "#b9bfc8"),
    "ink3": ("#868d97", "#7f8792"),
    "line": ("#c9ced6", "#3a404a"),
    "card": ("#f5f6f8", "#161b22"),
    "acc": ("#2d55c8", "#86a2ff"),
    "accsoft": ("#e7ecfb", "#1e2742"),
    "case": ("#0f7d73", "#4fd1c1"),
    "casesoft": ("#e2f5f2", "#123330"),
    "amb": ("#a86d00", "#e7a52a"),
    "ambsoft": ("#fbf0d6", "#3a2e14"),
    "red": ("#b3261e", "#ff8b80"),
    "redsoft": ("#fbe5e2", "#3d1c1a"),
}
ASIL_CLASS = {"QM": "qm", "A": "c", "B": "c", "C": "c", "D": "d"}


def themed_svg(W, H, title, desc, body):
    light = ";".join(f"--{k}:{v[0]}" for k, v in THEMED.items())
    dark = ";".join(f"--{k}:{v[1]}" for k, v in THEMED.items())
    style = f"""<style>
svg{{{light}}}
@media (prefers-color-scheme: dark){{svg{{{dark}}}}}
text{{font-family:{FONT};fill:var(--ink)}}
.h{{font-size:15px;font-weight:600}} .t{{font-size:12.5px;fill:var(--ink2)}} .s{{font-size:11px;fill:var(--ink3)}}
.b{{font-size:12px;font-weight:600}} .chip{{font-size:11px;font-weight:700}}
.card{{fill:var(--card);stroke:var(--line);stroke-width:1}}
.mon{{fill:var(--accsoft);stroke:var(--acc);stroke-width:1.5;stroke-dasharray:6 4}}
.case{{fill:var(--casesoft);stroke:var(--case);stroke-width:1.5}}
.bnd{{fill:none;stroke:var(--ink3);stroke-width:1;stroke-dasharray:4 4}}
.arr{{stroke:var(--ink2);stroke-width:1.6;fill:none;marker-end:url(#a)}}
.arr2{{stroke:var(--acc);stroke-width:1.4;fill:none;marker-end:url(#a2);stroke-dasharray:3 3}}
.qm{{fill:var(--card);stroke:var(--ink3)}} .d{{fill:var(--redsoft);stroke:var(--red)}} .c{{fill:var(--ambsoft);stroke:var(--amb)}}
.qmt{{fill:var(--ink2)}} .dt{{fill:var(--red)}} .ct{{fill:var(--amb)}}
.wp{{fill:var(--bg);stroke:var(--line)}}
.st-D{{fill:var(--amb)}} .st-S{{fill:none;stroke:var(--ink3);stroke-dasharray:2 1.5}} .st-R{{fill:none;stroke:var(--amb);stroke-width:1.5}}
.st-A{{fill:#23875a}} .st-B{{fill:#23875a;stroke:var(--ink);stroke-width:1.2}}
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--ink2)"/></marker>
<marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--acc)"/></marker></defs>"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{escape(title)}</title>\n<desc id="d">{escape(desc)}</desc>\n{style}\n'
        f'<rect width="{W}" height="{H}" rx="10" fill="var(--bg)" stroke="var(--line)"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def ttext(x, y, s, cls="t", anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{x:g}" y="{y:g}" class="{cls}"{a}>{escape(s)}</text>'


def chip(x, y, label, asil):
    kind = ASIL_CLASS[asil]
    w = 7 * len(label) + 16
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="10" class="{kind}"/>',
        ttext(x + w / 2, y + 14, label, f"chip {kind}t", "middle"),
    ]


def box(x, y, w, h, title, lines, cls="card"):
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>',
        ttext(x + 12, y + 22, title, "b"),
    ]
    return out + [ttext(x + 12, y + 42 + 16 * i, ln, "s") for i, ln in enumerate(lines)]


def asil_label(asil: str) -> str:
    return asil if asil == "QM" else f"ASIL {asil}"


ARCH_WPS = [  # work product -> short label on the strip
    ("WP-C-01", "Item"),
    ("WP-C-02", "ODD"),
    ("WP-C-03", "HARA"),
    ("WP-C-04", "Safety concept"),
    ("WP-C-05", "SOTIF"),
    ("WP-C-09", "Cybersecurity"),
    ("WP-C-11", "AI safety"),
    ("WP-C-12", "Fallback"),
]
STATUS_NAME = {
    "S": "Skeleton",
    "D": "Draft",
    "R": "In review",
    "A": "Approved",
    "B": "Baselined",
    "N/A": "N/A",
}


def architecture(f: fx.Facts, v: dict) -> str:
    reg = {p.wid: p for p in wpregister.load().products}
    W, H = 900, 470
    b = [
        ttext(24, 34, "Doer and checker: how the driverless system is built", "h"),
        ttext(
            24,
            54,
            "Autoware drives. An independent safety monitor checks every command and can stop the vehicle on its own.",
            "t",
        ),
        '<rect x="16" y="120" width="616" height="186" rx="12" class="bnd"/>',
        ttext(28, 137, "THE ITEM (WP-C-01)", "s"),
    ]
    b += box(
        30,
        148,
        158,
        112,
        "Sensors",
        [
            "LiDAR, camera, radar,",
            "GNSS, IMU for Autoware",
            "+ the monitor's own set",
            f"({v['dq_sensors']})",
        ],
    )
    b += box(
        210,
        148,
        180,
        112,
        "Autoware",
        ["Perceives, plans, controls", "Unmodified upstream,", "pinned in autoware.repos"],
    )
    b += chip(222, 232, asil_label(v["autoware"]), v["autoware"])
    b += box(
        420,
        148,
        196,
        112,
        "Safety monitor",
        ["Own hardware and sensors", "Checks commands against", "a safety envelope"],
        "mon",
    )
    b += chip(432, 232, asil_label(v["monitor"]), v["monitor"])
    b.append(ttext(604, 250, "not built yet", "s", "end"))
    b += box(
        670,
        148,
        210,
        112,
        "Vehicle drive-by-wire",
        ["Brakes, steering, propulsion", "Outside the item;", "vehicle chosen at G2"],
    )
    b += chip(682, 232, asil_label(v["dbw"]), v["dbw"])
    b.append(ttext(868, 276, f"required of the supplier ({v['dbw_aou']})", "s", "end"))
    b += box(420, 72, 196, 36, "Remote operations", [])
    b += chip(544, 80, asil_label(v["remote"]), v["remote"])
    b += [
        '<path d="M188,204 L208,204" class="arr"/>',
        '<path d="M390,204 L418,204" class="arr"/>',
        '<path d="M616,204 L668,204" class="arr"/>',
        '<path d="M518,108 L518,146" class="arr"/>',
        '<path d="M105,262 C105,292 518,292 518,264" class="arr2"/>',
        ttext(312, 298, "independent sensing path, not through Autoware", "s", "middle"),
        '<rect x="16" y="322" width="868" height="132" rx="12" class="case"/>',
        ttext(28, 344, "ASSURANCE: the concept work products, with their status in WP-M-00", "s"),
    ]
    x = 28
    for wid, label in ARCH_WPS:
        prod = reg.get(wid)
        if prod is None:
            raise fx.FactError(f"WP-M-00: no work product {wid}")
        b.append(f'<rect x="{x}" y="356" width="98" height="52" rx="6" class="wp"/>')
        b.append(ttext(x + 49, 374, label, "b", "middle"))
        b.append(ttext(x + 49, 389, wid, "s", "middle"))
        b.append(
            f'<rect x="{x + 22}" y="395" width="8" height="8" rx="2" class="st-{prod.status if prod.status != "N/A" else "S"}"/>'
        )
        b.append(ttext(x + 34, 403, STATUS_NAME[prod.status], "s"))
        x += 106
    case = reg.get("WP-K-01")
    b.append(
        ttext(
            450,
            438,
            f"all feed the UL 4600 safety case, WP-K-01 ({STATUS_NAME[case.status].lower() if case else 'missing'})",
            "t",
            "middle",
        )
    )
    desc = (
        f"Sensors feed Autoware, rated {v['autoware']}, which sends its commands through an independent safety monitor, "
        f"{asil_label(v['monitor'])} and not built yet, to the vehicle drive-by-wire, {asil_label(v['dbw'])} required of "
        f"the supplier. Remote operations, {asil_label(v['remote'])}, also send their commands through the monitor. The "
        "monitor has its own sensors. Below, the concept work products with their status in the register; they feed "
        "the UL 4600 safety case."
    )
    return themed_svg(W, H, "Doer and checker architecture", desc, b)


STANDARD_QUESTIONS = {  # the plain question each framework answers here (WP-M-01 §4)
    "ISO 26262": ("What if it fails?", "malfunctions, ASILs"),
    "ISO 21448": ("Is it good enough?", "performance limits"),
    "ISO/SAE 21434": ("What if it's attacked?", "remote link, updates"),
    "ISO/PAS 8800": ("Can the ML be trusted?", "perception models, data"),
    "Automotive SPICE 4.0": ("Is the process capable?", "engineering processes"),
}


def standards(f: fx.Facts) -> str:
    if (
        not f.standards
        or f.standards[0] != "UL 4600"
        or set(f.standards[1:]) != set(STANDARD_QUESTIONS)
    ):
        raise fx.FactError(
            f"WP-M-01 §4 lists {', '.join(f.standards)}; the standards map expects UL 4600 and {', '.join(STANDARD_QUESTIONS)}"
        )
    W, H = 900, 250
    b = [
        ttext(24, 34, "One safety case, five sources of evidence", "h"),
        '<rect x="24" y="52" width="852" height="58" rx="10" class="case"/>',
        ttext(450, 76, "UL 4600 · the safety case", "b", "middle"),
        ttext(
            450,
            96,
            "Is the driverless system acceptably safe across its whole ODD and lifecycle, with no driver to fall back on?",
            "t",
            "middle",
        ),
    ]
    x = 24
    for name in f.standards[1:]:
        q, sub = STANDARD_QUESTIONS[name]
        b.append(f'<rect x="{x}" y="150" width="162" height="78" rx="8" class="card"/>')
        b.append(ttext(x + 81, 174, name.replace("Automotive SPICE", "ASPICE"), "b", "middle"))
        b.append(ttext(x + 81, 194, q, "t", "middle"))
        b.append(ttext(x + 81, 212, sub, "s", "middle"))
        b.append(f'<path d="M{x + 81},148 L{x + 81},114" class="arr"/>')
        x += 172
    b.append(ttext(876, 136, "evidence", "s", "end"))
    desc = (
        "UL 4600 is the safety case. Five frameworks feed evidence into it: "
        + "; ".join(f"{n}, {STANDARD_QUESTIONS[n][1]}" for n in f.standards[1:])
        + ". As set out in WP-M-01 §4."
    )
    return themed_svg(W, H, "Standards map", desc, b)


# ---------------------------------------------------------------- wiki figures: the item, the minimal risk condition


def look_at(pos, target, pitch, focal, cx, cy):
    """A camera at `pos` turned towards `target` in the horizontal plane, pitched down by `pitch`."""
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    return r3.Camera(
        pos=pos, pitch=pitch, focal=focal, cx=cx, cy=cy, yaw=math.degrees(math.atan2(-dx, dy))
    )


def ground_grid(cam, x0, x1, y0, y1, step=1.0):
    out = []
    for i in range(int((x1 - x0) / step) + 1):
        x = x0 + i * step
        out.append(line(cam, (x, y0), (x, y1), "stroke:#2a2f36;stroke-width:1"))
    for j in range(int((y1 - y0) / step) + 1):
        y = y0 + j * step
        out.append(line(cam, (x0, y), (x1, y), "stroke:#2a2f36;stroke-width:1"))
    return out


def xray_box(cam, centre, size, color, label=None):
    """A translucent box seen through the body: where an element sits, roughly."""
    (x, y, z), (w, ln, h) = centre, size
    xs, ys, zs = (x - w / 2, x + w / 2), (y - ln / 2, y + ln / 2), (z - h / 2, z + h / 2)
    faces = [
        [
            (xs[0], ys[0], zs[1]),
            (xs[1], ys[0], zs[1]),
            (xs[1], ys[1], zs[1]),
            (xs[0], ys[1], zs[1]),
        ],
        [
            (xs[0], ys[0], zs[0]),
            (xs[0], ys[1], zs[0]),
            (xs[0], ys[1], zs[1]),
            (xs[0], ys[0], zs[1]),
        ],
        [
            (xs[0], ys[1], zs[0]),
            (xs[1], ys[1], zs[0]),
            (xs[1], ys[1], zs[1]),
            (xs[0], ys[1], zs[1]),
        ],
        [
            (xs[1], ys[0], zs[0]),
            (xs[1], ys[1], zs[0]),
            (xs[1], ys[1], zs[1]),
            (xs[1], ys[0], zs[1]),
        ],
    ]
    out = [
        poly(cam, f, f"fill:{color};fill-opacity:0.22;stroke:{color};stroke-width:1.4")
        for f in faces
    ]
    if label:
        out += tag(cam, (x, y, zs[1] + 0.25), label, color)
    return out


def element_rows(f: fx.Facts, in_item: bool) -> list[tuple[str, str, str]]:
    rows = []
    for e in f.elements.values():
        if e.in_item == in_item:
            note_ = f"required of others ({e.assumption})" if e.assumption else ""
            rows.append((e.eid, e.name, asil_label(e.asil) + (f" · {note_}" if note_ else "")))
    return rows


def item_figure(f: fx.Facts, v: dict, models) -> str:
    W, H = 1100, 520
    cam = look_at((-6.6, 7.2, 3.4), (0.0, 0.0), 15, 700, 345, 312)
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    b += ground_grid(cam, -4.0, 4.0, -4.0, 6.0)
    sx, sy = cam(0, 0, 0)
    b.append(
        f'<ellipse cx="{sx:.1f}" cy="{sy + 6:.1f}" rx="150" ry="30" fill="#000" fill-opacity="0.5" filter="url(#soft)"/>'
    )
    b += vehicle(cam, models["kiri10"], 0.0, 0.0, 0.0, EGO_PAINT, 0.025)[1]
    # elements of the item, at illustrative positions (the hardware is chosen with the vehicle)
    b += xray_box(cam, (0.0, -1.6, 0.75), (1.1, 0.6, 0.3), "#ff8a80", "Autoware computer")
    b += xray_box(cam, (0.0, -0.95, 0.62), (0.5, 0.35, 0.18), BLUE2, "Safety monitor")
    lx, ly = cam(0.0, -0.2, 1.62)
    b.append(
        f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="13" ry="7" fill="#1d2126" stroke="{GREEN}" stroke-width="1.6"/>'
    )
    b += tag(cam, (0.0, -0.2, 2.05), "Autoware's sensors", GREEN)
    for p in ((-0.7, 2.1, 0.55), (0.7, 2.1, 0.55)):
        px, py = cam(*p)
        b.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="{BLUE}" fill-opacity="0.5" stroke="{BLUE2}" stroke-width="1.4"/>'
        )
    b += tag(cam, (-0.7, 2.3, 0.15), "monitor's own sensors", BLUE2)
    b.append(text(28, 40, "The item: what the safety case is about", 22, "#ffffff", 700))
    b.append(
        text(
            28,
            64,
            "The sensors, the Autoware computer and the safety monitor are the item; the vehicle they drive is not (WP-C-01).",
            13.5,
            "#c9ced6",
        )
    )
    x0 = 690
    y = 110
    b.append(text(x0, y, "INSIDE THE ITEM", 11, "#9aa3ad", 700, extra='letter-spacing="1"'))
    y += 12
    for eid, name, rating in element_rows(f, True):
        b.append(
            f'<rect x="{x0}" y="{y}" width="380" height="40" rx="8" fill="#141820" stroke="#2c3440"/>'
        )
        b.append(text(x0 + 12, y + 17, f"{eid}  {name}", 13, "#f1f3f4", 650))
        b.append(text(x0 + 12, y + 33, rating, 11.5, BLUE2 if "ASIL" in rating else "#c9ced6"))
        y += 46
    y += 14
    b.append(
        text(
            x0,
            y,
            "OUTSIDE THE ITEM, BOUND BY AN ASSUMPTION",
            11,
            "#9aa3ad",
            700,
            extra='letter-spacing="1"',
        )
    )
    y += 12
    for eid, name, rating in element_rows(f, False):
        b.append(text(x0 + 2, y + 14, f"{eid}  {name}", 12.5, "#dfe2e6", 600))
        b.append(text(x0 + 380, y + 14, rating.split(" · ")[0], 12, AMBER, 650, "end"))
        y += 22
    b.append(
        text(
            x0,
            y + 16,
            f"Ratings derived in WP-C-04 §4; {v['dq_sensors']}: the monitor has its own sensors.",
            11,
            "#9aa3ad",
        )
    )
    b += stamp(
        28,
        H - 44,
        11,
        "ILLUSTRATION · positions are not decided; the hardware is chosen with the vehicle · draft",
    )
    desc = (
        "A white robotaxi seen from the front left, with the elements of the item drawn inside it at illustrative "
        "positions: the Autoware computer, the safety monitor, Autoware's roof sensor and the monitor's own sensors "
        "at the front. A list gives each element inside the item and outside it, with its rating from WP-C-04. "
        "The positions are not decided; everything is a draft for engineering review."
    )
    return svg(W, H, "The item", desc, b)


def mrc_figure(f: fx.Facts, v: dict, models) -> str:
    W, H = 1100, 470
    pw = W / 2
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    panels = [
        (
            "1",
            "Autoware pulls over when it still can",
            f"Its own minimal risk manoeuvre, rated {v['autoware']}",
            4.75,
            False,
            "#ff8a80",
        ),
        (
            "2",
            "If not: stopped and held in its lane",
            f"The rated condition: SG-07, ASIL {v['sg07']} ({v['dq_mrc']})",
            EGO[0],
            True,
            AMBER,
        ),
    ]
    for i, (num, title, sub, x, hazard, color) in enumerate(panels):
        ox = i * pw
        cam = r3.Camera(pos=(1.2, -12.0, 7.5), pitch=24, focal=560, cx=ox + pw / 2, cy=300)
        clip = f"panel{i}"
        b.append(
            f'<clipPath id="{clip}"><rect x="{ox + 12}" y="96" width="{pw - 24}" height="300" rx="12"/></clipPath>'
        )
        b.append(f'<g clip-path="url(#{clip})">')
        b.append(f'<rect x="{ox}" y="96" width="{pw}" height="300" fill="#15181d"/>')
        b += road(cam)
        b.append(
            poly(
                cam,
                [(3.6, -10, 0), (7.5, -10, 0), (7.5, 30, 0), (3.6, 30, 0)],
                "fill:#ffffff;fill-opacity:0.02",
            )
        )
        oncoming = vehicle(
            cam, models["sedan"], -1.75, 24.0, 180.0, TRAFFIC_PAINT["sedan"], ambient=0.55
        )[1]
        b += oncoming
        paint = r3.Paint(
            body=EGO_PAINT.body, indicator=(255, 176, 32) if hazard else EGO_PAINT.indicator
        )
        b += vehicle(cam, models["kiri10"], x, 6.0, 0.0, paint, 0.03)[1]
        if hazard:
            for dx, dy in ((-0.8, 8.1), (0.8, 8.1), (-0.8, 3.9), (0.8, 3.9)):
                hx, hy = cam(x + dx, dy, 0.75)
                b.append(
                    f'<circle class="pulse" cx="{hx:.1f}" cy="{hy:.1f}" r="9" fill="{AMBER}" fill-opacity="0.55" filter="url(#soft)"/>'
                )
        else:
            pts = [
                (EGO[0], 0.0, 0.02),
                (EGO[0] + 0.6, 2.0, 0.02),
                (x - 0.4, 4.0, 0.02),
                (x, 6.0, 0.02),
            ]
            d = " ".join(
                f"{'M' if k == 0 else 'L'}{a:.1f} {c:.1f}"
                for k, (a, c) in enumerate(cam(*p) for p in pts)
            )
            b.append(
                f'<path d="{d}" stroke="#ff8a80" stroke-width="3" stroke-dasharray="7 5" fill="none" stroke-opacity="0.9"/>'
            )
        b.append(
            f'<rect x="{ox + 12}" y="96" width="{pw - 24}" height="300" rx="12" fill="url(#vignette)"/>'
        )
        b.append("</g>")
        b.append(
            f'<rect x="{ox + 12}" y="96" width="{pw - 24}" height="300" rx="12" fill="none" stroke="{color}" stroke-opacity="0.6"/>'
        )
        b.append(f'<circle cx="{ox + 36}" cy="{124}" r="11" fill="{color}"/>')
        b.append(text(ox + 36, 128.5, num, 12.5, "#0d0f12", 800, "middle"))
        b.append(text(ox + 56, 129, title, 15, "#ffffff", 650))
        b.append(text(ox + 56, 148, sub, 12, "#c9ced6"))
    b.append(text(28, 40, "When it can no longer drive on safely", 22, "#ffffff", 700))
    b.append(
        text(
            28,
            64,
            "No driver takes over: the vehicle reaches a minimal risk condition by itself.",
            13.5,
            "#c9ced6",
        )
    )
    b.append(text(28, 424, "Safe state of SG-07 (WP-C-03):", 12, "#9aa3ad", 650))
    words, ln, lines_ = v["sg07_safe_state"].split(), "", []
    for w_ in words:
        if tw(ln + " " + w_, 12) > 820 and ln:
            lines_.append(ln)
            ln = w_
        else:
            ln = f"{ln} {w_}".strip()
    lines_.append(ln)
    for k, ln in enumerate(lines_[:2]):
        b.append(text(222, 424 + 16 * k, ln, 12, "#dfe2e6"))
    b += stamp(
        W - tw("ILLUSTRATION · draft for engineering review", 11) - 62,
        22,
        11,
        "ILLUSTRATION · draft for engineering review",
    )
    desc = (
        "Two panels. Left: the robotaxi has pulled over to the kerb, Autoware's own minimal risk manoeuvre. Right: "
        "the robotaxi is stopped in its lane with its hazard lights flashing, the rated minimal risk condition of "
        f"safety goal SG-07. Below, the safe state as WP-C-03 states it: {v['sg07_safe_state']}"
    )
    return svg(W, H, "Minimal risk condition", desc, b)


# ---------------------------------------------------------------- wiki figures: ODD, two questions, remote driving


def wrap(s: str, size: float, width: float) -> list[str]:
    words, line_, out = s.split(), "", []
    for w in words:
        if line_ and tw(f"{line_} {w}", size) > width:
            out.append(line_)
            line_ = w
        else:
            line_ = f"{line_} {w}".strip()
    return out + ([line_] if line_ else [])


def panel_frame(b, i, ox, top, pw, ph, color):
    """Open a clipped panel; returns the id so the caller can close it with </g>."""
    clip = f"p{i}"
    b.append(
        f'<clipPath id="{clip}"><rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" rx="12"/></clipPath>'
    )
    b.append(
        f'<g clip-path="url(#{clip})"><rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" fill="#15181d"/>'
    )
    band = f'<rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="42" fill="#0b0d10" fill-opacity="0.72"/>'
    return (
        band
        + f'<rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" rx="12" fill="none" stroke="{color}" stroke-opacity="0.6"/>'
    )


def sign(cam, x, y, value, ring, k=2.2):
    """A US speed limit sign on a post, facing the camera; drawn `k` times life size to be legible."""
    w, h, z = 0.32 * k, 0.42 * k, 1.6 + 0.42 * k
    out = [line(cam, (x, y, 0), (x, y, z), "stroke:#9aa0a6;stroke-width:2")]
    out.append(
        poly(
            cam,
            [(x - w, y, z - h), (x + w, y, z - h), (x + w, y, z + h), (x - w, y, z + h)],
            f"fill:#f4f5f7;stroke:{ring};stroke-width:3",
        )
    )
    cx_, cy_ = cam(x, y, z)
    scale = cam.focal / max(cam.depth((x, y, z)), 1.0)
    out.append(
        text(
            cx_,
            cy_ - 0.2 * k * scale,
            "SPEED LIMIT",
            max(4.0, 0.1 * k * scale),
            "#111",
            700,
            "middle",
        )
    )
    out.append(
        text(cx_, cy_ + 0.25 * k * scale, value, max(6.0, 0.36 * k * scale), "#111", 800, "middle")
    )
    return out


def rain(ox, top, pw, ph, n, rnd):
    d = "".join(
        f"M{ox + rnd.uniform(0, pw):.0f} {top + rnd.uniform(0, ph):.0f}l-4 14" for _ in range(n)
    )
    return f'<path d="{d}" stroke="#b8c7e0" stroke-opacity="0.45" stroke-width="1.2" fill="none"/>'


def odd_figure(f: fx.Facts, v: dict, models) -> str:
    W, H, top, ph = 1200, 560, 92, 270
    rows = [f.odd[k] for k in ("ODD-03", "ODD-10", "ODD-11")]
    speed_in = re.search(r"(\d+) mph", rows[0].inside)
    speed_out = re.search(r"(\d+) mph", rows[0].outside)
    if not (speed_in and speed_out):
        raise fx.FactError("WP-C-02 ODD-03 no longer gives the speeds in mph")
    rnd = random.Random(34503)
    b = [
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
        '<defs><linearGradient id="fogv" x1="0" y1="1" x2="0" y2="0"><stop offset="0.25" stop-color="#c9ced6" stop-opacity="0"/>'
        '<stop offset="0.75" stop-color="#c9ced6" stop-opacity="0.85"/></linearGradient></defs>',
    ]
    pw = (W - 48) / 3
    for i, row in enumerate(rows):
        ox = 12 + i * (pw + 12)
        border = panel_frame(b, i, ox, top, pw, ph, VIOLET)
        cam = r3.Camera(pos=(1.0, -12.0, 6.0), pitch=17, focal=430, cx=ox + pw / 2, cy=top + 165)
        b += road(cam)
        b += vehicle(cam, models["kiri10"], EGO[0], 0.0, 0.0, EGO_PAINT, 0.04)[1]
        if i == 0:
            b += sign(cam, 5.2, 9.0, speed_in.group(1), "#2fbf71")
            b.append(
                poly(
                    cam,
                    [(-40, 24, 0), (40, 24, 0), (40, 24, 3), (-40, 24, 3)],
                    "fill:url(#curtain)",
                )
            )
            b.append(
                line(
                    cam, (-40, 24), (40, 24), f"stroke:{VIOLET};stroke-width:2;stroke-dasharray:9 6"
                )
            )
            b += sign(cam, 5.2, 30.0, speed_out.group(1), RED)
            b += tag(cam, (-4.0, 24, 3.2), "geofence: the route stays inside", VIOLET)
        elif i == 1:
            b.append(rain(ox, top, pw, ph, 260, rnd))
        else:
            b.append(
                f'<rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" fill="url(#fogv)"/>'
            )
        b.append(
            f'<rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" fill="url(#vignette)"/>'
        )
        b.append("</g>")
        b.append(border)
        b.append(text(ox + 16, top + 26, f"{row.oid} · {row.attribute}", 14.5, "#ffffff", 700))
        y = top + ph + 26
        for label, body, col in (
            ("Inside", row.inside, "#2fbf71"),
            ("Outside", row.outside, "#ff8a80"),
        ):
            b.append(text(ox + 4, y, label.upper(), 10.5, col, 700, extra='letter-spacing="1"'))
            for k, ln in enumerate(wrap(body, 12.5, pw - 10)[:3]):
                b.append(text(ox + 4, y + 17 + 16 * k, ln, 12.5, "#e3e6ea"))
            y += 17 + 16 * min(3, len(wrap(body, 12.5, pw - 10))) + 10
        mon = row.detected_by.split()[0]
        b.append(
            text(
                ox + 4,
                y + 4,
                f"Detected by {mon} ({f.monitors.get(mon, '?')}) · {row.state.split(';')[0]}",
                11.5,
                VIOLET,
            )
        )
    b.append(text(28, 40, "Inside and outside the ODD", 22, "#ffffff", 700))
    b.append(
        text(
            28,
            64,
            "Anything the vehicle cannot handle must be outside the ODD, or it must notice and reach a minimal risk condition by itself.",
            13.5,
            "#c9ced6",
        )
    )
    b += stamp(
        W - tw("ILLUSTRATION · draft for engineering review", 11) - 62,
        22,
        11,
        "ILLUSTRATION · draft for engineering review",
    )
    desc = (
        "Three panels of the robotaxi on a city street. Speed: a "
        f"{speed_in.group(1)} mph sign inside the geofence and a {speed_out.group(1)} mph sign beyond it. Rain. Fog. "
        "Under each, the inside and outside of the attribute as WP-C-02 states it, and the monitor that detects it."
    )
    return svg(W, H, "Inside and outside the ODD", desc, b)


def two_ways_figure(f: fx.Facts, v: dict, models) -> str:
    W, H, top, ph = 1200, 500, 92, 300
    glare = f.odd["ODD-12"].outside.split(";")[-1].strip()
    if "glare" not in glare:
        raise fx.FactError("WP-C-02 ODD-12 no longer names glare as a triggering condition")
    b = [
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
        '<defs><radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff6d8" stop-opacity="1"/>'
        '<stop offset="0.25" stop-color="#ffe7a3" stop-opacity="0.75"/><stop offset="1" stop-color="#ffcf6e" stop-opacity="0"/></radialGradient></defs>',
    ]
    pw = (W - 36) / 2
    panels = [
        (
            "ISO 26262",
            STANDARD_QUESTIONS["ISO 26262"][0],
            "A part fails",
            f"For example SG-01: {v['sg01_text'].lower()}",
            f"ASIL {v['sg01']} · WP-C-03",
            RED,
        ),
        (
            "ISO 21448",
            STANDARD_QUESTIONS["ISO 21448"][0],
            "Nothing fails, but it is not good enough",
            f"For example: {glare}",
            "SOTIF · WP-C-02 ODD-12",
            AMBER,
        ),
    ]
    for i, (std, q, title, sub, src, col) in enumerate(panels):
        ox = 12 + i * (pw + 12)
        border = panel_frame(b, i, ox, top, pw, ph, col)
        cam = r3.Camera(pos=(1.0, -12.0, 6.0), pitch=17, focal=520, cx=ox + pw / 2, cy=top + 172)
        b += road(cam)
        if i == 0:
            arrow = [cam(EGO[0], y, 0.03) for y in (3.0, 16.0)]
            b.append(
                f'<path d="M{arrow[0][0]:.1f} {arrow[0][1]:.1f}L{arrow[1][0]:.1f} {arrow[1][1]:.1f}" stroke="{RED}" stroke-width="7" stroke-opacity="0.7" fill="none" marker-end="url(#ah)"/>'
            )
            b.append(
                f'<defs><marker id="ah" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>'
            )
            b += vehicle(cam, models["kiri10"], EGO[0], 0.0, 0.0, EGO_PAINT, 0.035)[1]
            sx, sy = cam(EGO[0], -0.4, 0.9)
            b.append(
                f'<circle class="pulse" cx="{sx:.1f}" cy="{sy:.1f}" r="16" fill="{RED}" fill-opacity="0.55" filter="url(#soft)"/>'
            )
            b += tag(cam, (EGO[0] - 1.6, -1.0, 1.9), "fault", "#ffb4ae")
        else:
            hx, hy = cam(-6, 120, 6)
            b.append(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="150" fill="url(#sun)"/>')
            b += cylinder(cam, PED[0], PED[1], 0.35, 1.75, "#ffffff")
            px, py = cam(PED[0], PED[1], 0.9)
            b.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="70" fill="url(#sun)" opacity="0.8"/>')
            b += detection_box(cam, PED[0], PED[1], 0, (0.9, 0.9, 1.9), AMBER)
            b += tag(cam, (PED[0], PED[1], 2.4), "not detected?", AMBER)
            b += vehicle(cam, models["kiri10"], EGO[0], 0.0, 0.0, EGO_PAINT, 0.035)[1]
        b.append(
            f'<rect x="{ox:.0f}" y="{top}" width="{pw:.0f}" height="{ph}" fill="url(#vignette)"/>'
        )
        b.append("</g>")
        b.append(border)
        b.append(text(ox + 16, top + 28, f"{std} · {q}", 15, "#ffffff", 700))
        b.append(text(ox + 16, top + ph + 28, title, 15, col, 700))
        for k, ln in enumerate(wrap(sub, 12.5, pw - 20)[:2]):
            b.append(text(ox + 16, top + ph + 48 + 16 * k, ln, 12.5, "#e3e6ea"))
        b.append(text(ox + 16, top + ph + 86, src, 11.5, col, 650))
    b.append(text(28, 40, "Two ways to be unsafe", 22, "#ffffff", 700))
    b.append(
        text(
            28,
            64,
            "Functional safety asks what happens when something fails; SOTIF asks what happens when nothing fails but the function is not good enough.",
            13.5,
            "#c9ced6",
        )
    )
    b += stamp(
        W - tw("ILLUSTRATION · draft for engineering review", 11) - 62,
        22,
        11,
        "ILLUSTRATION · draft for engineering review",
    )
    desc = (
        f"Left, ISO 26262: a fault makes the robotaxi accelerate when nothing asked it to; safety goal SG-01, {v['sg01_text']}, "
        f"ASIL {v['sg01']}. Right, ISO 21448: nothing has failed, but low sun dazzles the sensors and a pedestrian on the "
        f"crosswalk may not be detected; WP-C-02 says {glare}."
    )
    return svg(W, H, "Two ways to be unsafe", desc, b)


def operator_station(x, y):
    """A remote operations desk: three screens and an operator, drawn flat."""
    return [
        f'<rect x="{x}" y="{y + 70}" width="190" height="12" rx="3" fill="#2a2f37"/>',
        *[
            f'<rect x="{x + 8 + 60 * i}" y="{y + 18}" width="54" height="36" rx="4" fill="#1d2633" stroke="{BLUE2}" stroke-width="1.2"/>'
            for i in range(3)
        ],
        *[
            f'<rect x="{x + 30 + 60 * i}" y="{y + 54}" width="10" height="16" fill="#2a2f37"/>'
            for i in range(3)
        ],
        f'<circle cx="{x + 95}" cy="{y + 96}" r="13" fill="#3a4250"/>',
        f'<path d="M{x + 70} {y + 140} Q{x + 95} {y + 105} {x + 120} {y + 140} Z" fill="#3a4250"/>',
        text(x + 95, y + 162, "Remote operations centre", 12.5, "#dfe2e6", 650, "middle"),
    ]


def note2(x, y, w, num, title, sub, src, color):
    """A card with up to two lines of body text."""
    lines_ = wrap(sub, 11.5, w - 28)[:2]
    h = 50 + 15 * len(lines_)
    out = [
        f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#111418" fill-opacity="0.92" stroke="{color}" stroke-opacity="0.75" stroke-width="1.2"/></g>',
        f'<circle cx="{x + 20}" cy="{y + 21}" r="10" fill="{color}"/>',
        text(x + 20, y + 25.5, num, 12, "#0d0f12", 800, "middle"),
        text(x + 38, y + 26, title, 14, "#f3f4f6", 650),
    ]
    out += [text(x + 14, y + 44 + 15 * k, ln, 11.5, "#b9bfc8") for k, ln in enumerate(lines_)]
    out.append(
        text(
            x + 14,
            y + 44 + 15 * len(lines_) + 2,
            src,
            10.5,
            color,
            650,
            extra='letter-spacing="0.2"',
        )
    )
    return out


def remote_figure(f: fx.Facts, v: dict, models) -> str:
    W, H = 1200, 490
    cam = r3.Camera(pos=(-2.0, -11.0, 6.5), pitch=20, focal=620, cx=760, cy=300)
    b = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
    b += road(cam)
    b += vehicle(cam, models["kiri10"], EGO[0], 6.0, 0.0, EGO_PAINT, 0.03)[1]
    ax, ay = cam(EGO[0], 5.6, 1.7)
    b.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="4" fill="{GREEN}"/>')
    b += operator_station(70, 190)
    mx, my = 470, 250  # the monitor on the command path
    b.append(
        f'<path d="M262 245 C330 200 400 200 {mx - 46} {my - 6}" stroke="{BLUE2}" stroke-width="2.2" stroke-dasharray="6 5" fill="none" class="pulse"/>'
    )
    b.append(
        f'<path d="M{mx + 46} {my - 6} C560 180 {ax - 60:.0f} {ay - 50:.0f} {ax:.1f} {ay:.1f}" stroke="{BLUE2}" stroke-width="2.2" stroke-dasharray="6 5" fill="none" class="pulse"/>'
    )
    b.append(
        f'<g filter="url(#shadow)"><rect x="{mx - 46}" y="{my - 30}" width="92" height="48" rx="10" fill="#111a2b" stroke="{BLUE}" stroke-width="1.6"/></g>'
    )
    b.append(text(mx, my - 9, "Safety monitor", 12, "#ffffff", 700, "middle"))
    b.append(text(mx, my + 8, f"ASIL {v['monitor']}", 11, BLUE2, 650, "middle"))
    b.append(
        text(
            mx,
            my + 34,
            "on the vehicle; drawn apart to show the path",
            10.5,
            "#9aa3ad",
            400,
            "middle",
        )
    )
    b += note2(
        40,
        380,
        300,
        "1",
        "Remote operators may drive",
        v["dq_remote_title"],
        v["dq_remote"],
        "#d5d9df",
    )
    b += note2(
        356,
        380,
        400,
        "2",
        "Only fresh, intact commands",
        v["sg08_text"],
        f"SG-08 · ASIL {v['sg08']}",
        BLUE2,
    )
    safe = v["sg08_safe_state"][0].lower() + v["sg08_safe_state"][1:]
    b += note2(
        772,
        380,
        390,
        "3",
        "Otherwise it stops",
        f"{safe}; the link's loss or delay is watched by MON-04 ({f.monitors.get('MON-04', '?')})",
        "SG-08 safe state · WP-C-02 §4",
        AMBER,
    )
    b.append(text(28, 40, "Remote driving goes through the safety monitor", 22, "#ffffff", 700))
    b.append(
        text(
            28,
            64,
            "A remote operator's command is bounded like Autoware's: the monitor checks it, and stops the vehicle if it is stale or not the operator's.",
            13.5,
            "#c9ced6",
        )
    )
    b += stamp(W - tw(STAMP, 11) - 62, 84, 11)
    desc = (
        f"A remote operations centre sends driving commands over a wireless link; they pass through the safety monitor "
        f"(ASIL {v['monitor']}) before reaching the robotaxi. Cards: {v['dq_remote']}, {v['dq_remote_title']}; SG-08, "
        f"{v['sg08_text']}, ASIL {v['sg08']}; otherwise {v['sg08_safe_state'].lower()}, with MON-04 watching the link."
    )
    return svg(W, H, "Remote driving", desc, b)


def build() -> dict[Path, str]:
    f = fx.load()
    v = fx.need(f)
    models = {"kiri10": mesh.load_kiri(), **mesh.load_pack()}
    return {
        OUT / "hero.svg": banner(f, v, models),
        OUT / "scene.svg": full(f, v, models),
        OUT / "architecture.svg": architecture(f, v),
        OUT / "standards.svg": standards(f),
        OUT / "item.svg": item_figure(f, v, models),
        OUT / "minimal-risk-condition.svg": mrc_figure(f, v, models),
        OUT / "odd.svg": odd_figure(f, v, models),
        OUT / "two-ways-to-be-unsafe.svg": two_ways_figure(f, v, models),
        OUT / "remote-driving.svg": remote_figure(f, v, models),
    }


def main(argv: list[str] | None = None) -> int:
    try:
        outputs = build()
    except (fx.FactError, mesh.ModelError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return fx.fk.emit(outputs, argv, __doc__)


if __name__ == "__main__":
    sys.exit(main())
