#!/usr/bin/env python3
"""The timing budget of WP-S-04, generated from timing.yaml.

Writes the generated tables of WP-S-04 (FTTI per safety goal, budget per safety mechanism,
sensing-to-actuation chain, fallback timing) and Figure 2-1 (how each FTTI depends on the fault
magnitude the vehicle can produce). Every FTTI is computed from its margin and fault range:
a deviation goal from x = a t² / 2, a drift goal from x = v t, a derived goal as the shortest of the
goals it comes from. Budgets are the allocation shares of the shortest FTTI that binds a mechanism.

The model is refused when:
- a goal is not in the HARA, or a HARA goal has no timing entry;
- a goal's kind is unknown, its range does not exist, its margin is not positive, or a derived
  goal refers to a goal that does not exist or to itself;
- the allocation shares are not positive or add up to more than 1;
- a mechanism is not in WP-S-03, or names a goal that has no FTTI;
- a chain stage names a component that is not in WP-S-03.

    python3 timing.py            # write WP-S-04's generated tables and Figure 2-1
    python3 timing.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in ("01-management/figures", "02-concept/hara", "02-concept/fallback", "03-system/tsc"):
    sys.path.insert(0, str(ASSURANCE / sub))
import fallback  # noqa: E402
import figkit as fk  # noqa: E402
import hara  # noqa: E402
import tsc  # noqa: E402

MODEL = HERE / "timing.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-04-timing-ftti-budget.md"
FIG = HERE / "fig-s04-2-1-ftti.svg"
KINDS = ("deviation", "drift", "derived", "limit")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    t = tsc.load()
    return {
        "goals": {g["id"]: g for g in hara.load()["goals"]},
        "mechanisms": {s["id"]: s for s in t["mechanisms"]},
        "components": {c["id"]: c for c in t["components"]},
    }


def ftti(m: dict, gid: str, bound: str) -> float | None:
    """FTTI of a goal in seconds; bound 'high' is the worst case (largest fault, shortest time)."""
    g = next(x for x in m["goals"] if x["id"] == gid)
    if g["kind"] == "limit":
        return None
    if g["kind"] == "derived":
        vals = [ftti(m, x, bound) for x in g["from"]]
        vals = [v for v in vals if v is not None]
        return min(vals) if vals else None
    r = m["ranges"][g["range"]][bound]
    if g["kind"] == "deviation":
        return math.sqrt(2 * g["margin"] / r)
    return g["margin"] / r


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    ids = [g.get("id") for g in m.get("goals", [])]
    for g in m.get("goals", []):
        i = g.get("id")
        if i not in k["goals"]:
            errs.append(f"{i}: not a safety goal of the HARA")
        if ids.count(i) > 1:
            errs.append(f"{i}: duplicate")
        kind = g.get("kind")
        if kind not in KINDS:
            errs.append(f"{i}: kind must be one of {', '.join(KINDS)}")
        if kind in ("deviation", "drift"):
            if g.get("range") not in m.get("ranges", {}):
                errs.append(f"{i}: range {g.get('range')} does not exist")
            if not isinstance(g.get("margin"), (int, float)) or g["margin"] <= 0:
                errs.append(f"{i}: margin must be a positive number of metres")
        if kind == "derived":
            for x in g.get("from") or []:
                if x not in ids or x == i:
                    errs.append(f"{i}: derived from {x}, which has no timing entry or is itself")
        if not g.get("basis"):
            errs.append(f"{i}: missing basis")
    for gid in k["goals"]:
        if gid not in ids:
            errs.append(f"{gid}: safety goal with no timing entry")
    for name, r in m.get("ranges", {}).items():
        if not (0 < r.get("low", 0) <= r.get("high", 0)):
            errs.append(f"range {name}: needs 0 < low <= high")
    al = m.get("allocation", {})
    if not (al.get("detect", 0) > 0 and al.get("react", 0) > 0 and al["detect"] + al["react"] <= 1):
        errs.append("allocation: detect and react must be positive and add up to at most 1")
    if errs:
        return errs
    for s in m.get("mechanisms", []):
        if s["id"] not in k["mechanisms"]:
            errs.append(f"{s['id']}: not a safety mechanism of WP-S-03")
        for gid in s.get("goals") or []:
            if gid not in ids or ftti(m, gid, "high") is None:
                errs.append(f"{s['id']}: goal {gid} has no FTTI")
    for c in m.get("chain", []):
        if c.get("component") not in k["components"]:
            errs.append(
                f"chain stage '{c.get('stage')}': component {c.get('component')} is not in WP-S-03"
            )
    for mrm, sm in (m.get("fallback") or {}).items():
        if sm not in {s["id"] for s in m.get("mechanisms", [])}:
            errs.append(f"fallback {mrm}: mechanism {sm} has no budget")
    return errs


def ms(t: float | None) -> str:
    return "—" if t is None else f"{t * 1000:.0f} ms"


def span(lo: float | None, hi: float | None) -> str:
    """A range of times, shortest (worst case) first."""
    if lo is None:
        return "—"
    return ms(lo) if abs(lo - hi) < 1e-9 else f"{ms(lo)} to {ms(hi)}"


def bound(m: dict, s: dict) -> tuple[float, float, str]:
    """The binding (shortest) FTTI of a mechanism in the worst and best case, and its goal."""
    worst = min(s["goals"], key=lambda g: ftti(m, g, "high"))
    return ftti(m, worst, "high"), min(ftti(m, g, "low") for g in s["goals"]), worst


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict, vmax: float) -> dict[str, str]:
    t = {}
    rows = [
        "| Safety goal | Kind | Margin | Fault range | FTTI (worst case to best case) | Basis |",
        "|---|---|---|---|---|---|",
    ]
    for g in m["goals"]:
        rng = m["ranges"].get(g.get("range", ""), {})
        unit = "m/s" if g["kind"] == "drift" else "m/s²"
        fr = f"{rng['low']:g} to {rng['high']:g} {unit}" if rng else "—"
        margin = f"{g['margin']:g} m (proposed)" if "margin" in g else "—"
        kind = g["kind"] + (f" from {', '.join(g['from'])}" if g["kind"] == "derived" else "")
        rows.append(
            f"| {g['id']} {cell(k['goals'][g['id']]['statement'])} | {kind} | {margin} | {fr} "
            f"| {span(ftti(m, g['id'], 'high'), ftti(m, g['id'], 'low'))} | {cell(g['basis'])} |"
        )
    t["timing-ftti"] = "\n".join(rows)
    al = m["allocation"]
    rows = [
        "| Mechanism | Bound by | Binding FTTI | Detection budget | Reaction budget |",
        "|---|---|---|---|---|",
    ]
    for s in m["mechanisms"]:
        lo, hi, g = bound(m, s)
        rows.append(
            f"| {s['id']} {cell(k['mechanisms'][s['id']]['name'])} | {g} (of {', '.join(s['goals'])}) | {span(lo, hi)} "
            f"| {span(lo * al['detect'], hi * al['detect'])} | {span(lo * al['react'], hi * al['react'])} |"
        )
    t["timing-mechanisms"] = "\n".join(rows)
    rows = ["| Stage | Component | Budget | Measured |", "|---|---|---|---|"]
    for c in m["chain"]:
        rows.append(
            f"| {cell(c['stage'])} | {c['component']} {cell(k['components'][c['component']]['name'])} | To be set | Not yet |"
        )
    t["timing-chain"] = "\n".join(rows)
    fb = fallback.load()
    rows = [
        "| Manoeuvre | Started by | Detection budget | Time to stop from {} km/h | Total |".format(
            round(vmax * 3.6)
        ),
        "|---|---|---|---|---|",
    ]
    sms = {s["id"]: s for s in m["mechanisms"]}
    for x in fb["mrms"]:
        sm = (m.get("fallback") or {}).get(x["id"])
        det = None
        if sm:
            lo, hi, _ = bound(m, sms[sm])
            det = (lo * al["detect"], hi * al["detect"])
        stop = fallback.stop(vmax, x["decel"], x["jerk"])[0] if x.get("decel") else None
        total = f"{det[0] + stop:.1f} s to {det[1] + stop:.1f} s" if det and stop else "—"
        rows.append(
            f"| {x['id']} {cell(x['name'])} | {sm or 'Autoware (QM, not budgeted)'} | {span(*det) if det else '—'} "
            f"| {f'{stop:.1f} s' if stop else ('With the vehicle (DQ-008)' if sm else '—')} | {total} |"
        )
    t["timing-fallback"] = "\n".join(rows)
    timed = [g for g in m["goals"] if ftti(m, g["id"], "high") is not None]
    shortest = min(timed, key=lambda g: ftti(m, g["id"], "high"))
    t["timing-summary"] = (
        f"FTTIs for {len(timed)} of {len(m['goals'])} safety goals, computed from proposed margins and the range of "
        f"faults the candidate vehicles can produce; the other {len(m['goals']) - len(timed)} are met by limits, not "
        f"by time. The shortest is {shortest['id']} at {ms(ftti(m, shortest['id'], 'high'))} in the worst case. "
        f"{len(m['mechanisms'])} time-critical mechanisms get {al['detect']:.0%} of their binding FTTI to detect a fault "
        f"and {al['react']:.0%} to react. No value is measured yet."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/timing/timing.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-04 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .ax { stroke:var(--ink3); stroke-width:1; fill:none; }
svg .gl { stroke:var(--grid); stroke-width:1; fill:none; }
svg .l1 { stroke:var(--acc); stroke-width:2.4; fill:none; }
svg .l2 { stroke:var(--amb); stroke-width:2.4; fill:none; stroke-dasharray:7 4; }
svg .l3 { stroke:var(--ok); stroke-width:2.4; fill:none; stroke-dasharray:2 3; }
svg .k1 { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); }
svg .k2 { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--amb); }
svg .k3 { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ok); }
"""


