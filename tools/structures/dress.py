"""
Detail pass applied to every finished building: windows with shutters and flower boxes, a
gravel drip edge with plants, lantern posts, yard clutter that fits the building's trade,
rugs and clutter indoors, weathering, and loot wiring (every building has at least one chest,
all of them tied to that building's own loot table).
"""
from .kit import (FENCE, NS, cart, chopping_block, h, hide_frame, potted, water_barrel, weather, window,
                  woodpile)

WINDOW_WALLS = ("wattle_daub", "spruce_planks", "pine_planks", "dark_oak_planks", "oak_planks", "mud_bricks",
                "birch_planks")
SOLID_SKIP = ("air", "door", "fence", "pane", "trapdoor", "lantern", "chain", "torch", "carpet", "slab", "stairs",
              "banner", "shield", "ladder", "campfire", "candle", "bed", "chest", "barrel", "vine")
DIRS4 = ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north"))


def _solid(name):
    return name is not None and not any(k in name for k in SOLID_SKIP)


def windows(b, salt, spacing=4):
    """Glazed, shuttered windows in plain wall cells that have room inside and outside."""
    placed = []
    for (x, y, z), (name, props, nbt) in sorted(b.blocks.items()):
        if y not in (3, 4) or not name.endswith(WINDOW_WALLS):
            continue
        for dx, dz, out in DIRS4:
            if b.get(x + dx, y, z + dz) is not None or b.get(x - dx, y, z - dz) != "minecraft:air":
                continue
            if not (_solid(b.get(x, y - 1, z)) and _solid(b.get(x, y + 1, z))):
                continue
            # keep clear of doors and of other windows
            near_door = any("door" in (b.get(x + i * dz, yy, z + i * dx) or "") for i in range(-2, 3)
                            for yy in (2, 3))
            if near_door or any(abs(px - x) + abs(pz - z) < spacing and py == y for px, py, pz in placed):
                continue
            if h(x, y, z, salt, 9) < 0.55:
                window(b, x, y, z, out)
                placed.append((x, y, z))
            break
    return len(placed)


def footprint(b):
    return {(x, z) for (x, y, z), v in b.blocks.items() if y == 0 and v[0] != "minecraft:air"}


def drip_edge(b, salt):
    """Gravel and cobble around the foundation, with plants and flowers tucked against the walls."""
    fp = footprint(b)
    plants = ["fern", "grass", "sweet_berry_bush", "cornflower", "allium", "oxeye_daisy", f"{NS}:heather"]
    for (x, z) in list(fp):
        for dx, dz, _ in DIRS4:
            nx, nz = x + dx, z + dz
            if (nx, nz) in fp or b.get(nx, 0, nz) is not None or b.get(nx, 1, nz) is not None:
                continue
            r = h(nx, nz, salt, 31)
            b.set(nx, 0, nz, "gravel" if r < 0.45 else ("coarse_dirt" if r < 0.7 else "mossy_cobblestone"))
            if r > 0.82 and b.get(nx, 2, nz) is None:
                p = plants[int(h(nz, nx, salt) * len(plants))]
                b.set(nx, 0, nz, "grass_block", snowy=False)
                b.set(nx, 1, nz, p, **({"age": 2} if p == "sweet_berry_bush" else {}))


def _free(b, x, z, w=1, d=1, hgt=3):
    for xx in range(x, x + w):
        for zz in range(z, z + d):
            for y in range(1, hgt + 1):
                if b.get(xx, y, zz) is not None:
                    return False
            if b.get(xx, 0, zz) not in (None, "minecraft:gravel", "minecraft:coarse_dirt"):
                return False
    return True


def _ground(b, x, z, w=1, d=1):
    for xx in range(x, x + w):
        for zz in range(z, z + d):
            if b.get(xx, 0, zz) is None:
                b.set(xx, 0, zz, "coarse_dirt" if h(xx, zz) < 0.5 else "grass_block",
                      **({} if h(xx, zz) < 0.5 else {"snowy": False}))


YARD = {
    "house": ["woodpile", "chop", "water", "hide", "barrels", "pots", "hay", "lantern"],
    "core": ["woodpile", "lantern", "barrels", "cart", "rack", "lantern"],
    "craft": ["crates", "cart", "chop", "grind", "woodpile", "lantern", "anvil"],
    "civic": ["lantern", "banner", "pots", "barrels"],
}


