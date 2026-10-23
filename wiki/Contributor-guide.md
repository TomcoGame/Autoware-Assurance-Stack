How to change something in this repository. The binding rules are in [`CLAUDE.md`](../CLAUDE.md) and
[`assurance/README.md`](../assurance/README.md#conventions); this page collects them in the order you meet them.

## Before you start

- **Leave upstream content alone.** The fork's own work lives in [`assurance/`](../assurance/README.md), in its CI
  ([`assurance.yaml`](../.github/workflows/assurance.yaml)), and in the wiki ([`wiki/`](../wiki/README.md),
  [`tools/wiki/`](../tools/wiki/build_wiki.py), [`wiki.yaml`](../.github/workflows/wiki.yaml)). Changes to Autoware
  itself belong upstream.
- **Work on a branch** and open a pull request. The project lead decides whether it is merged.
- **Check whether it is a decision.** If the change needs a call only the safety authority can make (risk
  acceptance, ASIL or hazard scope, ODD limits, vehicle behaviour defaults, money or hardware, roles, the assessor,
  gate go/no-go), it goes to the [decision register](../assurance/01-management/decisions/README.md) first. See
  [How decisions are made](How-decisions-are-made.md).

## Changing a work product

1. **Edit the source, not the output.** If the content is generated (a table, figure or summary between
   `BEGIN GENERATED` and `END GENERATED` markers), find its generator in the
   [list of generators](../assurance/README.md#generated-content), edit the source it reads, and run it.
2. **Update the header.** Add a line to `Version` saying what changed and why, with the date and the decision it
   applies if any. If the status changes, change the register row in
   [WP-M-00](../assurance/01-management/WP-M-00-work-product-register.md) too.
3. **Keep proposals, evidence and accepted conclusions apart.** A value not yet decided is marked as proposed; a
   value that depends on the vehicle is marked provisional. Do not invent clauses, measurements, reviews or results.
4. **Never lower an ASIL, change a timing budget or loosen a safety limit to make a finding go away.**
5. **Commit the source and the generated output together.**

Work drafted by the AI assistant is at independence level I0. It is never marked Approved by its author, and it
never accepts evidence or claims, closes defeaters or passes gates.

## Checks to run before pushing

The same checks run in CI on every pull request that touches `assurance/`. The authoritative list is in
[`CLAUDE.md`](../CLAUDE.md); at the time of writing it is:

```sh
python3 -m pip install --user -r assurance/requirements.txt
python3 assurance/01-management/decisions/check_decisions.py
python3 assurance/case/tools/validate.py
python3 assurance/trace/tools/check_headers.py && python3 assurance/trace/tools/check_links.py && python3 assurance/trace/tools/check_tables.py
# every generator listed in assurance/README.md, with --check
python3 -m unittest discover -s assurance/tests -p 'test_*.py'
```

When a generator's `--check` fails, run it without `--check` and commit what it writes.

## Changing the wiki

Pages are in [`wiki/`](../wiki/README.md), one file per page. The folder README says how to link pages and
repository files and which placeholders the build fills in (for example `{{GENERATED:...}}` for a generated
summary and `{{PIN:...}}` for a pinned version), so that no page types a value the repository holds. Check with:

```sh
python3 -m unittest discover -s tools/wiki -p 'test_*.py'
python3 tools/wiki/build_wiki.py --check
```

The [wiki workflow](../.github/workflows/wiki.yaml) runs the same on every pull request, so moving a file that a
page links to fails before merge. On every push to `main` it publishes the pages to the wiki. Do not edit the wiki
in place; the next sync overwrites it.

## Style

- Plain, direct language. Say what is known, what is proposed and what is open.
- Python in `assurance/` and `tools/` uses the standard library and PyYAML only, formatted with black and isort at
  line length 100, as the rest of the repository ([`setup.cfg`](../setup.cfg)).
- Pull request titles follow conventional commits, for example `feat(assurance): ...` or `docs: ...`. Fill in the
  [pull request template](../.github/pull_request_template.md).
