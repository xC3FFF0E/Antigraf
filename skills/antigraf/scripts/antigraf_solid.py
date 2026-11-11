#!/usr/bin/env python3
"""G25 (solid part) - a 3D tool's output judged as a real solid, not as a picture.

    python antigraf_solid.py model.3mf                      # is this one file a clean solid?
    python antigraf_solid.py orig/model.3mf copy/model.3mf  # same input, same solid out?
        [--size-tol 0.1] [--volume-tol 1] [--area-tol 2] [--json gates.json]

Reads .3mf (the zip with a 3D/*.model inside) and .stl (text or binary) with the
standard library only. For every part it measures:

    triangles, size (bounding box in mm), volume (mm3), surface area (mm2),
    open edges (a hole: an edge used by one triangle only),
    bad edges (an edge used by three or more triangles, or twice the same way),
    pieces (separate shells inside one part), flat triangles (zero area).

A part is a clean solid ("watertight") when it has no open edges, no bad edges,
no flat triangles and a positive volume. Every printer and slicer needs that;
a switch that pokes through a wall or a floor with a hole fails here first.

With two files the copy is compared with the original, part by part:
    same number of parts,
    each size within --size-tol mm (default 0.1),
    each volume within --volume-tol percent (default 1),
    each surface area within --area-tol percent (default 2),
    every copy part watertight.
Triangle counts are shown, never compared: two engines may cut the same shape
into different triangles and still make the same object.

Parts are paired by name when both sides name them, otherwise by volume order.

What this does NOT check, said plainly: faces that cut through each other inside
one shell (self-intersection), colours and materials per face. Those stay for a
person or a slicer to confirm.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from __future__ import annotations

import math
import os
import re
import struct
import zipfile
import xml.etree.ElementTree as ET

from antigraf_common import (FAIL, PASS, Stop, emit, gate_ok, positional, run,
                             table, verdict, arg)

UNIT_MM = {"micron": 0.001, "millimeter": 1.0, "centimeter": 10.0,
           "inch": 25.4, "foot": 304.8, "meter": 1000.0}
IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
MAX_BYTES = 512 * 1024 * 1024


# ---------------------------------------------------------------- readers


def local(tag):
    return tag.rsplit("}", 1)[-1]


def matrix(text):
    """3MF transform 'm00 m01 m02 m10 m11 m12 m20 m21 m22 m30 m31 m32'."""
    if not text:
        return IDENTITY
    vals = [float(v) for v in text.split()]
    if len(vals) != 12:
        raise Stop("bad 3MF transform: {}".format(text))
    return tuple(vals)


def combine(a, b):
    """Apply a, then b (row-vector convention used by 3MF)."""
    out = []
    for r in range(4):
        row = a[r * 3:r * 3 + 3]
        for c in range(3):
            v = sum(row[k] * b[k * 3 + c] for k in range(3))
            if r == 3:
                v += b[9 + c]
            out.append(v)
    return tuple(out)


def apply(m, p):
    x, y, z = p
    return (x * m[0] + y * m[3] + z * m[6] + m[9],
            x * m[1] + y * m[4] + z * m[7] + m[10],
            x * m[2] + y * m[5] + z * m[8] + m[11])


def read_3mf(path):
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise Stop("{}: not a 3MF (it is not a zip file)".format(path))
    with zf:
        models = {}
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            if not name.lower().endswith(".model"):
                continue
            if ".." in name.split("/"):
                raise Stop("{}: refused unsafe path inside the file: {}".format(path, name))
            if info.file_size > MAX_BYTES:
                raise Stop("{}: {} is too large to read safely".format(path, name))
            models["/" + name.lstrip("/")] = ET.fromstring(zf.read(info))
    if not models:
        raise Stop("{}: no .model file inside - not a 3MF".format(path))
    root_key = "/3D/3dmodel.model" if "/3D/3dmodel.model" in models else sorted(models)[0]

    objects = {}
    scale = {}
    for key, root in models.items():
        scale[key] = UNIT_MM.get(root.get("unit", "millimeter"), 1.0)
        for res in root:
            if local(res.tag) != "resources":
                continue
            for obj in res:
                if local(obj.tag) != "object":
                    continue
                entry = {"name": obj.get("name") or "", "mesh": None, "components": []}
                for child in obj:
                    if local(child.tag) == "mesh":
                        verts, tris = [], []
                        for part in child:
                            if local(part.tag) == "vertices":
                                verts = [(float(v.get("x")), float(v.get("y")), float(v.get("z")))
                                         for v in part if local(v.tag) == "vertex"]
                            elif local(part.tag) == "triangles":
                                tris = [(int(t.get("v1")), int(t.get("v2")), int(t.get("v3")))
                                        for t in part if local(t.tag) == "triangle"]
                        entry["mesh"] = (verts, tris)
                    elif local(child.tag) == "components":
                        for comp in child:
                            ref = None
                            for k, v in comp.attrib.items():
                                if local(k) == "path":
                                    ref = v
                            entry["components"].append((ref or key, comp.get("objectid"),
                                                        matrix(comp.get("transform"))))
                objects[(key, obj.get("id"))] = entry

    def flatten(key, oid, m, depth=0):
        if depth > 32:
            raise Stop("{}: components nest too deep (a loop?)".format(path))
        entry = objects.get((key, oid))
        if entry is None:
            raise Stop("{}: object {} is referenced but missing".format(path, oid))
        tris = []
        unit = scale.get(key, 1.0)
        if entry["mesh"]:
            verts, idx = entry["mesh"]
            moved = [apply(m, v) for v in verts]
            for a, b, c in idx:
                if max(a, b, c) >= len(moved) or min(a, b, c) < 0:
                    raise Stop("{}: a triangle points at a vertex that does not exist".format(path))
                tris.append(tuple(tuple(x * unit for x in moved[i]) for i in (a, b, c)))
        for ref, cid, cm in entry["components"]:
            tris += flatten(ref, cid, combine(cm, m), depth + 1)
        return tris

    parts = []
    root = models[root_key]
    for node in root:
        if local(node.tag) != "build":
            continue
        for n, item in enumerate(node):
            if local(item.tag) != "item":
                continue
            ref = root_key
            for k, v in item.attrib.items():
                if local(k) == "path":
                    ref = v
            oid = item.get("objectid")
            name = objects.get((ref, oid), {}).get("name") or "item {}".format(n + 1)
            parts.append((name, flatten(ref, oid, matrix(item.get("transform")))))
    if not parts:
        raise Stop("{}: the 3MF builds nothing (no <build> items)".format(path))
    return parts


def read_stl(path):
    with open(path, "rb") as f:
        data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise Stop("{}: too large to read safely".format(path))
    if len(data) >= 84:
        count = struct.unpack("<I", data[80:84])[0]
        if 84 + count * 50 == len(data):
            tris = []
            for i in range(count):
                v = struct.unpack("<12f", data[84 + i * 50:84 + i * 50 + 48])
                tris.append(((v[3], v[4], v[5]), (v[6], v[7], v[8]), (v[9], v[10], v[11])))
            return [(os.path.basename(path), tris)]
    text = data.decode("utf-8", errors="replace")
    if not text.lstrip().lower().startswith("solid"):
        raise Stop("{}: not a readable STL (neither binary nor text)".format(path))
    parts, current, name, pts = [], [], "", []
    for line in text.splitlines():
        words = line.split()
        if not words:
            continue
        head = words[0].lower()
        if head == "solid":
            name, current = " ".join(words[1:]) or os.path.basename(path), []
        elif head == "vertex" and len(words) >= 4:
            pts.append(tuple(float(w) for w in words[1:4]))
            if len(pts) == 3:
                current.append(tuple(pts))
                pts = []
        elif head == "endsolid":
            parts.append((name, current))
            current = []
    if current:
        parts.append((name, current))
    if not parts:
        raise Stop("{}: the STL holds no triangles".format(path))
    return parts


def read_model(path):
    if not os.path.isfile(path):
        raise Stop("no such file: {}".format(path))
    low = path.lower()
    if low.endswith(".3mf"):
        return read_3mf(path)
    if low.endswith(".stl"):
        return read_stl(path)
    raise Stop("{}: only .3mf and .stl are read".format(path))


# ---------------------------------------------------------------- measuring


def measure(name, tris):
    """Every number a person needs to decide 'is this a clean solid?'."""
    ids, key_of = {}, lambda p: (round(p[0], 5), round(p[1], 5), round(p[2], 5))
    faces, flat = [], 0
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    volume = area = 0.0
    for a, b, c in tris:
        for p in (a, b, c):
            for k in range(3):
                lo[k] = min(lo[k], p[k])
                hi[k] = max(hi[k], p[k])
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        cx = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        twice = math.sqrt(cx[0] ** 2 + cx[1] ** 2 + cx[2] ** 2)
        area += twice / 2.0
        volume += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        tri = tuple(ids.setdefault(key_of(p), len(ids)) for p in (a, b, c))
        if twice < 1e-12 or len(set(tri)) < 3:
            flat += 1
            continue
        faces.append(tri)

    directed = {}
    for f in faces:
        for i in range(3):
            e = (f[i], f[(i + 1) % 3])
            directed[e] = directed.get(e, 0) + 1
    open_edges = bad_edges = 0
    seen = set()
    for (a, b), n in directed.items():
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        back = directed.get((b, a), 0)
        if n == 1 and back == 1:
            continue
        if n + back == 1:
            open_edges += 1
        else:
            bad_edges += 1

    parent = list(range(len(ids)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, c in faces:
        for x, y in ((a, b), (b, c)):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
    used = {v for f in faces for v in f}
    pieces = len({find(v) for v in used})
    size = [round(hi[k] - lo[k], 4) if tris else 0.0 for k in range(3)]
    watertight = bool(faces) and open_edges == 0 and bad_edges == 0 and flat == 0 and volume > 0
    return {"name": name, "triangles": len(tris), "size": size, "volume": round(volume, 3),
            "area": round(area, 3), "open_edges": open_edges, "bad_edges": bad_edges,
            "flat": flat, "pieces": pieces, "watertight": watertight}


def problems_of(p):
    out = []
    if p["open_edges"]:
        out.append("{} open edges (a hole)".format(p["open_edges"]))
    if p["bad_edges"]:
        out.append("{} bad edges (faces stacked or flipped)".format(p["bad_edges"]))
    if p["flat"]:
        out.append("{} flat triangles".format(p["flat"]))
    if p["volume"] <= 0:
        out.append("volume {} - inside out or empty".format(p["volume"]))
    return out


def size_text(s):
    return " x ".join("{:g}".format(v) for v in s)


def pct(a, b):
    if a == 0:
        return 0.0 if b == 0 else math.inf
    return abs(b - a) / abs(a) * 100.0


# ---------------------------------------------------------------- the gate


def main():
    files = positional()
    if len(files) not in (1, 2):
        raise Stop("usage: antigraf_solid.py model.3mf [copy.3mf] "
                   "[--size-tol 0.1] [--volume-tol 1] [--area-tol 2] [--json gates.json]")
    size_tol = float(arg("--size-tol", "0.1"))
    vol_tol = float(arg("--volume-tol", "1"))
    area_tol = float(arg("--area-tol", "2"))

    sides = [[measure(n, t) for n, t in read_model(f)] for f in files]

    if len(files) == 1:
        parts = sides[0]
        rows, fails = [], 0
        for p in parts:
            bad = problems_of(p)
            fails += 1 if bad else 0
            rows.append([p["name"], p["triangles"], size_text(p["size"]), p["volume"],
                         p["area"], p["pieces"], "clean solid" if not bad else "; ".join(bad)])
        print("Solid check - {}".format(files[0]))
        table(rows, ["part", "triangles", "size mm", "volume mm3", "area mm2", "pieces", "verdict"],
              "lrlrrrl")
        print("\n" + verdict(fails))
        emit("G25-solid", fails, 0, [dict(zip(("part", "verdict"), (r[0], r[-1]))) for r in rows])
        return PASS if gate_ok(fails) else FAIL

    orig, copy = sides
    print("Solid compare - original: {}   copy: {}".format(files[0], files[1]))
    fails, unknown, rows = 0, 0, []
    if len(orig) != len(copy):
        fails += 1
        print("parts: original {}, copy {} - FAIL".format(len(orig), len(copy)))
    named = all(p["name"] for p in orig + copy) and \
        sorted(p["name"] for p in orig) == sorted(p["name"] for p in copy)
    if named:
        by_name = {p["name"]: p for p in copy}
        pairs = [(p, by_name[p["name"]]) for p in orig]
    else:
        pairs = list(zip(sorted(orig, key=lambda p: -p["volume"]),
                         sorted(copy, key=lambda p: -p["volume"])))
    for o, c in pairs:
        why = []
        worst = max(abs(a - b) for a, b in zip(o["size"], c["size"]))
        if worst > size_tol:
            why.append("size off by {:.3g} mm".format(worst))
        dv, da = pct(o["volume"], c["volume"]), pct(o["area"], c["area"])
        if dv > vol_tol:
            why.append("volume {:+.2f}%".format((c["volume"] - o["volume"]) / (o["volume"] or 1) * 100))
        if da > area_tol:
            why.append("area {:+.2f}%".format((c["area"] - o["area"]) / (o["area"] or 1) * 100))
        bad = problems_of(c)
        if bad:
            why.append("copy not solid: " + "; ".join(bad))
        if o["pieces"] != c["pieces"]:
            why.append("pieces {} vs {}".format(o["pieces"], c["pieces"]))
        fails += 1 if why else 0
        rows.append(["{} / {}".format(o["name"], c["name"]),
                     size_text(o["size"]), size_text(c["size"]),
                     "{:.1f} / {:.1f}".format(o["volume"], c["volume"]),
                     "{} / {}".format(o["triangles"], c["triangles"]),
                     "match" if not why else "FAIL: " + "; ".join(why)])
    table(rows, ["part (orig / copy)", "size orig", "size copy", "volume mm3", "triangles", "verdict"])
    orig_bad = sum(1 for p in orig if problems_of(p))
    if orig_bad:
        print("\nnote: {} original part(s) are not clean solids themselves - reported, "
              "the copy is still held to a clean solid".format(orig_bad))
    print("\ntolerances: size {} mm, volume {}%, area {}%; triangle counts shown, never compared"
          .format(size_tol, vol_tol, area_tol))
    print(verdict(fails, unknown))
    emit("G25-solid", fails, unknown, [{"pair": r[0], "verdict": r[-1]} for r in rows])
    return PASS if gate_ok(fails, unknown) else FAIL


if __name__ == "__main__":
    run(main)
