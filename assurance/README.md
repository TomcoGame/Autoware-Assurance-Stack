# Autoware Assurance Stack

This tree holds the assurance work products for a driverless system built on Autoware: the safety case
(UL 4600), functional safety (ISO 26262:2018), SOTIF (ISO 21448:2022), cybersecurity (ISO/SAE 21434:2021),
AI safety (ISO/PAS 8800:2024) and process capability (Automotive SPICE 4.0).

UL 4600 is the main framework. There is no driver to fall back on, so the vehicle has to detect its own
failures and limits and reach a minimal risk condition by itself, and the safety case has to argue that
across the whole operational design domain. The other standards supply the methods and the evidence
([WP-M-01 §4](01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together)).

> [!WARNING]
> Everything here is a **draft prepared for engineering review**. Nothing has passed verification review,
> confirmation review or assessment. A document existing here does not mean the activity behind it is done.
> Read the `Status` field of each work product and the [register (WP-M-00)](01-management/WP-M-00-work-product-register.md).

## Status

![Assurance dashboard: work products by status and gate, decisions waiting on the safety authority, and the safety case records. The same values are listed as text below.](case/figures/dashboard.svg)

*Generated from the WP-M-00 register, the decision register and the safety case records by
[`case/tools/dashboard.py`](case/tools/dashboard.py); CI fails if it is stale. Nothing on it is typed by hand.*

<details>
<summary><b>The same values as text</b></summary>

<!-- BEGIN GENERATED: assurance-summary (assurance/case/tools/dashboard.py) -->

| Indicator | Value |
|---|---|
| Assurance state | Before G0: hazard analysis draft |
| Work products in the register | 91 (15 draft, 76 skeleton) |
| Work products approved or baselined | 0 |
| Decisions waiting on the safety authority | 0 open |
| Decisions applied | 24 |
| Safety case claims | 0 |
| Evidence items | 0 |
| Open defeaters | 0 |

<!-- END GENERATED: assurance-summary -->

</details>

## Start here

| Document | Why read it |
|---|---|
| [01-management/WP-M-01-assurance-strategy.md](01-management/WP-M-01-assurance-strategy.md) | The assurance path: what will be claimed, how the standards fit, the decisions it waits on |
| [01-management/WP-M-00-work-product-register.md](01-management/WP-M-00-work-product-register.md) | Every work product, its clauses, gate and status |
| [01-management/decisions/README.md](01-management/decisions/README.md) | The questions waiting on the safety authority, and how they are asked and answered |
| [case/README.md](case/README.md) | How the safety case records and the dashboard work |

## Layout

| Folder | Content | Primary standard clauses |
|---|---|---|
| `00-assessment/` | Baseline gap assessment of upstream Autoware against the target standards | n/a |
| `01-management/` | Plans, safety management, upstream and supplier management, the [decision register](01-management/decisions/README.md) | UL 4600 §5, §17; 26262-2; 21448 §4; 21434 §5–8; MAN.3/5, ACQ.4 |
| `02-concept/` | Item definition, ODD, HARA, FSC, fallback and minimal risk concept, SOTIF hazards and insufficiencies, TARA, AI safety requirements | UL 4600 §6–8; 26262-3; 21448 §5–8; 21434 §9, §15; PAS 8800 |
| `03-system/` | Technical safety requirements and concept, system architecture, timing, HSI, system integration and verification | UL 4600 §9–10; 26262-4; SYS.1–5 |
| `04-hardware/` | Hardware safety requirements, design, metrics, evaluation of bought-in elements | 26262-5; 26262-8 §13; HWE.1–4 |
| `05-software/` | Software requirements, architecture, units, verification, ML engineering, calibration and HD map data | UL 4600 §9, §11; 26262-6; SWE.1–6; MLE.1–4 |
| `06-validation/` | Safety validation, SOTIF scenario evaluation, fault injection, penetration testing, test operations, simulation credibility | UL 4600 §12; 26262-4 §8; 21448 §9–11; 21434 §11; VAL.1 |
| `07-supporting/` | Configuration, change, problems, documentation, reviews, traceability, tool and software-component qualification | UL 4600 §13–14; 26262-8; SUP.1/8/9/10 |
| `08-analyses/` | ASIL decomposition, freedom from interference, DFA, system FTA and FMEA, STPA | UL 4600 §6, §10; 26262-9 |
| `09-production-operation/` | Production, fleet operation, user information, field monitoring, incident response, safety performance indicators | UL 4600 §14–16; 26262-7; 21448 §13; 21434 §12–14 |
| `10-safety-case/` | Safety, SOTIF and cybersecurity cases; assessment and release records | UL 4600 §5, §17; 26262-2 §6; 21448 §12; 21434 §6 |
| `case/` | [Safety case records](case/README.md) (claims, evidence, defeaters) and the dashboard generator | UL 4600 §5 |
| `trace/` | Machine-readable requirement and trace data, and the checks on the whole tree | 26262-8 §6; ASPICE traceability |

