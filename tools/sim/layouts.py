"""Road layouts and choreography of the scenarios that tools/sim/scene.py can turn into a scene.

This file holds geometry only: where the road, the vehicle and the other road users are, in metres
(x to the right, y forward along the ego lane, z up, the frame of tools/readme/mesh.py), and how
they move during the clip. It holds no fact: every label, identifier, parameter value, safety goal
and ODD value comes from the records, through scene.py. The geometry is chosen to explain each
scenario, the way the sketches of WP-V-03 Figure 2-1 are, and is not a measurement or a result.

Motion is choreography: an actor goes along its path between two moments of the clip, given as
fractions of it (0 at the start, 1 at the end). No speed or acceleration of another road user is
stated anywhere, because the behaviour bounds that would give them (FSR-06.01, FSR-06.02) are not
fixed yet. When `stops` is set, the last point of the ego's path is where it stands still; scene.py
moves its first point back so that it cruises CRUISE_M at the sampled ODD-20 speed and then slows at
the firm level of FSR-03.02 to that point. The clip lasts as long as that takes.

A layout entry:
    road        the street and what is on it (see ROAD_KEYS)
    ego         the path the pass criterion asks of the vehicle, and whether it ends at a stop; one
                point when the scenario samples no speed and the vehicle stands throughout;
                `hold_s`, seconds it stands at the end (the clip's length when it stands
                throughout); `lights`, hazard, left or right, on from when it starts to slow (all
                the clip when it does not stop), or over `lights_m`, metres along its path
    plan        Autoware's planned path, as it would be drawn on the road; empty while it holds
    actors      the other road users: role (key: the one the scenario is about, other, parked),
                kind (a participant class of ODD-16, or `from: ODD-16` to take the sampled one),
                path, and the part of the clip in which it moves (`move`)
    hazard      where the hazard lies on the ground: a rectangle (x0, y0, x1, y1)
    still       the moment of the clip that the still shows, as a fraction of it
    camera      position, point looked at, lens in mm
    pick        concrete values chosen for categorical parameters instead of the seeded draw, so
                that a still shows the condition the scenario is about; scene.py refuses a value
                that is not one of the scenario's own
    features    scene parts that depend on a sampled value: {ODD-nn: {value: [part, ...]}}
    odd_limit   for a scenario that crosses the ODD boundary: where along y the drawing changes
                from inside the ODD to beyond its limit
    props       what the scenario puts on or beside the road (scene.PROPS): cones and barrier
                (from, to, n), work_sign, steam (at, r), debris (at, r), bay (a marked stopping
                place, from, to), bus_stop, paddle (at), door (side, and the clip fraction at
                which it opens; scene.py refuses one that opens before the vehicle stands)
    signal      the state of the signal on the ego's approach, red or green; the cross street shows
                the other; for a scenario whose description names it
    queue       where the stopped vehicles of the `queue` feature stand: (x, y, heading in degrees,
                0 along +y)
    variants    condition variants, LionDriver style: each a pick that overrides the layout's own,
                giving one more scene named <id>--<values>; the rest of the draw is unchanged
"""

from __future__ import annotations

import math

ROAD_KEYS = {
    "length",  # (y0, y1) of the main street
    "lane",  # lane width
    "parking",  # width of a parking strip on the ego side, 0 for none
    "sidewalk",  # sidewalk width
    "crosswalk",  # (y0, y1) of a marked crosswalk across the main street
    "stop_line",  # y of the ego lane's stop line; a sampled feature `no_stop_line` removes it
    "cross",  # a cross street: {"y": centre, "width": w, "sides": ["left", "right"]}
    "speed_sign",  # (x, y) of a posted limit sign, showing the sampled ODD-03 value
    "lanes",  # lanes in the ego's direction (1 if absent); the oncoming side has one
    "cycle_lane",  # width of a cycle lane on the ego side, between its lanes and the parking strip
    "roundabout",  # {"y": centre, "r": outer radius, "island": radius of the central island}
}

STREET = {"length": (-40, 120), "lane": 3.5, "parking": 0, "sidewalk": 3.0}
JUNCTION = {"y": 40.0, "width": 7.0, "sides": ["left", "right"]}


