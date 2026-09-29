"""Group C of the 50-bug expansion: beetles, hoppers, the mantis, water bugs and friends.

Same conventions as bugs.py (faces north / -Z, feet on y=0). Texture face orientation (checked in Blockbench):
    up:    row 0 = rear (+Z), column 0 = +X  -> use top() to author a head-up top view
    north: row 0 = top,  column 0 = +X
    east:  row 0 = top,  column 0 = rear; west: column 0 = front
"""
import math
import random

from bugs import *  # noqa: F401,F403

CLEAR = "#00000000"  # a px colour that punches a transparent hole


def top(rows):
    """Author an 'up' face as a head-up top view (row 0 = front, left = -X); returns the face's own row order."""
    return [r[::-1] for r in rows[::-1]]


def speck(w, h, colors, count, seed, avoid=()):
    """Random detail pixels (marbling, hairs, bumps) on a w x h face."""
    rnd = random.Random(seed)
    out = []
    for _ in range(count):
        x, y = rnd.randrange(w), rnd.randrange(h)
        if (x, y) in avoid:
            continue
        out.append([x, y, rnd.choice(colors)])
    return out


def legs_hold(v, n=3, prefix="leg"):
    return {f"{prefix}_{s}{i}": {"rotation": hold(v)} for s in "lr" for i in range(1, n + 1)}


def _rot(v, r):
    """Blockbench bone rotation (X, then Y, then Z; degrees) applied to a vector."""
    x, y, z = v
    ax, ay, az = (math.radians(a) for a in r)
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return [x, y, z]




def legs2g(parent, hips, femur, paint, thick=1, fan=(30, 0, -30), lift=20, splay=15, prefix="leg",
           tibia_paint=None, ground=-0.1, inflate=0.0, fpaint=None):
    """Like bugs.legs2 (same bone names), but each tibia is sized so its foot lands on `ground`.
    inflate < 0 makes thin legs (the target is lowered to compensate). Parent must have no rest rotation."""
    out = []
    for i, (hx, hy, hz) in enumerate(hips, start=1):
        yaw = fan[i - 1] if i - 1 < len(fan) else 0
        for side, sx in (("l", 1), ("r", -1)):
            rf = [0, sx * yaw, sx * lift]
            rk = [0, 0, sx * splay - sx * lift]
            fo = [hx if sx > 0 else -hx - femur, hy - thick / 2, hz - thick / 2]
            out.append(B(f"{prefix}_{side}{i}", [sx * hx, hy, hz],
                         [C(fo, [femur, thick, thick], fpaint or paint, inflate=inflate)], parent=parent, rot=rf))
            kx = sx * (hx + femur - thick / 2)
            knee_y = hy + _rot([kx - sx * hx, 0, 0], rf)[1]
            down = _rot(_rot([0, -1, 0], rk), rf)
            corner = min(_rot(_rot([a * thick / 2, 0, b * thick / 2], rk), rf)[1] for a in (-1, 1) for b in (-1, 1))
            need = (ground + inflate - knee_y - corner) / down[1]
            ln = max(1, round(need))
            to = [kx - thick / 2, hy - need, hz - thick / 2]
            out.append(B(f"knee_{side}{i}", [kx, hy, hz], [C(to, [thick, ln, thick], tibia_paint or paint, inflate=inflate)],
                         parent=f"{prefix}_{side}{i}", rot=rk))
    return out


def thin(bones, inflate=-0.25):
    """Make every cube of these bones a thinner rod (negative inflate)."""
    for b in bones:
        for c in b["cubes"]:
            c["inflate"] = inflate
    return bones


def antennae2(parent, x, y, z, length, paint, up=25, out=20, name="antenna", inflate=-0.3, tip=None):
    """Thin rod antennae (1x1 box shrunk by inflate), splayed outward; same bone names as bugs.antennae. tip: club paint."""
    res = []
    for side, sx in (("l", 1), ("r", -1)):
        cubes = [C([sx * x - 0.5, y - 0.5, z - length], [1, 1, length], paint, inflate=inflate)]
        if tip:
            cubes.append(C([sx * x - 0.5, y - 0.5, z - length - 0.5], [1, 1, 1], tip, inflate=-0.22))
        res.append(B(f"{name}_{side}", [sx * x, y, z], cubes, parent=parent, rot=[up, -sx * out, 0]))
    return res


def banded(c, c2):
    """Banded rod paint: bands run across the rod's length on every face."""
    return P(c, "vstripe", c2=c2, per=2, faces={"up": {"pat": "stripe"}, "down": {"pat": "stripe"}})


# ================================================================ COMMON

def grasshopper():
    G, GL, GD, Y = "#6cc644", "#92e060", "#4f9e2f", "#f2de4e"
    eye = P("#9a7440", n=4, faces={"east": {"px": [[-1, 0, "#f6f0d0"], [0, 1, "#3a2a16"]]},
                                   "west": {"px": [[0, 0, "#f6f0d0"], [-1, 1, "#3a2a16"]]},
                                   "north": {"px": [[0, 0, "#3a2a16"]]}})
    wing = P("#5fae3c", "vstripe", c2="#4a922d", per=2, n=6,
             faces={"up": {"px": [[0, 1, "#3f7f26"], [1, 3, "#3f7f26"], [0, 5, "#3f7f26"]]},
                    "east": {"pat": "solid"}, "west": {"pat": "solid"}})
    chevron = [[x, (x % 2), "#4f9e2f"] for x in range(4)]
    femur = P(G, hl=True, faces={"down": {"c": Y}, "east": {"px": chevron}, "west": {"px": chevron}})
    shin = P("#86b83c", faces={"down": {"px": [[0, y, "#3a4a18"] for y in range(0, 6, 2)]}})
    bones = [
        B("body", [0, 3, 0], [
            C([-1.5, 1.5, -3], [3, 3, 3], P(G, "grad", c2=Y, hl=True, faces={"up": {"pat": "solid", "c": GL, "px": col(1, 3, "#b0f07c")},
                                                                         "down": {"pat": "solid", "c": Y}}), name="pronotum"),
            C([-1.5, 1.5, 0], [3, 2, 5], P(G, "grad", c2=Y, faces={"up": {"pat": "stripe", "c": G, "c2": GD},
                                                                  "down": {"pat": "stripe", "c": Y, "c2": "#d4c040"}})),
            C([-1, 1.5, 5], [2, 2, 1], P(Y, faces={"up": {"c": G}})),
        ]),
        B("head", [0, 3.5, -3], [
            C([-1.5, 1.5, -5], [3, 3, 2], P(G, hl=True, faces={
                "north": {"px": [[1, 0, GL], [0, 2, GD], [1, 2, "#c9b23a"], [2, 2, GD]]}})),
            C([-1, 1, -5], [2, 1, 1], P("#b9b03a")),
            C([1, 2.5, -4.5], [1, 2, 1], eye),
            C([-2, 2.5, -4.5], [1, 2, 1], eye),
        ], parent="body"),
        B("wing_l", [0, 3.8, -1], [C([0, 3.3, -1.5], [2, 1, 8], wing)], parent="body", rot=[-2, 0, -14]),
        B("wing_r", [0, 3.8, -1], [C([-2, 3.3, -1.5], [2, 1, 8], wing, mirror=True)], parent="body", rot=[-2, 0, 14]),
        # big jumping legs: femur up and back, tibia folded down under it
        B("hind_l", [2, 2.8, 0.5], [C([1.5, 1.8, 0.5], [1, 2, 4], femur), C([1.5, 2.3, 4.5], [1, 1, 1], P(G)),
                                     C([1.5, 2.3, 5.5], [1, 1, 1], P("#3d5a22"), inflate=-0.05)],
          parent="body", rot=[-22, 8, 0]),
        B("hshin_l", [2, 2.8, 6], [C([1.5, 2.3, 0], [1, 1, 6], shin, inflate=-0.2)], parent="hind_l", rot=[-29, 0, 0]),
        B("hind_r", [-2, 2.8, 0.5], [C([-2.5, 1.8, 0.5], [1, 2, 4], femur, mirror=True), C([-2.5, 2.3, 4.5], [1, 1, 1], P(G)),
                                      C([-2.5, 2.3, 5.5], [1, 1, 1], P("#3d5a22"), inflate=-0.05)],
          parent="body", rot=[-22, -8, 0]),
        B("hshin_r", [-2, 2.8, 6], [C([-2.5, 2.3, 0], [1, 1, 6], shin, mirror=True, inflate=-0.2)], parent="hind_r", rot=[-29, 0, 0]),
    ]
    bones += antennae2("head", 0.5, 4.3, -4.8, 4, P("#7a8a36"), up=35, out=22)
    bones += legs2g("body", [(1.3, 2.2, -2.4), (1.4, 2.2, -0.9)], 2, P("#5ca838"), fan=(30, -10), lift=25, splay=15, inflate=-0.2)
    hop = merge(
        {"hind_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.07, [-4, 0, 0]), kf(0.15, [16, 0, 0]), kf(0.32, [8, 0, 0]), kf(0.5, [0, 0, 0])]},
         "hind_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.07, [-4, 0, 0]), kf(0.15, [16, 0, 0]), kf(0.32, [8, 0, 0]), kf(0.5, [0, 0, 0])]},
         "hshin_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.07, [8, 0, 0]), kf(0.15, [-115, 0, 0]), kf(0.32, [-60, 0, 0]), kf(0.5, [0, 0, 0])]},
         "hshin_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.07, [8, 0, 0]), kf(0.15, [-115, 0, 0]), kf(0.32, [-60, 0, 0]), kf(0.5, [0, 0, 0])]},
         "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.07, [-4, 0, 0]), kf(0.15, [14, 0, 0]), kf(0.35, [4, 0, 0]), kf(0.5, [0, 0, 0])],
                  "position": [kf(0, [0, 0, 0]), kf(0.07, [0, -0.6, 0]), kf(0.15, [0, 0.5, 0]), kf(0.5, [0, 0, 0])]}},
        {f"leg_{s}{i}": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [35, 0, 0]), kf(0.38, [35, 0, 0]), kf(0.5, [0, 0, 0])]} for s in "lr" for i in (1, 2)},
        antenna_idle(0.5, 14))
    idle = merge(antenna_idle(3, 10), bob("body", 3, 0.12),
                 {"hind_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.0, [0, 0, 0]), kf(2.1, [-6, 0, 0]), kf(2.2, [0, 0, 0]),
                                          kf(2.3, [-6, 0, 0]), kf(2.4, [0, 0, 0]), kf(3, [0, 0, 0])]},
                  "hind_r": {"rotation": [kf(0, [0, 0, 0]), kf(2.05, [0, 0, 0]), kf(2.15, [-6, 0, 0]), kf(2.25, [0, 0, 0]),
                                          kf(2.35, [-6, 0, 0]), kf(2.45, [0, 0, 0]), kf(3, [0, 0, 0])]}})
    walk = merge(tripod_walk(0.4, 22, 10, n=2), antenna_idle(0.4, 8),
                 {"hind_l": {"rotation": cycle(0.4, [[4, 3, 0], [-3, -3, 0]])},
                  "hind_r": {"rotation": cycle(0.4, [[-3, 3, 0], [4, -3, 0]])}})
    return {"id": "grasshopper", "seed": 101, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.4, "bones": walk},
        "hop": {"len": 0.5, "loop": False, "bones": hop},
    }}


