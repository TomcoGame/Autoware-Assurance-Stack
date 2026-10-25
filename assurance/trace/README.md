# WP-T-01 Requirements and Trace Data

| Field | Value |
|---|---|
| Work product | WP-T-01 Requirements and trace data (machine-readable), consistency evidence |
| Standard reference | UL 4600 §5, §9; ISO 26262-8 §6; ISO/SAE 21434 §10; ASPICE 4.0 SYS.2–5, SWE.1–6 (traceability) |
| Version | 0.1 (skeleton: the checks on the tree exist, trace data does not yet; 2026-10-22) |
| Status | Skeleton |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

This folder will hold the requirements (safety goals down to software and hardware safety requirements) and their
trace links as data, so that consistency is checked by a program rather than by reading. Until the hazard analysis
starts there are no requirements to trace; the folder holds the checks that already run on the whole assurance tree.

## 2. Checks on the tree

| Check (run this) | What it refuses |
|---|---|
| `python3 assurance/trace/tools/check_links.py` | A relative link or `#anchor` in the tree that does not resolve |
| `python3 assurance/trace/tools/check_tables.py` | A table row whose cell count differs from its header |
| `python3 assurance/trace/tools/check_restricted.py` | Restricted cybersecurity information in any tracked file: a file marked `classification: restricted` or named as restricted, key material, a table with an attack path, feasibility, risk value or attack vector column ([WP-M-09 §4](../01-management/WP-M-09-cybersecurity-plan.md#4-handling-of-cybersecurity-information)) |
| `python3 assurance/trace/tools/check_headers.py` | A work product without the full document control header, whose `Status` disagrees with WP-M-00, or that is missing from WP-M-00 |

Each has unit tests in [`assurance/tests/`](../tests/) and runs in the [assurance workflow](../../.github/workflows/assurance.yaml).

## 3. Trace data

To be written with the HARA: item schema, link types (derives, allocates, verifies, mitigates) and the consistency
rules of [WP-P-06](../07-supporting/WP-P-06-requirements-management-traceability.md).

## 4. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Define the trace data schema and its checks before the first safety goal is written | G1 |

## 5. Abbreviations, terms and symbols

| Term | Meaning |
|---|---|
| AI | Artificial intelligence; here the AI assistant that drafted this page |
| ASIL | Automotive Safety Integrity Level, A (lowest) to D (highest), from ISO 26262. "All" in the header means every level |
| ASPICE 4.0, SYS, SWE | Automotive SPICE version 4.0, a process capability model; SYS and SWE are its system and software engineering processes ("SYS.2–5" means processes 2 to 5) |
| CI | Continuous integration: the automated checks GitHub runs on every pull request and push |
| DQ | A question in the [decision register](../01-management/decisions/README.md), as in DQ-004 |
| G1 | Gate 1, the concept milestone ([WP-M-00 §2](../01-management/WP-M-00-work-product-register.md#2-gates)) |
| HARA | Hazard analysis and risk assessment: finds the hazards and sets the safety goals |
| I0 | Independence level 0: drafted with no independent review |
| ID, OI | Identifier; open item, a known gap numbered per document |
| ISO, ISO/SAE, UL | The standards bodies behind ISO 26262, ISO/SAE 21434 and UL 4600 |
| TBD | To be decided |
| Trace link | A recorded relation between two requirements or a requirement and a test (derives, allocates, verifies, mitigates) |
| WP | Work product, as in WP-T-01 |
| `ed48f39` | The short Git commit hash of upstream Autoware this work refers to |
| `#anchor` | The part of a link after `#` that points to a heading inside a page |
| § | Section or clause, as in "ISO 26262-8 §6" (part 8, clause 6) |

Other terms are defined in the [Glossary](../../wiki/Glossary.md).
