# WP-P-07 Software tool classification and qualification (including simulators)

| Field | Value |
|---|---|
| Work product | WP-P-07 Software tool classification and qualification (including simulators) |
| Standard reference | UL 4600 §13; ISO 26262-8 §11; ISO/SAE 21434 §5; ISO/PAS 8800:2024 (Tool confidence) |
| Version | 0.2 (the simulators of WP-V-08 with their proposed tool confidence levels, generated from `06-validation/simenv/simenv.yaml`; 2026-10-24). 0.1 (skeleton: structure and clause mapping; 2026-10-22) |
| Status | Skeleton |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

Classification and qualification of the software tools used to build and verify the item, including simulators.

Needed at gate G3 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

## 2. Tool inventory

So far only the simulators are listed (§4), from the ODD simulation environment of [WP-V-08](../06-validation/WP-V-08-simulation-credibility.md) §2. The rest of the inventory (compilers, build and test tools, the assurance generators, labelling and training tools) is still to be written (OI-2).

## 3. Tool impact and error detection

To be written.

## 4. Tool confidence levels

Each simulator's tool confidence level (TCL) is computed from its tool impact (TI) and tool error detection (TD) as ISO 26262-8 §11.4.5 sets out: TCL1 for TI1; for TI2, TCL1, TCL2 or TCL3 for TD1, TD2 or TD3. The ratings are Claude's proposals (I0). The detection ratings of SIM-02 and SIM-03 rest on the correlation with the real vehicle in WP-V-08 §3: if the lead decides that simulation takes credit without it (DQ-036), they become TD3 and the TCL rises to TCL3.

<!-- BEGIN GENERATED: simenv-tools (assurance/06-validation/simenv/simenv.py) -->

| Tool | Version | Use | Tool impact | Tool error detection | TCL | State |
|---|---|---|---|---|---|---|
| SIM-01 Autoware planning simulator | 1.0.0 | A simple vehicle model under Autoware's planning and control, with perception replaced by objects placed by hand; for development and regression of planning in the concept phase | TI1: Used to develop and debug, not to produce evidence that a requirement is met; nothing it reports is claimed in the safety case | TD1: Not needed at TI1 | TCL1 | Proposed |
| SIM-02 scenario_simulator_v2 | 22.0.0 | Runs the logical scenarios of WP-V-03 against Autoware, with participants, their behaviour and the traffic rules at object level; scenarios in OpenSCENARIO XML, driven from the scenario model | TI2: Its verdicts are evidence for the pass criteria of WP-V-03; a wrong verdict, or a scene that differs from the one specified, could hide a failure of the item | TD2: The corners of each logical scenario are repeated on the track and the results compared (WP-V-08 §3); errors that change a verdict only between the corners are not caught | TCL2 | Proposed; waits on DQ-036 |
| SIM-03 AWSIM | Not pinned | Renders camera and LiDAR data in a modelled scene, for the triggering conditions that act on the sensors (light, rain, spray, glare) and for the safety channel's perception | TI2: Its sensor data are evidence for the perception requirements under the triggering conditions; data that are too clean would hide insufficiencies | TD2: Recorded vehicle data under the same conditions are replayed through the same perception and the results compared (WP-V-08 §3), once the vehicle and its sensors exist | TCL2 | Proposed; waits on DQ-036 |

<!-- END GENERATED: simenv-tools -->

## 5. Qualification methods and results

To be written.

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Write this work product | G3 |
| OI-2 | Complete the tool inventory beyond the simulators | G3 |
| OI-3 | Choose the qualification method for each tool at TCL2 or above (ISO 26262-8 §11.4.6) once DQ-036 is decided | G3 |
