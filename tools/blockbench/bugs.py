"""Bug model specs for the Blockbench builder (builder.js).

Units are Blockbench pixels. Every bug faces north (-Z) with its feet on y=0.
Rotation conventions (Blockbench editor, bedrock format):
    +Z rotation lifts the +X side, +X rotation lifts the front (-Z), +Y swings +X toward the front.
Each spec: {id, seed, bones:[...], anims:{name: {len, loop, bones:{bone:{rotation|position|scale:[[t,[x,y,z]],...]}}}}}
Paint: P(color, pattern, c2, ...) - see paintFace in builder.js. glow=True (whole cube), glow="c2" (pattern pixels only),
or px detail pixels with a 4th element "glow".
"""
import math

# ---------------------------------------------------------------- helpers

def P(c, pat=None, c2=None, **kw):
    d = {"c": c}
    if pat:
        d["pat"] = pat
    if c2:
        d["c2"] = c2
    d.update(kw)
    return d


def C(o, s, paint, p=None, r=None, mirror=False, inflate=0, name=None):
    d = {"o": list(o), "s": list(s), "paint": paint}
    if p is not None:
        d["p"] = list(p)
    if r is not None:
        d["r"] = list(r)
    if mirror:
        d["mirror"] = True
    if inflate:
        d["inflate"] = inflate
    if name:
        d["name"] = name
    return d


def B(name, pivot, cubes=(), parent=None, rot=None):
    d = {"name": name, "pivot": list(pivot), "cubes": list(cubes)}
    if parent:
        d["parent"] = parent
    if rot:
        d["rot"] = list(rot)
    return d


def col(x, h, color, glow=False):
    return [[x, y, color] + (["glow"] if glow else []) for y in range(h)]


def row(y, w, color, glow=False):
    return [[x, y, color] + (["glow"] if glow else []) for x in range(w)]


def legs(parent, hips, length, paint, thick=1, down=None, prefix="leg", fan=None, sz=None):
    """Single-segment splayed legs. hips: (x, y, z) for the +X side; the -X side is mirrored.
    fan: per-pair yaw in degrees (positive swings the +X leg forward)."""
    out = []
    sz = thick if sz is None else sz
    for i, (hx, hy, hz) in enumerate(hips, start=1):
        ang = down if down is not None else math.degrees(math.asin(min(0.95, max(0.1, hy / length))))
        yaw = fan[i - 1] if fan else 0
        for side, sx in (("l", 1), ("r", -1)):
            o = [hx if sx > 0 else -hx - length, hy - thick / 2, hz - sz / 2]
            out.append(B(f"{prefix}_{side}{i}", [sx * hx, hy, hz],
                         [C(o, [length, thick, sz], paint)], parent=parent, rot=[0, sx * yaw, -sx * ang]))
    return out


def legs2(parent, hips, femur, tibia, paint, thick=1, fan=(30, 0, -30), lift=20, splay=15, prefix="leg",
          tibia_paint=None):
    """Two-segment legs: femur out and slightly up, tibia down to the ground."""
    out = []
    for i, (hx, hy, hz) in enumerate(hips, start=1):
        yaw = fan[i - 1] if i - 1 < len(fan) else 0
        for side, sx in (("l", 1), ("r", -1)):
            fo = [hx if sx > 0 else -hx - femur, hy - thick / 2, hz - thick / 2]
            out.append(B(f"{prefix}_{side}{i}", [sx * hx, hy, hz], [C(fo, [femur, thick, thick], paint)],
                         parent=parent, rot=[0, sx * yaw, sx * lift]))
            kx = sx * (hx + femur - thick / 2)
            drop = hy + femur * math.sin(math.radians(lift)) + 0.5
            to = [kx - thick / 2, hy - drop, hz - thick / 2]
            out.append(B(f"knee_{side}{i}", [kx, hy, hz], [C(to, [thick, round(drop), thick], tibia_paint or paint)],
                         parent=f"{prefix}_{side}{i}", rot=[0, 0, sx * splay - sx * lift]))
    return out


def grid(rows, palette, glow=""):
    """Pixel-art detail for a face: rows of characters mapped through palette ('.' = leave)."""
    out = []
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in palette:
                out.append([x, y, palette[ch]] + (["glow"] if ch in glow else []))
    return out


def kf(t, v, interp=None):
    return [t, v, interp] if interp else [t, v]


def cycle(period, values):
    """Evenly spaced keyframes over one loop; the last equals the first for a seamless loop."""
    n = len(values)
    return [kf(round(period * i / n, 4), values[i]) for i in range(n)] + [kf(period, values[0])]


def hold(v):
    return [kf(0, v)]


def tripod_walk(period=0.4, swing=22, lift=12, n=3, prefix="leg"):
    bones = {}
    for i in range(1, n + 1):
        for side, sx in (("l", 1), ("r", -1)):
            phase = (i + (0 if side == "l" else 1)) % 2
            fwd, back = [0, sx * swing, sx * lift], [0, -sx * swing, 0]
            seq = [fwd, [0, 0, sx * lift / 2], back, [0, 0, 0]] if phase == 0 else [back, [0, 0, 0], fwd, [0, 0, sx * lift / 2]]
            bones[f"{prefix}_{side}{i}"] = {"rotation": cycle(period, seq)}
    return bones


def flap(left, right, period=0.12, up=55, down=-25, extra=None):
    """Wing flap: +Z lifts the left (+X) wing, -Z lifts the right wing."""
    e = extra or [0, 0]
    return {left: {"rotation": cycle(period, [[e[0], e[1], up], [e[0], -e[1], down]])},
            right: {"rotation": cycle(period, [[e[0], -e[1], -up], [e[0], e[1], -down]])}}


def sway(bone, period, amp, axis=0, offset=0.0, base=(0, 0, 0)):
    def v(a):
        r = list(base)
        r[axis] += a
        return r
    return {bone: {"rotation": cycle(period, [v(round(amp * math.sin(2 * math.pi * (i / 4 + offset)), 3)) for i in range(4)])}}


def bob(bone, period, amp, base=(0, 0, 0)):
    return {bone: {"position": cycle(period, [list(base), [base[0], base[1] + amp, base[2]]])}}


def hide(*bones):
    return {b: {"scale": hold([0, 0, 0])} for b in bones}


