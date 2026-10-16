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

| 6 | Naturalist (Starfish Studios) | https://modrinth.com/mod/naturalist | Fabric 1.20.1: yes (5.0pre4, beta) | Assets ARR, code MIT | GeckoLib models: bear, moose, deer, hippo, alligator, rhino, elephant, mammoth, lion, giraffe, boar, ostrich, vulture, snake, tortoise, capybara... | candidate | Model source for Chapter 1: cave bear, elk (moose), hippo, crocodile (alligator), woolly rhino, elephant, mammoth. Needs GeckoLib (already in pack). |
| 7 | Animal Garden series (Aquarius.playz) | https://modrinth.com/user/Aquarius.playz | Fabric 1.20.1: yes (one mod per animal) | ARR | Western Gorilla, Bull Shark, Crocodile, Hippopotamus, White Rhinoceros, Bison, Lion, Snow Leopard, Spotted Hyena... | candidate | Fills the gaps: gorilla, shark, bison/buffalo. Install only the animals used. |
| 8 | Fossils and Archeology: Revival | https://modrinth.com/mod/fossils-and-archeology-revival | Fabric 1.20.1: yes (9.3.4.0) | FA License | 60+ prehistoric creatures incl. mammoth, smilodon (saber-tooth), terror bird, dodo, dinosaurs (revived from fossils/DNA) | candidate | Only needed for a true saber-tooth; brings a whole dinosaur system with it. Several dependencies. |

| 9 | Animal Garden - Common Raven | https://modrinth.com/mod/animal-garden-common-raven | Fabric 1.20.1: yes | ARR | Raven | candidate | Model for Huginn and Muninn. |
| 10 | Backported Wolves | https://modrinth.com/mod/backported-wolves | Fabric 1.20.1: yes | MIT | The newer wolf coat variants (ashen, black, chestnut, rusty, snowy, spotted, striped, woods) | candidate | Distinct coats for Geri, Freki, Skoll, Hati, Garmr and a giant black Fenrir on the vanilla wolf model. |
| 11 | Saint's Dragons | https://modrinth.com/mod/saints-dragons | Fabric 1.20.1: yes | Dual licence | Animated, tameable, rideable dragons | candidate | Model for Fafnir (and possibly Nidhoggr). |
| 12 | Useless Reptile | https://modrinth.com/mod/useless-reptile | Fabric 1.20.1: listed (author says older versions unsupported) | ARR (submods allowed) | Swamp Wyvern, Moleclaw (cave burrower), River Pikehorn, Lightning Chaser, Magmamuncher | candidate | Alternative dragon models; Moleclaw could suit a burrowing Nidhoggr. Needs YACL. |
| 13 | Myths of the Sea | https://modrinth.com/mod/myths-of-the-sea | 1.20.1 listed; Fabric 1.20.1 not confirmed yet | ARR | Leviathan, Kraken, Hippocampus, Bunyip, Bake Kujira, Abaia | candidate | Leviathan as a possible Jormungandr model; check the Fabric build. |

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
| 1 | Cave Bear | taiga lakelands, Caledonian pinewood (cave lair) | Swipes, rearing roar that slows you; a good first boss | pending |
| 2 | Giant Irish Elk | highland moors | Antler charges, knockback; calls a small herd | pending |
| 3 | Hippopotamus | oasis, tropical rivers | Hides underwater then lunges; huge bite, capsizes boats | pending |
| 4 | Nile Crocodile (giant) | fen, tropical rivers | Ambush from water, death-roll grab | pending |
| 5 | Silverback Gorilla | rainforest, cloud forest | Chest-beat stun, boulder throws, ground pound | pending |
| 6 | Saber-tooth Cat | endless steppe, golden savanna | Stalks invisibly in tall grass, pounce and bleed | Fossils and Archeology smilodon (chosen) |
| 7 | Woolly Rhinoceros | tundra, glacial outwash | Unstoppable charges that break blocks; dodge into walls to stun it | pending |
| 8 | Cape Buffalo bull / African Elephant bull | golden savanna | Stampede waves, trunk throw (elephant) | pending |
| 9 | Great White Shark / Orca | northern and temperate oceans | Naval fight around your ship; breaches and rams | pending |
| 10 | Woolly Mammoth | glacier, tundra | Chapter 1 finale: tusk sweeps, trumpet shockwave, stomp quakes; maybe rideable reward | pending |

### Chapter 2: Norse mythology - custom, models to be supplied

| Boss | Who | Fight ideas (draft) | Model |
|------|-----|---------------------|-------|
| Huginn and Muninn | Odin's ravens, Thought and Memory | Twin flying fight: one dives and strikes, the other blinds or confuses; kill both within a short window or the survivor revives the other | pending |
| Geri and Freki | Odin's wolves | Pack duo: flanking charges, howl that buffs the other, enrage when one falls | pending |
| Sleipnir | Odin's eight-legged horse, child of Loki | Fast arena charges and trampling, gallops through the air between phases; tamable or rideable reward possible | pending |
| Fenrir | Colossal wolf, child of Loki, slayer of Odin | Chained at the start: phases where he breaks Gleipnir link by link; huge bites, ground slams | pending |
| Skoll and Hati | Wolves chasing the sun and moon | Day and night pair: Skoll stronger by day, Hati by night; sky darkens or brightens as they win | pending |
| Garmr | Blood-stained hound at the gates of Hel | Gatekeeper of a Hel arena; summons draugr, life-steal bites | pending |
| Jormungandr | The Midgard Serpent, child of Loki | Ocean boss: surfaces around the ship or coast, coils, poison breath, tail slams; fits Small Ships naval combat | pending |
| Nidhoggr | Dragon gnawing Yggdrasil's roots | Underground or deep-cave fight among giant roots; corrosion and burrowing | pending |
| Fafnir | Dwarf turned dragon guarding cursed gold | Treasure-hoard lair; fire breath, flight, gold-greed mechanics (picking up gold enrages him); cursed-gold reward | pending |

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
