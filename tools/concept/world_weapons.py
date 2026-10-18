#!/usr/bin/env python3
"""
Weapons of the other civilizations in the pack, plus the endgame weapon with a molten core.
Same method as tools/concept/viking_weapons.py.

    python3 tools/concept/world_weapons.py  ->  docs/world_weapons/*.png
"""
import importlib.util
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("vw", ROOT / "tools/concept/viking_weapons.py")
vw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vw)
va = vw.va
h, vnoise, hexc, mul, mix = va.h, va.vnoise, va.hexc, va.mul, va.mix
W, steel, wood, haft, wrap, band, blade_profile = vw.W, vw.steel, vw.wood, vw.haft, vw.wrap, vw.band, vw.blade_profile
vgold = vw.vgold
GOLD, GOLD_HI, GOLD_LO, IVORY = va.GOLD, va.GOLD_HI, va.GOLD_LO, va.IVORY
STEEL, STEEL_EDGE, DARK_IRON = vw.STEEL, vw.STEEL_EDGE, vw.DARK_IRON
OUT = ROOT / "docs" / "world_weapons"
BRONZE = hexc("#b5803a")
LAPIS = hexc("#1f4fa8")


class G(W):
    def __init__(self):
        super().__init__()
        self.emissive = set()

    def glow(self, x, y, z, c):
        self.v[(x, y, z)] = c
        self.emissive.add((x, y, z))


def flat_text(m, x0, y0, z, text, col, scale=1):
    """Tiny 3x5 capitals for inscriptions (SPQR)."""
    font = {"S": "XXX/X../XXX/..X/XXX", "P": "XXX/X.X/XXX/X../X..", "Q": "XXX/X.X/X.X/XXX/..X", "R": "XX./X.X/XX./X.X/X.X"}
    for k, ch in enumerate(text):
        for j, row in enumerate(font[ch].split("/")):
            for i, c in enumerate(row):
                if c == "X":
                    for a in range(scale):
                        for b in range(scale):
                            m.set(x0 + (k * 4 + i) * scale + a, y0 - j * scale - b, z, col)


