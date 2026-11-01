"""
Ancient-civilization armor sets: 3D GeckoLib armor models, Minecraft-style textures, inventory icons, item models,
names, and the Java list of sets (AncientSets.java). Sets are listed weakest to strongest; their stats scale
linearly with that order (AncientArmorMaterial), and crafting recipes will follow the same order.

    python3 tools/ancient_armor.py            # everything
    python3 tools/ancient_armor.py sparta     # one set (model + texture + icons)

Each set is built from shared parts (helmet styles, cuirasses, shoulders, skirts, leg and foot pieces), so a new set
is a few lines: pick the parts and the colours.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mobkit import Model, hexrgb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "ragnarok/src/main"
ASSETS = ROOT / "resources/assets/vividlands_ragnarok"
GEO_DIR = ASSETS / "geo/item/armor"
TEX_DIR = ASSETS / "textures/item/armor"
ICON_DIR = ASSETS / "textures/item"
MODEL_DIR = ASSETS / "models/item"
JAVA = ROOT / "java/com/vividlands/ragnarok/armor/AncientSets.java"

H, B, RA, LA, RL, LL, RB, LB = ("armorHead", "armorBody", "armorRightArm", "armorLeftArm",
                                "armorRightLeg", "armorLeftLeg", "armorRightBoot", "armorLeftBoot")


def skeleton(m):
    m.bone(H, None, (0, 24, 0))
    m.bone(B, None, (0, 24, 0))
    m.bone(RA, None, (-5, 22, 0))
    m.bone(LA, None, (5, 22, 0))
    m.bone(RL, None, (-1.9, 12, 0))
    m.bone(LL, None, (1.9, 12, 0))
    m.bone(RB, None, (-1.9, 12, 0))
    m.bone(LB, None, (1.9, 12, 0))


def arms(fn):
    """fn(bone, side, x_in, x_out): the right arm is -x (side -1), the left +x."""
    return [(RA, -1, -4, -8), (LA, 1, 4, 8)]


def legs():
    return [(RL, RB, -1, -4.0, 0.0), (LL, LB, 1, 0.0, 4.0)]


def box(m, bone, x0, y0, z0, x1, y1, z1, mat, rot=None, pivot=None):
    m.cube(bone, (x0, y0, z0), (x1, y1, z1), mat, rot, pivot)


# ================================================================== helmets (bone armorHead)
def h_cap(m, P, low=27.5, mat="helm"):
    box(m, H, -4.6, low, -4.6, 4.6, 32.6, 4.6, P[mat])


def h_rim(m, P, y=27.5, mat="trim"):
    box(m, H, -4.8, y - 0.6, -4.8, 4.8, y + 0.3, 4.8, P[mat])


def h_cheeks(m, P, y0=24.6, mat="helm"):
    m.sym(H, (-4.75, y0, -4.75), (-3.0, 28.0, -0.6), P[mat])


def h_neck(m, P, mat="helm", flare=True):
    box(m, H, -4.8, 25.2, 3.6, 4.8, 28.2, 5.0, P[mat])
    if flare:
        box(m, H, -5.2, 24.6, 4.6, 5.2, 25.6, 6.4, P[mat])


def h_nasal(m, P, mat="helm"):
    box(m, H, -0.6, 25.4, -5.0, 0.6, 28.4, -4.5, P[mat])


def h_brow(m, P, mat="trim"):
    box(m, H, -4.8, 27.6, -5.4, 4.8, 28.6, -4.4, P[mat])


def h_crest(m, P, kind="fore", mat="plume", h=4.0):
    if kind == "fore":                                          # front-to-back fan
        box(m, H, -0.4, 32.4, -1.0, 0.4, 33.4, 1.0, P["trim"])
        box(m, H, -0.75, 33.2, -4.6, 0.75, 33.2 + h, 5.6, P[mat])
        box(m, H, -0.75, 33.2 + h - 1, 5.6, 0.75, 33.2 + h - 0.0, 7.4, P[mat])   # tail hanging back
        box(m, H, -0.75, 30.0, 5.4, 0.75, 33.4, 6.8, P[mat])
    elif kind == "transverse":                                  # side to side (a centurion's)
        box(m, H, -0.6, 32.4, -0.4, 0.6, 33.4, 0.4, P["trim"])
        box(m, H, -5.4, 33.2, -0.75, 5.4, 33.2 + h, 0.75, P[mat])
    elif kind == "tall":                                        # a high horsehair crest on a stand
        box(m, H, -0.4, 32.4, -0.4, 0.4, 35.0, 0.4, P["trim"])
        box(m, H, -0.75, 35.0, -4.0, 0.75, 35.0 + h, 4.6, P[mat])
        box(m, H, -0.75, 31.0, 4.0, 0.75, 35.6, 5.6, P[mat])


def h_cone(m, P, mat="helm", spike="trim"):
    box(m, H, -3.6, 32.4, -3.6, 3.6, 34.0, 3.6, P[mat])
    box(m, H, -2.5, 34.0, -2.5, 2.5, 35.4, 2.5, P[mat])
    box(m, H, -1.3, 35.4, -1.3, 1.3, 36.6, 1.3, P[mat])
    box(m, H, -0.5, 36.6, -0.5, 0.5, 38.0, 0.5, P[spike])


def h_horns(m, P, mat="horn", up=True):
    m.sym(H, (-6.6, 29.8, -1.0), (-4.6, 31.4, 1.0), P[mat])
    if up:
        m.sym(H, (-7.4, 31.2, -0.8), (-6.0, 34.6, 0.8), P[mat])
        m.sym(H, (-7.1, 34.6, -0.5), (-6.3, 36.0, 0.5), P[mat])
    else:
        m.sym(H, (-8.8, 29.2, -0.8), (-6.4, 30.8, 0.8), P[mat])


def h_corinthian(m, P):
    box(m, H, -4.65, 28.6, -4.65, 4.65, 32.6, 4.65, P["helm"])           # dome
    box(m, H, -4.65, 24.2, -3.4, 4.65, 28.6, 4.65, P["helm"])            # sides and back
    m.sym(H, (-4.65, 24.2, -4.75), (-0.7, 27.3, -3.3), P["helm"])        # cheek plates (a T-shaped slit)
    box(m, H, -0.55, 25.6, -4.95, 0.55, 28.6, -4.55, P["helm"])          # nose guard
    box(m, H, -4.8, 28.4, -4.8, 4.8, 28.9, 4.8, P["trim"])


def h_nemes(m, P):
    box(m, H, -4.75, 27.2, -4.75, 4.75, 32.8, 4.75, P["cloth2"])         # striped head-cloth
    m.sym(H, (-4.9, 19.5, -3.6), (-3.3, 27.4, -1.0), P["cloth2"])        # lappets down onto the chest
    box(m, H, -2.6, 20.5, 4.4, 2.6, 27.4, 5.4, P["cloth2"])              # the queue at the back
    box(m, H, -4.9, 28.4, -4.9, 4.9, 29.2, 4.9, P["gold"])               # brow band
    box(m, H, -0.6, 29.0, -5.4, 0.6, 31.6, -4.8, P["gold"])              # uraeus (the cobra)
    box(m, H, -0.4, 31.2, -5.6, 0.4, 32.0, -5.0, P["accent"])


def h_khepresh(m, P):
    box(m, H, -4.65, 27.4, -4.65, 4.65, 33.0, 4.65, P["helm"])
    box(m, H, -4.0, 33.0, -3.4, 4.0, 35.8, 4.8, P["helm"])
    box(m, H, -3.0, 35.8, -2.2, 3.0, 37.2, 4.4, P["helm"])
    box(m, H, -4.8, 27.2, -4.8, 4.8, 28.0, 4.8, P["gold"])
    box(m, H, -0.6, 29.0, -5.3, 0.6, 31.6, -4.7, P["gold"])
    box(m, H, -0.4, 31.2, -5.6, 0.4, 32.0, -5.0, P["accent"])


def h_hood(m, P, mat="cloth", chin=True):
    box(m, H, -4.75, 24.0, -3.2, 4.75, 32.9, 4.75, P[mat])
    box(m, H, -4.75, 29.6, -4.75, 4.75, 32.9, -3.2, P[mat])
    if chin:
        box(m, H, -4.75, 24.0, -4.85, 4.75, 26.4, -3.2, P[mat])
    box(m, H, -2.0, 32.8, -3.4, 2.0, 35.0, 1.0, P[mat], rot=(-18, 0, 0), pivot=(0, 32.8, -1))


def h_kabuto(m, P):
    box(m, H, -4.6, 28.0, -4.6, 4.6, 32.8, 4.6, P["helm"])
    box(m, H, -5.2, 27.0, -3.2, 5.2, 28.0, 5.4, P["armor2"])             # neck guard, flaring out in tiers
    box(m, H, -5.8, 26.0, -2.6, 5.8, 27.0, 5.9, P["armor2"])
    box(m, H, -6.4, 25.0, -2.0, 6.4, 26.0, 6.4, P["armor2"])
    m.sym(H, (-6.2, 27.4, -4.8), (-4.6, 29.4, -2.8), P["armor2"])        # turned-back ears (fukigaeshi)
    box(m, H, -4.8, 28.0, -5.4, 4.8, 28.8, -4.4, P["helm"])              # visor
    m.sym(H, (-3.4, 31.0, -5.3), (-2.6, 37.4, -4.7), P["gold"], rot=(0, 0, -16), pivot=(-1.0, 31.0, -5.0))   # kuwagata
    box(m, H, -1.0, 29.2, -5.4, 1.0, 31.2, -4.9, P["gold"])              # crest badge
    box(m, H, -2.4, 24.4, -5.2, 2.4, 27.0, -4.6, P["accent"])            # menpo (face mask)
    box(m, H, -0.4, 32.8, -0.4, 0.4, 33.6, 0.4, P["gold"])


def h_feathers(m, P, n=9, height=8.0, band="gold", mats=("plume", "plume2")):
    box(m, H, -4.85, 28.0, -4.85, 4.85, 30.2, 4.85, P[band])
    for i in range(n):
        a = -60 + 120 * i / (n - 1)
        x = -3.8 + 7.6 * i / (n - 1)
        hh = height - abs(a) / 60 * 2.5
        box(m, H, x - 0.45, 30.0, -4.6, x + 0.45, 30.0 + hh, -3.9, P[mats[i % 2]], rot=(0, 0, -a * 0.5), pivot=(x, 30.0, -4.25))


def h_eagle(m, P):
    h_cap(m, P, low=27.0, mat="feather")
    box(m, H, -1.9, 29.0, -8.0, 1.9, 31.6, -4.6, P["beak"])              # upper beak over the brow
    box(m, H, -1.3, 27.6, -8.6, 1.3, 29.2, -7.4, P["beak"])              # hooked tip
    box(m, H, -1.7, 24.0, -6.8, 1.7, 25.0, -4.6, P["beak"])              # lower beak under the chin
    m.sym(H, (-4.75, 30.0, -3.6), (-4.55, 31.0, -2.6), P["accent"])      # eagle's eyes
    box(m, H, -3.6, 31.8, 3.8, 3.6, 34.0, 6.6, P["feather"], rot=(-30, 0, 0), pivot=(0, 31.8, 4.6))   # crest feathers


def h_jaguar(m, P):
    h_cap(m, P, low=27.0, mat="pelt")
    m.sym(H, (-4.2, 32.4, -2.0), (-2.6, 34.2, -0.6), P["pelt"])          # ears
    box(m, H, -2.6, 28.4, -7.6, 2.6, 31.2, -4.6, P["pelt"])              # muzzle over the brow
    box(m, H, -1.0, 30.4, -7.9, 1.0, 31.2, -7.5, P["accent"])            # nose
    m.sym(H, (-2.2, 27.4, -7.4), (-1.5, 28.6, -6.8), P["bone"])          # fangs
    m.sym(H, (-4.8, 24.0, -3.4), (-3.4, 27.2, 4.6), P["pelt"])           # the pelt's cheeks
    m.sym(H, (-2.7, 30.6, -6.6), (-2.5, 31.4, -5.6), P["accent"])        # eyes


def h_turban(m, P):
    box(m, H, -4.85, 27.8, -4.85, 4.85, 30.0, 4.85, P["cloth"])
    box(m, H, -4.55, 30.0, -4.55, 4.55, 32.0, 4.55, P["cloth2"])
    box(m, H, -3.8, 32.0, -3.8, 3.8, 33.6, 3.8, P["cloth"])
    box(m, H, -0.8, 30.2, -5.2, 0.8, 31.8, -4.8, P["gold"])
    box(m, H, -0.3, 31.8, -5.0, 0.3, 35.6, -4.4, P["plume"], rot=(-15, 0, 0), pivot=(0, 31.8, -4.7))


def h_spangen(m, P):
    h_cap(m, P, low=28.0)
    h_cone(m, P)
    for x in (-0.4,):
        box(m, H, x, 28.0, -4.85, x + 0.8, 33.0, -4.55, P["gold"])
    m.sym(H, (-4.85, 28.0, -0.4), (-4.55, 33.0, 0.4), P["gold"])
    box(m, H, -4.9, 24.0, -3.2, 4.9, 28.2, 4.9, P["mail"])               # mail aventail
    h_nasal(m, P, "gold")
    box(m, H, -4.85, 27.6, -4.85, 4.85, 28.4, 4.85, P["gold"])


def h_murmillo(m, P):
    h_cap(m, P, low=26.0)
    box(m, H, -5.9, 27.0, -5.9, 5.9, 27.8, 5.9, P["helm"])               # broad brim
    box(m, H, -4.2, 24.2, -5.2, 4.2, 29.0, -4.6, P["grill"])              # grilled visor
    box(m, H, -0.85, 32.4, -4.4, 0.85, 36.2, 5.2, P["helm"])             # fish crest
    box(m, H, -0.4, 36.2, -3.4, 0.4, 37.6, 3.6, P["plume"])


def h_sun(m, P):
    box(m, H, -4.8, 28.0, -4.8, 4.8, 30.0, 4.8, P["gold"])
    box(m, H, -3.2, 30.0, -5.3, 3.2, 36.4, -4.8, P["gold"])              # the sun disk
    box(m, H, -1.6, 31.6, -5.5, 1.6, 34.8, -5.2, P["accent"])
    for i, x in enumerate((-2.6, -1.0, 1.0, 2.6)):
        box(m, H, x - 0.4, 30.0, -3.6, x + 0.4, 37.0 - abs(x) * 0.6, -3.0, P["plume" if i % 2 else "plume2"])


def h_furhat(m, P):
    box(m, H, -4.95, 27.0, -4.95, 4.95, 29.2, 4.95, P["fur"])
    box(m, H, -4.4, 29.2, -4.4, 4.4, 32.6, 4.4, P["helm"])
    box(m, H, -2.4, 32.6, -2.4, 2.4, 34.0, 2.4, P["helm"])
    box(m, H, -0.4, 34.0, -0.4, 0.4, 36.4, 0.4, P["gold"])
    box(m, H, -0.9, 31.0, 4.0, 0.9, 34.4, 5.0, P["plume"], rot=(25, 0, 0), pivot=(0, 34.4, 4.5))   # tassel
    m.sym(H, (-4.95, 23.8, -3.0), (-4.2, 27.2, 3.0), P["fur"])           # ear flaps


def h_topknot(m, P):
    box(m, H, -4.6, 29.4, -4.6, 4.6, 32.4, 4.6, P["cloth"])
    box(m, H, 0.6, 32.4, -1.6, 3.4, 34.6, 1.0, P["hair"])                # the bun, worn to the right
    box(m, H, -4.75, 29.0, -4.75, 4.75, 29.8, 4.75, P["trim"])
    m.sym(H, (-4.8, 24.2, -1.0), (-4.6, 29.0, -0.4), P["trim"])          # chin straps


def h_boar(m, P):
    box(m, H, -4.65, 26.0, -4.65, 4.65, 32.6, 4.65, P["tusk"])           # rows of boar tusks
    h_cheeks(m, P, mat="tusk")
    box(m, H, -0.8, 32.6, -0.8, 0.8, 34.4, 0.8, P["trim"])
    box(m, H, -0.6, 34.4, -0.6, 0.6, 37.4, 3.0, P["plume"], rot=(25, 0, 0), pivot=(0, 34.4, 0))


def h_phrygian(m, P):
    h_cap(m, P, low=27.4)
    box(m, H, -3.2, 32.4, -4.4, 3.2, 34.6, 2.0, P["helm"])
    box(m, H, -2.6, 33.6, -6.0, 2.6, 35.6, -3.4, P["helm"], rot=(20, 0, 0), pivot=(0, 34.6, -4.4))
    h_cheeks(m, P)
    h_rim(m, P)


def h_montefortino(m, P):
    h_cap(m, P, low=27.4)
    box(m, H, -4.8, 26.6, 3.4, 4.8, 27.6, 5.6, P["helm"])
    box(m, H, -0.8, 32.6, -0.8, 0.8, 34.0, 0.8, P["trim"])
    box(m, H, -1.2, 34.0, -1.2, 1.2, 34.8, 1.2, P["trim"])
    m.sym(H, (-1.2, 33.0, -0.5), (-0.4, 39.0, 0.5), P["plume"], rot=(0, 0, 18), pivot=(-0.8, 33.0, 0))
    h_cheeks(m, P)
    h_rim(m, P)


def h_negau(m, P):                                  # Etruscan: round bowl, rolled brim, a ridge on top
    h_cap(m, P, low=28.0)
    box(m, H, -5.2, 27.4, -5.2, 5.2, 28.4, 5.2, P["trim"])
    box(m, H, -0.5, 32.4, -3.6, 0.5, 33.6, 3.6, P["trim"])
    h_cheeks(m, P)


def h_illyrian(m, P):                               # two parallel ridges on top, open face, long cheek plates
    h_cap(m, P, low=27.4)
    m.sym(H, (-1.8, 32.4, -4.4), (-1.0, 33.8, 4.4), P["trim"])
    h_cheeks(m, P, 24.0)
    h_neck(m, P, flare=False)
    box(m, H, -0.6, 33.6, -2.0, 0.6, 37.4, 2.0, P["plume"])


def h_shang(m, P):                                  # Shang bronze: a beast-mask brow and a plume tube
    h_cap(m, P, low=27.0)
    box(m, H, -4.8, 28.0, -5.2, 4.8, 31.0, -4.6, P["trim"])            # taotie mask
    m.sym(H, (-3.4, 29.0, -5.5), (-1.6, 30.2, -5.1), P["accent"])      # its eyes
    m.sym(H, (-5.0, 30.4, -1.2), (-4.6, 33.0, 1.2), P["trim"])         # ear knobs
    box(m, H, -0.7, 32.6, -0.7, 0.7, 34.8, 0.7, P["trim"])
    box(m, H, -0.6, 34.8, -0.6, 0.6, 38.0, 0.6, P["plume"])


def h_olmec(m, P):                                  # the close cap of the colossal heads, with ear flaps
    box(m, H, -4.75, 28.0, -4.75, 4.75, 33.0, 4.75, P["helm"])
    m.sym(H, (-4.95, 24.0, -2.4), (-4.55, 29.0, 2.4), P["helm"])
    for y in (29.0, 30.6):
        box(m, H, -4.9, y, -4.9, 4.9, y + 0.8, -4.6, P["trim"])
    box(m, H, -1.0, 31.6, -5.2, 1.0, 33.4, -4.8, P["accent"])


def h_iberian(m, P):                                # sinew cap with a tall crest across
    h_cap(m, P, low=27.4, mat="leather")
    box(m, H, -0.6, 32.4, -0.6, 0.6, 33.4, 0.6, P["trim"])
    box(m, H, -4.4, 33.2, -0.7, 4.4, 37.0, 0.7, P["plume"])
    m.sym(H, (-4.8, 24.4, -1.0), (-4.6, 28.0, -0.4), P["trim"])


def h_goguryeo(m, P):                               # lamellar bowl, long plume spike, lamellar neck flaps
    h_cap(m, P, low=28.0, mat="lamellar")
    box(m, H, -4.9, 24.6, -3.0, 4.9, 28.4, 5.0, P["lamellar"])
    box(m, H, -4.85, 27.6, -4.85, 4.85, 28.4, 4.85, P["trim"])
    box(m, H, -0.5, 32.6, -0.5, 0.5, 36.0, 0.5, P["trim"])
    box(m, H, -0.9, 35.4, -0.9, 0.9, 38.4, 0.9, P["plume"])


def h_mokot(m, P):                                  # Khmer tiered crown
    box(m, H, -4.8, 28.0, -4.8, 4.8, 30.2, 4.8, P["gold"])
    box(m, H, -3.8, 30.2, -3.8, 3.8, 32.4, 3.8, P["gold"])
    box(m, H, -2.8, 32.4, -2.8, 2.8, 34.4, 2.8, P["gold"])
    box(m, H, -1.8, 34.4, -1.8, 1.8, 36.2, 1.8, P["gold"])
    box(m, H, -0.8, 36.2, -0.8, 0.8, 38.6, 0.8, P["gold"])
    for y in (29.0, 31.2, 33.4):
        box(m, H, -0.6, y, -5.0 + (y - 29) * 0.45, 0.6, y + 1.0, -4.6 + (y - 29) * 0.45, P["accent"])
    m.sym(H, (-5.2, 26.0, -0.8), (-4.7, 29.0, 0.8), P["gold"])        # ear ornaments


def h_suttonhoo(m, P):                              # Anglo-Saxon: full face mask with brows, nose and moustache
    h_cap(m, P, low=28.0)
    box(m, H, -0.6, 32.4, -4.8, 0.6, 33.6, 4.8, P["gold"])            # crest ridge
    box(m, H, -4.65, 24.2, -3.4, 4.65, 28.6, 4.65, P["helm"])         # neck and cheek guards
    m.sym(H, (-4.7, 24.4, -4.8), (-2.4, 27.0, -3.3), P["helm"])       # cheek plates
    m.sym(H, (-4.0, 28.0, -5.0), (-0.6, 28.8, -4.6), P["gold"])       # eyebrows
    box(m, H, -0.7, 25.6, -5.2, 0.7, 28.6, -4.6, P["gold"])           # nose
    box(m, H, -2.4, 25.0, -5.0, 2.4, 25.8, -4.6, P["gold"])           # moustache
    box(m, H, -4.8, 27.6, -4.8, 4.8, 28.2, 4.8, P["trim"])


HELMETS = {
    "cap": lambda m, P: (h_cap(m, P), h_rim(m, P)),
    "conical": lambda m, P: (h_cap(m, P, 28.0), h_cone(m, P), h_nasal(m, P), h_rim(m, P, 28.0)),
    "conical_mail": lambda m, P: (h_spangen(m, P)),
    "corinthian": lambda m, P: (h_corinthian(m, P), h_crest(m, P, "fore")),
    "attic": lambda m, P: (h_cap(m, P), h_brow(m, P), h_cheeks(m, P), h_neck(m, P, flare=False), h_crest(m, P, "tall", h=3.0)),
    "galea": lambda m, P: (h_cap(m, P), h_brow(m, P), h_cheeks(m, P), h_neck(m, P)),
    "galea_crest": lambda m, P: (h_cap(m, P), h_brow(m, P), h_cheeks(m, P), h_neck(m, P), h_crest(m, P, "fore", h=3.0)),
    "galea_transverse": lambda m, P: (h_cap(m, P), h_brow(m, P), h_cheeks(m, P), h_neck(m, P), h_crest(m, P, "transverse", h=3.4)),
    "montefortino": h_montefortino,
    "phrygian": h_phrygian,
    "boar": h_boar,
    "horned": lambda m, P: (h_cap(m, P), h_rim(m, P), h_horns(m, P)),
    "horned_side": lambda m, P: (h_cap(m, P), h_rim(m, P), h_horns(m, P, up=False), h_nasal(m, P)),
    "nemes": h_nemes,
    "khepresh": h_khepresh,
    "hood": h_hood,
    "kabuto": h_kabuto,
    "feathers": h_feathers,
    "eagle": h_eagle,
    "jaguar": h_jaguar,
    "turban": h_turban,
    "murmillo": h_murmillo,
    "sun": h_sun,
    "furhat": h_furhat,
    "topknot": h_topknot,
    "negau": h_negau,
    "illyrian": h_illyrian,
    "shang": h_shang,
    "olmec": h_olmec,
    "iberian": h_iberian,
    "goguryeo": h_goguryeo,
    "mokot": h_mokot,
    "suttonhoo": h_suttonhoo,
    "akkad": lambda m, P: (h_cap(m, P, 27.0), h_rim(m, P, 27.0), h_cheeks(m, P), h_neck(m, P, flare=False)),
    "hun": lambda m, P: (h_cap(m, P, 28.0), h_cone(m, P), h_furhat_brim(m, P), h_nasal(m, P)),
}


def h_furhat_brim(m, P):
    box(m, H, -4.95, 27.0, -4.95, 4.95, 28.6, 4.95, P["fur"])


# ================================================================== body (chestplate: armorBody + arms)
def torso(m, P, mat="chest", w=4.6, d=2.7, y0=11.6, y1=24.4):
    box(m, B, -w, y0, -d, w, y1, d, P[mat])


def c_muscle(m, P):
    torso(m, P)
    m.sym(B, (-3.9, 19.6, -3.05), (-0.3, 22.2, -2.6), P["chest"])        # chest muscles
    for y in (14.0, 15.9, 17.8):
        m.sym(B, (-2.8, y, -2.95), (-0.4, y + 1.5, -2.6), P["chest"])    # stomach
    box(m, B, -4.7, 23.4, -2.8, 4.7, 24.6, 2.8, P["trim"])


def c_lino(m, P):
    torso(m, P, "cloth")
    box(m, B, -4.75, 14.6, -2.85, 4.75, 18.6, 2.85, P["scale"])          # bronze scales round the waist
    m.sym(B, (-4.9, 23.8, -2.9), (-1.2, 25.0, 2.9), P["cloth"])          # shoulder flaps
    box(m, B, -4.75, 18.6, -2.85, 4.75, 19.2, 2.85, P["trim"])


def c_scale(m, P):
    torso(m, P, "scale")
    box(m, B, -4.8, 23.6, -2.9, 4.8, 24.6, 2.9, P["trim"])


def c_lamellar(m, P):
    torso(m, P, "lamellar")
    box(m, B, -4.8, 23.6, -2.9, 4.8, 24.6, 2.9, P["trim"])


def c_segmentata(m, P):
    torso(m, P, "bands")
    box(m, B, -3.0, 19.6, -3.0, 3.0, 23.6, -2.6, P["chest"])             # breast plates
    box(m, B, -4.8, 23.4, -2.9, 4.8, 24.6, 2.9, P["chest"])
    box(m, B, -0.4, 21.0, -3.1, 0.4, 22.0, -2.9, P["gold"])


def c_mail(m, P):
    torso(m, P, "mail")


def c_leather(m, P):
    torso(m, P, "leather")


def c_dendra(m, P):
    torso(m, P, "bands", w=5.4, d=3.4)
    box(m, B, -4.6, 24.0, -3.2, 4.6, 26.4, 3.2, P["chest"])              # high neck guard


def c_quilted(m, P):
    torso(m, P, "cloth", w=5.0, d=3.1)
    box(m, B, -5.1, 23.6, -3.2, 5.1, 24.6, 3.2, P["trim"])


def c_oyoroi(m, P):
    torso(m, P, "lamellar")
    box(m, B, -4.0, 19.0, -3.1, 4.0, 23.8, -2.7, P["armor2"])           # breast plate (tsurubashiri)
    box(m, B, -4.8, 23.6, -2.9, 4.8, 24.6, 2.9, P["trim"])


def c_pelt(m, P):
    torso(m, P, "leather")
    box(m, B, -4.9, 20.6, -3.0, 4.9, 24.9, 3.0, P["fur"])


def c_robe(m, P):
    torso(m, P, "cloth")
    box(m, B, -4.75, 18.0, -2.85, 4.75, 24.0, 2.85, P["scale"])
    box(m, B, -4.8, 23.6, -2.9, 4.8, 24.6, 2.9, P["trim"])


CHESTS = {"muscle": c_muscle, "linothorax": c_lino, "scale": c_scale, "lamellar": c_lamellar, "segmentata": c_segmentata,
          "mail": c_mail, "leather": c_leather, "dendra": c_dendra, "quilted": c_quilted, "oyoroi": c_oyoroi,
          "pelt": c_pelt, "robe": c_robe}


def belt(m, P, mat="belt"):
    box(m, B, -4.85, 11.8, -2.95, 4.85, 13.2, 2.95, P[mat])
    box(m, B, -0.8, 11.9, -3.15, 0.8, 13.1, -2.9, P["gold"])


def skirt(m, P, kind):
    if kind == "pteruges":                                       # leather strips hanging from the waist
        for i in range(6):
            x = -4.6 + i * 1.6
            box(m, B, x, 7.6, -2.95, x + 1.3, 12.0, -2.6, P["strips"])
            box(m, B, x, 7.6, 2.6, x + 1.3, 12.0, 2.95, P["strips"])
        m.sym(B, (-4.95, 7.6, -2.6), (-4.6, 12.0, 2.6), P["strips"])
    elif kind == "kilt":
        box(m, B, -4.75, 6.8, -2.85, 4.75, 12.0, 2.85, P["cloth"])
        box(m, B, -1.4, 6.4, -3.0, 1.4, 12.0, -2.85, P["cloth2"])        # front panel
    elif kind == "scale":
        box(m, B, -4.85, 7.0, -2.95, 4.85, 12.0, 2.95, P["scale"])
    elif kind == "panels":                                       # four hanging panels (kusazuri, tassets)
        for x0, x1, z0, z1 in ((-4.7, -0.2, -3.0, -2.6), (0.2, 4.7, -3.0, -2.6), (-4.7, -0.2, 2.6, 3.0), (0.2, 4.7, 2.6, 3.0)):
            box(m, B, x0, 6.8, z0, x1, 12.0, z1, P["armor2"])
    elif kind == "robe":
        box(m, B, -4.8, 4.0, -2.95, 4.8, 12.0, 2.95, P["cloth"])


SHOULDERS = {}


def s_plate(m, P, mat="chest"):
    for bone, s, xi, xo in arms(None):
        lo, hi = sorted((xi + s * -0.2, xo + s * 0.8))
        box(m, bone, lo, 20.6, -2.85, hi, 24.7, 2.85, P[mat])


def s_layered(m, P, mat="chest"):
    for bone, s, xi, xo in arms(None):
        for k, (y0, y1, out) in enumerate(((22.0, 24.8, 0.9), (19.8, 22.2, 0.8), (17.8, 20.0, 0.6))):
            lo, hi = sorted((xi + s * -0.2, xo + s * out))
            box(m, bone, lo, y0, -2.8 + k * 0.1, hi, y1, 2.8 - k * 0.1, P[mat])


def s_sode(m, P):
    for bone, s, xi, xo in arms(None):
        lo, hi = sorted((xo + s * 0.2, xo + s * 1.4))
        box(m, bone, lo, 16.4, -3.0, hi, 24.6, 3.0, P["lamellar"])
        lo, hi = sorted((xi, xo + s * 1.4))
        box(m, bone, lo, 24.0, -3.0, hi, 24.8, 3.0, P["trim"])


def s_fur(m, P):
    for bone, s, xi, xo in arms(None):
        lo, hi = sorted((xi + s * -0.4, xo + s * 1.0))
        box(m, bone, lo, 20.4, -3.0, hi, 24.9, 3.0, P["fur"])


def s_sleeve(m, P, mat="scale", y0=16.0):
    for bone, s, xi, xo in arms(None):
        lo, hi = sorted((xi, xo + s * 0.6))
        box(m, bone, lo, y0, -2.6, hi, 24.5, 2.6, P[mat])


def s_flap(m, P):
    pass


def sleeves(m, P):
    """Every chestplate covers the whole arm (like the armour mods do): a sleeve of the set's sleeve material."""
    for bone, s_, xi, xo in arms(None):
        lo, hi = sorted((xi - s_ * 0.05, xo + s_ * 0.5))
        box(m, bone, lo, 11.6, -2.5, hi, 24.5, 2.5, P["sleeve"])
        lo, hi = sorted((xi - s_ * 0.05, xo + s_ * 0.6))
        box(m, bone, lo, 11.5, -2.6, hi, 13.2, 2.6, P["cuff"])