def springtail():
    L, Ld, Lh, K = "#aaa6dc", "#7f86bc", "#dcd9f6", "#1e1c30"
    blob = P(L, hl=True, n=6)
    blob_up = dict(blob, faces={"up": {"px": [[0, 0, Lh], [1, 1, Ld], [2, 0, Lh]]}})
    fork = [".L.", "L.L", "L.L"]
    fork_px = [[x, y, CLEAR] for y, r in enumerate(top(fork)) for x, ch in enumerate(r) if ch == "."]
    bones = [
        B("body", [0, 1.8, 0], [
            C([-1.5, 1.3, 0], [3, 2, 2], blob, name="abdomen"),
            C([-1, 0.8, 0], [2, 3, 2], blob_up),
            C([-1, 1.3, -0.5], [2, 2, 3], dict(blob, faces={"east": {"px": [[1, 0, Lh]]}, "west": {"px": [[1, 1, Lh]]}})),
            C([-1, 1, -1.5], [2, 2, 1], P("#9895d0", hl=True)),
        ]),
        B("head", [0, 2, -1.5], [
            C([-1, 1.1, -2.5], [2, 2, 1], P("#9290cc", hl=True, faces={"east": {"px": [[0, 0, K]]}, "west": {"px": [[0, 0, K]]},
                                                                     "north": {"px": [[0, 1, "#b8b5e4"], [1, 1, "#b8b5e4"]]}})),
        ], parent="body"),
        B("furca", [0, 0.7, 2.3], [C([-1.5, 0.7, -0.7], [3, 0, 3], P("#c9c6ec", n=4, px=fork_px))], parent="body"),
    ]
    bones += antennae2("head", 0.5, 2.8, -2.4, 2, banded("#5d5a90", "#9a97cc"), up=40, out=28, inflate=-0.3)
    bones += thin(legs("body", [(0.8, 1.2, -1.2), (0.9, 1.2, -0.3), (0.9, 1.2, 0.7)], 2, P("#8a88c0"), fan=[30, 5, -25]), -0.3)
    hop = {"furca": {"rotation": [kf(0, [0, 0, 0]), kf(0.05, [-170, 0, 0]), kf(0.3, [-170, 0, 0]), kf(0.45, [0, 0, 0])]},
           "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.05, [6, 0, 0]), kf(0.15, [-120, 0, 0]), kf(0.3, [-260, 0, 0]), kf(0.42, [-360, 0, 0]), kf(0.5, [-360, 0, 0])],
                    "position": [kf(0, [0, 0, 0]), kf(0.05, [0, 0.3, 0]), kf(0.15, [0, 2.5, 0]), kf(0.3, [0, 2.5, 0]), kf(0.42, [0, 0.4, 0]), kf(0.5, [0, 0, 0])]}}
    return {"id": "springtail", "seed": 102, "bones": bones, "anims": {
        "idle": {"len": 2.5, "bones": merge(antenna_idle(2.5, 12), bob("body", 2.5, 0.1))},
        "walk": {"len": 0.3, "bones": merge(tripod_walk(0.3, 20, 10), antenna_idle(0.3, 8))},
        "hop": {"len": 0.5, "loop": False, "bones": hop},
    }}


def whirligig_beetle():
    shell = P("#121216", "iri", c2="#4d4128", j=0.12, hl=True, n=6)
    eye_t, eye_b = "#8a93a2", "#4d5563"
    bones = [
        B("body", [0, 1.2, 0], [
            C([-2, 0.3, -2], [4, 2, 4], shell),
            C([-1.5, 0.3, 2], [3, 2, 1], shell),
            C([-1.5, 2.3, -1.5], [3, 1, 3], dict(shell, faces={"up": {"px": [[2, 2, "#e9eef5"], [1, 2, "#8a7a56"], [2, 1, "#8a7a56"]]}})),
            C([-1.5, 0.3, -3], [3, 2, 1], dict(shell, faces={"up": {"px": [[0, 0, eye_t], [2, 0, eye_t]]},
                                                            "down": {"px": [[0, 0, eye_b], [2, 0, eye_b]]},
                                                            "east": {"px": [[0, 0, eye_t], [0, 1, eye_b]]},
                                                            "west": {"px": [[0, 0, eye_t], [0, 1, eye_b]]}}),
              name="head"),
            C([-1.5, 0.2, -2], [3, 0, 4], P("#2a241a")),
        ]),
        # long grasping front legs held forward along the head
        B("arm_l", [1.2, 0.9, -2], [C([1.2, 0.4, -3], [3, 1, 1], P("#1c1a18"), inflate=-0.25)], parent="body", rot=[0, 55, 0]),
        B("arm_r", [-1.2, 0.9, -2], [C([-4.2, 0.4, -3], [3, 1, 1], P("#1c1a18"), inflate=-0.25)], parent="body", rot=[0, -55, 0]),
    ]
    paddle = P("#4a3a22", "edge", c2="#8c7a4c", n=6)
    bones += legs("body", [(1.8, 0.8, 0.4), (1.8, 0.8, 1.6)], 2, paddle, thick=0, sz=1, down=8, fan=[-15, -40])
    row_ = {"leg_l1": {"rotation": cycle(0.16, [[0, 25, 0], [0, -30, 0]])},
            "leg_r1": {"rotation": cycle(0.16, [[0, -25, 0], [0, 30, 0]])},
            "leg_l2": {"rotation": cycle(0.16, [[0, -30, 0], [0, 25, 0]])},
            "leg_r2": {"rotation": cycle(0.16, [[0, 30, 0], [0, -25, 0]])}}
    idle = merge(bob("body", 2, 0.15), sway("body", 2, 3, axis=2),
                 {"leg_l2": {"rotation": [kf(0, [0, 0, 0]), kf(1.4, [0, 0, 0]), kf(1.5, [0, 20, 0]), kf(1.6, [0, 0, 0]), kf(2, [0, 0, 0])]},
                  "leg_r2": {"rotation": [kf(0, [0, 0, 0]), kf(1.4, [0, 0, 0]), kf(1.5, [0, -20, 0]), kf(1.6, [0, 0, 0]), kf(2, [0, 0, 0])]}})
    walk = merge(row_, {"body": {"rotation": cycle(0.32, [[0, 0, 4], [0, 0, -4]]),
                                 "position": cycle(0.16, [[0, 0, 0], [0, 0.15, 0]])}})
    return {"id": "whirligig_beetle", "seed": 103, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": idle},
        "walk": {"len": 0.32, "bones": walk},
    }}