def yard(b, role, salt, n=5):
    """Scatter role-appropriate clutter in free spots 2 blocks out from the walls."""
    kinds = YARD.get(role)
    if not kinds:
        return
    fp = footprint(b)
    if not fp:
        return
    xs = [x for x, _ in fp]
    zs = [z for _, z in fp]
    x0, x1, z0, z1 = min(xs) - 2, max(xs) + 2, min(zs) - 2, max(zs) + 2
    ring = [(x, z0) for x in range(x0, x1 + 1)] + [(x, z1) for x in range(x0, x1 + 1)] + \
           [(x0, z) for z in range(z0, z1 + 1)] + [(x1, z) for z in range(z0, z1 + 1)]
    ring.sort(key=lambda p: h(p[0], p[1], salt, 5))
    used = []
    for (x, z) in ring:
        if len(used) >= n:
            break
        if any(abs(x - ux) + abs(z - uz) < 6 for ux, uz in used):
            continue
        if z == z0 and min(xs) + 2 <= x <= max(xs) - 2:
            continue    # keep the front (door side) open
        kind = kinds[len(used) % len(kinds)]
        along_x = z in (z0, z1)
        if kind == "woodpile":
            w, d = (4, 1) if along_x else (1, 4)
            if _free(b, x, z, w, d):
                _ground(b, x, z, w, d)
                woodpile(b, x, 1, z, 4, axis="x" if along_x else "z")
                used.append((x, z))
        elif kind == "chop" and _free(b, x, z, 2, 2):
            _ground(b, x, z, 2, 2)
            chopping_block(b, x, 1, z)
            used.append((x, z))
        elif kind == "water" and _free(b, x, z):
            _ground(b, x, z)
            water_barrel(b, x, 1, z)
            used.append((x, z))
        elif kind == "hide":
            w, d = (4, 1) if along_x else (1, 4)
            if _free(b, x, z, w, d):
                _ground(b, x, z, w, d)
                hide_frame(b, x, 1, z, "x" if along_x else "z", ("brown", "white", "light_gray")[int(h(x, z) * 3)])
                used.append((x, z))
        elif kind == "barrels" and _free(b, x, z, 2, 1):
            _ground(b, x, z, 2, 1)
            b.barrel(x, 1, z)
            b.barrel(x + 1, 1, z, facing="north")
            potted(b, x, 2, z, salt)
            used.append((x, z))
        elif kind == "pots" and _free(b, x, z, 2, 1):
            _ground(b, x, z, 2, 1)
            b.set(x, 1, z, "decorated_pot", facing="north", cracked=False, waterlogged=False)
            b.set(x + 1, 1, z, "flower_pot") if h(x, z) < 0.3 else potted(b, x + 1, 1, z, salt)
            used.append((x, z))
        elif kind == "hay" and _free(b, x, z, 2, 1):
            _ground(b, x, z, 2, 1)
            b.set(x, 1, z, "hay_block", axis="x")
            b.set(x + 1, 1, z, "hay_block", axis="y")
            b.set(x, 2, z, "hay_block", axis="z")
            used.append((x, z))
        elif kind == "lantern" and _free(b, x, z):
            _ground(b, x, z)
            b.set(x, 1, z, "stripped_spruce_log", axis="y")
            b.set(x, 2, z, "spruce_fence", **FENCE)
            b.set(x, 3, z, "lantern", hanging=False, waterlogged=False)
            used.append((x, z))
        elif kind == "cart":
            w, d = (3, 3) if along_x else (3, 3)
            if _free(b, x - 1, z - 1, 3, 3):
                _ground(b, x - 1, z - 1, 3, 3)
                cart(b, x, 1, z, "x" if along_x else "z", "hay_block" if h(x, z) < 0.5 else "barrel")
                used.append((x, z))
        elif kind == "crates" and _free(b, x, z, 2, 2):
            _ground(b, x, z, 2, 2)
            for i, (dx, dz) in enumerate(((0, 0), (1, 0), (0, 1))):
                b.barrel(x + dx, 1, z + dz)
            b.barrel(x, 2, z)
            used.append((x, z))
        elif kind == "grind" and _free(b, x, z):
            _ground(b, x, z)
            b.set(x, 1, z, "grindstone", face="floor", facing="north")
            used.append((x, z))
        elif kind == "anvil" and _free(b, x, z):
            _ground(b, x, z)
            b.set(x, 1, z, "chipped_anvil", facing="north")
            used.append((x, z))
        elif kind == "rack" and _free(b, x, z, 3, 1):
            _ground(b, x, z, 3, 1)
            for i in range(3):
                b.set(x + i, 1, z, "spruce_fence", **FENCE)
            b.set(x + 1, 2, z, "dried_kelp_block")
            used.append((x, z))
        elif kind == "banner" and _free(b, x, z):
            _ground(b, x, z)
            b.fill(x, 1, z, x, 4, z, "stripped_spruce_log", axis="y")
            b.banner(x, 4, z - 1, "north", ("red", "blue", "yellow")[int(h(x, z, salt) * 3)])
            used.append((x, z))


