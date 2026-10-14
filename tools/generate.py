#!/usr/bin/env python3
"""
Vivid Lands world generation data generator (Minecraft 1.20.1).

Everything in src/main/resources/data is produced by this script, so edit
values here and re-run it rather than editing the JSON by hand.

    python3 tools/generate.py
"""
import json
import shutil
from pathlib import Path

MODID = "vividlands"
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src" / "main" / "resources"
DATA = RES / "data"

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
MIN_Y = -64
HEIGHT = 512                 # world goes from y=-64 to y=447
SEA_LEVEL = 63
VERTICAL_SCALE = 1.75        # how much taller land above sea level gets vs vanilla
SMOOTHING = 1.3              # >1 = smoother slopes, fewer overhangs and floating bits
DETAIL_NOISE = 0.7           # strength of small-scale 3D terrain noise (vanilla = 1.0)
RIDGE_STRENGTH = 0.30        # how strongly inland terrain forms ridges and valleys
RIDGE_LIFT = 0.12            # keeps ridge valleys above sea level
TOP_SLIDE = (424, 440)       # terrain fades out between these heights


def mc(x):
    return f"minecraft:{x}"


def vl(x):
    return f"{MODID}:{x}"


def write(path, obj):
    p = DATA / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


def state(name, **props):
    s = {"Name": name if ":" in name else mc(name)}
    if props:
        s["Properties"] = {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in props.items()}
    return s


def simple(name, **props):
    return {"type": mc("simple_state_provider"), "state": state(name, **props)}


def weighted(*entries):
    return {"type": mc("weighted_state_provider"),
            "entries": [{"weight": w, "data": s} for w, s in entries]}


def uniform(a, b):
    return {"type": mc("uniform"), "value": {"min_inclusive": a, "max_inclusive": b}}


def add(a, b):
    return {"type": mc("add"), "argument1": a, "argument2": b}


def mul(a, b):
    return {"type": mc("mul"), "argument1": a, "argument2": b}


def clamp(x, lo, hi):
    return {"type": mc("clamp"), "input": x, "min": lo, "max": hi}


def abs_(x):
    return {"type": mc("abs"), "argument": x}


# ---------------------------------------------------------------------------
# Dimension type: taller world
# ---------------------------------------------------------------------------
def dimension_type():
    write("minecraft/dimension_type/overworld.json", {
        "ultrawarm": False, "natural": True, "coordinate_scale": 1.0, "has_skylight": True,
        "has_ceiling": False, "ambient_light": 0.0, "monster_spawn_light_level": uniform(0, 7),
        "monster_spawn_block_light_limit": 0, "piglin_safe": False, "bed_works": True,
        "respawn_anchor_works": False, "has_raids": True, "logical_height": HEIGHT, "min_y": MIN_Y,
        "height": HEIGHT, "infiniburn": "#minecraft:infiniburn_overworld", "effects": mc("overworld"),
    })


# ---------------------------------------------------------------------------
# Density functions
# ---------------------------------------------------------------------------
def density_functions():
    top = MIN_Y + HEIGHT
    above = -(top - 64) / (128 * VERTICAL_SCALE)
    gradient = add({"type": mc("y_clamped_gradient"), "from_y": MIN_Y, "to_y": 64,
                    "from_value": 1.5, "to_value": 0.5},
                   {"type": mc("y_clamped_gradient"), "from_y": 64, "to_y": top,
                    "from_value": 0.0, "to_value": above})

    # Peaks & valleys: 1 on ridge crests, -1 in valley floors (vanilla "ridges_folded" maths).
    peaks_valleys = mul(-3.0, add(-0.3333333333333333,
                                  abs_(add(-0.6666666666666666, abs_(mc("overworld/ridges"))))))
    inland = clamp(mul(2.5, add(mc("overworld_large_biomes/continents"), -0.05)), 0.0, 1.0)
    rugged = clamp(mul(-1.5, add(mc("overworld_large_biomes/erosion"), -0.25)), 0.0, 1.0)
    ridge_term = mul(mul(inland, rugged), add(RIDGE_LIFT, mul(RIDGE_STRENGTH, peaks_valleys)))
    write(f"{MODID}/worldgen/density_function/overworld/offset.json", {
        "type": mc("flat_cache"), "argument": {"type": mc("cache_2d"), "argument":
                                               add(mc("overworld_large_biomes/offset"), ridge_term)}})
    write(f"{MODID}/worldgen/density_function/overworld/depth.json", add(gradient, vl("overworld/offset")))
    write(f"{MODID}/worldgen/density_function/overworld/factor.json",
          mul(VERTICAL_SCALE * SMOOTHING, mc("overworld_large_biomes/factor")))
    write(f"{MODID}/worldgen/density_function/overworld/base_3d_noise.json",
          mul(DETAIL_NOISE, {"type": mc("old_blended_noise"), "xz_scale": 0.25, "y_scale": 0.125,
                             "xz_factor": 120.0, "y_factor": 200.0, "smear_scale_multiplier": 8.0}))
    write(f"{MODID}/worldgen/density_function/overworld/sloped_cheese.json", add(
        mul(4.0, {"type": mc("quarter_negative"), "argument": mul(
            add(vl("overworld/depth"),
                mul(mc("overworld_large_biomes/jaggedness"),
                    {"type": mc("half_negative"), "argument": {"type": mc("noise"), "noise": mc("jagged"),
                                                              "xz_scale": 1500.0, "y_scale": 0.0}})),
            vl("overworld/factor"))}),
        vl("overworld/base_3d_noise")))
    # Caves kept as a separate, swappable piece (vanilla cave system).
    write(f"{MODID}/worldgen/density_function/overworld/caves.json", {
        "type": mc("max"),
        "argument1": {"type": mc("min"), "argument1": {"type": mc("min"), "argument1": add(
            mul(4.0, {"type": mc("square"), "argument": {"type": mc("noise"), "noise": mc("cave_layer"),
                                                         "xz_scale": 1.0, "y_scale": 8.0}}),
            add(clamp(add(0.27, {"type": mc("noise"), "noise": mc("cave_cheese"), "xz_scale": 1.0,
                                 "y_scale": 0.6666666666666666}), -1.0, 1.0),
                clamp(add(1.5, mul(-0.64, vl("overworld/sloped_cheese"))), 0.0, 0.5))),
            "argument2": mc("overworld/caves/entrances")},
            "argument2": add(mc("overworld/caves/spaghetti_2d"), mc("overworld/caves/spaghetti_roughness_function"))},
        "argument2": {"type": mc("range_choice"), "input": mc("overworld/caves/pillars"),
                      "min_inclusive": -1000000.0, "max_exclusive": 0.03, "when_in_range": -1000000.0,
                      "when_out_of_range": mc("overworld/caves/pillars")},
    })


def slides(inner):
    return add(0.1171875, mul(
        {"type": mc("y_clamped_gradient"), "from_y": MIN_Y, "to_y": MIN_Y + 24, "from_value": 0.0, "to_value": 1.0},
        add(-0.1171875, add(-0.078125, mul(
            {"type": mc("y_clamped_gradient"), "from_y": TOP_SLIDE[0], "to_y": TOP_SLIDE[1],
             "from_value": 1.0, "to_value": 0.0},
            add(0.078125, inner))))))


def ore_vein(noise):
    return abs_({"type": mc("interpolated"), "argument": {
        "type": mc("range_choice"), "input": mc("y"), "min_inclusive": -60.0, "max_exclusive": 51.0,
        "when_in_range": {"type": mc("noise"), "noise": mc(noise), "xz_scale": 4.0, "y_scale": 4.0},
        "when_out_of_range": 0.0}})


def climate(noise):
    return {"type": mc("shifted_noise"), "noise": mc(noise), "xz_scale": 0.25, "y_scale": 0.0,
            "shift_x": mc("shift_x"), "shift_y": 0.0, "shift_z": mc("shift_z")}


