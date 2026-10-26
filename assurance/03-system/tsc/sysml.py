#!/usr/bin/env python3
"""The architecture of WP-S-03 as a SysML v2 textual model, generated from tsc.yaml.

Writes tsc/architecture.sysml: the components as parts, with their element and the ASIL tsc.py
derives; the links and the redundancies as connections; the safety mechanisms as actions allocated
to the component that hosts them, with dependencies on the components they use and the reactions
they start; and the functional safety requirements each mechanism satisfies. Nothing in it is typed
by hand: tsc.yaml stays the single source, and the ASILs are those tsc.py computes.

The model is refused when tsc.py refuses tsc.yaml, or when the text written does not read back to
the same architecture: a component, link, mechanism, allocation, dependency, requirement or
redundancy missing, added or changed; a name declared twice or used without being declared; braces
that do not balance. The read-back covers only the subset of SysML v2 this generator writes; the
file has not been checked by a SysML v2 tool in CI (WP-S-03 OI).

    python3 sysml.py            # write tsc/architecture.sysml
    python3 sysml.py --check    # fail if it is stale or does not read back to tsc.yaml
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tsc  # noqa: E402

fk = tsc.fk
OUT = HERE / "architecture.sysml"
IND = "    "


def q(i: str) -> str:
    """A SysML v2 unrestricted name."""
    if "'" in i or "\\" in i:
        raise fk.FigureError(f"{i!r} cannot be a SysML name")
    return f"'{i}'"


def doc(s: str) -> str:
    return "doc /* " + " ".join(str(s).replace("*/", "* /").split()) + " */"


def string(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def mech_asil(s: dict, k: dict) -> str:
    return max(
        (k["fsrs"][f]["asil"] for f in s["implements"] if f in k["fsrs"]),
        key=tsc.rank,
        default="QM",
    )


def link_name(x: dict) -> str:
    return f"{x['from']} to {x['to']}"


def expected(m: dict, k: dict) -> dict:
    """The facts of tsc.yaml the SysML text must carry, in the form read() returns."""
    return {
        "components": {c["id"]: (c["element"], tsc.label(m, k, c["id"])) for c in m["components"]},
        "links": {link_name(x): (x["from"], x["to"]) for x in m["links"]},
        "mechanisms": {s["id"]: mech_asil(s, k) for s in m["mechanisms"]},
        "allocations": {(s["id"], s["host"]) for s in m["mechanisms"]},
        "uses": {(s["id"], c) for s in m["mechanisms"] for c in s.get("uses") or []},
        "reactions": {(s["id"], r) for s in m["mechanisms"] for r in s.get("reaction") or []},
        "satisfies": {(f, s["id"]) for s in m["mechanisms"] for f in s["implements"]},
        "redundancy": {
            r["id"]: (r["between"][0], r["between"][1], ", ".join(r.get("common") or []))
            for r in m["redundancy"]
        },
    }


def write(m: dict, k: dict) -> str:
    fsrs = sorted({f for s in m["mechanisms"] for f in s["implements"]})
    reactions = sorted({r for s in m["mechanisms"] for r in s.get("reaction") or []})
    out = [
        "// Generated from assurance/03-system/tsc/tsc.yaml by assurance/03-system/tsc/sysml.py.",
        "// Do not edit: edit tsc.yaml and run the generator. A draft by Claude (I0), not reviewed.",
        "",
        f"package {q('WP-S-03 Architecture')} {{",
        IND
        + doc(
            "The system architecture of WP-S-03: components with their element (WP-C-04) and derived "
            "ASIL, the links between them, the safety mechanisms allocated to them and the functional "
            "safety requirements they satisfy, and the redundancies with their common triggering conditions."
        ),
        f"{IND}private import ScalarValues::*;",
        "",
        f"{IND}part def Component {{",
        f"{IND * 2}attribute element : String;",
        f"{IND * 2}attribute asil : String;",
        f"{IND}}}",
        f"{IND}action def SafetyMechanism {{",
        f"{IND * 2}attribute asil : String;",
        f"{IND}}}",
        f"{IND}action def Reaction;",
        f"{IND}requirement def FunctionalSafetyRequirement;",
        f"{IND}connection def Link {{",
        f"{IND * 2}end part source : Component;",
        f"{IND * 2}end part target : Component;",
        f"{IND}}}",
        f"{IND}connection def Redundancy {{",
        f"{IND * 2}end part channelA : Component;",
        f"{IND * 2}end part channelB : Component;",
        f"{IND * 2}attribute commonCause : String;",
        f"{IND}}}",
        "",
        f"{IND}// Requirements (WP-C-04) and reactions (WP-C-12) the mechanisms refer to.",
    ]
    for f in fsrs:
        out.append(
            f"{IND}requirement {q(f)} : FunctionalSafetyRequirement {{ {doc(k['fsrs'][f]['text'])} }}"
        )
    for r in reactions:
        out.append(f"{IND}action {q(r)} : Reaction;")
    out += ["", f"{IND}// Components (WP-S-03 §2)."]
    for c in m["components"]:
        out += [
            f"{IND}part {q(c['id'])} : Component {{",
            f"{IND * 2}{doc(c['name'])}",
            f"{IND * 2}:>> element = {string(c['element'])};",
            f"{IND * 2}:>> asil = {string(tsc.label(m, k, c['id']))};",
            f"{IND}}}",
        ]
    out += ["", f"{IND}// Links (WP-S-03 Figure 2-1)."]
    for x in m["links"]:
        body = f" {{ {doc(x['label'])} }}" if x.get("label") else ";"
        out.append(
            f"{IND}connection {q(link_name(x))} : Link connect {q(x['from'])} to {q(x['to'])}{body}"
        )
    out += ["", f"{IND}// Safety mechanisms (WP-S-03 §3)."]
    for s in m["mechanisms"]:
        out += [
            f"{IND}action {q(s['id'])} : SafetyMechanism {{",
            f"{IND * 2}{doc(s['name'] + ': ' + s['does'])}",
            f"{IND * 2}:>> asil = {string(mech_asil(s, k))};",
            f"{IND}}}",
            f"{IND}allocate {q(s['id'])} to {q(s['host'])};",
        ]
        if s.get("uses"):
            targets = ", ".join(q(c) for c in s["uses"])
            out.append(f"{IND}dependency {q(s['id'] + ' uses')} from {q(s['id'])} to {targets};")
        if s.get("reaction"):
            targets = ", ".join(q(r) for r in s["reaction"])
            out.append(f"{IND}dependency {q(s['id'] + ' starts')} from {q(s['id'])} to {targets};")
        for f in s["implements"]:
            out.append(f"{IND}satisfy {q(f)} by {q(s['id'])};")
    out += ["", f"{IND}// Redundancy and diversity (WP-S-03 §4)."]
    for r in m["redundancy"]:
        a, b = r["between"]
        out += [
            f"{IND}connection {q(r['id'])} : Redundancy connect {q(a)} to {q(b)} {{",
            f"{IND * 2}{doc(r['what'] + '. Diversity: ' + r['diversity'])}",
            f"{IND * 2}:>> commonCause = {string(', '.join(r.get('common') or []))};",
            f"{IND}}}",
        ]
    out.append("}")
    return "\n".join(out) + "\n"


NAME = r"'([^']+)'"


def read(text: str) -> tuple[dict, list[str]]:
    """Read back the subset of SysML v2 that write() produces: (facts, structural errors)."""
    errs: list[str] = []
    body = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    if body.count("{") != body.count("}"):
        errs.append("braces do not balance")
    got: dict = {
        "components": {},
        "links": {},
        "mechanisms": {},
        "allocations": set(),
        "uses": set(),
        "reactions": set(),
        "satisfies": set(),
        "redundancy": {},
    }
    declared: dict[str, str] = {}

    def declare(name: str, kind: str) -> None:
        if name in declared:
            errs.append(f"{name}: declared twice")
        declared[name] = kind

    for name, element, asil in re.findall(
        rf"part {NAME} : Component \{{[^}}]*?:>> element = \"([^\"]*)\";[^}}]*?:>> asil = \"([^\"]*)\";",
        body,
    ):
        declare(name, "part")
        got["components"][name] = (element, asil)
    for name in re.findall(rf"requirement {NAME} : FunctionalSafetyRequirement", body):
        declare(name, "requirement")
    for name in re.findall(rf"action {NAME} : Reaction;", body):
        declare(name, "reaction")
    for name, asil in re.findall(
        rf"action {NAME} : SafetyMechanism \{{[^}}]*?:>> asil = \"([^\"]*)\";", body
    ):
        declare(name, "mechanism")
        got["mechanisms"][name] = asil
    for name, a, b in re.findall(rf"connection {NAME} : Link connect {NAME} to {NAME}", body):
        declare(name, "link")
        got["links"][name] = (a, b)
    for name, a, b, common in re.findall(
        rf"connection {NAME} : Redundancy connect {NAME} to {NAME} \{{[^}}]*?:>> commonCause = \"([^\"]*)\";",
        body,
    ):
        declare(name, "redundancy")
        got["redundancy"][name] = (a, b, common)
    for a, b in re.findall(rf"allocate {NAME} to {NAME};", body):
        got["allocations"].add((a, b))
    for name, src, targets in re.findall(rf"dependency {NAME} from {NAME} to ([^;]+);", body):
        declare(name, "dependency")
        key = (
            "uses" if name.endswith(" uses") else "reactions" if name.endswith(" starts") else None
        )
        if key is None:
            errs.append(f"{name}: dependency of unknown kind")
            continue
        for t in re.findall(NAME, targets):
            got[key].add((src, t))
    for f, s in re.findall(rf"satisfy {NAME} by {NAME};", body):
        got["satisfies"].add((f, s))
    refs = (
        [x for pair in got["allocations"] for x in pair]
        + [x for key in ("uses", "reactions", "satisfies") for pair in got[key] for x in pair]
        + [x for v in got["links"].values() for x in v]
        + [x for v in got["redundancy"].values() for x in v[:2]]
    )
    for r in sorted(set(refs)):
        if r not in declared:
            errs.append(f"{r}: used but not declared")
    return got, errs


def check(m: dict, k: dict, text: str) -> list[str]:
    got, errs = read(text)
    want = expected(m, k)
    for key, w in want.items():
        g = got[key]
        if isinstance(w, dict):
            for i in sorted(set(w) | set(g)):
                if i not in g:
                    errs.append(f"{key} {i}: in tsc.yaml but not in the SysML model")
                elif i not in w:
                    errs.append(f"{key} {i}: in the SysML model but not in tsc.yaml")
                elif g[i] != w[i]:
                    errs.append(f"{key} {i}: SysML says {g[i]}, tsc.yaml says {w[i]}")
        else:
            for x in sorted(w - g):
                errs.append(f"{key} {x}: in tsc.yaml but not in the SysML model")
            for x in sorted(g - w):
                errs.append(f"{key} {x}: in the SysML model but not in tsc.yaml")
    return errs


def build() -> dict[Path, str]:
    m, k = tsc.load(), tsc.known()
    errs = tsc.check(m, k)
    if errs:
        raise fk.FigureError("tsc.yaml: " + "; ".join(errs))
    text = write(m, k)
    errs = check(m, k, text)
    if errs:
        raise fk.FigureError("architecture.sysml: " + "; ".join(errs))
    return {OUT: text}


if __name__ == "__main__":
    fk.run(build, __doc__)
