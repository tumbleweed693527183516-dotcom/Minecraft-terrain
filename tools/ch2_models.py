"""
Chapter 2 boss models (Odin's war against Ragnarok), built with tools/mobkit.py.

    python3 tools/ch2_models.py              # all
    python3 tools/ch2_models.py fenrir       # one

Writes geo/entity/boss/<id>.geo.json and textures/entity/boss/<id>.png (+ _glowmask.png).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mobkit import Model  # noqa: E402


# ------------------------------------------------------------------ Sleipnir: Odin's eight-legged horse
def sleipnir():
    m = Model("sleipnir", tex_w=256, seed=13)
    m.material("coat", "#9ea4ab", "hide", marks=("dapple", "belly", "socks"))
    m.material("leg", "#8a9098", "fur", marks=("socks",))
    m.material("mane", "#e9edf1", "hair")
    m.material("hoof", "#2c2a2e", "dark")
    m.material("muzzle", "#6b7078", "hide")
    m.material("eye", "#8fe8ff", "glow")
    m.material("gold", "#d6a832", "gold")
    m.material("rune_gold", "#c99a2a", "gold", marks=("runes",), rune="#9ff3ff")
    m.material("cloth", "#3b4f8c", "cloth")
    m.material("nostril", "#24232a", "dark")
    m.material("spirit", "#9ff3ff", "glow")                                 # Odin's light in the mane and hooves
    m.look = dict(belly="#c9ced4", belly_cut=0.42, socks="#e4e8ec", socks_h=6)

    m.bone("body", None, (0, 17, 0))
    m.cube("body", (-5, 12, -11), (5, 22, 11), "coat")
    m.cube("body", (-4.5, 11, -10), (4.5, 12, 9), "coat")                 # belly line
    # Odin's barding: blue saddle cloth with gold trim, gold breastplate with glowing runes
    m.cube("body", (-5.5, 16, -5), (5.5, 22.5, 5), "cloth")
    m.cube("body", (-5.6, 15.5, -5.1), (5.6, 16.3, 5.1), "gold")
    m.cube("body", (-2, 22.5, -4), (2, 23.5, 3), "gold")                  # saddle seat
    m.cube("body", (-4.5, 13, -12), (4.5, 20, -11), "rune_gold")
    m.sym("body", (-5.7, 14, -11.2), (-5.0, 21, -5.5), "rune_gold")        # shoulder plates
    m.sym("body", (-5.7, 16, 6), (-5.0, 21, 11.2), "rune_gold")            # flank plates

    m.bone("neck", "body", (0, 20, -9), rot=(28, 0, 0))
    m.cube("neck", (-2.5, 18, -12.5), (2.5, 29, -6.5), "coat")
    m.cube("neck", (-0.8, 19, -6.5), (0.8, 30.5, -4.2), "mane")             # mane along the neck
    m.cube("neck", (-0.6, 20, -4.3), (0.6, 30, -3.4), "spirit")             # its glowing crest
    m.cube("neck", (-2.6, 21, -12.1), (2.6, 22, -6.4), "gold")            # collar

    m.bone("head", "neck", (0, 28, -9), rot=(-20, 0, 0))
    m.cube("head", (-3, 26, -15), (3, 32, -7.5), "coat")
    m.cube("head", (-2.2, 25.5, -21), (2.2, 30, -15), "muzzle")
    m.cube("head", (-1.2, 32, -14), (1.2, 33.5, -8), "mane")              # forelock
    m.sym("head", (-2.8, 32, -9.5), (-1.4, 35, -8.3), "coat")             # ears
    m.sym("head", (-3.05, 29, -13.2), (-2.6, 30.2, -11.8), "eye")
    m.sym("head", (-1.8, 27.5, -21.1), (-0.8, 28.5, -20.9), "nostril")
    m.cube("head", (-3.1, 28.5, -15.2), (3.1, 29.3, -14.6), "gold")       # bridle band
    m.cube("head", (-2.4, 29.5, -19.5), (2.4, 30.6, -12), "rune_gold")     # chanfron (face armour)
    m.cube("head", (-0.6, 30.5, -14), (0.6, 34.5, -12.6), "gold", rot=(-20, 0, 0), pivot=(0, 30.5, -13.3))   # crest spike
    m.sym("head", (-3.2, 31.5, -10), (-2.6, 34.5, -9), "gold", rot=(0, 0, -15), pivot=(-2.9, 31.5, -9.5))  # wing ornaments
    m.sym("head", (-2.4, 26.5, -19.5), (-2.2, 28.5, -15), "gold")         # cheek straps
    m.bone("jaw", "head", (0, 26, -15))
    m.cube("jaw", (-1.9, 24.5, -20.5), (1.9, 26, -15), "muzzle")

    m.bone("tail", "body", (0, 21, 11))
    m.cube("tail", (-1.5, 9, 11), (1.5, 21.5, 14), "mane", rot=(22, 0, 0), pivot=(0, 21, 11))
    m.cube("tail", (-1, 5, 13), (1, 10, 15.5), "mane", rot=(22, 0, 0), pivot=(0, 21, 11))
    m.cube("tail", (-0.7, 3.5, 13.8), (0.7, 5.2, 15.2), "spirit", rot=(22, 0, 0), pivot=(0, 21, 11))

    # eight legs: two on each corner, the inner pair a little shorter in reach
    for name, x, z in (("leg_fl1", -3.3, -9), ("leg_fl2", -3.3, -5), ("leg_bl1", -3.3, 5), ("leg_bl2", -3.3, 9)):
        for side, sx in (("", 1), ("r", -1)):
            bn = name.replace("_fl", "_fr").replace("_bl", "_br") if side else name
            xx = x * sx
            m.bone(bn, "body", (xx, 13, z))
            m.cube(bn, (xx - 1.5, 6, z - 1.5), (xx + 1.5, 13.5, z + 1.5), "leg")
            m.cube(bn, (xx - 1.2, 1.5, z - 1.2), (xx + 1.2, 6, z + 1.2), "leg")
            m.cube(bn, (xx - 1.6, 1.5, z - 1.6), (xx + 1.6, 3, z + 1.6), "mane")       # feathering
            m.cube(bn, (xx - 1.4, 0, z - 1.4), (xx + 1.4, 1.5, z + 1.4), "hoof")
            m.cube(bn, (xx - 1.55, 1.5, z - 1.55), (xx + 1.55, 1.9, z + 1.55), "spirit")    # hooves of light
            m.cube(bn, (xx - 1.65, 10, z - 1.65), (xx + 1.65, 11.2, z + 1.65), "rune_gold")  # leg bands
    return m


# ------------------------------------------------------------------ Fenrir: the bound wolf, slayer of Odin
def fenrir():
    m = Model("fenrir", tex_w=256, seed=29)
    m.material("fur", "#34343c", "fur", marks=("belly", "scars", "back"))
    m.material("ruff", "#1d1d22", "fur", marks=("scars",))
    m.material("leg", "#2c2c33", "fur")
    m.material("muzzle", "#5a5a62", "fur")
    m.material("nose", "#111114", "dark")
    m.material("mouth", "#5a1a1e", "plain")
    m.material("fang", "#e8e0c8", "bone")
    m.material("claw", "#d8d0b8", "bone")
    m.material("eye", "#ff7a1a", "glow")
    m.material("iron", "#4a4d55", "metal")
    m.material("gleipnir", "#ffd77a", "glow")
    m.material("spike", "#141418", "fur")
    m.material("maw", "#ff5a14", "glow")                                    # Ragnarok's fire inside him
    m.look = dict(belly="#4a4a52", belly_cut=0.36, back="#16161a", scar_color="#ff6a1a", scar_glow=True,
                  scars=[((-4, 17, -4), (-4, 13, 2)), ((-4, 16.5, -2.5), (-4, 12.5, 3.5)), ((4, 16, 1), (4, 12, 6)),
                         ((-3.5, 19, -12), (-3.5, 16, -10))])

    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-4, 9.5, -8), (4, 17.5, 9), "fur")
    m.cube("body", (-5, 11, -11), (5, 20.5, -2), "ruff")                 # shaggy shoulders
    m.cube("body", (-1.5, 20.5, -9), (1.5, 22, -3), "ruff")              # hackles
    m.cube("body", (-1, 17.5, -1), (1, 18.5, 7), "ruff")                 # ridge down the back
    for i, z in enumerate((-9.5, -7, -4.5, -2, 0.5, 3, 5.5)):                # bristling spikes of fur down the spine
        top = (22 if z < -2 else 18.5) + (1.8 if i < 3 else 1.2)
        base = 21.5 if z < -2 else 18
        m.cube("body", (-0.8, base, z), (0.8, top + 1.5, z + 1.6), "spike", rot=(-35, 0, 0), pivot=(0, base, z + 0.8))
    m.sym("body", (-5.4, 16, -10), (-4.6, 21, -6), "spike", rot=(0, 0, 20), pivot=(-5, 16, -8))   # shoulder tufts

    m.bone("head", "body", (0, 16, -10))
    m.cube("head", (-3.5, 13, -17), (3.5, 20, -10), "fur")
    m.cube("head", (-4.2, 12.5, -14.5), (4.2, 18.5, -11), "ruff")         # cheek fur
    m.cube("head", (-2, 13.5, -23), (2, 17, -17), "muzzle")
    m.cube("head", (-1, 16, -23.3), (1, 17, -22.5), "nose")
    m.cube("head", (-3.8, 19, -17), (3.8, 20.5, -12), "ruff")               # heavy brow
    m.cube("head", (-1.5, 13.6, -22.2), (1.5, 13.8, -17), "maw")
    m.sym("head", (-3.2, 19.5, -13.5), (-1.2, 23, -11.5), "fur", rot=(0, 0, -12), pivot=(-2.2, 20, -12.5))   # ears
    m.sym("head", (-3.65, 17, -16.4), (-3.4, 18.2, -14.4), "eye")
    m.sym("head", (-1.9, 10.8, -22.7), (-1, 13.8, -21.8), "fang")        # upper fangs, past the jaw
    m.bone("jaw", "head", (0, 13.5, -16))
    m.cube("jaw", (-1.9, 11.5, -22.5), (1.9, 13.5, -16), "muzzle")
    m.cube("jaw", (-1.5, 13.4, -22), (1.5, 13.6, -16.5), "mouth")
    m.sym("jaw", (-1.7, 13.5, -22.3), (-1.0, 14.6, -21.6), "fang")       # lower fangs

    m.bone("tail", "body", (0, 16, 9))
    m.cube("tail", (-1.6, 7, 9), (1.6, 16, 12.5), "ruff", rot=(32, 0, 0), pivot=(0, 16, 9))

    for name, x, z, front in (("leg_fl", -2.6, -6, True), ("leg_bl", -2.6, 6, False)):
        for sx, bn in ((1, name), (-1, name[:-1] + "r")):
            xx = x * sx
            m.bone(bn, "body", (xx, 12, z))
            if front:
                m.cube(bn, (xx - 1.6, 5, z - 1.6), (xx + 1.6, 12.5, z + 1.6), "leg")
            else:
                m.cube(bn, (xx - 1.8, 6, z - 2), (xx + 1.8, 13, z + 2), "fur")
            m.cube(bn, (xx - 1.3, 1.2, z - 1.3), (xx + 1.3, 6, z + 1.3), "leg")
            m.cube(bn, (xx - 1.6, 0, z - 2.4), (xx + 1.6, 1.4, z + 1.4), "leg")
            for cx in (-1.0, 0.0, 1.0):
                m.cube(bn, (xx + cx - 0.25, 0, z - 2.9), (xx + cx + 0.25, 0.7, z - 2.4), "claw")
            m.cube(bn, (xx - 1.8, 3, z - 1.8), (xx + 1.8, 4.6, z + 1.8), "iron")       # broken shackle
            m.cube(bn, (xx - 1.85, 3.6, z - 1.85), (xx + 1.85, 4.0, z + 1.85), "gleipnir")
            sx2 = xx + (-2.1 if xx < 0 else 2.1)
            m.cube(bn, (sx2 - 0.3, 1.6, z - 0.5), (sx2 + 0.3, 3.4, z + 0.5), "iron")    # a dangling broken link
            m.cube(bn, (sx2 - 0.5, 0.4, z - 0.3), (sx2 + 0.5, 1.8, z + 0.3), "iron")

    # Gleipnir: the iron collar laced with the glowing silk ribbon, broken chain hanging from it
    m.bone("chain", "body", (0, 13, -11))
    m.cube("chain", (-4.4, 13, -12), (4.4, 15.2, -9.5), "iron")
    m.cube("chain", (-4.5, 13.8, -12.1), (4.5, 14.4, -9.4), "gleipnir")
    for i, (w, d) in enumerate(((0.5, 1.0), (1.0, 0.5), (0.5, 1.0), (1.0, 0.5))):
        y = 12.8 - i * 1.8
        m.cube("chain", (-w, y - 2.0, -12.4 - d / 2), (w, y, -12.4 + d / 2), "iron")
    return m


# ------------------------------------------------------------------ Jormungandr: the Midgard Serpent
def jormungandr():
    m = Model("jormungandr", tex_w=512, seed=47)
    m.material("scale", "#1e5a4c", "scales", marks=("belly", "lateral"))
    m.material("head", "#1a5043", "scales", marks=("belly",))
    m.material("spine", "#0f2e28", "dark")
    m.material("fin", "#b5482a", "membrane")
    m.material("horn", "#d9cfae", "bone")
    m.material("fang", "#efe8d2", "bone")
    m.material("mouth", "#4a1418", "plain")
    m.material("eye", "#a8ff3a", "glow")
    m.material("venom", "#7dff4a", "glow")
    m.look = dict(belly="#c3c27e", belly_axis="local", belly_y=lambda P: 0 * P[..., 1] + 4.0,
                  lateral="#7dff4a", lateral_y=7.0)

    # a viper's head: wide at the back, narrowing to the snout, horns sweeping back
    m.bone("head", None, (0, 7, 0))
    m.cube("head", (-5, 3.5, -10), (5, 10, 0), "head")
    m.cube("head", (-4, 4, -15), (4, 9, -10), "head")
    m.cube("head", (-2.8, 4.5, -19), (2.8, 8.2, -15), "head")
    m.sym("head", (-5.4, 9.5, -12), (-2.4, 11, -4), "spine")                 # brow ridges
    m.sym("head", (-4.8, 9.5, -4), (-3, 11.5, 8), "horn", rot=(22, 14, 0), pivot=(-3.9, 10.5, -4))
    m.sym("head", (-4.3, 11.0, 7.6), (-3.4, 12.4, 12.5), "horn", rot=(38, 14, 0), pivot=(-3.9, 10.5, -4))
    m.sym("head", (-5.1, 7.6, -11.4), (-4.4, 9.2, -8.6), "eye")
    m.sym("head", (-2.4, 2.2, -18.6), (-1.6, 4.5, -17.8), "fang")
    m.sym("head", (-2.0, 1.2, -18.5), (-1.7, 2.2, -18.0), "venom")
    m.cube("head", (-0.5, 10, -8), (0.5, 13, 0), "fin")                      # crest
    m.bone("jaw", "head", (0, 4.5, -2))
    m.cube("jaw", (-4.6, 2, -18), (4.6, 4.2, -1.5), "head")
    m.cube("jaw", (-3.6, 4.1, -17.5), (3.6, 4.3, -3), "mouth")
    m.sym("jaw", (-2.4, 4.2, -17.4), (-1.7, 5.6, -16.7), "fang")
    m.sym("jaw", (-3.2, 4.2, -13), (-2.6, 5.2, -12.4), "fang")

    # 26 segments, thick behind the head and tapering to a whip of a tail
    z, parent, n = 0.0, "head", 26
    for i in range(1, n + 1):
        t = (i - 1) / (n - 1)
        w = 4.4 * (1 - 0.82 * t ** 1.3)
        h = 4.2 * (1 - 0.82 * t ** 1.3)
        ln = 7.0 - 2.6 * t
        bn = f"seg{i}"
        m.bone(bn, parent, (0, 7, z))
        m.cube(bn, (-w, 7 - h, z - 0.3), (w, 7 + h, z + ln), "scale")
        if i % 2 == 1 and i < n - 2:                                         # back spines
            sh = 2.6 * (1 - t) + 0.6
            m.cube(bn, (-0.5, 7 + h - 0.2, z + 1.5), (0.5, 7 + h + sh, z + 3), "spine", rot=(-25, 0, 0), pivot=(0, 7 + h, z + 2.2))
        if i == n:
            m.cube(bn, (-0.4, 7 - 2.5, z + ln - 1), (0.4, 7 + 3, z + ln + 4), "fin")   # tail fin
        parent, z = bn, z + ln
    return m


# ------------------------------------------------------------------ Garmr: the blood-stained hound at the gate of Hel
def garmr():
    m = Model("garmr", tex_w=256, seed=61)
    m.material("hide", "#2a2224", "fur", marks=("back", "belly"))
    m.material("blood", "#5a1612", "fur")
    m.material("leg", "#241c1e", "fur")
    m.material("bone", "#d8ceb4", "bone")
    m.material("iron", "#3e3a40", "metal")
    m.material("eye", "#ff2a1a", "glow")
    m.material("soul", "#5ad8ff", "glow")
    m.material("mouth", "#3a0c0c", "plain")
    m.material("nose", "#100c0c", "dark")
    m.look = dict(back="#1a1416", belly="#4a1a16", belly_cut=0.34)

    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-3.6, 10, -9), (3.6, 17, 8), "hide")
    m.cube("body", (-4, 9.5, -11), (4, 18.5, -5), "blood")                    # blood-soaked chest
    for y in (11.2, 12.8, 14.4):                                             # ribs through the torn hide
        m.sym("body", (-3.85, y, -3), (-3.5, y + 0.8, 3.5), "bone")
    for z in (-8.5, -5.5, -2.5, 0.5, 3.5, 6.5):                              # bone spikes down the spine
        h = 3.2 if z < 0 else 2.2
        m.cube("body", (-0.6, 17, z), (0.6, 17 + h, z + 1.2), "bone", rot=(-25, 0, 0), pivot=(0, 17, z + 0.6))
    for z in (-10, -7, -4):                                                  # soul-fire along the hackles
        m.cube("body", (-1.2, 18.5, z), (1.2, 21, z + 2), "soul")

    m.bone("head", "body", (0, 16, -10))
    m.cube("head", (-3.2, 12.5, -17), (3.2, 19, -10), "hide")
    m.cube("head", (-1.9, 12.8, -23), (1.9, 16.2, -17), "hide")
    m.cube("head", (-0.9, 15.3, -23.3), (0.9, 16.3, -22.6), "nose")
    m.cube("head", (-3.5, 18, -17.2), (3.5, 19.6, -12), "bone")              # skull plate
    m.sym("head", (-3.4, 19, -12.5), (-2, 22.5, -11), "bone", rot=(-20, 0, -10), pivot=(-2.7, 19, -11.7))   # horns
    m.sym("head", (-3.25, 16.8, -16.4), (-3.1, 17.8, -15.2), "eye")           # four eyes
    m.sym("head", (-3.25, 15.2, -15.6), (-3.1, 16.0, -14.6), "eye")
    m.sym("head", (-1.7, 11.0, -22.6), (-1.0, 12.9, -21.8), "bone")           # fangs
    m.sym("head", (-1.8, 11.5, -19.5), (-1.2, 12.9, -18.9), "bone")
    m.bone("jaw", "head", (0, 13, -16))
    m.cube("jaw", (-1.8, 11, -22.5), (1.8, 13, -16), "hide")
    m.cube("jaw", (-1.4, 12.9, -22), (1.4, 13.1, -16.5), "mouth")
    m.cube("jaw", (-1.6, 10.4, -21.5), (1.6, 11.1, -17), "blood")             # blood on the chin

    m.bone("tail", "body", (0, 16, 8))
    m.cube("tail", (-1, 7, 8), (1, 16, 10), "bone", rot=(28, 0, 0), pivot=(0, 16, 8))
    m.cube("tail", (-0.9, 5.2, 8.4), (0.9, 7.2, 10.2), "soul", rot=(28, 0, 0), pivot=(0, 16, 8))

    for name, x, z in (("leg_fl", -2.4, -6.5), ("leg_bl", -2.4, 5.5)):
        for sx, bn in ((1, name), (-1, name[:-1] + "r")):
            xx = x * sx
            m.bone(bn, "body", (xx, 12, z))
            m.cube(bn, (xx - 1.5, 5, z - 1.6), (xx + 1.5, 12.5, z + 1.6), "leg")
            m.cube(bn, (xx - 1.1, 1.2, z - 1.1), (xx + 1.1, 5.5, z + 1.1), "leg")
            m.cube(bn, (xx - 1.5, 0, z - 2.4), (xx + 1.5, 1.4, z + 1.3), "leg")
            for cx in (-1.0, 0.0, 1.0):
                m.cube(bn, (xx + cx - 0.25, 0, z - 3.0), (xx + cx + 0.25, 0.8, z - 2.4), "bone")

    # the chain of Gnipahellir: heavy collar, chain dragging on the ground
    m.bone("chain", "body", (0, 13, -11))
    m.cube("chain", (-4.2, 13, -12), (4.2, 15.6, -9), "iron")
    for i in range(5):
        y = 12.8 - i * 2.2
        w, d = ((0.5, 1.0), (1.0, 0.5))[i % 2]
        m.cube("chain", (-w, y - 2.4, -12.6 - d / 2), (w, y, -12.6 + d / 2), "iron")
    return m


# ------------------------------------------------------------------ Fafnir: the dwarf turned dragon, on his cursed hoard
def fafnir():
    m = Model("fafnir", tex_w=512, seed=71)
    m.material("scale", "#6e2a1c", "scales", marks=("back", "coins"))
    m.material("belly", "#d4a838", "plates")
    m.material("neck", "#6e2a1c", "scales", marks=("coins",))
    m.material("horn", "#e8dcb8", "bone")
    m.material("spike", "#2a1410", "dark")
    m.material("wingbone", "#4a1a12", "scales")
    m.material("membrane", "#9a3a24", "membrane")
    m.material("claw", "#1c100c", "dark")
    m.material("fang", "#f0e8d0", "bone")
    m.material("eye", "#ffb020", "glow")
    m.material("ember", "#ff6a1a", "glow")
    m.material("gold", "#e8b83a", "gold")
    m.look = dict(back="#4a1a12", coins="#e8b83a")

    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-5, 10, -10), (5, 19, 10), "scale")
    m.cube("body", (-4.2, 9.4, -9), (4.2, 10.4, 9), "belly")
    m.cube("body", (-5.1, 10, -10.1), (5.1, 14, -6), "belly")                 # gold chest plates
    for z in (-8, -4, 0, 4, 8):
        m.cube("body", (-0.6, 18.5, z), (0.6, 21.5, z + 1.6), "spike", rot=(-25, 0, 0), pivot=(0, 19, z + 0.8))

    m.bone("neck1", "body", (0, 17, -9), rot=(-28, 0, 0))
    m.cube("neck1", (-3, 14, -17), (3, 20, -8), "neck")
    m.cube("neck1", (-0.5, 19.5, -15), (0.5, 22, -13.5), "spike")
    m.bone("neck2", "neck1", (0, 17, -16))
    m.cube("neck2", (-2.6, 14.5, -23.5), (2.6, 19.5, -15.5), "neck")
    m.cube("neck2", (-0.5, 19, -22), (0.5, 21.5, -20.5), "spike")
    m.bone("head", "neck2", (0, 17, -22.5), rot=(26, 0, 0))
    m.cube("head", (-3.5, 14, -29), (3.5, 20, -21.5), "scale")
    m.cube("head", (-2.5, 14.5, -35), (2.5, 18.5, -29), "scale")
    m.cube("head", (-3.8, 19, -28), (3.8, 20.6, -23), "spike")               # brow
    m.sym("head", (-3.4, 19.2, -24), (-2.0, 21, -13), "horn", rot=(18, -12, 0), pivot=(-2.7, 20, -24))
    m.sym("head", (-3.2, 20.6, -14), (-2.4, 23.6, -12.6), "horn", rot=(18, -12, 0), pivot=(-2.7, 20, -24))
    m.sym("head", (-3.55, 17.5, -27.6), (-3.4, 18.6, -25.8), "eye")
    m.sym("head", (-1.6, 17.6, -35.1), (-0.8, 18.3, -34.9), "ember")         # smouldering nostrils
    m.sym("head", (-2.2, 13, -34.6), (-1.5, 14.6, -33.8), "fang")
    m.sym("head", (-2.4, 13.4, -31), (-1.8, 14.6, -30.4), "fang")
    m.bone("jaw", "head", (0, 14.5, -23))
    m.cube("jaw", (-2.3, 12.4, -34.5), (2.3, 14.5, -23), "scale")
    m.cube("jaw", (-1.8, 14.4, -34), (1.8, 14.6, -24), "ember")              # fire in the throat

    for side, s in (("l", -1), ("r", 1)):
        b1, b2 = f"wing_{side}", f"wing_{side}2"
        x0 = s * 4.5
        m.bone(b1, "body", (x0, 18, -6))
        lo, hi = sorted((x0, s * 17))
        m.cube(b1, (lo, 17.2, -7), (hi, 19, -5), "wingbone")
        m.cube(b1, (lo, 17.8, -5), (hi, 18.4, 9), "membrane")
        m.bone(b2, b1, (s * 17, 18, -6))
        lo, hi = sorted((s * 17, s * 29))
        m.cube(b2, (lo, 17.4, -6.6), (hi, 18.8, -5.2), "wingbone")
        m.cube(b2, (lo, 17.9, -5.2), (hi, 18.3, 7), "membrane")
        for k, zz in enumerate((-1, 3, 7)):                                     # finger spars
            fx = s * (20 + k * 3)
            m.cube(b2, (min(fx, fx + s * 1), 17.8, -5.2), (max(fx, fx + s * 1), 18.5, zz), "wingbone")
        lo, hi = sorted((s * 17, s * 18.4))
        m.cube(b2, (lo, 18.8, -7.4), (hi, 21, -6), "claw")                    # wing thumb claw

    for name, x, z, top in (("leg_fl", -4, -6, 12), ("leg_bl", -4.5, 6, 13)):
        for sx, bn in ((1, name), (-1, name[:-1] + "r")):
            xx = x * sx
            m.bone(bn, "body", (xx, top, z))
            m.cube(bn, (xx - 2, 5, z - 2.2), (xx + 2, top + 1, z + 2.2), "scale")
            m.cube(bn, (xx - 1.6, 1.2, z - 1.6), (xx + 1.6, 5.5, z + 1.6), "scale")
            m.cube(bn, (xx - 2, 0, z - 2.8), (xx + 2, 1.4, z + 1.8), "scale")
            for cx in (-1.3, 0.0, 1.3):
                m.cube(bn, (xx + cx - 0.3, 0, z - 3.8), (xx + cx + 0.3, 1.0, z - 2.8), "claw")

    m.bone("tail", "body", (0, 15, 10))
    m.cube("tail", (-3, 11.5, 9.5), (3, 17, 19), "scale")
    m.cube("tail", (-0.5, 16.6, 13), (0.5, 19, 14.6), "spike")
    m.bone("tail2", "tail", (0, 14, 18.5))
    m.cube("tail2", (-2.2, 12, 18.5), (2.2, 16, 28), "scale")
    m.cube("tail2", (-0.5, 15.6, 22), (0.5, 17.6, 23.4), "spike")
    m.bone("tail3", "tail2", (0, 14, 27.5))
    m.cube("tail3", (-1.4, 12.6, 27.5), (1.4, 15.2, 37), "scale")
    m.cube("tail3", (-3, 13.2, 36), (3, 14.6, 41), "spike")                  # spade tip
    m.cube("tail3", (-0.8, 15, 31), (0.8, 15.6, 33), "gold")                  # a ring stolen from the hoard
    return m


MODELS = {"sleipnir": sleipnir, "garmr": garmr, "fafnir": fafnir, "jormungandr": jormungandr, "fenrir": fenrir}

if __name__ == "__main__":
    for k in (sys.argv[1:] or MODELS):
        MODELS[k]().save()
