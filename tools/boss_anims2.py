"""
Animations for the 20-boss Chapter 1 and the 5-boss Chapter 2 (run after ch1_models.py / ch2_models.py).

    python3 tools/boss_anims2.py

- New Chapter 1 animals get rigs here (wolf/cat, quad, ape, bird, eagle, lizard, serpent).
- Chapter 2: Sleipnir and Fenrir from ch2_anims.py plus their new moves; Garmr on the hound rig; Fafnir on a
  dragon rig; the long Jormungandr on the serpent rig.
- Every boss (the first ten too) then gets the newer move animations it is missing: combo, breath, grab, spin,
  swoop, stagger (BossAnimations.MOVES), so every triggered move has something to play.
Signs: +X tips a bone's front down, -X lifts it; for wings, raising the left wing is -Z, the right wing +Z.
"""
import copy
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boss_anims as BA  # noqa: E402
import ch2_anims as C2  # noqa: E402
from boss_anims import ASSETS, anim, keys, put, wave  # noqa: E402

OUT = ASSETS / "animations/entity/boss"
NEW_MOVES = ("combo", "breath", "grab", "spin", "swoop", "stagger")


def bones_of(boss):
    geo = json.loads((ASSETS / f"geo/entity/boss/{boss}.geo.json").read_text())
    return {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}


def swing(length, amp, phase, steps=12, axis=0, offset=0.0):
    return wave(length, amp, phase=2 * math.pi * phase, steps=steps, axis=axis, offset=offset)


def flap(length, up, down, phase=0.0, steps=12, axis=2, sign=1):
    """Wing beat on one axis between `up` and `down` degrees."""
    mid, amp = (up + down) / 2, (down - up) / 2
    return swing(length, amp * sign, phase, steps, axis, offset=mid * sign)


# ------------------------------------------------------------------ shared extras
def combo_quad(B, front=("leg_fl", "leg_fr")):
    """Bite, bite, heavy forepaw slam."""
    a = anim(1.5, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.15, [-15, 10, 0]), (0.3, [18, -10, 0]), (0.45, [-15, -10, 0]),
                                    (0.6, [18, 10, 0]), (0.9, [-20, 0, 0]), (1.1, [15, 0, 0]), (1.5, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.15, [40, 0, 0]), (0.3, [0, 0, 0]), (0.45, [40, 0, 0]), (0.6, [0, 0, 0]),
                                   (1.5, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.9, [-25, 0, 0]), (1.1, [8, 0, 0]), (1.5, [0, 0, 0])), B)
    for leg in front:
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.9, [-75, 0, 0]), (1.1, [15, 0, 0]), (1.5, [0, 0, 0])), B)
    return a


def stagger(B, root="body"):
    """Reeling: wobbles, head hangs, jaw slack."""
    a = anim(3.5, False)
    put(a, root, "rotation", keys((0, [0, 0, 0]), (0.3, [8, 0, -12]), (0.9, [6, 0, 10]), (1.5, [8, 0, -8]), (2.2, [6, 0, 6]),
                                  (3.0, [4, 0, -3]), (3.5, [0, 0, 0])), B)
    put(a, root, "position", keys((0, [0, 0, 0]), (0.3, [0, -1.5, 0]), (3.0, [0, -1.5, 0]), (3.5, [0, 0, 0])), B)
    for h in ("head", "neck", "neck1"):
        put(a, h, "rotation", keys((0, [0, 0, 0]), (0.4, [28, 12, 0]), (1.4, [24, -12, 0]), (2.4, [28, 8, 0]), (3.5, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.4, [20, 0, 0]), (3.0, [20, 0, 0]), (3.5, [0, 0, 0])), B)
    return a


def fill(A, B):
    """Give a boss every move animation, deriving the ones it has no own version of."""
    A.setdefault("combo", copy.deepcopy(A.get("attack")))
    A.setdefault("breath", copy.deepcopy(A.get("roar")))
    A.setdefault("grab", copy.deepcopy(A.get("attack")))
    A.setdefault("swoop", copy.deepcopy(A.get("leap", A.get("attack"))))
    if "spin" not in A:
        a = anim(1.2, False)
        put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.6, [0, 180, 0]), (1.2, [0, 360, 0])), B)
        put(a, "head" if "body" not in B else "body", "rotation", keys((0, [0, 0, 0]), (0.6, [0, 180, 0]), (1.2, [0, 360, 0])), B)
        A["spin"] = a
    A.setdefault("stagger", stagger(B, "body" if "body" in B else "head"))
    for k in list(A):
        if A[k] is None:
            A[k] = anim(0.5, False)
    return A