def cape(m, P, mat="cape"):
    box(m, B, -4.7, 7.0, 2.75, 4.7, 24.2, 3.45, P[mat])
    box(m, B, -4.9, 23.2, -2.9, 4.9, 24.7, 3.5, P["gold"])


def bracers(m, P, mat="leather"):
    for bone, s, xi, xo in arms(None):
        lo, hi = sorted((xi, xo + s * 0.5))
        box(m, bone, lo, 12.6, -2.55, hi, 16.4, 2.55, P[mat])


SHOULDERS = {"plate": s_plate, "layered": s_layered, "sode": s_sode, "fur": s_fur, "sleeve": s_sleeve,
             "mail_sleeve": lambda m, P: s_sleeve(m, P, "mail", 15.0), "none": s_flap,
             "lamellar_sleeve": lambda m, P: s_sleeve(m, P, "lamellar", 17.0)}


# ================================================================== legs and feet
def l_trousers(m, P, mat="cloth3"):
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.45, 4.0, -2.5, x1 + 0.45, 12.4, 2.5, P[mat])


def l_haidate(m, P):
    l_trousers(m, P)
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.6, 6.0, -2.75, x1 + 0.6, 11.6, -2.45, P["lamellar"])


def l_wrap(m, P):
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.45, 5.0, -2.5, x1 + 0.45, 12.4, 2.5, P["wrap"])


