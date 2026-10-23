#!/usr/bin/env python3
"""The fallback concept of WP-C-12, generated from fallback.yaml.

Writes the generated tables of WP-C-12 (triggers, minimal risk manoeuvres, minimal risk conditions,
stopping times and distances) and Figure 3-1 (the fallback chain: which triggers start which MRM,
which MRM takes over when one cannot complete, and which condition each reaches). Stopping times
and distances are computed from each MRM's deceleration and jerk, from the maximum speed of
WP-C-02 ODD-20; detection and reaction times are left to WP-S-04.

The model is refused when:
- an identifier is malformed or repeated, or a kind is unknown;
- a trigger, MRM or condition names an element, FSR, ODD monitor, SOTIF hazard or assumption that
  does not exist, or is pending on a decision that is no longer open;
- an MRM's fallback is not a later MRM, so that a chain could loop;
- a chain of fallbacks does not end in an MRM rated at the ASIL of SG-07;
- a trigger takes away the element that carries out its MRM, or all the elements that detect it;
- the rated minimal risk condition is not at the ASIL of SG-07.

    python3 fallback.py            # write WP-C-12's generated tables and Figure 3-1
    python3 fallback.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "01-management" / "decisions"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "fsc"))
sys.path.insert(0, str(ASSURANCE / "02-concept" / "sotif"))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import sotif  # noqa: E402

MODEL = HERE / "fallback.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-12-fallback-and-minimal-risk-concept.md"
ODD = ASSURANCE / "02-concept" / "WP-C-02-odd-and-intended-functionality.md"
FIG = HERE / "fig-c12-3-1-fallback.svg"
KINDS = {
    "fault": "Fault",
    "odd": "ODD exit",
    "performance": "Performance limit",
    "event": "Event",
    "request": "Request",
}
GOAL = "SG-07"
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def odd() -> tuple[set[str], float]:
    """The ODD monitors of WP-C-02 §4, and the maximum speed of ODD-20 in m/s."""
    md = ODD.read_text(encoding="utf-8")
    _, rows = fk.table(fk.section(md, "## 4. ODD monitoring"), "ID")
    mons = {fk.plain(r[0]) for r in rows}
    row = next((ln for ln in md.splitlines() if ln.startswith("| ODD-20 |")), "")
    kmh = re.search(r"0 to (\d+) km/h", row)
    if not kmh:
        raise fk.FigureError("WP-C-02 ODD-20 no longer states the speed range as '0 to N km/h'")
    return mons, int(kmh.group(1)) / 3.6


def known() -> dict:
    """Everything the model may refer to."""
    f, mons = fsc.load(), odd()[0]
    return {
        "elements": {e["id"]: e for e in f["elements"]},
        "refs": {x["id"] for x in f["fsrs"]}
        | mons
        | {h["id"] for h in sotif.load()["hazards"]}
        | fsc.aous(),
        "goal_asil": fsc.goals()[GOAL]["asil"],
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def stop(v0: float, a: float, j: float) -> tuple[float, float]:
    """Time and distance to stop from v0 (m/s), braking ramped up at jerk j (m/s³) to a (m/s²)."""
    t1 = a / j
    if v0 <= a * t1 / 2:  # stopped before the full deceleration is reached
        t = math.sqrt(2 * v0 / j)
        return t, v0 * t - j * t**3 / 6
    d1 = v0 * t1 - j * t1**3 / 6
    v1 = v0 - a * t1 / 2
    return t1 + v1 / a, d1 + v1**2 / (2 * a)


def chain(mrms: dict[str, dict], start: str) -> list[str]:
    out, cur = [], start
    while cur and cur in mrms and cur not in out:
        out.append(cur)
        cur = mrms[cur].get("fallback")
    return out


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    els, rank = k["elements"], fsc.hara.ASILS
    mrms = {x.get("id"): x for x in m.get("mrms", [])}
    mrcs = {x.get("id"): x for x in m.get("mrcs", [])}
    order = list(mrms)

    def ids(items: list[dict], pat: str, label: str) -> None:
        seen: set[str] = set()
        for x in items:
            i = str(x.get("id"))
            if not re.fullmatch(pat, i):
                errs.append(f"{i}: {label} id has the wrong form")
            if i in seen:
                errs.append(f"{i}: duplicate id")
            seen.add(i)

    def pending(i: str, x: dict) -> None:
        p = x.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )

    ids(m.get("triggers", []), r"TR-\d\d", "trigger")
    ids(m.get("mrms", []), r"MRM-\d", "MRM")
    ids(m.get("mrcs", []), r"MRC-\d", "MRC")
    for t in m.get("triggers", []):
        i = t["id"]
        if t.get("kind") not in KINDS:
            errs.append(f"{i}: kind must be one of {', '.join(KINDS)}")
        if not t.get("condition"):
            errs.append(f"{i}: missing condition")
        for e in (t.get("detected_by") or []) + (t.get("lost") or []):
            if e not in els:
                errs.append(f"{i}: element {e} does not exist")
        for r in t.get("refs") or []:
            if r not in k["refs"]:
                errs.append(f"{i}: {r} does not exist")
        pending(i, t)
        r = t.get("response")
        if r not in mrms:
            errs.append(f"{i}: response {r} is not an MRM")
            continue
        lost = set(t.get("lost") or [])
        if not set(t.get("detected_by") or []) - lost:
            errs.append(f"{i}: no element that detects it survives it")
        if mrms[r].get("by") in lost:
            errs.append(
                f"{i}: its response {r} is carried out by {mrms[r]['by']}, which it takes away"
            )
    for x in m.get("mrms", []):
        i = x["id"]
        for f in ("name", "by", "asil", "when", "fails_when", "source", "reaches"):
            if not x.get(f):
                errs.append(f"{i}: missing {f}")
        if x.get("by") not in els:
            errs.append(f"{i}: element {x.get('by')} does not exist")
        if x.get("asil") not in rank:
            errs.append(f"{i}: ASIL must be one of {', '.join(rank)}")
        if x.get("reaches") not in mrcs:
            errs.append(f"{i}: reaches {x.get('reaches')}, which is not an MRC")
        if (x.get("decel") is None) != (x.get("jerk") is None):
            errs.append(f"{i}: give both decel and jerk, or neither")
        fb = x.get("fallback")
        if fb is not None and (fb not in mrms or order.index(fb) <= order.index(i)):
            errs.append(f"{i}: fallback {fb} must be a later MRM")
            continue
        last = mrms[chain(mrms, i)[-1]]
        if last.get("asil") in rank and rank.index(last["asil"]) < rank.index(k["goal_asil"]):
            errs.append(
                f"{i}: its fallback chain ends in {last['id']} at {last['asil']}, below {GOAL}'s {k['goal_asil']}"
            )
    for x in m.get("mrcs", []):
        i = x["id"]
        for f in ("name", "state", "held_by", "asil", "passengers", "leaves"):
            if not x.get(f):
                errs.append(f"{i}: missing {f}")
        for e in x.get("held_by") or []:
            if e not in els:
                errs.append(f"{i}: element {e} does not exist")
        pending(i, x)
    if not any(x.get("asil") == k["goal_asil"] for x in m.get("mrcs", [])):
        errs.append(f"no minimal risk condition is rated at {GOAL}'s ASIL {k['goal_asil']}")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict, vmax: float) -> dict[str, str]:
    els = k["elements"]
    t = {}
    rows = [
        "| ID | Kind | Condition | Detected by | Takes away | First response | Related |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in m["triggers"]:
        resp = x["response"] + (f" (proposed, {x['pending']})" if x.get("pending") else "")
        rows.append(
            f"| {x['id']} | {KINDS[x['kind']]} | {cell(x['condition'])} | {', '.join(x['detected_by'])} "
            f"| {', '.join(x['lost']) or '—'} | {resp} | {', '.join(x['refs']) or '—'} |"
        )
    t["fallback-triggers"] = "\n".join(rows)
    rows = [
        "| ID | Manoeuvre | Carried out by | ASIL | Chosen when | Cannot complete when | Then | Reaches | In the pinned Autoware |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for x in m["mrms"]:
        rows.append(
            f"| {x['id']} | {cell(x['name'])} | {x['by']} {cell(els[x['by']]['name'])} | {x['asil']} "
            f"| {cell(x['when'])} | {cell(x['fails_when'])} | {x['fallback'] or '—'} | {x['reaches']} | {cell(x['autoware'])} |"
        )
    t["fallback-mrms"] = "\n".join(rows)
    rows = [
        "| ID | Condition | State | Held by | ASIL | Passengers | Left when |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in m["mrcs"]:
        pas = cell(x["passengers"]) + (f" (proposed, {x['pending']})" if x.get("pending") else "")
        rows.append(
            f"| {x['id']} | {cell(x['name'])} | {cell(x['state'])} | {', '.join(x['held_by'])} | {x['asil']} "
            f"| {pas} | {cell(x['leaves'])} |"
        )
    t["fallback-mrcs"] = "\n".join(rows)
    kmh = round(vmax * 3.6)
    rows = [
        f"| MRM | Deceleration (m/s²) | Jerk (m/s³) | Time to stop from {kmh} km/h | Distance | Source |",
        "|---|---|---|---|---|---|",
    ]
    for x in m["mrms"]:
        if x["decel"] is None:
            rows.append(f"| {x['id']} {cell(x['name'])} | — | — | — | — | {cell(x['source'])} |")
            continue
        s, d = stop(vmax, x["decel"], x["jerk"])
        rows.append(
            f"| {x['id']} {cell(x['name'])} | {x['decel']:g} | {x['jerk']:g} | {s:.1f} s | {d:.0f} m | {cell(x['source'])} |"
        )
    t["fallback-timing"] = "\n".join(rows)
    rated = [x["id"] for x in m["mrms"] if x["asil"] != "QM"]
    pend = sorted({x["pending"] for x in m["triggers"] + m["mrcs"] if x.get("pending")})
    t["fallback-summary"] = (
        f"{len(m['triggers'])} triggers lead to {len(m['mrms'])} minimal risk manoeuvres and "
        f"{len(m['mrcs'])} minimal risk conditions. {len(rated)} manoeuvres ({', '.join(rated)}) are rated at "
        f"{GOAL}'s ASIL {k['goal_asil']}, and every chain of fallbacks ends in one of them. "
        + (
            f"Entries marked proposed wait on {', '.join(pend)}."
            if pend
            else "No entry waits on a decision."
        )
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/fallback/fallback.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-12 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .rated { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.6; }
svg .qm { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .wire { stroke:var(--ink2); stroke-width:1.4; fill:none; }
svg .fb { stroke:var(--ink2); stroke-width:1.4; fill:none; stroke-dasharray:5 3; }
svg .head { fill:var(--ink2); }
svg .col { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); letter-spacing:.06em; }
"""


