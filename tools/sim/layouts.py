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
    ego         the path the pass criterion asks of the vehicle, and whether it ends at a stop
    plan        Autoware's planned path, as it would be drawn on the road
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
"""

from __future__ import annotations

ROAD_KEYS = {
    "length",  # (y0, y1) of the main street
    "lane",  # lane width
    "parking",  # width of a parking strip on the ego side, 0 for none
    "sidewalk",  # sidewalk width
    "crosswalk",  # (y0, y1) of a marked crosswalk across the main street
    "stop_line",  # y of the ego lane's stop line; a sampled feature `no_stop_line` removes it
    "cross",  # a cross street: {"y": centre, "width": w, "sides": ["left", "right"]}
    "speed_sign",  # (x, y) of a posted limit sign, showing the sampled ODD-03 value
}

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
                "path": [(-1.75, 80.0), (-1.75, 20.0)],
                "move": (0, 1),
            },
        ],
        "hazard": (0.0, 23.0, 3.5, 27.0),
        "still": 0.8,
        "camera": {"pos": (-1.5, -8.0, 5.0), "look": (1.5, 24.0, 0.0), "lens": 28},
        "pick": {"ODD-13": "wet", "ODD-17": "congested"},
        "features": {"ODD-17": {"congested": ["queue"]}},
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
    },
}
