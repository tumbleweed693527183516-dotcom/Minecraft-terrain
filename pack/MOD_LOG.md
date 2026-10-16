# Vivid Lands modpack: mod log

Every mod suggested for the pack, with what it brings and whether it fits (Fabric 1.20.1).
Used to plan the boss progression: which creatures become bosses, in which structures.

Status: **pending** (not checked yet) · **ok** (Fabric 1.20.1, fits) · **no** (with reason)

## Structure mods

| # | Mod | Link | Loader / version | Licence | Structures worth using | Status | Notes |
|---|-----|------|------------------|---------|------------------------|--------|-------|
| 1 | Ancient Structures (Dawn of Time team) | https://modrinth.com/mod/ancient-structures | Fabric 1.20.1: yes (0.0.14) | GPL-3.0 | ~20 sites in four cultures (Mayan, Roman, Japanese, German): lone temples, sacred ruins, abandoned villages, military sites; already has mini-bosses, secret passages, custom loot | ok | Needs Dawn of Time, Armor of the Ages, Fusion, YACL. Open licence: add-on use is fine. Prime boss-arena candidates; need the structure ids once installed. |
| 2 | Ancient Villages (Dawn of Time team) | https://modrinth.com/mod/ancient-villages | Fabric 1.20.1: yes (0.0.4) | LGPL-3.0 | Japanese-style villages (military, farming, industrial, trade) with NPC quests and reputation; spawns in taiga biomes | ok | Wanted as the village style for the pack. Needs Dawn of Time, Armor of the Ages, Garden Trails, Fusion, YACL. Adds villages next to vanilla ones; switching vanilla villages off is a small data change. Early release. |

## Creature / animal mods

| # | Mod | Link | Loader / version | Licence | Creatures / models worth using | Status | Notes |
|---|-----|------|------------------|---------|--------------------------------|--------|-------|

| 6 | Naturalist (Starfish Studios) | https://modrinth.com/mod/naturalist | Fabric 1.20.1: yes (5.0pre4, beta) | Assets ARR, code MIT | GeckoLib models: bear, moose, deer, hippo, alligator, rhino, elephant, mammoth, lion, giraffe, boar, ostrich, vulture, snake, tortoise, capybara... | ok | CHOSEN: model source for Chapter 1: cave bear, elk (moose), hippo, crocodile (alligator), woolly rhino, elephant, mammoth. Needs GeckoLib (already in pack). |
| 7 | Animal Garden series (Aquarius.playz) | https://modrinth.com/user/Aquarius.playz | Fabric 1.20.1: yes (one mod per animal) | ARR | Western Gorilla, Bull Shark, Crocodile, Hippopotamus, White Rhinoceros, Bison, Lion, Snow Leopard, Spotted Hyena... | ok | CHOSEN: gorilla and bull shark (install only those two). |
| 8 | Fossils and Archeology: Revival | https://modrinth.com/mod/fossils-and-archeology-revival | Fabric 1.20.1: yes (9.3.4.0) | FA License | 60+ prehistoric creatures incl. mammoth, smilodon (saber-tooth), terror bird, dodo, dinosaurs (revived from fossils/DNA) | ok | CHOSEN for the saber-tooth (smilodon); brings a whole dinosaur system with it. Several dependencies. |

