# Scenario scenes in Blender

> [!WARNING]
> **Qualitative illustration · not a simulation result · draft for engineering review.** These scenes show what a
> known scenario of [WP-V-03](../../assurance/06-validation/WP-V-03-sotif-known-scenarios.md) is, what the vehicle
> and the independent safety monitor are meant to do, and where the hazard lies. They are for understanding and
> review. They are not verification or validation evidence, they are not output of Autoware or of a simulator, and
> no scenario has been run (WP-V-03 §4). Every render carries this stamp on its face.

**Gallery: [dashboards/README.md](dashboards/README.md)**, one review dashboard per scene with the state of its
render. The same gallery as a web page, with filters by safety goal, light and weather and the dashboards in a viewer:
**[Robotaxi Scenario Scenes](https://claude.ai/artifact/SWCvdEBXiHJyVWfAdh1XS8)** (a claude.ai page, private to the
project lead; republished after each gallery change). **Audit: [AUDIT.md](AUDIT.md)**, the pre-review audit of this tool (author-side, I0) and its findings.

![Review dashboard of SC-01: the chase view in the middle with the road users tagged, the forward and top views on the right, the scenario's records and the concrete sample on the left, the moments of the clip along the bottom](dashboards/SC-01.jpg)

## What it does

A scenario of [`scenarios.yaml`](../../assurance/06-validation/scenarios/scenarios.yaml) is a logical scenario: its
parameters have ranges. For each scenario that has a layout, the tool picks one concrete scenario from those ranges,
builds it in Blender, and renders a review dashboard and, if asked, a short clip. The scene holds:

- the road layout (lanes, sidewalks, crosswalk, stop line, junction, signals, posted limit sign);
- the ego robotaxi (the Kiri '10 model) and the other road users, of the participant classes the sample draws;
- Autoware's planned path (red), the safety monitor's envelope (a blue outline ahead of the vehicle, moving with
  it), what the pass criterion asks of the vehicle (dashed green, its moment ringed), and where the hazard lies (an
  orange outline). Every overlay lies flat on the road, as in LionDriver, so none hides the scene from the road-level
  cameras; `--verify` fails if one stands higher than OVERLAY_TOP_M;
- the ODD conditions the sample sets: day, dusk, low sun, night or unlit streets; rain; mist at a visibility; a wet
  road. A scenario that sweeps across the ODD limit (SC-14) shows the limit as a violet band across the road, with the condition
  drawn denser beyond it and no value stated there.

The dashboard (1920 × 1080, laid out like the LionDriver hazard-scene dashboards) puts on one page:

| Where | What | From |
|---|---|---|
| Header | Scenario id and name, the safety goals at stake with their ASIL, the motion source (choreography), the condition, the sampled ego speed, the methods | The description |
| Left | The scenario as the records state it: description, hazardous events, triggering conditions, situations, misuse cases, loss scenarios; below, the concrete sample, one line per parameter | The description |
| Centre | The chase view (a camera that follows the ego) at the moment the scene is about, every road user tagged and marked *qualitative*; what the vehicle is meant to do and the pass criterion with its references; a filmstrip of the moments of the clip | Blender; the description |
| Right | The forward view from the roof, the top view (planned path, envelope, hazard, without the weather), the safety goals at stake and the ODD monitors the pass criterion cites | Blender; the description |
| Footer | The stamp, the legend (only for what the scene draws), the model credits | The description |

There is no metric panel (gap, time to collision, speed traces): with the behaviour bounds not fixed and the vehicle
not chosen, any such number would be made up.

### The look

The scene is drawn with CC0 assets when they have been fetched, as the LionDriver scenes are:

| Part | With the assets (`fetch_assets.py`) | Without them (CI, offline, `--procedural`) |
|---|---|---|
| Sky | An HDRI for the light: clear, low sun, night; overcast under rain or mist (Poly Haven) | A flat colour |
| Road, sidewalks, verges | Scanned asphalt, concrete and grass, 2K PBR maps in world metres (Poly Haven, ambientCG) | Noise textures with a bump |
| Buildings | Three brick and window facades, 13 m tiles (ambientCG), with roofs | A procedural grid of windows |
| Street furniture | Street trees, bins and hydrants, seeded, kept clear of crosswalks, junctions, signs, poles and every road user's path | None |
| Pedestrians | Two CC0 Quaternius figures walking by the distance they cover ([`models/people/`](models/people/README.md), committed) | The same; cyclists, scooter riders and wheelchair users stay primitives |

The views render at 1.5 times their size on the dashboard and are box-filtered down, and the dashboard is laid out
with a narrow pixel filter so the pictures sit pixel on pixel. The look never moves anything the description places,
and `--verify` checks a scene the same way under either look. Each manifest records which assets a dashboard was
drawn with, the dashboard's credit line names them, and the gallery says which look each one has.

Scenes exist for SC-01, SC-02, SC-03, SC-06 and SC-14. The others have no layout yet.
[`layouts.py`](layouts.py) lists what a layout holds; adding one is enough for a scenario to be drawn.

A scenario that varies the remote operations link (ODD-15 `link-*`) or whose pass criterion rests on a
cybersecurity requirement (`CSR-`) is never drawn: its scene would show security architecture (CLAUDE.md, WP-M-09
§4). `scene.py` derives this from the records (SC-20, SC-21, SC-24, SC-25, SC-26 today) and refuses a layout for one.

## How it is built

| File | Runs in | Does |
|---|---|---|
| [`scene.py`](scene.py) | Python, PyYAML | Reads the records and writes [`scenes/<id>.json`](scenes/), the scene description, and the gallery page [`dashboards/README.md`](dashboards/README.md); `--check` fails if one is stale |
| [`layouts.py`](layouts.py) | (data) | Road geometry and choreography of each scene, in metres; holds no fact |
| [`build_blend.py`](build_blend.py) | Blender (`bpy`) | Builds the Blender scene from one description, renders the views and lays out the dashboard (in Blender too: no imaging library), writes a manifest of what it built, and with `--verify` fails when the built scene differs from the description |
| [`look.py`](look.py) | Blender (`bpy`) | The skies, surfaces, street furniture and pedestrians, from the CC0 assets or procedural |
| [`fetch_assets.py`](fetch_assets.py) | Python | Fetches the CC0 assets into `assets/` (git-ignored) and records them in [`assets.lock.json`](assets.lock.json); `--locked` checks every file's SHA-256 |
| [`test_sim.py`](test_sim.py) | Python, PyYAML | Unit tests; Blender not needed |

### Where the labels come from

Nothing on a frame is typed. `scene.py` reads:

| On the frame | From |
|---|---|
| Scenario id, name, description, parameters and their ranges, pass criterion and its references, methods, misuse cases, loss scenarios | `scenarios.yaml` (WP-V-03) |
| Safety goals at stake | `scenarios.py`'s own `stake()`, from the HARA events and the triggering conditions |
| Goal statements and ASILs | WP-C-03 §7, through [`tools/readme/facts.py`](../readme/facts.py) |
| ODD attribute names; monitor names | WP-C-02 §3 and §4, through `facts.py` |
| The rating of Autoware (EL-01) and of the safety monitor (EL-02) | WP-C-04 §4, through `facts.py` |
| That the vehicle is not chosen yet (the envelope legend) | The decision register: `scene.py` fails once DQ-008 is applied, so the legend cannot go stale |
| Hazardous events, triggering conditions | `hara.yaml`, `triggering.yaml`, through `scenarios.py` |
| The short "meant to do" line | The sketch of the scenario in WP-V-03 Figure 2-1 ([`scards.py`](../../assurance/06-validation/scenarios/scards.py)) |

The words that are not facts (panel headings, "qualitative", the moments of the filmstrip such as "vehicle starts
to slow") describe the picture, not the item. `build_blend.py` reads only the description.

### The concrete scenario

The sample is deterministic: each parameter has its own generator, seeded from `SALT`, the scenario id and the
parameter, so changing or picking one parameter leaves the others as they were.

- A two-sided numeric range: a draw inside it, to 0.1.
- A one-sided range (visibility of 200 m or more, a posted limit at or below 30 mph): the stated bound.
- A range that crosses the ODD limit: no value; the scene shows inside and beyond.
- A categorical parameter: a draw among the scenario's own values, unless the layout picks one (`pick`) so that the
  still shows what the scenario is about. `scene.py` refuses a pick that is not one of the scenario's values. The
  description records whether each value was drawn or picked.
- A behaviour bound that a requirement states but has not fixed (a pedestrian's walking speed, a lead vehicle's
  deceleration): no value.
- The ego speed (ODD-20) never exceeds the sampled posted limit (ODD-03), as ODD-20's `capped_by` says.

### What is not computed

- **Motion is choreography.** Each road user goes along its path between two moments of the clip. No speed or
  acceleration of another road user is stated, because the requirements that would bound them (FSR-06.01, FSR-06.02)
  have not fixed one. The ego cruises at its sampled speed, then slows to a stop at the end of its path at the firm
  level of FSR-03.02 (read from `fsc.yaml`), which is the most a stop that the safety channel does not have to
  confirm may brake. Its start is placed so that this stop fits, and the clip lasts as long as it takes. Which level
  Autoware itself would brake at is not modelled; the dashboard says so.
- **The envelope's length is not computed.** It is drawn at a fixed length (`ENVELOPE_M`) and shrinks with the
  square of the vehicle's speed share as it slows. The real envelope depends on the vehicle's deceleration and
  response time, which are parameters until the vehicle is chosen (DQ-008, WP-V-08 §2).
- **Weather is drawn, not modelled.** The number of rain streaks grows with the sampled rate (a fixed base plus a
  share proportional to the rate). Mist is a uniform volume whose extinction is set from the sampled visibility by
  the Koschmieder relation (3.912 / visibility); the volume shader is not calibrated, so the picture only suggests
  that visibility. Beyond the ODD limit both are drawn denser, with no value stated. None of this is a sensor model;
  SIM-03 (WP-V-08 §2) is.

## How the check works

Blender renders are not byte-deterministic (floating point, denoiser, version), so a raster image cannot be checked
the way the SVG figures are. The check has three parts:

1. **The scene description is the generated output.** `scenes/*.json` holds everything the scene shows and where it
   is, and `dashboards/README.md` the state of each committed dashboard. Both are byte-checked:
   `python3 tools/sim/scene.py --check` fails when a record they read has changed and they have not been regenerated.
   CI runs it on every pull request and push to main ([`sim.yaml`](../../.github/workflows/sim.yaml)), with the unit
   tests. No Blender is needed, so a change to a record never needs a render to pass CI.
2. **A dashboard is checked against its description, not against pixels.** `build_blend.py --verify` builds the
   scene and compares it with the description:
   - every road user at the position the description gives it at the still frame (within 5 cm);
   - the conditions and features drawn: light, wet road, rain, mist, the ODD-limit band and the denser mist
     beyond it, stop line, speed sign, occlusion, the sampled features;
   - on the dashboard and on the clip: the stamp, the scenario id and name, every sampled parameter, every safety
     goal, every monitor, the pass criterion, every legend line, the model credits.

   The manifest it writes (`<id>.manifest.json`) records this with the Blender version, the render settings, the
   SHA-256 of the description it was made from and the SHA-256 of the picture.

   The position check compares the keyframed scene with the same motion functions that made it, so it catches a
   fault in building the scene, not a wrong choreography. Choreography is checked by the unit tests (the clip runs at
   the sampled speed, the ego stops before its stop line) and by review of the dashboards.
3. **The dashboards are committed, and their state is shown.** The JPEGs and manifests in
   [`dashboards/`](dashboards/README.md) are kept out of the byte check. Instead, `scene.py` writes each one's state
   into the gallery page: *current* when its manifest's description hash is that of the committed description, its
   picture hash matches the file, and the manifest passes `--verify`; *stale* with the reason otherwise. A record
   change therefore never fails CI for want of a render, but the gallery says which pictures are out of date.

   The [`sim-render.yaml`](../../.github/workflows/sim-render.yaml) workflow re-renders every scene from the committed
   descriptions, verifies it and publishes the dashboards as the artifact `scenario-scenes` (30 days). It runs on
   pull requests that touch `tools/sim/`, the scenario records or the models, and on demand (where it can also
   render the clips). It is advisory: it is not a required check and does not run on pushes to main.

## Running it

Blender's Python module comes from PyPI (`bpy`, about 400 MB, Python 3.13). It is not a dependency of the assurance
checks.

```sh
python3 tools/sim/scene.py                       # regenerate the descriptions and the gallery page
python3 tools/sim/scene.py --check
python3 -m unittest discover -s tools/sim -p 'test_*.py' -v

python3 tools/sim/fetch_assets.py --locked        # the CC0 assets (about 200 MB, git-ignored); optional
python3.13 -m venv build/bpy && build/bpy/bin/pip install bpy==5.2.3
build/bpy/bin/python tools/sim/build_blend.py tools/sim/scenes/*.json --out tools/sim/dashboards --verify
python3 tools/sim/scene.py                       # the gallery page now shows the new renders as current
build/bpy/bin/python tools/sim/build_blend.py tools/sim/scenes/SC-01.json --out build/sim --animate --blend
blender -b -P tools/sim/build_blend.py -- tools/sim/scenes/SC-06.json --out build/sim   # with Blender itself
```

Cycles renders on the CPU. In the container this tool was written in (four cores), a dashboard at 48 samples took a
few minutes and a clip of a few seconds at reduced size several minutes; treat those as rough. `--samples 12` makes
a quick preview; `--no-render` only builds and verifies; `--blend` saves the scene so it can be opened and looked
round in Blender. The separate views go to `--work` (default `build/sim/work`, git-ignored).

## Models

The vehicles are the CC BY 4.0 models of [`tools/readme/models/`](../readme/models/CREDITS.md), loaded through
[`mesh.py`](../readme/mesh.py). Every dashboard and clip names their authors and the licence on its face. The changes
made for these scenes are listed in [CREDITS.md](../readme/models/CREDITS.md). The skies, textures and street
furniture are CC0 (Poly Haven, ambientCG; [`assets.lock.json`](assets.lock.json)), and so are the pedestrians
(Quaternius; [`models/people/`](models/people/README.md)).
