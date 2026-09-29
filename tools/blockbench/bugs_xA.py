"""Expansion group A: ants, spiders, centipede/millipede, scorpion, isopod and friends.

Same conventions as bugs.py: pixels, facing north (-Z), feet on y=0.
Box-UV note (verified in previews): on an "up" face, pixel row 0 is the REAR (+Z) edge; use topg() to write
top-face pixel art front-to-rear.
Extra helpers here: two-segment legs with per-pair geometry and slimming inflate (jlegs), thin single-segment
legs (slim_legs), elbowed antennae (elbow_antennae), rolled-plane feelers visible from above (feelers),
a phase-offset gait for any number of leg pairs (wave_gait) and a travelling body wave (wiggle).
"""
import math
import os
import random

from bugs import *  # noqa: F401,F403


# ---------------------------------------------------------------- group A helpers

def topg(rows, pal, glow=""):
    """grid() for an up face, rows written front (north) to rear (south)."""
    return grid(list(reversed(rows)), pal, glow)


def jlegs(parent, hips, paint, tpaint=None, thick=1, prefix="leg", knee="knee", inflate=-0.25, start=1, shell=None):
    """Two-segment legs with per-pair geometry.
    hips: (hx, hy, hz, femur, yaw, lift, splay) for the +X side; the -X side is mirrored.
    The femur points out and up by `lift`; the tibia drops from the knee to the ground, tilted outward by `splay`.
    inflate < 0 slims the leg below one pixel while keeping integer box UV.
    shell: optional paint for an inflated overlay cube on every segment (the scorpion's fluorescence)."""
    out = []
    for i, (hx, hy, hz, femur, yaw, lift, splay) in enumerate(hips, start=start):
        rise = (femur - thick / 2) * math.sin(math.radians(lift))
        tib = max(1, round((hy + rise) / math.cos(math.radians(splay)) - 2 * inflate + 0.1))
        for side, sx in (("l", 1), ("r", -1)):
            fo = [hx if sx > 0 else -hx - femur, hy - thick / 2, hz - thick / 2]
            cubes = [C(fo, [femur, thick, thick], paint, inflate=inflate)]
            if shell:
                cubes.append(C(fo, [femur, thick, thick], shell, inflate=inflate + 0.12))
            out.append(B(f"{prefix}_{side}{i}", [sx * hx, hy, hz], cubes, parent=parent, rot=[0, sx * yaw, sx * lift]))
            kx = sx * (hx + femur - thick / 2)
            to = [kx - thick / 2, hy - tib - inflate, hz - thick / 2]
            tc = [C(to, [thick, tib, thick], tpaint or paint, inflate=inflate)]
            if shell:
                tc.append(C(to, [thick, tib, thick], shell, inflate=inflate + 0.12))
            out.append(B(f"{knee}_{side}{i}", [kx, hy, hz], tc, parent=f"{prefix}_{side}{i}", rot=[0, 0, sx * (splay - lift)]))
    return out


def slim_legs(parent, hips, paint, prefix="leg", inflate=-0.3, start=1):
    """Single-segment thin legs. hips: (hx, hy, hz, length, yaw, extra_down). The leg is angled so its tip meets the ground."""
    out = []
    for i, (hx, hy, hz, ln, yaw, extra) in enumerate(hips, start=start):
        ang = math.degrees(math.asin(min(0.95, max(0.05, (hy + 0.1) / (ln + inflate * 2 - 0.2))))) + extra
        for side, sx in (("l", 1), ("r", -1)):
            o = [hx if sx > 0 else -hx - ln, hy - 0.5, hz - 0.5]
            out.append(B(f"{prefix}_{side}{i}", [sx * hx, hy, hz], [C(o, [ln, 1, 1], paint, inflate=inflate)],
                         parent=parent, rot=[0, sx * yaw, -sx * ang]))
    return out


def stick(x, y, z, length, paint, inflate=-0.35):
    """A thin rod pointing forward (-Z) from (x, y, z): a 1x1xL cube slimmed by a negative inflate."""
    return C([x - 0.5, y - 0.5, z - length], [1, 1, length], paint, inflate=inflate)


def beads(c, c2):
    """Beaded rod paint: alternating colours along the length of a stick()."""
    return P(c, "vstripe", c2=c2, per=2, n=0, faces={"up": {"pat": "stripe"}, "down": {"pat": "stripe"}})


def feelers(parent, x, y, z, length, paint, up=20, out=25, name="antenna", inflate=-0.35):
    """Straight antennae as thin rods."""
    return [B(f"{name}_l", [x, y, z], [stick(x, y, z, length, paint, inflate)], parent=parent, rot=[up, -out, 0]),
            B(f"{name}_r", [-x, y, z], [stick(-x, y, z, length, paint, inflate)], parent=parent, rot=[up, out, 0])]


def elbow_antennae(parent, x, y, z, scape, flag, paint, fpaint=None, up=55, out=25, bend=-85, name="antenna", inflate=-0.33):
    """Elbowed (ant) antennae: a scape rising up-forward, then a flagellum bent forward/down at the elbow."""
    res = []
    for side, sx in (("l", 1), ("r", -1)):
        res.append(B(f"{name}_{side}", [sx * x, y, z], [stick(sx * x, y, z, scape, paint, inflate)],
                     parent=parent, rot=[up, -sx * out, 0]))
        res.append(B(f"{name}_tip_{side}", [sx * x, y, z - scape + 0.3], [stick(sx * x, y, z - scape + 0.3, flag, fpaint or paint, inflate)],
                     parent=f"{name}_{side}", rot=[bend, sx * 12, 0]))
    return res


def wave_gait(pairs, period, swing, lift, step=0.5, side=0.5, prefix="leg", frames=8, start=1, reverse=False):
    """Gait for any number of leg pairs. Each leg swings forward while lifted and back while planted.
    step: phase offset between consecutive pairs (0.5 = alternating tripod/tetrapod, small = metachronal wave);
    side: phase offset between the left and right leg of a pair (0 = in step, like a millipede)."""
    bones = {}
    d = -1 if reverse else 1
    for i in range(start, start + pairs):
        for s, sx, so in (("l", 1, 0.0), ("r", -1, side)):
            ph = (i * step + so) % 1.0
            vals = []
            for k in range(frames):
                a = 2 * math.pi * (k / frames + ph)
                up = max(0.0, -d * math.sin(a))
                vals.append([0, round(sx * swing * math.cos(a), 2), round(sx * lift * up, 2)])
            bones[f"{prefix}_{s}{i}"] = {"rotation": cycle(period, vals)}
    return bones


def wiggle(names, period, amp, step=0.12, axis=1, frames=8, base=None):
    """Travelling wave down a bone chain (body undulation)."""
    bones = {}
    for i, n in enumerate(names):
        vals = []
        for k in range(frames):
            v = list(base[i]) if base else [0, 0, 0]
            v[axis] += round(amp * math.sin(2 * math.pi * (k / frames - i * step)), 2)
            vals.append(v)
        bones[n] = {"rotation": cycle(period, vals)}
    return bones


def two_sway(a, b, period, amp, axis=0, mirror=False):
    if mirror:
        return merge(sway(a, period, amp, axis=axis), sway(b, period, -amp, axis=axis))
    return merge(sway(a, period, amp, axis=axis), sway(b, period, amp, axis=axis, offset=0.5))


def feeler_idle(period=2.0, amp=10, name="antenna"):
    return merge(sway(f"{name}_l", period, amp), sway(f"{name}_r", period, amp, offset=0.5))


def ramp(t_end, frm, to, t0=0.0):
    return [kf(t0, frm), kf(t_end, to)]


def speckle(w, h, pal, seed, density=1.0):
    r = random.Random(seed)
    return [[x, y, r.choice(pal)] for y in range(h) for x in range(w) if r.random() < density]


def speckle_faces(size, pal, seed, density=1.0):
    w, h, d = [int(math.ceil(v)) for v in size]
    dims = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}
    return {f: {"px": speckle(a, b, pal, seed + i * 17, density)} for i, (f, (a, b)) in enumerate(dims.items())}


def legs_hold(n, v, prefix="leg"):
    return {f"{prefix}_{s}{i}": {"rotation": hold(v)} for s in "lr" for i in range(1, n + 1)}


# ---------------------------------------------------------------- palettes
ANT_RB = "#8c3319"
ANT_DK = "#561c0b"
ANT_HI = "#d0765a"


# ================================================================ COMMON

