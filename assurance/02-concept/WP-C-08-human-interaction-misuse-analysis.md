# WP-C-08 Interaction with passengers, road users and remote operators; foreseeable misuse

| Field | Value |
|---|---|
| Work product | WP-C-08 Interaction with passengers, road users and remote operators; foreseeable misuse |
| Standard reference | UL 4600 §7; ISO 26262-3 §6; ISO 21448 §6 |
| Version | 0.2 (first content: human roles, interactions, errors and foreseeable misuse with the measures that meet them, external communication of intent, remote assistance and operation, resulting requirements, generated from `misuse/misuse.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1; a human factors specialist) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

How passengers, other road users, remote operators and first responders interact with the vehicle, and how they can misuse it. With no driver, nobody in the vehicle can correct a passenger, explain the vehicle's intent to a pedestrian, or take instructions from a police officer; each of those has to be designed in or handed to the remote operations centre.

Needed at gate G1 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: misuse-summary (assurance/02-concept/misuse/misuse.py) -->

8 human roles and 23 entries: 11 foreseeable misuse, 5 errors by trained people, 7 interactions the item must support. 13 are met by measures already in the concept; 10 need one of the 10 new requirements, and entries marked proposed wait on DQ-029.

<!-- END GENERATED: misuse-summary -->

The entries are kept in `misuse/misuse.yaml`; `misuse/misuse.py` checks each one against the analyses it relates to and writes the tables and Figure 5-1. It refuses a role with no entry, and an entry with neither a measure already in the concept nor a new requirement. Most entries are met by measures the HARA, SOTIF, STPA, TARA and fallback work already put in place; this work product mostly confirms them from the human side and fills what is left.

## 2. Human roles (passenger, pedestrian, cyclist, other driver, remote operator, first responder)

<!-- BEGIN GENERATED: misuse-roles (assurance/02-concept/misuse/misuse.py) -->

| ID | Role | Misuse | Errors | Interactions |
|---|---|---|---|---|
| R-01 | Passenger | MU-01, MU-02, MU-03, MU-04, MU-05, MU-07 | — | MU-06 |
| R-02 | Child, elderly or less mobile passenger | MU-09 | — | MU-08 |
| R-03 | Pedestrian | MU-10, MU-12 | — | MU-11 |
| R-04 | Cyclist or scooter rider | — | — | MU-13 |
| R-05 | Driver of another vehicle | MU-14 | — | MU-15 |
| R-06 | Remote operator | — | MU-16, MU-17, MU-18, MU-19 | — |
| R-07 | First responder (police, fire, ambulance) | — | — | MU-20, MU-21 |
| R-08 | Fleet technician | MU-23 | MU-22 | — |

<!-- END GENERATED: misuse-roles -->

The fleet technician is added to the roles of the skeleton: the person who cleans, calibrates and returns vehicles to service is where several sensor and configuration hazards begin (MU-22, MU-23).

## 3. External communication of intent

A driver tells others what they will do with eye contact, a wave and the way the car moves. A driverless vehicle has only its motion and its lamps. The item already signals with turn indicators and hazard lights (F-12, FSR-09.01), and drives so that its motion reads like a typical driver's (FM-17, DQ-026 C). What is missing is a way to say "I am yielding to you" and "I am about to move" to a pedestrian waiting at a crossing (MU-11); HR-06 asks for it, by lamps or an external display, to be specified with the vehicle. No standard form of such a display is assumed here.

## 4. Remote assistance and remote operation

The remote operator is the only person who can act on the vehicle in service, so their errors carry over directly. The concept already bounds them: every remote command passes the safety monitor's envelope (FSR-08.02), remote messages are signed and bound to one vehicle (CSR-01), the centre is staffed for response times (SR-01) and operators are trained and drive one vehicle at a time (AOU-10). The entries below are the errors that remain.

<!-- BEGIN GENERATED: misuse-remote (assurance/02-concept/misuse/misuse.py) -->

| ID | Role | Kind | Situation | Consequence | Related | Measures in the concept | New |
|---|---|---|---|---|---|---|---|
| MU-16 | Remote operator | Error | Acts on the wrong vehicle | A vehicle released or moved that should not be | UCA-14, HZ-5 | CSR-01 | HR-07 |
| MU-17 | Remote operator | Error | Trusts the video too much and confirms a path that is blocked | Collision during remote assistance | UCA-07, HZ-1 | FSR-08.02, FM-11 | — |
| MU-18 | Remote operator | Error | Tired or handling several vehicles, and responds late | Vehicles stopped in lane for long | UCA-06, HZ-8 | SR-01, AOU-10 | — |
| MU-19 | Remote operator | Error | Releases a vehicle while a passenger is getting out | Passenger struck by the moving vehicle | UCA-14, HZ-7 | FSR-05.01, FSR-07.04 | — |

<!-- END GENERATED: misuse-remote -->

## 5. Reasonably foreseeable misuse

![WP-C-08 Figure 5-1: for each of the eight human roles, a row of labels naming its entries, shaded by kind (misuse amber, error red outline, interaction blue outline), with a dot on those that need a new requirement. The same data are in the tables of §2, §4 and §5.](misuse/fig-c08-5-1-entries.svg)

*Figure 5-1. Interactions, errors and misuse by role. Generated by `misuse/misuse.py` from `misuse/misuse.yaml`.*

<!-- BEGIN GENERATED: misuse-people (assurance/02-concept/misuse/misuse.py) -->

| ID | Role | Kind | Situation | Consequence | Related | Measures in the concept | New |
|---|---|---|---|---|---|---|---|
| MU-01 | Passenger | Misuse | Tries to open a door while the vehicle is moving | Falls out, or strikes a passing cyclist | UCA-47, HZ-7 | AOU-06, FSR-05.05 | — |
| MU-02 | Passenger | Misuse | Gets out on the traffic side at a stop in lane | Struck by a passing vehicle | SH-16, HZ-7 | FM-20 | — |
| MU-03 | Passenger | Misuse | Presses the stop request as a prank, or again and again | Needless stops; the vehicle blocks traffic | UCA-49, HZ-8 | TR-16 | HR-01 |
| MU-04 | Passenger | Misuse | Covers or damages a sensor or camera in the cabin or on the body | Perception degraded; the monitor's channel blinded | TC-24, FI-08 | FM-10, FSR-07.08 | — |
| MU-05 | Passenger | Misuse | Tries to take control of the vehicle | None if no control is reachable from the cabin | HZ-5 | AOU-07 | — |
| MU-06 | Passenger | Interaction | Has a medical emergency, or is threatened by another passenger | Harm made worse by delay | HZ-7 | — | HR-02 |
| MU-07 | Passenger | Misuse | Unbuckles or never buckles the seat belt during a trip | Injured in a hard stop or a collision | HZ-3 | — | HR-03 (proposed, DQ-029) |
| MU-08 | Child, elderly or less mobile passenger | Interaction | Needs more time or help to get in and out, or cannot reach the controls | Trapped by a door, or left in an unsafe place | HZ-7 | FSR-05.01, FSR-05.05 | HR-04 |
| MU-09 | Child, elderly or less mobile passenger | Misuse | A child rides alone, or is left in the vehicle at the end of a trip | An unsupervised child in a driverless vehicle | HZ-7 | — | HR-05 |
| MU-10 | Pedestrian | Misuse | Steps in front of the vehicle to test it, knowing it will stop | Hard braking; the vehicle blocks traffic | HZ-3, HZ-8 | FSR-02.02, FM-17, TR-14 | — |
| MU-11 | Pedestrian | Interaction | Waits for eye contact or a wave before crossing, which no driver can give | Hesitation on both sides, or a crossing at the wrong moment | SH-11, HZ-6 | FM-17 | HR-06 |
| MU-12 | Pedestrian | Misuse | Places cones or objects to trap the vehicle | The vehicle is stranded and blocks the lane | HZ-8 | TR-14, SR-01 | — |
| MU-13 | Cyclist or scooter rider | Interaction | Rides up alongside on the inside of a right turn | Struck by the turning vehicle | SH-04, HZ-1 | FSR-06.01, FM-06 | — |
| MU-14 | Driver of another vehicle | Misuse | Cuts in front or tailgates, because the vehicle is known to give way | Hard braking and rear-end collisions | SH-11, HZ-3 | FM-17, FSR-03.02 | — |
| MU-15 | Driver of another vehicle | Interaction | Takes a vehicle stopped in lane with hazard lights for a parked one and overtakes into the opposing lane | Head-on collision between other road users | HZ-8 | FSR-07.02, SR-01 | — |
| MU-20 | First responder (police, fire, ambulance) | Interaction | Needs to stop, hold, move or direct a driverless vehicle at a scene | Delay at the scene, or the vehicle moves when it should not | HZ-8, SH-10 | FM-16 | HR-08 |
| MU-21 | First responder (police, fire, ambulance) | Interaction | Needs to open doors and make the vehicle safe after a crash or in a fire | Rescue delayed | HZ-7 | SR-05 | HR-09 |
| MU-22 | Fleet technician | Error | Returns a vehicle to service with a sensor misaligned, uncalibrated or dirty | Degraded perception in service | TC-24 | AOU-08 | HR-10 |
| MU-23 | Fleet technician | Misuse | Uses a debug or service port to change parameters outside the release process | Safety limits changed without review | TS-05 | CR-03, CSR-05 | — |

<!-- END GENERATED: misuse-people -->

**Two patterns stand out.** People will test a vehicle that always yields (MU-10, MU-12, MU-14): stepping in front of it, trapping it with cones, cutting in. Each is safe, because the vehicle stops, but each strands it and blocks traffic, so they feed STPA HZ-8 and the staffing of SR-01. And passengers with nobody to supervise them create most of the new requirements: a medical emergency, an unbelted rider, a child alone (MU-06, MU-07, MU-09).

## 6. Resulting requirements

New requirements the entries need. They are proposals, each carried into the work product named in "Allocated to"; HR-04 and HR-09 become assumptions on the vehicle in WP-C-01 §8.

<!-- BEGIN GENERATED: misuse-requirements (assurance/02-concept/misuse/misuse.py) -->

| ID | Requirement | Allocated to | From |
|---|---|---|---|
| HR-01 | Act on the stop request by pulling over (MRM-1), connect the passenger to a remote operator, and after repeated requests let the operator decide | Autoware (TR-16); remote operations (WP-O-02) | MU-03 |
| HR-02 | Give every seat an emergency call to a remote operator, who can divert the vehicle to a safe stop or a meeting point with emergency services | Vehicle interface; remote operations (WP-O-02, WP-O-03) | MU-06 |
| HR-03 | Detect unfastened seat belts and respond as the decision on unbuckled passengers sets | Vehicle; Autoware; passenger information (WP-O-03) | MU-07 |
| HR-04 | Give passengers who need it more time and help to board and alight, with doors that never close on a person and controls reachable from a wheelchair | Vehicle (an assumption to add to WP-C-01 §8); WP-O-03 | MU-08 |
| HR-05 | Check the cabin before a trip ends and before the next begins, and do not end a trip with a person still inside without a remote operator's decision | Vehicle interface; remote operations (WP-O-02) | MU-09 |
| HR-06 | Show other road users, by lamps or an external display, when the vehicle is yielding and when it is about to move | Vehicle; Autoware (F-12) | MU-11 |
| HR-07 | Show the vehicle's identity, position and cabin view on every remote action, and ask the operator to confirm the vehicle before a release or a move | Remote operations station (EL-09) | MU-16 |
| HR-08 | Publish a first responder guide, mark the vehicles as driverless, and give emergency services a line to remote operations that can stop, hold or move any vehicle | Operations (WP-O-02); vehicle markings | MU-20 |
| HR-09 | Make the high-voltage and power isolation points and the manual door release findable and usable by first responders without tools specific to the fleet | Vehicle (assumption, WP-C-01 §8); first responder guide | MU-21 |
| HR-10 | Check calibration, cleanliness and software versions before every return to service, and let the vehicle refuse driverless dispatch until the check is recorded | Operations (WP-O-02); Autoware start-up checks | MU-22 |

<!-- END GENERATED: misuse-requirements -->

## 7. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Decide the response to unbelted passengers (DQ-029) | G1 |
| OI-2 | Specify the in-vehicle stop request and the emergency call (TR-16, HR-01, HR-02) with the vehicle | G2 |
| OI-3 | Add HR-04 and HR-09 as assumptions on the vehicle in WP-C-01 §8 | G1 |
| OI-4 | Set the fleet's rules for unaccompanied minors and for passengers who need assistance, in WP-O-03 | G2 |
| OI-5 | Specify the external display of intent (HR-06) once the vehicle is chosen (DQ-008) | G2 |
| OI-6 | Review by a human factors specialist, and test the passenger and first responder interfaces with users | G2 |
