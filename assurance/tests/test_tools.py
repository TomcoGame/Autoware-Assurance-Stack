#!/usr/bin/env python3
"""Unit tests of the assurance tools: the parsers, the checkers and the generators.

python3 -m unittest discover -s assurance/tests -p 'test_*.py' -v
"""

from __future__ import annotations

import copy
import io
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
    "02-concept/triggering",
    "02-concept/modifications",
    "08-analyses/stpa",
    "02-concept/tara",
    "02-concept/cybersecurity",
    "02-concept/ai",
    "02-concept/misuse",
    "03-system/tsc",
    "03-system/timing",
    "03-system/tsr",
    "03-system/hsi",
    "03-system/secarch",
    "03-system/integ",
    "03-system/verif",
    "06-validation/scenarios",
    "06-validation/simenv",
    "case/tools",
    "trace/tools",
):
    sys.path.insert(0, str(ASSURANCE / sub))

import ai  # noqa: E402
import build_inbox  # noqa: E402
import caselib  # noqa: E402
import check_decisions  # noqa: E402
import check_headers  # noqa: E402
import check_links  # noqa: E402
import check_tables  # noqa: E402
import cybersecurity  # noqa: E402
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
import hsi  # noqa: E402
import integ  # noqa: E402
import misuse  # noqa: E402
import modifications  # noqa: E402
import scenarios  # noqa: E402
import scenes  # noqa: E402
import secarch  # noqa: E402
import simenv  # noqa: E402
import sotif  # noqa: E402
import stpa  # noqa: E402
import tara  # noqa: E402
import timing  # noqa: E402
import triggering  # noqa: E402
import tsc  # noqa: E402
import tsr  # noqa: E402
import verif  # noqa: E402
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


class HaraRows(unittest.TestCase):
    def test_rows_cover_every_rated_pair_in_every_situation_and_condition(self):
        m, a = hara.load(), hara.load_analysis()
        rs = hara.analysis_rows(m, a)
        self.assertEqual(
            len(rs), len(hara.expanded(a)) * len(m["situations"]) * len(a["conditions"])
        )
        self.assertEqual(len({r["key"] for r in rs}), len(rs))
        r = next(r for r in rs if r["key"] == "F-06/M07/OS-16/W02")
        self.assertEqual((r["s"], r["e"], r["c"], r["asil"]), ("S3", "E3", "C3", "C"))
        self.assertTrue(all(r["asil"] == "QM" for r in rs if r["s"] == "S0"))

    def test_readme_states_the_row_count(self):
        m, a = hara.load(), hara.load_analysis()
        n = len(hara.analysis_rows(m, a))
        readme = (ASSURANCE.parent / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"{n:,}".replace(",", " ") + " rows", readme)

    def test_analysis_breaking_a_rule_is_refused(self):
        m, a = hara.load(), hara.load_analysis()

        def fn(model, fid):
            return next(f for f in model["functions"] if f["id"] == fid)

        cases = []
        bad = copy.deepcopy(a)
        fn(bad, "F-02")["class"]["M02"] = ["SC", "H-02", "M07", "x"]
        cases.append((bad, "F-02/M02: folded into M07, which is not an SC pair rated itself"))
        bad = copy.deepcopy(a)
        fn(bad, "F-02")["class"]["M02"] = ["SC", "H-03", "M01", "x"]
        cases.append((bad, "F-02/M02: folded into M01, which leads to H-02, not H-03"))
        bad = copy.deepcopy(a)
        del fn(bad, "F-03")["class"]["M05"]
        cases.append((bad, "F-03/M05: needs [class, hazard, folded into, reason]"))
        bad = copy.deepcopy(a)
        bad["severity"]["H-02"]["OS-09"] = ["S3", "split", "by a comma"]
        cases.append((bad, "H-02 in OS-09: needs [severity, reason]"))
        bad = copy.deepcopy(a)
        bad["none"]["H-06"] = {}
        cases.append((bad, "H-06 in OS-01: neither a severity nor a reason for S0"))
        bad = copy.deepcopy(a)
        bad["severity"]["H-01"]["OS-06"] = ["S2", "x"]
        cases.append((bad, "HE-01.1: rated S3, more severe than S2 for H-01 in OS-06"))
        bad = copy.deepcopy(a)
        bad["severity"]["H-03"]["OS-02"] = ["S3", "x"]
        bad["conditions"][0]["exposure"] = "E4"
        bad["severity"]["H-03"]["OS-01"] = ["S3", "x"]
        cases.append((bad, "exceeds SG-03's C"))
        bad = copy.deepcopy(a)
        bad["guidewords"]["M02"] = {
            "name": "Stops functioning",
            "means": "Acts at first",
            "then": None,
        }
        cases.append((bad, "M02: needs only a name and a means"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in hara.check_analysis(m, model)), needle)


