"""
Writes the real quest book for FTB Quests from quests.py / side_quests.py:

    pack/ftbquests/data.snbt, chapter_groups.snbt     book settings and the two chapter groups (Main Quest, Side Lines)
    pack/ftbquests/chapters/<chapter>.snbt            one file per chapter, all its quests inside
    ragnarok/.../assets/vividlands_ragnarok/textures/gui/quest_labels/   the section labels drawn on the chapter maps
    ragnarok/.../data/vividlands_ragnarok/advancements/quest/...         hidden advancements the book tracks

Tools/modpack.py puts pack/ftbquests into the modpack as config/ftbquests/quests. Every task is mapped to something
the game tracks (a kill, an item, a biome, a structure, a stat, an advancement our mod grants); what can't be tracked
becomes a checkbox the player ticks.

    python3 tools/questbook/build_quests.py
"""
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from quests import BOSS, MAIN, SIDE  # noqa: E402
from side_quests import CLASSES, CIVS, VIVID, ANIMALS, SETS, nice  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "pack/ftbquests"
ADV = ROOT / "ragnarok/src/main/resources/data/vividlands_ragnarok/advancements/quest"
NS = "vividlands_ragnarok"
H = "heracles:"
STATS = Counter()

# short names: the book's chapter list is narrow
GROUP = {"prologue": "Prologue", "chapter1": "I. Skadi's Hunt", "bridge": "Loki's Betrayal", "chapter2": "II. Odin's War",
         "epilogue": "Twilight Broken", "dwarves": "Dwarves' Forge", "paths": "Einherjar Paths", "armory": "Ancient Armory",
         "saga": "Wanderer's Saga", "dead": "Restless Dead", "forge": "Dwarves' Forge"}
FALLBACK_ICON = {"prologue": "minecraft:writable_book", "chapter1": "minecraft:bow", "bridge": "minecraft:golden_helmet",
                 "chapter2": "minecraft:netherite_sword", "epilogue": "minecraft:nether_star", "tutorial": "minecraft:book",
                 "forge": "create:cogwheel", "voyages": "smallships:oak_cog", "dead": "minecraft:skeleton_skull",
                 "bow": "minecraft:bow", "paths": f"{NS}:berserker_rune", "armory": "minecraft:iron_chestplate",
                 "kings": "minecraft:golden_helmet", "saga": "minecraft:compass", "bestiary": "minecraft:lead",
                 "hall": "minecraft:item_frame"}

# ------------------------------------------------------------------ what the game can track
BOSS_NAMES = {v[0].split(",")[0].lower(): k for k, v in BOSS.items()}
BOSS_NAMES.update({"the giant bull shark": "bull_shark", "the dire wolf alpha": "dire_wolf"})
CIV_KILLS = {"bjorn ironside": "nordic_boss", "king bjorn ironside": "nordic_boss", "loki": "boss_loki"}
for c, name, lid, leader, gid, god, _ in CIVS:
    CIV_KILLS[leader.lower()] = lid
    CIV_KILLS[god.lower()] = gid
STRUCT = {"Find a Draugr Tower": "mebahelcreaturesdraugr:draugr_tower", "Find a Draugr Fort": "mebahelcreaturesdraugr:draugr_fort",
          "Find a Draugr Bastion": "mebahelcreaturesdraugr:draugr_bastion", "Find a Draugr Crypt": "mebahelcreaturesdraugr:draugr_crypt",
          "Find a Mayan site": "ancientstructures:mayan_temple", "Find a Roman site": "ancientstructures:roman_temple",
          "Find a Japanese site": "ancientstructures:japanese_temple", "Find a German site": "ancientstructures:german_town",
          "Find a Mayan temple (Ancient Structures)": "ancientstructures:mayan_temple", "Find a stronghold": "betterstrongholds:stronghold",
          "Find the stronghold portal room": "betterstrongholds:stronghold", "Loot a Pirate Junk": "dungeons_arise_seven_seas:pirate_junk",
          "Loot a Corsair Corvette": "dungeons_arise_seven_seas:corsair_corvette",
          "Loot a Victorious or Unicorn Galleon": "dungeons_arise_seven_seas:unicorn_galleon",
          "Board a pirate ship": "dungeons_arise_seven_seas:pirate_junk",
          "Reach a Civilizations Norse settlement": "civilizations:nordic", "Visit a Civilizations settlement": "civilizations:nordic"}