# ------------------------------------------------------------------ Chapter 1: new animals
def dire_wolf(B):
    A = C2.fenrir(B)                                     # the wolf rig: howl, lunge, pounce, slam
    A["combo"] = combo_quad(B)
    return A


def cave_lion(B):
    A = C2.fenrir(B)
    lion = BA.quad(B)
    A["roar"] = lion["roar"]                             # a lion roars forward, it doesn't howl
    put(A["roar"], "jaw", "rotation", keys((0, [0, 0, 0]), (0.35, [50, 0, 0]), (1.2, [50, 0, 0]), (1.6, [0, 0, 0])), B)
    A["combo"] = combo_quad(B)
    return A


def steppe_bison(B):
    A = BA.quad(B)
    A["charge"] = copy.deepcopy(A["run"])
    put(A["charge"], "head", "rotation", keys((0, [28, 0, 0]), (0.6, [28, 0, 0])), B)      # horns down
    a = anim(1.0, False)                                 # horn toss
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.35, [35, 0, 0]), (0.55, [-40, 15, 0]), (1.0, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.35, [6, 0, 0]), (0.55, [-8, 0, 0]), (1.0, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a
    A["combo"] = combo_quad(B)
    return A


def glyptodon(B):
    A = BA.croc(B)
    a = anim(1.0, True)                                  # shell spin: legs tucked, whole body whirling
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [0, 180, 0]), (1.0, [0, 360, 0])), B)
    put(a, "body", "position", keys((0, [0, -2, 0]), (1.0, [0, -2, 0])), B)
    for leg in ("leg_fl", "leg_fr", "leg_bl", "leg_br"):
        put(a, leg, "position", keys((0, [0, 3, 0]), (1.0, [0, 3, 0])), B)
    put(a, "head", "position", keys((0, [0, 0, 2]), (1.0, [0, 0, 2])), B)
    A["spin"] = a
    a = anim(1.1, False)                                 # tail club swing
    put(a, "tail", "rotation", keys((0, [0, 0, 0]), (0.45, [0, -40, 0]), (0.62, [0, 55, 0]), (1.1, [0, 0, 0])), B)
    put(a, "tail2", "rotation", keys((0, [0, 0, 0]), (0.45, [0, -25, 0]), (0.62, [0, 40, 0]), (1.1, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.45, [0, 18, 0]), (0.62, [0, -22, 0]), (1.1, [0, 0, 0])), B)
    A["slam"] = A["combo"] = a
    return A


def walrus(B):
    A = BA.quad(B)
    a = anim(1.4, False)                                 # belly flop
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-30, 0, 0]), (0.75, [8, 0, 0]), (1.4, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.5, [0, 6, 0]), (0.75, [0, -1, 0]), (1.4, [0, 0, 0])), B)
    for leg, z in (("leg_fl", -40), ("leg_fr", 40)):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.5, [0, 0, z]), (0.75, [0, 0, -z * 0.3]), (1.4, [0, 0, 0])), B)
    A["slam"] = a
    a = anim(0.9, False)                                 # tusk stab: head rears and drives down
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.35, [-35, 0, 0]), (0.5, [35, 0, 0]), (0.9, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.35, [-8, 0, 0]), (0.5, [6, 0, 0]), (0.9, [0, 0, 0])), B)
    A["attack"] = a
    c = anim(1.8, False)
    for i in range(3):
        t0 = i * 0.55
        for b, v in (("head", [-35, 12 * (1 - i), 0]), ("body", [-8, 0, 0])):
            pass
    put(c, "head", "rotation", keys((0, [0, 0, 0]), (0.3, [-35, 15, 0]), (0.45, [35, 15, 0]), (0.85, [-35, -15, 0]),
                                    (1.0, [35, -15, 0]), (1.4, [-40, 0, 0]), (1.55, [40, 0, 0]), (1.8, [0, 0, 0])), B)
    A["combo"] = c
    for name, length in (("walk", 1.4), ("run", 0.8)):          # a walrus humps along on its flippers
        a = anim(length, True)
        put(a, "body", "position", wave(length, 1.0 if name == "run" else 0.6, axis=1, steps=12), B)
        put(a, "body", "rotation", swing(length, 6, 0.25), B)
        for leg, s in (("leg_fl", 1), ("leg_fr", -1)):
            put(a, leg, "rotation", swing(length, 25 * s, 0.0, axis=2), B)
        for leg in ("leg_bl", "leg_br"):
            put(a, leg, "rotation", swing(length, 18, 0.5), B)
        put(a, "head", "rotation", swing(length, 6, 0.6), B)
        A[name] = a
    A["charge"] = A["run"]
    return A


