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

| 6 | Naturalist (Starfish Studios) | https://modrinth.com/mod/naturalist | Fabric 1.20.1: yes (5.0pre4, beta) | Assets ARR, code MIT | GeckoLib models: bear, deer, hippo, alligator, rhino, elephant, lion, giraffe, boar, zebra, ostrich, vulture, snakes, tortoise... (checked in the jar: no moose, no mammoth) | ok | CHOSEN: model source for Chapter 1: cave bear, hippo, crocodile (alligator), elephant. Needs GeckoLib (already in pack). |
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
| 2 | Giant Irish Elk | highland moors | Antler charges, knockback; calls a small herd | Fossils and Archeology megaloceros (the real Irish elk; Naturalist has no moose) |
| 3 | Hippopotamus | oasis, tropical rivers | Hides underwater then lunges; huge bite, capsizes boats | Naturalist hippo |
| 4 | Nile Crocodile (giant) | fen, tropical rivers | Ambush from water, death-roll grab | Naturalist alligator |
| 5 | Silverback Gorilla | rainforest, cloud forest | Chest-beat stun, boulder throws, ground pound | Animal Garden gorilla |
| 6 | Saber-tooth Cat | endless steppe, golden savanna | Stalks invisibly in tall grass, pounce and bleed | Fossils and Archeology smilodon (chosen) |
| 7 | Woolly Rhinoceros | tundra, glacial outwash | Unstoppable charges that break blocks; dodge into walls to stun it | Fossils and Archeology elasmotherium (Ice Age rhino; Naturalist rhino as fallback) |
| 8 | African Elephant bull | golden savanna | Stampede waves, trunk throw | Naturalist elephant |
| 9 | Bull Shark (giant) | northern and temperate oceans | Naval fight around your ship; breaches and rams | Animal Garden bull shark |
| 10 | Woolly Mammoth | glacier, tundra | Chapter 1 finale: tusk sweeps, trumpet shockwave, stomp quakes; maybe rideable reward | Fossils and Archeology mammoth (Naturalist has none) |

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
| 15 | Garmr | the gate of Hel: the sealed portal room of a stronghold | Sun and Moon shards | Hel's Key (opens Nidhoggr's realm) |
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
| Huginn and Muninn | Draugr Tower (the ravens keep watch from it) | Mebahel's Creatures - Draugr Invasion |
| Geri and Freki | Norse settlement (the jarl's hall) | Civilizations |
| Sleipnir | floating sky island | MSS - Moog's Soaring Structures |
| Skoll and Hati | Draugr Fort | Mebahel's Creatures - Draugr Invasion |
| Garmr | stronghold portal room: the sealed portal is the gate of Hel | YUNG's Better Strongholds |
| Nidhoggr | Ancient City, deep underground among the roots | vanilla |
| Fafnir | Draugr Bastion treasure halls, cold mountains | Mebahel's Creatures - Draugr Invasion |
| Jormungandr | around a pirate ship in the open ocean | When Dungeons Arise: Seven Seas |
| Fenrir | central arena of the Draugr Crypt (largest, rarest dungeon) | Mebahel's Creatures - Draugr Invasion |

New structure mods this needs (all Fabric 1.20.1):
- **Mebahel's Creatures - Draugr Invasion** (https://modrinth.com/mod/mebahels-creatures-draugr): ARR. Needs Mebahel's API,
  Mebahel's Elder Scrolls Core and GeckoLib. Draugr Bastion, Crypt, Fort and Tower; its own Draugr Overlord boss and raid.
  ADDED to the modpack (v0.18).
- ~~Nordic Adventure~~ (https://modrinth.com/mod/nordic-adventure): user liked it, but REJECTED: no Fabric 1.20.1 build
  (1.20.1 is Forge only; Fabric only for 1.21.8). Its bosses moved to the Draugr Tower, Draugr Fort and Civilizations.
- **MSS - Moog's Soaring Structures** (https://modrinth.com/mod/mss-moogs-soaring-structures): GPL-3.0, floating islands.
- **When Dungeons Arise: Seven Seas** (https://modrinth.com/mod/when-dungeons-arise-seven-seas): hostile ships.
- **YUNG's Better Strongholds** (with YUNG's API). (Better Nether Fortresses dropped: the Nether is closed.)

Open question: whether the Civilizations Egyptian, Chinese, Roman and Greek bosses get a role (optional side bosses for now).

## Pack rules (v0.19, mod "Vivid Lands: Ragnarok" in ragnarok/)

- **No Warden.** Sculk shriekers never summon one; they still shriek and give Darkness. Ancient Cities stay (Nidhoggr).
- **The Nether and the End are closed.** Obsidian frames never light, eyes of ender can't go into portal frames, and
  nothing can travel to either dimension ("That realm is sealed until Ragnarok").
- **Create** (create-fabric) makes everything those dimensions give, and **every Nether and End item is craftable
  from cobblestone**: each chain starts with cobblestone (or a block made from it) and only adds ordinary renewable
  Overworld items (lava, water, gold, ender pearls, diamonds...). Create already does cobblestone -> gravel (milling),
  gravel -> sand (crushing), cobblestone -> blackstone (haunting), netherrack -> cinder flour (crushing), plus soul
  campfires/torches/lanterns, nether bricks and fungi. Pack recipes (tools/ragnarok_recipes.py):

| Item | Machine | Recipe |
|------|---------|--------|
| Netherrack | mixing | cobblestone + 50 mB lava |
| Soul sand x2 | mixing | netherrack + sand (lights soul fire, which runs Create's haunting fans) |
| Soul soil x2 | mixing | soul sand + gravel |
| Basalt x2 | compacting | 2 cobblestone + 100 mB lava |
| Blackstone | haunting (Create) | cobblestone |
| Magma block | compacting | netherrack + 100 mB lava |
| Gilded blackstone | deploying | gold ingot onto blackstone |
| Crying obsidian | superheated mixing / haunting | 2 blackstone + 250 mB lava / obsidian |
| Nether gold ore, nether quartz ore | deploying | gold nugget / quartz onto netherrack |
| Ancient debris | superheated compacting | netherite scrap + blackstone |
| Nether wart | mixing | soul sand + cinder flour + 100 mB water |
| Crimson nylium | deploying | nether wart onto netherrack |
| Warped nylium | mixing | netherrack + soul soil + 100 mB water |
| Fungi, roots, sprouts, stems, wart blocks, shroomlight, vines | vanilla | bone meal on nylium, then grow huge fungi |
| Nether quartz | crushing | blackstone (50% + 25%) |
| Glowstone dust | heated mixing | 2 cinder flour + 50 mB lava |
| Magma cream x3-4 | crushing | magma block |
| Blaze rod | compacting | blackstone + 2 gold nuggets + 250 mB lava |
| Blaze burner | crafting | empty blaze burner + 4 blaze rods |
| Ghast tear | heated mixing | soul sand + quartz + 250 mB water |
| Wither skeleton skull | superheated mixing / haunting | 2 blackstone + bone block / skeleton skull (the Wither: nether stars, beacons) |
| Netherite scrap | superheated mixing | blackstone + diamond + 2 crushed raw gold + 500 mB lava |
| Netherite upgrade template | mechanical crafting | 7 diamonds + netherite scrap + netherrack (then duplicate as usual) |
| Rib / snout trims | mechanical crafting | 7 diamonds + wither skull and bone block / gold block and blackstone |
| Piglin head | mechanical crafting | skeleton skull + 4 blackstone + 4 gold ingots |
| Pigstep disc | mechanical crafting | diamond + 4 blackstone + 4 gold ingots |
| Snout banner pattern | crafting | paper + gilded blackstone |
| End stone x4 | mixing | 4 cobblestone + ender pearl |
| Chorus fruit x4 | mixing | end stone + ender pearl + 250 mB water |
| Chorus flower | mixing | end stone + ender pearl + bone meal (plant on end stone) |
| Purpur, end rods, popped chorus | vanilla | from chorus fruit |
| Shulker shell | heated mixing | purpur block + 2 ender pearls + popped chorus fruit |
| Dragon's breath | heated mixing | glass bottle + popped chorus fruit + blaze powder |
| Elytra | mechanical crafting | 6 phantom membranes + shulker shell + diamond + popped chorus fruit |
| Spire trim | mechanical crafting | 7 diamonds + shulker shell + purpur block |
| Dragon head | mechanical crafting | wither skeleton skull + 4 end stone + 4 purpur blocks |
| Dragon egg | mechanical crafting (5x5) | nether star + 4 dragon heads + 4 shulker shells + 16 end stone |


**Cobblestone Generators MK1-MK5** (only this, from Kibe by lucaargolo, https://modrinth.com/mod/kibe, MPL-2.0): ported
into Vivid Lands: Ragnarok with Kibe's tiers, rates, recipes and textures; nothing else from Kibe. A 27-slot output
inventory that hoppers and Create funnels/chutes can pull from.

| Tier | Cobblestone per second | Recipe |
|------|------------------------|--------|
| MK1 | 0.2 | 5 cobblestone, water bucket, iron block, lava bucket, chest |
| MK2 | 0.8 | 4 MK1 + gold block |
| MK3 | 3.2 | 4 MK2 + diamond block |
| MK4 | 12.8 | 4 MK3 + emerald block |
| MK5 | 51.2 | 4 MK4 + netherite block |

## Pack test (v0.19, .github/workflows/packtest.yml)

Dedicated server with every server-side mod (178 mods loaded): starts cleanly, the Nether portal won't light, a pig in a
portal stays in the Overworld, all 24 Create recipes load. Generating 16,641 chunks took 6:28 (Vivid Lands with only BWG:
5:06), so the structure and creature mods cost about a quarter more generation time; pre-generate with Chunky.
Ancient Villages is single-player only (its Garden Trails library crashes dedicated servers).

Structure ids for boss spawns:
- Draugr Invasion: mebahelcreaturesdraugr:draugr_bastion, draugr_crypt, draugr_fort, draugr_tower (+ ruin, ruined_church, simple_grave)
- Civilizations: civilizations:nordic (also egypt, china, greece, rome)
- Ancient Structures: ancientstructures:mayan_temple, mayan_temple2-4, mayan_ruins, mayan_village (+ roman, german, japanese sites)
- Seven Seas: dungeons_arise_seven_seas:corsair_corvette, pirate_junk, small_yacht, unicorn_galleon, victory_frigate
- Strongholds: betterstrongholds:stronghold
- Moog's Soaring Structures: 35 sky structures (pick Sleipnir's when building him)

## Ships (v0.20)

- **Small Ships** (already in): sailing ships on the sea, including the Viking drakkar.
- **Valkyrien Skies 2** (https://modrinth.com/mod/valkyrien-skies, 2.4.11) + **Eureka! Ships** (https://modrinth.com/mod/eureka,
  1.6.3): airships. Build any ship out of blocks, place a ship helm and balloons, and fly it. Pack test: loads with
  everything else (181 mods); generation 6:50 for 16,641 chunks (6:28 without, within run-to-run noise).

## Quality of life (v0.20)

| Mod | What it does |
|-----|--------------|
| EMI | Recipe viewer (Create machine recipes included) |
| Jade | Shows what you're looking at: block or mob name, mod, health, machine status |
| Xaero's Minimap | Minimap with waypoints and death point |
| Xaero's World Map | Full-screen world map |
| AppleSkin | Food saturation and hunger previews |
| Mouse Tweaks | Drag and scroll to move items |
| Inventory Profiles Next | Sort inventories and chests, refill hotbar tools |
| Shulker Box Tooltip | See inside shulker boxes on hover |
| Enchantment Descriptions | Explains each enchantment in its tooltip |
| Controlling | Search keybinds and find clashes |
| Waystones | Fast travel across the world |
| way2wayfabric | Every waystone you find appears as a waypoint on Xaero's Minimap and World Map |
| Traveler's Backpack | Backpacks |
| Carry On | Pick up chests and animals |
| Universal Graves | Your items wait in a grave when you die |
| Polymorph | Choose between recipes with the same ingredients |
| Clumps | Merges XP orbs (less lag) |

Already in from the Fabulously Optimized base: Mod Menu, Zoomify, AdvancementInfo, Better Mount HUD, Continuity,
Borderless Mining, More Chat History, FastQuit.

## Armor and weapons (v0.20)

| Mod | What it adds |
|-----|--------------|
| Epic Knights: Shields, Armor and Weapons | Historical medieval armor, shields and weapons |
| Fantasy Armor + Fantasy Weapons | 13 fantasy sets with matching weapons |
| Immersive Armors | 9 sets: warrior, heavy, divine, skeleton, prismarine... |
| Armor of the Ages (already in) | Samurai, Roman, pharaoh, Anubis and other culture sets |
| Simply Swords | Spears, katanas, chakrams, rapiers and unique legendary weapons |
| Rogues & Warriors | Warrior (berserker) and rogue class gear and skills (needs Spell Engine) |
| Mythic Metals | Many new ores, each with tools, weapons and armor |
| Better Combat + Combat Roll | Swing animations, combos, dodge roll |

Skipped: Marium's Soulslike Weaponry (user: weapons not cool enough, and its bosses sit outside the story).

**Viking endgame sets (the pack's own, from boss drops; concept art first, docs/viking_armor/):**
Berserker (Chapter 1 trophies), Ulfhednar wolf-warrior (Geri and Freki, Skoll and Hati), Valkyrie (Huginn and Muninn,
Sleipnir), Jarl / Einherjar (Fafnir's gold, Jormungandr's scale; the best armor in the pack). Weapons: Fenrir's Fang,
Gungnir, Dane axe, round shield.

## Viking endgame armor in game (v0.21)

The four approved sets are real armor in Vivid Lands: Ragnarok: 16 pieces with 3D GeckoLib models generated from the
concept models (tools/concept/export_geckolib.py; 1,600-2,600 cubes per set, one 1024x256 texture each), set bonuses,
and recipes from the boss trophies (each tier upgrades the previous one: its piece goes in the middle of the recipe).

| Set | Defense (helm/chest/legs/boots) | Toughness | Knockback res. | Made from | Full-set bonus |
|-----|------------------|-----------|----------------|-----------|----------------|
| Berserker | 3/7/6/3 | 1 | 0 | Cave Bear Pelt + Saber Fang | Strength below half health (II below a quarter) |
| Úlfheðinn | 3/8/6/3 | 2 | 0.05 | Pelt of Geri and Freki + Eclipse Shard | Speed; Night Vision at night |
| Valkyrie | 3/8/7/3 | 3 | 0.1 | Feather of Thought and Memory + Sleipnir's Mane | Jump Boost; Slow Falling as you fall |
| Jarl of the Einherjar | 4/9/7/4 | 4 | 0.15 | Jörmungandr's Scale + Fáfnir's Gold | Resistance; Fire Resistance |

The trophies exist as items now; the bosses will drop them once they are built (until then: creative tab
"Vivid Lands: Ragnarok").

## Weapons in game (v0.22)

15 weapons in Vivid Lands: Ragnarok, each with its 3D GeckoLib model generated from the concepts
(tools/concept/export_weapons.py) and a Better Combat swing style. Stats are placeholders (to be balanced later).

| Weapon | Kind | Swing style | How to get it (for now) |
|--------|------|-------------|-------------------------|
| Bearded Axe | axe | axe | iron axe + Cave Bear Pelt + Saber Fang |
| Wolf Seax | sword | dagger | iron sword + Pelt of Geri and Freki + Eclipse Shard |
| Valkyrie Sword | sword | sword | diamond sword + 2 Feathers of Thought and Memory + Sleipnir's Mane |
| Jarl's Dane Axe | axe | heavy axe | Bearded Axe + 2 Fáfnir's Gold + Jörmungandr's Scale |
| Gungnir | spear | spear | Odin's reward (creative until the bosses exist) |
| Fenrir's Fang | greatsword | claymore | Fenrir's drop (creative until the bosses exist) |
| Viking Round Shield | shield | - | shield + red dye + bone meal + iron ingot + leather |
| Khopesh, Dragon Guandao, Gladius, Kopis | civilization | cutlass / glaive / sword / cutlass | Civilizations leaders' drops (later) |
| Macuahuitl, Katana, Flamberge Zweihänder | civilization | mace / katana / claymore | Ancient Structures bosses (later) |
| Ragnarök, Surtr's Blade | endgame, glowing molten core | claymore | Fenrir's Fang + 2 netherite ingots + magma block + blaze rod + Fáfnir's Gold + Jörmungandr's Scale |

## Bosses (v0.23, code in ragnarok/src/main/java/com/vividlands/ragnarok/boss)

How they work: each boss is a real creature from another mod, spawned as itself (so it keeps that mod's model, animations
and sounds; nothing is copied), then made into a boss: drawn and hit-boxed bigger, much more health, armour and damage,
a boss bar for everyone within 48 blocks, special moves on cooldowns, an enraged phase below half health (faster,
harder hitting, moves come back sooner), immune to falling, suffocating and drowning, can't be fed, tamed or ridden,
and back to full health if nobody fights it for 30 seconds. Beating one drops its trophy, gives a lot of XP, and counts
for everyone who fought it ("Skadi's trials: 3 of 10 complete"). Creature ids were checked in the mod jars (Mod inspect
workflow). Stats are placeholders, to be balanced later.

Where they appear: the wild bosses roam their home biomes. Every 30 s a player in a boss's biome has a 1 in 6 chance to
meet it 28-48 blocks away, if no other boss is near, the player has unlocked it, and it hasn't appeared in that
1024 x 1024 region before. The Silverback appears once per Mayan temple when a player who unlocked it walks in.
Gamerule `vividlandsBossSpawning` turns natural appearances off. Commands (operators): `/ragnarok boss summon <id> [pos]`,
`list`, `progress <player>`, `forget <player>`, `resetspawns`.

| # | Boss (id) | Creature (fallbacks) | Home | Unlocks after | Moves | Drops |
|---|-----------|----------------------|------|---------------|-------|-------|
| 1 | Cave Bear, Den-Mother of the Pines (cave_bear) | naturalist:bear (polar bear), x1.7 | taiga lakelands, Caledonian pinewood, boreal snowwoods, any taiga | - | own bite and swipe; roar (slows, weakens); 3-swipe maul; rearing ground smash | Cave Bear Pelt |
| 2 | Great Irish Elk, Lord of the Moors (irish_elk) | fossil:megaloceros (goat) | highland moors, alpine meadow, meadow | - | antler charge (stunned if it hits a wall); calls 2 elk; rearing stomp | Great Antlers |
| 3 | Hippopotamus, Terror of the Oasis (hippo) | naturalist:hippo (ravager), x1.5 | oasis, tropical river, river | - | own bite, attacks boats; lunge out of the water; capsizes boats and ships; double chomp | Hippo Hide |
| 4 | Giant Crocodile, the River's Jaws (crocodile) | naturalist:alligator, x2.0 | fen, tropical river, swamp, mangrove | Hippopotamus | death roll (holds you in its jaws; hit it hard to break free); water lunge; tail sweep | Crocodile Scales |
| 5 | Silverback, King of the Temple (silverback) | animalgarden_westerngorilla:westerngorilla (iron golem), x1.4 | Mayan temples (Ancient Structures) | any 3 | own punches; chest-beat roar (stuns); throws boulders; ground pound | Silverback Fist |
| 6 | Saber-tooth, the Unseen Hunter (saber_tooth) | fossil:smilodon (wolf) | endless steppe, golden savanna, wildflower prairie, savanna | any 4 | invisible while it stalks from afar; pounce (heavy bleeding); 4-bite maul; every bite bleeds | Saber Fang |
| 7 | Woolly Rhinoceros, the Tundra Ram (woolly_rhino) | fossil:elasmotherium (naturalist:rhino, ravager) | tundra, glacial outwash, snowy plains | Cave Bear | charge that smashes through soft blocks (dirt, sand, snow, leaves, glass) and is stunned by hard ones; stomp (slows) | Rhino Horn |
| 8 | Bull Elephant, Thunder of the Savanna (elephant) | naturalist:elephant (ravager), x1.3 | golden savanna, savanna | any 6 | own attacks; stampede charge; trunk fling (throws you high); trumpet (weakens); stomp | Ivory x2 |
| 9 | Giant Bull Shark, Blood in the Water (bull_shark) | animalgarden_bullshark:bullshark (dolphin), x2.0 | northern and temperate oceans, deep oceans | Crocodile | breach (leaps out of the water at you, heavy bleeding); rams boats and ships; bite flurry; every bite bleeds | Shark Tooth x2 |
| 10 | Woolly Mammoth, Skadi's Last Trial (mammoth) | fossil:mammoth (ravager) | glacier, glacier peaks, ice spikes | all other 9 | trumpet shockwave (jump over the ring); stomp quake (slows); block-smashing charge; tusk fling | Mammoth Tusk x2, Frozen Heart |

New: the Bleeding effect (1 damage a second per level, red particles) and thrown boulders (Silverback).
Chapter 2 bosses come next (Huginn and Muninn, Geri and Freki, Sleipnir, Skoll and Hati, Garmr, Nidhoggr, Fafnir,
Jormungandr, Fenrir), using the structures listed above.
