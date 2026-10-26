#!/usr/bin/env python3
"""The technical safety concept of WP-S-03, generated from tsc.yaml.

Writes the generated tables of WP-S-03 (components with their derived ASIL, safety mechanisms and
their placement, redundancy and diversity, architecture verification) and Figure 2-1 (the system
architecture). A component's ASIL is the highest ASIL of the FSRs of the mechanisms it hosts or
serves; it is computed, not typed.

The model is refused when:
- an identifier is malformed or repeated, or a link or box does not fit Figure 2-1;
- a component names an element of the functional safety concept that does not exist;
- a mechanism is hosted on, or uses, a component that does not exist, implements an FSR that does
  not exist, or implements an FSR allocated to an element other than its host's;
- a rated FSR (any ASIL but QM) is implemented by no mechanism;
- a component's derived ASIL exceeds the ASIL the functional safety concept derives for its element;
- a reaction, triggering condition or decision named does not exist, or a pending decision is no
  longer open;
- a component carries an ASIL beyond its decomposed one (`also`) without a decomposition or without
  an answered decision.

    python3 tsc.py            # write WP-S-03's generated tables and Figure 2-1
    python3 tsc.py --check    # fail if either is stale or the model breaks a rule
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
    "02-concept/fsc",
    "02-concept/fallback",
    "02-concept/triggering",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import fallback  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import terms  # noqa: E402
import triggering  # noqa: E402

sys.path.insert(0, str(HERE))
import cards  # noqa: E402

MODEL = HERE / "tsc.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-03-technical-safety-concept-architecture.md"
FIG = HERE / "fig-s03-2-1-architecture.svg"
FIG3 = HERE / "fig-s03-3-1-mechanisms.svg"
CSV = HERE / "mechanisms.csv"
README = HERE / "README.md"
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    f = fsc.load()
    fb = fallback.load()
    return {
        "fsrs": {x["id"]: x for x in f["fsrs"]},
        "elements": {e["id"]: e for e in f["elements"]},
        "element_asil": fsc.element_asil(f),
        "reactions": {x["id"] for x in fb["mrms"]} | {x["id"] for x in fb["triggers"]},
        "tcs": {x["id"] for x in triggering.load()["triggers"]},
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def rank(a: str) -> int:
    return fsc.hara.ASILS.index(a)


def dec_ok(k: dict, d: str | None) -> bool:
    return k["decisions"].get(d) in ("answered", "applied")


def label(m: dict, k: dict, cid: str) -> str:
    """The ASIL shown for a component: its decomposed ASIL where the lead decided one, else the derived one."""
    c = next(x for x in m["components"] if x["id"] == cid)
    return c["decomposed"]["asil"] if c.get("decomposed") else component_asil(m, k)[cid]


def also(c: dict) -> str:
    """An ASIL a component carries beyond its decomposed one, as a table suffix."""
    a = c.get("also")
    return f"; {a['asil']} for {a['for']} ({a['decision']})" if a else ""


def component_asil(m: dict, k: dict) -> dict[str, str]:
    out = {c["id"]: "QM" for c in m["components"]}
    for s in m["mechanisms"]:
        a = max(
            (k["fsrs"][f]["asil"] for f in s["implements"] if f in k["fsrs"]),
            key=rank,
            default="QM",
        )
        for c in [s["host"]] + s.get("uses", []):
            if c in out and rank(a) > rank(out[c]):
                out[c] = a
    return out


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    def pending(i: str, x: dict) -> None:
        p = x.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )

    comps = {c["id"]: c for c in m.get("components", [])}
    for c in m.get("components", []):
        new(c["id"], r"CMP-\d\d")
        if c.get("element") not in k["elements"]:
            errs.append(f"{c['id']}: element {c.get('element')} does not exist")
        pending(c["id"], c)
    implemented: set[str] = set()
    for s in m.get("mechanisms", []):
        i = s["id"]
        new(i, r"SM-\d\d")
        for key in ("name", "does", "verify"):
            if not s.get(key):
                errs.append(f"{i}: missing {key}")
        host = comps.get(s.get("host"))
        if not host:
            errs.append(f"{i}: host {s.get('host')} does not exist")
        for c in s.get("uses") or []:
            if c not in comps:
                errs.append(f"{i}: uses {c}, which does not exist")
        for f in s.get("implements") or []:
            if f not in k["fsrs"]:
                errs.append(f"{i}: {f} does not exist")
                continue
            implemented.add(f)
            if host and k["fsrs"][f]["element"] != host["element"]:
                errs.append(
                    f"{i}: {f} is allocated to {k['fsrs'][f]['element']}, but {host['id']} is part of {host['element']}"
                )
        for r in s.get("reaction") or []:
            if r not in k["reactions"]:
                errs.append(f"{i}: reaction {r} is not a fallback trigger or MRM")
    for f, d in k["fsrs"].items():
        if d["asil"] != "QM" and f not in implemented:
            errs.append(f"{f}: rated {d['asil']} but no mechanism implements it")
    for r in m.get("redundancy", []):
        new(r["id"], r"RD-\d\d")
        for c in r.get("between") or []:
            if c not in comps:
                errs.append(f"{r['id']}: component {c} does not exist")
        for t in r.get("common") or []:
            if t not in k["tcs"]:
                errs.append(f"{r['id']}: triggering condition {t} does not exist")
        pending(r["id"], r)
    for c in m.get("components", []):
        a = c.get("also")
        if a and (not dec_ok(k, a.get("decision")) or not c.get("decomposed")):
            errs.append(f"{c['id']}: also needs a decomposed component and an answered decision")
        dec = c.get("decomposed")
        if not dec:
            continue
        p = comps.get(dec.get("with"))
        if k["decisions"].get(dec.get("decision")) not in ("answered", "applied"):
            errs.append(
                f"{c['id']}: decomposition needs an answered decision, not {dec.get('decision')}"
            )
        if not p or (p.get("decomposed") or {}).get("with") != c["id"]:
            errs.append(
                f"{c['id']}: decomposed with {dec.get('with')}, which is not decomposed with it"
            )
        if not any(
            set(r.get("between", [])) == {c["id"], dec.get("with")} for r in m.get("redundancy", [])
        ):
            errs.append(
                f"{c['id']}: no redundancy entry between it and {dec.get('with')} to show their independence"
            )
    if errs:
        return errs
    ca = component_asil(m, k)
    for c in m["components"]:
        el = k["element_asil"][c["element"]]
        if rank(ca[c["id"]]) > rank(el):
            errs.append(f"{c['id']}: derived ASIL {ca[c['id']]} exceeds its element's {el}")
    errs += route_errors(m)
    return errs


def route_errors(m: dict) -> list[str]:
    errs = []
    cts = {c["id"]: c["box"] for c in m["components"]}
    for ln in m["links"]:
        a, b = cts[ln["from"]], cts[ln["to"]]
        if "y" in ln:
            if not (a[1] < ln["y"] < a[1] + a[3] and b[1] < ln["y"] < b[1] + b[3]):
                errs.append(f"link {ln['from']}→{ln['to']}: y={ln['y']} is not within both boxes")
            continue
        x = ln["x"]
        if not (a[0] < x < a[0] + a[2] and b[0] < x < b[0] + b[2]):
            errs.append(f"link {ln['from']}→{ln['to']}: x={x} is not within both boxes")
        top, bot = (a, b) if a[1] < b[1] else (b, a)
        for cid, c in cts.items():
            if (
                cid not in (ln["from"], ln["to"])
                and c[0] <= x <= c[0] + c[2]
                and top[1] + top[3] < c[1] < bot[1]
            ):
                errs.append(f"link {ln['from']}→{ln['to']}: x={x} crosses {cid}")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    ca = component_asil(m, k)
    comps = {c["id"]: c for c in m["components"]}
    t = {}
    rows = [
        "| ID | Component | Element | In the item | ASIL | Mechanisms hosted | Serves | Waits on |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in m["components"]:
        el = k["elements"][c["element"]]
        hosted = [s["id"] for s in m["mechanisms"] if s["host"] == c["id"]]
        serves = [s["id"] for s in m["mechanisms"] if c["id"] in s.get("uses", [])]
        rows.append(
            f"| {c['id']} | {cell(c['name'])} | {c['element']} | {'Yes' if el['in_item'] else 'No'} | **{label(m, k, c['id'])}**{also(c)} "
            f"| {', '.join(hosted) or '—'} | {', '.join(serves) or '—'} | {c.get('pending', '—')} |"
        )
    t["tsc-components"] = "\n".join(rows)
    rows = [
        "| ID | Safety mechanism | Hosted on | Uses | What it does | FSRs | ASIL | Reaction |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in m["mechanisms"]:
        a = max((k["fsrs"][f]["asil"] for f in s["implements"]), key=rank)
        rows.append(
            f"| {s['id']} | {cell(s['name'])} | {s['host']} {cell(comps[s['host']]['name'])} | {', '.join(s['uses']) or '—'} "
            f"| {cell(s['does'])} | {', '.join(s['implements'])} | {a} | {', '.join(s['reaction']) or '—'} |"
        )
    t["tsc-mechanisms"] = "\n".join(rows)
    rows = [
        "| ID | Between | What | Diversity | Common triggering conditions | Waits on |",
        "|---|---|---|---|---|---|",
    ]
    for r in m["redundancy"]:
        rows.append(
            f"| {r['id']} | {', '.join(dict.fromkeys(r['between']))} | {cell(r['what'])} | {cell(r['diversity'])} "
            f"| {', '.join(r['common']) or '—'} | {r.get('pending') or r.get('decision') or '—'} |"
        )
    t["tsc-redundancy"] = "\n".join(rows)
    t["tsc-mechanism-cards"] = (
        "![Figure 3-1: one card per safety mechanism SM-01 to SM-19. Each shows the system architecture of "
        "Figure 2-1 in small with the component the mechanism runs on filled and those it uses outlined; for a "
        "time-critical mechanism, a bar dividing the binding fault tolerant time interval of WP-S-04 into time "
        "to detect, time to react and reserve, with their ranges; the reaction it starts; what it does; and the "
        f"functional safety requirements it implements.](tsc/{FIG3.name})\n\n"
        "*Figure 3-1. Where each safety mechanism runs, and how fast it must act. Budgets are the ranges WP-S-04 "
        "computes, not measurements. Drawn by [`tsc/tsc.py`](tsc/tsc.py); CI fails if it is stale. Each "
        f"mechanism's trace to its FSRs, technical safety requirements and test cases is in "
        f"[`tsc/{CSV.name}`](tsc/{CSV.name}).*"
    )
    rows = ["| Mechanism | Verified by |", "|---|---|"]
    rows += [f"| {s['id']} {cell(s['name'])} | {cell(s['verify'])} |" for s in m["mechanisms"]]
    t["tsc-verification"] = "\n".join(rows)
    rated = sum(1 for f in k["fsrs"].values() if f["asil"] != "QM")
    pend = sorted({x["pending"] for x in m["components"] + m["redundancy"] if x.get("pending")})
    d_comps = [c for c in m["components"] if label(m, k, c["id"]) == "D"]
    t["tsc-summary"] = (
        f"{len(m['components'])} system components, {len(d_comps)} of them at ASIL D, carry {len(m['mechanisms'])} "
        f"safety mechanisms that implement all {rated} rated functional safety requirements, each on a component of "
        f"the element the FSR is allocated to. {len(m['redundancy'])} redundancies, each with its diversity and the "
        f"triggering conditions they share."
        + (f" Entries marked as waiting depend on {', '.join(pend)}." if pend else "")
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/tsc/tsc.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-03 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .aD { fill:var(--accsoft); stroke:var(--acc); stroke-width:2; }
svg .aC { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.2; stroke-dasharray:5 3; }
svg .aQM { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .out { stroke-dasharray:2 2; }
svg .wire { stroke:var(--ink2); stroke-width:1.4; fill:none; }
svg .hd { fill:var(--ink2); }
svg .lab { font:500 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .sm { font:600 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--acc); }
"""


