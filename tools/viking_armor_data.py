#!/usr/bin/env python3
"""
Data for the Viking endgame armor in Vivid Lands: Ragnarok: item models, recipes, names and tooltips.
(The 3D models and textures come from tools/concept/export_geckolib.py.)

Recipes: each set is made from its bosses' trophies; from tier 2 on, the previous tier's piece goes in the middle,
so the sets are upgraded one into the next.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "ragnarok/src/main/resources"
NS = "vividlands_ragnarok"

SETS = [  # id, display names (helmet, chest, legs, boots), primary trophy, secondary trophy, set line, bonus line
    ("berserker", ("Berserker Bear Hood", "Berserker Harness", "Berserker Leg Wraps", "Berserker Fur Boots"),
     "bear_pelt", "saber_fang", "Berserker set (tier 1)", "Full set: rage - Strength when below half health"),
    ("ulfhednar", ("Úlfheðinn Wolf Hood", "Úlfheðinn Hauberk", "Úlfheðinn Mail Skirt", "Úlfheðinn Turnshoes"),
     "wolf_pelt", "eclipse_shard", "Úlfheðinn set (tier 2)", "Full set: Speed, and Night Vision at night"),
    ("valkyrie", ("Valkyrie Winged Helm", "Valkyrie Scale Cuirass", "Valkyrie Tassets", "Valkyrie Sabatons"),
     "raven_feather", "sleipnir_hair", "Valkyrie set (tier 3)", "Full set: Jump Boost, and Slow Falling as you fall"),
    ("jarl", ("Jarl's Spectacle Helm", "Jarl's Dragonscale Hauberk", "Jarl's Greaves", "Jarl's War Boots"),
     "serpent_scale", "dragon_gold", "Jarl of the Einherjar set (tier 4)", "Full set: Resistance and Fire Resistance"),
]
PIECES = ["helmet", "chestplate", "leggings", "boots"]
TROPHIES = {
    "bear_pelt": ("Cave Bear Pelt", "Dropped by the Cave Bear"),
    "saber_fang": ("Saber Fang", "Dropped by the Saber-tooth Cat"),
    "wolf_pelt": ("Pelt of Geri and Freki", "Dropped by Odin's wolves"),
    "eclipse_shard": ("Eclipse Shard", "Dropped by Sköll and Hati, who chase the sun and moon"),
    "raven_feather": ("Feather of Thought and Memory", "Dropped by Huginn and Muninn"),
    "sleipnir_hair": ("Sleipnir's Mane", "Earned from Sleipnir"),
    "dragon_gold": ("Fáfnir's Gold", "Dropped by Fáfnir"),
    "serpent_scale": ("Jörmungandr's Scale", "Dropped by the World Serpent"),
}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def item(i):
    return {"item": i if ":" in i else f"{NS}:{i}"}


def recipe(piece, prim, sec, prev):
    if piece == "helmet":
        pattern = ["PSP", "PXP"] if prev else ["PSP", "P P"]
    elif piece == "chestplate":
        pattern = ["PXP", "PSP", "PPP"] if prev else ["P P", "PSP", "PPP"]
    elif piece == "leggings":
        pattern = ["PSP", "PXP", "P P"] if prev else ["PSP", "P P", "P P"]
    else:
        pattern = ["PXP", "S S"] if prev else ["P P", "S S"]
    key = {"P": item(prim), "S": item(sec)}
    if prev:
        key["X"] = item(prev)
    return {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern, "key": key}


def main():
    lang_file = RES / f"assets/{NS}/lang/en_us.json"
    lang = json.loads(lang_file.read_text()) if lang_file.exists() else {}
    lang["itemGroup.vividlands_ragnarok"] = "Vivid Lands: Ragnarok"
    prev_set = None
    for sid, names, prim, sec, set_line, bonus in SETS:
        lang[f"tooltip.{NS}.set.{sid}"] = set_line
        lang[f"tooltip.{NS}.bonus.{sid}"] = bonus
        for piece, nm in zip(PIECES, names):
            iid = f"{sid}_{piece}"
            lang[f"item.{NS}.{iid}"] = nm
            write(RES / f"assets/{NS}/models/item/{iid}.json",
                  {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{iid}"}})
            r = recipe(piece, prim, sec, f"{prev_set}_{piece}" if prev_set else None)
            r["result"] = {"item": f"{NS}:{iid}"}
            write(RES / f"data/{NS}/recipes/armor/{iid}.json", r)
        prev_set = sid
    for tid, (nm, lore) in TROPHIES.items():
        lang[f"item.{NS}.{tid}"] = nm
        write(RES / f"assets/{NS}/models/item/{tid}.json",
              {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{tid}"}})
    write(lang_file, lang)
    print("viking armor data written")


if __name__ == "__main__":
    main()
