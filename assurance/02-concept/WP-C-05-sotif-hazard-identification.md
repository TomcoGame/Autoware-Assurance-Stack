# WP-C-05 SOTIF hazard identification, risk evaluation and acceptance criteria

| Field | Value |
|---|---|
| Work product | WP-C-05 SOTIF hazard identification, risk evaluation and acceptance criteria |
| Standard reference | UL 4600 §6; ISO 21448 §6 |
| Version | 0.3 (AC-01 set: at least as safe as a careful, competent human driver on the same roads (DQ-020 A); 2026-10-23). 0.2 (first content: method, sixteen SOTIF hazards with their evaluation, the acceptance criteria framework, generated from `sotif/sotif.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | SOTIF |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | `051bf30`; item WP-C-01 v0.6, ODD WP-C-02 v0.5, HARA WP-C-03 v0.3, FSC WP-C-04 v0.3 |

## 1. Purpose

This identifies the hazards that arise when the item works as specified, with no fault, but its specification or its performance is not good enough for the situation: perception that misses a pedestrian, a map that no longer matches the road, a manoeuvre other drivers do not expect. It evaluates which of them need further work and sets the acceptance criteria the residual risk is judged against. The [HARA (WP-C-03)](WP-C-03-hara.md) does the same for malfunctions.

For a driverless system this is where most of the risk lies: a fault-free item still has to see, predict and decide well enough across the whole ODD, with no driver to notice when it does not.

In summary:

<!-- BEGIN GENERATED: sotif-summary (assurance/02-concept/sotif/sotif.py) -->

16 SOTIF hazards (8 from insufficiencies of the specification, 8 of performance), 16 needing further evaluation; 15 share a vehicle-level behaviour with a HARA hazard and 1 is SOTIF only. 2 acceptance criteria.

<!-- END GENERATED: sotif-summary -->

## 2. Basis

| Input | Use here |
|---|---|
| Item and functions F-01 to F-12 ([WP-C-01](WP-C-01-item-definition.md)) | The functions whose insufficiencies are analysed |
| ODD, OEDR and manoeuvres ([WP-C-02](WP-C-02-odd-and-intended-functionality.md)) | Where the item must perform; the gaps OEDR-09, OEDR-10 and MAN-10 |
| HARA hazards H-01 to H-10 ([WP-C-03](WP-C-03-hara.md)) | Vehicle-level behaviours shared with malfunctions; the same severity and controllability rules (§3.3 there; DQ-015 B) |
| Functional safety concept ([WP-C-04](WP-C-04-functional-safety-concept.md)) | DQ-017 A leaves traffic-rule compliance (the rule part of SG-06) to this analysis; the safety monitor's own perception (EL-03) has insufficiencies too |

## 3. Method

1. **Find hazardous behaviours.** For each function, ask how it could be insufficient in the ODD without a fault, and what the vehicle would then do. Sources: the functions and their pinned Autoware packages, the OEDR and manoeuvre lists, the HARA hazards, and the gaps already found (no emergency-vehicle response, no response to people directing traffic, no pull-over operator).
2. **Classify the insufficiency.** *Specification*: the function was not asked to do what the situation needs (for example, no siren detection). *Performance*: it was asked, but does not always manage (for example, missing a pedestrian at night).
3. **Evaluate.** Rate the worst credible harm (severity) and controllability with the HARA's rules: C3 for every hazard, because there is no driver and no credit is taken for others (DQ-015 B). A hazard needs further evaluation unless it is S0 or C0; with C3 throughout, every hazard with any harm does.
4. **Hand on.** The triggering conditions listed here seed [WP-C-06](WP-C-06-sotif-insufficiencies-triggering-conditions.md), which analyses them properly; the measures listed point to what the concept already does, and [WP-C-07](WP-C-07-sotif-functional-modifications.md) adds what is missing.

The hazards are kept in [`sotif/sotif.yaml`](sotif/sotif.yaml); [`sotif/sotif.py`](sotif/sotif.py) checks them against WP-C-01 and the HARA and writes §4 to §6 and Figure 4-1. CI runs it with `--check`.

## 4. SOTIF hazards

![Figure 4-1: a grid with the sixteen SOTIF hazards SH-01 to SH-16 as rows and the functions of the item as columns; a filled dot marks a function whose performance insufficiency can cause the hazard, a hollow dot one whose specification insufficiency can. Each row also shows the hazard's severity and the HARA hazards it shares a behaviour with. The same data are in the table below.](sotif/fig-c05-4-1-functions.svg)

*Figure 4-1. Which functions' insufficiencies lead to which hazards. Drawn from `sotif/sotif.yaml` by [`sotif/sotif.py`](sotif/sotif.py); CI fails if it is stale.*

<!-- BEGIN GENERATED: sotif-hazards (assurance/02-concept/sotif/sotif.py) -->

| ID | Hazardous behaviour | Insufficiency | Functions | Related HARA hazards | Example triggering conditions |
|---|---|---|---|---|---|
| SH-01 | Does not detect a road user or obstacle in its path in time, and does not slow or stop | Performance | F-02, F-06 | H-02 | Unusual shapes or postures (wheelchairs, children, people carrying objects), low light, glare, rain and spray, objects partly hidden, classes rare in the training data |
| SH-02 | Brakes hard for a road user or obstacle that is not there | Performance | F-02, F-10 | H-03 | Spray, steam, exhaust plumes, blowing debris, reflections, overhanging foliage, LiDAR returns from rain |
| SH-03 | Reads a red or amber signal as green, or misses a signal, and enters the intersection | Performance | F-03, F-06 | H-06 | Sun behind the signal, LED flicker, occluded or damaged heads, signals for another lane or road, temporary signals, power outages |
| SH-04 | Predicts another road user's motion wrongly and plans too little margin | Performance | F-04, F-06 | H-02, H-06 | Pedestrians at the kerb looking at phones, jaywalking, cyclists between lanes, vehicles not stopping at their stop line |
| SH-05 | Accepts too small a gap in an unprotected left turn or at a roundabout entry | Performance | F-02, F-04, F-06 | H-06 | Oncoming vehicles hidden behind a turning vehicle, speed misestimated at range, motorcycles, vehicles accelerating |
| SH-06 | Localises itself in the wrong place on the map and drives out of its lane | Performance | F-01, F-07 | H-04 | Featureless streets, many new or moved objects since the map was made, large vehicles blocking the LiDAR view, heavy rain |
| SH-07 | Follows an HD map that no longer matches the road | Specification | F-05, F-06 | H-04, H-06 | Construction, re-marked lanes, new one-way streets, temporary closures not yet in the map |
| SH-08 | Does not notice it has left its ODD and keeps driving | Specification | F-09 | H-07 | Rain beyond 2.5 mm/h, fog below 200 m visibility, standing water, loss of the remote link, roads outside the geofence |
| SH-09 | Does not yield to an emergency vehicle with siren and lights | Specification | F-02, F-06 | H-06 | Any emergency vehicle approaching; the pinned Autoware has no siren detection or yielding manoeuvre (WP-C-02 OEDR-09) |
| SH-10 | Ignores a police officer or flagger directing traffic | Specification | F-02, F-06 | H-06 | Signal outages, events, crashes being cleared, work zones; no support in the pinned Autoware (WP-C-02 OEDR-10) |
| SH-11 | Behaves in a way other road users do not expect (hesitates, stops without clear reason, blocks an intersection) | Specification | F-06 | H-03 | Ambiguous objects, conservative gap acceptance, stops in lane after an MRM, waiting at a green light for an unseen hazard |
| SH-12 | Enters a crosswalk or intersection at a speed that does not allow stopping for a road user emerging from behind an obstruction | Specification | F-02, F-06 | H-02, H-06 | Parked vans and buses, queues of stopped traffic, hedges and walls at corners |
| SH-13 | Is driven unsafely by a remote operator who cannot perceive the scene well enough | Performance | F-11 | H-08 | Video delay and compression, limited field of view, no sound, operator workload across several vehicles |
| SH-14 | The safety monitor's own perception misses a road user, or intervenes for one that is not there | Performance | F-10 | H-02, H-03 | Low or thin objects, dark clothing at night for camera-free channels, spray and steam, sensor blockage by dirt or snow |
| SH-15 | Pulls over during an MRM into an unsuitable place | Specification | F-09 | — (SOTIF only) | Bike lanes at the kerb, driveways, bus stops, crosswalks, no suitable kerb within reach |
| SH-16 | After stopping in lane, lets passengers step out into traffic | Specification | F-09 | H-07 | Stop in lane as the rated minimal risk condition (DQ-016 A); passengers wanting to leave a stopped taxi |

<!-- END GENERATED: sotif-hazards -->

Three hazards come from gaps already found in the pinned Autoware: SH-09 (no response to emergency vehicles), SH-10 (no response to a person directing traffic) and SH-15 (no pull-over operator, so its behaviour is still to be specified). SH-16 follows directly from making the stop in lane the rated minimal risk condition (DQ-016 A).

## 5. Evaluation

<!-- BEGIN GENERATED: sotif-evaluation (assurance/02-concept/sotif/sotif.py) -->

| ID | Harm | S | C | Further evaluation | Measures already in the concept |
|---|---|---|---|---|---|
| SH-01 | Collision with a pedestrian, cyclist or vehicle at up to 30 mph | S3 | C3 | **Yes** | Safety monitor's own detection (FSR-02.01, FSR-02.02); training data covering WP-C-02 §6 |
| SH-02 | Rear-end impact by a following vehicle or motorcycle | S2 | C3 | **Yes** | Monitor softens unconfirmed braking (FSR-03.02); false-positive limits on both channels (FSR-03.01) |
| SH-03 | Side impact with crossing traffic or a crossing pedestrian | S3 | C3 | **Yes** | Unknown or unrecognised state treated as red (FSR-06.03); collision avoidance by the monitor (FSR-06.01); this is the rule part of SG-06 that DQ-017 A leaves to SOTIF |
| SH-04 | Collision with a pedestrian stepping off the kerb, a cyclist swerving, or a vehicle running a red light | S3 | C3 | **Yes** | Monitor's bounds on others' motion (FSR-06.01); conservative prediction defaults (WP-C-07) |
| SH-05 | Side impact with an oncoming or circulating vehicle at up to 30 mph | S3 | C3 | **Yes** | Monitor checks the swept path against detected vehicles (FSR-06.01) and occlusion speed limits (FSR-06.02) |
| SH-06 | Head-on or side impact, or a pedestrian struck on the sidewalk | S3 | C3 | **Yes** | Localisation confidence monitoring (MON-02); monitor's lateral check against detected obstacles and kerbs (FSR-04.01) |
| SH-07 | Drives into a closed lane, against a changed traffic direction or through a work zone | S3 | C3 | **Yes** | Map currency and change control (WP-W-12); map–world divergence monitor (MON-02) |
| SH-08 | Any collision under conditions the item was not validated for | S3 | C3 | **Yes** | ODD monitors MON-01 to MON-04 (WP-C-02 §4); MRM on any monitor that cannot decide |
| SH-09 | Collision with an emergency vehicle, or delay to its response | S3 | C3 | **Yes** | Add siren and light detection and a yielding manoeuvre (WP-C-07) |
| SH-10 | Collision in an intersection or work zone controlled by a person | S3 | C3 | **Yes** | Detect a person directing traffic, stop and ask for remote assistance (MON-02, WP-C-07) |
| SH-11 | Rear-end impact, or another road user's evasive manoeuvre ending in a collision | S2 | C3 | **Yes** | Behaviour tuned against human driving data; stopped-vehicle signalling (WP-C-07) |
| SH-12 | Pedestrian or cyclist struck after emerging from behind a parked vehicle or bus | S3 | C3 | **Yes** | Occlusion speed limits enforced by the monitor (FSR-06.02); Autoware's occlusion handling (OEDR-08) |
| SH-13 | Collision during remote driving | S3 | C3 | **Yes** | Monitor envelope applies to remote commands (FSR-08.02); remote operator qualification and limits (AOU-10, WP-O-02) |
| SH-14 | Collision the monitor should have prevented, or an unjustified emergency stop | S3 | C3 | **Yes** | Detection and false-positive targets for EL-03 (FSR-02.01, FSR-03.01); sensor blockage detection; dependent failure analysis with Autoware's sensors (WP-A-03) |
| SH-15 | Collision with a cyclist in a bike lane or a pedestrian at a driveway or crosswalk | S2 | C3 | **Yes** | Pull-over operator restricted to mapped safe stopping places (DQ-016 A, WP-C-01 OI-3) |
| SH-16 | Passenger struck by a passing vehicle | S3 | C3 | **Yes** | Door release only on the kerb side and only with remote operations' consent (WP-C-08); passenger information (WP-O-03) |

<!-- END GENERATED: sotif-evaluation -->

## 6. Acceptance criteria

ISO 21448 asks for acceptance criteria for the residual risk of the hazards that need further evaluation, and UL 4600 asks the safety case to argue that the risk is acceptable across the ODD. With no driver, the natural yardstick is the risk of the same trips driven by people, and the lead, acting as safety authority until one is named, set it on 2026-10-23 (DQ-020 A): the item must be at least as safe as a careful, competent human driver on the same roads, not merely the average driver, who includes impaired and distracted ones. Which published crash data stands for that driver in an urban ODD at up to 30 mph, and with what statistical confidence the rate must be shown, are worked out in WP-V-02.

<!-- BEGIN GENERATED: sotif-acceptance (assurance/02-concept/sotif/sotif.py) -->

| ID | Acceptance criterion | Basis |
|---|---|---|
| AC-01 | The rate of injury crashes the item causes across its ODD does not exceed that of careful, competent human drivers on the same roads | DQ-020 A; the benchmark (published US crash data for urban streets at up to 30 mph, careful and competent drivers) is chosen and the validation target derived in WP-V-02 |
| AC-02 | For each SOTIF hazard needing further evaluation, its residual rate of hazardous behaviour is below the share of AC-01 allotted to it | Allotment in WP-V-02 once AC-01 is set |

<!-- END GENERATED: sotif-acceptance -->

The validation targets that show the criteria are met (how many miles, how many scenarios, of what kinds) follow from AC-01 and are derived in [WP-V-02](../06-validation/WP-V-02-sotif-vv-strategy.md).

## 7. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Choose the benchmark crash data for AC-01 and allot it across the hazards (AC-02, WP-V-02) | G1 |
| OI-2 | Analyse the triggering conditions of every hazard in WP-C-06 | G1 |
| OI-3 | Specify the functional modifications for SH-09, SH-10, SH-15 and SH-16, which have no measure in the concept yet (WP-C-07) | G1 |
| OI-4 | Cross-check with the STPA (WP-A-05) and the misuse analysis (WP-C-08) once drafted | G1 |
