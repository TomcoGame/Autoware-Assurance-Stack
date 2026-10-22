# WP-M-01 Assurance Strategy and Lifecycle Tailoring

| Field | Value |
|---|---|
| Work product | WP-M-01 Assurance strategy and lifecycle tailoring |
| Standard reference | UL 4600 §5, §17; ISO 26262-2:2018 §6 (tailoring, safety plan inputs); ISO 21448:2022 §4; ISO/SAE 21434:2021 §6; ISO/PAS 8800:2024 (AI safety management); ASPICE 4.0 MAN.3 |
| Version | 0.1 (first issue: starting point, how the standards fit, the open strategic decisions; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All (FuSa, SOTIF, CS, AI, process) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1); confirmation of the tailoring rationale by the independent assessor (I3) |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

This is the assurance path for a driverless system built on Autoware. It says what the project will claim and for which configuration, how the standards are combined, where they are tailored and why, and which strategic decisions the safety authority must take before the hazard analysis starts. The plans for each discipline ([WP-M-02](WP-M-02-safety-plan.md), [WP-M-08](WP-M-08-sotif-plan.md), [WP-M-09](WP-M-09-cybersecurity-plan.md), [WP-M-10](WP-M-10-ai-safety-plan.md)) carry it out; the [register (WP-M-00)](WP-M-00-work-product-register.md) lists every output.

## 2. Starting point

- The repository is an unmodified fork of `autowarefoundation/autoware` at `ed48f39`. That repository holds no driving code: it pins the source repositories in [`repositories/autoware.repos`](../../repositories/autoware.repos) (for example `autoware_core` 1.9.0 and `autoware_universe` 0.52.1) and the Ansible and Docker tooling that builds them.
- Autoware was not developed to ISO 26262, ISO 21448 or UL 4600, and carries no safety case. Its packages are open-source elements that this project must argue for (ISO 26262-8 §12 and §16, UL 4600 §13; [WP-P-08](../07-supporting/WP-P-08-software-component-qualification.md)).
- Autoware already contains functions that a safety concept can build on, though none is assured: `autoware_vehicle_cmd_gate` selects between the autonomous, external and emergency commands, filters them against limits and watches heartbeats; `autoware_mrm_handler` with the comfortable-stop and emergency-stop operators carries out minimal risk manoeuvres; `autoware_diagnostic_graph_aggregator` decides which operation modes are available; `autoware_control_validator` and `autoware_planning_validator` check outputs before they are used (all in `autoware_universe` 0.52.1).
- All of these run on the same computer, operating system and middleware as the functions they check. This shared platform is the central question for the safety architecture (§6).
- Perception and prediction rely on machine-learning models trained by third parties, on data this project does not hold.

## 3. What the project will claim

### 3.1 Reference configuration

Claims apply to one reference configuration only. Every row below waits on a decision of the safety authority.

| Element | Reference configuration | Decided by |
|---|---|---|
| Item and function | TBD | Decision register DQ-001 |
| ODD | TBD, specified in [WP-C-02](../02-concept/WP-C-02-odd-and-intended-functionality.md) | DQ-001 |
| Command-bounding element | TBD | DQ-002 |
| Vehicle and drive-by-wire | TBD, recorded in [WP-C-01](../02-concept/WP-C-01-item-definition.md) | DQ-003 |
| Software | A tagged release of this repository that pins every source repository, map and model weight by commit or digest | [WP-P-01](../07-supporting/WP-P-01-configuration-management-plan.md) |
| Operation | Driverless in the ODD, with a remote operations centre; during development, trained safety drivers ([WP-V-07](../06-validation/WP-V-07-test-operations.md)) | DQ-001 |

### 3.2 Top-level claim (proposed)

> **G0**: The reference configuration, operating without a driver inside its ODD, is acceptably safe: its risk to passengers and other road users is no greater than the acceptance criterion set by the safety authority, including when it fails, when it leaves its ODD and when it meets situations it was not designed for.

The acceptance criterion (for example a positive risk balance against a stated human-driven baseline) is a decision for the safety authority and is set with the SOTIF acceptance criteria ([WP-C-05](../02-concept/WP-C-05-sotif-hazard-identification.md)).

## 4. How the standards fit together

**Why UL 4600 is the main framework.** ISO 26262 and ISO 21448 were written for vehicles with a driver, or with a driver who can be asked to take over. Here no one takes over: the vehicle must detect its own failures and its own performance limits, and reach a minimal risk condition by itself. UL 4600 is written for exactly that case. It does not prescribe how to engineer the system; it requires a safety case that argues safety across the whole ODD and lifecycle, and it accepts the other standards as the means to produce the evidence.

