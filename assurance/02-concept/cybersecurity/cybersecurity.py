#!/usr/bin/env python3
"""The cybersecurity goals, claims and concept of WP-C-10, generated from cybersecurity.yaml.

Writes the generated tables of WP-C-10 (goals with their CAL, claims, cybersecurity requirements
on the item and on its operational environment) and Figure 2-1 (from the TARA's threat scenarios
to goals or claims, and from goals to requirements). Whether a threat needs a goal or a claim
follows from its treatment in the TARA. This repository is public: attack vectors, risk values and
the rationale of each claim are restricted (WP-M-09 §4) and kept outside it, so each goal's CAL is
recorded, not computed.

The model is refused when:
- it carries a restricted field (see tara.RESTRICTED), or a claim carries its rationale;
- an identifier is malformed or repeated, or a CAL is unknown;
- a threat scenario whose risk is reduced has no goal, or one whose risk is retained has no claim,
  or a threat is in a goal and a claim, or in the wrong one;
- a goal has no requirement, or a requirement names a goal that does not exist;
- a requirement or claim names a source that does not exist;
- a control the TARA proposed is taken up by no requirement or claim.

    python3 cybersecurity.py            # write WP-C-10's generated tables and Figure 2-1
    python3 cybersecurity.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in ("01-management/figures", "02-concept/tara"):
    sys.path.insert(0, str(ASSURANCE / sub))
import figkit as fk  # noqa: E402
import tara  # noqa: E402

MODEL = HERE / "cybersecurity.yaml"
DOC = ASSURANCE / "02-concept" / "WP-C-10-cybersecurity-goals-and-concept.md"
FIG = HERE / "fig-c10-2-1-goals.svg"
CALS = ("CAL1", "CAL2", "CAL3", "CAL4")
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    t = tara.load()
    k = tara.known()
    return {
        "tara": t,
        "threats": {x["id"]: x for x in t["threats"]},
        "controls": {c["id"] for c in t["controls"]},
        "refs": k["refs"] | {c["id"] for c in t["controls"]},
    }


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = tara.restricted(m)
    t = k["tara"]
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, i):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    in_goal = {ts for g in m.get("goals", []) for ts in g.get("threats", [])}
    in_claim = {ts for c in m.get("claims", []) for ts in c.get("threats", [])}
    for ts, x in k["threats"].items():
        need = tara.treatment(t, x)
        if need == "Reduce" and ts not in in_goal:
            errs.append(f"{ts}: its risk is reduced but no goal covers it")
        if need == "Retain" and ts not in in_claim:
            errs.append(f"{ts}: its risk is retained but no claim gives the reason")
        if ts in in_goal and ts in in_claim:
            errs.append(f"{ts}: in both a goal and a claim")
        if need == "Retain" and ts in in_goal:
            errs.append(f"{ts}: retained in the TARA, so it needs a claim, not a goal")
        if need == "Reduce" and ts in in_claim:
            errs.append(f"{ts}: reduced in the TARA, so it needs a goal, not a claim")
    for ts in in_goal | in_claim:
        if ts not in k["threats"]:
            errs.append(f"{ts}: threat scenario does not exist")
    goals = {g["id"] for g in m.get("goals", [])}
    used = set()
    for g in m.get("goals", []):
        new(g["id"], r"CG-\d\d")
        if not g.get("text") or not g.get("threats"):
            errs.append(f"{g['id']}: needs text and threats")
        if g.get("cal") not in CALS:
            errs.append(f"{g['id']}: CAL must be one of {', '.join(CALS)}")
        if not any(g["id"] in r.get("goals", []) for r in m.get("requirements", [])):
            errs.append(f"{g['id']}: no requirement meets it")
    for c in m.get("claims", []):
        new(c["id"], r"CC-\d\d")
        if "text" in c:
            errs.append(f"{c['id']}: the rationale of a claim is restricted (WP-M-09 §4)")
        for x in c.get("controls") or []:
            if x not in k["controls"]:
                errs.append(f"{c['id']}: control {x} is not in the TARA")
            used.add(x)
    for r in m.get("requirements", []):
        new(r["id"], r"CSR-\d\d")
        if r.get("scope") not in ("item", "environment"):
            errs.append(f"{r['id']}: scope must be item or environment")
        for g in r.get("goals") or []:
            if g not in goals:
                errs.append(f"{r['id']}: goal {g} does not exist")
        for x in r.get("from") or []:
            if x not in k["refs"]:
                errs.append(f"{r['id']}: source {x} does not exist")
            used.add(x)
    for c in sorted(k["controls"] - used):
        errs.append(f"{c}: the TARA proposed it but no requirement or claim takes it up")
    return errs


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def tables(m: dict, k: dict) -> dict[str, str]:
    out = {}
    rows = [
        "| ID | Cybersecurity goal | Threats | CAL | Requirements |",
        "|---|---|---|---|---|",
    ]
    for g in m["goals"]:
        reqs = [r["id"] for r in m["requirements"] if g["id"] in r["goals"]]
        rows.append(
            f"| {g['id']} | {cell(g['text'])} | {', '.join(g['threats'])} | **{g['cal']}** | {', '.join(reqs)} |"
        )
    out["cs-goals"] = "\n".join(rows)
    rows = ["| ID | Threats | Rationale | Controls applied anyway |", "|---|---|---|---|"]
    for c in m["claims"]:
        rows.append(
            f"| {c['id']} | {', '.join(c['threats'])} | Restricted (WP-M-09 §4) | {', '.join(c['controls']) or '—'} |"
        )
    out["cs-claims"] = "\n".join(rows)
    for on in ("item", "environment"):
        rows = ["| ID | Requirement | Goals | Allocated to | From |", "|---|---|---|---|---|"]
        for r in m["requirements"]:
            if r["scope"] != on:
                continue
            rows.append(
                f"| {r['id']} | {cell(r['text'])} | {', '.join(r['goals'])} | {cell(r['element'])} | {', '.join(r['from']) or '— (new)'} |"
            )
        out[f"cs-{on}"] = "\n".join(rows)
    cals = [g["cal"] for g in m["goals"]]
    hist = ", ".join(
        f"{sum(1 for c in cals if c == x)} at {x}" for x in reversed(CALS) if x in cals
    )
    env = sum(1 for r in m["requirements"] if r["scope"] == "environment")
    out["cs-summary"] = (
        f"{len(m['goals'])} cybersecurity goals for the {len(set(x for g in m['goals'] for x in g['threats']))} threat "
        f"scenarios whose risk is reduced ({hist}), and {len(m['claims'])} claims for the risks retained. "
        f"{len(m['requirements'])} cybersecurity requirements meet the goals: {len(m['requirements']) - env} on the "
        f"item and {env} on its operational environment. Every control the TARA proposed is taken up."
    )
    return out


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/02-concept/cybersecurity/cybersecurity.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-C-10 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .goal { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.4; }
svg .claim { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; stroke-dasharray:4 3; }
svg .ts { fill:var(--card); stroke:var(--grid); stroke-width:1; }
svg .req { fill:var(--bg); stroke:var(--acc); stroke-width:1.2; }
svg .link { stroke:var(--ink3); stroke-width:1; fill:none; opacity:.7; }
svg .id { font:600 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .cal { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); }
svg .col { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); letter-spacing:.06em; }
"""


