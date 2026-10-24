#!/usr/bin/env python3
"""The technical safety requirements of WP-S-02, generated from tsr.yaml.

Writes the generated tables of WP-S-02 (parameters, requirements, mechanisms with their detection,
reaction and fallback, allocation to components and to hardware or software, verification) and
Figure 4-1 (requirements per component and ASIL). A requirement's ASIL is the highest ASIL of the
FSRs it refines; on a component the lead decided to decompose (WP-S-03), a requirement refining an
FSR of the decomposed ASIL takes the decomposed ASIL instead. Timing budgets and margins are read
from WP-S-04, not typed.

The model is refused when:
- an identifier is malformed or repeated, or does not carry its mechanism's number;
- a requirement names a mechanism that is not in WP-S-03, sits on a component that is neither the
  mechanism's host nor one it uses, refines an FSR the mechanism does not implement, has an unknown
  allocation, or misses its text or verification;
- an FSR a mechanism implements is refined by none of its requirements, or a mechanism has none;
- a requirement claims a timing budget its mechanism does not have in WP-S-04, or a time-critical
  mechanism has no timed requirement;
- a parameter is unused, has no value source, or names a goal or mechanism the timing model lacks;
- a requirement on a decomposed component has an ASIL that WP-S-03 does not show for it;
- a parameter's value has no answered decision behind it;
- a decision named does not exist, or a pending decision is no longer open.

    python3 tsr.py            # write WP-S-02's generated tables and Figure 4-1
    python3 tsr.py --check    # fail if either is stale or the model breaks a rule
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
    "03-system/tsc",
    "03-system/timing",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import timing  # noqa: E402
import tsc  # noqa: E402

MODEL = HERE / "tsr.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-02-technical-safety-requirements.md"
FIG = HERE / "fig-s02-4-1-allocation.svg"
ALLOC = ("software", "hardware", "both")
KEYS = {"id", "mechanism", "component", "alloc", "text", "fsrs", "timing", "params", "pending"}
KEYS |= {"verify"}
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    t = tsc.load()
    tk = tsc.known()
    tm = timing.load()
    return {
        "tsc": t,
        "tsc_known": tk,
        "timing": tm,
        "fsrs": tk["fsrs"],
        "elements": tk["elements"],
        "mechanisms": {s["id"]: s for s in t["mechanisms"]},
        "components": {c["id"]: c for c in t["components"]},
        "timed": {s["id"]: s for s in tm["mechanisms"]},
        "margins": {g["id"]: g for g in tm["goals"] if "margin" in g},
        "decisions": tk["decisions"],
        "choices": {
            d["id"]: d["answer"]["choice"] for d in check_decisions.load() if d.get("answer")
        },
    }


def asil(r: dict, k: dict) -> str:
    """The ASIL of a requirement: its FSRs' highest, or the decomposed ASIL where it applies."""
    a = max((k["fsrs"][f]["asil"] for f in r["fsrs"]), key=tsc.rank)
    dec = k["components"][r["component"]].get("decomposed")
    if dec and dec["asil"].endswith(f"({a})"):
        return dec["asil"]
    return a


