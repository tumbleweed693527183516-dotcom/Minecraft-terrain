"""
Writes Viking structures into the datapack: .nbt templates, jigsaw template pools,
structures, structure sets (spacing), biome tags and loot tables.
"""
import json

from pathlib import Path

from .designs import all_designs
from .viking import catalogue
from .viking2 import DEPTH_MOUND, DEPTH_SHIP, catalogue2
from .warship import WATER as WARSHIP_WATER, catalogue3

CATALOGUE_OUT = Path(__file__).resolve().parents[2] / "src/main/resources/vividlands_villages/catalogue.json"

NS = "vividlands"

# Which of our biomes get which structure
VILLAGE_BIOMES = ["highland_moors", "caledonian_pinewood", "taiga_lakelands", "glacial_outwash", "mossy_lava_fields",
                  "tundra", "basalt_highlands"]
STRUCTURE_BIOMES = {
    "viking_village": VILLAGE_BIOMES,
    "longhouse": VILLAGE_BIOMES + ["mixed_woodland", "autumn_woodland", "alpine_meadow", "black_sand_desert",
                                   "boreal_snowwoods", "endless_steppe"],
    "turf_house": ["glacial_outwash", "mossy_lava_fields", "basalt_highlands", "highland_moors", "black_sand_desert",
                   "tundra", "hot_springs"],
    "runestone": VILLAGE_BIOMES + ["boreal_snowwoods", "mixed_woodland", "autumn_woodland", "alpine_meadow",
                                   "endless_steppe", "wildflower_prairie", "black_sand_desert", "rhyolite_highlands"],
    "longship": ["northern_ocean", "deep_northern_ocean", "temperate_ocean", "deep_temperate_ocean"],
    "burial_mound": VILLAGE_BIOMES + ["alpine_meadow", "endless_steppe", "mixed_woodland", "boreal_snowwoods",
                                      "wildflower_prairie"],
    "ship_burial": ["highland_moors", "glacial_outwash", "endless_steppe", "taiga_lakelands", "tundra",
                    "wildflower_prairie"],
    "stave_church": ["caledonian_pinewood", "taiga_lakelands", "mixed_woodland", "autumn_woodland",
                     "boreal_snowwoods", "alpine_meadow"],
    "mead_hall": ["highland_moors", "endless_steppe", "taiga_lakelands", "alpine_meadow", "mixed_woodland",
                  "glacial_outwash", "wildflower_prairie"],
    "fishing_hamlet": ["snowy_shore", "basalt_shore", "rocky_cliffs", "taiga_lakelands", "golden_beach"],
    "thing_site": ["highland_moors", "endless_steppe", "wildflower_prairie", "glacial_outwash", "mossy_lava_fields"],
    "shieling": ["highland_moors", "alpine_meadow", "highland_crags", "rhyolite_highlands", "basalt_highlands"],
    "beacon_cairn": ["highland_crags", "rocky_cliffs", "highland_moors", "basalt_highlands", "rhyolite_highlands",
                     "alpine_meadow"],
    "knarr": ["northern_ocean", "deep_northern_ocean", "temperate_ocean", "deep_temperate_ocean", "glacial_ocean"],
    "shipwreck": ["northern_ocean", "deep_northern_ocean", "temperate_ocean", "deep_temperate_ocean",
                  "glacial_ocean", "deep_glacial_ocean"],
    "drakkar": ["deep_northern_ocean", "deep_temperate_ocean", "deep_glacial_ocean", "northern_ocean",
                "temperate_ocean"],
    "trelleborg": ["highland_moors", "glacial_outwash", "endless_steppe", "taiga_lakelands", "wildflower_prairie",
                   "tundra", "alpine_meadow"],
    "frozen_longship": ["glacier", "tundra", "snowy_shore", "glacial_outwash"],
}

# Walled villages use the Java structure type vividlands:viking_village (see VikingVillageStructure).
VILLAGE_SPACING = (34, 14, 1946157313)
TRELLEBORG_SPACING = (72, 30, 1946157329)

