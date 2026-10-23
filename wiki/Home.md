This wiki explains the **Autoware Assurance Stack**: the assurance work for a driverless urban robotaxi built on
[Autoware](https://github.com/autowarefoundation/autoware), kept in a fork of the Autoware repository. The fork
leaves the upstream content as it is and adds the assurance work products in
[`assurance/`](../assurance/README.md) and the checks that run on them.

> [!WARNING]
> Everything in this project is a **draft prepared for engineering review**. Nothing is certified, assessed or
> approved for driverless operation, and no work product has passed verification review, confirmation review or
> assessment. A document existing does not mean the activity behind it is done. Do not use anything here to put a
> vehicle on the road.

## What the project is

- **The system.** A geofenced urban robotaxi: driverless passenger transport on public urban roads inside a mapped
  geofence, with a remote operations centre. The reference configuration and the decisions behind it are in
  [WP-M-01 §3.1](../assurance/01-management/WP-M-01-assurance-strategy.md#31-reference-configuration).
- **The software.** Upstream Autoware, unmodified, at the versions pinned in
  [`repositories/autoware.repos`](../repositories/autoware.repos). Autoware was not developed to the safety
  standards below and has no safety case; this project has to argue for it
  ([WP-M-01 §2](../assurance/01-management/WP-M-01-assurance-strategy.md#2-starting-point)).
- **The safety architecture.** An independent safety monitor on its own hardware, between Autoware and the
  drive-by-wire system, checks every command and can stop the vehicle on its own; Autoware stays QM
  ([WP-M-01 §6](../assurance/01-management/WP-M-01-assurance-strategy.md#6-safety-architecture-argument)).
- **The framework.** UL 4600 is the main framework because there is no driver to fall back on. ISO 26262,
  ISO 21448, ISO/SAE 21434, ISO/PAS 8800 and Automotive SPICE 4.0 supply the methods and evidence. See
  [Standards at a glance](Standards-at-a-glance.md).

## Status

![Assurance dashboard: the assurance state, work products by status and by gate, decisions waiting on the safety authority, and the safety case records. The same values are in the table below.](../assurance/case/figures/dashboard.svg)

*Generated from the work-product register, the decision register and the safety case records by
[`dashboard.py`](../assurance/case/tools/dashboard.py). How to read it: [Reading the assurance status](Reading-the-assurance-status.md).*

{{GENERATED:assurance/README.md:assurance-summary}}

## Where to start

| If you want to | Read |
|---|---|
| Find your way around the files | [How the repository is organized](How-the-repository-is-organized.md) |
| Understand what the project is building towards | [What is a safety case?](What-is-a-safety-case.md) |
| See which standard does what | [Standards at a glance](Standards-at-a-glance.md) |
| Know who decides what, and how a question is asked | [How decisions are made](How-decisions-are-made.md) |
| Look up an identifier or a term | [Glossary](Glossary.md) |
| Change something | [Contributor guide](Contributor-guide.md) |
| Review or assess the work | [For the assessor](For-the-assessor.md) |

The work products themselves start at [`assurance/README.md`](../assurance/README.md), the
[work-product register (WP-M-00)](../assurance/01-management/WP-M-00-work-product-register.md) and the
[assurance strategy (WP-M-01)](../assurance/01-management/WP-M-01-assurance-strategy.md).
