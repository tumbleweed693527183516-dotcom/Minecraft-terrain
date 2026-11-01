"""
Repaints the Chapter 1 boss textures with irregular, non-repeating detail.

Every texel is mapped back to its 3D point on the model and the detail is sampled from 3D noise there, so
patterns run continuously across faces and cubes instead of the same tile repeating on every face. On top of
that each boss gets its own features: patches, scars, mud, frost, wrinkles, scales, saddle, countershading.

Base colours come from the current texture (each face's mean), so the palette stays the one from Blockbench.
Eyes and other tiny/saturated details are left alone.

    python3 tools/boss_paint.py            # all bosses
    python3 tools/boss_paint.py cave_bear  # one
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "ragnarok/src/main/resources/assets/vividlands_ragnarok"
GEO = ROOT / "geo/entity/boss"
TEX = ROOT / "textures/entity/boss"
BASE = Path(__file__).resolve().parent / "models/bosses/base_tex"   # flat Blockbench paint the detail goes on


# ---------------------------------------------------------------- noise
def _hash(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise(p, seed):
    """Smooth 3D value noise in [-1, 1]. p: (..., 3)."""
    f = np.floor(p)
    t = p - f
    t = t * t * (3 - 2 * t)
    i = f.astype(np.int64)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[..., 0] if dx else 1 - t[..., 0]) * (t[..., 1] if dy else 1 - t[..., 1]) * (t[..., 2] if dz else 1 - t[..., 2])
                out = out + w * _hash(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out * 2 - 1


def fbm(p, seed, octaves=4):
    s, a, n = 0, 0.5, 0
    for o in range(octaves):
        s = s + a * vnoise(p * (2 ** o), seed + o * 17)
        n += a
        a *= 0.5
    return s / n


def voronoi(p, seed, cells=False):
    """F1, F2 distances to jittered cell points (and with cells=True the nearest cell's random id and centre)."""
    f = np.floor(p).astype(np.int64)
    d1 = np.full(p.shape[:-1], 9.0)
    d2 = np.full(p.shape[:-1], 9.0)
    cid = np.zeros(p.shape[:-1])
    cen = np.zeros(p.shape)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = f + np.array([dx, dy, dz])
                jit = np.stack([_hash(c[..., 0], c[..., 1], c[..., 2], seed + k) for k in range(3)], -1)
                q = c + jit
                d = np.linalg.norm(q - p, axis=-1)
                closer = d < d1
                d2 = np.where(closer, d1, np.minimum(d2, d))
                if cells:
                    cid = np.where(closer, _hash(c[..., 0], c[..., 1], c[..., 2], seed + 7), cid)
                    cen = np.where(closer[..., None], q, cen)
                d1 = np.minimum(d1, d)
    return (d1, d2, cid, cen) if cells else (d1, d2)


def texel_hash(P, seed):
    q = np.floor(P * 4.0 + 0.5).astype(np.int64)
    return _hash(q[..., 0], q[..., 1], q[..., 2], seed) * 2 - 1


# ---------------------------------------------------------------- geometry -> texels
def faces_of(geo, ppu):
    """Yields (face_name, cube, bone, texel rect, 3D points (h, w, 3), normal)."""
    g = geo["minecraft:geometry"][0]
    for b in g["bones"]:
        for c in b.get("cubes", []):
            uv = c.get("uv")
            if not isinstance(uv, dict):
                continue
            x0, y0, z0 = c["origin"]
            sx, sy, sz = c["size"]
            for name, f in uv.items():
                (u, v), (w, h) = f["uv"], f["uv_size"]
                u0, u1 = sorted((u, u + w))
                v0, v1 = sorted((v, v + h))
                px0, px1 = int(round(u0 * ppu)), int(round(u1 * ppu))
                py0, py1 = int(round(v0 * ppu)), int(round(v1 * ppu))
                W, H = px1 - px0, py1 - py0
                if W <= 0 or H <= 0:
                    continue
                a = (np.arange(W) + 0.5) / W
                bb = (np.arange(H) + 0.5) / H
                if w < 0:
                    a = a[::-1]
                if h < 0:
                    bb = bb[::-1]
                A, B = np.meshgrid(a, bb)
                if name == "north":
                    P = np.stack([x0 + A * sx, y0 + sy - B * sy, np.full_like(A, z0)], -1); n = (0, 0, -1)
                elif name == "south":
                    P = np.stack([x0 + sx - A * sx, y0 + sy - B * sy, np.full_like(A, z0 + sz)], -1); n = (0, 0, 1)
                elif name == "east":
                    P = np.stack([np.full_like(A, x0), y0 + sy - B * sy, z0 + sz - A * sz], -1); n = (-1, 0, 0)
                elif name == "west":
                    P = np.stack([np.full_like(A, x0 + sx), y0 + sy - B * sy, z0 + A * sz], -1); n = (1, 0, 0)
                elif name == "up":
                    P = np.stack([x0 + A * sx, np.full_like(A, y0 + sy), z0 + B * sz], -1); n = (0, 1, 0)
                else:
                    P = np.stack([x0 + A * sx, np.full_like(A, y0), z0 + B * sz], -1); n = (0, -1, 0)
                yield name, c, b, (px0, py0, px1, py1), P, n


def classify(rgb, area, thin=99, mid=99):
    r, g, b = rgb
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    mx, mn = max(rgb), min(rgb)
    sat = (mx - mn) / (mx + 1e-6)
    if area < 1.6:
        return "detail"                       # eyes, nostrils, tiny bits
    if area < 8 and ((r > 180 and g > 110 and b < 90 and sat > 0.5) or (sat > 0.7 and lum > 90)):
        return "detail"                       # glowing / bright eyes
    if lum > 165 and sat < 0.35 and thin <= 3.5 and mid <= 3.5:
        return "ivory"
    if lum < 38 and area < 40:
        return "dark"
    if r > 1.8 * g and r > 1.6 * b and r > 90:
        return "mouth"
    return "hide"


# ---------------------------------------------------------------- per-boss looks
LOOKS = {
    "cave_bear": dict(kind="fur", seed=11, strand=0.55, patch=("#3a2414", "#8a5a2c"), tips="#c79a62", tips_amt=0.10,
                      scars=7, dark_legs=0.35, mud=0.25),
    "irish_elk": dict(kind="short", seed=23, strand=0.25, patch=("#4a2e18", "#9a6a3c"), mane="#2e1d10", rump="#d9c39a",
                      scars=3, dark_legs=0.3, dapple=0.12),
    "hippo": dict(kind="skin", seed=31, wrinkle=0.6, patch=("#4a3a3e", "#9a6f74"), blush="#c98b86", scars=14, mud=0.55),
    "crocodile": dict(kind="scales", seed=41, patch=("#2a3518", "#5d6a2c"), belly="#c9b77a", moss="#4f6b23", scars=6, mud=0.3),
    "silverback": dict(kind="fur", seed=53, strand=0.35, patch=("#141416", "#3a3836"), saddle="#a8a8aa", scars=5, dark_legs=0.1),
    "saber_tooth": dict(kind="short", seed=61, strand=0.2, patch=("#8a5a26", "#c9914a"), stripes="#4a2e14", belly_light="#e8d8b8",
                        scars=6, dark_legs=0.2),
    "woolly_rhino": dict(kind="fur", seed=71, strand=0.85, patch=("#3b2615", "#7a5230"), frost="#e6eef2", frost_amt=0.35,
                         scars=5, dark_legs=0.4, mud=0.4, matted=0.3),
    "elephant": dict(kind="skin", seed=83, wrinkle=0.85, patch=("#4a4a4c", "#8e8a86"), dust="#b49a78", scars=10, mud=0.5, cracks=True),
    "bull_shark": dict(kind="shark", seed=97, patch=("#4f5a63", "#8a979f"), belly="#e8ecec", scars=12),
    "mammoth": dict(kind="fur", seed=101, strand=1.0, patch=("#2e1a0e", "#7a4a22"), frost="#eef4f6", frost_amt=0.45,
                    tips="#a8743c", tips_amt=0.12, scars=6, dark_legs=0.45, matted=0.45),
}


def hexrgb(s):
    return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)


