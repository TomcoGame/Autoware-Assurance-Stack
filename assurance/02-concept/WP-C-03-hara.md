# WP-C-03 Hazard analysis and risk assessment, safety goals

| Field | Value |
|---|---|
| Work product | WP-C-03 Hazard analysis and risk assessment, safety goals |
| Standard reference | UL 4600 §6; ISO 26262-3 §6 |
| Version | 0.3 (controllability C3 for every event (DQ-015 B), raising HE-03.1, HE-04.3, HE-05.2, HE-06.3 and HE-09.1 and with them SG-03 and SG-09 to ASIL C; SG-07 safe state set (DQ-016 A); 2026-10-23). 0.2 (first content: method, ten operational situations, ten hazards, nineteen hazardous events, nine safety goals, generated from `hara/hara.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | Up to ASIL D (proposed, §7) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1); confirmation review by an independent assessor (I3) before G1, see DQ-007 |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | `0cd1bda`; item as defined in WP-C-01 v0.4, ODD as in WP-C-02 v0.4 |

## 1. Purpose

This is the hazard analysis and risk assessment of the item ([WP-C-01](WP-C-01-item-definition.md)) in its ODD ([WP-C-02](WP-C-02-odd-and-intended-functionality.md)). It finds the hazards that malfunctions of the item can cause, rates each in the situations where it matters, and derives the safety goals with their ASILs. The functional safety concept ([WP-C-04](WP-C-04-functional-safety-concept.md)) and the fallback concept ([WP-C-12](WP-C-12-fallback-and-minimal-risk-concept.md)) start from §7.

In summary:

<!-- BEGIN GENERATED: hara-summary (assurance/02-concept/hara/hara.py) -->

10 operational situations, 10 hazards, 19 hazardous events (3 B, 8 C, 8 D), 9 safety goals (3 ASIL C, 6 ASIL D).

<!-- END GENERATED: hara-summary -->

Every rating is a draft (I0). The ratings, and therefore the ASILs, are the safety authority's to accept; the confirmation review at G1 checks them independently.

## 2. Scope

| In scope | Where else |
|---|---|
| Malfunctioning behaviour of the item: what happens when its hardware or software fails (ISO 26262) | — |
| | Hazards from the intended functionality working as specified but insufficiently (perception limits, prediction errors): SOTIF, [WP-C-05](WP-C-05-sotif-hazard-identification.md) |
| | Hazards from attacks: [WP-C-09](WP-C-09-tara.md); where an attack leads to a hazard here, the TARA refers to it |
| Foreseeable misuse by passengers where it changes a rating (HE-03.2) | Misuse in general: [WP-C-08](WP-C-08-human-interaction-misuse-analysis.md) |
| Remote driving (DQ-010 C) as an operating mode of the item | The remote operations centre's own failures: WP-O-02 |

The vehicle is not chosen (DQ-008), so severities assume a generic mid-size passenger car (WP-C-01 §6). The state is not chosen (DQ-014), so right-of-way follows the rules common to US states (WP-C-02 §5.1).

## 3. Method

### 3.1 Data and generation

The situations, hazards, events and goals are kept in [`hara/hara.yaml`](hara/hara.yaml). [`hara/hara.py`](hara/hara.py) checks the model, computes every ASIL and writes the tables of §4 to §7 and Figure 6-1; CI runs it with `--check`. To change a rating, edit the YAML and run the generator. No ASIL is typed by hand.

### 3.2 Ratings

| Parameter | Classes | How they are applied here |
|---|---|---|
| Severity | S0 no injuries; S1 light and moderate; S2 severe and life-threatening, survival probable; S3 life-threatening, survival uncertain, or fatal | Rated for the most exposed person at risk. Pedestrians and cyclists struck at 40 km/h or more are S3; at walking pace to 25 km/h S2 |
| Exposure | E0 incredible to E4 high probability | From the operational situation, by duration or by frequency as the situation's *Basis* says. Frequency is used where a situation is entered on every trip (stops, intersections) |
| Controllability | C0 controllable in general to C3 difficult to control or uncontrollable | See §3.3 |
| ASIL | QM, A, B, C, D | ISO 26262-3:2018 Table 4, computed: any class 0 gives QM; otherwise S + E + C of 10 gives D, 9 C, 8 B, 7 A, lower QM |

Class definitions are paraphrased; ISO 26262-3 Annex B and Tables 1 to 4 govern.

### 3.3 Controllability without a driver

ISO 26262 rates controllability by the driver or other persons at risk. Here there is no driver, passengers cannot influence the vehicle, and a remote operator, where one drives, cannot correct what the vehicle no longer receives. The rule used:

**Every hazardous event is rated C3** (decision of the safety authority, DQ-015 B, 2026-10-23). No credit is taken for a driver, for passengers, or for other road users avoiding harm by their own action, even where most of them could: following drivers keeping a legal gap (HE-03.1), pedestrians facing a vehicle at walking pace (HE-04.3, HE-05.2), circulating traffic in a roundabout (HE-06.3), and road users reacting to the vehicle's motion rather than its indicators (HE-09.1). Each of those events states what credit was declined.

The draft had credited those five cases with C2 or C1. Rating them C3 raises four of them by one ASIL and HE-09.1 by two (A to C), and with them SG-03 and SG-09 to ASIL C.

## 4. Operational situations

<!-- BEGIN GENERATED: hara-situations (assurance/02-concept/hara/hara.py) -->

| ID | Situation | Description | Exposure | Basis |
|---|---|---|---|---|
| OS-01 | Driving in lane on an urban street | 25–30 mph, mixed traffic, cyclists in or beside the lane, pedestrians on the sidewalks | E4 | Duration; most of the operating time in a 30 mph urban ODD |
| OS-02 | Driving slowly where pedestrians are dense | Up to 15 mph downtown, near crosswalks and pick-up zones, pedestrians close to the kerb | E3 | Duration; part of most trips but under a tenth of operating time |
| OS-03 | At a signalised intersection with cross traffic | Approaching, waiting at or crossing a signalised intersection while cross traffic moves at up to 30 mph | E4 | Frequency; several intersections on every trip |
| OS-04 | Turning left across oncoming traffic without a protected phase | Permissive green or uncontrolled junction, oncoming traffic at up to 30 mph (DQ-011 C) | E3 | Frequency; several times a day per vehicle, not on every trip |
| OS-05 | Entering or circulating in a roundabout | Single-lane or multi-lane roundabout, circulating traffic at up to 20 mph (DQ-011 C) | E3 | Frequency; the geofence is not known yet, so rated as a few times a day (to be confirmed with DQ-014) |
| OS-06 | Stopped in a queue or at a red light, pedestrians crossing in front | Standstill with vehicles ahead and behind, pedestrians on the crosswalk in front | E4 | Frequency; at every red light and in every queue |
| OS-07 | Stopped at a kerbside stop while passengers board or alight | Standstill at a mapped stop, doors opening, passengers and pedestrians beside and behind the vehicle | E4 | Frequency; twice on every trip |
| OS-08 | Following another vehicle in congested traffic | 0–30 mph, short gaps, the lead vehicle braking often | E4 | Duration; a large share of urban operating time |
| OS-09 | Approaching a crosswalk with pedestrians crossing | 25–30 mph towards a marked crosswalk with a pedestrian on it or stepping onto it | E4 | Frequency; many times on every downtown trip |
| OS-10 | Driven by a remote operator | REMOTE mode in urban traffic at up to 30 mph (DQ-010 C) | E3 | Duration; remote driving in general is allowed and its share of operating time is not yet bounded, so rated above the rare-recovery case (E2) |

<!-- END GENERATED: hara-situations -->

## 5. Hazards

Hazards are malfunctioning behaviours at vehicle level, independent of their cause inside the item.

<!-- BEGIN GENERATED: hara-hazards (assurance/02-concept/hara/hara.py) -->

| ID | Hazard | Description | Hazardous events | Safety goal |
|---|---|---|---|---|
| H-01 | Unintended acceleration | The vehicle accelerates more than needed, or when it should not accelerate at all | HE-01.1, HE-01.2 | SG-01 |
| H-02 | Insufficient deceleration | The vehicle decelerates less than needed, or not at all, when it must slow down or stop | HE-02.1, HE-02.2 | SG-02 |
| H-03 | Unintended hard deceleration | The vehicle brakes hard when there is no reason to | HE-03.1, HE-03.2 | SG-03 |
| H-04 | Unintended lateral motion | The vehicle leaves its planned path or lane | HE-04.1, HE-04.2, HE-04.3 | SG-04 |
| H-05 | Unintended motion from standstill | The vehicle moves forward or rolls when it should be held at standstill | HE-05.1, HE-05.2 | SG-05 |
| H-06 | Proceeding against right of way | Because of a malfunction, the vehicle enters an intersection, roundabout or crosswalk when it must stop or yield | HE-06.1, HE-06.2, HE-06.3, HE-06.4 | SG-06 |
| H-07 | No minimal risk manoeuvre when one is needed | The item can no longer drive safely and does not bring the vehicle to a minimal risk condition | HE-07.1 | SG-07 |
| H-08 | Acting on stale or corrupted remote driving commands | In REMOTE mode the vehicle keeps executing commands that are too old, corrupted or not the operator's | HE-08.1 | SG-08 |
| H-09 | Wrong signalling | Turn indicators show a manoeuvre other than the one the vehicle makes | HE-09.1 | SG-09 |
| H-10 | Unintended reverse motion | The vehicle selects reverse or moves backwards when it should not | HE-10.1 | SG-05 |

<!-- END GENERATED: hara-hazards -->

## 6. Hazardous events and ratings

![Figure 6-1: a grid with the ten hazards H-01 to H-10 as rows and the ten operational situations OS-01 to OS-10 as columns; each cell shows the ASIL of the hazardous events rated there, shaded from light (A) to dark (D); where a cell holds two events it shows the higher ASIL and the count. The same ratings are listed in the table below.](hara/fig-c03-6-1-asil-matrix.svg)

*Figure 6-1. The ASIL of each hazardous event below, by hazard and situation. Drawn from `hara/hara.yaml` by [`hara/hara.py`](hara/hara.py); CI fails if it is stale.*

<!-- BEGIN GENERATED: hara-events (assurance/02-concept/hara/hara.py) -->

| ID | Hazard | Situation | Hazardous event | At risk | S | Severity rationale | E | C | Controllability rationale | ASIL |
|---|---|---|---|---|---|---|---|---|---|---|
| HE-01.1 | H-01 Unintended acceleration | OS-06 Stopped in a queue or at a red light, pedestrians crossing in front | Pulls away from standstill into the pedestrians crossing in front | Pedestrians | S3 | Accelerating from standstill reaches about 25 km/h within a crosswalk's width; a pedestrian struck at that speed and run over can be killed | E4 | C3 | No driver; pedestrians in front of a stopped vehicle do not expect it to move | **D** |
| HE-01.2 | H-01 Unintended acceleration | OS-01 Driving in lane on an urban street | Accelerates into the vehicle ahead | Occupants of both vehicles | S2 | Rear impact at an urban speed difference; serious injury possible, survival probable | E4 | C3 | No driver; the driver ahead cannot avoid being hit | **C** |
| HE-02.1 | H-02 Insufficient deceleration | OS-09 Approaching a crosswalk with pedestrians crossing | Does not slow down for a pedestrian on the crosswalk | Pedestrians | S3 | Pedestrian struck at 40–48 km/h | E4 | C3 | No driver; a pedestrian on the crosswalk has no time to get clear | **D** |
| HE-02.2 | H-02 Insufficient deceleration | OS-08 Following another vehicle in congested traffic | Does not brake when the vehicle ahead slows or stops | Occupants of both vehicles | S2 | Rear impact at up to 48 km/h into a slowing vehicle | E4 | C3 | No driver; the driver ahead cannot avoid it | **C** |
| HE-03.1 | H-03 Unintended hard deceleration | OS-01 Driving in lane on an urban street | Brakes hard for no reason with a vehicle or motorcycle following | The following road user | S2 | Rear-end impact at an urban speed difference; S2 rather than S1 because the follower may be a motorcycle | E4 | C3 | No credit for the following driver's reaction (DQ-015 B); most following drivers keeping a legal gap could stop or swerve | **C** |
| HE-03.2 | H-03 Unintended hard deceleration | OS-01 Driving in lane on an urban street | Brakes hard for no reason while a passenger is unbelted (foreseeable misuse) | Passengers | S1 | An unbelted seated passenger thrown against the seat ahead; light to moderate injury | E4 | C3 | Passengers cannot influence the vehicle | **B** |
| HE-04.1 | H-04 Unintended lateral motion | OS-01 Driving in lane on an urban street | Steers into the oncoming lane | Occupants of both vehicles | S3 | Head-on impact with a combined closing speed near 100 km/h | E4 | C3 | No driver; the oncoming driver has little time and room to avoid it | **D** |
| HE-04.2 | H-04 Unintended lateral motion | OS-01 Driving in lane on an urban street | Steers into a cyclist in or beside the lane | Cyclists | S3 | Cyclist struck from behind or the side at 40–48 km/h | E4 | C3 | No driver; the cyclist cannot see it coming | **D** |
| HE-04.3 | H-04 Unintended lateral motion | OS-02 Driving slowly where pedestrians are dense | Steers onto the sidewalk at low speed | Pedestrians | S2 | Pedestrian struck at up to 24 km/h | E3 | C3 | No credit for pedestrians stepping away (DQ-015 B), though at low speed most could | **B** |
| HE-05.1 | H-05 Unintended motion from standstill | OS-07 Stopped at a kerbside stop while passengers board or alight | Moves off while a passenger is boarding or alighting | Passengers | S3 | A person half in the vehicle can be dragged or run over | E4 | C3 | The person boarding cannot get clear | **D** |
| HE-05.2 | H-05 Unintended motion from standstill | OS-06 Stopped in a queue or at a red light, pedestrians crossing in front | Creeps or rolls into the crosswalk while stopped at a red light | Pedestrians | S2 | Pedestrian knocked down at walking pace; run-over possible | E4 | C3 | No credit for pedestrians noticing the slow movement (DQ-015 B) | **C** |
| HE-06.1 | H-06 Proceeding against right of way | OS-03 At a signalised intersection with cross traffic | Enters the intersection on red into crossing traffic | Occupants of both vehicles | S3 | Side impact into the occupant compartment at up to 48 km/h | E4 | C3 | No driver; the crossing driver has right of way and little time | **D** |
| HE-06.2 | H-06 Proceeding against right of way | OS-04 Turning left across oncoming traffic without a protected phase | Turns left in front of an oncoming vehicle | Occupants of both vehicles | S3 | Oncoming vehicle at up to 48 km/h strikes the turning vehicle's side | E3 | C3 | No driver; the oncoming driver expects to keep right of way | **C** |
| HE-06.3 | H-06 Proceeding against right of way | OS-05 Entering or circulating in a roundabout | Enters the roundabout without yielding to circulating traffic | Occupants of both vehicles | S2 | Angled impact at roundabout speeds up to 32 km/h | E3 | C3 | No credit for circulating drivers braking (DQ-015 B), though at roundabout speeds most could | **B** |
| HE-06.4 | H-06 Proceeding against right of way | OS-09 Approaching a crosswalk with pedestrians crossing | Does not yield to a pedestrian on the crosswalk | Pedestrians | S3 | Pedestrian struck at 40–48 km/h | E4 | C3 | No driver; the pedestrian has right of way and no time to react | **D** |
| HE-07.1 | H-07 No minimal risk manoeuvre when one is needed | OS-01 Driving in lane on an urban street | After a fault in planning or control, keeps driving without control instead of stopping | All road users and passengers | S3 | Any collision at urban speed, including with pedestrians and cyclists | E4 | C3 | No driver and no other road user can take over | **D** |
| HE-08.1 | H-08 Acting on stale or corrupted remote driving commands | OS-10 Driven by a remote operator | Keeps moving on stale commands after the remote link is delayed or lost | All road users and passengers | S3 | Collision at urban speed, including with pedestrians | E3 | C3 | The remote operator cannot correct what the vehicle no longer receives | **C** |
| HE-09.1 | H-09 Wrong signalling | OS-01 Driving in lane on an urban street | Indicates the wrong direction before a turn or lane change | Cyclists and drivers nearby | S2 | A cyclist or driver moves into the path the vehicle then takes | E4 | C3 | No credit for other road users reacting to the vehicle's actual motion (DQ-015 B) | **C** |
| HE-10.1 | H-10 Unintended reverse motion | OS-07 Stopped at a kerbside stop while passengers board or alight | Reverses into a person behind the vehicle at a kerbside stop | Pedestrians and passengers | S2 | Pedestrian knocked down at walking pace; run-over possible | E4 | C3 | No driver; a person behind a stopped taxi does not expect it to reverse | **C** |

<!-- END GENERATED: hara-events -->

## 7. Safety goals

Each safety goal takes the highest ASIL of the hazardous events of its hazards. Fault tolerant time intervals are set in [WP-S-04](../03-system/WP-S-04-timing-ftti-budget.md) once the vehicle is known.

<!-- BEGIN GENERATED: hara-goals (assurance/02-concept/hara/hara.py) -->

| ID | Safety goal | ASIL | Hazards | From hazardous events | Safe state |
|---|---|---|---|---|---|
| SG-01 | Avoid unintended acceleration | **D** | H-01 | HE-01.1 | Propulsion off and the vehicle held at standstill |
| SG-02 | Decelerate at least as much as needed to avoid a collision the planned trajectory avoids | **D** | H-02 | HE-02.1 | Vehicle braked to standstill and held |
| SG-03 | Avoid unintended hard deceleration | **C** | H-03 | HE-03.1 | Normal driving continues, or a comfortable stop |
| SG-04 | Avoid unintended lateral motion out of the planned path | **D** | H-04 | HE-04.1, HE-04.2 | Vehicle stopped in its lane |
| SG-05 | Avoid unintended motion from standstill, forward or backward | **D** | H-05, H-10 | HE-05.1 | Vehicle held at standstill with the park brake applied |
| SG-06 | Do not enter an intersection, roundabout or crosswalk against right of way | **D** | H-06 | HE-06.1, HE-06.4 | Vehicle stopped before the stop line or conflict area |
| SG-07 | Reach a minimal risk condition whenever the item can no longer drive safely | **D** | H-07 | HE-07.1 | Vehicle stopped and held in its lane with hazard lights on; Autoware pulls over to the kerb first when it still can, but the rated condition is the stop in lane (DQ-016 A) |
| SG-08 | Do not act on remote driving commands that are stale, corrupted or not the operator's | **C** | H-08 | HE-08.1 | Vehicle brought to a stop and held |
| SG-09 | Avoid signalling a manoeuvre other than the one performed | **C** | H-09 | HE-09.1 | Indicators off, hazard lights on |

<!-- END GENERATED: hara-goals -->

**What the goals mean for the architecture (DQ-002 A).** Six goals are ASIL D. With Autoware kept QM, each of them falls on the independent safety monitor and the drive-by-wire path: the monitor must detect and stop unintended acceleration, insufficient braking, lateral departure and motion from standstill (SG-01, SG-02, SG-04, SG-05), refuse to pass a command that enters a conflict area against right of way (SG-06), and bring the vehicle to a stop on its own (SG-07). SG-06 and SG-02 are the hard ones: deciding that a command is unsafe there needs knowledge of the scene (a red light, a pedestrian), which a simple envelope monitor does not have. How the monitor can meet them, or whether ASIL decomposition between Autoware and the monitor is needed, is the first question of the functional safety concept ([WP-C-04](WP-C-04-functional-safety-concept.md), [WP-A-01](../08-analyses/WP-A-01-asil-decomposition.md)).

## 8. Assumptions and items to confirm

| ID | Item | Confirmed when |
|---|---|---|
| HA-1 | Severities assume a generic mid-size passenger car at up to 30 mph. A heavier vehicle can raise S2 ratings to S3 | Vehicle chosen (DQ-008) |
| HA-2 | Exposure of roundabouts (OS-05) and remote driving (OS-10) is estimated without a geofence or an operations concept | Geofence (DQ-014, WP-C-02 OI-6) and WP-O-02 |
| HA-3 | Right of way follows rules common to US states; where states differ the stricter case is assumed | State chosen (DQ-014) |
| HA-4 | Unbelted passengers are foreseeable misuse and rated (HE-03.2); standing passengers are not, because the vehicle is assumed to have seats only | Vehicle chosen (DQ-008) |
| HA-5 | The rated minimal risk condition is a stop in lane with hazard lights on; Autoware pulls over to the kerb first when it still can, which is not rated (DQ-016 A). Stops in lane are therefore part of normal operation after faults, and their exposure to rear-end impacts is covered by SG-03 and the fallback concept (WP-C-12) | Decided (DQ-016 A) |

## 9. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Safety authority to accept the ratings and safety goals as a whole before the confirmation review | G1 |
| OI-2 | Re-check every severity once the vehicle is chosen (HA-1, HA-4) | G2 |
| OI-3 | Re-check exposure of OS-05 and OS-10 with the geofence and the remote operations concept (HA-2) | G1 |
| OI-4 | Confirmation review of this HARA by an independent assessor (I3); needs DQ-007 | G1 |
| OI-5 | Cross-check against the SOTIF hazards (WP-C-05) and the STPA (WP-A-05) once drafted, and add any malfunctioning behaviour they find | G1 |
