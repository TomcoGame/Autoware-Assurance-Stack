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