def l_scale(m, P):
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.5, 4.0, -2.55, x1 + 0.5, 12.4, 2.55, P["scale"])


def l_mail(m, P):
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.45, 4.0, -2.5, x1 + 0.45, 12.4, 2.5, P["mail"])


def l_thighguard(m, P, mat="chest"):
    l_trousers(m, P)
    for leg, boot, s, x0, x1 in legs():
        box(m, leg, x0 - 0.6, 7.0, -2.7, x1 + 0.6, 11.0, 2.7, P[mat])


LEGS = {"trousers": l_trousers, "haidate": l_haidate, "wrap": l_wrap, "scale": l_scale, "mail": l_mail,
        "thighguard": l_thighguard, "bare": lambda m, P: l_trousers(m, P, "cloth")}


def f_sandal(m, P):
    for leg, boot, s, x0, x1 in legs():
        box(m, boot, x0 - 0.25, 0.4, -2.3, x1 + 0.25, 6.4, 2.3, P["wrap"])          # leg wraps under the straps
        box(m, boot, x0 - 0.3, 0.0, -2.7, x1 + 0.3, 0.6, 2.4, P["leather"])
        for y in (1.4, 2.8, 4.2):
            box(m, boot, x0 - 0.35, y, -2.4, x1 + 0.35, y + 0.5, 2.4, P["leather"])