# ================================================================== civilizations
def khopesh():
    """Egypt. Centerpiece: the Eye of Horus inlaid in gold and lapis on the hooked bronze blade.
    60 bronze / 30 gold and ebony / 10 lapis."""
    m = G()
    haft(m, 6, 28, 3, lambda x, y, z: mul(hexc("#2a1e18"), 0.85 + 0.25 * h(x, y // 2, z)))
    for y0 in (6, 14, 22):
        band(m, y0, y0 + 2, 4, vgold(False))
    for y in range(9, 26, 4):
        for z in (-4, 4):
            m.set(0, y, z, LAPIS)
    m.sphere(0, 3, 0, 4.5, GOLD)
    for x in range(-6, 7):
        for y in range(28, 31):
            for z in range(-3, 4):
                m.set(x, y, z, vgold()(x, y, z))
    bronze = lambda x, y, z: mix(mul(BRONZE, 0.85 + 0.25 * vnoise(x, y, z, 8, 3)), hexc("#3f7a64"), 0.35 * max(0, vnoise(x, y, z, 6, 4) - 0.55) * 2)
    def inside(x, y):
        if 30 <= y <= 74 and -3 <= x <= 3:
            return True                                      # the straight neck
        r = math.hypot(x - 10, y - 74)
        a = math.degrees(math.atan2(y - 74, x - 10))
        return 9.5 <= r <= 17.5 and -45 <= a <= 180
    def edge(x, y):
        r = math.hypot(x - 10, y - 74)
        a = math.degrees(math.atan2(y - 74, x - 10))
        return r >= 16.3 and -45 <= a <= 165 and y > 60
    blade_profile(m, -8, 30, 30, 93, inside, lambda x, y: 2 if y < 74 else 1, bronze, edge=edge, nicks=0.1, seed=7)
    eye = ["..XXXXX..", ".X.....X.", "X..XXX..X", ".X.....X.", "..XXXXX..", "....X..X.", "....X...X"]
    for j, row in enumerate(eye):
        for i, ch in enumerate(row):
            if ch == "X":
                for z in (3, -3):
                    m.set(-4 + i, 66 - j, z, GOLD_HI if j != 2 or i in (0, 8) else LAPIS)
    return m


def guandao():
    """China. Centerpiece: a golden dragon's head swallowing the base of the broad crescent blade.
    60 steel and red lacquer / 30 gold / 10 jade."""
    m = G()
    RED = hexc("#9a1a14")
    haft(m, 0, 168, 3, lambda x, y, z: mul(RED, 0.82 + 0.2 * vnoise(x, y, z, 7, 21)))
    for y0 in (20, 60, 100, 140):
        band(m, y0, y0 + 3, 4, vgold(False))
    for y in range(0, 12):                                    # butt spike
        band(m, y, y + 1, max(1, 4 - (12 - y) // 4), steel(DARK_IRON))
    for y in range(144, 152):                                 # jade ring
        for dx in range(-6, 7):
            for dz in range(-6, 7):
                if 4.2 < math.hypot(dx, dz) <= 6:
                    m.set(dx, y, dz, mul(hexc("#4caf7a"), 0.85 + 0.25 * h(dx, y, dz)))
    for j in range(22):                                       # red tassel
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if math.hypot(dx, dz) <= 3 - j * 0.05:
                    m.set(dx - 7, 143 - j, dz, mul(hexc("#c8281e"), 0.8 + 0.3 * h(dx, j, dz)))
    # dragon head at the top of the haft: a snout over the blade, horns, whiskers, ruby eyes
    for x in range(-7, 12):
        for y in range(166, 182):
            for z in range(-6, 7):
                if ((x - 2) / 8.5) ** 2 + ((y - 173) / 7.5) ** 2 + (z / 6) ** 2 <= 1:
                    m.set(x, y, z, vgold()(x, y, z))
    for x in range(8, 18):
        for y in range(170, 178):
            for z in range(-4, 5):
                if abs(z) < 4 - (x - 8) * 0.25:
                    m.set(x, y, z, vgold(False)(x, y, z))
    for z in (-6, 6):
        m.sphere(4, 177, z, 1.4, hexc("#c01830"))
        for i in range(12):
            m.set(-4 - i, 180 + i // 2, z, GOLD_HI)               # swept-back horns
        for i in range(10):
            m.set(16 + i, 171 - i // 3, z // 2, GOLD_HI)          # whiskers
    def inside(x, y):
        if y < 180 or y > 236:
            return False
        t = (y - 180) / 56
        back = -6 + 3 * t
        front = 4 + 14 * math.sin(min(1, t * 1.3) * math.pi / 2) - 18 * max(0, t - 0.75) ** 1.2
        notch = (-6 <= x <= -2) and 196 < y < 202
        return back <= x <= front and not notch
    blade_profile(m, -8, 22, 180, 237, inside, lambda x, y: 2 if x < 4 else 1, steel(hexc("#a8b0ba")),
                  edge=lambda x, y: not inside(x + 2, y), nicks=0.05, seed=8)
    for y in range(188, 228, 3):                              # a fuller of gold cloud-scroll inlay
        m.set(int(2 + 3 * math.sin(y * 0.3)), y, 2, GOLD)
        m.set(int(2 + 3 * math.sin(y * 0.3)), y, -2, GOLD)
    return m


def gladius():
    """Rome. Centerpiece: a gold aquila (eagle) pommel over a ribbed bone grip; SPQR on the blade.
    60 steel / 30 bone, brass and red / 10 gold."""
    m = G()
    def inside(x, y):
        if y < 32 or y > 104:
            return False
        t = (y - 32) / 72
        w = 7 - 1.5 * math.sin(t * math.pi) if t < 0.8 else 6 * (1 - (t - 0.8) / 0.2)
        return abs(x + 0.5) <= w
    blade_profile(m, -9, 9, 32, 105, inside, lambda x, y: 2 if abs(x + 0.5) < 3 else 1, steel(),
                  edge=lambda x, y: not inside(x + (1 if x >= 0 else -1) * 2, y), nicks=0.12, seed=9)
    flat_text(m, -7, 66, 3, "SPQR", GOLD_HI)
    for x in range(-9, 10):                                   # hemispherical guard (wood with brass plate)
        for y in range(26, 32):
            for z in range(-6, 7):
                if (x / 9.5) ** 2 + ((y - 26) / 6.5) ** 2 + (z / 6.5) ** 2 <= 1:
                    m.set(x, y, z, mul(BRONZE, 0.9 + 0.2 * h(x, y, z)) if y > 30 else mul(hexc("#6a4a30"), 0.9 + 0.2 * h(x, y)))
    haft(m, 10, 26, 3, lambda x, y, z: mul(IVORY, 0.78 if y % 4 == 0 else 0.95))    # ribbed bone grip
    for x in range(-7, 8):                                    # spherical pommel...
        for y in range(2, 10):
            for z in range(-5, 6):
                if (x / 7) ** 2 + ((y - 6) / 4.5) ** 2 + (z / 5.5) ** 2 <= 1:
                    m.set(x, y, z, mul(hexc("#6a4a30"), 0.9 + 0.2 * h(x, y)))
    for x in range(-6, 7):                                    # ...topped by a gold eagle with spread wings
        for y in range(-6, 2):
            if abs(x) < 6 - (y + 6) * 0.4 or (abs(x) < 2 and y > -9):
                for z in (-1, 0, 1):
                    m.set(x, y, z, vgold()(x, y, z))
    for x in range(-2, 3):
        for y in range(-11, -6):
            for z in (-1, 0, 1):
                m.set(x, y, z, GOLD)
    m.set(1, -9, 2, hexc("#1a1a1a"))
    for y in range(40, 50):                                   # red cord tied at the guard
        m.set(7, y, 0, hexc("#9a1a14"))
    return m


def kopis():
    """Greece. Centerpiece: the forward-curved blade with a gold meander (Greek key) along the spine and an owl of
    Athena; a bronze bird-head hilt.  60 steel / 30 bronze / 10 blue enamel."""
    m = G()
    def back(y):
        t = (y - 30) / 70
        return 4 + 6 * math.sin(t * math.pi * 0.9)
    def front(y):
        t = (y - 30) / 70
        return -3 - 9 * t ** 1.6 + (0 if t < 0.85 else (t - 0.85) / 0.15 * 14)
    def inside(x, y):
        return 30 <= y <= 100 and front(y) <= x <= back(y) + 1 - max(0, (y - 92)) * 0.9
    blade_profile(m, -16, 14, 30, 101, inside, lambda x, y: 2 if x > back(y) - 3 else 1, steel(),
                  edge=lambda x, y: x <= front(y) + 1, nicks=0.1, seed=10)
    for y in range(36, 88):                                   # meander along the spine
        bx = int(back(y)) - 2
        k = (y // 2) % 4
        for dx in range(3):
            on = (k == 0) or (dx == 0 and k in (1, 2)) or (dx == 2 and k in (2, 3))
            if on:
                m.set(bx - dx, y, 3, GOLD)
                m.set(bx - dx, y, -3, GOLD)
    owl = [".X.X.", "XXXXX", "XBXBX", "XXXXX", ".XXX.", ".X.X."]
    for j, row in enumerate(owl):
        for i, ch in enumerate(row):
            if ch != ".":
                for z in (3, -3):
                    m.set(-6 + i, 62 - j, z, hexc("#2f6fd8") if ch == "B" else GOLD_HI)
    haft(m, 8, 28, 3, lambda x, y, z: mul(hexc("#3a2a20"), 0.9 + 0.2 * h(x, y // 2, z)))
    for x in range(-6, 7):
        for y in range(28, 31):
            for z in range(-3, 4):
                m.set(x, y, z, mul(BRONZE, 0.9 + 0.2 * h(x, y, z)))
    for y in range(0, 10):                                    # bird-head pommel curving forward
        for x in range(-2 - (10 - y) // 2, 4):
            for z in range(-3, 4):
                m.set(x, y, z, mul(BRONZE, 0.85 + 0.25 * h(x, y, z)))
    m.set(-6, 5, 3, hexc("#2f6fd8"))
    m.set(-6, 5, -3, hexc("#2f6fd8"))
    return m


def macuahuitl():
    """Maya. Centerpiece: rows of black obsidian blades set into a painted wooden club; quetzal feathers.
    60 wood / 30 obsidian / 10 jade and quetzal green."""
    m = G()
    OBS = hexc("#141220")
    haft(m, 0, 30, 3, wood(hexc("#6a4628")))
    wrap(m, 4, 26, 3, hexc("#c8b48a"), pitch=4, cross=True)
    for x in range(-9, 10):                                   # the flat paddle
        for y in range(30, 120):
            t = (y - 30) / 90
            w = 6 + 3 * math.sin(min(1, t * 1.2) * math.pi / 2)
            if abs(x + 0.5) <= w and not (y > 116 and abs(x) > 6):
                for z in (-2, -1, 0, 1, 2):
                    c = wood(hexc("#7a5434"))(x, y, z)
                    if abs(z) == 2 and abs(x + 0.5) < w - 1:   # painted bands: red, turquoise, ochre steps
                        k = ((y // 6) + abs(x) // 3) % 3
                        c = (hexc("#9a2a1c"), hexc("#2a9a8a"), hexc("#c89a3a"))[k] if (y // 3) % 4 else c
                    m.set(x, y, z, c)
    for y in range(34, 116, 6):                               # obsidian blades along both edges
        for side in (-1, 1):
            t = (y - 30) / 90
            w = 6 + 3 * math.sin(min(1, t * 1.2) * math.pi / 2)
            for j in range(5):
                for k in range(-2, 3):
                    if abs(k) <= 2 - j // 2:
                        x = int(side * (w + 1 + j))
                        c = OBS if (j + k) % 3 else hexc("#4a4a6a")       # glossy glints
                        m.set(x, y + k + int(h(y, side) * 2), 0, c)
                        if j < 2:
                            m.set(x, y + k, 1, c)
                            m.set(x, y + k, -1, c)
    for x in range(-3, 4):                                    # jade inlay at the base
        for y in range(36, 42):
            m.set(x, y, 3, mul(hexc("#4caf7a"), 0.9 + 0.2 * h(x, y)))
    for i, col in enumerate((hexc("#1a8a4a"), hexc("#2ab86a"), hexc("#c8281e"))):   # quetzal feathers at the pommel
        for j in range(26):
            x = -4 + i * 3 + int(2 * math.sin(j * 0.3 + i))
            for w in (-1, 0, 1):
                m.set(x + w, -1 - j, 0, mul(col, 0.85 + 0.2 * h(i, j)) if w == 0 else mul(col, 0.7))
    return m


def katana():
    """Japan. Centerpiece: the wavy hamon (temper line) and a round tsuba with a cut-out dragon.
    60 steel / 30 black and white wrap / 10 gold."""
    m = G()
    def spine(y):
        t = (y - 38) / 110
        return 3 + 6 * t * t
    def inside(x, y):
        if y < 38 or y > 150:
            return False
        t = (y - 38) / 110
        w = 5.5 if t < 0.92 else 5.5 * max(0.0, 1 - (t - 0.92) / 0.08) ** 0.6
        return spine(y) - w <= x <= spine(y)
    def mat(x, y, z):
        hamon = spine(y) - 5.5 + 2.2 + 1.0 * math.sin(y * 0.5) + 0.6 * math.sin(y * 1.3)
        if x < hamon:
            return mul(hexc("#e4e8ee"), 0.95 + 0.06 * h(x, y))   # the hardened, frosty edge
        return mul(hexc("#8a919a"), 0.9 + 0.12 * vnoise(x, y, z, 6, 41))
    blade_profile(m, -6, 14, 38, 151, inside, lambda x, y: 1 if x < spine(y) - 3 else 2, mat, edge=None)
    for x in range(-3, 6):                                    # habaki
        for y in range(34, 39):
            for z in range(-3, 4):
                m.set(x, y, z, GOLD)
    for x in range(-12, 13):                                  # tsuba with a dragon cut-out
        for z in range(-12, 13):
            r = math.hypot(x, z)
            if r <= 12:
                ang = math.atan2(z, x)
                cut = 6 < r < 10 and abs(math.sin(ang * 2 + r * 0.6)) < 0.25
                if not cut:
                    for y in (31, 32, 33):
                        m.set(x, y, z, mul(hexc("#2a2622"), 0.9 + 0.2 * h(x, z)) if r < 11 else GOLD)
    haft(m, 2, 31, 3, lambda x, y, z: mul(hexc("#f0ece4"), 0.9 + 0.1 * h(x, y, z)))   # same (rayskin)
    wrap(m, 3, 30, 3, hexc("#1a1a1e"), pitch=6, cross=True)                              # ito diamonds
    for y in (14, 20):
        m.set(4, y, 0, GOLD)
        m.set(-4, y, 0, GOLD)
    band(m, 0, 3, 4, mul(hexc("#2a2622"), 1.0))
    return m


def zweihander():
    """Medieval Germany. Centerpiece: a wavy flamberge blade with parrying hooks and a leather-wrapped ricasso.
    60 steel / 30 black leather / 10 red and brass."""
    m = G()
    def inside(x, y):
        if y < 44 or y > 200:
            return False
        if y < 66:
            return abs(x + 0.5) <= 3                          # ricasso
        t = (y - 66) / 134
        w = 7 - 3 * t if t < 0.92 else 4.2 * (1 - (t - 0.92) / 0.08)
        wave = 1.6 * math.sin(y * 0.32)
        return -w + wave <= x + 0.5 <= w + wave
    blade_profile(m, -12, 12, 44, 201, inside, lambda x, y: 2 if abs(x + 0.5 - 1.6 * math.sin(y * 0.32)) < 3 else 1,
                  steel(), edge=lambda x, y: y > 66 and not inside(x + (1 if x >= 0 else -1) * 2, y), nicks=0.08, seed=11)
    wrap(m, 46, 64, 3, hexc("#1c1a1a"), pitch=4)
    for sx in (1, -1):                                        # parrying hooks
        for i in range(8):
            m.set(sx * (4 + i // 2) + (0 if sx > 0 else -1), 66 + (i if i < 5 else 9 - i), 0, steel()(0, 0, 0))
    for x in range(-22, 23):                                  # crossguard with curled ends
        for y in range(40, 44):
            for z in (-1, 0, 1):
                m.set(x, y, z, steel(DARK_IRON)(x, y, z))
    for sx in (1, -1):
        for i in range(10):
            a = i / 9 * math.pi * 1.2
            m.sphere(int(sx * (22 + 3 * math.sin(a))), int(42 + 4 - 4 * math.cos(a)), 0, 1.6, DARK_IRON)
    haft(m, 8, 40, 3, lambda x, y, z: mul(hexc("#1c1a1a"), 0.9 + 0.2 * h(x, y // 2, z)))
    wrap(m, 9, 39, 3, mul(hexc("#9a1a14"), 1.0), pitch=7)
    m.sphere(0, 4, 0, 5.5, BRONZE)
    for y in range(30, 46):                                   # red tassel on the guard
        m.set(10, y - 10, 2, hexc("#c8281e"))
    return m


# ================================================================== the endgame weapon
def surtr_blade():
    """Ragnarök, Surtr's blade: Fenrir's Fang reforged in the fire giant's forge.  A black, glassy shell cracked all
    over, the molten core glowing through the cracks (white-hot in the middle, orange and red at the edges); the
    pommel is an iron cage holding a ball of the molten core; embers drift off the blade.
    60 black obsidian / 30 molten orange / 10 white-hot."""
    m = G()
    CORE = [hexc("#fff4c8"), hexc("#ffd060"), hexc("#ff9a20"), hexc("#ff5a10"), hexc("#c02008")]
    SHELL = hexc("#16131a")

    def cracks(x, y, scale=9.0, seed=3):
        """Voronoi cell borders: distance to the nearest border, in voxels."""
        cx, cy = math.floor(x / scale), math.floor(y / scale)
        d1 = d2 = 1e9
        for i in range(-1, 2):
            for j in range(-1, 2):
                px = (cx + i + h(cx + i, cy + j, seed)) * scale
                py = (cy + j + h(cx + i, cy + j, seed + 1)) * scale
                d = math.hypot(x - px, y - py)
                if d < d1:
                    d1, d2 = d, d1
                elif d < d2:
                    d2 = d
        return (d2 - d1) / 2

    def width(y):
        t = (y - 46) / 170
        return 13 * (1 - t) ** 0.65 + 1.2

    def centre(y):
        t = (y - 46) / 170
        return 10 * t * t

    def inside(x, y):
        return 46 <= y <= 216 and centre(y) - width(y) <= x <= centre(y) + width(y) * 0.85

    for x in range(-16, 26):
        for y in range(46, 217):
            if not inside(x, y):
                continue
            w = width(y)
            rel = (x - centre(y)) / w
            thick = 4 if abs(rel) < 0.4 else (3 if abs(rel) < 0.7 else 2)
            cr = cracks(x, y) + 0.6 * (vnoise(x, y, 0, 4, 9) - 0.5)
            edge_heat = rel < -0.8 or rel > 0.7                 # the edges glow where they were sharpened
            for z in range(-thick, thick + 1):
                surface = abs(z) == thick
                if surface and cr < 0.55:
                    # a crack: recessed, showing the core; the core is hotter towards the blade's spine
                    heat = min(4, int(cr * 3.0 + abs(rel) * 2.2))
                    m.glow(x, y, z, CORE[heat])
                elif surface and cr < 1.25:
                    m.set(x, y, z, mix(SHELL, hexc("#5a1408"), 0.7))   # cooled crust at the crack edges
                elif edge_heat and surface:
                    m.glow(x, y, z, CORE[3] if h(x, y) > 0.5 else CORE[2])
                else:
                    m.set(x, y, z, mul(SHELL, 0.85 + 0.35 * vnoise(x, y, z, 5, 7)))
    # the inner, serrated edge of the old fang: white-hot teeth
    for y in range(50, 200, 6):
        x0 = int(centre(y) - width(y))
        for j in range(4):
            m.glow(x0 - j, y - j, 0, CORE[min(4, j)])
    # crossguard: two black iron horns curling up, with glowing seams
    for sx in (1, -1):
        pts = [(sx * 4, 42, 0, 1.0), (sx * 14, 40, 0, 0.9), (sx * 22, 46, 0, 0.7), (sx * 25, 56, 0, 0.5), (sx * 22, 64, 0, 0.25)]
        m.tube(pts, 4.0, lambda x, y, z, t: mul(DARK_IRON, 0.8 + 0.3 * h(int(x), int(y))))
        for i in range(0, 20):
            m.glow(sx * (5 + i), 41 + (i // 6), 4, CORE[2 if i % 5 else 1])
    for x in range(-6, 7):
        for y in range(38, 46):
            for z in range(-5, 6):
                m.set(x, y, z, mul(DARK_IRON, 0.8 + 0.3 * h(x, y, z)))
    for x in range(-2, 3):
        for y in range(39, 45):
            m.glow(x, y, 6, CORE[0] if abs(x) < 1 else CORE[1])     # rune of Surtr burning in the guard
    # grip: black leather bound with glowing wire
    haft(m, 14, 38, 3, lambda x, y, z: mul(hexc("#1a1618"), 0.9 + 0.2 * h(x, y // 2, z)))
    for y in range(14, 38):
        ang = y * 0.7
        m.glow(int(round(4 * math.cos(ang))), y, int(round(4 * math.sin(ang))), CORE[2])
    # pommel: an iron cage holding a ball of molten core
    for x in range(-8, 9):
        for y in range(-4, 14):
            for z in range(-8, 9):
                r = math.sqrt(x * x + (y - 5) ** 2 + z * z)
                if r <= 5.5:
                    m.glow(x, y, z, CORE[0] if r < 2.5 else (CORE[1] if r < 4.2 else CORE[2]))
                elif 6.5 <= r <= 8 and (abs(x) < 1.5 or abs(z) < 1.5 or abs(y - 5) < 1.2):
                    m.set(x, y, z, mul(DARK_IRON, 0.85 + 0.3 * h(x, y, z)))
    for y in (-5, 14):
        m.sphere(0, y, 0, 2.0, DARK_IRON)
    # embers drifting off the blade
    for k in range(70):
        y = int(60 + h(k, 1) * 170)
        x = int(centre(y) + (h(k, 2) - 0.3) * 30)
        z = int((h(k, 3) - 0.5) * 18)
        if not inside(x, y):
            m.glow(x, y, z, CORE[int(h(k, 4) * 4)])
    return m


WEAPONS = [
    ("1_khopesh", "Khopesh", "Egypt  ·  Civilizations (Khufu)", [
        "Centerpiece: the Eye of Horus inlaid in gold and lapis on the hooked bronze blade.",
        "Bronze with green patina in places, a gold guard, ebony grip with gold bands and lapis studs, a gold pommel."],
        khopesh, "#d9a520"),
    ("2_guandao", "Dragon Guandao", "China  ·  Civilizations (Qin Shi Huang)", [
        "Centerpiece: a golden dragon's head with ruby eyes, swept-back horns and whiskers, swallowing the base of the broad crescent blade.",
        "Red-lacquered haft with gold bands, a jade ring and a red tassel; gold cloud-scroll inlay up the blade; an iron butt spike."],
        guandao, "#c8281e"),
    ("3_gladius", "Gladius", "Rome  ·  Civilizations (Caesar), Ancient Structures", [
        "Centerpiece: a gold aquila (eagle) with spread wings on the pommel; SPQR inlaid on the blade.",
        "Mainz-pattern blade with a long point, wooden guard with a brass plate, ribbed bone grip, a red cord."], gladius, "#c8281e"),
    ("4_kopis", "Kopis", "Greece  ·  Civilizations (Alexander)", [
        "Centerpiece: the forward-curving blade with a gold meander (Greek key) along the spine and an owl of Athena with sapphire eyes.",
        "Bronze bird-head hilt hooking forward."], kopis, "#2f6fd8"),
    ("5_macuahuitl", "Macuahuitl", "Maya  ·  Ancient Structures (Mayan temples)", [
        "Centerpiece: rows of glossy black obsidian blades set along both edges of a wooden club.",
        "Painted red, turquoise and ochre bands, a jade inlay, a cord-wrapped grip and quetzal feathers hanging from the pommel."],
        macuahuitl, "#2ab86a"),
    ("6_katana", "Katana", "Japan  ·  Ancient Structures (Japanese sites), Ancient Villages", [
        "Centerpiece: the wavy hamon - the frosty hardened edge - and a round iron tsuba with a cut-out dragon rimmed in gold.",
        "Gold habaki, white rayskin under black diamond-wrapped ito, gold menuki."], katana, "#e4e8ee"),
    ("7_zweihander", "Flamberge Zweihänder", "Medieval Germany  ·  Ancient Structures (German sites)", [
        "Centerpiece: a wavy flamberge blade with parrying hooks above a leather-wrapped ricasso.",
        "Long crossguard with curled ends, black grip wound with red cord, a bronze pommel and a red tassel."], zweihander, "#c8281e"),
    ("8_ragnarok", "Ragnarök, Surtr's Blade", "ENDGAME  ·  Fenrir's Fang reforged in the fire giant's forge", [
        "Centerpiece: a molten core. The blade is a black, glassy shell cracked all over; the core glows through every crack - white-hot inside, orange and red at the edges - and the sharpened edges glow with heat.",
        "Black iron horns for a crossguard with glowing seams and a burning rune; grip bound with glowing wire; the pommel is an iron cage holding a ball of the molten core.",
        "Embers drift off the blade.  In game the core glows in the dark (emissive) and can slowly pulse."], surtr_blade, "#ff9a20"),
]


def bloom(img, model_img_glow):
    """Soft glow around emissive pixels."""
    blur = model_img_glow.filter(ImageFilter.GaussianBlur(10))
    return ImageChops.add(img, blur)


def glow_layer(model, renderer, **kw):
    g = G()                                   # same geometry (so the frames line up), only the glowing parts lit
    g.v = {p: (c if p in model.emissive else (0, 0, 0)) for p, c in model.v.items()}
    g.emissive = set(model.emissive)
    full = renderer(model, **kw)
    only = renderer(g, **kw)
    return full, only


def sheet(name, title, sub, notes, model, accent):
    views = []
    for label, fn, kw in (("SIDE", va.render_front, {"s": 3.0}), ("3/4", va.render_iso, {"s": 2.6}),
                          ("BACK 3/4", va.render_iso, {"s": 2.6, "back": True})):
        full, only = glow_layer(model, fn, **kw)
        views.append((label, full, only))
    pad, top = 40, 150
    Hv = max(v.height for _, v, _ in views)
    W_ = max(900, sum(v.width for _, v, _ in views) + pad * (len(views) + 1))
    wrapped = [textwrap.wrap(n, int(W_ / 11.5)) for n in notes]
    H = top + Hv + 70 + 28 * sum(len(w) for w in wrapped) + 30
    img = Image.new("RGB", (W_, H), "#14171c")
    glow = Image.new("RGB", (W_, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad, 30), title, font=ImageFont.truetype(va.FONT, 54), fill=hexc(accent))
    d.text((pad, 96), sub, font=ImageFont.truetype(va.FONT2, 24), fill=(200, 205, 212))
    f3 = ImageFont.truetype(va.FONT2, 20)
    x = pad
    for label, v, only in views:
        img.paste(v, (x, top + Hv - v.height), v)
        glow.paste(only.convert("RGB"), (x, top + Hv - v.height), only)
        d.text((x + v.width // 2 - 30, top + Hv + 14), label, font=f3, fill=(150, 156, 166))
        x += v.width + pad
    img = bloom(img, glow)
    d = ImageDraw.Draw(img)
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
    views = [(t, *glow_layer(m, va.render_iso, s=1.9)) for t, m in models]
    pad = 26
    W_ = sum(v.width for _, v, _ in views) + pad * (len(views) + 1)
    Hm = max(v.height for _, v, _ in views)
    img = Image.new("RGB", (W_, Hm + 170), "#14171c")
    glow = Image.new("RGB", (W_, Hm + 170), (0, 0, 0))
    x = pad
    for t, v, only in views:
        img.paste(v, (x, 100 + Hm - v.height), v)
        glow.paste(only.convert("RGB"), (x, 100 + Hm - v.height), only)
        x += v.width + pad
    img = bloom(img, glow)
    d = ImageDraw.Draw(img)
    d.text((pad, 24), "Civilization weapons + endgame blade", font=ImageFont.truetype(va.FONT, 40), fill=GOLD)
    x = pad
    for t, v, _ in views:
        for i, line in enumerate(textwrap.wrap(t, 14)):
            d.text((x, Hm + 112 + i * 22), line, font=ImageFont.truetype(va.FONT2, 18), fill=(214, 218, 224))
        x += v.width + pad
    img.save(OUT / "0_overview.png")
    print("wrote overview")


if __name__ == "__main__":
    main()
