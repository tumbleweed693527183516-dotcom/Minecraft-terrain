"""
Giant Viking warships (drekar): a dragon-headed sea-king's flagship and a large war longship.

Local y = WATER is the sea surface. Below deck the hull is dry (air cells push the sea out).
Spawners sit in dark places (the hold, the cabins) so they work by day, plus a crow's-nest
spawner that wakes at night, an armoured draugr crew on deck and a Draugr Jarl aft.
"""
import math

from .builder import Build
from .kit import FENCE, NS, armor_stand, candle, draugr, h, shield, slab, spawner, stair
from .nbtio import Byte

WATER = 5
DECK = 6


def helmet(item="iron_helmet"):
    """Spawned undead wear helmets so they don't burn on deck in daylight."""
    return {"ArmorItems": [{}, {}, {}, {"id": f"minecraft:{item}", "Count": Byte(1)}],
            "HandItems": [{"id": "minecraft:iron_axe", "Count": Byte(1)}, {}],
            "CustomName": '{"text":"Draugr"}'}


def fence_x(b, x, y, z, waterlogged=False):
    b.set(x, y, z, "spruce_fence", north=False, south=False, east=True, west=True, waterlogged=waterlogged)


def fence_z(b, x, y, z, mat="spruce_fence"):
    b.set(x, y, z, mat, north=True, south=True, east=False, west=False, waterlogged=False)


def line(b, p0, p1, fn):
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    for i in range(n + 1):
        t = i / max(n, 1)
        fn(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), round(z0 + (z1 - z0) * t))


