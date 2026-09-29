"""Builds bug models in Blockbench through its MCP plugin and exports them into the mod.

    python tools/blockbench/make_models.py ladybug firefly ...   (no args = all)
    python tools/blockbench/make_models.py --keep ladybug        (leave the project open in Blockbench)

Writes:
    src/main/resources/assets/bugslife/geo/entity/<id>.geo.json
    src/main/resources/assets/bugslife/animations/entity/<id>.animation.json
    src/main/resources/assets/bugslife/textures/entity/<id>.png (+ _glowmask.png)
    blockbench/<id>.bbmodel               (editable source)
    build/bug_previews/<id>_*.png         (screenshots)
"""
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bbclient as bb  # noqa: E402
import bugs  # noqa: E402
import importlib  # noqa: E402
import glob  # noqa: E402
import time  # noqa: E402

# every bugs*.py next to this file contributes a SPECS dict (bugs.py is the original twenty)
ALL_SPECS = {}
for _path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "bugs*.py"))):
    _mod = importlib.import_module(os.path.splitext(os.path.basename(_path))[0])
    ALL_SPECS.update(getattr(_mod, "SPECS", {}))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "bugslife")
PREVIEW = os.path.join(ROOT, "build", "bug_previews")


def write(path, data, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", encoding=None if binary else "utf-8") as f:
        f.write(data)


def data_url_bytes(url):
    return base64.b64decode(url.split(",", 1)[1])


def preview(bug_id):
    os.makedirs(PREVIEW, exist_ok=True)
    try:
        bb.call("delete_offscreen_view", {"view": "bl_prev"})
    except Exception:
        pass
    bb.call("create_offscreen_view", {"id": "bl_prev", "width": 640, "height": 480, "copy_view": "none"})
    size = bb.js("(() => { const b = new THREE.Box3().setFromObject(Project.model_3d || scene); "
                 "return [b.min.x,b.min.y,b.min.z,b.max.x,b.max.y,b.max.z]; })()")
    cx = (size[0] + size[3]) / 2; cy = (size[1] + size[4]) / 2; cz = (size[2] + size[5]) / 2
    ext = max(size[3] - size[0], size[4] - size[1], size[5] - size[2], 4)
    d = ext * 0.95
    shots = {"front": [cx - d * 0.8, cy + d * 0.7, cz - d * 1.1], "back": [cx + d * 0.9, cy + d * 0.8, cz + d * 1.0],
             "top": [cx + 0.01, cy + d * 1.9, cz + 0.01]}
    out = []
    for name, pos in shots.items():
        bb.call("set_camera_angle", {"view": "bl_prev", "position": pos, "target": [cx, cy, cz], "projection": "perspective", "fov": 45})
        p = os.path.join(PREVIEW, f"{bug_id}_{name}.png")
        bb.save_image("capture_screenshot", {"view": "bl_prev"}, p)
        out.append(p)
    # one mid-animation frame of the main movement animation
    for anim in ("walk", "fly", "roll", "hop", "spar", "horn"):
        ok = bb.js("(() => { const a = Animation.all.find(a => a.name.endsWith('." + anim + "')); if (!a) return false; "
                   "a.select(); Timeline.setTime(a.length * 0.3); Animator.preview(); return true; })()")
        if ok is True:
            bb.call("set_camera_angle", {"view": "bl_prev", "position": shots["front"], "target": [cx, cy, cz], "projection": "perspective", "fov": 45})
            p = os.path.join(PREVIEW, f"{bug_id}_{anim}.png")
            bb.save_image("capture_screenshot", {"view": "bl_prev"}, p)
            out.append(p)
    bb.js("(() => { Timeline.setTime(0); Animator.preview(); return true; })()")
    bb.call("delete_offscreen_view", {"view": "bl_prev"})
    return out


def contact_sheet(ids):
    from PIL import Image, ImageDraw
    rows = []
    for i in ids:
        files = sorted(f for f in os.listdir(PREVIEW) if f.startswith(i + "_") and f[len(i) + 1:].split(".")[0] in
                       ("front", "back", "top", "walk", "fly", "roll", "hop", "spar", "horn"))
        rows.append((i, [os.path.join(PREVIEW, f) for f in files]))
    tw, th = 320, 240
    cols = max(len(r[1]) for r in rows)
    sheet = Image.new("RGB", (tw * cols + 120, th * len(rows)), "white")
    d = ImageDraw.Draw(sheet)
    for y, (name, files) in enumerate(rows):
        d.text((4, y * th + th // 2), name, fill="black")
        for x, f in enumerate(files):
            src = Image.open(f).convert("RGBA").resize((tw, th))
            im = Image.new("RGB", (tw, th), (200, 204, 210))
            im.paste(src, (0, 0), src)
            sheet.paste(im, (120 + x * tw, y * th))
            d.text((124 + x * tw, y * th + 4), os.path.basename(f)[len(name) + 1:-4], fill="gray")
    path = os.path.join(PREVIEW, "sheet_" + "_".join(ids[:3]) + ("_etc" if len(ids) > 3 else "") + ".png")
    sheet.save(path)
    return path


def make(bug_id, keep=False):
    spec = ALL_SPECS[bug_id]()
    # close a previous build of this bug (never touches other projects)
    bb.js(f"JSON.stringify(ModelProject.all.filter(p => p.name === '{bug_id}').map(p => {{ p.saved = true; p.close(true); return p.name; }}))")
    info = bb.js("JSON.stringify(BL.build(" + json.dumps(spec) + "))")
    if isinstance(info, str):
        info = json.loads(info)
    exp = bb.js("JSON.stringify(BL.exportAll())")
    if isinstance(exp, str):
        exp = json.loads(exp)
    write(os.path.join(ASSETS, "geo", "entity", f"{bug_id}.geo.json"), exp["geo"])
    if exp["anim"]:
        write(os.path.join(ASSETS, "animations", "entity", f"{bug_id}.animation.json"), exp["anim"])
    write(os.path.join(ASSETS, "textures", "entity", f"{bug_id}.png"), data_url_bytes(exp["png"]), binary=True)
    glow_path = os.path.join(ASSETS, "textures", "entity", f"{bug_id}_glowmask.png")
    if exp["glow"]:
        write(glow_path, data_url_bytes(exp["glow"]), binary=True)
    elif os.path.exists(glow_path):
        os.remove(glow_path)
    write(os.path.join(ROOT, "blockbench", f"{bug_id}.bbmodel"), exp["bbmodel"])
    shots = preview(bug_id)
    if not keep:
        bb.js(f"JSON.stringify(BL.closeProject('{info['uuid']}', '{bug_id}'))")
    print(f"{bug_id}: tex {info['tex']} cubes {info['cubes']} bones {info['bones']} glow {info['glow']} -> {shots[0]}")


LOCK = os.path.join(ROOT, "build", ".blockbench.lock")


def acquire_lock():
    """Blockbench is one shared app: builds from parallel workers must take turns."""
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    waited = 0
    while True:
        try:
            os.mkdir(LOCK)
            return
        except FileExistsError:
            # a lock older than 20 minutes belongs to a crashed run
            if time.time() - os.path.getmtime(LOCK) > 1200:
                os.rmdir(LOCK)
                continue
            if waited % 30 == 0:
                print("waiting for the Blockbench lock...", flush=True)
            time.sleep(2)
            waited += 2


def main():
    args = sys.argv[1:]
    keep = "--keep" in args
    ids = [a for a in args if not a.startswith("--")] or list(ALL_SPECS)
    unknown = [i for i in ids if i not in ALL_SPECS]
    if unknown:
        sys.exit(f"unknown bug ids: {unknown}")
    acquire_lock()
    try:
        run(ids, keep)
    finally:
        os.rmdir(LOCK)


def run(ids, keep):
    src = open(os.path.join(os.path.dirname(__file__), "builder.js"), encoding="utf-8").read()
    # risky_eval rejects comments
    src = "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in src.splitlines())
    print(bb.js(src))
    done = []
    for i in ids:
        try:
            make(i, keep)
            done.append(i)
        except Exception as e:
            print(f"{i}: FAILED {e}")
    for k in range(0, len(done), 4):
        print("sheet:", contact_sheet(done[k:k + 4]))


if __name__ == "__main__":
    main()
