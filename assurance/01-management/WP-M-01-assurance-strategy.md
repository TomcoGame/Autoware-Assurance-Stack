# WP-M-01 Assurance Strategy and Lifecycle Tailoring

| Field | Value |
|---|---|
| Work product | WP-M-01 Assurance strategy and lifecycle tailoring |
| Standard reference | UL 4600 §5, §17; ISO 26262-2:2018 §6 (tailoring, safety plan inputs); ISO 21448:2022 §4; ISO/SAE 21434:2021 §6; ISO/PAS 8800:2024 (AI safety management); ASPICE 4.0 MAN.3 |
| Version | 0.5 (DQ-015 B, DQ-016 A; 2026-10-23). 0.4 (DQ-011 C, DQ-012 A, DQ-013 deferred; 2026-10-23). 0.3 (one US state (DQ-009 A), remote driving allowed (DQ-010 C); 2026-10-23). 0.2 (decisions of the lead, 2026-10-23: urban robotaxi ODD (DQ-001 B), independent safety monitor (DQ-002 A), vehicle chosen at G2 (DQ-003 C), safety authority and assessor deferred (DQ-004), hazard analysis may start (DQ-005 A); 2026-10-23). 0.1 (first issue; 2026-10-22) |
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

Claims apply to one reference configuration only. The rows below record the lead's decisions of 2026-10-23 (§8).

| Element | Reference configuration | Decided by |
|---|---|---|
| Item and function | Geofenced urban robotaxi: driverless passenger transport on public urban roads inside a mapped geofence | Decision register DQ-001 (B) |
| ODD | Public urban roads up to 50 km/h, day and night, dry weather and light rain, mixed traffic including pedestrians and cyclists; detailed in [WP-C-02](../02-concept/WP-C-02-odd-and-intended-functionality.md) | DQ-001 (B) |
| Command-bounding element | Independent safety monitor on its own hardware between Autoware and the drive-by-wire system (§6, pattern 1) | DQ-002 (A) |
| Vehicle and drive-by-wire | Chosen at G2. Until then the concept phase works against a generic vehicle model in Autoware's planning simulator and AWSIM, and every result that depends on the vehicle is marked provisional ([WP-C-01](../02-concept/WP-C-01-item-definition.md)) | DQ-003 (C) |
| Software | A tagged release of this repository that pins every source repository, map and model weight by commit or digest | [WP-P-01](../07-supporting/WP-P-01-configuration-management-plan.md) |
| Operation | Driverless in the ODD, with a remote operations centre; during development, trained safety drivers ([WP-V-07](../06-validation/WP-V-07-test-operations.md)) | DQ-001 (B) |

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

**Decided (DQ-002 A, 2026-10-23): pattern 1, an independent safety monitor.** The ASIL work is confined to the monitor and its interface to the drive-by-wire system; Autoware, including `vehicle_cmd_gate` and `mrm_handler`, stays QM for malfunctions and is argued under ISO 21448 and UL 4600 for its nominal performance. The monitor must be able to bring the vehicle to a minimal risk condition on its own when Autoware fails or goes silent ([WP-C-12](../02-concept/WP-C-12-fallback-and-minimal-risk-concept.md)), and its safety envelope must be simple enough to verify. This shapes the HARA allocation, the hardware (WP-H-02), the FTTI budget (WP-S-04) and the decomposition rationale (WP-A-01).

## 7. Phases and gates

The gates G0 to G6 and their exit criteria are in [WP-M-00 §2](WP-M-00-work-product-register.md#2-gates). G0 needs the decisions in §8 and the plans; G1 closes the concept, including the HARA confirmation review by the assessor.

## 8. Strategic decisions

Questions are asked and answered in the [decision register](decisions/README.md); the decisions are recorded here.

| Question | Decision (by the project lead, 2026-10-23) | Register |
|---|---|---|
| Which item and ODD to assure | B: geofenced urban robotaxi, public urban roads up to 50 km/h, day and night, light rain (§3.1) | DQ-001 |
| What bounds the commands | A: an independent safety monitor on its own hardware (§6) | DQ-002 |
| Which vehicle and drive-by-wire platform | C: decide at G2; work against a generic vehicle model in simulation until then (§3.1) | DQ-003 |
| Who is the safety authority, and who assesses | Deferred by the lead. Asked again before the HARA confirmation review (DQ-007); consequences in §9 | DQ-004 |
| May the hazard analysis start | A: start once DQ-001 to DQ-003 are answered, which they now are | DQ-005 |
| Where the robotaxi first operates | A: one US state; the state is asked next (DQ-013) | DQ-009 |
| May remote operators drive the vehicle | C: yes, remote driving in general, as well as assistance | DQ-010 |
| Unprotected turns and roundabouts | C: both inside the first ODD | DQ-011 |
| Weather and visibility limits | A: rain up to 2.5 mm/h, visibility of 200 m or more | DQ-012 |
| How much controllability the HARA may credit | B: none; C3 for every hazardous event | DQ-015 |
| Where the vehicle stops on its own | A: Autoware pulls over when it can; the rated minimal risk condition is a stop in lane | DQ-016 |
| Which US state | Deferred by the lead, leaning to the state where testing is easiest; analyses use common US rules until then; asked again before the HARA review (DQ-014) | DQ-013 |

**What the combination means.** An urban ODD at 50 km/h with pedestrians and cyclists gives the largest hazard space of the options, and the vehicle is not yet chosen. So the severity and exposure ratings can be drafted now, but the ratings that depend on the vehicle (mass, braking and steering capability, actuator redundancy) and everything downstream of them stay provisional until G2. The vehicle question returns at G2 (DQ-008).

**Scope.** With unprotected turns and roundabouts inside the ODD (DQ-011 C) and remote driving allowed, the first ODD is the widest of the options offered at each step. Gap acceptance against oncoming and circulating traffic, and the remote driving loop, are the largest new items in the hazard analysis and in validation.

**Remote driving (DQ-010 C)** puts the wireless link and the remote operator inside the control loop. The hazard analysis rates remote-driving situations, the TARA treats the link as a path to vehicle control, and the safety monitor bounds remote commands like any other, including their age (WP-C-02 MON-04).

## 9. AI-authored work

Much of the drafting is done by an AI assistant. Its output is a draft at independence level I0: it is never marked Approved by its author, it never accepts its own evidence, and a human reviewer at the level WP-M-06 requires verifies it before it counts.

**While DQ-004 is deferred** no approver is named, so no work product can move past Draft, and G0 cannot close. Drafting continues. The HARA confirmation review at G1 needs an independent assessor (I3), so DQ-007 must be answered before that review is scheduled.

## 10. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Set the acceptance criterion of §3.2 with the SOTIF acceptance criteria | G1 |
| OI-2 | Name the safety authority and the assessor (DQ-007, deferred from DQ-004) | G1 |
| OI-3 | Decide the tailoring candidates of §5 | G1 |
| OI-4 | Choose the vehicle and drive-by-wire platform, then confirm or redo the provisional ratings (DQ-008) | G2 |