def merge(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            if k in out:
                out[k].update(v)
            else:
                out[k] = dict(v)
    return out


def antennae(parent, x, y, z, length, paint, up=25, out=20, name="antenna"):
    return [B(f"{name}_l", [x, y, z], [C([x, y, z - length], [0, 1, length], paint)], parent=parent, rot=[up, out, 0]),
            B(f"{name}_r", [-x, y, z], [C([-x, y, z - length], [0, 1, length], paint)], parent=parent, rot=[up, -out, 0])]


def antenna_idle(period=2.0, amp=10):
    return merge(sway("antenna_l", period, amp), sway("antenna_r", period, amp, offset=0.5))


# ---------------------------------------------------------------- palettes
BLACK = "#1b1a1f"
EYE = "#0d0d10"
SHINE = "#e9eef5"
WING_CLEAR = P("#d8e2e6", "wing", c2="#5d6a70", alpha=0.45)

# ================================================================ COMMON

def ladybug():
    red = P("#d4251c", "spots", c2=BLACK, d=0.12, hl=True)
    bones = [
        B("body", [0, 2, 0], [
            C([-2.5, 0.5, -2.5], [5, 1, 5], P(BLACK)),
            C([-2, 1, -4], [4, 2, 1], P(BLACK, faces={"north": {"px": [[0, 0, "#f3f0e6"], [-1, 0, "#f3f0e6"]]},
                                                      "up": {"px": [[0, 0, "#f3f0e6"], [-1, 0, "#f3f0e6"]]}})),
        ]),
        B("head", [0, 1.5, -4], [C([-1.5, 0.5, -5], [3, 2, 1], P(BLACK, faces={"north": {"px": [[0, 0, SHINE], [2, 0, SHINE]]}}))], parent="body"),
        B("shell_l", [0, 4, -3], [C([0, 1, -3], [3, 2, 6], red),
                                   C([0, 3, -2.5], [2, 1, 5], red)], parent="body"),
        B("shell_r", [0, 4, -3], [C([-3, 1, -3], [3, 2, 6], red),
                                   C([-2, 3, -2.5], [2, 1, 5], red)], parent="body"),
        B("wing_l", [0, 2.9, -2], [C([0, 2.9, -2], [2, 0, 5], WING_CLEAR)], parent="body"),
        B("wing_r", [0, 2.9, -2], [C([-2, 2.9, -2], [2, 0, 5], WING_CLEAR)], parent="body"),
    ]
    bones += antennae("head", 0.5, 2, -5, 2, P(BLACK))
    bones += legs("body", [(1.5, 1, -2), (2, 1, 0), (1.5, 1, 2)], 2, P(BLACK), fan=[25, 0, -25])
    fly = merge({"shell_l": {"rotation": hold([-25, 0, 40])}, "shell_r": {"rotation": hold([-25, 0, -40])},
                 "wing_l": {"scale": hold([2.4, 1, 1]), "position": hold([0, 1.2, 0])}, "wing_r": {"scale": hold([2.4, 1, 1]), "position": hold([0, 1.2, 0])}},
                flap("wing_l", "wing_r", 0.1, 50, -20),
                {f"leg_{s}{i}": {"rotation": hold([30, 0, 0])} for s in "lr" for i in (1, 2, 3)})
    return {"id": "ladybug", "seed": 11, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": antenna_idle()},
        "walk": {"len": 0.4, "bones": merge(tripod_walk(0.4), antenna_idle(0.4, 8))},
        "fly": {"len": 0.1, "bones": fly},
    }}


def aphid():
    green = P("#9ad65c", "grad", c2="#62a334", hl=True)
    bones = [
        B("body", [0, 2, 0], [
            C([-1.5, 0.5, -1], [3, 3, 4], green),
            C([-1, 1, -2], [2, 2, 1], P("#8ccc52")),
            C([-0.5, 3, 3], [1, 1, 1], P("#4d8a2a")),
        ]),
        B("head", [0, 2, -2], [C([-1, 1, -3], [2, 2, 1], P("#86c64e", faces={"north": {"px": [[0, 0, "#7a1d1d"], [1, 0, "#7a1d1d"]]}}))], parent="body"),
        B("cornicle_l", [0.5, 3, 2.5], [C([0.5, 3, 2.5], [1, 1, 2], P("#3f7422"))], parent="body", rot=[35, -20, 0]),
        B("cornicle_r", [-0.5, 3, 2.5], [C([-1.5, 3, 2.5], [1, 1, 2], P("#3f7422"))], parent="body", rot=[35, 20, 0]),
    ]
    bones += antennae("head", 0.5, 2.5, -3, 4, P("#4d8a2a"), up=30, out=25)
    bones += legs("body", [(1, 1, -1), (1.5, 1, 0.5), (1, 1, 2)], 2, P("#4d8a2a"), fan=[25, 0, -25])
    return {"id": "aphid", "seed": 12, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 8), bob("body", 3, 0.2, (0, 0, 0)))},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35, 20, 10), antenna_idle(0.35, 6))},
    }}


def firefly():
    elytra_l = P("#2f2826", n=8, faces={"up": {"px": col(0, 5, "#c9a75a")}})
    elytra_r = P("#2f2826", n=8, faces={"up": {"px": col(-1, 5, "#c9a75a")}})
    lantern = P("#e9f76c", "stripe", c2="#c3d94a", per=2, glow=True, n=4)
    bones = [
        B("body", [0, 2, 0], [
            C([-1.5, 0.5, -2], [3, 1, 4], P("#3a302b")),
            C([-1.5, 0.5, 2], [3, 2, 3], lantern, name="lantern"),
        ]),
        B("pronotum", [0, 2, -2], [C([-2, 1.5, -4], [4, 1, 2], P("#e8843c", faces={"up": {"px": [[1, 0, BLACK], [2, 0, BLACK], [1, 1, "#c23a2a"], [2, 1, "#c23a2a"]]}}))], parent="body"),
        B("head", [0, 1.5, -4], [C([-1, 0.5, -5], [2, 1, 1], P(BLACK, faces={"north": {"px": [[0, 0, "#3b3b44"], [1, 0, "#3b3b44"]]}}))], parent="body"),
        B("elytra_l", [0, 2.5, -2], [C([0, 1.5, -2], [2, 1, 5], elytra_l)], parent="body"),
        B("elytra_r", [0, 2.5, -2], [C([-2, 1.5, -2], [2, 1, 5], elytra_r)], parent="body"),
        B("wing_l", [0, 2.4, -1], [C([0, 2.4, -1], [2, 0, 5], WING_CLEAR)], parent="body"),
        B("wing_r", [0, 2.4, -1], [C([-2, 2.4, -1], [2, 0, 5], WING_CLEAR)], parent="body"),
    ]
    bones += antennae("head", 0.5, 1.5, -5, 3, P("#2a2422"), up=20, out=25)
    bones += legs("body", [(1, 1, -1.5), (1.5, 1, 0), (1, 1, 1.5)], 2, P("#2a2422"), fan=[25, 0, -25])
    fly = merge({"body": {"rotation": hold([18, 0, 0])},
                 "elytra_l": {"rotation": hold([-20, 0, 45])}, "elytra_r": {"rotation": hold([-20, 0, -45])},
                 "wing_l": {"scale": hold([2.2, 1, 1])}, "wing_r": {"scale": hold([2.2, 1, 1])}},
                flap("wing_l", "wing_r", 0.09, 50, -25), antenna_idle(0.9, 6),
                {f"leg_{s}{i}": {"rotation": hold([35, 0, 0])} for s in "lr" for i in (1, 2, 3)})
    return {"id": "firefly", "seed": 13, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": antenna_idle()},
        "walk": {"len": 0.4, "bones": merge(tripod_walk(0.4), antenna_idle(0.4, 8))},
        "fly": {"len": 0.9, "bones": merge(fly, bob("body", 0.9, 0.6))},
    }}


