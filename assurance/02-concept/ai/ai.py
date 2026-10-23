#!/usr/bin/env python3
"""The AI system definition and AI safety requirements of WP-C-11, generated from ai.yaml.

Writes the generated tables of WP-C-11 (AI systems, their input space, AI safety requirements and
their allocation) and Figure 4-1 (which kinds of requirement each AI system has).

The model is refused when:
- an identifier is malformed or repeated, or a kind or allocation is unknown;
- an AI system names a function that is not in WP-C-01 §3, an element of the functional safety
  concept that does not exist, or one with a derived ASIL other than QM (no AI system may carry a
  rated requirement in this architecture, DQ-002 A);
- an AI system names a SOTIF hazard, insufficiency, requirement or input dimension that does not
  exist;
- an ML function of WP-C-01 §3, or an insufficiency of WP-C-06 with AI error causes, has no AI
  system;
- an AI system lacks a requirement of any kind, or a requirement names an AI system that does not
  exist.

    python3 ai.py            # write WP-C-11's generated tables and Figure 4-1
    python3 ai.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "02-concept/fsc",
    "02-concept/triggering",
    "02-concept/cybersecurity",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import cybersecurity  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import triggering  # noqa: E402

MODEL = HERE / "ai.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-11-ai-system-definition-and-safety-requirements.md"
ODD = ASSURANCE / "02-concept" / "WP-C-02-odd-and-intended-functionality.md"
FIG = HERE / "fig-c11-4-1-requirements.svg"
KINDS = {
    "performance": "Performance",
    "robustness": "Robustness",
    "uncertainty": "Uncertainty",
    "data": "Data",
    "monitoring": "Monitoring",
}
ALLOCATIONS = ("model", "data", "architecture", "operation")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dimensions() -> list[str]:
    """The input space dimensions of WP-C-02 §6."""
    md = ODD.read_text(encoding="utf-8")
    _, rows = fk.table(fk.section(md, "## 6. Input space of the AI components"), "Dimension")
    return [fk.plain(r[0]) for r in rows]


def known() -> dict:
    f = fsc.load()
    t = triggering.load()
    tk = triggering.known()
    c = cybersecurity.known()
    return {
        "functions": tk["functions"],
        "ml": tk["ml"],
        "elements": fsc.element_asil(f),
        "hazards": set(tk["hazards"]),
        "fis": {x["id"]: x for x in t["insufficiencies"]},
        "refs": c["refs"] | {r["id"] for r in cybersecurity.load()["requirements"]},
        "dims": dimensions(),
    }


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    systems = {s["id"]: s for s in m.get("systems", [])}
    for s in m.get("systems", []):
        i = s["id"]
        new(i, r"AIS-\d\d")
        for key in ("name", "component", "task", "consumers"):
            if not s.get(key):
                errs.append(f"{i}: missing {key}")
        if s.get("function") not in k["functions"]:
            errs.append(f"{i}: function {s.get('function')} is not in WP-C-01 §3")
        el = s.get("element")
        if el not in k["elements"]:
            errs.append(f"{i}: element {el} does not exist")
        elif k["elements"][el] != "QM":
            errs.append(
                f"{i}: on {el}, which is ASIL {k['elements'][el]}; no AI system may be on a rated element"
            )
        for h in s.get("hazards") or []:
            if h not in k["hazards"]:
                errs.append(f"{i}: SOTIF hazard {h} does not exist")
        for f in s.get("insufficiencies") or []:
            if f not in k["fis"]:
                errs.append(f"{i}: insufficiency {f} does not exist")
        for r in s.get("bounded_by") or []:
            if r not in k["refs"]:
                errs.append(f"{i}: {r} does not exist")
        for d in s.get("input") or []:
            if d not in k["dims"]:
                errs.append(f"{i}: input dimension '{d}' is not in WP-C-02 §6")
        kinds = {r["kind"] for r in m.get("requirements", []) if i in r.get("systems", [])}
        for kind in KINDS:
            if kind not in kinds:
                errs.append(f"{i}: no {kind} requirement")
    for fn in sorted(k["ml"]):
        if not any(s.get("function") == fn for s in m.get("systems", [])):
            errs.append(f"{fn}: an ML function of WP-C-01 §3 with no AI system")
    for fid, f in k["fis"].items():
        if f.get("ai") and not any(
            fid in s.get("insufficiencies", []) for s in m.get("systems", [])
        ):
            errs.append(f"{fid}: has AI error causes but no AI system")
    for r in m.get("requirements", []):
        i = r["id"]
        new(i, r"AISR-\d\d")
        if r.get("kind") not in KINDS:
            errs.append(f"{i}: kind must be one of {', '.join(KINDS)}")
        if r.get("allocated") not in ALLOCATIONS:
            errs.append(f"{i}: allocated must be one of {', '.join(ALLOCATIONS)}")
        for s in r.get("systems") or []:
            if s not in systems:
                errs.append(f"{i}: AI system {s} does not exist")
        for key in ("text", "target"):
            if not r.get(key):
                errs.append(f"{i}: missing {key}")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    t = {}
    rows = [
        "| ID | AI system | Component | Function | Element | Task | Output used by | SOTIF hazards | Bounded by |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in m["systems"]:
        rows.append(
            f"| {s['id']} | {cell(s['name'])} | {cell(s['component'])} | {s['function']} | {s['element']} ({k['elements'][s['element']]}) "
            f"| {cell(s['task'])} | {cell(s['consumers'])} | {', '.join(s['hazards'])} | {', '.join(s['bounded_by'])} |"
        )
    t["ai-systems"] = "\n".join(rows)
    rows = ["| AI system | " + " | ".join(k["dims"]) + " |", "|---" * (len(k["dims"]) + 1) + "|"]
    for s in m["systems"]:
        rows.append(
            f"| {s['id']} {cell(s['name'])} | "
            + " | ".join("●" if d in s["input"] else "" for d in k["dims"])
            + " |"
        )
    t["ai-input"] = "\n".join(rows)
    rows = ["| ID | Kind | AI systems | Requirement | Target set in |", "|---|---|---|---|---|"]
    for r in m["requirements"]:
        rows.append(
            f"| {r['id']} | {KINDS[r['kind']]} | {', '.join(r['systems'])} | {cell(r['text'])} | {cell(r['target'])} |"
        )
    t["ai-requirements"] = "\n".join(rows)
    rows = ["| Allocated to | Requirements |", "|---|---|"]
    for a in ALLOCATIONS:
        rows.append(
            f"| {a.capitalize()} | {', '.join(r['id'] for r in m['requirements'] if r['allocated'] == a) or '—'} |"
        )
    t["ai-allocation"] = "\n".join(rows)
    new = sum(1 for s in m["systems"] if "pinned" not in s["component"])
    t["ai-summary"] = (
        f"{len(m['systems'])} AI systems ({len(m['systems']) - new} in the pinned Autoware, {new} new), all on the "
        f"Autoware computer, which is QM; none is on a rated element. {len(m['requirements'])} AI safety requirements, "
        f"each AI system covered for performance, robustness, uncertainty, data and monitoring. No target value is "
        f"set here; each requirement names where it is derived."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/ai/ai.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-11 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .c1 { fill:var(--acc); fill-opacity:.2; } svg .c2 { fill:var(--acc); fill-opacity:.45; }
svg .c3 { fill:var(--acc); fill-opacity:.7; }
svg .n { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .col { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
"""


