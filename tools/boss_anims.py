#!/usr/bin/env python3
"""
Animations for the pack's own boss models (GeckoLib / Bedrock format):
  ragnarok/src/main/resources/assets/vividlands_ragnarok/animations/entity/boss/<id>.animation.json

Every model gets the same animation names (BossAnimations.java plays them):
  idle, walk, run (loops) and attack, roar, slam, charge, leap, roll, throw, hurt (one-shots, started by abilities).
They are made from the bones each model has, by rig type: four-legged animals, the gorilla, the crocodile, the shark.
Rotations are in degrees; positive X tips a bone forward/down.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "ragnarok/src/main/resources/assets/vividlands_ragnarok"

RIGS = {
    "cave_bear": "quad", "irish_elk": "quad", "hippo": "quad", "saber_tooth": "quad", "woolly_rhino": "quad",
    "elephant": "quad", "mammoth": "quad", "crocodile": "croc", "silverback": "ape", "bull_shark": "shark",
}


def wave(length, amp, phase=0.0, steps=8, axis=0, offset=0.0, base=(0, 0, 0)):
    """Keyframes of a sine wave on one axis over one loop."""
    out = {}
    for i in range(steps + 1):
        t = length * i / steps
        v = list(base)
        v[axis] = round(offset + amp * math.sin(2 * math.pi * (i / steps) + phase), 2)
        out[f"{t:.3f}".rstrip("0").rstrip(".") if t else "0.0"] = v
    return out


def keys(*frames):
    """keys((t, [x,y,z]), ...) -> keyframe dict."""
    return {(f"{t:.3f}".rstrip("0").rstrip(".") if t else "0.0"): [round(c, 2) for c in v] for t, v in frames}


def put(anim, bone, channel, frames, bones):
    if bone in bones:
        anim["bones"].setdefault(bone, {})[channel] = frames


def anim(length, loop):
    return {"loop": loop, "animation_length": length, "bones": {}}


def quad(bones):
    A = {}
    legs_a, legs_b = ["leg_fl", "leg_br"], ["leg_fr", "leg_bl"]
    trunk = [b for b in ("trunk1", "trunk2", "trunk3") if b in bones]
    # idle: breathing, a slow look around, tail and ears
    a = anim(3.0, True)
    put(a, "body", "position", wave(3.0, 0.25, axis=1), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (1.0, [4, -8, 0]), (2.0, [2, 8, 0]), (3.0, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", wave(3.0, 3, axis=0, offset=3), bones)
    put(a, "tail", "rotation", wave(3.0, 10, axis=1), bones)
    for i, t in enumerate(trunk):
        put(a, t, "rotation", wave(3.0, 6 + 3 * i, phase=i * 0.8, axis=0), bones)
    put(a, "ear_l", "rotation", wave(3.0, 10, axis=1), bones)
    put(a, "ear_r", "rotation", wave(3.0, -10, axis=1), bones)
    put(a, "neck", "rotation", wave(3.0, 3, axis=0), bones)
    A["idle"] = a
    # walk: diagonal pairs swing together
    for name, length, amp, bob in (("walk", 1.2, 24, 0.4), ("run", 0.6, 40, 0.9)):
        a = anim(length, True)
        for b in legs_a:
            put(a, b, "rotation", wave(length, amp, axis=0), bones)
        for b in legs_b:
            put(a, b, "rotation", wave(length, -amp, axis=0), bones)
        put(a, "body", "position", wave(length, bob, axis=1, phase=math.pi / 2, steps=8), bones)
        put(a, "body", "rotation", wave(length, 2 if name == "walk" else 5, axis=0), bones)
        put(a, "head", "rotation", wave(length, 4, axis=0, phase=1.0), bones)
        put(a, "tail", "rotation", wave(length, 14, axis=1), bones)
        for i, t in enumerate(trunk):
            put(a, t, "rotation", wave(length, 10 + 4 * i, phase=i * 0.7, axis=0), bones)
        put(a, "ear_l", "rotation", wave(length, 12, axis=1), bones)
        put(a, "ear_r", "rotation", wave(length, -12, axis=1), bones)
        A[name] = a
    # attack: rear the head back, then bite / gore down
    a = anim(0.6, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.15, [-22, 0, 0]), (0.3, [26, 0, 0]), (0.6, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.15, [28, 0, 0]), (0.32, [0, 0, 0]), (0.6, [0, 0, 0])), bones)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.3, [0, 0, -2]), (0.6, [0, 0, 0])), bones)
    for i, t in enumerate(trunk):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (0.15, [-40 - 15 * i, 0, 0]), (0.32, [20, 0, 0]), (0.6, [0, 0, 0])), bones)
    for b in ("leg_fl", "leg_fr"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.15, [-20, 0, 0]), (0.3, [10, 0, 0]), (0.6, [0, 0, 0])), bones)
    A["attack"] = a
    # roar: rear up on the hind legs, head high, mouth wide
    a = anim(1.6, False)
    up = keys((0, [0, 0, 0]), (0.4, [-24, 0, 0]), (1.2, [-24, 0, 0]), (1.6, [0, 0, 0]))
    put(a, "body", "rotation", up, bones)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.4, [0, 3, 2]), (1.2, [0, 3, 2]), (1.6, [0, 0, 0])), bones)
    for b in ("leg_fl", "leg_fr"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.4, [-30, 0, 0]), (0.8, [-15, 0, 0]), (1.2, [-30, 0, 0]), (1.6, [0, 0, 0])), bones)
    for b in ("leg_bl", "leg_br"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.4, [24, 0, 0]), (1.2, [24, 0, 0]), (1.6, [0, 0, 0])), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.4, [-18, 0, 0]), (0.8, [-24, 6, 0]), (1.2, [-18, -6, 0]), (1.6, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.35, [38, 0, 0]), (1.25, [38, 0, 0]), (1.6, [0, 0, 0])), bones)
    for i, t in enumerate(trunk):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (0.4, [-60 - 20 * i, 0, 0]), (1.2, [-60 - 20 * i, 0, 0]), (1.6, [0, 0, 0])), bones)
    put(a, "ear_l", "rotation", keys((0, [0, 0, 0]), (0.4, [0, -40, 0]), (1.2, [0, -40, 0]), (1.6, [0, 0, 0])), bones)
    put(a, "ear_r", "rotation", keys((0, [0, 0, 0]), (0.4, [0, 40, 0]), (1.2, [0, 40, 0]), (1.6, [0, 0, 0])), bones)
    put(a, "tail", "rotation", keys((0, [0, 0, 0]), (0.4, [-30, 0, 0]), (1.2, [-30, 0, 0]), (1.6, [0, 0, 0])), bones)
    A["roar"] = a
    # slam: rear up, then crash the front down
    a = anim(1.1, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.5, [-30, 0, 0]), (0.62, [8, 0, 0]), (0.8, [4, 0, 0]), (1.1, [0, 0, 0])), bones)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.5, [0, 4, 2]), (0.62, [0, -1, 0]), (1.1, [0, 0, 0])), bones)
    for b in ("leg_fl", "leg_fr"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.5, [-55, 0, 0]), (0.62, [12, 0, 0]), (1.1, [0, 0, 0])), bones)
    for b in ("leg_bl", "leg_br"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.5, [30, 0, 0]), (0.62, [-6, 0, 0]), (1.1, [0, 0, 0])), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.5, [-20, 0, 0]), (0.62, [24, 0, 0]), (1.1, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.55, [30, 0, 0]), (0.8, [0, 0, 0])), bones)
    A["slam"] = a
    # charge: head down, fast gallop
    a = anim(2.6, False)
    for b in legs_a:
        put(a, b, "rotation", wave(2.6, 45, axis=0, steps=24), bones)
    for b in legs_b:
        put(a, b, "rotation", wave(2.6, -45, axis=0, steps=24), bones)
    a["bones"].setdefault("leg_fl", {})
    for b in legs_a + legs_b:
        if b in a["bones"]:
            a["bones"][b]["rotation"] = {k: [v[0] * (1 if i % 2 else 1), 0, 0] for i, (k, v) in enumerate(a["bones"][b]["rotation"].items())}
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.4, [28, 0, 0]), (2.3, [28, 0, 0]), (2.6, [0, 0, 0])), bones)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.4, [6, 0, 0]), (2.3, [6, 0, 0]), (2.6, [0, 0, 0])), bones)
    for i, t in enumerate(trunk):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (0.4, [-50, 0, 0]), (2.3, [-50, 0, 0]), (2.6, [0, 0, 0])), bones)
    A["charge"] = a
    # leap: crouch, spring, land
    a = anim(1.2, False)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.35, [0, -2.5, 0]), (0.6, [0, 1, 0]), (1.0, [0, -1, 0]), (1.2, [0, 0, 0])), bones)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.35, [6, 0, 0]), (0.6, [-24, 0, 0]), (0.9, [12, 0, 0]), (1.2, [0, 0, 0])), bones)
    for b in ("leg_fl", "leg_fr"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.35, [20, 0, 0]), (0.6, [-60, 0, 0]), (0.9, [-20, 0, 0]), (1.2, [0, 0, 0])), bones)
    for b in ("leg_bl", "leg_br"):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.35, [-20, 0, 0]), (0.6, [50, 0, 0]), (0.9, [10, 0, 0]), (1.2, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.5, [32, 0, 0]), (0.9, [32, 0, 0]), (1.0, [0, 0, 0])), bones)
    A["leap"] = a
    A["roll"] = A["attack"]
    A["throw"] = A["attack"]
    a = anim(0.4, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.1, [0, 0, 6]), (0.25, [0, 0, -4]), (0.4, [0, 0, 0])), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.1, [-14, 0, 0]), (0.4, [0, 0, 0])), bones)
    A["hurt"] = a
    return A


def croc(bones):
    A = quad(bones)
    tails = [b for b in ("tail", "tail2", "tail3") if b in bones]
    for name, length, amp in (("idle", 3.0, 6), ("walk", 1.2, 16), ("run", 0.6, 22)):
        for i, t in enumerate(tails):
            put(A[name], t, "rotation", wave(length, amp + 4 * i, phase=-i * 0.9, axis=1), bones)
        if name != "idle":
            put(A[name], "body", "rotation", wave(length, 6, axis=1), bones)
    # death roll: spin around the length of the body with the jaws shut
    a = anim(3.0, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.75, [0, 0, 180]), (1.5, [0, 0, 360]), (2.25, [0, 0, 540]), (3.0, [0, 0, 720])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.15, [30, 0, 0]), (0.3, [0, 0, 0]), (3.0, [0, 0, 0])), bones)
    for i, t in enumerate(tails):
        put(a, t, "rotation", wave(3.0, 25, phase=-i, axis=1, steps=12), bones)
    A["roll"] = a
    # tail sweep (slam): whip the tail round
    a = anim(1.0, False)
    for i, t in enumerate(tails):
        put(a, t, "rotation", keys((0, [0, 0, 0]), (0.45, [0, -35 - 10 * i, 0]), (0.62, [0, 45 + 10 * i, 0]), (1.0, [0, 0, 0])), bones)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.45, [0, 15, 0]), (0.62, [0, -20, 0]), (1.0, [0, 0, 0])), bones)
    A["slam"] = a
    # roar for a crocodile: jaws gape, head up
    a = anim(1.4, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.4, [-25, 0, 0]), (1.0, [-25, 0, 0]), (1.4, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.4, [45, 0, 0]), (1.0, [45, 0, 0]), (1.4, [0, 0, 0])), bones)
    A["roar"] = a
    return A


def ape(bones):
    A = {}
    a = anim(3.0, True)
    put(a, "chest", "rotation", wave(3.0, 2, axis=0), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (1.0, [4, -10, 0]), (2.0, [0, 10, 0]), (3.0, [0, 0, 0])), bones)
    put(a, "arm_l", "rotation", wave(3.0, 3, axis=0), bones)
    put(a, "arm_r", "rotation", wave(3.0, -3, axis=0), bones)
    put(a, "jaw", "rotation", wave(3.0, 3, axis=0, offset=3), bones)
    A["idle"] = a
    for name, length, amp in (("walk", 1.2, 26), ("run", 0.7, 40)):
        a = anim(length, True)
        put(a, "arm_l", "rotation", wave(length, amp, axis=0), bones)
        put(a, "arm_r", "rotation", wave(length, -amp, axis=0), bones)
        put(a, "leg_l", "rotation", wave(length, -amp, axis=0), bones)
        put(a, "leg_r", "rotation", wave(length, amp, axis=0), bones)
        put(a, "body", "position", wave(length, 0.5, axis=1, phase=math.pi / 2), bones)
        put(a, "chest", "rotation", wave(length, 4, axis=1), bones)
        A[name] = a
    a = anim(0.6, False)
    put(a, "arm_r", "rotation", keys((0, [0, 0, 0]), (0.2, [-110, 0, -15]), (0.35, [15, 0, 0]), (0.6, [0, 0, 0])), bones)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.2, [-10, -15, 0]), (0.35, [10, 15, 0]), (0.6, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [25, 0, 0]), (0.4, [0, 0, 0])), bones)
    A["attack"] = a
    # chest beat: stand up and drum
    a = anim(1.8, False)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.3, [25, 0, 0]), (1.5, [25, 0, 0]), (1.8, [0, 0, 0])), bones)
    beat_l, beat_r = [(0, [0, 0, 0]), (0.3, [-80, 0, 30])], [(0, [0, 0, 0]), (0.3, [-80, 0, -30])]
    for i in range(6):
        t = 0.4 + i * 0.18
        beat_l.append((t, [-60 if i % 2 else -95, 0, 40]))
        beat_r.append((t, [-95 if i % 2 else -60, 0, -40]))
    beat_l.append((1.8, [0, 0, 0]))
    beat_r.append((1.8, [0, 0, 0]))
    put(a, "arm_l", "rotation", keys(*beat_l), bones)
    put(a, "arm_r", "rotation", keys(*beat_r), bones)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.3, [-20, 0, 0]), (1.5, [-20, 0, 0]), (1.8, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.3, [40, 0, 0]), (1.5, [40, 0, 0]), (1.8, [0, 0, 0])), bones)
    A["roar"] = a
    # ground pound: both fists up, then down
    a = anim(1.1, False)
    for b, z in (("arm_l", 20), ("arm_r", -20)):
        put(a, b, "rotation", keys((0, [0, 0, 0]), (0.45, [-165, 0, z]), (0.6, [10, 0, 0]), (1.1, [0, 0, 0])), bones)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.45, [20, 0, 0]), (0.6, [-25, 0, 0]), (1.1, [0, 0, 0])), bones)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.45, [0, 2, 0]), (0.6, [0, -1, 0]), (1.1, [0, 0, 0])), bones)
    A["slam"] = a
    a = anim(0.9, False)
    put(a, "arm_r", "rotation", keys((0, [0, 0, 0]), (0.4, [-170, 0, 0]), (0.55, [40, 0, 0]), (0.9, [0, 0, 0])), bones)
    put(a, "arm_l", "rotation", keys((0, [0, 0, 0]), (0.4, [-150, 0, 0]), (0.55, [30, 0, 0]), (0.9, [0, 0, 0])), bones)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.4, [20, 0, 0]), (0.55, [-20, 0, 0]), (0.9, [0, 0, 0])), bones)
    A["throw"] = a
    A["charge"], A["leap"], A["roll"] = A["run"], A["slam"], A["attack"]
    a = anim(0.4, False)
    put(a, "chest", "rotation", keys((0, [0, 0, 0]), (0.1, [-8, 0, 6]), (0.4, [0, 0, 0])), bones)
    A["hurt"] = a
    return A


def shark(bones):
    A = {}
    for name, length, amp in (("idle", 2.0, 12), ("walk", 1.2, 20), ("run", 0.6, 28)):
        a = anim(length, True)
        put(a, "body", "rotation", wave(length, amp * 0.3, axis=1), bones)
        put(a, "tail", "rotation", wave(length, amp, phase=-0.8, axis=1), bones)
        put(a, "tail2", "rotation", wave(length, amp * 1.4, phase=-1.6, axis=1), bones)
        put(a, "head", "rotation", wave(length, amp * 0.2, phase=0.5, axis=1), bones)
        put(a, "fin_l", "rotation", wave(length, 8, axis=2), bones)
        put(a, "fin_r", "rotation", wave(length, -8, axis=2), bones)
        A[name] = a
    a = anim(0.6, False)
    put(a, "head", "rotation", keys((0, [0, 0, 0]), (0.15, [-14, 0, 0]), (0.3, [10, 0, 0]), (0.6, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.15, [40, 0, 0]), (0.32, [0, 0, 0])), bones)
    put(a, "body", "position", keys((0, [0, 0, 0]), (0.3, [0, 0, -3]), (0.6, [0, 0, 0])), bones)
    A["attack"] = a
    a = anim(1.5, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.4, [-45, 0, 0]), (0.9, [30, 0, 0]), (1.5, [0, 0, 0])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.35, [45, 0, 0]), (0.8, [45, 0, 0]), (1.0, [0, 0, 0])), bones)
    put(a, "tail", "rotation", wave(1.5, 30, axis=1, steps=12), bones)
    put(a, "tail2", "rotation", wave(1.5, 40, phase=-1, axis=1, steps=12), bones)
    A["leap"] = a
    a = anim(2.0, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (1.0, [0, 0, 360]), (2.0, [0, 0, 720])), bones)
    put(a, "jaw", "rotation", keys((0, [0, 0, 0]), (0.2, [35, 0, 0]), (1.8, [35, 0, 0]), (2.0, [0, 0, 0])), bones)
    A["roll"] = a
    A["charge"] = A["run"]
    A["roar"] = A["slam"] = A["throw"] = A["attack"]
    a = anim(0.4, False)
    put(a, "body", "rotation", keys((0, [0, 0, 0]), (0.1, [0, 0, 10]), (0.4, [0, 0, 0])), bones)
    A["hurt"] = a
    return A


def main():
    out_dir = ASSETS / "animations/entity/boss"
    out_dir.mkdir(parents=True, exist_ok=True)
    for boss, rig in RIGS.items():
        geo = json.loads((ASSETS / f"geo/entity/boss/{boss}.geo.json").read_text())
        bones = {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}
        anims = {"quad": quad, "croc": croc, "ape": ape, "shark": shark}[rig](bones)
        data = {"format_version": "1.8.0", "animations": {f"animation.boss.{k}": v for k, v in anims.items()}}
        (out_dir / f"{boss}.animation.json").write_text(json.dumps(data, indent=1))
        print(boss, rig, len(anims), "animations,", len(bones), "bones")


if __name__ == "__main__":
    main()
