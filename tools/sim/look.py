"""The look of the scenario scenes in Blender: skies, ground and facade materials, street furniture, pedestrians.

build_blend.py calls these while it builds a scene. With the CC0 assets of fetch_assets.py present (tools/sim/assets/,
recorded in assets.lock.json), the sky is an HDRI, the road, sidewalks, verges and facades are scanned PBR
textures, and street trees, bins and hydrants line the sidewalks. Without them each of these falls back to a
procedural look, so a scene always builds. The look never moves anything the description places: the road, the
road users, the overlays and the conditions are build_blend.py's, and verify() checks them the same way under either
look. Pedestrians are the CC0 Quaternius figures of models/people/, walking by the distance they cover.

Runs inside Blender only.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
LOCK = HERE / "assets.lock.json"
PEOPLE = (("pedestrian_male.glb", 1.78), ("pedestrian_female.glb", 1.66))
WALK_CYCLE_M = (
    1.45  # one loop of Walk_Loop (two steps) per this many metres walked, as in LionDriver
)
SKY = {  # light -> HDRI slot and its strength; rain or mist switch to the overcast sky
    "day": ("hdri_day", 1.0),
    "low-sun": ("hdri_low_sun", 1.2),
    "dusk": ("hdri_low_sun", 0.18),
    "night": ("hdri_night", 0.5),
    "unlit": ("hdri_night", 0.25),
}


class Assets:
    """The fetched CC0 assets, as the lock records them; a slot counts only with every file present."""

    def __init__(self, root: Path = ASSETS, lock: Path = LOCK, use: bool = True):
        self.root = root
        self.slots = json.loads(lock.read_text(encoding="utf-8"))["slots"] if lock.exists() else {}
        self.use = use

    def have(self, slot: str) -> bool:
        s = self.slots.get(slot)
        return bool(
            self.use and s and all((self.root / slot / rel).exists() for rel in s.get("files", {}))
        )

    def path(self, slot: str, rel: str) -> Path:
        return self.root / slot / rel

    def used(self, slots: set[str]) -> list[dict]:
        return [
            {"slot": n, "id": self.slots[n]["id"], "source": self.slots[n]["source"]}
            for n in sorted(slots)
            if self.have(n)
        ]


def _nodes(m):
    m.use_nodes = True
    return m.node_tree.nodes, m.node_tree.links


def surface(bpy, assets: Assets, name: str, slot: str, fallback: str, base, rough=0.7, wet=False):
    """A material for the road, a sidewalk, a verge or a facade: the slot's PBR maps projected in world metres
    (box projection, so no UVs are needed), or a procedural stand-in of the kind `fallback` names.
    """
    m = bpy.data.materials.new(name)
    nodes, links = _nodes(m)
    p = nodes["Principled BSDF"]
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    if assets.have(slot):
        s = assets.slots[slot]
        size = s.get("size_m", 1.0)
        sx, sy = (size, size) if not isinstance(size, list) else size
        mapping.inputs["Scale"].default_value = (1 / sx, 1 / sy, 1 / sy)

        def tex(rel, colour=True):
            t = nodes.new("ShaderNodeTexImage")
            t.image = bpy.data.images.load(str(assets.path(slot, rel)), check_existing=True)
            if not colour:
                t.image.colorspace_settings.name = "Non-Color"
            t.projection, t.projection_blend = "BOX", 0.15
            links.new(mapping.outputs["Vector"], t.inputs["Vector"])
            return t

        col = tex("color.jpg")
        tint = s.get("tint", 1.0) * (0.55 if wet else 1.0)
        mix = nodes.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        links.new(col.outputs["Color"], mix.inputs["A"])
        mix.inputs["B"].default_value = (tint, tint, tint, 1)
        links.new(mix.outputs["Result"], p.inputs["Base Color"])
        r = tex("roughness.jpg", False)
        if wet:
            scale = nodes.new("ShaderNodeMath")
            scale.operation = "MULTIPLY"
            scale.inputs[1].default_value = 0.25
            links.new(r.outputs["Color"], scale.inputs[0])
            links.new(scale.outputs[0], p.inputs["Roughness"])
        else:
            links.new(r.outputs["Color"], p.inputs["Roughness"])
        nmap = nodes.new("ShaderNodeNormalMap")
        links.new(tex("normal.jpg", False).outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], p.inputs["Normal"])
        return m
    # procedural stand-ins
    dark = [c * (0.55 if wet else 1.0) for c in base]
    if fallback == "facade":
        b = nodes.new("ShaderNodeTexBrick")  # a grid of windows in a wall
        b.inputs["Scale"].default_value = 1.0
        b.inputs["Brick Width"].default_value = 2.6
        b.inputs["Row Height"].default_value = 3.2
        b.inputs["Mortar Size"].default_value = 0.9
        b.offset = 0.0
        b.inputs["Color1"].default_value = (0.08, 0.1, 0.13, 1)
        b.inputs["Color2"].default_value = (0.12, 0.14, 0.17, 1)
        b.inputs["Mortar"].default_value = (*base, 1)
        # along the wall (x + y: walls run along one axis) and up it (z), so windows sit in rows
        sep = nodes.new("ShaderNodeSeparateXYZ")
        add = nodes.new("ShaderNodeMath")
        comb = nodes.new("ShaderNodeCombineXYZ")
        links.new(coord.outputs["Object"], sep.inputs["Vector"])
        links.new(sep.outputs["X"], add.inputs[0])
        links.new(sep.outputs["Y"], add.inputs[1])
        links.new(add.outputs[0], comb.inputs["X"])
        links.new(sep.outputs["Z"], comb.inputs["Y"])
        links.new(comb.outputs["Vector"], b.inputs["Vector"])
        links.new(b.outputs["Color"], p.inputs["Base Color"])
        p.inputs["Roughness"].default_value = rough
        return m
    n = nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = {"asphalt": 9.0, "concrete": 2.0, "grass": 4.0}.get(
        fallback, 3
    )
    n.inputs["Detail"].default_value = 8.0
    links.new(mapping.outputs["Vector"], n.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.7 for c in dark], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.3) for c in dark], 1)
    links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    links.new(n.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.15 if wet else rough
    return m


def sky(bpy, scene, assets: Assets, light: str, overcast: bool, flat) -> str:
    """The world: an HDRI sky for the light (overcast under rain or mist), else the flat colour `flat`."""
    world = bpy.data.worlds.new("world")
    scene.world = world
    nodes, links = _nodes(world)
    bg = nodes["Background"]
    slot, strength = SKY[light]
    if overcast and light in ("day", "low-sun"):
        slot, strength = "hdri_overcast", 0.8
    elif overcast and light == "dusk":
        slot, strength = "hdri_overcast", 0.15
    if assets.have(slot):
        env = nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str(assets.path(slot, "sky.hdr")), check_existing=True)
        links.new(env.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = strength
        return slot
    bg.inputs["Color"].default_value = (*flat[0], 1.0)
    bg.inputs["Strength"].default_value = flat[1]
    return ""


def model(bpy, scene, assets: Assets, slot: str, height: float):
    """A fetched glTF as a hidden collection scaled to `height` metres, to be placed by instances; None when the
    slot is missing."""
    if not assets.have(slot):
        return None
    gltf = next(rel for rel in assets.slots[slot]["files"] if rel.endswith(".gltf"))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets.path(slot, gltf)))
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    top = max((o.matrix_world @ _v(c)).z for o in meshes for c in o.bound_box)
    k = height / top if top > 0 else 1.0
    for o in new:
        if o.parent is None:
            o.scale = tuple(v * k for v in o.scale)
            o.location = tuple(v * k for v in o.location)
    coll = bpy.data.collections.new(f"kit-{slot}")  # not in the scene: only its instances render
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return coll


def _v(c):
    from mathutils import Vector

    return Vector(c)


def place(bpy, scene, coll, name: str, x: float, y: float, yaw: float, scale: float = 1.0):
    e = bpy.data.objects.new(name, None)
    e.instance_type, e.instance_collection = "COLLECTION", coll
    e.location, e.rotation_euler, e.scale = (x, y, 0.15), (0, 0, yaw), (scale, scale, scale)
    scene.collection.objects.link(e)
    return e


def street_furniture(bpy, scene, assets: Assets, rnd: random.Random, rows, keep_clear) -> dict:
    """Street trees, bins and hydrants along the sidewalks: `rows` are (side, x, y0, y1), `keep_clear(x, y, r)` says
    whether a spot is free (crosswalks, junctions, road users' paths, signs and poles). Returns what was placed.
    """
    kits = {
        "tree": model(bpy, scene, assets, "tree", 5.5),
        "bin": model(bpy, scene, assets, "bin", 0.95),
        "hydrant": model(bpy, scene, assets, "hydrant", 0.8),
    }
    placed = {k: 0 for k in kits}
    for side, x, y0, y1 in rows:
        y = y0 + rnd.uniform(2, 8)
        while y < y1:
            if kits["tree"] is not None and keep_clear(x, y, 3.0):
                place(
                    bpy,
                    scene,
                    kits["tree"],
                    f"tree-{side}-{y:.0f}",
                    x,
                    y,
                    rnd.uniform(0, 6.28),
                    rnd.uniform(0.85, 1.1),
                )
                placed["tree"] += 1
            for kind, odds, dx in (("bin", 0.35, 1.6), ("hydrant", 0.2, -1.8)):
                yy = y + dx
                if kits[kind] is not None and rnd.random() < odds and keep_clear(x, yy, 1.2):
                    place(
                        bpy,
                        scene,
                        kits[kind],
                        f"{kind}-{side}-{yy:.0f}",
                        x,
                        yy,
                        math.pi / 2 if side == "left" else -math.pi / 2,
                    )
                    placed[kind] += 1
            y += rnd.uniform(11, 15)
    return {k: v for k, v in placed.items() if v}


def pedestrian(bpy, scene, name: str, seed: str, height: float, shirt):
    """A Quaternius CC0 figure facing +y, scaled to `height`, with its shirt in `shirt`; (root, rig, walk action) or
    None when the file is missing."""
    pick = sum(map(ord, name + seed))
    fname, _ = PEOPLE[pick % len(PEOPLE)]
    path = HERE / "models" / "people" / fname
    if not path.exists():
        return None
    objs, acts = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path))
    new = [o for o in bpy.data.objects if o not in objs]
    rig = next(o for o in new if o.type == "ARMATURE")

    def under_rig(o):
        while o is not None:
            if o == rig:
                return True
            o = o.parent
        return False

    keep = [o for o in new if under_rig(o)]
    for o in [o for o in new if not under_rig(o)]:  # helpers the file carries (an icosphere)
        bpy.data.objects.remove(o)
    new = keep
    walk = next((a for a in bpy.data.actions if a not in acts and "Walk" in a.name), None) or next(
        a for a in bpy.data.actions if a not in acts
    )
    if rig.animation_data:
        rig.animation_data.action = None
        for t in list(rig.animation_data.nla_tracks):
            rig.animation_data.nla_tracks.remove(t)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        scene.collection.objects.link(o)
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    eyes = next((o for o in meshes if o.name.startswith("Eyes")), None)
    fwd = (eyes.matrix_world.translation if eyes else _v((0, 1, 0))) - rig.matrix_world.translation
    top = max((o.matrix_world @ _v(c)).z for o in meshes for c in o.bound_box)
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)
    rig.parent = root
    rig.location = (0, 0, 0)
    rig.rotation_euler.z += math.pi / 2 - math.atan2(fwd.y, fwd.x)  # face +y
    rig.scale = tuple(v * height / top for v in rig.scale)
    mat = bpy.data.materials.new(f"{name}-shirt")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*shirt, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
    for o in meshes:
        for k, m in enumerate(o.data.materials):
            if m and m.name.split(".")[0] == "shirt":
                o.data.materials[k] = mat
    return root, rig, walk


def walk(rig, action, distances: list[float]):
    """Play the walk loop by the distance walked at each frame (frame i has distances[i]); still when standing."""
    f0, f1 = action.frame_range
    rig.animation_data_create()
    strip = rig.animation_data.nla_tracks.new().strips.new("walk", int(f0), action)
    strip.use_animated_time = True
    for f, dist in enumerate(distances):
        strip.strip_time = f0 + ((dist / WALK_CYCLE_M) % 1.0) * (f1 - f0)
        strip.keyframe_insert("strip_time", frame=f)
