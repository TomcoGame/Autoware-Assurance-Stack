#!/usr/bin/env python3
"""Shared helpers for the assurance figure and page generators.

- Markdown: find a section by its heading, read a pipe table, strip links and code from a cell.
- SVG: one style block for every figure (light and dark through prefers-color-scheme), text width
  estimates for wrapping, and an element builder that escapes text.
- Output: write generated files, or with --check report every stale file and exit 1.

Standard library only. Every generator is deterministic: the same inputs give the same bytes.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape

ASSURANCE = Path(__file__).resolve().parents[2]
REPO = ASSURANCE.parent


class FigureError(Exception):
    """A source table or record a generator reads is missing or malformed."""


# ---------------------------------------------------------------- markdown


def section(md: str, heading: str) -> str:
    """The text under the first heading that starts with `heading`, up to the next heading of
    the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    lines = md.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(heading):
            out = []
            for nxt in lines[i + 1 :]:
                m = re.match(r"(#+) ", nxt)
                if m and len(m.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out)
    raise FigureError(f"no heading starting with {heading!r}")


def split_row(line: str) -> list[str]:
    """Cells of a pipe-table row. A pipe inside backticks or escaped as \\| stays in its cell."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    cells, cur, code = [], "", False
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if c == "`":
            code = not code
        if c == "|" and not code:
            cells.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    cells.append(cur.strip())
    return cells


def table(text: str, first: str) -> tuple[list[str], list[list[str]]]:
    """The first pipe table in `text` whose first header cell is `first`: (header, rows)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("|") and split_row(ln)[0] == first:
            head = split_row(ln)
            rows = []
            for r in lines[i + 2 :]:
                if not r.lstrip().startswith("|"):
                    break
                rows.append(split_row(r))
            return head, rows
    raise FigureError(f"no table with first column {first!r}")


def col(head: list[str], name: str) -> int:
    try:
        return head.index(name)
    except ValueError:
        raise FigureError(f"table has no column {name!r} (has {', '.join(head)})") from None


def plain(cell: str) -> str:
    """Cell text without links, emphasis or code marks."""
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    s = re.sub(r"[*`]", "", s)
    return " ".join(s.split())


# ---------------------------------------------------------------- svg

FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"

# Light values first, dark values second. Status colours: skeleton is a dashed outline, draft is
# amber, in review is an amber outline, approved green, baselined green with an ink ring (form, not
# only shade, tells it from approved), N/A dotted grey.
TOKENS = {
    "bg": ("#ffffff", "#16181c"),
    "ink": ("#14171c", "#eceef1"),
    "ink2": ("#4b525c", "#b9bfc8"),
    "ink3": ("#868d97", "#7f8792"),
    "grid": ("#e2e5e9", "#30343b"),
    "card": ("#f5f6f8", "#1f2227"),
    "amb": ("#b97800", "#e7a52a"),
    "ambsoft": ("#fbf0d6", "#3a2e14"),
    "ok": ("#23875a", "#45b882"),
    "acc": ("#2d55c8", "#86a2ff"),
    "accsoft": ("#e7ecfb", "#232c48"),
    "bad": ("#b3261e", "#ff8b80"),
    "badsoft": ("#fbe5e2", "#3d1c1a"),
}

STATUS_CLASS = {"S": "st-s", "D": "st-d", "R": "st-r", "A": "st-a", "B": "st-b", "N/A": "st-na"}
STATUS_NAME = {
    "S": "Skeleton",
    "D": "Draft",
    "R": "In review",
    "A": "Approved",
    "B": "Baselined",
    "N/A": "Tailored out",
}

# Approximate advance width per character, as a fraction of the font size.
CHAR = {"h": 0.56, "tb": 0.58, "t": 0.5, "s": 0.5, "m": 0.62}
SIZE = {"h": 20, "tb": 13, "t": 13, "s": 11.5, "m": 12}