def arrow(x1: float, y1: float, x2: float, y2: float) -> list[str]:
    dx, dy = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
    tip = (
        f"M{fk.num(x2)} {fk.num(y2)} L{fk.num(x2 - 7 * dx - 4 * dy)} {fk.num(y2 - 7 * dy - 4 * dx)} "
        f"L{fk.num(x2 - 7 * dx + 4 * dy)} {fk.num(y2 - 7 * dy + 4 * dx)} Z"
    )
    return [
        fk.el(
            "path",
            None,
            d=f"M{fk.num(x1)} {fk.num(y1)} L{fk.num(x2 - 6 * dx)} {fk.num(y2 - 6 * dy)}",
            class_="wire",
        ),
        fk.el("path", None, d=tip, class_="hd"),
    ]


def span(ids: list[str]) -> str:
    nums = [int(i[3:]) for i in ids]
    if len(ids) > 2 and nums == list(range(nums[0], nums[0] + len(nums))):
        return f"{ids[0]}–{nums[-1]:02d}"
    return ", ".join(ids)


def figure(m: dict, k: dict) -> str:
    ca = component_asil(m, k)
    cts = {c["id"]: c for c in m["components"]}
    body = [
        fk.text(24, 32, "System architecture and safety mechanisms", "h"),
        fk.text(24, 54, "WP-S-03 §2: components with their derived ASIL and the safety", "t"),
        fk.text(24, 71, "mechanisms (SM) they host; arrows show the command and data paths", "t"),
    ]
    for ln in m["links"]:
        a, b = cts[ln["from"]]["box"], cts[ln["to"]]["box"]
        if "y" in ln:
            x1, x2 = (a[0], b[0] + b[2]) if a[0] > b[0] else (a[0] + a[2], b[0])
            body += arrow(x1, ln["y"], x2, ln["y"])
            if ln.get("label"):
                body.append(fk.text((x1 + x2) / 2, ln["y"] - 6, ln["label"], "lab", "middle"))
            continue
        down = a[1] < b[1]
        y1, y2 = (a[1] + a[3], b[1]) if down else (a[1], b[1] + b[3])
        body += arrow(ln["x"], y1, ln["x"], y2)
        if ln.get("label"):
            body.append(fk.text(ln["x"] + 6, (y1 + y2) / 2 + 4, ln["label"], "lab"))
    for c in m["components"]:
        x, y, w, h = c["box"]
        lab = label(m, k, c["id"])
        cls = f"a{'D' if lab.endswith('(D)') else lab}" + (
            "" if k["elements"][c["element"]]["in_item"] else " out"
        )
        body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=7, class_=cls))
        lines = fk.wrap(c["name"], w - 14, "tb")[:2]
        for n, s in enumerate(lines):
            body.append(fk.text(x + 8, y + 18 + 15 * n, s, "tb"))
        sms = [s["id"] for s in m["mechanisms"] if s["host"] == c["id"]]
        tag = label(m, k, c["id"]) + (f" · {span(sms)}" if sms else "")
        body.append(fk.text(x + 8, y + h - 9, fk.fit(tag, w - 14, "s"), "sm"))
    y = max(c["box"][1] + c["box"][3] for c in m["components"]) + 30
    legend = [
        ("aD", "ASIL D"),
        ("aC", "ASIL C"),
        ("aQM", "QM"),
        ("aD out", "Outside the item (dotted)"),
    ]
    lx = 24
    for cls, name in legend:
        body.append(fk.el("rect", None, x=lx, y=y - 13, width=26, height=18, rx=4, class_=cls))
        body.append(fk.text(lx + 34, y, name, "t"))
        lx += 34 + fk.width(name, "t") + 26
    y += 20
    desc = (
        "Components: "
        + "; ".join(
            f"{c['name']} ({label(m, k, c['id'])}) hosting {', '.join(s['id'] for s in m['mechanisms'] if s['host'] == c['id']) or 'no mechanism'}"
            for c in m["components"]
        )
        + ". Links: "
        + "; ".join(f"{cts[ln['from']]['name']} to {cts[ln['to']]['name']}" for ln in m["links"])
        + "."
    )
    return fk.svg(W, int(y), "WP-S-03 Figure 2-1: system architecture", desc, body, EXTRA)


