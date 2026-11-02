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
                         "patron": ch.get("patron"), "acts": ch.get("acts", False), "tab": ch.get("tab"),
                         "labels": ch.get("labels"), "quests": qs})

# armor guide: bands, sets, recipes and set bonuses, read from the generators and ArmorTraits.java
import re
java = (ROOT / "ragnarok/src/main/java/com/vividlands/ragnarok/armor/ArmorTraits.java").read_text()
trait_text = {m[0]: (m[1], m[2]) for m in re.findall(r'(\w+)\("([^"]+)", "([^"]+)"\)', java)}
trait_of = dict(re.findall(r'Map\.entry\("(\w+)", Trait\.(\w+)\)', java))
civ = dict(re.findall(r'new Set\("(\w+)", "([^"]+)"\)', (ROOT / "ragnarok/src/main/java/com/vividlands/ragnarok/armor/AncientSets.java").read_text()))
recipes = {}
for f in (ROOT / "ragnarok/src/main/resources/data/vividlands_ragnarok/recipes/ancient").glob("*_helmet.json"):
    r = json.loads(f.read_text()); k = r["key"]
    recipes[f.name[:-12]] = (k["M"]["item"].split(":")[1], (k["T"].get("item") or k["T"].get("tag")).split(":")[1], k["D"]["item"].split(":")[1])
BANDS = [(1, 5, 1, "Act I"), (6, 15, 2, "Act II"), (16, 25, 3, "Act III"), (26, 35, 4, "Act IV"), (36, 40, 5, "Sleipnir"),
         (41, 42, 6, "Garmr"), (43, 44, 7, "Fafnir"), (45, 46, 8, "Jormungandr"), (47, 49, 9, "Fenrir")]
order = list(civ)
armor = {"bands": [], "traits": [{"id": k, "title": v[0], "text": v[1]} for k, v in trait_text.items()]}
for a, b, ward, stage in BANDS:
    sets = []
    for t in range(a, b + 1):
        sid = order[t - 1]
        m, tr, dye = recipes[sid]
        icon = f"{sid}_helmet"
        icons[icon] = b64(ITEMS / f"{icon}.png")
        tot = sum(round(lo + (hi - lo) * (t - 1) / 48) for lo, hi in ((2, 4), (4, 9), (3, 7), (2, 4)))
        sets.append({"tier": t, "id": sid, "civ": civ[sid], "icon": icon, "trait": trait_of.get(sid, "PHALANX"),
                     "armor": tot, "tough": round((t - 1) * 6 / 48 * 2) / 2, "metal": m.replace("_", " "),
                     "trophy": {"trophies/act1": "Act I trophy", "trophies/act2": "Act II trophy", "trophies/act3": "Act III trophy",
                                "trophies/act4": "Act IV trophy"}.get(tr, tr.replace("_", " ")), "dye": dye.replace("_dye", "").replace("_", " ")})
    armor["bands"].append({"ward": ward, "stage": stage, "sets": sets})
# classes guide, read from NorseClass.java
nc = (ROOT / "ragnarok/src/main/java/com/vividlands/ragnarok/classes/NorseClass.java").read_text()
classes = []
for m in re.finditer(r'(\w+)\("(\w+)", "([^"]+)", 0x([0-9A-F]+), "([^"]+)", "([^"]+)",\s*List\.of\((.*?)\)\)\)', nc, re.S):
    abil = [{"name": a[0], "level": int(a[1]), "cd": int(a[2]), "text": a[3]}
            for a in re.findall(r'new Ability\("([^"]+)", (\d+), (\d+), "([^"]+)"', m.group(7))]
    icons[f"{m.group(2)}_rune"] = b64(ITEMS / f"{m.group(2)}_rune.png")
    classes.append({"id": m.group(2), "title": m.group(3), "color": "#" + m.group(4), "passive": m.group(5),
                    "passiveText": m.group(6), "abilities": abil})
data = json.dumps({"classes": classes, "armor": armor, "chapters": chapters, "icons": icons, "portraits": portraits}, ensure_ascii=False)
html = (Path(__file__).parent / "preview_template.html").read_text().replace("/*DATA*/null", data)
OUT.write_text(html)
print(OUT, len(html) // 1024, "KB")
