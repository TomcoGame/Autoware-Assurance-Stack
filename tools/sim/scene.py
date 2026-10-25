#!/usr/bin/env python3
"""Scene descriptions for the qualitative Blender scenes of the known scenarios (WP-V-03).

For each scenario that has a layout in layouts.py, this writes tools/sim/scenes/<id>.json: one
concrete scenario drawn from the logical scenario of assurance/06-validation/scenarios/scenarios.yaml
(a value inside each stated range, chosen deterministically from the scenario id), the road layout,
the vehicle and the other road users, Autoware's planned path and the safety monitor's envelope,
where the hazard lies, the ODD conditions to draw, and every label the render shows.

No label is typed here. The scenario's name, description, parameters, events, triggering conditions
and pass criterion come from scenarios.yaml; the safety goals at stake are worked out by scenarios.py's
own `stake()`; goal statements and ASILs (WP-C-03), ODD attribute names (WP-C-02), monitor names and
element ratings (WP-C-04) come from tools/readme/facts.py; the short "meant to do" line is the one
WP-V-03 Figure 2-1 shows (scards.py). A lookup that fails stops the build.

The scene is a qualitative illustration for review, not a simulation: the motion is choreography
(layouts.py), the envelope's length is not computed (the vehicle's deceleration is a parameter until
DQ-008 chooses the vehicle), and every render carries STAMP. tools/sim/build_blend.py turns a
description into a Blender scene and renders it; renders are not committed (tools/sim/README.md).

    python3 tools/sim/scene.py            # write tools/sim/scenes/*.json
    python3 tools/sim/scene.py --check    # fail if any is stale, or a layout breaks a rule
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCENARIOS_DIR = REPO / "assurance" / "06-validation" / "scenarios"
sys.path.insert(0, str(REPO / "tools" / "readme"))
sys.path.insert(0, str(SCENARIOS_DIR))
sys.path.insert(0, str(HERE))
import facts as fx  # noqa: E402
import figkit as fk  # noqa: E402  (on the path through facts)
from layouts import LAYOUTS  # noqa: E402
from layouts import ROAD_KEYS  # noqa: E402
import scenarios as sc  # noqa: E402  (first: it puts the concept generators on the path)

import scards  # noqa: E402  isort: skip

OUT = HERE / "scenes"
STAMP = "qualitative illustration · not a simulation result · draft for engineering review"
SALT = "tools/sim sample 1"  # change it to draw a different concrete scenario for every layout
VERSION = 1

# The vehicle a participant class of ODD-16 is drawn as: a car of the pack (models/CREDITS.md), or a
# simple primitive where the pack has nothing. Classes without an entry cannot be drawn yet.
DRAWN_AS = {
    "car": "sedan",
    "van": "minivan",
    "emergency-vehicle": "suv",
    "bus": "box:bus",
    "bus-at-stop": "box:bus",
    "truck": "box:truck",
    "motorcycle": "box:motorcycle",
    "bicycle": "person:bicycle",
    "e-scooter": "person:e-scooter",
    "pedestrian": "person:adult",
    "child": "person:child",
    "wheelchair": "person:wheelchair",
    "animal": "box:animal",
}
LIGHT = {"day", "dusk", "night", "unlit", "low-sun"}


class SceneError(fk.FigureError):
    """A layout or a record does not give what a scene needs."""


def rng(sid: str) -> random.Random:
    seed = int(hashlib.sha256(f"{SALT}:{sid}".encode()).hexdigest()[:16], 16)
    return random.Random(seed)


def human(value: str) -> str:
    return value.replace("-", " ")


def sample(s: dict, m: dict, lay: dict, odd: dict) -> list[dict]:
    """One concrete value per parameter of the logical scenario, in its order.

    Two-sided numeric range: a seeded draw inside it, to 0.1. One-sided range: the stated bound, the
    hardest case. A range that crosses the ODD limit: no value; the scene shows inside and beyond.
    Categorical: the layout's pick, or a seeded draw among the scenario's values. Behaviour bound: no
    value, since the requirement has not fixed one."""
    r = rng(s["id"])
    out = []
    for p in s.get("parameters") or []:
        name, rng_text, src = sc.param_text(p, m)
        if "bound" in p:
            out.append(
                {
                    "parameter": p["name"],
                    "range": rng_text,
                    "value": None,
                    "label": f"{p['name']}: {rng_text}; the motion drawn is choreography",
                }
            )
            continue
        attr = p["odd"]
        if attr not in odd:
            raise SceneError(f"{s['id']}: WP-C-02 has no attribute {attr}")
        title = f"{attr} {odd[attr].attribute}"
        a = m["odd"][attr]
        if "values" in a:
            pick = (lay.get("pick") or {}).get(attr)
            if pick is not None and pick not in p["values"]:
                raise SceneError(
                    f"{s['id']}: layout picks {attr} {pick}, which is not one of its values "
                    f"({', '.join(p['values'])})"
                )
            v = pick if pick is not None else r.choice(p["values"])
            out.append(
                {
                    "parameter": attr,
                    "range": rng_text,
                    "value": v,
                    "chosen": "layout" if pick is not None else "seeded",
                    "outside": bool(a["values"][v].get("outside")),
                    "label": f"{title}: {v}",
                }
            )
            continue
        lo, hi, unit = p.get("min"), p.get("max"), a["unit"]
        r.random()  # one draw per parameter, so a change to one range leaves the others as they were
        if p.get("crosses"):
            v, label = None, f"{title}: swept from inside the ODD to beyond its limit"
        elif lo is not None and hi is not None:
            v = round(lo + (hi - lo) * r.random(), 1)
            label = f"{title}: {v:g} {unit} (range {rng_text})"
        else:
            v = lo if hi is None else hi
            label = f"{title}: {v:g} {unit} (the stated bound)"
        out.append(
            {
                "parameter": attr,
                "range": rng_text,
                "value": v,
                "unit": unit,
                "crosses": bool(p.get("crosses")),
                "label": label,
            }
        )
    return out


def value(smp: list[dict], attr: str):
    for x in smp:
        if x["parameter"] == attr:
            return x
    return None


def conditions(s: dict, m: dict, smp: list[dict], lay: dict) -> dict:
    """The ODD conditions the scene draws, from the sample; what each is drawn from, for the legend."""
    light = value(smp, "ODD-12")
    rain = value(smp, "ODD-10")
    vis = value(smp, "ODD-11")
    surf = value(smp, "ODD-13")
    out = {
        "light": light["value"] if light else "day",
        "surface": surf["value"] if surf else "dry",
        "rain": None,
        "visibility": None,
        "beyond": None,
    }
    if out["light"] not in LIGHT:
        raise SceneError(f"{s['id']}: no way to draw ODD-12 {out['light']}")
    crossing = [x for x in (rain, vis) if x and x.get("crosses")]
    if crossing and "odd_limit" not in lay:
        raise SceneError(f"{s['id']}: crosses the ODD limit, so its layout needs odd_limit")
    if rain:
        # A crossing sweep is drawn at the limit up to odd_limit, and denser beyond it, unlabelled.
        out["rain"] = m["odd"]["ODD-10"]["max"] if rain.get("crosses") else rain["value"]
        out["rain_limit"] = m["odd"]["ODD-10"]["max"]
    if vis:
        out["visibility"] = m["odd"]["ODD-11"]["min"] if vis.get("crosses") else vis["value"]
        out["visibility_floor"] = m["odd"]["ODD-11"]["min"]
    if crossing:
        out["beyond"] = {"y": lay["odd_limit"], "attributes": [x["parameter"] for x in crossing]}
    return out


def actor_kind(s: dict, a: dict, smp: list[dict]) -> str:
    kind = a["kind"]
    if isinstance(kind, dict):
        v = value(smp, kind["from"])
        if not v:
            raise SceneError(
                f"{s['id']}: an actor takes its class from {kind['from']}, not a parameter"
            )
        kind = v["value"]
    if kind not in DRAWN_AS:
        raise SceneError(f"{s['id']}: no way to draw a {kind}")
    return kind


def features(s: dict, lay: dict, smp: list[dict]) -> list[str]:
    out = []
    for attr, by_value in (lay.get("features") or {}).items():
        v = value(smp, attr)
        if not v:
            raise SceneError(f"{s['id']}: layout features depend on {attr}, not a parameter")
        out += by_value.get(v["value"], [])
    return sorted(set(out))


def check_layout(sid: str, lay: dict) -> list[str]:
    errs = [
        f"{sid}: road key {k} is not one of {', '.join(sorted(ROAD_KEYS))}"
        for k in lay["road"]
        if k not in ROAD_KEYS
    ]
    for key in ("road", "ego", "plan", "hazard", "still", "camera"):
        if key not in lay:
            errs.append(f"{sid}: layout lacks {key}")
    if not 0 <= lay.get("still", 0) <= 1:
        errs.append(f"{sid}: still is a fraction of the clip")
    for a in lay.get("actors", []):
        if a["role"] not in ("key", "other", "parked"):
            errs.append(f"{sid}: actor role {a['role']} is not key, other or parked")
        if len(a["path"]) > 1 and "move" not in a:
            errs.append(f"{sid}: a moving actor needs `move`")
    return errs


def points(pts) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in pts]


def scene(s: dict, m: dict, k: dict, f: fx.Facts) -> dict:
    sid = s["id"]
    lay = LAYOUTS[sid]
    errs = check_layout(sid, lay)
    if errs:
        raise SceneError("; ".join(errs))
    smp = sample(s, m, lay, f.odd)
    goals = []
    for g in sc.stake(s, k):
        if g not in f.goals:
            raise SceneError(f"{sid}: WP-C-03 has no safety goal {g}")
        statement, asil, _ = f.goals[g]
        goals.append({"id": g, "asil": asil, "statement": statement})
    events = [
        {"id": e, "description": k["events"][e]["description"]} for e in s.get("events") or []
    ]
    triggers = [
        {"id": t, "condition": k["triggers"][t]["condition"]} for t in s.get("triggers") or []
    ]
    monitors = [r for r in s["pass"]["refs"] if r in f.monitors]
    call = scards.SCENES.get(sid, {}).get("call")
    if not call:
        raise SceneError(f"{sid}: WP-V-03 Figure 2-1 (scards.py) has no 'meant to do' line")
    for eid in ("EL-01", "EL-02"):
        if eid not in f.elements:
            raise SceneError(f"WP-C-04: no element {eid}")
    aw, mon = f.elements["EL-01"], f.elements["EL-02"]
    speed = value(smp, "ODD-20")
    posted = value(smp, "ODD-03")
    actors = []
    for a in lay.get("actors", []):
        kind = actor_kind(s, a, smp)
        actors.append(
            {
                "role": a["role"],
                "class": kind,
                "drawn_as": DRAWN_AS[kind],
                "label": human(kind),
                "path": points(a["path"]),
                "move": list(a.get("move", (0.0, 0.0))),
            }
        )
    road = {k_: (list(v) if isinstance(v, tuple) else v) for k_, v in lay["road"].items()}
    if "speed_sign" in road:
        if not posted:
            raise SceneError(f"{sid}: a speed sign needs an ODD-03 parameter")
        road["speed_sign"] = {
            "at": road["speed_sign"],
            "value": posted["value"],
            "unit": posted["unit"],
        }
    cond = conditions(s, m, smp, lay)
    return {
        "version": VERSION,
        "generator": "tools/sim/scene.py",
        "stamp": STAMP,
        "scenario": {
            "id": sid,
            "name": s["name"],
            "description": s["description"],
            "situations": s.get("situations") or [],
            "events": events,
            "triggers": triggers,
            "goals": goals,
            "monitors": [{"id": x, "name": f.monitors[x]} for x in monitors],
            "meant": call[1],
            "pass": s["pass"]["criterion"],
            "pass_refs": s["pass"]["refs"],
            "source": "assurance/06-validation/scenarios/scenarios.yaml (WP-V-03)",
        },
        "sample": {"salt": SALT, "parameters": smp},
        "conditions": cond,
        "legend": {
            "plan": f"Autoware's planned path ({aw.eid} {aw.name}, rated {aw.asil})",
            "envelope": (
                f"{mon.name}'s envelope ({mon.eid}, ASIL {mon.asil}); length not computed, "
                "the vehicle is not chosen"
            ),
            "meant": f"Meant to do: {call[1]}",
            "hazard": "Where the hazard lies: "
            + ("; ".join(f"{e['id']} {e['description']}" for e in events) or s["name"]),
            "key": "The road user or condition the scenario is about",
        },
        "road": road,
        "features": features(s, lay, smp),
        "ego": {
            "path": points(lay["ego"]["path"]),
            "stops": bool(lay["ego"].get("stops")),
            "speed_kmh": speed["value"] if speed else None,
        },
        "plan": points(lay["plan"]),
        "occlusion": points(lay.get("occlusion", [])),
        "hazard": list(lay["hazard"]),
        "actors": actors,
        "still": lay["still"],
        "camera": {k_: (list(v) if isinstance(v, tuple) else v) for k_, v in lay["camera"].items()},
        "credits": "Vehicle models: Kiri '10 by Daniel Zhabotinsky; Generic passenger car pack by "
        "Comrade1280; both CC BY 4.0, changed (tools/readme/models/CREDITS.md)",
    }


def build() -> dict[Path, str]:
    m, k, f = sc.load(), sc.known(), fx.load()
    errs = sc.check(m, k)
    if errs:
        raise SceneError("scenarios.yaml: " + "; ".join(errs))
    by_id = {s["id"]: s for s in m["scenarios"]}
    missing = sorted(set(LAYOUTS) - set(by_id))
    if missing:
        raise SceneError(f"layouts.py: no scenario {', '.join(missing)} in scenarios.yaml")
    out = {}
    for sid in sorted(LAYOUTS):
        text = json.dumps(scene(by_id[sid], m, k, f), indent=1, ensure_ascii=False) + "\n"
        out[OUT / f"{sid}.json"] = text
    orphans = sorted(p.name for p in OUT.glob("*.json") if p not in out)
    if orphans:
        raise SceneError(f"scenes/: {', '.join(orphans)} has no layout; delete it")
    return out


if __name__ == "__main__":
    fk.run(build, __doc__)
