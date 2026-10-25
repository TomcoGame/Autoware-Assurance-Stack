# WP-C-04 Functional safety concept (FSRs, allocation, assumptions)

| Field | Value |
|---|---|
| Work product | WP-C-04 Functional safety concept (FSRs, allocation, assumptions) |
| Standard reference | UL 4600 §10; ISO 26262-3 §7; ASPICE 4.0 SYS.2; IEEE 2846-2022 (informative, assumptions in safety-related models) |
| Version | 0.8 (Figure 2-1, the safety view of the item architecture; 2026-10-25). 0.7 (folder page `fsc/README.md` with the whole concept on one page, Figure 4-2 on how each goal is held, and `fsc/fsrs.csv` tracing every FSR to its mechanisms, technical requirements and verification cases; 2026-10-24). 0.6 (FSR-03.02: the firm level is 3 m/s² (DQ-033 A); 2026-10-24). 0.5 (FSR-07.08: the monitor checks Autoware's stop after its own sensors fail (DQ-021 A); 2026-10-23). 0.4 (FSR-07.06 and FSR-07.07: the vehicle stops when the monitor falls silent, from the fallback concept (WP-C-12); 2026-10-23). 0.3 (collision avoidance carries SG-06 (DQ-017 A); the safety channel has its own sensors (DQ-018 A); the monitor softens unconfirmed hard braking (DQ-019 A); 2026-10-23). 0.2 (first content: the envelope concept, nine elements, functional safety requirements for the nine safety goals, generated from `fsc/fsc.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | Up to ASIL D |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1); confirmation review (I3) with the HARA before G1 |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | `a485873`; safety goals of WP-C-03 v0.3 |

## 1. Purpose

This is the functional safety concept: how the safety goals of the [HARA (WP-C-03)](WP-C-03-hara.md) are met. It states the functional safety requirements (FSRs), allocates each to an element of the architecture, and names what the item assumes of the elements outside it. The technical safety concept ([WP-S-03](../03-system/WP-S-03-technical-safety-concept-architecture.md)) refines it, the fallback concept ([WP-C-12](WP-C-12-fallback-and-minimal-risk-concept.md)) details SG-07, and the ASIL decomposition rationale ([WP-A-01](../08-analyses/WP-A-01-asil-decomposition.md)) records any decomposition.

In summary:

<!-- BEGIN GENERATED: fsc-summary (assurance/02-concept/fsc/fsc.py) -->

39 functional safety requirements for 9 safety goals: 34 rated, 5 QM supporting the nominal function. 9 elements, 3 of them in the item. No requirement waits on a decision.

<!-- END GENERATED: fsc-summary -->

## 2. The concept

<!-- BEGIN GENERATED: fsc-safety-view (assurance/02-concept/fsc/fsc.py) -->

![Figure 2-1: the item boundary of WP-C-01 redrawn with the elements of the functional safety concept. Inside the item: Autoware computer (EL-01, QM), Safety monitor (EL-02, ASIL D), Safety perception channel (EL-03, ASIL D). Outside it: Vehicle drive-by-wire (EL-04, ASIL D), Park brake (EL-05, ASIL D), Vehicle state sensing (EL-06, ASIL D), Monitor power supply (EL-07, ASIL D), Door system (EL-08, ASIL D), Remote operations station (EL-09, ASIL C). Autoware's commands (dashed) reach the drive-by-wire only through the safety monitor; every flow a rated requirement rests on (solid) starts or ends at the monitor. Each element shows its derived ASIL and the number of FSRs allocated to it; the same data are in the elements table.](fsc/fig-c04-2-1-safety-view.svg)

*Figure 2-1. The safety view of the item architecture: the item of [WP-C-01](WP-C-01-item-definition.md) §5 with the elements this concept places its requirements on. Drawn by [`fsc/fsc.py`](fsc/fsc.py) from `fsc/fsc.yaml`; CI fails if it is stale or if an element has no place in it.*

<!-- END GENERATED: fsc-safety-view -->

### 2.1 Doer and checker

Autoware is the doer: it perceives, plans and controls, and it stays QM (DQ-002 A). It cannot be the basis of an ASIL D argument, because it runs learned perception on a general-purpose computer, operating system and middleware.

The safety monitor is the checker. Every command, from Autoware or from a remote operator, passes through it on the way to the drive-by-wire system (WP-C-01 I-03, I-04). It lets a command through only if the result stays inside a **safety envelope**, and it can stop the vehicle on its own.

### 2.2 An envelope of consequences, not of rules

The six ASIL D goals cannot all be checked from the command alone. Whether a deceleration is enough (SG-02), or whether entering an intersection is safe (SG-06), depends on the scene. The monitor therefore has its own view of the scene, the **safety perception channel** (EL-03). The concept limits what that channel must know:

- **What it checks:** that the vehicle's swept path over its stopping time stays clear of every road user and obstacle the channel detects, under stated bounds on how other road users can move. This is the pattern of formal safety envelopes such as Responsibility-Sensitive Safety, with the bounds stated as IEEE 2846 asks.
- **How it detects:** by geometry (LiDAR and radar returns, free space, motion), not by learned classification. "Something is there and moving this way" is enough; it does not need to know that it is a cyclist.
- **What it does not check:** traffic rules as such. Whether a light is red, or whose turn it is at a stop sign, stays with Autoware (FSR-06.03) and is argued under SOTIF. The monitor stops the collision that a rule violation would cause with a road user it can see. Where it cannot see (occlusion), it limits speed to what lets the vehicle stop for a road user emerging at the assumed speed (FSR-06.02).

SG-06 therefore rests on collision avoidance rather than rule compliance (decision of the safety authority, DQ-017 A, 2026-10-23). The ASIL D argument covers the collision the HARA rated; running a red light into an empty intersection is not prevented at ASIL D and is argued under SOTIF (WP-C-05) with Autoware's traffic-light chain.

### 2.3 Independence

The concept works only if a fault that makes Autoware command something unsafe cannot also blind or disable the monitor. The elements must therefore not share a computer, operating system, power supply (FSR-07.03) or sensors: the safety perception channel has its own sensors (DQ-018 A, 2026-10-23), reaching the monitor on a path that does not pass through the Autoware computer (WP-C-01 I-13). The dependent failure analysis ([WP-A-03](../08-analyses/WP-A-03-dependent-failure-analysis.md)) still has to show that the two sensor sets do not fail together, for example from shared mounting, cleaning, power or the same weather.

### 2.4 Two goals in tension

SG-02 (brake enough, ASIL D) and SG-03 (do not brake hard without reason, ASIL C) pull against each other. If Autoware brakes hard for something only it can see, the monitor cannot tell a justified emergency stop from a faulty one. The monitor limits such unconfirmed braking to a firm, non-emergency level (FSR-03.02; DQ-019 A, 2026-10-23), the number to be set in WP-S-04. The consequence is that Autoware alone can no longer emergency-brake for an object the safety channel misses, so the channel's detection (FSR-02.01) must carry SG-02 by itself.

## 3. Safety goals and their requirements

<!-- BEGIN GENERATED: fsc-goals (assurance/02-concept/fsc/fsc.py) -->

| Safety goal | ASIL | Safe state | FSRs at the goal's ASIL | Supporting QM FSRs |
|---|---|---|---|---|
| SG-01 Avoid unintended acceleration | **D** | Propulsion off and the vehicle held at standstill | FSR-01.01, FSR-01.02, FSR-01.03, FSR-01.05 | FSR-01.04 |
| SG-02 Decelerate at least as much as needed to avoid a collision the planned trajectory avoids | **D** | Vehicle braked to standstill and held | FSR-02.01, FSR-02.02, FSR-02.03, FSR-02.04 | FSR-02.05 |
| SG-03 Avoid unintended hard deceleration | **C** | Normal driving continues, or a comfortable stop | FSR-03.01, FSR-03.02, FSR-03.03 | — |
| SG-04 Avoid unintended lateral motion out of the planned path | **D** | Vehicle stopped in its lane | FSR-04.01, FSR-04.02, FSR-04.03, FSR-04.04, FSR-04.06 | FSR-04.05 |
| SG-05 Avoid unintended motion from standstill, forward or backward | **D** | Vehicle held at standstill with the park brake applied | FSR-05.01, FSR-05.02, FSR-05.03, FSR-05.04, FSR-05.05 | — |
| SG-06 Do not enter an intersection, roundabout or crosswalk against right of way | **D** | Vehicle stopped before the stop line or conflict area | FSR-06.01, FSR-06.02 | FSR-06.03 |
| SG-07 Reach a minimal risk condition whenever the item can no longer drive safely | **D** | Vehicle stopped and held in its lane with hazard lights on; Autoware pulls over to the kerb first when it still can, but the rated condition is the stop in lane (DQ-016 A) | FSR-07.01, FSR-07.02, FSR-07.03, FSR-07.04, FSR-07.06, FSR-07.07, FSR-07.08 | FSR-07.05 |
| SG-08 Do not act on remote driving commands that are stale, corrupted or not the operator's | **C** | Vehicle brought to a stop and held | FSR-08.01, FSR-08.02, FSR-08.03 | — |
| SG-09 Avoid signalling a manoeuvre other than the one performed | **C** | Indicators off, hazard lights on | FSR-09.01 | — |

<!-- END GENERATED: fsc-goals -->

## 4. Allocation to elements

![Figure 4-1: a grid with the nine safety goals SG-01 to SG-09 as rows and the nine elements EL-01 to EL-09 as columns; each cell shows how many functional safety requirements of that goal are allocated to that element, shaded by their ASIL. The safety monitor (EL-02) carries requirements for every goal. Elements outside the item are framed together with a dashed line. The same allocation is listed in the tables below.](fsc/fig-c04-4-1-allocation.svg)

*Figure 4-1. Which element carries which safety goal. Drawn from `fsc/fsc.yaml` and the HARA model by [`fsc/fsc.py`](fsc/fsc.py); CI fails if it is stale.*

![Figure 4-2: nine cards, one per safety goal SG-01 to SG-09. Each shows a chart of a faulty command, the envelope bound and what the safety monitor passes to the vehicle over time, a top-down scene with the path the faulty command would take, where the monitor steps in and the safe state reached, and the rated requirements by the element that carries them.](fsc/fig-c04-4-2-goals.svg)

*Figure 4-2. How the concept holds each safety goal. Schematic, not simulation results. Drawn by [`fsc/fsc.py`](fsc/fsc.py); CI fails if it is stale. The whole concept is on one page in [`fsc/README.md`](fsc/README.md).*

Each element's ASIL is derived: the highest ASIL among the FSRs allocated to it. Elements outside the item are bound by the assumption named, which becomes a requirement on the vehicle supplier through the development interface agreement ([WP-M-11](../01-management/WP-M-11-upstream-and-supplier-management.md)).

<!-- BEGIN GENERATED: fsc-elements (assurance/02-concept/fsc/fsc.py) -->

| ID | Element | In the item | Derived ASIL | Role | Assumption | FSRs |
|---|---|---|---|---|---|---|
| EL-01 | Autoware computer | Yes | **QM** | Plans and controls nominal driving, carries out its own MRMs and ODD monitors; QM by decision DQ-002 A | — | 5 |
| EL-02 | Safety monitor | Yes | **D** | Independent controller between Autoware and drive-by-wire; enforces the safety envelope and can stop the vehicle alone | — | 22 |
| EL-03 | Safety perception channel | Yes | **D** | Own sensors and processing for the safety monitor, independent of Autoware's (DQ-018 A); detects road users and obstacles without relying on learned classification | — | 2 |
| EL-04 | Vehicle drive-by-wire | No | **D** | Braking, steering, propulsion and gear by wire, with the redundancy AOU-01 requires | AOU-01 | 4 |
| EL-05 | Park brake | No | **D** | Holds the vehicle at standstill on the monitor's command | AOU-02 | 1 |
| EL-06 | Vehicle state sensing | No | **D** | Speed, steering angle, gear and by-wire faults delivered to the monitor without passing through Autoware | AOU-03 | 2 |
| EL-07 | Monitor power supply | No | **D** | Keeps the monitor, its channel and the actuation path powered when the Autoware computer's supply fails | AOU-05 | 1 |
| EL-08 | Door system | No | **D** | Reports door state and keeps the vehicle from moving with a door open | AOU-06 | 1 |
| EL-09 | Remote operations station | No | **C** | Sends remote driving commands with time stamp, sequence number and integrity protection | AOU-10 | 1 |

<!-- END GENERATED: fsc-elements -->

## 5. Functional safety requirements

Requirements that depended on a decision of the safety authority name it. [`fsc/fsrs.csv`](fsc/fsrs.csv) traces each one to the safety mechanisms of WP-S-03, the technical safety requirements of WP-S-02 and the verification cases of WP-S-09.

<!-- BEGIN GENERATED: fsc-fsrs (assurance/02-concept/fsc/fsc.py) -->

| ID | Requirement | ASIL | Allocated to | Verified by |
|---|---|---|---|---|
| FSR-01.01 | Limit commanded acceleration to the envelope for the current speed, and to zero or braking whenever the distance to a road user or obstacle ahead detected by EL-03 is below the safe longitudinal distance | D | EL-02 Safety monitor | Fault injection of excessive acceleration commands in HIL; scenario tests |
| FSR-01.02 | Detect actual acceleration above the bounded command from the vehicle state (EL-06), then cut propulsion and brake to standstill within the fault tolerant time interval | D | EL-02 Safety monitor | Fault injection on the vehicle side; FTTI measurement (WP-S-04) |
| FSR-01.03 | Cut propulsion on the safety monitor's command, whatever Autoware commands | D | EL-04 Vehicle drive-by-wire | Supplier evidence under the DIA; vehicle test |
| FSR-01.05 | Deliver measured speed and longitudinal acceleration to the safety monitor without passing through Autoware, and flag their own faults | D | EL-06 Vehicle state sensing | Supplier evidence under the DIA; fault injection on the signal path |
| FSR-01.04 | Plan and command acceleration within the vehicle's comfort and legal limits | QM | EL-01 Autoware computer | Simulation and vehicle test |
| FSR-02.01 | Detect road users and obstacles in and beside the vehicle's swept path out to the stopping distance at the maximum ODD speed, by day and night and in the weather of ODD-10 and ODD-11, and report their position and velocity to the monitor | D | EL-03 Safety perception channel | Detection performance tests across the ODD; fault injection of sensor faults |
| FSR-02.02 | When a detected road user or obstacle is closer than the safe longitudinal distance and the commanded deceleration does not restore it, command the deceleration that does | D | EL-02 Safety monitor | Scenario tests (cut-in, sudden stop, pedestrian entering); HIL |
| FSR-02.03 | Compare achieved with commanded deceleration (EL-06) and switch to the secondary braking path on a shortfall | D | EL-02 Safety monitor | Fault injection on the primary brake path |
| FSR-02.04 | Provide a secondary braking path that can still stop the vehicle after any single fault in the primary one | D | EL-04 Vehicle drive-by-wire | Supplier evidence under the DIA |
| FSR-02.05 | Plan and control to keep a safe distance and stop for road users and obstacles (nominal function) | QM | EL-01 Autoware computer | Simulation and vehicle test |
| FSR-03.01 | Keep false detections in the swept path below the rate the SOTIF acceptance criteria allow, so that monitor interventions are rarely unjustified | C | EL-03 Safety perception channel | Field and replay data over the ODD; false-positive rate estimation |
| FSR-03.02 | Limit decelerations from Autoware above the comfortable level that EL-03 does not confirm with a road user or obstacle to a firm, non-emergency level of 3 m/s² (DQ-019 A, DQ-033 A) | C | EL-02 Safety monitor | Fault injection of spurious braking commands; scenario tests |
| FSR-03.03 | Apply emergency-level deceleration on the monitor's own initiative only when FSR-02.02 requires it | C | EL-02 Safety monitor | Review of the intervention logic; replay tests |
| FSR-04.01 | Reject steering commands whose predicted swept path, over the stopping time, comes within the safe lateral distance of a road user, obstacle or kerb detected by EL-03, and stop in lane instead | D | EL-02 Safety monitor | Fault injection of steering commands; scenario tests with oncoming traffic and cyclists |
| FSR-04.02 | Limit commanded steering angle and rate to the envelope for the current speed | D | EL-02 Safety monitor | Fault injection; HIL |
| FSR-04.03 | Compare achieved with commanded steering (EL-06) and stop in lane on a deviation beyond the tolerance | D | EL-02 Safety monitor | Fault injection on the steering path |
| FSR-04.04 | Keep steering controllable by wire after any single fault long enough to complete a stop in lane | D | EL-04 Vehicle drive-by-wire | Supplier evidence under the DIA |
| FSR-04.06 | Deliver measured steering angle to the safety monitor without passing through Autoware, and flag its own faults | D | EL-06 Vehicle state sensing | Supplier evidence under the DIA; fault injection on the signal path |
| FSR-04.05 | Plan and follow a path inside the lane and the drivable area (nominal function) | QM | EL-01 Autoware computer | Simulation and vehicle test |
| FSR-05.01 | At standstill, hold the service brake and park brake until all release conditions hold: doors closed (EL-08), no road user or obstacle detected by EL-03 in the near field in the direction of travel, and a motion request in the selected gear | D | EL-02 Safety monitor | Fault injection; scenario tests at stops with passengers and pedestrians |
| FSR-05.02 | Detect motion while holding (EL-06) and apply the park brake | D | EL-02 Safety monitor | Fault injection on the brake hold |
| FSR-05.03 | Allow reverse only at standstill, on request, and with the rear near field clear as detected by EL-03 | D | EL-02 Safety monitor | Fault injection of gear commands; scenario tests |
| FSR-05.04 | Apply and hold the park brake on the safety monitor's command | D | EL-05 Park brake | Supplier evidence under the DIA |
| FSR-05.05 | Report door state to the safety monitor and inhibit motion with any door open | D | EL-08 Door system | Supplier evidence; vehicle test |
| FSR-06.01 | Do not permit motion whose swept path crosses the predicted path of a road user detected by EL-03 before the vehicle could stop or clear it, using stated bounds on other road users' acceleration and speed (DQ-017 A) | D | EL-02 Safety monitor | Scenario tests at intersections, unprotected turns, roundabouts and crosswalks; formal check of the rule |
| FSR-06.02 | Limit speed where EL-03's view is occluded so that the vehicle can stop for a road user emerging at the assumed maximum speed (DQ-017 A) | D | EL-02 Safety monitor | Scenario tests with occlusions |
| FSR-06.03 | Obey traffic lights, signs and right of way, treating an unknown or unrecognised signal as red (OEDR-05 to OEDR-07); argued under SOTIF (DQ-017 A) | QM | EL-01 Autoware computer | Simulation, scenario and vehicle tests; SOTIF evaluation (WP-V-03) |
| FSR-07.01 | Detect loss, delay or implausibility of Autoware's commands within the detection time WP-S-04 allots | D | EL-02 Safety monitor | Fault injection (computer, network, process faults); timing measurement |
| FSR-07.02 | On detection, bring the vehicle to a stop in lane with hazard lights on and hold it, without Autoware | D | EL-02 Safety monitor | Fault injection; vehicle test |
| FSR-07.03 | Keep the safety monitor, EL-03 and the actuation path powered after any single fault of the Autoware computer's supply | D | EL-07 Monitor power supply | Supplier evidence; power fault injection |
| FSR-07.04 | After a minimal risk condition, resume motion only on an explicit release from the remote operations centre with the release conditions of FSR-05.01 met | D | EL-02 Safety monitor | Review; scenario test |
| FSR-07.05 | Carry out an MRM when its diagnostics or ODD monitors (MON-01 to MON-04) require it, pulling over when it can and stopping in lane otherwise (DQ-016 A) | QM | EL-01 Autoware computer | Simulation and vehicle test |
| FSR-07.06 | Brake to a standstill and hold it when commands from the safety monitor stop for longer than the time WP-S-04 sets, whatever Autoware sends (WP-C-12 MRM-5) | D | EL-04 Vehicle drive-by-wire | Supplier evidence under the DIA; vehicle test with the monitor disconnected |
| FSR-07.07 | On detecting a fault of its own, stop sending commands to the vehicle, so that the vehicle's own stop (FSR-07.06) takes over | D | EL-02 Safety monitor | Fault injection inside the monitor; review of its diagnostic coverage |
| FSR-07.08 | When EL-03 fails, have Autoware stop in lane comfortably, check its speed, deceleration and steering against the vehicle state (EL-06), and stop the vehicle itself if it does not slow as expected (DQ-021 A) | D | EL-02 Safety monitor | Fault injection of EL-03 faults with Autoware's stop delayed or missing |
| FSR-08.01 | In REMOTE mode, reject commands older than the age bound WP-S-04 sets, out of sequence or failing their integrity check, and stop | C | EL-02 Safety monitor | Fault injection of delayed, repeated and corrupted commands |
| FSR-08.02 | Apply the same envelope checks to remote commands as to Autoware's (FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01) | C | EL-02 Safety monitor | Scenario tests in REMOTE mode |
| FSR-08.03 | Send every remote driving command with a time stamp, sequence number and integrity protection | C | EL-09 Remote operations station | Interface test; cybersecurity verification (WP-C-10) |
| FSR-09.01 | Compare the commanded turn indicator with the commanded and achieved steering direction, and switch to hazard lights on a mismatch | C | EL-02 Safety monitor | Fault injection of indicator commands |

<!-- END GENERATED: fsc-fsrs -->

## 6. Safe states, warning and degradation

| State | Entered when | Who brings it about | Leaves when |
|---|---|---|---|
| Normal driving | Autoware drives inside the envelope | Autoware; the monitor passes its commands | — |
| Envelope intervention | A command would leave the envelope (FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01) | The monitor replaces the command with braking, for as long as needed | The envelope is restored and Autoware's command is inside it again |
| Pull-over MRM | Autoware's own diagnostics or ODD monitors ask for it and Autoware can still drive (FSR-07.05) | Autoware, still checked by the monitor | Stopped at the kerb |
| Stop in lane | Autoware cannot complete a pull-over, or the monitor detects loss of valid commands (FSR-07.01, FSR-07.02) | Autoware if it can; otherwise the monitor alone | Stopped and held, hazard lights on |
| Held | After any stop | The monitor (FSR-05.01, FSR-07.04) | The remote operations centre releases it and the release conditions hold |

Passengers are told what is happening through the vehicle's interface, and the remote operations centre is alerted on every intervention and minimal risk condition (WP-O-02).

## 7. Assumptions on other elements

The elements outside the item carry rated requirements through the assumptions of [WP-C-01 §8](WP-C-01-item-definition.md#8-assumptions): AOU-01 (redundant by-wire braking and steering), AOU-02 (park brake), AOU-03 (independent vehicle state), AOU-05 (monitor power), AOU-06 (door interlock) and AOU-10 (remote operations). Each must be confirmed by the vehicle supplier at G2 (DQ-008); a vehicle that cannot meet them cannot carry this concept.

## 8. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Argue the traffic-rule part of SG-06 under SOTIF (WP-C-05), as DQ-017 A requires | G1 |
| OI-2 | Run the dependent failure analysis on the two sensor sets (WP-A-03) | G2 |
| OI-3 | Set the firm deceleration level of FSR-03.02 in WP-S-04 | G2 |
| OI-4 | State the bounds on other road users' motion that FSR-06.01 and FSR-06.02 assume, and their source | G2 |
| OI-5 | Record any ASIL decomposition in WP-A-01; this draft has none | G2 |
| OI-6 | Fault tolerant time intervals and detection times for every rated FSR (WP-S-04) | G2 |
