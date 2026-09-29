"""Expansion group B: moths, butterflies, flies, wasp, cicada, katydid, locust, shulker mite.

Wing art is hand-drawn with `art()`: rows are drawn as seen from ABOVE with the bug's head at the top and the body on
the LEFT, i.e. the +X wing (wing_l). The same paint mirrored (mirror=True) gives the -X wing. '.' cuts the pixel out
(alpha 0) so wings get real outlines; every other character goes through the palette.
"""
from bugs import *

CUT = "#00000000"


# ---------------------------------------------------------------- helpers (group B)

def art(rows, pal, glow=""):
    """Detail pixels for the up/down face of a horizontal plane from a top-down drawing (see module doc)."""
    h, w = len(rows), len(rows[0])
    out = []
    for r, line in enumerate(rows):
        assert len(line) == w, f"ragged art row {r}: {line!r}"
        for c, ch in enumerate(line):
            col = CUT if ch == "." else pal[ch]
            out.append([w - 1 - c, h - 1 - r, col] + (["glow"] if ch in glow else []))
    return out


def wing(up, pal, down=None, dpal=None, glow="", dglow=None, n=0):
    """Paint for a plane wing: `up` art on top, `down` art (default: same drawing, `dpal` colours) underneath."""
    first = next(ch for ch in "".join(up) if ch != ".")
    return P(pal[first], n=n, faces={"up": {"px": art(up, pal, glow)},
                                     "down": {"px": art(down or up, dpal or pal, glow if dglow is None else dglow)}})


def rod(o, s, color, inflate=-0.3, **kw):
    """A thin rod (visible from every side): an integer cube shrunk by a negative inflate."""
    return C(o, s, color if isinstance(color, dict) else P(color, n=0), inflate=inflate, **kw)


def club_antennae(parent, x, y, z, length, stalk, knob, up=35, out=18):
    """Butterfly antennae: thin stalks with a club at the tip."""
    bones = []
    for side, sx in (("l", 1), ("r", -1)):
        bones.append(B(f"antenna_{side}", [sx * x, y, z],
                       [rod([sx * x - 0.5, y - 0.5, z - length], [1, 1, length], stalk, inflate=-0.38),
                        rod([sx * x - 0.5, y - 0.5, z - length - 0.6], [1, 1, 1], knob, inflate=-0.2)],
                       parent=parent, rot=[up, sx * out, 0]))
    return bones


def rod_antennae(parent, x, y, z, length, color, up=25, out=20, inflate=-0.38, name="antenna"):
    return [B(f"{name}_{side}", [sx * x, y, z], [rod([sx * x - 0.5, y - 0.5, z - length], [1, 1, length], color, inflate=inflate)],
              parent=parent, rot=[up, sx * out, 0]) for side, sx in (("l", 1), ("r", -1))]


def feather_antennae(parent, x, y, z, length, width, c, c2, up=30, out=25):
    """Moth antennae: flat feathery combs (a plane with vein stripes)."""
    paint = P(c, "vstripe", c2=c2, per=2, n=6)
    return [B("antenna_l", [x, y, z], [C([x, y, z - length], [width, 0, length], paint)], parent=parent, rot=[up, out, 0]),
            B("antenna_r", [-x, y, z], [C([-x - width, y, z - length], [width, 0, length], paint, mirror=True)], parent=parent, rot=[up, -out, 0])]


def thin_legs(parent, hips, length, color, fan=(25, 0, -25), down=None):
    return legs(parent, hips, length, P(color, n=0), thick=1, sz=0, fan=list(fan), down=down)


def rod_legs2(parent, hips, femur, tibia, color, fan=(30, 0, -30), lift=25, splay=15, inflate=-0.3, tibia_color=None):
    """Two-segment rod legs (thin, visible from every side). Same bone names as legs2: leg_<s><i> / knee_<s><i>."""
    out = []
    for i, (hx, hy, hz) in enumerate(hips, start=1):
        yaw = fan[i - 1] if i - 1 < len(fan) else 0
        for side, sx in (("l", 1), ("r", -1)):
            fo = [hx if sx > 0 else -hx - femur, hy - 0.5, hz - 0.5]
            out.append(B(f"leg_{side}{i}", [sx * hx, hy, hz], [rod(fo, [femur, 1, 1], color, inflate)],
                         parent=parent, rot=[0, sx * yaw, sx * lift]))
            kx = sx * (hx + femur - 0.5)
            to = [kx - 0.5, hy - tibia, hz - 0.5]
            out.append(B(f"knee_{side}{i}", [kx, hy, hz], [rod(to, [1, tibia, 1], tibia_color or color, inflate)],
                         parent=f"leg_{side}{i}", rot=[0, 0, sx * splay - sx * lift]))
    return out


def tuck_legs(n=3, x=30, prefix="leg"):
    return {f"{prefix}_{s}{i}": {"rotation": hold([x, 0, 0])} for s in "lr" for i in range(1, n + 1)}


def rep(period, values, count):
    """Like cycle() but repeated `count` times (for fast loops inside a longer animation)."""
    n = len(values)
    out = []
    for k in range(count):
        for i in range(n):
            out.append(kf(round(period * (k + i / n), 4), values[i]))
    out.append(kf(round(period * count, 4), values[0]))
    return out


def flap_n(left, right, period, count, up, down, extra=(0, 0)):
    e = extra
    return {left: {"rotation": rep(period, [[e[0], e[1], up], [e[0], -e[1], down]], count)},
            right: {"rotation": rep(period, [[e[0], -e[1], -up], [e[0], e[1], -down]], count)}}


def perch_wings(left, right, open_=15, shut=80, length=3.0):
    """Butterfly at rest: wings held together above the back, opening slowly now and then."""
    t = length
    return {left: {"rotation": [kf(0, [0, 0, shut]), kf(t * 0.4, [0, 0, shut]), kf(t * 0.6, [0, 0, open_]),
                                kf(t * 0.8, [0, 0, open_]), kf(t, [0, 0, shut])]},
            right: {"rotation": [kf(0, [0, 0, -shut]), kf(t * 0.4, [0, 0, -shut]), kf(t * 0.6, [0, 0, -open_]),
                                 kf(t * 0.8, [0, 0, -open_]), kf(t, [0, 0, -shut])]}}


def moth_rest(left, right, amp=12, length=4.0):
    """Moth at rest: wings stay in their rest pose with a double shiver now and then (anims are relative to rest)."""
    t = length

    def seq(s):
        a, b = [0, 0, 0], [0, 0, s * amp]
        return [kf(0, a), kf(t * 0.7, a), kf(t * 0.75, b), kf(t * 0.8, a), kf(t * 0.85, b), kf(t * 0.9, a), kf(t, a)]
    return {left: {"rotation": seq(1)}, right: {"rotation": seq(-1)}}


def blink(bone, t_on, t_off, length):
    """Scale 1 between t_on and t_off, 0 otherwise (instant switches)."""
    e = 0.001
    ks = [kf(0, [0, 0, 0] if t_on > 0 else [1, 1, 1])]
    if t_on > 0:
        ks += [kf(t_on - e, [0, 0, 0]), kf(t_on, [1, 1, 1])]
    ks += [kf(t_off - e, [1, 1, 1]), kf(t_off, [0, 0, 0])]
    if t_off < length:
        ks += [kf(length, [0, 0, 0])]
    return {bone: {"scale": ks}}


# ================================================================ MAYFLY

