#!/usr/bin/env python3
"""Unit tests of the assurance tools: the parsers, the checkers and the generators.

python3 -m unittest discover -s assurance/tests -p 'test_*.py' -v
"""

from __future__ import annotations

import copy
from pathlib import Path
import re
import sys
import tempfile
import unittest

ASSURANCE = Path(__file__).resolve().parents[1]
for sub in (
    "01-management/figures",
    "01-management/decisions",
    "02-concept/figures",
    "02-concept/hara",
    "02-concept/fsc",
    "02-concept/sotif",
    "02-concept/fallback",
    "case/tools",
    "trace/tools",
):
    sys.path.insert(0, str(ASSURANCE / sub))

import build_inbox  # noqa: E402
import caselib  # noqa: E402
import check_decisions  # noqa: E402
import check_headers  # noqa: E402
import check_links  # noqa: E402
import check_tables  # noqa: E402
import dashboard  # noqa: E402
import fallback  # noqa: E402
import fig_c01_boundary  # noqa: E402
import fig_lifecycle  # noqa: E402
import fig_m00_register  # noqa: E402
import fig_questions  # noqa: E402
import figkit  # noqa: E402
import folder_index  # noqa: E402
import fsc  # noqa: E402
import hara  # noqa: E402
import sotif  # noqa: E402
import wpregister  # noqa: E402

GOOD = {
    "id": "DQ-001",
    "question": "Which?",
    "context": "Because.",
    "reversibility": "easy",
    "blocks": "Nothing",
    "gate": "G0",
    "asked": "2026-10-22",
    "batch": 1,
    "options": [
        {"key": "A", "title": "One", "detail": "Does one.", "recommended": True},
        {"key": "B", "title": "Two", "detail": "Does two."},
    ],
    "status": "open",
}


def errs(**changes) -> list[str]:
    d = copy.deepcopy(GOOD)
    for k, v in changes.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return check_decisions.check([d], ASSURANCE / "01-management" / "decisions")


class Markdown(unittest.TestCase):
    def test_split_row_keeps_code_and_escaped_pipes(self):
        self.assertEqual(figkit.split_row("| a | `x|y` | b\\|c |"), ["a", "`x|y`", "b|c"])

    def test_table_and_section(self):
        md = "# T\n\n## 2. Gates\n\n| Gate | Name |\n|---|---|\n| G0 | Gov |\n\n## 3. Next\n"
        head, rows = figkit.table(figkit.section(md, "## 2. Gates"), "Gate")
        self.assertEqual((head, rows), (["Gate", "Name"], [["G0", "Gov"]]))
        with self.assertRaises(figkit.FigureError):
            figkit.section(md, "## 9.")

    def test_plain(self):
        self.assertEqual(figkit.plain("[WP-C-03](x.md) `code` **b**"), "WP-C-03 code b")


class Register(unittest.TestCase):
    def test_gate_cells(self):
        self.assertEqual(wpregister.parse_gates("G1→G5 (living)", 7), [1, 2, 3, 4, 5])
        self.assertEqual(wpregister.parse_gates("G2 (definition), G6 (monitoring)", 7), [2, 6])
        with self.assertRaises(figkit.FigureError):
            wpregister.parse_gates("later", 7)

    def test_real_register_loads(self):
        reg = wpregister.load()
        self.assertEqual([g for g, _ in reg.gates], [f"G{i}" for i in range(7)])
        ids = [p.wid for p in reg.products]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("WP-C-12", ids)

    def test_row_with_wrong_cell_count_is_refused(self):
        md = wpregister.WP_M_00.read_text(encoding="utf-8").replace(
            "| G1 | S |", "| G1 | S | extra |", 1
        )
        with self.assertRaises(figkit.FigureError):
            wpregister.load(md)