def figure(m: dict) -> str:
    x0, x1, y0, y1 = 70, 500, 96, 356
    amax, tmax = 4.0, 1.0
    X = lambda a: x0 + (x1 - x0) * a / amax  # noqa: E731
    Y = lambda t: y1 - (y1 - y0) * t / tmax  # noqa: E731
    body = [
        fk.text(24, 32, "How long a fault may last", "h"),
        fk.text(
            24, 54, "WP-S-04 §2: FTTI against the acceleration a fault produces, over each", "t"
        ),
        fk.text(24, 71, "goal's range; the larger the fault, the less time to catch it", "t"),
    ]
    for tv in (0, 0.25, 0.5, 0.75, 1.0):
        body.append(
            fk.el("path", None, d=f"M{x0} {fk.num(Y(tv))} L{x1} {fk.num(Y(tv))}", class_="gl")
        )
        body.append(fk.text(x0 - 8, Y(tv) + 4, f"{tv * 1000:.0f} ms", "s", "end"))
    for a in range(0, 5):
        body.append(fk.text(X(a), y1 + 18, f"{a}", "s", "middle"))
    body.append(fk.text((x0 + x1) / 2, y1 + 38, "Fault acceleration (m/s²)", "t", "middle"))
    body.append(fk.el("path", None, d=f"M{x0} {y0} L{x0} {y1} L{x1} {y1}", class_="ax"))
    curves, seen = [], {}
    for g in m["goals"]:
        if g["kind"] != "deviation":
            continue
        key = (g["range"], g["margin"])
        if key in seen:
            seen[key].append(g["id"])
            continue
        seen[key] = [g["id"]]
        curves.append(key)
    for n, key in enumerate(curves):
        rng, margin = m["ranges"][key[0]], key[1]
        pts = []
        steps = 24
        for s in range(steps + 1):
            a = rng["low"] + (rng["high"] - rng["low"]) * s / steps
            pts.append((X(a), Y(math.sqrt(2 * margin / a))))
        d = "M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in pts)
        body.append(fk.el("path", None, d=d, class_=f"l{n + 1}"))
        lx, ly = pts[0]  # label each curve at its start, above it, where curves do not cross
        body.append(fk.text(lx + 6, ly - 8, f"{', '.join(seen[key])} · {margin:g} m", f"k{n + 1}"))
    y = y1 + 64
    body.append(
        fk.text(
            24,
            y,
            "Margins are proposals (WP-S-02); fault ranges span the candidate vehicles (DQ-008).",
            "s",
        )
    )
    y += 16
    desc = "FTTI against fault acceleration: " + "; ".join(
        f"{', '.join(seen[k])} with {k[1]:g} m margin, from {ms(math.sqrt(2 * k[1] / m['ranges'][k[0]]['low']))} at "
        f"{m['ranges'][k[0]]['low']:g} m/s² to {ms(math.sqrt(2 * k[1] / m['ranges'][k[0]]['high']))} at {m['ranges'][k[0]]['high']:g} m/s²"
        for k in curves
    )
    return fk.svg(W, int(y), "WP-S-04 Figure 2-1: FTTI against fault size", desc + ".", body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("timing.yaml: " + "; ".join(errs))
    vmax = fallback.odd()[1]
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k, vmax)), FIG: figure(m)}


if __name__ == "__main__":
    fk.run(build, __doc__)
