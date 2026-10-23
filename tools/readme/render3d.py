#!/usr/bin/env python3
"""Flat-shaded rendering of mesh.Model objects into SVG polygons.

A camera turns a world point (x right, y forward, z up, metres) into a screen point and a depth.
Each triangle facing the camera is shaded by one directional light and drawn back to front
(painter's algorithm), which is enough for convex-ish vehicles seen from outside. Coordinates are
rounded to 0.1 px so the output is deterministic and compact. Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from mesh import Model

Vec = tuple[float, float, float]


@dataclass
class Camera:
    """A pinhole camera at `pos`, looking along +y and pitched down by `pitch` degrees, then turned
    by `yaw` degrees to the left; `focal` in pixels; the principal point at (cx, cy)."""

    pos: Vec
    pitch: float
    focal: float
    cx: float
    cy: float
    yaw: float = 0.0

    def view(self, p: Vec) -> Vec:
        """(right, up, depth) of a world point in the camera frame."""
        dx, dy, dz = (p[i] - self.pos[i] for i in range(3))
        cy_, sy_ = math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw))
        dx, dy = dx * cy_ + dy * sy_, -dx * sy_ + dy * cy_
        ct, st = math.cos(math.radians(self.pitch)), math.sin(math.radians(self.pitch))
        return dx, dy * st + dz * ct, dy * ct - dz * st

    def __call__(self, x: float, y: float, z: float = 0.0) -> tuple[float, float]:
        r, u, d = self.view((x, y, z))
        d = max(d, 0.3)
        return self.cx + self.focal * r / d, self.cy - self.focal * u / d

    def depth(self, p: Vec) -> float:
        return self.view(p)[2]


@dataclass
class Paint:
    """Base colours per part class, as (r, g, b) in 0..255, and how strongly the light shades each."""

    body: tuple[int, int, int] = (226, 229, 233)
    glass: tuple[int, int, int] = (38, 48, 62)
    light_front: tuple[int, int, int] = (255, 244, 214)
    light_rear: tuple[int, int, int] = (226, 46, 40)
    indicator: tuple[int, int, int] = (255, 244, 214)  # amber when the hazard lights are on
    wheel: tuple[int, int, int] = (28, 30, 34)
    trim: tuple[int, int, int] = (46, 49, 54)

    def colour(self, cls: str, light: float) -> str:
        base = getattr(self, cls)
        if cls.startswith("light") or cls == "indicator":
            light = 1.0  # lamps are lit, not shaded
        elif cls == "glass":
            light = 0.55 + 0.6 * light  # glass shows mostly reflection
        r, g, b = (min(255, int(c * light)) for c in base)
        return f"#{r:02x}{g:02x}{b:02x}"


LIGHT = (-0.45, -0.55, 0.70)  # from the upper left, slightly towards the camera


def _norm(v: Vec) -> Vec:
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return (v[0] / n, v[1] / n, v[2] / n)


def place(m: Model, x: float, y: float, heading: float) -> list[Vec]:
    """World vertices of a model standing at (x, y), turned `heading` degrees to the left of +y."""
    c, s = math.cos(math.radians(heading)), math.sin(math.radians(heading))
    return [(x + vx * c - vy * s, y + vx * s + vy * c, vz) for vx, vy, vz in m.vertices]


def _fmt(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def render(
    m: Model,
    cam: Camera,
    x: float = 0.0,
    y: float = 0.0,
    heading: float = 0.0,
    paint: Paint | None = None,
    ambient: float = 0.42,
    cull: bool = True,
    min_area: float = 0.6,
    tones: int = 12,
    bands: int = 10,
) -> tuple[float, list[str]]:
    """The model as SVG paths, back to front, and its mean depth (to order several models).

    Triangles facing away from the camera are dropped (cull), as are those smaller than `min_area`
    square pixels; the light is rounded to `tones` steps. Faces are drawn back to front in `bands`
    slices of depth, each slice as one path per colour: within a slice the order between colours is
    lost, which a vehicle seen from outside does not show, and the output stays small."""
    paint = paint or Paint()
    light = _norm(LIGHT)
    world = place(m, x, y, heading)
    view = [cam.view(p) for p in world]
    screen = [cam(*p) for p in world]
    faces = []
    for (a, b, c), cls in zip(m.triangles, m.classes):
        if min(view[a][2], view[b][2], view[c][2]) < 0.5:
            continue
        (x1, y1), (x2, y2), (x3, y3) = screen[a], screen[b], screen[c]
        if abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2 < min_area:
            continue
        pa, pb, pc = world[a], world[b], world[c]
        n = _norm(
            (
                (pb[1] - pa[1]) * (pc[2] - pa[2]) - (pb[2] - pa[2]) * (pc[1] - pa[1]),
                (pb[2] - pa[2]) * (pc[0] - pa[0]) - (pb[0] - pa[0]) * (pc[2] - pa[2]),
                (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]),
            )
        )
        centre = tuple((pa[i] + pb[i] + pc[i]) / 3 for i in range(3))
        to_cam = _norm(tuple(cam.pos[i] - centre[i] for i in range(3)))
        if sum(n[i] * to_cam[i] for i in range(3)) < 0:
            if cull:
                continue
            n = (-n[0], -n[1], -n[2])
        lam = max(0.0, sum(n[i] * light[i] for i in range(3)))
        lam = round(lam * tones) / tones
        depth = (view[a][2] + view[b][2] + view[c][2]) / 3
        d = f"M{_fmt(x1)} {_fmt(y1)}L{_fmt(x2)} {_fmt(y2)}L{_fmt(x3)} {_fmt(y3)}Z"
        faces.append((depth, d, paint.colour(cls, ambient + (1 - ambient) * lam)))
    faces.sort(key=lambda f: -f[0])
    paths: list[str] = []
    if faces:
        near, far = faces[-1][0], faces[0][0]
        step = max((far - near) / bands, 1e-6)
        for b in range(bands):  # back to front; within a band, one path per colour
            lo, hi = far - (b + 1) * step, far - b * step
            group: dict[str, list[str]] = {}
            for depth, d, col in faces:
                if lo <= depth < hi or (b == bands - 1 and depth < hi) or (b == 0 and depth >= far):
                    group.setdefault(col, []).append(d)
            for col, ds in group.items():
                paths.append(
                    f'<path d="{"".join(ds)}" fill="{col}" stroke="{col}" stroke-width="0.5" stroke-linejoin="round"/>'
                )
    mean = sum(v[2] for v in view) / len(view)
    return mean, paths
