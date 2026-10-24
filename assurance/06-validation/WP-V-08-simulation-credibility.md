# WP-V-08 Simulation credibility and scenario coverage

| Field | Value |
|---|---|
| Work product | WP-V-08 Simulation credibility and scenario coverage |
| Standard reference | UL 4600 §12, §13; ISO 26262-8 §11; ISO 21448 §9; ISO/PAS 8800:2024 (AI V&V); ASPICE 4.0 VAL.1 |
| Version | 0.3 (simulation counts as evidence only where checked against the real vehicle (DQ-036 A); 2026-10-24). 0.2 (first content: the simulators and their roles, the ODD simulation environment with a parametric vehicle and sensor stand-ins, generated from `simenv/simenv.yaml`; scenario coverage of the ODD and the analyses, generated from `scenarios/scenarios.yaml`; validation method; 2026-10-24). 0.1 (skeleton: structure and clause mapping; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | `2a7707b`; simulators as pinned in `repositories/autoware.repos` and `repositories/simulator.repos` |

## 1. Purpose

Why simulation results can be trusted as evidence: the simulators, their validation against the real vehicle, and scenario coverage of the ODD.

Needed at gate G2 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: simenv-summary (assurance/06-validation/simenv/simenv.py) -->

3 simulators, 20 ODD attributes and what the simulation must represent of each: 5 need a sensor-level scene (ODD-07, ODD-10, ODD-11, ODD-12, ODD-19), 1 is not simulated (ODD-14). 14 participant classes map to OpenSCENARIO categories. The vehicle and 8 sensor stand-ins are parameters with no values until the vehicle is chosen (DQ-008). Proposed tool confidence levels: TCL1, TCL2. No simulator has been validated (§3).

<!-- END GENERATED: simenv-summary -->

**This describes what the simulation must represent, not what a simulator is known to do.** Whether a simulator represents an attribute credibly is shown by validation against vehicle data (§3), which needs the vehicle (DQ-008). Until then no simulation result counts as evidence. The lead decided (DQ-036 A, 2026-10-24) that afterwards too a simulation result counts only where it has been checked against the real vehicle: a scenario whose corners have been repeated on the track and agreed, or a sensor condition whose rendered data have been compared with recordings and agreed. Everywhere else simulation is for exploring and for regression; it can find failures but not show their absence.

The environment is kept in `simenv/simenv.yaml` and written into §2 and [WP-P-07](../07-supporting/WP-P-07-tool-classification-qualification.md) by `simenv/simenv.py`; the scenario coverage of §4 comes from the scenario model of [WP-V-03](WP-V-03-sotif-known-scenarios.md) through `scenarios/scenarios.py`. Both read the ODD of [WP-C-02](../02-concept/WP-C-02-odd-and-intended-functionality.md) through the same structured reading, which is checked against WP-C-02's own text.

## 2. Simulators and their roles (planning simulator, AWSIM, scenario_simulator_v2)

Each simulator works at a *level*: the road network (map), entities and their motion (object), the raw data a sensor would produce (sensor), the remote operations link (link), or the ego vehicle's motion (vehicle). A triggering condition that acts on the sensors, such as rain or glare, can only be exercised at sensor level.

<!-- BEGIN GENERATED: simenv-simulators (assurance/06-validation/simenv/simenv.py) -->

| Simulator | Version | Level | Role |
|---|---|---|---|
| SIM-01 Autoware planning simulator | 1.0.0 (`repositories/autoware.repos`) | object | A simple vehicle model under Autoware's planning and control, with perception replaced by objects placed by hand; for development and regression of planning in the concept phase |
| SIM-02 scenario_simulator_v2 | 22.0.0 (`repositories/simulator.repos`) | object | Runs the logical scenarios of WP-V-03 against Autoware, with participants, their behaviour and the traffic rules at object level; scenarios in OpenSCENARIO XML, driven from the scenario model |
| SIM-03 AWSIM | Not pinned | sensor | Renders camera and LiDAR data in a modelled scene, for the triggering conditions that act on the sensors (light, rain, spray, glare) and for the safety channel's perception |

<!-- END GENERATED: simenv-simulators -->

### 2.1 Road and junction types of the geofence

The geofence is not defined yet (WP-C-02 OI-6). The simulation uses the maps of the geofence once they exist, the same versions as the vehicle (WP-W-12); until then, maps of comparable streets that contain every type below.

<!-- BEGIN GENERATED: simenv-scenery (assurance/06-validation/simenv/simenv.py) -->

| ODD attribute | Level | The simulation must represent | Simulators |
|---|---|---|---|
| ODD-01 Area | map | The Lanelet2 and point cloud maps of the geofence | SIM-01, SIM-02, SIM-03 |
| ODD-02 Road type | map | Urban and collector streets with one or two lanes per direction | SIM-01, SIM-02, SIM-03 |
| ODD-03 Posted speed limit | map | The posted limit of every lanelet | SIM-01, SIM-02, SIM-03 |
| ODD-04 Junctions | map | Signalised | SIM-01, SIM-02, SIM-03 |
| ODD-05 Crossings | map | Marked crosswalks with and without signals | SIM-01, SIM-02, SIM-03 |
| ODD-06 Road surface and geometry | vehicle | Road gradient up to the ODD limit | SIM-01, SIM-03 |
| ODD-07 Lane markings | sensor | Lane markings as the sensors see them | SIM-03 |
| ODD-08 Temporary changes | object | Work zones | SIM-02, SIM-03 |
| ODD-09 Stopping places | map | Kerbside stops marked in the map | SIM-01, SIM-02, SIM-03 |

<!-- END GENERATED: simenv-scenery -->

### 2.2 Weather and lighting

<!-- BEGIN GENERATED: simenv-environment (assurance/06-validation/simenv/simenv.py) -->

| ODD attribute | Level | The simulation must represent | Simulators |
|---|---|---|---|
| ODD-10 Precipitation | sensor | Rain up to the ODD limit as it degrades LiDAR and camera data (drops | SIM-03 |
| ODD-11 Visibility | sensor | Mist | SIM-03 |
| ODD-12 Illumination | sensor | Day | SIM-03 |
| ODD-13 Road surface condition | vehicle | Grip of a wet road acting on braking and steering in the vehicle model | SIM-01, SIM-02, SIM-03 |
| ODD-14 Temperature | none | Not simulated: Temperature acts on the hardware | — |
| ODD-15 Connectivity | link | The remote operations link with delay | SIM-02 |

<!-- END GENERATED: simenv-environment -->

### 2.3 Traffic participants and their behaviour bounds

Participants move within the bounds the requirements assume for other road users: FSR-06.01 for their speed and acceleration, FSR-06.02 for the speed of one emerging from an occlusion. No work product has fixed those values yet; when it does, they become the limits of the behaviour models, and a scenario that needs a participant to break them (a red-light runner, TC-19) says so in its own parameters.

<!-- BEGIN GENERATED: simenv-dynamic (assurance/06-validation/simenv/simenv.py) -->

| ODD attribute | Level | The simulation must represent | Simulators |
|---|---|---|---|
| ODD-16 Traffic participants | object | Every participant class of the ODD (§2.3) | SIM-02, SIM-03 |
| ODD-17 Traffic density | object | Traffic from free flow to congested | SIM-02 |
| ODD-18 Special vehicles | object | Emergency vehicles with siren and lights | SIM-02, SIM-03 |
| ODD-19 Traffic direction by people | sensor | A person directing traffic | SIM-03 |
| ODD-20 Ego speed | vehicle | Ego speed up to the ODD limit and the posted limit | SIM-01, SIM-02, SIM-03 |

<!-- END GENERATED: simenv-dynamic -->

<!-- BEGIN GENERATED: simenv-participants (assurance/06-validation/simenv/simenv.py) -->

| Participant | ODD attribute | OpenSCENARIO category | Behaviour bounded by | Note |
|---|---|---|---|---|
| car | ODD-16 | car | FSR-06.01 (not yet fixed) | — |
| van | ODD-16 | van | FSR-06.01 (not yet fixed) | — |
| bus | ODD-16 | bus | FSR-06.01 (not yet fixed) | — |
| truck | ODD-16 | truck | FSR-06.01 (not yet fixed) | — |
| motorcycle | ODD-16 | motorbike | FSR-06.01 (not yet fixed) | — |
| bicycle | ODD-16 | bicycle | FSR-06.01 (not yet fixed) | — |
| e-scooter | ODD-16 | bicycle | FSR-06.01 (not yet fixed) | OpenSCENARIO has no e-scooter category; a bicycle entity with the scooter's size stands in |
| pedestrian | ODD-16 | pedestrian | FSR-06.02 (not yet fixed) | — |
| child | ODD-16 | pedestrian | FSR-06.02 (not yet fixed) | A pedestrian entity with a child's size |
| wheelchair | ODD-16 | wheelchair | FSR-06.02 (not yet fixed) | — |
| animal | ODD-16 | animal | FSR-06.02 (not yet fixed) | — |
| emergency-vehicle | ODD-18 | car | FSR-06.01 (not yet fixed) | Siren and lights are properties of the entity; OpenSCENARIO has no emergency category |
| bus-at-stop | ODD-18 | bus | FSR-06.01 (not yet fixed) | — |
| directing | ODD-19 | pedestrian | FSR-06.02 (not yet fixed) | Gestures are not part of an OpenSCENARIO entity; they need the sensor-level scene |

<!-- END GENERATED: simenv-participants -->

### 2.4 Vehicle and sensor stand-ins

The vehicle and its sensors are chosen at G2 (DQ-008). Until then the simulated vehicle is a placeholder whose properties are parameters, and each sensor is a stand-in whose position, orientation, field of view, range and rate are parameters, not chosen values: a study sweeps them, and no result is claimed for a particular vehicle. No detailed vehicle model, sensor mounting or vehicle dynamics is built before the choice. The generator refuses a stand-in parameter that carries a value.

<!-- BEGIN GENERATED: simenv-vehicle (assurance/06-validation/simenv/simenv.py) -->

| Vehicle property (WP-C-01 §6) | In the vehicle model | Value |
|---|---|---|
| Mass, dimensions, wheelbase | Size of the ego entity and its swept path; mass for the dynamics | Parameter (DQ-008) |
| Maximum deceleration by wire, and its response time | Braking limit and delay of the vehicle model | Parameter (DQ-008) |
| Steering range, rate and response time by wire | Steering limits and delay of the vehicle model | Parameter (DQ-008) |

<!-- END GENERATED: simenv-vehicle -->

<!-- BEGIN GENERATED: simenv-sensors (assurance/06-validation/simenv/simenv.py) -->

| Stand-in | Sensor | Channel | Serves | Parameters | Values |
|---|---|---|---|---|---|
| SNS-01 | LiDAR | Autoware | — | position, orientation, horizontal field of view, vertical field of view, range, rate, noise | Parameters (DQ-008) |
| SNS-02 | cameras | Autoware | — | position, orientation, field of view, resolution, exposure, rate | Parameters (DQ-008) |
| SNS-03 | radar | Autoware | — | position, orientation, field of view, range, rate, noise | Parameters (DQ-008) |
| SNS-04 | GNSS | Autoware | — | position, noise, rate | Parameters (DQ-008) |
| SNS-05 | IMU | Autoware | — | position, noise, rate | Parameters (DQ-008) |
| SNS-06 | CMP-04 Safety LiDAR | Safety monitor | FSR-02.01 | position, orientation, horizontal field of view, vertical field of view, range, rate, noise | Parameters (DQ-008) |
| SNS-07 | CMP-05 Safety radar | Safety monitor | FSR-02.01 | position, orientation, field of view, range, rate, noise | Parameters (DQ-008) |
| SNS-08 | CMP-07 Vehicle state sensing | Safety monitor | FSR-01.05, FSR-04.06 | signals, rate, noise | Parameters (DQ-008) |

<!-- END GENERATED: simenv-sensors -->

## 3. Simulation validation against vehicle data

Nothing is validated yet: there is no vehicle. The method, for review:

| Step | What is done | Applies to |
|---|---|---|
| Correlate scenarios | The corners of each logical scenario run in simulation are repeated on the track with the real vehicle, and the outcomes compared against the pass criterion and the measured kinematics | SIM-02 |
| Correlate sensor data | Vehicle recordings under each sensor-level condition of §2.2 are replayed through the same perception as the rendered data, and the detection results compared | SIM-03 |
| Correlate the vehicle model | Braking, steering and their delays in the vehicle model are compared with measurements of the chosen vehicle | SIM-01, SIM-02, SIM-03 |
| Bound the claim | A simulator counts as evidence only for the levels and attribute ranges where the comparison holds; outside them, its results are exploration (DQ-036 A) | All |

The acceptance thresholds for each comparison are to be set with the validation targets of [WP-V-02](WP-V-02-sotif-vv-strategy.md) and are not stated here.

## 4. Scenario coverage metrics against the ODD

### 4.1 Coverage of the ODD

![WP-V-08 Figure 4-1: a matrix with one row per scenario of WP-V-03 and one column per ODD attribute of WP-C-02, grouped into scenery, environment and dynamic elements. A filled cell means the scenario varies that attribute; a red outline means it sweeps across the ODD boundary to test a monitor. A row at the bottom counts the scenarios per attribute. The same information is in the table below.](scenarios/fig-v08-4-1-coverage.svg)

*Figure 4-1. Which ODD attributes each scenario varies. Generated by `scenarios/scenarios.py` from `scenarios/scenarios.yaml`.*

<!-- BEGIN GENERATED: scenarios-coverage-odd (assurance/06-validation/scenarios/scenarios.py) -->

| ODD attribute | Values the ODD admits | Exercised by | Values not exercised |
|---|---|---|---|
| ODD-01 Area | geofence | SC-09 | — |
| ODD-02 Road type | urban-street, collector, lanes-1-2, centre-line | SC-02, SC-09, SC-17, SC-22 | — |
| ODD-03 Posted speed limit | 0 to 30 mph | SC-01, SC-03, SC-09 | — |
| ODD-04 Junctions | signalised, protected-turn, unprotected-turn, stop-controlled, yield-controlled, t-junction, roundabout-single, roundabout-multi | SC-05, SC-06, SC-07, SC-08, SC-11, SC-12, SC-16, SC-23 | — |
| ODD-05 Crossings | marked-crosswalk, signalised-crosswalk, cycle-lane, mid-block | SC-01, SC-02, SC-08, SC-16, SC-18 | — |
| ODD-06 Road surface and geometry | 0 to 8 % | SC-09, SC-15, SC-16 | — |
| ODD-07 Lane markings | markings-visible, markings-absent; outside, for monitor tests: re-marking | SC-09, SC-10 | — |
| ODD-08 Temporary changes | none, captured; outside, for monitor tests: work-zone | SC-09, SC-10 | — |
| ODD-09 Stopping places | kerbside-stop | SC-15, SC-18, SC-21 | — |
| ODD-10 Precipitation | 0 to 2.5 mm/h | SC-01, SC-03, SC-04, SC-14 | — |
| ODD-11 Visibility | 200 m and above | SC-04, SC-14 | — |
| ODD-12 Illumination | day, dusk, night, unlit, low-sun | SC-01, SC-02, SC-05, SC-06, SC-10, SC-11, SC-13, SC-14, SC-17, SC-19, SC-20, SC-25 | — |
| ODD-13 Road surface condition | dry, wet | SC-01, SC-03, SC-04, SC-13, SC-14, SC-16 | — |
| ODD-14 Temperature | in-range | SC-26 | — |
| ODD-15 Connectivity | link-available, gnss-lost; outside, for monitor tests: link-lost | SC-09, SC-20, SC-21, SC-24, SC-25 | — |
| ODD-16 Traffic participants | car, van, bus, truck, motorcycle, bicycle, e-scooter, pedestrian, child, wheelchair, animal | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-13, SC-14, SC-15, SC-16, SC-18, SC-19, SC-20, SC-22, SC-23 | — |
| ODD-17 Traffic density | free-flow, congested | SC-03, SC-05, SC-07, SC-09, SC-12, SC-17, SC-19, SC-23 | — |
| ODD-18 Special vehicles | emergency-vehicle, bus-at-stop | SC-12, SC-18 | — |
| ODD-19 Traffic direction by people | None; outside, for monitor tests: directing | SC-11 | — |
| ODD-20 Ego speed | 0 to 50 km/h, capped by ODD-03 at 48.3 km/h | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-07, SC-08, SC-09, SC-10, SC-11, SC-12, SC-13, SC-14, SC-15, SC-17, SC-18, SC-20, SC-22, SC-23 | — |

<!-- END GENERATED: scenarios-coverage-odd -->

### 4.2 Coverage of the analyses

<!-- BEGIN GENERATED: scenarios-coverage-analyses (assurance/06-validation/scenarios/scenarios.py) -->

| Analysis | Items | With a scenario | Without |
|---|---|---|---|
| Triggering conditions (WP-C-06) | 29 | 29 | — |
| Misuse and interaction (WP-C-08) | 23 | 23 | — |
| Hazardous events (WP-C-03) | 19 | 19 | — |
| STPA loss scenarios (WP-A-05) | 27 | 27 | — |
| Safety goals (WP-C-03) | 9 | 9 | — |

<!-- END GENERATED: scenarios-coverage-analyses -->

These are counts of what the catalogue *exercises*, not of what has been shown. Coverage of the parameter space within each scenario, and the number of concrete runs, follow from the sampling plan (WP-V-03 OI-4).

## 5. Tool confidence (link to WP-P-07)

The simulators that produce evidence are software tools in the sense of ISO 26262-8 §11 and UL 4600 §13. Their proposed classification, with the tool confidence level computed from tool impact and tool error detection, is in [WP-P-07 §4](../07-supporting/WP-P-07-tool-classification-qualification.md#4-tool-confidence-levels). The error detection rating of SIM-02 and SIM-03 rests on the correlation of §3, which the lead made the condition for any simulation credit (DQ-036 A); they are therefore TD2 and TCL2, and need qualification at that level (WP-P-07 OI-3).

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Pin AWSIM in the repository and record its version (SIM-03) | G2 |
| OI-2 | Confirm, by test, which attributes of §2 each simulator can represent at the level the table asks for, and correct the table where it cannot | G2 |
| OI-3 | Replace the vehicle and sensor parameters with the chosen vehicle's values, and correlate the vehicle model (DQ-008) | G2 |
| OI-4 | Set the acceptance thresholds of each comparison in §3 with WP-V-02 | G2 |
| OI-5 | Plan the track time for the corners of every logical scenario, and the recordings for every sensor-level condition, that DQ-036 A requires, with WP-V-02 | G2 |
| OI-6 | Run the validation of §3 and record the results | G3 |
