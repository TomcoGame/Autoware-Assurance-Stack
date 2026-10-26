#!/usr/bin/env python3
"""Fetch the CC0 skies, ground and facade textures and street models the scenario scenes are drawn with.

Every asset comes from Poly Haven (polyhaven.com) or ambientCG (ambientcg.com), whose assets are all CC0 1.0: public
domain, no attribution required (the dashboards name the sites all the same). The asset IDs are those the
LionDriver hazard scenes chose and checked (its library/assets.yaml), plus three ambientCG facades. Files go under
tools/sim/assets/<slot>/ (git-ignored); tools/sim/assets.lock.json (committed) records each file's URL and SHA-256.
With --locked, exactly the locked files are fetched and each is checked, so two machines draw the same scene.
build_blend.py uses a slot when its files are present and a procedural look when they are not, so nothing in CI
needs them; the dashboard says which look it was drawn with.

    python3 tools/sim/fetch_assets.py              # fetch what is missing, write the lock
    python3 tools/sim/fetch_assets.py --locked     # fetch the locked files and check their SHA-256

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
DEST = HERE / "assets"
LOCK = HERE / "assets.lock.json"
POLYHAVEN = "https://api.polyhaven.com/files/"
AMBIENTCG = "https://ambientcg.com/get?file={id}_2K-JPG.zip"
AGENT = "autoware-assurance-stack tools/sim fetch_assets/1"

# slot -> source, asset ID, kind, and how the scene uses it. size_m: metres one texture tile covers ([x, y] when not
# square), as the source publishes it. tint: multiplies the colour map. strength: sky brightness.
SLOTS: dict[str, dict] = {
    "hdri_day": {
        "source": "polyhaven",
        "id": "kloofendal_48d_partly_cloudy_puresky",
        "kind": "hdri",
    },
    "hdri_low_sun": {"source": "polyhaven", "id": "spruit_sunrise", "kind": "hdri"},
    "hdri_night": {"source": "polyhaven", "id": "dikhololo_night", "kind": "hdri"},
    "hdri_overcast": {"source": "polyhaven", "id": "overcast_soil_puresky", "kind": "hdri"},
    "asphalt": {
        "source": "polyhaven",
        "id": "asphalt_02",
        "kind": "pbr",
        "size_m": 3.0,
        "tint": 0.5,
    },
    "concrete": {"source": "ambientcg", "id": "Concrete034", "kind": "pbr", "size_m": [1.1, 0.55]},
    "grass": {"source": "ambientcg", "id": "Grass004", "kind": "pbr", "size_m": 1.4},
    "facade_a": {"source": "ambientcg", "id": "Facade018A", "kind": "pbr", "size_m": 13.0},
    "facade_b": {"source": "ambientcg", "id": "Facade019A", "kind": "pbr", "size_m": 13.0},
    "facade_c": {"source": "ambientcg", "id": "Facade020A", "kind": "pbr", "size_m": 13.0},
    "tree": {"source": "polyhaven", "id": "tree_small_02", "kind": "model"},
    "bin": {"source": "polyhaven", "id": "metal_trash_can", "kind": "model"},
    "hydrant": {"source": "polyhaven", "id": "fire_hydrant", "kind": "model"},
}
MAPS = {
    "color": ("Diffuse", "_Color"),
    "normal": ("nor_gl", "_NormalGL"),
    "roughness": ("Rough", "_Roughness"),
}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def polyhaven(slot: dict) -> dict[str, str]:
    """relative path -> URL of the files a Poly Haven slot needs."""
    files = json.loads(get(POLYHAVEN + slot["id"]))
    if slot["kind"] == "hdri":
        url = files["hdri"]["2k"]["hdr"]["url"]
        return {"sky.hdr": url}
    if slot["kind"] == "pbr":
        return {f"{m}.jpg": files[key]["2k"]["jpg"]["url"] for m, (key, _) in MAPS.items()}
    g = files["gltf"]["1k"]["gltf"]
    out = {f"{slot['id']}.gltf": g["url"]}
    out.update({rel: v["url"] for rel, v in g["include"].items()})
    return out


def ambientcg(slot: dict) -> dict[str, bytes]:
    """relative path -> bytes of an ambientCG texture, unpacked from its 2K JPG zip."""
    out = {}
    with zipfile.ZipFile(io.BytesIO(get(AMBIENTCG.format(id=slot["id"])))) as z:
        for m, (_, suffix) in MAPS.items():
            name = f"{slot['id']}_2K-JPG{suffix}.jpg"
            if name not in z.namelist():
                raise SystemExit(f"{slot['id']}: the zip has no {name}")
            out[f"{m}.jpg"] = z.read(name)
    return out


def safe(rel: str) -> str:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        raise SystemExit(f"refusing the path {rel!r}")
    return rel


def fetch(locked: bool) -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.exists() else {"slots": {}}
    if locked and not lock["slots"]:
        raise SystemExit(f"{LOCK.name} is empty: run without --locked first")
    out = {"schema": 1, "licence": "CC0 1.0 (Poly Haven, ambientCG)", "slots": {}}
    for name, slot in SLOTS.items():
        dest = DEST / name
        entry = {k: v for k, v in slot.items()}
        entry["page"] = (
            f"https://polyhaven.com/a/{slot['id']}"
            if slot["source"] == "polyhaven"
            else f"https://ambientcg.com/view?id={slot['id']}"
        )
        known = lock["slots"].get(name, {})
        if locked:
            files = known.get("files", {})
        elif known.get("id") == slot["id"] and all(
            (dest / rel).exists() for rel in known.get("files", {})
        ):
            files = known["files"]
        else:
            files = {}
        if files and all(
            (dest / rel).exists() and sha256((dest / rel).read_bytes()) == f["sha256"]
            for rel, f in files.items()
        ):
            entry["files"] = files
            out["slots"][name] = entry
            print(f"{name}: present")
            continue
        if slot["source"] == "polyhaven":
            data = {rel: (url, get(url)) for rel, url in polyhaven(slot).items()}
        else:
            url = AMBIENTCG.format(id=slot["id"])
            data = {rel: (url, b) for rel, b in ambientcg(slot).items()}
        entry["files"] = {}
        for rel, (url, b) in data.items():
            if locked and files.get(rel, {}).get("sha256") != sha256(b):
                raise SystemExit(f"{name}/{rel}: SHA-256 differs from the lock")
            path = dest / safe(rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b)
            entry["files"][rel] = {"url": url, "sha256": sha256(b)}
        out["slots"][name] = entry
        print(f"{name}: fetched {len(data)} file(s)")
    if not locked:
        LOCK.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {LOCK.name}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--locked", action="store_true", help="fetch the locked files, check SHA-256")
    args = ap.parse_args(argv)
    try:
        return fetch(args.locked)
    except urllib.error.URLError as e:
        print(f"cannot reach the asset sites: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
