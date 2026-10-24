# WP-S-09 System verification specification and report

| Field | Value |
|---|---|
| Work product | WP-S-09 System verification specification and report |
| Standard reference | UL 4600 §12; ISO 26262-4 §7; ISO 21448 §10; ASPICE 4.0 SYS.5 |
| Version | 0.2 (first content: verification strategy, and a specification covering every functional safety requirement, triggering condition and functional modification, generated from `verif/verif.yaml`; 2026-10-24). 0.1 (skeleton: structure and clause mapping; 2026-10-22) |
| Status | Draft |
| ASIL / scope | ASIL D |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

How the integrated item is verified against what it must do as a whole:

- the functional safety requirements of [WP-C-04](../02-concept/WP-C-04-functional-safety-concept.md), and through them the safety goals of [WP-C-03](../02-concept/WP-C-03-hara.md) (ISO 26262-4 §7);
- the SOTIF measures: the known triggering conditions of [WP-C-06](../02-concept/WP-C-06-sotif-insufficiencies-triggering-conditions.md), the functional modifications of [WP-C-07](../02-concept/WP-C-07-sotif-functional-modifications.md), and the known scenarios of [WP-V-03](../06-validation/WP-V-03-sotif-known-scenarios.md) that exercise them (ISO 21448 §10);
- the system requirements of [WP-S-01](WP-S-01-system-requirements.md), once written (ASPICE SYS.5; OI-1).

[WP-S-08](WP-S-08-system-integration-test.md) shows that the technical requirements hold as the parts are put together. This work product verifies the item in its environments once they are. Whether the residual risk is acceptable in the ODD is validation, in 06-validation.

Needed at gate G4 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)). This version is the strategy and specification. Results follow when the item exists.

<!-- BEGIN GENERATED: verif-summary (assurance/03-system/verif/verif.py) -->

20 verification cases cover all 39 functional safety requirements of the 9 safety goals, each the way WP-C-04 says it is to be verified, all 29 triggering conditions and all 20 functional modifications, and run 23 of the 26 known scenarios of WP-V-03 (the other 3, SC-24, SC-25, SC-26, are bench and operations exercises of validation, WP-V-07). No case has been run.

<!-- END GENERATED: verif-summary -->

The model is kept in `verif/verif.yaml`; `verif/verif.py` checks it and writes the tables and Figure 2-1. It refuses a model in which:

- a functional safety requirement, triggering condition or functional modification is verified by no case;
- a requirement is not verified the way WP-C-04 says it is to be: if WP-C-04 names fault injection, a time measurement, supplier evidence, a scenario test, a review, a formal check, an interface or performance test, or simulation, HIL or the vehicle, a case covering it must use that method or environment;
- a case runs a scenario its environment cannot run, or claims a requirement of an element that does not act in it (the monitor in VC-01);
- a known scenario that simulation, HIL or the track can run is run by no case.

## 2. Verification strategy

A case verifies what it names and, through each WP-V-03 scenario it runs, the requirements and modifications that scenario's pass criterion refers to and the triggering conditions it varies. The scenarios are specified once, in WP-V-03, and not repeated here.

The cases build up in four kinds:

1. **The nominal function on its own (VC-01).** Autoware drives the known scenarios in simulation with the monitor recording but not acting. Each run in which the monitor would have acted is a finding against the nominal function, and the count feeds the SOTIF evaluation of WP-V-03.
2. **The integrated item over the known scenarios (VC-02, VC-03).** The same scenarios with the monitor acting, in simulation and then on the closed track. The difference from VC-01 shows what the safety channel and envelope add (FM-02). The track runs the corners of each scenario's parameter ranges and the worst runs simulation found. Simulation takes credit only where WP-V-08 §3 has checked it against the vehicle (DQ-036 A).
3. **Each safety goal's requirements, by the method WP-C-04 names (VC-04 to VC-17).** Fault injection, time measurement against the fault tolerant time intervals of [WP-S-04](WP-S-04-timing-ftti-budget.md), performance tests of the safety channel, a formal check of the monitor's rules, and supplier evidence for the vehicle's elements under the development interface agreement. Faults that would be dangerous on the road are injected on the HIL bench first, and in the vehicle only on a closed track up to 50 km/h (DQ-038 A).
4. **The ODD boundary and the measures checked by review (VC-18 to VC-20).** The ODD monitors as scenarios sweep to the boundary, and the measures a test cannot show: the training data, the route preference, the restart logic and the monitor's diagnostic coverage.

