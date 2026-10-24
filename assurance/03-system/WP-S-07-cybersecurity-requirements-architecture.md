# WP-S-07 Cybersecurity requirements and architectural design

| Field | Value |
|---|---|
| Work product | WP-S-07 Cybersecurity requirements and architectural design |
| Standard reference | UL 4600 §11; ISO/SAE 21434 §10; ASPICE 4.0 SEC.1, SYS.3 |
| Version | 0.2 (first content: technical cybersecurity requirements refined from WP-C-10 with their CAL, trust zones and conduits over the WP-S-05 interfaces, and the interfaces exposed outside the vehicle, generated from `secarch/secarch.yaml`; 2026-10-24). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | CS (up to CAL4) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

The cybersecurity requirements refined from the cybersecurity concept of [WP-C-10](../02-concept/WP-C-10-cybersecurity-goals-and-concept.md), allocated to the components of [WP-S-03](WP-S-03-technical-safety-concept-architecture.md), and the security architecture they sit in (ISO/SAE 21434 §10.4.1). The architecture has three parts:

- the trust zones;
- the conduits that cross them, over the interfaces of [WP-S-05](WP-S-05-hsi-specification.md);
- the interfaces through which the item can be reached from outside the vehicle.

Needed at gate G2 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: secarch-summary (assurance/03-system/secarch/secarch.py) -->

21 technical cybersecurity requirements refine the 8 item-level requirements of WP-C-10 onto 5 components; 12 of them at CAL4. The 11 components sit in 4 trust zones; 6 interfaces cross a zone and each is a conduit with its controls. 7 interfaces are exposed outside the vehicle, and every threat of the TARA reaches the item through one of them.

<!-- END GENERATED: secarch-summary -->

The model is kept in `secarch/secarch.yaml`; `secarch/secarch.py` checks it and writes the tables and Figure 3-1. It refuses a model in which:

- an item-level requirement of WP-C-10 is refined by nothing;
- a component sits in no zone;
- an interface crosses zones without being a conduit with controls;
- a threat of the TARA reaches the item through no exposed interface;
- a threat whose risk is reduced is exposed through an interface none of whose controls serves its goal.

## 2. Cybersecurity requirements

### 2.1 Technical cybersecurity requirements

Each refines an item-level requirement of WP-C-10 onto one component, in hardware, software or both. Its cybersecurity assurance level (CAL) is derived, not typed: it is the highest CAL of the goals of the requirement it refines (WP-C-10 §2). The CAL sets the rigour of its development and verification (ISO/SAE 21434 Annex E).

<!-- BEGIN GENERATED: secarch-requirements (assurance/03-system/secarch/secarch.py) -->