| 9 | Animal Garden - Common Raven | https://modrinth.com/mod/animal-garden-common-raven | Fabric 1.20.1: yes | ARR | Raven | ok | CHOSEN: model for Huginn and Muninn. |
| 10 | Backported Wolves | https://modrinth.com/mod/backported-wolves | Fabric 1.20.1: yes | MIT | The newer wolf coat variants (ashen, black, chestnut, rusty, snowy, spotted, striped, woods) | ok | CHOSEN: distinct coats for Geri, Freki, Skoll, Hati, Garmr and a giant black Fenrir on the vanilla wolf model. |
| 11 | Saint's Dragons | https://modrinth.com/mod/saints-dragons | Fabric 1.20.1: yes | Dual licence | Animated, tameable, rideable dragons | ok | CHOSEN: models for Fafnir and Nidhoggr (two looks). |
| 12 | Useless Reptile | https://modrinth.com/mod/useless-reptile | Fabric 1.20.1: listed (author says older versions unsupported) | ARR (submods allowed) | Swamp Wyvern, Moleclaw (cave burrower), River Pikehorn, Lightning Chaser, Magmamuncher | not used | Alternative dragon models; Moleclaw could suit a burrowing Nidhoggr. Needs YACL. |
| 13 | Myths of the Sea | https://modrinth.com/mod/myths-of-the-sea | 1.20.1 listed; Fabric 1.20.1 not confirmed yet | ARR | Leviathan, Kraken, Hippocampus, Bunyip, Bake Kujira, Abaia | not used | Jormungandr will be a custom segmented serpent instead (no extra dependency, can be truly colossal). |

## Other mods

| # | Mod | Link | Loader / version | Licence | Purpose | Status | Notes |
|---|-----|------|------------------|---------|---------|--------|-------|
| 4 | Civilizations | https://modrinth.com/mod/civilizations | Fabric 1.20.1: yes (0.2, release) | All Rights Reserved | Egyptian, Chinese, Roman, Greek, Norse civilizations; structures, currencies, trading; leader bosses (Khufu, Qin Shi Huang, Caesar, Alexander, Bjorn Ironside) and summonable gods (Anubis, Sun Wukong, Mercury, Artemis, Loki) | ok | CHOSEN. No dependencies. Core of the ancient-civilizations theme and a ready-made boss set; check which biomes its structures use once installed. |
| 5 | Luki's Grand Capitals | https://modrinth.com/mod/lukis-grand-capitals | Fabric 1.20.1: yes (1.1.3, release) | All Rights Reserved | Rebuilds vanilla villages as grand capitals with their own loot; also remakes pillager outpost, woodland mansion, swamp hut | ok | CHOSEN as the village replacement. No dependencies. Works through vanilla's village slots, so it uses Vivid Lands' village biome tags automatically. Beta: jungle, snowy, badlands, meadow villages still planned; warns some villages may generate oddly on rough terrain. |
| 3 | Small Ships | https://modrinth.com/mod/small-ships | Fabric 1.20.1: yes (2.0.0-b1.4, beta) | All Rights Reserved | Sailable medieval ships (cog, brigg, galley, drakkar, caravel, dhow, galleon), cannons, wind and sails, dockyard, ramming and sinking | ok | Gameplay mod for the pack. Only needs Fabric API. ARR, so install it as-is; an add-on that uses it is fine, copying its files is not. Fabric build is a beta. |

## Boss progression plan

Target: about 20 bosses in two chapters.

### Chapter 1: dangerous real (and Ice Age) animals - draft list

Fierce but believable, nothing mythical. Each tied to a Vivid Lands biome. Ordered roughly easy to hard.

| # | Boss | Home biome | Fight ideas (draft) | Model source |
|---|------|------------|---------------------|--------------|
| 1 | Cave Bear | taiga lakelands, Caledonian pinewood (cave lair) | Swipes, rearing roar that slows you; a good first boss | Naturalist bear |
| 2 | Giant Irish Elk | highland moors | Antler charges, knockback; calls a small herd | Naturalist moose |
| 3 | Hippopotamus | oasis, tropical rivers | Hides underwater then lunges; huge bite, capsizes boats | Naturalist hippo |
| 4 | Nile Crocodile (giant) | fen, tropical rivers | Ambush from water, death-roll grab | Naturalist alligator |
| 5 | Silverback Gorilla | rainforest, cloud forest | Chest-beat stun, boulder throws, ground pound | Animal Garden gorilla |
| 6 | Saber-tooth Cat | endless steppe, golden savanna | Stalks invisibly in tall grass, pounce and bleed | Fossils and Archeology smilodon (chosen) |
| 7 | Woolly Rhinoceros | tundra, glacial outwash | Unstoppable charges that break blocks; dodge into walls to stun it | Naturalist rhino |
| 8 | African Elephant bull | golden savanna | Stampede waves, trunk throw | Naturalist elephant |
| 9 | Bull Shark (giant) | northern and temperate oceans | Naval fight around your ship; breaches and rams | Animal Garden bull shark |
| 10 | Woolly Mammoth | glacier, tundra | Chapter 1 finale: tusk sweeps, trumpet shockwave, stomp quakes; maybe rideable reward | Naturalist mammoth |

