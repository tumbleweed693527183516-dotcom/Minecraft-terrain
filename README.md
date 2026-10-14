# Vivid Lands

Huge, vivid world generation for Minecraft **1.20.1** (Fabric).

Taller worlds (build limit y=511), continent-sized landmasses, and new biomes inspired by Iceland, Scotland and the great deserts.

## Blocks (v0.7)

Black sand, volcanic ash, salt crust, peat, heather, dry grass, and three woods - palm, redwood and Scots pine (log, leaves, planks) - with matching trees: drooping-frond palms, giant redwoods, orange-barked Scots pines and spreading giant oaks. All textures are drawn by `tools/textures.py`; blocks are defined once in `tools/blocks.py`.

## Viking structures (v0.9)

- **Viking villages** (moors, pinewoods, lakelands, lava fields, outwash plains, tundra, basalt highlands): a plaza with a bell and fire pit, winding paths, longhouses (shingle or turf roofs), Icelandic turf houses, a smithy, raised storehouses, farms and sheep pens - assembled differently every time, inhabited by villagers. They replace vanilla villages in these biomes.
- **Longhouses** and **turf houses** standing alone as homesteads, with villagers.
- **Longships** with striped sails, shields and a captain's chest, out on northern seas.
- **Runestones**, stone circles and cairns across the north.

Structures are defined in `tools/structures/designs.py` and spawn by biome tag, so other structure mods keep working.

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

## Compatibility

- Performance mods (Sodium, Lithium, C2ME, FerriteCore, ModernFix), Iris shaders, Distant Horizons: no code changes to the game, terrain is pure data.
- Structure mods (YUNG's, dungeon and boss mods): biomes carry vanilla and `c:` convention tags so structures find them.
- Cave mods: the vanilla cave system is kept as its own density function (`vividlands:overworld/caves`).
- Not compatible with other full terrain overhauls such as Terralith or Tectonic.

## Development

World data is generated: edit `tools/generate.py`, then run `python3 tools/generate.py` and `python3 tools/check.py`. The Java part (real-world mountain stamps) builds with `gradle build` (Fabric Loom, Java 17).

Real mountains come from `tools/stamps/fetch_stamps.py` (run by the "Fetch mountain stamps" workflow) and live in `src/main/resources/vividlands_stamps/`. See `STAMPS_ATTRIBUTION.md`.

Every push builds automatically on GitHub (Actions tab → latest run → `vivid-lands` artifact).
