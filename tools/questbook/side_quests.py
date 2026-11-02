"""
Side quest lines, Prominence II style: every chapter is a set of branches (a tutorial spine, then progression
branches, collection grids and a capstone), rewards climb through Rune Pouch tiers.

Each chapter is built from branches: (label, parent quest key or None, mode, quests). mode "chain" links each quest
to the one before; "grid" hangs every quest off the branch parent (a collection). A quest is
(key, title, icon, text, tasks, rewards[, kind]).
"""

POUCH = {1: "Rune Pouch (common)", 2: "Rune Pouch (uncommon)", 3: "Rune Pouch (rare)", 4: "Rune Pouch (epic)",
         5: "Rune Pouch (legendary)"}


def P(n, *extra):
    return [POUCH[n], *extra]


W = 6          # quests per row before a chain wraps


def build(cid, name, sub, patron, tab, branches):
    quests, labels, keys = [], [], {}
    y = 0.0
    for label, parent, mode, items in branches:
        labels.append([label, y])
        row_y = y + 0.6
        prev = keys.get(parent) if parent else None
        for i, it in enumerate(items):
            key, title, icon, text, tasks, rewards = it[:6]
            kind = it[6] if len(it) > 6 else "quest"
            x, r = i % W, i // W
            if mode == "grid":
                deps = [keys[parent]] if parent else []
            else:
                deps = [prev] if prev else []
            qid = f"{cid}_{key}"
            # draw: grid members hide their link (one link to the grid's first member is enough); a branch's first
            # quest links back to another branch with a dashed line
            edge = "none" if mode == "grid" and i > 0 else "cross" if i == 0 and parent else "solid"
            quests.append({"id": qid, "x": x, "y": row_y + r * 1.15, "deps": deps, "kind": kind, "title": title,
                           "icon": icon, "text": text, "tasks": tasks, "rewards": rewards, "edge": edge})
            keys[key] = qid
            prev = qid
        rows = (len(items) + W - 1) // W
        y = row_y + (rows - 1) * 1.15 + 1.35
    return {"id": cid, "name": name, "sub": sub, "patron": patron, "tab": tab, "labels": labels, "quests": quests}


R = lambda r: "rune:" + r          # noqa: E731
I = lambda i: "item:" + i          # noqa: E731

# ======================================================================================== TUTORIALS
TUTORIAL = build("tutorial", "First Steps", "How the pack works", "Mimir", "Tutorials", [
    ("Finding your way", None, "chain", [
        ("book", "The Quest Book", R("ᚨ"), "Every chapter here is optional except the main quest. Side lines pay off in the boss fights.",
         ["Open the quest book"], P(1)),
        ("emi", "Look It Up", R("ᚨ"), "EMI shows every recipe in the pack, including the Create ones for Nether items.",
         ["Open EMI and look up a recipe (press R on an item)"], ["8 bread"]),
        ("jade", "What Is That?", R("ᚨ"), "Jade names whatever block or creature you look at, and which mod it comes from.",
         ["Look at a modded block with Jade"], ["4 torches"]),
        ("map", "The World Map", R("ᚱ"), "Xaero's map remembers everywhere you have been.",
         ["Open the world map (M)", "Set a waypoint"], ["Compass"]),
        ("way", "The Old Roads", R("ᚱ"), "Waystones link the world. Every one you find is one you never walk to again.",
         ["Activate a waystone", "Travel with a waystone"], ["2 warp stones", *P(1)]),
    ]),
    ("Surviving", "book", "chain", [
        ("grave", "Death Is a Detour", R("ᚺ"), "When you die, your things wait in a grave where you fell.",
         ["Read about graves (check this box)"], ["Totem-free advice"]),
        ("carry", "Carry On", R("ᚺ"), "Pick up chests and animals and carry them.",
         ["Pick up a chest with an empty hand while sneaking"], P(1)),
        ("pack", "A Traveler's Backpack", R("ᚺ"), "Bosses are far away. Bring more than your pockets hold.",
         ["Craft a Traveler's Backpack"], ["Sleeping bag", *P(1)]),
        ("food", "Know Your Food", R("ᚺ"), "AppleSkin shows how much a meal really fills you.",
         ["Eat 5 different foods"], ["16 cooked mutton"]),
    ]),
    ("Fighting", "book", "chain", [
        ("roll", "The Roll", R("ᛏ"), "Combat Roll lets you dodge. Bosses telegraph their big hits: roll out of the red rings.",
         ["Dodge-roll 10 times"], P(1)),
        ("swing", "Better Combat", R("ᛏ"), "Weapons swing in arcs and combos. Two-handed weapons hit everything in front of you.",
         ["Kill a mob with a two-handed weapon"], ["Iron sword"]),
        ("ward", "Boss Ward", I("berserker_helmet"), "Armor made for a boss's act halves its hits. Armor from two acts back makes them hurt more.",
         ["Read the armor guide (check this box)"], P(2)),
        ("stagger", "Strike While It Reels", R("ᛏ"), "Hit a boss hard and fast and it staggers: it takes 50% more damage until it recovers.",
         ["Stagger any boss"], P(2), "boss2"),
    ]),
])

