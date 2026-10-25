Terms and identifiers as this project uses them. Definitions are plain-language summaries; where a standard defines
a term, the standard governs.

## Identifiers

Identifiers are never reused; a withdrawn item keeps its identifier and is marked `Withdrawn`. The full table is in
[`assurance/README.md`](../assurance/README.md#identifiers).

| Prefix | Meaning |
|---|---|
| `WP-<area>-<nn>` | Work product. Areas: M management, C concept, S system, H hardware, W software, V validation, P supporting processes, A analyses, O production and operation, K safety case, T traceability |
| `DQ-<nnn>` | A question in the [decision register](../assurance/01-management/decisions/README.md). "DQ-015 B" means option B of DQ-015 |
| `G0` to `G6` | Gates, from governance to operation ([WP-M-00 §2](../assurance/01-management/WP-M-00-work-product-register.md#2-gates)) |
| `H-<nn>`, `HE-<nn>.<n>`, `SG-<nn>` | Hazard, hazardous event, safety goal ([WP-C-03](../assurance/02-concept/WP-C-03-hara.md)) |
| `FSR-<nn>.<nn>`, `TSR-<nnn>` | Functional safety requirement, technical safety requirement |
| `SWSR-<nnn>`, `HWSR-<nnn>` | Software and hardware safety requirement |
| `SH-`, `FI-`, `TC-`, `FM-<nn>` | SOTIF hazard, functional insufficiency, triggering condition, functional modification |
| `MRM-<nn>`, `MRC-<nn>` | Minimal risk manoeuvre, minimal risk condition |
| `TS-`, `CSG-`, `CSR-<nn>` | Threat scenario, cybersecurity goal, cybersecurity requirement |
| `AOU-<nn>` | Assumption on the vehicle, infrastructure, people or environment |
| `SPI-<nn>` | Safety performance indicator |
| `CL-`, `EV-`, `DF-<nnn>` | Safety case claim, evidence item, defeater |
| `OI-<n>` | Open item, numbered per document |
| `F-<nn>`, `I-<nn>` | Function and interface of the item ([WP-C-01](../assurance/02-concept/WP-C-01-item-definition.md)) |
| `ODD-<nn>`, `MON-<nn>` | ODD attribute and ODD monitoring function ([WP-C-02](../assurance/02-concept/WP-C-02-odd-and-intended-functionality.md)) |
| `EL-<nn>` | Element of the functional safety concept ([WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md)) |
| `AC-<nn>` | SOTIF acceptance criterion ([WP-C-05](../assurance/02-concept/WP-C-05-sotif-hazard-identification.md)) |
| `AIS-<nn>`, `AISR-<nn>` | AI system and AI safety requirement ([WP-C-11](../assurance/02-concept/WP-C-11-ai-system-definition-and-safety-requirements.md)) |
| `CG-`, `CC-<nn>` | Cybersecurity goal and cybersecurity claim in the cybersecurity concept ([WP-C-10](../assurance/02-concept/WP-C-10-cybersecurity-goals-and-concept.md)) |
| `CR-<nn>` | Cybersecurity control proposed by the TARA ([WP-C-09](../assurance/02-concept/WP-C-09-tara.md)) |
| `CSTR-<nn>.<nn>` | Technical cybersecurity requirement ([WP-S-07](../assurance/03-system/secarch/README.md)) |
| `SZ-<n>`, `EX-<nn>` | Security zone (a part of the system with one level of trust) and external interface (a way into the vehicle from outside) ([WP-S-07](../assurance/03-system/secarch/README.md)) |
| `CMP-<nn>`, `SM-<nn>`, `RD-<nn>` | Component of the system architecture, safety mechanism, and redundancy (two channels that cover each other) ([WP-S-03](../assurance/03-system/tsc/README.md)) |
| `P-<nn>` | Safety envelope parameter ([WP-S-02](../assurance/03-system/tsr/README.md)) |
| `IF-<nn>`, `SIG-<nn>`, `CK-<nn>`, `HD-<nn>` | Interface, signal, clock and hardware diagnostic of the hardware–software interface ([WP-S-05](../assurance/03-system/hsi/README.md)) |
| `ENV-<n>`, `IS-<n>`, `IT-<nn>` | Test environment, integration step and integration test case ([WP-S-08](../assurance/03-system/integ/README.md)) |
| `SIM-<nn>` | Simulator used for validation ([WP-V-08](../assurance/06-validation/README.md)) |
| `TR-<nn>` | Fallback trigger: a condition that starts a minimal risk manoeuvre ([WP-C-12](../assurance/02-concept/WP-C-12-fallback-and-minimal-risk-concept.md)) |
| `OS-<nn>` | Operational situation: a driving situation the HARA rates hazards in ([WP-C-03](../assurance/02-concept/WP-C-03-hara.md)) |
| `M01` to `M14`, `W01` to `W06` | HARA guide words (the ways a function can malfunction, such as M01 "no function") and road and light conditions (such as W01 "dry road in daylight") ([WP-C-03](../assurance/02-concept/WP-C-03-hara.md)) |

## Terms

| Term | Meaning here |
|---|---|
| 21434, 21448, 26262, PAS 8800 | Short for ISO/SAE 21434 (cybersecurity), ISO 21448 (SOTIF), ISO 26262 (functional safety) and ISO/PAS 8800 (AI safety). "26262-3" is part 3 of ISO 26262; "26262-8 §13" is clause 13 of part 8 |
| ACQ, HWE, MAN, MLE, SUP, SWE, SYS, VAL | Automotive SPICE process groups: acquisition, hardware engineering, management, machine learning engineering, support, software engineering, system engineering, validation. "SWE.1–6" means processes 1 to 6 of the group |
| AD API | Autoware's autonomous driving API: the interface for trips, modes and requests |
| AI | Artificial intelligence: here the machine-learned perception and prediction models, and the AI assistant that drafts much of the work |
| API | Application programming interface: how one program asks another for something |
| ASIL | Automotive Safety Integrity Level, A (lowest) to D (highest), set by ISO 26262 for each safety goal from severity, exposure and controllability. QM means no ASIL: ordinary quality management is enough |
| ASPICE, Automotive SPICE | Automotive Software Process Improvement and Capability dEtermination: a model for rating how capable the development process is. The project uses version 4.0 |
| Assessor | An independent person or body who assesses the work (I3). Not yet named: DQ-004 was deferred and is asked again as DQ-007 |
| AUTOSAR | AUTomotive Open System ARchitecture: an industry standard for vehicle software, whose E2E profiles protect messages |
| Baseline | The commit or tag of upstream Autoware a work product refers to, named in the `Baseline` field of its header |
| C0–C3, E0–E4, S0–S3 | Controllability, exposure and severity classes used to rate a hazardous event ([WP-C-03 §3.2](../assurance/02-concept/WP-C-03-hara.md#32-ratings)) |
| CAL | Cybersecurity assurance level, CAL1 (lowest) to CAL4 (highest), from ISO/SAE 21434: how much rigour a cybersecurity requirement needs |
| CAN, CAN FD | Controller Area Network, and its flexible data-rate version: the common vehicle bus |
| CI | Continuous integration: the automated checks GitHub runs on every pull request and push |
| Claim | A statement the safety case asserts and has to support with evidence or sub-claims |
| Confirmation review | A review by someone independent of the author that a key work product, such as the HARA, is right ([WP-M-06](../assurance/01-management/WP-M-06-confirmation-measures-plan.md)) |
| CS | Cybersecurity, as a scope in a document header |
| DDT | Dynamic driving task: steering, braking, accelerating and watching the road, in real time |
| Decision register | Where questions for the safety authority are asked and answered. See [How decisions are made](How-decisions-are-made.md) |
| Defeater | A known reason a claim or evidence item may not hold. See [What is a safety case?](What-is-a-safety-case.md) |
| DFA | Dependent failure analysis: looks for one cause that could defeat several safety measures at once |
| DIA | Development interface agreement: who does which safety work, between this project and a supplier |
| Drive-by-wire | The vehicle's electronic interface for steering, braking and propulsion commands. Outside the item; chosen with the vehicle at G2 |
| E2E | End-to-end protection: a checksum, counter and timeout on each message, checked by the receiver |
| ECC | Error-correcting code: memory that detects and corrects bit errors |
| FMEA | Failure mode and effects analysis: works through how each part can fail and what follows |
| FMEDA | Failure modes, effects and diagnostic analysis: an FMEA that also counts how many failures the diagnostics catch |
| Fork | A copy of another repository that adds its own work; this repository is a fork of `autowarefoundation/autoware` |
| FSC | Functional safety concept: how the safety goals are met, as functional safety requirements allocated to elements ([WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md)) |
| FSR | Functional safety requirement, as in FSR-08.01 ([WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md)) |
| FTA | Fault tree analysis: works backward from a harmful event to the combinations of faults that cause it |
| FTTI | Fault tolerant time interval: how long a fault can last before it can lead to harm. Set in [WP-S-04](../assurance/03-system/WP-S-04-timing-ftti-budget.md) once the vehicle is known |
| Gate | A milestone with exit criteria. The project's gates are G0 to G6 |
| Generator | A script that writes tables, figures or summaries from a source file, with a `--check` mode that CI runs |
| GNSS | Global navigation satellite system, such as GPS; here also a source of exact time |
| HARA | Hazard analysis and risk assessment (ISO 26262-3): finds hazards from malfunctions, rates them, and sets safety goals ([WP-C-03](../assurance/02-concept/WP-C-03-hara.md)) |
| HD map | High-definition map: the detailed lane-level map Autoware drives from |
| HIL | Hardware in the loop: testing the real controller against a simulated vehicle |
| HSI | Hardware–software interface ([WP-S-05](../assurance/03-system/hsi/README.md)) |
| I0 to I3 | Levels of reviewer independence, from none (I0) to an independent assessor (I3). Work drafted by the AI assistant is I0. The project's definitions are to be written in [WP-M-06 §2](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#2-confirmation-reviews-and-required-independence-i1i3) |
| ID | Identifier |
| IEEE | Institute of Electrical and Electronics Engineers, which publishes standards such as IEEE 802.1AS (network time) and IEEE 2846 (driving behaviour assumptions) |
| ISO, ISO/SAE, ISO/PAS | International Organization for Standardization; a standard it publishes jointly with SAE International; a Publicly Available Specification, published before full consensus |
| Item | The system the safety work is about: here the sensors, Autoware on its computer, and the safety monitor. The vehicle is outside it ([WP-C-01](../assurance/02-concept/WP-C-01-item-definition.md)) |
| LFM | Latent fault metric: the share of latent (hidden) faults the design detects (ISO 26262-5) |
| Minimal risk condition (MRC) | A stable, stopped state the vehicle reaches by itself when it can no longer drive safely |
| Minimal risk manoeuvre (MRM) | The manoeuvre that brings the vehicle to a minimal risk condition |
| ML | Machine learning |
| n/a | Not applicable |
| ODD | Operational design domain: the roads, conditions and traffic the system is designed for ([WP-C-02](../assurance/02-concept/WP-C-02-odd-and-intended-functionality.md)) |
| OEDR | Object and event detection and response: noticing what happens around the vehicle and responding to it |
| OI | Open item: a known gap recorded in a document, numbered per document |
| OS | Operating system (not to be confused with `OS-<nn>`, an operational situation) |
| Pinned version | The exact version of an Autoware source repository, recorded in [`repositories/autoware.repos`](../repositories/autoware.repos) |
| PMHF | Probabilistic metric for random hardware failures: the rate at which hardware faults could violate a safety goal (ISO 26262-5) |
| QM | Quality management: no ASIL is needed, ordinary quality processes are enough |
| RAM | Random-access memory: a computer's working memory |
| Reference configuration | The one configuration the claims apply to ([WP-M-01 §3.1](../assurance/01-management/WP-M-01-assurance-strategy.md#31-reference-configuration)) |
| REMOTE | The operating mode in which a remote operator drives the vehicle ([WP-C-01](../assurance/02-concept/WP-C-01-item-definition.md)) |
| Robotaxi | A taxi with no driver on board |
| SAE | SAE International, formerly the Society of Automotive Engineers |
| Safe state | The state a safety goal requires the vehicle to reach or keep when it cannot otherwise meet the goal |
| Safety authority | Who accepts risk and decides the questions of the decision register. The project lead until DQ-004 names one |
| Safety case | A structured argument, with evidence, that the system is acceptably safe. See [What is a safety case?](What-is-a-safety-case.md) |
| Safety envelope | The bounds within which the safety monitor lets a command through ([WP-C-04 §2](../assurance/02-concept/WP-C-04-functional-safety-concept.md#2-the-concept)) |
| Safety goal | A top-level safety requirement from the HARA, with an ASIL and a safe state |
| Safety monitor | The independent controller, on its own hardware between Autoware and the drive-by-wire system, that checks every command and can stop the vehicle on its own (DQ-002 A). It does not exist yet |
| Skeleton, Draft, In review, Approved, Baselined | Status of a work product: structure only; written, not verified; in verification review; approved; approved and frozen ([status meanings](../assurance/README.md#status-meanings)) |
| SOTIF | Safety of the intended functionality (ISO 21448): harm from a function working as designed but not well enough |
| SPFM | Single-point fault metric: the share of single-point faults the design covers (ISO 26262-5) |
| SPI | Safety performance indicator: a measured value that shows in operation whether the safety case still holds ([WP-O-06](../assurance/09-production-operation/WP-O-06-safety-performance-indicators.md)) |
| STPA | System-theoretic process analysis: finds hazards from unsafe control actions and interactions rather than from failed parts |
| TARA | Threat analysis and risk assessment (ISO/SAE 21434) ([WP-C-09](../assurance/02-concept/WP-C-09-tara.md)) |
| TBD | To be decided |
| Trace link | A recorded relation between two requirements, or a requirement and a test: derives, allocates, verifies, mitigates |
| Triggering condition | A situation that makes a functional insufficiency lead to hazardous behaviour (SOTIF) |
| TSR | Technical safety requirement, as in TSR-01.01 ([WP-S-02](../assurance/03-system/tsr/README.md)) |
| UL 4600 | The standard for the safety of autonomous products, from UL Standards & Engagement; the main framework here |
| WBS | Work breakdown structure: the project's work split into tasks |
| Work product | A document or record the assurance path needs. All of them are listed in the [register](../assurance/01-management/WP-M-00-work-product-register.md) |
| YAML | A plain-text data format; the analyses and registers keep their source data in `.yaml` files |

## Tools and platforms

The software the [`ansible/`](../ansible/README.md) and [`docker/`](../docker/README.md) tooling sets up, as the upstream READMEs use the words. Each of those READMEs ends with a table of its own terms.

| Term | Meaning |
|---|---|
| amd64, x86_64, arm64, aarch64 | Processor architectures: 64-bit Intel/AMD (amd64, also called x86_64) and 64-bit ARM (arm64, also called aarch64, as on NVIDIA Jetson) |
| Ansible, role, playbook | Ansible is the automation tool in [`ansible/`](../ansible/README.md) that sets up a machine; a role installs or configures one thing; a playbook lists which roles to run |
| apt, apt-get | Advanced Package Tool: Ubuntu's package manager, used to install system software |
| AWSIM | An open-source Autoware simulator built on the Unity game engine, with simulated sensors and city maps |
| CUDA, cuDNN, TensorRT | NVIDIA's toolkits for running computation on its GPUs, its neural-network library, and its inference optimiser; Autoware's perception uses them |
| DDS, RMW | Data Distribution Service, the publish-subscribe middleware ROS 2 messages travel over, and the ROS middleware layer that selects a DDS implementation |
| Docker, image, container | Docker runs software in containers: isolated environments with their own files, started from a packaged image ([`docker/`](../docker/README.md)) |
| Git, commit, tag | The version control system; a commit is one recorded change, a tag a name given to one version |
| GPU | Graphics processing unit: used for graphics and for running neural networks |
| Humble, Jazzy | ROS 2 releases: Humble Hawksbill (with Ubuntu 22.04) and Jazzy Jalisco (with Ubuntu 24.04) |
| NVIDIA | The company that makes the GPUs and GPU software Autoware uses |
| Planning simulator, scenario simulator | Autoware's lightweight simulator for planning and control without real sensors, and `scenario_simulator_v2`, which runs scripted traffic scenarios against Autoware |
| ROS 2 | Robot Operating System 2: the middleware Autoware is built on |
| RViz | The ROS 2 3D viewer that shows the map, sensor data and planned path |
| sudo | Runs a command with administrator (root) rights |
| Ubuntu | The Linux distribution Autoware targets; versions are named year.month, such as 22.04 |
| Upstream | The original project this fork comes from: [Autoware](https://github.com/autowarefoundation/autoware) and its repositories |
| vcs, `.repos` file | The tool that clones every repository listed in a `.repos` manifest file at once, such as [`repositories/autoware.repos`](../repositories/autoware.repos) |

## Symbols

| Symbol | Meaning |
|---|---|
| `<nn>`, `<nnn>`, `<n>` | Placeholders in an identifier pattern for a two-digit, three-digit or any number |
| `--check` | The mode of a generator that changes nothing and fails if the committed output is stale |
| § | Section or clause, as in "WP-M-01 §4" or "UL 4600 §5" |
| – (en dash) in a range | "through", as in "§6–8" (clauses 6 to 8) or "I0–I3" |
| / | "and" between numbers, as in "MAN.3/5" (MAN.3 and MAN.5); "or" between alternatives, as in "hazard / hazardous event" |
| → | From one component to another, or leads to |
| — | Nothing: no value, or a subfolder with no README of its own |
| B(D) | An ASIL B requirement that is part of a decomposition of an ASIL D one |
| ⭐, 🔗, ➡️, ⚠️, 🛠️ and other emoji | Markers in the upstream READMEs: a link worth following, an external link, "is" or "leads to", a warning, advanced instructions. Each README's own table says what its emoji mean |

## In pictures

![The item: a white robotaxi seen from the front left, with the Autoware computer, the safety monitor, Autoware's roof sensor and the monitor's own sensors drawn inside it at illustrative positions, and a list of the elements inside and outside the item with their ratings from WP-C-04.](../tools/readme/figures/item.svg)

*Illustration: positions are not decided. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle model CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*

![When it can no longer drive on safely: left, the robotaxi pulled over to the kerb, Autoware's own manoeuvre; right, the robotaxi stopped in its lane with hazard lights on, the rated minimal risk condition of SG-07. Below, the safe state as WP-C-03 states it.](../tools/readme/figures/minimal-risk-condition.svg)

*Illustration. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle models CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*

![Inside and outside the ODD: three panels of the robotaxi on a city street, for the posted speed limit (a speed sign inside the geofence and a higher one beyond it), precipitation (rain) and visibility (fog). Under each, what is inside and outside the ODD as WP-C-02 states it, and the monitor that detects it.](../tools/readme/figures/odd.svg)

*Illustration. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle model CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*

![How long a fault may last: three panels of the robotaxi with the margin a safety goal keeps drawn in blue (SG-01 unintended acceleration, SG-04 unintended steering, SG-05 creeping from standstill), and under each a time line from the fault through detection and reaction to the FTTI, with the range WP-S-04 computes from proposed values.](../tools/readme/figures/ftti.svg)

*Illustration: proposed values, nothing measured. FTTIs computed by WP-S-04's own `timing.py`. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle models CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*

![Where an attacker could reach: the robotaxi with numbered markers where the assets of the threat analysis (WP-C-09) sit, and a list of the assets with their number of threat scenarios and highest risk.](../tools/readme/figures/attack-surface.svg)

*Illustration: positions are illustrative. Risks computed by WP-C-09's own `tara.py`. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle models CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*
