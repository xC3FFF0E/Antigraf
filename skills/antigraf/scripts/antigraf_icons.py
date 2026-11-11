#!/usr/bin/env python3
"""G17 Icons - is every icon its own shape, in its own place, in its own colour?

    python antigraf_icons.py capture/capture.json checks/round-3/capture.json \
        [--tol-size 2] [--tol-pos 8] [--shape strict|loose|off]

Why this gate exists: the picture score can be 98% while one icon in a row of
twelve is a different glyph. A picture blends; an icon pair does not. This gate
pairs every icon with exactly one partner and judges it on its own:

  count      the copy has the same number of icons (S2 when some are missing)
  place      x and y within --tol-pos px, at the same width  (S3)
  size       width and height within --tol-size px          (S3)
  colour     the same ink colour, exact                     (S3)
  shape      the same number of drawn pieces, and the same path
             --shape strict : path data must match exactly   (S3)
             --shape loose  : only the piece count must match (default)
             --shape off    : shape not judged (the picture score covers it)
  name       an icon that carried a label keeps one        (S2, it is usability)

Pairing, in this order (each pair used once):
  1. the same label, both sides
  2. the same glyph text or class
  3. remaining icons, in page order, one to one

Exit 0 pass, 1 fail, 2 cannot run. Standard library only.
"""

from __future__ import annotations

import os
from antigraf_common import FAIL, PASS, Stop, arg, gate_ok, load, need, num, positional, rgb, run, table, verdict


def ink(value):
    """Icon ink compared as an exact colour, with shorthand hex expanded."""
    r = rgb(value)
    return "rgb{}".format(r) if r else str(value or "").strip().lower()


def label_of(icon):
    return str(icon.get("label") or "").strip().lower()


def glyph_of(icon):
    return str(icon.get("glyph") or "").strip().lower()


def pair_up(icons_o, icons_c):
    """One original icon to one copy icon, never the same partner twice."""
    pairs, used = [], set()

    def take(pred):
        for i, o in enumerate(icons_o):
            if any(p[0] == i for p in pairs):
                continue
            for j, c in enumerate(icons_c):
                if j in used:
                    continue
                if pred(o, c):
                    pairs.append((i, j))
                    used.add(j)
                    return True
        return False

    for o in icons_o:                                    # 1. the same label
        take(lambda a, b, o=o: label_of(o) and label_of(a) == label_of(o) and label_of(b) == label_of(o))
    for o in icons_o:                                    # 2. the same glyph
        take(lambda a, b, o=o: glyph_of(o) and glyph_of(a) == glyph_of(o) and glyph_of(b) == glyph_of(o))
    for i, o in enumerate(icons_o):                      # 3. page order
        if any(p[0] == i for p in pairs):
            continue
        for j, c in enumerate(icons_c):
            if j not in used:
                pairs.append((i, j))
                used.add(j)
                break
    return pairs


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_icons.py capture/capture.json copy/capture.json "
                   "[--tol-size 2] [--tol-pos 8] [--shape strict|loose|off]")
    need([pos[0], pos[1]])
    tol_size = num(arg("--tol-size", "2"), 2.0)
    tol_pos = num(arg("--tol-pos", "8"), 8.0)
    shape = arg("--shape", "loose").strip().lower()
    if shape not in ("strict", "loose", "off"):
        raise Stop("--shape is strict, loose or off")

    a, b = load(pos[0]), load(pos[1])
    io, ic = a.get("icons"), b.get("icons")
    if io is None or ic is None:
        raise Stop("one side has no icons[] - re-run the collector (scripts/antigraf_collect.js) "
                   "on both pages, same widths")
    if not io:
        print("no icons on the original at this width - nothing for G17 to judge, so G17")
        print("does not pass: an empty set is not a comparison (it is unknown)")
        print("G17 {}  S2 structural - the original's icon set was not captured".format(
            verdict(1, 1)))
        return FAIL

    width_o = (a.get("widths") or ["?"])[0]
    width_c = (b.get("widths") or ["?"])[0]
    if width_o != width_c:
        raise Stop("widths differ ({} vs {}) - nothing is comparable".format(width_o, width_c))

    diffs = []

    def add(sev, what, o, c, where):
        diffs.append((sev, what, o, c, where))

    pairs = pair_up(io, ic)
    paired_o = {p[0] for p in pairs}

    if len(ic) < len(io):
        add("S2", "count", len(io), len(ic), "page @{}".format(width_o))

    for i, j in pairs:
        o, c = io[i], ic[j]
        tag = o.get("id") or "ico-{:02d}".format(i + 1)
        where = "{} @{}".format(o.get("label") or o.get("glyph") or tag, width_o)
        for key, tol, sev in (("w", tol_size, "S3"), ("h", tol_size, "S3"),
                              ("x", tol_pos, "S3"), ("y", tol_pos, "S3")):
            ov, cv = num(o.get(key)), num(c.get(key))
            if ov is None or cv is None:
                if ov is None:
                    add("S3", key, "not measured", cv if cv is not None else "-", where)
                continue
            if abs(ov - cv) > tol:
                add(sev, key, ov, cv, where)
        if ink(o.get("colour")) != ink(c.get("colour")):
            add("S3", "colour", o.get("colour"), c.get("colour"), where)
        if label_of(o) and not label_of(c):
            add("S2", "name", o.get("label"), "no label", where)
        elif shape == "strict" and (o.get("path_sig") or "") and (c.get("path_sig") or ""):
            if str(o.get("path_sig")).strip() != str(c.get("path_sig")).strip():
                add("S3", "path", str(o.get("path_sig"))[:40], str(c.get("path_sig"))[:40], where)
        elif shape == "loose":
            on, cn = num(o.get("paths")), num(c.get("paths"))
            if on is not None and cn is not None and on != cn:
                add("S3", "pieces", int(on), int(cn), where)

    for i, o in enumerate(io):
        if i not in paired_o:
            add("S2", "partner", o.get("label") or o.get("glyph") or o.get("id"), "-",
                "{} @{}".format(o.get("id") or "ico-{:02d}".format(i + 1), width_o))

    print("G17 icons @{}px  original {}  copy {}  paired {}  shape: {}".format(
        width_o, len(io), len(ic), len(pairs), shape))
    if diffs:
        rows = [(s, w, str(o)[:34], str(c)[:34], h) for s, w, o, c, h in diffs]
        print()
        table(rows, ["sev", "what", "original", "copy", "where"])
        s1 = [d for d in diffs if d[0] == "S1"]
        s2 = [d for d in diffs if d[0] == "S2"]
        print("\n{} difference line(s): {} fatal, {} structural, {} visual".format(
            len(diffs), len(s1), len(s2), len(diffs) - len(s1) - len(s2)))
        print("Every line above blocks the lock until it is fixed or the person waives it.")
        print("G17 {}".format(verdict(1, 0)))
        return FAIL

    print("every icon in its own place, its own size, its own colour, its own shape")
    print("G17 {}".format(verdict(0, 0)))
    return PASS


if __name__ == "__main__":
    run(main)