# ======================================================================================== THE DWARVES' FORGE (Create, Mythic Metals, Alloy Forgery)
FORGE = build("forge", "The Dwarves' Forge", "Create, Mythic Metals, Alloy Forgery", "Brokkr and Sindri", "Tech", [
    ("Kinetics", None, "chain", [
        ("andesite", "Andesite Alloy", R("ᛟ"), "Brokkr: \"Iron nuggets and andesite. The stone every machine is made of.\"",
         ["Craft 32 andesite alloy"], ["Wrench"]),
        ("shaft", "Shafts and Cogs", R("ᛟ"), "Sindri: \"Rotation is the forge's breath. Carry it.\"",
         ["Craft 16 shafts", "Craft 8 cogwheels and 4 large cogwheels"], P(1)),
        ("wheel", "The Water Wheel", R("ᛟ"), "Brokkr: \"Every forge starts with something that turns.\"",
         ["Place a water wheel", "Power a shaft with it"], ["4 water wheels"]),
        ("gear", "Gearboxes", R("ᛟ"), "Sindri: \"Turn the turning. Up, down, sideways.\"",
         ["Craft a gearbox", "Craft a clutch", "Craft a gearshift"], P(1)),
        ("goggles", "Engineer's Goggles", R("ᛟ"), "Brokkr: \"See the stress before the shaft snaps.\"",
         ["Craft Engineer's Goggles"], ["Stressometer"]),
        ("wind", "The Windmill", R("ᛟ"), "Sindri: \"Wind is free. Sails are not.\"",
         ["Build a windmill with a windmill bearing and 8 sails"], P(2)),
        ("steam", "Steam Engine", R("ᛟ"), "Brokkr: \"Fire and water, tamed. Real power.\"",
         ["Build a steam engine on a fluid tank with a blaze burner"], ["Steam engine", *P(3)], "gift"),
    ]),
    ("Processing", "andesite", "chain", [
        ("mill", "Millstone", R("ᛁ"), "Sindri: \"Grind it finer.\"", ["Craft a millstone", "Mill wheat into flour"], ["16 dough"]),
        ("press", "Mechanical Press", R("ᛁ"), "Brokkr: \"Ingots become sheets.\"", ["Press 16 iron sheets"], P(1)),
        ("crush", "Crushing Wheels", R("ᛁ"), "Sindri: \"Ore is just stone that has not been asked nicely.\"",
         ["Build a pair of crushing wheels", "Crush 32 raw ore"], P(2)),
        ("wash", "Wash, Smoke, Haunt", R("ᛁ"), "Brokkr: \"An encased fan does three jobs, depending on what you blow it through.\"",
         ["Wash gravel with a fan through water", "Smoke food with a fan through fire", "Haunt with a fan through soul fire"], P(2)),
        ("mix", "Mixer and Basin", R("ᛁ"), "Sindri: \"Stir.\"", ["Build a mechanical mixer over a basin"], ["Basin"]),
        ("brass", "Brass", R("ᛁ"), "Brokkr: \"Copper and zinc, mixed hot. The start of real machines.\"",
         ["Make 16 brass ingots in a heated basin"], ["16 brass ingots", *P(2)]),
        ("deploy", "The Deployer", R("ᛁ"), "Sindri: \"A hand that never tires.\"", ["Craft a deployer"], ["Brass hand"]),
        ("seq", "Precision Mechanism", R("ᛁ"), "Brokkr: \"Sequenced assembly. Five steps, one part.\"",
         ["Make a precision mechanism"], ["3 precision mechanisms", *P(3)], "gift"),
    ]),
    ("Logistics", "brass", "chain", [
        ("belt", "Belts", R("ᚱ"), "Sindri: \"Move it without carrying it.\"", ["Place 16 mechanical belts"], P(1)),
        ("funnel", "Funnels and Tunnels", R("ᚱ"), "Brokkr: \"In, out, sorted.\"", ["Use a brass funnel with a filter"], P(1)),
        ("arm", "Mechanical Arm", R("ᚱ"), "Sindri: \"It picks, it places, it never complains.\"", ["Craft a mechanical arm"], P(2)),
        ("crafter", "Mechanical Crafters", R("ᚱ"), "Brokkr: \"Some recipes need a bigger table.\"", ["Craft 9 mechanical crafters"], P(2)),
        ("packager", "Packages", R("ᚱ"), "Sindri: \"Box it, label it, send it.\"", ["Craft a packager", "Send a package"], P(2)),
        ("frog", "Frogports", R("ᚱ"), "Brokkr: \"Do not ask why it is a frog.\"", ["Deliver a package by frogport"], P(2)),
        ("stock", "Stock Keeper", R("ᚱ"), "Sindri: \"Know what you own.\"", ["Order items from a stock keeper"], P(3)),
        ("train", "The Iron Road", R("ᚱ"), "Brokkr: \"A train to the far biomes, where the beasts are.\"",
         ["Build a train with a station and 64 tracks"], ["Train controls", *P(4)], "gift"),
    ]),
    ("The Sealed Realms' Gifts", "mix", "chain", [
        ("netherrack", "Netherrack", R("ᚦ"), "Brokkr: \"The Nether is sealed. Its stone is not. Cobblestone and lava.\"",
         ["Mix 32 netherrack"], P(1)),
        ("quartz", "Quartz", R("ᚦ"), "Sindri: \"Crushed blackstone hides it.\"", ["Make 16 nether quartz"], P(1)),
        ("soul", "Soul Sand", R("ᚦ"), "Brokkr: \"Haunted sand. Soul fire and a fan.\"", ["Make 16 soul sand"], P(1)),
        ("wart", "Nether Wart", R("ᚦ"), "Sindri: \"Every brewer needs it.\"", ["Mix nether wart", "Grow 16 nether wart"], ["Brewing stand"]),
        ("blaze", "Blaze Rods", R("ᚦ"), "Brokkr: \"Compacted fire.\"", ["Make 8 blaze rods"], P(2)),
        ("glow", "Glowstone and Magma", R("ᚦ"), "Sindri: \"Light and heat.\"", ["Make glowstone dust", "Make magma cream"], P(2)),
        ("pearl", "End Stone and Pearls", R("ᚦ"), "Brokkr: \"The End is sealed too. Not its stone.\"", ["Mix 16 end stone"], P(2)),
        ("elytra", "Wings Without a City", I("raven_feather"), "Sindri: \"No End City, no problem.\"",
         ["Craft an elytra (pack recipe)"], ["Elytra", *P(4)], "gift"),
    ]),
    ("Mythic Metals", "crush", "chain", [
        ("tin", "Tin and Silver", R("ᛁ"), "Sindri: \"The common metals of the deep.\"", ["Mine tin", "Mine silver"], P(1)),
        ("forge", "The Alloy Forgery", R("ᛁ"), "Brokkr: \"Real alloys need a real forge.\"", ["Build an Alloy Forgery forge"], ["Forge controller"]),
        ("bronze", "Bronze", R("ᛁ"), "Sindri: \"Copper and tin. Older than iron.\"", ["Forge 16 bronze"], P(2)),
        ("steel", "Steel", R("ᛁ"), "Brokkr: \"Iron, made stronger.\"", ["Forge 16 steel"], P(2)),
        ("mythril", "Mythril", R("ᛁ"), "Sindri: \"Light as a feather.\"", ["Mine mythril", "Craft a mythril pickaxe"], P(2)),
        ("adamantite", "Adamantite", R("ᛁ"), "Brokkr: \"Hard as a giant's heart.\"", ["Mine adamantite"], P(3)),
        ("orichalcum", "Orichalcum", R("ᛁ"), "Sindri: \"The metal of drowned kingdoms.\"", ["Mine orichalcum"], P(3)),
        ("hallowed", "Hallowed", R("ᛁ"), "Brokkr: \"An alloy fit for the gods.\"", ["Forge hallowed"], P(3)),
        ("celestium", "Celestium", R("ᛁ"), "Sindri: \"Starlight in metal.\"", ["Forge celestium"], P(4)),
        ("star", "Star Platinum", R("ᛁ"), "Brokkr: \"The rarest thing we have ever forged.\"", ["Forge star platinum"], P(4)),
        ("full", "Mythic Arsenal", R("ᛁ"), "Sindri: \"A full set of tools from one mythic metal.\"",
         ["A pickaxe, axe, shovel, sword and hoe from one Mythic Metal"], P(5), "gift"),
    ]),
    ("Netherite Without the Nether", "blaze", "chain", [
        ("scrap", "Superheated Scrap", R("ᚦ"), "Brokkr: \"Superheated, mixed, pressed. Ancient debris was never needed.\"",
         ["Make netherite scrap by superheated mixing"], P(3)),
        ("ingot", "The Netherite Ingot", I("weapon/zweihander"), "Sindri: \"Now the hound of Hel can bite.\"",
         ["Craft a netherite ingot"], P(3)),
        ("template", "Upgrade Template", R("ᚦ"), "Brokkr: \"Seven diamonds. Worth it.\"", ["Craft a netherite upgrade template"], P(3)),
        ("set", "Netherite Kit", R("ᚦ"), "Sindri: \"Full netherite. Counts for Chapter 2.\"",
         ["Wear full netherite armor"], ["Counts for Chapter 2: Light in the Dark", *P(5)], "gift"),
    ]),
])

