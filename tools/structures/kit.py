"""
Building kit for detailed Viking structures: roofs, walls, framing and furniture.

All designs: door side faces north (-z); template origin is the min corner; y=0 is the
foundation course (placed at ground level), y=1 the floor.
"""
import math

from .builder import Build
from .nbtio import Byte

FENCE = dict(north=False, south=False, east=False, west=False, waterlogged=False)
NS = "vividlands"

ROOFS = {
    "shingle": ("dark_oak_stairs", "dark_oak_planks", "dark_oak_slab"),
    "spruce": ("spruce_stairs", "spruce_planks", "spruce_slab"),
    "thatch": (f"{NS}:thatch_stairs", f"{NS}:thatch", f"{NS}:thatch_slab"),
    "turf": ("grass_block", "dirt", "grass_block"),
}


def h(*k):
    v = 2166136261
    for n in k:
        v = ((v ^ (int(n) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 0x5BD1E995) & 0xFFFFFFFF
    v ^= v >> 15
    return v / 2 ** 32


def stair(b, x, y, z, mat, facing, half="bottom"):
    b.set(x, y, z, mat, facing=facing, half=half, shape="straight", waterlogged=False)


def slab(b, x, y, z, mat, kind="bottom"):
    b.set(x, y, z, mat, type=kind, waterlogged=False)


# ---------------------------------------------------------------------------
# Roofs
# ---------------------------------------------------------------------------
def gable_roof(b, cx, half_width, z0, z1, y0, style, overhang=1, salt=0):
    """
    Gable roof with its ridge along z. half_width(z) gives the wall half-width at each z
    (allowing bowed, ship-shaped halls). Returns {z: ridge_y}.
    """
    st, full, sl = ROOFS[style]
    turf = style == "turf"
    ridge = {}
    for z in range(z0 - overhang, z1 + overhang + 1):
        w = half_width(min(max(z, z0), z1)) + overhang
        k = 0
        while True:
            xl, xr, y = cx - w + k, cx + w - k, y0 + k
            if xl > xr:
                break
            if xl == xr:
                if turf:
                    b.set(xl, y, z, "grass_block", snowy=False)
                else:
                    slab(b, xl, y, z, sl)
                ridge[z] = y
                break
            if turf:
                b.set(xl, y, z, "grass_block", snowy=False)
                b.set(xr, y, z, "grass_block", snowy=False)
            else:
                stair(b, xl, y, z, st, "east")
                stair(b, xr, y, z, st, "west")
            if xr - xl >= 2:
                b.set(xl + 1, y, z, full)
                b.set(xr - 1, y, z, full)
            elif xr - xl == 1:
                if not turf:
                    slab(b, xl, y + 1, z, sl)
                    slab(b, xr, y + 1, z, sl)
                ridge[z] = y + 1
                break
            ridge[z] = y
            k += 1
        if turf:   # tufts and moss on turf roofs
            for x in range(cx - w, cx + w + 1):
                for yy in range(y0, y0 + w + 2):
                    if b.get(x, yy, z) == "minecraft:grass_block" and b.get(x, yy + 1, z) is None \
                            and h(x, yy, z, salt) < 0.18:
                        b.set(x, yy + 1, z, "moss_carpet" if h(z, x, salt) < 0.5 else "grass")
    return ridge


def gable_end(b, cx, half_width, z, y0, wall_y0, block_fn):
    """Fill the triangle under the roof at gable z (and the wall below it)."""
    w = half_width(z)
    for y in range(wall_y0, y0):
        for x in range(cx - w, cx + w + 1):
            b.set(x, y, z, *block_fn(x, y, z))
    k = 0
    while True:
        lo, hi = cx - w + k + 1, cx + w - k - 1
        if lo > hi:
            break
        for x in range(lo, hi + 1):
            b.set(x, y0 + k, z, *block_fn(x, y0 + k, z))
        k += 1


def crossed_horns(b, x, y, z, toward):
    """Carved crossed gable boards above a ridge end (dragon horns)."""
    b.set(x, y, z, f"{NS}:carved_post", axis="y")
    stair(b, x - 1, y + 1, z, "dark_oak_stairs", "east")
    stair(b, x + 1, y + 1, z, "dark_oak_stairs", "west")
    b.set(x - 1, y + 2, z, "dark_oak_fence", **FENCE)
    b.set(x + 1, y + 2, z, "dark_oak_fence", **FENCE)


# ---------------------------------------------------------------------------
# Wall styles: functions (x, y, z) -> (block, props)
# ---------------------------------------------------------------------------
def timber(post_every=3, infill="wattle", salt=0, sill_y=1, top_y=None):
    fill = {"wattle": f"{NS}:wattle_daub", "planks": "spruce_planks", "pine": f"{NS}:pine_planks"}[infill]

    def f(x, y, z):
        if y == sill_y:
            return ("cobblestone", {}) if h(x, z, salt) < 0.7 else ("mossy_cobblestone", {})
        if top_y is not None and y == top_y:
            return ("stripped_spruce_log", {"axis": "x"})
        if (x + z) % post_every == 0:
            return ("stripped_spruce_log", {"axis": "y"})
        return (fill, {})
    return f


def turf_wall(salt=0, sill_y=1):
    def f(x, y, z):
        r = h(x, y, z, salt)
        if y == sill_y:
            return ("cobblestone", {}) if r < 0.6 else ("mossy_cobblestone", {})
        if (x + y + z) % 2:
            return ("packed_mud", {}) if r < 0.65 else ("mud_bricks", {})
        return ("rooted_dirt", {}) if r < 0.45 else (("coarse_dirt", {}) if r < 0.75 else ("packed_mud", {}))
    return f


def plank_gable(x, y, z):
    return ("stripped_spruce_log", {"axis": "y"}) if x % 2 == 0 else ("spruce_planks", {})


# ---------------------------------------------------------------------------
# Furniture and dressing
# ---------------------------------------------------------------------------
def table(b, x, y, z, wood="spruce"):
    b.set(x, y, z, f"{wood}_fence", **FENCE)
    b.set(x, y + 1, z, f"{wood}_pressure_plate", powered=False)


def long_table(b, x, y, z0, z1, wood="spruce"):
    """Trestle table: top-half slabs on fence legs at the ends."""
    for z in range(z0, z1 + 1):
        b.set(x, y, z, f"{wood}_slab", type="top", waterlogged=False)


def bench(b, x, y, z, facing, wood="spruce"):
    stair(b, x, y, z, f"{wood}_stairs", facing)


def hanging_lantern(b, x, y_top, z, length=2):
    for i in range(length):
        b.set(x, y_top - i, z, "chain", axis="y", waterlogged=False)
    b.set(x, y_top - length, z, "lantern", hanging=True, waterlogged=False)


def shield(b, x, y, z, facing, salt=0):
    color = ("red", "blue", "yellow", "green")[int(h(x, y, z, salt) * 4)]
    b.set(x, y, z, f"{NS}:shield_{color}", facing=facing, waterlogged=False)


def candle(b, x, y, z, n=None):
    b.set(x, y, z, "candle", candles=n or 1 + int(h(x, y, z) * 3), lit=True, waterlogged=False)


def fur(b, x, y, z, salt=0):
    b.set(x, y, z, ("brown_carpet", "white_carpet", "light_gray_carpet", "gray_carpet")[int(h(x, z, salt) * 4)])


def woodpile(b, x, y, z, length, axis="x"):
    for i in range(length):
        for dy in range(2 if i % 3 else 1):
            xx, zz = (x + i, z) if axis == "x" else (x, z + i)
            b.set(xx, y + dy, zz, "spruce_log", axis="z" if axis == "x" else "x")


def crates(b, x, y, z, n, salt=0, loot=None):
    for i in range(n):
        dx, dz = i % 2, i // 2
        b.barrel(x + dx, y, z + dz, loot=loot if i == 0 else None)
        if h(i, x, z, salt) < 0.4:
            b.barrel(x + dx, y + 1, z + dz)


def armor_stand(b, x, y, z, yaw, hand=None, head=None, chest=None, offhand=None):
    def it(i):
        return {"id": f"minecraft:{i}", "Count": Byte(1)} if i else {}
    from .nbtio import FloatList
    b.entity(x + 0.5, y, z + 0.5, {
        "id": "minecraft:armor_stand", "ShowArms": Byte(1), "NoBasePlate": Byte(1),
        "HandItems": [it(hand), it(offhand)], "ArmorItems": [{}, {}, it(chest), it(head)],
        "Rotation": FloatList([float(yaw), 0.0]), "PersistenceRequired": Byte(1)})


def foundation(b, x0, x1, z0, z1, salt=0):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            b.set(x, 0, z, "mossy_cobblestone" if h(x, z, salt) < 0.3 else "cobblestone")


def bowed(cx_half_mid, cx_half_end, z0, z1):
    zc = (z0 + z1) / 2

    def hw(z):
        t = (z - zc) / ((z1 - z0) / 2 + 0.5)
        return int(round(cx_half_end + (cx_half_mid - cx_half_end) * math.cos(t * math.pi / 2)))
    return hw
