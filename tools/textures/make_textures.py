"""Generate Bug's Life item/block textures as hand-authored pixel art.

Every sprite is a list of strings, one character per pixel. '.' is transparent;
every other character is looked up in that sprite's palette.
Run from anywhere:  python tools/textures/make_textures.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/main/resources/assets/bugslife/textures"
ITEM = ASSETS / "item"
BUGS = ITEM / "bugs"
BLOCK = ASSETS / "block"
LOGO = ROOT / "src/main/resources/bugslife_logo.png"
PREVIEW = ROOT / "build/texture_previews/sheet.png"

# Jar interior (inclusive) where bug icons are drawn.
JAR_X0, JAR_Y0, JAR_W, JAR_H = 3, 5, 10, 9


def rgba(v):
    if isinstance(v, tuple):
        return v if len(v) == 4 else v + (255,)
    v = v.lstrip("#")
    r, g, b = int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    a = int(v[6:8], 16) if len(v) == 8 else 255
    return (r, g, b, a)


def sprite(name, rows, pal, w=16, h=16):
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


SPRITES = {}  # relative path -> Image


def item(name, rows, pal):
    SPRITES[f"item/{name}.png"] = sprite(name, rows, pal)


def block(name, rows, pal):
    SPRITES[f"block/{name}.png"] = sprite(name, rows, pal)


def bug(name, rows, pal):
    """Bug icon: a 10x9 sprite pasted into the jar interior of a blank 16x16."""
    small = sprite(name, rows, pal, JAR_W, JAR_H)
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    img.paste(small, (JAR_X0, JAR_Y0))
    SPRITES[f"item/bugs/{name}.png"] = img


# ---------------------------------------------------------------- items

NET_ROWS = [
    ".........mIIIm..",
    ".......mInNnNnm.",
    "......INnNnNnNni",
    "......InNnNnNnNi",
    "......mNnNnNnNni",
    ".......mNnNnNni.",
    "........iiiiiid.",
    "........midnNnd.",
    ".......mi.dNnNd.",
    "......lwk..dNnd.",
    ".....lwk...dnd..",
    "....lwk.....dd..",
    "...lwk..........",
    "..lwk...........",
    ".lwk............",
    "kwk.............",
]
item("bug_net", NET_ROWS, {
    "k": "#3a2814", "w": "#7a5530", "l": "#a8804a",
    "i": "#3c3c44", "m": "#7c7c86", "I": "#c9c9d0",
    "n": "#eeeade", "N": "#bdb6a2", "d": "#8a826c",
})

item("silk_net", [
    ".........mIIIm..",
    ".......mInpnNnm.",
    "......INnNnqnNni",
    "......InpnNnNnNi",
    "......mNnNnpnqni",
    ".......mNnqnNni.",
    "........iiiiiid.",
    "........midnpnd.",
    ".......mi.dqnNd.",
    "......lwk..dNnd.",
    ".....lwk...dnd..",
    "....lwk.....dd..",
    "...lwk..........",
    "..lwk...........",
    ".lwk............",
    "kwk.............",
], {
    "k": "#1e1008", "w": "#4e2a14", "l": "#7a4424",
    "i": "#8a5e1a", "m": "#c99a42", "I": "#f4dc8a",
    "n": "#ffffff", "N": "#dfe6f2", "d": "#a8b2cc",
    "p": "#f8dcf0", "q": "#d6f4ea",
})

JAR_PAL = {
    "K": "#3a2410", "L": "#d2a46a", "l": "#b88a52", "c": "#9a6c3a", "d": "#6e4a24",
    "T": "#8e7646", "t": "#d4bc84",
    "O": "#2c3a46",
    "r": (214, 232, 240, 210),
    "h": (226, 242, 250, 130),
    "g": (196, 222, 234, 96),
    "G": (150, 184, 200, 140),
    "W": (255, 255, 255, 235),
}
JAR_ROWS = [
    "................",
    "...KKKKKKKKKK...",
    "...KLlcccccdK...",
    "...KTtTtTtTtK...",
    "..OrrrrrrrrrrO..",
    "..OhggggggggGO..",
    "..OhWgggggggGO..",
    "..OhWgggggggGO..",
    "..OhWgggggggGO..",
    "..OhWgggggggGO..",
    "..OhggggggggGO..",
    "..OhWgggggggGO..",
    "..OhggggggggGO..",
    "..OGGGGGGGGGGO..",
    "...OOOOOOOOOO...",
    "................",
]
item("bug_jar", JAR_ROWS, JAR_PAL)

item("bug_jar_overlay", [
    "................",
    "................",
    "................",
    "................",
    "...rrrrrrrrrr...",
    "...s............",
    "...sW.......e...",
    "...sW.......e...",
    "...sW.......e...",
    "...sW.......e...",
    "...s........e...",
    "...sW.......e...",
    "...s............",
    "................",
    "................",
    "................",
], {
    "r": (240, 250, 255, 110),
    "s": (235, 246, 252, 70),
    "e": (200, 225, 238, 50),
    "W": (255, 255, 255, 235),
})

item("field_guide", [
    "................",
    "..OOOOOOOOOOOO..",
    "..ObBhhhhhhhGO..",
    "..OeehggggggGO..",
    "..ObBhgEgEggGO..",
    "..ObBhggegggGO..",
    "..ObBhgeEeggGO..",
    "..ObBheeEeegGO..",
    "..ObBheeEeegGO..",
    "..ObBhgeEeggGO..",
    "..ObBhggggggGO..",
    "..OeehggggggGO..",
    "..ObBGGGGGGGGO..",
    "..ObpppppppPPO..",
    "..OOOOOOOrOOOO..",
    ".........rR.....",
], {
    "O": "#231c0e", "b": "#7a5230", "B": "#553618",
    "h": "#7f8c4c", "g": "#5c6a34", "G": "#424c24",
    "e": "#dcb44c", "E": "#8e6c22",
    "p": "#efe6c8", "P": "#c8bc98",
    "r": "#c0342a", "R": "#7c1c16",
})

item("silk", [
    "................",
    "................",
    "..........OOO...",
    "........OOwwsO..",
    ".......OwwpssSO.",
    "......OwwssSSSO.",
    ".....OttssSSSO..",
    "....OwwttSSSO...",
    "...OwwssTTSO....",
    "...OwpssSTO.....",
    "..OwssSSSO......",
    "..OwsSSSO.......",
    "..OsSSOO........",
    ".qOOO...........",
    ".q..............",
    "..qq............",
], {
    "O": "#6c6c84", "q": "#dcdcea", "w": "#ffffff", "p": "#f6eefe", "s": "#e2e2ee", "S": "#bcbcd2",
    "t": "#e6cf86", "T": "#ae9448",
})

item("chitin", [
    "................",
    "................",
    "................",
    "...OOOOO........",
    "..OAWWHAOO......",
    "..OWHAaaaaOO....",
    "..OHAaammaamO...",
    "..OAaammaamdO...",
    "...OOAAammamdO..",
    ".....OAaammmdO..",
    "......OOAmmddO..",
    "........OAmddO..",
    ".........OOddO..",
    "...........OO...",
    "................",
    "................",
], {
    "O": "#1e0e04", "d": "#4a2008", "m": "#7a3a0e", "a": "#a85a16",
    "A": "#d8923a", "H": "#f0c070", "W": "#fff0d0",
})

item("glow_goo", [
    "................",
    "................",
    "................",
    "......OOOO......",
    "....OOdmmdOO....",
    "...OdmbbbbmdO...",
    "..OdmbcHcbbmdO..",
    "..OmbcHccbbmdO..",
    ".OdmbcccccbmmdO.",
    ".OdmbbcccbbmmdO.",
    ".OddmbbbbbmmddO.",
    "..OddmmmmmmddO..",
    "...OOddOOOddOO..",
    ".....OdO..OdO...",
    "......O....O....",
    "................",
], {
    "O": "#24520e", "d": "#46961a", "m": "#80cc2a", "b": "#bef04a",
    "c": "#eaffa0", "H": "#ffffff",
})

item("honeydew", [
    "................",
    ".......OO.......",
    "......OaaO......",
    "......OlaO......",
    ".....OlaamO.....",
    ".....OlaamO.....",
    "....OlHaamdO....",
    "....OHlaamdO....",
    "...OlHaaammdO...",
    "...OlHaaammdO...",
    "...OlaaaammdO...",
    "...OaaaammmdO...",
    "....OammmddO....",
    ".....OddddO.....",
    "......OOOO......",
    "................",
], {
    "O": "#5a2c04", "d": "#9c540a", "m": "#d08a16", "a": "#f0b832",
    "l": "#ffd868", "H": "#fff6d2",
})

item("frass", [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "......OOO.......",
    ".....OhlmO......",
    "....OOlmdOOO....",
    "...OhlOdOhlmO...",
    "..OOlmdOOlmdOO..",
    "..OhlOOhlOdOhlO.",
    ".OhlmdOlmdOhlmdO",
    ".OlmdOOmdOOlmddO",
    "..OOOOOOOOOOOOO.",
    "................",
], {
    "O": "#1c1008", "d": "#3a2412", "m": "#583820", "l": "#7c5430", "h": "#a07448",
})

GRUB_ROWS = [
    "................",
    "................",
    ".....OOOOOO.....",
    "...OOCCccscOOO..",
    "..OCCcsccschhHO.",
    ".OCcsccscOOhHHO.",
    ".OCsccsO...OOO..",
    "OCscccO.........",
    "OsssssO.........",
    "OCcccsO.........",
    ".OCcccsO........",
    ".OCcscccsOOOO...",
    "..OCcsccsccsSO..",
    "...OSSsSSsSSO...",
    "....OOOOOOOO....",
    "................",
]
item("crunchy_grub", GRUB_ROWS, {
    "O": "#6e5c3a", "C": "#fffaf0", "c": "#f2e8c8", "s": "#d4c49a", "S": "#bcaa7c",
    "h": "#8c5a24", "H": "#5a3410",
})

item("roasted_grub", [
    "................",
    "................",
    ".....OOOOOO.....",
    "...OOCCcxscOOO..",
    "..OCCcsxcschhHO.",
    ".OCcsxcscOOhHHO.",
    ".OCsccsO...OOO..",
    "OCscxcO.........",
    "OsssssO.........",
    "OCxccsO.........",
    ".OCcccsO........",
    ".OCcscxcsOOOO...",
    "..OCcsxcsccsSO..",
    "...OSSsSxsSSO...",
    "....OOOOOOOO....",
    "................",
], {
    "O": "#3a1c08", "C": "#f2c272", "c": "#d6964a", "s": "#a8661e", "S": "#7e4614",
    "x": "#4a260c", "h": "#4a2810", "H": "#2a1406",
})

item("candied_grub", [
    "..y.............",
    ".yWy............",
    "..y..OOOOOO.....",
    "...OOCWccscOOO..",
    "..OCWcsccschhHO.",
    ".OCWsccscOOhHHO.",
    ".OWsccsO...OOO..",
    "OCscccO.........",
    "OsssssO.........",
    "OCgccsO.........",
    ".OCcccsO........",
    ".OCcscccsOOOO...",
    "..OCcsccsccsSO..",
    "...OSSsSgsSSO...",
    "....OOOOgOOO....",
    "........O.......",
], {
    "O": "#6a2c04", "C": "#ffd27a", "c": "#eca038", "s": "#c0701e", "S": "#94500e",
    "g": "#ffc840", "W": "#fffbe8", "y": "#ffe89a", "h": "#5a2a0c", "H": "#381806",
})

item("bug_skewer", [
    "...............p",
    "...........OOOw.",
    "..........OlaaO.",
    "..........OaadO.",
    "..........OadDO.",
    ".........DwOOO..",
    "......OOOw......",
    ".....OlaaOD.....",
    "....DOaadO......",
    ".....OadDO......",
    "....DwOOO.......",
    ".OOOw...........",
    "OlaaOD..........",
    "OaadO...........",
    "OadDO...........",
    "wOOO............",
], {
    "w": "#b48c56", "p": "#e0c490",
    "O": "#3a1e0a", "l": "#eab668", "a": "#c8883a", "d": "#9a5a22", "D": "#5a3010",
})

item("cricket_cookie", [
    "................",
    ".............K..",
    ".....OOOOOO.K.k.",
    "...OOlcccccOO...",
    "...OllcKkccdO...",
    "..OlcKkcccccdO..",
    "..OlccccckcddO..",
    ".OlcccccccKkddO.",
    ".OcccKcccccccdO.",
    ".OcccKkcccdccdO.",
    "..OccccccKkcdO..",
    "..OcKccccccddO..",
    "...OdccKkcddO...",
    "...OOddddddOO...",
    ".....OOOOOO.....",
    "................",
], {
    "O": "#5a3410", "l": "#f0c878", "c": "#d8a04c", "d": "#aa7030",
    "K": "#2e1a0a", "k": "#5a3a1e",
})

item("glow_jelly", [
    "................",
    "................",
    "................",
    "......OOOO......",
    "....OOJJjjOO....",
    "..OOJWjjjjjgOO..",
    ".OJjjjjjjjjggO..",
    "OlrrrrrrrrrrrrbO",
    ".OlbbbbbbbbbbBO.",
    ".OlbbbbbbbbbbBO.",
    "..OlbbbbbbbbBO..",
    "...OlbbbbbbBO...",
    "....OBbbbbBO....",
    ".....OOOOOO.....",
    "................",
    "................",
], {
    "O": "#3a200c", "l": "#b48048", "r": "#9c6a36", "b": "#865628", "B": "#5e3a1a",
    "j": "#c8ff52", "J": "#ecffa8", "g": "#8ee02c", "W": "#ffffff",
})

# ------------------------------------------------------------ bug icons
# 10 x 9, drawn top-down (head up) unless noted.

bug("ladybug", [
    "...K...K..",
    "....KKK...",
    "...WKKKW..",
    "..kLRKRrk.",
    ".kLRRKRRrk",
    ".kRKRKRKrk",
    ".kRRRKRRrk",
    ".krKRKRKrk",
    "..krrKrrk.",
], {"K": "#18181e", "W": "#f0f0e6", "R": "#d82a1e", "L": "#ff6e4e",
    "r": "#9c1a12", "k": "#3a0806"})

bug("aphid", [
    "..........",
    "....d.d...",
    "....eGe...",
    "...dlgGd..",
    "...GlggG..",
    "..dGlggGd.",
    "...GgggG..",
    "...tGGGt..",
    "...t...t..",
], {"g": "#96da52", "l": "#c8f488", "G": "#5ea42c", "d": "#2e6a18",
    "t": "#24520e", "e": "#8c1a1a"})

bug("firefly", [
    "...K...K..",
    "....oKo...",
    "...oOKOo..",
    "...ybKby..",
    "..KybKbyK.",
    "...ybKby..",
    "..KybKbyK.",
    "...GgWgG..",
    "....GgG...",
], {"K": "#1a120c", "o": "#f07c2c", "O": "#c0401a", "b": "#3c2a1c",
    "y": "#e8d88c", "g": "#e8ff5c", "G": "#b0dc2c", "W": "#ffffc8"})

bug("cricket", [
    ".a......a.",
    "..a....a..",
    "...KbbK...",
    "..KBssBK..",
    "...BbbB...",
    "..KbssbK..",
    ".LLbsbbLL.",
    "LL.bssb.LL",
    "L...bb...L",
], {"a": "#4a3424", "K": "#140e0a", "b": "#3c2a1c", "B": "#5a3e2a",
    "s": "#6e4e34", "L": "#2a1c12"})

bug("pill_bug", [
    "..a....a..",
    "...KggK...",
    "..KlhlgK..",
    ".KGGGGGGK.",
    "KlhllgggGK",
    "KGGGGGGGGK",
    "KlhllgggGK",
    ".KGGGGGGK.",
    "..KKKKKK..",
], {"a": "#2a2e36", "K": "#1e2228", "g": "#6c7682", "G": "#4a525c",
    "l": "#9aa4b0", "h": "#c4ccd4"})

bug("water_strider", [
    "..l....l..",
    "...l..l...",
    "....KK....",
    "llllbbllll",
    "....bb....",
    "...lbbl...",
    "..l.bb.l..",
    ".l..bb..l.",
    "l........l",
], {"K": "#141410", "b": "#3e3c30", "l": "#5c5846"})

bug("monarch", [
    "KWKK..KKWK",
    "KooKKKKooK",
    "WoOoKKoOoW",
    "KoKoKKoKoK",
    ".KKKKKKKK.",
    ".KooKKooK.",
    ".WoKKKKoW.",
    "..KK..KK..",
    "..........",
], {"K": "#161010", "W": "#f6f6f0", "o": "#f28a1e", "O": "#c85c12"})

bug("silk_moth", [
    ".Aa....aA.",
    "..Aa..aA..",
    ".SScCCcSS.",
    "SCCcCCcCCS",
    "SCcsCCscCS",
    "SccsCCscsS",
    ".SSsCCsSS.",
    "..SScCSS..",
    "....SS....",
], {"A": "#6a4424", "a": "#9a6c3c", "C": "#fffaee", "c": "#eee2c4",
    "s": "#d4c4a0", "S": "#a8946c"})

bug("dragonfly", [
    "....eE....",
    ".wwwtTwww.",
    "wwwWtTWwww",
    ".wwwbBwww.",
    "wwwWbBWwww",
    "....bB....",
    "....BK....",
    "....bB....",
    "....BK....",
], {"e": "#48e8cc", "E": "#1c9c8a", "t": "#2a9a78", "T": "#1c6a54",
    "b": "#2e70e6", "B": "#163e92", "K": "#0e1830",
    "w": (184, 218, 238, 200), "W": (120, 160, 190, 230)})

bug("dung_beetle", [
    "..........",
    ".DDDD.....",
    "DlldbD....",
    "DlbbBD.KK.",
    "DbdbBDKgkK",
    "DbbBBKgkkK",
    "DbBBdKkkkK",
    ".DDDD.KKKK",
    "......K.K.",
], {"D": "#3a2410", "l": "#b27c42", "b": "#8a5a2a", "B": "#5e3a18",
    "d": "#6e4620", "K": "#0e0c10", "k": "#2a2630", "g": "#58546a"})

bug("cave_weta", [
    "a........a",
    ".a......a.",
    "..aDTtDa..",
    ".D.TTtt.D.",
    "D.dTtttd.D",
    "..TtddtT..",
    ".DTtddtTD.",
    "D..dttd..D",
    "D...tt...D",
], {"a": "#8a7050", "D": "#8e7652", "T": "#f2dcb4", "t": "#d8c098",
    "d": "#a88a60"})

bug("walking_stick", [
    ".....l...B",
    "......l.Bb",
    "...l...Bb.",
    "....l.Bbl.",
    ".....Bb..l",
    "..l.Bbl...",
    "...Bb..l..",
    "..Bbl.....",
    ".Bb..l....",
], {"B": "#a88452", "b": "#6e5430", "l": "#5c4828"})

bug("jewel_beetle", [
    "...K..K...",
    "...KRrK...",
    "..KRrrrK..",
    ".KgYggGGK.",
    "lKgYgggGKl",
    ".KyYygGgK.",
    "lKyYyyggKl",
    ".KoyYyyoK.",
    "..KooooK..",
], {"K": "#0e2a1c", "R": "#f07030", "r": "#c43c1a", "g": "#3cd06c",
    "G": "#1e9048", "Y": "#f4f07a", "y": "#d8d034", "o": "#e8942a",
    "l": "#1a6a4a"})

bug("stag_beetle", [
    ".M......M.",
    ".mM....Mm.",
    "..mMKKMm..",
    "...KCcK...",
    "l.KCccdK.l",
    ".KCcdccdK.",
    "lKCcdccdKl",
    ".KccdccdK.",
    "..KddddK..",
], {"M": "#d86c36", "m": "#a8421e", "K": "#140a06", "C": "#7a3e22",
    "c": "#52281a", "d": "#32180e", "l": "#241008"})

bug("glowworm", [
    "..........",
    ".KpPpPpcC.",
    ".KPsPsPCc.",
    "..t.t.t.t.",
    "..d.t.d.t.",
    "..t.d.t.t.",
    "..t.t.t.d.",
    "..d.t.d...",
    "....d.....",
], {"K": "#3a4a38", "p": "#eef4e6", "P": "#ccd8c4", "s": "#aab8a4",
    "c": "#8cfcff", "C": "#40d4e4", "t": (190, 236, 244, 190), "d": "#a8ffff"})

bug("hercules_beetle", [
    "....gK....",
    "....gK....",
    "...KgKK...",
    "..KgKKKK..",
    "lKgKKKKKKl",
    ".KYKyoyyK.",
    "lKyyyoKyKl",
    ".KyKyoyoK.",
    "..KyoooK..",
], {"K": "#121214", "g": "#4c4c56", "Y": "#dccf8a", "y": "#bcae68",
    "o": "#8c7e46", "l": "#1e1e22"})

bug("ember_beetle", [
    "...K..K...",
    "...yKKy...",
    "..KbBbbK..",
    ".KBoObbbK.",
    "lKbbrOobKl",
    ".KbbbbObK.",
    "lKOobbbbKl",
    ".KbrObObK.",
    "..KbbbbK..",
], {"K": "#0c0808", "y": "#ffe040", "b": "#2c2626", "B": "#443c3c",
    "o": "#ff8c1c", "O": "#ffc442", "r": "#c43c0a", "l": "#1c1414"})

bug("sculk_mite", [
    "..T....T..",
    "...T..T...",
    "..KtTTtK..",
    ".KtcTTtcK.",
    "KtTtCCtTtK",
    "KttcttcttK",
    ".KttTTttK.",
    "K.KtttK..K",
    "..K...K...",
], {"T": "#1e6c7c", "K": "#041418", "t": "#0e3a44", "c": "#30e8f0",
    "C": "#b4ffff"})

bug("golden_scarab", [
    "...G..G...",
    "..KbggbK..",
    "..KyWgGK..",
    ".KyWggggK.",
    "GKyggbgGKG",
    ".KgggBgGK.",
    "GKyggggGKG",
    ".KGgggGGK.",
    "..KGGGGK..",
], {"K": "#4a2a04", "g": "#e8b020", "G": "#b8800e", "y": "#ffe060",
    "W": "#fff8c4", "b": "#2e6cb8", "B": "#1a3c84"})

bug("void_moth", [
    ".La....aL.",
    "..La..aL..",
    ".kkpLLpkk.",
    "kpwPLLPpPk",
    "kPmMlLMmpk",
    "kpPplLpwPk",
    ".kpPlLPpk.",
    "..kkLLkk..",
    "....kk....",
], {"k": "#140820", "p": "#2c1244", "P": "#40225c", "l": "#c4a4e4",
    "L": "#e4d4f4", "a": "#9a78c8", "m": "#ff54c4", "M": "#ffaae4",
    "w": "#ffffff"})

# ---------------------------------------------------------------- blocks

OAK = {"l": "#56391c", "d": "#3c2814", "D": "#2a1a0c"}
GLASS = {"a": (220, 236, 242, 18), "s": (236, 246, 252, 120), "S": (226, 240, 248, 80)}

block("terrarium_glass", [
    "dlldllldlldllldD",
    "laaaaaaaaaaaaaad",
    "laaasaaSaaaaaaaD",
    "daasaaSaaaaaaaad",
    "lasaaSaaaaaaaaaD",
    "laaaSaaaaaaaaaad",
    "daaSaaaaaaaaaaaD",
    "laSaaaaaaaaaaaad",
    "laaaaaaaaaaaaaaD",
    "daaaaaaaaaaaaaad",
    "laaaaaaaaaaaaaaD",
    "laaaaaaaaaaaaasd",
    "daaaaaaaaaaaasaD",
    "laaaaaaaaaaasaad",
    "laaaaaaaaaaaaaaD",
    "dDDdDDDdDDdDDDdD",
], {**OAK, **GLASS})

block("terrarium_top", [
    "dlldllldlldllldD",
    "lw.w.w.w.w.w.w.d",
    "d.w.w.w.w.w.w.wD",
    "lw.w.w.w.w.w.w.d",
    "l.w.w.w.w.w.w.wD",
    "dw.w.w.w.w.w.w.d",
    "l.w.w.w.w.w.w.wD",
    "lw.w.w.w.w.w.w.d",
    "d.w.w.w.w.w.w.wD",
    "lw.w.w.w.w.w.w.d",
    "l.w.w.w.w.w.w.wD",
    "dw.w.w.w.w.w.w.d",
    "l.w.w.w.w.w.w.wD",
    "lw.w.w.w.w.w.w.d",
    "d.w.w.w.w.w.w.wD",
    "dDDdDDDdDDdDDDdD",
], {**OAK, "w": "#3a3a42"})

block("firefly_lantern", [
    "KKKKKKKmmmmKmi..",
    "KgWggKKmiiiKiK..",
    "KggyGKKivviKKm..",
    "KyggWKKivviKmi..",
    "KgWggKKiiiiKiK..",
    "KGggyKKKKKKKKm..",
    "KKKKKK..........",
    "................",
    "mmmimmmK........",
    "iiiKmiiK........",
    "....miiK........",
    "....KKKK........",
    "................",
    "................",
    "................",
    "................",
], {"K": "#1e1e24", "i": "#34343c", "m": "#52525e", "v": "#0e0e12",
    "g": "#d6f060", "G": "#b2d040", "y": "#f0ff94", "W": "#ffffd8"})

# ------------------------------------------------------------------ logo

LOGO_PAL = {
    "N": "#1a2240", "n": "#243060", "v": "#2e3c74", "R": "#10162c",
    "G": "#2e6a2a", "g": "#4a9a36", "H": "#6cc048",
    "K": "#3a2410", "L": "#d2a46a", "c": "#a0703c", "d": "#6e4a24",
    "T": "#8e7646", "t": "#d4bc84",
    "O": "#9cc4d6", "o": "#6a90a6",
    "a": "#2c4a5c", "b": "#3c6a5c", "e": "#5a8e4c", "f": "#8ebc3c",
    "W": "#ffffff", "y": "#f0ff80", "Y": "#d4f040",
    "k": "#1c140e", "x": "#f07c2c", "p": "#e8d88c",
    "r": "#d82a1e", "q": "#ff6e4e", "s": "#9c1a12", "z": "#18181e", "w": "#f0f0e6",
}
LOGO_ROWS = [
    "..............RRRR..............",
    "..........RRRRNNNNRRRR..........",
    "........RRNNNNNNNNNNNNRR........",
    ".......RNNNNNNNNNNNNvNNNR.......",
    ".....RRKKKKKKKKKKNNNNNNNNRR.....",
    "....RRNKLLcccccdKNNNNNNNNNRR....",
    "....RnnKLcccccddKnNNNNNNNNNR....",
    "...RnnnKTtTtTtTtKnnNNNNNyNNNR...",
    "..RnnnOOOOOOOOOOOOnnNNNNNNNNNR..",
    "..RnnOoaaaaaaaaaaoOnNNNNNNNNNR..",
    ".RnnnOaabbbbbbbaaaOnnNNNNNYNNNR.",
    ".RnnnOaWbbbbbbbbaaOnnNNNNNNNNNR.",
    ".RnnnObWbkeeekbbbaOnnnNyNNNNNNR.",
    ".RnnnObWeexkxeebbaOnnnNNNNNNNNR.",
    "RnnnnObWexxkxxeebbOnnnNNNNNNNNNR",
    "RnnnnObWepkkkpeebbOnnnNNNNNNNNNR",
    "RnnnnObWkpkkkpkebbOnnnNNNNNNNNNR",
    "RnnnnObeepkkkpeebbOnnzNNzNNNNNNR",
    ".RnnnObbkpkkkpkbbaOnnNzzzNNNNNR.",
    ".RnnnObWbYyWyYbbbaOnnwzzzwNNNNR.",
    ".RNnnOaWbbYyYbbbaaOnsqrzrrsNNNR.",
    ".RNnnOaabbbbbbbaaaOsqrzrzrrsNNR.",
    "..RNnOaaaaaaaaaaaaOsrrrzrrrsNR..",
    "..RNNOaaaaaaaaaaaaOsrzrzrzrsNR..",
    "...RHOaaaaaaaaaaaaONsrrzrrsHR...",
    "....RNOOOOOOOOOOOOgNgsssssgR....",
    "....RRggggggggggggggggggggRR....",
    ".....RRGGGGGGGGGGGGGGGGGGRR.....",
    ".......RGGGGGGGGGGGGGGGGR.......",
    "........RRGGGGGGGGGGGGRR........",
    "..........RRRRGGGGRRRR..........",
    "..............RRRR..............",
]


def make_logo():
    img = sprite("logo", LOGO_ROWS, LOGO_PAL, 32, 32)
    return img.resize((128, 128), Image.NEAREST)


# --------------------------------------------------------------- output

def contact_sheet(images):
    """Every texture at 8x on a checkerboard, labelled with its path."""
    jar = SPRITES["item/bug_jar.png"]
    over = SPRITES["item/bug_jar_overlay.png"]
    tiles = []
    for path, img in images.items():
        tiles.append((path, img))
        if path.startswith("item/bugs/"):
            comp = jar.copy()
            comp.alpha_composite(img)
            comp.alpha_composite(over)
            tiles.append(("  in jar", comp))
    scale, pad, label_h = 8, 8, 14
    cell_w, cell_h = 16 * scale + pad, 16 * scale + label_h + pad
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w + pad, rows * cell_h + pad + 150), (60, 60, 66, 255))
    draw = ImageDraw.Draw(sheet)
    for i, (path, img) in enumerate(tiles):
        cx = pad + (i % cols) * cell_w
        cy = pad + (i // cols) * cell_h
        size = 16 * scale
        bg = Image.new("RGBA", (size, size))
        bd = ImageDraw.Draw(bg)
        for yy in range(0, size, 16):
            for xx in range(0, size, 16):
                c = (150, 150, 158, 255) if (xx + yy) // 16 % 2 else (120, 120, 128, 255)
                bd.rectangle([xx, yy, xx + 15, yy + 15], fill=c)
        big = img.resize((size, size), Image.NEAREST) if img.size[0] < size else img.resize((size, size), Image.NEAREST)
        bg.alpha_composite(big)
        sheet.alpha_composite(bg, (cx, cy))
        draw.text((cx, cy + size + 2), path.replace("item/", "").replace(".png", ""), fill=(235, 235, 235, 255))
    return sheet


def main():
    for path, img in SPRITES.items():
        out = ASSETS / path
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
    logo = make_logo()
    logo.save(LOGO)
    allimgs = dict(SPRITES)
    allimgs["bugslife_logo"] = logo
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    contact_sheet(allimgs).save(PREVIEW)
    print(f"wrote {len(SPRITES)} textures + logo; preview at {PREVIEW}")


if __name__ == "__main__":
    main()
