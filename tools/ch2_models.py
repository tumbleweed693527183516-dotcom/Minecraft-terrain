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
    m.look = dict(belly="#c9ced4", belly_cut=0.42, socks="#e4e8ec", socks_h=6)

    m.bone("body", None, (0, 17, 0))
    m.cube("body", (-5, 12, -11), (5, 22, 11), "coat")
    m.cube("body", (-4.5, 11, -10), (4.5, 12, 9), "coat")                 # belly line
    # Odin's barding: blue saddle cloth with gold trim, gold breastplate with glowing runes
    m.cube("body", (-5.5, 16, -5), (5.5, 22.5, 5), "cloth")
    m.cube("body", (-5.6, 15.5, -5.1), (5.6, 16.3, 5.1), "gold")
    m.cube("body", (-2, 22.5, -4), (2, 23.5, 3), "gold")                  # saddle seat
    m.cube("body", (-4.5, 13, -12), (4.5, 20, -11), "rune_gold")

    m.bone("neck", "body", (0, 20, -9), rot=(28, 0, 0))
    m.cube("neck", (-2.5, 18, -12.5), (2.5, 29, -6.5), "coat")
    m.cube("neck", (-0.8, 19, -6.5), (0.8, 30.5, -4.2), "mane")             # mane along the neck
    m.cube("neck", (-2.6, 21, -12.1), (2.6, 22, -6.4), "gold")            # collar

    m.bone("head", "neck", (0, 28, -9), rot=(-20, 0, 0))
    m.cube("head", (-3, 26, -15), (3, 32, -7.5), "coat")
    m.cube("head", (-2.2, 25.5, -21), (2.2, 30, -15), "muzzle")
    m.cube("head", (-1.2, 32, -14), (1.2, 33.5, -8), "mane")              # forelock
    m.sym("head", (-2.8, 32, -9.5), (-1.4, 35, -8.3), "coat")             # ears
    m.sym("head", (-3.05, 29, -13.2), (-2.6, 30.2, -11.8), "eye")
    m.sym("head", (-1.8, 27.5, -21.1), (-0.8, 28.5, -20.9), "nostril")
    m.cube("head", (-3.1, 28.5, -15.2), (3.1, 29.3, -14.6), "gold")       # bridle band
    m.sym("head", (-2.4, 26.5, -19.5), (-2.2, 28.5, -15), "gold")         # cheek straps
    m.bone("jaw", "head", (0, 26, -15))
    m.cube("jaw", (-1.9, 24.5, -20.5), (1.9, 26, -15), "muzzle")

    m.bone("tail", "body", (0, 21, 11))
    m.cube("tail", (-1.5, 9, 11), (1.5, 21.5, 14), "mane", rot=(22, 0, 0), pivot=(0, 21, 11))
    m.cube("tail", (-1, 5, 13), (1, 10, 15.5), "mane", rot=(22, 0, 0), pivot=(0, 21, 11))

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
    m.look = dict(belly="#4a4a52", belly_cut=0.36, back="#16161a", scar_color="#7a6266",
                  scars=[((-4, 17, -4), (-4, 13, 2)), ((-4, 16.5, -2.5), (-4, 12.5, 3.5)), ((4, 16, 1), (4, 12, 6)),
                         ((-3.5, 19, -12), (-3.5, 16, -10))])

    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-4, 9.5, -8), (4, 17.5, 9), "fur")
    m.cube("body", (-5, 11, -11), (5, 20.5, -2), "ruff")                 # shaggy shoulders
    m.cube("body", (-1.5, 20.5, -9), (1.5, 22, -3), "ruff")              # hackles
    m.cube("body", (-1, 17.5, -1), (1, 18.5, 7), "ruff")                 # ridge down the back

    m.bone("head", "body", (0, 16, -10))
    m.cube("head", (-3.5, 13, -17), (3.5, 20, -10), "fur")
    m.cube("head", (-4.2, 12.5, -14.5), (4.2, 18.5, -11), "ruff")         # cheek fur
    m.cube("head", (-2, 13.5, -23), (2, 17, -17), "muzzle")
    m.cube("head", (-1, 16, -23.3), (1, 17, -22.5), "nose")
    m.sym("head", (-3.2, 19.5, -13.5), (-1.2, 23, -11.5), "fur", rot=(0, 0, -12), pivot=(-2.2, 20, -12.5))   # ears
    m.sym("head", (-3.65, 17, -16.4), (-3.4, 18.2, -14.4), "eye")
    m.sym("head", (-1.8, 12.4, -22.6), (-1, 13.8, -21.8), "fang")        # upper fangs
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
    m.material("scale", "#1e5a4c", "scales", marks=("belly",))
    m.material("head", "#1a5043", "scales", marks=("belly",))
    m.material("spine", "#0f2e28", "dark")
    m.material("fin", "#b5482a", "membrane")
    m.material("horn", "#d9cfae", "bone")
    m.material("fang", "#efe8d2", "bone")
    m.material("mouth", "#4a1418", "plain")
    m.material("eye", "#a8ff3a", "glow")
    m.material("venom", "#7dff4a", "glow")
    m.look = dict(belly="#c3c27e", belly_axis="local", belly_y=lambda P: 0 * P[..., 1] + 4.4)

    m.bone("head", None, (0, 7, 0))
    m.cube("head", (-5, 4, -12), (5, 11, 0), "head")
    m.cube("head", (-3.6, 4.5, -20), (3.6, 9, -12), "head")
    m.sym("head", (-5.6, 10, -11), (-2.4, 12, -3), "spine")                  # brow ridges
    m.sym("head", (-5, 10.5, -5), (-2.6, 13, 8), "horn", rot=(26, 12, 0), pivot=(-3.8, 11.5, -5))
    m.sym("head", (-4.4, 12.4, 7.5), (-3.2, 14, 13), "horn", rot=(40, 12, 0), pivot=(-3.8, 11.5, -5))
    m.sym("head", (-5.15, 7.8, -9.8), (-4.9, 9.6, -6.8), "eye")
    m.sym("head", (-3.4, 2.6, -19.6), (-2.6, 4.5, -18.8), "fang")             # upper fangs
    m.sym("head", (-3.6, 3.3, -16), (-2.9, 4.5, -15.2), "fang")
    m.sym("head", (-3.3, 1.5, -19.5), (-2.7, 2.6, -18.9), "venom")            # venom drop
    m.sym("head", (-8.5, 5, -2), (-5, 12, -0.5), "fin", rot=(0, -25, 0), pivot=(-5, 8, -1))   # neck frills
    m.cube("head", (-0.5, 11, -6), (0.5, 15, 0), "fin")                       # crest
    m.bone("jaw", "head", (0, 5, -4))
    m.cube("jaw", (-4.5, 1.5, -19), (4.5, 4.5, -3), "head")
    m.cube("jaw", (-3.8, 4.4, -18.5), (3.8, 4.6, -4), "mouth")
    m.sym("jaw", (-3.4, 4.5, -18.6), (-2.7, 6.2, -17.9), "fang")
    m.sym("jaw", (-3.6, 4.5, -14), (-2.9, 5.5, -13.3), "fang")

    # body: 12 segments trailing behind the head, each a child of the one before
    z = 0.0
    parent = "head"
    for i in range(1, 11):
        t = (i - 1) / 9
        w = 5.2 - 3.2 * t
        h = 5.0 - 3.0 * t
        ln = 10.5 - 2.5 * t
        bn = f"seg{i}"
        m.bone(bn, parent, (0, 7, z))
        m.cube(bn, (-w, 7 - h, z - 0.3), (w, 7 + h, z + ln), "scale")
        fh = 3.2 - 2.0 * t
        if i < 10:
            m.cube(bn, (-0.5, 7 + h, z + 1.5), (0.5, 7 + h + fh, z + ln - 2), "fin")     # dorsal sail
            m.cube(bn, (-0.6, 7 + h, z + ln * 0.5 - 0.6), (0.6, 7 + h + fh + 1.2, z + ln * 0.5 + 0.6), "spine")
        else:
            m.cube(bn, (-0.5, 7 - 5, z + ln - 1), (0.5, 7 + 6, z + ln + 6), "fin")         # tail fluke
            m.cube(bn, (-0.6, 7 - 0.6, z + ln - 1), (0.6, 7 + 0.6, z + ln + 6.5), "spine")
        if i in (2, 3):                                                                  # front flippers
            m.sym(bn, (-w - 4, 7 - h + 0.5, z + 2), (-w, 7 - h + 1.5, z + 6), "fin", rot=(0, 0, 18), pivot=(-w, 7 - h + 1, z + 4))
        parent = bn
        z += ln
    return m


MODELS = {"sleipnir": sleipnir, "fenrir": fenrir, "jormungandr": jormungandr}

if __name__ == "__main__":
    for k in (sys.argv[1:] or MODELS):
        MODELS[k]().save()