def noise_settings():
    sloped = vl("overworld/sloped_cheese")
    terrain = {"type": mc("range_choice"), "input": sloped, "min_inclusive": -1000000.0, "max_exclusive": 1.5625,
               "when_in_range": {"type": mc("min"), "argument1": sloped,
                                 "argument2": mul(5.0, mc("overworld/caves/entrances"))},
               "when_out_of_range": vl("overworld/caves")}
    final_density = {"type": mc("min"),
                     "argument1": {"type": mc("squeeze"), "argument": mul(0.64, {
                         "type": mc("interpolated"), "argument": {"type": mc("blend_density"),
                                                                  "argument": slides(terrain)}})},
                     "argument2": mc("overworld/caves/noodle")}
    initial = slides(clamp(add(-0.703125, mul(4.0, {"type": mc("quarter_negative"), "argument": mul(
        vl("overworld/depth"), {"type": mc("cache_2d"), "argument": vl("overworld/factor")})})), -64.0, 64.0))
    router = {
        "barrier": {"type": mc("noise"), "noise": mc("aquifer_barrier"), "xz_scale": 1.0, "y_scale": 0.5},
        "fluid_level_floodedness": {"type": mc("noise"), "noise": mc("aquifer_fluid_level_floodedness"),
                                    "xz_scale": 1.0, "y_scale": 0.67},
        "fluid_level_spread": {"type": mc("noise"), "noise": mc("aquifer_fluid_level_spread"),
                               "xz_scale": 1.0, "y_scale": 0.7142857142857143},
        "lava": {"type": mc("noise"), "noise": mc("aquifer_lava"), "xz_scale": 1.0, "y_scale": 1.0},
        "temperature": climate("temperature_large"),
        "vegetation": climate("vegetation_large"),
        "continents": mc("overworld_large_biomes/continents"),
        "erosion": mc("overworld_large_biomes/erosion"),
        "depth": vl("overworld/depth"),
        "ridges": mc("overworld/ridges"),
        "initial_density_without_jaggedness": initial,
        "final_density": final_density,
        "vein_toggle": {"type": mc("interpolated"), "argument": {
            "type": mc("range_choice"), "input": mc("y"), "min_inclusive": -60.0, "max_exclusive": 51.0,
            "when_in_range": {"type": mc("noise"), "noise": mc("ore_veininess"), "xz_scale": 1.5, "y_scale": 1.5},
            "when_out_of_range": 0.0}},
        "vein_ridged": add(-0.07999999821186066, {"type": mc("max"), "argument1": ore_vein("ore_vein_a"),
                                                  "argument2": ore_vein("ore_vein_b")}),
        "vein_gap": {"type": mc("noise"), "noise": mc("ore_gap"), "xz_scale": 1.0, "y_scale": 1.0},
    }
    spawn = {"temperature": [-1.0, 1.0], "humidity": [-1.0, 1.0], "continentalness": [-0.11, 1.0],
             "erosion": [-1.0, 1.0], "depth": 0.0, "offset": 0.0}
    write(f"{MODID}/worldgen/noise_settings/overworld.json", {
        "sea_level": SEA_LEVEL, "disable_mob_generation": False, "aquifers_enabled": True,
        "ore_veins_enabled": True, "legacy_random_source": False,
        "default_block": state("stone"), "default_fluid": state("water", level=0),
        "noise": {"min_y": MIN_Y, "height": HEIGHT, "size_horizontal": 1, "size_vertical": 2},
        "noise_router": router,
        "spawn_target": [dict(spawn, weirdness=[-1.0, -0.16]), dict(spawn, weirdness=[0.16, 1.0])],
        "surface_rule": surface_rule(),
    })


# ---------------------------------------------------------------------------
# Surface rule building blocks
# ---------------------------------------------------------------------------
def block(name, **props):
    return {"type": mc("block"), "result_state": state(name, **props)}


def seq(*rules):
    return {"type": mc("sequence"), "sequence": list(rules)}


def cond(c, rule):
    return {"type": mc("condition"), "if_true": c, "then_run": rule}


def biome_is(*names):
    return {"type": mc("biome"), "biome_is": list(names)}


BIG = 1.7976931348623157e308


def noise(n, lo, hi=BIG):
    return {"type": mc("noise_threshold"), "noise": mc(n), "min_threshold": lo, "max_threshold": hi}


def y_above(y):
    return {"type": mc("y_above"), "anchor": {"absolute": y}, "surface_depth_multiplier": 0,
            "add_stone_depth": False}


def not_(c):
    return {"type": mc("not"), "invert": c}


STEEP = {"type": mc("steep")}
BANDS = {"type": mc("bandlands")}
ON_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": False,
            "secondary_depth_range": 0}
UNDER_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": True,
               "secondary_depth_range": 0}
DEEP_UNDER_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": True,
                    "secondary_depth_range": 6}
ON_CEILING = {"type": mc("stone_depth"), "offset": 0, "surface_type": "ceiling", "add_surface_depth": False,
              "secondary_depth_range": 0}
ABOVE_WATER = {"type": mc("water"), "offset": -1, "surface_depth_multiplier": 0, "add_stone_depth": False}

GRASS = block("grass_block", snowy=False)
PODZOL = block("podzol", snowy=False)
DIRT = block("dirt")
SAND = block("sand")
GRAVEL = block("gravel")
STONE = block("stone")


def patches(*pairs, default):
    """Noise-driven patches: pairs of (min_surface_noise, rule), checked in order."""
    return seq(*[cond(noise("surface", lo), r) for lo, r in pairs], default)


def snowcap(y, rest, steep=STONE):
    return seq(cond(STEEP, steep), cond(y_above(y), block("snow_block")), rest)


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
ORDER = []   # global order of our placed features (prevents feature-order crashes)


def configured(name, ftype, config):
    write(f"{MODID}/worldgen/configured_feature/{name}.json", {"type": mc(ftype), "config": config})


def placed(name, feature, placement):
    ORDER.append(name)
    write(f"{MODID}/worldgen/placed_feature/{name}.json", {"feature": vl(feature), "placement": placement})


def count(n):
    return {"type": mc("count"), "count": n}


def rarity(n):
    return {"type": mc("rarity_filter"), "chance": n}


IN_SQUARE = {"type": mc("in_square")}
BIOME = {"type": mc("biome")}
AIR_ONLY = {"type": mc("matching_blocks"), "blocks": mc("air")}
WATER_ONLY = {"type": mc("matching_blocks"), "blocks": mc("water")}


def heightmap(h):
    return {"type": mc("heightmap"), "heightmap": h}


def surface(*mods, hm="MOTION_BLOCKING"):
    return list(mods) + [IN_SQUARE, heightmap(hm), BIOME]


def survives(name, **props):
    return {"type": mc("would_survive"), "state": state(name, **props)}


def tree_at(n, predicate, chance=None):
    mods = [rarity(chance)] if chance else [count(n)]
    return mods + [IN_SQUARE, {"type": mc("surface_water_depth_filter"), "max_water_depth": 0},
                   heightmap("OCEAN_FLOOR"), {"type": mc("block_predicate_filter"), "predicate": predicate},
                   BIOME]


def patch(name, provider, tries=48, xz=7, y=3, needs=None):
    filt = [{"type": mc("block_predicate_filter"), "predicate": AIR_ONLY}]
    if needs:
        filt.append({"type": mc("block_predicate_filter"), "predicate": needs})
    configured(name, "random_patch", {
        "tries": tries, "xz_spread": xz, "y_spread": y,
        "feature": {"feature": {"type": mc("simple_block"), "config": {"to_place": provider}}, "placement": filt}})


def column_patch(name, provider, lo, hi, tries=16, xz=4, needs=None):
    filt = [{"type": mc("block_predicate_filter"), "predicate": AIR_ONLY}]
    if needs:
        filt.append({"type": mc("block_predicate_filter"), "predicate": needs})
    configured(name, "random_patch", {
        "tries": tries, "xz_spread": xz, "y_spread": 2,
        "feature": {"feature": {"type": mc("block_column"), "config": {
            "direction": "up", "allowed_placement": AIR_ONLY, "prioritize_tip": False,
            "layers": [{"height": uniform(lo, hi), "provider": provider}]}}, "placement": filt}})


def tree(name, log, leaves, trunk, foliage, size, dirt="dirt", decorators=()):
    configured(name, "tree", {
        "ignore_vines": True, "force_dirt": False, "minimum_size": size,
        "dirt_provider": simple(dirt), "trunk_provider": simple(log, axis="y"),
        "foliage_provider": simple(leaves, distance=7, persistent=False, waterlogged=False),
        "trunk_placer": trunk, "foliage_placer": foliage, "decorators": list(decorators)})


def straight(base, a, b=0):
    return {"type": mc("straight_trunk_placer"), "base_height": base, "height_rand_a": a, "height_rand_b": b}


def blob(r, h=3, off=0):
    return {"type": mc("blob_foliage_placer"), "radius": r, "offset": off, "height": h}


TWO_LAYERS = {"type": mc("two_layers_feature_size"), "limit": 1, "lower_size": 0, "upper_size": 1}
GIANT_SIZE = {"type": mc("two_layers_feature_size"), "limit": 1, "lower_size": 1, "upper_size": 2}
VINES = [{"type": mc("trunk_vine")}, {"type": mc("leave_vine"), "probability": 0.25}]


def flowers(*names):
    return weighted(*[(1, state(n)) for n in names])