def f_greaves(m, P, mat="chest"):
    f_sandal(m, P)
    for leg, boot, s, x0, x1 in legs():
        box(m, boot, x0 - 0.45, 1.0, -2.75, x1 + 0.45, 7.4, -1.0, P[mat])   # shin plate
        m.cube(boot, (x0 - 0.5, 1.0, -1.2), (x0 - 0.3, 7.0, 1.6), P[mat])
        m.cube(boot, (x1 + 0.3, 1.0, -1.2), (x1 + 0.5, 7.0, 1.6), P[mat])


def f_boots(m, P, mat="leather", cuff="leather", h=5.0):
    for leg, boot, s, x0, x1 in legs():
        box(m, boot, x0 - 0.4, 0.0, -2.6, x1 + 0.4, h, 2.5, P[mat])
        box(m, boot, x0 - 0.55, h - 1.2, -2.7, x1 + 0.55, h + 0.2, 2.65, P[cuff])
        box(m, boot, x0 - 0.4, 0.0, -3.2, x1 + 0.4, 1.4, -2.5, P[mat])     # toe


def f_upturned(m, P):
    f_boots(m, P, "leather", "trim", 4.6)
    for leg, boot, s, x0, x1 in legs():
        box(m, boot, x0 + 0.8, 1.0, -4.0, x1 - 0.8, 2.2, -3.0, P["leather"])


FEET = {"sandal": f_sandal, "greaves": f_greaves, "boots": f_boots, "fur_boots": lambda m, P: f_boots(m, P, "leather", "fur", 5.4),
        "metal_boots": lambda m, P: f_boots(m, P, "chest", "trim", 5.0), "upturned": f_upturned,
        "wrapped": lambda m, P: f_boots(m, P, "wrap", "leather", 6.0),
        "lacquer_greaves": lambda m, P: f_greaves(m, P, "armor2")}


# ================================================================== the sets, weakest to strongest
MAT = {   # common materials: (colour, style, extra)
    "bronze": ("#b07a3a", "metal", {}), "bronze_scale": ("#b07a3a", "scales", {}), "copper": ("#b8693e", "metal", {}),
    "iron": ("#8a8d94", "metal", {}), "steel": ("#aab0b8", "metal", {}), "dark_iron": ("#4e5058", "metal", {}),
    "gold": ("#d6a832", "gold", {}), "silver": ("#c8ccd2", "metal", {}),
    "linen": ("#e8e0c8", "cloth", {}), "leather": ("#7a5434", "hide", {}), "dark_leather": ("#4a3424", "hide", {}),
    "fur": ("#8a6a48", "fur", {}), "white_fur": ("#e2ddd2", "fur", {}), "black_fur": ("#2e2a28", "fur", {}),
    "red_cloth": ("#9a2a22", "cloth", {}), "blue_cloth": ("#2e4a8a", "cloth", {}), "purple_cloth": ("#5e2a6a", "cloth", {}),
    "green_cloth": ("#3a6a3a", "cloth", {}), "black_cloth": ("#2a2a2e", "cloth", {}), "white_cloth": ("#ece8dc", "cloth", {}),
    "ivory": ("#e8dcb8", "bone", {}), "bone": ("#d8ceb4", "bone", {}),
}


def S(id, title, civ, helmet, chest, shoulders, skirt_kind, leg, foot, P, names, belt_mat="belt", bracer=None, glow=None,
      cloak=None):
    if cloak:
        P = dict(P, cape=cloak)
    return dict(id=id, title=title, civ=civ, helmet=helmet, chest=chest, shoulders=shoulders, skirt=skirt_kind, legs=leg,
                feet=foot, P=P, names=names, belt=belt_mat, bracer=bracer, glow=glow, cloak=cloak)


def pal(**kw):
    """Role -> (colour, style, extra). Unlisted roles fall back to sensible defaults."""
    base = {"helm": MAT["bronze"], "trim": MAT["bronze"], "chest": MAT["bronze"], "plume": ("#9a2a22", "hair", {}),
            "plume2": ("#e8c040", "hair", {}), "cloth": MAT["linen"], "cloth2": MAT["red_cloth"], "cloth3": MAT["linen"],
            "leather": MAT["leather"], "belt": MAT["leather"], "gold": MAT["gold"], "strips": MAT["leather"],
            "scale": MAT["bronze_scale"], "lamellar": ("#8a8d94", "lamellar", {}), "mail": ("#8a8d94", "mail", {}),
            "bands": ("#9aa0a8", "metal", {"band": ("#5a4030", 3)}), "fur": MAT["fur"], "accent": ("#3a6aa8", "plain", {}),
            "armor2": ("#2a2a2e", "lamellar", {}), "wrap": ("#c8bca0", "cloth", {"band": ("#8a7a60", 2)}),
            "horn": MAT["ivory"], "tusk": ("#e8dcb8", "bone", {"band": ("#6a4a2c", 2)}), "feather": ("#6a4a2c", "feather", {}),
            "beak": ("#e0b040", "bone", {}), "pelt": ("#c89a40", "fur", {"studs": ("#2a1c10", 2)}), "bone": MAT["bone"],
            "grill": ("#8a8d94", "mail", {}), "hair": ("#2a1c14", "hair", {})}
    base.update(kw)
    base.setdefault("sleeve", base["cloth"])
    base.setdefault("cuff", base["trim"])
    return base