def mix(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return a * (1 - t) + b * t


def scar_mask(P, scars):
    m = np.zeros(P.shape[:-1])
    for a, b, w in scars:
        ab = b - a
        t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(P - (a + t[..., None] * ab), axis=-1)
        m = np.maximum(m, np.clip(1 - d / w, 0, 1))
    return m


def paint(boss):
    look = LOOKS[boss]
    geo = json.loads((GEO / f"{boss}.geo.json").read_text())
    desc = geo["minecraft:geometry"][0]["description"]
    img = Image.open(BASE / f"{boss}.png").convert("RGBA")
    src = np.asarray(img).astype(float)
    out = src.copy()
    ppu = img.size[0] / desc["texture_width"]
    rng = np.random.default_rng(look["seed"])
    seed = look["seed"]

    faces = list(faces_of(geo, ppu))
    # model bounds from the hide faces
    allp = np.concatenate([f[4].reshape(-1, 3) for f in faces])
    lo, hi = allp.min(0), allp.max(0)
    height = hi[1] - lo[1]

    # scars: random strokes across the big hide areas (front half and flanks)
    hide_pts = []
    for name, c, b, rect, P, n in faces:
        x0, y0, x1, y1 = rect
        mean = src[y0:y1, x0:x1, :3].reshape(-1, 3).mean(0)
        if classify(mean, c["size"][0] * c["size"][1] * c["size"][2] ** 0) == "hide" and name in ("east", "west", "north", "up"):
            if P.shape[0] * P.shape[1] > 60:
                hide_pts.append((P, np.array(n, float)))
    scars = []
    for _ in range(look.get("scars", 0)):
        if not hide_pts:
            break
        P, n = hide_pts[rng.integers(len(hide_pts))]
        p = P[rng.integers(P.shape[0]), rng.integers(P.shape[1])]
        d = rng.normal(size=3)
        d -= n * (d @ n)
        d /= np.linalg.norm(d) + 1e-9
        L = rng.uniform(2.5, 7.0)
        for k in range(rng.integers(1, 4)):            # claw marks come in sets
            off = np.cross(d, n) * k * rng.uniform(0.9, 1.4)
            scars.append((p + off, p + off + d * L * rng.uniform(0.7, 1.1), rng.uniform(0.28, 0.45)))

    c_dark, c_light = hexrgb(look["patch"][0]), hexrgb(look["patch"][1])

    for name, c, b, rect, P, n in faces:
        x0, y0, x1, y1 = rect
        region = src[y0:y1, x0:x1]
        if region[..., 3].max() == 0:
            continue
        base = region[..., :3].reshape(-1, 3).mean(0)
        sizes = sorted(c["size"])
        kind = classify(base, sizes[1] * sizes[2], sizes[0], sizes[1])
        if kind == "detail":
            continue
        yrel = (P[..., 1] - lo[1]) / max(height, 1)    # 0 at feet .. 1 at top
        nrm = np.array(n, float)

        if kind == "ivory":
            g = fbm(P * np.array([2.5, 0.6, 2.5]) * 0.6, seed + 5, 3)
            rings = np.sin(P[..., 2] * 2.2 + P[..., 1] * 1.3 + fbm(P * 0.5, seed + 6, 2) * 3)
            col = base * (0.9 + 0.08 * g + 0.04 * rings)[..., None]
            stain = np.clip(fbm(P * 0.35, seed + 7, 3) * 1.5 - 0.1, 0, 1) * 0.35
            col = mix(col, np.array([150, 120, 80.0]), stain)
            chips = (vnoise(P * 3.1, seed + 8) > 0.78)
            col = np.where(chips[..., None], col * 0.82, col)
        elif kind == "dark":
            col = base * (0.85 + 0.25 * (fbm(P * 1.3, seed + 9, 3) + 1) / 2)[..., None]
        elif kind == "mouth":
            col = base * (0.85 + 0.25 * (fbm(P * 1.1, seed + 10, 3) + 1) / 2)[..., None]
        else:
            # --- hide: keep the face's own colour but pull it toward this boss's palette with big irregular patches
            big = fbm(P * 0.08, seed, 4)                    # body-scale blotches
            mid = fbm(P * 0.33, seed + 1, 4)
            fine = (vnoise(P * 2.7, seed + 2) + vnoise(P * 5.3, seed + 3) * 0.5) / 1.5
            pal = mix(c_dark, c_light, 0.5 + big * 1.4 + mid * 0.5)
            col = mix(np.broadcast_to(base, pal.shape), pal, np.full(pal.shape[:-1], 0.6))
            shade = 1 + 0.14 * mid + 0.08 * fine
            k = look["kind"]
            if k in ("fur", "short"):
                # tufts: irregular clumps, each with its own shade, lit at the top and shadowed at the bottom edge
                ts = np.array([0.6, 0.3, 0.6]) if k == "fur" else np.array([0.9, 0.7, 0.9])
                warp = np.stack([fbm(P * 0.3, seed + 4 + i, 2) for i in range(3)], -1) * 0.9
                f1, f2, cid, cen = voronoi(P * ts + warp, seed + 15, cells=True)
                inner = (P * ts + warp)[..., 1] - cen[..., 1]
                shade = shade + 0.20 * (cid - 0.5) + 0.12 * np.clip(inner * 1.4, -1, 1)
                shade = shade - 0.18 * np.clip(1 - (f2 - f1) / 0.14, 0, 1)
                sp = P * np.array([4.0, 0.35 if k == "fur" else 1.0, 4.0])
                sp[..., 0] += warp[..., 0] * 3
                sp[..., 2] += warp[..., 2] * 3
                strands = vnoise(sp, seed + 12) * 0.6 + vnoise(sp * 2.1, seed + 13) * 0.4
                shade = shade + (0.10 + look.get("strand", 0.5) * 0.16) * strands
                clumps = np.clip(fbm(P * np.array([0.5, 0.12, 0.5]), seed + 14, 3), 0, 1)
                shade = shade - look.get("matted", 0) * 0.35 * clumps
            shade = shade + 0.07 * texel_hash(P, seed + 16)
            if k == "skin":
                wr = np.abs(fbm(P * np.array([0.9, 0.35, 0.9]), seed + 20, 4))
                creases = np.clip(1 - wr / 0.08, 0, 1) * look.get("wrinkle", 0.5)
                shade = shade - 0.38 * creases
                f1, f2 = voronoi(P * 0.9, seed + 23)
                shade = shade - 0.10 * np.clip(1 - (f2 - f1) / 0.1, 0, 1)
                pores = vnoise(P * 4.4, seed + 21) > 0.72
                shade = shade - 0.05 * pores
                if look.get("cracks"):
                    f1, f2 = voronoi(P * 0.55, seed + 22)
                    shade = shade - 0.18 * np.clip(1 - (f2 - f1) / 0.08, 0, 1) * (yrel < 0.55)
            if k == "scales":
                f1, f2 = voronoi(P * np.array([0.75, 0.9, 0.55]), seed + 30)
                edge = np.clip(1 - (f2 - f1) / 0.12, 0, 1)
                bump = np.clip(1 - f1 / 0.7, 0, 1)
                shade = shade - 0.32 * edge + 0.10 * bump
                top = nrm[1] > 0.5
                if top:                                     # osteoderm ridges along the back
                    rid = np.abs(np.sin(P[..., 0] * 1.3 + fbm(P * 0.3, seed + 31, 2) * 2))
                    shade = shade - 0.12 * (rid < 0.25)
            col = col * shade[..., None]

            # --- features
            if "tips" in look:
                fl = (vnoise(P * np.array([4.5, 1.2, 4.5]), seed + 40) > 1 - 2 * look["tips_amt"]) & (fbm(P * 0.15, seed + 41, 3) > -0.1)
                col = np.where(fl[..., None], mix(col, hexrgb(look["tips"]), np.full(fl.shape, 0.6)), col)
            if "dark_legs" in look:
                col = col * (1 - look["dark_legs"] * np.clip((0.3 - yrel) / 0.3, 0, 1) * (0.7 + 0.3 * mid))[..., None]
            if "mane" in look:                              # elk: darker neck and chest
                t = np.clip((-P[..., 2] - 4) / 10, 0, 1) * np.clip((yrel - 0.35) / 0.3, 0, 1)
                col = mix(col, hexrgb(look["mane"]), t * (0.6 + 0.3 * mid))
            if "rump" in look:
                t = np.clip((P[..., 2] - 9) / 4 + fbm(P * 0.4, seed + 42, 3), 0, 1) * (yrel > 0.45)
                col = mix(col, hexrgb(look["rump"]), t * 0.8)
            if "dapple" in look:
                d1, _ = voronoi(P * 0.6, seed + 43)
                col = col * (1 + look["dapple"] * (d1 < 0.3))[..., None]
            if "saddle" in look:                            # silverback: silver back, ragged edge
                t = (yrel - 0.42) * 4 + fbm(P * 0.35, seed + 44, 4) * 1.6 + (P[..., 2] > -2) * 0.6 - 0.3
                if nrm[1] > 0.5 or nrm[2] > 0.5 or abs(nrm[0]) > 0.5:
                    gr = np.clip(t, 0, 1) * (P[..., 2] > -6)
                    silver = hexrgb(look["saddle"]) * (0.85 + 0.2 * fine)[..., None]
                    col = mix(col, silver, gr * 0.85)
            if "stripes" in look:                           # saber-tooth: broken, warped stripes
                s = np.sin(P[..., 2] * 0.9 + fbm(P * 0.25, seed + 45, 4) * 4.5 + P[..., 1] * 0.25)
                br = fbm(P * 0.6, seed + 46, 3)
                st = (s > 0.72) & (br > -0.15) & (yrel > 0.3)
                col = np.where(st[..., None], mix(col, hexrgb(look["stripes"]), np.full(st.shape, 0.65)), col)
            if "belly_light" in look:
                t = np.clip((0.42 - yrel) * 5 + fbm(P * 0.4, seed + 47, 3), 0, 1) * (nrm[1] <= 0.5) * (yrel > 0.18)
                col = mix(col, hexrgb(look["belly_light"]), t * 0.6)
            if "belly" in look:                             # crocodile / shark countershading, wavy line
                wav = fbm(P * np.array([0.2, 0.1, 0.25]), seed + 48, 4) * 0.35
                cut = 0.42 if look["kind"] == "shark" else 0.2
                t = np.clip((cut - yrel + wav) * 7, 0, 1) * (nrm[1] < 0.5)
                col = mix(col, hexrgb(look["belly"]) * (0.92 + 0.1 * fine)[..., None], t * 0.9)
            if "moss" in look:
                t = np.clip(fbm(P * 0.22, seed + 49, 4) * 2 - 0.35, 0, 1) * (nrm[1] > -0.5)
                col = mix(col, hexrgb(look["moss"]), t * 0.35)
            if look["kind"] == "shark":
                d = np.clip(1 - np.abs(fbm(P * 0.6, seed + 50, 3)) / 0.03, 0, 1) * 0.25
                col = col * (1 + d)[..., None]            # faint scratches all over
            if "blush" in look:                             # hippo: pinkish skin in folds and low parts
                t = np.clip((0.5 - yrel) * 2.2 + fbm(P * 0.18, seed + 51, 3), 0, 1)
                col = mix(col, hexrgb(look["blush"]) * (shade[..., None] * 0.9), t * 0.35)
            if "dust" in look:                              # elephant: dust on the back
                t = np.clip((yrel - 0.6) * 3 + fbm(P * 0.3, seed + 52, 4) * 1.2, 0, 1)
                col = mix(col, hexrgb(look["dust"]), t * 0.4)
            if "frost" in look:                             # rime on the shoulders and back
                t = np.clip((yrel - 0.5) * 3 + fbm(P * 0.28, seed + 53, 4) * 1.8 - 0.3, 0, 1)
                fl = fbm(P * np.array([0.9, 0.35, 0.9]), seed + 54, 3) > 0.05
                col = mix(col, hexrgb(look["frost"]), t * look["frost_amt"] * (0.35 + 0.9 * fl) * (nrm[1] > -0.5))
            if "mud" in look:                               # caked mud on the legs and belly, splashes higher
                t = np.clip((0.32 - yrel) * 4 + fbm(P * 0.3, seed + 55, 4) * 1.6 - 0.2, 0, 1)
                sp = (vnoise(P * 1.7, seed + 56) > 0.62) & (yrel < 0.5)
                t = np.maximum(t, sp * 0.7)
                mud = np.array([88, 66, 44.0]) * (0.8 + 0.3 * fine)[..., None]
                col = mix(col, mud, t * look["mud"])
            if scars:
                m = scar_mask(P, scars)
                scarc = mix(col * 0.55, np.array([150, 105, 95.0]), np.full(m.shape, 0.55))
                col = mix(col, scarc, m * 0.85)

        col = np.clip(col + rng.normal(0, 2.0, col.shape), 0, 255)
        a = region[..., 3:4]
        out[y0:y1, x0:x1, :3] = np.where(a > 0, col, region[..., :3])

    Image.fromarray(out.astype(np.uint8), "RGBA").save(TEX / f"{boss}.png")
    print("painted", boss)


if __name__ == "__main__":
    for b in (sys.argv[1:] or LOOKS):
        paint(b)
