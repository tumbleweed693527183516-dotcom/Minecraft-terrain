"""
Viking structure designs (batch 1), built block by block.

Conventions for village buildings: the door side faces north (-z). Row z=0 holds the
jigsaw connector in front of the door at y=1; y=0 is the foundation (replaces the top
ground block), y=1 is the floor, so floors sit one step above the ground.
"""
import math

from .builder import Build
from .nbtio import Byte

NS = "vividlands"
STREET = f"{NS}:street"
SIDE = f"{NS}:street_side"
ENTRY = f"{NS}:building_entry"
P_STREETS = f"{NS}:village/streets"
P_BUILDINGS = f"{NS}:village/buildings"


def h(*k):
    """Deterministic hash in [0, 1)."""
    v = 2166136261
    for n in k:
        v = ((v ^ (int(n) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 0x5BD1E995) & 0xFFFFFFFF
    v ^= v >> 15
    return v / 2 ** 32


def turf(b, x, y, z, salt=0):
    """Icelandic turf wall: herringbone-ish mix of sods."""
    r = h(x, y, z, salt)
    if (x + y + z) % 2:
        b.set(x, y, z, "packed_mud" if r < 0.7 else "mud_bricks")
    else:
        b.set(x, y, z, "rooted_dirt" if r < 0.5 else ("coarse_dirt" if r < 0.8 else "packed_mud"))


def entry(b, x, z=0):
    b.jigsaw(x, 1, z, "north", ENTRY, SIDE, "minecraft:empty", final_state="minecraft:spruce_slab")


def hanging_lantern(b, x, y_top, z, length=2):
    for i in range(length):
        b.set(x, y_top - i, z, "chain", axis="y", waterlogged=False)
    b.set(x, y_top - length, z, "lantern", hanging=True, waterlogged=False)


# ---------------------------------------------------------------------------
# Longhouse: bowed walls, aisled hall, sunken hearth, curved roof ridge
# ---------------------------------------------------------------------------
def longhouse(turf_roof=False):
    b = Build("longhouse_turf" if turf_roof else "longhouse")
    C, Z0, Z1 = 6, 1, 23                      # centre line, gable walls
    zc = (Z0 + Z1) / 2

    def hw(z):                                # half-width of the walls (bowed like a ship)
        z = min(max(z, Z0), Z1)
        return int(round(4 + math.cos(math.pi * (z - zc) / (Z1 - Z0 + 1))))

    # foundation and floor
    for z in range(Z0, Z1 + 1):
        w = hw(z)
        for x in range(C - w, C + w + 1):
            b.set(x, 0, z, "mossy_cobblestone" if h(x, z, 1) < 0.3 else "cobblestone")
            b.set(x, 1, z, "spruce_planks")
    # clear the interior
    for z in range(Z0 + 1, Z1):
        w = hw(z)
        b.air(C - w + 1, 2, z, C + w - 1, 12, z)

    # long walls: timber posts every third block, planks between, stone sill
    for z in range(Z0, Z1 + 1):
        w = hw(z)
        for x in (C - w, C + w):
            b.set(x, 1, z, "cobblestone")
            for y in range(2, 5):
                if z % 3 == 1:
                    b.set(x, y, z, "stripped_spruce_log", axis="y")
                else:
                    b.set(x, y, z, "spruce_planks")

    roof_mat = ("grass_block", "dirt") if turf_roof else ("dark_oak_stairs", "dark_oak_planks")
    ridge_y = {}
    for z in range(Z0 - 1, Z1 + 2):
        w = hw(z) + 1
        k = 0
        while True:
            xl, xr, y = C - w + k, C + w - k, 5 + k
            if xl > xr:
                break
            if xl == xr:
                b.set(xl, y, z, "grass_block" if turf_roof else "dark_oak_slab",
                      **({"snowy": False} if turf_roof else {"type": "bottom", "waterlogged": False}))
                ridge_y[z] = y
                break
            if turf_roof:
                b.set(xl, y, z, "grass_block", snowy=False)
                b.set(xr, y, z, "grass_block", snowy=False)
            else:
                b.set(xl, y, z, "dark_oak_stairs", facing="east", half="bottom", shape="straight", waterlogged=False)
                b.set(xr, y, z, "dark_oak_stairs", facing="west", half="bottom", shape="straight", waterlogged=False)
            if xr - xl >= 2:
                b.set(xl + 1, y, z, roof_mat[1])
                b.set(xr - 1, y, z, roof_mat[1])
            ridge_y[z] = y
            k += 1

    # gable walls
    for z in (Z0, Z1):
        w = hw(z)
        for y in range(2, 13):
            k = y - 5
            lo, hi = (C - w, C + w) if y < 5 else (C - (w + 1) + k + 2, C + (w + 1) - k - 2)
            for x in range(lo, hi + 1):
                if b.get(x, y, z) in ("minecraft:dark_oak_planks", "minecraft:dirt", "minecraft:grass_block"):
                    continue
                post = x in (C - 2, C + 2) or x == C
                b.set(x, y, z, "stripped_spruce_log" if post else "spruce_planks", **({"axis": "y"} if post else {}))
    b.door(C, 2, Z0, "north")
    entry(b, C)
    # carved gable posts at both ridge ends
    for z in (Z0 - 1, Z1 + 1):
        top = ridge_y[z]
        b.set(C, top + 1, z, "dark_oak_log", axis="y")
        b.set(C, top + 2, z, "dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False)

    # side door
    zs = 12
    b.door(C - hw(zs), 2, zs, "west")

    # aisle posts holding the roof
    for z in (5, 9, 15, 19):
        w = hw(z) + 1
        for x in (C - 3, C + 3):
            k = x - (C - w) - 1 if x < C else (C + w) - x - 1
            top = 5 + k - 1
            b.fill(x, 2, z, x, top, z, "stripped_spruce_log", axis="y")

    # sunken hearth down the middle
    b.fill(C - 1, 1, 9, C + 1, 1, 15, "cobblestone")
    for z in (10, 14):
        b.set(C, 1, z, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)

    # sleeping benches along the walls
    for z in range(4, 21):
        if z in (zs,):
            continue
        w = hw(z)
        for x in (C - w + 1, C + w - 1):
            if b.get(x, 2, z) == "minecraft:air":
                b.set(x, 2, z, "spruce_slab", type="bottom", waterlogged=False)

    # far end: beds, chief's chest, barrels
    for x in (C - 3, C - 2, C + 2, C + 3):
        b.bed(x, 2, Z1 - 2, "south", color="red" if x < C else "blue")
    b.chest(C, 2, Z1 - 1, "north", f"{NS}:chests/longhouse")
    b.barrel(C - 1, 2, Z1 - 1)
    b.barrel(C + 1, 2, Z1 - 1)
    # front end: kitchen and loom
    b.set(C - 3, 2, Z0 + 1, "smoker", facing="south", lit=False)
    b.set(C - 2, 2, Z0 + 1, "crafting_table")
    b.set(C + 2, 2, Z0 + 1, "loom", facing="south")
    b.barrel(C + 3, 2, Z0 + 1, loot=f"{NS}:chests/turf_house")

    for z in (4, 8, 16, 20):
        hanging_lantern(b, C, ridge_y[z] - 2, z)

    b.villager(C - 1, 2, 6, "butcher")
    b.villager(C + 1, 2, 17)
    b.villager(C - 1, 2, 19)
    return b


# ---------------------------------------------------------------------------
# Icelandic turf house: thick sod walls, grass roof, timber gable
# ---------------------------------------------------------------------------
def turf_house(station, salt):
    b = Build(f"turf_house_{station}")
    X1, Z0, Z1 = 8, 1, 10
    for x in range(0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "spruce_planks")
    b.air(2, 2, 2, 6, 7, Z1 - 2)
    # walls
    for y in range(1, 4):
        for z in range(Z0, Z1 + 1):
            for x in (0, 1, X1 - 1, X1):
                turf(b, x, y, z, salt)
        for x in range(2, X1 - 1):
            turf(b, x, y, Z1 - 1, salt)
            turf(b, x, y, Z1, salt)
    # grass roof: two-thick shell, outer grass
    for k in range(5):
        y = 4 + k
        for z in range(Z0, Z1 + 1):
            for x in (k, X1 - k):
                b.set(x, y, z, "grass_block", snowy=False)
            for x in (k + 1, X1 - k - 1):
                if 0 < k + 1 <= X1 - k - 1 and abs(x - 4) < 4 - k:
                    b.set(x, y, z, "dirt")
    # timber gable front
    for y in range(2, 8):
        span = 2 if y < 4 else y - 2
        for x in range(span, X1 - span + 1):
            if b.get(x, y, Z0) in ("minecraft:grass_block",):
                continue
            b.set(x, y, Z0, "stripped_spruce_log" if x in (2, 6) else "spruce_planks",
                  **({"axis": "y"} if x in (2, 6) else {}))
    b.set(4, 5, Z0, "glass_pane", north=False, south=False, east=False, west=False, waterlogged=False)
    b.door(4, 2, Z0, "north")
    entry(b, 4)
    for x in range(X1 + 1):            # moss and tufts on the roof
        for z in range(Z0, Z1 + 1):
            for k in range(5):
                if b.get(x, 4 + k, z) == "minecraft:grass_block" and b.get(x, 5 + k, z) is None \
                        and h(x, k, z, salt, 7) < 0.25:
                    b.set(x, 5 + k, z, "moss_carpet" if h(x, z, salt) < 0.6 else "grass")
    # interior
    b.bed(2, 2, Z1 - 3, "south", "brown")
    b.bed(6, 2, Z1 - 3, "south", "green")
    b.chest(4, 2, Z1 - 2, "north", f"{NS}:chests/turf_house")
    b.set(2, 2, 3, "furnace", facing="east", lit=False)
    station_block = {
        "farmer": ("composter", {"level": 0}),
        "shepherd": ("loom", {"facing": "east"}),
        "fletcher": ("fletching_table", {}),
        "librarian": ("lectern", {"facing": "west", "has_book": False, "powered": False}),
        "cleric": ("brewing_stand", {"has_bottle_0": False, "has_bottle_1": False, "has_bottle_2": False}),
        "fisherman": ("barrel", {"facing": "up", "open": False}),
    }[station]
    b.set(6, 2, 3, station_block[0], **station_block[1])
    b.set(4, 2, 5, "cauldron")
    for z in (3, 7):
        hanging_lantern(b, 4, 6, z, length=1)
    b.villager(4, 2, 3)
    b.villager(3, 2, 6)
    return b


# ---------------------------------------------------------------------------
# Smithy: open forge under a shed roof against a turf back wall
# ---------------------------------------------------------------------------
def smithy():
    b = Build("smithy")
    for x in range(9):
        for z in range(1, 9):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "stone_bricks" if h(x, z, 3) < 0.6 else "cobblestone")
    b.air(0, 2, 1, 8, 6, 7)
    for y in range(2, 7):
        for x in range(9):
            turf(b, x, y, 8, 11)
    for x, z in ((0, 1), (8, 1), (0, 4), (8, 4)):
        b.fill(x, 2, z, x, 5, z, "stripped_spruce_log", axis="y")
    for z in range(0, 10):
        y = 6 if z < 4 else (7 if z < 8 else 8)
        for x in range(-1, 10):
            b.set(x, y, z, "spruce_slab", type="bottom", waterlogged=False)
            if z in (4, 8):
                b.set(x, y - 1, z, "spruce_planks")
    b.set(4, 2, 7, "blast_furnace", facing="north", lit=False)
    b.set(3, 2, 7, "lava_cauldron")
    b.set(5, 2, 7, "water_cauldron", level=3)
    b.set(4, 2, 4, "anvil", facing="east")
    b.set(2, 2, 6, "smithing_table")
    b.set(6, 2, 6, "grindstone", face="floor", facing="north")
    b.chest(7, 2, 7, "north", f"{NS}:chests/smithy")
    b.barrel(1, 2, 7)
    b.set(0, 6, 4, "lantern", hanging=True, waterlogged=False)
    b.set(4, 5, 2, "lantern", hanging=True, waterlogged=False)
    entry(b, 4)
    b.villager(4, 2, 2, "armorer")
    return b


# ---------------------------------------------------------------------------
# Farm plot, sheep pen, raised storehouse
# ---------------------------------------------------------------------------
FENCE = dict(north=False, south=False, east=False, west=False, waterlogged=False)


def fence_ring(b, x0, z0, x1, z1, y, gate_x):
    for x in range(x0, x1 + 1):
        for z in (z0, z1):
            b.set(x, y, z, "spruce_fence", **FENCE)
    for z in range(z0, z1 + 1):
        for x in (x0, x1):
            b.set(x, y, z, "spruce_fence", **FENCE)
    b.set(gate_x, y, z0, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)


def farm(salt):
    b = Build(f"farm_{salt}")
    crops = [("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3)]
    crop_a, crop_b = crops[salt % 4], crops[(salt + 1) % 4]
    for x in range(11):
        for z in range(1, 10):
            b.set(x, 0, z, "dirt")
            edge = x in (0, 10) or z in (1, 9)
            if edge:
                b.set(x, 1, z, "coarse_dirt")
            elif x == 5:
                b.set(x, 1, z, "water", level=0)
            else:
                b.set(x, 1, z, "farmland", moisture=7)
                name, top = crop_a if x < 5 else crop_b
                age = top if h(x, z, salt) < 0.6 else int(h(z, x, salt) * top)
                b.set(x, 2, z, name, age=age)
    fence_ring(b, 0, 1, 10, 9, 2, 5)
    b.set(1, 2, 8, "composter", level=3)
    b.set(9, 2, 8, "hay_block", axis="y")
    b.set(1, 3, 1, "torch")  # on the fence post
    entry(b, 5)
    return b


def sheep_pen():
    b = Build("sheep_pen")
    for x in range(9):
        for z in range(1, 10):
            b.set(x, 0, z, "dirt")
            b.set(x, 1, z, "grass_block", snowy=False)
    b.air(1, 2, 2, 7, 3, 8)
    fence_ring(b, 0, 1, 8, 9, 2, 4)
    b.set(1, 2, 8, "hay_block", axis="y")
    b.set(2, 2, 8, "hay_block", axis="x")
    b.set(7, 2, 8, "water_cauldron", level=3)
    for (x, z), color in zip(((3, 4), (5, 6), (6, 3), (2, 6)), (0, 0, 12, 15)):
        b.animal(x, 2, z, "sheep", Color=Byte(color))
    b.set(0, 3, 1, "torch")
    entry(b, 4)
    return b


def storehouse():
    """Stabbur: timber storehouse raised on stone pillars."""
    b = Build("storehouse")
    X1, Z0, Z1 = 6, 1, 6
    for x, z in ((0, Z0), (X1, Z0), (0, Z1), (X1, Z1), (3, Z1)):
        b.set(x, 0, z, "cobblestone")
        b.set(x, 1, z, "cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
              waterlogged=False)
    for x in range(X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 2, z, "spruce_planks")
    b.air(1, 3, Z0 + 1, X1 - 1, 7, Z1 - 1)
    for y in range(3, 6):
        for z in range(Z0, Z1 + 1):
            b.set(0, y, z, "spruce_log", axis="z")
            b.set(X1, y, z, "spruce_log", axis="z")
        for x in range(1, X1):
            b.set(x, y, Z0, "spruce_log", axis="x")
            b.set(x, y, Z1, "spruce_log", axis="x")
    for k in range(5):
        y = 6 + k
        xl, xr = -1 + k, X1 + 1 - k
        if xl > xr:
            break
        for z in range(Z0 - 1, Z1 + 2):
            if xl == xr:
                b.set(xl, y, z, "spruce_slab", type="bottom", waterlogged=False)
            else:
                b.set(xl, y, z, "spruce_stairs", facing="east", half="bottom", shape="straight", waterlogged=False)
                b.set(xr, y, z, "spruce_stairs", facing="west", half="bottom", shape="straight", waterlogged=False)
        for z in (Z0, Z1):
            for x in range(xl + 1, xr):
                b.set(x, y, z, "spruce_planks")
    b.door(3, 3, Z0, "north")
    b.set(3, 2, 0, "spruce_stairs", facing="south", half="bottom", shape="straight", waterlogged=False)
    entry(b, 3)
    b.set(1, 3, Z1 - 1, "cartography_table")
    b.barrel(2, 3, Z1 - 1, loot=f"{NS}:chests/storehouse")
    b.barrel(4, 3, Z1 - 1)
    b.chest(5, 3, Z1 - 1, "north", f"{NS}:chests/storehouse")
    b.set(1, 3, Z0 + 1, "hay_block", axis="y")
    hanging_lantern(b, 3, 9, 3, length=3)
    b.villager(3, 3, 3, "cartographer")
    return b


# ---------------------------------------------------------------------------
# Village plaza and streets
# ---------------------------------------------------------------------------
def ground(b, x, z, salt):
    r = h(x, z, salt)
    b.set(x, 0, z, "gravel" if r < 0.3 else "cobblestone" if r < 0.5 else "coarse_dirt" if r < 0.75 else "dirt_path")


def runestone_at(b, x, y, z, axis="x", salt=0):
    """A 2-wide, 4-tall carved standing stone."""
    xs = [(x, z), (x + 1, z)] if axis == "x" else [(x, z), (x, z + 1)]
    for i, (sx, sz) in enumerate(xs):
        b.set(sx, y - 1, sz, "cobblestone")
        for dy in range(4 if i == 0 else 3):
            r = h(sx, dy, sz, salt)
            blk = "chiseled_stone_bricks" if dy == 1 else ("polished_andesite" if r < 0.5 else "andesite")
            b.set(sx, y + dy, sz, blk)


def plaza():
    b = Build("plaza")
    for x in range(15):
        for z in range(15):
            ground(b, x, z, 5)
    b.air(0, 1, 0, 14, 5, 14)
    # bell under a timber frame
    b.fill(6, 1, 7, 6, 3, 7, "stripped_spruce_log", axis="y")
    b.fill(8, 1, 7, 8, 3, 7, "stripped_spruce_log", axis="y")
    b.fill(6, 4, 7, 8, 4, 7, "stripped_spruce_log", axis="x")
    b.set(7, 3, 7, "bell", attachment="ceiling", facing="north", powered=False)
    runestone_at(b, 2, 1, 2, "x", 9)
    # fire pit
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        b.set(11 + dx, 1, 11 + dz, "cobblestone_slab", type="bottom", waterlogged=False)
    b.set(11, 1, 11, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
    # benches and lamp posts
    for x in (10, 12):
        b.set(x, 1, 9, "spruce_stairs", facing="south", half="bottom", shape="straight", waterlogged=False)
    for x, z in ((1, 12), (13, 2), (13, 12)):
        b.set(x, 1, z, "spruce_fence", **FENCE)
        b.set(x, 2, z, "lantern", hanging=False, waterlogged=False)
    b.set(3, 1, 12, "hay_block", axis="x")
    b.set(3, 2, 12, "hay_block", axis="y")
    for x, z, f in ((7, 0, "north"), (7, 14, "south"), (0, 7, "west"), (14, 7, "east")):
        b.jigsaw(x, 0, z, f, STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.villager(5, 1, 5)
    return b


def street(length):
    b = Build(f"street_{length}")
    for x in range(3):
        for z in range(length):
            ground(b, x, z, length)
    b.jigsaw(1, 0, 0, "north", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.jigsaw(1, 0, length - 1, "south", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    for z in range(3, length - 2, 6):
        b.jigsaw(0, 0, z, "west", SIDE, ENTRY, P_BUILDINGS, final_state="minecraft:dirt_path")
        b.jigsaw(2, 0, z, "east", SIDE, ENTRY, P_BUILDINGS, final_state="minecraft:dirt_path")
    return b


def street_junction():
    b = Build("street_junction")
    for x in range(9):
        for z in range(9):
            if 3 <= x <= 5 or 3 <= z <= 5:
                ground(b, x, z, 77)
    b.jigsaw(4, 0, 0, "north", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.jigsaw(0, 0, 4, "west", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.jigsaw(8, 0, 4, "east", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.jigsaw(4, 0, 8, "south", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    return b


def street_end():
    b = Build("street_end")
    for x in range(3):
        for z in range(3):
            ground(b, x, z, 31)
    b.jigsaw(1, 0, 0, "north", STREET, STREET, P_STREETS, final_state="minecraft:dirt_path")
    b.jigsaw(1, 0, 2, "south", SIDE, ENTRY, P_BUILDINGS, final_state="minecraft:dirt_path")
    return b


# ---------------------------------------------------------------------------
# Longship: dragon-prowed warship with a striped square sail and shields
# ---------------------------------------------------------------------------
def longship():
    b = Build("longship")
    L, C = 29, 4
    WATER = 3                       # local y of the sea surface

    def beam(z):
        t = z / (L - 1)
        return 3.6 * math.sin(math.pi * t) ** 0.55

    for z in range(L):
        bm = beam(z)
        for y in range(0, 5):
            # hull flares outward going up
            half = bm * (0.35 + 0.65 * min(1.0, y / 3.0))
            hw = int(round(half))
            if y == 0:
                if 1 <= z <= L - 2:
                    b.set(C, 0, z, "spruce_log", axis="z")
                continue
            if hw < 1 and not (2 <= z <= L - 3):
                b.set(C, y, z, "spruce_planks")
                continue
            for x in range(C - hw, C + hw + 1):
                edge = abs(x - C) == hw
                if edge:
                    b.set(x, y, z, "dark_oak_planks" if y == 4 else "spruce_planks")
                elif y <= 1:
                    b.set(x, y, z, "spruce_planks")      # bilge / ballast
                elif y == 2:
                    b.set(x, y, z, "spruce_planks")      # deck
                else:
                    b.set(x, y, z, "air")                # dry above deck
            # shields on the gunwale, above the water
            if y == 4 and 5 <= z <= L - 6 and z % 2 == 0 and hw >= 2:
                color = ("red", "yellow", "white", "black")[(z // 2) % 4]
                b.banner(C - hw - 1, 4, z, "west", color)
                b.banner(C + hw + 1, 4, z, "east", color)
    # rising stems; dragon head at the bow (z = 0), curled tail at the stern
    stem = [(0, 4), (0, 5), (-1, 6), (-1, 7), (-1, 8), (0, 9)]
    for dz, y in stem:
        b.set(C, y, 0 + dz, "dark_oak_planks")
        b.set(C, y, L - 1 - dz, "dark_oak_planks")
    b.set(C, 9, -2, "dark_oak_stairs", facing="south", half="bottom", shape="straight", waterlogged=False)
    b.set(C, 10, -1, "dark_oak_log", axis="y")
    b.set(C, 10, 0, "dark_oak_stairs", facing="north", half="top", shape="straight", waterlogged=False)
    b.set(C, 9, 1, "red_wool")  # tongue
    b.set(C, 9, L, "dark_oak_stairs", facing="north", half="top", shape="straight", waterlogged=False)
    # mast, yard and striped sail
    zm = L // 2
    b.fill(C, 3, zm, C, 13, zm, "stripped_spruce_log", axis="y")
    b.fill(C - 5, 13, zm, C + 5, 13, zm, "spruce_fence", **FENCE)
    for x in range(C - 5, C + 6):
        for y in range(6, 13):
            b.set(x, y, zm, "red_wool" if ((x - C + 5) // 2) % 2 == 0 else "white_wool")
    b.set(C, 3, zm, "stripped_spruce_log", axis="y")
    # rowing benches, cargo and the captain's chest at the stern
    for z in range(5, L - 5, 3):
        if z == zm:
            continue
        b.fill(C - 1, 3, z, C + 1, 3, z, "spruce_slab", type="bottom", waterlogged=False)
    b.chest(C, 3, L - 4, "north", f"{NS}:chests/longship")
    b.barrel(C - 1, 3, L - 5, loot=f"{NS}:chests/ship_cargo")
    b.barrel(C + 1, 3, L - 5)
    b.set(C, 3, 4, "lantern", hanging=False, waterlogged=False)
    return b, WATER


# ---------------------------------------------------------------------------
# Runestones
# ---------------------------------------------------------------------------
def runestone_single():
    b = Build("runestone_single")
    for x in range(4):
        for z in range(3):
            if h(x, z, 2) < 0.6:
                b.set(x, 1, z, "moss_carpet")
    runestone_at(b, 1, 1, 1, "x", 4)
    return b


def runestone_trio():
    b = Build("runestone_trio")
    runestone_at(b, 0, 1, 4, "z", 1)
    runestone_at(b, 4, 1, 0, "x", 2)
    runestone_at(b, 8, 1, 4, "z", 3)
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        b.set(4 + dx, 1, 5 + dz, "cobblestone_slab", type="bottom", waterlogged=False)
    b.set(4, 0, 5, "cobblestone")
    b.set(4, 1, 5, "campfire", lit=False, signal_fire=False, facing="north", waterlogged=False)
    return b


def cairn():
    b = Build("cairn")
    for y, r in ((1, 1), (2, 1), (3, 0), (4, 0)):
        for x in range(1 - r, 2 + r):
            for z in range(1 - r, 2 + r):
                b.set(x + 1, y, z + 1, "mossy_cobblestone" if h(x, y, z, 5) < 0.45 else "cobblestone")
    for x in range(4):
        for z in range(4):
            b.set(x, 0, z, "cobblestone")
    return b


def all_designs():
    """name -> Build. Village buildings and standalone structures."""
    d = {
        "village/plaza": plaza(),
        "village/street_13": street(13),
        "village/street_19": street(19),
        "village/street_junction": street_junction(),
        "village/street_end": street_end(),
        "village/longhouse": longhouse(),
        "village/longhouse_turf": longhouse(turf_roof=True),
        "village/smithy": smithy(),
        "village/sheep_pen": sheep_pen(),
        "village/storehouse": storehouse(),
        "runestone/single": runestone_single(),
        "runestone/trio": runestone_trio(),
        "runestone/cairn": cairn(),
    }
    for i, st in enumerate(("farmer", "shepherd", "fletcher", "librarian", "cleric", "fisherman")):
        d[f"village/turf_house_{st}"] = turf_house(st, i)
    for i in range(3):
        d[f"village/farm_{i}"] = farm(i)
    ship, _ = longship()
    d["longship/longship"] = ship
    return d