def mayfly():
    pale, seg, dark = "#f2e3a0", "#c9ad5c", "#6b5a2a"
    wpal = {"v": "#ece6c4b0", "w": "#f8fcf240", "e": "#e0d8aac0", "s": "#9a8a54e0"}
    wing_art = ["svvvv",
                "evwwe",
                ".wwwe",
                "..wwe",
                "...we",
                "....e"]
    hind_art = ["ve",
                "e."]
    body = P(pale, n=8, hl=True)
    bones = [
        B("body", [0, 3, 0], [C([-0.5, 2.5, -2], [1, 2, 3], dict(body, faces={"up": {"px": [[0, 1, seg], [0, 2, seg]]}}))]),
        B("head", [0, 3.5, -2], [C([-1, 3, -3], [2, 1, 1], P(pale, faces={"north": {"px": [[0, 0, "#2a2418"], [1, 0, "#2a2418"]]},
                                                                            "east": {"px": [[-1, 0, "#2a2418"]]}, "west": {"px": [[0, 0, "#2a2418"]]}}))], parent="body"),
        B("abdomen", [0, 3, 1], [C([-0.5, 2.5, 1], [1, 1, 3], P(pale, "stripe", c2=seg, per=2))], parent="body", rot=[-12, 0, 0]),
        B("tail", [0, 3, 4], [C([-0.5, 2.5, 4], [1, 1, 3], P("#e9d68a", "stripe", c2=seg, per=2))], parent="abdomen", rot=[-18, 0, 0]),
        B("filaments", [0, 3, 7], [rod([-0.5, 2.5, 7], [1, 1, 7], "#b9a45c", inflate=-0.4),
                                   rod([-0.5, 2.5, 7], [1, 1, 7], "#b9a45c", inflate=-0.4, r=[0, 16, 0], p=[0, 3, 7]),
                                   rod([-0.5, 2.5, 7], [1, 1, 7], "#b9a45c", inflate=-0.4, r=[0, -16, 0], p=[0, 3, 7])],
          parent="tail", rot=[-10, 0, 0]),
        B("wing_l", [0.5, 4.5, -2], [C([0.5, 4.5, -2.5], [5, 0, 6], wing(wing_art, wpal)),
                                     C([0.5, 4.49, 2.5], [2, 0, 2], wing(hind_art, wpal))], parent="body", rot=[0, 0, 84]),
        B("wing_r", [-0.5, 4.5, -2], [C([-5.5, 4.5, -2.5], [5, 0, 6], wing(wing_art, wpal), mirror=True),
                                      C([-2.5, 4.49, 2.5], [2, 0, 2], wing(hind_art, wpal), mirror=True)], parent="body", rot=[0, 0, -84]),
    ]
    bones += rod_antennae("head", 0.5, 4, -3, 2, dark, up=20, out=20)
    bones += thin_legs("body", [(0.5, 2.5, -1.5), (0.5, 2.5, -0.5), (0.5, 2.5, 0.5)], 3, "#b8a05a", fan=(40, 5, -30))
    idle = merge({"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.35, [0, 0, -24]), kf(2.5, [0, 0, 0]), kf(4, [0, 0, 0])]},
                  "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.35, [0, 0, 24]), kf(2.5, [0, 0, 0]), kf(4, [0, 0, 0])]}},
                 sway("abdomen", 4, 4), sway("filaments", 2, 6, axis=1), antenna_idle(4, 8), bob("body", 4, 0.15))
    fly = merge(flap_n("wing_l", "wing_r", 0.2, 5, 4, -75),
                {"body": {"position": cycle(1.0, [[0, 0, 0], [0, 1.5, 0], [0, 2.2, 0], [0, 0.8, 0]]),
                          "rotation": cycle(1.0, [[-20, 0, 0], [-25, 0, 0]])}},
                sway("abdomen", 1.0, 6), sway("filaments", 0.5, 8, axis=1), tuck_legs(3, 20))
    return {"id": "mayfly", "seed": 71, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": idle},
        "fly": {"len": 1.0, "bones": fly},
    }}


# ================================================================ MOSQUITO

def mosquito():
    K, Wt = "#2a2622", "#e4e2dc"
    wpal = {"v": "#5d686cd0", "w": "#d6e2e660", "e": "#9aa6aaa0"}
    wart = ["vvvve",
            "wwwe."]
    thor = P(K, n=6, faces={"up": {"px": [[0, 0, Wt], [1, 0, Wt], [0, 1, "#8a8680"], [1, 1, "#8a8680"]]},
                          "east": {"px": [[0, 1, Wt]]}, "west": {"px": [[1, 1, Wt]]}})
    abd = P(K, "stripe", c2=Wt, per=2, n=4, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})
    blood = P("#c01c24", "stripe", c2="#7e0c14", per=2, n=10, hl=True,
              faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})
    bones = [
        B("body", [0, 5, 0], [C([-1, 4, -2], [2, 2, 2], thor)]),
        B("head", [0, 4.5, -2], [C([-1, 4, -3], [2, 1, 1], P("#1c1916", faces={"north": {"px": [[0, 0, "#454a58"], [1, 0, "#454a58"]]}})),
                                 rod([-0.5, 4, -6], [1, 1, 3], "#1c1916", inflate=-0.4, r=[-18, 0, 0], p=[0, 4.5, -3])], parent="body"),
        B("abdomen", [0, 5, 0], [C([-0.5, 4.5, 0], [1, 1, 4], abd)], parent="body", rot=[-10, 0, 0]),
        B("blood", [0, 5, 0], [C([-0.5, 4.5, 0], [1, 1, 4], blood, inflate=-0.2)], parent="abdomen"),
        B("wing_l", [0.5, 6, -1], [C([0.5, 6, -1.5], [5, 0, 2], wing(wart, wpal))], parent="body", rot=[0, -78, 4]),
        B("wing_r", [-0.5, 6, -1], [C([-5.5, 6, -1.5], [5, 0, 2], wing(wart, wpal), mirror=True)], parent="body", rot=[0, 78, -4]),
        B("antenna_l", [0.3, 4.8, -3], [C([0.3, 4.8, -5], [1, 0, 2], P("#3a3530", "vstripe", c2="#6a655c", per=2))], parent="head", rot=[30, 20, 0]),
        B("antenna_r", [-0.3, 4.8, -3], [C([-1.3, 4.8, -5], [1, 0, 2], P("#3a3530", "vstripe", c2="#6a655c", per=2))], parent="head", rot=[30, -20, 0]),
    ]
    bones += rod_legs2("body", [(0.5, 4.5, -1.5), (0.5, 4.5, -1), (0.5, 4.5, -0.5)], 3, 6, "#2e2a26",
                       fan=(45, 0, -45), lift=35, splay=12, inflate=-0.42, tibia_color="#4a4640")
    hide_blood = {"blood": {"scale": hold([0, 0, 0])}}
    idle = merge(hide_blood, antenna_idle(2.5, 8), bob("body", 2.5, 0.2),
                 {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(1.8, [0, 0, 0]), kf(1.9, [0, 18, 8]), kf(2.0, [0, 0, 0]), kf(2.5, [0, 0, 0])]},
                  "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(1.8, [0, 0, 0]), kf(1.9, [0, -18, -8]), kf(2.0, [0, 0, 0]), kf(2.5, [0, 0, 0])]}})
    dangle = {f"leg_{s}{i}": {"rotation": hold([0, 0, (1 if s == 'l' else -1) * -45])} for s in "lr" for i in (1, 2, 3)}
    dangle.update({f"knee_{s}{i}": {"rotation": hold([-30, 0, 0])} for s in "lr" for i in (1, 2, 3)})
    fly_wings = {"wing_l": {"rotation": rep(0.05, [[0, 68, 50], [0, 68, -35]], 8)},
                 "wing_r": {"rotation": rep(0.05, [[0, -68, -50], [0, -68, 35]], 8)}}
    fly = merge(hide_blood, fly_wings, dangle, bob("body", 0.4, 0.4), {"body": {"rotation": hold([-8, 0, 0])}},
                antenna_idle(0.4, 5))
    fed = merge(fly_wings, dangle, bob("body", 0.4, 0.25), {"body": {"rotation": hold([-4, 0, 0])}},
                {"abdomen": {"scale": hold([1.6, 1.6, 1.2]), "rotation": hold([12, 0, 0])},
                 "blood": {"scale": hold([2.0, 2.0, 1.12])}})
    return {"id": "mosquito", "seed": 72, "bones": bones, "anims": {
        "idle": {"len": 2.5, "bones": idle},
        "fly": {"len": 0.4, "bones": fly},
        "fed": {"len": 0.4, "bones": fed},
    }}


# ================================================================ CICADA

