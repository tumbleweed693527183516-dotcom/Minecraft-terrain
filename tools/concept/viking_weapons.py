#!/usr/bin/env python3
"""
Viking weapon concepts, built like the armour (tools/concept/viking_armor_v2.py): 4 voxels per pixel, real
layers (core, wraps, bands, inlays, trinkets), one centerpiece each, 60-30-10 colours and battle wear.

    python3 tools/concept/viking_weapons.py  ->  docs/viking_weapons/*.png
"""
import importlib.util
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("va", ROOT / "tools/concept/viking_armor_v2.py")
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)
h, vnoise, hexc, mul, mix = va.h, va.vnoise, va.hexc, va.mul, va.mix
OUT = ROOT / "docs" / "viking_weapons"

STEEL = hexc("#8e959e")
STEEL_EDGE = hexc("#e2e7ee")
DARK_IRON = hexc("#3c4048")
GOLD, GOLD_HI, GOLD_LO = va.GOLD, va.GOLD_HI, va.GOLD_LO
IVORY = va.IVORY
ASH = hexc("#8a6a44")
DARK_WOOD = hexc("#3e2a1c")
LEATHER, LEATHER_DARK = va.LEATHER, va.LEATHER_DARK
RUNE_GLOW = hexc("#6fe0ff")


def vgold(engraved=True):
    g = va.gold(engraved)
    return lambda x, y, z, d=0: g(x, y, z, d)


class W(va.Model):
    """A weapon model: no body to avoid, so everything is placed."""

    def set(self, x, y, z, c, over_body=True):
        if c is not None:
            self.v[(x, y, z)] = c


def runes(n, seed=0):
    """Elder-futhark-like rune glyphs (3x5 dot patterns)."""
    glyphs = ["X.X/.X./X.X/.X./X.X", "XXX/X../XX./X../X..", "X../X../XXX/X.X/X.X", ".X./XXX/.X./.X./.X.",
              "X.X/XXX/X.X/X.X/X.X", "XX./X.X/XX./X.X/XX.", "X.X/X.X/.X./X.X/X.X", "XXX/.X./.X./.X./XXX"]
    return [glyphs[int(h(i, seed) * len(glyphs))] for i in range(n)]


