#!/usr/bin/env python3
"""
Turns the weapon concept models into GeckoLib item models for Vivid Lands: Ragnarok:
  assets/vividlands_ragnarok/geo/item/weapon/<id>.geo.json
  assets/vividlands_ragnarok/textures/item/weapon/<id>.png  (+ <id>_glow.png for glowing parts, drawn full-bright)
  assets/vividlands_ragnarok/animations/item/weapon/<id>.animation.json
  assets/vividlands_ragnarok/models/item/<id>.json          (builtin/entity with hand/GUI transforms)

Each weapon is laid out like a vanilla handheld item (grip low-left, tip up-right) so the vanilla handheld
transforms put it in the hand the usual way; big weapons are simply longer.
"""
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vw = load("vw", "tools/concept/viking_weapons.py")
ww = load("ww", "tools/concept/world_weapons.py")
ex = load("ex", "tools/concept/export_geckolib.py")
va = vw.va
NS = "vividlands_ragnarok"
ASSETS = ROOT / "ragnarok/src/main/resources/assets" / NS

# id: (model function, grip height in voxels, length in pixels when held, kind)
WEAPONS = {
    "bearded_axe": (vw.bearded_axe, 20, 24, "axe"),
    "wolf_seax": (vw.wolf_seax, 16, 19, "sword"),
    "valkyrie_sword": (vw.valkyrie_sword, 18, 24, "sword"),
    "dane_axe": (vw.dane_axe, 26, 36, "axe"),
    "gungnir": (vw.gungnir, 64, 40, "sword"),
    "fenrirs_fang": (vw.fenrirs_fang, 16, 28, "sword"),
    "round_shield": (vw.round_shield, 0, 22, "shield"),
    "khopesh": (ww.khopesh, 16, 20, "sword"),
    "guandao": (ww.guandao, 60, 44, "sword"),
    "gladius": (ww.gladius, 18, 20, "sword"),
    "kopis": (ww.kopis, 18, 20, "sword"),
    "macuahuitl": (ww.macuahuitl, 14, 24, "sword"),
    "katana": (ww.katana, 16, 26, "sword"),
    "zweihander": (ww.zweihander, 24, 34, "sword"),
    "ragnarok": (ww.surtr_blade, 26, 34, "sword"),
}
PIVOT = [5.5, -5.5, 0]          # bedrock coords: the grip sits where a vanilla sword sprite's handle is


def handheld_display(length):
    """Vanilla item/handheld transforms; GUI and ground scaled so long weapons fit in a slot."""
    fit = min(1.0, 22.0 / length)
    return {
        "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
        "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
        "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "ground": {"translation": [0, 2, 0], "scale": [0.5 * fit, 0.5 * fit, 0.5 * fit]},
        "gui": {"scale": [fit, fit, fit]},
        "fixed": {"rotation": [0, 180, 0], "scale": [fit, fit, fit]},
        "head": {"rotation": [0, 180, 0], "translation": [0, 13, 7]},
    }


def shield_display():
    """Vanilla shield transforms (the shield model is centred on the item origin, facing north)."""
    return {
        "thirdperson_righthand": {"rotation": [0, 90, 0], "translation": [10, 6, -4], "scale": [1, 1, 1]},
        "thirdperson_lefthand": {"rotation": [0, 90, 0], "translation": [10, 6, 12], "scale": [1, 1, 1]},
        "firstperson_righthand": {"rotation": [0, 180, 5], "translation": [-10, 2, -10], "scale": [1.25, 1.25, 1.25]},
        "firstperson_lefthand": {"rotation": [0, 180, 5], "translation": [10, 0, -10], "scale": [1.25, 1.25, 1.25]},
        "gui": {"rotation": [15, -25, -5], "translation": [2, 3, 0], "scale": [0.65, 0.65, 0.65]},
        "fixed": {"rotation": [0, 180, 0], "translation": [-2, 4, -5], "scale": [0.5, 0.5, 0.5]},
        "ground": {"translation": [4, 4, 2], "scale": [0.25, 0.25, 0.25]},
    }


