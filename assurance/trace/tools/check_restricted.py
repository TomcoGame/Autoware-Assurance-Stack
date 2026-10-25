#!/usr/bin/env python3
"""Refuse restricted cybersecurity information in the public repository (WP-M-09 §4).

This repository is public. Attack paths, attack feasibility ratings, risk values, attack vectors,
the rationale of retained risks, vulnerability and penetration test findings, and key material
are restricted and must be kept outside it. This check scans every file git tracks (or, outside a
git checkout, the assurance tree, the wiki and CLAUDE.md) and refuses:

- a file marked restricted: a line `classification: restricted` (any case, also inside an HTML
  comment), the marking contributors put on restricted material so it cannot be committed;
- a file under a folder named `restricted`, or named `*.restricted.*`;
- key material: a private key block, or a file with a key or certificate store extension;
- a Markdown table with a restricted column: attack path, attack potential, attack feasibility,
  risk value or attack vector.

The TARA and cybersecurity generators refuse restricted keys in their models themselves.

    python3 check_restricted.py
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ASSURANCE = Path(__file__).resolve().parents[2]
REPO = ASSURANCE.parent
SELF = Path(__file__).resolve()
PLAN = ASSURANCE / "01-management" / "WP-M-09-cybersecurity-plan.md"

MARK = re.compile(r"^\W*classification\s*:\s*restricted\b", re.I | re.M)
KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
KEY_EXT = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
COLUMN = re.compile(
    r"^\|(?:.*\|)?\s*(attack path|attack potential|(attack )?feasibility|risk value|highest risk|attack vector)s?\s*\|",
    re.I | re.M,
)


def files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "-z"],
            check=True,
            capture_output=True,
        ).stdout.decode()
        return [REPO / p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        found = sorted(p for p in ASSURANCE.rglob("*") if p.is_file())
        found += sorted(p for p in (REPO / "wiki").rglob("*") if p.is_file())
        return found + [p for p in [REPO / "CLAUDE.md"] if p.is_file()]


def check(paths: list[Path]) -> list[str]:
    errs = []
    for p in paths:
        if p.resolve() in (SELF, PLAN) or not p.is_file():
            continue
        rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p
        if "restricted" in p.parts[:-1] or ".restricted." in p.name:
            errs.append(f"{rel}: restricted files are kept outside this repository")
            continue
        if p.suffix.lower() in KEY_EXT:
            errs.append(f"{rel}: key or certificate store; keep it outside this repository")
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if MARK.search(text):
            errs.append(f"{rel}: marked classification: restricted")
        if KEY.search(text):
            errs.append(f"{rel}: contains a private key")
        if p.suffix == ".md":
            for m in COLUMN.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                errs.append(f"{rel}:{line}: table column '{m.group(1)}' is restricted")
    return errs


def main() -> int:
    errs = check(files())
    for e in errs:
        print(e, file=sys.stderr)
    if errs:
        print(
            f"{len(errs)} restricted item(s) found; see WP-M-09 §4 for what may be published",
            file=sys.stderr,
        )
        return 1
    print("No restricted cybersecurity information found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
