# WP-M-09 Cybersecurity plan

| Field | Value |
|---|---|
| Work product | WP-M-09 Cybersecurity plan |
| Standard reference | ISO/SAE 21434 §6; ASPICE 4.0 MAN.7 |
| Version | 0.2 (§4 handling of cybersecurity information: what may be published in this public repository; 2026-10-25). 0.1 (skeleton: structure and clause mapping; 2026-10-22) |
| Status | Skeleton |
| ASIL / scope | CS |
| Author | Claude (AI assistant; I0 per WP-M-02) |
| Reviewer(s) | TBD |
| Approver | Safety authority (to be named, decision register DQ-004) |
| Baseline | Upstream Autoware `ed48f39` (fork point) |

## 1. Purpose

How ISO/SAE 21434 activities are planned and run, including the remote operations link and over-the-air updates.

Needed at gate G0 ([WP-M-00](../01-management/WP-M-00-work-product-register.md)).

## 2. Cybersecurity scope and item

To be written.

## 3. Activities per ISO/SAE 21434 Clauses 9–15

To be written.

## 4. Handling of cybersecurity information

This repository is public. A cybersecurity work product here may publish what helps a reader understand and review the approach, but not what would help an attacker. Everything else is restricted: it is kept outside this repository, where only the people who need it can read it.

| May be published here | Restricted: never in this repository, its issues, pull requests, wiki, commit messages or CI logs |
|---|---|
| The method: standards, rating scales, the risk matrix and CAL table as the standards give them | Attack paths and attack trees |
| Assets and the cybersecurity properties that matter for each | Attack feasibility ratings and attack potential factors per threat |
| Damage scenarios and their impact ratings | Risk values per threat, and the attack vector of each |
| Threat scenarios named at the level of published research | The rationale for retaining a risk (what makes an attack hard) |
| The treatment of each threat (reduce or retain) and the decisions behind it | Design detail: the text of technical cybersecurity requirements, trust zones, conduits, exposed interfaces, key management, network topology, open ports and services, cryptographic parameters, debug access |
| Cybersecurity goals, their CALs, claims by identifier, concept-level requirements and controls, and the trace and CAL of technical requirements | Vulnerability analysis, penetration test and fuzzing plans and findings, known weaknesses, incident records |
| That an activity was done, by whom, and its overall outcome | Keys, certificates, credentials and any other secret |

How it is enforced:

- **Mark restricted material.** A restricted file carries the line `classification: restricted` (in YAML, or in an HTML comment in Markdown). Keep it in a folder named `restricted/` or name it `*.restricted.*`; git ignores both, so it stays on your machine.
- **The checks refuse it.** [`check_restricted.py`](../trace/tools/check_restricted.py) runs in CI on every pull request and refuses a marked or restricted-named file, key material, and a Markdown table with an attack path, attack potential, feasibility, risk value or attack vector column. The TARA and cybersecurity generators ([`tara.py`](../02-concept/tara/tara.py), [`cybersecurity.py`](../02-concept/cybersecurity/cybersecurity.py)) refuse restricted fields in their models.
- **Report vulnerabilities privately.** A vulnerability in the item or in this fork is reported through GitHub's private vulnerability reporting for this repository, never in a public issue.
- **When restricted information is published by mistake,** remove it from the tree, then from history, and tell the safety authority; treat a published secret as compromised and replace it.

The restricted tier of the TARA, the cybersecurity concept and the security architecture (WP-C-09, WP-C-10, WP-S-07), and the README figure that placed risk values on the vehicle, were removed from this repository and from its history on 2026-10-25. They are held outside it until a controlled store is chosen (OI-2).

## 5. Reuse and off-the-shelf components (Autoware, ROS 2, DDS, OS)

To be written.

## 6. Distributed activities with suppliers

To be written.

## 7. Cybersecurity case and assessment plan

To be written.

## 8. Open items

| ID | Open item | Closes at |
|---|---|---|
| OI-1 | Write this work product | G0 |
| OI-2 | Choose the controlled store for restricted cybersecurity information and who may read it | G1 |