class Decisions(unittest.TestCase):
    def test_good_entry_passes(self):
        self.assertEqual(errs(), [])

    def test_real_register_passes(self):
        self.assertEqual(check_decisions.check(check_decisions.load()), [])

    def test_recommended_option_comes_first(self):
        opts = copy.deepcopy(GOOD["options"])[::-1]
        self.assertTrue(any("comes first" in e for e in errs(options=opts)))

    def test_exactly_one_recommendation(self):
        opts = copy.deepcopy(GOOD["options"])
        opts[1]["recommended"] = True
        self.assertTrue(any("exactly one" in e for e in errs(options=opts)))

    def test_hard_question_is_never_assumed(self):
        e = errs(
            reversibility="hard",
            status="assumed",
            proceed_after="2026-10-22",
            answer={"choice": "A", "via": "assumed", "at": "2026-10-23"},
        )
        self.assertTrue(any("proceed_after is allowed only" in x for x in e))
        self.assertTrue(any("only an easy question" in x for x in e))

    def test_assumed_only_after_proceed_after(self):
        e = errs(
            status="assumed",
            proceed_after="2026-10-25",
            answer={"choice": "A", "via": "assumed", "at": "2026-10-23"},
        )
        self.assertTrue(any("before proceed_after" in x for x in e))

    def test_applied_needs_ref_and_record(self):
        e = errs(
            status="applied",
            answer={"choice": "A", "via": "chat", "at": "2026-10-22"},
            applied={"ref": "abc1234"},
        )
        self.assertTrue(any("applied.record" in x for x in e))

    def test_open_lead_question_needs_batch(self):
        self.assertTrue(any("needs a batch" in e for e in errs(batch=None)))

    def test_queued_needs_no_gate(self):
        self.assertEqual(errs(status="queued", gate=None, asked=None, batch=None), [])

    def test_claude_never_decides_hard(self):
        self.assertTrue(
            any("never Claude" in e for e in errs(decider="claude", reversibility="hard"))
        )

    def test_unknown_field_and_after(self):
        e = errs(colour="red", after=["DQ-999"])
        self.assertTrue(any("unknown field colour" in x for x in e))
        self.assertTrue(any("unknown question DQ-999" in x for x in e))


class Inbox(unittest.TestCase):
    def test_builds_and_escapes(self):
        d = copy.deepcopy(GOOD)
        d["context"] = "A **bold** fact </script><b>x</b>"
        page = build_inbox.build([d], built="2026-10-22")
        self.assertNotIn("</script><b>", page)
        self.assertIn("<b>bold<\\/b>", page)  # "</" is escaped inside the script
        self.assertIn("Built 2026-10-22", page)
        self.assertNotIn("/*__REGISTER__*/", page)

    def test_ref_url(self):
        self.assertTrue(build_inbox.ref_url("abc1234").endswith("/commit/abc1234"))
        self.assertTrue(build_inbox.ref_url("#12").endswith("/pull/12"))
        self.assertIsNone(build_inbox.ref_url("somewhere"))


class Case(unittest.TestCase):
    WP = {"WP-C-03"}

    def test_accepted_claim_needs_review_accepted_evidence_and_no_open_defeater(self):
        r = caselib.Records(
            claims=[
                {"id": "CL-001", "statement": "Safe", "status": "accepted", "evidence": ["EV-001"]}
            ],
            evidence=[
                {"id": "EV-001", "title": "HARA", "status": "drafted", "work_product": "WP-C-03"}
            ],
            defeaters=[
                {"id": "DF-001", "statement": "Maybe not", "against": "CL-001", "status": "open"}
            ],
        )
        e = caselib.check(r, self.WP)
        self.assertTrue(any("names the review" in x for x in e))
        self.assertTrue(any("evidence EV-001 is drafted" in x for x in e))
        self.assertTrue(any("DF-001 is open" in x for x in e))

    def test_references_and_loops(self):
        r = caselib.Records(
            claims=[
                {"id": "CL-001", "statement": "a", "status": "proposed", "parent": "CL-002"},
                {"id": "CL-002", "statement": "b", "status": "proposed", "parent": "CL-001"},
            ],
            evidence=[
                {"id": "EV-001", "title": "x", "status": "missing", "work_product": "WP-Z-99"}
            ],
            defeaters=[{"id": "DF-001", "statement": "y", "against": "CL-404", "status": "closed"}],
        )
        e = caselib.check(r, self.WP)
        self.assertTrue(any("loops" in x for x in e))
        self.assertTrue(any("WP-Z-99" in x for x in e))
        self.assertTrue(any("CL-404" in x for x in e))
        self.assertTrue(any("closed_by" in x for x in e))

    def test_real_records_pass(self):
        self.assertEqual(caselib.check(caselib.load()), [])


