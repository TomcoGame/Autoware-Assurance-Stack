#!/usr/bin/env python3
"""The facts the README figures show, read from the work products and the decision register.

No label on a figure is typed: each value below is looked up in the record that owns it, and a
lookup that fails stops the build with the record and the item it could not find. The figures are
concept illustrations, so these are the drafted values (I0) of the current work products.

Sources: the FSC element and requirement tables of WP-C-04, the safety goals of WP-C-03, the ODD
attributes of WP-C-02, the standards table of WP-M-01 §4 and the answers in the decision register.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

import yaml

REPO = Path(__file__).resolve().parents[2]
ASSURANCE = REPO / "assurance"
sys.path.insert(0, str(ASSURANCE / "01-management" / "figures"))
import figkit as fk  # noqa: E402

WP_C02 = ASSURANCE / "02-concept" / "WP-C-02-odd-and-intended-functionality.md"
WP_C03 = ASSURANCE / "02-concept" / "WP-C-03-hara.md"
WP_C04 = ASSURANCE / "02-concept" / "WP-C-04-functional-safety-concept.md"
WP_M01 = ASSURANCE / "01-management" / "WP-M-01-assurance-strategy.md"
REGISTER = ASSURANCE / "01-management" / "decisions" / "register.yaml"
WP_M00 = ASSURANCE / "01-management" / "WP-M-00-work-product-register.md"
ASSURANCE_README = ASSURANCE / "README.md"


class FactError(Exception):
    """A record does not hold a fact a figure needs."""


@dataclass(frozen=True)
class Element:
    eid: str
    name: str
    in_item: bool
    asil: str  # QM, A, B, C or D
    assumption: str  # "" or AOU-nn


@dataclass(frozen=True)
class Limit:
    oid: str
    short: str  # e.g. "≤ 30 mph"
    proposed: bool

    @property
    def tag(self) -> str:
        return f"{self.short} (proposed)" if self.proposed else self.short


@dataclass(frozen=True)
class OddRow:
    oid: str
    attribute: str
    inside: str
    outside: str
    detected_by: str
    state: str


@dataclass(frozen=True)
class Facts:
    elements: dict[str, Element]
    goals: dict[str, tuple[str, str, str]]  # SG id -> (statement, ASIL, safe state)
    requirements: dict[str, str]  # FSR id -> ASIL
    limits: dict[str, Limit]
    decisions: dict[str, str]  # DQ id -> chosen option, applied decisions only
    standards: list[str]  # WP-M-01 §4, in order
    odd: dict[str, OddRow]  # every ODD attribute of WP-C-02 §3
    monitors: dict[str, str]  # MON id -> its name, the text before the first colon (WP-C-02 §4)
    decision_titles: dict[str, str]  # DQ id -> title of the chosen option, applied decisions only

    def dq(self, qid: str) -> str:
        """'DQ-002 A' for an applied decision."""
        if qid not in self.decisions:
            raise FactError(f"{REGISTER.name}: {qid} is not an applied decision")
        return f"{qid} {self.decisions[qid]}"


def _rows(path: Path, first: str, start: str = "") -> tuple[list[str], list[list[str]]]:
    text = path.read_text(encoding="utf-8")
    if start:
        text = fk.section(text, start)
    try:
        return fk.table(text, first)
    except fk.FigureError as exc:
        raise FactError(f"{path.name}: {exc}") from None


def _asil(cell: str, where: str) -> str:
    v = fk.plain(cell).replace("ASIL", "").strip()
    if v not in ("QM", "A", "B", "C", "D"):
        raise FactError(f"{where}: {cell!r} is not an ASIL")
    return v


def elements() -> dict[str, Element]:
    head, rows = _rows(WP_C04, "ID", "## 4.")
    ci, cn, cin, ca, cas = (
        fk.col(head, c) for c in ("ID", "Element", "In the item", "Derived ASIL", "Assumption")
    )
    out = {}
    for r in rows:
        eid = fk.plain(r[ci])
        if eid.startswith("EL-"):
            aou = fk.plain(r[cas])
            out[eid] = Element(
                eid,
                fk.plain(r[cn]),
                fk.plain(r[cin]) == "Yes",
                _asil(r[ca], f"WP-C-04 {eid}"),
                "" if aou in ("—", "-") else aou,
            )
    return out


def goals() -> dict[str, tuple[str, str, str]]:
    head, rows = _rows(WP_C03, "ID", "## 7.")
    ci, cs, ca, css = (fk.col(head, c) for c in ("ID", "Safety goal", "ASIL", "Safe state"))
    return {
        fk.plain(r[ci]): (
            fk.plain(r[cs]),
            _asil(r[ca], f"WP-C-03 {fk.plain(r[ci])}"),
            fk.plain(r[css]),
        )
        for r in rows
        if fk.plain(r[ci]).startswith("SG-")
    }


def requirements() -> dict[str, str]:
    """FSR id -> ASIL, from the requirement tables of WP-C-04 §5 (one table per safety goal)."""
    head, _ = _rows(WP_C04, "ID", "## 5.")
    ci, ca = fk.col(head, "ID"), fk.col(head, "ASIL")
    out = {}
    for line in fk.section(WP_C04.read_text(encoding="utf-8"), "## 5.").splitlines():
        if line.startswith("| FSR-"):
            cells = fk.split_row(line)
            out[fk.plain(cells[ci])] = _asil(cells[ca], f"WP-C-04 {fk.plain(cells[ci])}")
    if not out:
        raise FactError(f"{WP_C04.name}: no functional safety requirements in §5")
    return out


LIMIT_PATTERNS = {  # ODD attribute -> (pattern on "Inside the ODD", short form)
    "ODD-03": (r"at or below (\d+) mph", "roads ≤ {} mph"),
    "ODD-10": (r"up to ([\d.]+) mm/h", "rain ≤ {} mm/h"),
    "ODD-11": (r"of (\d+) m or more", "visibility ≥ {} m"),
}


def limits() -> dict[str, Limit]:
    text = WP_C02.read_text(encoding="utf-8")
    out = {}
    for line in text.splitlines():
        if not line.startswith("| ODD-"):
            continue
        cells = fk.split_row(line)
        oid = fk.plain(cells[0])
        if oid in LIMIT_PATTERNS:
            pattern, short = LIMIT_PATTERNS[oid]
            m = re.search(pattern, fk.plain(cells[2]))
            if not m:
                raise FactError(
                    f"{WP_C02.name}: {oid} 'Inside the ODD' no longer matches {pattern!r}"
                )
            out[oid] = Limit(
                oid, short.format(m.group(1)), fk.plain(cells[-1]).startswith("Proposed")
            )
    missing = set(LIMIT_PATTERNS) - set(out)
    if missing:
        raise FactError(f"{WP_C02.name}: no row for {', '.join(sorted(missing))}")
    return out


def odd_rows() -> dict[str, OddRow]:
    out = {}
    for line in WP_C02.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ODD-"):
            c = [fk.plain(x) for x in fk.split_row(line)]
            if len(c) < 6:
                raise FactError(f"{WP_C02.name}: {c[0]} has {len(c)} cells, expected 6")
            out[c[0]] = OddRow(*c[:6])
    if not out:
        raise FactError(f"{WP_C02.name}: no ODD attributes")
    return out


def monitors() -> dict[str, str]:
    out = {}
    for line in WP_C02.read_text(encoding="utf-8").splitlines():
        if line.startswith("| MON-"):
            c = fk.split_row(line)
            out[fk.plain(c[0])] = fk.plain(c[1]).split(":")[0]
    return out


def decision_titles() -> dict[str, str]:
    entries = yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or []
    out = {}
    for d in entries:
        choice = (d.get("answer") or {}).get("choice")
        if d.get("status") == "applied" and choice:
            for o in d.get("options", []):
                if o.get("key") == choice:
                    out[d["id"]] = str(o.get("title", ""))
    return out


@dataclass(frozen=True)
class Gate:
    gid: str
    name: str
    criterion: str
    needed: int  # work products the gate needs (not tailored out)
    done: int  # of those, approved or baselined
    drafted: int  # of those, drafted or in review


def gates() -> list[Gate]:
    """The gates of WP-M-00 §2 with the work products each needs, from the §3 register."""
    import wpregister  # noqa: PLC0415  (beside figkit, on the path set above)

    head, rows = _rows(WP_M00, "Gate", "## 2.")
    crit = {fk.plain(r[0]): fk.plain(r[fk.col(head, "Exit criterion (summary)")]) for r in rows}
    reg = wpregister.load()
    out = []
    for gi, (gid, name) in enumerate(reg.gates):
        need = [p for p in reg.products if gi in p.gates and p.status != "N/A"]
        out.append(
            Gate(
                gid,
                name,
                crit.get(gid, ""),
                len(need),
                sum(p.status in ("A", "B") for p in need),
                sum(p.status in ("D", "R") for p in need),
            )
        )
    if not out:
        raise FactError(f"{WP_M00.name}: no gates")
    return out


def assurance_state() -> str:
    """The 'Assurance state' row of the generated summary in assurance/README.md."""
    m = re.search(
        r"^\| Assurance state \| (.+?) \|$", ASSURANCE_README.read_text(encoding="utf-8"), re.M
    )
    if not m:
        raise FactError(
            f"{ASSURANCE_README.name}: no 'Assurance state' row in the generated summary"
        )
    return m.group(1).strip()


@dataclass(frozen=True)
class Timing:
    goal: str
    kind: str  # deviation, drift, derived or limit
    margin: float | None  # metres, proposed
    ftti_short: float | None  # seconds, worst case (largest fault)
    ftti_long: float | None  # seconds, smallest fault
    detect: float  # share of the FTTI for detection
    react: float  # share for the reaction
    basis: str


def timing() -> dict[str, Timing]:
    """The FTTI of each safety goal, computed by WP-S-04's own timing.py from its timing.yaml."""
    sys.path.insert(0, str(ASSURANCE / "03-system" / "timing"))
    import timing as tm  # noqa: PLC0415

    m = tm.load()
    alloc = m["allocation"]
    out = {}
    for g in m["goals"]:
        out[g["id"]] = Timing(
            g["id"],
            g["kind"],
            g.get("margin"),
            tm.ftti(m, g["id"], "high"),
            tm.ftti(m, g["id"], "low"),
            alloc["detect"],
            alloc["react"],
            str(g.get("basis", "")),
        )
    return out


