# WP-M-00 Work Product Register

| Field | Value |
|---|---|
| Work product | WP-M-00 Work product register |
| Standard reference | UL 4600 §5 (safety case work products); ISO 26262-2:2018 §6 (safety plan, work product list); ISO/SAE 21434:2021 §6; ASPICE 4.0 MAN.3 (define work products), SUP.8 (configuration items) |
| Version | 0.12 (WP-C-09 drafted; 2026-10-23). 0.11 (WP-A-05 drafted; 2026-10-23). 0.10 (WP-C-07 drafted; 2026-10-23). 0.9 (WP-C-06 drafted; 2026-10-23). 0.8 (WP-C-12 drafted; 2026-10-23). 0.7 (WP-C-05 drafted; 2026-10-23). 0.6 (WP-C-04 drafted; 2026-10-23). 0.5 (WP-C-03 drafted; 2026-10-23). 0.4 (WP-C-02 drafted; 2026-10-23). 0.3 (WP-C-01 drafted; 2026-10-23). 0.2 (G2 exit criterion adds the vehicle choice, deferred to G2 by DQ-003 C; 2026-10-23). 0.1 (first issue: every work product of the assurance path, its clauses, gate and status; 2026-10-22) |
| Status | Draft |
| ASIL / scope | All |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

This register lists every work product that the assurance path for the Autoware-based driverless system needs. For each one it records the clauses it answers, the gate that needs it and its status. The [assurance strategy (WP-M-01)](WP-M-01-assurance-strategy.md) explains why the list looks the way it does; the [functional safety plan (WP-M-02)](WP-M-02-safety-plan.md) uses it as its list of work products; [configuration management (WP-P-01)](../07-supporting/WP-P-01-configuration-management-plan.md) puts each entry under configuration control.

UL 4600 is the primary framework, because the system has no driver to hand control back to: the safety case has to argue that the vehicle itself is acceptably safe across its whole operational design domain, including its own failures and its fallback. The register therefore gives UL 4600 its own column, and adds work products that a supervised system would not need: the fallback and minimal-risk concept (WP-C-12), HD map data (WP-W-12), simulation credibility (WP-V-08), safety performance indicators (WP-O-06) and the independent UL 4600 assessment (WP-K-07).

