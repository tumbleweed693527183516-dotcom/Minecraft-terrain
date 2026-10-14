#!/usr/bin/env python3
"""
After a structure world test: find Vivid Lands structures (from /locate and /place in
the server log, and from structure starts saved in chunks), dump the real blocks around
them, count entities, and render isometric views.

    python3 structures.py <world dir> <server.log> <out dir>
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from extract import chunks_in_region, unpack, MIN_Y  # noqa: E402
from structures.preview import color as block_color  # noqa: E402

R = 56
AIRS = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}


def load_chunks(world):
    out = {}
    for r in Path(world, "region").glob("r.*.mca"):
        for c in chunks_in_region(r):
            out[(c["xPos"], c["zPos"])] = c
    return out


def entity_list(world):
    ents = []
    for r in Path(world, "entities").glob("r.*.mca"):
        for c in chunks_in_region(r):
            for e in c.get("Entities", []):
                ents.append((e.get("id"), e.get("Pos")))
    return ents


def volume(chunks, cx, cz, R=R):
    x0, x1, z0, z1 = cx - R, cx + R, cz - R, cz + R
    tops = []
    for (px, pz), c in chunks.items():
        if px * 16 + 15 >= x0 and px * 16 <= x1 and pz * 16 + 15 >= z0 and pz * 16 <= z1 \
                and "WORLD_SURFACE" in c.get("Heightmaps", {}):
            tops.append(unpack(c["Heightmaps"]["WORLD_SURFACE"], 10, 256) + MIN_Y)
    if not tops:
        return None
    tops = np.concatenate(tops)
    y0, y1 = int(np.percentile(tops, 2)) - 6, int(tops.max()) + 2
    y1 = min(y1, y0 + 150)
    names = ["minecraft:air"]
    idx = {"minecraft:air": 0}
    vol = np.zeros((x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1), np.uint16)
    for (px, pz), c in chunks.items():
        if not (px * 16 + 15 >= x0 and px * 16 <= x1 and pz * 16 + 15 >= z0 and pz * 16 <= z1):
            continue
        if not c.get("Status", "").endswith("full"):
            continue
        for s in c["sections"]:
            sy = s["Y"]
            if sy * 16 + 15 < y0 or sy * 16 > y1 or "block_states" not in s:
                continue
            bs = s["block_states"]
            pal = []
            for p in bs["palette"]:
                n = p["Name"]
                if n not in idx:
                    idx[n] = len(names)
                    names.append(n)
                pal.append(idx[n])
            if "data" in bs:
                bits = max(4, int(np.ceil(np.log2(len(pal)))))
                arr = np.array(pal)[unpack(bs["data"], bits, 4096)]
            else:
                arr = np.full(4096, pal[0])
            arr = arr.reshape(16, 16, 16)  # y, z, x
            for ly in range(16):
                wy = sy * 16 + ly
                if not y0 <= wy <= y1:
                    continue
                for lz in range(16):
                    wz = pz * 16 + lz
                    if not z0 <= wz <= z1:
                        continue
                    xs = np.arange(16) + px * 16
                    m = (xs >= x0) & (xs <= x1)
                    vol[xs[m] - x0, wy - y0, wz - z0] = arr[ly, lz, m]
    return vol, names, (x0, y0, z0)


def render(vol, names, path, title):
    air = np.array([n in AIRS for n in names])
    solid = ~air[vol]
    vis = np.zeros_like(solid)
    pad = np.pad(solid, 1, constant_values=False)
    for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        nb = pad[1 + dx:pad.shape[0] - 1 + dx, 1 + dy:pad.shape[1] - 1 + dy, 1 + dz:pad.shape[2] - 1 + dz]
        vis |= solid & ~nb
    xs, ys, zs = np.nonzero(vis)
    order = np.lexsort((ys, xs + zs))
    s = 5 if vol.shape[0] < 150 else 3
    W = int((vol.shape[0] + vol.shape[2]) * s * 0.87) + 40
    H = int((vol.shape[0] + vol.shape[2]) * s * 0.5 + vol.shape[1] * s) + 60
    img = Image.new("RGB", (W, H), (226, 232, 238))
    d = ImageDraw.Draw(img)
    ox, oy = vol.shape[2] * s * 0.87 + 20, vol.shape[1] * s + 40
    cache = {}

    def proj(x, y, z):
        return ox + (x - z) * s * 0.87, oy + (x + z) * s * 0.5 - y * s

    for i in order:
        x, y, z = int(xs[i]), int(ys[i]), int(zs[i])
        bid = int(vol[x, y, z])
        if bid not in cache:
            n = names[bid]
            c = (95, 150, 60) if n.endswith(("grass_block", "_leaves", "fern", ":grass")) else block_color(n)
            if n.endswith("water"):
                c = (60, 120, 200)
            cache[bid] = c
        c = cache[bid]
        d.polygon([proj(x, y + 1, z), proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)], fill=c)
        d.polygon([proj(x, y + 1, z + 1), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x, y, z + 1)],
                  fill=tuple(int(v * 0.72) for v in c))
        d.polygon([proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x + 1, y, z)],
                  fill=tuple(int(v * 0.86) for v in c))
    d.text((10, 8), title, fill=(20, 20, 20))
    img.save(path)


def main(world, log, out):
    out = Path(out)
    text = Path(log).read_text(errors="replace")
    targets = []
    for m in re.finditer(r"nearest (vividlands:\w+) is at \[(-?\d+), [^,]+, (-?\d+)\] \((\d+) blocks away\)", text):
        targets.append(("located", m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))))
    for m in re.finditer(r'Generated structure "?(vividlands:\w+)"? at (-?\d+), (-?\d+), (-?\d+)', text):
        targets.append(("placed", m.group(1), int(m.group(2)), int(m.group(4)), 0))
    failures = re.findall(r"(Could not find[^\n]*|Failed to[^\n]*structure[^\n]*)", text)
    chunks = load_chunks(world)
    starts = []
    for (px, pz), c in chunks.items():
        for sid, st in c.get("structures", {}).get("starts", {}).items():
            if st.get("id", "INVALID") != "INVALID" and "vividlands" in sid:
                starts.append({"structure": sid, "chunk": [px, pz]})
    for st in starts:
        if st["structure"] == "vividlands:viking_village":
            targets.append(("natural", st["structure"], st["chunk"][0] * 16 + 8, st["chunk"][1] * 16 + 8, 0))
    ents = entity_list(world)
    summary = {"targets": [], "natural_starts": {}, "failures": failures}
    for s in starts:
        summary["natural_starts"][s["structure"]] = summary["natural_starts"].get(s["structure"], 0) + 1
    for kind, name, x, z, dist in targets:
        res = volume(chunks, x, z, 92 if "village" in name else R)
        near = [e for e in ents if e[1] and abs(e[1][0] - x) <= R and abs(e[1][2] - z) <= R]
        counts = {}
        for eid, _ in near:
            counts[eid] = counts.get(eid, 0) + 1
        entry = {"how": kind, "structure": name, "x": x, "z": z, "distance": dist, "entities": counts,
                 "generated": res is not None}
        if res is not None:
            vol, names, origin = res
            short = name.split(":")[1]
            fname = f"struct_{kind}_{short}.png"
            render(vol, names, out / fname, f"{name} ({kind}) at {x}, {z}")
            if "village" in name:
                np.savez_compressed(out / f"vol_{kind}_{short}.npz", vol=vol, origin=np.array(origin))
                (out / f"vol_{kind}_{short}.json").write_text(json.dumps(names))
            entry["image"] = fname
            entry["block_types"] = sorted({names[i] for i in np.unique(vol)} - AIRS)[:60]
        summary["targets"].append(entry)
    (out / "structures.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "targets"}, indent=2))
    for t in summary["targets"]:
        print(t["how"], t["structure"], t["x"], t["z"], "generated" if t["generated"] else "not generated",
              t["entities"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
