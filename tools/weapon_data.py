#!/usr/bin/env python3
"""
Data for the pack's weapons (Vivid Lands: Ragnarok): names, tooltips, Better Combat swing styles and recipes.
Stats are placeholders (set in weapon/Weapons.java) and will be balanced later.
Civilization weapons and the legendaries are boss rewards (no recipe yet; creative tab until the bosses exist).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "ragnarok/src/main/resources"
NS = "vividlands_ragnarok"

# id: (name, tooltip, Better Combat preset or None)
WEAPONS = {
    "bearded_axe": ("Bearded Axe", "Berserker · a cave-bear claw lashed beneath the head", "bettercombat:axe"),
    "wolf_seax": ("Wolf Seax", "Úlfheðinn · pattern-welded, with a bronze wolf-head pommel", "bettercombat:dagger"),
    "valkyrie_sword": ("Valkyrie Sword", "Valkyrie · winged guard, runes in the fuller", "bettercombat:sword"),
    "dane_axe": ("Jarl's Dane Axe", "Jarl of the Einherjar · Fáfnir's head at the toe", "bettercombat:heavy_axe"),
    "gungnir": ("Gungnir", "Odin's spear · Huginn and Muninn on the collar", "bettercombat:spear"),
    "fenrirs_fang": ("Fenrir's Fang", "Fenrir's own fang, still bound by a strand of Gleipnir", "bettercombat:claymore"),
    "round_shield": ("Viking Round Shield", "Painted linden planks, a domed iron boss, an arrow still stuck in it", None),
    "khopesh": ("Khopesh", "Egypt · the Eye of Horus in gold and lapis", "bettercombat:cutlass"),
    "guandao": ("Dragon Guandao", "China · a golden dragon swallowing the blade", "bettercombat:glaive"),
    "gladius": ("Gladius", "Rome · SPQR and a golden eagle pommel", "bettercombat:sword"),
    "kopis": ("Kopis", "Greece · a Greek key along the spine, an owl of Athena", "bettercombat:cutlass"),
    "macuahuitl": ("Macuahuitl", "Maya · obsidian teeth in a painted club", "bettercombat:mace"),
    "katana": ("Katana", "Japan · a wavy hamon and a dragon tsuba", "bettercombat:katana"),
    "zweihander": ("Flamberge Zweihänder", "Medieval Germany · a wavy blade with parrying hooks", "bettercombat:claymore"),
    "ragnarok": ("Ragnarök, Surtr's Blade", "The molten core of the fire giant's sword · Fenrir's Fang reforged",
                 "bettercombat:claymore"),
}

M = "minecraft:"
R = f"{NS}:"
RECIPES = {   # shapeless upgrades for the Viking weapons, from the same boss trophies as the armour
    "bearded_axe": [M + "iron_axe", R + "bear_pelt", R + "saber_fang"],
    "wolf_seax": [M + "iron_sword", R + "wolf_pelt", R + "eclipse_shard"],
    "valkyrie_sword": [M + "diamond_sword", R + "raven_feather", R + "raven_feather", R + "sleipnir_hair"],
    "dane_axe": [R + "bearded_axe", R + "dragon_gold", R + "dragon_gold", R + "serpent_scale"],
    "round_shield": [M + "shield", M + "red_dye", M + "bone_meal", M + "iron_ingot", M + "leather"],
    "ragnarok": [R + "fenrirs_fang", M + "netherite_ingot", M + "netherite_ingot", M + "magma_block", M + "blaze_rod",
                 R + "dragon_gold", R + "serpent_scale"],
}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def main():
    lang_file = RES / f"assets/{NS}/lang/en_us.json"
    lang = json.loads(lang_file.read_text()) if lang_file.exists() else {}
    for wid, (name, tip, preset) in WEAPONS.items():
        lang[f"item.{NS}.{wid}"] = name
        lang[f"tooltip.{NS}.weapon.{wid}"] = tip
        if preset:
            write(RES / f"data/{NS}/weapon_attributes/{wid}.json", {"parent": preset})
    for wid, ings in RECIPES.items():
        write(RES / f"data/{NS}/recipes/weapons/{wid}.json",
              {"type": "minecraft:crafting_shapeless", "category": "equipment",
               "ingredients": [{"item": i} for i in ings], "result": {"item": f"{NS}:{wid}"}})
    write(lang_file, lang)
    print("weapon data written")


if __name__ == "__main__":
    main()