# ======================================================================================== NJORD'S VOYAGES
VOYAGES = build("voyages", "Njord's Voyages", "Small Ships, Valkyrien Skies, Eureka, Seven Seas", "Njord, god of the sea", "Exploration", [
    ("Shipwright", None, "chain", [
        ("cog", "First Keel", R("ᛚ"), "Njord: \"A boat is a promise that you will come home.\"", ["Build a cog (Small Ships)"], ["Paddle", *P(1)]),
        ("sail", "Colors on the Mast", R("ᛚ"), "Njord: \"Your sail is your banner.\"", ["Dye a ship's sail"], ["16 wool"]),
        ("brigg", "The Brigg", R("ᛚ"), "Njord: \"Bigger hull, more cargo.\"", ["Build a brigg"], P(1)),
        ("galley", "The Galley", R("ᛚ"), "Njord: \"Oars when the wind dies.\"", ["Build a galley"], P(2)),
        ("drakkar", "The Drakkar", R("ᛚ"), "Njord: \"A dragon-prowed longship. The ship of the north.\"", ["Build a drakkar"], P(2)),
        ("cargo", "Cargo", R("ᛚ"), "Njord: \"A ship that carries nothing is a raft.\"", ["Load a chest onto a ship"], P(1)),
        ("voyage", "The Long Voyage", R("ᛚ"), "Njord: \"Cross the open sea.\"", ["Sail 2000 blocks in one trip"], ["Spyglass", *P(3)], "gift"),
    ]),
    ("Naval War", "brigg", "chain", [
        ("cannon", "Cannons", R("ᛏ"), "Njord: \"The sea is not friendly. Neither should you be.\"", ["Craft a ship cannon", "Mount it on a ship"], ["16 cannonballs"]),
        ("broadside", "Broadside", R("ᛏ"), "Njord: \"Four guns fire as one.\"", ["Put 4 cannons on one ship"], P(2)),
        ("sink", "Sink Something", R("ᛏ"), "Njord: \"Prove the cannons work.\"", ["Destroy a ship with cannon fire"], P(2)),
        ("shark", "Blood in the Water", I("shark_tooth"), "Njord: \"The bull shark hunts near ships. Let it come to you.\"",
         ["Defeat the Giant Bull Shark from a ship"], P(3), "boss2"),
        ("warship", "Warship", I("serpent_scale"), "Njord: \"Big enough for the World Serpent? Nothing is. Build it anyway.\"",
         ["A ship with 4 or more cannons and 2 or more crew"], ["Counts for Chapter 2: A Warship", *P(4)], "gift"),
    ]),
    ("The Seven Seas", "galley", "chain", [
        ("spot", "Sails on the Horizon", R("ᚱ"), "Njord: \"Pirate ships sail the deep water.\"", ["Find a When Dungeons Arise ship at sea"], P(1)),
        ("board", "Boarding Party", R("ᚱ"), "Njord: \"Grapple close, jump across.\"", ["Board a pirate ship"], P(2)),
        ("junk", "The Pirate Junk", R("ᚱ"), "Njord: \"Painted sails, full holds.\"", ["Loot a Pirate Junk"], P(2)),
        ("corvette", "The Corsair Corvette", R("ᚱ"), "Njord: \"Fast and mean.\"", ["Loot a Corsair Corvette"], P(2)),
        ("galleon", "The Great Galleons", R("ᚱ"), "Njord: \"Floating castles.\"", ["Loot a Victorious or Unicorn Galleon"], P(3)),
        ("captain", "Captain's Treasure", R("ᚱ"), "Njord: \"Every captain hides one chest.\"", ["Find a captain's chest"], ["Treasure map", *P(4)], "gift"),
    ]),
    ("Ships That Fly", "drakkar", "chain", [
        ("helm", "The Helm", R("ᛖ"), "Njord: \"Some dwarves say a ship can sail the sky.\"", ["Craft a ship helm (Eureka)"], P(1)),
        ("assemble", "Assemble", R("ᛖ"), "Njord: \"Blocks become a ship.\"", ["Assemble a Valkyrien Skies ship"], P(2)),
        ("engine", "Engines", R("ᛖ"), "Njord: \"Push.\"", ["Add an engine and fuel it"], P(2)),
        ("balloon", "Balloons", R("ᛖ"), "Njord: \"Lift.\"", ["Lift a ship with balloons"], P(2)),
        ("anchor", "Anchor", R("ᛖ"), "Njord: \"Stay where you are.\"", ["Anchor a flying ship"], P(2)),
        ("sky", "Skyfarer", R("ᛖ"), "Njord: \"Fly a ship over a mountain.\"", ["Fly a ship above Y 200"], P(3)),
        ("island", "Harbor in the Clouds", R("ᛖ"), "Njord: \"Dock at a floating island.\"",
         ["Land a flying ship on a Soaring Structures island"], P(4), "gift"),
    ]),
    ("Sea Blessing", "voyage", "chain", [
        ("bless", "Njord's Blessing", R("ᛚ"), "Njord: \"Near the beasts of the sea, I swim with you.\"", ["Receive the sea blessing near an ocean boss"], P(2)),
        ("deep", "The Deep", R("ᛚ"), "Njord: \"The World Serpent waits in deep water.\"", ["Find a deep ocean"], P(2)),
        ("storm", "Storm at Sea", R("ᛚ"), "Njord: \"Sail through a thunderstorm.\"", ["Be on a ship during a thunderstorm"], P(3), "gift"),
    ]),
])