for c, name, *_ in CIVS:
    STRUCT[f"Visit the {name} settlement"] = f"civilizations:{c}"
ITEMS = {
    "Craft a bed": ("#minecraft:beds", 1), "Craft a chest": ("minecraft:chest", 1), "Find or craft a waystone": ("waystones:waystone", 1),
    "Craft a shield": ("minecraft:shield", 1), "16 arrows": ("minecraft:arrow", 16), "Bring milk for poison": ("minecraft:milk_bucket", 1),
    "Diamond horse armor": ("minecraft:diamond_horse_armor", 1), "Craft a netherite chestplate (Create forge line)": ("minecraft:netherite_chestplate", 1),
    "Craft a Traveler's Backpack": ("travelersbackpack:standard", 1), "Craft 32 andesite alloy": ("create:andesite_alloy", 32),
    "Craft 16 shafts": ("create:shaft", 16), "Place a water wheel": ("create:water_wheel", 1), "Craft a gearbox": ("create:gearbox", 1),
    "Craft a clutch": ("create:clutch", 1), "Craft a gearshift": ("create:gearshift", 1), "Craft Engineer's Goggles": ("create:goggles", 1),
    "Craft a millstone": ("create:millstone", 1), "Mill wheat into flour": ("create:wheat_flour", 1), "Press 16 iron sheets": ("create:iron_sheet", 16),
    "Build a pair of crushing wheels": ("create:crushing_wheel", 2), "Build a mechanical mixer over a basin": ("create:mechanical_mixer", 1),
    "Make 16 brass ingots in a heated basin": ("create:brass_ingot", 16), "Craft a deployer": ("create:deployer", 1),
    "Make a precision mechanism": ("create:precision_mechanism", 1), "Place 16 mechanical belts": ("create:belt_connector", 16),
    "Craft a mechanical arm": ("create:mechanical_arm", 1), "Craft 9 mechanical crafters": ("create:mechanical_crafter", 9),
    "Craft a packager": ("create:packager", 1), "Deliver a package by frogport": ("create:package_frogport", 1),
    "Order items from a stock keeper": ("create:stock_ticker", 1), "Mix 32 netherrack": ("minecraft:netherrack", 32),
    "Make 16 nether quartz": ("minecraft:quartz", 16), "Make 16 soul sand": ("minecraft:soul_sand", 16), "Mix nether wart": ("minecraft:nether_wart", 1),
    "Grow 16 nether wart": ("minecraft:nether_wart", 16), "Make 8 blaze rods": ("minecraft:blaze_rod", 8), "Make glowstone dust": ("minecraft:glowstone_dust", 1),
    "Make magma cream": ("minecraft:magma_cream", 1), "Mix 16 end stone": ("minecraft:end_stone", 16), "Craft an elytra (pack recipe)": ("minecraft:elytra", 1),
    "Mine tin": ("mythicmetals:raw_tin", 1), "Mine silver": ("mythicmetals:raw_silver", 1), "Forge 16 bronze": ("mythicmetals:bronze_ingot", 16),
    "Forge 16 steel": ("mythicmetals:steel_ingot", 16), "Mine mythril": ("mythicmetals:raw_mythril", 1), "Craft a mythril pickaxe": ("mythicmetals:mythril_pickaxe", 1),
    "Mine adamantite": ("mythicmetals:raw_adamantite", 1), "Mine orichalcum": ("mythicmetals:raw_orichalcum", 1), "Forge hallowed": ("mythicmetals:hallowed_ingot", 1),
    "Forge celestium": ("mythicmetals:celestium_ingot", 1), "Forge star platinum": ("mythicmetals:star_platinum", 1),
    "Make netherite scrap by superheated mixing": ("minecraft:netherite_scrap", 1), "Craft a netherite ingot": ("minecraft:netherite_ingot", 1),
    "Craft a netherite upgrade template": ("minecraft:netherite_upgrade_smithing_template", 1), "Build a cog (Small Ships)": ("#smallships:cogs", 1),
    "Build a brigg": ("#smallships:briggs", 1), "Build a galley": ("#smallships:galleys", 1), "Build a drakkar": ("#smallships:drakkars", 1),
    "Craft a ship cannon": ("smallships:cannon", 1), "Build a Small Ships boat (Njord's Voyages line)": ("#smallships:ships", 1),
    "Craft a bow": ("minecraft:bow", 1), "Craft a crossbow": ("minecraft:crossbow", 1), "Hand in the Frozen Heart": (f"{NS}:frozen_heart", 1, True),
    "Craft a Simply Swords weapon": ("#simplyswords:simply_swords", 1),
}
ACT_TROPHIES = {
    "Hand in all 5 Act I trophies": ["bear_pelt", "wolf_pelt", "great_antlers", "terror_claw", "bison_horn"],
    "Hand in all 5 Act II trophies": ["hippo_hide", "komodo_venom", "croc_scales", "lion_mane", "saber_fang"],
    "Hand in all 5 Act III trophies": ["eagle_feather", "anaconda_skin", "silverback_fist", "glyptodon_plate", "walrus_tusk"],
}
ADVS = {"Use any class rune stone": "class/use_rune", "Use it": "class/use_rune", "Reach level 5 in any class": "class/any_5",
        "Reach level 10 in two classes": "class/two_10", "Reach level 20 in all five classes": "class/all_20",
        "Survive a killing blow with Undying Rage": "class/berserker_ability_4", "Stagger any boss": "boss/staggered",
        "Wear a full ancient set": "armor/full_set", "Have a full-set bonus active": "armor/full_set",
        "Hit a boss while your ward matches it": "armor/ward_matched", "Defeat a boss while two stages behind on ward": "boss/underdressed"}