A case in the vehicle starts only when the WP-S-08 cases at step IS-4 that cover the same parts have passed.

![WP-S-09 Figure 2-1: a grid with the verification cases VC-01 to VC-20 as rows and, as columns, the nine safety goals SG-01 to SG-09 with their ASIL, then the triggering conditions and the functional modifications. A cell is filled where the case covers functional safety requirements of that goal, shaded by their highest ASIL (dark for D, lighter for C, outlined for QM), or blue for triggering conditions and modifications; the number in it counts what the case covers in that column. The same coverage is in the tables of §3.](verif/fig-s09-2-1-coverage.svg)

*Figure 2-1. What each verification case verifies. Generated by `verif/verif.py` from `verif/verif.yaml`.*

## 3. Test specification

### 3.1 Environments

The environments are those of WP-S-08 §3. Each runs the scenarios of WP-V-03 marked for it:

<!-- BEGIN GENERATED: verif-environments (assurance/03-system/verif/verif.py) -->

| Environment (WP-S-08) | Runs scenarios marked | Cases |
|---|---|---|
| ENV-1 Software in the loop | sim | VC-01, VC-02, VC-08, VC-18 |
| ENV-2 Hardware in the loop | xil, bench | VC-04, VC-15, VC-16 |
| ENV-3 Sensor bench and closed track | bench | VC-07 |
| ENV-4 Vehicle on a closed track | track | VC-03, VC-05, VC-06, VC-09, VC-10, VC-11, VC-12, VC-14, VC-17 |
| No environment (review, formal check) | — | VC-13, VC-19, VC-20 |

<!-- END GENERATED: verif-environments -->

### 3.2 Verification cases

<!-- BEGIN GENERATED: verif-cases (assurance/03-system/verif/verif.py) -->

