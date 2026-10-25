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
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "readme"))

ENVELOPE_M = 14.0  # drawn length of the monitor's envelope at the clip's start speed; not computed
HOLD_S = 1.0  # seconds the ego stands still at the end of the clip
SUPERSAMPLE = (
    1.5  # views render at this multiple of their size on the dashboard, then are scaled down
)
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
LEGEND = (  # legend key of the description -> its colour in HEX
    ("plan", "red"),
    ("envelope", "blue"),
    ("meant", "green"),
    ("hazard", "orange"),
    ("key", "amber"),
    ("occlusion", "grey"),
    ("odd_limit", "violet"),
)

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


def ego_profile(desc: dict) -> tuple[float, float, float]:
    """Seconds the ego cruises, slows and stands, and the clip's length is their sum.

    The ego cruises at its sampled ODD-20 speed over the first `cruise_m` of its path, then slows at
    the description's `decel` (a level the records state) to stand still at the end of its path, and
    stands for HOLD_S. Without a sampled speed the clip lasts 6 s and nothing is to speed."""
    e = desc["ego"]
    v = (e.get("speed_kmh") or 0) / 3.6
    total = length(e["path"])
    if v <= 0 or total <= 0:
        return 6.0, 0.0, 0.0
    if not e["stops"]:
        return total / v, 0.0, 0.0
    brake = v / e["decel"]
    cruise = max(0.0, total - v * brake / 2) / v
    return cruise, brake, HOLD_S


def clip_seconds(desc: dict) -> float:
    return sum(ego_profile(desc))


def ego_speed_factor(desc: dict, u: float) -> float:
    """The ego's speed as a share of its sampled speed at clip fraction u."""
    cruise, brake, _ = ego_profile(desc)
    t = u * clip_seconds(desc)
    if not desc["ego"]["stops"] or t <= cruise:
        return 1.0
    return max(0.0, 1.0 - (t - cruise) / brake)


def ego_distance(desc: dict, u: float) -> float:
    """Metres the ego has covered along its path at clip fraction u."""
    cruise, brake, _ = ego_profile(desc)
    v = (desc["ego"].get("speed_kmh") or 0) / 3.6
    total = length(desc["ego"]["path"])
    if v <= 0:
        return total * u
    t = u * clip_seconds(desc)
    if t <= cruise or not brake:
        return min(total, v * t)
    tb = min(t - cruise, brake)
    return min(total, v * cruise + v * tb - v / brake * tb * tb / 2)


def ego_at(desc: dict, u: float) -> tuple[float, float, float]:
    return point_at(desc["ego"]["path"], ego_distance(desc, u))


def envelope_at(desc: dict, u: float) -> float:
    """Drawn envelope length: ENVELOPE_M scaled by the square of the speed share, never below 1 m."""
    return max(1.0, ENVELOPE_M * ego_speed_factor(desc, u) ** 2)


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
    y = put(x, y + 2, 13, desc["ego"]["motion_label"], width=pw)
    y = put(x, y + 12, 15, "Safety goals at stake", AMBER, pw)
    for g in sc["goals"]:
        y = put(x, y + 2, 13, f"{g['id']} (ASIL {g['asil']}): {g['statement']}", width=pw)
    for m in sc["monitors"]:
        y = put(x, y + 2, 13, f"{m['id']} {m['name']}", width=pw)
    y = put(x, y + 12, 15, "Pass criterion", AMBER, pw)
    put(x, y + 2, 13, sc["pass"] + " (" + ", ".join(sc["pass_refs"]) + ")", width=pw)
    lg = desc["legend"]
    y = 640
    for key, colour in LEGEND:
        if key not in lg:
            continue
        out.append({"swatch": srgb(HEX[colour]), "x": 28, "y": y + 2, "size": 12})
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


# ---------------------------------------------------------------- the review dashboard (plain Python)

DW, DH = 1920, 1080
CHASE = (384, 72, 1048, 590)  # x, y, w, h of the chase view on the dashboard
FORWARD = (1444, 96, 464, 261)
TOP = (1444, 392, 464, 261)
THUMB_W, THUMB_H, THUMB_Y = 200, 112, 830
CHASE_RIG = (
    (-2.2, -10.5, 4.6),
    (0.6, 16.0, 0.0),
)  # chase camera and the point it looks at, in the ego's frame
INK, INK2, MUTED = "#f0efec", "#c3c2b7", "#898781"
BG, PANEL, EDGE = "#111110", "#1a1a19", "#2c2c2a"
HEX = {
    "amber": "#ffcf6e",
    "blue": "#5b9bff",
    "red": "#ff4d40",
    "green": "#43f08a",
    "orange": "#ff7333",
    "grey": "#9da1a8",
    "violet": "#c38bff",
}