def worker_ant():
    glossy = P(ANT_RB, "grad", c2=ANT_DK, hl=True, n=8)
    bones = [
        B("body", [0, 2, -1], [
            C([-1, 1.5, -2], [2, 2, 2], dict(glossy, faces={"up": {"px": [[0, -1, ANT_HI]]}})),
            C([-0.5, 1.8, 0], [1, 2, 1], P("#6e2711", hl=True), inflate=-0.12, name="node"),
        ]),
        B("gaster", [0, 2.5, 0.8], [
            C([-1.5, 1.4, 0.8], [3, 2, 3], dict(glossy, faces={"up": {"px": [[0, -1, ANT_HI]]}})),
            C([-1, 0.9, 1.3], [2, 3, 2], P("#9a3c1f", "grad", c2=ANT_DK, hl=True, faces={"up": {"px": [[0, -1, "#e89a7c"]]}})),
        ], parent="body", rot=[12, 0, 0]),
        B("head", [0, 2.5, -2], [
            C([-1.5, 1.5, -4.2], [3, 2, 2], P("#83301a", hl=True, faces={
                "east": {"px": [[0, 0, EYE]]}, "west": {"px": [[-1, 0, EYE]]}})),
            C([0.1, 1.5, -5.2], [1, 1, 1], P("#3a1408"), p=[0.6, 2, -4.2], r=[0, 30, 0], inflate=-0.1),
            C([-1.1, 1.5, -5.2], [1, 1, 1], P("#3a1408"), p=[-0.6, 2, -4.2], r=[0, -30, 0], inflate=-0.1),
        ], parent="body", rot=[8, 0, 0]),
    ]
    bones += elbow_antennae("head", 0.8, 3.3, -3.9, 2, 2, P("#3a1408"), P("#5a2210"), up=60, out=25, bend=-95)
    bones += jlegs("body", [(0.8, 2, -1.7, 2, 45, 30, 28), (0.8, 2, -1.0, 2, 0, 30, 25), (0.8, 2, -0.3, 2, -45, 25, 28)],
                   P("#5a1e0e"), P("#4a180a"), inflate=-0.28)
    return {"id": "worker_ant", "seed": 101, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": merge(feeler_idle(2, 10), sway("head", 2, 4, axis=1),
                                           {"gaster": {"rotation": cycle(2, [[0, 0, 0], [-4, 0, 0]])}})},
        "walk": {"len": 0.3, "bones": merge(wave_gait(3, 0.3, 24, 14), feeler_idle(0.3, 8),
                                            {"gaster": {"rotation": cycle(0.3, [[0, 3, 0], [0, -3, 0]])}})},
    }}


def earwig():
    shell = P("#3a1e12", "stripe", c2="#26120a", per=2, hl=True, n=8)
    bones = [
        B("body", [0, 1.5, 0], [
            C([-1, 0.8, -2], [2, 1, 1], P("#3b2014", hl=True)),
            C([-1.5, 0.8, -1], [3, 1, 2], P("#c98a44", hl=True, n=8, faces={"up": {"px": col(1, 2, "#8a5424")}})),
        ]),
        B("abdomen", [0, 1.3, 1], [
            C([-1.5, 0.6, 1], [3, 1, 3], dict(shell, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
            C([-1, 0.6, 4], [2, 1, 1], P("#2e170c", hl=True)),
        ], parent="body"),
        B("forceps_l", [0.5, 1.1, 5], [
            C([0, 0.6, 5], [1, 1, 2], P("#6a3a1e", hl=True), inflate=-0.08),
            C([0, 0.6, 6.7], [1, 1, 2], P("#7c4424", hl=True), p=[0.5, 1.1, 6.8], r=[0, -42, 0], inflate=-0.14),
        ], parent="abdomen", rot=[0, 14, 0]),
        B("forceps_r", [-0.5, 1.1, 5], [
            C([-1, 0.6, 5], [1, 1, 2], P("#6a3a1e", hl=True), inflate=-0.08),
            C([-1, 0.6, 6.7], [1, 1, 2], P("#7c4424", hl=True), p=[-0.5, 1.1, 6.8], r=[0, 42, 0], inflate=-0.14),
        ], parent="abdomen", rot=[0, -14, 0]),
        B("head", [0, 1.3, -2], [C([-1, 0.8, -4], [2, 1, 2], P("#4a2414", hl=True, faces={
            "east": {"px": [[0, 0, EYE]]}, "west": {"px": [[-1, 0, EYE]]}}))], parent="body"),
    ]
    bones += feelers("head", 0.5, 1.3, -4, 4, beads("#6a4630", "#2a160c"), up=12, out=30)
    bones += jlegs("body", [(0.8, 1.2, -1.6, 2, 50, 12, 40), (1.2, 1.2, -0.5, 2, 5, 12, 40), (1.2, 1.2, 0.5, 2, -45, 12, 40)],
                   P("#b89060"), P("#a47c4c"), inflate=-0.25)
    pinch = {"abdomen": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [-18, 0, 0]), kf(0.5, [-18, 0, 0]), kf(0.7, [0, 0, 0])]},
             "forceps_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [-10, 22, 0]), kf(0.25, [-10, -26, 0]), kf(0.35, [-10, 18, 0]),
                                        kf(0.45, [-10, -26, 0]), kf(0.7, [0, 0, 0])]},
             "forceps_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.15, [-10, -22, 0]), kf(0.25, [-10, 26, 0]), kf(0.35, [-10, -18, 0]),
                                        kf(0.45, [-10, 26, 0]), kf(0.7, [0, 0, 0])]}}
    return {"id": "earwig", "seed": 102, "bones": bones, "anims": {
        "idle": {"len": 2.5, "bones": merge(feeler_idle(2.5, 12), sway("forceps_l", 2.5, 4, axis=1), sway("forceps_r", 2.5, 4, axis=1, offset=0.5))},
        "walk": {"len": 0.25, "bones": merge(wave_gait(3, 0.25, 22, 12), feeler_idle(0.25, 8), sway("abdomen", 0.5, 4, axis=1))},
        "pinch": {"len": 0.7, "loop": False, "bones": pinch},
    }}


def termite():
    cream = P("#f1e5c9", "stripe", c2="#dac8a2", per=2, hl=True, n=6)
    bones = [
        B("body", [0, 1.6, 0], [
            C([-1, 1, -1], [2, 1, 1], P("#eadcbc", hl=True, n=6)),
            C([-1.5, 0.8, 0], [3, 2, 3], dict(cream, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
            C([-1, 0.9, 3], [2, 1, 1], P("#d8c69e", n=6), inflate=-0.1),
        ]),
        B("head", [0, 1.8, -1], [
            C([-1, 1, -3], [2, 2, 2], P("#c8742c", "grad", c2="#a85a1c", hl=True, faces={"up": {"px": [[0, 0, "#e0904a"]]}})),
            C([0.1, 1, -4], [1, 1, 1], P("#3a1e0c"), p=[0.5, 1.5, -3], r=[0, 30, 0], inflate=-0.12),
            C([-1.1, 1, -4], [1, 1, 1], P("#3a1e0c"), p=[-0.5, 1.5, -3], r=[0, -30, 0], inflate=-0.12),
        ], parent="body"),
    ]
    bones += feelers("head", 0.6, 2.4, -3, 3, beads("#d8b080", "#9a7040"), up=8, out=32)
    bones += jlegs("body", [(0.8, 1.3, -0.8, 1, 45, 15, 35), (0.8, 1.3, -0.2, 1, 5, 15, 35), (1.0, 1.3, 0.4, 2, -40, 15, 30)],
                   P("#e6d6b4"), P("#d8c49c"), inflate=-0.28)
    return {"id": "termite", "seed": 103, "bones": bones, "anims": {
        "idle": {"len": 2, "bones": merge(feeler_idle(1.0, 12), sway("head", 2, 5, axis=1), bob("body", 2, 0.1))},
        "walk": {"len": 0.25, "bones": merge(wave_gait(3, 0.25, 22, 12), feeler_idle(0.25, 10))},
    }}


MILLI_N = 10


def millipede():
    black = "#17151a"
    orange = "#e2562a"
    seg_a = P(black, hl=True, n=6, faces={"east": {"px": [[0, 0, orange]]}, "west": {"px": [[0, 0, orange]]}})
    seg_b = P("#232128", hl=True, n=6)
    leg_a, leg_b = P("#e8742a", n=0), P("#c45a1e", n=0)
    bones = []
    z0 = -5
    for i in range(1, MILLI_N + 1):
        z = z0 + (i - 1)
        name = "body" if i == 1 else f"seg{i}"
        parent = None if i == 1 else ("body" if i == 2 else f"seg{i - 1}")
        cubes = [C([-1, 0.8, z], [2, 2, 1], seg_a if i % 2 else seg_b, inflate=0.05 if i % 2 else 0)]
        if i < MILLI_N:
            # joint filler: hidden inside the next ring when straight, closes the outer gaps when coiled
            cubes.append(C([-1, 0.8, z], [2, 2, 2], P("#101014", n=4), inflate=-0.12))
        bones.append(B(name, [0.6, 1.8, z], cubes, parent=parent))
        lp = leg_a if i % 2 else leg_b
        for side, sx in (("l", 1), ("r", -1)):
            hx, hy = 0.7, 1.0
            cubes = []
            for dz, yaw in ((-0.25, 8), (0.25, -8)):
                o = [hx if sx > 0 else -hx - 2, hy - 0.5, z + 0.5 + dz - 0.5]
                cubes.append(C(o, [2, 1, 1], lp, p=[sx * hx, hy, z + 0.5 + dz], r=[0, sx * yaw, 0], inflate=-0.32))
            bones.append(B(f"leg_{side}{i}", [sx * hx, hy, z + 0.5], cubes, parent=name, rot=[0, 0, -sx * 42]))
    bones.append(B("tail", [0.6, 1.8, z0 + MILLI_N], [C([-0.5, 1.1, z0 + MILLI_N], [1, 1, 1], P("#2a282e", hl=True), inflate=0.1)], parent=f"seg{MILLI_N}"))
    bones.append(B("head", [0, 1.8, z0], [C([-1, 0.8, z0 - 2], [2, 2, 2], P("#1d1b20", hl=True, faces={
        "east": {"px": [[0, 0, "#4a4652"]]}, "west": {"px": [[-1, 0, "#4a4652"]]},
        "north": {"px": [[0, -1, "#3a3036"], [1, -1, "#3a3036"]]}}), inflate=0.1)], parent="body"))
    bones += feelers("head", 0.6, 2.0, z0 - 1.8, 3, beads("#4a4452", "#2a2630"), up=-25, out=30)
    segs = ["body"] + [f"seg{i}" for i in range(2, MILLI_N + 1)]
    curl_ang = [0, 44, 42, 40, 38, 36, 34, 33, 32, 31]
    curl = {}
    for n, a in zip(segs, curl_ang):
        if a:
            curl[n] = {"rotation": ramp(0.6, [0, 0, 0], [0, a, 0])}
    curl["tail"] = {"rotation": ramp(0.6, [0, 0, 0], [0, 30, 0])}
    curl["head"] = {"rotation": ramp(0.6, [0, 0, 0], [-20, 40, 0])}
    curl["body"] = {"position": ramp(0.6, [0, 0, 0], [0, -0.6, 0])}
    curl["antenna_l"] = {"scale": ramp(0.4, [1, 1, 1], [0.2, 0.2, 0.2])}
    curl["antenna_r"] = {"scale": ramp(0.4, [1, 1, 1], [0.2, 0.2, 0.2])}
    for i in range(1, MILLI_N + 1):
        for s in "lr":
            curl[f"leg_{s}{i}"] = {"scale": ramp(0.4, [1, 1, 1], [0.1, 0.1, 0.1])}
    walk = merge(wave_gait(MILLI_N, 0.6, 22, 14, step=0.13, side=0.0), feeler_idle(0.6, 10),
                 wiggle(segs, 1.2, 1.5, step=0.1))
    return {"id": "millipede", "seed": 104, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(feeler_idle(1.5, 14), sway("head", 3, 5, axis=1))},
        "walk": {"len": 1.2, "bones": walk},
        "curl": {"len": 0.6, "loop": "hold", "bones": curl},
    }}