# ======================================================================================== THE RESTLESS DEAD
DEAD = build("dead", "The Restless Dead", "Mebahel's Draugr Invasion", "Hel, queen of the dead", "Combat & Gear", [
    ("First Contact", None, "chain", [
        ("first", "Cold Hands", R("ᚺ"), "Mimir: \"The draugr do not stay buried. Find out why.\"", ["Kill a draugr"], P(1)),
        ("ten", "Put Them Down", R("ᚺ"), "Mimir: \"Again.\"", ["Kill 25 draugr"], ["Healing potions", *P(1)]),
        ("hundred", "Gravekeeper", R("ᚺ"), "Mimir: \"Hel will notice you.\"", ["Kill 100 draugr"], P(3)),
        ("loot", "Grave Goods", R("ᚺ"), "Mimir: \"They were buried with their weapons.\"", ["Collect 5 different draugr drops"], P(2)),
    ]),
    ("Their Strongholds", "first", "chain", [
        ("tower", "The Watchtower", R("ᛉ"), "Mimir: \"They keep watch from towers on the hills.\"", ["Find a Draugr Tower"], ["Spyglass"]),
        ("towerc", "Take the Tower", R("ᛉ"), "Mimir: \"Climb it.\"", ["Reach the top of a Draugr Tower"], P(2)),
        ("fort", "Fort of the Dead", R("ᛉ"), "Mimir: \"A fort full of the dead. Clear it.\"", ["Find a Draugr Fort", "Clear it"], P(2)),
        ("bastion", "The Bastion", I("dragon_gold"), "Mimir: \"Their lord sits in the Bastion. Fafnir sleeps beneath one.\"", ["Find a Draugr Bastion"], ["Waypoint", *P(3)]),
        ("crypt", "The Crypt", I("weapon/fenrirs_fang"), "Mimir: \"The deepest, rarest crypt. Something huge is chained in one.\"", ["Find a Draugr Crypt"], ["Waypoint", *P(3)]),
        ("all", "Map of the Dead", R("ᛉ"), "Mimir: \"Now you know where they sleep.\"", ["All four Draugr structures found"], P(4), "gift"),
    ]),
    ("The Raid", "ten", "chain", [
        ("horn", "The Horn Sounds", R("ᛏ"), "Mimir: \"When they come for the living, hold the line.\"", ["Trigger a draugr raid"], P(1)),
        ("wave", "First Wave", R("ᛏ"), "Mimir: \"There are always more.\"", ["Survive the first wave"], P(2)),
        ("hold", "Hold the Village", R("ᛏ"), "Mimir: \"No villager falls.\"", ["Win a raid without losing a villager"], P(3)),
        ("three", "Three Raids", R("ᛏ"), "Mimir: \"They keep coming. So do you.\"", ["Win 3 draugr raids"], ["Totem of undying", *P(4)], "gift"),
    ]),
    ("The Overlord", "bastion", "chain", [
        ("find", "The Throne Room", R("ᛞ"), "Mimir: \"The Overlord waits at the heart of the Bastion.\"", ["Reach the Overlord's chamber"], P(2)),
        ("kill", "The Overlord Falls", R("ᛞ"), "Mimir: \"A king of the dead, dead again.\"", ["Defeat the Draugr Overlord"], P(4), "boss2"),
        ("relic", "Hel's Favor", I("hel_key"), "Hel: \"You are interesting, mortal. When you come to my gate, I will remember.\"",
         ["Defeat the Draugr Overlord twice"], P(5), "gift"),
    ]),
])

# ======================================================================================== ULLR'S BOW
def nbows(prefix, mod, counts, base):
    out = []
    for i, n in enumerate(counts):
        out.append((f"{prefix}{n}", f"{mod}: {n}", R("ᚢ"), f"Ullr: \"{['Each bow has a trick. Learn some.', 'More tricks.', 'Most hunters stop here.', 'Every bow in the rack.'][min(i, 3)]}\"",
                    [f"Craft {n} different bows from {mod}"], P(min(5, base + i))))
    return out