def cricket():
    brown = P("#3a2a1f", "grad", c2="#1f1612", hl=True)
    bones = [
        B("body", [0, 3, 0], [
            C([-1.5, 1.5, -2], [3, 2, 3], P("#3b2b20")),
            C([-1.5, 1, 1], [3, 2, 5], P("#2a1d15", "stripe", c2="#1b120d", per=2)),
        ]),
        B("head", [0, 3, -2], [C([-1.5, 1.5, -4.5], [3, 3, 3], P("#2d2019", faces={
            "north": {"px": [[0, 0, "#6b4a2c"], [2, 0, "#6b4a2c"], [1, 2, "#16100c"]]},
            "east": {"px": [[1, 0, EYE]]}, "west": {"px": [[1, 0, EYE]]}}))], parent="body"),
        B("wing_l", [0, 3.6, -1], [C([0, 3.6, -1.5], [2, 0, 6], P("#4a3525", "stripe", c2="#2d2016", per=2))], parent="body", rot=[-4, 0, -8]),
        B("wing_r", [0, 3.6, -1], [C([-2, 3.6, -1.5], [2, 0, 6], P("#4a3525", "stripe", c2="#2d2016", per=2))], parent="body", rot=[-4, 0, 8]),
        B("cerci", [0, 2, 6], [C([0.5, 2, 6], [0, 1, 3], P("#241911"), r=[10, -20, 0], p=[0.5, 2, 6]),
                              C([-0.5, 2, 6], [0, 1, 3], P("#241911"), r=[10, 20, 0], p=[-0.5, 2, 6])], parent="body"),
        # powerful hind legs: femur angled up/back, tibia back down
        B("hind_l", [1.5, 2, 1.5], [C([1.5, 1, 1.5], [1, 2, 5], P("#3a2a1f", "stripe", c2="#2a1d15", per=2))], parent="body", rot=[35, 0, 0]),
        B("hshin_l", [2, 1.5, 6], [C([1.5, 1.5, 1.5], [1, 1, 4.5], P("#241911"))], parent="hind_l", rot=[-75, 0, 0]),
        B("hind_r", [-1.5, 2, 1.5], [C([-2.5, 1, 1.5], [1, 2, 5], P("#3a2a1f", "stripe", c2="#2a1d15", per=2))], parent="body", rot=[35, 0, 0]),
        B("hshin_r", [-2, 1.5, 6], [C([-2.5, 1.5, 1.5], [1, 1, 4.5], P("#241911"))], parent="hind_r", rot=[-75, 0, 0]),
    ]
    bones += antennae("head", 0.5, 3.5, -4.5, 9, P("#2b1e15"), up=15, out=30)
    bones += legs("body", [(1.5, 2, -1.5), (1.5, 2, 0)], 3, P("#2b1e15"), fan=[30, -10])
    hop = merge({"hind_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-45, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hind_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-45, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hshin_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [60, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hshin_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [60, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [12, 0, 0]), kf(0.5, [0, 0, 0])]}},
                antenna_idle(0.5, 12))
    chirp = merge({"wing_l": {"rotation": cycle(0.08, [[20, 0, 0], [20, 6, 4]])},
                   "wing_r": {"rotation": cycle(0.08, [[20, 0, 0], [20, -6, -4]])}}, antenna_idle(1.0, 6))
    return {"id": "cricket", "seed": 14, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": antenna_idle(3, 12)},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35, 22, 10, n=2), antenna_idle(0.35, 8))},
        "hop": {"len": 0.5, "loop": False, "bones": hop},
        "chirp": {"len": 1.0, "bones": chirp},
    }}


def pill_bug():
    plate = P("#5f6772", "edge", c2="#3e444c", hl=True, n=8)
    widths = [3, 5, 5, 5, 5, 4, 3]
    cubes = []
    z = -3
    for i, w in enumerate(widths):
        h = 2 if w < 5 else 3
        cubes.append(C([-w / 2, 0.5, z], [w, h, 1], dict(plate, c="#636b76" if i % 2 else "#58606b")))
        z += 1
    bones = [
        B("body", [0, 1.5, 0], cubes),
        B("head", [0, 1, -3], [C([-1.5, 0.5, -4], [3, 1, 1], P("#4a5059", faces={"north": {"px": [[0, 0, EYE], [2, 0, EYE]]}}))], parent="body"),
        B("ball", [0, 2, 0], [C([-2, 0, -2], [4, 4, 4], P("#5d6570", "stripe", c2="#3c424a", per=2, hl=True))]),
    ]
    bones += antennae("head", 1, 1, -4, 2, P("#3c424a"), up=-10, out=35)
    bones += legs("body", [(1.5, 0.8, -2), (2, 0.8, -0.5), (2, 0.8, 1), (1.5, 0.8, 2.5)], 1, P("#8a8f96"), down=30, fan=[20, 5, -5, -20])
    roll = merge({"body": {"scale": [kf(0, [1, 1, 1]), kf(0.15, [0, 0, 0])]},
                  "ball": {"scale": [kf(0, [0, 0, 0]), kf(0.15, [1, 1, 1])]}})
    return {"id": "pill_bug", "seed": 15, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": merge(antenna_idle(2, 12), hide("ball"))},
        "walk": {"len": 0.3, "bones": merge(tripod_walk(0.3, 18, 8, n=4), antenna_idle(0.3, 10), hide("ball"))},
        "roll": {"len": 0.15, "loop": "hold", "bones": roll},
    }}