def caddisfly_larva():
    peb = ["#8a8378", "#6e665c", "#a39a88", "#5a4e40", "#b8ad96", "#7a6a52", "#948a70", "#c4b8a0"]
    front = [3, 3, 4]
    rear = [3, 3, 3]
    bones = [
        B("body", [0, 1.5, 0], [
            C([-1.5, 0, -2], front, P("#8a8070", n=0, faces=speckle_faces(front, peb, 5))),
            C([-1.5, 0.2, 2], rear, P("#8a8070", n=0, faces=speckle_faces(rear, peb, 9)), inflate=-0.2),
            C([0.9, 1.8, -1.2], [1, 1, 1], P("#b8ad96", n=4), inflate=0.1),
            C([-1.9, 0.6, 0.4], [1, 1, 1], P("#6e665c", n=4), inflate=0.05),
            C([-0.6, 2.7, 1.4], [1, 1, 1], P("#a39a88", n=4), inflate=0.05),
            C([1.2, 0.9, 3.0], [1, 1, 1], P("#5a4e40", n=4), inflate=0.1),
            C([-0.4, 2.8, -1.8], [1, 1, 1], P("#c4b8a0", n=4), inflate=-0.05),
            C([-1.8, 2.2, 2.6], [1, 1, 2], P("#7a6a52", n=4), inflate=-0.1),
            C([1.1, 2.4, 0.2], [1, 1, 1], P("#948a70", n=4), inflate=-0.1),
            C([0.2, 3.0, -0.5], [1, 1, 4], P("#6e5536", "stripe", c2="#54401f", per=3), p=[0.7, 3.4, 1], r=[0, 18, 8], inflate=-0.25, name="twig"),
        ]),
        B("larva", [0, 1.3, -2], [
            C([-1, 0.5, -2.8], [2, 2, 1], P("#e8dcc0", "stripe", c2="#cfc09c", per=2, n=6), inflate=-0.05),
            C([-1, 1.3, -3.2], [2, 1, 1], P("#8a6a40", hl=True, n=6), inflate=-0.02, name="thorax_plate"),
        ], parent="body"),
        B("head", [0, 1.5, -3.2], [
            C([-1, 0.8, -4.6], [2, 1, 2], P("#7a5a30", "spots", c2="#3a2814", d=0.3, hl=True, n=6, faces={
                "east": {"px": [[0, 0, "#0d0d10"]]}, "west": {"px": [[-1, 0, "#0d0d10"]]},
                "north": {"c": "#4a3418", "px": [[0, 0, "#241a0c"], [1, 0, "#241a0c"]]}})),
        ], parent="larva"),
    ]
    bones += jlegs("larva", [(0.7, 1.0, -3.0, 1, 60, 20, 20), (0.8, 1.0, -2.6, 1, 30, 20, 25), (0.8, 1.0, -2.2, 2, 5, 20, 25)],
                   P("#5a4428"), P("#3a2a1a"), inflate=-0.3)
    return {"id": "caddisfly_larva", "seed": 105, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(sway("head", 3, 8, axis=1), sway("larva", 3, 4, axis=0),
                                           {"body": {"rotation": cycle(3, [[0, 0, 0], [0, 0, 2], [0, 0, 0], [0, 0, -2]])}},
                                           wave_gait(3, 1.5, 10, 8))},
        "walk": {"len": 0.6, "bones": merge(wave_gait(3, 0.6, 28, 16),
                                            {"larva": {"position": cycle(0.6, [[0, 0, 0], [0, 0, -0.4]])},
                                             "body": {"rotation": cycle(0.6, [[0, 0, 2], [1, 0, 0], [0, 0, -2], [1, 0, 0]])}},
                                            sway("head", 0.6, 5, axis=1))},
    }}


# ================================================================ UNCOMMON

def orb_weaver():
    K, Y, W, S = "#1c1a18", "#ecc41c", "#ece8dc", "#b8b2a2"
    band_f = P(K, "vstripe", c2="#d8a820", per=3, n=6)
    band_t = P(K, "stripe", c2="#d8a820", per=3, n=6)
    pal = {"W": W, "Y": Y, "K": K, "S": S}
    cap = ["SWWS", "YYYY", "KKKK", "YYYY", "KKKK", "KYYK"]
    top_core = ["SWWWS", "WYYYW", "YKKKY", "KYYYK", "YKKKY", "KYYYK"]
    side = "SYKYKY"
    side_px = [[i, r, pal[c]] for i, c in enumerate(side) for r in range(3)]
    side_px_e = [[5 - i, r, pal[c]] for i, c in enumerate(side) for r in range(3)]
    core = P(K, n=8, faces={"up": {"px": topg(top_core, pal)}, "north": {"c": "#d8cc9a", "pat": "edge", "c2": K},
                            "east": {"px": side_px_e}, "west": {"px": side_px}, "down": {"px": col(2, 6, Y)}})
    abd = P(K, n=8, hl=True, faces={"up": {"px": topg(cap, pal)}})
    bones = [
        B("body", [0, 3, -1.5], [
            C([-1.5, 2, -3], [3, 2, 3], P("#3a302a", "edge", c2="#6a6058", hl=True, faces={
                "north": {"pat": "solid", "px": [[0, 0, "#0a0a0c"], [2, 0, "#0a0a0c"], [1, 0, "#bcb6a8"]]}})),
            C([-1, 2, -4], [2, 1, 1], P("#2a2320")),
        ]),
        B("abdomen", [0, 3.5, 0], [
            C([-2.5, 2, 0], [5, 3, 6], core),
            C([-2, 5, 0], [4, 1, 6], abd),
            C([-2, 1.4, 0.5], [4, 1, 5], P("#2a2622")),
            C([-0.5, 2.5, 5.7], [1, 1, 1], P("#3a2e24"), name="spinnerets"),
        ], parent="body", rot=[-10, 0, 0]),
        B("palp_l", [0.5, 2.5, -4], [C([0, 2, -6], [1, 1, 2], P(K), inflate=-0.25)], parent="body", rot=[20, 15, 0]),
        B("palp_r", [-0.5, 2.5, -4], [C([-1, 2, -6], [1, 1, 2], P(K), inflate=-0.25)], parent="body", rot=[20, -15, 0]),
    ]
    bones += jlegs("body", [(1.4, 3, -2.7, 4, 50, 40, 12), (1.4, 3, -2.0, 4, 18, 40, 12),
                            (1.4, 3, -1.3, 3, -22, 40, 12), (1.4, 3, -0.6, 4, -52, 40, 12)],
                   band_f, band_t, inflate=-0.28)
    return {"id": "orb_weaver", "seed": 106, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge({"abdomen": {"rotation": cycle(3, [[0, 0, 0], [3, 0, 0]])}},
                                           two_sway("palp_l", "palp_r", 1.5, 8),
                                           {"leg_l1": {"rotation": [kf(0, [0, 0, 0]), kf(2.2, [0, 0, 0]), kf(2.4, [0, 0, 18]), kf(2.6, [0, 0, 0]), kf(3, [0, 0, 0])]}})},
        "walk": {"len": 0.5, "bones": merge(wave_gait(4, 0.5, 18, 16, step=0.5, side=0.5),
                                            {"abdomen": {"rotation": cycle(0.25, [[0, 0, 0], [2, 0, 0]])}})},
    }}