ABILITY = {}
for cid, title, god, mat, abil, lines in CLASSES:
    for k, a in enumerate(abil):
        ABILITY[a] = f"class/{cid}_ability_{k + 1}"
STAT_TASKS = {"Defeat any boss": (f"{NS}:bosses_killed", 1), "Defeat any boss a second time": (f"{NS}:bosses_killed", 2),
              "Defeat 10 bosses in total": (f"{NS}:bosses_killed", 10), "Defeat 50 bosses in total": (f"{NS}:bosses_killed", 50),
              "Stagger bosses 25 times": (f"{NS}:boss_staggers", 25), "Travel 5000 blocks": ("minecraft:walk_one_cm", 500000),
              "Travel 25000 blocks": ("minecraft:walk_one_cm", 2500000)}
VIVID_NICE = {nice(b): b for b in VIVID}


def icon(item):
    return {"type": H + "item", "item": item}


def task_for(text, ch, q, i):
    """One task dict for a task line, plus the item it is about (for the quest icon)."""
    tid = f"t{i}"
    base = {"title": text}
    if text in ACT_TROPHIES:
        return None, [dict(base, type=H + "item", title=nice(t), item=f"{NS}:{t}", amount=1, collection="MANUAL")
                      for t in ACT_TROPHIES[text]]
    if text in ITEMS:
        v = ITEMS[text]
        t = dict(base, type=H + "item", item=v[0], amount=v[1])
        if len(v) > 2:
            t["collection"] = "MANUAL"
        return (None if v[0].startswith("#") else v[0]), [t]
    m = re.match(r"Hand in 1 (.+)$", text)
    if m and ch == "hall":
        trophy = q["icon"][5:].split("/")[-1]
        return f"{NS}:{trophy}", [dict(base, type=H + "item", item=f"{NS}:{trophy}", amount=1, collection="MANUAL")]
    m = re.match(r"Craft the full (.+) set$", text)
    if m:
        sid = m.group(1).lower().replace(" ", "_")
        if sid in SETS:
            return f"{NS}:{sid}_helmet", [dict(base, type=H + "item", title=f"{m.group(1)} {p}", item=f"{NS}:{sid}_{p}", amount=1)
                                          for p in ("helmet", "chestplate", "leggings", "boots")]
    m = re.match(r"Craft the (\w+) Rune Stone", text)
    if m:
        return f"{NS}:{m.group(1).lower()}_rune", [dict(base, type=H + "item", item=f"{NS}:{m.group(1).lower()}_rune", amount=1)]
    if text in STRUCT:
        return None, [dict(base, type=H + "structure", structures=STRUCT[text])]
    m = re.match(r"Visit (.+)$", text)
    if m and m.group(1) in VIVID_NICE:
        return None, [dict(base, type=H + "biome", biomes=f"vividlands:{VIVID_NICE[m.group(1)]}")]
    if text == "Travel to a pine or boreal forest":
        return None, [dict(base, type=H + "biome", biomes="vividlands:boreal_snowwoods")]
    if text in ADVS:
        return None, [dict(base, type=H + "advancement", advancements=[f"{NS}:quest/{ADVS[text]}"])]
    m = re.match(r"Reach (\w+) level (\d+)$", text)
    if m:
        return None, [dict(base, type=H + "advancement", advancements=[f"{NS}:quest/class/{m.group(1).lower()}_{m.group(2)}"])]
    m = re.match(r"Use (.+)$", text)
    if m and m.group(1) in ABILITY:
        return None, [dict(base, type=H + "advancement", advancements=[f"{NS}:quest/{ABILITY[m.group(1)]}"])]
    if text in STAT_TASKS:
        s, n = STAT_TASKS[text]
        return None, [dict(base, type=H + "stat", stat=s, target=n)]
    m = re.match(r"Kill (a|\d+) draugr$", text)
    if m:
        n = 1 if m.group(1) == "a" else int(m.group(1))
        return None, [dict(base, type=H + "kill_entity", entity={"type": "mebahelcreaturesdraugr:draugr"}, amount=n)]
    m = re.match(r"Defeat (the )?(.+?)( \(Civilizations\)| from a ship| twice| with a tamed wolf alive)?$", text)
    if m:
        who = m.group(2).lower()
        n = 2 if m.group(3) == " twice" else 1
        if who in BOSS_NAMES or f"the {who}" in BOSS_NAMES:
            b = BOSS_NAMES.get(who) or BOSS_NAMES[f"the {who}"]
            return f"{NS}:{BOSS[b][5].split('/')[-1]}", [dict(base, type=H + "kill_entity", entity={"type": f"{NS}:{b}"}, amount=n,
                                                              icon=f"{NS}:{BOSS[b][5].split('/')[-1]}")]
        if who in CIV_KILLS:
            return None, [dict(base, type=H + "kill_entity", entity={"type": f"civilizations:{CIV_KILLS[who]}"}, amount=n)]
        if who == "draugr overlord":
            return None, [dict(base, type=H + "kill_entity", entity={"type": "mebahelcreaturesdraugr:draugr_overlord"}, amount=n)]
    STATS["check"] += 1
    return None, [dict(base, type=H + "check")]


