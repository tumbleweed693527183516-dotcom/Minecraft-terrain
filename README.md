# Vivid Lands

Huge, vivid world generation for Minecraft **1.20.1** (Fabric).

Taller worlds (build limit y=447), continent-sized landmasses, and new biomes inspired by Iceland, Scotland and the great deserts.

## Biomes (v0.1)

| Biome | Feel |
|---|---|
| Volcanic Cones | Blackstone and basalt peaks, magma veins, lava pools, ash in the air, snow caps above y=300 |
| Basalt Highlands | Black rock and bright moss, basalt column clusters, glacial-teal water |
| Highland Moors | Heather-purple grass, pink heather carpets, azalea shrubs, mossy boulders, lone pines |
| Great Erg | Endless sand, sandstone hoodoos |
| Oasis | Palm-lined water channels winding through the Erg |
| Old-Growth Oakwood | Giant branching oaks, mossy floor, ferns |

Vanilla biomes fill the rest of the world and all of them are reshaped by the taller terrain.

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