| ID | Verification case | Environment | Methods | ASIL | Scenarios run | Also covers | Pass criterion |
|---|---|---|---|---|---|---|---|
| VC-01 | Nominal driving with the monitor in shadow mode | ENV-1 | scenario, requirements | QM | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-09, SC-10, SC-11, SC-12, SC-13, SC-14, SC-18, SC-22, SC-23 | FM-04, FM-12, FM-18, FSR-01.04, FSR-02.05, FSR-04.05, FSR-06.03, FSR-07.05 | Autoware alone, with the monitor recording but not acting, meets each scenario's pass criterion over its concrete runs; every run in which the monitor would have intervened is a finding against the nominal function, counted for WP-V-03 |
| VC-02 | The integrated item over the known scenarios in simulation | ENV-1 | scenario | D | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-09, SC-10, SC-11, SC-12, SC-13, SC-14, SC-15, SC-18, SC-19, SC-20, SC-22, SC-23 | FM-02 | With the monitor acting, every concrete run meets its scenario's pass criterion; the runs VC-01 failed and this case passes show what the safety channel and envelope (FM-02) add. A run counts as evidence only where WP-V-08 §3 has checked the simulator for its attributes (DQ-036 A) |
| VC-03 | The known scenarios on the closed track | ENV-4 | scenario, requirements | D | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-10, SC-11, SC-12, SC-13, SC-15, SC-16, SC-17, SC-18 | FM-12, FSR-01.04, FSR-02.05, FSR-04.05, FSR-06.03, FSR-07.05 | Concrete runs at the corners of each scenario's parameter ranges, and the worst runs VC-02 found, meet their pass criteria with soft targets, including on the wet surface of TC-25; each result agrees with its run in VC-02 within the tolerance WP-V-08 §3 sets, or the disagreement is a finding against the simulator |
| VC-04 | The envelope over its whole range on the HIL bench | ENV-2 | requirements, fault-injection, timing | D | — | FSR-01.01, FSR-02.02, FSR-04.02 | Commanded and injected acceleration, deceleration and steering over the whole speed range and the corners of P-01, P-05, P-06 and P-10 are bounded as the envelope requires, at speeds and fault combinations the track cannot reach safely |
| VC-05 | Acceleration bounded and propulsion cut in the vehicle | ENV-4 | requirements, fault-injection, timing, scenario | D | SC-03, SC-16 | FSR-01.01, FSR-01.02 | Every injected acceleration command beyond the envelope is bounded (P-01, P-06); an injected propulsion fault that drives acceleration above the bounded command beyond P-11 is detected, propulsion cut and the vehicle braked to standstill within the fault tolerant time interval of SG-01 (WP-S-04) |
| VC-06 | Deceleration and the secondary brake path in the vehicle | ENV-4 | requirements, fault-injection, timing, scenario | D | SC-01, SC-03, SC-13 | FSR-02.02, FSR-02.03 | With Autoware's braking withheld, the monitor restores the safe distance (P-05, P-06) in every run; an injected fault of the primary brake path is detected within P-11 and the secondary path stops the vehicle within the fault tolerant time interval of SG-02 (WP-S-04) |
| VC-07 | Detection performance of the safety channel across the ODD | ENV-3 | performance, fault-injection | D | — | FM-10, FSR-02.01, TC-01, TC-02, TC-03, TC-04, TC-05, TC-24 | Reference targets down to the smallest object of P-12 are detected out to its range with the probability WP-V-02 sets, in each light and weather condition of ODD-10 to ODD-13; soiled, wet and blocked sensors and injected sensor faults are reported to the monitor (FM-10) |
| VC-08 | False detections of the safety channel over recorded data | ENV-1 | performance, review | C | — | FSR-03.01, FSR-03.03 | Replayed over recorded drives in the ODD of the length WP-V-02 sets, false detections in the swept path stay below P-13 for each sensor and the channel, at the confidence WP-V-02 sets; the review of the intervention logic finds no path to an emergency-level stop that FSR-02.02 does not require |
| VC-09 | Spurious braking with a road user following | ENV-4 | fault-injection, scenario | D | SC-04 | FSR-03.02 | Injected spurious hard braking from Autoware that the safety channel does not confirm is limited to the firm level of P-05; the following vehicle in SC-04 keeps a gap in every run |
| VC-10 | Steering envelope and lateral monitoring in the vehicle | ENV-4 | fault-injection, scenario, timing | D | SC-08 | FSR-04.01, FSR-04.02, FSR-04.03 | Injected steering commands beyond the envelope (P-10) are limited, and those whose swept path comes within P-02 of a road user or kerb are rejected; an injected steering deviation beyond P-11 stops the vehicle in lane within the fault tolerant time interval of SG-04 (WP-S-04) |
| VC-11 | Hold, release and reverse at standstill | ENV-4 | fault-injection, scenario, requirements | D | SC-15, SC-16 | FSR-05.01, FSR-05.02, FSR-05.03, FSR-07.04 | The hold is released only with every condition met, under each injected fault of the release conditions; motion while holding is caught within P-03 and the park brake applied; reverse is refused unless at standstill, requested and with the rear clear; after a minimal risk condition the vehicle stays held until an explicit release |
| VC-12 | Right of way and speed near occlusions | ENV-4 | scenario | D | SC-02, SC-05, SC-06, SC-07 | FSR-06.01, FSR-06.02 | The monitor permits no motion whose swept path crosses a detected road user's predicted path within the bounds of P-07, and limits speed near occlusions so that the vehicle stops for a road user emerging at those bounds, in every run |
| VC-13 | The right-of-way and envelope rules against their formal model | — | formal, review | D | — | FSR-01.01, FSR-04.01, FSR-06.01 | The monitor's rules are shown to keep the vehicle out of a collision it can cause under the assumptions of P-06 and P-07, over the whole state space of the formal model (WP-W-05); each assumption the proof needs is in WP-S-02 |
| VC-14 | Loss of Autoware and the minimal risk manoeuvre | ENV-4 | fault-injection, timing, scenario | D | SC-17, SC-18 | FSR-07.01, FSR-07.02, FSR-07.07, FSR-07.08 | Injected computer, network and process faults are detected within the WP-S-04 budget and the vehicle stopped in lane with hazard lights and held; a fault injected inside the monitor silences its outputs; with the safety channel failed, Autoware's comfortable stop is checked and the monitor stops the vehicle when Autoware does not slow as expected |
| VC-15 | Remote driving, bounded and aged | ENV-2 | fault-injection, scenario, interface | D | SC-20, SC-21 | FSR-08.01, FSR-08.02, FSR-08.03 | Delayed, repeated, corrupted and unsigned remote commands are rejected (P-09); accepted remote commands are bounded like Autoware's; every command carries its time stamp, sequence number and integrity check; a release reaches only the vehicle and the moment it was meant for |
| VC-16 | Turn indicators against the manoeuvre | ENV-2 | fault-injection, scenario | D | SC-22 | FSR-09.01 | Every injected indicator command that disagrees with the commanded and achieved steering is caught and hazard lights switched on |
| VC-17 | Vehicle elements against the development interface agreement | ENV-4 | supplier, requirements, fault-injection | D | — | FSR-01.03, FSR-01.05, FSR-02.04, FSR-04.04, FSR-04.06, FSR-05.04, FSR-05.05, FSR-07.03, FSR-07.06 | The supplier's evidence for each requirement meets the DIA (DQ-008); on the vehicle, propulsion is cut and the park brake applied on the monitor's command whatever Autoware commands, the secondary brake and steering paths stop the vehicle after an injected single fault, measured state and door state reach the monitor with their fault flags, power faults leave the monitor and actuation powered, and with the monitor silenced the vehicle stops and holds after P-08 |
| VC-18 | ODD monitors at the boundary | ENV-1 | scenario, requirements | D | SC-10, SC-11, SC-14 | FM-14, FSR-07.05 | Each ODD monitor (MON-01 to MON-04) detects its condition as the scenario crosses the ODD boundary and starts its minimal risk manoeuvre before the boundary the scenario sweeps to is reached |
| VC-19 | Review of the monitor's restart and its own diagnostics | — | review | D | — | FSR-07.04, FSR-07.07 | No path in the monitor's logic resumes motion after a minimal risk condition without an explicit release; the diagnostic coverage of the monitor's own faults reaches what WP-H-04 needs for ASIL D |
| VC-20 | Modifications that are verified by review | — | review | — | — | FM-01, FM-08 | The training and test data cover the input space of WP-C-02 §6 with the classes FM-01 names, and the gaps WP-C-11 found are filled; route planning prefers a route without unprotected left turns across more than one oncoming lane or multi-lane roundabouts wherever one of similar length exists (FM-08) |