def card_known(m: dict, k: dict) -> dict:
    fb = fallback.load()
    names = {x["id"]: x["name"] for x in fb["mrms"]}
    names.update({x["id"]: "(a fallback trigger of WP-C-12)" for x in fb["triggers"]})
    return {**k, "components_list": m["components"], "reaction_names": names}


def mechanisms_csv(m: dict, k: dict) -> str:
    """Each mechanism with its placement, budget and trace to WP-S-02, WP-S-08 and WP-S-04."""
    import csv
    import io

    import yaml

    tm, tmech = cards.timed()
    tsrs = yaml.safe_load((HERE.parent / "tsr" / "tsr.yaml").read_text(encoding="utf-8"))["tsrs"]
    its = yaml.safe_load((HERE.parent / "integ" / "integ.yaml").read_text(encoding="utf-8"))[
        "cases"
    ]
    comps = {c["id"]: c["name"] for c in m["components"]}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(
        [
            "ID",
            "Safety mechanism",
            "ASIL",
            "Runs on",
            "Uses",
            "What it does",
            "Implements (WP-C-04)",
            "Safety goals",
            "Reaction",
            "Binding FTTI (WP-S-04)",
            "Time to detect",
            "Time to react",
            "Technical safety requirements (WP-S-02)",
            "Integration test cases (WP-S-08)",
            "Verified by (WP-S-03)",
        ]
    )
    for s in m["mechanisms"]:
        a = max((k["fsrs"][f]["asil"] for f in s["implements"]), key=rank)
        b = cards.budget(s, tm, tmech)
        rs = [r["id"] for r in tsrs if r["mechanism"] == s["id"]]
        cs = [c["id"] for c in its if set(c["covers"]) & set(rs)]
        goals = sorted({k["fsrs"][f]["goal"] for f in s["implements"]})
        w.writerow(
            [
                s["id"],
                s["name"],
                a,
                f"{s['host']} {comps[s['host']]}",
                ", ".join(f"{c} {comps[c]}" for c in s.get("uses") or []) or "—",
                s["does"],
                ", ".join(s["implements"]),
                ", ".join(goals),
                ", ".join(s["reaction"]) or "—",
                f"{cards.span(b['worst'], b['best'])} ({b['goal']})" if b else "—",
                cards.span(b["worst"] * b["detect"], b["best"] * b["detect"]) if b else "—",
                cards.span(b["worst"] * b["react"], b["best"] * b["react"]) if b else "—",
                ", ".join(rs) or "—",
                ", ".join(cs) or "—",
                s["verify"],
            ]
        )
    return buf.getvalue()