def features():
    oak_ok = survives("oak_sapling", stage=0)
    spruce_ok = survives("spruce_sapling", stage=0)
    jungle_ok = survives("jungle_sapling", stage=0)
    acacia_ok = survives("acacia_sapling", stage=0)
    birch_ok = survives("birch_sapling", stage=0)
    sand_or_grass = {"type": mc("matching_blocks"), "offset": [0, -1, 0], "blocks": [mc("sand"), mc("grass_block")]}

    # ---- trees ----
    tree("oak", "oak_log", "oak_leaves", straight(4, 2), blob(2), TWO_LAYERS)
    tree("broad_oak", "oak_log", "oak_leaves",
         {"type": mc("fancy_trunk_placer"), "base_height": 4, "height_rand_a": 11, "height_rand_b": 0},
         {"type": mc("fancy_foliage_placer"), "radius": 2, "offset": 4, "height": 4},
         {"type": mc("two_layers_feature_size"), "limit": 0, "lower_size": 0, "upper_size": 0,
          "min_clipped_height": 4})
    tree("ancient_oak", "oak_log", "oak_leaves",
         {"type": mc("mega_jungle_trunk_placer"), "base_height": 16, "height_rand_a": 6, "height_rand_b": 6},
         {"type": mc("jungle_foliage_placer"), "radius": 2, "offset": 0, "height": 2}, GIANT_SIZE)
    tree("swamp_oak", "oak_log", "oak_leaves", straight(5, 3), blob(3), TWO_LAYERS,
         decorators=[{"type": mc("leave_vine"), "probability": 0.25}])
    tree("birch", "birch_log", "birch_leaves", straight(5, 2), blob(2), TWO_LAYERS)
    tree("tall_birch", "birch_log", "birch_leaves", straight(8, 4), blob(2), TWO_LAYERS)
    tree("spruce", "spruce_log", "spruce_leaves", straight(6, 3),
         {"type": mc("spruce_foliage_placer"), "radius": uniform(2, 3), "offset": uniform(0, 2),
          "trunk_height": uniform(1, 2)}, {"type": mc("two_layers_feature_size"), "limit": 2,
                                           "lower_size": 0, "upper_size": 2})
    tree("pine", "spruce_log", "spruce_leaves", straight(7, 4),
         {"type": mc("pine_foliage_placer"), "radius": 1, "offset": 1, "height": uniform(3, 4)},
         {"type": mc("two_layers_feature_size"), "limit": 2, "lower_size": 0, "upper_size": 2})
    tree("highland_pine", "spruce_log", "spruce_leaves", straight(9, 4), blob(2), TWO_LAYERS)
    tree("redwood", "spruce_log", "spruce_leaves",
         {"type": mc("giant_trunk_placer"), "base_height": 26, "height_rand_a": 10, "height_rand_b": 8},
         {"type": mc("mega_pine_foliage_placer"), "radius": 0, "offset": 0, "crown_height": uniform(13, 17)},
         GIANT_SIZE, decorators=[{"type": mc("alter_ground"), "provider": simple("podzol", snowy=False)}])
    tree("acacia", "acacia_log", "acacia_leaves",
         {"type": mc("forking_trunk_placer"), "base_height": 5, "height_rand_a": 2, "height_rand_b": 2},
         {"type": mc("acacia_foliage_placer"), "radius": 2, "offset": 0}, TWO_LAYERS)
    tree("jungle_tree", "jungle_log", "jungle_leaves", straight(4, 8), blob(2), TWO_LAYERS,
         decorators=[{"type": mc("cocoa"), "probability": 0.2}] + VINES)
    tree("giant_jungle_tree", "jungle_log", "jungle_leaves",
         {"type": mc("mega_jungle_trunk_placer"), "base_height": 10, "height_rand_a": 2, "height_rand_b": 19},
         {"type": mc("jungle_foliage_placer"), "radius": 2, "offset": 0, "height": 2}, GIANT_SIZE,
         decorators=VINES)
    tree("palm", "jungle_log", "jungle_leaves",
         {"type": mc("bending_trunk_placer"), "base_height": 6, "height_rand_a": 3, "height_rand_b": 0,
          "min_height_for_leaves": 3, "bend_length": uniform(1, 2)},
         {"type": mc("acacia_foliage_placer"), "radius": 3, "offset": 0}, TWO_LAYERS, dirt="sand")
    tree("bush", "oak_log", "oak_leaves", straight(1, 0),
         {"type": mc("bush_foliage_placer"), "radius": 2, "offset": 1, "height": 2},
         {"type": mc("two_layers_feature_size"), "limit": 0, "lower_size": 0, "upper_size": 0})
    tree("jungle_bush", "jungle_log", "oak_leaves", straight(1, 0),
         {"type": mc("bush_foliage_placer"), "radius": 2, "offset": 1, "height": 2},
         {"type": mc("two_layers_feature_size"), "limit": 0, "lower_size": 0, "upper_size": 0})

    # ---- plants and ground cover ----
    patch("grass", weighted((5, state("grass")), (1, state("fern"))), tries=32)
    patch("tall_grass", weighted((3, state("tall_grass")), (2, state("grass"))), tries=64, xz=8)
    patch("ferns", weighted((3, state("fern")), (2, state("large_fern")), (1, state("grass"))), tries=48)
    patch("steppe_grass", weighted((6, state("grass")), (5, state("tall_grass")), (1, state("dead_bush"))),
          tries=96, xz=9)
    patch("prairie_flowers", flowers("poppy", "cornflower", "oxeye_daisy", "dandelion", "azure_bluet",
                                     "orange_tulip", "red_tulip", "allium"), tries=96, xz=9)
    patch("tall_flowers", flowers("sunflower", "lilac", "rose_bush", "peony"), tries=24, xz=6)
    patch("meadow_flowers", flowers("cornflower", "azure_bluet", "allium", "oxeye_daisy", "dandelion",
                                    "white_tulip"), tries=64, xz=8)
    patch("forest_flowers", flowers("lily_of_the_valley", "dandelion", "poppy", "white_tulip"), tries=32)
    patch("jungle_flowers", flowers("blue_orchid", "poppy"), tries=24)
    petals = [(3, state("pink_petals", facing=f, flower_amount=4)) for f in ("north", "east", "south", "west")]
    patch("heather", weighted(*petals, (2, state("allium"))), tries=96, xz=9)
    patch("shrubs", weighted((3, state("azalea")), (2, state("flowering_azalea"))), tries=12, xz=6)
    patch("moss_carpet", simple("moss_carpet"), tries=64)
    patch("sweet_berries", simple("sweet_berry_bush", age=3), tries=24, needs=survives("sweet_berry_bush", age=3))
    patch("dead_bush", simple("dead_bush"), tries=8, xz=7)
    patch("lily_pads", simple("lily_pad"), tries=12, xz=5, y=1)
    patch("melons", simple("melon"), tries=24, needs=survives("melon"))
    column_patch("sugar_cane", simple("sugar_cane", age=0), 2, 4, tries=20, needs=survives("sugar_cane", age=0))
    column_patch("cactus", simple("cactus", age=0), 1, 3, tries=10, needs=survives("cactus", age=0))
    column_patch("basalt_spires", simple("basalt", axis="y"), 3, 9)
    column_patch("ice_spikes", simple("packed_ice"), 4, 14, tries=10, xz=5)
    column_patch("sandstone_hoodoos", simple("sandstone"), 3, 7, tries=6, xz=3)
    column_patch("terracotta_spires", weighted((2, state("terracotta")), (1, state("orange_terracotta")),
                                               (1, state("red_terracotta"))), 4, 10, tries=8, xz=4)
    configured("mossy_boulder", "forest_rock", {"state": state("mossy_cobblestone")})
    configured("stone_boulder", "forest_rock", {"state": state("cobblestone")})
    configured("lava_pool", "lake", {"fluid": simple("lava", level=0), "barrier": simple("blackstone")})
    configured("water_lake", "lake", {"fluid": simple("water", level=0), "barrier": simple("stone")})

    # ---- ocean ----
    configured("seagrass", "seagrass", {"probability": 0.4})
    configured("kelp", "kelp", {})
    configured("coral", "simple_random_selector", {"features": [
        {"feature": {"type": mc(t), "config": {}}, "placement": []}
        for t in ("coral_tree", "coral_claw", "coral_mushroom")]})
    configured("sea_pickles", "sea_pickle", {"count": 20})
    configured("iceberg_packed", "iceberg", {"state": state("packed_ice")})
    configured("iceberg_blue", "iceberg", {"state": state("blue_ice")})

    # ---- placements (this order is the global feature order) ----
    p = placed
    p("iceberg_packed", "iceberg_packed", [rarity(16), IN_SQUARE, BIOME])
    p("iceberg_blue", "iceberg_blue", [rarity(200), IN_SQUARE, BIOME])
    p("lava_pools", "lava_pool", surface(rarity(5), hm="WORLD_SURFACE_WG"))
    p("lakes", "water_lake", surface(rarity(3), hm="WORLD_SURFACE_WG"))
    p("fen_pools", "water_lake", surface(rarity(2), hm="WORLD_SURFACE_WG"))
    p("boulders_mossy", "mossy_boulder", surface(rarity(3)))
    p("boulders_stone", "stone_boulder", surface(rarity(4)))
    p("spires_basalt", "basalt_spires", surface(rarity(2)))
    p("spires_basalt_rare", "basalt_spires", surface(rarity(6)))
    p("spires_ice", "ice_spikes", surface(rarity(3)))
    p("hoodoos_sandstone", "sandstone_hoodoos", surface(rarity(12)))
    p("spires_terracotta", "terracotta_spires", surface(rarity(4)))
    p("trees_redwood", "redwood", tree_at(3, spruce_ok))
    p("trees_ancient_oak", "ancient_oak", tree_at(2, oak_ok))
    p("trees_broad_oak_dense", "broad_oak", tree_at(6, oak_ok))
    p("trees_broad_oak", "broad_oak", tree_at(2, oak_ok))
    p("trees_broad_oak_rare", "broad_oak", tree_at(1, oak_ok, chance=6))
    p("trees_oak", "oak", tree_at(3, oak_ok))
    p("trees_oak_rare", "oak", tree_at(1, oak_ok, chance=4))
    p("trees_swamp_oak", "swamp_oak", tree_at(2, oak_ok))
    p("trees_tall_birch", "tall_birch", tree_at(3, birch_ok))
    p("trees_birch", "birch", tree_at(2, birch_ok))
    p("trees_spruce_dense", "spruce", tree_at(7, spruce_ok))
    p("trees_spruce", "spruce", tree_at(2, spruce_ok))
    p("trees_spruce_rare", "spruce", tree_at(1, spruce_ok, chance=5))
    p("trees_pine", "pine", tree_at(3, spruce_ok))
    p("trees_highland_pine_dense", "highland_pine", tree_at(4, spruce_ok))
    p("trees_highland_pine_rare", "highland_pine", tree_at(1, spruce_ok, chance=4))
    p("trees_acacia", "acacia", tree_at(1, acacia_ok, chance=2))
    p("trees_giant_jungle", "giant_jungle_tree", tree_at(2, jungle_ok))
    p("trees_jungle", "jungle_tree", tree_at(5, jungle_ok))
    p("trees_jungle_few", "jungle_tree", tree_at(2, jungle_ok))
    p("trees_palm", "palm", tree_at(6, sand_or_grass))
    p("trees_palm_rare", "palm", tree_at(1, sand_or_grass, chance=5))
    p("bushes", "bush", tree_at(1, oak_ok, chance=2))
    p("bushes_jungle", "jungle_bush", tree_at(4, jungle_ok))
    p("shrubs", "shrubs", surface(rarity(2)))
    p("heather", "heather", surface(count(5)))
    p("flowers_prairie", "prairie_flowers", surface(count(6)))
    p("flowers_tall", "tall_flowers", surface(rarity(2)))
    p("flowers_meadow", "meadow_flowers", surface(count(4)))
    p("flowers_forest", "forest_flowers", surface(count(2)))
    p("flowers_jungle", "jungle_flowers", surface(count(2)))
    p("grass_steppe", "steppe_grass", surface(count(8)))
    p("grass_tall", "tall_grass", surface(count(4)))
    p("grass", "grass", surface(count(5)))
    p("grass_sparse", "grass", surface(count(1)))
    p("ferns", "ferns", surface(count(5)))
    p("moss_carpet", "moss_carpet", surface(count(3)))
    p("sweet_berries", "sweet_berries", surface(rarity(6)))
    p("melons", "melons", surface(rarity(6)))
    p("dead_bush", "dead_bush", surface(rarity(2)))
    p("cactus", "cactus", surface(rarity(3)))
    p("sugar_cane", "sugar_cane", surface(count(3)))
    p("lily_pads", "lily_pads", surface(count(2), hm="WORLD_SURFACE_WG"))
    p("seagrass", "seagrass", [count(48), IN_SQUARE, heightmap("OCEAN_FLOOR_WG"), BIOME])
    p("kelp", "kelp", [count(40), IN_SQUARE, heightmap("OCEAN_FLOOR_WG"), BIOME])
    p("coral", "coral", [count(20), IN_SQUARE, heightmap("OCEAN_FLOOR_WG"), BIOME])
    p("sea_pickles", "sea_pickles", [rarity(16), IN_SQUARE, heightmap("OCEAN_FLOOR_WG"), BIOME])


