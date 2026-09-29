"""Builds the 3D chitin armour in Blockbench and exports it for GeckoLib's armour renderer.

    python tools/blockbench/armor.py          (build, paint, export, preview)
    python tools/blockbench/armor.py --keep   (leave the project open in Blockbench)

Writes:
    src/main/resources/assets/bugslife/geo/item/armor/chitin_armor.geo.json
    src/main/resources/assets/bugslife/textures/item/armor/chitin_armor.png
    src/main/resources/assets/bugslife/animations/item/armor/chitin_armor.animation.json
    blockbench/chitin_armor.bbmodel
    build/armor_previews/*.png

Coordinates follow GeckoLib's armour convention: the wearer faces -Z, their right side is +X,
and the bones are armorHead/armorBody/armorRightArm/... pivoted where the vanilla parts pivot.

Every scale is a thin plate hinged on its top edge and tipped outward, so rows overlap like
shingles. Base shells sit just outside the skin's overlay layer to keep the silhouette slim.
The texture is painted here, per face, from the UVs Blockbench lays out.
"""
import base64
import io
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bbclient as bb  # noqa: E402
from make_models import acquire_lock, LOCK, write, ROOT, ASSETS  # noqa: E402

ID = "chitin_armor"
PREVIEW = os.path.join(ROOT, "build", "armor_previews")

# chitin palette, matching the chitin item and blocks
K = (0x3a, 0x1f, 0x0e)   # deep shadow
D = (0x52, 0x29, 0x0f)   # seam
C = (0x6b, 0x3a, 0x1a)   # dark shell
A = (0x8c, 0x4e, 0x22)   # shell
B = (0xa8, 0x62, 0x2a)   # plate
H = (0xd8, 0x9a, 0x4a)   # highlight
S = (0xf2, 0xc9, 0x8a)   # shine

BONES = [
    ("armorHead", [0, 24, 0]),
    ("armorBody", [0, 24, 0]),
    ("armorRightArm", [5, 22, 0]),
    ("armorLeftArm", [-5, 22, 0]),
    ("armorRightLeg", [2, 12, 0]),
    ("armorLeftLeg", [-2, 12, 0]),
    ("armorRightBoot", [2, 12, 0]),
    ("armorLeftBoot", [-2, 12, 0]),
]
MIRROR = {"armorRightArm": "armorLeftArm", "armorRightLeg": "armorLeftLeg", "armorRightBoot": "armorLeftBoot"}

cubes = {b: [] for b, _ in BONES}
kinds = {}


def cube(bone, name, o, s, inflate=0.0, r=None, p=None, kind="plate", out="north", mirror=True):
    """Adds a cube; right-side pieces (x > 0) are mirrored onto the left automatically."""
    c = {"name": name, "o": list(o), "s": list(s), "inflate": inflate}
    if r:
        c["r"] = list(r)
        c["p"] = list(p)
    cubes[bone].append(c)
    kinds[name] = (kind, out)
    if not mirror:
        return
    mo = [-(o[0] + s[0]), o[1], o[2]]
    mr = [r[0], -r[1], -r[2]] if r else None
    mp = [-p[0], p[1], p[2]] if p else None
    mout = {"east": "west", "west": "east"}.get(out, out)
    mbone = MIRROR.get(bone, bone)
    mname = name.replace("_r", "_l", 1) if "_r" in name else name + "_l"
    cube(mbone, mname, mo, s, inflate, mr, mp, kind, mout, mirror=False)