def tick():
    body = P("#7a2a1a", "grad", c2="#5a1c10", hl=True, n=8)
    bones = [
        B("body", [0, 1.2, 0], [
            C([-2, 0.6, -1], [4, 1, 4], dict(body, faces={"up": {"px": topg(["....", "....", "....", "K..K"], {"K": "#4a1a10"})}})),
            C([-1.5, 0.6, -1.5], [3, 1, 5], P("#6e2616", hl=True, n=6), inflate=-0.06),
            C([-1.5, 1.6, -0.2], [3, 1, 3], P("#86301e", hl=True, n=6, faces={"up": {"px": [[1, 0, "#5a1c10"], [1, 1, "#a8442a"]]}}), inflate=-0.1),
            C([-1, 1.5, -1.6], [2, 1, 2], P("#2a1a14", hl=True, n=6, faces={"up": {"px": [[0, 1, "#5a4034"]]}}), inflate=0.05, name="scutum"),
        ]),
        B("head", [0, 1.2, -1.5], [
            C([-1, 0.7, -2.4], [2, 1, 1], P("#3a241a")),
            C([-0.5, 0.8, -3.2], [1, 1, 1], P("#241410"), inflate=-0.12),
            C([0.3, 0.8, -3.1], [1, 1, 1], P("#4a3024"), inflate=-0.27),
            C([-1.3, 0.8, -3.1], [1, 1, 1], P("#4a3024"), inflate=-0.27),
        ], parent="body"),
    ]
    bones += jlegs("body", [(1.2, 1.1, -1.4, 2, 55, 25, 15), (1.5, 1.1, -0.8, 2, 20, 25, 15),
                            (1.5, 1.1, -0.2, 2, -15, 25, 15), (1.4, 1.1, 0.4, 2, -45, 25, 15)],
                   P("#3a2418"), P("#2e1c12"), inflate=-0.3)
    return {"id": "tick", "seed": 107, "bones": bones, "anims": {
        "idle": {"len": 2.4, "bones": merge({"leg_l1": {"rotation": cycle(2.4, [[0, 0, 0], [0, 12, 40], [0, -8, 30], [0, 10, 42], [0, 0, 0], [0, 0, 0]])},
                                             "leg_r1": {"rotation": cycle(2.4, [[0, 0, 0], [0, -8, -30], [0, 12, -42], [0, -10, -35], [0, 0, 0], [0, 0, 0]])}},
                                            bob("body", 2.4, 0.08))},
        "walk": {"len": 0.35, "bones": wave_gait(4, 0.35, 16, 12, step=0.5)},
    }}


CENTI_N = 12


def centipede():
    body_a = P("#94401e", hl=True, n=8)
    body_b = P("#6a2a12", hl=True, n=8)
    legp = P("#e8a030", n=4)
    bones = []
    z0 = -5
    fan = [30 - 60 * (i / (CENTI_N - 2)) for i in range(CENTI_N - 1)]
    for i in range(1, CENTI_N + 1):
        z = z0 + (i - 1)
        name = "body" if i == 1 else f"seg{i}"
        parent = None if i == 1 else ("body" if i == 2 else f"seg{i - 1}")
        w = 3
        bones.append(B(name, [0, 1.5, z], [C([-w / 2, 1, z], [w, 1, 1], body_a if i % 2 else body_b, inflate=0.04 if i % 2 else 0)], parent=parent))
        if i < CENTI_N:
            bones += slim_legs(name, [(1.3, 1.3, z + 0.5, 4, fan[i - 1], 0)], legp, start=i)
    # long trailing rear legs on the last segment
    zl = z0 + CENTI_N - 1
    for side, sx in (("l", 1), ("r", -1)):
        bones.append(B(f"leg_{side}{CENTI_N}", [sx * 1.2, 1.4, zl + 0.5],
                       [C([1.2 if sx > 0 else -1.2 - 6, 0.9, zl], [6, 1, 1], P("#d88a24", "vstripe", c2="#b86a18", per=2, n=4), inflate=-0.3)],
                       parent=f"seg{CENTI_N}", rot=[0, sx * -70, -sx * 8]))
    bones.append(B("head", [0, 1.5, z0], [
        C([-1.5, 1, z0 - 2], [3, 1, 2], P("#5a2210", hl=True, faces={"east": {"px": [[0, 0, "#1a1010"]]}, "west": {"px": [[-1, 0, "#1a1010"]]}})),
        C([0.2, 0.6, z0 - 3.2], [1, 1, 2], P("#2a100a"), p=[0.7, 1, z0 - 1.5], r=[0, 35, 0], inflate=-0.2, name="forcipule_l"),
        C([-1.2, 0.6, z0 - 3.2], [1, 1, 2], P("#2a100a"), p=[-0.7, 1, z0 - 1.5], r=[0, -35, 0], inflate=-0.2, name="forcipule_r"),
    ], parent="body"))
    bones += feelers("head", 0.7, 1.6, z0 - 2, 6, beads("#e09a2c", "#a86018"), up=15, out=28)
    segs = ["body"] + [f"seg{i}" for i in range(2, CENTI_N + 1)]
    return {"id": "centipede", "seed": 108, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(feeler_idle(1.5, 12), wiggle(segs, 3, 1.2, step=0.08))},
        "walk": {"len": 0.5, "bones": merge(wave_gait(CENTI_N - 1, 0.5, 26, 12, step=0.09, side=0.5), feeler_idle(0.5, 8),
                                            wiggle(segs, 1.0, 3.0, step=0.08))},
    }}


def jumping_spider():
    K, W = "#1c1a1c", "#ece8e0"
    face = "#6a5846"
    eye = P("#0c0c14", "grad", c2="#020204", n=0, faces={"up": {"c": "#2a2630"}})
    glint = P("#ffffff", n=0)
    small = P("#060608", n=0)
    teal = P("#2fd6b0", "iri", c2="#3a6ad6", j=0.1, n=0, hl=True)
    abd_top = ["WWWW", "....", ".WW.", "W..W"]
    bones = [
        B("body", [0, 2.5, -1.5], [
            C([-2.5, 1.5, -3], [5, 3, 2], P(K, n=30, hl=True, faces={
                "north": {"c": face, "n": 25, "px": [[0, 0, W], [4, 0, W], [2, 0, "#9a8a78"]]},
                "up": {"px": topg([".....", "W...W"], {"W": "#8a8480"})}})),
            C([-2, 1.5, -1], [4, 2, 1], P(K, n=30, hl=True)),
            C([0.1, 2.2, -3.4], [2, 2, 1], eye, name="eye_l"),
            C([-2.1, 2.2, -3.4], [2, 2, 1], eye, name="eye_r"),
            C([0.2, 3.2, -3.95], [1, 1, 1], glint, inflate=-0.34, name="glint_l"),
            C([-2.0, 3.2, -3.95], [1, 1, 1], glint, inflate=-0.34, name="glint_r"),
            C([1.95, 3.3, -3.3], [1, 1, 1], small, inflate=-0.25),
            C([-2.95, 3.3, -3.3], [1, 1, 1], small, inflate=-0.25),
            C([0.05, 0.4, -3.3], [1, 2, 1], teal, inflate=-0.05, name="chelicera_l"),
            C([-1.05, 0.4, -3.3], [1, 2, 1], teal, inflate=-0.05, name="chelicera_r"),
        ]),
        B("abdomen", [0, 2.8, 0.1], [
            C([-2, 1.2, 0.2], [4, 3, 4], P(K, n=30, hl=True, faces={
                "up": {"px": topg(abd_top, {"W": W})}, "north": {"c": "#d8d2c8", "n": 10},
                "east": {"px": [[2, 0, W], [3, 1, W]]}, "west": {"px": [[-3, 0, W], [-4, 1, W]]}})),
            C([-1.5, 1.7, 4.2], [3, 2, 1], P("#242022", n=20), inflate=-0.15),
            C([-1.5, 0.8, 0.7], [3, 1, 3], P("#2a2426", n=20), inflate=-0.05),
        ], parent="body", rot=[-3, 0, 0]),
        B("palp_l", [0.9, 2.2, -3.3], [C([0.4, 1.0, -4.1], [1, 1, 1], P(K, faces={"north": {"c": W}, "up": {"c": W}}), inflate=-0.12)], parent="body"),
        B("palp_r", [-0.9, 2.2, -3.3], [C([-1.4, 1.0, -4.1], [1, 1, 1], P(K, faces={"north": {"c": W}, "up": {"c": W}}), inflate=-0.12)], parent="body"),
    ]
    legp = P("#242022", "vstripe", c2="#6a625c", per=3, n=20)
    legt = P("#242022", "stripe", c2="#8a827a", per=3, n=20)
    bones += jlegs("body", [(2, 2.6, -2.5, 3, 50, 35, 14)], P("#1e1a1c", "vstripe", c2="#3a3434", per=2, n=25),
                   P("#1e1a1c", "stripe", c2="#d8d0c4", per=3, n=25), inflate=-0.02)
    bones += jlegs("body", [(2, 2.2, -1.8, 2, 18, 30, 16), (2, 2.2, -1.1, 2, -15, 30, 16), (1.8, 2.2, -0.4, 2, -45, 30, 16)],
                   legp, legt, inflate=-0.15, start=2)
    wave = [kf(0, [0, 0, 0]), kf(0.12, [0, -18, 40]), kf(0.27, [0, 12, 50]), kf(0.42, [0, -18, 40]),
            kf(0.57, [0, 12, 50]), kf(0.72, [0, -18, 40]), kf(0.9, [0, 0, 0])]
    dance = merge({"leg_l1": {"rotation": wave},
                   "leg_r1": {"rotation": [kf(k[0], [k[1][0], -k[1][1], -k[1][2]]) for k in wave]},
                   "knee_l1": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, 0, 110]), kf(0.72, [0, 0, 110]), kf(0.9, [0, 0, 0])]},
                   "knee_r1": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, 0, -110]), kf(0.72, [0, 0, -110]), kf(0.9, [0, 0, 0])]},
                   "body": {"position": [kf(0, [0, 0, 0]), kf(0.225, [0.7, 0.4, 0]), kf(0.45, [0, 0.4, 0]), kf(0.675, [-0.7, 0.4, 0]), kf(0.9, [0, 0, 0])],
                            "rotation": [kf(0, [0, 0, 0]), kf(0.225, [-8, 0, 7]), kf(0.45, [-8, 0, 0]), kf(0.675, [-8, 0, -7]), kf(0.9, [0, 0, 0])]},
                   "abdomen": {"rotation": cycle(0.9, [[0, 0, 0], [-12, 10, 0], [0, 0, 0], [-12, -10, 0]])}},
                  two_sway("palp_l", "palp_r", 0.15, 30))
    return {"id": "jumping_spider", "seed": 109, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(two_sway("palp_l", "palp_r", 0.6, 15),
                                           {"body": {"rotation": [kf(0, [0, 0, 0]), kf(1.2, [0, 0, 0]), kf(1.35, [0, 18, 0]), kf(2.2, [0, 18, 0]),
                                                                  kf(2.35, [0, 0, 0]), kf(3, [0, 0, 0])]},
                                            "abdomen": {"rotation": cycle(3, [[0, 0, 0], [2, 0, 0]])}})},
        "walk": {"len": 0.3, "bones": merge(wave_gait(4, 0.3, 16, 16, step=0.5), two_sway("palp_l", "palp_r", 0.3, 10))},
        "dance": {"len": 0.9, "loop": False, "bones": dance},
    }}