BOW = build("bow", "Ullr's Bow", "Too Many Bows, More Bows and Arrows, Extra Bows, Progressive Archery, Truly Modular", "Ullr, god of the bow", "Combat & Gear", [
    ("String and Yew", None, "chain", [
        ("bow", "A Hunter's Bow", R("ᚢ"), "Ullr: \"A hunter who cannot shoot is only half a hunter.\"", ["Craft a bow"], ["32 arrows"]),
        ("hit", "Thirty Paces", R("ᚢ"), "Ullr: \"Hit something far away.\"", ["Hit a mob from 30 blocks"], P(1)),
        ("cross", "The Crossbow", R("ᚢ"), "Ullr: \"Slow, but it punches.\"", ["Craft a crossbow"], P(1)),
        ("ench", "Power and Flame", R("ᚢ"), "Ullr: \"Enchant it.\"", ["Enchant a bow with Power"], P(2)),
        ("far", "Sixty Paces", R("ᚢ"), "Ullr: \"Farther.\"", ["Hit a mob from 60 blocks"], P(3), "gift"),
    ]),
    ("Too Many Bows", "bow", "chain", nbows("tmb", "Too Many Bows", [1, 3, 6, 10], 1) + [
        ("charm", "Bow Charms", R("ᚢ"), "Ullr: \"A charm on the string.\"", ["Craft a bow charm"], P(2)),
        ("ricochet", "Ricochet", R("ᚢ"), "Ullr: \"One arrow, two targets.\"", ["Enchant a bow with Ricochet"], P(3), "gift"),
    ]),
    ("More Bows and Arrows", "bow", "chain", nbows("mba", "More Bows and Arrows", [1, 5, 10], 1) + [
        ("arrows", "Arrows With Teeth", R("ᚢ"), "Ullr: \"Fire, ice, explosions. Arrows are only the start.\"", ["Craft 5 kinds of special arrows"], P(2)),
        ("tnt", "Loud Arrows", R("ᚢ"), "Ullr: \"Careful.\"", ["Kill a mob with an explosive arrow"], P(3), "gift"),
    ]),
    ("Extra Bows and Modular Bows", "cross", "chain", nbows("eb", "Extra Bows", [1, 4], 1) + [
        ("miapi", "Build a Bow", R("ᚢ"), "Ullr: \"Choose the limbs, the grip, the string.\"", ["Build a modular bow (Truly Modular)"], P(2)),
        ("miapi2", "Your Best Bow", R("ᚢ"), "Ullr: \"Make one better than any in a chest.\"", ["Build a modular bow from a Mythic Metal"], P(4), "gift"),
    ]),
    ("The Archer's Path", "hit", "chain", [
        ("lv5", "Archery 5", R("ᚢ"), "Ullr: \"Draw faster.\"", ["Reach archery level 5 (Progressive Archery)"], P(1)),
        ("lv10", "Archery 10", R("ᚢ"), "Ullr: \"Hold steadier.\"", ["Reach archery level 10"], P(2)),
        ("lv20", "Archery 20", R("ᚢ"), "Ullr: \"Now you are a hunter.\"", ["Reach archery level 20"], P(3)),
        ("lv30", "Archery 30", R("ᚢ"), "Ullr: \"Now you are mine.\"", ["Reach archery level 30"], P(4)),
        ("eagle", "Shadow of the Peaks", I("eagle_feather"), "Ullr: \"Now you are ready for the eagle.\"",
         ["Shoot down a flying mob from 40 blocks", "Defeat Haast's Eagle"], ["Counts for Act III: Bow and Mountain", *P(5)], "gift"),
    ]),
])

# ======================================================================================== PATHS OF THE EINHERJAR
def path(prefix, name, god, items):
    return [(f"{prefix}{i}", t, R(r), f"{god}: \"{line}\"", tasks, P(lv), *([k] if k else []))
            for i, (t, r, line, tasks, lv, k) in enumerate(items)]


CLASSES = [
    ("berserker", "Berserker", "Tyr", "bone", ["Bloodrage", "Cleaving Leap", "Bear Shirt", "Undying Rage"],
     ["Rage is a weapon. Learn to hold it.", "Leap and crash down.", "Wear the bear.", "Death will have to wait."]),
    ("valkyrie", "Valkyrie", "Freyja", "feather", ["Spear of the Slain", "Ascent", "Freyja's Aegis", "Choose the Slain"],
     ["Throw true.", "Take to the sky.", "Shield your sisters.", "Choose who falls."]),
    ("huntsman", "Huntsman", "Skadi", "arrow", ["Volley", "Frost Snare", "Hunter's Mark", "Skadi's Hailstorm"],
     ["Many arrows.", "Let them walk into it.", "Nothing hides from you.", "Make it rain."]),
    ("volva", "Volva", "Freyja", "amethyst shard", ["Kenaz, the Torch", "Isa, the Ice", "Algiz, the Ward", "Thurisaz, the Thunder"],
     ["Fire from a rune.", "Ice from a rune.", "Protection from a rune.", "Thunder from a rune."]),
    ("ulfhednar", "Ulfhednar", "Odin", "leather", ["Call the Pack", "Howl", "Wolf Form", "Fenrir's Hunger"],
     ["Never hunt alone.", "Let them hear you.", "Become the wolf.", "Feed on the fight."]),
]


def class_branch(cid, title, god, mat, abil, lines):
    out = [(f"{cid}_rune", f"Path of the {title}", I(f"{cid}_rune"), f"{god}: \"Carve the rune and walk the path.\"",
            [f"Craft the {title} Rune Stone (2 cobblestone + {mat})", "Use it"], P(1))]
    for lv, name, line, tier in zip((1, 10, 20, 35), abil, lines, (1, 2, 3, 4)):
        out.append((f"{cid}_{lv}", f"{name}", I(f"{cid}_rune"), f"{god}: \"{line}\"",
                    [f"Reach {title} level {lv}", f"Use {name}" if not (cid == "berserker" and lv == 35) else "Survive a killing blow with Undying Rage"], P(tier)))
    out.append((f"{cid}_50", f"{title} Master", I(f"{cid}_rune"), f"{god}: \"Level 50. There is no more to teach you.\"",
                [f"Reach {title} level 50"], [f"Title: {title} Master", *P(5)], "gift"))
    return out


PATHS = build("paths", "Paths of the Einherjar", "the five classes, Better Combat, Simply Swords, Fantasy Weapons", "Tyr, god of war", "Combat & Gear", [
    ("Choose a Path", None, "chain", [
        ("choose", "Five Paths", R("ᛏ"), "Tyr: \"Berserker, Valkyrie, Huntsman, Volva or Ulfhednar. Every einherjar fights their own way.\"",
         ["Use any class rune stone"], ["Class starter kit"]),
        ("lv5", "First Blood", R("ᛏ"), "Tyr: \"Every kill teaches. Bosses teach the most.\"", ["Reach level 5 in any class"], P(1)),
        ("two", "A Second Path", R("ᛏ"), "Tyr: \"Switch any time. Each path keeps its own level.\"", ["Reach level 10 in two classes"], P(2)),
        ("all5", "All Five Paths", R("ᛏ"), "Tyr: \"Few walk them all.\"", ["Reach level 20 in all five classes"], ["Title: Einherjar of Five Paths", *P(5)], "gift"),
    ]),
    *[(title, "choose", "chain", class_branch(cid, title, god, mat, abil, lines)) for cid, title, god, mat, abil, lines in CLASSES],
    ("Weapon Master", "lv5", "chain", [
        ("ss1", "Simply Swords", R("ᛏ"), "Tyr: \"A new blade for every hand.\"", ["Craft a Simply Swords weapon"], P(1)),
        ("ss5", "Five Shapes", R("ᛏ"), "Tyr: \"Longsword, rapier, katana, glaive, scythe.\"", ["Craft 5 different Simply Swords weapon types"], P(2)),
        ("unique", "A Named Blade", R("ᛏ"), "Tyr: \"Some swords have names.\"", ["Find a Simply Swords unique weapon"], P(3)),
        ("fw", "Fantasy Weapons", R("ᛏ"), "Tyr: \"Stranger steel.\"", ["Craft a Fantasy Weapons weapon"], P(2)),
        ("ancient", "Weapons of the Ancients", I("weapon/khopesh"), "Tyr: \"Khopesh, gladius, kopis, macuahuitl.\"",
         ["Kill a mob with 4 different Vivid Lands weapons"], P(3)),
        ("all", "Master of Arms", I("weapon/ragnarok"), "Tyr: \"Swing every weapon the way it was meant to be swung.\"",
         ["Kill a mob with 10 different weapon types"], P(5), "gift"),
    ]),
])

