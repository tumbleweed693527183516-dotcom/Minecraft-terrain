"""
Mob kit: builds a GeckoLib boss model, its Minecraft-style texture and glow mask from a small Python spec, with no
Blockbench needed. Used for the Chapter 2 bosses (tools/ch2_models.py); the same look as the Chapter 1 repaint
(tools/boss_paint_mc.py): one flat colour per model unit, a few shades per material, simple readable markings.

Spec (geo coordinates: 1 unit = 1 pixel, y up, the mob faces -z, ground at y=0):
    m = Model("fenrir", tex_w=256)
    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-4, 10, -9), (4, 18, 9), "fur")
    m.cube("head", ..., "bone", rot=(20, 0, 0), pivot=(...))   # cube rotation, degrees; +X tips the front down
    m.sym(...)  # same as cube, plus its mirror image on the other side (x -> -x)
    m.material("fur", "#2b2b30", style="fur")
    m.save()  -> geo/entity/boss/<id>.geo.json, textures/entity/boss/<id>.png (+ _glowmask.png when glowing)

Texture: tex_w units wide, PPU (4) pixels per unit, so the files match the Chapter 1 bosses (64x files, painted
in 1-unit blocks so they read as 16x).
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "ragnarok/src/main/resources/assets/vividlands_ragnarok"
GEO = ROOT / "geo/entity/boss"
TEX = ROOT / "textures/entity/boss"
PPU = 4
LEVELS = np.array([0.80, 0.90, 1.0, 1.0, 1.0, 1.09, 1.17])


# ---------------------------------------------------------------- noise helpers
def _hash(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def cell(P, seed, scale=(1, 1, 1)):
    q = np.floor(P / np.array(scale, float) + 1e-3).astype(np.int64)
    return _hash(q[..., 0], q[..., 1], q[..., 2], seed)


def smooth(P, seed, size=5.0):
    """Blocky low-frequency value noise in [0,1] (bilinear between cells of `size` units)."""
    p = P / size
    f = np.floor(p)
    t = p - f
    i = f.astype(np.int64)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[..., 0] if dx else 1 - t[..., 0]) * (t[..., 1] if dy else 1 - t[..., 1]) * (t[..., 2] if dz else 1 - t[..., 2])
                out = out + w * _hash(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz, seed)
    return out


def shade(P, seed, rough=1.0):
    v = 0.55 * smooth(P, seed) + 0.45 * cell(P, seed + 3)
    v = 0.5 + (v - 0.5) * rough
    return LEVELS[np.clip((v * len(LEVELS)).astype(int), 0, len(LEVELS) - 1)]


def hexrgb(s):
    return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)


# ---------------------------------------------------------------- model
class Model:
    def __init__(self, ident, tex_w=256, seed=1):
        self.id = ident
        self.tex_w = tex_w
        self.seed = seed
        self.bones = []          # dicts in geo format
        self.cubes = []          # (bone, from, to, mat, rot, pivot, inflate)
        self.mats = {}
        self.look = {}

    # -- building
    def bone(self, name, parent, pivot, rot=None):
        b = {"name": name, "pivot": [float(v) for v in pivot]}
        if parent:
            b["parent"] = parent
        if rot:
            b["rotation"] = [float(v) for v in rot]
        self.bones.append(b)

    def cube(self, bone, a, b, mat, rot=None, pivot=None, inflate=0.0):
        a, b = np.minimum(a, b).tolist(), np.maximum(a, b).tolist()
        self.cubes.append((bone, a, b, mat, rot, pivot, inflate))

    def sym(self, bone, a, b, mat, rot=None, pivot=None, inflate=0.0, mbone=None):
        """Cube plus its mirror (x -> -x). Rotations about Y and Z flip sign in the mirror."""
        self.cube(bone, a, b, mat, rot, pivot, inflate)
        ma, mb = (-b[0], a[1], a[2]), (-a[0], b[1], b[2])
        mrot = None if rot is None else (rot[0], -rot[1], -rot[2])
        mpiv = None if pivot is None else (-pivot[0], pivot[1], pivot[2])
        self.cube(mbone or bone, ma, mb, mat, mrot, mpiv, inflate)

    def material(self, name, color, style="plain", **kw):
        self.mats[name] = dict(color=color, style=style, **kw)

    # -- uv packing (per face, shelf packed, 1-unit grid)
    def _pack(self):
        rects = []
        for ci, (bone, a, b, mat, rot, piv, inf) in enumerate(self.cubes):
            sx, sy, sz = (max(1, math.ceil(b[i] - a[i] - 1e-6)) for i in range(3))
            for face, (w, h) in (("north", (sx, sy)), ("south", (sx, sy)), ("east", (sz, sy)), ("west", (sz, sy)),
                                 ("up", (sx, sz)), ("down", (sx, sz))):
                rects.append((ci, face, w, h))
        order = sorted(range(len(rects)), key=lambda i: -rects[i][3])
        x = y = shelf = 0
        place = {}
        for i in order:
            ci, face, w, h = rects[i]
            if x + w > self.tex_w:
                x, y, shelf = 0, y + shelf, 0
            place[(ci, face)] = (x, y, w, h)
            x += w
            shelf = max(shelf, h)
        th = y + shelf
        self.tex_h = 1 << max(4, math.ceil(math.log2(th)))
        return place

    def geo(self):
        place = self._pack()
        bones = {b["name"]: dict(b, cubes=[]) for b in self.bones}
        for ci, (bone, a, b, mat, rot, piv, inf) in enumerate(self.cubes):
            c = {"origin": [round(v, 3) for v in a], "size": [round(b[i] - a[i], 3) for i in range(3)], "uv": {}}
            if inf:
                c["inflate"] = inf
            if rot:
                c["rotation"] = [float(v) for v in rot]
                c["pivot"] = [float(v) for v in (piv if piv is not None else bones[bone]["pivot"])]
            for face in ("north", "east", "south", "west", "up", "down"):
                u, v, w, h = place[(ci, face)]
                if face in ("up", "down"):        # Blockbench writes these from the far corner
                    c["uv"][face] = {"uv": [u + w, v + h], "uv_size": [-w, -h]}
                else:
                    c["uv"][face] = {"uv": [u, v], "uv_size": [w, h]}
            bones[bone]["cubes"].append(c)
        out = []
        for b in bones.values():
            if not b["cubes"]:
                del b["cubes"]
            out.append(b)
        allp = np.array([p for (_, a, b, *_r) in self.cubes for p in (a, b)])
        return {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": f"geometry.{self.id}", "texture_width": self.tex_w, "texture_height": self.tex_h,
                            "visible_bounds_width": round(float(np.ptp(allp[:, [0, 2]]) / 16 + 1), 1),
                            "visible_bounds_height": round(float(allp[:, 1].max() / 16 + 1), 1),
                            "visible_bounds_offset": [0, round(float(allp[:, 1].max() / 32), 2), 0]},
            "bones": out}]}

    # -- painting
    def paint(self, geo):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from boss_paint import faces_of
        W, H = self.tex_w * PPU, self.tex_h * PPU
        img = np.zeros((H, W, 4), float)
        glow = np.zeros((H, W, 4), float)
        mats_by_cube = {}
        # bones were emitted in spec bone order, cubes grouped per bone: rebuild the cube->material map that way
        order = [cc for bn in [x["name"] for x in self.bones] for cc in self.cubes if cc[0] == bn]
        k = 0
        for b in geo["minecraft:geometry"][0]["bones"]:
            for c in b.get("cubes", []):
                mats_by_cube[id(c)] = order[k][3]
                k += 1
        allp = np.concatenate([f[4].reshape(-1, 3) for f in faces_of(geo, PPU)])
        lo, hi = allp.min(0), allp.max(0)
        L = self.look
        s0 = self.seed
        for name, c, b, (x0, y0, x1, y1), P, n in faces_of(geo, PPU):
            mat = self.mats[mats_by_cube[id(c)]]
            h, w = P.shape[:2]
            jj = np.minimum((np.arange(h) // PPU) * PPU + PPU // 2, h - 1)
            ii = np.minimum((np.arange(w) // PPU) * PPU + PPU // 2, w - 1)
            Ps = P[jj][:, ii]
            yrel = (Ps[..., 1] - lo[1]) / max(hi[1] - lo[1], 1)
            nrm = np.array(n)
            base = hexrgb(mat["color"])
            col = np.broadcast_to(base, Ps.shape).copy()
            st = mat["style"]
            seed = s0 + sum(map(ord, mats_by_cube[id(c)])) % 997
            if st in ("fur", "hide", "scales", "hair", "cloth", "plain", "membrane", "plates", "feather", "lamellar"):
                col *= shade(Ps, seed, {"fur": 1.0, "hair": 0.6, "scales": 0.7, "hide": 0.8, "feather": 0.8}.get(st, 0.5))[..., None]
            ax = int(np.argmax(np.abs(nrm)))              # the two in-face axes
            u_ax, v_ax = [i for i in range(3) if i != ax]
            if st == "plates":                        # armour plates: an offset grid of darker seams
                pu, pv = Ps[..., u_ax], Ps[..., v_ax]
                row = np.floor(pv / 3)
                seam = (np.floor(pv) % 3 == 0) | (np.floor(pu + (row % 2) * 1.5) % 3 == 0)
                col = np.where(seam[..., None], col * 0.72, col * np.where(cell(Ps, seed + 4, (3, 3, 3)) > 0.5, 1.06, 1.0)[..., None])
            if st == "feather":                       # feather rows: each row a little darker at its lower edge
                rows = np.floor(Ps[..., 1] * 0.5 + Ps[..., 2] * 0.25) if ax != 1 else np.floor(Ps[..., 2] * 0.5)
                tip = (np.floor(Ps[..., 1]) % 2 == 0) if ax != 1 else (np.floor(Ps[..., 2]) % 2 == 0)
                col = np.where((tip & (cell(np.stack([rows, Ps[..., u_ax], rows * 0], -1), seed + 6) > 0.4))[..., None], col * 0.84, col)
            if st == "fur" and nrm[1] < 0.5:
                drip = cell(np.stack([Ps[..., 0], np.floor(Ps[..., 1] / 2), Ps[..., 2]], -1), seed + 7) > 0.85
                col = np.where(drip[..., None], col * 0.85, col)
            if st == "hair":                          # long strands: columns of light and dark
                strand = cell(np.stack([Ps[..., 0] + Ps[..., 2], np.floor(Ps[..., 1] / 4), Ps[..., 0] * 0], -1), seed + 8)
                col *= np.where(strand > 0.7, 1.1, np.where(strand < 0.25, 0.86, 1.0))[..., None]
            if st == "scales":                        # offset rows of darker scales
                row = np.floor(Ps[..., 1]) + np.floor(Ps[..., 2] / 2)
                chk = (np.floor(Ps[..., 0] + Ps[..., 2]) + row) % 3 == 0
                col = np.where(chk[..., None], col * 0.82, col)
            if st == "membrane":                      # fin rays
                ray = np.floor(Ps[..., 2] + Ps[..., 1] * 0.5) % 3 == 0
                col = np.where(ray[..., None], col * 0.75, col)
            if st in ("metal", "gold"):
                col *= (0.92 + 0.12 * (cell(Ps, seed) > 0.5))[..., None]
                if nrm[1] > 0.5:
                    col *= 1.15
                elif nrm[1] < -0.5:
                    col *= 0.8
                pit = cell(Ps, seed + 9) > 0.88
                col = np.where(pit[..., None], col * 0.75, col)
            if st == "mail":                          # rings: a dark dot on every other unit, offset each row
                ring = (np.floor(Ps[..., u_ax]) + np.floor(Ps[..., v_ax])) % 2 == 0
                col *= np.where(ring, 0.78, 1.04)[..., None] * (0.95 + 0.1 * (cell(Ps, seed) > 0.5))[..., None]
                if nrm[1] > 0.5:
                    col *= 1.1
            if st == "lamellar":                      # small upright plates in rows, laced together
                pv = Ps[..., 1] if ax != 1 else Ps[..., 2]
                pu = Ps[..., u_ax] if ax != 1 else Ps[..., 0]
                row = np.floor(pv / 2)
                seam = (np.floor(pv) % 2 == 0) & (cell(np.stack([row, pu, row * 0], -1), seed + 2) > -1)
                col = np.where(seam[..., None], col * 0.7, col * np.where((np.floor(pu + row) % 2) == 0, 1.06, 0.97)[..., None])
                if mat.get("lace"):
                    lace = (np.floor(pv) % 2 == 0) & (np.floor(pu) % 2 == 0)
                    col = np.where(lace[..., None], hexrgb(mat["lace"]) * np.ones_like(col), col)
            if mat.get("band"):                       # coloured bands: (colour, period, offset)
                bc, per = mat["band"][0], mat["band"][1]
                off = mat["band"][2] if len(mat["band"]) > 2 else 0
                pv = Ps[..., 1] if ax != 1 else Ps[..., 2]
                t = (np.floor(pv) + off) % per == 0
                col = np.where(t[..., None], hexrgb(bc) * shade(Ps, seed + 30, 0.4)[..., None], col)
            if mat.get("studs"):                      # rivets / studs on a grid: (colour, spacing)
                sc, sp = mat["studs"]
                t = (np.floor(Ps[..., u_ax]) % sp == 1) & (np.floor(Ps[..., v_ax]) % sp == 1)
                col = np.where(t[..., None], hexrgb(sc) * np.ones_like(col), col)
            if mat.get("trim"):                       # a contrasting rim along the face's top and bottom edge
                pv = Ps[..., v_ax]
                edge = (pv - pv.min() < 1) | (pv.max() - pv < 1)
                if ax != 1:
                    col = np.where(edge[..., None], hexrgb(mat["trim"]) * shade(Ps, seed + 31, 0.4)[..., None], col)
            bev = mat.get("bevel", {"metal": 0.22, "gold": 0.22, "plates": 0.16, "lamellar": 0.14, "scales": 0.12,
                                    "bone": 0.14, "hide": 0.1, "cloth": 0.08, "mail": 0.1, "dark": 0.08}.get(st, 0.0))
            if bev and ax != 1 and P.shape[0] > 1:     # pixel-art bevel: lit top-left edge, shaded bottom-right edge
                pv, pu = Ps[..., 1], Ps[..., u_ax]
                top = pv.max() - pv < 1
                bot = pv - pv.min() < 1
                lft = pu - pu.min() < 1
                rgt = pu.max() - pu < 1
                if ax == 2 and nrm[2] > 0 or ax == 0 and nrm[0] < 0:
                    lft, rgt = rgt, lft
                f = np.ones(Ps.shape[:2])
                f = np.where(bot | rgt, 1 - bev, f)
                f = np.where(top | lft, 1 + bev * 0.9, f)
                col *= f[..., None]
            elif bev and ax == 1:
                col *= (1 + bev * 0.5 if nrm[1] > 0 else 1 - bev)
            if st == "bone":
                col *= np.where(cell(Ps, seed + 5) > 0.8, 0.9, 1.0)[..., None]
                if nrm[1] > 0.5:
                    col *= 1.05
            if st == "dark":
                col *= shade(Ps, seed, 0.4)[..., None]
            # model-wide markings
            mk = mat.get("marks", ())
            if "belly" in mk and nrm[1] <= 0.5 and "belly" in L:
                bel = hexrgb(L["belly"]) * shade(Ps, seed + 11, 0.6)[..., None]
                t = (yrel < L.get("belly_cut", 0.3)) if nrm[1] > -0.5 else np.ones(yrel.shape, bool)
                if L.get("belly_axis") == "local":    # serpent: underside of every segment
                    t = (Ps[..., 1] < L["belly_y"](Ps)) | (nrm[1] < -0.5)
                col = np.where(t[..., None], bel, col)
            if "back" in mk and "back" in L and nrm[1] > 0.5:
                col = hexrgb(L["back"]) * shade(Ps, seed + 12, 0.8)[..., None]
            if "dapple" in mk:
                d = (cell(Ps, seed + 13, (2, 2, 2)) > 0.72) & (cell(Ps, seed + 14) > 0.3)
                col = np.where(d[..., None], col * 1.14, col)
            if "socks" in mk and "socks" in L:
                t = Ps[..., 1] < L["socks_h"]
                col = np.where(t[..., None], hexrgb(L["socks"]) * shade(Ps, seed + 15, 0.5)[..., None], col)
            scar_px = np.zeros(Ps.shape[:2], bool)
            if "scars" in mk and "scars" in L:
                for (a, b2) in L["scars"]:
                    a, b2 = np.array(a, float), np.array(b2, float)
                    ab = b2 - a
                    t = np.clip(((Ps - a) @ ab) / (ab @ ab), 0, 1)
                    d = np.linalg.norm(Ps - (a + t[..., None] * ab), axis=-1)
                    scar_px |= d < 0.75
                col = np.where(scar_px[..., None], hexrgb(L["scar_color"]) * shade(Ps, seed + 16, 0.4)[..., None], col)
            if "stripes" in mk and "stripes" in L:   # broken bands across the body
                band = (np.floor(Ps[..., 2] + 40) % L.get("stripe_gap", 4) == 0)
                keep = cell(np.stack([np.floor(Ps[..., 2]), np.floor(Ps[..., 1] / 2), Ps[..., 0] * 0], -1), seed + 18) > 0.35
                t = band & keep & (yrel > L.get("stripe_min", 0.4))
                col = np.where(t[..., None], hexrgb(L["stripes"]) * shade(Ps, seed + 19, 0.4)[..., None], col)
            if "spots" in mk and "spots" in L:       # blotches (2x2 units) on the back and sides
                sp = (cell(Ps, seed + 20, (2, 2, 2)) > L.get("spot_rate", 0.78)) & (yrel > L.get("spot_min", 0.0))
                col = np.where(sp[..., None], hexrgb(L["spots"]) * shade(Ps, seed + 21, 0.4)[..., None], col)
            gm = np.zeros(Ps.shape[:2], bool)
            if L.get("scar_glow"):
                gm |= scar_px
            if "runes" in mk:                         # glowing rune pixels in a stepped pattern
                r = ((np.floor(Ps[..., 0] * 1 + Ps[..., 2]) + np.floor(Ps[..., 1])) % 4 == 0) & (cell(Ps, seed + 17) > 0.35)
                col = np.where(r[..., None], hexrgb(mat["rune"]), col)
                gm |= r
            if "lateral" in mk and "lateral" in L:   # a glowing line along each side (the serpent's venom line)
                t = (np.abs(nrm[0]) > 0.5) & (np.abs(Ps[..., 1] - L["lateral_y"]) < 0.6) & (cell(Ps, seed + 22) > 0.25)
                col = np.where(t[..., None], hexrgb(L["lateral"]), col)
                gm |= t
            if "coins" in mk and "coins" in L:       # gold coins stuck in the scales (Fafnir sleeps on his hoard)
                t = (cell(Ps, seed + 23) > 0.965) & (nrm[1] > -0.5)
                col = np.where(t[..., None], hexrgb(L["coins"]) * np.where(cell(Ps, seed + 24) > 0.5, 1.1, 0.9)[..., None], col)
            px = np.repeat(np.repeat(np.ones(Ps.shape[:2]), 1, 0), 1, 1)
            img[y0:y1, x0:x1, :3] = np.clip(col, 0, 255)
            img[y0:y1, x0:x1, 3] = 255 * px
            if st == "glow":
                glow[y0:y1, x0:x1, :3] = np.clip(col, 0, 255)
                glow[y0:y1, x0:x1, 3] = 255
            elif gm.any():
                glow[y0:y1, x0:x1, :3] = np.where(gm[..., None], np.clip(col, 0, 255), 0)
                glow[y0:y1, x0:x1, 3] = np.where(gm, 255, 0)
        return img.astype(np.uint8), glow.astype(np.uint8)

    def save(self, geo_dir=None, tex_dir=None, quiet=False):
        geo_dir, tex_dir = geo_dir or GEO, tex_dir or TEX
        g = self.geo()
        geo_dir.mkdir(parents=True, exist_ok=True)
        tex_dir.mkdir(parents=True, exist_ok=True)
        (geo_dir / f"{self.id}.geo.json").write_text(json.dumps(g, indent=1))
        img, glow = self.paint(g)
        Image.fromarray(img, "RGBA").save(tex_dir / f"{self.id}.png")
        gp = tex_dir / f"{self.id}_glowmask.png"
        if glow[..., 3].any():
            Image.fromarray(glow, "RGBA").save(gp)
        elif gp.exists():
            gp.unlink()
        if not quiet:
            print(f"{self.id}: {len(self.bones)} bones, {len(self.cubes)} cubes, texture {self.tex_w}x{self.tex_h}")
        return g