def circle(cy: float, r: float, a0: float, a1: float, step: float = 15.0) -> list:
    """Points of an arc about (0, cy), from angle a0 to a1 in degrees (counterclockwise)."""
    n = max(1, round(abs(a1 - a0) / step))
    return [
        (
            round(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), 2),
            round(cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 2),
        )
        for i in range(n + 1)
    ]


LAYOUTS: dict[str, dict] = {
    "SC-01": {
        "road": {
            "length": (-40, 110),
            "lane": 3.5,
            "parking": 0,
            "sidewalk": 3.5,
            "crosswalk": (30.0, 34.0),
            "stop_line": 28.0,
            "speed_sign": (4.4, 8.0),
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 25.2)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 100.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(5.8, 31.6), (-4.5, 32.4)],
                "move": (0.15, 1.0),
            },
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 70.0), (-1.75, 40.0)],
                "move": (0, 0.5),
            },
        ],
        "hazard": (0.0, 30.0, 3.5, 34.0),
        "still": 0.55,
        "camera": {"pos": (-1.5, -9.0, 5.5), "look": (1.0, 30.0, 0.0), "lens": 28},
        "pick": {"ODD-12": "night", "ODD-13": "wet"},
        "features": {"ODD-05": {"signalised-crosswalk": ["ped_signals"]}},
        "variants": [{"ODD-12": "day"}],
    },
    "SC-02": {
        "road": {
            "length": (-40, 110),
            "lane": 3.5,
            "parking": 2.5,
            "sidewalk": 3.0,
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 21.0)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 100.0)],
        "actors": [
            {"role": "parked", "kind": "van", "path": [(4.75, 24.0)]},
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(5.6, 27.6), (0.6, 27.6)],
                "move": (0.35, 1.0),
            },
            {"role": "other", "kind": "car", "path": [(4.75, 46.0)]},
        ],
        "occlusion": [(3.6, 21.6), (3.6, 26.4), (7.5, 32.0), (7.5, 21.6)],
        "hazard": (0.0, 25.0, 9.0, 30.0),
        "still": 0.6,
        "camera": {"pos": (-1.5, -8.0, 5.0), "look": (2.5, 26.0, 0.0), "lens": 28},
        "pick": {"ODD-16": "child", "ODD-12": "day"},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-03": {
        "road": {"length": (-40, 120), "lane": 3.5, "parking": 0, "sidewalk": 3.0},
        "ego": {"path": [(1.75, 0.0), (1.75, 21.0)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 100.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(1.75, 18.0), (1.75, 29.0)],
                "move": (0.0, 0.7),
            },
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 60.0), (-1.75, 20.0)],
                "move": (0, 1),
            },
        ],
        "hazard": (0.0, 23.0, 3.5, 27.0),
        "still": 0.8,
        "camera": {"pos": (-1.5, -8.0, 5.0), "look": (1.5, 24.0, 0.0), "lens": 28},
        "pick": {"ODD-13": "wet", "ODD-17": "congested"},
        "features": {"ODD-17": {"congested": ["queue"]}},
        "queue": [
            (1.75, 38.0, 0),
            (1.75, 45.5, 0),
            (-1.75, 12.0, 180),
            (-1.75, 4.0, 180),
            (-1.75, -4.0, 180),
        ],
    },
    "SC-06": {
        "road": {
            "length": (-40, 110),
            "lane": 3.5,
            "parking": 0,
            "sidewalk": 3.0,
            "stop_line": 26.0,
            "cross": {"y": 32.0, "width": 7.0, "sides": ["left", "right"]},
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 23.4)], "stops": True},
        "plan": [
            (1.75, 0.0),
            (1.75, 26.0),
            (1.2, 29.5),
            (-0.6, 32.4),
            (-3.4, 33.6),
            (-8.0, 33.75),
            (-40.0, 33.75),
        ],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(-1.75, 80.0), (-1.75, 6.0)],
                "move": (0.0, 1.0),
            },
        ],
        "hazard": (-3.5, 28.5, 0.0, 35.5),
        "still": 0.55,
        "camera": {"pos": (4.0, -6.0, 8.0), "look": (-2.0, 32.0, 0.0), "lens": 24},
        "pick": {"ODD-16": "motorcycle", "ODD-12": "dusk"},
        "variants": [{"ODD-12": "night"}],
        "features": {
            "ODD-04": {
                "signalised": ["signals"],
                "stop-controlled": ["stop_sign"],
                "unprotected-turn": ["no_stop_line"],
                "t-junction": ["t_left", "no_stop_line"],
            }
        },
    },
    "SC-14": {
        "road": {
            "length": (-40, 140),
            "lane": 3.5,
            "parking": 0,
            "sidewalk": 3.0,
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 40.0)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 130.0)],
        "actors": [
            {
                "role": "other",
                "kind": {"from": "ODD-16"},
                "path": [(-1.75, 90.0), (-1.75, 30.0)],
                "move": (0.0, 1.0),
            },
        ],
        "hazard": (0.0, 48.0, 3.5, 70.0),
        "odd_limit": 46.0,
        "still": 0.7,
        "camera": {"pos": (-1.5, -9.0, 5.0), "look": (1.0, 40.0, 0.0), "lens": 28},
        "pick": {"ODD-12": "dusk", "ODD-13": "wet", "ODD-16": "car"},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-04": {
        "road": STREET,
        "ego": {"path": [(1.75, 0.0), (1.75, 60.0)]},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(1.75, -10.0), (1.75, 50.0)],
                "move": (0.0, 1.0),
            },
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 90.0), (-1.75, -10.0)],
                "move": (0.0, 1.0),
            },
        ],
        "props": [{"kind": "steam", "at": (1.6, 30.0), "r": 1.5}],
        "hazard": (0.0, 28.0, 3.5, 32.0),
        "still": 0.42,
        "camera": {"pos": (-1.5, -9.0, 5.0), "look": (1.0, 28.0, 0.0), "lens": 28},
        "pick": {"ODD-13": "wet"},
    },
    "SC-05": {
        "road": STREET | {"stop_line": 35.5, "cross": JUNCTION},
        "ego": {"path": [(1.75, 0.0), (1.75, 32.8)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(25.0, 41.75), (-25.0, 41.75)],
                "move": (0.1, 1.0),
            },
        ],
        "signal": "green",
        "queue": [(-9.0, 38.25, -90), (-15.5, 38.25, -90)],
        "hazard": (0.0, 36.5, 3.5, 43.5),
        "still": 0.6,
        "camera": {"pos": (-1.5, -8.0, 6.0), "look": (1.0, 38.0, 0.0), "lens": 26},
        "pick": {"ODD-04": "signalised", "ODD-12": "day", "ODD-16": "car", "ODD-17": "congested"},
        "features": {
            "ODD-04": {"signalised": ["signals"], "protected-turn": ["signals"]},
            "ODD-17": {"congested": ["queue"]},
        },
        "variants": [{"ODD-12": "night"}, {"ODD-12": "low-sun"}],
    },
    "SC-07": {
        "road": STREET
        | {
            "stop_line": 28.6,
            "cross": JUNCTION,
            "roundabout": {"y": 40.0, "r": 11.0, "island": 5.0},
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 26.0)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 28.0)] + circle(40.0, 8.0, -70.0, 75.0) + [(1.75, 110.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": circle(40.0, 8.0, 120.0, 360.0),
                "move": (0.1, 0.95),
            },
        ],
        "hazard": (-3.5, 29.0, 3.5, 34.0),
        "still": 0.6,
        "camera": {"pos": (-2.0, -6.0, 8.0), "look": (0.0, 38.0, 0.0), "lens": 24},
        "pick": {"ODD-04": "roundabout-single", "ODD-16": "car", "ODD-17": "free-flow"},
    },
    "SC-08": {
        "road": STREET
        | {
            "cycle_lane": 1.5,
            "stop_line": 35.5,
            "cross": {"y": 40.0, "width": 7.0, "sides": ["right"]},
        },
        "ego": {"path": [(1.75, 0.0), (1.75, 32.8)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 34.0), (2.3, 36.3), (3.7, 37.8), (6.0, 38.25), (40.0, 38.25)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(4.25, 8.0), (4.25, 60.0)],
                "move": (0.0, 1.0),
            },
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 90.0), (-1.75, 0.0)],
                "move": (0.0, 1.0),
            },
        ],
        "hazard": (3.5, 30.0, 5.0, 40.0),
        "still": 0.4,
        "camera": {"pos": (-1.0, -8.0, 6.0), "look": (3.0, 34.0, 0.0), "lens": 26},
        "pick": {"ODD-04": "stop-controlled", "ODD-16": "bicycle"},
        "features": {"ODD-04": {"signalised": ["signals"], "stop-controlled": ["stop_sign"]}},
    },
    "SC-09": {
        "road": STREET | {"speed_sign": (4.4, 8.0)},
        "ego": {"path": [(1.75, 0.0), (1.75, 70.0)]},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "other",
                "kind": "truck",
                "path": [(-1.75, 100.0), (-1.75, -10.0)],
                "move": (0.0, 1.0),
            },
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 118.0), (-1.75, 30.0)],
                "move": (0.1, 1.0),
            },
        ],
        "hazard": (-0.4, 20.0, 0.4, 60.0),
        "still": 0.5,
        "camera": {"pos": (-1.5, -9.0, 5.0), "look": (1.0, 30.0, 0.0), "lens": 28},
        "pick": {"ODD-07": "markings-absent", "ODD-08": "none", "ODD-17": "free-flow"},
        "features": {"ODD-07": {"markings-absent": ["no_markings"]}},
        "variants": [{"ODD-07": "markings-visible"}],
    },
    "SC-10": {
        "road": STREET,
        "ego": {"path": [(1.75, 0.0), (1.75, 26.5)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 60.0), (-1.75, 10.0)],
                "move": (0.0, 1.0),
            },
        ],
        "props": [
            {"kind": "cones", "from": (3.3, 30.0), "to": (0.4, 42.0), "n": 9},
            {"kind": "barrier", "from": (0.3, 44.0), "to": (3.3, 44.0), "n": 3},
            {"kind": "work_sign", "at": (4.8, 29.0)},
        ],
        "hazard": (0.0, 30.0, 3.5, 46.0),
        "still": 0.75,
        "camera": {"pos": (-1.5, -8.0, 5.5), "look": (1.5, 32.0, 0.0), "lens": 28},
        "pick": {"ODD-12": "day"},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-11": {
        "road": STREET | {"stop_line": 35.5, "cross": JUNCTION},
        "ego": {"path": [(1.75, 0.0), (1.75, 32.8)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-19"},
                "path": [(0.6, 40.0)],
                "face": 180,
            },
        ],
        "props": [{"kind": "paddle", "at": (1.0, 39.9)}],
        "signal": "green",
        "hazard": (-3.5, 36.5, 3.5, 43.5),
        "still": 0.75,
        "camera": {"pos": (-1.5, -8.0, 5.5), "look": (1.0, 38.0, 0.0), "lens": 28},
        "pick": {"ODD-04": "signalised", "ODD-12": "day"},
        "features": {"ODD-04": {"signalised": ["signals"], "stop-controlled": ["stop_sign"]}},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-12": {
        "road": STREET | {"parking": 2.5, "cross": {"y": 62.0, "width": 7.0, "sides": ["left"]}},
        "ego": {
            "path": [
                (1.75, 0.0),
                (1.75, 20.0),
                (2.6, 23.5),
                (3.9, 26.5),
                (4.6, 29.0),
                (4.75, 31.0),
            ],
            "stops": True,
            "lights": "right",
            "hold_s": 2.0,
        },
        "plan": [(1.75, 0.0), (1.75, 20.0), (2.6, 23.5), (3.9, 26.5), (4.6, 29.0), (4.75, 31.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-18"},
                "path": [(-1.75, -15.0), (-1.75, 55.0)],
                "move": (0.3, 1.0),
            },
        ],
        "hazard": (-3.5, 20.0, 0.0, 45.0),
        "still": 0.8,
        "camera": {"pos": (-3.0, -8.0, 6.0), "look": (1.0, 28.0, 0.0), "lens": 26},
        "pick": {"ODD-17": "free-flow", "ODD-04": "t-junction"},
    },
    "SC-13": {
        "road": STREET,
        "ego": {"path": [(1.75, 0.0), (1.75, 35.0)], "stops": True},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {"role": "key", "kind": {"from": "ODD-16"}, "path": [(1.9, 40.0)], "lying": True},
            {
                "role": "other",
                "kind": "car",
                "path": [(-1.75, 70.0), (-1.75, 20.0)],
                "move": (0.0, 1.0),
            },
        ],
        "props": [{"kind": "debris", "at": (1.0, 42.0), "r": 0.7}],
        "hazard": (0.3, 38.5, 3.2, 43.0),
        "still": 0.8,
        "camera": {"pos": (-1.5, -8.0, 5.0), "look": (1.5, 38.0, 0.0), "lens": 28},
        "pick": {"ODD-16": "e-scooter", "ODD-12": "day"},
        "variants": [{"ODD-12": "night"}, {"ODD-12": "unlit"}],
    },
    "SC-15": {
        "road": STREET | {"parking": 2.5},
        "ego": {
            "path": [
                (1.75, 0.0),
                (1.75, 18.0),
                (2.9, 22.0),
                (4.2, 26.0),
                (4.7, 28.5),
                (4.75, 30.0),
            ],
            "stops": True,
            "hold_s": 7.0,
        },
        "plan": [(1.75, 0.0), (1.75, 18.0), (2.9, 22.0), (4.2, 26.0), (4.7, 28.5), (4.75, 30.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(8.2, 28.2), (7.0, 28.6), (6.2, 28.95)],
                "move": (0.72, 0.95),
            },
            {"role": "other", "kind": "pedestrian", "path": [(6.6, 26.4)]},
        ],
        "props": [
            {"kind": "bay", "from": (3.65, 23.0), "to": (5.9, 36.0)},
            {"kind": "door", "side": "right", "open": 0.66},
        ],
        "hazard": (3.4, 26.0, 7.5, 34.5),
        "still": 0.86,
        "camera": {"pos": (-1.5, -6.0, 6.0), "look": (4.0, 29.0, 0.0), "lens": 26},
        "pick": {"ODD-16": "pedestrian"},
    },
    "SC-16": {
        "road": STREET
        | {
            "crosswalk": (34.0, 37.0),
            "stop_line": 32.0,
            "cross": {"y": 44.0, "width": 7.0, "sides": ["left", "right"]},
        },
        "ego": {"path": [(1.75, 29.4)], "stops": True, "hold_s": 9.0},
        "plan": [],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(5.6, 34.8), (-5.0, 35.2)],
                "move": (0.05, 0.95),
            },
            {
                "role": "other",
                "kind": "pedestrian",
                "path": [(-5.2, 36.6), (5.6, 36.3)],
                "move": (0.15, 1.0),
            },
        ],
        "signal": "red",
        "hazard": (0.0, 34.0, 3.5, 37.0),
        "still": 0.45,
        "camera": {"pos": (-1.5, 18.0, 5.0), "look": (1.0, 36.0, 0.0), "lens": 28},
        "pick": {"ODD-04": "signalised", "ODD-05": "signalised-crosswalk", "ODD-16": "child"},
        "features": {
            "ODD-04": {"signalised": ["signals"]},
            "ODD-05": {"signalised-crosswalk": ["ped_signals"]},
        },
    },
    "SC-17": {
        "road": STREET,
        "ego": {
            "path": [(1.75, 0.0), (1.75, 40.0)],
            "stops": True,
            "lights": "hazard",
            "hold_s": 8.0,
        },
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "other",
                "kind": "car",
                "path": [(1.75, 24.0), (-1.75, 31.0), (-1.75, 50.0), (1.75, 58.0), (1.75, 70.0)],
                "move": (0.65, 1.0),
            },
        ],
        "hazard": (-3.5, 34.0, 0.0, 46.0),
        "still": 0.8,
        "camera": {"pos": (-3.0, -8.0, 5.5), "look": (0.5, 38.0, 0.0), "lens": 26},
        "pick": {"ODD-17": "free-flow", "ODD-12": "day"},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-18": {
        "road": STREET | {"parking": 2.5, "cycle_lane": 1.5},
        "ego": {
            "path": [
                (1.75, 0.0),
                (1.75, 16.0),
                (3.3, 21.5),
                (5.2, 26.0),
                (6.1, 29.0),
                (6.25, 31.0),
            ],
            "stops": True,
            "lights": "right",
        },
        "plan": [(1.75, 0.0), (1.75, 16.0), (3.3, 21.5), (5.2, 26.0), (6.1, 29.0), (6.25, 31.0)],
        "actors": [
            {"role": "other", "kind": {"from": "ODD-18"}, "path": [(6.25, 52.0)]},
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(4.25, 20.0), (4.25, 45.0)],
                "move": (0.0, 1.0),
            },
        ],
        "props": [
            {"kind": "bay", "from": (5.15, 23.0), "to": (7.4, 37.0)},
            {"kind": "bus_stop", "at": (8.0, 47.0)},
        ],
        "hazard": (3.5, 16.0, 5.0, 30.0),
        "still": 0.7,
        "camera": {"pos": (-1.0, -6.0, 6.5), "look": (4.5, 30.0, 0.0), "lens": 26},
        "pick": {"ODD-05": "cycle-lane", "ODD-16": "bicycle"},
    },
    "SC-19": {
        "road": STREET,
        "ego": {"path": [(1.75, 30.0)], "stops": True, "lights": "hazard"},
        "plan": [],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(-1.3, 18.0), (-1.3, 42.0)],
                "move": (0.05, 0.7),
            },
        ],
        "props": [{"kind": "door", "side": "left", "open": 0.72}],
        "hazard": (-3.0, 26.5, 0.0, 33.5),
        "still": 0.38,
        "camera": {"pos": (-3.0, 18.0, 5.0), "look": (0.0, 32.0, 0.0), "lens": 26},
        "pick": {"ODD-16": "bicycle", "ODD-12": "day"},
        "variants": [{"ODD-12": "night"}],
    },
    "SC-22": {
        "road": STREET | {"lanes": 2},
        "ego": {
            "path": [
                (5.25, 0.0),
                (5.25, 20.0),
                (4.4, 25.0),
                (2.6, 30.5),
                (1.75, 35.0),
                (1.75, 75.0),
            ],
            "lights": "left",
            "lights_m": (0.0, 36.0),
        },
        "plan": [(5.25, 0.0), (5.25, 20.0), (4.4, 25.0), (2.6, 30.5), (1.75, 35.0), (1.75, 110.0)],
        "actors": [
            {"role": "parked", "kind": "van", "path": [(5.25, 44.0)]},
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(1.75, -22.0), (1.75, 50.0)],
                "move": (0.0, 1.0),
            },
        ],
        "hazard": (0.0, 24.0, 3.5, 38.0),
        "still": 0.45,
        "camera": {"pos": (1.5, -8.0, 6.0), "look": (3.0, 30.0, 0.0), "lens": 26},
        "pick": {"ODD-16": "car"},
    },
    "SC-23": {
        "road": STREET | {"stop_line": 35.5, "cross": JUNCTION},
        "ego": {"path": [(1.75, 0.0), (1.75, 32.8)], "stops": True, "hold_s": 2.0},
        "plan": [(1.75, 0.0), (1.75, 110.0)],
        "actors": [
            {
                "role": "key",
                "kind": {"from": "ODD-16"},
                "path": [(9.0, 41.75), (-14.0, 41.75)],
                "move": (0.35, 1.0),
            },
        ],
        "hazard": (-3.5, 36.5, 3.5, 43.5),
        "still": 0.62,
        "camera": {"pos": (-1.5, -8.0, 6.0), "look": (1.0, 38.0, 0.0), "lens": 26},
        "pick": {"ODD-04": "stop-controlled", "ODD-16": "car"},
        "features": {"ODD-04": {"stop-controlled": ["stop_sign"]}},
    },
}
