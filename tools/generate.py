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
TOP_SLIDE = (424, 440)       # terrain fades out between these heights


def mc(x):
    return f"minecraft:{x}"


def vl(x):
    return f"{MODID}:{x}"


def write(path, obj, compact=False):
    p = DATA / path
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, separators=(",", ":")) if compact else json.dumps(obj, indent=2)
    p.write_text(text + "\n")


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


# ---------------------------------------------------------------------------
# Dimension type: taller world
# ---------------------------------------------------------------------------
def dimension_type():
    write("minecraft/dimension_type/overworld.json", {
        "ultrawarm": False,
        "natural": True,
        "coordinate_scale": 1.0,
        "has_skylight": True,
        "has_ceiling": False,
        "ambient_light": 0.0,
        "monster_spawn_light_level": uniform(0, 7),
        "monster_spawn_block_light_limit": 0,
        "piglin_safe": False,
        "bed_works": True,
        "respawn_anchor_works": False,
        "has_raids": True,
        "logical_height": HEIGHT,
        "min_y": MIN_Y,
        "height": HEIGHT,
        "infiniburn": "#minecraft:infiniburn_overworld",
        "effects": mc("overworld"),
    })


# ---------------------------------------------------------------------------
# Density functions: vanilla "large biomes" shapes, stretched upward
# ---------------------------------------------------------------------------
def density_functions():
    top = MIN_Y + HEIGHT  # 448
    # Below sea level: vanilla slope (1/128 per block). Above: slope / VERTICAL_SCALE.
    above = -(top - 64) / (128 * VERTICAL_SCALE)
    gradient = {
        "type": mc("add"),
        "argument1": {"type": mc("y_clamped_gradient"), "from_y": MIN_Y, "to_y": 64,
                      "from_value": 1.5, "to_value": 0.5},
        "argument2": {"type": mc("y_clamped_gradient"), "from_y": 64, "to_y": top,
                      "from_value": 0.0, "to_value": above},
    }
    write(f"{MODID}/worldgen/density_function/overworld/depth.json", {
        "type": mc("add"),
        "argument1": gradient,
        "argument2": mc("overworld_large_biomes/offset"),
    })
    write(f"{MODID}/worldgen/density_function/overworld/factor.json", {
        "type": mc("mul"),
        "argument1": VERTICAL_SCALE,
        "argument2": mc("overworld_large_biomes/factor"),
    })
    write(f"{MODID}/worldgen/density_function/overworld/sloped_cheese.json", {
        "type": mc("add"),
        "argument1": {
            "type": mc("mul"),
            "argument1": 4.0,
            "argument2": {
                "type": mc("quarter_negative"),
                "argument": {
                    "type": mc("mul"),
                    "argument1": {
                        "type": mc("add"),
                        "argument1": vl("overworld/depth"),
                        "argument2": {
                            "type": mc("mul"),
                            "argument1": mc("overworld_large_biomes/jaggedness"),
                            "argument2": {
                                "type": mc("half_negative"),
                                "argument": {"type": mc("noise"), "noise": mc("jagged"),
                                             "xz_scale": 1500.0, "y_scale": 0.0},
                            },
                        },
                    },
                    "argument2": vl("overworld/factor"),
                },
            },
        },
        "argument2": mc("overworld/base_3d_noise"),
    })
    # Caves kept as a separate, swappable piece (vanilla cave system).
    write(f"{MODID}/worldgen/density_function/overworld/caves.json", {
        "type": mc("max"),
        "argument1": {
            "type": mc("min"),
            "argument1": {
                "type": mc("min"),
                "argument1": {
                    "type": mc("add"),
                    "argument1": {
                        "type": mc("mul"),
                        "argument1": 4.0,
                        "argument2": {"type": mc("square"),
                                      "argument": {"type": mc("noise"), "noise": mc("cave_layer"),
                                                   "xz_scale": 1.0, "y_scale": 8.0}},
                    },
                    "argument2": {
                        "type": mc("add"),
                        "argument1": {
                            "type": mc("clamp"),
                            "input": {"type": mc("add"), "argument1": 0.27,
                                      "argument2": {"type": mc("noise"), "noise": mc("cave_cheese"),
                                                    "xz_scale": 1.0, "y_scale": 0.6666666666666666}},
                            "min": -1.0, "max": 1.0,
                        },
                        "argument2": {
                            "type": mc("clamp"),
                            "input": {"type": mc("add"), "argument1": 1.5,
                                      "argument2": {"type": mc("mul"), "argument1": -0.64,
                                                    "argument2": vl("overworld/sloped_cheese")}},
                            "min": 0.0, "max": 0.5,
                        },
                    },
                },
                "argument2": mc("overworld/caves/entrances"),
            },
            "argument2": {"type": mc("add"),
                          "argument1": mc("overworld/caves/spaghetti_2d"),
                          "argument2": mc("overworld/caves/spaghetti_roughness_function")},
        },
        "argument2": {
            "type": mc("range_choice"),
            "input": mc("overworld/caves/pillars"),
            "min_inclusive": -1000000.0, "max_exclusive": 0.03,
            "when_in_range": -1000000.0,
            "when_out_of_range": mc("overworld/caves/pillars"),
        },
    })


