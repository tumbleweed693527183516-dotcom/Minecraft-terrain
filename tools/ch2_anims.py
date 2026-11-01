"""
Hand-made animations for the Chapter 2 bosses (same animation names as every boss, see boss_anims.py):
idle, walk, run (loops) and attack, roar, slam, charge, leap, roll, throw, hurt.

    python3 tools/ch2_anims.py

Sign conventions (checked in the preview and in game): +X rotation tips a bone's front down (a head nods down,
a leg swings back); -X lifts the front (rearing up, a leg swinging forward). Y turns left/right.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boss_anims import ASSETS, anim, keys, put, wave  # noqa: E402


def bones_of(boss):
    geo = json.loads((ASSETS / f"geo/entity/boss/{boss}.geo.json").read_text())
    return {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}


def swing(length, amp, phase, steps=12, axis=0, offset=0.0):
    """wave() with the phase given as a fraction of the cycle."""
    return wave(length, amp, phase=2 * math.pi * phase, steps=steps, axis=axis, offset=offset)


# ------------------------------------------------------------------ Sleipnir
def sleipnir(B):
    A = {}
    legs = {"leg_fl1": 0.0, "leg_fl2": 0.12, "leg_fr1": 0.5, "leg_fr2": 0.62,
            "leg_bl1": 0.25, "leg_bl2": 0.37, "leg_br1": 0.75, "leg_br2": 0.87}

    a = anim(4.0, True)                                     # idle: tail swish, head toss, paws the ground
    put(a, "body", "position", wave(4.0, 0.2, axis=1), B)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (1.5, [6, 0, 0]), (2.2, [-6, 6, 0]), (3.0, [0, -4, 0]), (4.0, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (2.2, [-8, 0, 0]), (2.5, [4, 0, 0]), (4.0, [0, 0, 0])), B)
    put(a, "tail", "rotation", wave(4.0, 14, axis=1, steps=12), B)
    put(a, "leg_fl1", "rotation", keys((0, [0, 0, 0]), (2.6, [0, 0, 0]), (2.85, [-35, 0, 0]), (3.1, [5, 0, 0]),
                                       (3.35, [-30, 0, 0]), (3.6, [0, 0, 0]), (4.0, [0, 0, 0])), B)
    A["idle"] = a

    for name, length, amp, bob, neck in (("walk", 1.2, 22, 0.3, 4), ("run", 0.6, 42, 0.9, 8)):
        a = anim(length, True)
        for leg, ph in legs.items():
            if name == "run":                               # gallop: fronts together, backs together
                ph = {"f": 0.0, "b": 0.5}[leg[4]] + (0.08 if leg.endswith("2") else 0) + (0.04 if "r" in leg[5] else 0)
            put(a, leg, "rotation", swing(length, amp, ph), B)
        put(a, "body", "position", wave(length, bob, axis=1, steps=12, phase=0.0) if name == "walk"
            else wave(length, bob, axis=1, steps=12), B)
        put(a, "body", "rotation", swing(length, 2 if name == "walk" else 5, 0.25), B)
        put(a, "neck", "rotation", swing(length, neck, 0.6, offset=8 if name == "run" else 0), B)
        put(a, "tail", "rotation", keys((0, [25 if name == "run" else 8, 0, 0]), (length, [25 if name == "run" else 8, 0, 0])), B)
        A[name] = a
    A["charge"] = json.loads(json.dumps(A["run"]))
    put(A["charge"], "neck", "rotation", swing(0.6, 6, 0.6, offset=22), B)       # head down, charging

    a = anim(0.9, False)                                    # attack: rear and stomp with both front pairs
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.3, [-28, 0, 0]), (0.5, [-30, 0, 0]), (0.62, [6, 0, 0]), (0.9, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.3, [0, 3, 0]), (0.62, [0, 0, 0]), (0.9, [0, 0, 0])), B)
    for leg in ("leg_fl1", "leg_fl2", "leg_fr1", "leg_fr2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.3, [-70, 0, 0]), (0.5, [-50, 0, 0]), (0.62, [10, 0, 0]), (0.9, [0, 0, 0])), B)
    for leg in ("leg_bl1", "leg_bl2", "leg_br1", "leg_br2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.3, [28, 0, 0]), (0.62, [-6, 0, 0]), (0.9, [0, 0, 0])), B)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.3, [-10, 0, 0]), (0.62, [15, 0, 0]), (0.9, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a

    a = anim(1.6, False)                                    # roar: rears high and neighs, hooves pawing the air
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.4, [-42, 0, 0]), (1.2, [-42, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.4, [0, 5, 0]), (1.2, [0, 5, 0]), (1.6, [0, 0, 0])), B)
    for i, leg in enumerate(("leg_fl1", "leg_fr1", "leg_fl2", "leg_fr2")):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.4, [-60, 0, 0]), (0.6 + 0.1 * i, [-20, 0, 0]),
                                     (0.85 + 0.1 * i, [-70, 0, 0]), (1.1, [-40, 0, 0]), (1.6, [0, 0, 0])), B)
    for leg in ("leg_bl1", "leg_bl2", "leg_br1", "leg_br2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.4, [40, 0, 0]), (1.2, [40, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.4, [-15, 0, 0]), (0.8, [-5, 10, 0]), (1.2, [-15, -10, 0]), (1.6, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.45, [30, 0, 0]), (1.15, [30, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "tail", "rotation", keys((0, [0, 0, 0]), (0.4, [40, 0, 0]), (1.6, [0, 0, 0])), B)
    A["roar"] = a

    a = anim(1.3, False)                                    # slam: rears up then crashes down (thunder hooves)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-48, 0, 0]), (0.75, [8, 0, 0]), (1.0, [4, 0, 0]), (1.3, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.5, [0, 6, 0]), (0.75, [0, -1, 0]), (1.3, [0, 0, 0])), B)
    for leg in ("leg_fl1", "leg_fl2", "leg_fr1", "leg_fr2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.5, [-80, 0, 0]), (0.75, [15, 0, 0]), (1.3, [0, 0, 0])), B)
    for leg in ("leg_bl1", "leg_bl2", "leg_br1", "leg_br2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.5, [45, 0, 0]), (0.75, [-10, 0, 0]), (1.3, [0, 0, 0])), B)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.5, [-20, 0, 0]), (0.75, [25, 0, 0]), (1.3, [0, 0, 0])), B)
    A["slam"] = A["roll"] = a

    a = anim(1.1, False)                                    # leap: crouch, spring, legs tucked, land
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.2, [0, -2, 0]), (0.55, [0, 12, 0]), (0.9, [0, 0, 0]), (1.1, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.2, [6, 0, 0]), (0.4, [-15, 0, 0]), (0.75, [10, 0, 0]), (1.1, [0, 0, 0])), B)
    for leg in ("leg_fl1", "leg_fl2", "leg_fr1", "leg_fr2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.4, [-55, 0, 0]), (0.75, [-20, 0, 0]), (1.1, [0, 0, 0])), B)
    for leg in ("leg_bl1", "leg_bl2", "leg_br1", "leg_br2"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.2, [-15, 0, 0]), (0.4, [55, 0, 0]), (0.75, [20, 0, 0]), (1.1, [0, 0, 0])), B)
    A["leap"] = a

    a = anim(0.45, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.12, [-6, 0, 8]), (0.45, [0, 0, 0])), B)
    put(a, "neck", "rotation", keys((0, [0, 0, 0]), (0.12, [-15, 10, 0]), (0.45, [0, 0, 0])), B)
    A["hurt"] = a
    return A


# ------------------------------------------------------------------ Fenrir
def fenrir(B):
    A = {}
    a = anim(3.0, True)                                     # idle: heavy breathing, panting, chain swinging
    put(a, "body", "position", wave(3.0, 0.35, axis=1), B)
    put(a, "body", "rotation", wave(3.0, 1.5, axis=0), B)
    put(a, "head", "rotation", keys((0, [8, 0, 0]), (1.0, [10, -12, 0]), (2.0, [6, 10, 0]), (3.0, [8, 0, 0])), B)
    put(a, "jaw", "rotation", wave(3.0, 6, axis=0, offset=10, steps=12), B)
    put(a, "tail", "rotation", wave(3.0, 8, axis=1), B)
    put(a, "chain", "rotation", wave(3.0, 8, axis=0, steps=12), B)
    A["idle"] = a

    for name, length, amp in (("walk", 1.2, 24), ("run", 0.55, 48)):
        a = anim(length, True)
        if name == "walk":
            ph = {"leg_fl": 0, "leg_br": 0.0, "leg_fr": 0.5, "leg_bl": 0.5}
        else:                                               # bounding: fronts together, backs together
            ph = {"leg_fl": 0, "leg_fr": 0.06, "leg_bl": 0.5, "leg_br": 0.56}
        for leg, p in ph.items():
            put(a, leg, "rotation", swing(length, amp, p), B)
        put(a, "body", "rotation", swing(length, 2 if name == "walk" else 7, 0.25), B)
        put(a, "body", "position", wave(length, 0.3 if name == "walk" else 1.2, axis=1, steps=12), B)
        put(a, "head", "rotation", swing(length, 3 if name == "walk" else 7, 0.6, offset=6 if name == "walk" else 12), B)
        put(a, "tail", "rotation", keys((0, [10 if name == "walk" else -20, 0, 0]), (length, [10 if name == "walk" else -20, 0, 0])), B)
        put(a, "chain", "rotation", swing(length, 10 if name == "walk" else 25, 0.3, offset=0 if name == "walk" else -20), B)
        put(a, "jaw", "rotation", keys((0, [15, 0, 0]), (length, [15, 0, 0])), B) if name == "run" else None
        A[name] = a
    A["charge"] = json.loads(json.dumps(A["run"]))
    put(A["charge"], "head", "rotation", swing(0.55, 5, 0.6, offset=25), B)

    a = anim(0.75, False)                                   # attack: lunging bite
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.2, [-6, 0, 0]), (0.38, [10, 0, 0]), (0.75, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.2, [-18, 0, 0]), (0.38, [20, 0, 0]), (0.75, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [50, 0, 0]), (0.36, [50, 0, 0]), (0.42, [0, 0, 0]), (0.75, [0, 0, 0])), B)
    put(a, "leg_fl", "rotation", keys((0, [0, 0, 0]), (0.38, [-25, 0, 0]), (0.75, [0, 0, 0])), B)
    put(a, "leg_fr", "rotation", keys((0, [0, 0, 0]), (0.38, [-25, 0, 0]), (0.75, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a

    a = anim(2.4, False)                                    # roar: the howl at the end of the world
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.4, [-14, 0, 0]), (2.0, [-14, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-55, 0, 0]), (1.2, [-62, 0, 0]), (2.0, [-55, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [28, 0, 0]), (1.0, [38, 0, 0]), (1.6, [30, 0, 0]), (2.0, [34, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "leg_fl", "rotation", keys((0, [0, 0, 0]), (0.4, [-12, 0, 0]), (2.0, [-12, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "leg_fr", "rotation", keys((0, [0, 0, 0]), (0.4, [-12, 0, 0]), (2.0, [-12, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "leg_bl", "rotation", keys((0, [0, 0, 0]), (0.4, [14, 0, 0]), (2.0, [14, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "leg_br", "rotation", keys((0, [0, 0, 0]), (0.4, [14, 0, 0]), (2.0, [14, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "tail", "rotation", keys((0, [0, 0, 0]), (0.4, [-30, 0, 0]), (2.0, [-30, 0, 0]), (2.4, [0, 0, 0])), B)
    put(a, "chain", "rotation", keys((0, [0, 0, 0]), (0.5, [-30, 0, 0]), (1.0, [10, 0, 0]), (1.5, [-15, 0, 0]), (2.4, [0, 0, 0])), B)
    A["roar"] = a

    a = anim(1.1, False)                                    # slam: rears and crashes both forepaws down
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.45, [-38, 0, 0]), (0.65, [10, 0, 0]), (1.1, [0, 0, 0])), B)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.45, [0, 4, 0]), (0.65, [0, -1, 0]), (1.1, [0, 0, 0])), B)
    for leg in ("leg_fl", "leg_fr"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.45, [-75, 0, 0]), (0.65, [15, 0, 0]), (1.1, [0, 0, 0])), B)
    for leg in ("leg_bl", "leg_br"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.45, [38, 0, 0]), (0.65, [-8, 0, 0]), (1.1, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.45, [-10, 0, 0]), (0.65, [25, 0, 0]), (1.1, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [35, 0, 0]), (0.8, [10, 0, 0]), (1.1, [0, 0, 0])), B)
    A["slam"] = A["roll"] = a

    a = anim(1.0, False)                                    # leap: pounce
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.2, [0, -2, 0]), (0.5, [0, 10, 0]), (0.85, [0, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.2, [8, 0, 0]), (0.4, [-18, 0, 0]), (0.75, [12, 0, 0]), (1.0, [0, 0, 0])), B)
    for leg in ("leg_fl", "leg_fr"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.4, [-70, 0, 0]), (0.75, [-30, 0, 0]), (1.0, [0, 0, 0])), B)
    for leg in ("leg_bl", "leg_br"):
        put(a, leg, "rotation", keys((0, [0, 0, 0]), (0.2, [-20, 0, 0]), (0.4, [60, 0, 0]), (0.75, [10, 0, 0]), (1.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.4, [45, 0, 0]), (0.8, [45, 0, 0]), (0.9, [0, 0, 0])), B)
    put(a, "tail", "rotation", keys((0, [0, 0, 0]), (0.4, [-40, 0, 0]), (1.0, [0, 0, 0])), B)
    A["leap"] = a

    a = anim(0.4, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.1, [0, 0, -8]), (0.4, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.1, [-12, -15, 0]), (0.4, [0, 0, 0])), B)
    A["hurt"] = a
    return A


# ------------------------------------------------------------------ Jormungandr
def jormungandr(B):
    A = {}
    segs = sorted((b for b in B if b.startswith("seg")), key=lambda s: int(s[3:]))

    def undulate(a, length, amp, lag=0.11, grow=0.12):
        for i, s in enumerate(segs):
            put(a, s, "rotation", swing(length, amp * (1 + grow * i), -lag * (i + 1), axis=1, steps=16), B)
        put(a, "head", "rotation", swing(length, amp * 0.6, 0.0, axis=1, steps=16), B)

    a = anim(4.0, True)
    undulate(a, 4.0, 6)
    put(a, "jaw", "rotation", wave(4.0, 4, axis=0, offset=4), B)
    A["idle"] = a
    for name, length, amp in (("walk", 2.0, 10), ("run", 1.1, 14)):
        a = anim(length, True)
        undulate(a, length, amp)
        A[name] = a
    A["charge"] = A["run"]

    a = anim(0.85, False)                                   # attack: coil back and strike
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.25, [-25, 0, 0]), (0.42, [18, 0, 0]), (0.85, [0, 0, 0])), B)
    put(a, "seg1", "rotation", keys((0, [0, 0, 0]), (0.25, [20, 0, 0]), (0.42, [-12, 0, 0]), (0.85, [0, 0, 0])), B)
    put(a, "seg2", "rotation", keys((0, [0, 0, 0]), (0.25, [10, 0, 0]), (0.42, [-6, 0, 0]), (0.85, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.25, [55, 0, 0]), (0.4, [55, 0, 0]), (0.47, [0, 0, 0]), (0.85, [0, 0, 0])), B)
    A["attack"] = A["throw"] = a

    a = anim(2.0, False)                                    # roar: rears out of the sea, venom spray
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-55, 0, 0]), (1.0, [-50, 15, 0]), (1.4, [-50, -15, 0]), (2.0, [0, 0, 0])), B)
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.5, [0, 10, 0]), (1.6, [0, 10, 0]), (2.0, [0, 0, 0])), B)
    for s, v in zip(segs, (20, 15, 10, 5)):              # the body curves back down to the water behind the head
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.5, [v, 0, 0]), (1.6, [v, 0, 0]), (2.0, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [50, 0, 0]), (1.6, [50, 0, 0]), (2.0, [0, 0, 0])), B)
    A["roar"] = a

    a = anim(1.5, False)                                    # slam: the tail rises and crashes down
    tail = segs[len(segs) // 2:]
    for i, s in enumerate(tail):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.6, [14 + 3 * i, 0, 0]), (0.85, [-12 - 2 * i, 0, 0]), (1.1, [4, 0, 0]), (1.5, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.6, [-10, 0, 0]), (0.85, [5, 0, 0]), (1.5, [0, 0, 0])), B)
    A["slam"] = a

    a = anim(1.6, False)                                    # leap: breaches like a whale and dives back in
    put(a, "head", "position", keys((0, [0, 0, 0]), (0.6, [0, 16, 0]), (1.2, [0, 2, 0]), (1.6, [0, 0, 0])), B)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.4, [-45, 0, 0]), (0.8, [0, 0, 0]), (1.2, [40, 0, 0]), (1.6, [0, 0, 0])), B)
    for i, s in enumerate(segs):
        put(a, s, "rotation", keys((0, [0, 0, 0]), (0.4 + 0.04 * i, [10, 0, 0]), (0.9 + 0.04 * i, [-8, 0, 0]), (1.6, [0, 0, 0])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [40, 0, 0]), (1.0, [40, 0, 0]), (1.2, [0, 0, 0])), B)
    A["leap"] = a

    a = anim(1.6, False)                                    # roll: twisting death spiral
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.8, [0, 0, 360]), (1.6, [0, 0, 720])), B)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [35, 0, 0]), (1.4, [35, 0, 0]), (1.6, [0, 0, 0])), B)
    A["roll"] = a

    a = anim(0.45, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.12, [-10, 12, 8]), (0.45, [0, 0, 0])), B)
    put(a, "seg1", "rotation", keys((0, [0, 0, 0]), (0.12, [0, -15, 0]), (0.45, [0, 0, 0])), B)
    A["hurt"] = a
    return A


RIGS = {"sleipnir": sleipnir, "fenrir": fenrir, "jormungandr": jormungandr}


def main():
    out = ASSETS / "animations/entity/boss"
    for boss, fn in RIGS.items():
        A = fn(bones_of(boss))
        data = {"format_version": "1.8.0", "animations": {f"animation.boss.{k}": v for k, v in A.items()}}
        (out / f"{boss}.animation.json").write_text(json.dumps(data, indent=1))
        print(boss, len(A), "animations")


if __name__ == "__main__":
    main()
