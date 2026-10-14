"""
Viking structures, batch 2: burial dungeons, sacred and civic sites, coastal life, ships
and wrecks. Same conventions as viking.py unless noted (dungeons place y = DEPTH at ground).
"""
import math

from .builder import Build
from .designs import longship, runestone_at
from .kit import (FENCE, NS, animals, armor_stand, arrow_trap, bench, candle, cart, chopping_block, cobweb,
                  compose, crates, crossed_horns, draugr, fur, gable_end, gable_roof, h, hanging_lantern,
                  hide_frame, kitchen_garden, plank_gable, potted, shield, skull, slab, spawner, stair, timber,
                  turf_wall, water_barrel, weather, window, woodpile)
from .nbtio import Byte


def ellipse_mound(b, cx, cz, rx, rz, height, base_y, salt, skirt=4):
    """Grassy burial mound with a smooth dome profile; a dirt skirt below hides slopes."""
    for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
        for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
            d = math.hypot((x - cx) / rx, (z - cz) / rz)
            if d > 1.0:
                continue
            top = base_y + int(round(height * math.sqrt(max(0.0, 1 - d * d))))
            for y in range(base_y - skirt, top + 1):
                if b.get(x, y, z) is None:
                    b.set(x, y, z, "grass_block" if y == top else ("dirt" if y > top - 3 else "stone"),
                          **({"snowy": False} if y == top else {}))
            if b.get(x, top + 1, z) is None and h(x, z, salt) < 0.12:
                b.set(x, top + 1, z, ("grass", "fern", "cornflower", "moss_carpet", f"{NS}:heather")[
                    int(h(z, x, salt) * 5)])


def stone_lined(b, x0, x1, y0, y1, z0, z1, salt, ceiling="timber"):
    """A chamber: dressed stone walls and floor, a timber (or corbelled stone) ceiling, air inside."""
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            for y in range(y0 - 1, y1 + 2):
                edge = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1) or y in (y0 - 1, y1 + 1)
                if not edge:
                    b.set(x, y, z, "air")
                    continue
                r = h(x, y, z, salt)
                if y == y1 + 1 and ceiling == "timber":
                    b.set(x, y, z, "dark_oak_log" if x % 3 == 0 else "dark_oak_planks", **({"axis": "z"} if x % 3 == 0 else {}))
                elif y == y0 - 1:
                    b.set(x, y, z, "cobblestone" if r < 0.5 else ("mossy_cobblestone" if r < 0.75 else "gravel"))
                else:
                    b.set(x, y, z, "stone_bricks" if r < 0.45 else "mossy_stone_bricks" if r < 0.7 else
                          "cracked_stone_bricks" if r < 0.85 else "cobblestone")


# ---------------------------------------------------------------------------
# Burial mound (haugr): a small dungeon
# ---------------------------------------------------------------------------
DEPTH_MOUND = 7


