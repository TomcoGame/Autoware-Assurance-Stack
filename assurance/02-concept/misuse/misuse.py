#!/usr/bin/env python3
"""Human interaction and foreseeable misuse of WP-C-08, generated from misuse.yaml.

Writes the generated tables of WP-C-08 (roles, interactions and misuse by role, resulting
requirements) and Figure 5-1 (every entry by role and kind, marked where it needs a new
requirement).

The model is refused when:
- an identifier is malformed or repeated, or a kind is unknown;
- an entry names a role that does not exist, or an analysis item (hazard, UCA, triggering
  condition, insufficiency, threat) or measure that does not exist;
- an entry has neither a measure already in the concept nor a new requirement, or is pending on a
  decision that is no longer open;
- a role has no entry, or a new requirement is used by no entry.

    python3 misuse.py            # write WP-C-08's generated tables and Figure 5-1
    python3 misuse.py --check    # fail if either is stale or the model breaks a rule
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
    "02-concept/ai",
    "08-analyses/stpa",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import ai  # noqa: E402
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import stpa  # noqa: E402

MODEL = HERE / "misuse.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-08-human-interaction-misuse-analysis.md"
FIG = HERE / "fig-c08-5-1-entries.svg"
KINDS = {"misuse": "Misuse", "error": "Error", "interaction": "Interaction"}
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    a = ai.known()
    s = stpa.load()
    t = ai.triggering.load()
    tara = ai.cybersecurity.tara.load()
    items = (
        a["hazards"]
        | {h["id"] for h in s["hazards"]}
        | {u["id"] for _, _, u in stpa.ucas(s)}
        | {x["id"] for x in t["insufficiencies"]}
        | {x["id"] for x in t["triggers"]}
        | {x["id"] for x in tara["threats"]}
    )
    return {
        "measures": a["refs"],
        "items": items,
        "decisions": {d["id"]: d["status"] for d in check_decisions.load()},
    }


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    roles = {r["id"] for r in m.get("roles", [])}
    hrs = {r["id"] for r in m.get("requirements", [])}
    used: set[str] = set()
    for r in m.get("roles", []):
        new(r["id"], r"R-\d\d")
        if not any(e.get("role") == r["id"] for e in m.get("entries", [])):
            errs.append(f"{r['id']}: no interaction or misuse for this role")
    for e in m.get("entries", []):
        i = e["id"]
        new(i, r"MU-\d\d")
        if e.get("role") not in roles:
            errs.append(f"{i}: role {e.get('role')} does not exist")
        if e.get("kind") not in KINDS:
            errs.append(f"{i}: kind must be one of {', '.join(KINDS)}")
        for key in ("situation", "consequence"):
            if not e.get(key):
                errs.append(f"{i}: missing {key}")
        for x in e.get("refs") or []:
            if x not in k["items"]:
                errs.append(f"{i}: {x} does not exist")
        for x in e.get("measures") or []:
            if x not in k["measures"]:
                errs.append(f"{i}: measure {x} does not exist")
        for x in e.get("new") or []:
            if x not in hrs:
                errs.append(f"{i}: new requirement {x} does not exist")
            used.add(x)
        if not e.get("measures") and not e.get("new"):
            errs.append(f"{i}: has neither a measure nor a new requirement")
        p = e.get("pending")
        if p and k["decisions"].get(p) not in ("open", "queued"):
            errs.append(
                f"{i}: pending on {p}, which is {k['decisions'].get(p, 'not in the register')}; apply the decision"
            )
    for r in m.get("requirements", []):
        new(r["id"], r"HR-\d\d")
        if r["id"] not in used:
            errs.append(f"{r['id']}: no entry needs it")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict) -> dict[str, str]:
    t = {}
    names = {r["id"]: r["name"] for r in m["roles"]}
    rows = ["| ID | Role | Misuse | Errors | Interactions |", "|---|---|---|---|---|"]
    for r in m["roles"]:
        es = [e for e in m["entries"] if e["role"] == r["id"]]
        rows.append(
            f"| {r['id']} | {cell(r['name'])} | "
            + " | ".join(", ".join(e["id"] for e in es if e["kind"] == kd) or "—" for kd in KINDS)
            + " |"
        )
    t["misuse-roles"] = "\n".join(rows)
    for block, role_ids in (("misuse-people", None), ("misuse-remote", {"R-06"})):
        rows = [
            "| ID | Role | Kind | Situation | Consequence | Related | Measures in the concept | New |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for e in m["entries"]:
            if (role_ids is None) == (e["role"] in {"R-06"}):
                continue
            new = ", ".join(e.get("new") or []) + (
                f" (proposed, {e['pending']})" if e.get("pending") else ""
            )
            rows.append(
                f"| {e['id']} | {cell(names[e['role']])} | {KINDS[e['kind']]} | {cell(e['situation'])} | {cell(e['consequence'])} "
                f"| {', '.join(e['refs'])} | {', '.join(e['measures']) or '—'} | {new or '—'} |"
            )
        t[block] = "\n".join(rows)
    rows = ["| ID | Requirement | Allocated to | From |", "|---|---|---|---|"]
    for r in m["requirements"]:
        by = [e["id"] for e in m["entries"] if r["id"] in (e.get("new") or [])]
        rows.append(f"| {r['id']} | {cell(r['text'])} | {cell(r['to'])} | {', '.join(by)} |")
    t["misuse-requirements"] = "\n".join(rows)
    n = {kd: sum(1 for e in m["entries"] if e["kind"] == kd) for kd in KINDS}
    needs = sum(1 for e in m["entries"] if e.get("new"))
    pend = sorted({e["pending"] for e in m["entries"] if e.get("pending")})
    t["misuse-summary"] = (
        f"{len(m['roles'])} human roles and {len(m['entries'])} entries: {n['misuse']} foreseeable misuse, "
        f"{n['error']} errors by trained people, {n['interaction']} interactions the item must support. "
        f"{len(m['entries']) - needs} are met by measures already in the concept; {needs} need one of the "
        f"{len(m['requirements'])} new requirements"
        + (f", and entries marked proposed wait on {', '.join(pend)}." if pend else ".")
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/misuse/misuse.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-08 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


# Kinds by form and shade: misuse filled amber, error outlined red, interaction outlined blue; a dot marks an
# entry that needs a new requirement.
EXTRA = """svg .misuse { fill:var(--ambsoft); stroke:var(--amb); stroke-width:1.4; }
svg .error { fill:var(--badsoft); stroke:var(--bad); stroke-width:1.4; }
svg .interaction { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.4; }
svg .chip { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .dot { fill:var(--ink); }
"""


def figure(m: dict) -> str:
    x0, top, rh, cw, ch, gap = 200, 96, 34, 50, 20, 5
    body = [
        fk.text(24, 32, "Interactions and misuse by role", "h"),
        fk.text(24, 54, "WP-C-08 §2–5: what each kind of person may do with the vehicle; a", "t"),
        fk.text(24, 71, "dot marks an entry that needs a new requirement", "t"),
    ]
    for i, r in enumerate(m["roles"]):
        y = top + i * rh
        lines = fk.wrap(r["name"], x0 - 34, "s")[:2]
        for n, ln in enumerate(lines):
            body.append(
                fk.text(
                    24, y + 15 - 7 * (len(lines) - 1) + 14 * n, ln, "s" if len(lines) > 1 else "t"
                )
            )
        es = [e for e in m["entries"] if e["role"] == r["id"]]
        if x0 + len(es) * (cw + gap) > W - 16:
            raise fk.FigureError(f"Figure 5-1 has no room for {len(es)} entries of {r['id']}")
        for j, e in enumerate(es):
            cx = x0 + j * (cw + gap)
            body.append(
                fk.el("rect", None, x=cx, y=y + 1, width=cw, height=ch, rx=4, class_=e["kind"])
            )
            body.append(fk.text(cx + 5, y + 15, e["id"], "chip"))
            if e.get("new"):
                body.append(fk.el("circle", None, cx=cx + cw - 6, cy=y + 11, r=3, class_="dot"))
    y = top + len(m["roles"]) * rh + 24
    lx = 24
    for kd, label in KINDS.items():
        body.append(fk.el("rect", None, x=lx, y=y - 13, width=26, height=18, rx=4, class_=kd))
        body.append(fk.text(lx + 34, y, label, "t"))
        lx += 34 + fk.width(label, "t") + 28
    body.append(fk.el("circle", None, cx=lx + 6, cy=y - 4, r=3, class_="dot"))
    body.append(fk.text(lx + 16, y, "Needs a new requirement", "t"))
    y += 20
    desc = "Entries by role: " + "; ".join(
        f"{r['name']}: "
        + ", ".join(
            f"{e['id']} {e['kind']}{' (new requirement)' if e.get('new') else ''}"
            for e in m["entries"]
            if e["role"] == r["id"]
        )
        for r in m["roles"]
    )
    return fk.svg(
        W, int(y), "WP-C-08 Figure 5-1: interactions and misuse by role", desc + ".", body, EXTRA
    )


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("misuse.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m)), FIG: figure(m)}


if __name__ == "__main__":
    fk.run(build, __doc__)