def honeypot_ant():
    amber = P("#f2ac2c", "grad", c2="#cc7a16", hl=True, n=6)
    band = "#9a5014"
    bands = dict(amber, pat="stripe", c2=band, per=3)
    vb = dict(amber, pat="vstripe", c2=band, per=3)
    hon = {"up": {"pat": "stripe", "px": [[1, -2, "#fff6d0"], [2, -2, "#ffe8a0"], [1, -3, "#ffe8a0"]]},
           "east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}}
    bones = [
        B("body", [0, 2.5, -1], [
            C([-1, 2, -2], [2, 1, 2], P("#3a2012", hl=True, n=8)),
            C([-0.5, 2.2, 0], [1, 1, 1], P("#2e180c"), inflate=-0.05, name="node"),
        ]),
        B("gaster", [0, 3, 1], [
            C([-2.5, 1, 1.5], [5, 4, 4], dict(bands, faces=hon), name="honey_core"),
            C([-2, 0.5, 2], [4, 5, 3], dict(bands, faces=hon)),
            C([-2, 1.5, 1], [4, 3, 5], dict(vb, faces={"north": {"pat": "solid", "c": "#e89a24", "px": [[1, 0, "#6a3810"], [2, 0, "#6a3810"]]},
                                                       "south": {"pat": "solid", "c": "#c07018"}})),
            C([-3, 1.5, 2], [6, 3, 3], dict(vb, faces={"east": {"pat": "vstripe", "px": [[1, 0, "#ffe7a0"]]}, "west": {"pat": "vstripe", "px": [[-2, 0, "#ffe7a0"]]}})),
            C([-0.5, 2.5, 5.8], [1, 1, 1], P("#4a2a10"), inflate=-0.15),
        ], parent="body"),
        B("head", [0, 2.6, -2], [
            C([-1, 2, -4], [2, 2, 2], P("#2a1a10", hl=True, faces={"east": {"px": [[0, 0, "#0a0a0a"]]}, "west": {"px": [[-1, 0, "#0a0a0a"]]}})),
            C([-1, 2, -4.8], [2, 1, 1], P("#1a0e06"), inflate=-0.15),
        ], parent="body"),
    ]
    bones += elbow_antennae("head", 0.6, 3.8, -3.6, 2, 2, P("#2a1a10"), up=55, out=25, bend=-90)
    bones += jlegs("body", [(0.8, 2.5, -1.7, 3, 45, 18, 32), (0.8, 2.5, -1.1, 3, 5, 18, 34), (0.8, 2.5, -0.5, 3, -40, 15, 36)],
                   P("#3a2012"), P("#2e180c"), inflate=-0.27)
    squish = {"gaster": {"scale": cycle(3, [[1, 1, 1], [1.03, 0.98, 1.03]])}}
    return {"id": "honeypot_ant", "seed": 110, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(feeler_idle(1.5, 10), squish, sway("head", 3, 4, axis=1))},
        "walk": {"len": 0.5, "bones": merge(wave_gait(3, 0.5, 20, 14), feeler_idle(0.5, 8),
                                            {"gaster": {"scale": cycle(0.25, [[1, 1, 1], [1.05, 0.95, 1.02]]),
                                                        "rotation": cycle(0.5, [[0, 0, 2], [0, 0, -2]])}})},
    }}


def antlion():
    sand = P("#a89a7c", "spots", c2="#6e6450", d=0.25, n=18, hl=True)
    jaw = P("#8a5a32", "grad", c2="#5a3418", hl=True, n=6)
    tip = P("#3a2010", hl=True, n=4)
    tooth = P("#efe4c8", n=0)
    bristle = P("#5a5040", n=0)
    bones = [
        B("body", [0, 2, 1], [
            C([-2.5, 0.5, 0], [5, 3, 4], dict(sand, faces={"up": {"px": topg([".....", ".K.K.", ".K.K.", "....."], {"K": "#5a5040"})}})),
            C([-1.5, 3.5, 1], [3, 1, 2], P("#b4a688", "spots", c2="#6e6450", d=0.3, n=18, hl=True)),
            C([-1.5, 1, 4], [3, 2, 1], P("#9a8c6e", "spots", c2="#6e6450", d=0.3, n=18)),
            C([-2.9, 1.2, 1], [1, 2, 2], P("#9c8e70", "spots", c2="#5a5040", d=0.3), inflate=-0.1),
            C([1.9, 1.2, 1], [1, 2, 2], P("#9c8e70", "spots", c2="#5a5040", d=0.3), inflate=-0.1),
        ]),
        B("thorax", [0, 1.8, 0], [C([-1.5, 1, -1], [3, 2, 1], P("#968a6c", "spots", c2="#5a5040", d=0.2, hl=True))], parent="body"),
        B("head", [0, 1.8, -1], [
            C([-1.5, 1.2, -3], [3, 1, 2], P("#7a6a50", hl=True, faces={"up": {"px": [[0, -1, "#1a1410"], [2, -1, "#1a1410"]]}})),
            C([1.1, 1.6, -2.9], [1, 1, 1], P("#2a2018"), inflate=-0.3),
            C([-2.1, 1.6, -2.9], [1, 1, 1], P("#2a2018"), inflate=-0.3),
        ], parent="thorax"),
    ]
    # bristles sticking out of the round abdomen
    for (x, y, z, yaw, rl) in [(2.3, 2.5, 1.2, 20, 25), (2.3, 1.5, 3.0, -25, 10), (2.0, 3.2, 3.5, -40, 40), (1.0, 3.8, 2.0, 10, 70)]:
        for sx in (1, -1):
            o = [sx * x - 0.5 if sx > 0 else sx * x - 1.5, y - 0.5, z - 0.5]
            bones[0]["cubes"].append(C(o, [2, 1, 1], bristle, p=[sx * x, y, z], r=[0, sx * yaw, sx * rl], inflate=-0.4))
    for side, sx in (("l", 1), ("r", -1)):
        bx = 0.25 if sx > 0 else -1.25
        bones.append(B(f"jaw_{side}", [sx * 0.9, 1.7, -3], [
            C([bx, 1.2, -5.2], [1, 1, 2], jaw, inflate=-0.12),
            C([bx, 1.2, -6.9], [1, 1, 2], dict(jaw, c="#704424"), p=[sx * 0.75, 1.7, -5.0], r=[0, sx * 24, 0], inflate=-0.16),
            C([bx, 1.2, -8.3], [1, 1, 2], tip, p=[sx * 0.75, 1.7, -6.6], r=[0, sx * 64, 0], inflate=-0.2),
            C([bx - sx * 0.55, 1.2, -4.9], [1, 1, 1], tooth, inflate=-0.36),
            C([bx - sx * 0.55, 1.2, -5.9], [1, 1, 1], tooth, inflate=-0.36),
        ], parent="head", rot=[0, -sx * 24, 0]))
    bones += slim_legs("thorax", [(1.2, 1.3, -0.85, 2, 40, 5), (1.3, 1.3, -0.5, 2, 5, 5), (1.2, 1.3, -0.15, 3, -35, 0)],
                       P("#7a6c52"), inflate=-0.27)
    grab = {"jaw_l": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, -20, 0]), kf(0.2, [0, 36, 0]), kf(0.35, [0, 36, 0]), kf(0.6, [0, 0, 0])]},
            "jaw_r": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [0, 20, 0]), kf(0.2, [0, -36, 0]), kf(0.35, [0, -36, 0]), kf(0.6, [0, 0, 0])]},
            "head": {"rotation": [kf(0, [0, 0, 0]), kf(0.12, [8, 0, 0]), kf(0.2, [-18, 0, 0]), kf(0.35, [-18, 0, 0]), kf(0.6, [0, 0, 0])]},
            "thorax": {"position": [kf(0, [0, 0, 0]), kf(0.2, [0, 0, -0.6]), kf(0.6, [0, 0, 0])]}}
    return {"id": "antlion", "seed": 111, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(two_sway("jaw_l", "jaw_r", 3, 6, axis=1, mirror=True), bob("body", 3, 0.12),
                                           sway("head", 3, 4, axis=0))},
        "walk": {"len": 0.5, "bones": merge(wave_gait(3, 0.5, 20, 12, reverse=True), {"body": {"rotation": cycle(0.5, [[0, 0, 3], [0, 0, -3]])}})},
        "grab": {"len": 0.6, "loop": False, "bones": grab},
    }}