<!-- END GENERATED: verif-cases -->

The methods are those ISO 26262-4 §7 and ISO 21448 §10 ask of verification at the item level, with review where a measure cannot be shown by test:

<!-- BEGIN GENERATED: verif-methods (assurance/03-system/verif/verif.py) -->

| Method | Cases |
|---|---|
| Requirements-based test | VC-01, VC-03, VC-04, VC-05, VC-06, VC-11, VC-17, VC-18 |
| Fault injection test | VC-04, VC-05, VC-06, VC-07, VC-09, VC-10, VC-11, VC-14, VC-15, VC-16, VC-17 |
| Timing measurement against the WP-S-04 budget | VC-04, VC-05, VC-06, VC-10, VC-14 |
| Scenario test (WP-V-03 logical scenarios, sampled into concrete runs) | VC-01, VC-02, VC-03, VC-05, VC-06, VC-09, VC-10, VC-11, VC-12, VC-14, VC-15, VC-16, VC-18 |
| Statistical performance test (detection and false-detection rates) | VC-07, VC-08 |
| Interface test | VC-15 |
| Formal check of a rule against its model | VC-13 |
| Review or analysis | VC-08, VC-13, VC-19, VC-20 |
| Review of supplier evidence under the development interface agreement | VC-17 |

<!-- END GENERATED: verif-methods -->

Pass criteria refer to the parameters of [WP-S-02](WP-S-02-technical-safety-requirements.md) and the targets of [WP-V-02](../06-validation/WP-V-02-sotif-vv-strategy.md) rather than repeat their values, so that a value changed there changes the criterion here. A result that misses its criterion is a finding against the design (WP-P-03); the criterion, the budget and the parameter are not changed to pass it.

### 3.3 Functional safety requirements

<!-- BEGIN GENERATED: verif-fsrs (assurance/03-system/verif/verif.py) -->