def cicada():
    blk, grn, dgrn = "#1f2a1e", "#5f9a3c", "#2e4a26"
    red = "#d0301e"
    wpal = {"G": "#3f8a3cf0", "v": "#6fb862b8", "w": "#e2f0de48", "t": "#9fd08a90"}
    wart = ["wwG",
            "vwG",
            "wvG",
            "wwG",
            "vwG",
            "wvG",
            "twv",
            "wtv",
            ".vv"]
    pron = P(blk, n=8, hl=True, faces={"up": {"px": art(["gKKg",
                                                        "KggK",
                                                        "gKKg"], {"g": grn, "K": blk})}})
    abd = P("#1b2219", "stripe", c2="#34422c", per=2, n=6, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})
    head = P(blk, faces={"up": {"px": [[1, 0, red], [2, 0, red], [0, 1, grn], [3, 1, grn]]},
                         "north": {"px": [[1, 0, grn], [2, 0, grn], [1, 1, "#3a4a34"], [2, 1, "#3a4a34"]]}})
    bones = [
        B("body", [0, 3, 0], [C([-2, 1, -3], [4, 3, 3], pron)]),
        B("abdomen", [0, 2.5, 0], [C([-1.5, 0.7, 0], [3, 3, 4], abd), C([-1, 1.2, 4], [2, 2, 1], P("#1b2219"))], parent="body"),
        B("head", [0, 2.5, -3], [C([-2, 1.5, -4.5], [4, 2, 2], head),
                                 C([2, 2, -4.5], [1, 1, 1], P(red, hl=True, n=6), inflate=0.15),
                                 C([-3, 2, -4.5], [1, 1, 1], P(red, hl=True, n=6), inflate=0.15)], parent="body"),
        B("wing_l", [0.3, 4.2, -2.5], [C([0.3, 4.2, -2.5], [3, 0, 9], wing(wart, wpal))], parent="body", rot=[3, 0, -20]),
        B("wing_r", [-0.3, 4.2, -2.5], [C([-3.3, 4.2, -2.5], [3, 0, 9], wing(wart, wpal), mirror=True)], parent="body", rot=[3, 0, 20]),
    ]
    bones += rod_antennae("head", 1, 3, -4.5, 1, dgrn, up=10, out=35, inflate=-0.3)
    bones += legs("body", [(1.5, 1.5, -2.5), (2, 1.5, -1), (1.5, 1.5, 0.5)], 3, P("#2a3522"), fan=[35, 5, -30])
    idle = merge(bob("abdomen", 2.5, 0.12),
                 {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.0, [0, 0, 0]), kf(2.1, [0, 0, 8]), kf(2.2, [0, 0, 0]), kf(3, [0, 0, 0])]},
                  "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(2.0, [0, 0, 0]), kf(2.1, [0, 0, -8]), kf(2.2, [0, 0, 0]), kf(3, [0, 0, 0])]}},
                 antenna_idle(3, 6))
    walk = merge(tripod_walk(0.4, 20, 10), antenna_idle(0.4, 6))
    fly = merge({"wing_l": {"rotation": rep(0.07, [[0, 65, 45], [0, 65, -15]], 1)},
                 "wing_r": {"rotation": rep(0.07, [[0, -65, -45], [0, -65, 15]], 1)}},
                {"body": {"rotation": hold([10, 0, 0])}}, bob("body", 0.07, 0.2), tuck_legs(3, 35))
    buzz = merge({"abdomen": {"scale": rep(0.04, [[1, 1, 1], [1.12, 1.12, 1.05]], 20)},
                  "wing_l": {"rotation": rep(0.04, [[0, 0, 0], [0, 3, 6]], 20)},
                  "wing_r": {"rotation": rep(0.04, [[0, 0, 0], [0, -3, -6]], 20)},
                  "body": {"position": rep(0.04, [[0, 0, 0], [0.08, 0, 0], [0, 0, 0], [-0.08, 0, 0]], 20)}})
    return {"id": "cicada", "seed": 73, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "walk": {"len": 0.4, "bones": walk},
        "fly": {"len": 0.07, "bones": fly},
        "buzz": {"len": 0.8, "loop": False, "bones": buzz},
    }}


# ================================================================ KATYDID

def katydid():
    g, G, d = "#6cc24a", "#8fdc68", "#3f8a2c"
    # the forewing is a leaf: dark rim, pale midrib, side veins
    leaf = {"l": "#3f8a2c", "L": "#6cc24a", "M": "#c4f09a", "v": "#96d86c"}
    leaf_art = [".lll.",
                "lLvLl",
                "lvMLl",
                "lLMvl",
                "lvMLl",
                "lLMvl",
                "lvMLl",
                ".LMvl",
                "..Ml.",
                "..l.."]
    bones = [
        B("body", [0, 4, 0], [C([-1, 2.5, -2.5], [2, 3, 3], P(g, n=8, hl=True, faces={"up": {"px": col(0, 3, G) + col(1, 3, G)}})),
                              C([-1, 2.5, 0.5], [2, 2, 5], P(g, "stripe", c2=d, per=2, n=6))]),
        B("head", [0, 4.5, -2.5], [C([-1, 2.5, -4.5], [2, 3, 2], P(G, n=8, hl=True, faces={
            "east": {"px": [[-1, 0, "#2b3a1c"]]}, "west": {"px": [[0, 0, "#2b3a1c"]]},
            "north": {"px": [[0, 2, "#c9a24a"], [1, 2, "#c9a24a"]]}}))], parent="body", rot=[-15, 0, 0]),
        B("wing_l", [0.2, 6, -1], [C([0.2, 6, -1.5], [5, 0, 10], wing(leaf_art, leaf))], parent="body", rot=[-4, 0, -58]),
        B("wing_r", [-0.2, 6, -1], [C([-5.2, 6, -1.5], [5, 0, 10], wing(leaf_art, leaf), mirror=True)], parent="body", rot=[-4, 0, 58]),
        B("hind_l", [1, 3.5, 1], [C([1, 2.5, 1], [1, 2, 6], P(g, "stripe", c2=G, per=3))], parent="body", rot=[35, 0, -8]),
        B("hshin_l", [1.5, 3, 7], [C([1, 3, 1.5], [1, 1, 5.5], P(d))], parent="hind_l", rot=[-75, 0, 0]),
        B("hind_r", [-1, 3.5, 1], [C([-2, 2.5, 1], [1, 2, 6], P(g, "stripe", c2=G, per=3))], parent="body", rot=[35, 0, 8]),
        B("hshin_r", [-1.5, 3, 7], [C([-2, 3, 1.5], [1, 1, 5.5], P(d))], parent="hind_r", rot=[-75, 0, 0]),
    ]
    bones += rod_antennae("head", 0.5, 5.2, -4.5, 16, "#5a8a3a", up=22, out=18, inflate=-0.42)
    bones += rod_legs2("body", [(1, 3, -2), (1, 3, -0.5)], 2, 4, d, fan=(35, -10), lift=30, splay=12, inflate=-0.25)
    hop = merge({"hind_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-45, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hind_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [-45, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hshin_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [60, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "hshin_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [60, 0, 0]), kf(0.5, [0, 0, 0])]},
                 "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.1, [14, 0, 0]), kf(0.5, [0, 0, 0])]}},
                antenna_idle(0.5, 14))
    sing = merge({"wing_l": {"rotation": rep(0.06, [[0, 0, 0], [0, 5, 7]], 10)},
                  "wing_r": {"rotation": rep(0.06, [[0, 0, 0], [0, -5, -7]], 10)}},
                 antenna_idle(0.6, 10))
    walk = merge(tripod_walk(0.45, 22, 10, n=2),
                 {"hind_l": {"rotation": cycle(0.45, [[0, 0, 0], [-7, 0, 0]])},
                  "hind_r": {"rotation": cycle(0.45, [[-7, 0, 0], [0, 0, 0]])}},
                 antenna_idle(0.45, 8))
    return {"id": "katydid", "seed": 74, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(antenna_idle(4, 14), bob("body", 4, 0.1))},
        "walk": {"len": 0.45, "bones": walk},
        "hop": {"len": 0.5, "loop": False, "bones": hop},
        "sing": {"len": 0.6, "loop": False, "bones": sing},
    }}


# ================================================================ LOCUST

