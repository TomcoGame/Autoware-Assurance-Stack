#!/usr/bin/env python3
"""Vehicle models for the README figures: loaded from the two FBX files in models/, normalised,
classified into parts and simplified.

Every model comes out in the frame of the README scenes: x to the right, y forward, z up, in metres,
with the origin on the ground under the centre of the vehicle. Each triangle carries a part class
(body, glass, light_front, light_rear, wheel, trim) that the renderer colours; textures are not used.
Badges, number plates and the interior are dropped. Simplification clusters vertices on a grid and
drops the triangles that collapse, so a car of thousands of triangles becomes a few hundred.

Model-specific knowledge (which part is which, which way is forward) is kept in this file, next to
the code that applies it. Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

import fbx

MODELS = Path(__file__).resolve().parent / "models"
KIRI = MODELS / "kiri10.fbx"
PACK = MODELS / "generic-passenger-car-pack.fbx"
CLASSES = ("body", "glass", "light_front", "light_rear", "wheel", "trim")
Vec = tuple[float, float, float]


class ModelError(Exception):
    """A model file does not hold what this module expects of it."""


@dataclass
class Model:
    name: str
    vertices: list[Vec]
    triangles: list[tuple[int, int, int]]
    classes: list[str]  # one per triangle

    def bounds(self) -> tuple[Vec, Vec]:
        lo = tuple(min(v[i] for v in self.vertices) for i in range(3))
        hi = tuple(max(v[i] for v in self.vertices) for i in range(3))
        return lo, hi  # type: ignore[return-value]

    def size(self) -> Vec:
        lo, hi = self.bounds()
        return tuple(round(hi[i] - lo[i], 3) for i in range(3))  # type: ignore[return-value]


# ---------------------------------------------------------------- building a model


def _merge(name: str, parts: list[tuple[str, list[Vec], list[tuple[int, int, int]]]]) -> Model:
    verts: list[Vec] = []
    tris: list[tuple[int, int, int]] = []
    classes: list[str] = []
    for cls, pv, pt in parts:
        base = len(verts)
        verts += pv
        tris += [(a + base, b + base, c + base) for a, b, c in pt]
        classes += [cls] * len(pt)
    return Model(name, verts, tris, classes)


def ground_centre(m: Model) -> Model:
    """Move the model so that its lowest point is at z = 0, centred in x and y."""
    lo, hi = m.bounds()
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    return Model(
        m.name, [(x - cx, y - cy, z - lo[2]) for x, y, z in m.vertices], m.triangles, m.classes
    )


def simplify(m: Model, cell: float) -> Model:
    """Cluster vertices on a grid of `cell` metres, per part class so colours do not bleed, and drop
    the triangles that collapse to a line or a point."""
    key_to_index: dict[tuple, int] = {}
    sums: list[list[float]] = []
    remap: dict[tuple[str, int], int] = {}
    for t, cls in zip(m.triangles, m.classes):
        for vi in t:
            if (cls, vi) in remap:
                continue
            x, y, z = m.vertices[vi]
            key = (cls, round(x / cell), round(y / cell), round(z / cell))
            if key not in key_to_index:
                key_to_index[key] = len(sums)
                sums.append([0.0, 0.0, 0.0, 0])
            k = key_to_index[key]
            s = sums[k]
            s[0] += x
            s[1] += y
            s[2] += z
            s[3] += 1
            remap[(cls, vi)] = k
    verts = [(s[0] / s[3], s[1] / s[3], s[2] / s[3]) for s in sums]
    tris, classes, seen = [], [], set()
    for t, cls in zip(m.triangles, m.classes):
        a, b, c = (remap[(cls, vi)] for vi in t)
        if a == b or b == c or a == c:
            continue
        key = tuple(sorted((a, b, c)))
        if key in seen:
            continue
        seen.add(key)
        tris.append((a, b, c))
        classes.append(cls)
    return Model(m.name, verts, tris, classes)


# ---------------------------------------------------------------- Kiri '10 (the ego vehicle)

KIRI_DROP = ("interior", "Steering", "Badges", "Numberplate", "Inner", "Suspension")
KIRI_CLASS = [  # first match on the part name wins
    ("Headlights", "light_front"),
    ("blinkers", "light_front"),
    ("Brakelights", "light_rear"),
    ("Taillights", "light_rear"),
    ("Reverse", "light_rear"),
    ("Glass", "glass"),
    ("glass", "glass"),
    ("Windshield", "glass"),
    ("Wheel", "wheel"),
    ("Bottom", "trim"),
]


def load_kiri(path: Path = KIRI) -> Model:
    """Kiri '10: one car, y up, x forward, z to the right, in metres."""
    scene = fbx.meshes(fbx.parse(path.read_bytes()))
    parts = []
    for mesh in scene.meshes:
        if any(d in mesh.name for d in KIRI_DROP):
            continue
        cls = next((c for key, c in KIRI_CLASS if key in mesh.name), "body")
        verts = [(z, x, y) for x, y, z in mesh.vertices]  # right, forward, up
        parts.append((cls, verts, mesh.triangles))
    if not parts:
        raise ModelError(f"{path.name}: no mesh parts")
    return ground_centre(_merge("kiri10", parts))