# name: (start pool, size, start height, terrain adaptation, spacing, separation, salt)
STRUCTURES = {
    "longhouse": ("longhouse/start", 1, -1, "beard_thin", 24, 8, 1946157314),
    "turf_house": ("turf_house/start", 1, -1, "beard_thin", 20, 7, 1946157315),
    "runestone": ("runestone/start", 1, -1, "beard_thin", 18, 7, 1946157316),
    "longship": ("longship/start", 1, -4, "none", 22, 8, 1946157317),
    # batch 2 -- dungeons sink so their template ground level (DEPTH) meets the surface
    "burial_mound": ("burial_mound/start", 1, -(DEPTH_MOUND + 1), "none", 20, 8, 1946157318),
    "ship_burial": ("ship_burial/start", 1, -(DEPTH_SHIP + 1), "none", 40, 16, 1946157319),
    "beacon_cairn": ("beacon_cairn/start", 1, -1, "beard_thin", 24, 8, 1946157325),
    # giant warships: the start height counts from the top water block; hold floor = top water block
    "drakkar": ("drakkar/start", 1, -(WARSHIP_WATER + 1), "none", 44, 18, 1946157330),
    "knarr": ("knarr/start", 1, -4, "none", 28, 10, 1946157326),
    "shipwreck": ("shipwreck/start", 1, -2, "none", 18, 7, 1946157327),
    "frozen_longship": ("frozen_longship/start", 1, -4, "beard_thin", 36, 12, 1946157328),
}
HEIGHTMAP = {"shipwreck": "OCEAN_FLOOR_WG"}

# Big sites keep clear of walled villages (chunks)
EXCLUDE = {"trelleborg": 12, "mead_hall": 8, "stave_church": 7, "thing_site": 8, "fishing_hamlet": 6,
           "ship_burial": 7, "shieling": 5, "longhouse": 5, "turf_house": 5}


def placement(name, spacing, sep, salt):
    p = {"type": "minecraft:random_spread", "spacing": spacing, "separation": sep, "salt": salt}
    if name in EXCLUDE:
        p["exclusion_zone"] = {"other_set": f"{NS}:viking_village", "chunk_count": EXCLUDE[name]}
    return p

# Standalone sites placed by the Java type vividlands:site (dry, level ground; some beside water)
# name: (templates, sink, max slope, min water samples, spacing, separation, salt)
SITES = {
    "stave_church": (["site/stave_church"], 0, 12, 0, 34, 14, 1946157320),
    "mead_hall": (["site/mead_hall"], 0, 12, 0, 32, 16, 1946157321),
    "fishing_hamlet": (["site/fishing_hamlet"], 3, 10, 5, 20, 8, 1946157322),
    "thing_site": (["site/thing_site"], 0, 10, 0, 34, 16, 1946157323),
    "shieling": (["site/shieling"], 0, 14, 0, 18, 6, 1946157324),
}


def element(location, weight, projection="rigid"):
    return {"weight": weight, "element": {"element_type": "minecraft:single_pool_element",
                                          "location": f"{NS}:{location}", "projection": projection,
                                          "processors": "minecraft:empty"}}


def pools():
    longhouses = [n for n in catalogue() if n.startswith("viking/longhouse_")]
    turf = ["viking/farmstead_a", "viking/farmstead_b", "viking/turf_cottage_a", "viking/turf_cottage_b"]
    return {
        "longhouse/start": ("minecraft:empty", [element(n, 1) for n in longhouses]),
        "turf_house/start": ("minecraft:empty", [element(n, 1) for n in turf]),
        "runestone/start": ("minecraft:empty", [element("runestone/single", 3), element("runestone/trio", 1),
                                                element("runestone/cairn", 2)]),
        "longship/start": ("minecraft:empty", [element("longship/longship", 1)]),
        "burial_mound/start": ("minecraft:empty", [element("dungeon/burial_mound", 1), element("dungeon/burial_mound_b", 1)]),
        "ship_burial/start": ("minecraft:empty", [element("dungeon/ship_burial", 1)]),
        "beacon_cairn/start": ("minecraft:empty", [element("site/beacon_cairn", 1)]),
        "knarr/start": ("minecraft:empty", [element("sea/knarr", 1)]),
        "drakkar/start": ("minecraft:empty", [element("sea/sea_king_drakkar", 1), element("sea/war_drakkar", 2)]),
        "shipwreck/start": ("minecraft:empty", [element("sea/shipwreck", 1)]),
        "frozen_longship/start": ("minecraft:empty", [element("sea/frozen_longship", 1)]),
    }


