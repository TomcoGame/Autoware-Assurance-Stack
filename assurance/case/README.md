# Safety case records

The safety case ([WP-K-01](../10-safety-case/WP-K-01-safety-case.md)) argues, in the structure UL 4600 §5 asks
for, that the driverless system is acceptably safe in its ODD. Its claims, the evidence for each, and the known
counter-evidence against them are kept here as records, so that the status shown on the
[dashboard](../README.md#status) is computed and never typed.

## 1. Files

| File | Holds |
|---|---|
| [`records/claims.yaml`](records/claims.yaml) | Claims `CL-nnn`: what the case asserts, arranged as a tree by `parent` |
| [`records/evidence.yaml`](records/evidence.yaml) | Evidence items `EV-nnn`: what supports a claim, and the work product that holds it |
| [`records/defeaters.yaml`](records/defeaters.yaml) | Defeaters `DF-nnn`: known reasons a claim or an evidence item may not hold |
| [`tools/validate.py`](tools/validate.py) | Checks the records against §3 |
| [`tools/dashboard.py`](tools/dashboard.py) | Draws `figures/dashboard.svg` and the summary block of `assurance/README.md` |

All three lists are empty until the item, the command bound and the vehicle are decided (decision register DQ-001 to
DQ-003): a claim written before then would argue about a system nobody has chosen.

## 2. Fields

| Record | Field | Meaning |
|---|---|---|
| Claim | `id`, `statement`, `status` | `status` is `proposed`, `supported`, `accepted` or `withdrawn` |
| Claim | `parent` | The claim this one supports; none for the top-level claim |
| Claim | `evidence` | Evidence items cited directly |
| Claim | `ul4600` | The UL 4600 clauses the claim answers |
| Claim | `review` | The review record that accepted it |
| Evidence | `id`, `title`, `status`, `work_product` | `status` is `missing`, `drafted`, `available` or `accepted`; `work_product` is a WP-M-00 ID |
| Evidence | `review` | The review record that accepted it |
| Defeater | `id`, `statement`, `against`, `status` | `against` is a claim or evidence ID; `status` is `open` or `closed` |
| Defeater | `closed_by` | What closed it: a change, an analysis or an argument, with its reference |

## 3. Rules

`validate.py` refuses records that break these rules, and CI runs it on every pull request:

- Identifiers are unique, well formed and never reused; every reference resolves.
- The claim tree has no loops.
- A claim is `accepted` only when a recorded review accepts it, every evidence item it cites is `accepted`, it has
  evidence or sub-claims, and no defeater against it is open.
- An evidence item is `accepted` only with a recorded review, and it names a work product that exists in WP-M-00.
- A closed defeater says what closed it.

A passing CI run, a passing test, or the existence of a document never accepts a claim on its own. Work drafted by an
AI assistant is I0 and is never the review that accepts a claim or evidence.

## 4. Dashboard

`dashboard.py` reads the WP-M-00 register, the decision register and these records. A gate counts as passed only when
every work product it needs is approved or baselined. The figure and the text block are written together, so they
cannot disagree; `--check` fails when either is stale.