| ID | Technical cybersecurity requirement | Component | Zone | Allocation | CAL | Refines | Verification |
|---|---|---|---|---|---|---|---|
| CSTR-01.01 | Sign every remote driving command, assistance command and release with a key held in the station's hardware security module, bound to one vehicle's identity, with sequence number and time stamp (TSR-19.01) | CMP-11 Remote operations station | SZ-1 | both | CAL4 | CSR-01 | Interface test; review of the key handling; penetration test of the station |
| CSTR-01.02 | Verify the signature of every remote message, and reject one for another vehicle, out of sequence, older than P-09 or with a bad signature, before any of its content is used (TSR-05.02, TSR-06.05) | CMP-02 Safety monitor controller | SZ-3 | software | CAL4 | CSR-01 | Fault injection of forged, replayed, misaddressed and aged messages (WP-S-05 SIG-01, SIG-02); fuzzing of the message parser |
| CSTR-01.03 | Keep the verification keys and the vehicle identity in the hardware security module of the monitor's controller, readable only by the verification, and replaceable only through CSTR-05.01 | CMP-02 Safety monitor controller | SZ-3 | hardware | CAL4 | CSR-01 | Review of the controller's security manual (DQ-030 A); test that keys cannot be read out through EX-05 |
| CSTR-01.04 | Keep the link to the Autoware computer point to point, with no routing through the monitor, and accept on it only the messages of WP-S-05 SIG-03 to SIG-05; drop and count anything else | CMP-02 Safety monitor controller | SZ-3 | both | CAL4 | CSR-01 | Fuzzing and flooding of IF-02; review of the network design |
| CSTR-03.01 | Provide two cellular links on different networks, with separate modems and antennas, so that losing one network or one antenna leaves the other | CMP-01 Autoware computer | SZ-2 | hardware | CAL4 | CSR-03 | Design review; field test with each link disabled |
| CSTR-03.02 | Detect the loss of each link, switch to the other, and report the loss of both as TR-11 (WP-C-12) | CMP-01 Autoware computer | SZ-2 | software | CAL4 | CSR-03 | Test with each link and both links cut while driving |
| CSTR-03.03 | Accept a local release from a field technician only through an authenticated service tool on EX-05, with the release conditions of TSR-06.02, and log it | CMP-02 Safety monitor controller | SZ-3 | software | CAL4 | CSR-03 | Test of the local release with valid and invalid credentials; review of the log |
| CSTR-05.01 | Boot only firmware and envelope parameters signed with the project's release key, verified from immutable boot code; on a failed check stay silent, so that the vehicle does not move (MRM-5) | CMP-02 Safety monitor controller | SZ-3 | both | CAL3 | CSR-05 | Test with unsigned, altered and old images; review of the boot chain |
| CSTR-05.02 | Boot only signed firmware on the safety channel processor and its safety island; on a failed check report itself failed (SIG-10) | CMP-03 Safety channel processor | SZ-3 | both | CAL3 | CSR-05 | Test with unsigned and altered images |
| CSTR-05.03 | Verify the boot chain of the Autoware computer, and verify every software, map and model package against its signature before install; install only out of service | CMP-01 Autoware computer | SZ-2 | both | CAL3 | CSR-05 | Test with unsigned and altered packages; test that install is refused in service |
| CSTR-05.04 | Check at start that the software, map, model and parameter versions form one released set, and refuse to enter service otherwise | CMP-01 Autoware computer | SZ-2 | software | CAL3 | CSR-05 | Test with each part of the set changed alone |
| CSTR-05.05 | Keep a monotonic counter in the controller that refuses older firmware and parameters than those installed | CMP-02 Safety monitor controller | SZ-3 | hardware | CAL3 | CSR-05 | Rollback test |
| CSTR-05.06 | Be the only node of the safety and vehicle zones with a path to the Autoware zone, and forward nothing between them | CMP-02 Safety monitor controller | SZ-3 | both | CAL3 | CSR-05 | Network review; test that no message from the Autoware computer reaches the by-wire bus |
| CSTR-05.07 | Close the monitor's debug ports in production, open them only with an authenticated unlock that erases the keys, and seal the housing (CR-03) | CMP-02 Safety monitor controller | SZ-3 | hardware | CAL3 | CSR-05 | Test of the production debug state; inspection of the seal |
| CSTR-07.01 | Include the known physical attacks on LiDAR and radar (spoofed returns, jamming, relays) in the detection and false-detection tests of TSR-09.01 to TSR-09.06, and report a sensor whose data is implausible as degraded (TSR-10.01) | CMP-03 Safety channel processor | SZ-3 | software | CAL4 | CSR-07 | Attack tests on the bench and on the track with the sensors chosen (WP-H-02) |
| CSTR-07.02 | Test Autoware's perception against the known adversarial patches and sensor attacks for the ODD, and keep the list current with the threat monitoring of WP-O-05 | CMP-01 Autoware computer | SZ-2 | software | CAL4 | CSR-07 | Attack tests in replay and on the track; review of the list |
| CSTR-08.01 | Accept an initial pose only when scan matching against the map and the last known pose agree with it; never take a GNSS fix alone | CMP-01 Autoware computer | SZ-2 | software | CAL4 | CSR-08 | Tests with spoofed and displaced GNSS fixes at start-up |
| CSTR-09.01 | Yield to an emergency vehicle only when sound and light confirm each other, and report every yield where no emergency vehicle is plausible to remote operations | CMP-01 Autoware computer | SZ-2 | software | CAL4 | CSR-09 | Tests with siren only, lights only and both; review of the reports |
| CSTR-11.01 | Accept a change of destination or route from the backend only when it is signed, show it to the passenger, and act on it only after the passenger or an operator confirms it | CMP-01 Autoware computer | SZ-2 | software | CAL4 | CSR-11 | Tests with unsigned, unconfirmed and confirmed route changes |
| CSTR-12.01 | Accept from the passenger interface and the passenger app only the stop request and door commands, rate-limited, and pass door commands to the door system without overriding its interlocks | CMP-01 Autoware computer | SZ-2 | software | CAL1 | CSR-12 | Fuzzing of the passenger interface; tests with every other command |
| CSTR-12.02 | Act on a door command only within the door system's own interlocks, whatever the passenger interface sends (TSR-17.01) | CMP-09 Door system | SZ-4 | hardware | CAL1 | CSR-12 | Supplier evidence; vehicle test |

<!-- END GENERATED: secarch-requirements -->

Several of these meet safety requirements on the same component:

- **Signed remote messages.** The monitor's checks of a remote message (CSTR-01.02) are the same checks as TSR-05.02 and TSR-06.05. A message rejected for security is a rejected command for safety, and MRM-4 follows.
- **Failed secure boot.** If secure boot fails, the monitor stays silent (CSTR-05.01). The vehicle's own stop takes over (MRM-5), so a tampered monitor fails safe rather than driving.
- **Keys in the monitor.** The verification keys sit in the hardware security module of the ASIL D controller chosen under DQ-030 A (CSTR-01.03). Its security manual must show that it has one.

### 2.2 Requirements on the operating environment

The requirements of WP-C-10 that the remote operations centre, the fleet backend and the engineering processes meet. They are not refined here; their owners carry them, and the safety case relies on them as conditions of operation.

<!-- BEGIN GENERATED: secarch-environment (assurance/03-system/secarch/secarch.py) -->

| Requirement | Met by | Goals | Text |
|---|---|---|---|
| CSR-02 | Remote operations centre | CG-01, CG-06 | Authenticate remote operators with phishing-resistant multi-factor authentication, give each the least privilege, log every action, and ask a second confirmation for releases and route changes |
| CSR-04 | Remote operations backend | CG-02 | Protect the remote operations backend against flooding, with capacity and filtering sized for the fleet |
| CSR-06 | Map and ML engineering (WP-W-10, WP-W-12) | CG-03 | Change maps and training data only through reviewed, logged changes, with separation of duties between who changes and who releases |
| CSR-10 | Fleet backend | CG-05 | Encrypt trip data, cabin video and telemetry in transit and at rest, keep them only as long as needed, and give access by role |

<!-- END GENERATED: secarch-environment -->

## 3. Security architecture and controls

The components of WP-S-03 sit in four trust zones. The safety zone holds the safety monitor, the safety channel, its sensors and its power supply. It has no direct connection to the outside world, boots only signed software, and is the only zone with a path to the vehicle's by-wire bus. The Autoware zone is connected and QM, and the design never trusts it on its own.

<!-- BEGIN GENERATED: secarch-zones (assurance/03-system/secarch/secarch.py) -->

| Zone | Trust | Components | Exposed interfaces |
|---|---|---|---|
| SZ-1 Off-board | Not trusted by the vehicle; everything it sends is authenticated | CMP-11 Remote operations station | EX-06 |
| SZ-2 Autoware | Connected to the outside world; QM, and never in the rated path on its own | CMP-01 Autoware computer | EX-01, EX-02, EX-03, EX-04, EX-07 |
| SZ-3 Safety | Trusted; no direct connection to the outside world; boots only signed software | CMP-02 Safety monitor controller, CMP-03 Safety channel processor, CMP-04 Safety LiDAR, CMP-05 Safety radar, CMP-10 Monitor power supply | EX-05 |
| SZ-4 Vehicle | Trusted to the extent its supplier shows; reachable only from the safety zone (CR-09) | CMP-06 Drive-by-wire, CMP-07 Vehicle state sensing, CMP-08 Park brake, CMP-09 Door system | — |

<!-- END GENERATED: secarch-zones -->