def style(extra: str = "") -> str:
    light = " ".join(f"--{k}:{v[0]};" for k, v in TOKENS.items())
    dark = " ".join(f"--{k}:{v[1]};" for k, v in TOKENS.items())
    return f"""<style>
svg {{ {light} }}
@media (prefers-color-scheme: dark) {{ svg {{ {dark} }} }}
svg .bg {{ fill:var(--bg); }} svg .card {{ fill:var(--card); }} svg .hair {{ stroke:var(--grid); stroke-width:1; fill:none; }}
svg .h {{ font:600 20px {FONT}; fill:var(--ink); }}
svg .tb {{ font:600 13px {FONT}; fill:var(--ink); }}
svg .t {{ font:13px {FONT}; fill:var(--ink2); }}
svg .s {{ font:11.5px {FONT}; fill:var(--ink3); }}
svg .m {{ font:500 12px {MONO}; fill:var(--ink); }}
svg .st-s {{ fill:var(--bg); stroke:var(--ink3); stroke-width:1.3; stroke-dasharray:4 3; }}
svg .st-d {{ fill:var(--amb); }}
svg .st-r {{ fill:var(--ambsoft); stroke:var(--amb); stroke-width:1.5; }}
svg .st-a {{ fill:var(--ok); }} svg .st-b {{ fill:var(--ok); stroke:var(--ink); stroke-width:1.6; }}
svg .st-na {{ fill:var(--bg); stroke:var(--grid); stroke-width:1.2; stroke-dasharray:2 2; }}
{extra}</style>"""


def el(tag: str, content: str | None = None, **attrs) -> str:
    """An SVG element. Attribute names: trailing _ dropped, other _ become -."""
    a = "".join(
        f' {k.rstrip("_").replace("_", "-")}="{escape(str(v), {chr(34): "&quot;"})}"'
        for k, v in attrs.items()
        if v not in ("", None)
    )
    return f"<{tag}{a}/>" if content is None else f"<{tag}{a}>{escape(content)}</{tag}>"


def num(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text(x: float, y: float, s: str, cls: str = "t", anchor: str = "") -> str:
    return el("text", s, x=num(x), y=num(y), class_=cls, text_anchor=anchor)


def width(s: str, cls: str) -> float:
    return len(s) * CHAR[cls] * SIZE[cls]


def fit(s: str, w: float, cls: str) -> str:
    """`s`, cut with an ellipsis if it is wider than `w`."""
    if width(s, cls) <= w:
        return s
    n = max(1, int(w / (CHAR[cls] * SIZE[cls])) - 1)
    return s[:n].rstrip(" ,;(") + "…"


def wrap(s: str, w: float, cls: str) -> list[str]:
    """`s` broken into lines no wider than `w`."""
    lines, cur = [], ""
    for word in s.split():
        cand = f"{cur} {word}".strip()
        if cur and width(cand, cls) > w:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    return lines + [cur] if cur else lines


def svg(w: int, h: int, title: str, desc: str, body: list[str], extra_style: str = "") -> str:
    """A complete figure: accessible title and description, the shared style, a background."""
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'role="img" aria-labelledby="t d">'
    )
    return (
        "\n".join(
            [
                head,
                el("title", title, id="t"),
                el("desc", desc, id="d"),
                style(extra_style),
                f'<rect class="bg" width="{w}" height="{h}"/>',
                *body,
                "</svg>",
            ]
        )
        + "\n"
    )


# ---------------------------------------------------------------- output


def emit(outputs: dict[Path, str], argv: list[str] | None = None, doc: str = "") -> int:
    """Write `outputs`, or with --check list the stale ones and return 1."""
    ap = argparse.ArgumentParser(description=(doc or "").strip().splitlines()[0] if doc else None)
    ap.add_argument("--check", action="store_true", help="fail if a generated file is stale")
    args = ap.parse_args(argv)
    stale = []
    for path, content in outputs.items():
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old == content:
            continue
        if args.check:
            stale.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    if stale:
        for p in stale:
            print(f"stale: {p.relative_to(REPO)}")
        print("Run the generator without --check and commit the result.")
        return 1
    if args.check:
        print(f"{len(outputs)} generated file(s) current")
    return 0


def run(build, doc: str) -> None:
    """Standard entry point: build() returns {path: content}."""
    try:
        outputs = build()
    except FigureError as e:
        print(f"error: {e}")
        sys.exit(2)
    sys.exit(emit(outputs, doc=doc))
