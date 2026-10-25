#!/usr/bin/env python3
"""Unit tests of the scenario scene tools: the scene descriptions and the plain-Python half of
build_blend.py (motion, frame texts, verification). Blender is not needed.

python3 -m unittest discover -s tools/sim -p 'test_*.py' -v
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_blend as bb  # noqa: E402
import scene  # noqa: E402

M, K, F = scene.sc.load(), scene.sc.known(), scene.fx.load()
BY_ID = {s["id"]: s for s in M["scenarios"]}


def describe(sid: str, layout: dict | None = None) -> dict:
    if layout is None:
        return scene.scene(BY_ID[sid], M, K, F)
    saved = scene.LAYOUTS[sid]
    scene.LAYOUTS[sid] = layout
    try:
        return scene.scene(BY_ID[sid], M, K, F)
    finally:
        scene.LAYOUTS[sid] = saved


class Descriptions(unittest.TestCase):
    def test_committed_descriptions_are_current(self):
        for path, text in scene.build().items():
            self.assertEqual(path.read_text(encoding="utf-8"), text, path.name)

    def test_every_render_is_stamped(self):
        self.assertIn("not a simulation result", scene.STAMP)
        for sid in scene.LAYOUTS:
            d = describe(sid)
            self.assertEqual(d["stamp"], scene.STAMP)
            self.assertIn(
                d["stamp"].upper(), " ".join(" ".join(t.get("lines", [])) for t in bb.hud_texts(d))
            )

    def test_samples_lie_inside_the_stated_ranges(self):
        for sid in scene.LAYOUTS:
            s = BY_ID[sid]
            for p, x in zip(s["parameters"], describe(sid)["sample"]["parameters"]):
                if "bound" in p:
                    self.assertIsNone(x["value"], f"{sid}: a bound not yet fixed has no value")
                elif "values" in p:
                    self.assertIn(x["value"], p["values"], sid)
                elif p.get("crosses"):
                    self.assertIsNone(x["value"], f"{sid}: a crossing sweep states no value")
                else:
                    lo = p.get("min", 0)
                    hi = p.get("max", lo)
                    self.assertTrue(lo <= x["value"] <= hi, f"{sid} {p['odd']}: {x['value']}")

    def test_the_draw_is_deterministic(self):
        self.assertEqual(describe("SC-03"), describe("SC-03"))

    def test_labels_come_from_the_records(self):
        d = describe("SC-01")
        s = BY_ID["SC-01"]
        self.assertEqual(d["scenario"]["name"], s["name"])
        self.assertEqual(d["scenario"]["pass"], s["pass"]["criterion"])
        self.assertEqual([g["id"] for g in d["scenario"]["goals"]], scene.sc.stake(s, K))
        for g in d["scenario"]["goals"]:
            self.assertEqual(g["statement"], F.goals[g["id"]][0])
            self.assertEqual(g["asil"], F.goals[g["id"]][1])
        self.assertIn(F.elements["EL-02"].asil, d["legend"]["envelope"])
        self.assertIn(
            F.odd["ODD-12"].attribute, " ".join(p["label"] for p in d["sample"]["parameters"])
        )

    def test_a_pick_outside_the_scenario_is_refused(self):
        lay = copy.deepcopy(scene.LAYOUTS["SC-01"])
        lay["pick"]["ODD-12"] = "low-sun"  # an ODD value, but not one of SC-01's
        with self.assertRaises(scene.SceneError):
            describe("SC-01", lay)

    def test_a_crossing_scenario_needs_where_the_limit_is(self):
        lay = copy.deepcopy(scene.LAYOUTS["SC-14"])
        del lay["odd_limit"]
        with self.assertRaises(scene.SceneError):
            describe("SC-14", lay)

    def test_an_unknown_road_key_is_refused(self):
        lay = copy.deepcopy(scene.LAYOUTS["SC-01"])
        lay["road"]["tunnel"] = True
        with self.assertRaises(scene.SceneError):
            describe("SC-01", lay)

    def test_no_layout_for_restricted_or_remote_link_scenarios(self):
        # The remote link and release scenarios touch the cybersecurity concept; they are not drawn.
        for sid in ("SC-20", "SC-21", "SC-26"):
            self.assertNotIn(sid, scene.LAYOUTS)


class Motion(unittest.TestCase):
    def test_point_at(self):
        pts = [[0, 0], [0, 10], [10, 10]]
        self.assertEqual(bb.point_at(pts, 5)[:2], (0.0, 5.0))
        x, y, hd = bb.point_at(pts, 15)
        self.assertAlmostEqual(x, 5.0)
        self.assertAlmostEqual(y, 10.0)
        self.assertAlmostEqual(hd, -1.5707963, places=5)  # heading right of +y

    def test_ego_stops_at_the_end_of_its_path(self):
        self.assertEqual(bb.ego_share(0.0, True), 0.0)
        self.assertAlmostEqual(bb.ego_share(bb.STOP_AT, True), 1.0)
        self.assertAlmostEqual(bb.ego_share(1.0, True), 1.0)
        shares = [bb.ego_share(i / 50, True) for i in range(51)]
        self.assertEqual(shares, sorted(shares))
        self.assertEqual(bb.ego_speed_factor(0.95, True), 0.0)

    def test_envelope_shrinks_as_the_vehicle_slows(self):
        d = describe("SC-01")
        self.assertEqual(bb.envelope_at(d, 0.0), bb.ENVELOPE_M)
        self.assertLess(bb.envelope_at(d, 0.7), bb.envelope_at(d, 0.5))
        self.assertEqual(bb.envelope_at(d, 1.0), 1.0)

    def test_wrap_keeps_every_word(self):
        text = "No contact with the pedestrian; the vehicle yields as the traffic rules require"
        lines = bb.wrap(text, 13, 200)
        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), text)


class Verification(unittest.TestCase):
    def manifest(self, d: dict, frames: int = 72) -> dict:
        texts = [" ".join(t["lines"]) for t in bb.hud_texts(d) if "lines" in t]
        return {"render": {"frames": frames}, "objects": bb.expected(d, frames), "texts": texts}

    def test_a_faithful_scene_passes(self):
        for sid in scene.LAYOUTS:
            d = describe(sid)
            self.assertEqual(bb.verify(d, self.manifest(d)), [], sid)

    def test_a_moved_road_user_fails(self):
        d = describe("SC-06")
        m = self.manifest(d)
        name = next(n for n in m["objects"] if n.startswith("actor0"))
        m["objects"][name] = [m["objects"][name][0] + 1.0, m["objects"][name][1]]
        self.assertTrue(any(name in e for e in bb.verify(d, m)))

    def test_a_missing_stamp_fails(self):
        d = describe("SC-02")
        m = self.manifest(d)
        m["texts"] = [t for t in m["texts"] if "SIMULATION RESULT" not in t]
        self.assertTrue(any("label not on the frame" in e for e in bb.verify(d, m)))

    def test_descriptions_name_their_generator(self):
        for path in sorted(scene.OUT.glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(d["generator"], "tools/sim/scene.py")
            self.assertEqual(d["version"], scene.VERSION)


if __name__ == "__main__":
    unittest.main()