![WP-S-07 Figure 3-1: four zones side by side. Off-board holds the remote operations station; Autoware holds the Autoware computer; Safety holds the safety monitor controller, the safety channel processor, the safety LiDAR and radar and the monitor's power supply; Vehicle holds the drive-by-wire, vehicle state sensing, park brake and door system. Arrows show the conduits: remote commands from off-board to the safety zone, tunnelled through the Autoware zone; Autoware's commands into the safety zone; and the safety zone's links with the vehicle. Red tags above each zone name the interfaces it exposes outside the vehicle. The same content is in the tables of §3 and §4.](secarch/fig-s07-3-1-zones.svg)

*Figure 3-1. Trust zones, conduits and exposed interfaces. Generated by `secarch/secarch.py` from `secarch/secarch.yaml`.*

Every interface of WP-S-05 that crosses a zone is a conduit, protected by technical requirements, by the controls the TARA proposed (CR), or by safety mechanisms (SM) that bound whatever crosses it:

<!-- BEGIN GENERATED: secarch-conduits (assurance/03-system/secarch/secarch.py) -->

| Interface | From → to | Zones | Controls | Note |
|---|---|---|---|---|
| IF-01 | Remote operations station → Safety monitor controller | SZ-1 → SZ-3, through SZ-2 Autoware | CSTR-01.01, CSTR-01.02, CSTR-01.03 | Tunnelled through the Autoware zone, which can delay or drop the commands but cannot forge or replay them |
| IF-02 | Autoware computer → Safety monitor controller | SZ-2 → SZ-3 | CSTR-01.04, SM-01, SM-02, SM-05 | The monitor accepts on this link only the messages of SIG-03 to SIG-05, and bounds whatever they say (CC-05) |
| IF-06 | Safety monitor controller → Drive-by-wire | SZ-3 → SZ-4 | CR-09, CSTR-05.06 | The by-wire bus carries commands only from the monitor (CC-03) |
| IF-07 | Vehicle state sensing → Safety monitor controller | SZ-4 → SZ-3 | CR-09, CSTR-05.06 | — |
| IF-08 | Safety monitor controller → Park brake | SZ-3 → SZ-4 | CR-09, CSTR-05.06 | — |
| IF-09 | Door system → Safety monitor controller | SZ-4 → SZ-3 | CR-09, CSTR-05.06 | — |

<!-- END GENERATED: secarch-conduits -->

**Remote commands cross the Autoware zone without trusting it.** They reach the monitor through the cellular links and the Autoware computer's network, because the monitor has no radio of its own. That transport can delay or drop a remote command but cannot forge, alter or replay it (CSTR-01.02). A delay or a drop becomes an aged or missing command, which the monitor treats as TR-12 and answers with MRM-4. Giving the monitor its own modem would remove the tunnel. It would also make the safety zone reachable from the network, the exposure the zones are drawn to avoid.

## 4. Interfaces exposed outside the vehicle

Every way the item can be reached from outside the vehicle, with the attack vector, the threats of the TARA ([WP-C-09](../02-concept/WP-C-09-tara.md)) that use it, and its controls. A threat marked *claim* is retained under a cybersecurity claim of WP-C-10 rather than reduced, and its controls are applied anyway where the concept says so.

<!-- BEGIN GENERATED: secarch-external (assurance/03-system/secarch/secarch.py) -->

| ID | Exposed interface | Zone | Attack vector | Threats | Controls | Waits on |
|---|---|---|---|---|---|---|
| EX-01 | Cellular links to remote operations and the fleet backend | SZ-2 | network | TS-01, TS-02, TS-04, TS-06 (claim), TS-13 (claim), TS-14 | CSTR-01.01, CSTR-01.02, CSTR-03.01, CSTR-03.02, CSTR-05.03, CSTR-11.01, CSR-04, CSR-10 | — |
| EX-02 | GNSS antenna and receiver | SZ-2 | adjacent | TS-09 | CSTR-08.01 | — |
| EX-03 | The physical scene as the sensors and microphones receive it (light, radio, sound, markings) | SZ-2 | adjacent | TS-08, TS-10 | CSTR-07.01, CSTR-07.02, CSTR-09.01 | — |
| EX-04 | Passenger interface (cabin screen, stop button) and the passenger app through the backend | SZ-2 | local | TS-14, TS-15 | CSTR-11.01, CSTR-12.01, CSTR-12.02 | — |
| EX-05 | Service and debug ports (safety monitor, Autoware computer, vehicle diagnostic connector) | SZ-3 | physical | TS-05 (claim), TS-11 (claim), TS-16 (claim) | CR-03, CSTR-05.01, CSTR-05.02, CSTR-05.05, CSTR-03.03, CSTR-05.07 | — |
| EX-06 | Remote operations centre and fleet backend, off-board | SZ-1 | network | TS-03, TS-07, TS-12 | CSR-02, CSR-06, CSR-10 | — |
| EX-07 | Short-range wireless on the vehicle (Wi-Fi, Bluetooth) | SZ-2 | adjacent | None in the TARA | — | DQ-037 |

<!-- END GENERATED: secarch-external -->

**Short-range wireless.** The design has none (EX-07), so the TARA has no threat through it. Whether the vehicle should have Wi-Fi or Bluetooth is a product choice for the lead (DQ-037, recommended: none). If one is added, its threats go into the TARA and its stack stays out of the safety and vehicle zones.

## 5. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Settle short-range wireless (DQ-037), and add its threats to the TARA if any is fitted | G2 |
| OI-2 | Confirm that the parts chosen for CMP-02 and CMP-03 provide a hardware security module, secure boot and a monotonic counter (DQ-030 A, WP-H-01) | G2 |
| OI-3 | Take CR-09 into the vehicle's development interface agreement: the by-wire bus reachable only from the monitor (DQ-008, WP-M-11) | G2 |
| OI-4 | Define the key management: who holds the release and station keys, how they are generated, rotated and revoked (WP-P-02, WP-O-05) | G3 |
| OI-5 | Repeat the TARA at design level over this architecture, as WP-C-09 OI-2 plans | G3 |
