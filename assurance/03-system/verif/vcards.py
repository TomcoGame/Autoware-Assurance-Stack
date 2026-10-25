"""Verification sheet for WP-S-09: one card per safety goal, and two for the SOTIF measures.

verif.py calls `sheet()` with the coverage already worked out and writes Figure 2-2 next to the verification files.
A safety goal's card lists each of its functional safety requirements with the verification cases that verify it,
as chips coloured by where the case runs (simulation, HIL, bench, closed track, or review only). The two SOTIF cards
do the same for the triggering conditions of WP-C-06 by category and the functional modifications of WP-C-07 by type.
Figure 2-1 reads the same coverage case by case; this one reads it requirement by requirement.

No case has been run; a chip says a case is planned to verify the requirement, not that it has.
"""

from __future__ import annotations

import math

import figkit as fk

CW = 330
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
CHIP_W, CHIP_H, CHIP_GAP = 42, 15, 4
ROW_X = 128  # where the chips start inside a card
ENV_CLASS = {"ENV-1": "e1", "ENV-2": "e2", "ENV-3": "e3", "ENV-4": "e4", None: "e0"}


def chips_lines(n: int) -> int:
    per = int((CW - ROW_X - 14 + CHIP_GAP) // (CHIP_W + CHIP_GAP))
    return max(1, math.ceil(n / per)) if n else 1


def row_h(r: dict) -> float:
    return chips_lines(len(r["cases"])) * (CHIP_H + 3) + 6


def chips(x: float, y: float, cases: list[tuple[str, str | None]]) -> list[str]:
    out = []
    per = int((CW - ROW_X - 14 + CHIP_GAP) // (CHIP_W + CHIP_GAP))
    for i, (vc, env) in enumerate(cases):
        cx = x + (i % per) * (CHIP_W + CHIP_GAP)
        cy = y + (i // per) * (CHIP_H + 3)
        cls = ENV_CLASS[env]
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(cx),
                y=fk.num(cy),
                width=CHIP_W,
                height=CHIP_H,
                rx=7,
                class_=cls,
            )
        )
        out.append(fk.text(cx + CHIP_W / 2, cy + 11, vc, cls + "t", "middle"))
    if not cases:
        out.append(fk.text(x, y + 11, "no case", "bad"))
    return out


def card(x: float, y: float, c: dict, h: float) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=fk.num(h), rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, c["id"], "gid"))
    if c.get("asil"):
        label = c["asil"] if c["asil"] == "QM" else f"ASIL {c['asil']}"
        w = fk.width(label, "m") * 0.85 + 12
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x + CW - 14 - w),
                y=y + 11,
                width=fk.num(w),
                height=18,
                rx=4,
                class_="pa",
            )
        )
        out.append(fk.text(x + CW - 14 - w / 2, y + 24, label, "pat", "middle"))
    lines = fk.wrap(c["title"], CW - 28, "tb")[:3]
    for i, ln in enumerate(lines):
        out.append(fk.text(x + 14, y + 44 + 16 * i, ln, "tb"))
    yy = y + top(c)
    for r in c["rows"]:
        out.append(fk.text(x + 14, yy + 11, r["id"], "rid"))
        if r.get("sub"):
            out.append(fk.text(x + 14, yy + 23, fk.fit(r["sub"], ROW_X - 18, "s"), "ax"))
        out += chips(x + ROW_X, yy, r["cases"])
        yy += max(row_h(r), 30 if r.get("sub") else 0)
    return out


def top(c: dict) -> float:
    return 38 + 16 * len(fk.wrap(c["title"], CW - 28, "tb")[:3])


def height(c: dict) -> float:
    return top(c) + sum(max(row_h(r), 30 if r.get("sub") else 0) for r in c["rows"]) + 14


EXTRA = """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --a3:#d4644a; --e1:#7c5cc4; --e2:#2d55c8; --e3:#23875a; --e4:#b97800; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --a3:#bb4f34; --e1:#b49cf0; --e2:#86a2ff; --e3:#45b882; --e4:#e7a52a; } }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .bad { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bad); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .rid { font:600 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .pa { fill:var(--a3); } svg .pat { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:#ffffff; }
svg .e1 { fill:none; stroke:var(--e1); stroke-width:1.3; } svg .e1t { font:600 9.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--e1); }
svg .e2 { fill:none; stroke:var(--e2); stroke-width:1.3; } svg .e2t { font:600 9.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--e2); }
svg .e3 { fill:none; stroke:var(--e3); stroke-width:1.3; } svg .e3t { font:600 9.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--e3); }
svg .e4 { fill:none; stroke:var(--e4); stroke-width:1.3; } svg .e4t { font:600 9.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--e4); }
svg .e0 { fill:none; stroke:var(--ink3); stroke-width:1.2; stroke-dasharray:3 2; } svg .e0t { font:600 9.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink3); }
"""


def sheet(cards: list[dict], envs: dict[str, str]) -> str:
    rows = [cards[i : i + COLS] for i in range(0, len(cards), COLS)]
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    body = [
        fk.text(MARGIN, 34, "How each safety goal and SOTIF measure is verified", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-09 §2, Figure 2-2: each requirement of each safety goal, and the triggering conditions and "
            "modifications by kind, with the cases that",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "verify them, coloured by where each case runs. No case has been run; a chip is a plan, not a result.",
            "t",
        ),
    ]
    y = HEAD
    for row in rows:
        rh = max(height(c) for c in row)
        for i, c in enumerate(row):
            body += card(MARGIN + i * (CW + GAP), y, c, rh)
        y += rh + GAP
    ly = y + 24
    lx = MARGIN
    for env, label in list(envs.items()) + [(None, "review only")]:
        cls = ENV_CLASS[env]
        body += [
            fk.el("rect", None, x=lx, y=ly - 12, width=26, height=CHIP_H, rx=7, class_=cls),
            fk.text(lx + 34, ly, label, "t"),
        ]
        lx += 34 + fk.width(label, "t") + 22
        if lx > w - 260:
            lx, ly = MARGIN, ly + 24
    desc = "Verification by requirement: " + "; ".join(
        f"{c['id']}: "
        + ", ".join(
            f"{r['id']} by {', '.join(v for v, _ in r['cases']) or 'no case'}" for r in c["rows"]
        )
        for c in cards
    )
    return fk.svg(
        w, int(ly + 22), "WP-S-09 Figure 2-2: verification by requirement", desc + ".", body, EXTRA
    )
