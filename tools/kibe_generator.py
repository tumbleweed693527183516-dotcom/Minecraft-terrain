#!/usr/bin/env python3
"""
Writes the assets and data of the Cobblestone Generators (MK1-MK5) in the Vivid Lands: Ragnarok mod.

The generators are ported from Kibe by lucaargolo (https://github.com/lucaargolo/kibe, MPL-2.0): same tiers,
rates, recipes and textures. Only the cobblestone generator is taken from Kibe; nothing else.

    python3 tools/kibe_generator.py [path to a Kibe checkout, for the textures]
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "ragnarok" / "src" / "main" / "resources"
NS = "vividlands_ragnarok"
TIERS = [  # (tier, upgrade block, cobblestone per second)
    (1, None, 0.2), (2, "minecraft:gold_block", 0.8), (3, "minecraft:diamond_block", 3.2),
    (4, "minecraft:emerald_block", 12.8), (5, "minecraft:netherite_block", 51.2)]


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def main():
    lang = {}
    for tier, upgrade, rate in TIERS:
        n = f"cobblestone_generator_mk{tier}"
        write(RES / f"assets/{NS}/blockstates/{n}.json", {"variants": {"": {"model": f"{NS}:block/{n}"}}})
        write(RES / f"assets/{NS}/models/block/{n}.json", {
            "parent": "minecraft:block/cube",
            "textures": {"north": f"{NS}:block/{n}", "east": f"{NS}:block/{n}", "south": f"{NS}:block/{n}",
                         "west": f"{NS}:block/{n}", "up": f"{NS}:block/machine_top_mk{tier}",
                         "down": f"{NS}:block/machine_bottom_mk{tier}",
                         "particle": f"{NS}:block/machine_bottom_mk{tier}"}})
        write(RES / f"assets/{NS}/models/item/{n}.json", {"parent": f"{NS}:block/{n}"})
        write(RES / f"data/{NS}/loot_tables/blocks/{n}.json", {
            "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:{n}"}],
                                                  "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
        if upgrade is None:
            recipe = {"type": "minecraft:crafting_shaped", "pattern": ["###", "WIL", "#C#"],
                      "key": {"#": {"item": "minecraft:cobblestone"}, "W": {"item": "minecraft:water_bucket"},
                              "I": {"item": "minecraft:iron_block"}, "L": {"item": "minecraft:lava_bucket"},
                              "C": {"item": "minecraft:chest"}},
                      "result": {"item": f"{NS}:{n}"}}
        else:
            recipe = {"type": "minecraft:crafting_shaped", "pattern": [" # ", "#G#", " # "],
                      "key": {"#": {"item": f"{NS}:cobblestone_generator_mk{tier - 1}"}, "G": {"item": upgrade}},
                      "result": {"item": f"{NS}:{n}"}}
        write(RES / f"data/{NS}/recipes/generators/{n}.json", recipe)
        lang[f"block.{NS}.{n}"] = f"Cobblestone Generator MK{tier}"
        lang[f"tooltip.{NS}.{n}"] = f"Generates {rate:g} Cobblestone per second"
    lang["container.vividlands_ragnarok.cobblestone_generator"] = "Cobblestone Generator"
    write(RES / f"assets/{NS}/lang/en_us.json", lang)
    write(RES / "data/minecraft/tags/blocks/mineable/pickaxe.json",
          {"replace": False, "values": [f"{NS}:cobblestone_generator_mk{t}" for t, _, _ in TIERS]})

    if len(sys.argv) > 1:   # copy Kibe's textures (MPL-2.0) from a checkout
        src = Path(sys.argv[1]) / "src/main/resources/assets/kibe/textures/block"
        dst = RES / f"assets/{NS}/textures/block"
        dst.mkdir(parents=True, exist_ok=True)
        for tier, _, _ in TIERS:
            for name in (f"cobblestone_generator_mk{tier}.png", f"cobblestone_generator_mk{tier}.png.mcmeta",
                         f"machine_top_mk{tier}.png", f"machine_bottom_mk{tier}.png"):
                if (src / name).exists():
                    shutil.copy(src / name, dst / name)
        shutil.copy(Path(sys.argv[1]) / "LICENSE", RES / f"assets/{NS}/KIBE_LICENSE_MPL-2.0.txt")
    print("cobblestone generator assets written")


if __name__ == "__main__":
    main()
