#!/usr/bin/env python3
"""G15 Speed - is the copy as light and as quick as the original?

    python antigraf_speed.py capture/speed.json checks/round-3/speed.json

A pixel-perfect copy that ships four times the javascript is not a copy a person
would keep. Both sides are measured with the same tool, on the same machine, with
the same throttling (references/fidelity.md section3), and this script compares:

  first paint, largest visible paint, layout shift   not worse than the original
  javascript bytes                                   within 15% of the original
  css bytes                                          within 20%
  image bytes                                        within 25%
  number of requests                                 within 20%
  font files                                         the same count, same format
  lazy loading                                       every offscreen image deferred where the original is

Budget caps, when given, are hard: a copy over the cap fails even if the original
is heavier.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import FAIL, PASS, Stop, arg, load, need, num, positional, run, table

TOL = {
    "js_bytes": 0.15,
    "css_bytes": 0.20,
    "image_bytes": 0.25,
    "requests": 0.20,
    "total_bytes": 0.20,
}
TIME_ABS_MS = 300.0
TIME_REL = 0.20
CLS_ABS = 0.02


def metrics(doc):
    return doc.get("metrics") or doc or {}


def over(copy_v, orig_v, rel):
    c, o = num(copy_v), num(orig_v)
    if c is None:
        return False
    if o is None or o <= 0:
        return c > 0
    return c > o * (1.0 + rel)


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_speed.py capture/speed.json build/speed.json")
    need(pos[:2])
    o = metrics(load(pos[0]))
    c = metrics(load(pos[1]))

    rows = []
    diffs = []

    for key, label, rel in (("js_bytes", "javascript bytes", TOL["js_bytes"]),
                            ("css_bytes", "css bytes", TOL["css_bytes"]),
                            ("image_bytes", "image bytes", TOL["image_bytes"]),
                            ("total_bytes", "total bytes", TOL["total_bytes"]),
                            ("requests", "requests", TOL["requests"])):
        vo, vc = num(o.get(key)), num(c.get(key))
        if vo is None and vc is None:
            continue
        bad = over(vc, vo, rel)
        rows.append(("fail" if bad else "ok", label, fmt(vo), fmt(vc),
                     "" if not bad else "over by {:.0f}% (allowed {:.0f}%)".format(
                         pct_over(vo, vc), rel * 100)))
        if bad:
            diffs.append("S3")

    for key, label in (("first_paint_ms", "first paint"),
                       ("largest_paint_ms", "largest visible paint")):
        vo, vc = num(o.get(key)), num(c.get(key))
        if vo is None or vc is None:
            continue
        allowed = vo + max(TIME_ABS_MS, vo * TIME_REL)
        bad = vc > allowed
        rows.append(("fail" if bad else "ok", label, "{:.0f} ms".format(vo), "{:.0f} ms".format(vc),
                     "" if not bad else "slower than {:.0f} ms".format(allowed)))
        if bad:
            diffs.append("S3")

    vo, vc = num(o.get("cls")), num(c.get("cls"))
    if vo is not None and vc is not None:
        allowed = round(vo + CLS_ABS, 3)
        bad = vc > allowed
        rows.append(("fail" if bad else "ok", "layout shift", str(vo), str(vc),
                     "" if not bad else "worse than {}".format(allowed)))
        if bad:
            diffs.append("S3")

    fo, fc = o.get("font_files"), c.get("font_files")
    if isinstance(fc, list) and isinstance(fo, list) and len(fc) > len(fo):
        rows.append(("fail", "font files", len(fo), len(fc), "the copy ships more font files"))
        diffs.append("S3")

    lo, lc = o.get("lazy_offscreen_images"), c.get("lazy_offscreen_images")
    if lo is not None and lc is not None and bool(lo) and not bool(lc):
        rows.append(("fail", "lazy loading", "deferred", "not deferred",
                     "the copy loads offscreen images up front"))
        diffs.append("S3")

    caps = c.get("budgets") or {}
    for key, cap in caps.items():
        module = {}
        val = num(c.get(key))
        if val is None:
            continue
        if val > float(cap):
            rows.append(("fail", "budget " + key, cap, val, "over the cap the run was given"))
            diffs.append("S1")

    if not rows:
        print("No speed numbers on either side. Measure both with the same tool first"
              " (references/fidelity.md section3) - a speed gate with no numbers is not a pass.")
        return FAIL

    table(rows, ("result", "measure", "original", "copy", "note"))
    if diffs:
        fatal = "S1" in diffs
        print("\nG15 Speed - fail  {}".format("S1" if fatal else "S3"))
        print("  {} row(s). The biggest win is almost always images and javascript: fix those first."
              .format(len(diffs)))
        return FAIL
    print("\nG15 Speed - pass")
    print("  no heavier than the original, within tolerance, on the same machine and throttling.")
    return PASS


def fmt(v):
    if v is None:
        return "-"
    if v >= 1024 * 1024:
        return "{:.1f} MB".format(v / (1024.0 * 1024.0))
    if v >= 1024:
        return "{:.0f} kB".format(v / 1024.0)
    return "{:.0f}".format(v)


def pct_over(o, c):
    o, c = num(o), num(c)
    if not o:
        return 0.0
    return 100.0 * (c - o) / o


if __name__ == "__main__":
    run(main)
