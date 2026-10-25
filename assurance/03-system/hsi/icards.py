"""Interface sheet for WP-S-05: one card per interface, showing what crosses it and how fast.

hsi.py calls `sheet()` with the interfaces already worked out (ends, signals, protection, ASILs, timeouts) and writes
Figure 1-2 next to the HSI files. Each card shows the two components the interface joins, the item interface of
WP-C-01 it belongs to, its medium, and every signal that crosses it with its direction, protection, the ASIL of the
requirements it serves at each end, its receive timeout and the longest period that keeps `frames_per_timeout`
frames inside it. Where the interface carries a timed signal, a strip shows the tightest one: its frames inside the
timeout window, one of them lost, which is not yet a fault.

Every number comes from hsi.py, which takes it from the timing budget of WP-S-04; none is measured.
"""

from __future__ import annotations

import math

import figkit as fk

CW, CH = 330, 372
COLS, GAP, MARGIN, HEAD = 3, 16, 24, 96
PROT = {"e2e": "E2E", "signature": "SIGNED", "none": "NONE"}


def box(x: float, y: float, w: float, h: float, name: str) -> list[str]:
    out = [
        fk.el("rect", None, x=fk.num(x), y=fk.num(y), width=fk.num(w), height=h, rx=5, class_="cb")
    ]
    lines = fk.wrap(name, w - 10, "s")[:2]
    top = y + h / 2 - (len(lines) - 1) * 7 + 4
    for i, ln in enumerate(lines):
        out.append(fk.text(x + w / 2, top + 14 * i, ln, "cbt", "middle"))
    return out


def arrow(x1: float, x2: float, y: float, cls: str) -> list[str]:
    d = 1 if x2 > x1 else -1
    return [
        fk.el(
            "line",
            None,
            x1=fk.num(x1),
            y1=fk.num(y),
            x2=fk.num(x2 - 7 * d),
            y2=fk.num(y),
            class_=cls,
        ),
        fk.el(
            "path",
            None,
            d=f"M{fk.num(x2)} {fk.num(y)} L{fk.num(x2 - 8 * d)} {fk.num(y - 4.5)} L{fk.num(x2 - 8 * d)} {fk.num(y + 4.5)} Z",
            class_=cls + "h",
        ),
    ]


def strip(x: float, y: float, sig: dict, n: int) -> list[str]:
    """The timeout window of a signal with its frames, one lost."""
    w = CW - 28
    period = w / n
    out = [
        fk.el("rect", None, x=x, y=y, width=w, height=22, rx=3, class_="win"),
        fk.text(
            x,
            y - 5,
            f"{sig['id']}: {n} frames per {sig['timeout']} timeout, so one may be lost",
            "ax",
        ),
    ]
    for i in range(n):
        fx = x + period * (i + 0.5)
        cls = "frx" if i == 1 else "fr"
        out.append(
            fk.el("rect", None, x=fk.num(fx - 5), y=y + 4, width=10, height=14, rx=2, class_=cls)
        )
    out.append(fk.text(x + w, y + 36, f"sent at least every {sig['period']}", "ax", "end"))
    return out


EXTRA = """svg { --mon:#2d55c8; --monsoft:#e7ecfb; --perf:#c2412b; --amb2:#b97800; }
@media (prefers-color-scheme: dark) { svg { --mon:#86a2ff; --monsoft:#232c48; --perf:#ff7a63; --amb2:#e7a52a; } }
svg .ax { font:10.5px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink3); }
svg .gid { font:700 12px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .cb { fill:var(--monsoft); stroke:var(--mon); stroke-width:1.2; }
svg .cbt { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .fw { stroke:var(--mon); stroke-width:2; } svg .fwh { fill:var(--mon); }
svg .bk { stroke:var(--ink3); stroke-width:1.6; stroke-dasharray:4 2; } svg .bkh { fill:var(--ink3); }
svg .ip { fill:var(--card); stroke:var(--ink3); stroke-width:1; }
svg .ipt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink2); }
svg .ut { fill:var(--bg); stroke:var(--perf); stroke-width:1.2; stroke-dasharray:3 2; }
svg .utt { font:600 10px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--perf); }
svg .sid { font:700 10.5px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink); }
svg .sn { font:600 11px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif; fill:var(--ink); }
svg .pe { fill:var(--monsoft); stroke:var(--mon); stroke-width:1; } svg .pet { font:700 9px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--mon); }
svg .ps { fill:var(--bg); stroke:var(--perf); stroke-width:1; } svg .pst { font:700 9px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--perf); }
svg .pn { fill:var(--bg); stroke:var(--ink3); stroke-width:1; } svg .pnt { font:700 9px ui-monospace,'SF Mono',Menlo,Consolas,monospace; fill:var(--ink3); }
svg .win { fill:var(--bg); stroke:var(--amb2); stroke-width:1.4; stroke-dasharray:4 2; }
svg .fr { fill:var(--mon); } svg .frx { fill:none; stroke:var(--perf); stroke-width:1.4; stroke-dasharray:2 2; }
"""


