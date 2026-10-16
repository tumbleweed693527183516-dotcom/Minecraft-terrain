#!/usr/bin/env python3
"""
Writes the Create recipes of the Vivid Lands: Ragnarok pack mod (ragnarok/src/main/resources/data).

The Nether and the End are closed in this pack, so everything they normally give can be made in
the Overworld with Create machines. Create already covers a lot (haunting: soul sand, soul soil,
blackstone, crimson/warped fungus, nether brick; crushing diorite -> quartz; filling cinder flour ->
glowstone; crushing netherrack -> cinder flour for blaze cakes). These recipes fill the gaps.

Every Nether and End item is craftable from cobblestone: each chain starts with cobblestone (or a
block already made from it) and only adds ordinary renewable Overworld items.

  cobblestone + lava (mixing) -> netherrack -> soul sand -> soul soil, nylium, nether wart, magma
  cobblestone (haunting, Create) -> blackstone -> quartz, blaze rods, crying obsidian, netherite
  cobblestone + ender pearl (mixing) -> end stone -> chorus fruit and flowers -> purpur, shulker shells
Fluid amounts are Fabric droplets: 81 per millibucket.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ragnarok" / "src" / "main" / "resources" / "data" / "vividlands_ragnarok" / "recipes"
MB = 81
CREATE = [{"condition": "fabric:all_mods_loaded", "values": ["create"]}]


def item(i, count=None):
    d = {"tag": i[1:]} if i.startswith("#") else {"item": i}
    if count:
        d["count"] = count
    return d


def fluid(f, mb):
    return {"fluid": f, "amount": mb * MB}


R = {}


def processing(name, kind, ingredients, results, heat=None, **extra):
    r = {"fabric:load_conditions": CREATE, "type": f"create:{kind}",
         "ingredients": [x if isinstance(x, dict) else item(x) for x in ingredients],
         "results": [x if isinstance(x, dict) else item(x) for x in results]}
    if heat:
        r["heatRequirement"] = heat
    r.update(extra)
    R[name] = r


def mechanical(name, pattern, key, result, count=1):
    R[name] = {"fabric:load_conditions": CREATE, "type": "create:mechanical_crafting", "acceptMirrored": False,
               "key": {k: item(v) for k, v in key.items()}, "pattern": pattern,
               "result": item(result, count if count > 1 else None)}


def shapeless(name, ingredients, result, count=1):
    R[name] = {"fabric:load_conditions": CREATE, "type": "minecraft:crafting_shapeless",
               "ingredients": [item(i) for i in ingredients], "result": item(result, count if count > 1 else None)}


M = "minecraft:"
C = "create:"

# Every Nether and End item can be made from cobblestone: each chain starts with cobblestone (or a block
# already made from it), plus only ordinary renewable Overworld extras (lava, water, gold, pearls...).
# Create's own chain gives: cobblestone -milling-> gravel -crushing-> sand; haunting cobblestone -> blackstone.

# ---------------- Nether: blocks ----------------
processing("netherrack_from_mixing", "mixing", ["#c:cobblestone", fluid(M + "lava", 50)], [M + "netherrack"])
processing("soul_sand_from_mixing", "mixing", [M + "netherrack", "#minecraft:sand"], [item(M + "soul_sand", 2)])
processing("soul_soil_from_mixing", "mixing", [M + "soul_sand", M + "gravel"], [item(M + "soul_soil", 2)])
processing("basalt_from_compacting", "compacting", ["#c:cobblestone", "#c:cobblestone", fluid(M + "lava", 100)],
           [item(M + "basalt", 2)])
processing("magma_block_from_compacting", "compacting", [M + "netherrack", fluid(M + "lava", 100)], [M + "magma_block"])
processing("gilded_blackstone_from_deploying", "deploying", [M + "blackstone", M + "gold_ingot"], [M + "gilded_blackstone"])
processing("crying_obsidian_from_haunting", "haunting", [M + "obsidian"], [M + "crying_obsidian"])
processing("crying_obsidian_from_mixing", "mixing", [M + "blackstone", M + "blackstone", fluid(M + "lava", 250)],
           [M + "crying_obsidian"], heat="superheated")
processing("nether_gold_ore_from_deploying", "deploying", [M + "netherrack", M + "gold_nugget"], [M + "nether_gold_ore"])
processing("nether_quartz_ore_from_deploying", "deploying", [M + "netherrack", M + "quartz"], [M + "nether_quartz_ore"])
processing("ancient_debris_from_compacting", "compacting", [M + "netherite_scrap", M + "blackstone"], [M + "ancient_debris"],
           heat="superheated")

# ---------------- Nether: plants (bone-meal nylium for fungi, roots, sprouts; grow huge fungi for stems,
# wart blocks, shroomlight and vines) ----------------
processing("nether_wart_from_mixing", "mixing", [M + "soul_sand", C + "cinder_flour", fluid(M + "water", 100)],
           [M + "nether_wart"])
processing("crimson_nylium_from_deploying", "deploying", [M + "netherrack", M + "nether_wart"], [M + "crimson_nylium"])
processing("warped_nylium_from_mixing", "mixing", [M + "netherrack", M + "soul_soil", fluid(M + "water", 100)],
           [M + "warped_nylium"])

# ---------------- Nether: items ----------------
processing("quartz_from_crushing", "crushing", [M + "blackstone"],
           [{"item": M + "quartz", "chance": 0.5}, {"item": M + "quartz", "chance": 0.25}], processingTime=250)
processing("glowstone_dust_from_mixing", "mixing", [C + "cinder_flour", C + "cinder_flour", fluid(M + "lava", 50)],
           [M + "glowstone_dust"], heat="heated")
processing("magma_cream_from_crushing", "crushing", [M + "magma_block"],
           [item(M + "magma_cream", 3), {"item": M + "magma_cream", "chance": 0.5}], processingTime=200)
processing("blaze_rod_from_compacting", "compacting",
           [M + "blackstone", M + "gold_nugget", M + "gold_nugget", fluid(M + "lava", 250)], [M + "blaze_rod"])
shapeless("blaze_burner_from_blaze_rods", [C + "empty_blaze_burner"] + [M + "blaze_rod"] * 4, C + "blaze_burner")
processing("ghast_tear_from_mixing", "mixing", [M + "soul_sand", M + "quartz", fluid(M + "water", 250)],
           [M + "ghast_tear"], heat="heated")
processing("wither_skeleton_skull_from_haunting", "haunting", [M + "skeleton_skull"], [M + "wither_skeleton_skull"])
processing("wither_skeleton_skull_from_mixing", "mixing", [M + "blackstone", M + "blackstone", M + "bone_block"],
           [M + "wither_skeleton_skull"], heat="superheated")
processing("netherite_scrap_from_mixing", "mixing",
           [M + "diamond", C + "crushed_raw_gold", C + "crushed_raw_gold", M + "blackstone", fluid(M + "lava", 500)],
           [M + "netherite_scrap"], heat="superheated")
mechanical("netherite_upgrade_smithing_template", ["DSD", "DND", "DDD"],
           {"D": M + "diamond", "S": M + "netherite_scrap", "N": M + "netherrack"},
           M + "netherite_upgrade_smithing_template")
mechanical("rib_armor_trim_smithing_template", ["DSD", "DBD", "DDD"],
           {"D": M + "diamond", "S": M + "wither_skeleton_skull", "B": M + "bone_block"},
           M + "rib_armor_trim_smithing_template")
mechanical("snout_armor_trim_smithing_template", ["DGD", "DBD", "DDD"],
           {"D": M + "diamond", "G": M + "gold_block", "B": M + "blackstone"},
           M + "snout_armor_trim_smithing_template")
mechanical("piglin_head", ["GBG", "BSB", "GBG"],
           {"G": M + "gold_ingot", "B": M + "blackstone", "S": M + "skeleton_skull"}, M + "piglin_head")
mechanical("music_disc_pigstep", ["BGB", "GDG", "BGB"],
           {"B": M + "blackstone", "G": M + "gold_ingot", "D": M + "diamond"}, M + "music_disc_pigstep")
shapeless("piglin_banner_pattern", [M + "paper", M + "gilded_blackstone"], M + "piglin_banner_pattern")

# ---------------- End ----------------
processing("end_stone_from_mixing", "mixing", ["#c:cobblestone"] * 4 + [M + "ender_pearl"], [item(M + "end_stone", 4)])
processing("chorus_fruit_from_mixing", "mixing", [M + "end_stone", M + "ender_pearl", fluid(M + "water", 250)],
           [item(M + "chorus_fruit", 4)])
processing("chorus_flower_from_mixing", "mixing", [M + "end_stone", M + "ender_pearl", M + "bone_meal"],
           [M + "chorus_flower"])
processing("shulker_shell_from_mixing", "mixing",
           [M + "purpur_block", M + "ender_pearl", M + "ender_pearl", M + "popped_chorus_fruit"],
           [M + "shulker_shell"], heat="heated")
processing("dragon_breath_from_mixing", "mixing", [M + "glass_bottle", M + "popped_chorus_fruit", M + "blaze_powder"],
           [M + "dragon_breath"], heat="heated")
mechanical("elytra", ["MSM", "MDM", "MPM"],
           {"M": M + "phantom_membrane", "S": M + "shulker_shell", "D": M + "diamond", "P": M + "popped_chorus_fruit"},
           M + "elytra")
mechanical("spire_armor_trim_smithing_template", ["DSD", "DPD", "DDD"],
           {"D": M + "diamond", "S": M + "shulker_shell", "P": M + "purpur_block"},
           M + "spire_armor_trim_smithing_template")
mechanical("dragon_head", ["PEP", "ESE", "PEP"],
           {"P": M + "purpur_block", "E": M + "end_stone", "S": M + "wither_skeleton_skull"}, M + "dragon_head")
mechanical("dragon_egg", ["EEEEE", "ESDSE", "EDNDE", "ESDSE", "EEEEE"],
           {"E": M + "end_stone", "S": M + "shulker_shell", "D": M + "dragon_head", "N": M + "nether_star"},
           M + "dragon_egg")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for name, r in sorted(R.items()):
        (OUT / f"{name}.json").write_text(json.dumps(r, indent=2) + "\n")
    print(f"wrote {len(R)} recipes to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
