"""Builds questbook_preview.html: a browsable copy of the quest book (data in quests.py)."""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from quests import BOSS, MAIN, SIDE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ITEMS = ROOT / "ragnarok/src/main/resources/assets/vividlands_ragnarok/textures/item"
PORTRAITS = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/portraits")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/questbook_preview.html")


def b64(p):
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


icons, portraits = {}, {}
chapters = []
for group, lst in (("main", MAIN), ("side", SIDE)):
    for ch in lst:
        qs = []
        for qd in ch["quests"]:
            qd = dict(qd)
            if qd["kind"] == "boss":
                name, hp, where, unlock, drop, icon, moves, p2, tip = BOSS[qd["id"]]
                qd.update(title=name.split(",")[0], full=name, hp=hp, where=where, unlock=unlock, drop=drop,
                          icon="item:" + icon, moves=moves, phase2=p2, tip=tip)
                portraits[qd["id"]] = b64(PORTRAITS / f"{qd['id']}.png")
            if qd["icon"].startswith("item:"):
                key = qd["icon"][5:]
                icons[key] = b64(ITEMS / f"{key}.png")
            qs.append(qd)
        chapters.append({"id": ch["id"], "group": group, "name": ch["name"], "sub": ch["sub"],
                         "patron": ch.get("patron"), "acts": ch.get("acts", False), "quests": qs})

data = json.dumps({"chapters": chapters, "icons": icons, "portraits": portraits}, ensure_ascii=False)
html = (Path(__file__).parent / "preview_template.html").read_text().replace("/*DATA*/null", data)
OUT.write_text(html)
print(OUT, len(html) // 1024, "KB")