def pill(x: float, y: float, text: str, cls: str) -> tuple[list[str], float]:
    w = fk.width(text, "m") * 0.8 + 12
    return (
        [
            fk.el("rect", None, x=fk.num(x - w), y=y, width=fk.num(w), height=17, rx=4, class_=cls),
            fk.text(x - w / 2, y + 12.5, text, cls + "t", "middle"),
        ],
        w,
    )


def card(x: float, y: float, f: dict, n: int) -> list[str]:
    out = [fk.el("rect", None, x=x, y=y, width=CW, height=CH, rx=8, class_="card")]
    out.append(fk.text(x + 14, y + 24, f["id"], "gid"))
    px = x + CW - 14
    p, w = pill(px, y + 11, f["item"], "ip")
    out += p
    px -= w + 6
    if f["untrusted"]:
        p, w = pill(px, y + 11, "UNTRUSTED", "ut")
        out += p
    bw = 112
    ax, bx = x + 14, x + CW - 14 - bw
    out += box(ax, y + 40, bw, 46, f["a"])
    out += box(bx, y + 40, bw, 46, f["b"])
    fwd = any(s["dir"] == "forward" for s in f["signals"])
    back = any(s["dir"] == "back" for s in f["signals"])
    if fwd:
        out += arrow(ax + bw + 4, bx - 4, y + 56 if back else y + 63, "fw")
    if back:
        out += arrow(bx - 4, ax + bw + 4, y + 72 if fwd else y + 63, "bk")
    yy = y + 104
    for ln in fk.wrap(f["medium"], CW - 28, "s")[:3]:
        out.append(fk.text(x + 14, yy, ln, "ax"))
        yy += 13
    yy += 10
    if len(f["signals"]) > 5:
        raise fk.FigureError(f"{f['id']}: a card holds 5 signals; it has {len(f['signals'])}")
    for s in f["signals"]:
        sym = "→" if s["dir"] == "forward" else "←"
        out.append(fk.text(x + 14, yy, f"{sym} {s['id']}", "sid"))
        out.append(fk.text(x + 82, yy, fk.fit(s["name"], CW - 150, "s"), "sn"))
        cls = {"e2e": "pe", "signature": "ps", "none": "pn"}[s["protection"]]
        p, _ = pill(x + CW - 14, yy - 12, PROT[s["protection"]], cls)
        out += p
        detail = f"{s['asil_tx']} → {s['asil_rx']}"
        detail += (
            f" · timeout {s['timeout']} ({s['by']}) · every {s['period']}"
            if s["timeout"]
            else " · event, checked when used"
        )
        out.append(fk.text(x + 30, yy + 14, fk.fit(detail, (CW - 44) * 11.5 / 10.5, "s"), "ax"))
        yy += 34
    timed = [s for s in f["signals"] if s["timeout"]]
    if timed:
        tight = min(timed, key=lambda s: s["timeout_s"])
        out += strip(x + 14, y + CH - 52, tight, n)
    return out


def sheet(ifs: list[dict], n: int) -> str:
    rows = math.ceil(len(ifs) / COLS)
    w = MARGIN * 2 + COLS * CW + (COLS - 1) * GAP
    h = HEAD + rows * (CH + GAP) - GAP + 56
    body = [
        fk.text(MARGIN, 34, "What crosses each interface, and how fast", "h"),
        fk.text(
            MARGIN,
            56,
            "WP-S-05 §1, Figure 1-2: each interface of the WP-S-03 architecture, its signals with their protection, "
            "the ASIL of the requirements they serve at each",
            "t",
        ),
        fk.text(
            MARGIN,
            73,
            f"end, their receive timeout from WP-S-04 and the longest period that keeps {n} frames in it. Nothing "
            "is measured or selected yet.",
            "t",
        ),
    ]
    for i, f in enumerate(ifs):
        body += card(MARGIN + (i % COLS) * (CW + GAP), HEAD + (i // COLS) * (CH + GAP), f, n)
    ly = h - 26
    lx = MARGIN
    body += arrow(lx, lx + 28, ly - 4, "fw") + [
        fk.text(lx + 36, ly, "forward, as WP-S-03 draws the link", "t")
    ]
    lx += 36 + fk.width("forward, as WP-S-03 draws the link", "t") + 24
    body += arrow(lx + 28, lx, ly - 4, "bk") + [fk.text(lx + 36, ly, "back", "t")]
    lx += 36 + fk.width("back", "t") + 24
    for cls, label in (("fr", "frame"), ("frx", "lost frame"), ("win", "receive timeout")):
        body += [
            fk.el(
                "rect",
                None,
                x=lx,
                y=ly - 12,
                width=10 if cls != "win" else 26,
                height=14,
                rx=2,
                class_=cls,
            ),
            fk.text(lx + (18 if cls != "win" else 34), ly, label, "t"),
        ]
        lx += (18 if cls != "win" else 34) + fk.width(label, "t") + 24
    desc = "Interfaces: " + "; ".join(
        f"{f['id']} {f['a']} to {f['b']} ({f['item']}): "
        + ", ".join(
            f"{s['id']} {s['name']} {PROT[s['protection']]}"
            + (f" timeout {s['timeout']}" if s["timeout"] else "")
            for s in f["signals"]
        )
        for f in ifs
    )
    return fk.svg(w, h, "WP-S-05 Figure 1-2: interfaces and their signals", desc + ".", body, EXTRA)