# ---------------------------------------------------------------------------
# Spawns
# ---------------------------------------------------------------------------
def spawn(entity, weight, lo, hi):
    return {"type": mc(entity), "weight": weight, "minCount": lo, "maxCount": hi}


FARM = [spawn("sheep", 12, 4, 4), spawn("pig", 10, 4, 4), spawn("chicken", 10, 4, 4), spawn("cow", 8, 4, 4)]
CREATURES = {
    "none": [],
    "farm": FARM,
    "plains": FARM + [spawn("horse", 5, 2, 6), spawn("donkey", 1, 1, 3)],
    "forest": FARM + [spawn("wolf", 5, 4, 4)],
    "taiga": FARM + [spawn("wolf", 8, 4, 4), spawn("rabbit", 4, 2, 3), spawn("fox", 8, 2, 4)],
    "snowy": [spawn("rabbit", 10, 2, 3), spawn("polar_bear", 1, 1, 2), spawn("fox", 4, 2, 4)],
    "highland": [spawn("sheep", 16, 3, 6), spawn("rabbit", 6, 2, 3), spawn("fox", 4, 1, 2), spawn("goat", 3, 1, 3)],
    "mountain": [spawn("goat", 8, 1, 3), spawn("sheep", 4, 2, 4)],
    "savanna": FARM + [spawn("horse", 1, 2, 6), spawn("donkey", 1, 1, 1), spawn("llama", 8, 4, 4)],
    "jungle": [spawn("parrot", 40, 1, 2), spawn("panda", 1, 1, 2), spawn("ocelot", 2, 1, 3),
               spawn("chicken", 10, 4, 4), spawn("pig", 6, 4, 4)],
    "desert": [spawn("rabbit", 4, 2, 3), spawn("camel", 2, 1, 2)],
    "oasis": [spawn("camel", 6, 1, 3), spawn("rabbit", 4, 2, 3), spawn("chicken", 6, 2, 4)],
    "wetland": FARM + [spawn("frog", 10, 2, 5)],
    "beach": [spawn("turtle", 5, 2, 5)],
    "frozen_ocean": [spawn("polar_bear", 1, 1, 2)],
}
WATER = {
    "none": ([], []),
    "river": ([spawn("squid", 2, 1, 4)], [spawn("salmon", 5, 1, 5)]),
    "cold": ([spawn("squid", 3, 1, 4)], [spawn("cod", 15, 3, 6), spawn("salmon", 15, 1, 5)]),
    "ocean": ([spawn("squid", 1, 1, 4), spawn("dolphin", 1, 1, 2)], [spawn("cod", 10, 3, 6)]),
    "warm": ([spawn("squid", 10, 4, 4), spawn("dolphin", 2, 1, 2)],
             [spawn("tropical_fish", 25, 8, 8), spawn("pufferfish", 15, 1, 3)]),
}


def monsters(kind):
    base = [spawn("spider", 100, 4, 4), spawn("creeper", 100, 4, 4), spawn("slime", 100, 4, 4),
            spawn("enderman", 10, 1, 4), spawn("witch", 5, 1, 1)]
    if kind == "desert":
        return base + [spawn("zombie", 19, 4, 4), spawn("zombie_villager", 1, 1, 1), spawn("husk", 80, 4, 4),
                       spawn("skeleton", 100, 4, 4)]
    if kind == "snowy":
        return base + [spawn("zombie", 95, 4, 4), spawn("zombie_villager", 5, 1, 1), spawn("skeleton", 20, 4, 4),
                       spawn("stray", 80, 4, 4)]
    m = base + [spawn("zombie", 95, 4, 4), spawn("zombie_villager", 5, 1, 1), spawn("skeleton", 100, 4, 4)]
    if kind in ("ocean", "river"):
        m.append(spawn("drowned", 5 if kind == "ocean" else 100, 1, 1))
    return m


# ---------------------------------------------------------------------------
# Biomes
# ---------------------------------------------------------------------------
VANILLA_ORES = [mc(f"ore_{x}") for x in [
    "dirt", "gravel", "granite_upper", "granite_lower", "diorite_upper", "diorite_lower",
    "andesite_upper", "andesite_lower", "tuff", "coal_upper", "coal_lower", "iron_upper", "iron_middle",
    "iron_small", "gold", "gold_lower", "redstone", "redstone_lower", "diamond", "diamond_large",
    "diamond_buried", "lapis", "lapis_buried", "copper"]]

BIOMES = {}
LOCAL = {"iceberg_packed", "iceberg_blue"}
LAKES = {"lava_pools", "lakes", "fen_pools"}


def B(name, *, temp, downfall, colors, surface, under=DIRT, underwater=DIRT, sandy=False, rain=None,
      frozen=False, mobs="farm", monster="normal", water="none", veg=(), tail=(), particle=None, tags=()):
    BIOMES[name] = dict(temp=temp, downfall=downfall, colors=colors, surface=surface, under=under,
                        underwater=underwater, sandy=sandy, rain=temp < 1.5 if rain is None else rain,
                        frozen=frozen, mobs=mobs, monster=monster, water=water, veg=list(veg), tail=list(tail),
                        particle=particle, tags=list(tags))


def colors(sky, fog, water, water_fog, grass, foliage):
    return dict(sky=sky, fog=fog, water=water, water_fog=water_fog, grass=grass, foliage=foliage)


