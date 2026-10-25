#!/usr/bin/env python3
"""The technical cybersecurity requirements of WP-S-07, generated from secarch.yaml.

Writes the generated tables of WP-S-07 (technical cybersecurity requirements with their CAL, and
the requirements on the operating environment). This repository is public, so secarch.yaml is the
public tier: the text and verification of each technical requirement, the trust zones, the
conduits, the interfaces exposed outside the vehicle and their attack vectors are restricted
(WP-M-09 §4) and kept outside it. A technical requirement's CAL is the highest CAL of the goals of
the WP-C-10 requirement it refines.

The model is refused when:
- it carries a restricted field (see tara.RESTRICTED, and text, verify, zones, conduits, external);
- an identifier is malformed or repeated, or a technical requirement does not carry the number of
  the requirement it refines;
- a component named does not exist, or an allocation is unknown;
- an item-level requirement of WP-C-10 is refined by no technical requirement, or a technical
  requirement refines one of the operating environment.

    python3 secarch.py            # write WP-S-07's generated tables
    python3 secarch.py --check    # fail if they are stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "02-concept/tara",
    "02-concept/cybersecurity",
    "03-system/tsc",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import cybersecurity  # noqa: E402
import figkit as fk  # noqa: E402
import tara  # noqa: E402
import tsc  # noqa: E402

MODEL = HERE / "secarch.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-07-cybersecurity-requirements-architecture.md"
ALLOC = ("software", "hardware", "both")
# Restricted here as well as the fields every cybersecurity model refuses (WP-M-09 §4).
RESTRICTED = {"text", "verify", "zones", "conduits", "external", "zone"}


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    cm = cybersecurity.load()
    t = tsc.load()
    return {
        "csrs": {r["id"]: r for r in cm["requirements"]},
        "goals": {g["id"]: g for g in cm["goals"]},
        "components": {c["id"]: c for c in t["components"]},
    }


def cal(r: dict, k: dict) -> str | None:
    """The CAL of a technical requirement: the highest of the goals its WP-C-10 requirement serves."""
    cals = [k["goals"][g]["cal"] for g in k["csrs"][r["csr"]]["goals"]]
    return max(cals, key=cybersecurity.CALS.index) if cals else None


def check(m: dict, k: dict) -> list[str]:
    errs = tara.restricted(m)
    errs += [
        f"{key}: restricted (WP-M-09 §4); keep it out of the public repository"
        for key in m
        if key in RESTRICTED
    ]
    seen: set[str] = set()
    refined: set[str] = set()
    for r in m.get("tcsrs", []):
        i = r["id"]
        if not re.fullmatch(r"CSTR-\d\d\.\d\d", i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        for key in set(r) & RESTRICTED:
            errs.append(f"{i}: '{key}' is restricted (WP-M-09 §4)")
        if set(r) - RESTRICTED - {"id", "csr", "component", "alloc"}:
            errs.append(
                f"{i}: unexpected keys {sorted(set(r) - {'id', 'csr', 'component', 'alloc'})}"
            )
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
    for i, r in k["csrs"].items():
        if r["scope"] == "item" and i not in refined:
            errs.append(f"{i}: item-level requirement refined by no technical requirement")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    comps = k["components"]
    t = {}
    rows = [
        "| ID | Refines | Component | Allocation | CAL |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(m["tcsrs"], key=lambda r: r["id"]):
        c = r["component"]
        rows.append(
            f"| {r['id']} | {r['csr']} | {c} {cell(comps[c]['name'])} | {r['alloc']} | {cal(r, k) or '—'} |"
        )
    t["secarch-requirements"] = "\n".join(rows)
    rows = ["| Requirement | Met by | Goals | Text |", "|---|---|---|---|"]
    for i, r in k["csrs"].items():
        if r["scope"] == "environment":
            rows.append(
                f"| {i} | {cell(r['element'])} | {', '.join(r['goals'])} | {cell(r['text'])} |"
            )
    t["secarch-environment"] = "\n".join(rows)
    item = [i for i, r in k["csrs"].items() if r["scope"] == "item"]
    cals = [cal(r, k) for r in m["tcsrs"]]
    top = max((c for c in cals if c), key=cybersecurity.CALS.index)
    t["secarch-summary"] = (
        f"{len(m['tcsrs'])} technical cybersecurity requirements refine the {len(item)} item-level requirements "
        f"of WP-C-10 onto {len({r['component'] for r in m['tcsrs']})} components; "
        f"{sum(c == top for c in cals)} of them at {top}. Their text and verification, the trust zones, the "
        f"conduits and the interfaces exposed outside the vehicle are restricted and not published here."
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


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("secarch.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k))}


if __name__ == "__main__":
    fk.run(build, __doc__)
