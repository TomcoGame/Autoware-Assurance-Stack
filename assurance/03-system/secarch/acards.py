"""Attack path sheet for WP-S-07: one card per interface exposed outside the vehicle.

secarch.py calls `sheet()` with the exposed interfaces already worked out and writes Figure 4-1 next to the security
architecture files. Each card shows the four trust zones in a row, where an attacker reaches the item (the zone the
interface opens into, and the attack vector), the path from there toward the safety and vehicle zones, and the
controls that stand on it: at the boundary into the safety zone, or at the interface itself when it opens into the
safety zone. Under the drawing are the threats of the TARA that use the interface, marked where a cybersecurity claim
retains them, and its controls with the highest CAL among them.

The drawing is schematic; the threats, controls and CALs are those of the model.
"""

from __future__ import annotations

import math

import figkit as fk

CW, CH = 330, 360
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
SAFE = "SZ-3"


def zones_row(ox: float, oy: float, zones: list[dict], entry: str, none: bool) -> list[str]:
    n = len(zones)
    gap = 8
    w = (CW - 28 - gap * (n - 1)) / n
    xs = {z["id"]: ox + i * (w + gap) for i, z in enumerate(zones)}
    out = []
    for z in zones:
        cls = "zs" if z["id"] == SAFE else "ze" if z["id"] == entry and not none else "zn"
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(xs[z["id"]]),
                y=oy + 36,
                width=fk.num(w),
                height=60,
                rx=5,
                class_=cls,
            )
        )
        out.append(fk.text(xs[z["id"]] + w / 2, oy + 52, z["id"], "zid", "middle"))
        for i, ln in enumerate(fk.wrap(z["name"], w - 6, "s")[:2]):
            out.append(fk.text(xs[z["id"]] + w / 2, oy + 66 + 12 * i, ln, "zt", "middle"))
    ex = xs[entry] + w / 2
    # the attacker, above the zone the interface opens into
    out.append(fk.el("circle", None, cx=fk.num(ex), cy=oy + 10, r=7, class_="atk"))
    out.append(fk.text(ex, oy + 13.5, "A", "atkt", "middle"))
    if none:
        out.append(
            fk.el(
                "line",
                None,
                x1=fk.num(ex - 9),
                y1=oy + 1,
                x2=fk.num(ex + 9),
                y2=oy + 19,
                class_="xo",
            )
        )
        out.append(
            fk.el(
                "line",
                None,
                x1=fk.num(ex + 9),
                y1=oy + 1,
                x2=fk.num(ex - 9),
                y2=oy + 19,
                class_="xo",
            )
        )
        return out
    out.append(
        fk.el("line", None, x1=fk.num(ex), y1=oy + 18, x2=fk.num(ex), y2=oy + 34, class_="ap")
    )
    out.append(
        fk.el(
            "path",
            None,
            d=f"M{fk.num(ex)} {oy + 36} L{fk.num(ex - 4)} {oy + 29} L{fk.num(ex + 4)} {oy + 29} Z",
            class_="aph",
        )
    )
    order = [z["id"] for z in zones]
    i, j = order.index(entry), order.index(SAFE)
    py = oy + 90
    if i < j:  # along the row toward the safety zone, stopped at its boundary
        x1, x2 = ex, xs[SAFE] - 2
        out.append(fk.el("line", None, x1=fk.num(x1), y1=py, x2=fk.num(x2), y2=py, class_="ap"))
        shield_x = xs[SAFE] - gap / 2
    else:  # the interface opens into the safety zone itself: the controls are at the entry
        shield_x = ex
    if i < j:
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(shield_x - 6),
                y=py - 12,
                width=12,
                height=24,
                rx=3,
                class_="sh",
            )
        )
    else:
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(shield_x - 12),
                y=oy + 21,
                width=24,
                height=10,
                rx=3,
                class_="sh",
            )
        )
    return out


