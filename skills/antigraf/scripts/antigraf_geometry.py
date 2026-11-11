#!/usr/bin/env python3
"""G5 Layout - the gap table: what a person would point at, as numbers.

    python antigraf_geometry.py capture/capture.json checks/round-N/capture.json \
        [--tol-type 2] [--tol-pad 4] [--tol-col 8]

For every width, every paired section: original value, copy value, gap,
tolerance, verdict. A row that has a number on one side only is `unknown`, never
a pass - that is the difference between "we measured it" and "we looked at it".

Measured things:
  * no sideways scroll at any width (a page that scrolls sideways on a phone is
    the single most common miss);
  * page width equals the viewport;
  * heading and body type sizes within +-2 px;
  * each section's padding, gap and content column within their tolerances;
  * items per row, exact;
  * section heights within +-8% (a section 40% taller changes the whole page's rhythm).

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import (FAIL, PASS, Stop, arg, gate_ok, load, need, num, positional,
                            run, table, verdict)

DEFAULTS = {"type": 2.0, "pad": 4.0, "col": 8.0, "height_pct": 8.0}


def by_width(cap):
    out = {}
    for layout in cap.get("layouts", []):
        w = num(layout.get("width"))
        if w:
            out[w] = layout
    return out


def sections(layout):
    out = {}
    for i, b in enumerate(layout.get("blocks", [])):
        key = (str(b.get("tag", "")).lower(), str(b.get("heading", "")).strip().lower())
        out[key] = (i, b)
    return out


def pads(block):
    p = block.get("pad")
    if isinstance(p, (list, tuple)):
        return [num(x, 0.0) for x in p]
    if p is None:
        return None
    v = num(p)
    return [v, v, v, v] if v is not None else None


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_geometry.py capture/capture.json copy-capture.json")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])

    tol = dict(DEFAULTS)
    names = {"type": "--tol-type", "pad": "--tol-pad", "col": "--tol-col",
             "height_pct": "--tol-height"}
    for key, flag in names.items():
        raw = arg(flag)
        if raw is not None:
            v = num(raw)
            if v is not None:
                tol[key] = v

    ow, cw = by_width(orig), by_width(copy)
    if not ow:
        raise Stop("{} has no layouts - Study has not run".format(pos[0]))
    shared = sorted(set(ow) & set(cw))
    if not shared:
        raise Stop("no shared width between the two captures (G10: both sides must use the same widths)")

    rows, fails, unknown = [], 0, 0

    for w in sorted(set(ow) | set(cw)):
        if w not in shared:
            unknown += 1
            print("  unknown   width {} exists on one side only - not compared".format(int(w)))

    for w in shared:
        a, b = ow[w], cw[w]
        # page-level
        for name, tol_key in (("scrolls_x", None), ("page_w", "col")):
            av, bv = a.get(name), b.get(name)
            if name == "scrolls_x":
                ok = bool(av) == bool(bv)
                rows.append(["@%d" % int(w), "scrolls sideways", av, bv, "-", "-",
                             verdict(ok)])
                fails += 0 if ok else 1
                if av and not bv:
                    print("  our build scrolls sideways at {} px; the original does not".format(int(w)))
            elif num(av) is not None and num(bv) is not None:
                gap = num(bv) - num(av)
                ok = abs(gap) <= tol["col"]
                rows.append(["@%d" % int(w), "page width", int(num(av)), int(num(bv)),
                             "%+d" % gap, "+-%g" % tol["col"], verdict(ok)])
                fails += 0 if ok else 1
            else:
                unknown += 1

        # type sizes
        at, bt = a.get("type", {}), b.get("type", {})
        for role in ("h1", "h2", "h3", "body", "small"):
            if num(at.get(role)) is None or num(bt.get(role)) is None:
                # Unknown only when one side shows this size and the other does
                # not. A size neither page renders is not something to compare,
                # so it is not a hole either.
                if num(at.get(role)) is not None or num(bt.get(role)) is not None:
                    unknown += 1
                continue
            gap = num(bt[role]) - num(at[role])
            ok = abs(gap) <= tol["type"]
            rows.append(["@%d" % int(w), "type " + role, num(at[role]), num(bt[role]),
                         "%+g" % gap, "+-%g" % tol["type"], verdict(ok)])
            fails += 0 if ok else 1

        # sections, paired by (tag, heading) then by order
        sa, sb = sections(a), sections(b)
        for key, (idx, blk) in sa.items():
            partner = sb.get(key)
            if partner is None:
                rows.append(["@%d" % int(w), "section %s" % (key[1] or key[0]), "-", "-",
                             "-", "-", "FAIL"])
                print("  MISSING   @{} section {}".format(int(w), " / ".join(key)))
                fails += 1
                continue
            _, blk2 = partner

            pa, pb = pads(blk), pads(blk2)
            if pa and pb:
                for i, side in enumerate(("top", "right", "bottom", "left")):
                    gap = pb[i] - pa[i]
                    ok = abs(gap) <= tol["pad"]
                    rows.append(["@%d" % int(w), "%s pad-%s" % (key[1] or key[0], side),
                                 "%g" % pa[i], "%g" % pb[i], "%+g" % gap, "+-%g" % tol["pad"],
                                 verdict(ok)])
                    fails += 0 if ok else 1
            elif pa or pb:
                unknown += 1

            ga, gb = num(blk.get("gap")), num(blk2.get("gap"))
            if ga is not None and gb is not None:
                gap = gb - ga
                ok = abs(gap) <= tol["pad"]
                rows.append(["@%d" % int(w), "%s gap" % (key[1] or key[0]),
                             "%g" % ga, "%g" % gb, "%+g" % gap, "+-%g" % tol["pad"], verdict(ok)])
                fails += 0 if ok else 1
            elif ga is not None:
                unknown += 1

            ra, rb = num(blk.get("per_row")), num(blk2.get("per_row"))
            if ra is not None:
                ok = ra == rb
                rows.append(["@%d" % int(w), "%s per row" % (key[1] or key[0]),
                             int(ra), "-" if rb is None else int(rb), "-", "exact", verdict(ok)])
                fails += 0 if ok else 1
                if rb is None:
                    unknown += 1

            ca = num((blk.get("column") or {}).get("max_w"))
            cb = num((blk2.get("column") or {}).get("max_w"))
            if ca is not None and cb is not None:
                gap = cb - ca
                ok = abs(gap) <= tol["col"]
                rows.append(["@%d" % int(w), "%s column" % (key[1] or key[0]),
                             "%g" % ca, "%g" % cb, "%+g" % gap, "+-%g" % tol["col"], verdict(ok)])
                fails += 0 if ok else 1
            elif ca is not None:
                unknown += 1

            ha, hb = num(blk.get("h")), num(blk2.get("h"))
            if ha and hb:
                pct = abs(hb - ha) / ha * 100.0
                ok = pct <= tol["height_pct"]
                rows.append(["@%d" % int(w), "%s height" % (key[1] or key[0]),
                             int(ha), int(hb), "%+.1f%%" % pct, "+-%g%%" % tol["height_pct"],
                             verdict(ok)])
                fails += 0 if ok else 1

    table(rows, ["width", "item", "original", "copy", "gap", "tol", "verdict"])
    clear = [r for r in rows if str(r[6]) == "FAIL"]
    ok = gate_ok(fails, unknown)
    print("G5 {}  {} row(s) failing - {} unknown (not compared, never a pass)".format(
        verdict(fails, unknown), len(clear), unknown))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