def slides(inner):
    """Vanilla-style bottom and top slides around a density function."""
    return {
        "type": mc("add"),
        "argument1": 0.1171875,
        "argument2": {
            "type": mc("mul"),
            "argument1": {"type": mc("y_clamped_gradient"), "from_y": MIN_Y, "to_y": MIN_Y + 24,
                          "from_value": 0.0, "to_value": 1.0},
            "argument2": {
                "type": mc("add"),
                "argument1": -0.1171875,
                "argument2": {
                    "type": mc("add"),
                    "argument1": -0.078125,
                    "argument2": {
                        "type": mc("mul"),
                        "argument1": {"type": mc("y_clamped_gradient"), "from_y": TOP_SLIDE[0],
                                      "to_y": TOP_SLIDE[1], "from_value": 1.0, "to_value": 0.0},
                        "argument2": {"type": mc("add"), "argument1": 0.078125, "argument2": inner},
                    },
                },
            },
        },
    }


def ore_vein(noise):
    return {"type": mc("abs"), "argument": {
        "type": mc("interpolated"), "argument": {
            "type": mc("range_choice"), "input": mc("y"),
            "min_inclusive": -60.0, "max_exclusive": 51.0,
            "when_in_range": {"type": mc("noise"), "noise": mc(noise), "xz_scale": 4.0, "y_scale": 4.0},
            "when_out_of_range": 0.0}}}


def climate(noise):
    return {"type": mc("shifted_noise"), "noise": mc(noise), "xz_scale": 0.25, "y_scale": 0.0,
            "shift_x": mc("shift_x"), "shift_y": 0.0, "shift_z": mc("shift_z")}


def noise_settings():
    sloped = vl("overworld/sloped_cheese")
    terrain = {
        "type": mc("range_choice"),
        "input": sloped,
        "min_inclusive": -1000000.0, "max_exclusive": 1.5625,
        "when_in_range": {"type": mc("min"), "argument1": sloped,
                          "argument2": {"type": mc("mul"), "argument1": 5.0,
                                        "argument2": mc("overworld/caves/entrances")}},
        "when_out_of_range": vl("overworld/caves"),
    }
    final_density = {
        "type": mc("min"),
        "argument1": {"type": mc("squeeze"), "argument": {
            "type": mc("mul"), "argument1": 0.64,
            "argument2": {"type": mc("interpolated"), "argument": {
                "type": mc("blend_density"), "argument": slides(terrain)}}}},
        "argument2": mc("overworld/caves/noodle"),
    }
    initial = slides({
        "type": mc("clamp"),
        "input": {"type": mc("add"), "argument1": -0.703125,
                  "argument2": {"type": mc("mul"), "argument1": 4.0,
                                "argument2": {"type": mc("quarter_negative"), "argument": {
                                    "type": mc("mul"), "argument1": vl("overworld/depth"),
                                    "argument2": {"type": mc("cache_2d"),
                                                  "argument": vl("overworld/factor")}}}}},
        "min": -64.0, "max": 64.0,
    })
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
            "when_in_range": {"type": mc("noise"), "noise": mc("ore_veininess"), "xz_scale": 1.5,
                              "y_scale": 1.5},
            "when_out_of_range": 0.0}},
        "vein_ridged": {"type": mc("add"), "argument1": -0.07999999821186066,
                        "argument2": {"type": mc("max"), "argument1": ore_vein("ore_vein_a"),
                                      "argument2": ore_vein("ore_vein_b")}},
        "vein_gap": {"type": mc("noise"), "noise": mc("ore_gap"), "xz_scale": 1.0, "y_scale": 1.0},
    }
    spawn = {"temperature": [-1.0, 1.0], "humidity": [-1.0, 1.0], "continentalness": [-0.11, 1.0],
             "erosion": [-1.0, 1.0], "depth": 0.0, "offset": 0.0}
    write(f"{MODID}/worldgen/noise_settings/overworld.json", {
        "sea_level": SEA_LEVEL,
        "disable_mob_generation": False,
        "aquifers_enabled": True,
        "ore_veins_enabled": True,
        "legacy_random_source": False,
        "default_block": state("stone"),
        "default_fluid": state("water", level=0),
        "noise": {"min_y": MIN_Y, "height": HEIGHT, "size_horizontal": 1, "size_vertical": 2},
        "noise_router": router,
        "spawn_target": [dict(spawn, weirdness=[-1.0, -0.16]), dict(spawn, weirdness=[0.16, 1.0])],
        "surface_rule": surface_rule(),
    })


# ---------------------------------------------------------------------------
# Surface rules
# ---------------------------------------------------------------------------
def block(name, **props):
    return {"type": mc("block"), "result_state": state(name, **props)}


def seq(*rules):
    return {"type": mc("sequence"), "sequence": list(rules)}


def cond(c, rule):
    return {"type": mc("condition"), "if_true": c, "then_run": rule}


def biome_is(*names):
    return {"type": mc("biome"), "biome_is": list(names)}


def noise_range(noise, lo, hi=1.7976931348623157e308):
    return {"type": mc("noise_threshold"), "noise": mc(noise), "min_threshold": lo, "max_threshold": hi}


def y_above(y):
    return {"type": mc("y_above"), "anchor": {"absolute": y}, "surface_depth_multiplier": 0,
            "add_stone_depth": False}