REWARD_ITEMS = {"Map": ("minecraft:map", 1), "8 bread": ("minecraft:bread", 8), "Glamour Template": (f"{NS}:glamour_template", 1),
                "Glamour Template x2": (f"{NS}:glamour_template", 2), "Glamour Template x4": (f"{NS}:glamour_template", 4),
                "16 torches": ("minecraft:torch", 16), "Iron sword": ("minecraft:iron_sword", 1), "2 warp stones": ("waystones:warp_stone", 2),
                "Spyglass": ("minecraft:spyglass", 1), "16 arrows": ("minecraft:arrow", 16), "32 arrows": ("minecraft:arrow", 32),
                "Compass": ("minecraft:compass", 1), "A waystone": ("waystones:waystone", 1), "Raven Feather": (f"{NS}:raven_feather", 1),
                "Fenrir's Fang": (f"{NS}:fenrirs_fang", 1), "Wrench": ("create:wrench", 1), "8 shafts": ("create:shaft", 8),
                "4 cogwheels": ("create:cogwheel", 4), "16 dough": ("create:dough", 16), "16 brass ingots": ("create:brass_ingot", 16),
                "Brass hand": ("create:brass_hand", 1), "3 precision mechanisms": ("create:precision_mechanism", 3),
                "Brewing stand": ("minecraft:brewing_stand", 1), "Elytra": ("minecraft:elytra", 1), "Stressometer": ("create:stressometer", 1),
                "4 water wheels": ("create:water_wheel", 4), "Steam engine": ("create:steam_engine", 1), "Basin": ("create:basin", 1),
                "Train controls": ("create:controls", 1), "Totem of undying": ("minecraft:totem_of_undying", 1),
                "Netherite upgrade template": ("minecraft:netherite_upgrade_smithing_template", 1), "16 wool": ("minecraft:white_wool", 16),
                "16 cannonballs": ("smallships:cannon_ball", 16), "Mythril pickaxe": ("mythicmetals:mythril_pickaxe", 1),
                "Leather armor": ("minecraft:leather_chestplate", 1), "8 potions of fire resistance": ("minecraft:potion", 1),
                "Emeralds": ("minecraft:emerald", 8), "Healing potions": ("minecraft:golden_carrot", 8)}