def moments(desc: dict) -> list[tuple[float, str]]:
    """The moments of the clip the filmstrip shows: (clip fraction, what happens)."""
    out = [(0.0, "start")]
    for a in desc["actors"]:
        if a["role"] == "key" and len(a["path"]) > 1 and a["move"][0] > 0:
            out.append((a["move"][0], f"{a['label']} starts to move"))
    cruise, brake, _ = ego_profile(desc)
    t = clip_seconds(desc)
    if desc["ego"]["stops"]:
        out.append((cruise / t, "vehicle starts to slow"))
    out.append((desc["still"], "the moment in the main view"))
    out.append(
        ((cruise + brake) / t, "vehicle stands still") if desc["ego"]["stops"] else (1.0, "end")
    )
    out.sort(key=lambda m: m[0])
    kept: list[tuple[float, str]] = []
    for u, label in out:
        if kept and u - kept[-1][0] < 0.05:
            if label == "the moment in the main view":
                kept[-1] = (u, label)
            continue
        kept.append((u, label))
    return kept[:5]


def header_fields(desc: dict) -> list[tuple[str, str]]:
    speed = next((p for p in desc["sample"]["parameters"] if p["parameter"] == "ODD-20"), None)
    return [
        ("Motion", "choreography (qualitative)"),
        ("Condition", desc["condition_label"]),
        ("Ego speed (sample)", f"{speed['value']:g} {speed['unit']}" if speed else "—"),
        ("Methods (WP-V-03)", ", ".join(desc["scenario"]["methods"])),
    ]


def place_tags(tags: list[dict]) -> list[dict]:
    """Tag boxes (x, y, w) in the chase view's pixels: above each road user, inside the view, and
    moved up, one row at a time, until no two overlap."""
    placed: list[dict] = []
    for t in sorted(tags, key=lambda t: -t["y"]):
        w = len(t["label"]) * 12 * 0.56 + 14
        x = min(max(4, t["x"] - w / 2), CHASE[2] - w - 4)
        y = min(max(4, t["y"] - 34), CHASE[3] - 26)
        while any(
            abs(y - p["box"][1]) < 25 and x < p["box"][0] + p["box"][2] and p["box"][0] < x + w
            for p in placed
        ):
            y -= 26
        placed.append({**t, "box": (x, max(4, y), w)})
    return placed


def chip_width(label: str) -> float:
    return len(label) * 12 * 0.6 + 14


def goal_chips(goals: list[dict], room: float) -> list[str]:
    """The header chips of the safety goals at stake, as many as fit in `room` pixels; the rest are
    counted in a last chip ("+2 more"), so no goal disappears without a trace."""
    labels = [f"{g['id']} ASIL {g['asil']}" for g in goals]
    for n in range(len(labels), -1, -1):
        shown = labels[:n] + ([f"+{len(labels) - n} more"] if n < len(labels) else [])
        if sum(chip_width(x) + 6 for x in shown) <= room:
            return shown
    return []


def look_credit(look_: dict) -> str:
    """The credit line of the assets a dashboard was drawn with (all CC0, credited all the same)."""
    sources = sorted({a["source"] for a in look_.get("assets", [])})
    names = {"polyhaven": "Poly Haven", "ambientcg": "ambientCG"}
    out = []
    if sources:
        out.append("sky, textures and street furniture: " + ", ".join(names[x] for x in sources))
    if look_.get("pedestrians", "").startswith("Quaternius"):
        out.append("pedestrians: Quaternius")
    return ("; ".join(out) + " (CC0)") if out else "procedural look (no fetched assets)"


