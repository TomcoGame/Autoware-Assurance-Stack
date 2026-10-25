#!/usr/bin/env python3
"""The cybersecurity requirements and architecture of WP-S-07, generated from secarch.yaml.

Writes the generated tables of WP-S-07 (technical cybersecurity requirements with their CAL,
requirements on the operating environment, trust zones, conduits, interfaces exposed outside the
vehicle) and Figure 3-1 (the trust zones, their components, the conduits between them and the
exposed interfaces of each). A technical requirement's CAL is the highest CAL of the goals of the
WP-C-10 requirement it refines.

The model is refused when:
- an identifier is malformed or repeated, or a technical requirement does not carry the number of
  the requirement it refines;
- a component of WP-S-03 is in no zone or in two, or a zone names one that does not exist;
- an interface of WP-S-05 crosses zones without a conduit, a conduit joins two components of one
  zone, or a conduit or exposed interface has no control;
- a control, threat, requirement or component named does not exist;
- an item-level requirement of WP-C-10 is refined by no technical requirement, or a technical
  requirement refines one of the operating environment;
- a threat of the TARA reaches the item through no exposed interface, or a threat whose risk is
  reduced is exposed through an interface none of whose controls serves its goal;
- an exposed interface has no threat and no decision that says why;
- a pending decision is no longer open, or a decision rested on is not answered.

    python3 secarch.py            # write WP-S-07's generated tables and Figure 3-1
    python3 secarch.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "01-management/decisions",
    "02-concept/tara",
    "02-concept/cybersecurity",
    "03-system/tsc",
    "03-system/hsi",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import cybersecurity  # noqa: E402
import figkit as fk  # noqa: E402
import hsi  # noqa: E402
import terms  # noqa: E402
import tsc  # noqa: E402

sys.path.insert(0, str(HERE))
import acards  # noqa: E402

MODEL = HERE / "secarch.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-07-cybersecurity-requirements-architecture.md"
FIG = HERE / "fig-s07-3-1-zones.svg"
FIG2 = HERE / "fig-s07-4-1-attack-paths.svg"
CSV = HERE / "requirements.csv"
README = HERE / "README.md"
ALLOC = ("software", "hardware", "both")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    cm = cybersecurity.load()
    ck = cybersecurity.known()
    t = tsc.load()
    return {
        "cyber": cm,
        "cyber_known": ck,
        "csrs": {r["id"]: r for r in cm["requirements"]},
        "goals": {g["id"]: g for g in cm["goals"]},
        "claimed": {ts for c in cm["claims"] for ts in c["threats"]},
        "threats": ck["threats"],
        "tara_controls": ck["controls"],
        "components": {c["id"]: c for c in t["components"]},
        "mechanisms": {s["id"] for s in t["mechanisms"]},
        "interfaces": {f["id"]: f for f in hsi.load()["interfaces"]},
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
        "choices": {
            d["id"]: d["answer"]["choice"] for d in check_decisions.load() if d.get("answer")
        },
    }


def cal(r: dict, k: dict) -> str | None:
    """The CAL of a technical requirement: the highest of the goals its WP-C-10 requirement serves."""
    cals = [
        cybersecurity.cal(k["cyber"], k["cyber_known"], k["goals"][g])
        for g in k["csrs"][r["csr"]]["goals"]
    ]
    cals = [c for c in cals if c]
    return max(cals, key=cybersecurity.CALS.index) if cals else None


def goals_of(c: str, m: dict, k: dict) -> set[str]:
    """The cybersecurity goals a control serves: through its requirement, or none for a CR or SM."""
    tc = {r["id"]: r for r in m.get("tcsrs", [])}
    if c in tc:
        return set(k["csrs"][tc[c]["csr"]]["goals"])
    if c in k["csrs"]:
        return set(k["csrs"][c]["goals"])
    return set()


def decided(e: dict, k: dict) -> str:
    if e.get("pending"):
        return f"Waits on {e['pending']}"
    if e.get("decision"):
        return f"{e['decision']} {k['choices'].get(e['decision'], '')}".strip()
    return "—"


def zone_of(m: dict) -> dict[str, str]:
    return {c: z["id"] for z in m["zones"] for c in z["components"]}


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    def pending(i: str, d: str | None) -> None:
        if d and k["decisions"].get(d) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {d}, which is {k['decisions'].get(d, 'not in the register')}; apply the decision"
            )

    tc = {r["id"]: r for r in m.get("tcsrs", [])}
    env = {i for i, r in k["csrs"].items() if r["scope"] == "environment"}

    def control(owner: str, c: str) -> None:
        if not (c in tc or c in env or c in k["tara_controls"] or c in k["mechanisms"]):
            errs.append(
                f"{owner}: control {c} is not a technical or environment requirement, CR or SM"
            )

    zones = {z["id"]: z for z in m.get("zones", [])}
    placed: dict[str, list[str]] = {}
    for z in m.get("zones", []):
        new(z["id"], r"SZ-\d")
        for c in z.get("components") or []:
            if c not in k["components"]:
                errs.append(f"{z['id']}: component {c} does not exist")
            placed.setdefault(c, []).append(z["id"])
    for c in k["components"]:
        if len(placed.get(c, [])) != 1:
            errs.append(f"{c}: must be in exactly one zone, is in {placed.get(c, [])}")
    if errs:
        return errs
    zof = zone_of(m)
    conduits = {x["interface"]: x for x in m.get("conduits", [])}
    for i, f in k["interfaces"].items():
        a, b = (zof[c] for c in f["link"])
        if a != b and i not in conduits:
            errs.append(f"{i}: crosses {a} and {b} but is not a conduit")
        if a == b and i in conduits:
            errs.append(f"{i}: joins two components of {a}; it is not a conduit")
    for x in m.get("conduits", []):
        if x["interface"] not in k["interfaces"]:
            errs.append(f"conduit {x['interface']}: not an interface of WP-S-05")
        if x.get("via") and x["via"] not in zones:
            errs.append(f"conduit {x['interface']}: zone {x['via']} does not exist")
        if not x.get("controls"):
            errs.append(f"conduit {x['interface']}: no control")
        for c in x.get("controls") or []:
            control(f"conduit {x['interface']}", c)
    exposed: set[str] = set()
    for e in m.get("external", []):
        new(e["id"], r"EX-\d\d")
        if e.get("zone") not in zones:
            errs.append(f"{e['id']}: zone {e.get('zone')} does not exist")
        if e.get("vector") not in k["cyber"]["method"]["vectors"]:
            errs.append(f"{e['id']}: vector {e.get('vector')} is not an attack vector of WP-C-10")
        for c in e.get("controls") or []:
            control(e["id"], c)
        if e.get("threats") and not e.get("controls"):
            errs.append(f"{e['id']}: exposed to threats but has no control")
        served = set().union(*(goals_of(c, m, k) for c in e.get("controls") or [])) | set()
        for ts in e.get("threats") or []:
            if ts not in k["threats"]:
                errs.append(f"{e['id']}: threat {ts} does not exist")
                continue
            exposed.add(ts)
            gs = {g for g, x in k["goals"].items() if ts in x["threats"]}
            if gs and not gs & served:
                errs.append(
                    f"{e['id']}: {ts} is reduced under {', '.join(sorted(gs))}, but no control here serves it"
                )
        pending(e["id"], e.get("pending"))
        if e.get("decision") and k["decisions"].get(e["decision"]) not in ("answered", "applied"):
            errs.append(f"{e['id']}: rests on {e['decision']}, which is not answered")
        if not e.get("threats") and not (e.get("pending") or e.get("decision")):
            errs.append(f"{e['id']}: no threat in the TARA, and no decision says why")
    for ts in k["threats"]:
        if ts not in exposed:
            errs.append(f"{ts}: reaches the item through no exposed interface")
    refined: set[str] = set()
    for r in m.get("tcsrs", []):
        i = r["id"]
        new(i, r"CSTR-\d\d\.\d\d")
        csr = k["csrs"].get(r.get("csr"))
        if not csr:
            errs.append(f"{i}: {r.get('csr')} is not a requirement of WP-C-10")
            continue
        if i[5:7] != r["csr"][4:]:
            errs.append(f"{i}: does not carry the number of {r['csr']}")
        if csr["scope"] != "item":
            errs.append(f"{i}: refines {r['csr']}, which the operating environment meets")
        refined.add(r["csr"])
        if r.get("component") not in k["components"]:
            errs.append(f"{i}: component {r.get('component')} does not exist")
        if r.get("alloc") not in ALLOC:
            errs.append(f"{i}: alloc must be one of {', '.join(ALLOC)}")
        for key in ("text", "verify"):
            if not r.get(key):
                errs.append(f"{i}: missing {key}")
    for i, r in k["csrs"].items():
        if r["scope"] == "item" and i not in refined:
            errs.append(f"{i}: item-level requirement refined by no technical requirement")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    comps = k["components"]
    zof = zone_of(m)
    zones = {z["id"]: z for z in m["zones"]}
    t = {}
    rows = [
        "| ID | Technical cybersecurity requirement | Component | Zone | Allocation | CAL | Refines | Verification |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(m["tcsrs"], key=lambda r: r["id"]):
        c = r["component"]
        rows.append(
            f"| {r['id']} | {cell(r['text'])} | {c} {cell(comps[c]['name'])} | {zof[c]} | {r['alloc']} "
            f"| {cal(r, k) or '—'} | {r['csr']} | {cell(r['verify'])} |"
        )
    t["secarch-requirements"] = "\n".join(rows)
    rows = ["| Requirement | Met by | Goals | Text |", "|---|---|---|---|"]
    for i, r in k["csrs"].items():
        if r["scope"] == "environment":
            rows.append(
                f"| {i} | {cell(r['element'])} | {', '.join(r['goals'])} | {cell(r['text'])} |"
            )
    t["secarch-environment"] = "\n".join(rows)
    rows = ["| Zone | Trust | Components | Exposed interfaces |", "|---|---|---|---|"]
    for z in m["zones"]:
        ex = [e["id"] for e in m["external"] if e["zone"] == z["id"]]
        rows.append(
            f"| {z['id']} {z['name']} | {cell(z['trust'])} "
            f"| {', '.join(c + ' ' + comps[c]['name'] for c in z['components'])} | {', '.join(ex) or '—'} |"
        )
    t["secarch-zones"] = "\n".join(rows)
    rows = ["| Interface | From → to | Zones | Controls | Note |", "|---|---|---|---|---|"]
    for x in m["conduits"]:
        f = k["interfaces"][x["interface"]]
        a, b = f["link"]
        via = f", through {x['via']} {zones[x['via']]['name']}" if x.get("via") else ""
        rows.append(
            f"| {x['interface']} | {comps[a]['name']} → {comps[b]['name']} | {zof[a]} → {zof[b]}{via} "
            f"| {', '.join(x['controls'])} | {cell(x.get('note', '—'))} |"
        )
    t["secarch-conduits"] = "\n".join(rows)
    rows = [
        "| ID | Exposed interface | Zone | Attack vector | Threats | Controls | Decision |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in m["external"]:
        th = [f"{ts}{' (claim)' if ts in k['claimed'] else ''}" for ts in e["threats"]]
        rows.append(
            f"| {e['id']} | {cell(e['name'])} | {e['zone']} | {e['vector']} | {', '.join(th) or 'None in the TARA'} "
            f"| {', '.join(e['controls']) or '—'} | {decided(e, k)} |"
        )
    t["secarch-external"] = "\n".join(rows)
    t["secarch-attack-cards"] = (
        "![Figure 4-1: one card per interface exposed outside the vehicle, EX-01 to EX-07. Each shows the four "
        "trust zones in a row, the attacker at the zone the interface opens into with its attack vector, the "
        "attack path toward the safety zone and where the controls stand on it, then the threats of the TARA "
        "that use the interface and its controls with their highest CAL. EX-07 has no threat because none is "
        f"fitted (DQ-037 A). The same data are in the table above.](secarch/{FIG2.name})\n\n"
        "*Figure 4-1. Where an attacker can reach the item, and what stops them. Drawn by "
        "[`secarch/secarch.py`](secarch/secarch.py); CI fails if it is stale. Every technical cybersecurity "
        f"requirement with its trace is in [`secarch/{CSV.name}`](secarch/{CSV.name}).*"
    )
    item = [i for i, r in k["csrs"].items() if r["scope"] == "item"]
    cals = [cal(r, k) for r in m["tcsrs"]]
    top = max((c for c in cals if c), key=cybersecurity.CALS.index)
    t["secarch-summary"] = (
        f"{len(m['tcsrs'])} technical cybersecurity requirements refine the {len(item)} item-level requirements "
        f"of WP-C-10 onto {len({r['component'] for r in m['tcsrs']})} components; "
        f"{sum(c == top for c in cals)} of them at {top}. The {len(k['components'])} components sit in "
        f"{len(m['zones'])} trust zones; {len(m['conduits'])} interfaces cross a zone and each is a conduit with its "
        f"controls. {len(m['external'])} interfaces are exposed outside the vehicle, and every threat of the TARA "
        f"reaches the item through one of them."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/secarch/secarch.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-07 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .z1 { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; stroke-dasharray:5 4; }
svg .z2 { fill:var(--ambsoft); stroke:var(--amb); stroke-width:1.4; }
svg .z3 { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.8; }
svg .z4 { fill:var(--card); stroke:var(--ink2); stroke-width:1.4; }
svg .cd { stroke:var(--ink); stroke-width:1.6; fill:none; }
svg .tn { stroke:var(--ink); stroke-width:1.6; fill:none; stroke-dasharray:6 4; }
svg .hd { fill:var(--ink); }
svg .ex { fill:var(--bad); }
svg .w { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
"""
CLS = {"SZ-1": "z1", "SZ-2": "z2", "SZ-3": "z3", "SZ-4": "z4"}


