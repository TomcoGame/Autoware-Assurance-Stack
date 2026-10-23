#!/usr/bin/env python3
"""The threat analysis and risk assessment of WP-C-09, generated from tara.yaml.

Writes the generated tables of WP-C-09 (assets, damage scenarios, threat scenarios, ratings, risk
and treatment) and Figure 5-1 (the threat scenarios placed on the risk matrix). Attack feasibility
is computed from the attack potential factors, the risk value from the matrix, and the treatment
from the threshold; none of them is typed.

The model is refused when:
- an identifier is malformed or repeated, or the risk matrix does not match the impact and
  feasibility scales;
- an asset has a property other than C, I or A, or no threat scenario;
- a damage scenario has an impact rating outside the scale, or names a HARA hazard that does not
  exist, or no threat scenario leads to it;
- a threat scenario names an asset, damage scenario or factor value that does not exist;
- a threat scenario whose risk must be reduced names no control, or names a control that does not
  exist (cybersecurity controls here, or requirements of the STPA, the functional safety concept,
  the fallback concept and the functional modifications);
- a control here is used by no threat scenario;
- the treatment threshold is pending on a decision that is no longer open.

    python3 tara.py            # write WP-C-09's generated tables and Figure 5-1
    python3 tara.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in ("01-management/figures", "01-management/decisions", "08-analyses/stpa"):
    sys.path.insert(0, str(ASSURANCE / sub))
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import stpa  # noqa: E402

MODEL = HERE / "tara.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-09-tara.md"
FIG = HERE / "fig-c09-5-1-risk-matrix.svg"
CATEGORIES = ("safety", "financial", "operational", "privacy")
FEAS = ("Very low", "Low", "Medium", "High")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    s = stpa.load()
    k = stpa.known()
    return {
        "hara": k["hara"],
        "refs": k["measures"] | {r["id"] for r in s["requirements"]},
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def potential(m: dict, t: dict) -> int:
    f = m["method"]["factors"]
    return sum(f[k][v] for k, v in t["factors"].items())


def feasibility(m: dict, t: dict) -> str:
    p = potential(m, t)
    return [name for low, name in m["method"]["feasibility"] if p >= low][-1]


def impact(m: dict, t: dict) -> str:
    """The highest impact, over every category, of the damage scenarios the threat leads to."""
    scale = m["method"]["impacts"]
    ds = {d["id"]: d for d in m["damage"]}
    return max((ds[d]["impact"][c] for d in t["damage"] for c in CATEGORIES), key=scale.index)


def risk(m: dict, t: dict) -> int:
    meth = m["method"]
    return meth["matrix"][meth["impacts"].index(impact(m, t))][FEAS.index(feasibility(m, t))]


def treatment(m: dict, t: dict) -> str:
    return "Reduce" if risk(m, t) >= m["method"]["reduce_at"] else "Retain"


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    meth = m.get("method", {})
    scale = meth.get("impacts", [])
    if [n for _, n in meth.get("feasibility", [])] != list(reversed(FEAS)):
        errs.append(f"method: feasibility must run {', '.join(reversed(FEAS))}")
    mx = meth.get("matrix", [])
    if len(mx) != len(scale) or any(len(r) != len(FEAS) for r in mx):
        errs.append(
            "method: the risk matrix must have a row per impact and a column per feasibility"
        )
    p = meth.get("pending")
    if p and k["decisions"].get(p) not in ("open", "queued"):
        errs.append(
            f"method: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
        )
    seen: set[str] = set()

    def new(i: str, pat: str, keys: set[str], x: dict) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)
        if set(x) - keys:
            errs.append(f"{i}: unexpected keys {sorted(set(x) - keys)} (quote a text with commas)")

    threats = m.get("threats", [])
    for a in m.get("assets", []):
        new(a["id"], r"A-\d\d", {"id", "name", "properties"}, a)
        if not a.get("properties") or set(a["properties"]) - {"C", "I", "A"}:
            errs.append(f"{a['id']}: properties must be among C, I, A")
        if not any(a["id"] in t.get("assets", []) for t in threats):
            errs.append(f"{a['id']}: no threat scenario names it")
    for d in m.get("damage", []):
        new(d["id"], r"DS-\d\d", {"id", "text", "impact", "hara"}, d)
        for c in CATEGORIES:
            if (d.get("impact") or {}).get(c) not in scale:
                errs.append(f"{d['id']}: {c} impact must be one of {', '.join(scale)}")
        for h in d.get("hara") or []:
            if h not in k["hara"]:
                errs.append(f"{d['id']}: HARA hazard {h} does not exist")
        if not any(d["id"] in t.get("damage", []) for t in threats):
            errs.append(f"{d['id']}: no threat scenario leads to it")
    assets = {a["id"] for a in m.get("assets", [])}
    damage = {d["id"] for d in m.get("damage", [])}
    controls = {c["id"] for c in m.get("controls", [])}
    used: set[str] = set()
    for t in threats:
        i = t["id"]
        new(
            i,
            r"TS-\d\d",
            {"id", "text", "stride", "assets", "damage", "path", "factors", "controls"},
            t,
        )
        for a in t.get("assets") or []:
            if a not in assets:
                errs.append(f"{i}: asset {a} does not exist")
        for d in t.get("damage") or []:
            if d not in damage:
                errs.append(f"{i}: damage scenario {d} does not exist")
        for f, v in (t.get("factors") or {}).items():
            if v not in meth.get("factors", {}).get(f, {}):
                errs.append(f"{i}: {f} '{v}' is not a value of the method")
        if set(t.get("factors") or {}) != set(meth.get("factors", {})):
            errs.append(f"{i}: rate every factor of the method")
        for c in t.get("controls") or []:
            if c not in controls | k["refs"]:
                errs.append(f"{i}: control {c} does not exist")
            used.add(c)
    for c in m.get("controls", []):
        new(c["id"], r"CR-\d\d", {"id", "text"}, c)
        if c["id"] not in used:
            errs.append(f"{c['id']}: no threat scenario uses it")
    if not errs:
        for t in threats:
            if treatment(m, t) == "Reduce" and not t.get("controls"):
                errs.append(f"{t['id']}: its risk must be reduced but it names no control")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict) -> dict[str, str]:
    meth = m["method"]
    t = {}
    rows = ["| ID | Asset | Properties | Threat scenarios |", "|---|---|---|---|"]
    for a in m["assets"]:
        ts = [x["id"] for x in m["threats"] if a["id"] in x["assets"]]
        rows.append(
            f"| {a['id']} | {cell(a['name'])} | {', '.join(a['properties'])} | {', '.join(ts)} |"
        )
    t["tara-assets"] = "\n".join(rows)
    rows = [
        "| ID | Damage scenario | Safety | Financial | Operational | Privacy | HARA hazards |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in m["damage"]:
        im = d["impact"]
        rows.append(
            f"| {d['id']} | {cell(d['text'])} | "
            + " | ".join(im[c] for c in CATEGORIES)
            + f" | {', '.join(d['hara']) or '—'} |"
        )
    t["tara-damage"] = "\n".join(rows)
    rows = [
        "| ID | Threat scenario | STRIDE | Assets | Attack path | Damage |",
        "|---|---|---|---|---|---|",
    ]
    for x in m["threats"]:
        rows.append(
            f"| {x['id']} | {cell(x['text'])} | {x['stride']} | {', '.join(x['assets'])} | {cell(x['path'])} | {', '.join(x['damage'])} |"
        )
    t["tara-threats"] = "\n".join(rows)
    rows = [
        "| ID | Elapsed time | Expertise | Knowledge | Window | Equipment | Attack potential | Feasibility | Impact |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for x in m["threats"]:
        f = x["factors"]
        rows.append(
            f"| {x['id']} | {f['time']} | {f['expertise']} | {f['knowledge']} | {f['window']} | {f['equipment']} "
            f"| {potential(m, x)} | {feasibility(m, x)} | {impact(m, x)} |"
        )
    t["tara-ratings"] = "\n".join(rows)
    ctl = {c["id"]: c["text"] for c in m["controls"]}
    pend = f" (proposed, {meth['pending']})" if meth.get("pending") else ""
    rows = ["| ID | Risk value | Treatment | Controls |", "|---|---|---|---|"]
    for x in sorted(m["threats"], key=lambda x: (-risk(m, x), x["id"])):
        rows.append(
            f"| {x['id']} | **{risk(m, x)}** | {treatment(m, x)}{pend} | {', '.join(x['controls']) or '—'} |"
        )
    t["tara-risk"] = "\n".join(rows)
    rows = ["| ID | Proposed cybersecurity control | For |", "|---|---|---|"]
    for c, text in ctl.items():
        by = [x["id"] for x in m["threats"] if c in x["controls"]]
        rows.append(f"| {c} | {cell(text)} | {', '.join(by)} |")
    t["tara-controls"] = "\n".join(rows)
    hist = {v: sum(1 for x in m["threats"] if risk(m, x) == v) for v in range(5, 0, -1)}
    reduce = sum(1 for x in m["threats"] if treatment(m, x) == "Reduce")
    t["tara-summary"] = (
        f"{len(m['assets'])} assets, {len(m['damage'])} damage scenarios and {len(m['threats'])} threat scenarios. "
        f"Risk values before any cybersecurity control: "
        + ", ".join(f"{n} at {v}" for v, n in hist.items() if n)
        + f". {reduce} must be reduced at the {'proposed ' if meth.get('pending') else ''}threshold of {meth['reduce_at']}"
        + (f" ({meth['pending']})" if meth.get("pending") else "")
        + f"; {len(m['controls'])} cybersecurity controls are proposed for WP-C-10."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/tara/tara.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-09 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


# Five steps of one warm hue for the risk values, ink chosen for contrast on each.
EXTRA = """svg { --r1:#f7eedd; --r2:#f0d6a8; --r3:#e5a65a; --r4:#c96a2b; --r5:#8f3415; --t1:#3d2508; --t5:#ffffff; }
@media (prefers-color-scheme: dark) { svg { --r1:#3a3020; --r2:#5a4322; --r3:#8a5a26; --r4:#c06a2c; --r5:#e8925a; --t1:#f3e6d2; --t5:#1b0f06; } }
svg .r1 { fill:var(--r1); } svg .r2 { fill:var(--r2); } svg .r3 { fill:var(--r3); }
svg .r4 { fill:var(--r4); } svg .r5 { fill:var(--r5); }
svg .k1 { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--t1); }
svg .k5 { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--t5); }
svg .rv { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--t1); opacity:.7; }
svg .rvi { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--t5); opacity:.8; }
svg .ax { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
"""


def figure(m: dict) -> str:
    meth = m["method"]
    rows = list(reversed(meth["impacts"]))  # Severe on top
    x0, top, cw, rh = 120, 108, 124, 74
    body = [
        fk.text(24, 32, "Threats on the risk matrix", "h"),
        fk.text(24, 54, "WP-C-09 §5: each threat scenario by the impact of its damage and", "t"),
        fk.text(24, 71, "the feasibility of its attack, before any cybersecurity control", "t"),
        fk.text(x0 + cw * len(FEAS) / 2, top - 12, "Attack feasibility →", "ax", "middle"),
    ]
    for j, f in enumerate(FEAS):
        body.append(fk.text(x0 + cw * j + cw / 2, top + rh * len(rows) + 18, f, "t", "middle"))
    for i, im in enumerate(rows):
        y = top + i * rh
        body.append(fk.text(x0 - 10, y + rh / 2 + 4, im, "t", "end"))
        for j, f in enumerate(FEAS):
            v = meth["matrix"][meth["impacts"].index(im)][j]
            x = x0 + cw * j
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=x + 1,
                    y=y + 1,
                    width=cw - 2,
                    height=rh - 2,
                    rx=4,
                    class_=f"r{v}",
                )
            )
            dark = v >= 4
            body.append(fk.text(x + cw - 8, y + 16, str(v), "rvi" if dark else "rv", "end"))
            ids = [t["id"] for t in m["threats"] if impact(m, t) == im and feasibility(m, t) == f]
            for n, s in enumerate(fk.wrap(", ".join(ids), cw - 16, "s")):
                body.append(fk.text(x + 8, y + 34 + 15 * n, s, "k5" if dark else "k1"))
            if len(ids) > 9:
                raise fk.FigureError(f"Figure 5-1: too many threats in {im}/{f}")
    body.append(fk.text(24, top - 12, "Impact ↓", "ax"))
    y = top + rh * len(rows) + 44
    body.append(
        fk.text(
            24,
            y,
            f"Cell number: risk value 1 to 5. Reduce at {meth['reduce_at']} or more"
            + (" (proposed)." if meth.get("pending") else "."),
            "t",
        )
    )
    y += 18
    desc = (
        "Risk matrix with threat scenarios: "
        + "; ".join(
            f"{t['id']} impact {impact(m, t)}, feasibility {feasibility(m, t)}, risk {risk(m, t)}"
            for t in m["threats"]
        )
        + "."
    )
    return fk.svg(W, int(y), "WP-C-09 Figure 5-1: threats on the risk matrix", desc, body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("tara.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m)), FIG: figure(m)}


if __name__ == "__main__":
    fk.run(build, __doc__)