def waits(r: dict, params: dict[str, dict]) -> list[str]:
    """Decisions a requirement waits on: its own, and those of the parameters it uses."""
    out = [r["pending"]] if r.get("pending") else []
    for p in r.get("params") or []:
        d = params[p].get("pending")
        if d and d not in out:
            out.append(d)
    return out


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    def pending(i: str, d: str | None) -> None:
        if d and k["decisions"].get(d) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {d}, which is {k['decisions'].get(d, 'not in the register')}; apply the decision"
            )

    params = {p["id"]: p for p in m.get("parameters", [])}
    for p in m.get("parameters", []):
        new(p["id"], r"P-\d\d")
        if not p.get("name"):
            errs.append(f"{p['id']}: missing name")
        sources = [x for x in ("margin", "budget", "pending", "source", "value") if p.get(x)]
        if len(sources) != 1:
            errs.append(f"{p['id']}: needs exactly one of margin, budget, pending, source or value")
        if bool(p.get("value")) != bool(p.get("decision")):
            errs.append(
                f"{p['id']}: a value needs the decision that set it, and only a value has one"
            )
        if p.get("decision") and k["decisions"].get(p["decision"]) not in ("answered", "applied"):
            errs.append(f"{p['id']}: {p['decision']} is not an answered decision")
        if p.get("margin") and p["margin"] not in k["margins"]:
            errs.append(f"{p['id']}: {p['margin']} has no margin in WP-S-04")
        if p.get("budget") and p["budget"] not in k["timed"]:
            errs.append(f"{p['id']}: {p['budget']} has no budget in WP-S-04")
        pending(p["id"], p.get("pending"))
    used: set[str] = set()
    refined: dict[str, set[str]] = {}
    timed: set[str] = set()
    for r in m.get("tsrs", []):
        i = r.get("id")
        new(i, r"TSR-\d\d\.\d\d")
        for key in set(r) - KEYS:
            errs.append(f"{i}: unknown key {key}")
        for key in ("text", "verify", "fsrs"):
            if not r.get(key):
                errs.append(f"{i}: missing {key}")
        s = k["mechanisms"].get(r.get("mechanism"))
        if not s:
            errs.append(f"{i}: mechanism {r.get('mechanism')} is not in WP-S-03")
            continue
        if str(i)[4:6] != s["id"][3:]:
            errs.append(f"{i}: does not carry the number of {s['id']}")
        if r.get("component") not in [s["host"]] + s.get("uses", []):
            errs.append(
                f"{i}: on {r.get('component')}, which is neither the host of {s['id']} nor one it uses"
            )
        if r.get("alloc") not in ALLOC:
            errs.append(f"{i}: alloc must be one of {', '.join(ALLOC)}")
        for f in r.get("fsrs") or []:
            if f not in s["implements"]:
                errs.append(f"{i}: refines {f}, which {s['id']} does not implement")
            refined.setdefault(s["id"], set()).add(f)
        if r.get("timing"):
            if r["timing"] not in ("detect", "react"):
                errs.append(f"{i}: timing must be detect or react")
            if s["id"] not in k["timed"]:
                errs.append(f"{i}: {s['id']} has no budget in WP-S-04")
            timed.add(s["id"])
        for p in r.get("params") or []:
            if p not in params:
                errs.append(f"{i}: parameter {p} does not exist")
            used.add(p)
        pending(i, r.get("pending"))
        c = k["components"].get(r.get("component"), {})
        if c.get("decomposed") and r.get("fsrs") and all(f in k["fsrs"] for f in r["fsrs"]):
            a = asil(r, k)
            if a != c["decomposed"]["asil"] and a != (c.get("also") or {}).get("asil"):
                errs.append(
                    f"{i}: ASIL {a} on {c['id']}, which WP-S-03 shows at {c['decomposed']['asil']} only"
                )
    for sid, s in k["mechanisms"].items():
        if sid not in refined:
            errs.append(f"{sid}: no technical safety requirement")
            continue
        for f in s["implements"]:
            if f not in refined[sid]:
                errs.append(f"{sid}: {f} is refined by none of its requirements")
    for sid in k["timed"]:
        if sid not in timed:
            errs.append(f"{sid}: time-critical in WP-S-04 but no requirement has a timing budget")
    for p in params:
        if p not in used:
            errs.append(f"{p}: used by no requirement")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def budget(m: dict, k: dict, sid: str, part: str) -> str:
    lo, hi, _ = timing.bound(k["timing"], k["timed"][sid])
    share = k["timing"]["allocation"][part]
    return timing.span(lo * share, hi * share)


def value(p: dict, m: dict, k: dict) -> str:
    if p.get("margin"):
        return f"{k['margins'][p['margin']]['margin']:g} m, the margin of {p['margin']} (proposed, WP-S-04 §2)"
    if p.get("budget"):
        return f"{budget(m, k, p['budget'], 'detect')}, the detection budget of {p['budget']} (WP-S-04 §4)"
    if p.get("pending"):
        return f"Waits on {p['pending']}"
    if p.get("value"):
        return (
            f"{cell(p['value'])} ({p['decision']} {k['choices'].get(p['decision'], '')})".replace(
                " )", ")"
            )
        )
    return cell(p["source"])