def dashboard_layout(desc: dict, tags: list[dict], look_: dict | None = None) -> list[dict]:
    """Everything on the dashboard, in pixels (x right, y down): rects, images, texts.

    `tags` are the road-user labels on the chase view, with their position in that view's pixels."""
    sc = desc["scenario"]
    el: list[dict] = [{"rect": (0, 0, DW, DH), "fill": BG}]

    def rect(x, y, w, h, fill=PANEL, edge=EDGE):
        el.append({"rect": (x, y, w, h), "fill": fill, "edge": edge})

    def text(x, y, s, body, colour=INK, width=2000, key=None):
        lines = wrap(body, s, width)
        el.append({"text": lines, "x": x, "y": y, "size": s, "colour": colour, "key": key})
        return y + len(lines) * s * 1.3

    def flow(box, blocks, sizes=(14, 13, 12, 11, 10)):
        """Headings and paragraphs in a panel, at the largest size that fits."""
        x, y, w, h = box
        rect(x, y, w, h)
        for s in sizes:
            yy, height = y + 12, 0.0
            for kind, body, _ in blocks:
                n = len(wrap(body, s + (1 if kind == "h" else 0), w - 24))
                height += n * (s + 1) * 1.3 + (8 if kind == "h" else 3)
            if height <= h - 18 or s == sizes[-1]:
                break
        for kind, body, colour in blocks:
            if kind == "h":
                yy = text(x + 12, yy + 5, s + 1, body, colour, w - 24) + 3
            else:
                yy = text(x + 12, yy, s, body, colour, w - 24) + 3

    # header strip
    text(16, 12, 24, f"{sc['id']} {sc['name']}", INK, 1060, key="title")
    cx = 16 + min(1060, len(f"{sc['id']} {sc['name']}") * 24 * 0.52) + 16
    for i, label in enumerate(goal_chips(sc["goals"], 1060 - cx)):
        w = chip_width(label)
        el.append({"rect": (cx, 16, w, 24), "fill": "#8f2a22", "edge": HEX["red"]})
        text(cx + 7, 21, 12, label, INK)
        cx += w + 6
    hx = 1080
    for (label, value), w in zip(header_fields(desc), (170, 330, 140, 190)):
        text(hx, 8, 11, label, MUTED)
        text(hx, 25, 13 if len(wrap(value, 13, w - 10)) <= 2 else 11, value, INK, w - 10)
        hx += w

    # left: the scenario as the records state it, and the concrete sample
    blocks = [("p", sc["description"], INK2)]
    if sc["events"]:
        blocks.append(("h", "Hazardous events (WP-C-03)", HEX["orange"]))
        blocks += [("p", f"{e['id']} {e['description']}", INK) for e in sc["events"]]
    if sc["triggers"]:
        blocks.append(("h", "Triggering conditions (WP-C-06)", HEX["amber"]))
        blocks += [("p", f"{t['id']} {t['condition']}", INK) for t in sc["triggers"]]
    refs = [
        ("Situations", sc["situations"]),
        ("Misuse (WP-C-08)", sc["misuse"]),
        ("Loss scenarios (WP-A-05)", sc["losses"]),
    ]
    for label, ids in refs:
        if ids:
            blocks.append(("p", f"{label}: {', '.join(ids)}", INK2))
    flow((12, 72, 360, 430), [("h", "Scenario (WP-V-03)", INK)] + blocks)
    flow(
        (12, 512, 360, 448),
        [("h", "One concrete scenario (seeded sample)", HEX["amber"])]
        + [("p", p["label"], INK) for p in desc["sample"]["parameters"]]
        + [("p", desc["ego"]["motion_label"], INK2)],
    )

    # centre: the chase view with its tags, what the vehicle is meant to do, the filmstrip
    rect(*CHASE)
    el.append({"image": "chase", "box": CHASE})
    for t in place_tags(tags):
        x, y, w = t["box"]
        el.append(
            {"rect": (CHASE[0] + x, CHASE[1] + y, w, 22), "fill": "#0d0f12", "edge": t["colour"]}
        )
        text(CHASE[0] + x + 7, CHASE[1] + y + 5, 12, t["label"], t["colour"])
    flow(
        (384, 672, 1048, 146),
        [
            ("h", desc["legend"]["meant"], HEX["green"]),
            ("p", f"Pass criterion: {sc['pass']} ({', '.join(sc['pass_refs'])})", INK),
        ],
        sizes=(13, 12, 11, 10),
    )
    for i, (u, label) in enumerate(moments(desc)):
        x = 384 + i * (THUMB_W + 12)
        rect(x, THUMB_Y - 2, THUMB_W, THUMB_H + 34)
        el.append({"image": f"thumb{i}", "box": (x, THUMB_Y, THUMB_W, THUMB_H)})
        text(x + 6, THUMB_Y + THUMB_H + 6, 11, label, INK2, THUMB_W - 12)

    # right: forward and top views, the safety goals at stake
    for box, title, key in (
        (FORWARD, "Forward view", "forward"),
        (TOP, "Top view: planned path, envelope, hazard", "top"),
    ):
        rect(box[0], box[1] - 24, box[2], box[3] + 24)
        text(box[0] + 10, box[1] - 19, 13, title, INK)
        el.append({"image": key, "box": box})
    goals = [("h", "Safety goals at stake", HEX["red"])]
    goals += [("p", f"{g['id']} (ASIL {g['asil']}): {g['statement']}", INK) for g in sc["goals"]]
    if sc["monitors"]:
        goals.append(("h", "ODD monitors the pass criterion cites (WP-C-02 §4)", HEX["blue"]))
        goals += [("p", f"{m['id']} {m['name']}", INK) for m in sc["monitors"]]
    flow((1444, 664, 464, 296), goals)

    # footer: the stamp, the legend, the credits
    text(16, 986, 22, desc["stamp"].upper(), HEX["amber"], 1900, key="stamp")
    lx, ly = 16, 1018
    for key, colour in LEGEND:
        if key not in desc["legend"] or key == "meant":
            continue
        body = desc["legend"][key]
        w = 20 + len(body) * 11 * 0.52
        if lx > 16 and lx + w > DW - 16:
            lx, ly = 16, ly + 18
        el.append({"rect": (lx, ly + 2, 14, 10), "fill": HEX[colour], "edge": HEX[colour]})
        text(lx + 20, ly, 11, body, INK2, DW - 52)
        lx += w + 22
    credit = desc["credits"] + " · " + look_credit(look_ or {}) + " · " + sc["source"]
    text(16, 1062, 10, credit, MUTED, 1900)
    return el


