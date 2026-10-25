"""FTTI sheet for WP-S-04: one card per safety goal, showing how its fault tolerant time interval comes about.

timing.py calls `sheet()` and writes Figure 2-2 next to the timing files. Each card plots, on one time axis shared by
every card, how far a fault moves the vehicle (x = a t² / 2 for a deviation goal, x = v t for a drift goal) for the
largest and the smallest fault the candidate vehicles can produce, the margin it must not reach, and the FTTI where it
does. Under the plot, the worst-case FTTI is split into the share for detecting the fault, the share for reacting and
the reserve, on the same time axis. A derived goal shows the goal that binds it; a goal met by a limit says so.

Every number on a card is computed from timing.yaml by the same functions as the WP-S-04 tables; none is measured.
"""

from __future__ import annotations

import math

import figkit as fk

CW, CH = 330, 386
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
TMAX = 1.0  # s, the time axis of every card
PX0, PX1, PY0, PY1 = 46, 300, 14, 132  # plot area inside a card's drawing


def binding(m: dict, gid: str, ftti) -> str | None:
    """The goal whose curve sets a goal's FTTI: itself, or for a derived goal the one it takes the shortest from."""
    g = next(x for x in m["goals"] if x["id"] == gid)
    if g["kind"] == "limit":
        return None
    if g["kind"] == "derived":
        src = [x for x in g["from"] if ftti(m, x, "high") is not None]
        return binding(m, min(src, key=lambda x: ftti(m, x, "high")), ftti) if src else None
    return gid


def curve(g: dict, m: dict, bound: str) -> list[tuple[float, float]]:
    """(t, x) for the fault of the given bound, over the card's time axis."""
    r = m["ranges"][g["range"]][bound]
    pts = []
    for i in range(61):
        t = TMAX * i / 60
        pts.append((t, r * t * t / 2 if g["kind"] == "deviation" else r * t))
    return pts


def card(x: float, y: float, gid: str, m: dict, k: dict, ftti, ms, mech: list[str]) -> list[str]:
    g = next(z for z in m["goals"] if z["id"] == gid)
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, gid, "gid"))
    kind = g["kind"] + (f" from {', '.join(g['from'])}" if g["kind"] == "derived" else "")
    pw = fk.width(kind, "s") + 14
    out.append(
        fk.el(
            "rect",
            None,
            x=fk.num(x + CW - 14 - pw),
            y=y + 11,
            width=fk.num(pw),
            height=18,
            rx=4,
            class_="kp",
        )
    )
    out.append(fk.text(x + CW - 14 - pw / 2, y + 24, kind, "kpt", "middle"))
    for i, ln in enumerate(fk.wrap(k["goals"][gid]["statement"], CW - 28, "tb")[:3]):
        out.append(fk.text(x + 14, y + 44 + 16 * i, ln, "tb"))
    ox, oy = x + 8, y + 86
    b = binding(m, gid, ftti)
    X = lambda t: ox + PX0 + (PX1 - PX0) * min(t, TMAX) / TMAX  # noqa: E731
    out.append(fk.el("rect", None, x=ox, y=oy, width=CW - 16, height=PY1 + 30, rx=6, class_="plot"))
    if b is None:
        out.append(fk.text(x + CW / 2, oy + 70, "met by a limit, not by time", "dmt", "middle"))
        out.append(fk.text(x + CW / 2, oy + 88, "no FTTI", "ax", "middle"))
    else:
        bg = next(z for z in m["goals"] if z["id"] == b)
        margin = bg["margin"]
        ymax = margin * 1.6
        Y = lambda v: oy + PY1 - (PY1 - PY0) * min(v, ymax) / ymax  # noqa: E731
        for tv in (0, 0.25, 0.5, 0.75, 1.0):
            out.append(
                fk.el(
                    "line",
                    None,
                    x1=fk.num(X(tv)),
                    y1=oy + PY0,
                    x2=fk.num(X(tv)),
                    y2=oy + PY1,
                    class_="gl",
                )
            )
            out.append(fk.text(X(tv), oy + PY1 + 13, f"{tv * 1000:.0f}", "ax", "middle"))
        out.append(fk.text(ox + PX1, oy + PY1 + 26, "ms after the fault", "ax", "end"))
        out.append(fk.text(ox + PX0 - 4, oy + PY0 + 8, "↑ m", "ax", "end"))
        out.append(
            fk.el(
                "line",
                None,
                x1=fk.num(X(0)),
                y1=fk.num(Y(margin)),
                x2=fk.num(X(TMAX)),
                y2=fk.num(Y(margin)),
                class_="mg",
            )
        )
        out.append(fk.text(X(0) + 4, Y(margin) - 4, f"margin {margin:g} m", "mgt"))
        for bound, cls in (("high", "cw"), ("low", "cb")):
            pts = curve(bg, m, bound)
            d = "M" + " L".join(
                f"{fk.num(X(t))} {fk.num(Y(v))}" for t, v in pts if v <= ymax * 1.02
            )
            out.append(fk.el("path", None, d=d, class_=cls))
            t = ftti(m, b, bound)
            out.append(
                fk.el(
                    "line",
                    None,
                    x1=fk.num(X(t)),
                    y1=fk.num(Y(margin)),
                    x2=fk.num(X(t)),
                    y2=oy + PY1,
                    class_="ft",
                )
            )
        lo, hi = ftti(m, b, "high"), ftti(m, b, "low")
        out.append(fk.el("circle", None, cx=fk.num(X(lo)), cy=fk.num(Y(margin)), r=4, class_="fd"))
        unit = "m/s²" if bg["kind"] == "deviation" else "m/s"
        rng = m["ranges"][bg["range"]]
        fault = (
            f"fault {rng['high']:g} {unit} solid, {rng['low']:g} dashed"
            if rng["high"] != rng["low"]
            else f"at {rng['high']:g} {unit}"
        )
        if b != gid:
            fault = f"as {b} · {fault}"
        out.append(fk.text(ox + PX0 - 30, oy + PY1 + 26, fault, "ax"))
        # budget bar on the same time axis
        by = oy + PY1 + 36
        al = m["allocation"]
        xs = X(0)
        for cls, share in (
            ("det", al["detect"]),
            ("rea", al["react"]),
            ("res", 1 - al["detect"] - al["react"]),
        ):
            w = (X(lo) - X(0)) * share
            out.append(
                fk.el(
                    "rect",
                    None,
                    x=fk.num(xs),
                    y=by,
                    width=fk.num(max(w - 1, 0)),
                    height=12,
                    class_=cls,
                )
            )
            xs += w
        out.append(
            fk.text(
                X(lo) + 6,
                by + 10,
                f"FTTI {ms(lo)}" + (f" to {ms(hi)}" if abs(hi - lo) > 1e-9 else ""),
                "dmt",
            )
        )
    yy = y + 286
    for ln in fk.wrap(g["basis"], CW - 28, "s")[:4]:
        out.append(fk.text(x + 14, yy, ln, "ax"))
        yy += 14
    out.append(
        fk.text(
            x + 14,
            yy + 6,
            fk.fit("Binds " + ", ".join(mech) if mech else "Binds no mechanism", CW - 28, "s"),
            "s",
        )
    )
    return out