TIER = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}


def rewards_for(q):
    out, tier = {}, 0
    for i, r in enumerate(q.get("rewards", [])):
        m = re.match(r"Rune Pouch \((\w+)\)", r)
        if m:
            tier = max(tier, TIER[m.group(1)])
            out[f"r{i}"] = {"type": H + "loottable", "loot_table": f"{NS}:rune_pouch/{m.group(1)}"}
        elif r in REWARD_ITEMS:
            item, n = REWARD_ITEMS[r]
            out[f"r{i}"] = {"type": H + "item", "item": {"id": item, "count": n}}
        elif r == "Agamemnon's set":
            for p in ("helmet", "chestplate", "leggings", "boots"):
                out[f"r{i}{p}"] = {"type": H + "item", "item": {"id": f"{NS}:agamemnon_{p}", "count": 1}}
        elif r == "Wolf Pelt x2":
            out[f"r{i}"] = {"type": H + "item", "item": {"id": f"{NS}:wolf_pelt", "count": 2}}
        else:
            STATS["reward_text"] += 1
    xp = {0: 50, 1: 50, 2: 120, 3: 250, 4: 450, 5: 800}[tier]
    if q["kind"] in ("boss", "boss2"):
        xp = max(xp, 200)
    if q["kind"] == "gift":
        xp = max(xp, 300)
    out["class_xp"] = {"type": H + "command", "command": f"ragnarok class xp {xp}"}
    return out, xp


def description(q):
    lines = [q["text"], ""]
    if q["kind"] == "boss":
        name, hp, where, unlock, drop, ic, moves, p2, tip = BOSS[q["id"]]
        lines += [f"Where: {where}", f"Health: {hp}", f"Spawns after: {unlock}", f"Moves: {moves}", f"Phase 2: {p2}", "", f"Tip: {tip}"]
    texts = [r for r in q.get("rewards", []) if not r.startswith("Rune Pouch") and r not in REWARD_ITEMS]
    if texts:
        lines += ["", "Also: " + "; ".join(texts)]
    return lines


# ------------------------------------------------------------------ chapter links (the main line runs on)
CHAIN = {"a1": ["p6"], "b1": ["g4"], "c1": ["b4"], "e1": ["fenrir"]}
ACTS = [("Act I · Forest and Plain", 0), ("Act II · Rivers and Claws", 2.6), ("Act III · The Far Lands", 5.2), ("Act IV · The Titans", 7.8)]
SX, SY = 1.75, 1.6          # FTB grid units per layout unit
TAG_ADV = {}                # "#ns:tag" -> advancement path (for "have any item of a tag" tasks)


# ------------------------------------------------------------------ SNBT (the FTB Quests file format)
class D(float):
    """A double, written as 1.5d."""


class L(int):
    """A long, written as 5L."""


class B(int):
    """A byte, written as 1b."""


def snbt(v, ind=0):
    pad = "\t" * ind
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, D):
        return f"{float(v)!r}d"
    if isinstance(v, L):
        return f"{int(v)}L"
    if isinstance(v, B):
        return f"{int(v)}b"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, list):
        if not v:
            return "[ ]"
        return "[\n" + "\n".join(pad + "\t" + snbt(x, ind + 1) for x in v) + "\n" + pad + "]"
    if isinstance(v, dict):
        if not v:
            return "{ }"
        return "{\n" + "\n".join(f"{pad}\t{k}: {snbt(x, ind + 1)}" for k, x in sorted(v.items())) + "\n" + pad + "}"
    raise TypeError(v)


def fid(key):
    """Stable 16-hex-digit FTB object id from a name."""
    import hashlib
    h = hashlib.sha1(("vividlands:" + key).encode()).hexdigest()[:16].upper()
    return ("1" + h[1:]) if h[0] == "0" else h


def stack(item, count=1):
    return {"id": item, "Count": B(count)}