def figure(m: dict, k: dict) -> str:
    comps = k["components"]
    zof = zone_of(m)
    zones = {z["id"]: z for z in m["zones"]}
    body = [
        fk.text(24, 32, "Trust zones and what crosses them", "h"),
        fk.text(24, 54, "WP-S-07 §3: components by zone, the conduits between zones,", "t"),
        fk.text(24, 71, "and the interfaces each zone exposes outside the vehicle", "t"),
    ]
    for z in m["zones"]:
        x, y, w, h = z["box"]
        body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=8, class_=CLS[z["id"]]))
        body.append(fk.text(x + 10, y + 20, f"{z['name']}", "tb"))
        ex = [e for e in m["external"] if e["zone"] == z["id"]]
        for n, e in enumerate(ex):
            ex_x, ex_y = x + 10 + (n % 3) * 40, y + 30 + (n // 3) * 20
            body.append(fk.el("rect", None, x=ex_x, y=ex_y, width=36, height=16, rx=3, class_="ex"))
            body.append(fk.text(ex_x + 18, ex_y + 12, e["id"], "w", "middle"))
        ly = y + 30 + 20 * -(-len(ex) // 3) + 16
        for c in z["components"]:
            for s in fk.wrap(comps[c]["name"], w - 20, "s")[:2]:
                body.append(fk.text(x + 10, ly, s, "s"))
                ly += 14
            ly += 3
    # One arrow per pair of zones, at its own height near the bottom of the boxes.
    pairs: dict[tuple[str, str], list[str]] = {}
    for x in m["conduits"]:
        a, b = (zof[c] for c in k["interfaces"][x["interface"]]["link"])
        key = tuple(sorted((a, b)))
        pairs.setdefault(key, []).append(x["interface"])
    tunnel = {x["interface"] for x in m["conduits"] if x.get("via")}
    for n, (key, ifs) in enumerate(sorted(pairs.items())):
        a, b = zones[key[0]]["box"], zones[key[1]]["box"]
        ay = a[1] + a[3] - 20 - 20 * n
        x1, x2 = a[0] + a[2], b[0]
        cls = "tn" if set(ifs) <= tunnel else "cd"
        body.append(fk.el("path", None, d=f"M{x1} {ay} L{x2 - 7} {ay}", class_=cls))
        body.append(
            fk.el(
                "path", None, d=f"M{x2} {ay} L{x2 - 8} {ay - 4} L{x2 - 8} {ay + 4} Z", class_="hd"
            )
        )
        span_ = ifs[0] if len(ifs) == 1 else f"{ifs[0]} to {ifs[-1]}"
        body.append(fk.text(x2 + 6, ay + 4, span_, "s"))
        if any(zof[k["interfaces"][i]["link"][0]] == key[1] for i in ifs):
            body.append(fk.text(x2 + 6, ay + 18, "both ways", "s"))
    y = max(z["box"][1] + z["box"][3] for z in m["zones"]) + 30
    body.append(fk.el("rect", None, x=24, y=y - 12, width=36, height=16, rx=3, class_="ex"))
    body.append(fk.text(68, y + 1, "Interface exposed outside the vehicle (§4)", "s"))
    y += 20
    body.append(fk.el("path", None, d=f"M24 {y - 4} L60 {y - 4}", class_="tn"))
    body.append(fk.text(68, y + 1, "Conduit tunnelled through another zone", "s"))
    y += 16
    desc = (
        "Trust zones: "
        + "; ".join(
            f"{z['name']} with {', '.join(comps[c]['name'] for c in z['components'])}, exposing "
            f"{', '.join(e['id'] for e in m['external'] if e['zone'] == z['id']) or 'nothing'}"
            for z in m["zones"]
        )
        + ". Conduits: "
        + "; ".join(
            f"{', '.join(v)} between {zones[a]['name']} and {zones[b]['name']}"
            for (a, b), v in sorted(pairs.items())
        )
    )
    return fk.svg(
        W,
        int(y + 6),
        "WP-S-07 Figure 3-1: trust zones",
        desc + ".",
        body,
        EXTRA,
    )


def control_cal(c: str, m: dict, k: dict) -> str | None:
    """The CAL a control carries: a technical requirement's, or the highest of a requirement's goals."""
    tc = {r["id"]: r for r in m["tcsrs"]}
    if c in tc:
        return cal(tc[c], k)
    if c in k["csrs"]:
        cals = [
            cybersecurity.cal(k["cyber"], k["cyber_known"], k["goals"][g])
            for g in k["csrs"][c]["goals"]
        ]
        cals = [x for x in cals if x]
        return max(cals, key=cybersecurity.CALS.index) if cals else None
    return None


def card_data(m: dict, k: dict) -> tuple[list[dict], list[dict]]:
    """The exposed interfaces with their threats and controls worked out, and the zones in drawing order."""
    zones = sorted(m["zones"], key=lambda z: z["box"][0])
    out = []
    for e in m["external"]:
        cals = [x for x in (control_cal(c, m, k) for c in e["controls"]) if x]
        out.append(
            {
                "id": e["id"],
                "name": e["name"],
                "zone": e["zone"],
                "vector": e["vector"],
                "threats": [
                    {"id": ts, "text": k["threats"][ts]["text"], "claim": ts in k["claimed"]}
                    for ts in e["threats"]
                ],
                "controls": e["controls"],
                "cal": max(cals, key=cybersecurity.CALS.index) if cals else "",
                "decision": decided(e, k),
            }
        )
    return out, [{"id": z["id"], "name": z["name"]} for z in zones]


def requirements_csv(m: dict, k: dict) -> str:
    """Every technical cybersecurity requirement with its placement, CAL and trace."""
    import csv
    import io

    import yaml

    its = yaml.safe_load((HERE.parent / "integ" / "integ.yaml").read_text(encoding="utf-8"))[
        "cases"
    ]
    comps = k["components"]
    zof = zone_of(m)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(
        [
            "ID",
            "Technical cybersecurity requirement",
            "CAL",
            "Component",
            "Zone",
            "Allocation",
            "Refines (WP-C-10)",
            "Cybersecurity goals",
            "Guards exposed interfaces",
            "Guards conduits",
            "Verification",
            "Integration test cases (WP-S-08)",
        ]
    )
    for r in sorted(m["tcsrs"], key=lambda r: r["id"]):
        c = r["component"]
        w.writerow(
            [
                r["id"],
                r["text"],
                cal(r, k) or "—",
                f"{c} {comps[c]['name']}",
                zof[c],
                r["alloc"],
                r["csr"],
                ", ".join(k["csrs"][r["csr"]]["goals"]),
                ", ".join(e["id"] for e in m["external"] if r["id"] in e["controls"]) or "—",
                ", ".join(x["interface"] for x in m["conduits"] if r["id"] in x["controls"]) or "—",
                r["verify"],
                ", ".join(x["id"] for x in its if r["id"] in x["covers"]) or "—",
            ]
        )
    return buf.getvalue()


def here(md: str) -> str:
    """Text of WP-S-07 with its relative links rewritten to work from this folder."""
    md = md.replace("](secarch/", "](")
    return re.sub(r"\]\((?!https?:|#|fig-|requirements\.csv|secarch\.|README)", "](../", md)


def readme(t: dict[str, str], doc: str) -> str:
    """The folder page: the whole cybersecurity requirements and architecture on one page."""

    def part(heading: str) -> str:
        return here(fk.section(doc, heading).strip())

    files = [
        "| File | What it holds |",
        "|---|---|",
        f"| [`{CSV.name}`]({CSV.name}) | Every technical cybersecurity requirement with its CAL, component, zone, allocation, the requirement and goals it refines, the exposed interfaces and conduits it guards, and the integration test cases that cover it |",
        f"| [`{FIG.name}`]({FIG.name}) | Figure 3-1, the trust zones, conduits and exposed interfaces |",
        f"| [`{FIG2.name}`]({FIG2.name}) | Figure 4-1, where an attacker can reach the item and what stops them |",
        "| [`secarch.yaml`](secarch.yaml) | Trust zones, conduits, exposed interfaces and the technical cybersecurity requirements |",
        "| [`secarch.py`](secarch.py), [`acards.py`](acards.py) | The generator: checks the model against the cybersecurity concept, the TARA, the architecture and the hardware-software interface, and writes WP-S-07's tables and everything here |",
    ]
    lines = [
        "<!-- Generated by assurance/03-system/secarch/secarch.py; do not edit by hand. -->",
        "",
        "# Cybersecurity requirements and architecture",
        "",
        "The whole of [WP-S-07](../WP-S-07-cybersecurity-requirements-architecture.md) on one page: the "
        "technical cybersecurity requirements refined from the cybersecurity concept, the trust zones the "
        "components of the [technical safety concept](../tsc/README.md) sit in, the conduits over the "
        "[hardware-software interface](../hsi/README.md) that cross them, and every interface through which "
        "the item can be reached from outside the vehicle. Everything here is generated by `secarch.py` from "
        "`secarch.yaml`; CI fails if it is stale. Everything is a draft by Claude (I0) until it is reviewed.",
        "",
        t["secarch-summary"],
        "",
        "1. [What this covers](#1-what-this-covers)",
        "2. [Cybersecurity requirements](#2-cybersecurity-requirements)",
        "3. [Trust zones and conduits](#3-trust-zones-and-conduits)",
        "4. [Interfaces exposed outside the vehicle](#4-interfaces-exposed-outside-the-vehicle)",
        "5. [Files in this folder](#5-files-in-this-folder)",
        "",
        "## 1. What this covers",
        "",
        re.sub(
            r"<!-- BEGIN GENERATED: secarch-summary .*?END GENERATED: secarch-summary -->\n\n",
            "",
            part("## 1. Purpose"),
            flags=re.S,
        ),
        "",
        "## 2. Cybersecurity requirements",
        "",
        f"Every technical requirement, with what it guards and the tests that cover it, is in [`{CSV.name}`]"
        f"({CSV.name}), which GitHub shows as a table that can be searched.",
        "",
        part("## 2. Cybersecurity requirements"),
        "",
        "## 3. Trust zones and conduits",
        "",
        part("## 3. Security architecture and controls"),
        "",
        "## 4. Interfaces exposed outside the vehicle",
        "",
        part("## 4. Interfaces exposed outside the vehicle"),
        "",
        "## 5. Files in this folder",
        "",
        *files,
        "",
    ]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("secarch.yaml: " + "; ".join(errs))
    t = tables(m, k)
    doc = fill(DOC.read_text(encoding="utf-8"), t)
    exposed, zones = card_data(m, k)
    return {
        DOC: doc,
        FIG: figure(m, k),
        FIG2: acards.sheet(exposed, zones),
        CSV: requirements_csv(m, k),
        README: terms.close(readme(t, doc), README),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
