#!/usr/bin/env python3
"""The STPA of WP-A-05, generated from stpa.yaml.

Writes the generated tables of WP-A-05 (losses and hazards, control actions, unsafe control
actions, loss scenarios, resulting requirements) and Figure 3-1 (the control structure).

The model is refused when:
- an identifier is malformed or repeated;
- a hazard names a loss or HARA or SOTIF hazard that does not exist, or leads to no loss;
- a control action is not examined for all four types (N, P, T, D), each with UCAs or a reason;
- an unsafe control action names a hazard that does not exist, or no loss scenario explains it;
- a loss scenario has neither a measure already in the concept nor a new requirement, or names
  one that does not exist;
- a new requirement is not used by any scenario;
- a link's arrow in Figure 3-1 would leave its boxes or cross another box.

    python3 stpa.py            # write WP-A-05's generated tables and Figure 3-1
    python3 stpa.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "02-concept/fsc",
    "02-concept/fallback",
    "02-concept/modifications",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import fallback  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import modifications  # noqa: E402

MODEL = HERE / "stpa.yaml"
DOC = ASSURANCE / "08-analyses" / "WP-A-05-stpa.md"
FIG = HERE / "fig-a05-3-1-control-structure.svg"
TYPES = {
    "N": "Not provided",
    "P": "Provided",
    "T": "Too early, too late or out of order",
    "D": "Stopped too soon or applied too long",
}
KINDS = ("controller", "process model", "control path", "controlled process")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    h = fsc.hara.load()
    fb = fallback.load()
    k = fallback.known()
    return {
        "hara": {x["id"] for x in h["hazards"]},
        "sotif": _sotif_ids(),
        "measures": k["refs"]
        | {x["id"] for x in fb["triggers"]}
        | {x["id"] for x in fb["mrms"]}
        | {x["id"] for x in modifications.load()["modifications"]},
    }


def _sotif_ids() -> set[str]:
    import yaml

    path = ASSURANCE / "02-concept" / "sotif" / "sotif.yaml"
    return {x["id"] for x in yaml.safe_load(path.read_text(encoding="utf-8"))["hazards"]}


def actions(m: dict) -> list[tuple[dict, dict]]:
    """(link, control action) for every control action, in order."""
    return [(ln, a) for ln in m["links"] for a in ln["actions"]]


def ucas(m: dict) -> list[tuple[dict, str, dict]]:
    """(control action, type, UCA) for every unsafe control action, in order."""
    out = []
    for _, a in actions(m):
        for t in TYPES:
            v = a["ucas"].get(t)
            if isinstance(v, list):
                out += [(a, t, u) for u in v]
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

    losses = {x["id"] for x in m.get("losses", [])}
    for x in m.get("losses", []):
        new(x["id"], r"L-\d")
    hz = {}
    for x in m.get("hazards", []):
        new(x["id"], r"HZ-\d")
        hz[x["id"]] = x
        if not x.get("losses"):
            errs.append(f"{x['id']}: leads to no loss")
        for lo in x.get("losses") or []:
            if lo not in losses:
                errs.append(f"{x['id']}: loss {lo} does not exist")
        for h in x.get("hara") or []:
            if h not in k["hara"]:
                errs.append(f"{x['id']}: HARA hazard {h} does not exist")
        for h in x.get("sotif") or []:
            if h not in k["sotif"]:
                errs.append(f"{x['id']}: SOTIF hazard {h} does not exist")
    cts = {c["id"]: c for c in m.get("controllers", [])}
    for c in m.get("controllers", []):
        new(c["id"], r"CT-\d")
    for ln in m.get("links", []):
        for e in (ln.get("from"), ln.get("to")):
            if e not in cts:
                errs.append(f"link {ln.get('from')}→{ln.get('to')}: controller {e} does not exist")
        for a in ln.get("actions") or []:
            new(a["id"], r"CA-\d\d")
            for t in TYPES:
                v = (a.get("ucas") or {}).get(t)
                if isinstance(v, dict) and v.get("none"):
                    continue
                if not isinstance(v, list) or not v:
                    errs.append(f"{a['id']}: type {t} has neither UCAs nor a reason for none")
                    continue
                for u in v:
                    new(u["id"], r"UCA-\d\d")
                    if set(u) != {"id", "text", "hz"}:
                        errs.append(
                            f"{u['id']}: unexpected keys {sorted(set(u) - {'id', 'text', 'hz'})} (quote a text with commas)"
                        )
                    for h in u.get("hz") or []:
                        if h not in hz:
                            errs.append(f"{u['id']}: hazard {h} does not exist")
                    if not u.get("hz"):
                        errs.append(f"{u['id']}: names no hazard")
    all_ucas = {u["id"] for _, _, u in ucas(m)} if not errs else set()
    srs = {r["id"] for r in m.get("requirements", [])}
    used: set[str] = set()
    for s in m.get("scenarios", []):
        new(s["id"], r"LS-\d\d")
        if s.get("kind") not in KINDS:
            errs.append(f"{s['id']}: kind must be one of {', '.join(KINDS)}")
        for u in s.get("ucas") or []:
            if all_ucas and u not in all_ucas:
                errs.append(f"{s['id']}: {u} does not exist")
        for x in s.get("measures") or []:
            if x not in k["measures"]:
                errs.append(f"{s['id']}: measure {x} does not exist")
        for r in s.get("new") or []:
            if r not in srs:
                errs.append(f"{s['id']}: new requirement {r} does not exist")
            used.add(r)
        if not s.get("measures") and not s.get("new"):
            errs.append(f"{s['id']}: has neither a measure nor a new requirement")
    for r in m.get("requirements", []):
        new(r["id"], r"SR-\d\d")
        if r["id"] not in used:
            errs.append(f"{r['id']}: no scenario needs it")
    for u in sorted(all_ucas):
        if not any(u in (s.get("ucas") or []) for s in m.get("scenarios", [])):
            errs.append(f"{u}: no loss scenario explains it")
    if not errs:
        errs += route_errors(m)
    return errs


def route_errors(m: dict) -> list[str]:
    """An arrow at x from one box to another must stay inside both and cross no other box."""
    errs = []
    cts = {c["id"]: c["box"] for c in m["controllers"]}
    for ln in m["links"]:
        a, b = cts[ln["from"]], cts[ln["to"]]
        top, bot = (a, b) if a[1] < b[1] else (b, a)
        for key in ("x", "fx"):
            x = ln.get(key)
            if x is None:
                continue
            if not (a[0] < x < a[0] + a[2] and b[0] < x < b[0] + b[2]):
                errs.append(f"link {ln['from']}→{ln['to']}: {key}={x} is not within both boxes")
            for cid, c in cts.items():
                if cid in (ln["from"], ln["to"]):
                    continue
                if c[0] <= x <= c[0] + c[2] and top[1] + top[3] < c[1] < bot[1]:
                    errs.append(f"link {ln['from']}→{ln['to']}: {key}={x} crosses {cid}")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict) -> dict[str, str]:
    cts = {c["id"]: c["name"] for c in m["controllers"]}
    t = {}
    rows = ["| ID | Loss |", "|---|---|"] + [
        f"| {x['id']} | {cell(x['text'])} |" for x in m["losses"]
    ]
    t["stpa-losses"] = "\n".join(rows)
    rows = [
        "| ID | System-level hazard | Losses | HARA hazards | SOTIF hazards | UCAs |",
        "|---|---|---|---|---|---|",
    ]
    for x in m["hazards"]:
        n = sum(1 for _, _, u in ucas(m) if x["id"] in u["hz"])
        rows.append(
            f"| {x['id']} | {cell(x['text'])} | {', '.join(x['losses'])} | {', '.join(x.get('hara') or []) or '— (found by STPA)'} "
            f"| {', '.join(x.get('sotif') or []) or '—'} | {n} |"
        )
    t["stpa-hazards"] = "\n".join(rows)
    rows = [
        "| ID | Control action | From | To | Feedback to the controller |",
        "|---|---|---|---|---|",
    ]
    for ln in m["links"]:
        for a in ln["actions"]:
            rows.append(
                f"| {a['id']} | {cell(a['name'])} | {cts[ln['from']]} | {cts[ln['to']]} | {cell('; '.join(ln['feedback'])) or '—'} |"
            )
    t["stpa-actions"] = "\n".join(rows)
    rows = [
        "| Control action | " + " | ".join(TYPES.values()) + " |",
        "|---" * (len(TYPES) + 1) + "|",
    ]
    for _, a in actions(m):
        cells = []
        for ty in TYPES:
            v = a["ucas"][ty]
            if isinstance(v, dict):
                cells.append(f"*None: {cell(v['none'])}*")
            else:
                cells.append(
                    "<br>".join(
                        f"**{u['id']}** {cell(u['text'])} [{', '.join(u['hz'])}]" for u in v
                    )
                )
        rows.append(f"| {a['id']} {cell(a['name'])} | " + " | ".join(cells) + " |")
    t["stpa-ucas"] = "\n".join(rows)
    rows = [
        "| ID | Kind | Scenario | Explains | Measures in the concept | New requirements |",
        "|---|---|---|---|---|---|",
    ]
    for s in m["scenarios"]:
        rows.append(
            f"| {s['id']} | {s['kind'].capitalize()} | {cell(s['text'])} | {', '.join(s['ucas'])} "
            f"| {', '.join(s.get('measures') or []) or '—'} | {', '.join(s.get('new') or []) or '—'} |"
        )
    t["stpa-scenarios"] = "\n".join(rows)
    rows = ["| ID | Requirement | Allocated to | From |", "|---|---|---|---|"]
    for r in m["requirements"]:
        by = [s["id"] for s in m["scenarios"] if r["id"] in (s.get("new") or [])]
        rows.append(f"| {r['id']} | {cell(r['text'])} | {cell(r['to'])} | {', '.join(by)} |")
    t["stpa-requirements"] = "\n".join(rows)
    found = [x["id"] for x in m["hazards"] if not x.get("hara")]
    t["stpa-summary"] = (
        f"{len(m['losses'])} losses, {len(m['hazards'])} system-level hazards ({len(found)} not in the HARA: "
        f"{', '.join(found)}), {len(m['controllers'])} controllers, {len(actions(m))} control actions, "
        f"{len(ucas(m))} unsafe control actions, {len(m['scenarios'])} loss scenarios and "
        f"{len(m['requirements'])} new requirements. Every control action is examined for all four types, "
        f"every unsafe control action has a scenario, and every scenario a measure or a new requirement."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/08-analyses/stpa/stpa.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-A-05 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .box { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.6; }
svg .ctl { stroke:var(--ink2); stroke-width:1.5; fill:none; }
svg .fbk { stroke:var(--ink3); stroke-width:1.3; fill:none; stroke-dasharray:5 3; }
svg .hd { fill:var(--ink2); } svg .hf { fill:var(--ink3); }
svg .lab { font:600 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""


def arrow(x: float, y1: float, y2: float, cls: str, head: str) -> list[str]:
    d = 1 if y2 > y1 else -1
    tip = f"M{fk.num(x)} {fk.num(y2)} L{fk.num(x - 4)} {fk.num(y2 - 7 * d)} L{fk.num(x + 4)} {fk.num(y2 - 7 * d)} Z"
    return [
        fk.el(
            "path",
            None,
            d=f"M{fk.num(x)} {fk.num(y1)} L{fk.num(x)} {fk.num(y2 - 6 * d)}",
            class_=cls,
        ),
        fk.el("path", None, d=tip, class_=head),
    ]


def span(ids: list[str]) -> str:
    """CA-01, CA-02, CA-03 → CA-01–03 (the actions of a link are numbered consecutively)."""
    nums = [int(i[3:]) for i in ids]
    if len(ids) == 1 or nums != list(range(nums[0], nums[0] + len(nums))):
        return ", ".join(ids)
    return f"{ids[0]}–{ids[-1][3:]}"


def figure(m: dict) -> str:
    cts = {c["id"]: c for c in m["controllers"]}
    body = [
        fk.text(24, 32, "Control structure", "h"),
        fk.text(24, 54, "WP-A-05 §3: who controls whom; solid arrows carry control actions,", "t"),
        fk.text(24, 71, "dashed arrows feedback", "t"),
    ]
    for ln in m["links"]:
        a, b = cts[ln["from"]]["box"], cts[ln["to"]]["box"]
        down = a[1] < b[1]
        ya, yb = (a[1] + a[3], b[1]) if down else (a[1], b[1] + b[3])
        if ln["actions"]:
            body += arrow(ln["x"], ya, yb, "ctl", "hd")
            ids = [x["id"] for x in ln["actions"]]
            left = ln.get("label") == "left"
            lx = ln["x"] - 6 if left else ln["x"] + 6
            ly = ya + 26 if down else ya - 18  # in the gap next to the controller
            body.append(fk.text(lx, ly, span(ids), "lab", "end" if left else ""))
        fx = ln.get("fx", ln["x"] if not ln["actions"] else None)
        if fx is not None and ln["feedback"]:
            body += (
                arrow(fx, yb, ya, "fbk", "hf") if ln["actions"] else arrow(fx, ya, yb, "fbk", "hf")
            )
    for c in m["controllers"]:
        x, y, w, h = c["box"]
        body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=7, class_="box"))
        lines = fk.wrap(c["name"], w - 16, "tb")
        for n, s in enumerate(lines):
            body.append(
                fk.text(
                    x + w / 2, y + h / 2 + 5 + 16 * (n - (len(lines) - 1) / 2), s, "tb", "middle"
                )
            )
    y = max(c["box"][1] + c["box"][3] for c in m["controllers"]) + 34
    body += [
        fk.el("path", None, d=f"M24 {y - 5} L56 {y - 5}", class_="ctl"),
        fk.el("path", None, d=f"M62 {y - 5} L55 {y - 9} L55 {y - 1} Z", class_="hd"),
        fk.text(70, y, "Control actions (table in §3)", "t"),
        fk.el("path", None, d=f"M300 {y - 5} L332 {y - 5}", class_="fbk"),
        fk.el("path", None, d=f"M338 {y - 5} L331 {y - 9} L331 {y - 1} Z", class_="hf"),
        fk.text(346, y, "Feedback", "t"),
    ]
    y += 20
    desc = "Control structure: " + "; ".join(
        f"{cts[ln['from']]['name']} to {cts[ln['to']]['name']}: "
        + (", ".join(f"{a['id']} {a['name']}" for a in ln["actions"]) or "feedback only")
        + (f"; feedback: {', '.join(ln['feedback'])}" if ln["feedback"] else "")
        for ln in m["links"]
    )
    return fk.svg(W, int(y), "WP-A-05 Figure 3-1: control structure", desc + ".", body, EXTRA)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("stpa.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m)), FIG: figure(m)}


if __name__ == "__main__":
    fk.run(build, __doc__)