def ground_sloth(B):
    A = BA.ape(B)
    a = anim(1.6, False)                                 # claw combo: right, left, both
    put(a, "arm_r", "rotation", keys((0, [0, 0, 0]), (0.25, [-120, 0, -20]), (0.4, [20, 0, 10]), (0.9, [0, 0, 0]),
                                     (1.1, [-150, 0, -10]), (1.3, [15, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "arm_l", "rotation", keys((0, [0, 0, 0]), (0.5, [0, 0, 0]), (0.7, [-120, 0, 20]), (0.85, [20, 0, -10]),
                                     (1.1, [-150, 0, 10]), (1.3, [15, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.25, [-15, -15, 0]), (0.4, [10, 15, 0]), (0.7, [-15, 15, 0]),
                                     (0.85, [10, -15, 0]), (1.1, [-30, 0, 0]), (1.3, [15, 0, 0]), (1.6, [0, 0, 0])), B)
    A["combo"] = a
    a = anim(2.4, False)                                 # bear hug: rear up, arms close round you, squeeze
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.4, [-35, 0, 0]), (2.0, [-30, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "arm_l", "rotation", keys((0, [0, 0, 0]), (0.4, [-90, -30, 30]), (0.6, [-80, 30, -10]), (1.2, [-75, 35, -15]),
                                     (1.6, [-80, 30, -10]), (2.0, [-75, 35, -15]), (2.4, [0, 0, 0])), B)
    put(a, "arm_r", "rotation", keys((0, [0, 0, 0]), (0.4, [-90, 30, -30]), (0.6, [-80, -30, 10]), (1.2, [-75, -35, 15]),
                                     (1.6, [-80, -30, 10]), (2.0, [-75, -35, 15]), (2.4, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.4, [25, 0, 0]), (2.0, [25, 0, 0]), (2.4, [0, 0, 0])), B)
    A["grab"] = a
    return A


def terror_bird(B):
    A = {}
    a = anim(3.0, True)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.8, [6, 0, 0]), (1.0, [-4, 0, 0]), (2.0, [0, 0, 0]), (3.0, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [0, 20, 0]), (0.6, [0, 20, 0]), (1.4, [0, -20, 0]), (1.5, [0, -20, 0]),
                                    (2.2, [0, 0, 8]), (3.0, [0, 0, 0])), B)
    put(a, "body", "position", wave(3.0, 0.25, axis=1), B)
    A["idle"] = a
    for name, length, amp, lean in (("walk", 0.8, 30, 4), ("run", 0.45, 50, 16)):
        a = anim(length, True)
        put(a, "leg_l", "rotation", swing(length, amp, 0.0), B)
        put(a, "leg_r", "rotation", swing(length, amp, 0.5), B)
        put(a, "body", "position", wave(length, 0.6 if name == "walk" else 1.2, axis=1, steps=12, phase=0.0), B)
        put(a, "body", "rotation", keys((0, [lean, 0, 0]), (length, [lean, 0, 0])), B)
        put(a, "neck", "rotation", swing(length, 8, 0.25, offset=lean), B)
        put(a, "wing_l", "rotation", swing(length, 10, 0.0, axis=2, offset=-8 if name == "run" else 0), B)
        put(a, "wing_r", "rotation", swing(length, -10, 0.0, axis=2, offset=8 if name == "run" else 0), B)
        A[name] = a
    A["charge"] = A["run"]
    a = anim(0.6, False)                                 # peck: rear back and hammer down with the beak
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.2, [-30, 0, 0]), (0.32, [45, 0, 0]), (0.6, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.2, [-10, 0, 0]), (0.32, [25, 0, 0]), (0.6, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [35, 0, 0]), (0.3, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a
    a = anim(1.2, False)                                 # three pecks, the last one heavy
    k = [(0, [0, 0, 0])]
    for i, t in enumerate((0.1, 0.4, 0.75)):
        k += [(t, [-25 - 10 * i, 10 * (1 - i), 0]), (t + 0.12, [40 + 10 * i, -5 * (1 - i), 0])]
    k.append((1.2, [0, 0, 0]))
    put(a, "neck", "rotation", keys(*k), B)
    A["combo"] = a
    a = anim(1.4, False)                                 # screech, wings out
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.35, [-35, 0, 0]), (1.0, [-35, 0, 0]), (1.4, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.35, [45, 0, 0]), (1.0, [45, 0, 0]), (1.4, [0, 0, 0])), B)
    put(a, "wing_l", "rotation", keys((0, [0, 0, 0]), (0.35, [0, 0, -70]), (1.0, [0, 0, -60]), (1.4, [0, 0, 0])), B)
    put(a, "wing_r", "rotation", keys((0, [0, 0, 0]), (0.35, [0, 0, 70]), (1.0, [0, 0, 60]), (1.4, [0, 0, 0])), B)
    A["roar"] = a
    a = anim(1.0, False)                                 # leaping kick: the sickle claw
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.2, [0, -2, 0]), (0.5, [0, 8, 0]), (0.85, [0, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-20, 0, 0]), (0.85, [5, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "leg_l", "rotation", keys((0, [0, 0, 0]), (0.45, [-80, 0, 0]), (0.6, [-20, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "leg_r", "rotation", keys((0, [0, 0, 0]), (0.5, [-70, 0, 0]), (0.65, [-10, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "wing_l", "rotation", keys((0, [0, 0, 0]), (0.4, [0, 0, -60]), (1.0, [0, 0, 0])), B)
    put(a, "wing_r", "rotation", keys((0, [0, 0, 0]), (0.4, [0, 0, 60]), (1.0, [0, 0, 0])), B)
    A["leap"] = A["slam"] = A["roll"] = a
    a = anim(0.4, False)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.1, [-15, 15, 0]), (0.4, [0, 0, 0])), B)
    A["hurt"] = a
    return A


def haast_eagle(B):
    A = {}

    def beat(a, length, up=-35, down=30, lag=0.12):
        put(a, "wing_l", "rotation", flap(length, up, down, 0.0), B)
        put(a, "wing_r", "rotation", flap(length, up, down, 0.0, sign=-1), B)
        put(a, "wing_l2", "rotation", flap(length, up * 0.6, down * 0.6, -lag), B)
        put(a, "wing_r2", "rotation", flap(length, up * 0.6, down * 0.6, -lag, sign=-1), B)
        put(a, "body", "position", swing(length, 1.2, 0.25, axis=1), B)

    for name, length, pitch in (("idle", 1.2, 0), ("walk", 1.0, 8), ("run", 0.6, 18)):
        a = anim(length, True)
        beat(a, length)
        put(a, "body", "rotation", keys((0, [pitch, 0, 0]), (length, [pitch, 0, 0])), B)
        put(a, "tail", "rotation", swing(length, 5, 0.4), B)
        for leg in ("leg_l", "leg_r"):
            put(a, leg, "rotation", keys((0, [25 + pitch, 0, 0]), (length, [25 + pitch, 0, 0])), B)
        A[name] = a
    A["charge"] = A["run"]
    a = anim(0.7, False)                                 # talon strike
    beat(a, 0.7, -50, 20)
    for leg in ("leg_l", "leg_r"):
        put(a, leg, "rotation", keys((0, [20, 0, 0]), (0.3, [-75, 0, 0]), (0.45, [-30, 0, 0]), (0.7, [20, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.3, [-25, 0, 0]), (0.7, [0, 0, 0])), B)
    A["attack"] = A["throw"] = A["slam"] = a
    a = anim(1.6, False)                                 # swoop: wings tucked back, steep dive
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.4, [45, 0, 0]), (1.2, [45, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "wing_l", "rotation", keys((0, [0, 0, 0]), (0.4, [0, -45, -15]), (1.2, [0, -45, -15]), (1.6, [0, 0, 0])), B)
    put(a, "wing_r", "rotation", keys((0, [0, 0, 0]), (0.4, [0, 45, 15]), (1.2, [0, 45, 15]), (1.6, [0, 0, 0])), B)
    put(a, "wing_l2", "rotation", keys((0, [0, 0, 0]), (0.4, [0, -40, 0]), (1.2, [0, -40, 0]), (1.6, [0, 0, 0])), B)
    put(a, "wing_r2", "rotation", keys((0, [0, 0, 0]), (0.4, [0, 40, 0]), (1.2, [0, 40, 0]), (1.6, [0, 0, 0])), B)
    for leg in ("leg_l", "leg_r"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (1.0, [40, 0, 0]), (1.25, [-80, 0, 0]), (1.6, [0, 0, 0])), B)
    A["swoop"] = A["leap"] = a
    a = anim(1.0, True)                                  # carrying you off: heavy beats, talons clenched
    beat(a, 1.0, -55, 35)
    for leg in ("leg_l", "leg_r"):
        put(a, leg, "rotation", keys((0, [-40, 0, 0]), (1.0, [-40, 0, 0])), B)
    A["grab"] = a
    A["grab"]["loop"] = False
    a = anim(1.4, False)                                 # screech
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.3, [-30, 0, 0]), (1.0, [-30, 0, 0]), (1.4, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.3, [40, 0, 0]), (1.0, [40, 0, 0]), (1.4, [0, 0, 0])), B)
    put(a, "wing_l", "rotation", keys((0, [0, 0, 0]), (0.3, [0, 0, -50]), (1.0, [0, 0, -50]), (1.4, [0, 0, 0])), B)
    put(a, "wing_r", "rotation", keys((0, [0, 0, 0]), (0.3, [0, 0, 50]), (1.0, [0, 0, 50]), (1.4, [0, 0, 0])), B)
    A["roar"] = a
    a = anim(0.4, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.1, [-10, 0, 15]), (0.4, [0, 0, 0])), B)
    A["hurt"] = a
    A["roll"] = A["attack"]
    return A


