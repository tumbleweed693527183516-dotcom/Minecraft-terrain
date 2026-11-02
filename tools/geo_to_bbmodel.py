"""
Rebuilds the Blockbench source of an armor set (tools/models/armor/<id>.bbmodel) from the model the game uses
(geo/item/armor/<id>.geo.json) and its texture, so the two never drift apart. Keeps the file's other settings.

    python3 tools/geo_to_bbmodel.py agamemnon [more ids...]

Bedrock geometry is mirrored on X compared with Blockbench's own coordinates: a cube's x range, its pivot and its
X/Y rotation flip sign; face names stay the same.
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "ragnarok/src/main/resources/assets/vividlands_ragnarok"


def uid(*parts):
    h = hashlib.md5("/".join(map(str, parts)).encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def r(v):
    return round(v, 4)


def convert(set_id):
    out = ROOT / f"tools/models/armor/{set_id}.bbmodel"
    bb = json.loads(out.read_text())
    geo = json.loads((RES / f"geo/item/armor/{set_id}.geo.json").read_text())["minecraft:geometry"][0]
    elements, groups, outliner = [], [], []
    for bone in geo["bones"]:
        px, py, pz = bone.get("pivot", [0, 0, 0])
        g = dict(bb["groups"][0]) if bb.get("groups") else {}
        g.update(name=bone["name"], uuid=uid(set_id, bone["name"]), origin=[r(-px), r(py), r(pz)],
                 rotation=[-bone.get("rotation", [0, 0, 0])[0], -bone.get("rotation", [0, 0, 0])[1], bone.get("rotation", [0, 0, 0])[2]])
        groups.append(g)
        kids = []
        for i, c in enumerate(bone.get("cubes", [])):
            (ox, oy, oz), (sx, sy, sz) = c["origin"], c["size"]
            faces = {}
            for face, f in c["uv"].items():
                (u, v), (w, h) = f["uv"], f["uv_size"]
                faces[face] = {"uv": [r(min(u, u + w)), r(min(v, v + h)), r(max(u, u + w)), r(max(v, v + h))], "texture": 0}
            e = {"name": bone["name"], "box_uv": False, "render_order": "default", "locked": False, "export": True, "scope": 0,
                 "allow_mirror_modeling": True, "from": [r(-(ox + sx)), r(oy), r(oz)], "to": [r(-ox), r(oy + sy), r(oz + sz)],
                 "autouv": 0, "color": 0, "origin": [0, 0, 0], "faces": faces, "type": "cube", "uuid": uid(set_id, bone["name"], i)}
            if "rotation" in c:
                cpx, cpy, cpz = c.get("pivot", [0, 0, 0])
                e["rotation"] = [-c["rotation"][0], -c["rotation"][1], c["rotation"][2]]
                e["origin"] = [r(-cpx), r(cpy), r(cpz)]
            if c.get("inflate"):
                e["inflate"] = c["inflate"]
            elements.append(e)
            kids.append(e["uuid"])
        outliner.append({"uuid": g["uuid"], "isOpen": False, "children": kids})
    bb.update(elements=elements, groups=groups, outliner=outliner)
    tex = RES / f"textures/item/armor/{set_id}.png"
    bb["textures"][0]["source"] = "data:image/png;base64," + base64.b64encode(tex.read_bytes()).decode()
    bb["textures"][0].update(uv_width=geo["description"]["texture_width"], uv_height=geo["description"]["texture_height"])
    out.write_text(json.dumps(bb, separators=(",", ":")))
    print(out.relative_to(ROOT), len(elements), "cubes")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        convert(s)