def not_(c):
    return {"type": mc("not"), "invert": c}


STEEP = {"type": mc("steep")}
ON_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": False,
            "secondary_depth_range": 0}
UNDER_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": True,
               "secondary_depth_range": 0}
DEEP_UNDER_FLOOR = {"type": mc("stone_depth"), "offset": 0, "surface_type": "floor", "add_surface_depth": True,
                    "secondary_depth_range": 6}
ON_CEILING = {"type": mc("stone_depth"), "offset": 0, "surface_type": "ceiling", "add_surface_depth": False,
              "secondary_depth_range": 0}
ABOVE_WATER = {"type": mc("water"), "offset": -1, "surface_depth_multiplier": 0, "add_stone_depth": False}

SANDY = [vl("great_erg"), mc("beach"), mc("snowy_beach"), mc("desert"), mc("warm_ocean"),
         mc("lukewarm_ocean"), mc("deep_lukewarm_ocean")]
OCEANS = [mc(x) for x in ["ocean", "deep_ocean", "cold_ocean", "deep_cold_ocean", "frozen_ocean",
                          "deep_frozen_ocean", "lukewarm_ocean", "deep_lukewarm_ocean", "warm_ocean"]]


def surface_rule():
    top = seq(
        # --- Vivid Lands biomes ---
        cond(biome_is(vl("volcanic_cones")), seq(
            cond(y_above(300), cond(not_(STEEP), block("snow_block"))),
            cond(STEEP, block("basalt", axis="y")),
            cond(noise_range("surface", -0.06, 0.06), block("magma_block")),
            cond(noise_range("surface_secondary", 0.25), block("tuff")),
            block("blackstone"))),
        cond(biome_is(vl("basalt_highlands")), seq(
            cond(STEEP, block("basalt", axis="y")),
            cond(noise_range("surface", 0.05), block("moss_block")),
            cond(noise_range("surface_secondary", 0.3), block("tuff")),
            block("blackstone"))),
        cond(biome_is(vl("highland_moors")), seq(
            cond(STEEP, block("stone")),
            cond(noise_range("surface", 0.55), block("podzol", snowy=False)),
            cond(noise_range("surface", -10.0, -0.6), block("coarse_dirt")),
            block("grass_block", snowy=False))),
        cond(biome_is(vl("great_erg")), block("sand")),
        cond(biome_is(vl("oasis")), seq(
            cond(noise_range("surface", -0.25), block("grass_block", snowy=False)),
            block("sand"))),
        cond(biome_is(vl("old_growth_oakwood")), seq(
            cond(noise_range("surface", 0.35), block("podzol", snowy=False)),
            cond(noise_range("surface", -10.0, -0.7), block("coarse_dirt")),
            block("grass_block", snowy=False))),
        # --- vanilla biomes kept in the mix ---
        cond(biome_is(mc("frozen_peaks"), mc("jagged_peaks")), seq(
            cond(STEEP, block("stone")),
            cond(noise_range("packed_ice", 0.0, 0.2), block("packed_ice")),
            block("snow_block"))),
        cond(biome_is(mc("snowy_slopes")), seq(
            cond(STEEP, block("stone")),
            cond(noise_range("powder_snow", 0.45, 0.58), block("powder_snow")),
            block("snow_block"))),
        cond(biome_is(mc("stony_peaks")), seq(
            cond(noise_range("calcite", -0.0125, 0.0125), block("calcite")),
            block("stone"))),
        cond(biome_is(mc("stony_shore")), seq(
            cond(noise_range("gravel", -0.05, 0.05), block("gravel")),
            block("stone"))),
        cond(biome_is(mc("mushroom_fields")), block("mycelium", snowy=False)),
        cond(biome_is(mc("badlands"), mc("wooded_badlands")), seq(
            cond(biome_is(mc("wooded_badlands")),
                 cond(y_above(97), seq(cond(noise_range("surface", 0.2), block("coarse_dirt")),
                                       block("grass_block", snowy=False)))),
            cond(STEEP, {"type": mc("bandlands")}),
            block("red_sand"))),
        cond(biome_is(mc("mangrove_swamp")), block("mud")),
        cond(biome_is(mc("old_growth_spruce_taiga")), seq(
            cond(noise_range("surface", 0.6), block("coarse_dirt")),
            cond(noise_range("surface", -0.2), block("podzol", snowy=False)),
            block("grass_block", snowy=False))),
        cond(biome_is(*SANDY), block("sand")),
        cond(biome_is(*OCEANS), block("gravel")),
        block("grass_block", snowy=False),
    )
    underwater = seq(
        cond(biome_is(vl("volcanic_cones"), vl("basalt_highlands")), block("blackstone")),
        cond(biome_is(*SANDY, vl("oasis")), block("sand")),
        cond(biome_is(mc("badlands"), mc("wooded_badlands")), block("red_sand")),
        cond(biome_is(mc("mangrove_swamp")), block("mud")),
        cond(biome_is(*OCEANS, mc("frozen_river"), mc("stony_shore")), block("gravel")),
        block("dirt"),
    )
    under = seq(
        cond(biome_is(vl("volcanic_cones")), block("blackstone")),
        cond(biome_is(vl("basalt_highlands")), block("tuff")),
        cond(biome_is(vl("oasis"), *SANDY), block("sand")),
        cond(biome_is(mc("frozen_peaks"), mc("jagged_peaks"), mc("snowy_slopes")),
             cond(not_(STEEP), block("snow_block"))),
        cond(biome_is(mc("stony_peaks"), mc("stony_shore"), mc("frozen_peaks"), mc("jagged_peaks"),
                      mc("snowy_slopes")), block("stone")),
        cond(biome_is(mc("badlands"), mc("wooded_badlands")), {"type": mc("bandlands")}),
        cond(biome_is(mc("mangrove_swamp")), block("mud")),
        cond(biome_is(*OCEANS), block("gravel")),
        block("dirt"),
    )
    return seq(
        cond({"type": mc("vertical_gradient"), "random_name": mc("bedrock_floor"),
              "true_at_and_below": {"above_bottom": 0}, "false_at_and_above": {"above_bottom": 5}},
             block("bedrock")),
        cond({"type": mc("above_preliminary_surface")}, seq(
            cond(ON_FLOOR, seq(cond(ABOVE_WATER, top), underwater)),
            cond(UNDER_FLOOR, under),
            cond(DEEP_UNDER_FLOOR, cond(biome_is(vl("oasis"), *SANDY), block("sandstone"))),
            cond(ON_CEILING, cond(biome_is(vl("oasis"), *SANDY), block("sandstone"))),
        )),
        cond({"type": mc("vertical_gradient"), "random_name": mc("deepslate"),
              "true_at_and_below": {"absolute": 0}, "false_at_and_above": {"absolute": 8}},
             block("deepslate", axis="y")),
    )


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
def configured(name, ftype, config):
    write(f"{MODID}/worldgen/configured_feature/{name}.json", {"type": mc(ftype), "config": config})


