#!/usr/bin/env python3
"""The hardware-software interface of WP-S-05, generated from hsi.yaml.

Writes the generated tables of WP-S-05 (interfaces, the signals of each section, clocks, hardware
diagnostics, supplier requirements internal to their element) and Figure 1-1 (receive timeout and
maximum period of each timed signal). A signal's ASILs are those of the requirements it serves
(WP-S-02), on its sending and on its receiving end. Its receive timeout is the shortest detection
budget (WP-S-04 §4, worst case) of the time-critical mechanisms among the requirements on its
receiving end, and its maximum period that timeout divided by the frames each timeout must hold.

The model is refused when:
- an identifier is malformed or repeated;
- a link of WP-S-03 has no interface, or an interface matches no link or names an item interface
  that WP-C-01 does not list;
- a signal names an interface that does not exist, serves a requirement, assumption or fallback
  trigger that does not exist, or a requirement on neither end of its interface;
- a rated signal is unprotected, or a signal on an untrusted interface is not signed;
- an interface carries no signal;
- a requirement on a supplier component crosses no interface and is not listed as internal, or one
  listed as internal also crosses one;
- a clock or diagnostic names a component, or a diagnostic a requirement, that does not exist, or a
  diagnostic sits on a component outside the item.

    python3 hsi.py            # write WP-S-05's generated tables and Figure 1-1
    python3 hsi.py --check    # fail if either is stale or the model breaks a rule
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ASSURANCE = HERE.parents[1]
for sub in (
    "01-management/figures",
    "02-concept/fsc",
    "02-concept/fallback",
    "03-system/tsc",
    "03-system/timing",
    "03-system/tsr",
):
    sys.path.insert(0, str(ASSURANCE / sub))
import fallback  # noqa: E402
import figkit as fk  # noqa: E402
import fsc  # noqa: E402
import terms  # noqa: E402
import timing  # noqa: E402
import tsc  # noqa: E402
import tsr  # noqa: E402

sys.path.insert(0, str(HERE))
import icards  # noqa: E402

MODEL = HERE / "hsi.yaml"
DOC = ASSURANCE / "03-system" / "WP-S-05-hsi-specification.md"
FIG = HERE / "fig-s05-1-1-signals.svg"
FIG2 = HERE / "fig-s05-1-2-interfaces.svg"
CSV = HERE / "signals.csv"
README = HERE / "README.md"
PROTECTION = ("e2e", "signature", "none")
KEYS = {"id", "interface", "dir", "name", "content", "serves", "protection"}
# Which section of WP-S-05 an interface belongs to, by the components at its ends.
VEHICLE = {"CMP-06", "CMP-07", "CMP-08", "CMP-09"}
SENSORS = {"CMP-04", "CMP-05"}
W = 640


def load(path: Path = MODEL) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def known() -> dict:
    k = tsr.known()
    m = tsr.load()
    head, rows = fk.table(
        fk.section(fsc.ITEM.read_text(encoding="utf-8"), "### 5.2 Interfaces"), "ID"
    )
    return {
        **k,
        "tsr_model": m,
        "tsrs": {r["id"]: r for r in m["tsrs"]},
        "links": [(ln["from"], ln["to"]) for ln in k["tsc"]["links"]],
        "item_ifs": {fk.plain(r[0]) for r in rows},
        "aous": fsc.aous(),
        "triggers": {t["id"] for t in fallback.load()["triggers"]},
    }


def section_of(f: dict) -> str:
    ends = set(f["link"])
    if ends & VEHICLE:
        return "vehicle"
    if ends & SENSORS:
        return "sensors"
    return "compute"


def asils(s: dict, k: dict, comp: str) -> str:
    """The ASILs of the requirements a signal serves on one of its ends; QM where it serves none."""
    rated = {
        tsr.asil(k["tsrs"][x], k)
        for x in s["serves"]
        if x in k["tsrs"] and k["tsrs"][x]["component"] == comp
    }
    return ", ".join(sorted(rated, key=lambda a: (-tsc.rank(a.split("(")[0]), a))) or "QM"


def timeout(s: dict, k: dict, f: dict) -> tuple[float, str] | None:
    """The worst-case receive timeout of a signal in seconds, and the mechanism that sets it: the
    shortest detection budget of the time-critical mechanisms it serves on its receiving end."""
    rx = ends(s, f)[1]
    sms = {
        k["tsrs"][x]["mechanism"]
        for x in s["serves"]
        if x in k["tsrs"] and k["tsrs"][x].get("timing") and k["tsrs"][x]["component"] == rx
    }
    sms = sorted(x for x in sms if x in k["timed"])  # sorted, so a tie is broken the same way
    if not sms:
        return None
    share = k["timing"]["allocation"]["detect"]
    best = min(sms, key=lambda x: timing.bound(k["timing"], k["timed"][x])[0])
    return timing.bound(k["timing"], k["timed"][best])[0] * share, best


def check(m: dict, k: dict) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()

    def new(i: str, pat: str) -> None:
        if not re.fullmatch(pat, str(i)):
            errs.append(f"{i}: id has the wrong form")
        if i in seen:
            errs.append(f"{i}: duplicate id")
        seen.add(i)

    if not isinstance(m.get("frames_per_timeout"), int) or m["frames_per_timeout"] < 2:
        errs.append("frames_per_timeout must be a whole number of at least 2")
    ifs = {f["id"]: f for f in m.get("interfaces", [])}
    for f in m.get("interfaces", []):
        new(f["id"], r"IF-\d\d")
        if tuple(f.get("link") or ()) not in k["links"]:
            errs.append(f"{f['id']}: {f.get('link')} is not a link of WP-S-03")
        if f.get("item") not in k["item_ifs"]:
            errs.append(f"{f['id']}: item interface {f.get('item')} is not in WP-C-01 §5.2")
        if not f.get("medium"):
            errs.append(f"{f['id']}: missing medium")
    for ln in k["links"]:
        if sum(tuple(f.get("link") or ()) == ln for f in ifs.values()) != 1:
            errs.append(f"link {ln[0]}→{ln[1]} of WP-S-03 needs exactly one interface")
    crossing: set[str] = set()
    for s in m.get("signals", []):
        i = s["id"]
        new(i, r"SIG-\d\d")
        for key in set(s) - KEYS:
            errs.append(f"{i}: unknown key {key}")
        for key in ("name", "content", "serves"):
            if not s.get(key):
                errs.append(f"{i}: missing {key}")
        f = ifs.get(s.get("interface"))
        if not f:
            errs.append(f"{i}: interface {s.get('interface')} does not exist")
            continue
        if s.get("dir", "forward") not in ("forward", "back"):
            errs.append(f"{i}: dir must be forward or back")
        for x in s.get("serves") or []:
            if x in k["tsrs"]:
                crossing.add(x)
                if k["tsrs"][x]["component"] not in f["link"]:
                    errs.append(
                        f"{i}: serves {x} on {k['tsrs'][x]['component']}, which is on neither end of {f['id']}"
                    )
            elif x not in k["aous"] and x not in k["triggers"]:
                errs.append(f"{i}: serves {x}, which is not a requirement, assumption or trigger")
        p = s.get("protection")
        if p not in PROTECTION:
            errs.append(f"{i}: protection must be one of {', '.join(PROTECTION)}")
        if f.get("untrusted") and p != "signature":
            errs.append(f"{i}: crosses the untrusted {f['id']}, so it must be signed")
        if p == "none" and any(asils(s, k, c) != "QM" for c in f["link"]):
            errs.append(f"{i}: serves a rated requirement but is unprotected")
    for fid in ifs:
        if not any(s.get("interface") == fid for s in m.get("signals", [])):
            errs.append(f"{fid}: carries no signal")
    internal = {x["tsr"] for x in m.get("internal", [])}
    for x in m.get("internal", []):
        if x["tsr"] not in k["tsrs"] or not x.get("why"):
            errs.append(f"internal {x['tsr']}: not a requirement, or no reason given")
        elif x["tsr"] in crossing:
            errs.append(f"internal {x['tsr']}: also crosses an interface")
    for rid, r in k["tsrs"].items():
        el = k["components"][r["component"]]["element"]
        if not k["elements"][el]["in_item"] and rid not in crossing | internal:
            errs.append(
                f"{rid}: on a supplier component, but crosses no interface and is not internal"
            )
    for c in m.get("clocks", []):
        new(c["id"], r"CK-\d\d")
        for comp in [c.get("master")] + (c.get("clients") or []):
            if comp not in k["components"]:
                errs.append(f"{c['id']}: component {comp} does not exist")
        for x in c.get("serves") or []:
            if x not in k["tsrs"]:
                errs.append(f"{c['id']}: {x} does not exist")
    for d in m.get("diagnostics", []):
        new(d["id"], r"HD-\d\d")
        comp = k["components"].get(d.get("component"))
        if not comp:
            errs.append(f"{d['id']}: component {d.get('component')} does not exist")
        elif not k["elements"][comp["element"]]["in_item"]:
            errs.append(
                f"{d['id']}: {comp['id']} is outside the item; its diagnostics are the supplier's"
            )
        for x in d.get("serves") or []:
            if x not in k["tsrs"]:
                errs.append(f"{d['id']}: {x} does not exist")
    return errs


def tmo(m: dict, s: dict, k: dict) -> tuple[float, str] | None:
    return timeout(s, k, next(f for f in m["interfaces"] if f["id"] == s["interface"]))


def cell(s) -> str:
    return str(s).replace("|", "\\|")


def ends(s: dict, f: dict) -> tuple[str, str]:
    a, b = f["link"]
    return (a, b) if s.get("dir", "forward") == "forward" else (b, a)


def signal_rows(m: dict, k: dict, part: str) -> str:
    ifs = {f["id"]: f for f in m["interfaces"]}
    comps = k["components"]
    rows = [
        "| ID | Signal | From → to | Content | Sender ASIL | Receiver ASIL | Protection | Receive timeout "
        "| Maximum period | Serves |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in m["signals"]:
        f = ifs[s["interface"]]
        if section_of(f) != part:
            continue
        a, b = ends(s, f)
        to = tmo(m, s, k)
        n = m["frames_per_timeout"]
        rows.append(
            f"| {s['id']} | {cell(s['name'])} | {comps[a]['name']} → {comps[b]['name']} ({f['id']}) "
            f"| {cell(s['content'])} | {asils(s, k, a)} | {asils(s, k, b)} | {PROT[s['protection']]} "
            f"| {timing.ms(to[0]) + ' (' + to[1] + ')' if to else 'Event; checked when used'} "
            f"| {timing.ms(to[0] / n) if to else '—'} | {', '.join(s['serves'])} |"
        )
    return "\n".join(rows)


PROT = {"e2e": "End-to-end", "signature": "Signed (CSR-01) and aged", "none": "None"}


def tables(m: dict, k: dict) -> dict[str, str]:
    comps = k["components"]
    t = {
        "hsi-interface-cards": (
            "![Figure 1-2: one card per interface IF-01 to IF-09. Each shows the two components it joins, its "
            "item interface and medium, and every signal crossing it with its direction, protection (end to "
            "end, or signed), the ASIL of the requirements it serves at the sending and the receiving end, its "
            "receive timeout and the mechanism that sets it, and the longest period that keeps three frames in "
            "the timeout; where the interface carries a timed signal, a strip shows the tightest one with its "
            "frames in the timeout window, one of them lost. The same values are in the tables below.]"
            f"(hsi/{FIG2.name})\n\n"
            "*Figure 1-2. What crosses each interface, and how fast. Drawn by [`hsi/hsi.py`](hsi/hsi.py) from "
            "`hsi/hsi.yaml`; CI fails if it is stale. Every signal is also in "
            f"[`hsi/{CSV.name}`](hsi/{CSV.name}).*"
        )
    }
    rows = [
        "| ID | From → to | Item interface | Medium | Signals |",
        "|---|---|---|---|---|",
    ]
    for f in m["interfaces"]:
        sig = [s["id"] for s in m["signals"] if s["interface"] == f["id"]]
        trust = " **Untrusted transport.**" if f.get("untrusted") else ""
        rows.append(
            f"| {f['id']} | {f['link'][0]} {comps[f['link'][0]]['name']} → {f['link'][1]} {comps[f['link'][1]]['name']} "
            f"| {f['item']} | {cell(f['medium'])}{trust} | {', '.join(sig)} |"
        )
    t["hsi-interfaces"] = "\n".join(rows)
    for part in ("compute", "vehicle", "sensors"):
        t[f"hsi-signals-{part}"] = signal_rows(m, k, part)
    rows = ["| Requirement | Component | Why it crosses no interface |", "|---|---|---|"]
    for x in m["internal"]:
        c = k["tsrs"][x["tsr"]]["component"]
        rows.append(f"| {x['tsr']} | {c} {comps[c]['name']} | {cell(x['why'])} |")
    t["hsi-internal"] = "\n".join(rows)
    rows = [
        "| ID | Clock | Master → clients | Method | Bound | Serves |",
        "|---|---|---|---|---|---|",
    ]
    for c in m["clocks"]:
        rows.append(
            f"| {c['id']} | {cell(c['name'])} | {c['master']} → {', '.join(c['clients'])} | {cell(c['method'])} "
            f"| {cell(c['bound'])} | {', '.join(c['serves'])} |"
        )
    t["hsi-clocks"] = "\n".join(rows)
    rows = [
        "| ID | Component | Hardware feature | How the software uses it | Serves |",
        "|---|---|---|---|---|",
    ]
    for d in m["diagnostics"]:
        rows.append(
            f"| {d['id']} | {d['component']} {comps[d['component']]['name']} | {cell(d['name'])} | {cell(d['use'])} "
            f"| {', '.join(d['serves'])} |"
        )
    t["hsi-diagnostics"] = "\n".join(rows)
    timed = [s for s in m["signals"] if tmo(m, s, k)]
    tight = min(timed, key=lambda s: tmo(m, s, k)[0])
    t["hsi-summary"] = (
        f"{len(m['signals'])} signals cross the {len(m['interfaces'])} interfaces of the WP-S-03 architecture; "
        f"{len(timed)} feed a time-critical mechanism and get a receive timeout from its detection budget. The "
        f"shortest is {tight['id']} {tight['name'].lower()} at {timing.ms(tmo(m, tight, k)[0])}, so it must be sent "
        f"at least every {timing.ms(tmo(m, tight, k)[0] / m['frames_per_timeout'])}. "
        f"{sum(s['protection'] != 'none' for s in m['signals'])} signals are protected end to end or signed; "
        f"{len(m['clocks'])} clocks and {len(m['diagnostics'])} hardware diagnostics complete the interface."
    )
    return t


def fill(doc: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        begin = f"<!-- BEGIN GENERATED: {name} (assurance/03-system/hsi/hsi.py) -->"
        end = f"<!-- END GENERATED: {name} -->"
        if doc.count(begin) != 1 or doc.count(end) != 1:
            raise fk.FigureError(f"WP-S-05 needs exactly one generated block {name}")
        doc = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            lambda _: f"{begin}\n\n{body}\n\n{end}",
            doc,
            flags=re.S,
        )
    return doc


EXTRA = """svg .to { fill:var(--accsoft); stroke:var(--acc); stroke-width:1.2; }
svg .pe { stroke:var(--amb); stroke-width:2.6; fill:none; }
svg .pd { fill:var(--amb); }
"""


def figure(m: dict, k: dict) -> str:
    timed = sorted((s for s in m["signals"] if tmo(m, s, k)), key=lambda s: tmo(m, s, k)[0])
    n = m["frames_per_timeout"]
    x0, x1, y = 290, W - 100, 112
    tmax = 0.25
    X = lambda t: x0 + (x1 - x0) * t / tmax  # noqa: E731
    body = [
        fk.text(24, 32, "How often each signal must arrive", "h"),
        fk.text(24, 54, f"WP-S-05 §1: receive timeout of each timed signal (bar) and the", "t"),
        fk.text(24, 71, f"longest period that still fits {n} frames in it (marker)", "t"),
    ]
    row = 26
    top = y - 8
    for tv in (0, 0.05, 0.1, 0.15, 0.2, 0.25):
        body.append(
            fk.el(
                "path",
                None,
                d=f"M{fk.num(X(tv))} {top} L{fk.num(X(tv))} {top + row * len(timed)}",
                class_="hair",
            )
        )
        body.append(fk.text(X(tv), top - 6, f"{tv * 1000:.0f} ms", "s", "middle"))
    for s in timed:
        to, sm = tmo(m, s, k)
        body.append(fk.text(24, y + 11, fk.fit(f"{s['id']} {s['name']}", x0 - 36, "t"), "t"))
        body.append(
            fk.el(
                "rect",
                None,
                x=x0,
                y=y,
                width=fk.num(X(to) - x0),
                height=row - 12,
                rx=3,
                class_="to",
            )
        )
        px = X(to / n)
        body.append(
            fk.el("path", None, d=f"M{fk.num(px)} {y - 3} L{fk.num(px)} {y + row - 9}", class_="pe")
        )
        body.append(fk.text(X(to) + 6, y + 11, f"{timing.ms(to)} · {sm}", "s"))
        y += row
    y += 22
    body.append(fk.el("rect", None, x=24, y=y - 11, width=14, height=14, rx=3, class_="to"))
    body.append(fk.text(44, y + 1, "Receive timeout (detection budget, worst case)", "s"))
    y += 20
    body.append(fk.el("path", None, d=f"M31 {y - 12} L31 {y + 3}", class_="pe"))
    body.append(fk.text(44, y + 1, f"Longest period: timeout / {n}", "s"))
    y += 16
    desc = "Receive timeout and longest period of each timed signal: " + "; ".join(
        f"{s['id']} {s['name']}, {timing.ms(tmo(m, s, k)[0])} set by {tmo(m, s, k)[1]}, sent at least every "
        f"{timing.ms(tmo(m, s, k)[0] / n)}"
        for s in timed
    )
    return fk.svg(W, int(y + 6), "WP-S-05 Figure 1-1: signal timeouts", desc + ".", body, EXTRA)


def card_data(m: dict, k: dict) -> list[dict]:
    """Each interface with its ends and signals worked out, for the interface cards."""
    comps = k["components"]
    n = m["frames_per_timeout"]
    out = []
    for f in m["interfaces"]:
        sigs = []
        for s in m["signals"]:
            if s["interface"] != f["id"]:
                continue
            a, b = ends(s, f)
            to = tmo(m, s, k)
            sigs.append(
                {
                    "id": s["id"],
                    "name": s["name"],
                    "dir": s.get("dir", "forward"),
                    "protection": s["protection"],
                    "asil_tx": asils(s, k, a),
                    "asil_rx": asils(s, k, b),
                    "timeout": timing.ms(to[0]) if to else "",
                    "timeout_s": to[0] if to else None,
                    "by": to[1] if to else "",
                    "period": timing.ms(to[0] / n) if to else "",
                }
            )
        out.append(
            {
                "id": f["id"],
                "a": comps[f["link"][0]]["name"],
                "b": comps[f["link"][1]]["name"],
                "item": f["item"],
                "medium": f["medium"],
                "untrusted": bool(f.get("untrusted")),
                "signals": sigs,
            }
        )
    return out


def signals_csv(m: dict, k: dict) -> str:
    """Every signal with its interface, ends, protection, ASILs, timing and the requirements it serves."""
    import csv
    import io

    ifs = {f["id"]: f for f in m["interfaces"]}
    comps = k["components"]
    n = m["frames_per_timeout"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(
        [
            "ID",
            "Signal",
            "Interface",
            "Item interface (WP-C-01)",
            "From",
            "To",
            "Content",
            "Protection",
            "Sender ASIL",
            "Receiver ASIL",
            "Receive timeout (WP-S-04)",
            "Set by",
            "Maximum period",
            "Medium",
            "Serves",
        ]
    )
    for s in m["signals"]:
        f = ifs[s["interface"]]
        a, b = ends(s, f)
        to = tmo(m, s, k)
        w.writerow(
            [
                s["id"],
                s["name"],
                f["id"],
                f["item"],
                f"{a} {comps[a]['name']}",
                f"{b} {comps[b]['name']}",
                s["content"],
                PROT[s["protection"]],
                asils(s, k, a),
                asils(s, k, b),
                timing.ms(to[0]) if to else "Event; checked when used",
                to[1] if to else "—",
                timing.ms(to[0] / n) if to else "—",
                f["medium"],
                ", ".join(s["serves"]),
            ]
        )
    return buf.getvalue()


def here(md: str) -> str:
    """Text of WP-S-05 with its relative links rewritten to work from this folder."""
    md = md.replace("](hsi/", "](")
    return re.sub(r"\]\((?!https?:|#|fig-|signals\.csv|hsi\.|README)", "](../", md)


def readme(t: dict[str, str], doc: str) -> str:
    """The folder page: the whole hardware-software interface on one page."""

    def part(heading: str) -> str:
        return here(fk.section(doc, heading).strip())

    files = [
        "| File | What it holds |",
        "|---|---|",
        f"| [`{CSV.name}`]({CSV.name}) | Every signal with its interface, ends, content, protection, the ASIL at each end, its receive timeout and maximum period, its medium and the requirements it serves |",
        f"| [`{FIG.name}`]({FIG.name}) | Figure 1-1, receive timeout and longest period of each timed signal |",
        f"| [`{FIG2.name}`]({FIG2.name}) | Figure 1-2, what crosses each interface and how fast |",
        "| [`hsi.yaml`](hsi.yaml) | Interfaces, signals, clocks, hardware diagnostics and supplier-internal requirements |",
        "| [`hsi.py`](hsi.py), [`icards.py`](icards.py) | The generator: checks the model against the architecture, the technical safety requirements, the item definition and the timing budget, and writes WP-S-05's tables and everything here |",
    ]
    lines = [
        "<!-- Generated by assurance/03-system/hsi/hsi.py; do not edit by hand. -->",
        "",
        "# Hardware-software interface",
        "",
        "The whole hardware-software interface of [WP-S-05](../WP-S-05-hsi-specification.md) on one page: "
        "every interface of the [technical safety concept](../tsc/README.md)'s architecture and the signals "
        "that cross it, their protection and timing, the clocks they are stamped against, and the hardware "
        "diagnostics the monitor's software relies on. The timeouts come from the [timing budget](../timing/README.md) "
        "and the signals serve the [technical safety requirements](../tsr/README.md). Everything here is "
        "generated by `hsi.py` from `hsi.yaml`; CI fails if it is stale. Everything is a draft by Claude (I0) "
        "until it is reviewed.",
        "",
        t["hsi-summary"],
        "",
        "1. [Interfaces, protection and timing](#1-interfaces-protection-and-timing)",
        "2. [Compute and safety monitor](#2-compute-and-safety-monitor)",
        "3. [Drive-by-wire command and feedback](#3-drive-by-wire-command-and-feedback)",
        "4. [Sensors and time synchronisation](#4-sensors-and-time-synchronisation)",
        "5. [Diagnostics and status](#5-diagnostics-and-status)",
        "6. [Files in this folder](#6-files-in-this-folder)",
        "",
        "## 1. Interfaces, protection and timing",
        "",
        re.sub(
            r"<!-- BEGIN GENERATED: hsi-summary .*?END GENERATED: hsi-summary -->\n\n",
            "",
            part("## 1. Purpose"),
            flags=re.S,
        ),
        "",
        f"Every signal is also in [`{CSV.name}`]({CSV.name}), which GitHub shows as a table that can be "
        "searched.",
        "",
        "## 2. Compute and safety monitor",
        "",
        part("## 2. Compute and safety monitor interfaces"),
        "",
        "## 3. Drive-by-wire command and feedback",
        "",
        part("## 3. Drive-by-wire command and feedback signals"),
        "",
        "## 4. Sensors and time synchronisation",
        "",
        part("## 4. Sensor interfaces and time synchronisation"),
        "",
        "## 5. Diagnostics and status",
        "",
        part("## 5. Diagnostics and status signals"),
        "",
        "## 6. Files in this folder",
        "",
        *files,
        "",
    ]
    return "\n".join(lines)


def build() -> dict[Path, str]:
    m, k = load(), known()
    errs = check(m, k)
    if errs:
        raise fk.FigureError("hsi.yaml: " + "; ".join(errs))
    t = tables(m, k)
    doc = fill(DOC.read_text(encoding="utf-8"), t)
    return {
        DOC: doc,
        FIG: figure(m, k),
        FIG2: icards.sheet(card_data(m, k), m["frames_per_timeout"]),
        CSV: signals_csv(m, k),
        README: terms.close(readme(t, doc), README),
    }


if __name__ == "__main__":
    fk.run(build, __doc__)
