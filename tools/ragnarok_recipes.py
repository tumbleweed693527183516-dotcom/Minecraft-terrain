#!/usr/bin/env python3
"""
Writes the Create recipes of the Vivid Lands: Ragnarok pack mod (ragnarok/src/main/resources/data).

The Nether and the End are closed in this pack, so everything they normally give can be made in
the Overworld with Create machines. Create already covers a lot (haunting: soul sand, soul soil,
blackstone, crimson/warped fungus, nether brick; crushing diorite -> quartz; filling cinder flour ->
glowstone; crushing netherrack -> cinder flour for blaze cakes). These recipes fill the gaps.

Progression, roughly:
  early   mixing sand + rotten flesh + bone meal -> the first soul sand (soul fire -> haunting fans)
          haunting: granite -> netherrack, beetroot seeds -> nether wart, skeleton skull -> wither
          skeleton skull, obsidian -> crying obsidian; deploying fungus on netherrack -> nylium
          (bone-meal fungus on nylium for stems, wart blocks, shroomlight, vines)
  middle  compacting stick + gold + lava -> blaze rod; empty blaze burner + 4 blaze rods -> blaze burner
          heated mixing: ghast tear, glowstone dust, dragon's breath, shulker shell
          end stone and chorus flowers (grow on end stone -> chorus fruit, purpur, end rods)
  late    superheated mixing -> netherite scrap; mechanical crafting -> netherite upgrade template,
          rib / snout / spire trims, elytra
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

# ---------------- Nether ----------------
processing("soul_sand_from_mixing", "mixing", ["#minecraft:sand", M + "rotten_flesh", M + "bone_meal"], [M + "soul_sand"])
processing("netherrack_from_haunting", "haunting", [M + "granite"], [M + "netherrack"])
processing("nether_wart_from_haunting", "haunting", [M + "beetroot_seeds"], [M + "nether_wart"])
processing("wither_skeleton_skull_from_haunting", "haunting", [M + "skeleton_skull"], [M + "wither_skeleton_skull"])
processing("crying_obsidian_from_haunting", "haunting", [M + "obsidian"], [M + "crying_obsidian"])
processing("crimson_nylium_from_deploying", "deploying", [M + "netherrack", M + "crimson_fungus"], [M + "crimson_nylium"])
processing("warped_nylium_from_deploying", "deploying", [M + "netherrack", M + "warped_fungus"], [M + "warped_nylium"])
processing("gilded_blackstone_from_deploying", "deploying", [M + "blackstone", M + "gold_ingot"], [M + "gilded_blackstone"])
processing("magma_block_from_compacting", "compacting", [M + "netherrack", fluid(M + "lava", 100)], [M + "magma_block"])
processing("blaze_rod_from_compacting", "compacting",
           [M + "stick", M + "gold_nugget", M + "gold_nugget", fluid(M + "lava", 250)], [M + "blaze_rod"])
shapeless("blaze_burner_from_blaze_rods", [C + "empty_blaze_burner"] + [M + "blaze_rod"] * 4, C + "blaze_burner")
processing("ghast_tear_from_mixing", "mixing", [M + "soul_sand", M + "phantom_membrane", fluid(M + "water", 250)],
           [M + "ghast_tear"], heat="heated")
processing("glowstone_dust_from_mixing", "mixing", [M + "redstone", M + "redstone", M + "glow_ink_sac"],
           [item(M + "glowstone_dust", 2)], heat="heated")
processing("netherite_scrap_from_mixing", "mixing",
           [M + "diamond", C + "crushed_raw_gold", C + "crushed_raw_gold", M + "blackstone", fluid(M + "lava", 500)],
           [M + "netherite_scrap"], heat="superheated")
processing("ancient_debris_from_compacting", "compacting", [M + "netherite_scrap", M + "blackstone"],
           [M + "ancient_debris"], heat="superheated")
mechanical("netherite_upgrade_smithing_template", ["DSD", "DND", "DDD"],
           {"D": M + "diamond", "S": M + "netherite_scrap", "N": M + "netherrack"},
           M + "netherite_upgrade_smithing_template")
mechanical("rib_armor_trim_smithing_template", ["DSD", "DBD", "DDD"],
           {"D": M + "diamond", "S": M + "wither_skeleton_skull", "B": M + "bone_block"},
           M + "rib_armor_trim_smithing_template")
mechanical("snout_armor_trim_smithing_template", ["DGD", "DBD", "DDD"],
           {"D": M + "diamond", "G": M + "gold_block", "B": M + "blackstone"},
           M + "snout_armor_trim_smithing_template")

# ---------------- End ----------------
processing("end_stone_from_mixing", "mixing", [M + "sandstone"] * 4 + [M + "ender_pearl"], [item(M + "end_stone", 4)])
processing("chorus_flower_from_mixing", "mixing", [M + "ender_pearl", M + "beetroot_seeds", M + "bone_meal"],
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


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for name, r in sorted(R.items()):
        (OUT / f"{name}.json").write_text(json.dumps(r, indent=2) + "\n")
    print(f"wrote {len(R)} recipes to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