# ======================================================================================== THE ANCIENT ARMORY (collection)
SETS = ["sumerian", "akkadian", "egyptian", "minoan", "shang", "nubian", "hittite", "phoenician", "mycenaean", "olmec",
        "assyrian", "babylonian", "etruscan", "celtic", "illyrian", "thracian", "iberian", "athenian", "spartan", "macedonian",
        "argyraspid", "scythian", "persian", "carthaginian", "numidian", "dacian", "roman", "gladiator", "centurion", "praetorian",
        "germanic", "hun", "qin", "han", "goguryeo", "maurya", "aksumite", "sarmatian", "parthian", "anglo_saxon",
        "byzantine", "khmer", "mongol", "maya", "aztec", "inca", "samurai", "pharaoh", "agamemnon"]
BANDS = [("Ward 1: for Act I", 0, 5, 1), ("Ward 2: for Act II", 5, 15, 2), ("Ward 3: for Act III", 15, 25, 3),
         ("Ward 4: for Act IV", 25, 35, 4), ("Wards 5 to 9: for Chapter 2", 35, 49, 5)]


def nice(s):
    return s.replace("_", " ").title()


armory_branches = [("The Armorer", None, "chain", [
    ("first", "Dressed for the Hunt", I("sumerian_helmet"), "Mimir: \"Sumer, Akkad, Egypt. The first armies.\"", ["Wear a full ancient set"], P(1)),
    ("glam", "Wear What You Like", I("glamour_template"), "Mimir: \"Strength from one set, looks from another.\"", ["Glamour an armor piece"], ["Glamour Template x4"]),
    ("bonus", "Set Bonus", R("ᛗ"), "Mimir: \"A full set gives its people's gift.\"", ["Have a full-set bonus active"], P(2)),
    ("ward", "Caught Up", I("berserker_helmet"), "Mimir: \"Fight a boss with armor made for it.\"", ["Hit a boss while your ward matches it"], P(2)),
])]
for label, a, b, lv in BANDS:
    armory_branches.append((label, "first", "grid", [
        (s, nice(s), I(f"{s}_helmet"), f"Tier {SETS.index(s) + 1}.", [f"Craft the full {nice(s)} set"], P(min(5, lv)))
        for s in SETS[a:b]]))
armory_branches.append(("Other Smiths", "bonus", "chain", [
    ("ek", "Epic Knights", R("ᛗ"), "Mimir: \"Plate and mail from the west.\"", ["Craft a full Epic Knights set"], P(2)),
    ("ia", "Immersive Armors", R("ᛗ"), "Mimir: \"Bone, wither, divine.\"", ["Craft a full Immersive Armors set"], P(2)),
    ("aota", "Armor of the Ages", R("ᛗ"), "Mimir: \"From the builders of Dawn of Time.\"", ["Craft a full Armor of the Ages set"], P(2)),
    ("fa", "Fantasy Armor", R("ᛗ"), "Mimir: \"Strange shapes.\"", ["Craft a full Fantasy Armor set"], P(3)),
    ("viking", "The Viking Sets", I("jarl_helmet"), "Mimir: \"Berserker, Ulfhednar, Valkyrie, Jarl.\"", ["Craft all four Viking sets"], P(5), "gift"),
]))
armory_branches.append(("The Collector", "ward", "chain", [
    ("c10", "Ten Sets", R("ᛗ"), "Mimir: \"A small museum.\"", ["Craft 10 ancient sets"], P(3)),
    ("c25", "Twenty-Five Sets", R("ᛗ"), "Mimir: \"Half the old world.\"", ["Craft 25 ancient sets"], P(4)),
    ("c49", "Every Army of the Old World", I("agamemnon_helmet"), "Mimir: \"All forty-nine. Not even Odin has that.\"",
     ["Craft all 49 ancient sets"], ["Title: Collector", *P(5)], "gift"),
]))
ARMORY = build("armory", "The Ancient Armory", "the 49 ancient sets and the other armor mods", "Mimir", "Combat & Gear", armory_branches)

# ======================================================================================== KINGS OF MIDGARD
KINGS = build("kings", "Kings of Midgard", "Civilizations", "Odin", "Exploration", [
    ("Many Peoples", None, "chain", [
        ("visit", "Strangers", R("ᛗ"), "Mimir: \"Midgard has many kings. Most of them want your head.\"", ["Visit a Civilizations settlement"], P(1)),
        ("visit3", "Three Peoples", R("ᛗ"), "Mimir: \"Learn who rules where.\"", ["Visit 3 different Civilizations settlements"], P(2)),
        ("norse", "The Northmen", R("ᛗ"), "Mimir: \"Your own people. For now.\"", ["Visit the Norse settlement"], P(1)),
        ("all", "Every Banner", R("ᛗ"), "Mimir: \"You have seen every people in Midgard.\"", ["Visit every Civilizations people"], P(4), "gift"),
    ]),
    ("Crowns and Gods", "visit", "chain", [
        ("leader", "A Fallen Crown", R("ᛞ"), "Mimir: \"Their leaders fight for their people. So will you.\"", ["Defeat a Civilizations leader"], P(2), "boss2"),
        ("leader3", "Three Crowns", R("ᛞ"), "Mimir: \"Kingslayer, they will call you.\"", ["Defeat 3 Civilizations leaders"], P(3)),
        ("god", "Gods of Other Lands", R("ᛞ"), "Mimir: \"Odin is not the only god who walks Midgard.\"", ["Defeat a Civilizations god"], P(4), "boss2"),
        ("gods", "Twilight of Many Gods", R("ᛞ"), "Mimir: \"Ragnarok is not only ours.\"", ["Defeat every Civilizations god"], ["Title: Godslayer", *P(5)], "gift"),
    ]),
])

