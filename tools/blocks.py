#!/usr/bin/env python3
"""
Vivid Lands custom blocks: one list drives everything - Java registration
(generated ModBlocks.java), blockstates, models, item models, loot tables,
tags, recipes and names. Called by generate.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src/main/resources"
ASSETS = RES / "assets/vividlands"
JAVA = ROOT / "src/main/java/com/vividlands/ModBlocks.java"

# name: (kind, English name, extra)
BLOCKS = {
    "black_sand": ("sand", "Black Sand", {"dust": 0x2A2A30, "copy": "SAND", "map": "COLOR_BLACK"}),
    "volcanic_ash": ("sand", "Volcanic Ash", {"dust": 0x75736F, "copy": "GRAVEL", "map": "COLOR_GRAY"}),
    "salt_crust": ("cube", "Salt Crust", {"copy": "CALCITE", "tool": "pickaxe"}),
    "peat": ("cube", "Peat", {"copy": "COARSE_DIRT", "tool": "shovel"}),
    "sinter": ("cube", "Sinter", {"copy": "CALCITE", "tool": "pickaxe"}),
    "travertine": ("cube", "Travertine", {"copy": "CALCITE", "tool": "pickaxe"}),
    "thermal_mat": ("cube", "Thermal Mat", {"copy": "MUD", "tool": "shovel"}),
    "sulfur_crust": ("cube", "Sulfur Crust", {"copy": "CALCITE", "tool": "pickaxe"}),
    "heather": ("flower", "Heather", {}),
    "dry_grass": ("dry_plant", "Dry Grass", {}),
    "palm_log": ("log", "Palm Log", {}),
    "palm_leaves": ("leaves", "Palm Leaves", {}),
    "palm_planks": ("planks", "Palm Planks", {"log": "palm_log"}),
    "redwood_log": ("log", "Redwood Log", {}),
    "redwood_leaves": ("leaves", "Redwood Leaves", {}),
    "redwood_planks": ("planks", "Redwood Planks", {"log": "redwood_log"}),
    "pine_log": ("log", "Scots Pine Log", {}),
    "pine_leaves": ("leaves", "Scots Pine Leaves", {}),
    "pine_planks": ("planks", "Scots Pine Planks", {"log": "pine_log"}),
    # Viking building blocks
    "thatch": ("thatch", "Thatch", {}),
    "thatch_stairs": ("stairs", "Thatch Stairs", {"base": "thatch"}),
    "thatch_slab": ("slab", "Thatch Slab", {"base": "thatch"}),
    "wattle_daub": ("cube", "Wattle and Daub", {"copy": "MUD_BRICKS", "tool": "pickaxe"}),
    "carved_post": ("pillar", "Carved Post", {}),
    "palisade_stake": ("stake", "Palisade Stake", {}),
    "shield_red": ("shield", "Red Shield", {}),
    "shield_blue": ("shield", "Blue Shield", {}),
    "shield_yellow": ("shield", "Yellow Shield", {}),
    "shield_green": ("shield", "Green Shield", {}),
}


def jwrite(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def stairs_blockstate(m):
    base = {"east": 0, "south": 90, "west": 180, "north": 270}
    v = {}
    for facing, yaw in base.items():
        for half in ("bottom", "top"):
            for shape in ("straight", "inner_left", "inner_right", "outer_left", "outer_right"):
                model = m + ("_inner" if shape.startswith("inner") else "_outer" if shape.startswith("outer") else "")
                y = yaw
                if half == "bottom" and shape.endswith("left"):
                    y = yaw - 90
                if half == "top" and shape.endswith("right"):
                    y = yaw + 90
                entry = {"model": model}
                if half == "top":
                    entry["x"] = 180
                if y % 360:
                    entry["y"] = y % 360
                if "x" in entry or "y" in entry:
                    entry["uvlock"] = True
                v[f"facing={facing},half={half},shape={shape}"] = entry
    return {"variants": v}


def java_source():
    lines = []
    for name, (kind, _, x) in BLOCKS.items():
        const = name.upper()
        if kind == "sand":
            ctor = (f"new SandBlock(0x{x['dust']:06X}, BlockBehaviour.Properties.copy(Blocks.{x['copy']})"
                    f".mapColor(MapColor.{x['map']}))")
        elif kind == "cube":
            ctor = f"new Block(BlockBehaviour.Properties.copy(Blocks.{x['copy']}))"
        elif kind == "flower":
            ctor = "new FlowerBlock(MobEffects.REGENERATION, 5, BlockBehaviour.Properties.copy(Blocks.POPPY))"
        elif kind == "dry_plant":
            ctor = "new DeadBushBlock(BlockBehaviour.Properties.copy(Blocks.DEAD_BUSH).mapColor(MapColor.SAND))"
        elif kind == "log":
            ctor = "new RotatedPillarBlock(BlockBehaviour.Properties.copy(Blocks.OAK_LOG))"
        elif kind == "leaves":
            ctor = "new LeavesBlock(BlockBehaviour.Properties.copy(Blocks.OAK_LEAVES))"
        elif kind == "thatch":
            ctor = "new Block(BlockBehaviour.Properties.copy(Blocks.HAY_BLOCK).mapColor(MapColor.COLOR_YELLOW))"
        elif kind == "stairs":
            b = x["base"].upper()
            ctor = f"new ModStairBlock({b}.defaultBlockState(), BlockBehaviour.Properties.copy({b}))"
        elif kind == "slab":
            ctor = f"new SlabBlock(BlockBehaviour.Properties.copy({x['base'].upper()}))"
        elif kind == "pillar":
            ctor = "new RotatedPillarBlock(BlockBehaviour.Properties.copy(Blocks.SPRUCE_LOG))"
        elif kind == "stake":
            ctor = "new StakeBlock(BlockBehaviour.Properties.copy(Blocks.SPRUCE_LOG).noOcclusion())"
        elif kind == "shield":
            ctor = "new WallShieldBlock(BlockBehaviour.Properties.copy(Blocks.SPRUCE_PLANKS).noOcclusion())"
        else:
            ctor = "new Block(BlockBehaviour.Properties.copy(Blocks.OAK_PLANKS))"
        lines.append(f'    public static final Block {const} = register("{name}", {ctor});')
    cutout = [n.upper() for n, (k, _, _) in BLOCKS.items() if k in ("flower", "dry_plant", "shield")]
    mipped = [n.upper() for n, (k, _, _) in BLOCKS.items() if k == "leaves"]
    burn_rates = {"log": (5, 5), "planks": (5, 20), "leaves": (30, 60), "flower": (60, 100), "dry_plant": (60, 100),
                  "thatch": (60, 20), "stairs": (60, 20), "slab": (60, 20), "pillar": (5, 5), "stake": (5, 5),
                  "shield": (5, 20)}
    burn = [(n.upper(), burn_rates[k]) for n, (k, _, _) in BLOCKS.items() if k in burn_rates]
    return f'''// GENERATED by tools/blocks.py - edit the block list there, not this file.
package com.vividlands;

import net.fabricmc.fabric.api.registry.FlammableBlockRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

import java.util.ArrayList;
import java.util.List;

public final class ModBlocks {{
    public static final List<Block> ALL = new ArrayList<>();

{chr(10).join(lines)}

    public static final List<Block> CUTOUT = List.of({", ".join(cutout)});
    public static final List<Block> CUTOUT_MIPPED = List.of({", ".join(mipped)});

    private ModBlocks() {{
    }}

    private static Block register(String name, Block block) {{
        ResourceLocation id = new ResourceLocation(VividLands.MOD_ID, name);
        Registry.register(BuiltInRegistries.BLOCK, id, block);
        Registry.register(BuiltInRegistries.ITEM, id, new BlockItem(block, new Item.Properties()));
        ALL.add(block);
        return block;
    }}

    static void init() {{
        FlammableBlockRegistry fire = FlammableBlockRegistry.getDefaultInstance();
{chr(10).join(f"        fire.add({c}, {a}, {b});" for c, (a, b) in burn)}
    }}
}}
'''


def assets_and_data(data_dir):
    lang = {}
    for name, (kind, label, x) in BLOCKS.items():
        lang[f"block.vividlands.{name}"] = label
        bs = ASSETS / "blockstates" / f"{name}.json"
        model = ASSETS / "models/block" / f"{name}.json"
        item = ASSETS / "models/item" / f"{name}.json"
        tex = f"vividlands:block/{name}"
        if kind == "log":
            jwrite(model, {"parent": "minecraft:block/cube_column",
                           "textures": {"end": f"{tex}_top", "side": tex}})
            jwrite(ASSETS / "models/block" / f"{name}_horizontal.json",
                   {"parent": "minecraft:block/cube_column_horizontal", "textures": {"end": f"{tex}_top", "side": tex}})
            jwrite(bs, {"variants": {
                "axis=y": {"model": f"vividlands:block/{name}"},
                "axis=z": {"model": f"vividlands:block/{name}_horizontal", "x": 90},
                "axis=x": {"model": f"vividlands:block/{name}_horizontal", "x": 90, "y": 90}}})
        elif kind in ("flower", "dry_plant"):
            jwrite(model, {"parent": "minecraft:block/cross", "textures": {"cross": tex}})
            jwrite(bs, {"variants": {"": {"model": f"vividlands:block/{name}"}}})
        elif kind == "pillar":
            jwrite(model, {"parent": "minecraft:block/cube_column", "textures": {"end": f"{tex}_top", "side": tex}})
            jwrite(ASSETS / "models/block" / f"{name}_horizontal.json",
                   {"parent": "minecraft:block/cube_column_horizontal", "textures": {"end": f"{tex}_top", "side": tex}})
            jwrite(bs, {"variants": {
                "axis=y": {"model": f"vividlands:block/{name}"},
                "axis=z": {"model": f"vividlands:block/{name}_horizontal", "x": 90},
                "axis=x": {"model": f"vividlands:block/{name}_horizontal", "x": 90, "y": 90}}})
        elif kind == "stairs":
            base = f"vividlands:block/{x['base']}"
            t = {"bottom": base, "top": base, "side": base}
            for suffix, parent in (("", "stairs"), ("_inner", "inner_stairs"), ("_outer", "outer_stairs")):
                jwrite(ASSETS / "models/block" / f"{name}{suffix}.json", {"parent": f"minecraft:block/{parent}", "textures": t})
            jwrite(bs, stairs_blockstate(f"vividlands:block/{name}"))
        elif kind == "slab":
            base = f"vividlands:block/{x['base']}"
            t = {"bottom": base, "top": base, "side": base}
            jwrite(model, {"parent": "minecraft:block/slab", "textures": t})
            jwrite(ASSETS / "models/block" / f"{name}_top.json", {"parent": "minecraft:block/slab_top", "textures": t})
            jwrite(bs, {"variants": {"type=bottom": {"model": f"vividlands:block/{name}"},
                                     "type=top": {"model": f"vividlands:block/{name}_top"},
                                     "type=double": {"model": base}}})
        elif kind == "stake":
            side, end = "vividlands:block/pine_log", "vividlands:block/pine_log_top"

            def el(a, b, top_tex):
                faces = {f: {"texture": "#side"} for f in ("north", "south", "east", "west")}
                faces["up"] = {"texture": "#end" if top_tex else "#side"}
                faces["down"] = {"texture": "#end"}
                return {"from": a, "to": b, "faces": faces}
            jwrite(model, {"parent": "minecraft:block/block", "textures": {"side": side, "end": end, "particle": side},
                           "elements": [el([2, 0, 2], [14, 9, 14], False), el([4, 9, 4], [12, 13, 12], False),
                                        el([6, 13, 6], [10, 16, 10], True)]})
            jwrite(bs, {"variants": {"": {"model": f"vividlands:block/{name}"}}})
        elif kind == "shield":
            disc = {"from": [1, 1, 15], "to": [15, 15, 16], "faces": {
                "north": {"uv": [1, 1, 15, 15], "texture": "#face"},
                "south": {"uv": [1, 1, 15, 15], "texture": "#face", "cullface": "south"},
                "east": {"uv": [0, 1, 1, 15], "texture": "#rim"}, "west": {"uv": [15, 1, 16, 15], "texture": "#rim"},
                "up": {"uv": [1, 0, 15, 1], "texture": "#rim"}, "down": {"uv": [1, 15, 15, 16], "texture": "#rim"}}}
            boss = {"from": [6, 6, 14], "to": [10, 10, 15], "faces": {
                f: {"uv": [7, 7, 9, 9], "texture": "#boss"} for f in ("north", "east", "west", "up", "down")}}
            jwrite(model, {"parent": "minecraft:block/block", "ambientocclusion": False,
                           "textures": {"face": tex, "rim": "minecraft:block/dark_oak_planks",
                                        "boss": "minecraft:block/iron_block", "particle": tex},
                           "elements": [disc, boss]})
            jwrite(bs, {"variants": {f"facing={f}": {"model": f"vividlands:block/{name}", "y": r}
                                     for f, r in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
        else:
            jwrite(model, {"parent": "minecraft:block/cube_all", "textures": {"all": tex}})
            jwrite(bs, {"variants": {"": {"model": f"vividlands:block/{name}"}}})
        if kind in ("flower", "dry_plant", "shield"):
            jwrite(item, {"parent": "minecraft:item/generated", "textures": {"layer0": tex}})
        else:
            jwrite(item, {"parent": f"vividlands:block/{name}"})

        # loot
        self_drop = {"type": "minecraft:item", "name": f"vividlands:{name}"}
        if kind == "leaves":
            shears_or_silk = {"condition": "minecraft:any_of", "terms": [
                {"condition": "minecraft:match_tool", "predicate": {"items": ["minecraft:shears"]}},
                {"condition": "minecraft:match_tool", "predicate": {"enchantments": [
                    {"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]}}]}
            pools = [{"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
                dict(self_drop, conditions=[shears_or_silk]),
                {"type": "minecraft:item", "name": "minecraft:stick",
                 "conditions": [{"condition": "minecraft:random_chance", "chance": 0.03}]}]}]}]
        else:
            pools = [{"rolls": 1, "entries": [self_drop], "conditions": [{"condition": "minecraft:survives_explosion"}]}]
        jwrite(data_dir / "vividlands/loot_tables/blocks" / f"{name}.json", {"type": "minecraft:block", "pools": pools})

        if kind == "planks":
            jwrite(data_dir / "vividlands/recipes" / f"{name}.json", {
                "type": "minecraft:crafting_shapeless", "category": "building", "group": "planks",
                "ingredients": [{"item": f"vividlands:{x['log']}"}],
                "result": {"item": f"vividlands:{name}", "count": 4}})

    def of(*kinds):
        return [f"vividlands:{n}" for n, (k, _, _) in BLOCKS.items() if k in kinds]

    tags = {
        "minecraft:logs_that_burn": of("log"),
        "minecraft:leaves": of("leaves"),
        "minecraft:planks": of("planks"),
        "minecraft:small_flowers": of("flower"),
        "minecraft:sand": ["vividlands:black_sand"],
        "minecraft:mineable/axe": of("log", "planks", "pillar", "stake", "shield"),
        "minecraft:stairs": of("stairs"),
        "minecraft:slabs": of("slab"),
        "minecraft:mineable/hoe": of("leaves", "flower", "dry_plant", "thatch", "stairs", "slab") + ["vividlands:peat"],
        "minecraft:mineable/shovel": ["vividlands:black_sand", "vividlands:volcanic_ash", "vividlands:peat",
                                      "vividlands:thermal_mat"],
        "minecraft:mineable/pickaxe": ["vividlands:salt_crust", "vividlands:sinter", "vividlands:travertine",
                                       "vividlands:sulfur_crust", "vividlands:wattle_daub"],
        "minecraft:dirt": ["vividlands:peat"],
    }
    item_tags = {
        "minecraft:logs_that_burn": of("log"),
        "minecraft:leaves": of("leaves"),
        "minecraft:planks": of("planks"),
        "minecraft:small_flowers": of("flower"),
        "minecraft:sand": ["vividlands:black_sand"],
        "minecraft:dirt": ["vividlands:peat"],
    }
    for kind_dir, table in (("blocks", tags), ("items", item_tags)):
        for tag, values in table.items():
            ns, path = tag.split(":")
            jwrite(data_dir / ns / "tags" / kind_dir / f"{path}.json", {"replace": False, "values": values})
    lang["itemGroup.vividlands"] = "Vivid Lands"
    JAVA.write_text(java_source())
    return lang
