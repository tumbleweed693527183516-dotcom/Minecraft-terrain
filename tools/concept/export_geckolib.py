#!/usr/bin/env python3
"""
Turns the Viking armor concept models (tools/concept/viking_armor_v2.py) into real GeckoLib armor:
  assets/vividlands_ragnarok/geo/item/armor/<set>.geo.json        (bones armorHead/Body/arms/legs/boots)
  assets/vividlands_ragnarok/textures/item/armor/<set>.png        (per-face texture atlas)
  assets/vividlands_ragnarok/animations/item/armor/<set>.animation.json
  assets/vividlands_ragnarok/textures/item/<set>_<piece>.png      (inventory icons)
plus the boss trophy item icons used in the recipes.

Voxels (4 per pixel) are merged into as few cubes as possible per bone; each visible cube face gets its own
patch of the texture, so every voxel keeps its colour.
"""
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("va", ROOT / "tools/concept/viking_armor_v2.py")
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)

NS = "vividlands_ragnarok"
ASSETS = ROOT / "ragnarok/src/main/resources/assets" / NS
R = 4
SETS = {"berserker": va.berserker, "ulfhednar": va.ulfhednar, "valkyrie": va.valkyrie, "jarl": va.jarl}

# bone -> (pivot in model pixels, part box it hugs)
BONES = {
    "armorHead": ([0, 24, 0], va.HEAD),
    "armorBody": ([0, 24, 0], va.BODY),
    "armorRightArm": ([-5, 22, 0], va.ARM_R),
    "armorLeftArm": ([5, 22, 0], va.ARM_L),
    "armorRightLeg": ([-1.9, 12, 0], va.LEG_R),
    "armorLeftLeg": ([1.9, 12, 0], va.LEG_L),
    "armorRightBoot": ([-1.9, 12, 0], va.LEG_R),
    "armorLeftBoot": ([1.9, 12, 0], va.LEG_L),
}
BOOT_TOP = 18          # leg voxels below this height belong to the boots
PIECE_BONES = {"helmet": ["armorHead"], "chestplate": ["armorBody", "armorRightArm", "armorLeftArm"],
               "leggings": ["armorRightLeg", "armorLeftLeg"], "boots": ["armorRightBoot", "armorLeftBoot"]}


def dist(p, b):
    x, y, z = p
    return max(b[0] - x, 0, x - (b[1] - 1), b[2] - y, 0, y - (b[3] - 1), b[4] - z, 0, z - (b[5] - 1))


def bone_of(p):
    x, y, z = p
    cands = [("armorHead", va.HEAD), ("armorBody", va.BODY), ("armorRightArm", va.ARM_R), ("armorLeftArm", va.ARM_L),
             ("armorRightLeg", va.LEG_R), ("armorLeftLeg", va.LEG_L)]
    if y >= 102:                                 # helmet, hood, wings, ears
        return "armorHead"
    best = min(cands[1:], key=lambda c: (dist(p, c[1]), 0 if c[0] == "armorBody" else 1))
    name = best[0]
    if name in ("armorRightLeg", "armorLeftLeg") and y < BOOT_TOP:
        name = name.replace("Leg", "Boot")
    if name == "armorBody" and y < 46:           # skirt and tassets below the belt move with the legs
        name = "armorRightLeg" if x >= 0 else "armorLeftLeg"
    return name


def greedy(vox):
    left = set(vox)
    cubes = []
    for p in sorted(vox):
        if p not in left:
            continue
        x, y, z = p
        x1 = x
        while (x1 + 1, y, z) in left:
            x1 += 1
        y1 = y
        while all((xx, y1 + 1, z) in left for xx in range(x, x1 + 1)):
            y1 += 1
        z1 = z
        while all((xx, yy, z1 + 1) in left for xx in range(x, x1 + 1) for yy in range(y, y1 + 1)):
            z1 += 1
        for xx in range(x, x1 + 1):
            for yy in range(y, y1 + 1):
                for zz in range(z, z1 + 1):
                    left.discard((xx, yy, zz))
        cubes.append((x, x1, y, y1, z, z1))
    return cubes


class Atlas:
    """Shelf packer for face patches: patches are collected first, then packed tallest first."""

    def __init__(self, width=1024):
        self.w = width
        self.patches = []                 # [img, uv-dict-to-fill]

    def add(self, img, slot):
        self.patches.append((img, slot))

    def pack(self):
        x = y = row = 0
        for img, slot in sorted(self.patches, key=lambda p: (-p[0].size[1], -p[0].size[0])):
            w, h = img.size
            if x + w > self.w:
                x, y, row = 0, y + row, 0
            slot["uv"] = [x, y]
            slot["pos"] = (x, y)
            x += w
            row = max(row, h)
        H = 1 << max(4, math.ceil(math.log2(max(1, y + row))))
        out = Image.new("RGBA", (self.w, H), (0, 0, 0, 0))
        for img, slot in self.patches:
            out.paste(img, slot.pop("pos"))
        return out