def komodo(B):
    A = BA.croc(B)
    a = anim(1.0, False)                                 # venom bite: head snaps sideways and tears
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.25, [-15, 0, 0]), (0.4, [15, 0, 0]), (0.6, [10, 25, 0]),
                                    (0.75, [10, -25, 0]), (1.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.25, [45, 0, 0]), (0.4, [0, 0, 0]), (1.0, [0, 0, 0])), B)
    A["attack"] = A["combo"] = a
    return A


def serpent(B, amp_idle=6, strike=True):
    """Any long snake: head + seg1..segN."""
    A = {}
    segs = sorted((b for b in B if b.startswith("seg")), key=lambda s: int(s[3:]))
    n = len(segs)
    lag = 2.2 / n                                        # about two full waves along the body

    def undulate(a, length, amp):
        for i, s in enumerate(segs):
            put(a, s, "rotation", swing(length, amp * (0.6 + 0.8 * i / n), -lag * (i + 1), axis=1, steps=16), B)
        put(a, "head", "rotation", swing(length, amp * 0.5, 0.0, axis=1, steps=16), B)

    for name, length, amp in (("idle", 4.0, amp_idle), ("walk", 2.0, 11), ("run", 1.1, 15)):
        a = anim(length, True)
        undulate(a, length, amp)
        if name == "idle":
            put(a, "jaw", "rotation", wave(4.0, 3, axis=0, offset=3), B)
        A[name] = a
    A["charge"] = A["run"]
    a = anim(0.85, False)                                # coil back and strike
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.25, [-25, 0, 0]), (0.42, [18, 0, 0]), (0.85, [0, 0, 0])), B)
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.25, [0, 3, 3]), (0.42, [0, 0, -4]), (0.85, [0, 0, 0])), B)
    for s, v in zip(segs, (20, 12, 6)):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.25, [v, 0, 0]), (0.42, [-v * 0.6, 0, 0]), (0.85, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.25, [55, 0, 0]), (0.4, [55, 0, 0]), (0.47, [0, 0, 0]), (0.85, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a
    a = anim(1.6, False)                                 # double strike
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.2, [-25, 15, 0]), (0.35, [18, 15, 0]), (0.7, [-25, -15, 0]),
                                    (0.85, [18, -15, 0]), (1.6, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [50, 0, 0]), (0.36, [0, 0, 0]), (0.7, [50, 0, 0]), (0.86, [0, 0, 0]),
                                   (1.6, [0, 0, 0])), B)
    A["combo"] = a
    a = anim(2.0, False)                                 # rear up
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-55, 0, 0]), (1.0, [-50, 15, 0]), (1.4, [-50, -15, 0]), (2.0, [0, 0, 0])), B)
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.5, [0, 8, 0]), (1.6, [0, 8, 0]), (2.0, [0, 0, 0])), B)
    for s, v in zip(segs, (20, 15, 10, 5)):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.5, [v, 0, 0]), (1.6, [v, 0, 0]), (2.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [50, 0, 0]), (1.6, [50, 0, 0]), (2.0, [0, 0, 0])), B)
    A["roar"] = a
    a = copy.deepcopy(a)                                 # breath: rear, then sweep the spray side to side
    a["animation_length"] = 3.0
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-30, 0, 0]), (1.2, [-15, -28, 0]), (2.2, [-15, 28, 0]),
                                    (2.7, [-15, 0, 0]), (3.0, [0, 0, 0])), B)
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.5, [0, 6, 0]), (2.7, [0, 6, 0]), (3.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [45, 0, 0]), (2.7, [45, 0, 0]), (3.0, [0, 0, 0])), B)
    for s in segs[:4]:
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.5, [12, 0, 0]), (2.7, [12, 0, 0]), (3.0, [0, 0, 0])), B)
    A["breath"] = a
    a = anim(3.0, False)                                 # constrict: the body curls round and squeezes
    for i, s in enumerate(segs):
        c = 28 if i < n * 0.75 else 10
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.6, [0, c, 0]), (1.2, [0, c * 1.15, 0]), (1.8, [0, c, 0]),
                                   (2.4, [0, c * 1.15, 0]), (3.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.6, [35, 0, 0]), (2.4, [35, 0, 0]), (3.0, [0, 0, 0])), B)
    A["grab"] = a
    a = anim(1.5, False)                                 # tail slam
    tail = segs[n // 2:]
    for i, s in enumerate(tail):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.6, [10 + 30 / len(tail) * i, 0, 0]), (0.85, [-8 - 20 / len(tail) * i, 0, 0]),
                                   (1.1, [3, 0, 0]), (1.5, [0, 0, 0])), B)
    A["slam"] = a
    a = anim(1.6, False)                                 # leap / breach
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.6, [0, 14, 0]), (1.2, [0, 2, 0]), (1.6, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.4, [-45, 0, 0]), (0.8, [0, 0, 0]), (1.2, [40, 0, 0]), (1.6, [0, 0, 0])), B)
    for i, s in enumerate(segs):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.4 + 0.6 * i / n, [40 / n * 3, 0, 0]), (0.9 + 0.6 * i / n, [-30 / n * 3, 0, 0]),
                                   (1.6, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [40, 0, 0]), (1.0, [40, 0, 0]), (1.2, [0, 0, 0])), B)
    A["leap"] = A["swoop"] = a
    a = anim(1.6, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.8, [0, 0, 360]), (1.6, [0, 0, 720])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [35, 0, 0]), (1.4, [35, 0, 0]), (1.6, [0, 0, 0])), B)
    A["roll"] = a
    a = anim(0.45, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.12, [-10, 12, 8]), (0.45, [0, 0, 0])), B)
    A["hurt"] = a
    A["stagger"] = stagger(B, "head")
    return A