def bookworm():
    beige = P("#ece0c4", "stripe", c2="#d4c49c", per=2, n=6, hl=True)
    K = "#1a1a1e"
    glasses = P("#000000", n=0, alpha=0, px=grid([".K...K.", "KgKKKgK", ".K...K."], {"K": "#2e2624", "g": "#cfe6ee"}))
    bones = [
        B("body", [0, 1.6, 0.5], [
            C([-1.5, 0.8, 0], [3, 2, 3], dict(beige, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
            C([-1, 1, -1], [2, 1, 1], P("#e6d8b8", n=6)),
        ]),
        B("head", [0, 1.8, -1], [
            C([-3.5, 0.8, -4], [7, 4, 3], P("#f2e6cc", hl=True, n=6, faces={
                "north": {"px": [[1, 3, "#eab4a4"], [5, 3, "#eab4a4"], [3, 3, "#c8a890"]]},
                "up": {"px": topg([".......", "...b...", "......."], {"b": "#e0d0b0"})}})),
            C([-3.5, 1.8, -4.12], [7, 3, 0], glasses, name="spectacles"),
            C([3.55, 2.8, -4.1], [0, 1, 2], P("#000000", n=0, alpha=0, px=[[0, 0, K], [1, 0, K]]), name="temple_l"),
            C([-3.55, 2.8, -4.1], [0, 1, 2], P("#000000", n=0, alpha=0, px=[[0, 0, K], [1, 0, K]]), name="temple_r"),
        ], parent="body"),
    ]
    bones += feelers("head", 1.2, 4.6, -3.3, 3, beads("#c8b088", "#a08860"), up=40, out=30)
    bones += jlegs("body", [(0.9, 1.4, -0.6, 1, 45, 20, 30), (1.2, 1.4, 0.4, 1, 5, 20, 30), (1.2, 1.4, 1.4, 2, -40, 20, 28)],
                   P("#dcc8a4"), P("#ccb890"), inflate=-0.27)
    return {"id": "bookworm", "seed": 112, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(feeler_idle(2, 10),
                                           {"head": {"rotation": [kf(0, [0, 0, 0]), kf(1, [6, 0, 8]), kf(2, [6, 0, 8]), kf(2.5, [0, 0, 0]),
                                                                  kf(3.2, [-4, 10, 0]), kf(4, [0, 0, 0])]}},
                                           bob("body", 2, 0.1))},
        "walk": {"len": 0.3, "bones": merge(wave_gait(3, 0.3, 22, 12), feeler_idle(0.3, 8),
                                            {"head": {"rotation": cycle(0.3, [[0, 0, 4], [0, 0, -4]])}})},
    }}


# ================================================================ RARE

SHELL = not os.environ.get("BL_NO_SHELL")


def scorpion():
    """Glow: an inflated pale-cyan shell (glow=True) wraps every body part. GeckoLib cuts glowmask pixels out of the
    base texture, so by day the shell is invisible and the scorpion is plain amber; the glow layer draws the cyan
    shell full-bright, and its strength (BugEntity#glowStrength) decides how much it fluoresces."""
    amber = P("#c89a4a", "grad", c2="#a8782e", hl=True, n=10)
    dark = "#6e4e20"
    glow = P("#9ff8e8", "grad", c2="#5ad8d0", glow=True, n=6)
    seg_top = dict(amber, faces={"up": {"pat": "stripe", "c2": "#9a6c28", "per": 2}})

    def g(o, s, paint, infl=0, **kw):
        out = [C(o, s, paint, inflate=infl, **kw)]
        if SHELL:
            out.append(C(o, s, glow, inflate=infl + 0.12, **kw))
        return out

    bones = [
        B("body", [0, 2, 0], g([-2.5, 1, -2], [5, 2, 6], seg_top) + g([-2, 1, -5], [4, 2, 3], dict(amber, faces={
            "up": {"px": [[1, 1, "#2a1a0a"], [2, 1, "#2a1a0a"], [0, -1, dark], [3, -1, dark]]}}))),
    ]
    # metasoma: chained tail segments curling up over the back
    tail_rot = [-38, -40, -38, -36, -30]
    z = 4
    prev = "body"
    for i in range(1, 6):
        w = 2 if i > 1 else 3
        name = f"tail{i}"
        bones.append(B(name, [0, 2.6, z], g([-w / 2, 1.6, z], [w, 2, 2], amber, infl=-0.1 if i > 2 else 0), parent=prev, rot=[tail_rot[i - 1], 0, 0]))
        prev = name
        z += 2
    bones.append(B("stinger", [0, 2.6, z], g([-1, 1.4, z], [2, 2, 2], P("#d8aa58", hl=True, n=6), infl=0.1)
                   + [C([-0.5, 1.2, z + 1.8], [1, 1, 2], P("#2a1a0e"), p=[0, 1.7, z + 1.8], r=[45, 0, 0], inflate=-0.15)],
                   parent=prev, rot=[-30, 0, 0]))
    # pedipalps with chelae: arm out-forward, claw (palm + fixed finger) pointing forward, movable outer finger
    for side, sx in (("l", 1), ("r", -1)):
        ax = 1.5 if sx > 0 else -4.5
        bones.append(B(f"arm_{side}", [sx * 1.5, 2, -4.5], g([ax, 1.5, -5], [3, 1, 1], amber, infl=-0.05),
                       parent="body", rot=[0, sx * 55, 8 * sx]))
        px_ = 3.5 if sx > 0 else -5.5
        bones.append(B(f"claw_{side}", [sx * 4.5, 2, -4.5],
                       g([px_, 1, -7.5], [2, 2, 3], P("#d4a452", hl=True, n=8)) +
                       g([3.5 if sx > 0 else -4.5, 1.4, -9.5], [1, 1, 2], P("#8a6428"), infl=-0.1),
                       parent=f"arm_{side}", rot=[0, -sx * 45, -8 * sx]))
        bones.append(B(f"finger_{side}", [sx * 5, 2, -7.5],
                       g([4.5 if sx > 0 else -5.5, 1.4, -9.5], [1, 1, 2], P("#6a4818"), infl=-0.1),
                       parent=f"claw_{side}", rot=[0, -sx * 16, 0]))
    bones += jlegs("body", [(2.2, 2, -3.2, 3, 40, 35, 18), (2.4, 2, -1.8, 3, 10, 35, 18),
                            (2.4, 2, -0.6, 3, -20, 35, 18), (2.2, 2, 0.6, 3, -45, 35, 20)],
                   P("#c49448", n=6), P("#b0843c", n=6), inflate=-0.2, shell=glow if SHELL else None)
    tails = [f"tail{i}" for i in range(1, 6)]
    sting = {"tail1": {"rotation": [kf(0, [0, 0, 0]), kf(0.2, [15, 0, 0]), kf(0.3, [-42, 0, 0]), kf(0.45, [-42, 0, 0]), kf(0.7, [0, 0, 0])]}}
    for n in tails[1:]:
        sting[n] = {"rotation": [kf(0, [0, 0, 0]), kf(0.2, [4, 0, 0]), kf(0.3, [-4, 0, 0]), kf(0.45, [-4, 0, 0]), kf(0.7, [0, 0, 0])]}
    sting["stinger"] = {"rotation": [kf(0, [0, 0, 0]), kf(0.2, [-10, 0, 0]), kf(0.3, [22, 0, 0]), kf(0.45, [22, 0, 0]), kf(0.7, [0, 0, 0])]}
    sting["body"] = {"position": [kf(0, [0, 0, 0]), kf(0.2, [0, 0, 0.4]), kf(0.3, [0, 0, -0.6]), kf(0.7, [0, 0, 0])]}
    return {"id": "scorpion", "seed": 113, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(wiggle(tails, 3, 2.5, step=0.12, axis=0), sway("stinger", 3, 6, axis=1),
                                           {"finger_l": {"rotation": cycle(1.5, [[0, 0, 0], [0, -22, 0]])},
                                            "finger_r": {"rotation": cycle(1.5, [[0, 0, 0], [0, 22, 0]])}})},
        "walk": {"len": 0.4, "bones": merge(wave_gait(4, 0.4, 18, 14, step=0.5), wiggle(tails, 0.8, 3, step=0.1, axis=1),
                                            two_sway("arm_l", "arm_r", 0.4, 4, axis=1, mirror=True))},
        "sting": {"len": 0.7, "loop": False, "bones": sting},
    }}


