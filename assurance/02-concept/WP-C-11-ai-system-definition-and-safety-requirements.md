# WP-C-11 AI system definition and AI safety requirements

| Field | Value |
|---|---|
| Work product | WP-C-11 AI system definition and AI safety requirements |
| Standard reference | UL 4600 §8; ISO 21448 §7; ISO/PAS 8800:2024 (AI safety requirements); ASPICE 4.0 MLE.1 |
| Version | 0.2 (first content: the five AI systems, their role, input space and the safety mechanisms that bound them, AI safety requirements of five kinds and their allocation, generated from `ai/ai.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | AI |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1; an ML engineer) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

Definition of each AI system in the item and the AI safety requirements allocated to it, as ISO/PAS 8800 asks. It builds on the input space of the ODD ([WP-C-02 §6](WP-C-02-odd-and-intended-functionality.md#6-input-space-of-the-ai-components)), the insufficiencies and AI error causes of [WP-C-06](WP-C-06-sotif-insufficiencies-triggering-conditions.md), and the decision that emergency vehicles are detected by sound and light (DQ-025 A).

Needed at gate G1 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: ai-summary (assurance/02-concept/ai/ai.py) -->

5 AI systems (3 in the pinned Autoware, 2 new), all on the Autoware computer, which is QM; none is on a rated element. 14 AI safety requirements, each AI system covered for performance, robustness, uncertainty, data and monitoring. No target value is set here; each requirement names where it is derived.

<!-- END GENERATED: ai-summary -->

The systems and requirements are kept in `ai/ai.yaml`; `ai/ai.py` checks them and writes the tables and Figure 4-1. It refuses an AI system on an element with a rated ASIL, an ML function of WP-C-01 or an insufficiency with AI error causes that has no AI system, and an AI system missing any kind of requirement.

## 2. AI systems and their role in the function

<!-- BEGIN GENERATED: ai-systems (assurance/02-concept/ai/ai.py) -->

| ID | AI system | Component | Function | Element | Task | Output used by | SOTIF hazards | Bounded by |
|---|---|---|---|---|---|---|---|---|
| AIS-01 | LiDAR object detection | `autoware_lidar_centerpoint` (pinned) | F-02 | EL-01 (QM) | Detect and classify vehicles, pedestrians and cyclists in the LiDAR point cloud, with position, size and heading | Tracking (`autoware_multi_object_tracker`), then prediction and planning | SH-01, SH-02, SH-04 | FSR-02.01, FSR-02.02, FSR-06.01 |
| AIS-02 | Traffic light detection | `autoware_traffic_light_fine_detector` (pinned) | F-03 | EL-01 (QM) | Find the signal heads in the camera image, in the regions the map predicts | Traffic light classification (AIS-03) | SH-03 | FSR-06.01, FSR-06.03 |
| AIS-03 | Traffic light classification | `autoware_traffic_light_classifier` (pinned) | F-03 | EL-01 (QM) | Read the colour and arrow of each signal head found by AIS-02 | Traffic light arbiter, then the traffic light module of planning | SH-03 | FSR-06.01, FSR-06.03 |
| AIS-04 | Siren detection | New (FM-15, DQ-025 A) | F-02 | EL-01 (QM) | Detect an emergency siren in the microphone signals, with its rough direction | Emergency vehicle response (FM-15), together with AIS-05 | SH-09 | FSR-02.02, FSR-06.01 |
| AIS-05 | Emergency light detection | New (FM-15, DQ-025 A) | F-02 | EL-01 (QM) | Detect the flashing lights of an emergency vehicle in the camera images | Emergency vehicle response (FM-15), together with AIS-04 | SH-09 | FSR-02.02, FSR-06.01 |

<!-- END GENERATED: ai-systems -->

**Where AI sits in the architecture.** Every AI system runs on the Autoware computer, which is QM by decision (DQ-002 A). None carries a safety goal: their errors are SOTIF insufficiencies, and the rated safety monitor bounds their effect with its own perception channel, which uses no learned classification (WP-C-04 EL-03, DQ-018 A). This is what keeps the AI out of the ASIL D argument. It holds only while the safety channel stays free of learned classification; adding ML to it would bring ISO/PAS 8800 into the rated part of the item and needs the lead's decision.

**The list is not yet complete.** It covers the ML functions WP-C-01 §3 names and the two new detectors. The pinned Autoware has further learned components that the reference launch configuration may start (for example camera-based object detection); OI-2 inventories them from the configuration that is actually deployed.

## 3. Input space and ODD coverage

Each AI system's input space is the part of WP-C-02 §6 it sees. Coverage of each dimension by training and test data is a requirement (AISR-11), measured in WP-W-10.

<!-- BEGIN GENERATED: ai-input (assurance/02-concept/ai/ai.py) -->

| AI system | Object classes | Lighting | Weather | Visibility | Scenery | Traffic lights |
|---|---|---|---|---|---|---|
| AIS-01 LiDAR object detection | ● | ● | ● | ● | ● |  |
| AIS-02 Traffic light detection |  | ● | ● | ● |  | ● |
| AIS-03 Traffic light classification |  | ● | ● | ● |  | ● |
| AIS-04 Siren detection |  |  | ● |  | ● |  |
| AIS-05 Emergency light detection | ● | ● | ● | ● |  |  |

<!-- END GENERATED: ai-input -->

The siren detector (AIS-04) hears rather than sees: its input space is not yet in WP-C-02 §6, which was written for the cameras and LiDAR. The acoustic dimensions (traffic noise, rain on the roof, reflections between buildings, other sirens and alarms) are to be added there (OI-3).

## 4. AI safety requirements (performance, robustness, uncertainty)

![WP-C-11 Figure 4-1: a grid with the five AI systems as rows and five kinds of requirement as columns (performance, robustness, uncertainty, data, monitoring); each cell shows how many AI safety requirements of that kind apply to that system. Every cell is filled. The same data are in the table below.](ai/fig-c11-4-1-requirements.svg)

*Figure 4-1. AI safety requirements by system and kind. Generated by `ai/ai.py` from `ai/ai.yaml`.*

<!-- BEGIN GENERATED: ai-requirements (assurance/02-concept/ai/ai.py) -->

| ID | Kind | AI systems | Requirement | Target set in |
|---|---|---|---|---|
| AISR-01 | Performance | AIS-01 | Detect every class of WP-C-02 ODD-16 within the range and with the miss and false-detection rates that the allotment of AC-02 gives to SH-01 and SH-02 | WP-V-02 (allotment of AC-02) |
| AISR-02 | Performance | AIS-02, AIS-03 | Read signal states with the error rate the allotment of AC-02 gives to SH-03, reporting unknown rather than guessing | WP-V-02 (allotment of AC-02) |
| AISR-03 | Performance | AIS-04, AIS-05 | Detect an approaching emergency vehicle early enough for the yielding manoeuvre to complete, with a false-detection rate low enough that unneeded yields stay rare | WP-V-02; timing from WP-S-04 |
| AISR-04 | Robustness | AIS-01 | Keep the performance of AISR-01 under the triggering conditions of WP-C-06 that reach it (TC-02 to TC-05, TC-15, TC-16, TC-24) | WP-V-03 |
| AISR-05 | Robustness | AIS-02, AIS-03 | Keep the performance of AISR-02 under glare, LED flicker and occluded or damaged heads (TC-01, TC-06, TC-07) | WP-V-03 |
| AISR-06 | Robustness | AIS-04, AIS-05 | Tell real sirens and emergency lights from other loud or flashing sources, and from deliberate fakes (TS-10) | WP-V-03; CSR-09 |
| AISR-07 | Robustness | AIS-01, AIS-02, AIS-03, AIS-05 | Keep performance against the physical attacks on sensors and models known for the ODD (TS-08) | CSR-07 |
| AISR-08 | Uncertainty | AIS-01 | Report a confidence for each detection that matches how often detections at that confidence are right, so that tracking and planning can weigh them | WP-W-10 (calibration measure) |
| AISR-09 | Uncertainty | AIS-02, AIS-03 | Report a state as unknown when its confidence is below the level that keeps AISR-02, so that it is treated as red (FSR-06.03) | WP-W-10 |
| AISR-10 | Uncertainty | AIS-04, AIS-05 | Report confidence for each detection, and yield only when sound and light agree (CSR-09) | WP-W-10 |
| AISR-11 | Data | AIS-01, AIS-02, AIS-03, AIS-04, AIS-05 | Train and test on data covering every dimension of the input space in WP-C-02 §6, collected or verified in the geofence, with the coverage of each dimension measured and reported | WP-W-10 |
| AISR-12 | Data | AIS-01, AIS-02, AIS-03, AIS-04, AIS-05 | Keep training, validation and test sets apart, label them to a written guide with measured label quality, and record each set's version with the model it produced | WP-W-10 |
| AISR-13 | Monitoring | AIS-01 | Rely on the safety channel's own detection, without learned classification, to bound the effect of any detection error (DQ-002 A, DQ-018 A) | FSR-02.01, FSR-02.02 |
| AISR-14 | Monitoring | AIS-01, AIS-02, AIS-03, AIS-04, AIS-05 | Monitor in operation for inputs unlike the training data and for drops in performance, report them, and feed them into retraining and the search for unknown scenarios (WP-V-04) | WP-O-06 (safety performance indicators) |

<!-- END GENERATED: ai-requirements -->

No requirement carries a number yet. Performance targets follow from allotting the SOTIF acceptance criterion (WP-C-05 AC-02, after DQ-020 A) across the hazards, which WP-V-02 does; inventing them here would put unsupported numbers into the safety case.

## 5. Allocation to architecture and to data

<!-- BEGIN GENERATED: ai-allocation (assurance/02-concept/ai/ai.py) -->

| Allocated to | Requirements |
|---|---|
| Model | AISR-01, AISR-02, AISR-03, AISR-04, AISR-05, AISR-06, AISR-07, AISR-08, AISR-09 |
| Data | AISR-11, AISR-12 |
| Architecture | AISR-10, AISR-13 |
| Operation | AISR-14 |

<!-- END GENERATED: ai-allocation -->

How the data requirements AISR-11 and AISR-12 are met depends on whether the project trains its own versions of the models or uses the published ones: the lead's decision (DQ-028).

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Decide whether the project trains its own versions of the models (DQ-028) | G1 |
| OI-2 | Inventory every learned component the deployed launch configuration starts, and add any missing AI system | G1 |
| OI-3 | Add the acoustic dimensions of the siren detector's input space to WP-C-02 §6 | G1 |
| OI-4 | Set the targets of AISR-01 to AISR-03 from the allotment of AC-02 (WP-V-02) | G2 |
| OI-5 | Plan data collection, labelling, training and release in WP-W-10 | G2 |
| OI-6 | Review by an ML engineer independent of the author | G1 |
