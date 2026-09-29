"""Generate the chitin armor, shield and block textures as hand-authored pixel art.

Same approach as make_textures.py: every sprite (or model face) is a list of
strings, one character per pixel. '.' is transparent; every other character is
looked up in the palette. Model textures (armor layers, shield) are assembled
by pasting each face at its UV position.

Run from anywhere:  python tools/textures/chitin_textures.py
Preview sheet:      build/texture_previews/chitin_sheet.png
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/main/resources/assets/bugslife/textures"
PREVIEW = ROOT / "build/texture_previews/chitin_sheet.png"


def rgba(v):
    if isinstance(v, tuple):
        return v if len(v) == 4 else v + (255,)
    v = v.lstrip("#")
    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    a = int(v[6:8], 16) if len(v) == 8 else 255
    return (r, g, b, a)


# Chitin palette: outline, seam, chestnut, amber, honey, sheen, eye slit.
CHITIN = {
    "K": "#3a1f0e", "d": "#52290f", "C": "#6b3a1a", "a": "#8c4e22",
    "A": "#a8622a", "H": "#d89a4a", "S": "#f2c98a", "E": "#140904",
}


def draw(img, x0, y0, rows, pal=CHITIN, name="?"):
    """Paint a string sprite onto img with its top-left corner at (x0, y0)."""
    w = len(rows[0])
    for y, row in enumerate(rows):
        assert len(row) == w, f"{name}: row {y} has {len(row)} chars, expected {w}: {row!r}"
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            assert ch in pal, f"{name}: unknown char {ch!r} at {x},{y}"
            img.putpixel((x0 + x, y0 + y), rgba(pal[ch]))


def sprite(name, rows, pal=CHITIN, w=16, h=16):
    assert len(rows) == h, f"{name}: {len(rows)} rows, expected {h}"
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw(img, 0, 0, rows, pal, name)
    return img


def mirror(rows):
    return [r[::-1] for r in rows]


OUT = {}  # relative path -> Image

# ---------------------------------------------------------------- item icons
# Silhouettes follow the vanilla armor icon footprints; the pixels are our own.

OUT["item/chitin_helmet.png"] = sprite("chitin_helmet", [
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "....KAHSSHAK....",
    "...KAHHSSHACK...",
    "...KHHASSAACK...",
    "...KHAAHSAaCK...",
    "...KaAAHHAaCK...",
    "...KdddKKdddK...",
    "...KAKEEEEKCK...",
    "....KC....CK....",
    "................",
    "................",
    "................",
    "................",
])

OUT["item/chitin_chestplate.png"] = sprite("chitin_chestplate", [
    "................",
    "................",
    ".KKKKK....KKKKK.",
    ".KHSHK....KHACK.",
    ".KAHAKK..KKAACK.",
    ".KdddHSKdHAdddK.",
    ".KAHHSAKdHAACCK.",
    ".KKKHSAKdHACKKK.",
    "...KHSAKdHACK...",
    "...KAHAKdAACK...",
    "...KdddKdddCK...",
    "...KHSAKdHACK...",
    "...KAHAKdACCK...",
    "....KCAKdCCK....",
    ".....KKKKKK.....",
    "................",
])

OUT["item/chitin_leggings.png"] = sprite("chitin_leggings", [
    "................",
    "................",
    "....KKKKKKKK....",
    "...KAHSHHAACK...",
    "...KddddddddK...",
    "...KHSAKKHACK...",
    "...KAHAKKAACK...",
    "...KAAK..KACK...",
    "...KddK..KddK...",
    "...KHSK..KHAK...",
    "...KAHK..KACK...",
    "...KddK..KddK...",
    "...KHAK..KACK...",
    "...KKKK..KKKK...",
    "................",
    "................",
])

OUT["item/chitin_boots.png"] = sprite("chitin_boots", [
    "................",
    "................",
    "................",
    "....KKK..KKK....",
    "...KHAK..KHAK...",
    "...KHSK..KHCK...",
    "...KddK..KddK...",
    "...KHAK..KHAK...",
    "...KAHK..KACK...",
    "..KddAK..KAddK..",
    ".KHSHAK..KHAACK.",
    ".KAAACK..KACCCK.",
    ".KKKK......KKKK.",
    "................",
    "................",
    "................",
])

# ------------------------------------------------------- armor layer 1 (64x32)
# Humanoid UV layout. Head box 8x8x8 at (0,0): top (8,0), faces row y=8:
# right (0), front (8), left (16), back (24). Body 8x12x4 at (16,16): faces row
# y=20: right (16), front (20), left (28), back (32). Arm 4x12x4 at (40,16):
# top (44,16), faces row y=20: outer (40), front (44), inner (48), back (52).
# Leg 4x12x4 at (0,16): top (4,16), bottom (8,16), faces row y=20 at 0/4/8/12.

HEAD_TOP = [  # row 0 = back of the head, row 7 = forehead
    "KCAHSACK",
    "CAAHSAAC",
    "CAHHSHAC",
    "KddKKddK",
    "CAAHSAAC",
    "CAHHSHAC",
    "CAAHSAAC",
    "KAAHSAAK",
]
HEAD_FRONT = [  # horn ridge running down to a point between two eye slits
    "KAAHSAAK",
    "CAHHSHAC",
    "CaAHSAaC",
    "CEEAHEEC",
    "KC....CK",
    ".K....K.",
    "........",
    "........",
]
HEAD_RIGHT = [  # col 0 = back edge, col 7 = front edge
    "KCAAHAAK",
    "CAAHSHAC",
    "CaAHHAaC",
    "KddKdddK",
    "CAHCK...",
    "CaaCK...",
    "KCCK....",
    "........",
]
HEAD_BACK = [  # segmented neck guard
    "KCAHSACK",
    "CAAHSAAC",
    "CaHHSHaC",
    "KddKKddK",
    "CAAHSAAC",
    "KddKKddK",
    ".CaHHaC.",
    "..KKKK..",
]

BODY_FRONT = [  # overlapping plates split down the middle
    "CHSHKdHC",
    "CAHAKdAC",
    "CaAaKdaC",
    "KdddKddK",
    "CHSHKdHC",
    "CAHAKdAC",
    "CaAaKdaC",
    "KdddKddK",
    "CHSHKdHC",
    "CAHAKdAC",
    ".CaAKdC.",
    "..KKKK..",
]
BODY_SIDE = [  # right side; col 3 meets the front
    "CAHC",
    "CAAC",
    "CaaC",
    "KddK",
    "CAHC",
    "CAAC",
    "CaaC",
    "KddK",
    "CAHC",
    "KCCK",
    "....",
    "....",
]
BODY_BACK = [  # elytra: pronotum rim, then two long wing cases
    "CAHHSHAC",
    "KddKKddK",
    "CHSKdHAC",
    "CHSKdHAC",
    "CHAKdHAC",
    "CAHKdAAC",
    "CAAKdAaC",
    "CAAKdaaC",
    "CaAKdaCC",
    "CaCKdCCd",
    ".CCKdCd.",
    "..KKKK..",
]

ARM_TOP = [
    "KCCK",
    "CAHC",
    "CHAC",
    "KCCK",
]
ARM_FACE = [  # two-segment pauldron, gap, bracer
    "AHSA",
    "CAHA",
    "KddK",
    "CHAC",
    "CaaC",
    "KKKK",
    "....",
    "....",
    "KddK",
    "CHAC",
    "CaaC",
    "KKKK",
]
ARM_BACK = [
    "AHHA",
    "CAAC",
    "KddK",
    "CAAC",
    "CaaC",
    "KKKK",
    "....",
    "....",
    "KddK",
    "CAAC",
    "CaaC",
    "KKKK",
]

BOOT_FRONT = [  # cuff, shin plate, toe cap
    "KddK",
    "CHSC",
    "CAHC",
    "CaaC",
    "HSHA",
    "KCCK",
]
BOOT_SIDE = [
    "KddK",
    "CAHC",
    "CaAC",
    "CaaC",
    "CAHC",
    "KCCK",
]
BOOT_SOLE = [
    "KddK",
    "dCCd",
    "dCCd",
    "KddK",
]


def layer_1():
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # helmet
    draw(img, 8, 0, HEAD_TOP, name="head_top")
    draw(img, 0, 8, HEAD_RIGHT, name="head_right")
    draw(img, 8, 8, HEAD_FRONT, name="head_front")
    draw(img, 16, 8, mirror(HEAD_RIGHT), name="head_left")
    draw(img, 24, 8, HEAD_BACK, name="head_back")
    # chestplate
    draw(img, 16, 20, BODY_SIDE, name="body_right")
    draw(img, 20, 20, BODY_FRONT, name="body_front")
    draw(img, 28, 20, mirror(BODY_SIDE), name="body_left")
    draw(img, 32, 20, BODY_BACK, name="body_back")
    draw(img, 44, 16, ARM_TOP, name="arm_top")
    draw(img, 40, 20, ARM_FACE, name="arm_outer")
    draw(img, 44, 20, ARM_FACE, name="arm_front")
    draw(img, 48, 20, ARM_BACK, name="arm_inner")
    draw(img, 52, 20, ARM_BACK, name="arm_back")
    # boots: lower half of the leg box, plus the sole
    draw(img, 8, 16, BOOT_SOLE, name="boot_sole")
    draw(img, 0, 26, BOOT_SIDE, name="boot_outer")
    draw(img, 4, 26, BOOT_FRONT, name="boot_front")
    draw(img, 8, 26, mirror(BOOT_SIDE), name="boot_inner")
    draw(img, 12, 26, BOOT_SIDE, name="boot_back")
    return img


# ------------------------------------------------------- armor layer 2 (64x32)

LEG_TOP = [
    "KCCK",
    "CAAC",
    "CaaC",
    "KCCK",
]
LEG_FRONT = [  # thigh plate, knee cap
    "CHSC",
    "CAHA",
    "CAHC",
    "CaAC",
    "KddK",
    "AHSA",
    "CHHC",
    "CaaC",
    "KCCK",
]
LEG_SIDE = [
    "CAHC",
    "CAAC",
    "CaAC",
    "CaaC",
    "KddK",
    "CAHC",
    "CaAC",
    "CaaC",
    "KCCK",
]
WAIST_FRONT = [  # a belt of tasset plates across the hips
    "KddKKddK",
    "CHSKdHAC",
    "CAHKdAAC",
    "CaAKdAaC",
    "KddKKddK",
]
WAIST_SIDE = [
    "KddK",
    "CAHC",
    "CAAC",
    "CaaC",
    "KddK",
]


def layer_2():
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    draw(img, 4, 16, LEG_TOP, name="leg_top")
    draw(img, 0, 20, LEG_SIDE, name="leg_outer")
    draw(img, 4, 20, LEG_FRONT, name="leg_front")
    draw(img, 8, 20, mirror(LEG_SIDE), name="leg_inner")
    draw(img, 12, 20, LEG_SIDE, name="leg_back")
    draw(img, 16, 27, WAIST_SIDE, name="waist_right")
    draw(img, 20, 27, WAIST_FRONT, name="waist_front")
    draw(img, 28, 27, mirror(WAIST_SIDE), name="waist_left")
    draw(img, 32, 27, WAIST_FRONT, name="waist_back")
    return img


# ------------------------------------------------------------ shield (64x64)
# Plate cube 12x22x1 at UV (0,0): top edge (1..12, 0), bottom edge (13..24, 0),
# right edge x=0, front x=1..12, left edge x=13, back x=14..25, rows 1..22.
# Handle cube 2x6x6 at UV (26,0): top (32,0), bottom (34,0), faces row y=6.
# The base is rendered solid, so every pixel of the used faces is opaque.

SHIELD_FRONT = [  # a domed beetle: pronotum, seam, split elytra, dark rim
    "KKKKKKKKKKKK",
    "KCAHHHHHAACK",
    "KAHSSHHAAAaK",
    "KAHSHAAAAaCK",
    "KCaAAAAAaCCK",
    "KKddddddddKK",
    "KCHHAKdHHaCK",
    "KHSHAKdHSaCK",
    "KHSAAKdHAaCK",
    "KHSAAKdAAaCK",
    "KHHAAKdAaaCK",
    "KAHAAKdAaCCK",
    "KAHAaKdaaCCK",
    "KAAAaKdaCCCK",
    "KAAaCKdaCCdK",
    "KaAaCKdCCCdK",
    "KCaaCKdCCddK",
    "KCCaCKdCCddK",
    "KdCCCKdCddKK",
    "KKdCCKdCdKKK",
    "KKKdCKdCKKKK",
    "KKKKKKKKKKKK",
]
SHIELD_BACK = [  # dark chestnut shell with a stitched leather strap
    "KKKKKKKKKKKK",
    "KCaCCdCCaCdK",
    "KCaCCdCCaCdK",
    "KCCCCdCCaCdK",
    "KCaCCdCCCCdK",
    "KCaCCdCCaCdK",
    "KCaCCdCCaCdK",
    "KKKKKKKKKKKK",
    "KHaHaHaHaHaK",
    "KAAAAAAAAAAK",
    "KAaAAAaAAAaK",
    "KaAAaAAAaAAK",
    "KHaHaHaHaHaK",
    "KKKKKKKKKKKK",
    "KCaCCdCCaCdK",
    "KCaCCdCCCCdK",
    "KCCCCdCCaCdK",
    "KCaCCdCCaCdK",
    "KCaCCdCCaCdK",
    "KCaCCdCCaCdK",
    "KdCCCdCCCddK",
    "KKKKKKKKKKKK",
]


def shield():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    edge_col = ["K" if y in (0, 21) else ("d" if y % 4 == 1 else "C") for y in range(22)]
    draw(img, 0, 1, edge_col, name="shield_right")
    draw(img, 13, 1, edge_col, name="shield_left")
    draw(img, 1, 0, ["KdCCdCCdCCdK"], name="shield_top")
    draw(img, 13, 0, ["KdCCdCCdCCdK"], name="shield_bottom")
    draw(img, 1, 1, SHIELD_FRONT, name="shield_front")
    draw(img, 14, 1, SHIELD_BACK, name="shield_back")
    # handle: dark brown wrapped grip
    for x0 in (32, 34):
        draw(img, x0, 0, ["KK", "dd", "KK", "dd", "KK", "dd"], name="handle_end")
    grip_side = ["KdKdKd", "dCdCdd", "KdKdKd", "dCdCdd", "KdKdKd", "KKKKKK"]
    grip_face = ["dK", "Cd", "dK", "Cd", "dK", "KK"]
    draw(img, 26, 6, grip_side, name="handle_side_a")
    draw(img, 32, 6, grip_face, name="handle_front")
    draw(img, 34, 6, grip_side, name="handle_side_b")
    draw(img, 40, 6, grip_face, name="handle_back")
    return img


# -------------------------------------------------------------- blocks (16x16)

# The three chitin blocks share one low-contrast palette and tile seamlessly, so walls built from any
# mix of them read as one surface rather than a grid of framed squares.
BLK = {"sh": (0x80, 0x46, 0x1e), "base": (0xa0, 0x5c, 0x28), "body": (0xa8, 0x62, 0x2a),
       "rim": (0xbe, 0x78, 0x36), "shine": (0xd0, 0x8c, 0x44), "seam": (0x70, 0x3c, 0x1a)}


def _noisy(col, rnd, amt=4):
    f = 1 + (rnd.random() - 0.5) * amt / 100
    return tuple(max(0, min(255, round(v * f)))for v in col) + (255,)


def chitin_block():
    """Staggered overlapping scales, 8x4 cells, rows offset by half a scale; tiles on every side."""
    import random
    rnd = random.Random(71)
    img = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            row, yy = divmod(y, 4)
            xx = (x + (row % 2) * 4) % 8
            if yy == 0:
                col = BLK["sh"] if xx in (0, 7) else BLK["base"]
            elif yy == 3:
                col = BLK["sh"] if xx in (0, 7) else (BLK["base"] if xx in (1, 6) else BLK["rim"])
            else:
                col = BLK["sh"] if xx == 0 else BLK["body"]
                if yy == 1 and xx in (2, 3):
                    col = BLK["shine"] if xx == 2 else BLK["rim"]
            img.putpixel((x, y), _noisy(col, rnd))
    return img


def chitin_tiles():
    """Running-bond plates, 8x8 with a soft bevel; every seam lands the same way so blocks join."""
    import random
    rnd = random.Random(72)
    img = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            row, yy = divmod(y, 8)
            xx = (x + (row % 2) * 4) % 8
            if yy == 7 or xx == 7:
                col = BLK["seam"]
            elif yy == 0 or xx == 0:
                col = BLK["rim"]
            elif yy == 6 or xx == 6:
                col = BLK["sh"]
            else:
                col = BLK["body"]
            if (yy, xx) == (1, 1):
                col = BLK["shine"]
            img.putpixel((x, y), _noisy(col, rnd))
    return img


OUT["block/chitin_block.png"] = chitin_block()
OUT["block/chitin_tiles.png"] = chitin_tiles()

LAMP_PAL = {
    **CHITIN,
    "W": "#ffffe0", "y": "#f4ff9c", "g": "#d6f060", "G": "#b2d040", "m": "#88c02c",
    "r": "#be7836", "b": "#a8622a", "s": "#80461e", "e": "#703c1a",
}
# frame edges use the tiles' bevel (rim top-left, seam bottom-right) so a lamp set into tiles fits
OUT["block/shell_lamp.png"] = sprite("shell_lamp", [
    "rrrrrrrrrrrrrrre",
    "rbbbbbbbbbbbbbse",
    "rbmGGsgggysGGmse",
    "rbGggsgyygsggGse",
    "rbGggsgyygsggGse",
    "rbssssssssssssse",
    "rbggysyWWysyggse",
    "rbgyysWWWWsyygse",
    "rbgyysWWWWsyygse",
    "rbggysyWWysyggse",
    "rbssssssssssssse",
    "rbGggsgyygsggGse",
    "rbGggsgyygsggGse",
    "rbmGGsgggysGGmse",
    "rsssssssssssssse",
    "eeeeeeeeeeeeeeee",
], LAMP_PAL)

GLASS = {"g": (220, 236, 242, 20), "s": (236, 246, 252, 110), "t": (226, 240, 248, 70)}

OUT["block/reinforced_terrarium_glass.png"] = sprite("reinforced_terrarium_glass", [
    "KKKKdCCCCCCdKKKK",
    "KSHKHAHHAHHAKHAK",
    "KHAKggggggggKACK",
    "KKKKgsgtggggKKKK",
    "CHggsgtgggggggAC",
    "AHgsgtggggggggAC",
    "CHsgtgggggggggAC",
    "CHgtggggggggggAC",
    "CHggggggggggggAC",
    "AHggggggggggggAC",
    "CHgggggggggggsAC",
    "CHggggggggggsgAC",
    "KKKKggggggggKKKK",
    "KHAKggggggggKACK",
    "KAaKaAAaAAaAKCCK",
    "KKKKdCCCCCCdKKKK",
], {**CHITIN, **GLASS})

OUT["block/reinforced_terrarium_top.png"] = sprite("reinforced_terrarium_top", [
    "KKKKdCCCCCCdKKKK",
    "KSHKHAHHAHHAKHAK",
    "KHAK.w.w.w.wKACK",
    "KKKKw.w.w.w.KKKK",
    "CH.w.w.w.w.w.wAC",
    "AHw.w.w.w.w.w.AC",
    "CH.w.w.w.w.w.wAC",
    "CHw.w.w.w.w.w.AC",
    "CH.w.w.w.w.w.wAC",
    "AHw.w.w.w.w.w.AC",
    "CH.w.w.w.w.w.wAC",
    "CHw.w.w.w.w.w.AC",
    "KKKK.w.w.w.wKKKK",
    "KHAKw.w.w.w.KACK",
    "KAaKaAAaAAaAKCCK",
    "KKKKdCCCCCCdKKKK",
], {**CHITIN, "w": "#3a3a42"})

OUT["models/armor/chitin_layer_1.png"] = layer_1()
OUT["models/armor/chitin_layer_2.png"] = layer_2()
OUT["entity/chitin_shield.png"] = shield()


# ------------------------------------------------------------------ preview

def checker(w, h, cell):
    bg = Image.new("RGBA", (w, h))
    bd = ImageDraw.Draw(bg)
    for yy in range(0, h, cell):
        for xx in range(0, w, cell):
            c = (150, 150, 158, 255) if (xx + yy) // cell % 2 else (120, 120, 128, 255)
            bd.rectangle([xx, yy, xx + cell - 1, yy + cell - 1], fill=c)
    return bg


def contact_sheet(images, scale=8):
    """Every texture at 8x on a checkerboard, plus 3x3 tilings of the blocks."""
    pad, label_h = 12, 16
    tiles = list(images.items())
    for path, img in images.items():
        if path.startswith("block/"):
            tiled = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
            for ty in range(3):
                for tx in range(3):
                    tiled.alpha_composite(img, (tx * 16, ty * 16))
            tiles.append((path.replace(".png", "") + " x3", tiled))
    # simple shelf packing, max width 1100
    max_w = 1100
    placed, x, y, shelf_h = [], pad, pad, 0
    for path, img in tiles:
        s = scale if img.width <= 64 else 4
        if path.endswith(" x3"):
            s = 4
        w, h = img.width * s, img.height * s
        if x + w + pad > max_w:
            x, y, shelf_h = pad, y + shelf_h + label_h + pad, 0
        placed.append((path, img, s, x, y))
        x += w + pad
        shelf_h = max(shelf_h, h)
    total_h = y + shelf_h + label_h + pad
    sheet = Image.new("RGBA", (max_w, total_h), (60, 60, 66, 255))
    draw_ = ImageDraw.Draw(sheet)
    for path, img, s, x, y in placed:
        w, h = img.width * s, img.height * s
        bg = checker(w, h, 16)
        bg.alpha_composite(img.resize((w, h), Image.NEAREST))
        sheet.alpha_composite(bg, (x, y))
        draw_.text((x, y + h + 2), path.replace(".png", ""), fill=(235, 235, 235, 255))
    return sheet


def main():
    for path, img in OUT.items():
        out = ASSETS / path
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    contact_sheet(OUT).save(PREVIEW)
    print(f"wrote {len(OUT)} textures; preview at {PREVIEW}")


if __name__ == "__main__":
    main()
