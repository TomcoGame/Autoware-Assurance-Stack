# WP-V-03 Evaluation of known hazardous scenarios

| Field | Value |
|---|---|
| Work product | WP-V-03 Evaluation of known hazardous scenarios |
| Standard reference | UL 4600 §12; ISO 21448 §10; ASPICE 4.0 SYS.5, VAL.1 |
| Version | 0.2 (first content: the scenario catalogue, its logical parameters and pass criteria, generated from `scenarios/scenarios.yaml`; evaluation method; 2026-10-24). 0.1 (skeleton: structure and clause mapping; 2026-10-22) |
| Status | Draft |
| ASIL / scope | SOTIF |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | `2a7707b`; Autoware sources as pinned in `repositories/autoware.repos` (`autoware_core` 1.9.0, `autoware_universe` 0.52.1) |

## 1. Purpose

The known hazardous scenarios of the item, and how each is evaluated (ISO 21448 §10). A known scenario is one the analyses have already found: a triggering condition of [WP-C-06](../02-concept/WP-C-06-sotif-insufficiencies-triggering-conditions.md), a misuse or interaction of [WP-C-08](../02-concept/WP-C-08-human-interaction-misuse-analysis.md), a hazardous event of [WP-C-03](../02-concept/WP-C-03-hara.md) or a loss scenario of [WP-A-05](../08-analyses/WP-A-05-stpa.md). Unknown scenarios are searched for in [WP-V-04](WP-V-04-sotif-unknown-scenarios.md).

Needed at gate G4 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: scenarios-summary (assurance/06-validation/scenarios/scenarios.py) -->

26 logical scenarios exercise all 29 triggering conditions of WP-C-06, all 23 misuse and interaction entries of WP-C-08 and all 19 hazardous events of WP-C-03. Their parameters take only values WP-C-02 states; 10 behaviour parameters wait on the bounds that FSR-06.01, FSR-06.02, FSR-08.01 state but no work product has fixed yet. 4 scenarios (SC-10, SC-11, SC-14, SC-20) cross the ODD boundary to test a monitor. Each pass criterion is judged against existing requirements. No scenario has been run.

<!-- END GENERATED: scenarios-summary -->

**The catalogue is drafted before the vehicle is chosen (DQ-008), and nothing in it has been run.** It uses no measured value: every range comes from the ODD of [WP-C-02](../02-concept/WP-C-02-odd-and-intended-functionality.md), and every pass criterion points at a requirement that already exists. Where a requirement says the item assumes a bound on how other road users move (FSR-06.01, FSR-06.02) but no work product has fixed the bound, the parameter is listed without a number.