def water_strider():
    dark = P("#35332e", "grad", c2="#22211d", hl=True)
    leg = P("#2a2824")
    bones = [
        B("body", [0, 2, 0], [
            C([-1, 1.5, -3], [2, 1, 4], dark),
            C([-0.5, 1.5, 1], [1, 1, 5], P("#2d2b27")),
        ]),
        B("head", [0, 2, -3], [C([-1, 1.5, -5], [2, 1, 2], P("#2f2d29", faces={"east": {"px": [[0, 0, "#8a8474"]]}, "west": {"px": [[-1, 0, "#8a8474"]]}}))], parent="body"),
        # front legs: short, held forward
        B("front_l", [1, 2, -2.5], [C([1, 1.5, -2.5], [3, 0, 1], leg)], parent="body", rot=[0, 50, -10]),
        B("front_r", [-1, 2, -2.5], [C([-4, 1.5, -2.5], [3, 0, 1], leg)], parent="body", rot=[0, -50, 10]),
        # middle legs: long oars
        B("mid_l", [1, 2, -1], [C([1, 1.5, -1], [10, 0, 1], leg)], parent="body", rot=[0, 15, 8]),
        B("mid_r", [-1, 2, -1], [C([-11, 1.5, -1], [10, 0, 1], leg)], parent="body", rot=[0, -15, -8]),
        # hind legs: long, trailing
        B("back_l", [1, 2, 0], [C([1, 1.5, 0], [9, 0, 1], leg)], parent="body", rot=[0, -40, 8]),
        B("back_r", [-1, 2, 0], [C([-10, 1.5, 0], [9, 0, 1], leg)], parent="body", rot=[0, 40, -8]),
    ]
    bones += antennae("head", 0.5, 2, -5, 3, leg, up=10, out=20)
    skate = {"mid_l": {"rotation": cycle(0.6, [[0, 15, 8], [0, -25, 12], [0, 15, 8]])},
             "mid_r": {"rotation": cycle(0.6, [[0, -15, -8], [0, 25, -12], [0, -15, -8]])}}
    return {"id": "water_strider", "seed": 16, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 8), bob("body", 3, 0.15))},
        "walk": {"len": 0.6, "bones": merge(skate, antenna_idle(0.6, 6))},
    }}


# ================================================================ UNCOMMON

def monarch():
    K, O, W, D = "#171313", "#f08a1c", "#f4efe2", "#c8641a"
    pal = {"K": K, "O": O, "W": W, "D": D}
    pale = {"K": "#2a2220", "O": "#f2b25a", "W": W, "D": "#d9923f"}
    fore = ["KWKKKKK", "WKOOKOK", "KOOKOOK", "WKDOKOK", "KWKKKKK"]
    hind = ["KOOKOK", "KOKOOK", "WKODOK", "KWKKKK"]
    fwing = P(K, n=6, faces={"up": {"px": grid(fore, pal)}, "down": {"px": grid(fore, pale)}})
    hwing = P(K, n=6, faces={"up": {"px": grid(hind, pal)}, "down": {"px": grid(hind, pale)}})
    body = P("#1a1616", "spots", c2="#f2efe6", d=0.2)
    bones = [
        B("body", [0, 2, 0], [C([-0.5, 1, -3], [1, 1, 6], body)]),
        B("head", [0, 1.5, -3], [C([-1, 1, -4], [2, 1, 1], P(BLACK, faces={"north": {"px": [[0, 0, "#55504a"], [1, 0, "#55504a"]]}}))], parent="body"),
        B("wing_l", [0.5, 2, -1], [C([0.5, 2, -4], [7, 0, 5], fwing), C([0.5, 1.99, 0], [6, 0, 4], hwing)], parent="body"),
        B("wing_r", [-0.5, 2, -1], [C([-7.5, 2, -4], [7, 0, 5], fwing, mirror=True), C([-6.5, 1.99, 0], [6, 0, 4], hwing, mirror=True)], parent="body"),
    ]
    bones += antennae("head", 0.5, 2, -4, 4, P("#141111", px=[[0, 0, "#3a3430"]]), up=35, out=18)
    bones += legs("body", [(0.5, 1, -2), (0.5, 1, -1), (0.5, 1, 0)], 2, P("#141111"), thick=1, sz=0, fan=[25, 0, -25])
    return {"id": "monarch", "seed": 21, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge({"wing_l": {"rotation": [kf(0, [0, 0, 80]), kf(1.2, [0, 0, 80]), kf(1.8, [0, 0, 15]), kf(2.4, [0, 0, 15]), kf(3, [0, 0, 80])]},
                                            "wing_r": {"rotation": [kf(0, [0, 0, -80]), kf(1.2, [0, 0, -80]), kf(1.8, [0, 0, -15]), kf(2.4, [0, 0, -15]), kf(3, [0, 0, -80])]}},
                                           antenna_idle(3, 6))},
        "fly": {"len": 0.3, "bones": merge(flap("wing_l", "wing_r", 0.3, 75, -30), bob("body", 0.3, 0.8),
                                           {"body": {"rotation": hold([-10, 0, 0])}})},
    }}


def silk_moth():
    fur = P("#efe6d2", n=16, hl=True)
    wingp = P("#ece2cc", "stripe", c2="#cdbd9c", per=3, n=8)
    bones = [
        B("body", [0, 2.5, 0], [
            C([-1.5, 1, -2.5], [3, 3, 3], fur),
            C([-1, 1, 0.5], [2, 2, 4], P("#e6dcc4", "stripe", c2="#d2c4a4", per=2)),
        ]),
        B("head", [0, 2.5, -2.5], [C([-1, 1.5, -3.5], [2, 2, 1], P("#e8dcc0", faces={"north": {"px": [[0, 0, EYE], [1, 0, EYE]]}}))], parent="body"),
        B("wing_l", [1.5, 3.5, -2], [C([1.5, 3.5, -3], [5, 0, 5], wingp, name="fore_l"),
                                      C([1.5, 3.49, 1], [4, 0, 4], dict(wingp, c="#e6dac0"))], parent="body", rot=[0, -10, -10]),
        B("wing_r", [-1.5, 3.5, -2], [C([-6.5, 3.5, -3], [5, 0, 5], wingp, mirror=True),
                                       C([-5.5, 3.49, 1], [4, 0, 4], dict(wingp, c="#e6dac0"), mirror=True)], parent="body", rot=[0, 10, 10]),
        # feathery antennae
        B("antenna_l", [0.5, 3, -3.5], [C([0.5, 3, -6.5], [2, 0, 3], P("#9a7d52", "vstripe", c2="#6d5536", per=2))], parent="head", rot=[30, 25, 0]),
        B("antenna_r", [-0.5, 3, -3.5], [C([-2.5, 3, -6.5], [2, 0, 3], P("#9a7d52", "vstripe", c2="#6d5536", per=2))], parent="head", rot=[30, -25, 0]),
    ]
    bones += legs("body", [(1, 1.5, -2), (1.5, 1.5, -1), (1, 1.5, 0)], 2, P("#d8ccb0"), fan=[25, 0, -25])
    return {"id": "silk_moth", "seed": 22, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(antenna_idle(4, 6),
                                           {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(3.6, [0, 0, 0]), kf(3.8, [0, 0, 15]), kf(4, [0, 0, 0])]},
                                            "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(3.6, [0, 0, 0]), kf(3.8, [0, 0, -15]), kf(4, [0, 0, 0])]}})},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 18, 8), antenna_idle(0.5, 6))},
        "fly": {"len": 0.25, "bones": merge(flap("wing_l", "wing_r", 0.25, 60, -30), bob("body", 0.25, 0.5),
                                            {f"leg_{s}{i}": {"rotation": hold([30, 0, 0])} for s in "lr" for i in (1, 2, 3)})},
    }}


