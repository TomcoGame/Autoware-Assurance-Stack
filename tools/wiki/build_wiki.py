#!/usr/bin/env python3
"""Build the GitHub wiki of this repository from wiki/, and check the pages.

The pages are written and reviewed in the repository under wiki/. The GitHub wiki is a separate git
repository (<owner>/<repo>.wiki.git) with its own link rules, so this tool converts the folder:

  * a link to another page, written `Page-Name.md` or `Page-Name.md#anchor` so that it works when the
    folder is read on GitHub, becomes `Page-Name` or `Page-Name#anchor`, which is how the wiki links pages;
  * a link to a repository file or folder, written relative to wiki/ (`../assurance/README.md`), becomes
    an absolute link to that path on the published branch (`blob/` for a file, `tree/` for a folder);
    an image written `![alt](../path.svg)` becomes the `raw/` address, which the wiki can display;
  * placeholders are filled from the repository, so that no page types a value the repository holds:
      {{REPO}} {{BRANCH}} {{SYNC_COMMIT}} {{SYNC_DATE}}   where and when the pages were built
      {{GENERATED:<path>:<name>}}   the body of the block `<!-- BEGIN GENERATED: <name> (...) -->` in <path>
      {{PIN:<key>}}                 the version that repositories/autoware.repos pins for <key>
  * wiki/README.md, which describes the folder, is not published.

It refuses, with one line per problem: a page that _Sidebar.md does not link to, a page link to a page
that does not exist, a repository link to a path that does not exist, an #anchor that matches no heading
of its Markdown target, a relative link that is neither, an HTML link or image with a relative address,
and a placeholder it cannot fill. Fenced code blocks and code spans are left as they are. It also checks
the relative links of the repository's README.md, the landing page that points to the wiki.

    python3 tools/wiki/build_wiki.py --check             # check the pages, write nothing
    python3 tools/wiki/build_wiki.py --out build/wiki    # check, then write the wiki pages to build/wiki

--repo, --branch, --commit and --date say what the pages are built from; they default to this
repository, `main`, the checked-out commit and that commit's date.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from dataclasses import field
import datetime as dt
from pathlib import Path
import re
import subprocess
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WIKI = REPO_ROOT / "wiki"
DEFAULT_REPO = "TomcoGame/Autoware-Assurance-Stack"
DEFAULT_BRANCH = "main"
NOT_PUBLISHED = {"README.md"}
SPECIAL = {"_Sidebar.md", "_Footer.md"}
PINS = "repositories/autoware.repos"

FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.M | re.S)
CODE_SPAN = re.compile(r"`[^`\n]+`")
LINK = re.compile(
    r"(?P<bang>!?)\[(?P<text>(?:`[^`\n]*`|[^\]`\n])*)\]"
    r"\((?P<target>[^)\s]+)(?P<title>\s+\"[^\"]*\")?\)"
)
HTML_REF = re.compile(r"\b(?:href|src)=\"(?P<target>[^\"]*)\"")
PLACEHOLDER = re.compile(r"\{\{(?P<name>[A-Z_]+)(?::(?P<arg>[^}]*))?\}\}")
# Links (whose text may hold code spans), code spans and placeholders, in one left-to-right scan, so
# that a code span is never searched for links or placeholders.
TOKEN = re.compile(
    f"(?P<link>{LINK.pattern})|(?P<code>{CODE_SPAN.pattern})|(?P<ph>{PLACEHOLDER.pattern})"
)
HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t#]*$", re.M)
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)


@dataclass
class Context:
    repo: str = DEFAULT_REPO
    branch: str = DEFAULT_BRANCH
    commit: str = "unknown"
    date: str = ""
    root: Path = REPO_ROOT
    src: Path = WIKI


@dataclass
class Result:
    pages: dict[str, str] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)


def slug(heading: str) -> str:
    """The anchor GitHub gives a heading."""
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip()).lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(text: str) -> set[str]:
    """The anchors of the headings of a Markdown text, outside code blocks."""
    out: set[str] = set()
    for h in HEADING.findall(FENCE.sub("", text)):
        base = slug(h)
        name, n = base, 1
        while name in out:
            name, n = f"{base}-{n}", n + 1
        out.add(name)
    return out


def split_fences(text: str) -> list[tuple[bool, str]]:
    """Split text into (is_code, part), code being fenced blocks."""
    parts: list[tuple[bool, str]] = []
    pos = 0
    for m in FENCE.finditer(text):
        parts.append((False, text[pos : m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    parts.append((False, text[pos:]))
    return parts


def generated_block(root: Path, rel: str, name: str) -> str | None:
    """The body of a generated block, without its markers and surrounding blank lines."""
    path = root / rel
    if not path.is_file():
        return None
    m = re.search(
        rf"<!-- BEGIN GENERATED: {re.escape(name)} \([^)]*\) -->\n(.*?)<!-- END GENERATED: "
        rf"{re.escape(name)} -->",
        path.read_text(encoding="utf-8"),
        re.S,
    )
    return m.group(1).strip("\n") if m else None


def pinned_version(root: Path, key: str) -> str | None:
    path = root / PINS
    if not path.is_file():
        return None
    entry = (
        (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("repositories", {}).get(key)
    )
    return str(entry["version"]) if entry and "version" in entry else None


def fill(m: re.Match, page: str, ctx: Context, problems: list[str]) -> str:
    """The value of one placeholder; the placeholder itself, and a problem, when it has none."""
    name, arg = m.group("name"), m.group("arg")
    simple = {
        "REPO": ctx.repo,
        "BRANCH": ctx.branch,
        "SYNC_COMMIT": ctx.commit,
        "SYNC_DATE": ctx.date,
    }
    if name in simple and arg is None:
        return simple[name]
    if name == "GENERATED" and arg and arg.count(":") == 1:
        rel, block = arg.split(":")
        body = generated_block(ctx.root, rel, block)
        if body is not None:
            return body
        problems.append(f"{page}: no generated block '{block}' in {rel}")
    elif name == "PIN" and arg:
        version = pinned_version(ctx.root, arg)
        if version is not None:
            return version
        problems.append(f"{page}: {PINS} pins no repository '{arg}'")
    else:
        problems.append(f"{page}: unknown placeholder {m.group(0)}")
    return m.group(0)


def rewrite_target(
    target: str, image: bool, page: str, ctx: Context, sources: dict[str, str], problems: list[str]
) -> str:
    if EXTERNAL.match(target):
        return target
    path, _, anchor = target.partition("#")
    if not path:
        if anchor and anchor not in anchors(sources[page]):
            problems.append(f"{page}: no heading for #{anchor} in this page")
        return target
    if "/" not in path and path.endswith(".md"):
        if path not in sources or path in NOT_PUBLISHED:
            problems.append(f"{page}: link to page {path}, which does not exist in wiki/")
        elif anchor and anchor not in anchors(sources[path]):
            problems.append(f"{page}: no heading for #{anchor} in {path}")
        return path[: -len(".md")] + (f"#{anchor}" if anchor else "")
    resolved = (ctx.src / path).resolve()
    root = ctx.root.resolve()
    if not path.startswith("../") or (root not in resolved.parents and resolved != root):
        problems.append(
            f"{page}: link {target} is neither a page (Name.md) nor a repository path (../path)"
        )
        return target
    rel = resolved.relative_to(root).as_posix()
    if not resolved.exists():
        problems.append(f"{page}: link to {rel}, which does not exist in the repository")
        return target
    if anchor and resolved.suffix == ".md" and anchor not in anchors(resolved.read_text("utf-8")):
        problems.append(f"{page}: no heading for #{anchor} in {rel}")
    base = f"https://github.com/{ctx.repo}"
    if image:
        return f"{base}/raw/{ctx.branch}/{rel}"
    kind = "tree" if resolved.is_dir() else "blob"
    return f"{base}/{kind}/{ctx.branch}/{rel}" + (f"#{anchor}" if anchor else "")


def convert(page: str, ctx: Context, sources: dict[str, str], problems: list[str]) -> str:
    def token(m: re.Match) -> str:
        if m.group("code"):
            return m.group(0)
        if m.group("ph"):
            return fill(m, page, ctx, problems)
        target = rewrite_target(
            m.group("target"), bool(m.group("bang")), page, ctx, sources, problems
        )
        return f"{m.group('bang')}[{m.group('text')}]({target}{m.group('title') or ''})"

    out = []
    for is_code, part in split_fences(sources[page]):
        if not is_code:
            for m in HTML_REF.finditer(CODE_SPAN.sub("", part)):
                if not EXTERNAL.match(m.group("target")):
                    problems.append(f"{page}: HTML link {m.group(0)} is relative; use Markdown")
            part = TOKEN.sub(token, part)
        out.append(part)
    return "".join(out)


def sidebar_pages(sidebar: str) -> set[str]:
    """The pages _Sidebar.md links to."""
    return {
        m.group("target").partition("#")[0]
        for is_code, part in split_fences(sidebar)
        if not is_code
        for m in TOKEN.finditer(part)
        if m.group("link") and re.fullmatch(r"[^/#]+\.md(#.*)?", m.group("target"))
    }


def check_readme(ctx: Context, name: str = "README.md") -> list[str]:
    """Problems with the relative links of the repository's landing page, which links to the wiki."""
    problems: list[str] = []
    path = ctx.root / name
    for is_code, part in split_fences(path.read_text(encoding="utf-8")):
        for m in TOKEN.finditer(part) if not is_code else ():
            target = m.group("target") if m.group("link") else None
            if not target or EXTERNAL.match(target):
                continue
            rel, _, anchor = target.partition("#")
            resolved = (path.parent / rel).resolve() if rel else path
            if not resolved.exists():
                problems.append(f"{name}: link to {rel}, which does not exist in the repository")
            elif (
                anchor
                and resolved.suffix == ".md"
                and anchor not in anchors(resolved.read_text(encoding="utf-8"))
            ):
                problems.append(f"{name}: no heading for #{anchor} in {rel or name}")
    return problems