# ------------------------------------------------------------------ Chapter 2
def sleipnir(B):
    A = C2.sleipnir(B)
    a = anim(1.6, False)                                 # combo: double rear-kick, then the stomp
    for leg in ("leg_bl1", "leg_bl2", "leg_br1", "leg_br2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.35, [70, 0, 0]), (0.55, [0, 0, 0]),
                                     (0.7, [-15, 0, 0]), (0.85, [70, 0, 0]), (1.05, [0, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.35, [18, 0, 0]), (0.55, [0, 0, 0]), (0.85, [18, 0, 0]), (1.05, [0, 0, 0]),
                                    (1.25, [-30, 0, 0]), (1.4, [6, 0, 0]), (1.6, [0, 0, 0])), B)
    for leg in ("leg_fl1", "leg_fl2", "leg_fr1", "leg_fr2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (1.05, [0, 0, 0]), (1.25, [-70, 0, 0]), (1.4, [10, 0, 0]), (1.6, [0, 0, 0])), B)
    A["combo"] = a
    return A


def fenrir(B):
    A = C2.fenrir(B)
    A["combo"] = combo_quad(B)
    return A


def garmr(B):
    A = C2.fenrir(B)
    A["combo"] = combo_quad(B)
    a = anim(3.0, False)                                 # Hel's breath: head low, maw wide, sweeping
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-15, 0, 0]), (0.8, [10, -25, 0]), (2.2, [10, 25, 0]),
                                    (2.7, [10, 0, 0]), (3.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [20, 0, 0]), (0.8, [45, 0, 0]), (2.7, [45, 0, 0]), (3.0, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-6, 0, 0]), (0.8, [6, 0, 0]), (2.7, [6, 0, 0]), (3.0, [0, 0, 0])), B)
    A["breath"] = a
    return A