Each numbered folder has a README page generated from this table and the register
([`folder_index.py`](01-management/figures/folder_index.py)).

## Conventions

### Identifiers

| Prefix | Meaning | Example |
|---|---|---|
| `WP-<area>-<nn>` | Work product; areas M, C, S, H, W, V, P, A, O, K, T follow the folders | `WP-C-03` |
| `DQ-<nnn>` | Question in the decision register | `DQ-002` |
| `H-<nn>` / `HE-<nn>.<n>` / `SG-<nn>` | Hazard / hazardous event / safety goal | `SG-01` |
| `FSR-<nn>.<nn>` / `TSR-<nnn>` | Functional / technical safety requirement | `TSR-014` |
| `SWSR-<nnn>` / `HWSR-<nnn>` | Software / hardware safety requirement | `SWSR-031` |
| `SH-<nn>` / `FI-<nn>` / `TC-<nn>` / `FM-<nn>` | SOTIF hazard / functional insufficiency / triggering condition / functional modification | `TC-12` |
| `MRM-<nn>` / `MRC-<nn>` | Minimal risk manoeuvre / minimal risk condition | `MRM-02` |
| `TS-<nn>` / `CSG-<nn>` / `CSR-<nn>` | Threat scenario / cybersecurity goal / cybersecurity requirement | `CSG-02` |
| `AOU-<nn>` | Assumption (on the vehicle, infrastructure, people or environment) | `AOU-05` |
| `SPI-<nn>` | Safety performance indicator | `SPI-03` |
| `CL-<nnn>` / `EV-<nnn>` / `DF-<nnn>` | Safety case claim / evidence item / defeater | `CL-001` |
| `OI-<n>` | Open item, numbered per document | `OI-3` |

Identifiers are never reused. A withdrawn item keeps its identifier and is marked `Withdrawn`.

### Document control header

Every work product starts with this table, checked by [`check_headers.py`](trace/tools/check_headers.py):

```text
| Field | Value |
|---|---|
| Work product | WP-x-nn <name> |
| Standard reference | <clause list> |
| Version | <n.m> (<what changed>; <date>) |
| Status | Skeleton / Draft / In review / Approved / Baselined |
| ASIL / scope | <highest ASIL addressed, or QM / SOTIF / CS / AI / All> |
| Author | <name> |
| Reviewer(s) | <name, independence level I0–I3> |
| Approver | <name> |
| Baseline | <commit or tag the content refers to> |
```

### Status meanings

| Status | Meaning |
|---|---|
| Skeleton | Structure and clause mapping exist; content still to be written |
| Draft | Content written; not yet verified |
| In review | Verification review open (pull request) |
| Approved | Verification review passed and approved by the approver named in the safety plan |
| Baselined | Approved and frozen in a tagged baseline |

The `Status` of a work product and its row in WP-M-00 must agree; `check_headers.py` fails otherwise.

### Generated content

Every figure, index page and generated block in this tree comes from a generator, and CI runs each one with
`--check`: if the committed output differs from what the generator makes from the current sources, the
[assurance workflow](../.github/workflows/assurance.yaml) fails. To fix it, run the generator without `--check`
and commit the result.

