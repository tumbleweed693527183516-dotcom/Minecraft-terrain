"""
Quick software preview of a boss model with its texture (rest pose), so texture work can be checked without
starting the game. Writes a 3/4 front and 3/4 back view side by side.

    python3 tools/boss_preview.py cave_bear [out.png]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boss_paint import GEO, TEX  # noqa: E402


def rot(rx, ry, rz):
    a, b, c = map(math.radians, (-rx, -ry, rz))
    X = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Y = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Z = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Z @ Y @ X


def quads(geo, tex, ppu):
    g = geo["minecraft:geometry"][0]
    for bone in g["bones"]:
        for c in bone.get("cubes", []):
            uv = c.get("uv")
            if not isinstance(uv, dict):
                continue
            inf = c.get("inflate", 0)
            x0, y0, z0 = (o - inf for o in c["origin"])
            sx, sy, sz = (s + 2 * inf for s in c["size"])
            R = rot(*c.get("rotation", [0, 0, 0]))
            piv = np.array(c.get("pivot", [0, 0, 0]), float)
            for name, f in uv.items():
                (u, v), (w, h) = f["uv"], f["uv_size"]
                u0, u1 = sorted((u, u + w)); v0, v1 = sorted((v, v + h))
                px0, px1 = int(round(u0 * ppu)), int(round(u1 * ppu))
                py0, py1 = int(round(v0 * ppu)), int(round(v1 * ppu))
                W, H = px1 - px0, py1 - py0
                if W <= 0 or H <= 0:
                    continue
                a = np.linspace(0, 1, W + 1); b = np.linspace(0, 1, H + 1)
                if w < 0: a = a[::-1]
                if h < 0: b = b[::-1]
                A, B = np.meshgrid(a, b)
                if name == "north":
                    P = np.stack([x0 + A * sx, y0 + sy - B * sy, np.full_like(A, z0)], -1); n = (0, 0, -1)
                elif name == "south":
                    P = np.stack([x0 + sx - A * sx, y0 + sy - B * sy, np.full_like(A, z0 + sz)], -1); n = (0, 0, 1)
                elif name == "east":
                    P = np.stack([np.full_like(A, x0), y0 + sy - B * sy, z0 + sz - A * sz], -1); n = (-1, 0, 0)
                elif name == "west":
                    P = np.stack([np.full_like(A, x0 + sx), y0 + sy - B * sy, z0 + A * sz], -1); n = (1, 0, 0)
                elif name == "up":
                    P = np.stack([x0 + A * sx, np.full_like(A, y0 + sy), z0 + B * sz], -1); n = (0, 1, 0)
                else:
                    P = np.stack([x0 + A * sx, np.full_like(A, y0), z0 + B * sz], -1); n = (0, -1, 0)
                P = (P - piv) @ R.T + piv
                yield P, R @ np.array(n, float), tex[py0:py1, px0:px1]


def view(geo, tex, ppu, yaw, size=700):
    cy, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    pitch = math.radians(18)
    V = np.array([[cy, 0, -sy_], [0, 1, 0], [sy_, 0, cy]])
    Pt = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
    M = Pt @ V
    light = np.array([0.4, 0.9, -0.3]); light /= np.linalg.norm(light)
    items = []
    for P, n, t in quads(geo, tex, ppu):
        Q = P @ M.T
        nn = M @ n
        if nn[2] > 0.02:          # facing away (camera looks down +z)
            continue
        items.append((Q[..., 2].mean(), Q, t, 0.62 + 0.38 * max(0, n @ light)))
    allq = np.concatenate([q[1].reshape(-1, 3) for q in items])
    lo, hi = allq.min(0), allq.max(0)
    sc = (size * 0.9) / max(hi[0] - lo[0], hi[1] - lo[1])
    img = Image.new("RGB", (size, size), (150, 185, 225))
    d = ImageDraw.Draw(img)
    for _, Q, t, shade in sorted(items, key=lambda i: -i[0]):
        X = (Q[..., 0] - (lo[0] + hi[0]) / 2) * sc + size / 2
        Y = size / 2 - (Q[..., 1] - (lo[1] + hi[1]) / 2) * sc
        for j in range(t.shape[0]):
            for i in range(t.shape[1]):
                px = t[j, i]
                if px[3] < 10:
                    continue
                col = tuple(int(min(255, c * shade)) for c in px[:3])
                d.polygon([(X[j, i], Y[j, i]), (X[j, i + 1], Y[j, i + 1]), (X[j + 1, i + 1], Y[j + 1, i + 1]), (X[j + 1, i], Y[j + 1, i])], fill=col)
    return img


def preview(boss, out, tex_path=None):
    geo = json.loads((GEO / f"{boss}.geo.json").read_text())
    img = Image.open(tex_path or TEX / f"{boss}.png").convert("RGBA")
    ppu = img.size[0] / geo["minecraft:geometry"][0]["description"]["texture_width"]
    t = np.asarray(img)
    a = view(geo, t, ppu, 210)
    b = view(geo, t, ppu, 35)
    s = Image.new("RGB", (1400, 700)); s.paste(a, (0, 0)); s.paste(b, (700, 0)); s.save(out)


if __name__ == "__main__":
    preview(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else f"/tmp/{sys.argv[1]}_preview.png")
