#!/usr/bin/env python3
"""Unit tests of the scenario scene tools: the scene descriptions and the plain-Python half of
build_blend.py (motion, frame texts, verification). Blender is not needed.

python3 -m unittest discover -s tools/sim -p 'test_*.py' -v
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_blend as bb  # noqa: E402
import scene  # noqa: E402

M, K, F = scene.sc.load(), scene.sc.known(), scene.fx.load()
BY_ID = {s["id"]: s for s in M["scenarios"]}
ALL = {  # every scene, condition variants included, by its name
    p.stem: json.loads(text) for p, text in scene.build().items() if p.suffix == ".json"
}


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
        for sid, d in ALL.items():
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

    def test_a_picked_speed_lies_inside_the_range_and_says_so(self):
        d = ALL["SC-17"]
        speed = next(p for p in d["sample"]["parameters"] if p["parameter"] == "ODD-20")
        self.assertEqual(speed["chosen"], "layout")
        self.assertIn("picked, not seeded", speed["label"])
        for bad in (60.0, -1.0):  # outside 0 to 48 km/h
            lay = copy.deepcopy(scene.LAYOUTS["SC-17"])
            lay["pick"]["ODD-20"] = bad
            with self.assertRaises(scene.SceneError):
                describe("SC-17", lay)
        lay = copy.deepcopy(scene.LAYOUTS["SC-14"])  # ODD-10 crosses the limit: no pick
        lay["pick"]["ODD-10"] = 1.0
        with self.assertRaises(scene.SceneError):
            describe("SC-14", lay)

    def test_an_unknown_road_key_is_refused(self):
        lay = copy.deepcopy(scene.LAYOUTS["SC-01"])
        lay["road"]["tunnel"] = True
        with self.assertRaises(scene.SceneError):
            describe("SC-01", lay)

    def test_scenarios_on_the_remote_link_or_a_cybersecurity_requirement_are_not_drawn(self):
        # Derived from the records, so a new scenario of that kind is caught without a list here.
        refused = {s["id"] for s in M["scenarios"] if scene.restricted(s)}
        self.assertTrue({"SC-20", "SC-21", "SC-26"} <= refused)
        self.assertFalse(refused & set(scene.LAYOUTS))
        saved = scene.LAYOUTS.get("SC-20")
        scene.LAYOUTS["SC-20"] = copy.deepcopy(scene.LAYOUTS["SC-01"])
        try:
            with self.assertRaises(scene.SceneError):
                scene.scene(BY_ID["SC-20"], M, K, F)
        finally:
            del scene.LAYOUTS["SC-20"]
        self.assertIsNone(saved)

    def test_each_parameter_has_its_own_draw(self):
        # Picking a value for one parameter leaves the draws of the others as they were (F2).
        lay = copy.deepcopy(scene.LAYOUTS["SC-01"])
        del lay["pick"]["ODD-12"]
        a = {p["parameter"]: p["value"] for p in describe("SC-01")["sample"]["parameters"]}
        b = {p["parameter"]: p["value"] for p in describe("SC-01", lay)["sample"]["parameters"]}
        self.assertEqual(
            {k: v for k, v in a.items() if k != "ODD-12"},
            {k: v for k, v in b.items() if k != "ODD-12"},
        )

    def test_ego_speed_never_above_the_posted_limit(self):
        smp = [
            {"parameter": "ODD-20", "value": 48.0, "unit": "km/h", "label": "ODD-20 Ego speed: 48"},
            {"parameter": "ODD-03", "value": 25, "unit": "mph", "label": "ODD-03 Posted limit: 25"},
        ]
        scene.cap(BY_ID["SC-01"], M, smp)
        self.assertLessEqual(smp[0]["value"], 25 * scene.sc.MPH)
        self.assertIn("capped", smp[0]["label"])

    def test_the_envelope_legend_names_the_open_vehicle_decision(self):
        self.assertNotIn(scene.VEHICLE, F.decisions)
        self.assertIn(scene.VEHICLE, describe("SC-01")["legend"]["envelope"])

    def test_legend_lines_only_for_what_is_drawn(self):
        self.assertNotIn("key", describe("SC-14")["legend"])  # SC-14 has no key road user
        self.assertIn("odd_limit", describe("SC-14")["legend"])
        self.assertIn("occlusion", describe("SC-02")["legend"])
        self.assertNotIn("occlusion", describe("SC-01")["legend"])

    def test_the_ego_stops_before_its_stop_line(self):
        front = bb_front()
        for sid, d in ALL.items():
            if (
                "stop_line" in d["road"]
                and "no_stop_line" not in d["features"]
                and d["ego"]["stops"]
            ):
                end = d["ego"]["path"][-1][1]
                self.assertLess(end + front, d["road"]["stop_line"] - 0.25, sid)


def bb_front() -> float:
    sys.path.insert(0, str(HERE.parent / "readme"))
    import mesh  # noqa: PLC0415

    return mesh.load_kiri().bounds()[1][1]


class Motion(unittest.TestCase):
    def test_point_at(self):
        pts = [[0, 0], [0, 10], [10, 10]]
        self.assertEqual(bb.point_at(pts, 5)[:2], (0.0, 5.0))
        x, y, hd = bb.point_at(pts, 15)
        self.assertAlmostEqual(x, 5.0)
        self.assertAlmostEqual(y, 10.0)
        self.assertAlmostEqual(hd, -1.5707963, places=5)  # heading right of +y

    def test_ego_stops_at_the_end_of_its_path(self):
        for sid, d in ALL.items():
            dist = [bb.ego_distance(d, i / 100) for i in range(101)]
            self.assertEqual(dist, sorted(dist), sid)
            self.assertAlmostEqual(dist[-1], bb.length(d["ego"]["path"]), places=6, msg=sid)
            if d["ego"]["stops"]:
                self.assertEqual(bb.ego_speed_factor(d, 1.0), 0.0, sid)

    def test_the_ego_slows_at_the_level_the_records_state(self):
        # FSR-03.02's firm level, read from fsc.yaml; the stop is consistent with it.
        fsr = next(x for x in scene.sc.misuse.ai.fsc.load()["fsrs"] if x["id"] == "FSR-03.02")
        for sid, d in ALL.items():
            self.assertIn(f"{d['ego']['decel']:g} m/s²", fsr["text"])
            if bb.standing(d) or not d["ego"]["stops"]:
                continue
            cruise, brake, _ = bb.ego_profile(d)
            v = d["ego"]["speed_kmh"] / 3.6
            self.assertAlmostEqual(v / brake, d["ego"]["decel"], places=6)
            # at least CRUISE_M: a path whose turns are longer than the stop keeps its start
            self.assertGreaterEqual(cruise * v, scene.CRUISE_M - 0.05, sid)

    def test_envelope_shrinks_as_the_vehicle_slows(self):
        d = describe("SC-01")
        self.assertEqual(bb.envelope_at(d, 0.0), bb.ENVELOPE_M)
        self.assertLess(bb.envelope_at(d, 0.7), bb.envelope_at(d, 0.5))
        self.assertEqual(bb.envelope_at(d, 1.0), 1.0)

    def test_the_clip_runs_at_the_sampled_speed(self):
        # F1: while it cruises, the ego covers its path at the ODD-20 value of the sample.
        for sid, d in ALL.items():
            if bb.standing(d):
                self.assertEqual(bb.ego_distance(d, 0.5), 0.0)
                continue
            t = bb.clip_seconds(d)
            u0, u1 = 0.0, bb.ego_profile(d)[0] / t * 0.9
            v = (bb.ego_distance(d, u1) - bb.ego_distance(d, u0)) / ((u1 - u0) * t) * 3.6
            self.assertAlmostEqual(v, d["ego"]["speed_kmh"], places=6, msg=sid)

    def test_moments_are_ordered_and_include_the_still(self):
        for sid, d in ALL.items():
            m = bb.moments(d)
            self.assertEqual([u for u, _ in m], sorted(u for u, _ in m))
            self.assertTrue(any("main view" in x for _, x in m), sid)
            if d["ego"]["stops"] and not bb.standing(d):  # the stop is never merged away
                self.assertTrue(any("vehicle stands still" in x for _, x in m), sid)
            self.assertLessEqual(len(m), 5)

    def test_tags_do_not_overlap(self):
        tags = [
            {"label": "Car (qualitative)", "colour": "#fff", "x": 500, "y": 300 + i}
            for i in range(4)
        ]
        boxes = [t["box"] for t in bb.place_tags(tags)]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1 :]:
                self.assertTrue(
                    abs(a[1] - b[1]) >= 25 or a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0]
                )

    def test_the_dashboard_stays_on_its_canvas(self):
        for sid, d in ALL.items():
            for e in bb.dashboard_layout(d, []):
                if "rect" in e or "image" in e:
                    x, y, w, h = e.get("rect") or e["box"]
                    self.assertTrue(
                        0 <= x and 0 <= y and x + w <= bb.DW and y + h <= bb.DH, (sid, e)
                    )
                else:
                    bottom = e["y"] + len(e["text"]) * e["size"] * 1.3
                    right = e["x"] + max(len(t) for t in e["text"]) * e["size"] * 0.52
                    self.assertLessEqual(bottom, bb.DH, (sid, e["text"][:1]))
                    self.assertLessEqual(right, bb.DW, (sid, e["text"][:1]))

    def test_footer_lines_do_not_overlap(self):
        for sid, d in ALL.items():
            texts = [e for e in bb.dashboard_layout(d, []) if "text" in e and e["y"] >= 970]
            rows = sorted({(e["y"], e["size"]) for e in texts})
            for (y0, s0), (y1, _) in zip(rows, rows[1:]):
                self.assertLessEqual(y0 + s0 * 1.2, y1, (sid, y0, y1))

    def test_goal_chips_fit_or_say_how_many_are_left(self):
        goals = [{"id": f"SG-0{i}", "asil": "D"} for i in range(1, 5)]
        chips = bb.goal_chips(goals, 400)
        self.assertTrue(chips[-1].startswith("+"))
        self.assertEqual(len(chips) - 1 + int(chips[-1][1]), 4)
        self.assertLessEqual(sum(bb.chip_width(c) + 6 for c in chips), 400)
        self.assertEqual(len(bb.goal_chips(goals, 2000)), 4)

    def test_the_dashboard_credits_the_look_it_was_drawn_with(self):
        cc0 = {
            "assets": [{"slot": "asphalt", "id": "asphalt_02", "source": "polyhaven"}],
            "pedestrians": "Quaternius (CC0)",
        }
        self.assertIn("Poly Haven", bb.look_credit(cc0))
        self.assertIn("Quaternius", bb.look_credit(cc0))
        self.assertIn("procedural", bb.look_credit({}))
        texts = bb.dashboard_texts(bb.dashboard_layout(describe("SC-01"), [], cc0))
        self.assertTrue(any("Poly Haven" in t for t in texts))

    def test_the_sim_workflows_parse(self):
        # A workflow GitHub cannot parse fails at once and silently drops its checks from the pull request.
        import yaml  # noqa: PLC0415

        for name in ("sim.yaml", "sim-render.yaml"):
            wf = yaml.safe_load(
                (HERE.parents[1] / ".github" / "workflows" / name).read_text("utf-8")
            )
            self.assertTrue(wf.get("jobs"), name)
            for job in wf["jobs"].values():
                for step in job["steps"]:
                    self.assertIsInstance(step.get("run", ""), str, name)

    def test_the_asset_lock_names_only_cc0_sources(self):
        lock = json.loads((HERE / "assets.lock.json").read_text(encoding="utf-8"))
        self.assertIn("CC0", lock["licence"])
        for name, slot in lock["slots"].items():
            self.assertIn(slot["source"], ("polyhaven", "ambientcg"), name)
            for rel, f in slot["files"].items():
                self.assertRegex(f["sha256"], r"^[0-9a-f]{64}$", f"{name}/{rel}")
                self.assertTrue(f["url"].startswith("https://"), f"{name}/{rel}")

    def test_the_pedestrian_models_are_the_recorded_files(self):
        readme = (HERE / "models" / "people" / "README.md").read_text(encoding="utf-8")
        for f in ("pedestrian_male.glb", "pedestrian_female.glb"):
            digest = hashlib.sha256((HERE / "models" / "people" / f).read_bytes()).hexdigest()
            self.assertIn(digest, readme, f)

    def test_wrap_keeps_every_word(self):
        text = "No contact with the pedestrian; the vehicle yields as the traffic rules require"
        lines = bb.wrap(text, 13, 200)
        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), text)


# Footprints (width, length) in metres of what the scenes draw, for the overlap test: the models'
# bounds (tools/readme/mesh.py) rounded up, and the primitives of build_blend.py.
FOOT = {
    "ego": (1.71, 4.36),
    "sedan": (2.19, 4.91),
    "minivan": (2.11, 5.19),
    "suv": (2.33, 5.19),
    "queue": (2.2, 5.19),
    "box:bus": (2.55, 12.0),
    "box:truck": (2.5, 8.0),
    "box:motorcycle": (0.7, 2.1),
    "box:animal": (0.3, 0.9),
    "person:adult": (0.6, 0.6),
    "person:child": (0.5, 0.5),
    "person:wheelchair": (0.7, 1.0),
    "person:bicycle": (0.6, 1.8),
    "person:e-scooter": (0.6, 1.0),
}


def corners(x: float, y: float, hd: float, foot: tuple[float, float]) -> list[tuple[float, float]]:
    w, ln = foot[0] / 2, foot[1] / 2
    c, s = math.cos(hd), math.sin(hd)
    return [
        (x + dx * c - dy * s, y + dx * s + dy * c)
        for dx, dy in ((-w, -ln), (w, -ln), (w, ln), (-w, ln))
    ]


def overlap(a: list, b: list, margin: float = 0.2) -> bool:
    """Separating-axis test of two rectangles, each grown by margin / 2."""
    for poly in (a, b):
        for i in range(4):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % 4]
            nx, ny = y1 - y0, x0 - x1
            n = math.hypot(nx, ny)
            pa = [(px * nx + py * ny) / n for px, py in a]
            pb = [(px * nx + py * ny) / n for px, py in b]
            if max(pa) + margin < min(pb) or max(pb) + margin < min(pa):
                return False
    return True


class Choreography(unittest.TestCase):
    def test_no_two_road_users_overlap(self):
        # The choreography never draws a collision: the ego, every road user and every queued
        # vehicle stay apart at every moment of the clip.
        for sid, d in ALL.items():
            static = [
                corners(q[0], q[1], math.radians(q[2]), FOOT["queue"]) for q in d.get("queue", [])
            ]
            n_queue = len(static)
            for p in d["props"]:  # what stands on the road is in the way too
                if p["kind"] in ("cones", "barrier"):
                    (xa, ya), (xb, yb) = p["from"], p["to"]
                    hd = math.atan2(-(xb - xa), yb - ya)
                    foot = (0.5, math.dist(p["from"], p["to"]) + 0.5)
                    static.append(corners((xa + xb) / 2, (ya + yb) / 2, hd, foot))
                elif p["kind"] == "debris":  # steam is not solid: the ego drives through it
                    static.append(corners(*p["at"], 0.0, (2 * p["r"], 2 * p["r"])))
                elif p["kind"] in ("work_sign", "bus_stop"):  # a paddle is held
                    static.append(corners(*p["at"], 0.0, (0.3, 0.3)))
            doors = [p for p in d["props"] if p["kind"] == "door"]
            for i in range(201):
                u = i / 200
                boxes = [("ego", corners(*bb.ego_at(d, u), FOOT["ego"]))]
                for p in doors:  # the open door's swept box, beside the ego
                    if u >= p["open"]:
                        x, y, hd = bb.ego_at(d, u)
                        sgn = -1 if p["side"] == "left" else 1
                        lx, ly = sgn * (FOOT["ego"][0] / 2 + 0.5), 0.25
                        c, s_ = math.cos(hd), math.sin(hd)
                        boxes.append(
                            (
                                "door",
                                corners(x + lx * c - ly * s_, y + lx * s_ + ly * c, hd, (1.0, 1.0)),
                            )
                        )
                for k, a in enumerate(d["actors"]):
                    boxes.append((f"actor{k}", corners(*bb.actor_at(a, u), FOOT[a["drawn_as"]])))
                boxes += [
                    (f"queue{k}" if k < n_queue else f"prop{k - n_queue}", q)
                    for k, q in enumerate(static)
                ]
                for j, (na, ba) in enumerate(boxes):
                    for nb, bx in boxes[j + 1 :]:
                        if {na, nb} == {"ego", "door"} or (
                            na.startswith("queue") and nb.startswith("queue")
                        ):
                            continue
                        self.assertFalse(overlap(ba, bx), f"{sid}: {na} meets {nb} at {u:.3f}")

    def test_every_drawable_scenario_has_a_scene(self):
        drawable = {s["id"] for s in M["scenarios"] if not scene.restricted(s)}
        self.assertEqual(set(scene.LAYOUTS), drawable)

    def test_a_variant_changes_only_what_it_picks(self):
        for key, d in ALL.items():
            if not d["variant"]:
                continue
            base = ALL[d["variant"]["of"]]
            self.assertTrue(key.startswith(base["key"] + "--"))
            changed = {
                a["parameter"]
                for a, b in zip(d["sample"]["parameters"], base["sample"]["parameters"])
                if a != b
            }
            picked = {part.split(" ")[0] for part in d["variant"]["label"].split(", ")}
            self.assertTrue(changed, key)
            self.assertLessEqual(changed, picked, key)
            self.assertEqual(d["actors"], base["actors"], key)
            self.assertEqual(d["ego"], base["ego"], key)

    def test_a_variant_pick_outside_the_scenario_is_refused(self):
        saved = scene.LAYOUTS["SC-13"]
        for bad in ({"ODD-12": "dusk"}, {"ODD-03": "30"}):  # not one of its values; not a parameter
            scene.LAYOUTS["SC-13"] = copy.deepcopy(saved) | {"variants": [bad]}
            try:
                with self.assertRaises(scene.SceneError, msg=bad):
                    scene.build()
            finally:
                scene.LAYOUTS["SC-13"] = saved

    def test_a_door_never_opens_before_the_vehicle_stands(self):
        lay = copy.deepcopy(scene.LAYOUTS["SC-15"])
        lay["props"] = [p | {"open": 0.2} if p["kind"] == "door" else p for p in lay["props"]]
        with self.assertRaises(scene.SceneError):
            describe("SC-15", lay)
        for key, d in ALL.items():
            for p in d["props"]:
                if p["kind"] == "door":
                    self.assertGreaterEqual(p["open"], bb.stands_at(d), key)

    def test_a_vehicle_that_holds_draws_no_plan(self):
        d = ALL["SC-16"]
        self.assertEqual(d["plan"], [])
        self.assertNotIn("plan", d["legend"])
        self.assertTrue(bb.standing(d))
        self.assertIn("plan", ALL["SC-01"]["legend"])

    def test_lights_come_on_as_the_vehicle_slows(self):
        d = ALL["SC-17"]
        self.assertEqual(d["ego"]["lights"], "hazard")
        on, off = bb.lights_window(d)
        self.assertAlmostEqual(on, bb.ego_profile(d)[0] / bb.clip_seconds(d))
        self.assertEqual(off, 1.0)

    def test_the_indicator_matches_the_steering(self):
        # SC-22's pass criterion: the indicator matches the commanded and achieved steering
        # direction, so it is off once the lane change is over and the ego drives straight.
        d = ALL["SC-22"]
        on, off = bb.lights_window(d)
        self.assertEqual(on, 0.0)
        self.assertLess(off, 1.0)
        x_after = bb.ego_at(d, off + 0.02)[0]
        self.assertAlmostEqual(x_after, bb.ego_at(d, 1.0)[0], places=2)  # straight from there on
        self.assertLess(bb.ego_at(d, off - 0.05)[0], bb.ego_at(d, 0.0)[0])  # it was steering left


class Verification(unittest.TestCase):
    def manifest(self, d: dict, frames: int = 72) -> dict:
        clip = [" ".join(t["lines"]) for t in bb.hud_texts(d) if "lines" in t]
        return {
            "render": {"frames": frames},
            "objects": bb.expected(d, frames),
            "drawn": {**bb.described(d), "overlay_top_m": 0.05},
            "texts": bb.dashboard_texts(bb.dashboard_layout(d, [])),
            "clip_texts": clip,
        }

    def test_a_faithful_scene_passes(self):
        for sid, d in ALL.items():
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
        self.assertTrue(any("label not on the dashboard" in e for e in bb.verify(d, m)))

    def test_a_missing_credit_on_the_clip_fails(self):
        d = describe("SC-01")
        m = self.manifest(d)
        m["clip_texts"] = [t for t in m["clip_texts"] if "CC BY" not in t]
        self.assertTrue(any("label not on the clip" in e for e in bb.verify(d, m)))

    def test_an_overlay_standing_up_fails(self):
        # As in LionDriver, nothing drawn for the analysis may stand in front of the road-level cameras.
        d = describe("SC-14")
        m = self.manifest(d)
        m["drawn"] = {**m["drawn"], "overlay_top_m": 0.9}  # the old envelope wall
        self.assertTrue(any("overlay stands" in e for e in bb.verify(d, m)))

    def test_a_condition_not_drawn_fails(self):
        d = describe("SC-14")
        m = self.manifest(d)
        m["drawn"] = {**m["drawn"], "fog": False}
        self.assertTrue(any(e.startswith("drawn: fog") for e in bb.verify(d, m)))

    def test_descriptions_name_their_generator(self):
        for path in sorted(scene.OUT.glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(d["generator"], "tools/sim/scene.py")
            self.assertEqual(d["version"], scene.VERSION)


if __name__ == "__main__":
    unittest.main()
