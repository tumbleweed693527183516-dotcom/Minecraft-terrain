#!/usr/bin/env python3
"""
Pixel-art textures for Vivid Lands blocks, drawn by code (16x16, vanilla-style).
Deterministic: the same seed always produces the same textures.

    python3 tools/textures.py   (writes into src/main/resources/assets/vividlands/textures/block)
"""
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "src/main/resources/assets/vividlands/textures/block"
S = 16


def rng(name):
    return np.random.default_rng(abs(hash(name)) % (2 ** 32) if False else sum(map(ord, name)) * 7919)


def canvas(rgb=(0, 0, 0), alpha=255):
    a = np.zeros((S, S, 4), np.uint8)
    a[..., :3] = rgb
    a[..., 3] = alpha
    return a


def save(name, a):
    OUT.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a, "RGBA").save(OUT / f"{name}.png")


def speckle(name, palette, weights, glint=None, glint_p=0.0):
    r = rng(name)
    idx = r.choice(len(palette), size=(S, S), p=np.array(weights) / sum(weights))
    a = canvas()
    a[..., :3] = np.array(palette)[idx]
    if glint:
        m = r.random((S, S)) < glint_p
        a[m, :3] = glint
    return a


def black_sand():
    return speckle("black_sand", [(36, 34, 40), (28, 27, 32), (48, 46, 54), (58, 56, 64), (22, 21, 26)],
                   [5, 4, 3, 2, 2], glint=(96, 94, 108), glint_p=0.03)


def volcanic_ash():
    return speckle("volcanic_ash", [(118, 116, 113), (104, 102, 99), (134, 132, 128), (92, 90, 88), (146, 143, 138)],
                   [5, 4, 3, 2, 1])


def salt_crust():
    r = rng("salt")
    pts = r.random((7, 2)) * S
    yy, xx = np.mgrid[0:S, 0:S] + 0.5
    d = []
    for px, py in pts:  # tileable distances
        dx = np.minimum(abs(xx - px), S - abs(xx - px))
        dy = np.minimum(abs(yy - py), S - abs(yy - py))
        d.append(np.hypot(dx, dy))
    d = np.sort(np.stack(d), axis=0)
    crack = (d[1] - d[0]) < 0.9
    a = speckle("salt_base", [(238, 234, 226), (230, 226, 218), (244, 242, 236), (224, 219, 210)], [5, 4, 3, 2])
    a[crack, :3] = (196, 189, 178)
    return a


def peat():
    r = rng("peat")
    a = speckle("peat", [(52, 36, 24), (64, 44, 28), (44, 30, 20), (58, 40, 26)], [4, 3, 3, 2])
    for _ in range(9):  # fibrous streaks
        y, x, ln = r.integers(0, S), r.integers(0, S), r.integers(3, 7)
        for i in range(ln):
            a[y, (x + i) % S, :3] = (84, 60, 36) if i % 2 else (74, 52, 32)
    return a


def plank(name, base, dark, light):
    r = rng(name)
    a = canvas(base)
    for row in range(4):
        y0 = row * 4
        tone = np.array(base) + r.integers(-8, 9)
        a[y0:y0 + 4, :, :3] = np.clip(tone, 0, 255)
        a[y0 + 3, :, :3] = dark                                      # seam under each board
        cut = int(r.integers(2, 14))
        a[y0:y0 + 3, cut, :3] = dark                                 # board end
        for _ in range(3):                                           # grain
            gy, gx = y0 + int(r.integers(0, 3)), int(r.integers(0, S))
            a[gy, gx:gx + int(r.integers(2, 5)), :3] = light
    return a


