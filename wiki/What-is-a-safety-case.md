A safety case is a structured argument, backed by evidence, that a system is acceptably safe for a stated use in a
stated environment. It is what this project is building towards. This page explains the idea and how the project
keeps its safety case; the case itself is [WP-K-01](../assurance/10-safety-case/WP-K-01-safety-case.md) with its
records in [`assurance/case/`](../assurance/case/README.md).

## Claims, evidence and defeaters

A safety case has three kinds of content:

- **Claims** say what is asserted, from a top-level claim ("the system is acceptably safe in its ODD") down to
  claims narrow enough to be shown directly. Each claim is supported by sub-claims or by evidence.
- **Evidence** is what supports a claim: an analysis, a test result, a review record. Evidence is only as good as
  the review that accepted it.
- **Defeaters** are known reasons a claim or an evidence item may not hold: counter-evidence, a gap in an argument,
  an assumption nobody has checked. An open defeater blocks the claim it is against.

UL 4600 asks for this structure and for the case to cover the whole ODD and lifecycle, including the system's own
failures, its fallback, the people around it, its data, its tools and its operation in the field
([WP-M-01 §4](../assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together)).

## Why this project needs one

There is no driver. The vehicle must notice its own failures and the limits of what it can perceive and do, and
reach a minimal risk condition by itself. Standards written for vehicles with a driver do not argue that on their
own; a safety case that covers the whole ODD does, using their methods as evidence.

The proposed top-level claim, G0, is in
[WP-M-01 §3.2](../assurance/01-management/WP-M-01-assurance-strategy.md#32-top-level-claim-proposed). Its
acceptance criterion is for the safety authority to set, and is still an open item of WP-M-01.

## How the records are kept

Claims (`CL-nnn`), evidence (`EV-nnn`) and defeaters (`DF-nnn`) are YAML records in
[`assurance/case/records/`](../assurance/case/records), not prose. [`validate.py`](../assurance/case/tools/validate.py)
enforces the rules in [`case/README.md` §3](../assurance/case/README.md#3-rules); among them:

- a claim is `accepted` only when a recorded review accepts it, every evidence item it cites is accepted, it has
  evidence or sub-claims, and no defeater against it is open;
- an evidence item is `accepted` only with a recorded review, and it names a work product in the register;
- a closed defeater says what closed it.

A passing CI run, a passing test, or the existence of a document never accepts a claim on its own. Work drafted by
the AI assistant is at independence level I0 and is never the review that accepts a claim or evidence.

## Where the case stands

The [case README](../assurance/case/README.md#1-files) keeps the record lists empty until the item, the command
bound and the vehicle are decided: a claim written before then would argue about a system nobody has chosen. The
current counts of claims, evidence and open defeaters are on the dashboard, computed from these files
([Reading the assurance status](Reading-the-assurance-status.md)).

## How the rest of the work feeds it

![Doer and checker architecture: sensors, Autoware and the independent safety monitor in the item, the drive-by-wire outside it, each with its rating from WP-C-04; below, the concept work products with their status in the register, all feeding the UL 4600 safety case.](../tools/readme/figures/architecture.svg)

*Ratings from WP-C-04, statuses from WP-M-00; drawn by [`figures.py`](../tools/readme/figures.py).*

The hazard analysis ([WP-C-03](../assurance/02-concept/WP-C-03-hara.md)) finds what can go wrong and sets safety
goals; the functional safety concept ([WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md)) says
how each goal is met and by which element; later work products refine and verify that down to hardware and
software. Each of those, once reviewed and accepted, becomes evidence that a claim of the case can cite. The SOTIF
and cybersecurity arguments have cases of their own
([WP-K-02](../assurance/10-safety-case/WP-K-02-sotif-release-argument.md),
[WP-K-03](../assurance/10-safety-case/WP-K-03-cybersecurity-case.md)), and an independent UL 4600 assessment
([WP-K-07](../assurance/10-safety-case/WP-K-07-ul4600-assessment.md)) checks the whole.

The safety goals the hazard analysis sets; the work products after it show how each is met:

![The nine safety goals: one small scene of the robotaxi per safety goal of WP-C-03, drawn as the situation going wrong (unintended acceleration, braking too little, unintended hard braking, drifting out of the planned path, moving off from standstill, entering against right of way, failing to reach a minimal risk condition, acting on stale remote commands, signalling the wrong manoeuvre), each with its ASIL and safe state.](../tools/readme/figures/safety-goals.svg)

*Illustration. Labels read from the work products by [`figures.py`](../tools/readme/figures.py); vehicle models CC BY 4.0, see [credits](../tools/readme/models/CREDITS.md).*
