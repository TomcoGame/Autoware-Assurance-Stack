A guide for a reviewer or assessor of this project's assurance work. No assessor is named yet: the question was
deferred (DQ-004) and is asked again as DQ-007 before the HARA confirmation review
([WP-M-01 §8](../assurance/01-management/WP-M-01-assurance-strategy.md#8-strategic-decisions)).

> [!IMPORTANT]
> Everything here is a draft. Nothing has passed verification review, confirmation review or assessment. Much of
> the drafting is done by an AI assistant; its output is at independence level I0 and counts for nothing until a
> human reviewer at the required level has verified it
> ([WP-M-01 §9](../assurance/01-management/WP-M-01-assurance-strategy.md#9-ai-authored-work)).

## Where to start

| To check | Read |
|---|---|
| What is claimed, for which configuration | [WP-M-01 §3](../assurance/01-management/WP-M-01-assurance-strategy.md#3-what-the-project-will-claim) |
| How the standards are combined, and why UL 4600 leads | [WP-M-01 §4](../assurance/01-management/WP-M-01-assurance-strategy.md#4-how-the-standards-fit-together) |
| Every work product, its clauses, gate and status | [WP-M-00 §3](../assurance/01-management/WP-M-00-work-product-register.md#3-register) |
| What is tailored out or covered elsewhere | [WP-M-00 §4 and §5](../assurance/01-management/WP-M-00-work-product-register.md#4-work-products-the-standards-define-that-are-covered-elsewhere), [WP-M-01 §5](../assurance/01-management/WP-M-01-assurance-strategy.md#5-tailoring) |
| Every decision of the safety authority, with its options and sources | [`register.yaml`](../assurance/01-management/decisions/register.yaml), and the decisions as recorded in [WP-M-01 §8](../assurance/01-management/WP-M-01-assurance-strategy.md#8-strategic-decisions) |
| The concept phase | [WP-C-01](../assurance/02-concept/WP-C-01-item-definition.md) item definition, [WP-C-02](../assurance/02-concept/WP-C-02-odd-and-intended-functionality.md) ODD, [WP-C-03](../assurance/02-concept/WP-C-03-hara.md) HARA, [WP-C-04](../assurance/02-concept/WP-C-04-functional-safety-concept.md) FSC |
| The safety case records and their rules | [`assurance/case/`](../assurance/case/README.md) |

## How to trace a value to its source

- **Ratings and ASILs** are not typed. They are kept in [`hara.yaml`](../assurance/02-concept/hara/hara.yaml);
  [`hara.py`](../assurance/02-concept/hara/hara.py) computes each ASIL and writes the tables of WP-C-03. The
  functional safety requirements and element ASILs come from [`fsc.yaml`](../assurance/02-concept/fsc/fsc.yaml)
  through [`fsc.py`](../assurance/02-concept/fsc/fsc.py).
- **Status** is the `Status` field of each work product's header, which must match its register row
  ([`check_headers.py`](../assurance/trace/tools/check_headers.py)).
- **Decisions** are cited by identifier and option (for example "DQ-016 A"). Each register entry names the commit or
  pull request that applied it and where it is recorded.
- **Upstream software** is identified by the versions pinned in
  [`repositories/autoware.repos`](../repositories/autoware.repos) and the fork point named in each header's
  `Baseline` field.
- **History** is the git history: each change to the assurance work reaches `main` as a merged pull request.

## What the checks prove, and what they do not

CI ([`assurance.yaml`](../.github/workflows/assurance.yaml)) checks that the decision register follows its
lifecycle, that the case records follow their rules, that headers agree with the register, that links and tables are
sound, that every generated output matches its source, and that the tools pass their unit tests
([`assurance/tests/`](../assurance/tests/test_tools.py)). That is consistency, not correctness: CI cannot tell
whether a rating is right, a hazard is missing, or an assumption holds. Those are for review.

## Known limits of the current state

- The standards are not reproduced here. Clause references must be checked against licensed copies before an audit
  ([WP-M-00 OI-1](../assurance/01-management/WP-M-00-work-product-register.md#6-open-items)).
- The vehicle and drive-by-wire platform are not chosen (DQ-003 C). Values that depend on them are marked
  provisional until G2.
- The safety monitor does not exist yet; the concept describes what it must do.
- Upstream Autoware was not developed to these standards and has no safety case of its own.
- Open items are listed at the end of each work product.
