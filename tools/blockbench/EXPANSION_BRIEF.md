# Modelling brief: Bug's Life 50-bug expansion

You are modelling a batch of new bugs for the Minecraft NeoForge 1.21.1 mod "Bug's Life" at
`C:\Users\messe\OneDrive\Documents\GitHub\BugsLife`. Models are built inside the running Blockbench desktop app through
its MCP plugin (HTTP at localhost:3000/bb-mcp) by our own pipeline; you describe each bug as a Python spec.

## Read first
- `tools/blockbench/expansion_manifest.json` - every new bug: id, group, look, rough size (`px` = model length in
  Blockbench pixels), and the EXACT animation names each bug must have. Only model the bugs whose `group` is yours.
- `tools/blockbench/bugs.py` - the helpers (`P`, `C`, `B`, `legs`, `legs2`, `antennae`, `grid`, `col`, `row`,
  `kf`, `cycle`, `hold`, `tripod_walk`, `flap`, `sway`, `bob`, `hide`, `merge`) and the original 20 specs. Study
  several of them (ladybug, monarch, stag_beetle, glowworm, void_moth) - your bugs must match their style and quality.
- `tools/blockbench/builder.js` - how paint specs become textures. Patterns: solid (default, with noise `n`),
  stripe/vstripe (`per`, `sw`), grad/hgrad, edge, check, spots (`d` density), iri (`j` jitter), wing (translucent
  membrane with veins; `alpha`), monarch. `faces={"up": {...}}` overrides a face; `px=[[x, y, "#rrggbb"(, "glow")]]`
  paints detail pixels (negative x/y count from the far edge); `grid(rows, palette)` turns character art into px.
  Glow: `glow=True` (whole cube into the glowmask), `glow="c2"` (only the pattern's c2 pixels), or px entries
  with a 4th element `"glow"`. `alpha=0.4` makes a cube's pixels translucent (the renderer uses a translucent
  render type for bugs whose manifest entry says `"translucent": true`).
- Preview sheets of the existing bugs: `build/bug_previews/sheet_*.png` (open them to calibrate).

## Conventions (verified)
- Units are pixels; the bug faces north (-Z); feet on y=0. Box UV is automatic - use INTEGER cube sizes.
  Zero thickness on one axis is fine for wings/antennae/thin legs (a plane).
- Rotation signs: +Z lifts the +X side, +X lifts the front (-Z), +Y swings +X toward the front.
  For wings use `flap(left, right, ...)` (+Z lifts the left/+X wing).
- Bone names referenced by animations must exist. Animation names are `animation.<id>.<name>`; the builder adds
  the prefix - you just key `anims` by the manifest's names ("idle", "walk", "fly", "hop", plus specials).
- Loop control: `"loop": False` plays once (hop/strike/etc.), `"loop": "hold"` plays once and holds the last frame
  (curl), default loops. Special actions in the manifest (pinch, dance, strike, spray, sing, buzz, gust, sting,
  click, grab, dig) are one-shot triggered animations: make them 0.3-1.0 s, `"loop": False`. `curl` is hold.
  `fed`, `bask`, `charge` are looping state animations.
- "idle" must look alive (antennae sway, breathing bob, wing twitch). "walk" needs a leg gait (tripod_walk for 6
  legs; write your own alternating gait for 8 legs or many-legged bugs). Flyers need a good "fly" and a perched
  "idle". Hoppers need "hop" (loop False, ~0.5 s).
- Keep total size near the manifest's `px`. Keep texture reasonable (the packer picks 16-128 px sheets).

## Your files (do not edit anything else)
- Specs: `tools/blockbench/bugs_x<GROUP>.py` - start with `from bugs import *` and end with
  `SPECS = {f.__name__: f for f in [...]}` holding exactly your ids (function name == bug id). Add any helper
  functions you need in YOUR file (e.g. an 8-leg gait, a segmented-body chain) - never edit bugs.py/builder.js/
  make_models.py.
- Jar icons: `tools/textures/bug_icons_<group lowercase>.py`, drawing one 16x16 RGBA PNG per bug to
  `src/main/resources/assets/bugslife/textures/item/bugs/<id>.png`. The bug is drawn ONLY inside x=3..12, y=5..13
  (it sits inside `textures/item/bug_jar.png`, under `bug_jar_overlay.png`). Hand-drawn pixel art from palette
  strings, top-down or 3/4 view, readable, matching your model's colours. Look at the existing icons in that folder
  (and `tools/textures/make_textures.py`) for the style. Preview by compositing jar + icon + overlay at 8x.
- Any extra item textures your brief section asks for, into `src/main/resources/assets/bugslife/textures/item/`.

## Building and reviewing
- `python tools/blockbench/make_models.py <id> [<id> ...]` (run from the repo root). It takes a lock so the three
  modelling batches share Blockbench one at a time - it may print "waiting for the Blockbench lock"; that is normal.
  It writes geo/animation/texture/glowmask into src/main/resources, a `.bbmodel` into `blockbench/`, screenshots to
  `build/bug_previews/<id>_*.png` and contact sheets `build/bug_previews/sheet_*.png`. Build several ids per call.
- LOOK at every preview and iterate until each bug is instantly recognisable, charming, and at the quality of the
  original twenty. Typical fixes: wrong rotation sign, legs floating or sunk, wings clipping, a texture reading as
  noise (use `grid`/px detail for patterns that matter).
- Never close or modify Blockbench projects you did not create (the pipeline only closes its own).
- No git commands, no gradle, no Java edits.

## Report back (briefly)
The ids you finished, which ones you are least happy with, and anything the Java side must know (e.g. a bone you
expect code to hide). Keep it short.
