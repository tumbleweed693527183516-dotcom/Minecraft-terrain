#!/usr/bin/env python3
"""
Builds build/VividLands-TestPack-<version>.mrpack: a Modrinth modpack for testing.
Import it in the Modrinth App (or Prism Launcher). It downloads Fabric API, Sodium, Indium,
Iris and Distant Horizons for 1.20.1 and includes the Vivid Lands jar.

    python3 tools/build.py && python3 tools/testpack.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build"
VERSION = (ROOT / "VERSION").read_text().strip()

MODS = [
    ("fabric-api-0.92.12+1.20.1.jar",
     "https://cdn.modrinth.com/data/P7dR8mSH/versions/rvI2dfzR/fabric-api-0.92.12%2B1.20.1.jar", 2137232,
     "3e9cdd3e2f827ca9a259df9eb8e31949437b6bd4",
     "de9da2344043b3e9ef9fb7dbfff5f2577b06000c4f73f2a37959a80123141169084cece19133bd299b45feaaa4648bdaca2ea085684888cc8c55cc9134a477ca"),
    ("sodium-fabric-0.5.13+mc1.20.1.jar",
     "https://cdn.modrinth.com/data/AANobbMI/versions/OihdIimA/sodium-fabric-0.5.13%2Bmc1.20.1.jar", 971552,
     "bcdbf37d9494e405cba210d7a80ed58e756297b5",
     "81c64f9c2d3402dfa43ee54d8f5a054f5243bfb08984e3addcab9fe885073c79c43c1c8c41e8f30b625d26a656f82a8e5f370bbbbf222ff1c08f4b324edb7ea4"),
    ("indium-1.0.36+mc1.20.1.jar",
     "https://cdn.modrinth.com/data/Orvt0mRa/versions/nQHYSjxO/indium-1.0.36%2Bmc1.20.1.jar", 105382,
     "d824614e7a173d273167969f427702f51846aca7",
     "7c5a1851f1fc08ae69318e151d07151fabba6cda2a24616c9251e1a4e5b969453e88b97d60f926271d60e3511bfc6fa05a64a108466efb7f29bec4519547e0c9"),
    ("iris-1.7.6+mc1.20.1.jar",
     "https://cdn.modrinth.com/data/YL57xq9U/versions/s5eFLITc/iris-1.7.6%2Bmc1.20.1.jar", 2726899,
     "880c0b9ce38bb4997645793407c1801df83f4233",
     "f1337b0441c31269bd3bfcb28647d521326a83e73128c1ac8d065615f8a5a4ca1e8c96a468b356584236ece5b164ec8d8a52b1878064f4e391ecf4f32885e301"),
    ("DistantHorizons-3.3.3-1.20.1-fabric-forge.jar",
     "https://cdn.modrinth.com/data/uCdwusMi/versions/6UnEfsRQ/DistantHorizons-3.3.3-1.20.1-fabric-forge.jar",
     27700542,
     "5447c4716571bfdba817c85278a9ce0d411573ec",
     "2ac0a2fd34fe17bb3a3764bb53838f00595998a7e0b4bd70c5068aa9244626c6b0e622af548f97a1614dbb0b7c3df29b6d313edfc890d572dc361591c2a176c0"),
]


def main():
    files = []
    for name, url, size, sha1, sha512 in MODS:
        assert len(sha1) == 40 and len(sha512) == 128, name
        int(sha1, 16), int(sha512, 16)
        files.append({"path": f"mods/{name}", "hashes": {"sha1": sha1, "sha512": sha512},
                      "env": {"client": "required", "server": "optional" if name.startswith(("sodium", "iris", "indium"))
                              else "required"},
                      "downloads": [url], "fileSize": size})
    index = {
        "formatVersion": 1, "game": "minecraft", "versionId": VERSION,
        "name": "Vivid Lands Test Pack",
        "summary": "Vivid Lands world generation with Sodium, Iris and Distant Horizons",
        "files": files,
        "dependencies": {"minecraft": "1.20.1", "fabric-loader": "0.16.10"},
    }
    jar = OUT / f"vividlands-{VERSION}.jar"
    out = OUT / f"VividLands-TestPack-{VERSION}.mrpack"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        z.write(jar, f"overrides/mods/{jar.name}")
    print(f"Built {out.name}")


if __name__ == "__main__":
    main()