| Standard | Role in this project | Main outputs |
|---|---|---|
| UL 4600 | Structure of the safety case; scope of what it must cover (ODD, fallback, humans, data, tools, operation, SPIs); independent assessment | WP-K-01, WP-K-07, WP-O-06 |
| ISO 26262 | Method for the risk from malfunctions: HARA, safety goals, ASILs, safety concepts, hardware metrics | WP-C-03, WP-C-04, WP-S-02 to WP-S-05, 04-hardware, 05-software |
| ISO 21448 | Method for the risk from insufficiencies of the intended function: perception limits, triggering conditions, validation targets | WP-C-05 to WP-C-07, WP-V-02 to WP-V-04 |
| ISO/SAE 21434 | Cybersecurity, including the remote operations link and over-the-air updates of software, maps and models | WP-M-09, WP-C-09, WP-C-10, WP-S-07 |
| ISO/PAS 8800 | Safety of the machine-learning components and their data | WP-M-10, WP-C-11, WP-W-10 |
| Automotive SPICE 4.0 | Capability of the engineering and support processes | WP-M-13 |

**Controllability with no driver.** ISO 26262 rates controllability by the driver or others at risk. With no driver, controllability by the occupants is C3 unless an argument shows otherwise; controllability by other road users can be credited only where it is reasonable. WP-C-03 states the rule it uses.

## 5. Tailoring

No tailoring is proposed yet. Candidates, each to be decided with its rationale once the item is fixed:

| Candidate | Why it may apply |
|---|---|
| ISO 26262 scope for a low-speed purpose-built vehicle | ISO 26262 covers series-production road vehicles; some shuttles fall outside it (see WP-M-00 §5). The project applies it as a method either way |
| ISO 26262-5 metrics for bought-in compute and sensors | Supplier failure-rate data may not exist; WP-H-07 evaluation may replace parts of the metrics |
| ASPICE capability targets | Target levels per process are set in WP-M-13 |

## 6. Safety architecture argument

The argument depends on where the commands to the vehicle are bounded, and by what (decision register DQ-002). Three patterns are possible:

1. **Independent safety monitor.** A separate controller, on its own hardware between Autoware and the drive-by-wire system, checks every command against a safety envelope and can bring the vehicle to a stop on its own when Autoware fails or goes silent. Autoware stays QM for malfunctions; its nominal performance is argued under ISO 21448 and UL 4600.
2. **`vehicle_cmd_gate` rated for safety.** The existing gate is developed or qualified to an ASIL. It shares compute, operating system and middleware with the functions it bounds, so the dependent-failure argument (ISO 26262-9 §7) and freedom from interference on Linux and ROS 2 carry the case.
3. **The drive-by-wire platform as the bound.** The vehicle's own by-wire controllers enforce limits and a watchdog stop; Autoware and the gate stay QM. The case then rests on the supplier's safety evidence.

The recommendation, and its costs, are in the decision register entry. The choice shapes the HARA allocation, the hardware (WP-H-02), the FTTI budget (WP-S-04) and the fallback concept (WP-C-12), so the hazard analysis does not start before it.

## 7. Phases and gates

The gates G0 to G6 and their exit criteria are in [WP-M-00 §2](WP-M-00-work-product-register.md#2-gates). G0 needs the decisions in §8 and the plans; G1 closes the concept, including the HARA confirmation review by the assessor.

## 8. Strategic decisions required

The open questions live in the [decision register](decisions/README.md). Those this strategy waits on:

| Question | Register |
|---|---|
| Which item and ODD to assure | DQ-001 |
| What bounds the commands: a separate safety monitor, or `vehicle_cmd_gate` rated for safety | DQ-002 |
| Which vehicle and drive-by-wire platform | DQ-003 |
| Who is the safety authority, and who assesses | DQ-004 |

Once applied, each decision is recorded here and in the work product that owns it.

## 9. AI-authored work

Much of the drafting is done by an AI assistant. Its output is a draft at independence level I0: it is never marked Approved by its author, it never accepts its own evidence, and a human reviewer at the level WP-M-06 requires verifies it before it counts.

## 10. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Fill §3.1 and §3.2 from DQ-001 to DQ-003 and the acceptance criterion | G0 |
| OI-2 | Choose the safety architecture pattern of §6 (DQ-002) and record its rationale | G0 |
| OI-3 | Decide the tailoring candidates of §5 | G1 |