def dragonfly():
    tail = P("#2f7fd6", "iri", c2="#1f4fa8", n=10)
    thorax = P("#3ea36b", "iri", c2="#2a7e8f", hl=True)
    wing = P("#e4f1f6", "wing", c2="#6f8a96", alpha=0.35, px=[[-1, 0, "#3a3326"], [-2, 0, "#3a3326"]])
    bones = [
        B("body", [0, 3, 0], [
            C([-1, 2, -2], [2, 2, 3], thorax),
            C([-0.5, 2.5, 1], [1, 1, 9], dict(tail, faces={"up": {"px": [[0, y, "#1a1a1f"] for y in range(0, 9, 2)]}}), name="abdomen"),
        ]),
        B("head", [0, 3, -2], [C([-1.5, 2, -4], [3, 2, 2], P("#35b6a0", "iri", c2="#1b7d8a", hl=True, faces={"north": {"px": [[1, 1, "#193b3b"]]}}))], parent="body"),
        B("wing_fl", [1, 4, -1.5], [C([1, 4, -1.5], [8, 0, 2], wing)], parent="body", rot=[0, 8, 0]),
        B("wing_fr", [-1, 4, -1.5], [C([-9, 4, -1.5], [8, 0, 2], wing, mirror=True)], parent="body", rot=[0, -8, 0]),
        B("wing_bl", [1, 4, 0.5], [C([1, 3.99, 0.5], [7, 0, 2], wing)], parent="body", rot=[0, -8, 0]),
        B("wing_br", [-1, 4, 0.5], [C([-8, 3.99, 0.5], [7, 0, 2], wing, mirror=True)], parent="body", rot=[0, 8, 0]),
    ]
    bones += legs("body", [(0.5, 2, -1.5), (0.5, 2, -0.5), (0.5, 2, 0.5)], 2, P("#222226"), fan=[30, 0, -30])
    fly = merge(flap("wing_fl", "wing_fr", 0.08, 40, -25, extra=[0, 8]), flap("wing_bl", "wing_br", 0.08, -25, 40, extra=[0, -8]),
                {f"leg_{s}{i}": {"rotation": hold([40, 0, 0])} for s in "lr" for i in (1, 2, 3)},
                {"body": {"rotation": hold([-4, 0, 0])}})
    return {"id": "dragonfly", "seed": 23, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(bob("body", 4, 0.1),
                                           {"wing_fl": {"rotation": [kf(0, [0, 0, 0]), kf(3.7, [0, 0, 0]), kf(3.85, [0, 0, 12]), kf(4, [0, 0, 0])]},
                                            "wing_fr": {"rotation": [kf(0, [0, 0, 0]), kf(3.7, [0, 0, 0]), kf(3.85, [0, 0, -12]), kf(4, [0, 0, 0])]}})},
        "fly": {"len": 0.08, "bones": fly},
    }}


DUNG = P("#6b4a2b", "spots", c2="#4e3520", d=0.25, n=22)


def dung_beetle():
    shell = P("#231d1a", "vstripe", c2="#2f2723", per=2, hl=True)
    bones = [
        B("body", [0, 3, 0], [
            C([-2.5, 1, -1], [5, 3, 5], shell),
            C([-2.5, 1, -3], [5, 2, 2], P("#1f1a17", hl=True)),
        ]),
        B("head", [0, 2, -3], [C([-2, 1, -5], [4, 1, 2], P("#1c1714", faces={"north": {"px": [[0, 0, "#3a302a"], [1, 0, "#2a221e"], [2, 0, "#3a302a"], [3, 0, "#2a221e"]]}})),
                               C([-1, 2, -4.5], [2, 1, 1], P("#1c1714", faces={"north": {"px": [[0, 0, "#5a4a3a"], [1, 0, "#5a4a3a"]]}}))], parent="body"),
        B("ball", [0, 3, -9], [C([-3, 1, -11], [6, 4, 4], DUNG), C([-2, 0, -11], [4, 6, 4], DUNG), C([-2, 1, -12], [4, 4, 6], DUNG)]),
    ]
    bones += legs2("body", [(2, 2, -2), (2.5, 2, 0.5), (2, 2, 3)], 2, 3, P("#1e1916"), fan=[40, 0, -35], lift=25, splay=20)
    return {"id": "dung_beetle", "seed": 24, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": bob("body", 3, 0.15)},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 20, 10), {"ball": {"rotation": cycle(1.0, [[0, 0, 0], [-90, 0, 0], [-180, 0, 0], [-270, 0, 0]])}})},
    }}