def dashboard_texts(layout: list[dict]) -> list[str]:
    return [" ".join(e["text"]) for e in layout if "text" in e]


def srgb(hex_: str) -> tuple[float, float, float]:
    """A #rrggbb colour as linear RGB, for an emission shader shown through the Standard view."""
    c = [int(hex_[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def described(desc: dict) -> dict:
    """What the scene should show of the conditions and features, as the manifest records it."""
    c, rd, feats = desc["conditions"], desc["road"], set(desc["features"])
    beyond = c.get("beyond") or {}
    want = {
        "light": c["light"],
        "wet": c["surface"] == "wet",
        "rain": bool(c.get("rain")),
        "fog": bool(c.get("visibility")),
        "beyond": sorted(
            (["fog-beyond"] if "ODD-11" in beyond.get("attributes", []) else [])
            + (["odd-limit"] if beyond else [])
        ),
        "features": sorted(feats),
        "stop_line": "stop_line" in rd and "no_stop_line" not in feats,
        "speed_sign": "speed_sign" in rd,
        "occlusion": bool(desc["occlusion"]),
    }
    return want


def drawn_errors(desc: dict, drawn: dict) -> list[str]:
    """What the scene should show of the conditions and features, against what was built."""
    want = described(desc)
    if not drawn:
        return ["the manifest does not say what was drawn"]
    return [
        f"{k}: drawn {drawn.get(k)!r}, described {v!r}"
        for k, v in want.items()
        if drawn.get(k) != v
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
    errs += [f"drawn: {e}" for e in drawn_errors(desc, manifest.get("drawn", {}))]
    sc = desc["scenario"]
    labels = [desc["stamp"].upper(), sc["id"], sc["name"], desc["credits"], sc["pass"]]
    labels.append(desc["ego"]["motion_label"])
    labels += [f"{m['id']} {m['name']}" for m in sc["monitors"]]
    labels += [p["label"] for p in desc["sample"]["parameters"]]
    labels += [f"{g['id']} (ASIL {g['asil']}): {g['statement']}" for g in desc["scenario"]["goals"]]
    labels += list(desc["legend"].values())
    for frame in ("texts", "clip_texts"):
        if frame not in manifest:
            continue
        texts = " ".join(" ".join(t.split()) for t in manifest[frame])
        where = "the dashboard" if frame == "texts" else "the clip"
        for lab in labels:
            if " ".join(lab.split()) not in texts:
                errs.append(f"label not on {where}: {lab!r}")
    return errs


# ---------------------------------------------------------------- Blender


def build(desc: dict, args) -> dict:  # pragma: no cover - needs Blender
    import bpy
    import look
    from mathutils import Vector
    import mesh

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    assets = look.Assets(use=not args.procedural)
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.seed = 1
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = args.scale
    fps, frames = args.fps, max(2, round(args.fps * clip_seconds(desc)))
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
    asphalt = look.surface(
        bpy, assets, "asphalt", "asphalt", "asphalt", (0.09, 0.095, 0.1), 0.75, wet
    )
    paving = look.surface(
        bpy, assets, "sidewalk", "concrete", "concrete", (0.32, 0.32, 0.31), 0.8, wet
    )
    verge = look.surface(bpy, assets, "verge", "grass", "grass", (0.12, 0.16, 0.1), 0.9)
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
    if "stop_line" in rd and "no_stop_line" not in desc["features"]:
        quad("stop-line", 0.1, rd["stop_line"] - 0.25, lane, rd["stop_line"] + 0.25, 0.005, paint)
    # buildings, seeded, for a sense of place
    concrete = [
        look.surface(bpy, assets, f"building-{i}", slot, "facade", c, 0.85)
        for i, (slot, c) in enumerate(
            (
                ("facade_a", (0.36, 0.35, 0.34)),
                ("facade_b", (0.26, 0.28, 0.31)),
                ("facade_c", (0.42, 0.38, 0.33)),
            )
        )
    ]
    roof = mat("roof", (0.2, 0.2, 0.21), 0.9)
    for side, xa in (("left", left - walk - 2.5), ("right", right + walk + 2.5)):
        s = y0
        while s < y1:
            d = rnd.uniform(9, 16)
            if not any(g0 - 4 < s + d and s < g1 + 4 for g0, g1 in gaps if side in sides):
                h_ = rnd.uniform(6, 14)
                xb = xa - 12 if side == "left" else xa + 12
                b_ = box(
                    f"building-{side}-{s:.0f}",
                    min(xa, xb),
                    s,
                    0,
                    max(xa, xb),
                    s + d - 1.2,
                    h_,
                    rnd.choice(concrete),
                )
                b_.data.materials.append(roof)
                b_.data.polygons[1].material_index = 1  # the top face
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
    actors, walkers = [], {}
    for i, a in enumerate(desc["actors"]):
        colour = (
            AMBER if a["role"] == "key" else GREY if a["role"] == "other" else (0.55, 0.57, 0.6)
        )
        name = f"actor{i}-{a['class']}"
        kind, _, variant = a["drawn_as"].partition(":")
        fig = None
        if kind == "person" and variant in ("adult", "child") and not args.procedural:
            fig = look.pedestrian(
                bpy,
                scene,
                name,
                desc["scenario"]["id"],
                1.2 if variant == "child" else 1.72,
                colour if a["role"] == "key" else (0.25, 0.3, 0.4),
            )
        if fig:
            o, rig, action = fig
            walkers[name] = (rig, action)
        elif kind == "person":
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

    # -------- street furniture, kept clear of what the description places
    avoid = []  # (x, y, r): points nothing may stand near
    for a in desc["actors"]:
        for i in range(21):
            x, y, _ = point_at(a["path"], length(a["path"]) * i / 20)
            avoid.append((x, y, 2.0))
    for i in range(41):
        x, y, _ = point_at(desc["ego"]["path"], length(desc["ego"]["path"]) * i / 40)
        avoid.append((x, y, 1.0))
    if "crosswalk" in rd:
        avoid += [(x, y, 2.5) for x in (left - walk / 2, right + walk / 2) for y in rd["crosswalk"]]
    if "speed_sign" in rd:
        avoid.append((*rd["speed_sign"]["at"], 1.5))
    lamp_ys = list(range(int(y0) + 10, int(y1), 28))
    for side_x in (left - walk + 0.5, right + walk - 0.5):
        avoid += [(side_x, ly, 2.0) for ly in lamp_ys]
    sx_ = rd.get("stop_line")
    if sx_ is not None:
        avoid += [(x, sx_, 2.0) for x in (left - walk / 2, right + walk / 2)]
    occ = desc["occlusion"]

    def keep_clear(x, y, r):
        if any(g0 - 3 < y < g1 + 3 for g0, g1 in gaps):
            return False
        if "crosswalk" in rd and rd["crosswalk"][0] - 3 < y < rd["crosswalk"][1] + 3:
            return False
        if occ and min(p[1] for p in occ) - 3 < y < max(p[1] for p in occ) + 3 and x > 0:
            return False
        return all(math.dist((x, y), (ax, ay)) > r + ar for ax, ay, ar in avoid)

    furniture = look.street_furniture(
        bpy,
        scene,
        assets,
        random.Random(desc["scenario"]["id"] + ":furniture"),
        [
            ("left", left - walk + 0.9, y0 + 4, y1 - 4),
            ("right", right + walk - 0.9, y0 + 4, y1 - 4),
        ],
        keep_clear,
    )

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
    light = cond["light"]
    flat = {
        "day": ((0.5, 0.66, 0.9), 1.0),
        "low-sun": ((0.75, 0.62, 0.45), 1.2),
        "dusk": ((0.28, 0.22, 0.32), 0.45),
        "night": ((0.015, 0.02, 0.035), 0.5),
        "unlit": ((0.01, 0.012, 0.02), 0.35),
    }[light]
    sky_slot = look.sky(
        bpy, scene, assets, light, bool(cond.get("rain") or cond.get("visibility")), flat
    )
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
        rain_beyond = bool(beyond) and "ODD-10" in beyond["attributes"]
        drops = mat(
            "rain",
            (0.8, 0.85, 0.9),
            0.1,
            emit=0.9 if light in ("night", "unlit", "dusk") else 0.5,
            alpha=0.35,
        )
        v, f = [], []
        for zone, count, ylo, yhi in (
            ("in", n, -8.0, beyond["y"] if rain_beyond else 80.0),
            ("beyond", 3 * n if rain_beyond else 0, beyond["y"] if beyond else 0, 110.0),
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
    aim = Vector(desc["camera"]["look"]) - Vector(desc["camera"]["pos"])
    cam.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam
    d = 1.0
    vw = 36 / cam_d.lens * d
    vh = vw * H / W

    def at(px, py):
        return ((px / W - 0.5) * vw, (0.5 - py / H) * vh)

    texts, hud = [], []
    for i, (px, py, pw, ph, op) in enumerate(panels()):
        (x0, y0_), (x1, y1_) = at(px, py), at(px + pw, py + ph)
        pm = mat(f"panel-{i}", (0.03, 0.035, 0.04), 1.0, emit=1.0, alpha=op)
        hud.append(
            obj(
                f"panel-{i}",
                [(x0, y0_, -d), (x1, y0_, -d), (x1, y1_, -d), (x0, y1_, -d)],
                [(0, 1, 2, 3)],
                pm,
                parent=cam,
            )
        )
    for i, t in enumerate(hud_texts(desc)):
        k = vw / W
        if "swatch" in t:
            (x0, y0_), (x1, y1_) = at(t["x"], t["y"]), at(t["x"] + 16, t["y"] + 12)
            hud.append(
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
        hud.append(o)
        texts.append(body)

    # -------- motion
    n_f = scene.frame_end + 1
    walked = {name: [] for name in walkers}
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
            if o.name in walked:
                d0 = walked[o.name][-1] if walked[o.name] else 0.0
                p0 = o.location.copy() if walked[o.name] else None
                walked[o.name].append(d0 + (math.dist((x, y), (p0.x, p0.y)) if p0 else 0.0))
            o.location = (x, y, 0)
            if len(a["path"]) > 1:
                o.rotation_euler = (0, 0, hd)
                o.keyframe_insert("rotation_euler", frame=fr)
            o.keyframe_insert("location", frame=fr)
    for name, (rig, action) in walkers.items():
        look.walk(rig, action, walked[name])
    scene.frame_set(still)
    built = {"ego": [round(ego.location.x, 2), round(ego.location.y, 2)]}
    for o, a in actors:
        built[o.name] = [round(o.location.x, 2), round(o.location.y, 2)]
    weather = [o for o in scene.objects if o.name in ("rain", "fog", "fog-beyond")]
    names = {o.name for o in scene.objects}
    drawn = {
        "light": light,
        "wet": wet,
        "rain": "rain" in names,
        "fog": "fog" in names,
        "beyond": sorted(n for n in ("fog-beyond", "odd-limit") if n in names),
        "features": sorted(feats),
        "stop_line": "stop-line" in names,
        "speed_sign": "speed-sign" in names,
        "occlusion": "occlusion" in names,
    }
    ctx = {"scene": scene, "camera": cam, "ego": ego, "actors": actors, "hud": hud}
    ctx["weather"], ctx["ego_size"] = weather, (ego_w, hi_[1] - lo_[1], hi_[2])
    return ctx, {
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
        "drawn": drawn,
        "look": {
            "assets": assets.used(
                {"asphalt", "concrete", "grass", "facade_a", "facade_b", "facade_c", sky_slot}
                | set(furniture)
            ),
            "furniture": furniture,
            "pedestrians": "Quaternius (CC0)" if walkers else "primitives",
        },
        "texts": texts,
    }


def text_obj(bpy, body: str, size: float, material, scene=None):  # pragma: no cover - Blender
    cu = bpy.data.curves.new("text", "FONT")
    cu.body = body
    cu.size = size
    o = bpy.data.objects.new("text", cu)
    o.data.materials.append(material)
    (scene or bpy.context.scene).collection.objects.link(o)
    return o


def render_view(bpy, scene, cam, frame: int, size: tuple[int, int], samples: int, path: Path):
    """One view of the 3D scene to a PNG, at SUPERSAMPLE times its size on the dashboard."""
    scene.camera = cam  # pragma: no cover - needs Blender
    scene.frame_set(frame)
    scene.render.resolution_x, scene.render.resolution_y = (round(v * SUPERSAMPLE) for v in size)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True, scene=scene.name)


def tags_at(bpy, ctx: dict, desc: dict, cam, size: tuple[int, int]) -> list[dict]:
    """The labels of the ego and the road users on the chase view, at the current frame."""
    from bpy_extras.object_utils import world_to_camera_view  # pragma: no cover
    from mathutils import Vector

    scene = ctx["scene"]
    heights = {"person": 2.0, "box": 3.4}
    items = [(ctx["ego"], "Ego robotaxi (choreography)", HEX["blue"], ctx["ego_size"][2] + 0.5)]
    for o, a in ctx["actors"]:
        role = {"key": "", "parked": "parked ", "other": ""}[a["role"]]
        label = f"{role}{a['label']} (qualitative)".capitalize()
        colour = HEX["amber"] if a["role"] == "key" else INK2
        items.append((o, label, colour, heights.get(a["drawn_as"].partition(":")[0], 1.9)))
    out = []
    for o, label, colour, h in items:
        p = world_to_camera_view(scene, cam, Vector((o.location.x, o.location.y, h)))
        if p.z <= 0 or not (0 <= p.x <= 1 and 0 <= p.y <= 1):
            continue
        out.append({"label": label, "colour": colour, "x": p.x * size[0], "y": (1 - p.y) * size[1]})
    return out


def dashboard(args, desc: dict, ctx: dict, work: Path, out: Path, manifest: dict):
    """Render the views and lay them out as the review dashboard <id>.jpg."""  # pragma: no cover
    import bpy
    from mathutils import Vector

    scene, ego = ctx["scene"], ctx["ego"]
    sid = desc["scenario"]["id"]
    work.mkdir(parents=True, exist_ok=True)
    for o in ctx["hud"]:
        o.hide_render = True
    n_f = manifest["render"]["frames"]
    still = manifest["render"]["still_frame"]

    fwd_d = bpy.data.cameras.new("forward")
    fwd_d.lens, fwd_d.clip_start = 18, 0.1
    fwd = bpy.data.objects.new("forward", fwd_d)
    fwd.parent = ego
    fwd.location = (0, ctx["ego_size"][1] / 2 - 0.4, ctx["ego_size"][2] + 0.1)
    fwd.rotation_euler = (math.radians(84), 0, 0)  # along +y, slightly down
    scene.collection.objects.link(fwd)

    top_d = bpy.data.cameras.new("top")
    top_d.type = "ORTHO"
    ys = [p[1] for p in desc["ego"]["path"]] + [desc["hazard"][1], desc["hazard"][3]]
    lo, hi = min(ys) - 8, max(ys) + 10
    top_d.ortho_scale = hi - lo
    top_d.clip_end = 200
    top = bpy.data.objects.new("top", top_d)
    top.location = (0, (lo + hi) / 2, 80)
    top.rotation_euler = (0, 0, math.pi / 2)  # the ego drives from left to right
    scene.collection.objects.link(top)

    rig_d = bpy.data.cameras.new("chase")
    rig_d.lens, rig_d.clip_start, rig_d.clip_end = 26, 0.1, 600
    rig = bpy.data.objects.new("chase", rig_d)
    rig.parent = ego
    rig.location = CHASE_RIG[0]
    aim = Vector(CHASE_RIG[1]) - Vector(CHASE_RIG[0])
    rig.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(rig)
    chase = rig

    views = {}
    size = (CHASE[2], CHASE[3])
    render_view(bpy, scene, chase, still, size, args.samples, work / "chase.png")
    views["chase"] = work / "chase.png"
    tags = tags_at(bpy, ctx, desc, chase, size)
    render_view(bpy, scene, fwd, still, FORWARD[2:], args.samples, work / "forward.png")
    views["forward"] = work / "forward.png"
    for o in ctx["weather"]:
        o.hide_render = True
    render_view(bpy, scene, top, still, TOP[2:], max(8, args.samples // 2), work / "top.png")
    views["top"] = work / "top.png"
    for o in ctx["weather"]:
        o.hide_render = False
    for i, (u, _) in enumerate(moments(desc)):
        f = round(u * (n_f - 1))
        p = work / f"thumb{i}.png"
        render_view(bpy, scene, chase, f, (THUMB_W, THUMB_H), max(8, args.samples // 3), p)
        views[f"thumb{i}"] = p
    scene.frame_set(still)
    for o in ctx["hud"]:
        o.hide_render = False

    layout = dashboard_layout(desc, tags, manifest.get("look"))
    ds = bpy.data.scenes.new("dashboard")
    ds.render.engine = "CYCLES"
    ds.cycles.device = "CPU"
    ds.cycles.samples = 16
    ds.cycles.filter_width = 0.5  # images sit pixel on pixel: a wide filter would blur them
    ds.cycles.use_denoising = False
    ds.cycles.seed = 1
    ds.view_settings.view_transform = "Standard"
    ds.render.resolution_x, ds.render.resolution_y = DW, DH
    ds.render.resolution_percentage = 100
    cam_d = bpy.data.cameras.new("dashboard")
    cam_d.type, cam_d.ortho_scale, cam_d.sensor_fit = "ORTHO", DW, "HORIZONTAL"
    cam_d.clip_end = 1000
    cam = bpy.data.objects.new("dashboard", cam_d)
    cam.location = (DW / 2, -DH / 2, 500)
    ds.collection.objects.link(cam)
    ds.camera = cam
    mats: dict[str, object] = {}

    def emission(key, colour=None, image=None):
        if key in mats:
            return mats[key]
        m = bpy.data.materials.new(key)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        em = nt.nodes.new("ShaderNodeEmission")
        if image is not None:
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(str(image[0]))
            tex.image.scale(*image[1])  # box filter down to its size on the dashboard
            tex.interpolation = "Closest"
            nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        else:
            em.inputs["Color"].default_value = (*srgb(colour), 1.0)
        nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
        mats[key] = m
        return m

    def plane(name, x, y, w, h, z, material):
        me = bpy.data.meshes.new(name)
        me.from_pydata(
            [(x, -y, z), (x + w, -y, z), (x + w, -y - h, z), (x, -y - h, z)], [], [(0, 1, 2, 3)]
        )
        uv = me.uv_layers.new()
        for loop, co in zip(uv.data, ((0, 1), (1, 1), (1, 0), (0, 0))):
            loop.uv = co
        o = bpy.data.objects.new(name, me)
        o.data.materials.append(material)
        ds.collection.objects.link(o)

    for i, e in enumerate(layout):
        z = i * 0.01
        if "rect" in e:
            x, y, w, h = e["rect"]
            if e.get("edge"):
                plane(
                    f"edge{i}",
                    x - 1,
                    y - 1,
                    w + 2,
                    h + 2,
                    z - 0.005,
                    emission(e["edge"], e["edge"]),
                )
            plane(f"rect{i}", x, y, w, h, z, emission(e["fill"], e["fill"]))
        elif "image" in e:
            x, y, w, h = e["box"]
            img = emission(f"img-{e['image']}", image=(views[e["image"]], (round(w), round(h))))
            plane(f"img{i}", x, y, w, h, z, img)
        else:
            o = text_obj(
                bpy, "\n".join(e["text"]), e["size"], emission(e["colour"], e["colour"]), ds
            )
            o.data.space_line = 1.3 / 1.2
            o.data.align_y = "TOP"
            o.location = (e["x"], -e["y"], z)
    ds.render.image_settings.file_format = "JPEG"
    ds.render.image_settings.quality = 85
    ds.render.filepath = str(out / f"{sid}.jpg")
    bpy.ops.render.render(write_still=True, scene=ds.name)
    manifest["texts"] = dashboard_texts(layout)
    manifest["tags"] = [t["label"] for t in tags]
    manifest["moments"] = [label for _, label in moments(desc)]
    manifest["dashboard"] = f"{sid}.jpg"
    manifest["dashboard_sha256"] = hashlib.sha256((out / f"{sid}.jpg").read_bytes()).hexdigest()
    manifest["render"]["dashboard_samples"] = {"chase": args.samples, "dashboard": 16}
    manifest["render"]["supersample"] = SUPERSAMPLE


def clip(args, desc: dict, ctx: dict, out: Path, manifest: dict) -> None:  # pragma: no cover
    """The chase view as an MP4, with the overlay of the description on the frame."""
    import bpy

    scene = ctx["scene"]
    sid = desc["scenario"]["id"]
    scene.camera = ctx["camera"]
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = args.scale
    scene.cycles.samples = args.samples
    s = scene.render
    if hasattr(s.image_settings, "media_type"):
        s.image_settings.media_type = "VIDEO"
    s.image_settings.file_format = "FFMPEG"
    s.ffmpeg.format = "MPEG4"
    s.ffmpeg.codec = "H264"
    s.ffmpeg.constant_rate_factor = "MEDIUM"
    s.filepath = str(out / f"{sid}-")
    bpy.ops.render.render(animation=True, scene=scene.name)
    made = sorted(out.glob(f"{sid}-*.mp4"))
    if made:
        made[-1].replace(out / f"{sid}.mp4")
        manifest["animation"] = f"{sid}.mp4"


def main(argv: list[str]) -> int:  # pragma: no cover - needs Blender
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "scene", type=Path, nargs="+", help="scene description(s), tools/sim/scenes/*.json"
    )
    ap.add_argument("--out", type=Path, default=Path("build/sim"), help="dashboards and manifests")
    ap.add_argument("--work", type=Path, default=Path("build/sim/work"), help="the separate views")
    ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--scale", type=int, default=100, help="clip size in percent of 1600 x 900")
    ap.add_argument("--animate", action="store_true", help="also render the clip as MP4")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--blend", action="store_true", help="also save the .blend file")
    ap.add_argument(
        "--verify", action="store_true", help="fail when the scene differs from the description"
    )
    ap.add_argument("--no-render", action="store_true", help="build and verify only")
    ap.add_argument(
        "--procedural", action="store_true", help="ignore the fetched assets: the procedural look"
    )
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    failed = 0
    for path in args.scene:
        raw = path.read_bytes()
        desc = json.loads(raw)
        sid = desc["scenario"]["id"]
        ctx, manifest = build(desc, args)
        manifest["description"] = f"tools/sim/scenes/{path.name}"
        manifest["description_sha256"] = hashlib.sha256(raw).hexdigest()
        manifest["clip_texts"] = manifest.pop("texts")
        if not args.no_render:
            dashboard(args, desc, ctx, args.work / sid, args.out, manifest)
            if args.animate:
                clip(args, desc, ctx, args.out, manifest)
        if args.blend:
            import bpy

            bpy.ops.wm.save_as_mainfile(filepath=str(args.out / f"{sid}.blend"))
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
            + ("" if args.no_render else f", dashboard {args.out / (sid + '.jpg')}")
            + (f", {len(errs)} difference(s)" if errs else ", matches its description")
        )
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]))