SETS = [
    S("sumerian", "Sumerian", "Sumer", "cap", "leather", "none", "kilt", "bare", "sandal",
      pal(helm=MAT["copper"], trim=MAT["copper"], leather=("#6a4a30", "hide", {"studs": ("#b8693e", 3)}),
          cloth=("#d8ccaa", "cloth", {"band": ("#8a6a40", 3)}), cloth2=MAT["linen"]),
      ("Copper Helm", "Studded Cloak", "Wool Kilt", "Reed Sandals")),
    S("egyptian", "Egyptian", "Egypt", "nemes", "linothorax", "none", "kilt", "bare", "sandal",
      pal(cloth=MAT["linen"], cloth2=("#e8c040", "cloth", {"band": ("#2e4a8a", 2)}), accent=("#3a8aa8", "plain", {}),
          scale=("#c89a40", "scales", {}), trim=MAT["gold"]),
      ("Nemes Headdress", "Linen Corslet", "Shendyt Kilt", "Papyrus Sandals")),
    S("minoan", "Minoan", "Crete", "boar", "linothorax", "none", "kilt", "bare", "sandal",
      pal(cloth=("#e8e0c8", "cloth", {"band": ("#2e6aa8", 4)}), cloth2=("#2e6aa8", "cloth", {}), plume=("#2e6aa8", "hair", {})),
      ("Boar-Tusk Helmet", "Painted Linen", "Bull-Leaper's Kilt", "Sandals")),
    S("nubian", "Nubian", "Kush", "feathers", "leather", "none", "kilt", "bare", "sandal",
      pal(leather=("#8a5a30", "hide", {"studs": ("#d6a832", 3)}), plume=("#ece8dc", "feather", {}), plume2=("#2a2a2e", "feather", {}),
          cloth=("#c8501e", "cloth", {"band": ("#d6a832", 3)}), cloth2=MAT["gold"]),
      ("Archer's Plumes", "Bowman's Harness", "Royal Kilt", "Desert Sandals"), bracer="gold"),
    S("hittite", "Hittite", "Hatti", "conical", "scale", "sleeve", "scale", "trousers", "upturned",
      pal(cloth3=("#7a3a2a", "cloth", {}), scale=("#b07a3a", "scales", {}), plume=("#2a1c14", "hair", {})),
      ("Charioteer's Cone", "Bronze Scale Coat", "Scale Leggings", "Upturned Boots")),
    S("mycenaean", "Mycenaean", "Mycenae", "boar", "dendra", "layered", "none", "trousers", "greaves",
      pal(chest=("#c08a40", "metal", {}), bands=("#c08a40", "metal", {"band": ("#6a4a28", 3)})),
      ("Boar-Tusk Helm", "Dendra Cuirass", "Linen Leggings", "Bronze Greaves")),
    S("assyrian", "Assyrian", "Assyria", "conical", "lamellar", "lamellar_sleeve", "scale", "trousers", "boots",
      pal(helm=MAT["iron"], trim=MAT["bronze"], lamellar=("#8a8d94", "lamellar", {}), scale=("#8a8d94", "scales", {}),
          cloth3=("#7a2a2a", "cloth", {"band": ("#d6a832", 4)}), leather=("#5a3a24", "hide", {})),
      ("Pointed Helm", "Iron Lamellar", "Fringed Leggings", "Laced Boots")),
    S("babylonian", "Babylonian", "Babylon", "turban", "robe", "none", "robe", "trousers", "upturned",
      pal(cloth=("#2e4a8a", "cloth", {"band": ("#d6a832", 4)}), cloth2=("#e8c040", "cloth", {}), scale=("#d6a832", "scales", {}),
          plume=("#ece8dc", "feather", {}), cloth3=("#2e4a8a", "cloth", {}), trim=MAT["gold"]),
      ("Royal Turban", "Ishtar Robe", "Embroidered Leggings", "Upturned Slippers")),
    S("celtic", "Celtic", "Gaul", "horned", "mail", "none", "none", "trousers", "boots",
      pal(helm=MAT["bronze"], horn=MAT["bronze"], cloth3=("#3a6a3a", "cloth", {"band": ("#9a2a22", 3)}), trim=MAT["gold"]),
      ("Horned Helm", "Ring-Mail Shirt", "Checked Trousers", "Leather Shoes"), belt_mat="gold"),
    S("thracian", "Thracian", "Thrace", "phrygian", "scale", "sleeve", "none", "trousers", "boots",
      pal(scale=("#b07a3a", "scales", {}), cloth3=("#5e2a6a", "cloth", {"band": ("#d6a832", 3)}), leather=("#4a3424", "hide", {})),
      ("Phrygian Helm", "Scale Corslet", "Patterned Trousers", "Fawn-Skin Boots")),
    S("athenian", "Athenian", "Athens", "attic", "linothorax", "none", "pteruges", "bare", "greaves",
      pal(cloth=MAT["white_cloth"], plume=("#2e4a8a", "hair", {}), strips=MAT["white_cloth"]),
      ("Attic Helmet", "Linothorax", "Chiton", "Bronze Greaves")),
    S("spartan", "Spartan", "Sparta", "corinthian", "muscle", "none", "pteruges", "bare", "greaves",
      pal(cloth=("#9a2a22", "cloth", {}), plume=("#9a2a22", "hair", {}), strips=("#8a2a20", "hide", {})),
      ("Corinthian Helm", "Bronze Cuirass", "Crimson Chiton", "Hoplite Greaves"), cloak=("#8a2018", "cloth", {})),
    S("macedonian", "Macedonian", "Macedon", "phrygian", "linothorax", "none", "pteruges", "bare", "greaves",
      pal(cloth=("#ece8dc", "cloth", {"band": ("#5e2a6a", 5)}), helm=("#c08a40", "metal", {}), plume=("#ece8dc", "hair", {}),
          scale=("#c8ccd2", "scales", {})),
      ("Phrygian Helm", "Phalangite Corslet", "Pteruges", "Phalanx Greaves"), cloak=("#ece8dc", "cloth", {"band": ("#5e2a6a", 5)})),
    S("scythian", "Scythian", "Scythia", "hood", "scale", "sleeve", "none", "trousers", "boots",
      pal(cloth=("#9a2a22", "cloth", {"band": ("#d6a832", 4)}), scale=("#d6a832", "scales", {}), cloth3=("#2e4a8a", "cloth", {}),
          leather=("#5a3a24", "hide", {})),
      ("Riding Hood", "Gold Scale Coat", "Riding Trousers", "Soft Boots")),
    S("persian", "Persian", "Persia", "hood", "scale", "sleeve", "robe", "trousers", "boots",
      pal(cloth=("#e8dcb8", "cloth", {}), scale=("#8a8d94", "scales", {}), cloth3=("#5e2a6a", "cloth", {"band": ("#d6a832", 3)}),
          trim=MAT["gold"]),
      ("Immortal's Tiara", "Scale Tunic", "Immortal's Robe", "Persian Boots"), cloak=("#5e2a6a", "cloth", {"trim": "#d6a832"})),
    S("carthaginian", "Carthaginian", "Carthage", "montefortino", "muscle", "none", "pteruges", "bare", "greaves",
      pal(chest=("#c08a40", "metal", {}), cloth=("#5e2a6a", "cloth", {}), plume=("#ece8dc", "feather", {}),
          strips=("#5e2a6a", "cloth", {})),
      ("Montefortino Helm", "Punic Cuirass", "Tyrian Purple Chiton", "Greaves")),
    S("roman", "Legionary", "Rome", "galea", "segmentata", "layered", "pteruges", "bare", "sandal",
      pal(helm=MAT["steel"], trim=MAT["bronze"], chest=MAT["steel"], bands=("#aab0b8", "metal", {"band": ("#5a4030", 3)}),
          cloth=("#9a2a22", "cloth", {}), strips=("#7a5434", "hide", {"studs": ("#b07a3a", 2)})),
      ("Galea", "Lorica Segmentata", "Legion Tunic", "Caligae"), cloak=("#9a2a22", "cloth", {})),
    S("gladiator", "Gladiator", "Rome", "murmillo", "leather", "plate", "kilt", "wrap", "greaves",
      pal(helm=MAT["bronze"], chest=MAT["bronze"], cloth=MAT["white_cloth"], cloth2=("#9a2a22", "cloth", {}),
          plume=("#e8c040", "hair", {}), leather=("#7a5434", "hide", {"studs": ("#b07a3a", 3)})),
      ("Murmillo Helm", "Arena Harness", "Subligaculum", "Arena Greaves"), bracer="leather"),
    S("centurion", "Centurion", "Rome", "galea_transverse", "mail", "plate", "pteruges", "bare", "greaves",
      pal(helm=MAT["steel"], trim=MAT["silver"], mail=("#a8aeb6", "mail", {"studs": ("#d6a832", 4)}), chest=MAT["silver"],
          cloth=("#9a2a22", "cloth", {}), strips=("#7a5434", "hide", {"studs": ("#c8ccd2", 2)})),
      ("Crested Galea", "Phalerae Mail", "Centurion's Tunic", "Silvered Greaves"), cloak=("#9a2a22", "cloth", {"trim": "#d6a832"})),
    S("praetorian", "Praetorian", "Rome", "attic", "muscle", "plate", "pteruges", "bare", "greaves",
      pal(helm=MAT["gold"], chest=("#d6a832", "gold", {}), trim=MAT["silver"], plume=("#5e2a6a", "hair", {}),
          cloth=("#5e2a6a", "cloth", {}), strips=("#5e2a6a", "cloth", {"trim": "#d6a832"})),
      ("Praetorian Helm", "Gilded Cuirass", "Imperial Tunic", "Gilded Greaves"), cloak=("#5e2a6a", "cloth", {"trim": "#d6a832"})),
    S("germanic", "Germanic", "Germania", "conical_mail", "pelt", "fur", "none", "trousers", "fur_boots",
      pal(helm=MAT["iron"], fur=("#5a4632", "fur", {}), cloth3=("#4a5a3a", "cloth", {"band": ("#2a2a2e", 3)}),
          mail=("#7a7d84", "mail", {}), leather=("#4a3424", "hide", {})),
      ("Spangenhelm", "Chieftain's Pelt", "Wool Trousers", "Fur Boots"), cloak=("#5a4632", "fur", {})),
    S("qin", "Terracotta", "Qin China", "topknot", "lamellar", "lamellar_sleeve", "panels", "trousers", "boots",
      pal(lamellar=("#6a5a48", "lamellar", {"lace": "#c84a2a"}), cloth=("#3a6a3a", "cloth", {}), cloth3=("#2e4a8a", "cloth", {}),
          armor2=("#6a5a48", "lamellar", {"lace": "#c84a2a"}), trim=("#c84a2a", "cloth", {})),
      ("Topknot Cap", "Studded Lamellar", "Warrior's Trousers", "Square-Toed Shoes")),
    S("han", "Han", "Han China", "conical", "lamellar", "lamellar_sleeve", "panels", "trousers", "metal_boots",
      pal(helm=("#8a2a22", "metal", {}), trim=MAT["gold"], lamellar=("#8a2a22", "lamellar", {"lace": "#d6a832"}),
          armor2=("#8a2a22", "lamellar", {"lace": "#d6a832"}), chest=("#8a2a22", "metal", {}), cloth3=("#2a2a2e", "cloth", {}),
          plume=("#9a2a22", "hair", {})),
      ("General's Helm", "Red Lacquer Lamellar", "Battle Trousers", "Lacquered Boots")),
    S("maurya", "Mauryan", "Maurya", "turban", "scale", "none", "kilt", "wrap", "sandal",
      pal(cloth=("#e8a030", "cloth", {}), cloth2=("#9a2a22", "cloth", {}), scale=("#d6a832", "scales", {}), plume=("#2e8a5a", "feather", {}),
          wrap=("#ece8dc", "cloth", {"band": ("#d6a832", 3)})),
      ("Jeweled Turban", "Golden Scale Vest", "Dhoti", "Anklet Sandals"), bracer="gold"),
    S("sarmatian", "Sarmatian", "Sarmatia", "conical_mail", "scale", "sleeve", "scale", "scale", "metal_boots",
      pal(helm=MAT["iron"], scale=("#9aa0a8", "scales", {}), chest=MAT["iron"], mail=("#8a8d94", "mail", {})),
      ("Lancer's Helm", "Horn-Scale Coat", "Scale Leggings", "Iron Boots")),
    S("parthian", "Parthian", "Parthia", "conical_mail", "lamellar", "mail_sleeve", "panels", "mail", "metal_boots",
      pal(helm=MAT["steel"], lamellar=("#aab0b8", "lamellar", {}), armor2=("#aab0b8", "lamellar", {}), mail=("#9aa0a8", "mail", {}),
          chest=MAT["steel"]),
      ("Cataphract Helm", "Cataphract Lamellar", "Mail Chausses", "Plated Boots")),
    S("byzantine", "Byzantine", "Byzantium", "conical", "lamellar", "layered", "pteruges", "mail", "metal_boots",
      pal(helm=MAT["gold"], trim=MAT["gold"], lamellar=("#d6a832", "lamellar", {}), chest=("#d6a832", "gold", {}),
          strips=("#5e2a6a", "cloth", {"trim": "#d6a832"}), mail=("#a8aeb6", "mail", {}), plume=("#5e2a6a", "hair", {})),
      ("Kataphrakt Helm", "Gilded Klibanion", "Mail Leggings", "Imperial Boots"), cloak=("#5e2a6a", "cloth", {"trim": "#d6a832"})),
    S("mongol", "Mongol", "Mongolia", "furhat", "lamellar", "lamellar_sleeve", "panels", "trousers", "fur_boots",
      pal(helm=MAT["iron"], fur=("#6a4a2c", "fur", {}), lamellar=("#4e5058", "lamellar", {"lace": "#2e4a8a"}),
          armor2=("#4e5058", "lamellar", {"lace": "#2e4a8a"}), cloth3=("#2e4a8a", "cloth", {}), plume=("#9a2a22", "hair", {})),
      ("Keshig Helm", "Iron Lamellar Deel", "Riding Trousers", "Felt Boots")),
    S("maya", "Maya", "Maya", "jaguar", "quilted", "fur", "kilt", "wrap", "sandal",
      pal(pelt=("#c89a40", "fur", {"studs": ("#2a1c10", 2)}), fur=("#c89a40", "fur", {"studs": ("#2a1c10", 2)}),
          cloth=("#ece8dc", "cloth", {"band": ("#3a8a6a", 3)}), cloth2=("#3a8a6a", "cloth", {}), accent=("#2a1c10", "plain", {}),
          wrap=("#ece8dc", "cloth", {"band": ("#3a8a6a", 3)}), trim=("#3a8a6a", "cloth", {})),
      ("Jaguar Helm", "Quilted Cotton Armor", "Jaguar Loincloth", "Jade Sandals"), cloak=("#3a8a6a", "feather", {})),
    S("aztec", "Aztec", "Mexica", "eagle", "quilted", "none", "kilt", "wrap", "sandal",
      pal(feather=("#6a4a2c", "feather", {}), cloth=("#ece8dc", "cloth", {"studs": ("#c8501e", 2)}), cloth2=("#2e8a8a", "cloth", {}),
          accent=("#e8c040", "plain", {}), wrap=("#ece8dc", "cloth", {"band": ("#2e8a8a", 3)}), trim=("#2e8a8a", "cloth", {})),
      ("Eagle Warrior Helm", "Ichcahuipilli", "Feathered Loincloth", "Warrior Sandals"), bracer="gold", cloak=("#2e8a8a", "feather", {})),
    S("inca", "Inca", "Tawantinsuyu", "sun", "quilted", "plate", "kilt", "wrap", "sandal",
      pal(cloth=("#9a2a22", "cloth", {"band": ("#d6a832", 3)}), cloth2=("#2a2a2e", "cloth", {}), chest=MAT["gold"], accent=("#c8501e", "plain", {}),
          plume=("#e8c040", "feather", {}), plume2=("#9a2a22", "feather", {}), wrap=("#9a2a22", "cloth", {"band": ("#d6a832", 3)}),
          trim=MAT["gold"]),
      ("Sun Crown", "Qhapaq Tunic", "Royal Loincloth", "Gold-Bound Sandals"), bracer="gold"),
    S("samurai", "Samurai", "Japan", "kabuto", "oyoroi", "sode", "panels", "haidate", "lacquer_greaves",
      pal(helm=("#2a2a2e", "metal", {}), armor2=("#2a2a2e", "lamellar", {"lace": "#c8282a"}), lamellar=("#2a2a2e", "lamellar", {"lace": "#c8282a"}),
          trim=MAT["gold"], accent=("#3a2a24", "plain", {}), cloth3=("#2e3a6a", "cloth", {})),
      ("Kabuto", "O-Yoroi", "Haidate", "Suneate")),
    S("pharaoh", "Pharaoh", "Egypt", "khepresh", "robe", "plate", "kilt", "bare", "sandal",
      pal(helm=("#2e4a8a", "metal", {"studs": ("#d6a832", 2)}), cloth=("#ece8dc", "cloth", {}), cloth2=MAT["gold"],
          scale=("#d6a832", "scales", {"band": ("#2e4a8a", 3)}), chest=MAT["gold"], trim=MAT["gold"], accent=("#3a8aa8", "plain", {})),
      ("Blue War Crown", "Royal Broad Collar", "Golden Shendyt", "Pharaoh's Sandals"), bracer="gold", cloak=("#2e4a8a", "cloth", {"band": ("#d6a832", 4)})),
    S("akkadian", "Akkadian", "Akkad", "akkad", "leather", "none", "kilt", "bare", "sandal",
      pal(helm=MAT["copper"], trim=MAT["copper"], leather=("#5a4030", "hide", {"studs": ("#b8693e", 2)}),
          cloth=("#d8c8a0", "cloth", {"band": ("#6a4a2c", 2)}), cloth2=MAT["linen"]),
      ("Sargon's Helm", "Studded Leather Coat", "Fleece Kilt", "Sandals")),
    S("shang", "Shang", "Shang China", "shang", "lamellar", "none", "panels", "trousers", "boots",
      pal(helm=("#8a7a4a", "metal", {}), trim=("#6a8a6a", "metal", {}), accent=("#c84a2a", "plain", {}),
          lamellar=("#6a4a30", "lamellar", {"lace": "#c84a2a"}), armor2=("#6a4a30", "lamellar", {}), cloth=("#c84a2a", "cloth", {}),
          cloth3=("#3a3a3a", "cloth", {}), plume=("#c84a2a", "hair", {})),
      ("Taotie Helm", "Hide Lamellar", "Bronze-Age Trousers", "Hide Boots")),
    S("phoenician", "Phoenician", "Phoenicia", "conical", "scale", "sleeve", "kilt", "bare", "sandal",
      pal(helm=MAT["bronze"], scale=("#b07a3a", "scales", {}), cloth=("#5e2a6a", "cloth", {"band": ("#d6a832", 4)}),
          cloth2=("#5e2a6a", "cloth", {}), sleeve=("#5e2a6a", "cloth", {})),
      ("Sea-Trader's Helm", "Tyrian Scale Coat", "Purple Kilt", "Sailor's Sandals")),
    S("olmec", "Olmec", "Olmec", "olmec", "quilted", "none", "kilt", "wrap", "sandal",
      pal(helm=("#6a7a5a", "hide", {}), trim=("#3a8a6a", "bone", {}), accent=("#3a8a6a", "plain", {}),
          cloth=("#c8b88a", "cloth", {"band": ("#3a8a6a", 3)}), cloth2=("#3a8a6a", "cloth", {}),
          wrap=("#c8b88a", "cloth", {"band": ("#6a7a5a", 2)})),
      ("Colossal Head Cap", "Jade-Stitched Tunic", "Loincloth", "Jungle Sandals"), bracer="trim"),
    S("etruscan", "Etruscan", "Etruria", "negau", "muscle", "none", "pteruges", "bare", "greaves",
      pal(chest=("#c08a40", "metal", {}), cloth=("#2a2a2e", "cloth", {"band": ("#c84a2a", 3)}), strips=("#2a2a2e", "hide", {}),
          plume=("#c84a2a", "hair", {})),
      ("Negau Helmet", "Bell Cuirass", "Tebenna", "Bronze Greaves")),
    S("illyrian", "Illyrian", "Illyria", "illyrian", "muscle", "none", "pteruges", "bare", "greaves",
      pal(cloth=("#ece8dc", "cloth", {"band": ("#2e4a8a", 4)}), plume=("#2e4a8a", "hair", {}), strips=("#5a3a24", "hide", {})),
      ("Illyrian Helmet", "Bronze Bell Cuirass", "Pleated Tunic", "Greaves")),
    S("iberian", "Iberian", "Iberia", "iberian", "leather", "none", "kilt", "bare", "boots",
      pal(leather=("#5a3a24", "hide", {"studs": ("#c8ccd2", 2)}), cloth=("#ece8dc", "cloth", {"band": ("#9a2a22", 3)}),
          cloth2=("#9a2a22", "cloth", {}), plume=("#9a2a22", "hair", {}), trim=MAT["silver"]),
      ("Sinew Helm", "Disc-Plate Harness", "Falcata Tunic", "Hill Boots")),
    S("argyraspid", "Silver Shield", "Seleucia", "attic", "muscle", "plate", "pteruges", "bare", "greaves",
      pal(helm=MAT["silver"], chest=MAT["silver"], trim=MAT["gold"], plume=("#ece8dc", "hair", {}), cloth=("#2e4a8a", "cloth", {}),
          strips=("#2e4a8a", "cloth", {"trim": "#c8ccd2"})),
      ("Argyraspid Helm", "Silvered Cuirass", "Veteran's Chiton", "Silvered Greaves"), cloak=("#2e4a8a", "cloth", {})),
    S("numidian", "Numidian", "Numidia", "hood", "leather", "none", "kilt", "bare", "sandal",
      pal(cloth=("#e8dcc0", "cloth", {}), leather=("#7a5434", "hide", {"studs": ("#d6a832", 3)}), cloth2=("#c8501e", "cloth", {}),
          sleeve=("#e8dcc0", "cloth", {})),
      ("Desert Rider's Hood", "Rider's Jerkin", "Light Kilt", "Riding Sandals")),
    S("dacian", "Dacian", "Dacia", "phrygian", "scale", "sleeve", "none", "trousers", "boots",
      pal(helm=MAT["iron"], scale=("#8a8d94", "scales", {}), cloth3=("#4a5a3a", "cloth", {"band": ("#2a2a2e", 2)}),
          leather=("#4a3424", "hide", {}), sleeve=("#4a5a3a", "cloth", {})),
      ("Wolf-Banner Helm", "Iron Scale Shirt", "Wool Trousers", "Mountain Boots")),
    S("hun", "Hunnic", "Huns", "hun", "lamellar", "fur", "panels", "trousers", "fur_boots",
      pal(helm=MAT["iron"], trim=MAT["gold"], fur=("#4a3a2a", "fur", {}), lamellar=("#5a5a62", "lamellar", {}),
          armor2=("#5a5a62", "lamellar", {}), cloth3=("#6a4a2c", "cloth", {})),
      ("Steppe Helm", "Horseman's Lamellar", "Leather Trousers", "Felt-Lined Boots")),
    S("goguryeo", "Goguryeo", "Goguryeo", "goguryeo", "lamellar", "lamellar_sleeve", "panels", "haidate", "metal_boots",
      pal(lamellar=("#6a6e78", "lamellar", {"lace": "#2e8a8a"}), armor2=("#6a6e78", "lamellar", {"lace": "#2e8a8a"}),
          trim=("#2e8a8a", "cloth", {}), plume=("#c84a2a", "hair", {}), cloth3=("#2a2a2e", "cloth", {}), chest=MAT["steel"]),
      ("Plumed Lamellar Helm", "Cavalry Lamellar", "Lamellar Thigh Guards", "Iron Boots")),
    S("aksumite", "Aksumite", "Aksum", "feathers", "scale", "plate", "kilt", "bare", "sandal",
      pal(scale=("#d6a832", "scales", {}), chest=MAT["gold"], plume=("#c89a40", "fur", {}), plume2=("#2a2a2e", "feather", {}),
          cloth=("#ece8dc", "cloth", {"band": ("#d6a832", 4)}), cloth2=("#9a2a22", "cloth", {})),
      ("Lion's Mane Crown", "Golden Scale Coat", "Royal Kilt", "Highland Sandals"), bracer="gold", cloak=("#c89a40", "fur", {})),
    S("anglo_saxon", "Anglo-Saxon", "Wessex", "suttonhoo", "mail", "plate", "none", "trousers", "boots",
      pal(helm=MAT["iron"], trim=MAT["gold"], chest=MAT["iron"], mail=("#8a8d94", "mail", {}), cloth3=("#6a4a2c", "cloth", {}),
          sleeve=("#8a8d94", "mail", {})),
      ("Sutton Hoo Helm", "Thegn's Byrnie", "Wool Leggings", "Leather Turnshoes"), cloak=("#2e4a8a", "cloth", {"trim": "#d6a832"})),
    S("khmer", "Khmer", "Angkor", "mokot", "robe", "plate", "kilt", "bare", "sandal",
      pal(gold=MAT["gold"], accent=("#c84a2a", "plain", {}), cloth=("#c84a2a", "cloth", {"band": ("#d6a832", 3)}),
          cloth2=("#d6a832", "cloth", {}), scale=("#d6a832", "scales", {}), chest=MAT["gold"], trim=MAT["gold"]),
      ("Mokot Crown", "Temple Guard Collar", "Sampot", "Temple Sandals"), bracer="gold"),
]