# ------------------------------------------------------------------ helmet
H0 = "armorHead"
cube(H0, "cap", [-4, 29, -4], [8, 3, 8], 0.7, kind="shell", out="up", mirror=False)
cube(H0, "skirt", [-4, 24, -1], [8, 5, 5], 0.6, kind="shell", out="south", mirror=False)
# two shell halves meeting at a centre seam, overhanging the brow like a beetle's wing cases
cube(H0, "tent_r", [0.1, 32.8, -5.0], [5, 1, 10], -0.1, [0, 0, -10], [0, 33.2, 0], kind="tent", out="up")
# scale rows down the back of the head
for i, top in enumerate((31.0, 28.6, 26.2)):
    zr = [0, 0, 0]
    if i % 2 == 0:
        cube(H0, f"nape{i}_r", [-0.1, top - 3, 4.55], [5, 3, 1], -0.1, [-12, 0, 0], [2.4, top, 4.65], out="south")
    else:
        cube(H0, f"nape{i}_c", [-2.5, top - 3, 4.7], [5, 3, 1], -0.1, [-12, 0, 0], [0, top, 4.8], out="south", mirror=False)
        cube(H0, f"nape{i}_r", [1.9, top - 3, 4.55], [3, 3, 1], -0.1, [-12, 0, 0], [3.4, top, 4.65], out="south")
# mandible cheek guards and jaw tips
cube(H0, "cheek_r", [4.1, 24.2, -3.6], [1, 3, 3], -0.1, out="east")
cube(H0, "jaw_r", [3.2, 24.0, -4.6], [2, 1, 1], -0.1, [0, 18, 0], [5.0, 24.5, -4.1], out="north")
# short antennae, swept back and out
cube(H0, "antenna_r", [1.0, 33.4, -4.4], [1, 4, 1], -0.3, [30, 0, -20], [1.5, 33.4, -3.9], kind="antenna", out="north")

# ------------------------------------------------------------------ chestplate
B0 = "armorBody"
cube(B0, "cuirass", [-4, 12, -2], [8, 12, 4], 0.45, kind="shell", out="north", mirror=False)
for i, top in enumerate((24.6, 22.3, 20.0, 17.7, 15.4)):
    if i % 2 == 0:
        cube(B0, f"scale{i}_r", [-0.1, top - 3, -3.3], [5, 3, 1], -0.1, [12, 0, 0], [2.4, top, -2.8], out="north")
    else:
        cube(B0, f"scale{i}_c", [-2.5, top - 3, -3.45], [5, 3, 1], -0.1, [12, 0, 0], [0, top, -2.95], out="north", mirror=False)
        cube(B0, f"scale{i}_r", [1.9, top - 3, -3.3], [3, 3, 1], -0.1, [12, 0, 0], [3.4, top, -2.8], out="north")
# wing cases down the back, tucked in toward the sides
cube(B0, "elytron_r", [0.1, 12.8, 2.3], [5, 11, 1], -0.1, [0, 6, 0], [0, 24, 2.8], kind="elytron", out="south")
cube(B0, "scutellum", [-1.5, 21.6, 2.9], [3, 2, 1], -0.1, kind="plate", out="south", mirror=False)

R = "armorRightArm"
cube(R, "sleeve_r", [4, 16, -2], [4, 8, 4], 0.4, kind="shell", out="east")
cube(R, "pauldron_r", [3.6, 24.2, -3], [5, 1, 6], 0, [0, 0, -18], [4.5, 24.7, 0], kind="plate", out="up")
cube(R, "spaulder1_r", [8.3, 20.2, -3.0], [1, 4, 6], -0.2, [0, 0, 8], [8.5, 24.1, 0], out="east")
cube(R, "spaulder2_r", [8.6, 17.8, -2.8], [1, 3, 6], -0.2, [0, 0, 10], [8.8, 20.8, 0], out="east")
cube(R, "bracer_r", [4, 12, -2], [4, 3, 4], 0.45, kind="shell", out="east")
cube(R, "vambrace_r", [8.2, 12.2, -2.0], [1, 3, 4], -0.15, [0, 0, 8], [8.5, 15.2, 0], out="east")

