Six frameworks shape the work. UL 4600 is the main one; the others supply methods and evidence for parts of the
argument. The project's own account of how they fit is
[WP-M-01 §4](../assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together); this page
summarises it.

> [!NOTE]
> The standards are copyrighted and are not reproduced in this repository. Clause references in the work products
> point to the editions below and must be checked against a licensed copy before an audit
> ([`assurance/README.md`](../assurance/README.md#standards-text)).

## The six frameworks

| Framework | Edition used | The question it answers here | Main work products |
|---|---|---|---|
| UL 4600 | 3rd edition | Is there a complete, convincing argument that the driverless system is acceptably safe across its ODD and lifecycle? | [WP-K-01](../assurance/10-safety-case/WP-K-01-safety-case.md), [WP-K-07](../assurance/10-safety-case/WP-K-07-ul4600-assessment.md), [WP-O-06](../assurance/09-production-operation/WP-O-06-safety-performance-indicators.md) |
| ISO 26262 | 2018 | What harm can malfunctions cause, how much integrity (ASIL) does preventing it need, and how is that met? | [WP-C-03](../assurance/02-concept/WP-C-03-hara.md), [WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md), `03-system/` to `05-software/` |
| ISO 21448 (SOTIF) | 2022 | What harm can the intended function cause when it works as designed but not well enough, for example a perception limit? | [WP-C-05](../assurance/02-concept/WP-C-05-sotif-hazard-identification.md) to [WP-C-07](../assurance/02-concept/WP-C-07-sotif-functional-modifications.md), [WP-V-02](../assurance/06-validation/WP-V-02-sotif-vv-strategy.md) to [WP-V-04](../assurance/06-validation/WP-V-04-sotif-unknown-scenarios.md) |
| ISO/SAE 21434 | 2021 | What can an attacker do, including over the remote operations link and over-the-air updates, and how is it prevented? | [WP-M-09](../assurance/01-management/WP-M-09-cybersecurity-plan.md), [WP-C-09](../assurance/02-concept/WP-C-09-tara.md), [WP-C-10](../assurance/02-concept/WP-C-10-cybersecurity-goals-and-concept.md), [WP-S-07](../assurance/03-system/WP-S-07-cybersecurity-requirements-architecture.md) |
| ISO/PAS 8800 | 2024, cited by topic | Are the machine-learning components and their data safe enough for their role? | [WP-M-10](../assurance/01-management/WP-M-10-ai-safety-plan.md), [WP-C-11](../assurance/02-concept/WP-C-11-ai-system-definition-and-safety-requirements.md), [WP-W-10](../assurance/05-software/WP-W-10-ml-engineering.md) |
| Automotive SPICE | 4.0 | Are the engineering and support processes capable? | [WP-M-13](../assurance/01-management/WP-M-13-aspice-capability-baseline.md) |

Every work product lists the clauses it answers in its header, and the
[register (WP-M-00)](../assurance/01-management/WP-M-00-work-product-register.md#3-register) has one column per
framework.

## Why UL 4600 leads

ISO 26262 and ISO 21448 were written for vehicles with a driver, or a driver who can be asked to take over. Here
nobody takes over, so the vehicle must detect its own failures and performance limits and reach a minimal risk
condition by itself. UL 4600 is written for that case. It does not prescribe how to engineer the system; it
requires a safety case that covers the whole ODD and lifecycle, and accepts other standards as the means of
producing evidence ([WP-M-01 §4](../assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together)).

## Two consequences of having no driver

- **Controllability.** ISO 26262 rates how well the driver or others can avoid harm. With no driver, the safety
  authority decided that the hazard analysis credits no controllability: every hazardous event is rated C3
  ([WP-C-03 §3.3](../assurance/02-concept/WP-C-03-hara.md#33-controllability-without-a-driver)).
- **The ODD carries more weight.** Anything the vehicle cannot handle must be outside the ODD, or the vehicle must
  detect it and reach a minimal risk condition by itself
  ([WP-C-02 §1](../assurance/02-concept/WP-C-02-odd-and-intended-functionality.md#1-purpose)).

## Other references

Some work products also use informative references, named in their headers: ISO 34503 and SAE J3016 for ODD
taxonomy and terms in [WP-C-02](../assurance/02-concept/WP-C-02-odd-and-intended-functionality.md), and
IEEE 2846-2022 for assumptions in safety-related models in
[WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md).

## How the work is staged

The register groups the work products by gate, G0 (governance) to G6 (operation). The dashboard counts a gate as
passed only when every work product it needs is approved or baselined. The gates and their exit criteria are in
[WP-M-00 §2](../assurance/01-management/WP-M-00-work-product-register.md#2-gates).
