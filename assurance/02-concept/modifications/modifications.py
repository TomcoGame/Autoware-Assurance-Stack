#!/usr/bin/env python3
"""The functional modifications of WP-C-07, generated from modifications.yaml.

Writes the generated tables of WP-C-07 (modifications, the hazards they address, residual risk
per hazard) and Figure 2-1 (for each SOTIF hazard, the modifications that address it and whether
each is already in the concept, new work, or waiting on a decision). Which hazards a modification
addresses is computed through the insufficiencies of WP-C-06, not typed.

The model is refused when:
- an identifier is malformed or repeated, or a type is unknown;
- a modification addresses an insufficiency that is not in ../triggering/triggering.yaml, or
  names a requirement, monitor or assumption that does not exist, or is pending on a decision
  that is no longer open;
- an insufficiency of WP-C-06 is addressed by no modification;
- an insufficiency of the specification is addressed only by data or architecture, with no
  change to the function, its use or its operation.

    python3 modifications.py            # write WP-C-07's generated tables and Figure 2-1
    python3 modifications.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "01-management" / "decisions"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "fsc"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "triggering"))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import triggering  # noqa: E402

MODEL = HERE / "modifications.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-07-sotif-functional-modifications.md"
FIG = HERE / "fig-c07-2-1-modifications.svg"
TYPES = {
    "function": "Function",
    "odd": "ODD and routing",
    "architecture": "Architecture",
    "data": "Data",
    "operations": "Operations",
}
SPEC_CHANGES = {"function", "odd", "operations"}
STATES = {
    "concept": "Required by the concept",
    "new": "New work",
    "pending": "Waits on a decision",
}
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    t = triggering.load()
    k = triggering.known()
    return {
        "fis": {f["id"]: f for f in t["insufficiencies"]},
        "hazards": k["hazards"],
        "refs": {f["id"] for f in fsc.load()["fsrs"]} | k["monitors"] | fsc.aous(),
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def state(fm: dict) -> str:
    if fm.get("pending"):
        return "pending"
    return "concept" if fm.get("concept") else "new"


def hazards(fm: dict, k: dict) -> list[str]:
    return sorted({h for f in fm["addresses"] if f in k["fis"] for h in k["fis"][f]["hazards"]})


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    fms = m.get("modifications", [])
    for fm in fms:
        i = str(fm.get("id"))
        if not re.fullmatch(r"FM-\d\d", i):
            errs.append(f"{i}: id must look like FM-01")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        for key in ("name", "change", "addresses", "by"):
            if not fm.get(key):
                errs.append(f"{i}: missing {key}")
        if fm.get("type") not in TYPES:
            errs.append(f"{i}: type must be one of {', '.join(TYPES)}")
        for f in fm.get("addresses") or []:
            if f not in k["fis"]:
                errs.append(f"{i}: insufficiency {f} is not in WP-C-06")
        for r in fm.get("concept") or []:
            if r not in k["refs"]:
                errs.append(f"{i}: {r} does not exist")
        p = fm.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )
    for f, d in k["fis"].items():
        by = [fm for fm in fms if f in (fm.get("addresses") or [])]
        if not by:
            errs.append(f"{f}: no modification addresses it")
        elif d["kind"] == "specification" and not any(fm.get("type") in SPEC_CHANGES for fm in by):
            errs.append(
                f"{f}: a specification insufficiency needs a change to the function, its use or its operation"
            )
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    fms = m["modifications"]
    t = {}
    rows = [
        "| ID | Modification | Type | Change | Carried by | Addresses | SOTIF hazards | Required by | State |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for fm in fms:
        st = STATES[state(fm)] + (f" ({fm['pending']})" if fm.get("pending") else "")
        rows.append(
            f"| {fm['id']} | {cell(fm['name'])} | {TYPES[fm['type']]} | {cell(fm['change'])} | {cell(fm['by'])} "
            f"| {', '.join(fm['addresses'])} | {', '.join(hazards(fm, k))} | {', '.join(fm['concept']) or '—'} | {st} |"
        )
    t["modifications-list"] = "\n".join(rows)
    rows = [
        "| SOTIF hazard | Insufficiencies (WP-C-06) | Modifications | Waiting on | Residual risk |",
        "|---|---|---|---|---|",
    ]
    for h in k["hazards"]:
        fis = [f for f, d in k["fis"].items() if h in d["hazards"]]
        by = [fm for fm in fms if h in hazards(fm, k)]
        wait = sorted({fm["pending"] for fm in by if fm.get("pending")})
        rows.append(
            f"| {h} | {', '.join(fis)} | {', '.join(fm['id'] for fm in by)} | {', '.join(wait) or '—'} "
            f"| To be evaluated against AC-02 (WP-V-03) |"
        )
    t["modifications-residual"] = "\n".join(rows)
    n = {s: sum(1 for fm in fms if state(fm) == s) for s in STATES}
    pend = sorted({fm["pending"] for fm in fms if fm.get("pending")})
    t["modifications-summary"] = (
        f"{len(fms)} functional modifications address the {len(k['fis'])} insufficiencies of WP-C-06: "
        f"{n['concept']} already required by the concept (a requirement, ODD monitor or assumption) though not "
        f"yet built, {n['new']} new work, "
        f"{n['pending']} waiting on {', '.join(pend) or 'no decision'}. Every insufficiency is addressed; "
        f"none is shown to be enough yet (WP-V-03)."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/modifications/modifications.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-07 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


# Required by the concept: green; new work: blue outline; waits on a decision: amber. Form differs too.
EXTRA = """svg .concept { fill:var(--ok); } svg .new { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.4; }
svg .pending { fill:var(--ambsoft); stroke:var(--amb); stroke-width:1.4; stroke-dasharray:4 2; }
svg .chip { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .chipi { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--bg); }
"""


def figure(m: dict, k: dict) -> str:
    fms = m["modifications"]
    x0, top, rh, cw, ch = 120, 100, 28, 52, 20
    body = [
        fk.text(24, 32, "What addresses each SOTIF hazard", "h"),
        fk.text(24, 54, "WP-C-07 §2: the functional modifications for each hazard, and how", "t"),
        fk.text(24, 71, "far each has got", "t"),
    ]
    for i, h in enumerate(k["hazards"]):
        y = top + i * rh
        body.append(fk.text(24, y + 15, h, "tb"))
        body.append(fk.text(76, y + 15, k["hazards"][h]["severity"], "s"))
        by = [fm for fm in fms if h in hazards(fm, k)]
        if x0 + len(by) * (cw + 6) > W - 16:
            raise fk.FigureError(f"Figure 2-1 has no room for {len(by)} modifications on {h}")
        for j, fm in enumerate(by):
            cx = x0 + j * (cw + 6)
            s = state(fm)
            body.append(fk.el("rect", None, x=cx, y=y + 1, width=cw, height=ch, rx=4, class_=s))
            body.append(
                fk.text(
                    cx + cw / 2, y + 15, fm["id"], "chipi" if s == "concept" else "chip", "middle"
                )
            )
    y = top + len(k["hazards"]) * rh + 26
    lx = 24
    for s, label in STATES.items():
        body.append(fk.el("rect", None, x=lx, y=y - 13, width=26, height=18, rx=4, class_=s))
        body.append(fk.text(lx + 34, y, label, "t"))
        lx += 34 + fk.width(label, "t") + 28
    y += 22
    desc = (
        "Functional modifications per SOTIF hazard: "
        + "; ".join(
            f"{h}: "
            + ", ".join(
                f"{fm['id']} ({STATES[state(fm)].lower()})" for fm in fms if h in hazards(fm, k)
            )
            for h in k["hazards"]
        )
        + "."
    )
    return fk.svg(W, int(y), "WP-C-07 Figure 2-1: modifications by hazard", desc, body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("modifications.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