def locust():
    y, Y, br, dk = "#c9a55a", "#e2c47a", "#8a6a34", "#5a4222"
    speck = P(y, "spots", c2=br, d=0.18, n=8, hl=True)
    tpal = {"b": "#9a7440", "B": "#6e5028", "t": "#c8a868", "k": "#4a361c"}
    teg = ["tbt",
           "bBt",
           "tbk",
           "Btb",
           "tkt",
           "bBt",
           "tbk",
           "kbt",
           "tBb",
           ".t."]
    hpal = {"p": "#e0506a", "P": "#f07a8a", "v": "#8a2a3a", "e": "#5a3a2a"}
    hwing = ["vpvPv.",
             "pvPvpv",
             "vPpvPv",
             "pvpPve",
             "vpPve.",
             "eee..."]
    bones = [
        B("body", [0, 4, 0], [C([-1.5, 2.5, -2.5], [3, 3, 3], dict(speck, faces={"up": {"px": col(1, 3, Y)}})),
                              C([-1, 2.5, 0.5], [2, 2, 6], P(y, "stripe", c2=br, per=2, n=8))]),
        B("head", [0, 4.5, -2.5], [C([-1.5, 2.5, -4.5], [3, 3, 2], P(Y, n=8, hl=True, faces={
            "east": {"px": [[-1, 0, dk], [-2, 0, dk]]}, "west": {"px": [[0, 0, dk], [1, 0, dk]]},
            "north": {"px": [[0, 1, br], [2, 1, br], [1, 2, "#a07a3a"]]}}))], parent="body", rot=[-12, 0, 0]),
        B("wing_l", [0.3, 5.5, -2], [C([0.3, 5.5, -2], [3, 0, 10], wing(teg, tpal))], parent="body", rot=[-3, 4, -40]),
        B("wing_r", [-0.3, 5.5, -2], [C([-3.3, 5.5, -2], [3, 0, 10], wing(teg, tpal), mirror=True)], parent="body", rot=[-3, -4, 40]),
        B("hwing_l", [0.5, 5.3, -1], [C([0.5, 5.3, -1], [6, 0, 6], wing(hwing, hpal))], parent="body"),
        B("hwing_r", [-0.5, 5.3, -1], [C([-6.5, 5.3, -1], [6, 0, 6], wing(hwing, hpal), mirror=True)], parent="body"),
        B("hind_l", [1.5, 3.5, 1], [C([1.5, 2.5, 1], [1, 2, 6], P(y, "stripe", c2=dk, per=2, faces={"up": {"c": Y}}))], parent="body", rot=[35, 0, -6]),
        B("hshin_l", [2, 3, 7], [C([1.5, 3, 1.5], [1, 1, 5.5], P("#a8683a", "stripe", c2="#8a4a2a", per=3))], parent="hind_l", rot=[-75, 0, 0]),
        B("hind_r", [-1.5, 3.5, 1], [C([-2.5, 2.5, 1], [1, 2, 6], P(y, "stripe", c2=dk, per=2, faces={"up": {"c": Y}}))], parent="body", rot=[35, 0, 6]),
        B("hshin_r", [-2, 3, 7], [C([-2.5, 3, 1.5], [1, 1, 5.5], P("#a8683a", "stripe", c2="#8a4a2a", per=3))], parent="hind_r", rot=[-75, 0, 0]),
    ]
    bones += rod_antennae("head", 0.6, 5, -4.5, 4, br, up=25, out=22, inflate=-0.35)
    bones += rod_legs2("body", [(1.5, 3, -2), (1.5, 3, -0.5)], 2, 4, "#a8884a", fan=(35, -10), lift=30, splay=12, inflate=-0.25)
    hide_h = {"hwing_l": {"scale": hold([0, 0, 0])}, "hwing_r": {"scale": hold([0, 0, 0])}}
    walk = merge(hide_h, tripod_walk(0.4, 22, 10, n=2),
                 {"hind_l": {"rotation": cycle(0.4, [[0, 0, 0], [-8, 0, 0]])},
                  "hind_r": {"rotation": cycle(0.4, [[-8, 0, 0], [0, 0, 0]])}}, antenna_idle(0.4, 8))
    fly = merge({"wing_l": {"rotation": rep(0.12, [[0, 55, 70], [0, 55, 20]], 1)},
                 "wing_r": {"rotation": rep(0.12, [[0, -55, -70], [0, -55, -20]], 1)}},
                flap("hwing_l", "hwing_r", 0.12, 40, -35),
                {"body": {"rotation": hold([6, 0, 0])}}, tuck_legs(2, 40), antenna_idle(0.12, 4))
    return {"id": "locust", "seed": 75, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(hide_h, antenna_idle(3, 12), bob("body", 3, 0.1))},
        "walk": {"len": 0.4, "bones": walk},
        "fly": {"len": 0.12, "bones": fly},
    }}


# ================================================================ PAPER WASP

def paper_wasp():
    Y, K, O = "#f2c21e", "#1c1812", "#e0842a"
    wpal = {"v": "#4a3a2cd8", "w": "#7a6650a0", "e": "#5a4838c0"}
    wart = ["vvvvv",
            "wwwe.",
            "wwe.."]
    thor = P(K, n=6, hl=True, faces={"up": {"px": [[0, 2, Y], [1, 2, Y], [0, 0, Y], [1, 0, Y]]},
                                   "east": {"px": [[1, 0, Y]]}, "west": {"px": [[1, 0, Y]]}})
    abd = P(K, "stripe", c2=Y, per=2, n=6, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"},
                                                  "up": {"px": [[0, 1, K], [1, 1, K]]}})
    face = P(Y, n=6, faces={"north": {"px": [[0, 0, K], [1, 0, K], [0, 1, K], [1, 1, "#2a2016"]]},
                            "up": {"px": row(0, 2, K) + row(1, 2, K)},
                            "east": {"px": [[0, 0, K], [1, 0, K]]}, "west": {"px": [[0, 0, K], [1, 0, K]]}})
    bones = [
        B("body", [0, 4, 0], [C([-1, 3, -2.5], [2, 2, 3], thor), rod([-0.5, 3, 0.5], [1, 1, 1], K, inflate=-0.15)]),
        B("head", [0, 4, -2.5], [C([-1, 3, -4.5], [2, 2, 2], face),
                                 C([-0.5, 2.6, -4.7], [1, 1, 1], P(O), inflate=-0.2)], parent="body"),
        B("abdomen", [0, 4, 1.5], [C([-1, 3, 1.5], [2, 2, 4], abd),
                                   C([-0.5, 3.5, 5.5], [1, 1, 1], P(Y)),
                                   rod([-0.5, 3.5, 6.2], [1, 1, 1], K, inflate=-0.35)], parent="body", rot=[8, 0, 0]),
        B("wing_l", [0.5, 5, -1.5], [C([0.5, 5, -1.5], [5, 0, 3], wing(wart, wpal))], parent="body", rot=[0, -78, 4]),
        B("wing_r", [-0.5, 5, -1.5], [C([-5.5, 5, -1.5], [5, 0, 3], wing(wart, wpal), mirror=True)], parent="body", rot=[0, 78, -4]),
    ]
    for side, sx in (("l", 1), ("r", -1)):
        bones.append(B(f"antenna_{side}", [sx * 0.5, 4.5, -4.5], [rod([sx * 0.5 - 0.5, 4, -7], [1, 1, 2.5], O, inflate=-0.36)],
                       parent="head", rot=[35, sx * 25, 0]))
        bones.append(B(f"antenna_tip_{side}", [sx * 0.5, 4.5, -7], [rod([sx * 0.5 - 0.5, 4, -9], [1, 1, 2], O, inflate=-0.36)],
                       parent=f"antenna_{side}", rot=[-55, sx * 10, 0]))
    bones += rod_legs2("body", [(1, 3.5, -2), (1, 3.5, -1), (1, 3.5, 0)], 2, 4, O, fan=(35, 0, -35), lift=30, splay=14, inflate=-0.3)
    fly_w = {"wing_l": {"rotation": rep(0.05, [[0, 66, 45], [0, 66, -30]], 10)},
             "wing_r": {"rotation": rep(0.05, [[0, -66, -45], [0, -66, 30]], 10)}}
    dangle = {f"leg_{s}{i}": {"rotation": hold([0, 0, (1 if s == 'l' else -1) * -40])} for s in "lr" for i in (1, 2, 3)}
    dangle.update({f"knee_{s}{i}": {"rotation": hold([-30, 0, 0])} for s in "lr" for i in (1, 2, 3)})
    fly = merge(fly_w, dangle, bob("body", 0.5, 0.4), {"body": {"rotation": hold([-12, 0, 0])},
                                                       "abdomen": {"rotation": cycle(0.5, [[12, 0, 0], [20, 0, 0]])}},
                antenna_idle(0.5, 6))
    return {"id": "paper_wasp", "seed": 76, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(antenna_idle(1.5, 12), {"abdomen": {"rotation": cycle(1.5, [[0, 0, 0], [-6, 0, 0]])}},
                                           {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(2.4, [0, 0, 0]), kf(2.5, [0, 8, 6]), kf(2.6, [0, 0, 0]), kf(3, [0, 0, 0])]},
                                            "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(2.4, [0, 0, 0]), kf(2.5, [0, -8, -6]), kf(2.6, [0, 0, 0]), kf(3, [0, 0, 0])]}})},
        "walk": {"len": 0.4, "bones": merge(tripod_walk(0.4, 20, 10), antenna_idle(0.4, 10))},
        "fly": {"len": 0.5, "bones": fly},
    }}


