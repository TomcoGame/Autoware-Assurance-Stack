#!/usr/bin/env python3
"""The ODD simulation environment of WP-V-08 §2 and the simulators of WP-P-07, from simenv.yaml.

Writes the generated tables of WP-V-08 §2 (simulators and their roles; what the simulation must
represent of the scenery, the environment and the dynamic elements; participants and their behaviour
bounds; the vehicle and sensor stand-ins) and the simulator rows of WP-P-07 (inventory and tool
confidence level). Each tool confidence level is computed from its tool impact and tool error
detection (ISO 26262-8 §11.4.5): TCL1 at TI1, otherwise TCL1, TCL2 or TCL3 for TD1, TD2 or TD3.
Simulator versions are read from the .repos files of the repository.

The model is refused when:
- an identifier is malformed or repeated, a simulator lacks a role or a basis for its ratings, its
  impact or detection is not a valid class, its pin does not resolve, or a pending decision is no
  longer open;
- an ODD attribute of the scenario model has no representation, or names a level or simulator that
  does not exist, or is not simulated without saying how it is covered instead; a simulator is used
  for nothing;
- a participant class of the ODD (ODD-16, ODD-18, ODD-19) has no entity, or names an OpenSCENARIO
  category that does not exist or a behaviour bound on a requirement that does not exist;
- a vehicle property is not one of WP-C-01 §6;
- a sensor stand-in names a kind outside WP-C-01 §5.1, a component that is not a sensor of WP-S-03,
  or a requirement that does not exist; a parameter carries a value instead of a name (the vehicle
  waits on DQ-008); a sensor component of WP-S-03 has no stand-in;
- a scenario run in simulation varies an ODD attribute that no simulator represents.

    python3 simenv.py            # write the generated tables of WP-V-08 §2 and WP-P-07
    python3 simenv.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
REPO = ASSURANCE.parent
for sub in (
    "01-management/figures",
    "01-management/decisions",
    "06-validation/scenarios",
    "03-system/tsc",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import scenarios  # noqa: E402
import tsc  # noqa: E402

MODEL = HERE / "simenv.yaml"
V08 = scenarios.V08
P07 = ASSURANCE / "07-supporting" / "WP-P-07-tool-classification-qualification.md"
C01 = ASSURANCE / "02-concept" / "WP-C-01-item-definition.md"
LEVELS = ("map", "object", "sensor", "link", "vehicle", "none")
# OpenSCENARIO 1.x VehicleCategory and PedestrianCategory.
CATEGORIES = {
    "car",
    "van",
    "truck",
    "trailer",
    "semitrailer",
    "bus",
    "motorbike",
    "bicycle",
    "train",
    "tram",
    "pedestrian",
    "wheelchair",
    "animal",
}
PARTICIPANTS = ("ODD-16", "ODD-18", "ODD-19")
SENSING = ("EL-03", "EL-06")


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def pin(p: dict | None) -> str | None:
    """The version a .repos file pins for a repository key, or None."""
    if not p:
        return None
    import yaml

    f = REPO / p["file"]
    if not f.is_file():
        return None
    repos = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("repositories", {})
    v = (repos.get(p["key"]) or {}).get("version")
    return str(v) if v is not None else None


def tcl(ti: str, td: str) -> str:
    return "TCL1" if ti == "TI1" else f"TCL{td[-1]}"


def known() -> dict:
    sm, sk = scenarios.load(), scenarios.known()
    t = tsc.load()
    inbound = {x["to"] for x in t["links"]}
    md = C01.read_text(encoding="utf-8")
    _, elems = fk.table(fk.section(md, "### 5.1"), "Element")
    sensors_row = next((fk.plain(" ".join(r)) for r in elems if fk.plain(r[0]) == "Sensors"), "")
    _, veh = fk.table(fk.section(md, "## 6."), "Property")
    return {
        "odd_model": sm["odd"],
        "odd_rows": sk["odd"],
        "scenarios": sm["scenarios"],
        "refs": sk["refs"],
        "components": {c["id"]: c for c in t["components"]},
        "sensor_components": {
            c["id"] for c in t["components"] if c["element"] in SENSING and c["id"] not in inbound
        },
        "sensors_row": sensors_row,
        "vehicle": {fk.plain(r[0]) for r in veh},
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    sims = {s["id"]: s for s in m.get("simulators", [])}
    for s in m.get("simulators", []):
        i = s["id"]
        new(i, r"SIM-\d\d")
        for key in ("name", "role", "impact_basis", "detection_basis"):
            if not s.get(key):
                errs.append(f"{i}: missing {key}")
        if s.get("level") not in LEVELS:
            errs.append(f"{i}: level must be one of {', '.join(LEVELS)}")
        if s.get("impact") not in ("TI1", "TI2"):
            errs.append(f"{i}: impact must be TI1 or TI2")
        if s.get("detection") not in ("TD1", "TD2", "TD3"):
            errs.append(f"{i}: detection must be TD1, TD2 or TD3")
        if s.get("pin") and pin(s["pin"]) is None:
            errs.append(f"{i}: pin {s['pin'].get('key')} is not in {s['pin'].get('file')}")
        p = s.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )
    used: set[str] = set()
    rep = m.get("represent") or {}
    for attr in k["odd_model"]:
        if attr not in rep:
            errs.append(f"{attr}: ODD attribute with no representation in the simulation")
    for attr, r in rep.items():
        if attr not in k["odd_model"]:
            errs.append(f"{attr}: not an attribute of the ODD model")
        if r.get("level") not in LEVELS:
            errs.append(f"{attr}: level must be one of {', '.join(LEVELS)}")
        for s in r.get("sims") or []:
            if s not in sims:
                errs.append(f"{attr}: simulator {s} does not exist")
            used.add(s)
        if not r.get("sims") and not r.get("instead"):
            errs.append(f"{attr}: not simulated, so it must say how it is covered instead")
        if r.get("sims") and not r.get("needs"):
            errs.append(f"{attr}: missing needs")
    for s in sims:
        if s not in used:
            errs.append(f"{s}: represents no ODD attribute")
    parts = m.get("participants") or {}
    for attr in PARTICIPANTS:
        for v in (k["odd_model"].get(attr) or {}).get("values", {}):
            if v not in parts:
                errs.append(f"{attr} {v}: participant class with no entity")
    for v, p in parts.items():
        if not any(v in (k["odd_model"].get(a) or {}).get("values", {}) for a in PARTICIPANTS):
            errs.append(f"participant {v}: not a value of {', '.join(PARTICIPANTS)}")
        if p.get("category") not in CATEGORIES:
            errs.append(f"participant {v}: {p.get('category')} is not an OpenSCENARIO category")
        if p.get("bound") not in k["refs"]:
            errs.append(f"participant {v}: bound {p.get('bound')} does not exist")
    for x in m.get("vehicle") or []:
        if x.get("property") not in k["vehicle"]:
            errs.append(f"vehicle: {x.get('property')!r} is not a property of WP-C-01 §6")
        if not x.get("model"):
            errs.append(f"vehicle {x.get('property')!r}: missing model")
    stood: set[str] = set()
    for s in m.get("sensors") or []:
        i = s["id"]
        new(i, r"SNS-\d\d")
        c = s.get("component")
        if c:
            if c not in k["sensor_components"]:
                errs.append(f"{i}: {c} is not a sensor component of WP-S-03")
            stood.add(c)
        elif s.get("kind", "") not in k["sensors_row"]:
            errs.append(f"{i}: kind {s.get('kind')!r} is not a sensor of WP-C-01 §5.1")
        for r in s.get("serves") or []:
            if r not in k["refs"]:
                errs.append(f"{i}: serves {r}, which does not exist")
        if not s.get("params"):
            errs.append(f"{i}: missing params")
        for p in s.get("params") or []:
            if not isinstance(p, str) or re.search(r"\d", p):
                errs.append(f"{i}: parameter {p!r} carries a value; the vehicle waits on DQ-008")
    for c in sorted(k["sensor_components"] - stood):
        errs.append(f"{c}: sensor component of WP-S-03 with no stand-in")
    for sc in k["scenarios"]:
        if "sim" not in sc.get("methods", []):
            continue
        for attr in scenarios.varies(sc):
            if attr in rep and not rep[attr].get("sims"):
                errs.append(
                    f"{sc['id']}: runs in simulation but varies {attr}, which no simulator represents"
                )
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    t = {}
    sims = {s["id"]: s for s in m["simulators"]}
    rows = ["| Simulator | Version | Level | Role |", "|---|---|---|---|"]
    for s in m["simulators"]:
        v = pin(s.get("pin"))
        ver = f"{v} (`{s['pin']['file']}`)" if v else "Not pinned"
        rows.append(f"| {s['id']} {cell(s['name'])} | {ver} | {s['level']} | {cell(s['role'])} |")
    t["simenv-simulators"] = "\n".join(rows)
    rep = m["represent"]
    for group, block in (
        ("Scenery", "simenv-scenery"),
        ("Environment", "simenv-environment"),
        ("Dynamic", "simenv-dynamic"),
    ):
        rows = [
            "| ODD attribute | Level | The simulation must represent | Simulators |",
            "|---|---|---|---|",
        ]
        for attr, row in k["odd_rows"].items():
            if row["group"] != group or attr not in rep:
                continue
            r = rep[attr]
            what = r.get("needs") or f"Not simulated: {r['instead']}"
            names = ", ".join(r.get("sims") or []) or "—"
            rows.append(f"| {attr} {row['name']} | {r['level']} | {cell(what)} | {names} |")
        t[block] = "\n".join(rows)
    rows = [
        "| Participant | ODD attribute | OpenSCENARIO category | Behaviour bounded by | Note |",
        "|---|---|---|---|---|",
    ]
    for v, p in m["participants"].items():
        attr = next(a for a in PARTICIPANTS if v in (k["odd_model"].get(a) or {}).get("values", {}))
        rows.append(
            f"| {v} | {attr} | {p['category']} | {p['bound']} (not yet fixed) | {cell(p.get('note', '—'))} |"
        )
    t["simenv-participants"] = "\n".join(rows)
    rows = ["| Vehicle property (WP-C-01 §6) | In the vehicle model | Value |", "|---|---|---|"]
    for x in m["vehicle"]:
        rows.append(f"| {cell(x['property'])} | {cell(x['model'])} | Parameter (DQ-008) |")
    t["simenv-vehicle"] = "\n".join(rows)
    rows = [
        "| Stand-in | Sensor | Channel | Serves | Parameters | Values |",
        "|---|---|---|---|---|---|",
    ]
    for s in m["sensors"]:
        c = s.get("component")
        what = f"{c} {k['components'][c]['name']}" if c else s["kind"]
        rows.append(
            f"| {s['id']} | {cell(what)} | {s['channel']} | {', '.join(s.get('serves') or []) or '—'} "
            f"| {', '.join(s['params'])} | Parameters (DQ-008) |"
        )
    t["simenv-sensors"] = "\n".join(rows)
    rows = [
        "| Tool | Version | Use | Tool impact | Tool error detection | TCL | State |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in m["simulators"]:
        v = pin(s.get("pin")) or "Not pinned"
        state = f"Proposed; waits on {s['pending']}" if s.get("pending") else "Proposed"
        rows.append(
            f"| {s['id']} {cell(s['name'])} | {v} | {cell(s['role'])} | {s['impact']}: {cell(s['impact_basis'])} "
            f"| {s['detection']}: {cell(s['detection_basis'])} | {tcl(s['impact'], s['detection'])} | {state} |"
        )
    t["simenv-tools"] = "\n".join(rows)
    sensor_level = [a for a, r in rep.items() if r["level"] == "sensor"]
    none = [a for a, r in rep.items() if not r.get("sims")]
    tcls = sorted({tcl(s["impact"], s["detection"]) for s in sims.values()})
    t["simenv-summary"] = (
        f"{len(sims)} simulators, {len(rep)} ODD attributes and what the simulation must represent of each: "
        f"{len(sensor_level)} need a sensor-level scene ({', '.join(sensor_level)}), "
        f"{len(none) or 'none'} {'is' if len(none) == 1 else 'are'} not simulated ({', '.join(none) or '—'}). "
        f"{len(m['participants'])} participant classes map to OpenSCENARIO categories. The vehicle and "
        f"{len(m['sensors'])} sensor stand-ins are parameters with no values until the vehicle is chosen (DQ-008). "
        f"Proposed tool confidence levels: {', '.join(tcls)}. No simulator has been validated (§3)."
    )
    return t


def fill(doc: str, blocks: dict[str, str], name: str) -> str:
    for block, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {block} (assurance/06-validation/simenv/simenv.py) -->"
        end = f"<!-- END GENERATED: {block} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"{name} needs exactly one generated block {block}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("simenv.yaml: " + "; ".join(errs))
    t = tables(m, k)
    p07 = {"simenv-tools": t.pop("simenv-tools")}
    return {
        V08: fill(V08.read_text(encoding="utf-8"), t, "WP-V-08"),
        P07: fill(P07.read_text(encoding="utf-8"), p07, "WP-P-07"),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