# ------------------------------------------------------------------ Heracles-style task/reward dicts -> FTB
def ftb_task(key, t):
    ty = t["type"][len(H):]
    out = {"id": fid(key)}
    if t.get("title"):
        out["title"] = t["title"]
    if ty == "item":
        if t["item"].startswith("#"):
            tag = t["item"][1:]
            path = "has/" + tag.replace(":", "_").replace("/", "_")
            TAG_ADV[tag] = path
            out.update(type="advancement", advancement=f"{NS}:quest/{path}", criterion="")
        else:
            out.update(type="item", item=stack(t["item"]))
            if t.get("amount", 1) > 1:
                out["count"] = L(t["amount"])
            if t.get("collection") == "MANUAL":
                out["consume_items"] = True
    elif ty == "kill_entity":
        out.update(type="kill", entity=t["entity"]["type"], value=L(t["amount"]))
        if t.get("icon"):
            out["icon"] = stack(t["icon"])
    elif ty == "biome":
        out.update(type="biome", biome=t["biomes"])
    elif ty == "structure":
        out.update(type="structure", structure=t["structures"])
    elif ty == "advancement":
        out.update(type="advancement", advancement=t["advancements"][0], criterion="")
    elif ty == "stat":
        out.update(type="stat", stat=t["stat"], value=t["target"])
    elif ty == "check":
        out.update(type="checkmark")
    else:
        raise ValueError(ty)
    return out


POUCH_ICON = {"common": "minecraft:chest", "uncommon": "minecraft:chest", "rare": "minecraft:barrel",
              "epic": "minecraft:ender_chest", "legendary": "minecraft:ender_chest"}


def ftb_reward(key, r):
    ty = r["type"][len(H):]
    out = {"id": fid(key)}
    if ty == "item":
        out.update(type="item", item=stack(r["item"]["id"]))
        if r["item"]["count"] > 1:
            out["count"] = r["item"]["count"]
    elif ty == "loottable":
        tier = r["loot_table"].split("/")[-1]
        out.update(type="command", command=f"/loot give @s loot {r['loot_table']}", elevate_perms=True, silent=True,
                   title=f"Rune Pouch ({tier.title()})", icon=stack(POUCH_ICON[tier]))
    elif ty == "command":
        n = r["command"].split()[-1]
        out.update(type="command", command="/" + r["command"], elevate_perms=True, silent=True,
                   title=f"{n} class XP", icon=stack("minecraft:experience_bottle"))
    else:
        raise ValueError(ty)
    return out


def ftb_text(line):
    """FTB reads & as a colour code and a leading { or [ as JSON; keep our text literal."""
    line = line.replace("&", "and")
    return (" " + line) if line[:1] and line[:1] in "{[" else line


# ------------------------------------------------------------------ section labels: little pixel-font images on the map
FONT = {  # 5x7, rows top to bottom, '#' = ink
    "A": ".###.#...##...#######...##...##...#", "B": "####.#...##...#####.#...##...#####.", "C": ".###.#...##....#....#....#...#.###.",
    "D": "####.#...##...##...##...##...#####.", "E": "######....#....####.#....#....#####", "F": "######....#....####.#....#....#....",
    "G": ".###.#...##....#.####...##...#.####", "H": "#...##...##...#######...##...##...#", "I": ".###...#....#....#....#....#...###.",
    "J": "..###...#....#....#....#.#..#..##..", "K": "#...##..#.#.#..##...#.#..#..#.#...#", "L": "#....#....#....#....#....#....#####",
    "M": "#...###.###.#.##.#.##...##...##...#", "N": "#...###..##.#.##..###...##...##...#", "O": ".###.#...##...##...##...##...#.###.",
    "P": "####.#...##...#####.#....#....#....", "Q": ".###.#...##...##...##.#.##..#..##.#", "R": "####.#...##...#####.#.#..#..#.#...#",
    "S": ".#####....#.....###.....#....#####.", "T": "#####..#....#....#....#....#....#..", "U": "#...##...##...##...##...##...#.###.",
    "V": "#...##...##...##...##...#.#.#...#..", "W": "#...##...##...##.#.##.#.##.#.#.#.#.", "X": "#...##...#.#.#...#...#.#.#...##...#",
    "Y": "#...##...#.#.#...#....#....#....#..", "Z": "#####....#...#...#...#...#....#####",
    "0": ".###.#...##..###.#.###..##...#.###.", "1": "..#...##....#....#....#....#...###.", "2": ".###.#...#....#...#...#...#...#####",
    "3": ".###.#...#....#..##.....##...#.###.", "4": "...#...##..#.#.#..#.#####...#....#.", "5": "######....####.....#....##...#.###.",
    "6": "..##..#...#....####.#...##...#.###.", "7": "#####....#...#...#...#....#....#...", "8": ".###.#...##...#.###.#...##...#.###.",
    "9": ".###.#...##...#.####....#...#..##..", " ": "." * 35, ":": "......##...##........##...##.......",
    "'": "..#....#...#.......................", "·": ".................#.................", ".": "..............................##...",
    "-": "................###................", ",": "...........................##...#..", "&": ".##..#..#.#.#...#...#.#.##..#..##.#",
    "(": "...#...#...#....#....#.....#.....#.", ")": ".#.....#.....#....#....#...#...#...", "/": "....#...#...#...#...#...#....#.....",
}
LABEL_DIR = ROOT / "ragnarok/src/main/resources/assets/vividlands_ragnarok/textures/gui/quest_labels"