OCEAN_FLOOR_SAND = patches((0.6, GRAVEL), default=SAND)
OCEAN_FLOOR_GRAVEL = patches((0.4, block("clay")), default=GRAVEL)
RIVER_FLOOR = patches((0.3, SAND), (-0.4, DIRT), default=GRAVEL)


def define_biomes():
    # ---------------- oceans ----------------
    for deep in (False, True):
        d = "deep_" if deep else ""
        tags_o = ["ocean", "deep_ocean" if deep else "shallow_ocean"]
        B(f"{d}glacial_ocean", temp=0.0, downfall=0.5, frozen=True,
          colors=colors("#86b5ff", "#cfe6ff", "#4fb6e8" if not deep else "#3a92d0", "#0e3049", "#80b497", "#60a17b"),
          surface=OCEAN_FLOOR_GRAVEL, underwater=OCEAN_FLOOR_GRAVEL, mobs="frozen_ocean", monster="ocean",
          water="cold", veg=["iceberg_packed", "iceberg_blue"], tags=tags_o + ["cold", "frozen"])
        B(f"{d}northern_ocean", temp=0.5, downfall=0.5,
          colors=colors("#7ba7ff", "#c0d8ff", "#2e78b8" if not deep else "#225f9a", "#0b2338", "#80b497", "#60a17b"),
          surface=OCEAN_FLOOR_GRAVEL, underwater=OCEAN_FLOOR_GRAVEL, mobs="none", monster="ocean", water="cold",
          veg=["seagrass", "kelp"], tags=tags_o + ["cold"])
        B(f"{d}temperate_ocean", temp=0.5, downfall=0.5,
          colors=colors("#78a7ff", "#c0d8ff", "#2f96e6" if not deep else "#2276cc", "#0d3a66", "#8eb971", "#71a74d"),
          surface=OCEAN_FLOOR_SAND, underwater=OCEAN_FLOOR_SAND, mobs="none", monster="ocean", water="ocean",
          veg=["seagrass", "kelp"], tags=tags_o + ["temperate"])
        B(f"{d}tropical_ocean", temp=0.5, downfall=0.5,
          colors=colors("#6fb6ff", "#c8e8ff", "#1ad8cc" if not deep else "#12aedc", "#0a5f6a", "#8eb971", "#71a74d"),
          surface=SAND, underwater=SAND, sandy=True, mobs="none", monster="ocean", water="warm",
          veg=["seagrass", "coral", "sea_pickles"], tags=tags_o + ["warm"])

    # ---------------- coasts and rivers ----------------
    B("snowy_shore", temp=0.0, downfall=0.3, colors=colors("#86b5ff", "#cfe6ff", "#4fb6e8", "#0e3049", "#80b497", "#60a17b"),
      surface=patches((0.2, GRAVEL), default=SAND), underwater=GRAVEL, mobs="snowy", monster="snowy",
      tags=["beach", "cold", "snowy"])
    B("basalt_shore", temp=0.3, downfall=0.6, colors=colors("#9ec4ff", "#c9d6e0", "#1ec8d8", "#0b4a55", "#8fd14f", "#6fbf3f"),
      surface=seq(cond(STEEP, block("basalt", axis="y")),
                  patches((0.3, GRAVEL), (-0.3, block("blackstone")), default=block("basalt", axis="y"))),
      under=block("blackstone"), underwater=GRAVEL, mobs="none", veg=["spires_basalt_rare"],
      tags=["beach", "cold", "rocky"])
    B("golden_beach", temp=0.8, downfall=0.4, colors=colors("#78a7ff", "#c0d8ff", "#2fb0ff", "#0d3a66", "#8eb971", "#71a74d"),
      surface=SAND, under=SAND, underwater=SAND, sandy=True, mobs="beach", tags=["beach", "temperate"])
    B("tropical_beach", temp=0.95, downfall=0.6, colors=colors("#6fb6ff", "#c8e8ff", "#22e8d8", "#0a5f6a", "#6fe05a", "#4fd03a"),
      surface=SAND, under=SAND, underwater=SAND, sandy=True, mobs="beach", veg=["trees_palm_rare"],
      tags=["beach", "warm"])
    B("rocky_cliffs", temp=0.6, downfall=0.5, colors=colors("#7fb0ff", "#c4d8f0", "#2a8fd8", "#0d3a66", "#7fc04a", "#62aa3a"),
      surface=seq(cond(STEEP, STONE), patches((0.5, GRAVEL), default=GRASS)), underwater=GRAVEL, mobs="mountain",
      veg=["boulders_stone", "grass_sparse"], tags=["beach", "rocky", "hill"])
    B("glacial_river", temp=0.0, downfall=0.5, frozen=False,
      colors=colors("#86b5ff", "#cfe6ff", "#7fe0e8", "#2a6a7a", "#80b497", "#60a17b"),
      surface=RIVER_FLOOR, underwater=RIVER_FLOOR, mobs="none", monster="river", water="river",
      tags=["river", "cold", "frozen"])
    B("clearwater_river", temp=0.5, downfall=0.5, colors=colors("#78a7ff", "#c0d8ff", "#3fa8f0", "#0d3a66", "#7fc94a", "#5fb83a"),
      surface=RIVER_FLOOR, underwater=RIVER_FLOOR, mobs="none", monster="river", water="river",
      veg=["sugar_cane"], tags=["river", "temperate"])
    B("tropical_river", temp=0.95, downfall=0.9, colors=colors("#6fb6ff", "#c8e8ff", "#2fc8a8", "#0a5040", "#5fe050", "#3fd03a"),
      surface=RIVER_FLOOR, underwater=RIVER_FLOOR, mobs="none", monster="river", water="river",
      veg=["sugar_cane", "lily_pads"], tags=["river", "warm"])
    B("oasis", temp=1.6, downfall=0.5, rain=False, colors=colors("#6fb6ff", "#ffe2b0", "#22e0d4", "#0b6e66", "#5fe060", "#3fcf4f"),
      surface=patches((-0.25, GRASS), default=SAND), under=SAND, underwater=SAND, sandy=True, mobs="oasis",
      monster="desert", water="river", veg=["trees_palm", "grass", "sugar_cane", "lily_pads"],
      tags=["river", "hot", "dry", "desert"])

    # ---------------- frozen ----------------
    B("glacier_peaks", temp=-0.7, downfall=0.9, colors=colors("#a8ccff", "#e4f0ff", "#8fe8ff", "#2a5a7a", "#80b497", "#60a17b"),
      surface=seq(cond(STEEP, STONE), cond(noise("packed_ice", 0.0, 0.25), block("packed_ice")), block("snow_block")),
      under=seq(cond(STEEP, STONE), block("snow_block")), mobs="mountain", monster="snowy",
      tags=["mountain", "peak", "cold", "snowy", "frozen"])
    B("glacier", temp=-0.6, downfall=0.6, colors=colors("#a8ccff", "#e4f0ff", "#8fe8ff", "#2a5a7a", "#80b497", "#60a17b"),
      surface=seq(cond(STEEP, block("packed_ice")), cond(noise("ice", 0.3), block("blue_ice")),
                  cond(noise("surface", 0.4), block("packed_ice")), block("snow_block")),
      under=block("packed_ice"), mobs="snowy", monster="snowy", veg=["spires_ice"],
      tags=["hill", "cold", "snowy", "frozen"])
    B("tundra", temp=-0.3, downfall=0.4, colors=colors("#98bfff", "#d8e6f5", "#4aa8e0", "#14405e", "#9fb07a", "#7f9a5a"),
      surface=patches((0.55, GRAVEL), (0.3, block("coarse_dirt")), default=GRASS), mobs="snowy", monster="snowy",
      veg=["boulders_stone", "sweet_berries", "grass_sparse"], tags=["plains", "cold", "snowy"])
    B("boreal_snowwoods", temp=-0.5, downfall=0.8, colors=colors("#98bfff", "#d8e6f5", "#3a7fc0", "#0e2e4e", "#80b497", "#60a17b"),
      surface=patches((0.4, PODZOL), default=GRASS), mobs="taiga", monster="snowy",
      veg=["trees_spruce_dense", "sweet_berries", "ferns"], tags=["forest", "taiga", "cold", "snowy", "conifer"])

    # ---------------- cold (Iceland & Scotland) ----------------
    B("volcanic_cones", temp=0.2, downfall=0.3, colors=colors("#8fa3d1", "#b9aa9c", "#2fb8c9", "#0a3a44", "#7a9a3a", "#5e8a2e"),
      surface=seq(cond(y_above(300), cond(not_(STEEP), block("snow_block"))), cond(STEEP, block("basalt", axis="y")),
                  cond(noise("surface", -0.06, 0.06), block("magma_block")),
                  cond(noise("surface_secondary", 0.25), block("tuff")), block("blackstone")),
      under=block("blackstone"), underwater=block("blackstone"), mobs="mountain",
      veg=["lava_pools", "spires_basalt"], particle=("white_ash", 0.004),
      tags=["mountain", "peak", "cold", "dry", "volcanic", "rocky"])
    B("highland_crags", temp=0.25, downfall=0.7, colors=colors("#9fbbe0", "#c8d2dc", "#3a90c8", "#0e3048", "#8f8f5a", "#6f7f3a"),
      surface=snowcap(250, patches((0.6, GRAVEL), default=GRASS)), mobs="mountain",
      veg=["boulders_mossy", "heather", "grass"], tags=["mountain", "peak", "cold", "rocky"])
    B("basalt_highlands", temp=0.3, downfall=0.6, colors=colors("#9ec4ff", "#c9d6e0", "#1ec8d8", "#0b4a55", "#8fd14f", "#6fbf3f"),
      surface=seq(cond(STEEP, block("basalt", axis="y")), cond(noise("surface", 0.05), block("moss_block")),
                  cond(noise("surface_secondary", 0.3), block("tuff")), block("blackstone")),
      under=block("tuff"), underwater=block("blackstone"), mobs="highland",
      veg=["spires_basalt", "moss_carpet", "grass"], tags=["hill", "cold", "rocky"])
    B("highland_moors", temp=0.45, downfall=0.8, colors=colors("#a9bcd6", "#c4ccd6", "#3a5f7a", "#1d2b33", "#9a7598", "#6b7d3a"),
      surface=seq(cond(STEEP, STONE), patches((0.55, PODZOL), default=seq(
          cond(noise("surface", -10.0, -0.6), block("coarse_dirt")), GRASS))),
      mobs="highland", veg=["boulders_mossy", "trees_highland_pine_rare", "shrubs", "heather", "grass"],
      tags=["hill", "cold", "wet", "plains"])
    B("caledonian_pinewood", temp=0.35, downfall=0.8, colors=colors("#9fbbe0", "#c8d2dc", "#2f6f9f", "#0e2a40", "#8a8a62", "#5f7a3a"),
      surface=patches((0.3, PODZOL), (-0.3, GRASS), default=block("coarse_dirt")), mobs="taiga",
      veg=["boulders_mossy", "trees_highland_pine_dense", "shrubs", "heather", "ferns"],
      tags=["forest", "taiga", "cold", "wet", "conifer"])
    B("taiga_lakelands", temp=0.3, downfall=0.9, colors=colors("#90b8ff", "#c8d8ec", "#2a9fe8", "#0c3a5c", "#7aa868", "#5a9048"),
      surface=patches((0.35, PODZOL), default=GRASS), mobs="taiga",
      veg=["lakes", "trees_spruce", "trees_pine", "sweet_berries", "ferns"],
      tags=["forest", "taiga", "cold", "wet", "conifer"])

    # ---------------- temperate ----------------
    B("alpine_peaks", temp=0.1, downfall=0.6, colors=colors("#7fb2ff", "#d0e0f5", "#40b8ff", "#0e3a5e", "#7fc04a", "#5fa83a"),
      surface=seq(cond(STEEP, seq(cond(noise("calcite", -0.02, 0.02), block("calcite")), STONE)),
                  cond(y_above(260), block("snow_block")), cond(y_above(215), patches((0.0, GRAVEL), default=STONE)),
                  GRASS),
      under=seq(cond(STEEP, STONE), cond(y_above(215), STONE), DIRT), mobs="mountain",
      veg=["trees_spruce_rare", "flowers_meadow", "grass"], tags=["mountain", "peak", "temperate", "snowy"])
    B("jagged_spires", temp=0.0, downfall=0.6, colors=colors("#7fb2ff", "#d0e0f5", "#40b8ff", "#0e3a5e", "#7fc04a", "#5fa83a"),
      surface=seq(cond(STEEP, seq(cond(noise("calcite", -0.03, 0.03), block("calcite")), STONE)),
                  cond(y_above(240), block("snow_block")), STONE),
      under=STONE, mobs="mountain", tags=["mountain", "peak", "temperate", "snowy", "rocky"])
    B("alpine_meadow", temp=0.4, downfall=0.7, colors=colors("#7fb2ff", "#d0e0f5", "#3fc8ff", "#0e3a5e", "#83d148", "#63bb38"),
      surface=seq(cond(STEEP, STONE), GRASS), mobs="mountain",
      veg=["trees_spruce_rare", "flowers_meadow", "flowers_tall", "grass_tall", "grass"],
      tags=["hill", "temperate", "plains", "floral"])
    B("endless_steppe", temp=0.7, downfall=0.3, colors=colors("#7fb0ff", "#cfe0f0", "#4a9fd0", "#0e3a5e", "#a8c060", "#8eaa48"),
      surface=patches((0.65, block("coarse_dirt")), default=GRASS), mobs="plains",
      veg=["trees_oak_rare", "grass_steppe"], tags=["plains", "temperate", "dry"])
    B("wildflower_prairie", temp=0.8, downfall=0.5, colors=colors("#78a7ff", "#c0d8ff", "#3fa8f0", "#0d3a66", "#8ad04a", "#6cbc3a"),
      surface=GRASS, mobs="plains", veg=["trees_broad_oak_rare", "flowers_prairie", "flowers_tall", "grass_tall", "grass"],
      tags=["plains", "temperate", "floral"])
    B("mixed_woodland", temp=0.65, downfall=0.75, colors=colors("#78a7ff", "#c0d8ff", "#3f9fdf", "#0b3050", "#6fc43e", "#4fb02e"),
      surface=patches((0.6, PODZOL), default=GRASS), mobs="forest",
      veg=["trees_broad_oak", "trees_oak", "trees_birch", "bushes", "flowers_forest", "grass"],
      tags=["forest", "temperate", "deciduous"])
    B("autumn_woodland", temp=0.6, downfall=0.75, colors=colors("#86b0ff", "#e0d8c8", "#3a88c0", "#0b2a44", "#b4b048", "#e07a22"),
      surface=patches((0.5, PODZOL), (-0.6, GRASS), default=block("coarse_dirt")), mobs="forest",
      veg=["trees_broad_oak_dense", "trees_tall_birch", "bushes", "flowers_forest", "ferns"],
      tags=["forest", "temperate", "deciduous"])
    B("old_growth_oakwood", temp=0.7, downfall=0.9, colors=colors("#7fb2ff", "#c0d8ff", "#3f9fdf", "#0b3050", "#5fbf3a", "#3ea82a"),
      surface=patches((0.35, PODZOL), default=seq(cond(noise("surface", -10.0, -0.7), block("coarse_dirt")), GRASS)),
      mobs="forest", veg=["trees_ancient_oak", "trees_broad_oak_dense", "moss_carpet", "ferns", "flowers_forest"],
      tail=[mc("brown_mushroom_normal"), mc("red_mushroom_normal")],
      tags=["forest", "temperate", "wet", "deciduous"])
    B("redwood_giants", temp=0.55, downfall=0.95, colors=colors("#86b0ff", "#d4e2ee", "#2f7fb0", "#0b2a44", "#5fae4a", "#3f9a3a"),
      surface=patches((0.25, PODZOL), (-0.5, GRASS), default=block("coarse_dirt")), mobs="taiga",
      veg=["trees_redwood", "trees_spruce", "ferns", "moss_carpet"],
      tail=[mc("brown_mushroom_normal"), mc("red_mushroom_normal")],
      tags=["forest", "taiga", "temperate", "wet", "conifer"])
    B("fen", temp=0.7, downfall=0.9, colors=colors("#88a8d8", "#b8c4b0", "#5a7a3a", "#232f17", "#6a9a3a", "#5a8a2a"),
      surface=patches((0.2, block("mud")), default=GRASS), underwater=block("mud"), mobs="wetland", monster="river",
      veg=["fen_pools", "trees_swamp_oak", "lily_pads", "sugar_cane", "grass"], tags=["swamp", "temperate", "wet"])

    # ---------------- warm ----------------
    B("golden_savanna", temp=1.2, downfall=0.1, colors=colors("#7ab4ff", "#f0e4c8", "#3fa8c8", "#0d3a4a", "#c8c048", "#a8a838"),
      surface=patches((0.75, SAND), (0.45, block("coarse_dirt")), default=GRASS), mobs="savanna",
      veg=["trees_acacia", "grass_steppe"], tags=["savanna", "warm", "dry", "plains"])
    B("rainforest", temp=0.95, downfall=0.9, colors=colors("#6fb6ff", "#c8e8d8", "#2fc89f", "#0a4a3a", "#4fd83a", "#30c02a"),
      surface=patches((0.4, PODZOL), default=GRASS), mobs="jungle",
      veg=["trees_giant_jungle", "trees_jungle", "bushes_jungle", "melons", "flowers_jungle", "ferns"],
      tags=["jungle", "warm", "wet"])
    B("cloud_forest", temp=0.8, downfall=1.0, colors=colors("#a0b8d0", "#dce6ea", "#2fb8a8", "#0a4a40", "#4fc84a", "#30b03a"),
      surface=seq(cond(STEEP, STONE), patches((0.3, block("moss_block")), default=GRASS)), mobs="jungle",
      veg=["boulders_mossy", "trees_jungle_few", "bushes_jungle", "moss_carpet", "ferns"],
      tags=["jungle", "hill", "warm", "wet"])
    B("red_canyonlands", temp=2.0, downfall=0.0, rain=False,
      colors=colors("#7ab4ff", "#f0c8a0", "#4fb0c8", "#0d3a4a", "#b8a050", "#a09040"),
      surface=seq(cond(STEEP, BANDS), cond(y_above(160), BANDS), block("red_sand")), under=BANDS,
      underwater=block("red_sand"), mobs="desert", monster="desert",
      veg=["spires_terracotta", "dead_bush", "cactus"], tags=["badlands", "hot", "dry", "rocky"])

    # ---------------- hot ----------------
    B("great_erg", temp=2.0, downfall=0.0, rain=False, colors=colors("#6fb6ff", "#ffe2b0", "#3bd4c4", "#0b5e57", "#d9c060", "#c8b040"),
      surface=SAND, under=SAND, underwater=SAND, sandy=True, mobs="desert", monster="desert",
      veg=["hoodoos_sandstone", "dead_bush", "cactus"], tags=["desert", "hot", "dry"])
    B("rocky_hamada", temp=2.0, downfall=0.0, rain=False, colors=colors("#70b4ff", "#f0d8b0", "#4cb0b8", "#0d3a4a", "#c8b060", "#b0a040"),
      surface=seq(cond(STEEP, STONE), patches((0.45, GRAVEL), (0.1, block("red_sand")), (-0.4, SAND),
                                              default=block("coarse_dirt"))),
      under=patches((0.1, block("red_sand")), default=SAND), underwater=GRAVEL, mobs="desert", monster="desert",
      veg=["boulders_stone", "dead_bush"], tags=["desert", "hot", "dry", "rocky"])
    B("salt_flats", temp=2.0, downfall=0.0, rain=False, colors=colors("#62b0ff", "#fff6e8", "#9ff0ff", "#3aa0b0", "#d0c890", "#c0b880"),
      surface=block("calcite"), under=block("calcite"), underwater=block("calcite"), mobs="desert", monster="desert",
      veg=["dead_bush"], tags=["desert", "hot", "dry", "plains"])