def stink_bug():
    base, dark, light, cream, mem = "#7b6650", "#57473a", "#9c8a70", "#e0d0a6", "#3d3027"
    marble = ["#6a5543", "#8c775e", "#62503f"]

    def plate(w, d, seed, extra=()):
        return P(base, "vstripe", c2=cream, per=2, n=8, faces={
            "up": {"pat": "solid", "px": speck(w, d, marble, max(1, w * d // 3), seed) + list(extra)},
            "down": {"pat": "solid", "c": "#b8a78a"},
            "north": {"pat": "solid"}, "south": {"pat": "solid"}})

    scut = ["wSSSw", ".SSS.", ".SsS.", "..s.."]
    scut_pal = {"s": "#e2cfa4", "S": "#c9b38c", "w": "#f2e6c4"}
    scut_px = grid(top(scut), scut_pal) + [[x, y, CLEAR] for y, r in enumerate(top(scut)) for x, ch in enumerate(r) if ch == "."]
    bones = [
        B("body", [0, 1.8, 0], [
            C([-2, 0.8, -3], [4, 2, 1], plate(4, 1, 1), name="pronotum"),
            C([-3, 0.8, -2], [6, 2, 1], plate(6, 1, 2, [[0, 0, "#3a2e24"], [5, 0, "#3a2e24"]])),
            C([-3, 0.8, -1], [6, 2, 2], plate(6, 2, 3)),
            C([-2.5, 0.8, 1], [5, 2, 1], plate(5, 1, 4)),
            C([-2, 0.8, 2], [4, 2, 1], dict(plate(4, 1, 5), faces={"up": {"pat": "solid", "c": mem, "px": [[1, 0, "#57463a"]]},
                                                                   "down": {"pat": "solid", "c": "#b8a78a"}})),
            C([-1, 0.8, 3], [2, 1, 1], P(mem)),
            C([-2.5, 2.86, -1], [5, 0, 4], P("#c9b38c", n=4, px=scut_px), name="scutellum"),
        ]),
        B("head", [0, 1.8, -3], [
            C([-1, 1.2, -4], [2, 1, 1], P("#6a5644", faces={"up": {"px": [[0, 1, dark]]}})),
            C([0.9, 1.3, -3.9], [1, 1, 1], P("#6a2016"), inflate=-0.2),
            C([-1.9, 1.3, -3.9], [1, 1, 1], P("#6a2016"), inflate=-0.2),
        ], parent="body"),
    ]
    bones += antennae2("head", 0.6, 1.8, -3.9, 4, banded("#3a2e24", cream), up=15, out=30)
    bones += legs2g("body", [(1.8, 1.2, -1.8), (2.3, 1.2, -0.3), (2, 1.2, 1.3)], 2, P("#8a7560", "stripe", c2="#5c4a38", per=2),
                    fan=(40, 5, -35), lift=15, splay=22, inflate=-0.2)
    spray = merge({"body": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [-14, 0, 0]), kf(0.2, [-14, 0, 3]), kf(0.28, [-14, 0, -3]),
                                         kf(0.36, [-14, 0, 3]), kf(0.44, [-14, 0, -3]), kf(0.6, [0, 0, 0])],
                            "position": [kf(0, [0, 0, 0]), kf(0.12, [0, 0.4, 0]), kf(0.44, [0, 0.4, 0]), kf(0.6, [0, 0, 0])]},
                   "antenna_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [15, -25, 0]), kf(0.44, [15, -25, 0]), kf(0.6, [0, 0, 0])]},
                   "antenna_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [15, 25, 0]), kf(0.44, [15, 25, 0]), kf(0.6, [0, 0, 0])]}})
    return {"id": "stink_bug", "seed": 104, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 10), bob("body", 3, 0.1))},
        "walk": {"len": 0.45, "bones": merge(tripod_walk(0.45, 20, 10), antenna_idle(0.45, 8))},
        "spray": {"len": 0.6, "loop": False, "bones": spray},
    }}


# ================================================================ UNCOMMON

def praying_mantis():
    G, GL, GD = "#7cc24a", "#a4da6e", "#5a9a36"
    eye = P("#d8f0a0", n=4, faces={"north": {"px": [[0, 1, "#26341a"]]}, "east": {"px": [[-1, 1, "#26341a"]]},
                                   "west": {"px": [[0, 1, "#26341a"]]}})
    spines = [[0, y, "#eef8cc"] for y in range(0, 4, 2)]
    arm = P(GL, hl=True, faces={"west": {"px": spines}, "east": {"px": spines}})
    wing = P("#8dcf58", "vstripe", c2="#6fae44", per=3, n=6, faces={"up": {"px": [[0, 3, "#e7f2c8"], [-1, 3, "#e7f2c8"]]}})
    bones = [
        B("body", [0, 2.5, 0], [
            C([-1, 1.5, -1], [2, 2, 2], P(G, hl=True)),
            C([-1.5, 1.5, 1], [3, 2, 4], P(G, "stripe", c2=GD, per=2, faces={"up": {"pat": "solid"}})),
            C([-1, 1.5, 5], [2, 2, 2], P(G, "stripe", c2=GD, per=2)),
            C([-0.5, 2, 7], [1, 1, 1], P(GD)),
        ]),
        B("wings", [0, 3.55, 0], [C([0, 3.55, 0], [2, 0, 7], wing, r=[0, 0, -12], p=[0, 3.55, 0]),
                                   C([-2, 3.55, 0], [2, 0, 7], wing, mirror=True, r=[0, 0, 12], p=[0, 3.55, 0])], parent="body"),
        # long raised prothorax
        B("thorax", [0, 2.5, -1], [C([-0.5, 2, -6], [1, 1, 5], P(G, hl=True)),
                                    C([-1, 2, -6], [2, 1, 1], P(GL))], parent="body", rot=[42, 0, 0]),
        B("head", [0, 2.5, -6], [
            C([-1, 2.5, -7], [2, 2, 1], P(G, hl=True, faces={"north": {"px": [[0, 1, GL], [1, 1, GL]]}})),
            C([1, 3, -7.2], [1, 2, 1], eye),
            C([-2, 3, -7.2], [1, 2, 1], eye),
            C([-0.5, 1.5, -7], [1, 1, 1], P("#b8c85a")),
        ], parent="thorax", rot=[-30, 0, 0]),
        # raptorial legs: femur hanging, tibia folded up in front of it
        B("arm_l", [1, 2.2, -5.5], [C([0.5, -1.8, -6], [1, 4, 1], arm)], parent="thorax", rot=[0, 0, -6]),
        B("claw_l", [1, -1.8, -6], [C([0.5, -1.8, -7], [1, 3, 1], P(G)), C([0.5, 0.9, -7.6], [1, 1, 1], P(GD), inflate=-0.2)], parent="arm_l"),
        B("arm_r", [-1, 2.2, -5.5], [C([-1.5, -1.8, -6], [1, 4, 1], arm, mirror=True)], parent="thorax", rot=[0, 0, 6]),
        B("claw_r", [-1, -1.8, -6], [C([-1.5, -1.8, -7], [1, 3, 1], P(G)), C([-1.5, 0.9, -7.6], [1, 1, 1], P(GD), inflate=-0.2)], parent="arm_r"),
    ]
    bones += antennae2("head", 0.4, 4.4, -7, 6, P("#6a8a3a"), up=45, out=22, inflate=-0.35)
    bones += legs2g("body", [(1, 2, -0.5), (1.3, 2, 0.8)], 4, P(GD), fan=(40, -45), lift=30, splay=25, inflate=-0.25)
    strike = {
        "arm_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.08, [25, 0, 0]), kf(0.15, [100, 0, 0]), kf(0.24, [70, 0, 0]), kf(0.55, [0, 0, 0])]},
        "arm_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.08, [25, 0, 0]), kf(0.15, [100, 0, 0]), kf(0.24, [70, 0, 0]), kf(0.55, [0, 0, 0])]},
        "claw_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.08, [-110, 0, 0]), kf(0.15, [-80, 0, 0]), kf(0.22, [0, 0, 0]), kf(0.55, [0, 0, 0])]},
        "claw_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.08, [-110, 0, 0]), kf(0.15, [-80, 0, 0]), kf(0.22, [0, 0, 0]), kf(0.55, [0, 0, 0])]},
        "thorax": {"rotation": [kf(0, [0, 0, 0]), kf(0.08, [8, 0, 0]), kf(0.15, [-18, 0, 0]), kf(0.3, [-10, 0, 0]), kf(0.55, [0, 0, 0])]},
        "head": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [16, 0, 0]), kf(0.3, [10, 0, 0]), kf(0.55, [0, 0, 0])]},
        "body": {"position": [kf(0, [0, 0, 0]), kf(0.15, [0, 0, -1.2]), kf(0.35, [0, 0, -0.8]), kf(0.55, [0, 0, 0])]},
    }
    idle = merge(antenna_idle(4, 10), sway("body", 4, 2.5, axis=2),
                 {"head": {"rotation": [kf(0, [0, 0, 0]), kf(1.0, [0, 0, 0]), kf(1.3, [0, 22, 0]), kf(2.4, [0, 22, 0]),
                                        kf(2.7, [0, -14, 0]), kf(3.5, [0, -14, 0]), kf(4, [0, 0, 0])]}})
    walk = merge(tripod_walk(0.6, 20, 10, n=2), sway("body", 0.6, 2, axis=2), antenna_idle(0.6, 6),
                 {"arm_l": {"rotation": cycle(0.6, [[4, 0, 0], [-4, 0, 0]])}, "arm_r": {"rotation": cycle(0.6, [[-4, 0, 0], [4, 0, 0]])}})
    return {"id": "praying_mantis", "seed": 105, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": idle},
        "walk": {"len": 0.6, "bones": walk},
        "strike": {"len": 0.55, "loop": False, "bones": strike},
    }}