def placed(name, feature, placement):
    write(f"{MODID}/worldgen/placed_feature/{name}.json", {"feature": feature, "placement": placement})


def count(n):
    return {"type": mc("count"), "count": n}


def rarity(n):
    return {"type": mc("rarity_filter"), "chance": n}


IN_SQUARE = {"type": mc("in_square")}
BIOME = {"type": mc("biome")}


def heightmap(h):
    return {"type": mc("heightmap"), "heightmap": h}


def surface_placement(*mods, hm="MOTION_BLOCKING"):
    return list(mods) + [IN_SQUARE, heightmap(hm), BIOME]


def tree_placement(n, survive):
    return [count(n), IN_SQUARE, {"type": mc("surface_water_depth_filter"), "max_water_depth": 0},
            heightmap("OCEAN_FLOOR"), {"type": mc("block_predicate_filter"), "predicate": survive}, BIOME]


AIR_ONLY = {"type": mc("matching_blocks"), "blocks": mc("air")}


def patch(name, provider, tries=48, xz=7, y=3):
    configured(name, "random_patch", {
        "tries": tries, "xz_spread": xz, "y_spread": y,
        "feature": {"feature": {"type": mc("simple_block"), "config": {"to_place": provider}},
                    "placement": [{"type": mc("block_predicate_filter"), "predicate": AIR_ONLY}]},
    })


def column_patch(name, provider, lo, hi, tries=16, xz=4):
    configured(name, "random_patch", {
        "tries": tries, "xz_spread": xz, "y_spread": 2,
        "feature": {"feature": {"type": mc("block_column"), "config": {
            "direction": "up",
            "allowed_placement": AIR_ONLY,
            "prioritize_tip": False,
            "layers": [{"height": uniform(lo, hi), "provider": provider}]}},
            "placement": [{"type": mc("block_predicate_filter"), "predicate": AIR_ONLY}]},
    })


def tree(name, log, leaves, trunk, foliage, size, dirt="dirt"):
    configured(name, "tree", {
        "ignore_vines": True,
        "force_dirt": False,
        "minimum_size": size,
        "dirt_provider": simple(dirt),
        "trunk_provider": simple(log, axis="y"),
        "foliage_provider": simple(leaves, distance=7, persistent=False, waterlogged=False),
        "trunk_placer": trunk,
        "foliage_placer": foliage,
        "decorators": [],
    })


TWO_LAYERS = {"type": mc("two_layers_feature_size"), "limit": 1, "lower_size": 0, "upper_size": 1}


