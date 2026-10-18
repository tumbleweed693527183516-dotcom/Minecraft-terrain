#!/usr/bin/env python3
"""
Viking armor concepts, version 2: built at 4 voxels per Minecraft pixel, in real layers
(padding -> mail -> scales/plates -> trim, straps, trinkets), so every set is several layers deep.

    python3 tools/concept/viking_armor_v2.py  ->  docs/viking_armor/*.png
"""
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "viking_armor"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT2 = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
R = 4                                    # voxels per Minecraft pixel


# ================================================================== basics
def h(*a):
    n = 0
    for v in a:
        n = (n * 0x9E3779B1 + (int(v) & 0xFFFFFFFF) * 0x85EBCA77 + 0x165667B1) & 0xFFFFFFFF
        n ^= n >> 15
    n = (n * 0x2C1B3C6D) & 0xFFFFFFFF
    n ^= n >> 12
    return (n & 0xFFFF) / 65536.0


def vnoise(x, y, z, scale=12.0, seed=0):
    """Smooth 3D value noise in [0, 1): large, soft variation (wear, tarnish, dirt)."""
    fx, fy, fz = x / scale, y / scale, z / scale
    ix, iy, iz = math.floor(fx), math.floor(fy), math.floor(fz)
    tx, ty, tz = fx - ix, fy - iy, fz - iz
    tx, ty, tz = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty), tz * tz * (3 - 2 * tz)
    acc = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (tx if dx else 1 - tx) * (ty if dy else 1 - ty) * (tz if dz else 1 - tz)
                acc += w * h(ix + dx, iy + dy, iz + dz, seed)
    return acc