def bombardier_beetle():
    O, K, Y, leg = "#e0782a", "#1e2440", "#e8c23a", "#d8772c"
    el = ["YKKY", "KKKK", "KYYK", "KKKK"]
    elytra = P(K, n=8, hl=True, faces={"up": {"px": grid(top(el), {"Y": Y, "K": K})},
                                       "east": {"px": [[2, 0, Y], [3, 0, Y]]}, "west": {"px": [[1, 0, Y], [0, 0, Y]]}})
    bones = [
        B("body", [0, 2, 0], [
            C([-2, 1, -1], [4, 2, 4], elytra, name="elytra"),
            C([-1.5, 1, -3], [3, 2, 2], P(O, hl=True, faces={"up": {"px": [[1, 0, "#f09a4a"], [1, 1, "#c8601e"]]}}), name="pronotum"),
            C([-1.5, 0.7, -1], [3, 1, 3], P("#a0501c")),
        ]),
        B("head", [0, 2, -3], [
            C([-1, 1, -4], [2, 2, 1], P("#d86e24", hl=True, faces={"north": {"px": [[0, 1, "#5a2a10"], [1, 1, "#5a2a10"]]},
                                                                "east": {"px": [[0, 0, "#141414"]]}, "west": {"px": [[0, 0, "#141414"]]}})),
            C([-0.5, 1, -4.6], [1, 1, 1], P("#6a3010"), inflate=-0.2),
        ], parent="body"),
        # abdomen tip: the 'turret' that swings up to spray
        B("abdomen", [0, 1.3, 2], [C([-1.5, 0.8, 2], [3, 1, 2], P("#c0602a", "stripe", c2="#8e4418", per=2)),
                                    C([-0.5, 1, 4], [1, 1, 1], P("#ffb040"))], parent="body"),
    ]
    bones += antennae2("head", 0.6, 2.5, -4, 4, banded("#d0702a", "#8e4418"), up=20, out=30)
    bones += legs2g("body", [(1.5, 1.5, -2.2), (2, 1.5, -0.4), (2, 1.5, 1.2)], 2, P(leg, hl=True), fan=(35, 0, -32),
                    lift=25, splay=20, inflate=-0.2)
    spray = {"abdomen": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-65, 0, 0]), kf(0.25, [-75, 25, 0]), kf(0.45, [-75, -25, 0]),
                                      kf(0.6, [-65, 0, 0]), kf(0.8, [0, 0, 0])]},
             "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-8, 0, 0]), kf(0.6, [-8, 0, 0]), kf(0.8, [0, 0, 0])],
                      "position": [kf(0, [0, 0, 0]), kf(0.1, [0, 0.4, 0]), kf(0.6, [0, 0.4, 0]), kf(0.8, [0, 0, 0])]}}
    return {"id": "bombardier_beetle", "seed": 106, "bones": bones, "anims": {
        "idle": {"len": 2.5, "bones": merge(antenna_idle(2.5, 10), bob("body", 2.5, 0.12))},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35, 22, 10), antenna_idle(0.35, 8))},
        "spray": {"len": 0.8, "loop": False, "bones": merge(spray, antenna_idle(0.8, 12))},
    }}


def diving_beetle():
    OB, OL, Y, U = "#232a18", "#3a4526", "#d8b440", "#7a6628"
    pits = [[1, z, "#34401f"] for z in range(0, 4, 2)] + [[3, z, "#34401f"] for z in range(1, 4, 2)]
    elytra = P(OB, "iri", c2=OL, j=0.08, hl=True, n=5, faces={
        "up": {"pat": "iri", "px": col(0, 4, Y) + col(4, 4, Y) + pits},
        "east": {"pat": "solid", "px": row(0, 4, Y)}, "west": {"pat": "solid", "px": row(0, 4, Y)},
        "down": {"pat": "solid", "c": U}})
    pron = P(OB, "iri", c2=OL, j=0.08, hl=True, n=5, faces={
        "up": {"px": col(0, 2, Y) + col(3, 2, Y)},
        "east": {"px": row(0, 2, Y)}, "west": {"px": row(0, 2, Y)}, "down": {"c": U}})
    taper = P(OB, hl=True, n=5, faces={"up": {"px": [[0, 0, Y], [-1, 0, Y]]}, "east": {"px": row(0, 1, Y)},
                                        "west": {"px": row(0, 1, Y)}, "down": {"c": U}})
    fringe = [[x, 0, "#e4d49a"] for x in range(0, 6, 2)] + [[x, 0, "#b8a468"] for x in range(1, 6, 2)]
    oar = P("#5a4a20", n=6, faces={"up": {"px": fringe + [[x, 1, "#4a3c18"] for x in range(3, 6)]},
                                   "down": {"px": fringe}})
    oar_r = P("#5a4a20", n=6, faces={"up": {"px": fringe + [[x, 1, "#4a3c18"] for x in range(0, 3)]},
                                     "down": {"px": fringe}})
    bones = [
        B("body", [0, 1.8, 0], [
            C([-2.5, 0.8, -1.5], [5, 2, 4], elytra, name="elytra"),
            C([-2, 0.8, 2.5], [4, 2, 1], taper),
            C([-1, 1, 3.5], [2, 1, 1], P(OB, faces={"down": {"c": U}})),
            C([-2, 0.8, -3.5], [4, 2, 2], pron, name="pronotum"),
        ]),
        B("head", [0, 1.6, -3.5], [
            C([-1.5, 0.9, -4.5], [3, 1, 1], P("#2e3420", hl=True, faces={"up": {"px": [[1, 0, Y], [0, 0, "#6a6030"], [2, 0, "#6a6030"]]},
                                                                      "north": {"px": [[1, 0, Y]]},
                                                                      "east": {"px": [[0, 0, "#0e1008"]]}, "west": {"px": [[0, 0, "#0e1008"]]}})),
        ], parent="body"),
        # flattened, fringed swimming legs
        B("oar_l", [2, 1.3, 1.5], [C([2, 1.3, 1], [6, 0, 2], oar)], parent="body", rot=[0, -35, -4]),
        B("oar_r", [-2, 1.3, 1.5], [C([-8, 1.3, 1], [6, 0, 2], oar_r)], parent="body", rot=[0, 35, 4]),
    ]
    bones += antennae2("head", 0.8, 1.6, -4.4, 3, P("#8a7a3a"), up=10, out=35)
    bones += legs2g("body", [(1.6, 1.2, -2.6), (2.1, 1.2, -0.6)], 2, P("#4a4020"), fan=(40, -10), lift=20, splay=25, inflate=-0.2)
    stroke = {"oar_l": {"rotation": [kf(0, [0, 40, 6]), kf(0.18, [0, -20, -6]), kf(0.3, [0, -22, 0]), kf(0.6, [0, 40, 6])]},
              "oar_r": {"rotation": [kf(0, [0, -40, -6]), kf(0.18, [0, 20, 6]), kf(0.3, [0, 22, 0]), kf(0.6, [0, -40, -6])]},
              "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.18, [-3, 0, 0]), kf(0.6, [0, 0, 0])],
                       "position": [kf(0, [0, 0, 0]), kf(0.18, [0, 0.15, 0]), kf(0.6, [0, 0, 0])]}}
    idle = merge(antenna_idle(3, 8), bob("body", 3, 0.12),
                 {"oar_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.4, [0, 18, 0]), kf(2.7, [0, 0, 0]), kf(3, [0, 0, 0])]},
                  "oar_r": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.4, [0, -18, 0]), kf(2.7, [0, 0, 0]), kf(3, [0, 0, 0])]}})
    walk = merge(stroke, antenna_idle(0.6, 6), tripod_walk(0.6, 12, 6, n=2))
    return {"id": "diving_beetle", "seed": 107, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.6, "bones": walk},
    }}


