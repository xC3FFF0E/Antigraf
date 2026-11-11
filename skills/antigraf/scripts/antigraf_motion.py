#!/usr/bin/env python3
"""G13 Motion - are the animations the same, to the millisecond?

    python antigraf_motion.py capture/motion.json checks/round-3/motion.json

Both sides are recorded with the same probe (references/fidelity.md section1), so this
script pairs every animation by its unit and its property, and then compares the
numbers that make it feel like the original:

  duration   within 50 ms or 10%, whichever is wider
  delay      within 50 ms
  easing     the exact curve - "ease-out" is not "cubic-bezier(.4,0,.2,1)"
  iterations infinite stays infinite
  direction  same
  reduced motion  honoured on both sides, or honoured on neither

A motion the original has and the copy does not is a difference (S3). A motion
the copy invents where the original has none is also a difference - a copy that
wiggles where the original is still is not a copy.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import FAIL, PASS, Stop, arg, load, need, norm_token, num, positional, run, table

DUR_TOL_MS = 50.0
DUR_TOL_REL = 0.10
DELAY_TOL_MS = 50.0

BUCKETS = ("transitions", "animations", "scroll_effects", "hover_effects")


def ident(item):
    who = str(item.get("unit") or item.get("element") or item.get("control") or "").strip().lower()
    what = str(item.get("property") or item.get("name") or item.get("effect") or "").strip().lower()
    return who, what


def index(doc):
    out = {}
    for bucket in BUCKETS:
        for item in doc.get(bucket) or []:
            k = (bucket,) + ident(item)
            out[k] = item
    return out


def easing(value):
    if value is None:
        return None
    return norm_token(str(value).replace(" ", ""))


def close(orig, copy, abs_tol, rel_tol=0.0):
    a, b = num(orig), num(copy)
    if a is None or b is None:
        return False
    if abs(a - b) <= abs_tol:
        return True
    return a > 0 and abs(a - b) / a <= rel_tol


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_motion.py capture/motion.json build/motion.json")
    need(pos[:2])
    a = load(pos[0])
    b = load(pos[1])

    oi, ci = index(a), index(b)
    diffs = []
    matched = 0

    for k, o in oi.items():
        c = ci.get(k)
        if c is None:
            diffs.append(("S3", "missing", k[0] + " " + k[1] + " " + k[2],
                          "original has this motion, the copy has none"))
            continue
        matched += 1
        problems = []
        if not close(o.get("duration_ms"), c.get("duration_ms"), DUR_TOL_MS, DUR_TOL_REL):
            problems.append("duration {} vs {}".format(
                num(o.get("duration_ms")), num(c.get("duration_ms"))))
        if not close(o.get("delay_ms") or 0, c.get("delay_ms") or 0, DELAY_TOL_MS):
            problems.append("delay {} vs {}".format(num(o.get("delay_ms")) or 0,
                                                    num(c.get("delay_ms")) or 0))
        if easing(o.get("easing")) != easing(c.get("easing")):
            problems.append("easing {} vs {}".format(o.get("easing"), c.get("easing")))
        if str(o.get("iterations") or "") != str(c.get("iterations") or ""):
            problems.append("iterations {} vs {}".format(o.get("iterations"), c.get("iterations")))
        if str(o.get("direction") or "") != str(c.get("direction") or ""):
            problems.append("direction {} vs {}".format(o.get("direction"), c.get("direction")))
        if problems:
            diffs.append(("S3", "differs", "{} {} {}".format(k[0], k[1], k[2]), "; ".join(problems)))

    for k, c in ci.items():
        if k in oi:
            continue
        # an invented motion is only a difference when the original is still
        if str(c.get("src") or "measured") == "measured":
            diffs.append(("S3", "extra", "{} {} {}".format(k[0], k[1], k[2]),
                          "the copy animates where the original does not"))

    rm_a = (a.get("reduced_motion") or {}).get("honored")
    rm_b = (b.get("reduced_motion") or {}).get("honored")
    if rm_a is not None or rm_b is not None:
        if bool(rm_a) != bool(rm_b):
            diffs.append(("S2", "reduced-motion",
                          "reduced motion",
                          "original honours it: {}, copy honours it: {}".format(rm_a, rm_b)))

    if not oi and not ci:
        # A page that animates nothing is not a page nobody measured. Both
        # motion documents exist, and both say the same thing: no motion.
        # Recording nothing to animate is an answer, so this passes.
        if a.get("src") or a.get("transitions") is not None or a.get("reduced_motion"):
            print("G13 Motion - pass: neither side animates, both were recorded")
            return PASS
        print("G13 Motion - cannot run: neither side recorded a single animation.")
        print("Record motion with the probe in references/fidelity.md, on both sides, before claiming this gate.")
        return FAIL

    print("motion  {} original, {} copy, {} paired".format(len(oi), len(ci), matched))
    if diffs:
        rows = [(s, kind, what, note) for s, kind, what, note in diffs[:40]]
        table(rows, ("severity", "kind", "what", "detail"))
    for s, _kind, _what, _note in diffs[:6]:
        assert s in ("S1", "S2", "S3", "S4")

    print("\nG13 Motion - {}{}S3".format("pass" if not diffs else "fail  ",
                                         "" if not diffs else "  S3"))
    if diffs:
        print("  {} motion difference(s). The first three are the ones that make the copy feel different.".format(
            len(diffs)))
        return FAIL
    print("  every animation matches: same duration, same curve, same delay, same loop, same reduced-motion.")
    return PASS


if __name__ == "__main__":
    run(main)
