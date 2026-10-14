# Vivid Lands

Huge, vivid world generation for Minecraft **1.20.1** (Fabric).

Taller worlds (build limit y=511), continent-sized landmasses, and new biomes inspired by Iceland, Scotland and the great deserts.

## Blocks

Palisade stakes, thatch (block, stairs, slab), wattle and daub, carved posts, painted wall shields, black sand, volcanic ash, salt crust, peat, heather, dry grass, and three woods - palm, redwood and Scots pine (log, leaves, planks) - with matching trees: drooping-frond palms, giant redwoods, orange-barked Scots pines and spreading giant oaks. All textures are drawn by `tools/textures.py`; blocks are defined once in `tools/blocks.py`.

## Viking structures (v0.12)

- **Walled Viking villages** (moors, pinewoods, lakelands, lava fields, outwash plains, tundra, basalt highlands): a ring palisade of sharpened logs that follows the ground, 2-3 gatehouses with walkways, watchtowers, a central plaza with a covered well, bell and runestones, a chieftain's great hall (45 blocks long), longhouses in three sizes with shingle, thatch or turf roofs, Glaumbær-style turf farmsteads, a forge with a chimney, a temple, a market, stabbur storehouses, a granary, a byre, a weaving pit-house, a training yard, paths to every door, and fields and sheep folds outside the walls. Built by a custom generator (`com.vividlands.village`) so every village is laid out differently, inhabited by villagers. They replace vanilla villages in these biomes.
- **Level sites:** before a village or fortress is built its ground is graded into a level plateau (hills cut, hollows and ponds filled, with the local surface blocks), blending back into the land outside the walls.
- **Details on every building:** shuttered windows with flower boxes, covered entrance porches with banners on timber halls, painted shields under the eaves, smoke rising from the roof vents, gravel drip edges with plants, rugs, and yards with woodpiles, chopping blocks, carts, hide frames, water barrels, hay and lantern posts.
- **Trelleborg ring fortresses** (rare): a perfectly round earthen rampart with a palisade on its crest and a ditch outside, four gates on the compass points, cross streets, watchtowers and rows of garrison halls in the four quarters.
- **Burial mounds** (dungeons): a grassy mound ringed by standing stones; a timbered passage with an arrow trap leads down to a stone chamber with a bier, grave goods, a caged spawner and armoured *Draugr*.
- **Ship burials** (rare dungeons): a whole longship laid in a timber chamber under a great mound, guarded by draugr, two spawners and the **Draugr Jarl** (80 health, diamond axe), with the richest loot in the mod.
- **Stave churches**: tiered dark-wood roofs, a covered gallery, dragon heads on every roof edge, a bell spire, benches and an altar, with runestones in the churchyard.
- **Mead halls**: a chieftain's great hall standing alone in a fenced yard with carved gate posts, a cart, woodpile, hide frame, kitchen garden, horses and chickens.
- **Fishing hamlets** on northern shores: turf and thatch huts, a boathouse with a boat, fish-drying racks and a jetty.
- **Thing sites**: open-air assemblies with a stepped law rock, rings of stone seats, coloured booths, fires and banner poles.
- **Shielings** (summer huts with a dry-stone sheep fold) and **beacon cairns** on the hills.
- **Longhouses**, **turf farmsteads** and **cottages** standing alone as homesteads.
- **Longships** and **knarr** cargo ships out on northern seas, **shipwrecks** on the sea floor, and **frozen longships** locked in glacier ice with draugr guarding the treasure.
- **Runestones**, stone circles and cairns across the north.

Building designs live in `tools/structures/viking.py` and `viking2.py` (helpers in `kit.py`); they are written to structure templates by `tools/generate.py`.

## Biomes

44 biomes replace the vanilla overworld (vanilla caves, mushroom islands and mangroves stay). Every biome has its own water, sky, fog, grass and foliage colours.

- **Oceans:** glacial (icebergs), northern (kelp), temperate, tropical (turquoise, coral) - each with a deep variant
- **Coasts & rivers:** snowy shore, basalt shore, golden beach, tropical beach, rocky cliffs, glacial river (milky teal), clearwater river, tropical river, oasis
- **Frozen:** glacier peaks, glacier (blue ice, ice spires), tundra, boreal snowwoods
- **Iceland & Scotland:** volcanic cones, highland crags, basalt highlands, highland moors, Caledonian pinewood, taiga lakelands
- **Temperate:** alpine peaks, jagged spires, alpine meadow, endless steppe, wildflower prairie, mixed woodland, autumn woodland, old-growth oakwood, redwood giants, fen
- **Warm & hot:** golden savanna, rainforest, cloud forest, red canyonlands, great erg, rocky hamada, salt flats

Terrain: basin-and-range mountains, like the Wasatch rising out of the Salt Lake valley - flat basins, steep mountain fronts leaping straight out of them, long winding ranges with a jagged crest and pointed horn summits up to about y=385, and river gorges cutting through. Mountain biomes follow the actual ranges; basins keep lowland biomes.

## Installing for testing

- **Mod:** put `vividlands-<version>.jar` in your Fabric 1.20.1 `mods` folder with **Fabric API**.
- **Test pack:** import `VividLands-TestPack-<version>.mrpack` into the Modrinth App.

Always create a **new world**. Do not add this to an existing world.

## Loot

Every village building has two or three chests (one for fields, gates and towers), filled from its own table `vividlands:chests/village/<building>`. Two empty hook tables let you add your own loot without replacing anything:

- `vividlands:chests/extra/village`: added to every village and fortress chest.
- `vividlands:chests/extra/everywhere`: added to every Vivid Lands chest.

Override them with a datapack (an example ships as `VividLands-Loot-Datapack.zip`).

## Compatibility

- Performance mods (Sodium, Lithium, C2ME, FerriteCore, ModernFix), Iris shaders, Distant Horizons: no code changes to the game, terrain is pure data.
- Structure mods (YUNG's, dungeon and boss mods): biomes carry vanilla and `c:` convention tags so structures find them.
- Cave mods: the vanilla cave system is kept as its own density function (`vividlands:overworld/caves`).
- Not compatible with other full terrain overhauls such as Terralith or Tectonic.

## Development

World data is generated: edit `tools/generate.py`, then run `python3 tools/generate.py` and `python3 tools/check.py`. The Java part (real-world mountain stamps) builds with `gradle build` (Fabric Loom, Java 17).

Real mountains come from `tools/stamps/fetch_stamps.py` (run by the "Fetch mountain stamps" workflow) and live in `src/main/resources/vividlands_stamps/`. See `STAMPS_ATTRIBUTION.md`.

Every push builds automatically on GitHub (Actions tab → latest run → `vivid-lands` artifact).