def mole_cricket():
    V, VD, VL, CL = "#7a5536", "#5a3a22", "#b08a5c", "#3a2412"
    velvet = P(V, n=20, hl=True, faces={"down": {"c": VL}})
    hood = P("#6e4a2e", n=20, hl=True, faces={"up": {"px": [[1, 1, "#553620"], [2, 1, "#553620"], [1, 2, "#553620"]]}, "down": {"c": VL}})
    spade = P("#4e2c14", hl=True, n=8, faces={"north": {"px": [[0, 0, "#7a4a24"], [1, 1, "#3a200c"]]}})
    claw = P("#2a1608", n=4, faces={"north": {"c": "#a07048"}})
    bones = [
        B("body", [0, 2.5, 0], [
            C([-2, 0.8, -3.5], [4, 3, 3], hood, name="pronotum"),
            C([-1.5, 0.8, -0.5], [3, 3, 4], P("#8a6440", "stripe", c2="#76532f", per=2, n=16, faces={"up": {"pat": "solid", "c": V},
                                                                                                    "down": {"pat": "solid", "c": VL}})),
            C([-1, 1, 3.5], [2, 2, 1], P("#7e5a38", n=14)),
            C([-1.5, 3.85, -0.8], [3, 0, 3], P("#4e3520", "vstripe", c2="#3a2616", per=2, n=6)),
        ]),
        B("cerci", [0, 2.2, 4.5], [C([0.2, 1.7, 4.3], [1, 1, 2], P("#5a3a22"), inflate=-0.35, r=[0, 20, 0], p=[0.5, 2.2, 4.5]),
                                    C([-1.2, 1.7, 4.3], [1, 1, 2], P("#5a3a22"), inflate=-0.35, r=[0, -20, 0], p=[-0.5, 2.2, 4.5])], parent="body"),
        B("head", [0, 2.3, -3.5], [
            C([-1.5, 1.2, -5.5], [3, 2, 2], P("#7a5236", n=14, hl=True, faces={"north": {"px": [[1, 1, "#3a2414"], [0, 0, "#9a7048"], [2, 0, "#9a7048"]]},
                                                                             "east": {"px": [[-1, 0, "#140c06"]]}, "west": {"px": [[0, 0, "#140c06"]]}})),
            C([-0.2, 0.9, -6.2], [1, 1, 1], P("#a07850"), inflate=-0.3), C([-0.8, 0.9, -6.2], [1, 1, 1], P("#a07850"), inflate=-0.3),
        ], parent="body"),
        # huge digging forelegs: velvet femur, glossy spade, dark claws
        B("shovel_l", [1.6, 1.9, -3.2], [C([1.4, 1.0, -4.4], [1, 2, 2], velvet), C([2.1, 0.3, -5.3], [2, 2, 1], spade),
                                          C([2.1, 0.05, -6], [1, 1, 1], claw, inflate=-0.25), C([3.1, 0.05, -6], [1, 1, 1], claw, inflate=-0.25),
                                          C([2.6, 0.05, -6.2], [1, 1, 1], claw, inflate=-0.25)],
          parent="body", rot=[0, 14, -6]),
        B("shovel_r", [-1.6, 1.9, -3.2], [C([-2.4, 1.0, -4.4], [1, 2, 2], velvet), C([-4.1, 0.3, -5.3], [2, 2, 1], spade, mirror=True),
                                           C([-3.1, 0.05, -6], [1, 1, 1], claw, inflate=-0.25), C([-4.1, 0.05, -6], [1, 1, 1], claw, inflate=-0.25),
                                           C([-3.6, 0.05, -6.2], [1, 1, 1], claw, inflate=-0.25)],
          parent="body", rot=[0, -14, 6]),
    ]
    bones += antennae2("head", 0.7, 2.8, -5.4, 4, P("#5a3c24"), up=18, out=35)
    bones += legs2g("body", [(1.6, 1.4, -0.8), (1.6, 1.4, 1.4)], 2, P("#6a4a30"), fan=(10, -35), lift=20, splay=22, inflate=-0.18)
    dig = {"shovel_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [18, -60, -10]), kf(0.3, [0, 0, 0]), kf(0.45, [18, -60, -10]), kf(0.6, [0, 0, 0])]},
           "shovel_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [18, 60, 10]), kf(0.3, [0, 0, 0]), kf(0.45, [18, 60, 10]), kf(0.6, [0, 0, 0])]},
           "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-10, 0, 0]), kf(0.5, [-10, 0, 0]), kf(0.6, [0, 0, 0])]},
           "head": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-10, 0, 0]), kf(0.5, [-10, 0, 0]), kf(0.6, [0, 0, 0])]}}
    idle = merge(antenna_idle(3, 10), bob("body", 3, 0.12),
                 {"shovel_l": {"rotation": [kf(0, [0, 0, 0]), kf(1.6, [0, 0, 0]), kf(1.8, [8, -15, 0]), kf(2.0, [0, 0, 0]), kf(3, [0, 0, 0])]},
                  "shovel_r": {"rotation": [kf(0, [0, 0, 0]), kf(1.7, [0, 0, 0]), kf(1.9, [8, 15, 0]), kf(2.1, [0, 0, 0]), kf(3, [0, 0, 0])]}})
    walk = merge(tripod_walk(0.45, 22, 10, n=2), antenna_idle(0.45, 8),
                 {"shovel_l": {"rotation": cycle(0.45, [[6, 10, 0], [-4, -10, 0]])},
                  "shovel_r": {"rotation": cycle(0.45, [[-4, 10, 0], [6, -10, 0]])}})
    return {"id": "mole_cricket", "seed": 108, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.45, "bones": walk},
        "dig": {"len": 0.6, "loop": False, "bones": dig},
    }}


def darkling_beetle():
    K, R, H = "#18171b", "#26252a", "#3a3940"
    shell = P(K, "vstripe", c2=R, per=2, n=4, faces={"up": {"px": speck(5, 5, [H], 6, 7)}, "down": {"pat": "solid"}})
    dome = P(K, "vstripe", c2=R, per=2, n=4, faces={"up": {"px": speck(4, 4, [H], 5, 8)}})
    drop = P("#c4ecff", n=0, px=[[0, 0, "#ffffff"]])
    bones = [
        B("body", [0, 3.5, 0], [
            C([-2.5, 2.5, -1.5], [5, 3, 5], shell, name="elytra"),
            C([-2, 5.5, -1], [4, 1, 4], dome),
            C([-2, 2.5, 3.5], [4, 2, 1], shell),
            C([-2, 2.8, -3.5], [4, 2, 2], P("#1c1b20", n=4, faces={"up": {"px": [[1, 0, H], [2, 1, H]]}}), name="pronotum"),
        ]),
        B("head", [0, 3.4, -3.5], [
            C([-1.5, 2.8, -4.5], [3, 2, 1], P("#1d1c21", n=4, faces={"east": {"px": [[0, 0, "#4a4952"]]}, "west": {"px": [[0, 0, "#4a4952"]]},
                                                                   "north": {"px": [[1, 1, "#2e2d33"]]}})),
        ], parent="body"),
        # fog-basking water droplets (only shown by the bask animation)
        B("drops", [0, 6, 1], [C([0.3, 6.2, 0], [1, 1, 1], drop, inflate=-0.28), C([-1.2, 6.2, 1.5], [1, 1, 1], drop, inflate=-0.3),
                               C([1, 6.2, 2.2], [1, 1, 1], drop, inflate=-0.32), C([-0.4, 5.3, 3.4], [1, 1, 1], drop, inflate=-0.3),
                               C([-1.6, 5.2, 3.0], [1, 1, 1], drop, inflate=-0.34), C([0.9, 4.9, -2.6], [1, 1, 1], drop, inflate=-0.34)],
          parent="body"),
    ]
    bones += antennae2("head", 0.8, 3.6, -4.4, 3, banded("#1d1c21", "#34333a"), up=15, out=35)
    bones += legs2g("body", [(2, 3, -2.5), (2.4, 3, -0.3), (2.2, 3, 1.8)], 3, P("#1a191e"), fan=(40, 5, -35), lift=25, splay=15, inflate=-0.2)
    # stilt pose: rear high, head down; front legs fold, hind legs extend
    bask = merge({"body": {"rotation": hold([-24, 0, 0]), "position": hold([0, 0.2, 0])},
                  "head": {"rotation": hold([-12, 0, 0])},
                  "leg_l1": {"rotation": hold([-10, 0, 12])}, "leg_r1": {"rotation": hold([-10, 0, -12])},
                  "leg_l2": {"rotation": hold([10, 0, 0])}, "leg_r2": {"rotation": hold([10, 0, 0])},
                  "knee_l2": {"rotation": hold([0, 0, -4])}, "knee_r2": {"rotation": hold([0, 0, 4])},
                  "leg_l3": {"rotation": hold([25, 0, -48])}, "leg_r3": {"rotation": hold([25, 0, 48])},
                  "drops": {"scale": [kf(0, [0.3, 0.3, 0.3]), kf(0.8, [1, 1, 1]), kf(2, [1, 1, 1])],
                            "position": [kf(0, [0, 0, 0]), kf(0.8, [0, 0, 0]), kf(2, [0, 0, -1.2])]}},
                 antenna_idle(2, 6))
    return {"id": "darkling_beetle", "seed": 109, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 10), bob("body", 3, 0.12), hide("drops"))},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 22, 12), antenna_idle(0.5, 8), hide("drops"))},
        "bask": {"len": 2, "bones": bask},
    }}


# ================================================================ RARE

def leaf_insect():
    L, V, M, Bn = "#7cc243", "#64a836", "#b8e070", "#a88a40"
    leaf = ["..LML..",
            ".LVMVL.",
            "LVLMLVL",
            "VLLMLBV",
            "LLVMVLL",
            ".VLMLV.",
            "..LML..",
            "...M..."]
    pal = {"L": L, "V": V, "M": M, "B": Bn}
    under = {"L": "#9ad060", "V": "#86be52", "M": "#c4e888", "B": "#9ad060"}
    holes = [[x, y, CLEAR] for y, r in enumerate(top(leaf)) for x, ch in enumerate(r) if ch == "."]
    blade = P(L, n=6, faces={"up": {"px": grid(top(leaf), pal) + holes}, "down": {"px": grid(top(leaf), under) + holes}})
    flare = [".LL.", "LVVL"]
    fholes = [[x, y, CLEAR] for y, r in enumerate(top(flare)) for x, ch in enumerate(r) if ch == "."]
    fl = P(L, n=6, faces={"up": {"px": grid(top(flare), pal) + fholes}, "down": {"px": grid(top(flare), under) + fholes}})
    bones = [
        B("body", [0, 2, 0], [
            C([-3.5, 1.9, -1], [7, 0, 8], blade, name="leaf"),
            C([-0.5, 0.9, -1], [1, 1, 6], P("#6aae3a", n=6)),
            C([-1, 1.4, -4], [2, 1, 3], P("#72b83e", hl=True)),
            C([-2, 1.95, -3], [4, 0, 2], fl, name="flare"),
        ]),
        B("head", [0, 1.9, -4], [
            C([-1, 1.4, -5], [2, 1, 1], P("#80c448", hl=True)),
            C([0.7, 1.5, -5.1], [1, 1, 1], P("#8a6a30"), inflate=-0.28), C([-1.7, 1.5, -5.1], [1, 1, 1], P("#8a6a30"), inflate=-0.28),
        ], parent="body"),
    ]
    bones += antennae2("head", 0.4, 2.2, -5, 2, P("#6a9a3a"), up=20, out=30, inflate=-0.32)
    legs_ = legs2g("body", [(1, 1.7, -3.5), (1, 1.7, -2), (1.2, 1.7, -0.5)], 2, P("#6aae3a"), fan=(50, 10, -45),
                   lift=25, splay=25, inflate=-0.22)
    # leafy flaps on the femora
    lobe = ["LL", "L."]
    for b in legs_:
        if b["name"].startswith("leg_"):
            c0 = b["cubes"][0]
            x0, y0, z0 = c0["o"][0], c0["o"][1] + 0.5, c0["o"][2] + 0.5
            sx = 1 if b["name"][4] == "l" else -1
            shape = lobe if sx > 0 else [r[::-1] for r in lobe]
            fh = [[x, y, CLEAR] for y, r in enumerate(shape) for x, ch in enumerate(r) if ch == "."]
            b["cubes"].append(C([x0, y0, z0 - 2], [2, 0, 2], P(L, n=6, faces={"up": {"px": fh}, "down": {"px": fh}})))
    bones += legs_
    walk = merge(tripod_walk(0.9, 16, 8), sway("body", 0.9, 4, axis=2), antenna_idle(0.9, 5))
    return {"id": "leaf_insect", "seed": 110, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(antenna_idle(4, 6), sway("body", 4, 3, axis=2))},
        "walk": {"len": 0.9, "bones": walk},
    }}