# ================================================================ HAWK MOTH

def hawk_moth():
    fur, dfur, K, Wt, O = "#8a7c6a", "#6a5c4c", "#1c1814", "#f0ece4", "#e8862a"
    fpal = {"g": "#8e8272", "G": "#a89c8a", "d": "#5a4e40", "k": "#3a3028"}
    fore = ["kddddd",
            "gGgdGg",
            "gdgGd."]
    hpal = {"o": O, "O": "#f4a040", "k": "#3a2a1c"}
    hind = ["oOok",
            "ooOk",
            "okk."]
    abd = P(dfur, "stripe", c2="#5a4c3e", per=2, n=10,
            faces={"east": {"px": [[0, 0, Wt], [1, 0, Wt], [2, 0, "#3a2e24"]]}, "west": {"px": [[0, 0, Wt], [1, 0, Wt], [2, 0, "#3a2e24"]]}})
    bones = [
        B("body", [0, 4, 0], [C([-1.5, 2.5, -2.5], [3, 3, 3], P(fur, n=18, hl=True)),
                              C([-1.5, 2.5, 0.5], [3, 3, 3], abd),
                              C([-1, 3, 3.5], [2, 2, 1], P(K, faces={"east": {"px": [[0, 0, Wt]]}, "west": {"px": [[0, 0, Wt]]}}))]),
        B("head", [0, 4, -2.5], [C([-1, 2.5, -3.5], [2, 2, 1], P(fur, n=12, faces={"north": {"px": [[0, 0, K], [1, 0, K], [0, 1, "#b0a490"], [1, 1, "#b0a490"]]}})),
                                 C([1, 3.2, -3.5], [1, 1, 1], P("#241c16"), inflate=-0.1),
                                 C([-2, 3.2, -3.5], [1, 1, 1], P("#241c16"), inflate=-0.1)], parent="body"),
        B("proboscis", [0, 3, -3.5], [rod([-0.5, 2.5, -8.5], [1, 1, 5], "#3a2e24", inflate=-0.38)], parent="head", rot=[8, 0, 0]),
        B("tail_fan", [0, 4, 4.5], [C([-2, 4, 4.5], [4, 0, 2], P(K, faces={"up": {"px": art(["KWKW", "WKWK"], {"K": K, "W": Wt})},
                                                                            "down": {"px": art(["KWKW", "WKWK"], {"K": K, "W": Wt})}}))],
          parent="body", rot=[-10, 0, 0]),
        B("wing_l", [1.5, 5.2, -2], [C([1.5, 5.2, -2.5], [6, 0, 3], wing(fore, fpal)), C([1.5, 5.19, -0.5], [4, 0, 3], wing(hind, hpal))],
          parent="body", rot=[0, -30, -6]),
        B("wing_r", [-1.5, 5.2, -2], [C([-7.5, 5.2, -2.5], [6, 0, 3], wing(fore, fpal), mirror=True),
                                      C([-5.5, 5.19, -0.5], [4, 0, 3], wing(hind, hpal), mirror=True)], parent="body", rot=[0, 30, 6]),
    ]
    bones += club_antennae("head", 0.5, 4.2, -3.5, 3, "#4a3e32", "#2a221a", up=30, out=25)
    bones += thin_legs("body", [(1, 2.5, -2), (1.5, 2.5, -1), (1, 2.5, 0)], 2, "#5a4e40")
    fly = merge({"wing_l": {"rotation": rep(0.06, [[0, 22, 60], [0, 12, -40]], 10)},
                 "wing_r": {"rotation": rep(0.06, [[0, -22, -60], [0, -12, 40]], 10)}},
                {"body": {"rotation": hold([-18, 0, 0])}}, bob("body", 0.6, 0.3), tuck_legs(3, 40),
                {"tail_fan": {"scale": hold([1.3, 1, 1.2])}},
                {"proboscis": {"rotation": cycle(0.6, [[6, 0, 0], [12, 0, 0]])}})
    idle = merge(moth_rest("wing_l", "wing_r", 14, 3), antenna_idle(3, 6),
                 {"proboscis": {"rotation": [kf(0, [0, 0, 0]), kf(1.5, [22, 0, 0]), kf(3, [0, 0, 0])]}})
    return {"id": "hawk_moth", "seed": 77, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": idle},
        "fly": {"len": 0.6, "bones": fly},
    }}


# ================================================================ SAKURA MOTH

def sakura_moth():
    # one cherry blossom per wing: white petals, deep pink heart, on a rose ground
    pal = {"p": "#eea2bc", "W": "#fff6fa", "V": "#fcdce8", "c": "#d63c78", "q": "#d8729a"}
    fore = ["qqqqq",
            "pVWVp",
            "pWcWq",
            "pVWVq",
            "ppqq."]
    hind = ["VWVp",
            "WcWq",
            "VWVq",
            "pqq."]
    dpal = {"p": "#f4d2de", "W": "#fdf0f4", "V": "#fae6ee", "c": "#e27aa0", "q": "#e0a6ba"}
    fur = P("#f5c5d5", n=16, hl=True)
    bones = [
        B("body", [0, 3, 0], [C([-1, 1.5, -2], [2, 2, 3], fur),
                              C([-1.5, 1.5, -2.5], [3, 2, 1], P("#fdf8f8", n=10, hl=True), inflate=0.3),
                              C([-1, 1.5, 1], [2, 2, 4], P("#f2b6ca", "stripe", c2="#e496b0", per=2, n=10))]),
        B("head", [0, 3, -2.5], [C([-1, 2, -3.5], [2, 2, 1], P("#f7d3df", faces={"north": {"px": [[0, 0, "#3a2030"], [1, 0, "#3a2030"]]}}))], parent="body"),
        B("wing_l", [1, 3.6, -2], [C([1, 3.6, -3], [5, 0, 5], wing(fore, pal, dpal=dpal)), C([1, 3.59, 1], [4, 0, 4], wing(hind, pal, dpal=dpal))],
          parent="body", rot=[0, -8, -8]),
        B("wing_r", [-1, 3.6, -2], [C([-6, 3.6, -3], [5, 0, 5], wing(fore, pal, dpal=dpal), mirror=True),
                                    C([-5, 3.59, 1], [4, 0, 4], wing(hind, pal, dpal=dpal), mirror=True)], parent="body", rot=[0, 8, 8]),
    ]
    bones += feather_antennae("head", 0.5, 3.5, -3.5, 3, 2, "#f08cb0", "#c85a86", up=30, out=25)
    bones += thin_legs("body", [(1, 1.5, -1.5), (1, 1.5, -0.5), (1, 1.5, 0.5)], 2, "#e8a8c0")
    return {"id": "sakura_moth", "seed": 78, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(moth_rest("wing_l", "wing_r", 14, 4), antenna_idle(4, 6))},
        "fly": {"len": 0.3, "bones": merge(flap("wing_l", "wing_r", 0.3, 65, -30), bob("body", 0.3, 0.6), tuck_legs())},
    }}


# ================================================================ LUNA MOTH

