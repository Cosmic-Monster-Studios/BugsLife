"""Generates Bug's Life JSON assets and data: lang, models, blockstates, loot tables, recipes, advancements, tags.

    python tools/gen_resources.py

Everything written here is derived from the BUGS table below, so re-run it after adding or renaming a bug.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "src", "main", "resources")
A = os.path.join(RES, "assets", "bugslife")
D = os.path.join(RES, "data", "bugslife")
M = "bugslife"

# id, name, rarity, product item, habitat text, fact text
BUGS = [
    ("ladybug", "Ladybug", "common", "bugslife:frass",
     "Crops and farmland on sunny days. Also climbs tree trunks.",
     "A ladybug can eat fifty aphids a day. Set a few loose on your farm: they hunt aphids and help crops grow."),
    ("aphid", "Aphid", "common", "bugslife:honeydew",
     "On crops, and on the tops of leaves.",
     "Aphids sip plant sap and drip sweet honeydew. Many are born already carrying the next generation."),
    ("firefly", "Firefly", "common", "bugslife:glow_goo",
     "Over grass on warm nights, especially near water.",
     "Fireflies make cold light. Neighbours flash in unison, just like the synchronous fireflies of the Smoky Mountains."),
    ("cricket", "Cricket", "common", "bugslife:frass",
     "Around villages at night, and now and then in plains grass.",
     "Only males chirp, by rubbing their wings together. Count the chirps in 14 seconds and add 40 to get the temperature in Fahrenheit."),
    ("pill_bug", "Pill Bug", "common", "bugslife:frass",
     "Damp, dim places: moss, podzol, mud and shallow caves.",
     "Not an insect but a land crustacean, closer to a shrimp. Get too close and it rolls into an armoured ball."),
    ("water_strider", "Water Strider", "common", "bugslife:frass",
     "Skating on still fresh water in the daytime.",
     "Water-repelling hairs on its legs let it stand on the surface tension of the water."),
    ("monarch", "Monarch Butterfly", "uncommon", "bugslife:honeydew",
     "Around flowers on sunny days.",
     "Monarchs migrate thousands of miles. Watch one sip nectar and it may spread flowers across the grass nearby."),
    ("silk_moth", "Silk Moth", "uncommon", "bugslife:silk",
     "Among birch and dark oak leaves at dusk and after dark.",
     "Its cocoon is a single silk thread up to a kilometre long. Like every moth, it cannot resist a bright light."),
    ("dragonfly", "Dragonfly", "uncommon", "bugslife:chitin",
     "Darting over rivers, lakes and swamps.",
     "Dragonflies catch nearly every insect they chase, and each of their four wings moves on its own."),
    ("dung_beetle", "Dung Beetle", "uncommon", "bugslife:frass",
     "Wherever cows, sheep, pigs, goats or horses graze.",
     "Dung beetles steer by the Milky Way. They follow grazing animals around and leave rich frass behind."),
    ("cave_weta", "Cave Weta", "uncommon", "bugslife:chitin",
     "Pitch-dark stone caves, deep underground.",
     "Its antennae are many times its body length, for feeling through the dark. It leaps away from loud footsteps."),
    ("walking_stick", "Walking Stick", "rare", "minecraft:stick",
     "Hidden among the leaves of any tree.",
     "It sways like a twig in the wind and freezes the instant it is watched. A frozen stick is an easy catch."),
    ("jewel_beetle", "Jewel Beetle", "rare", "bugslife:chitin",
     "Only on birch trunks, in the daytime.",
     "Its colour comes from microscopic layers in the shell rather than pigment. Its wing cases were once worn as jewellery."),
    ("stag_beetle", "Stag Beetle", "rare", "bugslife:chitin",
     "On oak and dark oak trunks after dark.",
     "Those huge 'antlers' are jaws. Rival males wrestle with them, but they are too big to bite with."),
    ("glowworm", "Glowworm", "rare", "bugslife:glow_goo",
     "Hanging from cave ceilings, most of all in lush and dripstone caves.",
     "Not a worm but a gnat larva. It lowers glowing, sticky silk threads to snare prey in the dark."),
    ("hercules_beetle", "Hercules Beetle", "epic", "bugslife:chitin",
     "On jungle trunks at night, and only in jungles.",
     "One of the largest beetles in the world, and for its size one of the strongest animals alive."),
    ("ember_beetle", "Ember Beetle", "epic", "minecraft:blaze_powder",
     "Scuttling over netherrack, basalt and nylium in the Nether.",
     "Its shell is cracked basalt glowing with inner heat. Fire does not bother it at all."),
    ("sculk_mite", "Sculk Mite", "epic", "minecraft:experience_bottle",
     "Creeping over sculk in the Deep Dark.",
     "It feels every footstep. Walk normally and it burrows away; sneak, and it never knows you were there."),
    ("golden_scarab", "Golden Scarab", "legendary", "minecraft:gold_nugget",
     "On desert sand under the stars.",
     "Ancient peoples saw the rolling sun in the scarab. This one flees any clumsy approach, so sneak up on it."),
    ("void_moth", "Void Moth", "legendary", "minecraft:ender_pearl",
     "Drifting among chorus plants and end rods in the End.",
     "It flickers between places like an enderman. Swing and miss, and it blinks away."),
]

import sys as _sys
_sys.path.insert(0, os.path.dirname(__file__))
from bug_catalog_expansion import NEW_BUGS  # noqa: E402

BUGS = BUGS + NEW_BUGS


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def generated(tex):
    return {"parent": "minecraft:item/generated", "textures": {"layer0": tex}}


# ---------------------------------------------------------------- items
SIMPLE_ITEMS = ["silk", "chitin", "glow_goo", "honeydew", "frass", "cicada_shell", "royal_jelly", "crunchy_grub", "roasted_grub", "bug_skewer",
                "cricket_cookie", "candied_grub", "glow_jelly", "field_guide"]


def item_models():
    for i in SIMPLE_ITEMS:
        write(f"{A}/models/item/{i}.json", generated(f"{M}:item/{i}"))
    for net in ("bug_net", "silk_net"):
        write(f"{A}/models/item/{net}.json", {"parent": "minecraft:item/handheld", "textures": {"layer0": f"{M}:item/{net}"}})
    overrides = []
    for n, b in enumerate(BUGS, start=1):
        bug = b[0]
        write(f"{A}/models/item/bug_jar_{bug}.json", {"parent": "minecraft:item/generated", "textures": {
            "layer0": f"{M}:item/bug_jar", "layer1": f"{M}:item/bugs/{bug}", "layer2": f"{M}:item/bug_jar_overlay"}})
        overrides.append({"predicate": {f"{M}:species": round(n / 100, 2)}, "model": f"{M}:item/bug_jar_{bug}"})
        write(f"{A}/models/item/{bug}_spawn_egg.json", {"parent": "minecraft:item/template_spawn_egg"})
    jar = generated(f"{M}:item/bug_jar")
    jar["overrides"] = overrides
    write(f"{A}/models/item/bug_jar.json", jar)
    write(f"{A}/models/item/terrarium.json", {"parent": f"{M}:block/terrarium"})
    write(f"{A}/models/item/firefly_lantern.json", {"parent": f"{M}:block/firefly_lantern"})


# ---------------------------------------------------------------- blocks
def face(tex, uv=None, cull=None):
    f = {"texture": tex}
    if uv:
        f["uv"] = uv
    if cull:
        f["cullface"] = cull
    return f


def block_models():
    sides = ("north", "south", "east", "west")
    terrarium = {
        "parent": "minecraft:block/block",
        "render_type": "minecraft:translucent",
        "ambientocclusion": False,
        "textures": {"particle": "minecraft:block/glass", "glass": f"{M}:block/terrarium_glass",
                     "lid": f"{M}:block/terrarium_top", "moss": "minecraft:block/moss_block",
                     "soil": "minecraft:block/rooted_dirt", "log": "minecraft:block/oak_log",
                     "stone": "minecraft:block/mossy_cobblestone"},
        "elements": [
            {"from": [1, 0, 1], "to": [15, 2, 15], "faces": {
                "up": face("#moss", [1, 1, 15, 15]), "down": face("#soil", [1, 1, 15, 15], "down"),
                **{s: face("#soil", [1, 14, 15, 16]) for s in sides}}},
            {"from": [3, 2, 7], "to": [13, 3.5, 8.5], "rotation": {"angle": 22.5, "axis": "y", "origin": [8, 2, 8]},
             "faces": {"up": face("#log", [0, 0, 10, 1.5]), **{s: face("#log", [0, 0, 10, 1.5]) for s in sides}}},
            {"from": [10, 2, 10], "to": [13, 4, 13], "faces": {
                "up": face("#stone", [0, 0, 3, 3]), **{s: face("#stone", [0, 0, 3, 2]) for s in sides}}},
            {"from": [0.5, 0, 0.5], "to": [15.5, 15, 15.5], "faces": {
                "up": face("#lid", [0, 0, 16, 16]),
                **{s: face("#glass", [0, 1, 16, 16]) for s in sides}}},
        ],
    }
    write(f"{A}/models/block/terrarium.json", terrarium)
    write(f"{A}/blockstates/terrarium.json", {"variants": {"": {"model": f"{M}:block/terrarium"}}})

    def lantern(y0, hanging):
        els = [
            {"from": [5, y0, 5], "to": [11, y0 + 7, 11], "faces": {
                "down": face("#t", [6, 0, 12, 6]), "up": face("#t", [6, 0, 12, 6]),
                **{s: face("#t", [0, 0, 6, 7]) for s in sides}}},
            {"from": [6, y0 + 7, 6], "to": [10, y0 + 9, 10], "faces": {
                "up": face("#t", [4, 8, 8, 12]), **{s: face("#t", [0, 8, 4, 10]) for s in sides}}},
        ]
        top = 16 if hanging else y0 + 11
        els.append({"from": [8, y0 + 9, 7], "to": [8, top, 9], "rotation": {"angle": 45, "axis": "y", "origin": [8, 8, 8]},
                    "shade": False, "faces": {"east": face("#t", [12, 0, 14, 6]), "west": face("#t", [12, 0, 14, 6])}})
        els.append({"from": [7, y0 + 9, 8], "to": [9, top, 8], "rotation": {"angle": 45, "axis": "y", "origin": [8, 8, 8]},
                    "shade": False, "faces": {"north": face("#t", [12, 0, 14, 6]), "south": face("#t", [12, 0, 14, 6])}})
        return {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "ambientocclusion": False,
                "textures": {"t": f"{M}:block/firefly_lantern", "particle": f"{M}:block/firefly_lantern"}, "elements": els}

    write(f"{A}/models/block/firefly_lantern.json", lantern(0, False))
    write(f"{A}/models/block/firefly_lantern_hanging.json", lantern(1, True))
    write(f"{A}/blockstates/firefly_lantern.json", {"variants": {
        "hanging=false": {"model": f"{M}:block/firefly_lantern"},
        "hanging=true": {"model": f"{M}:block/firefly_lantern_hanging"}}})


# ---------------------------------------------------------------- loot
def self_drop(block):
    return {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{M}:{block}"}],
                                                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]}


def loot():
    write(f"{D}/loot_table/blocks/terrarium.json", self_drop("terrarium"))
    write(f"{D}/loot_table/blocks/firefly_lantern.json", self_drop("firefly_lantern"))
    cook = {"function": "minecraft:furnace_smelt", "conditions": [{"condition": "minecraft:entity_properties", "entity": "this",
                                                                    "predicate": {"flags": {"is_on_fire": True}}}]}
    for bug, name, rarity, product, *_ in BUGS:
        pools = []
        if bug != "aphid":
            pools.append({"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.6}],
                          "entries": [{"type": "minecraft:item", "name": f"{M}:crunchy_grub", "functions": [cook]}]})
        pools.append({"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.5 if bug == "aphid" else 0.25}],
                      "entries": [{"type": "minecraft:item", "name": product}]})
        write(f"{D}/loot_table/entities/{bug}.json", {"type": "minecraft:entity", "pools": pools})


# ---------------------------------------------------------------- recipes
def ing(x):
    return {"tag": x[1:]} if x.startswith("#") else {"item": x}


def shaped(name, pattern, key, result, count=1, cat="misc"):
    write(f"{D}/recipe/{name}.json", {"type": "minecraft:crafting_shaped", "category": cat, "pattern": pattern,
                                        "key": {k: ing(v) for k, v in key.items()}, "result": {"id": result, "count": count}})


def shapeless(name, items, result, count=1, cat="misc"):
    write(f"{D}/recipe/{name}.json", {"type": "minecraft:crafting_shapeless", "category": cat,
                                        "ingredients": [ing(i) for i in items], "result": {"id": result, "count": count}})


def cooking(name, kind, inp, out, xp, time):
    write(f"{D}/recipe/{name}.json", {"type": f"minecraft:{kind}", "category": "food", "ingredient": ing(inp),
                                        "result": {"id": out}, "experience": xp, "cookingtime": time})


def recipes():
    shaped("bug_net", [" SS", " WS", "W  "], {"S": "minecraft:string", "W": "minecraft:stick"}, f"{M}:bug_net", cat="equipment")
    shaped("silk_net", [" SS", " CS", "W  "], {"S": f"{M}:silk", "C": f"{M}:chitin", "W": "minecraft:stick"}, f"{M}:silk_net", cat="equipment")
    shaped("bug_jar", [" P ", "G G", "GGG"], {"P": "#minecraft:planks", "G": "#c:glass_blocks/colorless"}, f"{M}:bug_jar", 4)
    shaped("terrarium", ["GGG", "GJG", "PDP"], {"G": "#c:glass_blocks/colorless", "J": f"{M}:bug_jar", "P": "#minecraft:planks",
                                                "D": "#minecraft:dirt"}, f"{M}:terrarium")
    shaped("firefly_lantern", ["NNN", "NGN", "NNN"], {"N": "minecraft:iron_nugget", "G": f"{M}:glow_goo"}, f"{M}:firefly_lantern")
    shapeless("field_guide", ["minecraft:book", "minecraft:string"], f"{M}:field_guide")
    shapeless("string_from_silk", [f"{M}:silk"], "minecraft:string", 3)
    shapeless("bone_meal_from_chitin", [f"{M}:chitin"], "minecraft:bone_meal", 3)
    shapeless("chitin_from_cicada_shell", [f"{M}:cicada_shell"], f"{M}:chitin", 2)
    shapeless("glowstone_dust_from_glow_goo", [f"{M}:glow_goo", f"{M}:glow_goo"], "minecraft:glowstone_dust", 1)
    shapeless("bug_skewer", ["minecraft:stick", f"{M}:roasted_grub", f"{M}:roasted_grub", f"{M}:roasted_grub"], f"{M}:bug_skewer", cat="misc")
    shaped("cricket_cookie", ["WGW"], {"W": "minecraft:wheat", "G": f"{M}:crunchy_grub"}, f"{M}:cricket_cookie", 6)
    shapeless("candied_grub", [f"{M}:roasted_grub", f"{M}:honeydew", "minecraft:sugar"], f"{M}:candied_grub")
    shapeless("glow_jelly", ["minecraft:bowl", f"{M}:glow_goo", f"{M}:honeydew", "minecraft:sugar"], f"{M}:glow_jelly")
    cooking("roasted_grub", "smelting", f"{M}:crunchy_grub", f"{M}:roasted_grub", 0.35, 200)
    cooking("roasted_grub_smoking", "smoking", f"{M}:crunchy_grub", f"{M}:roasted_grub", 0.35, 100)
    cooking("roasted_grub_campfire", "campfire_cooking", f"{M}:crunchy_grub", f"{M}:roasted_grub", 0.35, 600)


# ---------------------------------------------------------------- advancements
def adv(name, parent, icon, title, desc, criteria, frame="task", hidden=False, requirements=None, toast=True, background=None):
    display = {"icon": {"id": icon}, "title": title, "description": desc, "frame": frame,
               "show_toast": toast, "announce_to_chat": toast, "hidden": hidden}
    if background:
        display["background"] = background
    obj = {"display": display, "criteria": criteria}
    if parent:
        obj["parent"] = f"{M}:{parent}"
    if requirements:
        obj["requirements"] = requirements
    write(f"{D}/advancement/{name}.json", obj)


def catch(**cond):
    return {"trigger": f"{M}:catch_bug", "conditions": cond}


def action(a):
    return {"trigger": f"{M}:bug_action", "conditions": {"action": a}}


def has(item):
    return {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": item}]}}


def eat(item):
    return {"trigger": "minecraft:consume_item", "conditions": {"item": {"items": item}}}


ADV_LANG = {}


def advancements():
    def t(key, title, desc):
        ADV_LANG[f"advancements.{M}.{key}.title"] = title
        ADV_LANG[f"advancements.{M}.{key}.description"] = desc
        return {"translate": f"advancements.{M}.{key}.title"}, {"translate": f"advancements.{M}.{key}.description"}

    ti, de = t("root", "A Bug's Life", "Craft a Bug Net and start exploring the tiny world underfoot")
    adv("root", None, f"{M}:bug_net", ti, de, {"net": has(f"{M}:bug_net"), "guide": has(f"{M}:field_guide"), "caught": catch()},
        requirements=[["net", "guide", "caught"]], toast=False, background="minecraft:textures/block/moss_block.png")
    ti, de = t("field_guide", "Field Notes", "Make a Field Guide to keep track of every bug you find")
    adv("field_guide", "root", f"{M}:field_guide", ti, de, {"guide": has(f"{M}:field_guide")})
    ti, de = t("first_catch", "Gotcha!", "Catch a bug in a jar")
    adv("first_catch", "root", f"{M}:bug_jar", ti, de, {"caught": catch()})
    ti, de = t("naturalist", "Budding Naturalist", "Catch 5 different kinds of bug")
    adv("naturalist", "first_catch", "minecraft:spyglass", ti, de, {"five": action("discover_5")})
    ti, de = t("collector", "Bug Collector", "Catch 10 different kinds of bug")
    adv("collector", "naturalist", f"{M}:field_guide", ti, de, {"ten": action("discover_10")}, frame="goal")
    crit = {b[0]: catch(species=b[0]) for b in BUGS}
    ti, de = t("serious_collector", "Serious Collector", "Catch 25 different kinds of bug")
    adv("serious_collector", "collector", "minecraft:spyglass", ti, de, {"c": action("discover_25")}, frame="goal")
    ti, de = t("master_naturalist", "Master Naturalist", "Catch 50 different kinds of bug")
    adv("master_naturalist", "serious_collector", f"{M}:silk_net", ti, de, {"c": action("discover_50")}, frame="challenge")
    ti, de = t("entomologist", "Entomologist", f"Catch every one of the {len(BUGS)} bugs")
    adv("entomologist", "master_naturalist", f"{M}:silk_net", ti, de, crit, frame="challenge", requirements=[[b[0]] for b in BUGS])
    ti, de = t("rare_find", "Rare Find", "Catch a rare bug")
    adv("rare_find", "first_catch", "minecraft:amethyst_shard", ti, de, {"c": catch(min_rarity="rare")})
    ti, de = t("epic_find", "Epic Encounter", "Catch an epic bug")
    adv("epic_find", "rare_find", "minecraft:echo_shard", ti, de, {"c": catch(min_rarity="epic")}, frame="goal")
    ti, de = t("legendary_find", "Stuff of Legends", "Catch a legendary bug")
    adv("legendary_find", "epic_find", "minecraft:nether_star", ti, de, {"c": catch(min_rarity="legendary")}, frame="challenge")
    ti, de = t("prismatic", "Shimmering Specimen", "Catch a prismatic bug, a one-in-four-hundred rainbow rarity")
    adv("prismatic", "first_catch", "minecraft:prismarine_crystals", ti, de, {"c": catch(prismatic=True)}, frame="challenge", hidden=True)
    ti, de = t("night_lights", "Night Lights", "Catch a firefly")
    adv("night_lights", "first_catch", f"{M}:glow_goo", ti, de, {"c": catch(species="firefly")})
    ti, de = t("lantern", "Lantern Keeper", "Make a Firefly Lantern")
    adv("lantern", "night_lights", f"{M}:firefly_lantern", ti, de, {"c": has(f"{M}:firefly_lantern")})
    ti, de = t("statue_game", "Statue Game", "Catch a Walking Stick while it pretends to be a twig")
    adv("statue_game", "first_catch", "minecraft:stick", ti, de, {"c": catch(species="walking_stick")})
    ti, de = t("hush", "Hush...", "Sneak up on a Sculk Mite and catch it")
    adv("hush", "rare_find", "minecraft:sculk_sensor", ti, de, {"c": catch(species="sculk_mite")}, frame="goal")
    ti, de = t("too_loud", "Too Loud!", "Spook a Sculk Mite with your footsteps")
    adv("too_loud", "first_catch", "minecraft:sculk", ti, de, {"c": action("spook_mite")}, hidden=True)
    ti, de = t("playing_with_fire", "Playing with Fire", "Catch an Ember Beetle in the Nether")
    adv("playing_with_fire", "rare_find", "minecraft:magma_block", ti, de, {"c": catch(species="ember_beetle")})
    ti, de = t("void_moth", "Moth to a Void Flame", "Catch a Void Moth in the End")
    adv("void_moth", "epic_find", "minecraft:end_rod", ti, de, {"c": catch(species="void_moth")}, frame="challenge")
    ti, de = t("golden", "Sun in a Jar", "Catch a Golden Scarab")
    adv("golden", "epic_find", "minecraft:gold_block", ti, de, {"c": catch(species="golden_scarab")}, frame="challenge")
    ti, de = t("silk_road", "The Silk Road", "Make a Silk Net from silk and chitin")
    adv("silk_road", "first_catch", f"{M}:silk_net", ti, de, {"c": has(f"{M}:silk_net")})
    ti, de = t("release", "Born Free", "Let a bug go")
    adv("release", "first_catch", "minecraft:glass_bottle", ti, de, {"c": action("release")})
    ti, de = t("terrarium", "Home Sweet Home", "Put a bug in a Terrarium")
    adv("terrarium", "first_catch", f"{M}:terrarium", ti, de, {"c": action("terrarium_insert")})
    ti, de = t("harvest", "Bug Farmer", "Collect a harvest from a Terrarium")
    adv("harvest", "terrarium", f"{M}:silk", ti, de, {"c": action("terrarium_harvest")})
    ti, de = t("breed", "Circle of Life", "Feed a pair of bugs in a Terrarium and watch a new one hatch")
    adv("breed", "terrarium", "minecraft:turtle_egg", ti, de, {"c": action("terrarium_hatch")}, frame="goal")
    ti, de = t("pest_control", "Pest Control", "Watch a Ladybug eat an Aphid")
    adv("pest_control", "first_catch", "minecraft:wheat", ti, de, {"c": action("witness_hunt")})
    ti, de = t("pollinator", "Flower Power", "Watch a Monarch Butterfly spread flowers")
    adv("pollinator", "first_catch", "minecraft:cornflower", ti, de, {"c": action("witness_pollinate")})
    ti, de = t("acquired_taste", "Acquired Taste", "Eat a bug. Go on.")
    adv("acquired_taste", "root", f"{M}:crunchy_grub", ti, de,
        {"raw": eat(f"{M}:crunchy_grub"), "roasted": eat(f"{M}:roasted_grub")}, requirements=[["raw", "roasted"]])
    ti, de = t("exoskeleton", "Exoskeleton", "Wear a full set of chitin armour - no bug can touch you now")
    adv("exoskeleton", "first_catch", f"{M}:chitin_chestplate", ti, de, {"c": {"trigger": "minecraft:inventory_changed", "conditions": {
        "items": [{"items": f"{M}:chitin_helmet"}, {"items": f"{M}:chitin_chestplate"}, {"items": f"{M}:chitin_leggings"}, {"items": f"{M}:chitin_boots"}]}}},
        frame="goal")
    ti, de = t("shell_shock", "Shell Shock", "Block a blow with a chitin shield and throw it back")
    adv("shell_shock", "exoskeleton", f"{M}:chitin_shield", ti, de, {"c": action("shield_reflect")})
    ti, de = t("itchy", "Itchy!", "Get bitten by a mosquito")
    adv("itchy", "first_catch", "minecraft:redstone", ti, de, {"c": action("bitten")}, hidden=True)
    ti, de = t("eight_legs", "Eight-Legged Friend", "Tame a tarantula with grubs")
    adv("eight_legs", "first_catch", f"{M}:roasted_grub", ti, de, {"c": action("tame_tarantula")}, frame="goal")
    ti, de = t("duet", "Duet", "Play a note block and hear a katydid sing it back")
    adv("duet", "first_catch", "minecraft:note_block", ti, de, {"c": action("katydid_duet")})
    ti, de = t("sweet_tooth", "Sweet Tooth", "Milk a honeypot ant with a glass bottle")
    adv("sweet_tooth", "first_catch", "minecraft:honey_bottle", ti, de, {"c": action("milk_honeypot")})
    ti, de = t("owl_eyes", "Owl Be Watching", "Have an owl butterfly scare off a phantom")
    adv("owl_eyes", "rare_find", "minecraft:phantom_membrane", ti, de, {"c": action("owl_scare")})
    ti, de = t("carpe_diem", "Carpe Diem", "Catch a mayfly before its few minutes are up")
    adv("carpe_diem", "first_catch", "minecraft:clock", ti, de, {"c": catch(species="mayfly")})
    ti, de = t("blue_moon", "Once in a Blue Moon", "Catch a luna moth under the full moon")
    adv("blue_moon", "rare_find", "minecraft:lantern", ti, de, {"c": catch(species="luna_moth")}, frame="goal")
    ti, de = t("now_you_see_me", "Now You See Me", "Catch a leaf insect")
    adv("now_you_see_me", "rare_find", "minecraft:spyglass", ti, de, {"c": catch(species="leaf_insect")})
    ti, de = t("silent_steps", "Silent Steps", "Catch an echo moth in the Deep Dark")
    adv("silent_steps", "epic_find", "minecraft:sculk_shrieker", ti, de, {"c": catch(species="echo_moth")}, frame="goal")
    ti, de = t("bottled_lightning", "Lightning in a Bottle", "Catch a storm beetle in a thunderstorm")
    adv("bottled_lightning", "legendary_find", "minecraft:lightning_rod", ti, de, {"c": catch(species="storm_beetle")}, frame="challenge")
    ti, de = t("long_live", "Long Live the Queen", "Catch a queen ant")
    adv("long_live", "legendary_find", f"{M}:royal_jelly", ti, de, {"c": catch(species="queen_ant")}, frame="challenge")
    ti, de = t("geode", "Geode Jewel", "Catch a crystal beetle")
    adv("geode", "legendary_find", "minecraft:amethyst_cluster", ti, de, {"c": catch(species="crystal_beetle")}, frame="challenge")
    dishes = ["roasted_grub", "bug_skewer", "cricket_cookie", "candied_grub", "glow_jelly", "honeydew", "royal_jelly"]
    ti, de = t("gourmet", "Six-Legged Gourmet", "Eat every bug dish")
    adv("gourmet", "acquired_taste", f"{M}:bug_skewer", ti, de, {d: eat(f"{M}:{d}") for d in dishes},
        frame="challenge", requirements=[[d] for d in dishes])


# ---------------------------------------------------------------- chitin gear and blocks
SHIELD_DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, 90, 0], "translation": [10, 6, -4], "scale": [1, 1, 1]},
    "thirdperson_lefthand": {"rotation": [0, 90, 0], "translation": [10, 6, 12], "scale": [1, 1, 1]},
    "firstperson_righthand": {"rotation": [0, 180, 5], "translation": [-10, 2, -10], "scale": [1.25, 1.25, 1.25]},
    "firstperson_lefthand": {"rotation": [0, 180, 5], "translation": [10, 0, -10], "scale": [1.25, 1.25, 1.25]},
    "gui": {"rotation": [15, -25, -5], "translation": [2, 3, 0], "scale": [0.65, 0.65, 0.65]},
    "fixed": {"rotation": [0, 180, 0], "translation": [-4.5, 4.5, -5], "scale": [0.55, 0.55, 0.55]},
    "ground": {"rotation": [0, 0, 0], "translation": [2, 4, 2], "scale": [0.25, 0.25, 0.25]},
}
SHIELD_BLOCKING_DISPLAY = {
    "thirdperson_righthand": {"rotation": [45, 155, 0], "translation": [-3.49, 11, -2], "scale": [1, 1, 1]},
    "thirdperson_lefthand": {"rotation": [45, 155, 0], "translation": [11.51, 7, 2.5], "scale": [1, 1, 1]},
    "firstperson_righthand": {"rotation": [0, 180, -5], "translation": [-15, 5, -11], "scale": [1.25, 1.25, 1.25]},
    "firstperson_lefthand": {"rotation": [0, 180, -5], "translation": [5, 5, -11], "scale": [1.25, 1.25, 1.25]},
    "gui": {"rotation": [15, -25, -5], "translation": [2, 3, 0], "scale": [0.65, 0.65, 0.65]},
}
ARMOR = ["chitin_helmet", "chitin_chestplate", "chitin_leggings", "chitin_boots"]


def stairs_models(name, tex):
    t = {"bottom": tex, "top": tex, "side": tex}
    write(f"{A}/models/block/{name}.json", {"parent": "minecraft:block/stairs", "textures": t})
    write(f"{A}/models/block/{name}_inner.json", {"parent": "minecraft:block/inner_stairs", "textures": t})
    write(f"{A}/models/block/{name}_outer.json", {"parent": "minecraft:block/outer_stairs", "textures": t})
    variants = {}
    rot = {"east": 0, "south": 90, "west": 180, "north": 270}
    for facing in ("east", "north", "south", "west"):
        for half in ("bottom", "top"):
            for shape in ("inner_left", "inner_right", "outer_left", "outer_right", "straight"):
                model = f"{M}:block/{name}" + ("_inner" if shape.startswith("inner") else "_outer" if shape.startswith("outer") else "")
                y = rot[facing]
                if shape in ("inner_left", "outer_left"):
                    y = (y - 90) % 360
                x = 0
                if half == "top":
                    x = 180
                    if shape in ("inner_left", "outer_left", "inner_right", "outer_right"):
                        y = (y + 90) % 360
                v = {"model": model}
                if x:
                    v["x"] = x
                if y:
                    v["y"] = y
                if x or y:
                    v["uvlock"] = True
                variants[f"facing={facing},half={half},shape={shape}"] = v
    write(f"{A}/blockstates/{name}.json", {"variants": variants})


def slab_models(name, full, tex):
    t = {"bottom": tex, "top": tex, "side": tex}
    write(f"{A}/models/block/{name}.json", {"parent": "minecraft:block/slab", "textures": t})
    write(f"{A}/models/block/{name}_top.json", {"parent": "minecraft:block/slab_top", "textures": t})
    write(f"{A}/blockstates/{name}.json", {"variants": {
        "type=bottom": {"model": f"{M}:block/{name}"},
        "type=top": {"model": f"{M}:block/{name}_top"},
        "type=double": {"model": f"{M}:block/{full}"}}})


def chitin():
    for a in ARMOR:
        write(f"{A}/models/item/{a}.json", generated(f"{M}:item/{a}"))
    shield = {"parent": "builtin/entity", "gui_light": "front", "textures": {"particle": f"{M}:block/chitin_block"},
              "display": SHIELD_DISPLAY, "overrides": [{"predicate": {"blocking": 1}, "model": f"{M}:item/chitin_shield_blocking"}]}
    write(f"{A}/models/item/chitin_shield.json", shield)
    write(f"{A}/models/item/chitin_shield_blocking.json", {"parent": "builtin/entity", "gui_light": "front",
                                                           "textures": {"particle": f"{M}:block/chitin_block"},
                                                           "display": SHIELD_BLOCKING_DISPLAY})
    for b in ("chitin_block", "chitin_tiles", "shell_lamp"):
        write(f"{A}/models/block/{b}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{M}:block/{b}"}})
        write(f"{A}/blockstates/{b}.json", {"variants": {"": {"model": f"{M}:block/{b}"}}})
        write(f"{A}/models/item/{b}.json", {"parent": f"{M}:block/{b}"})
        write(f"{D}/loot_table/blocks/{b}.json", self_drop(b))
    stairs_models("chitin_tile_stairs", f"{M}:block/chitin_tiles")
    write(f"{A}/models/item/chitin_tile_stairs.json", {"parent": f"{M}:block/chitin_tile_stairs"})
    write(f"{D}/loot_table/blocks/chitin_tile_stairs.json", self_drop("chitin_tile_stairs"))
    slab_models("chitin_tile_slab", "chitin_tiles", f"{M}:block/chitin_tiles")
    write(f"{A}/models/item/chitin_tile_slab.json", {"parent": f"{M}:block/chitin_tile_slab"})
    write(f"{D}/loot_table/blocks/chitin_tile_slab.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{
        "type": "minecraft:item", "name": f"{M}:chitin_tile_slab", "functions": [
            {"function": "minecraft:set_count", "count": 2, "conditions": [{"condition": "minecraft:block_state_property",
                                                                            "block": f"{M}:chitin_tile_slab", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]}]}]})
    # reinforced terrarium: same shape as the terrarium, chitin-framed glass
    import copy
    base = json.load(open(f"{A}/models/block/terrarium.json", encoding="utf-8"))
    reinforced = copy.deepcopy(base)
    reinforced["textures"]["glass"] = f"{M}:block/reinforced_terrarium_glass"
    reinforced["textures"]["lid"] = f"{M}:block/reinforced_terrarium_top"
    write(f"{A}/models/block/reinforced_terrarium.json", reinforced)
    write(f"{A}/blockstates/reinforced_terrarium.json", {"variants": {"": {"model": f"{M}:block/reinforced_terrarium"}}})
    write(f"{A}/models/item/reinforced_terrarium.json", {"parent": f"{M}:block/reinforced_terrarium"})
    write(f"{D}/loot_table/blocks/reinforced_terrarium.json", self_drop("reinforced_terrarium"))

    C = f"{M}:chitin"
    shaped("chitin_helmet", ["CCC", "C C"], {"C": C}, f"{M}:chitin_helmet", cat="equipment")
    shaped("chitin_chestplate", ["C C", "CCC", "CCC"], {"C": C}, f"{M}:chitin_chestplate", cat="equipment")
    shaped("chitin_leggings", ["CCC", "C C", "C C"], {"C": C}, f"{M}:chitin_leggings", cat="equipment")
    shaped("chitin_boots", ["C C", "C C"], {"C": C}, f"{M}:chitin_boots", cat="equipment")
    shaped("chitin_shield", ["CIC", "CCC", " C "], {"C": C, "I": "minecraft:iron_ingot"}, f"{M}:chitin_shield", cat="equipment")
    shaped("reinforced_terrarium", [" C ", "CTC", " C "], {"C": C, "T": f"{M}:terrarium"}, f"{M}:reinforced_terrarium")
    shaped("chitin_block", ["CC", "CC"], {"C": C}, f"{M}:chitin_block", cat="building")
    shapeless("chitin_from_block", [f"{M}:chitin_block"], C, 4)
    shaped("chitin_tiles", ["BB", "BB"], {"B": f"{M}:chitin_block"}, f"{M}:chitin_tiles", 4, cat="building")
    shaped("chitin_tile_stairs", ["T  ", "TT ", "TTT"], {"T": f"{M}:chitin_tiles"}, f"{M}:chitin_tile_stairs", 4, cat="building")
    shaped("chitin_tile_slab", ["TTT"], {"T": f"{M}:chitin_tiles"}, f"{M}:chitin_tile_slab", 6, cat="building")
    shaped("shell_lamp", [" C ", "CGC", " C "], {"C": C, "G": f"{M}:glow_goo"}, f"{M}:shell_lamp", cat="building")
    for name, inp, out, n in (("chitin_tiles_stonecutting", "chitin_block", "chitin_tiles", 1),
                              ("chitin_tile_stairs_stonecutting", "chitin_block", "chitin_tile_stairs", 1),
                              ("chitin_tile_slab_stonecutting", "chitin_block", "chitin_tile_slab", 2)):
        write(f"{D}/recipe/{name}.json", {"type": "minecraft:stonecutting", "ingredient": {"item": f"{M}:{inp}"},
                                          "result": {"id": f"{M}:{out}", "count": n}})

    tag = lambda path, values: write(os.path.join(RES, "data", "minecraft", "tags", *path.split("/")) + ".json",
                                     {"replace": False, "values": values})
    tag("block/mineable/pickaxe", [f"{M}:chitin_block", f"{M}:chitin_tiles", f"{M}:chitin_tile_stairs",
                                   f"{M}:chitin_tile_slab", f"{M}:shell_lamp"])
    tag("item/enchantable/head_armor", [f"{M}:chitin_helmet"])
    tag("item/enchantable/chest_armor", [f"{M}:chitin_chestplate"])
    tag("item/enchantable/leg_armor", [f"{M}:chitin_leggings"])
    tag("item/enchantable/foot_armor", [f"{M}:chitin_boots"])
    tag("item/enchantable/armor", [f"{M}:{a}" for a in ARMOR])
    tag("item/enchantable/durability", [f"{M}:bug_net", f"{M}:silk_net", f"{M}:chitin_shield"] + [f"{M}:{a}" for a in ARMOR])
    tag("item/enchantable/equippable", [f"{M}:{a}" for a in ARMOR])


# ---------------------------------------------------------------- tags
def tags():
    pass


# ---------------------------------------------------------------- lang
def lang():
    L = {
        "itemGroup.bugslife": "Bug's Life",
        "item.bugslife.bug_net": "Bug Net",
        "item.bugslife.silk_net": "Silk Net",
        "item.bugslife.bug_jar": "Bug Jar",
        "item.bugslife.bug_jar.filled": "%s in a Jar",
        "item.bugslife.bug_jar.empty_tip": "Carry empty jars when netting bugs.",
        "item.bugslife.bug_jar.filled_tip": "Use on a block to release, or on a Terrarium to keep.",
        "item.bugslife.bug_net.tip": "Use on a bug to catch it. Sneaking improves your odds.",
        "item.bugslife.silk_net.tip": "Far better at catching rare bugs.",
        "item.bugslife.field_guide": "Field Guide",
        "item.bugslife.field_guide.tip": "Every bug, where it lives, and which ones you have caught.",
        "item.bugslife.silk": "Silk",
        "item.bugslife.chitin": "Chitin",
        "item.bugslife.glow_goo": "Glow Goo",
        "item.bugslife.honeydew": "Honeydew",
        "item.bugslife.honeydew.tip": "Sweet and sticky. Soothes poison.",
        "item.bugslife.frass": "Frass",
        "item.bugslife.frass.tip": "Bug droppings make superb fertilizer. Works like bone meal.",
        "item.bugslife.crunchy_grub": "Crunchy Grub",
        "item.bugslife.roasted_grub": "Roasted Grub",
        "item.bugslife.bug_skewer": "Bug Skewer",
        "item.bugslife.cricket_cookie": "Cricket Cookie",
        "item.bugslife.candied_grub": "Candied Grub",
        "item.bugslife.glow_jelly": "Glow Jelly",
        "item.bugslife.cicada_shell": "Cicada Shell",
        "item.bugslife.chitin_helmet": "Chitin Helmet",
        "item.bugslife.chitin_chestplate": "Chitin Chestplate",
        "item.bugslife.chitin_leggings": "Chitin Leggings",
        "item.bugslife.chitin_boots": "Chitin Boots",
        "item.bugslife.chitin_shield": "Chitin Shield",
        "item.bugslife.chitin_shield.tip": "Throws blocked blows back at the attacker. Bugs get it worst.",
        "block.bugslife.reinforced_terrarium": "Reinforced Terrarium",
        "block.bugslife.chitin_block": "Chitin Block",
        "block.bugslife.chitin_tiles": "Chitin Tiles",
        "block.bugslife.chitin_tile_stairs": "Chitin Tile Stairs",
        "block.bugslife.chitin_tile_slab": "Chitin Tile Slab",
        "block.bugslife.shell_lamp": "Shell Lamp",
        "item.bugslife.royal_jelly": "Royal Jelly",
        "bugslife.msg.underground": "It's underground - wait for it to surface.",
        "bugslife.msg.honeypot_empty": "The honeypot ant is still refilling.",
        "bugslife.msg.tarantula_sit": "Your tarantula settles down to wait.",
        "bugslife.msg.tarantula_follow": "Your tarantula scuttles after you.",
        "gui.bugslife.page": "%s/%s",
        "block.bugslife.terrarium": "Terrarium",
        "block.bugslife.terrarium.tip1": "Keeps up to %s bugs, which produce harvests over time.",
        "block.bugslife.terrarium.speed": "Harvests %s%% faster",
        "block.bugslife.terrarium.tip2": "Feed a matching pair their favourite food to breed them.",
        "block.bugslife.terrarium.tip3": "Use with an empty hand to collect. Hoppers work too.",
        "block.bugslife.firefly_lantern": "Firefly Lantern",
        "bugslife.rarity.common": "Common",
        "bugslife.rarity.uncommon": "Uncommon",
        "bugslife.rarity.rare": "Rare",
        "bugslife.rarity.epic": "Epic",
        "bugslife.rarity.legendary": "Legendary",
        "bugslife.prismatic": "✦ Prismatic",
        "bugslife.baby": "Juvenile",
        "bugslife.msg.need_jar": "You need an empty Bug Jar to hold a bug.",
        "bugslife.msg.slipped": "The %s slipped away!",
        "bugslife.msg.caught_rare": "You caught a %2$s! (%1$s)",
        "bugslife.msg.caught_prismatic": "✦ You caught a PRISMATIC %s! ✦",
        "bugslife.msg.new_entry": "New Field Guide entry: %s (%s/%s)",
        "bugslife.msg.mite_burrowed": "The Sculk Mite felt your footsteps and burrowed away...",
        "bugslife.msg.terrarium_full": "This terrarium is full (%s bugs).",
        "bugslife.msg.terrarium_empty": "An empty terrarium. Use a jarred bug on it to move one in.",
        "bugslife.msg.need_pair": "Bugs need a pair of their own kind to breed.",
        "bugslife.msg.already_breeding": "They are already courting.",
        "bugslife.msg.no_room": "There's no room in here for a new bug.",
        "bugslife.msg.courting": "courting (%s)",
        "bugslife.msg.next_harvest": "next harvest in %s",
        "bugslife.msg.prismatic_hatch": "✦ A prismatic %s hatched in your terrarium! ✦",
        "gui.bugslife.field_guide": "Field Guide",
        "gui.bugslife.discovered": "%s/%s found",
        "gui.bugslife.caught": "Caught: %s",
        "gui.bugslife.habitat": "Where to look",
        "gui.bugslife.food": "Favourite food",
        "gui.bugslife.harvest": "Harvest",
        "gui.bugslife.unknown": "Catch one to learn more about it.",
    }
    for bug, name, rarity, product, habitat, fact in BUGS:
        L[f"entity.bugslife.{bug}"] = name
        L[f"item.bugslife.{bug}_spawn_egg"] = f"{name} Spawn Egg"
        L[f"bugslife.guide.{bug}.habitat"] = habitat
        L[f"bugslife.guide.{bug}.fact"] = fact
    L.update(ADV_LANG)
    write(f"{A}/lang/en_us.json", L)


if __name__ == "__main__":
    item_models()
    block_models()
    chitin()
    loot()
    recipes()
    advancements()
    tags()
    lang()
    print("resources generated")
