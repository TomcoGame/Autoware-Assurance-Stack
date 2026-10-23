#!/usr/bin/env python3
"""The functional insufficiencies and triggering conditions of WP-C-06, generated from triggering.yaml.

Writes the generated tables of WP-C-06 (insufficiencies, triggering conditions, AI error causes)
and Figure 5-1 (how many triggering conditions of each kind lead to each SOTIF hazard). Which
hazards a triggering condition leads to is computed through the insufficiencies it exposes, not
typed.

The model is refused when:
- an identifier is malformed or repeated, or a kind, category or AI error cause is unknown;
- an insufficiency names a function that is not in WP-C-01 §3 or a hazard that is not in
  ../sotif/sotif.yaml; a triggering condition names an ODD attribute or monitor that is not in
  WP-C-02, or an insufficiency that does not exist;
- a SOTIF hazard that needs further evaluation has no insufficiency, or an insufficiency no
  triggering condition;
- AI error causes are given for an insufficiency of a function that is not an ML function in
  WP-C-01 §3, or an ML function has no insufficiency with AI error causes;
- a triggering condition outside the ODD does not name the monitor that must catch it.

    python3 triggering.py            # write WP-C-06's generated tables and Figure 5-1
    python3 triggering.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "sotif"))
import figkit as fk  # noqa: E402
import sotif  # noqa: E402

MODEL = HERE / "triggering.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-06-sotif-insufficiencies-triggering-conditions.md"
ITEM = ASSURANCE / "02-concept" / "WP-C-01-item-definition.md"
ODD = ASSURANCE / "02-concept" / "WP-C-02-odd-and-intended-functionality.md"
FIG = HERE / "fig-c06-5-1-coverage.svg"
KINDS = ("specification", "performance")
CATEGORIES = {
    "environment": "Environment",
    "road": "Road and map",
    "road_users": "Road users",
    "vehicle": "Vehicle and sensors",
    "operations": "Operations",
}
# AI error causes, after the kinds of cause ISO/PAS 8800 asks to be analysed for an AI component.
AI_CAUSES = {
    "coverage": "Training data do not cover part of the input space (WP-C-02 §6)",
    "labels": "Errors or inconsistencies in the labels of training or test data",
    "shift": "The data seen in operation differ in distribution from the training data (new place, sensor, season)",
    "robustness": "Small changes of the input (noise, blur, partial occlusion) change the output",
    "ood": "Inputs unlike anything in the training data, for which the output is arbitrary",
    "calibration": "The confidence the model reports does not match how often it is right",
}
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ml_functions() -> set[str]:
    """The functions WP-C-01 §3 marks as realised by ML components."""
    head, rows = fk.table(fk.section(ITEM.read_text(encoding="utf-8"), "## 3. The item"), "ID")
    return {fk.plain(r[0]) for r in rows if "ML component" in r[fk.col(head, "State")]}


def odd() -> tuple[dict[str, str], set[str]]:
    """{ODD-xx: what is inside the ODD for it}, and the monitors of WP-C-02 §4."""
    md = ODD.read_text(encoding="utf-8")
    attrs = {}
    for ln in md.splitlines():
        m = re.match(r"\| (ODD-\d\d) \| ([^|]+) \| ([^|]+) \|", ln)
        if m:
            attrs[m.group(1)] = m.group(3).strip()
    _, rows = fk.table(fk.section(md, "## 4. ODD monitoring"), "ID")
    return attrs, {fk.plain(r[0]) for r in rows}


def known() -> dict:
    s = sotif.load()
    attrs, mons = odd()
    return {
        "functions": sotif.functions(),
        "ml": ml_functions(),
        "hazards": {h["id"]: h for h in s["hazards"]},
        "odd": attrs,
        "monitors": mons,
    }


def leads_to(m: dict, tc: dict) -> list[str]:
    """The SOTIF hazards a triggering condition can lead to, through what it exposes."""
    fis = {f["id"]: f for f in m["insufficiencies"]}
    return sorted({h for f in tc["exposes"] if f in fis for h in fis[f]["hazards"]})


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []

    def ids(items: list[dict], pat: str) -> None:
        seen: set[str] = set()
        for x in items:
            i = str(x.get("id"))
            if not re.fullmatch(pat, i):
                errs.append(f"{i}: id must look like {pat.replace(chr(92) + 'd', '0')}")
            if i in seen:
                errs.append(f"{i}: duplicate id")
            seen.add(i)

    fis = m.get("insufficiencies", [])
    tcs = m.get("triggers", [])
    ids(fis, r"FI-\d\d")
    ids(tcs, r"TC-\d\d")
    fi_ids = {f.get("id") for f in fis}
    for f in fis:
        i = f["id"]
        for key in ("element", "description", "functions", "hazards"):
            if not f.get(key):
                errs.append(f"{i}: missing {key}")
        if f.get("kind") not in KINDS:
            errs.append(f"{i}: kind must be one of {', '.join(KINDS)}")
        for fn in f.get("functions") or []:
            if fn not in k["functions"]:
                errs.append(f"{i}: function {fn} is not in WP-C-01 §3")
        for h in f.get("hazards") or []:
            if h not in k["hazards"]:
                errs.append(f"{i}: SOTIF hazard {h} does not exist")
        ai = f.get("ai") or []
        for c in ai:
            if c not in AI_CAUSES:
                errs.append(f"{i}: AI error cause {c} must be one of {', '.join(AI_CAUSES)}")
        if ai and not set(f.get("functions") or []) & k["ml"]:
            errs.append(f"{i}: has AI error causes but none of its functions is an ML function")
        if not any(f["id"] in (t.get("exposes") or []) for t in tcs):
            errs.append(f"{i}: no triggering condition exposes it")
    for t in tcs:
        i = t["id"]
        if t.get("category") not in CATEGORIES:
            errs.append(f"{i}: category must be one of {', '.join(CATEGORIES)}")
        if not t.get("condition"):
            errs.append(f"{i}: missing condition")
        if not t.get("exposes"):
            errs.append(f"{i}: exposes no insufficiency")
        for f in t.get("exposes") or []:
            if f not in fi_ids:
                errs.append(f"{i}: insufficiency {f} does not exist")
        for o in t.get("odd") or []:
            if o not in k["odd"]:
                errs.append(f"{i}: ODD attribute {o} is not in WP-C-02 §3")
        mon = t.get("monitor")
        if mon is not None and mon not in k["monitors"]:
            errs.append(f"{i}: monitor {mon} is not in WP-C-02 §4")
        if any(k["odd"].get(o) == "None" for o in t.get("odd") or []) and not mon:
            errs.append(f"{i}: a condition outside the ODD needs the monitor that catches it")
    for h, d in k["hazards"].items():
        if sotif.further(d) and not any(h in f.get("hazards", []) for f in fis):
            errs.append(f"{h}: needs further evaluation but no insufficiency leads to it")
    for fn in sorted(k["ml"]):
        if not any(fn in f.get("functions", []) and f.get("ai") for f in fis):
            errs.append(f"{fn}: an ML function with no insufficiency giving AI error causes")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    fis, tcs = m["insufficiencies"], m["triggers"]
    t = {}
    for kind in KINDS:
        rows = [
            "| ID | Element | Insufficiency | Functions | SOTIF hazards | Exposed by |",
            "|---|---|---|---|---|---|",
        ]
        for f in fis:
            if f["kind"] != kind:
                continue
            by = [x["id"] for x in tcs if f["id"] in x["exposes"]]
            rows.append(
                f"| {f['id']} | {cell(f['element'])} | {cell(f['description'])} "
                f"| {', '.join(f['functions'])} | {', '.join(f['hazards'])} | {', '.join(by)} |"
            )
        t[f"triggering-{kind}"] = "\n".join(rows)
    rows = [
        "| ID | Kind | Triggering condition | ODD attributes | Caught by | Exposes | Can lead to |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in tcs:
        rows.append(
            f"| {x['id']} | {CATEGORIES[x['category']]} | {cell(x['condition'])} | {', '.join(x['odd']) or '—'} "
            f"| {x.get('monitor') or '— (inside the ODD)'} | {', '.join(x['exposes'])} | {', '.join(leads_to(m, x))} |"
        )
    t["triggering-conditions"] = "\n".join(rows)
    rows = ["| Cause | What it means | Insufficiencies |", "|---|---|---|"]
    for c, what in AI_CAUSES.items():
        on = [f["id"] for f in fis if c in (f.get("ai") or [])]
        rows.append(f"| {c} | {cell(what)} | {', '.join(on) or '—'} |")
    t["triggering-ai"] = "\n".join(rows)
    spec = sum(1 for f in fis if f["kind"] == "specification")
    ai = [f["id"] for f in fis if f.get("ai")]
    edge = [x["id"] for x in tcs if x.get("monitor")]
    t["triggering-summary"] = (
        f"{len(fis)} functional insufficiencies ({spec} of the specification, {len(fis) - spec} of performance, "
        f"{len(ai)} of them in ML components) and {len(tcs)} triggering conditions, of which {len(edge)} lie "
        f"at the boundary of the ODD and must be caught by a monitor. Every SOTIF hazard that needs further "
        f"evaluation is reached by at least one. None is evaluated yet (WP-V-03)."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/triggering/triggering.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-06 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


# Four steps of one hue: the count of triggering conditions in a cell.
EXTRA = """svg .c1 { fill:var(--acc); fill-opacity:.18; } svg .c2 { fill:var(--acc); fill-opacity:.42; }
svg .c3 { fill:var(--acc); fill-opacity:.68; } svg .c4 { fill:var(--acc); fill-opacity:.92; }
svg .n { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .ni { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .col { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
"""


def figure(m: dict, k: dict) -> str:
    cats = list(CATEGORIES)
    hz = list(k["hazards"])
    count = {(h, c): 0 for h in hz for c in cats}
    for x in m["triggers"]:
        for h in leads_to(m, x):
            count[(h, x["category"])] += 1
    x0, top, rh = 150, 132, 24
    cw = (W - 24 - x0) / len(cats)
    body = [
        fk.text(24, 32, "Where the triggering conditions fall", "h"),
        fk.text(24, 54, "WP-C-06 §5: the number of triggering conditions of each kind", "t"),
        fk.text(24, 71, "that can lead to each SOTIF hazard", "t"),
    ]
    for j, c in enumerate(cats):
        lines = fk.wrap(CATEGORIES[c], cw - 8, "s")
        for n, ln in enumerate(lines):
            body.append(
                fk.text(
                    x0 + cw * j + cw / 2, top - 14 - 14 * (len(lines) - 1 - n), ln, "col", "middle"
                )
            )
    for i, h in enumerate(hz):
        y = top + i * rh
        body.append(fk.text(24, y + 16, h, "tb"))
        body.append(fk.text(76, y + 16, k["hazards"][h]["severity"], "s"))
        for j, c in enumerate(cats):
            n = count[(h, c)]
            cx = x0 + cw * j
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(cx + 2),
                    y=y + 2,
                    width=fk.num(cw - 4),
                    height=rh - 4,
                    rx=3,
                    class_=f"c{min(n, 4)}" if n else "card",
                )
            )
            if n:
                body.append(fk.text(cx + cw / 2, y + 16, str(n), "ni" if n >= 3 else "n", "middle"))
    y = top + len(hz) * rh + 30
    body.append(fk.text(24, y, "Triggering conditions per cell:", "t"))
    for n in range(1, 5):
        lx = 232 + (n - 1) * 70
        body.append(fk.el("rect", None, x=lx, y=y - 13, width=26, height=18, rx=3, class_=f"c{n}"))
        body.append(fk.text(lx + 32, y, f"{n}+" if n == 4 else str(n), "t"))
    y += 24
    desc = (
        "Number of triggering conditions of each kind that can lead to each SOTIF hazard: "
        + "; ".join(
            f"{h}: " + ", ".join(f"{CATEGORIES[c]} {count[(h, c)]}" for c in cats if count[(h, c)])
            for h in hz
        )
        + "."
    )
    return fk.svg(
        W, int(y), "WP-C-06 Figure 5-1: triggering conditions by hazard", desc, body, EXTRA
    )


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("triggering.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