def count(lo, hi):
    return [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]


def item(name, weight, lo=1, hi=1, extra=None):
    e = {"type": "minecraft:item", "name": f"minecraft:{name}", "weight": weight}
    fns = (count(lo, hi) if hi > 1 else []) + (extra or [])
    if fns:
        e["functions"] = fns
    return e


def table(rolls, entries, bonus=None):
    pools = [{"rolls": {"type": "minecraft:uniform", "min": rolls[0], "max": rolls[1]}, "entries": entries}]
    if bonus:
        pools.append(bonus)
    return {"type": "minecraft:chest", "pools": pools}


ENCHANT = [{"function": "minecraft:enchant_randomly"}]

LOOT = {
    "great_hall": table((6, 10), [
        item("gold_ingot", 8, 2, 6), item("emerald", 6, 2, 6), item("diamond", 3, 1, 3), item("iron_ingot", 6, 2, 6),
        item("golden_apple", 3), item("iron_axe", 4, extra=ENCHANT), item("iron_sword", 4, extra=ENCHANT),
        item("shield", 4), item("chainmail_helmet", 2), item("chainmail_chestplate", 2), item("honey_bottle", 5, 1, 3),
        item("cooked_beef", 6, 2, 6), item("bread", 6, 2, 6), item("goat_horn", 1), item("amethyst_shard", 4, 2, 6)],
        bonus={"rolls": 1, "entries": [{"type": "minecraft:empty", "weight": 2}, item("enchanted_book", 2, extra=ENCHANT),
                                       item("diamond_axe", 1, extra=ENCHANT)]}),
    "hof": table((3, 6), [
        item("candle", 8, 1, 4), item("gold_nugget", 8, 3, 10), item("amethyst_shard", 6, 1, 4),
        item("experience_bottle", 4, 1, 4), item("glow_berries", 5, 2, 6), item("bone", 5, 2, 6),
        item("golden_carrot", 3, 1, 3), item("enchanted_book", 2, extra=ENCHANT), item("totem_of_undying", 1)]),
    "longhouse": table((4, 8), [
        item("bread", 10, 1, 4), item("cooked_cod", 8, 2, 6), item("cooked_salmon", 6, 2, 5), item("mutton", 6, 1, 4),
        item("wheat", 6, 3, 9), item("white_wool", 5, 1, 4), item("leather", 6, 1, 4), item("iron_ingot", 5, 1, 4),
        item("gold_nugget", 5, 2, 8), item("emerald", 3, 1, 3), item("iron_axe", 3), item("shield", 3),
        item("leather_helmet", 2), item("bow", 2), item("arrow", 4, 4, 12), item("honey_bottle", 2, 1, 2)],
        bonus={"rolls": 1, "entries": [{"type": "minecraft:empty", "weight": 4},
                                       item("iron_axe", 1, extra=ENCHANT), item("golden_apple", 1)]}),
    "turf_house": table((3, 6), [
        item("bread", 10, 1, 3), item("baked_potato", 8, 2, 5), item("cooked_mutton", 6, 1, 3), item("wheat", 6, 2, 6),
        item("white_wool", 6, 1, 3), item("flint", 5, 1, 3), item("stick", 5, 2, 6), item("candle", 3, 1, 2),
        item("bone_meal", 4, 1, 4), item("emerald", 1), item("string", 4, 1, 4)]),
    "smithy": table((3, 7), [
        item("iron_ingot", 10, 1, 5), item("iron_nugget", 8, 3, 9), item("coal", 8, 2, 7), item("gold_ingot", 3, 1, 3),
        item("iron_axe", 4), item("iron_sword", 3), item("iron_helmet", 2), item("chainmail_chestplate", 1),
        item("shield", 3), item("flint_and_steel", 2), item("bucket", 2), item("diamond", 1)]),
    "storehouse": table((4, 8), [
        item("wheat", 10, 3, 12), item("potato", 8, 2, 8), item("carrot", 8, 2, 8), item("beetroot", 6, 2, 8),
        item("dried_kelp", 6, 3, 10), item("cooked_cod", 6, 2, 6), item("hay_block", 3, 1, 2), item("leather", 4, 1, 3),
        item("map", 2), item("paper", 3, 2, 6), item("emerald", 2, 1, 2)]),
    "longship": table((5, 9), [
        item("gold_ingot", 8, 1, 5), item("gold_nugget", 8, 3, 12), item("emerald", 6, 1, 5), item("iron_axe", 4),
        item("iron_sword", 4), item("shield", 4), item("arrow", 5, 6, 16), item("cooked_cod", 6, 2, 6),
        item("compass", 2), item("spyglass", 2), item("amethyst_shard", 4, 1, 4), item("diamond", 2, 1, 2),
        item("trident", 1)],
        bonus={"rolls": 1, "entries": [{"type": "minecraft:empty", "weight": 3},
                                       item("golden_apple", 2), item("iron_sword", 1, extra=ENCHANT),
                                       item("diamond_axe", 1)]}),
    "burial": table((4, 7), [
        item("bone", 10, 2, 6), item("rotten_flesh", 8, 2, 6), item("gold_nugget", 8, 3, 12), item("gold_ingot", 5, 1, 4),
        item("iron_axe", 4, extra=ENCHANT), item("iron_sword", 3, extra=ENCHANT), item("chainmail_helmet", 3),
        item("amethyst_shard", 5, 1, 5), item("emerald", 4, 1, 4), item("candle", 4, 1, 3), item("goat_horn", 1),
        item("experience_bottle", 3, 1, 4), item("golden_apple", 2), item("name_tag", 2)],
        bonus={"rolls": 1, "entries": [{"type": "minecraft:empty", "weight": 2}, item("enchanted_book", 2, extra=ENCHANT),
                                       item("diamond", 1, 1, 2)]}),
    "ship_burial": table((7, 11), [
        item("gold_ingot", 10, 2, 8), item("gold_block", 2), item("emerald", 8, 2, 8), item("diamond", 4, 1, 4),
        item("golden_apple", 4), item("enchanted_golden_apple", 1), item("diamond_axe", 2, extra=ENCHANT),
        item("iron_sword", 4, extra=ENCHANT), item("golden_helmet", 3, extra=ENCHANT), item("shield", 3),
        item("amethyst_shard", 6, 2, 8), item("experience_bottle", 5, 2, 6), item("totem_of_undying", 1)],
        bonus={"rolls": 2, "entries": [item("enchanted_book", 3, extra=ENCHANT), item("music_disc_otherside", 1),
                                       item("trident", 1)]}),
    "fishing": table((3, 7), [
        item("cod", 10, 2, 8), item("salmon", 8, 2, 6), item("dried_kelp", 8, 3, 10), item("string", 6, 2, 6),
        item("fishing_rod", 4), item("ink_sac", 5, 1, 4), item("nautilus_shell", 1), item("kelp", 5, 2, 6),
        item("lead", 3, 1, 2), item("prismarine_shard", 3, 1, 3), item("emerald", 2, 1, 2)]),
    "shipwreck": table((4, 8), [
        item("gold_nugget", 10, 3, 10), item("gold_ingot", 5, 1, 4), item("iron_ingot", 5, 1, 4), item("emerald", 4, 1, 4),
        item("iron_axe", 3, extra=ENCHANT), item("rotten_flesh", 6, 1, 4), item("prismarine_crystals", 4, 1, 4),
        item("nautilus_shell", 2), item("heart_of_the_sea", 1), item("compass", 3), item("map", 3),
        item("diamond", 1, 1, 2)]),
    "warship": table((4, 8), [
        item("gold_ingot", 8, 2, 6), item("iron_ingot", 8, 2, 8), item("emerald", 6, 2, 6), item("arrow", 6, 8, 24),
        item("iron_axe", 5, extra=ENCHANT), item("iron_sword", 4, extra=ENCHANT), item("shield", 5),
        item("chainmail_chestplate", 3), item("iron_helmet", 3), item("cooked_cod", 6, 2, 8), item("bread", 5, 2, 5),
        item("amethyst_shard", 4, 2, 6), item("diamond", 2, 1, 3), item("trident", 1), item("saddle", 1)],
        bonus={"rolls": 1, "entries": [{"type": "minecraft:empty", "weight": 3}, item("golden_apple", 2),
                                       item("enchanted_book", 2, extra=ENCHANT)]}),
    "warship_captain": table((6, 10), [
        item("gold_ingot", 10, 3, 9), item("gold_block", 3, 1, 2), item("emerald", 8, 3, 10), item("diamond", 5, 1, 4),
        item("diamond_axe", 3, extra=ENCHANT), item("diamond_sword", 2, extra=ENCHANT), item("golden_apple", 4),
        item("enchanted_golden_apple", 1), item("heart_of_the_sea", 2), item("nautilus_shell", 4, 1, 3),
        item("experience_bottle", 6, 2, 8), item("map", 3), item("spyglass", 3), item("totem_of_undying", 1)],
        bonus={"rolls": 2, "entries": [item("enchanted_book", 4, extra=ENCHANT), item("trident", 1, extra=ENCHANT),
                                       item("music_disc_pigstep", 1)]}),
    "guard": table((3, 6), [
        item("arrow", 10, 4, 16), item("bow", 4), item("crossbow", 2), item("iron_axe", 4), item("iron_sword", 3),
        item("shield", 4), item("chainmail_helmet", 3), item("leather_chestplate", 3), item("bread", 6, 1, 3),
        item("cooked_mutton", 5, 1, 3), item("torch", 5, 2, 6), item("goat_horn", 1), item("spyglass", 1)]),
    "farm": table((3, 6), [
        item("wheat_seeds", 10, 2, 8), item("wheat", 8, 2, 6), item("carrot", 6, 1, 4), item("potato", 6, 1, 4),
        item("beetroot_seeds", 5, 1, 6), item("bone_meal", 6, 1, 4), item("iron_hoe", 2), item("shears", 2),
        item("white_wool", 4, 1, 3), item("lead", 2), item("pumpkin_seeds", 2, 1, 3)]),
    "ship_cargo": table((3, 6), [
        item("wheat", 6, 4, 12), item("white_wool", 6, 2, 8), item("leather", 6, 2, 6), item("cod", 6, 3, 9),
        item("salmon", 5, 3, 8), item("iron_ingot", 4, 1, 4), item("honeycomb", 3, 1, 4), item("barrel", 2),
        item("lead", 3, 1, 2)]),
}