| Generator (run this) | Writes | Reads |
|---|---|---|
| `python3 assurance/01-management/figures/fig_m00_register.py` | WP-M-00 Figure 3-1 | WP-M-00 §2, §3 |
| `python3 assurance/01-management/figures/folder_index.py` | `README.md` and `index-status.svg` of each numbered folder | This page's Layout table, WP-M-00 §3 |
| `python3 assurance/01-management/decisions/fig_lifecycle.py` | Decision register Figure 1 | The status table of `decisions/README.md` |
| `python3 assurance/01-management/decisions/fig_questions.py` | The figures of decision register entries | Its own option data, checked against `register.yaml` |
| `python3 assurance/02-concept/figures/fig_c01_boundary.py` | WP-C-01 Figure 5-1 | WP-C-01 §3, §5.1, §5.2 |
| `python3 assurance/02-concept/hara/hara.py` | WP-C-03 §1 summary, §4 to §7 tables and Figure 6-1 (every ASIL computed) | `02-concept/hara/hara.yaml` |
| `python3 assurance/02-concept/fsc/fsc.py` | WP-C-04 §1 summary, §3 to §5 tables and Figure 4-1 (element ASILs derived) | `02-concept/fsc/fsc.yaml`, `hara/hara.yaml`, WP-C-01 §8, the decision register |
| `python3 assurance/02-concept/sotif/sotif.py` | WP-C-05 §1 summary, §4 to §6 tables and Figure 4-1 | `02-concept/sotif/sotif.yaml`, WP-C-01 §3, `hara/hara.yaml` |
| `python3 assurance/02-concept/fallback/fallback.py` | WP-C-12 §1 summary, §2 to §4 and §6 tables, Figure 3-1 | `02-concept/fallback/fallback.yaml`, `fsc/fsc.yaml`, `hara/hara.yaml`, `sotif/sotif.yaml`, WP-C-01 §8, WP-C-02 §3 and §4, decision register |
| `python3 assurance/02-concept/triggering/triggering.py` | WP-C-06 §1 summary, §3 to §6 tables and Figure 5-1 | `02-concept/triggering/triggering.yaml`, `sotif/sotif.yaml`, WP-C-01 §3, WP-C-02 §3 and §4 |
| `python3 assurance/02-concept/modifications/modifications.py` | WP-C-07 §1 summary, §2 and §5 tables, Figure 2-1 | `02-concept/modifications/modifications.yaml`, `triggering/triggering.yaml`, `fsc/fsc.yaml`, WP-C-01 §8, WP-C-02 §4, decision register |
| `python3 assurance/08-analyses/stpa/stpa.py` | WP-A-05 §1 summary, §2 to §6 tables and Figure 3-1 | `08-analyses/stpa/stpa.yaml`, `hara/hara.yaml`, `sotif/sotif.yaml`, `fsc/fsc.yaml`, `fallback/fallback.yaml`, `modifications/modifications.yaml` |
| `python3 assurance/02-concept/tara/tara.py` | WP-C-09 §1 summary, §2 to §5 tables and Figure 5-1 | `02-concept/tara/tara.yaml`, `stpa/stpa.yaml` and the references it checks, decision register |
| `python3 assurance/02-concept/cybersecurity/cybersecurity.py` | WP-C-10 §1 summary, §2 to §4 tables and Figure 2-1 | `02-concept/cybersecurity/cybersecurity.yaml`, `tara/tara.yaml` and the references it checks |
| `python3 assurance/02-concept/ai/ai.py` | WP-C-11 §1 summary, §2 to §5 tables and Figure 4-1 | `02-concept/ai/ai.yaml`, WP-C-01 §3, WP-C-02 §6, `fsc/fsc.yaml`, `triggering/triggering.yaml`, `cybersecurity/cybersecurity.yaml` |
| `python3 assurance/02-concept/misuse/misuse.py` | WP-C-08 §1 summary, §2 and §4 to §6 tables, Figure 5-1 | `02-concept/misuse/misuse.yaml` and the analyses it refers to, decision register |
| `python3 assurance/case/tools/dashboard.py` | `case/figures/dashboard.svg`, the summary block above | WP-M-00, `register.yaml`, `case/records/` |

The decision inbox page is built by `decisions/build_inbox.py` and published outside the repository; CI builds it
to prove it still builds.

### Standards text

The standards are copyrighted and are not reproduced here. Clause references point to the editions named above
(UL 4600 3rd edition); ISO/PAS 8800 is cited by topic. Check each clause number against a licensed copy before an
audit ([WP-M-00](01-management/WP-M-00-work-product-register.md) OI-1).

### Who decides

Questions only the safety authority can answer (risk acceptance, ASIL and hazard scope, ODD limits, vehicle
behaviour defaults, money and hardware, roles and the assessor, gate go/no-go) go to the
[decision register](01-management/decisions/README.md). Work authored by an AI assistant is a draft at
independence level I0 and needs human review before it counts.
