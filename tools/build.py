#!/usr/bin/env python3
"""
Packages Vivid Lands into:
  build/vividlands-<version>.jar          Fabric 1.20.1 mod (needs Fabric API)
  build/VividLands-datapack-<version>.zip plain datapack (vanilla, Forge, Fabric)

    python3 tools/build.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "src" / "main" / "resources"
OUT = ROOT / "build"
VERSION = (ROOT / "VERSION").read_text().strip()


def files_under(*dirs):
    for d in dirs:
        for p in sorted((RES / d).rglob("*")):
            if p.is_file():
                yield p


def build():
    OUT.mkdir(exist_ok=True)
    jar = OUT / f"vividlands-{VERSION}.jar"
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
        meta = json.loads((RES / "fabric.mod.json").read_text().replace("${version}", VERSION))
        z.writestr("fabric.mod.json", json.dumps(meta, indent=2))
        z.write(RES / "pack.mcmeta", "pack.mcmeta")
        for p in files_under("data", "assets"):
            z.write(p, p.relative_to(RES).as_posix())
    pack = OUT / f"VividLands-datapack-{VERSION}.zip"
    with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(RES / "pack.mcmeta", "pack.mcmeta")
        z.write(RES / "assets" / "vividlands" / "icon.png", "pack.png")
        for p in files_under("data"):
            z.write(p, p.relative_to(RES).as_posix())
    print(f"Built {jar.name} and {pack.name}")


if __name__ == "__main__":
    build()