def feature_steps(spec):
    order = {n: i for i, n in enumerate(ORDER)}
    veg = sorted(spec["veg"], key=order.__getitem__)
    return [
        [],
        [mc("lake_lava_underground")] + [vl(v) for v in veg if v in LAKES],
        [mc("amethyst_geode")] + [vl(v) for v in veg if v in LOCAL],
        [mc("monster_room"), mc("monster_room_deep")],
        [], [],
        list(VANILLA_ORES),
        [],
        [mc("spring_water"), mc("spring_lava")],
        [vl(v) for v in veg if v not in LAKES and v not in LOCAL] + spec["tail"],
        [mc("freeze_top_layer")],
    ]


def color(hexstr):
    return int(hexstr.lstrip("#"), 16)


def write_biomes():
    for name, s in BIOMES.items():
        c = s["colors"]
        effects = {"sky_color": color(c["sky"]), "fog_color": color(c["fog"]), "water_color": color(c["water"]),
                   "water_fog_color": color(c["water_fog"]), "grass_color": color(c["grass"]),
                   "foliage_color": color(c["foliage"]),
                   "mood_sound": {"sound": mc("ambient.cave"), "tick_delay": 6000, "block_search_extent": 8,
                                  "offset": 2.0}}
        if s["particle"]:
            effects["particle"] = {"options": {"type": mc(s["particle"][0])}, "probability": s["particle"][1]}
        water_creature, water_ambient = WATER[s["water"]]
        biome = {"has_precipitation": s["rain"], "temperature": s["temp"]}
        if s["frozen"]:
            biome["temperature_modifier"] = "frozen"
        biome.update({
            "downfall": s["downfall"],
            "effects": effects,
            "spawners": {"monster": monsters(s["monster"]), "creature": CREATURES[s["mobs"]],
                         "ambient": [spawn("bat", 10, 8, 8)],
                         "underground_water_creature": [spawn("glow_squid", 10, 4, 6)],
                         "water_creature": water_creature, "water_ambient": water_ambient,
                         "axolotls": [], "misc": []},
            "spawn_costs": {},
            "carvers": {"air": [mc("cave"), mc("cave_extra_underground"), mc("canyon")]},
            "features": feature_steps(s),
        })
        write(f"{MODID}/worldgen/biome/{name}.json", biome)