def export(wid, fn, grip_y, length, kind):
    m = va.smooth(fn())
    em = getattr(m, "emissive", set())
    ys = [p[1] for p in m.v]
    span = max(ys) - min(ys) + 1
    R = span / length                                 # voxels per pixel for this weapon
    vox, glow = {}, set()
    for (x, y, z), c in m.v.items():
        b = (-x - 1, y - grip_y, z)                    # bedrock voxel space, grip at y = 0
        vox[b] = c
        if (x, y, z) in em:
            glow.add(b)
    atlas = ex.Atlas()
    glow_patches = []
    cubes_json = []
    for (bx0, bx1, by0, by1, bz0, bz1) in ex.greedy(vox):
        uv = {}
        faces = {
            "north": (bx1 - bx0 + 1, by1 - by0 + 1, lambda u, v: (bx0 + u, by1 - v, bz0), (0, 0, -1)),
            "south": (bx1 - bx0 + 1, by1 - by0 + 1, lambda u, v: (bx1 - u, by1 - v, bz1), (0, 0, 1)),
            "west": (bz1 - bz0 + 1, by1 - by0 + 1, lambda u, v: (bx1, by1 - v, bz0 + u), (1, 0, 0)),
            "east": (bz1 - bz0 + 1, by1 - by0 + 1, lambda u, v: (bx0, by1 - v, bz1 - u), (-1, 0, 0)),
            "up": (bx1 - bx0 + 1, bz1 - bz0 + 1, lambda u, v: (bx0 + u, by1, bz1 - v), (0, 1, 0)),
            "down": (bx1 - bx0 + 1, bz1 - bz0 + 1, lambda u, v: (bx0 + u, by0, bz0 + v), (0, -1, 0)),
        }
        for fname, (w, hgt, at, (nx, ny, nz)) in faces.items():
            cells = [(u, v) for u in range(w) for v in range(hgt)]
            if not any((p[0] + nx, p[1] + ny, p[2] + nz) not in vox for p in (at(u, v) for u, v in cells)):
                continue
            img = Image.new("RGBA", (w, hgt))
            gimg = Image.new("RGBA", (w, hgt), (0, 0, 0, 0))
            px, gpx = img.load(), gimg.load()
            lit = False
            for u, v in cells:
                p = at(u, v)
                c = vox.get(p, (255, 0, 255))
                px[u, v] = tuple(c) + (255,)
                if p in glow:
                    gpx[u, v] = tuple(c) + (255,)
                    lit = True
            uv[fname] = {"uv": [0, 0], "uv_size": [w, hgt]}
            atlas.add(img, uv[fname])
            glow_patches.append((uv[fname], gimg if lit else None, img))
        if uv:
            if kind == "shield":
                origin = [bx0 / R, by0 / R, bz0 / R]
            else:
                origin = [PIVOT[0] + bx0 / R, PIVOT[1] + by0 / R, PIVOT[2] + bz0 / R]
            cubes_json.append({"origin": [round(o, 4) for o in origin],
                               "size": [round((bx1 - bx0 + 1) / R, 4), round((by1 - by0 + 1) / R, 4), round((bz1 - bz0 + 1) / R, 4)],
                               "uv": uv})
    # glow mask uses the same atlas positions: pack once, then paint the glowing patches
    tex = atlas.pack()
    gtex = None
    if glow:
        gtex = Image.new("RGBA", tex.size, (0, 0, 0, 0))
        for slot, gimg, _ in glow_patches:
            if gimg is not None:
                gtex.paste(gimg, tuple(slot["uv"]))
    bone = {"name": "weapon", "pivot": [0, 0, 0] if kind == "shield" else PIVOT, "cubes": cubes_json}
    if kind != "shield":
        bone["rotation"] = [0, 0, -45]
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{wid}", "texture_width": tex.width, "texture_height": tex.height,
                        "visible_bounds_width": 6, "visible_bounds_height": 6, "visible_bounds_offset": [0, 0, 0]},
        "bones": [bone]}]}
    for sub in ("geo/item/weapon", "textures/item/weapon", "animations/item/weapon", "models/item"):
        (ASSETS / sub).mkdir(parents=True, exist_ok=True)
    (ASSETS / f"geo/item/weapon/{wid}.geo.json").write_text(json.dumps(geo, separators=(",", ":")))
    tex.save(ASSETS / f"textures/item/weapon/{wid}.png")
    if gtex:
        gtex.save(ASSETS / f"textures/item/weapon/{wid}_glow.png")
    (ASSETS / f"animations/item/weapon/{wid}.animation.json").write_text(json.dumps({"format_version": "1.8.0", "animations": {}}))
    model = {"parent": "builtin/entity", "gui_light": "front",
             "display": shield_display() if kind == "shield" else handheld_display(length)}
    (ASSETS / f"models/item/{wid}.json").write_text(json.dumps(model, indent=2) + "\n")
    print(f"{wid}: {len(cubes_json)} cubes, {R:.2f} voxels/px, texture {tex.width}x{tex.height}{', glowing' if glow else ''}")


def test_variants():
    """Render-test-only item models. a: current transforms; b: right/left hand rotations swapped (cancels a
    left-right mirror between our models and vanilla sprites); c: b with the first-person ones left unswapped."""
    base = handheld_display(24)
    swap = json.loads(json.dumps(base))
    for k in ("thirdperson", "firstperson"):
        r, l = swap[k + "_righthand"]["rotation"], swap[k + "_lefthand"]["rotation"]
        swap[k + "_righthand"]["rotation"], swap[k + "_lefthand"]["rotation"] = l, r
    third_only = json.loads(json.dumps(swap))
    third_only["firstperson_righthand"] = base["firstperson_righthand"]
    third_only["firstperson_lefthand"] = base["firstperson_lefthand"]
    for name, disp in (("test_view_a", base), ("test_view_b", swap), ("test_view_c", third_only)):
        (ASSETS / f"models/item/{name}.json").write_text(json.dumps(
            {"parent": "builtin/entity", "gui_light": "front", "display": disp}, indent=2) + "\n")


def main():
    for wid, (fn, grip, length, kind) in WEAPONS.items():
        export(wid, fn, grip, length, kind)
    test_variants()


if __name__ == "__main__":
    main()
