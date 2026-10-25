# Scenario scenes in Blender

> [!WARNING]
> **Qualitative illustration · not a simulation result · draft for engineering review.** These scenes show what a
> known scenario of [WP-V-03](../../assurance/06-validation/WP-V-03-sotif-known-scenarios.md) is, what the vehicle
> and the independent safety monitor are meant to do, and where the hazard lies. They are for understanding and
> review. They are not verification or validation evidence, they are not output of Autoware or of a simulator, and
> no scenario has been run (WP-V-03 §4). Every render carries this stamp on its face.

## What it does

A scenario of [`scenarios.yaml`](../../assurance/06-validation/scenarios/scenarios.yaml) is a logical scenario: its
parameters have ranges. For each scenario that has a layout, the tool picks one concrete scenario from those ranges,
builds it in Blender, and renders a still and, if asked, a short clip:

- the road layout (lanes, sidewalks, crosswalk, stop line, junction, signals, posted limit sign);
- the ego robotaxi (the Kiri '10 model) and the other road users, of the participant classes the sample draws;
- Autoware's planned path (red), the safety monitor's envelope (blue, moving with the vehicle), what the pass
  criterion asks of the vehicle (dashed green, its moment ringed), and where the hazard lies (orange);
- the ODD conditions the sample sets: day, dusk, low sun, night or unlit streets; rain; mist at a visibility; a wet
  road. A scenario that sweeps across the ODD limit (SC-14) shows the limit as a violet curtain, with the condition
  drawn denser beyond it and no value stated there.

Scenes exist for SC-01, SC-02, SC-03, SC-06 and SC-14. The others have no layout yet.
[`layouts.py`](layouts.py) lists what a layout holds; adding one is enough for a scenario to be drawn.

Scenarios about the remote operations link, remote release and return to service (SC-20, SC-21, SC-26) are not drawn
and must not be: their scenes would show security architecture. The tests check that they have no layout.

## How it is built

| File | Runs in | Does |
|---|---|---|
| [`scene.py`](scene.py) | Python, PyYAML | Reads the records and writes [`scenes/<id>.json`](scenes/), the scene description; `--check` fails if one is stale |
| [`layouts.py`](layouts.py) | (data) | Road geometry and choreography of each scene, in metres; holds no fact |
| [`build_blend.py`](build_blend.py) | Blender (`bpy`) | Builds the Blender scene from one description, renders it, writes a manifest of what it built, and with `--verify` fails when the built scene differs from the description |
| [`test_sim.py`](test_sim.py) | Python, PyYAML | Unit tests; Blender not needed |

### Where the labels come from

Nothing on a frame is typed. `scene.py` reads:

| On the frame | From |
|---|---|
| Scenario id, name, description, parameters and their ranges, pass criterion and its references | `scenarios.yaml` (WP-V-03) |
| Safety goals at stake | `scenarios.py`'s own `stake()`, from the HARA events and the triggering conditions |
| Goal statements and ASILs | WP-C-03 §7, through [`tools/readme/facts.py`](../readme/facts.py) |
| ODD attribute names; monitor names | WP-C-02 §3 and §4, through `facts.py` |
| The rating of Autoware (EL-01) and of the safety monitor (EL-02) | WP-C-04 §4, through `facts.py` |
| Hazardous events, triggering conditions | `hara.yaml`, `triggering.yaml`, through `scenarios.py` |
| The short "meant to do" line | The sketch of the scenario in WP-V-03 Figure 2-1 ([`scards.py`](../../assurance/06-validation/scenarios/scards.py)) |

`build_blend.py` reads only the description. A lookup that fails stops `scene.py`.

### The concrete scenario

The sample is deterministic: a generator seeded from the scenario id (and `SALT` in `scene.py`).

- A two-sided numeric range: a draw inside it, to 0.1.
- A one-sided range (visibility of 200 m or more, a posted limit at or below 30 mph): the stated bound.
- A range that crosses the ODD limit: no value; the scene shows inside and beyond.
- A categorical parameter: a draw among the scenario's own values, unless the layout picks one (`pick`) so that the
  still shows what the scenario is about. `scene.py` refuses a pick that is not one of the scenario's values. The
  description records whether each value was drawn or picked.
- A behaviour bound that a requirement states but has not fixed (a pedestrian's walking speed, a lead vehicle's
  deceleration): no value.

### What is not computed

- **Motion is choreography.** Each road user goes along its path between two moments of the clip. No speed or
  acceleration of another road user is stated, because the requirements that would bound them (FSR-06.01, FSR-06.02)
  have not fixed one. The ego vehicle cruises, slows and stops at the end of its path; its sampled speed is a label.
- **The envelope's length is not computed.** It is drawn at a fixed length (`ENVELOPE_M`) and shrinks with the
  square of the vehicle's speed share as it slows. The real envelope depends on the vehicle's deceleration and
  response time, which are parameters until the vehicle is chosen (DQ-008, WP-V-08 §2).
- **Weather is drawn, not modelled.** The rain density is proportional to the sampled rate. Mist uses the
  Koschmieder relation (extinction 3.912 / visibility) so that a 200 m visibility looks like one. Beyond the ODD
  limit both are drawn denser, with no value stated. None of this is a sensor model; SIM-03 (WP-V-08 §2) is.

## How the check works

Blender renders are not byte-deterministic (floating point, denoiser, version), so a raster image cannot be checked
the way the SVG figures are. The check is split:

1. **The scene description is the generated output.** `scenes/*.json` holds everything the scene shows and where it
   is. It is committed and byte-checked: `python3 tools/sim/scene.py --check` fails when a record it reads has
   changed and the description has not been regenerated. CI runs it on every pull request
   ([`sim.yaml`](../../.github/workflows/sim.yaml)), with the unit tests.
2. **The Blender scene is checked against the description, not against pixels.** `build_blend.py --verify` builds
   the scene, then compares what it built with the description: every road user at the position the description
   gives it at the still frame (within 5 cm), and on the frame the stamp, the scenario id and name, every sampled
   parameter, every safety goal and every legend line. The manifest it writes (`<id>.manifest.json`) records this
   with the Blender version and the render settings. CI runs it in the `render` job.
3. **Renders are not committed.** The `render` job publishes the stills (and the manifests) as a workflow artifact
   named `scenario-scenes`, kept 30 days. It runs when a pull request touches `tools/sim/`, the scenario records or the
   models, and on demand (`workflow_dispatch`, which can also render the clips). A render is therefore always made
   from the committed description by the committed code, and never sits in the repository looking like evidence.

## Running it

Blender's Python module comes from PyPI (`bpy`, about 400 MB, Python 3.13). It is not a dependency of the assurance
checks.

```sh
python3 tools/sim/scene.py                       # regenerate the descriptions after a record changes
python3 tools/sim/scene.py --check
python3 -m unittest discover -s tools/sim -p 'test_*.py' -v

python3.13 -m venv build/bpy && build/bpy/bin/pip install bpy==5.2.3
build/bpy/bin/python tools/sim/build_blend.py tools/sim/scenes/*.json --out build/sim --verify
build/bpy/bin/python tools/sim/build_blend.py tools/sim/scenes/SC-01.json --out build/sim --animate --blend
blender -b -P tools/sim/build_blend.py -- tools/sim/scenes/SC-06.json --out build/sim   # with Blender itself
```

Cycles renders on the CPU; a still at 1600 × 900 and 48 samples takes about a minute on four cores. `--scale 50` and
`--samples 16` make a quick preview; `--no-render` only builds and verifies. `--blend` saves the scene so it can be
opened and looked round in Blender.

## Models

The vehicles are the CC BY 4.0 models of [`tools/readme/models/`](../readme/models/CREDITS.md), loaded through
[`mesh.py`](../readme/mesh.py). Every render names their authors and the licence on its face. The changes made for
these scenes are listed in [CREDITS.md](../readme/models/CREDITS.md).
