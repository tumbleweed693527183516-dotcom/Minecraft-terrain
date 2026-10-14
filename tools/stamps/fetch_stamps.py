#!/usr/bin/env python3
"""
Downloads real-world elevation for famous mountains and bakes them into "stamps":
square height grids the mod places into the world.

Source: open Terrain Tiles (Terrarium encoding) on AWS, which combine SRTM, USGS NED,
ETOPO1, EU-DEM and other open datasets. See STAMPS_ATTRIBUTION.md.

    python3 fetch_stamps.py <out dir>
Writes <out>/<name>.bin (uint16 big-endian, SIZE x SIZE), <out>/stamps.json and previews.
"""
import io
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 512                 # grid resolution of each stamp
FOOTPRINT_BLOCKS = 1400    # how wide a stamp is in Minecraft blocks (before random 0.85-1.15 scale)
DEPTH_UNIT_BLOCKS = 224    # Vivid Lands: 1.0 depth unit = 224 blocks above sea level

# name, latitude, longitude, box width (km), target relief in blocks, kind
STAMPS = [
    ("wasatch", 40.60, -111.68, 22, 320, "range"),          # rising out of the Salt Lake valley
    ("grand_teton", 43.74, -110.80, 20, 330, "range"),      # rising out of Jackson Hole
    ("sierra_whitney", 36.58, -118.25, 22, 330, "range"),   # east face above Owens Valley
    ("matterhorn", 45.976, 7.658, 16, 340, "horn"),
    ("eiger_jungfrau", 46.55, 7.98, 18, 330, "range"),
    ("dolomites_sella", 46.52, 11.78, 18, 270, "spires"),
    ("fitz_roy", -49.27, -73.04, 18, 320, "spires"),
    ("ama_dablam", 27.86, 86.86, 18, 340, "horn"),
    ("mount_fuji", 35.36, 138.73, 36, 330, "volcano"),
    ("mount_rainier", 46.853, -121.76, 30, 340, "volcano"),
    ("eyjafjallajokull", 63.63, -19.62, 26, 220, "volcano"),
    ("glen_coe", 56.66, -4.98, 16, 230, "highland"),
]

TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"


def tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def fetch_tile(z, x, y):
    with urllib.request.urlopen(TILE_URL.format(z=z, x=x, y=y), timeout=60) as r:
        rgb = np.asarray(Image.open(io.BytesIO(r.read())).convert("RGB")).astype(np.float64)
    return rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768


def build(name, lat, lon, width_km, relief_blocks, kind):
    # pick a zoom giving roughly 700-1400 source pixels across the box
    z = 12
    while True:
        m_per_px = 156543.03392 * math.cos(math.radians(lat)) / 2 ** z
        if width_km * 1000 / m_per_px < 1400 or z <= 9:
            break
        z -= 1
    half_px = width_km * 1000 / m_per_px / 2
    cx, cy = tile_xy(lat, lon, z)
    px0, py0 = cx * 256 - half_px, cy * 256 - half_px
    tx0, ty0 = int(px0 // 256), int(py0 // 256)
    tx1, ty1 = int((px0 + 2 * half_px) // 256), int((py0 + 2 * half_px) // 256)
    mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = fetch_tile(z, tx, ty)
    ox, oy = px0 - tx0 * 256, py0 - ty0 * 256
    crop = mosaic[int(oy):int(oy + 2 * half_px), int(ox):int(ox + 2 * half_px)]
    grid = np.asarray(Image.fromarray(crop.astype(np.float32), "F").resize((SIZE, SIZE), Image.BICUBIC), np.float64)

    # relative to the valley floor, feathered into flat ground toward the edges
    base = np.percentile(grid, 4)
    rel = np.clip(grid - base, 0, None)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    r = np.hypot(xx - (SIZE - 1) / 2, yy - (SIZE - 1) / 2) / (SIZE / 2)
    t = np.clip((r - 0.62) / 0.36, 0, 1)
    feather = 1 - t * t * (3 - 2 * t)
    rel *= feather
    relief_m = float(rel.max())
    norm = rel / relief_m
    (OUT / f"{name}.bin").write_bytes(np.round(norm * 65535).astype(">u2").tobytes())
    prev = (np.clip(norm, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(prev).save(OUT / f"{name}_preview.png")
    meta = {"name": name, "file": f"{name}.bin", "size": SIZE, "kind": kind,
            "blocks_per_px": FOOTPRINT_BLOCKS / SIZE, "height_units": relief_blocks / DEPTH_UNIT_BLOCKS,
            "source": {"lat": lat, "lon": lon, "width_km": width_km, "zoom": z, "relief_m": round(relief_m),
                       "horizontal_m_per_block": round(width_km * 1000 / FOOTPRINT_BLOCKS, 1),
                       "vertical_m_per_block": round(relief_m / relief_blocks, 1)}}
    print(f"{name:18s} zoom {z}  relief {relief_m:6.0f} m -> {relief_blocks} blocks  "
          f"(h {meta['source']['horizontal_m_per_block']} m/block, v {meta['source']['vertical_m_per_block']} m/block)")
    return meta


if __name__ == "__main__":
    OUT = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    metas = [build(*s) for s in STAMPS]
    (OUT / "stamps.json").write_text(json.dumps(metas, indent=2))
