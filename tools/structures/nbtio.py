"""Minimal NBT writer (big-endian, gzip) for Minecraft structure templates."""
import gzip
import struct


class Byte(int):
    pass


class Short(int):
    pass


class Long(int):
    pass


class Float(float):
    pass


class Double(float):
    pass


class IntList(list):
    """List of TAG_Int (as opposed to a TAG_Int_Array)."""


class DoubleList(list):
    """List of TAG_Double."""


def _tag_id(v):
    if isinstance(v, bool):
        return 1
    if isinstance(v, Byte):
        return 1
    if isinstance(v, Short):
        return 2
    if isinstance(v, Long):
        return 4
    if isinstance(v, Float):
        return 5
    if isinstance(v, (Double, float)):
        return 6
    if isinstance(v, int):
        return 3
    if isinstance(v, str):
        return 8
    if isinstance(v, (list, tuple)):
        return 9
    if isinstance(v, dict):
        return 10
    raise TypeError(f"cannot encode {type(v)}")


def _payload(out, v):
    t = _tag_id(v)
    if t == 1:
        out += struct.pack(">b", int(v))
    elif t == 2:
        out += struct.pack(">h", int(v))
    elif t == 3:
        out += struct.pack(">i", int(v))
    elif t == 4:
        out += struct.pack(">q", int(v))
    elif t == 5:
        out += struct.pack(">f", float(v))
    elif t == 6:
        out += struct.pack(">d", float(v))
    elif t == 8:
        b = v.encode("utf-8")
        out += struct.pack(">H", len(b)) + b
    elif t == 9:
        if isinstance(v, IntList):
            et = 3
        elif isinstance(v, DoubleList):
            et = 6
        else:
            et = _tag_id(v[0]) if v else 0
        out += struct.pack(">bi", et, len(v))
        for item in v:
            if et == 3:
                out += struct.pack(">i", int(item))
            elif et == 6:
                out += struct.pack(">d", float(item))
            else:
                _payload(out, item)
    elif t == 10:
        for k, item in v.items():
            out += struct.pack(">b", _tag_id(item))
            kb = k.encode("utf-8")
            out += struct.pack(">H", len(kb)) + kb
            _payload(out, item)
        out += b"\x00"


def write_nbt(path, root, name=""):
    out = bytearray()
    out += struct.pack(">b", 10)
    nb = name.encode("utf-8")
    out += struct.pack(">H", len(nb)) + nb
    _payload(out, root)
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as f:
        f.write(bytes(out))