def click_beetle():
    Br, Dk, Pr, Gl = "#4a3222", "#33231a", "#3e2a1c", "#a8ff5a"
    elytra = P(Br, "vstripe", c2="#3e2a1c", per=2, n=6, hl=True, faces={"down": {"pat": "solid", "c": "#5a4030"}})
    bones = [
        B("body", [0, 2, 0], [
            C([-1.5, 1, -1], [3, 2, 5], elytra, name="elytra"),
            C([-1, 1, 4], [2, 1, 1], P(Dk)),
            C([-1, 1.3, -1], [2, 1, 4], P("#5a4030")),
        ]),
        B("front", [0, 2, -1], [
            C([-1.5, 1, -3], [3, 2, 2], P(Pr, hl=True, n=6, faces={"up": {"px": [[0, 0, Gl, "glow"], [2, 0, Gl, "glow"], [1, 1, "#4e3626"]]},
                                                                "east": {"px": [[0, 0, Gl, "glow"]]}, "west": {"px": [[-1, 0, Gl, "glow"]]}}),
              name="pronotum"),
            C([1.2, 1, -1.4], [1, 1, 1], P(Pr), inflate=-0.25), C([-2.2, 1, -1.4], [1, 1, 1], P(Pr), inflate=-0.25),
            C([-1, 1, -4], [2, 1, 1], P("#2e2016", faces={"north": {"px": [[0, 0, "#0e0a06"], [1, 0, "#0e0a06"]]}})),
        ], parent="body"),
    ]
    bones += antennae2("front", 0.6, 1.8, -3.8, 3, banded("#3a2818", "#5a4030"), up=15, out=30)
    bones += legs2g("body", [(1.2, 1.5, -1.6), (1.5, 1.5, -0.2), (1.4, 1.5, 1.4)], 2, P("#3a2818"), fan=(40, 0, -30),
                    lift=20, splay=20, inflate=-0.22)
    click = merge({"front": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [28, 0, 0]), kf(0.2, [-18, 0, 0]), kf(0.32, [0, 0, 0]), kf(0.5, [0, 0, 0])]},
                   "body": {"position": [kf(0, [0, 0, 0]), kf(0.18, [0, 0, 0]), kf(0.28, [0, 3, 0]), kf(0.42, [0, 0.3, 0]), kf(0.5, [0, 0, 0])],
                            "rotation": [kf(0, [0, 0, 0]), kf(0.15, [-6, 0, 0]), kf(0.2, [8, 0, 0]), kf(0.3, [0, 0, 20]), kf(0.42, [0, 0, 0])]}},
                  legs_hold([30, 0, 0]))
    return {"id": "click_beetle", "seed": 111, "bones": bones, "anims": {
        "idle": {"len": 2.5, "bones": merge(antenna_idle(2.5, 10), bob("body", 2.5, 0.1))},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35, 22, 10), antenna_idle(0.35, 8))},
        "click": {"len": 0.5, "loop": False, "bones": click},
    }}


def sea_skater():
    body = P("#8e98a4", "iri", c2="#4a5462", j=0.1, hl=True, n=6, faces={"up": {"px": [[1, 1, "#e6ecf2"], [0, 2, "#c2cad4"]]}})
    leg = P("#39414c")
    bones = [
        B("body", [0, 1.5, 0], [
            C([-1.5, 1, -1], [3, 2, 3], body),
            C([-1, 1.2, -2], [2, 1, 1], P("#6c7682", hl=True, faces={"east": {"px": [[0, 0, "#141820"]]}, "west": {"px": [[0, 0, "#141820"]]}})),
        ]),
        B("head", [0, 1.8, -2], [C([-1, 1.2, -3], [2, 1, 1], P("#5c6672", faces={"east": {"px": [[0, 0, "#10141a"]]},
                                                                                 "west": {"px": [[0, 0, "#10141a"]]},
                                                                                 "north": {"px": [[0, 0, "#10141a"], [1, 0, "#10141a"]]}}))],
          parent="body"),
        B("front_l", [1, 1.6, -1.5], [C([1, 1.1, -2], [2, 1, 1], leg, inflate=-0.3)], parent="body", rot=[0, 45, -25]),
        B("front_r", [-1, 1.6, -1.5], [C([-3, 1.1, -2], [2, 1, 1], leg, inflate=-0.3)], parent="body", rot=[0, -45, 25]),
        B("mid_l", [1.2, 1.6, -0.5], [C([1.2, 1.1, -1], [8, 1, 1], leg, inflate=-0.34)], parent="body", rot=[0, 18, -9]),
        B("mid_r", [-1.2, 1.6, -0.5], [C([-9.2, 1.1, -1], [8, 1, 1], leg, inflate=-0.34)], parent="body", rot=[0, -18, 9]),
        B("back_l", [1.2, 1.6, 1], [C([1.2, 1.1, 0.5], [6, 1, 1], leg, inflate=-0.34)], parent="body", rot=[0, -40, -11]),
        B("back_r", [-1.2, 1.6, 1], [C([-7.2, 1.1, 0.5], [6, 1, 1], leg, inflate=-0.34)], parent="body", rot=[0, 40, 11]),
    ]
    bones += antennae2("head", 0.5, 1.8, -3, 3, leg, up=12, out=22, inflate=-0.35)
    skate = {"mid_l": {"rotation": cycle(0.5, [[0, 0, 0], [0, -35, 4], [0, 0, 0]])},
             "mid_r": {"rotation": cycle(0.5, [[0, 0, 0], [0, 35, -4], [0, 0, 0]])},
             "body": {"position": cycle(0.5, [[0, 0, 0], [0, 0.1, 0], [0, 0, 0]])}}
    return {"id": "sea_skater", "seed": 112, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 8), bob("body", 3, 0.15),
                                          {"back_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.35, [0, 8, 0]), kf(2.5, [0, 0, 0]), kf(3, [0, 0, 0])]}})},
        "walk": {"len": 0.5, "bones": merge(skate, antenna_idle(0.5, 6))},
    }}


def mushroom_beetle():
    O, K, KH = "#e8531c", "#141214", "#4a4652"
    elytra = P(O, hl=True, n=6, faces={"up": {"px": [[x, y, K] for y in (1, 3) for x in range(4)]},
                                       "east": {"px": col(1, 2, K) + col(3, 2, K)}, "west": {"px": col(1, 2, K) + col(3, 2, K)},
                                       "north": {"c": O}, "south": {"c": O}, "down": {"c": "#2a1a14"}})
    dome = P(O, hl=True, n=6, faces={"up": {"px": [[x, y, K] for y in (0, 2) for x in range(3)] + [[2, 3, "#ffb080"]]},
                                     "east": {"px": col(0, 1, K) + col(2, 1, K)}, "west": {"px": col(1, 1, K) + col(3, 1, K)}})
    cap = P("#d42a1e", hl=True, n=6, faces={"up": {"px": [[0, 0, "#f4efe6"], [2, 1, "#f4efe6"], [1, 2, "#f4efe6"]]},
                                            "east": {"px": [[1, 0, "#f4efe6"]]}, "west": {"px": [[1, 0, "#f4efe6"]]},
                                            "down": {"c": "#f0d8c8"}})
    bones = [
        B("body", [0, 2, 0], [
            C([-2, 1, -1.5], [4, 2, 5], elytra, name="elytra"),
            C([-1.5, 3, -1.5], [3, 1, 4], dome),
            C([-1.5, 1, -3.5], [3, 2, 2], P(K, hl=True, faces={"up": {"px": [[2, 1, "#5a5662"]]}}), name="pronotum"),
            C([-1.5, 0.7, -1.5], [3, 1, 4], P("#2a1a14")),
        ]),
        B("head", [0, 1.8, -3.5], [C([-1, 1, -4.5], [2, 1, 1], P(K, faces={"north": {"px": [[0, 0, KH], [1, 0, KH]]}}))], parent="body"),
        # the tiny mushroom it farms on its back
        B("mushroom", [0.5, 4, 0.5], [
            C([0, 4, 0], [1, 2, 1], P("#ece2cc", n=6)),
            C([-1, 6, -1], [3, 1, 3], cap),
            C([-0.5, 7, -0.5], [2, 1, 2], dict(cap, faces={"up": {"px": [[0, 0, "#f4efe6"]]}})),
        ], parent="body", rot=[0, 0, -8]),
    ]
    bones += antennae2("head", 0.5, 1.6, -4.4, 2, P(K), up=15, out=35, tip=P("#2a262e"))
    bones += legs2g("body", [(1.4, 1.4, -2.4), (1.8, 1.4, -0.3), (1.6, 1.4, 1.6)], 2, P("#1e1b20", hl=True),
                    fan=(38, 0, -32), lift=22, splay=20, inflate=-0.2)
    idle = merge(antenna_idle(3, 10), bob("body", 3, 0.12), sway("mushroom", 3, 5, axis=2, base=(0, 0, -8)))
    walk = merge(tripod_walk(0.4, 22, 10), antenna_idle(0.4, 8), sway("mushroom", 0.4, 6, axis=2, base=(0, 0, -8)))
    return {"id": "mushroom_beetle", "seed": 113, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.4, "bones": walk},
    }}


