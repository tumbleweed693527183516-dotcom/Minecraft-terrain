"""
The ten new Chapter 1 animal bosses (Skadi's trials 11-20), built with tools/mobkit.py.

    python3 tools/ch1_models.py              # all
    python3 tools/ch1_models.py cave_lion    # one

Rigs (bone names) match the animation rigs in tools/ch1_anims.py:
  quad:    body, head, jaw, tail, leg_fl, leg_fr, leg_bl, leg_br (+ ear_l/ear_r)
  ape:     body, chest, head, jaw, arm_l, arm_r, leg_l, leg_r, tail
  bird:    body, neck, head, jaw, wing_l, wing_r, leg_l, leg_r, tail
  eagle:   body, head, jaw, wing_l, wing_l2, wing_r, wing_r2, tail, leg_l, leg_r
  lizard:  quad + tail2
  serpent: head, jaw, seg1..segN
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mobkit import Model  # noqa: E402


def legs4(m, front, back, mat, foot, claw=None, sock=None):
    """Four legs. front/back: (x, z, top_y, width, depth); each leg is one bone pivoting at its top."""
    for (x, z, top, w, d), names in ((front, ("leg_fl", "leg_fr")), (back, ("leg_bl", "leg_br"))):
        for sx, bn in ((1, names[0]), (-1, names[1])):
            xx = -abs(x) if sx == 1 else abs(x)
            m.bone(bn, "body", (xx, top, z))
            m.cube(bn, (xx - w / 2, 1.2, z - d / 2), (xx + w / 2, top + 0.5, z + d / 2), mat)
            m.cube(bn, (xx - w / 2 - 0.2, 0, z - d / 2 - 0.6), (xx + w / 2 + 0.2, 1.4, z + d / 2 + 0.2), foot)
            if claw:
                for cx in (-w / 3, 0, w / 3):
                    m.cube(bn, (xx + cx - 0.25, 0, z - d / 2 - 1.2), (xx + cx + 0.25, 0.7, z - d / 2 - 0.6), claw)
            if sock:
                m.cube(bn, (xx - w / 2 - 0.15, 1.4, z - d / 2 - 0.15), (xx + w / 2 + 0.15, 3.5, z + d / 2 + 0.15), sock)


# ------------------------------------------------------------------ Dire Wolf Alpha
def dire_wolf():
    m = Model("dire_wolf", 256, seed=101)
    m.material("fur", "#6e6458", "fur", marks=("belly", "back", "scars"))
    m.material("ruff", "#5a5248", "fur")
    m.material("leg", "#625a4e", "fur")
    m.material("muzzle", "#9a8e7c", "fur")
    m.material("nose", "#181614", "dark")
    m.material("eye", "#e8c040", "plain")
    m.material("fang", "#ece4cc", "bone")
    m.material("paw", "#3a342c", "dark")
    m.look = dict(belly="#b8ad9c", belly_cut=0.4, back="#4a4339", scar_color="#8a6a62",
                  scars=[((-3.05, 16.5, -14), (-3.05, 13.5, -12)), ((3.5, 14, -2), (3.5, 11, 3))])
    m.bone("body", None, (0, 13, 0))
    m.cube("body", (-3.5, 9, -8), (3.5, 16, 8), "fur")
    m.cube("body", (-4.5, 10, -10), (4.5, 17.5, -3), "ruff")
    m.cube("body", (-1.2, 17.5, -9), (1.2, 18.5, -4), "ruff")
    m.bone("head", "body", (0, 14, -9))
    m.cube("head", (-3, 11.5, -15), (3, 17, -9), "fur")
    m.cube("head", (-1.8, 11.5, -19.5), (1.8, 14.5, -15), "muzzle")
    m.cube("head", (-0.8, 13.6, -19.8), (0.8, 14.6, -19.3), "nose")
    m.bone("ear_l", "head", (-2, 17, -11.5))
    m.cube("ear_l", (-2.8, 17, -12.5), (-1.2, 20, -11), "ruff")
    m.bone("ear_r", "head", (2, 17, -11.5))
    m.cube("ear_r", (1.2, 17, -12.5), (2.8, 20, -11), "ruff")
    m.sym("head", (-3.05, 15, -14.2), (-2.9, 16, -13), "eye")
    m.sym("head", (-1.5, 10.6, -19.2), (-0.9, 11.6, -18.6), "fang")
    m.bone("jaw", "head", (0, 12, -14))
    m.cube("jaw", (-1.6, 10.2, -19), (1.6, 12, -14), "muzzle")
    m.bone("tail", "body", (0, 14.5, 8))
    m.cube("tail", (-1.4, 6, 8), (1.4, 14.5, 11), "ruff", rot=(30, 0, 0), pivot=(0, 14.5, 8))
    legs4(m, (2.2, -6, 10, 2.6, 2.6), (2.2, 6, 10, 2.8, 3.0), "leg", "paw")
    return m


# ------------------------------------------------------------------ Cave Lion
def cave_lion():
    m = Model("cave_lion", 256, seed=103)
    m.material("coat", "#c49a5a", "fur", marks=("belly", "back", "stripes"))
    m.material("ruff", "#a87c42", "fur", marks=("stripes",))
    m.material("leg", "#b88e50", "fur")
    m.material("muzzle", "#e3cfa6", "fur")
    m.material("nose", "#5a3428", "dark")
    m.material("eye", "#d8b030", "plain")
    m.material("fang", "#ece4cc", "bone")
    m.material("paw", "#8a6a3c", "fur")
    m.material("tuft", "#3a2414", "hair")
    m.look = dict(belly="#e3cfa6", belly_cut=0.38, back="#a87c42", stripes="#8a6234", stripe_gap=3, stripe_min=0.5)
    m.bone("body", None, (0, 13, 0))
    m.cube("body", (-4, 9, -10), (4, 17, 10), "coat")
    m.cube("body", (-4.4, 10, -11), (4.4, 18, -6), "ruff")
    m.bone("head", "body", (0, 15, -10))
    m.cube("head", (-3.5, 12, -16), (3.5, 18.5, -9.5), "coat")
    m.cube("head", (-2.2, 12, -19.5), (2.2, 15.5, -16), "muzzle")
    m.cube("head", (-0.9, 14.6, -19.8), (0.9, 15.6, -19.3), "nose")
    m.cube("head", (-3.6, 17, -15), (3.6, 18.7, -11), "ruff")            # brow
    m.bone("ear_l", "head", (-2.4, 18.5, -11.5))
    m.cube("ear_l", (-3.1, 18.5, -12), (-1.5, 20, -11), "ruff")
    m.bone("ear_r", "head", (2.4, 18.5, -11.5))
    m.cube("ear_r", (1.5, 18.5, -12), (3.1, 20, -11), "ruff")
    m.sym("head", (-3.55, 16, -15.4), (-3.4, 17, -14), "eye")
    m.sym("head", (-1.8, 11, -19.3), (-1.1, 12.2, -18.6), "fang")
    m.bone("jaw", "head", (0, 12, -14))
    m.cube("jaw", (-2, 10.5, -19), (2, 12, -14), "muzzle")
    m.bone("tail", "body", (0, 16, 10))
    m.cube("tail", (-0.8, 5, 10), (0.8, 16, 11.6), "coat", rot=(25, 0, 0), pivot=(0, 16, 10))
    m.cube("tail", (-1.3, 2.5, 9.6), (1.3, 6, 12), "tuft", rot=(25, 0, 0), pivot=(0, 16, 10))
    legs4(m, (2.6, -7, 10, 3.2, 3.2), (2.6, 7, 11, 3.4, 3.8), "leg", "paw")
    return m


# ------------------------------------------------------------------ Steppe Bison
def steppe_bison():
    m = Model("steppe_bison", 256, seed=107)
    m.material("rear", "#6b4a2c", "fur", marks=("belly",))
    m.material("hump", "#3d2816", "hair")
    m.material("leg", "#4a3220", "fur")
    m.material("face", "#2a1e14", "fur")
    m.material("horn", "#3a3632", "bone")
    m.material("tip", "#cfc6b0", "bone")
    m.material("hoof", "#1e1a16", "dark")
    m.material("eye", "#1a1210", "dark")
    m.look = dict(belly="#54391f", belly_cut=0.35)
    m.bone("body", None, (0, 14, 0))
    m.cube("body", (-4.5, 9, -1), (4.5, 18, 11), "rear")
    m.cube("body", (-5.5, 8, -11), (5.5, 24, 1), "hump")
    m.cube("body", (-4, 24, -9), (4, 25.5, -2), "hump")
    m.bone("head", "body", (0, 16, -11))
    m.cube("head", (-3.5, 9, -17), (3.5, 17, -10), "face")
    m.cube("head", (-2.5, 9, -19), (2.5, 14, -17), "face")
    m.cube("head", (-3, 12, -12), (3, 18, -9), "hump")                    # mane over the brow
    m.cube("head", (-2.5, 5, -16), (2.5, 9, -11), "hump")                 # beard
    m.sym("head", (-6.5, 15, -14), (-3.5, 16.6, -12.5), "horn")
    m.sym("head", (-7.1, 16.4, -14.1), (-5.8, 18.6, -12.8), "horn")
    m.sym("head", (-7.0, 18.6, -14.0), (-6.0, 19.6, -13.0), "tip")
    m.sym("head", (-3.55, 13.5, -15.5), (-3.4, 14.4, -14.3), "eye")
    m.bone("jaw", "head", (0, 10, -15))
    m.cube("jaw", (-2, 8.4, -18.8), (2, 9.4, -15), "face")
    m.bone("tail", "body", (0, 17, 11))
    m.cube("tail", (-0.6, 9, 11), (0.6, 17, 12), "rear", rot=(10, 0, 0), pivot=(0, 17, 11))
    m.cube("tail", (-1, 6.5, 10.8), (1, 9.5, 12.4), "hump", rot=(10, 0, 0), pivot=(0, 17, 11))
    legs4(m, (3, -7, 10, 3.2, 3.2), (3, 7, 10, 2.8, 3.0), "leg", "hoof")
    for z, bns in ((-7, ("leg_fl", "leg_fr")),):
        for sx, bn in ((-1, bns[0]), (1, bns[1])):
            m.cube(bn, (sx * 3 - 2.1, 5.5, z - 2.1), (sx * 3 + 2.1, 10.5, z + 2.1), "hump")   # shaggy forelegs
    return m


# ------------------------------------------------------------------ Giant Ground Sloth (Megatherium), ape rig
def ground_sloth():
    m = Model("ground_sloth", 256, seed=109)
    m.material("fur", "#7a5a3a", "hair", marks=("back",))
    m.material("chest", "#6a4c30", "hair")
    m.material("dark", "#54391f", "hair")
    m.material("face", "#3a2c20", "hide")
    m.material("claw", "#e6dcc0", "bone")
    m.material("eye", "#120c08", "dark")
    m.material("nose", "#1a120c", "dark")
    m.look = dict(back="#8a6a46")
    m.bone("body", None, (0, 14, 2))
    m.cube("body", (-5, 9, -2), (5, 20, 9), "fur")
    m.bone("chest", "body", (0, 18, -1))
    m.cube("chest", (-5.5, 15, -10), (5.5, 27, 1), "chest")
    m.cube("chest", (-4.5, 26, -9), (4.5, 28, -1), "fur")
    m.bone("head", "chest", (0, 24, -9))
    m.cube("head", (-3, 21, -15), (3, 26.5, -8.5), "face")
    m.cube("head", (-2, 21, -18.5), (2, 24.5, -15), "face")
    m.cube("head", (-1, 23.5, -18.8), (1, 24.5, -18.3), "nose")
    m.cube("head", (-3.3, 24.5, -14), (3.3, 27.5, -8), "dark")           # shaggy crown
    m.sym("head", (-3.05, 24, -14), (-2.9, 25, -13), "eye")
    m.bone("jaw", "head", (0, 21.5, -12))
    m.cube("jaw", (-1.8, 19.8, -17.5), (1.8, 21.5, -12), "face")
    for bn, x in (("arm_l", -6.5), ("arm_r", 6.5)):
        m.bone(bn, "chest", (x, 25, -5))
        m.cube(bn, (x - 2, 13, -7.5), (x + 2, 26, -2.5), "dark")
        m.cube(bn, (x - 1.7, 3, -7.2), (x + 1.7, 13, -2.8), "fur")
        m.cube(bn, (x - 2.1, 1, -8.5), (x + 2.1, 3.2, -2.5), "face")
        for i in range(3):                                                 # three great hooked claws
            cx = x - 1.4 + i * 1.4
            m.cube(bn, (cx - 0.35, 0, -11.5), (cx + 0.35, 1.4, -8.4), "claw")
    for bn, x in (("leg_l", -3.5), ("leg_r", 3.5)):
        m.bone(bn, "body", (x, 11, 4))
        m.cube(bn, (x - 2.3, 1.5, 1.5), (x + 2.3, 12, 6.8), "dark")
        m.cube(bn, (x - 2.5, 0, 0.5), (x + 2.5, 1.6, 7), "face")
    m.bone("tail", "body", (0, 13, 9))
    m.cube("tail", (-2.5, 5, 9), (2.5, 13, 14.5), "fur", rot=(35, 0, 0), pivot=(0, 13, 9))
    return m


# ------------------------------------------------------------------ Glyptodon
def glyptodon():
    m = Model("glyptodon", 256, seed=113)
    m.material("shell", "#8a6a44", "plates")
    m.material("rim", "#5c4428", "plates")
    m.material("skin", "#6e6252", "hide")
    m.material("cap", "#7a5c3a", "plates")
    m.material("club", "#6a4e30", "plates")
    m.material("spike", "#d8ccaa", "bone")
    m.material("claw", "#2e2620", "dark")
    m.material("eye", "#100c08", "dark")
    m.bone("body", None, (0, 9, 0))
    m.cube("body", (-6, 6, -9), (6, 16, 9), "shell")
    m.cube("body", (-5, 16, -7), (5, 18.5, 7), "shell")
    m.cube("body", (-3.5, 18.5, -4.5), (3.5, 19.5, 4.5), "shell")
    m.cube("body", (-6.6, 5, -9.6), (6.6, 7, 9.6), "rim")
    m.bone("head", "body", (0, 8, -9))
    m.cube("head", (-2.5, 4, -14), (2.5, 9, -9), "skin")
    m.cube("head", (-2.8, 8.5, -13.6), (2.8, 10, -9.2), "cap")
    m.sym("head", (-2.55, 7, -12.6), (-2.4, 7.8, -11.8), "eye")
    m.bone("jaw", "head", (0, 4.5, -10))
    m.cube("jaw", (-1.8, 3, -13.5), (1.8, 4.5, -10), "skin")
    legs4(m, (4, -6, 6.5, 3.4, 3.4), (4, 6, 6.5, 3.6, 3.6), "skin", "skin", claw="claw")
    m.bone("tail", "body", (0, 9, 9))
    m.cube("tail", (-2, 7, 9), (2, 11, 13), "rim")
    m.bone("tail2", "tail", (0, 9, 13))
    m.cube("tail2", (-1.6, 7.4, 12.6), (1.6, 10.6, 16), "rim")
    m.cube("tail2", (-2.8, 6.5, 15.5), (2.8, 11.5, 20.5), "club")            # the spiked club
    m.sym("tail2", (-3.8, 8.5, 17), (-2.8, 9.5, 18.5), "spike")
    m.cube("tail2", (-0.5, 11.5, 17), (0.5, 12.6, 18.5), "spike")
    m.cube("tail2", (-0.5, 8.5, 20.5), (0.5, 9.5, 21.6), "spike")
    return m


# ------------------------------------------------------------------ Terror Bird (Phorusrhacid), bird rig
def terror_bird():
    m = Model("terror_bird", 256, seed=127)
    m.material("feather", "#4a4038", "feather", marks=("belly",))
    m.material("wing", "#3a322a", "feather")
    m.material("crest", "#7a2a1c", "feather")
    m.material("beak", "#d9a43a", "bone")
    m.material("leg", "#b8a070", "scales")
    m.material("claw", "#2a2420", "dark")
    m.material("eye", "#e8c838", "plain")
    m.material("pupil", "#100c08", "dark")
    m.look = dict(belly="#8a7a68", belly_cut=0.5)
    m.bone("body", None, (0, 18, 0))
    m.cube("body", (-4, 14, -6), (4, 22, 7), "feather")
    m.cube("body", (-3, 17, 6.5), (3, 22, 12), "wing", rot=(-20, 0, 0), pivot=(0, 21, 7))
    m.bone("neck", "body", (0, 20, -5), rot=(12, 0, 0))
    m.cube("neck", (-2, 20, -8), (2, 32, -4), "feather")
    m.bone("head", "neck", (0, 31, -6), rot=(-12, 0, 0))
    m.cube("head", (-2.5, 30, -11), (2.5, 35, -4), "feather")
    m.cube("head", (-1.8, 30.5, -19), (1.8, 34.5, -11), "beak")
    m.cube("head", (-1.4, 28.8, -19.6), (1.4, 31, -17.6), "beak")             # hooked tip
    m.cube("head", (-0.6, 35, -9), (0.6, 38, -4), "crest")
    m.sym("head", (-2.55, 32.5, -9.5), (-2.4, 33.6, -8.3), "eye")
    m.sym("head", (-2.6, 32.8, -9.2), (-2.5, 33.4, -8.7), "pupil")
    m.bone("jaw", "head", (0, 30.5, -11))
    m.cube("jaw", (-1.6, 29, -18), (1.6, 30.5, -11), "beak")
    for bn, x in (("wing_l", -4), ("wing_r", 4)):
        m.bone(bn, "body", (x, 21, -3))
        m.cube(bn, (min(x, x * 1.25), 15, -4), (max(x, x * 1.25), 21, 5), "wing")
    for bn, x in (("leg_l", -2.2), ("leg_r", 2.2)):
        m.bone(bn, "body", (x, 15, 1))
        m.cube(bn, (x - 1.6, 9, -0.5), (x + 1.6, 16, 3), "feather")
        m.cube(bn, (x - 0.8, 1, 0.2), (x + 0.8, 9.5, 1.8), "leg")
        m.cube(bn, (x - 1.4, 0, -3), (x + 1.4, 1, 2), "leg")
        m.cube(bn, (x - 0.4, 0, -4.4), (x + 0.4, 1.2, -3), "claw")
        m.cube(bn, (x - 0.35, 1.5, -0.2), (x + 0.35, 3.2, 0.4), "claw")         # the killing claw
    m.bone("tail", "body", (0, 19, 7))
    return m


# ------------------------------------------------------------------ Haast's Eagle, eagle rig (flying boss)
def haast_eagle():
    m = Model("haast_eagle", 256, seed=131)
    m.material("plumage", "#3e2c1e", "feather", marks=("belly",))
    m.material("wing", "#4a3424", "feather")
    m.material("tips", "#22180f", "feather")
    m.material("bar", "#8a6a48", "feather")
    m.material("head", "#2e2218", "feather")
    m.material("beak", "#e0b040", "bone")
    m.material("leg", "#d8b040", "scales")
    m.material("talon", "#1a1410", "dark")
    m.material("eye", "#f0c838", "plain")
    m.look = dict(belly="#7a5a3c", belly_cut=0.45)
    m.bone("body", None, (0, 10, 0))
    m.cube("body", (-3.5, 6, -6), (3.5, 12, 7), "plumage")
    m.bone("head", "body", (0, 12, -6))
    m.cube("head", (-2.2, 10, -10), (2.2, 15, -5.5), "head")
    m.cube("head", (-2.4, 13.5, -9.5), (2.4, 15.2, -6), "tips")                # heavy brow
    m.cube("head", (-1.2, 10.5, -13.5), (1.2, 13.5, -10), "beak")
    m.cube("head", (-1, 9.5, -14), (1, 11, -12.8), "beak")
    m.sym("head", (-2.25, 12.5, -9), (-2.1, 13.5, -8), "eye")
    m.bone("jaw", "head", (0, 10.6, -10))
    m.cube("jaw", (-1, 9.8, -12.6), (1, 10.6, -10), "beak")
    for side, s in (("l", -1), ("r", 1)):
        b1, b2 = f"wing_{side}", f"wing_{side}2"
        m.bone(b1, "body", (s * 3.5, 11, -2))
        lo, hi = sorted((s * 3.5, s * 13))
        m.cube(b1, (lo, 10.4, -4), (hi, 11.6, 5), "wing")
        m.cube(b1, (lo, 10.3, 5), (hi, 11.0, 8), "bar")
        m.bone(b2, b1, (s * 13, 11, -2))
        lo, hi = sorted((s * 13, s * 23))
        m.cube(b2, (lo, 10.5, -3), (hi, 11.4, 5), "wing")
        m.cube(b2, (lo, 10.4, 5), (hi, 11.0, 9), "tips")
        for i in range(4):                                                 # spread primary feathers
            fx = s * (23 + i * 0.0) if False else s * 23
            z0 = -3 + i * 2
            lo2, hi2 = sorted((fx, fx + s * (4 - i * 0.6)))
            m.cube(b2, (lo2, 10.5, z0), (hi2, 11.1, z0 + 1.6), "tips")
    m.bone("tail", "body", (0, 9, 7))
    m.cube("tail", (-3.5, 8.5, 7), (3.5, 9.5, 15), "wing")
    m.cube("tail", (-3.6, 8.4, 13), (3.6, 9.6, 15), "bar")
    for bn, x in (("leg_l", -1.8), ("leg_r", 1.8)):
        m.bone(bn, "body", (x, 6.5, 1))
        m.cube(bn, (x - 1.2, 4, -0.5), (x + 1.2, 7, 2.5), "plumage")         # feathered thighs
        m.cube(bn, (x - 0.8, 1, 0.2), (x + 0.8, 4.5, 1.8), "leg")
        m.cube(bn, (x - 1.4, 0, -1.6), (x + 1.4, 1, 2.2), "leg")
        m.cube(bn, (x - 1.2, -0.8, -2.4), (x - 0.6, 0.4, -1.4), "talon")
        m.cube(bn, (x + 0.6, -0.8, -2.4), (x + 1.2, 0.4, -1.4), "talon")
        m.cube(bn, (x - 0.3, -0.8, 2.0), (x + 0.3, 0.4, 3.0), "talon")
    return m


# ------------------------------------------------------------------ Komodo Dragon, lizard rig
def komodo():
    m = Model("komodo", 256, seed=137)
    m.material("scale", "#6e6656", "scales", marks=("belly", "back", "spots"))
    m.material("head", "#5e584a", "scales")
    m.material("leg", "#646050", "scales")
    m.material("claw", "#1e1a16", "dark")
    m.material("tongue", "#e8c040", "plain")
    m.material("eye", "#c89a30", "plain")
    m.material("drool", "#b8d8a8", "plain")
    m.look = dict(belly="#9a9078", belly_cut=0.32, back="#4e4a3e", spots="#7e7460", spot_rate=0.82, spot_min=0.3)
    m.bone("body", None, (0, 5.5, 0))
    m.cube("body", (-3.5, 3, -8), (3.5, 8, 8), "scale")
    m.cube("body", (-2.6, 3.5, -12), (2.6, 7.4, -8), "scale")                  # neck
    m.bone("head", "body", (0, 6, -12))
    m.cube("head", (-2.5, 3.6, -17), (2.5, 7.4, -12), "head")
    m.cube("head", (-1.8, 3.6, -21), (1.8, 6.4, -17), "head")
    m.sym("head", (-2.55, 6, -16.2), (-2.4, 6.8, -15.2), "eye")
    m.bone("jaw", "head", (0, 4, -13))
    m.cube("jaw", (-1.7, 2.4, -20.5), (1.7, 3.8, -13), "head")
    m.cube("jaw", (-0.3, 3.4, -24), (0.3, 3.7, -20.4), "tongue")
    m.sym("jaw", (-0.8, 3.4, -24.6), (-0.1, 3.7, -23.8), "tongue")
    m.cube("jaw", (-1.2, 1.4, -19), (-0.6, 2.4, -18.4), "drool")
    # sprawling legs: out to the side, then down
    for bn, x, z in (("leg_fl", -3.5, -5), ("leg_fr", 3.5, -5), ("leg_bl", -3.5, 5), ("leg_br", 3.5, 5)):
        s = -1 if x < 0 else 1
        m.bone(bn, "body", (x, 5, z))
        lo, hi = sorted((x, x + s * 3))
        m.cube(bn, (lo, 3.6, z - 1.3), (hi, 5.8, z + 1.3), "leg")
        lo, hi = sorted((x + s * 1.6, x + s * 3.6))
        m.cube(bn, (lo, 0.8, z - 1.2), (hi, 4.2, z + 1.2), "leg")
        m.cube(bn, (lo - 0.2, 0, z - 2.2), (hi + 0.2, 0.9, z + 1.2), "leg")
        for cx in (lo, (lo + hi) / 2 - 0.25, hi - 0.5):
            m.cube(bn, (cx, 0, z - 3.0), (cx + 0.5, 0.6, z - 2.2), "claw")
    m.bone("tail", "body", (0, 5.5, 8))
    m.cube("tail", (-2.5, 3, 8), (2.5, 7, 16), "scale")
    m.bone("tail2", "tail", (0, 5, 16))
    m.cube("tail2", (-1.6, 3.4, 16), (1.6, 6.2, 25), "scale")
    m.cube("tail2", (-0.9, 3.8, 25), (0.9, 5.4, 30), "scale")
    return m


# ------------------------------------------------------------------ Giant Anaconda, serpent rig
def anaconda():
    m = Model("anaconda", 512, seed=139)
    m.material("scale", "#4a5a2a", "scales", marks=("belly", "spots"))
    m.material("head", "#3e4c22", "scales", marks=("spots",))
    m.material("eye", "#d8b838", "plain")
    m.material("tongue", "#b8283a", "plain")
    m.material("fang", "#ece4cc", "bone")
    m.look = dict(belly="#c8b860", belly_axis="local", belly_y=lambda P: 0 * P[..., 1] + 1.8,
                  spots="#141a0c", spot_rate=0.74)
    m.bone("head", None, (0, 4, 0))
    m.cube("head", (-3, 1.2, -8), (3, 6, 0), "head")
    m.cube("head", (-2.2, 1.6, -11), (2.2, 5, -8), "head")
    m.sym("head", (-3.05, 4.4, -7), (-2.6, 5.4, -5.6), "eye")
    m.bone("jaw", "head", (0, 1.8, -1))
    m.cube("jaw", (-2.6, 0, -10.6), (2.6, 1.6, -1), "head")
    m.cube("jaw", (-0.3, 0.8, -14), (0.3, 1.1, -10.6), "tongue")
    m.sym("jaw", (-1.9, 1.6, -10.2), (-1.4, 2.6, -9.6), "fang")
    z, parent = 0.0, "head"
    n = 18
    for i in range(1, n + 1):
        t = (i - 1) / (n - 1)
        w = 3.6 - 2.6 * t * t
        h = 3.2 - 2.2 * t * t
        ln = 6.5 - 1.5 * t
        bn = f"seg{i}"
        m.bone(bn, parent, (0, 3.5, z))
        m.cube(bn, (-w, 3.5 - h, z - 0.3), (w, 3.5 + h, z + ln), "scale")
        parent, z = bn, z + ln
    return m


# ------------------------------------------------------------------ Walrus Bull
def walrus():
    m = Model("walrus", 256, seed=149)
    m.material("hide", "#a87a62", "hide", marks=("scars", "back"))
    m.material("pad", "#d8b8a0", "hide")
    m.material("whisker", "#efe2c8", "hair")
    m.material("tusk", "#efe6cc", "bone")
    m.material("flipper", "#7a5442", "hide")
    m.material("eye", "#140c08", "dark")
    m.look = dict(back="#94664e", scar_color="#d0a08c",
                  scars=[((-6, 9, -4), (-6, 6, 1)), ((6, 10, -2), (6, 7, 3)), ((-5, 13, 2), (-2, 13, 6))])
    m.bone("body", None, (0, 7, 0))
    m.cube("body", (-6, 1, -9), (6, 13, 8), "hide")
    m.cube("body", (-4.5, 1, 8), (4.5, 9, 13), "hide")
    m.bone("head", "body", (0, 12, -9))
    m.cube("head", (-4.5, 8, -15), (4.5, 15, -8), "hide")
    m.cube("head", (-4, 7, -17), (4, 11.5, -14.5), "pad")
    m.cube("head", (-4.2, 7.6, -17.2), (4.2, 9.6, -16.8), "whisker")
    m.sym("head", (-4.55, 12.5, -13.4), (-4.4, 13.3, -12.6), "eye")
    m.sym("head", (-2.8, 0.5, -16.4), (-1.6, 8, -15.2), "tusk", rot=(-8, 0, 0), pivot=(-2.2, 8, -15.8))
    m.bone("jaw", "head", (0, 7.5, -10))
    m.cube("jaw", (-2.5, 6, -15), (2.5, 7.5, -10), "pad")
    for bn, x in (("leg_fl", -6), ("leg_fr", 6)):
        s = -1 if x < 0 else 1
        m.bone(bn, "body", (x, 4, -4))
        lo, hi = sorted((x, x + s * 5))
        m.cube(bn, (lo, 0, -6.5), (hi, 1.6, -1), "flipper")
    for bn, x in (("leg_bl", -2.5), ("leg_br", 2.5)):
        m.bone(bn, "body", (x, 2, 12))
        m.cube(bn, (x - 2, 0, 12), (x + 2, 1.4, 18), "flipper")
    m.bone("tail", "body", (0, 5, 13))
    return m


MODELS = {"dire_wolf": dire_wolf, "cave_lion": cave_lion, "steppe_bison": steppe_bison, "ground_sloth": ground_sloth,
          "glyptodon": glyptodon, "terror_bird": terror_bird, "haast_eagle": haast_eagle, "komodo": komodo,
          "anaconda": anaconda, "walrus": walrus}

if __name__ == "__main__":
    for k in (sys.argv[1:] or MODELS):
        MODELS[k]().save()