# ---------------------------------------------------------------- Generic passenger car pack (traffic)

PACK_CARS = {  # body mesh name -> model name
    "Sedan Body": "sedan",
    "Hatchback Body": "hatchback",
    "Wagon Body": "wagon",
    "SUV Body": "suv",
    "minivan body": "minivan",
    "Compact Body": "compact",
}
PACK_CLASS = {"Body": "body", "Glass": "glass", "Optics": "light_front", "": "trim"}


def _inverse(m: list[list[float]]) -> list[list[float]]:
    """Inverse of an affine 4x4 matrix."""
    a = [row[:3] for row in m[:3]]
    det = (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )
    if abs(det) < 1e-12:
        raise ModelError("singular transform")
    inv = [
        [
            (
                a[(j + 1) % 3][(i + 1) % 3] * a[(j + 2) % 3][(i + 2) % 3]
                - a[(j + 1) % 3][(i + 2) % 3] * a[(j + 2) % 3][(i + 1) % 3]
            )
            / det
            for j in range(3)
        ]
        for i in range(3)
    ]
    t = [m[0][3], m[1][3], m[2][3]]
    it = [-sum(inv[i][k] * t[k] for k in range(3)) for i in range(3)]
    return [inv[0] + [it[0]], inv[1] + [it[1]], inv[2] + [it[2]], [0, 0, 0, 1]]


def _apply(m: list[list[float]], v: Vec) -> Vec:
    return tuple(m[r][0] * v[0] + m[r][1] * v[1] + m[r][2] * v[2] + m[r][3] for r in range(3))  # type: ignore[return-value]


def front_is_positive_y(verts: list[Vec]) -> bool:
    """A car's front is the end with the lower top: a bonnet is lower than a boot lid or tailgate."""
    ys = [v[1] for v in verts]
    lo, hi = min(ys), max(ys)
    band = (hi - lo) * 0.12
    top_pos = max(v[2] for v in verts if v[1] > hi - band)
    top_neg = max(v[2] for v in verts if v[1] < lo + band)
    return top_pos < top_neg


def load_pack(path: Path = PACK) -> dict[str, Model]:
    """The cars of the generic passenger car pack: each body with the four wheels nearest to it,
    brought into the body's own frame (z up, length along y, millimetres), then turned so that
    forward is +y and scaled to metres."""
    root = fbx.parse(path.read_bytes())
    world = fbx.meshes(root)
    local = fbx.meshes(root, local=True)
    wheels = [w for w in world.meshes if w.name.startswith("Wheel")]
    out = {}
    for wbody, lbody in zip(world.meshes, local.meshes):
        if wbody.name not in PACK_CARS:
            continue
        centre = _centroid(wbody.vertices)
        near = sorted(wheels, key=lambda w: _flat_dist(_centroid(w.vertices), centre))[:4]
        if len(near) < 4 or _flat_dist(_centroid(near[-1].vertices), centre) > 3500:
            raise ModelError(f"{path.name}: {wbody.name} does not have four wheels nearby")
        # wbody.matrix = W * G and lbody.matrix = G, so W^-1 = G * (W * G)^-1.
        to_local = _matmul(lbody.matrix, _inverse(wbody.matrix))
        parts = []
        for cls in CLASSES:
            tris = [
                t
                for t, mat in zip(lbody.triangles, lbody.materials)
                if PACK_CLASS.get(mat, "trim") == cls
            ]
            if tris:
                parts.append((cls, lbody.vertices, tris))
        for w in near:
            parts.append(("wheel", [_apply(to_local, v) for v in w.vertices], w.triangles))
        turn = (
            1 if front_is_positive_y(lbody.vertices) else -1
        )  # half a turn about z keeps handedness
        parts = [
            (cls, [(turn * x / 1000, turn * y / 1000, z / 1000) for x, y, z in pv], pt)
            for cls, pv, pt in parts
        ]
        name = PACK_CARS[wbody.name]
        out[name] = _rear_lights(ground_centre(_merge(name, parts)))
    missing = set(PACK_CARS.values()) - set(out)
    if missing:
        raise ModelError(f"{path.name}: missing {', '.join(sorted(missing))}")
    return out


def _centroid(vs: list[Vec]) -> Vec:
    return tuple(sum(v[i] for v in vs) / len(vs) for i in range(3))  # type: ignore[return-value]


def _flat_dist(a: Vec, b: Vec) -> float:
    """Horizontal distance in the pack's world frame, which has y up."""
    return math.hypot(a[0] - b[0], a[2] - b[2])


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _rear_lights(m: Model) -> Model:
    """The pack has one material for all lamps; those in the rear half are rear lights."""
    cls = []
    for t, c in zip(m.triangles, m.classes):
        if c == "light_front" and sum(m.vertices[i][1] for i in t) / 3 < 0:
            c = "light_rear"
        cls.append(c)
    return Model(m.name, m.vertices, m.triangles, cls)
