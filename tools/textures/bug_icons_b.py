"""Jar icons for expansion group B, plus the cicada shell item.

Each bug icon is top-down (head up) or front view pixel art, drawn inside the jar interior (x=3..12, y=5..13). Icons
are symmetric: every row gives the LEFT five pixels and is mirrored to ten. '.' is transparent.
Run from anywhere:  python tools/textures/bug_icons_b.py [--preview out.png]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ITEM = ROOT / "src/main/resources/assets/bugslife/textures/item"
BUGS = ITEM / "bugs"
JAR_X0, JAR_Y0, JAR_W, JAR_H = 3, 5, 10, 9


def rgba(v):
    if isinstance(v, tuple):
        return v if len(v) == 4 else v + (255,)
    v = v.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) + ((int(v[6:8], 16),) if len(v) == 8 else (255,))


def sprite(name, rows, pal, w, h):
    assert len(rows) == h, f"{name}: {len(rows)} rows, expected {h}"
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, line in enumerate(rows):
        assert len(line) == w, f"{name}: row {y} has {len(line)} chars: {line!r}"
        for x, ch in enumerate(line):
            if ch != ".":
                assert ch in pal, f"{name}: unknown char {ch!r} at {x},{y}"
                img.putpixel((x, y), rgba(pal[ch]))
    return img


ICONS = {}


def bug(name, half, pal):
    """half: 9 rows of the left 5 pixels; mirrored into a 10x9 sprite and pasted into the jar interior."""
    rows = [r + r[::-1] for r in half]
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    img.paste(sprite(name, rows, pal, JAR_W, JAR_H), (JAR_X0, JAR_Y0))
    ICONS[name] = img


# ---------------------------------------------------------------- flies & co

bug("mayfly", [
    "...a.",
    "....h",
    ".vvvb",
    "vwwvb",
    ".vwwb",
    "..v.s",
    "....b",
    "...t.",
    "..t.T",
], {"a": "#6b5a2a", "h": "#7a6428", "b": "#ecd070", "s": "#b8943c",
    "w": (240, 244, 230, 150), "v": "#a89a5c", "t": "#9a843c", "T": "#c8b068"})

bug("mosquito", [
    ".l..p",
    "..l.h",
    "...lT",
    "LLLwT",
    "...wS",
    "..lws",
    ".l.wS",
    "l...s",
    "....S",
], {"p": "#1c1916", "h": "#3a3f4a", "T": "#2e2a26", "S": "#e8e6e0", "s": "#24201c",
    "l": "#3a3530", "L": "#4a4640", "w": (200, 214, 220, 160)})

bug("cicada", [
    ".l...",
    "..Rgk",
    "l.kgk",
    ".vGkg",
    "lvwGk",
    ".vwGk",
    ".vwwG",
    "..vww",
    "...vv",
], {"R": "#d8321e", "g": "#6aa840", "k": "#1f2a1e", "G": "#3f8a3c", "l": "#2a3522",
    "v": (70, 150, 66, 235), "w": (214, 236, 208, 120)})

bug("katydid", [
    "a....",
    ".a...",
    "..aEG",
    ".l.dM",
    "..ldM",
    "...LM",
    "..DLM",
    ".D.LM",
    "D...d",
], {"a": "#4a7a2e", "E": "#2b3a1c", "G": "#8fdc68", "g": "#5aa83a", "l": "#3f8a2c", "L": "#7ccf56",
    "M": "#c4f09a", "d": "#3a7a26", "D": "#4a9a34"})

bug("locust", [
    ".a...",
    "..a.H",
    "...hH",
    "..lbB",
    ".l.tb",
    "..Ltb",
    ".L.tb",
    "L..Tb",
    "....t",
], {"a": "#8a6a34", "H": "#e2c47a", "h": "#5a4222", "l": "#a8884a", "b": "#c9a55a",
    "B": "#b8944a", "t": "#9a7440", "T": "#6e5028", "L": "#c89a50"})

bug("paper_wasp", [
    ".o...",
    "..o.Y",
    "..o.K",
    "o.wwK",
    ".owwY",
    "..o.k",
    ".o.YY",
    "o..KK",
    "...YK",
], {"o": "#e0842a", "Y": "#f2c21e", "K": "#1c1812", "k": "#3a2c1c", "w": (122, 102, 80, 190)})

# ---------------------------------------------------------------- moths & butterflies

bug("hawk_moth", [
    "..a.p",
    "...aF",
    "GGgdF",
    ".GGgF",
    "..OoF",
    "...of",
    "....f",
    "...WK",
    "..W.K",
], {"a": "#4a3e32", "p": "#3a2e24", "F": "#9a8c78", "G": "#a89c8a", "g": "#8e8272", "d": "#5a4e40",
    "O": "#f4a040", "o": "#d87424", "f": "#6a5c4c", "W": "#f0ece4", "K": "#1c1814"})

bug("sakura_moth", [
    ".a...",
    "..a.W",
    ".qqqW",
    "qpVWf",
    "qWcWf",
    "qpVWf",
    ".qpWf",
    "..Wcf",
    "...q.",
], {"a": "#e0709c", "W": "#fff6fa", "V": "#fcdce8", "q": "#d8729a", "p": "#eea2bc",
    "c": "#d63c78", "f": "#f5c5d5"})

bug("luna_moth", [
    ".y...",
    "..y.w",
    "ppppw",
    "dGGgw",
    "dyegw",
    ".dGgw",
    "..dgw",
    "..d..",
    ".o...",
], {"y": "#c8a040", "w": "#f4f4ea", "p": "#7a3a58", "g": "#98dca8", "G": "#c4f6cc", "d": "#5eae76",
    "e": "#6a2a70", "o": "#e0a840"})

bug("morpho", [
    ".a...",
    "..a.b",
    "WKKKb",
    "KABCb",
    ".KABb",
    "..KKb",
    ".KABb",
    ".KBCb",
    "..KK.",
], {"a": "#2a1c12", "b": "#3a2a1c", "W": "#f4f2ea", "K": "#100d12",
    "A": "#6adcff", "B": "#2a9cff", "C": "#1766e0"})

bug("owl_butterfly", [
    ".a...",
    "..a.b",
    "kkkkb",
    "kTlTb",
    ".klTb",
    ".kYYb",
    "kYEEb",
    "kYEWb",
    ".kYY.",
], {"a": "#2a1c12", "b": "#4a3424", "k": "#2a1a10", "T": "#d4ac78", "l": "#5a3a22",
    "Y": "#f0c040", "E": "#120a06", "W": "#ffffff"})

bug("atlas_moth", [
    "YE...",
    "YYr.a",
    ".rrrf",
    "RrWrf",
    "RWkrf",
    "Rppof",
    ".Rrrf",
    ".Wkrf",
    "..yy.",
], {"Y": "#f2d060", "E": "#140a06", "r": "#a8421e", "R": "#6e2412", "a": "#c89a58",
    "f": "#e0c8a8", "W": "#fff4e6", "k": "#241008", "p": "#f0c4b0", "o": "#c87838", "y": "#dcae52"})

bug("soul_moth", [
    ".a...",
    "..a.e",
    "cSSSf",
    "Csdsf",
    "csssf",
    ".cSsf",
    "..ccf",
    "...C.",
    ".....",
], {"a": "#5a4232", "e": "#8ff8ff", "S": "#664c38", "s": "#4e3a2b", "d": "#2a1c14", "f": "#3a2a1e",
    "c": "#1fb8e6", "C": "#9ef6ff"})

bug("gust_moth", [
    ".a...",
    "..a.h",
    "eeeeR",
    "wsssr",
    "swwsR",
    "swSsr",
    ".sssR",
    "..w.r",
    "....R",
], {"a": "#6a7ac8", "h": "#dfe8f6", "R": "#f2f6fc", "r": "#8a9ce0",
    "e": (120, 200, 216, 220), "w": (216, 244, 242, 110), "s": (60, 170, 196, 240), "S": "#e8ffff"})

bug("echo_moth", [
    ".C...",
    "..t.e",
    ".kckb",
    "ckckb",
    "ckckb",
    ".kckb",
    "..ckb",
    "...kb",
    ".....",
], {"C": "#7ff9ff", "t": "#16545e", "e": "#7ff9ff", "k": "#0b1c22", "c": "#3fe4e8", "b": "#10282e"})

bug("shulker_mite", [
    ".....",
    ".LLLL",
    ".PPPP",
    ".DDDD",
    ".lGEG",
    ".pppp",
    ".PPPP",
    ".DDDD",
    "g.g..",
], {"L": "#c8a0c8", "P": "#9a6b9a", "D": "#6a4570", "l": "#8aa83a", "G": "#d4f06a", "E": "#20301a",
    "p": "#b88fb8", "g": "#8aa83a"})


# ---------------------------------------------------------------- items

CICADA_SHELL = [
    "................",
    "..k..........k..",
    ".kHk.kkkkkk.kHk.",
    ".kak.kHddAk.kak.",
    "..kAkeHddAekAk..",
    "...kkAd..dAkk...",
    "..kHAHd..dAAAk..",
    ".kaHAAd..dAAaAk.",
    "k.kHAAHddAAAak.k",
    "...kHAAAAAAak...",
    "..kkaaaaaaaakk..",
    ".k..kHAAAAak..k.",
    ".....kaaaaak....",
    ".....kHAAak.....",
    "......kaak......",
    ".......kk.......",
]
CICADA_SHELL_PAL = {"k": "#3c220e", "A": (204, 140, 62, 220), "a": (150, 90, 34, 230), "H": (246, 204, 128, 235),
                    "e": "#6a3c16", "d": (110, 62, 20, 235)}


def main():
    BUGS.mkdir(parents=True, exist_ok=True)
    for name, img in ICONS.items():
        img.save(BUGS / f"{name}.png")
    shell = sprite("cicada_shell", CICADA_SHELL, CICADA_SHELL_PAL, 16, 16)
    shell.save(ITEM / "cicada_shell.png")
    print(f"wrote {len(ICONS)} jar icons + cicada_shell.png")
    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        jar = Image.open(ITEM / "bug_jar.png").convert("RGBA")
        over = Image.open(ITEM / "bug_jar_overlay.png").convert("RGBA")
        tiles = []
        for name, img in ICONS.items():
            t = jar.copy()
            t.alpha_composite(img)
            t.alpha_composite(over)
            tiles.append(t)
        tiles.append(shell)
        cols = 6
        sheet = Image.new("RGBA", (cols * 136, ((len(tiles) + cols - 1) // cols) * 136), (90, 90, 90, 255))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize((128, 128), Image.NEAREST), ((i % cols) * 136 + 4, (i // cols) * 136 + 4))
        sheet.save(out)


if __name__ == "__main__":
    main()
