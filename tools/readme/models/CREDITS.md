# 3D models

The vehicles in the README and wiki figures are rendered from two models published on Sketchfab under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
Both were downloaded on 2026-10-23. The FBX files here are the `source/` files of those downloads, renamed and
otherwise unchanged; the textures of the downloads are not used and not kept.

| File | Model | Author | Licence | SHA-256 |
|---|---|---|---|---|
| `kiri10.fbx` | ["Kiri '10 - Low poly model"](https://sketchfab.com/3d-models/kiri-10-low-poly-model-7fd6e15785fa4aa9bfd6e31eb7c97ba6) | [Daniel Zhabotinsky](https://sketchfab.com/DanielZhabotinsky) | CC BY 4.0 | `392d1c1435f5a97e4791b948997ee51d5757392d95f9288cd54e0fc436e85f44` |
| `generic-passenger-car-pack.fbx` | ["Generic passenger car pack"](https://sketchfab.com/3d-models/generic-passenger-car-pack-20f9af9b8a404d5cb022ac6fe87f21f5) | [Comrade1280](https://sketchfab.com/comrade1280) | CC BY 4.0 | `3b60a21399cde2723e6250f29f80f4487e932e937ca08d4e17d90b1d8e845ee6` |

## Changes made in the figures

[`mesh.py`](../mesh.py) and [`render3d.py`](../render3d.py) change the models when they draw them:

- the interior, steering wheel, badges, number plates and inner bumper parts of the Kiri '10 are left out;
- six of the pack's cars are used (sedan, hatchback, wagon, SUV, minivan, compact), each with its four wheels; the
  coupe, sport car, pickup and off-road car are not;
- textures are not used: every part is flat-shaded in one colour per part class, and the body colours are ours;
- the meshes are simplified (vertices clustered on a grid), so fine detail is lost;
- the ego vehicle carries a roof sensor that is not part of the model.

## Changes made in the Blender scenes

[`tools/sim/build_blend.py`](../../sim/build_blend.py) uses the models, through `mesh.py`, in qualitative scenes of the
known scenarios:

- the same parts are left out and kept as above, and the models are normalised the same way;
- the meshes are used at full resolution, not simplified;
- textures are not used: each part class has one material, and the body colours are ours (amber for the road user a
  scenario is about, grey for the others, white for the ego vehicle);
- the ego vehicle carries a roof sensor that is not part of the model;
- the SUV of the pack stands in for an emergency vehicle and the minivan for a van.

Every render names both models, their authors and the licence on its face.

The scenes also use CC0 1.0 assets, which need no credit; the dashboards name their sources all the same:

- skies (HDRIs), road, sidewalk, verge and facade textures, street trees, bins and hydrants from
  [Poly Haven](https://polyhaven.com) and [ambientCG](https://ambientcg.com), fetched by
  [`tools/sim/fetch_assets.py`](../../sim/fetch_assets.py) and recorded with their SHA-256 in
  [`tools/sim/assets.lock.json`](../../sim/assets.lock.json) (the files themselves are not committed);
- two pedestrian figures by Quaternius, in [`tools/sim/models/people/`](../../sim/models/people/README.md).

Their use here does not mean that either author endorses this project or its figures.