def burial_mound(salt):
    b = Build(f"burial_mound_{salt}")
    G = DEPTH_MOUND           # ground level in template coordinates
    cx, cz = 11, 13
    # chamber
    stone_lined(b, cx - 4, cx + 4, 1, 5, cz - 3, cz + 6, salt)
    # passage descending from the mound's foot (north side) into the chamber
    for i, z in enumerate(range(0, cz - 3)):
        y = max(1, G - (i * G) // (cz - 4))
        for x in range(cx - 1, cx + 2):
            b.set(x, y - 1, z, "cobblestone" if h(x, z, salt) < 0.6 else "mossy_cobblestone")
            for yy in range(y, y + 3):
                b.set(x, yy, z, "air")
        for x in (cx - 2, cx + 2):
            for yy in range(y - 1, y + 4):
                b.set(x, yy, z, "stripped_dark_oak_log" if z % 3 == 0 else "stone_bricks",
                      **({"axis": "y"} if z % 3 == 0 else {}))
        for x in range(cx - 2, cx + 3):
            b.set(x, y + 3, z, "dark_oak_planks")
        if z < 3:
            for x in range(cx - 1, cx + 2):
                b.set(x, y - 1, z, "dirt_path")
    # entrance portal: two standing stones and a lintel
    for x in (cx - 2, cx + 2):
        b.fill(x, G, 0, x, G + 3, 0, "polished_andesite")
    b.fill(cx - 2, G + 4, 0, cx + 2, G + 4, 0, "polished_andesite_slab", type="bottom", waterlogged=False)
    ellipse_mound(b, cx, cz + 1, 10.5, 9.0, 7, G, salt)
    # re-open the passage mouth through the mound
    for z in range(0, 3):
        for x in range(cx - 1, cx + 2):
            for yy in range(G, G + 3):
                b.set(x, yy, z, "air")
    # standing stones around the mound foot
    for i in range(10):
        a = i * math.pi * 2 / 10 + 0.3
        x, z = int(round(cx + 12 * math.cos(a))), int(round(cz + 1 + 10.5 * math.sin(a)))
        if z > 2:
            b.fill(x, G, z, x, G + 1 + int(h(i, salt) * 2), z, "andesite" if i % 2 else "stone")
    # trap in the passage
    tz = cz - 6
    ty = max(1, G - ((tz) * G) // (cz - 4))
    arrow_trap(b, (cx - 1, ty, tz), [(cx - 2, ty, tz, "east")])
    arrow_trap(b, (cx + 1, ty, tz), [(cx + 2, ty, tz, "west")])
    b.set(cx, ty, tz, "stone_pressure_plate", powered=False)
    # bier, grave goods, guardians
    for x in range(cx - 1, cx + 2):
        for z in range(cz + 2, cz + 5):
            b.set(x, 1, z, "polished_andesite")
        slab(b, x, 2, cz + 3, "polished_andesite_slab")
    b.set(cx, 3, cz + 3, "skeleton_skull", rotation=8)
    b.chest(cx - 3, 1, cz + 6, "north", f"{NS}:chests/burial")
    b.chest(cx + 3, 1, cz + 6, "north", f"{NS}:chests/burial")
    b.set(cx, 1, cz + 6, "decorated_pot", facing="north", cracked=False, waterlogged=False)
    armor_stand(b, cx + 3, 1, cz, 270, hand="iron_axe", offhand="shield", head="iron_helmet")
    for x, z in ((cx - 4, cz - 3), (cx + 4, cz - 3), (cx - 4, cz + 6), (cx + 4, cz + 6)):
        cobweb(b, x, 5, z)
    for x, z in ((cx - 4, cz + 1), (cx + 4, cz + 4)):
        b.set(x, 1, z, "bone_block", axis="y")
        skull(b, x, 2, z, int(h(x, z) * 16))
    for z in (cz - 1, cz + 4):
        b.set(cx, 5, z, "chain", axis="y", waterlogged=False)
        b.set(cx, 4, z, "soul_lantern", hanging=True, waterlogged=False)
    # caged spawner in the corner
    b.set(cx - 4, 1, cz - 3, "spawner")
    spawner(b, cx - 4, 1, cz - 3, "zombie")
    for x, z in ((cx - 3, cz - 3), (cx - 4, cz - 2), (cx - 3, cz - 2)):
        b.set(x, 1, z, "iron_bars", north=False, south=False, east=False, west=False, waterlogged=False)
    draugr(b, cx - 2, 1, cz + 1, "zombie", "chain", yaw=180)
    draugr(b, cx + 2, 1, cz + 1, "zombie", "iron", yaw=180)
    draugr(b, cx, 1, cz - 1, "skeleton", "leather", yaw=180)
    weather(b, salt, vines=False)
    return b


# ---------------------------------------------------------------------------
# Ship burial: a longship laid in a timber chamber under a great mound
# ---------------------------------------------------------------------------
DEPTH_SHIP = 8


def ship_burial(salt):
    b = Build(f"ship_burial_{salt}")
    G = DEPTH_SHIP
    ship, _ = longship()
    (sx0, sy0, sz0), (sx1, sy1, sz1) = ship.bounds()
    W, L = sx1 - sx0 + 1, sz1 - sz0 + 1
    x0, z0 = 6, 10
    stone_lined(b, x0 - 1, x0 + W, 1, 15, z0 - 1, z0 + L, salt)
    # timber burial house on deck, like Oseberg: walls lining the chamber
    for z in range(z0 - 1, z0 + L + 1, 4):
        for x in (x0 - 1, x0 + W):
            b.fill(x, 1, z, x, 15, z, "dark_oak_log", axis="y")
    # lay the ship in a cradle of earth so it sits upright
    for (x, y, z), v in ship.blocks.items():
        if v[0] == "minecraft:air":
            continue
        b.blocks[(x - sx0 + x0, y - sy0 + 1, z - sz0 + z0)] = v
    for x in range(x0, x0 + W):
        for z in range(z0, z0 + L):
            if b.get(x, 1, z) == "minecraft:air":
                b.set(x, 1, z, "coarse_dirt" if h(x, z) < 0.5 else "gravel")
    # grave goods on deck and around the hull
    deck_y = 2 + 3 - sy0
    for i, z in enumerate(range(z0 + 6, z0 + L - 6, 5)):
        b.chest(x0 + W // 2, deck_y, z, "north", f"{NS}:chests/ship_burial" if i % 2 == 0 else f"{NS}:chests/burial")
    for z in range(z0 + 2, z0 + L - 2, 6):
        for x in (x0, x0 + W - 1):
            b.set(x, 2, z, "decorated_pot", facing="north", cracked=h(x, z) < 0.4, waterlogged=False)
    for z in range(z0 + 1, z0 + L - 1, 5):
        b.set(x0 + W // 2, 15, z, "chain", axis="y", waterlogged=False)
        b.set(x0 + W // 2, 14, z, "soul_lantern", hanging=True, waterlogged=False)
    for x, z in ((x0 - 1, z0 - 1), (x0 + W, z0 - 1), (x0 - 1, z0 + L), (x0 + W, z0 + L)):
        cobweb(b, x + (1 if x < x0 else -1), 14, z + (1 if z < z0 else -1))
    spawner(b, x0 - 1 + 1, 1, z0 + 3, "skeleton")
    spawner(b, x0 + W - 1, 1, z0 + L - 4, "stray")
    draugr(b, x0 + W // 2, deck_y, z0 + L // 2 + 2, "zombie", "jarl", boss=True, yaw=0)
    for i, (x, z) in enumerate(((x0 + 1, z0 + 5), (x0 + W - 2, z0 + 9), (x0 + 1, z0 + L - 9), (x0 + W - 2, z0 + L - 6))):
        draugr(b, x, 2, z, "zombie" if i % 2 else "skeleton", "iron" if i < 2 else "chain")
    # long sloping entrance passage from the north
    cxp = x0 + W // 2
    for i, z in enumerate(range(0, z0 - 1)):
        y = max(1, G - (i * (G - 1)) // max(1, z0 - 3))
        for x in range(cxp - 1, cxp + 2):
            b.set(x, y - 1, z, "cobblestone")
            for yy in range(y, y + 3):
                b.set(x, yy, z, "air")
        for x in (cxp - 2, cxp + 2):
            for yy in range(y - 1, y + 4):
                b.set(x, yy, z, "stone_bricks")
        for x in range(cxp - 2, cxp + 3):
            b.set(x, y + 3, z, "dark_oak_planks")
    for x in range(cxp - 1, cxp + 2):
        for yy in range(1, 4):
            b.set(x, yy, z0 - 1, "air")
    ty = max(1, G - (4 * (G - 1)) // max(1, z0 - 3))
    arrow_trap(b, (cxp - 1, ty, 4), [(cxp - 2, ty, 4, "east")])
    arrow_trap(b, (cxp + 1, ty, 4), [(cxp + 2, ty, 4, "west")])
    ellipse_mound(b, x0 + W / 2, z0 + L / 2, W / 2 + 9, L / 2 + 8, 11, G, salt)
    for z in range(0, 3):
        for x in range(cxp - 1, cxp + 2):
            for yy in range(G, G + 3):
                b.set(x, yy, z, "air")
    for x in (cxp - 2, cxp + 2):
        b.fill(x, G, 0, x, G + 4, 0, "chiseled_stone_bricks")
    runestone_at(b, cxp + 5, G, 1, "x", salt)
    weather(b, salt, vines=False)
    return b


# ---------------------------------------------------------------------------
# Stave church (Borgund-style): stacked roofs, a covered gallery, dragon gables
# ---------------------------------------------------------------------------
def pyramid(b, cx, cz, half, y0, mat="dark_oak", cap=True):
    for k in range(half + 1):
        r = half - k
        y = y0 + k
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                if max(abs(x - cx), abs(z - cz)) == r:
                    if r == 0:
                        slab(b, x, y, z, f"{mat}_slab")
                    elif abs(x - cx) == r and abs(z - cz) == r:
                        b.set(x, y, z, f"{mat}_planks")
                    elif abs(x - cx) == r:
                        stair(b, x, y, z, f"{mat}_stairs", "east" if x < cx else "west")
                    else:
                        stair(b, x, y, z, f"{mat}_stairs", "south" if z < cz else "north")
    return y0 + half


def stave_church(salt):
    b = Build(f"stave_church_{salt}")
    cx, cz = 10, 11
    stave = lambda x, y, z: ("stripped_dark_oak_log" if (x + z) % 2 else "dark_oak_log", {"axis": "y"})  # noqa: E731
    # stone plinth and the covered gallery (svalgang)
    for x in range(cx - 8, cx + 9):
        for z in range(cz - 8, cz + 9):
            b.set(x, 0, z, "cobblestone" if h(x, z, salt) < 0.7 else "mossy_cobblestone")
            b.set(x, 1, z, "spruce_planks")
    for x in range(cx - 8, cx + 9):
        for z in range(cz - 8, cz + 9):
            ring = max(abs(x - cx), abs(z - cz))
            if ring == 8:
                b.set(x, 2, z, "dark_oak_fence", **FENCE)
                if (x + z) % 3 == 0:
                    b.fill(x, 2, z, x, 5, z, "dark_oak_log", axis="y")
            if ring in (7, 8, 9):
                y = 5 if ring == 9 else (6 if ring == 8 else 7)
                b.set(x, y, z, "dark_oak_slab", type="bottom", waterlogged=False)
    # nave walls
    for x in range(cx - 6, cx + 7):
        for z in range(cz - 6, cz + 7):
            ring = max(abs(x - cx), abs(z - cz))
            if ring == 6:
                for y in range(2, 10):
                    b.set(x, y, z, *stave(x, y, z))
            elif ring < 6:
                b.air(x, 2, z, x, 20, z)
    y = pyramid(b, cx, cz, 7, 9)
    # second tier
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            ring = max(abs(x - cx), abs(z - cz))
            if ring == 3:
                for yy in range(11, 16):
                    b.set(x, yy, z, *stave(x, yy, z))
            elif ring < 3:
                b.air(x, 9, z, x, 15, z)
    pyramid(b, cx, cz, 4, 15)
    # bell tower spire
    for x in range(cx - 1, cx + 2):
        for z in range(cz - 1, cz + 2):
            if (x, z) != (cx, cz):
                b.fill(x, 19, z, x, 21, z, "dark_oak_fence", **FENCE)
    pyramid(b, cx, cz, 2, 22)
    b.set(cx, 25, cz, f"{NS}:carved_post", axis="y")
    b.set(cx, 26, cz, "lightning_rod", facing="up", powered=False, waterlogged=False)
    # dragon heads rearing from the middle of every roof edge, both tiers
    for (dx, dz, face) in ((0, -1, "south"), (0, 1, "north"), (-1, 0, "east"), (1, 0, "west")):
        for r, yy in ((7, 9), (4, 15)):
            x, z = cx + dx * r, cz + dz * r
            b.set(x, yy + 1, z, f"{NS}:carved_post", axis="y")
            b.set(x, yy + 2, z, "dark_oak_fence", **FENCE)
            stair(b, x + dx, yy + 2, z + dz, "dark_oak_stairs", face, "top")
    # doors, portal posts
    b.air(cx, 2, cz - 8, cx, 3, cz - 8)
    b.door(cx, 2, cz - 6, "north")
    for x in (cx - 1, cx + 1):
        b.fill(x, 2, cz - 6, x, 4, cz - 6, f"{NS}:carved_post", axis="y")
    # interior: inner ring of staves, altar, benches, candles
    for x in range(cx - 3, cx + 4, 3):
        for z in range(cz - 3, cz + 4, 3):
            if x != cx:
                b.fill(x, 2, z, x, 10, z, "stripped_dark_oak_log", axis="y")
    slab(b, cx - 1, 2, cz + 5, "polished_andesite_slab", "top")
    slab(b, cx + 1, 2, cz + 5, "polished_andesite_slab", "top")
    b.set(cx, 2, cz + 5, "lectern", facing="north", has_book=False, powered=False)
    for x in (cx - 1, cx + 1):
        candle(b, x, 3, cz + 5, 3)
    for z in range(cz - 4, cz + 3, 2):
        for x in (cx - 4, cx - 2, cx + 2, cx + 4):
            bench(b, x, 2, z, "south")
    for z in (cz - 3, cz + 3):
        hanging_lantern(b, cx, 10, z, length=2)
    b.chest(cx + 5, 2, cz + 5, "north", f"{NS}:chests/hof")
    # churchyard: runestones and a lychgate path
    runestone_at(b, cx - 11, 1, cz - 9, "x", salt)
    runestone_at(b, cx + 10, 1, cz + 7, "z", salt + 1)
    for z in range(cz - 12, cz - 8):
        b.set(cx, 0, z, "gravel")
    b.villager(cx, 2, cz)
    weather(b, salt)
    return b


# ---------------------------------------------------------------------------
# Mead hall homestead: the great hall in its own fenced yard
# ---------------------------------------------------------------------------
def mead_hall(hall_build, salt):
    b = Build(f"mead_hall_{salt}")
    (x0, y0, z0), (x1, y1, z1) = hall_build.bounds()
    W, L = x1 - x0 + 1, z1 - z0 + 1
    ox, oz = 10, 8
    compose(b, hall_build, ox - x0, -y0, oz - z0)
    X1, Z1 = ox + W + 9, oz + L + 7
    for x in range(0, X1 + 1):
        for z in (0, Z1):
            if not (ox - x0 + 8 <= x <= ox - x0 + 12 and z == 0):
                b.set(x, 1, z, "spruce_fence", **FENCE)
    for z in range(0, Z1 + 1):
        for x in (0, X1):
            b.set(x, 1, z, "spruce_fence", **FENCE)
    hx = ox - x0 + 10     # hall door (its centre line)
    for x in (hx - 3, hx + 3):
        b.fill(x, 1, 0, x, 4, 0, f"{NS}:carved_post", axis="y")
        b.banner(x, 4, -1, "north", "red")
    for z in range(1, oz):
        b.set(hx, 0, z, "dirt_path" if z % 3 else "gravel")
    cart(b, 4, 1, 6, "z")
    chopping_block(b, X1 - 5, 1, 4)
    woodpile(b, X1 - 3, 1, 8, 6, axis="z")
    hide_frame(b, 3, 1, Z1 - 8, "z")
    kitchen_garden(b, X1 - 8, Z1 - 7, 6, 5, salt=salt)
    water_barrel(b, 3, 1, 3)
    runestone_at(b, 5, 1, Z1 - 3, "x", salt)
    animals(b, "chicken", [(6, 1, 12), (7, 1, 14), (5, 1, 15)])
    animals(b, "horse", [(X1 - 4, 1, Z1 - 12)])
    for x, z in ((ox - 2, 2), (ox + W + 1, 2)):
        b.set(x, 1, z, "spruce_fence", **FENCE)
        b.set(x, 2, z, "lantern", hanging=False, waterlogged=False)
    weather(b, salt)
    return b


# ---------------------------------------------------------------------------
# Fishing hamlet: boathouse, net sheds, drying racks and a jetty
# ---------------------------------------------------------------------------
def hut(b, x0, z0, w, d, salt, roof="turf", job=None):
    cx = x0 + w // 2
    half = w // 2
    wall = turf_wall(salt) if roof == "turf" else timber(3, "planks", salt)
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + d):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "spruce_planks")
            edge = x in (x0, x0 + w - 1) or z in (z0, z0 + d - 1)
            for y in range(2, 4):
                b.set(x, y, z, *(wall(x, y, z) if edge else ("air", {})))
    gable_roof(b, cx, lambda z: half, z0, z0 + d - 1, 4, roof, overhang=1, salt=salt)
    for z in (z0, z0 + d - 1):
        gable_end(b, cx, lambda zz: half, z, 4, 4, plank_gable)
    b.door(cx, 2, z0, "north")
    window(b, x0, 3, z0 + d // 2, "west")
    b.set(cx - 1, 2, z0 + d - 2, "barrel", nbt={"id": "minecraft:barrel"}, facing="up", open=False)
    b.bed(cx + 1, 2, z0 + d - 3, "south", "light_blue")
    hanging_lantern(b, cx, 4 + half - 2, z0 + d // 2, length=1)
    if job:
        b.set(cx - 1, 2, z0 + 1, job[0], **job[1])


def fishing_hamlet(salt):
    b = Build(f"fishing_hamlet_{salt}")
    for x in range(0, 34):
        for z in range(0, 28):
            b.set(x, 0, z, "gravel" if h(x, z, salt) < 0.35 else ("coarse_dirt" if h(z, x) < 0.5 else "sand"))
    hut(b, 2, 12, 7, 9, salt, "turf", ("barrel", {"facing": "up", "open": False}))
    hut(b, 11, 15, 7, 8, salt + 1, "thatch", ("smoker", {"facing": "south", "lit": False}))
    # boathouse (naust): long open-ended shed with a boat inside
    bx0, bz0, bw, bd = 21, 6, 9, 18
    for z in range(bz0, bz0 + bd):
        for x in range(bx0, bx0 + bw):
            b.set(x, 0, z, "cobblestone" if x in (bx0, bx0 + bw - 1) else "gravel")
        for x in (bx0, bx0 + bw - 1):
            for y in range(1, 4):
                b.set(x, y, z, *turf_wall(salt)(x, y, z))
        b.air(bx0 + 1, 1, z, bx0 + bw - 2, 6, z)
    gable_roof(b, bx0 + bw // 2, lambda z: bw // 2, bz0, bz0 + bd - 1, 4, "turf", overhang=1, salt=salt)
    gable_end(b, bx0 + bw // 2, lambda z: bw // 2, bz0 + bd - 1, 4, 1, plank_gable)
    b.entity(bx0 + bw / 2, 1.0, bz0 + bd / 2, {"id": "minecraft:boat", "Type": "spruce"})
    for z in range(bz0 + 2, bz0 + bd - 2, 4):
        b.set(bx0 + 1, 2, z, "barrel", nbt={"id": "minecraft:barrel", "LootTable": f"{NS}:chests/fishing"},
              facing="up", open=False) if z == bz0 + 2 else b.set(bx0 + 1, 1, z, "cobweb")
    # jetty out over the water (north)
    for z in range(-12, 4):
        for x in (bx0 + 3, bx0 + 4, bx0 + 5):
            b.set(x, 0, z, "spruce_planks" if x != bx0 + 4 or z % 4 else "spruce_slab",
                  **({} if x != bx0 + 4 or z % 4 else {"type": "top", "waterlogged": False}))
        if z % 4 == 0:
            for x in (bx0 + 2, bx0 + 6):
                b.fill(x, -3, z, x, 1, z, "spruce_log", axis="y")
    b.set(bx0 + 2, 2, -12, "lantern", hanging=False, waterlogged=False)
    b.set(bx0 + 6, 2, -12, "lantern", hanging=False, waterlogged=False)
    # drying racks with fish (dried kelp) and nets
    for i in range(3):
        x0 = 3 + i * 4
        for z in (3, 8):
            b.fill(x0, 1, z, x0, 3, z, "spruce_fence", **FENCE)
        for z in range(3, 9):
            b.set(x0, 4, z, "spruce_log", axis="z")
            if 3 < z < 8:
                b.set(x0, 3, z, "dried_kelp_block")
                if h(x0, z, salt) < 0.5:
                    b.set(x0, 2, z, "dried_kelp_block")
    hide_frame(b, 15, 1, 6, "x", "white")
    chopping_block(b, 10, 1, 25)
    crates(b, 18, 1, 24, 3, salt, loot=f"{NS}:chests/fishing")
    water_barrel(b, 1, 1, 24)
    animals(b, "cat", [(9, 1, 11)])
    b.villager(6, 2, 16, "fisherman")
    b.villager(14, 2, 18, "fisherman")
    b.villager(24, 1, 4)
    weather(b, salt)
    return b


# ---------------------------------------------------------------------------
# Thing site: the open-air assembly with a law rock, stone seats and booths
# ---------------------------------------------------------------------------
def thing_site(salt):
    b = Build(f"thing_site_{salt}")
    N = 37
    c = N // 2
    for x in range(N):
        for z in range(N):
            r = math.hypot(x - c, z - c)
            if r <= c:
                b.set(x, 0, z, "grass_block", snowy=False)
                b.air(x, 1, z, x, 4, z)
    # law rock: stepped stone mound with a carved post and banner
    for k, rr in enumerate((4, 3, 2)):
        for x in range(c - rr, c + rr + 1):
            for z in range(c - rr, c + rr + 1):
                if math.hypot(x - c, z - c) <= rr + 0.3:
                    b.set(x, 1 + k, z, "mossy_cobblestone" if h(x, z, k) < 0.4 else "stone")
    b.fill(c, 4, c, c, 7, c, f"{NS}:carved_post", axis="y")
    b.banner(c, 7, c - 1, "north", "red")
    stair(b, c, 1, c - 5, "stone_stairs", "south")
    stair(b, c, 2, c - 4, "stone_stairs", "south")
    stair(b, c, 3, c - 3, "stone_stairs", "south")
    # rings of stone seats facing the rock
    for radius in (8, 11, 14):
        n = int(radius * 2 * math.pi / 2.2)
        for i in range(n):
            a = i * 2 * math.pi / n
            if abs(math.sin(a)) < 0.25 and math.cos(a) < 0:   # leave an aisle on one side
                continue
            x, z = int(round(c + radius * math.cos(a))), int(round(c + radius * math.sin(a)))
            dx, dz = c - x, c - z
            facing = ("east" if dx < 0 else "west") if abs(dx) > abs(dz) else ("south" if dz < 0 else "north")
            stair(b, x, 1, z, "stone_brick_stairs" if radius < 14 else "cobblestone_stairs", facing)
    # booths (temporary turf-walled tents) around the edge
    for i, a in enumerate((0.5, 1.6, 2.7, 3.9, 5.0)):
        bx, bz = int(round(c + 16 * math.cos(a))), int(round(c + 16 * math.sin(a)))
        col = ("red", "blue", "yellow", "white", "green")[i]
        door = (bx + (1 if bx < c else -1), bz) if abs(bx - c) > abs(bz - c) else (bx, bz + (1 if bz < c else -1))
        for x in range(bx - 1, bx + 2):
            for z in range(bz - 1, bz + 2):
                for y in (1, 2):
                    edge = (x, z) != (bx, bz)
                    b.set(x, y, z, f"{col}_wool" if edge and (x, z) != door else "air")
                b.set(x, 3, z, f"{col}_wool" if (x + z) % 2 else "white_wool")
        b.fill(bx, 4, bz, bx, 4, bz, "spruce_fence", **FENCE)
        b.set(bx, 1, bz, "barrel", nbt={"id": "minecraft:barrel"}, facing="up", open=False)
    # fire pits and banner poles
    for (x, z) in ((c - 9, c + 9), (c + 9, c - 9)):
        b.set(x, 1, z, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
    for (x, z, col) in ((c - 12, c - 12, "red"), (c + 12, c + 12, "blue"), (c + 12, c - 12, "yellow")):
        b.fill(x, 1, z, x, 5, z, "stripped_spruce_log", axis="y")
        b.banner(x, 5, z - 1, "north", col)
    runestone_at(b, c - 3, 1, c + 15, "x", salt)
    for i, (x, z) in enumerate(((c - 5, c + 6), (c + 6, c + 4), (c + 2, c - 9), (c - 8, c - 2))):
        b.villager(x, 1, z, ("librarian", "cleric", "none", "none")[i])
    return b


# ---------------------------------------------------------------------------
# Shieling and beacon cairn
# ---------------------------------------------------------------------------
def shieling(salt):
    b = Build(f"shieling_{salt}")
    # stone and turf hut
    for x in range(7):
        for z in range(1, 8):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "packed_mud")
            edge = x in (0, 6) or z in (1, 7)
            for y in range(2, 4):
                r = h(x, y, z, salt)
                b.set(x, y, z, ("mossy_cobblestone" if r < 0.5 else "cobblestone") if edge else "air")
    gable_roof(b, 3, lambda z: 3, 1, 7, 4, "turf", overhang=1, salt=salt)
    gable_end(b, 3, lambda z: 3, 1, 4, 4, lambda x, y, z: ("cobblestone", {}))
    gable_end(b, 3, lambda z: 3, 7, 4, 4, lambda x, y, z: ("cobblestone", {}))
    b.door(3, 2, 1, "north")
    b.bed(1, 2, 5, "south", "brown")
    b.set(5, 2, 6, "cauldron")
    b.set(5, 2, 2, "composter", level=2)
    b.set(1, 1, 3, "campfire", lit=False, signal_fire=False, facing="north", waterlogged=False)
    hanging_lantern(b, 3, 5, 4, length=1)
    # dry-stone sheep fold
    for x in range(8, 19):
        for z in range(0, 11):
            b.set(x, 0, z, "grass_block", snowy=False)
            if x in (8, 18) or z in (0, 10):
                if not (z == 0 and x == 13):
                    b.set(x, 1, z, "mossy_cobblestone_wall" if h(x, z) < 0.5 else "cobblestone_wall",
                          up=True, north="none", south="none", east="none", west="none", waterlogged=False)
            else:
                b.set(x, 1, z, "air")
    b.set(13, 1, 0, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)
    b.set(10, 1, 8, "hay_block", axis="y")
    animals(b, "sheep", [(11, 1, 3), (14, 1, 5), (16, 1, 7)], Color=Byte(0))
    animals(b, "goat", [(12, 1, 7)])
    b.villager(3, 2, 4, "shepherd")
    weather(b, salt)
    return b


def beacon_cairn(salt):
    b = Build(f"beacon_cairn_{salt}")
    for k, r in enumerate((3, 3, 2, 2, 1)):
        for x in range(4 - r, 5 + r):
            for z in range(4 - r, 5 + r):
                if math.hypot(x - 4, z - 4) <= r + 0.4:
                    b.set(x, k, z, "mossy_cobblestone" if h(x, k, z, salt) < 0.4 else
                          ("cobblestone" if h(z, x, k) < 0.6 else "stone"))
    b.set(4, 5, 4, "campfire", lit=True, signal_fire=True, facing="north", waterlogged=False)
    b.set(4, 4, 4, "hay_block", axis="y")
    for (x, z) in ((3, 4), (5, 4), (4, 3), (4, 5)):
        slab(b, x, 5, z, "cobblestone_slab")
    woodpile(b, 8, 0, 2, 3, axis="z")
    return b


# ---------------------------------------------------------------------------
# Ships: knarr (cargo), shipwreck, frozen longship
# ---------------------------------------------------------------------------
def knarr():
    b = Build("knarr")
    L, C = 23, 4

    def beam(z):
        t = z / (L - 1)
        return 4.2 * math.sin(math.pi * t) ** 0.45

    for z in range(L):
        bm = beam(z)
        for y in range(0, 6):
            half = bm * (0.3 + 0.7 * min(1.0, y / 3.0))
            hw = int(round(half))
            if y == 0:
                if 1 <= z <= L - 2:
                    b.set(C, 0, z, "spruce_log", axis="z")
                continue
            if hw < 1 and not (2 <= z <= L - 3):
                b.set(C, y, z, "spruce_planks")
                continue
            for x in range(C - hw, C + hw + 1):
                if abs(x - C) == hw:
                    b.set(x, y, z, "oak_planks" if y < 5 else "dark_oak_planks")
                elif y <= 2:
                    b.set(x, y, z, "spruce_planks")
                else:
                    b.set(x, y, z, "air")
    for dz, y in ((0, 5), (0, 6), (-1, 7), (0, 8)):
        b.set(C, y, 0 + dz, "dark_oak_planks")
        b.set(C, y, L - 1 - dz, "dark_oak_planks")
    zm = L // 2
    b.fill(C, 3, zm, C, 15, zm, "stripped_spruce_log", axis="y")
    b.fill(C - 5, 15, zm, C + 5, 15, zm, "spruce_fence", **FENCE)
    for x in range(C - 5, C + 6):
        for y in range(7, 15):
            b.set(x, y, zm, "blue_wool" if (y // 2) % 2 else "white_wool")
    # cargo hold amidships, decks fore and aft
    for z in range(zm - 4, zm + 5):
        if z == zm:
            continue
        for x in range(C - 2, C + 3):
            if h(x, z) < 0.55:
                b.barrel(x, 3, z, loot=f"{NS}:chests/ship_cargo" if h(z, x) < 0.25 else None)
            elif h(x, z, 3) < 0.5:
                b.set(x, 3, z, "hay_block", axis="z")
    for (x, y, z), v in list(b.blocks.items()):           # seal the hull below the waterline
        if v[0] == "minecraft:air" and y <= 3:
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
                if b.get(x + dx, y + dy, z + dz) is None:
                    b.set(x + dx, y + dy, z + dz, "oak_planks")
    b.chest(C, 3, L - 4, "north", f"{NS}:chests/longship")
    animals(b, "sheep", [(C - 1, 3, 4), (C + 1, 3, 5)], Color=Byte(0))
    b.set(C, 4, L - 3, "lantern", hanging=False, waterlogged=False)
    for z in range(4, L - 3, 3):
        for x in (C - int(round(beam(z))) - 1, C + int(round(beam(z))) + 1):
            if 5 <= z <= L - 6:
                b.banner(x, 5, z, "west" if x < C else "east", ("white", "blue")[z % 2])
    return b


def shipwreck(salt):
    """A broken longship on the sea floor: no air (keeps the water), planks missing, mast down."""
    ship, _ = longship()
    b = Build(f"shipwreck_{salt}")
    for (x, y, z), (name, props, nbt) in ship.blocks.items():
        if name == "minecraft:air" or "wool" in name and h(x, y, z, salt) < 0.7 or "banner" in name:
            continue
        if y > 4 and "stripped_spruce_log" in name:
            continue    # mast snapped
        if h(x, y, z, salt) < 0.22 and y >= 1:
            continue    # holes in the hull
        sink = 1 if z > 18 else 0     # stern settled deeper
        p = dict(props)
        if "waterlogged" in p:
            p["waterlogged"] = "true"
        b.blocks[(x, y - sink, z)] = (name, tuple(sorted(p.items())), nbt)
    # fallen mast lying across the hull
    for x in range(-3, 10):
        b.set(x, 3, 12, "stripped_spruce_log", axis="x")
    for x in range(0, 9):
        if h(x, salt) < 0.5:
            b.set(x, 2, 13, "red_wool")
    for (x, y, z), v in list(b.blocks.items()):
        if v[0] == "minecraft:chest":
            b.blocks[(x, y, z)] = ("minecraft:chest", (("facing", "north"), ("type", "single"),
                                                       ("waterlogged", "true")),
                                   {"id": "minecraft:chest", "LootTable": f"{NS}:chests/longship"})
        if v[0] == "minecraft:lantern":
            del b.blocks[(x, y, z)]
    b.set(4, 1, 6, "chest", nbt={"id": "minecraft:chest", "LootTable": f"{NS}:chests/shipwreck"}, facing="east",
          type="single", waterlogged=True)
    return b


def frozen_longship(salt):
    ship, _ = longship()
    b = Build(f"frozen_longship_{salt}")
    compose(b, ship, 6, 0, 3)
    (x0, y0, z0), (x1, y1, z1) = b.bounds()
    # encase the stern two-thirds in glacier ice; the dragon prow breaks free
    for x in range(x0 - 4, x1 + 5):
        for z in range(z0 + 6, z1 + 6):
            edge = min(x - (x0 - 4), (x1 + 4) - x, z - (z0 + 6), (z1 + 5) - z)
            top = min(8 + int(3 * h(x, z, salt)) - (2 if z < z0 + 10 else 0), 1 + int(1.6 * edge + 2 * h(z, x, salt)))
            for y in range(-3, top):
                if b.get(x, y, z) is None or b.get(x, y, z) == "minecraft:air":
                    r = h(x, y, z, salt, 5)
                    b.set(x, y, z, "packed_ice" if r < 0.6 else ("blue_ice" if r < 0.85 else "ice"))
            b.set(x, top, z, "snow_block") if h(z, x) < 0.5 else None
    # a cave dug in to the frozen deck, where the treasure still lies
    for z in range(z0 + 5, z0 + 20):
        for x in range(x0 + 3, x0 + 6):
            for y in range(4, 7):
                if b.get(x, y, z) in ("minecraft:packed_ice", "minecraft:blue_ice", "minecraft:ice"):
                    b.set(x, y, z, "air")
    b.chest(x0 + 4, 4, z0 + 18, "north", f"{NS}:chests/ship_burial")
    draugr(b, x0 + 4, 4, z0 + 14, "stray", "chain")
    draugr(b, x0 + 4, 4, z0 + 11, "stray", "iron")
    return b


def catalogue2():
    from .viking import hall
    from .dress import dress_exterior
    great = dress_exterior(hall("great_hall_mh", 43, 7, 5, "shingle", "stave", wall_h=4, great=True, salt=11,
                                villagers=4), "core", 11)
    return {
        "dungeon/burial_mound": burial_mound(0),
        "dungeon/burial_mound_b": burial_mound(3),
        "dungeon/ship_burial": ship_burial(0),
        "site/stave_church": stave_church(0),
        "site/mead_hall": mead_hall(great, 0),
        "site/fishing_hamlet": fishing_hamlet(0),
        "site/thing_site": thing_site(0),
        "site/shieling": shieling(0),
        "site/beacon_cairn": beacon_cairn(0),
        "sea/knarr": knarr(),
        "sea/shipwreck": shipwreck(0),
        "sea/frozen_longship": frozen_longship(0),
    }