def here(md: str) -> str:
    """Text of WP-S-03 with its relative links rewritten to work from this folder."""
    md = md.replace("](tsc/", "](")
    return re.sub(
        r"\]\((?!https?:|#|fig-|mechanisms\.csv|architecture\.sysml|tsc\.|README)", "](../", md
    )


def readme(m: dict, k: dict, t: dict[str, str], doc: str) -> str:
    """The folder page: the whole technical safety concept on one page."""

    def part(heading: str) -> str:
        return here(fk.section(doc, heading).strip())

    files = [
        "| File | What it holds |",
        "|---|---|",
        f"| [`{CSV.name}`]({CSV.name}) | Every safety mechanism with where it runs, its ASIL, the FSRs it implements, its reaction, its time budget, and the technical safety requirements and integration test cases that trace to it |",
        f"| [`{FIG.name}`]({FIG.name}) | Figure 2-1, the system architecture |",
        f"| [`{FIG3.name}`]({FIG3.name}) | Figure 3-1, where each safety mechanism runs and how fast it must act |",
        "| [`tsc.yaml`](tsc.yaml) | Components, links, safety mechanisms and redundancies |",
        "| [`tsc.py`](tsc.py), [`cards.py`](cards.py) | The generator: checks the model against the functional safety concept, the fallback concept and the triggering conditions, and writes WP-S-03's tables and everything here |",
        "| [`architecture.sysml`](architecture.sysml) | The same architecture as a SysML v2 textual model, for SysML v2 tools |",
        "| [`sysml.py`](sysml.py) | Its generator: writes `architecture.sysml` from `tsc.yaml` and refuses a file that does not read back to it |",
    ]
    lines = [
        "<!-- Generated by assurance/03-system/tsc/tsc.py; do not edit by hand. -->",
        "",
        "# Technical safety concept",
        "",
        "The whole technical safety concept and system architecture of "
        "[WP-S-03](../WP-S-03-technical-safety-concept-architecture.md) on one page: the components that "
        "refine the elements of the [functional safety concept](../../02-concept/fsc/README.md), the safety "
        "mechanisms placed on them and how fast each must act, the redundancies and their independence, the AI "
        "measures and how the architecture is verified. Everything here is generated by `tsc.py` from "
        "`tsc.yaml`; CI fails if it is stale. Everything is a draft by Claude (I0) until it is reviewed.",
        "",
        t["tsc-summary"],
        "",
        "1. [The architecture](#1-the-architecture)",
        "2. [Safety mechanisms](#2-safety-mechanisms)",
        "3. [Redundancy and diversity](#3-redundancy-and-diversity)",
        "4. [AI architecture measures](#4-ai-architecture-measures)",
        "5. [Architecture verification](#5-architecture-verification)",
        "6. [Files in this folder](#6-files-in-this-folder)",
        "",
        "## 1. The architecture",
        "",
        part("## 2. Architecture overview"),
        "",
        "## 2. Safety mechanisms",
        "",
        part("## 3. Safety mechanisms"),
        "",
        "## 3. Redundancy and diversity",
        "",
        part("## 4. Redundancy and diversity"),
        "",
        "## 4. AI architecture measures",
        "",
        part("## 5. AI architecture measures"),
        "",
        "## 5. Architecture verification",
        "",
        part("## 6. Architecture verification"),
        "",
        "## 6. Files in this folder",
        "",
        *files,
        "",
    ]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("tsc.yaml: " + "; ".join(errs))
    t = tables(m, k)
    doc = fill(DOC.read_text(encoding="utf-8"), t)
    return {
        DOC: doc,
        FIG: figure(m, k),
        FIG3: cards.sheet(m, card_known(m, k)),
        CSV: mechanisms_csv(m, k),
        README: terms.close(readme(m, k, t, doc), README),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
