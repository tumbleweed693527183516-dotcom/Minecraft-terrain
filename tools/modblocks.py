"""
Vivid Lands has no blocks of its own: terrain and structures use blocks from established mods
(Oh The Biomes We've Gone, Decorative Blocks) and vanilla. The generators are still written with
short design names (vividlands:thatch ...); everything they write passes through remap() here.

MAP: design id -> (real id, properties to keep or None for all)
"""
BWG = "biomeswevegone"
DB = "decorative_blocks"
M = "minecraft"

MAP = {
    "vividlands:black_sand": (f"{BWG}:black_sand", ()),
    "vividlands:volcanic_ash": (f"{BWG}:dacite", ()),            # volcanic rock fields
    "vividlands:salt_crust": (f"{BWG}:white_sand", ()),
    "vividlands:peat": (f"{BWG}:peat", ()),
    "vividlands:sinter": (f"{M}:calcite", ()),                     # hot-spring silica terraces
    "vividlands:travertine": (f"{BWG}:white_sandstone", ()),
    "vividlands:thermal_mat": (f"{BWG}:red_rock", ()),             # orange-red algal mats
    "vividlands:sulfur_crust": (f"{M}:yellow_terracotta", ()),
    "vividlands:heather": (f"{BWG}:purple_sage", ()),
    "vividlands:dry_grass": (f"{BWG}:prairie_grass", ()),
    "vividlands:palm_log": (f"{BWG}:palm_log", ("axis",)),
    "vividlands:palm_leaves": (f"{BWG}:palm_leaves", None),
    "vividlands:palm_planks": (f"{BWG}:palm_planks", ()),
    "vividlands:redwood_log": (f"{BWG}:redwood_log", ("axis",)),
    "vividlands:redwood_leaves": (f"{BWG}:redwood_leaves", None),
    "vividlands:redwood_planks": (f"{BWG}:redwood_planks", ()),
    "vividlands:pine_log": (f"{BWG}:pine_log", ("axis",)),
    "vividlands:pine_leaves": (f"{BWG}:pine_leaves", None),
    "vividlands:pine_planks": (f"{BWG}:pine_planks", ()),
    "vividlands:thatch": (f"{BWG}:cattail_thatch", ()),
    "vividlands:thatch_stairs": (f"{BWG}:cattail_thatch_stairs", None),
    "vividlands:thatch_slab": (f"{BWG}:cattail_thatch_slab", None),
    "vividlands:wattle_daub": (f"{M}:packed_mud", ()),
    "vividlands:carved_post": (f"{M}:stripped_dark_oak_log", ("axis",)),
    "vividlands:palisade_stake": (f"{DB}:spruce_palisade", ()),
    "vividlands:shield_red": (f"{M}:red_wall_banner", ("facing",)),
    "vividlands:shield_blue": (f"{M}:blue_wall_banner", ("facing",)),
    "vividlands:shield_yellow": (f"{M}:yellow_wall_banner", ("facing",)),
    "vividlands:shield_green": (f"{M}:green_wall_banner", ("facing",)),
}
# Some data references use the bare design name (e.g. a "vl(...)" id); these are not blocks.
NOT_BLOCKS = {"vividlands:stamps", "vividlands:stamp_seed"}


def name(n):
    return MAP[n][0] if n in MAP else n


def props(n, p):
    """Filter a property mapping (dict or tuple of pairs) for the block n maps to."""
    if n not in MAP:
        return p
    keep = MAP[n][1]
    if keep is None:
        return p
    if isinstance(p, dict):
        return {k: v for k, v in p.items() if k in keep}
    return tuple((k, v) for k, v in p if k in keep)


BLOCK_KEYS = {"blocks", "block", "Name"}


def remap_json(obj, key=None):
    """Rewrite block references in a JSON-like tree: block states ({"Name", "Properties"}) and
    block ids under block-predicate keys. Other ids (features, biomes...) are left alone."""
    if isinstance(obj, dict):
        if isinstance(obj.get("Name"), str) and obj["Name"] in MAP:
            out = {k: remap_json(v, k) for k, v in obj.items() if k not in ("Name", "Properties")}
            n = obj["Name"]
            out["Name"] = name(n)
            if "Properties" in obj:
                p = props(n, obj["Properties"])
                if p:
                    out["Properties"] = p
            return out
        return {k: remap_json(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [remap_json(v, key) for v in obj]
    if isinstance(obj, str) and key in BLOCK_KEYS and obj in MAP:
        return name(obj)
    return obj
