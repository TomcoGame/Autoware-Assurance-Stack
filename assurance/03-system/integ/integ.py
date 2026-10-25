#!/usr/bin/env python3
"""The system integration test strategy and specification of WP-S-08, generated from integ.yaml.

Writes the generated tables of WP-S-08 (test environments, integration steps, test cases with the
time budgets their requirements carry, and coverage of requirements, signals and cybersecurity
requirements) and Figure 2-1 (the integration steps, what each adds, and the cases run at each).
A case's ASIL is the highest of the technical safety requirements it covers.

The model is refused when:
- an identifier is malformed or repeated, or an environment, step or method named does not exist;
- the steps do not integrate every component of WP-S-03 exactly once, or do not exercise every
  interface of WP-S-05 exactly once, or a step adds an interface before both its ends are integrated;
- a case runs at a step before everything it covers is integrated, or in an environment its step
  does not use;
- a technical safety requirement, signal or technical cybersecurity requirement is covered by no case,
  or a case covers something that does not exist;
- a requirement with a WP-S-04 budget is covered by no case that measures time, or a requirement whose
  mechanism reacts to a detected fault is covered by no fault injection;
- a pending decision is no longer open.

    python3 integ.py            # write WP-S-08's generated tables and Figure 2-1
    python3 integ.py --check    # fail if either is stale or the model breaks a rule
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
    "03-system/tsc",
    "03-system/tsr",
    "03-system/hsi",
    "03-system/secarch",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import hsi  # noqa: E402
import secarch  # noqa: E402
import tsc  # noqa: E402
import tsr  # noqa: E402

MODEL = HERE / "integ.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-08-system-integration-test.md"
FIG = HERE / "fig-s08-2-1-steps.svg"
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    k = tsr.known()
    rm = tsr.load()
    hm = hsi.load()
    sm = secarch.load()
    return {
        "tsr_known": k,
        "tsrs": {r["id"]: r for r in rm["tsrs"]},
        "signals": {s["id"]: s for s in hm["signals"]},
        "interfaces": {f["id"]: f for f in hm["interfaces"]},
        "cstrs": {r["id"]: r for r in sm["tcsrs"]},
        "components": k["components"],
        "mechanisms": k["mechanisms"],
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def needs(x: str, k: dict) -> tuple[set[str], set[str]]:
    """The components and interfaces a covered item needs integrated."""
    if x in k["tsrs"]:
        return {k["tsrs"][x]["component"]}, set()
    if x in k["cstrs"]:
        return {k["cstrs"][x]["component"]}, set()
    f = k["interfaces"][k["signals"][x]["interface"]]
    return set(f["link"]), {f["id"]}


def integrated(m: dict, upto: str) -> tuple[set[str], set[str]]:
    comps, ifs = set(), set()
    for s in m["steps"]:
        comps |= set(s["adds"])
        ifs |= set(s["interfaces"])
        if s["id"] == upto:
            break
    return comps, ifs


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    envs = {e["id"]: e for e in m.get("environments", [])}
    for e in m.get("environments", []):
        new(e["id"], r"ENV-\d")
        p = e.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{e['id']}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )
    steps = {s["id"]: s for s in m.get("steps", [])}
    comps: list[str] = []
    ifs: list[str] = []
    for s in m.get("steps", []):
        new(s["id"], r"IS-\d")
        for c in s.get("adds") or []:
            if c not in k["components"]:
                errs.append(f"{s['id']}: component {c} does not exist")
            comps.append(c)
        for e in s.get("envs") or []:
            if e not in envs:
                errs.append(f"{s['id']}: environment {e} does not exist")
        for f in s.get("interfaces") or []:
            ifs.append(f)
            if f not in k["interfaces"]:
                errs.append(f"{s['id']}: interface {f} does not exist")
            elif not set(k["interfaces"][f]["link"]) <= set(comps):
                errs.append(f"{s['id']}: {f} is exercised before both its ends are integrated")
    for c in k["components"]:
        if comps.count(c) != 1:
            errs.append(f"{c}: integrated {comps.count(c)} times; must be once")
    for f in k["interfaces"]:
        if ifs.count(f) != 1:
            errs.append(f"{f}: exercised by {ifs.count(f)} steps; must be one")
    if errs:
        return errs
    covered: dict[str, set[str]] = {}
    for c in m.get("cases", []):
        i = c["id"]
        new(i, r"IT-\d\d")
        s = steps.get(c.get("step"))
        if not s:
            errs.append(f"{i}: step {c.get('step')} does not exist")
            continue
        if c.get("env") not in (s.get("envs") or []):
            errs.append(f"{i}: environment {c.get('env')} is not one of {s['id']}'s")
        for meth in c.get("methods") or []:
            if meth not in m["methods"]:
                errs.append(f"{i}: method {meth} does not exist")
        if not c.get("pass"):
            errs.append(f"{i}: missing pass criterion")
        have_c, have_i = integrated(m, s["id"])
        for x in c.get("covers") or []:
            if x not in k["tsrs"] and x not in k["cstrs"] and x not in k["signals"]:
                errs.append(f"{i}: covers {x}, which does not exist")
                continue
            nc, ni = needs(x, k)
            if not (nc <= have_c and ni <= have_i):
                errs.append(
                    f"{i}: covers {x}, which needs {', '.join(sorted(nc | ni))} integrated by {s['id']}"
                )
            covered.setdefault(x, set()).update(c.get("methods") or [])
    for group in (k["tsrs"], k["signals"], k["cstrs"]):
        for x in group:
            if x not in covered:
                errs.append(f"{x}: covered by no integration test case")
    for x, r in k["tsrs"].items():
        if x not in covered:
            continue
        if r.get("timing") and "timing" not in covered[x]:
            errs.append(f"{x}: has a WP-S-04 budget but no case measures its time")
        if r.get("timing") == "detect" and k["mechanisms"][r["mechanism"]]["reaction"]:
            if "fault-injection" not in covered[x]:
                errs.append(f"{x}: detects faults for {r['mechanism']} but no case injects them")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def asil(c: dict, k: dict) -> str:
    rated = [tsr.asil(k["tsrs"][x], k["tsr_known"]) for x in c["covers"] if x in k["tsrs"]]
    return max(rated, key=lambda a: tsc.rank(a.split("(")[0])) if rated else "—"


def budgets(c: dict, k: dict) -> str:
    out = []
    for x in c["covers"]:
        r = k["tsrs"].get(x)
        if r and r.get("timing"):
            word = "detect" if r["timing"] == "detect" else "react"
            out.append(
                f"{x} {word} within {tsr.budget(None, k['tsr_known'], r['mechanism'], r['timing'])}"
            )
    return "; ".join(out) or "—"


def tables(m: dict, k: dict) -> dict[str, str]:
    comps = k["components"]
    t = {}
    rows = ["| ID | Environment | What it is |", "|---|---|---|"]
    for e in m["environments"]:
        wait = f" Waits on {e['pending']}." if e.get("pending") else ""
        rows.append(f"| {e['id']} | {cell(e['name'])} | {cell(e['what'])}{wait} |")
    t["integ-environments"] = "\n".join(rows)
    rows = [
        "| Step | Adds | Interfaces first exercised | Environments | Cases | Note |",
        "|---|---|---|---|---|---|",
    ]
    for s in m["steps"]:
        cases = [c["id"] for c in m["cases"] if c["step"] == s["id"]]
        rows.append(
            f"| {s['id']} {s['name']} | {', '.join(c + ' ' + comps[c]['name'] for c in s['adds'])} "
            f"| {', '.join(s['interfaces']) or '—'} | {', '.join(s['envs'])} | {', '.join(cases)} | {cell(s['note'])} |"
        )
    t["integ-steps"] = "\n".join(rows)
    rows = [
        "| ID | Test case | Step | Environment | Methods | ASIL | Covers | Time budgets | Pass criterion |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in m["cases"]:
        rows.append(
            f"| {c['id']} | {cell(c['name'])} | {c['step']} | {c['env']} | {', '.join(c['methods'])} | {asil(c, k)} "
            f"| {', '.join(c['covers'])} | {budgets(c, k)} | {cell(c['pass'])} |"
        )
    t["integ-cases"] = "\n".join(rows)
    rows = ["| Method | Cases |", "|---|---|"]
    for meth, name in m["methods"].items():
        cs = [c["id"] for c in m["cases"] if meth in c["methods"]]
        rows.append(f"| {name} | {', '.join(cs) or '—'} |")
    t["integ-methods"] = "\n".join(rows)
    n = {
        "technical safety requirements": len(k["tsrs"]),
        "interface signals": len(k["signals"]),
        "technical cybersecurity requirements": len(k["cstrs"]),
    }
    timed = sum(bool(r.get("timing")) for r in k["tsrs"].values())
    t["integ-summary"] = (
        f"{len(m['cases'])} integration test cases in {len(m['steps'])} steps cover all "
        + ", ".join(f"{v} {name}" for name, v in n.items())
        + f". The {timed} requirements with a WP-S-04 budget are measured for time, and every fault-detecting "
        f"mechanism is tested by fault injection. No test has been run."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/integ/integ.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-08 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .st { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.4; }
svg .done { fill:var(--card); stroke:var(--grid); stroke-width:1; }
"""


