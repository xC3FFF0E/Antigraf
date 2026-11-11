#!/usr/bin/env python3
"""Pixel likeness - computed from the PNGs themselves, with no image library.

    python antigraf_pixels.py capture/shot-1440.png checks/round-3/shot-1440.png \
        [--widths 1440,768,390] [--noise capture/noise-1440.png checks/round-3/noise-1440.png]

Reads both PNGs with zlib + struct (standard library only), tiles the picture
into a grid, and prints:

    likeness          share of tiles whose mean colour matches within a tolerance
    worst tiles       the areas a person would point at, named by position
    bands             likeness per horizontal band, top to bottom, so a bad footer
                      cannot hide behind a good hero

This number is REPORTED, never a gate. Two builds written separately can reach
~99 but not 100, so gate G5 (measurements) and the plan rows do the failing; the
pixel score is the "does it feel the same" reading beside them.

Exit 0 always when both pictures were read (a report ran); 2 when a file could
not be decoded, so a missing picture is never mistaken for a perfect score.
"""

from __future__ import annotations

import struct
import sys
import zlib

from antigraf_common import Stop, positional, need, run


def read_png(path):
    """Decode a PNG to (width, height, RGB rows). Handles the common PNG forms."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise Stop("{} is not a PNG".format(path))
    pos, chunks = 8, {}
    while pos < len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        chunks.setdefault(ctype, []).append(body)
        pos += 12 + length
        if ctype == b"IEND":
            break
    ihdr = chunks.get(b"IHDR", [None])[0]
    if not ihdr:
        raise Stop("{}: no IHDR header".format(path))
    width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", ihdr)
    if depth != 8:
        raise Stop("{}: {}-bit PNGs are not supported (save as 8-bit)".format(path, depth))
    if interlace:
        raise Stop("{}: interlaced PNGs are not supported (save without interlacing)".format(path))

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    if channels is None:
        raise Stop("{}: PNG colour type {} is not supported".format(path, color))

    palette = None
    if color == 3:
        plte = chunks.get(b"PLTE")
        if not plte:
            raise Stop("{}: palette PNG without PLTE".format(path))
        raw = plte[0]
        palette = [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]

    idat = b"".join(chunks.get(b"IDAT", []))
    try:
        raw = zlib.decompress(idat)
    except zlib.error as e:
        raise Stop("{}: corrupt image data ({})".format(path, e))

    stride = width * channels
    rows, prev = [], [0] * stride
    i = 0
    for _ in range(height):
        ftype = raw[i]
        i += 1
        line = list(raw[i:i + stride])
        i += stride
        if ftype == 1:
            for x in range(channels, stride):
                line[x] = (line[x] + line[x - channels]) & 0xFF
        elif ftype == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif ftype == 3:
            for x in range(stride):
                left = line[x - channels] if x >= channels else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 0xFF
        elif ftype == 4:
            for x in range(stride):
                a = line[x - channels] if x >= channels else 0
                b = prev[x]
                c = prev[x - channels] if x >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 0xFF
        elif ftype != 0:
            raise Stop("{}: unknown filter type {}".format(path, ftype))
        prev = line

        if channels == 3:
            rows.append([tuple(line[x:x + 3]) for x in range(0, stride, 3)])
        elif channels == 4:
            rows.append([tuple(line[x:x + 3]) for x in range(0, stride, 4)])
        elif channels == 1 and palette:
            rows.append([palette[min(line[x], len(palette) - 1)] for x in range(0, stride)])
        else:  # grey
            rows.append([(line[x], line[x], line[x]) for x in range(0, stride, channels)])
    return width, height, rows


def tile_means(img, grid=24):
    """Mean colour per tile, so a shift of a few pixels is not counted as a miss."""
    width, height, rows = img
    step_x = max(1, width // grid)
    step_y = max(1, height // grid)
    out = {}
    for ty in range(0, height, step_y):
        for tx in range(0, width, step_x):
            r = g = b = n = 0
            for y in range(ty, min(ty + step_y, height)):
                for x in range(tx, min(tx + step_x, width)):
                    px = rows[y][x]
                    r += px[0]
                    g += px[1]
                    b += px[2]
                    n += 1
            if n:
                out[(tx // step_x, ty // step_y)] = (r / n, g / n, b / n)
    return out


def close(a, b, tol):
    return all(abs(a[i] - b[i]) <= tol for i in range(3))


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_pixels.py original.png copy.png [--tol 12] "
                   "[--mask original-noise.png copy-noise.png] [--label 1440]")
    need(pos[:2])
    tol = 12
    mask = None
    label = "shot"
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--tol" and i + 1 < len(argv):
            tol = int(float(argv[i + 1]))
        if a == "--label" and i + 1 < len(argv):
            label = argv[i + 1]
        if a == "--mask" and i + 2 < len(argv):
            mask = (argv[i + 1], argv[i + 2])

    a = read_png(pos[0])
    b = read_png(pos[1])
    if mask:
        need(list(mask))

    Aw, Ah, _ = a
    Bw, Bh, _ = b
    ratios = {k: round(b_ / a_, 3) for k, a_, b_ in
              (("width", Aw, Bw), ("height", Ah, Bh)) }

    ta, tb = tile_means(a), tile_means(b)
    common = set(ta) & set(tb)
    worst = []
    good = 0
    for key in common:
        if close(ta[key], tb[key], tol):
            good += 1
        else:
            y, x = key[1], key[0]
            worst.append((x, y, ta[key], tb[key]))
    live = len(common) or 1
    likeness = 100.0 * good / live

    # per horizontal band, top to bottom
    bands = {}
    gx, gy = max(1, Aw // 24), max(1, Ah // 24)
    for key in common:
        band = key[1] // max(1, gy // 1) if gy else 0
        bands.setdefault(key[1], [0, 0])
        bands[key[1]][1] += 1
        if close(ta[key], tb[key], tol):
            bands[key[1]][0] += 1

    print("{} size original {}x{}  copy {}x{}  scale {}".format(
        label, Aw, Ah, Bw, Bh, ratios))
    print("likeness {:.1f}%  ({} of {} tiles within +-{} per channel)".format(
        likeness, good, live, tol))
    if worst:
        print("worst tiles (x, y, original, copy):")
        for x, y, ca, cb in sorted(worst, key=lambda t: -sum(
                abs(t[2][i] - t[3][i]) for i in range(3)))[:10]:
            print("  tile {:>3},{:<3}  #{:02x}{:02x}{:02x} vs #{:02x}{:02x}{:02x}".format(
                x, y, int(ca[0]), int(ca[1]), int(ca[2]),
                int(cb[0]), int(cb[1]), int(cb[2])))
    tall = sorted(bands.keys())
    print("bands (row of tiles: likeness)  " + "  ".join(
        "{}:{:.0f}%".format(r, 100.0 * bands[r][0] / max(1, bands[r][1])) for r in tall[:12]))
    if len(tall) > 12:
        print("  ... {} more rows".format(len(tall) - 12))
    print("REPORTED ONLY - the pixel score never passes or fails a gate (this is G5's job).")
    return 0


if __name__ == "__main__":
    run(main)
