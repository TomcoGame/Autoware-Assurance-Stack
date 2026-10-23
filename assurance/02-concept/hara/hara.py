#!/usr/bin/env python3
"""The HARA of WP-C-03, generated from hara.yaml.

Writes the four generated tables of WP-C-03 (operational situations, hazards, hazardous events,
safety goals) and Figure 6-1 (the ASIL of every hazardous event, hazard by situation). No ASIL is
typed anywhere: each hazardous event's ASIL is computed from its S, E and C ratings with the rule
of ISO 26262-3:2018 Table 4, and each safety goal takes the highest ASIL of its hazards' events.

The model is refused when:
- a rating is not one of S0–S3, E0–E4, C0–C3, or an identifier is malformed or repeated;
- a hazardous event names a hazard or situation that does not exist, or its number does not
  start with its hazard's (HE-04.2 belongs to H-04);
- a hazard has no hazardous event, or is not covered by exactly one safety goal;
- a situation is not used by any hazardous event.

    python3 hara.py            # write WP-C-03's generated tables and Figure 6-1
    python3 hara.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
import figkit as fk  # noqa: E402

MODEL = HERE / "hara.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-03-hara.md"
FIG = HERE / "fig-c03-6-1-asil-matrix.svg"
ASILS = ["QM", "A", "B", "C", "D"]
S_SCALE, E_SCALE, C_SCALE = (
    ("S0", "S1", "S2", "S3"),
    ("E0", "E1", "E2", "E3", "E4"),
    ("C0", "C1", "C2", "C3"),
)
W = 640


def asil(s: str, e: str, c: str) -> str:
    """ISO 26262-3:2018 Table 4. Any class 0 gives QM; otherwise S + E + C of 10 is D, 9 C, 8 B,
    7 A, and anything lower QM."""
    si, ei, ci = int(s[1]), int(e[1]), int(c[1])
    if 0 in (si, ei, ci):
        return "QM"
    return {10: "D", 9: "C", 8: "B", 7: "A"}.get(si + ei + ci, "QM")


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(m: dict) -> list[str]:
    errs: list[str] = []
    sits = {s["id"]: s for s in m.get("situations", [])}
    hazs = {h["id"]: h for h in m.get("hazards", [])}
    evs = m.get("events", [])
    goals = m.get("goals", [])
    for kind, items, pat in (
        ("situation", m.get("situations", []), r"OS-\d\d"),
        ("hazard", m.get("hazards", []), r"H-\d\d"),
        ("event", evs, r"HE-\d\d\.\d"),
        ("goal", goals, r"SG-\d\d"),
    ):
        seen = set()
        for it in items:
            i = it.get("id", "?")
            if not re.fullmatch(pat, str(i)):
                errs.append(f"{kind} {i}: id must look like {pat}")
            if i in seen:
                errs.append(f"{kind} {i}: duplicate id")
            seen.add(i)
    for s in sits.values():
        if s.get("exposure") not in E_SCALE:
            errs.append(f"{s['id']}: exposure must be one of {', '.join(E_SCALE)}")
    for e in evs:
        i = e.get("id")
        if e.get("hazard") not in hazs:
            errs.append(f"{i}: hazard {e.get('hazard')} does not exist")
        elif not str(i).startswith("HE-" + e["hazard"][2:] + "."):
            errs.append(f"{i}: its number must start with its hazard's ({e['hazard']})")
        if e.get("situation") not in sits:
            errs.append(f"{i}: situation {e.get('situation')} does not exist")
        if e.get("severity") not in S_SCALE:
            errs.append(f"{i}: severity must be one of {', '.join(S_SCALE)}")
        if e.get("controllability") not in C_SCALE:
            errs.append(f"{i}: controllability must be one of {', '.join(C_SCALE)}")
        for k in ("description", "s_rationale", "c_rationale", "at_risk"):
            if not e.get(k):
                errs.append(f"{i}: missing {k}")
    covered: dict[str, list[str]] = {}
    for g in goals:
        for h in g.get("hazards", []):
            if h not in hazs:
                errs.append(f"{g['id']}: hazard {h} does not exist")
            covered.setdefault(h, []).append(g["id"])
        for k in ("statement", "safe_state"):
            if not g.get(k):
                errs.append(f"{g['id']}: missing {k}")
    for h in hazs:
        if not any(e.get("hazard") == h for e in evs):
            errs.append(f"{h}: no hazardous event rates it")
        if len(covered.get(h, [])) != 1:
            errs.append(
                f"{h}: must be covered by exactly one safety goal, is by {covered.get(h, [])}"
            )
    for s in sits:
        if not any(e.get("situation") == s for e in evs):
            errs.append(f"{s}: no hazardous event uses it")
    return errs


def rated(m: dict) -> list[dict]:
    """Events with their exposure (from the situation) and computed ASIL."""
    sits = {s["id"]: s for s in m["situations"]}
    out = []
    for e in m["events"]:
        ex = sits[e["situation"]]["exposure"]
        out.append({**e, "exposure": ex, "asil": asil(e["severity"], ex, e["controllability"])})
    return out


def goal_asil(m: dict, ev: list[dict]) -> dict[str, str]:
    return {
        g["id"]: max(
            (e["asil"] for e in ev if e["hazard"] in g["hazards"]), key=ASILS.index, default="QM"
        )
        for g in m["goals"]
    }


# ---------------------------------------------------------------- tables


def cell(s: str) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict) -> dict[str, str]:
    ev = rated(m)
    ga = goal_asil(m, ev)
    hz = {h["id"]: h for h in m["hazards"]}
    sit = {s["id"]: s for s in m["situations"]}
    t = {}
    rows = ["| ID | Situation | Description | Exposure | Basis |", "|---|---|---|---|---|"]
    rows += [
        f"| {s['id']} | {cell(s['name'])} | {cell(s['description'])} | {s['exposure']} | {cell(s['basis'])} |"
        for s in m["situations"]
    ]
    t["hara-situations"] = "\n".join(rows)
    rows = [
        "| ID | Hazard | Description | Hazardous events | Safety goal |",
        "|---|---|---|---|---|",
    ]
    for h in m["hazards"]:
        hes = ", ".join(e["id"] for e in ev if e["hazard"] == h["id"])
        sg = next(g["id"] for g in m["goals"] if h["id"] in g["hazards"])
        rows.append(f"| {h['id']} | {cell(h['name'])} | {cell(h['description'])} | {hes} | {sg} |")
    t["hara-hazards"] = "\n".join(rows)
    rows = [
        "| ID | Hazard | Situation | Hazardous event | At risk | S | Severity rationale | E | C | Controllability rationale | ASIL |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for e in ev:
        rows.append(
            f"| {e['id']} | {e['hazard']} {cell(hz[e['hazard']]['name'])} | {e['situation']} {cell(sit[e['situation']]['name'])} "
            f"| {cell(e['description'])} | {cell(e['at_risk'])} | {e['severity']} | {cell(e['s_rationale'])} | {e['exposure']} "
            f"| {e['controllability']} | {cell(e['c_rationale'])} | **{e['asil']}** |"
        )
    t["hara-events"] = "\n".join(rows)
    rows = [
        "| ID | Safety goal | ASIL | Hazards | From hazardous events | Safe state |",
        "|---|---|---|---|---|---|",
    ]
    for g in m["goals"]:
        top = [e["id"] for e in ev if e["hazard"] in g["hazards"] and e["asil"] == ga[g["id"]]]
        rows.append(
            f"| {g['id']} | {cell(g['statement'])} | **{ga[g['id']]}** | {', '.join(g['hazards'])} | {', '.join(top)} | {cell(g['safe_state'])} |"
        )
    t["hara-goals"] = "\n".join(rows)
    counts = {a: sum(1 for e in ev if e["asil"] == a) for a in ASILS}
    gcounts = {a: sum(1 for v in ga.values() if v == a) for a in ASILS}
    t["hara-summary"] = (
        f"{len(m['situations'])} operational situations, {len(m['hazards'])} hazards, {len(ev)} hazardous events "
        f"({', '.join(f'{n} {a}' for a, n in counts.items() if n)}), {len(m['goals'])} safety goals "
        f"({', '.join(f'{n} ASIL {a}' if a != 'QM' else f'{n} QM' for a, n in gcounts.items() if n)})."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/hara/hara.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-03 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


# ---------------------------------------------------------------- figure

EXTRA = """svg { --a1:#f5dcd3; --a2:#eaa48f; --a3:#d4644a; --a4:#9e2f1c; --t1:#3b140b; --t4:#ffffff; }
@media (prefers-color-scheme: dark) { svg { --a1:#4a2820; --a2:#7d3a28; --a3:#bb4f34; --a4:#f07656; --t1:#f6e3dd; --t4:#1b0a05; } }
svg .qm { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .aa { fill:var(--a1); } svg .ab { fill:var(--a2); } svg .ac { fill:var(--a3); } svg .ad { fill:var(--a4); }
svg .tq { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .t1 { font:700 13px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--t1); }
svg .t4 { font:700 13px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--t4); }
svg .col { font:500 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""
FILL = {
    "QM": ("qm", "tq"),
    "A": ("aa", "t1"),
    "B": ("ab", "t1"),
    "C": ("ac", "t4"),
    "D": ("ad", "t4"),
}


def figure(m: dict) -> str:
    ev = rated(m)
    sits = [s["id"] for s in m["situations"]]
    x0, xg, top = 24, 252, 112
    cw = (W - 24 - xg) / len(sits)
    rh = 30
    body = [
        fk.text(24, 32, "ASIL of each hazardous event", "h"),
        fk.text(24, 54, "WP-C-03 §6: hazard by operational situation; A·2 is two events,", "t"),
        fk.text(24, 71, "the higher ASIL shown; empty where not rated", "t"),
    ]
    for j, s in enumerate(sits):
        body.append(fk.text(xg + cw * j + cw / 2, top - 10, s[3:], "col", "middle"))
    body.append(fk.text(xg - 8, top - 10, "OS-", "col", "end"))
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
        body.append(fk.text(x0, y + 19, h["id"], "tb"))
        body.append(fk.text(x0 + 46, y + 19, fk.fit(h["name"], xg - x0 - 54, "s"), "s"))
        for j, s in enumerate(sits):
            here = [e for e in ev if e["hazard"] == h["id"] and e["situation"] == s]
            if not here:
                continue
            top_asil = max((e["asil"] for e in here), key=ASILS.index)
            cls, tcls = FILL[top_asil]
            label = (
                top_asil if len(here) == 1 else f"{top_asil}·{len(here)}"
            )  # highest ASIL, and how many events
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(xg + cw * j + 2),
                    y=fk.num(y + 4),
                    width=fk.num(cw - 4),
                    height=rh - 8,
                    rx=4,
                    class_=cls,
                )
            )
            body.append(fk.text(xg + cw * j + cw / 2, y + 20, label, tcls, "middle"))
        y += rh
    y += 26
    x = x0
    for a in ASILS:
        n = sum(1 for e in ev if e["asil"] == a)
        if not n:
            continue
        cls, tcls = FILL[a]
        label = f"{'ASIL ' + a if a != 'QM' else 'QM'} ({n})"
        body += [
            fk.el("rect", None, x=x, y=fk.num(y - 13), width=26, height=18, rx=4, class_=cls),
            fk.text(x + 13, y + 1, a if a != "QM" else "Q", tcls, "middle"),
            fk.text(x + 32, y, label, "t"),
        ]
        x += 32 + fk.width(label, "t") + 18
    y += 20
    sit_name = {s["id"]: s["name"] for s in m["situations"]}
    desc = (
        "Hazardous events of WP-C-03 with their ASIL: "
        + "; ".join(
            f"{e['id']} ({e['hazard']} in {e['situation']} {sit_name[e['situation']]}): {e['asil']}"
            for e in ev
        )
        + "."
    )
    return fk.svg(W, int(y), "WP-C-03 Figure 6-1: ASIL of each hazardous event", desc, body, EXTRA)


def build() -> dict[Path, str]:
    m = load()
    errs = check(m)
    if errs:
        raise fk.FigureError("hara.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m)), FIG: figure(m)}


if __name__ == "__main__":
    fk.run(build, __doc__)