def export_set(name, model):
    # model voxels -> bedrock voxel space (rotate 180 degrees: front +z -> north -z, right arm -> -x)
    armor = {}
    for (x, y, z), c in model.v.items():
        if va.in_body((x, y, z)):
            continue
        armor[(-x - 1, y, -z - 1)] = (c, bone_of((x, y, z)))
    by_bone = {}
    for p, (c, b) in armor.items():
        by_bone.setdefault(b, {})[p] = c
    atlas = Atlas()
    bones_json = []
    total = 0
    for bone, (pivot, _) in BONES.items():
        vox = by_bone.get(bone, {})
        cubes_json = []
        for (bx0, bx1, by0, by1, bz0, bz1) in greedy(vox):
            uv = {}
            faces = {
                # Mapping taken from GeckoLib's BakedModelFactory/GeoQuad (java x = -bedrock X):
                # "west" is the +X side and "east" the -X side in bedrock coordinates.
                # face: (size w, h, texel (u, v) -> voxel, outward neighbour)
                "north": (bx1 - bx0 + 1, by1 - by0 + 1, lambda u, v: (bx0 + u, by1 - v, bz0), (0, 0, -1)),
                "south": (bx1 - bx0 + 1, by1 - by0 + 1, lambda u, v: (bx1 - u, by1 - v, bz1), (0, 0, 1)),
                "west": (bz1 - bz0 + 1, by1 - by0 + 1, lambda u, v: (bx1, by1 - v, bz0 + u), (1, 0, 0)),
                "east": (bz1 - bz0 + 1, by1 - by0 + 1, lambda u, v: (bx0, by1 - v, bz1 - u), (-1, 0, 0)),
                "up": (bx1 - bx0 + 1, bz1 - bz0 + 1, lambda u, v: (bx0 + u, by1, bz1 - v), (0, 1, 0)),
                "down": (bx1 - bx0 + 1, bz1 - bz0 + 1, lambda u, v: (bx0 + u, by0, bz0 + v), (0, -1, 0)),
            }
            for fname, (w, h, at, (nx, ny, nz)) in faces.items():
                cells = [(u, v) for u in range(w) for v in range(h)]
                visible = any((lambda p: (p[0] + nx, p[1] + ny, p[2] + nz) not in vox)(at(u, v)) for u, v in cells)
                if not visible:
                    continue
                img = Image.new("RGBA", (w, h))
                px = img.load()
                for u, v in cells:
                    c = vox.get(at(u, v), (255, 0, 255))
                    px[u, v] = tuple(c) + (255,)
                uv[fname] = {"uv": [0, 0], "uv_size": [w, h]}
                atlas.add(img, uv[fname])
            if not uv:
                continue
            cubes_json.append({"origin": [round(bx0 / R, 4), round(by0 / R, 4), round(bz0 / R, 4)],
                               "size": [round((bx1 - bx0 + 1) / R, 4), round((by1 - by0 + 1) / R, 4),
                                        round((bz1 - bz0 + 1) / R, 4)],
                               "uv": uv})
        total += len(cubes_json)
        bones_json.append({"name": bone, "pivot": pivot, "cubes": cubes_json})
    tex = atlas.pack()
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{name}", "texture_width": tex.width, "texture_height": tex.height,
                        "visible_bounds_width": 4, "visible_bounds_height": 4.5, "visible_bounds_offset": [0, 1.5, 0]},
        "bones": bones_json}]}
    (ASSETS / "geo/item/armor").mkdir(parents=True, exist_ok=True)
    (ASSETS / "textures/item/armor").mkdir(parents=True, exist_ok=True)
    (ASSETS / "animations/item/armor").mkdir(parents=True, exist_ok=True)
    (ASSETS / f"geo/item/armor/{name}.geo.json").write_text(json.dumps(geo, separators=(",", ":")))
    tex.save(ASSETS / f"textures/item/armor/{name}.png")
    (ASSETS / f"animations/item/armor/{name}.animation.json").write_text(
        json.dumps({"format_version": "1.8.0", "animations": {}}))
    print(f"{name}: {total} cubes, texture {tex.width}x{tex.height}")
    return armor