def head(x: float, y: float, dx: float, dy: float) -> str:
    """An arrowhead with its tip at (x, y), pointing along (dx, dy)."""
    a = math.atan2(dy, dx)
    hx, hy = x - 7 * math.cos(a), y - 7 * math.sin(a)
    px, py = 4 * math.sin(a), -4 * math.cos(a)
    d = f"M{fk.num(x)} {fk.num(y)} L{fk.num(hx + px)} {fk.num(hy + py)} L{fk.num(hx - px)} {fk.num(hy - py)} Z"
    return fk.el("path", None, d=d, class_="head")


def figure(m: dict, k: dict) -> str:
    els = k["elements"]
    top, bh, pitch = 120, 72, 100
    tx, mx, mw, cx, cw = 24, 190, 250, 468, 148
    row = {x["id"]: j for j, x in enumerate(m["mrms"])}
    body = [
        fk.text(24, 32, "Fallback chain", "h"),
        fk.text(24, 54, "WP-C-12 §3: what starts each minimal risk manoeuvre, what takes", "t"),
        fk.text(24, 71, "over when it cannot complete, and the condition it reaches", "t"),
        fk.text(tx, top - 14, "TRIGGERS", "col"),
        fk.text(mx, top - 14, "MANOEUVRES", "col"),
        fk.text(cx, top - 14, "CONDITIONS", "col"),
    ]
    for x in m["mrms"]:
        j = row[x["id"]]
        y = top + j * pitch
        cy = y + bh / 2
        trs = [t["id"] for t in m["triggers"] if t["response"] == x["id"]]
        lines = fk.wrap(", ".join(trs), mx - tx - 34, "s")
        for n, ln in enumerate(lines):
            body.append(fk.text(tx, cy + 4 - (len(lines) - 1) * 7.5 + 15 * n, ln, "s"))
        if trs:
            body.append(
                fk.el(
                    "path", None, d=f"M{mx - 26} {fk.num(cy)} L{mx - 1} {fk.num(cy)}", class_="wire"
                )
            )
            body.append(head(mx - 1, cy, 1, 0))
        cls = "qm" if x["asil"] == "QM" else "rated"
        body.append(fk.el("rect", None, x=mx, y=y, width=mw, height=bh, rx=7, class_=cls))
        rating = "not rated" if x["asil"] == "QM" else f"ASIL {x['asil']}"
        who = f"{x['id']} · {els[x['by']]['name']} · {rating}"
        body.append(fk.text(mx + 12, y + 21, fk.fit(who, mw - 24, "s"), "s"))
        for n, ln in enumerate(fk.wrap(x["name"], mw - 24, "tb")[:2]):
            body.append(fk.text(mx + 12, y + 42 + 17 * n, ln, "tb"))
        fb = x.get("fallback")
        if fb:
            if row[fb] != j + 1:
                raise fk.FigureError("Figure 3-1 draws fallbacks between neighbouring MRMs only")
            fx = mx + 36
            body.append(fk.el("path", None, d=f"M{fx} {y + bh} L{fx} {y + pitch - 1}", class_="fb"))
            body.append(head(fx, y + pitch - 1, 0, 1))
            body.append(fk.text(fx + 10, y + bh + 19, "cannot complete", "s"))
    for c in m["mrcs"]:
        rows = [row[x["id"]] for x in m["mrms"] if x["reaches"] == c["id"]]
        if not rows:
            continue
        y0, y1 = top + min(rows) * pitch, top + max(rows) * pitch + bh
        cls = "qm" if c["asil"] == "QM" else "rated"
        body.append(fk.el("rect", None, x=cx, y=y0, width=cw, height=y1 - y0, rx=7, class_=cls))
        rating = "not rated" if c["asil"] == "QM" else f"ASIL {c['asil']}"
        body.append(fk.text(cx + 12, y0 + 21, f"{c['id']} · {rating}", "s"))
        name = fk.wrap(c["name"], cw - 24, "tb")[:2]
        for n, ln in enumerate(name):
            body.append(fk.text(cx + 12, y0 + 42 + 17 * n, ln, "tb"))
        if y1 - y0 > bh:
            for n, ln in enumerate(fk.wrap(c["state"], cw - 24, "s")):
                body.append(fk.text(cx + 12, y0 + 52 + 17 * len(name) + 16 * n, ln, "s"))
        for r in rows:
            cy = top + r * pitch + bh / 2
            body.append(
                fk.el(
                    "path", None, d=f"M{mx + mw} {fk.num(cy)} L{cx - 1} {fk.num(cy)}", class_="wire"
                )
            )
            body.append(head(cx - 1, cy, 1, 0))
    y = top + (len(m["mrms"]) - 1) * pitch + bh + 40
    body += [
        fk.el("rect", None, x=24, y=y - 12, width=22, height=14, rx=3, class_="rated"),
        fk.text(54, y, f"Rated at {GOAL}'s ASIL {k['goal_asil']}", "t"),
        fk.el("rect", None, x=244, y=y - 12, width=22, height=14, rx=3, class_="qm"),
        fk.text(274, y, "Not rated (QM)", "t"),
        fk.el("path", None, d=f"M404 {y - 5} L436 {y - 5}", class_="fb"),
        head(440, y - 5, 1, 0),
        fk.text(450, y, "Next if it cannot complete", "t"),
    ]
    y += 24
    desc = (
        "Fallback chain: "
        + "; ".join(
            f"{x['id']} {x['name']} ({x['asil']}), started by "
            f"{', '.join(t['id'] for t in m['triggers'] if t['response'] == x['id']) or 'none'}, "
            f"reaches {x['reaches']}, then {x['fallback'] or 'nothing further'}"
            for x in m["mrms"]
        )
        + "."
    )
    return fk.svg(W, int(y), "WP-C-12 Figure 3-1: fallback chain", desc, body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("fallback.yaml: " + "; ".join(errs))
    vmax = odd()[1]
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k, vmax)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