def figure(m: dict, k: dict) -> str:
    top, rh = 116, 24
    cx = {"ts": (24, 92), "mid": (228, 150), "req": (514, 102)}
    nodes = [(g["id"], "goal") for g in m["goals"]] + [(c["id"], "claim") for c in m["claims"]]
    threats = [i for g in m["goals"] for i in g["threats"]]
    threats += [i for c in m["claims"] for i in c["threats"]]
    reqs = [r["id"] for r in m["requirements"]]
    n = max(len(threats), len(nodes), len(reqs))
    pos = {}

    def place(ids: list[str], col: str) -> None:
        off = (n - len(ids)) * rh / 2
        for j, i in enumerate(ids):
            pos[(col, i)] = top + off + j * rh

    place(threats, "ts")
    place([i for i, _ in nodes], "mid")
    place(reqs, "req")
    body = [
        fk.text(24, 32, "From threats to goals and requirements", "h"),
        fk.text(24, 54, "WP-C-10 §2–4: each TARA threat goes to a goal (risk reduced) or a", "t"),
        fk.text(
            24, 71, "claim (risk retained); each goal is met by cybersecurity requirements", "t"
        ),
        fk.text(cx["ts"][0], top - 14, "THREATS", "col"),
        fk.text(cx["mid"][0], top - 14, "GOALS AND CLAIMS", "col"),
        fk.text(cx["req"][0], top - 14, "REQUIREMENTS", "col"),
    ]
    h = rh - 6

    def curve(x1: float, y1: float, x2: float, y2: float) -> str:
        mx = (x1 + x2) / 2
        return fk.el(
            "path",
            None,
            d=f"M{fk.num(x1)} {fk.num(y1)} C{fk.num(mx)} {fk.num(y1)} {fk.num(mx)} {fk.num(y2)} {fk.num(x2)} {fk.num(y2)}",
            class_="link",
        )

    for g in m["goals"]:
        for ts in g["threats"]:
            body.append(
                curve(
                    cx["ts"][0] + cx["ts"][1],
                    pos[("ts", ts)] + h / 2,
                    cx["mid"][0],
                    pos[("mid", g["id"])] + h / 2,
                )
            )
        for r in m["requirements"]:
            if g["id"] in r["goals"]:
                body.append(
                    curve(
                        cx["mid"][0] + cx["mid"][1],
                        pos[("mid", g["id"])] + h / 2,
                        cx["req"][0],
                        pos[("req", r["id"])] + h / 2,
                    )
                )
    for c in m["claims"]:
        for ts in c["threats"]:
            body.append(
                curve(
                    cx["ts"][0] + cx["ts"][1],
                    pos[("ts", ts)] + h / 2,
                    cx["mid"][0],
                    pos[("mid", c["id"])] + h / 2,
                )
            )
    for ts in threats:
        y = pos[("ts", ts)]
        body.append(
            fk.el(
                "rect",
                None,
                x=cx["ts"][0],
                y=fk.num(y),
                width=cx["ts"][1],
                height=h,
                rx=4,
                class_="ts",
            )
        )
        body.append(fk.text(cx["ts"][0] + 8, y + 13, ts, "id"))
    for i, kind in nodes:
        y = pos[("mid", i)]
        body.append(
            fk.el(
                "rect",
                None,
                x=cx["mid"][0],
                y=fk.num(y),
                width=cx["mid"][1],
                height=h,
                rx=4,
                class_=kind,
            )
        )
        body.append(fk.text(cx["mid"][0] + 8, y + 13, i, "id"))
        if kind == "goal":
            c = next(g for g in m["goals"] if g["id"] == i)["cal"]
            body.append(fk.text(cx["mid"][0] + cx["mid"][1] - 8, y + 13, c, "cal", "end"))
        else:
            body.append(fk.text(cx["mid"][0] + cx["mid"][1] - 8, y + 13, "retained", "s", "end"))
    for r in m["requirements"]:
        y = pos[("req", r["id"])]
        body.append(
            fk.el(
                "rect",
                None,
                x=cx["req"][0],
                y=fk.num(y),
                width=cx["req"][1],
                height=h,
                rx=4,
                class_="req",
            )
        )
        body.append(fk.text(cx["req"][0] + 8, y + 13, r["id"], "id"))
        body.append(
            fk.text(
                cx["req"][0] + cx["req"][1] - 8,
                y + 13,
                "env" if r["scope"] == "environment" else "item",
                "s",
                "end",
            )
        )
    y = top + n * rh + 22
    body.append(
        fk.text(
            24,
            y,
            "Goal label: CAL. Requirement label: on the item or its environment.",
            "s",
        )
    )
    y += 16
    desc = (
        "Goals: "
        + "; ".join(f"{g['id']} ({g['cal']}) from {', '.join(g['threats'])}" for g in m["goals"])
        + ". Claims: "
        + "; ".join(f"{c['id']} for {', '.join(c['threats'])}" for c in m["claims"])
        + ". Requirements: "
        + "; ".join(f"{r['id']} for {', '.join(r['goals'])}" for r in m["requirements"])
        + "."
    )
    return fk.svg(
        W, int(y), "WP-C-10 Figure 2-1: threats, goals and requirements", desc, body, EXTRA
    )


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("cybersecurity.yaml: " + "; ".join(errs))
    return {DOC: fill(DOC.read_text(encoding="utf-8"), tables(m, k)), FIG: figure(m, k)}


if __name__ == "__main__":
    fk.run(build, __doc__)