def icons(name, model):
    """Inventory icons: a 3/4 render of each piece, shrunk to 32x32."""
    parts = {k: va.Model() for k in PIECE_BONES}
    for (x, y, z), c in model.v.items():
        if va.in_body((x, y, z)):
            continue
        b = bone_of((x, y, z))
        for piece, bones in PIECE_BONES.items():
            if b in bones:
                parts[piece].v[(x, y, z)] = c
    for piece, m in parts.items():
        if not m.v:
            continue
        img = va.render_iso(m, s=2.0)
        bbox = img.getbbox()
        img = img.crop(bbox)
        side = max(img.size)
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
        sq.resize((32, 32), Image.LANCZOS).save(ASSETS / f"textures/item/{name}_{piece}.png")


def trophy_icons():
    """Simple 16x16 pixel icons for the boss trophies the armor is made from."""
    def canvas():
        return Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    def save(img, n):
        img.save(ASSETS / f"textures/item/{n}.png")

    def pelt(base, n, stripe=None):
        img = canvas()
        d = img.load()
        b = va.hexc(base)
        for x in range(16):
            for y in range(16):
                inside = (2 <= x <= 13 and 3 <= y <= 13) or (x in (1, 14) and y in (3, 4, 12, 13)) or (y == 2 and 5 <= x <= 10)
                if inside:
                    f = 0.75 + 0.45 * va.h(x, y // 2)
                    if x in (2, 13) or y in (3, 13):
                        f *= 0.7
                    d[x, y] = va.mul(b, f) + (255,)
        save(img, n)

    pelt("#6b4428", "bear_pelt")
    pelt("#9a968e", "wolf_pelt")
    img = canvas()                                           # saber fang
    d = img.load()
    for i in range(12):
        for w in range(max(1, 3 - i // 4)):
            d[3 + i + w // 2, 2 + i - w] = va.mul(va.IVORY, 1.05 - 0.03 * i) + (255,)
    for x, y in ((2, 2), (3, 2), (2, 3)):
        d[x, y] = (150, 120, 90, 255)
    save(img, "saber_fang")
    img = canvas()                                           # eclipse shard: half sun, half moon
    d = img.load()
    for x in range(16):
        for y in range(16):
            r = math.hypot(x - 7.5, y - 7.5)
            if r < 6.5 and abs(x - 7.5) + abs(y - 7.5) < 8.5:
                d[x, y] = ((255, 196, 60) if x < 8 else (170, 190, 230)) + (255,)
                if r < 3:
                    d[x, y] = ((255, 240, 160) if x < 8 else (230, 236, 255)) + (255,)
    save(img, "eclipse_shard")
    img = canvas()                                           # raven feather
    d = img.load()
    for i in range(13):
        cx, cy = 3 + i, 13 - i
        d[cx, cy] = (120, 120, 140, 255)
        for w in (1, 2):
            if 2 < i < 12:
                d[min(15, cx + w), cy] = (30, 30, 42, 255) if w == 1 else (50, 50, 70, 255)
                d[cx, max(0, cy - w)] = (24, 24, 34, 255)
    save(img, "raven_feather")
    img = canvas()                                           # Sleipnir's mane hair
    d = img.load()
    for k in range(5):
        for y in range(2, 15):
            x = 3 + k * 2 + int(1.5 * math.sin(y / 2 + k))
            if 0 <= x < 16:
                d[x, y] = va.mul((200, 205, 215), 0.8 + 0.3 * va.h(k, y)) + (255,)
    for x in range(3, 13):
        d[x, 2] = va.GOLD + (255,)
    save(img, "sleipnir_hair")
    img = canvas()                                           # dragon gold
    d = img.load()
    for x in range(2, 14):
        for y in range(5, 12):
            if not ((x in (2, 13)) and y in (5, 11)):
                d[x, y] = va.mul(va.GOLD, 0.8 + 0.4 * va.h(x, y) + (0.2 if y == 6 else 0)) + (255,)
    d[7, 8] = (200, 24, 48, 255)
    d[8, 8] = (255, 90, 110, 255)
    save(img, "dragon_gold")
    img = canvas()                                           # serpent scale
    d = img.load()
    for x in range(16):
        for y in range(16):
            if (x - 7.5) ** 2 / 36 + (y - 6) ** 2 / 64 < 1 and y < 14:
                d[x, y] = va.mul(va.hexc("#2c8a7a"), 1.3 - y * 0.05) + (255,)
                if abs(x - 7.5) < 1:
                    d[x, y] = va.mul(va.hexc("#2c8a7a"), 1.5) + (255,)
    save(img, "serpent_scale")


def main():
    (ASSETS / "textures/item").mkdir(parents=True, exist_ok=True)
    for name, fn in SETS.items():
        model = va.finish(fn())
        export_set(name, model)
        icons(name, model)
    trophy_icons()


if __name__ == "__main__":
    main()
