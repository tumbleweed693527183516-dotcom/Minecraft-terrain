#!/usr/bin/env python3
"""
Builds build/VividLands-Modpack-<version>.mrpack: the Vivid Lands modpack.
Import it in the Modrinth App (or Prism Launcher). It downloads performance mods,
Iris + Complementary Reimagined shaders, Distant Horizons and two vanilla-style
resource packs, and includes the Vivid Lands jar with everything pre-enabled.

    gradle build && python3 tools/modpack.py
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
    ("shaderpacks", "ComplementaryReimagined_r5.9.3.zip",
     f"{CDN}/HVnmMxH1/versions/Bqen1mJX/ComplementaryReimagined_r5.9.3.zip",
     553397, "838139b54cddb56b2e83cd260d8efd960ac536d6",
     "45304b1d7862afdb2177b7e6226fc9c6737911d17a4ad46cc9c519ca4deb935f05072cd337cd8b19a15bb8062b57b54eceec7bdee4cd572d94858e2946d37d85", False),
]

# Resolved from Modrinth at build time (newest Fabric 1.20.1 release, plus required dependencies).
# The client set follows Fabulously Optimized's 1.20.1 pack (BSD-3, see pack/), minus FO's
# branding, capes, screenshot/LAN extras and resource-pack effect mods.  (project id, needed on a server)
RESOLVE = [
    # --- shared libraries first, so their newest versions win over older pinned dependencies ---
    ("WwbubTsV", True),   # YOSBR (default settings that never overwrite yours)
    ("9s6osm5g", True),   # Cloth Config
    ("1eAoo2KR", True),   # YetAnotherConfigLib (Armor of the Ages needs it on servers too)
    ("Ha28R6CL", True),   # Fabric Language Kotlin
    # --- Fabulously Optimized: performance ---
    ("PtjYWJkn", False),  # Sodium Extra
    ("Bh37bMuy", False),  # Reese's Sodium Options
    ("51shyZVL", False),  # MoreCulling
    ("OVuFYfre", False),  # Enhanced Block Entities
    ("NRjRiSSD", True),   # Memory Leak Fix
    ("QwxR6Gcd", True),   # Debugify (vanilla bug fixes)
    ("QdG47OkI", False),  # Model Gap Fix
    ("ZP7xHXtw", False),  # Remove Reloading Screen
    ("x1hIzbuY", False),  # FastQuit
    # --- Fabulously Optimized: quality of life and libraries ---
    ("1IjD5062", False),  # Continuity (connected textures)
    ("w7ThoJFB", False),  # Zoomify
    ("uLbm7CG6", False),  # Language Reload
    ("mOgUt4GM", False),  # Mod Menu
    ("G1epq3jN", False),  # AdvancementInfo
    ("kqJFAPU9", False),  # Better Mount HUD
    ("kYq5qkSL", False),  # Borderless Mining
    ("8qkXwOnk", False),  # More Chat History
    ("qQyHxfxd", True),   # No Chat Reports
    ("sGmHWmeL", True),   # MixinTrace (clearer crash reports when you add mods)
    # --- for Vivid Lands ---
    ("badoptimizations", False),
    ("chunky", True),                      # pre-generate the world: no generation lag while exploring
    ("oh-the-biomes-weve-gone", True),     # blocks Vivid Lands builds with
    # --- structures for the boss progression (see pack/MOD_LOG.md) ---
    ("mebahels-creatures-draugr", True),   # Draugr Bastion, Crypt, Fort, Tower (+ Mebahel's API, Elder Scrolls Core, GeckoLib)
    ("ancient-structures", True),          # Mayan temple (Gorilla) and other ancient sites (+ Dawn of Time, Armor of the Ages, Fusion)
    ("ancient-villages", False),           # Japanese-style villages in taiga; single-player only: its Garden Trails library crashes dedicated servers
    ("civilizations", True),               # Norse settlement (Geri and Freki), Bjorn Ironside and Loki
    ("lukis-grand-capitals", True),        # replaces vanilla villages with grand capitals
    ("mss-moogs-soaring-structures", True),     # sky islands (Sleipnir)
    ("when-dungeons-arise-seven-seas", True, "ZQjAxRej"),   # hostile ships (Jormungandr); the 1.20.x build
    ("yungs-better-strongholds", True),    # stronghold portal room: the gate of Hel (Garmr)
    ("small-ships", True),                 # sailable ships (Bull Shark, Jormungandr fights)
    # --- creatures whose models the bosses use ---
    ("naturalist", True, "3B6AIHXy"),      # 5.0pre4 beta: has the mammoth and moose (4.0.3 does not)
    ("animal-garden-western-gorilla", True),
    ("animal-garden-bull-shark", True),
    ("animal-garden-common-raven", True),
    ("fossils-and-archeology-revival", True),   # smilodon (Saber-tooth)
    ("backported-wolves", True),
    ("saints-dragons", True),              # Fafnir and Nidhoggr
    # --- tech ---
    ("create-fabric", True),               # Create: makes everything the closed Nether and End would give
    # --- ships: Small Ships on the sea, Valkyrien Skies + Eureka for airships (build any ship, add a helm and balloons) ---
    ("valkyrien-skies", True),
    ("eureka", True),
    # --- quality of life (the usual modpack set) ---
    ("emi", True),                         # recipe viewer (Create shows its machine recipes in it)
    ("jade", True),                        # what am I looking at: block/mob name, mod, health, machine status
    ("xaeros-minimap", False),             # minimap with waypoints and death point
    ("xaeros-world-map", False),           # full-screen world map
    ("appleskin", True),                   # food saturation and hunger previews
    ("mouse-tweaks", False),               # drag and scroll to move items
    ("inventory-profiles-next", False),    # sort inventories and chests, refill hotbar tools
    ("shulkerboxtooltip", False),          # see inside shulker boxes on hover
    ("enchantment-descriptions", False),   # what each enchantment does, in its tooltip
    ("controlling", False),                # search and fix clashing keybinds (lots of mods)
    ("waystones", True),                   # waystones for fast travel across a huge world
    ("travelersbackpack", True),           # backpacks
    ("carry-on", True),                    # pick up chests and animals
    ("universal-graves", True),            # your items wait in a grave when you die
    ("polymorph", True),                   # choose between recipes that share the same ingredients
    ("clumps", True),                      # merges XP orbs (less lag after boss fights)
]
API = "https://api.modrinth.com/v2"
LOADER_FALLBACK = "0.19.5"


def fabric_loader():
    """Newest stable Fabric Loader for 1.20.1 (newest mod releases often require it)."""
    import urllib.request
    try:
        req = urllib.request.Request("https://meta.fabricmc.net/v2/versions/loader/1.20.1",
                                     headers={"User-Agent": "vividlands-modpack"})
        for v in json.load(urllib.request.urlopen(req, timeout=30)):
            if v["loader"].get("stable"):
                return v["loader"]["version"]
    except Exception as e:
        print(f"warning: could not look up Fabric Loader ({e}); using {LOADER_FALLBACK}")
    return LOADER_FALLBACK
# Modrinth project ids of the pinned files above (never pull a second copy in as a dependency)
PINNED = {"P7dR8mSH", "AANobbMI", "Orvt0mRa", "gvQqBUqZ", "VSNURh3q", "uXXizFIs", "nmDcB62a", "5ZwdcRci",
          "NNAgCjsB", "LQ3K71Q1", "YL57xq9U", "uCdwusMi", "HVnmMxH1"}


def _get(path):
    import urllib.request
    req = urllib.request.Request(f"{API}{path}", headers={"User-Agent": "vividlands-testpack"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def _entry(v, server):
    f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
    return ("mods", f["filename"], f["url"], f["size"], f["hashes"]["sha1"], f["hashes"]["sha512"], server)


def resolve(slug, server, seen, version=None):
    """Latest Fabric 1.20.1 file for a Modrinth project (or an exact version) plus its required
    dependencies, however Modrinth lists them (by project or by version)."""
    import urllib.parse
    if version is None:
        q = urllib.parse.urlencode({"game_versions": '["1.20.1"]', "loaders": '["fabric"]'})
        versions = _get(f"/project/{slug}/version?{q}")
        if not versions:
            raise RuntimeError("no 1.20.1 fabric version")
        version = next((x for x in versions if x.get("version_type") == "release"), versions[0])
    v = version
    if v["project_id"] in seen or v["project_id"] in PINNED:
        return []
    seen.add(v["project_id"])
    out = [_entry(v, server)]
    for d in v.get("dependencies", []):
        if d.get("dependency_type") != "required":
            continue
        pid = d.get("project_id")
        if d.get("version_id"):
            dv = _get(f"/version/{d['version_id']}")
            out += resolve(None, server, seen, version=dv)
        elif pid and pid not in seen and pid not in PINNED:
            out += resolve(pid, server, seen)
    return out


PACK = ROOT / "pack"
LOADER = LOADER_FALLBACK


def resolve_all(slugs, seen, have):
    extra = []
    for slug, server, *pin in slugs:
        try:
            got = resolve(slug, server, seen, version=_get(f"/version/{pin[0]}") if pin else None)
            extra += [g for g in got if g[1] not in have | {e[1] for e in extra}]
            print(f"resolved {slug}: {', '.join(g[1] for g in got)}")
        except Exception as e:                           # offline or renamed: build the pack without it
            print(f"warning: could not resolve {slug}: {e}")
    return extra


def build(out_name, title, summary, entries, jars):
    files = []
    for folder, name, url, size, sha1, sha512, server in entries:
        assert len(sha1) == 40 and len(sha512) == 128, name
        int(sha1, 16), int(sha512, 16)
        files.append({"path": f"{folder}/{name}", "hashes": {"sha1": sha1, "sha512": sha512},
                      "env": {"client": "required", "server": "required" if server else "unsupported"},
                      "downloads": [url], "fileSize": size})
    index = {"formatVersion": 1, "game": "minecraft", "versionId": VERSION, "name": title, "summary": summary,
             "files": files, "dependencies": {"minecraft": "1.20.1", "fabric-loader": LOADER}}
    OUT.mkdir(exist_ok=True)
    out = OUT / out_name
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, indent=2))
        for jar in jars:
            z.write(jar, f"overrides/mods/{jar.name}")
        # default settings via YOSBR: applied on first launch, never overwriting your own changes
        defaults = PACK / "fo-defaults"
        for f in sorted(defaults.rglob("*")):
            if f.is_file():
                z.write(f, f"overrides/config/yosbr/{f.relative_to(defaults).as_posix()}")
        z.write(PACK / "FABULOUSLY-OPTIMIZED-LICENSE.md", "overrides/FABULOUSLY-OPTIMIZED-LICENSE.md")
    print(f"Built {out.name} ({len(files)} downloads)")


def main():
    global LOADER
    LOADER = fabric_loader()
    print(f"Fabric Loader {LOADER}")
    entries = FILES + resolve_all(RESOLVE, set(), set())
    jars = [ROOT / "build" / "libs" / f"vividlands-{VERSION}.jar",
            ROOT / "ragnarok" / "build" / "libs" / f"vividlands_ragnarok-{VERSION}.jar"]
    build(f"VividLands-Modpack-{VERSION}.mrpack", "Vivid Lands",
          "Vivid Lands: a Norse road to Ragnarok - 20 bosses, Create, ancient civilizations, on a Fabulously Optimized-style base",
          entries, jars)


if __name__ == "__main__":
    main()