def features():
    # Volcanic Cones
    configured("lava_pool", "lake", {"fluid": simple("lava", level=0), "barrier": simple("blackstone")})
    placed("volcanic_lava_pool", vl("lava_pool"), surface_placement(rarity(5), hm="WORLD_SURFACE_WG"))
    column_patch("basalt_spires", simple("basalt", axis="y"), 3, 9)
    placed("volcanic_basalt_spires", vl("basalt_spires"), surface_placement(rarity(3)))
    placed("highland_basalt_columns", vl("basalt_spires"), surface_placement(rarity(2)))

    # Basalt Highlands / Highland Moors ground cover
    patch("moss_carpet_patch", simple("moss_carpet"), tries=64)
    placed("highland_moss_carpet", vl("moss_carpet_patch"), surface_placement(count(3)))
    patch("highland_grass_patch", weighted((3, state("grass")), (2, state("fern"))), tries=32)
    placed("highland_grass", vl("highland_grass_patch"), surface_placement(count(4)))
    placed("moors_grass", vl("highland_grass_patch"), surface_placement(count(6)))
    petals = [(3, state("pink_petals", facing=f, flower_amount=4)) for f in ("north", "east", "south", "west")]
    patch("heather_patch", weighted(*petals, (2, state("allium"))), tries=96, xz=9, y=3)
    placed("moors_heather", vl("heather_patch"), surface_placement(count(5)))
    patch("moor_shrub_patch", weighted((3, state("azalea")), (2, state("flowering_azalea"))), tries=12, xz=6)
    placed("moors_shrubs", vl("moor_shrub_patch"), surface_placement(rarity(2)))
    configured("mossy_boulder", "forest_rock", {"state": state("mossy_cobblestone")})
    placed("moors_boulder", vl("mossy_boulder"), surface_placement(rarity(3)))
    tree("highland_pine", "spruce_log", "spruce_leaves",
         {"type": mc("straight_trunk_placer"), "base_height": 9, "height_rand_a": 4, "height_rand_b": 0},
         {"type": mc("blob_foliage_placer"), "radius": 2, "offset": 0, "height": 3}, TWO_LAYERS)
    placed("moors_pines", vl("highland_pine"),
           [rarity(4)] + tree_placement(1, {"type": mc("would_survive"),
                                            "state": state("spruce_sapling", stage=0)})[1:])

    # Great Erg / Oasis
    patch("dead_bush_patch", simple("dead_bush"), tries=8, xz=7)
    placed("erg_dead_bush", vl("dead_bush_patch"), surface_placement(rarity(2)))
    column_patch("sandstone_hoodoos", simple("sandstone"), 3, 7, tries=6, xz=3)
    placed("erg_hoodoos", vl("sandstone_hoodoos"), surface_placement(rarity(12)))
    tree("palm", "jungle_log", "jungle_leaves",
         {"type": mc("bending_trunk_placer"), "base_height": 6, "height_rand_a": 3, "height_rand_b": 0,
          "min_height_for_leaves": 3, "bend_length": uniform(1, 2)},
         {"type": mc("acacia_foliage_placer"), "radius": 3, "offset": 0}, TWO_LAYERS, dirt="sand")
    placed("oasis_palms", vl("palm"),
           tree_placement(6, {"type": mc("matching_blocks"), "offset": [0, -1, 0],
                              "blocks": [mc("sand"), mc("grass_block")]}))
    patch("oasis_grass_patch", weighted((4, state("grass")), (1, state("fern"))), tries=48)
    placed("oasis_grass", vl("oasis_grass_patch"), surface_placement(count(6)))
    patch("lily_pad_patch", simple("lily_pad"), tries=12, xz=5, y=1)
    placed("oasis_lily_pads", vl("lily_pad_patch"), surface_placement(count(2), hm="WORLD_SURFACE_WG"))

    # Old-Growth Oakwood
    tree("ancient_oak", "oak_log", "oak_leaves",
         {"type": mc("mega_jungle_trunk_placer"), "base_height": 16, "height_rand_a": 6, "height_rand_b": 6},
         {"type": mc("jungle_foliage_placer"), "radius": 2, "offset": 0, "height": 2},
         {"type": mc("two_layers_feature_size"), "limit": 1, "lower_size": 1, "upper_size": 2})
    tree("broad_oak", "oak_log", "oak_leaves",
         {"type": mc("fancy_trunk_placer"), "base_height": 4, "height_rand_a": 11, "height_rand_b": 0},
         {"type": mc("fancy_foliage_placer"), "radius": 2, "offset": 4, "height": 4},
         {"type": mc("two_layers_feature_size"), "limit": 0, "lower_size": 0, "upper_size": 0,
          "min_clipped_height": 4})
    oak_sapling = {"type": mc("would_survive"), "state": state("oak_sapling", stage=0)}
    placed("oakwood_ancient_oaks", vl("ancient_oak"), tree_placement(2, oak_sapling))
    placed("oakwood_broad_oaks", vl("broad_oak"), tree_placement(6, oak_sapling))
    placed("oakwood_moss_carpet", vl("moss_carpet_patch"), surface_placement(count(2)))
    patch("oakwood_floor_patch", weighted((3, state("fern")), (3, state("grass")),
                                          (1, state("lily_of_the_valley"))), tries=64)
    placed("oakwood_floor", vl("oakwood_floor_patch"), surface_placement(count(6)))


# ---------------------------------------------------------------------------
# Biomes
# ---------------------------------------------------------------------------
VANILLA_ORES = [mc(f"ore_{x}") for x in [
    "dirt", "gravel", "granite_upper", "granite_lower", "diorite_upper", "diorite_lower",
    "andesite_upper", "andesite_lower", "tuff", "coal_upper", "coal_lower", "iron_upper", "iron_middle",
    "iron_small", "gold", "gold_lower", "redstone", "redstone_lower", "diamond", "diamond_large",
    "diamond_buried", "lapis", "lapis_buried", "copper"]]


