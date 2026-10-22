# WP-S-07 Cybersecurity requirements and architectural design

| Field | Value |
|---|---|
| Work product | WP-S-07 Cybersecurity requirements and architectural design |
| Standard reference | UL 4600 §11; ISO/SAE 21434 §10; ASPICE 4.0 SEC.1, SYS.3 |
| Version | 0.5 (public tier: the text and verification of the technical requirements, the trust zones, conduits, exposed interfaces and Figures 3-1 and 4-1 moved out of the public repository (WP-M-09 §4); 2026-10-25). 0.4 (folder page `secarch/README.md` with the whole of WP-S-07 on one page, Figure 4-1 on where an attacker can reach the item and what stops them, and `secarch/requirements.csv` tracing every technical cybersecurity requirement; 2026-10-25). 0.3 (no short-range wireless on the vehicle (DQ-037 A); 2026-10-24). 0.2 (first content: technical cybersecurity requirements refined from WP-C-10 with their CAL, trust zones and conduits over the WP-S-05 interfaces, and the interfaces exposed outside the vehicle, generated from `secarch/secarch.yaml`; 2026-10-24). 0.1 (skeleton; 2026-10-22) |
| Status | Draft |
| ASIL / scope | CS (up to CAL4) |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-007) |
| Baseline | Upstream Autoware `ed48f39` (fork point); `autoware_universe` 0.52.1 |

## 1. Purpose

The cybersecurity requirements refined from the cybersecurity concept of [WP-C-10](../02-concept/WP-C-10-cybersecurity-goals-and-concept.md), allocated to the components of [WP-S-03](WP-S-03-technical-safety-concept-architecture.md), and the security architecture they sit in (ISO/SAE 21434 §10.4.1): the trust zones, the conduits that cross them over the interfaces of [WP-S-05](WP-S-05-hsi-specification.md), and the interfaces through which the item can be reached from outside the vehicle.

> [!IMPORTANT]
> **This repository is public.** The text and verification of each technical cybersecurity requirement, the trust zones, the conduits, the exposed interfaces with their attack vectors, and the TARA repeated on the design are restricted ([WP-M-09 §4](../01-management/WP-M-09-cybersecurity-plan.md#4-handling-of-cybersecurity-information)) and kept outside it. This page publishes each requirement's trace, component, allocation and CAL, and the requirements on the operating environment.

Needed at gate G2 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

<!-- BEGIN GENERATED: secarch-summary (assurance/03-system/secarch/secarch.py) -->

21 technical cybersecurity requirements refine the 8 item-level requirements of WP-C-10 onto 5 components; 12 of them at CAL4. Their text and verification, the trust zones, the conduits and the interfaces exposed outside the vehicle are restricted and not published here.

<!-- END GENERATED: secarch-summary -->

The public tier is kept in `secarch/secarch.yaml`; `secarch/secarch.py` checks it and writes the tables. It refuses an item-level requirement of WP-C-10 refined by nothing, a component that does not exist, and any restricted field.

## 2. Cybersecurity requirements

### 2.1 Technical cybersecurity requirements

Each refines an item-level requirement of WP-C-10 onto one component, in hardware, software or both. Its cybersecurity assurance level (CAL) is derived, not typed: it is the highest CAL of the goals of the requirement it refines (WP-C-10 §2). The CAL sets the rigour of its development and verification (ISO/SAE 21434 Annex E). The text and verification of each are restricted.

<!-- BEGIN GENERATED: secarch-requirements (assurance/03-system/secarch/secarch.py) -->

| ID | Refines | Component | Allocation | CAL |
|---|---|---|---|---|
| CSTR-01.01 | CSR-01 | CMP-11 Remote operations station | both | CAL4 |
| CSTR-01.02 | CSR-01 | CMP-02 Safety monitor controller | software | CAL4 |
| CSTR-01.03 | CSR-01 | CMP-02 Safety monitor controller | hardware | CAL4 |
| CSTR-01.04 | CSR-01 | CMP-02 Safety monitor controller | both | CAL4 |
| CSTR-03.01 | CSR-03 | CMP-01 Autoware computer | hardware | CAL4 |
| CSTR-03.02 | CSR-03 | CMP-01 Autoware computer | software | CAL4 |
| CSTR-03.03 | CSR-03 | CMP-02 Safety monitor controller | software | CAL4 |
| CSTR-05.01 | CSR-05 | CMP-02 Safety monitor controller | both | CAL3 |
| CSTR-05.02 | CSR-05 | CMP-03 Safety channel processor | both | CAL3 |
| CSTR-05.03 | CSR-05 | CMP-01 Autoware computer | both | CAL3 |
| CSTR-05.04 | CSR-05 | CMP-01 Autoware computer | software | CAL3 |
| CSTR-05.05 | CSR-05 | CMP-02 Safety monitor controller | hardware | CAL3 |
| CSTR-05.06 | CSR-05 | CMP-02 Safety monitor controller | both | CAL3 |
| CSTR-05.07 | CSR-05 | CMP-02 Safety monitor controller | hardware | CAL3 |
| CSTR-07.01 | CSR-07 | CMP-03 Safety channel processor | software | CAL4 |
| CSTR-07.02 | CSR-07 | CMP-01 Autoware computer | software | CAL4 |
| CSTR-08.01 | CSR-08 | CMP-01 Autoware computer | software | CAL4 |
| CSTR-09.01 | CSR-09 | CMP-01 Autoware computer | software | CAL4 |
| CSTR-11.01 | CSR-11 | CMP-01 Autoware computer | software | CAL4 |
| CSTR-12.01 | CSR-12 | CMP-01 Autoware computer | software | CAL1 |
| CSTR-12.02 | CSR-12 | CMP-09 Door system | hardware | CAL1 |

<!-- END GENERATED: secarch-requirements -->

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

The trust zones, the conduits between them and their controls are restricted (WP-M-09 §4).

## 4. Interfaces exposed outside the vehicle

The interfaces through which the item can be reached, their attack vectors and the threats that use them are restricted (WP-M-09 §4). The lead decided that the vehicle has no short-range wireless (DQ-037 A, 2026-10-24).

## 5. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Confirm by a radio scan of the chosen vehicle that it has no short-range wireless reaching the item, or isolate what it has (DQ-037 A, DQ-008) | G2 |
| OI-2 | Confirm that the parts chosen for CMP-02 and CMP-03 provide a hardware security module, secure boot and a monotonic counter (DQ-030 A, WP-H-01) | G2 |
| OI-3 | Take CR-09 into the vehicle's development interface agreement: the by-wire bus reachable only from the monitor (DQ-008, WP-M-11) | G2 |
| OI-4 | Define the key management: who holds the release and station keys, how they are generated, rotated and revoked (WP-P-02, WP-O-05) | G3 |
| OI-5 | Repeat the TARA at design level over this architecture, as WP-C-09 OI-2 plans | G3 |
