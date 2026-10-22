# WP-C-09 Threat analysis and risk assessment (TARA)

| Field | Value |
|---|---|
| Work product | WP-C-09 Threat analysis and risk assessment (TARA) |
| Standard reference | UL 4600 §11; ISO/SAE 21434 §9.4, §15; ASPICE 4.0 SEC.1 |
| Version | 0.4 (public tier: attack paths, feasibility ratings and risk values moved out of the public repository (WP-M-09 §4); 2026-10-25). 0.3 (every risk of 3 or more is reduced (DQ-027 A); 2026-10-23). 0.2 (first content: assets, damage scenarios, threat scenarios with attack paths, attack feasibility from attack potential, risk values and proposed treatment, proposed cybersecurity controls, generated from `tara/tara.yaml`; 2026-10-23). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | CS |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1; a cybersecurity specialist) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

Threat analysis and risk assessment of the item, including remote operations, map and model updates and the drive-by-wire interface. With remote driving allowed (DQ-010 C), the wireless link and the remote operations centre are inside the control loop, so an attack on them is an attack on vehicle control; with no driver, nobody in the vehicle can notice and take over.

Needed at gate G1 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: tara-summary (assurance/02-concept/tara/tara.py) -->

13 assets, 11 damage scenarios and 16 threat scenarios. 11 are reduced and 5 retained (DQ-027 A); 11 cybersecurity controls are proposed for WP-C-10. Attack paths, feasibility ratings and risk values are restricted and not published here.

<!-- END GENERATED: tara-summary -->

The analysis follows the steps of ISO/SAE 21434 §15: assets, damage scenarios and their impact, threat scenarios and attack paths, attack feasibility, risk value and treatment. The public tier is kept in `tara/tara.yaml`; `tara/tara.py` writes the tables. It refuses an asset no threat reaches, a damage scenario no threat leads to, a threat to reduce with no control named, and any restricted field.

