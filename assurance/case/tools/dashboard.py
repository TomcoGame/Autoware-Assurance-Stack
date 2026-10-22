#!/usr/bin/env python3
"""The assurance dashboard: case/figures/dashboard.svg and the summary block of assurance/README.md.

Both are computed from records, never typed: the WP-M-00 register (work products, gates, status),
the decision register (questions waiting on the lead) and the safety case records (claims,
evidence, defeaters). A gate counts as passed only when every work product it needs is approved
or baselined.

    python3 dashboard.py            # write the figure and the README block
    python3 dashboard.py --check    # fail if either is stale
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
sys.path.insert(0, str(ASSURANCE / "01-management" / "decisions"))
sys.path.insert(0, str(HERE))
import caselib  # noqa: E402
import check_decisions  # noqa: E402
import figkit as fk  # noqa: E402
import wpregister  # noqa: E402

SVG = ASSURANCE / "case" / "figures" / "dashboard.svg"
README = ASSURANCE / "README.md"
BEGIN = "<!-- BEGIN GENERATED: assurance-summary (assurance/case/tools/dashboard.py) -->"
END = "<!-- END GENERATED: assurance-summary -->"
W = 640
DONE = ("A", "B")
STATUS_ORDER = ["B", "A", "R", "D", "S", "N/A"]


def summary(reg: wpregister.Register, dq: list[dict], rec: caselib.Records) -> dict:
    prods = reg.products
    passed = -1
    for gi in range(len(reg.gates)):
        need = [p for p in prods if gi in p.gates and p.status != "N/A"]
        if need and all(p.status in DONE for p in need):
            passed = gi
        else:
            break
    hara = next((p for p in prods if p.wid == "WP-C-03"), None)
    if passed >= 0:
        state = f"Gate {reg.gates[passed][0]} passed"
    elif hara is None or hara.status == "S":
        state = "Scaffold: no hazard analysis yet"
    else:
        state = f"Before G0: hazard analysis {fk.STATUS_NAME[hara.status].lower()}"
    counts = {s: sum(p.status == s for p in prods) for s in STATUS_ORDER}
    return {
        "state": state,
        "wp": len(prods),
        "wp_by": counts,
        "wp_done": sum(counts[s] for s in DONE),
        "dq_open": sum(d["status"] == "open" for d in dq),
        "dq_hard": sum(d["status"] == "open" and d["reversibility"] != "easy" for d in dq),
        "dq_waiting": sum(d["status"] == "answered" for d in dq),
        "dq_applied": sum(d["status"] == "applied" for d in dq),
        "claims": len(rec.claims),
        "claims_ok": sum(c.get("status") == "accepted" for c in rec.claims),
        "evidence": len(rec.evidence),
        "defeaters_open": sum(d.get("status") == "open" for d in rec.defeaters),
        "gates": [
            (
                g,
                name,
                {s: sum(gi in p.gates and p.status == s for p in prods) for s in STATUS_ORDER},
            )
            for gi, (g, name) in enumerate(reg.gates)
        ],
    }


def svg(s: dict) -> str:
    body = [
        fk.text(24, 32, "Assurance status", "h"),
        fk.text(24, 54, f"Autoware driverless safety case · {s['state']}", "t"),
    ]
    tiles = [
        ("Work products", s["wp"], f"{s['wp_done']} approved"),
        ("Decisions for you", s["dq_open"], f"{s['dq_hard']} not easy to undo"),
        ("Safety case claims", s["claims"], f"{s['claims_ok']} accepted"),
        ("Open defeaters", s["defeaters_open"], f"{s['evidence']} evidence items"),
    ]
    tw, gap, y = (W - 48 - 3 * 10) / 4, 10, 72
    for i, (label, value, sub) in enumerate(tiles):
        x = 24 + i * (tw + gap)
        body += [
            fk.el("rect", None, x=fk.num(x), y=y, width=fk.num(tw), height=88, rx=6, class_="card"),
            fk.text(x + 12, y + 22, fk.fit(label, tw - 20, "s"), "s"),
            fk.text(x + 12, y + 56, str(value), "big"),
        ]
        for j, ln in enumerate(fk.wrap(sub, tw - 20, "s")[:1]):
            body.append(fk.text(x + 12, y + 76 + 14 * j, fk.fit(ln, tw - 20, "s"), "s"))
    y += 120
    body.append(fk.text(24, y, "Work products each gate needs, by status", "tb"))
    y += 12
    xb, xe = 252, W - 56
    most = max(sum(c.values()) for _, _, c in s["gates"]) or 1
    for g, name, c in s["gates"]:
        y += 30
        body.append(fk.text(24, y, g, "tb"))
        body.append(fk.text(52, y, fk.fit(name, xb - 60, "t"), "t"))
        x = xb
        for st in STATUS_ORDER:
            n = c[st]
            if not n:
                continue
            w = (xe - xb) * n / most
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(x),
                    y=y - 12,
                    width=fk.num(max(w - 2, 2)),
                    height=16,
                    rx=3,
                    class_=fk.STATUS_CLASS[st],
                )
            )
            x += w
        body.append(fk.text(x + 6, y, str(sum(c.values())), "tb"))
    y += 34
    x = 24
    for st in STATUS_ORDER:
        n = s["wp_by"][st]
        if not n:
            continue
        label = f"{fk.STATUS_NAME[st]} ({n})"
        body += [
            fk.el(
                "rect", None, x=x, y=y - 11, width=22, height=14, rx=3, class_=fk.STATUS_CLASS[st]
            ),
            fk.text(x + 28, y, label, "t"),
        ]
        x += 28 + fk.width(label, "t") + 18
    y += 24
    desc = (
        f"{s['state']}. "
        + "; ".join(f"{a}: {b} ({c})" for a, b, c in tiles)
        + ". Work products needed per gate: "
        + "; ".join(f"{g} {name} {sum(c.values())}" for g, name, c in s["gates"])
        + "."
    )
    big = "svg .big { font:600 30px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); font-variant-numeric:tabular-nums; }"
    return fk.svg(W, int(y), "Assurance status dashboard", desc, body, big)


def block(s: dict) -> str:
    by = ", ".join(f"{n} {fk.STATUS_NAME[st].lower()}" for st, n in s["wp_by"].items() if n)
    rows = [
        ("Assurance state", s["state"]),
        ("Work products in the register", f"{s['wp']} ({by})"),
        ("Work products approved or baselined", s["wp_done"]),
        ("Decisions waiting on the safety authority", f"{s['dq_open']} open"),
        ("Decisions applied", s["dq_applied"]),
        ("Safety case claims", s["claims"]),
        ("Evidence items", s["evidence"]),
        ("Open defeaters", s["defeaters_open"]),
    ]
    return "\n".join(
        [
            BEGIN,
            "",
            "| Indicator | Value |",
            "|---|---|",
            *(f"| {a} | {b} |" for a, b in rows),
            "",
            END,
        ]
    )


def build() -> dict[Path, str]:
    rec = caselib.load()
    errs = caselib.check(rec)
    if errs:
        raise fk.FigureError("safety case records do not validate: " + "; ".join(errs))
    s = summary(wpregister.load(), check_decisions.load(), rec)
    readme = README.read_text(encoding="utf-8")
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise fk.FigureError(
            "assurance/README.md needs exactly one generated assurance-summary block"
        )
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block(s), readme, flags=re.S)
    return {SVG: svg(s), README: new}


if __name__ == "__main__":
    fk.run(build, __doc__)
