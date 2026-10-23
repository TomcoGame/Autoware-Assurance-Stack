# WP-C-01 Item definition

| Field | Value |
|---|---|
| Work product | WP-C-01 Item definition |
| Standard reference | UL 4600 §5; ISO 26262-3 §5; ISO 21448 §5; ISO/SAE 21434 §9.3; ASPICE 4.0 SYS.1 |
| Version | 0.4 (state deferred to DQ-014; 2026-10-23). 0.3 (first market one US state (DQ-009 A); remote driving allowed (DQ-010 C): §4, I-08, §7, new AOU-10, hazard added; 2026-10-23). 0.2 (first content: item, functions, modes, boundary and interfaces, vehicle placeholders, legal context, assumptions, preliminary hazards, from DQ-001 B, DQ-002 A, DQ-003 C; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All (ASILs follow from WP-C-03) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1); HARA confirmation review covers this definition (I3) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | `3794b76`; Autoware sources as pinned in `repositories/autoware.repos` (`autoware_core` 1.9.0, `autoware_universe` 0.52.1, `autoware_adapi_msgs` 1.9.2) |

## 1. Purpose

This document says what the item is: the functions it performs, its operating modes, where its boundary lies, what crosses that boundary, and what it assumes about the vehicle, the infrastructure and the people around it. The hazard analysis ([WP-C-03](WP-C-03-hara.md)), the SOTIF hazard identification ([WP-C-05](WP-C-05-sotif-hazard-identification.md)), the STPA ([WP-A-05](../08-analyses/WP-A-05-stpa.md)) and the TARA ([WP-C-09](WP-C-09-tara.md)) all analyse the item as defined here. The ODD it operates in is specified in [WP-C-02](WP-C-02-odd-and-intended-functionality.md).

## 2. Basis and status

