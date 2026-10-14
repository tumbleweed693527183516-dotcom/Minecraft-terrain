"""
Writes Viking structures into the datapack: .nbt templates, jigsaw template pools,
structures, structure sets (spacing), biome tags and loot tables.
"""
import json

from .designs import all_designs

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
}

# name: (start pool, size, start height, terrain adaptation, spacing, separation, salt)
STRUCTURES = {
    "viking_village": ("village/plaza", 6, -1, "beard_thin", 32, 12, 1946157313),
    "longhouse": ("longhouse/start", 1, -1, "beard_thin", 24, 8, 1946157314),
    "turf_house": ("turf_house/start", 1, -1, "beard_thin", 20, 7, 1946157315),
    "runestone": ("runestone/start", 1, -1, "beard_thin", 10, 4, 1946157316),
    "longship": ("longship/start", 1, -4, "none", 22, 8, 1946157317),
}


def element(location, weight, projection="rigid"):
    return {"weight": weight, "element": {"element_type": "minecraft:single_pool_element",
                                          "location": f"{NS}:{location}", "projection": projection,
                                          "processors": "minecraft:empty"}}


def pools():
    turf = [f"village/turf_house_{s}" for s in ("farmer", "shepherd", "fletcher", "librarian", "cleric", "fisherman")]
    farms = [f"village/farm_{i}" for i in range(3)]
    return {
        "village/plaza": ("minecraft:empty", [element("village/plaza", 1)]),
        "village/streets": (f"{NS}:village/street_ends", [
            element("village/street_13", 4, "terrain_matching"), element("village/street_19", 3, "terrain_matching"),
            element("village/street_junction", 2, "terrain_matching"),
            element("village/street_end", 1, "terrain_matching")]),
        "village/street_ends": ("minecraft:empty", [element("village/street_end", 1, "terrain_matching")]),
        "village/buildings": ("minecraft:empty", [element("village/longhouse", 2), element("village/longhouse_turf", 2),
                                                  element("village/smithy", 2), element("village/sheep_pen", 2),
                                                  element("village/storehouse", 2)]
                              + [element(t, 2) for t in turf] + [element(f, 2) for f in farms]),
        "longhouse/start": ("minecraft:empty", [element("village/longhouse", 1), element("village/longhouse_turf", 1)]),
        "turf_house/start": ("minecraft:empty", [element(t, 1) for t in turf]),
        "runestone/start": ("minecraft:empty", [element("runestone/single", 3), element("runestone/trio", 1),
                                                element("runestone/cairn", 2)]),
        "longship/start": ("minecraft:empty", [element("longship/longship", 1)]),
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
    "ship_cargo": table((3, 6), [
        item("wheat", 6, 4, 12), item("white_wool", 6, 2, 8), item("leather", 6, 2, 6), item("cod", 6, 3, 9),
        item("salmon", 5, 3, 8), item("iron_ingot", 4, 1, 4), item("honeycomb", 3, 1, 4), item("barrel", 2),
        item("lead", 3, 1, 2)]),
}


def write(data_dir, biome_exists):
    out = data_dir / NS
    sizes = {}
    for name, b in all_designs().items():
        sizes[name] = b.save(out / "structures" / f"{name}.nbt")
    for name, (fallback, elements) in pools().items():
        path = out / "worldgen/template_pool" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"fallback": fallback, "elements": elements}, indent=2))
    for name, (pool, size, start_y, adapt, spacing, sep, salt) in STRUCTURES.items():
        _w(out / "worldgen/structure" / f"{name}.json", {
            "type": "minecraft:jigsaw", "biomes": f"#{NS}:has_structure/{name}", "step": "surface_structures",
            "spawn_overrides": {}, "terrain_adaptation": adapt, "start_pool": f"{NS}:{pool}", "size": size,
            "start_height": {"absolute": start_y}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
            "max_distance_from_center": 80, "use_expansion_hack": False})
        _w(out / "worldgen/structure_set" / f"{name}.json", {
            "structures": [{"structure": f"{NS}:{name}", "weight": 1}],
            "placement": {"type": "minecraft:random_spread", "spacing": spacing, "separation": sep, "salt": salt}})
        biomes = [f"{NS}:{b}" for b in STRUCTURE_BIOMES[name] if biome_exists(b)]
        _w(out / "tags/worldgen/biome/has_structure" / f"{name}.json", {"replace": False, "values": biomes})
    for name, t in LOOT.items():
        _w(out / "loot_tables/chests" / f"{name}.json", t)
    return sizes


def _w(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2))
