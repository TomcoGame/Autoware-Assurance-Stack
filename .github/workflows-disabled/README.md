# Upstream workflows turned off in this fork

GitHub runs only the files in `.github/workflows/`. The upstream Autoware workflows below do not apply to this
fork, so they were moved here unchanged. Moving keeps their content, so an upstream sync still merges cleanly
into them, and any one can be turned back on by moving it back.

| Workflow | Why it is off |
|---|---|
| `backport.yaml`, `comment-on-pr.yaml`, `semantic-pull-request.yaml` | Upstream pull request conventions; run on `pull_request_target` with write tokens, which this fork does not need |
| `bump-repo-versions-autoware.yaml`, `bump-repo-versions-simulator.yaml`, `bump-repo-versions-tools.yaml`, `regenerate-lockfiles.yaml` | Move the `.repos` pins and lockfiles automatically. Here a pin moves only through change management with an impact analysis (WP-P-02, WP-M-12) |
| `cleanup-actions-caches.yaml`, `cleanup-autoware-buildcache.yaml`, `keep-build-cache-small.yaml` | Maintain upstream's shared build caches |
| `dco.yaml` | Upstream's Developer Certificate of Origin policy for contributions to the Autoware Foundation |
| `docker-build-and-push.yaml`, `docker-build-pipeline.yaml`, `docker-build.yaml`, `docker-manifest.yaml`, `github-release.yaml` | Publish upstream's images and releases. Releases of this fork follow WP-P-10 |
| `health-check.yaml` | Upstream's scheduled and post-merge build of every configuration. Pull requests that touch the build are still checked by `health-check-pr.yaml` |
| `health-check-ansible-artifacts.yaml` | Needs the upstream `HF_TOKEN` secret |
| `mirror-main-branch.yaml`, `sync-files.yaml` | Mirror and template sync for the upstream organisation; `sync-files` would overwrite this fork's changes to synced files such as `.prettierignore` |
| `pre-commit.yaml` | Needs the upstream GitHub App secrets (`APP_ID`, `PRIVATE_KEY`) to push autofixes |
| `spell-check-daily.yaml`, `spell-check-differential.yaml` | Use the Autoware dictionaries, which lack assurance terms; off until the assurance tree has its own word list (decision register DQ-006) |

Still running: `health-check-pr.yaml` with `health-check-reusable.yaml` and `health-check-ansible.yaml` (build checks
when the build inputs change, on the `run:health-check` label), `validate-lockfiles.yaml`, `pre-commit-optional.yaml`,
`pre-commit-ansible.yaml`, and this fork's own `assurance.yaml`.

## Abbreviations, terms and symbols

| Term | Meaning |
|---|---|
| ansible | Automation tool that installs and configures software from scripts called roles and playbooks; this repository uses it to set up machines and images |
| assurance | The safety-assurance work in this fork: the documents and evidence that show the system is acceptably safe |
| assurance tree | The `assurance/` folder that holds the assurance documents |
| autofix | A change a tool makes on its own to fix a problem it found, such as formatting |
| Autoware | The open-source self-driving software stack this fork is based on |
| Autoware Foundation | The non-profit organisation that runs the upstream Autoware project |
| backport | Copying a fix to an older release branch |
| build cache | Saved results of earlier builds, reused to make later builds faster |
| change management | The controlled process for proposing, assessing and approving changes |
| DCO | Developer Certificate of Origin: a statement each contributor signs on their commits that they have the right to submit the work |
| decision register | Where questions for the safety authority are asked and answered |
| dictionary | The list of accepted words the spell check uses |
| Docker | Software that builds images and runs them as isolated containers |
| DQ-006 | Decision register question 6: whether the spell check stays off until the assurance tree has its own word list |
| fork | A copy of another repository that is developed separately; this repository is a fork of upstream Autoware |
| GitHub App | An automated account on GitHub with its own permissions, used here by upstream to push autofixes |
| health check | A build of the Autoware configurations to check they still work |
| `HF_TOKEN` | A Hugging Face access token, used by upstream to download files from Hugging Face |
| image | A packaged, read-only snapshot of an operating system plus installed software, from which containers are started |
| impact analysis | An assessment of what a change could affect before it is made |
| label | A tag on a GitHub pull request; adding `run:health-check` starts the health check |
| lockfile | A file that records the exact version of every package to install, so builds can be repeated |
| manifest | The list that ties images for different processor types to one image name |
| mirror | Keeping a copy of a branch in step with another |
| organisation | A GitHub account shared by a group, here the Autoware Foundation's |
| pin | A fixed, exact version of a dependency |
| post-merge | After a change is merged into the main branch |
| pre-commit | A tool that runs checks such as formatting and linting on changed files |
| `.prettierignore` | The list of files that the Prettier formatter must leave alone |
| pull request | A proposed change on GitHub, reviewed before it is merged |
| `pull_request_target` | A GitHub trigger that runs a workflow for a pull request with the target repository's permissions and secrets |
| release | A published, numbered version of the software |
| `.repos` | Files that list the source repositories and the exact versions to clone |
| secret | A password or key stored in GitHub settings for workflows to use |
| semantic pull request | A check that pull request titles follow a fixed naming convention |
| spell check | An automatic check for spelling mistakes |
| template sync | Automatic copying of shared files from a template repository |
| token | A key that gives a program permission to act on GitHub |
| upstream | The original Autoware repository this fork was copied from |
| upstream sync | Bringing the latest upstream changes into this fork |
| workflow | An automated job that GitHub Actions runs on events such as a push or pull request, defined in a YAML file |
| work product | A document or record the assurance path needs |
| WP-M-12 | Work product M-12: the reuse and impact analysis |
| WP-P-02 | Work product P-02: change management |
| WP-P-10 | Work product P-10: release management |
| write token | A token that lets a workflow change the repository |
| YAML | A plain-text format for configuration files (`.yaml`) |

Other project terms are defined in the [Glossary](../../wiki/Glossary.md).