| Input | What it fixes | Source |
|---|---|---|
| Item and ODD | Geofenced urban robotaxi, public urban roads up to 50 km/h, day and night, dry weather and light rain | DQ-001 B, [WP-M-01 §3.1](../01-management/WP-M-01-assurance-strategy.md#31-reference-configuration) |
| Command bound | An independent safety monitor on its own hardware, between Autoware and the drive-by-wire system | DQ-002 A, [WP-M-01 §6](../01-management/WP-M-01-assurance-strategy.md#6-safety-architecture-argument) |
| Vehicle | Not chosen until G2. Until then a generic vehicle model; every value that depends on the vehicle is marked **provisional** | DQ-003 C, DQ-008 |
| Software | Autoware as pinned at the baseline above; package names below are those of the pinned versions | `repositories/autoware.repos` |

This is a draft by an AI assistant (I0). Statements about Autoware describe what the pinned source contains; none of it is assured yet. Statements about the vehicle, the safety monitor and the remote operations centre describe what the item needs; none of those exists yet.

## 3. The item and its functions

The item is an automated driving system for driverless passenger transport inside a mapped urban geofence. It performs the entire dynamic driving task and its fallback without a driver (SAE Level 4). It consists of the sensors, the Autoware software on its computer, and the independent safety monitor, with the connections between them (§5). The vehicle it drives is outside the item.

| ID | Function | Realised by (pinned packages) | State |
|---|---|---|---|
| F-01 | Localise the vehicle on the HD map | `autoware_ndt_scan_matcher`, `autoware_ekf_localizer`, `autoware_pose_initializer` (core) | Upstream, unassured |
| F-02 | Detect and track objects: vehicles, pedestrians, cyclists, obstacles | `autoware_lidar_centerpoint`, `autoware_ground_segmentation`, `autoware_radar_object_tracker`, `autoware_object_merger`, `autoware_multi_object_tracker` (universe) | Upstream, unassured; ML components (WP-C-11) |
| F-03 | Recognise traffic lights | `autoware_traffic_light_map_based_detector`, `autoware_traffic_light_fine_detector`, `autoware_traffic_light_classifier`, `autoware_traffic_light_arbiter` (universe) | Upstream, unassured; ML components |
| F-04 | Predict the motion of other road users | `autoware_map_based_prediction` (universe) | Upstream, unassured |
| F-05 | Plan the route to the passenger's destination inside the geofence | `autoware_mission_planner` (core), `autoware_mission_planner_universe` | Upstream, unassured |
| F-06 | Plan behaviour and motion: lanes, intersections, crosswalks, traffic lights, stops, speed | `autoware_behavior_path_planner`, `autoware_behavior_velocity_planner` and its modules, `autoware_motion_velocity_planner`, `autoware_path_optimizer`, `autoware_velocity_smoother` | Upstream, unassured |
| F-07 | Follow the planned trajectory | `autoware_trajectory_follower_node` with `autoware_mpc_lateral_controller` and `autoware_pid_longitudinal_controller` (universe) | Upstream, unassured |
| F-08 | Select and limit the command sent on: autonomous, external or emergency | `autoware_vehicle_cmd_gate`, `autoware_external_cmd_selector` (universe) | Upstream, unassured |
| F-09 | Monitor the system and carry out a minimal risk manoeuvre (MRM) | `autoware_diagnostic_graph_aggregator`, `autoware_mrm_handler`, `autoware_mrm_comfortable_stop_operator`, `autoware_mrm_emergency_stop_operator` (universe) | Upstream, unassured |
| F-10 | Bound every command to a safety envelope, and stop the vehicle independently of Autoware | Safety monitor (to be developed; [WP-C-12](WP-C-12-fallback-and-minimal-risk-concept.md), [WP-S-03](../03-system/WP-S-03-technical-safety-concept-architecture.md)) | **Does not exist** |
| F-11 | Accept trips, mode changes and requests from the remote operations centre and passengers | Autoware AD API (`autoware_default_adapi`, core; `autoware_default_adapi_universe`) | Upstream, unassured; the HMI and the centre are outside the item |
| F-12 | Signal intent to other road users: turn indicators, hazard lights | Planning and MRM outputs through `autoware_vehicle_cmd_gate` | Upstream, unassured; the lamps are the vehicle's |

The item does not include door control, passenger boarding and alighting, or cabin functions; they belong to the vehicle and its operator, and their interaction with the item (for example, never moving while a door is open) is an assumption in §8.

## 4. Operating modes

The modes are those of the Autoware AD API (`OperationModeState` in `autoware_adapi_msgs` 1.9.2) and of its fail-safe state (`MrmState`), plus the safety monitor's own stop.

| Mode or state | Meaning | In driverless operation |
|---|---|---|
| `STOP` | Autoware holds the vehicle at standstill | Used; the state between trips |
| `AUTONOMOUS` | Autoware drives | Used; the normal driving mode |
| `LOCAL` | A person in the vehicle drives through a local controller | Development only, with a safety driver ([WP-V-07](../06-validation/WP-V-07-test-operations.md)); not available in driverless operation (AOU-07) |
| `REMOTE` | A remote operator drives the vehicle: steering, acceleration and braking commands from the remote operations centre | Used (DQ-010 C). Remote commands reach the vehicle through `vehicle_cmd_gate` and the safety monitor like any other command, so the monitor's envelope bounds them; loss or delay of the link while driving is detected (MON-04) and ends in a minimal risk manoeuvre |
| MRM `NORMAL` | No minimal risk manoeuvre active | |
| MRM `MRM_OPERATING` | A minimal risk manoeuvre is running: comfortable stop or emergency stop | Used |
| MRM `MRM_SUCCEEDED` | The vehicle reached a minimal risk condition (stopped) | Used; needs remote recovery |
| MRM `MRM_FAILED` | The manoeuvre did not complete | Must be covered by the safety monitor's independent stop (F-10) |
| Monitor stop | The safety monitor stops the vehicle without Autoware: Autoware silent, command outside the envelope, or monitor fault | Used; to be specified in WP-C-12 |

`MrmState` also defines a `PULL_OVER` behaviour, and `autoware_mrm_handler` can select it, but no pull-over operator package is present in `autoware_universe` 0.52.1. Until one is added and assured, the only Autoware MRMs are comfortable stop and emergency stop, both of which stop in lane. Whether stopping in lane on an urban road is an acceptable minimal risk condition is a question for the hazard analysis (OI-3).

## 5. Item boundary and interfaces

![The item boundary: inside it the sensors, the Autoware computer and the safety monitor; outside it, on the left, the HD map data, the update backend, the remote operations centre and the passengers; on the right, the vehicle platform with its drive-by-wire system, the power supply and the other road users. Arrows numbered I-01 to I-12 show what crosses the boundary, as listed in the table of §5.2.](figures/fig-c01-5-1-boundary.svg)

*Figure 5-1. The elements of §5.1 and the interfaces of §5.2. Drawn from both tables by [`figures/fig_c01_boundary.py`](figures/fig_c01_boundary.py); CI fails if it is stale.*

### 5.1 Elements

| Element | In the item | What it is |
|---|---|---|
| Sensors | Yes | LiDAR, cameras, radar, GNSS and IMU, with their mounts and calibration; selection open until the vehicle is chosen (WP-H-02) |
| Autoware computer | Yes | The main computer running Linux, ROS 2 and the Autoware functions F-01 to F-09, F-11 and F-12 |
| Safety monitor | Yes | An independent controller on its own hardware between Autoware and the drive-by-wire system (F-10) |
| Vehicle platform | No | The vehicle with its drive-by-wire steering, braking, propulsion and gear, its lamps, doors and park brake; provisional until G2 |
| Power supply | No | The vehicle's low-voltage supply to the item |
| HD map data | No | Lanelet2 vector map and point cloud map of the geofence ([WP-W-12](../05-software/WP-W-12-hd-map-data.md)) |
| Update backend | No | The service that delivers software, map, model and parameter updates |
| Remote operations centre | No | Staff and systems that dispatch trips, watch the fleet and assist vehicles |
| Passengers | No | People riding in the vehicle, through its passenger interface |
| Other road users | No | Pedestrians, cyclists, drivers and their vehicles inside the ODD |

### 5.2 Interfaces

| ID | From | To | What crosses | Notes |
|---|---|---|---|---|
| I-01 | Other road users | Sensors | Their presence, position and motion, as sensed | The world as perceived; insufficiencies here are SOTIF (WP-C-06) |
| I-02 | Sensors | Autoware computer | Point clouds, images, radar objects, GNSS fixes, IMU data, with time stamps | Time synchronisation is part of the interface (WP-S-05) |
| I-03 | Autoware computer | Safety monitor | Control command (steering, acceleration), gear, lamps; heartbeat | The only path from Autoware to the vehicle |
| I-04 | Safety monitor | Vehicle platform | Bounded command, or the monitor's own stop command | The only command path into the drive-by-wire system |
| I-05 | Vehicle platform | Safety monitor | Speed, steering angle, gear, control mode, by-wire faults | Must not depend on the Autoware computer (AOU-03) |
| I-06 | Vehicle platform | Autoware computer | Speed, steering, gear, control mode, turn signal state | Used by localisation and control |
| I-07 | HD map data | Autoware computer | Lanelet2 vector map and point cloud map | Safety-related data (WP-W-12); loaded at start and on update |
| I-08 | Remote operations centre | Autoware computer | Trips, routes, mode changes, MRM requests, assistance commands and remote driving commands; fleet telemetry and camera video back | Through the AD API and the external command path over a wireless link. With remote driving (DQ-010 C) the link is in the control loop: its delay, loss and integrity are safety-relevant (WP-C-03, WP-S-04) as well as cybersecurity-relevant (WP-C-09) |
| I-09 | Passengers | Autoware computer | Trip start, stop request; trip status back | Through the vehicle's passenger interface and the AD API |
| I-10 | Update backend | Autoware computer | Software, map, model and parameter updates | Change-controlled (WP-P-02); cybersecurity-relevant |
| I-11 | Vehicle platform | Other road users | Motion, turn indicators, hazard lights, horn | What others see of the item's decisions |
| I-12 | Power supply | Safety monitor | Low-voltage power; the monitor's supply must stay up when the Autoware computer's fails (AOU-05) | The other elements are supplied too; this path is drawn because the fallback depends on it |

## 6. Vehicle and platform (provisional)

The vehicle is chosen at G2 (DQ-008). Until then the concept phase uses a generic passenger vehicle, Autoware's planning simulator and AWSIM. The table lists what the item needs to know about the vehicle; every value is a placeholder to be replaced from the chosen platform's data, and any result that used it is re-checked then.

| Property | Needed for | Provisional value |
|---|---|---|
| Mass, dimensions, wheelbase | Severity of collisions, stopping distance, path planning | Generic mid-size passenger car (TBD) |
| Maximum deceleration by wire, and its response time | Emergency stop, FTTI (WP-S-04) | TBD |
| Steering range, rate and response time by wire | Trajectory following, envelope limits | TBD |
| Redundancy of braking and steering actuation | Whether a single actuator fault defeats the MRM | Unknown; required by AOU-01 |
| Park brake commandable by wire | Holding a minimal risk condition | Required by AOU-02 |
| Independent vehicle state signals | The monitor's own view of speed and steering (I-05) | Required by AOU-03 |
| Supplier safety evidence and interface agreement | ISO 26262-8 §5 development interface agreement (WP-M-11) | None yet |

## 7. Legal and regulatory context

The robotaxi first operates in one US state (DQ-009 A, 2026-10-23); the state is deferred (DQ-013): the lead leans to the state where testing is easiest, and it is asked again before the HARA confirmation review (DQ-014). The instruments below apply in any state; the state's own law adds its permits, its vehicle code (the traffic rules of WP-C-02) and any rules on remote driving.

| Level | Instrument (informative; to be confirmed for the chosen state) | Bears on |
|---|---|---|
| Federal | Federal Motor Vehicle Safety Standards (FMVSS); a vehicle built without manual controls needs an exemption | Vehicle choice (DQ-008) |
| Federal | NHTSA Standing General Order 2021-01: crash reporting for vehicles equipped with automated driving systems | Field monitoring (WP-O-04) |
| State | Permits for driverless testing and for deployment or passenger service, with their conditions on the ODD, reporting and remote operation | ODD (WP-C-02), test operations (WP-V-07), remote operations (WP-O-02) |
| State | The vehicle code: right of way, signals, speed limits, school zones, yielding to emergency vehicles | Intended functionality (WP-C-02 §5), HARA |

The traffic rules of the chosen state are part of the intended functionality and the hazard analysis rates violations of them. Speeds in the US are posted in miles per hour; the ODD uses 30 mph as the posted-limit ceiling (WP-C-02 ODD-03).

## 8. Assumptions

Assumptions are what the item relies on from outside its boundary. Each is checked when the element it concerns is chosen or built, and each becomes a requirement on that element.

| ID | Assumption | On | Checked by |
|---|---|---|---|
| AOU-01 | The vehicle's drive-by-wire braking accepts commands from the safety monitor and can stop the vehicle after any single fault in the braking path | Vehicle | WP-H-07, DIA (WP-M-11) at G2 |
| AOU-02 | The vehicle has a park brake, commandable by wire from the safety monitor, that holds the vehicle at standstill on the gradients of the geofence | Vehicle | WP-H-07 at G2 |
| AOU-03 | The vehicle provides speed and steering angle to the safety monitor through a path that does not pass through the Autoware computer | Vehicle | WP-S-05 at G2 |
| AOU-04 | The HD map matches the geofence within the accuracy and currency WP-W-12 sets, and the item detects when it does not | Map data | WP-W-12 |
| AOU-05 | The safety monitor's power stays up when the Autoware computer's supply fails | Power supply | WP-H-02 |
| AOU-06 | The vehicle does not move while a door is open, and tells the item when doors are open | Vehicle | WP-S-05 at G2 |
| AOU-07 | In driverless operation there is no driver: `LOCAL` mode is not available, and passengers cannot take control | Vehicle, operation | WP-O-02 |
| AOU-08 | Sensors are cleaned, calibrated and inspected at the intervals WP-O-02 sets | Operation | WP-O-02 |
| AOU-09 | The remote operations centre is staffed whenever a vehicle is in service, and its link loss is detected by the item | Operation | WP-O-02, WP-C-12 |
| AOU-10 | A remote operator who drives a vehicle is trained and qualified for it, drives one vehicle at a time, and has video and vehicle state with a delay inside the bound WP-S-04 sets | Operation | WP-O-02, WP-S-04 |

## 9. Preliminary hazards

ISO 26262-3 §5 asks the item definition to name the hazards already known. This list is the starting point for the hazard analysis; nothing here is rated. The HARA (WP-C-03), the SOTIF analysis (WP-C-05) and the STPA (WP-A-05) replace it.

| Hazard (vehicle-level behaviour) | Kinds of cause |
|---|---|
| Moves or accelerates when it should not, including from standstill | Malfunction (F-07, F-08), insufficiency (F-02, F-06), door interlock (AOU-06) |
| Decelerates too little to avoid a collision | Missed or late detection (F-02), wrong prediction (F-04), malfunction (F-07), actuator fault (AOU-01) |
| Decelerates hard when it should not (unexpected braking) | False detection (F-02), malfunction |
| Steers out of its lane or path | Localisation error (F-01), map error (AOU-04), malfunction (F-07) |
| Enters an intersection or crosswalk against the right of way | Traffic light recognition (F-03), planning (F-06) |
| Stops somewhere unsafe and stays there | MRM in lane (§4, OI-3), loss of the remote link (AOU-09) |
| Operates outside its ODD without noticing | ODD monitoring (WP-C-02), weather and lighting detection |
| Responds to a forged or corrupted command or update | Remote link and updates (I-08, I-10; WP-C-09) |
| Is driven unsafely by a remote operator, or keeps moving on stale remote commands when the link is delayed or lost | Remote driving (DQ-010 C, I-08, AOU-10), link monitoring (MON-04) |

## 10. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Replace the provisional vehicle values of §6 from the chosen platform, and re-check AOU-01 to AOU-03 and AOU-06 (DQ-008) | G2 |
| OI-2 | Choose the state (DQ-014) and fill §7 for it | G1 |
| OI-3 | Decide in the HARA whether a stop in lane is an acceptable minimal risk condition in the urban ODD, or whether a pull-over operator must be added and assured | G1 |
| OI-4 | Bound the remote driving loop: maximum link delay, the speed allowed under remote driving, and the response to link loss (WP-S-04, WP-C-12) | G2 |
| OI-5 | Specify the passenger interface (I-09) with the vehicle | G2 |
