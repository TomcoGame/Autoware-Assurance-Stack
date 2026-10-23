# WP-C-06 Functional insufficiencies and triggering conditions

| Field | Value |
|---|---|
| Work product | WP-C-06 Functional insufficiencies and triggering conditions |
| Standard reference | UL 4600 §8; ISO 21448 §7; ISO/PAS 8800:2024 (AI error causes) |
| Version | 0.2 (first content: method, functional insufficiencies of the specification and of performance, triggering conditions with the hazards they lead to, AI error causes, generated from `triggering/triggering.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | SOTIF |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

The SOTIF hazard identification ([WP-C-05](WP-C-05-sotif-hazard-identification.md)) found sixteen hazardous behaviours the item can show with nothing broken. This work product goes one level down: which **functional insufficiencies** (gaps in what the functions were specified to do, or limits of how well they do it) cause those behaviours, and which **triggering conditions** (situations in the ODD) expose the insufficiencies. It is the input to the functional modifications ([WP-C-07](WP-C-07-sotif-functional-modifications.md)) and to the evaluation of known hazardous scenarios ([WP-V-03](../06-validation/WP-V-03-sotif-known-scenarios.md)).

Needed at gate G1 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: triggering-summary (assurance/02-concept/triggering/triggering.py) -->

18 functional insufficiencies (8 of the specification, 10 of performance, 2 of them in ML components) and 29 triggering conditions, of which 3 lie at the boundary of the ODD and must be caught by a monitor. Every SOTIF hazard that needs further evaluation is reached by at least one. None is evaluated yet (WP-V-03).

<!-- END GENERATED: triggering-summary -->

## 2. Method

1. **From hazards to insufficiencies.** For each SOTIF hazard of WP-C-05, ask which function's specification or performance lets it happen (ISO 21448 §7). Functions are those of [WP-C-01 §3](WP-C-01-item-definition.md#3-the-item-and-its-functions); the element named is the pinned package or the part of the concept that carries the insufficiency.
2. **From insufficiencies to triggering conditions.** For each insufficiency, list the situations in the ODD that expose it, starting from the example triggers of WP-C-05, the ODD attributes WP-C-02 leaves to this analysis (ODD-12, ODD-16), and the gaps already found in the pinned Autoware. Each condition names the ODD attributes it belongs to; a condition at the ODD's edge names the monitor that must catch it (WP-C-02 §4).
3. **AI error causes.** For insufficiencies of an ML function, list the kinds of cause ISO/PAS 8800 asks to be analysed for an AI component (§6).
4. **Close the loop.** Which hazards a condition can lead to is computed through the insufficiencies it exposes. The generator refuses a model in which a hazard needing further evaluation has no insufficiency, an insufficiency has no triggering condition, or an ML function has no AI error cause.

The insufficiencies and conditions are kept in `triggering/triggering.yaml`; `triggering/triggering.py` writes the tables and Figure 5-1. Nothing here is evaluated yet: whether the item's response to each condition is acceptable is decided by test in WP-V-03, against the acceptance criteria of WP-C-05 §6.

This list covers the **known** conditions. ISO 21448 also asks for the **unknown** ones to be sought; that is the job of the validation in [WP-V-04](../06-validation/WP-V-04-sotif-unknown-scenarios.md), and of the field monitoring in operation, and every condition they find is added here.

## 3. Insufficiencies of specification

What the functions were never specified to do. Most come from gaps in the pinned Autoware already recorded in WP-C-01 and WP-C-02, or from decisions that leave a residual risk (FI-18, DQ-023 C).

<!-- BEGIN GENERATED: triggering-specification (assurance/02-concept/triggering/triggering.py) -->

| ID | Element | Insufficiency | Functions | SOTIF hazards | Exposed by |
|---|---|---|---|---|---|
| FI-11 | HD map currency | Plans on a map that no longer matches the road, with no check that it still does | F-05, F-06 | SH-07 | TC-09 |
| FI-12 | ODD monitoring | No function compares the conditions with the ODD (WP-C-02 §4), so leaving it goes unnoticed | F-09 | SH-08 | TC-28 |
| FI-13 | Emergency vehicle response | No detection of sirens or emergency lights and no yielding manoeuvre (WP-C-02 OEDR-09) | F-02, F-06 | SH-09 | TC-21 |
| FI-14 | Response to people directing traffic | No recognition of a police officer's or flagger's signals (WP-C-02 OEDR-10) | F-02, F-06 | SH-10 | TC-22 |
| FI-15 | Driving style | Behaviour tuned for caution rather than for what other road users expect (long hesitations, stops without visible reason) | F-06 | SH-11 | TC-23 |
| FI-16 | Speed at occlusions | Speed near occlusions is not tied to the stopping distance for a road user emerging from them | F-06 | SH-12 | TC-10 |
| FI-17 | Choice of a place to pull over | No rule for which kerbside places are safe to stop in during an MRM; the operator does not exist yet | F-09 | SH-15 | TC-14 |
| FI-18 | Passenger guidance at a stop in lane | Doors unlock at standstill (DQ-023 C) with no specified warning of traffic on the passenger's side | F-09 | SH-16 | TC-29 |

<!-- END GENERATED: triggering-specification -->

## 4. Performance insufficiencies (sensors, models, maps, localization)

What the functions do, but not well enough in every situation of the ODD.

<!-- BEGIN GENERATED: triggering-performance (assurance/02-concept/triggering/triggering.py) -->

| ID | Element | Insufficiency | Functions | SOTIF hazards | Exposed by |
|---|---|---|---|---|---|
| FI-01 | LiDAR object detection (`autoware_lidar_centerpoint`) | Misses, mislocates or misclassifies objects unlike those it was trained on, and reports objects that are not there | F-02 | SH-01, SH-02 | TC-02, TC-03, TC-04, TC-05, TC-15, TC-16, TC-24 |
| FI-02 | Ground segmentation (`autoware_ground_segmentation`) | Removes low objects as ground, or keeps returns from the road, spray or debris as obstacles | F-02 | SH-01, SH-02 | TC-03, TC-04, TC-16 |
| FI-03 | Tracking and merging (`autoware_multi_object_tracker`, `autoware_object_merger`) | Loses, splits or swaps tracks of objects that are partly hidden or close together, and estimates their velocity late | F-02 | SH-01, SH-04, SH-12 | TC-10, TC-11, TC-18 |
| FI-04 | Traffic light recognition (`autoware_traffic_light_fine_detector`, `autoware_traffic_light_classifier`) | Reads the wrong colour or arrow, or matches a signal head to the wrong lane | F-03 | SH-03 | TC-01, TC-06, TC-07 |
| FI-05 | Motion prediction (`autoware_map_based_prediction`) | Assumes road users follow the map's lanes and rules, so mispredicts people who do not | F-04 | SH-04, SH-05, SH-12 | TC-12, TC-13, TC-17, TC-18, TC-19 |
| FI-06 | Speed estimation of vehicles at range | Estimates the speed of oncoming or circulating vehicles too low, or too late, for a gap decision | F-02, F-04 | SH-05 | TC-05, TC-12, TC-13, TC-20 |
| FI-07 | Localisation (`autoware_ndt_scan_matcher`, `autoware_ekf_localizer`) | Converges to a wrong pose, or degrades without noticing, where the scene differs from the point cloud map | F-01 | SH-06 | TC-08, TC-11 |
| FI-08 | Safety perception channel (EL-03) | Misses low, thin or dark objects, or detects spray and steam as obstacles, so the monitor fails to act or acts without reason | F-10 | SH-14 | TC-02, TC-03, TC-04, TC-05, TC-15, TC-24 |
| FI-09 | Remote driving loop (video, link and operator) | Gives the remote operator too late, too narrow or too poor a picture of the scene to drive safely | F-11 | SH-13 | TC-26, TC-27 |
| FI-10 | Longitudinal and lateral control (`autoware_trajectory_follower_node`) | Achieves less deceleration or more tracking error than planned on a wet road | F-07 | SH-01, SH-06 | TC-25 |

<!-- END GENERATED: triggering-performance -->

FI-08 is the safety monitor's own perception channel. It does not use learned classification (WP-C-04 EL-03), so it has no AI error causes, but it shares triggering conditions with Autoware's perception (TC-02, TC-03, TC-04, TC-15, TC-24). A condition that blinds both at once defeats the doer/checker split; the dependent failure analysis (WP-A-03) must treat these shared conditions as common causes.

## 5. Triggering conditions

![WP-C-06 Figure 5-1: a grid with the sixteen SOTIF hazards SH-01 to SH-16 as rows and five kinds of triggering condition as columns (environment, road and map, road users, vehicle and sensors, operations); each cell shows how many triggering conditions of that kind can lead to that hazard, shaded darker for more. The same data are in the table below.](triggering/fig-c06-5-1-coverage.svg)

*Figure 5-1. How many triggering conditions of each kind can lead to each SOTIF hazard. Generated by `triggering/triggering.py` from `triggering/triggering.yaml`.*

<!-- BEGIN GENERATED: triggering-conditions (assurance/02-concept/triggering/triggering.py) -->

| ID | Kind | Triggering condition | ODD attributes | Caught by | Exposes | Can lead to |
|---|---|---|---|---|---|---|
| TC-01 | Environment | Low sun or oncoming headlights in a camera's view | ODD-12 | — (inside the ODD) | FI-04 | SH-03 |
| TC-02 | Environment | Night or unlit streets, with road users in dark clothing | ODD-12, ODD-16 | — (inside the ODD) | FI-01, FI-08 | SH-01, SH-02, SH-14 |
| TC-03 | Environment | Light rain, spray thrown up by other vehicles, reflections from the wet road | ODD-10, ODD-13 | — (inside the ODD) | FI-01, FI-02, FI-08 | SH-01, SH-02, SH-14 |
| TC-04 | Environment | Steam from vents, exhaust plumes, blowing dust or leaves | ODD-11 | — (inside the ODD) | FI-01, FI-02, FI-08 | SH-01, SH-02, SH-14 |
| TC-05 | Environment | Mist with visibility near the 200 m floor | ODD-11 | — (inside the ODD) | FI-01, FI-06, FI-08 | SH-01, SH-02, SH-05, SH-14 |
| TC-06 | Environment | LED signal heads that flicker against the camera's exposure | ODD-04 | — (inside the ODD) | FI-04 | SH-03 |
| TC-07 | Road and map | Signal heads that are hidden, damaged, temporary, dark in a power outage, or meant for another lane | ODD-04 | — (inside the ODD) | FI-04 | SH-03 |
| TC-08 | Road and map | Streets with few features, or with many objects moved since the point cloud map was made | ODD-01, ODD-02 | — (inside the ODD) | FI-07 | SH-06 |
| TC-09 | Road and map | Construction, re-marked lanes or closures not yet in the map | ODD-07, ODD-08 | MON-02 | FI-11 | SH-07 |
| TC-10 | Road and map | Parked vans, buses, hedges or walls hiding a crossing or a corner | ODD-05, ODD-16 | — (inside the ODD) | FI-03, FI-16 | SH-01, SH-04, SH-12 |
| TC-11 | Road and map | Large vehicles alongside, blocking the LiDAR's view of the surroundings | ODD-17 | — (inside the ODD) | FI-03, FI-07 | SH-01, SH-04, SH-06, SH-12 |
| TC-12 | Road and map | Unprotected left turn with a turning vehicle hiding an oncoming lane | ODD-04 | — (inside the ODD) | FI-05, FI-06 | SH-04, SH-05, SH-12 |
| TC-13 | Road and map | Entry to a multi-lane roundabout with traffic circulating | ODD-04 | — (inside the ODD) | FI-05, FI-06 | SH-04, SH-05, SH-12 |
| TC-14 | Road and map | Bike lanes, driveways, bus stops or crosswalks along the kerb where a pull-over is tried | ODD-05, ODD-09 | — (inside the ODD) | FI-17 | SH-15 |
| TC-15 | Road users | People of unusual shape or posture (wheelchairs, children, people carrying large objects or pushing strollers) | ODD-16 | — (inside the ODD) | FI-01, FI-08 | SH-01, SH-02, SH-14 |
| TC-16 | Road users | Rare objects (animals, e-scooters, fallen loads, debris low on the road) | ODD-16 | — (inside the ODD) | FI-01, FI-02 | SH-01, SH-02 |
| TC-17 | Road users | People crossing away from crossings, or at the kerb looking at a phone | ODD-05, ODD-16 | — (inside the ODD) | FI-05 | SH-04, SH-05, SH-12 |
| TC-18 | Road users | Cyclists riding between lanes or swerving round obstacles | ODD-16 | — (inside the ODD) | FI-03, FI-05 | SH-01, SH-04, SH-05, SH-12 |
| TC-19 | Road users | A vehicle running a red light or not stopping at its stop line | ODD-04, ODD-17 | — (inside the ODD) | FI-05 | SH-04, SH-05, SH-12 |
| TC-20 | Road users | Motorcycles, and vehicles accelerating hard, approaching from far away | ODD-16 | — (inside the ODD) | FI-06 | SH-05 |
| TC-21 | Road users | An emergency vehicle approaching with siren and lights | ODD-18 | — (inside the ODD) | FI-13 | SH-09 |
| TC-22 | Road users | A police officer or flagger directing traffic | ODD-19 | MON-02 | FI-14 | SH-10 |
| TC-23 | Road users | Drivers who expect give and take (four-way stops, merging, letting someone out) | ODD-04, ODD-17 | — (inside the ODD) | FI-15 | SH-11 |
| TC-24 | Vehicle and sensors | Sensors soiled or blocked by dirt, insects or water drops | ODD-10 | — (inside the ODD) | FI-01, FI-08 | SH-01, SH-02, SH-14 |
| TC-25 | Vehicle and sensors | Wet road reducing grip during braking or turning | ODD-13 | — (inside the ODD) | FI-10 | SH-01, SH-06 |
| TC-26 | Operations | Video to the remote operator delayed, compressed or with a narrow field of view | ODD-15 | — (inside the ODD) | FI-09 | SH-13 |
| TC-27 | Operations | A remote operator dealing with more than one vehicle, or tired | ODD-15 | — (inside the ODD) | FI-09 | SH-13 |
| TC-28 | Environment | Weather changing during a trip toward the limits of the ODD | ODD-10, ODD-11 | MON-03 | FI-12 | SH-08 |
| TC-29 | Operations | Passengers getting out at a stop in lane beside moving traffic | — | — (inside the ODD) | FI-18 | SH-16 |

<!-- END GENERATED: triggering-conditions -->

**Reading Figure 5-1.** Not detecting a road user (SH-01) has the most triggering conditions, followed by the other perception- and prediction-led hazards: braking for nothing (SH-02), mispredicting others (SH-04), gap acceptance (SH-05), occlusions (SH-12) and the monitor's own misses (SH-14). Their conditions spread over the environment, the road and road users, which is why the validation of WP-V-03 must vary them together rather than one at a time. The hazards with a single condition (SH-07 to SH-11, SH-15, SH-16) are specification gaps: the condition is ordinary, and what is missing is a specified response.

**Conditions shared by both channels.** TC-02, TC-03, TC-04, TC-15 and TC-24 expose both Autoware's perception (FI-01) and the safety monitor's (FI-08). See §4.

## 6. AI error causes

ISO/PAS 8800 asks for the causes of errors of each AI component to be analysed. The ML functions of the item are those WP-C-01 §3 marks as ML components: object detection (F-02) and traffic light recognition (F-03). For their insufficiencies (FI-01, FI-04), the kinds of cause are:

<!-- BEGIN GENERATED: triggering-ai (assurance/02-concept/triggering/triggering.py) -->

| Cause | What it means | Insufficiencies |
|---|---|---|
| coverage | Training data do not cover part of the input space (WP-C-02 §6) | FI-01, FI-04 |
| labels | Errors or inconsistencies in the labels of training or test data | FI-01, FI-04 |
| shift | The data seen in operation differ in distribution from the training data (new place, sensor, season) | FI-01, FI-04 |
| robustness | Small changes of the input (noise, blur, partial occlusion) change the output | FI-01, FI-04 |
| ood | Inputs unlike anything in the training data, for which the output is arbitrary | FI-04 |
| calibration | The confidence the model reports does not match how often it is right | FI-01 |

<!-- END GENERATED: triggering-ai -->

What data the pinned models were trained and tested on is not established here; the gap between that and the input space of WP-C-02 §6 is assessed in [WP-C-11](WP-C-11-ai-system-definition-and-safety-requirements.md) and [WP-W-10](../05-software/WP-W-10-ml-engineering.md). Until it is, every cause listed applies.

## 7. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Evaluate the item's response to each triggering condition (WP-V-03) | G3 |
| OI-2 | Specify the functional modifications for the specification insufficiencies FI-11 to FI-18 (WP-C-07) | G1 |
| OI-3 | Treat the conditions shared by both perception channels (TC-02, TC-03, TC-04, TC-15, TC-24) as common causes in the dependent failure analysis (WP-A-03) | G2 |
| OI-4 | Establish the training and test data of the pinned ML models against WP-C-02 §6 (WP-C-11, WP-W-10) | G2 |
| OI-5 | Add the sensor-specific triggering conditions once the vehicle and sensor set are chosen (DQ-008, WP-H-02) | G2 |
| OI-6 | Add conditions found by the search for unknown scenarios (WP-V-04) and by field monitoring | G4 |
