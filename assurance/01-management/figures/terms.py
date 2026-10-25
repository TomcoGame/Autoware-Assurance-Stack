#!/usr/bin/env python3
"""The closing table of a generated README: the abbreviations, terms and symbols it uses.

Every generator that writes a README passes its page through `close()`, which appends a table of
the TERMS entries the page's text matches and a link to the wiki glossary. An abbreviation on the
page that no entry defines is refused, so a page cannot gain a term a newcomer cannot look up.
"""

from __future__ import annotations

import os
from pathlib import Path
import re

import figkit as fk

GLOSSARY = fk.ASSURANCE.parent / "wiki" / "Glossary.md"
HEADING = "## Abbreviations, terms and symbols"

# (pattern, term, meaning). The table lists the entries whose pattern matches the page, words
# alphabetically, then symbols in this order. An identifier prefix is defined by what it numbers.
TERMS = [
    (
        r"\b(?:21434|21448|26262)\b|\bPAS 8800",
        "21434, 21448, 26262, PAS 8800",
        "ISO/SAE 21434 (cybersecurity), ISO 21448 (SOTIF), ISO 26262 (functional safety), ISO/PAS 8800 "
        '(AI safety). "26262-3" is part 3 of ISO 26262',
    ),
    (
        r"\b(?:ACQ|HWE|MAN|MLE|SUP|SWE|SYS|VAL)\.\d",
        "ACQ, HWE, MAN, MLE, SUP, SWE, SYS, VAL",
        "Automotive SPICE process groups: acquisition, hardware engineering, management, machine learning "
        'engineering, support, software engineering, system engineering, validation. "SWE.1–6" means '
        "processes 1 to 6 of the group",
    ),
    (r"\bAC-\d", "AC", "SOTIF acceptance criterion identifier, as in AC-01 (WP-C-05)"),
    (
        r"\bAD API\b",
        "AD API",
        "Autoware's autonomous driving API: the interface for trips, modes and requests",
    ),
    (
        r"\bAI\b",
        "AI",
        "Artificial intelligence; here the machine-learned perception and prediction models",
    ),
    (r"\bAIS-\d", "AIS", "AI system identifier, as in AIS-01 (WP-C-11)"),
    (r"\bAISR-\d", "AISR", "AI safety requirement identifier, as in AISR-01 (WP-C-11)"),
    (
        r"\bAOU-\d",
        "AOU",
        "Assumption of use: an assumption on the vehicle, infrastructure, people or "
        "environment, as in AOU-05",
    ),
    (
        r"\bAPI\b",
        "API",
        "Application programming interface: how one program asks another for something",
    ),
    (
        r"\bASILs?\b",
        "ASIL",
        "Automotive Safety Integrity Level, A (lowest) to D (highest), set by ISO 26262 for "
        "each safety goal. B(D) means rated B as part of a decomposition of D",
    ),
    (
        r"\bASPICE\b",
        "ASPICE",
        "Automotive SPICE: a model for rating how capable the development process is",
    ),
    (
        r"\bAUTOSAR\b",
        "AUTOSAR",
        "AUTomotive Open System ARchitecture: an industry standard for vehicle software, "
        "whose E2E profiles protect messages",
    ),
    (
        r"\bCAL\d?\b",
        "CAL",
        "Cybersecurity assurance level, CAL1 (lowest) to CAL4 (highest), from ISO/SAE 21434: "
        "how much rigour a cybersecurity requirement needs",
    ),
    (
        r"\bCAN\b",
        "CAN, CAN FD",
        "Controller Area Network, and its flexible data-rate version: the common vehicle " "bus",
    ),
    (r"\bCC-\d", "CC", "Cybersecurity claim identifier, as in CC-01 (WP-C-10)"),
    (r"\bCG-\d", "CG", "Cybersecurity goal identifier, as in CG-01 (WP-C-10)"),
    (
        r"\bCI\b",
        "CI",
        "Continuous integration: the automated checks GitHub runs on every pull request and push",
    ),
    (
        r"\bCK-\d",
        "CK",
        "Clock identifier, as in CK-01: a time source that signals are stamped against (WP-S-05)",
    ),
    (
        r"\bCMP-\d",
        "CMP",
        "Component identifier, as in CMP-02: a part of the system architecture (WP-S-03)",
    ),
    (r"\bCR-\d", "CR", "Cybersecurity control identifier from the TARA, as in CR-01 (WP-C-09)"),
    (r"\bCSR-\d", "CSR", "Cybersecurity requirement identifier, as in CSR-01 (WP-C-10)"),
    (
        r"\bCSTR-\d",
        "CSTR",
        "Technical cybersecurity requirement identifier, as in CSTR-01.01 (WP-S-07)",
    ),
    (
        r"\b[CES][0-4]\b",
        "C0–C3, E0–E4, S0–S3",
        "HARA ratings: controllability, exposure and severity classes of a hazardous event; higher is worse",
    ),
    (
        r"\bDDT\b",
        "DDT",
        "Dynamic driving task: steering, braking, accelerating and watching the road",
    ),
    (
        r"\bDFA\b",
        "DFA",
        "Dependent failure analysis: one cause that could defeat several safety measures at once",
    ),
    (
        r"\bDIA\b",
        "DIA",
        "Development interface agreement: who does which safety work, between this project and a "
        "supplier",
    ),
    (
        r"\bDQ-\d",
        "DQ",
        'A question in the decision register, as in DQ-004. "DQ-015 B" means option B',
    ),
    (
        r"\bE2E\b",
        "E2E",
        "End-to-end protection: a checksum, counter and timeout on each message, checked by the "
        "receiver",
    ),
    (r"\bECC\b", "ECC", "Error-correcting code: memory that detects and corrects bit errors"),
    (r"\bEL-\d", "EL", "Element of the functional safety concept, as in EL-02 (WP-C-04)"),
    (
        r"\bEX-\d",
        "EX",
        "External interface identifier, as in EX-05: a way into the vehicle from outside (WP-S-07)",
    ),
    (r"\bFI-\d", "FI", "Functional insufficiency identifier, as in FI-01 (WP-C-06)"),
    (r"\bFM-\d", "FM", "Functional modification identifier, as in FM-01 (WP-C-07)"),
    (
        r"\bFMEA\b",
        "FMEA",
        "Failure mode and effects analysis: how each part can fail and what follows",
    ),
    (
        r"\bFMEDA\b",
        "FMEDA",
        "Failure modes, effects and diagnostic analysis: an FMEA that also counts how many "
        "failures the diagnostics catch",
    ),
    (r"\bFSCs?\b", "FSC", "Functional safety concept: how the safety goals are met"),
    (r"\bFSRs?\b", "FSR", "Functional safety requirement, as in FSR-08.01 (WP-C-04)"),
    (
        r"\bFTA\b",
        "FTA",
        "Fault tree analysis: from a harmful event back to the faults that cause it",
    ),
    (
        r"\bFTTIs?\b",
        "FTTI",
        "Fault tolerant time interval: how long a fault can last before it can lead to harm",
    ),
    (r"\bF-\d", "F", "Function of the item identifier, as in F-01 (WP-C-01)"),
    (r"\bG\d\b", "G0 to G6", "Gates: project milestones with exit criteria, defined in WP-M-00 §2"),
    (
        r"\bGNSS\b",
        "GNSS",
        "Global navigation satellite system, such as GPS; here also a source of exact time",
    ),
    (
        r"\bHARA\b",
        "HARA",
        "Hazard analysis and risk assessment: finds the hazards and sets the safety goals",
    ),
    (
        r"\bHD map\b",
        "HD map",
        "High-definition map: the detailed lane-level map Autoware drives from",
    ),
    (r"\bHD-\d", "HD", "Hardware diagnostic identifier, as in HD-01 (WP-S-05)"),
    (
        r"\bHE-\d",
        "HE",
        "Hazardous event identifier: a hazard in one operational situation, as in HE-01.1",
    ),
    (r"\bH-\d", "H", "Hazard identifier, as in H-01 (WP-C-03)"),
    (
        r"\bHIL\b",
        "HIL",
        "Hardware in the loop: testing the real controller against a simulated vehicle",
    ),
    (r"\bHSI\b", "HSI", "Hardware–software interface"),
    (
        r"\bI[0-3]\b",
        "I0 to I3",
        "Independence of a reviewer from the author, from none (I0) to an independent "
        "assessor (I3). Work drafted by the AI assistant is I0",
    ),
    (r"\bI-\d", "I", "Interface of the item identifier, as in I-08 (WP-C-01)"),
    (r"\bIDs?\b", "ID", "Identifier"),
    (
        r"\bIEEE\b",
        "IEEE",
        "Institute of Electrical and Electronics Engineers, which publishes standards such as "
        "IEEE 802.1AS (network time) and IEEE 2846 (driving behaviour assumptions)",
    ),
    (
        r"\bIF-\d",
        "IF",
        "Interface identifier of the hardware–software interface, as in IF-01 (WP-S-05)",
    ),
    (r"\bISO\b", "ISO", "International Organization for Standardization"),
    (
        r"\bLFM\b",
        "LFM",
        "Latent fault metric: the share of latent (hidden) faults the design detects (ISO 26262-5)",
    ),
    (
        r"\bM\d\d\b",
        "M01 to M14",
        'HARA guide words: the ways a function can malfunction, such as M01 "no ' 'function"',
    ),
    (r"\bML\b", "ML", "Machine learning"),
    (r"\bMON-\d", "MON", "ODD monitoring function identifier, as in MON-04 (WP-C-02)"),
    (
        r"\bMRCs?\b",
        "MRC",
        "Minimal risk condition: a stable, stopped state the vehicle reaches by itself",
    ),
    (
        r"\bMRMs?\b",
        "MRM",
        "Minimal risk manoeuvre: the manoeuvre that brings the vehicle to a minimal risk "
        "condition",
    ),
    (
        r"\bODD\b",
        "ODD",
        "Operational design domain: the roads, conditions and traffic the system is designed for",
    ),
    (r"\bOEDR\b", "OEDR", "Object and event detection and response"),
    (r"\bOIs?\b", "OI", "Open item: a known gap recorded in a document, numbered per document"),
    (
        r"\bOS-\d",
        "OS (in OS-01)",
        "Operational situation identifier: a driving situation the HARA rates " "hazards in",
    ),
    (r"\bOS\b(?!-)", "OS", "Operating system"),
    (r"\bP-\d", "P", "Safety envelope parameter identifier, as in P-01 (WP-S-02)"),
    (
        r"\bPMHF\b",
        "PMHF",
        "Probabilistic metric for random hardware failures: the rate at which hardware faults "
        "could violate a safety goal (ISO 26262-5)",
    ),
    (
        r"\bQM\b",
        "QM",
        "Quality management: no ASIL is needed, ordinary quality processes are enough",
    ),
    (r"\bRAM\b", "RAM", "Random-access memory: a computer's working memory"),
    (
        r"\bRD-\d",
        "RD",
        "Redundancy identifier, as in RD-01: a pair of channels that cover each other (WP-S-03)",
    ),
    (
        r"\bREMOTE\b",
        "REMOTE",
        "The operating mode in which a remote operator drives the vehicle (WP-C-01)",
    ),
    (r"\bROS\b", "ROS 2", "Robot Operating System 2: the middleware Autoware is built on"),
    (r"\bSAE\b", "SAE", "SAE International, formerly the Society of Automotive Engineers"),
    (r"\bSGs?\b", "SG", "Safety goal: a top-level safety requirement from the HARA, as in SG-01"),
    (r"\bSH-\d", "SH", "SOTIF hazard identifier, as in SH-01 (WP-C-05)"),
    (
        r"\bSIG-\d",
        "SIG",
        "Signal identifier, as in SIG-01: one message that crosses an interface (WP-S-05)",
    ),
    (
        r"\| (?:Skeleton|Draft|In review|Approved|Baselined) \|",
        "Skeleton, Draft, In review, Approved, Baselined",
        "Status of a work product: structure only; written, not verified; in verification review; approved; "
        "approved and frozen",
    ),
    (r"\bSM-\d", "SM", "Safety mechanism identifier, as in SM-01 (WP-S-03)"),
    (
        r"\bSOTIF\b",
        "SOTIF",
        "Safety of the intended functionality (ISO 21448): harm from a function working as "
        "designed but not well enough",
    ),
    (
        r"\bSPFM\b",
        "SPFM",
        "Single-point fault metric: the share of single-point faults the design covers "
        "(ISO 26262-5)",
    ),
    (
        r"\bSTPA\b",
        "STPA",
        "System-theoretic process analysis: hazards from unsafe control actions and "
        "interactions",
    ),
    (
        r"\bSZ-\d",
        "SZ",
        "Security zone identifier, as in SZ-1: a part of the system with one level of trust "
        "(WP-S-07)",
    ),
    (r"\bTARA\b", "TARA", "Threat analysis and risk assessment (ISO/SAE 21434)"),
    (r"\bTC-\d", "TC", "Triggering condition identifier, as in TC-12 (WP-C-06)"),
    (
        r"\bTR-\d",
        "TR",
        "Fallback trigger identifier, as in TR-01: a condition that starts a minimal risk "
        "manoeuvre (WP-C-12)",
    ),
    (r"\bTS-\d", "TS", "Threat scenario identifier, as in TS-01 (WP-C-09)"),
    (r"\bTSRs?\b", "TSR", "Technical safety requirement, as in TSR-01.01 (WP-S-02)"),
    (
        r"\bUL\b",
        "UL 4600",
        "The standard for the safety of autonomous products; the main framework here",
    ),
    (
        r"\bW\d\d\b",
        "W01 to W06",
        'HARA road and light conditions, such as W01 "dry road in daylight"',
    ),
    (r"\bWBS\b", "WBS", "Work breakdown structure: the project's work split into tasks"),
    (
        r"\bWP-",
        "WP",
        "Work product: a document or record the assurance path needs. WP-M-00 is the register "
        "that lists them all",
    ),
    (
        r"\bYAML\b|\.yaml\b",
        "YAML",
        "A plain-text data format; the generator's source data is a `.yaml` file",
    ),
    (r"\bENV-\d", "ENV", "Test environment identifier, as in ENV-1 (WP-S-08)"),
    (r"\bIS-\d", "IS", "Integration step identifier, as in IS-1 (WP-S-08)"),
    (r"\bIT-\d", "IT", "Integration test case identifier, as in IT-01 (WP-S-08)"),
    (r"\bSIM-\d", "SIM", "Simulator identifier, as in SIM-01 (WP-V-08)"),
    (r"§", "§", 'Section or clause, as in "UL 4600 §5"'),
    (r"\d–\d", "– (en dash) in a range", '"through", as in "§5–8" (clauses 5 to 8)'),
    (r"\d/\d", "/ between numbers", '"and", as in "MAN.3/5" (MAN.3 and MAN.5)'),
    (r"→", "→", "From one component to another, or leads to"),
    (r"\| — \|", "—", "Nothing: no value, or the subfolder has no README of its own"),
]
# Capitalised words that are not abbreviations needing a definition.
NOT_ABBREVIATIONS = {"README", "TBD"}


