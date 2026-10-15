#!/usr/bin/env python3
"""
Summarise jstack samples taken during world generation (run_server.sh with PROFILE=true).
For worker threads that are busy (RUNNABLE), count:
  - "self":  the top frame (where the CPU actually is)
  - "total": every distinct method on the stack (inclusive time)
    python3 profile.py <dir with s*.txt> <out.txt> [mappings.tiny]

A production server uses intermediary names (class_1234.method_5678); pass Loom's merged
tiny mappings (intermediary -> named) to translate them back to Mojang names.
"""
import re
import sys
from collections import Counter
from pathlib import Path

FRAME = re.compile(r"^\s+at ([\w$.<>/]+)\(")


def threads(text):
    for block in text.split("\n\n"):
        lines = block.strip().splitlines()
        if not lines or not lines[0].startswith('"'):
            continue
        name = lines[0].split('"')[1]
        if "java.lang.Thread.State: RUNNABLE" not in block:
            continue
        frames = [translate(m.group(1)) for l in lines if (m := FRAME.match(l))]
        if frames:
            yield name, frames


CLASSES, METHODS = {}, {}


def load_mappings(path):
    ns, cls = None, None
    for line in open(path, encoding="utf-8"):
        cols = line.rstrip("\n").split("\t")
        if cols[0] == "tiny":
            ns = cols[3:]
            continue
        if ns is None:
            continue
        if cols[0] == "c":
            names = dict(zip(ns, cols[1:]))
            cls = names.get("named")
            if "intermediary" in names and cls:
                CLASSES[names["intermediary"].replace("/", ".")] = cls.replace("/", ".")
        elif len(cols) > 2 and cols[1] == "m":
            names = dict(zip(ns, cols[3:]))
            if names.get("intermediary", "").startswith("method_") and names.get("named"):
                METHODS[names["intermediary"]] = names["named"]


def translate(frame):
    cls, _, meth = frame.rpartition(".")
    base, _, inner = cls.partition("$")
    named = CLASSES.get(cls) or (CLASSES.get(base, base) + ("$" + inner if inner else ""))
    return f"{named}.{METHODS.get(meth, meth)}"


def short(f):
    parts = translate(f).split(".")
    return ".".join(parts[-2:])


def main(d, out):
    self_c, total_c, groups, n = Counter(), Counter(), Counter(), 0
    for f in sorted(Path(d).glob("s*.txt")):
        for name, frames in threads(f.read_text(errors="replace")):
            if not any(k in name for k in ("Worker", "Server thread", "c2me", "Chunky")):
                continue
            n += 1
            self_c[short(frames[0])] += 1
            seen = set()
            for fr in frames:
                s = short(fr)
                if s not in seen:
                    total_c[s] += 1
                    seen.add(s)
            stack = " ".join(frames)
            g = ("noise/density" if "DensityFunction" in stack or "NoiseChunk" in stack else
                 "features (trees, plants...)" if "Feature" in stack and "place" in stack else
                 "surface rules" if "SurfaceSystem" in stack or "SurfaceRules" in stack else
                 "biomes" if "BiomeSource" in stack or "Climate" in stack else
                 "lighting" if "Light" in stack else
                 "structures" if "Structure" in stack else
                 "saving/IO" if "RegionFile" in stack or "ChunkStorage" in stack or "NbtIo" in stack else
                 "other")
            groups[g] += 1
    lines = [f"{n} busy-thread samples", "", "== by stage =="]
    lines += [f"{v * 100 / max(n, 1):5.1f}%  {k}" for k, v in groups.most_common()]
    lines += ["", "== self (top of stack) =="]
    lines += [f"{v * 100 / max(n, 1):5.1f}%  {k}" for k, v in self_c.most_common(40)]
    lines += ["", "== inclusive =="]
    lines += [f"{v * 100 / max(n, 1):5.1f}%  {k}" for k, v in total_c.most_common(80)]
    Path(out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))


if __name__ == "__main__":
    if len(sys.argv) > 3 and Path(sys.argv[3]).exists():
        load_mappings(sys.argv[3])
        print(f"loaded {len(CLASSES)} classes, {len(METHODS)} methods")
    main(sys.argv[1], sys.argv[2])
