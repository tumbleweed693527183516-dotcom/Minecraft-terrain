#!/usr/bin/env python3
"""
Reads a generated world's region files and saves compact maps for inspection:
surface height, ocean-floor height, top block and surface biome for every column.

    python3 extract.py <world dir> <out dir>
Writes <out>/world_maps.npz and <out>/names.json.
"""
import io
import json
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

MIN_Y = -64


# ---- minimal NBT reader ----
def read_nbt(buf):
    f = io.BytesIO(buf)

    def rd(fmt):
        return struct.unpack(">" + fmt, f.read(struct.calcsize(">" + fmt)))[0]

    def string():
        return f.read(rd("H")).decode("utf-8", "replace")

    def payload(t):
        if t == 1: return rd("b")
        if t == 2: return rd("h")
        if t == 3: return rd("i")
        if t == 4: return rd("q")
        if t == 5: return rd("f")
        if t == 6: return rd("d")
        if t == 7: return f.read(rd("i"))
        if t == 8: return string()
        if t == 9:
            et, n = rd("b"), rd("i")
            return [payload(et) for _ in range(n)]
        if t == 10:
            out = {}
            while True:
                et = rd("b")
                if et == 0:
                    return out
                name = string()
                out[name] = payload(et)
        if t == 11: return np.frombuffer(f.read(4 * rd("i")), ">i4")
        if t == 12: return np.frombuffer(f.read(8 * rd("i")), ">i8")
        raise ValueError(f"bad tag {t}")

    t = rd("b")
    string()
    return payload(t)


def unpack(longs, bits, count):
    """Unpack Minecraft's packed long arrays (1.16+: entries don't span longs)."""
    per = 64 // bits
    u = np.asarray(longs).astype(np.uint64)
    shifts = (np.arange(per, dtype=np.uint64) * np.uint64(bits))
    vals = (u[:, None] >> shifts[None, :]) & np.uint64((1 << bits) - 1)
    return vals.reshape(-1)[:count].astype(np.int64)


def chunks_in_region(path):
    data = path.read_bytes()
    if len(data) < 8192:
        return
    for i in range(1024):
        off = int.from_bytes(data[i * 4:i * 4 + 3], "big")
        if off == 0:
            continue
        start = off * 4096
        length = int.from_bytes(data[start:start + 4], "big")
        comp = data[start + 4]
        raw = data[start + 5:start + 4 + length]
        if comp == 2:
            yield read_nbt(zlib.decompress(raw))


def main(world, out):
    regions = sorted(Path(world, "region").glob("r.*.mca"))
    chunks = []
    for r in regions:
        chunks.extend(c for c in chunks_in_region(r) if c.get("Status", "").endswith("full"))
    xs = [c["xPos"] for c in chunks]
    zs = [c["zPos"] for c in chunks]
    x0, z0 = min(xs), min(zs)
    W, H = (max(xs) - x0 + 1) * 16, (max(zs) - z0 + 1) * 16
    surf = np.full((H, W), -9999, np.int16)
    floor = np.full((H, W), -9999, np.int16)
    block_id = np.zeros((H, W), np.uint16)
    biome_id = np.zeros((H, W), np.uint16)
    block_names, biome_names = {"?": 0}, {"?": 0}

    def bid(name, table):
        if name not in table:
            table[name] = len(table)
        return table[name]

    for c in chunks:
        hm = c["Heightmaps"]
        hs = unpack(hm["WORLD_SURFACE"], 10, 256).reshape(16, 16) + MIN_Y
        hf = unpack(hm["OCEAN_FLOOR"], 10, 256).reshape(16, 16) + MIN_Y
        cx, cz = (c["xPos"] - x0) * 16, (c["zPos"] - z0) * 16
        surf[cz:cz + 16, cx:cx + 16] = hs
        floor[cz:cz + 16, cx:cx + 16] = hf
        sections = {s["Y"]: s for s in c["sections"]}
        top_y = hs - 1
        cache = {}
        for sy in np.unique(top_y >> 4):
            s = sections.get(int(sy))
            if s is None or "block_states" not in s:
                continue
            bs = s["block_states"]
            pal = [bid(p["Name"], block_names) for p in bs["palette"]]
            if "data" in bs:
                bits = max(4, int(np.ceil(np.log2(len(pal)))))
                blocks = np.array(pal)[unpack(bs["data"], bits, 4096)]
            else:
                blocks = np.full(4096, pal[0])
            bm = s.get("biomes", {})
            bpal = [bid(p, biome_names) for p in bm.get("palette", ["?"])]
            if "data" in bm:
                bbits = max(1, int(np.ceil(np.log2(len(bpal)))))
                biomes = np.array(bpal)[unpack(bm["data"], bbits, 64)]
            else:
                biomes = np.full(64, bpal[0])
            cache[int(sy)] = (blocks, biomes)
        zz, xx = np.mgrid[0:16, 0:16]
        for sy, (blocks, biomes) in cache.items():
            mask = (top_y >> 4) == sy
            ly = top_y[mask] & 15
            block_id[cz:cz + 16, cx:cx + 16][mask] = blocks[ly * 256 + zz[mask] * 16 + xx[mask]]
            biome_id[cz:cz + 16, cx:cx + 16][mask] = biomes[(ly >> 2) * 16 + (zz[mask] >> 2) * 4 + (xx[mask] >> 2)]

    Path(out).mkdir(parents=True, exist_ok=True)
    np.savez_compressed(Path(out, "world_maps.npz"), surface=surf, floor=floor, block=block_id, biome=biome_id,
                        origin=np.array([x0 * 16, z0 * 16]))
    Path(out, "names.json").write_text(json.dumps({
        "blocks": sorted(block_names, key=block_names.get), "biomes": sorted(biome_names, key=biome_names.get)}))
    print(f"Extracted {len(chunks)} chunks, {W}x{H} blocks, height {surf[surf > -9999].min()}..{surf.max()}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
