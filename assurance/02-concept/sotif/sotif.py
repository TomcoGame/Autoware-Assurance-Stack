#!/usr/bin/env python3
"""The SOTIF hazard identification of WP-C-05, generated from sotif.yaml.

Writes the generated tables of WP-C-05 (hazards, their evaluation, acceptance criteria) and
Figure 4-1 (which functions' insufficiencies lead to which hazards, the starting point of WP-C-06).
A hazard needs further evaluation unless it is rated S0 or C0 (ISO 21448:2022 §6); that is
computed, not typed.

The model is refused when:
- an identifier is malformed or repeated, or a rating is not one of S0–S3, C0–C3;
- a hazard names a function that is not in WP-C-01 §3, or a HARA hazard that is not in
  ../hara/hara.yaml;
- the insufficiency is not "specification" or "performance";
- a field the tables show is missing.

    python3 sotif.py            # write WP-C-05's generated tables and Figure 4-1
    python3 sotif.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "hara"))
import figkit as fk  # noqa: E402
import hara  # noqa: E402

MODEL = HERE / "sotif.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-05-sotif-hazard-identification.md"
ITEM = ASSURANCE / "02-concept" / "WP-C-01-item-definition.md"
FIG = HERE / "fig-c05-4-1-functions.svg"
KINDS = ("specification", "performance")
FIELDS = (
    "behaviour",
    "insufficiency",
    "functions",
    "harm",
    "severity",
    "controllability",
    "triggers",
    "measures",
)
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def functions() -> dict[str, str]:
    """{F-01: name} from WP-C-01 §3."""
    head, rows = fk.table(fk.section(ITEM.read_text(encoding="utf-8"), "## 3. The item"), "ID")
    return {fk.plain(r[0]): fk.plain(r[fk.col(head, "Function")]) for r in rows}


def hara_hazards() -> set[str]:
    return {h["id"] for h in hara.load()["hazards"]}


def further(h: dict) -> bool:
    """ISO 21448 §6: no further evaluation when no harm (S0) or controllable in general (C0)."""
    return h["severity"] != "S0" and h["controllability"] != "C0"


def check(m: dict, funcs: dict[str, str], hz: set[str]) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for h in m.get("hazards", []):
        i = str(h.get("id"))
        if not re.fullmatch(r"SH-\d\d", i):
            errs.append(f"{i}: id must look like SH-01")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        for k in FIELDS:
            if not h.get(k):
                errs.append(f"{i}: missing {k}")
        if h.get("insufficiency") not in KINDS:
            errs.append(f"{i}: insufficiency must be one of {', '.join(KINDS)}")
        if h.get("severity") not in hara.S_SCALE:
            errs.append(f"{i}: severity must be one of {', '.join(hara.S_SCALE)}")
        if h.get("controllability") not in hara.C_SCALE:
            errs.append(f"{i}: controllability must be one of {', '.join(hara.C_SCALE)}")
        for f in h.get("functions") or []:
            if f not in funcs:
                errs.append(f"{i}: function {f} is not in WP-C-01 §3")
        for x in h.get("hara") or []:
            if x not in hz:
                errs.append(f"{i}: HARA hazard {x} does not exist")
    seen = set()
    for a in m.get("acceptance", []):
        i = str(a.get("id"))
        if not re.fullmatch(r"AC-\d\d", i) or i in seen:
            errs.append(f"{i}: acceptance criterion id must look like AC-01 and be unique")
        seen.add(i)
        if not a.get("statement") or not a.get("basis"):
            errs.append(f"{i}: needs statement and basis")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, funcs: dict[str, str]) -> dict[str, str]:
    hs = m["hazards"]
    t = {}
    rows = [
        "| ID | Hazardous behaviour | Insufficiency | Functions | Related HARA hazards | Example triggering conditions |",
        "|---|---|---|---|---|---|",
    ]
    for h in hs:
        rows.append(
            f"| {h['id']} | {cell(h['behaviour'])} | {h['insufficiency'].capitalize()} | {', '.join(h['functions'])} "
            f"| {', '.join(h['hara']) or '— (SOTIF only)'} | {cell(h['triggers'])} |"
        )
    t["sotif-hazards"] = "\n".join(rows)
    rows = [
        "| ID | Harm | S | C | Further evaluation | Measures already in the concept |",
        "|---|---|---|---|---|---|",
    ]
    for h in hs:
        rows.append(
            f"| {h['id']} | {cell(h['harm'])} | {h['severity']} | {h['controllability']} | {'**Yes**' if further(h) else 'No'} | {cell(h['measures'])} |"
        )
    t["sotif-evaluation"] = "\n".join(rows)
    rows = ["| ID | Acceptance criterion | Basis |", "|---|---|---|"]
    rows += [
        f"| {a['id']} | {cell(a['statement'])} | {cell(a['basis'])} |" for a in m["acceptance"]
    ]
    t["sotif-acceptance"] = "\n".join(rows)
    n_further = sum(1 for h in hs if further(h))
    spec = sum(1 for h in hs if h["insufficiency"] == "specification")
    only = sum(1 for h in hs if not h["hara"])
    t["sotif-summary"] = (
        f"{len(hs)} SOTIF hazards ({spec} from insufficiencies of the specification, {len(hs) - spec} of performance), "
        f"{n_further} needing further evaluation; {len(hs) - only} share a vehicle-level behaviour with a HARA hazard "
        f"and {only} {'is' if only == 1 else 'are'} SOTIF only. {len(m['acceptance'])} acceptance criteria."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/sotif/sotif.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-05 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .perf { fill:var(--acc); } svg .spec { fill:var(--bg); stroke:var(--acc); stroke-width:2; }
svg .col { font:500 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .sev { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
"""