# ------------------------------------------------------------------ leggings
L = "armorRightLeg"
cube(L, "thigh_r", [0, 6, -2], [4, 6, 4], 0.4, kind="shell", out="east")
for i, top in enumerate((12.5, 10.1)):
    cube(L, f"cuisse{i}_r", [-0.3, top - 3, -3.25], [5, 3, 1], -0.1, [12, 0, 0], [2.2, top, -2.75], out="north")
    cube(L, f"tasset{i}_r", [4.1, top - 3, -2.4], [1, 3, 5], -0.15, [0, 0, 10], [4.4, top, 0], out="east")
cube(L, "knee_r", [0.5, 5.0, -3.5], [3, 3, 1], -0.05, [6, 0, 0], [2, 8, -3.0], out="north")

# ------------------------------------------------------------------ boots
F = "armorRightBoot"
cube(F, "boot_r", [0, 0, -2], [4, 5, 4], 0.5, kind="shell", out="east")
for i, top in enumerate((5.6, 3.4)):
    cube(F, f"greave{i}_r", [-0.5, top - 3, -3.35], [5, 3, 1], -0.1, [12, 0, 0], [2, top, -2.85], out="north")
cube(F, "toe_r", [0, -0.5, -3.3], [4, 1, 1], 0.1, kind="plate", out="north")


def spec():
    bones = []
    for name, pivot in BONES:
        bones.append({"name": name, "pivot": pivot, "cubes": cubes[name]})
    return {"id": ID, "seed": 11, "visible_box": [1, 2, 0], "bones": bones}


# ------------------------------------------------------------------ painting
def jitter(c, rnd, amt=6):
    f = 1 + (rnd.random() - 0.5) * amt / 100
    return tuple(max(0, min(255, round(v * f))) for v in c)


CLEAR = None  # transparent: the armour renders as cutout, so clear pixels round the scales off