EXTRA = """svg { --mon:#2d55c8; --amb2:#b97800; --perf:#c2412b; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --amb2:#e7a52a; --perf:#ff7a63; } }
svg .plot { fill:var(--bg); stroke:var(--grid); stroke-width:1; }
svg .gl { stroke:var(--grid); stroke-width:1; }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .dmt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .kp { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .kpt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .mg { stroke:var(--amb2); stroke-width:1.6; stroke-dasharray:5 3; }
svg .mgt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--amb2); }
svg .cw { fill:none; stroke:var(--perf); stroke-width:2.4; }
svg .cb { fill:none; stroke:var(--perf); stroke-width:1.6; stroke-dasharray:5 3; }
svg .ft { stroke:var(--perf); stroke-width:1; stroke-dasharray:2 3; }
svg .fd { fill:var(--perf); }
svg .det { fill:var(--mon); } svg .rea { fill:var(--amb2); } svg .res { fill:var(--grid); }
"""


def sheet(m: dict, k: dict, ftti, ms, bound) -> str:
    goals = [g["id"] for g in m["goals"]]
    mech = {gid: [] for gid in goals}
    for s in m["mechanisms"]:
        mech[bound(m, s)[2]].append(s["id"])
    rows = math.ceil(len(goals) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "How long each safety goal lets a fault last", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-04 §2, Figure 2-2: how far a fault moves the vehicle over time, for the largest (solid) and "
            "smallest (dashed) fault, the margin it must not",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "reach, and the FTTI where it does, split into detect, react and reserve. Computed from proposed "
            "margins and fault ranges; nothing is measured.",
            "t",
        ),
    ]
    for i, gid in enumerate(goals):
        body += card(
            MARGIN + (i % COLS) * (CW + GAP),
            HEAD + (i // COLS) * (CH + GAP),
            gid,
            m,
            k,
            ftti,
            ms,
            mech[gid],
        )
    ly = h - 26
    lx = MARGIN
    for cls, label in (
        ("det", "time to detect"),
        ("rea", "time to react"),
        ("res", "reserve"),
    ):
        body += [
            fk.el("rect", None, x=lx, y=ly - 11, width=22, height=12, class_=cls),
            fk.text(lx + 30, ly, label, "t"),
        ]
        lx += 30 + fk.width(label, "t") + 24
    body += [
        fk.el("line", None, x1=lx, y1=ly - 5, x2=lx + 26, y2=ly - 5, class_="mg"),
        fk.text(lx + 34, ly, "margin (proposed, WP-S-02)", "t"),
    ]

    def one(gid: str) -> str:
        b = binding(m, gid, ftti)
        if b is None:
            return f"{gid} is met by a limit"
        lo, hi = ftti(m, b, "high"), ftti(m, b, "low")
        return f"{gid} FTTI {ms(lo)} to {ms(hi)}" + (f" (as {b})" if b != gid else "")

    desc = "FTTI per safety goal: " + "; ".join(one(g) for g in goals)
    return fk.svg(w, h, "WP-S-04 Figure 2-2: FTTI per safety goal", desc + ".", body, EXTRA)
