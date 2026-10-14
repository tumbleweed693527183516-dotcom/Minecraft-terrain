#!/usr/bin/env python3
"""Checks the generated data: valid JSON, and every vividlands:/minecraft: ID it uses is known."""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "main" / "resources" / "data"

# Vanilla 1.20.1 IDs this mod relies on, grouped by registry.
VANILLA = {
    "density_function": {
        "overworld_large_biomes/offset", "overworld_large_biomes/factor", "overworld_large_biomes/jaggedness",
        "overworld_large_biomes/continents", "overworld_large_biomes/erosion", "overworld/ridges",
        "overworld/base_3d_noise", "overworld/caves/entrances", "overworld/caves/noodle",
        "overworld/caves/pillars", "overworld/caves/spaghetti_2d",
        "overworld/caves/spaghetti_roughness_function", "y", "shift_x", "shift_z",
    },
    "placed_feature": {
        "lake_lava_underground", "amethyst_geode", "monster_room", "monster_room_deep", "spring_water",
        "spring_lava", "freeze_top_layer", "patch_sugar_cane", "brown_mushroom_normal", "red_mushroom_normal",
        "ore_dirt", "ore_gravel", "ore_granite_upper", "ore_granite_lower", "ore_diorite_upper",
        "ore_diorite_lower", "ore_andesite_upper", "ore_andesite_lower", "ore_tuff", "ore_coal_upper",
        "ore_coal_lower", "ore_iron_upper", "ore_iron_middle", "ore_iron_small", "ore_gold", "ore_gold_lower",
        "ore_redstone", "ore_redstone_lower", "ore_diamond", "ore_diamond_large", "ore_diamond_buried",
        "ore_lapis", "ore_lapis_buried", "ore_copper",
    },
    "carver": {"cave", "cave_extra_underground", "canyon"},
}


def load_all():
    files = {}
    for p in DATA.rglob("*.json"):
        try:
            files[p] = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            sys.exit(f"Invalid JSON in {p}: {e}")
    return files


def own_ids():
    ids = {}
    for p in DATA.glob("vividlands/worldgen/*/**/*.json"):
        reg = p.relative_to(DATA / "vividlands" / "worldgen").parts[0]
        rest = p.relative_to(DATA / "vividlands" / "worldgen" / reg).with_suffix("").as_posix()
        ids.setdefault(reg, set()).add(rest)
    return ids


def main():
    files = load_all()
    own = own_ids()
    errors = []

    def need(reg, ident, where):
        ns, path = ident.split(":", 1)
        pool = own.get(reg, set()) if ns == "vividlands" else VANILLA.get(reg, set())
        if path not in pool:
            errors.append(f"{where}: unknown {reg} {ident}")

    for p, obj in files.items():
        rel = p.relative_to(DATA).as_posix()
        if "/worldgen/biome/" in rel and rel.startswith("vividlands"):
            for step in obj["features"]:
                for f in step:
                    need("placed_feature", f, rel)
            for c in obj["carvers"]["air"]:
                need("carver", c, rel)
            # same feature must never appear twice in one biome
            flat = [f for step in obj["features"] for f in step]
            if len(flat) != len(set(flat)):
                errors.append(f"{rel}: duplicate feature")
        if "/placed_feature/" in rel and isinstance(obj["feature"], str):
            need("configured_feature", obj["feature"], rel)
        if "/density_function/" in rel or "/noise_settings/" in rel:
            for ident in re.findall(r'"((?:minecraft|vividlands):[a-z0-9_/]+)"', json.dumps(obj)):
                ns, path = ident.split(":", 1)
                if (ns == "vividlands" and path in own.get("density_function", set())) or \
                        (ns == "minecraft" and path in VANILLA["density_function"]):
                    need("density_function", ident, rel)
    biomes_used = {e["biome"] for e in files[DATA / "minecraft/dimension/overworld.json"]["generator"]
                   ["biome_source"]["biomes"]}
    for b in sorted(biomes_used):
        if b.startswith("vividlands:") and b.split(":")[1] not in own["biome"]:
            errors.append(f"biome map: missing biome {b}")
    unused = own["biome"] - {b.split(":")[1] for b in biomes_used if b.startswith("vividlands:")}
    if unused:
        errors.append(f"biomes never placed: {sorted(unused)}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(files)} files, {len(biomes_used)} biomes in the map")
    print("Biomes:", ", ".join(sorted(biomes_used)))


if __name__ == "__main__":
    main()