def tarantula():
    fur = "#2e2119"
    hair = P(fur, "spots", c2="#4a3628", d=0.25, n=40, hl=True)
    O, O2 = "#e8782a", "#b85a20"
    knee_px = [[0, 0, O], [1, 0, O], [0, 1, O2], [1, 1, O2]]
    tib = P("#2a1e16", "spots", c2="#4a3628", d=0.2, n=35, faces={f: {"px": knee_px} for f in ("north", "south", "east", "west")})
    tib["faces"]["up"] = {"c": O}
    fem = P("#2a1e16", "spots", c2="#4a3628", d=0.2, n=35)
    chel = P("#241a14", n=30, faces={"north": {"px": [[0, -1, "#0a0806"], [1, -1, "#0a0806"]]}})
    bones = [
        B("body", [0, 3.2, -2.5], [
            C([-2.5, 2.2, -5], [5, 2, 5], dict(hair, faces={"up": {"px": topg([".....", "..K..", ".K.K.", "..K..", "....."], {"K": "#1a120c"})}})),
            C([-1, 3.9, -4.8], [2, 1, 1], P("#16110e", n=0, faces={"up": {"px": [[0, 0, "#5a5660"]]}, "north": {"px": [[1, 0, "#4a4650"]]}}), inflate=-0.1, name="eyes"),
            C([0.05, 1.3, -6.4], [2, 2, 2], chel, inflate=-0.1, name="chelicera_l"),
            C([-2.05, 1.3, -6.4], [2, 2, 2], chel, inflate=-0.1, name="chelicera_r"),
        ]),
        B("abdomen", [0, 3.5, 0], [
            C([-3, 1.5, 0], [6, 4, 6], P(fur, "spots", c2="#5e3a22", d=0.2, n=40, hl=True)),
            C([-2, 5.5, 1], [4, 1, 4], P("#35261c", "spots", c2="#8a5430", d=0.25, n=40)),
            C([-2, 2.5, 6], [4, 2, 1], P("#2a1e16", "spots", c2="#6a4026", d=0.2, n=40)),
            C([-2, 1.0, 1], [4, 1, 4], P("#241a12", n=30)),
            C([-0.5, 2, 6.6], [1, 1, 1], P("#1a120c"), inflate=-0.1, name="spinnerets"),
        ], parent="body", rot=[-4, 0, 0]),
        B("palp_l", [1.3, 2.6, -5], [C([0.8, 2.1, -8], [1, 1, 3], P("#2a1e16", n=35, faces={"north": {"c": "#1a120c"}}), inflate=-0.05)], parent="body", rot=[-25, -12, 0]),
        B("palp_r", [-1.3, 2.6, -5], [C([-1.8, 2.1, -8], [1, 1, 3], P("#2a1e16", n=35, faces={"north": {"c": "#1a120c"}}), inflate=-0.05)], parent="body", rot=[-25, 12, 0]),
    ]
    bones += jlegs("body", [(2.3, 3.2, -4.4, 4, 50, 35, 16), (2.4, 3.2, -3.4, 4, 18, 35, 16),
                            (2.4, 3.2, -2.4, 4, -16, 35, 16), (2.3, 3.2, -1.4, 5, -48, 32, 18)],
                   fem, tib, thick=2, inflate=-0.3)
    return {"id": "tarantula", "seed": 114, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(two_sway("palp_l", "palp_r", 2, 8), bob("body", 4, 0.15),
                                           {"abdomen": {"rotation": cycle(4, [[0, 0, 0], [2, 0, 0]])},
                                            "leg_l1": {"rotation": [kf(0, [0, 0, 0]), kf(2.8, [0, 0, 0]), kf(3.1, [0, -8, 20]), kf(3.4, [0, 0, 0]), kf(4, [0, 0, 0])]}})},
        "walk": {"len": 0.8, "bones": merge(wave_gait(4, 0.8, 15, 14, step=0.5), two_sway("palp_l", "palp_r", 0.8, 10),
                                            {"abdomen": {"rotation": cycle(0.4, [[0, 0, 0], [2, 0, 0]])}})},
    }}