| Requirement | Safety goal | ASIL | Element | WP-C-04 says verify by | Verified by |
|---|---|---|---|---|---|
| FSR-01.01 | SG-01 | D | EL-02 | Fault injection of excessive acceleration commands in HIL; scenario tests | VC-02, VC-03, VC-04, VC-05, VC-06, VC-11, VC-13, VC-14, VC-15 |
| FSR-01.02 | SG-01 | D | EL-02 | Fault injection on the vehicle side; FTTI measurement (WP-S-04) | VC-02, VC-03, VC-05, VC-06, VC-11 |
| FSR-01.03 | SG-01 | D | EL-04 | Supplier evidence under the DIA; vehicle test | VC-17 |
| FSR-01.05 | SG-01 | D | EL-06 | Supplier evidence under the DIA; fault injection on the signal path | VC-17 |
| FSR-01.04 | SG-01 | QM | EL-01 | Simulation and vehicle test | VC-01, VC-03 |
| FSR-02.01 | SG-02 | D | EL-03 | Detection performance tests across the ODD; fault injection of sensor faults | VC-02, VC-03, VC-06, VC-07, VC-09, VC-12, VC-18 |
| FSR-02.02 | SG-02 | D | EL-02 | Scenario tests (cut-in, sudden stop, pedestrian entering); HIL | VC-02, VC-03, VC-04, VC-05, VC-06, VC-10, VC-12, VC-14, VC-15, VC-18 |
| FSR-02.03 | SG-02 | D | EL-02 | Fault injection on the primary brake path | VC-02, VC-03, VC-05, VC-06 |
| FSR-02.04 | SG-02 | D | EL-04 | Supplier evidence under the DIA | VC-17 |
| FSR-02.05 | SG-02 | QM | EL-01 | Simulation and vehicle test | VC-01, VC-02, VC-03, VC-05, VC-06 |
| FSR-03.01 | SG-03 | C | EL-03 | Field and replay data over the ODD; false-positive rate estimation | VC-02, VC-03, VC-06, VC-08, VC-09, VC-10, VC-12, VC-15, VC-18 |
| FSR-03.02 | SG-03 | C | EL-02 | Fault injection of spurious braking commands; scenario tests | VC-02, VC-03, VC-05, VC-06, VC-09 |
| FSR-03.03 | SG-03 | C | EL-02 | Review of the intervention logic; replay tests | VC-02, VC-03, VC-08, VC-09 |
| FSR-04.01 | SG-04 | D | EL-02 | Fault injection of steering commands; scenario tests with oncoming traffic and cyclists | VC-02, VC-03, VC-10, VC-12, VC-13, VC-14, VC-15, VC-16, VC-18 |
| FSR-04.02 | SG-04 | D | EL-02 | Fault injection; HIL | VC-02, VC-04, VC-10 |
| FSR-04.03 | SG-04 | D | EL-02 | Fault injection on the steering path | VC-02, VC-10 |
| FSR-04.04 | SG-04 | D | EL-04 | Supplier evidence under the DIA | VC-17 |
| FSR-04.06 | SG-04 | D | EL-06 | Supplier evidence under the DIA; fault injection on the signal path | VC-17 |
| FSR-04.05 | SG-04 | QM | EL-01 | Simulation and vehicle test | VC-01, VC-02, VC-03, VC-05, VC-06, VC-10, VC-12 |
| FSR-05.01 | SG-05 | D | EL-02 | Fault injection; scenario tests at stops with passengers and pedestrians | VC-02, VC-03, VC-05, VC-11, VC-15 |
| FSR-05.02 | SG-05 | D | EL-02 | Fault injection on the brake hold | VC-03, VC-05, VC-11 |
| FSR-05.03 | SG-05 | D | EL-02 | Fault injection of gear commands; scenario tests | VC-02, VC-03, VC-11 |
| FSR-05.04 | SG-05 | D | EL-05 | Supplier evidence under the DIA | VC-03, VC-05, VC-11, VC-17 |
| FSR-05.05 | SG-05 | D | EL-08 | Supplier evidence; vehicle test | VC-02, VC-03, VC-11, VC-17 |
| FSR-06.01 | SG-06 | D | EL-02 | Scenario tests at intersections, unprotected turns, roundabouts and crosswalks; formal check of the rule | VC-02, VC-03, VC-05, VC-06, VC-10, VC-12, VC-13, VC-15, VC-18 |
| FSR-06.02 | SG-06 | D | EL-02 | Scenario tests with occlusions | VC-02, VC-03, VC-12 |
| FSR-06.03 | SG-06 | QM | EL-01 | Simulation, scenario and vehicle tests; SOTIF evaluation (WP-V-03) | VC-01, VC-02, VC-03, VC-06, VC-12, VC-18 |
| FSR-07.01 | SG-07 | D | EL-02 | Fault injection (computer, network, process faults); timing measurement | VC-02, VC-03, VC-14, VC-15 |
| FSR-07.02 | SG-07 | D | EL-02 | Fault injection; vehicle test | VC-02, VC-03, VC-14 |
| FSR-07.03 | SG-07 | D | EL-07 | Supplier evidence; power fault injection | VC-17 |
| FSR-07.04 | SG-07 | D | EL-02 | Review; scenario test | VC-02, VC-03, VC-11, VC-15, VC-19 |
| FSR-07.05 | SG-07 | QM | EL-01 | Simulation and vehicle test | VC-01, VC-02, VC-03, VC-14, VC-15, VC-18 |
| FSR-07.06 | SG-07 | D | EL-04 | Supplier evidence under the DIA; vehicle test with the monitor disconnected | VC-03, VC-14, VC-17 |
| FSR-07.07 | SG-07 | D | EL-02 | Fault injection inside the monitor; review of its diagnostic coverage | VC-03, VC-14, VC-19 |
| FSR-07.08 | SG-07 | D | EL-02 | Fault injection of EL-03 faults with Autoware's stop delayed or missing | VC-02, VC-03, VC-09, VC-14 |
| FSR-08.01 | SG-08 | C | EL-02 | Fault injection of delayed, repeated and corrupted commands | VC-02, VC-15 |
| FSR-08.02 | SG-08 | C | EL-02 | Scenario tests in REMOTE mode | VC-02, VC-15 |
| FSR-08.03 | SG-08 | C | EL-09 | Interface test; cybersecurity verification (WP-C-10) | VC-02, VC-15 |
| FSR-09.01 | SG-09 | C | EL-02 | Fault injection of indicator commands | VC-02, VC-16 |

