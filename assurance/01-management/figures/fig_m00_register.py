#!/usr/bin/env python3
"""WP-M-00 Figure 3-1: work products by folder section and gate, one dot per work product.

Rows are the §3 sections of the register, columns the gates of §2. Each cell holds one dot for
every work product of that section the gate needs, coloured by its status. A work product needed
at several gates has a dot in each. The bottom row totals each gate.

    python3 fig_m00_register.py            # write figures/fig-m00-3-1-wp-status.svg
    python3 fig_m00_register.py --check    # fail if it is stale
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figkit as fk  # noqa: E402
import wpregister  # noqa: E402

OUT = HERE / "fig-m00-3-1-wp-status.svg"
W = 640
X0 = 24  # left margin
XG = 214  # first gate column
DOT, GAP, PER_ROW = 8, 2, 5
DOT_STYLE = ".st-s.dot { stroke-dasharray:none; fill:none; stroke-width:1.2; }"


def short(title: str) -> str:
    """A section title up to its first comma or 'and': 'Production, operation and …' → 'Production'."""
    return re.split(r",| and ", title)[0]


def build_svg(reg: wpregister.Register) -> str:
    gates = [g for g, _ in reg.gates]
    gw = (W - X0 - XG) / len(gates)
    body = [
        fk.text(X0, 32, "Work products by gate and status", "h"),
        fk.text(X0, 54, "WP-M-00 §3: one dot per work product at each gate that needs it", "t"),
        fk.el("line", None, x1=X0, y1=68, x2=W - X0, y2=68, class_="hair"),
    ]
    y = 92
    for i, g in enumerate(gates):
        body.append(fk.text(XG + gw * i + gw / 2, y, g, "tb", "middle"))
    y += 10
    totals = [{} for _ in gates]
    for k, (num, title, folder) in enumerate(reg.sections):
        prods = [p for p in reg.products if p.section == num]
        per_gate = [[p for p in prods if gi in p.gates] for gi in range(len(gates))]
        rows = max([1] + [-(-len(c) // PER_ROW) for c in per_gate])
        h = max(38, 14 + rows * (DOT + GAP) + 10)
        if k % 2 == 0:
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=X0 - 8,
                    y=fk.num(y),
                    width=W - 2 * (X0 - 8),
                    height=h,
                    rx=4,
                    class_="card",
                )
            )
        body.append(fk.text(X0, y + 17, fk.fit(f"{num} {short(title)}", XG - X0 - 10, "tb"), "tb"))
        body.append(fk.text(X0, y + 31, f"{folder}/ · {len(prods)}", "s"))
        for gi, cell in enumerate(per_gate):
            span = min(len(cell), PER_ROW) * (DOT + GAP) - GAP
            cx = XG + gw * gi + (gw - span) / 2
            for n, p in enumerate(sorted(cell, key=lambda p: p.wid)):
                r, c = divmod(n, PER_ROW)
                body.append(
                    fk.el(
                        "rect",
                        None,
                        x=fk.num(cx + c * (DOT + GAP)),
                        y=fk.num(y + 11 + r * (DOT + GAP)),
                        width=DOT,
                        height=DOT,
                        rx=1.5,
                        class_=fk.STATUS_CLASS[p.status] + " dot",
                    )
                )
                totals[gi][p.status] = totals[gi].get(p.status, 0) + 1
        y += h
    body.append(
        fk.el("line", None, x1=X0, y1=fk.num(y + 6), x2=W - X0, y2=fk.num(y + 6), class_="hair")
    )
    y += 26
    body.append(fk.text(X0, y, "Needed at gate", "tb"))
    for gi, t in enumerate(totals):
        body.append(fk.text(XG + gw * gi + gw / 2, y, str(sum(t.values())), "tb", "middle"))
    y += 30
    x = X0
    present = sorted({p.status for p in reg.products}, key=list(fk.STATUS_CLASS).index)
    for s in present:
        n = sum(1 for p in reg.products if p.status == s)
        label = f"{fk.STATUS_NAME[s]} ({n})"
        body += [
            fk.el(
                "rect",
                None,
                x=x,
                y=fk.num(y - 9),
                width=DOT + 2,
                height=DOT + 2,
                rx=1.5,
                class_=fk.STATUS_CLASS[s] + " dot",
            ),
            fk.text(x + 16, y, label, "t"),
        ]
        x += 16 + fk.width(label, "t") + 18
    y += 20
    desc = (
        f"{len(reg.products)} work products in {len(reg.sections)} register sections. "
        + " ".join(
            f"{g}: {sum(t.values())} work products"
            + (
                " ("
                + ", ".join(f"{v} {fk.STATUS_NAME[s].lower()}" for s, v in sorted(t.items()))
                + ")"
                if t
                else ""
            )
            + "."
            for g, t in zip(gates, totals)
        )
        + " By section: "
        + "; ".join(
            f"{num} {title}: "
            + ", ".join(
                f"{p.wid} {fk.STATUS_NAME[p.status].lower()} at {p.gate_text}"
                for p in reg.products
                if p.section == num
            )
            for num, title, _ in reg.sections
        )
        + "."
    )
    return fk.svg(
        W, int(y), "Work products by gate and status (WP-M-00 Figure 3-1)", desc, body, DOT_STYLE
    )


def build() -> dict[Path, str]:
    return {OUT: build_svg(wpregister.load())}


if __name__ == "__main__":
    fk.run(build, __doc__)
