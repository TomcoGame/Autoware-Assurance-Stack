#!/usr/bin/env python3
"""Unit tests of build_wiki.py, and a check of the real wiki/ folder.

python3 -m unittest discover -s tools/wiki -p 'test_*.py' -v
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_wiki as bw  # noqa: E402

BASE = "https://github.com/owner/repo"

FILES = {
    "README.md": "# Landing\n\nSee [the wiki pages](wiki/Home.md) and [docs](docs/guide.md#usage).\n",
    "docs/guide.md": "# Guide\n\n## Usage\n\nText.\n",
    "docs/figure.svg": "<svg/>",
    "summary.md": (
        "# Summary\n\n<!-- BEGIN GENERATED: counts (gen.py) -->\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        "<!-- END GENERATED: counts -->\n"
    ),
    "repositories/autoware.repos": (
        "repositories:\n  core/autoware_core:\n    type: git\n    url: https://example.org/x.git\n"
        "    version: 1.2.3\n"
    ),
    "wiki/README.md": "Describes the folder; not published.\n",
    "wiki/_Sidebar.md": "- [Home](Home.md)\n- [Other page](Other-page.md)\n- [Guide](../docs/guide.md)\n",
    "wiki/_Footer.md": "Built from {{REPO}} on {{BRANCH}} at {{SYNC_COMMIT}} ({{SYNC_DATE}}).\n",
    "wiki/Home.md": "Welcome. Read the [other page](Other-page.md#part-two).\n",
    "wiki/Other-page.md": "## Part one\n\nText.\n\n## Part two\n\nBack [home](Home.md).\n",
}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel, text in FILES.items():
            self.write(rel, text)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def ctx(self) -> bw.Context:
        return bw.Context(
            repo="owner/repo",
            branch="main",
            commit="abc1234",
            date="2026-01-02",
            root=self.root,
            src=self.root / "wiki",
        )

    def page(self, text: str) -> bw.Result:
        """Build with Home.md replaced by text."""
        self.write("wiki/Home.md", text)
        return bw.build(self.ctx())


class Links(Fixture):
    def test_fixture_builds_cleanly(self):
        res = bw.build(self.ctx())
        self.assertEqual(res.problems, [])
        self.assertNotIn("README.md", res.pages)
        self.assertEqual(
            sorted(res.pages), ["Home.md", "Other-page.md", "_Footer.md", "_Sidebar.md"]
        )

    def test_page_link_loses_md_and_keeps_anchor(self):
        res = bw.build(self.ctx())
        self.assertIn("[other page](Other-page#part-two)", res.pages["Home.md"])
        self.assertIn("[Home](Home)", res.pages["_Sidebar.md"])

    def test_repository_file_folder_and_image(self):
        res = self.page(
            "[g](../docs/guide.md#usage) [d](../docs) ![fig](../docs/figure.svg)\n"
            "[`code text`](../docs/guide.md)\n"
        )
        self.assertEqual(res.problems, [])
        text = res.pages["Home.md"]
        self.assertIn(f"[g]({BASE}/blob/main/docs/guide.md#usage)", text)
        self.assertIn(f"[d]({BASE}/tree/main/docs)", text)
        self.assertIn(f"![fig]({BASE}/raw/main/docs/figure.svg)", text)
        self.assertIn(f"[`code text`]({BASE}/blob/main/docs/guide.md)", text)

    def test_external_and_same_page_links_are_kept(self):
        res = self.page("# Top\n\n[x](https://example.org/a.md) [y](#top) [m](mailto:a@b.c)\n")
        self.assertEqual(res.problems, [])
        self.assertIn(
            "[x](https://example.org/a.md) [y](#top) [m](mailto:a@b.c)", res.pages["Home.md"]
        )

    def test_code_is_left_alone(self):
        text = "`[a](Missing.md)` and `{{NOPE}}`\n\n```sh\n[b](../nowhere.md) {{NOPE}}\n```\n"
        res = self.page(text)
        self.assertEqual(res.problems, [])
        self.assertEqual(res.pages["Home.md"], text)

    def test_broken_links_are_refused(self):
        res = self.page(
            "[a](Missing.md) [b](Other-page.md#no-such) [c](../docs/missing.md) "
            "[d](../docs/guide.md#nope) [e](docs/guide.md) [f](#nowhere) [g](README.md)\n"
        )
        problems = "\n".join(res.problems)
        for expected in (
            "page Missing.md, which does not exist",
            "#no-such in Other-page.md",
            "docs/missing.md, which does not exist",
            "#nope in docs/guide.md",
            "link docs/guide.md is neither",
            "#nowhere in this page",
            "page README.md, which does not exist",
        ):
            self.assertIn(expected, problems)
        self.assertEqual(len(res.problems), 7)

    def test_link_outside_the_repository_is_refused(self):
        res = self.page("[x](../../outside.md)\n")
        self.assertIn("is neither a page", "\n".join(res.problems))

    def test_relative_html_is_refused(self):
        res = self.page('<img src="../docs/figure.svg"> <a href="https://example.org">ok</a>\n')
        self.assertEqual(len(res.problems), 1)
        self.assertIn("HTML link", res.problems[0])


class Pages(Fixture):
    def test_page_missing_from_sidebar_is_refused(self):
        self.write("wiki/Orphan.md", "Nobody links here.\n")
        self.assertEqual(bw.build(self.ctx()).problems, ["Orphan.md: not linked from _Sidebar.md"])

    def test_required_pages(self):
        (self.root / "wiki" / "_Footer.md").unlink()
        self.assertIn("wiki/_Footer.md is missing", bw.build(self.ctx()).problems)

    def test_readme_links_are_checked(self):
        self.write("README.md", "[a](docs/missing.md) [b](docs/guide.md#nope) [c](wiki/Home.md)\n")
        problems = bw.build(self.ctx()).problems
        self.assertEqual(len(problems), 2)
        self.assertTrue(all(p.startswith("README.md:") for p in problems))


class Placeholders(Fixture):
    def test_sync_stamp(self):
        footer = bw.build(self.ctx()).pages["_Footer.md"]
        self.assertEqual(footer, "Built from owner/repo on main at abc1234 (2026-01-02).\n")

    def test_generated_block_and_pin(self):
        res = self.page("{{GENERATED:summary.md:counts}}\n\ncore {{PIN:core/autoware_core}}\n")
        self.assertEqual(res.problems, [])
        self.assertEqual(res.pages["Home.md"], "| A | B |\n|---|---|\n| 1 | 2 |\n\ncore 1.2.3\n")

    def test_unknown_placeholders_are_refused(self):
        res = self.page(
            "{{GENERATED:summary.md:nope}} {{GENERATED:missing.md:counts}} {{PIN:core/nope}} "
            "{{WHAT}} {{REPO:x}}\n"
        )
        self.assertEqual(len(res.problems), 5)
        self.assertIn("{{WHAT}}", res.pages["Home.md"])


class Helpers(unittest.TestCase):
    def test_slug_matches_github(self):
        self.assertEqual(bw.slug("3.1 Reference configuration"), "31-reference-configuration")
        self.assertEqual(bw.slug("What is `case/`?"), "what-is-case")
        self.assertEqual(
            bw.slug("2. Confirmation reviews and required independence (I1–I3)"),
            "2-confirmation-reviews-and-required-independence-i1i3",
        )

    def test_duplicate_headings_are_numbered(self):
        self.assertEqual(bw.anchors("## A\n## A\n```\n## B\n```\n"), {"a", "a-1"})


class Command(Fixture):
    def run_main(self, *args: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return bw.main([*args, "--src", str(self.root / "wiki"), "--commit", "abc1234"])

    def test_check_writes_nothing_and_out_writes_pages(self):
        out = self.root / "out"
        old = bw.REPO_ROOT
        bw.REPO_ROOT = self.root
        try:
            self.assertEqual(self.run_main("--check", "--date", "2026-01-02"), 0)
            self.assertFalse(out.exists())
            (out).mkdir()
            (out / "Stale.md").write_text("old", encoding="utf-8")
            self.assertEqual(self.run_main("--out", str(out), "--date", "2026-01-02"), 0)
            self.assertEqual(
                sorted(p.name for p in out.iterdir()),
                ["Home.md", "Other-page.md", "_Footer.md", "_Sidebar.md"],
            )
            self.write("wiki/Home.md", "[a](Missing.md)\n")
            self.assertEqual(self.run_main("--check"), 1)
        finally:
            bw.REPO_ROOT = old


class RealWiki(unittest.TestCase):
    def test_wiki_folder_builds_without_problems(self):
        ctx = bw.Context(commit="0000000", date="2026-01-01")
        res = bw.build(ctx)
        self.assertEqual(res.problems, [])
        self.assertIn("Home.md", res.pages)
        self.assertIn("at commit 0000000 (2026-01-01)", res.pages["_Footer.md"])


if __name__ == "__main__":
    unittest.main()
