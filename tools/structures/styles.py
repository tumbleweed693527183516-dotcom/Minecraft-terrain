"""
Regional styles for Viking villages. Every building is designed once (the northern homeland
look) and re-materialed here for the other regions, so each vanilla village type has a Norse
counterpart:

    north   turf, spruce and thatch (moors, pinewoods, lakelands, lava fields...)
    snow    dark timber and snow-laden roofs (tundra, snowy woods)
    forest  oak-framed halls (temperate woodlands, meadows)
    steppe  birch-walled Rus towns under thatch (steppe, prairie, savanna)
    desert  Varangian trading posts: palm wood, sandstone and mud brick (deserts, canyons)
    jungle  far-voyager camps in jungle wood (rainforest, cloud forest)
"""
from .builder import Build
from .kit import NS, h

STYLES = ["north", "snow", "forest", "steppe", "desert", "jungle"]
WOOD = {"snow": "dark_oak", "forest": "oak", "steppe": "birch", "desert": "acacia", "jungle": "jungle"}
PINE = {"snow": "minecraft:spruce_planks", "forest": "minecraft:oak_planks", "steppe": "minecraft:birch_planks",
        "desert": f"{NS}:palm_planks", "jungle": "minecraft:jungle_planks"}
VILLAGER_TYPE = {"north": "taiga", "snow": "snow", "forest": "plains", "steppe": "plains", "desert": "desert",
                 "jungle": "jungle"}

M = "minecraft:"
SNOW_LAYER = (M + "snow", (("layers", "1"),))
PLANTS = ("grass", "fern", "cornflower", "allium", "oxeye_daisy", "moss_carpet", "sweet_berry_bush", "dandelion",
          "poppy", "azure_bluet")

# exact replacements: name -> (new name, keep the block's properties?)
SWAPS = {
    "snow": {
        M + "grass_block": (M + "snow_block", False),
        f"{NS}:thatch": (M + "dark_oak_planks", False),
        f"{NS}:thatch_stairs": (M + "dark_oak_stairs", True),
        f"{NS}:thatch_slab": (M + "dark_oak_slab", True),
        M + "mossy_cobblestone": (M + "cobblestone", False),
        M + "mossy_cobblestone_wall": (M + "cobblestone_wall", True),
        M + "mossy_stone_bricks": (M + "stone_bricks", False),
        M + "vine": (M + "air", False),
        f"{NS}:heather": SNOW_LAYER,
    },
    "desert": {
        M + "grass_block": (f"{NS}:thatch", False),
        M + "dirt": (M + "packed_mud", False),
        M + "coarse_dirt": (M + "terracotta", False),
        M + "rooted_dirt": (M + "mud_bricks", False),
        M + "cobblestone": (M + "sandstone", False),
        M + "mossy_cobblestone": (M + "smooth_sandstone", False),
        M + "cobblestone_slab": (M + "sandstone_slab", True),
        M + "cobblestone_stairs": (M + "sandstone_stairs", True),
        M + "cobblestone_wall": (M + "sandstone_wall", True),
        M + "mossy_cobblestone_wall": (M + "sandstone_wall", True),
        M + "stone_bricks": (M + "cut_sandstone", False),
        M + "mossy_stone_bricks": (M + "cut_sandstone", False),
        M + "cracked_stone_bricks": (M + "smooth_sandstone", False),
        M + "stone_brick_stairs": (M + "smooth_sandstone_stairs", True),
        M + "stone_brick_slab": (M + "smooth_sandstone_slab", True),
        M + "stone_stairs": (M + "sandstone_stairs", True),
        M + "polished_andesite": (M + "smooth_sandstone", False),
        M + "polished_andesite_slab": (M + "smooth_sandstone_slab", True),
        M + "spruce_log": (f"{NS}:palm_log", True),
        M + "spruce_planks": (f"{NS}:palm_planks", False),
        M + "vine": (M + "air", False),
        f"{NS}:heather": (f"{NS}:dry_grass", False),
    },
    "jungle": {
        M + "cobblestone": (M + "mossy_cobblestone", False),
        f"{NS}:heather": (M + "fern", False),
    },
}


def _swap(style, name, props):
    rule = SWAPS.get(style, {}).get(name)
    if rule:
        new, keep = rule[0], rule[1]
        if isinstance(keep, tuple):
            return new, keep
        return new, props if keep else ()
    short = name.split(":")[1]
    if style == "snow" and short in PLANTS:
        return SNOW_LAYER
    if style == "desert" and short in PLANTS:
        return (M + "air", ()) if short == "moss_carpet" else (M + "dead_bush", ())
    if name == f"{NS}:pine_planks":
        return PINE[style], ()
    if "spruce" in name and name.startswith(M) and style in WOOD:
        return name.replace("spruce", WOOD[style]), props
    return name, props


def restyle(b, style, name):
    if style == "north":
        return b
    out = Build(name)
    for pos, (n, props, nbt) in b.blocks.items():
        nn, pp = _swap(style, n, props)
        if style == "desert" and nn == M + "sandstone" and h(*pos, 7) < 0.25:
            nn = M + "smooth_sandstone"          # a little variety in the stonework
        out.blocks[pos] = (nn, tuple(pp), nbt)
    for (x, y, z, nbt) in b.entities:
        if nbt.get("id") == M + "villager":
            nbt = dict(nbt, VillagerData=dict(nbt["VillagerData"], type=M + VILLAGER_TYPE[style]))
        out.entities.append((x, y, z, nbt))
    return out