def fafnir(B):
    A = {}
    legs_a, legs_b = ("leg_fl", "leg_br"), ("leg_fr", "leg_bl")
    tails = [t for t in ("tail", "tail2", "tail3") if t in B]

    def wings(a, length, up, down, lag=0.1):
        put(a, "wing_l", "rotation", flap(length, up, down, 0.0), B)
        put(a, "wing_r", "rotation", flap(length, up, down, 0.0, sign=-1), B)
        put(a, "wing_l2", "rotation", flap(length, up * 0.7, down * 0.7, -lag), B)
        put(a, "wing_r2", "rotation", flap(length, up * 0.7, down * 0.7, -lag, sign=-1), B)

    for name, length, amp in (("idle", 4.0, 0), ("walk", 1.4, 20), ("run", 0.8, 34)):
        a = anim(length, True)
        if amp:
            for l in legs_a:
                put(a, l, "rotation", swing(length, amp, 0.0), B)
            for l in legs_b:
                put(a, l, "rotation", swing(length, amp, 0.5), B)
        put(a, "body", "position", wave(length, 0.3 if not amp else 0.6, axis=1, steps=12), B)
        put(a, "neck1", "rotation", swing(length, 4, 0.3), B)
        put(a, "head", "rotation", swing(length, 3, 0.5, axis=1), B)
        for i, t in enumerate(tails):
            put(a, t, "rotation", swing(length, 6 + 4 * i, -0.15 * i, axis=1), B)
        wings(a, length, -12 if name != "run" else -35, 4 if name != "run" else 20)
        A[name] = a
    A["charge"] = A["run"]
    a = anim(0.8, False)                                 # bite
    put(a, "neck1", "rotation", keys((0, [0, 0, 0]), (0.25, [-15, 0, 0]), (0.4, [20, 0, 0]), (0.8, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.25, [-10, 0, 0]), (0.4, [18, 0, 0]), (0.8, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.25, [50, 0, 0]), (0.38, [50, 0, 0]), (0.45, [0, 0, 0]), (0.8, [0, 0, 0])), B)
    A["attack"] = A["throw"] = A["grab"] = a
    a = anim(1.6, False)                                 # claw, claw, tail whip
    put(a, "leg_fl", "rotation", keys((0, [0, 0, 0]), (0.2, [-80, 0, 0]), (0.35, [10, 0, 0]), (0.6, [0, 0, 0])), B)
    put(a, "leg_fr", "rotation", keys((0, [0, 0, 0]), (0.45, [0, 0, 0]), (0.6, [-80, 0, 0]), (0.75, [10, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.2, [-10, 10, 0]), (0.6, [-10, -10, 0]), (1.0, [0, -30, 0]), (1.25, [0, 40, 0]),
                                    (1.6, [0, 0, 0])), B)
    for i, t in enumerate(tails):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (1.0, [0, -30 - 10 * i, 0]), (1.25, [0, 45 + 10 * i, 0]), (1.6, [0, 0, 0])), B)
    A["combo"] = a
    a = anim(3.2, False)                                 # fire breath: rear back, then sweep the flames
    put(a, "neck1", "rotation", keys((0, [0, 0, 0]), (0.6, [-25, 0, 0]), (0.9, [10, 0, 0]), (2.8, [10, 0, 0]), (3.2, [0, 0, 0])), B)
    put(a, "neck2", "rotation", keys((0, [0, 0, 0]), (0.6, [-15, 0, 0]), (0.9, [5, -25, 0]), (2.0, [5, 25, 0]), (2.8, [5, 0, 0]),
                                     (3.2, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.6, [-20, 0, 0]), (0.9, [10, 0, 0]), (2.8, [10, 0, 0]), (3.2, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.6, [20, 0, 0]), (0.9, [45, 0, 0]), (2.8, [45, 0, 0]), (3.2, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [4, 0, 0]), (3.2, [0, 0, 0])), B)
    wings(a, 3.2, -30, -10)
    A["breath"] = a
    a = anim(1.8, False)                                 # roar: rears, wings flung wide
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-28, 0, 0]), (1.4, [-28, 0, 0]), (1.8, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.5, [0, 4, 0]), (1.4, [0, 4, 0]), (1.8, [0, 0, 0])), B)
    for l in ("leg_fl", "leg_fr"):
        put(a, l, "rotation", keys((0, [0, 0, 0]), (0.5, [-45, 0, 0]), (1.4, [-45, 0, 0]), (1.8, [0, 0, 0])), B)
    for l in ("leg_bl", "leg_br"):
        put(a, l, "rotation", keys((0, [0, 0, 0]), (0.5, [28, 0, 0]), (1.4, [28, 0, 0]), (1.8, [0, 0, 0])), B)
    put(a, "wing_l", "rotation", keys((0, [0, 0, 0]), (0.5, [0, 0, -55]), (1.4, [0, 0, -55]), (1.8, [0, 0, 0])), B)
    put(a, "wing_r", "rotation", keys((0, [0, 0, 0]), (0.5, [0, 0, 55]), (1.4, [0, 0, 55]), (1.8, [0, 0, 0])), B)
    put(a, "neck1", "rotation", keys((0, [0, 0, 0]), (0.5, [-15, 0, 0]), (1.4, [-15, 0, 0]), (1.8, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [50, 0, 0]), (1.4, [50, 0, 0]), (1.8, [0, 0, 0])), B)
    A["roar"] = a
    a = anim(1.3, False)                                 # slam: rear and crash down
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-40, 0, 0]), (0.75, [10, 0, 0]), (1.3, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.5, [0, 6, 0]), (0.75, [0, -1, 0]), (1.3, [0, 0, 0])), B)
    for l in ("leg_fl", "leg_fr"):
        put(a, l, "rotation", keys((0, [0, 0, 0]), (0.5, [-70, 0, 0]), (0.75, [15, 0, 0]), (1.3, [0, 0, 0])), B)
    wings(a, 1.3, -50, 30)
    A["slam"] = a
    a = anim(1.5, False)                                 # leap: a wing-assisted bound
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.25, [0, -2, 0]), (0.7, [0, 14, 0]), (1.2, [0, 0, 0]), (1.5, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.25, [6, 0, 0]), (0.5, [-15, 0, 0]), (1.0, [10, 0, 0]), (1.5, [0, 0, 0])), B)
    wings(a, 0.5, -60, 40)
    for l in ("leg_fl", "leg_fr", "leg_bl", "leg_br"):
        put(a, l, "rotation", keys((0, [0, 0, 0]), (0.5, [-40 if "f" in l[4] else 40, 0, 0]), (1.2, [0, 0, 0]), (1.5, [0, 0, 0])), B)
    A["leap"] = A["swoop"] = a
    a = anim(1.2, False)                                 # tail sweep spin
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.3, [0, -30, 0]), (0.9, [0, 330, 0]), (1.2, [0, 360, 0])), B)
    for i, t in enumerate(tails):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (0.3, [0, 20, 0]), (0.9, [0, -25, 0]), (1.2, [0, 0, 0])), B)
    A["spin"] = A["roll"] = a
    a = anim(0.45, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.12, [-6, 0, 8]), (0.45, [0, 0, 0])), B)
    put(a, "neck1", "rotation", keys((0, [0, 0, 0]), (0.12, [-15, 15, 0]), (0.45, [0, 0, 0])), B)
    A["hurt"] = a
    return A


