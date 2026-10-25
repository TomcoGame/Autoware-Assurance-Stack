#!/usr/bin/env python3
"""The scenario catalogue of WP-V-03 and its ODD coverage in WP-V-08, generated from scenarios.yaml.

Writes the generated tables of WP-V-03 (catalogue, logical parameters, pass criteria) and of
WP-V-08 §4 (coverage of the ODD and of the analyses), Figure 2-1 of WP-V-03 (a card per scenario,
drawn by scards.py), Figure 4-1 of WP-V-08 (which ODD attributes each scenario varies), and the
folder page README.md with scenarios.csv. The safety goals at stake in a scenario are computed:
the goals of the hazards of its hazardous events, and of the HARA hazards its triggering conditions
can lead to through the insufficiencies they expose (WP-C-06) and the SOTIF hazards those cause
(WP-C-05).

The model is refused when:
- an identifier is malformed or repeated, or a scenario lacks a name, description, method or pass
  criterion, or exercises no hazardous event, triggering condition or misuse case;
- an ODD value quotes text that WP-C-02 §3 does not contain (an outside value: not in the "Outside
  the ODD" cell), or a numeric limit is not stated in its quote;
- a parameter names an ODD attribute or value that does not exist, has a range outside the ODD
  (including a speed above the posted limit), a unit other than the attribute's, or a behaviour bound
  on a requirement that does not exist;
- a scenario crosses the ODD boundary without citing the monitor that detects it and FSR-07.05;
- a reference to a situation, manoeuvre, OEDR item, hazardous event, triggering condition, misuse
  case, loss scenario or requirement does not exist, or an event's situation is not the scenario's;
- a safety goal at stake has no FSR of that goal among the pass references, or a scenario that
  exercises a triggering condition cites no SOTIF acceptance criterion;
- a triggering condition, misuse case or hazardous event has no scenario;
- a scenario has no sketch in scards.py, or a sketch has no scenario.

    python3 scenarios.py            # write the tables of WP-V-03 and WP-V-08, the figures and the folder page
    python3 scenarios.py --check    # fail if any is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "02-concept/hara",
    "02-concept/sotif",
    "02-concept/triggering",
    "02-concept/misuse",
    "02-concept/fallback",
    "08-analyses/stpa",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import fallback  # noqa: E402
import figkit as fk  # noqa: E402
import hara  # noqa: E402
import misuse  # noqa: E402
import scards  # noqa: E402
import sotif  # noqa: E402
import stpa  # noqa: E402
import terms  # noqa: E402
import triggering  # noqa: E402

MODEL = HERE / "scenarios.yaml"
V03 = ASSURANCE / "06-validation" / "WP-V-03-sotif-known-scenarios.md"
V08 = ASSURANCE / "06-validation" / "WP-V-08-simulation-credibility.md"
FIG = HERE / "fig-v08-4-1-coverage.svg"
FIG2 = HERE / "fig-v03-2-1-scenarios.svg"
CSV = HERE / "scenarios.csv"
README = HERE / "README.md"
VERIF = ASSURANCE / "03-system" / "verif" / "verif.yaml"
METHODS = {
    "sim": "Simulation",
    "xil": "In the loop",
    "track": "Track",
    "road": "Road",
    "bench": "Bench",
    "drill": "Drill",
}
MPH = 1.609344
CROSS = "FSR-07.05"
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def odd_rows() -> dict[str, dict]:
    """The attribute rows of WP-C-02 §3: id -> name, group, inside, outside, detected by."""
    md = fallback.ODD.read_text(encoding="utf-8")
    out = {}
    for sub, group in (("### 3.1", "Scenery"), ("### 3.2", "Environment"), ("### 3.3", "Dynamic")):
        head, rows = fk.table(fk.section(md, sub), "ID")
        for r in rows:
            out[fk.plain(r[0])] = {
                "name": fk.plain(r[fk.col(head, "Attribute")]),
                "group": group,
                "inside": fk.plain(r[fk.col(head, "Inside the ODD")]),
                "outside": fk.plain(r[fk.col(head, "Outside the ODD")]),
                "monitors": re.findall(r"MON-\d\d", r[fk.col(head, "Detected by")]),
            }
    return out


def ids_in(md: str, heading: str) -> set[str]:
    _, rows = fk.table(fk.section(md, heading), "ID")
    return {fk.plain(r[0]) for r in rows}


def known() -> dict:
    h = hara.load()
    t = triggering.load()
    md = fallback.ODD.read_text(encoding="utf-8")
    goals: dict[str, set[str]] = {}
    for g in h["goals"]:
        for hz in g["hazards"]:
            goals.setdefault(hz, set()).add(g["id"])
    sh = {x["id"]: x["hara"] for x in sotif.load()["hazards"]}
    fsc_goal = {x["id"]: x["goal"] for x in misuse.ai.fsc.load()["fsrs"]}
    return {
        "odd": odd_rows(),
        "situations": {x["id"]: x for x in h["situations"]},
        "events": {x["id"]: x for x in h["events"]},
        "goal_of_hazard": goals,
        "goals": {g["id"]: g for g in h["goals"]},
        "triggers": {x["id"]: x for x in t["triggers"]},
        "fis": {x["id"]: x for x in t["insufficiencies"]},
        "sh_hara": sh,
        "misuse": {x["id"]: x for x in misuse.load()["entries"]},
        "losses": {x["id"]: x for x in stpa.load()["scenarios"]},
        "oedr": ids_in(md, "### 5.2"),
        "manoeuvres": ids_in(md, "### 5.3"),
        "fsr_goal": fsc_goal,
        "acceptance": {x["id"] for x in sotif.load()["acceptance"]},
        "refs": misuse.known()["measures"]
        | {x["id"] for x in sotif.load()["acceptance"]}
        | {x["id"] for x in misuse.load()["requirements"]},
    }


def stake(s: dict, k: dict) -> list[str]:
    """Safety goals at stake: from the events' hazards, and from the triggering conditions through
    insufficiency, SOTIF hazard and HARA hazard."""
    hz = {k["events"][e]["hazard"] for e in s.get("events") or [] if e in k["events"]}
    for tc in s.get("triggers") or []:
        for fi in k["triggers"].get(tc, {}).get("exposes", []):
            for sh in k["fis"].get(fi, {}).get("hazards", []):
                hz |= set(k["sh_hara"].get(sh, []))
    return sorted({g for h in hz for g in k["goal_of_hazard"].get(h, ())})


def ceiling(m: dict, attr: str) -> float | None:
    """Upper limit of a numeric ODD attribute, lowered by the attribute that caps it."""
    a = m["odd"][attr]
    top = a.get("max")
    cap = a.get("capped_by")
    if cap and m["odd"].get(cap, {}).get("max") is not None:
        c = m["odd"][cap]
        cv = c["max"] * MPH if (c["unit"], a["unit"]) == ("mph", "km/h") else c["max"]
        top = cv if top is None else min(top, cv)
    return top


def check_odd(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    for attr, a in (m.get("odd") or {}).items():
        row = k["odd"].get(attr)
        if not row:
            errs.append(f"{attr}: not an attribute of WP-C-02 §3")
            continue
        if "values" in a:
            for v, d in a["values"].items():
                cell = row["outside"] if d.get("outside") else row["inside"]
                where = "Outside the ODD" if d.get("outside") else "the row"
                text = cell if d.get("outside") else f"{row['inside']} {row['outside']}"
                if not d.get("quote") or d["quote"] not in text:
                    errs.append(
                        f"{attr} {v}: quote {d.get('quote')!r} is not in {where} of WP-C-02"
                    )
                if d.get("outside") and not row["monitors"]:
                    errs.append(f"{attr} {v}: outside value, but no monitor detects {attr}")
        else:
            q = a.get("quote", "")
            if q not in row["inside"]:
                errs.append(f"{attr}: quote {q!r} is not in the Inside cell of WP-C-02")
            for key in ("min", "max"):
                if key in a and not re.search(rf"(?<![\d.]){a[key]:g}(?![\d.])", q):
                    errs.append(f"{attr}: {key} {a[key]:g} is not stated in its quote")
            if not a.get("unit"):
                errs.append(f"{attr}: numeric attribute needs a unit")
            if a.get("capped_by") and a["capped_by"] not in m["odd"]:
                errs.append(f"{attr}: capped by {a['capped_by']}, which is not in the model")
    return errs


def check_param(sid: str, p: dict, m: dict, k: dict) -> tuple[list[str], bool]:
    """Errors in one parameter, and whether it crosses the ODD boundary."""
    errs: list[str] = []
    if "bound" in p:
        if not p.get("name"):
            errs.append(f"{sid}: a behaviour bound needs a name")
        if p["bound"] not in k["refs"]:
            errs.append(f"{sid}: bound {p['bound']} does not exist")
        for key in ("min", "max", "values"):
            if key in p:
                errs.append(
                    f"{sid}: bound '{p.get('name')}' must not state {key} until it is fixed"
                )
        return errs, False
    attr = p.get("odd")
    a = (m.get("odd") or {}).get(attr)
    if not a:
        return [f"{sid}: parameter on {attr}, which is not in the ODD model"], False
    if "values" in a:
        crossing = False
        if not p.get("values"):
            errs.append(f"{sid}: {attr} is categorical and needs values")
        for v in p.get("values") or []:
            if v not in a["values"]:
                errs.append(f"{sid}: {attr} has no value {v}")
            elif a["values"][v].get("outside"):
                crossing = True
        return errs, crossing
    if p.get("unit") != a["unit"]:
        errs.append(f"{sid}: {attr} is in {a['unit']}, not {p.get('unit')}")
    lo, hi = p.get("min"), p.get("max")
    if lo is None and hi is None:
        errs.append(f"{sid}: {attr} needs min or max")
    top = ceiling(m, attr)
    for v in (lo, hi):
        if v is None:
            continue
        if v < (a["min"] if a.get("min") is not None else 0):
            errs.append(
                f"{sid}: {attr} value {v:g} is below the ODD limit {a.get('min', 0):g} {a['unit']}"
            )
        if top is not None and v > top + 1e-9:
            errs.append(f"{sid}: {attr} value {v:g} is above the ODD limit {top:g} {a['unit']}")
    if lo is not None and hi is not None and lo > hi:
        errs.append(f"{sid}: {attr} min is above max")
    return errs, bool(p.get("crosses"))


def check(m: dict, k: dict) -> list[str]:
    errs = check_odd(m, k)
    seen: set[str] = set()
    covered = {"triggers": set(), "misuse": set(), "events": set()}
    for s in m.get("scenarios", []):
        i = s.get("id", "?")
        if not re.fullmatch(r"SC-\d\d", i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        for key in ("name", "description", "situations", "methods"):
            if not s.get(key):
                errs.append(f"{i}: missing {key}")
        for x in s.get("methods") or []:
            if x not in METHODS:
                errs.append(f"{i}: method {x} must be one of {', '.join(METHODS)}")
        for key, universe, what in (
            ("situations", k["situations"], "situation"),
            ("manoeuvres", k["manoeuvres"], "manoeuvre"),
            ("oedr", k["oedr"], "OEDR item"),
            ("events", k["events"], "hazardous event"),
            ("triggers", k["triggers"], "triggering condition"),
            ("misuse", k["misuse"], "misuse case"),
            ("losses", k["losses"], "loss scenario"),
        ):
            for x in s.get(key) or []:
                if x not in universe:
                    errs.append(f"{i}: {what} {x} does not exist")
                elif key in covered:
                    covered[key].add(x)
        if not (s.get("events") or s.get("triggers") or s.get("misuse")):
            errs.append(f"{i}: exercises no hazardous event, triggering condition or misuse case")
        for e in s.get("events") or []:
            os_ = k["events"].get(e, {}).get("situation")
            if os_ and os_ not in (s.get("situations") or []):
                errs.append(f"{i}: {e} happens in {os_}, which is not among its situations")
        crossing, monitors = False, set()
        for p in s.get("parameters") or []:
            e, c = check_param(i, p, m, k)
            errs += e
            if c:
                crossing = True
                monitors |= set(k["odd"].get(p.get("odd"), {}).get("monitors", []))
        ps = s.get("pass") or {}
        refs = ps.get("refs") or []
        if not ps.get("criterion") or not refs:
            errs.append(f"{i}: needs a pass criterion and the requirements it is judged against")
        for r in refs:
            if r not in k["refs"]:
                errs.append(f"{i}: requirement {r} does not exist")
        if crossing and not (CROSS in refs and monitors & set(refs)):
            errs.append(
                f"{i}: crosses the ODD boundary, so it must cite {CROSS} and one of {', '.join(sorted(monitors))}"
            )
        for g in stake(s, k):
            if not any(k["fsr_goal"].get(r) == g for r in refs):
                errs.append(f"{i}: {g} is at stake, but no FSR of {g} is in its pass references")
        if s.get("triggers") and not k["acceptance"] & set(refs):
            errs.append(f"{i}: exercises a triggering condition but cites no acceptance criterion")
    for key, universe, what in (
        ("triggers", k["triggers"], "triggering condition"),
        ("misuse", k["misuse"], "misuse case"),
        ("events", k["events"], "hazardous event"),
    ):
        for x in universe:
            if x not in covered[key]:
                errs.append(f"{x}: {what} with no scenario")
    errs += scards.check([s.get("id") for s in m.get("scenarios", [])])
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def ids(xs) -> str:
    return ", ".join(xs) if xs else "—"


def param_text(p: dict, m: dict) -> tuple[str, str, str]:
    """(parameter, range or values, source) of one parameter row."""
    if "bound" in p:
        return p["name"], f"Bound stated by {p['bound']}, not yet fixed", p["bound"]
    attr = p["odd"]
    a = m["odd"][attr]
    if "values" in a:
        vals = ", ".join(
            v + (" (outside)" if a["values"][v].get("outside") else "") for v in p["values"]
        )
        return attr, vals, f"WP-C-02 {attr}"
    lo, hi = p.get("min"), p.get("max")
    if hi is None:
        rng = f"{lo:g} {a['unit']} and above"
    elif lo is None:
        rng = f"up to {hi:g} {a['unit']}"
    else:
        rng = f"{lo:g} to {hi:g} {a['unit']}"
    if p.get("crosses"):
        rng += ", and across the limit"
    return attr, rng, f"WP-C-02 {attr}"


def varies(s: dict) -> dict[str, bool]:
    """ODD attributes a scenario varies -> whether it crosses the boundary on that attribute."""
    out: dict[str, bool] = {}
    for p in s.get("parameters") or []:
        if "odd" in p:
            out[p["odd"]] = out.get(p["odd"], False) or bool(p.get("crosses"))
    return out


def crosses_on(s: dict, m: dict) -> dict[str, bool]:
    out = varies(s)
    for p in s.get("parameters") or []:
        a = m["odd"].get(p.get("odd"), {})
        if any(a.get("values", {}).get(v, {}).get("outside") for v in p.get("values") or []):
            out[p["odd"]] = True
    return out


def tables(m: dict, k: dict) -> dict[str, str]:
    t = {}
    sc = m["scenarios"]
    rows = [
        "| Scenario | Situations | Manoeuvres and OEDR | Hazardous events | Triggering conditions | Misuse | Loss scenarios | Goals at stake | Methods |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in sc:
        rows.append(
            f"| {s['id']} {cell(s['name'])} | {ids(s['situations'])} "
            f"| {ids((s.get('manoeuvres') or []) + (s.get('oedr') or []))} | {ids(s.get('events'))} "
            f"| {ids(s.get('triggers'))} | {ids(s.get('misuse'))} | {ids(s.get('losses'))} "
            f"| {ids(stake(s, k))} | {', '.join(METHODS[x] for x in s['methods'])} |"
        )
    t["scenarios-catalogue"] = "\n".join(rows)
    rows = ["| Scenario | Parameter | Range or values | Source |", "|---|---|---|---|"]
    for s in sc:
        for n, p in enumerate(s.get("parameters") or []):
            name, rng, src = param_text(p, m)
            label = f"{s['id']}" if n == 0 else ""
            if "odd" in p:
                name = f"{p['odd']} {k['odd'][p['odd']]['name']}"
            rows.append(f"| {label} | {cell(name)} | {cell(rng)} | {src} |")
    t["scenarios-parameters"] = "\n".join(rows)
    rows = ["| Scenario | Pass criterion | Judged against |", "|---|---|---|"]
    for s in sc:
        rows.append(f"| {s['id']} | {cell(s['pass']['criterion'])} | {ids(s['pass']['refs'])} |")
    t["scenarios-pass"] = "\n".join(rows)
    bounds = sorted({p["bound"] for s in sc for p in s.get("parameters") or [] if "bound" in p})
    nb = sum(1 for s in sc for p in s.get("parameters") or [] if "bound" in p)
    cross = [s["id"] for s in sc if any(crosses_on(s, m).values())]
    t["scenarios-cards"] = (
        "![Figure 2-1: one card per scenario SC-01 to SC-26. Each has a top-down sketch of one concrete instance "
        "of the logical scenario: the vehicle in blue, the road user or condition the scenario is about in amber, "
        "other road users grey, and the behaviour the pass criterion asks for as a dashed green path with its "
        "moment ringed. Under the sketch: the hazardous events, triggering conditions, misuse cases and loss "
        "scenarios it exercises, the safety goals at stake, the ODD attributes it varies (outlined red where it "
        "sweeps across the ODD boundary) and the behaviour bounds not yet fixed, its methods, its pass criterion "
        "with the requirements it is judged against, and the verification cases of WP-S-09 that run it. The same "
        f"information is in the tables of §2.](scenarios/{FIG2.name})\n\n"
        "*Figure 2-1. What each known scenario sets up, and when it passes. Schematic: one instance chosen to "
        "explain each scenario; the ranges are in §2.2, and no scenario has been run. Drawn by "
        "[`scenarios/scenarios.py`](scenarios/scenarios.py) and `scenarios/scards.py`; CI fails if it is stale. "
        f"Every scenario is also in [`scenarios/{CSV.name}`](scenarios/{CSV.name}).*"
    )
    t["scenarios-summary"] = (
        f"{len(sc)} logical scenarios exercise all {len(k['triggers'])} triggering conditions of WP-C-06, all "
        f"{len(k['misuse'])} misuse and interaction entries of WP-C-08 and all {len(k['events'])} hazardous events "
        f"of WP-C-03. Their parameters take only values WP-C-02 states; {nb} behaviour parameters wait on the bounds "
        f"that {', '.join(bounds)} state but no work product has fixed yet. {len(cross)} scenarios "
        f"({', '.join(cross)}) cross the ODD boundary to test a monitor. Each pass criterion is judged against "
        "existing requirements. No scenario has been run."
    )
    # WP-V-08 §4: ODD coverage
    rows = [
        "| ODD attribute | Values the ODD admits | Exercised by | Values not exercised |",
        "|---|---|---|---|",
    ]
    for attr, row in k["odd"].items():
        a = m["odd"].get(attr)
        users = [s["id"] for s in sc if attr in varies(s)]
        if not a:
            rows.append(f"| {attr} {row['name']} | Not in the model | — | — |")
            continue
        if "values" in a:
            used = {
                v
                for s in sc
                for p in s.get("parameters") or []
                if p.get("odd") == attr
                for v in p["values"]
            }
            admits = ", ".join(v for v, d in a["values"].items() if not d.get("outside")) or "None"
            outside = [v for v, d in a["values"].items() if d.get("outside")]
            if outside:
                admits += f"; outside, for monitor tests: {', '.join(outside)}"
            gap = [v for v in a["values"] if v not in used]
        else:
            top = ceiling(m, attr)
            lo = f"{a['min']:g}" if a.get("min") is not None else "0"
            admits = (
                f"{lo} to {a['max']:g} {a['unit']}"
                if top is not None
                else f"{lo} {a['unit']} and above"
            )
            if top is not None and top < a["max"]:
                admits += f", capped by {a['capped_by']} at {top:.1f} {a['unit']}"
            gap = []
        rows.append(f"| {attr} {row['name']} | {cell(admits)} | {ids(users)} | {ids(gap)} |")
    t["scenarios-coverage-odd"] = "\n".join(rows)
    rows = ["| Analysis | Items | With a scenario | Without |", "|---|---|---|---|"]
    for name, key, universe in (
        ("Triggering conditions (WP-C-06)", "triggers", k["triggers"]),
        ("Misuse and interaction (WP-C-08)", "misuse", k["misuse"]),
        ("Hazardous events (WP-C-03)", "events", k["events"]),
        ("STPA loss scenarios (WP-A-05)", "losses", k["losses"]),
    ):
        used = {x for s in sc for x in s.get(key) or []}
        missing = [x for x in universe if x not in used]
        rows.append(
            f"| {name} | {len(universe)} | {len(universe) - len(missing)} | {ids(missing)} |"
        )
    goals = {g for s in sc for g in stake(s, k)}
    rows.append(
        f"| Safety goals (WP-C-03) | {len(k['goals'])} | {len(goals & set(k['goals']))} "
        f"| {ids([g for g in k['goals'] if g not in goals])} |"
    )
    t["scenarios-coverage-analyses"] = "\n".join(rows)
    return t


def fill(doc: str, blocks: dict[str, str], name: str) -> str:
    for block, body in blocks.items():
        begin = (
            f"<!-- BEGIN GENERATED: {block} (assurance/06-validation/scenarios/scenarios.py) -->"
        )
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


EXTRA = """svg .on { fill:var(--acc); }
svg .x { fill:var(--badsoft); stroke:var(--bad); stroke-width:1.6; }
svg .off { fill:var(--card); }
svg .grp { stroke:var(--ink3); stroke-width:1; fill:none; }
"""


def figure(m: dict, k: dict) -> str:
    attrs = list(k["odd"])
    sc = m["scenarios"]
    lx, cx, cw, ch, top = 24, 268, 17, 17, 128
    body = [
        fk.text(24, 32, "Which ODD conditions each scenario varies", "h"),
        fk.text(
            24, 54, "WP-V-08 §4: a filled cell is an ODD attribute (WP-C-02 §3) the scenario", "t"
        ),
        fk.text(24, 71, "sweeps; a red outline marks a sweep across the ODD boundary", "t"),
    ]
    groups: dict[str, list[int]] = {}
    for n, a in enumerate(attrs):
        groups.setdefault(k["odd"][a]["group"], []).append(n)
    for g, cols in groups.items():
        x0, x1 = cx + cols[0] * cw, cx + (cols[-1] + 1) * cw - 3
        body.append(fk.el("path", None, d=f"M{fk.num(x0)} 96 L{fk.num(x1)} 96", class_="grp"))
        body.append(fk.text(x0, 90, g, "s"))
    for n, a in enumerate(attrs):
        body.append(fk.text(cx + n * cw + 7, top - 12, a[-2:], "s", "middle"))
    for r, s in enumerate(sc):
        y = top + r * ch
        body.append(fk.text(lx, y + 12, fk.fit(f"{s['id']} {s['name']}", cx - lx - 10, "s"), "s"))
        v = crosses_on(s, m)
        for n, a in enumerate(attrs):
            cls = "x" if v.get(a) else ("on" if a in v else "off")
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=cx + n * cw,
                    y=y + 1,
                    width=cw - 3,
                    height=ch - 3,
                    rx=2,
                    class_=cls,
                )
            )
    y = top + len(sc) * ch + 16
    counts = [sum(1 for s in sc if a in varies(s)) for a in attrs]
    body.append(fk.text(cx - 10, y, "Scenarios", "s", "end"))
    for n, c in enumerate(counts):
        body.append(fk.text(cx + n * cw + 7, y, str(c), "s", "middle"))
    y += 26
    legend = [("on", "varied"), ("x", "swept across the boundary"), ("off", "held fixed")]
    lxx = 24
    for cls, lab in legend:
        body.append(fk.el("rect", None, x=lxx, y=y - 11, width=14, height=14, rx=2, class_=cls))
        body.append(fk.text(lxx + 20, y, lab, "s"))
        lxx += 34 + fk.width(lab, "s")
    y += 22
    gaps = [a for a, c in zip(attrs, counts) if c == 0]
    note = (
        f"Not varied by any scenario: {', '.join(gaps)}."
        if gaps
        else "Every ODD attribute is varied."
    )
    body.append(fk.text(24, y, note, "s"))
    y += 18
    desc = (
        f"Matrix of {len(sc)} scenarios against the {len(attrs)} ODD attributes of WP-C-02. Scenarios per "
        "attribute: "
        + "; ".join(f"{a} {k['odd'][a]['name']} {c}" for a, c in zip(attrs, counts))
        + ". Across the boundary: "
        + "; ".join(
            f"{s['id']} on {', '.join(a for a, x in crosses_on(s, m).items() if x)}"
            for s in sc
            if any(crosses_on(s, m).values())
        )
        + f". {note}"
    )
    return fk.svg(W, int(y), "WP-V-08 Figure 4-1: ODD coverage of the scenarios", desc, body, EXTRA)


def run_by() -> dict[str, list[str]]:
    """Scenario -> the verification cases of WP-S-09 that run it (read from verif.yaml, which imports this)."""
    import yaml

    out: dict[str, list[str]] = {}
    for c in yaml.safe_load(VERIF.read_text(encoding="utf-8"))["cases"]:
        for sid in c.get("scenarios") or []:
            out.setdefault(sid, []).append(c["id"])
    return out


def bounds(s: dict) -> list[str]:
    return [p["bound"] for p in s.get("parameters") or [] if "bound" in p]


def card_data(m: dict, k: dict) -> list[dict]:
    """One card per scenario: what it exercises, what it varies, how it runs and when it passes."""
    runs = run_by()
    cards = []
    for s in m["scenarios"]:
        ex = [
            (label, s.get(key) or [])
            for label, key in (
                ("Hazardous events", "events"),
                ("Triggering conditions", "triggers"),
                ("Misuse", "misuse"),
                ("Loss scenarios", "losses"),
            )
        ]
        ex.append(("Goals at stake", stake(s, k)))
        cross = crosses_on(s, m)
        cards.append(
            {
                "id": s["id"],
                "name": s["name"],
                "crosses": any(cross.values()),
                "exercises": [(label, xs) for label, xs in ex if xs],
                "odd": list(cross.items()),
                "bounds": sorted(set(bounds(s))),
                "methods": [METHODS[x] for x in s["methods"]],
                "criterion": s["pass"]["criterion"],
                "refs": s["pass"]["refs"],
                "run_by": runs.get(s["id"], []),
            }
        )
    return cards


def scenarios_csv(m: dict, k: dict) -> str:
    """Every scenario with what it exercises and varies, how it runs, when it passes, and its result."""
    import csv
    import io

    runs = run_by()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(
        [
            "ID",
            "Scenario",
            "Description",
            "Situations (WP-C-03)",
            "Manoeuvres and OEDR (WP-C-02)",
            "Hazardous events (WP-C-03)",
            "Triggering conditions (WP-C-06)",
            "Misuse (WP-C-08)",
            "Loss scenarios (WP-A-05)",
            "Safety goals at stake",
            "ODD attributes varied (WP-C-02)",
            "Crosses the ODD boundary on",
            "Behaviour bounds not yet fixed",
            "Methods",
            "Pass criterion",
            "Judged against",
            "Run by (WP-S-09)",
            "Result",
        ]
    )
    for s in m["scenarios"]:
        cross = crosses_on(s, m)
        w.writerow(
            [
                s["id"],
                s["name"],
                s["description"],
                ids(s["situations"]),
                ids((s.get("manoeuvres") or []) + (s.get("oedr") or [])),
                ids(s.get("events")),
                ids(s.get("triggers")),
                ids(s.get("misuse")),
                ids(s.get("losses")),
                ids(stake(s, k)),
                ids(list(cross)),
                ids([a for a, x in cross.items() if x]),
                ids(sorted(set(bounds(s)))),
                ", ".join(METHODS[x] for x in s["methods"]),
                s["pass"]["criterion"],
                ids(s["pass"]["refs"]),
                ids(runs.get(s["id"], [])),
                "Not run",
            ]
        )
    return buf.getvalue()


def here(md: str) -> str:
    """Text of WP-V-03 or WP-V-08 with its relative links rewritten to work from this folder."""
    md = md.replace("](scenarios/", "](")
    return re.sub(r"\]\((?!https?:|#|fig-|scenarios\.|scards\.|README)", "](../", md)


def readme(t: dict[str, str], v03: str, v08: str) -> str:
    """The folder page: the known scenarios of WP-V-03 and their coverage of the ODD (WP-V-08 §4)."""

    def part(doc: str, heading: str) -> str:
        return here(fk.section(doc, heading).strip())

    files = [
        "| File | What it holds |",
        "|---|---|",
        f"| [`{CSV.name}`]({CSV.name}) | Every scenario with what it exercises, the goals at stake, the ODD attributes it varies and crosses, the open behaviour bounds, its methods, pass criterion, the verification cases that run it and its result |",
        f"| [`{FIG2.name}`]({FIG2.name}) | WP-V-03 Figure 2-1, what each known scenario sets up and when it passes |",
        f"| [`{FIG.name}`]({FIG.name}) | WP-V-08 Figure 4-1, which ODD attributes each scenario varies |",
        "| [`scenarios.yaml`](scenarios.yaml) | The structured reading of the ODD and the logical scenarios |",
        "| [`scenarios.py`](scenarios.py), [`scards.py`](scards.py) | The generator: checks the model against the ODD and the analyses, and writes the tables of WP-V-03 and WP-V-08 §4 and everything here |",
    ]
    lines = [
        "<!-- Generated by assurance/06-validation/scenarios/scenarios.py; do not edit by hand. -->",
        "",
        "# Known scenarios",
        "",
        "The known hazardous scenarios of [WP-V-03](../WP-V-03-sotif-known-scenarios.md) on one page: what each "
        "logical scenario sets up, what it exercises from the analyses, the ODD ranges it varies, how it is run and "
        "when it passes, and how the catalogue covers the ODD ([WP-V-08 §4](../WP-V-08-simulation-credibility.md"
        "#4-scenario-coverage-metrics-against-the-odd)). The [system verification](../../03-system/verif/README.md) "
        "runs them. Everything here is generated by `scenarios.py` from `scenarios.yaml`; CI fails if it is stale. "
        "Everything is a draft by Claude (I0); no scenario has been run.",
        "",
        t["scenarios-summary"],
        "",
        "1. [What this covers](#1-what-this-covers)",
        "2. [Scenario catalogue](#2-scenario-catalogue)",
        "3. [Evaluation method](#3-evaluation-method)",
        "4. [Results](#4-results)",
        "5. [Open items](#5-open-items)",
        "6. [Coverage of the ODD and the analyses](#6-coverage-of-the-odd-and-the-analyses)",
        "7. [Files in this folder](#7-files-in-this-folder)",
        "",
        "## 1. What this covers",
        "",
        re.sub(
            r"<!-- BEGIN GENERATED: scenarios-summary .*?END GENERATED: scenarios-summary -->\n\n",
            "",
            part(v03, "## 1. Purpose"),
            flags=re.S,
        ),
        "",
        "## 2. Scenario catalogue",
        "",
        f"Every scenario is also in [`{CSV.name}`]({CSV.name}), which GitHub shows as a table that can be searched.",
        "",
        part(v03, "## 2. Scenario catalogue"),
        "",
        "## 3. Evaluation method",
        "",
        part(v03, "## 3. Evaluation method"),
        "",
        "## 4. Results",
        "",
        part(v03, "## 4. Results"),
        "",
        "## 5. Open items",
        "",
        part(v03, "## 5. Open items"),
        "",
        "## 6. Coverage of the ODD and the analyses",
        "",
        "From [WP-V-08 §4](../WP-V-08-simulation-credibility.md#4-scenario-coverage-metrics-against-the-odd).",
        "",
        re.sub(
            r"^### 4\.",
            "### 6.",
            part(v08, "## 4. Scenario coverage metrics against the ODD"),
            flags=re.M,
        ),
        "",
        "## 7. Files in this folder",
        "",
        *files,
        "",
    ]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("scenarios.yaml: " + "; ".join(errs))
    t = tables(m, k)
    v03 = {
        x: t[x]
        for x in (
            "scenarios-summary",
            "scenarios-cards",
            "scenarios-catalogue",
            "scenarios-parameters",
            "scenarios-pass",
        )
    }
    v08 = {x: t[x] for x in ("scenarios-coverage-odd", "scenarios-coverage-analyses")}
    doc3 = fill(V03.read_text(encoding="utf-8"), v03, "WP-V-03")
    doc8 = fill(V08.read_text(encoding="utf-8"), v08, "WP-V-08")
    return {
        V03: doc3,
        V08: doc8,
        FIG: figure(m, k),
        FIG2: scards.sheet(card_data(m, k)),
        CSV: scenarios_csv(m, k),
        README: terms.close(readme(t, doc3, doc8), README),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
