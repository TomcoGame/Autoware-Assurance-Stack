#!/usr/bin/env python3
"""Build a Blender scene from a scene description (tools/sim/scenes/<id>.json) and render it.

Runs inside Blender, either with the `bpy` module from PyPI or with Blender itself:

    python3 tools/sim/build_blend.py tools/sim/scenes/SC-01.json --out build/sim
    blender -b -P tools/sim/build_blend.py -- tools/sim/scenes/SC-01.json --out build/sim

It writes <id>.png (the still), <id>.manifest.json (what was built: the objects, where they are at
the still, every text on the frame, the Blender version and render settings), and optionally
<id>.mp4 (--animate) and <id>.blend (--blend). With --verify it compares the built scene against
the description and exits non-zero on a difference: every road user at the place the description
puts it, the stamp on the frame, every label of the description on the frame.

Everything the frame says comes from the description, which scene.py reads from the records; this
file types no label. The vehicles are the models of tools/readme/models/ (CC BY 4.0, see CREDITS.md),
loaded by tools/readme/mesh.py; everything else is drawn from primitives. The scene is a
qualitative illustration, not a simulation: positions follow the choreography of layouts.py, and
the monitor's envelope is drawn at a fixed length (ENVELOPE_M) that is not computed from anything.

The functions above `build()` are plain Python, so the unit tests run without Blender.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "readme"))

ENVELOPE_M = 14.0  # drawn length of the monitor's envelope at the clip's start speed; not computed
CRUISE_TO, STOP_AT = 0.45, 0.85  # the ego slows from CRUISE_TO and stands still from STOP_AT
W, H = 1600, 900
AMBER, BLUE, RED, GREEN, VIOLET, GREY = (
    (1.0, 0.81, 0.43),
    (0.36, 0.61, 1.0),
    (1.0, 0.30, 0.25),
    (0.26, 0.94, 0.54),
    (0.76, 0.55, 1.0),
    (0.84, 0.85, 0.87),
)
HUD_TEXT = (0.91, 0.92, 0.93)

# ---------------------------------------------------------------- geometry and motion (plain Python


def length(pts: list[list[float]]) -> float:
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def point_at(pts: list[list[float]], s: float) -> tuple[float, float, float]:
    """(x, y, heading) at distance s along a polyline; heading in radians to the left of +y."""
    if len(pts) == 1:
        return pts[0][0], pts[0][1], 0.0
    s = max(0.0, s)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        seg = math.dist(a, b)
        if s <= seg or i == len(pts) - 2:
            u = min(1.0, s / seg) if seg else 0.0
            heading = math.atan2(-(b[0] - a[0]), b[1] - a[1])
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, heading
        s -= seg
    raise AssertionError("unreachable")


def ego_speed_factor(u: float, stops: bool) -> float:
    """The ego's speed as a share of its sampled speed at clip fraction u."""
    if not stops or u <= CRUISE_TO:
        return 1.0
    if u >= STOP_AT:
        return 0.0
    return 1.0 - (u - CRUISE_TO) / (STOP_AT - CRUISE_TO)


def ego_share(u: float, stops: bool) -> float:
    """The share of its path the ego has covered at clip fraction u (the integral of the speed)."""
    if not stops:
        return u
    ramp = STOP_AT - CRUISE_TO
    total = CRUISE_TO + ramp / 2
    if u <= CRUISE_TO:
        return u / total
    v = min(u, STOP_AT) - CRUISE_TO
    return (CRUISE_TO + v - v * v / (2 * ramp)) / total


def ego_at(desc: dict, u: float) -> tuple[float, float, float]:
    pts = desc["ego"]["path"]
    return point_at(pts, length(pts) * ego_share(u, desc["ego"]["stops"]))


def envelope_at(desc: dict, u: float) -> float:
    """Drawn envelope length: ENVELOPE_M scaled by the square of the speed share, never below 1 m."""
    return max(1.0, ENVELOPE_M * ego_speed_factor(u, desc["ego"]["stops"]) ** 2)


def actor_at(actor: dict, u: float) -> tuple[float, float, float]:
    pts = actor["path"]
    if len(pts) == 1:
        return pts[0][0], pts[0][1], 0.0
    a, b = actor["move"]
    share = 0.0 if u <= a else 1.0 if u >= b else (u - a) / (b - a)
    return point_at(pts, length(pts) * share)


def still_frame(desc: dict, frames: int) -> int:
    return round(desc["still"] * (frames - 1))


def expected(desc: dict, frames: int) -> dict[str, list[float]]:
    """Where the description puts the ego and every road user at the still frame: name -> [x, y]."""
    u = still_frame(desc, frames) / (frames - 1)
    out = {"ego": [round(v, 2) for v in ego_at(desc, u)[:2]]}
    for i, a in enumerate(desc["actors"]):
        out[f"actor{i}-{a['class']}"] = [round(v, 2) for v in actor_at(a, u)[:2]]
    return out


