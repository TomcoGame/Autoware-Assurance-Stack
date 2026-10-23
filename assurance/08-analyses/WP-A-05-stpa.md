# WP-A-05 System-theoretic process analysis (STPA)

| Field | Value |
|---|---|
| Work product | WP-A-05 System-theoretic process analysis (STPA) |
| Standard reference | UL 4600 §6; ISO 26262-9 §8; ISO 21448 §6–7 |
| Version | 0.2 (first content: losses, system-level hazards, the control structure with remote operations and passengers, unsafe control actions for every control action, loss scenarios and new requirements, generated from `stpa/stpa.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

STPA of the driverless control structure, including remote operations. The HARA ([WP-C-03](../02-concept/WP-C-03-hara.md)) starts from malfunctions and the SOTIF analysis ([WP-C-05](../02-concept/WP-C-05-sotif-hazard-identification.md)) from insufficiencies of single functions. STPA starts from the control loops: who commands whom, what each controller believes, and what feedback it gets. It finds hazards that arise when every part works as specified but their interaction does not, which matters most where people (remote operators, passengers, the map process) are in the loop. The method follows the STPA Handbook (Leveson and Thomas, 2018).

Needed at gate G2 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: stpa-summary (assurance/08-analyses/stpa/stpa.py) -->

4 losses, 8 system-level hazards (2 not in the HARA: HZ-7, HZ-8), 6 controllers, 15 control actions, 49 unsafe control actions, 27 loss scenarios and 7 new requirements. Every control action is examined for all four types, every unsafe control action has a scenario, and every scenario a measure or a new requirement.

<!-- END GENERATED: stpa-summary -->

The analysis is kept in `stpa/stpa.yaml`; `stpa/stpa.py` checks it and writes the tables and Figure 3-1. It refuses a control action not examined for all four ways it can be unsafe, an unsafe control action with no loss scenario, and a scenario with neither a measure already in the concept nor a new requirement.

## 2. Losses and hazards

Losses are what the stakeholders must not suffer. L-4 is not harm in itself, but a driverless vehicle that stops in lane (DQ-016 A) can obstruct an ambulance, which turns into harm.

<!-- BEGIN GENERATED: stpa-losses (assurance/08-analyses/stpa/stpa.py) -->

| ID | Loss |
|---|---|
| L-1 | Death or injury of people outside the vehicle |
| L-2 | Death or injury of passengers |
| L-3 | Damage to vehicles or property |
| L-4 | Obstruction of traffic or of emergency services |

<!-- END GENERATED: stpa-losses -->

System-level hazards are system states that, in the worst environment, lead to a loss. Each is mapped to the HARA hazards it covers; two are not in the HARA at all.

<!-- BEGIN GENERATED: stpa-hazards (assurance/08-analyses/stpa/stpa.py) -->

| ID | System-level hazard | Losses | HARA hazards | SOTIF hazards | UCAs |
|---|---|---|---|---|---|
| HZ-1 | The vehicle comes closer to a road user or obstacle than it can stop or steer away from | L-1, L-2, L-3 | H-01, H-02, H-04, H-05, H-10 | — | 23 |
| HZ-2 | The vehicle enters a conflict area against right of way | L-1, L-2, L-3 | H-06 | — | 6 |
| HZ-3 | The vehicle decelerates hard without need | L-1, L-2, L-3 | H-03 | — | 6 |
| HZ-4 | The vehicle keeps driving when it can no longer drive safely | L-1, L-2, L-3 | H-07 | — | 9 |
| HZ-5 | The vehicle acts on commands that are stale, corrupted or not from the intended controller | L-1, L-2, L-3 | H-08 | — | 4 |
| HZ-6 | The vehicle misleads other road users about what it will do | L-1, L-3 | H-09 | — | 4 |
| HZ-7 | Passengers are exposed to traffic, or cannot leave the vehicle when they must | L-2 | — (found by STPA) | SH-16 | 6 |
| HZ-8 | The vehicle stays stopped where it obstructs traffic or emergency services for longer than needed | L-4, L-1 | — (found by STPA) | — | 5 |

<!-- END GENERATED: stpa-hazards -->

**What STPA adds to the HARA.** HZ-7 (passengers exposed to traffic, or unable to leave) and HZ-8 (the vehicle stays stopped where it blocks traffic or emergency services) are not malfunctions of the item, so the HARA, which rates malfunctions, does not have them. HZ-7 matches SOTIF hazard SH-16; HZ-8 is new, and comes from the decision that the rated minimal risk condition is a stop in lane. Both are carried into the safety case through the requirements of §6.

## 3. Control structure

![WP-A-05 Figure 3-1: the control structure. At the top, the map and update process controls Autoware, and the remote operations centre controls Autoware and the safety monitor. Autoware and the passengers are in the second row; Autoware commands the safety monitor, which commands the vehicle; passengers act on the vehicle. Feedback runs back up each link, and the vehicle also reports its state to Autoware directly. The same links are listed in the table below.](stpa/fig-a05-3-1-control-structure.svg)

*Figure 3-1. The control structure of the item in operation. Generated by `stpa/stpa.py` from `stpa/stpa.yaml`.*

The structure follows the item definition ([WP-C-01 §5](../02-concept/WP-C-01-item-definition.md#5-item-boundary-and-interfaces)): every command Autoware sends to the vehicle passes the safety monitor (I-03, I-04), the remote operations centre reaches Autoware through the AD API (I-08), and the monitor takes the release after a minimal risk condition from the remote operations centre (FSR-07.04). Autoware's internal loops (planning to control, the MRM handler) are not drawn separately; their unsafe control actions appear as Autoware's commands.

<!-- BEGIN GENERATED: stpa-actions (assurance/08-analyses/stpa/stpa.py) -->

| ID | Control action | From | To | Feedback to the controller |
|---|---|---|---|---|
| CA-06 | Install a map, software or model update | Map and update process | Autoware | — |
| CA-01 | Dispatch a trip | Remote operations centre | Autoware | Trip and MRM status; camera video; vehicle state; requests for assistance |
| CA-02 | Request an MRM or an emergency stop | Remote operations centre | Autoware | Trip and MRM status; camera video; vehicle state; requests for assistance |
| CA-03 | Give remote assistance (confirm a path) | Remote operations centre | Autoware | Trip and MRM status; camera video; vehicle state; requests for assistance |
| CA-04 | Drive the vehicle remotely | Remote operations centre | Autoware | Trip and MRM status; camera video; vehicle state; requests for assistance |
| CA-05 | Release the vehicle from a minimal risk condition | Remote operations centre | Safety monitor | — |
| CA-07 | Command acceleration or braking | Autoware | Safety monitor | Interventions and the monitor's state |
| CA-08 | Command steering | Autoware | Safety monitor | Interventions and the monitor's state |
| CA-09 | Command the gear | Autoware | Safety monitor | Interventions and the monitor's state |
| CA-10 | Command the turn indicators and hazard lights | Autoware | Safety monitor | Interventions and the monitor's state |
| CA-14 | Open a door | Passengers | Vehicle | Door state; trip status; messages from the vehicle and remote operations |
| CA-15 | Ask the vehicle to stop (in-vehicle stop request, relayed to Autoware through the AD API, I-09) | Passengers | Vehicle | Door state; trip status; messages from the vehicle and remote operations |
| CA-11 | Pass or bound the command | Safety monitor | Vehicle | Speed; steering angle; gear; by-wire faults; door state; collision signal |
| CA-12 | Intervene (brake, cut propulsion, reject steering) | Safety monitor | Vehicle | Speed; steering angle; gear; by-wire faults; door state; collision signal |
| CA-13 | Apply and hold the park brake | Safety monitor | Vehicle | Speed; steering angle; gear; by-wire faults; door state; collision signal |

<!-- END GENERATED: stpa-actions -->

## 4. Unsafe control actions

Each control action is examined for the four ways it can be unsafe. Where a type gives no hazard, the reason is stated.

<!-- BEGIN GENERATED: stpa-ucas (assurance/08-analyses/stpa/stpa.py) -->

| Control action | Not provided | Provided | Too early, too late or out of order | Stopped too soon or applied too long |
|---|---|---|---|---|
| CA-06 Install a map, software or model update | **UCA-16** The map is not updated after the road has changed [HZ-1, HZ-2] | **UCA-17** An update is installed that was not validated, or whose map, software and models do not match [HZ-1, HZ-4] | **UCA-18** An update is installed while the vehicle is in service [HZ-4] | *None: An update is a single action* |
| CA-01 Dispatch a trip | *None: Without a trip the vehicle stays parked; no hazard* | **UCA-01** A trip is dispatched into conditions outside the ODD (weather, closures) [HZ-4] | **UCA-02** A trip is dispatched before the checks after a minimal risk condition are done [HZ-4] | *None: A dispatch is a single action* |
| CA-02 Request an MRM or an emergency stop | **UCA-03** The operator does not request a stop when the vehicle is in a situation it does not recognise [HZ-2, HZ-4] | **UCA-04** The operator requests an emergency stop where hard braking itself endangers a following vehicle [HZ-3] | **UCA-05** The request arrives late because of link delay or operator workload [HZ-4] | *None: Once requested the manoeuvre runs to a stop (DQ-022 A)* |
| CA-03 Give remote assistance (confirm a path) | **UCA-06** No assistance is given for a long time to a vehicle stopped in lane [HZ-8] | **UCA-07** The operator confirms a path that is blocked or crosses a road user they cannot see [HZ-1, HZ-2] | **UCA-08** The confirmation is acted on after the scene has changed [HZ-1, HZ-5] | *None: A confirmation is a single action* |
| CA-04 Drive the vehicle remotely | **UCA-09** Remote commands stop while the vehicle is in a conflict area [HZ-1, HZ-8] | **UCA-10** A command drives toward a road user the operator cannot see on the video [HZ-1] | **UCA-11** Commands are applied late or out of sequence [HZ-5] | **UCA-12** A steering or acceleration command is still applied after the link has dropped [HZ-1, HZ-5] |
| CA-05 Release the vehicle from a minimal risk condition | **UCA-13** The vehicle is not released although it is safe to, and stays stopped in lane [HZ-8] | **UCA-14** The vehicle is released while a door is open, a passenger is getting out, or the fault persists [HZ-4, HZ-7] | **UCA-15** A release arrives late after conditions changed, or is replayed [HZ-5] | *None: A release is a single action* |
| CA-07 Command acceleration or braking | **UCA-19** No braking is commanded when a road user is in the path [HZ-1]<br>**UCA-20** No stop is commanded when a minimal risk manoeuvre is needed [HZ-4] | **UCA-21** Acceleration is commanded toward a road user, or from standstill when the path is not clear [HZ-1]<br>**UCA-22** Hard braking is commanded without need [HZ-3] | **UCA-23** Braking starts too late for the stopping distance [HZ-1] | **UCA-24** Braking is released before the road user has cleared the path [HZ-1] |
| CA-08 Command steering | **UCA-25** No steering is commanded to follow the lane through a curve [HZ-1] | **UCA-26** Steering is commanded out of the lane toward a road user or the kerb [HZ-1] | **UCA-27** Steering in a turn comes too late and cuts into the opposing lane [HZ-1, HZ-2] | **UCA-28** Steering is held too long and the vehicle overshoots its lane [HZ-1] |
| CA-09 Command the gear | *None: Without a gear command the gear does not change* | **UCA-29** Reverse is selected while moving forward, or with a road user behind [HZ-1] | **UCA-30** Park is selected before the vehicle has stopped [HZ-3] | *None: A gear change is a single action* |
| CA-10 Command the turn indicators and hazard lights | **UCA-31** No hazard lights at a stop in lane [HZ-6] | **UCA-32** An indicator shows a direction other than the manoeuvre [HZ-6] | **UCA-33** The indicator comes on too late for others to react [HZ-6] | **UCA-34** The indicator stays on after the manoeuvre [HZ-6] |
| CA-14 Open a door | **UCA-45** A door cannot be opened after a crash or in a fire [HZ-7] | **UCA-46** A door is opened on the traffic side at a stop in lane [HZ-7] | **UCA-47** A door is opened before the vehicle has stopped [HZ-7] | *None: Opening a door is a single action* |
| CA-15 Ask the vehicle to stop (in-vehicle stop request, relayed to Autoware through the AD API, I-09) | **UCA-48** A passenger who sees a danger cannot ask the vehicle to stop [HZ-7] | **UCA-49** A stop request makes the vehicle stop in a conflict area or brake hard [HZ-3, HZ-8] | *None: The request starts an MRM; its timing is that of UCA-49* | *None: A request is a single action* |
| CA-11 Pass or bound the command | **UCA-35** The monitor stops forwarding commands while the vehicle is moving, and nothing stops it [HZ-4] | **UCA-36** The monitor passes a command that leaves the envelope [HZ-1, HZ-2] | **UCA-37** The monitor checks the command against stale data from its sensors or the vehicle [HZ-1] | *None: Passing is continuous; its stopping is UCA-35* |
| CA-12 Intervene (brake, cut propulsion, reject steering) | **UCA-38** The monitor does not intervene when the envelope is violated [HZ-1, HZ-2] | **UCA-39** The monitor brakes hard for a road user that is not there [HZ-3] | **UCA-40** The intervention comes too late for the stopping distance [HZ-1] | **UCA-41** The intervention is released too soon, or held until the vehicle stops in a conflict area [HZ-1, HZ-8] |
| CA-13 Apply and hold the park brake | **UCA-42** The park brake is not applied at a minimal risk condition on a slope [HZ-1] | **UCA-43** The park brake is applied while the vehicle is moving [HZ-3] | *None: Applying it before standstill is UCA-43* | **UCA-44** The park brake is released before the release conditions hold [HZ-1, HZ-7] |

<!-- END GENERATED: stpa-ucas -->

## 5. Loss scenarios

A loss scenario explains why a controller would give an unsafe control action, or why a safe one would not be carried out. Kinds follow the Handbook: the controller's own logic, its process model (what it believes), the control path, and the controlled process.

<!-- BEGIN GENERATED: stpa-scenarios (assurance/08-analyses/stpa/stpa.py) -->

| ID | Kind | Scenario | Explains | Measures in the concept | New requirements |
|---|---|---|---|---|---|
| LS-01 | Process model | Autoware's perception misses or loses the road user (WP-C-06 FI-01 to FI-03), so it plans as if the path were clear | UCA-19, UCA-21, UCA-23, UCA-24 | FM-02, FSR-02.01, FSR-02.02, FM-04 | — |
| LS-02 | Controller | Autoware predicts a road user's motion wrongly (FI-05) and plans too little margin | UCA-21, UCA-26, UCA-27 | FM-06, FSR-06.01 | — |
| LS-03 | Control path | A command is corrupted, delayed or stuck between Autoware and the monitor | UCA-21, UCA-23, UCA-26, UCA-28 | FSR-07.01, FSR-01.01, FSR-04.01, FSR-04.02 | — |
| LS-04 | Controlled process | The vehicle brakes less than commanded (wet road, a fault in the brake path) | UCA-23, UCA-40 | FSR-02.03, FSR-02.04, FM-12, AOU-01 | — |
| LS-05 | Process model | Autoware believes it is somewhere else on the map (FI-07) | UCA-25, UCA-26, UCA-27 | FM-09, FSR-04.01 | — |
| LS-06 | Controller | Autoware's MRM handler does not start an MRM, or calls it off when the fault report clears (WP-C-12 §3.1) | UCA-20 | TR-01, TR-04, FSR-07.01, FSR-07.05 | — |
| LS-07 | Process model | Autoware or the dispatcher does not know the conditions have left the ODD (FI-12) | UCA-01, UCA-20 | FM-14, MON-01, MON-03 | SR-07 |
| LS-08 | Process model | A false detection by Autoware or by the safety channel (spray, steam, reflections) | UCA-22, UCA-39 | FSR-03.01, FSR-03.02, FM-10 | — |
| LS-09 | Process model | The remote operator's picture of the scene is late, narrow or incomplete (FI-09) | UCA-03, UCA-07, UCA-10 | FM-11, FSR-08.02, AOU-10 | — |
| LS-10 | Control path | The remote link is delayed, lost or replayed | UCA-05, UCA-08, UCA-09, UCA-11, UCA-12, UCA-15 | FSR-08.01, FSR-08.03, MON-04, TR-12 | SR-02 |
| LS-11 | Controller | The remote operator is busy with other vehicles, or the centre is understaffed | UCA-03, UCA-06, UCA-13 | AOU-09, AOU-10 | SR-01 |
| LS-12 | Process model | The operator releases the vehicle without knowing a door is open or a passenger is getting out | UCA-14 | FSR-05.01, FSR-05.05, FSR-07.04 | — |
| LS-13 | Controller | A release message is forged or replayed | UCA-15 | FSR-07.04 | SR-02 |
| LS-14 | Process model | The map process does not learn of a change to the road | UCA-16 | FM-13, MON-02 | — |
| LS-15 | Controller | An update is released without validation, or the map, software and models are mixed across versions | UCA-17, UCA-18 | — | SR-03 |
| LS-16 | Controller | Autoware commands the wrong gear | UCA-29, UCA-30 | FSR-05.03 | SR-04 |
| LS-17 | Controller | Autoware commands the wrong lamps, or none | UCA-31, UCA-32, UCA-33, UCA-34 | FSR-09.01, FSR-07.02 | — |
| LS-18 | Controller | The safety monitor has a fault of its own | UCA-35, UCA-36, UCA-38, UCA-41 | FSR-07.07, FSR-07.06, AOU-11 | — |
| LS-19 | Process model | The safety channel's data are stale or its sensors blocked (FI-08) | UCA-37, UCA-38, UCA-39, UCA-40 | FSR-07.08, FM-10 | — |
| LS-20 | Controller | The monitor's hold logic lets go before the release conditions hold | UCA-41, UCA-44 | FSR-07.04, FSR-05.01 | — |
| LS-21 | Controlled process | The park brake does not hold on the slope | UCA-42 | AOU-02, FSR-05.04, FSR-05.02 | — |
| LS-22 | Controller | A fault makes the monitor apply the park brake while moving | UCA-43 | FSR-07.07 | SR-04 |
| LS-23 | Process model | A passenger does not know the vehicle is stopped in a traffic lane, or that it is still moving | UCA-46, UCA-47 | FM-20, AOU-06, FSR-05.05 | — |
| LS-24 | Controlled process | The doors stay locked after a crash or a loss of power | UCA-45 | — | SR-05 |
| LS-25 | Controller | There is no stop request in the vehicle, or it starts a hard stop wherever the vehicle is | UCA-48, UCA-49 | TR-16 | — |
| LS-26 | Controller | The operator presses emergency stop by reflex when a firm stop would do | UCA-04 | FSR-03.02 | SR-06 |
| LS-27 | Process model | A trip is dispatched without checking the forecast and closures along the route, or before the post-MRC checks | UCA-01, UCA-02 | MON-01, FSR-07.04 | SR-07 |

<!-- END GENERATED: stpa-scenarios -->

**Remote emergency stop and the monitor (LS-26).** The monitor softens hard braking it cannot match to a road user (FSR-03.02, DQ-019 A). A remote emergency stop is such braking, so it is softened too. That is the intended behaviour, as SR-06 states, but it must be explained to remote operators: their emergency stop is a firm stop unless the safety channel sees an obstacle.

## 6. Resulting requirements

Requirements the scenarios need that the concept does not yet have. They are proposals: each is carried into the work product named in "Allocated to" when that is drafted or revised, and SR-05 becomes an assumption on the vehicle in WP-C-01 §8.

<!-- BEGIN GENERATED: stpa-requirements (assurance/08-analyses/stpa/stpa.py) -->

| ID | Requirement | Allocated to | From |
|---|---|---|---|
| SR-01 | Staff the remote operations centre so that a vehicle stopped in lane, or asking for help, reaches an operator within a time WP-O-02 sets | Remote operations (WP-O-02) | LS-11 |
| SR-02 | Authenticate every release and remote driving message, bind it to one vehicle, and reject it when stale or replayed | Safety monitor and remote operations station; cybersecurity concept (WP-C-10) | LS-10, LS-13 |
| SR-03 | Install updates only when the vehicle is out of service, after the release checks of WP-P-02, and check software, map and model versions as one set before driving | Update process (WP-P-02) and Autoware start-up checks | LS-15 |
| SR-04 | Let the monitor apply the park brake or accept park and reverse only at standstill as reported by the vehicle state (EL-06) | Safety monitor | LS-16, LS-22 |
| SR-05 | Doors can always be opened from inside with a manual release, also without the vehicle's power | Vehicle (an assumption on the vehicle, to add to WP-C-01 §8) | LS-24 |
| SR-06 | A remote emergency stop uses the firm deceleration of FSR-03.02 unless the safety channel confirms an obstacle | Safety monitor | LS-26 |
| SR-07 | Before dispatch, and while driving, check the forecast and closures along the route against the ODD | Remote operations and route planning (MON-01, MON-03) | LS-07, LS-27 |

<!-- END GENERATED: stpa-requirements -->

## 7. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Carry SR-01 to SR-07 into the work products they are allocated to | G2 |
| OI-2 | Add the manual door release as an assumption on the vehicle (SR-05, WP-C-01 §8) | G1 |
| OI-3 | Refine the control structure with Autoware's internal loops (planning, control, MRM handler) once the technical safety concept is drafted (WP-S-03) | G2 |
| OI-4 | Cross-check HZ-8 with the remote operations procedures: how long a vehicle may block a lane before it is recovered (WP-O-02) | G2 |
| OI-5 | Review the analysis with people who have operated remote operations centres and robotaxis | G2 |