# ======================================================================================== THE WANDERER'S SAGA
VIVID = ["taiga_lakelands", "caledonian_pinewood", "boreal_snowwoods", "highland_moors", "alpine_meadow", "oasis", "tropical_river",
         "fen", "endless_steppe", "golden_savanna", "wildflower_prairie", "tundra", "glacial_outwash", "glacier", "rainforest",
         "tropical_beach", "red_canyonlands", "rocky_hamada", "cloud_forest", "old_growth_oakwood", "redwood_giants",
         "alpine_peaks", "highland_crags", "jagged_spires", "snowy_shore", "northern_ocean"]
SAGA = build("saga", "The Wanderer's Saga", "Ancient Structures, Ancient Villages, Grand Capitals, Soaring Structures, Better Strongholds, Vivid Lands biomes", "Odin the Wanderer", "Exploration", [
    ("The Wanderer", None, "chain", [
        ("start", "The Grey Cloak", R("ᚱ"), "Odin: \"I walked Midgard in a grey cloak for a thousand years. Walk it too.\"", ["Travel 5000 blocks"], P(1)),
        ("far", "Ten Thousand Steps", R("ᚱ"), "Odin: \"Farther.\"", ["Travel 25000 blocks"], P(2)),
        ("ways", "Waystone Network", R("ᚱ"), "Odin: \"Ten old roads.\"", ["Activate 10 waystones"], P(3)),
        ("edge", "The Edge of the Map", R("ᚱ"), "Odin: \"Go where no one has been.\"", ["Travel 10000 blocks from spawn"], P(4), "gift"),
    ]),
    ("Ancient Structures", "start", "chain", [
        ("maya", "The Mayan Temple", R("ᚨ"), "Odin: \"Stepped pyramids in the jungle. The Silverback rules one.\"", ["Find a Mayan site"], P(1)),
        ("rome", "Roman Ruins", R("ᚨ"), "Odin: \"An empire's bones.\"", ["Find a Roman site"], P(1)),
        ("japan", "The Shrine", R("ᚨ"), "Odin: \"Torii gates and quiet halls.\"", ["Find a Japanese site"], P(1)),
        ("german", "The Hall", R("ᚨ"), "Odin: \"A northern hall. Almost home.\"", ["Find a German site"], P(1)),
        ("secret", "Secret Passage", R("ᚨ"), "Odin: \"The builders hid things.\"", ["Find a secret passage in an Ancient Structures site"], P(2)),
        ("minib", "Guardians", R("ᚨ"), "Odin: \"Some sites have keepers.\"", ["Defeat an Ancient Structures guardian"], P(3)),
        ("village", "Ancient Villages", R("ᚨ"), "Odin: \"A village of the old ways.\"", ["Find an Ancient Villages village"], P(2)),
        ("all4", "Four Cultures", R("ᚨ"), "Odin: \"You have seen all four peoples who built them.\"", ["All four Ancient Structures cultures found"], P(4), "gift"),
    ]),
    ("Wonders", "far", "chain", [
        ("capital", "Grand Capitals", R("ᛟ"), "Odin: \"Cities of kings, empty now.\"", ["Visit a Luki's Grand Capitals city"], P(2)),
        ("capital2", "Three Capitals", R("ᛟ"), "Odin: \"Each built by a different hand.\"", ["Visit 3 grand capitals"], P(3)),
        ("sky", "Islands in the Sky", R("ᛟ"), "Odin: \"Some ruins float. Do not look down.\"", ["Reach a Soaring Structures island"], P(2)),
        ("sky3", "Sky Walker", R("ᛟ"), "Odin: \"Three of them.\"", ["Reach 3 floating islands"], P(3)),
        ("hold", "The Stronghold", R("ᛟ"), "Odin: \"Better Strongholds go deep.\"", ["Find a stronghold"], P(2)),
        ("gate", "The Gate Below", I("hel_key"), "Odin: \"Under one stronghold, Hel's gate waits. Find it before Garmr finds you.\"",
         ["Find the stronghold portal room"], ["Waypoint for Chapter 2: Garmr", *P(4)], "gift"),
    ]),
    ("The Lands of Vivid Lands", "start", "grid", [
        (b, nice(b), R("ᛚ"), "A land of Midgard.", [f"Visit {nice(b)}"], P(1)) for b in VIVID]),
    ("Atlas", "ways", "chain", [
        ("b10", "Ten Lands", R("ᛚ"), "Odin: \"Every land has its beast.\"", ["Visit 10 Vivid Lands biomes"], P(2)),
        ("b20", "Twenty Lands", R("ᛚ"), "Odin: \"Know them all.\"", ["Visit 20 Vivid Lands biomes"], P(3)),
        ("otbwg", "Oh The Biomes", R("ᛚ"), "Odin: \"Even stranger lands.\"", ["Visit 10 Oh The Biomes We've Gone biomes"], P(3)),
        ("atlas", "Atlas of Midgard", R("ᛚ"), "Odin: \"You know Midgard better than I do.\"", ["Visit every Vivid Lands biome"], ["Title: Wanderer", *P(5)], "gift"),
    ]),
])

# ======================================================================================== SKADI'S BESTIARY
ANIMALS = ["bear", "deer", "boar", "lion", "rhino", "elephant", "zebra", "giraffe", "hippo", "alligator", "vulture", "tortoise",
           "snail", "butterfly", "firefly", "duck", "rattlesnake", "coral_snake", "bass", "catfish"]