def close(md: str, path: Path) -> str:
    """The page with its closing table, for a README written at `path`."""
    text = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    text = "\n".join(ln if ln.startswith("|") else fk.plain(ln) for ln in text.splitlines())
    text = re.sub(r"\]\([^)]*\)", "]", text)
    found = [(t, m) for pat, t, m in TERMS if re.search(pat, text)]
    for tok in sorted(set(re.findall(r"\b[A-Z][A-Z0-9]+s?\b", text)) - NOT_ABBREVIATIONS):
        if re.fullmatch(r"[A-Z]\d+|[A-Z]{2,}\d+", tok) and any(
            re.search(p, tok) for p, _, _ in TERMS
        ):
            continue
        if not any(tok.rstrip("s") in re.split(r"[ ,()]+", t) for t, _ in found):
            raise fk.FigureError(
                f"{path.name} in {path.parent.name}/ uses {tok}, which terms.py does not define"
            )
    words = sorted((x for x in found if x[0][0].isalnum()), key=lambda x: x[0].lower())
    found = words + [x for x in found if not x[0][0].isalnum()]
    link = f"[Glossary]({Path(os.path.relpath(GLOSSARY, path.parent)).as_posix()})"
    out = [md.rstrip("\n"), "", HEADING, ""]
    if not found:
        return "\n".join(out + [f"This page uses none. Terms are defined in the {link}.", ""])
    out += ["| Term | Meaning |", "|---|---|"] + [f"| {t} | {m} |" for t, m in found]
    return "\n".join(out + ["", f"Other terms are defined in the {link}.", ""])