def card(x: float, y: float, e: dict, zones: list[dict]) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, e["id"], "gid"))
    pw = fk.width(e["vector"], "s") + 14
    out.append(
        fk.el(
            "rect",
            None,
            x=fk.num(x + CW - 14 - pw),
            y=y + 11,
            width=fk.num(pw),
            height=18,
            rx=4,
            class_="vp",
        )
    )
    out.append(fk.text(x + CW - 14 - pw / 2, y + 24, e["vector"], "vpt", "middle"))
    if e["cal"]:
        cw = fk.width(e["cal"], "m") * 0.85 + 12
        out.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x + CW - 20 - pw - cw),
                y=y + 11,
                width=fk.num(cw),
                height=18,
                rx=4,
                class_="cal",
            )
        )
        out.append(fk.text(x + CW - 20 - pw - cw / 2, y + 24, e["cal"], "calt", "middle"))
    for i, ln in enumerate(fk.wrap(e["name"], CW - 28, "tb")[:3]):
        out.append(fk.text(x + 14, y + 44 + 16 * i, ln, "tb"))
    out += zones_row(x + 14, y + 88, zones, e["zone"], not e["threats"])
    yy = y + 208
    if e["threats"]:
        out.append(fk.text(x + 14, yy, "Threats (TARA)", "hd"))
        yy += 15
        for t in e["threats"][:5]:
            label = f"{t['id']} {t['text']}" + (" (claim)" if t["claim"] else "")
            out.append(fk.text(x + 14, yy, fk.fit(label, CW - 28, "s"), "ax"))
            yy += 13
        if len(e["threats"]) > 5:
            out.append(fk.text(x + 14, yy, f"and {len(e['threats']) - 5} more", "ax"))
            yy += 13
        yy += 6
        out.append(fk.text(x + 14, yy, f"Controls ({len(e['controls'])})", "hd"))
        yy += 15
        for ln in fk.wrap(", ".join(e["controls"]), CW - 28, "s")[:3]:
            out.append(fk.text(x + 14, yy, ln, "ax"))
            yy += 13
    else:
        out.append(fk.text(x + 14, yy, "No threat in the TARA: none is fitted", "hd"))
        out.append(fk.text(x + 14, yy + 15, f"Decision {e['decision']}", "ax"))
    return out


EXTRA = """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --perf:#c2412b; --perfsoft:#fbe5e2; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --perf:#ff7a63; --perfsoft:#3d1c1a; } }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .hd { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .vp { fill:var(--bg); stroke:var(--perf); stroke-width:1; } svg .vpt { font:600 10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--perf); }
svg .cal { fill:var(--card); stroke:var(--ink3); stroke-width:1; } svg .calt { font:700 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .zn { fill:var(--bg); stroke:var(--grid); stroke-width:1.2; }
svg .ze { fill:var(--perfsoft); stroke:var(--perf); stroke-width:1.4; }
svg .zs { fill:var(--monsoft); stroke:var(--mon); stroke-width:2; }
svg .zid { font:700 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .zt { font:10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink2); }
svg .atk { fill:var(--perf); } svg .atkt { font:700 9.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--bg); }
svg .ap { stroke:var(--perf); stroke-width:2; stroke-dasharray:5 3; } svg .aph { fill:var(--perf); }
svg .sh { fill:var(--mon); }
svg .xo { stroke:var(--ink3); stroke-width:2; }
"""


def sheet(exposed: list[dict], zones: list[dict]) -> str:
    rows = math.ceil(len(exposed) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "Where an attacker can reach the item, and what stops them", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-07 §4, Figure 4-1: each interface exposed outside the vehicle, the trust zone it opens into and "
            "its attack vector, the path toward the safety zone",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            "and where its controls stand, the TARA's threats that use it, and its controls with their highest CAL.",
            "t",
        ),
    ]
    for i, e in enumerate(exposed):
        body += card(MARGIN + (i % COLS) * (CW + GAP), HEAD + (i // COLS) * (CH + GAP), e, zones)
    ly = h - 26
    lx = MARGIN
    items = [
        ("atk", "attacker"),
        ("ze", "zone the interface opens into"),
        ("zs", "safety zone"),
        ("sh", "controls"),
    ]
    for cls, label in items:
        if cls == "atk":
            body.append(fk.el("circle", None, cx=lx + 8, cy=ly - 4, r=7, class_=cls))
        else:
            body.append(
                fk.el(
                    "rect",
                    None,
                    x=lx,
                    y=ly - 12,
                    width=16 if cls != "sh" else 10,
                    height=16,
                    rx=3,
                    class_=cls,
                )
            )
        body.append(fk.text(lx + 24, ly, label, "t"))
        lx += 24 + fk.width(label, "t") + 24
    body += [
        fk.el("line", None, x1=lx, y1=ly - 4, x2=lx + 26, y2=ly - 4, class_="ap"),
        fk.text(lx + 34, ly, "attack path", "t"),
    ]
    desc = "Exposed interfaces: " + "; ".join(
        f"{e['id']} {e['name']}, {e['vector']}, into {e['zone']}: "
        + (
            f"threats {', '.join(t['id'] for t in e['threats'])}; controls {', '.join(e['controls'])}"
            if e["threats"]
            else f"no threat, decision {e['decision']}"
        )
        for e in exposed
    )
    return fk.svg(w, h, "WP-S-07 Figure 4-1: attack paths", desc + ".", body, EXTRA)
