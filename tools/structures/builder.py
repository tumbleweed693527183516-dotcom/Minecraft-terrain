"""
Tiny voxel builder for structure templates.

Coordinates: x = width, y = up, z = length. Only cells that are set are written, so
anything left unset keeps whatever terrain is there (like structure void).
"""
from .nbtio import Byte, DoubleList, IntList, write_nbt

import modblocks

DATA_VERSION = 3465  # Minecraft 1.20.1


def mc(n):
    return n if ":" in n else f"minecraft:{n}"


class Build:
    def __init__(self, name):
        self.name = name
        self.blocks = {}      # (x, y, z) -> (block, props tuple, nbt or None)
        self.entities = []

    # ---- basic ----
    def set(self, x, y, z, block, nbt=None, **props):
        self.blocks[(x, y, z)] = (mc(block), tuple(sorted((k, str(v).lower() if isinstance(v, bool) else str(v))
                                                         for k, v in props.items())), nbt)

    def get(self, x, y, z):
        b = self.blocks.get((x, y, z))
        return b[0] if b else None

    def fill(self, x0, y0, z0, x1, y1, z1, block, **props):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, block, **props)

    def air(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, "air")

    # ---- special blocks ----
    def chest(self, x, y, z, facing, loot):
        self.set(x, y, z, "chest", nbt={"id": "minecraft:chest", "LootTable": loot}, facing=facing, type="single",
                 waterlogged=False)

    def barrel(self, x, y, z, facing="up", loot=None):
        nbt = {"id": "minecraft:barrel"}
        if loot:
            nbt["LootTable"] = loot
        self.set(x, y, z, "barrel", nbt=nbt, facing=facing, open=False)

    def bed(self, x, y, z, facing, color="red"):
        """Bed whose head points toward `facing` from the foot at (x, y, z)."""
        dx, dz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[facing]
        nbt = {"id": "minecraft:bed"}
        self.set(x, y, z, f"{color}_bed", nbt=nbt, facing=facing, part="foot", occupied=False)
        self.set(x + dx, y, z + dz, f"{color}_bed", nbt=nbt, facing=facing, part="head", occupied=False)

    def door(self, x, y, z, facing, wood="spruce", hinge="left"):
        for half, dy in (("lower", 0), ("upper", 1)):
            self.set(x, y + dy, z, f"{wood}_door", facing=facing, half=half, hinge=hinge, open=False, powered=False)

    def jigsaw(self, x, y, z, front, name, target, pool, final_state="minecraft:air", joint="aligned"):
        self.set(x, y, z, "jigsaw", nbt={"id": "minecraft:jigsaw", "name": name, "target": target, "pool": pool,
                                         "final_state": final_state, "joint": joint},
                 orientation=f"{front}_up")

    def banner(self, x, y, z, facing, color):
        self.set(x, y, z, f"{color}_wall_banner", nbt={"id": "minecraft:banner"}, facing=facing)

    def entity(self, x, y, z, nbt):
        self.entities.append((x, y, z, nbt))

    def villager(self, x, y, z, profession="none"):
        self.entity(x + 0.5, y, z + 0.5, {
            "id": "minecraft:villager", "PersistenceRequired": Byte(1),
            "VillagerData": {"type": "minecraft:taiga", "profession": f"minecraft:{profession}", "level": 1}})

    def animal(self, x, y, z, kind, **extra):
        self.entity(x + 0.5, y, z + 0.5, dict({"id": f"minecraft:{kind}", "PersistenceRequired": Byte(1)}, **extra))

    # ---- output ----
    def bounds(self):
        xs, ys, zs = zip(*self.blocks)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def save(self, path):
        (x0, y0, z0), (x1, y1, z1) = self.bounds()
        palette, index, blocks = [], {}, []
        for (x, y, z), (name, props, nbt) in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            name, props = modblocks.name(name), modblocks.props(name, props)   # design names -> mod blocks
            key = (name, props)
            if key not in index:
                index[key] = len(palette)
                entry = {"Name": name}
                if props:
                    entry["Properties"] = dict(props)
                palette.append(entry)
            b = {"pos": IntList([x - x0, y - y0, z - z0]), "state": index[key]}
            if nbt:
                b["nbt"] = nbt
            blocks.append(b)
        ents = [{"pos": DoubleList([ex - x0, ey - y0, ez - z0]),
                 "blockPos": IntList([int(ex - x0), int(ey - y0), int(ez - z0)]), "nbt": nbt}
                for ex, ey, ez, nbt in self.entities]
        root = {"DataVersion": DATA_VERSION, "size": IntList([x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1]),
                "palette": palette, "blocks": blocks, "entities": ents}
        path.parent.mkdir(parents=True, exist_ok=True)
        write_nbt(path, root)
        return root["size"]
