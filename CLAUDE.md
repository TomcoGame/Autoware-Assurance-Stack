# Working on this repository

This is a fork of `autowarefoundation/autoware` that carries the assurance stack for a driverless system built on
Autoware. The upstream content is left as it is; the fork's own work lives in [`assurance/`](assurance/README.md),
its CI in [`.github/workflows/assurance.yaml`](.github/workflows/assurance.yaml). UL 4600 is the main framework,
because there is no driver to fall back on.

## Working with the project lead

The project lead is the safety authority until decision DQ-004 names one, and often reviews from a phone. Ask them
few questions, and make each one quick to answer.

- **Every question goes in the [decision register](assurance/01-management/decisions/README.md).** Ask only what
  the lead alone can decide: risk acceptance, ASIL and hazard scope, ODD limits, vehicle behaviour defaults, money
  and hardware, roles, the assessor, gate go/no-go. A reversible technical choice is `decider: claude`: take the
  recommendation and say so. A task is not a decision; it stays in its work product.
- **Every question stands on its own.** Plain words, what is at stake, two to four options with what each does and
  costs, the recommendation first, how hard it is to undo, what it blocks, its sources; one figure when a picture
  shows the difference between the options.
- **About ten open at a time,** in numbered batches, those that unblock the most first.
- **At the start of a session,** read the inbox page's `answers` and `explain` collections, copy them into the
  register, and answer requests for explanation before asking anything new.
- **In chat,** name a question by its words, not its ID. Ask in chat only when blocked right now: multiple choice,
  recommendation first, then record it with `via: chat`.

## Rules for assurance work

- Work on a branch and ask before merging. Do not start the hazard analysis until the lead says so (DQ-005).
- Your drafts are I0. Never mark your own work Approved, accept evidence or claims, close defeaters or pass gates.
- Never lower an ASIL, change a timing budget or loosen a safety limit to make a finding go away.
- Keep proposals, evidence and accepted conclusions apart. Do not invent clauses, measurements, reviews or results.
- Every generated output has a generator with `--check`, and CI runs it. Edit the source (a table, a register,
  a record), run the generator, commit both. The generators are listed in
  [assurance/README.md](assurance/README.md#generated-content).
- Before pushing, run what CI runs:

```sh
python3 -m pip install --user -r assurance/requirements.txt
python3 assurance/01-management/decisions/check_decisions.py
python3 assurance/case/tools/validate.py
python3 assurance/trace/tools/check_headers.py && python3 assurance/trace/tools/check_links.py && python3 assurance/trace/tools/check_tables.py
for g in assurance/01-management/figures/fig_m00_register.py assurance/01-management/figures/folder_index.py \
         assurance/01-management/decisions/fig_lifecycle.py assurance/01-management/decisions/fig_questions.py \
         assurance/02-concept/figures/fig_c01_boundary.py assurance/02-concept/hara/hara.py \
         assurance/02-concept/fsc/fsc.py \
         assurance/case/tools/dashboard.py; do python3 "$g" --check; done
python3 -m unittest discover -s assurance/tests -p 'test_*.py'
```

- Python in `assurance/` uses the standard library and PyYAML only, formatted with black and isort at line length
  100 as the rest of the repository.