def warship(name, L, B, masts, salt, sail=("red", "white")):
    b = Build(name)
    C = int(math.ceil(B)) + 8          # room for the oars on the west side

    def bm(z):
        t = z / (L - 1)
        return B * math.sin(math.pi * t) ** 0.42

    def hw(z, y):
        return int(round(bm(z) * (0.28 + 0.72 * min(1.0, y / 5.0))))

    def top(z):
        t = z / (L - 1)
        return 9 + int(round(5 * abs(2 * t - 1) ** 3))

    # ---- hull -------------------------------------------------------------------
    for z in range(L):
        T = top(z)
        if bm(z) < 1.6:                                       # stem and stern posts
            for y in range(0, T + 1):
                b.set(C, y, z, "dark_oak_planks")
            continue
        for y in range(0, T + 1):
            w, wp = hw(z, y), hw(z, y - 1) if y else 0
            strake = "dark_oak_planks" if (y // 2) % 2 == 0 else "spruce_planks"
            for x in range(C - max(w, wp), C + max(w, wp) + 1):
                dx = abs(x - C)
                if y == 0:
                    if dx <= w:
                        b.set(x, 0, z, "dark_oak_planks")
                    continue
                if dx >= w:
                    b.set(x, y, z, "stripped_dark_oak_log" if y == T else strake,
                          **({"axis": "z"} if y == T else {}))
                elif y == 1:
                    b.set(x, y, z, "spruce_planks")                # hold floor
                elif y == DECK:
                    b.set(x, y, z, f"{NS}:pine_planks" if (z + salt) % 7 else "spruce_planks")
                else:
                    b.set(x, y, z, "air")
        if 3 <= z <= L - 4:
            b.set(C, -1, z, "dark_oak_log", axis="z")            # keel
    # make the hull watertight: every open cell below deck must be boxed in by planks
    for (x, y, z), v in list(b.blocks.items()):
        if v[0] != "minecraft:air" or y >= DECK:
            continue
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
            if b.get(x + dx, y + dy, z + dz) is None:
                b.set(x + dx, y + dy, z + dz, "dark_oak_planks")
    # keelson and deck beams below deck
    for z in range(4, L - 4):
        if bm(z) >= 1.6:
            b.set(C, 1, z, "stripped_dark_oak_log", axis="z")
            if z % 4 == 0:
                for x in range(C - hw(z, 5) + 1, C + hw(z, 5)):
                    b.set(x, 5, z, "stripped_spruce_log", axis="x")

    # ---- dragon head and curled tail -------------------------------------------
    T0 = top(0)
    NECK = 16
    for k in range(NECK):                                       # thick neck curving up and forward
        z, y = 1 - round(k * 0.5), T0 + k
        r = 1 if k > 1 else 0
        for x in range(C - r, C + r + 1):
            for dz in ((0, 1) if k > 4 else (0,)):
                b.set(x, y, z + dz, "dark_oak_planks" if (k + x) % 3 else "stripped_dark_oak_log",
                      **({} if (k + x) % 3 else {"axis": "y"}))
        if k % 2 == 0 and k > 2:
            stair(b, C, y, z + 2, "dark_oak_stairs", "north", "top")   # spines down the back of the neck
    hy, hz = T0 + NECK, 1 - round((NECK - 1) * 0.5)
    for z in range(hz - 8, hz + 2):                             # head: 5 wide, 4 tall, 10 long
        for x in range(C - 2, C + 3):
            for y in range(hy, hy + 4):
                if abs(x - C) == 2 and (y == hy + 3 or z < hz - 5):
                    continue                                     # taper the snout
                b.set(x, y, z, "dark_oak_planks")
    for z in range(hz - 8, hz - 2):                             # gaping jaws
        for x in range(C - 1, C + 2):
            b.set(x, hy + 1, z, "air")
            b.set(x, hy - 1, z, "dark_oak_planks")
        b.set(C, hy, z, "red_wool")                             # tongue
    for x in (C - 1, C + 1):
        for y in (hy, hy + 2):
            b.set(x, y, hz - 8, "bone_block", axis="y")         # fangs
    for x in (C - 2, C + 2):
        b.set(x, hy + 2, hz - 4, "redstone_block")              # glowing eyes
        b.set(x, hy + 2, hz - 3, "redstone_block")
    for x in (C - 1, C + 1):
        b.fill(x, hy + 4, hz - 1, x, hy + 5, hz - 1, "dark_oak_fence", **FENCE)   # swept-back horns
        b.fill(x, hy + 5, hz, x, hy + 6, hz + 1, "dark_oak_fence", **FENCE)
    for z in range(hz - 6, hz + 1, 2):
        stair(b, C, hy + 4, z, "dark_oak_stairs", "south")      # crest
    Tl = top(L - 1)
    for k in range(10):                                         # tail curling up and back over
        a = k / 9 * math.pi * 1.1
        z = L - 1 + round(3 * math.sin(a))
        y = Tl + round(6 * (1 - math.cos(a)) / 2 * 1.6)
        b.set(C, y, z, "dark_oak_planks")
        b.set(C, y + 1, z, "dark_oak_planks")
    b.set(C, Tl + 10, L - 2, f"{NS}:carved_post", axis="y")

    # ---- shields along the bulwarks, oars below them ----------------------------
    for z in range(6, L - 6):
        if bm(z) < 3:
            continue
        T = top(z)
        for side in (-1, 1):
            w = hw(z, T - 1)
            x = C + side * (w + 1)
            if z % 2 == 0 and b.get(x, T - 1, z) is None:
                shield(b, x, T - 1, z, "west" if side < 0 else "east", salt + z)
            if z % 4 == 1 and 10 <= z <= L - 11:                 # oars: out and down to the sea
                ox = C + side * (w + 1)
                for i in range(7):
                    y = T - 2 if i < 3 else (T - 3 if i < 5 else WATER)
                    y = max(y, WATER)
                    fence_x(b, ox + side * i, y, z, waterlogged=(y == WATER))
                b.set(ox + side * 7, WATER, z, "spruce_slab", type="top", waterlogged=True)

    # ---- rowing benches and sea chests on deck ----------------------------------
    for z in range(10, L - 26, 4):
        w = hw(z, DECK + 1)
        for x in range(C - w + 1, C + w):
            if abs(x - C) > 1:
                slab(b, x, DECK + 1, z, "spruce_slab")
        for side in (-1, 1):
            x = C + side * (w - 1)
            if (z // 4) % 3 == 0:
                b.chest(x, DECK + 1, z + 1, "east" if side < 0 else "west", f"{NS}:chests/warship")
            else:
                b.barrel(x, DECK + 1, z + 1, facing="up")

    # ---- masts, sails, yards, crow's nests, rigging --------------------------------
    mast_top = 38 if masts == 2 else 36
    zs = [round(L * 0.36), round(L * 0.6)] if masts == 2 else [round(L * 0.45)]
    for mi, zm in enumerate(zs):
        top_y = mast_top - (4 if mi == 0 and masts == 2 else 0)
        b.fill(C, 1, zm, C, top_y, zm, "stripped_spruce_log", axis="y")
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b.set(C + dx, DECK + 1, zm + dz, "dark_oak_planks")      # mast partner
        yard_y = top_y - 4
        half = int(B) + 2
        b.fill(C - half, yard_y, zm - 1, C + half, yard_y, zm - 1, "spruce_log", axis="x")
        sail_lo = DECK + 7
        for x in range(C - half + 1, C + half):
            for y in range(sail_lo, yard_y):
                u = (x - (C - half)) / (2 * half)
                v = (y - sail_lo) / (yard_y - sail_lo)
                bulge = round(2.4 * math.sin(math.pi * u) * math.sin(math.pi * (0.25 + 0.75 * v)))
                col = sail[(abs(x - C) // 3) % 2]
                b.set(x, y, zm - 1 - bulge, f"{col}_wool")
                if bulge >= 2:
                    b.set(x, y, zm - bulge, f"{col}_wool")           # no see-through gaps in the billow
        # sheets from the sail's lower corners down to the bulwarks
        for side in (-1, 1):
            line(b, (C + side * (half - 1), sail_lo, zm - 1), (C + side * (hw(zm + 4, 8) - 1), top(zm) + 1, zm + 4),
                 lambda x, y, z: b.set(x, y, z, "spruce_fence", **FENCE) if b.get(x, y, z) is None else None)
        # crow's nest above the yard
        ny = yard_y + 1
        for x in range(C - 1, C + 2):
            for z in range(zm - 1, zm + 2):
                if (x, z) != (C, zm):
                    b.set(x, ny, z, "dark_oak_planks")
                    b.set(x, ny + 1, z, "dark_oak_fence", **FENCE)
        b.set(C, top_y + 1, zm, "red_banner" if mi % 2 == 0 else "blue_banner", rotation=0,
              nbt={"id": "minecraft:banner"})
        spawner(b, C + 1, ny + 1, zm + 1, "skeleton", entity=helmet("chainmail_helmet"))
        b.set(C - 1, ny + 1, zm - 1, "air")
        # stays: fore and back from the masthead to the stems
        line(b, (C, top_y - 1, zm), (C, top(3) + 2, 3), lambda x, y, z: fence_z(b, x, y, z)
             if b.get(x, y, z) in (None, "minecraft:air") else None)
        line(b, (C, top_y - 1, zm), (C, top(L - 4) + 2, L - 4), lambda x, y, z: fence_z(b, x, y, z)
             if b.get(x, y, z) in (None, "minecraft:air") else None)
        # ladder up the mast
        for y in range(DECK + 1, ny + 1):
            b.set(C, y, zm + 1, "ladder", facing="south", waterlogged=False)
        b.set(C, ny, zm + 1, "air")

    # ---- stern castle: captain's cabin with a raised deck on top ----------------
    c0, c1 = L - 26, L - 11
    roof = DECK + 6
    for z in range(c0, c1 + 1):
        w = hw(z, DECK + 1) - 1
        for x in range(C - w, C + w + 1):
            edge = abs(x - C) == w or z in (c0, c1)
            for y in range(DECK + 1, roof):
                if edge:
                    post = (z - c0) % 4 == 0 or abs(x - C) == w and z in (c0, c1)
                    b.set(x, y, z, "dark_oak_log" if post else "spruce_planks", **({"axis": "y"} if post else {}))
                else:
                    b.set(x, y, z, "air")
            b.set(x, roof, z, "dark_oak_planks")
            if edge:
                b.set(x, roof + 1, z, "dark_oak_fence", **FENCE)
    b.door(C, DECK + 1, c0, "north", wood="dark_oak")
    b.door(C - 1, DECK + 1, c0, "north", wood="dark_oak", hinge="right")
    for x in (C - 3, C + 2):
        b.set(x, DECK + 3, c0, "glass_pane", **FENCE)
    # stairs up to the raised deck on the starboard side
    w0 = hw(c0, DECK + 1) - 1
    for i in range(5):
        stair(b, C + w0 - 1, DECK + 1 + i, c0 - 5 + i, "spruce_stairs", "south")
    b.set(C + w0 - 1, roof + 1, c0, "air")
    # steering oar on the starboard quarter, tiller on the raised deck
    zr = c1 - 3
    xr = C + hw(zr, 8) + 1
    b.fill(xr, 0, zr, xr, roof + 1, zr, "stripped_spruce_log", axis="y")
    b.fill(xr, 0, zr + 1, xr, 3, zr + 1, "spruce_planks")
    for x in range(C + 1, xr):
        fence_x(b, x, roof + 1, zr)
    # cabin interior
    w = hw((c0 + c1) // 2, DECK + 1) - 2
    b.bed(C - w, DECK + 1, c1 - 2, "south", "red")
    b.set(C - w, DECK + 1, c1 - 4, "cartography_table")
    b.set(C + w, DECK + 1, c1 - 1, "lectern", facing="west", has_book=False, powered=False)
    b.chest(C - 1, DECK + 1, c1 - 1, "north", f"{NS}:chests/warship_captain")
    b.chest(C + 1, DECK + 1, c1 - 1, "north", f"{NS}:chests/warship_captain")
    armor_stand(b, C + w, DECK + 1, c1 - 4, 270, hand="iron_sword", head="golden_helmet",
                chest="iron_chestplate", offhand="shield")
    for z in (c0 + 3, c1 - 3):
        b.set(C, roof - 1, z, "soul_lantern", hanging=True, waterlogged=False)
    spawner(b, C + w, DECK + 1, c0 + 2, "vindicator")
    draugr(b, C, DECK + 1, c1 - 5, "zombie", "jarl", boss=True, yaw=0)

    # ---- seer's hut on the fore deck: a witch spawner among herbs and candles ----
    f0, f1 = 8, 15
    for z in range(f0, f1 + 1):
        w = min(3, hw(z, DECK + 1) - 2)
        for x in range(C - w, C + w + 1):
            edge = abs(x - C) == w or z in (f0, f1)
            for y in range(DECK + 1, DECK + 4):
                b.set(x, y, z, ("black_wool" if (x + z) % 2 else "gray_wool") if edge else "air")
            b.set(x, DECK + 4, z, "black_wool" if abs(x - C) < w else "dark_oak_slab",
                  **({} if abs(x - C) < w else {"type": "bottom", "waterlogged": False}))
    b.air(C, DECK + 1, f1, C, DECK + 2, f1)
    b.set(C - 2, DECK + 1, f0 + 1, "brewing_stand", has_bottle_0=False, has_bottle_1=False, has_bottle_2=False)
    b.set(C + 2, DECK + 1, f0 + 1, "cauldron")
    b.set(C, DECK + 1, f0 + 1, "skeleton_skull", rotation=8)
    candle(b, C - 2, DECK + 1, f0 + 3, 3)
    spawner(b, C + 2, DECK + 1, f0 + 4, "witch")
    b.chest(C - 2, DECK + 1, f1 - 1, "east", f"{NS}:chests/hof")

    # ---- the hold: three dark compartments with hatches and ladders ----------------
    bulk = [round(L * 0.33), round(L * 0.66)]
    for zb in bulk:
        for x in range(C - hw(zb, 5) + 1, C + hw(zb, 5)):
            for y in range(2, DECK):
                b.set(x, y, zb, "spruce_planks" if abs(x - C) > 1 or y > 3 else "air")
    hatches = [round(L * 0.2), round(L * 0.5), round(L * 0.75)]
    for zh in hatches:
        b.set(C + 2, DECK, zh, "air")
        b.fill(C + 3, 2, zh, C + 3, DECK - 1, zh, "stripped_spruce_log", axis="y")
        for y in range(2, DECK + 1):
            b.set(C + 2, y, zh, "ladder", facing="west", waterlogged=False)
    # fore hold: cargo, with zombies and spiders in the dark
    z0, z1 = 6, bulk[0] - 1
    for z in range(z0, z1):
        w = hw(z, 3) - 1
        if w < 2:
            continue
        for x in (C - w, C + w):
            r = h(x, z, salt)
            if r < 0.4:
                b.barrel(x, 2, z, loot=f"{NS}:chests/ship_cargo" if r < 0.08 else None)
                if r < 0.2:
                    b.barrel(x, 3, z)
            elif r < 0.6:
                b.set(x, 2, z, "hay_block", axis="z")
            elif r < 0.7:
                b.set(x, 2, z, "white_wool")
            elif r < 0.75:
                b.set(x, 4, z, "cobweb")
    spawner(b, C - 2, 2, z0 + (z1 - z0) // 2, "zombie", entity=helmet())
    spawner(b, C + 2, 2, z0 + 3 + (z1 - z0) // 2, "spider")
    b.chest(C - 1, 2, z1 - 1, "south", f"{NS}:chests/warship")
    # mid hold: prisoners' cage and plunder
    m0, m1 = bulk[0] + 1, bulk[1] - 1
    cz = (m0 + m1) // 2
    w = hw(cz, 3) - 1
    for z in range(cz - 3, cz + 4):
        b.set(C - 2, 2, z, "iron_bars", north=True, south=True, east=False, west=False, waterlogged=False)
        b.set(C - 2, 3, z, "iron_bars", north=True, south=True, east=False, west=False, waterlogged=False)
    spawner(b, C - w + 1, 2, cz, "zombie_villager")
    b.set(C - w + 1, 3, cz - 2, "chain", axis="y", waterlogged=False)
    for z in (m0 + 1, m1 - 1):
        b.chest(C + w, 2, z, "west", f"{NS}:chests/warship")
        b.set(C + w, 2, z + (1 if z == m0 + 1 else -1), "gold_block")
    spawner(b, C + w - 1, 2, cz, "skeleton", entity=helmet("chainmail_helmet"))
    for z in range(m0, m1, 3):
        b.set(C + w, 3, z, "cobweb") if h(z, salt) < 0.5 else None
    # aft hold: the armoury, guarded by strays
    a0, a1 = bulk[1] + 1, L - 7
    for z in range(a0 + 1, a1, 3):
        w = hw(z, 3) - 1
        if w >= 2:
            armor_stand(b, C - w, 2, z, 90, hand="iron_axe", head="iron_helmet", chest="chainmail_chestplate")
    b.chest(C + 1, 2, a1 - 1, "north", f"{NS}:chests/warship")
    b.set(C - 1, 2, a1 - 1, "smithing_table")
    b.set(C + 2, 2, a0 + 2, "grindstone", face="floor", facing="north")
    spawner(b, C + 1, 2, (a0 + a1) // 2, "stray", entity=helmet())

    # ---- deck crew and lights --------------------------------------------------
    for i, z in enumerate(range(14, L - 28, 7)):
        x = C + (2 if i % 2 else -2)
        draugr(b, x, DECK + 1, z, ("zombie", "skeleton", "stray")[i % 3], ("iron", "chain", "leather")[i % 3],
               yaw=float(90 * (i % 4)))
    for z in (hatches[0], hatches[1], hatches[2]):
        b.set(C - 2, DECK + 1, z, "spruce_fence", **FENCE)
        b.set(C - 2, DECK + 2, z, "lantern", hanging=False, waterlogged=False)
    return b


def catalogue3():
    return {
        "sea/sea_king_drakkar": warship("sea_king_drakkar", 91, 10.5, 2, 0, ("red", "white")),
        "sea/war_drakkar": warship("war_drakkar", 73, 8.5, 1, 3, ("blue", "white")),
    }
