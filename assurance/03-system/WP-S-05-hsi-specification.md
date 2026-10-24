# WP-S-05 Hardware-software interface, including the drive-by-wire interface

| Field | Value |
|---|---|
| Work product | WP-S-05 Hardware-software interface, including the drive-by-wire interface |
| Standard reference | UL 4600 §10; ISO 26262-4 §6; ASPICE 4.0 SYS.3 |
| Version | 0.2 (first content: interfaces, signals with their protection, receive timeouts and maximum periods, clocks, and the hardware diagnostics the monitor's software uses, generated from `hsi/hsi.yaml`; 2026-10-24). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | ASIL D |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

The hardware-software interface (HSI) of the item: what crosses each link of the architecture of [WP-S-03](WP-S-03-technical-safety-concept-architecture.md), including the drive-by-wire command and status interface; which clocks the signals are stamped against; and which hardware safety features the software of the item's own processors relies on (ISO 26262-4 §6.4.7). It is where the technical safety requirements of [WP-S-02](WP-S-02-technical-safety-requirements.md) meet hardware, and the start of the hardware and software requirements of WP-H-01 and the software work products.

Needed at gate G2 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: hsi-summary (assurance/03-system/hsi/hsi.py) -->

19 signals cross the 9 interfaces of the WP-S-03 architecture; 12 feed a time-critical mechanism and get a receive timeout from its detection budget. The shortest is SIG-01 remote driving command at 143 ms, so it must be sent at least every 48 ms. 19 signals are protected end to end or signed; 2 clocks and 8 hardware diagnostics complete the interface.

<!-- END GENERATED: hsi-summary -->

The model is kept in `hsi/hsi.yaml`; `hsi/hsi.py` checks it and writes the tables and Figure 1-1. It refuses a model in which:

- a link of WP-S-03 has no interface;
- a signal serves a requirement on neither end of its interface;
- a rated signal is unprotected, or a signal on an untrusted transport is not signed;
- a requirement on a supplier component neither crosses an interface nor is stated to be internal to the supplier.

**The vehicle side is provisional.** The drive-by-wire, vehicle state, park brake and door interfaces are set by the vehicle chosen at G2 (DQ-008). What this work product fixes is what must cross them and how fast. The bus, message layout and supplier's own protection follow from the vehicle and are agreed in the development interface agreement (WP-M-11).

### 1.1 Interfaces

<!-- BEGIN GENERATED: hsi-interfaces (assurance/03-system/hsi/hsi.py) -->

| ID | From → to | Item interface | Medium | Signals |
|---|---|---|---|---|
| IF-01 | CMP-11 Remote operations station → CMP-02 Safety monitor controller | I-08 | Cellular link to the vehicle, then through the Autoware computer's network to the monitor **Untrusted transport.** | SIG-01, SIG-02 |
| IF-02 | CMP-01 Autoware computer → CMP-02 Safety monitor controller | I-03 | Dedicated point-to-point Automotive Ethernet, not shared with Autoware's other traffic (proposed) | SIG-03, SIG-04, SIG-05, SIG-06 |
| IF-03 | CMP-04 Safety LiDAR → CMP-03 Safety channel processor | I-13 | Automotive Ethernet from the LiDAR, as the sensor offers (WP-H-02) | SIG-07 |
| IF-04 | CMP-05 Safety radar → CMP-03 Safety channel processor | I-13 | CAN FD or Automotive Ethernet from the radar, as the sensor offers (WP-H-02) | SIG-08 |
| IF-05 | CMP-03 Safety channel processor → CMP-02 Safety monitor controller | I-13 | Dedicated point-to-point link between the two processors, inside the monitor's enclosure (proposed) | SIG-09, SIG-10 |
| IF-06 | CMP-02 Safety monitor controller → CMP-06 Drive-by-wire | I-04 | The vehicle's by-wire bus, set by the vehicle (DQ-008); the only command path into the drive-by-wire | SIG-11, SIG-12, SIG-13 |
| IF-07 | CMP-07 Vehicle state sensing → CMP-02 Safety monitor controller | I-05 | A vehicle bus segment the Autoware computer is not connected to (AOU-03), set by the vehicle (DQ-008) | SIG-14, SIG-15, SIG-16 |
| IF-08 | CMP-02 Safety monitor controller → CMP-08 Park brake | I-04 | The vehicle's by-wire bus, set by the vehicle (DQ-008) | SIG-17, SIG-18 |
| IF-09 | CMP-09 Door system → CMP-02 Safety monitor controller | I-05 | The vehicle's by-wire bus, set by the vehicle (DQ-008) | SIG-19 |

<!-- END GENERATED: hsi-interfaces -->

### 1.2 Protection, timeouts and periods

Every signal carries end-to-end protection in the manner of the AUTOSAR E2E profiles: a checksum over the data and a data identifier, a sequence counter, and a timeout at the receiver. This lets the receiver detect corruption, repetition, loss, delay and masquerade by another sender on the bus. Remote commands cross a cellular link and the Autoware computer's network, which are not trusted, so they are signed (CSR-01) and aged instead (TSR-05.02).

A signal read by a time-critical mechanism must arrive within that mechanism's detection budget (WP-S-04 §4, worst case), and the receive timeout is that budget. So that one lost frame is not yet a fault, the signal is sent at least three times per timeout. That ratio is a design proposal of this work product (`frames_per_timeout`), not a decision of the lead. Only the requirements at the receiving end set the timeout. A signal whose receiver has no time-critical mechanism is an event, checked for age and sequence when it is used.

Each signal lists the ASIL of the requirements it serves at its sending and at its receiving end. Where the sender is QM (the Autoware computer, the vehicle side before its supplier rates it), the receiver's checks carry the integrity, which is the point of the monitor architecture (DQ-002 A).

![WP-S-05 Figure 1-1: a horizontal bar chart of each timed signal's receive timeout, shortest first, with a marker at the longest period that still fits three frames in the timeout. The remote driving command and Autoware's control command and heartbeat are tightest at 143 ms (sent at least every 48 ms), set by the command stream watchdog SM-05. The safety channel's report and status, the bounded motion command, the propulsion cut, the drive-by-wire status and the vehicle state follow at 179 ms (sent at least every 60 ms), and the safety sensors' frames at 200 ms (every 67 ms). The same values are in the tables below.](hsi/fig-s05-1-1-signals.svg)

*Figure 1-1. Receive timeout and longest period of each timed signal. Generated by `hsi/hsi.py` from `hsi/hsi.yaml`.*

## 2. Compute and safety monitor interfaces

The Autoware computer reaches the vehicle only through the monitor (I-03, I-04). The safety channel processor reports to the monitor on its own link (I-13). Remote commands arrive from the remote operations station.

<!-- BEGIN GENERATED: hsi-signals-compute (assurance/03-system/hsi/hsi.py) -->

| ID | Signal | From → to | Content | Sender ASIL | Receiver ASIL | Protection | Receive timeout | Maximum period | Serves |
|---|---|---|---|---|---|---|---|---|---|
| SIG-01 | Remote driving command | Remote operations station → Safety monitor controller (IF-01) | Acceleration, steering angle and rate, gear; time stamp, sequence number and signature (CSR-01) | C | C | Signed (CSR-01) and aged | 143 ms (SM-05) | 48 ms | TSR-05.02, TSR-01.06, TSR-19.01 |
| SIG-02 | Release after a minimal risk condition | Remote operations station → Safety monitor controller (IF-01) | Release request for one vehicle; time stamp, sequence number and signature (CSR-01) | C | D | Signed (CSR-01) and aged | Event; checked when used | — | TSR-06.05, TSR-19.01 |
| SIG-03 | Control command | Autoware computer → Safety monitor controller (IF-02) | Longitudinal acceleration (negative for braking), steering angle and steering rate, gear, motion request; sequence counter | QM | D, C | End-to-end | 143 ms (SM-05) | 48 ms | TSR-05.01, TSR-01.02, TSR-01.03, TSR-02.01, TSR-02.02, TSR-04.01, TSR-06.02, TSR-06.04 |
| SIG-04 | Lamp command | Autoware computer → Safety monitor controller (IF-02) | Turn indicator left, right or off; hazard lights | QM | C | End-to-end | Event; checked when used | — | TSR-07.01 |
| SIG-05 | Autoware heartbeat and state | Autoware computer → Safety monitor controller (IF-02) | Alive counter, operation mode, Autoware's own MRM state | QM | D | End-to-end | 143 ms (SM-05) | 48 ms | TSR-05.01, TSR-03.04 |
| SIG-06 | Monitor status to Autoware | Safety monitor controller → Autoware computer (IF-02) | Whether the monitor is limiting the command, the safety channel has failed (Autoware is to stop comfortably), MRM-4 is active, or the vehicle is held | D | QM | End-to-end | Event; checked when used | — | TSR-03.04 |
| SIG-09 | Obstacle and free-space report | Safety channel processor → Safety monitor controller (IF-05) | Road users and obstacles with position, velocity and extent; occluded zones beside the path; near field front and rear clear; whether braking above the firm level is confirmed; frame time stamp | D, C | D, C | End-to-end | 179 ms (SM-02) | 60 ms | TSR-09.01, TSR-04.02, TSR-01.01, TSR-01.04, TSR-01.05, TSR-02.02, TSR-04.01, TSR-06.02, TSR-06.04 |
| SIG-10 | Safety channel status | Safety channel processor → Safety monitor controller (IF-05) | Each sensor's state (available, degraded, blocked, lost) and the processor's own state, failed or not | D | D | End-to-end | 179 ms (SM-03) | 60 ms | TSR-10.01, TSR-09.07, TSR-03.04 |

<!-- END GENERATED: hsi-signals-compute -->

The monitor reports its state back to Autoware (SIG-06), so that Autoware can stop comfortably when the safety channel has failed (TSR-03.04, DQ-021 A) and knows when its command is being limited. Autoware must not rely on that status for anything rated.

## 3. Drive-by-wire command and feedback signals

The monitor is the only sender of motion commands to the drive-by-wire (I-04). The vehicle state comes back on a path the Autoware computer is not connected to (AOU-03).

<!-- BEGIN GENERATED: hsi-signals-vehicle (assurance/03-system/hsi/hsi.py) -->

| ID | Signal | From → to | Content | Sender ASIL | Receiver ASIL | Protection | Receive timeout | Maximum period | Serves |
|---|---|---|---|---|---|---|---|---|---|
| SIG-11 | Bounded motion command | Safety monitor controller → Drive-by-wire (IF-06) | Acceleration or deceleration, steering angle and rate, gear, lamps including hazard lights; alive counter that the vehicle watches for MRM-5 | D, C | D | End-to-end | 179 ms (SM-14) | 60 ms | TSR-01.02, TSR-01.03, TSR-02.01, TSR-06.01, TSR-07.01, TSR-08.02, TSR-14.01 |
| SIG-12 | Propulsion cut and brake switch | Safety monitor controller → Drive-by-wire (IF-06) | Propulsion cut; switch to the secondary brake path | D | D | End-to-end | 179 ms (SM-03) | 60 ms | TSR-11.01, TSR-03.01, TSR-03.02, TSR-03.05 |
| SIG-13 | Drive-by-wire status | Drive-by-wire → Safety monitor controller (IF-06) | Control mode, active brake path, propulsion cut acknowledged, by-wire faults | D | D | End-to-end | 179 ms (SM-03) | 60 ms | TSR-03.05, TSR-03.02 |
| SIG-14 | Longitudinal vehicle state | Vehicle state sensing → Safety monitor controller (IF-07) | Speed, longitudinal acceleration, standstill; their fault flags | D | D | End-to-end | 179 ms (SM-03) | 60 ms | TSR-15.01, TSR-01.07, TSR-03.01, TSR-03.02, TSR-06.03 |
| SIG-15 | Steering and gear state | Vehicle state sensing → Safety monitor controller (IF-07) | Steering angle, gear engaged, turn indicator state; their fault flags | D | D, C | End-to-end | 179 ms (SM-03) | 60 ms | TSR-15.02, TSR-03.03, TSR-07.01 |
| SIG-16 | Collision detected | Vehicle state sensing → Safety monitor controller (IF-07) | Collision flag from the vehicle's crash detection, for example the airbag control unit | QM | QM | End-to-end | Event; checked when used | — | AOU-12, TR-15 |
| SIG-17 | Park brake command | Safety monitor controller → Park brake (IF-08) | Apply or release | D | D | End-to-end | Event; checked when used | — | TSR-16.01, TSR-06.03 |
| SIG-18 | Park brake state | Park brake → Safety monitor controller (IF-08) | Applied, released or fault | D | D | End-to-end | Event; checked when used | — | TSR-16.01, TSR-06.02 |
| SIG-19 | Door state | Door system → Safety monitor controller (IF-09) | Each door open or closed and locked; fault flag | D | D | End-to-end | Event; checked when used | — | TSR-17.01, TSR-06.02, AOU-06 |

<!-- END GENERATED: hsi-signals-vehicle -->

The alive counter of SIG-11 is what the vehicle watches for its own stop (MRM-5, TSR-14.01). Its timeout at the vehicle is P-08, the detection budget of SM-14. The monitor's output disable (HD-06) silences SIG-11, SIG-12 and SIG-17 at once.

Some supplier requirements are properties inside the supplier's element and cross no interface:

<!-- BEGIN GENERATED: hsi-internal (assurance/03-system/hsi/hsi.py) -->

| Requirement | Component | Why it crosses no interface |
|---|---|---|
| TSR-12.01 | CMP-06 Drive-by-wire | The secondary brake path is inside the drive-by-wire; the monitor only selects it (SIG-12) and sees which is active (SIG-13) |
| TSR-13.01 | CMP-06 Drive-by-wire | Fault-tolerant steering is inside the drive-by-wire |
| TSR-18.01 | CMP-10 Monitor power supply | Power is a supply |

<!-- END GENERATED: hsi-internal -->

## 4. Sensor interfaces and time synchronisation

The safety channel's sensors reach its processor on their own links, not through the Autoware computer (I-13, DQ-018 A). Autoware's own sensors (I-02) are outside the rated path and are specified with Autoware's software architecture (WP-W-03).

<!-- BEGIN GENERATED: hsi-signals-sensors (assurance/03-system/hsi/hsi.py) -->

| ID | Signal | From → to | Content | Sender ASIL | Receiver ASIL | Protection | Receive timeout | Maximum period | Serves |
|---|---|---|---|---|---|---|---|---|---|
| SIG-07 | LiDAR point cloud | Safety LiDAR → Safety channel processor (IF-03) | Points with range, angle and intensity, time-stamped against CK-01; sensor fault and blockage flags | C, B(D) | D | End-to-end | 200 ms (SM-09) | 67 ms | TSR-09.02, TSR-09.04, TSR-09.01, TSR-10.01 |
| SIG-08 | Radar detections | Safety radar → Safety channel processor (IF-04) | Detections with range, angle and radial velocity, time-stamped against CK-01; sensor fault and blockage flags | C, B(D) | D | End-to-end | 200 ms (SM-09) | 67 ms | TSR-09.03, TSR-09.05, TSR-09.01, TSR-10.01 |

<!-- END GENERATED: hsi-signals-sensors -->

**Finding: the safety LiDAR must run at 15 Hz or faster.** The safety channel's signals must arrive within 200 ms and at least three times in that time, so every 67 ms or sooner. A LiDAR scanning at 10 Hz delivers a frame every 100 ms and could not meet it. The requirement goes to the sensor choice (WP-H-02, OI-2). It is not met by lowering the frames per timeout or lengthening the budget.

<!-- BEGIN GENERATED: hsi-clocks (assurance/03-system/hsi/hsi.py) -->

| ID | Clock | Master → clients | Method | Bound | Serves |
|---|---|---|---|---|---|
| CK-01 | Safety channel time | CMP-03 → CMP-04, CMP-05 | Generalised precision time protocol (IEEE 802.1AS) from the safety channel processor (proposed) | Set with the sensors (WP-H-02) so that fusing LiDAR and radar frames misplaces no road user by more than the detection needs | TSR-09.01 |
| CK-02 | Remote command time | CMP-11 → CMP-02 | Both sides disciplined to GNSS time, with a monitored holdover on the vehicle (proposed) | Its error counts against the age bound P-09, so it is kept a small part of it | TSR-05.03, TSR-19.01 |

<!-- END GENERATED: hsi-clocks -->

The monitor does not need a common clock with the Autoware computer. It judges Autoware's commands by their arrival, sequence and counters (TSR-05.01). Only remote commands need a shared time, because their age is measured from the operator's station (CK-02).

## 5. Diagnostics and status signals

Hardware features of the item's own processors that their software relies on to detect their own faults and to fall silent. Their diagnostic coverage is shown in WP-H-04; the parts are selected under DQ-030 A. The vehicle-side components diagnose themselves under their supplier's safety manual and report through the status signals above.

<!-- BEGIN GENERATED: hsi-diagnostics (assurance/03-system/hsi/hsi.py) -->

| ID | Component | Hardware feature | How the software uses it | Serves |
|---|---|---|---|---|
| HD-01 | CMP-02 Safety monitor controller | Lockstep cores | A lockstep mismatch raises a fault the software cannot mask; the fault handler drives the output disable (HD-06) | TSR-08.01, TSR-08.02 |
| HD-02 | CMP-02 Safety monitor controller | ECC on RAM and flash | Corrected errors are counted and reported; an uncorrectable error is handled as HD-01 | TSR-08.01 |
| HD-03 | CMP-02 Safety monitor controller | Memory protection unit | Keeps the communication stacks from writing the envelope software's memory; a violation is handled as HD-01 | TSR-08.01 |
| HD-04 | CMP-02 Safety monitor controller | External window watchdog | Serviced by the envelope task in a fixed window each cycle; a missed or early service drives the output disable | TSR-08.01, TSR-08.02 |
| HD-05 | CMP-02 Safety monitor controller | Independent clock monitor | Compares the core clock with a second oscillator; a deviation is handled as HD-01, and the clock of CK-02 is checked against it | TSR-08.01, TSR-05.03 |
| HD-06 | CMP-02 Safety monitor controller | Output disable | A hardware path that silences the transmitters to the drive-by-wire and park brake, so the vehicle's own stop takes over (MRM-5) | TSR-08.02, TSR-14.01 |
| HD-07 | CMP-02 Safety monitor controller | Supply voltage monitor | Under- and over-voltage drive the output disable; a supply warning is reported in SIG-06 | TSR-08.01, TSR-18.01 |
| HD-08 | CMP-03 Safety channel processor | Safety island with lockstep, ECC and watchdog | The safety island checks the perception cores and itself; a fault sets the processor failed in SIG-10 or stops SIG-10, which the monitor treats alike | TSR-09.07 |

<!-- END GENERATED: hsi-diagnostics -->

Writing this work product added one requirement to WP-S-02. The safety channel processor must detect its own faults and report itself failed or fall silent (TSR-09.07). Until then WP-S-02 covered the faults of its sensors (TSR-10.01) but not those of the processor itself.

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Replace the vehicle-side media, message layouts and protection with the chosen vehicle's, and agree them in the DIA (DQ-008, WP-M-11) | G2 |
| OI-2 | Choose a safety LiDAR and radar that deliver a frame at least every 67 ms, and set the bound of CK-01 with them (WP-H-02) | G2 |
| OI-3 | Set the error bound of CK-02 within the age bound P-09, and its holdover when GNSS is lost | G2 |
| OI-4 | Select the parts for CMP-02 and CMP-03 and confirm that their safety manuals provide HD-01 to HD-08 (DQ-030 A, WP-H-01) | G2 |
| OI-5 | Rate the collision signal SIG-16 once the response to a collision (TR-15) is given a rated requirement, or confirm it stays QM | G2 |
