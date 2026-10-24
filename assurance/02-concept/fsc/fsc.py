#!/usr/bin/env python3
"""The functional safety concept of WP-C-04, generated from fsc.yaml and the HARA model.

Writes the generated tables of WP-C-04 (safety goals with their FSRs, the FSRs, the elements)
and Figure 4-1 (which element carries which safety goal, at what ASIL). Safety goal ASILs come
from ../hara/hara.yaml through hara.py; element ASILs are derived from the FSRs allocated to them.

The model is refused when:
- an FSR's identifier does not start with its safety goal's number (FSR-04.02 belongs to SG-04),
  or an identifier is malformed or repeated;
- an FSR names a safety goal or element that does not exist;
- an FSR's ASIL is neither QM (a nominal function supporting the goal) nor its goal's ASIL
  (ASIL decomposition is recorded in WP-A-01 and would need an explicit field here);
- a safety goal has no FSR at its own ASIL;
- an element outside the item has no assumption (AOU) in WP-C-01 §8, or names one that does not
  exist there; an element carries no FSR;
- an FSR marked pending names a decision that is not open or queued in the decision register.

    python3 fsc.py            # write WP-C-04's generated tables and Figure 4-1
    python3 fsc.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "01-management" / "decisions"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "hara"))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import hara  # noqa: E402

sys.path.insert(0, str(HERE))
import envelope  # noqa: E402

MODEL = HERE / "fsc.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-04-functional-safety-concept.md"
ITEM = ASSURANCE / "02-concept" / "WP-C-01-item-definition.md"
FIG = HERE / "fig-c04-4-1-allocation.svg"
FIG2 = HERE / "fig-c04-4-2-goals.svg"
CSV = HERE / "fsrs.csv"
README = HERE / "README.md"
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def aous() -> set[str]:
    head, rows = fk.table(fk.section(ITEM.read_text(encoding="utf-8"), "## 8. Assumptions"), "ID")
    return {fk.plain(r[0]) for r in rows}


def goals() -> dict[str, dict]:
    m = hara.load()
    ga = hara.goal_asil(m, hara.rated(m))
    return {g["id"]: {**g, "asil": ga[g["id"]]} for g in m["goals"]}


def check(m: dict, sg: dict[str, dict], known_aou: set[str], decisions: list[dict]) -> list[str]:
    errs: list[str] = []
    els = {e["id"]: e for e in m.get("elements", [])}
    status = {d["id"]: d["status"] for d in decisions}
    seen: set[str] = set()
    for e in m.get("elements", []):
        if not re.fullmatch(r"EL-\d\d", str(e.get("id"))):
            errs.append(f"element {e.get('id')}: id must look like EL-01")
        if not e.get("in_item"):
            if not e.get("aou"):
                errs.append(f"{e['id']}: an element outside the item needs an assumption (aou)")
            elif e["aou"] not in known_aou:
                errs.append(f"{e['id']}: assumption {e['aou']} is not in WP-C-01 §8")
    for f in m.get("fsrs", []):
        i = str(f.get("id"))
        if not re.fullmatch(r"FSR-\d\d\.\d\d", i):
            errs.append(f"{i}: id must look like FSR-01.01")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        g = f.get("goal")
        if g not in sg:
            errs.append(f"{i}: safety goal {g} does not exist")
            continue
        if not i.startswith("FSR-" + g[3:] + "."):
            errs.append(f"{i}: its number must start with its safety goal's ({g})")
        if f.get("element") not in els:
            errs.append(f"{i}: element {f.get('element')} does not exist")
        if f.get("asil") not in ("QM", sg[g]["asil"]):
            errs.append(f"{i}: ASIL {f.get('asil')} is neither QM nor {g}'s ASIL {sg[g]['asil']}")
        for k in ("text", "verify"):
            if not f.get(k):
                errs.append(f"{i}: missing {k}")
        p = f.get("pending")
        if p and status.get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {status.get(p, 'not in the register')}; apply the decision"
            )
    for g, d in sg.items():
        if not any(f.get("goal") == g and f.get("asil") == d["asil"] for f in m.get("fsrs", [])):
            errs.append(f"{g}: no FSR at its ASIL {d['asil']}")
    for e in els:
        if not any(f.get("element") == e for f in m.get("fsrs", [])):
            errs.append(f"{e}: no FSR is allocated to it")
    return errs


def element_asil(m: dict) -> dict[str, str]:
    return {
        e["id"]: max(
            (f["asil"] for f in m["fsrs"] if f["element"] == e["id"]),
            key=hara.ASILS.index,
            default="QM",
        )
        for e in m["elements"]
    }


def cell(s: str) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, sg: dict[str, dict]) -> dict[str, str]:
    els = {e["id"]: e for e in m["elements"]}
    ea = element_asil(m)
    t = {}
    rows = [
        "| Safety goal | ASIL | Safe state | FSRs at the goal's ASIL | Supporting QM FSRs |",
        "|---|---|---|---|---|",
    ]
    for g, d in sg.items():
        rated = [f["id"] for f in m["fsrs"] if f["goal"] == g and f["asil"] != "QM"]
        qm = [f["id"] for f in m["fsrs"] if f["goal"] == g and f["asil"] == "QM"]
        rows.append(
            f"| {g} {cell(d['statement'])} | **{d['asil']}** | {cell(d['safe_state'])} | {', '.join(rated)} | {', '.join(qm) or '—'} |"
        )
    t["fsc-goals"] = "\n".join(rows)
    rows = ["| ID | Requirement | ASIL | Allocated to | Verified by |", "|---|---|---|---|---|"]
    for f in m["fsrs"]:
        rows.append(
            f"| {f['id']} | {cell(f['text'])} | {f['asil']} | {f['element']} {cell(els[f['element']]['name'])} | {cell(f['verify'])} |"
        )
    t["fsc-fsrs"] = "\n".join(rows)
    rows = [
        "| ID | Element | In the item | Derived ASIL | Role | Assumption | FSRs |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in m["elements"]:
        n = sum(1 for f in m["fsrs"] if f["element"] == e["id"])
        rows.append(
            f"| {e['id']} | {cell(e['name'])} | {'Yes' if e['in_item'] else 'No'} | **{ea[e['id']]}** | {cell(e['role'])} | {e.get('aou', '—')} | {n} |"
        )
    t["fsc-elements"] = "\n".join(rows)
    n_rated = sum(1 for f in m["fsrs"] if f["asil"] != "QM")
    pend = sorted({f["pending"] for f in m["fsrs"] if f.get("pending")})
    t["fsc-summary"] = (
        f"{len(m['fsrs'])} functional safety requirements for {len(sg)} safety goals: {n_rated} rated, "
        f"{len(m['fsrs']) - n_rated} QM supporting the nominal function. {len(m['elements'])} elements, "
        f"{sum(1 for e in m['elements'] if e['in_item'])} of them in the item. "
        + (
            f"Requirements marked Proposed wait on {', '.join(pend)}."
            if pend
            else "No requirement waits on a decision."
        )
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/fsc/fsc.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-04 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


def figure(m: dict, sg: dict[str, dict]) -> str:
    els = m["elements"]
    ea = element_asil(m)
    x0, xg, top = 24, 248, 144
    cw = (W - 24 - xg) / len(els)
    rh = 30
    body = [
        fk.text(24, 32, "Which element carries which safety goal", "h"),
        fk.text(24, 54, "WP-C-04 §4: FSRs per goal and element, shaded by their ASIL;", "t"),
        fk.text(24, 71, "a number is the count of FSRs in that cell", "t"),
    ]
    outside = [j for j, e in enumerate(els) if not e["in_item"]]
    if outside:  # the elements outside the item, framed together
        a, b = min(outside), max(outside)
        body.append(
            fk.el(
                "rect",
                None,
                x=fk.num(xg + cw * a + 1),
                y=top - 50,
                width=fk.num(cw * (b - a + 1) - 2),
                height=50 + rh * len(sg) + 6,
                rx=6,
                class_="outcol",
            )
        )
        body.append(fk.text(xg + cw * a + 8, top - 38, "outside the item", "s"))
    for j, e in enumerate(els):
        cx = xg + cw * j + cw / 2
        body.append(fk.text(cx, top - 18, e["id"][3:], "col", "middle"))
        cls, tcls = hara.FILL[ea[e["id"]]]
        body.append(
            fk.el(
                "rect", None, x=fk.num(cx - 11), y=top - 13, width=22, height=12, rx=3, class_=cls
            )
        )
    body.append(fk.text(xg - 8, top - 18, "EL-", "col", "end"))
    body.append(fk.text(xg - 8, top - 4, "element ASIL", "s", "end"))
    y = top + 4
    for i, (g, d) in enumerate(sg.items()):
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
        body.append(fk.text(x0, y + 19, g, "tb"))
        body.append(fk.text(x0 + 50, y + 19, f"ASIL {d['asil']}", "s"))
        for j, e in enumerate(els):
            fs = [f for f in m["fsrs"] if f["goal"] == g and f["element"] == e["id"]]
            if not fs:
                continue
            top_asil = max((f["asil"] for f in fs), key=hara.ASILS.index)
            cls, tcls = hara.FILL[top_asil]
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(xg + cw * j + 3),
                    y=fk.num(y + 4),
                    width=fk.num(cw - 6),
                    height=rh - 8,
                    rx=4,
                    class_=cls,
                )
            )
            body.append(fk.text(xg + cw * j + cw / 2, y + 20, str(len(fs)), tcls, "middle"))
        y += rh
    y += 28
    x = x0
    for a in hara.ASILS:
        cls, tcls = hara.FILL[a]
        label = "QM" if a == "QM" else f"ASIL {a}"
        body += [
            fk.el("rect", None, x=x, y=fk.num(y - 13), width=22, height=18, rx=4, class_=cls),
            fk.text(x + 28, y, label, "t"),
        ]
        x += 28 + fk.width(label, "t") + 16
    y += 26
    for k, e in enumerate(els):
        col, row = k % 2, k // 2
        body.append(fk.text(x0 + col * 300, y + row * 17, f"{e['id']} {e['name']}", "s"))
    y += 17 * ((len(els) + 1) // 2) + 8
    desc = (
        "Functional safety requirements by safety goal and element: "
        + "; ".join(
            f"{g} (ASIL {d['asil']}): "
            + ", ".join(
                f"{e['name']} {sum(1 for f in m['fsrs'] if f['goal'] == g and f['element'] == e['id'])}"
                for e in els
                if any(f["goal"] == g and f["element"] == e["id"] for f in m["fsrs"])
            )
            for g, d in sg.items()
        )
        + ". Element ASILs: "
        + ", ".join(f"{e['name']} {ea[e['id']]}" for e in els)
        + "."
    )
    extra = (
        hara.EXTRA
        + "svg .outcol { fill:none; stroke:var(--ink3); stroke-width:1; stroke-dasharray:3 3; }\n"
    )
    return fk.svg(
        W, int(y), "WP-C-04 Figure 4-1: allocation of safety goals to elements", desc, body, extra
    )


def trace() -> dict[str, dict[str, list[str]]]:
    """For each FSR: the safety mechanisms (WP-S-03) that implement it, the technical safety
    requirements (WP-S-02) that refine it and the verification cases (WP-S-09) that verify it."""
    import yaml

    sys.path.insert(0, str(ASSURANCE / "03-system" / "verif"))
    import verif

    out: dict[str, dict[str, list[str]]] = {}

    def add(fsr: str, key: str, x: str) -> None:
        out.setdefault(fsr, {"sm": [], "tsr": [], "vc": []})[key].append(x)

    sys_dir = ASSURANCE / "03-system"
    for sm in yaml.safe_load((sys_dir / "tsc" / "tsc.yaml").read_text(encoding="utf-8"))[
        "mechanisms"
    ]:
        for f in sm.get("implements") or []:
            add(f, "sm", sm["id"])
    for r in yaml.safe_load((sys_dir / "tsr" / "tsr.yaml").read_text(encoding="utf-8"))["tsrs"]:
        for f in r.get("fsrs") or []:
            add(f, "tsr", r["id"])
    vm, vk = verif.load(), verif.known()
    for c in vm["cases"]:
        for x in sorted(verif.covered(c, vk)):
            if x.startswith("FSR-"):
                add(x, "vc", c["id"])
    return out


def to_csv(header: list[str], data: list[list[str]]) -> str:
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(data)
    return buf.getvalue()


def fsrs_csv(m: dict, sg: dict[str, dict]) -> str:
    els = {e["id"]: e for e in m["elements"]}
    tr = trace()
    rows = []
    for f in m["fsrs"]:
        t = tr.get(f["id"], {"sm": [], "tsr": [], "vc": []})
        rows.append(
            [
                f["id"],
                f"{f['goal']} {sg[f['goal']]['statement']}",
                f["asil"],
                f"{f['element']} {els[f['element']]['name']}",
                f["text"],
                f["verify"],
                ", ".join(t["sm"]) or "—",
                ", ".join(t["tsr"]) or "—",
                ", ".join(t["vc"]) or "—",
            ]
        )
    return to_csv(
        [
            "ID",
            "Safety goal",
            "ASIL",
            "Allocated to",
            "Requirement",
            "To be verified by (WP-C-04)",
            "Safety mechanisms (WP-S-03)",
            "Technical safety requirements (WP-S-02)",
            "Verification cases (WP-S-09)",
        ],
        rows,
    )


def here(md: str) -> str:
    """Text of WP-C-04 with its relative links rewritten to work from this folder."""
    md = re.sub(r"\]\(fsc/", "](", md)
    return re.sub(r"\]\((?!https?:|#|\.\./\.\./|fig-|fsrs|README)", "](../", md)


def readme(m: dict, sg: dict[str, dict], t: dict[str, str]) -> str:
    """The folder page: the whole functional safety concept on one page."""
    doc = DOC.read_text(encoding="utf-8")

    def part(heading: str) -> str:
        body = fk.section(doc, heading).strip()
        return here(body)

    files = [
        "| File | What it holds |",
        "|---|---|",
        "| [`fsrs.csv`](fsrs.csv) | Every functional safety requirement with its goal, ASIL, element, how WP-C-04 says to verify it, and the safety mechanisms, technical safety requirements and verification cases that trace to it |",
        f"| [`{FIG.name}`]({FIG.name}) | Figure 4-1, which element carries which safety goal |",
        f"| [`{FIG2.name}`]({FIG2.name}) | Figure 4-2, how the concept holds each safety goal |",
        "| [`fsc.yaml`](fsc.yaml) | The elements and the functional safety requirements |",
        "| [`fsc.py`](fsc.py), [`envelope.py`](envelope.py) | The generator: checks the model against the HARA, the item definition and the decision register, and writes WP-C-04's tables and everything here |",
    ]
    lines = [
        "<!-- Generated by assurance/02-concept/fsc/fsc.py; do not edit by hand. -->",
        "",
        "# Functional safety concept",
        "",
        "The whole functional safety concept of [WP-C-04](../WP-C-04-functional-safety-concept.md) on one "
        "page: the item and its elements, how the concept works, the safety goals it meets, which element "
        "carries what, every functional safety requirement and how each goal is held. Everything here is "
        "generated by `fsc.py` from `fsc.yaml` and the HARA; CI fails if it is stale. Everything is a draft "
        "by Claude (I0) until it is reviewed.",
        "",
        t["fsc-summary"],
        "",
        "1. [The item](#1-the-item)",
        "2. [The concept](#2-the-concept)",
        "3. [Safety goals](#3-safety-goals)",
        "4. [Allocation to elements](#4-allocation-to-elements)",
        "5. [How each goal is held](#5-how-each-goal-is-held)",
        "6. [Functional safety requirements](#6-functional-safety-requirements)",
        "7. [Safe states, warning and degradation](#7-safe-states-warning-and-degradation)",
        "8. [Assumptions on other elements](#8-assumptions-on-other-elements)",
        "9. [Files in this folder](#9-files-in-this-folder)",
        "",
        "## 1. The item",
        "",
        "![The item boundary: inside it the sensors, the Autoware computer and the safety monitor; outside it, "
        "on the left, the HD map data, the update backend, the remote operations centre and the passengers; on "
        "the right, the vehicle platform with its drive-by-wire system, the power supply and the other road "
        "users. Arrows numbered I-01 to I-13 show what crosses the boundary.](../figures/fig-c01-5-1-boundary.svg)",
        "",
        "*The item and its boundary, from [WP-C-01](../WP-C-01-item-definition.md) §5. The concept places "
        "its requirements on the elements below.*",
        "",
        here(t["fsc-elements"]),
        "",
        "## 2. The concept",
        "",
        part("## 2. The concept"),
        "",
        "## 3. Safety goals",
        "",
        "The safety goals come from the [HARA](../hara/README.md), with the ASIL of their worst hazardous "
        "event. Each has requirements at its own ASIL; QM requirements support the nominal function.",
        "",
        t["fsc-goals"],
        "",
        "## 4. Allocation to elements",
        "",
        "![Figure 4-1: a grid with the nine safety goals SG-01 to SG-09 as rows and the nine elements EL-01 to "
        "EL-09 as columns; each cell shows how many functional safety requirements of that goal are allocated "
        "to that element, shaded by their ASIL. The safety monitor (EL-02) carries requirements for every "
        f"goal. Elements outside the item are framed together with a dashed line.]({FIG.name})",
        "",
        "*Figure 4-1. Which element carries which safety goal. Each element's ASIL is the highest of the "
        "requirements allocated to it.*",
        "",
        "## 5. How each goal is held",
        "",
        "One card per safety goal: what Autoware or a remote operator commands when it goes wrong (red, "
        "dashed), the bound the safety envelope sets (amber), and what reaches the vehicle through the "
        "safety monitor (blue). Under it, the hazard on the road: where the faulty command would take the "
        "vehicle, where the monitor steps in, and the safe state the item reaches instead. The cards are "
        "schematic; they explain the concept and are not simulation results.",
        "",
        "![Figure 4-2: nine cards, one per safety goal SG-01 to SG-09. Each shows a chart of the faulty "
        "command, the envelope bound and what the monitor passes to the vehicle over time, a top-down scene "
        "with the path the faulty command would take, where the monitor steps in and the safe state reached, "
        f"and the rated requirements by the element that carries them.]({FIG2.name})",
        "",
        "## 6. Functional safety requirements",
        "",
        "Every requirement, with the safety mechanisms, technical safety requirements and verification cases "
        "that trace to it, is in [`fsrs.csv`](fsrs.csv), which GitHub shows as a table that can be searched.",
        "",
        here(t["fsc-fsrs"]),
        "",
        "## 7. Safe states, warning and degradation",
        "",
        part("## 6. Safe states, warning and degradation"),
        "",
        "## 8. Assumptions on other elements",
        "",
        part("## 7. Assumptions on other elements"),
        "",
        "## 9. Files in this folder",
        "",
        *files,
        "",
    ]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    m, sg = load(), goals()
    errs = check(m, sg, aous(), check_decisions.load()) + envelope.check(sg)
    if errs:
        raise fk.FigureError("fsc.yaml: " + "; ".join(errs))
    t = tables(m, sg)
    els = {e["id"]: e for e in m["elements"]}
    return {
        DOC: fill(DOC.read_text(encoding="utf-8"), t),
        FIG: figure(m, sg),
        FIG2: envelope.sheet(m, sg, els),
        CSV: fsrs_csv(m, sg),
        README: readme(m, sg, t),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