> [!IMPORTANT]
> **This repository is public.** The attack paths, the attack feasibility ratings and the risk values of this TARA are restricted ([WP-M-09 §4](../01-management/WP-M-09-cybersecurity-plan.md#4-handling-of-cybersecurity-information)) and are kept outside it. This page publishes the assets, damage scenarios, threat scenarios, the treatment of each and the proposed controls.

**What the ratings mean.** The restricted ratings are made against the concept as it stands, before any cybersecurity control is designed. A high risk here says the concept is exposed and needs a control, not that the product will be insecure. The cybersecurity goals and the concept that meets them follow in [WP-C-10](WP-C-10-cybersecurity-goals-and-concept.md), and the TARA is repeated on the design (WP-S-07).

## 2. Assets and damage scenarios

Assets are what an attacker could harm, with the cybersecurity properties that matter for each: confidentiality (C), integrity (I) and availability (A).

<!-- BEGIN GENERATED: tara-assets (assurance/02-concept/tara/tara.py) -->

| ID | Asset | Properties | Threat scenarios |
|---|---|---|---|
| A-01 | Remote driving commands | I, A | TS-01, TS-04 |
| A-02 | Remote assistance and release messages | I, A | TS-02, TS-04 |
| A-03 | Remote operator accounts and the operations station | C, I | TS-03 |
| A-04 | Trip and route commands from the fleet backend | I | TS-14 |
| A-05 | Safety monitor firmware and envelope parameters | I | TS-05 |
| A-06 | Autoware software, parameters and ML models | I | TS-06, TS-07 |
| A-07 | HD map data | I | TS-06, TS-07 |
| A-08 | Update packages and the update channel | I, A | TS-06 |
| A-09 | Sensor inputs (LiDAR, cameras, radar, GNSS, microphones) | I, A | TS-08, TS-09, TS-10 |
| A-10 | Command path to the drive-by-wire (I-03, I-04) | I, A | TS-11, TS-16 |
| A-11 | Passenger trip data and cabin video | C | TS-12 |
| A-12 | Fleet telemetry and vehicle positions | C, A | TS-04, TS-13 |
| A-13 | Passenger interface (stop request, doors) | I | TS-15 |

<!-- END GENERATED: tara-assets -->

Damage scenarios are what happens when a property is lost. Each is rated in the four impact categories of ISO/SAE 21434; the safety impact uses the severity scale of the HARA (Severe for S3, Major for S2, Moderate for S1, Negligible for S0), and the scenario names the HARA hazards it can cause.

<!-- BEGIN GENERATED: tara-damage (assurance/02-concept/tara/tara.py) -->

| ID | Damage scenario | Safety | Financial | Operational | Privacy | HARA hazards |
|---|---|---|---|---|---|---|
| DS-01 | The vehicle is driven into a road user by commands the operator did not give | Severe | Major | Major | Negligible | H-08 |
| DS-02 | The vehicle moves off from a minimal risk condition while a passenger is getting out | Severe | Moderate | Moderate | Negligible | H-05 |
| DS-03 | Vehicles across the fleet stop in lane at once and cannot be released | Major | Major | Severe | Negligible | H-03 |
| DS-04 | The safety envelope is disabled or widened, so the monitor no longer stops unsafe commands | Severe | Major | Major | Negligible | H-01, H-02, H-04 |
| DS-05 | Autoware drives unsafely because its software, models or map were altered | Severe | Major | Major | Negligible | H-02, H-04, H-06 |
| DS-06 | Perception or localisation is deceived by false sensor input, and the vehicle acts on a false world | Severe | Moderate | Moderate | Negligible | H-02, H-03, H-04 |
| DS-07 | A fake siren or emergency light makes vehicles pull over or stop without need | Moderate | Negligible | Moderate | Negligible | H-03 |
| DS-08 | Passengers' trips or cabin video are disclosed | Negligible | Major | Moderate | Major | — |
| DS-09 | The positions of the fleet are tracked by an outsider | Negligible | Moderate | Moderate | Moderate | — |
| DS-10 | A vehicle with a passenger aboard is sent somewhere the passenger did not ask to go | Major | Major | Major | Severe | — |
| DS-11 | A false stop request or door command stops the vehicle where it should not, or opens a door | Moderate | Negligible | Moderate | Negligible | H-03 |

<!-- END GENERATED: tara-damage -->

## 3. Threat scenarios and attack paths

Threat scenarios were found by applying STRIDE to each asset and to each interface of the item ([WP-C-01 §5.2](WP-C-01-item-definition.md#52-interfaces)), and by taking the STPA scenarios whose cause could be an attacker ([WP-A-05](../08-analyses/WP-A-05-stpa.md) LS-10, LS-13, LS-15).

<!-- BEGIN GENERATED: tara-threats (assurance/02-concept/tara/tara.py) -->

| ID | Threat scenario | STRIDE | Assets | Damage | Impact |
|---|---|---|---|---|---|
| TS-01 | Inject or alter remote driving commands on the wireless link | Tampering | A-01 | DS-01 | Severe |
| TS-02 | Replay or forge a release from a minimal risk condition | Spoofing | A-02 | DS-02 | Severe |
| TS-03 | Take over a remote operator's account | Spoofing | A-03 | DS-01, DS-02, DS-10 | Severe |
| TS-04 | Jam the vehicles' radio links, or flood the backend, so remote operations is lost | Denial of service | A-01, A-02, A-12 | DS-03 | Severe |
| TS-05 | Alter the safety monitor's firmware or envelope parameters through a service or debug port | Tampering | A-05 | DS-04 | Severe |
| TS-06 | Deliver malicious software, models or maps through the update channel | Tampering | A-06, A-07, A-08 | DS-05 | Severe |
| TS-07 | An insider alters a map or model before it is released | Tampering | A-06, A-07 | DS-05 | Severe |
| TS-08 | Spoof LiDAR or camera inputs (laser spoofing, adversarial patches on signs or road) | Spoofing | A-09 | DS-06 | Severe |
| TS-09 | Spoof GNSS used to initialise the vehicle's pose | Spoofing | A-09 | DS-06 | Severe |
| TS-10 | Play a siren or show emergency lights to make vehicles pull over | Spoofing | A-09 | DS-07 | Moderate |
| TS-11 | Reach the drive-by-wire bus past the safety monitor | Elevation of privilege | A-10 | DS-04 | Severe |
| TS-12 | Read passengers' trip data or cabin video from the backend | Information disclosure | A-11 | DS-08 | Major |
| TS-13 | Track the fleet from its telemetry | Information disclosure | A-12 | DS-09 | Moderate |
| TS-14 | Send a vehicle with a passenger aboard to another destination | Tampering | A-04 | DS-10 | Severe |
| TS-15 | Fake a stop request or door command through the passenger interface or app | Spoofing | A-13 | DS-11 | Moderate |
| TS-16 | Tamper with the command path between Autoware and the safety monitor inside the vehicle | Tampering | A-10 | DS-01 | Severe |

<!-- END GENERATED: tara-threats -->

## 4. Impact and feasibility ratings

The impact of a threat is the highest impact, over every category, of the damage scenarios it leads to; it is in the §3 table. Attack feasibility uses the attack potential approach of ISO/SAE 21434 (Annex G, after ISO/IEC 18045). The feasibility ratings are restricted (WP-M-09 §4) and are not published here.

## 5. Treatment decisions

Which risks are reduced and which are accepted is a risk acceptance for the safety authority. The lead decided (DQ-027 A, 2026-10-23) that every risk of 3 or more is reduced, and risks of 1 and 2 are retained, each with a written reason in WP-C-10. The risk values themselves are restricted; the treatment below is their outcome.

<!-- BEGIN GENERATED: tara-risk (assurance/02-concept/tara/tara.py) -->

| ID | Treatment | Controls |
|---|---|---|
| TS-01 | Reduce | SR-02, FSR-08.01, FSR-08.02, FSR-08.03 |
| TS-02 | Reduce | SR-02, FSR-05.01, FSR-07.04 |
| TS-03 | Reduce | CR-01, FSR-08.02 |
| TS-04 | Reduce | CR-02, AOU-09 |
| TS-07 | Reduce | CR-05, SR-03 |
| TS-08 | Reduce | FM-02, FSR-02.01, CR-06 |
| TS-09 | Reduce | FM-09, CR-07 |
| TS-10 | Reduce | CR-08 |
| TS-12 | Reduce | CR-10 |
| TS-14 | Reduce | CR-01, CR-11 |
| TS-15 | Reduce | FSR-05.05, AOU-06, TR-16 |
| TS-05 | Retain | CR-03 |
| TS-06 | Retain | CR-04, SR-03 |
| TS-11 | Retain | CR-09 |
| TS-13 | Retain | CR-10 |
| TS-16 | Retain | FSR-01.01, FSR-04.01, FSR-07.01 |

<!-- END GENERATED: tara-risk -->

The controls proposed for the risks to reduce are below. Several reuse requirements the STPA already found (SR-02 authenticated, fresh messages; SR-03 updates only out of service) or the safety concept (FSR-08.01 to FSR-08.03 on remote commands). The rest are new, and go to WP-C-10 as the basis for the cybersecurity goals.

<!-- BEGIN GENERATED: tara-controls (assurance/02-concept/tara/tara.py) -->

| ID | Proposed cybersecurity control | For |
|---|---|---|
| CR-01 | Remote operator accounts use phishing-resistant multi-factor authentication, least privilege and per-action logging; vehicle-level actions need a second confirmation | TS-03, TS-14 |
| CR-02 | Vehicles keep a second, independent link to remote operations, and a release can be given locally by a field technician when both are lost | TS-04 |
| CR-03 | The safety monitor accepts only signed firmware and parameters, its debug ports are closed in production, and its housing is sealed and checked | TS-05 |
| CR-04 | Updates are signed with keys held in hardware, verified by the vehicle before install, and released only through the change process (WP-P-02) | TS-06 |
| CR-05 | Maps and training data are changed only through reviewed, logged changes with separation of duties | TS-07 |
| CR-06 | Perception is tested against known physical attacks on sensors and models (WP-C-11) | TS-08 |
| CR-07 | The initial pose is cross-checked against the map and the last known pose before use, and GNSS is never trusted alone | TS-09 |
| CR-08 | An emergency vehicle detection is confirmed by sound and light together, and a yield in a place where no emergency vehicle is plausible is reported | TS-10 |
| CR-09 | The drive-by-wire accepts commands only from the safety monitor, and the vehicle's other units cannot reach that bus (WP-H-07) | TS-11 |
| CR-10 | Trip data, video and telemetry are encrypted in transit and at rest, kept only as long as needed, and accessed by role | TS-12, TS-13 |
| CR-11 | A route change with a passenger aboard is shown to the passenger and confirmed by them or by an operator | TS-14 |

<!-- END GENERATED: tara-controls -->

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Check the attack potential values and the risk matrix against the text of ISO/SAE 21434 Annexes G and H | G1 |
| OI-2 | Write the reason for retaining each risk of 1 or 2 (WP-C-10) | G1 |
| OI-3 | Derive the cybersecurity goals, claims and CALs from §5 (WP-C-10) | G1 |
| OI-4 | Add the threats of the vehicle's own interfaces (telematics, diagnostics, charging) once it is chosen (DQ-008) | G2 |
| OI-5 | Repeat the TARA on the design, with controls in place, to show residual risk (WP-S-07) | G3 |
| OI-6 | Review by a cybersecurity specialist independent of the author | G1 |