def luna_moth():
    pal = {"p": "#7a3a58", "P": "#9a5070", "g": "#a8e6b4", "G": "#c4f6cc", "h": "#e0ffe6", "y": "#f0dc6a", "e": "#6a2a70", "o": "#e8c060"}
    fore = ["pppppp.",
            "gGGGGpp",
            "gGhyGg.",
            "gGyeyg.",
            "gGGyg..",
            "gGg...."]
    hind = ["gGGGg.",
            "gGyGGg",
            "gyeyGg",
            "gGyGg.",
            "ghGg..",
            ".gG..."]
    tail = ["gGg.",
            ".gG.",
            ".gG.",
            "..gG",
            "..gG",
            "..Go",
            ".oo."]
    dpal = dict(pal, g="#98d8a4", G="#b4ecc0", h="#c8f4d0", p="#8a5068")
    glow = "hye"
    fur = P("#f4f4ea", n=14, hl=True)
    bones = [
        B("body", [0, 3, 0], [C([-1, 1.5, -2.5], [2, 2, 3], fur),
                              C([-1, 1.5, 0.5], [2, 2, 4], P("#ecf2e4", "stripe", c2="#d4e8d0", per=2, n=8))]),
        B("head", [0, 3, -2.5], [C([-1, 1.5, -3.5], [2, 2, 1], P("#f0f0e4", faces={"north": {"px": [[0, 0, "#2a3a2a"], [1, 0, "#2a3a2a"]]}}))], parent="body"),
        B("wing_l", [1, 3.6, -2], [C([1, 3.6, -4], [7, 0, 6], wing(fore, pal, dpal=dpal, glow=glow)),
                                   C([1, 3.59, 0], [6, 0, 6], wing(hind, pal, dpal=dpal, glow=glow))], parent="body", rot=[0, -6, -6]),
        B("wing_r", [-1, 3.6, -2], [C([-8, 3.6, -4], [7, 0, 6], wing(fore, pal, dpal=dpal, glow=glow), mirror=True),
                                    C([-7, 3.59, 0], [6, 0, 6], wing(hind, pal, dpal=dpal, glow=glow), mirror=True)], parent="body", rot=[0, 6, 6]),
        B("tail_l", [3, 3.58, 5.5], [C([2, 3.58, 5], [4, 0, 7], wing(tail, pal, dpal=dpal, glow=glow))], parent="wing_l"),
        B("tail_r", [-3, 3.58, 5.5], [C([-6, 3.58, 5], [4, 0, 7], wing(tail, pal, dpal=dpal, glow=glow), mirror=True)], parent="wing_r"),
    ]
    bones += feather_antennae("head", 0.5, 3.5, -3.5, 3, 2, "#d8b858", "#a88830", up=30, out=25)
    bones += thin_legs("body", [(1, 1.5, -1.5), (1, 1.5, -0.5), (1, 1.5, 0.5)], 2, "#b86a92")
    idle = merge(moth_rest("wing_l", "wing_r", 12, 4), antenna_idle(4, 6),
                 sway("tail_l", 4, 8), sway("tail_r", 4, 8, offset=0.25))
    fly = merge(flap("wing_l", "wing_r", 0.4, 65, -30), bob("body", 0.4, 0.7), tuck_legs(),
                {"tail_l": {"rotation": cycle(0.4, [[20, 0, 0], [-25, 0, 0]])},
                 "tail_r": {"rotation": cycle(0.4, [[20, 0, 0], [-25, 0, 0]])}})
    return {"id": "luna_moth", "seed": 79, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": idle},
        "fly": {"len": 0.4, "bones": fly},
    }}


# ================================================================ MORPHO

def morpho():
    up = {"K": "#100d12", "W": "#f4f2ea", "A": "#5fd4ff", "B": "#2a9cff", "C": "#1766e0", "D": "#0d3a9a"}
    dn = {"K": "#3a2616", "W": "#f4ecdc", "b": "#7a5230", "t": "#b88c58", "Y": "#fad44c", "E": "#20140c", "D": "#5a3a20"}
    fore = ["KKKK...",
            "DBAKKK.",
            "DCBAAKW",
            "DCAAAKK",
            "DBAAKK.",
            "KDBK..."]
    fore_dn = ["KKKK...",
               "btbKKK.",
               "bttYtKW",
               "btYEYtK",
               "bttYKK.",
               "Kbtb..."]
    hind = ["DBAAAK",
            "DCAAKK",
            "DBAAK.",
            "KDBK..",
            "KK...."]
    hind_dn = ["btYtYK",
               "bYEYEK",
               "btYtY.",
               "Kbtb..",
               "KK...."]
    fw = wing(fore, up, fore_dn, dn, glow="ABC", dglow="")
    hw = wing(hind, up, hind_dn, dn, glow="ABC", dglow="")
    bones = [
        B("body", [0, 2, 0], [C([-0.5, 1, -3], [1, 1, 3], P("#33271e", n=10)),
                              C([-0.5, 1, 0], [1, 1, 4], P("#2a2019", "stripe", c2="#3d2f24", per=2, n=8))]),
        B("head", [0, 1.5, -3], [C([-1, 1, -4], [2, 1, 1], P("#241a14", faces={"north": {"px": [[0, 0, "#0a0808"], [1, 0, "#0a0808"]]}}))], parent="body"),
        B("wing_l", [0.5, 2, -1], [C([0.5, 2, -4], [7, 0, 6], fw), C([0.5, 1.99, 0], [6, 0, 5], hw)], parent="body"),
        B("wing_r", [-0.5, 2, -1], [C([-7.5, 2, -4], [7, 0, 6], fw, mirror=True), C([-6.5, 1.99, 0], [6, 0, 5], hw, mirror=True)], parent="body"),
    ]
    bones += club_antennae("head", 0.5, 2, -4, 4, "#1a1410", "#3a2e24")
    bones += thin_legs("body", [(0.5, 1, -2), (0.5, 1, -1), (0.5, 1, 0)], 2, "#1a1410")
    return {"id": "morpho", "seed": 61, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(perch_wings("wing_l", "wing_r", 10, 82, 3), antenna_idle(3, 6))},
        "fly": {"len": 0.32, "bones": merge(flap("wing_l", "wing_r", 0.32, 75, -30), bob("body", 0.32, 0.8),
                                            {"body": {"rotation": hold([-10, 0, 0])}}, tuck_legs())},
    }}


# ================================================================ OWL BUTTERFLY

def owl_butterfly():
    up = {"k": "#241810", "d": "#4a3020", "t": "#b88c5a", "T": "#dcb482", "l": "#5a3a22",
          "b": "#5a3c26", "Y": "#f0c040", "E": "#120a06", "W": "#ffffff", "o": "#8a6a3a"}
    dn = dict(up, t="#b4a080", T="#d4c4a4", l="#6a5a48", b="#8a765c", d="#6a5a44", m="#9a866a", k="#3a2a1c")
    fore = ["kkkkkk.",
            "dtTTtTk",
            "dllTllk",
            "dTTlTTk",
            "dlltlk.",
            "kdTk..."]
    fore_dn = ["kkkkkk.",
               "dmtmlmk",
               "dtmltmk",
               "dmYYmlk",
               "dmYEk..",
               "kdmk..."]
    hind = ["dbbbbbk",
            "dboYYok",
            "dbYEEYk",
            "dbYEWY.",
            "dboYYk.",
            "kkbk..."]
    fw = wing(fore, up, fore_dn, dn)
    hw = wing(hind, up, hind, dn)
    bones = [
        B("body", [0, 2, 0], [C([-0.5, 1, -3], [1, 1, 3], P("#4a3424", n=12)),
                              C([-0.5, 1, 0], [1, 1, 5], P("#3a2a1c", "stripe", c2="#5a4230", per=2, n=8))]),
        B("head", [0, 1.5, -3], [C([-1, 1, -4], [2, 1, 1], P("#3a281a", faces={"north": {"px": [[0, 0, "#120a06"], [1, 0, "#120a06"]]}}))], parent="body"),
        B("wing_l", [0.5, 2, -1], [C([0.5, 2, -4], [7, 0, 6], fw), C([0.5, 1.99, 0], [7, 0, 6], hw)], parent="body"),
        B("wing_r", [-0.5, 2, -1], [C([-7.5, 2, -4], [7, 0, 6], fw, mirror=True), C([-7.5, 1.99, 0], [7, 0, 6], hw, mirror=True)], parent="body"),
    ]
    bones += club_antennae("head", 0.5, 2, -4, 4, "#2a1c12", "#4a3424")
    bones += thin_legs("body", [(0.5, 1, -2), (0.5, 1, -1), (0.5, 1, 0)], 2, "#2a1c12")
    return {"id": "owl_butterfly", "seed": 62, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(perch_wings("wing_l", "wing_r", 20, 82, 4), antenna_idle(4, 6))},
        "fly": {"len": 0.4, "bones": merge(flap("wing_l", "wing_r", 0.4, 70, -30), bob("body", 0.4, 0.9),
                                           {"body": {"rotation": hold([-10, 0, 0])}}, tuck_legs())},
    }}


