"""
Detailed Viking buildings for walled villages and homesteads.

Inspired by excavated and reconstructed Viking-age sites: the Borg chieftain's hall
(Lofoten), Trelleborg longhouses (bowed walls, outer posts), Hedeby houses (wattle and
daub), Stöng and Glaumbær (Icelandic turf farms), stave-built temples and raised
Norwegian stabbur storehouses.

Conventions (see kit.py): door faces north (-z), origin at min corner, y=0 foundation.
"""
from .builder import Build
from .kit import (FENCE, NS, armor_stand, bench, bowed, candle, crates, crossed_horns, foundation, fur, gable_end,
                  gable_roof, h, hanging_lantern, long_table, plank_gable, shield, slab, stair, table, timber,
                  turf_wall, woodpile)
from .nbtio import Byte


# ---------------------------------------------------------------------------
# Longhouses and the great hall
# ---------------------------------------------------------------------------
def hall(name, length, half_mid, half_end, roof, walls, wall_h=3, byre=False, loft=False, chamber=True,
         great=False, salt=0, villagers=2):
    b = Build(name)
    Z0, Z1 = 2, length + 1
    cx = half_mid + 3
    hw = bowed(half_mid, half_end, Z0, Z1)
    wall_top = 1 + wall_h
    roof_y = wall_top + 1

    wall_fn = {
        "timber": timber(3, "wattle", salt),
        "plank": timber(4, "planks", salt),
        "stave": lambda x, y, z: (("cobblestone", {}) if y == 1 else ("stripped_spruce_log", {"axis": "y"})
                                  if (x + z) % 2 else ("spruce_log", {"axis": "y"})),
        "turf": turf_wall(salt),
    }[walls]

    # foundation, floor, interior air
    for z in range(Z0, Z1 + 1):
        w = hw(z)
        for x in range(cx - w, cx + w + 1):
            b.set(x, 0, z, "mossy_cobblestone" if h(x, z, salt) < 0.3 else "cobblestone")
            b.set(x, 1, z, f"{NS}:pine_planks" if (x + salt) % 5 else "spruce_planks")
        if Z0 < z < Z1:
            b.air(cx - w + 1, 2, z, cx + w - 1, roof_y + w + 2, z)

    # long walls
    for z in range(Z0, Z1 + 1):
        w = hw(z)
        for x in (cx - w, cx + w):
            for y in range(1, wall_top + 1):
                b.set(x, y, z, *wall_fn(x, y, z))
            if walls == "turf":   # turf walls are thick: an outer sod layer
                ox = x - 1 if x < cx else x + 1
                for y in range(1, wall_top):
                    b.set(ox, y, z, *wall_fn(ox, y, z))
                b.set(ox, wall_top, z, "grass_block", snowy=False)

    ridge = gable_roof(b, cx, hw, Z0, Z1, roof_y, roof, overhang=1 if walls != "turf" else 2, salt=salt)
    for z in (Z0, Z1):
        gable_end(b, cx, hw, z, roof_y, 2, plank_gable)
    # carved horns on both ridge ends
    oh = 1 if walls != "turf" else 2
    for z in (Z0 - oh, Z1 + oh):
        if z in ridge:
            crossed_horns(b, cx, ridge[z] + 1, z, "out")

    # doors: front gable, both long walls in the middle
    zm = (Z0 + Z1) // 2
    if great:
        b.door(cx - 1, 2, Z0, "north", hinge="left")
        b.door(cx + 1, 2, Z0, "north", hinge="right")
        b.set(cx, 2, Z0, f"{NS}:carved_post", axis="y")
        b.set(cx, 3, Z0, f"{NS}:carved_post", axis="y")
        b.air(cx - 1, 2, Z0 - 1, cx + 1, 3, Z0 - 1)
    else:
        b.door(cx, 2, Z0, "north")
    for side in (-1, 1):
        x = cx + side * hw(zm)
        b.door(x, 2, zm, "west" if side < 0 else "east")
        if walls == "turf":
            b.air(x + side, 2, zm, x + side, 3, zm)
    # doorstep and flanking carved posts at the front (turf halls; timber halls get a porch below)
    if walls == "turf":
        for x in (cx - 2, cx + 2):
            b.set(x, 2, Z0 - 1, f"{NS}:carved_post", axis="y")
            b.set(x, 3, Z0 - 1, "lantern", hanging=False, waterlogged=False)
        slab(b, cx, 1, Z0 - 1, "cobblestone_slab")

    # covered entrance porch on timber halls: two posts, a little gabled roof, steps and banners
    if walls != "turf":
        pz = Z0 - 3
        for x in (cx - 2, cx + 2):
            b.fill(x, 1, pz, x, 3, pz, f"{NS}:carved_post", axis="y")
            b.set(x, 1, Z0 - 2, "spruce_fence", **FENCE)
        for z in (pz, Z0 - 2):
            stair(b, cx - 3, 4, z, "spruce_stairs", "east")
            stair(b, cx + 3, 4, z, "spruce_stairs", "west")
            b.set(cx - 2, 4, z, "spruce_planks")
            b.set(cx + 2, 4, z, "spruce_planks")
            stair(b, cx - 2, 5, z, "dark_oak_stairs", "east")
            stair(b, cx + 2, 5, z, "dark_oak_stairs", "west")
            stair(b, cx - 1, 5, z, "dark_oak_stairs", "east") if half_mid < 5 else b.set(cx - 1, 5, z, "dark_oak_planks")
            stair(b, cx + 1, 5, z, "dark_oak_stairs", "west") if half_mid < 5 else b.set(cx + 1, 5, z, "dark_oak_planks")
            slab(b, cx, 6, z, "dark_oak_slab")
            b.air(cx - 1, 2, z, cx + 1, 4, z)
        crossed_horns(b, cx, 7, pz, "out")
        for z in range(pz, Z0):
            for x in range(cx - 1, cx + 2):
                b.set(x, 0, z, "cobblestone")
                slab(b, x, 1, z, "spruce_slab", "bottom") if z > pz else stair(b, x, 1, z, "cobblestone_stairs", "south")
        b.banner(cx - 2, 3, pz - 1, "north", "red" if salt % 2 else "blue")
        b.banner(cx + 2, 3, pz - 1, "north", "red" if salt % 2 else "blue")
        hanging_lantern(b, cx, 4, Z0 - 2, length=1)

    # painted shields hung outside along the long walls, under the eaves
    if walls != "turf":
        for z in range(Z0 + 1, Z1, 3):
            for side in (-1, 1):
                x = cx + side * (hw(z) + 1)
                if b.get(x, wall_top, z) is None and b.get(x - side, wall_top, z) not in (None, "minecraft:air"):
                    shield(b, x, wall_top, z, "west" if side < 0 else "east", salt + z)

    # a smoke vent on the ridge above the hearth: a lit campfire sends a plume up over the roof
    vz = (Z0 + Z1) // 2 + 2
    if vz in ridge:
        b.set(cx, ridge[vz] + 1, vz, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
        for dx in (-1, 1):
            slab(b, cx + dx, ridge[vz] + 1, vz, "cobblestone_slab")

    # outer posts under the eaves (Trelleborg-style), every 4 blocks
    if walls in ("timber", "plank", "stave"):
        for z in range(Z0 + 2, Z1 - 1, 4):
            for side in (-1, 1):
                x = cx + side * (hw(z) + 1)
                for y in range(1, roof_y):
                    if b.get(x, y, z) is None:
                        b.set(x, y, z, "stripped_spruce_log" if y < roof_y - 1 else "spruce_fence",
                              **({"axis": "y"} if y < roof_y - 1 else FENCE))

    # aisle posts and tie beams
    post_dx = max(2, half_mid - 2)
    for z in range(Z0 + 3, Z1 - 1, 4):
        w = hw(z) + oh
        tops = []
        for x in (cx - post_dx, cx + post_dx):
            k = (x - (cx - w) - 1) if x < cx else ((cx + w) - x - 1)
            top = roof_y + k - 1
            tops.append(top)
            b.fill(x, 2, z, x, top, z, "stripped_spruce_log", axis="y")
        for x in range(cx - hw(z) + 1, cx + hw(z)):
            if b.get(x, roof_y, z) in (None, "minecraft:air"):
                b.set(x, roof_y, z, "stripped_spruce_log", axis="x")

    # long hearth down the middle
    hz0, hz1 = Z0 + 5 + (5 if byre else 0), Z1 - (7 if chamber else 4)
    for z in range(hz0, hz1 + 1):
        for x in (cx - 1, cx, cx + 1):
            b.set(x, 1, z, "packed_mud" if x != cx else "cobblestone")
    for z in range(hz0 + 1, hz1, 5):
        b.set(cx, 1, z, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
        b.set(cx - 1, 2, z, "cauldron") if (z // 5) % 2 == 0 else b.set(cx + 1, 2, z, "cauldron")

    # sleeping and sitting platforms with furs along the walls
    for z in range(Z0 + 2, Z1 - (6 if chamber else 1)):
        if z == zm or (byre and z < Z0 + 8):
            continue
        for side in (-1, 1):
            x = cx + side * (hw(z) - 1)
            if b.get(x, 2, z) == "minecraft:air":
                slab(b, x, 2, z, "spruce_slab")
                if h(x, z, salt, 2) < 0.45:
                    fur(b, x, 3, z, salt)
            # shields on the walls above the platforms
            if z % 2 == 0 and b.get(x + side, wall_top, z) not in (None, "minecraft:air"):
                shield(b, x, wall_top, z, "east" if side < 0 else "west", salt)

    # feasting tables in big halls
    if half_mid >= 6:
        for side in (-1, 1):
            x = cx + side * 3
            long_table(b, x, 2, hz0 + 1, hz1 - 1)
            for z in range(hz0 + 1, hz1):
                if z % 2:
                    bench(b, x + side, 2, z, "west" if side < 0 else "east")
                if z % 4 == 1:
                    candle(b, x, 3, z)

    # high seat for the chieftain
    if great:
        x = cx - (hw(zm + 3) - 1)
        b.air(x, 2, zm + 2, x, 3, zm + 4)
        stair(b, x, 2, zm + 3, "dark_oak_stairs", "west")
        for z in (zm + 2, zm + 4):
            b.fill(x, 2, z, x, wall_top, z, f"{NS}:carved_post", axis="y")
        b.banner(x, wall_top, zm + 3, "east", "red")
        b.set(x + 1, 2, zm + 6, "lectern", facing="west", has_book=False, powered=False)

    # byre at the front end: stalls with cattle
    if byre:
        for z in range(Z0 + 1, Z0 + 8):
            for side in (-1, 1):
                x = cx + side * (hw(z) - 3)
                if z in (Z0 + 3, Z0 + 6):
                    for xx in range(min(x, cx + side * (hw(z) - 1)), max(x, cx + side * (hw(z) - 1)) + 1):
                        b.set(xx, 2, z, "spruce_fence", **FENCE)
            b.set(cx - 1, 1, z, "coarse_dirt")
            b.set(cx + 1, 1, z, "coarse_dirt")
        b.set(cx - hw(Z0 + 7) + 1, 2, Z0 + 7, "hay_block", axis="y")
        b.set(cx + hw(Z0 + 7) - 1, 2, Z0 + 7, "hay_block", axis="x")
        for x, z in ((cx - 2, Z0 + 2), (cx + 2, Z0 + 5)):
            b.animal(x, 2, z, "cow")
        b.set(cx + hw(Z0 + 1) - 1, 2, Z0 + 1, "composter", level=4)

    # loft over the front end
    if loft:
        for z in range(Z0 + 1, Z0 + 5):
            for x in range(cx - hw(z) + 1, cx + hw(z)):
                if b.get(x, wall_top + 1, z) in (None, "minecraft:air"):
                    b.set(x, wall_top + 1, z, "spruce_planks")
        b.set(cx - 1, wall_top + 2, Z0 + 2, "hay_block", axis="y")
        b.barrel(cx + 1, wall_top + 2, Z0 + 2)
        for y in range(2, wall_top + 2):
            b.set(cx - 2, y, Z0 + 4, "stripped_spruce_log", axis="y")
            b.set(cx - 2, y, Z0 + 5, "ladder", facing="south", waterlogged=False)

    # private chamber at the far end
    if chamber:
        zp = Z1 - 6
        w = hw(zp)
        wr = w + oh
        for x in range(cx - w + 1, cx + w):
            d = min(x - (cx - wr), (cx + wr) - x)      # roof underside is at roof_y + d - 1
            for y in range(2, roof_y + d - 1):
                if b.get(x, y, zp) == "minecraft:air":
                    b.set(x, y, zp, "spruce_planks" if (x + y) % 3 else "stripped_spruce_log",
                          **({} if (x + y) % 3 else {"axis": "y"}))
        b.door(cx, 2, zp, "south")
        bx = [cx - w + 2, cx + w - 3]
        for x in bx:
            b.bed(x, 2, Z1 - 2, "south", "red" if x < cx else "blue")
            fur(b, x + (1 if x < cx else -1), 2, Z1 - 2, salt)
        b.chest(cx, 2, Z1 - 1, "north", f"{NS}:chests/{'great_hall' if great else 'longhouse'}")
        b.barrel(cx - 1, 2, Z1 - 1)
        b.barrel(cx + 1, 2, Z1 - 1)
        hanging_lantern(b, cx, ridge[Z1 - 3] - 2, Z1 - 3)
        if great:
            armor_stand(b, cx + w - 2, 2, Z1 - 4, 270, hand="iron_axe", head="iron_helmet",
                        chest="chainmail_chestplate", offhand="shield")

    # storage near the front, workstations
    zf = Z0 + 1 if not byre else Z0 + 8
    w = hw(zf)
    crates(b, cx - w + 1, 2, zf, 2, salt, loot=f"{NS}:chests/storehouse")
    b.set(cx + w - 1, 2, zf, "smoker", facing="west", lit=False)
    b.set(cx + w - 2, 2, zf, "crafting_table")
    if half_mid >= 5:
        b.set(cx - w + 1, 2, zf + 2, "loom", facing="east")

    # lanterns under the ridge
    for z in range(Z0 + 3, Z1 - 1, 5):
        if z in ridge:
            hanging_lantern(b, cx, ridge[z] - 2, z, length=max(1, min(3, ridge[z] - roof_y - 2)))

    # outside: woodpile, barrels, hay
    side_x = cx + hw(zm) + (3 if walls == "turf" else 2)
    woodpile(b, side_x, 1, Z0 + 3, 4, axis="z")
    b.barrel(cx - hw(Z0 + 1) - 2, 1, Z0 + 1)
    b.set(cx + hw(Z1 - 2) + 2, 1, Z1 - 2, "hay_block", axis="y")

    profs = ["butcher", "none", "shepherd", "librarian", "none"]
    for i in range(villagers):
        b.villager(cx + (1 if i % 2 else -1) * 2, 2, Z0 + 4 + i * 3 + (8 if byre else 0), profs[i % len(profs)])
    return b


# ---------------------------------------------------------------------------
# Icelandic turf buildings
# ---------------------------------------------------------------------------
def turf_unit(b, x0, width, depth, z0, salt, purpose, front="timber"):
    """One gabled turf house cell: thick sod side/back walls, grass roof, timber gable front."""
    cx = x0 + width // 2
    w_in = width // 2 - 2     # interior half-width (walls 2 thick)
    z1 = z0 + depth - 1
    sod = turf_wall(salt)
    for x in range(x0, x0 + width):
        for z in range(z0, z1 + 1):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "packed_mud" if purpose in ("byre", "kitchen") else f"{NS}:pine_planks")
    b.air(cx - w_in, 2, z0 + 1, cx + w_in, 2 + w_in + 2, z1 - 2)
    for y in range(1, 4):
        for z in range(z0, z1 + 1):
            for x in (x0, x0 + 1, x0 + width - 2, x0 + width - 1):
                b.set(x, y, z, *sod(x, y, z))
        for x in range(x0 + 2, x0 + width - 2):
            for z in (z1 - 1, z1):
                b.set(x, y, z, *sod(x, y, z))
    half = width // 2
    gable_roof(b, cx, lambda z: half, z0, z1, 4, "turf", overhang=0, salt=salt)
    # timber gable front, set back one block under the roof
    for y in range(2, 4 + half):
        span = half - 2 if y < 4 else half - 2 - (y - 4)
        for x in range(cx - span, cx + span + 1):
            if b.get(x, y, z0) == "minecraft:grass_block":
                continue
            post = abs(x - cx) == span
            if front == "black":
                b.set(x, y, z0, "dark_oak_planks" if not post else "dark_oak_log", **({"axis": "y"} if post else {}))
            else:
                b.set(x, y, z0, "stripped_spruce_log" if post else "spruce_planks", **({"axis": "y"} if post else {}))
    b.door(cx, 2, z0, "north")
    if half >= 4:
        b.set(cx - 1, 4, z0, "glass_pane", **FENCE)
        b.set(cx + 1, 4, z0, "glass_pane", **FENCE)
    hanging_lantern(b, cx, 4 + half - 2, (z0 + z1) // 2, length=max(1, half - 2))
    zi = z1 - 2
    if purpose == "dwelling":
        for x in (cx - w_in, cx + w_in):
            b.bed(x, 2, zi - 1, "south", "brown" if x < cx else "green")
        b.chest(cx, 2, zi, "north", f"{NS}:chests/turf_house")
        fur(b, cx, 2, zi - 2, salt)
    elif purpose == "kitchen":
        b.set(cx - w_in, 2, zi, "smoker", facing="east", lit=False)
        b.set(cx, 2, zi, "furnace", facing="north", lit=False)
        b.set(cx + w_in, 2, zi, "cauldron")
        b.barrel(cx - w_in, 2, zi - 2, loot=f"{NS}:chests/storehouse")
        b.set(cx, 1, (z0 + z1) // 2, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
    elif purpose == "store":
        crates(b, cx - w_in, 2, zi - 1, 4, salt, loot=f"{NS}:chests/storehouse")
        b.set(cx + w_in, 2, zi, "hay_block", axis="y")
        b.set(cx + w_in, 3, zi, "hay_block", axis="x")
    elif purpose == "workshop":
        b.set(cx - w_in, 2, zi, "fletching_table")
        b.set(cx + w_in, 2, zi, "loom", facing="west")
        b.set(cx, 2, zi, "crafting_table")
    elif purpose == "byre":
        for x in range(cx - w_in, cx + w_in + 1):
            b.set(x, 2, zi - 2, "spruce_fence", **FENCE)
        b.set(cx, 2, zi - 2, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)
        b.set(cx - w_in, 2, zi, "hay_block", axis="y")
        b.animal(cx, 2, zi, "cow")
    return z1


def farmstead(salt):
    """Glaumbær-style row of connected turf houses with gables side by side."""
    plans = [("dwelling", 9, 13), ("kitchen", 7, 12), ("store", 7, 11), ("workshop", 9, 12), ("byre", 7, 13)]
    order = plans[salt % 2:] + plans[:salt % 2]
    b = Build(f"farmstead_{salt}")
    x = 0
    units = []
    for purpose, width, depth in order[:4 + salt % 2]:
        z1 = turf_unit(b, x, width, depth, 1, salt + x, purpose, front="black" if (x // 7) % 2 else "timber")
        units.append((x, width, z1))
        x += width - 2     # neighbours share a wall
    # back passage linking the houses through the shared walls
    for x0, width, z1 in units[1:]:
        for xx in (x0, x0 + 1):
            b.air(xx, 2, 6, xx, 3, 6)
    # yard: drying rack, woodpile, barrels
    end = x + 2
    woodpile(b, 1, 1, -2, 5)
    b.barrel(end - 2, 1, -1)
    b.barrel(end - 3, 1, -1)
    b.villager(units[0][0] + 4, 2, 4, "none")
    b.villager(units[-1][0] + 3, 2, 4, "farmer")
    b.villager(units[len(units) // 2][0] + 3, 2, 4, "fletcher")
    return b


def turf_cottage(salt):
    b = Build(f"turf_cottage_{salt}")
    z1 = turf_unit(b, 0, 9, 12, 1, salt, "dwelling")
    # small byre leaning on the side
    turf_unit(b, 7, 7, 10, 3, salt + 3, "byre")
    b.air(7, 2, 6, 8, 3, 6)
    woodpile(b, 0, 1, -1, 4)
    b.villager(4, 2, 4)
    return b


# ---------------------------------------------------------------------------
# Craft buildings
# ---------------------------------------------------------------------------
def pit_house(salt):
    """Grubenhaus weaving hut: sunken floor, thatch A-frame reaching the ground."""
    b = Build(f"pit_house_{salt}")
    X1, Z0, Z1 = 8, 1, 10
    for x in range(X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 0, z, "packed_mud" if 1 <= x <= X1 - 1 and Z0 < z < Z1 else "coarse_dirt")
    b.air(1, 1, Z0 + 1, X1 - 1, 5, Z1 - 1)
    gable_roof(b, X1 // 2, lambda z: X1 // 2, Z0, Z1, 1, "thatch", overhang=0, salt=salt)
    for z in (Z0, Z1):
        gable_end(b, X1 // 2, lambda zz: X1 // 2, z, 1, 1,
                  lambda x, y, zz: ((f"{NS}:wattle_daub", {}) if (x + y) % 4 else ("stripped_spruce_log", {"axis": "y"})))
    b.door(X1 // 2, 1, Z0, "north")
    for x in (2, 6):  # warp-weighted loom against the back wall
        b.fill(x, 1, Z1 - 1, x, 3, Z1 - 1, "spruce_fence", **FENCE)
    for x in range(3, 6):
        b.set(x, 2, Z1 - 1, "white_wool")
        b.set(x, 3, Z1 - 1, "white_wool" if x != 4 else "red_wool")
        b.set(x, 1, Z1 - 1, "cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
              waterlogged=False)
    b.set(2, 1, 3, "loom", facing="east")
    b.set(6, 1, 3, "barrel", nbt={"id": "minecraft:barrel"}, facing="up", open=False)
    b.set(6, 1, 4, "white_wool")
    b.set(6, 2, 4, "brown_wool")
    b.set(2, 1, 6, "white_carpet")
    hanging_lantern(b, 4, 3, 5, length=0)
    b.villager(4, 1, 5, "shepherd")
    return b


def forge(salt):
    b = Build(f"forge_{salt}")
    X1, Z0, Z1 = 12, 1, 12
    foundation(b, 0, X1, Z0, Z1, salt)
    for x in range(X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 1, z, "stone_bricks" if h(x, z, salt) < 0.5 else ("cobblestone" if h(z, x) < 0.6 else "gravel"))
    b.air(0, 2, Z0, X1, 9, Z1 - 1)
    # back workshop room (turf walled), walls reaching up to the sloping roof
    sod = turf_wall(salt)

    def roof_at(z):
        return 6 + max(0, (z - Z0) // 4)
    for x in range(X1 + 1):
        for z in (Z1, Z1 - 5):
            for y in range(1 if z == Z1 else 2, roof_at(z)):
                b.set(x, y, z, *sod(x, y, z))
    for z in range(Z1 - 5, Z1 + 1):
        for x in (0, X1):
            for y in range(1, roof_at(z)):
                b.set(x, y, z, *sod(x, y, z))
    # open forge hall: posts and a spruce shed roof sloping to the front
    for x in (0, 4, 8, X1):
        b.fill(x, 2, Z0, x, 5, Z0, "stripped_spruce_log", axis="y")
    for z in range(Z0 - 1, Z1 + 2):
        y = 6 + max(0, (z - Z0) // 4)
        for x in range(-1, X1 + 2):
            slab(b, x, y, z, "spruce_slab")
            if (z - Z0) % 4 == 3:
                b.set(x, y, z, "spruce_planks")
    # stone forge hearth with a chimney
    fx, fz = 8, Z1 - 7
    for x in range(fx - 1, fx + 2):
        for z in range(fz - 1, fz + 2):
            b.fill(x, 2, z, x, 3, z, "stone_bricks")
    b.set(fx, 3, fz, "lava_cauldron")
    b.set(fx, 2, fz - 1, "blast_furnace", facing="north", lit=False)
    b.fill(fx - 1, 4, fz - 1, fx + 1, 12, fz + 1, "cobblestone")
    b.air(fx, 4, fz, fx, 12, fz)
    b.set(fx, 4, fz, "campfire", lit=True, signal_fire=True, facing="north", waterlogged=False)
    b.set(fx - 2, 2, fz, "anvil", facing="east")
    b.set(fx + 2, 2, fz - 2, "water_cauldron", level=3)
    b.set(fx + 3, 2, fz - 2, "water_cauldron", level=3)
    b.set(3, 2, fz, "grindstone", face="floor", facing="east")
    b.set(2, 2, fz - 2, "smithing_table")
    b.chest(4, 2, Z1 - 1, "north", f"{NS}:chests/smithy")
    crates(b, 1, 2, Z1 - 4, 2, salt)
    # tool and weapon racks
    armor_stand(b, 1, 2, fz + 1, 90, hand="iron_axe", offhand="shield", head="iron_helmet")
    armor_stand(b, 5, 2, Z1 - 1, 180, hand="iron_sword", chest="chainmail_chestplate")
    woodpile(b, X1 - 3, 2, Z1 - 1, 3)
    b.set(X1 - 1, 2, Z0 + 1, "coal_block")
    b.set(X1 - 1, 3, Z0 + 1, "coal_block")
    b.door(6, 2, Z1 - 5, "north")
    for x, z in ((2, Z0 + 1), (10, Z1 - 3)):
        b.set(x, 5, z, "lantern", hanging=True, waterlogged=False)
    b.villager(6, 2, fz - 1, "armorer")
    b.villager(3, 2, Z0 + 2, "weaponsmith")
    b.villager(6, 2, Z1 - 2, "toolsmith")
    return b


def stabbur(large, salt):
    """Raised storehouse on stone legs; the large one has an overhanging gallery."""
    b = Build(f"stabbur_{'large' if large else 'small'}_{salt}")
    X1, Z0, Z1 = (8, 1, 8) if large else (6, 1, 6)
    legs = [(0, Z0), (X1, Z0), (0, Z1), (X1, Z1)] + ([(X1 // 2, Z0), (X1 // 2, Z1)] if large else [])
    for x, z in legs:
        b.set(x, 0, z, "cobblestone")
        b.set(x, 1, z, "cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
              waterlogged=False)
        slab(b, x, 2, z, "polished_andesite_slab")
    for x in range(X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 3, z, "spruce_planks")
    b.air(1, 4, Z0 + 1, X1 - 1, 9, Z1 - 1)
    top = 6
    for y in range(4, top + 1):
        for z in range(Z0, Z1 + 1):
            b.set(0, y, z, "spruce_log", axis="z")
            b.set(X1, y, z, "spruce_log", axis="z")
        for x in range(1, X1):
            b.set(x, y, Z0, "spruce_log", axis="x")
            b.set(x, y, Z1, "spruce_log", axis="x")
    base = top + 1
    if large:   # second storey overhanging by one, with a gallery rail below
        for x in range(-1, X1 + 2):
            for z in range(Z0 - 1, Z1 + 2):
                b.set(x, base, z, "spruce_planks")
        for x in range(-1, X1 + 2):
            for z in (Z0 - 1, Z1 + 1):
                b.set(x, base + 1, z, "spruce_log", axis="x")
                b.set(x, base + 2, z, "spruce_log", axis="x")
        for z in range(Z0, Z1 + 1):
            for x in (-1, X1 + 1):
                b.set(x, base + 1, z, "spruce_log", axis="z")
                b.set(x, base + 2, z, "spruce_log", axis="z")
        b.air(0, base + 1, Z0, X1, base + 4, Z1)
        roof_base, cx, half = base + 3, X1 // 2, X1 // 2 + 1
        for x in (0, X1):
            b.set(x, base + 1, Z0 - 1, f"{NS}:carved_post", axis="y")
        b.barrel(1, base + 1, Z0)
        b.set(X1 - 1, base + 1, Z0, "hay_block", axis="y")
        for y in range(4, base + 1):
            b.set(X1 - 1, y, Z1 - 1, "ladder", facing="north", waterlogged=False)
    else:
        roof_base, cx, half = base, X1 // 2, X1 // 2
    ridge = gable_roof(b, cx, lambda z: half, Z0 - (1 if large else 0), Z1 + (1 if large else 0), roof_base,
                       "shingle", overhang=1)
    for z in ((Z0 - 1, Z1 + 1) if large else (Z0, Z1)):
        gable_end(b, cx, lambda zz: half, z, roof_base, roof_base, plank_gable)
    for z in ((Z0 - 2, Z1 + 2) if large else (Z0 - 1, Z1 + 1)):
        crossed_horns(b, cx, ridge[z] + 1, z, "out")
    b.door(X1 // 2, 4, Z0, "north")
    stair(b, X1 // 2, 2, Z0 - 1, "spruce_stairs", "south")
    stair(b, X1 // 2, 1, Z0 - 2, "spruce_stairs", "south")
    b.set(1, 4, Z1 - 1, "cartography_table")
    b.chest(2, 4, Z1 - 1, "north", f"{NS}:chests/storehouse")
    crates(b, X1 - 2, 4, Z1 - 2, 2, salt, loot=f"{NS}:chests/storehouse")
    b.set(1, 4, Z0 + 1, "hay_block", axis="y")
    hanging_lantern(b, X1 // 2, 6, (Z0 + Z1) // 2, length=1)
    b.villager(X1 // 2, 4, (Z0 + Z1) // 2, "cartographer")
    return b


def byre(salt):
    b = Build(f"byre_{salt}")
    half, Z0, Z1 = 4, 1, 19
    cx = half + 2
    hw = lambda z: half  # noqa: E731
    wall = timber(4, "planks", salt)
    for z in range(Z0, Z1 + 1):
        for x in range(cx - half, cx + half + 1):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "coarse_dirt" if abs(x - cx) > 1 else "cobblestone")
        if Z0 < z < Z1:
            b.air(cx - half + 1, 2, z, cx + half - 1, 9, z)
        for x in (cx - half, cx + half):
            for y in range(1, 4):
                b.set(x, y, z, *wall(x, y, z))
    gable_roof(b, cx, hw, Z0, Z1, 4, "thatch", overhang=1, salt=salt)
    for z in (Z0, Z1):
        gable_end(b, cx, hw, z, 4, 2, plank_gable)
    b.air(cx - 1, 2, Z0, cx + 1, 4, Z0)
    for x in (cx - 1, cx + 1):
        b.set(x, 2, Z0, "spruce_fence_gate", facing="north", open=True, in_wall=False, powered=False)
    # stalls both sides
    for z in range(Z0 + 2, Z1 - 1):
        for side in (-1, 1):
            if (z - Z0) % 4 == 1:
                for x in range(cx + side * 2, cx + side * half, side):
                    b.set(x, 2, z, "spruce_fence", **FENCE)
            elif (z - Z0) % 4 == 3:
                b.set(cx + side * (half - 1), 2, z, "hay_block", axis="y")
    for i, z in enumerate(range(Z0 + 3, Z1 - 2, 4)):
        b.animal(cx + (2 if i % 2 else -2), 2, z, "cow" if i % 3 else "horse")
    b.set(cx - half + 1, 2, Z1 - 1, "water_cauldron", level=3)
    b.set(cx + half - 1, 2, Z1 - 1, "composter", level=5)
    for z in range(Z0 + 3, Z1, 6):
        hanging_lantern(b, cx, 6, z, length=1)
    b.villager(cx, 2, Z1 - 2, "farmer")
    return b


def granary(salt):
    b = Build(f"granary_{salt}")
    X1, Z0, Z1 = 6, 1, 7
    for x, z in ((0, Z0), (X1, Z0), (0, Z1), (X1, Z1), (0, 4), (X1, 4)):
        b.set(x, 0, z, "cobblestone")
        b.set(x, 1, z, "cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
              waterlogged=False)
        b.set(x, 2, z, "polished_andesite")
    for x in range(X1 + 1):
        for z in range(Z0, Z1 + 1):
            b.set(x, 3, z, "spruce_planks")
    b.air(1, 4, Z0 + 1, X1 - 1, 8, Z1 - 1)
    for y in range(4, 6):
        for z in range(Z0, Z1 + 1):
            for x in (0, X1):
                b.set(x, y, z, f"{NS}:wattle_daub" if z % 3 else "stripped_spruce_log",
                      **({} if z % 3 else {"axis": "y"}))
        for x in range(1, X1):
            for z in (Z0, Z1):
                b.set(x, y, z, f"{NS}:wattle_daub")
    cx = X1 // 2
    gable_roof(b, cx, lambda z: cx, Z0, Z1, 6, "thatch", overhang=1, salt=salt)
    for z in (Z0, Z1):
        gable_end(b, cx, lambda zz: cx, z, 6, 6, lambda x, y, zz: (f"{NS}:wattle_daub", {}))
    b.door(cx, 4, Z0, "north")
    stair(b, cx, 2, Z0 - 1, "spruce_stairs", "south")
    stair(b, cx, 1, Z0 - 2, "spruce_stairs", "south")
    for x in range(1, X1):
        for z in range(Z0 + 2, Z1):
            b.set(x, 4, z, "hay_block", axis="y")
            if h(x, z, salt) < 0.5:
                b.set(x, 5, z, "hay_block", axis="x")
    b.barrel(1, 4, Z0 + 1, loot=f"{NS}:chests/storehouse")
    return b


def hof(salt):
    """Temple hall with a tiered stave roof, idol posts and an outdoor stone altar ring."""
    b = Build(f"hof_{salt}")
    half, Z0, Z1 = 5, 4, 20
    cx = half + 3
    hw = lambda z: half  # noqa: E731
    stave = lambda x, y, z: (("cobblestone", {}) if y == 1 else  # noqa: E731
                             ("dark_oak_log", {"axis": "y"}) if (x + z) % 2 else ("stripped_dark_oak_log", {"axis": "y"}))
    for z in range(Z0, Z1 + 1):
        for x in range(cx - half, cx + half + 1):
            b.set(x, 0, z, "cobblestone")
            b.set(x, 1, z, "polished_andesite" if abs(x - cx) <= 1 else "spruce_planks")
        if Z0 < z < Z1:
            b.air(cx - half + 1, 2, z, cx + half - 1, 14, z)
        for x in (cx - half, cx + half):
            for y in range(1, 6):
                b.set(x, y, z, *stave(x, y, z))
    ridge = gable_roof(b, cx, hw, Z0, Z1, 6, "shingle", overhang=1, salt=salt)
    for z in (Z0, Z1):
        gable_end(b, cx, hw, z, 6, 2, lambda x, y, zz: stave(x, y, zz))
    # raised upper tier over the middle (stave-church look)
    zt0, zt1 = Z0 + 5, Z1 - 5
    for z in range(zt0, zt1 + 1):
        for x in (cx - 2, cx + 2):
            for y in range(9, 12):
                b.set(x, y, z, *stave(x, y, z))
    gable_roof(b, cx, lambda z: 2, zt0, zt1, 12, "shingle", overhang=1, salt=salt + 1)
    for z in (zt0, zt1):
        gable_end(b, cx, lambda zz: 2, z, 12, 9, lambda x, y, zz: stave(x, y, zz))
    b.air(cx - 1, 9, zt0 + 1, cx + 1, 12, zt1 - 1)   # open the clerestory into the hall
    # spire with crossed horns
    zc = (Z0 + Z1) // 2
    b.fill(cx, 15, zc, cx, 18, zc, "dark_oak_log", axis="y")
    b.set(cx, 19, zc, "dark_oak_fence", **FENCE)
    crossed_horns(b, cx, ridge[Z0 - 1] + 1, Z0 - 1, "out")
    crossed_horns(b, cx, ridge[Z1 + 1] + 1, Z1 + 1, "out")
    b.door(cx, 2, Z0, "north")
    # idols, altar, banners, candles
    for x in (cx - 3, cx, cx + 3):
        b.fill(x, 2, Z1 - 2, x, 5, Z1 - 2, f"{NS}:carved_post", axis="y")
        b.set(x, 6, Z1 - 2, "dark_oak_log", axis="y")
    slab(b, cx - 1, 2, Z1 - 4, "polished_andesite_slab", "top")
    slab(b, cx + 1, 2, Z1 - 4, "polished_andesite_slab", "top")
    b.set(cx, 2, Z1 - 4, "brewing_stand", has_bottle_0=False, has_bottle_1=False, has_bottle_2=False)
    for x in (cx - 1, cx + 1):
        candle(b, x, 3, Z1 - 4, 3)
    for z in range(Z0 + 2, Z1 - 3, 3):
        for side in (-1, 1):
            x = cx + side * (half - 1)
            b.banner(x, 5, z, "east" if side < 0 else "west", "red" if (z // 3) % 2 else "black")
            bench(b, cx + side * 2, 2, z, "south")
    for z in range(Z0 + 3, Z1 - 2, 4):
        if zt0 < z < zt1:
            hanging_lantern(b, cx, 13, z, length=4)
        else:
            hanging_lantern(b, cx, 10, z, length=2)
    b.chest(cx + half - 1, 2, Z1 - 1, "north", f"{NS}:chests/hof")
    # stone altar (hörgr) with a fire in front of the temple
    for x in (cx - 3, cx + 3):
        b.fill(x, 1, 1, x, 2, 1, "mossy_cobblestone")
    b.set(cx, 1, 1, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
    b.villager(cx, 2, Z1 - 6, "cleric")
    return b


def market(salt):
    """A row of trading stalls with striped wool awnings."""
    b = Build(f"market_{salt}")
    colours = [("red", "white"), ("blue", "white"), ("yellow", "brown"), ("green", "white")]
    goods = [("barrel", "hay_block"), ("fletching_table", "barrel"), ("cartography_table", "barrel"),
             ("stonecutter", "chest")]
    for i in range(3 + salt % 2):
        x0 = i * 6
        c1, c2 = colours[(i + salt) % 4]
        for x in range(x0, x0 + 5):
            for z in range(1, 6):
                b.set(x, 0, z, "gravel" if h(x, z) < 0.4 else "cobblestone")
                b.set(x, 1, z, "coarse_dirt" if h(z, x) < 0.5 else "dirt_path")
        for x, z in ((x0, 1), (x0 + 4, 1), (x0, 5), (x0 + 4, 5)):
            b.fill(x, 2, z, x, 4 if z == 1 else 5, z, "stripped_spruce_log", axis="y")
        for x in range(x0, x0 + 5):
            for z in range(0, 6):
                y = 5 if z < 3 else 6
                b.set(x, y, z, f"{c1}_wool" if x % 2 else f"{c2}_wool")
        for x in range(x0 + 1, x0 + 4):
            slab(b, x, 2, 2, "spruce_slab", "top")
        g1, g2 = goods[(i + salt) % 4]
        if g1 == "barrel":
            b.barrel(x0 + 1, 2, 4)
        elif g1 == "stonecutter":
            b.set(x0 + 1, 2, 4, g1, facing="north")
        else:
            b.set(x0 + 1, 2, 4, g1)
        if g2 == "chest":
            b.chest(x0 + 3, 2, 4, "north", f"{NS}:chests/storehouse")
        elif g2 == "hay_block":
            b.set(x0 + 3, 2, 4, g2, axis="y")
        else:
            b.barrel(x0 + 3, 2, 4, loot=f"{NS}:chests/storehouse")
        candle(b, x0 + 2, 3, 2)
        b.set(x0 + 2, 2, 4, "lantern", hanging=False, waterlogged=False)
    b.villager(2, 2, 3, "fletcher")
    b.villager(8, 2, 3, "cartographer")
    b.villager(14, 2, 3, "mason")
    return b


def training_yard(salt):
    b = Build(f"training_yard_{salt}")
    X1, Z1 = 16, 13
    for x in range(X1 + 1):
        for z in range(1, Z1 + 1):
            b.set(x, 0, z, "dirt")
            b.set(x, 1, z, "coarse_dirt" if h(x, z, salt) < 0.5 else ("gravel" if h(z, x) < 0.5 else "dirt_path"))
    b.air(0, 2, 1, X1, 5, Z1)
    for x in range(X1 + 1):
        for z in (1, Z1):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    for z in range(1, Z1 + 1):
        for x in (0, X1):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    b.air(7, 2, 1, 9, 2, 1)
    # practice dummies
    for x, z in ((4, 5), (8, 5), (12, 5)):
        b.set(x, 2, z, "hay_block", axis="y")
        armor_stand(b, x, 3, z, 180, head="carved_pumpkin" if h(x) < 0.3 else "leather_helmet",
                    chest="leather_chestplate")
    # archery targets
    for x in (3, 7, 11):
        b.set(x, 2, Z1 - 1, "hay_block", axis="y")
        b.set(x, 3, Z1 - 1, "target", power=0)
    # weapon racks and benches
    armor_stand(b, 1, 2, 9, 90, hand="iron_axe", offhand="shield")
    armor_stand(b, X1 - 1, 2, 9, 270, hand="iron_sword", offhand="shield")
    for x in range(5, 12):
        bench(b, x, 2, 9, "north")
    b.set(14, 2, 3, "fletching_table")
    b.set(15, 3, 1, "lantern", hanging=False, waterlogged=False)
    b.set(1, 3, 1, "lantern", hanging=False, waterlogged=False)
    b.villager(6, 2, 3, "fletcher")
    return b


def drying_racks(salt):
    b = Build(f"drying_racks_{salt}")
    for x in range(-1, 9):
        for z in range(0, 8):
            b.set(x, 0, z, "coarse_dirt" if h(x, z, salt) < 0.5 else "dirt_path")
    for i in range(3):
        x0 = i * 3
        for z in (1, 6):
            b.fill(x0, 1, z, x0, 3, z, "spruce_fence", **FENCE)
        for z in range(1, 7):
            b.set(x0, 4, z, "spruce_log", axis="z")
            if 1 < z < 6:
                b.set(x0, 3, z, "dried_kelp_block")
                if h(x0, z, salt) < 0.5:
                    b.set(x0, 2, z, "dried_kelp_block")
    b.barrel(7, 1, 0)
    b.set(8, 1, 0, "water_cauldron", level=3)
    return b


# ---------------------------------------------------------------------------
# Village civic pieces
# ---------------------------------------------------------------------------
def plaza(salt):
    b = Build(f"plaza_{salt}")
    N = 23
    c = N // 2
    for x in range(N):
        for z in range(N):
            r = h(x, z, salt)
            b.set(x, 0, z, "cobblestone" if r < 0.35 else "gravel" if r < 0.55 else "dirt_path" if r < 0.8 else
                  "coarse_dirt")
    b.air(0, 1, 0, N - 1, 7, N - 1)
    # covered well
    for x in range(c - 1, c + 2):
        for z in range(c - 1, c + 2):
            if (x, z) == (c, c):
                b.set(x, 0, z, "water", level=0)
            else:
                b.set(x, 1, z, "cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                      waterlogged=False)
    for x, z in ((c - 1, c - 1), (c + 1, c - 1), (c - 1, c + 1), (c + 1, c + 1)):
        b.fill(x, 2, z, x, 3, z, "spruce_fence", **FENCE)
    gable_roof(b, c, lambda z: 1, c - 1, c + 1, 4, "spruce", overhang=1)
    b.set(c, 4, c, "chain", axis="y", waterlogged=False)
    b.set(c, 3, c, "chain", axis="y", waterlogged=False)
    b.set(c, 2, c, "lantern", hanging=True, waterlogged=False)
    # bell under a carved frame
    bx, bz = c, c - 6
    b.fill(bx - 1, 1, bz, bx - 1, 4, bz, f"{NS}:carved_post", axis="y")
    b.fill(bx + 1, 1, bz, bx + 1, 4, bz, f"{NS}:carved_post", axis="y")
    b.set(bx, 5, bz, "stripped_spruce_log", axis="x")
    b.set(bx - 1, 5, bz, "stripped_spruce_log", axis="x")
    b.set(bx + 1, 5, bz, "stripped_spruce_log", axis="x")
    b.set(bx, 4, bz, "bell", attachment="ceiling", facing="north", powered=False)
    # runestones at the corners
    from .designs import runestone_at
    runestone_at(b, 2, 1, 2, "x", salt)
    runestone_at(b, N - 4, 1, N - 3, "x", salt + 1)
    # fire pit with benches
    fx, fz = c + 6, c + 5
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        slab(b, fx + dx, 1, fz + dz, "cobblestone_slab")
    b.set(fx, 1, fz, "campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
    for dx in (-2, 2):
        for dz in (-1, 0, 1):
            bench(b, fx + dx, 1, fz + dz, "west" if dx > 0 else "east")
    # banner poles and lamp posts
    for x, z, col in ((3, c, "red"), (N - 4, c, "blue"), (c, N - 3, "yellow")):
        b.fill(x, 1, z, x, 5, z, "stripped_spruce_log", axis="y")
        b.banner(x, 5, z - 1, "north", col)
        b.set(x, 6, z, "lantern", hanging=False, waterlogged=False)
    for x, z in ((c - 5, c + 5), (c + 5, c - 5), (c - 6, c - 3)):
        b.set(x, 1, z, "spruce_fence", **FENCE)
        b.set(x, 2, z, "spruce_fence", **FENCE)
        b.set(x, 3, z, "lantern", hanging=False, waterlogged=False)
    b.set(c - 6, 1, c + 7, "hay_block", axis="x")
    b.set(c - 5, 1, c + 7, "hay_block", axis="y")
    b.barrel(c + 7, 1, c - 7)
    b.barrel(c + 8, 1, c - 7)
    b.villager(c - 3, 1, c)
    b.villager(c + 3, 1, c - 2)
    return b


def gatehouse(salt):
    """Two log towers flanking the gate, joined by a walkway, topped with stakes."""
    b = Build(f"gatehouse_{salt}")
    W, D = 17, 6       # x width, z depth
    gx0, gx1 = 6, 10   # gate opening
    for x in range(W):
        for z in range(D):
            b.set(x, 0, z, "cobblestone")
    for x in range(gx0, gx1 + 1):
        for z in range(D):
            b.set(x, 0, z, "gravel" if h(x, z) < 0.5 else "dirt_path")
    for tx0 in (0, gx1 + 1):
        tx1 = tx0 + 5
        for x in range(tx0, tx1 + 1):
            for z in range(D):
                edge = x in (tx0, tx1) or z in (0, D - 1)
                for y in range(1, 9):
                    if edge:
                        corner = x in (tx0, tx1) and z in (0, D - 1)
                        b.set(x, y, z, "stripped_spruce_log" if corner else "spruce_log", axis="y")
                    else:
                        b.set(x, y, z, "air")
                b.set(x, 9, z, "spruce_planks")
                if edge:
                    b.set(x, 10, z, "spruce_log", axis="y")
                    b.set(x, 11, z, f"{NS}:palisade_stake")
        # inner door and ladder
        dx = tx0 + 2
        b.door(dx, 1, D - 1, "south")
        for y in range(1, 10):
            b.set(tx0 + 1, y, 1, "ladder", facing="south", waterlogged=False)
        # arrow slits
        for y in (4, 7):
            b.set(tx0 + 2, y, 0, "air")
            b.set(tx0 + 3, y, 0, "air")
        b.set(tx0 + 3, 2, D - 2, "barrel", nbt={"id": "minecraft:barrel"}, facing="up", open=False)
        b.set(tx0 + 2, 8, 2, "lantern", hanging=True, waterlogged=False)
    # walkway bridge over the gate
    for x in range(gx0, gx1 + 1):
        for z in range(D):
            b.set(x, 7, z, "spruce_planks")
            if z in (0, D - 1):
                b.set(x, 8, z, "spruce_fence", **FENCE)
    # gate leaves standing open, banners and lanterns
    b.set(gx0, 1, 0, "spruce_fence_gate", facing="north", open=True, in_wall=False, powered=False)
    b.set(gx1, 1, 0, "spruce_fence_gate", facing="north", open=True, in_wall=False, powered=False)
    b.banner(gx0 - 1, 6, -1, "north", "red")
    b.banner(gx1 + 1, 6, -1, "north", "red")
    b.set(gx0, 6, 0, "lantern", hanging=True, waterlogged=False)
    b.set(gx1, 6, 0, "lantern", hanging=True, waterlogged=False)
    for x in (gx0 - 1, gx1 + 1):
        shield(b, x, 4, -1, "north", salt)
    b.villager(3, 9, 3)
    return b


def watchtower(salt):
    b = Build(f"watchtower_{salt}")
    for x in range(5):
        for z in range(5):
            b.set(x, 0, z, "cobblestone")
    for x, z in ((0, 0), (4, 0), (0, 4), (4, 4)):
        b.fill(x, 1, z, x, 12, z, "spruce_log", axis="y")
    for y in (4, 8):
        for i in range(1, 4):
            b.set(i, y, 0, "stripped_spruce_log", axis="x")
            b.set(i, y, 4, "stripped_spruce_log", axis="x")
            b.set(0, y, i, "stripped_spruce_log", axis="z")
            b.set(4, y, i, "stripped_spruce_log", axis="z")
    for x in range(-1, 6):
        for z in range(-1, 6):
            b.set(x, 12, z, "spruce_planks")
    for x in range(-1, 6):
        for z in (-1, 5):
            b.set(x, 13, z, "spruce_fence", **FENCE)
    for z in range(-1, 6):
        for x in (-1, 5):
            b.set(x, 13, z, "spruce_fence", **FENCE)
    for x, z in ((-1, -1), (5, -1), (-1, 5), (5, 5)):
        b.fill(x, 13, z, x, 15, z, "spruce_log", axis="y")
    for k in range(4):   # pyramid roof
        for x in range(-2 + k, 7 - k):
            for z in range(-2 + k, 7 - k):
                if x in (-2 + k, 6 - k) or z in (-2 + k, 6 - k):
                    b.set(x, 16 + k, z, "dark_oak_planks" if k < 3 else "dark_oak_slab",
                          **({} if k < 3 else {"type": "bottom", "waterlogged": False}))
    b.set(2, 19, 2, f"{NS}:carved_post", axis="y")
    b.set(2, 20, 2, "lightning_rod", facing="up", powered=False, waterlogged=False)
    for y in range(1, 13):
        b.set(2, y, 0, "spruce_log", axis="y")
        b.set(2, y, 1, "ladder", facing="south", waterlogged=False)
    b.set(2, 15, 2, "lantern", hanging=True, waterlogged=False)
    b.set(2, 16, 2, "dark_oak_planks")
    b.barrel(3, 13, 3)
    b.banner(4, 11, 5, "south", "red")
    return b


def farm(salt, w=15, d=11):
    b = Build(f"field_{salt}")
    crops = [("wheat", 7), ("carrots", 7), ("potatoes", 7), ("beetroots", 3), ("wheat", 7)]
    for x in range(w):
        for z in range(1, d + 1):
            b.set(x, 0, z, "dirt")
            edge = x in (0, w - 1) or z in (1, d)
            if edge:
                b.set(x, 1, z, "coarse_dirt")
            elif x % 5 == 0:
                b.set(x, 1, z, "water", level=0)
            else:
                b.set(x, 1, z, "farmland", moisture=7)
                name, top = crops[(x // 5 + salt) % 5]
                age = top if h(x, z, salt) < 0.65 else int(h(z, x, salt) * top)
                b.set(x, 2, z, name, age=age)
    for x in range(w):
        for z in (1, d):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    for z in range(1, d + 1):
        for x in (0, w - 1):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    b.set(w // 2, 2, 1, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)
    b.set(1, 2, d - 1, "composter", level=3)
    # scarecrow
    sx, sz = w // 2 + 1, d // 2 + 1
    b.set(sx, 2, sz, "spruce_fence", **FENCE)
    b.set(sx, 3, sz, "hay_block", axis="y")
    armor_stand(b, sx, 3, sz, 180, head="carved_pumpkin", chest="leather_chestplate")
    for x in (w - 3, w - 2):   # hay drying on fence posts
        b.set(x, 2, d + 1, "spruce_fence", **FENCE)
        b.set(x, 3, d + 1, "hay_block", axis="x")
    b.set(0, 3, 1, "torch")
    return b


def sheep_fold(salt):
    b = Build(f"sheep_fold_{salt}")
    W, D = 13, 11
    for x in range(W):
        for z in range(1, D + 1):
            b.set(x, 0, z, "dirt")
            b.set(x, 1, z, "grass_block", snowy=False)
    b.air(1, 2, 2, W - 2, 4, D - 1)
    for x in range(W):
        for z in (1, D):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    for z in range(1, D + 1):
        for x in (0, W - 1):
            b.set(x, 2, z, "spruce_fence", **FENCE)
    b.set(W // 2, 2, 1, "spruce_fence_gate", facing="north", open=False, in_wall=False, powered=False)
    # lean-to shelter at the back
    for x in range(1, W - 1):
        for z in range(D - 3, D):
            slab(b, x, 5 if z < D - 1 else 5, z, f"{NS}:thatch_slab")
    for x in (1, W - 2):
        b.fill(x, 2, D - 3, x, 4, D - 3, "spruce_fence", **FENCE)
    for x in range(1, W - 1):
        b.set(x, 2, D - 1, "spruce_planks")
        b.set(x, 3, D - 1, "spruce_planks")
        b.set(x, 4, D - 1, "spruce_planks")
    b.set(2, 2, D - 2, "hay_block", axis="y")
    b.set(3, 2, D - 2, "hay_block", axis="x")
    b.set(W - 3, 2, D - 2, "water_cauldron", level=3)
    for i, (x, z) in enumerate(((3, 4), (6, 5), (8, 3), (9, 6), (4, 7))):
        b.animal(x, 2, z, "sheep", Color=Byte((0, 0, 12, 15, 8)[i]))
    b.set(0, 3, 1, "torch")
    b.set(W - 1, 3, 1, "torch")
    return b


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
def catalogue():
    """name -> (Build, role). Roles: core, house, craft, civic, field, wall."""
    c = {}

    def add(n, b, role):
        from .dress import dress
        c[f"viking/{n}"] = (dress(b, f"viking/{n}", role, salt=sum(map(ord, n))), role)

    add("great_hall", hall("great_hall", 43, 7, 5, "shingle", "stave", wall_h=4, great=True, salt=1, villagers=4),
        "core")
    add("longhouse_large_shingle", hall("lh_ls", 31, 6, 4, "shingle", "timber", wall_h=3, byre=True, salt=2,
                                        villagers=3), "house")
    add("longhouse_large_thatch", hall("lh_lt", 29, 6, 4, "thatch", "plank", wall_h=3, loft=True, salt=3,
                                       villagers=3), "house")
    add("longhouse_medium_turf", hall("lh_mt", 23, 5, 4, "turf", "turf", wall_h=3, salt=4, villagers=2), "house")
    add("longhouse_medium_thatch", hall("lh_mth", 23, 5, 4, "thatch", "timber", wall_h=3, byre=True, chamber=False,
                                        salt=5, villagers=2), "house")
    add("longhouse_medium_shingle", hall("lh_ms", 21, 5, 4, "shingle", "plank", wall_h=3, loft=True, salt=6,
                                         villagers=2), "house")
    add("longhouse_small_thatch", hall("lh_st", 15, 4, 3, "thatch", "timber", wall_h=3, chamber=False, salt=7,
                                       villagers=1), "house")
    add("longhouse_small_turf", hall("lh_stu", 15, 4, 3, "turf", "turf", wall_h=3, chamber=False, salt=8,
                                     villagers=1), "house")
    add("farmstead_a", farmstead(0), "house")
    add("farmstead_b", farmstead(1), "house")
    add("turf_cottage_a", turf_cottage(0), "house")
    add("turf_cottage_b", turf_cottage(5), "house")
    add("pit_house", pit_house(0), "craft")
    add("forge", forge(0), "craft")
    add("stabbur_small", stabbur(False, 0), "craft")
    add("stabbur_large", stabbur(True, 1), "craft")
    add("byre", byre(0), "craft")
    add("granary", granary(0), "craft")
    add("hof", hof(0), "civic")
    add("market", market(0), "civic")
    add("training_yard", training_yard(0), "civic")
    add("drying_racks", drying_racks(0), "craft")
    add("plaza", plaza(0), "plaza")
    add("gatehouse", gatehouse(0), "wall")
    add("watchtower", watchtower(0), "wall")
    add("field_a", farm(0), "field")
    add("field_b", farm(2, w=11, d=13), "field")
    add("sheep_fold", sheep_fold(0), "field")
    return c