ORDER = ["sumerian", "akkadian", "egyptian", "minoan", "shang", "nubian", "hittite", "phoenician", "mycenaean", "olmec",
         "assyrian", "babylonian", "etruscan", "celtic", "illyrian", "thracian", "iberian", "athenian", "spartan",
         "macedonian", "argyraspid", "scythian", "persian", "carthaginian", "numidian", "dacian", "roman", "gladiator",
         "centurion", "praetorian", "germanic", "hun", "qin", "han", "goguryeo", "maurya", "aksumite", "sarmatian",
         "parthian", "anglo_saxon", "byzantine", "khmer", "mongol", "maya", "aztec", "inca", "samurai", "pharaoh"]
_by = {x["id"]: x for x in SETS}
assert sorted(ORDER) == sorted(_by), set(ORDER) ^ set(_by)
SETS = [_by[k] for k in ORDER]


# ================================================================== the King of Mycenae (legendary set, also a glamour look)
# Original design built from real Mycenaean finds: the gold funerary "Mask of Agamemnon", the Lion Gate,
# the Dendra panoply and boar-tusk helmets. Not based on any film costume.
def h_wanax(m, P):
    h_cap(m, P, low=28.0)
    box(m, H, -4.9, 27.6, -4.9, 4.9, 28.6, 4.9, P["gold"])                 # gold rim
    for y in (29.4, 31.0):                                                  # rows of boar tusks round the bowl
        box(m, H, -4.75, y, -4.75, 4.75, y + 0.9, 4.75, P["tusk"])
    box(m, H, -4.7, 24.2, -3.4, 4.7, 28.0, 4.7, P["helm"])                 # cheeks and neck
    box(m, H, -5.2, 24.4, 4.2, 5.2, 25.6, 6.0, P["helm"])                  # flared neck guard
    # the gold death mask: eye slits, straight nose, beard
    box(m, H, -4.3, 24.0, -5.05, 4.3, 27.2, -4.6, P["mask"])
    m.sym(H, (-4.3, 27.2, -5.05), (-2.9, 28.6, -4.6), P["mask"])
    box(m, H, -1.0, 27.2, -5.05, 1.0, 28.6, -4.6, P["mask"])
    box(m, H, -0.6, 26.4, -5.5, 0.6, 28.8, -5.0, P["mask"])                # nose
    m.sym(H, (-3.6, 28.6, -5.25), (-0.8, 29.2, -4.85), P["gold_dark"])     # brows
    box(m, H, -3.4, 24.0, -5.25, 3.4, 25.0, -4.9, P["gold_dark"])          # beard edge
    box(m, H, -1.1, 29.4, -5.3, 1.1, 31.4, -4.8, P["gold"])                # lion emblem on the brow
    m.sym(H, (-5.5, 28.8, -1.5), (-4.7, 33.6, 2.6), P["gold"])             # side plumes holders
    m.sym(H, (-5.4, 33.6, -0.6), (-4.8, 37.4, 1.4), P["plume"], rot=(0, 0, -12), pivot=(-5.1, 33.6, 0.4))
    # the great crest: on a gold stand, sweeping back and down
    box(m, H, -0.5, 32.4, -1.5, 0.5, 35.4, 1.5, P["gold"])
    box(m, H, -0.9, 35.4, -5.0, 0.9, 39.6, 5.4, P["plume"])
    box(m, H, -0.9, 31.4, 5.2, 0.9, 39.0, 7.2, P["plume"])
    box(m, H, -0.9, 26.0, 6.2, 0.9, 31.6, 7.8, P["plume"])


