#!/usr/bin/env python3
"""The system verification specification of WP-S-09, generated from verif.yaml.

Writes the generated tables of WP-S-09 (verification cases, and the coverage of functional safety
requirements, triggering conditions, functional modifications and known scenarios) and Figure 2-1
(which safety goals and SOTIF measures each case verifies). A case covers what it names and,
through each scenario of WP-V-03 it runs, the requirements and modifications that scenario's pass
criterion refers to and the triggering conditions it varies. A case does not verify the requirements
of an element it excludes. A case's ASIL is the highest of the functional safety requirements it
covers.

The model is refused when:
- an identifier is malformed or repeated, or a method, environment or scenario named does not exist;
- a case runs a scenario its environment cannot run, or a case that tests has no environment;
- a case names a requirement of an element it excludes (the monitor in shadow mode);
- a functional safety requirement, triggering condition or functional modification is verified by
  no case, or a case covers something that does not exist;
- a functional safety requirement is not verified the way WP-C-04 says it is: by fault injection,
  timing, supplier evidence, scenario test, review, formal check, interface or performance test,
  or in simulation, HIL or the vehicle, wherever its `verify` names one;
- a known scenario that simulation, HIL or the track can run is run by no case.

    python3 verif.py            # write WP-S-09's generated tables and Figure 2-1
    python3 verif.py --check    # fail if either is stale or the model breaks a rule
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
    "02-concept/fsc",
    "02-concept/triggering",
    "02-concept/modifications",
    "03-system/integ",
    "06-validation/scenarios",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import integ  # noqa: E402
import modifications  # noqa: E402
import scenarios  # noqa: E402
import triggering  # noqa: E402

sys.path.insert(0, str(HERE))
import vcards  # noqa: E402

MODEL = HERE / "verif.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-09-system-verification.md"
FIG = HERE / "fig-s09-2-1-coverage.svg"
FIG2 = HERE / "fig-s09-2-2-requirements.svg"
CSV = HERE / "cases.csv"
README = HERE / "README.md"
ASILS = ["QM", "A", "B", "C", "D"]

# What WP-C-04 says about verifying a requirement, and what that asks of the cases covering it.
METHOD_WORDS = {
    "fault injection": "fault-injection",
    "ftti": "timing",
    "timing measurement": "timing",
    "supplier evidence": "supplier",
    "scenario test": "scenario",
    "review": "review",
    "formal check": "formal",
    "interface test": "interface",
    "detection performance": "performance",
    "false-positive rate": "performance",
}
ENV_WORDS = {"simulation": "ENV-1", "hil": "ENV-2", "vehicle test": "ENV-4"}


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    return {
        "fsrs": {r["id"]: r for r in fsc.load()["fsrs"]},
        "goals": fsc.goals(),
        "tcs": {t["id"]: t for t in triggering.load()["triggers"]},
        "fms": {f["id"]: f for f in modifications.load()["modifications"]},
        "scenarios": {s["id"]: s for s in scenarios.load()["scenarios"]},
        "envs": {e["id"]: e for e in integ.load()["environments"]},
    }


def covered(c: dict, k: dict) -> set[str]:
    """What a case verifies: what it names, and what its scenarios refer to and vary."""
    out = set(c.get("covers") or [])
    for sid in c.get("scenarios") or []:
        s = k["scenarios"].get(sid)
        if s:
            refs = s["pass"]["refs"] + (s.get("triggers") or [])
            out |= {r for r in refs if r in k["fsrs"] or r in k["fms"] or r in k["tcs"]}
    off = set(c.get("excludes") or [])
    return {x for x in out if x not in k["fsrs"] or k["fsrs"][x]["element"] not in off}


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for env, kinds in m.get("runs", {}).items():
        if env not in k["envs"]:
            errs.append(f"runs: environment {env} is not one of WP-S-08's")
    by: dict[str, list[dict]] = {}
    for c in m.get("cases", []):
        i = c["id"]
        if not re.fullmatch(r"VC-\d\d", str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        meths = c.get("methods") or []
        for meth in meths:
            if meth not in m["methods"]:
                errs.append(f"{i}: method {meth} does not exist")
        env = c.get("env")
        if env is None and not set(meths) <= {"review", "formal", "supplier"}:
            errs.append(f"{i}: tests, so needs an environment")
        if env is not None and env not in k["envs"]:
            errs.append(f"{i}: environment {env} is not one of WP-S-08's")
        if not c.get("pass"):
            errs.append(f"{i}: missing pass criterion")
        for sid in c.get("scenarios") or []:
            s = k["scenarios"].get(sid)
            if not s:
                errs.append(f"{i}: scenario {sid} does not exist")
            elif not set(m["runs"].get(env, [])) & set(s["methods"]):
                errs.append(f"{i}: {env} cannot run {sid}, which is for {', '.join(s['methods'])}")
        if c.get("scenarios") and "scenario" not in meths:
            errs.append(f"{i}: runs scenarios but is not a scenario test")
        for x in c.get("covers") or []:
            if x not in k["fsrs"] and x not in k["fms"] and x not in k["tcs"]:
                errs.append(f"{i}: covers {x}, which does not exist")
            elif x in k["fsrs"] and k["fsrs"][x]["element"] in (c.get("excludes") or []):
                errs.append(
                    f"{i}: covers {x}, but its element {k['fsrs'][x]['element']} does not act in it"
                )
        for x in covered(c, k):
            by.setdefault(x, []).append(c)
    for group, what in ((k["fsrs"], "requirement"), (k["tcs"], "triggering condition")):
        for x in group:
            if x not in by:
                errs.append(f"{x}: {what} verified by no case")
    for x in k["fms"]:
        if x not in by:
            errs.append(f"{x}: functional modification verified by no case")
    for x, r in k["fsrs"].items():
        cs = by.get(x, [])
        how = r.get("verify", "").lower()
        meths = {meth for c in cs for meth in c.get("methods") or []}
        envs = {c.get("env") for c in cs}
        for word, meth in METHOD_WORDS.items():
            if word in how and meth not in meths:
                errs.append(f"{x}: WP-C-04 verifies it by {word}, but no case covering it does")
        for word, env in ENV_WORDS.items():
            if word in how and env not in envs:
                errs.append(
                    f"{x}: WP-C-04 verifies it by {word}, but no case covering it runs in {env}"
                )
    runnable = set(m.get("must_run") or [])
    run = {sid for c in m.get("cases", []) for sid in c.get("scenarios") or []}
    for sid, s in k["scenarios"].items():
        if set(s["methods"]) & runnable and sid not in run:
            errs.append(
                f"{sid}: can be run in {', '.join(sorted(set(s['methods']) & runnable))} but no case runs it"
            )
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def asil(c: dict, k: dict) -> str:
    rated = [k["fsrs"][x]["asil"] for x in covered(c, k) if x in k["fsrs"]]
    return max(rated, key=ASILS.index) if rated else "—"


def ids(xs) -> str:
    return ", ".join(sorted(xs)) or "—"


def tables(m: dict, k: dict) -> dict[str, str]:
    t = {}
    cases = m["cases"]
    rows = ["| Environment (WP-S-08) | Runs scenarios marked | Cases |", "|---|---|---|"]
    for env, kinds in m["runs"].items():
        cs = [c["id"] for c in cases if c.get("env") == env]
        rows.append(
            f"| {env} {cell(k['envs'][env]['name'])} | {', '.join(kinds)} | {', '.join(cs) or '—'} |"
        )
    desk = [c["id"] for c in cases if not c.get("env")]
    rows.append(f"| No environment (review, formal check) | — | {', '.join(desk) or '—'} |")
    t["verif-environments"] = "\n".join(rows)
    rows = [
        "| ID | Verification case | Environment | Methods | ASIL | Scenarios run | Also covers | Pass criterion |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in cases:
        rows.append(
            f"| {c['id']} | {cell(c['name'])} | {c.get('env') or '—'} | {', '.join(c['methods'])} | {asil(c, k)} "
            f"| {ids(c['scenarios'])} | {ids(c['covers'])} | {cell(c['pass'])} |"
        )
    t["verif-cases"] = "\n".join(rows)
    rows = [
        "| Requirement | Safety goal | ASIL | Element | WP-C-04 says verify by | Verified by |",
        "|---|---|---|---|---|---|",
    ]
    for x, r in k["fsrs"].items():
        cs = [c["id"] for c in cases if x in covered(c, k)]
        rows.append(
            f"| {x} | {r['goal']} | {r['asil']} | {r['element']} | {cell(r['verify'])} | {', '.join(cs)} |"
        )
    t["verif-fsrs"] = "\n".join(rows)
    rows = ["| Triggering condition | Category | Verified by |", "|---|---|---|"]
    for x, tc in k["tcs"].items():
        cs = [c["id"] for c in cases if x in covered(c, k)]
        rows.append(f"| {x} {cell(tc['condition'])} | {tc['category']} | {', '.join(cs)} |")
    t["verif-tcs"] = "\n".join(rows)
    rows = ["| Functional modification | Type | Verified by |", "|---|---|---|"]
    for x, fm in k["fms"].items():
        cs = [c["id"] for c in cases if x in covered(c, k)]
        rows.append(f"| {x} {cell(fm['name'])} | {fm['type']} | {', '.join(cs)} |")
    t["verif-fms"] = "\n".join(rows)
    rows = ["| Method | Cases |", "|---|---|"]
    for meth, name in m["methods"].items():
        cs = [c["id"] for c in cases if meth in c["methods"]]
        rows.append(f"| {name} | {', '.join(cs) or '—'} |")
    t["verif-methods"] = "\n".join(rows)
    t["verif-requirement-cards"] = (
        "![Figure 2-2: one card per safety goal SG-01 to SG-09 and two for the SOTIF measures. A goal's card "
        "lists each of its functional safety requirements with the verification cases that verify it, as chips "
        "coloured by where the case runs (simulation, HIL, bench, closed track, or review only); the SOTIF cards "
        "do the same for the triggering conditions by category and the functional modifications by type. The "
        f"same coverage is in the tables of §3.](verif/{FIG2.name})\n\n"
        "*Figure 2-2. How each safety goal and SOTIF measure is verified, requirement by requirement. No case "
        "has been run. Drawn by [`verif/verif.py`](verif/verif.py); CI fails if it is stale. Every case is "
        f"also in [`verif/{CSV.name}`](verif/{CSV.name}).*"
    )
    run = {sid for c in cases for sid in c["scenarios"]}
    not_run = [s for s in k["scenarios"] if s not in run]
    t["verif-summary"] = (
        f"{len(cases)} verification cases cover all {len(k['fsrs'])} functional safety requirements of the "
        f"{len(k['goals'])} safety goals, each the way WP-C-04 says it is to be verified, all {len(k['tcs'])} "
        f"triggering conditions and all {len(k['fms'])} functional modifications, and run {len(run)} of the "
        f"{len(k['scenarios'])} known scenarios of WP-V-03 (the other {len(not_run)}, {ids(not_run)}, are "
        f"bench and operations exercises of validation, WP-V-07). No case has been run."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/verif/verif.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-09 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg { --a1:#f5dcd3; --a3:#d4644a; --a4:#9e2f1c; --t1:#3b140b; --t4:#ffffff; }
@media (prefers-color-scheme: dark) { svg { --a1:#4a2820; --a3:#bb4f34; --a4:#f07656; --t1:#f6e3dd; --t4:#1b0a05; } }
svg .qm { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .ac { fill:var(--a3); } svg .ad { fill:var(--a4); } svg .so { fill:var(--accsoft); stroke:var(--acc); stroke-width:1; }
svg .empty { fill:none; stroke:var(--grid); stroke-width:1; }
svg .n4 { font:700 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--t4); }
svg .nq { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .ns { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); }
svg .col { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""
FILL = {"QM": ("qm", "nq"), "C": ("ac", "n4"), "D": ("ad", "n4")}


def figure(m: dict, k: dict) -> str:
    goals = list(k["goals"])
    cols = goals + ["TC", "FM"]
    x0, xg, cw, top, rh = 24, 330, 40, 120, 26
    w = xg + cw * len(cols) + 24
    body = [
        fk.text(24, 32, "What each verification case verifies", "h"),
        fk.text(24, 54, "WP-S-09 §2: the functional safety requirements of each safety goal", "t"),
        fk.text(24, 71, "it covers, by ASIL, and the triggering conditions and modifications", "t"),
    ]
    for j, g in enumerate(cols):
        cx = xg + cw * j + cw / 2
        body.append(fk.text(cx, top - 26, g.replace("SG-0", "SG"), "col", "middle"))
        sub = k["goals"][g]["asil"] if g in k["goals"] else "SOTIF"
        body.append(fk.text(cx, top - 12, sub, "s", "middle"))
    y = top
    for c in m["cases"]:
        cov = covered(c, k)
        body.append(fk.text(x0, y + 17, c["id"], "tb"))
        body.append(fk.text(x0 + 52, y + 17, fk.fit(c["name"], xg - x0 - 60, "s"), "s"))
        for j, g in enumerate(cols):
            x = xg + cw * j
            if g == "TC":
                n, a = sum(1 for v in cov if v in k["tcs"]), None
            elif g == "FM":
                n, a = sum(1 for v in cov if v in k["fms"]), None
            else:
                rs = [k["fsrs"][v] for v in cov if v in k["fsrs"] and k["fsrs"][v]["goal"] == g]
                n = len(rs)
                a = max((r["asil"] for r in rs), key=ASILS.index) if rs else None
            if not n:
                cls, tcls = "empty", None
            elif a is None:
                cls, tcls = "so", "ns"
            else:
                cls, tcls = FILL[a]
            body.append(
                fk.el("rect", None, x=x + 2, y=y + 2, width=cw - 4, height=rh - 4, rx=3, class_=cls)
            )
            if n:
                body.append(fk.text(x + cw / 2, y + 17.5, str(n), tcls, "middle"))
        y += rh
    y += 26
    lx = x0
    for cls, label in (
        ("ad", "ASIL D requirements"),
        ("ac", "ASIL C"),
        ("qm", "QM (nominal function)"),
        ("so", "SOTIF: conditions, modifications"),
    ):
        body += [
            fk.el("rect", None, x=lx, y=y - 12, width=16, height=16, rx=3, class_=cls),
            fk.text(lx + 22, y + 1, label, "s"),
        ]
        lx += 22 + fk.width(label, "s") + 20
    y += 22
    body.append(
        fk.text(x0, y, "The number in a cell counts what the case covers in that column.", "s")
    )
    desc = "Verification cases: " + "; ".join(
        f"{c['id']} {c['name']} covers {ids(covered(c, k))}" for c in m["cases"]
    )
    return fk.svg(
        int(w), int(y + 18), "WP-S-09 Figure 2-1: verification coverage", desc + ".", body, EXTRA
    )


def card_data(m: dict, k: dict) -> list[dict]:
    """The coverage requirement by requirement: one card per safety goal, then the SOTIF measures."""
    cov = {c["id"]: covered(c, k) for c in m["cases"]}
    env = {c["id"]: c.get("env") for c in m["cases"]}
    elements = {e["id"]: e["name"] for e in fsc.load()["elements"]}

    def by(x: str) -> list[tuple[str, str | None]]:
        return [(v, env[v]) for v in cov if x in cov[v]]

    cards = []
    for g, d in k["goals"].items():
        rows = [
            {"id": f, "sub": f"{r['asil']} · {elements[r['element']]}", "cases": by(f)}
            for f, r in k["fsrs"].items()
            if r["goal"] == g
        ]
        cards.append({"id": g, "title": d["statement"], "asil": d["asil"], "rows": rows})
    for title, items, key in (
        ("Triggering conditions (WP-C-06), by category", k["tcs"], "category"),
        ("Functional modifications (WP-C-07), by type", k["fms"], "type"),
    ):
        groups: dict[str, list[str]] = {}
        for x, item in items.items():
            groups.setdefault(item[key], []).append(x)
        rows = []
        for grp, xs in groups.items():
            vcs = sorted({v for x in xs for v, _ in by(x)})
            rows.append(
                {
                    "id": grp.replace("_", " "),
                    "sub": f"{len(xs)} {'item' if len(xs) == 1 else 'items'}",
                    "cases": [(v, env[v]) for v in vcs],
                }
            )
        cards.append({"id": "SOTIF", "title": title, "rows": rows})
    return cards


def cases_csv(m: dict, k: dict) -> str:
    """Every verification case with what it verifies and its result."""
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(
        [
            "ID",
            "Verification case",
            "Environment",
            "Methods",
            "ASIL",
            "Scenarios run (WP-V-03)",
            "Functional safety requirements (WP-C-04)",
            "Triggering conditions (WP-C-06)",
            "Functional modifications (WP-C-07)",
            "Pass criterion",
            "Result",
        ]
    )
    for c in m["cases"]:
        cov = covered(c, k)
        w.writerow(
            [
                c["id"],
                c["name"],
                c.get("env") or "—",
                ", ".join(m["methods"][x] for x in c["methods"]),
                asil(c, k),
                ", ".join(c["scenarios"]) or "—",
                ids(x for x in cov if x in k["fsrs"]),
                ids(x for x in cov if x in k["tcs"]),
                ids(x for x in cov if x in k["fms"]),
                c["pass"],
                "Not run",
            ]
        )
    return buf.getvalue()


def here(md: str) -> str:
    """Text of WP-S-09 with its relative links rewritten to work from this folder."""
    md = md.replace("](verif/", "](")
    return re.sub(r"\]\((?!https?:|#|fig-|cases\.csv|verif\.|README)", "](../", md)


def readme(t: dict[str, str], doc: str) -> str:
    """The folder page: the whole system verification plan on one page."""

    def part(heading: str) -> str:
        return here(fk.section(doc, heading).strip())

    files = [
        "| File | What it holds |",
        "|---|---|",
        f"| [`{CSV.name}`]({CSV.name}) | Every verification case with its environment, methods, ASIL, the scenarios it runs, the requirements, triggering conditions and modifications it verifies, its pass criterion and result |",
        f"| [`{FIG.name}`]({FIG.name}) | Figure 2-1, what each verification case verifies |",
        f"| [`{FIG2.name}`]({FIG2.name}) | Figure 2-2, how each safety goal and SOTIF measure is verified |",
        "| [`verif.yaml`](verif.yaml) | Methods, the scenarios each environment can run, and the verification cases |",
        "| [`verif.py`](verif.py), [`vcards.py`](vcards.py) | The generator: checks the model against the functional safety concept, the triggering conditions, the modifications, the known scenarios and the test environments, and writes WP-S-09's tables and everything here |",
    ]
    lines = [
        "<!-- Generated by assurance/03-system/verif/verif.py; do not edit by hand. -->",
        "",
        "# System verification",
        "",
        "The whole system verification plan of [WP-S-09](../WP-S-09-system-verification.md) on one page: how "
        "the integrated item is verified against the [functional safety concept](../../02-concept/fsc/README.md) "
        "and the SOTIF measures, by which cases, where they run, and when each passes. It runs the known "
        "scenarios of WP-V-03 in the environments of the [integration tests](../integ/README.md). Everything "
        "here is generated by `verif.py` from `verif.yaml`; CI fails if it is stale. Everything is a draft by "
        "Claude (I0); no case has been run.",
        "",
        t["verif-summary"],
        "",
        "1. [What this covers](#1-what-this-covers)",
        "2. [Verification strategy](#2-verification-strategy)",
        "3. [Test specification](#3-test-specification)",
        "4. [Results and deviations](#4-results-and-deviations)",
        "5. [Files in this folder](#5-files-in-this-folder)",
        "",
        "## 1. What this covers",
        "",
        re.sub(
            r"<!-- BEGIN GENERATED: verif-summary .*?END GENERATED: verif-summary -->\n\n",
            "",
            part("## 1. Purpose"),
            flags=re.S,
        ),
        "",
        "## 2. Verification strategy",
        "",
        part("## 2. Verification strategy"),
        "",
        "## 3. Test specification",
        "",
        f"Every case is also in [`{CSV.name}`]({CSV.name}), which GitHub shows as a table that can be searched.",
        "",
        part("## 3. Test specification"),
        "",
        "## 4. Results and deviations",
        "",
        part("## 4. Results and deviations"),
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
        raise fk.FigureError("verif.yaml: " + "; ".join(errs))
    t = tables(m, k)
    doc = fill(DOC.read_text(encoding="utf-8"), t)
    envs = {e: f"{e} {k['envs'][e]['name']}" for e in m["runs"]}
    return {
        DOC: doc,
        FIG: figure(m, k),
        FIG2: vcards.sheet(card_data(m, k), envs),
        CSV: cases_csv(m, k),
        README: readme(t, doc),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