def feature_steps(lakes=(), vegetation=(), vegetation_tail=()):
    return [
        [],                                                              # raw_generation
        [mc("lake_lava_underground")] + list(lakes),                     # lakes
        [mc("amethyst_geode")],                                          # local_modifications
        [mc("monster_room"), mc("monster_room_deep")],                   # underground_structures
        [],                                                              # surface_structures
        [],                                                              # strongholds
        list(VANILLA_ORES),                                              # underground_ores
        [],                                                              # underground_decoration
        [mc("spring_water"), mc("spring_lava")],                         # fluid_springs
        [vl(v) for v in vegetation] + list(vegetation_tail),             # vegetal_decoration
        [mc("freeze_top_layer")],                                        # top_layer_modification
    ]


def spawn(entity, weight, lo, hi):
    return {"type": mc(entity), "weight": weight, "minCount": lo, "maxCount": hi}


def monsters(desert=False):
    m = [spawn("spider", 100, 4, 4), spawn("skeleton", 100, 4, 4), spawn("creeper", 100, 4, 4),
         spawn("slime", 100, 4, 4), spawn("enderman", 10, 1, 4), spawn("witch", 5, 1, 1)]
    if desert:
        m += [spawn("zombie", 19, 4, 4), spawn("zombie_villager", 1, 1, 1), spawn("husk", 80, 4, 4)]
    else:
        m += [spawn("zombie", 95, 4, 4), spawn("zombie_villager", 5, 1, 1)]
    return m


def color(hexstr):
    return int(hexstr.lstrip("#"), 16)


def biome(name, *, temp, downfall, rain, sky, fog, water, water_fog, grass, foliage, creatures,
          desert=False, lakes=(), vegetation=(), vegetation_tail=(), particle=None):
    effects = {
        "sky_color": color(sky), "fog_color": color(fog),
        "water_color": color(water), "water_fog_color": color(water_fog),
        "grass_color": color(grass), "foliage_color": color(foliage),
        "mood_sound": {"sound": mc("ambient.cave"), "tick_delay": 6000, "block_search_extent": 8,
                       "offset": 2.0},
    }
    if particle:
        effects["particle"] = {"options": {"type": mc(particle[0])}, "probability": particle[1]}
    write(f"{MODID}/worldgen/biome/{name}.json", {
        "has_precipitation": rain,
        "temperature": temp,
        "downfall": downfall,
        "effects": effects,
        "spawners": {
            "monster": monsters(desert),
            "creature": creatures,
            "ambient": [spawn("bat", 10, 8, 8)],
            "underground_water_creature": [spawn("glow_squid", 10, 4, 6)],
            "water_creature": [], "water_ambient": [], "axolotls": [], "misc": [],
        },
        "spawn_costs": {},
        "carvers": {"air": [mc("cave"), mc("cave_extra_underground"), mc("canyon")]},
        "features": feature_steps(lakes, vegetation, vegetation_tail),
    })


def biomes():
    biome("volcanic_cones", temp=0.2, downfall=0.3, rain=True,
          sky="#8fa3d1", fog="#b9aa9c", water="#2fb8c9", water_fog="#0a3a44",
          grass="#7a9a3a", foliage="#5e8a2e",
          creatures=[spawn("goat", 5, 1, 3)],
          lakes=[vl("volcanic_lava_pool")],
          vegetation=["volcanic_basalt_spires"],
          particle=("white_ash", 0.004))
    biome("basalt_highlands", temp=0.3, downfall=0.6, rain=True,
          sky="#9ec4ff", fog="#c9d6e0", water="#1ec8d8", water_fog="#0b4a55",
          grass="#8fd14f", foliage="#6fbf3f",
          creatures=[spawn("sheep", 12, 2, 4), spawn("rabbit", 6, 2, 3)],
          vegetation=["highland_basalt_columns", "highland_moss_carpet", "highland_grass"])
    biome("highland_moors", temp=0.45, downfall=0.8, rain=True,
          sky="#a9bcd6", fog="#c4ccd6", water="#3a5f7a", water_fog="#1d2b33",
          grass="#9a7598", foliage="#6b7d3a",
          creatures=[spawn("sheep", 16, 3, 6), spawn("rabbit", 6, 2, 3), spawn("fox", 4, 1, 2)],
          vegetation=["moors_boulder", "moors_pines", "moors_shrubs", "moors_heather", "moors_grass"])
    biome("great_erg", temp=2.0, downfall=0.0, rain=False,
          sky="#6fb6ff", fog="#ffe2b0", water="#3bd4c4", water_fog="#0b5e57",
          grass="#d9c060", foliage="#c8b040", desert=True,
          creatures=[spawn("rabbit", 4, 2, 3), spawn("camel", 2, 1, 2)],
          vegetation=["erg_hoodoos", "erg_dead_bush"])
    biome("oasis", temp=1.6, downfall=0.5, rain=False,
          sky="#6fb6ff", fog="#ffe2b0", water="#22e0d4", water_fog="#0b6e66",
          grass="#5fe060", foliage="#3fcf4f", desert=True,
          creatures=[spawn("camel", 6, 1, 3), spawn("rabbit", 4, 2, 3), spawn("chicken", 6, 2, 4)],
          vegetation=["oasis_palms", "oasis_grass", "oasis_lily_pads"],
          vegetation_tail=[mc("patch_sugar_cane")])
    biome("old_growth_oakwood", temp=0.7, downfall=0.9, rain=True,
          sky="#7fb2ff", fog="#c0d8ff", water="#3f9fdf", water_fog="#0b3050",
          grass="#5fbf3a", foliage="#3ea82a",
          creatures=[spawn("wolf", 5, 4, 4), spawn("pig", 8, 4, 4), spawn("sheep", 10, 4, 4),
                     spawn("cow", 8, 4, 4), spawn("chicken", 8, 4, 4)],
          vegetation=["oakwood_ancient_oaks", "oakwood_broad_oaks", "oakwood_moss_carpet", "oakwood_floor"],
          vegetation_tail=[mc("brown_mushroom_normal"), mc("red_mushroom_normal")])


