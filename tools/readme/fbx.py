#!/usr/bin/env python3
"""A minimal reader for binary FBX files: enough to take triangle meshes out of a model.

FBX binary layout: a 27-byte header, then a tree of node records. Each record holds an end offset, a
property count and length, a name, typed properties (scalars, strings, raw bytes and arrays, the arrays
optionally zlib-compressed) and nested records. Version 7500 and later use 64-bit offsets.

Only what mesh extraction needs is read: Geometry nodes (Vertices, PolygonVertexIndex, material
indices), Model nodes with their local transforms, Material names, the Connections between them and
GlobalSettings (up axis, unit scale). Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import math
import struct
import zlib

MAGIC = b"Kaydara FBX Binary  \x00"


class FbxError(Exception):
    """The file is not a binary FBX this reader understands."""


@dataclass
class Node:
    name: str
    props: list = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)

    def child(self, name: str) -> "Node | None":
        return next((c for c in self.children if c.name == name), None)

    def all(self, name: str) -> list["Node"]:
        return [c for c in self.children if c.name == name]


_ARRAY = {"f": ("f", 4), "d": ("d", 8), "l": ("q", 8), "i": ("i", 4), "b": ("b", 1)}
_SCALAR = {
    "Y": ("<h", 2),
    "C": ("<?", 1),
    "I": ("<i", 4),
    "F": ("<f", 4),
    "D": ("<d", 8),
    "L": ("<q", 8),
}


def _prop(data: bytes, pos: int) -> tuple[object, int]:
    code = chr(data[pos])
    pos += 1
    if code in _SCALAR:
        fmt, size = _SCALAR[code]
        return struct.unpack_from(fmt, data, pos)[0], pos + size
    if code in _ARRAY:
        n, enc, clen = struct.unpack_from("<III", data, pos)
        pos += 12
        raw = data[pos : pos + clen]
        if enc == 1:
            raw = zlib.decompress(raw)
        fmt, size = _ARRAY[code]
        if len(raw) != n * size:
            raise FbxError(f"array of {n} '{code}' has {len(raw)} bytes")
        return list(struct.unpack(f"<{n}{fmt}", raw)), pos + clen
    if code in "SR":
        (n,) = struct.unpack_from("<I", data, pos)
        pos += 4
        raw = data[pos : pos + n]
        return (raw.decode("utf-8", "replace") if code == "S" else raw), pos + n
    raise FbxError(f"unknown property type {code!r} at byte {pos - 1}")


def _node(data: bytes, pos: int, wide: bool) -> tuple["Node | None", int]:
    head = "<QQQB" if wide else "<IIIB"
    end, nprops, _plen, nlen = struct.unpack_from(head, data, pos)
    pos += struct.calcsize(head)
    if end == 0:
        return None, pos
    name = data[pos : pos + nlen].decode("ascii", "replace")
    pos += nlen
    node = Node(name)
    for _ in range(nprops):
        value, pos = _prop(data, pos)
        node.props.append(value)
    while pos < end:
        child, pos = _node(data, pos, wide)
        if child is None:
            break
        node.children.append(child)
    return node, end


def parse(data: bytes) -> Node:
    """The root of the node tree of a binary FBX file."""
    if not data.startswith(MAGIC):
        raise FbxError("not a binary FBX file (ASCII FBX is not supported)")
    (version,) = struct.unpack_from("<I", data, 23)
    wide = version >= 7500
    root, pos = Node("root"), 27
    while pos < len(data):
        node, pos = _node(data, pos, wide)
        if node is None:
            break
        root.children.append(node)
    return root


def _name(prop: object) -> str:
    return str(prop).split("\x00\x01")[0]


def _p70(node: Node) -> dict[str, list]:
    p70 = node.child("Properties70")
    return {p.props[0]: p.props[4:] for p in (p70.children if p70 else []) if p.name == "P"}


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _translate(v: list[float]) -> list[list[float]]:
    return [[1, 0, 0, v[0]], [0, 1, 0, v[1]], [0, 0, 1, v[2]], [0, 0, 0, 1]]


def _scale(v: list[float]) -> list[list[float]]:
    return [[v[0], 0, 0, 0], [0, v[1], 0, 0], [0, 0, v[2], 0], [0, 0, 0, 1]]


def _euler_xyz(deg: list[float]) -> list[list[float]]:
    """FBX's default rotation order: X first, then Y, then Z (R = Rz * Ry * Rx)."""
    x, y, z = (math.radians(d) for d in deg)
    rx = [
        [1, 0, 0, 0],
        [0, math.cos(x), -math.sin(x), 0],
        [0, math.sin(x), math.cos(x), 0],
        [0, 0, 0, 1],
    ]
    ry = [
        [math.cos(y), 0, math.sin(y), 0],
        [0, 1, 0, 0],
        [-math.sin(y), 0, math.cos(y), 0],
        [0, 0, 0, 1],
    ]
    rz = [
        [math.cos(z), -math.sin(z), 0, 0],
        [math.sin(z), math.cos(z), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
    return _matmul(rz, _matmul(ry, rx))


def _local(model: Node) -> list[list[float]]:
    """T * Roff * Rp * Rpre * R * Rp^-1 * Soff * Sp * S * Sp^-1 (post-rotation is not supported)."""
    p = _p70(model)
    vec = lambda key, d: [float(v) for v in p.get(key, d)[:3]]  # noqa: E731
    t, r, s = (
        vec("Lcl Translation", [0, 0, 0]),
        vec("Lcl Rotation", [0, 0, 0]),
        vec("Lcl Scaling", [1, 1, 1]),
    )
    pre, rp, sp = (
        vec("PreRotation", [0, 0, 0]),
        vec("RotationPivot", [0, 0, 0]),
        vec("ScalingPivot", [0, 0, 0]),
    )
    roff, soff = vec("RotationOffset", [0, 0, 0]), vec("ScalingOffset", [0, 0, 0])
    m = _translate(t)
    for step in (
        _translate(roff),
        _translate(rp),
        _euler_xyz(pre),
        _euler_xyz(r),
        _translate([-c for c in rp]),
        _translate(soff),
        _translate(sp),
        _scale(s),
        _translate([-c for c in sp]),
    ):
        m = _matmul(m, step)
    return m


def _geometric(model: Node) -> list[list[float]]:
    """The offset that applies to the model's own geometry only, not to its children."""
    p = _p70(model)
    vec = lambda key, d: [float(v) for v in p.get(key, d)[:3]]  # noqa: E731
    m = _translate(vec("GeometricTranslation", [0, 0, 0]))
    m = _matmul(m, _euler_xyz(vec("GeometricRotation", [0, 0, 0])))
    return _matmul(m, _scale(vec("GeometricScaling", [1, 1, 1])))


@dataclass
class Mesh:
    """Triangles in world space: one name and one material name per part."""

    name: str
    vertices: list[tuple[float, float, float]]
    triangles: list[tuple[int, int, int]]
    materials: list[str]  # one per triangle
    matrix: list[list[float]]  # the transform that was applied to the vertices


@dataclass
class Scene:
    up_axis: int  # 0 x, 1 y, 2 z
    unit_cm: float  # centimetres per unit
    meshes: list[Mesh]


def meshes(root: Node, local: bool = False) -> Scene:
    """Every mesh of the file, triangulated as a fan, in world space; with local=True in the frame
    of its own model (only the geometric offset applied), which keeps a vehicle's own axes."""
    objects = root.child("Objects")
    if objects is None:
        raise FbxError("no Objects section")
    gs = _p70(root.child("GlobalSettings") or Node("GlobalSettings"))
    up = int(gs.get("UpAxis", [1])[0])
    unit = float(gs.get("UnitScaleFactor", [1.0])[0])
    by_id = {o.props[0]: o for o in objects.children if o.props}
    parent: dict[int, int] = {}
    owners: dict[int, list[int]] = {}  # object -> objects connected to it
    for c in (root.child("Connections") or Node("Connections")).all("C"):
        if c.props[0] != "OO":
            continue
        child, par = c.props[1], c.props[2]
        owners.setdefault(par, []).append(child)
        if by_id.get(child) is not None and by_id[child].name == "Model":
            parent[child] = par

    def world(mid: int) -> list[list[float]]:
        m = _local(by_id[mid])
        p = parent.get(mid)
        while p in by_id and by_id[p].name == "Model":
            m = _matmul(_local(by_id[p]), m)
            p = parent.get(p)
        return m

    out = []
    for gid, geo in by_id.items():
        if geo.name != "Geometry" or len(geo.props) < 3 or geo.props[2] != "Mesh":
            continue
        model_ids = [
            m
            for m, kids in owners.items()
            if gid in kids and m in by_id and by_id[m].name == "Model"
        ]
        if not model_ids:
            continue
        mid = model_ids[0]
        mats = [
            _name(by_id[k].props[1])
            for k in owners.get(mid, [])
            if k in by_id and by_id[k].name == "Material"
        ]
        v = geo.child("Vertices").props[0]
        idx = geo.child("PolygonVertexIndex").props[0]
        lem = geo.child("LayerElementMaterial")
        per_poly = lem.child("Materials").props[0] if lem and lem.child("Materials") else [0]
        m = _geometric(by_id[mid]) if local else _matmul(world(mid), _geometric(by_id[mid]))
        verts = []
        for i in range(0, len(v), 3):
            x, y, z = v[i : i + 3]
            verts.append(tuple(m[r][0] * x + m[r][1] * y + m[r][2] * z + m[r][3] for r in range(3)))
        tris, tmat, poly, pi = [], [], [], 0
        for k in idx:
            if k < 0:
                poly.append(~k)
                mi = per_poly[pi] if pi < len(per_poly) else per_poly[0]
                name = mats[mi] if 0 <= mi < len(mats) else (mats[0] if mats else "")
                for j in range(1, len(poly) - 1):
                    tris.append((poly[0], poly[j], poly[j + 1]))
                    tmat.append(name)
                poly, pi = [], pi + 1
            else:
                poly.append(k)
        out.append(Mesh(_name(by_id[mid].props[1]), verts, tris, tmat, m))
    return Scene(up, unit, out)