A work product tailored out stays in the register with status `N/A` and a reference to its rationale in [WP-M-01 §5](WP-M-01-assurance-strategy.md#5-tailoring).

## 2. Gates

| Gate | Name | Exit criterion (summary) |
|---|---|---|
| G0 | Governance | Plans approved; safety authority, assessor and roles named; CM and change control running |
| G1 | Concept | Item and ODD fixed; HARA, FSC, fallback concept, SOTIF hazards and insufficiencies, TARA and CS concept approved; HARA confirmation review (I3) passed; test operations with safety drivers approved |
| G2 | System design | Vehicle and drive-by-wire platform chosen and the provisional concept ratings confirmed (DQ-008); TSC, system architecture, HSI, timing, simulation credibility plan, SPIs and system-level safety analyses approved |
| G3 | HW/SW development | HW and SW safety requirements, architecture, units and unit verification approved for every safety-relevant element; elements not developed to ISO 26262 qualified or argued |
| G4 | Integration and verification | SW, HW and system integration and verification complete; fault injection campaign closed; known scenarios evaluated |
| G5 | Validation and release | Safety validation, SOTIF residual risk acceptance, CS validation, safety case, FSA, CS assessment and UL 4600 assessment complete; release for driverless operation in the ODD signed |
| G6 | Operation | Field monitoring, SPI monitoring, incident response and update processes running |

## 3. Register

Clause columns cite the editions in [assurance/README.md](../README.md#standards-text): UL 4600 (3rd edition), ISO 26262:2018, ISO 21448:2022, ISO/SAE 21434:2021, ISO/PAS 8800:2024 (cited by topic) and Automotive SPICE PAM 4.0 (process IDs, including the MLE, VAL and SEC processes).
**Status**: S = Skeleton, D = Draft, R = In review, A = Approved, B = Baselined, N/A = tailored out.

![Figure 3-1: work-product status by gate, one row per folder section of §3.1 to §3.11, a bar at each gate G0 to G6 with the number of work products that gate needs, split by status](figures/fig-m00-3-1-wp-status.svg)

*Figure 3-1.* How many work products each gate needs, by folder section, coloured by status. Drawn from §2 and the §3 tables by [`figures/fig_m00_register.py`](figures/fig_m00_register.py); CI fails if it is stale. Change it together with §2 and §3.

### 3.1 Management (`01-management/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-M-00](WP-M-00-work-product-register.md) | Work product register | §5 | 2 §6 | | §6 | | MAN.3, SUP.8 | G0 | D |
| [WP-M-01](WP-M-01-assurance-strategy.md) | Assurance strategy and lifecycle tailoring | §5, §17 | 2 §6 | §4 | §6 | AI safety management | MAN.3 | G0 | D |
| [WP-M-02](WP-M-02-safety-plan.md) | Functional safety plan | §5 | 2 §6 | | | | MAN.3 | G0 | S |
| [WP-M-03](WP-M-03-project-plan.md) | Project plan (scope, WBS, schedule, resources) | | | | | | MAN.3 | G0 | S |
| [WP-M-04](WP-M-04-organization-competence-safety-culture.md) | Organization, roles, competence and safety culture | §5 | 2 §5 | | §5 | AI safety management | | G0 | S |
| [WP-M-05](WP-M-05-quality-assurance-plan.md) | Quality management and quality assurance plan | | 2 §5 | | §5 | | SUP.1 | G0 | S |
| [WP-M-06](WP-M-06-confirmation-measures-plan.md) | Confirmation measures plan (reviews, audit, assessment, independence) | §17 | 2 §6 | §4 | §6 | | | G0 | S |
| [WP-M-07](WP-M-07-risk-management.md) | Project risk management plan and register | | | | | | MAN.5 | G0 | S |
| [WP-M-08](WP-M-08-sotif-plan.md) | SOTIF plan | | | §4 | | | MAN.3 | G0 | S |
| [WP-M-09](WP-M-09-cybersecurity-plan.md) | Cybersecurity plan | | | | §6 | | MAN.7 | G0 | S |
| [WP-M-10](WP-M-10-ai-safety-plan.md) | AI safety management plan (perception and prediction models) | §8 | | | | AI safety management | MLE.1–4, SUP.11 | G0 | S |
| [WP-M-11](WP-M-11-upstream-and-supplier-management.md) | Upstream (Autoware Foundation) and supplier management, development interface agreements | §13 | 8 §5 | | §7 | | ACQ.4 | G0 | S |
| [WP-M-12](WP-M-12-reuse-and-impact-analysis.md) | Reuse and impact analysis of the Autoware baseline | §13 | 2 §6, 8 §16 | | §6 | | REU.2 | G0 | S |
| [WP-M-13](WP-M-13-aspice-capability-baseline.md) | ASPICE capability baseline (self-assessment) | | | | | | All in scope | G0 | S |

### 3.2 Concept phase (`02-concept/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-C-01](../02-concept/WP-C-01-item-definition.md) | Item definition | §5 | 3 §5 | §5 | §9.3 | | SYS.1 | G1 | D |
| [WP-C-02](../02-concept/WP-C-02-odd-and-intended-functionality.md) | ODD and intended functionality (DDT, OEDR, manoeuvres) | §8 | 3 §5 | §5 | | Input space definition | SYS.1 | G1 | D |
| [WP-C-03](../02-concept/WP-C-03-hara.md) | Hazard analysis and risk assessment, safety goals | §6 | 3 §6 | | | | | G1 | D |
| [WP-C-04](../02-concept/WP-C-04-functional-safety-concept.md) | Functional safety concept (FSRs, allocation, assumptions) | §10 | 3 §7 | | | | SYS.2 | G1 | D |
| [WP-C-05](../02-concept/WP-C-05-sotif-hazard-identification.md) | SOTIF hazard identification, risk evaluation and acceptance criteria | §6 | | §6 | | | | G1 | D |
| [WP-C-06](../02-concept/WP-C-06-sotif-insufficiencies-triggering-conditions.md) | Functional insufficiencies and triggering conditions | §8 | | §7 | | AI error causes | | G1 | D |
| [WP-C-07](../02-concept/WP-C-07-sotif-functional-modifications.md) | Functional modifications addressing SOTIF risk | | | §8 | | | SYS.2 | G1 | D |
| [WP-C-08](../02-concept/WP-C-08-human-interaction-misuse-analysis.md) | Interaction with passengers, road users and remote operators; foreseeable misuse | §7 | 3 §6 | §6 | | | | G1 | S |
| [WP-C-09](../02-concept/WP-C-09-tara.md) | Threat analysis and risk assessment (TARA) | §11 | | | §9.4, §15 | | SEC.1 | G1 | D |
| [WP-C-10](../02-concept/WP-C-10-cybersecurity-goals-and-concept.md) | Cybersecurity goals, claims and concept | §11 | | | §9.4, §9.5 | | SEC.1 | G1 | S |
| [WP-C-11](../02-concept/WP-C-11-ai-system-definition-and-safety-requirements.md) | AI system definition and AI safety requirements | §8 | | §7 | | AI safety requirements | MLE.1 | G1 | S |
| [WP-C-12](../02-concept/WP-C-12-fallback-and-minimal-risk-concept.md) | Fallback, minimal risk manoeuvres and minimal risk conditions | §8, §10 | 3 §7 | §5, §8 | | | SYS.2 | G1 | D |

### 3.3 System level (`03-system/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-S-01](../03-system/WP-S-01-system-requirements.md) | System requirements specification | §9 | | §5 | | | SYS.2 | G2 | S |
| [WP-S-02](../03-system/WP-S-02-technical-safety-requirements.md) | Technical safety requirements specification | §10 | 4 §6 | | | | SYS.2 | G2 | S |
| [WP-S-03](../03-system/WP-S-03-technical-safety-concept-architecture.md) | Technical safety concept and system architectural design | §10 | 4 §6 | §8 | | AI architecture measures | SYS.3 | G2 | S |
| [WP-S-04](../03-system/WP-S-04-timing-ftti-budget.md) | Timing: FTTI, detection and reaction budget, fallback timing | §10 | 4 §6 | | | | SYS.3 | G2 | S |
| [WP-S-05](../03-system/WP-S-05-hsi-specification.md) | Hardware-software interface, including the drive-by-wire interface | §10 | 4 §6 | | | | SYS.3 | G2 | S |
| [WP-S-06](../03-system/WP-S-06-requirements-production-operation.md) | Requirements for production, operation, service and decommissioning | §14, §15 | 4 §6 | §13 | §10 | | SYS.2 | G2 | S |
| [WP-S-07](../03-system/WP-S-07-cybersecurity-requirements-architecture.md) | Cybersecurity requirements and architectural design | §11 | | | §10 | | SEC.1, SYS.3 | G2 | S |
| [WP-S-08](../03-system/WP-S-08-system-integration-test.md) | System integration and test strategy, specification and report | §12 | 4 §7 | | | | SYS.4 | G4 | S |
| [WP-S-09](../03-system/WP-S-09-system-verification.md) | System verification specification and report | §12 | 4 §7 | §10 | | | SYS.5 | G4 | S |

### 3.4 Hardware level (`04-hardware/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-H-01](../04-hardware/WP-H-01-hardware-safety-requirements.md) | Hardware safety requirements specification | §10 | 5 §6 | | | | HWE.1 | G3 | S |
| [WP-H-02](../04-hardware/WP-H-02-hardware-design.md) | Hardware design (compute, safety monitor, sensors, drive-by-wire, power, network) | §10 | 5 §7 | | | | HWE.2 | G3 | S |
| [WP-H-03](../04-hardware/WP-H-03-hardware-safety-analysis-fmeda.md) | Hardware safety analysis (FMEA, FMEDA) | §10 | 5 §7, §8 | | | | HWE.2 | G3 | S |
| [WP-H-04](../04-hardware/WP-H-04-hardware-metrics.md) | Hardware architectural metrics (SPFM, LFM) | | 5 §8 | | | | | G3 | S |
| [WP-H-05](../04-hardware/WP-H-05-random-hardware-failures-pmhf.md) | Random hardware failures (PMHF) | | 5 §9 | | | | | G3 | S |
| [WP-H-06](../04-hardware/WP-H-06-hardware-integration-verification.md) | Hardware integration and verification | §12 | 5 §10 | | | | HWE.3, HWE.4 | G4 | S |
| [WP-H-07](../04-hardware/WP-H-07-hardware-element-evaluation.md) | Evaluation of hardware elements (compute, sensors, drive-by-wire kit) | §13 | 8 §13 | | | | | G3 | S |

### 3.5 Software level (`05-software/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-W-01](../05-software/WP-W-01-software-development-environment-guidelines.md) | Software development environment, languages and coding guidelines | §9 | 6 §5 | | §10 | | SWE.3 | G3 | S |
| [WP-W-02](../05-software/WP-W-02-software-safety-requirements.md) | Software safety requirements specification | §9 | 6 §6 | | | | SWE.1 | G3 | S |
| [WP-W-03](../05-software/WP-W-03-software-architecture.md) | Software architectural design (ROS 2 graph, executors, middleware) | §9 | 6 §7 | | | | SWE.2 | G3 | S |
| [WP-W-04](../05-software/WP-W-04-software-safety-analysis.md) | Software safety analysis and software-level DFA | §9 | 6 §7, 9 §7–8 | | | | SWE.2 | G3 | S |
| [WP-W-05](../05-software/WP-W-05-software-unit-design.md) | Software unit design and implementation | §9 | 6 §8 | | §10 | | SWE.3 | G3 | S |
| [WP-W-06](../05-software/WP-W-06-software-unit-verification.md) | Software unit verification | §12 | 6 §9 | | §10 | | SWE.4 | G3 | S |
| [WP-W-07](../05-software/WP-W-07-software-integration-verification.md) | Software integration and verification | §12 | 6 §10 | | | | SWE.5 | G4 | S |
| [WP-W-08](../05-software/WP-W-08-embedded-software-testing.md) | Testing of the embedded software | §12 | 6 §11 | | | | SWE.6 | G4 | S |
| [WP-W-09](../05-software/WP-W-09-configuration-calibration-data.md) | Safety-related configuration and calibration data (parameters, vehicle description) | §11 | 6 Annex C | | | | SWE.3 | G3 | S |
| [WP-W-10](../05-software/WP-W-10-ml-engineering.md) | ML engineering: data, training, testing and deployment of models | §8, §11 | | §7, §10 | | Data, AI V&V | MLE.1–4, SUP.11 | G3 | S |
| [WP-W-11](../05-software/WP-W-11-cybersecurity-implementation-verification.md) | Cybersecurity implementation and verification | §11 | | | §10 | | SEC.2, SEC.3 | G3 | S |
| [WP-W-12](../05-software/WP-W-12-hd-map-data.md) | HD map data (Lanelet2 and point cloud): requirements, production, verification | §11 | 6 Annex C | §7 | | | SUP.8 | G3 | S |

### 3.6 Validation (`06-validation/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-V-01](../06-validation/WP-V-01-safety-validation.md) | Safety validation plan, specification and report | §12 | 4 §8 | | | | VAL.1 | G5 | S |
| [WP-V-02](../06-validation/WP-V-02-sotif-vv-strategy.md) | SOTIF verification and validation strategy, validation targets | §12 | | §9 | | AI V&V | VAL.1 | G2 | S |
| [WP-V-03](../06-validation/WP-V-03-sotif-known-scenarios.md) | Evaluation of known hazardous scenarios | §12 | | §10 | | | SYS.5, VAL.1 | G4 | S |
| [WP-V-04](../06-validation/WP-V-04-sotif-unknown-scenarios.md) | Evaluation of unknown hazardous scenarios | §12 | | §11 | | | VAL.1 | G5 | S |
| [WP-V-05](../06-validation/WP-V-05-fault-injection.md) | Fault injection test specification and report | §12 | 4 §7, 5 §10, 6 §10–11 | | | | SYS.4, SWE.6 | G4 | S |
| [WP-V-06](../06-validation/WP-V-06-cybersecurity-validation.md) | Cybersecurity validation and penetration testing | §11 | | | §11 | | SEC.4 | G5 | S |
| [WP-V-07](../06-validation/WP-V-07-test-operations.md) | Test operations: safety drivers, remote supervisors, test sites | §12, §14 | 4 §8 | §10–11 | | | VAL.1 | G1 | S |
| [WP-V-08](../06-validation/WP-V-08-simulation-credibility.md) | Simulation credibility and scenario coverage | §12, §13 | 8 §11 | §9 | | AI V&V | VAL.1 | G2 | S |

### 3.7 Supporting processes (`07-supporting/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-P-01](../07-supporting/WP-P-01-configuration-management-plan.md) | Configuration management plan (baselines, `.repos` pins, safety-relevant paths) | §14 | 8 §7 | | §5 | | SUP.8 | G0 | S |
| [WP-P-02](../07-supporting/WP-P-02-change-management.md) | Change management plan | §14 | 8 §8 | | §6 | | SUP.10 | G0 | S |
| [WP-P-03](../07-supporting/WP-P-03-problem-resolution.md) | Problem resolution management | §14 | 2 §5 | §13 | §8 | | SUP.9 | G0 | S |
| [WP-P-04](../07-supporting/WP-P-04-documentation-management.md) | Documentation management | §5 | 8 §10 | | §5 | | | G0 | S |
| [WP-P-05](../07-supporting/WP-P-05-verification-review-procedure.md) | Verification and review procedure | §12 | 8 §9 | | | | | G0 | S |
| [WP-P-06](../07-supporting/WP-P-06-requirements-management-traceability.md) | Requirements management and traceability procedure | §9 | 8 §6 | | | | SYS.2, SWE.1 | G0 | S |
| [WP-P-07](../07-supporting/WP-P-07-tool-classification-qualification.md) | Software tool classification and qualification (including simulators) | §13 | 8 §11 | | §5 | Tool confidence | | G3 | S |
| [WP-P-08](../07-supporting/WP-P-08-software-component-qualification.md) | Software components not developed to ISO 26262 (Autoware packages, ROS 2, middleware, OS) | §13 | 8 §12, §16 | | §6 | | | G3 | S |
| [WP-P-09](../07-supporting/WP-P-09-proven-in-use.md) | Proven-in-use argument evaluation | §13 | 8 §14 | | | | | G3 | S |
| [WP-P-10](../07-supporting/WP-P-10-release-management.md) | Release management and baseline procedure | §14 | 2 §6, 8 §7 | | §6 | | SUP.8 | G5 | S |

### 3.8 Safety analyses (`08-analyses/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-A-01](../08-analyses/WP-A-01-asil-decomposition.md) | ASIL decomposition rationale | §10 | 9 §5 | | | | | G2 | S |
| [WP-A-02](../08-analyses/WP-A-02-coexistence-freedom-from-interference.md) | Coexistence of elements and freedom from interference | §10 | 9 §6 | | | | | G2 | S |
| [WP-A-03](../08-analyses/WP-A-03-dependent-failure-analysis.md) | Dependent failure analysis | §10 | 9 §7 | | | | | G2 | S |
| [WP-A-04](../08-analyses/WP-A-04-system-fta-fmea.md) | System-level safety analyses (FTA, FMEA) | §6, §10 | 9 §8, 4 §6 | §7 | | Safety analysis of AI | | G2 | S |
| [WP-A-05](../08-analyses/WP-A-05-stpa.md) | System-theoretic process analysis (STPA) | §6 | 9 §8 | §6–7 | | | | G2 | D |

### 3.9 Production, operation and decommissioning (`09-production-operation/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-O-01](../09-production-operation/WP-O-01-production-installation-provisioning.md) | Production, installation and provisioning control | §14 | 7 §5–6 | | §12 | | | G5 | S |
| [WP-O-02](../09-production-operation/WP-O-02-operation-service-decommissioning.md) | Fleet operation, service, sensor calibration and decommissioning | §14, §15 | 7 §7 | | §13, §14 | | | G5 | S |
| [WP-O-03](../09-production-operation/WP-O-03-user-information.md) | Information for passengers, fleet operators and first responders | §7 | 7 §5 | §13 | | | | G5 | S |
| [WP-O-04](../09-production-operation/WP-O-04-field-monitoring.md) | Field monitoring and incident reporting | §16 | 2 §7 | §13 | §8 | Measures during operation | | G6 | S |
| [WP-O-05](../09-production-operation/WP-O-05-cybersecurity-incident-response-updates.md) | Cybersecurity incident response, vulnerability management and updates | §11, §15 | | | §8, §13 | | SEC.* | G6 | S |
| [WP-O-06](../09-production-operation/WP-O-06-safety-performance-indicators.md) | Safety performance indicators (definition and monitoring) | §16 | | §13 | | Measures during operation | MAN.6 | G2 (definition), G6 (monitoring) | S |

### 3.10 Assurance cases and release (`10-safety-case/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-K-01](../10-safety-case/WP-K-01-safety-case.md) | Safety case (integrated UL 4600 argument over FuSa, SOTIF, AI and cybersecurity) | §5 | 2 §6 | §12 | | Assurance argument | | G1→G5 (living) | S |
| [WP-K-02](../10-safety-case/WP-K-02-sotif-release-argument.md) | SOTIF achievement evaluation and release recommendation | §5 | | §12 | | | | G5 | S |
| [WP-K-03](../10-safety-case/WP-K-03-cybersecurity-case.md) | Cybersecurity case | §11 | | | §6 | | | G5 | S |
| [WP-K-04](../10-safety-case/WP-K-04-functional-safety-assessment.md) | Functional safety assessment report (I3) | §17 | 2 §6 | | | | | G5 | S |
| [WP-K-05](../10-safety-case/WP-K-05-cybersecurity-assessment.md) | Cybersecurity assessment report | | | | §6 | | | G5 | S |
| [WP-K-06](../10-safety-case/WP-K-06-release-record.md) | Release for driverless operation (release record) | §5 | 2 §6 | §12 | §6 | | SUP.8 | G5 | S |
| [WP-K-07](../10-safety-case/WP-K-07-ul4600-assessment.md) | UL 4600 independent assessment report | §17 | | | | | | G5 | S |

### 3.11 Traceability (`trace/`)

| ID | Work product | UL 4600 | ISO 26262 | ISO 21448 | ISO/SAE 21434 | ISO/PAS 8800 | ASPICE | Gate | Status |
|---|---|---|---|---|---|---|---|---|---|
| [WP-T-01](../trace/README.md) | Requirements and trace data (machine-readable), consistency evidence | §5, §9 | 8 §6 | | §10 | | SYS.2–5, SWE.1–6 (traceability) | G1→G5 | S |

## 4. Work products the standards define that are covered elsewhere

| Standard work product | Where it is covered |
|---|---|
| Safety goals (ISO 26262-3 §6) | [WP-C-03](../02-concept/WP-C-03-hara.md) |
| Safety case (UL 4600 §5, ISO 26262-2 §6) | [WP-K-01](../10-safety-case/WP-K-01-safety-case.md), with its records in [`case/`](../case/README.md) |
| Verification review reports | Pull request reviews and `*/reviews/RR-yyyy-nnn.md` records, per [WP-P-05](../07-supporting/WP-P-05-verification-review-procedure.md) |
| Confirmation review reports, functional safety audit | Records under `10-safety-case/confirmation/`, created per [WP-M-06](WP-M-06-confirmation-measures-plan.md) |
| Decisions of the safety authority | [Decision register](decisions/README.md); once applied, recorded in the work product that owns the item |
| Cybersecurity claims (ISO/SAE 21434 §9.4) | [WP-C-10](../02-concept/WP-C-10-cybersecurity-goals-and-concept.md) |
| Vulnerability analysis and management (ISO/SAE 21434 §8) | [WP-O-05](../09-production-operation/WP-O-05-cybersecurity-incident-response-updates.md) |

## 5. Not applicable

| Standard part | Rationale |
|---|---|
| ISO 26262-12 (motorcycles) | The item is not fitted to a motorcycle |
| ISO 26262-10 | Informative guideline; it requires no work products |
| ISO 26262-11 (semiconductors) as a source of work products | Informative; used as input to WP-H-07 |

Whether ISO 26262 applies in full depends on the vehicle chosen (decision register DQ-003): ISO 26262 covers series-production road vehicles, and a purpose-built low-speed shuttle may sit outside its scope. The project applies it either way, as the method for the functional safety argument inside the UL 4600 case ([WP-M-01 §4](WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together)).

## 6. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Confirm each clause reference against licensed copies of the standards before an audit | G0 |
| OI-2 | Re-check the register once the item, monitor architecture and vehicle are decided (DQ-001 to DQ-003): some work products may be tailored out or split | G0 |
