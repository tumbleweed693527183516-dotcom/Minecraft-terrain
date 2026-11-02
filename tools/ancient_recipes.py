"""
Crafting recipes for the 49 ancient armor sets (writes data/vividlands_ragnarok/recipes/ancient/ and trophy tags).

Each piece is the vanilla armor shape in the band's metal, with two extra slots: a dye that picks the set inside its
band, and a trophy from the bosses that band was made to beat. Bands follow the Boss Ward (armor/ArmorTraits.java).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "ragnarok/src/main/resources/data/vividlands_ragnarok"
SETS = re.findall(r'new Set\("(\w+)"', (ROOT / "ragnarok/src/main/java/com/vividlands/ragnarok/armor/AncientSets.java").read_text())
ACT = {
    "act1": ["bear_pelt", "wolf_pelt", "great_antlers", "terror_claw", "bison_horn"],
    "act2": ["hippo_hide", "komodo_venom", "croc_scales", "lion_mane", "saber_fang"],
    "act3": ["eagle_feather", "anaconda_skin", "silverback_fist", "glyptodon_plate", "walrus_tusk"],
    "act4": ["sloth_claw", "shark_tooth", "rhino_horn", "ivory", "mammoth_tusk"],
}
# (last tier of band, metal, trophy key: item or #tag)
BANDS = [
    (5, "minecraft:iron_ingot", {"item": "minecraft:leather"}),
    (15, "minecraft:iron_ingot", {"tag": "vividlands_ragnarok:trophies/act1"}),
    (25, "minecraft:diamond", {"tag": "vividlands_ragnarok:trophies/act2"}),
    (35, "minecraft:diamond", {"tag": "vividlands_ragnarok:trophies/act3"}),
    (40, "minecraft:diamond", {"tag": "vividlands_ragnarok:trophies/act4"}),
    (42, "minecraft:netherite_ingot", {"item": "vividlands_ragnarok:sleipnir_hair"}),
    (44, "minecraft:netherite_ingot", {"item": "vividlands_ragnarok:hel_key"}),
    (46, "minecraft:netherite_ingot", {"item": "vividlands_ragnarok:dragon_gold"}),
    (49, "minecraft:netherite_ingot", {"item": "vividlands_ragnarok:serpent_scale"}),
]
DYES = ["red", "blue", "yellow", "green", "white", "black", "purple", "orange", "cyan", "lime", "brown", "pink", "light_blue", "magenta", "gray", "light_gray"]
SHAPES = {"helmet": ["MTM", "MDM"], "chestplate": ["MDM", "MTM", "MMM"], "leggings": ["MMM", "MDM", "MTM"], "boots": ["MDM", "MTM"]}

out = DATA / "recipes/ancient"
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("*.json"):
    f.unlink()
start = 1
rows = []
for last, metal, trophy in BANDS:
    for k, sid in enumerate(SETS[start - 1:last]):
        dye = DYES[k]
        for piece, shape in SHAPES.items():
            r = {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": shape,
                 "key": {"M": {"item": metal}, "T": trophy, "D": {"item": f"minecraft:{dye}_dye"}},
                 "result": {"item": f"vividlands_ragnarok:{sid}_{piece}"}}
            (out / f"{sid}_{piece}.json").write_text(json.dumps(r, indent=2) + "\n")
        rows.append((start + k, sid, metal.split(":")[1], trophy.get("item", trophy.get("tag")).split(":")[1], dye))
    start = last + 1
tags = DATA / "tags/items/trophies"
tags.mkdir(parents=True, exist_ok=True)
for act, items in ACT.items():
    (tags / f"{act}.json").write_text(json.dumps({"replace": False, "values": [f"vividlands_ragnarok:{i}" for i in items]}, indent=2) + "\n")
print(len(rows), "sets,", len(list(out.glob('*.json'))), "recipes")
for r in rows:
    print(*r)