def c_royal(m, P):
    torso(m, P, "bands", w=5.2, d=3.2)
    box(m, B, -4.9, 23.8, -3.4, 4.9, 26.2, 3.4, P["chest"])                # Dendra collar
    box(m, B, -3.8, 17.2, -3.55, 3.8, 23.6, -3.1, P["gold"])               # gold breastplate
    m.sym(B, (-3.6, 19.6, -3.75), (-0.6, 22.6, -3.45), P["gold"])          # two lions facing (the Lion Gate)
    box(m, B, -0.5, 18.0, -3.8, 0.5, 23.2, -3.45, P["crimson"])            # the column between them
    box(m, B, -1.4, 13.6, -3.65, 1.4, 16.2, -3.15, P["crimson"])           # rosette
    box(m, B, -5.3, 11.8, -3.4, 5.3, 13.4, 3.4, P["gold"])                 # belt


def s_lion(m, P):
    for bone, s_, xi, xo in arms(None):
        lo, hi = sorted((xi + s_ * -0.4, xo + s_ * 1.3))
        box(m, bone, lo, 20.0, -3.2, hi, 25.2, 3.2, P["chest"])            # great shoulder bell
        lo, hi = sorted((xi + s_ * -0.4, xo + s_ * 1.5))
        box(m, bone, lo, 24.6, -3.3, hi, 25.6, 3.3, P["gold"])
        lo, hi = sorted((xo + s_ * 1.2, xo + s_ * 2.3))
        box(m, bone, lo, 20.6, -1.8, hi, 24.2, 1.8, P["mane"])             # lion's mane
        lo, hi = sorted((xo + s_ * 2.2, xo + s_ * 2.8))
        box(m, bone, lo, 21.2, -1.1, hi, 23.6, 1.1, P["gold"])             # lion's face
        lo, hi = sorted((xi + s_ * -0.2, xo + s_ * 0.9))
        box(m, bone, lo, 17.4, -3.0, hi, 20.2, 3.0, P["chest"])            # second lame
        lo, hi = sorted((xi, xo + s_ * 0.7))
        box(m, bone, lo, 11.8, -2.75, hi, 15.6, 2.75, P["chest"])          # vambrace
        box(m, bone, lo, 15.2, -2.85, hi, 15.8, 2.85, P["gold"])


def royal_skirt(m, P):
    box(m, B, -5.3, 8.0, -3.4, 5.3, 12.0, 3.4, P["bands"])                 # Dendra hip plates
    box(m, B, -1.6, 6.0, -3.6, 1.6, 12.0, -3.3, P["crimson"])              # front tabard
    box(m, B, -1.6, 5.6, -3.7, 1.6, 6.4, -3.4, P["gold"])


def f_royal(m, P):
    f_greaves(m, P, "chest")
    for leg, boot, s_, x0, x1 in legs():
        box(m, boot, x0 - 0.55, 6.4, -3.0, x1 + 0.55, 8.0, -1.6, P["gold"])   # gold knee caps
        box(m, boot, x0 + 1.0, 4.4, -2.95, x1 - 1.0, 6.2, -2.7, P["gold"])     # lion mask on the shin


HELMETS["wanax"] = h_wanax
CHESTS["royal"] = c_royal
SHOULDERS["lion"] = s_lion
FEET["royal"] = f_royal
LEGS["royal"] = lambda m, P: l_thighguard(m, P, "bands")

SETS.append(S("agamemnon", "Agamemnon's", "Mycenae (legendary)", "wanax", "royal", "lion", "none", "royal", "royal",
              pal(helm=("#7a4e2a", "metal", {}), chest=("#8a5a30", "metal", {}), trim=("#e0b040", "gold", {}),
                  gold=("#e8b83a", "gold", {}), gold_dark=("#a8782a", "gold", {}), mask=("#ecc04a", "gold", {"band": ("#c89a30", 2, 1)}),
                  bands=("#8a5a30", "metal", {"band": ("#e0b040", 3)}), plume=("#8a1418", "hair", {}), crimson=("#8a1418", "cloth", {}),
                  mane=("#a8702a", "fur", {}), tusk=("#e8dcb8", "bone", {"band": ("#8a6a3a", 2)}), cloth=("#8a1418", "cloth", {}),
                  sleeve=("#8a1418", "cloth", {}), cloth3=("#5a1218", "cloth", {}), wrap=("#5a1218", "cloth", {}),
                  belt=("#e8b83a", "gold", {})),
              ("Golden Mask Helm", "Lion Gate Cuirass", "King's Thigh Guards", "Lion Greaves"),
              belt_mat="belt", cloak=("#5e1a2a", "cloth", {"trim": "#e8b83a", "band": ("#e8b83a", 6, 3)})))