<!-- END GENERATED: verif-fsrs -->

### 3.4 Triggering conditions

<!-- BEGIN GENERATED: verif-tcs (assurance/03-system/verif/verif.py) -->

| Triggering condition | Category | Verified by |
|---|---|---|
| TC-01 Low sun or oncoming headlights in a camera's view | environment | VC-01, VC-02, VC-03, VC-07, VC-12 |
| TC-02 Night or unlit streets, with road users in dark clothing | environment | VC-01, VC-02, VC-03, VC-06, VC-07 |
| TC-03 Light rain, spray thrown up by other vehicles, reflections from the wet road | environment | VC-01, VC-02, VC-03, VC-06, VC-07, VC-09 |
| TC-04 Steam from vents, exhaust plumes, blowing dust or leaves | environment | VC-01, VC-02, VC-03, VC-07, VC-09 |
| TC-05 Mist with visibility near the 200 m floor | environment | VC-01, VC-02, VC-07, VC-18 |
| TC-06 LED signal heads that flicker against the camera's exposure | environment | VC-01, VC-02, VC-03, VC-12 |
| TC-07 Signal heads that are hidden, damaged, temporary, dark in a power outage, or meant for another lane | road | VC-01, VC-02, VC-03, VC-12 |
| TC-08 Streets with few features, or with many objects moved since the point cloud map was made | road | VC-01, VC-02 |
| TC-09 Construction, re-marked lanes or closures not yet in the map | road | VC-01, VC-02, VC-03, VC-18 |
| TC-10 Parked vans, buses, hedges or walls hiding a crossing or a corner | road | VC-01, VC-02, VC-03, VC-12 |
| TC-11 Large vehicles alongside, blocking the LiDAR's view of the surroundings | road | VC-01, VC-02, VC-03, VC-05, VC-06 |
| TC-12 Unprotected left turn with a turning vehicle hiding an oncoming lane | road | VC-01, VC-02, VC-03, VC-12 |
| TC-13 Entry to a multi-lane roundabout with traffic circulating | road | VC-01, VC-02, VC-03, VC-12 |
| TC-14 Bike lanes, driveways, bus stops or crosswalks along the kerb where a pull-over is tried | road | VC-01, VC-02, VC-03, VC-14 |
| TC-15 People of unusual shape or posture (wheelchairs, children, people carrying large objects or pushing strollers) | road_users | VC-01, VC-02, VC-03, VC-06 |
| TC-16 Rare objects (animals, e-scooters, fallen loads, debris low on the road) | road_users | VC-01, VC-02, VC-03, VC-06 |
| TC-17 People crossing away from crossings, or at the kerb looking at a phone | road_users | VC-01, VC-02, VC-03, VC-12 |
| TC-18 Cyclists riding between lanes or swerving round obstacles | road_users | VC-01, VC-02, VC-03, VC-10 |
| TC-19 A vehicle running a red light or not stopping at its stop line | road_users | VC-01, VC-02, VC-03, VC-12 |
| TC-20 Motorcycles, and vehicles accelerating hard, approaching from far away | road_users | VC-01, VC-02, VC-03, VC-12 |
| TC-21 An emergency vehicle approaching with siren and lights | road_users | VC-01, VC-02, VC-03 |
| TC-22 A police officer or flagger directing traffic | road_users | VC-01, VC-02, VC-03, VC-18 |
| TC-23 Drivers who expect give and take (four-way stops, merging, letting someone out) | road_users | VC-01, VC-02 |
| TC-24 Sensors soiled or blocked by dirt, insects or water drops | vehicle | VC-01, VC-02, VC-03, VC-07, VC-09 |
| TC-25 Wet road reducing grip during braking or turning | vehicle | VC-01, VC-02, VC-03, VC-05, VC-06 |
| TC-26 Video to the remote operator delayed, compressed or with a narrow field of view | operations | VC-02, VC-15 |
| TC-27 A remote operator dealing with more than one vehicle, or tired | operations | VC-02, VC-15 |
| TC-28 Weather changing during a trip toward the limits of the ODD | environment | VC-01, VC-02, VC-18 |
| TC-29 Passengers getting out at a stop in lane beside moving traffic | operations | VC-02 |

