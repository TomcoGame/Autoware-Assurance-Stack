# Pedestrians

Two walking figures for the pedestrians of the scenario scenes, copied unchanged from the LionDriver hazard scenes
(`jherrodthomas/LionDriver`, branch `liondriver-dev` at `bc8ca54`, `assurance/sim/blender/library/people/`). LionDriver
built them from two free Quaternius packs, both **CC0 1.0** (public domain dedication; no attribution required).

| File | Figure | Built from | SHA-256 |
|---|---|---|---|
| `pedestrian_male.glb` | Male base character, short parted hair; 1.78 m | Universal Base Characters [Standard]: `Superhero_Male_FullBody`, `Hair_SimpleParted` | `3e02857c0a3532ac1899d743d94bfd8dad50c8d3b8709d29ac563429efa412f8` |
| `pedestrian_female.glb` | Female base character, hair in buns; 1.66 m | Universal Base Characters [Standard]: `Superhero_Female_FullBody`, `Hair_Buns` | `c9d384117e3f6e1e2807c7d95952cf0fe2239c0291e0dc1c9e632d1fd64a3ba9` |

Both carry the pack's rig and the `Walk_Loop` animation of the Universal Animation Library [Standard]; LionDriver cut
their textures to 1024 px JPEG and gave them a shirt, trousers and shoes.

[`../../look.py`](../../look.py) imports one figure per pedestrian, faces it along its path, recolours the shirt
(amber for the road user the scenario is about), scales it to a child where the sample draws a child, and plays
`Walk_Loop` by the distance walked (one loop every 1.45 m, as LionDriver does). Cyclists, scooter riders and
wheelchair users are still drawn from primitives.

Sources: Universal Base Characters ([quaternius.com](https://quaternius.com/packs/universalbasecharacters.html)) and
Universal Animation Library ([quaternius.com](https://quaternius.com/packs/universalanimationlibrary.html)); both
packs' `License.txt` give CC0 1.0.
