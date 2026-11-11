#!/usr/bin/env python3
"""G25 / G26 - the scene gate: a 3D canvas judged as a scene, not as a picture.

    python antigraf_scene_gate.py capture/scene.json checks/round-3/scene.json
    python antigraf_scene_gate.py capture/scene.json checks/round-3/scene.json --frames

G25 compares what is actually inside the canvas: the library and its revision,
the render settings that decide the whole look (tone mapping, exposure, shadow
map, antialias), the camera, every light, the meshes, triangles, materials and
post-processing.

G26 (--frames) compares how the scene moves: the sampled frames of both sides,
frame by frame, so a copy whose idle spin is the wrong speed or that does not
spin at all cannot hide behind an identical still picture.

Why this exists: every other gate sees a 3D page as one grey rectangle. That is
how a copy ends up with the right shapes and the wrong light, which is exactly
the case a person notices first.

Verdicts, in the same language as every other gate:
    unknown   one side has no scene (found:false) - never a pass
    FAIL      the scenes differ on a compared value
    pass      every compared value is within tolerance

Exit 0 pass, 1 fail, 2 cannot run.
"""

import os
import re

from antigraf_common import FAIL, PASS, Stop, emit, flag, gate_ok, load, need, positional, run, table, verdict
from antigraf_pixels import read_png

# The uniforms that make a 3D look: bloom, glow, exposure, tone mapping. On a
# page whose scene graph is private these are the only readable evidence of the
# passes that turn flat geometry into the picture a person remembers.
LOOK_UNIFORM = re.compile(r"bloom|glow|exposure|tonemap|tone_map|saturation|emissive|intensity", re.I)

# A scene is a rendered image, so "the same" is never bit-identical: these are
# the tolerances the comparison uses, and they are written down so a person can
# tighten or loosen them on purpose instead of by accident.
TOL = {
    "exposure": 0.02,        # absolute
    "intensity_rel": 0.02,   # relative, per light
    "position": 0.01,        # relative, per light and camera
    "fov": 0.5,              # degrees
    "aspect": 0.01,
    "triangles_rel": 0.05,   # a differently built mesh is a different mesh
    "pixel_ratio": 0.001,
    "frame_likeness": 90.0,  # per frame picture, 0-100: below this a glow is missing
}


