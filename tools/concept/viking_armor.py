#!/usr/bin/env python3
"""
Concept art for the pack's Viking endgame armor: each set is built as a voxel model on a Minecraft player
(1 voxel = half a pixel, the detail a GeckoLib armor model allows) and rendered front, 3/4 front and 3/4 back.

    python3 tools/concept/viking_armor.py  ->  docs/viking_armor/*.png
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "viking_armor"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT2 = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ------------------------------------------------------------------ helpers
def h(*a):
    """Deterministic hash noise in [0, 1)."""
    n = 0
    for v in a:
        n = (n * 0x9E3779B1 + (v & 0xFFFFFFFF) * 0x85EBCA77 + 0x165667B1) & 0xFFFFFFFF
        n ^= n >> 15
    n = (n * 0x2C1B3C6D) & 0xFFFFFFFF
    n ^= n >> 12
    return (n & 0xFFFF) / 65536.0


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mul(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


class Model:
    def __init__(self):
        self.v = {}

    def box(self, x0, x1, y0, y1, z0, z1, paint, shell_only=False, keep=None):
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    edge = x in (x0, x1 - 1) or y in (y0, y1 - 1) or z in (z0, z1 - 1)
                    if shell_only and not edge:
                        continue
                    if keep and not keep(x, y, z):
                        continue
                    c = paint(x, y, z) if callable(paint) else paint
                    if c is None:
                        self.v.pop((x, y, z), None)
                    else:
                        self.v[(x, y, z)] = c

    def put(self, x, y, z, c):
        self.v[(x, y, z)] = c

    def clear(self, x0, x1, y0, y1, z0, z1):
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    self.v.pop((x, y, z), None)

    def mirror_x(self, pts):
        """pts: list of (x,y,z,c) placed on the +x side; adds the -x mirror (x -> -1-x)."""
        for x, y, z, c in pts:
            self.v[(x, y, z)] = c
            self.v[(-1 - x, y, z)] = c


# ------------------------------------------------------------------ materials (texel = 2 voxels)
def fur(base, dark=0.72, light=1.12):
    base = hexc(base) if isinstance(base, str) else base

    def p(x, y, z):
        t = h(x // 2, z // 2, (y + int(4 * h(x // 2, z // 2))) // 3)
        f = dark + (light - dark) * t
        return mul(base, f)
    return p


def mail(base="#8f959c"):
    base = hexc(base)

    def p(x, y, z):
        a = ((x // 2) + (y // 2) + (z // 2)) % 2
        ring = (x + y + z) % 2 == 0
        f = (1.08 if a else 0.78) * (1.0 if ring else 0.9)
        return mul(base, f)
    return p


def scales(base, edge=None):
    """Overlapping scales: 4x4-voxel cells, rows offset, rounded dark lower edge, bright top."""
    base = hexc(base)
    edge = hexc(edge) if edge else mul(base, 0.55)

    def p(x, y, z):
        row = y // 4
        u = (x + z + (row % 2) * 2) % 4
        v = y % 4
        if v == 0:
            return edge if u in (0, 3) else mul(base, 0.7)
        if v == 1 and u in (0, 3):
            return mul(base, 0.8)
        if v == 3:
            return mul(base, 1.28)
        return mul(base, 1.0 + 0.12 * (h(x // 4, row, z // 4) - 0.5))
    return p


def plate(base, rivet=None, every=6):
    base = hexc(base)
    rivet = hexc(rivet) if rivet else mul(base, 1.35)

    def p(x, y, z):
        if (x % every == 2) and (y % every == 2):
            return rivet
        return mul(base, 0.95 + 0.12 * h(x // 3, y // 3, z // 3))
    return p


def cloth(base, stripe=None):
    base = hexc(base)
    stripe = hexc(stripe) if stripe else None

    def p(x, y, z):
        f = 0.92 + 0.14 * h(x // 2, y // 2, z // 2)
        return mul(base, f)
    return p


def leather(base="#6b4428"):
    base = hexc(base)

    def p(x, y, z):
        f = 0.9 + 0.18 * h(x // 2, y // 2, z // 2)
        if y % 8 == 0 and (x + z) % 2 == 0:
            f = 1.3      # stitching
        return mul(base, f)
    return p


def solid(c):
    c = hexc(c)
    return lambda x, y, z: c


GOLD = hexc("#d9a520")
GOLD_HI = hexc("#ffe27a")
GOLD_LO = hexc("#8a5d0c")
STEEL = hexc("#6f757d")
STEEL_DARK = hexc("#3c4046")
SKIN = hexc("#c98f6b")
SKIN_DARK = hexc("#a46e50")


def gold(x, y, z):
    t = h(x // 2, y // 2, z // 2)
    return GOLD_HI if t > 0.82 else (GOLD_LO if t < 0.15 else GOLD)


# ------------------------------------------------------------------ base player
# voxel boxes (half pixels). Player faces +z.  y: feet 0 -> head top 64.
HEAD = (-8, 8, 48, 64, -8, 8)
BODY = (-8, 8, 24, 48, -4, 4)
ARM_R = (8, 16, 24, 48, -4, 4)
ARM_L = (-16, -8, 24, 48, -4, 4)
LEG_R = (0, 8, 0, 24, -4, 4)
LEG_L = (-8, 0, 0, 24, -4, 4)


def base_player(m, beard="#7a4a22", hair="#7a4a22", eyes="#3a6fb0"):
    beard, hair, eyes = hexc(beard), hexc(hair), hexc(eyes)
    m.box(*HEAD, lambda x, y, z: mul(SKIN, 0.97 + 0.06 * h(x, y, z)))
    m.box(*BODY, cloth("#5a4a3a"))
    m.box(*ARM_R, SKIN)
    m.box(*ARM_L, SKIN)
    m.box(*LEG_R, cloth("#4a4038"))
    m.box(*LEG_L, cloth("#4a4038"))
    # face (front plane z = 7): eyes, brows, nose, beard
    for x in range(-8, 8):
        for y in range(48, 64):
            c = None
            if y >= 60:
                c = mul(hair, 0.9 + 0.2 * h(x // 2, y // 2))
            if y in (56, 57) and (x in (-6, -5, -4) or x in (3, 4, 5)):
                c = eyes if x in (-5, 4) else (240, 240, 240)
            if y == 58 and (-7 <= x <= -3 or 2 <= x <= 6):
                c = mul(hair, 0.7)
            if y in (53, 54, 55) and x in (-1, 0):
                c = SKIN_DARK
            if y < 54 and not (y in (52, 53) and -3 <= x <= 2):
                c = mul(beard, 0.85 + 0.3 * h(x // 2, y // 2))
            if y in (52,) and -3 <= x <= 2:
                c = (90, 40, 30)      # mouth
            if c:
                m.put(x, y, 7, c)
    # beard braids hanging below the chin
    for y in range(40, 48):
        for x in (-3, -2, 1, 2):
            if y > 41 or x in (-2, 1):
                m.put(x, y, 7, mul(beard, 0.8 + 0.3 * h(x, y)))
                m.put(x, y, 6, mul(beard, 0.7))


# ------------------------------------------------------------------ armor pieces (shared shapes)
def helmet_shell(m, paint, face_open_below=None):
    m.box(-9, 9, 47, 65, -9, 9, paint, shell_only=True,
          keep=lambda x, y, z: not (face_open_below and z == 8 and y < face_open_below and -8 <= x < 8)
          and not (y == 47))


def chest_shell(m, paint):
    m.box(-9, 9, 23, 49, -5, 5, paint, shell_only=True, keep=lambda x, y, z: y != 48 or abs(x) > 4)


def arm_shells(m, paint, y0=23):
    m.box(8, 17, y0, 49, -5, 5, paint, shell_only=True)
    m.box(-17, -8, y0, 49, -5, 5, paint, shell_only=True)


def leg_shells(m, paint, y0=0, y1=25):
    m.box(-9, 9, y0, y1, -5, 5, paint, shell_only=True,
          keep=lambda x, y, z: not (x in (-1, 0) and -4 <= z < 4 and y < y1 - 2))


def cape(m, paint, y0, y1, x0=-9, x1=9, flare=True):
    for y in range(y0, y1):
        w = 0
        if flare:
            w = int((y1 - y) / (y1 - y0) * 3)
        for x in range(x0 - w, x1 + w):
            for z in (-6, -7):
                m.put(x, y, z, paint(x, y, z))


def belt(m, y0, y1, paint, buckle=None):
    for y in range(y0, y1):
        for x in range(-10, 10):
            for z in range(-6, 6):
                if (abs(x + 0.5) >= 9 or z in (-6, 5)) and abs(x + 0.5) <= 10:
                    m.put(x, y, z, paint(x, y, z))
    if buckle:
        for y in range(y0, y1):
            for x in range(-2, 2):
                m.put(x, y, 6, buckle if (x in (-2, 1) or y in (y0, y1 - 1)) else mul(buckle, 0.6))


def round_shield(m, cx, cy, zface, r, colors, boss, rim):
    """Round shield on the back (zface negative) or arm."""
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > r + 0.3:
                continue
            ang = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            seg = int(ang * len(colors) * 2) % len(colors)
            c = colors[seg]
            if d > r - 1.2:
                c = rim
            elif d < 3:
                c = boss
            m.put(cx + dx, cy + dy, zface, c)
            m.put(cx + dx, cy + dy, zface + (1 if zface > 0 else -1) * (-1), mul(c, 0.8))
    for dx in range(-2, 2):
        for dy in range(-2, 2):
            m.put(cx + dx, cy + dy, zface + (-1 if zface < 0 else 1), mul(boss, 1.1))


# ------------------------------------------------------------------ the four sets
def berserker():
    m = Model()
    base_player(m, beard="#8a3b1c", hair="#8a3b1c")
    bear = fur("#5b3a22")
    bear_light = fur("#7a5434")
    # war paint (blue woad) across the eyes
    for x in range(-8, 8):
        for y in (55, 58):
            if (x + y) % 3 != 0:
                pass
    for x in list(range(-7, -2)) + list(range(2, 7)):
        m.put(x, 59, 7, hexc("#2a4f8a"))
    # bear hood: fur helmet, open face
    helmet_shell(m, bear, face_open_below=60)
    m.box(-9, 9, 59, 66, 7, 11, bear)                       # brow / forehead overhang
    m.box(-5, 5, 58, 64, 11, 17, bear_light)                # snout
    m.box(-4, 4, 59, 62, 16, 18, fur("#9a7450"))            # muzzle
    m.box(-2, 2, 61, 63, 17, 18, solid("#161616"))          # nose
    for x in (-4, 3):                                       # fangs
        m.put(x, 57, 15, (238, 232, 214))
        m.put(x, 58, 15, (238, 232, 214))
    for x in (-7, 6):                                       # bear eyes
        m.put(x, 63, 11, (20, 16, 14))
        m.put(x, 64, 11, (20, 16, 14))
    m.box(-9, -5, 65, 69, -1, 3, bear)                      # ears
    m.box(5, 9, 65, 69, -1, 3, bear)
    m.box(-8, -6, 66, 68, 3, 4, fur("#3a2414"))
    m.box(6, 8, 66, 68, 3, 4, fur("#3a2414"))
    # pelt down the back + paws over the shoulders
    cape(m, bear, 8, 48)
    m.box(-17, -8, 46, 51, -6, 6, bear)                     # shoulder fur
    m.box(8, 17, 46, 51, -6, 6, bear)
    for sx in (1, -1):
        for y in range(38, 47):
            for x in range(9, 15):
                X = x if sx > 0 else -1 - x
                m.put(X, y, 5, bear(X, y, 5))
                m.put(X, y, 6, bear(X, y, 6))
        for x in (9, 11, 13):
            X = x if sx > 0 else -1 - x
            m.put(X, 37, 6, (230, 225, 210))                # claws
    # bare chest with leather harness (X straps), belt, iron buckle
    m.box(-9, 9, 23, 49, -5, 5, lambda x, y, z: mul(SKIN, 0.95 + 0.08 * h(x, y, z)), shell_only=True)
    for y in range(24, 49):
        for x in range(-9, 9):
            for z in (4, -5):
                d1 = abs((x + 0.5) - (y - 36) * 0.6)
                d2 = abs((x + 0.5) + (y - 36) * 0.6)
                if d1 < 1.4 or d2 < 1.4:
                    m.put(x, y, z, leather("#4a2e18")(x, y, z))
    for x in list(range(-6, -2)) + list(range(2, 6)):        # woad on the chest
        m.put(x, 42, 4, hexc("#2a4f8a"))
    belt(m, 24, 28, leather("#3d2512"), buckle=hexc("#9aa0a6"))
    # bracers with iron studs, fur boots, leg wraps
    for X0 in (8, -17):
        m.box(X0, X0 + 9, 23, 34, -5, 5, leather("#4a2e18"), shell_only=True)
        for y in (26, 30):
            for x in range(X0 + 1, X0 + 8, 3):
                m.put(x, y, 5, hexc("#b8bec4"))
    leg_shells(m, lambda x, y, z: (hexc("#3b3128") if (x + y) % 6 < 3 else hexc("#5a4a3a"))
               if y > 9 else fur("#4a2e1a")(x, y, z), 0, 24)
    m.box(-10, 10, 0, 9, -6, 6, fur("#4a2e1a"), shell_only=True,
          keep=lambda x, y, z: not (x in (-1, 0)))
    return m


def ulfhednar():
    m = Model()
    base_player(m, beard="#5c5248", hair="#5c5248", eyes="#c48a1a")
    wolf = fur("#8e8a84")
    wolf_light = fur("#c9c4bc")
    helmet_shell(m, wolf, face_open_below=60)
    m.box(-9, 9, 59, 66, 7, 10, wolf)
    m.box(-4, 4, 59, 64, 10, 17, wolf_light)                 # long narrow snout
    m.box(-3, 3, 60, 63, 16, 18, fur("#d8d3cb"))
    m.box(-1, 1, 62, 64, 17, 18, solid("#141414"))
    for x in (-3, 2):
        m.put(x, 58, 15, (236, 230, 214))
    for x in (-7, 6):
        m.put(x, 64, 10, hexc("#e0a020"))                    # amber eyes
    for sx in (1, -1):                                        # tall pointed ears
        for i, y in enumerate(range(65, 73)):
            w = max(1, 4 - i // 2)
            for x in range(5, 5 + w):
                X = x if sx > 0 else -1 - x
                for z in (0, 1):
                    m.put(X, y, z, wolf(X, y, z))
                m.put(X, y, 2, fur("#d0b0a0")(X, y, 2) if w > 1 else wolf(X, y, 2))
    cape(m, wolf, 6, 48)
    m.box(-11, 11, 44, 50, -7, 7, fur("#6e6a66"), shell_only=True)   # fur ruff around the shoulders
    chest_shell(m, mail())
    belt(m, 26, 29, leather("#4a3220"), buckle=hexc("#b07a34"))
    for y in range(29, 32):                                  # wolf-tooth trophy necklace
        pass
    for x in range(-6, 6, 2):
        m.put(x, 44, 5, (236, 230, 214))
        m.put(x, 43, 5, (236, 230, 214))
    arm_shells(m, mail())
    for X0 in (8, -17):
        m.box(X0, X0 + 9, 23, 33, -5, 5, leather("#4a3220"), shell_only=True)
    leg_shells(m, lambda x, y, z: (hexc("#3a3a3e") if (x - y) % 5 < 2 else hexc("#55565c"))
               if y > 8 else leather("#3d2a1a")(x, y, z), 0, 24)
    # wolf-pelt tail of the cloak
    m.box(-2, 2, 2, 8, -8, -6, fur("#7a7672"))
    return m


def valkyrie():
    m = Model()
    base_player(m, beard="#e2c26a", hair="#e2c26a", eyes="#3f7fd0")
    # no beard: re-skin the lower face
    for x in range(-8, 8):
        for y in range(48, 54):
            m.put(x, y, 7, mul(SKIN, 0.98))
    for x in range(-2, 2):
        m.put(x, 51, 7, (170, 80, 80))
    for y in range(40, 48):
        for x in range(-3, 3):
            m.v.pop((x, y, 7), None)
            m.v.pop((x, y, 6), None)
    silver = plate("#c4cad2", "#eef2f6", every=5)
    helmet_shell(m, silver, face_open_below=59)
    m.box(-9, 9, 58, 61, 8, 9, gold)                         # brow band
    m.box(-1, 1, 51, 61, 8, 10, silver)                      # nasal
    m.box(-1, 1, 65, 67, -7, 8, gold)                        # crest
    feather = [hexc("#fbfbfb"), hexc("#e7e9ee"), hexc("#cfd4dc")]
    # wings on the helmet sides: flat feathered wings in the side plane, sweeping up and back
    for sx in (1, -1):
        for z in range(4, -13, -1):
            t = 4 - z                                   # 0 at the front root -> 16 at the tip
            bot = 57 + int(t * 0.55)
            top = 61 + int(t * 0.95) - (max(0, t - 12) * 2)
            out = 9 + (1 if t > 6 else 0) + (1 if t > 11 else 0)
            for y in range(bot, top + 1):
                k = (y - bot + t) % 4                   # diagonal feather lines
                edge = y in (bot, top)
                c = hexc("#c9ced8") if edge else (hexc("#ffffff") if k else hexc("#dfe3ea"))
                for x in (out, out + 1):
                    X = x if sx > 0 else -1 - x
                    m.put(X, y, z, c if x == out + 1 else mul(c, 0.9))
            if t < 4:
                for x in (out, out + 1):
                    X = x if sx > 0 else -1 - x
                    m.put(X, bot, z, GOLD)
    # long blonde braids
    for sx in (1, -1):
        for y in range(34, 50):
            for x in (7, 8):
                X = x if sx > 0 else -1 - x
                m.put(X, y, 6, mul(hexc("#e2c26a"), 0.8 + 0.3 * ((y // 2) % 2)))
    chest_shell(m, scales("#c4cad2", "#7e8794"))
    for y in range(23, 49):                                   # gold trim at neck and hem
        for x in range(-9, 9):
            for z in (-5, 4):
                if y in (23, 24, 47, 48) or abs(x + 0.5) > 8:
                    m.put(x, y, z, gold(x, y, z))
    m.box(8, 19, 43, 50, -6, 6, lambda x, y, z: feather[(x + y) % 3], shell_only=True)   # feather pauldrons
    m.box(-19, -8, 43, 50, -6, 6, lambda x, y, z: feather[(x + y) % 3], shell_only=True)
    arm_shells(m, cloth("#3c62a6"))
    for X0 in (8, -17):
        m.box(X0, X0 + 9, 23, 34, -5, 5, silver, shell_only=True)
        m.box(X0, X0 + 9, 33, 35, -5, 5, gold, shell_only=True)
    # blue skirt with white border, silver greaves
    m.box(-10, 10, 12, 26, -6, 6, lambda x, y, z: hexc("#f1f1f1") if y < 14 else cloth("#3c62a6")(x, y, z),
          shell_only=True, keep=lambda x, y, z: z in (-6, 5) or abs(x + 0.5) > 9)
    leg_shells(m, silver, 0, 13)
    cape(m, cloth("#7fa6e0"), 4, 48)
    for y in range(4, 48):
        for x in (-12, -11, 10, 11):
            if (x, y, -7) in m.v:
                m.put(x, y, -7, gold(x, y, -7))
    return m


def jarl():
    m = Model()
    base_player(m, beard="#b8b2a8", hair="#b8b2a8", eyes="#6aa0c8")
    dark = plate("#4a4f57", "#9aa2ac", every=6)
    serpent = scales("#2c8a7a", "#123f3a")
    helmet_shell(m, dark, face_open_below=60)
    # Gjermundbu spectacle guard: frames around the eyes + nasal
    for x in range(-9, 9):
        for y in range(54, 61):
            ring_l = -7 <= x <= -2 and (y in (54, 59, 60) or x in (-7, -2))
            ring_r = 1 <= x <= 6 and (y in (54, 59, 60) or x in (1, 6))
            nasal = x in (-1, 0)
            if ring_l or ring_r or nasal:
                m.put(x, y, 8, gold(x, y, 8) if y >= 59 else mul(STEEL, 1.05))
    m.box(-9, 9, 59, 61, -9, 9, gold, shell_only=True, keep=lambda x, y, z: not (z == 8 and False))
    m.box(-1, 1, 64, 67, -9, 9, gold)                        # crest ridge
    m.box(-9, 9, 44, 48, -9, 9, mail("#7d838b"), shell_only=True,
          keep=lambda x, y, z: not (z == 8 and -4 <= x < 4))  # aventail
    # fur collar and gold pauldrons
    m.box(-11, 11, 46, 51, -7, 7, fur("#2a221c"), shell_only=True)
    for X0, X1 in ((8, 20), (-20, -8)):
        for y in range(41, 50):
            for x in range(X0, X1):
                for z in range(-7, 7):
                    top = y == 49 or (y == 48 and (x + z) % 2 == 0)
                    outer = x in (X0, X1 - 1) or z in (-7, 6) or top
                    if outer and y >= 41 + (abs(x - (X0 + X1) / 2) // 3):
                        m.put(x, y, z, gold(x, y, z) if (y - 41) % 3 else GOLD_LO)
    chest_shell(m, serpent)
    for y in range(23, 49):                                   # gold edges and a rune line down the middle
        for x in range(-9, 9):
            for z in (-5, 4):
                if y in (23, 24) or abs(x + 0.5) > 8:
                    m.put(x, y, z, gold(x, y, z))
    rune = ["X.X", ".X.", "X.X", "...", "XXX", "X..", "XX.", "...", ".X.", "XXX", ".X.", "..."]
    for i, row in enumerate(rune):
        for j, ch in enumerate(row):
            if ch == "X":
                m.put(-2 + j, 44 - i * 1 - 0, 5, GOLD_HI)
    belt(m, 25, 28, gold, buckle=GOLD_HI)
    arm_shells(m, mail())
    for X0 in (8, -17):
        m.box(X0, X0 + 9, 23, 35, -5, 5, serpent, shell_only=True)
        m.box(X0, X0 + 9, 34, 36, -5, 5, gold, shell_only=True)
    # serpent-scale tassets, dark greaves with gold
    m.box(-10, 10, 12, 26, -6, 6, serpent, shell_only=True,
          keep=lambda x, y, z: (z in (-6, 5) or abs(x + 0.5) > 9) and not (x in (-1, 0) and y < 20))
    leg_shells(m, lambda x, y, z: gold(x, y, z) if y in (10, 11) else dark(x, y, z), 0, 13)
    # red cloak with gold border and brooch
    cape(m, cloth("#8a1c1c"), 2, 49)
    for (x, y, z) in list(m.v):
        if z == -7 and m.v.get((x, y, -6)) and (y in (2, 3) or (x - 1, y, -7) not in m.v or (x + 1, y, -7) not in m.v):
            m.put(x, y, -7, gold(x, y, -7))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if 1.2 < math.hypot(dx, dy) < 2.6:
                m.put(6 + dx, 45 + dy, 6, GOLD_HI)
    return m


# ------------------------------------------------------------------ rendering
TOP, LEFT, RIGHT = 1.0, 0.84, 0.66


def render_iso(model, back=False, s=7):
    vox = {}
    for (x, y, z), c in model.v.items():
        if back:
            x, z = -1 - x, -1 - z
        vox[(x, y, z)] = c
    xs = [k[0] for k in vox]
    ys = [k[1] for k in vox]
    zs = [k[2] for k in vox]
    c30, s30 = math.cos(math.pi / 6), 0.5

    def P(x, y, z):
        return ((x - z) * c30 * s, (x + z) * s30 * s - y * s)

    corners = [P(x, y, z) for x in (min(xs), max(xs) + 1) for y in (min(ys), max(ys) + 1) for z in (min(zs), max(zs) + 1)]
    minu = min(c[0] for c in corners) - 20
    minv = min(c[1] for c in corners) - 20
    W = int(max(c[0] for c in corners) - minu + 20)
    H = int(max(c[1] for c in corners) - minv + 20)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for (x, y, z) in sorted(vox, key=lambda k: (k[0] + k[1] + k[2], k[1])):
        c = vox[(x, y, z)]
        faces = []
        if (x, y + 1, z) not in vox:
            faces.append(([(x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)], TOP))
        if (x, y, z + 1) not in vox:
            faces.append(([(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)], LEFT))
        if (x + 1, y, z) not in vox:
            faces.append(([(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)], RIGHT))
        for pts, f in faces:
            poly = [(u - minu, v - minv) for u, v in (P(*p) for p in pts)]
            d.polygon(poly, fill=mul(c, f) + (255,))
    return img


def render_front(model, back=False, s=9):
    best = {}
    for (x, y, z), c in model.v.items():
        X = -1 - x if back else x
        depth = -z if back else z
        k = (X, y)
        if k not in best or depth > best[k][0]:
            best[k] = (depth, c)
    xs = [k[0] for k in best]
    ys = [k[1] for k in best]
    x0, y1 = min(xs), max(ys)
    W = (max(xs) - x0 + 1) * s
    H = (y1 - min(ys) + 1) * s
    img = Image.new("RGBA", (W + 2 * s, H + 2 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for (X, y), (depth, c) in best.items():
        shade = 0.82 + 0.018 * max(-6, min(10, depth))      # nearer = brighter
        px, py = (X - x0 + 1) * s, (y1 - y + 1) * s
        d.rectangle([px, py, px + s - 1, py + s - 1], fill=mul(c, shade) + (255,))
    return img


def sheet(name, title, subtitle, notes, model, bg="#14171c", accent="#d9a520"):
    views = [("FRONT", render_front(model)), ("3/4 FRONT", render_iso(model)), ("3/4 BACK", render_iso(model, back=True))]
    pad = 40
    top = 150
    Hv = max(v.height for _, v in views)
    W = sum(v.width for _, v in views) + pad * (len(views) + 1)
    H = top + Hv + 70 + 30 * len(notes) + 30
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # ground glow
    f1 = ImageFont.truetype(FONT, 54)
    f2 = ImageFont.truetype(FONT2, 24)
    f3 = ImageFont.truetype(FONT2, 20)
    d.text((pad, 30), title, font=f1, fill=hexc(accent))
    d.text((pad, 96), subtitle, font=f2, fill=(200, 205, 212))
    x = pad
    for label, v in views:
        y = top + (Hv - v.height)
        img.paste(v, (x, y), v)
        d.text((x + v.width // 2 - 40, top + Hv + 14), label, font=f3, fill=(150, 156, 166))
        x += v.width + pad
    y = top + Hv + 60
    for n in notes:
        d.text((pad, y), "•  " + n, font=f3, fill=(214, 218, 224))
        y += 30
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")
    return img


SETS = [
    ("1_berserker", "Berserker", "Tier 1  ·  from the Chapter 1 trophies (Cave Bear pelt, Saber Fangs)", [
        "Bear-head hood: snout, fangs and ears over an open face with blue war paint.",
        "Bare chest with crossed leather harness, iron-studded bracers, bear pelt down the back and paws over the shoulders.",
        "Fur boots and wrapped legs.  Set idea: rage - more damage the lower your health."], berserker, "#c0662c"),
    ("2_ulfhednar", "Úlfheðinn", "Tier 2  ·  wolf-warrior, from Geri & Freki and Sköll & Hati", [
        "Grey wolf-head hood with long snout, amber eyes and tall pointed ears.",
        "Chainmail shirt under a wolf pelt and fur ruff, wolf-tooth necklace, leather bracers.",
        "Set idea: speed and night vision; nearby tamed wolves fight harder."], ulfhednar, "#a9b4c0"),
    ("3_valkyrie", "Valkyrie", "Tier 3  ·  from Huginn & Muninn's feathers and Sleipnir", [
        "Silver winged helm with gold brow band, nasal and crest; long blonde braids.",
        "Silver scale cuirass with gold trim, feather pauldrons, blue skirt and sky-blue cape.",
        "Set idea: slow falling and a double jump (a glide when sprinting)."], valkyrie, "#8fb4ef"),
    ("4_jarl", "Jarl of the Einherjar", "Tier 4 (best)  ·  Fáfnir's gold and Jörmungandr's scale", [
        "Gjermundbu spectacle helm in dark steel with gold, crest ridge and mail aventail.",
        "Teal serpent-scale armor edged in dragon gold with a rune line, gold pauldrons, fur collar.",
        "Red cloak with gold border and ring brooch.  Set idea: the strongest armor in the pack, resists everything Ragnarok throws."],
        jarl, "#d9a520"),
]


def main():
    imgs = []
    for name, title, sub, notes, fn, accent in SETS:
        imgs.append(sheet(name, title, sub, notes, fn(), accent=accent))
        print("wrote", OUT / f"{name}.png")
    # overview: the four 3/4 views side by side
    views = [render_iso(fn(), s=6) for *_, fn, _ in SETS]
    pad = 30
    W = sum(v.width for v in views) + pad * (len(views) + 1)
    H = max(v.height for v in views) + 160
    img = Image.new("RGB", (W, H), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 24), "Viking endgame armor - concept", font=ImageFont.truetype(FONT, 44), fill=GOLD)
    x = pad
    for v, (name, title, *_r) in zip(views, SETS):
        img.paste(v, (x, 100 + max(w.height for w in views) - v.height), v)
        d.text((x + 10, H - 46), title, font=ImageFont.truetype(FONT2, 22), fill=(214, 218, 224))
        x += v.width + pad
    img.save(OUT / "0_overview.png")
    print("wrote", OUT / "0_overview.png")
    weapon_sheet()


# ------------------------------------------------------------------ legendary weapons (flat 2-voxel-thick items)
def item(pixels):
    m = Model()
    for (x, y), c in pixels.items():
        for z in (0, 1):
            m.put(x, y, z, c if z == 1 else mul(c, 0.8))
    return m


def dane_axe():
    px = {}
    wood = hexc("#6e4a2a")
    for y in range(0, 70):                                   # long ash haft
        for x in (0, 1):
            px[(x, y)] = mul(wood, 0.85 + 0.25 * h(x, y // 3))
    for y in range(8, 18):                                   # leather grip
        for x in (-1, 0, 1, 2):
            px[(x, y)] = hexc("#3a2414") if (y % 2) else hexc("#4e3220")
    for y in range(60, 66):
        for x in (-1, 0, 1, 2):
            px[(x, y)] = STEEL_DARK
    for y in range(46, 72):                                   # bearded head
        t = (y - 46) / 26
        reach = int(4 + 14 * math.sin(t * math.pi) ** 0.7 + (6 if y < 54 else 0) * (1 - (y - 46) / 8))
        for x in range(2, 2 + reach):
            edge = x >= 2 + reach - 2
            px[(x, y)] = hexc("#e4e8ee") if edge else mul(STEEL, 0.9 + 0.2 * h(x // 2, y // 2))
    for (x, y) in ((6, 60), (8, 58), (6, 56), (8, 54)):      # runes
        px[(x, y)] = GOLD
    return item(px)


def gungnir():
    px = {}
    ash = hexc("#4a3020")
    for y in range(0, 84):
        for x in (0, 1):
            px[(x, y)] = mul(ash, 0.85 + 0.25 * h(x, y // 3))
    for y0 in (6, 30, 54, 64):                                # gold bands
        for y in range(y0, y0 + 3):
            for x in (-1, 0, 1, 2):
                px[(x, y)] = gold(x, y, 0)
    for y in range(34, 52, 3):                               # glowing runes up the shaft
        px[(0, y)] = hexc("#7fd4ff")
        px[(1, y + 1)] = hexc("#7fd4ff")
    for y in range(66, 70):
        for x in range(-2, 4):
            px[(x, y)] = gold(x, y, 0)
    for y in range(70, 96):                                   # leaf-shaped blade
        t = (y - 70) / 26
        w = int(1 + 5 * math.sin(min(1, t * 1.6) * math.pi / 2) * (1 - t) ** 0.6)
        for x in range(1 - w, 1 + w):
            mid = x in (0, 1)
            px[(x, y)] = hexc("#7fd4ff") if mid and y % 3 == 0 else (hexc("#f2f5f9") if mid else mul(hexc("#c9d0d8"), 0.95 + 0.1 * h(x, y)))
    return item(px)


def fenrirs_fang():
    px = {}
    for y in range(0, 4):                                     # pommel
        for x in range(-2, 4):
            px[(x, y)] = STEEL_DARK
    for y in range(4, 16):                                    # grip wrapped in black wolf fur
        for x in (-1, 0, 1, 2):
            px[(x, y)] = mul(hexc("#222024"), 0.8 + 0.5 * h(x, y))
    for y in range(16, 20):                                   # guard: two fangs
        for x in range(-7, 9):
            px[(x, y)] = STEEL_DARK if abs(x - 0.5) < 6 else hexc("#e8e2d0")
    for y in range(20, 74):                                   # curved fang blade, ivory with red veins
        t = (y - 20) / 54
        cx = 0.5 + 9 * t * t
        w = 4.5 * (1 - t) ** 0.8 + 0.6
        for x in range(int(cx - w), int(cx + w) + 1):
            dark_edge = x <= cx - w + 1
            vein = abs((x - cx) - 1.5 * math.sin(y / 5)) < 0.6
            c = hexc("#b81f1f") if vein else (mul(hexc("#d9d2bf"), 0.75) if dark_edge else mul(hexc("#efe9d8"), 0.92 + 0.12 * h(x, y // 2)))
            px[(x, y)] = c
    return item(px)


def round_shield_item():
    px = {}
    r = 22
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d > r + 0.4:
                continue
            ang = math.atan2(dy, dx) + d / 9                  # painted swirl
            seg = int((ang % (2 * math.pi)) / (2 * math.pi) * 6) % 2
            c = hexc("#a52a1e") if seg else hexc("#e9dfc8")
            c = mul(c, 0.9 + 0.15 * h(dx // 2, dy // 2))
            if d > r - 2:
                c = mul(STEEL, 0.9 + 0.2 * h(dx, dy)) if (int(math.degrees(math.atan2(dy, dx))) % 30) > 3 else hexc("#c9ced6")
            elif d < 5:
                c = mul(STEEL, 1.1 - d * 0.06)
            px[(dx, dy + r)] = c
    return item(px)


def weapon_sheet():
    items = [("Dane Axe", "Jarl tier: two-handed, cleaves shields", dane_axe()),
             ("Gungnir", "Odin's spear: never misses (returns when thrown)", gungnir()),
             ("Fenrir's Fang", "Final weapon, from Fenrir: bleeds and howls", fenrirs_fang()),
             ("Round Shield", "Painted linden-wood shield with iron boss and rim", round_shield_item())]
    renders = [render_front(m, s=7) for *_, m in items]
    pad = 50
    top = 130
    Hv = max(r.height for r in renders)
    col = [max(r.width, 300) for r in renders]
    W = sum(col) + pad * (len(renders) + 1)
    H = top + Hv + 140
    img = Image.new("RGB", (W, H), "#14171c")
    d = ImageDraw.Draw(img)
    d.text((pad, 30), "Legendary Viking weapons - concept", font=ImageFont.truetype(FONT, 48), fill=GOLD)
    x = pad
    f2, f3 = ImageFont.truetype(FONT, 24), ImageFont.truetype(FONT2, 17)
    import textwrap
    for (name, note, _), r, cw in zip(items, renders, col):
        img.paste(r, (x + (cw - r.width) // 2, top + Hv - r.height), r)
        d.text((x, top + Hv + 16), name, font=f2, fill=(230, 232, 236))
        for i, line in enumerate(textwrap.wrap(note, 30)):
            d.text((x, top + Hv + 52 + 22 * i), line, font=f3, fill=(160, 166, 176))
        x += cw + pad
    img.save(OUT / "5_weapons.png")
    print("wrote", OUT / "5_weapons.png")


if __name__ == "__main__":
    main()