# ================================================================ ATLAS MOTH

def atlas_moth():
    pal = {"R": "#5e1e10", "r": "#a0401e", "q": "#b8522a", "W": "#fff4e6", "k": "#241008", "p": "#f0c4b0",
           "o": "#c87838", "y": "#dcae52", "Y": "#f2d060", "E": "#140a06", "d": "#6a3a1a"}
    fore = ["RRrrrrrk..",
            "RrqrrrrkYY",
            "RrWWkrrkYE",
            "RrWkrrpkYY",
            "Rrkrrpoky.",
            "Rrrrpoyy..",
            "Rrrpoydy..",
            "RRpoyy...."]
    hind = ["Rrqrrpoy",
            "RrWWkpoy",
            "RrWkrpdy",
            "Rrkrpoy.",
            "Rrrpody.",
            "Rrpoyy..",
            "RRoy...."]
    dpal = dict(pal, R="#6e3020", r="#a85a38", q="#b86a44", o="#c89058", y="#d8b870", p="#e8c8b8")
    fw = wing(fore, pal, dpal=dpal)
    hw = wing(hind, pal, dpal=dpal)
    fur = P("#9a3e1e", n=16, hl=True)
    bones = [
        B("body", [0, 4, 0], [C([-1.5, 2, -3], [3, 3, 4], dict(fur, faces={"up": {"px": row(-1, 3, "#f0dcc8")}})),
                              C([-1, 2, 1], [2, 2, 6], P("#a8502c", "stripe", c2="#e0c8a8", per=2, n=10))]),
        B("head", [0, 4, -3], [C([-1, 2.5, -4], [2, 2, 1], P("#8a3a1c", n=10, faces={"north": {"px": [[0, 0, "#1a0a06"], [1, 0, "#1a0a06"]]}}))], parent="body"),
        B("wing_l", [1.5, 4.6, -2], [C([1.5, 4.6, -5], [10, 0, 8], fw), C([1.5, 4.59, 1], [8, 0, 7], hw)], parent="body", rot=[0, -4, -6]),
        B("wing_r", [-1.5, 4.6, -2], [C([-11.5, 4.6, -5], [10, 0, 8], fw, mirror=True), C([-9.5, 4.59, 1], [8, 0, 7], hw, mirror=True)],
          parent="body", rot=[0, 4, 6]),
    ]
    bones += feather_antennae("head", 0.5, 4.5, -4, 4, 2, "#c89a58", "#8a6030", up=30, out=28)
    bones += thin_legs("body", [(1, 2, -2.5), (1.5, 2, -1), (1, 2, 0.5)], 3, "#7a2e14")
    return {"id": "atlas_moth", "seed": 81, "bones": bones, "anims": {
        "idle": {"len": 5, "bones": merge(moth_rest("wing_l", "wing_r", 8, 5), antenna_idle(5, 5))},
        "fly": {"len": 0.6, "bones": merge(flap("wing_l", "wing_r", 0.6, 45, -25), bob("body", 0.6, 1.0),
                                           {"body": {"rotation": hold([-6, 0, 0])}}, tuck_legs())},
    }}


# ================================================================ SOUL MOTH

def soul_moth():
    pal = {"s": "#4e3a2b", "S": "#664c38", "d": "#2a1c14", "c": "#1fb8e6", "C": "#9ef6ff", "b": "#2a6e9a"}
    fore = ["sssSbc",
            "sdSdcC",
            "sSsSc.",
            "sdddc.",
            "sScc.."]
    hind = ["sSsbc",
            "sdSc.",
            "sScc.",
            "cc..."]
    fa = [".......",
          "......C",
          ".....C.",
          "......c",
          "....C..",
          "..c...."]
    fb = ["......C",
          "......c",
          "......C",
          ".....c.",
          ".....c.",
          "...C..."]
    ha = ["......",
          ".....c",
          "....C.",
          "..c...",
          "C.....",
          "......"]
    hb = [".....C",
          "....C.",
          ".....c",
          "...C..",
          "..c...",
          ".c...."]
    glow = "cCb"
    fw, hw = wing(fore, pal, glow=glow), wing(hind, pal, glow=glow)
    fur = P("#4a3628", n=18, hl=True)
    bones = [
        B("body", [0, 3, 0], [C([-1.5, 1.5, -2.5], [3, 3, 3], fur),
                              C([-1, 1.5, 0.5], [2, 2, 4], P("#3a2a20", "stripe", c2="#5a4434", per=2, n=10))]),
        B("head", [0, 3, -2.5], [C([-1, 2, -3.5], [2, 2, 1], P("#3a2a1e", faces={"north": {"px": [[0, 0, "#8ff8ff", "glow"], [1, 0, "#8ff8ff", "glow"]]},
                                                                               "east": {"px": [[-1, 0, "#3ee0ff", "glow"]]},
                                                                               "west": {"px": [[0, 0, "#3ee0ff", "glow"]]}}))], parent="body"),
        B("wing_l", [1.5, 4, -2], [C([1.5, 4, -4], [6, 0, 5], fw), C([1.5, 3.99, 0.5], [5, 0, 4], hw)], parent="body", rot=[0, -8, -8]),
        B("wing_r", [-1.5, 4, -2], [C([-7.5, 4, -4], [6, 0, 5], fw, mirror=True), C([-6.5, 3.99, 0.5], [5, 0, 4], hw, mirror=True)],
          parent="body", rot=[0, 8, 8]),
    ]
    for side, sx in (("l", 1), ("r", -1)):
        for tag, fo, ho in (("a", fa, ha), ("b", fb, hb)):
            f_x = 1.5 if sx > 0 else -8.5
            h_x = 1.5 if sx > 0 else -7.5
            bones.append(B(f"flame_{side}{tag}", [sx * 1.5, 4, -2],
                           [C([f_x, 4.02, -4], [7, 0, 6], wing(fo, pal, glow=glow), mirror=sx < 0),
                            C([h_x, 4.01, 0.5], [6, 0, 6], wing(ho, pal, glow=glow), mirror=sx < 0)], parent=f"wing_{side}"))
    bones += feather_antennae("head", 0.5, 4, -3.5, 3, 2, "#5a4232", "#3ac8e8", up=30, out=25)
    bones += thin_legs("body", [(1, 2, -2), (1.5, 2, -1), (1, 2, 0)], 2, "#3a2a1e")

    def flicker(length, step):
        out = {}
        n = int(round(length / step))
        for side in "lr":
            for tag, ph in (("a", 0), ("b", 1)):
                ks = []
                for i in range(n):
                    on = (i + ph) % 2 == 0
                    t = round(i * step, 4)
                    v = [1, 1, 1] if on else [0, 0, 0]
                    ks.append(kf(t, v))
                    ks.append(kf(round(t + step - 0.001, 4), v))
                ks.append(kf(length, ks[0][1]))
                out[f"flame_{side}{tag}"] = {"scale": ks}
        return out
    return {"id": "soul_moth", "seed": 82, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(moth_rest("wing_l", "wing_r", 12, 4), antenna_idle(4, 6), flicker(4, 0.25))},
        "fly": {"len": 0.3, "bones": merge(flap("wing_l", "wing_r", 0.3, 65, -30), bob("body", 0.3, 0.6), tuck_legs(), flicker(0.3, 0.15))},
    }}


# ================================================================ GUST MOTH