def ice_crawler():
    ice = P("#b4dcf0", "spots", c2="#f4fcff", d=0.14, n=8, hl=True, alpha=0.84)
    seg = P("#aad4ea", "stripe", c2="#86bcd8", per=2, n=6, hl=True, alpha=0.84)
    leg = P("#b8dcec", n=6, alpha=0.9)
    bones = [
        B("body", [0, 2, 0], [
            C([-1.5, 1, -4], [3, 2, 3], ice),
            C([-1.5, 1, -1], [3, 2, 4], dict(seg, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
            C([-1, 1.2, 3], [2, 1, 2], dict(seg, c="#b8d8ea", faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
        ]),
        B("head", [0, 2, -4], [
            C([-1.5, 1.1, -6], [3, 2, 2], P("#c4e4f4", hl=True, n=6, alpha=0.88, faces={
                "east": {"px": [[0, 0, "#3a4a5e"]]}, "west": {"px": [[-1, 0, "#3a4a5e"]]},
                "north": {"px": [[0, -1, "#9ab8c8"], [2, -1, "#9ab8c8"]]}})),
        ], parent="body"),
    ]
    for side, sx in (("l", 1), ("r", -1)):
        bones.append(B(f"cercus_{side}", [sx * 0.6, 1.8, 5], [C([sx * 0.6 - 0.5, 1.3, 5], [1, 1, 4], beads("#a8d0e4", "#d8f0fa"), inflate=-0.32)],
                       parent="body", rot=[-12, sx * 20, 0]))
    bones += feelers("head", 0.6, 2.6, -6, 7, beads("#b8dcec", "#8ab8d0"), up=12, out=25)
    bones += jlegs("body", [(1.2, 1.8, -3.5, 3, 40, 30, 22), (1.2, 1.8, -2.5, 3, 0, 30, 22), (1.2, 1.8, -1.5, 3, -40, 25, 24)],
                   leg, dict(leg, c="#a8cde2"), inflate=-0.3)
    return {"id": "ice_crawler", "seed": 115, "bones": bones, "anims": {
        "idle": {"len": 3, "bones": merge(feeler_idle(3, 12), two_sway("cercus_l", "cercus_r", 3, 6, axis=1), bob("body", 3, 0.1))},
        "walk": {"len": 0.35, "bones": merge(wave_gait(3, 0.35, 24, 14), feeler_idle(0.35, 8), two_sway("cercus_l", "cercus_r", 0.35, 5, axis=1))},
    }}


def giant_isopod():
    L, Lhi, Ldk = "#b9aec6", "#d6cce2", "#9c90ae"
    widths = [7, 8, 8, 8, 8, 7, 6]
    names = ["plate1", "plate2", "plate3", "body", "plate5", "plate6", "plate7"]
    parents = ["plate2", "plate3", "body", None, "body", "plate5", "plate6"]
    TOP = 3.8
    bones = []
    for i in (3, 2, 1, 0, 4, 5, 6):
        w, n, par = widths[i], names[i], parents[i]
        z = -6 + 2 * i
        main = P(L, "grad", c2="#9e92b0", hl=True, n=6, faces={"up": {"px": row(0, w, Ldk)}})
        top = P(Lhi, hl=True, n=6, faces={"up": {"px": row(0, w - 2, "#bcb0cc")}})
        infl = 0.06 if i % 2 else 0
        pivot_z = z + 2 if i < 3 else z if i > 3 else z + 1
        bones.append(B(n, [0, TOP, pivot_z], [C([-w / 2, 0.8, z], [w, 2, 2], main, inflate=infl),
                                               C([-(w - 2) / 2, 2.8, z], [w - 2, 1, 2], top, inflate=infl)], parent=par))
    eye = P("#141018", "spots", c2="#3e3848", d=0.35, n=0, hl=True)
    bones.append(B("head", [0, TOP, -6], [
        C([-3, 0.9, -8], [6, 2, 2], P("#b0a4be", "grad", c2="#9a8eac", hl=True, n=6)),
        C([-2, 2.9, -8], [4, 1, 2], P("#cfc4dc", hl=True, n=6)),
        C([1.4, 1.1, -8.3], [2, 2, 2], eye, name="eye_l"),
        C([-3.4, 1.1, -8.3], [2, 2, 2], eye, name="eye_r"),
    ], parent="plate1"))
    bones += feelers("head", 1.6, 1.4, -8, 8, beads("#c8bcd4", "#9a8eac"), up=4, out=48)
    bones += feelers("head", 0.6, 1.6, -8, 2, P("#b8acc8", n=0), up=-10, out=15, name="antennule")
    bones.append(B("tail", [0, TOP, 8], [
        C([-2, 1.2, 8], [4, 1, 3], P("#b4a8c2", hl=True, n=6, faces={"up": {"px": [[x, 0, "#e8e0f0"] for x in range(0, 4, 2)] + [[0, 1, Ldk], [3, 1, Ldk]]}})),
        C([1.6, 1.0, 7.6], [2, 1, 3], P("#a89cb8", hl=True, n=6), p=[1.8, 1.5, 7.6], r=[0, 28, 0], inflate=-0.05, name="uropod_l"),
        C([-3.6, 1.0, 7.6], [2, 1, 3], P("#a89cb8", hl=True, n=6), p=[-1.8, 1.5, 7.6], r=[0, -28, 0], inflate=-0.05, name="uropod_r"),
    ], parent="plate7"))
    legp = P("#dcd2e4", n=4)
    for i, n in enumerate(names, start=1):
        zc = -6 + 2 * (i - 1) + 1
        bones += slim_legs(n, [(2.6, 1.1, zc, 3, 35 - 70 * (i - 1) / 6, 0)], legp, inflate=-0.28, start=i)
    curl = {"body": {"position": ramp(0.6, [0, 0, 0], [0, 1.9, 0])}}
    for n in ("plate3", "plate2", "plate1", "head"):
        curl[n] = {"rotation": ramp(0.6, [0, 0, 0], [-45, 0, 0])}
    for n in ("plate5", "plate6", "plate7", "tail"):
        curl[n] = {"rotation": ramp(0.6, [0, 0, 0], [45, 0, 0])}
    for i in range(1, 8):
        for s in "lr":
            curl[f"leg_{s}{i}"] = {"scale": ramp(0.35, [1, 1, 1], [0.1, 0.1, 0.1])}
    for n in ("antenna_l", "antenna_r", "antennule_l", "antennule_r"):
        curl[n] = {"scale": ramp(0.4, [1, 1, 1], [0.15, 0.15, 0.15])}
    return {"id": "giant_isopod", "seed": 116, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(feeler_idle(4, 8), two_sway("antennule_l", "antennule_r", 1, 12),
                                           wave_gait(7, 4, 5, 4, step=0.1), bob("body", 4, 0.1))},
        "walk": {"len": 0.9, "bones": merge(wave_gait(7, 0.9, 18, 12, step=0.12, side=0.5), feeler_idle(0.9, 6),
                                            two_sway("antennule_l", "antennule_r", 0.45, 12))},
        "curl": {"len": 0.6, "loop": "hold", "bones": curl},
    }}


# ================================================================ LEGENDARY

def queen_ant():
    RB, DK, GOLD = "#6e2010", "#3e0e06", "#f0c83a"
    glossy = P(RB, "grad", c2=DK, hl=True, n=8)
    gbands = P(RB, "stripe", c2=GOLD, per=3, n=8, hl=True)
    wing_art = ["VV.", "VMV", "V.V", "VVV", "V.V", "VMV", "V.V", ".V."]
    wingp = P("#efe6d0", n=0, alpha=0, px=topg(wing_art, {"V": "#c4b494", "M": "#ece4d2"}))
    bones = [
        B("body", [0, 3, -1.5], [
            C([-1.5, 2, -4], [3, 2, 4], dict(glossy, faces={"up": {"px": topg(["...", ".G.", "...", ".G."], {"G": GOLD})}})),
            C([-1, 4, -3.5], [2, 1, 3], P("#7e2a14", hl=True, faces={"up": {"px": [[0, 1, GOLD], [1, 1, GOLD]]}})),
            C([-0.5, 2.2, 0], [1, 2, 1], P(DK, hl=True), inflate=-0.1, name="node"),
        ]),
        B("gaster", [0, 3.2, 1], [
            C([-2, 1.4, 1], [4, 3, 5], dict(gbands, faces={"east": {"pat": "vstripe"}, "west": {"pat": "vstripe"}})),
            C([-1.5, 4.4, 1.5], [3, 1, 4], dict(gbands, c="#7a2614")),
            C([-1.5, 1.9, 6], [3, 2, 1], P(DK, hl=True)),
            C([-1.5, 0.9, 1.5], [3, 1, 4], P(DK)),
        ], parent="body", rot=[6, 0, 0]),
        B("head", [0, 3, -4], [
                        C([-1.5, 2, -7], [3, 3, 3], P("#7a2412", hl=True, faces={"east": {"px": [[0, 0, EYE], [0, 1, EYE]]}, "west": {"px": [[-1, 0, EYE], [-1, 1, EYE]]},
                                                                     "up": {"px": [[1, -1, "#ffe070"]]}})),
            C([-1.5, 4.8, -6.4], [3, 1, 1], P(GOLD, hl=True, n=6), inflate=-0.12, name="crown"),
            C([-1.5, 5.5, -6.4], [1, 1, 1], P("#ffe070", n=0), inflate=-0.3),
            C([-0.5, 5.6, -6.4], [1, 1, 1], P("#ffe070", n=0), inflate=-0.26),
            C([0.5, 5.5, -6.4], [1, 1, 1], P("#ffe070", n=0), inflate=-0.3),
            C([0.1, 2.0, -8.6], [1, 1, 2], P("#2a0a04"), p=[0.6, 2.5, -7], r=[0, 28, 0], inflate=-0.12),
            C([-1.1, 2.0, -8.6], [1, 1, 2], P("#2a0a04"), p=[-0.6, 2.5, -7], r=[0, -28, 0], inflate=-0.12),
        ], parent="body"),
        B("wing_l", [0.3, 5.5, -2.5], [C([-0.7, 5.5, -2.5], [3, 0, 8], wingp)], parent="body", rot=[-3, 6, 0]),
        B("wing_r", [-0.3, 5.5, -2.5], [C([-2.3, 5.49, -2.5], [3, 0, 8], wingp, mirror=True)], parent="body", rot=[-3, -6, 0]),
    ]
    bones += elbow_antennae("head", 0.9, 4.4, -6.6, 3, 4, P(DK), P("#5a1a0c"), up=60, out=25, bend=-95)
    bones += jlegs("body", [(1, 2.8, -3.3, 3, 45, 28, 26), (1, 2.8, -2.3, 3, 0, 28, 24), (1, 2.8, -1.3, 4, -45, 24, 26)],
                   P(DK), P("#4a140a"), inflate=-0.25)
    flutter = {"wing_l": {"rotation": [kf(0, [0, 0, 0]), kf(3.2, [0, 0, 0]), kf(3.3, [0, 0, 12]), kf(3.4, [0, 0, 0]), kf(3.5, [0, 0, 10]), kf(3.6, [0, 0, 0]), kf(4, [0, 0, 0])]},
               "wing_r": {"rotation": [kf(0, [0, 0, 0]), kf(3.2, [0, 0, 0]), kf(3.3, [0, 0, -12]), kf(3.4, [0, 0, 0]), kf(3.5, [0, 0, -10]), kf(3.6, [0, 0, 0]), kf(4, [0, 0, 0])]}}
    return {"id": "queen_ant", "seed": 117, "bones": bones, "anims": {
        "idle": {"len": 4, "bones": merge(feeler_idle(2, 10), flutter,
                                           {"head": {"rotation": [kf(0, [0, 0, 0]), kf(1, [-6, 12, 0]), kf(2, [-6, 12, 0]), kf(2.6, [-6, -10, 0]), kf(3.4, [-6, -10, 0]), kf(4, [0, 0, 0])]},
                                            "gaster": {"rotation": cycle(4, [[0, 0, 0], [-3, 0, 0]])}})},
        "walk": {"len": 0.45, "bones": merge(wave_gait(3, 0.45, 22, 12), feeler_idle(0.45, 8),
                                             {"gaster": {"rotation": cycle(0.45, [[0, 3, 0], [0, -3, 0]])}})},
    }}


SPECS = {f.__name__: f for f in [
    worker_ant, earwig, termite, millipede, caddisfly_larva,
    orb_weaver, tick, centipede, jumping_spider, honeypot_ant, antlion, bookworm,
    scorpion, tarantula, ice_crawler, giant_isopod,
    queen_ant,
]}