def label_image(name, text):
    """Gold pixel text with a fading rule after it; returns (texture id, width/height ratio)."""
    from PIL import Image
    text = text.upper()
    w = sum(6 for _ in text) + 3 + 60
    img = Image.new("RGBA", (w + 2, 11), (0, 0, 0, 0))
    gold, shade = (224, 182, 90, 255), (12, 17, 22, 200)
    x = 1
    for c in text:
        g = (FONT.get(c) or FONT[" "]).ljust(35, ".")
        for i, ch in enumerate(g[:35]):
            if ch == "#":
                px, py = x + i % 5, 2 + i // 5
                img.putpixel((px + 1, py + 1), shade)
                img.putpixel((px, py), gold)
        x += 6
    x += 3
    for k in range(60):  # the rule fades out
        a = int(200 * (1 - k / 60))
        img.putpixel((x + k, 5), (168, 121, 58, a))
    LABEL_DIR.mkdir(parents=True, exist_ok=True)
    img.save(LABEL_DIR / f"{name}.png")
    return f"{NS}:textures/gui/quest_labels/{name}.png", img.width / img.height


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    if LABEL_DIR.exists():
        shutil.rmtree(LABEL_DIR)
    (OUT / "chapters").mkdir(parents=True)
    group_ids = {"main": fid("group/main"), "side": fid("group/side")}
    (OUT / "chapter_groups.snbt").write_text(snbt({"chapter_groups": [
        {"id": group_ids["main"], "title": "Main Quest", "icon": stack("minecraft:writable_book")},
        {"id": group_ids["side"], "title": "Side Lines", "icon": stack("minecraft:map")}]}) + "\n")
    (OUT / "data.snbt").write_text(snbt({
        "version": 13, "title": "Vivid Lands: Ragnarok", "icon": stack("minecraft:writable_book"),
        "default_reward_team": False, "default_consume_items": False, "default_autoclaim_rewards": "disabled",
        "default_quest_shape": "square", "default_quest_disable_jei": False, "emergency_items_cooldown": 300,
        "drop_loot_crates": False, "disable_gui": False, "grid_scale": D(0.5), "pause_game": False, "lock_message": "",
        "progression_mode": "linear", "detection_delay": 20, "show_lock_icons": True, "drop_book_on_death": False}) + "\n")
    total, order = 0, 0
    for group, chapters in (("main", MAIN), ("side", SIDE)):
        for ch in chapters:
            gname = GROUP.get(ch["id"], ch["name"])
            fname = re.sub(r"[^a-z0-9]+", "_", gname.lower()).strip("_")
            quests, images = [], []
            labels = ACTS if ch.get("acts") else (ch.get("labels") or [])
            for k, (text, ly) in enumerate(labels):
                tex, ratio = label_image(f"{ch['id']}_{k}", text)
                h = 0.42
                images.append({"x": D(round(-0.6 + h * ratio / 2, 3)), "y": D(round(ly * SY + 0.1, 3)), "width": D(round(h * ratio, 3)),
                               "height": D(h), "rotation": D(0.0), "image": tex})
            for q in ch["quests"]:
                q = dict(q)
                if q["kind"] == "boss":
                    b = BOSS[q["id"]]
                    q.update(title=b[0].split(",")[0], subtitle=b[0].split(", ", 1)[1] if ", " in b[0] else "",
                             tasks=[], rewards=[], icon="item:" + b[5])
                tasks, main_item = [], None
                if q["kind"] == "boss":
                    tasks.append(ftb_task(f"{q['id']}/kill", {"type": H + "kill_entity", "title": f"Defeat the {q['title']}",
                                                             "entity": {"type": f"{NS}:{q['id']}"}, "amount": 1}))
                    tasks[-1]["icon"] = stack(f"{NS}:{BOSS[q['id']][5].split('/')[-1]}")  # bosses have no spawn egg
                for i, t in enumerate(q["tasks"]):
                    item, ts = task_for(t, ch["id"], q, i)
                    main_item = main_item or item
                    for k, td in enumerate(ts):
                        tasks.append(ftb_task(f"{q['id']}/t{i}_{k}", td))
                rewards, xp = rewards_for(q)
                ic = q["icon"]
                item_icon = f"{NS}:{ic[5:].split('/')[-1]}" if ic.startswith("item:") else (main_item or FALLBACK_ICON.get(ch["id"], "minecraft:book"))
                y = q["y"] + (0.6 if ch.get("acts") else 0)
                if ch.get("acts"):
                    y += 0.4 * int((q["y"] + 0.1) // 2.2)
                deps = list(q["deps"]) + CHAIN.get(q["id"], [])
                kind = q["kind"]
                quest = {"id": fid("quest/" + q["id"]), "title": ftb_text(q["title"]), "icon": stack(item_icon),
                         "x": D(round(q["x"] * SX, 3)), "y": D(round(y * SY, 3)),
                         "description": [ftb_text(l) for l in description(q)], "tags": [kind, "q_" + q["id"]],
                         "tasks": tasks, "rewards": [ftb_reward(f"{q['id']}/{rk}", r) for rk, r in rewards.items()]}
                if q.get("subtitle"):
                    quest["subtitle"] = ftb_text(q["subtitle"])
                if deps:
                    quest["dependencies"] = [fid("quest/" + d) for d in deps]
                if kind in ("boss", "boss2"):
                    quest.update(shape="circle", size=D(1.5))
                elif kind == "gift":
                    quest.update(shape="diamond", size=D(1.25))
                if q.get("edge", "solid") == "none":
                    quest["hide_dependency_lines"] = True
                quests.append(quest)
                total += 1
                STATS[kind] += 1
            chapter = {"id": fid("chapter/" + ch["id"]), "group": group_ids[group], "order_index": order, "filename": fname,
                       "title": gname, "icon": stack(FALLBACK_ICON.get(ch["id"], "minecraft:book")),
                       "default_quest_shape": "", "default_hide_dependency_lines": False, "quest_links": [], "quests": quests}
            sub = ch["sub"] if gname != ch["sub"] and not gname.endswith(ch["sub"]) else ""
            if sub:
                chapter["subtitle"] = [ftb_text(sub)]
            if images:
                chapter["images"] = images
            (OUT / "chapters" / f"{fname}.snbt").write_text(snbt(chapter) + "\n")
            order += 1
    return total




def advancements():
    """Hidden advancements (no display, no toast) that the mod grants and the book checks."""
    if ADV.exists():
        shutil.rmtree(ADV)
    paths = ["class/use_rune", "class/any_5", "class/two_10", "class/all_20", "boss/staggered", "boss/underdressed",
             "armor/full_set", "armor/ward_matched"]
    for cid, *_ in CLASSES:
        paths += [f"class/{cid}_{lv}" for lv in (1, 5, 10, 20, 35, 50)]
        paths += [f"class/{cid}_ability_{k}" for k in range(1, 5)]
    for p in paths:
        f = ADV / f"{p}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"criteria": {"done": {"trigger": "minecraft:impossible"}}}) + "\n")
    for tag, p in TAG_ADV.items():  # "have any item of this tag" (FTB item tasks can't take a tag on their own)
        f = ADV / f"{p}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"criteria": {"has": {"trigger": "minecraft:inventory_changed",
                                                      "conditions": {"items": [{"tag": tag}]}}}}) + "\n")
    return len(paths) + len(TAG_ADV)


if __name__ == "__main__":
    n = build()
    a = advancements()
    print(n, "quests,", a, "advancements;", dict(STATS))