def wrap(text: str, size: float, width: float) -> list[str]:
    """Greedy word wrap with a mean glyph width of 0.52 em, which fits Blender's default font."""
    words, lines, line = text.split(), [], ""
    per = max(1, int(width / (size * 0.52)))
    for w_ in words:
        if line and len(line) + 1 + len(w_) > per:
            lines.append(line)
            line = w_
        else:
            line = f"{line} {w_}" if line else w_
    if line:
        lines.append(line)
    return lines


def hud_texts(desc: dict) -> list[dict]:
    """Every text on the frame, with its pixel box: x, y (top), size, colour, lines."""
    sc = desc["scenario"]
    out: list[dict] = []

    def put(x, y, s, text, colour=HUD_TEXT, width=1500):
        lines = wrap(text, s, width)
        out.append({"x": x, "y": y, "size": s, "colour": colour, "lines": lines})
        return y + len(lines) * s * 1.28

    put(28, 22, 30, f"{sc['id']} {sc['name']}")
    put(28, 66, 17, sc["description"], (0.75, 0.77, 0.8), 1060)
    x, y, pw = 1128, 132, 450
    y = put(x, y, 15, "One concrete scenario (seeded sample of the logical scenario)", AMBER, pw)
    for p in desc["sample"]["parameters"]:
        y = put(x, y + 2, 13, p["label"], width=pw)
    y = put(x, y + 12, 15, "Safety goals at stake", AMBER, pw)
    for g in sc["goals"]:
        y = put(x, y + 2, 13, f"{g['id']} (ASIL {g['asil']}): {g['statement']}", width=pw)
    for m in sc["monitors"]:
        y = put(x, y + 2, 13, f"{m['id']} {m['name']}", width=pw)
    y = put(x, y + 12, 15, "Pass criterion", AMBER, pw)
    put(x, y + 2, 13, sc["pass"] + " (" + ", ".join(sc["pass_refs"]) + ")", width=pw)
    lg = desc["legend"]
    y = 640
    for key, colour in (
        ("plan", RED),
        ("envelope", BLUE),
        ("meant", GREEN),
        ("hazard", (1.0, 0.45, 0.2)),
        ("key", AMBER),
    ):
        out.append({"swatch": colour, "x": 28, "y": y + 2, "size": 12})
        y = put(52, y, 13, lg[key], width=1040) + 3
    put(28, 812, 22, desc["stamp"].upper(), AMBER, 1500)
    put(28, 852, 12, desc["credits"] + " · " + desc["scenario"]["source"], (0.6, 0.62, 0.65))
    return out


def panels() -> list[tuple[float, float, float, float, float]]:
    """Dark backgrounds behind the texts: x, y, w, h, opacity."""
    return [
        (0, 0, W, 118, 0.78),
        (1112, 120, 480, 505, 0.8),
        (14, 630, 1080, 158, 0.72),
        (0, 796, W, 104, 0.85),
    ]


def verify(desc: dict, manifest: dict, tol: float = 0.05) -> list[str]:
    """Differences between the built scene (its manifest) and the description."""
    errs = []
    built = manifest.get("objects", {})
    frames = manifest.get("render", {}).get("frames", 0)
    if frames < 2:
        return ["the manifest does not say how many frames the clip has"]
    for name, xy in expected(desc, frames).items():
        if name not in built:
            errs.append(f"{name}: not in the scene")
        elif math.dist(xy, built[name][:2]) > tol:
            errs.append(f"{name}: at {built[name][:2]}, the description puts it at {xy}")
    texts = " ".join(" ".join(t.split()) for t in manifest.get("texts", []))
    labels = [desc["stamp"].upper(), desc["scenario"]["id"], desc["scenario"]["name"]]
    labels += [p["label"] for p in desc["sample"]["parameters"]]
    labels += [f"{g['id']} (ASIL {g['asil']}): {g['statement']}" for g in desc["scenario"]["goals"]]
    labels += list(desc["legend"].values())
    for lab in labels:
        if " ".join(lab.split()) not in texts:
            errs.append(f"label not on the frame: {lab!r}")
    return errs


# ---------------------------------------------------------------- Blender