# ---------------------------------------------------------------------------
# Biome layout (replaces the vanilla overworld biome map)
# ---------------------------------------------------------------------------
T = [(-1.0, -0.45), (-0.45, -0.15), (-0.15, 0.2), (0.2, 0.55), (0.55, 1.0)]
H = [(-1.0, -0.35), (-0.35, -0.1), (-0.1, 0.1), (0.1, 0.3), (0.3, 1.0)]
C = {"mushroom": (-1.2, -1.05), "deep_ocean": (-1.05, -0.455), "ocean": (-0.455, -0.19),
     "coast": (-0.19, -0.11), "near": (-0.11, 0.03), "mid": (0.03, 0.3), "far": (0.3, 1.0)}
E = [(-1.0, -0.78), (-0.78, -0.375), (-0.375, -0.2225), (-0.2225, 0.05), (0.05, 0.45), (0.45, 0.55),
     (0.55, 1.0)]
W = [("high_neg", (-1.0, -0.26)), ("low_neg", (-0.26, -0.05)), ("valley", (-0.05, 0.05)),
     ("low_pos", (0.05, 0.26)), ("high_pos", (0.26, 1.0))]


def pick(t, h, c, e, w):
    if c == "mushroom":
        return "mushroom_fields"
    if c in ("deep_ocean", "ocean"):
        deep = c == "deep_ocean"
        if t == 0:
            return "deep_frozen_ocean" if deep else "frozen_ocean"
        if t == 1:
            return "deep_cold_ocean" if deep else "cold_ocean"
        if t == 2:
            return "deep_ocean" if deep else "ocean"
        if t == 3:
            return "deep_lukewarm_ocean" if deep else "lukewarm_ocean"
        return "warm_ocean"
    if w == "valley" and e >= 2:
        if t == 0:
            return "frozen_river"
        if t == 4 and h <= 2:
            return vl("oasis")
        return "river"
    if c == "coast":
        if e <= 2:
            return vl("basalt_highlands") if (t == 1 and h <= 2) else "stony_shore"
        if t == 0:
            return "snowy_beach"
        if t == 1 and h <= 1:
            return vl("basalt_highlands")
        if t == 4 and h <= 2:
            return vl("great_erg")
        return "beach"
    mountain = e == 0 or (e == 1 and c in ("mid", "far"))
    if mountain:
        if t == 0:
            return "frozen_peaks" if w.endswith("neg") else "jagged_peaks"
        if t == 1:
            return vl("volcanic_cones") if h <= 2 else "jagged_peaks"
        if t == 2:
            if h == 0:
                return vl("volcanic_cones")
            return "jagged_peaks" if w == "high_pos" else "stony_peaks"
        if t == 3:
            return "stony_peaks"
        return "badlands" if h <= 2 else "stony_peaks"
    if e in (1, 2):
        if t == 0:
            return "snowy_slopes"
        if t == 1:
            return vl("basalt_highlands") if h <= 1 else vl("highland_moors")
        if t == 2:
            return "meadow" if h == 0 else vl("highland_moors") if h <= 2 else vl("old_growth_oakwood")
        if t == 3:
            return "savanna_plateau" if h <= 2 else "jungle"
        return vl("great_erg") if h <= 2 else "wooded_badlands"
    # lowlands
    if e == 6 and c == "near":
        if t in (2, 3) and h >= 2:
            return "swamp"
        if t == 4 and h >= 3:
            return "mangrove_swamp"
    if t == 0:
        if h <= 2:
            return "ice_spikes" if (h == 0 and w == "high_pos") else "snowy_plains"
        return "snowy_taiga"
    if t == 1:
        return [vl("basalt_highlands"), vl("highland_moors"), vl("highland_moors"), "taiga",
                "old_growth_spruce_taiga"][h]
    if t == 2:
        if h <= 1:
            return "plains"
        if h == 2:
            return "birch_forest" if w.endswith("neg") else "forest"
        return vl("old_growth_oakwood")
    if t == 3:
        return ["savanna", "savanna", "plains", "sparse_jungle", "jungle"][h]
    return vl("great_erg") if h <= 2 else ("sparse_jungle" if h == 3 else "jungle")


def r(pair):
    return [pair[0], pair[1]]