def log_side(name, colors, style):
    r = rng(name)
    a = canvas(colors[0])
    if style == "palm":       # stacked frond scars: horizontal ridges with a diamond offset
        for y in range(S):
            for x in range(S):
                ridge = ((y + (x // 4) % 2 * 2) % 4) == 0
                a[y, x, :3] = colors[2] if ridge else colors[int(r.integers(0, 2))]
    elif style == "redwood":  # deep vertical fibres
        for x in range(S):
            c = colors[int(r.integers(0, 3))]
            a[:, x, :3] = c
            for y in range(S):
                if r.random() < 0.18:
                    a[y, x, :3] = colors[3]
    else:                     # scots pine: orange plates with dark cracks
        a[..., :3] = colors[0]
        for y in range(S):
            for x in range(S):
                a[y, x, :3] = colors[int(r.integers(0, 3))]
        for _ in range(7):
            x, y, ln = int(r.integers(0, S)), int(r.integers(0, S)), int(r.integers(3, 7))
            for i in range(ln):
                a[(y + i) % S, x, :3] = colors[3]
            a[y, (x + 1) % S, :3] = colors[3]
    return a


def log_top(name, bark, ring_a, ring_b):
    yy, xx = np.mgrid[0:S, 0:S] + 0.5
    rr = np.hypot(xx - 8, yy - 8)
    a = canvas(ring_a)
    a[(rr.astype(int) % 2) == 1, :3] = ring_b
    edge = (xx < 1) | (yy < 1) | (xx > S - 1) | (yy > S - 1)
    a[edge, :3] = bark
    return a


def leaves(name, palette, holes=0.22):
    r = rng(name)
    a = speckle(name, palette, [4, 3, 2, 1][:len(palette)])
    for _ in range(14):  # brighter leaf clusters
        x, y = int(r.integers(0, S)), int(r.integers(0, S))
        a[y, x, :3] = np.clip(np.array(palette[0]) + 22, 0, 255)
    a[r.random((S, S)) < holes, 3] = 0
    return a


def palm_leaves():
    r = rng("palm_fronds")
    a = canvas((0, 0, 0), 0)
    greens = [(70, 160, 52), (54, 132, 42), (92, 182, 64), (40, 110, 36)]
    for k in range(12):  # feathery diagonal fronds
        x0, y0 = int(r.integers(-4, S)), int(r.integers(0, S))
        dx = 1 if k % 2 else -1
        for i in range(14):
            x, y = (x0 + i * dx) % S, (y0 + i // 2) % S
            a[y, x] = (*greens[int(r.integers(0, 3))], 255)
            for side in (-1, 1):  # leaflets
                if r.random() < 0.75:
                    a[(y + side) % S, (x - dx) % S] = (*greens[int(r.integers(0, 4))], 255)
    return a


def plant(name, stems, heads, height=(6, 13), count=7, head_size=2):
    r = rng(name)
    a = canvas((0, 0, 0), 0)
    for k in range(count):
        x = int(np.clip(1 + k * 2 + r.integers(-1, 2), 0, S - 1))
        h = int(r.integers(*height))
        for i in range(h):
            xx = int(np.clip(x + (1 if (i > h * 0.6 and k % 3 == 0) else 0), 0, S - 1))
            a[S - 1 - i, xx] = (*stems[int(r.integers(0, len(stems)))], 255)
        if heads:
            top = S - h
            for j in range(head_size * 3):
                hy, hx = top + int(r.integers(-1, head_size + 1)), x + int(r.integers(-1, 2))
                if 0 <= hy < S and 0 <= hx < S:
                    a[hy, hx] = (*heads[int(r.integers(0, len(heads)))], 255)
    return a


def heather():
    return plant("heather", stems=[(74, 82, 44), (90, 96, 52), (66, 70, 40)],
                 heads=[(156, 84, 178), (184, 112, 204), (128, 62, 148), (206, 140, 220)], height=(5, 11), count=8,
                 head_size=3)


def dry_grass():
    r = rng("dry_grass")
    a = canvas((0, 0, 0), 0)
    golds = [(206, 176, 98), (176, 146, 74), (226, 204, 128), (150, 122, 62)]
    for k in range(10):
        x = int(np.clip(k * 1.6 + r.integers(-1, 2), 0, S - 1))
        h = int(r.integers(5, 15))
        lean = int(r.choice([-1, 0, 1]))
        for i in range(h):
            xx = int(np.clip(x + (lean if i > h // 2 else 0), 0, S - 1))
            a[S - 1 - i, xx] = (*golds[int(r.integers(0, 4))], 255)
    return a


def layered(name, bands, pore=None, pore_p=0.0, wobble=1):
    """Horizontal mineral layers (sinter, travertine), slightly wavy, with optional pores."""
    r = rng(name)
    a = canvas()
    offs = r.integers(-wobble, wobble + 1, S)
    for y in range(S):
        for x in range(S):
            band = bands[((y + offs[x]) // 2) % len(bands)]
            jitter = r.integers(-6, 7)
            a[y, x, :3] = np.clip(np.array(band) + jitter, 0, 255)
    if pore:
        m = r.random((S, S)) < pore_p
        a[m, :3] = pore
    return a


def thermal_mat():
    """Orange bacterial mat around hot springs: slimy rust and saffron streaks."""
    r = rng("thermal_mat")
    a = speckle("thermal_mat", [(214, 112, 38), (190, 92, 30), (232, 146, 52), (168, 76, 28)], [4, 3, 3, 2])
    for _ in range(6):
        y, x = int(r.integers(0, S)), int(r.integers(0, S))
        for i in range(int(r.integers(3, 8))):
            a[y, (x + i) % S, :3] = (238, 190, 70)
    return a


TEXTURES = {
    "sinter": lambda: layered("sinter", [(222, 220, 212), (206, 204, 196), (232, 230, 224), (196, 194, 188)],
                              pore=(176, 172, 164), pore_p=0.04),
    "travertine": lambda: layered("travertine", [(226, 206, 168), (212, 188, 146), (236, 220, 186), (198, 172, 130)],
                                  pore=(160, 136, 100), pore_p=0.07, wobble=0),
    "thermal_mat": thermal_mat,
    "sulfur_crust": lambda: speckle("sulfur", [(226, 206, 58), (204, 182, 40), (240, 226, 98), (180, 160, 36),
                                               (250, 240, 150)], [5, 4, 3, 2, 1]),
    "black_sand": black_sand,
    "volcanic_ash": volcanic_ash,
    "salt_crust": salt_crust,
    "peat": peat,
    "heather": heather,
    "dry_grass": dry_grass,
    "palm_log": lambda: log_side("palm_log", [(168, 138, 98), (156, 126, 88), (122, 98, 68)], "palm"),
    "palm_log_top": lambda: log_top("palm_top", (140, 112, 78), (196, 166, 120), (172, 142, 100)),
    "palm_leaves": palm_leaves,
    "palm_planks": lambda: plank("palm_planks", (204, 174, 124), (150, 122, 84), (220, 194, 146)),
    "redwood_log": lambda: log_side("redwood_log", [(122, 56, 40), (98, 44, 32), (140, 70, 50), (74, 32, 24)],
                                    "redwood"),
    "redwood_log_top": lambda: log_top("redwood_top", (98, 44, 32), (170, 92, 62), (142, 72, 48)),
    "redwood_leaves": lambda: leaves("redwood_leaves", [(42, 88, 46), (32, 72, 38), (56, 104, 56), (26, 60, 32)]),
    "redwood_planks": lambda: plank("redwood_planks", (152, 76, 56), (104, 50, 36), (172, 96, 72)),
    "pine_log": lambda: log_side("pine_log", [(172, 98, 54), (150, 82, 46), (190, 116, 68), (84, 48, 30)], "pine"),
    "pine_log_top": lambda: log_top("pine_top", (120, 70, 40), (196, 164, 120), (172, 140, 98)),
    "pine_leaves": lambda: leaves("pine_leaves", [(56, 102, 82), (44, 86, 70), (72, 122, 96), (36, 72, 60)]),
    "pine_planks": lambda: plank("pine_planks", (192, 152, 106), (138, 104, 70), (210, 174, 128)),
}


def main():
    for name, fn in TEXTURES.items():
        save(name, fn())
    print(f"Wrote {len(TEXTURES)} textures to {OUT}")


if __name__ == "__main__":
    main()
