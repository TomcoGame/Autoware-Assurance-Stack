# WP-C-02 ODD and intended functionality (DDT, OEDR, manoeuvres)

| Field | Value |
|---|---|
| Work product | WP-C-02 ODD and intended functionality (DDT, OEDR, manoeuvres) |
| Standard reference | UL 4600 §8; ISO 26262-3 §5; ISO 21448 §5; ISO/PAS 8800:2024 (Input space definition); ASPICE 4.0 SYS.1; ISO 34503:2023 and SAE J3016 (informative, taxonomy and terms) |
| Version | 0.5 (pull-over manoeuvre added, stop in lane as the rated fallback (DQ-016 A); 2026-10-23). 0.4 (unprotected turns and roundabouts inside the ODD (DQ-011 C); rain and visibility limits decided (DQ-012 A); state still open, so traffic rules are rated against common US rules until it is chosen (DQ-013); 2026-10-23). 0.3 (one US state, so US vehicle code and mph (DQ-009 A); remote driving allowed, so MON-04 bounds the remote loop (DQ-010 C); 2026-10-23). 0.2 (first content: ODD attributes with proposed limits, ODD monitoring, intended functionality, AI input space; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | `3a8514a`; Autoware sources as pinned in `repositories/autoware.repos` (`autoware_core` 1.9.0, `autoware_universe` 0.52.1) |

## 1. Purpose

This document specifies where and when the item may drive (its operational design domain, ODD), what it must do there (its intended functionality), and how it knows when it has left. The item is defined in [WP-C-01](WP-C-01-item-definition.md). The hazard analysis ([WP-C-03](WP-C-03-hara.md)) draws its operational situations from §3, the SOTIF analysis ([WP-C-05](WP-C-05-sotif-hazard-identification.md), [WP-C-06](WP-C-06-sotif-insufficiencies-triggering-conditions.md)) its triggering conditions from §3 and §5, and the validation targets ([WP-V-02](../06-validation/WP-V-02-sotif-vv-strategy.md)) their coverage from §3.

With no driver, the ODD carries more weight than it would for a supervised system: anything the item cannot handle must be outside the ODD, or the item must detect it and reach a minimal risk condition by itself.

## 2. Basis and status

| Input | What it fixes | Source |
|---|---|---|
| Item and ODD envelope | Geofenced urban robotaxi; public urban roads up to 50 km/h; day and night; dry weather and light rain | DQ-001 B ([WP-M-01 §3.1](../01-management/WP-M-01-assurance-strategy.md#31-reference-configuration)) |
| Traffic rules | The vehicle code of one US state. The state is not chosen yet (the lead leans to the state where testing is easiest); until it is, the analyses use rules common to US states (§5.1) and check the chosen state's differences then | DQ-009 A, DQ-013 (deferred) |
| Remote operation | Remote operators may drive the vehicle as well as assist it | DQ-010 C |
| Intersection manoeuvres | Unprotected turns across oncoming traffic and roundabouts are inside the ODD | DQ-011 C |
| Weather and visibility limits | Rain up to 2.5 mm/h; visibility of 200 m or more | DQ-012 A |

Limits are the safety authority's to set. Each limit below that is not yet decided is marked **Proposed**: it is Claude's draft value, used so the analyses can start, and it is replaced by the decision when it is made. Values that depend on the vehicle are marked **Provisional** (DQ-008).

## 3. ODD attributes

Attributes follow the three top-level groups of ISO 34503: scenery (static), environmental conditions, and dynamic elements. For each attribute: what is inside the ODD, what is outside, and how the item knows which it is in (§4).

### 3.1 Scenery

| ID | Attribute | Inside the ODD | Outside the ODD | Detected by | State |
|---|---|---|---|---|---|
| ODD-01 | Area | Public roads inside a mapped geofence; every road in it has a verified HD map (WP-W-12) | Anywhere outside the geofence or without a verified map | MON-01 | Decided (DQ-001) |
| ODD-02 | Road type | Urban streets and collector roads, one or two lanes per direction, with or without a centre line | Motorways, expressways, ramps; unpaved roads; private car parks; drive-throughs | MON-01 (map) | Proposed |
| ODD-03 | Posted speed limit | Roads posted at or below 30 mph (48 km/h) | Roads posted higher, including the 35 mph arterials common in US cities | MON-01 (map) | Proposed; DQ-001 set 50 km/h, and the nearest US posted limit at or below it is 30 mph |
| ODD-04 | Junctions | Signalised intersections with protected and unprotected turns; stop-controlled and yield-controlled junctions; T-junctions; single-lane and multi-lane roundabouts | Level crossings with railways or trams | MON-01 (map, route planning) | Decided (DQ-011 C), except level crossings: Proposed |
| ODD-05 | Crossings | Marked pedestrian crossings, with or without signals; cycle lanes alongside the road | Unmarked mid-block crossings are not excluded (people cross anyway) and are handled by OEDR (§5.2) | n/a | Proposed |
| ODD-06 | Road surface and geometry | Paved, gradients up to 8 %, curves the vehicle can take at the posted speed | Gradients above 8 %; surfaces the map flags as damaged | MON-01 (map) | Proposed; gradient depends on the vehicle (Provisional) |
| ODD-07 | Lane markings | Present and visible, or absent where the map encodes the lane | Roads under re-marking where the map and the markings disagree | MON-02 | Proposed |
| ODD-08 | Temporary changes | None, or changes that the map update process has captured | Construction zones, closures and diversions not yet in the map | MON-02, remote operations | Proposed |
| ODD-09 | Stopping places | Kerbside stops marked in the map for pick-up and drop-off | Stopping anywhere else except as an MRM | Route planning | Proposed |

### 3.2 Environmental conditions

| ID | Attribute | Inside the ODD | Outside the ODD | Detected by | State |
|---|---|---|---|---|---|
| ODD-10 | Precipitation | Dry; light rain up to 2.5 mm/h | Rain above 2.5 mm/h; snow, sleet, hail | MON-03 | Decided (DQ-012 A) |
| ODD-11 | Visibility | Meteorological visibility of 200 m or more | Fog, mist, smoke, dust or spray below 200 m | MON-03 | Decided (DQ-012 A) |
| ODD-12 | Illumination | Day, dusk and night, including unlit streets | None excluded by time of day; low sun and glare are triggering conditions (WP-C-06) | n/a | Decided (DQ-001) |
| ODD-13 | Road surface condition | Dry or wet | Standing water deeper than the vehicle allows; ice; snow cover | MON-03, temperature | Proposed |
| ODD-14 | Temperature | The operating range of the sensors and computer | Outside it | Hardware diagnostics | Provisional (WP-H-02) |
| ODD-15 | Connectivity | Remote operations link available, with a delay inside the bound WP-S-04 sets while a remote operator drives (DQ-010 C); GNSS available or not (localisation uses the point cloud map) | Loss of the remote link: the item stays inside the ODD only long enough to reach a minimal risk condition (AOU-09) | MON-04 | Proposed |

### 3.3 Dynamic elements

| ID | Attribute | Inside the ODD | Outside the ODD | Detected by | State |
|---|---|---|---|---|---|
| ODD-16 | Traffic participants | Cars, vans, buses, trucks, motorcycles, bicycles, e-scooters, pedestrians including children and people using wheelchairs, animals at the roadside | None excluded: urban roads cannot exclude any of them. Recognition limits are SOTIF triggering conditions (WP-C-06) | n/a | Proposed |
| ODD-17 | Traffic density | Free flow to congested | None excluded | n/a | Proposed |
| ODD-18 | Special vehicles | Emergency vehicles with sirens and lights, which the item must yield to; buses at stops | None excluded | OEDR (§5.2) | Proposed |
| ODD-19 | Traffic direction by people | None | A police officer or flagger directing traffic: the item stops safely and asks for remote assistance | MON-02, OEDR | Proposed |
| ODD-20 | Ego speed | 0 to 50 km/h, never above the posted limit | Above 50 km/h | Safety monitor envelope (F-10) | Decided (DQ-001) |

## 4. ODD monitoring

The item must know when it is about to leave its ODD or has left it, and then reach a minimal risk condition ([WP-C-12](WP-C-12-fallback-and-minimal-risk-concept.md)). The pinned Autoware has no function that monitors the ODD as such. It has related pieces: localisation quality in the diagnostics, `autoware_image_diagnostics` for camera image quality, and `autoware_raindrop_cluster_filter` for LiDAR returns from rain. Building the monitors below is new work.

| ID | Monitor | Covers | What Autoware has today | State |
|---|---|---|---|---|
| MON-01 | Map and route check: the planned route stays inside the geofence, on roads whose map attributes are inside ODD-02 to ODD-06 and ODD-09 | ODD-01 to ODD-06, ODD-09 | Route planning on the Lanelet2 map; no check of map attributes against the ODD | To be built |
| MON-02 | Map–world divergence: what the sensors see disagrees with the map (markings, lanes, closures, a person directing traffic) | ODD-07, ODD-08, ODD-19 | Localisation score in diagnostics; nothing that compares the scene with the map's lanes | To be built |
| MON-03 | Weather and visibility: rain rate, visibility and surface condition, from sensor degradation and an external weather feed | ODD-10, ODD-11, ODD-13 | Camera image diagnostics; LiDAR raindrop filtering; no rain-rate or visibility estimate | To be built |
| MON-04 | Remote link: loss or delay of the link to the remote operations centre. While a remote operator drives, it stops the vehicle on commands older than the bound, independently of the operator | ODD-15 | `autoware_vehicle_cmd_gate` times out the system emergency and external emergency-stop heartbeats; a reading of its source (0.52.1) found no check on the age of the external control commands themselves, to be confirmed in WP-W-03. AD API connectivity is not monitored as an ODD condition | To be built |

Each monitor's response when its condition leaves the ODD is a minimal risk manoeuvre, specified in WP-C-12. A monitor that cannot tell inside from outside (for example, rain rate near 2.5 mm/h) counts as outside.

## 5. Intended functionality

### 5.1 Dynamic driving task

Inside the ODD the item performs the whole dynamic driving task: steering, acceleration and braking, object and event detection and response, manoeuvre planning, and signalling (SAE J3016). It also performs the fallback: when it can no longer drive safely it reaches a minimal risk condition by itself (WP-C-12). It drives to the vehicle code of the chosen US state (DQ-009 A), and in doubt it yields. Until the state is chosen (DQ-014), the analyses use the rules common to US states: the MUTCD for signs, signals and markings, and the right-of-way rules of the Uniform Vehicle Code, the model code many state codes follow. Where states differ (for example turns on red, or rules at roundabouts), the hazard analysis rates the stricter case and marks it for checking. In `REMOTE` mode a remote operator drives instead (DQ-010 C); the safety monitor's envelope and MON-04 still apply.

### 5.2 Object and event detection and response

| ID | Object or event | Required response | Realised by (pinned) |
|---|---|---|---|
| OEDR-01 | Vehicle ahead in the lane, moving or stopped | Follow at a safe gap, or stop behind it | `autoware_motion_velocity_obstacle_cruise_module`, `obstacle_stop_module` |
| OEDR-02 | Parked or stopped vehicle partly in the lane | Pass it within the lane or by changing lane when the way is clear; otherwise wait | `autoware_behavior_path_static_obstacle_avoidance_module`, `lane_change_module` |
| OEDR-03 | Pedestrian or cyclist at or on a crosswalk | Yield as the traffic rules require | `autoware_behavior_velocity_crosswalk_module` |
| OEDR-04 | Pedestrian, cyclist or animal entering the road elsewhere | Slow down or stop to avoid a collision | `autoware_motion_velocity_run_out_module`, `dynamic_obstacle_stop_module` |
| OEDR-05 | Traffic light | Obey; treat an unknown or unrecognised state as red | `autoware_behavior_velocity_traffic_light_module`, traffic light recognition (F-03) |
| OEDR-06 | Stop sign, yield sign, stop line | Stop or yield as marked | `autoware_behavior_velocity_stop_line_module`, `intersection_module` |
| OEDR-07 | Cross traffic at a junction | Enter only with right of way and a sufficient gap | `autoware_behavior_velocity_intersection_module`, `blind_spot_module` |
| OEDR-08 | View blocked at a junction or crossing | Creep or wait until it can see enough | `autoware_behavior_velocity_occlusion_spot_module`, `intersection_module` |
| OEDR-09 | Emergency vehicle with siren or lights | Pull to the side if safe, or stop, and let it pass | **None in the pinned Autoware**; siren detection and the yielding manoeuvre are new work |
| OEDR-10 | Person directing traffic | Stop safely; ask for remote assistance | **None**; to be built with MON-02 |
| OEDR-11 | Obstacle or debris on the road | Stop before it, or pass it within the lane if clear | `autoware_motion_velocity_obstacle_stop_module`, `static_obstacle_avoidance_module` |
| OEDR-12 | Vehicle about to leave its lane or path (own) | Stay inside the drivable area | `autoware_motion_velocity_boundary_departure_prevention_module`, `out_of_lane_module` |

### 5.3 Manoeuvres

| ID | Manoeuvre | Inside the ODD | Realised by (pinned) |
|---|---|---|---|
| MAN-01 | Lane following and speed keeping | Yes | `autoware_behavior_path_planner`, `autoware_velocity_smoother`, trajectory follower |
| MAN-02 | Lane change, including to pass a stopped vehicle | Yes | `autoware_behavior_path_lane_change_module`, `avoidance_by_lane_change_module` |
| MAN-03 | Turns at signalised junctions with a protected phase | Yes | `autoware_behavior_velocity_intersection_module`, `traffic_light_module` |
| MAN-04 | Unprotected turns across oncoming traffic, including left turns on a permissive green | Yes (DQ-011 C) | `autoware_behavior_velocity_intersection_module` |
| MAN-05 | Roundabouts, single-lane and multi-lane | Yes (DQ-011 C) | `autoware_behavior_velocity_roundabout_module` |
| MAN-06 | Pull in to a kerbside stop and pull out again | Yes, at stops marked in the map (ODD-09) | `autoware_behavior_path_goal_planner_module`, `start_planner_module` |
| MAN-07 | Stop in lane as a minimal risk manoeuvre, with hazard lights on | Yes, as the rated fallback (DQ-016 A) | `autoware_mrm_comfortable_stop_operator`, `mrm_emergency_stop_operator`; the safety monitor's own stop |
| MAN-10 | Pull over to the kerb as a minimal risk manoeuvre | Yes, when Autoware still can (DQ-016 A); not rated | **None in the pinned Autoware**: `mrm_handler` can select a pull-over MRM, but no operator exists; to be built |
| MAN-08 | Reversing, U-turns, three-point turns | No | Excluded by route planning |
| MAN-09 | Crossing a centre line to pass an obstacle | Proposed: only when the map allows it and oncoming traffic is clear | `autoware_behavior_path_static_obstacle_avoidance_module` |

## 6. Input space of the AI components

ISO/PAS 8800 asks for the input space of each AI component to be defined from the ODD. The perception models (WP-C-01 F-02, F-03) see the ODD through the sensors, so their input space is the product of §3 with the sensor set, which is open until the vehicle is chosen (WP-H-02). For now it is stated as the conditions the training and test data must cover:

| Dimension | Must cover | From |
|---|---|---|
| Object classes | Every participant of ODD-16 and ODD-18, with children, wheelchairs and e-scooters as their own classes | ODD-16, ODD-18 |
| Lighting | Day, dusk, night, unlit streets, low sun and glare | ODD-12 |
| Weather | Dry and light rain up to the limit of ODD-10, with wet roads and spray | ODD-10, ODD-13 |
| Visibility | Down to the floor of ODD-11 | ODD-11 |
| Scenery | The road types, junctions and crossings of the geofence | ODD-02 to ODD-05 |
| Traffic lights | US signal heads (MUTCD), including protected-turn arrows, pedestrian and bicycle signals | ODD-04, DQ-009 A |

Gaps between this and what the pinned models were trained on are assessed in WP-C-11 and WP-W-10.

## 7. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Replace each remaining Proposed value with the safety authority's decision | G1 |
| OI-2 | Choose the state (DQ-014), then check its vehicle code against the common US rules the analyses used, and redo any rating that differs | G1 |
| OI-3 | Replace Provisional values from the chosen vehicle (DQ-008): gradients, temperature range | G2 |
| OI-4 | Specify MON-01 to MON-04 as requirements in WP-S-01 and WP-S-02 | G2 |
| OI-5 | Specify the emergency-vehicle response (OEDR-09) and the person-directing-traffic response (OEDR-10), which Autoware does not provide | G2 |
| OI-6 | Define the geofence and its map coverage once the first market and city are known | G1 |