def rain_beetle():
    CH, FUR, HAIR, LEG = "#7a3c1a", "#c8963e", "#ecc878", "#3a1a0a"
    elytra = P(CH, "grad", c2="#5c2a10", hl=True, n=22, faces={"up": {"pat": "solid", "px": speck(5, 5, ["#8e4a22", "#6a3214"], 8, 21)}})
    fur = P(FUR, n=34, hl=True, faces={"up": {"px": speck(4, 2, [HAIR, "#a8762a"], 5, 22)},
                                       "east": {"px": speck(2, 3, [HAIR], 3, 23)}, "west": {"px": speck(2, 3, [HAIR], 3, 24)}})
    skirt = P("#b8863a", n=34, faces={"east": {"px": [[x, 0, HAIR] for x in range(0, 7, 2)]},
                                      "west": {"px": [[x, 0, HAIR] for x in range(1, 7, 2)]}})
    lam = P("#b8782c", hl=True, n=8)
    bones = [
        B("body", [0, 2.5, 0], [
            C([-2.5, 1.5, -1], [5, 3, 5], elytra, name="elytra"),
            C([-2, 4.5, -0.5], [4, 1, 4], dict(elytra, faces={"up": {"pat": "solid", "px": [[1, 3, "#a86030"], [2, 3, "#a86030"]]}})),
            C([-2, 1.5, 4], [4, 2, 1], P("#6a3214", n=20)),
            C([-2, 1.5, -3], [4, 3, 2], fur, name="pronotum"),
            C([-2.5, 1.1, -3], [5, 1, 7], skirt, name="hair"),
        ]),
        B("head", [0, 2.6, -3], [
            C([-1.5, 1.6, -4], [3, 2, 1], P("#5a2a10", hl=True, n=12, faces={"east": {"px": [[0, 0, "#140a04"]]}, "west": {"px": [[0, 0, "#140a04"]]},
                                                                           "north": {"px": [[0, 1, "#3a1a08"], [2, 1, "#3a1a08"]]}})),
        ], parent="body"),
    ]
    # antennae: short stalk plus a fan of three golden lamellae that open and close
    for side, sx in (("l", 1), ("r", -1)):
        bones.append(B(f"antenna_{side}", [sx * 0.9, 2.8, -4], [C([sx * 0.9 - 0.5, 2.3, -5.5], [1, 1, 2], P("#4a2410"), inflate=-0.3)],
                       parent="head", rot=[20, -sx * 40, 0]))
        for k, yaw in enumerate((-12, 4, 20), start=1):
            bones.append(B(f"lam_{side}{k}", [sx * 0.9, 2.8, -5.2], [C([sx * 0.9 - 0.5, 2.3, -8], [1, 1, 3], lam, inflate=-0.28)],
                           parent=f"antenna_{side}", rot=[k * 4 - 8, sx * yaw, 0]))
    bones += legs2g("body", [(2, 2, -2.2), (2.4, 2, 0), (2.2, 2, 2)], 2, P(LEG, hl=True, faces={"up": {"px": [[0, 0, HAIR]]}}),
                    fan=(38, 0, -32), lift=25, splay=20, inflate=-0.15)

    def fan(period, opened):
        out = {}
        for side, sx in (("l", 1), ("r", -1)):
            for k, (c, o) in enumerate(zip((-12, 4, 20), (-40, 4, 48)), start=1):
                base = [0, 0, 0]
                open_ = [0, sx * (o - c), 0]
                out[f"lam_{side}{k}"] = {"rotation": [kf(0, base), kf(period * 0.3, open_ if opened else base),
                                                      kf(period * 0.7, open_), kf(period, base)]}
        return out
    return {"id": "rain_beetle", "seed": 114, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(fan(3, True), antenna_idle(3, 8), bob("body", 3, 0.12))},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 20, 10), antenna_idle(0.5, 8),
                                            {f"lam_{s}{k}": {"rotation": hold([0, (1 if s == 'l' else -1) * d, 0])}
                                             for s in "lr" for k, d in ((1, -18), (2, 0), (3, 18))})},
    }}


# ================================================================ EPIC

def chorus_weevil():
    Pu, Pl, Pd = "#9a74b8", "#dcc4ec", "#5e3f7a"
    chorus = P(Pu, "spots", c2=Pl, d=0.22, hl=True, n=10)
    bumpy = lambda w, h, seed: dict(chorus, faces={"up": {"px": speck(w, h, [Pd, "#b894d4"], w * h // 3, seed)},
                                                   "east": {"px": speck(h, 3, [Pd], 2, seed + 1)},
                                                   "west": {"px": speck(h, 3, [Pd], 2, seed + 2)}})
    bones = [
        B("body", [0, 2.5, 0], [
            C([-2, 1.5, -1.5], [4, 3, 4], bumpy(4, 4, 31), name="elytra"),
            C([-1.5, 4.5, -1], [3, 1, 3], bumpy(3, 3, 34)),
            C([-1.5, 1.5, 2.5], [3, 2, 1], bumpy(3, 1, 37)),
            C([-1.5, 1.8, -3.5], [3, 2, 2], P("#8a66aa", hl=True, n=8, faces={"up": {"px": [[1, 0, Pd], [1, 1, "#b894d4"]]}}), name="pronotum"),
        ]),
        B("head", [0, 2.8, -3.5], [
            C([-1, 2, -4.5], [2, 2, 1], P("#8462a4", hl=True, faces={"east": {"px": [[0, 0, "#1a0e24"]]}, "west": {"px": [[0, 0, "#1a0e24"]]}})),
        ], parent="body"),
        # very long down-curved snout (rostrum)
        B("snout", [0, 2.8, -4.3], [C([-0.5, 2.3, -7.3], [1, 1, 3], P("#7a58a0", hl=True), inflate=-0.05)], parent="head", rot=[-16, 0, 0]),
        B("snout_tip", [0, 2.8, -7.2], [C([-0.5, 2.3, -9.2], [1, 1, 2], P("#6e4e92"), inflate=-0.1),
                                        C([-0.5, 2.3, -9.6], [1, 1, 1], P("#3a2450"), inflate=-0.25)], parent="snout", rot=[-24, 0, 0]),
    ]
    # elbowed antennae sprouting from the middle of the snout
    bones += antennae2("snout", 0.5, 2.9, -6.2, 3, P("#6a4a8a"), up=55, out=55, inflate=-0.32, tip=P("#c8a8e0"))
    bones += legs2g("body", [(1.4, 2, -2.6), (1.8, 2, -0.4), (1.7, 2, 1.6)], 2, P("#7a58a0"), tibia_paint=P("#5e3f7a"),
                    fan=(40, 0, -35), lift=25, splay=18, inflate=-0.2)
    idle = merge(antenna_idle(3, 12), bob("body", 3, 0.12),
                 {"snout": {"rotation": [kf(0, [0, 0, 0]), kf(1.2, [0, 0, 0]), kf(1.5, [-6, 0, 0]), kf(1.8, [0, 0, 0]), kf(3, [0, 0, 0])]},
                  "head": {"rotation": [kf(0, [0, 0, 0]), kf(2.0, [0, 0, 0]), kf(2.3, [0, 10, 0]), kf(2.7, [0, -6, 0]), kf(3, [0, 0, 0])]}})
    walk = merge(tripod_walk(0.45, 20, 10), antenna_idle(0.45, 8),
                 {"head": {"rotation": cycle(0.45, [[3, 0, 0], [-2, 0, 0]])}})
    return {"id": "chorus_weevil", "seed": 115, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.45, "bones": walk},
    }}


# ================================================================ LEGENDARY