def paint_scale(px, w, h, rnd):
    """A scale seen from outside: tucked shadow on top, warm body, bright lip, rounded corners."""
    for y in range(h):
        for x in range(w):
            edge = x in (0, w - 1) and w > 2
            if y == 0:
                col = C
            elif y == h - 1:
                col = CLEAR if edge else H
            else:
                col = A if edge else B
            px(x, y, col if col is CLEAR else jitter(col, rnd, 4))
    if w >= 5 and h >= 3:
        px(w // 2, h - 1, S)


def paint_shell(px, w, h, rnd, face):
    """Base shell under the scales: a faint flat scale pattern so it reads as one hide with the plates."""
    for y in range(h):
        for x in range(w):
            if face in ("up", "down"):
                col = A if face == "up" else C
            else:
                row = y // 3
                cx = (x + (row % 2) * 2) % 4
                if y % 3 == 2:
                    col = B if cx in (1, 2) else C
                else:
                    col = A
            px(x, y, jitter(col, rnd, 4))


def paint_tent(px, w, h, rnd, right):
    """Helmet shell half (top face): seam dark, a highlight ridge beside it, brow lip bright."""
    for y in range(h):
        for x in range(w):
            inner = x if right else (w - 1 - x)   # distance from the centre seam
            col = B
            if inner == 0:
                col = D
            elif inner == 1:
                col = H
            elif inner == w - 1:
                col = A
            if y == 0 and inner:
                col = H
            if y == h - 1:
                col = C
            px(x, y, jitter(col, rnd, 4))
    px(1 if right else w - 2, 1, S)


def paint_elytron(px, w, h, rnd):
    for y in range(h):
        for x in range(w):
            col = B
            if x in (0, w - 1):
                col = A
            elif x == 2:
                col = H
            if y == 0:
                col = A
            if y == h - 1:
                col = CLEAR if x in (0, w - 1) else (H if x == 2 else A)
            px(x, y, col if col is CLEAR else jitter(col, rnd, 4))
    px(2, 1, S)


LATERAL = {"north": ("east", "west"), "south": ("east", "west"), "east": ("north", "south"), "west": ("north", "south")}
BACK = {"north": "south", "south": "north", "east": "west", "west": "east"}


def paint_plate_face(px, w, h, rnd, face, out):
    """Faces of a scale plate other than its outer one; the rounded corners are cut through them too."""
    for y in range(h):
        for x in range(w):
            col = C
            if face == BACK.get(out):
                col = CLEAR if y == h - 1 and x in (0, w - 1) and w > 2 else C
            elif face in LATERAL.get(out, ()):
                col = CLEAR if y == h - 1 else C
            elif face == "down":
                ends = (x in (0, w - 1) and w > 2) if out in ("north", "south") else (y in (0, h - 1) and h > 2)
                col = CLEAR if ends else A
            px(x, y, col if col is CLEAR else jitter(col, rnd, 4))


def paint(uv_info, tw, th):
    from PIL import Image
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    rnd = random.Random(1311)
    for c in uv_info:
        kind, out = kinds[c["name"]]
        for face, uv in c["faces"].items():
            if uv is None:
                continue
            x0, y0 = int(round(min(uv[0], uv[2]))), int(round(min(uv[1], uv[3])))
            x1, y1 = int(round(max(uv[0], uv[2]))), int(round(max(uv[1], uv[3])))
            w, h = x1 - x0, y1 - y0
            if w < 1 or h < 1:
                continue

            def px(x, y, col, x0=x0, y0=y0, w=w, h=h):
                if 0 <= x < w and 0 <= y < h:
                    img.putpixel((x0 + x, y0 + y), (0, 0, 0, 0) if col is CLEAR else tuple(col) + (255,))

            if kind == "shell":
                paint_shell(px, w, h, rnd, face)
            elif kind == "antenna":
                for y in range(h):
                    for x in range(w):
                        px(x, y, K if y else H)
            elif kind == "tent":
                if face == "up":
                    paint_tent(px, w, h, rnd, right=c["name"].endswith("_r"))
                else:
                    for y in range(h):
                        for x in range(w):
                            px(x, y, jitter(C if face != "down" else A, rnd, 4))
            elif kind == "elytron" and face == out:
                paint_elytron(px, w, h, rnd)
            elif out == "up":
                # pauldron: scale on top, plain rim elsewhere
                for y in range(h):
                    for x in range(w):
                        col = (H if y == h - 1 else B) if face == "up" else C
                        px(x, y, jitter(col, rnd, 4))
            elif face == out:
                paint_scale(px, w, h, rnd)
            else:
                paint_plate_face(px, w, h, rnd, face, out)
    return img


# ------------------------------------------------------------------ driver
def data_url(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


MANNEQUIN = [
    ("m_head", [-4, 24, -4], [8, 8, 8]), ("m_body", [-4, 12, -2], [8, 12, 4]),
    ("m_rarm", [4, 12, -2], [4, 12, 4]), ("m_larm", [-8, 12, -2], [4, 12, 4]),
    ("m_rleg", [0, 0, -2], [4, 12, 4]), ("m_lleg", [-4, 0, -2], [4, 12, 4]),
    ("m_nose", [-1, 27, -4.3], [2, 1, 0.3]),
]


def previews(img):
    """Adds a grey stand-in body (preview only, after export) and captures four views."""
    os.makedirs(PREVIEW, exist_ok=True)
    # bedrock projects render one texture, so the stand-in borrows one spare pixel of it
    spare = next((x, y) for y in range(img.height) for x in range(img.width) if img.getpixel((x, y))[3] == 0)
    shown = img.copy()
    shown.putpixel(spare, (125, 138, 153, 255))
    safe = data_url(shown).replace("/", "_")
    u, v = spare
    uv = [u + 0.25, v + 0.25, u + 0.75, v + 0.75]
    js_cubes = json.dumps(MANNEQUIN)
    bb.js("(() => { const t = Texture.all[0]; t.fromDataURL(" + json.dumps(safe) + ".split('_').join('/')); "
          "const g = new Group({name: 'mannequin', origin: [0,0,0]}).init(); "
          f"for (const m of {js_cubes}) {{ const c = new Cube({{name: m[0], from: m[1], "
          "to: [m[1][0]+m[2][0], m[1][1]+m[2][1], m[1][2]+m[2][2]], box_uv: false}).addTo(g).init(); "
          f"for (const f in c.faces) c.faces[f].uv = {json.dumps(uv)}; c.applyTexture(t, true); }} "
          "Canvas.updateAll(); return 'ok'; })()")
    try:
        bb.call("delete_offscreen_view", {"view": "arm_prev"})
    except Exception:
        pass
    bb.call("create_offscreen_view", {"id": "arm_prev", "width": 720, "height": 720, "copy_view": "none"})
    target = [0, 18, 0]
    shots = {"front": [22, 32, -52], "back": [-22, 32, 52], "side": [56, 24, 2], "top": [16, 60, -26]}
    out = []
    for name, pos in shots.items():
        bb.call("set_camera_angle", {"view": "arm_prev", "position": pos, "target": target, "projection": "perspective", "fov": 40})
        p = os.path.join(PREVIEW, f"{name}.png")
        bb.save_image("capture_screenshot", {"view": "arm_prev"}, p)
        out.append(p)
    bb.call("delete_offscreen_view", {"view": "arm_prev"})
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in out]
    sheet = Image.new("RGB", (720 * 2, 720 * 2), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * 720, (i // 2) * 720))
    sp = os.path.join(PREVIEW, "sheet.png")
    sheet.save(sp)
    return sp


def main():
    keep = "--keep" in sys.argv
    acquire_lock()
    try:
        src = open(os.path.join(os.path.dirname(__file__), "builder.js"), encoding="utf-8").read()
        src = "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in src.splitlines())
        bb.js(src)
        bb.js(f"JSON.stringify(ModelProject.all.filter(p => p.name === '{ID}').map(p => {{ p.saved = true; p.close(true); return p.name; }}))")
        info = bb.js("JSON.stringify(BL.build(" + json.dumps(spec()) + "))")
        info = json.loads(info) if isinstance(info, str) else info
        uv = bb.js("JSON.stringify(Cube.all.map(c => ({name: c.name, faces: Object.fromEntries("
                   "Object.entries(c.faces).map(([k, f]) => [k, f.uv])) })))")
        uv = json.loads(uv) if isinstance(uv, str) else uv
        tw, th = info["tex"]
        img = paint(uv, tw, th)
        safe = data_url(img).replace("/", "_")  # risky_eval refuses any '//' in the code
        bb.js("(() => { const t = Texture.all[0]; t.fromDataURL(" + json.dumps(safe) + ".split('_').join('/')); "
              "if (t.updateMaterial) t.updateMaterial(); Canvas.updateAll(); return 'ok'; })()")
        exp = bb.js("JSON.stringify(BL.exportAll())")
        exp = json.loads(exp) if isinstance(exp, str) else exp
        write(os.path.join(ASSETS, "geo", "item", "armor", f"{ID}.geo.json"), exp["geo"])
        tex_path = os.path.join(ASSETS, "textures", "item", "armor", f"{ID}.png")
        os.makedirs(os.path.dirname(tex_path), exist_ok=True)
        img.save(tex_path)
        write(os.path.join(ASSETS, "animations", "item", "armor", f"{ID}.animation.json"),
              json.dumps({"format_version": "1.8.0", "animations": {}}, indent=2))
        write(os.path.join(ROOT, "blockbench", f"{ID}.bbmodel"), exp["bbmodel"])
        sheet = previews(img)
        if not keep:
            bb.js(f"JSON.stringify(BL.closeProject('{info['uuid']}', '{ID}'))")
        print(f"{ID}: tex {info['tex']} cubes {info['cubes']} -> {sheet}")
    finally:
        os.rmdir(LOCK)


if __name__ == "__main__":
    main()
