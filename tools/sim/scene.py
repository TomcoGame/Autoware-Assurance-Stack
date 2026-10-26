#!/usr/bin/env python3
"""Scene descriptions for the qualitative Blender scenes of the known scenarios (WP-V-03).

For each scenario that has a layout in layouts.py, this writes tools/sim/scenes/<id>.json (and
<id>--<values>.json for each condition variant of the layout): one
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
import math
from pathlib import Path
import random
import re
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
GALLERY = HERE / "dashboards"
STAMP = "qualitative illustration · not a simulation result · draft for engineering review"
SALT = "tools/sim sample 1"  # change it to draw a different concrete scenario for every layout
VERSION = 1
SLOWING = "FSR-03.02"  # the requirement whose firm level the ego is drawn slowing at
CRUISE_M = 8.0  # metres the ego is drawn cruising before it slows: choreography
VEHICLE = "DQ-008"  # the decision that chooses the vehicle, and with it the envelope's length

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
    "directing": "person:adult",
}
PROPS = {"cones", "barrier", "work_sign", "steam", "debris", "bay", "bus_stop", "paddle", "door"}
LIGHTS = {"hazard", "left", "right"}
LIGHT = {"day", "dusk", "night", "unlit", "low-sun"}


class SceneError(fk.FigureError):
    """A layout or a record does not give what a scene needs."""


def rng(sid: str, key: str) -> random.Random:
    """The generator of one parameter of one scenario: a change to one parameter, or a pick, leaves
    the draws of the others as they were."""
    seed = int(hashlib.sha256(f"{SALT}:{sid}:{key}".encode()).hexdigest()[:16], 16)
    return random.Random(seed)


def human(value: str) -> str:
    return value.replace("-", " ")


def sample(s: dict, m: dict, lay: dict, odd: dict) -> list[dict]:
    """One concrete value per parameter of the logical scenario, in its order.

    Two-sided numeric range: a seeded draw inside it, to 0.1, or the layout's pick inside it (its
    label says so). One-sided range: the stated bound, the
    hardest case. A range that crosses the ODD limit: no value; the scene shows inside and beyond.
    Categorical: the layout's pick, or a seeded draw among the scenario's values. Behaviour bound: no
    value, since the requirement has not fixed one."""
    out = []
    for p in s.get("parameters") or []:
        r = rng(s["id"], p.get("odd") or p.get("name", ""))
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
        pick = (lay.get("pick") or {}).get(attr)
        if pick is not None and (p.get("crosses") or lo is None or hi is None):
            raise SceneError(f"{s['id']}: layout picks {attr}, which has no two-sided range")
        if p.get("crosses"):
            v, label = None, f"{title}: swept from inside the ODD to beyond its limit"
        elif pick is not None:
            if not lo <= pick <= hi:
                raise SceneError(f"{s['id']}: layout picks {attr} {pick}, outside {rng_text}")
            v = float(pick)
            label = f"{title}: {v:g} {unit} (range {rng_text}; picked, not seeded)"
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
            | ({"chosen": "layout"} if pick is not None else {})
        )
    cap(s, m, out)
    return out


def cap(s: dict, m: dict, smp: list[dict]) -> None:
    """Keep the sampled ego speed at or below the sampled posted limit (ODD-20 `capped_by`)."""
    speed = value(smp, "ODD-20")
    by = m["odd"]["ODD-20"].get("capped_by")
    limit = value(smp, by) if by else None
    if not speed or not limit or speed["value"] is None or limit["value"] is None:
        return
    top = limit["value"] * sc.MPH if (limit["unit"], speed["unit"]) == ("mph", "km/h") else None
    if top is None:
        raise SceneError(f"{s['id']}: no conversion from {limit['unit']} to {speed['unit']}")
    if speed["value"] > top:
        speed["value"] = math.floor(top * 10) / 10
        speed["label"] = (
            f"ODD-20 {speed['label'].split(':')[0].split(' ', 1)[1]}: {speed['value']:g} km/h "
            f"(capped at the sampled {by} limit)"
        )


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


def slowing(k: dict) -> tuple[float, str]:
    """The level the ego is drawn slowing at, and where it comes from: the firm, non-emergency level
    of FSR-03.02, the most a stop that the safety channel does not have to confirm may brake."""
    fsr = next((x for x in sc.misuse.ai.fsc.load()["fsrs"] if x["id"] == SLOWING), None)
    hit = re.search(r"firm, non-emergency level of ([\d.]+) m/s²", fsr["text"]) if fsr else None
    if not hit:
        raise SceneError(f"fsc.yaml: {SLOWING} no longer states its firm level in m/s²")
    dq = re.findall(r"DQ-\d{3}", fsr["text"])
    level = float(hit.group(1))
    return level, (
        f"Ego slows at {level:g} m/s², the firm level of {SLOWING} ({', '.join(dq)}); "
        "choreography, not Autoware's planned braking"
    )


def ego_path(sid: str, lay: dict, speed: dict | None, decel: float) -> list[list[float]]:
    """The ego's path: it ends where the layout stops it, and starts far enough back to cruise
    CRUISE_M at the sampled speed and then slow at `decel` to that stop."""
    pts = points(lay["ego"]["path"])
    if not lay["ego"].get("stops") or not speed or len(pts) < 2:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[1]
    seg = math.dist(pts[0], pts[1])
    rest = sum(math.dist(pts[i], pts[i + 1]) for i in range(1, len(pts) - 1))
    v = speed["value"] / 3.6
    need = CRUISE_M + v * v / (2 * decel) - rest
    if need < 1.0:
        # The turns of the path are already longer than the stop needs: keep its start, so that it
        # still meets the road where the layout draws it.
        return pts
    ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
    return [[round(x1 - ux * need, 2), round(y1 - uy * need, 2)]] + pts[1:]


def condition_label(smp: list[dict]) -> str:
    """The light, surface and weather of the sample, in a few words for the dashboard header."""
    out = []
    for attr in ("ODD-12", "ODD-13", "ODD-10", "ODD-11"):
        v = value(smp, attr)
        if not v:
            continue
        if v.get("crosses"):
            out.append(f"{attr} across the limit")
        elif "unit" in v:
            out.append(f"{attr} {v['value']:g} {v['unit']}")
        else:
            out.append(f"{attr} {v['value']}")
    return " · ".join(out) or "not set by the scenario"


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


def restricted(s: dict) -> str:
    """Why a scenario must not be drawn, or "": one that rests on the remote operations link or a
    cybersecurity requirement would show security architecture (CLAUDE.md, WP-M-09 §4)."""
    link = [
        v
        for p in s.get("parameters") or []
        if p.get("odd") == "ODD-15"
        for v in p.get("values") or []
        if v.startswith("link")
    ]
    if link:
        return f"it varies the remote operations link (ODD-15 {', '.join(link)})"
    cs = [r for r in s["pass"]["refs"] if r.startswith("CSR-")]
    if cs:
        return f"its pass criterion rests on {', '.join(cs)}"
    return ""


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
        if a.get("lying") and len(a["path"]) > 1:
            errs.append(f"{sid}: a road user lying in the lane does not move")
    errs += [
        f"{sid}: prop {p['kind']} is not one of {', '.join(sorted(PROPS))}"
        for p in lay.get("props", [])
        if p["kind"] not in PROPS
    ]
    lights = lay["ego"].get("lights")
    if lights is not None and lights not in LIGHTS:
        errs.append(f"{sid}: ego lights {lights} are not one of {', '.join(sorted(LIGHTS))}")
    if lay.get("signal") not in (None, "red", "green"):
        errs.append(f"{sid}: the ego's signal is red or green")
    return errs


def points(pts) -> list[list[float]]:
    return [[float(x), float(y)] for x, y in pts]


def variant_key(sid: str, pick: dict | None) -> str:
    """The name of a scene: the scenario id, and for a condition variant the values it picks."""
    return sid if not pick else f"{sid}--" + "-".join(pick[a] for a in sorted(pick))


def scene(s: dict, m: dict, k: dict, f: fx.Facts, variant: dict | None = None) -> dict:
    sid = s["id"]
    lay = LAYOUTS[sid]
    why = restricted(s)
    if why:
        raise SceneError(f"{sid}: not drawn, because {why}; remove its layout")
    errs = check_layout(sid, lay)
    pickable = {
        p["odd"]
        for p in s.get("parameters") or []
        if "values" in p or ("min" in p and "max" in p and not p.get("crosses"))
    }
    for attr in {**(lay.get("pick") or {}), **(variant or {})}:
        if attr not in pickable:
            errs.append(
                f"{sid}: picks {attr}, which is not one of its parameters with values or a range"
            )
    if errs:
        raise SceneError("; ".join(errs))
    if variant:
        lay = {**lay, "pick": {**(lay.get("pick") or {}), **variant}}
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
    if VEHICLE in f.decisions:
        raise SceneError(
            f"{VEHICLE} is applied: the vehicle is chosen, so the envelope legend and ENVELOPE_M "
            "of build_blend.py need revisiting"
        )
    for eid in ("EL-01", "EL-02"):
        if eid not in f.elements:
            raise SceneError(f"WP-C-04: no element {eid}")
    aw, mon = f.elements["EL-01"], f.elements["EL-02"]
    speed = value(smp, "ODD-20")
    posted = value(smp, "ODD-03")
    decel, motion_label = slowing(k)
    actors = []
    for a in lay.get("actors", []):
        kind = actor_kind(s, a, smp)
        actors.append(
            {
                "role": a["role"],
                "class": kind,
                "drawn_as": DRAWN_AS[kind],
                "label": human(kind) + (" lying in the lane" if a.get("lying") else ""),
                "path": points(a["path"]),
                "move": list(a.get("move", (0.0, 0.0))),
            }
            | ({"lying": True} if a.get("lying") else {})
            | ({"face": float(a["face"])} if "face" in a else {})
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
    path = ego_path(sid, lay, speed, decel)
    standing = len(path) == 1
    if standing != (speed is None):
        raise SceneError(
            f"{sid}: the ego stands (one point) exactly when the scenario samples no ODD-20 speed"
        )
    if speed is not None and speed["value"] == 0 and not standing:
        raise SceneError(
            f"{sid}: the draw gives an ego speed of 0 on a path; change SALT or the layout"
        )
    if standing:
        motion_label = "Ego stands still throughout; choreography"
    hold = float(lay["ego"].get("hold_s", 0.0))
    legend_extra = {}
    if any(a["role"] == "key" for a in actors):
        legend_extra["key"] = "Amber, ringed: the road user the scenario is about"
    if lay.get("occlusion"):
        legend_extra["occlusion"] = "Grey area: what the parked vehicle hides from the ego"
    if cond.get("beyond"):
        legend_extra["odd_limit"] = (
            "Violet band across the road: where the drawing passes the ODD limit of "
            + ", ".join(cond["beyond"]["attributes"])
            + "; beyond it drawn denser, no value stated"
        )
    feats = features(s, lay, smp)
    if "queue" in feats and not lay.get("queue"):
        raise SceneError(f"{sid}: the queue feature needs the queue's positions")
    desc = {
        "version": VERSION,
        "generator": "tools/sim/scene.py",
        "key": variant_key(sid, variant),
        "variant": (
            {"of": sid, "label": ", ".join(f"{a} {variant[a]}" for a in sorted(variant))}
            if variant
            else None
        ),
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
            "misuse": s.get("misuse") or [],
            "losses": s.get("losses") or [],
            "methods": [sc.METHODS[x] for x in s["methods"]],
            "meant": call[1],
            "pass": s["pass"]["criterion"],
            "pass_refs": s["pass"]["refs"],
            "source": "assurance/06-validation/scenarios/scenarios.yaml (WP-V-03)",
        },
        "sample": {"salt": SALT, "parameters": smp},
        "condition_label": condition_label(smp),
        "conditions": cond,
        "legend": (
            {"plan": f"Autoware's planned path ({aw.eid} {aw.name}, rated {aw.asil})"}
            if lay["plan"]
            else {}
        )
        | {
            "envelope": (
                f"{mon.name}'s envelope ({mon.eid}, ASIL {mon.asil}); length not computed: "
                f"the vehicle is not chosen yet ({VEHICLE})"
            ),
            "meant": f"Meant to do: {call[1]}",
            "meant_mark": (
                "Green ring: where the pass criterion holds the vehicle"
                if standing
                else "Dashed green: the path the pass criterion asks of the vehicle"
                + ("; green ring: where it is judged" if lay["ego"].get("stops") else "")
            ),
            "hazard": "Where the hazard lies: "
            + ("; ".join(f"{e['id']} {e['description']}" for e in events) or s["name"]),
        }
        | legend_extra,
        "road": road,
        "features": feats,
        "ego": {
            "path": path,
            "stops": bool(lay["ego"].get("stops")),
            "speed_kmh": speed["value"] if speed else None,
            "decel": decel,
            "motion_label": motion_label,
        }
        | ({"hold_s": hold} if hold else {})
        | ({"lights": lay["ego"]["lights"]} if lay["ego"].get("lights") else {})
        | ({"lights_m": list(lay["ego"]["lights_m"])} if lay["ego"].get("lights_m") else {}),
        "plan": points(lay["plan"]),
        "occlusion": points(lay.get("occlusion", [])),
        "hazard": list(lay["hazard"]),
        "actors": actors,
        "props": [
            {k_: (list(v) if isinstance(v, tuple) else v) for k_, v in p.items()}
            for p in lay.get("props", [])
        ],
        "signal": lay.get("signal"),
        "queue": [list(q) for q in lay.get("queue", [])] if "queue" in feats else [],
        "still": lay["still"],
        "camera": {k_: (list(v) if isinstance(v, tuple) else v) for k_, v in lay["camera"].items()},
        "credits": "Vehicle models: Kiri '10 by Daniel Zhabotinsky; Generic passenger car pack by "
        "Comrade1280; both CC BY 4.0, changed (tools/readme/models/CREDITS.md)",
    }
    if "chase" in lay:  # only where a scene needs it, so the others' descriptions stay as they were
        desc["chase"] = {k_: list(v) for k_, v in lay["chase"].items()}
    import build_blend  # noqa: PLC0415  (plain Python above its Blender part)

    stands = build_blend.stands_at(desc)
    for p in desc["props"]:
        if p["kind"] == "door" and p["open"] < stands:
            raise SceneError(
                f"{sid}: a door opens at {p['open']:g} of the clip, before the ego stands still "
                f"({stands:.2f}); the pass criterion holds the vehicle while a door is open"
            )
    return desc


def render_state(key: str, text: str) -> tuple[str, dict]:
    """Whether the committed dashboard of a scene was rendered from its current description."""
    mf = GALLERY / f"{key}.manifest.json"
    jpg = GALLERY / f"{key}.jpg"
    if not mf.exists() or not jpg.exists():
        return "not rendered", {}
    man = json.loads(mf.read_text(encoding="utf-8"))
    if man.get("dashboard_sha256") != hashlib.sha256(jpg.read_bytes()).hexdigest():
        return "**stale**: the picture is not the one its manifest records", man
    if man.get("description_sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
        return "**stale**: the description changed since the render", man
    errs = verify_manifest(key, man)
    if errs:
        return "**stale**: " + "; ".join(errs), man
    return "current", man


def verify_manifest(key: str, man: dict) -> list[str]:
    import build_blend  # noqa: PLC0415  (plain Python above its Blender part)

    desc = json.loads((OUT / f"{key}.json").read_text(encoding="utf-8"))
    return build_blend.verify(desc, man)


def gallery(descs: dict[str, dict], texts: dict[str, str]) -> str:
    """The page of the committed review dashboards, with the state of each render."""
    rows = [
        "| Dashboard | Scenario | Safety goals at stake | Events and triggering conditions | Condition (sample) | Render |",
        "|---|---|---|---|---|---|",
    ]
    for sid, d in descs.items():
        state, man = render_state(sid, texts[sid])
        sc_ = d["scenario"]
        cond = d["condition_label"] + (" (condition variant)" if d["variant"] else "")
        goals = ", ".join(f"{g['id']} ({g['asil']})" for g in sc_["goals"]) or "—"
        ev = ", ".join([e["id"] for e in sc_["events"]] + [t["id"] for t in sc_["triggers"]])
        link = f"[{sid}]({sid}.jpg)" if man else sid
        drawn_with = "CC0 assets" if (man.get("look") or {}).get("assets") else "procedural look"
        made = f"{state}; Blender {man.get('blender', '?')}, {drawn_with}" if man else state
        rows.append(f"| {link} | {sc_['name']} | {goals} | {ev or '—'} | {cond} | {made} |")
    first = next((s for s in descs if (GALLERY / f"{s}.jpg").exists()), None)
    hero = (
        [
            f"![Review dashboard of {first}: {descs[first]['scenario']['name']}; the chase view in the "
            "middle with the road users tagged, the forward and top views on the right, the scenario's "
            "records on the left, the moments of the clip along the bottom]"
            f"({first}.jpg)",
            "",
        ]
        if first
        else []
    )
    return "\n".join(
        [
            "# Scenario scene dashboards",
            "",
            f"> [!WARNING]\n> **{STAMP.capitalize()}.** Pictures for understanding and review only: no "
            "simulation has been run, nothing here is verification or validation evidence, and no "
            "scenario has been run (WP-V-03 §4).",
            "",
            "One review dashboard per scene of [`../scenes/`](../scenes/), rendered in Blender by "
            "[`../build_blend.py`](../build_blend.py) and explained in [`../README.md`](../README.md). "
            "This page is generated by [`../scene.py`](../scene.py); the Render column says whether "
            "each committed dashboard was made from the current description of its scene (the "
            "manifest beside it records the description's SHA-256, the picture's, and what was "
            "built). Re-render a stale one with "
            "`build_blend.py tools/sim/scenes/<id>.json --out tools/sim/dashboards --verify`, then "
            "run `scene.py`.",
            "",
            *hero,
            *rows,
            "",
        ]
    )


def build() -> dict[Path, str]:
    m, k, f = sc.load(), sc.known(), fx.load()
    errs = sc.check(m, k)
    if errs:
        raise SceneError("scenarios.yaml: " + "; ".join(errs))
    by_id = {s["id"]: s for s in m["scenarios"]}
    missing = sorted(set(LAYOUTS) - set(by_id))
    if missing:
        raise SceneError(f"layouts.py: no scenario {', '.join(missing)} in scenarios.yaml")
    out, descs = {}, {}
    for sid in sorted(LAYOUTS):
        for variant in [None] + list(LAYOUTS[sid].get("variants", [])):
            d = scene(by_id[sid], m, k, f, variant)
            if d["key"] in descs:
                raise SceneError(f"{sid}: two scenes are named {d['key']}")
            descs[d["key"]] = d
            out[OUT / f"{d['key']}.json"] = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    out[GALLERY / "README.md"] = gallery(descs, {s: out[OUT / f"{s}.json"] for s in descs})
    orphans = sorted(p.name for p in OUT.glob("*.json") if p not in out)
    orphans += sorted(p.name for p in GALLERY.glob("SC-*.*") if p.name.split(".")[0] not in descs)
    if orphans:
        raise SceneError(f"scenes/: {', '.join(orphans)} has no layout; delete it")
    return out


if __name__ == "__main__":
    fk.run(build, __doc__)
