# Pre-review audit: scenario scenes in Blender (tools/sim)

| Field | Value |
|---|---|
| Item audited | [`tools/sim/`](README.md) (scene descriptions, Blender builder, review dashboards, gallery), the workflows [`sim.yaml`](../../.github/workflows/sim.yaml) and [`sim-render.yaml`](../../.github/workflows/sim-render.yaml), the added section of [`tools/readme/models/CREDITS.md`](../readme/models/CREDITS.md) and the added line of `CLAUDE.md` |
| Baseline | First round: `4295f6b` on `origin/main` `310b1be`, fixed in `a9dc860`. Second round (picture quality): `a9dc860`, fixed in the commit after it (pull request #57) |
| Review type | Pre-review audit (author-side self-check), in the form of the LionDriver review records. **Not** a verification review: WP-P-05 (verification and review procedure) is still a skeleton, and this record does not count as one |
| Checklist | The brief of the task (below, C-01 to C-14) and the rules of `CLAUDE.md` |
| Date | 2026-10-25 |
| Author of the item | Claude Code (AI assistant) |
| Auditors and independence | Claude Code, the author: **I0**. A second Claude Code agent that had no part in writing the tool, given the code and the brief but not the author's conclusions: also **I0** (the same AI system, no human). This record accepts nothing and approves nothing; the project lead decides |

## Checklist

FC fully met, PC partly met, NO not met.

| # | Requirement (brief, `CLAUDE.md`) | Result | Evidence |
|---|---|---|---|
| C-01 | Find out whether Blender runs here; do not fake renders | FC | `bpy` 5.2.3 from PyPI runs headless with Cycles on the CPU; the dashboards in [`dashboards/`](dashboards/README.md) were rendered by it, and their manifests record the version |
| C-02 | A tool that turns a scenario into a Blender scene: road layout, the ego and the other road users placed from the scenario's parameters, Autoware's planned path and the monitor's envelope, ODD conditions | FC | Five scenes (SC-01, SC-02, SC-03, SC-06, SC-14); `--verify` checks the road users' positions and the conditions and features drawn (F-09) |
| C-03 | A sample inside the stated ranges, chosen deterministically | FC | `test_samples_lie_inside_the_stated_ranges`, `test_the_draw_is_deterministic`, `test_each_parameter_has_its_own_draw`, `test_ego_speed_never_above_the_posted_limit` (F-02, F-03) |
| C-04 | Every label and number read from the records, never typed | FC | [README, where the labels come from](README.md#where-the-labels-come-from); `test_labels_come_from_the_records`. The envelope legend's "vehicle not chosen" is now tied to DQ-008 (F-12). Panel headings and filmstrip captions describe the picture, not the item |
| C-05 | Motion is a qualitative illustration; every render stamped; never presented as V&V evidence | FC | The stamp is checked on every dashboard and clip by `--verify` (`test_a_missing_stamp_fails`); the gallery and README open with the warning; road users are tagged *qualitative* |
| C-06 | No invented measurements, results or reviews | FC after fixes | The clip's speed contradicted the sampled speed (F-01, fixed); the weather wording overstated (F-06, fixed); a typed render time (F-13, reworded). No metric panel: gap, time to collision and speed traces would be made up |
| C-07 | Standard library and PyYAML only, plus `bpy` inside Blender; black and isort at 100 | FC | No other import; the dashboard is laid out in Blender, not with an imaging library; black and isort clean |
| C-08 | A generator with `--check` that CI runs; the check of non-deterministic renders designed and written down | FC | `scene.py --check` in `sim.yaml` on every pull request and push to main; [README, how the check works](README.md#how-the-check-works). Its limit is written down (F-09) |
| C-09 | Do not edit `assurance/` | FC | `git diff origin/main --stat -- assurance/` is empty |
| C-10 | Keep the models' CC BY credit; record further changes | FC | Credit on the face of every dashboard and clip, checked by `--verify` (F-10); changes in [CREDITS.md](../readme/models/CREDITS.md#changes-made-in-the-blender-scenes) |
| C-11 | Do not render or describe attack paths, threat details or security architecture | FC | Scenarios on the remote link or a cybersecurity requirement are refused, derived from the records (F-11); `check_restricted.py` passes |
| C-12 | Work is I0; a branch and a pull request, never merged by the author | FC | Pull request #57, open for the lead to decide; this record claims nothing |
| C-13 | Run what `CLAUDE.md` lists, the tests and `--check` before pushing | FC | Results below |
| C-14 | As the LionDriver hazard scenes: a review dashboard per scene, a gallery, an audit | FC | [dashboards/README.md](dashboards/README.md); this record. Deliberate differences: no metric or chart panels (nothing computed to plot), the dashboard is composed in Blender (no Pillow here), and road users are tagged *qualitative* from the start, as the lead directed for new projects |

## Findings

Severity: Major = must be fixed before the lead reviews; Minor = fix or carry as a tracked item; Note = no action
needed, or the lead's call. F-01 to F-16 are the second agent's findings on `4295f6b`, each checked by the author
before it was fixed; F-17 to F-22 are the author's, F-19 to F-22 from reading the full renders of the dashboards.

| # | Location | Description | Severity | Disposition |
|---|---|---|---|---|
| F-01 | `layouts.py` docstring; `build_blend.py` motion | The clip ignored the sampled ego speed: the ego covered its path in a fixed share of 6 s, so the speed seen in the clip contradicted the one printed on it (SC-01: about 24 km/h against 40.1) | Major | **Fixed:** the clip's length is chosen so that the ego cruises at the sampled speed (`clip_seconds`); `test_the_clip_runs_at_the_sampled_speed` |
| F-02 | `scene.py` `sample()` | "One draw per parameter" was false: draws were shared, so a pick or a changed range moved other parameters' values | Minor | **Fixed:** one generator per parameter, seeded from the salt, the scenario and the parameter; `test_each_parameter_has_its_own_draw`. The sampled values of the five scenes changed with it |
| F-03 | `scene.py` | The ego speed was not capped by the sampled posted limit (ODD-20 `capped_by: ODD-03`); latent today | Minor | **Fixed:** `cap()`; `test_ego_speed_never_above_the_posted_limit` |
| F-04 | `layouts.py` SC-06 (and SC-01) | The ego's front stopped past the stop line it is meant to stop before. The author found SC-01 did the same | Minor | **Fixed:** both paths shortened; `test_the_ego_stops_before_its_stop_line` |
| F-05 | `build_blend.py` rain | Rain was drawn denser beyond the ODD limit even when only visibility crosses it | Minor | **Fixed:** checked against the crossing attributes, as mist already was |
| F-06 | `README.md` | "Proportional" rain (it is affine) and mist that "looks like" 200 m visibility (an uncalibrated shader) overstated | Minor | **Fixed:** reworded |
| F-07 | Legend | The ODD-limit curtain and the occlusion area had no legend line; SC-14's legend named an amber road user it does not have | Minor | **Fixed:** legend lines come from the description, only for what is drawn; `test_legend_lines_only_for_what_is_drawn` |
| F-08 | `layouts.py` SC-02 | The hazard area lay in the ego lane while its label is HE-04.3, steering onto the sidewalk | Minor | **Fixed:** the area spans the lane, the parking strip and the sidewalk where the child emerges |
| F-09 | `build_blend.py` `verify()` | The position check is circular (the same functions make and check the motion), and conditions, features, plan and hazard were not checked | Minor | **Partly fixed:** the conditions and features drawn are recorded and compared (`test_a_condition_not_drawn_fails`). The circularity is inherent and is written down in the README; choreography is covered by unit tests and by review |
| F-10 | `verify()` | The credits, the pass criterion and the monitors were not checked on the frame; overflowing text was not caught | Minor | **Fixed** for the labels (`test_a_missing_credit_on_the_clip_fails`). The dashboard's panels fit their text by shrinking it, and `test_the_dashboard_stays_on_its_canvas` checks the bounds. **Open:** the clip's overlay is not checked for overflow (it uses an estimated glyph width) |
| F-11 | `test_sim.py` | The security exclusion was a typed list (SC-20, SC-21, SC-26); SC-24 and SC-25 also rest on the remote link | Minor | **Fixed:** `restricted()` derives it from the records (ODD-15 `link-*`, `CSR-` references) and `scene.py` refuses a layout for one; it now also excludes SC-24 and SC-25 |
| F-12 | `scene.py` envelope legend | "The vehicle is not chosen" was typed and would go stale when DQ-008 is answered | Minor | **Fixed:** the legend names DQ-008, and `scene.py` fails once DQ-008 is applied |
| F-13 | `README.md` | A render time stated as a measurement | Note | **Fixed:** stated as rough, for the container it was seen in |
| F-14 | `layouts.py` SC-06 | A stop line was drawn whatever the sampled junction type (it suggests stop control at a T-junction) | Note | **Fixed:** a sampled `no_stop_line` feature for unprotected turns and T-junctions |
| F-15 | `sim-render.yaml` | The render job runs only on some pull requests and on demand; nothing said whether it is required | Note | **Fixed:** the README says it is advisory |
| F-16 | `assurance/README.md` | `scene.py` is not in the generator list that `CLAUDE.md` points to (neither is `tools/readme/figures.py`) | Note | **Open, the lead's call:** that list is in `assurance/`, which this change does not edit; `CLAUDE.md` lists the check |
| F-17 | `build_blend.py` dashboard | Text widths are estimated (0.52 em) for wrapping, the header chips and the tags, so a long label could overrun its box | Note | **Open:** bounds are tested on the canvas; read the dashboards when a label grows |
| F-18 | Design | The first version kept renders out of the repository. Following LionDriver, the dashboards are now committed, outside the byte check, with their state on the gallery page | Note | **Changed in this change:** see [README, how the check works](README.md#how-the-check-works) |
| F-19 | Dashboard footer | On SC-14 the last legend line ran off the right edge; the canvas test checked heights only | Minor | **Fixed:** a legend line that would not fit starts a new row; the test also checks the right edge |
| F-20 | Dashboard header | SC-14's condition (four attributes) wrapped to three lines and touched the chase view | Minor | **Fixed:** a wider condition column, and a smaller size when it needs more than two lines |
| F-21 | Motion (after F-01) | With the cruise at the sampled speed, the fixed slowing share of the clip made SC-02 stop from 42.7 km/h in about 6.5 m (over 1 g): a picture of an impossible stop | Major | **Fixed:** the ego slows at the firm level of FSR-03.02 (3 m/s², DQ-019 A, DQ-033 A), read from `fsc.yaml`, and its start is placed far enough back for that stop; the dashboard says the slowing is choreography, not Autoware's planned braking. `test_the_ego_slows_at_the_level_the_records_state` |
| F-22 | Dashboard header | The goal chips stopped silently when they ran out of room (SC-14 showed three of its four goals) and could run into the first header field (SC-03) | Minor | **Fixed:** the chips stop before the header fields, and a last chip counts the goals not shown; every goal is also listed in the right panel. `test_goal_chips_fit_or_say_how_many_are_left` |

## Second round: picture quality against LionDriver (2026-10-25)

The lead asked why the graphics look lower in resolution than LionDriver's. Same form: the finding, measured, then
fixed in this change.

**How it was measured.** Resolution was not the cause: the dashboards are 1920 × 1080, LionDriver's 1600 × 900. Fine
detail was measured as the variance of the Laplacian of the grey image (×10⁴; higher means more fine detail), over the
inner part of the 3D view, clear of the tags (ours x 534 to 1282, y 112 to 512; LionDriver's x 420 to 1132, y 94 to
494), on the committed JPEGs. The same measure on the raw chase render before compositing gave 31, against 45 for the
same region of the dashboard, so the loss was in the 3D scene and its render, not in the compositing.

| Dashboard | Fine detail of the 3D view |
|---|---|
| LionDriver `sh-11-pedestrian-occluded` | 193 |
| LionDriver `he-01-2-hardover-adjacent` | 144 |
| LionDriver `he-03-2-queue-pedestrian` | 157 |
| SC-02 at `a9dc860` (flat colours, rendered at panel size) | 89 |
| SC-02, procedural look, rendered at 1.5× and scaled down | 194 |
| SC-02, CC0 look, rendered at 1.5× and scaled down | 245 |

The committed dashboards, before (`a9dc860`) and after this change (32 samples, CC0 look), same region:

| Scene | Before | After |
|---|---|---|
| SC-01 (night, rain) | 84 | 218 |
| SC-02 (day) | 89 | 246 |
| SC-03 (wet, rain) | 70 | 207 |
| SC-06 (dusk) | 61 | 180 |
| SC-14 (dusk, rain and mist past the ODD limit) | 40 | 101 |

SC-14 stays lowest because its mist hides detail, as it should.

| # | Location | Description | Severity | Disposition |
|---|---|---|---|---|
| F-23 | `build_blend.py` materials, world, render | The 3D views carried roughly half LionDriver's fine detail: every surface was one flat colour, the sky a flat colour, the buildings plain boxes, the pedestrians primitives, and the views rendered at their size on the dashboard with no supersampling. LionDriver uses CC0 HDRIs, scanned PBR textures and street furniture (Poly Haven, ambientCG), CC0 pedestrians, CC-BY building kits, and renders its chase view larger than its panel | Major | **Fixed:** [`fetch_assets.py`](fetch_assets.py) fetches the CC0 skies, asphalt, concrete, grass, three facades, a street tree, bins and hydrants (the IDs LionDriver chose and checked, plus the facades), pinned by SHA-256 in [`assets.lock.json`](assets.lock.json); [`look.py`](look.py) draws with them, with a textured procedural fallback; the Quaternius pedestrians walk; views render at 1.5× and are box-filtered down. Table above |
| F-24 | `build_blend.py` dashboard | The compositing pass drew the views pixel on pixel through Cycles' default 1.5 px filter, softening them and the text | Minor | **Fixed:** views box-filtered to their exact size, sampled nearest, and a 0.5 px filter; the text panels' fine detail doubled (SC-02 left panel 1258 to 2368) |
| F-25 | `look.py` pedestrians | The Quaternius file carries a helper icosphere, which landed at the origin as a white ball in the lane (seen in the top view and the filmstrip of the first render) | Minor | **Fixed:** only the rig and the meshes under it are kept |
| F-26 | `look.py` procedural facade | Without the assets, the facades showed vertical stripes: the brick pattern read the wrong axes on vertical walls | Minor | **Fixed:** the pattern runs along the wall and up it |
| F-27 | Buildings | LionDriver's urban buildings are CC-BY kits in its private assets repository; they are not this project's to use, so the buildings here are boxes with CC0 facade textures, plainer than LionDriver's | Note | **Open, the lead's call:** licensing kits for this repository, or keeping the textured boxes |
| F-28 | Road users | Cyclists, scooter riders, wheelchair users, buses, trucks and motorcycles are still primitives; only pedestrians and children use the CC0 figures | Note | **Open:** no CC0 models for them were chosen in this change |
| F-29 | `sim-render.yaml` | The CI render fetches the assets at run time from two third-party sites; if they are unreachable it renders the procedural look | Note | **By design:** the lock pins every file by SHA-256, the manifest records which assets a dashboard used, and the gallery shows the look of each committed dashboard |

## Third round: overlays that stand in front of the scene (2026-10-25)

The lead asked what the boxes in front of the vehicle are. They were overlays drawn for the analysis, and three of
them read as solid objects standing in the scene, hiding what is behind them. LionDriver's renderer has the rule this
broke ("the ghosts and the path read from above; from the road they block the view", `hazard_scene.py`): in its
road-level views only flat marks on the road are drawn.

| # | Location | Description | Severity | Disposition |
|---|---|---|---|---|
| F-30 | `build_blend.py` envelope | The safety monitor's envelope was a translucent slab ending in a 0.9 m wall. Glowing, it rendered as a white box in front of the vehicle in the chase and forward views, hiding the road and what the scene is about; nothing on the frame said what the box was | Major | **Fixed:** the envelope is a flat blue outline on the road with a faint fill; its far edge moves with it as it shortens |
| F-31 | `build_blend.py` ODD limit | The ODD limit (SC-14) was a violet panel 7 m high and 60 m wide across the street, hiding everything beyond it | Major | **Fixed:** a flat violet band across the carriageway at the limit; the denser rain and mist beyond it still show the change |
| F-32 | `build_blend.py` hazard area | The hazard area was a glowing orange slab, opaque enough to read as an object on the road | Minor | **Fixed:** an orange outline with a light fill |
| F-33 | `verify()` | Nothing checked that overlays stay on the road, so all three got through the first two rounds | Minor | **Fixed:** the manifest records the highest point of every overlay at the still frame, and `--verify` fails above OVERLAY_TOP_M (0.25 m, a sidewalk's height); `test_an_overlay_standing_up_fails` |
| F-34 | Review | The first two rounds checked labels, positions, motion and picture detail, but not whether the overlays were legible to someone seeing the frames cold. The question came from the lead, not from the audit | Note | **Applied in this round:** each dashboard was read as a first-time reviewer would; F-35 is what that found. Carried as a check for later rounds |
| F-35 | Dashboard legend | The dashed green path and the green ring had no legend line on the dashboard (only the green "Meant to do" heading hinted at them) | Minor | **Fixed:** a legend line from the description says what both mean; the footer is re-spaced for it, and `test_footer_lines_do_not_overlap` checks it |
| F-36 | `sim-render.yaml` | The step added in round 2 to fetch the assets had an unquoted `run:` value containing ": ", which is not valid YAML. GitHub could not parse the workflow, so from `bd2bba6` on every render run failed at once and its check vanished from the pull request; the author then reported the job as "probably still queued" instead of looking | Major | **Fixed:** the step is a block scalar; `test_the_sim_workflows_parse` loads both sim workflows. The committed dashboards were rendered and verified locally, so they are unaffected; the CI render is re-checked on the push that carries this fix |

## Fourth round: every drawable scenario, and condition variants (2026-10-26)

The lead asked for more scenarios, as in LionDriver. This round adds a scene for each of the 16 scenarios that had
none and may be drawn (SC-04, SC-05, SC-07 to SC-13, SC-15 to SC-19, SC-22, SC-23) and 13 condition variants in
LionDriver's style (`SC-13--unlit`, `SC-05--low-sun`, ...): 34 scenes in all. SC-20, SC-21 and SC-24 to SC-26 stay
undrawn (F-11). To draw them, the builder gained lanes, a cycle lane, a roundabout, lit signal states, all-way stop
signs, cones, a barrier and work sign, steam, debris, a marked stopping place, a bus stop, a traffic paddle, the
ego's indicators and hazard lights, a door that opens, an emergency vehicle's light bar and an object lying in the
lane. The render in CI is now one job per scene.

The audit followed the earlier rounds: a second agent reviewed the code and layouts against the brief without the
author's conclusions (F-37 to F-50), and the author read every dashboard cold (F-51 onwards). Before that review,
the author's own new overlap test had already caught three drawn collisions (F-52).

| # | Location | Description | Severity | Disposition |
|---|---|---|---|---|
| F-37 | SC-22 layout, `lights_from()` | The left indicator stayed lit for the whole clip, also after the lane change, while the ego drove straight. The pass criterion is that the indicator always matches the steering direction, so the scene showed the failure it is about; a test locked the behaviour in | Major | **Fixed:** an indicator can be lit over a stretch of the path (`lights_m`); SC-22's goes off once the lane change ends; `test_the_indicator_matches_the_steering` |
| F-38 | SC-12 layout | The sample picked ODD-04 `t-junction`, and the dashboard said so, but no junction was drawn | Major | **Fixed:** a T-junction on the left beyond the pull-over |
| F-39 | README, choreography | The README said the paths imply a pace fit for each kind of road user; nothing checked it, and some did not (an oncoming car at 50 km/h in congested SC-03, two pedestrians at a run in SC-16) | Minor | **Fixed:** SC-03's car and SC-16's clip changed; the sentence now says it is checked by reading the dashboards, not by a test, and is no claim about speed |
| F-40 | SC-17 layout | The car passing the stopped vehicle drove the wrong way up the oncoming lane for 100 m | Minor | **Fixed:** it waits behind the ego, pulls out round it and back in; the clip holds longer so that it can pass at a road pace |
| F-41 | SC-08 layout | The main view showed the cyclist already past the junction | Minor | **Fixed:** the still is when the cyclist is alongside |
| F-42 | `build_blend.py` `drawn` | A prop of an unknown kind and a road user lying in the lane counted as drawn without being built | Minor | **Fixed:** an unknown prop stops the build; lying objects are recorded as they are built |
| F-43 | Ego lights | The lights are steady, not flashing | Minor | **Kept, said:** a still must show them on; the README says steady |
| F-44 | `test_no_two_road_users_overlap` | Props and the open door were outside the overlap test | Minor | **Fixed:** cones, barrier, debris, signs and the door's swept box are in it (steam is not solid, a paddle is held) |
| F-45 | `scene.py` / `build_blend.py` | "Stands throughout" meant one path point in one file and no speed in the other; a seeded speed of 0 would have split them | Minor | **Fixed:** both mean one path point, and `scene.py` refuses a drawn speed of 0 on a path |
| F-46 | `test_a_variant_pick_outside_the_scenario_is_refused` | The test reached its refusal by a roundabout route and never built a layout holding a bad variant | Minor | **Fixed:** it builds layouts whose variant picks a value outside the scenario and an attribute that is not a parameter |
| F-47 | `moments()` | Labels within 0.05 of the main view were merged away, so five filmstrips never showed "vehicle stands still", where the pass criterion is judged | Minor | **Fixed:** one thumbnail names both ("vehicle stands still; main view"); a test checks every stopping scene shows its stop |
| F-48 | `sim-render.yaml` | A job whose verify failed uploaded nothing, losing the manifest that says why | Minor | **Fixed:** the upload runs always |
| F-49 | SC-23, `stop_sign` | The four-way stop had a sign on the right approach only | Note | **Fixed:** every approach of the cross street has one |
| F-50 | Scenes SC-11, SC-13, SC-18 | Their pass criteria mention remote assistance or a remote operator. Nothing of it is drawn; the text is public in `scenarios.yaml` and `restricted()` refuses only the remote link (`link-*`) and `CSR-` requirements | Note | **The lead's call:** whether that reading of the cybersecurity rule is right |
| F-52 | Layouts (author, before the review) | The new overlap test found three collisions in the first layouts: the pull-in path of SC-15 drove through a person standing at the kerb, SC-16's two pedestrians walked into each other, SC-17's passing car met an oncoming van head-on. A pace check by hand found a bicycle at 82 km/h (SC-19) and red-runners and an emergency vehicle at over 75 km/h | Minor | **Fixed** before the review: positions and paths moved, paths shortened |
| F-53 | Dashboard, SC-18 (cold read) | A scenario with no safety goal at stake showed the "Safety goals at stake" heading over nothing | Minor | **Fixed:** the panel says that `stake()` derives none |
| F-54 | SC-08, SC-17 | The seeded speeds are 1.6 and 2.3 km/h, so the vehicle crawls and the clips are long; "loss of Autoware while driving" at walking pace is a weak picture | Note | **Kept:** the draw is not tuned to look good (SALT is one for all); the README says so. The lead may ask for a pick |
| F-55 | SC-10 | The red planned path runs into the barrier: it stands for Autoware following the map that still shows the lane open. The legend calls it Autoware's planned path, which is what it is in that scenario | Note | **Kept** |
| F-56 | SC-05 | The ego starts to slow after the main view's moment, so the still shows it cruising up to the line while the red-runner crosses | Note | **Kept:** consistent with the pass criterion (it does not enter while the path is crossed) |

## Checks run before pushing

Run on the commit of the third round, in the session's container (Python 3.13, PyYAML 6.0.2, `bpy` 5.2.3):

| Check | Result |
|---|---|
| Everything `CLAUDE.md` lists: the decision register, the safety case records, headers, links, tables, `check_restricted.py`, every generator with `--check`, the assurance tests, the README figures | All pass |
| `python3 tools/sim/scene.py --check` | 6 generated files current |
| `python3 -m unittest discover -s tools/sim -p 'test_*.py'` | 36 tests pass |
| `build_blend.py tools/sim/scenes/*.json --out tools/sim/dashboards --verify` (32 samples, CC0 look after `fetch_assets.py --locked`) | All five scenes match their descriptions; the gallery shows each dashboard as current |
| The wiki's tests and `build_wiki.py --check` | Pass |
| black and isort at line length 100 | Clean |
| `git diff origin/main -- assurance/` | Empty |

## What this record does not do

It does not verify the tool in the sense of WP-P-05, accept anything, or make any picture evidence. The open items
(F-10 for the clip's overlay, F-16, F-17, F-27, F-28) wait on the lead's review of pull request #57.