class Hara(unittest.TestCase):
    def test_asil_matches_iso_26262_3_table_4(self):
        # Spot cases read from ISO 26262-3:2018 Table 4, independent of the sum rule hara.asil uses.
        table = {
            ("S3", "E4", "C3"): "D",
            ("S3", "E4", "C2"): "C",
            ("S3", "E4", "C1"): "B",
            ("S3", "E3", "C3"): "C",
            ("S3", "E2", "C3"): "B",
            ("S3", "E1", "C3"): "A",
            ("S2", "E4", "C3"): "C",
            ("S2", "E4", "C2"): "B",
            ("S2", "E3", "C2"): "A",
            ("S1", "E4", "C3"): "B",
            ("S1", "E4", "C1"): "QM",
            ("S1", "E3", "C3"): "A",
            ("S1", "E2", "C3"): "QM",
            ("S2", "E1", "C1"): "QM",
            ("S0", "E4", "C3"): "QM",
            ("S3", "E0", "C3"): "QM",
            ("S3", "E4", "C0"): "QM",
        }
        for (s, e, c), want in table.items():
            self.assertEqual(hara.asil(s, e, c), want, (s, e, c))

    def test_real_model_passes_and_goals_take_the_highest_asil(self):
        m = hara.load()
        self.assertEqual(hara.check(m), [])
        ev = hara.rated(m)
        ga = hara.goal_asil(m, ev)
        for g in m["goals"]:
            mine = [e["asil"] for e in ev if e["hazard"] in g["hazards"]]
            self.assertEqual(ga[g["id"]], max(mine, key=hara.ASILS.index), g["id"])

    def test_model_breaking_a_rule_is_refused(self):
        m = hara.load()
        cases = []
        bad = copy.deepcopy(m)
        bad["events"][0]["severity"] = "S4"
        cases.append((bad, "severity"))
        bad = copy.deepcopy(m)
        bad["events"][0]["id"] = "HE-09.9"  # number does not match its hazard
        cases.append((bad, "must start with"))
        bad = copy.deepcopy(m)
        bad["goals"][0]["hazards"].append("H-02")  # H-02 now in two goals
        cases.append((bad, "exactly one safety goal"))
        bad = copy.deepcopy(m)
        bad["events"] = [e for e in bad["events"] if e["hazard"] != "H-09"]
        cases.append((bad, "no hazardous event rates it"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in hara.check(model)), needle)


class Fsc(unittest.TestCase):
    def setUp(self):
        self.m, self.sg = fsc.load(), fsc.goals()
        self.aou, self.dq = fsc.aous(), check_decisions.load()

    def errs(self, m):
        return fsc.check(m, self.sg, self.aou, self.dq)

    def test_real_model_passes_and_every_goal_has_a_requirement_at_its_asil(self):
        self.assertEqual(self.errs(self.m), [])
        for g, d in self.sg.items():
            self.assertTrue(
                any(f["goal"] == g and f["asil"] == d["asil"] for f in self.m["fsrs"]), g
            )

    def test_element_asil_is_the_highest_of_its_requirements(self):
        ea = fsc.element_asil(self.m)
        self.assertEqual(ea["EL-01"], "QM")
        self.assertEqual(ea["EL-02"], "D")

    def test_model_breaking_a_rule_is_refused(self):
        cases = []
        bad = copy.deepcopy(self.m)
        next(f for f in bad["fsrs"] if f["goal"] == "SG-04" and f["asil"] == "D")["asil"] = "B"
        cases.append((bad, "neither QM nor"))
        bad = copy.deepcopy(self.m)
        bad["fsrs"] = [f for f in bad["fsrs"] if not (f["goal"] == "SG-09" and f["asil"] != "QM")]
        cases.append((bad, "no FSR at its ASIL"))
        bad = copy.deepcopy(self.m)
        bad["elements"][3]["aou"] = "AOU-99"
        cases.append((bad, "is not in WP-C-01"))
        bad = copy.deepcopy(self.m)
        bad["fsrs"][0]["pending"] = "DQ-001"  # an applied decision
        cases.append((bad, "apply the decision"))
        bad = copy.deepcopy(self.m)
        bad["fsrs"][0]["id"] = "FSR-07.99"
        cases.append((bad, "must start with"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in self.errs(model)), needle)


