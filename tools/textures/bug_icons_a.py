"""Jar icons for expansion group A (ants, spiders, centipede/millipede, scorpion, isopod and friends),
plus the royal jelly item texture.

Each bug is a 10x9 palette sprite pasted into the jar interior (x=3..12, y=5..13) of a blank 16x16, in the same
style as tools/textures/make_textures.py. '.' is transparent.
Run from anywhere:  python tools/textures/bug_icons_a.py   (also writes a preview to build/texture_previews/icons_a.png)
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ITEM = ROOT / "src/main/resources/assets/bugslife/textures/item"
BUGS = ITEM / "bugs"
PREVIEW = ROOT / "build/texture_previews/icons_a.png"
JAR_X0, JAR_Y0, JAR_W, JAR_H = 3, 5, 10, 9


def rgba(v):
    if isinstance(v, tuple):
        return v if len(v) == 4 else v + (255,)
    v = v.lstrip("#")
    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    a = int(v[6:8], 16) if len(v) == 8 else 255
    return (r, g, b, a)


def sprite(name, rows, pal, w, h):
    assert len(rows) == h, f"{name}: {len(rows)} rows, expected {h}"
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        assert len(row) == w, f"{name}: row {y} has {len(row)} chars: {row!r}"
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            assert ch in pal, f"{name}: unknown char {ch!r} at {x},{y}"
            img.putpixel((x, y), rgba(pal[ch]))
    return img


ICONS = {}
ITEMS = {}


def bug(name, rows, pal):
    small = sprite(name, rows, pal, JAR_W, JAR_H)
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    img.paste(small, (JAR_X0, JAR_Y0))
    ICONS[name] = img


def item(name, rows, pal):
    ITEMS[name] = sprite(name, rows, pal, 16, 16)


# ------------------------------------------------------------ bug icons (10 x 9, head up)

bug("worker_ant", [
    ".a.m..m.a.",
    "..aKHHKa..",
    "...KhHK...",
    "l...TT...l",
    ".l.lTTl.l.",
    "..l.tt.l..",
    "...KGGK...",
    "..KGgGGK..",
    "...KGGK...",
], {"a": "#4a180a", "m": "#2a0c04", "K": "#3a1006", "H": "#9a3a1c", "h": "#d0765a", "T": "#8c3319",
    "t": "#5a1e0c", "G": "#8c3319", "g": "#c8664a", "l": "#4a180a"})

bug("earwig", [
    ".b......b.",
    "..b.KK.b..",
    "....HH....",
    ".l.KPPK.l.",
    "..lOooOl..",
    ".l.KAaK.l.",
    "...KAAK...",
    "..F.KK.F..",
    "...F..F...",
], {"b": "#6a4630", "K": "#1e0e06", "H": "#4a2414", "P": "#3b2014", "O": "#c98a44", "o": "#8a5424",
    "A": "#3a1e12", "a": "#6a3e26", "F": "#7c4424", "l": "#b89060"})

bug("termite", [
    "..b....b..",
    "...bKKb...",
    "..KHHHHK..",
    "..mHhHHm..",
    ".l.OccO.l.",
    "..lCcCCl..",
    ".l.CccC.l.",
    "..OCCCCO..",
    "...OCCO...",
], {"b": "#c8a070", "K": "#6a3410", "m": "#3a1e0c", "H": "#c8742c", "h": "#e8a060", "c": "#e6d6b4",
    "C": "#f4ead2", "O": "#b8a070", "l": "#c8b08a"})

bug("millipede", [
    "..KKKKK...",
    ".KoKKKoK..",
    "KoK...KoK.",
    "KK..KK.KK.",
    "Ko.KhHK.oK",
    "KK.K..KKK.",
    "KoK...oK..",
    ".KoKKKK...",
    "..KKK.....",
], {"K": "#17151a", "o": "#e2562a", "h": "#4a4652", "H": "#26242a"})

bug("caddisfly_larva", [
    "....KK....",
    "..lKhhKl..",
    ".l.lppl.l.",
    "...OSsO...",
    "..OsSTsO..",
    "..OSsTSO..",
    "..OsSsTO..",
    "...OsSO...",
    "....OO....",
], {"K": "#241a0c", "h": "#7a5a30", "p": "#e8dcc0", "l": "#4a3624", "O": "#4a4238", "S": "#8a8378",
    "s": "#b8ad96", "T": "#6e5536"})

bug("orb_weaver", [
    "y.l....l.y",
    ".l.l..l.l.",
    "l.yKccKy.l",
    ".l.KccK.l.",
    "l.KWWWWK.l",
    ".KYKYYKYK.",
    ".KYYKKYYK.",
    "..KYKKYK..",
    "...KKKK...",
], {"l": "#1c1a18", "y": "#d8a820", "K": "#1c1a18", "c": "#5a4e44", "W": "#ece8dc", "Y": "#ecc41c"})

bug("tick", [
    "....mm....",
    "..l.ss.l..",
    ".l.sSSs.l.",
    "l.lsSSsl.l",
    ".l.RrRR.l.",
    "..RrRRRR..",
    "..RRRRRR..",
    "...RRRd...",
    "....dd....",
], {"m": "#241410", "s": "#2a1a14", "S": "#5a4034", "l": "#3a2418", "R": "#7a2a1a", "r": "#b04a30",
    "d": "#5a1c10"})

bug("centipede", [
    "a.a.......",
    ".aHH.y....",
    "y.HBBy.y..",
    ".y.yBBy.y.",
    "..y.yBBy.y",
    "...y.yBBy.",
    "....y.yBBy",
    ".....y.yB.",
    "......y.yy",
], {"a": "#e09a2c", "H": "#5a2210", "B": "#94401e", "y": "#e8a030"})

bug("jumping_spider", [
    "..........",
    "..KKKKKK..",
    ".KwffffwK.",
    ".KsEffsEK.",
    "lKEEffEEKl",
    "lKKKttKKKl",
    "l.KKKKKK.l",
    ".l.l..l.l.",
    "l.l....l.l",
], {"K": "#1c1a1c", "w": "#ece8e0", "f": "#6a5846", "E": "#060608", "s": "#ffffff", "t": "#2fd6b0", "l": "#3a3434"})

bug("honeypot_ant", [
    "..a....a..",
    "...aKKa...",
    "..l.KK.l..",
    ".l.lKKl.l.",
    "...OOOO...",
    "..OyWyyO..",
    "..ObbbbO..",
    "..OyyyyO..",
    "...OOOO...",
], {"a": "#2a1a10", "K": "#2a1a10", "l": "#3a2012", "O": "#b8680e", "y": "#f2ac2c", "W": "#fff6d0",
    "b": "#c8801a"})

bug("antlion", [
    ".J......J.",
    ".J......J.",
    "..J.HH.J..",
    "...jHHj...",
    "..lOSSOl..",
    ".lOSsSSOl.",
    "..OSSsSO..",
    ".lOsSSSOl.",
    "...OSSO...",
], {"J": "#3a2010", "j": "#8a5a32", "H": "#7a6a50", "O": "#5e5444", "S": "#a89a7c", "s": "#7a6e58",
    "l": "#6a5c46"})

bug("bookworm", [
    "..a....a..",
    "...a..a...",
    "..CCCCCC..",
    ".KKKCCKKK.",
    ".KgKKKKgK.",
    ".KKKCCKKK.",
    "..CpCCpC..",
    "..lBBBBl..",
    ".l.BbbB.l.",
], {"a": "#b8a078", "C": "#f2e6cc", "K": "#2a2228", "g": "#d8eef4", "p": "#eab4a4", "B": "#ece0c4",
    "b": "#d4c49c", "l": "#ccb890"})

bug("scorpion", [
    ".cC....Cc.",
    ".CC....CC.",
    "...A..A...",
    "..l.AA.l..",
    ".l.lBBl.l.",
    "..l.BB.l..",
    ".l.lBBl.S.",
    "....TT.T..",
    ".....TT...",
], {"C": "#d4a452", "c": "#5a3a10", "A": "#b8883c", "B": "#c89a4a", "l": "#9a7030", "T": "#c89a4a",
    "S": "#2a1a0e"})

bug("tarantula", [
    "l.l....l.l",
    ".o.lKKl.o.",
    "l.lKccKl.l",
    ".o.KccK.o.",
    "l.lKAAKl.l",
    "..KAaaAK..",
    ".KAaAAaAK.",
    "..KAAAAK..",
    "...KKKK...",
], {"l": "#2a1e16", "o": "#e8782a", "K": "#16100c", "c": "#3a2a20", "A": "#2e2119", "a": "#5e3a22"})

bug("ice_crawler", [
    "a........a",
    ".a.OHHO.a.",
    "...OHHO...",
    "..l.BB.l..",
    ".l.lBBl.l.",
    "l..OBbO..l",
    "...OBBO...",
    "...c..c...",
    "..c....c..",
], {"a": "#6a98b8", "O": "#5a88a8", "H": "#c4e4f4", "B": "#aad4ea", "b": "#eaf8ff", "l": "#7aa8c4",
    "c": "#7aa8c4"})

bug("giant_isopod", [
    ".a.KKKK.a.",
    "a.KEHHEK.a",
    ".KPPPPPPK.",
    ".KppppppK.",
    ".KPPPPPPK.",
    ".KppppppK.",
    "..KPPPPK..",
    "..KppppK..",
    "...KTTK...",
], {"a": "#8a7e9c", "K": "#5a506a", "E": "#141018", "H": "#cfc4dc", "P": "#cfc4dc", "p": "#a498b4",
    "T": "#b4a8c2"})

bug("queen_ant", [
    "..a.GG.a..",
    "...aHHa...",
    "..lKHHKl..",
    ".l.KTTK.l.",
    "l.lWTTWl.l",
    "..WRRRRW..",
    ".W.gGgg.W.",
    "..WRRRRW..",
    "....gg....",
], {"a": "#3e0e06", "G": "#f0c83a", "H": "#8a2c14", "K": "#3e0e06", "T": "#7a2412", "l": "#3e0e06",
    "W": "#d8ccb0", "R": "#6e2010", "g": "#f0c83a"})

# ------------------------------------------------------------ items

item("royal_jelly", [
    "................",
    "................",
    "................",
    "................",
    "......OOOO......",
    ".....OJWWJO.....",
    "....OJJWJJjO....",
    "...OjJJJJJjjO...",
    "..OORRRRRRRROO..",
    "..OjrrrrrrrrdO..",
    "...OjPPPPPPdO...",
    "...OJpPPPPPdO...",
    "...OpPPPPPPdO...",
    "....OddddddO....",
    ".....OOOOOO.....",
    "................",
], {"O": "#4a2408", "J": "#f6e4a4", "W": "#fffbe6", "j": "#dcb862", "R": "#c08444", "r": "#8e5424",
    "P": "#a8683a", "p": "#c8864e", "d": "#6e3a14"})


# --------------------------------------------------------------- output

def composite(icon):
    jar = Image.open(ITEM / "bug_jar.png").convert("RGBA")
    over = Image.open(ITEM / "bug_jar_overlay.png").convert("RGBA")
    comp = jar.copy()
    comp.alpha_composite(icon)
    comp.alpha_composite(over)
    return comp


def preview():
    tiles = []
    for name, img in ICONS.items():
        tiles.append((name, img))
        tiles.append(("  in jar", composite(img)))
    for name, img in ITEMS.items():
        tiles.append((name, img))
    scale, pad, label_h = 8, 8, 14
    cell_w, cell_h = 16 * scale + pad, 16 * scale + label_h + pad
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w + pad, rows * cell_h + pad), (60, 60, 66, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(tiles):
        cx = pad + (i % cols) * cell_w
        cy = pad + (i // cols) * cell_h
        size = 16 * scale
        bg = Image.new("RGBA", (size, size))
        bd = ImageDraw.Draw(bg)
        for yy in range(0, size, 16):
            for xx in range(0, size, 16):
                c = (150, 150, 158, 255) if (xx + yy) // 16 % 2 else (120, 120, 128, 255)
                bd.rectangle([xx, yy, xx + 15, yy + 15], fill=c)
        bg.alpha_composite(img.resize((size, size), Image.NEAREST))
        sheet.alpha_composite(bg, (cx, cy))
        draw.text((cx, cy + size + 2), name, fill=(235, 235, 235, 255))
    return sheet


def main():
    BUGS.mkdir(parents=True, exist_ok=True)
    for name, img in ICONS.items():
        img.save(BUGS / f"{name}.png")
    for name, img in ITEMS.items():
        img.save(ITEM / f"{name}.png")
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview().save(PREVIEW)
    print(f"wrote {len(ICONS)} bug icons + {len(ITEMS)} items; preview at {PREVIEW}")


if __name__ == "__main__":
    main()
