# Autoware Assurance Stack

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