def storm_beetle():
    S, SD, Y, VG, CU = "#2a3140", "#1f2430", "#ffe14a", "#5dbf9c", "#b86a3c"
    bolt = ["....YY",
            "...YY.",
            "..YY..",
            ".YYYY.",
            "...YY.",
            "..YY..",
            ".Y...."]
    right_half = [r[:3] for r in bolt]      # top view: left half of the picture is the -X (right) elytron
    left_half = [r[3:] for r in bolt]
    bolt_px = lambda rows: [[x, y, Y, "glow"] for y, r in enumerate(top(rows)) for x, ch in enumerate(r) if ch == "Y"]
    zig = [[1, 2, Y, "glow"], [2, 1, Y, "glow"], [3, 1, Y, "glow"], [4, 0, Y, "glow"]]
    el_l = P(S, hl=True, n=6, faces={"up": {"px": bolt_px(left_half)}, "east": {"px": zig}, "down": {"c": SD}})
    el_r = P(S, hl=True, n=6, faces={"up": {"px": bolt_px(right_half)}, "west": {"px": [[6 - x, yy, c, g] for x, yy, c, g in zig]},
                                     "down": {"c": SD}})
    wing = P("#b8d8ff", "wing", c2="#6a8ab8", alpha=0.5, n=4)
    bones = [
        B("body", [0, 3.5, 0], [
            C([-2.5, 1.8, -1], [5, 1, 6], P(SD)),
            C([-2.5, 2, -4], [5, 3, 3], P("#353c4a", hl=True, n=6, faces={"up": {"px": [[2, 0, Y, "glow"], [2, 1, Y, "glow"], [1, 2, Y, "glow"]]}}),
              name="pronotum"),
        ]),
        B("wing_l", [0, 4.9, -0.5], [C([0, 4.9, -0.5], [3, 0, 6], wing)], parent="body"),
        B("wing_r", [0, 4.9, -0.5], [C([-3, 4.9, -0.5], [3, 0, 6], wing, mirror=True)], parent="body"),
        B("elytra_l", [0, 5, -1], [C([0, 2, -1], [3, 3, 7], el_l)], parent="body"),
        B("elytra_r", [0, 5, -1], [C([-3, 2, -1], [3, 3, 7], el_r)], parent="body"),
        B("head", [0, 3.5, -4], [
            C([-1.5, 2, -6], [3, 2, 2], P("#2a303b", hl=True, faces={"east": {"px": [[-1, 0, "#fff4b0", "glow"]]}, "west": {"px": [[0, 0, "#fff4b0", "glow"]]},
                                                                  "north": {"px": [[0, 1, "#1a1e26"], [2, 1, "#1a1e26"]]}})),
        ], parent="body"),
        # a copper lightning-rod horn gone green with age
        B("horn", [0, 3.8, -5.5], [C([-0.5, 3.8, -6], [1, 4, 1], P(VG, "grad", c2=CU, n=6), inflate=-0.05),
                                   C([-0.5, 7.6, -6], [1, 1, 1], P("#8ef0c8", px=[[0, 0, "#e8fff4", "glow"]]), inflate=-0.1)],
          parent="head", rot=[-32, 0, 0]),
    ]
    bones += antennae2("head", 1, 3.2, -5.8, 3, P("#1e232c"), up=25, out=35, tip=P(VG))
    bones += legs2g("body", [(2.3, 2.5, -3), (2.7, 2.5, 0), (2.5, 2.5, 3)], 3, P("#1e232c", hl=True), tibia_paint=P("#262c36", faces={"down": {"c": VG}}),
                    fan=(40, 0, -35), lift=25, splay=20, inflate=-0.15)
    jit = lambda b, v: {b: {"rotation": [kf(0, v), kf(0.05, [v[0], v[1], v[2] + 5]), kf(0.1, [v[0], v[1], v[2] - 3]),
                                         kf(0.15, [v[0], v[1], v[2] + 4]), kf(0.2, v)]}}
    charge = merge(jit("elytra_l", [-12, 0, 38]), jit("elytra_r", [-12, 0, -38]),
                   flap("wing_l", "wing_r", 0.1, 30, 5), {"wing_l": {"position": hold([0, 0.6, 0])}, "wing_r": {"position": hold([0, 0.6, 0])}},
                   {"body": {"position": cycle(0.2, [[0.1, 0, 0], [-0.1, 0.05, 0], [0.1, 0, 0.05], [-0.1, 0, 0]])},
                    "horn": {"rotation": cycle(0.2, [[-6, 0, 2], [-6, 0, -2]])},
                    "antenna_l": {"rotation": hold([25, 10, 0])}, "antenna_r": {"rotation": hold([25, -10, 0])}})
    return {"id": "storm_beetle", "seed": 116, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 8), bob("body", 3, 0.15),
                                          {"horn": {"rotation": [kf(0, [0, 0, 0]), kf(1.5, [0, 0, 0]), kf(1.6, [0, 0, 4]), kf(1.7, [0, 0, -4]), kf(1.8, [0, 0, 0]), kf(3, [0, 0, 0])]}})},
        "walk": {"len": 0.6, "bones": merge(tripod_walk(0.6, 20, 10), antenna_idle(0.6, 6), bob("body", 0.3, 0.15))},
        "charge": {"len": 0.2, "bones": charge},
    }}


def crystal_beetle():
    shell = P("#9a5cf0", "iri", c2="#5ce0f0", j=0.1, alpha=0.72, n=8, hl=True)
    hi = "#ffffff"
    el_l = dict(shell, faces={"up": {"px": [[0, 1, hi, "glow"], [1, 4, hi, "glow"], [2, 6, "#e0fbff", "glow"]]},
                              "east": {"px": [[2, 0, hi, "glow"], [5, 1, "#e0fbff", "glow"]]}})
    el_r = dict(shell, faces={"up": {"px": [[2, 2, hi, "glow"], [1, 5, hi, "glow"], [0, 0, "#e0fbff", "glow"]]},
                              "west": {"px": [[4, 0, hi, "glow"], [1, 1, "#e0fbff", "glow"]]}})
    ridge = P("#c8b0ff", "iri", c2="#b8fbff", j=0.08, alpha=0.8, n=6, px=[[0, 0, hi, "glow"], [1, 3, hi, "glow"]])
    gem = lambda c1, c2: P(c1, "grad", c2=c2, alpha=0.85, n=4, glow="c2")
    dark = P("#2e2350", hl=True, n=6)
    bones = [
        B("body", [0, 3, 0], [
            C([-2, 1.6, -1], [4, 2, 6], P("#3a2a66", hl=True, n=6)),
            C([-2, 2, -4], [4, 3, 3], dict(shell, c="#b07cf4", faces={"up": {"px": [[1, 2, hi, "glow"], [2, 0, "#e0fbff", "glow"]]}}), name="pronotum"),
            C([-1, 4.3, -3.5], [2, 1, 2], P("#d8c8ff", "iri", c2="#b8fbff", alpha=0.8, px=[[0, 0, hi, "glow"]]), r=[0, 45, 0], p=[0, 4.8, -2.5]),
        ]),
        B("elytra_l", [0, 5, -1.5], [C([0, 2, -1.5], [3, 3, 7], el_l)], parent="body"),
        B("elytra_r", [0, 5, -1.5], [C([-3, 2, -1.5], [3, 3, 7], el_r)], parent="body"),
        # faceted ridge along the seam and gems growing out of the shell
        B("gems", [0, 5, 2], [
            C([-1, 4, -1], [2, 2, 6], ridge, r=[0, 0, 45], p=[0, 5, 2]),
            C([1.2, 4.6, 0.5], [1, 3, 1], gem("#8a4ae8", "#f0d8ff"), r=[15, 45, -25], p=[1.7, 4.6, 1]),
            C([-2.4, 4.6, 2.5], [1, 2, 1], gem("#3ab8e0", "#e0fcff"), r=[-10, 45, 30], p=[-1.9, 4.6, 3]),
            C([0.6, 4.8, 3.6], [1, 2, 1], gem("#e0a0ff", "#ffffff"), r=[-25, 45, -10], p=[1.1, 4.8, 4.1]),
        ], parent="body"),
        B("head", [0, 3, -4], [
            C([-1.5, 2, -5], [3, 2, 1], P("#2a1f4a", hl=True, faces={"north": {"px": [[0, 0, "#c8fbff", "glow"], [2, 0, "#c8fbff", "glow"]]},
                                                                  "east": {"px": [[0, 0, "#c8fbff", "glow"]]}, "west": {"px": [[0, 0, "#c8fbff", "glow"]]}})),
        ], parent="body"),
    ]
    bones += antennae2("head", 0.8, 3.4, -5, 3, dark, up=25, out=32, tip=P("#8ef4ff", glow=True))
    bones += legs2g("body", [(2, 2.5, -2.8), (2.5, 2.5, -0.2), (2.3, 2.5, 2.4)], 3, dark, fan=(40, 0, -35), lift=25, splay=20,
                    inflate=-0.18)
    idle = merge(antenna_idle(3, 8), bob("body", 3, 0.12),
                 {"gems": {"rotation": [kf(0, [0, 0, 0]), kf(1.5, [0, 6, 0]), kf(3, [0, 0, 0])]}})
    return {"id": "crystal_beetle", "seed": 117, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.55, "bones": merge(tripod_walk(0.55, 20, 10), antenna_idle(0.55, 6))},
    }}


SPECS = {f.__name__: f for f in [
    grasshopper, springtail, whirligig_beetle, stink_bug, praying_mantis, bombardier_beetle,
    diving_beetle, mole_cricket, darkling_beetle, leaf_insect, click_beetle, sea_skater,
    mushroom_beetle, rain_beetle, chorus_weevil, storm_beetle, crystal_beetle,
]}
