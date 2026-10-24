# WP-C-03 Hazard analysis and risk assessment, safety goals

| Field | Value |
|---|---|
| Work product | WP-C-03 Hazard analysis and risk assessment, safety goals |
| Standard reference | UL 4600 §6; ISO 26262-3 §6 |
| Version | 0.4 (every function of WP-C-01 against fourteen malfunction guide words, each safety-related pair rated in twenty operational situations under six road and light conditions: 5 400 rated rows, browsable as tables; ten situations added; the safety goals and their ASILs unchanged; 2026-10-24). 0.3 (controllability C3 for every event (DQ-015 B), raising HE-03.1, HE-04.3, HE-05.2, HE-06.3 and HE-09.1 and with them SG-03 and SG-09 to ASIL C; SG-07 safe state set (DQ-016 A); 2026-10-23). 0.2 (first content: method, ten operational situations, ten hazards, nineteen hazardous events, nine safety goals, generated from `hara/hara.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
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

5400 rated rows (every safety-related function and malfunction pair in every situation and condition; 3828 hazardous, 3403 of them ASIL A or above), 20 operational situations, 10 hazards, 19 named hazardous events (3 B, 8 C, 8 D), 9 safety goals (3 ASIL C, 6 ASIL D).

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

The analysis works through every malfunction of every function, in every situation, instead of starting from the events an analyst thinks of:

1. Every function of the item (WP-C-01 §2) is taken against fourteen malfunction guide words (§6.1). Each pair is classed safety-related, not safety-related or not applicable, with the reason. A safety-related pair names the hazard it leads to; a pair with the same effect on the vehicle as another of the same function is folded into it and rated once.
2. Every safety-related pair that is not folded is rated in every operational situation (§4) under every road and light condition (§4.1). Severity comes from the hazard and the situation, with its reason, or is S0 with the reason it cannot occur there. Exposure is the rarer of the situation's and the condition's. Controllability follows §3.3. Nothing is dropped: a row that is not hazardous is kept with S0 and its reason.
3. The rows are written one file per hazard ([`hara/hazardous-events/`](hara/hazardous-events/)), which GitHub shows as a searchable table in the browser, so the analysis can be read row by row without downloading anything (§6.2).
4. The named hazardous events of §6.3 are the representative events the rest of the safety case refers to. The generator refuses a named event more severe than its rows allow, and a row whose ASIL exceeds the ASIL its safety goal takes from the named events. Either would mean the named events no longer cover the analysis.

The situations, hazards, named events and goals are kept in [`hara/hara.yaml`](hara/hara.yaml); the functions, guide-word classification, conditions and severity rules in [`hara/analysis.yaml`](hara/analysis.yaml). [`hara/hara.py`](hara/hara.py) checks both, computes every ASIL, and writes the tables of §4 to §7, Figures 6-1 and 6-2, and the row files; CI runs it with `--check`. To change a rating, edit the YAML and run the generator; the diff of the row files shows every row the change moves. No ASIL is typed by hand.

### 3.2 Ratings

| Parameter | Classes | How they are applied here |
|---|---|---|
| Severity | S0 no injuries; S1 light and moderate; S2 severe and life-threatening, survival probable; S3 life-threatening, survival uncertain, or fatal | Rated for the most exposed person at risk. Pedestrians and cyclists struck at 40 km/h or more are S3; at walking pace to 25 km/h S2 |
| Exposure | E0 incredible to E4 high probability | From the operational situation, by duration or by frequency as the situation's *Basis* says. Frequency is used where a situation is entered on every trip (stops, intersections). In the rated rows, the rarer of the situation's and the condition's exposure (§4.1) |
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
| OS-11 | Passing parked vehicles | 25–30 mph past a row of parked vehicles, doors may open and pedestrians step out between them | E4 | Duration; most urban streets in the geofence have kerbside parking |
| OS-12 | Near a school or playground at school times | Up to 20 mph in a school zone, children on the footway and at crossings | E3 | Duration; school zones on some routes, twice a day on school days |
| OS-13 | On a narrow street without a centre line | Up to 25 mph with oncoming traffic close, parked vehicles narrowing the road | E3 | Duration; residential and collector streets, 1–10 % of operating time |
| OS-14 | Changing lanes on a street with two lanes per direction | 25–30 mph, vehicles and cyclists in the target lane | E3 | Frequency; a few times on most trips |
| OS-15 | Pulling into or out of a kerbside stop across a cycle lane | Up to 15 mph across a cycle lane or bus stop to and from the kerb | E4 | Frequency; twice on every trip |
| OS-16 | At a stop- or yield-controlled junction | Stopping at the line, then pulling out across or into traffic at up to 30 mph, pedestrians crossing | E4 | Frequency; several junctions on every trip |
| OS-17 | Passing a work zone captured in the map | Up to 20 mph through a mapped work zone, workers and cones beside the lane | E2 | Duration; work zones are a small share of operating time |
| OS-18 | An emergency vehicle approaching with siren and lights | Making way for an emergency vehicle from behind or across a junction (OEDR-09) | E2 | Frequency; a few times a month per vehicle |
| OS-19 | Stopped in lane after a minimal risk manoeuvre | Standstill in the lane with hazard lights on (MRC-2), traffic passing, passengers may be leaving (DQ-023 C) | E2 | Frequency; only after faults or ODD exits, rarer than once a month per vehicle |
| OS-20 | Stopped or starting on a gradient | Standstill and start on gradients up to 8 %, vehicles or pedestrians behind | E3 | Frequency; depends on the geofence (DQ-014), rated as some trips |

<!-- END GENERATED: hara-situations -->

### 4.1 Road and light conditions

Each row is rated under each condition across the ODD (WP-C-02 ODD-10 to ODD-13), and one beyond it that a vehicle can meet before the weather monitor ends the trip. Conditions change exposure, not severity: severities are rated at the ODD's speeds, which wet roads and darkness do not raise.

<!-- BEGIN GENERATED: hara-conditions (assurance/02-concept/hara/hara.py) -->

| ID | Condition | Exposure | Basis |
|---|---|---|---|
| W01 | Dry road in daylight | E4 | Most operating time |
| W02 | Wet road or light rain | E3 | Inside the ODD up to 2.5 mm/h (DQ-012 A); 1–10 % of time |
| W03 | Dry road at night under street lighting | E3 | Night service is inside the ODD; 1–10 % of time |
| W04 | Wet road at night | E2 | Both together; under 1 % of time |
| W05 | Visibility near the ODD bound of 200 m (mist | E2 | Under 1 % of time |
| W06 | Heavy rain beyond the ODD before the weather monitor ends the trip | E1 | MON-03 ends the trip; the time spent there is short and rare |

<!-- END GENERATED: hara-conditions -->

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

### 6.1 Functions and malfunction guide words

The fourteen guide words, applied to every function:

<!-- BEGIN GENERATED: hara-guidewords (assurance/02-concept/hara/hara.py) -->

| ID | Guide word | Means |
|---|---|---|
| M01 | No function | Never acts when it should |
| M02 | Stops functioning | Acts at first |
| M03 | Unrequested function | Acts when it should not |
| M04 | Function stuck | Holds its last output and ignores new input |
| M05 | Excessive function | Output larger than intended |
| M06 | Partial function | Output smaller than intended but not zero |
| M07 | Functions early | Acts before its trigger |
| M08 | Functions late | Acts after its trigger has passed |
| M09 | Applies too short | Output lasts shorter than intended |
| M10 | Applies too long | Output lasts longer than intended |
| M11 | Delayed | Acts correctly but with latency beyond its specification |
| M12 | Inverse function | Acts in the opposite direction or sense |
| M13 | Erratic or intermittent | Output oscillates |
| M14 | Uneven | Output asymmetric or non-monotonic |

<!-- END GENERATED: hara-guidewords -->

How each function's pairs were classed. The class, hazard and reason of every pair are in [`hara/guide-words.csv`](hara/guide-words.csv), which opens as a table in the browser.

<!-- BEGIN GENERATED: hara-functions (assurance/02-concept/hara/hara.py) -->

| ID | Function | Safety-related (rated) | Safety-related (folded) | Not safety-related | Not applicable | Hazards reached |
|---|---|---|---|---|---|---|
| F-01 | Localise the vehicle on the HD map | 4 | 5 | 1 | 4 | H-04, H-06 |
| F-02 | Detect and track objects | 3 | 7 | 0 | 4 | H-02, H-03 |
| F-03 | Recognise traffic lights | 1 | 5 | 2 | 6 | H-06 |
| F-04 | Predict the motion of other road users | 3 | 6 | 0 | 5 | H-02, H-03, H-06 |
| F-05 | Plan the route to the destination | 0 | 0 | 8 | 6 | — |
| F-06 | Plan behaviour and motion | 8 | 6 | 0 | 0 | H-01, H-02, H-03, H-04, H-05, H-06, H-07 |
| F-07 | Follow the planned trajectory | 6 | 5 | 1 | 2 | H-01, H-02, H-04, H-05 |
| F-08 | Select and limit the command sent on | 7 | 5 | 0 | 2 | H-01, H-02, H-03, H-07, H-08, H-10 |
| F-09 | Monitor the system and carry out a minimal risk manoeuvre | 4 | 7 | 1 | 2 | H-03, H-05, H-07 |
| F-10 | Bound every command to a safety envelope and stop the vehicle independently | 5 | 3 | 5 | 1 | H-01, H-02, H-03, H-05, H-07 |
| F-11 | Accept trips, mode changes and requests | 1 | 2 | 6 | 5 | H-05 |
| F-12 | Signal intent to other road users | 3 | 7 | 1 | 3 | H-09 |

<!-- END GENERATED: hara-functions -->

Two choices shape the classes. The safety monitor (F-10) failing to bound a command causes no hazard while Autoware works. That is a latent fault, so it is not rated here; WP-H-04 counts it in the hardware metrics. The monitor intervening without reason, releasing a hold too early or commanding the wrong sense is rated. And a wrong route (F-05) is not a malfunction hazard: the planner still drives the route correctly, a route outside the geofence is caught by MON-01, and a route nobody asked for is a security goal (WP-C-10 CG-06).

### 6.2 Every rated hazardous event

<!-- BEGIN GENERATED: hara-counts (assurance/02-concept/hara/hara.py) -->

| Step | Count |
|---|---|
| Functions × guide words (12 × 14) | 168 |
| … safety-related | 103 (45 rated, 58 folded into another with the same effect) |
| … not safety-related | 25 |
| … not applicable | 40 |
| Situations × conditions (20 × 6) | 120 |
| Rated rows (45 × 120) | 5400 |
| … not hazardous in that situation (S0, reason recorded) | 1572 |
| … QM | 425 |
| … ASIL A / B / C / D | 1000 / 1477 / 765 / 161 |
| Distinct hazardous events (hazard × situation, S above S0) | 126 |

<!-- END GENERATED: hara-counts -->

![Figure 6-2: a grid with the ten hazards H-01 to H-10 as rows and the twenty operational situations OS-01 to OS-20 as columns; each filled cell shows the highest ASIL of that hazard in that situation over every function, guide word and condition, shaded from light (A) to dark (D); a cell is empty where the hazard cannot occur in that situation. The worst ASIL of each hazard is in the table below.](hara/fig-c03-6-2-all-events.svg)

*Figure 6-2. Worst ASIL by hazard and situation over every rated row. Drawn by [`hara/hara.py`](hara/hara.py); CI fails if it is stale.*

**To read the rows,** open a hazard's file below. GitHub shows it as a table that can be searched by function, guide word, situation, condition or ASIL, with the reason for every S, E and C. Each row has a stable key, *function/guide word/situation/condition* (for example `F-06/M07/OS-16/W01`), to quote in a review comment.

<!-- BEGIN GENERATED: hara-all-events (assurance/02-concept/hara/hara.py) -->

| Hazard | Rows | Rated A or above | Worst ASIL | Situations where it is worst | Safety goal | Open as a table |
|---|---|---|---|---|---|---|
| H-01 Unintended acceleration | 600 | 575 | **D** | OS-01, OS-03, OS-06, OS-07, OS-09, OS-11, OS-15, OS-16 | SG-01 | [H-01-unintended-acceleration.csv](hara/hazardous-events/H-01-unintended-acceleration.csv) |
| H-02 Insufficient deceleration | 960 | 720 | **D** | OS-01, OS-03, OS-09, OS-11, OS-16 | SG-02 | [H-02-insufficient-deceleration.csv](hara/hazardous-events/H-02-insufficient-deceleration.csv) |
| H-03 Unintended hard deceleration | 720 | 402 | **C** | OS-01, OS-03, OS-04, OS-08, OS-09, OS-11 | SG-03 | [H-03-unintended-hard-deceleration.csv](hara/hazardous-events/H-03-unintended-hard-deceleration.csv) |
| H-04 Unintended lateral motion | 720 | 540 | **D** | OS-01, OS-03, OS-08, OS-09, OS-11 | SG-04 | [H-04-unintended-lateral-motion.csv](hara/hazardous-events/H-04-unintended-lateral-motion.csv) |
| H-05 Unintended motion from standstill | 600 | 160 | **D** | OS-07 | SG-05 | [H-05-unintended-motion-from-standstill.csv](hara/hazardous-events/H-05-unintended-motion-from-standstill.csv) |
| H-06 Proceeding against right of way | 480 | 292 | **D** | OS-03, OS-06, OS-09, OS-16 | SG-06 | [H-06-proceeding-against-right-of-way.csv](hara/hazardous-events/H-06-proceeding-against-right-of-way.csv) |
| H-07 No minimal risk manoeuvre when one is needed | 600 | 465 | **D** | OS-01, OS-03, OS-08, OS-09, OS-11, OS-16 | SG-07 | [H-07-no-minimal-risk-manoeuvre-when-one-is-needed.csv](hara/hazardous-events/H-07-no-minimal-risk-manoeuvre-when-one-is-needed.csv) |
| H-08 Acting on stale or corrupted remote driving commands | 240 | 12 | **C** | OS-10 | SG-08 | [H-08-acting-on-stale-or-corrupted-remote-driving-commands.csv](hara/hazardous-events/H-08-acting-on-stale-or-corrupted-remote-driving-commands.csv) |
| H-09 Wrong signalling | 360 | 207 | **C** | OS-01, OS-03, OS-08, OS-11, OS-15, OS-16 | SG-09 | [H-09-wrong-signalling.csv](hara/hazardous-events/H-09-wrong-signalling.csv) |
| H-10 Unintended reverse motion | 120 | 30 | **C** | OS-06, OS-07, OS-15, OS-16 | SG-05 | [H-10-unintended-reverse-motion.csv](hara/hazardous-events/H-10-unintended-reverse-motion.csv) |

<!-- END GENERATED: hara-all-events -->

### 6.3 Named hazardous events

The events below are the ones the functional safety concept, the fallback concept, the STPA and the scenario catalogue refer to. Each sits on the rows of §6.2, and together they give every safety goal the highest ASIL of its rows.

![Figure 6-1: a grid with the ten hazards H-01 to H-10 as rows and the ten operational situations the named events use, OS-01 to OS-10, as columns; each cell shows the ASIL of the hazardous events rated there, shaded from light (A) to dark (D); where a cell holds two events it shows the higher ASIL and the count. The same ratings are listed in the table below.](hara/fig-c03-6-1-asil-matrix.svg)

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
| HA-6 | Remote driving is limited to 10 km/h (DQ-032 A). The new rows of OS-10 are rated at that speed; the named event HE-08.1 keeps its rating at urban speed, so SG-08 stays ASIL C. Re-rating it at 10 km/h would lower SG-08, which is the safety authority's decision | Safety authority (OI-7) |
| HA-7 | Exposure of the situations added in version 0.4 (OS-11 to OS-20) is estimated without a geofence; school zones, work zones, gradients and stops in lane depend on it | Geofence (DQ-014, WP-C-02 OI-6) |
| HA-5 | The rated minimal risk condition is a stop in lane with hazard lights on; Autoware pulls over to the kerb first when it still can, which is not rated (DQ-016 A). Stops in lane are therefore part of normal operation after faults, and their exposure to rear-end impacts is covered by SG-03 and the fallback concept (WP-C-12) | Decided (DQ-016 A) |

## 9. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Safety authority to accept the ratings and safety goals as a whole before the confirmation review | G1 |
| OI-2 | Re-check every severity once the vehicle is chosen (HA-1, HA-4) | G2 |
| OI-3 | Re-check exposure of OS-05 and OS-10 with the geofence and the remote operations concept (HA-2) | G1 |
| OI-4 | Confirmation review of this HARA by an independent assessor (I3); needs DQ-007 | G1 |
| OI-5 | Cross-check against the SOTIF hazards (WP-C-05) and the STPA (WP-A-05) once drafted, and add any malfunctioning behaviour they find | G1 |
| OI-6 | Independent review of the guide-word classes (§6.1) and the severity rules behind every row (§6.2); both are single-author drafts | G1 |
| OI-7 | Decide whether HE-08.1 is re-rated at the 10 km/h of remote driving (HA-6) | G1 |
