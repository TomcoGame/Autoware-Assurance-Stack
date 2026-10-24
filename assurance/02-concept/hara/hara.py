#!/usr/bin/env python3
"""The HARA of WP-C-03, generated from hara.yaml and analysis.yaml.

Writes the generated tables of WP-C-03 (operational situations, conditions, functions and their
guide words, hazards, every rated hazardous event, the named hazardous events, safety goals),
Figures 6-1 and 6-2, the guide-word classification (guide-words.csv) and every rated row, one file
per hazard (hazardous-events/). No ASIL is typed anywhere: each row's and each named event's ASIL
is computed from S, E and C with the rule of ISO 26262-3:2018 Table 4, and each safety goal takes
the highest ASIL of its hazards' events.

Every safety-related pair of a function of WP-C-01 and a malfunction guide word, unless folded into
another pair of the same function, is rated in every operational situation under every condition:
S from the hazard and situation (analysis.yaml `severity`, or S0 with the reason in `none`), E the
rarer of the situation's and the condition's, C from `controllability`.

The model is refused when:
- a rating is not one of S0–S3, E0–E4, C0–C3, or an identifier is malformed or repeated;
- a hazardous event names a hazard or situation that does not exist, or its number does not
  start with its hazard's (HE-04.2 belongs to H-04);
- a hazard has no hazardous event, or is not covered by exactly one safety goal;
- a situation is used by no hazardous event and rated above S0 by no row;
- a function lacks a guide word, a class is not SC, NSC or NA, an SC pair names no hazard or is
  folded into a pair that is not SC or is itself folded, or an NSC or NA pair has no reason;
- a hazard is reached by no SC pair, or a hazard has neither a severity nor a reason for S0 in a
  situation;
- a named hazardous event is more severe than its row allows, or a row's ASIL exceeds the ASIL its
  safety goal takes from the named events.

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
ANALYSIS = HERE / "analysis.yaml"
EVENTS_DIR = HERE / "hazardous-events"
GUIDE_CSV = HERE / "guide-words.csv"
FIG2 = HERE / "fig-c03-6-2-all-events.svg"
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


def load_analysis(path: Path = ANALYSIS) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def pairs(a: dict) -> list[tuple[dict, str, list]]:
    """Every function and guide word with its classification."""
    return [(f, gw, f["class"][gw]) for f in a["functions"] for gw in a["guidewords"]]


def expanded(a: dict) -> list[tuple[dict, str, str]]:
    """The SC pairs rated row by row: those not folded into another pair."""
    return [(f, gw, c[1]) for f, gw, c in pairs(a) if c[0] == "SC" and not c[2]]


def severity(a: dict, m: dict, hz: str, sit: dict) -> tuple[str, str]:
    rule = a["severity"].get(hz, {}).get(sit["id"])
    if rule:
        return rule[0], rule[1]
    none = a["none"].get(hz, {})
    return "S0", none.get(sit["motion"]) or none.get("default") or ""


def analysis_rows(m: dict, a: dict) -> list[dict]:
    """Every rated row: expanded pair x situation x condition."""
    goal_of = {h: g["id"] for g in m["goals"] for h in g["hazards"]}
    c_cls, c_why = a["controllability"]["default"]
    out = []
    for f, gw, hz in expanded(a):
        for sit in m["situations"]:
            s, s_why = severity(a, m, hz, sit)
            for w in a["conditions"]:
                e = min(sit["exposure"], w["exposure"], key=E_SCALE.index)
                c = c_cls if s != "S0" else "C0"
                out.append(
                    {
                        "key": f"{f['id']}/{gw}/{sit['id']}/{w['id']}",
                        "function": f,
                        "gw": gw,
                        "hazard": hz,
                        "situation": sit,
                        "condition": w,
                        "s": s,
                        "e": e,
                        "c": c,
                        "asil": asil(s, e, c),
                        "goal": goal_of.get(hz, ""),
                        "s_why": s_why,
                        "e_why": f"{sit['id']} {sit['exposure']}, {w['id']} {w['exposure']}: the rarer of the two",
                        "c_why": c_why if s != "S0" else "Not rated; no hazard in this situation",
                    }
                )
    return out


def check_analysis(m: dict, a: dict) -> list[str]:
    errs: list[str] = []
    hazs = {h["id"] for h in m.get("hazards", [])}
    sits = {s["id"]: s for s in m.get("situations", [])}
    for s in sits.values():
        if s.get("motion") not in ("moving", "stopped"):
            errs.append(f"{s['id']}: motion must be moving or stopped")
    for w in a.get("conditions", []):
        if w.get("exposure") not in E_SCALE:
            errs.append(f"{w['id']}: exposure must be one of {', '.join(E_SCALE)}")
    reached: set[str] = set()
    for f in a.get("functions", []):
        cls = f.get("class") or {}
        for gw in a["guidewords"]:
            c = cls.get(gw)
            key = f"{f['id']}/{gw}"
            if not c or len(c) != 4:
                errs.append(
                    f"{key}: needs [class, hazard, folded into, reason]; quote a reason with commas"
                )
                continue
            kind, hz, into, why = c
            if kind not in ("SC", "NSC", "NA"):
                errs.append(f"{key}: class must be SC, NSC or NA")
            if not why:
                errs.append(f"{key}: no reason given")
            if kind == "SC":
                if hz not in hazs:
                    errs.append(f"{key}: hazard {hz} does not exist")
                reached.add(hz)
                if into:
                    t = cls.get(into)
                    if not t or t[0] != "SC" or t[2]:
                        errs.append(
                            f"{key}: folded into {into}, which is not an SC pair rated itself"
                        )
                    elif t[1] != hz:
                        errs.append(f"{key}: folded into {into}, which leads to {t[1]}, not {hz}")
            elif hz or into:
                errs.append(f"{key}: only an SC pair names a hazard or is folded")
        for gw in cls:
            if gw not in a["guidewords"]:
                errs.append(f"{f['id']}/{gw}: not a guide word")
    for h in hazs:
        if h not in reached:
            errs.append(f"{h}: reached by no SC function and guide-word pair")
        for sid, sit in sits.items():
            s, why = severity(a, m, h, sit)
            if s not in S_SCALE:
                errs.append(f"{h} in {sid}: severity must be one of {', '.join(S_SCALE)}")
            if not why:
                errs.append(f"{h} in {sid}: neither a severity nor a reason for S0")
    for h, by in a.get("severity", {}).items():
        for sid, rule in by.items():
            if not isinstance(rule, list) or len(rule) != 2:
                errs.append(f"{h} in {sid}: needs [severity, reason]; quote a reason with commas")
            if sid not in sits:
                errs.append(f"{h}: severity for {sid}, which is not a situation")
    if errs:
        return errs
    rs = analysis_rows(m, a)
    ev = rated(m)
    ga = goal_asil(m, ev)
    for e in ev:
        s, _ = severity(a, m, e["hazard"], sits[e["situation"]])
        if S_SCALE.index(e["severity"]) > S_SCALE.index(s):
            errs.append(
                f"{e['id']}: rated {e['severity']}, more severe than {s} for {e['hazard']} in {e['situation']}"
            )
    for r in rs:
        g = r["goal"]
        if g and ASILS.index(r["asil"]) > ASILS.index(ga[g]):
            errs.append(
                f"{r['key']}: ASIL {r['asil']} exceeds {g}'s {ga[g]}; name the event in hara.yaml or re-rate it"
            )
            break
    return errs


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
    rated_sits: set[str] = set()
    if not errs and ANALYSIS.exists():
        a = load_analysis()
        errs += check_analysis(m, a)
        if not errs:
            rated_sits = {r["situation"]["id"] for r in analysis_rows(m, a) if r["s"] != "S0"}
    for s in sits:
        if not any(e.get("situation") == s for e in evs) and s not in rated_sits:
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


# ---------------------------------------------------------------- files


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def event_file(h: dict) -> Path:
    return EVENTS_DIR / f"{h['id']}-{slug(h['name'])}.csv"


def to_csv(header: list[str], data: list[list[str]]) -> str:
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(data)
    return buf.getvalue()


def csv_files(m: dict, a: dict) -> dict[Path, str]:
    gw = a["guidewords"]
    out = {}
    head = [
        "Key",
        "Function",
        "Guide word",
        "Situation",
        "Condition",
        "S",
        "E",
        "C",
        "ASIL",
        "Safety goal",
        "Severity basis",
        "Exposure basis",
        "Controllability basis",
    ]
    rs = analysis_rows(m, a)
    for h in m["hazards"]:
        data = [
            [
                r["key"],
                f"{r['function']['id']} {r['function']['name']}",
                f"{r['gw']} {gw[r['gw']]['name']}",
                f"{r['situation']['id']} {r['situation']['name']}",
                f"{r['condition']['id']} {r['condition']['name']}",
                r["s"],
                r["e"],
                r["c"],
                r["asil"],
                r["goal"],
                r["s_why"],
                r["e_why"],
                r["c_why"],
            ]
            for r in rs
            if r["hazard"] == h["id"]
        ]
        out[event_file(h)] = to_csv(head, data)
    data = [
        [
            f"{f['id']}/{g}",
            f"{f['id']} {f['name']}",
            f"{g} {gw[g]['name']}",
            c[0],
            c[1],
            c[2] and f"{c[2]} {gw[c[2]]['name']}",
            c[3],
        ]
        for f, g, c in pairs(a)
    ]
    out[GUIDE_CSV] = to_csv(
        ["Key", "Function", "Guide word", "Class", "Hazard", "Rated as", "Reason"], data
    )
    return out


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
    t.update(analysis_tables(m, load_analysis()))
    counts = {a: sum(1 for e in ev if e["asil"] == a) for a in ASILS}
    gcounts = {a: sum(1 for v in ga.values() if v == a) for a in ASILS}
    rs = analysis_rows(m, load_analysis())
    rated_rows = [r for r in rs if r["s"] != "S0"]
    t["hara-summary"] = (
        f"{len(rs)} rated rows (every safety-related function and malfunction pair in every situation and "
        f"condition; {len(rated_rows)} hazardous, {sum(r['asil'] != 'QM' for r in rs)} of them ASIL A or above), "
        f"{len(m['situations'])} operational situations, {len(m['hazards'])} hazards, {len(ev)} named hazardous events "
        f"({', '.join(f'{n} {a}' for a, n in counts.items() if n)}), {len(m['goals'])} safety goals "
        f"({', '.join(f'{n} ASIL {a}' if a != 'QM' else f'{n} QM' for a, n in gcounts.items() if n)})."
    )
    return t


def worst(rs: list[dict]) -> str:
    return max((r["asil"] for r in rs), key=ASILS.index, default="QM")


def analysis_tables(m: dict, a: dict) -> dict[str, str]:
    t = {}
    rs = analysis_rows(m, a)
    gw = a["guidewords"]
    rows_ = ["| ID | Condition | Exposure | Basis |", "|---|---|---|---|"]
    rows_ += [
        f"| {w['id']} | {cell(w['name'])} | {w['exposure']} | {cell(w['basis'])} |"
        for w in a["conditions"]
    ]
    t["hara-conditions"] = "\n".join(rows_)
    rows_ = ["| ID | Guide word | Means |", "|---|---|---|"]
    rows_ += [f"| {g} | {v['name']} | {cell(v['means'])} |" for g, v in gw.items()]
    t["hara-guidewords"] = "\n".join(rows_)
    rows_ = [
        "| ID | Function | Safety-related (rated) | Safety-related (folded) | Not safety-related | Not applicable | Hazards reached |",
        "|---|---|---|---|---|---|---|",
    ]
    for f in a["functions"]:
        cs = list(f["class"].values())
        sc = [c for c in cs if c[0] == "SC"]
        rows_.append(
            f"| {f['id']} | {cell(f['name'])} | {sum(not c[2] for c in sc)} | {sum(bool(c[2]) for c in sc)} "
            f"| {sum(c[0] == 'NSC' for c in cs)} | {sum(c[0] == 'NA' for c in cs)} "
            f"| {', '.join(sorted({c[1] for c in sc})) or '—'} |"
        )
    t["hara-functions"] = "\n".join(rows_)
    allp = pairs(a)
    sc = [p for p in allp if p[2][0] == "SC"]
    rated_rows = [r for r in rs if r["s"] != "S0"]
    distinct = {(r["hazard"], r["situation"]["id"]) for r in rated_rows}
    by = {x: sum(r["asil"] == x for r in rs) for x in ASILS}
    rows_ = ["| Step | Count |", "|---|---|"]
    rows_ += [
        f"| Functions × guide words ({len(a['functions'])} × {len(gw)}) | {len(allp)} |",
        f"| … safety-related | {len(sc)} ({len(expanded(a))} rated, {len(sc) - len(expanded(a))} folded into another with the same effect) |",
        f"| … not safety-related | {sum(p[2][0] == 'NSC' for p in allp)} |",
        f"| … not applicable | {sum(p[2][0] == 'NA' for p in allp)} |",
        f"| Situations × conditions ({len(m['situations'])} × {len(a['conditions'])}) | {len(m['situations']) * len(a['conditions'])} |",
        f"| Rated rows ({len(expanded(a))} × {len(m['situations']) * len(a['conditions'])}) | {len(rs)} |",
        f"| … not hazardous in that situation (S0, reason recorded) | {len(rs) - len(rated_rows)} |",
        f"| … QM | {by['QM'] - (len(rs) - len(rated_rows))} |",
        f"| … ASIL A / B / C / D | {by['A']} / {by['B']} / {by['C']} / {by['D']} |",
        f"| Distinct hazardous events (hazard × situation, S above S0) | {len(distinct)} |",
    ]
    t["hara-counts"] = "\n".join(rows_)
    rows_ = [
        "| Hazard | Rows | Rated A or above | Worst ASIL | Situations where it is worst | Safety goal | Open as a table |",
        "|---|---|---|---|---|---|---|",
    ]
    goal_of = {h: g["id"] for g in m["goals"] for h in g["hazards"]}
    for h in m["hazards"]:
        hr = [r for r in rs if r["hazard"] == h["id"]]
        w = worst(hr)
        at = sorted({r["situation"]["id"] for r in hr if r["asil"] == w and w != "QM"})
        rel = event_file(h).relative_to(DOC.parent).as_posix()
        rows_.append(
            f"| {h['id']} {cell(h['name'])} | {len(hr)} | {sum(r['asil'] != 'QM' for r in hr)} | **{w}** "
            f"| {', '.join(at) or '—'} | {goal_of[h['id']]} | [{event_file(h).name}]({rel}) |"
        )
    t["hara-all-events"] = "\n".join(rows_)
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
    sits = [s["id"] for s in m["situations"] if any(e["situation"] == s["id"] for e in ev)]
    x0, xg, top = 24, 252, 112
    cw = (W - 24 - xg) / len(sits)
    rh = 30
    body = [
        fk.text(24, 32, "ASIL of each hazardous event", "h"),
        fk.text(24, 54, "WP-C-03 §6.3: hazard by operational situation; A·2 is two events,", "t"),
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


def figure_all(m: dict, a: dict) -> str:
    rs = analysis_rows(m, a)
    sits = [x["id"] for x in m["situations"]]
    x0, xg, top = 24, 196, 112
    cw = (W - 24 - xg) / len(sits)
    rh = 28
    body = [
        fk.text(24, 32, "Worst ASIL of every hazard in every situation", "h"),
        fk.text(24, 54, "WP-C-03 §6.2: highest ASIL over every function, guide word and", "t"),
        fk.text(24, 71, "condition rated there; empty where the hazard cannot occur (S0)", "t"),
    ]
    for j, sid in enumerate(sits):
        body.append(fk.text(xg + cw * j + cw / 2, top - 10, sid[3:], "col", "middle"))
    body.append(fk.text(xg - 6, top - 10, "OS-", "col", "end"))
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
        body.append(fk.text(x0, y + 18, h["id"], "tb"))
        body.append(fk.text(x0 + 46, y + 18, fk.fit(h["name"], xg - x0 - 52, "s"), "s"))
        for j, sid in enumerate(sits):
            here = [r for r in rs if r["hazard"] == h["id"] and r["situation"]["id"] == sid]
            if all(r["s"] == "S0" for r in here):
                continue
            w = worst(here)
            cls, tcls = FILL[w]
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(xg + cw * j + 1.5),
                    y=fk.num(y + 4),
                    width=fk.num(cw - 3),
                    height=rh - 8,
                    rx=3,
                    class_=cls,
                )
            )
            body.append(
                fk.text(xg + cw * j + cw / 2, y + 19, w if w != "QM" else "Q", tcls, "middle")
            )
        y += rh
    y += 26
    x = x0
    for asil_ in ASILS:
        cls, tcls = FILL[asil_]
        label = "QM" if asil_ == "QM" else f"ASIL {asil_}"
        body += [
            fk.el("rect", None, x=x, y=fk.num(y - 13), width=22, height=18, rx=3, class_=cls),
            fk.text(x + 11, y + 1, asil_ if asil_ != "QM" else "Q", tcls, "middle"),
            fk.text(x + 28, y, label, "t"),
        ]
        x += 28 + fk.width(label, "t") + 16
    y += 20
    desc = "Worst ASIL by hazard and situation: " + "; ".join(
        f"{h['id']}: "
        + ", ".join(
            f"{sid} {worst([r for r in rs if r['hazard'] == h['id'] and r['situation']['id'] == sid])}"
            for sid in sits
            if any(
                r["s"] != "S0" for r in rs if r["hazard"] == h["id"] and r["situation"]["id"] == sid
            )
        )
        for h in m["hazards"]
    )
    return fk.svg(
        W, int(y), "WP-C-03 Figure 6-2: worst ASIL by hazard and situation", desc + ".", body, EXTRA
    )


def build() -> dict[Path, str]:
    m = load()
    errs = check(m)
    if errs:
        raise fk.FigureError("hara.yaml: " + "; ".join(errs))
    a = load_analysis()
    out = {
        DOC: fill(DOC.read_text(encoding="utf-8"), tables(m)),
        FIG: figure(m),
        FIG2: figure_all(m, a),
    }
    out.update(csv_files(m, a))
    return out


if __name__ == "__main__":
    fk.run(build, __doc__)