class Sotif(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(sotif.check(sotif.load(), sotif.functions(), sotif.hara_hazards()), [])

    def test_further_evaluation_follows_iso_21448_section_6(self):
        self.assertTrue(sotif.further({"severity": "S2", "controllability": "C3"}))
        self.assertFalse(sotif.further({"severity": "S0", "controllability": "C3"}))
        self.assertFalse(sotif.further({"severity": "S3", "controllability": "C0"}))

    def test_model_breaking_a_rule_is_refused(self):
        m, funcs, hz = sotif.load(), sotif.functions(), sotif.hara_hazards()
        cases = []
        bad = copy.deepcopy(m)
        bad["hazards"][0]["functions"] = ["F-99"]
        cases.append((bad, "is not in WP-C-01"))
        bad = copy.deepcopy(m)
        bad["hazards"][0]["hara"] = ["H-99"]
        cases.append((bad, "does not exist"))
        bad = copy.deepcopy(m)
        bad["hazards"][0]["insufficiency"] = "both"
        cases.append((bad, "insufficiency must be"))
        bad = copy.deepcopy(m)
        bad["hazards"][1]["id"] = bad["hazards"][0]["id"]
        cases.append((bad, "duplicate id"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in sotif.check(model, funcs, hz)), needle)


class Fallback(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(fallback.check(fallback.load(), fallback.known()), [])

    def test_stopping_time_and_distance(self):
        # Constant deceleration when the jerk is very high: v²/2a and v/a.
        t, d = fallback.stop(10.0, 2.0, 1e9)
        self.assertAlmostEqual(t, 5.0, places=3)
        self.assertAlmostEqual(d, 25.0, places=3)
        # Stops while the braking is still ramping up: v0 = j t²/2.
        t, d = fallback.stop(0.5, 5.0, 1.0)
        self.assertAlmostEqual(t, 1.0)
        self.assertAlmostEqual(d, 0.5 - 1.0 / 6)

    def test_model_breaking_a_rule_is_refused(self):
        m, k = fallback.load(), fallback.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["mrms"][-1]["asil"] = "B"
        cases.append((bad, "below SG-07"))
        bad = copy.deepcopy(m)
        bad["mrms"][2]["fallback"] = "MRM-1"
        cases.append((bad, "must be a later MRM"))
        bad = copy.deepcopy(m)
        tr = next(t for t in bad["triggers"] if t["id"] == "TR-01")
        tr["response"] = "MRM-3"
        cases.append((bad, "which it takes away"))
        bad = copy.deepcopy(m)
        tr = next(t for t in bad["triggers"] if t["id"] == "TR-01")
        tr["detected_by"] = ["EL-01"]
        cases.append((bad, "no element that detects it survives"))
        bad = copy.deepcopy(m)
        bad["triggers"][0]["refs"] = ["MON-99"]
        cases.append((bad, "does not exist"))
        bad = copy.deepcopy(m)
        bad["triggers"][0]["pending"] = "DQ-001"
        cases.append((bad, "apply the decision"))
        bad = copy.deepcopy(m)
        for c in bad["mrcs"]:
            c["asil"] = "QM"
        cases.append((bad, "no minimal risk condition is rated"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in fallback.check(model, k)), needle)


class TreeChecks(unittest.TestCase):
    def test_table_cell_count(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n| 1 |\n"
        self.assertEqual(len(check_tables.check_text(md, "x.md")), 1)
        self.assertEqual(
            check_tables.check_text("```\n| A | B |\n|---|---|\n| 1 |\n```\n", "x.md"), []
        )

    def test_slug_matches_github(self):
        self.assertEqual(
            check_links.slug("4. How the standards fit together"),
            "4-how-the-standards-fit-together",
        )
        self.assertEqual(
            check_links.slug("3.1 Management (`01-management/`)"), "31-management-01-management"
        )

    def test_broken_link_and_anchor(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t, "a.md"), Path(t, "b.md")
            b.write_text("# Title\n\n## Real part\n", encoding="utf-8")
            a.write_text(
                "[ok](b.md#real-part) [bad](b.md#nope) [gone](c.md) `[code](c.md)` [web](https://x.org)\n",
                encoding="utf-8",
            )
            orig = check_links.REPO
            check_links.REPO = Path(t)
            try:
                e = check_links.check([a])
            finally:
                check_links.REPO = orig
        self.assertEqual(len(e), 2)

    def test_header_status_must_match_register(self):
        p = next(x for x in wpregister.load().products if x.wid == "WP-C-03")
        original = p.path.read_text(encoding="utf-8")
        text = re.sub(
            r"^\| Status \| [^|]+ \|$", "| Status | Approved |", original, count=1, flags=re.M
        )
        self.assertNotEqual(text, original)
        self.assertTrue(any("register says" in x for x in check_headers.check_product(p, text)))
        self.assertEqual(check_headers.check_product(p, p.path.read_text(encoding="utf-8")), [])


class Generators(unittest.TestCase):
    """Each generator is deterministic and its output is well-formed, accessible SVG or Markdown."""

    def test_deterministic_and_accessible(self):
        import xml.dom.minidom

        for mod in (
            fig_m00_register,
            folder_index,
            fig_lifecycle,
            fig_questions,
            dashboard,
            fig_c01_boundary,
            hara,
            fsc,
            sotif,
            fallback,
        ):
            first, second = mod.build(), mod.build()
            self.assertEqual(first, second, mod.__name__)
            for path, content in first.items():
                if path.suffix == ".svg":
                    doc = xml.dom.minidom.parseString(content)
                    root = doc.documentElement
                    self.assertEqual(root.getAttribute("role"), "img", path)
                    self.assertTrue(
                        doc.getElementsByTagName("title") and doc.getElementsByTagName("desc"), path
                    )
                    self.assertIn("prefers-color-scheme: dark", content, path)

    def test_figure_disagreeing_with_register_is_refused(self):
        self.assertEqual(sorted(fig_questions.FIGURES), ["DQ-001", "DQ-002"])
        orig = fig_questions.CHAIN
        fig_questions.CHAIN = {**orig, "D": orig["A"]}
        fig_questions.FIGURES["DQ-002"] = (
            "figures/dq-002.svg",
            fig_questions.dq002,
            list(fig_questions.CHAIN),
        )
        try:
            with self.assertRaises(figkit.FigureError):
                fig_questions.build()
        finally:
            fig_questions.CHAIN = orig
            fig_questions.FIGURES["DQ-002"] = (
                "figures/dq-002.svg",
                fig_questions.dq002,
                list(orig),
            )

    def test_boundary_figure_refuses_a_table_it_cannot_draw(self):
        orig = fig_c01_boundary.DOC
        text = orig.read_text(encoding="utf-8")
        cases = [
            text.replace(
                "| Passengers | No |", "| Passengers | Yes |"
            ),  # wrong side of the boundary
            text.replace(
                "| I-09 | Passengers |", "| I-09 | Update backend |"
            ),  # ends differ from the route
            text.replace("| I-12 |", "| I-13 |"),  # an interface with no route
        ]
        with tempfile.TemporaryDirectory() as t:
            for i, changed in enumerate(cases):
                self.assertNotEqual(changed, text, i)
                p = Path(t, f"c01-{i}.md")
                p.write_text(changed, encoding="utf-8")
                fig_c01_boundary.DOC = p
                try:
                    with self.assertRaises(figkit.FigureError, msg=str(i)):
                        fig_c01_boundary.build()
                finally:
                    fig_c01_boundary.DOC = orig

    def test_emit_check_reports_stale(self):
        with tempfile.TemporaryDirectory(dir=figkit.REPO) as t:
            p = Path(t, "x.svg")
            p.write_text("old", encoding="utf-8")
            self.assertEqual(figkit.emit({p: "new"}, ["--check"]), 1)
            self.assertEqual(p.read_text(encoding="utf-8"), "old")
            self.assertEqual(figkit.emit({p: "new"}, []), 0)
            self.assertEqual(figkit.emit({p: "new"}, ["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
