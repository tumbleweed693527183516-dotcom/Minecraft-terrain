#!/usr/bin/env python3
"""
Builds build/VividLands-TestPack-<version>.mrpack: a Modrinth modpack for testing.
Import it in the Modrinth App (or Prism Launcher). It downloads performance mods,
Iris + Complementary Reimagined shaders, Distant Horizons and two vanilla-style
resource packs, and includes the Vivid Lands jar with everything pre-enabled.

    gradle build && python3 tools/testpack.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build"
VERSION = (ROOT / "VERSION").read_text().strip()
CDN = "https://cdn.modrinth.com/data"

# (folder, filename, url, size, sha1, sha512, needed on a server too)
FILES = [
    # --- core ---
    ("mods", "fabric-api-0.92.12+1.20.1.jar", f"{CDN}/P7dR8mSH/versions/rvI2dfzR/fabric-api-0.92.12%2B1.20.1.jar",
     2137232, "3e9cdd3e2f827ca9a259df9eb8e31949437b6bd4",
     "de9da2344043b3e9ef9fb7dbfff5f2577b06000c4f73f2a37959a80123141169084cece19133bd299b45feaaa4648bdaca2ea085684888cc8c55cc9134a477ca", True),
    # --- performance ---
    ("mods", "sodium-fabric-0.5.13+mc1.20.1.jar", f"{CDN}/AANobbMI/versions/OihdIimA/sodium-fabric-0.5.13%2Bmc1.20.1.jar",
     971552, "bcdbf37d9494e405cba210d7a80ed58e756297b5",
     "81c64f9c2d3402dfa43ee54d8f5a054f5243bfb08984e3addcab9fe885073c79c43c1c8c41e8f30b625d26a656f82a8e5f370bbbbf222ff1c08f4b324edb7ea4", False),
    ("mods", "indium-1.0.36+mc1.20.1.jar", f"{CDN}/Orvt0mRa/versions/nQHYSjxO/indium-1.0.36%2Bmc1.20.1.jar",
     105382, "d824614e7a173d273167969f427702f51846aca7",
     "7c5a1851f1fc08ae69318e151d07151fabba6cda2a24616c9251e1a4e5b969453e88b97d60f926271d60e3511bfc6fa05a64a108466efb7f29bec4519547e0c9", False),
    ("mods", "lithium-fabric-mc1.20.1-0.11.4.jar", f"{CDN}/gvQqBUqZ/versions/iEcXOkz4/lithium-fabric-mc1.20.1-0.11.4.jar",
     691483, "048227ed60a3005cf9fa55880dfe0cf20b0ba680",
     "31938b7e849609892ffa1710e41f2e163d11876f824452540658c4b53cd13c666dbdad8d200989461932bd9952814c5943e64252530c72bdd5d8641775151500", True),
    ("mods", "c2me-fabric-mc1.20.1-0.2.0+alpha.11.18.jar",
     f"{CDN}/VSNURh3q/versions/fyt7FtgA/c2me-fabric-mc1.20.1-0.2.0%2Balpha.11.18.jar",
     1426510, "ffeeafb265d7f0914e9b96ab70a1181d3642773a",
     "5068a570cde47f105ec17bde14d0004c5f5d3f73b89d8e23a8ac5955a35f4a0dc59ff1d9e0626bfb29e04a7329dc0e9e089f41d637aff6843a6cd43d0573ece9", True),
    ("mods", "ferritecore-6.0.1-fabric.jar", f"{CDN}/uXXizFIs/versions/unerR5MN/ferritecore-6.0.1-fabric.jar",
     125197, "8fa3b84fc5860dbc30fdf8cced02af68dffcf3fa",
     "9b7dc686bfa7937815d88c7bbc6908857cd6646b05e7a96ddbdcada328a385bd4ba056532cd1d7df9d2d7f4265fd48bd49ff683f217f6d4e817177b87f6bc457", True),
    ("mods", "modernfix-fabric-5.25.2+mc1.20.1.jar", f"{CDN}/nmDcB62a/versions/rPmgLeZC/modernfix-fabric-5.25.2%2Bmc1.20.1.jar",
     545175, "be03b9eb570c1e9df7593e68623f0fecbd039460",
     "878e39d182767ffd08ad6a3539fae780739129db133abe02b9b73dc3df6e1ac9ddbe509620356b0aae5e7bfbed535d0e18741703334317a16fefef820269da2d", True),
    ("mods", "ImmediatelyFast-Fabric-1.5.5+1.20.4.jar", f"{CDN}/5ZwdcRci/versions/iwYUrQJO/ImmediatelyFast-Fabric-1.5.5%2B1.20.4.jar",
     348818, "9f0110b60dc752ca093f2fc10a72d221b6dc8ac3",
     "8733e4f1fcd64581979f93f2580ae9f530e64ba21e90b2a46d4c1bdcb802e5a53a49a160e4dae06ec9e4d7829ea34715c9c9e1c2bfd7238b4de7fccfbc482ffd", False),
    ("mods", "entityculling-fabric-1.11.3-mc1.20.1.jar",
     f"{CDN}/NNAgCjsB/versions/xSrd3qsM/entityculling-fabric-1.11.3-mc1.20.1.jar",
     1516696, "42d17e5455f5015fa9b9c918a9b599683ff83f1c",
     "6bb4af050ec3bb5f4e2f76b33abc2bb6e0096c94849ba728979200beddeed8b2c3a5a962ecbec9cf79f11a99ba996a847814f1aabdb8ffad54105800fc0fed72", False),
    ("mods", "dynamic-fps-3.11.4+minecraft-1.20.0-fabric.jar",
     f"{CDN}/LQ3K71Q1/versions/QwPQBhiQ/dynamic-fps-3.11.4%2Bminecraft-1.20.0-fabric.jar",
     223261, "38196ee5bcfb3605f9bb9e52a45916b250216313",
     "3689a13abe56e02adc3ee96bb0426b185c7ae02588bbea1a3f350414768c260d0436682a7f59418bdd62306bc486af0b6184a24c50666e47b662993d2b789a14", False),
    # --- visuals ---
    ("mods", "iris-1.7.6+mc1.20.1.jar", f"{CDN}/YL57xq9U/versions/s5eFLITc/iris-1.7.6%2Bmc1.20.1.jar",
     2726899, "880c0b9ce38bb4997645793407c1801df83f4233",
     "f1337b0441c31269bd3bfcb28647d521326a83e73128c1ac8d065615f8a5a4ca1e8c96a468b356584236ece5b164ec8d8a52b1878064f4e391ecf4f32885e301", False),
    ("mods", "DistantHorizons-3.3.3-1.20.1-fabric-forge.jar",
     f"{CDN}/uCdwusMi/versions/6UnEfsRQ/DistantHorizons-3.3.3-1.20.1-fabric-forge.jar",
     27700542, "5447c4716571bfdba817c85278a9ce0d411573ec",
     "2ac0a2fd34fe17bb3a3764bb53838f00595998a7e0b4bd70c5068aa9244626c6b0e622af548f97a1614dbb0b7c3df29b6d313edfc890d572dc361591c2a176c0", True),
    ("mods", "entity_texture_features-7.2.5-1.20.1-fabric.jar",
     f"{CDN}/BVzZfTc1/versions/XtfsASE0/entity_texture_features-7.2.5-1.20.1-fabric.jar",
     807756, "b5d1de5452a58485d52843936a36361e5f27ac43",
     "dc3e632a74d03941c923ef48be2ca7189957152a8e6c84864d7be982ede682f29ccdb47277bbd7f7eb3d48a4479ca50f937b8925ca2c287c54b62a1f387e7c7d", False),
    ("mods", "entity_model_features-3.3.11-1.20.1-fabric.jar",
     f"{CDN}/4I1XuqiY/versions/rQLv8RBX/entity_model_features-3.3.11-1.20.1-fabric.jar",
     651739, "f9905c6b030413c37c1dcbdcc5b7d0d8ec446b86",
     "2ca796bb0f7ccade70a1151bd7e60f4d8b0c6861076d5fc5c9b7736707ad06786d4c94e04b7d19613ace1d443847dba86b59dbade1e16e2eac8e23d1fe266700", False),
    ("shaderpacks", "ComplementaryReimagined_r5.9.3.zip",
     f"{CDN}/HVnmMxH1/versions/Bqen1mJX/ComplementaryReimagined_r5.9.3.zip",
     553397, "838139b54cddb56b2e83cd260d8efd960ac536d6",
     "45304b1d7862afdb2177b7e6226fc9c6737911d17a4ad46cc9c519ca4deb935f05072cd337cd8b19a15bb8062b57b54eceec7bdee4cd572d94858e2946d37d85", False),
    ("resourcepacks", "FreshAnimations_v1.10.4.zip", f"{CDN}/50dA9Sha/versions/xN57JJts/FreshAnimations_v1.10.4.zip",
     850941, "73db740a6868e043c5e615c036fca2c912615b6e",
     "41258f9bea1a773d823f9a014d0c08206e9e7b339bc538e1538211fff28fadd06878a836d292cbb636ed6829cd2801a509368ae3eb3ad4bedf42190a0d5f7a90", False),
    ("resourcepacks", "Better-Leaves-9.6.zip", f"{CDN}/uvpymuxq/versions/w4ReEpuG/Better-Leaves-9.6.zip",
     1977146, "fa3a961b82a9f15a4e80b1f7f021bc121649f073",
     "793dacaca4c200656e8875195e42975ecb628af114e13aad2059368b51cf45f00280f86075368e9adf492e847718a9d593bdf481664e10cf1aa9628d2a51a8d6", False),
]

# Starting settings for a fresh instance: resource packs on, shader on, smooth biome blending,
# a moderate render distance (Distant Horizons draws the far terrain cheaply).
OPTIONS = """version:3465
resourcePacks:["vanilla","fabric","file/FreshAnimations_v1.10.4.zip","file/Better-Leaves-9.6.zip"]
biomeBlendRadius:7
graphicsMode:1
renderDistance:12
simulationDistance:8
"""
IRIS = """enableShaders=true
shaderPack=ComplementaryReimagined_r5.9.3.zip
"""


def main():
    files = []
    for folder, name, url, size, sha1, sha512, server in FILES:
        assert len(sha1) == 40 and len(sha512) == 128, name
        int(sha1, 16), int(sha512, 16)
        files.append({"path": f"{folder}/{name}", "hashes": {"sha1": sha1, "sha512": sha512},
                      "env": {"client": "required", "server": "required" if server else "unsupported"},
                      "downloads": [url], "fileSize": size})
    index = {
        "formatVersion": 1, "game": "minecraft", "versionId": VERSION,
        "name": "Vivid Lands Test Pack",
        "summary": "Vivid Lands world generation with performance mods, shaders, Distant Horizons and resource packs",
        "files": files,
        "dependencies": {"minecraft": "1.20.1", "fabric-loader": "0.16.10"},
    }
    jar = ROOT / "build" / "libs" / f"vividlands-{VERSION}.jar"
    OUT.mkdir(exist_ok=True)
    out = OUT / f"VividLands-TestPack-{VERSION}.mrpack"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        z.write(jar, f"overrides/mods/{jar.name}")
        z.writestr("overrides/options.txt", OPTIONS)
        z.writestr("overrides/config/iris.properties", IRIS)
    print(f"Built {out.name} ({len(files)} downloads)")


if __name__ == "__main__":
    main()
