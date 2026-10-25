"""WP-C-04 Figure 2-1: the safety view of the item architecture.

The item boundary of WP-C-01 Figure 5-1, redrawn with the elements of the functional safety concept: each element
with its derived ASIL and the number of FSRs allocated to it, the doer (Autoware) whose commands reach the vehicle
only through the checker (the safety monitor), and the safety-relevant flows between them with the FSRs that rest on
each. What is not an element (map data, updates, passengers, other road users) stays as context.

Where each element sits and how each flow is routed is fixed here; fsc.py refuses to draw if fsc.yaml has an element
this view has no place for, or a place for an element that does not exist, or if an element is drawn on the wrong
side of the item boundary.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hara"))
import figkit as fk  # noqa: E402
import hara  # noqa: E402

W = 824
LX, CX, RX = 24, 268, 596  # left edges of the three columns
LW, CW, RW = 150, 240, 204
TOP = 100

# Element or context box: (x, y, width, height). Elements are keyed by their FSC id.
BOX = {
    "sensors": (CX, TOP, 76, 64),
    "EL-03": (CX + 88, TOP, CW - 88, 64),
    "EL-01": (CX, 214, CW, 112),
    "EL-02": (CX, 380, CW, 200),
    "maps": (LX, 214, LW, 34),
    "updates": (LX, 256, LW, 34),
    "passengers": (LX, 298, LW, 34),
    "EL-09": (LX, 450, LW, 60),
    "roadusers": (RX, TOP, RW, 60),
    "EL-06": (RX, 382, RW, 46),
    "EL-08": (RX, 436, RW, 46),
    "EL-05": (RX, 490, RW, 46),
    "EL-04": (RX, 544, RW, 76),
    "EL-07": (CX, 624, CW, 46),
}
CONTEXT = {
    "sensors": "Autoware's sensors (EL-01)",
    "maps": "HD map data",
    "updates": "Update backend",
    "passengers": "Passengers",
    "roadusers": "Other road users",
}

# Flow: (from, to, points, label, label position, kind, anchor). `safe` flows carry rated requirements; `doer` flows
# carry Autoware's QM commands and data; `ctx` flows are context. Labels name the WP-C-01 interface.
MID = CX + CW / 2
GL, GR = (LX + LW + CX) / 2, (CX + CW + RX) / 2
FLOWS = [
    ("roadusers", "EL-03", [(RX, 130), (CX + CW, 130)], "I-01", (GR, 124), "ctx", "middle"),
    ("sensors", "EL-01", [(CX + 38, 164), (CX + 38, 214)], "I-02", (CX + 46, 194), "doer", ""),
    (
        "EL-03",
        "EL-02",
        [
            (CX + CW - 30, 164),
            (CX + CW - 30, 176),
            (CX + CW + 7, 176),
            (CX + CW + 7, 360),
            (CX + CW - 30, 360),
            (CX + CW - 30, 380),
        ],
        "I-13 detections",
        (CX + CW + 18, 272),
        "safe",
        "",
    ),
    (
        "EL-01",
        "EL-02",
        [(CX + 70, 326), (CX + 70, 380)],
        "I-03 commands (QM)",
        (CX + 78, 357),
        "doer",
        "",
    ),
    ("maps", "EL-01", [(LX + LW, 231), (CX, 231)], "I-07", (GL, 225), "ctx", "middle"),
    ("updates", "EL-01", [(LX + LW, 273), (CX, 273)], "I-10", (GL, 267), "ctx", "middle"),
    ("passengers", "EL-01", [(LX + LW, 315), (CX, 315)], "I-09", (GL, 309), "ctx", "middle"),
    ("EL-09", "EL-02", [(LX + LW, 480), (CX, 480)], "I-08 signed", (GL, 474), "safe", "middle"),
    ("EL-06", "EL-02", [(RX, 405), (CX + CW, 405)], "I-05 state", (GR, 399), "safe", "middle"),
    ("EL-08", "EL-02", [(RX, 459), (CX + CW, 459)], "door state", (GR, 453), "safe", "middle"),
    ("EL-02", "EL-05", [(CX + CW, 513), (RX, 513)], "hold", (GR, 507), "safe", "middle"),
    ("EL-02", "EL-04", [(CX + CW, 562), (RX, 562)], "I-04 bounded", (GR, 556), "safe", "middle"),
    ("EL-07", "EL-02", [(MID, 624), (MID, 580)], "I-12 power", (MID + 8, 616), "safe", ""),
]
NOTES = {
    "EL-01": "Perceives, plans and drives; its commands reach the vehicle only through EL-02",
    "EL-02": "Bounds every command to the safety envelope, and can stop the vehicle alone",
    "EL-04": "Stops on its own if the monitor falls silent",
}

EXTRA = hara.EXTRA + """svg .in { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.6; }
svg .ck { fill:var(--accsoft); stroke:var(--acc); stroke-width:3; }
svg .out { fill:var(--card); stroke:var(--ink3); stroke-width:1.2; }
svg .ctx { fill:var(--bg); stroke:var(--grid); stroke-width:1.2; stroke-dasharray:4 3; }
svg .bound { fill:none; stroke:var(--acc); stroke-width:1.4; stroke-dasharray:7 5; }
svg .vp { fill:none; stroke:var(--ink3); stroke-width:1; stroke-dasharray:3 3; }
svg .bl { font:600 12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--acc); letter-spacing:.06em; }
svg .safe { stroke:var(--acc); stroke-width:2.4; fill:none; }
svg .doer { stroke:var(--ink2); stroke-width:1.4; fill:none; stroke-dasharray:6 3; }
svg .ctxw { stroke:var(--ink3); stroke-width:1; fill:none; }
svg .hs { fill:var(--acc); } svg .hd { fill:var(--ink2); } svg .hc { fill:var(--ink3); }
svg .iid { font:500 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .ctxt { font:11.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .eid { font:700 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--acc); }
svg .eido { font:700 11px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
"""


def head_at(x1: float, y1: float, x2: float, y2: float, cls: str) -> str:
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 8 * math.cos(a), y2 - 8 * math.sin(a)
    px, py = 4.5 * math.sin(a), -4.5 * math.cos(a)
    return fk.el(
        "path",
        None,
        d=f"M{fk.num(x2)} {fk.num(y2)} L{fk.num(hx + px)} {fk.num(hy + py)} L{fk.num(hx - px)} {fk.num(hy - py)} Z",
        class_=cls,
    )


def check(m: dict) -> list[str]:
    els = {e["id"] for e in m["elements"]}
    placed = {k for k in BOX if k.startswith("EL-")}
    errs = [f"{e}: no place in the safety view (safetyview.py)" for e in sorted(els - placed)]
    errs += [f"{e}: placed in the safety view but not in fsc.yaml" for e in sorted(placed - els)]
    inside = {e["id"]: e["in_item"] for e in m["elements"]}
    for e in placed & els:
        x = BOX[e][0]
        if inside[e] != (CX <= x < CX + CW and BOX[e][1] < 600):
            errs.append(f"{e}: drawn on the wrong side of the item boundary")
    return errs


def alt(m: dict, ea: dict[str, str]) -> str:
    """The figure's description for a Markdown image, from the model."""

    def one(e: dict) -> str:
        a = ea[e["id"]]
        return f"{e['name']} ({e['id']}, {a if a == 'QM' else 'ASIL ' + a})"

    inside = [one(e) for e in m["elements"] if e["in_item"]]
    outside = [one(e) for e in m["elements"] if not e["in_item"]]
    return (
        "Figure 2-1: the item boundary of WP-C-01 redrawn with the elements of the functional safety concept. "
        f"Inside the item: {', '.join(inside)}. Outside it: {', '.join(outside)}. Autoware's commands (dashed) "
        "reach the drive-by-wire only through the safety monitor; every flow a rated requirement rests on "
        "(solid) starts or ends at the monitor. Each element shows its derived ASIL and the number of FSRs "
        "allocated to it; the same data are in the elements table."
    )


def figure(m: dict, ea: dict[str, str]) -> str:
    els = {e["id"]: e for e in m["elements"]}
    n = {e: sum(1 for f in m["fsrs"] if f["element"] == e) for e in els}
    body = [
        fk.text(24, 32, "Safety view of the item architecture", "h"),
        fk.text(
            24,
            54,
            "WP-C-04 §2: the item of WP-C-01 Figure 5-1 as the functional safety concept sees it,",
            "t",
        ),
        fk.text(
            24,
            71,
            "with each element's derived ASIL and the flows the rated requirements rest on",
            "t",
        ),
        fk.el("rect", None, x=CX - 14, y=74, width=CW + 28, height=524, rx=12, class_="bound"),
        fk.text(CX - 6, 90, "ITEM", "bl"),
        fk.el("rect", None, x=RX - 8, y=356, width=RW + 16, height=272, rx=8, class_="vp"),
        fk.text(RX, 372, "Vehicle platform", "ctxt"),
    ]
    for a, b, pts, label, (lx, ly), kind, anchor in FLOWS:
        cls, hcls = {"safe": ("safe", "hs"), "doer": ("doer", "hd"), "ctx": ("ctxw", "hc")}[kind]
        d = "M" + " L".join(f"{fk.num(x)} {fk.num(y)}" for x, y in pts)
        body.append(fk.el("path", None, d=d, class_=cls))
        body.append(head_at(*pts[-2], *pts[-1], hcls))
        body.append(fk.text(lx, ly, label, "iid", anchor))
    for key, (x, y, w, h) in BOX.items():
        if key in CONTEXT:
            body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=6, class_="ctx"))
            lines = fk.wrap(CONTEXT[key], w - 12, "s")
            top = y + h / 2 - (len(lines) - 1) * 7 + 4
            for j, ln in enumerate(lines):
                body.append(fk.text(x + w / 2, top + 14 * j, ln, "ctxt", "middle"))
            continue
        e = els[key]
        inside = e["in_item"]
        cls = "ck" if key == "EL-02" else "in" if inside else "out"
        body.append(fk.el("rect", None, x=x, y=y, width=w, height=h, rx=7, class_=cls))
        asil = ea[key]
        fcls, tcls = hara.FILL[asil]
        chip = asil if asil == "QM" else f"ASIL {asil}"
        cw_ = fk.width(chip, "s") + 10
        body.append(
            fk.el(
                "rect",
                None,
                x=fk.num(x + w - cw_ - 6),
                y=y + 6,
                width=fk.num(cw_),
                height=16,
                rx=3,
                class_=fcls,
            )
        )
        body.append(
            fk.text(x + w - cw_ / 2 - 6, y + 18, chip, "tq" if asil == "QM" else tcls, "middle")
        )
        body.append(fk.text(x + 8, y + 18, key, "eid" if inside else "eido"))
        body.append(fk.text(x + 52, y + 18, f"{n[key]} FSR{'s' if n[key] != 1 else ''}", "s"))
        yy = y + 36
        for ln in fk.wrap(e["name"], w - 16, "tb")[: 1 if h < 56 else 2]:
            body.append(fk.text(x + 8, yy, ln, "tb"))
            yy += 16
        if key in NOTES:
            for ln in fk.wrap(NOTES[key], w - 16, "s")[: max(1, int((y + h - yy + 6) // 14))]:
                body.append(fk.text(x + 8, yy, ln, "s"))
                yy += 14
    y = 708
    x = 24
    for cls, label in (
        ("in", "Element in the item"),
        ("out", "Element outside the item"),
        ("ctx", "Context, not an element"),
    ):
        body += [
            fk.el("rect", None, x=x, y=y - 12, width=22, height=16, rx=4, class_=cls),
            fk.text(x + 30, y, label, "t"),
        ]
        x += 30 + fk.width(label, "t") + 22
    y += 24
    x = 24
    for cls, label in (
        ("safe", "flow a rated requirement rests on"),
        ("doer", "Autoware's commands and data (QM)"),
    ):
        body += [
            fk.el("line", None, x1=x, y1=y - 4, x2=x + 26, y2=y - 4, class_=cls),
            fk.text(x + 34, y, label, "t"),
        ]
        x += 34 + fk.width(label, "t") + 24
    y += 22
    desc = (
        "Elements: "
        + "; ".join(
            f"{e['id']} {e['name']}, {'inside' if e['in_item'] else 'outside'} the item, derived ASIL "
            f"{ea[e['id']]}, {n[e['id']]} FSRs"
            for e in m["elements"]
        )
        + ". Flows: "
        + "; ".join(
            f"{CONTEXT.get(a, a)} to {CONTEXT.get(b, b)} ({label})"
            for a, b, _, label, _, _, _ in FLOWS
        )
        + ". Autoware's commands reach the drive-by-wire only through the safety monitor."
    )
    return fk.svg(
        W, y, "WP-C-04 Figure 2-1: safety view of the item architecture", desc, body, EXTRA
    )