def figure(m: dict, k: dict) -> str:
    x0, top, rh = 210, 112, 34
    cw = (W - 24 - x0) / len(KINDS)
    body = [
        fk.text(24, 32, "AI safety requirements by system", "h"),
        fk.text(24, 54, "WP-C-11 §4: how many requirements of each kind each AI system has;", "t"),
        fk.text(24, 71, "every cell must be filled", "t"),
    ]
    for j, kind in enumerate(KINDS.values()):
        body.append(fk.text(x0 + cw * j + cw / 2, top - 12, kind, "col", "middle"))
    for i, s in enumerate(m["systems"]):
        y = top + i * rh
        body.append(fk.text(24, y + 15, s["id"], "tb"))
        body.append(fk.text(24, y + 29, fk.fit(s["name"], x0 - 34, "s"), "s"))
        for j, kind in enumerate(KINDS):
            n = sum(1 for r in m["requirements"] if r["kind"] == kind and s["id"] in r["systems"])
            x = x0 + cw * j
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(x + 2),
                    y=y + 3,
                    width=fk.num(cw - 4),
                    height=rh - 6,
                    rx=4,
                    class_=f"c{min(n, 3)}" if n else "card",
                )
            )
            if n:
                body.append(fk.text(x + cw / 2, y + rh / 2 + 4, str(n), "n", "middle"))
    y = top + len(m["systems"]) * rh + 26
    body.append(
        fk.text(
            24,
            y,
            "All five AI systems run on the Autoware computer (QM); the safety channel uses none.",
            "s",
        )
    )
    y += 16
    desc = "AI safety requirements per system and kind: " + "; ".join(
        f"{s['id']} "
        + ", ".join(
            f"{KINDS[kd]} {sum(1 for r in m['requirements'] if r['kind'] == kd and s['id'] in r['systems'])}"
            for kd in KINDS
        )
        for s in m["systems"]
    )
    return fk.svg(
        W, int(y), "WP-C-11 Figure 4-1: AI safety requirements by system", desc + ".", body, EXTRA
    )


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("ai.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