def build(ctx: Context) -> Result:
    res = Result()
    sources = {p.name: p.read_text(encoding="utf-8") for p in sorted(ctx.src.glob("*.md"))}
    for required in ("Home.md", *sorted(SPECIAL)):
        if required not in sources:
            res.problems.append(f"wiki/{required} is missing")
    if (ctx.root / "README.md").is_file():
        res.problems.extend(check_readme(ctx))
    linked = sidebar_pages(sources.get("_Sidebar.md", ""))
    for name in sources:
        if name in NOT_PUBLISHED:
            continue
        if name not in SPECIAL and name not in linked:
            res.problems.append(f"{name}: not linked from _Sidebar.md")
        res.pages[name] = convert(name, ctx, sources, res.problems)
    return res


def git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def context(args: argparse.Namespace) -> Context:
    commit = args.commit or git(REPO_ROOT, "rev-parse", "HEAD") or "unknown"
    date = args.date or git(REPO_ROOT, "show", "-s", "--format=%cs", commit)
    if not date:
        date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    return Context(
        repo=args.repo,
        branch=args.branch,
        commit=commit[:7],
        date=date,
        root=REPO_ROOT,
        src=args.src,
    )


def write(pages: dict[str, str], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.md"):
        if old.name not in pages:
            old.unlink()
    for name, text in pages.items():
        (out / name).write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="check the pages, write nothing")
    mode.add_argument("--out", type=Path, help="check, then write the wiki pages to this folder")
    ap.add_argument("--repo", default=DEFAULT_REPO, help="OWNER/NAME on GitHub")
    ap.add_argument("--branch", default=DEFAULT_BRANCH, help="branch the links point to")
    ap.add_argument("--commit", help="commit the pages are built from (default: HEAD)")
    ap.add_argument("--date", help="sync date, YYYY-MM-DD (default: the commit's date)")
    ap.add_argument("--src", type=Path, default=WIKI, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    res = build(context(args))
    for p in res.problems:
        print(p, file=sys.stderr)
    if res.problems:
        print(f"{len(res.problems)} problem(s) in wiki/; nothing written.", file=sys.stderr)
        return 1
    if args.out:
        write(res.pages, args.out)
        print(f"Wrote {len(res.pages)} wiki pages to {args.out}.")
    else:
        print(f"wiki/: {len(res.pages)} pages build without problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
