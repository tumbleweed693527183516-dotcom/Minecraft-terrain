"""Isometric previews of Build objects (full view and roof-off cutaway)."""
from PIL import Image, ImageDraw

COLORS = {
    "spruce_planks": (115, 85, 49), "spruce_log": (58, 37, 16), "stripped_spruce_log": (116, 89, 52),
    "dark_oak_planks": (66, 43, 20), "dark_oak_stairs": (66, 43, 20), "dark_oak_slab": (66, 43, 20),
    "dark_oak_log": (60, 46, 26), "dark_oak_fence": (66, 43, 20), "spruce_stairs": (115, 85, 49),
    "spruce_slab": (115, 85, 49), "spruce_fence": (115, 85, 49), "spruce_fence_gate": (115, 85, 49),
    "spruce_door": (106, 80, 48), "cobblestone": (122, 122, 122), "mossy_cobblestone": (110, 120, 95),
    "stone_bricks": (122, 121, 122), "cobblestone_slab": (122, 122, 122), "cobblestone_wall": (122, 122, 122),
    "grass_block": (110, 160, 70), "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "rooted_dirt": (144, 104, 76),
    "packed_mud": (142, 106, 79), "mud_bricks": (137, 103, 79), "moss_carpet": (89, 109, 45), "grass": (100, 150, 60),
    "gravel": (136, 126, 126), "dirt_path": (148, 122, 65), "farmland": (82, 54, 32), "water": (60, 110, 220),
    "wheat": (200, 180, 80), "carrots": (230, 140, 40), "potatoes": (190, 170, 90), "beetroots": (150, 40, 50),
    "hay_block": (200, 170, 40), "andesite": (136, 136, 136), "polished_andesite": (132, 134, 133),
    "chiseled_stone_bricks": (118, 118, 118), "red_wool": (160, 39, 34), "white_wool": (234, 236, 236),
    "yellow_wall_banner": (240, 200, 50), "red_wall_banner": (180, 40, 40), "white_wall_banner": (230, 230, 230),
    "black_wall_banner": (30, 30, 34), "campfire": (220, 120, 40), "lantern": (240, 200, 110), "chain": (60, 64, 72),
    "bell": (230, 190, 60), "glass_pane": (190, 220, 230), "chest": (160, 110, 40), "barrel": (130, 95, 55),
    "torch": (250, 210, 100), "jigsaw": (240, 0, 240), "snow": (238, 242, 248), "snow_block": (238, 242, 248),
    "stone": (125, 125, 125), "ice": (150, 185, 250), "packed_ice": (141, 180, 250), "sand": (219, 207, 163),
    "spruce_leaves": (60, 90, 60), "tuff": (108, 109, 102), "blackstone": (42, 35, 40), "basalt": (73, 72, 77),
    "black_sand": (40, 38, 46), "moss_block": (89, 109, 45), "podzol": (91, 63, 24), "peat": (56, 40, 26),
    "pine_log": (170, 96, 54), "pine_leaves": (56, 102, 82), "heather": (150, 90, 170),
    "thatch": (200, 164, 86), "thatch_stairs": (200, 164, 86), "thatch_slab": (200, 164, 86),
    "wattle_daub": (216, 202, 174), "carved_post": (122, 84, 48), "palisade_stake": (116, 89, 52),
    "shield_red": (176, 36, 32), "shield_blue": (40, 70, 150), "shield_yellow": (226, 182, 52),
    "shield_green": (52, 110, 58), "pine_planks": (192, 152, 106), "stripped_dark_oak_log": (96, 76, 49),
    "polished_andesite_slab": (132, 134, 133), "spruce_pressure_plate": (115, 85, 49), "candle": (230, 220, 190),
    "brown_carpet": (114, 72, 41), "white_carpet": (233, 236, 236), "light_gray_carpet": (142, 142, 135),
    "gray_carpet": (62, 68, 71), "smoker": (90, 85, 80), "cauldron": (70, 70, 74), "water_cauldron": (60, 110, 220),
    "lava_cauldron": (220, 100, 30), "blast_furnace": (100, 100, 104), "ladder": (120, 90, 50),
    "dried_kelp_block": (50, 60, 35), "target": (230, 210, 200), "lectern": (160, 120, 70),
    "dark_oak_door": (66, 43, 20), "stone_bricks": (122, 121, 122), "coal_block": (20, 20, 20),
}


def color(name):
    n = name.split(":")[-1]
    if n.endswith("_bed"):
        return {"red": (160, 40, 40), "blue": (50, 70, 160), "brown": (110, 75, 45), "green": (80, 110, 40)}.get(
            n[:-4], (150, 60, 60))
    return COLORS.get(n, (150, 150, 150))


def render(build, path, cutaway_above=None, scale=8):
    cells = [(p, b[0]) for p, b in build.blocks.items() if b[0] != "minecraft:air"
             and (cutaway_above is None or p[1] <= cutaway_above)]
    if not cells:
        return
    xs = [p[0] for p, _ in cells]
    ys = [p[1] for p, _ in cells]
    zs = [p[2] for p, _ in cells]
    s = scale
    W = int((max(xs) - min(xs) + max(zs) - min(zs) + 4) * s * 0.87) + 40
    H = int((max(xs) - min(xs) + max(zs) - min(zs) + 4) * s * 0.5 + (max(ys) - min(ys) + 3) * s) + 40
    img = Image.new("RGB", (W, H), (226, 232, 238))
    d = ImageDraw.Draw(img)
    ox = (max(zs) - min(zs) + 2) * s * 0.87 + 20
    oy = (max(ys) - min(ys) + 2) * s + 20

    def proj(x, y, z):
        x, y, z = x - min(xs), y - min(ys), z - min(zs)
        return ox + (x - z) * s * 0.87, oy + (x + z) * s * 0.5 - y * s

    thin = ("slab", "carpet", "stairs", "fence", "chain", "lantern", "torch", "banner", "pane", "door",
            "campfire", "wheat", "carrots", "potatoes", "beetroots", "grass", "bell")
    for (x, y, z), name in sorted(cells, key=lambda c: (c[0][0] + c[0][2], c[0][1])):
        c = color(name)
        top = [proj(x, y + 1, z), proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
        left = [proj(x, y + 1, z + 1), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x, y, z + 1)]
        right = [proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x + 1, y, z)]
        if any(t in name for t in thin) and "grass_block" not in name:
            c = tuple(int(v * 0.95) for v in c)
        d.polygon(top, fill=c)
        d.polygon(left, fill=tuple(int(v * 0.72) for v in c))
        d.polygon(right, fill=tuple(int(v * 0.86) for v in c))
    img.save(path)