def surface_rule():
    top, under, underwater, sandy = [], [], [], []
    for name, s in BIOMES.items():
        top.append(cond(biome_is(vl(name)), s["surface"]))
        under.append(cond(biome_is(vl(name)), s["under"]))
        underwater.append(cond(biome_is(vl(name)), s["underwater"]))
        if s["sandy"]:
            sandy.append(vl(name))
    # vanilla biomes still in the map
    top += [cond(biome_is(mc("mushroom_fields")), block("mycelium", snowy=False)),
            cond(biome_is(mc("mangrove_swamp")), block("mud"))]
    underwater.append(cond(biome_is(mc("mangrove_swamp")), block("mud")))
    under.append(cond(biome_is(mc("mangrove_swamp")), block("mud")))
    return seq(
        cond({"type": mc("vertical_gradient"), "random_name": mc("bedrock_floor"),
              "true_at_and_below": {"above_bottom": 0}, "false_at_and_above": {"above_bottom": 5}}, block("bedrock")),
        cond({"type": mc("above_preliminary_surface")}, seq(
            cond(ON_FLOOR, seq(cond(ABOVE_WATER, seq(*top, GRASS)), seq(*underwater, DIRT))),
            cond(UNDER_FLOOR, seq(*under, DIRT)),
            cond(DEEP_UNDER_FLOOR, cond(biome_is(*sandy), block("sandstone"))),
            cond(ON_CEILING, cond(biome_is(*sandy), block("sandstone"))),
        )),
        cond({"type": mc("vertical_gradient"), "random_name": mc("deepslate"),
              "true_at_and_below": {"absolute": 0}, "false_at_and_above": {"absolute": 8}},
             block("deepslate", axis="y")),
    )


# ---------------------------------------------------------------------------
# Biome layout. Neighbouring climate bands hold related biomes, so the land
# changes gradually: dry -> wet runs across humidity, cold -> hot across
# temperature, lowland -> highland -> mountain across erosion.
# ---------------------------------------------------------------------------
T = [(-1.0, -0.45), (-0.45, -0.15), (-0.15, 0.2), (0.2, 0.55), (0.55, 1.0)]
H = [(-1.0, -0.35), (-0.35, -0.1), (-0.1, 0.1), (0.1, 0.3), (0.3, 1.0)]
C = {"mushroom": (-1.2, -1.05), "deep_ocean": (-1.05, -0.455), "ocean": (-0.455, -0.19),
     "coast": (-0.19, -0.11), "near": (-0.11, 0.03), "mid": (0.03, 0.3), "far": (0.3, 1.0)}
E = [(-1.0, -0.78), (-0.78, -0.375), (-0.375, -0.2225), (-0.2225, 0.05), (0.05, 0.45), (0.45, 0.55),
     (0.55, 1.0)]
W = [("high_neg", (-1.0, -0.26)), ("low_neg", (-0.26, -0.05)), ("valley", (-0.05, 0.05)),
     ("low_pos", (0.05, 0.26)), ("high_pos", (0.26, 1.0))]

OCEAN_BY_T = ["glacial_ocean", "northern_ocean", "temperate_ocean", "tropical_ocean", "tropical_ocean"]
RIVER_BY_T = ["glacial_river", "glacial_river", "clearwater_river", "clearwater_river", "tropical_river"]
LOWLAND = [
    ["tundra", "tundra", "tundra", "boreal_snowwoods", "boreal_snowwoods"],
    ["basalt_highlands", "highland_moors", "highland_moors", "caledonian_pinewood", "taiga_lakelands"],
    ["endless_steppe", "wildflower_prairie", "mixed_woodland", "old_growth_oakwood", "redwood_giants"],
    ["golden_savanna", "golden_savanna", "wildflower_prairie", "rainforest", "rainforest"],
    ["great_erg", "great_erg", "rocky_hamada", "rainforest", "rainforest"],
]
HIGHLAND = [
    ["glacier", "glacier", "glacier", "boreal_snowwoods", "boreal_snowwoods"],
    ["basalt_highlands", "basalt_highlands", "highland_moors", "caledonian_pinewood", "taiga_lakelands"],
    ["alpine_meadow", "alpine_meadow", "highland_moors", "old_growth_oakwood", "redwood_giants"],
    ["golden_savanna", "golden_savanna", "wildflower_prairie", "cloud_forest", "cloud_forest"],
    ["great_erg", "rocky_hamada", "red_canyonlands", "cloud_forest", "rainforest"],
]
MOUNTAIN = [
    ["glacier_peaks"] * 5,
    ["volcanic_cones", "volcanic_cones", "highland_crags", "glacier_peaks", "glacier_peaks"],
    ["highland_crags", "alpine_peaks", "alpine_peaks", "alpine_peaks", "alpine_peaks"],
    ["red_canyonlands", "red_canyonlands", "alpine_peaks", "cloud_forest", "cloud_forest"],
    ["red_canyonlands", "red_canyonlands", "red_canyonlands", "cloud_forest", "cloud_forest"],
]