def folders() -> dict[str, str]:
    """Folder -> its content, from the Layout table of assurance/README.md."""
    head, rows = _rows(ASSURANCE_README, "Folder", "## Layout")
    return {fk.plain(r[0]).strip("/"): fk.plain(r[fk.col(head, "Content")]) for r in rows}


def decisions() -> dict[str, str]:
    entries = yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or []
    return {
        d["id"]: str(d["answer"]["choice"])
        for d in entries
        if d.get("status") == "applied" and d.get("answer", {}).get("choice")
    }


def standards() -> list[str]:
    head, rows = _rows(WP_M01, "Standard", "## 4.")
    return [fk.plain(r[fk.col(head, "Standard")]) for r in rows]


def load() -> Facts:
    return Facts(
        elements(),
        goals(),
        requirements(),
        limits(),
        decisions(),
        standards(),
        odd_rows(),
        monitors(),
        decision_titles(),
    )


def need(facts: Facts) -> dict[str, str]:
    """Every value the figures use, by name, so a missing one fails before anything is drawn."""
    el, sg, fsr = facts.elements, facts.goals, facts.requirements
    for k in ("EL-01", "EL-02", "EL-03", "EL-04", "EL-09"):
        if k not in el:
            raise FactError(f"{WP_C04.name}: no element {k}")
    for k in ("SG-01", "SG-02", "SG-06", "SG-07", "SG-08"):
        if k not in sg:
            raise FactError(f"{WP_C03.name}: no safety goal {k}")
    for k in ("FSR-06.01", "FSR-06.02"):
        if k not in fsr:
            raise FactError(f"{WP_C04.name}: no requirement {k}")
    return {
        "autoware": el["EL-01"].asil,
        "monitor": el["EL-02"].asil,
        "channel": el["EL-03"].asil,
        "dbw": el["EL-04"].asil,
        "dbw_aou": el["EL-04"].assumption,
        "remote": el["EL-09"].asil,
        "sg02": sg["SG-02"][1],
        "sg06": sg["SG-06"][1],
        "sg07": sg["SG-07"][1],
        "sg07_safe_state": sg["SG-07"][2],
        "fsr0601": fsr["FSR-06.01"],
        "fsr0602": fsr["FSR-06.02"],
        "dq_qm": facts.dq("DQ-002"),
        "dq_mrc": facts.dq("DQ-016"),
        "dq_sg06": facts.dq("DQ-017"),
        "dq_sensors": facts.dq("DQ-018"),
        "dq_remote": facts.dq("DQ-010"),
        "dq_remote_title": facts.decision_titles.get("DQ-010", ""),
        "sg01": sg["SG-01"][1],
        "sg01_text": sg["SG-01"][0],
        "sg08": sg["SG-08"][1],
        "sg08_text": sg["SG-08"][0],
        "sg08_safe_state": sg["SG-08"][2],
    }


if __name__ == "__main__":
    f = load()
    for k, v in need(f).items():
        print(f"{k:12} {v}")
    for lim in f.limits.values():
        print(f"{lim.oid:12} {lim.tag}")
    print("standards   ", ", ".join(f.standards))