class HaraFolder(unittest.TestCase):
    def test_hazop_has_every_pair_with_its_full_deviation(self):
        m, a = hara.load(), hara.load_analysis()
        rs = hara.hazop_rows(m, a)
        self.assertEqual(len(rs), len(a["functions"]) * len(a["guidewords"]))
        r = next(r for r in rs if r["key"] == "F-01/M02")
        self.assertEqual(r["deviation"], "Acts at first, then stops while still needed")

    def test_every_safety_related_guide_word_has_a_scene_card(self):
        m, a = hara.load(), hara.load_analysis()
        self.assertEqual(scenes.check(a, {h["id"] for h in m["hazards"]}), [])
        figs = hara.scene_files(m, a)
        for f in a["functions"]:
            sc = sorted(g for g, c in f["class"].items() if c[0] == "SC")
            path = hara.scene_file(f)
            if not sc:
                self.assertNotIn(path, figs, f["id"])
                continue
            cards = re.findall(r'class="gid">(M\d\d)<', figs[path][1])
            self.assertEqual(sorted(cards), sc, f["id"])

    def test_scene_starts_where_the_chart_does(self):
        self.assertEqual(scenes.onset("M01"), 20)
        self.assertEqual(scenes.onset("M02"), 55)
        self.assertEqual(scenes.onset("M07"), 20)
        self.assertEqual(scenes.onset("M10"), 55)

    def test_folder_page_links_every_file_in_the_folder(self):
        page = hara.build()[hara.README]
        for p in hara.HERE.iterdir():
            if p.suffix in (".csv", ".svg", ".yaml"):
                self.assertIn(f"]({p.name})", page, p.name)
        self.assertIn("../figures/fig-c01-5-1-boundary.svg", page)
        self.assertNotIn("](hara/", page)


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

    def test_every_goal_has_a_scene_card(self):
        self.assertEqual(fsc.envelope.check(self.sg), [])
        svg = fsc.envelope.sheet(self.m, self.sg, {e["id"]: e for e in self.m["elements"]})
        self.assertEqual(sorted(re.findall(r'class="gid">(SG-\d\d)<', svg)), sorted(self.sg))
        self.assertIn("SG-99: no scene", fsc.envelope.check({**self.sg, "SG-99": {}})[0])

    def test_fsrs_csv_traces_every_requirement(self):
        import csv

        rows = list(csv.DictReader(io.StringIO(fsc.fsrs_csv(self.m, self.sg))))
        self.assertEqual([r["ID"] for r in rows], [f["id"] for f in self.m["fsrs"]])
        self.assertTrue(all(r["Verification cases (WP-S-09)"] != "—" for r in rows))
        r = next(r for r in rows if r["ID"] == "FSR-01.01")
        self.assertIn("SM-01", r["Safety mechanisms (WP-S-03)"])
        self.assertIn("TSR-01.02", r["Technical safety requirements (WP-S-02)"])

    def test_folder_page_links_every_file_in_the_folder(self):
        page = fsc.build()[fsc.README]
        for p in fsc.HERE.iterdir():
            if p.suffix in (".csv", ".svg", ".yaml", ".py"):
                self.assertIn(f"]({p.name})", page, p.name)
        self.assertIn("../figures/fig-c01-5-1-boundary.svg", page)
        self.assertNotIn("](fsc/", page)

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