### Chapter 2: Norse mythology - custom, models to be supplied

| Boss | Who | Fight ideas (draft) | Model |
|------|-----|---------------------|-------|
| Huginn and Muninn | Odin's ravens, Thought and Memory | Twin flying fight: one dives and strikes, the other blinds or confuses; kill both within a short window or the survivor revives the other | Animal Garden raven |
| Geri and Freki | Odin's wolves | Pack duo: flanking charges, howl that buffs the other, enrage when one falls | vanilla wolf + Backported Wolves coats |
| Sleipnir | Odin's eight-legged horse, child of Loki | Fast arena charges and trampling, gallops through the air between phases; tamable or rideable reward possible | custom: vanilla horse model with 8 legs |
| Fenrir | Colossal wolf, child of Loki, slayer of Odin | Chained at the start: phases where he breaks Gleipnir link by link; huge bites, ground slams | giant black wolf (vanilla + Backported Wolves) |
| Skoll and Hati | Wolves chasing the sun and moon | Day and night pair: Skoll stronger by day, Hati by night; sky darkens or brightens as they win | wolf coats (vanilla + Backported Wolves) |
| Garmr | Blood-stained hound at the gates of Hel | Gatekeeper of a Hel arena; summons draugr, life-steal bites | wolf coat (vanilla + Backported Wolves) |
| Jormungandr | The Midgard Serpent, child of Loki | Ocean boss: surfaces around the ship or coast, coils, poison breath, tail slams; fits Small Ships naval combat | custom segmented serpent |
| Nidhoggr | Dragon gnawing Yggdrasil's roots | Underground or deep-cave fight among giant roots; corrosion and burrowing | Saint's Dragons (dark) |
| Fafnir | Dwarf turned dragon guarding cursed gold | Treasure-hoard lair; fire breath, flight, gold-greed mechanics (picking up gold enrages him); cursed-gold reward | Saint's Dragons (gold) |

Notes: Civilizations already includes Loki and Bjorn Ironside, so Loki's children (Fenrir, Jormungandr, Sleipnir) and the Norse leader can tie into one storyline toward Ragnarok.

## Candidates suggested (not chosen yet)

Village replacements and ancient-civilization content found on Modrinth (Fabric 1.20.1):

| Mod | Link | Licence | Why it might fit |
|-----|------|---------|------------------|
| Civilizations | https://modrinth.com/mod/civilizations | ARR | Egyptian, Chinese, Roman, Greek and Norse civilizations with structures, currencies and trading; leaders (Khufu, Qin Shi Huang, Caesar, Alexander, Bjorn Ironside) to fight and gods (Anubis, Sun Wukong, Mercury, Artemis, Loki) to summon. Fabric only, 1.20.1-1.20.4. |
| Towns and Towers | https://modrinth.com/mod/towns-and-towers | CC-BY-NC-SA-4.0 | 50+ villages, outposts and ships inspired by real-world architecture styles; adds alongside vanilla. Needs CristelLib. |
| ChoiceTheorem's Overhauled Village | https://modrinth.com/mod/ct-overhaul-village | CC-BY-NC-ND-4.0 | Villages for many more biomes plus overhauled vanilla ones. |
| Epic Structures: Villages | https://modrinth.com/mod/epic-structures-villages | ARR | Replaces villages with large medieval cities and towns. |
| Luki's Grand Capitals | https://modrinth.com/mod/lukis-grand-capitals | ARR | Rebuilds vanilla villages as grand capitals. |
| Mebahel's Antique Beasts | https://modrinth.com/mod/mebahels-antique-beasts | ARR | Ancient warriors, legendary beasts, forgotten ruins (creature/boss candidate). |