def pick(t, h, c, e, w):
    if c == "mushroom":
        return mc("mushroom_fields")
    if c in ("deep_ocean", "ocean"):
        return ("deep_" if c == "deep_ocean" else "") + OCEAN_BY_T[t]
    if w == "valley" and e >= 2:
        if t == 4 and h <= 2:
            return "oasis"
        return "tropical_river" if (t == 3 and h >= 3) else RIVER_BY_T[t]
    if c == "coast":
        if t == 0:
            return "snowy_shore"
        if e <= 2:
            if t == 1 and h <= 2:
                return "basalt_shore"
            return "rocky_hamada" if (t == 4 and h <= 2) else "rocky_cliffs"
        if t == 1:
            return "basalt_shore" if h <= 2 else "golden_beach"
        if t == 4 and h <= 1:
            return "great_erg"
        return "tropical_beach" if (t >= 3 and h >= 2) else "golden_beach"
    mountain = e == 0 or (e == 1 and c in ("mid", "far"))
    if mountain:
        name = MOUNTAIN[t][h]
        if name == "alpine_peaks" and w == "high_pos":
            return "jagged_spires"
        return name
    if e in (1, 2):
        return HIGHLAND[t][h]
    if e == 6 and c == "near" and h >= 2:
        if t == 2:
            return "fen"
        if t >= 3:
            return mc("mangrove_swamp") if h >= 3 else "fen"
    if t == 4 and h == 0 and e >= 5:
        return "salt_flats"
    name = LOWLAND[t][h]
    if name == "mixed_woodland" and w.endswith("neg"):
        return "autumn_woodland"
    return name


def biome_layout():
    entries = []
    for ti, tr in enumerate(T):
        for hi, hr in enumerate(H):
            for cname, cr in C.items():
                for ei, er in enumerate(E):
                    runs = []
                    for wname, wr in W:
                        b = pick(ti, hi, cname, ei, wname)
                        b = b if ":" in b else vl(b)
                        if runs and runs[-1][0] == b:
                            runs[-1][2] = wr[1]
                        else:
                            runs.append([b, wr[0], wr[1]])
                    for b, wlo, whi in runs:
                        for depth in (0.0, 1.0):
                            entries.append({"biome": b, "parameters": {
                                "temperature": list(tr), "humidity": list(hr), "continentalness": list(cr),
                                "erosion": list(er), "weirdness": [wlo, whi], "depth": depth, "offset": 0.0}})
    full = [-1.0, 1.0]
    for b, hum, cont, depth, ero in [
        (mc("dripstone_caves"), full, [0.8, 1.0], [0.2, 0.9], full),
        (mc("lush_caves"), [0.7, 1.0], full, [0.2, 0.9], full),
        (mc("deep_dark"), full, full, 1.1, [-1.0, -0.375]),
    ]:
        entries.append({"biome": b, "parameters": {"temperature": full, "humidity": hum, "continentalness": cont,
                                                   "erosion": ero, "weirdness": full, "depth": depth,
                                                   "offset": 0.0}})
    write("minecraft/dimension/overworld.json", {
        "type": mc("overworld"),
        "generator": {"type": mc("noise"), "settings": vl("overworld"),
                      "biome_source": {"type": mc("multi_noise"), "biomes": entries}}})
    return entries


# ---------------------------------------------------------------------------
# Biome tags: how structure mods, quests and other mods find our biomes.
# Each biome lists simple categories; these map them onto real tags.
# ---------------------------------------------------------------------------
CATEGORY_TAGS = {
    "ocean": ["minecraft:is_ocean", "c:ocean", "minecraft:has_structure/shipwreck",
              "minecraft:has_structure/ruined_portal_ocean", "minecraft:plays_underwater_music",
              "minecraft:water_on_map_outlines"],
    "deep_ocean": ["minecraft:is_deep_ocean", "c:deep_ocean"],
    "shallow_ocean": ["c:shallow_ocean"],
    "river": ["minecraft:is_river", "c:river", "minecraft:plays_underwater_music", "minecraft:has_closer_water_fog",
              "minecraft:reduce_water_ambient_spawns", "minecraft:water_on_map_outlines"],
    "beach": ["minecraft:is_beach", "c:beach"],
    "mountain": ["minecraft:is_mountain", "c:mountain", "minecraft:has_structure/ruined_portal_mountain"],
    "peak": ["c:mountain_peak"],
    "hill": ["minecraft:is_hill", "c:extreme_hills"],
    "forest": ["minecraft:is_forest", "c:forest"],
    "taiga": ["minecraft:is_taiga", "c:taiga", "minecraft:has_structure/village_taiga"],
    "jungle": ["minecraft:is_jungle", "c:jungle", "minecraft:has_structure/jungle_temple",
               "minecraft:has_structure/ruined_portal_jungle"],
    "savanna": ["minecraft:is_savanna", "c:savanna", "minecraft:has_structure/village_savanna"],
    "badlands": ["minecraft:is_badlands", "c:badlands", "c:mesa", "minecraft:has_structure/mineshaft_mesa",
                 "minecraft:has_structure/ruined_portal_desert"],
    "desert": ["c:desert", "minecraft:has_structure/village_desert", "minecraft:has_structure/desert_pyramid",
               "minecraft:has_structure/ruined_portal_desert", "minecraft:spawns_gold_rabbits",
               "minecraft:snow_golem_melts"],
    "plains": ["c:plains", "minecraft:has_structure/village_plains", "minecraft:has_structure/pillager_outpost"],
    "swamp": ["c:swamp", "minecraft:has_structure/swamp_hut", "minecraft:has_structure/ruined_portal_swamp",
              "minecraft:water_on_map_outlines"],
    "snowy": ["c:snowy", "minecraft:spawns_snow_foxes", "minecraft:spawns_white_rabbits",
              "minecraft:has_structure/igloo"],
    "frozen": ["c:icy"],
    "cold": ["c:climate_cold", "minecraft:spawns_cold_variant_frogs", "minecraft:has_structure/ocean_ruin_cold"],
    "temperate": ["c:climate_temperate", "minecraft:has_structure/ocean_ruin_cold"],
    "warm": ["c:climate_hot", "minecraft:spawns_warm_variant_frogs", "minecraft:has_structure/ocean_ruin_warm",
             "minecraft:produces_corals_from_bonemeal"],
    "hot": ["c:climate_hot", "minecraft:spawns_warm_variant_frogs", "minecraft:snow_golem_melts"],
    "dry": ["c:climate_dry"],
    "wet": ["c:climate_wet"],
    "conifer": ["c:tree_coniferous"],
    "deciduous": ["c:tree_deciduous", "minecraft:has_structure/trail_ruins", "minecraft:has_structure/woodland_mansion"],
    "floral": ["c:floral"],
    "volcanic": ["c:volcanic"],
    "rocky": ["c:rocky"],
}
LAND_TAGS = ["minecraft:is_overworld", "c:in_overworld", "minecraft:stronghold_biased_to",
             "minecraft:has_structure/mineshaft"]
WATER_STRUCTURE_ONLY = {"ocean", "river"}


def tags():
    out = {}
    for name, s in BIOMES.items():
        tag_list = ["minecraft:is_overworld", "c:in_overworld", "minecraft:has_structure/mineshaft"]
        if not WATER_STRUCTURE_ONLY & set(s["tags"]):
            tag_list += LAND_TAGS
            tag_list.append("minecraft:has_structure/ruined_portal_standard")
        for cat in s["tags"]:
            tag_list += CATEGORY_TAGS[cat]
        # ocean-only structures stay in oceans
        if "ocean" not in s["tags"]:
            tag_list = [t for t in tag_list if "ocean_ruin" not in t and "shipwreck" not in t]
        for t in set(tag_list):
            out.setdefault(t, set()).add(vl(name))
    for t, members in out.items():
        ns, path = t.split(":")
        write(f"{ns}/tags/worldgen/biome/{path}.json", {"replace": False, "values": sorted(members)})


def lang():
    names = {f"biome.{MODID}.{n}": n.replace("_", " ").title().replace("Old Growth", "Old-Growth")
             for n in BIOMES}
    p = RES / "assets" / MODID / "lang" / "en_us.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(names, indent=2) + "\n")


def main():
    if DATA.exists():
        shutil.rmtree(DATA)
    dimension_type()
    density_functions()
    features()
    define_biomes()
    noise_settings()
    write_biomes()
    entries = biome_layout()
    tags()
    lang()
    print(f"Generated {len(BIOMES)} biomes, {len(ORDER)} placed features, {len(entries)} biome map entries")


if __name__ == "__main__":
    main()