class Triggering(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(triggering.check(triggering.load(), triggering.known()), [])

    def test_hazards_follow_from_insufficiencies(self):
        m = triggering.load()
        tc = {"exposes": ["FI-01", "FI-04"]}
        fis = {f["id"]: f for f in m["insufficiencies"]}
        self.assertEqual(
            triggering.leads_to(m, tc),
            sorted(set(fis["FI-01"]["hazards"] + fis["FI-04"]["hazards"])),
        )

    def test_model_breaking_a_rule_is_refused(self):
        m, k = triggering.load(), triggering.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["insufficiencies"] = [f for f in bad["insufficiencies"] if "SH-07" not in f["hazards"]]
        cases.append((bad, "SH-07: needs further evaluation"))
        bad = copy.deepcopy(m)
        bad["insufficiencies"].append(dict(bad["insufficiencies"][1], id="FI-99"))
        cases.append((bad, "FI-99: no triggering condition exposes it"))
        bad = copy.deepcopy(m)
        fi = next(f for f in bad["insufficiencies"] if f["id"] == "FI-05")
        fi["ai"] = ["coverage"]
        cases.append((bad, "none of its functions is an ML function"))
        bad = copy.deepcopy(m)
        for f in bad["insufficiencies"]:
            if "F-03" in f["functions"]:
                f.pop("ai", None)
        cases.append((bad, "F-03: an ML function"))
        bad = copy.deepcopy(m)
        tc = next(t for t in bad["triggers"] if t["id"] == "TC-22")
        tc.pop("monitor")
        cases.append((bad, "needs the monitor"))
        bad = copy.deepcopy(m)
        bad["triggers"][0]["odd"] = ["ODD-99"]
        cases.append((bad, "is not in WP-C-02"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in triggering.check(model, k)), needle)


class Modifications(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(modifications.check(modifications.load(), modifications.known()), [])

    def test_model_breaking_a_rule_is_refused(self):
        m, k = modifications.load(), modifications.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["modifications"] = [x for x in bad["modifications"] if "FI-11" not in x["addresses"]]
        cases.append((bad, "FI-11: no modification addresses it"))
        bad = copy.deepcopy(m)
        fm = next(x for x in bad["modifications"] if "FI-13" in x["addresses"])
        fm["type"] = "data"
        cases.append((bad, "FI-13: a specification insufficiency needs"))
        bad = copy.deepcopy(m)
        bad["modifications"][0]["concept"] = ["FSR-99.99"]
        cases.append((bad, "does not exist"))
        bad = copy.deepcopy(m)
        bad["modifications"][0]["pending"] = "DQ-001"
        cases.append((bad, "apply the decision"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in modifications.check(model, k)), needle)


class Stpa(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(stpa.check(stpa.load(), stpa.known()), [])

    def test_model_breaking_a_rule_is_refused(self):
        m, k = stpa.load(), stpa.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["links"][0]["actions"][0]["ucas"].pop("D")
        cases.append((bad, "type D has neither UCAs nor a reason"))
        bad = copy.deepcopy(m)
        bad["scenarios"] = [s for s in bad["scenarios"] if "UCA-45" not in s["ucas"]]
        cases.append((bad, "UCA-45: no loss scenario explains it"))
        bad = copy.deepcopy(m)
        bad["scenarios"][0]["measures"], bad["scenarios"][0]["new"] = [], []
        cases.append((bad, "neither a measure nor a new requirement"))
        bad = copy.deepcopy(m)
        bad["scenarios"][0]["measures"] = ["FSR-99.99"]
        cases.append((bad, "measure FSR-99.99 does not exist"))
        bad = copy.deepcopy(m)
        bad["requirements"].append({"id": "SR-99", "text": "x", "to": "y"})
        cases.append((bad, "SR-99: no scenario needs it"))
        bad = copy.deepcopy(m)
        bad["links"][0]["x"] = 300
        cases.append((bad, "is not within both boxes"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in stpa.check(model, k)), needle)


class Tara(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(tara.check(tara.load(), tara.known()), [])

    def test_feasibility_and_risk_are_computed(self):
        m = tara.load()
        t = {
            "damage": ["DS-01"],
            "factors": {
                "time": "≤1 day",
                "expertise": "layman",
                "knowledge": "public",
                "window": "unlimited",
                "equipment": "standard",
            },
        }
        self.assertEqual(tara.potential(m, t), 0)
        self.assertEqual(tara.feasibility(m, t), "High")
        self.assertEqual(tara.impact(m, t), "Severe")
        self.assertEqual(tara.risk(m, t), 5)
        t["factors"].update(time=">6 months", expertise="multiple experts")
        self.assertEqual(tara.feasibility(m, t), "Very low")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = tara.load(), tara.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["threats"] = [t for t in bad["threats"] if "DS-09" not in t["damage"]]
        cases.append((bad, "DS-09: no threat scenario leads to it"))
        bad = copy.deepcopy(m)
        ts = next(t for t in bad["threats"] if t["id"] == "TS-03")
        ts["controls"] = []
        cases.append((bad, "TS-03: its risk must be reduced but it names no control"))
        bad = copy.deepcopy(m)
        bad["threats"][0]["factors"]["time"] = "a fortnight"
        cases.append((bad, "is not a value of the method"))
        bad = copy.deepcopy(m)
        bad["assets"][0]["properties"] = ["X"]
        cases.append((bad, "properties must be among C, I, A"))
        bad = copy.deepcopy(m)
        bad["method"]["pending"] = "DQ-001"
        cases.append((bad, "apply the decision"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in tara.check(model, k)), needle)


class Cybersecurity(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(cybersecurity.check(cybersecurity.load(), cybersecurity.known()), [])

    def test_cal_is_the_highest_over_the_threats(self):
        m, k = cybersecurity.load(), cybersecurity.known()
        self.assertEqual(cybersecurity.cal(m, k, {"threats": ["TS-15"]}), "CAL1")
        self.assertEqual(cybersecurity.cal(m, k, {"threats": ["TS-15", "TS-01"]}), "CAL4")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = cybersecurity.load(), cybersecurity.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["goals"][0]["threats"] = ["TS-01"]
        cases.append((bad, "TS-03: its risk is reduced but no goal covers it"))
        bad = copy.deepcopy(m)
        bad["claims"] = bad["claims"][1:]
        cases.append((bad, "TS-05: its risk is retained but no claim"))
        bad = copy.deepcopy(m)
        bad["requirements"] = [r for r in bad["requirements"] if "CG-07" not in r["goals"]]
        cases.append((bad, "CG-07: no requirement meets it"))
        bad = copy.deepcopy(m)
        for r in bad["requirements"]:
            r["from"] = [x for x in r["from"] if x != "CR-11"]
        cases.append((bad, "CR-11: the TARA proposed it"))
        bad = copy.deepcopy(m)
        bad["vectors"]["TS-01"] = "telepathy"
        cases.append((bad, "TS-01: attack vector must be"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in cybersecurity.check(model, k)), needle)


class Ai(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(ai.check(ai.load(), ai.known()), [])

    def test_model_breaking_a_rule_is_refused(self):
        m, k = ai.load(), ai.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["systems"][0]["element"] = "EL-02"
        cases.append((bad, "no AI system may be on a rated element"))
        bad = copy.deepcopy(m)
        bad["systems"] = [s for s in bad["systems"] if s["function"] != "F-03"]
        cases.append((bad, "F-03: an ML function"))
        bad = copy.deepcopy(m)
        bad["requirements"] = [r for r in bad["requirements"] if r["kind"] != "uncertainty"]
        cases.append((bad, "no uncertainty requirement"))
        bad = copy.deepcopy(m)
        bad["systems"][0]["input"] = ["Smell"]
        cases.append((bad, "is not in WP-C-02"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in ai.check(model, k)), needle)


class Misuse(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(misuse.check(misuse.load(), misuse.known()), [])

    def test_model_breaking_a_rule_is_refused(self):
        m, k = misuse.load(), misuse.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["entries"] = [e for e in bad["entries"] if e["role"] != "R-04"]
        cases.append((bad, "R-04: no interaction or misuse"))
        bad = copy.deepcopy(m)
        bad["entries"][0]["measures"], bad["entries"][0]["new"] = [], []
        cases.append((bad, "neither a measure nor a new requirement"))
        bad = copy.deepcopy(m)
        bad["entries"][0]["refs"] = ["UCA-99"]
        cases.append((bad, "UCA-99 does not exist"))
        bad = copy.deepcopy(m)
        bad["requirements"].append({"id": "HR-99", "text": "x", "to": "y"})
        cases.append((bad, "HR-99: no entry needs it"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in misuse.check(model, k)), needle)


class Tsc(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(tsc.check(tsc.load(), tsc.known()), [])

    def test_every_mechanism_has_a_card_with_its_budget(self):
        m, k = tsc.load(), tsc.known()
        svg = tsc.cards.sheet(m, tsc.card_known(m, k))
        self.assertEqual(
            re.findall(r'class="gid">(SM-\d\d)<', svg), [s["id"] for s in m["mechanisms"]]
        )
        tm, tmech = tsc.cards.timed()
        b = tsc.cards.budget(next(s for s in m["mechanisms"] if s["id"] == "SM-05"), tm, tmech)
        self.assertEqual(b["goal"], "SG-08")
        self.assertIsNone(
            tsc.cards.budget(next(s for s in m["mechanisms"] if s["id"] == "SM-04"), tm, tmech)
        )

    def test_mechanisms_csv_traces_every_mechanism(self):
        import csv

        m, k = tsc.load(), tsc.known()
        rows = list(csv.DictReader(io.StringIO(tsc.mechanisms_csv(m, k))))
        self.assertEqual([r["ID"] for r in rows], [s["id"] for s in m["mechanisms"]])
        r = rows[0]
        self.assertIn("TSR-01.02", r["Technical safety requirements (WP-S-02)"])
        self.assertIn("IT-03", r["Integration test cases (WP-S-08)"])
        self.assertTrue(r["Binding FTTI (WP-S-04)"].endswith("(SG-01)"))

    def test_folder_page_links_every_file_in_the_folder(self):
        page = tsc.build()[tsc.README]
        for p in tsc.HERE.iterdir():
            if p.suffix in (".csv", ".svg", ".yaml", ".py"):
                self.assertIn(f"]({p.name})", page, p.name)
        self.assertNotIn("](tsc/", page)

    def test_component_asil_is_derived(self):
        m, k = tsc.load(), tsc.known()
        ca = tsc.component_asil(m, k)
        self.assertEqual(ca["CMP-01"], "QM")
        self.assertEqual(ca["CMP-02"], "D")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = tsc.load(), tsc.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["mechanisms"] = [s for s in bad["mechanisms"] if "FSR-07.03" not in s["implements"]]
        cases.append((bad, "FSR-07.03: rated D but no mechanism"))
        bad = copy.deepcopy(m)
        sm = next(s for s in bad["mechanisms"] if s["id"] == "SM-07")
        sm["host"] = "CMP-01"
        cases.append((bad, "but CMP-01 is part of EL-01"))
        bad = copy.deepcopy(m)
        bad["mechanisms"][0]["reaction"] = ["MRM-9"]
        cases.append((bad, "is not a fallback trigger or MRM"))
        bad = copy.deepcopy(m)
        bad["links"][1]["x"] = 600
        cases.append((bad, "is not within both boxes"))
        bad = copy.deepcopy(m)
        bad["redundancy"] = [r for r in bad["redundancy"] if r["id"] != "RD-02"]
        cases.append((bad, "no redundancy entry between it and CMP-05"))
        bad = copy.deepcopy(m)
        next(c for c in bad["components"] if c["id"] == "CMP-05").pop("decomposed")
        cases.append((bad, "decomposed with CMP-05, which is not decomposed with it"))
        bad = copy.deepcopy(m)
        next(c for c in bad["components"] if c["id"] == "CMP-04")["also"]["decision"] = "DQ-008"
        cases.append((bad, "CMP-04: also needs a decomposed component and an answered decision"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in tsc.check(model, k)), needle)


class Timing(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(timing.check(timing.load(), timing.known()), [])

    def test_ftti_follows_the_kinematics(self):
        m = timing.load()
        g = next(x for x in m["goals"] if x["id"] == "SG-01")
        hi = m["ranges"][g["range"]]["high"]
        self.assertAlmostEqual(timing.ftti(m, "SG-01", "high"), (2 * g["margin"] / hi) ** 0.5)
        self.assertEqual(
            timing.ftti(m, "SG-07", "high"),
            min(timing.ftti(m, x, "high") for x in ("SG-01", "SG-02", "SG-04")),
        )
        self.assertIsNone(timing.ftti(m, "SG-03", "high"))

    def test_model_breaking_a_rule_is_refused(self):
        m, k = timing.load(), timing.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["goals"] = [g for g in bad["goals"] if g["id"] != "SG-09"]
        cases.append((bad, "SG-09: safety goal with no timing entry"))
        bad = copy.deepcopy(m)
        bad["allocation"] = {"detect": 0.6, "react": 0.6}
        cases.append((bad, "add up to at most 1"))
        bad = copy.deepcopy(m)
        bad["goals"][0]["margin"] = 0
        cases.append((bad, "margin must be a positive number"))
        bad = copy.deepcopy(m)
        bad["mechanisms"][0]["goals"] = ["SG-03"]
        cases.append((bad, "goal SG-03 has no FTTI"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in timing.check(model, k)), needle)


class Tsr(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(tsr.check(tsr.load(), tsr.known()), [])

    def test_asil_follows_fsrs_and_decomposition(self):
        m, k = tsr.load(), tsr.known()
        by = {r["id"]: r for r in m["tsrs"]}
        self.assertEqual(tsr.asil(by["TSR-09.01"], k), "D")
        self.assertEqual(tsr.asil(by["TSR-09.02"], k), "B(D)")
        self.assertEqual(tsr.asil(by["TSR-09.04"], k), "C")
        params = {p["id"]: p for p in m["parameters"]}
        self.assertEqual(tsr.waits(by["TSR-04.01"], params), [])
        self.assertIn("3 m/s² (DQ-033 A)", tsr.value(params["P-05"], m, k))

    def test_model_breaking_a_rule_is_refused(self):
        m, k = tsr.load(), tsr.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["tsrs"] = [r for r in bad["tsrs"] if r["mechanism"] != "SM-07"]
        cases.append((bad, "SM-07: no technical safety requirement"))
        bad = copy.deepcopy(m)
        bad["tsrs"] = [r for r in bad["tsrs"] if r["id"] != "TSR-01.04"]
        cases.append((bad, "SM-01: FSR-06.01 is refined by none"))
        bad = copy.deepcopy(m)
        next(r for r in bad["tsrs"] if r["id"] == "TSR-07.01")["component"] = "CMP-06"
        cases.append((bad, "neither the host of SM-07"))
        bad = copy.deepcopy(m)
        next(r for r in bad["tsrs"] if r["id"] == "TSR-07.01")["timing"] = "detect"
        cases.append((bad, "SM-07 has no budget in WP-S-04"))
        bad = copy.deepcopy(m)
        for r in bad["tsrs"]:
            if r["mechanism"] == "SM-10":
                r.pop("timing", None)
        cases.append((bad, "SM-10: time-critical in WP-S-04"))
        bad = copy.deepcopy(m)
        next(r for r in bad["tsrs"] if r["id"] == "TSR-07.01")["fsrs"] = ["FSR-01.01"]
        cases.append((bad, "refines FSR-01.01, which SM-07 does not implement"))
        bad = copy.deepcopy(m)
        next(p for p in bad["parameters"] if p["id"] == "P-05")["pending"] = "DQ-019"
        cases.append((bad, "pending on DQ-019, which is applied"))
        bad = copy.deepcopy(m)
        bad["parameters"].append({"id": "P-99", "name": "Unused", "source": "Nowhere"})
        cases.append((bad, "P-99: used by no requirement"))
        bad = copy.deepcopy(m)
        next(p for p in bad["parameters"] if p["id"] == "P-05").pop("decision")
        cases.append((bad, "P-05: a value needs the decision"))
        k2 = copy.deepcopy(k)
        k2["components"]["CMP-04"].pop("also")
        self.assertIn(
            "TSR-09.04: ASIL C on CMP-04, which WP-S-03 shows at B(D) only", tsr.check(m, k2)
        )
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in tsr.check(model, k)), needle)


class Hsi(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(hsi.check(hsi.load(), hsi.known()), [])

    def test_timeout_is_the_receivers_detection_budget(self):
        m, k = hsi.load(), hsi.known()
        by = {s["id"]: s for s in m["signals"]}
        to, sm = hsi.tmo(m, by["SIG-03"], k)
        lo = timing.bound(k["timing"], k["timed"]["SM-05"])[0]
        self.assertEqual(sm, "SM-05")
        self.assertAlmostEqual(to, lo * k["timing"]["allocation"]["detect"])
        self.assertIsNone(hsi.tmo(m, by["SIG-06"], k))
        self.assertEqual(hsi.asils(by["SIG-03"], k, "CMP-01"), "QM")
        self.assertEqual(hsi.asils(by["SIG-07"], k, "CMP-04"), "C, B(D)")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = hsi.load(), hsi.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["interfaces"] = [f for f in bad["interfaces"] if f["id"] != "IF-09"]
        bad["signals"] = [s for s in bad["signals"] if s["interface"] != "IF-09"]
        cases.append((bad, "link CMP-09→CMP-02 of WP-S-03 needs exactly one interface"))
        bad = copy.deepcopy(m)
        next(s for s in bad["signals"] if s["id"] == "SIG-01")["protection"] = "e2e"
        cases.append((bad, "SIG-01: crosses the untrusted IF-01, so it must be signed"))
        bad = copy.deepcopy(m)
        next(s for s in bad["signals"] if s["id"] == "SIG-03")["protection"] = "none"
        cases.append((bad, "SIG-03: serves a rated requirement but is unprotected"))
        bad = copy.deepcopy(m)
        next(s for s in bad["signals"] if s["id"] == "SIG-19")["serves"] = ["TSR-16.01"]
        cases.append((bad, "SIG-19: serves TSR-16.01 on CMP-08, which is on neither end of IF-09"))
        bad = copy.deepcopy(m)
        bad["internal"] = [x for x in bad["internal"] if x["tsr"] != "TSR-13.01"]
        cases.append((bad, "TSR-13.01: on a supplier component, but crosses no interface"))
        bad = copy.deepcopy(m)
        bad["diagnostics"][0]["component"] = "CMP-06"
        cases.append((bad, "HD-01: CMP-06 is outside the item"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in hsi.check(model, k)), needle)


class Scenarios(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(scenarios.check(scenarios.load(), scenarios.known()), [])

    def test_goals_at_stake_are_computed(self):
        m, k = scenarios.load(), scenarios.known()
        sc = next(s for s in m["scenarios"] if s["id"] == "SC-01")
        # HE-02.1 is H-02 (SG-02); HE-06.4 is H-06 (SG-06); TC-02 exposes FI-08, which causes SH-14 (H-03, SG-03).
        self.assertEqual(scenarios.stake(sc, k), ["SG-02", "SG-03", "SG-06"])
        self.assertAlmostEqual(scenarios.ceiling(m, "ODD-20"), 30 * scenarios.MPH)

    def test_model_breaking_a_rule_is_refused(self):
        m, k = scenarios.load(), scenarios.known()

        def sc(model, sid):
            return next(s for s in model["scenarios"] if s["id"] == sid)

        cases = []
        bad = copy.deepcopy(m)
        sc(bad, "SC-23")["triggers"] = []
        cases.append((bad, "TC-23: triggering condition with no scenario"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-26")["misuse"] = ["MU-22"]
        cases.append((bad, "MU-23: misuse case with no scenario"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-01")["triggers"].append("TC-99")
        cases.append((bad, "triggering condition TC-99 does not exist"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-01")["pass"]["refs"].append("FSR-99.01")
        cases.append((bad, "requirement FSR-99.01 does not exist"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-01")["parameters"][0]["max"] = 50
        cases.append((bad, "ODD-20 value 50 is above the ODD limit"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-04")["parameters"][2]["min"] = 150
        cases.append((bad, "ODD-11 value 150 is below the ODD limit"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-01")["parameters"][2]["values"] = ["snow"]
        cases.append((bad, "has no value snow"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-14")["pass"]["refs"].remove("FSR-07.05")
        cases.append((bad, "crosses the ODD boundary"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-06")["pass"]["refs"].remove("FSR-06.01")
        sc(bad, "SC-06")["pass"]["refs"].remove("FSR-06.02")
        sc(bad, "SC-06")["pass"]["refs"].remove("FSR-06.03")
        cases.append((bad, "SG-06 is at stake"))
        bad = copy.deepcopy(m)
        bad["odd"]["ODD-10"]["max"] = 5
        cases.append((bad, "max 5 is not stated in its quote"))
        bad = copy.deepcopy(m)
        bad["odd"]["ODD-12"]["values"]["fog"] = {"quote": "thick fog"}
        cases.append((bad, "is not in the row of WP-C-02"))
        bad = copy.deepcopy(m)
        sc(bad, "SC-01")["parameters"][-1]["min"] = 1
        cases.append((bad, "must not state min until it is fixed"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in scenarios.check(model, k)), needle)


class Simenv(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(simenv.check(simenv.load(), simenv.known()), [])

    def test_tcl_follows_impact_and_detection(self):
        self.assertEqual(simenv.tcl("TI1", "TD3"), "TCL1")
        self.assertEqual(simenv.tcl("TI2", "TD1"), "TCL1")
        self.assertEqual(simenv.tcl("TI2", "TD3"), "TCL3")
        self.assertEqual(simenv.pin(simenv.load()["simulators"][1]["pin"]), "22.0.0")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = simenv.load(), simenv.known()
        cases = []
        bad = copy.deepcopy(m)
        del bad["represent"]["ODD-10"]
        cases.append((bad, "ODD-10: ODD attribute with no representation"))
        bad = copy.deepcopy(m)
        bad["sensors"][0]["params"][0] = "position 1.2 m"
        cases.append((bad, "carries a value; the vehicle waits on DQ-008"))
        bad = copy.deepcopy(m)
        bad["sensors"] = [s for s in bad["sensors"] if s.get("component") != "CMP-05"]
        cases.append((bad, "CMP-05: sensor component of WP-S-03 with no stand-in"))
        bad = copy.deepcopy(m)
        del bad["participants"]["wheelchair"]
        cases.append((bad, "ODD-16 wheelchair: participant class with no entity"))
        bad = copy.deepcopy(m)
        bad["participants"]["car"]["category"] = "hovercraft"
        cases.append((bad, "not an OpenSCENARIO category"))
        bad = copy.deepcopy(m)
        bad["simulators"][0]["impact"] = "TI3"
        cases.append((bad, "impact must be TI1 or TI2"))
        bad = copy.deepcopy(m)
        bad["simulators"][1]["pin"]["key"] = "simulator/nothing"
        cases.append((bad, "is not in repositories/simulator.repos"))
        bad = copy.deepcopy(m)
        bad["represent"]["ODD-10"]["sims"] = []
        bad["represent"]["ODD-10"]["instead"] = "Not at all"
        cases.append((bad, "runs in simulation but varies ODD-10"))
        bad = copy.deepcopy(m)
        bad["vehicle"][0]["property"] = "Colour"
        cases.append((bad, "is not a property of WP-C-01 §6"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in simenv.check(model, k)), needle)


class Secarch(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(secarch.check(secarch.load(), secarch.known()), [])

    def test_cal_follows_the_goals_refined(self):
        m, k = secarch.load(), secarch.known()
        by = {r["id"]: r for r in m["tcsrs"]}
        goal = k["goals"]["CG-01"]
        self.assertEqual(
            secarch.cal(by["CSTR-01.02"], k),
            cybersecurity.cal(k["cyber"], k["cyber_known"], goal),
        )

    def test_model_breaking_a_rule_is_refused(self):
        m, k = secarch.load(), secarch.known()
        cases = []
        bad = copy.deepcopy(m)
        bad["zones"][3]["components"].remove("CMP-09")
        cases.append((bad, "CMP-09: must be in exactly one zone"))
        bad = copy.deepcopy(m)
        bad["conduits"] = [x for x in bad["conduits"] if x["interface"] != "IF-02"]
        cases.append((bad, "IF-02: crosses SZ-2 and SZ-3 but is not a conduit"))
        bad = copy.deepcopy(m)
        bad["conduits"].append({"interface": "IF-05", "controls": ["CR-09"]})
        cases.append((bad, "IF-05: joins two components of SZ-3"))
        bad = copy.deepcopy(m)
        bad["tcsrs"] = [r for r in bad["tcsrs"] if r["csr"] != "CSR-08"]
        bad["external"][1]["controls"] = ["CSTR-07.01"]
        cases.append((bad, "CSR-08: item-level requirement refined by no technical requirement"))
        bad = copy.deepcopy(m)
        bad["external"][1]["controls"] = ["CSTR-07.01"]
        bad["external"][1]["threats"] = ["TS-03"]
        cases.append((bad, "EX-02: TS-03 is reduced under CG-01, but no control here serves it"))
        bad = copy.deepcopy(m)
        bad["external"] = [e for e in bad["external"] if e["id"] != "EX-02"]
        cases.append((bad, "TS-09: reaches the item through no exposed interface"))
        bad = copy.deepcopy(m)
        next(r for r in bad["tcsrs"] if r["id"] == "CSTR-08.01")["csr"] = "CSR-02"
        cases.append((bad, "refines CSR-02, which the operating environment meets"))
        bad = copy.deepcopy(m)
        bad["external"][6]["pending"] = "DQ-031"
        cases.append((bad, "pending on DQ-031, which is applied"))
        bad = copy.deepcopy(m)
        bad["external"][6].pop("decision")
        cases.append((bad, "EX-07: no threat in the TARA, and no decision says why"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in secarch.check(model, k)), needle)


class Integ(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(integ.check(integ.load(), integ.known()), [])

    def test_budgets_come_from_the_timing_model(self):
        m, k = integ.load(), integ.known()
        case = next(c for c in m["cases"] if c["id"] == "IT-06")
        self.assertIn(
            f"TSR-05.01 detect within {tsr.budget(None, k['tsr_known'], 'SM-05', 'detect')}",
            integ.budgets(case, k),
        )
        self.assertEqual(integ.asil(case, k), "D")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = integ.load(), integ.known()

        def case(model, cid):
            return next(c for c in model["cases"] if c["id"] == cid)

        cases = []
        bad = copy.deepcopy(m)
        bad["steps"][3]["adds"].remove("CMP-09")
        cases.append((bad, "CMP-09: integrated 0 times"))
        bad = copy.deepcopy(m)
        bad["steps"][0]["interfaces"] = ["IF-02"]
        bad["steps"][2]["interfaces"] = ["IF-01"]
        cases.append((bad, "IS-1: IF-02 is exercised before both its ends are integrated"))
        bad = copy.deepcopy(m)
        case(bad, "IT-16")["covers"] = ["SIG-19"]
        cases.append((bad, "SIG-16: covered by no integration test case"))
        bad = copy.deepcopy(m)
        case(bad, "IT-01")["covers"].append("TSR-16.01")
        cases.append((bad, "IT-01: covers TSR-16.01, which needs CMP-08 integrated by IS-1"))
        bad = copy.deepcopy(m)
        case(bad, "IT-09")["methods"] = ["timing"]
        cases.append((bad, "TSR-10.01: detects faults for SM-10 but no case injects them"))
        bad = copy.deepcopy(m)
        case(bad, "IT-04")["methods"] = ["requirements", "fault-injection"]
        cases.append((bad, "TSR-02.01: has a WP-S-04 budget but no case measures its time"))
        bad = copy.deepcopy(m)
        case(bad, "IT-13")["env"] = "ENV-1"
        cases.append((bad, "IT-13: environment ENV-1 is not one of IS-4's"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in integ.check(model, k)), needle)


class Verif(unittest.TestCase):
    def test_real_model_passes(self):
        self.assertEqual(verif.check(verif.load(), verif.known()), [])

    def test_scenarios_carry_their_requirements_and_conditions(self):
        m, k = verif.load(), verif.known()
        case = next(c for c in m["cases"] if c["id"] == "VC-12")
        cov = verif.covered(case, k)
        self.assertIn("FSR-06.01", cov)
        self.assertIn("TC-12", cov)
        self.assertEqual(verif.asil(case, k), "D")

    def test_shadow_mode_does_not_verify_the_monitor(self):
        m, k = verif.load(), verif.known()
        case = next(c for c in m["cases"] if c["id"] == "VC-01")
        cov = verif.covered(case, k)
        self.assertNotIn("FSR-02.02", cov)
        self.assertIn("FSR-02.05", cov)
        self.assertEqual(verif.asil(case, k), "QM")

    def test_model_breaking_a_rule_is_refused(self):
        m, k = verif.load(), verif.known()

        def case(model, cid):
            return next(c for c in model["cases"] if c["id"] == cid)

        cases = []
        bad = copy.deepcopy(m)
        case(bad, "VC-15")["methods"] = ["scenario", "interface"]
        cases.append((bad, "FSR-08.01: WP-C-04 verifies it by fault injection"))
        bad = copy.deepcopy(m)
        case(bad, "VC-17")["covers"].remove("FSR-07.03")
        cases.append((bad, "FSR-07.03: requirement verified by no case"))
        bad = copy.deepcopy(m)
        case(bad, "VC-20")["covers"] = ["FM-01"]
        cases.append((bad, "FM-08: functional modification verified by no case"))
        bad = copy.deepcopy(m)
        case(bad, "VC-05")["scenarios"].append("SC-09")
        cases.append((bad, "VC-05: ENV-4 cannot run SC-09"))
        bad = copy.deepcopy(m)
        case(bad, "VC-01")["covers"].append("FSR-02.02")
        cases.append((bad, "VC-01: covers FSR-02.02, but its element EL-02 does not act in it"))
        bad = copy.deepcopy(m)
        for c in bad["cases"]:
            c["scenarios"] = [x for x in c["scenarios"] if x != "SC-22"]
        cases.append((bad, "SC-22: can be run in sim, xil but no case runs it"))
        bad = copy.deepcopy(m)
        del case(bad, "VC-04")["env"]
        cases.append((bad, "VC-04: tests, so needs an environment"))
        for model, needle in cases:
            self.assertTrue(any(needle in x for x in verif.check(model, k)), needle)


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
            triggering,
            modifications,
            stpa,
            tara,
            cybersecurity,
            ai,
            misuse,
            tsc,
            timing,
            tsr,
            hsi,
            scenarios,
            simenv,
            secarch,
            integ,
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
        self.assertEqual(sorted(fig_questions.FIGURES), ["DQ-001", "DQ-002", "DQ-034"])
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
