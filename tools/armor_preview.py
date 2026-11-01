"""Contact sheet of the ancient armor sets on a plain mannequin: python3 tools/armor_preview.py [out.png] [ids...]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ancient_armor import SETS, GEO_DIR, TEX_DIR  # noqa: E402
from boss_preview import view  # noqa: E402

_S = [((-4, 24, -4), (4, 32, 4)), ((-4, 12, -2), (4, 24, 2)), ((-8, 12, -2), (-4, 24, 2)), ((4, 12, -2), (8, 24, 2)),
      ((-4, 0, -2), (0, 12, 2)), ((0, 0, -2), (4, 12, 2))]
SKIN = [(tuple(v + 0.35 for v in a), tuple(v - 0.35 for v in b)) for a, b in _S]     # a little inside the armour


def with_mannequin(geo, tex):
    g = json.loads(json.dumps(geo))
    G = g["minecraft:geometry"][0]
    tw, th = G["description"]["texture_width"], G["description"]["texture_height"]
    ppu = tex.shape[1] / tw
    t = np.concatenate([tex, np.zeros((int(4 * ppu), tex.shape[1], 4), np.uint8)], 0)
    t[-int(4 * ppu):, :int(4 * ppu)] = (150, 150, 158, 255)
    G["description"]["texture_height"] = th + 4
    cubes = []
    for a, b in SKIN:
        size = [b[i] - a[i] for i in range(3)]
        cubes.append({"origin": list(a), "size": size, "uv": {f: {"uv": [0, th], "uv_size": [1, 1]} for f in
                                                               ("north", "south", "east", "west", "up", "down")}})
    G["bones"].append({"name": "mannequin", "pivot": [0, 0, 0], "cubes": cubes})
    return g, t


def sheet(out, ids=None, cols=6, S=260, both=False):
    sets = [s for s in SETS if not ids or s["id"] in ids]
    rows = (len(sets) + cols - 1) // cols
    img = Image.new("RGB", (cols * S, rows * (S + 20)), (150, 185, 225))
    d = ImageDraw.Draw(img)
    for i, s in enumerate(sets):
        geo = json.loads((GEO_DIR / f"{s['id']}.geo.json").read_text())
        tex = np.asarray(Image.open(TEX_DIR / f"{s['id']}.png").convert("RGBA"))
        g, t = with_mannequin(geo, tex)
        ppu = tex.shape[1] / geo["minecraft:geometry"][0]["description"]["texture_width"]
        x, y = (i % cols) * S, (i // cols) * (S + 20)
        if both:
            img.paste(view(g, t, ppu, 25, S // 2 * 2).resize((S // 2, S)), (x, y + 20))
            img.paste(view(g, t, ppu, 205, S // 2 * 2).resize((S // 2, S)), (x + S // 2, y + 20))
        else:
            img.paste(view(g, t, ppu, 25, S), (x, y + 20))
        d.text((x + 6, y + 4), f"{i + 1}. {s['title']} ({s['civ']})", fill=(20, 20, 30))
    img.save(out)


if __name__ == "__main__":
    sheet(sys.argv[1] if len(sys.argv) > 1 else "/tmp/armor.png", sys.argv[2:] or None, both=True, cols=7, S=300)