def tables(m: dict, k: dict) -> dict[str, str]:
    params = {p["id"]: p for p in m["parameters"]}
    comps = k["components"]
    t = {}
    rows = ["| ID | Parameter | Value or source | Used by |", "|---|---|---|---|"]
    for p in m["parameters"]:
        users = [r["id"] for r in m["tsrs"] if p["id"] in (r.get("params") or [])]
        rows.append(f"| {p['id']} | {cell(p['name'])} | {value(p, m, k)} | {', '.join(users)} |")
    t["tsr-parameters"] = "\n".join(rows)
    rows = [
        "| ID | Technical safety requirement | Component | ASIL | Refines | Time | Waits on |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in m["tsrs"]:
        tm = (
            f"{'Detect' if r['timing'] == 'detect' else 'React'} within {budget(m, k, r['mechanism'], r['timing'])}"
            if r.get("timing")
            else "—"
        )
        rows.append(
            f"| {r['id']} | {cell(r['text'])} | {r['component']} {cell(comps[r['component']]['name'])} "
            f"| {asil(r, k)} | {', '.join(r['fsrs'])} | {tm} | {', '.join(waits(r, params)) or '—'} |"
        )
    t["tsr-requirements"] = "\n".join(rows)
    rows = [
        "| Mechanism | Requirements | Detection budget | Reaction budget | Reaction |",
        "|---|---|---|---|---|",
    ]
    for s in k["tsc"]["mechanisms"]:
        ids = [r["id"] for r in m["tsrs"] if r["mechanism"] == s["id"]]
        tb = s["id"] in k["timed"]
        rows.append(
            f"| {s['id']} {cell(s['name'])} | {', '.join(ids)} "
            f"| {budget(m, k, s['id'], 'detect') if tb else '—'} | {budget(m, k, s['id'], 'react') if tb else '—'} "
            f"| {', '.join(s['reaction']) or 'Prevents; no reaction of its own'} |"
        )
    t["tsr-mechanisms"] = "\n".join(rows)
    rows = [
        "| Component | Element | Developed by | Software | Hardware | Both | ASILs |",
        "|---|---|---|---|---|---|---|",
    ]
    for cid, c in comps.items():
        rs = [r for r in m["tsrs"] if r["component"] == cid]
        if not rs:
            continue
        inside = k["elements"][c["element"]]["in_item"]
        n = {a: sum(r["alloc"] == a for r in rs) for a in ALLOC}
        asils = sorted({asil(r, k) for r in rs}, key=lambda a: -tsc.rank(a[0]))
        rows.append(
            f"| {cid} {cell(c['name'])} | {c['element']} | {'The project' if inside else 'Supplier, under the DIA'} "
            f"| {n['software'] or '—'} | {n['hardware'] or '—'} | {n['both'] or '—'} | {', '.join(asils)} |"
        )
    t["tsr-allocation"] = "\n".join(rows)
    rows = ["| Requirement | Verification | Level |", "|---|---|---|"]
    for r in m["tsrs"]:
        inside = k["elements"][comps[r["component"]]["element"]]["in_item"]
        rows.append(
            f"| {r['id']} | {cell(r['verify'])} | {'System (WP-S-08, WP-S-09)' if inside else 'Supplier evidence, then system'} |"
        )
    t["tsr-verification"] = "\n".join(rows)
    pend = sorted({d for r in m["tsrs"] for d in waits(r, params)})
    n_wait = sum(bool(waits(r, params)) for r in m["tsrs"])
    sup = sum(not k["elements"][comps[r["component"]]["element"]]["in_item"] for r in m["tsrs"])
    t["tsr-summary"] = (
        f"{len(m['tsrs'])} technical safety requirements refine the {len(k['fsrs']) - sum(f['asil'] == 'QM' for f in k['fsrs'].values())} "
        f"rated FSRs through the {len(k['mechanisms'])} safety mechanisms of WP-S-03, on {len({r['component'] for r in m['tsrs']})} "
        f"components; {sup} of them fall to suppliers under the DIA. {sum(bool(r.get('timing')) for r in m['tsrs'])} carry a "
        f"detection or reaction budget from WP-S-04. {len(m['parameters'])} parameters set the envelope, "
        f"{sum(bool(p.get('decision')) for p in m['parameters'])} of them decided by the lead; "
        + (
            f"{n_wait} requirements wait on {', '.join(pend)}."
            if pend
            else "no requirement waits on an open decision."
        )
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/tsr/tsr.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-02 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .a-d { fill:var(--bad); } svg .a-c { fill:var(--amb); }
svg .a-b { fill:var(--acc); } svg .a-bd { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.4; }
svg .a-x { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; }
svg .sup { fill:none; stroke:var(--ink3); stroke-width:1; stroke-dasharray:4 3; }
"""
# Fill per ASIL, darkest for the highest; a decomposed ASIL is outlined, not filled.
SHADE = {"D": "a-d", "C": "a-c", "B": "a-b", "B(D)": "a-bd"}


def figure(m: dict, k: dict) -> str:
    comps = k["components"]
    order = [cid for cid in comps if any(r["component"] == cid for r in m["tsrs"])]
    counts = {
        cid: {a: sum(asil(r, k) == a for r in m["tsrs"] if r["component"] == cid) for a in SHADE}
        for cid in order
    }
    for cid in order:
        other = sum(r["component"] == cid for r in m["tsrs"]) - sum(counts[cid].values())
        if other:
            raise fk.FigureError(f"Figure 4-1 has no shade for an ASIL on {cid}")
    nmax = max(sum(c.values()) for c in counts.values())
    x0, x1, y = 266, W - 40, 100
    unit = (x1 - x0) / nmax
    body = [
        fk.text(24, 32, "Where the requirements fall", "h"),
        fk.text(24, 54, "WP-S-02 §4: requirements per component, by ASIL; dashed rows are", "t"),
        fk.text(24, 71, "built by a supplier under the DIA", "t"),
    ]
    row = 26
    for cid in order:
        c = comps[cid]
        inside = k["elements"][c["element"]]["in_item"]
        if not inside:
            body.append(
                fk.el("rect", None, x=18, y=y - 4, width=W - 36, height=row - 4, rx=5, class_="sup")
            )
        body.append(fk.text(28, y + 13, fk.fit(f"{cid} {c['name']}", x0 - 44, "t"), "t"))
        x = x0
        for a, cls in SHADE.items():
            n = counts[cid][a]
            if n:
                body.append(
                    fk.el(
                        "rect",
                        None,
                        x=fk.num(x),
                        y=y,
                        width=fk.num(n * unit - 2),
                        height=row - 12,
                        rx=3,
                        class_=cls,
                    )
                )
                x += n * unit
        body.append(fk.text(x + 6, y + 13, str(sum(counts[cid].values())), "s"))
        y += row
    y += 14
    lx = 24
    for a, cls in SHADE.items():
        if not any(counts[cid][a] for cid in order):
            continue
        body.append(fk.el("rect", None, x=lx, y=y - 11, width=14, height=14, rx=3, class_=cls))
        body.append(fk.text(lx + 20, y + 1, f"ASIL {a}", "s"))
        lx += 96
    y += 18
    desc = "Technical safety requirements per component, by ASIL: " + "; ".join(
        f"{cid} {comps[cid]['name']}"
        + ("" if k["elements"][comps[cid]["element"]]["in_item"] else " (supplier)")
        + ": "
        + ", ".join(f"{n} at {a}" for a, n in counts[cid].items() if n)
        for cid in order
    )
    return fk.svg(
        W, int(y + 6), "WP-S-02 Figure 4-1: requirements per component", desc + ".", body, EXTRA
    )


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("tsr.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