BEAST = build("bestiary", "Skadi's Bestiary", "Naturalist, Animal Garden, Backported Wolves, Saint's Dragons", "Skadi", "Wildlife", [
    ("Know Your Prey", None, "chain", [
        ("first", "A Hunter's Eye", R("ᛖ"), "Skadi: \"A hunter knows every animal, not only the ones she kills.\"", ["Find 5 Naturalist animals"], P(1)),
        ("net", "Bug Net", R("ᛖ"), "Skadi: \"Small things too.\"", ["Catch a butterfly or firefly"], P(1)),
        ("ten", "Ten Kinds", R("ᛖ"), "Skadi: \"Keep looking.\"", ["Find 10 Naturalist animals"], P(2)),
        ("all", "The Full Bestiary", R("ᛖ"), "Skadi: \"Now you know my lands as I do.\"", ["Find every animal in the grid below"], ["Title: Huntress's Friend", *P(5)], "gift"),
    ]),
    ("Field Notes", "first", "grid", [(a, nice(a), R("ᛖ"), "Seen in the wild.", [f"Find a {nice(a).lower()}"], P(1)) for a in ANIMALS]),
    ("Wolves", "first", "chain", [
        ("wolf", "A Loyal Wolf", I("wolf_pelt"), "Skadi: \"Even I keep wolves.\"", ["Tame a wolf"], P(1)),
        ("variants", "Every Coat", I("wolf_pelt"), "Skadi: \"Woods, ashen, snowy, spotted...\"", ["Tame 4 different wolf variants"], P(2)),
        ("pack", "Your Own Pack", I("wolf_pelt"), "Skadi: \"Five wolves at your heel.\"", ["Have 5 tamed wolves"], P(3)),
        ("alpha", "Pack Against Pack", I("wolf_pelt"), "Skadi: \"Bring your pack to the Dire Wolf.\"", ["Defeat the Dire Wolf Alpha with a tamed wolf alive"], P(4), "gift"),
    ]),
    ("Animal Garden", "ten", "chain", [
        ("raven", "Ravens of Your Own", I("raven_feather"), "Skadi: \"Odin has two ravens. Find yours.\"", ["Find a common raven"], P(2)),
        ("gorilla", "The Gorilla", I("silverback_fist"), "Skadi: \"The Silverback's smaller cousins.\"", ["Find a western gorilla"], P(2)),
        ("shark", "Fins", I("shark_tooth"), "Skadi: \"Know the shark before you fight its king.\"", ["Find a bull shark"], P(2), "gift"),
    ]),
    ("Dragons", "ten", "chain", [
        ("egg", "Dragon's Egg", I("dragon_gold"), "Mimir: \"Not every dragon is Fafnir. Some can be raised.\"", ["Find a dragon egg (Saint's Dragons)"], P(2)),
        ("hatch", "Hatchling", I("dragon_gold"), "Mimir: \"Keep it warm.\"", ["Hatch a dragon"], P(3)),
        ("grow", "Growing Up", I("dragon_gold"), "Mimir: \"It eats a lot.\"", ["Raise a dragon to adult"], P(3)),
        ("saddle", "Saddled", I("dragon_gold"), "Mimir: \"Hold on.\"", ["Saddle a dragon"], P(3)),
        ("ride", "Wings Before Fafnir", I("dragon_gold"), "Skadi: \"Fight a dragon from the back of a dragon.\"", ["Ride a grown dragon"], ["Counts for Chapter 2: Dragon-Slayer", *P(5)], "gift"),
    ]),
])

# ======================================================================================== TROPHY HALL (like Prominence's Trophy Collection)
TROPHIES = [("cave_bear", "bear_pelt"), ("dire_wolf", "wolf_pelt"), ("irish_elk", "great_antlers"), ("terror_bird", "terror_claw"),
            ("steppe_bison", "bison_horn"), ("hippo", "hippo_hide"), ("komodo", "komodo_venom"), ("crocodile", "croc_scales"),
            ("cave_lion", "lion_mane"), ("saber_tooth", "saber_fang"), ("haast_eagle", "eagle_feather"), ("anaconda", "anaconda_skin"),
            ("silverback", "silverback_fist"), ("glyptodon", "glyptodon_plate"), ("walrus", "walrus_tusk"), ("ground_sloth", "sloth_claw"),
            ("bull_shark", "shark_tooth"), ("woolly_rhino", "rhino_horn"), ("elephant", "ivory"), ("mammoth", "mammoth_tusk"),
            ("sleipnir", "sleipnir_hair"), ("garmr", "hel_key"), ("fafnir", "dragon_gold"), ("jormungandr", "serpent_scale"),
            ("fenrir", "weapon/fenrirs_fang")]
HALL = build("hall", "Hall of Trophies", "Every boss, beaten again and again", "Odin", "Collections", [
    ("The Hall", None, "chain", [
        ("open", "An Empty Hall", R("ᚹ"), "Odin: \"Every einherjar keeps a hall of trophies. Yours is empty.\"", ["Defeat any boss"], P(1)),
        ("stand", "Display It", R("ᚹ"), "Odin: \"Put a trophy on a stand where guests can see it.\"", ["Place a trophy in an item frame"], P(1)),
    ]),
    ("Trophies of Chapter 1", "open", "grid", [(t, nice(b), I(i), "Hand in the trophy.", [f"Hand in 1 {nice(i.split('/')[-1])}"], P(2), "boss2") for b, i in TROPHIES[:20] for t in [b]]),
    ("Trophies of Chapter 2", "open", "grid", [(t, nice(b), I(i), "Hand in the trophy.", [f"Hand in 1 {nice(i.split('/')[-1])}"], P(4), "boss2") for b, i in TROPHIES[20:] for t in [b]]),
    ("Veteran Hunts", "stand", "chain", [
        ("v1", "Again", R("ᚹ"), "Odin: \"Once is luck.\"", ["Defeat any boss a second time"], P(2)),
        ("v10", "Ten Hunts", R("ᚹ"), "Odin: \"Ten is skill.\"", ["Defeat 10 bosses in total"], P(3)),
        ("v50", "Fifty Hunts", R("ᚹ"), "Odin: \"Fifty is a legend.\"", ["Defeat 50 bosses in total"], P(4)),
        ("stagger", "Breaker", R("ᚹ"), "Odin: \"Stagger 25 bosses.\"", ["Stagger bosses 25 times"], P(3)),
        ("nohit", "Untouched", R("ᚹ"), "Odin: \"Kill a boss without taking a hit.\"", ["Defeat a boss without taking damage"], P(5)),
        ("under", "Underdressed", R("ᚹ"), "Odin: \"Kill a boss two acts above your armor's ward.\"", ["Defeat a boss while two stages behind on ward"], P(5)),
        ("all", "The Full Hall", I("agamemnon_helmet"), "Odin: \"Every trophy of Midgard. Valhalla has a seat for you.\"",
         ["Every trophy handed in"], ["Title: Einherjar Champion", *P(5)], "gift"),
    ]),
])

SIDE = [TUTORIAL, FORGE, VOYAGES, DEAD, BOW, PATHS, ARMORY, KINGS, SAGA, BEAST, HALL]