def frame_grid(path, cols=40, rows=24):
    """Read a frame picture as a coarse grid of mean colours.

    A frame comparison does not need every pixel. It needs to see that a glow
    pass, a shadow or a tint is not there, and that shows in the average colour
    of a region long before it shows pixel for pixel.
    """
    w, h, px = read_png(path)
    out = []
    for gy in range(rows):
        y0 = int(h * gy / rows)
        y1 = max(int(h * (gy + 1) / rows), y0 + 1)
        stepy = max((y1 - y0) // 4, 1)
        for gx in range(cols):
            x0 = int(w * gx / cols)
            x1 = max(int(w * (gx + 1) / cols), x0 + 1)
            stepx = max((x1 - x0) // 4, 1)
            r = g = b = n = 0
            for y in range(y0, min(y1, h), stepy):
                line = px[y]
                for x in range(x0, min(x1, w), stepx):
                    c = line[x]
                    r += c[0]
                    g += c[1]
                    b += c[2]
                    n += 1
            n = max(n, 1)
            out.append((r // n, g // n, b // n))
    return w, h, out


def frame_likeness(pa, pb):
    """Likeness of two frame pictures, 0-100, or (None, why) when uncomparable."""
    wa, ha, ga = frame_grid(pa)
    wb, hb, gb = frame_grid(pb)
    if (wa, ha) != (wb, hb):
        return None, "the two frames are different sizes ({}x{} vs {}x{})".format(wa, ha, wb, hb)
    total = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]) for a, b in zip(ga, gb))
    return 100.0 - (total / (len(ga) * 3.0)) / 255.0 * 100.0, ""


def rel_close(a, b, rel):
    a, b = float(a), float(b)
    if a == b:
        return True
    base = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / base <= rel


def abs_close(a, b, tol):
    return abs(float(a) - float(b)) <= tol


def light_key(l):
    pos = " ".join(str(round(float(l.get(k) or 0), 2)) for k in ("x", "y", "z"))
    return "{} {} {}".format(l.get("type"), l.get("color"), pos)


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_scene_gate.py scene-original.json scene-copy.json [--frames]")
    need(pos[:2])
    a = load(pos[0])
    b = load(pos[1])
    frames_mode = flag("--frames")

    rows, fails, unknown = [], 0, 0

    def judge(item, o, c, ok, why=""):
        nonlocal fails, unknown
        if o is None and c is None:
            return
        if o is None or c is None:
            unknown += 1
            rows.append([item, o, c, "UNKNOWN", "one side never recorded this"])
            return
        if ok:
            rows.append([item, o, c, "pass", ""])
        else:
            fails += 1
            rows.append([item, o, c, "FAIL", why])

    gate = "G26" if frames_mode else "G25"

    if not a.get("found") or not b.get("found"):
        missing = [name for name, doc in (("original", a), ("copy", b)) if not doc.get("found")]
        print("{} Scene".format(gate))
        print("  no scene on the {}: {}. A canvas that was never read is not a canvas that matches.".format(
            " and ".join(missing),
            (a.get("reason") or b.get("reason") or "no reason recorded")))
        print("  {} FAIL (1 unknown - not compared is not a pass)".format(gate))
        emit(gate, 1, 1, [])
        return FAIL

    print("{} Scene - {}".format(gate, "how it moves" if frames_mode else "what is in the canvas"))
    print("  original  {}".format(pos[0]))
    print("  our build {}".format(pos[1]))

    if frames_mode:
        fa, fb = a.get("frames") or [], b.get("frames") or []
        if not fa or not fb:
            print("  no frames sampled on both sides - nothing to compare")
            emit(gate, 0, 1, [])
            return FAIL
        # the frames carry their picture relative to the file the probe wrote,
        # so the gate reads them from beside the scene.json it was handed
        bases = [os.path.dirname(os.path.abspath(p)) for p in pos[:2]]
        n = min(len(fa), len(fb))
        for i in range(n):
            o, c = fa[i], fb[i]
            mo, mc = int(o.get("moving_count") or 0), int(c.get("moving_count") or 0)
            # the same number of moving things, and the same dominant direction
            same_count = mo == mc
            do = sum((d.get("d_ry") or 0) for d in (o.get("moving") or []))
            dc = sum((d.get("d_ry") or 0) for d in (c.get("moving") or []))
            # on a private scene the motion is in the animated uniforms, not in
            # object rotations, so the sum falls back to those deltas
            if not do:
                do = sum((d.get("d") or 0) for d in (o.get("moving") or []))
            if not dc:
                dc = sum((d.get("d") or 0) for d in (c.get("moving") or []))
            same_way = (do >= 0) == (dc >= 0) if (do or dc) else True
            same_rate = rel_close(do, dc, 0.35) if (do or dc) else True
            same_cost = ((o.get("calls") is None and c.get("calls") is None)
                         or (o.get("calls") is not None and c.get("calls") is not None
                             and rel_close(o["calls"], c["calls"], 0.25)))
            judge("frame {} objects".format(i + 1), "{} moving".format(mo), "{} moving".format(mc),
                  same_count and same_way and same_rate and same_cost,
                  "moving things, their speed or the draw cost differ")
            # the frame's own picture: identical motion on both sides still
            # renders differently when a glow, a shadow or a tint is missing
            files = [o.get("file"), c.get("file")]
            if files[0] or files[1]:
                paths = [os.path.join(b, f) if f else None for b, f in zip(bases, files)]
                if not (paths[0] and paths[1]):
                    unknown += 1
                    rows.append(["frame {} picture".format(i + 1), files[0] or "-",
                                 files[1] or "-", "UNKNOWN", "one side saved no frame picture"])
                elif not (os.path.exists(paths[0]) and os.path.exists(paths[1])):
                    unknown += 1
                    rows.append(["frame {} picture".format(i + 1), files[0], files[1],
                                 "UNKNOWN", "the frame picture named in the record is not on disk"])
                else:
                    like, why = frame_likeness(paths[0], paths[1])
                    if like is None:
                        unknown += 1
                        rows.append(["frame {} picture".format(i + 1), files[0], files[1], "UNKNOWN", why])
                    else:
                        judge("frame {} picture".format(i + 1), "{:.1f}% alike".format(like),
                              "{:.1f}% alike".format(like), like >= TOL["frame_likeness"],
                              "below {}% - a glow, a shadow or a tint is missing".format(TOL["frame_likeness"]),)
                        rows[-1][1] = rows[-1][2] = "{:.1f}% alike".format(like)
        table(rows, ["frame", "original", "our build", "result", "why"])
        ok = gate_ok(fails, unknown)
        print("\n{} {}  {}".format(gate, verdict(fails, unknown),
                                   "" if ok else "S2 the scene does not move the same way"))
        emit(gate, fails, unknown, [{"item": r[0], "result": r[3]} for r in rows])
        return PASS if ok else FAIL

    # ---- what the page is built from
    judge("library", a.get("lib"), b.get("lib"), a.get("lib") == b.get("lib"),
          "a different 3D library renders differently, so this is not a 1:1 scene")
    judge("revision", a.get("revision"), b.get("revision"),
          str(a.get("revision")) == str(b.get("revision")),
          "the same library at a different revision is a different renderer")

    # ---- the render settings: the reason two copies never look alike
    ra, rb = a.get("render") or {}, b.get("render") or {}
    judge("tone mapping", ra.get("tone_mapping"), rb.get("tone_mapping"),
          ra.get("tone_mapping") == rb.get("tone_mapping"),
          "tone mapping decides the whole contrast of the picture")
    judge("exposure", ra.get("tone_mapping_exposure"), rb.get("tone_mapping_exposure"),
          ra.get("tone_mapping_exposure") is not None and rb.get("tone_mapping_exposure") is not None
          and abs_close(ra["tone_mapping_exposure"], rb["tone_mapping_exposure"], TOL["exposure"]),
          "exposure within +-{}".format(TOL["exposure"]))
    judge("shadow map", ra.get("shadow_map"), rb.get("shadow_map"),
          ra.get("shadow_map") == rb.get("shadow_map"), "shadows on or off changes every edge")
    judge("shadow type", ra.get("shadow_type"), rb.get("shadow_type"),
          ra.get("shadow_type") == rb.get("shadow_type"), "")
    judge("output colour", ra.get("output_color_space"), rb.get("output_color_space"),
          ra.get("output_color_space") == rb.get("output_color_space"), "")
    judge("antialias", ra.get("antialias"), rb.get("antialias"),
          ra.get("antialias") == rb.get("antialias"), "")
    judge("pixel ratio", ra.get("pixel_ratio"), rb.get("pixel_ratio"),
          ra.get("pixel_ratio") is not None and rb.get("pixel_ratio") is not None
          and abs_close(ra["pixel_ratio"], rb["pixel_ratio"], TOL["pixel_ratio"]), "")

    # ---- camera
    ca, cb = a.get("camera") or {}, b.get("camera") or {}
    judge("camera type", ca.get("type"), cb.get("type"), ca.get("type") == cb.get("type"), "")
    judge("camera fov", ca.get("fov"), cb.get("fov"),
          ca.get("fov") is not None and cb.get("fov") is not None
          and abs_close(ca["fov"], cb["fov"], TOL["fov"]), "")
    judge("camera aspect", ca.get("aspect"), cb.get("aspect"),
          ca.get("aspect") is not None and cb.get("aspect") is not None
          and abs_close(ca["aspect"], cb["aspect"], TOL["aspect"]), "")

    # ---- lights, one by one
    la, lb = a.get("lights") or [], b.get("lights") or []
    judge("lights", len(la), len(lb), len(la) == len(lb),
          "a missing light is a missing shadow and a flat copy")
    a_keys = {light_key(x) for x in la}
    b_keys = {light_key(x) for x in lb}
    only_a = sorted(a_keys - b_keys)[:4]
    only_b = sorted(b_keys - a_keys)[:4]
    judge("light setup", len(a_keys), len(b_keys), a_keys == b_keys,
          "original only: {} | copy only: {}".format(only_a, only_b))

    # ---- the scene itself
    sa, sb = a.get("stats") or {}, b.get("stats") or {}
    for key in ("objects", "meshes", "lights", "lines", "points", "sprites", "guesses"):
        if key in sa or key in sb:
            judge(key, sa.get(key), sb.get(key), sa.get(key) == sb.get(key), "")
    judge("triangles", sa.get("triangles"), sb.get("triangles"),
          sa.get("triangles") is not None and sb.get("triangles") is not None
          and rel_close(sa["triangles"], sb["triangles"], TOL["triangles_rel"]),
          "triangles within +-{}% - a differently built mesh is a different mesh".format(
              int(TOL["triangles_rel"] * 100)))
    judge("textures", sa.get("textures"), sb.get("textures"), sa.get("textures") == sb.get("textures"), "")
    judge("materials", ",".join(a.get("materials") or []), ",".join(b.get("materials") or []),
          sorted(a.get("materials") or []) == sorted(b.get("materials") or []),
          "a material type renders its own way (standard vs phong vs basic)")
    judge("material colours", ",".join(a.get("colors") or []), ",".join(b.get("colors") or []),
          sorted(a.get("colors") or []) == sorted(b.get("colors") or []), "")
    judge("post-processing", ",".join(a.get("post") or []), ",".join(b.get("post") or []),
          sorted(a.get("post") or []) == sorted(b.get("post") or []),
          "bloom and post passes are the difference between glow and flat")

    # ---- what the graphics card was actually asked to do. On a page whose scene
    #      graph is private this is the whole reading, and it is the reading that
    #      decides whether the copy is a lighter, flatter render.
    ha, hb = a.get("hook") or {}, b.get("hook") or {}
    judge("draw calls / frame", sa.get("draw_calls"), sb.get("draw_calls"),
          sa.get("draw_calls") is not None and sb.get("draw_calls") is not None
          and rel_close(sa["draw_calls"], sb["draw_calls"], 0.10),
          "within +-10% - far fewer calls is a simpler render")
    judge("shader programs", ha.get("programs"), hb.get("programs"),
          ha.get("programs") == hb.get("programs"),
          "a shader program is a pass: bloom, glow and tone mapping are passes")
    ua = [n for n in (ha.get("uniform_names") or []) if LOOK_UNIFORM.search(n)]
    ub = [n for n in (hb.get("uniform_names") or []) if LOOK_UNIFORM.search(n)]
    judge("lighting uniforms", ",".join(sorted(ua)) or "-", ",".join(sorted(ub)) or "-",
          sorted(ua) == sorted(ub),
          "these are the knobs that make the glow: a missing one is a missing pass")
    judge("clear colour", ha.get("clear"), hb.get("clear"),
          ha.get("clear") == hb.get("clear"), "the canvas backdrop the page clears to")

    table(rows, ["item", "original", "our build", "result", "why"])
    ok = gate_ok(fails, unknown)
    print("\n{} {}  {}".format(gate, verdict(fails, unknown),
                               "" if ok else "S2 the scene is not the same scene"))
    emit(gate, fails, unknown, [{"item": r[0], "result": r[3]} for r in rows])
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