def build(desc: dict, args) -> dict:  # pragma: no cover - needs Blender
    import bpy
    from mathutils import Vector
    import mesh

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.seed = 1
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = args.scale
    fps, frames = args.fps, max(2, round(args.fps * args.seconds))
    scene.render.fps = fps
    scene.frame_start, scene.frame_end = 0, frames - 1
    still = still_frame(desc, frames)
    cond = desc["conditions"]
    rnd = random.Random(desc["scenario"]["id"])
    mats: dict[str, object] = {}

    def mat(name, colour, rough=0.6, emit=0.0, alpha=1.0, metal=0.0):
        if name in mats:
            return mats[name]
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*colour, 1.0)
        p.inputs["Roughness"].default_value = rough
        p.inputs["Metallic"].default_value = metal
        if emit:
            p.inputs["Emission Color"].default_value = (*colour, 1.0)
            p.inputs["Emission Strength"].default_value = emit
        if alpha < 1.0:
            p.inputs["Alpha"].default_value = alpha
        mats[name] = m
        return m

    def obj(name, verts, faces, material, parent=None, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        o = bpy.data.objects.new(name, me)
        o.location = loc
        if material is not None:
            o.data.materials.append(material)
        if parent is not None:
            o.parent = parent
        scene.collection.objects.link(o)
        return o

    def box(name, x0, y0, z0, x1, y1, z1, material, parent=None):
        v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        return obj(name, v, f, material, parent)

    def quad(name, x0, y0, x1, y1, z, material):
        return obj(
            name, [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [(0, 1, 2, 3)], material
        )

    def cyl(name, r, h, material, loc, n=16, parent=None, axis="z"):
        v, f = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            c, s = r * math.cos(a), r * math.sin(a)
            for z in (0, h):
                v.append(
                    {"z": (c, s, z), "x": (z - h / 2, c, s + r), "y": (c, z - h / 2, s + r)}[axis]
                )
        for i in range(n):
            j = (i + 1) % n
            f.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
        f.append(tuple(2 * i for i in range(n))[::-1])
        f.append(tuple(2 * i + 1 for i in range(n)))
        return obj(name, v, f, material, parent, loc)

    def ring(name, cx, cy, r0, r1, material, parent=None, n=40):
        v, f = [], []
        for i in range(n):
            a_ = 2 * math.pi * i / n
            v += [(cx + r * math.cos(a_), cy + r * math.sin(a_), 0.05) for r in (r0, r1)]
        for i in range(n):
            j = (i + 1) % n
            f.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
        return obj(name, v, f, material, parent)

    def ribbon(name, pts, width, z, material, dash=None):
        """A flat band along a polyline; with dash=(on, off) a dashed one."""
        total, s = length(pts), 0.0
        step = 0.5
        marks = []
        while s < total:
            marks.append(s)
            s += step
        marks.append(total)
        v, f = [], []
        for i in range(len(marks) - 1):
            if dash and (marks[i] % sum(dash)) >= dash[0]:
                continue
            for sv in (marks[i], marks[i + 1]):
                x, y, hd = point_at(pts, sv)
                nx, ny = math.cos(hd), math.sin(hd)
                v += [
                    (x - nx * width / 2, y - ny * width / 2, z),
                    (x + nx * width / 2, y + ny * width / 2, z),
                ]
            k = len(v) - 4
            f.append((k, k + 1, k + 3, k + 2))
        return obj(name, v, f, material)

    # -------- the road
    rd = desc["road"]
    y0, y1 = rd["length"]
    lane, park, walk = rd["lane"], rd.get("parking", 0), rd["sidewalk"]
    wet = cond["surface"] == "wet"
    asphalt = mat(
        "asphalt", (0.05, 0.055, 0.06) if wet else (0.09, 0.095, 0.1), 0.12 if wet else 0.75
    )
    paving = mat("sidewalk", (0.32, 0.32, 0.31), 0.35 if wet else 0.8)
    verge = mat("verge", (0.12, 0.16, 0.1), 0.9)
    paint = mat("paint", (0.85, 0.85, 0.82), 0.5)
    yellow = mat("yellow-paint", (0.85, 0.66, 0.12), 0.5)
    quad("ground", -80, y0 - 20, 80, y1 + 40, -0.02, verge)
    left, right = -lane, lane + park
    cross = rd.get("cross")
    sides = list(cross["sides"]) if cross else []
    if "t_left" in desc["features"]:
        sides = ["left"]
    quad("carriageway", left, y0, right, y1, 0.0, asphalt)
    gaps = []
    if cross:
        cy, cw = cross["y"], cross["width"]
        gaps = [(cy - cw / 2 - 1.5, cy + cw / 2 + 1.5)]
        if "left" in sides:
            quad("cross-left", -80, cy - cw / 2, left, cy + cw / 2, 0.0, asphalt)
        if "right" in sides:
            quad("cross-right", right, cy - cw / 2, 80, cy + cw / 2, 0.0, asphalt)

    def runs(a, b, side):
        """Stretches of [a, b] along y not cut by a cross street on that side."""
        cuts = [g for g in gaps if side in sides]
        out, s = [], a
        for g0, g1 in sorted(cuts):
            out.append((s, g0))
            s = g1
        out.append((s, b))
        return [(p, q) for p, q in out if q > p]

    for side, xa, xb in (("left", left - walk, left), ("right", right, right + walk)):
        for i, (p, q) in enumerate(runs(y0, y1, side)):
            box(f"sidewalk-{side}-{i}", xa, p, 0.0, xb, q, 0.15, paving)
    if cross:
        cy, cw = cross["y"], cross["width"]
        for side in sides:
            xa, xb = (-80, left - 1.5) if side == "left" else (right + 1.5, 80)
            box(f"cross-walk-{side}-a", xa, cy - cw / 2 - walk, 0.0, xb, cy - cw / 2, 0.15, paving)
            box(f"cross-walk-{side}-b", xa, cy + cw / 2, 0.0, xb, cy + cw / 2 + walk, 0.15, paving)
    # centre line, dashed, with a gap at a junction
    s = y0
    while s < y1:
        if not any(g0 - 2 < s < g1 for g0, g1 in gaps):
            quad(f"centre-{s:.0f}", -0.08, s, 0.08, s + 3.0, 0.004, yellow)
        s += 6.0
    if park:
        quad("parking-edge", lane - 0.06, y0, lane + 0.06, y1, 0.004, paint)
    if "crosswalk" in rd:
        a, b = rd["crosswalk"]
        x = left + 0.3
        while x < right - 0.3:
            quad(f"zebra-{x:.1f}", x, a, x + 0.5, b, 0.005, paint)
            x += 1.0
    if "stop_line" in rd:
        quad("stop-line", 0.1, rd["stop_line"] - 0.25, lane, rd["stop_line"] + 0.25, 0.005, paint)
    # buildings, seeded, for a sense of place
    concrete = [
        mat(f"building-{i}", c, 0.85)
        for i, c in enumerate(((0.36, 0.35, 0.34), (0.26, 0.28, 0.31), (0.42, 0.38, 0.33)))
    ]
    for side, xa in (("left", left - walk - 2.5), ("right", right + walk + 2.5)):
        s = y0
        while s < y1:
            d = rnd.uniform(9, 16)
            if not any(g0 - 4 < s + d and s < g1 + 4 for g0, g1 in gaps if side in sides):
                h_ = rnd.uniform(6, 14)
                xb = xa - 12 if side == "left" else xa + 12
                box(
                    f"building-{side}-{s:.0f}",
                    min(xa, xb),
                    s,
                    0,
                    max(xa, xb),
                    s + d - 1.2,
                    h_,
                    rnd.choice(concrete),
                )
            s += d
    # street lamps
    pole = mat("pole", (0.2, 0.21, 0.22), 0.5, metal=0.6)
    lit = cond["light"] in ("night", "dusk")
    for side, x in (("left", left - walk + 0.5), ("right", right + walk - 0.5)):
        for k, ly in enumerate(range(int(y0) + 10, int(y1), 28)):
            if any(g0 < ly < g1 for g0, g1 in gaps):
                continue
            cyl(f"lamp-{side}-{k}", 0.08, 6.5, pole, (x, ly, 0.15))
            if lit:
                lamp = bpy.data.lights.new(f"lamp-{side}-{k}", "POINT")
                lamp.energy = 900 if cond["light"] == "night" else 400
                lamp.color = (1.0, 0.82, 0.6)
                lamp.shadow_soft_size = 0.3
                lo = bpy.data.objects.new(f"lamp-light-{side}-{k}", lamp)
                lo.location = (x + (1.2 if side == "left" else -1.2), ly, 6.4)
                scene.collection.objects.link(lo)
    if "speed_sign" in rd:
        sx, sy = rd["speed_sign"]["at"]
        cyl("speed-sign-pole", 0.05, 2.4, pole, (sx, sy, 0.15))
        box(
            "speed-sign",
            sx - 0.05,
            sy - 0.32,
            2.0,
            sx + 0.05,
            sy + 0.32,
            2.75,
            mat("sign", (0.9, 0.9, 0.9), 0.4),
        )
        t = text_obj(
            bpy,
            f"{rd['speed_sign']['value']:g}\n{rd['speed_sign']['unit']}",
            0.22,
            mat("sign-ink", (0.02, 0.02, 0.02), 0.5),
        )
        t.location = (sx - 0.07, sy, 2.6)
        t.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
        t.data.align_x, t.data.align_y = "CENTER", "CENTER"
    feats = set(desc["features"])
    head_mat = mat("signal-head", (0.03, 0.03, 0.03), 0.4)
    if "ped_signals" in feats and "crosswalk" in rd:
        a, b = rd["crosswalk"]
        for k, (x, y) in enumerate(((right + 0.4, a - 0.6), (left - 0.4, b + 0.6))):
            cyl(f"ped-signal-pole-{k}", 0.06, 2.8, pole, (x, y, 0.15))
            box(f"ped-signal-{k}", x - 0.2, y - 0.2, 2.5, x + 0.2, y + 0.2, 3.1, head_mat)
    if "signals" in feats and cross:
        cy, cw = cross["y"], cross["width"]
        for k, (x, y) in enumerate(
            ((right + 0.5, cy - cw / 2 - 0.8), (left - 0.5, cy + cw / 2 + 0.8))
        ):
            cyl(f"signal-pole-{k}", 0.09, 4.6, pole, (x, y, 0.15))
            box(f"signal-{k}", x - 0.22, y - 0.22, 3.6, x + 0.22, y + 0.22, 4.7, head_mat)
    if "stop_sign" in feats and cross:
        cy, cw = cross["y"], cross["width"]
        x, y = right + 0.4, cy - cw / 2 - 1.0
        cyl("stop-sign-pole", 0.05, 2.3, pole, (x, y, 0.15))
        cyl(
            "stop-sign",
            0.38,
            0.04,
            mat("stop-red", (0.7, 0.04, 0.04), 0.4),
            (x, y, 2.4),
            n=8,
            axis="y",
        )

    # -------- vehicles and road users
    pack = mesh.load_pack()
    paint_of = {
        "body": (0.89, 0.9, 0.91),
        "glass": (0.06, 0.08, 0.11),
        "light_front": (1.0, 0.95, 0.84),
        "light_rear": (0.89, 0.18, 0.16),
        "indicator": (1.0, 0.95, 0.84),
        "wheel": (0.03, 0.03, 0.035),
        "trim": (0.07, 0.075, 0.08),
    }

    def vehicle(name, model, body):
        me = bpy.data.meshes.new(name)
        me.from_pydata(model.vertices, [], model.triangles)
        me.update()
        o = bpy.data.objects.new(name, me)
        for cls in mesh.CLASSES:
            colour = body if cls == "body" else paint_of[cls]
            lamp = cls.startswith("light")
            o.data.materials.append(
                mat(
                    f"{name}-{cls}" if cls == "body" else f"car-{cls}",
                    colour,
                    0.05 if cls == "glass" else 0.35,
                    emit=2.0 if lamp and cond["light"] != "day" else 0.0,
                    metal=0.3 if cls == "body" else 0.0,
                )
            )
        for poly, cls in zip(me.polygons, model.classes):
            poly.material_index = mesh.CLASSES.index(cls)
            poly.use_smooth = False
        scene.collection.objects.link(o)
        return o

    def person(name, variant, colour):
        root = bpy.data.objects.new(name, None)
        scene.collection.objects.link(root)
        cloth = mat(f"{name}-cloth", colour, 0.8)
        skin = mat("skin", (0.55, 0.4, 0.32), 0.7)
        k = {"child": 0.68}.get(variant, 1.0)
        z0 = 0.0
        if variant == "wheelchair":
            for sx in (-0.33, 0.33):
                cyl(
                    f"{name}-wheel{sx}",
                    0.3,
                    0.05,
                    mat("tyre", (0.03, 0.03, 0.03), 0.8),
                    (sx, 0, 0),
                    axis="x",
                    parent=root,
                )
            box(f"{name}-seat", -0.25, -0.25, 0.45, 0.25, 0.25, 0.52, cloth, root)
            box(f"{name}-body", -0.18, -0.15, 0.52, 0.18, 0.12, 1.15, cloth, root)
            cyl(f"{name}-head", 0.11, 0.24, skin, (0, 0, 1.17), parent=root)
            return root
        if variant in ("bicycle", "e-scooter"):
            frame = mat("frame", (0.15, 0.15, 0.16), 0.4, metal=0.5)
            if variant == "bicycle":
                for sy in (-0.55, 0.55):
                    cyl(
                        f"{name}-wheel{sy}",
                        0.34,
                        0.04,
                        mat("tyre", (0.03, 0.03, 0.03), 0.8),
                        (0, sy, 0),
                        axis="x",
                        parent=root,
                    )
                box(f"{name}-frame", -0.03, -0.5, 0.35, 0.03, 0.5, 0.75, frame, root)
                z0 = 0.55
            else:
                box(f"{name}-deck", -0.08, -0.45, 0.08, 0.08, 0.45, 0.14, frame, root)
                box(f"{name}-post", -0.02, 0.38, 0.14, 0.02, 0.44, 1.05, frame, root)
                z0 = 0.14
        box(f"{name}-legs", -0.14, -0.1, z0, 0.14, 0.1, z0 + 0.8 * k, cloth, root)
        box(f"{name}-torso", -0.2, -0.12, z0 + 0.8 * k, 0.2, 0.12, z0 + 1.45 * k, cloth, root)
        cyl(f"{name}-head", 0.11 * k, 0.24 * k, skin, (0, 0, z0 + 1.47 * k), parent=root)
        return root

    def boxed(name, variant, colour):
        root = bpy.data.objects.new(name, None)
        scene.collection.objects.link(root)
        m = mat(f"{name}-body", colour, 0.5, metal=0.2)
        dims = {
            "bus": (2.55, 12.0, 3.1),
            "truck": (2.5, 8.0, 3.4),
            "motorcycle": (0.7, 2.1, 1.0),
            "animal": (0.3, 0.9, 0.6),
        }[variant]
        w_, l_, h_ = dims
        box(
            f"{name}-hull",
            -w_ / 2,
            -l_ / 2,
            0.3,
            w_ / 2,
            l_ / 2,
            h_,
            m,
            root,
        )
        if variant in ("bus", "truck"):
            box(
                f"{name}-glass",
                -w_ / 2 - 0.01,
                l_ / 2 - 1.6,
                1.4,
                w_ / 2 + 0.01,
                l_ / 2 + 0.01,
                h_ - 0.3,
                mat("car-glass", paint_of["glass"], 0.05),
                root,
            )
        if variant == "motorcycle":
            cyl(
                f"{name}-rider",
                0.18,
                0.6,
                mat(f"{name}-rider", (0.1, 0.1, 0.12), 0.7),
                (0, -0.1, 1.0),
                parent=root,
            )
        return root

    kiri = mesh.load_kiri()
    ego = vehicle("ego", kiri, (0.93, 0.94, 0.95))
    lo_, hi_ = kiri.bounds()
    ego_front, ego_w = hi_[1], hi_[0] - lo_[0]
    sensor = mat("roof-sensor", (0.1, 0.11, 0.13), 0.3)
    cyl("ego-roof-sensor", 0.16, 0.14, sensor, (0, 0.2, hi_[2]), parent=ego)
    if cond["light"] != "day":
        for k, sx in enumerate((-0.6, 0.6)):
            hl = bpy.data.lights.new(f"headlight-{k}", "SPOT")
            hl.energy, hl.spot_size, hl.spot_blend = 1500, math.radians(50), 0.4
            hl.color = (1.0, 0.95, 0.85)
            ho = bpy.data.objects.new(f"headlight-{k}", hl)
            ho.location = (sx, ego_front - 0.1, 0.7)
            ho.rotation_euler = (math.radians(85), 0, 0)  # along +y, slightly down
            ho.parent = ego
            scene.collection.objects.link(ho)
    actors = []
    for i, a in enumerate(desc["actors"]):
        colour = (
            AMBER if a["role"] == "key" else GREY if a["role"] == "other" else (0.55, 0.57, 0.6)
        )
        name = f"actor{i}-{a['class']}"
        kind, _, variant = a["drawn_as"].partition(":")
        if kind == "person":
            o = person(name, variant, colour)
        elif kind == "box":
            o = boxed(name, variant, colour)
        else:
            o = vehicle(name, pack[a["drawn_as"]], colour)
        if a["role"] == "key":
            ring(f"{name}-ring", 0.0, 0.0, 1.3, 1.6, mat("key-ring", AMBER, 0.5, emit=3.0), o)
        actors.append((o, a))
    if "queue" in feats:
        for k, (x, y, hd) in enumerate(
            (
                (1.75, 38.0, 0),
                (1.75, 45.5, 0),
                (-1.75, 12.0, math.pi),
                (-1.75, 4.0, math.pi),
                (-1.75, -4.0, math.pi),
            )
        ):
            q = vehicle(
                f"queue-{k}",
                pack[("hatchback", "wagon", "suv", "compact", "sedan")[k]],
                (0.55, 0.57, 0.6),
            )
            q.location, q.rotation_euler = (x, y, 0), (0, 0, hd)

    # -------- overlays
    plan_m = mat("plan", RED, 0.5, emit=1.6, alpha=0.55)
    ribbon("plan", desc["plan"], 0.45, 0.03, plan_m)
    meant_m = mat("meant", GREEN, 0.5, emit=2.0, alpha=0.9)
    ribbon("meant", desc["ego"]["path"], 0.22, 0.045, meant_m, dash=(1.0, 0.8))
    if desc["ego"]["stops"]:
        ex, ey, _ = point_at(desc["ego"]["path"], length(desc["ego"]["path"]))
        ring("meant-moment", ex, ey + ego_front + 0.6, 2.3, 2.6, meant_m)
    hx0, hy0, hx1, hy1 = desc["hazard"]
    haz = mat("hazard", (1.0, 0.45, 0.2), 0.5, emit=1.4, alpha=0.38)
    quad("hazard", hx0, hy0, hx1, hy1, 0.04, haz)
    edge = mat("hazard-edge", (1.0, 0.45, 0.2), 0.5, emit=3.0)
    for k, (a_, b_) in enumerate(
        (
            ((hx0, hy0), (hx1, hy0)),
            ((hx1, hy0), (hx1, hy1)),
            ((hx1, hy1), (hx0, hy1)),
            ((hx0, hy1), (hx0, hy0)),
        )
    ):
        ribbon(f"hazard-edge-{k}", [list(a_), list(b_)], 0.12, 0.05, edge)
    if desc["occlusion"]:
        occ = desc["occlusion"]
        obj(
            "occlusion",
            [(x, y, 0.2) for x, y in occ],
            [tuple(range(len(occ)))],
            mat("occlusion", (0.6, 0.62, 0.66), 0.5, emit=0.4, alpha=0.3),
        )
    env_m = mat("envelope", BLUE, 0.4, emit=1.2, alpha=0.33)
    env = box("envelope", -ego_w / 2 - 0.3, 0.0, 0.02, ego_w / 2 + 0.3, 1.0, 0.25, env_m)
    env.parent = ego
    env.location = (0, ego_front, 0)
    env_wall = box(
        "envelope-wall",
        -ego_w / 2 - 0.3,
        0.98,
        0.02,
        ego_w / 2 + 0.3,
        1.0,
        0.9,
        mat("envelope-wall", BLUE, 0.4, emit=2.0, alpha=0.4),
    )
    env_wall.parent = env
    beyond = cond.get("beyond")
    if beyond:
        by = beyond["y"]
        curtain = mat("odd-limit", VIOLET, 0.5, emit=1.5, alpha=0.28)
        obj(
            "odd-limit",
            [(-30, by, 0), (30, by, 0), (30, by, 7), (-30, by, 7)],
            [(0, 1, 2, 3)],
            curtain,
        )

    # -------- the ODD conditions
    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    light = cond["light"]
    sky = {
        "day": ((0.5, 0.66, 0.9), 1.0),
        "low-sun": ((0.75, 0.62, 0.45), 1.2),
        "dusk": ((0.28, 0.22, 0.32), 0.45),
        "night": ((0.015, 0.02, 0.035), 0.5),
        "unlit": ((0.01, 0.012, 0.02), 0.35),
    }[light]
    bg.inputs["Color"].default_value = (*sky[0], 1.0)
    bg.inputs["Strength"].default_value = sky[1]
    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy, sun_d.color, elev, az = {
        "day": (3.5, (1.0, 0.97, 0.92), 50, 30),
        "low-sun": (5.0, (1.0, 0.8, 0.55), 6, 180),
        "dusk": (1.0, (1.0, 0.6, 0.4), 6, 300),
        "night": (0.06, (0.6, 0.7, 1.0), 40, 20),
        "unlit": (0.04, (0.6, 0.7, 1.0), 40, 20),
    }[light]
    sun = bpy.data.objects.new("sun", sun_d)
    # azimuth 0 sends the light along +y, away from the camera; low sun (180) shines into it
    sun.rotation_euler = (math.radians(90 - elev), 0, math.radians(az))
    scene.collection.objects.link(sun)
    if cond.get("rain"):
        n = int(2500 * cond["rain"] / cond["rain_limit"]) + 300
        drops = mat(
            "rain",
            (0.8, 0.85, 0.9),
            0.1,
            emit=0.9 if light in ("night", "unlit", "dusk") else 0.5,
            alpha=0.35,
        )
        v, f = [], []
        for zone, count, ylo, yhi in (
            ("in", n, -8.0, beyond["y"] if beyond else 80.0),
            ("beyond", 3 * n if beyond else 0, beyond["y"] if beyond else 0, 110.0),
        ):
            for _ in range(count):
                x, y, z = rnd.uniform(-14, 14), rnd.uniform(ylo, yhi), rnd.uniform(0.0, 9.0)
                k = len(v)
                v += [
                    (x, y, z),
                    (x + 0.012, y, z),
                    (x + 0.06, y + 0.02, z + 0.55),
                    (x + 0.048, y + 0.02, z + 0.55),
                ]
                f.append((k, k + 1, k + 2, k + 3))
        obj("rain", v, f, drops)
    if cond.get("visibility") or beyond:
        vis = cond.get("visibility") or cond.get("visibility_floor")

        def fog(name, ylo, yhi, density):
            vm = bpy.data.materials.new(name)
            vm.use_nodes = True
            nt = vm.node_tree
            nt.nodes.remove(nt.nodes["Principled BSDF"])
            pv = nt.nodes.new("ShaderNodeVolumePrincipled")
            pv.inputs["Density"].default_value = density
            pv.inputs["Color"].default_value = (0.75, 0.77, 0.8, 1)
            nt.links.new(pv.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
            box(name, -60, ylo, -0.1, 60, yhi, 25, vm)

        # Koschmieder: a contrast threshold of 2 % gives an extinction of 3.912 / visibility
        top = beyond["y"] if beyond else y1 + 30
        if cond.get("visibility"):
            fog("fog", y0 - 30, top, 3.912 / vis)
        if beyond and "ODD-11" in beyond["attributes"]:
            fog("fog-beyond", top, y1 + 30, 3.912 / (vis * 0.4))  # drawn denser; no value stated

    # -------- camera and the frame's texts
    cam_d = bpy.data.cameras.new("camera")
    cam_d.lens = desc["camera"]["lens"]
    cam_d.sensor_fit = "HORIZONTAL"
    cam_d.sensor_width = 36
    cam_d.clip_start = 0.05
    cam_d.clip_end = 600
    cam = bpy.data.objects.new("camera", cam_d)
    cam.location = desc["camera"]["pos"]
    look = Vector(desc["camera"]["look"]) - Vector(desc["camera"]["pos"])
    cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    d = 1.0
    vw = 36 / cam_d.lens * d
    vh = vw * H / W

    def at(px, py):
        return ((px / W - 0.5) * vw, (0.5 - py / H) * vh)

    texts = []
    for i, (px, py, pw, ph, op) in enumerate(panels()):
        (x0, y0_), (x1, y1_) = at(px, py), at(px + pw, py + ph)
        pm = mat(f"panel-{i}", (0.03, 0.035, 0.04), 1.0, emit=1.0, alpha=op)
        obj(
            f"panel-{i}",
            [(x0, y0_, -d), (x1, y0_, -d), (x1, y1_, -d), (x0, y1_, -d)],
            [(0, 1, 2, 3)],
            pm,
            parent=cam,
        )
    for i, t in enumerate(hud_texts(desc)):
        k = vw / W
        if "swatch" in t:
            (x0, y0_), (x1, y1_) = at(t["x"], t["y"]), at(t["x"] + 16, t["y"] + 12)
            obj(
                f"swatch-{i}",
                [
                    (x0, y0_, -d * 0.999),
                    (x1, y0_, -d * 0.999),
                    (x1, y1_, -d * 0.999),
                    (x0, y1_, -d * 0.999),
                ],
                [(0, 1, 2, 3)],
                mat(f"swatch-{i}", t["swatch"], 1.0, emit=2.0),
                parent=cam,
            )
            continue
        body = "\n".join(t["lines"])
        o = text_obj(
            bpy, body, t["size"] * k, mat(f"ink-{t['colour']}", t["colour"], 1.0, emit=1.0)
        )
        o.data.space_line = 1.28 / 1.2
        o.data.align_y = "TOP"
        x, y = at(t["x"], t["y"])
        o.location = (x, y, -d * 0.998)
        o.parent = cam
        texts.append(body)

    # -------- motion
    n_f = scene.frame_end + 1
    for fr in range(n_f):
        u = fr / (n_f - 1)
        x, y, hd = ego_at(desc, u)
        ego.location, ego.rotation_euler = (x, y, 0), (0, 0, hd)
        ego.keyframe_insert("location", frame=fr)
        ego.keyframe_insert("rotation_euler", frame=fr)
        env.scale = (1, envelope_at(desc, u), 1)
        env.keyframe_insert("scale", frame=fr)
        for o, a in actors:
            x, y, hd = actor_at(a, u)
            o.location = (x, y, 0)
            if len(a["path"]) > 1:
                o.rotation_euler = (0, 0, hd)
                o.keyframe_insert("rotation_euler", frame=fr)
            o.keyframe_insert("location", frame=fr)
    scene.frame_set(still)
    built = {"ego": [round(ego.location.x, 2), round(ego.location.y, 2)]}
    for o, a in actors:
        built[o.name] = [round(o.location.x, 2), round(o.location.y, 2)]
    return {
        "scenario": desc["scenario"]["id"],
        "blender": bpy.app.version_string,
        "render": {
            "engine": "CYCLES",
            "samples": args.samples,
            "size": [W * args.scale // 100, H * args.scale // 100],
            "still_frame": still,
            "frames": n_f,
            "fps": fps,
        },
        "objects": built,
        "texts": texts,
    }


def text_obj(bpy, body: str, size: float, material):  # pragma: no cover - needs Blender
    cu = bpy.data.curves.new("text", "FONT")
    cu.body = body
    cu.size = size
    o = bpy.data.objects.new("text", cu)
    o.data.materials.append(material)
    bpy.context.scene.collection.objects.link(o)
    return o


def render(args, desc: dict, out: Path, manifest: dict) -> None:  # pragma: no cover - needs Blender
    import bpy

    scene = bpy.context.scene
    sid = desc["scenario"]["id"]
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(out / f"{sid}.png")
    bpy.ops.render.render(write_still=True)
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(out / f"{sid}.blend"))
    if args.animate:
        s = scene.render
        if hasattr(s.image_settings, "media_type"):
            s.image_settings.media_type = "VIDEO"
        s.image_settings.file_format = "FFMPEG"
        s.ffmpeg.format = "MPEG4"
        s.ffmpeg.codec = "H264"
        s.ffmpeg.constant_rate_factor = "MEDIUM"
        s.filepath = str(out / f"{sid}-")
        bpy.ops.render.render(animation=True)
        made = sorted(out.glob(f"{sid}-*.mp4"))
        if made:
            made[-1].replace(out / f"{sid}.mp4")
            manifest["animation"] = f"{sid}.mp4"


def main(argv: list[str]) -> int:  # pragma: no cover - needs Blender
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "scene", type=Path, nargs="+", help="scene description(s), tools/sim/scenes/*.json"
    )
    ap.add_argument("--out", type=Path, default=Path("build/sim"))
    ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--scale", type=int, default=100, help="render size in percent of 1600 x 900")
    ap.add_argument("--animate", action="store_true", help="also render the clip as MP4")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--blend", action="store_true", help="also save the .blend file")
    ap.add_argument(
        "--verify", action="store_true", help="fail when the scene differs from the description"
    )
    ap.add_argument("--no-render", action="store_true", help="build and verify only")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    failed = 0
    for path in args.scene:
        desc = json.loads(path.read_text(encoding="utf-8"))
        manifest = build(desc, args)
        if not args.no_render:
            render(args, desc, args.out, manifest)
        sid = desc["scenario"]["id"]
        (args.out / f"{sid}.manifest.json").write_text(
            json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        errs = verify(desc, manifest)
        for e in errs:
            print(f"{sid}: {e}")
        if errs and args.verify:
            failed += 1
        print(
            f"{sid}: built"
            + ("" if args.no_render else f", rendered to {args.out}")
            + (f", {len(errs)} difference(s)" if errs else ", matches its description")
        )
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]))