def cave_weta():
    pale = P("#c9b391", "stripe", c2="#9c8462", per=2, hl=True)
    bones = [
        B("body", [0, 4, 0], [
            C([-1.5, 2, -3], [3, 3, 3], P("#c2aa86", hl=True)),
            C([-1.5, 1.5, 0], [3, 4, 5], pale),
            C([-1, 1.5, 5], [2, 2, 2], pale),
        ]),
        B("head", [0, 3.5, -3], [C([-1.5, 1.5, -5], [3, 3, 2], P("#b89f7b", faces={"north": {"px": [[0, 0, "#20190f"], [2, 0, "#20190f"]]}}))], parent="body", rot=[-20, 0, 0]),
        B("hind_l", [1.5, 3, 2], [C([1.5, 2.5, 2], [1, 2, 7], P("#b69c77", "stripe", c2="#8a7050", per=2))], parent="body", rot=[40, 0, -10]),
        B("hshin_l", [2, 2.5, 8.5], [C([1.5, 2.5, 2], [1, 1, 7], P("#8a7050"))], parent="hind_l", rot=[-85, 0, 0]),
        B("hind_r", [-1.5, 3, 2], [C([-2.5, 2.5, 2], [1, 2, 7], P("#b69c77", "stripe", c2="#8a7050", per=2))], parent="body", rot=[40, 0, 10]),
        B("hshin_r", [-2, 2.5, 8.5], [C([-2.5, 2.5, 2], [1, 1, 7], P("#8a7050"))], parent="hind_r", rot=[-85, 0, 0]),
    ]
    bones += antennae("head", 0.5, 3.5, -5, 14, P("#7a6448"), up=20, out=25)
    bones += legs2("body", [(1.5, 2.5, -2.5), (1.5, 2.5, -0.5)], 3, 4, P("#a88f6a"), fan=[35, -10], lift=30, splay=15)
    hop = merge({"hind_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [-50, 0, 0]), kf(0.6, [0, 0, 0])]},
                 "hind_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [-50, 0, 0]), kf(0.6, [0, 0, 0])]},
                 "hshin_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [70, 0, 0]), kf(0.6, [0, 0, 0])]},
                 "hshin_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [70, 0, 0]), kf(0.6, [0, 0, 0])]}}, antenna_idle(0.6, 15))
    return {"id": "cave_weta", "seed": 25, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": antenna_idle(4, 14)},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 20, 12, n=2), antenna_idle(0.5, 10))},
        "hop": {"len": 0.6, "loop": False, "bones": hop},
    }}


# ================================================================ RARE

def walking_stick():
    twig = P("#7c6a42", "stripe", c2="#65552f", per=4, n=14)
    bones = [
        B("body", [0, 3, 0], [
            C([-0.5, 2.5, -6], [1, 1, 6], twig),
            C([-0.5, 2.5, 0], [1, 1, 8], dict(twig, c="#76643c")),
        ]),
        B("head", [0, 3, -6], [C([-0.5, 2.5, -8], [1, 1, 2], P("#6e5d36", faces={"north": {"px": [[0, 0, "#2d2616"]]}}))], parent="body"),
        B("tail", [0, 3, 8], [C([-0.5, 2.5, 8], [1, 1, 3], P("#6a5932"))], parent="body", rot=[8, 0, 0]),
    ]
    bones += antennae("head", 0.3, 3, -8, 6, P("#5a4b2a"), up=10, out=12)
    bones += legs2("body", [(0.5, 3, -5), (0.5, 3, -0.5), (0.5, 3, 4)], 4, 4, P("#6a5932"), fan=[45, 5, -40], lift=20, splay=18)
    return {"id": "walking_stick", "seed": 31, "bones": bones, "anims": {
        # stick insects rock like a twig in the wind
        "idle": {"len": 3, "bones": merge(sway("body", 3, 4, axis=2), antenna_idle(3, 5))},
        "walk": {"len": 0.8, "bones": merge(tripod_walk(0.8, 18, 10), sway("body", 0.8, 3, axis=2))},
    }}


def jewel_beetle():
    elytra = P("#23b86e", "iri", c2="#c9b23a", n=6, j=0.06, hl=True)
    bones = [
        B("body", [0, 2.5, 0], [
            C([-2, 1, -2], [4, 2, 3], elytra),
            C([-1.5, 1, 1], [3, 2, 3], elytra),
            C([-1, 1, 4], [2, 1, 1], elytra),
            C([-1.5, 0.5, -2], [3, 1, 6], P("#1d5a4a")),
        ]),
        B("pronotum", [0, 2.5, -2], [C([-1.5, 1, -3.5], [3, 2, 2], P("#c9452f", "iri", c2="#e6a13a", j=0.06, hl=True))], parent="body"),
        B("head", [0, 2, -3.5], [C([-1, 1, -4.5], [2, 1, 1], P("#2a7a5e", faces={"north": {"px": [[0, 0, "#0f2a22"], [1, 0, "#0f2a22"]]}}))], parent="body"),
        B("wing_l", [0, 2.9, -1], [C([0, 2.9, -1], [2, 0, 5], WING_CLEAR)], parent="body"),
        B("wing_r", [0, 2.9, -1], [C([-2, 2.9, -1], [2, 0, 5], WING_CLEAR)], parent="body"),
    ]
    bones += antennae("head", 0.5, 1.5, -4.5, 2, P("#1b4d3f"), up=15, out=30)
    bones += legs("body", [(1.5, 1, -1.5), (2, 1, 0.5), (1.5, 1, 2.5)], 2, P("#1e6b52"), fan=[25, 0, -25])
    fly = merge({"wing_l": {"scale": hold([2, 1, 1])}, "wing_r": {"scale": hold([2, 1, 1])}, "body": {"rotation": hold([10, 0, 0])}},
                flap("wing_l", "wing_r", 0.09, 50, -20),
                {f"leg_{s}{i}": {"rotation": hold([30, 0, 0])} for s in "lr" for i in (1, 2, 3)})
    return {"id": "jewel_beetle", "seed": 32, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": antenna_idle(2, 10)},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35), antenna_idle(0.35, 8))},
        "fly": {"len": 0.09, "bones": fly},
    }}


def stag_beetle():
    shell = P("#4a2616", "grad", c2="#2f170d", hl=True, n=8)
    mand = P("#7c3a1f", "grad", c2="#4f2312", hl=True)
    bones = [
        B("body", [0, 4, 0], [
            C([-3, 1.5, -1], [6, 3, 7], dict(shell, faces={"up": {"px": col(2, 7, "#2a130a") + col(3, 7, "#2a130a")}})),
            C([-3, 1.5, -4], [6, 3, 3], P("#1f1510", hl=True)),
        ]),
        B("head", [0, 3.5, -4], [C([-3, 1.5, -7], [6, 2, 3], P("#2a1a12", hl=True, faces={"east": {"px": [[1, 0, "#6e5a3c"]]}, "west": {"px": [[1, 0, "#6e5a3c"]]}}))], parent="body"),
        B("mand_l", [1.5, 2.5, -7], [C([1, 2, -13], [1, 1, 6], mand), C([0, 2, -10], [1, 1, 1], mand), C([0, 2, -13], [1, 1, 1], mand)], parent="head", rot=[10, -15, 0]),
        B("mand_r", [-1.5, 2.5, -7], [C([-2, 2, -13], [1, 1, 6], mand), C([-1, 2, -10], [1, 1, 1], mand), C([-1, 2, -13], [1, 1, 1], mand)], parent="head", rot=[10, 15, 0]),
    ]
    bones += antennae("head", 2.5, 2.5, -7, 3, P("#1d140e"), up=10, out=45)
    bones += legs2("body", [(3, 2.5, -3), (3, 2.5, 0), (3, 2.5, 3)], 3, 4, P("#1f1510"), fan=[40, 0, -35], lift=25, splay=20)
    spar = {"mand_l": {"rotation": cycle(0.5, [[0, 0, 0], [5, -20, 0], [0, 20, 0]])},
            "mand_r": {"rotation": cycle(0.5, [[0, 0, 0], [5, 20, 0], [0, -20, 0]])},
            "body": {"rotation": cycle(0.5, [[0, 0, 0], [-12, 0, 0], [0, 0, 0]])}}
    return {"id": "stag_beetle", "seed": 33, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(3, 8), sway("mand_l", 3, 4, axis=1), sway("mand_r", 3, 4, axis=1, offset=0.5))},
        "walk": {"len": 0.6, "bones": merge(tripod_walk(0.6, 20, 10), antenna_idle(0.6, 6))},
        "spar": {"len": 0.5, "bones": spar},
    }}


