# The wiki source

This folder is the source of the repository's GitHub wiki. Pages are written and reviewed here by pull request;
the [wiki workflow](../.github/workflows/wiki.yaml) checks them on every pull request and, on every push to
`main`, builds them with [`tools/wiki/build_wiki.py`](../tools/wiki/build_wiki.py) and pushes the result to the
wiki repository. An edit made on the wiki itself is overwritten by the next push to `main`.

This file describes the folder and is not published.

## What the wiki is for

Orientation: what the project is, how the repository is laid out, how decisions are made, what the identifiers
and terms mean, how to read the status. The wiki explains and links. It is not a work product: no page has a
document control header, counts as evidence, or states a hazard, requirement, rating or decision on its own
authority. Where a page needs one, it links to the record in [`assurance/`](../assurance/README.md) that owns it.

## Writing a page

- One page per file, named `Title-With-Hyphens.md`. The wiki shows the name with spaces for hyphens.
- Every page is linked from [`_Sidebar.md`](_Sidebar.md); the build fails otherwise.
- Link to another page as `[Glossary](Glossary.md)`, so the link also works when this folder is read on GitHub.
  The build turns it into `Glossary`.
- Link to a repository file or folder relative to this folder, as `[assurance/](../assurance/README.md)`. The build
  turns it into an absolute link on `main` and fails if the path, or the `#anchor` in a Markdown target, does not
  exist.
- Embed only images that already exist in the repository, as `![alt](../path/to/figure.svg)`, with alt text that
  says what the figure shows and a caption that names its generator. Do not draw figures for the wiki.
- Do not type a value the repository holds (a count, a status, an ASIL, a version). Link to its source, or use a
  placeholder that the build fills in:

| Placeholder | Becomes |
|---|---|
| `{{GENERATED:<path>:<name>}}` | The body of the block `<!-- BEGIN GENERATED: <name> (...) -->` in `<path>`, for example `{{GENERATED:assurance/README.md:assurance-summary}}` |
| `{{PIN:<key>}}` | The version [`repositories/autoware.repos`](../repositories/autoware.repos) pins for `<key>`, for example `{{PIN:universe/autoware_universe}}` |
| `{{REPO}}`, `{{BRANCH}}`, `{{SYNC_COMMIT}}`, `{{SYNC_DATE}}` | Where and when the pages were built; used by the sync stamp in [`_Footer.md`](_Footer.md) |

Placeholders are filled on the wiki, not when this folder is read on GitHub. A placeholder inside a code span or a
fenced code block is left as it is.

Check before opening a pull request:

```sh
python3 -m unittest discover -s tools/wiki -p 'test_*.py'
python3 tools/wiki/build_wiki.py --check
python3 tools/wiki/build_wiki.py --out build/wiki   # to look at the result
```

## One-time setup

GitHub creates the wiki repository (`<owner>/<repo>.wiki.git`) only when a first page is saved from the
repository's **Wiki** tab. Until then the publish job of the workflow fails at "Clone the wiki" and says so. Any
first page will do; the first sync replaces it.