# ================================================================== build
def build(spec):
    m = Model(spec["id"], tex_w=256, seed=sum(map(ord, spec["id"])))
    skeleton(m)
    P = {}
    for role, (col, style, extra) in spec["P"].items():
        name = role
        m.material(name, col, style, **extra)
        P[role] = name
    HELMETS[spec["helmet"]](m, P)
    CHESTS[spec["chest"]](m, P)
    sleeves(m, P)
    SHOULDERS[spec["shoulders"]](m, P)
    if spec["skirt"] != "none":
        skirt(m, P, spec["skirt"])
    if spec["id"] == "agamemnon":
        royal_skirt(m, P)
    belt(m, P, spec["belt"])
    if spec["cloak"]:
        cape(m, P)
    if spec["bracer"]:
        bracers(m, P, spec["bracer"])
    LEGS[spec["legs"]](m, P)
    FEET[spec["feet"]](m, P)
    m.save(GEO_DIR, TEX_DIR, quiet=True)
    return m


# ---------------- inventory icons (16x16, drawn in the set's own colours)
def _c(spec, role):
    return hexrgb(spec["P"][role][0])


def icons(spec):
    out = {}
    helm, trim, chest = _c(spec, "helm"), _c(spec, "trim"), _c(spec, "chest")
    hk = spec["helmet"]
    if hk in ("nemes", "hood", "turban", "topknot"):
        helm = _c(spec, "cloth2" if hk == "nemes" else "cloth")
    elif hk in ("eagle",):
        helm = _c(spec, "feather")
    elif hk in ("jaguar",):
        helm = _c(spec, "pelt")
    elif hk in ("wanax",):
        helm = _c(spec, "gold")
    elif hk in ("boar",):
        helm = _c(spec, "tusk")
    elif hk in ("feathers", "sun", "mokot"):
        helm = _c(spec, "gold")
    ck = spec["chest"]
    body = {"linothorax": "cloth", "scale": "scale", "lamellar": "lamellar", "segmentata": "chest", "mail": "mail",
            "leather": "leather", "dendra": "chest", "quilted": "cloth", "oyoroi": "lamellar", "pelt": "fur",
            "robe": "cloth", "muscle": "chest", "royal": "gold"}[ck]
    body_c = _c(spec, body)
    legs_c = _c(spec, {"trousers": "cloth3", "haidate": "lamellar", "wrap": "wrap", "scale": "scale", "mail": "mail",
                       "thighguard": "chest", "bare": "cloth", "royal": "bands"}[spec["legs"]])
    feet_c = _c(spec, {"sandal": "leather", "greaves": "chest", "boots": "leather", "fur_boots": "fur", "metal_boots": "chest",
                       "upturned": "leather", "wrapped": "wrap", "lacquer_greaves": "armor2", "royal": "chest"}[spec["feet"]])

    def img(rows, colors):
        a = np.zeros((16, 16, 4), np.uint8)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == ".":
                    continue
                c = colors[ch]
                f = 1.0
                if ch.isupper():
                    f = 0.72
                n = ((x * 7 + y * 13) % 5) / 40
                a[y, x, :3] = np.clip(np.array(c, float) * (f + n - 0.05), 0, 255)
                a[y, x, 3] = 255
        # dark outline
        m = a[..., 3] > 0
        o = np.zeros_like(m)
        o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
        o &= ~m
        a[o] = (28, 22, 20, 255)
        return a

    H_ROWS = {
        "default": ["................", "................", ".....tttttt.....", "....hhhhhhhh....", "...hhhhhhhhhh...",
                    "...hhhhhhhhhh...", "...hhhhhhhhhh...", "...tttttttttt...", "...hh......hh...", "...hh......hh...",
                    "...HH......HH...", "................", "................", "................", "................", "................"],
        "crest": ["......pppp......", ".....pppppp.....", "....pphhhhpp....", "....hhhhhhhh....", "...hhhhhhhhhh...",
                  "...hhhhhhhhhh...", "...hhhhhhhhhh...", "...tttttttttt...", "...hhh.hh.hhh...", "...hhh.hh.hhh...",
                  "...HHH.HH.HHH...", "....HH....HH....", "................", "................", "................", "................"],
        "cone": [".......tt.......", "......hhhh......", ".....hhhhhh.....", "....hhhhhhhh....", "...hhhhhhhhhh...",
                 "...hhhhhhhhhh...", "...hhhhhhhhhh...", "...tttttttttt...", "...hh..tt..hh...", "...hh..tt..hh...",
                 "...HH..TT..HH...", "................", "................", "................", "................", "................"],
        "horn": ["................", ".pp..........pp.", ".pp..........pp.", "..pp.tttttt.pp..", "...phhhhhhhhp...",
                 "...hhhhhhhhhh...", "...hhhhhhhhhh...", "...tttttttttt...", "...hh......hh...", "...hh......hh...",
                 "...HH......HH...", "................", "................", "................", "................", "................"],
        "plumes": ["..p.q.p.q.p.q...", "..p.q.p.q.p.q...", "..pqpqpqpqpqp...", "..pqpqpqpqpqp...", "...pqpqpqpqp....",
                   "...tttttttttt...", "...tttttttttt...", "...hh......hh...", "...hh......hh...", "................",
                   "................", "................", "................", "................", "................", "................"],
        "cloth": ["................", "................", ".....hhhhhh.....", "....hhhhhhhh....", "...hhhhhhhhhh...",
                  "...hhhhhhhhhh...", "...tttttttttt...", "...hh......hh...", "...hh......hh...", "...hh......hh...",
                  "...HH......HH...", "...HH......HH...", "................", "................", "................", "................"],
    }
    hrow = {"corinthian": "crest", "attic": "crest", "galea_crest": "crest", "galea_transverse": "crest", "murmillo": "crest",
            "conical": "cone", "conical_mail": "cone", "furhat": "cone", "khepresh": "cone", "horned": "horn",
            "horned_side": "horn", "feathers": "plumes", "sun": "plumes", "nemes": "cloth", "hood": "cloth",
            "turban": "cloth", "kabuto": "horn", "montefortino": "crest", "illyrian": "crest", "iberian": "crest",
            "shang": "crest", "wanax": "crest", "goguryeo": "cone", "mokot": "cone", "hun": "cone", "suttonhoo": "default"}.get(hk, "default")
    plume = _c(spec, "horn") if hrow == "horn" and hk.startswith("horned") else (_c(spec, "gold") if hk == "kabuto" else _c(spec, "plume"))
    out["helmet"] = img(H_ROWS[hrow], {"h": helm, "H": helm, "t": trim, "T": trim, "p": plume, "q": _c(spec, "plume2")})
    out["chestplate"] = img(["................", "..ttt......ttt..", ".tbbbtttttttbbbt", ".bbbbbbbbbbbbbbb".replace("b", "b"),
                             ".bbbbbbbbbbbbbbb", "..bbbbbbbbbbbbb.", "...bbbbbbbbbb...", "...bbbbbbbbbb...", "...bbbbbbbbbb...",
                             "...bbbbbbbbbb...", "...gggggggggg...", "...BBBBBBBBBB...", "...BBBBBBBBBB...", "................",
                             "................", "................"],
                            {"b": body_c, "B": body_c, "t": trim, "g": _c(spec, spec["belt"] if spec["belt"] in spec["P"] else "belt")})
    out["leggings"] = img(["................", "...gggggggggg...", "...llllllllll...", "...llllllllll...", "...lllll.llll...",
                           "...llll..llll...", "...llll..llll...", "...llll..llll...", "...llll..llll...", "...llll..llll...",
                           "...LLLL..LLLL...", "...LLLL..LLLL...", "................", "................", "................", "................"],
                          {"l": legs_c, "L": legs_c, "g": _c(spec, "belt")})
    out["boots"] = img(["................", "................", "................", "................", "................",
                        "...ffff..ffff...", "...ffff..ffff...", "...ffff..ffff...", "...ffff..ffff...", "..fffff..fffff..",
                        "..fffff..fffff..", ".FFFFFF..FFFFFF.", "................", "................", "................", "................"],
                       {"f": feet_c, "F": feet_c})
    for k, a in out.items():
        Image.fromarray(a, "RGBA").resize((32, 32), Image.NEAREST).save(ICON_DIR / f"{spec['id']}_{k}.png")
        (MODEL_DIR / f"{spec['id']}_{k}.json").write_text(json.dumps(
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"vividlands_ragnarok:item/{spec['id']}_{k}"}}, indent=2) + "\n")


def java():
    lines = [f'            new Set("{s["id"]}", "{s["civ"]}"),' for s in SETS]
    JAVA.write_text('''package com.vividlands.ragnarok.armor;

import java.util.List;

/**
 * The ancient-civilization armor sets, weakest to strongest (generated by tools/ancient_armor.py: edit the list there).
 * A set's place in this list is its tier; stats scale linearly with it (AncientArmorMaterial).
 */
public final class AncientSets {
    public record Set(String id, String civilization) {
    }

    public static final List<Set> ALL = List.of(
''' + "\n".join(lines).rstrip(",") + '''
    );

    private AncientSets() {
    }
}
''')


def lang():
    f = ASSETS / "lang/en_us.json"
    L = json.loads(f.read_text())
    for i, s in enumerate(SETS):
        for piece, name in zip(("helmet", "chestplate", "leggings", "boots"), s["names"]):
            L[f"item.vividlands_ragnarok.{s['id']}_{piece}"] = f"{s['title']} {name}" if s["title"] not in name else name
        L[f"tooltip.vividlands_ragnarok.ancient.{s['id']}"] = f"{s['civ']} - tier {i + 1} of {len(SETS)}"
    L["itemGroup.vividlands_ragnarok.ancient"] = "Ancient Armor"
    f.write_text(json.dumps(dict(sorted(L.items())), indent=2, ensure_ascii=False) + "\n")


def main(ids):
    for s in SETS:
        if ids and s["id"] not in ids:
            continue
        build(s)
        icons(s)
        print(s["id"], end=" ", flush=True)
    print()
    if not ids:
        java()
        lang()
        print(len(SETS), "sets")


if __name__ == "__main__":
    main(sys.argv[1:])
