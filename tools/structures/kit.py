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


# ---------------------------------------------------------------------------
# Exterior detail
# ---------------------------------------------------------------------------
DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
SIDE = {"north": ("east", "west"), "south": ("east", "west"), "east": ("north", "south"), "west": ("north", "south")}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def window(b, x, y, z, out, wood="spruce"):
    """Glass window in a wall cell with open shutters on the outside."""
    b.set(x, y, z, "glass_pane", **FENCE)
    dx, dz = DIRS[out]
    for side in SIDE[out]:
        sx, sz = DIRS[side]
        cx, cz = x + dx + sx, z + dz + sz
        if b.get(cx, y, cz) is None:
            b.set(cx, y, cz, f"{wood}_trapdoor", facing=side, half="bottom", open=True, powered=False,
                  waterlogged=False)
    if b.get(x + dx, y - 1, z + dz) is None:     # flower box under the window
        b.set(x + dx, y - 1, z + dz, f"{wood}_trapdoor", facing=out, half="top", open=False, powered=False,
              waterlogged=False)


def cart(b, x, y, z, axis="x", cargo="hay_block"):
    along = (1, 0) if axis == "x" else (0, 1)
    across = (0, 1) if axis == "x" else (1, 0)
    for i in range(2):
        cx, cz = x + along[0] * i, z + along[1] * i
        slab(b, cx, y, cz, "spruce_slab", "top")
        for s in (-1, 1):
            wx, wz = cx + across[0] * s, cz + across[1] * s
            face = ("south" if s > 0 else "north") if axis == "x" else ("east" if s > 0 else "west")
            if i == 0 and b.get(wx, y, wz) is None:
                b.set(wx, y, wz, "dark_oak_trapdoor", facing=face, half="bottom", open=True, powered=False,
                      waterlogged=False)
        if cargo == "hay_block":
            b.set(cx, y + 1, cz, "hay_block", axis="y")
        else:
            b.barrel(cx, y + 1, cz)
    fx, fz = x - along[0], z - along[1]
    b.set(fx, y, fz, "spruce_fence", **FENCE)


def chopping_block(b, x, y, z):
    b.set(x, y, z, "stripped_spruce_log", axis="y")
    b.set(x + 1, y, z, "spruce_log", axis="x")
    b.set(x + 1, y + 1, z, "spruce_log", axis="x")
    b.set(x, y, z + 1, "spruce_slab", type="bottom", waterlogged=False)


def hide_frame(b, x, y, z, axis="x", colour="brown"):
    along = (1, 0) if axis == "x" else (0, 1)
    for i in (0, 3):
        b.fill(x + along[0] * i, y, z + along[1] * i, x + along[0] * i, y + 2, z + along[1] * i, "spruce_fence",
               **FENCE)
    for i in (1, 2):
        b.set(x + along[0] * i, y + 1, z + along[1] * i, f"{colour}_wool")
        b.set(x + along[0] * i, y + 2, z + along[1] * i, "spruce_fence", **FENCE)