RIGS = {
    "dire_wolf": dire_wolf, "cave_lion": cave_lion, "steppe_bison": steppe_bison, "ground_sloth": ground_sloth,
    "glyptodon": glyptodon, "terror_bird": terror_bird, "haast_eagle": haast_eagle, "komodo": komodo,
    "anaconda": lambda B: serpent(B, 5), "walrus": walrus,
    "sleipnir": sleipnir, "garmr": garmr, "fafnir": fafnir, "jormungandr": lambda B: serpent(B, 5), "fenrir": fenrir,
}


def write(boss, A):
    data = {"format_version": "1.8.0", "animations": {f"animation.boss.{k}": v for k, v in A.items()}}
    (OUT / f"{boss}.animation.json").write_text(json.dumps(data, indent=1))


def main():
    for boss, fn in RIGS.items():
        B = bones_of(boss)
        write(boss, fill(fn(B), B))
        print(boss)
    # the first ten Chapter 1 bosses: keep their animations, add the newer moves
    for boss, rig in BA.RIGS.items():
        B = bones_of(boss)
        A = {"quad": BA.quad, "croc": BA.croc, "ape": BA.ape, "shark": BA.shark}[rig](B)
        if rig == "quad":
            A["combo"] = combo_quad(B)
        write(boss, fill(A, B))
        print(boss, "(filled)")


if __name__ == "__main__":
    main()
