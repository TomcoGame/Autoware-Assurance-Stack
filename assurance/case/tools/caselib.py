#!/usr/bin/env python3
"""Load and check the safety case records in assurance/case/records/.

Three lists, one file each: claims.yaml (CL-nnn), evidence.yaml (EV-nnn), defeaters.yaml (DF-nnn).
The rules are those of assurance/case/README.md §3; check() returns one message per broken rule.
Needs PyYAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
RECORDS = CASE / "records"
sys.path.insert(0, str(CASE.parent / "01-management" / "figures"))
import wpregister  # noqa: E402

CLAIM_STATUS = ("proposed", "supported", "accepted", "withdrawn")
EVIDENCE_STATUS = ("missing", "drafted", "available", "accepted")
DEFEATER_STATUS = ("open", "closed")


@dataclass
class Records:
    claims: list[dict]
    evidence: list[dict]
    defeaters: list[dict]


def load(base: Path = RECORDS) -> Records:
    import yaml

    def one(name: str) -> list[dict]:
        data = yaml.safe_load((base / f"{name}.yaml").read_text(encoding="utf-8")) or []
        if not isinstance(data, list):
            raise SystemExit(f"{name}.yaml must be a list")
        return data

    return Records(one("claims"), one("evidence"), one("defeaters"))


def check(r: Records, wp_ids: set[str] | None = None) -> list[str]:
    if wp_ids is None:
        wp_ids = {p.wid for p in wpregister.load().products}
    errs: list[str] = []

    def ids(items: list[dict], prefix: str, kind: str) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i, it in enumerate(items):
            iid = str(it.get("id", f"{kind} {i + 1}"))
            if not re.fullmatch(rf"{prefix}-\d{{3}}", iid):
                errs.append(f"{iid}: id must look like {prefix}-001")
            if iid in out:
                errs.append(f"{iid}: duplicate id")
            out[iid] = it
        return out

    cl, ev, df = (
        ids(r.claims, "CL", "claim"),
        ids(r.evidence, "EV", "evidence"),
        ids(r.defeaters, "DF", "defeater"),
    )
    for cid, c in cl.items():
        for k in ("statement", "status"):
            if not c.get(k):
                errs.append(f"{cid}: missing {k}")
        if c.get("status") not in CLAIM_STATUS:
            errs.append(f"{cid}: status must be one of {', '.join(CLAIM_STATUS)}")
        parent = c.get("parent")
        if parent is not None and parent not in cl:
            errs.append(f"{cid}: parent {parent} is not a claim")
        for e in c.get("evidence") or []:
            if e not in ev:
                errs.append(f"{cid}: evidence {e} is not recorded")
        if c.get("status") == "accepted":
            if not c.get("review"):
                errs.append(f"{cid}: an accepted claim names the review that accepted it")
            for e in c.get("evidence") or []:
                if e in ev and ev[e].get("status") != "accepted":
                    errs.append(f"{cid}: accepted, but its evidence {e} is {ev[e].get('status')}")
            if not c.get("evidence") and not any(x.get("parent") == cid for x in cl.values()):
                errs.append(f"{cid}: accepted with neither evidence nor sub-claims")
            for d in df.values():
                if d.get("against") == cid and d.get("status") == "open":
                    errs.append(f"{cid}: accepted while defeater {d.get('id')} is open")
    # A cycle in the claim tree would make the argument circular.
    for cid in cl:
        seen, cur = set(), cid
        while cur is not None and cur in cl:
            if cur in seen:
                errs.append(f"{cid}: the parent chain loops")
                break
            seen.add(cur)
            cur = cl[cur].get("parent")
    for eid, e in ev.items():
        for k in ("title", "status", "work_product"):
            if not e.get(k):
                errs.append(f"{eid}: missing {k}")
        if e.get("status") not in EVIDENCE_STATUS:
            errs.append(f"{eid}: status must be one of {', '.join(EVIDENCE_STATUS)}")
        if e.get("work_product") and e["work_product"] not in wp_ids:
            errs.append(f"{eid}: work product {e['work_product']} is not in WP-M-00")
        if e.get("status") == "accepted" and not e.get("review"):
            errs.append(f"{eid}: accepted evidence names the review that accepted it")
    for did, d in df.items():
        for k in ("statement", "against", "status"):
            if not d.get(k):
                errs.append(f"{did}: missing {k}")
        if d.get("status") not in DEFEATER_STATUS:
            errs.append(f"{did}: status must be one of {', '.join(DEFEATER_STATUS)}")
        if d.get("against") and d["against"] not in cl and d["against"] not in ev:
            errs.append(f"{did}: against {d['against']} is neither a claim nor evidence")
        if d.get("status") == "closed" and not d.get("closed_by"):
            errs.append(f"{did}: a closed defeater says what closed it (closed_by)")
    return errs
