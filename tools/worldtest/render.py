#!/usr/bin/env python3
"""
Renders maps extracted by extract.py:
  map.png       top-down map with real block colours, biome tints and hill shading
  biomes.png    biome map with legend
  view_*.png    3D views of the most mountainous areas
  stats.txt     height and biome statistics

    python3 render.py <dir with world_maps.npz + names.json> <generated data dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BLOCK_COLORS = {
    "grass_block": None, "oak_leaves": None, "spruce_leaves": (60, 90, 60), "birch_leaves": (128, 167, 85),
    "jungle_leaves": None, "acacia_leaves": None, "dark_oak_leaves": None, "azalea_leaves": (90, 120, 50),
    "water": None, "vine": None, "grass": None, "tall_grass": None, "fern": None, "large_fern": None,
    "sand": (219, 207, 163), "red_sand": (190, 102, 33), "sandstone": (216, 203, 155), "gravel": (136, 126, 126),
    "stone": (125, 125, 125), "cobblestone": (122, 122, 122), "mossy_cobblestone": (110, 120, 95),
    "snow": (249, 254, 254), "snow_block": (249, 254, 254), "powder_snow": (248, 253, 253), "ice": (145, 183, 253),
    "packed_ice": (141, 180, 250), "blue_ice": (116, 167, 253), "calcite": (223, 224, 220),
    "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "podzol": (91, 63, 24), "mud": (60, 57, 61),
    "mycelium": (111, 99, 105), "clay": (160, 166, 179), "terracotta": (152, 94, 67),
    "orange_terracotta": (161, 83, 37), "red_terracotta": (143, 61, 46), "yellow_terracotta": (186, 133, 35),
    "white_terracotta": (209, 178, 161), "brown_terracotta": (77, 51, 35), "light_gray_terracotta": (135, 107, 98),
    "basalt": (73, 72, 77), "blackstone": (42, 35, 40), "tuff": (108, 109, 102), "magma_block": (142, 63, 31),
    "moss_block": (89, 109, 45), "moss_carpet": (89, 109, 45), "lava": (207, 92, 20), "deepslate": (80, 80, 82),
    "oak_log": (109, 85, 50), "spruce_log": (58, 37, 16), "birch_log": (216, 215, 210), "jungle_log": (85, 67, 25),
    "acacia_log": (103, 96, 86), "cactus": (85, 127, 43), "dead_bush": (107, 78, 40), "lily_pad": (32, 128, 48),
    "sugar_cane": (148, 192, 101), "pink_petals": (230, 150, 200), "allium": (180, 120, 220),
    "azalea": (100, 125, 45), "flowering_azalea": (150, 110, 160), "sweet_berry_bush": (60, 100, 50),
    "melon": (111, 145, 30), "bedrock": (85, 85, 85),
}
FLOWERS = (215, 190, 90)


def biome_colors(data_dir):
    out = {}
    for p in Path(data_dir, "vividlands/worldgen/biome").glob("*.json"):
        e = json.loads(p.read_text())["effects"]
        out["vividlands:" + p.stem] = {k: e.get(k) for k in ("grass_color", "foliage_color", "water_color")}
    return out


def rgb(i):
    return ((i >> 16) & 255, (i >> 8) & 255, i & 255)


def main(src, data_dir):
    src = Path(src)
    m = np.load(src / "world_maps.npz")
    names = json.loads((src / "names.json").read_text())
    blocks = [b.split(":")[-1] for b in names["blocks"]]
    biomes = names["biomes"]
    bcol = biome_colors(data_dir)
    surf, floor, blk, bio = m["surface"].astype(float), m["floor"].astype(float), m["block"], m["biome"]
    valid = surf > -9000
    H, W = surf.shape

    # --- top-down map ---
    lut = np.zeros((len(blocks), len(biomes), 3), float)
    for bi, b in enumerate(blocks):
        for gi, g in enumerate(biomes):
            c = BLOCK_COLORS.get(b, FLOWERS if b.endswith(("tulip", "poppy", "dandelion", "orchid", "daisy",
                                                             "bluet", "cornflower", "valley", "lilac", "peony",
                                                             "bush", "sunflower")) else (120, 120, 120))
            if c is None:
                bc = bcol.get(g, {})
                if b == "water":
                    c = rgb(bc.get("water_color") or 0x3F76E4)
                elif b.endswith("leaves") or b == "vine":
                    c = tuple(int(v * 0.75) for v in rgb(bc.get("foliage_color") or 0x48B518))
                else:
                    c = tuple(int(v * 0.85) for v in rgb(bc.get("grass_color") or 0x91BD59))
            lut[bi, gi] = c
    col = lut[blk, bio]
    gy, gx = np.gradient(np.where(valid, floor, 0))
    shade = np.clip(1.0 + (-gx - gy) * 0.08, 0.45, 1.45)
    water = np.array([blocks[i] == "water" for i in range(len(blocks))])[blk]
    shade = np.where(water, 1.0, shade)
    img = np.clip(col * shade[..., None], 0, 255).astype(np.uint8)
    img[~valid] = 0
    Image.fromarray(img).save(src / "map.png")
    small = Image.fromarray(img).resize((min(W, 1600), int(H * min(W, 1600) / W)), Image.LANCZOS)
    small.save(src / "map_small.png")

    # --- biome map ---
    rng = np.random.default_rng(3)
    pal = rng.integers(40, 230, (len(biomes), 3))
    bimg = Image.fromarray(pal[bio].astype(np.uint8)).resize((1200, int(1200 * H / W)), Image.NEAREST)
    counts = np.bincount(bio[valid], minlength=len(biomes))
    order = np.argsort(-counts)
    legend = Image.new("RGB", (1200 + 330, bimg.height), (250, 250, 250))
    legend.paste(bimg, (0, 0))
    d = ImageDraw.Draw(legend)
    for row, gi in enumerate([g for g in order if counts[g] > 0][:45]):
        y = 8 + row * 18
        d.rectangle([1210, y, 1224, y + 12], fill=tuple(int(v) for v in pal[gi]))
        d.text((1230, y), f"{biomes[gi].split(':')[-1]}  {100 * counts[gi] / valid.sum():.1f}%", fill=(20, 20, 20))
    legend.save(src / "biomes.png")

    # --- stats ---
    land = valid & ~water
    lines = [f"area: {W}x{H} blocks",
             "land surface height  p5/p25/p50/p75/p95/max: " +
             " / ".join(f"{np.percentile(floor[land], q):.0f}" for q in (5, 25, 50, 75, 95, 100)),
             f"water share: {100 * (water & valid).sum() / valid.sum():.1f}%",
             f"blocks above y=300: {100 * (floor[land] > 300).mean():.2f}%  above y=200: {100 * (floor[land] > 200).mean():.2f}%",
             "", "biomes by area:"]
    lines += [f"  {biomes[g]:40s} {100 * counts[g] / valid.sum():5.1f}%" for g in order if counts[g] > 0]
    (src / "stats.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:5]))

    # --- 3D views of the most mountainous spots ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    win = 384
    hsm = np.where(valid, floor, 0)
    picks = []
    tmp = hsm.copy()
    for _ in range(3):
        r, c = np.unravel_index(np.argmax(tmp), tmp.shape)
        picks.append((r, c))
        tmp[max(0, r - win):r + win, max(0, c - win):c + win] = -9999
    for k, (r, c) in enumerate(picks):
        r0, c0 = int(np.clip(r - win // 2, 0, H - win)), int(np.clip(c - win // 2, 0, W - win))
        z = hsm[r0:r0 + win:2, c0:c0 + win:2]
        cc = img[r0:r0 + win:2, c0:c0 + win:2] / 255.0
        fig = plt.figure(figsize=(12, 8), dpi=110)
        ax = fig.add_subplot(projection="3d")
        X, Y = np.meshgrid(np.arange(z.shape[1]) * 2, np.arange(z.shape[0]) * 2)
        ls = LightSource(azdeg=315, altdeg=40)
        ax.plot_surface(X, Y, z, facecolors=ls.shade_rgb(cc, z, blend_mode="soft", vert_exag=0.5),
                        rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
        ax.set_box_aspect((1, 1, (z.max() - z.min() + 1) / win))
        ax.view_init(elev=24, azim=-60 + k * 40)
        ax.set_axis_off()
        ox, oz = m["origin"]
        ax.set_title(f"around x={ox + c0 + win // 2}, z={oz + r0 + win // 2}  (peak y={int(hsm[r, c])})")
        fig.savefig(src / f"view_{k + 1}.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