def glowworm():
    body = P("#d8e4cf", "stripe", c2="#b9c9ae", per=2, n=6)
    tail = P("#8ff0ff", glow=True, n=4)
    thread = P("#cfe6ee", alpha=0.35, n=0)
    drop = "#b8fbff"
    bones = [
        B("body", [0, 15, 0], [
            C([-1, 14, -4], [2, 1, 6], body),
            C([-1, 14, 2], [2, 1, 2], tail, name="lantern"),
            C([-0.5, 14.2, -5], [1, 1, 1], P("#3a4034")),
        ]),
        B("threads", [0, 14, 0], [], parent="body"),
    ]
    # sticky silk threads with glowing droplets
    specs = [(-1.5, -2, 10), (0.5, -3, 13), (1.5, 0, 8), (-0.5, 1, 12), (0.5, 3, 9), (-1.5, 2, 6), (1.5, -1, 11)]
    for i, (x, z, ln) in enumerate(specs):
        px = [[0, y, drop, "glow"] for y in range(1, ln, 3)]
        bones.append(B(f"thread_{i}", [x, 14, z], [C([x, 14 - ln, z], [0, ln, 1], dict(thread, px=px))], parent="threads"))
    anim = {}
    for i, (x, z, ln) in enumerate(specs):
        anim.update(sway(f"thread_{i}", 3 + i * 0.37, 3 + i % 3, axis=0 if i % 2 else 2, offset=i * 0.13))
    return {"id": "glowworm", "seed": 34, "bones": bones, "anims": {
        "idle": {"len": 6, "bones": merge(anim, sway("body", 6, 3, axis=1))},
    }}


# ================================================================ EPIC

def hercules_beetle():
    elytra = P("#b9a766", "spots", c2="#2a2419", d=0.08, hl=True, n=10)
    black = P("#16130f", hl=True)
    bones = [
        B("body", [0, 5, 0], [
            C([-4, 2, -2], [8, 4, 9], dict(elytra, faces={"up": {"px": col(3, 9, "#2a2419") + col(4, 9, "#2a2419")}})),
            C([-3.5, 1.5, -2], [7, 1, 8], P("#1a1612")),
        ]),
        B("pronotum", [0, 5, -2], [C([-3.5, 2, -6], [7, 4, 4], black)], parent="body"),
        # long thoracic horn curving forward over the head
        B("horn_top", [0, 5.5, -5], [C([-1, 5, -14], [2, 1, 9], P("#1a1612", faces={"down": {"c": "#7a5a2a", "pat": "vstripe", "c2": "#5a3f1c"}})),
                                     C([-0.5, 3.5, -14], [1, 2, 1], black)], parent="pronotum", rot=[-8, 0, 0]),
        B("head", [0, 3, -6], [C([-2, 2, -8], [4, 2, 2], P("#1a1612", faces={"east": {"px": [[0, 0, "#7b6a4a"]]}, "west": {"px": [[-1, 0, "#7b6a4a"]]}}))], parent="body"),
        B("horn_low", [0, 3, -8], [C([-0.5, 2.5, -13], [1, 1, 5], black), C([-0.5, 3.5, -13], [1, 1, 1], black)], parent="head", rot=[15, 0, 0]),
    ]
    bones += antennae("head", 1.5, 3, -8, 2, P("#16130f"), up=0, out=45)
    bones += legs2("body", [(3.5, 3, -4), (4, 3, -0.5), (4, 3, 3.5)], 4, 5, P("#1a1612"), fan=[40, 0, -35], lift=25, splay=20)
    raise_horn = {"pronotum": {"rotation": cycle(1.2, [[0, 0, 0], [15, 0, 0], [15, 0, 0]])},
                  "head": {"rotation": cycle(1.2, [[0, 0, 0], [-12, 0, 0], [-12, 0, 0]])}}
    return {"id": "hercules_beetle", "seed": 41, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(antenna_idle(4, 6), bob("body", 4, 0.2, (0, 0, 0)))},
        "walk": {"len": 0.8, "bones": merge(tripod_walk(0.8, 18, 8), bob("body", 0.4, 0.2))},
        "horn": {"len": 1.2, "bones": raise_horn},
    }}


def ember_beetle():
    crust = P("#2a2323", "spots", c2="#ff7a1a", d=0.16, glow="c2", hl=True, n=14)
    bones = [
        B("body", [0, 3, 0], [
            C([-2.5, 1, -2], [5, 3, 6], crust),
            C([-2, 0.5, -2], [4, 1, 6], P("#3a1a10", "spots", c2="#ffb347", d=0.2, glow="c2")),
        ]),
        B("pronotum", [0, 3, -2], [C([-2, 1, -4], [4, 2, 2], P("#1f1a1a", "spots", c2="#ff9a2a", d=0.2, glow="c2"))], parent="body"),
        B("head", [0, 2, -4], [C([-1.5, 1, -5.5], [3, 2, 2], P("#1b1616", faces={"north": {"px": [[0, 0, "#ffd24a", "glow"], [2, 0, "#ffd24a", "glow"]]}}))], parent="body"),
    ]
    bones += antennae("head", 1, 2.5, -5.5, 3, P("#3a2020"), up=20, out=30)
    bones += legs2("body", [(2, 2, -1.5), (2.5, 2, 0.5), (2, 2, 2.5)], 2, 3, P("#241c1c"), fan=[35, 0, -30], lift=25, splay=20)
    return {"id": "ember_beetle", "seed": 42, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": merge(antenna_idle(2, 10), bob("body", 2, 0.15))},
        "walk": {"len": 0.4, "bones": merge(tripod_walk(0.4), antenna_idle(0.4, 8))},
    }}


def sculk_mite():
    shell = P("#0f2a33", "spots", c2="#2ee6f0", d=0.1, glow="c2", hl=True, n=10)
    bones = [
        B("body", [0, 3, 0], [
            C([-2.5, 1, -2], [5, 3, 5], shell),
            C([-2, 4, -1.5], [4, 1, 4], dict(shell, d=0.15)),
            C([-2, 0.5, -2], [4, 1, 5], P("#0a1d24")),
        ]),
        B("head", [0, 2, -2], [C([-1, 1, -3.5], [2, 1.5, 2], P("#132f38", faces={"north": {"px": [[0, 0, "#7ff9ff", "glow"], [1, 0, "#7ff9ff", "glow"]]}})),
                               C([-0.5, 1, -4.5], [1, 1, 1], P("#0b2229"))], parent="body"),
        # sensor tendrils like a sculk sensor
        B("tendril_l", [1, 5, 0], [C([1, 5, 0], [0, 4, 1], P("#1b5b66", "grad", c2="#39f0ff", glow="c2"))], parent="body", rot=[0, 0, -15]),
        B("tendril_r", [-1, 5, 0], [C([-1, 5, 0], [0, 4, 1], P("#1b5b66", "grad", c2="#39f0ff", glow="c2"))], parent="body", rot=[0, 0, 15]),
    ]
    bones += legs2("body", [(2, 2, -1.5), (2.5, 2, -0.2), (2.5, 2, 1.2), (2, 2, 2.5)], 2, 3, P("#0c242b"),
                   fan=(40, 12, -12, -40), lift=25, splay=20)
    alert = merge({"tendril_l": {"rotation": cycle(0.3, [[0, 0, 10], [0, 0, 25]])},
                   "tendril_r": {"rotation": cycle(0.3, [[0, 0, -10], [0, 0, -25]])},
                   "body": {"position": hold([0, 0.5, 0])}})
    return {"id": "sculk_mite", "seed": 43, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(sway("tendril_l", 3, 8, axis=2), sway("tendril_r", 3, 8, axis=2, offset=0.5))},
        "walk": {"len": 0.35, "bones": merge(tripod_walk(0.35, 18, 10, n=4), sway("tendril_l", 0.7, 6, axis=0), sway("tendril_r", 0.7, 6, axis=0))},
        "alert": {"len": 0.3, "bones": alert},
    }}