def figure(m: dict, k: dict) -> str:
    comps = k["components"]
    n = len(m["steps"])
    gap, x0 = 12, 24
    w = (W - 2 * x0 - gap * (n - 1)) / n
    top = 96
    body = [
        fk.text(24, 32, "How the item is put together and tested", "h"),
        fk.text(24, 54, "WP-S-08 §2: each step adds components (blue) to what is already", "t"),
        fk.text(24, 71, "integrated (grey), and runs its cases", "t"),
    ]
    ys = []
    for i, s in enumerate(m["steps"]):
        x = x0 + i * (w + gap)
        body.append(fk.text(x, top, s["id"], "tb"))
        body.append(fk.text(x, top + 16, fk.fit(s["name"], w, "s"), "s"))
        y = top + 28
        before, _ = integrated(m, m["steps"][i - 1]["id"]) if i else (set(), set())
        for c in comps:
            if c in before or c in s["adds"]:
                cls = "st" if c in s["adds"] else "done"
                lines = fk.wrap(comps[c]["name"], w - 12, "s")[:2]
                h = 8 + 14 * len(lines)
                body.append(
                    fk.el(
                        "rect", None, x=fk.num(x), y=y, width=fk.num(w), height=h, rx=4, class_=cls
                    )
                )
                for n, ln in enumerate(lines):
                    body.append(fk.text(x + 6, y + 15 + 14 * n, ln, "s"))
                y += h + 4
        cases = [c["id"] for c in m["cases"] if c["step"] == s["id"]]
        y += 8
        for ln in fk.wrap(", ".join(cases), w, "s"):
            body.append(fk.text(x, y + 10, ln, "s"))
            y += 14
        ys.append(y)
    y = max(ys) + 24
    desc = "Integration steps: " + "; ".join(
        f"{s['id']} {s['name']} adds {', '.join(comps[c]['name'] for c in s['adds'])} and runs "
        f"{', '.join(c['id'] for c in m['cases'] if c['step'] == s['id'])}"
        for s in m["steps"]
    )
    return fk.svg(W, int(y), "WP-S-08 Figure 2-1: integration steps", desc + ".", body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("integ.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
