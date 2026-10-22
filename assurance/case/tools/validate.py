#!/usr/bin/env python3
"""Check the safety case records against the rules of assurance/case/README.md §3.

python3 validate.py
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caselib  # noqa: E402


def main() -> int:
    r = caselib.load()
    errs = caselib.check(r)
    for e in errs:
        print(e)
    if errs:
        return 1
    print(
        f"safety case records OK: {len(r.claims)} claims, {len(r.evidence)} evidence items, {len(r.defeaters)} defeaters"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