# ================================================================ LEGENDARY

def golden_scarab():
    gold = P("#f2c94c", "iri", c2="#b8860b", hl=True, n=8)
    bones = [
        B("body", [0, 3, 0], [
            C([-3, 1, -1], [6, 3, 6], dict(gold, faces={"up": {"px": col(2, 6, "#8f6a12") + col(3, 6, "#8f6a12")}})),
            C([-2.5, 0.5, -1], [5, 1, 6], P("#7a5a10")),
        ]),
        B("pronotum", [0, 3, -1], [C([-2.5, 1, -3.5], [5, 3, 3], P("#f5d36a", "iri", c2="#c79a1c", hl=True, faces={"up": {"px": [[1, 1, "#2f7fb5"], [3, 1, "#2f7fb5"]]}}))], parent="body"),
        # rake-toothed clypeus
        B("head", [0, 2, -3.5], [C([-2.5, 1, -5.5], [5, 1, 2], P("#e8bc3a", faces={"north": {"px": [[x, 0, "#8f6a12"] for x in range(0, 5, 2)]}})),
                                 C([-1.5, 2, -5], [3, 1, 1], P("#d9ab2c", faces={"north": {"px": [[0, 0, "#1f4f7a"], [2, 0, "#1f4f7a"]]}}))], parent="body"),
        B("wing_l", [0, 3.9, 0], [C([0, 3.9, 0], [3, 0, 5], WING_CLEAR)], parent="body"),
        B("wing_r", [0, 3.9, 0], [C([-3, 3.9, 0], [3, 0, 5], WING_CLEAR)], parent="body"),
    ]
    bones += legs2("body", [(2.5, 2, -2.5), (3, 2, 0.5), (2.5, 2, 3.5)], 2, 3, P("#b8860b", hl=True), fan=[40, 0, -35], lift=25, splay=20)
    fly = merge({"wing_l": {"scale": hold([2, 1, 1.2])}, "wing_r": {"scale": hold([2, 1, 1.2])}, "body": {"rotation": hold([12, 0, 0])}},
                flap("wing_l", "wing_r", 0.1, 50, -20))
    return {"id": "golden_scarab", "seed": 51, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": bob("body", 3, 0.15)},
        "walk": {"len": 0.45, "bones": tripod_walk(0.45)},
        "fly": {"len": 0.1, "bones": fly},
    }}


def void_moth():
    wingp = P("#1c0f2e", "spots", c2="#e6b3ff", d=0.07, glow="c2", n=10)
    eye = "#ff4fd8"
    fur = P("#cbb7e6", n=16, hl=True)
    bones = [
        B("body", [0, 3, 0], [
            C([-1.5, 1.5, -2.5], [3, 3, 3], fur),
            C([-1, 1.5, 0.5], [2, 2, 5], P("#2a1845", "stripe", c2="#b58af0", per=2, glow="c2")),
        ]),
        B("head", [0, 3, -2.5], [C([-1, 2, -3.5], [2, 2, 1], P("#b9a2d9", faces={"north": {"px": [[0, 0, eye, "glow"], [1, 0, eye, "glow"]]}}))], parent="body"),
        B("wing_l", [1.5, 4, -2], [C([1.5, 4, -4], [7, 0, 6], dict(wingp, faces={"up": {"px": [[4, 2, eye, "glow"], [4, 3, eye, "glow"], [5, 2, "#ffffff", "glow"]]}})),
                                    C([1.5, 3.99, 1], [6, 0, 5], dict(wingp, c="#231238"))], parent="body", rot=[0, -8, -8]),
        B("wing_r", [-1.5, 4, -2], [C([-8.5, 4, -4], [7, 0, 6], dict(wingp, faces={"up": {"px": [[2, 2, eye, "glow"], [2, 3, eye, "glow"], [1, 2, "#ffffff", "glow"]]}})),
                                     C([-7.5, 3.99, 1], [6, 0, 5], dict(wingp, c="#231238"))], parent="body", rot=[0, 8, 8]),
        B("antenna_l", [0.5, 3.5, -3.5], [C([0.5, 3.5, -7.5], [2, 0, 4], P("#8f6fc0", "vstripe", c2="#5c3f8a", per=2))], parent="head", rot=[30, 25, 0]),
        B("antenna_r", [-0.5, 3.5, -3.5], [C([-2.5, 3.5, -7.5], [2, 0, 4], P("#8f6fc0", "vstripe", c2="#5c3f8a", per=2))], parent="head", rot=[30, -25, 0]),
    ]
    bones += legs("body", [(1, 2, -2), (1.5, 2, -1), (1, 2, 0)], 2, P("#9c86c4"), fan=[25, 0, -25])
    return {"id": "void_moth", "seed": 52, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(antenna_idle(4, 6),
                                           {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(2, [0, 0, 14]), kf(4, [0, 0, 0])]},
                                            "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(2, [0, 0, -14]), kf(4, [0, 0, 0])]}})},
        "walk": {"len": 0.5, "bones": merge(tripod_walk(0.5, 18, 8), antenna_idle(0.5, 6))},
        "fly": {"len": 0.3, "bones": merge(flap("wing_l", "wing_r", 0.3, 65, -30), bob("body", 0.3, 0.6),
                                           {f"leg_{s}{i}": {"rotation": hold([30, 0, 0])} for s in "lr" for i in (1, 2, 3)})},
    }}


SPECS = {f.__name__: f for f in [
    ladybug, aphid, firefly, cricket, pill_bug, water_strider,
    monarch, silk_moth, dragonfly, dung_beetle, cave_weta,
    walking_stick, jewel_beetle, stag_beetle, glowworm,
    hercules_beetle, ember_beetle, sculk_mite,
    golden_scarab, void_moth,
]}
