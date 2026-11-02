"""
Downloads the FTB quest book mods (FTB Quests, FTB Library, FTB Teams; Fabric 1.20.1) from the FTB maven into a
folder. They aren't on Modrinth, so the modpack can't list them; the tests fetch them with this, players add them
by hand (see README).

    python3 tools/ftb_jars.py <mods folder>
"""
import sys
import urllib.request
from pathlib import Path

FTB = {"ftb-quests-fabric": "2001.4.22", "ftb-library-fabric": "2001.2.13", "ftb-teams-fabric": "2001.3.2"}

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for a, v in FTB.items():
        url = f"https://maven.ftb.dev/releases/dev/ftb/mods/{a}/{v}/{a}-{v}.jar"
        req = urllib.request.Request(url, headers={"User-Agent": "vividlands-tests"})
        (out / f"{a}-{v}.jar").write_bytes(urllib.request.urlopen(req, timeout=180).read())
        print("downloaded", a, v)