def biome_layout():
    entries = []
    for ti, tr in enumerate(T):
        for hi, hr in enumerate(H):
            for cname, cr in C.items():
                for ei, er in enumerate(E):
                    # merge neighbouring weirdness bands that pick the same biome
                    runs = []
                    for wname, wr in W:
                        b = pick(ti, hi, cname, ei, wname)
                        b = b if ":" in b else mc(b)
                        if runs and runs[-1][0] == b:
                            runs[-1][2] = wr[1]
                        else:
                            runs.append([b, wr[0], wr[1]])
                    for b, wlo, whi in runs:
                        for depth in (0.0, 1.0):
                            entries.append({"biome": b, "parameters": {
                                "temperature": r(tr), "humidity": r(hr), "continentalness": r(cr),
                                "erosion": r(er), "weirdness": [wlo, whi], "depth": depth, "offset": 0.0}})
    full = [-1.0, 1.0]
    caves = [
        (mc("dripstone_caves"), dict(continentalness=[0.8, 1.0], humidity=full, depth=[0.2, 0.9])),
        (mc("lush_caves"), dict(continentalness=full, humidity=[0.7, 1.0], depth=[0.2, 0.9])),
        (mc("deep_dark"), dict(continentalness=full, humidity=full, depth=1.1, erosion=[-1.0, -0.375])),
    ]
    for b, p in caves:
        params = {"temperature": full, "humidity": p["humidity"], "continentalness": p["continentalness"],
                  "erosion": p.get("erosion", full), "weirdness": full, "depth": p["depth"], "offset": 0.0}
        entries.append({"biome": b, "parameters": params})
    write("minecraft/dimension/overworld.json", {
        "type": mc("overworld"),
        "generator": {
            "type": mc("noise"),
            "settings": vl("overworld"),
            "biome_source": {"type": mc("multi_noise"), "biomes": entries},
        },
    }, compact=True)
    return entries


# ---------------------------------------------------------------------------
# Biome tags (how structure mods, quests and other mods find our biomes)
# ---------------------------------------------------------------------------
TAGS = {
    "minecraft": {
        "is_overworld": ["volcanic_cones", "basalt_highlands", "highland_moors", "great_erg", "oasis",
                         "old_growth_oakwood"],
        "is_mountain": ["volcanic_cones"],
        "is_hill": ["basalt_highlands", "highland_moors"],
        "is_forest": ["old_growth_oakwood"],
        "stronghold_biased_to": ["volcanic_cones", "basalt_highlands", "highland_moors", "great_erg",
                                 "oasis", "old_growth_oakwood"],
        "has_structure/mineshaft": ["volcanic_cones", "basalt_highlands", "highland_moors", "great_erg",
                                    "oasis", "old_growth_oakwood"],
        "has_structure/ruined_portal_mountain": ["volcanic_cones", "basalt_highlands"],
        "has_structure/ruined_portal_standard": ["highland_moors", "old_growth_oakwood"],
        "has_structure/ruined_portal_desert": ["great_erg", "oasis"],
        "has_structure/village_plains": ["highland_moors"],
        "has_structure/village_desert": ["great_erg", "oasis"],
        "has_structure/village_taiga": ["basalt_highlands"],
        "has_structure/desert_pyramid": ["great_erg"],
        "has_structure/pillager_outpost": ["highland_moors", "great_erg", "basalt_highlands"],
        "has_structure/woodland_mansion": ["old_growth_oakwood"],
        "has_structure/trail_ruins": ["old_growth_oakwood", "highland_moors"],
        "allows_surface_slime_spawns": [],
        "spawns_cold_variant_frogs": ["basalt_highlands", "highland_moors", "volcanic_cones"],
        "spawns_warm_variant_frogs": ["great_erg", "oasis"],
    },
    # Fabric convention tags (used by many Fabric mods)
    "c": {
        "in_overworld": ["volcanic_cones", "basalt_highlands", "highland_moors", "great_erg", "oasis",
                         "old_growth_oakwood"],
        "mountain": ["volcanic_cones"],
        "mountain_peak": ["volcanic_cones"],
        "volcanic": ["volcanic_cones"],
        "climate_cold": ["volcanic_cones", "basalt_highlands"],
        "climate_temperate": ["highland_moors", "old_growth_oakwood"],
        "climate_hot": ["great_erg", "oasis"],
        "climate_dry": ["great_erg", "volcanic_cones"],
        "climate_wet": ["highland_moors", "old_growth_oakwood"],
        "desert": ["great_erg", "oasis"],
        "forest": ["old_growth_oakwood"],
        "tree_deciduous": ["old_growth_oakwood"],
        "plains": ["highland_moors"],
        "rocky": ["basalt_highlands", "volcanic_cones"],
    },
}


def tags():
    for ns, group in TAGS.items():
        for tag, names in group.items():
            if names:
                write(f"{ns}/tags/worldgen/biome/{tag}.json",
                      {"replace": False, "values": [vl(n) for n in names]})


def lang():
    names = {
        "volcanic_cones": "Volcanic Cones", "basalt_highlands": "Basalt Highlands",
        "highland_moors": "Highland Moors", "great_erg": "Great Erg", "oasis": "Oasis",
        "old_growth_oakwood": "Old-Growth Oakwood",
    }
    p = RES / "assets" / MODID / "lang" / "en_us.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({f"biome.{MODID}.{k}": v for k, v in names.items()}, indent=2) + "\n")


def main():
    if DATA.exists():
        shutil.rmtree(DATA)
    dimension_type()
    density_functions()
    noise_settings()
    features()
    biomes()
    entries = biome_layout()
    tags()
    lang()
    print(f"Generated data: {len(entries)} biome map entries")


if __name__ == "__main__":
    main()
