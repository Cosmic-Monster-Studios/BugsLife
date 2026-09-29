"""Jar icons for the group C expansion bugs (hand-drawn 10x9 pixel art, pasted into the jar interior).

    python tools/textures/bug_icons_c.py

Writes src/main/resources/assets/bugslife/textures/item/bugs/<id>.png and a jar-composited preview at
build/texture_previews/icons_c.png. Same format as the bug() icons in make_textures.py: '.' is transparent.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ITEM = ROOT / "src/main/resources/assets/bugslife/textures/item"
BUGS = ITEM / "bugs"
PREVIEW = ROOT / "build/texture_previews/icons_c.png"

JAR_X0, JAR_Y0, JAR_W, JAR_H = 3, 5, 10, 9
ICONS = {}


def rgba(v):
    if isinstance(v, tuple):
        return v if len(v) == 4 else v + (255,)
    v = v.lstrip("#")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), int(v[6:8], 16) if len(v) == 8 else 255)


def bug(name, rows, pal):
    assert len(rows) == JAR_H, f"{name}: {len(rows)} rows"
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        assert len(row) == JAR_W, f"{name}: row {y} has {len(row)} chars: {row!r}"
        for x, ch in enumerate(row):
            if ch != ".":
                assert ch in pal, f"{name}: unknown char {ch!r}"
                img.putpixel((JAR_X0 + x, JAR_Y0 + y), rgba(pal[ch]))
    ICONS[name] = img


# ------------------------------------------------------------------ common

bug("grasshopper", [
    "..a....a..",
    "...a..a...",
    "...eGGe...",
    "..lGLLGl..",
    "...GLLG...",
    "..FGggGF..",
    ".lFGggGFl.",
    "..FgggGF..",
    "..k.GG.k..",
], {"a": "#5a7a2a", "e": "#6a4a24", "G": "#6cc644", "L": "#a8e878", "g": "#4f9e2f",
    "F": "#8ada58", "l": "#3f8a26", "k": "#2f4a1a"})

bug("springtail", [
    "..........",
    "...a..a...",
    "....aa....",
    "...kHHk...",
    "..LhHHhL..",
    ".lLHhHHLl.",
    "..LHHHHL..",
    ".l.LHHL.l.",
    "...f..f...",
], {"a": "#5d5a90", "k": "#1e1c30", "H": "#aaa6dc", "h": "#dcd9f6", "L": "#6a70a8",
    "l": "#6a68a0", "f": "#b9b6e4"})

bug("whirligig_beetle", [
    "..........",
    "...kKKk...",
    "..KgKKgK..",
    "aKbbBBbbKa",
    ".KbBBWBbK.",
    "pKbBBBBbKp",
    ".KbbBBbbK.",
    "pKKbbbbKKp",
    "...KKKK...",
], {"K": "#121216", "k": "#2a2a30", "g": "#8a93a2", "b": "#3a3020", "B": "#6e5a34",
    "W": "#e9eef5", "a": "#1c1a18", "p": "#8c7a4c"})

bug("stink_bug", [
    "a........a",
    ".a..hh..a.",
    "..rKhhKr..",
    ".KbbbbbbK.",
    "KbmbSSbmbK",
    "cbbbSSbbbc",
    ".cbmSSmbc.",
    "..KbddbK..",
    "...KddK...",
], {"a": "#3a2e24", "h": "#6a5644", "r": "#8a2a1a", "K": "#3a2e24", "b": "#7b6650",
    "m": "#57473a", "S": "#c9b38c", "c": "#e0d0a6", "d": "#3d3027"})

# ------------------------------------------------------------------ uncommon

bug("praying_mantis", [
    "..a....a..",
    "...a..a...",
    "...EhhE...",
    "..A.tt.A..",
    "..A.tt.A..",
    ".l.AttA.l.",
    "..lWWWWl..",
    ".l.WwwW.l.",
    "...WwwW...",
], {"a": "#6a8a3a", "E": "#d8f0a0", "h": "#7cc24a", "t": "#6cb23e", "A": "#a4da6e",
    "l": "#5a9a36", "W": "#8dcf58", "w": "#6fae44"})

bug("bombardier_beetle", [
    "..a....a..",
    "...a..a...",
    "...oOOo...",
    "..lOOOOl..",
    ".l.KKKK.l.",
    "..KYKKYK..",
    ".lKKBKKKl.",
    "..KKYYKK..",
    "...KKKKy..",
], {"a": "#d0702a", "o": "#c05a1c", "O": "#e0782a", "l": "#d8772c", "K": "#1e2440",
    "Y": "#e8c23a", "B": "#34427a", "y": "#ffb040"})

bug("diving_beetle", [
    "..a....a..",
    "...yHHy...",
    "..yKKKKy..",
    ".yKKkkKKy.",
    ".yKkKKkKy.",
    "OyKKKKKKyO",
    ".OyKKKKyO.",
    "O.OyKKyO.O",
    "O..OyyO..O",
], {"a": "#8a7a3a", "y": "#d8b440", "H": "#2e3420", "K": "#232a18", "k": "#3a4526",
    "O": "#b8a468"})

bug("mole_cricket", [
    ".a......a.",
    "S.a.hh.a.S",
    "SS.hhhh.SS",
    ".SSPPPPSS.",
    "...PppP...",
    "..lVVVVl..",
    "...VwwV...",
    ".l.VVVV.l.",
    "...cVVc...",
], {"a": "#5a3c24", "S": "#4e2c14", "h": "#7a5236", "P": "#6e4a2e", "p": "#8a6040",
    "V": "#8a6440", "w": "#4e3520", "l": "#6a4a30", "c": "#5a3a22"})

bug("darkling_beetle", [
    "..a....a..",
    "l..KhhK..l",
    ".l.KKKK.l.",
    "..KkKKkK..",
    "lKkKkdKkKl",
    ".KKkKKkKK.",
    "lKkKkkKkKl",
    ".lKKkkKKl.",
    "l..KKKK..l",
], {"a": "#3a3940", "l": "#2a292e", "K": "#18171b", "h": "#26252a", "k": "#34333a",
    "d": "#bfe8ff"})

# ------------------------------------------------------------------ rare

bug("leaf_insect", [
    "...a..a...",
    "....hh....",
    "..l.tt.l..",
    "l..LMML..l",
    ".LLVMMVLL.",
    "LLVLMMLVLL",
    ".LLLMMLBL.",
    "..LVMMVL..",
    "....MM....",
], {"a": "#6a9a3a", "h": "#80c448", "t": "#72b83e", "l": "#5e9e32", "L": "#7cc243",
    "V": "#64a836", "M": "#b8e070", "B": "#a88a40"})

bug("click_beetle", [
    "..a....a..",
    "...a..a...",
    "....hh....",
    "...PPPP...",
    "..lGPPGl..",
    ".l.EeeE.l.",
    "...EeeE...",
    ".l.EeeE.l.",
    "....EE....",
], {"a": "#5a4030", "h": "#2e2016", "P": "#3e2a1c", "G": "#a8ff5a", "l": "#3a2818",
    "E": "#4a3222", "e": "#34241a"})

bug("sea_skater", [
    "..l....l..",
    "...l..l...",
    "....hh....",
    "LLLsWSsLLL",
    "...SSSS...",
    "...sSSs...",
    "..L.ss.L..",
    ".L......L.",
    "L........L",
], {"l": "#1e242c", "h": "#2a3038", "L": "#1e242c", "S": "#a4aeba", "s": "#4e5866",
    "W": "#f4f8fc"})

bug("mushroom_beetle", [
    "....RWRR..",
    "...RRRRWR.",
    "......s...",
    "...OOKOOK.",
    "aKKOOKOOKO",
    ".KKOOKOOKO",
    "..KKKKKKK.",
    "..l.l..l..",
    ".l..l...l.",
], {"R": "#d42a1e", "W": "#f4efe6", "s": "#ece2cc", "O": "#e8531c", "K": "#141214",
    "a": "#2a262e", "l": "#1e1b20"})

bug("rain_beetle", [
    "FF.F..F.FF",
    ".FFa..aFF.",
    "...hHHh...",
    "..lPpPPl..",
    "..pPPpPp..",
    ".lCcCCcCl.",
    "..CCcCCC..",
    ".lCcCCcCl.",
    "..CCCCCC..",
], {"F": "#d8963c", "a": "#4a2410", "h": "#5a2a10", "H": "#6a3418", "P": "#c8963e",
    "p": "#ecc878", "C": "#7a3c1a", "c": "#9a5028", "l": "#3a1a0a"})

# ------------------------------------------------------------------ epic / legendary

bug("chorus_weevil", [
    "..c.ss.c..",
    "...assa...",
    "....ss....",
    "...lhhl...",
    ".l.PpPP.l.",
    "..PdPPpP..",
    ".lPPpPdPl.",
    "..pPPdPp..",
    "...PPPP...",
], {"p": "#dcc4ec", "P": "#9a74b8", "d": "#5e3f7a", "c": "#c8a8e0", "a": "#6a4a8a",
    "s": "#7a58a0", "h": "#8462a4", "l": "#6e4e92"})

bug("storm_beetle", [
    "....gg....",
    ".v..cc..v.",
    "..a.hh.a..",
    "..PPPPPP..",
    ".lSSSSYYl.",
    "..SSSYYS..",
    ".lSYYYYSl.",
    "..SSYYSS..",
    ".lSYSSSSl.",
], {"g": "#8ef0c8", "c": "#b86a3c", "v": "#5dbf9c", "a": "#1e232c", "h": "#1f2430",
    "P": "#353c4a", "S": "#2a3140", "Y": "#ffe14a", "l": "#1e232c"})

bug("crystal_beetle", [
    "..v....v..",
    "...a..a...",
    "...eDDe...",
    "..PPPPPP..",
    ".lpCgWCpl.",
    "..pCCcCp..",
    ".lpCGCCpl.",
    "..pWCCcp..",
    "...pppp...",
], {"v": "#8ef4ff", "a": "#2e2350", "e": "#c8fbff", "D": "#2a1f4a", "P": "#b07cf4",
    "p": "#9a5cf0", "C": "#5ce0f0", "c": "#8ab8f8", "W": "#ffffff", "g": "#e0a0ff",
    "G": "#3ab8e0", "l": "#2e2350"})


def preview():
    jar = Image.open(ITEM / "bug_jar.png").convert("RGBA")
    over = Image.open(ITEM / "bug_jar_overlay.png").convert("RGBA")
    scale, pad, label = 8, 8, 14
    cell_w, cell_h = 16 * scale * 2 + pad * 2, 16 * scale + label + pad
    cols = 3
    rows = (len(ICONS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w + pad, rows * cell_h + pad), (60, 60, 66, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(ICONS.items()):
        cx, cy = pad + (i % cols) * cell_w, pad + (i // cols) * cell_h
        comp = jar.copy()
        comp.alpha_composite(img)
        comp.alpha_composite(over)
        for k, im in enumerate((img, comp)):
            bg = Image.new("RGBA", (16 * scale, 16 * scale), (130, 130, 138, 255))
            bg.alpha_composite(im.resize((16 * scale, 16 * scale), Image.NEAREST))
            sheet.alpha_composite(bg, (cx + k * (16 * scale + pad), cy))
        d.text((cx, cy + 16 * scale + 2), name, fill=(235, 235, 235, 255))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(PREVIEW)


def main():
    BUGS.mkdir(parents=True, exist_ok=True)
    for name, img in ICONS.items():
        img.save(BUGS / f"{name}.png")
    preview()
    print(f"wrote {len(ICONS)} group C icons; preview at {PREVIEW}")


if __name__ == "__main__":
    main()