def hexc(s):
    if isinstance(s, tuple):
        return s
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mul(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


# player parts in voxels (faces +z)
HEAD = (-16, 16, 96, 128, -16, 16)
BODY = (-16, 16, 48, 96, -8, 8)
ARM_R = (16, 32, 48, 96, -8, 8)
ARM_L = (-32, -16, 48, 96, -8, 8)
LEG_R = (0, 16, 0, 48, -8, 8)
LEG_L = (-16, 0, 0, 48, -8, 8)
PARTS = (HEAD, BODY, ARM_R, ARM_L, LEG_R, LEG_L)


def inside(p, b):
    return b[0] <= p[0] < b[1] and b[2] <= p[1] < b[3] and b[4] <= p[2] < b[5]


def in_body(p):
    return any(inside(p, b) for b in PARTS)


class Model:
    def __init__(self):
        self.v = {}

    def set(self, x, y, z, c, over_body=False):
        if c is None:
            return
        if not over_body and in_body((x, y, z)):
            return
        self.v[(x, y, z)] = c

    def paint_part(self, part, mat):
        x0, x1, y0, y1, z0, z1 = part
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    self.v[(x, y, z)] = mat(x, y, z, 0)

    def sleeve(self, part, y0, y1, d0, d1, mat, bulge=None, keep=None, maxb=6):
        """Layer around a part between distance d0 (exclusive) and d1 (+bulge), over heights y0..y1."""
        x0, x1, _, _, z0, z1 = part
        for x in range(x0 - d1 - maxb, x1 + d1 + maxb):
            dx = max(x0 - x, 0, x - (x1 - 1))
            for z in range(z0 - d1 - maxb, z1 + d1 + maxb):
                dz = max(z0 - z, 0, z - (z1 - 1))
                d = max(dx, dz)
                if d <= d0 or d > d1 + maxb:
                    continue
                for y in range(y0, y1):
                    lim = d1 + (bulge(x, y, z) if bulge else 0)
                    if d > lim:
                        continue
                    if keep and not keep(x, y, z):
                        continue
                    self.set(x, y, z, mat(x, y, z, d))

    def cap(self, part, ymin, d0, d1, mat, bulge=None, keep=None, maxb=6):
        x0, x1, y0, y1, z0, z1 = part
        for x in range(x0 - d1 - maxb, x1 + d1 + maxb):
            dx = max(x0 - x, 0, x - (x1 - 1))
            for z in range(z0 - d1 - maxb, z1 + d1 + maxb):
                dz = max(z0 - z, 0, z - (z1 - 1))
                for y in range(ymin, y1 + d1 + maxb):
                    dy = max(y0 - y, 0, y - (y1 - 1))
                    d = max(dx, dy, dz)
                    if d <= d0:
                        continue
                    lim = d1 + (bulge(x, y, z) if bulge else 0)
                    if d > lim:
                        continue
                    if keep and not keep(x, y, z):
                        continue
                    self.set(x, y, z, mat(x, y, z, d))

    def box(self, x0, x1, y0, y1, z0, z1, mat, over_body=False):
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    self.set(x, y, z, mat(x, y, z, 0) if callable(mat) else mat, over_body)

    def sphere(self, cx, cy, cz, r, mat, over_body=False):
        ri = int(math.ceil(r))
        for x in range(-ri, ri + 1):
            for y in range(-ri, ri + 1):
                for z in range(-ri, ri + 1):
                    if x * x + y * y + z * z <= r * r + 0.3:
                        c = mat(cx + x, cy + y, cz + z, 0) if callable(mat) else mat
                        self.set(cx + x, cy + y, cz + z, mul(c, 1.0 + 0.04 * y), over_body)

    def tube(self, pts, radius, mat):
        """A tapered tube along a polyline: pts = [(x, y, z, r_scale), ...]."""
        for (ax, ay, az, ar), (bx, by, bz, br) in zip(pts, pts[1:]):
            n = int(max(abs(bx - ax), abs(by - ay), abs(bz - az)) * 2) + 1
            for i in range(n + 1):
                t = i / n
                x, y, z = ax + (bx - ax) * t, ay + (by - ay) * t, az + (bz - az) * t
                r = radius * (ar + (br - ar) * t)
                self.sphere(int(round(x)), int(round(y)), int(round(z)), max(0.6, r),
                            (lambda c: (lambda X, Y, Z, D: c))(mat(x, y, z, t)))


# ================================================================== materials (x, y, z, d) -> colour or None
def u_of(x, z):
    return x + z


def cloth(base, weave=0.06):
    base = hexc(base)
    return lambda x, y, z, d: mul(base, 0.93 + weave * ((x + y + z) % 2) + 0.08 * h(x // 3, y // 3, z // 3))


def quilt(base):
    base = hexc(base)

    def m(x, y, z, d):
        u = u_of(x, z)
        line = (u + y) % 8 == 0 or (u - y) % 8 == 0
        c = mul(base, 0.66 if line else 0.92 + 0.12 * h(x // 2, y // 2, z // 2))
        c = mul(c, 0.82 + 0.3 * vnoise(x, y, z, 13, 51))   # faded and stained in places
        if line and h(x, y, z) > 0.8:
            c = hexc("#d8c8a0")                            # stitches
        return c
    return m


def quilt_bulge(x, y, z):
    u = u_of(x, z)
    return 1 if (u + y) % 8 in (3, 4, 5) and (u - y) % 8 in (3, 4, 5) else 0


def skin(base="#c98f6b"):
    base = hexc(base)
    return lambda x, y, z, d: mul(base, 0.96 + 0.07 * h(x // 2, y // 2, z // 2))


def fur(base, tip=None, belly=None):
    """Flowing fur: strands run downward and wave, clumps vary in size and colour, lighter tips."""
    base = hexc(base)
    tip = hexc(tip) if tip else mul(base, 1.35)

    def m(x, y, z, d):
        warp = int(5 * vnoise(x, y, z, 9, 3) - 2.5)
        strand = h((x + warp) // 2, (z + warp) // 2, (y + int(9 * h(x // 2, z // 2))) // 8)
        clump = vnoise(x, y, z, 14, 5)
        c = mix(mul(base, 0.62 + 0.25 * clump), mul(base, 1.0 + 0.2 * clump), strand)
        return mix(c, tip, min(1.0, max(0.0, (d - 2) / 4)) * (0.35 + 0.4 * clump))
    return m


def fur_bulge(scale=1.0):
    def b(x, y, z):
        clump = vnoise(x, y, z, 10, 9)
        t = h(x // 2, z // 2, (y + int(9 * h(x // 2 + 3, z // 2))) // 9, 11)
        v = (0 if t < 0.3 else (1 if t < 0.6 else 2)) + int(3 * clump * clump)
        return int(round(v * scale))
    return b


def mail(base="#9aa0a8", under=None, rust=0.25):
    """Riveted rings with open centres (the layer below shows through), patches of rust and tarnish."""
    base = hexc(base)
    RUST = hexc("#7a4a2a")

    def m(x, y, z, d):
        u = u_of(x, z)
        row = y // 3
        uu = (u + (row % 2) * 2) % 4
        vv = y % 3
        if uu in (1, 2) and vv == 1:
            return None                                   # ring hole
        f = 1.18 if (uu == 0 or vv == 0) else 0.84
        c = mul(base, f * (0.86 + 0.22 * vnoise(x, y, z, 10, 21)))
        r = vnoise(x, y, z, 7, 22)
        if r > 1 - rust:
            c = mix(c, RUST, min(0.8, (r - (1 - rust)) * 3))
        return c
    return m


def scales(base, edge, rivet=None, w=8, ht=6, missing=0.035, tarnish=None):
    """Shingled scales. Each scale has its own tint and wear; a few are missing (the mail shows through);
    the lower rim of each scale catches the light where it is scuffed."""
    base, edge = hexc(base), hexc(edge)
    rivet = hexc(rivet) if rivet else None
    tarnish = hexc(tarnish) if tarnish else mul(base, 0.6)

    def cell(x, y, z):
        u = u_of(x, z)
        row = (y + 1000) // ht
        cu = (u + (row % 2) * (w // 2)) % w
        cv = ht - 1 - ((y + 1000) % ht)                    # 0 at the top of a scale
        sid = ((u + (row % 2) * (w // 2)) // w, row)
        return cu, cv, sid

    def m(x, y, z, d):
        cu, cv, sid = cell(x, y, z)
        own = h(sid[0], sid[1], 77)
        if own < missing:
            return None
        if cv == ht - 1 and cu in (0, w - 1):
            return mul(edge, 0.55)
        if cu == 0:
            return edge
        if rivet and cv == 1 and cu in (w // 2 - 1, w // 2):
            return rivet
        t = cv / (ht - 1)
        c = mul(base, (1.25 - 0.45 * t) * (0.85 + 0.3 * own))
        c = mix(c, tarnish, 0.5 * vnoise(x, y, z, 16, 31))
        if cv == ht - 1 and h(x, y, z) > 0.55:
            c = mul(c, 1.35)                               # scuffed rim
        return c

    def b(x, y, z):
        cu, cv, sid = cell(x, y, z)
        return -9 if h(sid[0], sid[1], 77) < missing else cv // 2
    return m, b


def plate(base, every=0, dents=True):
    """Hammered plate: soft brushed variation, darker grime patches, light scratches."""
    base = hexc(base)

    def m(x, y, z, d):
        c = mul(base, 0.88 + 0.18 * vnoise(x, y, z, 11, 41) + 0.03 * ((x + z) % 2))
        if dents and h(x // 3, y // 3, z // 3, 5) > 0.93:
            c = mul(c, 0.8)                                # dents
        sc = (u_of(x, z) * 2 + y) % 23 == 0 and h(x // 6, y // 6, 9) > 0.6
        if sc:
            c = mul(c, 1.3)                                # scratches
        return c
    return m


def knot_engraved(x, y, z):
    """Interlaced knotwork lines (engraved grooves)."""
    u = u_of(x, z)
    a = (u + int(round(3 * math.sin(y * 0.39)))) % 10
    b = (u - int(round(3 * math.sin(y * 0.39 + 1.6)))) % 10
    return a in (0, 1) or b in (0, 1)


GOLD = hexc("#d9a520")
GOLD_HI = hexc("#ffe27a")
GOLD_LO = hexc("#7a520a")
SILVER = hexc("#c8ced6")
STEEL = hexc("#6f757d")
STEEL_DARK = hexc("#3a3e44")
IRON = hexc("#8d939a")
LEATHER = hexc("#5a3a20")
LEATHER_DARK = hexc("#3a2414")
IVORY = hexc("#ece4cc")
BLACK = hexc("#141414")


def gold(engraved=True, base=GOLD):
    def m(x, y, z, d):
        if engraved and knot_engraved(x, y, z):
            return GOLD_LO
        return mul(base, 0.95 + 0.25 * h(x // 2, y // 2, z // 2))
    return m


def solid(c):
    c = hexc(c) if isinstance(c, str) else c
    return lambda x, y, z, d: c


def leather(base=LEATHER, stitch=True):
    base = hexc(base) if isinstance(base, str) else base

    def m(x, y, z, d):
        f = 0.9 + 0.16 * h(x // 3, y // 3, z // 3)
        return mul(base, f)
    return m


# ================================================================== reusable details
def face(m, beard="#7a4a22", hair="#7a4a22", eyes="#3a6fb0", beard_len=24, braids=True, beads=GOLD, woman=False):
    beard, hair, eyes = hexc(beard), hexc(hair), hexc(eyes)
    S = skin()
    m.paint_part(HEAD, S)
    zf = 15
    for x in range(-16, 16):
        for y in range(96, 128):
            c = None
            if y >= 120:
                c = mul(hair, 0.85 + 0.25 * h(x // 2, y // 2))
            # eyes: white, iris, pupil
            for ex in (-10, 6):
                if ex <= x < ex + 4 and 110 <= y < 113:
                    c = (240, 240, 240)
                    if ex + 1 <= x < ex + 3:
                        c = eyes
                    if ex + 2 == x and y == 111:
                        c = (20, 20, 30)
            if 113 <= y < 115 and (-12 <= x < -5 or 4 <= x < 11):
                c = mul(hair, 0.7)                                   # brows
            if -2 <= x < 2 and 104 <= y < 110:
                c = mul(hexc("#c98f6b"), 0.8)                         # nose
            if not woman and y < 106 and not (-5 <= x < 5 and 102 <= y < 104):
                c = mul(beard, 0.82 + 0.3 * h(x // 2, y // 2))
            if -5 <= x < 5 and 102 <= y < 104:
                c = (120, 50, 40)                                     # mouth
            if c:
                m.v[(x, y, zf)] = c
    if woman:
        return
    # moustache and beard stand out from the face
    for x in range(-12, 12):
        for y in range(104, 107):
            if abs(x) > 2:
                m.set(x, y, 16, mul(beard, 0.9 + 0.2 * h(x, y)))
    for x in range(-14, 14):
        for y in range(96 - beard_len // 2, 104):
            depth = 16 + (2 if abs(x) < 10 else 1) + (1 if y > 98 else 0)
            for z in range(16, depth):
                m.set(x, y, z, mul(beard, 0.78 + 0.35 * h(x // 2, y // 3, z)))
    if braids:
        for bx in (-6, 2):
            for y in range(96 - beard_len, 96 - beard_len // 2):
                for x in range(bx, bx + 4):
                    tw = (y + x) % 4 < 2
                    m.set(x, y, 18, mul(beard, 1.0 if tw else 0.72))
                    m.set(x, y, 17, mul(beard, 0.8))
            for y in range(96 - beard_len - 3, 96 - beard_len):
                for x in range(bx, bx + 4):
                    m.set(x, y, 18, mul(beads, 1.1 if y % 2 else 0.85))
                    m.set(x, y, 17, beads)


def belt(m, y0, y1, d0=1, d1=3, strap=LEATHER_DARK, plaques=None, buckle=IRON):
    m.sleeve(BODY, y0, y1, d0, d1, leather(strap))
    if plaques:
        for px in range(-14, 16, 7):
            for z in (9 + d1 - 1,):
                m.box(px, px + 4, y0 + 1, y1 - 1, d1 + 8, d1 + 9, plaques, over_body=True)
    # buckle frame + prong
    zb = 8 + d1
    for x in range(-4, 4):
        for y in range(y0 - 1, y1 + 1):
            if x in (-4, 3) or y in (y0 - 1, y1):
                m.set(x, y, zb, buckle)
                m.set(x, y, zb + 1, mul(buckle, 1.2))
    for x in range(-4, 1):
        m.set(x, (y0 + y1) // 2, zb + 1, mul(buckle, 0.9))


def pouch(m, x0, y0, z0, w=8, hgt=9, dep=5, col=LEATHER, flap=LEATHER_DARK, toggle=IVORY):
    m.box(x0, x0 + w, y0, y0 + hgt, z0, z0 + dep, leather(col))
    m.box(x0, x0 + w, y0 + hgt - 4, y0 + hgt + 1, z0 - 1, z0 + dep + 1, leather(flap))
    m.box(x0 + w // 2 - 1, x0 + w // 2 + 1, y0 + hgt - 6, y0 + hgt - 3, z0 + dep + 1, z0 + dep + 2, solid(toggle))


def drinking_horn(m, x, y, z, side=1):
    pts = [(x, y, z, 1.0), (x + 3 * side, y - 6, z - 1, 0.9), (x + 5 * side, y - 13, z - 3, 0.7),
           (x + 4 * side, y - 19, z - 5, 0.45), (x + 1 * side, y - 23, z - 6, 0.2)]

    def col(px, py, pz, t):
        if t < 0.08 and (px, py) == (x, y):
            return GOLD
        return mix(IVORY, hexc("#6b4a2a"), 0.0 if py > y - 18 else 0.7)
    m.tube(pts, 3.0, lambda px, py, pz, t: mix(IVORY, hexc("#5a3a20"), min(1, max(0, (y - py - 14) / 9))))
    for dy in (0, -1):                                           # gold rim and cord
        for dx in range(-3, 4):
            m.set(x + dx, y + dy, z + 3, GOLD)


def teeth_necklace(m, y=88, n=7, z=9, col=IVORY, cord=LEATHER_DARK, spread=12, sag=4):
    for i in range(-spread, spread + 1):
        yy = y - int(sag * (1 - (i / spread) ** 2))
        m.set(i, yy, z, cord, over_body=True)
    for k in range(n):
        tx = int(-spread + 2 + k * (2 * spread - 4) / max(1, n - 1))
        ty = y - int(sag * (1 - (tx / spread) ** 2)) - 1
        for j in range(5):
            w = 2 if j < 2 else 1
            for dx in range(w):
                m.set(tx + dx, ty - j, z + 1, mul(col, 1.05 - 0.05 * j), over_body=True)


def mjolnir(m, y=82, z=9):
    for dy in range(0, 6):
        m.set(-1, y + dy, z, LEATHER_DARK, over_body=True)
    for x in range(-4, 4):
        for yy in range(y - 3, y):
            m.set(x, yy, z + 1, SILVER if (x + yy) % 3 else IRON, over_body=True)
    for x in range(-2, 2):
        for yy in range(y - 8, y - 3):
            m.set(x, yy, z + 1, SILVER, over_body=True)


def arm_ring(m, part, y, col=GOLD, d0=0, d1=2):
    """A twisted gold arm ring: thin, two strands."""
    m.sleeve(part, y, y + 3, d0, d1, lambda x, yy, z, d: GOLD_HI if (u_of(x, z) + yy * 2) % 6 < 3 else mul(col, 0.8))


def studs(m, part, y0, y1, d, col=IRON, step=5):
    x0, x1, _, _, z0, z1 = part
    for y in range(y0, y1, step):
        for x in range(x0 + 2, x1 - 1, step):
            m.sphere(x, y, z1 + d, 1.2, col)
            m.sphere(x, y, z0 - d - 1, 1.2, col)
        for z in range(z0 + 2, z1 - 1, step):
            m.sphere(x1 + d, y, z, 1.2, col)
            m.sphere(x0 - d - 1, y, z, 1.2, col)


def cloak(m, mat, y0, y1, x0=-20, x1=20, zb=-10, trim=None, folds=1.0, flare=6):
    for y in range(y0, y1):
        t = (y1 - y) / (y1 - y0)
        w = int(flare * t)
        for x in range(x0 - w, x1 + w):
            fold = folds * (2.0 * math.sin(x * 0.45) + 1.0 * math.sin(x * 1.1 + 1.0)) * (0.4 + 0.6 * t)
            zz = int(round(zb - 1.5 - fold))
            edge = x in (x0 - w, x0 - w + 1, x1 + w - 2, x1 + w - 1) or y in (y0, y0 + 1, y0 + 2)
            for z in range(zz - 1, zz + 2):
                c = (trim(x, y, z, 0) if trim and edge else mat(x, y, z, 0))
                m.set(x, y, z, mul(c, 0.85 + 0.12 * (math.sin(x * 0.45) + 1) / 2))


def laces(m, part, y0, y1, d, col):
    x0, x1, _, _, z0, z1 = part
    cx = (x0 + x1) // 2
    for y in range(y0, y1):
        k = (y - y0) % 6
        off = k if k < 3 else 6 - k
        for x in (cx - 1 - off, cx + off):
            m.set(x, y, z1 + d, col)


# ================================================================== more details
def sash(m, mat, x_top, x_bot, y_top=100, y_bot=44, width=7, d0=3, d1=6, bulge=None, part=BODY):
    """A band worn diagonally from one shoulder to the other hip (front, back and over the shoulder)."""
    def on(x, y, z):
        if y > 96:                                        # over the shoulder top
            return abs(x - x_top) < width
        t = (y_top - y) / (y_top - y_bot)
        cx = x_top + (x_bot - x_top) * t
        return abs(x + 0.5 - cx) < width
    m.sleeve(part, y_bot, y_top, d0, d1, mat, bulge=bulge, keep=on)
    x0, x1 = (ARM_R if x_top > 0 else ARM_L)[0:2]
    m.sleeve(ARM_R if x_top > 0 else ARM_L, 90, 100, d0, d1, mat, bulge=bulge,
             keep=lambda x, y, z: abs(z) < width + 2)


def half_cloak(m, mat, side, y0, y1, trim=None, folds=1.2):
    """A cloak thrown over one shoulder: hangs long on that side, cut away on the other."""
    for y in range(y0, y1):
        t = (y1 - y) / (y1 - y0)
        for x in range(-24, 24):
            reach = 22 + 8 * t                              # on the cloak side
            cut = -6 + 26 * (1 - t) ** 1.4                  # diagonal cut on the other side
            xs = x * side
            if not (-cut <= xs <= reach) or (xs < 0 and -xs > cut):
                continue
            if xs < -cut:
                continue
            fold = folds * (2.0 * math.sin(x * 0.45) + 1.0 * math.sin(x * 1.1 + 1.0)) * (0.4 + 0.6 * t)
            zz = int(round(-11.5 - fold))
            edge = abs(xs - reach) < 2 or abs(xs + cut) < 2 or y < y0 + 3
            for z in range(zz - 1, zz + 2):
                c = (trim(x, y, z, 0) if trim and edge else mat(x, y, z, 0))
                m.set(x, y, z, mul(c, 0.85 + 0.12 * (math.sin(x * 0.45) + 1) / 2))
    # drape over the shoulder and down the front of that side
    part = ARM_R if side > 0 else ARM_L
    m.sleeve(part, 84, 100, 2, 4, mat)
    for y in range(64, 98):
        for x in range(10, 22):
            X = x if side > 0 else -1 - x
            if abs(x - 15 - (97 - y) * 0.15) < 5:
                for z in (10, 11, 12):
                    m.set(X, y, z, mat(X, y, z, 0), over_body=True)


def round_shield_back(m, cx, cy, r=26, z0=-15, paint=("#8a1c1c", "#e6dcc4"), motif=None):
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > r + 0.4:
                continue
            ang = math.atan2(dy, dx)
            plank = (dx + 100) // 6
            wood = mul(hexc("#7a5636"), 0.85 + 0.25 * h(plank, 3))
            col = hexc(paint[0]) if (int((ang + math.pi) / (math.pi / 2)) % 2) else hexc(paint[1])
            if motif and motif(dx, dy):
                col = hexc("#1a1a1a")
            chip = vnoise(dx, dy, 0, 5, 71) > 0.68              # paint chipped off: bare wood shows
            c = wood if chip else mul(col, 0.85 + 0.2 * h(plank, dy // 4))
            if d > r - 2.2:
                c = mul(IRON, 0.85 + 0.25 * h(dx, dy)) if int(math.degrees(ang) + 400) % 24 > 2 else mul(IRON, 1.3)
            for z in (z0, z0 - 1):
                m.set(cx + dx, cy + dy, z, c if z == z0 - 1 else mul(c, 0.8))
            if d < 5.5:
                m.set(cx + dx, cy + dy, z0 - 2, mul(IRON, 1.15 - d * 0.05))
                if d < 3:
                    m.set(cx + dx, cy + dy, z0 - 3, mul(IRON, 1.3))
    m.box(-12, 12, 60, 64, -11, -9, leather(LEATHER_DARK))     # carrying strap


EMBLEM = [
    "....XX....XX....",
    "...XXX....XXX...",
    "..XXXXXXXXXXXX..",
    "..XX#XXXXXX#XX..",
    ".XXXXXXXXXXXXXX.",
    ".XXXXXXXXXXXXXX.",
    "..XXXXXXXXXXXX..",
    "...XXXXXXXXXX...",
    "...XX.XXXX.XX...",
    "....XXXXXXXX....",
    "....V.V..V.V....",
    ".....XXXXXX.....",
    "......XXXX......",
]


def dragon_emblem(m, cx, top_y, z0, px=2):
    """Fáfnir's head in raised gold, deeper towards the middle, with ruby eyes and ivory fangs."""
    rows = len(EMBLEM)
    for j, row in enumerate(EMBLEM):
        for i, ch in enumerate(row):
            if ch == ".":
                continue
            edge = sum(1 for (a, b) in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                       if not (0 <= b < rows and 0 <= a < len(row)) or EMBLEM[b][a] == ".")
            depth = 2 if edge else (4 if 2 < j < 9 and 3 < i < 12 else 3)
            for a in range(px):
                for b in range(px):
                    x = cx + (i - len(row) // 2) * px + a
                    y = top_y - j * px - b
                    for z in range(z0, z0 + depth):
                        if ch == "#":
                            c = hexc("#c01830") if z < z0 + depth - 1 else hexc("#ff5a6e")
                        elif ch == "V":
                            c = IVORY
                        else:
                            c = GOLD_LO if (z == z0 + depth - 1 and knot_engraved(x, y, z)) else mul(GOLD, 0.95 + 0.25 * h(x, y))
                        m.set(x, y, z, c, over_body=True)


def horn(m, x, y, z, dx, dy, dz, length=18, r0=2.6, col=IVORY):
    pts = []
    for i in range(6):
        t = i / 5
        pts.append((x + dx * t * length + 2 * t * t * dx, y + dy * t * length + 4 * t * t, z + dz * t * length, 1 - 0.8 * t))
    m.tube(pts, r0, lambda px, py, pz, t: mix(col, mul(col, 0.6), t))


# ================================================================== the sets
def berserker():
    """Centerpiece: the bear's head worn as a hood, jaws open around the face.
    Asymmetry: the pelt is slung over the LEFT shoulder only; left arm armoured, right arm bare with rings.
    60 brown fur and leather / 30 skin and iron / 10 blue woad."""
    m = Model()
    face(m, beard="#8a3b1c", hair="#8a3b1c", beard_len=26)
    S = skin()
    for p in (BODY, ARM_R, ARM_L):
        m.paint_part(p, S)
    woad = hexc("#2a5fb0")
    for (x, y, z) in list(m.v):                               # woad: a single spiral on the right of the chest + right arm
        if inside((x, y, z), BODY) and z == 7 and 64 < y < 92 and x > 0:
            r = math.hypot(x - 8, y - 80)
            if abs((r * 1.4 + math.atan2(y - 80, x - 8) * 3) % 6 - 3) < 0.9 and r < 9:
                m.v[(x, y, z)] = woad
        if inside((x, y, z), ARM_R) and 56 < y < 74 and (y + u_of(x, z) // 2) % 7 == 0:
            m.v[(x, y, z)] = woad
    m.paint_part(LEG_R, cloth("#4a3f35"))
    m.paint_part(LEG_L, cloth("#4a3f35"))
    bear, bear_l = fur("#5b3a22", "#8a6440"), fur("#7a5434", "#a07a52")
    # --- the hood: a full bear head, upper jaw over the brow, lower jaw framing the cheeks
    m.cap(HEAD, 110, 0, 4, bear, bulge=fur_bulge(0.8),
          keep=lambda x, y, z: not (z >= 16 and y < 119 and -15 <= x < 15))
    m.box(-18, 18, 117, 134, 15, 24, lambda x, y, z, d: bear(x, y, z, 2))        # forehead
    m.box(-10, 10, 116, 130, 24, 38, lambda x, y, z, d: bear_l(x, y, z, 1))      # upper snout
    m.box(-8, 8, 117, 126, 38, 42, solid("#9a7450"))
    m.box(-5, 5, 123, 128, 41, 43, solid("#0e0e0e"))
    m.set(-3, 127, 43, (210, 210, 220))
    for tx, ln in ((-8, 6), (-5, 3), (-2, 2), (1, 2), (4, 3), (7, 6)):            # upper teeth, big canines
        for j in range(ln):
            m.box(tx, tx + 2, 116 - j, 117 - j, 34, 37, solid(mul(IVORY, 1 - 0.05 * j)))
    for sx in (1, -1):                                         # lower jaw along the cheeks, with teeth pointing up
        for y in range(96, 112):
            for z in range(10, 30):
                if abs((z - 10) - (111 - y) * 0.2) < 14 and y > 96 + (z - 10) * 0.3:
                    for x in (16, 17, 18):
                        X = x if sx > 0 else -1 - x
                        m.set(X, y, z, bear(X, y, z, 2))
        for z in range(16, 30, 4):
            for j in range(3):
                X = 16 if sx > 0 else -17
                m.set(X - sx, 108 + j, z, IVORY)
    for ex in (-14, 11):
        m.box(ex, ex + 4, 128, 132, 24, 25, solid("#0a0806"))
        m.set(ex + 1, 131, 25, (225, 225, 225))
    for sx in (-1, 1):
        for x in range(10, 18):
            for y in range(132, 141):
                if (x - 14) ** 2 + (y - 133) ** 2 <= 14:
                    X = x if sx > 0 else -1 - x
                    for z in range(-2, 4):
                        m.set(X, y, z, bear(X, y, z, 2))
                    if (x - 14) ** 2 + (y - 133) ** 2 <= 5:
                        m.set(X, y, 4, hexc("#3a2414"))
    # --- pelt: down the back and over the LEFT shoulder as a sash, one paw hanging in front
    half_cloak(m, bear, -1, 26, 112, folds=0.6)
    sash(m, bear, x_top=-14, x_bot=12, y_top=102, y_bot=50, width=8, d0=2, d1=5, bulge=fur_bulge(1.0))
    m.sleeve(ARM_L, 84, 104, 0, 5, bear, bulge=fur_bulge(1.2))                   # bulky left shoulder
    for y in range(66, 90):
        for x in range(18, 30):
            if abs(x - 24) < 5 - (y < 70) * 2:
                for z in (9, 10, 11):
                    m.set(-1 - x, y, z, bear(-1 - x, y, z, 3), over_body=True)
    for x in (19, 22, 25, 28):
        for j in range(5):
            m.set(-1 - x, 65 - j, 11 - j // 2, mul(IVORY, 1 - 0.07 * j), over_body=True)
    # --- harness: one strap from the right shoulder, iron boss where it meets the pelt
    for y in range(52, 98):
        for x in range(-16, 16):
            d2 = abs((x + 0.5) - (y - 74) * 0.62)
            if d2 < 2.6:
                for z in (8, 9):
                    m.set(x, y, z, leather(LEATHER_DARK)(x, y, z, 0))
                    m.set(x, y, -9 - (z - 8), leather(LEATHER_DARK)(x, y, z, 0))
                if d2 < 0.6 and y % 5 == 0:
                    m.set(x, y, 10, IRON)
    for x in range(-6, 6):
        for y in range(68, 80):
            r = math.hypot(x + 0.5, y - 73.5)
            if r < 6:
                m.set(x - 2, y, 12, mul(IRON, 1.15 - r * 0.05))
                if r < 2.5:
                    m.set(x - 2, y, 13, mul(IRON, 1.3))
    teeth_necklace(m, y=94, n=5, z=10, spread=9, sag=4)
    # --- belt: knife on the RIGHT front, horn on the LEFT back, pouch; leather strips of uneven lengths
    belt(m, 46, 52, d1=3)
    m.box(9, 12, 26, 44, 9, 12, leather(LEATHER_DARK))
    m.box(9, 12, 44, 50, 9, 12, solid("#d8ccb0"))
    m.box(8, 13, 30, 31, 9, 13, solid(IRON))
    drinking_horn(m, -15, 46, -9, side=-1)
    pouch(m, -12, 36, 10, w=7, hgt=8, dep=4)
    for i, x in enumerate(range(-18, 18, 5)):
        dz = 2 if i % 2 else 1
        bottom = 22 + int(8 * h(i, 5))
        for y in range(bottom, 46):
            for xx in range(x, x + 4):
                for z in (8 + dz, -9 - dz):
                    m.set(xx, y, z, mul(LEATHER, 0.85 + 0.2 * h(xx, y // 3, i)) if y > bottom + 1 else IRON)
    # --- left forearm: studded bracer; right forearm: rope wraps and three gold rings
    m.sleeve(ARM_L, 52, 74, 0, 2, leather(LEATHER_DARK))
    studs(m, ARM_L, 54, 74, 2, step=5)
    m.sleeve(ARM_R, 52, 68, 0, 1, lambda x, y, z, d: hexc("#b49a70") if (y + u_of(x, z) // 3) % 3 else hexc("#8a7450"),
             bulge=lambda x, y, z: 1 if (y + u_of(x, z) // 3) % 3 == 0 else 0)
    for y in (70, 76, 82):
        arm_ring(m, ARM_R, y)
    # --- leg wraps and boots
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 12, 40, 0, 1, lambda x, y, z, d: hexc("#5c4e3e") if (u_of(x, z) + y) % 8 < 3 else hexc("#3e342a"),
                 bulge=lambda x, y, z: 1 if (u_of(x, z) + y) % 8 < 3 else 0)
        m.sleeve(part, 0, 14, 0, 2, leather(LEATHER))
        laces(m, part, 2, 13, 3, hexc("#c8b48a"))
        m.sleeve(part, 12, 18, 0, 3, fur("#4a2e1a", "#7a5434"), bulge=fur_bulge(0.8))
    return m


def ulfhednar():
    """Centerpiece: the snarling wolf head.  Asymmetry: pelt over the RIGHT shoulder, shield on the back,
    axe on the right hip.  60 grey fur and mail / 30 oxblood padding / 10 amber eyes and bronze."""
    m = Model()
    face(m, beard="#5c5248", hair="#5c5248", eyes="#c48a1a", beard_len=22, beads=IRON)
    for p in (BODY, ARM_R, ARM_L):
        m.paint_part(p, cloth("#5a2a20"))
    for p in (LEG_R, LEG_L):
        m.paint_part(p, cloth("#3a3a40"))
    wolf, wolf_l = fur("#8e8a84", "#cfcac2"), fur("#c9c4bc", "#eeeae2")
    # --- gambeson, then mail (holes show the quilting); a torn sleeve on the left
    m.sleeve(BODY, 30, 96, 0, 2, quilt("#6a2e22"), bulge=quilt_bulge)
    for part in (ARM_R, ARM_L):
        m.sleeve(part, 52, 96, 0, 2, quilt("#6a2e22"), bulge=quilt_bulge)
    m.sleeve(ARM_R, 70, 96, 2, 3, mail())
    m.sleeve(ARM_L, 80, 96, 2, 3, mail(), keep=lambda x, y, z: y > 82 or h(x, z) > 0.4)
    hem = lambda x, y, z: y > 33 + int(4 * vnoise(x, 0, z, 6, 81)) or (u_of(x, z) // 3) % 2 == 0
    m.sleeve(BODY, 28, 96, 2, 3, mail(), keep=hem)
    m.sleeve(LEG_R, 28, 48, 2, 3, mail(), keep=hem)
    m.sleeve(LEG_L, 28, 48, 2, 3, mail(), keep=hem)
    # --- leather lamellar plates on the LEFT chest only (the shield side)
    lm, lb = scales("#6b4428", "#2e1a0e", rivet="#b07a34", w=6, ht=8, missing=0.0, tarnish="#4a2e18")
    m.sleeve(BODY, 60, 92, 3, 5, lm, bulge=lb, keep=lambda x, y, z: x < 0 or z < -8)
    # --- belt with bronze plaques, axe on the right hip, pouch on the left, Mjölnir and tooth necklace
    belt(m, 46, 52, d0=3, d1=5, plaques=solid("#b07a34"), buckle=hexc("#b07a34"))
    m.box(10, 12, 22, 56, 13, 15, leather("#6e4a2a"))
    for y in range(44, 56):
        reach = 6 + int(4 * math.sin((y - 44) / 11 * math.pi))
        m.box(12, 12 + reach, y, y + 1, 13, 15, lambda x, yy, z, d: SILVER if x >= 12 + reach - 2 else mul(STEEL, 0.9 + 0.2 * h(x, yy)))
    pouch(m, -14, 36, 13, w=8, hgt=9, dep=4)
    teeth_necklace(m, y=94, n=7, z=12, spread=10, sag=4)
    mjolnir(m, y=84, z=12)
    # --- wolf hood: snarling jaws, wrinkled muzzle, amber eyes, tall ears with tufts
    m.cap(HEAD, 110, 0, 4, wolf, bulge=fur_bulge(0.7),
          keep=lambda x, y, z: not (z >= 16 and y < 119 and -15 <= x < 15))
    m.box(-18, 18, 116, 131, 15, 22, lambda x, y, z, d: wolf(x, y, z, 2))
    m.box(-7, 7, 120, 129, 22, 40, lambda x, y, z, d: wolf_l(x, y, z, 1))
    for z in range(24, 34, 3):                                     # snarl wrinkles
        m.box(-7, 7, 129, 130, z, z + 1, solid(mul(hexc("#c9c4bc"), 0.75)))
    m.box(-6, 6, 112, 116, 22, 36, lambda x, y, z, d: wolf_l(x, y, z, 1))
    m.box(-6, 6, 116, 120, 22, 37, solid("#7a1e22"))
    m.box(-4, 4, 126, 130, 39, 41, solid("#121212"))
    for tx in (-6, 5):
        for j in range(5):
            m.set(tx, 119 - j, 36, IVORY)
            m.set(tx, 116 + j, 34, IVORY)
    for tx in range(-4, 5, 2):
        m.set(tx, 119, 37, IVORY)
        m.set(tx, 116, 35, IVORY)
    for ex in (-13, 10):
        m.box(ex, ex + 4, 126, 129, 22, 23, solid("#ffb020"))
        m.box(ex + 1, ex + 3, 126, 129, 23, 24, solid("#e08a10"))
        m.set(ex + 2, 127, 24, BLACK)
    for sx in (1, -1):
        for i, y in enumerate(range(129, 150)):
            w = max(1, 7 - i // 3)
            for x in range(6, 6 + w):
                X = x if sx > 0 else -1 - x
                for z in range(-1, 4):
                    m.set(X, y, z, wolf(X, y, z, 2))
                if w > 2 and x > 6:
                    m.set(X, y, 4, hexc("#c09a8a"))
        X = 7 if sx > 0 else -8
        for j in range(4):
            m.set(X, 150 + j, 1, wolf(X, 150 + j, 1, 5))
    # --- pelt over the RIGHT shoulder, forelegs knotted on the left chest, ruff
    half_cloak(m, wolf, 1, 24, 112, folds=0.8)
    m.sleeve(ARM_R, 84, 104, 0, 5, wolf, bulge=fur_bulge(1.2))
    m.sleeve(BODY, 92, 102, 0, 4, wolf, bulge=fur_bulge(1.0))
    for y in range(74, 96):
        for x in range(-14, 18):
            if abs((x + 6) - (y - 74) * 0.95) < 3:
                for z in (12, 13, 14):
                    m.set(x, y, z, wolf(x, y, z, 3), over_body=True)
    m.box(-12, -5, 72, 79, 13, 17, lambda x, y, z, d: wolf(x, y, z, 3), over_body=True)
    for x in (-12, -9, -6):
        for j in range(3):
            m.set(x, 71 - j, 16, IVORY, over_body=True)
    # --- round shield on the back, painted with a black wolf head, paint chipped
    round_shield_back(m, -4, 72, r=24, z0=-16, paint=("#7a1c1c", "#d8cfb4"),
                      motif=lambda dx, dy: (abs(dx) < 7 - dy * 0.3 and -8 < dy < 8) or (abs(abs(dx) - 6) < 2 and 6 < dy < 12))
    # --- bracers, leg wraps, turnshoes
    for part in (ARM_R, ARM_L):
        m.sleeve(part, 52, 70, 2, 4, leather(LEATHER))
        studs(m, part, 54, 70, 4, col=hexc("#b07a34"), step=5)
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 10, 30, 0, 1, lambda x, y, z, d: hexc("#6a6460") if (u_of(x, z) - y) % 7 < 3 else hexc("#3e3a38"),
                 bulge=lambda x, y, z: 1 if (u_of(x, z) - y) % 7 < 3 else 0)
        m.sleeve(part, 0, 11, 0, 2, leather("#4a3220"))
        m.box(part[0] + 6, part[0] + 9, 7, 9, 10, 12, solid(IVORY))
    return m


def valkyrie():
    """Centerpiece: the great winged helm.  Asymmetry: a feathered wing-pauldron on the LEFT shoulder, a
    plain plate on the right, a sash from the right shoulder, a cape over the left.
    60 silver / 30 blue / 10 gold and sapphire."""
    m = Model()
    face(m, hair="#e2c26a", eyes="#3f7fd0", woman=True)
    for p in (BODY, ARM_R, ARM_L, LEG_R, LEG_L):
        m.paint_part(p, cloth("#3c62a6"))
    silver = plate(SILVER)
    fcols = [hexc("#ffffff"), hexc("#eceff4"), hexc("#d7dce4"), hexc("#bfc6d0")]

    def feather(x0, y0, z0, length, width, dx, dy, dz, shade=0):
        n = math.sqrt(dx * dx + dy * dy + dz * dz)
        dx, dy, dz = dx / n, dy / n, dz / n
        for i in range(length):
            t = i / length
            w = width * math.sin(min(1, t * 1.3) * math.pi / 2) * (1 - t) ** 0.35
            cx, cy, cz = x0 + dx * i, y0 + dy * i, z0 + dz * i
            for k in range(-int(w), int(w) + 1):
                c = fcols[min(3, shade + (1 if abs(k) == int(w) else 0))]
                if k == 0:
                    c = hexc("#aab1bc")
                if t > 0.8 and shade == 0:
                    c = mix(c, hexc("#9aa4b4"), 0.5)         # darker feather tips
                m.set(int(round(cx)), int(round(cy + k * 0.4)), int(round(cz + k * 0.9)), c)
    # --- linen; silver scale cuirass (some scales missing); engraved gold neckline
    sc, sb = scales("#c8ced6", "#6f7884", rivet="#d9a520", w=8, ht=6, tarnish="#8a8f8a")
    m.sleeve(BODY, 46, 94, 1, 3, sc, bulge=sb)
    m.sleeve(BODY, 90, 96, 1, 5, gold())
    m.sleeve(BODY, 44, 48, 1, 5, gold())
    # --- centre of the chest: a sapphire set in a gold ring (the 10% pop)
    for x in range(-7, 7):
        for y in range(76, 90):
            r = math.hypot(x + 0.5, y - 83)
            if r < 6.5:
                m.set(x, y, 12, GOLD if r > 3.5 else hexc("#2f6fd8"), over_body=True)
                if r < 3.5:
                    m.set(x, y, 13, hexc("#5fa8ff") if r < 1.6 else hexc("#2f6fd8"), over_body=True)
    # --- LEFT shoulder: a wing of feathers sweeping out and down over stacked plates
    for k, (y0, y1) in enumerate(((84, 94), (88, 98))):
        m.sleeve(ARM_L, y0, y1, 2 + k, 4 + k, lambda x, y, z, dd, y0=y0: gold()(x, y, z, dd) if y < y0 + 2 else silver(x, y, z, dd))
    for row, (y, n, length) in enumerate(((104, 10, 16), (98, 11, 22), (92, 12, 30))):
        for j in range(n):
            z = 8 - j * 1.6
            feather(-18 - row * 2, y, int(z), length, 2.6, -0.55, -1.0, -0.1, shade=row)
    # --- RIGHT shoulder: a single plain plate (the spear arm)
    m.sleeve(ARM_R, 86, 98, 2, 4, lambda x, y, z, d: gold(False)(x, y, z, d) if y < 88 else silver(x, y, z, d))
    # --- sash from the right shoulder to the left hip with a gold fringe
    sash(m, cloth("#2a4c8e"), x_top=14, x_bot=-12, y_top=100, y_bot=40, width=5, d0=3, d1=5)
    for x in range(-18, -6):
        for j in range(4):
            if x % 2 == 0:
                m.set(x, 39 - j, 13, GOLD)
    # --- vambraces (right engraved, left plain with an arm ring), gauntlets
    m.sleeve(ARM_R, 54, 76, 1, 3, silver)
    m.sleeve(ARM_R, 60, 70, 1, 4, gold())
    m.sleeve(ARM_L, 54, 72, 1, 3, silver)
    arm_ring(m, ARM_L, 76)
    for part in (ARM_R, ARM_L):
        for y in range(48, 54, 2):
            m.sleeve(part, y, y + 2, 1, 2 + (y % 4 == 0), silver)
    # --- skirt: linen with three layers of tassets, longer on the left
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 16, 46, 0, 2, cloth("#3c62a6"))
        m.sleeve(part, 16, 18, 0, 3, solid("#f1f1f1"))
    for k, (y0, y1) in enumerate(((40, 48), (34, 42), (26, 36))):
        for part in (LEG_R, LEG_L):
            lo = y0 - (4 if part is LEG_L and k == 2 else 0)
            m.sleeve(part, lo, y1, 2 + k, 4 + k, lambda x, y, z, d, lo=lo: gold(False)(x, y, z, d) if y == lo else silver(x, y, z, d),
                     keep=lambda x, y, z: (u_of(x, z) // 4) % 3 != 2)
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 4, 18, 1, 3, silver)
        m.sphere((part[0] + part[1]) // 2, 19, 11, 4.5, silver)
        m.sphere((part[0] + part[1]) // 2, 19, 13, 2.2, GOLD)
        for i, y in enumerate((0, 2)):
            m.sleeve(part, y, y + 2, 1, 3 - i, silver)
    belt(m, 46, 50, d0=3, d1=5, strap=hexc("#2a3f6e"), plaques=gold(False), buckle=GOLD)
    # --- cape over the LEFT shoulder
    half_cloak(m, cloth("#7fa6e0"), -1, 4, 100, trim=gold(False), folds=1.3)
    # --- the winged helm
    m.cap(HEAD, 112, 0, 3, silver, keep=lambda x, y, z: not (z >= 16 and y < 117 and -15 <= x < 15))
    m.sleeve(HEAD, 114, 119, 3, 5, gold())
    m.box(-2, 2, 104, 119, 16, 20, silver)
    m.box(-1, 1, 113, 116, 20, 21, solid(GOLD))
    for sx in (1, -1):
        for x in range(10, 18):
            X = x if sx > 0 else -1 - x
            for y in range(100, 114):
                if y > 100 + (x - 10):
                    for z in range(16, 19):
                        m.set(X, y, z, silver(X, y, z, 0))
    for x in range(-16, 16, 4):
        m.sphere(x, 122, 19, 1.0, GOLD_HI)
    m.box(-2, 2, 131, 135, -18, 18, gold())
    for sx in (1, -1):                                          # big swept wings: four rows of feathers
        for row, (n, length) in enumerate(((6, 12), (7, 18), (8, 26), (8, 34))):
            for j in range(n):
                ang = 0.2 + j * 0.12
                x = (19 + row) * sx + (0 if sx > 0 else -1)
                feather(x, 116 + row * 2, 4 - j * 2, length, 2.8 - row * 0.3,
                        0.3 * sx, math.cos(ang) * 1.0, -math.sin(ang) * 1.25, shade=min(3, 3 - row))
    # --- one long braid over the right shoulder with gold beads
    for y in range(64, 104):
        for x in (12, 13, 14, 15):
            m.set(x, y, 17, mul(hexc("#e2c26a"), 0.72 + 0.38 * (((y + x) // 2) % 2)), over_body=True)
    for y in range(60, 64):
        for x in (12, 13, 14, 15):
            m.set(x, y, 17, GOLD, over_body=True)
    return m


def jarl():
    """Centerpiece: Fáfnir's head in raised gold on the chest, ruby eyes.  Silhouette: a massive RIGHT
    pauldron with horns, a high fur gorget, a cloak over the left shoulder.
    60 dark steel and mail / 30 teal serpent scale / 10 gold and ruby."""
    m = Model()
    face(m, beard="#b8b2a8", hair="#b8b2a8", eyes="#6aa0c8", beard_len=12, braids=False)
    for p in (BODY, ARM_R, ARM_L):
        m.paint_part(p, cloth("#6a1414"))
    for p in (LEG_R, LEG_L):
        m.paint_part(p, cloth("#2e2a2a"))
    dark = plate("#4a4f57")
    sc, sb = scales("#2c8a7a", "#0f3a34", rivet="#d9a520", w=8, ht=6, tarnish="#1e5a50")
    hem = lambda x, y, z: y > 23 + int(4 * vnoise(x, 0, z, 6, 91)) or (u_of(x, z) // 3) % 2 == 0
    m.sleeve(BODY, 20, 96, 0, 2, quilt("#7a1a1a"), bulge=quilt_bulge)
    m.sleeve(BODY, 18, 96, 2, 3, mail(), keep=hem)
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 18, 48, 2, 3, mail(), keep=hem)
    m.sleeve(BODY, 52, 94, 3, 5, sc, bulge=sb)
    m.sleeve(BODY, 50, 54, 3, 7, gold())
    dragon_emblem(m, 0, 88, 15, px=2)
    # --- massive RIGHT pauldron: five stacked lames, gold edges, rivets, two horns
    for k, (y0, y1) in enumerate(((72, 84), (77, 89), (82, 94), (87, 99), (92, 106))):
        d = 2 + k * 2
        m.sleeve(ARM_R, y0, y1, d, d + 2, lambda x, y, z, dd, y0=y0: gold()(x, y, z, dd) if y < y0 + 3 else dark(x, y, z, dd))
    for k, y in enumerate((80, 85, 90, 95, 100)):              # rivets along each lame's gold edge
        d = 2 + k * 2 + 2
        for x in range(ARM_R[0] + 1, ARM_R[1] + d, 5):
            m.set(x, y - 3, ARM_R[5] + d, GOLD_HI)
    horn(m, 30, 104, 4, 0.55, 0.7, -0.35, length=20, r0=3.0, col=hexc("#2a2622"))
    horn(m, 30, 104, -6, 0.55, 0.65, -0.6, length=15, r0=2.4, col=hexc("#2a2622"))
    # --- modest LEFT pauldron (two lames)
    for k, (y0, y1) in enumerate(((84, 94), (90, 100))):
        m.sleeve(ARM_L, y0, y1, 2 + k, 4 + k, lambda x, y, z, dd, y0=y0: gold(False)(x, y, z, dd) if y < y0 + 2 else dark(x, y, z, dd))
    # --- high fur gorget, cloak over the LEFT shoulder held by a ring brooch on the right
    m.sleeve(BODY, 90, 106, 2, 8, fur("#22201e", "#4a4642"), bulge=fur_bulge(1.2),
             keep=lambda x, y, z: not (z > 8 and -9 <= x < 9 and y < 100))
    half_cloak(m, cloth("#8a1c1c"), -1, 2, 100, trim=gold(), folds=1.4)
    for dx in range(-6, 7):
        for dy in range(-6, 7):
            r = math.hypot(dx, dy)
            if 3.5 < r < 6:
                m.set(12 + dx, 96 + dy, 17, GOLD_HI if (dx + dy) % 3 else GOLD, over_body=True)
                m.set(12 + dx, 96 + dy, 16, GOLD_LO, over_body=True)
    for i in range(14):
        m.set(12 - 5 + i, 98 - i // 2, 18, GOLD_HI, over_body=True)
    # --- belt, sword on the LEFT hip, pouch on the right
    belt(m, 46, 52, d0=4, d1=6, plaques=gold(False), buckle=GOLD)
    m.box(-22, -18, 6, 46, 6, 10, leather("#3a1e10"))
    for y in range(12, 44, 8):
        m.box(-23, -17, y, y + 2, 6, 10, gold(False))
    m.box(-22, -18, 4, 10, 6, 10, gold(False))
    m.box(-25, -15, 46, 48, 6, 10, gold(False))
    m.box(-21, -19, 48, 56, 7, 9, leather("#2a1a10"))
    m.box(-23, -17, 56, 60, 6, 10, gold(False))
    m.set(-20, 58, 10, hexc("#c01830"))
    pouch(m, 10, 34, 14, w=8, hgt=9, dep=4, col=hexc("#4a2a18"), flap=hexc("#2e1a10"), toggle=GOLD)
    # --- arms: mail sleeves; right arm serpent vambrace, left arm plate vambrace; arm rings; gauntlets
    for part in (ARM_R, ARM_L):
        m.sleeve(part, 52, 96, 0, 1, mail())
        m.sleeve(part, 48, 54, 1, 2, dark)
        for kx in range(part[0] + 2, part[1] - 1, 4):
            m.box(kx, kx + 3, 49, 52, part[5] + 2, part[5] + 3, solid(GOLD))
    m.sleeve(ARM_R, 54, 72, 1, 3, sc, bulge=sb)
    m.sleeve(ARM_R, 70, 73, 1, 4, gold())
    m.sleeve(ARM_L, 54, 72, 1, 3, dark)
    arm_ring(m, ARM_L, 74)
    arm_ring(m, ARM_L, 64)
    # --- legs
    for part in (LEG_R, LEG_L):
        m.sleeve(part, 4, 18, 2, 4, dark)
        m.sleeve(part, 15, 17, 2, 5, gold(False))
        m.sphere((part[0] + part[1]) // 2, 20, 12, 5.0, dark)
        m.sphere((part[0] + part[1]) // 2, 20, 15, 2.4, GOLD)
        m.sleeve(part, 0, 5, 0, 3, leather(LEATHER_DARK))
    # --- Gjermundbu helm with crest, spike, spectacle guard; mail aventail
    m.cap(HEAD, 114, 0, 3, dark, keep=lambda x, y, z: not (z >= 16 and y < 119 and -15 <= x < 15))
    m.sleeve(HEAD, 116, 121, 3, 5, gold())
    for x in range(-18, 18):
        for z in range(-18, 18):
            for y in range(120, 134):
                if (abs(x + 0.5) < 1.6 or abs(z + 0.5) < 1.6):
                    dx = max(-16 - x, 0, x - 15)
                    dz = max(-16 - z, 0, z - 15)
                    dy = max(0, y - 127)
                    if 3 < max(dx, dy, dz) <= 5:
                        m.set(x, y, z, mul(STEEL, 1.15) if (x + y + z) % 6 else GOLD_HI)
    m.box(-1, 1, 133, 140, -1, 1, solid(STEEL))
    for x in range(-16, 16):
        for y in range(106, 118):
            ring = any((ex - 1 <= x < ex + 5) and (108 <= y < 116) and not (ex <= x < ex + 4 and 109 <= y < 115)
                       for ex in (-10, 6))
            if ring or -2 <= x < 2 or abs(x) >= 12:
                for z in (16, 17, 18):
                    m.set(x, y, z, dark(x, y, z, 0) if z < 18 else (GOLD if y >= 115 else mul(STEEL, 1.1)))
    m.sleeve(HEAD, 88, 106, 2, 3, mail(), keep=lambda x, y, z: not (z >= 16 and -12 <= x < 12))
    return m


# ================================================================== weathering
def weather(m, mud_height=18):
    """Mud on the boots, scuffed (lighter) worn edges and corners."""
    MUD = hexc("#4f3f2c")
    out = {}
    v = m.v
    for (x, y, z), c in v.items():
        exposed = sum(1 for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1))
                      if q not in v)
        if exposed >= 3:
            c = mul(c, 1.12)                               # worn edge
        if y < mud_height:
            t = (1 - y / mud_height) * (0.35 + 0.65 * vnoise(x, y, z, 6, 61))
            if t > 0.25:
                c = mix(c, MUD, min(0.75, t))
        out[(x, y, z)] = c
    m.v = out
    return m


# ================================================================== rendering
TOP, LEFT, RIGHT = 1.0, 0.84, 0.66


def render_iso(model, back=False, s=3.3):
    vox = {}
    for (x, y, z), c in model.v.items():
        if back:
            x, z = -1 - x, -1 - z
        vox[(x, y, z)] = c
    c30, s30 = math.cos(math.pi / 6), 0.5

    def P(x, y, z):
        return ((x - z) * c30 * s, (x + z) * s30 * s - y * s)

    us, vs = [], []
    for (x, y, z) in vox:
        u, v = P(x, y, z)
        us.append(u)
        vs.append(v)
    minu, minv = min(us) - 20, min(vs) - 40
    W, H = int(max(us) - minu + 30), int(max(vs) - minv + 30)
    SS = 2                                                 # supersample for smooth edges
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for (x, y, z) in sorted(vox, key=lambda k: (k[0] + k[1] + k[2], k[1])):
        c = vox[(x, y, z)]
        faces = []
        if (x, y + 1, z) not in vox:
            faces.append(([(x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)], TOP,
                          [(x - 1, y + 1, z), (x + 1, y + 1, z), (x, y + 1, z - 1), (x, y + 1, z + 1), (x, y + 2, z)]))
        if (x, y, z + 1) not in vox:
            faces.append(([(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)], LEFT,
                          [(x - 1, y, z + 1), (x + 1, y, z + 1), (x, y + 1, z + 1), (x, y - 1, z + 1), (x, y + 1, z + 2)]))
        if (x + 1, y, z) not in vox:
            faces.append(([(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)], RIGHT,
                          [(x + 1, y + 1, z), (x + 1, y - 1, z), (x + 1, y, z - 1), (x + 1, y, z + 1), (x + 2, y + 1, z)]))
        for pts, f, ao in faces:
            occ = sum(1 for q in ao if q in vox)
            poly = [((u - minu) * SS, (v - minv) * SS) for u, v in (P(*p) for p in pts)]
            d.polygon(poly, fill=mul(c, f * (1.0 - 0.07 * occ)) + (255,))
    return img.resize((W, H), Image.LANCZOS)


def render_front(model, s=3.9):
    best = {}
    for (x, y, z), c in model.v.items():
        if (x, y) not in best or z > best[(x, y)][0]:
            best[(x, y)] = (z, c)
    xs = [k[0] for k in best]
    ys = [k[1] for k in best]
    x0, y1 = min(xs), max(ys)
    W, H = int((max(xs) - x0 + 3) * s), int((y1 - min(ys) + 3) * s)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for (X, y), (z, c) in best.items():
        shade = 0.8 + 0.012 * max(-10, min(20, z))
        up, left = best.get((X, y + 1)), best.get((X - 1, y))
        if up and up[0] > z:
            shade *= 0.72 if up[0] - z > 1 else 0.84
        elif left and left[0] > z + 1:
            shade *= 0.86
        elif up is None or up[0] < z:
            shade *= 1.12
        px, py = (X - x0 + 1) * s, (y1 - y + 1) * s
        d.rectangle([px, py, px + s, py + s], fill=mul(c, shade) + (255,))
    return img


def sheet(name, title, subtitle, notes, model, accent):
    views = [("FRONT", render_front(model)), ("3/4 FRONT", render_iso(model)), ("3/4 BACK", render_iso(model, back=True))]
    pad, top = 40, 150
    Hv = max(v.height for _, v in views)
    W = sum(v.width for _, v in views) + pad * (len(views) + 1)
    wrapped = [textwrap.wrap(n, max(60, int((sum(v.width for _, v in views) + 160) / 11.5))) for n in notes]
    H = top + Hv + 70 + 28 * sum(len(w) for w in wrapped) + 30
    img = Image.new("RGB", (W, H), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 30), title, font=ImageFont.truetype(FONT, 54), fill=hexc(accent))
    d.text((pad, 96), subtitle, font=ImageFont.truetype(FONT2, 24), fill=(200, 205, 212))
    f3 = ImageFont.truetype(FONT2, 20)
    x = pad
    for label, v in views:
        img.paste(v, (x, top + (Hv - v.height)), v)
        d.text((x + v.width // 2 - 40, top + Hv + 14), label, font=f3, fill=(150, 156, 166))
        x += v.width + pad
    y = top + Hv + 60
    for lines in wrapped:
        for i, line in enumerate(lines):
            d.text((pad, y), ("•  " if i == 0 else "    ") + line, font=f3, fill=(214, 218, 224))
            y += 28
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")


SETS = [
    ("1_berserker", "Berserker", "Tier 1  ·  from the Chapter 1 trophies (Cave Bear pelt, Saber Fangs)", [
        "Centerpiece: a whole bear's head worn as a hood - upper jaw over the brow, lower jaw down the cheeks, fangs, wet nose, glass eyes.",
        "Asymmetric: the pelt is slung over the LEFT shoulder as a sash with one paw and ivory claws hanging in front; the left arm gets a studded bracer, the right arm stays bare with rope wraps, blue woad and three twisted gold arm rings.",
        "Layers: skin and woad, a single harness strap with rivets and an iron boss, the pelt on top.  Belt with a knife on the right, a pouch and a drinking horn on the left, leather strips of uneven length.",
        "Colours 60/30/10: brown fur and leather / skin and iron / blue woad.  Weathered: worn edges, mud on the laced boots."], berserker, "#c0662c"),
    ("2_ulfhednar", "Úlfheðinn", "Tier 2  ·  wolf-warrior, from Geri & Freki and Sköll & Hati", [
        "Centerpiece: a snarling wolf head - wrinkled muzzle, open jaws with teeth top and bottom, glowing amber eyes, tall tufted ears.",
        "Asymmetric: the pelt is thrown over the RIGHT shoulder, its forelegs knotted on the left chest; leather lamellar only on the left (shield) side; a painted round shield with a black wolf on the back; a bearded axe on the right hip.",
        "Layers: quilted oxblood gambeson, mail over it (you see the quilting through the rings), rust patches, a ragged mail hem, a torn left sleeve.",
        "Colours 60/30/10: grey fur and mail / oxblood padding / amber eyes and bronze.  Chipped shield paint, mud on the turnshoes."], ulfhednar, "#a9b4c0"),
    ("3_valkyrie", "Valkyrie", "Tier 3  ·  from Huginn & Muninn's feathers and Sleipnir", [
        "Centerpiece: a great winged helm - four rows of single feathers per wing, engraved gold brow band, nasal, cheek guards, rivets and crest.",
        "Asymmetric: a feathered wing-pauldron over stacked plates on the LEFT shoulder, a single plain plate on the right (spear arm); a sash from the right shoulder; the cape thrown over the left; one long braid with gold beads.",
        "Layers: blue linen, shingled silver scales riveted in gold (a few missing, tarnished in places), three layers of tassets (longer on the left), knee cops, layered greaves and sabatons.",
        "Colours 60/30/10: silver / blue / gold and a sapphire set in the chest."], valkyrie, "#8fb4ef"),
    ("4_jarl", "Jarl of the Einherjar", "Tier 4 (best)  ·  Fáfnir's gold and Jörmungandr's scale", [
        "Centerpiece: Fáfnir's head in raised, engraved gold on the chest, with ruby eyes and ivory fangs.",
        "Silhouette: a massive five-plate RIGHT pauldron with two black horns, a modest two-plate left one, a high black fur gorget, the cloak thrown over the left shoulder and pinned by a gold ring brooch on the right.",
        "Layers: quilted crimson gambeson, a ragged mail hauberk to the knees, teal serpent scales with gold rivets, plate and scale vambraces (one each), arm rings, gauntlets with knuckle plates.",
        "Gjermundbu helm with spectacle guard, slim riveted cross bands and spike, mail aventail.  Sword on the left hip.  Colours 60/30/10: dark steel and mail / teal scale / gold and ruby."],
        jarl, "#d9a520"),
]


def main():
    models = {}
    for name, title, sub, notes, fn, accent in SETS:
        models[name] = weather(fn())
        sheet(name, title, sub, notes, models[name], accent)
        print("wrote", OUT / f"{name}.png", len(models[name].v), "voxels")
    views = [render_iso(models[n], s=2.6) for n, *_ in SETS]
    pad = 30
    W = sum(v.width for v in views) + pad * (len(views) + 1)
    Hm = max(v.height for v in views)
    img = Image.new("RGB", (W, Hm + 160), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 24), "Viking endgame armor - concept", font=ImageFont.truetype(FONT, 44), fill=GOLD)
    x = pad
    for v, (name, title, *_r) in zip(views, SETS):
        img.paste(v, (x, 100 + Hm - v.height), v)
        d.text((x + 10, Hm + 114), title, font=ImageFont.truetype(FONT2, 22), fill=(214, 218, 224))
        x += v.width + pad
    img.save(OUT / "0_overview.png")
    print("wrote", OUT / "0_overview.png")


if __name__ == "__main__":
    main()
