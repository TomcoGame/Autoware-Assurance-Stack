# Autoware Assurance Stack

[![assurance checks](https://github.com/TomcoGame/Autoware-Assurance-Stack/actions/workflows/assurance.yaml/badge.svg)](https://github.com/TomcoGame/Autoware-Assurance-Stack/actions/workflows/assurance.yaml)
[![README figures](https://github.com/TomcoGame/Autoware-Assurance-Stack/actions/workflows/readme.yaml/badge.svg)](https://github.com/TomcoGame/Autoware-Assurance-Stack/actions/workflows/readme.yaml)
[![wiki](https://github.com/TomcoGame/Autoware-Assurance-Stack/actions/workflows/wiki.yaml/badge.svg)](https://github.com/TomcoGame/Autoware-Assurance-Stack/wiki)
![status: draft for engineering review](https://img.shields.io/badge/status-draft%20for%20engineering%20review-d29922)
![framework: UL 4600](https://img.shields.io/badge/framework-UL%204600-2d55c8)
![built on: Autoware, Apache-2.0](https://img.shields.io/badge/built%20on-Autoware%20%C2%B7%20Apache--2.0-6e7781)

[![Concept illustration: a white robotaxi on Autoware approaches a crosswalk. Autoware's planned path is red; the independent safety monitor's envelope is blue and ends at a stop wall before a pedestrian. A parked minivan hides the kerb, and the ODD limits are shown along the bottom. Stamped: concept illustration, the safety monitor is not built yet, draft for engineering review.](tools/readme/figures/hero.svg)](tools/readme/figures/scene.svg)

_Concept illustration, not output of the system; select it for the full figure. Every label is read from the work
products and the decision register by [`tools/readme/figures.py`](tools/readme/figures.py), and CI fails if a figure
is stale. Vehicle models by Daniel Zhabotinsky and Comrade1280, CC BY 4.0, simplified and recoloured
([credits](tools/readme/models/CREDITS.md))._

The assurance work for a driverless urban robotaxi built on unmodified [Autoware](https://github.com/autowarefoundation/autoware).
This repository is a fork of `autowarefoundation/autoware`: the upstream content is left as it is, and the fork adds
the assurance work products in [`assurance/`](assurance/README.md) and the checks that run on them.

UL 4600 is the main framework, because there is no driver to fall back on: the vehicle has to detect its own failures
and limits and reach a minimal risk condition by itself, and the safety case has to argue that across the whole
operational design domain. ISO 26262, ISO 21448 (SOTIF), ISO/SAE 21434, ISO/PAS 8800 and Automotive SPICE 4.0
supply the methods and evidence ([WP-M-01 §4](assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together)).

> [!WARNING]
> Everything in this repository's assurance work is a **draft prepared for engineering review**. Nothing is
> certified, assessed or approved for driverless operation. No work product has passed verification review,
> confirmation review or assessment, and a document existing here does not mean the activity behind it is done.
> Much of the drafting is done by an AI assistant at independence level I0, which counts for nothing until a human
> reviewer has verified it. Do not use anything here to put a vehicle on the road.

## How the system is built

![Doer and checker architecture: sensors feed Autoware, whose commands pass through an independent safety monitor (not built yet) to the vehicle drive-by-wire; remote operations also pass through the monitor, which has its own sensors. Each element carries its rating from WP-C-04. Below, the concept work products with their status in the register.](tools/readme/figures/architecture.svg)

_Ratings from the functional safety concept ([WP-C-04 §4](assurance/02-concept/WP-C-04-functional-safety-concept.md#4-allocation-to-elements)),
statuses from the [register](assurance/01-management/WP-M-00-work-product-register.md); drawn by
[`figures.py`](tools/readme/figures.py)._

## How the standards fit

![Standards map: UL 4600 is the safety case; ISO 26262, ISO 21448, ISO/SAE 21434, ISO/PAS 8800 and Automotive SPICE 4.0 each feed evidence into it.](tools/readme/figures/standards.svg)

_From [WP-M-01 §4](assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together); the
questions are a plain-language summary._

## Assurance status

![Assurance dashboard: the assurance state, work products by status and by gate, decisions waiting on the safety authority, and the safety case records. The same values are listed as text in assurance/README.md.](assurance/case/figures/dashboard.svg)

_Generated from the work-product register, the decision register and the safety case records by
[`dashboard.py`](assurance/case/tools/dashboard.py); CI fails if it is stale. The same values as text are in
[`assurance/README.md`](assurance/README.md#status)._

| Start here                                                                                               | What it is                                                                                   |
| -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [`assurance/README.md`](assurance/README.md)                                                             | The assurance stack: layout, identifiers, document header, status meanings, generators       |
| [WP-M-00 Work-product register](assurance/01-management/WP-M-00-work-product-register.md)                | Every work product, the clauses it answers, the gate that needs it and its status            |
| [WP-M-01 Assurance strategy](assurance/01-management/WP-M-01-assurance-strategy.md)                      | What will be claimed and for which configuration, how the standards fit, the decisions taken |
| [WP-C-01 Item definition](assurance/02-concept/WP-C-01-item-definition.md)                               | The item: its functions, modes, boundary, interfaces and assumptions                         |
| [WP-C-02 ODD and intended functionality](assurance/02-concept/WP-C-02-odd-and-intended-functionality.md) | Where and when the vehicle may drive, what it must do there, and how it knows it has left    |
| [WP-C-03 HARA](assurance/02-concept/WP-C-03-hara.md)                                                     | Hazard analysis and risk assessment: hazardous events, ratings, safety goals and their ASILs |
| [WP-C-04 Functional safety concept](assurance/02-concept/WP-C-04-functional-safety-concept.md)           | How the safety goals are met: functional safety requirements and their allocation            |
| [Decision register](assurance/01-management/decisions/README.md)                                         | The questions only the safety authority can answer, and how they are asked and recorded      |

## Browse the hazard analysis

The HARA rates every malfunction of every function of the item in every operational situation and road condition:
5 400 rows, each with its severity, exposure and controllability, the reason for each, its ASIL and its safety goal.
Everything is on one page in [`assurance/02-concept/hara/`](assurance/02-concept/hara/): the item and its
functions, what each malfunction of each function leads to (a HAZOP sheet, and a scene for each safety-related one), every rated row,
one file per hazard that GitHub shows as a searchable table, the named hazardous events and the safety goals.
Nothing needs to be downloaded.

## Wiki

The [wiki](https://github.com/TomcoGame/Autoware-Assurance-Stack/wiki) explains the project for newcomers,
contributors and assessors: how the repository is organized, what a safety case is, the standards at a glance, how
decisions are made, how to read the status, and a glossary. Its pages are kept in [`wiki/`](wiki/README.md) and
published by the [wiki workflow](.github/workflows/wiki.yaml) on every push to `main`. The wiki explains and links;
it is not a work product.

## Upstream Autoware

The assurance work refers to Autoware as pinned in [`repositories/autoware.repos`](repositories/autoware.repos),
which fixes the version of each Autoware source repository. This repository holds no driving code itself; the
packages live in the repositories it pins. Each work product names the commit it refers to in the `Baseline` field
of its header.

To build and run Autoware, follow the upstream documentation:

- [Installation](https://autowarefoundation.github.io/autoware-documentation/main/installation)
- [Demos](https://autowarefoundation.github.io/autoware-documentation/main/demos/)
- [Autoware documentation](https://autowarefoundation.github.io/autoware-documentation/main/)

The Ansible and Docker tooling in [`ansible/`](ansible) and [`docker/`](docker) is upstream's, unchanged.

## Contributing

Work on a branch and open a pull request; the project lead decides what is merged. The rules for assurance work and
the checks to run before pushing are in [`CLAUDE.md`](CLAUDE.md), and the
[contributor guide](wiki/Contributor-guide.md) collects them. Changes to Autoware itself belong upstream; see
[Autoware's contribution guidelines](https://autowarefoundation.github.io/autoware-documentation/main/contributing/).

## Credit and licence

Autoware is developed by [The Autoware Foundation](https://www.autoware.org/) and its contributors and is licensed
under the Apache License 2.0. This repository carries Autoware's [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) and
[`DISCLAIMER.md`](DISCLAIMER.md) unchanged.

The vehicles in the README figures are rendered from ["Kiri '10 - Low poly model"](https://sketchfab.com/3d-models/kiri-10-low-poly-model-7fd6e15785fa4aa9bfd6e31eb7c97ba6)
by Daniel Zhabotinsky and ["Generic passenger car pack"](https://sketchfab.com/3d-models/generic-passenger-car-pack-20f9af9b8a404d5cb022ac6fe87f21f5)
by Comrade1280, both licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). They are simplified,
recoloured and partly removed; the changes are listed in [`CREDITS.md`](tools/readme/models/CREDITS.md).

## Abbreviations, terms and symbols

| Term                     | Meaning                                                                                                                                              |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| AI                       | Artificial intelligence; here the AI assistant that drafts much of the work, and the machine-learned models in Autoware                              |
| Apache-2.0               | Apache License 2.0, the open-source licence of Autoware                                                                                              |
| ASIL                     | Automotive Safety Integrity Level, A (lowest) to D (highest), set by ISO 26262 for each safety goal                                                  |
| Automotive SPICE 4.0     | Automotive Software Process Improvement and Capability dEtermination, version 4.0: a model for rating how capable the development process is         |
| CC BY 4.0                | Creative Commons Attribution 4.0: the licence of the vehicle models, which requires crediting their authors                                          |
| CI                       | Continuous integration: the automated checks GitHub runs on every pull request and push                                                              |
| Drive-by-wire            | The vehicle's electronic interface for steering, braking and propulsion commands                                                                     |
| Fork                     | A copy of another repository that adds its own work; here of `autowarefoundation/autoware`                                                           |
| HARA                     | Hazard analysis and risk assessment: finds the hazards, rates them and sets the safety goals                                                         |
| I0                       | Independence level 0: no review by anyone independent of the author yet                                                                              |
| ISO, ISO/SAE, ISO/PAS    | International Organization for Standardization; a standard published jointly with SAE International; a Publicly Available Specification              |
| Item                     | The system the safety work is about: the sensors, Autoware on its computer and the safety monitor                                                    |
| Minimal risk condition   | A stable, stopped state the vehicle reaches by itself when it can no longer drive safely                                                             |
| ODD                      | Operational design domain: the roads, conditions and traffic the system is designed for                                                              |
| Robotaxi                 | A taxi with no driver on board                                                                                                                       |
| Safety authority         | Who accepts risk and decides the questions of the decision register; the project lead until one is named                                             |
| Safety case              | A structured argument, with evidence, that the system is acceptably safe                                                                             |
| Safety monitor           | The independent controller between Autoware and the vehicle that checks every command and can stop the vehicle on its own (not built yet)            |
| SOTIF                    | Safety of the intended functionality (ISO 21448): harm from a function working as designed but not well enough                                       |
| UL 4600                  | The standard for the safety of autonomous products, from UL Standards & Engagement; the main framework here                                          |
| WP                       | Work product: a document or record the assurance path needs, as in WP-C-03. The letter is its area (M management, C concept)                         |
| Badges (top of the page) | The first three show whether the assurance checks, the README figures and the wiki build pass on `main` (green) or fail (red); the others are labels |
| `Baseline`               | The header field of a work product naming the Autoware commit it refers to                                                                           |
| WARNING box              | A GitHub callout that marks a warning to read before anything else                                                                                   |
| §                        | Section, as in "WP-M-01 §4"                                                                                                                          |

Every identifier and more terms are defined in the [Glossary](wiki/Glossary.md).
