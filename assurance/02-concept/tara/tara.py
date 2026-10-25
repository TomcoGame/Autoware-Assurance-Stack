#!/usr/bin/env python3
"""The threat analysis and risk assessment of WP-C-09, generated from tara.yaml.

Writes the generated tables of WP-C-09 (assets, damage scenarios, threat scenarios, treatment and
proposed controls). This repository is public, so tara.yaml is the public tier of the TARA: attack
paths, attack feasibility ratings, risk values and attack vectors are restricted (WP-M-09 §4) and
kept outside it. The treatment of each threat is recorded, not computed.

The model is refused when:
- it carries a restricted field (an attack path, attack potential factors, a feasibility rating,
  a risk value or an attack vector);
- an identifier is malformed or repeated;
- an asset has a property other than C, I or A, or no threat scenario;
- a damage scenario has an impact rating outside the scale, or names a HARA hazard that does not
  exist, or no threat scenario leads to it;
- a threat scenario names an asset or damage scenario that does not exist, or has a treatment
  other than reduce or retain;
- a threat scenario to reduce names no control, or names a control that does not exist
  (cybersecurity controls here, or requirements of the STPA, the functional safety concept, the
  fallback concept and the functional modifications);
- a control here is used by no threat scenario.

    python3 tara.py            # write WP-C-09's generated tables
    python3 tara.py --check    # fail if they are stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in ("01-management/figures", "01-management/decisions", "08-analyses/stpa"):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import stpa  # noqa: E402

MODEL = HERE / "tara.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-09-tara.md"
CATEGORIES = ("safety", "financial", "operational", "privacy")
# Fields that must never reach the public repository (WP-M-09 §4).
RESTRICTED = {"path", "factors", "feasibility", "potential", "risk", "vector", "vectors", "matrix"}


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    s = stpa.load()
    k = stpa.known()
    return {
        "hara": k["hara"],
        "refs": k["measures"] | {r["id"] for r in s["requirements"]},
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def impact(m: dict, t: dict) -> str:
    """The highest impact, over every category, of the damage scenarios the threat leads to."""
    scale = m["method"]["impacts"]
    ds = {d["id"]: d for d in m["damage"]}
    return max((ds[d]["impact"][c] for d in t["damage"] for c in CATEGORIES), key=scale.index)


def treatment(m: dict, t: dict) -> str:
    return t["treatment"].capitalize()


def restricted(x, where: str = "") -> list[str]:
    """Restricted keys anywhere in the model, by where they sit."""
    if isinstance(x, list):
        return [e for i, v in enumerate(x) for e in restricted(v, f"{where}[{i}]")]
    if not isinstance(x, dict):
        return []
    here = x.get("id", where)
    out = [
        f"{here}: '{key}' is restricted (WP-M-09 §4); keep it out of the public repository"
        for key in x
        if key in RESTRICTED
    ]
    return out + [
        e for key, v in x.items() for e in restricted(v, f"{here}.{key}" if here else key)
    ]


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = restricted(m)
    meth = m.get("method", {})
    scale = meth.get("impacts", [])
    seen: set[str] = set()

    def new(i: str, pat: str, keys: set[str], x: dict) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        if set(x) - keys:
            errs.append(f"{i}: unexpected keys {sorted(set(x) - keys)} (quote a text with commas)")

    threats = m.get("threats", [])
    for a in m.get("assets", []):
        new(a["id"], r"A-\d\d", {"id", "name", "properties"}, a)
        if not a.get("properties") or set(a["properties"]) - {"C", "I", "A"}:
            errs.append(f"{a['id']}: properties must be among C, I, A")
        if not any(a["id"] in t.get("assets", []) for t in threats):
            errs.append(f"{a['id']}: no threat scenario names it")
    for d in m.get("damage", []):
        new(d["id"], r"DS-\d\d", {"id", "text", "impact", "hara"}, d)
        for c in CATEGORIES:
            if (d.get("impact") or {}).get(c) not in scale:
                errs.append(f"{d['id']}: {c} impact must be one of {', '.join(scale)}")
        for h in d.get("hara") or []:
            if h not in k["hara"]:
                errs.append(f"{d['id']}: HARA hazard {h} does not exist")
        if not any(d["id"] in t.get("damage", []) for t in threats):
            errs.append(f"{d['id']}: no threat scenario leads to it")
    assets = {a["id"] for a in m.get("assets", [])}
    damage = {d["id"] for d in m.get("damage", [])}
    controls = {c["id"] for c in m.get("controls", [])}
    used: set[str] = set()
    for t in threats:
        i = t["id"]
        new(
            i,
            r"TS-\d\d",
            {"id", "text", "stride", "assets", "damage", "controls", "treatment"},
            t,
        )
        for a in t.get("assets") or []:
            if a not in assets:
                errs.append(f"{i}: asset {a} does not exist")
        for d in t.get("damage") or []:
            if d not in damage:
                errs.append(f"{i}: damage scenario {d} does not exist")
        if t.get("treatment") not in ("reduce", "retain"):
            errs.append(f"{i}: treatment must be reduce or retain")
        for c in t.get("controls") or []:
            if c not in controls | k["refs"]:
                errs.append(f"{i}: control {c} does not exist")
            used.add(c)
    for c in m.get("controls", []):
        new(c["id"], r"CR-\d\d", {"id", "text"}, c)
        if c["id"] not in used:
            errs.append(f"{c['id']}: no threat scenario uses it")
    if not errs:
        for t in threats:
            if t["treatment"] == "reduce" and not t.get("controls"):
                errs.append(f"{t['id']}: its risk must be reduced but it names no control")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict) -> dict[str, str]:
    t = {}
    rows = ["| ID | Asset | Properties | Threat scenarios |", "|---|---|---|---|"]
    for a in m["assets"]:
        ts = [x["id"] for x in m["threats"] if a["id"] in x["assets"]]
        rows.append(
            f"| {a['id']} | {cell(a['name'])} | {', '.join(a['properties'])} | {', '.join(ts)} |"
        )
    t["tara-assets"] = "\n".join(rows)
    rows = [
        "| ID | Damage scenario | Safety | Financial | Operational | Privacy | HARA hazards |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in m["damage"]:
        im = d["impact"]
        rows.append(
            f"| {d['id']} | {cell(d['text'])} | "
            + " | ".join(im[c] for c in CATEGORIES)
            + f" | {', '.join(d['hara']) or '—'} |"
        )
    t["tara-damage"] = "\n".join(rows)
    rows = [
        "| ID | Threat scenario | STRIDE | Assets | Damage | Impact |",
        "|---|---|---|---|---|---|",
    ]
    for x in m["threats"]:
        rows.append(
            f"| {x['id']} | {cell(x['text'])} | {x['stride']} | {', '.join(x['assets'])} | {', '.join(x['damage'])} | {impact(m, x)} |"
        )
    t["tara-threats"] = "\n".join(rows)
    ctl = {c["id"]: c["text"] for c in m["controls"]}
    rows = ["| ID | Treatment | Controls |", "|---|---|---|"]
    for x in sorted(m["threats"], key=lambda x: (x["treatment"] != "reduce", x["id"])):
        rows.append(f"| {x['id']} | {treatment(m, x)} | {', '.join(x['controls']) or '—'} |")
    t["tara-risk"] = "\n".join(rows)
    rows = ["| ID | Proposed cybersecurity control | For |", "|---|---|---|"]
    for c, text in ctl.items():
        by = [x["id"] for x in m["threats"] if c in x["controls"]]
        rows.append(f"| {c} | {cell(text)} | {', '.join(by)} |")
    t["tara-controls"] = "\n".join(rows)
    reduce = sum(1 for x in m["threats"] if x["treatment"] == "reduce")
    t["tara-summary"] = (
        f"{len(m['assets'])} assets, {len(m['damage'])} damage scenarios and {len(m['threats'])} threat scenarios. "
        f"{reduce} are reduced and {len(m['threats']) - reduce} retained (DQ-027 A); "
        f"{len(m['controls'])} cybersecurity controls are proposed for WP-C-10. "
        f"Attack paths, feasibility ratings and risk values are restricted and not published here."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/tara/tara.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-09 needs exactly one generated block {name}")
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
        raise fk.FigureError("tara.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m))}


if __name__ == "__main__":
    fk.run(build, __doc__)
