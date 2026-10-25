#!/usr/bin/env python3
"""Unit tests of the README figure tools: the FBX reader, the models, the renderer, the facts and
the figures themselves.

python3 -m unittest discover -s tools/readme -p 'test_*.py' -v
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import re
import struct
import sys
import unittest
from xml.sax.saxutils import escape
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))

import facts as fx  # noqa: E402
import fbx  # noqa: E402
import figures  # noqa: E402
import mesh  # noqa: E402
import render3d as r3  # noqa: E402

# ---------------------------------------------------------------- a tiny binary FBX, written here


def _prop(v) -> bytes:
    if isinstance(v, str):
        b = v.encode()
        return b"S" + struct.pack("<I", len(b)) + b
    if isinstance(v, bool):
        return b"C" + struct.pack("<?", v)
    if isinstance(v, int):
        return b"L" + struct.pack("<q", v)
    if isinstance(v, float):
        return b"D" + struct.pack("<d", v)
    code, fmt, items, compress = v  # an array: ("d" | "i", fmt, values, compress)
    raw = struct.pack(f"<{len(items)}{fmt}", *items)
    data = zlib.compress(raw) if compress else raw
    return code.encode() + struct.pack("<III", len(items), 1 if compress else 0, len(data)) + data


def _node(name: str, props=(), children=(), offset=0, wide=True) -> bytes:
    head = "<QQQB" if wide else "<IIIB"
    hsize = struct.calcsize(head)
    pbytes = b"".join(_prop(p) for p in props)
    sentinel = b"\0" * hsize if children else b""
    body_start = offset + hsize + len(name) + len(pbytes)
    kids, pos = b"", body_start
    for c in children:
        k = c(pos)
        kids += k
        pos += len(k)
    end = pos + len(sentinel)
    return (
        struct.pack(head, end, len(props), len(pbytes), len(name))
        + name.encode()
        + pbytes
        + kids
        + sentinel
    )


def N(name, props=(), children=()):  # noqa: N802
    return lambda offset: _node(name, props, children, offset)


def tiny_fbx() -> bytes:
    """One unit cube (as six quads) on a model translated by (10, 0, 0), with a geometric offset of
    (0, 5, 0), in a file with y up and centimetre units."""
    verts = [
        x
        for v in [
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 0, 1),
            (1, 1, 1),
            (0, 1, 1),
        ]
        for x in v
    ]
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    idx = [i for q in quads for i in (q[0], q[1], q[2], ~q[3])]
    p70 = lambda *ps: N("Properties70", children=[N("P", p) for p in ps])  # noqa: E731
    objects = N(
        "Objects",
        children=[
            N("Geometry", (100, "cube\x00\x01Geometry", "Mesh"), [
                N("Vertices", [("d", "d", [float(x) for x in verts], True)]),
                N("PolygonVertexIndex", [("i", "i", idx, False)]),
            ]),
            N("Model", (200, "Cube\x00\x01Model", "Mesh"), [
                p70(("Lcl Translation", "Lcl Translation", "", "A", 10.0, 0.0, 0.0),
                    ("GeometricTranslation", "Vector3D", "Vector", "", 0.0, 5.0, 0.0)),
            ]),
            N("Material", (300, "Paint\x00\x01Material", "")),
        ],
    )  # fmt: skip
    conns = N(
        "Connections",
        children=[N("C", ("OO", 100, 200)), N("C", ("OO", 200, 0)), N("C", ("OO", 300, 200))],
    )
    settings = N(
        "GlobalSettings",
        children=[
            p70(
                ("UpAxis", "int", "Integer", "", 1),
                ("UnitScaleFactor", "double", "Number", "", 1.0),
            )
        ],
    )
    data = fbx.MAGIC + b"\x1a\x00" + struct.pack("<I", 7500)
    for n in (settings, objects, conns):
        data += n(len(data))
    return data + b"\0" * 25


class Fbx(unittest.TestCase):
    def test_reads_nodes_properties_and_compressed_arrays(self):
        root = fbx.parse(tiny_fbx())
        geo = root.child("Objects").child("Geometry")
        self.assertEqual(geo.props[2], "Mesh")
        self.assertEqual(len(geo.child("Vertices").props[0]), 24)
        self.assertEqual(geo.child("PolygonVertexIndex").props[0][3], ~1)

    def test_meshes_triangulate_and_apply_transforms(self):
        scene = fbx.meshes(fbx.parse(tiny_fbx()))
        self.assertEqual((scene.up_axis, scene.unit_cm), (1, 1.0))
        (m,) = scene.meshes
        self.assertEqual((m.name, len(m.triangles), set(m.materials)), ("Cube", 12, {"Paint"}))
        self.assertEqual(min(v[0] for v in m.vertices), 10.0)  # model translation
        self.assertEqual(min(v[1] for v in m.vertices), 5.0)  # geometric offset
        local = fbx.meshes(fbx.parse(tiny_fbx()), local=True).meshes[0]
        self.assertEqual(
            min(v[0] for v in local.vertices), 0.0
        )  # local keeps only the geometric offset

    def test_refuses_other_files(self):
        with self.assertRaises(fbx.FbxError):
            fbx.parse(b"; FBX 7.4.0 project file\n")


# ---------------------------------------------------------------- models


def cube(cls="body") -> mesh.Model:
    verts = [(x, y, z) for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)]
    i = {v: n for n, v in enumerate(verts)}
    faces = [  # outward winding
        ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)),
        ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
        ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
        ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
        ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)),
        ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
    ]
    tris = []
    for f in faces:
        a, b, c, d = (i[tuple(float(t) for t in p)] for p in f)
        tris += [(a, b, c), (a, c, d)]
    return mesh.ground_centre(mesh.Model("cube", verts, tris, [cls] * len(tris)))


class Models(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kiri = mesh.load_kiri()
        cls.pack = mesh.load_pack()

    def test_ground_centre(self):
        lo, hi = cube().bounds()
        self.assertEqual((lo, hi), ((-0.5, -0.5, 0.0), (0.5, 0.5, 1.0)))

    def test_simplify_merges_vertices_and_keeps_classes_apart(self):
        m = cube()
        self.assertEqual(len(mesh.simplify(m, 0.01).triangles), 12)
        self.assertEqual(len(mesh.simplify(m, 10.0).triangles), 0)  # everything collapses
        two = mesh._merge(
            "two", [("body", m.vertices, m.triangles), ("glass", m.vertices, m.triangles)]
        )
        self.assertEqual(sorted(set(mesh.simplify(two, 0.01).classes)), ["body", "glass"])

    def test_ego_vehicle_is_a_car_sized_sedan_without_badges(self):
        w, ln, h = self.kiri.size()
        self.assertTrue(1.6 < w < 1.9 and 4.2 < ln < 4.6 and 1.3 < h < 1.6, self.kiri.size())
        self.assertEqual(set(self.kiri.classes) - set(mesh.CLASSES), set())

    def test_every_vehicle_faces_forward(self):
        for name, m in [("kiri10", self.kiri), *self.pack.items()]:
            ys = {c: [] for c in ("light_front", "light_rear", "wheel")}
            for t, c in zip(m.triangles, m.classes):
                if c in ys:
                    ys[c].append(sum(m.vertices[i][1] for i in t) / 3)
            front = sum(ys["light_front"]) / len(ys["light_front"])
            rear = sum(ys["light_rear"]) / len(ys["light_rear"])
            self.assertGreater(front, rear, name)
            self.assertTrue(ys["wheel"], name)

    def test_pack_has_the_traffic_cars(self):
        self.assertEqual(sorted(self.pack), sorted(mesh.PACK_CARS.values()))
        for name, m in self.pack.items():
            self.assertTrue(3.4 < m.size()[1] < 5.4, (name, m.size()))


# ---------------------------------------------------------------- renderer


class Render(unittest.TestCase):
    def test_camera_projects_the_point_ahead_to_the_centre(self):
        cam = r3.Camera(pos=(0.0, -10.0, 0.0), pitch=0, focal=500, cx=100, cy=50)
        self.assertEqual(cam(0.0, 0.0, 0.0), (100.0, 50.0))
        x, y = cam(1.0, 0.0, 1.0)
        self.assertAlmostEqual(x, 150.0)
        self.assertAlmostEqual(y, 0.0)

    def test_back_faces_are_culled_and_output_is_deterministic(self):
        cam = r3.Camera(pos=(0.0, -6.0, 3.0), pitch=20, focal=400, cx=200, cy=150)
        _, culled = r3.render(cube(), cam, min_area=0)
        _, both = r3.render(cube(), cam, min_area=0, cull=False)
        count = lambda paths: sum(p.count("Z") for p in paths)  # noqa: E731
        self.assertLess(count(culled), count(both))
        self.assertLessEqual(count(culled), 6)  # at most three faces of a cube are seen
        self.assertEqual(culled, r3.render(cube(), cam, min_area=0)[1])


# ---------------------------------------------------------------- facts


class Facts(unittest.TestCase):
    def test_real_records_give_every_fact(self):
        f = fx.load()
        v = fx.need(f)
        self.assertEqual(v["monitor"], f.elements["EL-02"].asil)
        self.assertTrue(v["dq_qm"].startswith("DQ-002 "))
        self.assertEqual(set(f.limits), set(fx.LIMIT_PATTERNS))
        self.assertEqual(f.standards[0], "UL 4600")

    def test_limit_tag_marks_proposed_values(self):
        self.assertEqual(
            fx.Limit("ODD-03", "roads ≤ 30 mph", True).tag, "roads ≤ 30 mph (proposed)"
        )
        self.assertEqual(fx.Limit("ODD-10", "rain ≤ 2.5 mm/h", False).tag, "rain ≤ 2.5 mm/h")

    def test_missing_decision_is_refused(self):
        f = fx.load()
        with self.assertRaises(fx.FactError):
            f.dq("DQ-999")


# ---------------------------------------------------------------- figures


class Figures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = figures.build()

    def test_scene_figures_say_they_are_concept_illustrations(self):
        for name in ("hero.svg", "scene.svg"):
            text = self.out[figures.OUT / name]
            self.assertIn(figures.STAMP.replace("'", "&apos;").split(" · ")[0], text)
            self.assertIn("not built yet", text)
            self.assertIn("prefers-reduced-motion", text)

    def test_labels_come_from_the_records(self):
        f = fx.load()
        v = fx.need(f)
        scene = self.out[figures.OUT / "scene.svg"]
        for lim in f.limits.values():
            self.assertIn(lim.tag, scene)
        self.assertIn(v["dq_mrc"], scene)
        arch = self.out[figures.OUT / "architecture.svg"]
        self.assertIn(v["dq_sensors"], arch)
        self.assertIn(f"({v['dbw_aou']})", arch)

    def test_item_figure_lists_every_element_with_its_rating(self):
        f = fx.load()
        item = self.out[figures.OUT / "item.svg"]
        for e in f.elements.values():
            self.assertIn(escape(f"{e.eid}  {e.name}"), item)
        self.assertIn("ILLUSTRATION", item)
        self.assertIn("positions are not decided", item)

    def test_minimal_risk_figure_quotes_the_safe_state(self):
        v = fx.need(fx.load())
        mrc = self.out[figures.OUT / "minimal-risk-condition.svg"]
        self.assertIn(escape(v["sg07_safe_state"]), mrc)
        self.assertIn(v["dq_mrc"], mrc)
        self.assertIn("ILLUSTRATION", mrc)

    def test_odd_figure_quotes_inside_and_outside(self):
        f = fx.load()
        odd = self.out[figures.OUT / "odd.svg"]
        flat = " ".join(re.findall(r">([^<]*)</text>", odd))
        for k in ("ODD-03", "ODD-10", "ODD-11"):
            for part in (f.odd[k].inside, f.odd[k].outside):
                self.assertIn(" ".join(escape(part).split()), flat, k)

    def test_two_ways_and_remote_figures_use_the_records(self):
        v = fx.need(fx.load())
        two = self.out[figures.OUT / "two-ways-to-be-unsafe.svg"]
        self.assertIn(escape(v["sg01_text"].lower()), two)
        self.assertIn("glare", two)
        remote = " ".join(
            re.findall(r">([^<]*)</text>", self.out[figures.OUT / "remote-driving.svg"])
        )
        self.assertIn(escape(v["sg08_text"]), remote)
        self.assertIn(v["dq_remote"], remote)
        self.assertIn("not built yet", remote)

    def test_sizes_stay_reasonable_for_a_readme(self):
        for path, text in self.out.items():
            self.assertLess(len(text.encode()), 450_000, path.name)

    def test_committed_figures_are_current(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(figures.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
