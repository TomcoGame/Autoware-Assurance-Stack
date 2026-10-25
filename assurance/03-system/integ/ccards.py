"""Integration test case sheet for WP-S-08: one card per test case, showing what it runs on and what it proves.

integ.py calls `sheet()` with the cases already worked out and writes Figure 4-1 next to the integration files. Each
card shows the architecture of WP-S-03 in small as it stands at the case's integration step: components not yet
integrated are faint, those already integrated grey, those the step adds outlined, and those the case exercises
(the components its requirements, signals and cybersecurity requirements sit on) filled. Under it: the environment,
the methods, how many requirements, signals and cybersecurity requirements it covers, the time budgets it measures
and its pass criterion.

No case has been run; nothing here is a result.
"""

from __future__ import annotations

import math

import cards as tsc_cards
import figkit as fk

CW, CH = 330, 430
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
SX, SY, OX, OY = 0.5, 0.4, 24, 96  # Figure 2-1 of WP-S-03 at card scale


def arch(ox: float, oy: float, comps: list[dict], state: dict[str, str]) -> list[str]:
    out = [fk.el("rect", None, x=ox - 6, y=oy - 6, width=312, height=162, rx=6, class_="verge")]
    for c in comps:
        x, y, w, h = c["box"]
        x, y, w, h = ox + (x - OX) * SX, oy + (y - OY) * SY, w * SX, h * SY
        cls = state[c["id"]]
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x),
                y=fk.num(y),
                width=fk.num(w),
                height=fk.num(h),
                rx=3,
                class_=cls,
            )
        )
        label = fk.fit(tsc_cards.SHORT.get(c["id"], c["name"]), (w - 4) * 11.5 / 9.5, "s")
        if h >= 16:
            out.append(fk.text(x + w / 2, y + h / 2 + 3.5, label, cls + "t", "middle"))
    return out


def card(x: float, y: float, c: dict, comps: list[dict]) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, c["id"], "gid"))
    px = x + CW - 14
    for text, cls in (
        (c["asil"], "pa" if c["asil"] != "—" else "pn"),
        (c["env"], "pn"),
        (c["step"], "ps"),
    ):
        if text == "—":
            continue
        label = f"ASIL {text}" if cls == "pa" else text
        w = fk.width(label, "m") * 0.85 + 12
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(px - w),
                y=y + 11,
                width=fk.num(w),
                height=18,
                rx=4,
                class_=cls,
            )
        )
        out.append(fk.text(px - w / 2, y + 24, label, cls + "t", "middle"))
        px -= w + 6
    for i, ln in enumerate(fk.wrap(c["name"], CW - 28, "tb")[:2]):
        out.append(fk.text(x + 14, y + 46 + 16 * i, ln, "tb"))
    out += arch(x + 15, y + 82, comps, c["state"])
    yy = y + 256
    out.append(fk.text(x + 14, yy, c["env_name"], "hd"))
    yy += 16
    mx = x + 14
    for meth in c["methods"]:
        w = fk.width(meth, "s") + 10
        if mx + w > x + CW - 14:
            mx = x + 14
            yy += 20
        out.append(
            fk.el(
                "rect", None, x=fk.num(mx), y=yy - 12, width=fk.num(w), height=16, rx=8, class_="mp"
            )
        )
        out.append(fk.text(mx + w / 2, yy, meth, "mpt", "middle"))
        mx += w + 5
    yy += 20
    out.append(fk.text(x + 14, yy, c["covers"], "ax"))
    yy += 14
    for ln in fk.wrap(c["budgets"], CW - 28, "s")[:2]:
        out.append(fk.text(x + 14, yy, ln, "ax"))
        yy += 14
    yy += 6
    out.append(fk.text(x + 14, yy, "Passes when", "hd"))
    yy += 15
    for ln in fk.wrap(c["pass"], CW - 28, "s")[:6]:
        out.append(fk.text(x + 14, yy, ln, "s"))
        yy += 14
    return out


EXTRA = """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --a3:#d4644a; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --a3:#bb4f34; } }
svg .verge { fill:var(--bg); stroke:var(--grid); stroke-width:1; }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .hd { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .ps { fill:var(--monsoft); stroke:var(--mon); stroke-width:1; } svg .pst { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--mon); }
svg .pn { fill:var(--card); stroke:var(--ink3); stroke-width:1; } svg .pnt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .pa { fill:var(--a3); } svg .pat { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:#ffffff; }
svg .ex { fill:var(--mon); } svg .ext { font:600 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .add { fill:var(--monsoft); stroke:var(--mon); stroke-width:1.4; } svg .addt { font:600 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--mon); }
svg .has { fill:var(--card); stroke:var(--ink3); stroke-width:1; } svg .hast { font:9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .not { fill:none; stroke:var(--grid); stroke-width:1; stroke-dasharray:3 2; } svg .nott { font:9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--grid); }
svg .mp { fill:var(--card); stroke:var(--grid); stroke-width:1; } svg .mpt { font:10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
"""


def sheet(cases: list[dict], comps: list[dict]) -> str:
    rows = math.ceil(len(cases) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "What each integration test runs on, and what it proves", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-08 §4, Figure 4-1: each case on the architecture as it stands at its step (faint not yet "
            "integrated, grey integrated, outlined added at",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "the step, filled exercised by the case), its environment, methods, coverage, time budgets and pass "
            "criterion. No case has been run.",
            "t",
        ),
    ]
    for i, c in enumerate(cases):
        body += card(MARGIN + (i % COLS) * (CW + GAP), HEAD + (i // COLS) * (CH + GAP), c, comps)
    ly = h - 26
    lx = MARGIN
    for cls, label in (
        ("ex", "exercised by the case"),
        ("add", "added at its step"),
        ("has", "already integrated"),
        ("not", "not yet integrated"),
    ):
        body += [
            fk.el("rect", None, x=lx, y=ly - 12, width=22, height=14, rx=3, class_=cls),
            fk.text(lx + 30, ly, label, "t"),
        ]
        lx += 30 + fk.width(label, "t") + 24
    desc = "Integration test cases: " + "; ".join(
        f"{c['id']} {c['name']} at {c['step']} in {c['env']}, exercising "
        + ", ".join(k for k, v in c["state"].items() if v == "ex")
        for c in cases
    )
    return fk.svg(w, h, "WP-S-08 Figure 4-1: integration test cases", desc + ".", body, EXTRA)
