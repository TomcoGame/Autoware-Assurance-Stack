#!/usr/bin/env python3
"""Check the decision register (register.yaml) against the lifecycle rules of README.md.

    python3 check_decisions.py [register.yaml]

Prints one line per broken rule and exits 1, or prints a summary and exits 0. Needs PyYAML.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
REGISTER = HERE / "register.yaml"

STATUSES = ("queued", "open", "answered", "assumed", "applied", "withdrawn")
REVERSIBILITY = ("easy", "revisit", "hard")
DECIDERS = ("lead", "claude")
VIAS = ("inbox", "chat", "assumed")
GATES = tuple(f"G{i}" for i in range(7))
ALWAYS = ("id", "question", "context", "reversibility", "blocks", "options", "status")
ONCE_ASKED = ("gate", "asked")
KNOWN = set(ALWAYS + ONCE_ASKED) | {
    "ref",
    "batch",
    "decider",
    "after",
    "proceed_after",
    "figure",
    "caption",
    "sources",
    "answer",
    "applied",
    "explanation",
    "note",
}


def load(path: Path = REGISTER) -> list[dict]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise SystemExit(f"{path}: the register must be a list of entries")
    return data


def as_date(v) -> dt.date | None:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str):
        try:
            return dt.date.fromisoformat(v[:10])
        except ValueError:
            return None
    return None


def check_entry(d: dict, base: Path) -> list[str]:
    errs: list[str] = []
    add = errs.append
    status = d.get("status")
    rev = d.get("reversibility")

    for k in ALWAYS:
        if d.get(k) in (None, "", []):
            add(f"missing {k}")
    if status != "queued":
        for k in ONCE_ASKED:
            if d.get(k) in (None, ""):
                add(f"missing {k} (needed once a question is asked)")
    for k in sorted(set(d) - KNOWN):
        add(f"unknown field {k}")
    if status not in STATUSES:
        add(f"status must be one of {', '.join(STATUSES)}")
    if rev not in REVERSIBILITY:
        add(f"reversibility must be one of {', '.join(REVERSIBILITY)}")
    if d.get("gate") is not None and d.get("gate") not in GATES:
        add("gate must be G0 … G6")
    decider = d.get("decider", "lead")
    if decider not in DECIDERS:
        add(f"decider must be one of {', '.join(DECIDERS)}")
    if decider == "claude" and rev == "hard":
        add("a hard question is never Claude's to decide")
    if "batch" in d and (
        not isinstance(d["batch"], int) or isinstance(d["batch"], bool) or d["batch"] < 1
    ):
        add("batch must be a whole number from 1")
    if status == "open" and decider == "lead" and "batch" not in d:
        add("an open question for the lead needs a batch")
    asked = as_date(d.get("asked"))
    if d.get("asked") is not None and asked is None:
        add("asked is not a date")

    opts = d.get("options") or []
    keys = [o.get("key") for o in opts if isinstance(o, dict)]
    if len(opts) < 2 or len(opts) > 4:
        add("needs two to four options")
    if len(set(keys)) != len(keys):
        add("option keys repeat")
    for o in opts:
        if not isinstance(o, dict) or not all(o.get(k) for k in ("key", "title", "detail")):
            add("every option needs key, title and detail")
    recommended = [o.get("key") for o in opts if isinstance(o, dict) and o.get("recommended")]
    if len(recommended) != 1:
        add("exactly one option must be recommended")
    elif opts and opts[0].get("key") != recommended[0]:
        add("the recommended option comes first")
    rec = recommended[0] if recommended else None

    if "proceed_after" in d:
        pa = as_date(d["proceed_after"])
        if rev != "easy":
            add("proceed_after is allowed only on easy questions")
        if pa is None:
            add("proceed_after is not a date")
        elif asked and pa < asked:
            add("proceed_after is before asked")

    fig = d.get("figure")
    if fig and not (base / fig).is_file():
        add(f"figure {fig} not found")
    if fig and not d.get("caption"):
        add("a figure needs a caption")
    if d.get("caption") and not fig:
        add("a caption without a figure")

    ans = d.get("answer")
    if status in ("answered", "assumed", "applied"):
        if not isinstance(ans, dict) or not ans.get("choice"):
            add(f"status {status} needs answer.choice")
            ans = {}
        choice, via, at = ans.get("choice"), ans.get("via"), as_date(ans.get("at"))
        if choice not in keys and choice != "other":
            add(f"answer.choice {choice} is not an option")
        if choice == "other" and not ans.get("note"):
            add("an answer of 'other' needs a note")
        if via not in VIAS:
            add(f"answer.via must be one of {', '.join(VIAS)}")
        if at is None:
            add("answer.at must be a date")
        if via == "assumed":
            if rev != "easy":
                add("only an easy question can be assumed")
            if choice != rec:
                add("an assumed answer is the recommended option")
            pa = as_date(d.get("proceed_after"))
            if pa is None:
                add("an assumed answer needs proceed_after")
            elif at and at < pa:
                add("assumed before proceed_after")
        if status == "assumed" and via != "assumed":
            add("status assumed needs answer.via: assumed")
        if status == "answered" and via == "assumed":
            add("status answered needs an answer from the lead (inbox or chat)")
        if rev == "hard" and via == "assumed":
            add("a hard question is never applied without an answer from the lead")
    elif ans:
        add(f"status {status} cannot carry an answer")

    ap = d.get("applied")
    if status == "applied":
        if not isinstance(ap, dict) or not ap.get("ref") or not ap.get("record"):
            add(
                "status applied needs applied.ref (commit or PR) and applied.record (where it is recorded)"
            )
    elif ap:
        add("only status applied carries applied")
    if status == "withdrawn" and not d.get("note"):
        add("status withdrawn needs a note saying why")
    ex = d.get("explanation")
    if ex and (not isinstance(ex, dict) or not ex.get("text") or as_date(ex.get("at")) is None):
        add("explanation needs text and at")
    return errs


def check(entries: list[dict], base: Path = HERE) -> list[str]:
    errs: list[str] = []
    ids = [str(d.get("id")) for d in entries]
    for i, d in enumerate(entries):
        did = str(d.get("id") or f"entry {i + 1}")
        if not re.fullmatch(r"DQ-\d{3}", did):
            errs.append(f"{did}: id must look like DQ-001")
        if ids.count(did) > 1 and ids.index(did) != i:
            errs.append(f"{did}: duplicate id")
        if (
            i
            and re.fullmatch(r"DQ-\d{3}", ids[i - 1])
            and re.fullmatch(r"DQ-\d{3}", did)
            and did <= ids[i - 1]
        ):
            errs.append(f"{did}: entries are in id order")
        errs += [f"{did}: {e}" for e in check_entry(d, base)]
        for a in d.get("after") or []:
            if a not in ids or a == did:
                errs.append(f"{did}: after names unknown question {a}")
    return errs


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else REGISTER
    entries = load(path)
    errs = check(entries, path.parent)
    for e in errs:
        print(e)
    if errs:
        return 1
    counts = {s: sum(d["status"] == s for d in entries) for s in STATUSES}
    print(
        f"decision register OK: {len(entries)} questions ("
        + ", ".join(f"{n} {s}" for s, n in counts.items() if n)
        + ")"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