### Story: the road to Ragnarok (approved)

Ragnarok, the prophesied end of the world, is coming. The player is a mortal chosen to become one of the einherjar,
Odin's champions for the last battle.

- **Skadi** (goddess of winter, mountains and the hunt) gives Chapter 1. She doesn't trust mortals and sets the player
  hunter's trials: slay the greatest beasts of Midgard. Each boss is one trial, and her gifts are the rewards. The Woolly
  Mammoth is her final test; bringing her the Frozen Heart proves the player worthy, and she tells Odin.
- **Loki's betrayal** (the bridge): Odin summons the player just as Loki (Civilizations) breaks free and starts Ragnarok.
  Beating Loki doesn't stop it, because his monstrous children are already loose.
- **Odin** gives Chapter 2, his war against Ragnarok:
  - Huginn and Muninn, Geri and Freki, and Sleipnir are Odin's own companions. These are trials of worthiness, not fights
    to the death: once beaten, they join the player (the ravens scout the remaining bosses, the wolves fight alongside
    them, and Sleipnir becomes the player's mount).
  - Skoll and Hati, Garmr, Nidhoggr, Fafnir and Jormungandr are the forces of Ragnarok, to be hunted down before the end.
  - Fenrir is the finale. In the myth, Fenrir kills Odin at Ragnarok; here the player stands in Odin's place and breaks
    the prophecy.
- **Mimir**, the wise severed head Odin keeps for counsel, guides the player throughout. He gives quests, explains the
  lore and points the way to the next boss, as an NPC or a talking item.

Delivery in game (to decide later): a quest book, quest-giver NPCs or shrines for Skadi and Odin, and raven messages
after each boss.

### Progression (draft v1)

Each boss drops a **trophy** (needed to unlock the next tier) and **gear materials** that make the next fights possible.
Chapter 1 bosses live in Vivid Lands biomes (wild lairs, or arenas in Ancient Structures sites). Chapter 2 is unlocked
through the Civilizations Norse storyline and is fought at sacred Norse sites.

**Chapter 1: the wild (iron to diamond tier)**

| Order | Boss | Where | Unlock | Key drops |
|-------|------|-------|--------|-----------|
| 1 | Cave Bear | cave lair in pine forests | none: the starter boss | Bear Pelt (warm armour: no freezing in cold biomes) |
| 2 | Giant Irish Elk | highland moors, at a stone circle | none | Great Antlers (fast charge-dash tool / mount gear) |
| 3 | Hippopotamus | oasis and tropical rivers | none | Hippo Hide (water-walking boots: no slowness in water) |
| 4 | Giant Crocodile | fen, tropical rivers | Hippo trophy (lure bait) | Croc Scales (armour with underwater breathing) |
| 5 | Silverback Gorilla | rainforest, ruined Mayan temple (Ancient Structures) | any 3 trophies | Silverback Fists (knockback gauntlets) |
| 6 | Saber-tooth Cat | steppe, savanna | any 4 trophies | Saber Fangs (bleed-effect blade) |
| 7 | Woolly Rhinoceros | tundra, glacial outwash | Bear Pelt worn (cold) | Rhino Horn (block-breaking charge, shield upgrade) |
| 8 | Bull Elephant | golden savanna | any 6 trophies | Ivory (key crafting material for tier 2 gear) |
| 9 | Giant Bull Shark | northern/temperate ocean, fought from a Small Ships ship | Croc Scales | Shark Teeth (ship rams and harpoons) |
| 10 | Woolly Mammoth | glacier | all 9 Chapter 1 trophies | Mammoth Tusk + Frozen Heart (opens Chapter 2); tameable mammoth mount |

**Bridge: Civilizations**

The Frozen Heart leads into the Civilizations Norse storyline: defeat **Bjorn Ironside**, then face **Loki**. Beating Loki
releases his children and opens the way to the Norse gods. The other Civilizations leaders and gods stay optional side bosses
with their own rewards.

**Chapter 2: the Nine Worlds (netherite tier and beyond)**

| Order | Boss | Where | Unlock | Key drops |
|-------|------|-------|--------|-----------|
| 11 | Huginn and Muninn | above the highest mountain peaks | beat Loki | Feathers of Thought and Memory (reveal the other Norse bosses on a map) |
| 12 | Geri and Freki | ancient Norse hall (Ancient Structures German/Norse site) | ravens' feathers | Wolf-fang charms (pack buffs) |
| 13 | Sleipnir | sky above the steppe, at dawn | ravens' feathers | Sleipnir becomes rideable: flies and gallops on water |
| 14 | Skoll and Hati | glacier plateau, fought across a full day and night | Geri and Freki trophy | Sun and Moon shards (day/night armour set) |
| 15 | Garmr | the gate of Hel, deep below a volcano | Sun and Moon shards | Hel's Key (opens Nidhoggr's realm) |
| 16 | Nidhoggr | giant roots far underground | Hel's Key | Root of Yggdrasil (upgrade material) |
| 17 | Fafnir | treasure hoard in a mountain cave | Root of Yggdrasil | Cursed Gold, Fafnir's Heart (dragon-slayer blade) |
| 18 | Jormungandr | open ocean, from a warship | Fafnir's Heart | Serpent Scale (ultimate armour) |
| 19 | Fenrir | Ragnarok arena: final fight | all Chapter 2 trophies | Gleipnir, Fenrir's Fang (final weapon), credits |