def figure(m: dict, funcs: dict[str, str]) -> str:
    fids = list(funcs)
    used = [f for f in fids if any(f in h["functions"] for h in m["hazards"])]
    x0, xg, top = 24, 150, 112
    cw = (W - 24 - xg) / len(used)
    rh = 26
    body = [
        fk.text(24, 32, "Which insufficiencies lead to which hazards", "h"),
        fk.text(24, 54, "WP-C-05 §4: a dot where a function's insufficiency can cause", "t"),
        fk.text(24, 71, "the hazard; filled for performance, hollow for specification", "t"),
    ]
    for j, f in enumerate(used):
        body.append(fk.text(xg + cw * j + cw / 2, top - 12, f[2:], "col", "middle"))
    body.append(fk.text(xg - 8, top - 12, "F-", "col", "end"))
    y = top
    for i, h in enumerate(m["hazards"]):
        if i % 2 == 0:
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=x0 - 8,
                    y=fk.num(y),
                    width=W - 2 * (x0 - 8),
                    height=rh,
                    rx=4,
                    class_="card",
                )
            )
        body.append(fk.text(x0, y + 17, h["id"], "tb"))
        body.append(
            fk.text(
                x0 + 52, y + 17, f"{h['severity']} · {', '.join(h['hara']) or 'SOTIF only'}", "sev"
            )
        )
        for j, f in enumerate(used):
            if f in h["functions"]:
                cls = "perf" if h["insufficiency"] == "performance" else "spec"
                body.append(
                    fk.el(
                        "circle",
                        None,
                        cx=fk.num(xg + cw * j + cw / 2),
                        cy=fk.num(y + rh / 2),
                        r=6,
                        class_=cls,
                    )
                )
        y += rh
    y += 24
    body += [
        fk.el("circle", None, cx=x0 + 6, cy=fk.num(y - 4), r=6, class_="perf"),
        fk.text(x0 + 18, y, "Performance insufficiency", "t"),
        fk.el("circle", None, cx=x0 + 216, cy=fk.num(y - 4), r=6, class_="spec"),
        fk.text(x0 + 228, y, "Specification insufficiency", "t"),
    ]
    y += 24
    for k, f in enumerate(used):
        col, row = k % 2, k // 2
        body.append(fk.text(x0 + col * 300, y + row * 17, fk.fit(f"{f} {funcs[f]}", 290, "s"), "s"))
    y += 17 * ((len(used) + 1) // 2) + 8
    desc = (
        "SOTIF hazards and the functions whose insufficiencies can cause them: "
        + "; ".join(
            f"{h['id']} ({h['insufficiency']}, {h['severity']}): {', '.join(h['functions'])}"
            for h in m["hazards"]
        )
        + "."
    )
    return fk.svg(W, int(y), "WP-C-05 Figure 4-1: functions and SOTIF hazards", desc, body, EXTRA)


def build() -> dict[Path, str]:
    m, funcs = load(), functions()
    errs = check(m, funcs, hara_hazards())
    if errs:
        raise fk.FigureError("sotif.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, funcs)), FIG: figure(m, funcs)}


if __name__ == "__main__":
    fk.run(build, __doc__)