def interior(b, salt):
    """Rugs on open floor and the odd candle on a shelf."""
    for (x, y, z), (name, props, nbt) in list(b.blocks.items()):
        if name != "minecraft:air" or y != 2:
            continue
        below = b.get(x, 1, z) or ""
        if not below.endswith("planks"):
            continue
        r = h(x, z, salt, 41)
        if r < 0.05:
            b.set(x, y, z, ("brown_carpet", "red_carpet", "light_gray_carpet", "white_carpet")[int(h(z, x) * 4)])


def chests(b):
    return [(p, v) for p, v in b.blocks.items() if v[0] == "minecraft:chest"]


CHEST_COUNT = {"core": 3, "house": 2, "craft": 2, "civic": 2, "plaza": 1, "wall": 1, "field": 1}


def ensure_chests(b, loot, n, salt=0):
    """Top the building up to n chests: indoors against a wall where there is an interior (spread
    apart, never blocking a door), otherwise in the yard beside something solid."""
    have = [p for p, _ in chests(b)]
    if len(have) >= n:
        return
    cands = []
    for (x, y, z), (name, props, nbt) in b.blocks.items():
        if name != "minecraft:air" or y < 1:
            continue
        if not _solid(b.get(x, y - 1, z)) or b.get(x, y + 1, z) not in ("minecraft:air", None):
            continue
        walls = [(dx, dz, f) for dx, dz, f in DIRS4 if _solid(b.get(x + dx, y, z + dz))]
        if not walls or any("door" in (b.get(x + dx, y + dy, z + dz) or "") for dx, dz, _ in DIRS4
                            for dy in (0, -1)):
            continue
        dx, dz, f = walls[0]
        facing = {"east": "west", "west": "east", "south": "north", "north": "south"}[f]
        cands.append((h(x, y, z, salt), x, y, z, facing))
    if not cands:      # open-air structures: beside the fence, at a corner
        (x0, _, z0), (x1, _, z1) = b.bounds()
        for x, z in ((x0 - 1, z0 + 1), (x1 + 1, z1 - 1), (x0 - 1, z1 - 1)):
            b.set(x, 0, z, "coarse_dirt")
            cands.append((h(x, z, salt), x, 1, z, "east" if x < x0 else "west"))
    cands.sort()
    for _, x, y, z, f in cands:
        if len(have) >= n:
            break
        if any(abs(x - px) + abs(z - pz) < 6 for (px, py, pz) in have):
            continue
        b.chest(x, y, z, f, loot)
        have.append((x, y, z))


def wire_loot(b, loot):
    """Point every container that already had loot at this building's own table."""
    for p, (name, props, nbt) in list(b.blocks.items()):
        if nbt and "LootTable" in nbt:
            nbt = dict(nbt)
            nbt["LootTable"] = loot
            b.blocks[p] = (name, props, nbt)


def dress_exterior(b, role, salt=0):
    windows(b, salt)
    drip_edge(b, salt)
    interior(b, salt)
    yard(b, role, salt, n=6 if role == "core" else 4)
    return b


VILLAGERS = {"core": 2, "house": 1, "craft": 1, "civic": 1, "plaza": 1, "wall": 0, "field": 0}


def lighten(b, role):
    """Performance: one lit fire per building (campfire smoke is costly to render), and a modest
    number of villagers (villager AI is the classic cause of server lag in big villages)."""
    fires = sorted(p for p, v in b.blocks.items() if v[0] == "minecraft:campfire" and ("lit", "true") in v[1])
    for p in fires[1:]:
        name, props, nbt = b.blocks[p]
        b.blocks[p] = (name, tuple((k, "false" if k == "lit" else v) for k, v in props), nbt)
    keep = VILLAGERS.get(role, 1)
    out = []
    for e in b.entities:
        if e[3].get("id") == "minecraft:villager":
            if keep <= 0:
                continue
            keep -= 1
        out.append(e)
    b.entities = out


def dress(b, name, role, salt=0):
    short = name.split("/")[-1]
    loot = f"{NS}:chests/village/{short}"
    if role in ("house", "core", "craft", "civic"):
        windows(b, salt)
        drip_edge(b, salt)
        interior(b, salt)
        yard(b, role, salt, n=6 if role == "core" else 4)
    lighten(b, role)
    wire_loot(b, loot)
    ensure_chests(b, loot, CHEST_COUNT.get(role, 1), salt)
    weather(b, salt, vines=role != "field")
    return b