def wood(base, grain=True):
    def m(x, y, z, d=0):
        g = math.sin((x * 0.9 + z * 0.7) + y * 0.08 + 6 * vnoise(x, y, z, 14, 3))
        return mul(base, 0.82 + 0.14 * (g + 1) / 2 + 0.08 * h(x, y // 3, z))
    return m


def steel(base=STEEL):
    def m(x, y, z, d=0):
        c = mul(base, 0.86 + 0.2 * vnoise(x, y, z, 9, 11))
        if (x * 2 + y) % 17 == 0 and h(x // 5, y // 5) > 0.55:
            c = mul(c, 1.25)                                   # scratches
        if vnoise(x, y, z, 5, 12) > 0.8:
            c = mix(c, hexc("#6a4a32"), 0.45)                  # rust spots
        return c
    return m


def haft(m, y0, y1, r, mat, x=0, z=0):
    """A round-ish haft (octagonal in voxels) along y."""
    for y in range(y0, y1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + r * 0.6:
                    m.set(x + dx, y, z + dz, mat(x + dx, y, z + dz))


def wrap(m, y0, y1, r, col, pitch=4, x=0, z=0, cross=False):
    """Leather or wire wrapping, standing proud of the haft, spiralling."""
    for y in range(y0, y1):
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                dd = dx * dx + dz * dz
                if r * r < dd <= (r + 1) * (r + 1) + r:
                    ang = math.atan2(dz, dx)
                    s = (y + ang / (2 * math.pi) * pitch) % pitch
                    s2 = (y - ang / (2 * math.pi) * pitch) % pitch
                    on = s < pitch * 0.55 or (cross and s2 < pitch * 0.3)
                    c = col if on else mul(col, 0.62)
                    m.set(x + dx, y, z + dz, mul(c, 0.9 + 0.2 * h(dx, y, dz)))


def band(m, y0, y1, r, mat, x=0, z=0):
    for y in range(y0, y1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + r:
                    m.set(x + dx, y, z + dz, mat(x + dx, y, z + dz) if callable(mat) else mat)


def blade_profile(m, x0, x1, y0, y1, inside, thick, mat, edge=None, nicks=0.0, seed=0):
    """Fill a flat shape (in the x-y plane) with thickness thick(x, y) half-width in z; the edge is bright and nicked."""
    for x in range(x0, x1):
        for y in range(y0, y1):
            if not inside(x, y):
                continue
            t = thick(x, y)
            is_edge = edge(x, y) if edge else False
            if is_edge and h(x, y, seed) < nicks:
                continue                                       # a nick in the edge
            for z in range(-t, t + 1):
                c = STEEL_EDGE if is_edge else mat(x, y, z)
                m.set(x, y, z, mul(c, 1.0 + 0.03 * z))


def engrave_runes(m, xs, y_top, z, glyphs, col=RUNE_GLOW, step=6, vertical=True):
    for k, g in enumerate(glyphs):
        rows = g.split("/")
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "X":
                    if vertical:
                        m.set(xs + i, y_top - k * step - j, z, col)
                    else:
                        m.set(xs + k * 5 + i, y_top - j, z, col)


# ================================================================== the weapons
def bearded_axe():
    """Berserker: bearded axe. Centerpiece: the axe head with a cave-bear claw lashed under it.
    60 wood/fur/leather, 30 iron, 10 blue woad cord."""
    m = W()
    haft(m, 0, 112, 3, wood(ASH))
    band(m, 0, 4, 4, steel(DARK_IRON))                         # butt cap
    wrap(m, 6, 34, 3, hexc("#5a3a20"), pitch=5, cross=True)    # grip
    m.sphere(0, 110, 0, 3.5, mul(DARK_IRON, 1.1))
    # bear fur wrapped below the head
    for y in range(80, 94):
        for dx in range(-7, 8):
            for dz in range(-7, 8):
                rr = math.hypot(dx, dz)
                lim = 4 + 3 * vnoise(dx, y, dz, 4, 5)
                if 3 < rr <= lim:
                    m.set(dx, y, dz, va.fur("#5b3a22", "#8a6440")(dx, y, dz, int(rr)))
    # socket and head: bearded profile toward +x
    band(m, 94, 112, 4, steel(DARK_IRON))
    def edge_x(y):                                           # convex cutting edge from the toe to the beard tip
        return 27 + 4 * math.sin(math.pi * min(1, max(0, (y - 72) / 42)))
    def top(x):
        return 112 + (x - 4) * 0.15
    def bottom(x):                                           # concave throat sweeping down into the beard
        t = (x - 4) / 22
        return 101 - 29 * min(1, t) ** 2.2
    def inside(x, y):
        return 4 <= x <= edge_x(y) and bottom(x) <= y <= top(x)
    blade_profile(m, 4, 33, 68, 117, inside, lambda x, y: 3 if x < 10 else (2 if x < 22 else 1),
                  steel(), edge=lambda x, y: x >= edge_x(y) - 1.5, nicks=0.25, seed=1)
    for x in range(8, 13):                                      # punched maker's marks
        m.set(x, 106, 4, DARK_IRON)
    for (rx, ry) in ((6, 108), (6, 99)):                        # rivets through the socket
        m.sphere(rx - 2, ry, 0, 1.4, mul(STEEL, 1.2))
    # the bear claw lashed under the head with a blue cord and a bead
    pts = [(2, 88, 5, 1.0), (7, 84, 7, 0.85), (10, 78, 8, 0.6), (10, 72, 8, 0.35), (8, 68, 7, 0.15)]
    m.tube(pts, 2.6, lambda x, y, z, t: mix(IVORY, hexc("#7a6a50"), t * 0.6))
    for y in range(84, 91):
        for dx in range(-5, 6):
            m.set(dx, y, 6 if y % 2 else 5, hexc("#2a5fb0"))
    for y in range(66, 84):
        m.set(-3, y, 6, hexc("#2a5fb0"))
    m.sphere(-3, 64, 6, 2.0, GOLD)
    return m


def wolf_seax():
    """Úlfheðinn: broken-back seax with a pattern-welded fuller, antler grip and a bronze wolf-head pommel.
    60 steel, 30 antler and leather, 10 amber."""
    m = W()
    BRONZE = hexc("#b07a34")
    # blade: single edge on the left, broken back on the right, pointing up
    def inside(x, y):
        if y < 30 or y > 104:
            return False
        t = (y - 30) / 74
        back = 6 if t < 0.72 else 6 - (t - 0.72) / 0.28 * 13       # the "broken back" angle
        edge = -6 + t * 2.5 if t < 0.85 else -3.9 + (t - 0.85) / 0.15 * 9.0
        return edge <= x <= back
    def mat(x, y, z):
        if 0 <= x <= 3 and 36 < y < 92:                         # pattern-welded fuller (twisted bands)
            k = int(2 * math.sin(y * 0.55 + x * 1.3)) % 2
            return mul(hexc("#7d848c") if k else hexc("#4a5058"), 0.95 + 0.1 * h(x, y))
        return steel()(x, y, z)
    blade_profile(m, -8, 8, 30, 106, inside, lambda x, y: 2 if x > 0 else 1, mat,
                  edge=lambda x, y: not inside(x - 2, y), nicks=0.18, seed=2)
    engrave_runes(m, -4, 86, 3, runes(4, 7), col=hexc("#c8d0d8"), step=7)
    # guard plate, antler grip with bronze bands, wolf-head pommel with amber eyes
    for y in range(26, 30):
        for x in range(-7, 9):
            for z in range(-3, 4):
                m.set(x, y, z, mul(BRONZE, 0.9 + 0.2 * h(x, y, z)))
    haft(m, 6, 26, 3, lambda x, y, z: mul(hexc("#d8ccb0"), 0.8 + 0.25 * vnoise(x, y, z, 3, 9)))
    for y0 in (8, 17, 24):
        band(m, y0, y0 + 2, 4, BRONZE)
    for x in range(-5, 6):                                       # wolf head (ears, snout, eyes)
        for y in range(-4, 7):
            for z in range(-4, 5):
                if (x * x) / 30 + ((y - 1) ** 2) / 22 + (z * z) / 20 <= 1:
                    m.set(x, y, z, mul(BRONZE, 0.85 + 0.25 * h(x, y, z)))
    for z in range(4, 10):
        for x in range(-2, 3):
            for y in range(-2, 2):
                m.set(x, y, z, mul(BRONZE, 0.9))
    for sx in (-3, 3):
        for y in range(6, 10):
            m.set(sx, y, 0, BRONZE)
        m.set(sx, 2, 4, hexc("#ffb020"))
    # sheath beside it: leather with bronze chape and mouth, a wolf-tooth hanging from a thong
    for y in range(28, 96):
        for x in range(16, 30):
            for z in range(-3, 4):
                t = (y - 28) / 68
                if 16 + t * 3 <= x <= 29 - max(0, t - 0.8) * 30:
                    m.set(x, y, z, mul(LEATHER_DARK, 0.9 + 0.2 * h(x // 2, y // 3, z)) if abs(z) < 3 else LEATHER)
    for y in range(90, 96):
        for x in range(16, 30):
            for z in (-3, 3):
                m.set(x, y, z, BRONZE)
    for y in range(28, 34):
        for x in range(18, 24):
            for z in (-3, 3):
                m.set(x, y, z, BRONZE)
    for k, y in enumerate(range(50, 80, 10)):                   # stitching
        for x in range(17, 29, 2):
            m.set(x, y, 4, hexc("#c8b48a"))
    for y in range(70, 88):
        m.set(31, y, 0, LEATHER_DARK)
    for j in range(5):
        m.set(31, 69 - j, 0, IVORY)
        m.set(32, 69 - j, 0, IVORY if j < 2 else mul(IVORY, 0.8))
    return m


def valkyrie_sword():
    """Valkyrie: straight double-edged sword. Centerpiece: the crossguard is a pair of spread wings.
    60 silver steel, 30 blue leather, 10 gold and sapphire."""
    m = W()
    def inside(x, y):
        if y < 34 or y > 130:
            return False
        t = (y - 34) / 96
        w = 7 - 3 * t if t < 0.9 else (7 - 3 * 0.9) * (1 - (t - 0.9) / 0.1)
        return abs(x + 0.5) <= w
    def mat(x, y, z):
        if abs(x + 0.5) < 2 and 38 < y < 118:
            return mul(STEEL, 0.75)                             # fuller (recessed below)
        return steel(hexc("#b4bcc6"))(x, y, z)
    blade_profile(m, -8, 8, 34, 131, inside,
                  lambda x, y: 0 if abs(x + 0.5) < 2 and 38 < y < 118 else (2 if abs(x + 0.5) < 4 else 1),
                  mat, edge=lambda x, y: not inside(x + 1 if x >= 0 else x - 1, y), nicks=0.06, seed=3)
    engrave_runes(m, -1, 112, 1, runes(9, 11), col=RUNE_GLOW, step=8)
    # wings guard
    for sx in (1, -1):
        for i in range(24):
            x = (4 + i) * sx + (0 if sx > 0 else -1)
            top = 34 + int(10 * math.sin(i / 23 * math.pi * 0.85)) + i // 3
            bot = 28 + i // 4
            for y in range(bot, top):
                feather_row = (y - bot + i) % 4
                c = hexc("#f2f4f8") if feather_row else hexc("#c8ced8")
                if i < 4:
                    c = GOLD
                for z in (-2, -1, 0, 1):
                    m.set(x, y, z, mul(c, 1.0 - 0.04 * abs(z)))
    for x in range(-4, 4):
        for y in range(28, 36):
            for z in range(-3, 4):
                m.set(x, y, z, vgold()(x, y, z, 0))
    # grip: blue leather with silver wire; pommel: gold with a sapphire
    haft(m, 8, 28, 3, lambda x, y, z: mul(hexc("#2a4c8e"), 0.9 + 0.2 * h(x, y // 2, z)))
    wrap(m, 9, 27, 3, hexc("#d8dde4"), pitch=3)
    for x in range(-6, 6):
        for y in range(0, 8):
            for z in range(-4, 5):
                if (x + 0.5) ** 2 / 36 + (y - 4) ** 2 / 16 + z * z / 20 <= 1:
                    m.set(x, y, z, vgold()(x, y, z, 0))
    m.sphere(0, 4, 4, 2.4, hexc("#2f6fd8"))
    m.set(0, 5, 6, hexc("#9fd0ff"))
    return m


def dane_axe():
    """Jarl: two-handed Dane axe. Centerpiece: the crescent head, its toe ending in Fáfnir's golden head with a
    ruby eye.  60 dark iron and wood, 30 gold, 10 ruby and teal."""
    m = W()
    haft(m, 0, 160, 3, wood(DARK_WOOD))
    band(m, 0, 5, 4, vgold())
    for y in range(40, 138):                                    # spiral gold wire up the haft
        ang = y * 0.45
        m.set(int(round(3.6 * math.cos(ang))), y, int(round(3.6 * math.sin(ang))), GOLD_HI)
    wrap(m, 8, 34, 3, hexc("#2a1a10"), pitch=4, cross=True)
    for y in range(110, 140):                                   # langets: iron strips down the haft
        for z in (-4, 4):
            m.set(0, y, z, DARK_IRON)
            if y % 6 == 0:
                m.set(0, y, z + (1 if z > 0 else -1), GOLD)
    for y in range(36, 40):
        for dz in range(-6, 7):                                   # teal tassel ring
            m.set(-4, y, dz, hexc("#2c8a7a"))
    for j in range(16):
        for dz in range(-3, 4):
            m.set(-5 - (j // 6), 35 - j, dz, mul(hexc("#2c8a7a"), 0.8 + 0.3 * h(dz, j)))
    band(m, 140, 162, 4, steel(DARK_IRON))
    def edge_x(y):                                           # long convex edge between the two horns
        return 34 + 7 * math.sin(math.pi * min(1, max(0, (y - 112) / 68)))
    def top(x):
        return 162 + 18 * ((x - 4) / 34) ** 1.7
    def bottom(x):
        return 140 - 28 * ((x - 4) / 30) ** 1.7
    def inside(x, y):
        return 4 <= x <= edge_x(y) and bottom(x) <= y <= top(x)
    def mat(x, y, z):
        if va.knot_engraved(x * 2, y, z) and 9 < x < 28 and bottom(x) + 6 < y < top(x) - 6 and abs(z) >= 2:
            return GOLD                                         # knotwork inlay on the cheek
        return steel(hexc("#5a606a"))(x, y, z)
    blade_profile(m, 4, 42, 108, 182, inside, lambda x, y: 3 if x < 12 else (2 if x < 30 else 1), mat,
                  edge=lambda x, y: x >= edge_x(y) - 1.5, nicks=0.12, seed=4)
    # Fáfnir's head at the toe of the blade
    cx, cy = 31, 116
    for x in range(cx - 6, cx + 7):
        for y in range(cy - 7, cy + 6):
            for z in range(-4, 5):
                if ((x - cx) / 6.5) ** 2 + ((y - cy) / 6.5) ** 2 + (z / 4.5) ** 2 <= 1:
                    m.set(x, y, z, vgold()(x, y, z, 0))
    for x in range(cx - 13, cx - 5):
        for y in range(cy - 4, cy + 1):
            for z in range(-2, 3):
                m.set(x, y, z, vgold(False)(x, y, z, 0))     # snout pointing down the haft
    for z in (-5, 5):
        m.sphere(cx + 1, cy + 2, z, 1.6, hexc("#c01830"))
    for x in range(cx + 2, cx + 9):
        m.set(x, cy + 6 + (x - cx) // 2, 0, GOLD_HI)             # horn
    return m


def gungnir():
    """Odin's spear. Centerpiece: the gold collar with Huginn and Muninn's heads facing out; glowing runes.
    60 silver and ash, 30 gold, 10 rune light."""
    m = W()
    haft(m, 0, 150, 3, wood(hexc("#6a4a30")))
    for y in range(0, 10):
        r = max(0, 3 - (10 - y) // 3)
        band(m, y, y + 1, r, steel())
    wrap(m, 50, 76, 3, hexc("#3a2414"), pitch=3, cross=True)
    engrave_runes(m, -1, 140, 4, runes(8, 21), col=RUNE_GLOW, step=7)
    for y0 in (80, 98, 146):
        band(m, y0, y0 + 3, 4, vgold())
    # collar and ravens
    band(m, 150, 158, 5, vgold())
    for sx in (1, -1):
        for x in range(5, 18):
            for y in range(148, 164):
                for z in range(-5, 6):
                    if ((x - 10) / 6.5) ** 2 + ((y - 156) / 6.0) ** 2 + (z / 4.6) ** 2 <= 1:
                        m.set(x * sx, y, z, mul(hexc("#22222c"), 0.8 + 0.4 * h(x, y, z)))
        for x in range(16, 23):                                 # beaks
            for y in range(154, 158):
                for z in (-1, 0, 1):
                    m.set(x * sx, y - (x - 16) // 2, z, GOLD)
        for z in (-5, 5):                                       # eyes
            m.set(12 * sx, 159, z, RUNE_GLOW)
            m.set(13 * sx, 159, z, RUNE_GLOW)
    # blade: long leaf with a raised mid-rib and runes
    def inside(x, y):
        if y < 158 or y > 214:
            return False
        t = (y - 158) / 56
        w = 2 + 9 * math.sin(min(1, t * 1.4) * math.pi / 2) * (1 - t) ** 0.7
        return abs(x + 0.5) <= w
    blade_profile(m, -12, 12, 158, 215, inside, lambda x, y: 3 if abs(x + 0.5) < 1.5 else (2 if abs(x + 0.5) < 5 else 1),
                  steel(hexc("#c9d0d8")), edge=lambda x, y: not inside(x + 1 if x >= 0 else x - 1, y), nicks=0.04, seed=5)
    engrave_runes(m, -5, 190, 3, runes(3, 31), col=RUNE_GLOW, step=0, vertical=False)
    return m


def fenrirs_fang():
    """Final weapon. Centerpiece: a blade that is a giant fang, still bound by a strand of Gleipnir.
    60 ivory and black, 30 dark iron, 10 blood red."""
    m = W()
    def inside(x, y):
        if y < 34 or y > 150:
            return False
        t = (y - 34) / 116
        cx = 14 * t * t
        w = 10 * (1 - t) ** 0.75 + 0.8
        return cx - w <= x <= cx + w * 0.9
    def mat(x, y, z):
        t = (y - 34) / 116
        cx = 14 * t * t
        vein = abs((x - cx) - 2 * math.sin(y / 6)) < 0.8 or abs((x - cx + 4) - 1.5 * math.sin(y / 4 + 1)) < 0.6
        if vein and t < 0.8:
            return hexc("#b81f1f") if h(x, y) > 0.3 else hexc("#ff4a4a")
        c = mul(IVORY, 0.82 + 0.2 * vnoise(x, y, z, 10, 51))
        return mix(c, hexc("#a89878"), 0.4 * vnoise(x, y, z, 6, 52))
    def edge(x, y):
        t = (y - 34) / 116
        cx = 14 * t * t
        w = 10 * (1 - t) ** 0.75 + 0.8
        return x <= cx - w + 1.2
    blade_profile(m, -14, 26, 34, 151, inside, lambda x, y: 3 if y < 100 else 2, mat, edge=None)
    for y in range(36, 140, 5):                                 # serrated inner edge (teeth)
        t = (y - 34) / 116
        cx = 14 * t * t
        w = 10 * (1 - t) ** 0.75 + 0.8
        for j in range(3):
            m.set(int(cx - w) - j, y - j, 0, mul(IVORY, 1.05))
    # Gleipnir: a thin silken ribbon wound around the base, glinting
    for y in range(36, 60):
        for x in range(-12, 12):
            t = (y - 34) / 116
            if abs((x + y * 1.3) % 9 - 4.5) < 0.9 and inside(x, y):
                m.set(x, y, 4, hexc("#f4f0ff") if (x + y) % 3 else hexc("#ffffff"))
                m.set(x, y, -4, hexc("#d8d0f0"))
    # guard: a black iron jaw with teeth; grip: black fur; pommel: a wolf skull
    for x in range(-14, 15):
        for y in range(26, 36):
            for z in range(-4, 5):
                if abs(x) < 14 - (y - 26) * 0.6:
                    m.set(x, y, z, steel(DARK_IRON)(x, y, z))
    for x in range(-12, 13, 4):
        for j in range(4):
            m.set(x, 36 + j, 5, IVORY)
    haft(m, 8, 26, 3, lambda x, y, z: va.fur("#1c1a1c", "#4a4648")(x, y, z, 3))
    for x in range(-6, 7):
        for y in range(-2, 9):
            for z in range(-5, 6):
                if (x / 6.2) ** 2 + ((y - 3) / 5.5) ** 2 + (z / 5) ** 2 <= 1:
                    m.set(x, y, z, mul(hexc("#e6dcc4"), 0.85 + 0.2 * h(x, y, z)))
    for sx in (-2, 2):
        for y in (3, 4):
            m.set(sx, y, 5, hexc("#220808"))
            m.set(sx, y, 6, hexc("#ff3030"))
    return m


def round_shield():
    """Linden-plank shield. Centerpiece: the domed iron boss; the painted wolf is chipped and gouged, an arrow is
    still stuck in it.  60 wood, 30 red-and-bone paint, 10 iron."""
    m = W()
    R = 44
    for x in range(-R, R + 1):
        for y in range(-R, R + 1):
            d = math.hypot(x, y)
            if d > R + 0.3:
                continue
            plank = (x + 200) // 11
            gap = (x + 200) % 11 == 0
            woodc = mul(hexc("#8a6a44"), 0.78 + 0.25 * h(plank, 7) + 0.08 * math.sin(y * 0.4 + plank))
            ang = math.atan2(y, x)
            spiral = int(((ang + math.pi) / (2 * math.pi) * 4 + d / 16)) % 2
            paint = hexc("#8a1c1c") if spiral else hexc("#e2d6bc")
            wolf = (abs(x) < 10 - y * 0.25 and -14 < y < 12) or (abs(abs(x) - 8) < 3 and 10 < y < 20)
            if wolf and d > 9:
                paint = hexc("#1a1a1a")
            chipped = vnoise(x, y, 0, 6, 61) > 0.73 or (gap and h(x, y) > 0.5)
            c = woodc if chipped else mul(paint, 0.85 + 0.2 * h(x // 3, y // 3))
            if gap:
                c = mul(c, 0.6)
            for z in (0, 1, 2):
                m.set(x, y, z, c if z == 2 else mul(woodc, 0.85))
            if d > R - 3:                                        # rawhide rim, stitched
                for z in (0, 1, 2, 3):
                    m.set(x, y, z, mul(hexc("#b8a078"), 0.85 + 0.2 * h(x, y)) if int(math.degrees(ang) + 720) % 9 else LEATHER_DARK)
    # axe gouges
    for (gx, gy, ang) in ((18, 16, 0.6), (-24, -10, -0.4)):
        for t in range(-8, 9):
            x, y = int(gx + t * math.cos(ang)), int(gy + t * math.sin(ang))
            m.v.pop((x, y, 2), None)
            m.v.pop((x, y + 1, 2), None)
            m.set(x, y, 1, hexc("#5a4028"))
    # domed boss with rivets
    for x in range(-11, 12):
        for y in range(-11, 12):
            d = math.hypot(x, y)
            if d <= 11:
                hgt = int(round(math.sqrt(max(0, 121 - d * d)) * 0.7))
                for z in range(3, 3 + max(1, hgt)):
                    m.set(x, y, z, steel(hexc("#6f757d"))(x, y, z))
                if 9.6 < d <= 11 and int(math.degrees(math.atan2(y, x)) + 720) % 60 < 8:
                    m.set(x, y, 4, mul(STEEL, 1.4))
    # back: two cross battens, an iron grip bar over the boss hole, a leather carrying strap
    for x in range(-38, 39):
        for y in (-18, 18):
            for dy in range(-2, 3):
                if math.hypot(x, y + dy) < R - 3:
                    for z in (-1, -2):
                        m.set(x, y + dy, z, mul(hexc("#6a4a2c"), 0.85 + 0.2 * h(x // 4, y)))
            if x % 9 == 0:
                m.set(x, y, -3, mul(STEEL, 1.2))                # clench nails
    for y in range(-12, 13):
        for x in range(-2, 3):
            for z in (-1, -2, -3):
                m.set(x, y, z, steel(DARK_IRON)(x, y, z))
    for y in range(-6, 7):
        for x in (-1, 0, 1):
            m.set(x, y, -4, mul(LEATHER_DARK, 1.1))             # leather-wrapped grip
    for x in range(-30, 31):
        yy = int(26 - (x / 30) ** 2 * 6)
        for z in (-3, -4):
            m.set(x, yy, z, LEATHER)
    # an arrow stuck in it (asymmetry)
    pts = [(-20, 22, 3, 1.0), (-28, 30, 14, 1.0), (-36, 38, 26, 1.0)]
    m.tube(pts, 0.9, lambda x, y, z, t: hexc("#9a7a50"))
    for k in range(6):
        for j in range(3):
            m.set(-35 - j, 38 + k // 2, 25 + k, hexc("#e8e4dc") if j else hexc("#5a4a3a"))
    return m


# ================================================================== sheets
WEAPONS = [
    ("1_bearded_axe", "Bearded Axe", "Berserker  ·  tier 1", [
        "Centerpiece: the bearded iron head with a cave-bear claw lashed beneath it by a blue woad cord and a gold bead.",
        "Layers: ash haft, crossed leather grip, a collar of bear fur, iron socket with rivets and maker's marks.",
        "Worn: a nicked edge, scratches and rust spots.  Colours: wood, fur and leather / iron / blue."], bearded_axe, "#c0662c"),
    ("2_wolf_seax", "Wolf Seax", "Úlfheðinn  ·  tier 2", [
        "Centerpiece: a bronze wolf-head pommel with amber eyes on an antler grip bound with bronze bands.",
        "Broken-back blade with a pattern-welded fuller (twisted light and dark steel) and engraved runes; a nicked edge.",
        "Shown with its stitched leather sheath, bronze chape and mouth, and a wolf tooth hanging from a thong."], wolf_seax, "#a9b4c0"),
    ("3_valkyrie_sword", "Valkyrie Sword", "Valkyrie  ·  tier 3", [
        "Centerpiece: the crossguard is a pair of spread silver wings with gold roots.",
        "Straight double-edged blade with a deep fuller full of glowing runes.",
        "Blue leather grip wound with silver wire; a gold pommel set with a sapphire."], valkyrie_sword, "#8fb4ef"),
    ("4_dane_axe", "Jarl's Dane Axe", "Jarl of the Einherjar  ·  tier 4", [
        "Centerpiece: a great crescent head whose toe ends in Fáfnir's golden head with ruby eyes; gold knotwork inlaid in the cheek.",
        "Long dark haft with a spiral of gold wire, iron langets, gold bands, a crossed grip and a teal tassel.",
        "Colours: dark iron and wood / gold / ruby and teal."], dane_axe, "#d9a520"),
    ("5_gungnir", "Gungnir", "Legendary  ·  Odin's spear", [
        "Centerpiece: a gold collar where Huginn and Muninn's black heads face outward, their eyes lit with rune light.",
        "Long leaf blade with a raised mid-rib; runes glow up the ash shaft between gold bands; an iron butt spike."], gungnir, "#6fe0ff"),
    ("6_fenrirs_fang", "Fenrir's Fang", "Legendary  ·  the final weapon", [
        "Centerpiece: the blade is Fenrir's own fang, curved and serrated, with blood-red veins, still bound by a strand of Gleipnir.",
        "Guard of black iron shaped like a jaw with teeth, a black wolf-fur grip and a wolf-skull pommel with red eyes."], fenrirs_fang, "#ff4a4a"),
    ("7_round_shield", "Round Shield", "Every tier  ·  linden planks", [
        "Centerpiece: a domed, riveted iron boss.  Painted planks (red-and-bone spiral and a black wolf), chipped to bare wood.",
        "Stitched rawhide rim, two axe gouges and an arrow still stuck in it."], round_shield, "#e2d6bc"),
]


def render_side(model, s=3.0):
    """Orthographic view from the side (looking along -z)."""
    return va.render_front(model, s=s)


def sheet(name, title, sub, notes, model, accent):
    views = [("SIDE", render_side(model)), ("3/4", va.render_iso(model, s=2.6)),
             ("BACK 3/4", va.render_iso(model, back=True, s=2.6))]
    pad, top = 40, 150
    Hv = max(v.height for _, v in views)
    W_ = sum(v.width for _, v in views) + pad * (len(views) + 1)
    W_ = max(W_, 900)
    wrapped = [textwrap.wrap(n, int(W_ / 11.5)) for n in notes]
    H = top + Hv + 70 + 28 * sum(len(w) for w in wrapped) + 30
    img = Image.new("RGB", (W_, H), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 30), title, font=ImageFont.truetype(va.FONT, 54), fill=hexc(accent))
    d.text((pad, 96), sub, font=ImageFont.truetype(va.FONT2, 24), fill=(200, 205, 212))
    f3 = ImageFont.truetype(va.FONT2, 20)
    x = pad
    for label, v in views:
        img.paste(v, (x, top + Hv - v.height), v)
        d.text((x + v.width // 2 - 30, top + Hv + 14), label, font=f3, fill=(150, 156, 166))
        x += v.width + pad
    y = top + Hv + 60
    for lines in wrapped:
        for i, line in enumerate(lines):
            d.text((pad, y), ("•  " if i == 0 else "    ") + line, font=f3, fill=(214, 218, 224))
            y += 28
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")


def main():
    models = []
    for name, title, sub, notes, fn, accent in WEAPONS:
        m = va.smooth(fn())
        models.append((title, m))
        sheet(name, title, sub, notes, m, accent)
        print("wrote", name, len(m.v), "voxels")
    views = [(t, va.render_iso(m, s=2.0)) for t, m in models]
    pad = 30
    W_ = sum(v.width for _, v in views) + pad * (len(views) + 1)
    Hm = max(v.height for _, v in views)
    img = Image.new("RGB", (W_, Hm + 170), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 24), "Viking weapons - concept", font=ImageFont.truetype(va.FONT, 44), fill=GOLD)
    x = pad
    for t, v in views:
        img.paste(v, (x, 100 + Hm - v.height), v)
        d.text((x, Hm + 120), t, font=ImageFont.truetype(va.FONT2, 20), fill=(214, 218, 224))
        x += v.width + pad
    img.save(OUT / "0_overview.png")
    print("wrote overview")


if __name__ == "__main__":
    main()
