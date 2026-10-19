#!/usr/bin/env python3
"""
Assets for the bosses of Vivid Lands: Ragnarok:
  - names (boss bars, messages, trophies, the Bleeding effect, the gamerule) merged into en_us.json
  - item models and 16x16 icons for the Chapter 1 trophies
  - the 18x18 Bleeding effect icon
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NS = "vividlands_ragnarok"
ASSETS = ROOT / "ragnarok/src/main/resources/assets" / NS

BOSSES = {
    "cave_bear": "Cave Bear, Den-Mother of the Pines",
    "irish_elk": "Great Irish Elk, Lord of the Moors",
    "hippo": "Hippopotamus, Terror of the Oasis",
    "crocodile": "Giant Crocodile, the River's Jaws",
    "silverback": "Silverback, King of the Temple",
    "saber_tooth": "Saber-tooth, the Unseen Hunter",
    "woolly_rhino": "Woolly Rhinoceros, the Tundra Ram",
    "elephant": "Bull Elephant, Thunder of the Savanna",
    "bull_shark": "Giant Bull Shark, Blood in the Water",
    "mammoth": "Woolly Mammoth, Skadi's Last Trial",
}

TROPHIES = {
    "great_antlers": "Great Antlers",
    "hippo_hide": "Hippo Hide",
    "croc_scales": "Crocodile Scales",
    "silverback_fist": "Silverback Fist",
    "rhino_horn": "Rhino Horn",
    "ivory": "Ivory",
    "shark_tooth": "Shark Tooth",
    "mammoth_tusk": "Mammoth Tusk",
    "frozen_heart": "Frozen Heart",
}

LANG = {
    "boss.vividlands_ragnarok.enraged": "%s is enraged!",
    "boss.vividlands_ragnarok.slain": "%s has been slain!",
    "boss.vividlands_ragnarok.trials": "Skadi's trials: %s of %s complete",
    "boss.vividlands_ragnarok.locked": "%s is watching you... prove yourself in other trials first.",
    "effect.vividlands_ragnarok.bleeding": "Bleeding",
    "entity.vividlands_ragnarok.boulder": "Boulder",
    "gamerule.vividlandsBossSpawning": "Bosses appear in the wild",
}


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mul(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def noise(x, y):
    n = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n & 0xFFFF) / 65535.0


def canvas(size=16):
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def outline(img, color=(30, 22, 18)):
    """Dark 1-pixel outline around the shape (reads well in the inventory)."""
    src = img.copy()
    s, d = src.load(), img.load()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            if s[x, y][3]:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and s[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                d[x, y] = color + (255,)
    return img


def antlers():
    img, base = canvas(), hexc("#c8b28a")
    d = img.load()
    def line(x0, y0, x1, y1):
        n = max(abs(x1 - x0), abs(y1 - y0)) + 1
        for i in range(n):
            x = round(x0 + (x1 - x0) * i / max(1, n - 1))
            y = round(y0 + (y1 - y0) * i / max(1, n - 1))
            d[x, y] = mul(base, 0.85 + 0.3 * noise(x, y)) + (255,)
    line(7, 13, 7, 9); line(8, 13, 8, 9)
    for side in (-1, 1):
        cx = 7.5 + side * 0.5
        line(int(cx), 9, int(cx + side * 5), 5)              # main beam
        line(int(cx + side * 5), 5, int(cx + side * 6), 2)
        line(int(cx + side * 2), 8, int(cx + side * 2), 4)   # tines
        line(int(cx + side * 4), 6, int(cx + side * 3), 2)
        line(int(cx + side * 5), 5, int(cx + side * 6), 5)
    for x, y in ((7, 13), (8, 13), (7, 14), (8, 14)):
        d[x, y] = (110, 82, 56, 255)
    return outline(img)


def hide(color, spots=None):
    img, base = canvas(), hexc(color)
    d = img.load()
    for x in range(16):
        for y in range(16):
            inside = (2 <= x <= 13 and 3 <= y <= 12) or (x in (1, 14) and y in (4, 5, 10, 11)) or (y == 13 and 4 <= x <= 11)
            if inside:
                f = 0.8 + 0.35 * noise(x // 2, y)
                if spots and noise(x * 3, y * 5) > 0.86:
                    f *= 0.7
                d[x, y] = mul(base, f) + (255,)
    return outline(img)


def scales():
    img, base = canvas(), hexc("#4f6b38")
    d = img.load()
    for x in range(1, 15):
        for y in range(2, 14):
            if (x - 7.5) ** 2 / 46 + (y - 7.5) ** 2 / 34 > 1:
                continue
            row = y // 3
            u = (x + (row % 2) * 2) % 4
            v = y % 3
            f = 1.1 - 0.12 * v - (0.25 if u == 0 else 0)
            d[x, y] = mul(base, f * (0.9 + 0.2 * noise(x, y))) + (255,)
    return outline(img)


def fist():
    img = canvas()
    d = img.load()
    fur, skin = hexc("#3a3634"), hexc("#5a4a42")
    for x in range(3, 13):
        for y in range(4, 13):
            if (x in (3, 12) and y in (4, 12)):
                continue
            d[x, y] = (mul(skin, 0.85 + 0.25 * noise(x, y)) if y <= 7 else mul(fur, 0.8 + 0.4 * noise(x, y))) + (255,)
    for k in range(4):                                      # knuckles
        d[4 + k * 2, 4] = mul(skin, 1.25) + (255,)
        d[5 + k * 2, 5] = mul(skin, 0.7) + (255,)
    for y in range(13, 15):
        for x in range(5, 11):
            d[x, y] = (205, 205, 210, 255) if y == 13 else (150, 150, 158, 255)   # silver back fur at the wrist
    return outline(img)


def horn(color, length=12, curve=0.25, width=3):
    """A curved cone from the wide root (bottom left) to the tip (top right), shaded on one side."""
    img, base = canvas(), hexc(color)
    d = img.load()
    steps = 60
    for i in range(steps):
        t = i / (steps - 1)
        x0, y0, x1, y1 = 3.0, 13.0, 3.0 + length * 0.78, 13.0 - length * 0.85
        cx = x0 + (x1 - x0) * t + curve * 6 * math.sin(t * math.pi) * 0.7
        cy = y0 + (y1 - y0) * t + curve * 6 * math.sin(t * math.pi) * 0.7
        r = width * 0.5 * (1 - t) ** 0.8 + 0.35
        for x in range(16):
            for y in range(16):
                dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if dd <= r:
                    side = ((x + 0.5 - cx) - (y + 0.5 - cy)) / max(r, 0.5)
                    f = 1.05 - 0.25 * t + 0.18 * side + 0.08 * noise(x, y)
                    d[x, y] = mul(base, f) + (255,)
    for k in range(3):                                      # root band (where it was cut from the skull)
        x, y = 2 + k, 14 - k
        if 0 <= x < 16 and 0 <= y < 16:
            d[x, y] = mul(base, 0.55) + (255,)
    return outline(img)


def tooth():
    img, base = canvas(), hexc("#f2ecdc")
    d = img.load()
    for y in range(2, 14):
        half = max(0, round((y - 2) / 12 * 4.2))
        for x in range(8 - half, 8 + half + 1):
            d[x, y] = mul(base, 1.05 - 0.04 * abs(x - 8) + 0.06 * noise(x, y)) + (255,)
    for x in range(4, 13):                                  # serrated base and the cord it hangs on
        d[x, 14] = (120, 84, 52, 255)
    for x in range(5, 12, 2):
        d[x, 13] = mul(base, 0.8) + (255,)
    return outline(img)


def frozen_heart():
    img = canvas()
    d = img.load()
    for x in range(16):
        for y in range(16):
            u, v = (x - 7.5) / 6.2, -(y - 7.0) / 6.0
            if (u * u + v * v - 1) ** 3 - u * u * v ** 3 < 0:   # heart curve
                core = math.hypot(x - 7.5, y - 6.5)
                c = (150, 220, 255) if core > 3 else (225, 248, 255)
                if (x + y) % 5 == 0:
                    c = (110, 180, 235)
                d[x, y] = mul(c, 0.9 + 0.2 * noise(x, y)) + (255,)
    for x, y in ((5, 4), (6, 4), (5, 5)):
        d[x, y] = (255, 255, 255, 255)
    return outline(img, (20, 40, 70))


def bleeding_icon():
    img = canvas(18)
    d = img.load()
    for x in range(18):
        for y in range(18):
            u, v = (x - 8.5) / 5.5, (y - 10.5) / 5.5
            drop = (u * u + v * v < 1) or (y < 11 and abs(x - 8.5) < (y - 2) * 0.6)
            if drop and 2 <= y <= 16:
                c = (200, 20, 24) if x > 6 else (150, 10, 14)
                if (x, y) in ((7, 9), (7, 10), (6, 11)):
                    c = (255, 120, 120)
                d[x, y] = c + (255,)
    return outline(img, (40, 0, 0))


def main():
    tex = ASSETS / "textures/item"
    tex.mkdir(parents=True, exist_ok=True)
    icons = {
        "great_antlers": antlers(),
        "hippo_hide": hide("#7a6470", spots=True),
        "croc_scales": scales(),
        "silverback_fist": fist(),
        "rhino_horn": horn("#6b5a48", 11, -0.35, 6),
        "ivory": horn("#efe6cf", 13, 0.45, 4),
        "shark_tooth": tooth(),
        "mammoth_tusk": horn("#e2d3ae", 14, 0.9, 5),
        "frozen_heart": frozen_heart(),
    }
    models = ASSETS / "models/item"
    models.mkdir(parents=True, exist_ok=True)
    for name, img in icons.items():
        img.save(tex / f"{name}.png")
        (models / f"{name}.json").write_text(json.dumps(
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{name}"}}, indent=2) + "\n")
    eff = ASSETS / "textures/mob_effect"
    eff.mkdir(parents=True, exist_ok=True)
    bleeding_icon().save(eff / "bleeding.png")

    lang_file = ASSETS / "lang/en_us.json"
    lang = json.loads(lang_file.read_text()) if lang_file.exists() else {}
    for k, v in BOSSES.items():
        lang[f"boss.{NS}.{k}"] = v
    for k, v in TROPHIES.items():
        lang[f"item.{NS}.{k}"] = v
    lang.update(LANG)
    lang_file.write_text(json.dumps(dict(sorted(lang.items())), indent=2, ensure_ascii=False) + "\n")
    print(f"{len(BOSSES)} bosses, {len(icons)} trophies")


if __name__ == "__main__":
    main()