def gust_moth():
    pal = {"w": "#d8f4f260", "s": "#7fd0dcd8", "e": "#b0e6ecb0", "S": "#e8ffffe8"}
    fore = ["eeeee.",
            "wsssSw",
            "wswwsw",
            "wswSsw",
            "wswww."]
    hind = ["wsssw",
            "wswsw",
            "wsSsw",
            "ew..."]
    ring = P("#f2f6fc", n=6, hl=True)
    core = P("#9eaee6", "stripe", c2="#b8c4f0", per=2, n=6)
    cubes = [C([-1, 2, -3], [2, 2, 8], core)]
    for z in (-2, 0, 2, 4):
        cubes.append(C([-1.5, 1.5, z], [3, 3, 1], ring))
    bones = [
        B("body", [0, 3, 0], cubes),
        B("head", [0, 3, -3], [C([-1, 2, -4], [2, 2, 1], P("#e4ecf8", faces={"north": {"px": [[0, 0, "#2c3478"], [1, 0, "#2c3478"]]}}))], parent="body"),
        B("wing_l", [1.5, 4, -2], [C([1.5, 4, -4], [6, 0, 5], wing(fore, pal)), C([1.5, 3.99, 0.5], [5, 0, 4], wing(hind, pal))], parent="body", rot=[0, -8, -8]),
        B("wing_r", [-1.5, 4, -2], [C([-7.5, 4, -4], [6, 0, 5], wing(fore, pal), mirror=True), C([-6.5, 3.99, 0.5], [5, 0, 4], wing(hind, pal), mirror=True)],
          parent="body", rot=[0, 8, 8]),
    ]
    bones += feather_antennae("head", 0.5, 4, -4, 3, 2, "#c8d8f4", "#8a9ad8", up=30, out=25)
    bones += thin_legs("body", [(1, 2, -1.5), (1.5, 2, -0.5), (1, 2, 0.5)], 2, "#9aa8d8")
    gust = {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, -12, 48]), kf(0.25, [0, 78, -2]), kf(0.6, [0, 0, 0])]},
            "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, 12, -48]), kf(0.25, [0, -78, 2]), kf(0.6, [0, 0, 0])]},
            "body": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [-12, 0, 0]), kf(0.25, [10, 0, 0]), kf(0.6, [0, 0, 0])]}}
    return {"id": "gust_moth", "seed": 83, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(moth_rest("wing_l", "wing_r", 12, 4), antenna_idle(4, 8), bob("body", 4, 0.2))},
        "fly": {"len": 0.28, "bones": merge(flap("wing_l", "wing_r", 0.28, 65, -30), bob("body", 0.28, 0.6), tuck_legs())},
        "gust": {"len": 0.6, "loop": False, "bones": gust},
    }}


# ================================================================ ECHO MOTH

def echo_moth():
    pal = {"k": "#0b1c22", "K": "#133038", "c": "#3fe4e8", ".": CUT}
    # concentric sound-wave rings spreading from the body
    fore = ["cckKck",
            "kkckkc",
            "ckkckc",
            "kcKckc",
            "kckck."]
    hind = ["kckck",
            "cKkck",
            "kkck.",
            "cc..."]
    glow = "c"
    dpal = dict(pal, k="#10262c", K="#183a42", c="#2ab8c0")
    fw, hw = wing(fore, pal, dpal=dpal, glow=glow), wing(hind, pal, dpal=dpal, glow=glow)
    tendril = P("#16545e", "grad", c2="#3ff0ff", glow="c2", n=6)
    bones = [
        B("body", [0, 3, 0], [C([-1.5, 1.5, -2.5], [3, 3, 3], P("#10282e", n=14, hl=True)),
                              C([-1, 1.5, 0.5], [2, 2, 4], P("#0a1c22", "stripe", c2="#1a6a74", per=2, glow="c2", n=8))]),
        B("head", [0, 3, -2.5], [C([-1, 2, -3.5], [2, 2, 1], P("#0e2228", faces={"north": {"px": [[0, 0, "#7ff9ff", "glow"], [1, 0, "#7ff9ff", "glow"]]}}))], parent="body"),
        B("wing_l", [1.5, 4, -2], [C([1.5, 4, -4], [6, 0, 5], fw), C([1.5, 3.99, 0.5], [5, 0, 4], hw)], parent="body", rot=[0, -8, -8]),
        B("wing_r", [-1.5, 4, -2], [C([-7.5, 4, -4], [6, 0, 5], fw, mirror=True), C([-6.5, 3.99, 0.5], [5, 0, 4], hw, mirror=True)],
          parent="body", rot=[0, 8, 8]),
        B("tendril_l", [0.5, 4, -3], [C([0.5, 4, -3.5], [0, 4, 1], tendril), C([0, 4, -3], [1, 4, 0], tendril)], parent="head", rot=[-30, 0, -20]),
        B("tendril_r", [-0.5, 4, -3], [C([-0.5, 4, -3.5], [0, 4, 1], tendril), C([-1, 4, -3], [1, 4, 0], tendril)], parent="head", rot=[-30, 0, 20]),
    ]
    bones += thin_legs("body", [(1, 2, -2), (1.5, 2, -1), (1, 2, 0)], 2, "#0e2a30")
    tend = merge(sway("tendril_l", 3, 10, axis=2), sway("tendril_r", 3, 10, axis=2, offset=0.5))
    return {"id": "echo_moth", "seed": 84, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(moth_rest("wing_l", "wing_r", 12, 3), tend)},
        "fly": {"len": 0.3, "bones": merge(flap("wing_l", "wing_r", 0.3, 65, -30), bob("body", 0.3, 0.6), tuck_legs(),
                                           {"tendril_l": {"rotation": hold([-25, 0, 5])}, "tendril_r": {"rotation": hold([-25, 0, -5])}})},
    }}


# ================================================================ SHULKER MITE

def shulker_mite():
    pur, lpur, dpur = "#9a6b9a", "#b88fb8", "#6a4570"
    lid = P(pur, n=8, hl=True, faces={
        "up": {"c": lpur, "pat": "edge", "c2": pur},
        "north": {"px": row(-1, 6, dpur)}, "south": {"px": row(-1, 6, dpur)},
        "east": {"px": row(-1, 6, dpur)}, "west": {"px": row(-1, 6, dpur)}})
    base = P(pur, n=8, faces={"north": {"px": row(0, 6, lpur)}, "south": {"px": row(0, 6, lpur)},
                              "east": {"px": row(0, 6, lpur)}, "west": {"px": row(0, 6, lpur)}, "down": {"c": dpur}})
    body = P("#c6e05a", glow=True, n=10, faces={"north": {"px": [[0, 0, "#20301a"], [3, 0, "#20301a"], [0, 1, "#20301a"], [3, 1, "#20301a"],
                                                                    [1, 2, "#8aa83a"], [2, 2, "#8aa83a"]]}})
    bones = [
        B("body", [0, 2, 0], [C([-3, 0.5, -3], [6, 2, 6], base)]),
        B("core", [0, 2.5, 0], [C([-2, 1.5, -2], [4, 3, 4], body)], parent="body"),
        B("lid", [0, 2.5, 3], [C([-3, 2.5, -3], [6, 3, 6], lid)], parent="body", rot=[14, 0, 0]),
    ]
    bones += thin_legs("body", [(3, 1.2, -1.5), (3, 1.2, 0), (3, 1.2, 1.5)], 2, "#8aa83a", fan=(30, 0, -30), down=35)
    fly = merge({"lid": {"rotation": cycle(1.2, [[0, 0, 0], [20, 0, 0], [16, 0, 0], [2, 0, 0]])},
                 "body": {"position": cycle(1.2, [[0, 0, 0], [0, 1, 0]]), "rotation": cycle(2.4, [[0, 0, 0], [0, 8, 0], [0, 0, 0], [0, -8, 0]])},
                 "core": {"position": cycle(1.2, [[0, 0, 0], [0, 0.4, 0]])}},
                {f"leg_{s}{i}": {"rotation": cycle(0.6, [[0, 0, 0], [15, 0, 0]])} for s in "lr" for i in (1, 2, 3)})
    idle = merge({"lid": {"rotation": [kf(0, [0, 0, 0]), kf(2, [0, 0, 0]), kf(2.2, [-8, 0, 0]), kf(2.8, [-8, 0, 0]), kf(3.1, [8, 0, 0]), kf(4, [0, 0, 0])]}},
                 bob("core", 2, 0.2))
    return {"id": "shulker_mite", "seed": 85, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": idle},
        "fly": {"len": 2.4, "bones": fly},
    }}


SPECS = {f.__name__: f for f in [
    mayfly, mosquito, cicada, katydid, hawk_moth, sakura_moth, paper_wasp, locust,
    luna_moth, morpho, owl_butterfly, atlas_moth, soul_moth, gust_moth, shulker_mite, echo_moth,
]}