The model is kept in `scenarios/scenarios.yaml`; `scenarios/scenarios.py` checks it and writes the tables below and the coverage tables and Figure 4-1 of [WP-V-08](WP-V-08-simulation-credibility.md#4-scenario-coverage-metrics-against-the-odd). The generator refuses a triggering condition, misuse entry or hazardous event that no scenario exercises, a reference to an identifier that does not exist, and a parameter outside the ODD.

## 2. Scenario catalogue

Each scenario is a *logical* scenario in the terms of ISO 34501: a functional description with parameter ranges. Running it means sampling *concrete* scenarios from the ranges (§3). The structure maps onto OpenSCENARIO: a parameter becomes a parameter declaration with its range as a constraint, a participant class becomes an entity of the matching category ([WP-V-08 §2](WP-V-08-simulation-credibility.md)). The YAML stays the source; an exporter to OpenSCENARIO 2 or to the format scenario_simulator_v2 reads is future work (OI-2).

The safety goals at stake are computed, not typed: the goals of the hazards of a scenario's hazardous events, and those of the HARA hazards its triggering conditions can lead to, through the insufficiencies they expose (WP-C-06) and the SOTIF hazards those cause ([WP-C-05](../02-concept/WP-C-05-sotif-hazard-identification.md)).

### 2.1 Scenarios and what they exercise

<!-- BEGIN GENERATED: scenarios-catalogue (assurance/06-validation/scenarios/scenarios.py) -->

| Scenario | Situations | Manoeuvres and OEDR | Hazardous events | Triggering conditions | Misuse | Loss scenarios | Goals at stake | Methods |
|---|---|---|---|---|---|---|---|---|
| SC-01 Pedestrian on or stepping onto a marked crosswalk | OS-09 | OEDR-03 | HE-02.1, HE-06.4 | TC-02, TC-03, TC-15 | MU-11 | LS-01, LS-02 | SG-02, SG-03, SG-06 | Simulation, Track, Road |
| SC-02 Pedestrian emerging from behind a parked vehicle | OS-02, OS-01 | OEDR-04, OEDR-08 | HE-04.3 | TC-10, TC-17 | MU-10 | LS-01, LS-02 | SG-02, SG-04, SG-06 | Simulation, Track |
| SC-03 Vehicle ahead braking or stopping in congested traffic | OS-08, OS-01 | OEDR-01 | HE-01.2, HE-02.2 | TC-11, TC-25 | MU-14 | LS-03, LS-04 | SG-01, SG-02, SG-04, SG-06 | Simulation, In the loop, Track |
| SC-04 Spurious obstacle with a road user following | OS-01 | OEDR-01, OEDR-11 | HE-03.1, HE-03.2 | TC-03, TC-04, TC-24 | MU-04, MU-07 | LS-08, LS-19 | SG-02, SG-03 | Simulation, Track |
| SC-05 Signalised intersection with cross traffic | OS-03 | MAN-03, OEDR-05, OEDR-07 | HE-06.1 | TC-01, TC-06, TC-07, TC-19 | — | LS-01, LS-02 | SG-02, SG-06 | Simulation, Track, Road |
| SC-06 Unprotected left turn across oncoming traffic | OS-04 | MAN-04, OEDR-07, OEDR-08 | HE-06.2 | TC-12, TC-20 | — | LS-02 | SG-02, SG-06 | Simulation, Track |
| SC-07 Entry to a roundabout with traffic circulating | OS-05 | MAN-05, OEDR-06, OEDR-07 | HE-06.3 | TC-13 | — | LS-02 | SG-02, SG-06 | Simulation, Track |
| SC-08 Cyclist alongside on the inside of a turn | OS-01, OS-03 | MAN-03, OEDR-04, OEDR-12 | HE-04.2 | TC-18 | MU-13 | LS-02 | SG-02, SG-04, SG-06 | Simulation, Track |
| SC-09 Lane keeping where localisation is degraded | OS-01, OS-02 | MAN-01, OEDR-12 | HE-04.1, HE-04.3 | TC-08, TC-11 | — | LS-05 | SG-02, SG-04, SG-06 | Simulation, Road |
| SC-10 Work zone or re-marked lanes not yet in the map | OS-01 | MAN-01, MAN-07, OEDR-11 | — | TC-09 | — | LS-14 | SG-04, SG-06 | Simulation, Track |
| SC-11 Person directing traffic | OS-03 | MAN-07, OEDR-10 | — | TC-22 | MU-20 | — | SG-06 | Simulation, Track, Drill |
| SC-12 Emergency vehicle approaching with siren and lights | OS-01, OS-03 | MAN-07, MAN-10, OEDR-09 | — | TC-21 | — | — | SG-06 | Simulation, Track |
| SC-13 Rare object or debris in the lane | OS-01 | OEDR-11, OEDR-02 | — | TC-15, TC-16 | MU-12 | LS-01 | SG-02, SG-03 | Simulation, Track |
| SC-14 Weather changing toward the ODD limits during a trip | OS-01 | MAN-07, MAN-10 | — | TC-05, TC-28 | — | LS-07, LS-27 | SG-02, SG-03, SG-06, SG-07 | Simulation, Road |
| SC-15 Kerbside stop while passengers board or alight | OS-07 | MAN-06 | HE-05.1, HE-10.1 | — | MU-01, MU-08, MU-19 | LS-12, LS-16, LS-20 | SG-05 | Simulation, Bench, Track |
| SC-16 Stopped at a red light with pedestrians crossing in front | OS-06 | OEDR-03, OEDR-05 | HE-01.1, HE-05.2 | — | — | LS-20, LS-21 | SG-01, SG-05 | In the loop, Bench, Track |
| SC-17 Loss of Autoware while driving | OS-01 | MAN-07 | HE-07.1 | — | MU-15 | LS-03, LS-06, LS-18, LS-22 | SG-07 | In the loop, Track |
| SC-18 Pull-over minimal risk manoeuvre along a busy kerb | OS-01 | MAN-10, MAN-07 | — | TC-14 | MU-03 | LS-25 | — | Simulation, Track |
| SC-19 Passengers leaving at a stop in lane | OS-01 | MAN-07 | — | TC-29 | MU-02 | LS-23 | SG-07 | Simulation, Drill |
| SC-20 Remote driving with a delayed or lost link | OS-10 | — | HE-08.1 | TC-26, TC-27 | MU-17, MU-18 | LS-09, LS-10, LS-11, LS-26 | SG-08 | Simulation, In the loop, Drill |
| SC-21 Remote release of the wrong vehicle or at the wrong moment | OS-07, OS-06 | — | — | — | MU-16 | LS-12, LS-13 | — | Bench, Drill |
| SC-22 Turn indicator during a turn or lane change | OS-01 | MAN-02, MAN-03, OEDR-02 | HE-09.1 | — | — | LS-17 | SG-09 | Simulation, In the loop |
| SC-23 Give and take with other drivers | OS-03, OS-08 | OEDR-06, OEDR-07 | — | TC-23 | — | — | SG-03 | Simulation, Road |
| SC-24 Passenger misuse and emergencies in the cabin | OS-01, OS-07 | — | — | — | MU-05, MU-06, MU-09 | — | — | Bench, Drill |
| SC-25 First responders at a collision | OS-01 | MAN-07 | — | — | MU-21 | LS-24 | — | Bench, Drill |
| SC-26 Return to service after maintenance | OS-01 | — | — | — | MU-22, MU-23 | LS-15 | — | Bench, Drill |

<!-- END GENERATED: scenarios-catalogue -->

### 2.2 Logical parameters

A range on an ODD attribute stays inside the limits WP-C-02 states; ego speed is also capped by the posted limit (ODD-03, 30 mph or 48 km/h). Values marked *outside*, and ranges swept *across the limit*, appear only in the scenarios that test an ODD monitor; how far past the limit they go is set when the monitor's requirements are written (WP-C-02 OI-4), not here.

<!-- BEGIN GENERATED: scenarios-parameters (assurance/06-validation/scenarios/scenarios.py) -->

| Scenario | Parameter | Range or values | Source |
|---|---|---|---|
| SC-01 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-03 Posted speed limit | up to 30 mph | WP-C-02 ODD-03 |
|  | ODD-05 Crossings | marked-crosswalk, signalised-crosswalk | WP-C-02 ODD-05 |
|  | ODD-16 Traffic participants | pedestrian, child, wheelchair | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, dusk, night, unlit | WP-C-02 ODD-12 |
|  | ODD-10 Precipitation | 0 to 2.5 mm/h | WP-C-02 ODD-10 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
|  | Pedestrian walking speed and start time | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-02 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-05 Crossings | mid-block | WP-C-02 ODD-05 |
|  | ODD-16 Traffic participants | pedestrian, child, bicycle, e-scooter | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, night, unlit | WP-C-02 ODD-12 |
|  | ODD-02 Road type | urban-street, lanes-1-2 | WP-C-02 ODD-02 |
|  | Speed of the road user emerging from the occlusion | Bound stated by FSR-06.02, not yet fixed | FSR-06.02 |
| SC-03 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-03 Posted speed limit | up to 30 mph | WP-C-02 ODD-03 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-16 Traffic participants | car, van, bus, truck, motorcycle | WP-C-02 ODD-16 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
|  | ODD-10 Precipitation | 0 to 2.5 mm/h | WP-C-02 ODD-10 |
|  | Deceleration of the lead vehicle and cut-in gap | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-04 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-10 Precipitation | 0 to 2.5 mm/h | WP-C-02 ODD-10 |
|  | ODD-11 Visibility | 200 m and above | WP-C-02 ODD-11 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
|  | ODD-16 Traffic participants | car, motorcycle | WP-C-02 ODD-16 |
|  | Gap of the following road user | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-05 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-04 Junctions | signalised, protected-turn | WP-C-02 ODD-04 |
|  | ODD-12 Illumination | day, low-sun, night | WP-C-02 ODD-12 |
|  | ODD-16 Traffic participants | car, truck, motorcycle, bicycle | WP-C-02 ODD-16 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | Speed of the crossing vehicle running the red | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-06 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-04 Junctions | signalised, unprotected-turn, stop-controlled, t-junction | WP-C-02 ODD-04 |
|  | ODD-16 Traffic participants | car, van, truck, motorcycle, bicycle | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, dusk, night | WP-C-02 ODD-12 |
|  | Speed and acceleration of the oncoming vehicle | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-07 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-04 Junctions | roundabout-single, roundabout-multi, yield-controlled | WP-C-02 ODD-04 |
|  | ODD-16 Traffic participants | car, bus, truck, motorcycle, bicycle | WP-C-02 ODD-16 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | Speed of circulating vehicles | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-08 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-05 Crossings | cycle-lane | WP-C-02 ODD-05 |
|  | ODD-16 Traffic participants | bicycle, e-scooter | WP-C-02 ODD-16 |
|  | ODD-04 Junctions | signalised, stop-controlled, t-junction | WP-C-02 ODD-04 |
|  | Cyclist speed and lateral motion | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-09 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-01 Area | geofence | WP-C-02 ODD-01 |
|  | ODD-02 Road type | urban-street, collector, centre-line | WP-C-02 ODD-02 |
|  | ODD-03 Posted speed limit | up to 30 mph | WP-C-02 ODD-03 |
|  | ODD-07 Lane markings | markings-visible, markings-absent | WP-C-02 ODD-07 |
|  | ODD-08 Temporary changes | none, captured | WP-C-02 ODD-08 |
|  | ODD-15 Connectivity | gnss-lost | WP-C-02 ODD-15 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-06 Road surface and geometry | 0 to 8 % | WP-C-02 ODD-06 |
| SC-10 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-07 Lane markings | re-marking (outside) | WP-C-02 ODD-07 |
|  | ODD-08 Temporary changes | work-zone (outside) | WP-C-02 ODD-08 |
|  | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
| SC-11 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-19 Traffic direction by people | directing (outside) | WP-C-02 ODD-19 |
|  | ODD-04 Junctions | signalised, stop-controlled | WP-C-02 ODD-04 |
|  | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
| SC-12 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-18 Special vehicles | emergency-vehicle | WP-C-02 ODD-18 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-04 Junctions | signalised, t-junction | WP-C-02 ODD-04 |
|  | Speed of the emergency vehicle | Bound stated by FSR-06.01, not yet fixed | FSR-06.01 |
| SC-13 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-16 Traffic participants | animal, e-scooter, wheelchair | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, night, unlit | WP-C-02 ODD-12 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
| SC-14 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-10 Precipitation | 0 to 2.5 mm/h, and across the limit | WP-C-02 ODD-10 |
|  | ODD-11 Visibility | 200 m and above, and across the limit | WP-C-02 ODD-11 |
|  | ODD-12 Illumination | day, dusk, night | WP-C-02 ODD-12 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
|  | ODD-16 Traffic participants | car, pedestrian, bicycle | WP-C-02 ODD-16 |
| SC-15 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-09 Stopping places | kerbside-stop | WP-C-02 ODD-09 |
|  | ODD-16 Traffic participants | pedestrian, child, wheelchair, bicycle | WP-C-02 ODD-16 |
|  | ODD-06 Road surface and geometry | 0 to 8 % | WP-C-02 ODD-06 |
| SC-16 | ODD-04 Junctions | signalised | WP-C-02 ODD-04 |
|  | ODD-05 Crossings | marked-crosswalk, signalised-crosswalk | WP-C-02 ODD-05 |
|  | ODD-06 Road surface and geometry | 0 to 8 % | WP-C-02 ODD-06 |
|  | ODD-16 Traffic participants | pedestrian, child, wheelchair | WP-C-02 ODD-16 |
|  | ODD-13 Road surface condition | dry, wet | WP-C-02 ODD-13 |
| SC-17 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-02 Road type | urban-street, centre-line | WP-C-02 ODD-02 |
|  | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
| SC-18 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-05 Crossings | cycle-lane, marked-crosswalk | WP-C-02 ODD-05 |
|  | ODD-09 Stopping places | kerbside-stop | WP-C-02 ODD-09 |
|  | ODD-18 Special vehicles | bus-at-stop | WP-C-02 ODD-18 |
|  | ODD-16 Traffic participants | bicycle, pedestrian | WP-C-02 ODD-16 |
| SC-19 | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-16 Traffic participants | car, bicycle, motorcycle | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
| SC-20 | ODD-20 Ego speed | 0 to 10 km/h | WP-C-02 ODD-20 |
|  | ODD-15 Connectivity | link-available, link-lost (outside) | WP-C-02 ODD-15 |
|  | ODD-16 Traffic participants | pedestrian, bicycle, car | WP-C-02 ODD-16 |
|  | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
|  | Age of remote commands | Bound stated by FSR-08.01, not yet fixed | FSR-08.01 |
| SC-21 | ODD-15 Connectivity | link-available | WP-C-02 ODD-15 |
|  | ODD-09 Stopping places | kerbside-stop | WP-C-02 ODD-09 |
| SC-22 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-02 Road type | lanes-1-2 | WP-C-02 ODD-02 |
|  | ODD-16 Traffic participants | car, bicycle, pedestrian | WP-C-02 ODD-16 |
| SC-23 | ODD-20 Ego speed | 0 to 48 km/h | WP-C-02 ODD-20 |
|  | ODD-04 Junctions | stop-controlled, yield-controlled, t-junction | WP-C-02 ODD-04 |
|  | ODD-17 Traffic density | free-flow, congested | WP-C-02 ODD-17 |
|  | ODD-16 Traffic participants | car, van, bicycle, pedestrian | WP-C-02 ODD-16 |
| SC-24 | ODD-15 Connectivity | link-available | WP-C-02 ODD-15 |
| SC-25 | ODD-12 Illumination | day, night | WP-C-02 ODD-12 |
|  | ODD-15 Connectivity | link-available | WP-C-02 ODD-15 |
| SC-26 | ODD-14 Temperature | in-range | WP-C-02 ODD-14 |

<!-- END GENERATED: scenarios-parameters -->

### 2.3 Pass criteria

A pass criterion says what must hold in every concrete scenario, in the words of the requirements it is judged against. The generator refuses a scenario in which a safety goal is at stake but no functional safety requirement of that goal is among its references, and a scenario with a triggering condition that cites no SOTIF acceptance criterion: its residual rate is what counts against AC-02.

<!-- BEGIN GENERATED: scenarios-pass (assurance/06-validation/scenarios/scenarios.py) -->

| Scenario | Pass criterion | Judged against |
|---|---|---|
| SC-01 | No contact with the pedestrian; the vehicle yields as the traffic rules require, and the monitor commands the deceleration that restores the safe distance whenever Autoware does not; unjustified hard braking counts against the SOTIF acceptance criteria | FSR-02.01, FSR-02.02, FSR-02.05, FSR-03.01, FSR-06.01, FSR-06.03, AC-02 |
| SC-02 | The vehicle's speed near the occlusion lets it stop for a road user emerging at the assumed speed; no contact, and no swerve out of the drivable area to avoid one | FSR-06.02, FSR-02.02, FSR-04.01, FSR-04.05, FSR-03.01, AC-02 |
| SC-03 | No collision with the vehicle ahead; acceleration stays inside the envelope, the monitor restores the safe longitudinal distance, and a braking shortfall on a wet road switches to the secondary path | FSR-01.01, FSR-01.02, FSR-02.02, FSR-02.03, FSR-02.05, FSR-03.02, FSR-04.05, FSR-06.01, AC-02 |
| SC-04 | Braking that the safety channel does not confirm stays at or below the firm level; emergency braking happens only when a road user is confirmed; a blocked safety sensor is detected and Autoware stops comfortably; the belt warning acts | FSR-03.01, FSR-03.02, FSR-03.03, FSR-02.01, FSR-07.08, FM-10, HR-03, AC-02 |
| SC-05 | The vehicle enters only on a recognised green and treats an unknown signal as red; whatever the signal, it does not enter when its swept path crosses that of a detected road user before it could stop or clear | FSR-06.01, FSR-06.03, FSR-02.01, FSR-02.02, FSR-03.01, FM-05, AC-02 |
| SC-06 | The vehicle starts the turn only with a gap that lets the oncoming road user pass at its assumed speed and acceleration, and stops before the conflict area otherwise | FSR-06.01, FSR-06.02, FSR-06.03, FSR-02.02, FSR-03.01, FM-07, AC-02 |
| SC-07 | The vehicle yields to circulating traffic and enters only with a gap that its assumed speed allows | FSR-06.01, FSR-06.03, FSR-02.02, FM-07, AC-02 |
| SC-08 | No steering command whose swept path comes within the safe lateral distance of the cyclist is executed; the vehicle waits or stops in lane | FSR-04.01, FSR-04.05, FSR-06.01, FSR-02.02, FSR-03.01, FM-06, AC-02 |
| SC-09 | The vehicle stays in its lane and drivable area; a steering command toward a detected road user or kerb is rejected and the vehicle stops in lane; a degraded pose is detected | FSR-04.01, FSR-04.02, FSR-04.03, FSR-04.05, FSR-02.02, FSR-03.01, FSR-06.01, FM-09, AC-02 |
| SC-10 | The divergence monitor detects the disagreement and the vehicle carries out a minimal risk manoeuvre; it never follows the map into a closed lane | MON-02, FSR-07.05, FSR-04.01, FSR-02.02, FSR-06.01, FSR-06.03, TR-09, FM-13, AC-02 |
| SC-11 | The vehicle detects the person directing traffic, stops safely and asks for remote assistance; it does not move on the signal alone, and responders can stop or hold it | MON-02, FSR-07.05, FSR-06.01, FSR-02.02, FM-16, HR-08, AC-02 |
| SC-12 | The vehicle detects the emergency vehicle, pulls to the side when safe or stops, and lets it pass; when it cannot yield it reaches a minimal risk condition | FSR-06.01, FSR-06.03, FSR-07.05, FSR-02.02, FM-15, TR-14, AC-02 |
| SC-13 | The vehicle stops before the object or passes it within the lane when clear; a vehicle that cannot find a way on reaches a minimal risk condition and asks for help | FSR-02.01, FSR-02.02, FSR-03.01, FM-03, TR-14, SR-01, AC-02 |
| SC-14 | The weather monitor detects the exit, treats a reading it cannot tell from the limit as outside, and the vehicle reaches a minimal risk condition; detection inside the ODD still meets the safety channel's requirement | MON-03, FSR-07.05, FSR-02.01, FSR-02.02, FSR-03.01, FSR-06.01, TR-10, SR-07, AC-02 |
| SC-15 | The vehicle does not move with a door open or a person in the near field in the direction of travel, never reverses, and resumes only when every release condition holds | FSR-05.01, FSR-05.03, FSR-05.05, FSR-07.04, HR-04 |
| SC-16 | The vehicle stays held until every release condition holds; motion while holding is detected and the park brake applied; no acceleration toward a detected road user | FSR-05.01, FSR-05.02, FSR-05.04, FSR-01.01, FSR-01.02 |
| SC-17 | The monitor detects the loss within its detection budget and stops the vehicle in lane with hazard lights on, without Autoware; a fault of the monitor itself leads to the vehicle's own stop, never to the park brake while moving | FSR-07.01, FSR-07.02, FSR-07.06, FSR-07.07, FSR-01.01, FSR-02.02, FSR-04.01, TR-01, SR-01, SR-04 |
| SC-18 | The vehicle pulls over only into a mapped safe stopping place and stops in lane otherwise; repeated stop requests go to a remote operator | FSR-07.05, FSR-04.01, FSR-02.02, MRM-1, FM-19, HR-01, AC-02 |
| SC-19 | The vehicle holds the minimal risk condition with hazard lights on and warns passengers of traffic on their side before they leave; the residual risk counts against the SOTIF acceptance criteria | FSR-07.02, FSR-07.04, FM-20, AC-02 |
| SC-20 | Commands older than the age bound, out of sequence or failing their integrity check are rejected and the vehicle stops; the envelope checks apply to remote commands as to Autoware's; a remote emergency stop brakes firmly unless the safety channel confirms a road user | MON-04, FSR-07.05, FSR-08.01, FSR-08.02, FSR-08.03, FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01, FSR-07.01, FSR-03.01, SR-06, FM-11, AC-02 |
| SC-21 | A release moves the vehicle only when it is bound to that vehicle, authentic and fresh, and the release conditions hold | FSR-07.04, FSR-05.01, SR-02, CSR-01, HR-07 |
| SC-22 | The indicator always matches the commanded and achieved steering direction; on a mismatch hazard lights come on | FSR-09.01, FSR-04.01 |
| SC-23 | The vehicle takes its turn as the rules give it and shows when it yields and when it is about to move; its hesitations and stops count against the SOTIF acceptance criteria | FSR-06.01, FSR-06.03, FSR-03.02, FM-17, HR-06, AC-02 |
| SC-24 | No control is reachable from the cabin; every seat reaches a remote operator who can divert the vehicle; no trip ends with a person inside without an operator's decision | AOU-07, HR-02, HR-05 |
| SC-25 | The vehicle stops and holds after a collision; doors open from inside without power; responders can find the isolation points and reach remote operations | TR-15, MRM-3, SR-05, HR-08, HR-09 |
| SC-26 | The vehicle refuses driverless dispatch until calibration, cleanliness and versions are checked and recorded; parameter changes outside the release process are rejected | HR-10, AOU-08, SR-03, CR-03, CSR-05 |

<!-- END GENERATED: scenarios-pass -->

## 3. Evaluation method

| Step | What is done | Where it is recorded |
|---|---|---|
| Sample | Concrete scenarios are drawn from each logical scenario's ranges: the corners of every range, combinations that pair triggering conditions, and a random sample over the rest. The sampling plan and the number of samples follow from the validation targets of [WP-V-02](WP-V-02-sotif-vv-strategy.md) | WP-V-02, this document §4 |
| Choose the method | Each scenario lists the methods it needs. Simulation covers the breadth of the ranges; track tests confirm the corners and the cases simulation cannot yet represent credibly; road driving in the ODD confirms exposure; bench, in-the-loop and drill cover what has no driving scene | §2.1, [WP-V-08 §3](WP-V-08-simulation-credibility.md#3-simulation-validation-against-vehicle-data) |
| Run | Every run is tied to a released configuration (software, maps, models, parameters) and a recorded scenario version | [WP-P-01](../07-supporting/WP-P-01-configuration-management-plan.md) |
| Judge | The pass criterion is applied to each run. A failed run is a problem report and, if it shows a new insufficiency or triggering condition, an update to WP-C-06 | [WP-P-03](../07-supporting/WP-P-03-problem-resolution.md) |
| Count | Residual hazardous behaviour per SOTIF hazard is counted against its share of AC-01 (AC-02), with the exposure from road driving | WP-V-02 |

Simulation results count as evidence only as far as [WP-V-08](WP-V-08-simulation-credibility.md) shows the simulator credible for the scenario; how much credit simulation may take at all is a question for the lead, asked in the decision register (DQ-036).

## 4. Results

None yet. No scenario has been sampled or run; the simulators and the vehicle are not set up (WP-V-08, DQ-008).

## 5. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Fix the behaviour bounds that FSR-06.01 and FSR-06.02 state (WP-S-02), then give those parameters ranges | G2 |
| OI-2 | Write the exporter from `scenarios.yaml` to the scenario format of the chosen simulator, generated and checked like the tables | G2 |
| OI-3 | Set how far beyond the ODD limit the boundary scenarios (SC-10, SC-11, SC-14, SC-20) sweep, with the monitors' requirements (WP-C-02 OI-4) | G2 |
| OI-4 | Write the sampling plan per scenario from the validation targets of WP-V-02 | G3 |
| OI-5 | Run the catalogue and record the results in §4 | G4 |
