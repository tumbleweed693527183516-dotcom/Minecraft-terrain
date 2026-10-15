# Vivid Lands

Huge, vivid world generation for Minecraft **1.20.1** (Fabric).

Taller worlds (build limit y=511), continent-sized landmasses, and new biomes inspired by Iceland, Scotland and the great deserts.

## Blocks

Vivid Lands adds no blocks of its own. Terrain uses blocks from **[Oh The Biomes We've Gone](https://modrinth.com/mod/oh-the-biomes-weve-gone)** (palm, pine and redwood trees, black and white sand, white sandstone, peat, dacite, red rock, purple sage, prairie grass) and vanilla. It is required, with its libraries TerraBlender, CorgiLib, Oh The Trees You'll Grow and GeckoLib. Its own biomes are switched off in the Vivid Lands overworld, so only its blocks appear. The mapping lives in `tools/modblocks.py`.

## Biomes

44 biomes replace the vanilla overworld (vanilla caves, mushroom islands and mangroves stay). Every biome has its own water, sky, fog, grass and foliage colours.

- **Oceans:** glacial (icebergs), northern (kelp), temperate, tropical (turquoise, coral) - each with a deep variant
- **Coasts & rivers:** snowy shore, basalt shore, golden beach, tropical beach, rocky cliffs, glacial river (milky teal), clearwater river, tropical river, oasis
- **Frozen:** glacier peaks, glacier (blue ice, ice spires), tundra, boreal snowwoods
- **Iceland & Scotland:** volcanic cones, highland crags, basalt highlands, highland moors, Caledonian pinewood, taiga lakelands
- **Temperate:** alpine peaks, jagged spires, alpine meadow, endless steppe, wildflower prairie, mixed woodland, autumn woodland, old-growth oakwood, redwood giants, fen
- **Warm & hot:** golden savanna, rainforest, cloud forest, red canyonlands, great erg, rocky hamada, salt flats

Terrain: basin-and-range mountains, like the Wasatch rising out of the Salt Lake valley - flat basins, steep mountain fronts leaping straight out of them, long winding ranges with a jagged crest and pointed horn summits up to about y=385, and river gorges cutting through. Mountain biomes follow the actual ranges; basins keep lowland biomes.

## The Vivid Lands modpack

`VividLands-Modpack-<version>.mrpack` (import it into the Modrinth App or Prism Launcher) is built on the client set of
[Fabulously Optimized](https://github.com/Fabulously-Optimized/fabulously-optimized) for 1.20.1 (BSD-3; its licence
ships with the pack) with every mod updated to its newest 1.20.1 release, plus what a heavy world generator needs:

- **Rendering:** Sodium, Sodium Extra, Reese's Sodium Options, Indium, ImmediatelyFast, Entity Culling, MoreCulling, Enhanced Block Entities, Model Gap Fix, BadOptimizations, Continuity
- **Game logic and memory:** Lithium, FerriteCore, ModernFix, Memory Leak Fix, Debugify, Dynamic FPS (idles when the window is in the background)
- **World generation:** C2ME (multi-threaded chunk generation) and Chunky (pre-generate an area: `/chunky radius 2000` then `/chunky start`)
- **Visuals:** Iris with Complementary Reimagined (off by default, press K), Distant Horizons (far terrain built from the surface shape only)
- **Quality of life:** Mod Menu, Zoomify (C), FastQuit, Remove Reloading Screen, Language Reload, AdvancementInfo, Better Mount HUD, Borderless Mining, More Chat History, No Chat Reports
- **Adding your own mods safely:** MixinTrace (names the mod behind a crash), YOSBR (the pack's default settings are applied once and never overwrite yours), Cloth Config, YetAnotherConfigLib, Fabric Language Kotlin

Default settings come from Fabulously Optimized's tuned configs with render distance 10, simulation distance 6, smaller biome blend and fewer particles.

Give the instance **6-8 GB of RAM** (Modrinth App: instance settings > Java and memory); raise it as you add more mods. Always create a **new world**.

## Performance

- The whole land shape (mountain ranges, real-world stamps, creeks) is one compiled density function, `vividlands:terrain_2d`, computed once per column: the terrain formula shrank from ~2,500 steps to ~180, so each chunk sets up far faster.
- Aquifers skip open sky: above the ground and sea level the water/lava/air check answers "air" at once (a mixin; identical results).
- Benchmark (same 16,641 chunks on a test server): vanilla 6:40, Vivid Lands before 7:36, now 5:06, with identical terrain.
- Open sky is skipped: above the terrain's smooth shape the 3D terrain, cave and entrance noise isn't computed at all (most of a 576-block-tall world).
- The 16-octave jagged-peaks noise is cached per column instead of being recomputed at every cell.
- Hot springs use vanilla's light water-patch feature instead of lakes.

## Compatibility

- Performance mods (Sodium, Lithium, C2ME, FerriteCore, ModernFix), Iris shaders, Distant Horizons: no code changes to the game, terrain is pure data.
- Structure mods (YUNG's, dungeon and boss mods): biomes carry vanilla and `c:` convention tags so structures find them. All vanilla structures generate (villages, strongholds, temples, mineshafts...).
- Cave mods: the vanilla cave system is kept as its own density function (`vividlands:overworld/caves`).
- Not compatible with other full terrain overhauls such as Terralith or Tectonic.

## Development

World data is generated: edit `tools/generate.py`, then run `python3 tools/generate.py` and `python3 tools/check.py`. The Java part (real-world mountain stamps) builds with `gradle build` (Fabric Loom, Java 17).

Real mountains come from `tools/stamps/fetch_stamps.py` (run by the "Fetch mountain stamps" workflow) and live in `src/main/resources/vividlands_stamps/`. See `STAMPS_ATTRIBUTION.md`.

Every push builds automatically on GitHub (Actions tab → latest run → `vivid-lands` artifact).
