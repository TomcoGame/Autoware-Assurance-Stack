# WP-C-12 Fallback, minimal risk manoeuvres and minimal risk conditions

| Field | Value |
|---|---|
| Work product | WP-C-12 Fallback, minimal risk manoeuvres and minimal risk conditions |
| Standard reference | UL 4600 §8, §10; ISO 26262-3 §7; ISO 21448 §5, §8; ASPICE 4.0 SYS.2 |
| Version | 0.3 (the monitor's sensors failing ends in Autoware's comfortable stop under the monitor's check (DQ-021 A); every MRM runs to a stop (DQ-022 A); doors unlock at standstill (DQ-023 C); 2026-10-23). 0.2 (first content: triggers, the chain of minimal risk manoeuvres, minimal risk conditions, what the pinned Autoware does today, stopping times, the remote operations role, generated from `fallback/fallback.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | ASIL D (SG-07) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

What the vehicle does when it can no longer drive safely: what tells it so, the minimal risk manoeuvres (MRMs) it can carry out, the minimal risk conditions (MRCs) they reach, and what still stops the vehicle when the main stack has failed. With no driver, this is the whole fallback: no one takes over, so every chain of fallbacks must end in a stop the item can reach by itself. It details safety goal SG-07 of the [HARA (WP-C-03)](WP-C-03-hara.md) and the safe states of the [functional safety concept (WP-C-04 §6)](WP-C-04-functional-safety-concept.md#6-safe-states-warning-and-degradation), within the decision that the rated condition is a stop in lane and Autoware pulls over first when it still can (DQ-016 A).

Needed at gate G1 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

The triggers, manoeuvres and conditions are kept in `fallback/fallback.yaml`; `fallback/fallback.py` checks them against the functional safety concept, the ODD monitors and the assumptions, and writes the tables and Figure 3-1. It refuses a model in which a chain of fallbacks does not end in a manoeuvre rated at SG-07's ASIL, or in which a trigger takes away the element that has to answer it.

<!-- BEGIN GENERATED: fallback-summary (assurance/02-concept/fallback/fallback.py) -->

18 triggers lead to 5 minimal risk manoeuvres and 2 minimal risk conditions. 2 manoeuvres (MRM-4, MRM-5) are rated at SG-07's ASIL D, and every chain of fallbacks ends in one of them. No entry waits on a decision.

<!-- END GENERATED: fallback-summary -->

## 2. Fallback triggers (faults, ODD exit, insufficiencies, remote command)

A trigger is anything after which the vehicle should stop driving its trip: a fault, a condition outside the ODD ([WP-C-02 §4](WP-C-02-odd-and-intended-functionality.md#4-odd-monitoring)), a limit of its performance, an event such as a collision, or a request. Each has a first response; if that cannot complete, the chain of §3 takes over. "Takes away" names the elements the trigger leaves unusable, so the answer cannot rely on them. A monitor that cannot tell inside from outside counts as outside (WP-C-02 §4).

<!-- BEGIN GENERATED: fallback-triggers (assurance/02-concept/fallback/fallback.py) -->

| ID | Kind | Condition | Detected by | Takes away | First response | Related |
|---|---|---|---|---|---|---|
| TR-01 | Fault | Autoware's commands stop, arrive late or are implausible (computer, power, network or process fault) | EL-02 | EL-01 | MRM-4 | FSR-07.01, FSR-07.02, FSR-07.03, AOU-05 |
| TR-02 | Fault | Autoware's diagnostics report a fault that leaves it able to drive on with reduced margin (one sensor of a redundant set, a non-critical node) | EL-01 | — | MRM-1 | FSR-07.05 |
| TR-03 | Fault | Autoware's diagnostics report a fault that leaves it able to follow its lane but not to drive on | EL-01 | — | MRM-2 | FSR-07.05 |
| TR-04 | Fault | Autoware can no longer follow its lane (localisation, planning or control lost), or its MRM handler has no availability report for 0.5 s | EL-01 | — | MRM-3 | FSR-07.05 |
| TR-05 | Fault | The safety perception channel fails or is blocked (dirt, snow, sensor fault) | EL-02, EL-03 | EL-03 | MRM-2 | FSR-02.01, FSR-07.08, SH-14 |
| TR-06 | Fault | The vehicle reports a braking, steering or by-wire fault, or its state signals to the monitor are lost | EL-02 | — | MRM-4 | FSR-02.03, FSR-04.03, AOU-01, AOU-03 |
| TR-07 | Fault | The safety monitor detects a fault of its own, or loses its power | EL-02, EL-04 | EL-02, EL-03 | MRM-5 | FSR-07.07, FSR-07.06, AOU-11 |
| TR-08 | ODD exit | The planned route leaves the geofence or the road types of the ODD | EL-01 | — | MRM-1 | MON-01 |
| TR-09 | ODD exit | The scene disagrees with the map (closed or re-marked lanes, a work zone, a person directing traffic) | EL-01 | — | MRM-2 | MON-02, SH-07, SH-10 |
| TR-10 | ODD exit | Rain, visibility or road surface is outside the ODD, or the monitor cannot tell | EL-01 | — | MRM-1 | MON-03, SH-08 |
| TR-11 | ODD exit | The remote operations link is lost while Autoware drives | EL-01 | — | MRM-1 | MON-04, AOU-09 |
| TR-12 | ODD exit | While a remote operator drives, the link is lost or commands arrive too old, out of sequence or corrupted | EL-02 | — | MRM-4 | MON-04, FSR-08.01 |
| TR-13 | Performance limit | The safety monitor has had to correct Autoware's commands more often than WP-S-04 allows in a set time | EL-02 | — | MRM-1 | FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01 |
| TR-14 | Performance limit | Autoware cannot find a safe way on (a blocked road, an emergency vehicle it cannot yield to, unclear right of way) | EL-01 | — | MRM-2 | SH-09, SH-10, SH-11 |
| TR-15 | Event | The vehicle has had a collision | EL-02 | — | MRM-3 | AOU-12 |
| TR-16 | Request | A passenger asks to stop, through the in-vehicle stop request to be specified in WP-C-08 | EL-01 | — | MRM-1 | — |
| TR-17 | Request | The remote operations centre asks for a minimal risk manoeuvre | EL-01 | — | MRM-1 | AOU-09 |
| TR-18 | Request | The remote operations centre presses emergency stop (external emergency stop of `vehicle_cmd_gate`; QM, not relied on for safety) | EL-01 | — | MRM-3 | — |

<!-- END GENERATED: fallback-triggers -->

Two rules apply to every trigger:

- **The answer comes from an element that survives the trigger.** When Autoware is lost (TR-01) the safety monitor stops the vehicle; when the monitor is lost (TR-07) the vehicle's own drive-by-wire does (AOU-11). The generator enforces this.
- **The remote operations centre is told of every trigger and every MRM** (§7), but no trigger waits for it: the vehicle reaches an MRC by itself even with the link down (AOU-09).

TR-05, the loss of the safety monitor's own sensors, has no good answer: Autoware's stop is unchecked for road users, and the monitor's stop is rated but just as blind. The lead decided (DQ-021 A, 2026-10-23) that Autoware makes its comfortable stop in lane while the monitor checks speed, deceleration and steering against the vehicle's own signals, and stops the vehicle itself if Autoware does not slow as expected (FSR-07.08). For about 16 s from 50 km/h (§6) only Autoware looks for road users.

## 3. Minimal risk manoeuvres (comfortable stop, emergency stop, pull over)

![WP-C-12 Figure 3-1: fallback chain](fallback/fig-c12-3-1-fallback.svg)

*Figure 3-1. The chain of minimal risk manoeuvres: each trigger starts one, a manoeuvre that cannot complete hands over to the next, and each ends in a minimal risk condition. Generated by `fallback/fallback.py` from `fallback/fallback.yaml`.*

<!-- BEGIN GENERATED: fallback-mrms (assurance/02-concept/fallback/fallback.py) -->

| ID | Manoeuvre | Carried out by | ASIL | Chosen when | Cannot complete when | Then | Reaches | In the pinned Autoware |
|---|---|---|---|---|---|---|---|---|
| MRM-1 | Pull over to a mapped safe stopping place | EL-01 Autoware computer | QM | Autoware can still drive safely and a mapped safe stopping place is within reach (DQ-016 A) | No stopping place is within reach or free, or Autoware's state gets worse on the way | MRM-2 | MRC-1 | No operator in the pinned Autoware (MAN-10); to be built, then `use_pull_over` turned on |
| MRM-2 | Comfortable stop in lane | EL-01 Autoware computer | QM | Autoware can follow its lane but should not drive on | Autoware loses the ability to follow its lane, or does not slow as planned | MRM-3 | MRC-2 | `autoware_mrm_comfortable_stop_operator`; off by default (`use_comfortable_stop: false`) |
| MRM-3 | Emergency stop in lane | EL-01 Autoware computer | QM | Autoware can still command braking but not follow its lane, or must stop now | Autoware's commands stop or the vehicle does not decelerate as commanded (the monitor sees it, TR-01) | MRM-4 | MRC-2 | `autoware_mrm_emergency_stop_operator`; the only MRM the pinned defaults select |
| MRM-4 | Safety monitor stop in lane | EL-02 Safety monitor | D | Autoware cannot be relied on to stop, or the monitor itself must stop the vehicle (FSR-07.02) | The monitor itself fails (TR-07) | MRM-5 | MRC-2 | Not Autoware; part of the safety monitor to be built (F-10) |
| MRM-5 | Vehicle's own stop on loss of the monitor | EL-04 Vehicle drive-by-wire | D | Commands from the safety monitor stop for longer than WP-S-04 allows | Not covered further; AOU-01 makes the braking path single-fault tolerant | — | MRC-2 | Not Autoware; a function of the vehicle's drive-by-wire (AOU-11) |

<!-- END GENERATED: fallback-mrms -->

The first three manoeuvres are Autoware's and are not rated (DQ-002 A): they are the comfortable way to stop, and they keep the rated ones rare. MRM-4 and MRM-5 are what the safety case relies on for SG-07.

### 3.1 What the pinned Autoware does today

A reading of `autoware_mrm_handler` and the two stop operators in `autoware_universe` 0.52.1 (`system/autoware_mrm_handler/src/mrm_handler/mrm_handler_core.cpp` and the packages' `config/*.param.yaml`) found:

- **With its default parameters, the only MRM it selects is the emergency stop.** `use_comfortable_stop` and `use_pull_over` are both `false`; the handler falls through to `EMERGENCY_STOP`. No pull-over operator package exists (WP-C-02 MAN-10).
- **It drives on as soon as the fault report clears.** When the current operation mode is available again, the handler returns to `NORMAL` and cancels the MRM, even after the vehicle has stopped. With `use_emergency_holding: true` it stays in emergency only after a fault that has lasted `timeout_emergency_recovery` (5 s by default).
- **It does nothing once stopped.** In `MRM_SUCCEEDED` the code has a to-do for the MRC behaviour and returns; the gear is put in park only with `use_parking_after_stopped: true` (default `false`). During an emergency it switches the hazard lights on and the turn indicators off by default.
- **It starts an MRM only while the vehicle reports autonomous control mode.** Whether that holds while a remote operator drives through the external command path is to be confirmed in WP-W-03.
- **A missing availability report is itself an emergency.** After 0.5 s without one, the handler selects the emergency stop.

None of this is a defect for a supervised vehicle; for a driverless one it means Autoware's configuration must change, and the hold after a stop cannot be left to Autoware:

| Parameter of `autoware_mrm_handler` | Pinned default | Needed here | Why |
|---|---|---|---|
| `use_comfortable_stop` | `false` | `true` | MRM-2 exists; without it every Autoware MRM is an emergency stop |
| `use_pull_over` | `false` | `true` once the operator exists | MRM-1 (DQ-016 A, MAN-10) |
| `use_emergency_holding` | `false` | `true` | An MRM must not be called off by itself (DQ-022 A) |
| `timeout_emergency_recovery` | 5.0 s | 0 s (DQ-022 A) | Any fault that starts an MRM keeps the vehicle stopped |
| `use_parking_after_stopped` | `false` | `true` | Park gear at the MRC, in addition to the monitor's park brake (FSR-05.04) |
| `turning_hazard_on.emergency` | `true` | `true` | Hazard lights during and after an MRM |

These are proposals for the configuration managed under WP-W-03; the safety monitor's hold after any stop (FSR-07.04) does not depend on them.

### 3.2 Rules for every manoeuvre

- A manoeuvre runs to a stop once started, even if its fault clears, and the vehicle then waits for the remote operations centre (DQ-022 A, 2026-10-23).
- The safety monitor checks every Autoware manoeuvre like any other driving: its envelope still applies (FSR-01.01, FSR-02.02, FSR-04.01, FSR-06.01).
- The monitor softens hard braking it cannot match to a road user or obstacle (FSR-03.02, DQ-019 A). If WP-S-04 sets that firm level below the 2.5 m/s² of Autoware's emergency stop, an unconfirmed MRM-3 becomes a firm stop and takes longer; WP-S-04 sets the two together.
- Hazard lights are on from the start of every MRM (F-12, FSR-09.01).

## 4. Minimal risk conditions and their safety

<!-- BEGIN GENERATED: fallback-mrcs (assurance/02-concept/fallback/fallback.py) -->

| ID | Condition | State | Held by | ASIL | Passengers | Left when |
|---|---|---|---|---|---|---|
| MRC-1 | Stopped at the kerb | Stopped in a mapped safe stopping place, hazard lights on, park brake applied, gear in park | EL-01, EL-02, EL-05 | QM | Doors unlock at standstill (DQ-023 C) | On release by the remote operations centre with the conditions of FSR-05.01 met (FSR-07.04) |
| MRC-2 | Stopped in lane | Stopped in its lane, hazard lights on, park brake applied and held by the safety monitor | EL-02, EL-05 | D | Doors unlock at standstill, as in a taxi (DQ-023 C); the vehicle tells passengers to leave on the kerb side and to watch for traffic (SH-16, WP-O-03) | On release by the remote operations centre with the conditions of FSR-05.01 met (FSR-07.04); Autoware then drives on, a remote operator moves the vehicle, or it is recovered |

<!-- END GENERATED: fallback-mrcs -->

**Why a stop in lane is acceptable as the rated condition.** It is the one condition the safety monitor can always reach without Autoware, and a stopped vehicle with hazard lights is something other road users meet every day (a breakdown, a delivery stop). Its residual risks are a following vehicle striking it, and passengers leaving it into traffic. The first is reduced by a comfortable stop wherever Autoware can still make one and by hazard lights. For the second, the lead decided that the doors unlock at standstill, as in a taxi (DQ-023 C, 2026-10-23): nothing keeps a passenger from stepping out on the traffic side, so the measures are hazard lights and telling passengers to leave on the kerb side and watch for traffic (WP-O-03), and the residual risk of SH-16 counts against the SOTIF acceptance criteria (WP-C-05 AC-02). How long a vehicle may stand in lane before it is recovered is set with the remote operations procedures (WP-O-02).

**Holding the condition.** A rated MRC needs the vehicle held, not just stopped: the monitor applies the park brake (FSR-05.04, AOU-02) and keeps propulsion off until the remote operations centre releases it and the conditions of FSR-05.01 hold (FSR-07.04). This does not rely on Autoware's handler, which neither holds nor parks by default (§3.1).

## 5. Element that executes the fallback when the main stack is lost (DQ-002)

The safety monitor (EL-02) is the element that stops the vehicle when Autoware is lost (DQ-002 A). For that it needs, independently of the Autoware computer:

| Need | Provided by | Requirement |
|---|---|---|
| To see that Autoware is lost | The monitor's own checks on Autoware's commands | FSR-07.01 |
| To see the road ahead while stopping | The safety perception channel, own sensors (DQ-018 A) | FSR-02.01 |
| To know speed, steering and faults | Vehicle state sensing, not through Autoware | FSR-01.05, AOU-03 |
| To brake, steer and hold | Drive-by-wire and park brake commandable by the monitor | FSR-01.03, FSR-02.04, FSR-05.04, AOU-01, AOU-02 |
| Power | A supply that survives the Autoware computer's | FSR-07.03, AOU-05 |

**When the monitor itself is lost** (TR-07), nothing in the item is left to stop the vehicle. The monitor is therefore fail-silent: on a fault of its own it stops sending commands (FSR-07.07), and the vehicle's drive-by-wire brakes to a standstill when the monitor's commands stop (MRM-5, FSR-07.06, AOU-11). This is the last link of every chain, and it is outside the item: the vehicle chosen at G2 must provide it (DQ-008).

## 6. Fallback timing (input to WP-S-04)

How long each manoeuvre takes, and how far it travels, from the top of the speed range (WP-C-02 ODD-20). The figures are computed from the deceleration and jerk in the model, with the braking ramped up at the given jerk; they start when braking starts, so detection and reaction times come on top, and they assume the deceleration is achieved on the road surface of the ODD.

<!-- BEGIN GENERATED: fallback-timing (assurance/02-concept/fallback/fallback.py) -->

| MRM | Deceleration (m/s²) | Jerk (m/s³) | Time to stop from 50 km/h | Distance | Source |
|---|---|---|---|---|---|
| MRM-1 Pull over to a mapped safe stopping place | — | — | — | — | Comfortable deceleration, set with the operator |
| MRM-2 Comfortable stop in lane | 1 | 0.3 | 15.6 s | 119 m | Default parameters of `autoware_mrm_comfortable_stop_operator` (0.52.1) |
| MRM-3 Emergency stop in lane | 2.5 | 1.5 | 6.4 s | 50 m | Default parameters of `autoware_mrm_emergency_stop_operator` (0.52.1) |
| MRM-4 Safety monitor stop in lane | — | — | — | — | Firm level of FSR-03.02, raised to emergency braking only when FSR-02.02 requires it; set in WP-S-04 |
| MRM-5 Vehicle's own stop on loss of the monitor | — | — | — | — | Set by the vehicle supplier within the limits WP-S-04 gives |

<!-- END GENERATED: fallback-timing -->

The values for MRM-2 and MRM-3 are the pinned Autoware's defaults, not decided values. WP-S-04 sets the timing the rated chain needs:

| Quantity | Used by | Bounded by |
|---|---|---|
| Time to detect that Autoware's commands are lost, late or implausible | TR-01, FSR-07.01 | The fault tolerant time interval of SG-07 and of the goals Autoware's loss can violate (SG-01, SG-02, SG-04) |
| Deceleration of the monitor's stop, and when it rises to emergency | MRM-4, FSR-03.02, FSR-02.02 | SG-02 against SG-03 (DQ-019 A) |
| Time after which the vehicle stops on loss of the monitor's commands | MRM-5, FSR-07.06 | The same intervals, less the monitor's own detection time |
| Age bound of remote commands | TR-12, FSR-08.01 | AOU-10 |
| Number of envelope corrections that ends the trip | TR-13 | To be set from fleet data; a proposal, not a safety bound |

## 7. Remote operations role

The remote operations centre is not part of the rated fallback: the item reaches an MRC on its own, and nothing in §2 waits for the centre (AOU-09). Its role is everything around that:

| When | What the centre does | Bounded by |
|---|---|---|
| Any trigger or MRM | Is alerted with the trigger, the manoeuvre and the vehicle's position and camera views | WP-O-02 |
| While Autoware drives | May ask for an MRM (TR-17) or press emergency stop (TR-18); both go through Autoware and are not relied on for safety | — |
| At an MRC | Talks to the passengers, and calls for recovery or other help | WP-O-02, WP-O-03 |
| To leave an MRC | Releases the vehicle once the conditions of FSR-05.01 hold; Autoware drives on, or a remote operator moves the vehicle out of the lane | FSR-07.04; in `REMOTE` mode the monitor's envelope still applies (FSR-08.02) |
| Stuck, not faulty (TR-09, TR-14) | Gives remote assistance, such as confirming a path round a blockage, which Autoware then drives under the monitor | WP-C-04 §2 |

The vehicle does not resume a trip after an MRC without the centre, so a vehicle that has lost its link stays stopped until the link returns or the vehicle is recovered.

## 8. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Set the expected deceleration profile and tolerance the monitor checks Autoware's stop against when EL-03 has failed (FSR-07.08, WP-S-04) | G2 |
| OI-2 | Set Autoware's handler parameters of §3.1 in WP-W-03 | G2 |
| OI-3 | Carry the door rule (DQ-023 C) into WP-C-08 and the passenger information into WP-O-03 | G1 |
| OI-4 | Specify the pull-over operator (MRM-1) and the mapped safe stopping places it may use (WP-C-01 OI-3) | G2 |
| OI-5 | Set the timing of §6 in WP-S-04 | G2 |
| OI-6 | Confirm with the vehicle supplier that the drive-by-wire stops on loss of the monitor's commands and reports collisions (AOU-11, AOU-12) | G2 |
| OI-7 | Confirm in WP-W-03 whether Autoware's MRM handler runs while a remote operator drives (§3.1) | G2 |
| OI-8 | Specify the in-vehicle stop request (TR-16) in WP-C-08 | G1 |