def kitchen_garden(b, x0, z0, w, d, y=1, salt=0):
    crops = [("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("sweet_berry_bush", 3)]
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + d):
            edge = x in (x0, x0 + w - 1) or z in (z0, z0 + d - 1)
            b.set(x, y - 1, z, "dirt")
            if edge:
                b.set(x, y, z, "spruce_fence", **FENCE)
            else:
                name, top = crops[int(h(x, z, salt) * 4)]
                if name == "sweet_berry_bush":
                    b.set(x, y - 1, z, "grass_block", snowy=False)
                    b.set(x, y, z, name, age=top)
                else:
                    b.set(x, y - 1, z, "farmland", moisture=7)
                    b.set(x, y, z, name, age=top)
    b.set(x0 + w // 2, y, z0, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)
    b.set(x0, y + 1, z0, "torch")


def water_barrel(b, x, y, z):
    b.set(x, y, z, "water_cauldron", level=3)


def potted(b, x, y, z, salt=0):
    plants = ["potted_cornflower", "potted_allium", "potted_fern", "potted_oxeye_daisy", "potted_spruce_sapling"]
    b.set(x, y, z, plants[int(h(x, y, z, salt) * len(plants))])


def stepping_stones(b, x0, z0, x1, z1, y=0, salt=0):
    n = max(abs(x1 - x0), abs(z1 - z0))
    for i in range(n + 1):
        x = x0 + round((x1 - x0) * i / max(n, 1))
        z = z0 + round((z1 - z0) * i / max(n, 1))
        if b.get(x, y, z) is None and h(x, z, salt) < 0.8:
            b.set(x, y, z, "dirt_path" if h(z, x) < 0.6 else "gravel")


def animals(b, kind, spots, **extra):
    for x, y, z in spots:
        b.animal(x, y, z, kind, **extra)


def weather(b, salt=0, vines=True):
    """Age a finished build: mossy stone, cracked bricks, vines on shady (north) faces."""
    for (x, y, z), (name, props, nbt) in list(b.blocks.items()):
        r = h(x, y, z, salt, 77)
        if name == "minecraft:cobblestone" and r < 0.3:
            b.blocks[(x, y, z)] = ("minecraft:mossy_cobblestone", props, nbt)
        elif name == "minecraft:stone_bricks" and r < 0.35:
            b.blocks[(x, y, z)] = ("minecraft:mossy_stone_bricks" if r < 0.2 else "minecraft:cracked_stone_bricks",
                                   props, nbt)
        if not vines or y < 1 or y > 6:
            continue
        solid = name.endswith(("cobblestone", "stone_bricks", "_log", "packed_mud", "mud_bricks", "rooted_dirt",
                               "wattle_daub", "planks"))
        if solid and b.get(x, y, z - 1) is None and r > 0.86:
            for dy in range(0, 1 + int(h(x, z, salt) * 3)):
                if b.get(x, y - dy, z - 1) is None and y - dy >= 1:
                    b.set(x, y - dy, z - 1, "vine", north=False, south=True, east=False, west=False, up=False)


# ---------------------------------------------------------------------------
# Dungeons
# ---------------------------------------------------------------------------
def spawner(b, x, y, z, mob, delay=(240, 600)):
    from .nbtio import Short
    b.set(x, y, z, "spawner", nbt={
        "id": "minecraft:mob_spawner", "SpawnData": {"entity": {"id": f"minecraft:{mob}"}},
        "SpawnCount": Short(2), "SpawnRange": Short(4), "Delay": Short(20), "MinSpawnDelay": Short(delay[0]),
        "MaxSpawnDelay": Short(delay[1]), "MaxNearbyEntities": Short(5), "RequiredPlayerRange": Short(14)})


def draugr(b, x, y, z, kind="zombie", gear="iron", boss=False, yaw=0):
    """Undead Norse warrior: an armoured, persistent zombie/skeleton/stray."""
    from .nbtio import Float, FloatList
    sets = {"iron": ("iron_boots", "chainmail_leggings", "iron_chestplate", "iron_helmet"),
            "chain": ("chainmail_boots", "chainmail_leggings", "chainmail_chestplate", "chainmail_helmet"),
            "leather": ("leather_boots", "leather_leggings", "leather_chestplate", "iron_helmet"),
            "jarl": ("iron_boots", "iron_leggings", "diamond_chestplate", "golden_helmet")}[gear]
    hand = "bow" if kind in ("skeleton", "stray") else ("iron_axe" if not boss else "diamond_axe")

    def it(i):
        return {"id": f"minecraft:{i}", "Count": Byte(1)}
    nbt = {"id": f"minecraft:{kind}", "PersistenceRequired": Byte(1),
           "ArmorItems": [it(p) for p in sets], "HandItems": [it(hand), it("shield") if kind == "zombie" else {}],
           "ArmorDropChances": FloatList([0.05, 0.05, 0.05, 0.05]),
           "HandDropChances": FloatList([0.1, 0.05]), "Rotation": FloatList([float(yaw), 0.0]),
           "CustomName": '{"text":"Draugr Jarl","color":"dark_aqua","bold":true}' if boss else '{"text":"Draugr"}'}
    if boss:
        nbt["Attributes"] = [{"Name": "minecraft:generic.max_health", "Base": 80.0},
                             {"Name": "minecraft:generic.attack_damage", "Base": 8.0}]
        nbt["Health"] = Float(80.0)
        nbt["HandDropChances"] = FloatList([1.0, 0.5])
    b.entity(x + 0.5, y, z + 0.5, nbt)


def arrow_trap(b, plate, dispensers):
    """Stone pressure plate wired straight into flanking dispensers loaded with arrows."""
    b.set(*plate, "stone_pressure_plate", powered=False)
    for (x, y, z, facing) in dispensers:
        b.set(x, y, z, "dispenser", nbt={"id": "minecraft:dispenser", "Items": [
            {"Slot": Byte(0), "id": "minecraft:arrow", "Count": Byte(24)}]}, facing=facing, triggered=False)


def cobweb(b, x, y, z):
    b.set(x, y, z, "cobweb")


def skull(b, x, y, z, rot=0):
    b.set(x, y, z, "skeleton_skull", rotation=rot)


def compose(b, other, dx=0, dy=0, dz=0):
    """Copy another build's blocks and entities into b at an offset."""
    for (x, y, z), v in other.blocks.items():
        b.blocks[(x + dx, y + dy, z + dz)] = v
    for (x, y, z, nbt) in other.entities:
        b.entities.append((x + dx, y + dy, z + dz, nbt))
