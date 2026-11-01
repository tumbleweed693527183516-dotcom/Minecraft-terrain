"""
Minecraft-style boss textures: one flat colour per model unit (the 16x look, even though the files are 64x),
a handful of shades per material, and a few simple, readable markings per boss: lighter belly, darker feet,
a stripe or patch. Detail still comes from the 3D position so neighbouring faces line up, but it stays chunky.

    python3 tools/boss_paint_mc.py            # all bosses
    python3 tools/boss_paint_mc.py cave_bear  # one
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boss_paint import BASE, GEO, TEX, _hash, classify, faces_of, fbm, hexrgb  # noqa: E402

LEVELS = np.array([0.80, 0.90, 1.0, 1.0, 1.0, 1.09, 1.17])   # base shade appears most often

LOOKS = {
    "cave_bear":    dict(seed=11, fur=True, belly="#7a5634", feet=0.75, muzzle="#8a6a48"),
    "irish_elk":    dict(seed=23, fur=True, belly="#b89a70", feet=0.7, rump="#d8c49c", mane="#4a3220"),
    "hippo":        dict(seed=31, belly="#a8787a", feet=0.85, spots="#5a4448"),
    "crocodile":    dict(seed=41, scales=True, belly="#b8aa72", feet=0.85),
    "silverback":   dict(seed=53, fur=True, saddle="#8e8e92", feet=0.8),
    "saber_tooth":  dict(seed=61, fur=True, belly="#e2d2b0", stripes="#7a4a1e", feet=0.85),
    "woolly_rhino": dict(seed=71, fur=True, belly="#5a3a20", feet=0.75, snow="#e8eef0"),
    "elephant":     dict(seed=83, belly="#6e6a68", feet=0.85, spots="#5e5a58"),
    "bull_shark":   dict(seed=97, belly="#e4e8e8", shark=True),
    "mammoth":      dict(seed=101, fur=True, belly="#4a2c16", feet=0.75, snow="#e8eef0"),
}


def blocks(P, ppu):
    """The 3D point at the centre of each model-unit block of the face, so every block is one flat colour."""
    h, w = P.shape[:2]
    jj = np.minimum((np.arange(h) // ppu) * ppu + ppu // 2, h - 1)
    ii = np.minimum((np.arange(w) // ppu) * ppu + ppu // 2, w - 1)
    return P[jj][:, ii]


def cell_hash(Ps, seed):
    q = np.floor(Ps * 1.0 + 1e-3).astype(np.int64)
    return _hash(q[..., 0], q[..., 1], q[..., 2], seed)


def shade_of(Ps, seed, rough=1.0):
    v = 0.55 * (fbm(Ps * 0.18, seed, 2) * 0.5 + 0.5) + 0.45 * cell_hash(Ps, seed + 3)
    v = 0.5 + (v - 0.5) * rough
    return LEVELS[np.clip((v * len(LEVELS)).astype(int), 0, len(LEVELS) - 1)]


def paint(boss):
    look = LOOKS[boss]
    seed = look["seed"]
    geo = json.loads((GEO / f"{boss}.geo.json").read_text())
    desc = geo["minecraft:geometry"][0]["description"]
    img = Image.open(BASE / f"{boss}.png").convert("RGBA")
    src = np.asarray(img).astype(float)
    out = src.copy()
    ppu = int(round(img.size[0] / desc["texture_width"]))
    faces = list(faces_of(geo, ppu))
    allp = np.concatenate([f[4].reshape(-1, 3) for f in faces])
    lo, hi = allp.min(0), allp.max(0)
    height = hi[1] - lo[1]

    # one colour per cube (the average of its faces), so the flat Blockbench paint loses its baked side shading
    cube_col = {}
    for name, c, b, (x0, y0, x1, y1), P, n in faces:
        reg = src[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        if m.any():
            cube_col.setdefault(id(c), []).append(reg[..., :3][m].mean(0))
    cube_col = {k: np.mean(v, 0) for k, v in cube_col.items()}

    for name, c, b, (x0, y0, x1, y1), P, n in faces:
        reg = src[y0:y1, x0:x1]
        if reg[..., 3].max() == 0:
            continue
        face_mean = reg[..., :3][reg[..., 3] > 0].mean(0)
        sz = sorted(c["size"])
        kind = classify(face_mean, sz[1] * sz[2], sz[0], sz[1])
        if kind == "detail":
            continue
        base = cube_col[id(c)]
        Ps = blocks(P, ppu)
        yrel = (Ps[..., 1] - lo[1]) / max(height, 1)
        nrm = np.array(n)
        col = np.broadcast_to(base, Ps.shape).copy()

        if kind == "ivory":
            col *= np.where(cell_hash(Ps, seed + 5) > 0.8, 0.9, 1.0)[..., None]
            col *= np.where(nrm[1] > 0.5, 1.05, 1.0)
        elif kind in ("dark", "mouth"):
            col *= shade_of(Ps, seed + 6, 0.5)[..., None]
        else:
            col *= shade_of(Ps, seed, 1.0 if look.get("fur") else 0.7)[..., None]
            if look.get("fur") and nrm[1] < 0.5:      # a few 1-unit drips of darker fur on the sides
                drip = (cell_hash(np.stack([Ps[..., 0], np.floor(Ps[..., 1] / 2), Ps[..., 2]], -1), seed + 7) > 0.86)
                col = np.where(drip[..., None], col * 0.86, col)
            if look.get("scales"):                    # classic offset rows of darker scale pixels on top and sides
                row = np.floor(Ps[..., 1] + Ps[..., 0] * 0) + np.floor(Ps[..., 2] / 2)
                chk = ((np.floor(Ps[..., 0] + Ps[..., 2]) + row) % 3 == 0) & (yrel > 0.25)
                col = np.where(chk[..., None], col * 0.82, col)
                if nrm[1] > 0.5:
                    ridge = (np.abs(Ps[..., 0]) < 1.6) & (np.floor(Ps[..., 2]) % 2 == 0)
                    col = np.where(ridge[..., None], col * 0.75, col)
            if "belly" in look and nrm[1] <= 0.5 and not b["name"].startswith("leg"):
                cut = 0.38 if look.get("shark") else 0.3
                jag = (cell_hash(np.stack([Ps[..., 0], Ps[..., 2] * 0, Ps[..., 2]], -1), seed + 8) > 0.5) * 0.04
                if nrm[1] < -0.5:
                    t = np.ones(Ps.shape[:2]) * (yrel < 0.6)
                else:
                    t = (yrel < cut + jag) & (yrel > (0.0 if look.get("shark") else 0.16))
                bel = hexrgb(look["belly"]) * shade_of(Ps, seed + 9, 0.6)[..., None]
                col = np.where(t[..., None] > 0, bel, col)
            if "feet" in look:                        # bottom unit of each leg a shade darker
                col = np.where((Ps[..., 1] - lo[1] < 1.0)[..., None], col * look["feet"], col)
            if "rump" in look:
                t = (Ps[..., 2] > 9) & (yrel > 0.5)
                col = np.where(t[..., None], hexrgb(look["rump"]) * shade_of(Ps, seed + 10, 0.5)[..., None], col)
            if "mane" in look:
                t = (Ps[..., 2] < -6) & (yrel > 0.45) & (yrel < 0.72)
                col = np.where(t[..., None], hexrgb(look["mane"]) * shade_of(Ps, seed + 11)[..., None], col)
            if "saddle" in look:
                edge = (cell_hash(np.stack([Ps[..., 0], Ps[..., 1] * 0, Ps[..., 2]], -1), seed + 12) > 0.5) * 0.04
                t = (yrel > 0.55 + edge) & (Ps[..., 2] > -4) & (nrm[2] > -0.5)
                col = np.where(t[..., None], hexrgb(look["saddle"]) * shade_of(Ps, seed + 13, 0.6)[..., None], col)
            if "stripes" in look and yrel.mean() > 0.3:
                band = (np.floor(Ps[..., 2] + 40) % 4 == 0)
                gap = cell_hash(np.stack([np.floor(Ps[..., 2]), np.floor(Ps[..., 1] / 2), Ps[..., 0] * 0], -1), seed + 14) > 0.3
                t = band & gap & (yrel > 0.42)
                col = np.where(t[..., None], hexrgb(look["stripes"]) * 1.0, col)
            if "spots" in look:
                t = (cell_hash(Ps, seed + 15) > 0.93) & (yrel > 0.3)
                col = np.where(t[..., None], hexrgb(look["spots"]), col)
            if "snow" in look and nrm[1] > 0.5:        # a dusting of snow on top
                t = cell_hash(Ps, seed + 16) > 0.55
                col = np.where(t[..., None], hexrgb(look["snow"]) * shade_of(Ps, seed + 17, 0.4)[..., None], col)
            if "snow" in look and nrm[1] <= 0.5:
                t = (cell_hash(Ps, seed + 18) > 0.8) & (Ps[..., 1] > hi[1] - 2.5)
                col = np.where(t[..., None], hexrgb(look["snow"]), col)
            if look.get("shark") and nrm[1] > 0.5:
                col = col * 0.92

        a = reg[..., 3:4]
        out[y0:y1, x0:x1, :3] = np.where(a > 0, np.clip(col, 0, 255), reg[..., :3])

    Image.fromarray(out.astype(np.uint8), "RGBA").save(TEX / f"{boss}.png")
    print("painted", boss)


if __name__ == "__main__":
    for b in (sys.argv[1:] or LOOKS):
        paint(b)