<!-- END GENERATED: verif-tcs -->

### 3.5 Functional modifications

<!-- BEGIN GENERATED: verif-fms (assurance/03-system/verif/verif.py) -->

| Functional modification | Type | Verified by |
|---|---|---|
| FM-01 Training and test data for the ODD | data | VC-20 |
| FM-02 Independent safety channel and envelope | architecture | VC-02 |
| FM-03 Ground segmentation for low objects | function | VC-01, VC-02, VC-03, VC-06 |
| FM-04 Tracks held through occlusion | function | VC-01 |
| FM-05 Conservative traffic light reading | function | VC-01, VC-02, VC-03, VC-12 |
| FM-06 Prediction of rule-breaking road users | function | VC-01, VC-02, VC-03, VC-10 |
| FM-07 Conservative gap acceptance | function | VC-01, VC-02, VC-03, VC-12 |
| FM-08 Route preference away from the hardest junctions | odd | VC-20 |
| FM-09 Localisation integrity monitor | function | VC-01, VC-02 |
| FM-10 Safety channel sensors and blockage detection | function | VC-01, VC-02, VC-03, VC-07, VC-09 |
| FM-11 Limits on remote driving | operations | VC-02, VC-15 |
| FM-12 Wet-road driving | function | VC-01, VC-03 |
| FM-13 Map change management | operations | VC-01, VC-02, VC-03, VC-18 |
| FM-14 ODD monitors | function | VC-18 |
| FM-15 Emergency vehicle response | function | VC-01, VC-02, VC-03 |
| FM-16 Response to people directing traffic | function | VC-01, VC-02, VC-03, VC-18 |
| FM-17 Predictable driving style | function | VC-01, VC-02 |
| FM-18 Occlusion-aware speed | function | VC-01 |
| FM-19 Pull-over to mapped safe stopping places | function | VC-01, VC-02, VC-03, VC-14 |
| FM-20 Passenger warning at a stop in lane | operations | VC-02 |

<!-- END GENERATED: verif-fms -->

## 4. Results and deviations

No case has been run. Results are recorded per case against a released configuration (WP-P-01): for a scenario case, every concrete run with its parameters and outcome; for a timed case, the measured times against their budget. Each failure is a problem report (WP-P-03), and each deviation from this specification is recorded with its reason before the result is used.

## 5. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Verify against the system requirements of WP-S-01 once they are written; until then the functional safety requirements and the SOTIF measures stand in for them | G2 |
| OI-2 | Set the detection and false-detection targets and their confidence in WP-V-02, which VC-07 and VC-08 test against | G3 |
| OI-3 | Write the formal model of the monitor's rules that VC-13 checks (WP-W-05, as WP-S-08 OI-3) | G3 |
| OI-4 | Agree the supplier evidence VC-17 reviews in the development interface agreement, once the vehicle is chosen (DQ-008) | G2 |
| OI-5 | Detail each case into concrete test procedures, with the sampling of each scenario's parameters into concrete runs | G3 |
| OI-6 | Run the cases and record the results | G4 |