# Which default loot each village building's own table draws from
VILLAGE_LOOT = [("great_hall", "great_hall"), ("longhouse", "longhouse"), ("farmstead", "turf_house"),
                ("turf_cottage", "turf_house"), ("forge", "smithy"), ("hof", "hof"), ("gatehouse", "guard"),
                ("watchtower", "guard"), ("training_yard", "guard"), ("field", "farm"), ("sheep_fold", "farm"),
                ("byre", "farm"), ("", "storehouse")]


def ref(name):
    return {"rolls": 1, "entries": [{"type": "minecraft:loot_table", "name": f"{NS}:{name}"}]}


EMPTY = {"type": "minecraft:chest", "pools": []}


def village_table(building):
    base = next(t for key, t in VILLAGE_LOOT if key in building)
    return {"type": "minecraft:chest", "pools": [ref(f"chests/{base}"), ref("chests/extra/village")]}


def write(data_dir, biome_exists):
    out = data_dir / NS
    sizes = {}
    for name, b in all_designs().items():
        if name.startswith(("runestone/", "longship/")):
            sizes[name] = b.save(out / "structures" / f"{name}.nbt")
    cat = []
    role_map = {"wall": None}
    for name, (b, role) in catalogue().items():
        sizes[name] = b.save(out / "structures" / f"{name}.nbt")
        if role == "wall":
            role = "wall_gate" if "gate" in name else "wall_tower"
        cat.append({"id": f"{NS}:{name}", "role": role, "size": list(sizes[name])})
    for name, b in list(catalogue2().items()) + list(catalogue3().items()):
        sizes[name] = b.save(out / "structures" / f"{name}.nbt")
    CATALOGUE_OUT.parent.mkdir(parents=True, exist_ok=True)
    CATALOGUE_OUT.write_text(json.dumps(cat, indent=2))
    # walled village: custom structure type
    _w(out / "worldgen/structure/viking_village.json", {
        "type": f"{NS}:viking_village", "biomes": f"#{NS}:has_structure/viking_village",
        "step": "top_layer_modification", "spawn_overrides": {}, "terrain_adaptation": "none"})
    sp, se, salt = VILLAGE_SPACING
    _w(out / "worldgen/structure_set/viking_village.json", {
        "structures": [{"structure": f"{NS}:viking_village", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": sp, "separation": se, "salt": salt}})
    _w(out / "tags/worldgen/biome/has_structure/viking_village.json",
       {"replace": False, "values": [f"{NS}:{b}" for b in STRUCTURE_BIOMES["viking_village"] if biome_exists(b)]})
    # Trelleborg ring fortress: custom structure type vividlands:trelleborg
    _w(out / "worldgen/structure/trelleborg.json", {
        "type": f"{NS}:trelleborg", "biomes": f"#{NS}:has_structure/trelleborg",
        "step": "top_layer_modification", "spawn_overrides": {}, "terrain_adaptation": "none"})
    sp, se, salt = TRELLEBORG_SPACING
    _w(out / "worldgen/structure_set/trelleborg.json", {
        "structures": [{"structure": f"{NS}:trelleborg", "weight": 1}],
        "placement": placement("trelleborg", sp, se, salt)})
    _w(out / "tags/worldgen/biome/has_structure/trelleborg.json",
       {"replace": False, "values": [f"{NS}:{b}" for b in STRUCTURE_BIOMES["trelleborg"] if biome_exists(b)]})
    for name, (templates, sink, slope, water, spacing, sep, salt) in SITES.items():
        _w(out / "worldgen/structure" / f"{name}.json", {
            "type": f"{NS}:site", "biomes": f"#{NS}:has_structure/{name}", "step": "surface_structures",
            "spawn_overrides": {}, "terrain_adaptation": "beard_thin",
            "templates": [f"{NS}:{t}" for t in templates], "sink": sink, "max_slope": slope, "min_water": water})
        _w(out / "worldgen/structure_set" / f"{name}.json", {
            "structures": [{"structure": f"{NS}:{name}", "weight": 1}],
            "placement": placement(name, spacing, sep, salt)})
        _w(out / "tags/worldgen/biome/has_structure" / f"{name}.json",
           {"replace": False, "values": [f"{NS}:{b}" for b in STRUCTURE_BIOMES[name] if biome_exists(b)]})
    for name, (fallback, elements) in pools().items():
        path = out / "worldgen/template_pool" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"fallback": fallback, "elements": elements}, indent=2))
    for name, (pool, size, start_y, adapt, spacing, sep, salt) in STRUCTURES.items():
        _w(out / "worldgen/structure" / f"{name}.json", {
            "type": "minecraft:jigsaw", "biomes": f"#{NS}:has_structure/{name}", "step": "surface_structures",
            "spawn_overrides": {}, "terrain_adaptation": adapt, "start_pool": f"{NS}:{pool}", "size": size,
            "start_height": {"absolute": start_y}, "project_start_to_heightmap": HEIGHTMAP.get(name, "WORLD_SURFACE_WG"),
            "max_distance_from_center": 80, "use_expansion_hack": False})
        _w(out / "worldgen/structure_set" / f"{name}.json", {
            "structures": [{"structure": f"{NS}:{name}", "weight": 1}],
            "placement": placement(name, spacing, sep, salt)})
        biomes = [f"{NS}:{b}" for b in STRUCTURE_BIOMES[name] if biome_exists(b)]
        _w(out / "tags/worldgen/biome/has_structure" / f"{name}.json", {"replace": False, "values": biomes})
    for name, t in LOOT.items():
        t = dict(t, pools=t["pools"] + [ref("chests/extra/everywhere")])
        _w(out / "loot_tables/chests" / f"{name}.json", t)
    # every village building has its own table (default contents + the shared village extra)
    for name in catalogue():
        short = name.split("/")[-1]
        _w(out / "loot_tables/chests/village" / f"{short}.json", village_table(short))
    # empty hook tables: override these in a datapack to add your own loot everywhere at once
    for hook in ("village", "everywhere"):
        _w(out / "loot_tables/chests/extra" / f"{hook}.json", EMPTY)
    return sizes


def _w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))