### Boss locations: existing structures only (user rule: no custom arenas unless absolutely necessary)

Chapter 1 animals need no building: they are rare "alpha" spawns that roam their biome (one per region, boss bar
when you get close). The exceptions use structures that already exist.

| Boss | Location | From |
|------|----------|------|
| Silverback Gorilla | Mayan temple | Ancient Structures |
| Giant Bull Shark | open ocean, fought from a Small Ships ship | no structure |
| other Chapter 1 animals | roam their biomes | no structure |
| Huginn and Muninn | Viking tower (the ravens keep watch from it) | Nordic Adventure |
| Geri and Freki | Meadhall (Odin's hall, Valhalla) | Nordic Adventure |
| Sleipnir | floating sky island | MSS - Moog's Soaring Structures |
| Skoll and Hati | Viking fort | Nordic Adventure |
| Garmr | Nether fortress (the Nether is Hel; Garmr guards its gate) | YUNG's Better Nether Fortresses |
| Nidhoggr | Ancient City, deep underground among the roots | vanilla |
| Fafnir | Draugr Bastion treasure halls, cold mountains | Mebahel's Creatures - Draugr Invasion |
| Jormungandr | around a pirate ship in the open ocean | When Dungeons Arise: Seven Seas |
| Fenrir | central arena of the Draugr Crypt (largest, rarest dungeon) | Mebahel's Creatures - Draugr Invasion |

New structure mods this needs (all Fabric 1.20.1):
- **Nordic Adventure** (https://modrinth.com/mod/nordic-adventure): ARR, alpha, made with MCreator; benchmark it for lag.
  Longhouse, farmhouse, meadhall (with a boss), Draugr mine, Viking fort (Jarl Eirik Raudi), longboat, Viking village
  (Jarl Ivar the Boneless), Viking tower.
- **Mebahel's Creatures - Draugr Invasion** (https://modrinth.com/mod/mebahels-creatures-draugr): ARR. Needs Mebahel's API,
  Mebahel's Elder Scrolls Core and GeckoLib. Draugr Bastion, Crypt, Fort and Tower; its own Draugr Overlord boss and raid.
- **MSS - Moog's Soaring Structures** (https://modrinth.com/mod/mss-moogs-soaring-structures): GPL-3.0, floating islands.
- **When Dungeons Arise: Seven Seas** (https://modrinth.com/mod/when-dungeons-arise-seven-seas): hostile ships.
- **YUNG's Better Nether Fortresses** (with YUNG's API).

Open question: whether the Civilizations Egyptian, Chinese, Roman and Greek bosses get a role (optional side bosses for now).
