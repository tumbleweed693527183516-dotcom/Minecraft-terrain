# Vivid Lands

Huge, vivid world generation for Minecraft **1.20.1** (Fabric).

Taller worlds (build limit y=511), continent-sized landmasses, and new biomes inspired by Iceland, Scotland and the great deserts.

## Biomes (v0.4)

44 biomes replace the vanilla overworld (vanilla caves, mushroom islands and mangroves stay). Every biome has its own water, sky, fog, grass and foliage colours.

- **Oceans:** glacial (icebergs), northern (kelp), temperate, tropical (turquoise, coral) - each with a deep variant
- **Coasts & rivers:** snowy shore, basalt shore, golden beach, tropical beach, rocky cliffs, glacial river (milky teal), clearwater river, tropical river, oasis
- **Frozen:** glacier peaks, glacier (blue ice, ice spires), tundra, boreal snowwoods
- **Iceland & Scotland:** volcanic cones, highland crags, basalt highlands, highland moors, Caledonian pinewood, taiga lakelands
- **Temperate:** alpine peaks, jagged spires, alpine meadow, endless steppe, wildflower prairie, mixed woodland, autumn woodland, old-growth oakwood, redwood giants, fen
- **Warm & hot:** golden savanna, rainforest, cloud forest, red canyonlands, great erg, rocky hamada, salt flats

Terrain: Earth-style mountain ranges built from a warped ridged multifractal - broad massifs, branching ridgelines, pointed horn summits (Matterhorn-style, where two ridge systems cross) up to about y=455, V-shaped valleys and river gorges cutting through. Vanilla plateaus are flattened out, and slopes are smoother than vanilla.

## Installing for testing

- **Mod:** put `vividlands-<version>.jar` in your Fabric 1.20.1 `mods` folder with **Fabric API**.
- **Datapack:** add `VividLands-datapack-<version>.zip` when creating a world (works without any mod loader).

Always create a **new world**. Do not add this to an existing world.

## Compatibility

- Performance mods (Sodium, Lithium, C2ME, FerriteCore, ModernFix), Iris shaders, Distant Horizons: no code changes to the game, terrain is pure data.
- Structure mods (YUNG's, dungeon and boss mods): biomes carry vanilla and `c:` convention tags so structures find them.
- Cave mods: the vanilla cave system is kept as its own density function (`vividlands:overworld/caves`).
- Not compatible with other full terrain overhauls such as Terralith or Tectonic.

## Development

All data is generated. Edit `tools/generate.py`, then:

```
python3 tools/generate.py   # write the JSON
python3 tools/check.py      # validate references
python3 tools/build.py      # package jar + datapack into build/
```

Every push builds automatically on GitHub (Actions tab → latest run → `vivid-lands` artifact).
